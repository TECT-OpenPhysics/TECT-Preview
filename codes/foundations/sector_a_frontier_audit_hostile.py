#!/usr/bin/env python3
"""Run fail-closed mutation tests against the additive Sector-A frontier.

This hostile harness rebuilds the expected metadata contract from the current
repository and rejects deliberately corrupted payloads.  It is not an
analytic proof and does not alter any authority or method.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PROGRAMME = REPO / "strategy" / "main-proof-program-v1.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A5-SECTOR-A-SYNTHESIS"
    / "runs"
    / "2026-08-31-sector-a-frontier-audit"
    / "hostile.json"
)
AUDIT_ID = "SECTOR-A-FRONTIER-AUDIT-HOSTILE-v1"
EXPLORATION_ID = "EXP-001351"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def source_contract() -> dict[str, Any]:
    cards: dict[str, dict[str, Any]] = {}
    for path in sorted((REPO / "claims").glob("*/status.json")):
        payload = load_json(path)
        if payload.get("sector") != "A":
            continue
        card_id = payload.get("id")
        if not isinstance(card_id, str) or not card_id:
            raise ValueError(f"missing Sector-A id: {path}")
        if card_id in cards:
            raise ValueError(f"duplicate Sector-A id: {card_id}")
        cards[card_id] = payload
    if not cards:
        raise ValueError("no Sector-A status cards")
    ids = sorted(cards)
    dependencies = {
        card_id: sorted(
            set(cards[card_id].get("dependencies", []))
            | set(cards[card_id].get("soft_dependencies", []))
        )
        for card_id in ids
    }
    gate_consumers: dict[str, list[str]] = {}
    for card_id in ids:
        for gate in sorted(set(cards[card_id].get("open_gates", []))):
            gate_consumers.setdefault(gate, []).append(card_id)
    programme = load_json(PROGRAMME)
    lanes = programme.get("lanes", {})
    a5 = cards.get("A5-SECTOR-A-SYNTHESIS", {})
    base = {
        "sector_a_ids": ids,
        "dependencies": dependencies,
        "open_gate_union": sorted(gate_consumers),
        "a5_dependencies": sorted(a5.get("dependencies", [])),
        "a5_contract": {
            "tier": a5.get("tier"),
            "lifecycle": a5.get("lifecycle"),
            "open_gates": sorted(a5.get("open_gates", [])),
        },
        "lane_contract": {
            "forward": {
                "task_id": lanes.get("forward", {}).get("task_id"),
                "science_gate": lanes.get("forward", {}).get("science_gate"),
            },
            "inverse": {
                "task_id": lanes.get("inverse", {}).get("task_id"),
                "science_gate": lanes.get("inverse", {}).get("science_gate"),
            },
        },
    }
    fingerprint_input = json.dumps(base, sort_keys=True, separators=(",", ":")).encode()
    base["core_fingerprint"] = hashlib.sha256(fingerprint_input).hexdigest()
    return base


def valid(payload: dict[str, Any], expected: dict[str, Any]) -> bool:
    """Accept only the exact source-derived contract (fail closed)."""

    fields = (
        "sector_a_ids",
        "dependencies",
        "open_gate_union",
        "a5_dependencies",
        "a5_contract",
        "lane_contract",
    )
    if any(payload.get(field) != expected.get(field) for field in fields):
        return False
    encoded = {field: payload.get(field) for field in fields}
    fingerprint = hashlib.sha256(
        json.dumps(encoded, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return payload.get("core_fingerprint") == fingerprint == expected.get("core_fingerprint")


def mutation_payloads(base: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []
    remove_id = copy.deepcopy(base)
    remove_id["sector_a_ids"] = remove_id["sector_a_ids"][1:]
    mutations.append(("remove-one-sector-a-id", remove_id))

    remove_gate = copy.deepcopy(base)
    remove_gate["open_gate_union"] = remove_gate["open_gate_union"][1:]
    mutations.append(("remove-one-open-gate", remove_gate))

    alter_tier = copy.deepcopy(base)
    alter_tier["a5_contract"]["tier"] = "T7"
    mutations.append(("alter-a5-tier", alter_tier))

    alter_forward = copy.deepcopy(base)
    alter_forward["lane_contract"]["forward"]["task_id"] = "T-999"
    mutations.append(("alter-forward-task", alter_forward))

    inject_dependency = copy.deepcopy(base)
    first_id = inject_dependency["sector_a_ids"][0]
    inject_dependency["dependencies"][first_id] = sorted(
        set(inject_dependency["dependencies"][first_id]) | {"MISSING-DEPENDENCY"}
    )
    mutations.append(("inject-missing-dependency", inject_dependency))
    return mutations


def build_report() -> dict[str, Any]:
    expected = source_contract()
    rows = []
    for name, payload in mutation_payloads(expected):
        rejected = not valid(payload, expected)
        rows.append({"mutation": name, "status": "REJECTED" if rejected else "ACCEPTED"})
    passed = sum(row["status"] == "REJECTED" for row in rows)
    return {
        "schema": "tect/sector-a-frontier-audit-hostile/1.0",
        "schema_version": "1.0",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_context": ["A5-SECTOR-A-SYNTHESIS"],
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "HOSTILE_MUTATIONS_REJECTED"
        if passed == len(rows)
        else "HOSTILE_MUTATION_ACCEPTED",
        "evidence_level": "T0 fail-closed metadata mutation audit",
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "base_core_fingerprint": expected["core_fingerprint"],
        "mutations": rows,
        "mutation_summary": {"rejected": passed, "total": len(rows)},
        "assertions": [
            {
                "name": "every deliberate mutation is rejected",
                "status": "PASS" if passed == len(rows) else "FAIL",
                "actual": {"rejected": passed, "total": len(rows)},
                "expected": "all rejected",
            }
        ],
        "missing_assumptions": [
            "The current source-derived contract is the expected baseline for this audit.",
            "Mutation coverage is finite and does not replace hostile review of analytic proof steps.",
        ],
        "non_claims": [
            "No source authority or proof method is changed.",
            "No physical, QFT, Yang--Mills, continuum, or mass-gap result is claimed.",
            "Mutation rejection does not close any A6-A13 or owner-level gate.",
        ],
        "boundary": "Finite fail-closed mutation coverage for the Sector-A metadata frontier only.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true", help="assert all mutations reject")
    args = parser.parse_args()
    report = build_report()
    atomic_write(args.output, report)
    if report["verdict"] != "HOSTILE_MUTATIONS_REJECTED":
        print("SECTOR-A-FRONTIER-HOSTILE: FAIL")
        return 1
    print(
        "SECTOR-A-FRONTIER-HOSTILE: PASS "
        f"(rejected={report['mutation_summary']['rejected']}/"
        f"{report['mutation_summary']['total']}; "
        f"fingerprint={report['base_core_fingerprint']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
