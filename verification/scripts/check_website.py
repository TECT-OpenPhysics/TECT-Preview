#!/usr/bin/env python3
"""Semantic smoke gate for the compact live website."""

__version__ = "1.0.0"
__first_issued__ = "2026-08-10"
__version_issued__ = "2026-08-10"

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main():
    errors = []
    app = (REPO / "publish/website/app.js").read_text(encoding="utf-8")
    html = (REPO / "publish/website/index.html").read_text(encoding="utf-8")
    summary = json.loads((REPO / "verification/catalog-summary.json").read_text(encoding="utf-8"))
    paths = summary.get("claim_status_paths", [])
    exact = re.compile(r"claims/(?!_)[^/]+/status\.json\Z")
    if summary.get("claim_count") != 49 or len(paths) != 49:
        errors.append(f"canonical claim index is not 49: {summary.get('claim_count')}/{len(paths)}")
    if any(not exact.fullmatch(path) for path in paths):
        errors.append("claim_status_paths includes a noncanonical or nested card")
    ids = []
    for path in paths:
        payload = json.loads((REPO / path).read_text(encoding="utf-8"))
        ids.append(payload.get("id"))
    if len(ids) != len(set(ids)):
        errors.append("canonical website claim IDs are not unique")

    required = (
        'fetchJSON("verification/catalog-summary.json")',
        'fetchJSON("verification/catalog/index.json")',
        'mdPage("Changelog", "changelog/INDEX.md")',
        'mdPage("Current research management", "management/INDEX.md")',
        'mdPage("Gate & hypothesis index", "claims/GATES-INDEX.md")',
        'mdPage("Reusable results index", "results/INDEX.md")',
        'mdPage("Proof-evidence entry", "theory/proof-evidence/INDEX.md")',
        "rewriteRepoLinks",
        "esc(c.statement)",
        "esc(c.falsifier)",
        "SLUG_RE",
        'repoLink.textContent = "Repository: ";',
    )
    for token in required:
        if token not in app:
            errors.append(f"website contract missing: {token}")
    legacy_catalog = "verification/catalog" + ".json"
    forbidden = (legacy_catalog, "Top priority: STEP-5B", "${SLUG}</a>")
    for token in forbidden:
        if token in app:
            errors.append(f"website retains forbidden legacy/raw pattern: {token}")

    for route in ("#/roadmap", "#/catalog", "#/changelog", "#/results", "#/evidence"):
        if route not in html:
            errors.append(f"navigation route missing: {route}")
    for relative in (
        "claims/GATES-INDEX.md", "management/INDEX.md", "negative-results/INDEX.md",
        "results/INDEX.md", "theory/proof-evidence/INDEX.md", "changelog/INDEX.md",
        "verification/catalog/index.json",
    ):
        if not (REPO / relative).exists():
            errors.append(f"website target missing: {relative}")

    if errors:
        print("WEBSITE-SMOKE: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("WEBSITE-SMOKE: PASS -- 49 canonical cards, compact routes, escaped text, validated slug")
    return 0


if __name__ == "__main__":
    sys.exit(main())
