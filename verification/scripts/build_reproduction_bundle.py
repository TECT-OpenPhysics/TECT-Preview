#!/usr/bin/env python3
"""build_reproduction_bundle.py -- assemble a self-contained referee REPRODUCTION
BUNDLE for one result: note + reproducible code + transitive deps + environment +
expected-output logs + per-file hashes + README, packaged for external review and
for publish distribution.

Policy (governance/reproduction-bundle-policy.md, binding from 2026-06-10): the FINAL
deliverable of every claim is a reproduction bundle of this form. "Reference code" is
not enough; an outsider must be able to run it and obtain the same PASS/values.

Usage:
    python verification/scripts/build_reproduction_bundle.py \
        --note claims/<ID>/<sub>/notes/<note>.tex.txt \
        --scripts codes/vacuum/res5_032_window_certification.py ... \
        --out claims/<ID>/<sub>/bundle/<name>

Mechanism. TECT reproduction scripts self-locate REPO = __file__.parents[2] and add
the repo subdirs to sys.path, so a bundle that MIRRORS the repo-relative paths of the
needed files runs UNCHANGED: `cd <bundle> && python codes/vacuum/res5_0NN.py` resolves
its imports inside the bundle and writes its result.json inside the bundle. The builder
(1) resolves the transitive LOCAL python deps of the entry scripts by AST, (2) copies
them + the note (.tex.txt + .pdf) preserving repo-relative paths, (3) RUNS each entry
script with the bundle as REPO, capturing stdout to expected/<name>.log and asserting
exit 0, (4) emits requirements.txt, environment.txt, README.md and MANIFEST.json
(sha256 of every file + a content-addressable bundle digest + a repo_commit slot to be
stamped at publish).
"""
__version__ = "1.8.0"
__first_issued__ = "2026-06-10"
__version_issued__ = "2026-06-10"

import argparse, ast, hashlib, json, os, platform, re, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEARCH = [REPO/"codes"/"vacuum", REPO/"archive"/"legacy"/"scripts",
          REPO/"codes"/"pde", REPO/"codes"/"scripts", REPO/"codes"/"tools"]
STDLIB = {"os","sys","math","json","re","collections","pathlib","itertools","functools",
          "time","tempfile","argparse","datetime","typing","__future__","hashlib","platform",
          "shutil","subprocess","ast","random","copy","warnings","importlib"}

def find_module(name):
    for d in SEARCH:
        p = d/(name+".py")
        if p.exists():
            return p
    return None

def resolve_deps(entries):
    seen, deps, thirdparty = set(), set(), set()
    stack = [Path(e).stem for e in entries]
    while stack:
        m = stack.pop()
        if m in seen:
            continue
        seen.add(m)
        p = find_module(m)
        if not p:
            if m not in STDLIB:
                thirdparty.add(m)
            continue
        deps.add(p)
        src = p.read_text()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for a in node.names:
                    stack.append(a.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                stack.append(node.module.split('.')[0])
        # ALSO catch runtime file reads: any "<name>.py" string literal that resolves
        # to a module in the search path (e.g. (LEG / "MathNN.py").read_text()).
        for ref in re.findall(r"""['"]([A-Za-z0-9_]+)\.py['"]""", src):
            if find_module(ref):
                stack.append(ref)
    return sorted(deps), sorted(thirdparty - STDLIB)

def sha256(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def discover_folder(folder):
    """Auto-discover a sub-proof folder's headline note + union of reproduction scripts."""
    import re
    fdir = REPO/folder/"notes"
    notes = [n for n in sorted(fdir.glob("*.tex.txt"))]
    live = []
    for n in notes:
        first = n.read_text().split("\n",1)[0]
        if first.startswith("% SUPERSEDED"):
            continue
        live.append(n)
    if not live:
        return None, []
    # headline: prefer consolidation/final/referee/audit/enactment/closure; tie-break by version
    KEY = ("consolidation","referee","final","audit","enactment","closure","record")
    def ver(n):
        m = re.search(r"-v(\d+)\.(\d+)\.tex\.txt$", n.name)
        return (int(m.group(1)), int(m.group(2))) if m else (0,0)
    def score(n):
        nm = n.name.lower()
        return (sum(k in nm for k in KEY), ver(n))
    headline = max(live, key=score)
    # union of reproduction scripts across live notes
    scripts = []
    for n in live:
        m = re.search(r"Reproduction command:\s*(.+)", n.read_text())
        if m:
            for sc in re.findall(r"([A-Za-z0-9_]+\.py)", m.group(1)):
                rel = None
                for d in SEARCH:
                    if (d/sc).exists(): rel=(d/sc).relative_to(REPO).as_posix(); break
                if rel and rel not in scripts: scripts.append(rel)
    return headline, scripts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder")
    ap.add_argument("--note")
    ap.add_argument("--scripts", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true", help="rebuild even if a complete bundle (MANIFEST) exists")
    ap.add_argument("--tier", help="tier tag for the bundle name (e.g. T7, DRAFT)")
    ap.add_argument("--result", help="result-name slug for the bundle name (default: sub-folder name)")
    ap.add_argument("--title", default="")
    args = ap.parse_args()
    if args.tier and args.tier.strip().upper() == "DRAFT":
        print("ERROR: 'DRAFT' is not a valid bundle tier. Bundles are built only after"
              " operator confirmation; tag with the result's T-tier (e.g. T6, T7)."
              " See governance/reproduction-bundle-policy.md sec.14.")
        return 1
    if args.folder:
        hn, scr = discover_folder(args.folder)
        if hn is None:
            print(f"ERROR: no live notes in {args.folder}/notes"); return 1
        args.note = hn.relative_to(REPO).as_posix()
        args.scripts = scr
        if not args.out:
            parts = args.folder.rstrip("/").split("/")           # claims/<ID>/<sub>
            cid, sub = parts[1], parts[-1]
            result = args.result or sub
            tier = args.tier
            if not tier:
                print("ERROR: --tier is required (the result's confirmed T-tier);"
                      " bundles are post-confirmation artefacts (policy sec.14).")
                return 1
            date = time.strftime("%y%m%d", time.gmtime())
            # convention (reproduction-bundle-policy.md sec.13): claim-top-level, tier+date stamped
            args.out = f"claims/{cid}/bundle/{result}-{tier}-{date}"
        if not args.title:
            args.title = f"{args.folder.split('/')[-2]} / {args.folder.split('/')[-1]}"
        print(f"[folder] headline={hn.name}  scripts={len(scr)}")
        if not scr:
            print("n/a: folder has no numerical-claim reproduction scripts (doc-only); no code bundle needed")
            return 0
    if not args.note or not args.scripts:
        print("ERROR: provide --folder OR (--note + --scripts)"); return 1

    note = REPO/args.note
    out = REPO/args.out
    if out.exists() and (out/"MANIFEST.json").exists() and not args.force:
        print(f"ERROR: {args.out} already has a complete bundle (MANIFEST.json); use --force to rebuild"); return 1
    if args.force and out.exists():
        # full clean so a re-issue leaves NO orphan (e.g. an old note version). On a
        # mount that blocks unlink this is a no-op (ignore_errors) and the orphans must
        # be cleared at the git layer; on a normal FS the rebuild is pristine.
        shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)  # partial (no MANIFEST) is resumed/overwritten

    deps, thirdparty = resolve_deps(args.scripts)
    copied = []
    # (1) code + transitive deps, repo-relative paths preserved
    for p in deps:
        rel = p.relative_to(REPO)
        dst = out/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        copied.append(rel.as_posix())
    # (2) note tex + pdf, repo-relative
    for ext in (".tex.txt", ".pdf"):
        srcname = note.name[:-len(".tex.txt")] + ext if ext == ".pdf" else note.name
        src = note.parent/srcname
        if src.exists():
            rel = src.relative_to(REPO)
            dst = out/rel; dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst); copied.append(rel.as_posix())

    # (3) RUN each entry script with the bundle as REPO; capture expected output.
    #     RESUMABLE: a script already captured with a PASS log is skipped, so a heavy
    #     bundle can be completed across several invocations (each does what fits in its
    #     time budget; an outer timeout leaves the in-flight script's log absent -> re-run).
    (out/"expected").mkdir(exist_ok=True)
    runlog = {}
    def captured_pass(name):
        lg = out/"expected"/f"{name}.log"
        if not lg.exists(): return None
        txt = lg.read_text()
        ps = [l for l in txt.splitlines() if "PASS" in l or "FAIL" in l]
        ok = bool(ps) and "FAIL" not in ps[-1] and "[STDERR]" not in txt
        return (ps[-1] if ps else "") if ok else None
    for s in args.scripts:
        name = Path(s).stem
        done = captured_pass(name)
        if done is not None:
            runlog[name] = dict(exit=0, pass_line=done); print(f"  skip {name} (cached PASS)"); continue
        _env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, s], cwd=out, env=_env, capture_output=True, text=True, errors="replace")
        (out/"expected"/f"{name}.log").write_text(r.stdout + ("\n[STDERR]\n"+r.stderr if r.stderr.strip() else ""))
        tail = [l for l in r.stdout.splitlines() if "PASS" in l or "FAIL" in l]
        runlog[name] = dict(exit=r.returncode, pass_line=(tail[-1] if tail else ""))
        print(f"  ran {name}: exit={r.returncode}  {runlog[name]['pass_line']}")
    ndone = sum(1 for v in runlog.values() if v["exit"] == 0 and "FAIL" not in v["pass_line"])
    if ndone < len(args.scripts):
        print(f"\nPARTIAL: {ndone}/{len(args.scripts)} scripts captured; re-run the same command to continue "
              "(cached PASS scripts are skipped). MANIFEST is written only when all pass.")
        return 2

    # (4) requirements + environment
    (out/"requirements.txt").write_text("\n".join(thirdparty) + ("\n" if thirdparty else ""))
    try:
        import numpy as _np; npv = _np.__version__
    except Exception:
        npv = "unknown"
    env = dict(python=sys.version.split()[0], platform=platform.platform(),
               numpy=npv, built_utc=time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    (out/"environment.txt").write_text(json.dumps(env, indent=2))

    # collect every bundle file for the manifest (after expected/ logs written)
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*")
                   if p.is_file() and p.name != "MANIFEST.json"
                   and "__pycache__" not in p.parts and not p.name.endswith(".pyc"))
    hashes = {f: sha256(out/f) for f in files}
    bundle_digest = hashlib.sha256(
        "\n".join(f"{h}  {f}" for f, h in sorted(hashes.items())).encode()).hexdigest()

    # (5) README
    runcmds = "\n".join(f"  python {s}" for s in args.scripts)
    expected = "\n".join(f"  {n}: exit 0, `{runlog[n]['pass_line']}`" for n in runlog)
    _bn = Path(args.out.rstrip("/")).name
    grade = "PUBLISHED (operator-confirmed)"  # policy sec.14: bundles are post-confirmation only
    readme = f"""# Reproduction bundle -- {args.title or note.stem}

Self-contained referee reproduction bundle (TECT verification-first repository).
Built {env['built_utc']} with Python {env['python']}, numpy {env['numpy']}.

**Bundle grade:** {grade} -- `{_bn}`.

## What this verifies
The note (below) is the proof map; the code reproduces every numerical constant,
window, interval and sanity check it cites. An external referee can run the code
here, without a TECT checkout, and obtain the same PASS lines.

## Contents
- the referee note (proof, self-contained): `{note.relative_to(REPO).as_posix()}`
  (+ its `.pdf`)
- reproduction code + all transitive local dependencies (repo-relative paths preserved)
- `expected/` -- captured stdout of each script at build time (the PASS reference)
- `requirements.txt`, `environment.txt` -- the build environment
- `MANIFEST.json` -- sha256 of every file + a content-addressable bundle digest

## How to reproduce (from this bundle directory)
```
pip install -r requirements.txt        # numpy only
{runcmds}
```
Each script self-locates this bundle as its repository root, resolves its imports
inside the bundle, prints its self-test asserts, and exits 0 iff all pass. Compare
your output against `expected/`.

## Expected (must match)
{expected}

## Integrity
Bundle content digest (sha256 over `<sha256>  <path>` lines):
`{bundle_digest}`
The repository commit that produced this bundle is recorded at publish time in
`MANIFEST.json:repo_commit`.

## Scope / how to attack
See the note's section 1 (scope) and section 10 (devil's-advocate + falsifier).
The result is scope-qualified (T7-SCOPE), not an unconditional claim.
"""
    (out/"README.md").write_text(readme)

    manifest = dict(
        bundle=args.title or note.stem, built_utc=env["built_utc"],
        note=note.relative_to(REPO).as_posix(), entry_scripts=list(args.scripts),
        environment=env, third_party=thirdparty, runlog=runlog,
        repo_commit="TO BE STAMPED AT PUBLISH (git rev-parse HEAD)",
        bundle_digest=bundle_digest, files=hashes)
    (out/"MANIFEST.json").write_text(json.dumps(manifest, indent=2))

    # (6) post-build durability + integrity self-check (mount-truncation guard, v1.6.0).
    # Scripts emit run-artefact JSON into the bundle tree; on a network/virtualised
    # mount these writes can be left unflushed and truncate on call teardown. fsync
    # every file, then re-parse all JSON/PY; a truncated bundle FAILS the build loudly
    # rather than shipping silently.
    for _f in out.rglob("*"):
        if _f.is_file():
            try:
                _fd = os.open(_f, os.O_RDONLY); os.fsync(_fd); os.close(_fd)
            except OSError:
                pass
    _corrupt = []
    for _f in out.rglob("*"):
        if _f.suffix == ".json":
            try: json.loads(_f.read_text())
            except Exception as _e: _corrupt.append((_f, str(_e)[:60]))
        elif _f.suffix == ".py":
            try: ast.parse(_f.read_text())
            except Exception as _e: _corrupt.append((_f, str(_e)[:60]))
    if _corrupt:
        print(f"\nBUNDLE INTEGRITY FAIL ({len(_corrupt)} truncated/corrupt file(s)):")
        for _f, _e in _corrupt:
            print(f"  {_f.relative_to(out).as_posix()}: {_e}")
        return 1

    allpass = all(v["exit"] == 0 for v in runlog.values())
    print(f"\nBUNDLE: {args.out}  ({len(files)+1} files, {len(deps)} code deps, "
          f"{len(args.scripts)} entry scripts {'ALL PASS' if allpass else 'SOME FAIL'})")
    print(f"  digest {bundle_digest[:16]}...  third-party: {thirdparty}")
    return 0 if allpass else 1

if __name__ == "__main__":
    sys.exit(main())
