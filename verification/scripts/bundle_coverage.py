#!/usr/bin/env python3
"""bundle_coverage.py -- claim-level reproduction-bundle coverage report.

This reflects reproduction-bundle-policy.md sec.14: bundles are main-line,
claim-level artefacts under `claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/`.
Sub-proof-folder bundle coverage was retired on 2026-06-11. Therefore the
failing coverage gate is the operator-confirmed main-proof-line registry, not
every T5+ claim in the repository.

Usage:
    python verification/scripts/bundle_coverage.py
"""
__version__ = "2.0.1"
__first_issued__ = "2026-06-10"
__version_issued__ = "2026-07-20"

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RANK = {"T7": 7, "T6": 6, "T5": 5, "T4": 4, "T3": 3, "T2": 2, "T1": 1, "T0": 0}


def _load_status(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_rows(claim_dir):
    rows = []
    for manifest in sorted((claim_dir / "bundle").glob("*/MANIFEST.json")):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append((manifest.parent.name, "BAD-MANIFEST", str(exc)))
            continue
        runlog = data.get("runlog", {})
        all_pass = all(v.get("exit") == 0 and "FAIL" not in v.get("pass_line", "") for v in runlog.values())
        commit = str(data.get("repo_commit", ""))
        stamped = bool(commit) and "TO BE STAMPED" not in commit
        if all_pass and stamped:
            status = "PUBLISHED"
        elif all_pass:
            status = "UNSTAMPED"
        else:
            status = "FAILING"
        ref = f"claims/{claim_dir.name}/bundle/{manifest.parent.name}"
        rows.append((manifest.parent.name, status, data.get("bundle_digest", "")[:12], ref))
    return rows


def _mainline_bundles():
    path = REPO / "theory" / "main-proof-line.md"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    refs = set()
    for ref in re.findall(r"`([^`]+/bundle/[^`]+)`", text):
        clean = ref.strip("/")
        if not clean.startswith("claims/"):
            clean = "claims/" + clean
        refs.add(clean)
    return refs


def _registered_bundle_refs(card):
    refs = set()
    for item in card.get("legacy_evidence", []):
        text = str(item).strip()
        for ref in re.findall(r"claims/[A-Z0-9-]+/bundle/[A-Za-z0-9_.\-/]+", text):
            refs.add(ref.rstrip("/"))
    notes = str(card.get("notes", ""))
    for ref in re.findall(r"claims/[A-Z0-9-]+/bundle/[A-Za-z0-9_.\-/]+", notes):
        refs.add(ref.rstrip("/"))
    return refs


def main():
    mainline = _mainline_bundles()
    rows = []
    mainline_gaps = []
    for claim_dir in sorted((REPO / "claims").iterdir()):
        status_path = claim_dir / "status.json"
        if not claim_dir.is_dir() or not status_path.exists():
            continue
        card = _load_status(status_path)
        tier = str(card.get("tier", "?")).split()[0]
        rank = RANK.get(tier, -1)
        bundles = _bundle_rows(claim_dir)
        registered_refs = _registered_bundle_refs(card)
        claim_bundle_refs = {b[3] for b in bundles}
        is_mainline = any(ref in mainline for ref in claim_bundle_refs)
        is_card_registered = bool(registered_refs & claim_bundle_refs)
        preferred = [b for b in bundles if b[3] in registered_refs]
        if not preferred:
            preferred = [b for b in bundles if b[3] in mainline]
        if not preferred:
            preferred = bundles[-1:] if bundles else []
        # A claim may intentionally retain immutable bundles from earlier
        # tiers.  Among otherwise registered/main-line candidates, prefer the
        # bundle whose stamped name matches the card's current tier instead of
        # silently choosing the lexicographically last historical bundle.
        current_tier_preferred = [b for b in preferred if f"-{tier}-" in b[0]]
        if current_tier_preferred:
            preferred = current_tier_preferred
        current = preferred[-1] if preferred else ("-", "NO-BUNDLE", "", "")
        if is_mainline:
            requirement = "MAIN-LINE"
        elif is_card_registered:
            requirement = "CARD-REF"
        elif rank >= 5:
            requirement = "NON-MAIN"
        elif rank == 4:
            requirement = "optional"
        else:
            requirement = "-"
        rows.append((card["id"], tier, requirement, current[0], current[1], current[2], len(bundles)))
        if is_mainline and current[1] in {"NO-BUNDLE", "UNSTAMPED", "FAILING", "BAD-MANIFEST"}:
            mainline_gaps.append(card["id"])

    print(f"{'claim':42} {'tier':4} {'req':11} {'current-bundle':38} {'status':12} digest")
    for cid, tier, req, bundle, status, digest, count in rows:
        suffix = f" ({count} total)" if count else ""
        print(f"{cid:42} {tier:4} {req:11} {bundle[:38]:38} {status:12} {digest}{suffix}")
    print()
    print(f"MAIN-LINE bundle refs: {len(mainline)}; gaps: {len(mainline_gaps)}")
    if mainline_gaps:
        print("MAIN-LINE GAPS: " + ", ".join(mainline_gaps))
    return 1 if mainline_gaps else 0


if __name__ == "__main__":
    sys.exit(main())
