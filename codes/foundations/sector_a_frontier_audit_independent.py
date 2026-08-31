#!/usr/bin/env python3
"""Independently recompute the additive Sector-A frontier contract.

The primary audit is intentionally not imported.  This reader reconstructs
the Sector-A status/dependency frontier and the two programme lane contracts
from source files, then emits a compact fingerprint for integration.  It is a
T0 metadata check only: it neither edits authorities nor proves an analytic,
physical, QFT, Yang--Mills, continuum, or mass-gap statement.
"""

from __future__ import annotations

import argparse
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
    / "independent.json"
)
AUDIT_ID = "SECTOR-A-FRONTIER-AUDIT-INDEPENDENT-v1"
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


def read_sector_a() -> dict[str, dict[str, Any]]:
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
    return cards


def core_payload() -> dict[str, Any]:
    cards = read_sector_a()
    ids = sorted(cards)
    id_set = set(ids)
    dependencies = {
        card_id: sorted(
            set(cards[card_id].get("dependencies", []))
            | set(cards[card_id].get("soft_dependencies", []))
        )
        for card_id in ids
    }
    unresolved = {
        card_id: sorted(dep for dep in deps if dep not in id_set)
        for card_id, deps in dependencies.items()
        if any(dep not in id_set for dep in deps)
    }
    gate_consumers: dict[str, list[str]] = {}
    for card_id in ids:
        for gate in sorted(set(cards[card_id].get("open_gates", []))):
            gate_consumers.setdefault(gate, []).append(card_id)
    open_gates = sorted(gate_consumers)
    programme = load_json(PROGRAMME)
    lanes = programme.get("lanes", {})
    forward = lanes.get("forward", {})
    inverse = lanes.get("inverse", {})
    lane_contract = {
        "forward": {
            "task_id": forward.get("task_id"),
            "science_gate": forward.get("science_gate"),
        },
        "inverse": {
            "task_id": inverse.get("task_id"),
            "science_gate": inverse.get("science_gate"),
        },
    }
    a5 = cards.get("A5-SECTOR-A-SYNTHESIS", {})
    a5_dependencies = sorted(a5.get("dependencies", []))
    fingerprint_input = {
        "sector_a_ids": ids,
        "dependencies": dependencies,
        "open_gate_union": open_gates,
        "a5_dependencies": a5_dependencies,
        "a5_contract": {
            "tier": a5.get("tier"),
            "lifecycle": a5.get("lifecycle"),
            "open_gates": sorted(a5.get("open_gates", [])),
        },
        "lane_contract": lane_contract,
    }
    encoded = json.dumps(fingerprint_input, sort_keys=True, separators=(",", ":")).encode()
    return {
        "sector_a_ids": ids,
        "sector_a_card_count": len(ids),
        "dependencies": dependencies,
        "dependency_unresolved": unresolved,
        "open_gate_union": open_gates,
        "gate_consumers": {
            gate: sorted(set(consumers)) for gate, consumers in sorted(gate_consumers.items())
        },
        "a5_dependencies": a5_dependencies,
        "a5_dependency_missing": sorted(dep for dep in a5_dependencies if dep not in id_set),
        "a5_contract": {
            "tier": a5.get("tier"),
            "lifecycle": a5.get("lifecycle"),
            "open_gates": sorted(a5.get("open_gates", [])),
        },
        "lane_contract": lane_contract,
        "core_fingerprint": hashlib.sha256(encoded).hexdigest(),
    }


def run_assertions(core: dict[str, Any]) -> list[dict[str, Any]]:
    ids = core["sector_a_ids"]
    a5 = core["a5_contract"]
    lanes = core["lane_contract"]
    checks = [
        (
            "Sector-A ids are unique",
            len(ids) == len(set(ids)),
            len(ids),
            "unique ids",
        ),
        (
            "all declared dependencies resolve",
            core["dependency_unresolved"] == {},
            core["dependency_unresolved"],
            {},
        ),
        (
            "A5 dependencies resolve",
            core["a5_dependency_missing"] == [],
            core["a5_dependency_missing"],
            [],
        ),
        (
            "A5 remains T6 ACTIVE with no open gates",
            a5 == {"tier": "T6", "lifecycle": "ACTIVE", "open_gates": []},
            a5,
            {"tier": "T6", "lifecycle": "ACTIVE", "open_gates": []},
        ),
        (
            "forward lane remains T-054",
            lanes["forward"]
            == {
                "task_id": "T-054",
                "science_gate": "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
            },
            lanes["forward"],
            {
                "task_id": "T-054",
                "science_gate": "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
            },
        ),
        (
            "inverse lane remains T-059",
            lanes["inverse"]
            == {
                "task_id": "T-059",
                "science_gate": "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE",
            },
            lanes["inverse"],
            {
                "task_id": "T-059",
                "science_gate": "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE",
            },
        ),
        (
            "open gates are named",
            bool(core["open_gate_union"])
            and all(isinstance(gate, str) and gate for gate in core["open_gate_union"]),
            core["open_gate_union"],
            "nonempty named gate set",
        ),
    ]
    return [
        {"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected}
        for name, passed, actual, expected in checks
    ]


def build_report() -> dict[str, Any]:
    core = core_payload()
    assertions = run_assertions(core)
    passed = sum(item["status"] == "PASS" for item in assertions)
    return {
        "schema": "tect/sector-a-frontier-audit-independent/1.0",
        "schema_version": "1.0",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_context": ["A5-SECTOR-A-SYNTHESIS"],
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "SECTOR_A_FRONTIER_INDEPENDENT_PASS"
        if passed == len(assertions)
        else "SECTOR_A_FRONTIER_INDEPENDENT_FAIL",
        "evidence_level": "T0 independent metadata/dependency recomputation",
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "core": core,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "missing_assumptions": [
            "The source status cards correctly declare their dependencies and gates.",
            "This recomputation does not supply any missing owner-level analytic input.",
        ],
        "non_claims": [
            "No authority card, tier, method, functional, owner order, or gate is changed.",
            "No theorem, limit, physical sector, QFT, Yang--Mills, continuum, or mass-gap result is claimed.",
            "Agreement with the primary audit is only a metadata consistency check.",
        ],
        "boundary": "Independent cross-check of the additive Sector-A frontier only; all load-bearing proof gates remain subject to their existing methods.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true", help="assert the recomputed contract")
    args = parser.parse_args()
    report = build_report()
    atomic_write(args.output, report)
    if report["verdict"] != "SECTOR_A_FRONTIER_INDEPENDENT_PASS":
        print("SECTOR-A-FRONTIER-INDEPENDENT: FAIL")
        return 1
    print(
        "SECTOR-A-FRONTIER-INDEPENDENT: PASS "
        f"(cards={report['core']['sector_a_card_count']}; "
        f"open_gates={len(report['core']['open_gate_union'])}; "
        f"assertions={report['assertion_summary']['passed']}/{report['assertion_summary']['total']}; "
        f"fingerprint={report['core']['core_fingerprint']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
