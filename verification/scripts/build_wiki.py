#!/usr/bin/env python3
"""build_wiki.py — generate GitHub-Wiki pages from the repository (one source).

Usage:
    python verification/scripts/build_wiki.py [--repo owner/name]

Emits the wiki pages into a FRESH TEMPORARY directory (printed) — a SNAPSHOT
of the live record (wikis cannot fetch at view time, so unlike the website
these are generated; every page carries an AUTO-GENERATED banner).
Hand-editing the wiki is forbidden; regenerate and re-push instead
(governance/publication-tiers.md, wiki channel). Nothing is written inside
the repository.

Publish (PowerShell, after the wiki's first page exists on GitHub):
    python verification\\scripts\\build_wiki.py --repo <owner>/<repo> --out $env:TEMP\\tect-wiki
    git clone https://github.com/<owner>/<repo>.wiki.git $env:TEMP\\tect-wiki-repo
    Copy-Item $env:TEMP\\tect-wiki\\*.md $env:TEMP\\tect-wiki-repo -Force
    cd $env:TEMP\\tect-wiki-repo; git add -A
    git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee" commit -m "wiki: regenerate from repository"
    git push

Changelog:
  1.0.0 (2026-06-05) first issue: Home, Claims-Ledger, Gate-Registry, Roadmap,
        Negative-Results, Predictions, Reviewing, Catalog-Summary.
  1.0.1 (2026-06-05) skip claims/_TEMPLATE (was counted as an 18th claim, tier T0).
  1.1.0 (2026-06-05) output to a temp dir (--out override); build/ area retired repo-wide.
"""
__version__ = "1.1.0"
__first_issued__ = "2026-06-05"
__version_issued__ = "2026-06-05"

import argparse
import datetime as _dt
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def banner(sources):
    src = ", ".join(f"`{s}`" for s in sources)
    return ("> **AUTO-GENERATED** by `verification/scripts/build_wiki.py` from " + src +
            f" on {_dt.date.today().isoformat()}. Do not edit the wiki by hand — "
            "regenerate and re-push. The repository is the only source of truth.\n\n")


def load_cards():
    cards = []
    for d in sorted((REPO / "claims").iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        sj = d / "status.json"
        if sj.exists():
            cards.append(json.loads(sj.read_text(encoding="utf-8")))
    return cards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="OWNER/REPO", help="owner/name for blob links")
    ap.add_argument("--out", default=None,
                    help="output dir (default: fresh temp dir, printed)")
    args = ap.parse_args()
    blob = f"https://github.com/{args.repo}/blob/main/"
    OUT = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="tect-wiki-"))
    OUT.mkdir(parents=True, exist_ok=True)
    cards = load_cards()

    tiers = {}
    for c in cards:
        tiers[c["tier"]] = tiers.get(c["tier"], 0) + 1
    tier_line = " · ".join(f"{t}: {n}" for t, n in sorted(tiers.items()))

    pages = {}
    pages["Home.md"] = banner(["claims/*/status.json", "README.md"]) + f"""# TECT — verification-first research programme

TECT is operated as a Unified Classical Field Theory / partial-TOE research
programme. No TOE-level claim is made; every result is a claim card with a
precise statement, pinned scope, named hypotheses, a falsifier, and a TSv2
maturity tier. **{len(cards)} claims** · {tier_line}.

- [[Claims-Ledger]] — every claim with tier, lifecycle, gates
- [[Gate-Registry]] — promotion gates and named hypotheses
- [[Roadmap]] — 6-stage roadmap and priority queue
- [[Negative-Results]] — failed branches (trust assets)
- [[Predictions]] — prediction ledger and freeze protocol
- [[Reviewing]] — how to attack TECT in 30 minutes
- [[Catalog-Summary]] — artefact counts

Live website (always-current, fetches the repo at view time):
see the repository's GitHub Pages. Canonical record: [{args.repo}](https://github.com/{args.repo}).
"""

    rows = "\n".join(
        f"| [{c['id']}]({blob}claims/{c['id']}/claim.md) | {c['title']} | {c['sector']} "
        f"| {c['tier']}{' (T7-cand.)' if c['t7_candidate'] else ''} | {c['lifecycle']} "
        f"| {', '.join(c['open_gates']) or '—'} |" for c in cards)
    pages["Claims-Ledger.md"] = banner(["claims/*/status.json"]) + f"""# Claims ledger

| ID | Title | Sector | Tier | Lifecycle | Open gates |
|---|---|---|---|---|---|
{rows}

Reading rules: T5 = closed only within its pinned scope; T6 = theorem modulo
listed hypotheses; T7-cand. = legacy-proved, re-entering at T6 pending a
reproduction package (no-auto-T7 rule).
"""

    for page, src, title in [
        ("Gate-Registry.md", "claims/GATES.md", None),
        ("Roadmap.md", "ROADMAP.md", None),
        ("Negative-Results.md", "negative-results/registry.md", None),
        ("Predictions.md", "predictions/prediction-ledger.md", None),
        ("Reviewing.md", "REVIEWING.md", None)]:
        body = (REPO / src).read_text(encoding="utf-8")
        pages[page] = banner([src]) + body

    cat = json.loads((REPO / "verification" / "catalog.json").read_text(encoding="utf-8"))
    kinds = {}
    for e in cat["entries"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    pages["Catalog-Summary.md"] = banner(["verification/catalog.json"]) + (
        f"# Catalog summary\n\n{len(cat['entries'])} tracked artefacts.\n\n" +
        "| Kind | Count |\n|---|---|\n" +
        "\n".join(f"| {k} | {n} |" for k, n in sorted(kinds.items())) +
        f"\n\nFull table: [CATALOG.md]({blob}CATALOG.md)\n")

    for name, text in pages.items():
        (OUT / name).write_text(text, encoding="utf-8")
    print(f"WIKI: {len(pages)} pages -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
