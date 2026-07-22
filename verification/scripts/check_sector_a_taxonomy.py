#!/usr/bin/env python3
"""Validate the canonical Sector-A theorem-family and subproof map.

The check is deliberately structural. It prevents an unclassified Sector-A
claim or an unapproved numeric-ID expansion from entering a release while
preserving every already-issued immutable claim ID.

Usage:
    python verification/scripts/check_sector_a_taxonomy.py --check
    python verification/scripts/check_sector_a_taxonomy.py --self-test
    python verification/scripts/check_sector_a_taxonomy.py --report reviews/report.json
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIMS = REPO / "claims"
DEFAULT_MAP = REPO / "governance" / "sector-a-theorem-map.json"
ID_NUMBER = re.compile(r"^A(\d+)-")
NOTE_VERSION = re.compile(r"-\d{6}(?:-\d{6})?-v\d+\.\d+\.tex\.txt$")
ALLOWED_ROLES = {
    "CANONICAL_INPUT",
    "CONDITIONAL_THEOREM",
    "BRIDGE",
    "BRANCH_THEOREM",
    "CANONICAL_OBJECT",
    "TOP_LEVEL_THEOREM",
    "FOUNDATION",
    "LONG_TERM_THEOREM_ANCHOR",
    "REFERENCE_ENDPOINT",
    "INTERPOLATION_BRIDGE",
    "DEVELOPMENT_ANCHOR",
    "ACTIVE_SUBPROOF_HOST",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def load_cards(claims_dir: Path) -> dict[str, dict[str, Any]]:
    cards: dict[str, dict[str, Any]] = {}
    for status in sorted(claims_dir.glob("A*/status.json")):
        card = json.loads(status.read_text(encoding="utf-8"))
        if card.get("sector") == "A":
            cards[str(card["id"])] = card
    return cards


def lineage_slug(name: str) -> str:
    return NOTE_VERSION.sub("", name)


def current_a13_lineages(claims_dir: Path, host: str) -> set[str]:
    notes = claims_dir / host / "notes"
    if not notes.exists():
        return set()
    return {lineage_slug(path.name) for path in notes.glob("*.tex.txt")}


def validate(
    cards: dict[str, dict[str, Any]],
    theorem_map: dict[str, Any],
    repo: Path,
    claims_dir: Path,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if theorem_map.get("schema") != "tect/sector-a-theorem-map/1.0":
        errors.append("unsupported or missing theorem-map schema")

    policy = theorem_map.get("id_policy", {})
    if policy.get("issued_ids_are_immutable") is not True:
        errors.append("issued-ID immutability must be true")
    criteria = policy.get("new_claim_criteria", [])
    if not isinstance(criteria, list) or len(criteria) != 5:
        errors.append("new-claim policy must contain exactly five criteria")

    seen: dict[str, str] = {}
    roles: dict[str, str] = {}
    family_rows: list[dict[str, Any]] = []
    families = theorem_map.get("families", [])
    if not isinstance(families, list) or not families:
        errors.append("at least one theorem family is required")
        families = []
    for family in families:
        family_id = str(family.get("id", ""))
        entries = family.get("claims", [])
        if not family_id or not isinstance(entries, list) or not entries:
            errors.append(f"invalid or empty family: {family_id or '<missing>'}")
            continue
        member_ids: list[str] = []
        for entry in entries:
            claim_id = str(entry.get("id", ""))
            role = str(entry.get("role", ""))
            if claim_id in seen:
                errors.append(
                    f"claim {claim_id} appears in both {seen[claim_id]} and {family_id}"
                )
            else:
                seen[claim_id] = family_id
                roles[claim_id] = role
            if role not in ALLOWED_ROLES:
                errors.append(f"claim {claim_id} has unsupported role {role}")
            member_ids.append(claim_id)
        family_rows.append(
            {
                "id": family_id,
                "kind": family.get("kind"),
                "claim_count": len(member_ids),
                "claims": member_ids,
            }
        )

    registered = set(cards)
    mapped = set(seen)
    for missing in sorted(registered - mapped):
        errors.append(f"registered Sector-A claim is unclassified: {missing}")
    for unknown in sorted(mapped - registered):
        errors.append(f"theorem map cites an unknown Sector-A claim: {unknown}")

    ceiling = policy.get("current_numeric_ceiling")
    if not isinstance(ceiling, int) or ceiling < 1:
        errors.append("current_numeric_ceiling must be a positive integer")
        ceiling = 0
    approvals = policy.get("approved_new_claims_above_ceiling", [])
    approved: dict[str, dict[str, Any]] = {}
    if not isinstance(approvals, list):
        errors.append("approved_new_claims_above_ceiling must be a list")
        approvals = []
    for approval in approvals:
        claim_id = str(approval.get("id", ""))
        approved[claim_id] = approval
        record = repo / str(approval.get("decision_record", ""))
        if not approval.get("decision_record") or not record.is_file():
            errors.append(f"approved claim {claim_id} lacks an existing decision record")
    for claim_id in sorted(registered):
        match = ID_NUMBER.match(claim_id)
        if match and int(match.group(1)) > ceiling and claim_id not in approved:
            errors.append(
                f"claim {claim_id} exceeds the A{ceiling} ceiling without approval"
            )

    frontier = theorem_map.get("active_frontier", {})
    host = str(frontier.get("host_claim", ""))
    if host not in registered:
        errors.append(f"active frontier host is not a registered claim: {host}")
    elif roles.get(host) != "ACTIVE_SUBPROOF_HOST":
        errors.append(f"active frontier host {host} lacks ACTIVE_SUBPROOF_HOST role")
    if frontier.get("record_as") != "SUBPROOF":
        errors.append("active frontier must be recorded as SUBPROOF")
    selected = str(frontier.get("selected_subproof", ""))
    host_prefix = ID_NUMBER.match(host)
    if not selected or not host_prefix or not selected.startswith(
        f"A{host_prefix.group(1)}-"
    ):
        errors.append("selected subproof must inherit the active host numeric prefix")
    current_child = str(frontier.get("current_child", ""))
    if current_child and (
        not host_prefix or not current_child.startswith(f"A{host_prefix.group(1)}-")
    ):
        errors.append("current child must inherit the active host numeric prefix")

    taxonomy = theorem_map.get("subproof_taxonomy", {}).get(host, [])
    prefixes: dict[str, str] = {}
    for group in taxonomy:
        group_name = str(group.get("name", ""))
        for prefix in group.get("lineage_prefixes", []):
            prefix = str(prefix)
            if prefix in prefixes:
                errors.append(
                    f"lineage prefix {prefix} appears in two subproof groups"
                )
            prefixes[prefix] = group_name
    lineages = current_a13_lineages(claims_dir, host) if host else set()
    unassigned: list[str] = []
    multiply_assigned: list[str] = []
    for lineage in sorted(lineages):
        matches = [prefix for prefix in prefixes if lineage.startswith(prefix)]
        if not matches:
            unassigned.append(lineage)
        elif len(matches) > 1:
            multiply_assigned.append(lineage)
    if unassigned:
        errors.append("unassigned active-host note lineages: " + ", ".join(unassigned))
    if multiply_assigned:
        errors.append(
            "multiply assigned active-host note lineages: "
            + ", ".join(multiply_assigned)
        )

    report = {
        "schema": "tect/sector-a-theorem-map-audit/1.0",
        "map_version": theorem_map.get("version"),
        "registered_claim_cards": len(registered),
        "theorem_families": len(family_rows),
        "mapped_claim_cards": len(mapped & registered),
        "unclassified_claim_cards": sorted(registered - mapped),
        "current_numeric_ceiling": ceiling,
        "active_frontier": frontier,
        "active_host_note_lineages": sorted(lineages),
        "active_host_unassigned_lineages": unassigned,
        "families": family_rows,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    return errors, report


def self_test() -> None:
    cards = load_cards(CLAIMS)
    theorem_map = json.loads(DEFAULT_MAP.read_text(encoding="utf-8"))
    errors, _ = validate(cards, theorem_map, REPO, CLAIMS)
    assert not errors, errors

    missing_map = copy.deepcopy(theorem_map)
    missing_map["families"][0]["claims"].pop()
    errors, _ = validate(cards, missing_map, REPO, CLAIMS)
    assert any("unclassified" in error for error in errors)

    duplicate_map = copy.deepcopy(theorem_map)
    duplicate_map["families"][0]["claims"].append(
        copy.deepcopy(duplicate_map["families"][1]["claims"][0])
    )
    errors, _ = validate(cards, duplicate_map, REPO, CLAIMS)
    assert any("appears in both" in error for error in errors)

    expanded_cards = copy.deepcopy(cards)
    expanded_cards["A14-MOCK-UNAPPROVED"] = {
        "id": "A14-MOCK-UNAPPROVED",
        "sector": "A",
    }
    expanded_map = copy.deepcopy(theorem_map)
    expanded_map["families"][-1]["claims"].append(
        {"id": "A14-MOCK-UNAPPROVED", "role": "DEVELOPMENT_ANCHOR"}
    )
    errors, _ = validate(expanded_cards, expanded_map, REPO, CLAIMS)
    assert any("exceeds the A13 ceiling" in error for error in errors)

    wrong_frontier = copy.deepcopy(theorem_map)
    wrong_frontier["active_frontier"]["record_as"] = "CLAIM"
    errors, _ = validate(cards, wrong_frontier, REPO, CLAIMS)
    assert any("recorded as SUBPROOF" in error for error in errors)
    print("SECTOR-A-TAXONOMY SELF-TEST: PASS (5 scenarios)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()

    if arguments.self_test:
        self_test()
        return 0

    map_path = arguments.map.resolve()
    theorem_map = json.loads(map_path.read_text(encoding="utf-8"))
    cards = load_cards(CLAIMS)
    errors, report = validate(cards, theorem_map, REPO, CLAIMS)
    report["map"] = str(map_path.relative_to(REPO)).replace("\\", "/")
    report["map_sha256"] = digest(map_path)
    if arguments.report:
        output = arguments.report
        if not output.is_absolute():
            output = REPO / output
        atomic_json(output, report)
        print(f"  report: {output.relative_to(REPO)}")
    if errors:
        print(f"SECTOR-A-TAXONOMY: FAIL ({len(errors)} error(s))")
        for error in errors:
            print(f"  ERR {error}")
        return 1
    print(
        "SECTOR-A-TAXONOMY: PASS "
        f"({report['registered_claim_cards']} cards -> "
        f"{report['theorem_families']} theorem families; "
        "0 unclassified)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
