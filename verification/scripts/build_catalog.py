#!/usr/bin/env python3
"""build_catalog.py — derived catalog of every research artefact in the repo.

Usage:
    python verification/scripts/build_catalog.py            # write CATALOG.md + verification/catalog.json
    python verification/scripts/build_catalog.py --check    # fail if either is out of sync

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
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-06-05"

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG_MD = REPO / "CATALOG.md"
CATALOG_JSON = REPO / "verification" / "catalog.json"

VER_RE = re.compile(r"-(\d{6})(?:-(\d{6}))?-v(\d+)\.(\d+)\.(?:md|tex\.txt|txt)$")
TAG_RE = re.compile(r"(Math\d+)")
SKIP_DIRS = {".git", "internal", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {"CATALOG.md", "catalog.json", ".gitkeep"}

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
    if p.startswith("runs/"):
        return "run-artefact"
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
    for d in (REPO / "runs").iterdir() if (REPO / "runs").exists() else []:
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file():
                    links.setdefault(str(f.relative_to(REPO)).replace("\\", "/"), set()).add(d.name)
    return links


def iso(yymmdd):
    return f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}" if yymmdd else None


def scan():
    links = claim_links()
    entries = []
    for f in sorted(REPO.rglob("*")):
        if not f.is_file():
            continue
        rel = str(f.relative_to(REPO)).replace("\\", "/")
        if any(part in SKIP_DIRS for part in f.parts) or f.name in SKIP_NAMES:
            continue
        data = f.read_bytes()
        m = VER_RE.search(f.name)
        first, cur, ver = None, None, None
        if m:
            first = iso(m.group(1))
            cur = iso(m.group(2)) if m.group(2) else first
            ver = f"v{m.group(3)}.{m.group(4)}"
        if f.suffix == ".py" and not rel.startswith("archive/"):
            head = data[:2048].decode("utf-8", "replace")
            hv = re.search(r"__version__\s*=\s*[\"']([^\"']+)", head)
            hf = re.search(r"__first_issued__\s*=\s*[\"'](\d{4}-\d{2}-\d{2})", head)
            hc = re.search(r"__version_issued__\s*=\s*[\"'](\d{4}-\d{2}-\d{2})", head)
            if hv:
                ver = "v" + hv.group(1)
            if hf:
                first = hf.group(1)
            if hc:
                cur = hc.group(1)
        if rel.startswith("runs/") and f.suffix == ".json" and first is None:
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
        entries.append({
            "path": rel,
            "kind": classify(rel),
            "claims": sorted(links.get(rel, [])),
            "tag": tag,
            "first_issued": first,
            "version_issued": cur,
            "version": ver,
            "lifecycle": "SUPERSEDED" if superseded else "ACTIVE",
            "bytes": len(data),
            "sha256_12": hashlib.sha256(data).hexdigest()[:12],
        })
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    entries = scan()
    md = render_md(entries)
    js = json.dumps({"generated": _dt.date.today().isoformat(), "entries": entries},
                    indent=1, ensure_ascii=False) + "\n"
    if args.check:
        strip = lambda s: [l for l in s.splitlines() if not l.startswith("Generated:")]
        old_md = CATALOG_MD.read_text(encoding="utf-8") if CATALOG_MD.exists() else ""
        old_js = {}
        if CATALOG_JSON.exists():
            old_js = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        ok_md = strip(old_md) == strip(md)
        ok_js = old_js.get("entries") == entries
        print(f"CATALOG-CHECK: {'PASS' if ok_md and ok_js else 'FAIL'} "
              f"(md {'ok' if ok_md else 'STALE'}, json {'ok' if ok_js else 'STALE'})")
        return 0 if (ok_md and ok_js) else 1
    CATALOG_MD.write_text(md, encoding="utf-8")
    CATALOG_JSON.write_text(js, encoding="utf-8")
    print(f"CATALOG: {len(entries)} artefacts -> CATALOG.md + verification/catalog.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
