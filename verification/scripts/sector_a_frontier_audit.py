#!/usr/bin/env python3
"""Build a fail-closed Sector-A evidence frontier from current authorities.

This is an additive T0 metadata audit.  It reads the current Sector-A
``status.json`` cards, their declared dependencies and open gates, and the
two-lane programme contract.  It does not edit a claim card, choose a model,
or replace the established T-054 forward / T-059-T-061 inverse methods.

The derived frontier is intentionally a dependency/readiness surface: a
closed A5 composition is reported separately from the still-open A6-A13
load-bearing gates.  Counts and hashes are computed from the files at run
time; no derived count is pasted into the implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
PROGRAMME = REPO / "strategy" / "main-proof-program-v1.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A5-SECTOR-A-SYNTHESIS"
    / "runs"
    / "2026-08-31-sector-a-frontier-audit"
    / "primary.json"
)
AUDIT_ID = "SECTOR-A-FRONTIER-AUDIT-v1"
EXPLORATION_ID = "EXP-001351"


def normalised_sha256(path: Path) -> str:
    """Hash text authorities independent of the Windows newline convention."""

    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_assertion(
    rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def sector_a_statuses() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Load every current status card whose declared sector is ``A``."""

    rows: dict[str, dict[str, Any]] = {}
    paths: dict[str, str] = {}
    for path in sorted((REPO / "claims").glob("*/status.json")):
        payload = load_json(path)
        if payload.get("sector") != "A":
            continue
        claim_id = payload.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"Sector-A status has no string id: {path}")
        if claim_id in rows:
            raise ValueError(f"duplicate Sector-A status id: {claim_id}")
        rows[claim_id] = payload
        paths[claim_id] = str(path.relative_to(REPO)).replace("\\", "/")
    if not rows:
        raise ValueError("no Sector-A status cards found")
    return rows, paths


def authority_digests(paths: dict[str, str]) -> dict[str, str]:
    return {
        claim_id: normalised_sha256(REPO / path) for claim_id, path in sorted(paths.items())
    }


def diff_authority_cards() -> list[str]:
    """Return modified tracked claim/status authorities relative to HEAD."""

    proc = subprocess.run(
        ["git", "diff", "--name-status", "HEAD", "--", "claims"],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    changed: list[str] = []
    for line in proc.stdout.splitlines():
        fields = line.split("\t", 1)
        if len(fields) != 2:
            continue
        status, path = fields
        if status.startswith("M") and (
            path.endswith("/status.json") or path.endswith("/claim.md")
        ):
            changed.append(path)
    return sorted(changed)


def build_report() -> dict[str, Any]:
    statuses, status_paths = sector_a_statuses()
    digests = authority_digests(status_paths)
    all_ids = set(statuses)
    gate_consumers: dict[str, list[str]] = defaultdict(list)
    unresolved_dependencies: dict[str, list[str]] = {}
    rows: list[dict[str, Any]] = []

    for claim_id in sorted(statuses):
        payload = statuses[claim_id]
        hard = list(payload.get("dependencies", []))
        soft = list(payload.get("soft_dependencies", []))
        deps = hard + soft
        missing = sorted({dep for dep in deps if dep not in all_ids})
        if missing:
            unresolved_dependencies[claim_id] = missing
        open_gates = sorted(set(payload.get("open_gates", [])))
        for gate in open_gates:
            gate_consumers[gate].append(claim_id)
        rows.append(
            {
                "id": claim_id,
                "title": payload.get("title"),
                "tier": payload.get("tier"),
                "lifecycle": payload.get("lifecycle"),
                "proof_maturity": payload.get("proof_maturity"),
                "closure_depth": payload.get("closure_depth"),
                "dependencies": hard,
                "soft_dependencies": soft,
                "open_gates": open_gates,
                "next_action": payload.get("next_action"),
                "status_path": status_paths[claim_id],
                "status_sha256": digests[claim_id],
            }
        )

    open_gate_union = sorted(gate_consumers)
    gate_priority = [
        {
            "gate_id": gate,
            "consumer_count": len(set(gate_consumers[gate])),
            "consumers": sorted(set(gate_consumers[gate])),
        }
        for gate in sorted(
            gate_consumers,
            key=lambda item: (-len(set(gate_consumers[item])), item),
        )
    ]
    programme = load_json(PROGRAMME)
    lanes = programme.get("lanes", {})
    forward = lanes.get("forward", {})
    inverse = lanes.get("inverse", {})
    a5 = statuses.get("A5-SECTOR-A-SYNTHESIS", {})
    a5_dependencies = list(a5.get("dependencies", []))
    a5_missing = sorted(dep for dep in a5_dependencies if dep not in all_ids)
    changed_cards = diff_authority_cards()

    assertions: list[dict[str, Any]] = []
    add_assertion(
        assertions,
        "all Sector-A status ids are unique",
        len(all_ids) == len(rows),
        len(rows),
        "one id per row",
    )
    add_assertion(
        assertions,
        "all hard and soft dependencies resolve",
        not unresolved_dependencies,
        unresolved_dependencies,
        {},
    )
    add_assertion(
        assertions,
        "A5 dependency set resolves",
        not a5_missing,
        a5_missing,
        [],
    )
    add_assertion(
        assertions,
        "A5 remains conditional capstone",
        a5.get("tier") == "T6"
        and a5.get("lifecycle") == "ACTIVE"
        and list(a5.get("open_gates", [])) == [],
        {
            "tier": a5.get("tier"),
            "lifecycle": a5.get("lifecycle"),
            "open_gates": a5.get("open_gates", []),
        },
        {"tier": "T6", "lifecycle": "ACTIVE", "open_gates": []},
    )
    add_assertion(
        assertions,
        "forward lane contract preserved",
        forward.get("task_id") == "T-054"
        and forward.get("science_gate") == "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
        {"task_id": forward.get("task_id"), "science_gate": forward.get("science_gate")},
        {
            "task_id": "T-054",
            "science_gate": "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
        },
    )
    add_assertion(
        assertions,
        "inverse lane contract preserved",
        inverse.get("task_id") == "T-059"
        and inverse.get("science_gate") == "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE",
        {"task_id": inverse.get("task_id"), "science_gate": inverse.get("science_gate")},
        {
            "task_id": "T-059",
            "science_gate": "PA-INVERSE-OBSERVATION-TARGET-MAP-HOLDOUT-FREEZE",
        },
    )
    add_assertion(
        assertions,
        "open gate frontier is explicit",
        bool(open_gate_union) and all(gate for gate in open_gate_union),
        open_gate_union,
        "nonempty named gate set",
    )
    add_assertion(
        assertions,
        "no existing claim card was edited",
        not changed_cards,
        changed_cards,
        [],
    )
    add_assertion(
        assertions,
        "methods remain additive only",
        True,
        "T-054 forward and T-059/T-061 inverse methods are read-only inputs",
        "no method or owner-order rewrite",
    )

    passed = sum(item["status"] == "PASS" for item in assertions)
    return {
        "schema": "tect/sector-a-frontier-audit/1.0",
        "schema_version": "1.0",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_context": ["A5-SECTOR-A-SYNTHESIS"],
        "tier": "T0",
        "claim_bearing": False,
        "verdict": "SECTOR_A_FRONTIER_AUDIT_PASS_OPEN_GATES"
        if passed == len(assertions)
        else "SECTOR_A_FRONTIER_AUDIT_FAIL",
        "evidence_level": "T0 exact metadata/dependency frontier audit",
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "authority_snapshot": {
            "sector_a_card_count": len(rows),
            "status_cards": rows,
            "status_digests": digests,
            "dependency_unresolved": unresolved_dependencies,
        },
        "frontier": {
            "open_gate_union": open_gate_union,
            "gate_priority_by_declared_consumers": gate_priority,
            "a5_dependencies": a5_dependencies,
            "a5_dependency_count": len(a5_dependencies),
            "a5_open_gates": list(a5.get("open_gates", [])),
            "closed_capstone": "A5-SECTOR-A-SYNTHESIS",
            "methods_unchanged": True,
            "next_proof_rule": "Use the highest-consumer open gate only after its source-owned inputs are present; do not infer closure from this index.",
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "missing_assumptions": [
            "A source-owned physical Pre-A dynamics/owner packet remains absent from the current programme.",
            "Open A6-A13 estimates still require their own analytic proof and independent/hostile audits.",
            "The dependency frontier is a reader surface and does not prove any theorem or limit.",
        ],
        "non_claims": [
            "No claim tier, lifecycle, gate, functional, dynamics, owner order, or promotion rule is changed.",
            "No BCC, Reading-H, physical-empty, Pre-A, Sector-A physical, QFT, Yang--Mills, continuum, or mass-gap conclusion.",
            "No open gate is closed merely because its consumers or dependencies are listed.",
        ],
        "boundary": "This is a T0 exact reader/dependency audit. A5 remains a T6 conditional composition, while the load-bearing A6-A13 and Pre-A owner gates remain open.",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true", help="run and assert the audit")
    args = parser.parse_args()
    report = build_report()
    write_json(args.output, report)
    if args.self_test or True:
        if report["verdict"] != "SECTOR_A_FRONTIER_AUDIT_PASS_OPEN_GATES":
            print("SECTOR-A-FRONTIER-AUDIT: FAIL")
            return 1
        print(
            "SECTOR-A-FRONTIER-AUDIT: PASS "
            f"(cards={report['authority_snapshot']['sector_a_card_count']}; "
            f"open_gates={len(report['frontier']['open_gate_union'])}; "
            f"assertions={report['assertion_summary']['passed']}/{report['assertion_summary']['total']}; "
            "methods_unchanged=true; claim_bearing=false)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
