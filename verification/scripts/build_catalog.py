#!/usr/bin/env python3
"""build_catalog.py — derived catalog of every research artefact in the repo.

Usage:
    python verification/scripts/build_catalog.py            # write compact/current generated views
    python verification/scripts/build_catalog.py --check    # fail if any view is out of sync

DESIGN RULE (governance/verification-standard.md §9): the catalog is a DERIVED
INDEX, never an authoritative store. Sources of truth remain the files
themselves (+ claims/*/status.json + git history). If the catalog is ever
wrong, delete and regenerate — no information lives only here. This kills the
two-sources-of-truth drift class by construction.

Captured per entry: path, kind, linked claim IDs, theory tag (archive),
first-issue date, this-version date (two-date rule), version, lifecycle
(SUPERSEDED banner detection), size, content hash (sha256/12).
Stdlib-only by design.

Changelog:
  1.0.0 (2026-06-05) first issue: filename two-date parsing, SUPERSEDED detection.
  1.1.0 (2026-06-05) parse python __version__/__first_issued__/__version_issued__
        headers and run-artefact "date" fields, so code and results carry the
        same date/version columns as documents (naming §5 uniform-visibility).
  1.1.1 (2026-06-05) skip git-ignored build/ area (PDF build artefacts are not catalogued).
  1.1.2 (2026-06-05) two-date parsing extended to .pdf (note PDFs now live beside sources).
  1.1.3 (2026-06-05) run artefacts relocated into the claim package (claims/<ID>/runs/); top-level runs/ branch removed.
  1.2.0 (2026-06-23) ADR-0001 performance fix: enumerate via git (repo_inventory.real_files,
        honoring .gitignore incl. committed-by-mistake junk via check-ignore --no-index) instead
        of rglob+SKIP_DIRS; per-file intrinsics cached in verification/.cache/ keyed on
        (size, mtime_ns) so unchanged files are never re-read. Kills the 45s Drive-junk timeout;
        regen becomes O(changed). SKIP_DIRS retained only for the no-git fallback.
  1.2.1 (2026-07-23) harden the no-git fallback: exclude .venv, venv, and tmp so a
        workspace-local document toolchain cannot pollute generated catalog surfaces.
  1.3.0 (2026-08-10) freeze CATALOG.md as a verifier compatibility volume; add
        a compact catalog/INDEX.md and catalog-summary.json; canonicalize UTF-8
        line endings so catalog hashes are stable across Windows/Linux worktrees.
  1.4.0 (2026-08-10) freeze the legacy full catalog JSON and emit a thin current
        manifest with one bounded JSON shard per artefact kind.
  1.4.1 (2026-08-10) remove trailing whitespace from the compact summary line.
"""
__version__ = "1.4.1"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-08-10"

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import tempfile
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo_inventory import real_files, StatCache  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CATALOG_MD = REPO / "CATALOG.md"
CATALOG_JSON = REPO / "verification" / "catalog.json"
CATALOG_INDEX = REPO / "catalog" / "INDEX.md"
CATALOG_SUMMARY = REPO / "verification" / "catalog-summary.json"
CATALOG_MANIFEST = REPO / "verification" / "catalog" / "index.json"
CATALOG_SHARDS = REPO / "verification" / "catalog" / "kinds"
CUTOVER_COMMIT = "4db22f4ea94bb1a936d1a2e4b416aa2d6d1960d4"
CUTOVER_CANONICAL_SHA256 = "121625b81a42e3650eb46327bee84f0dfd9ed821f7d71ecc85077c606ea97d47"
CUTOVER_JSON_CANONICAL_SHA256 = "5e09e38b81b8ea34b3349c423a626cc9ae6d8e062134a2e14c8c6d41104c91bc"

VER_RE = re.compile(r"-(\d{6})(?:-(\d{6}))?-v(\d+)\.(\d+)\.(?:md|tex\.txt|txt|pdf)$")
TAG_RE = re.compile(r"(Math\d+)")
SKIP_DIRS = {".git", ".venv", "venv", "internal", "tmp", "__pycache__", ".pytest_cache", "build", ".cache"}
SKIP_NAMES = {"CATALOG.md", "catalog.json", "catalog-summary.json", ".gitkeep"}
SKIP_PATHS = {"catalog/INDEX.md"}

KINDS = [
    ("claim-card",       "Claim cards (registry layer)"),
    ("proof-note",       "Working proof notes (on claim cards)"),
    ("synthesis",        "Theory synthesis documents (Layer 2)"),
    ("archive-note",     "Migrated legacy notes (immutable)"),
    ("archive-script",   "Migrated legacy scripts (runnable)"),
    ("archive-artefact", "Migrated legacy run artefacts (immutable)"),
    ("run-artefact",     "Fresh run artefacts (TSv2 evidence)"),
    ("code",             "Domain codes"),
    ("verification",     "Verification harness"),
    ("paper",            "Papers (publication layer)"),
    ("website",          "Website (publication layer)"),
    ("registry",         "Registries and ledgers"),
    ("policy",           "Governance policies"),
    ("root-doc",         "Root documents"),
    ("other",            "Other tracked files"),
]
KIND_ORDER = {k: i for i, (k, _) in enumerate(KINDS)}


def classify(rel: str) -> str:
    p = rel.replace("\\", "/")
    if p.startswith("claims/") and p.endswith(("claim.md", "status.json")):
        return "claim-card"
    if p.startswith("claims/") and "/notes/" in p:
        return "proof-note"
    if p.startswith("claims/") and "/runs/" in p:
        return "run-artefact"
    if p.startswith("claims/") and p.endswith("INDEX.md"):
        return "registry"
    if p.startswith("claims/") and "SYNTHESIS" in p:
        return "synthesis"
    if p.startswith("claims/"):
        return "registry" if p.endswith("GATES.md") else "claim-card"
    if p.startswith("theory/") and "synthesis" in p.lower():
        return "synthesis"
    if p.startswith("archive/legacy/notes/"):
        return "archive-note"
    if p.startswith("archive/legacy/scripts/"):
        return "archive-script"
    if p.startswith("archive/legacy/artefacts/"):
        return "archive-artefact"
    if p.startswith("codes/"):
        return "code"
    if p.startswith("verification/"):
        return "verification"
    if p.startswith("publish/papers/"):
        return "paper"
    if p.startswith("publish/website/"):
        return "website"
    if p.startswith(("negative-results/", "predictions/")) or p.endswith(("MIGRATION-LEDGER.md", "INDEX.md", "BY-CLAIM.md")):
        return "registry"
    if p.startswith("governance/"):
        return "policy"
    if "/" not in p:
        return "root-doc"
    return "other"


def claim_links():
    """path -> set of claim IDs, from folder location + status.json evidence."""
    links = {}
    for d in sorted((REPO / "claims").iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        cid = d.name
        for f in d.rglob("*"):
            if f.is_file():
                links.setdefault(str(f.relative_to(REPO)).replace("\\", "/"), set()).add(cid)
        sj = d / "status.json"
        if sj.exists():
            try:
                card = json.loads(sj.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for ev in card.get("legacy_evidence", []):
                if isinstance(ev, str) and ev.startswith("archive/"):
                    links.setdefault(ev, set()).add(cid)
    return links


def iso(yymmdd):
    return f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}" if yymmdd else None


CACHE_PATH = REPO / "verification" / ".cache" / "catalog-stat-v2.json"


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent)); os.close(fd)
    with Path(tmp).open("w", encoding="utf-8", newline="") as stream:
        stream.write(text)
    os.replace(tmp, str(path))


def canonical_bytes(data: bytes) -> bytes:
    """Normalize UTF-8 text for cross-platform size/hash identity.

    Binary files and non-UTF-8 legacy artefacts remain byte-exact.  NUL-bearing
    payloads are always treated as binary.
    """
    if b"\x00" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _intrinsic(rel, f, data):
    """Per-file intrinsic catalog fields (everything except `claims`, which
    depends on status.json and is re-attached each run). Computed only on a
    StatCache miss; `data` is the full file bytes."""
    data = canonical_bytes(data)
    m = VER_RE.search(f.name)
    first, cur, ver = None, None, None
    if m:
        first = iso(m.group(1))
        cur = iso(m.group(2)) if m.group(2) else first
        ver = f"v{m.group(3)}.{m.group(4)}"
    if f.suffix == ".py" and not rel.startswith("archive/"):
        head = data[:2048].decode("utf-8", "replace")
        hv = re.search(r"__version__\s*=\s*[\"\']([^\"\']+)", head)
        hf = re.search(r"__first_issued__\s*=\s*[\"\'](\d{4}-\d{2}-\d{2})", head)
        hc = re.search(r"__version_issued__\s*=\s*[\"\'](\d{4}-\d{2}-\d{2})", head)
        if hv:
            ver = "v" + hv.group(1)
        if hf:
            first = hf.group(1)
        if hc:
            cur = hc.group(1)
    if "/runs/" in rel and f.suffix == ".json" and first is None:
        try:
            j = json.loads(data.decode("utf-8"))
            d = j.get("date") or j.get("generated")
            if isinstance(d, str) and len(d) == 10:
                first = cur = d
        except Exception:
            pass
    superseded = False
    if f.suffix in (".md", ".txt"):
        head = data[:300].decode("utf-8", "replace")
        superseded = "SUPERSEDED by" in head
    tag = None
    tm = TAG_RE.search(f.name)
    if tm and rel.startswith("archive/"):
        tag = tm.group(1)
    return {
        "kind": classify(rel),
        "tag": tag,
        "first_issued": first,
        "version_issued": cur,
        "version": ver,
        "lifecycle": "SUPERSEDED" if superseded else "ACTIVE",
        "bytes": len(data),
        "sha256_12": hashlib.sha256(data).hexdigest()[:12],
    }


def scan():
    """Enumerate real artefacts via git (junk-excluded, ADR-0001) and build
    catalog entries, re-reading only files whose (size, mtime_ns) changed."""
    links = claim_links()
    cache = StatCache(CACHE_PATH)
    entries = []
    for f in real_files(REPO, skip_names=SKIP_NAMES):
        rel = str(f.relative_to(REPO)).replace("\\", "/")
        if rel in SKIP_PATHS or rel.startswith("verification/catalog/"):
            continue
        intr = cache.get_or_compute(REPO, f, lambda ff, data, _r=rel: _intrinsic(_r, ff, data))
        # preserve original key order (no diff churn) and re-attach claims fresh
        entries.append({
            "path": rel,
            "kind": intr["kind"],
            "claims": sorted(links.get(rel, [])),
            "tag": intr["tag"],
            "first_issued": intr["first_issued"],
            "version_issued": intr["version_issued"],
            "version": intr["version"],
            "lifecycle": intr["lifecycle"],
            "bytes": intr["bytes"],
            "sha256_12": intr["sha256_12"],
        })
    cache.prune()
    cache.save()
    entries.sort(key=lambda e: (KIND_ORDER.get(e["kind"], 99), e["path"]))
    return entries


def render_md(entries):
    today = _dt.date.today().isoformat()
    n_sup = sum(1 for e in entries if e["lifecycle"] == "SUPERSEDED")
    L = []
    L.append("# CATALOG — every tracked research artefact (generated)")
    L.append("")
    L.append("<!-- AUTO-GENERATED by verification/scripts/build_catalog.py -->")
    L.append("<!-- DO NOT HAND-EDIT. Derived index — sources of truth are the files,")
    L.append("     claims/*/status.json, and git history. Regenerate at will. -->")
    L.append("")
    L.append(f"Generated: {today}")
    L.append("")
    L.append(f"**{len(entries)} artefacts** · superseded versions kept: {n_sup} · "
             f"machine-readable twin: `verification/catalog.json`")
    L.append("")
    L.append("Dates follow the two-date filename rule "
             "(`governance/naming-and-versioning.md` §3): first-issue anchors the")
    L.append("lineage; version-issue shows currency. Files without encoded dates show —.")
    L.append("")
    for kind, label in KINDS:
        group = [e for e in entries if e["kind"] == kind]
        if not group:
            continue
        L.append(f"## {label}")
        L.append("")
        L.append("| Path | Claims | First issued | Version issued | Ver | Lifecycle | sha256/12 |")
        L.append("|---|---|---|---|---|---|---|")
        for e in group:
            claims = ", ".join(e["claims"]) or "—"
            L.append(f"| `{e['path']}` | {claims} | {e['first_issued'] or '—'} "
                     f"| {e['version_issued'] or '—'} | {e['version'] or '—'} "
                     f"| {e['lifecycle']} | `{e['sha256_12']}` |")
        L.append("")
    return "\n".join(L) + "\n"


def summary_payload(entries):
    stats = []
    for kind, label in KINDS:
        group = [entry for entry in entries if entry["kind"] == kind]
        if group:
            stats.append({
                "kind": kind,
                "label": label,
                "count": len(group),
                "bytes": sum(entry["bytes"] for entry in group),
            })
    claim_status_paths = sorted(
        entry["path"] for entry in entries
        if re.fullmatch(r"claims/(?!_)[^/]+/status\.json", entry["path"])
    )
    largest = sorted(entries, key=lambda entry: (-entry["bytes"], entry["path"]))[:20]
    return {
        "schema": "tect/catalog-summary/1.0",
        "authority": "tracked files + claims/*/status.json + git history",
        "full_catalog": "verification/catalog/index.json",
        "legacy_full_catalog": "verification/catalog.json",
        "compatibility_cutover": {
            "path": "CATALOG.md",
            "commit": CUTOVER_COMMIT,
            "canonical_sha256": CUTOVER_CANONICAL_SHA256,
        },
        "total": len(entries),
        "total_bytes": sum(entry["bytes"] for entry in entries),
        "superseded": sum(entry["lifecycle"] == "SUPERSEDED" for entry in entries),
        "claim_count": len(claim_status_paths),
        "claim_status_paths": claim_status_paths,
        "kinds": stats,
        "largest": [
            {"path": entry["path"], "kind": entry["kind"], "bytes": entry["bytes"]}
            for entry in largest
        ],
    }


def render_index(summary):
    lines = [
        "# TECT catalog index",
        "",
        "Compact generated reader surface. The complete current machine inventory is",
        "`../verification/catalog/index.json`; source files and Git history remain authoritative.",
        f"`../CATALOG.md` is a frozen compatibility volume at commit `{CUTOVER_COMMIT[:8]}`",
        "for historical verifiers and no longer grows.",
        "",
        f"**{summary['total']} artefacts** · **{summary['claim_count']} live claim cards** ·",
        f"{summary['superseded']} superseded artefacts retained",
        "",
        "## By kind",
        "",
        "| Kind | Artefacts | Canonical bytes |",
        "|---|---:|---:|",
    ]
    for row in summary["kinds"]:
        lines.append(f"| {row['label']} (`{row['kind']}`) | {row['count']} | {row['bytes']:,} |")
    lines.extend([
        "",
        "## Use",
        "",
        "- Current compact metadata: `../verification/catalog-summary.json`",
        "- Complete current machine inventory: `../verification/catalog/index.json`",
        "- Frozen machine compatibility volume: `../verification/catalog.json`",
        "- Live claim registry: `../CLAIMS.md`",
        "- Proof and failure navigation: `../theory/proof-evidence-map.md`",
        "",
        "New code should consume `catalog-summary.json` when it only needs counts or",
        "top-level claim paths. Current inventory clients load only the required",
        "kind shard from the manifest.",
        "",
    ])
    return "\n".join(lines)


def _legacy_ok():
    if not CATALOG_MD.exists():
        return False
    digest = hashlib.sha256(canonical_bytes(CATALOG_MD.read_bytes())).hexdigest()
    return digest == CUTOVER_CANONICAL_SHA256


def _legacy_json_ok():
    if not CATALOG_JSON.exists():
        return False
    digest = hashlib.sha256(canonical_bytes(CATALOG_JSON.read_bytes())).hexdigest()
    return digest == CUTOVER_JSON_CANONICAL_SHA256


def _catalog_outputs(entries):
    groups = {}
    for entry in entries:
        groups.setdefault(entry["kind"], []).append(entry)
    outputs = {}
    descriptors = []
    for kind in sorted(groups, key=lambda value: KIND_ORDER.get(value, 99)):
        payload = {
            "schema": "tect/catalog-kind/1.0",
            "kind": kind,
            "count": len(groups[kind]),
            "entries": groups[kind],
        }
        text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
        path = CATALOG_SHARDS / f"{kind}.json"
        outputs[path] = text
        descriptors.append({
            "kind": kind,
            "path": path.relative_to(REPO).as_posix(),
            "count": len(groups[kind]),
            "bytes": len(text.encode("utf-8")),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    manifest = {
        "schema": "tect/catalog-manifest/2.0",
        "authority": "tracked files + claims/*/status.json + git history",
        "total": len(entries),
        "shards": descriptors,
    }
    outputs[CATALOG_MANIFEST] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return outputs


def _stale_shards(outputs):
    expected = {path.resolve() for path in outputs if path.parent == CATALOG_SHARDS}
    actual = ({path.resolve() for path in CATALOG_SHARDS.glob("*.json")}
              if CATALOG_SHARDS.exists() else set())
    return sorted(actual - expected)


def _restore_compatibility_json():
    run = subprocess.run(
        ["git", "show", f"{CUTOVER_COMMIT}:verification/catalog.json"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    if run.returncode != 0:
        detail = run.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(detail or f"git show exited {run.returncode}")
    data = canonical_bytes(run.stdout)
    if hashlib.sha256(data).hexdigest() != CUTOVER_JSON_CANONICAL_SHA256:
        raise RuntimeError("cutover catalog JSON hash mismatch")
    atomic_write(CATALOG_JSON, data.decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--restore-compatibility", action="store_true")
    args = ap.parse_args()
    if args.restore_compatibility:
        try:
            _restore_compatibility_json()
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"CATALOG: REFUSED -- cannot restore compatibility JSON: {exc}")
            return 1
    entries = scan()
    summary = summary_payload(entries)
    index_md = render_index(summary)
    summary_json = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    outputs = _catalog_outputs(entries)
    if args.check:
        ok_index = (CATALOG_INDEX.exists() and
                    CATALOG_INDEX.read_text(encoding="utf-8") == index_md)
        ok_summary = (CATALOG_SUMMARY.exists() and
                      CATALOG_SUMMARY.read_text(encoding="utf-8") == summary_json)
        ok_legacy = _legacy_ok()
        ok_legacy_json = _legacy_json_ok()
        stale = [path for path, expected in outputs.items()
                 if not path.exists() or path.read_text(encoding="utf-8") != expected]
        stale.extend(_stale_shards(outputs))
        ok_shards = not stale
        ok = ok_legacy and ok_legacy_json and ok_index and ok_summary and ok_shards
        print(f"CATALOG-CHECK: {'PASS' if ok else 'FAIL'} "
              f"(legacy {'ok' if ok_legacy else 'STALE'}, "
              f"legacy-json {'ok' if ok_legacy_json else 'STALE'}, "
              f"index {'ok' if ok_index else 'STALE'}, "
              f"summary {'ok' if ok_summary else 'STALE'}, "
              f"shards {'ok' if ok_shards else 'STALE'})")
        for path in stale[:10]:
            print(f"  - {path.relative_to(REPO)}")
        return 0 if ok else 1
    if not _legacy_ok() or not _legacy_json_ok():
        print("CATALOG: REFUSED -- frozen catalog compatibility volume differs from cutover")
        return 1
    atomic_write(CATALOG_INDEX, index_md)
    atomic_write(CATALOG_SUMMARY, summary_json)
    for path, text in outputs.items():
        atomic_write(path, text)
    for path in _stale_shards(outputs):
        path.unlink()
    print(f"CATALOG: preserved frozen compatibility volumes + indexed "
          f"{len(entries)} current artefacts in {len(outputs) - 1} kind shard(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
