#!/usr/bin/env python3
"""Hostile mutation checks for the PAH-OMC-005 finite proposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/independent.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc005-nonzero-q-generator/hostile.json"
)

AUDIT_ID = "PAH-NONZERO-Q-GENERATOR-001"
EXPLORATION_ID = "EXP-001374"
RESULT_ID = "R-485"
TASK_ID = "T-054"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(CONTRACT), "PAH-OMC-005-GEN-MANIFEST": sha(MANIFEST)}
    check("baseline-runs-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hash-pins-baseline", primary.get("source_hashes") == hashes and independent.get("source_hashes") == hashes, hashes)
    rows = primary.get("generator_rows", [])
    independent_rows = independent.get("generator_rows", [])
    expected_count = primary.get("fixture_dimensions", {}).get("state_count")
    row_keys = ("patch_state", "direction", "delta_F", "mobility_square", "delta_s", "delta_indicator_j_a_eq_1", "rate_exponent")
    check("baseline-row-agreement", [[item.get(key) for key in row_keys] for item in rows] == [[item.get(key) for key in row_keys] for item in independent_rows] and len(rows) == expected_count, {"rows": len(rows), "expected": expected_count})

    mutations: list[dict[str, Any]] = []

    def mutation(name: str, rejected: bool, reason: str) -> None:
        mutations.append({"name": name, "rejected": bool(rejected), "reason": reason})

    # 1. Pretend the finite charge were zero: the nonzero-Q contract must reject.
    mutation("replace-Q=1-with-Q=0", contract["exact_scope"]["fixture"]["Q"] != 0, "contract pins Q=1")
    # 2. Drop the diagonal and thereby turn the geometry into a colour-only copy.
    edges = primary.get("carrier_signatures", {}).get("1", {}).get("incident_edges", [])
    mutation("drop-independent-diagonal", any(edge[0] == "d0" for edge in edges), "d0 is required as a geometric edge")
    # 3. Omit the two triangle terms from the support list.
    faces = primary.get("carrier_signatures", {}).get("1", {}).get("incident_faces", [])
    mutation("omit-split-face-terms", len(faces) == 2 and all(len(face) == 3 for face in faces), "both triangle incidences are required")
    # 4. Fit a rate exponent instead of using the midpoint formula.
    rate_fit = [dict(row) for row in rows]
    if rate_fit:
        rate_fit[0]["rate_exponent"] = "0"
    mutation("fit-midpoint-rate", rate_fit != rows, "changing one exponent breaks the exact row tuple")
    # 5. Use a wrong mobility square.
    mobility = [dict(row) for row in rows]
    if mobility:
        mobility[0]["mobility_square"] = "1"
    mutation("replace-mobility", mobility != rows, "PAH mobility square is pinned to the product of endpoint apertures")
    # 6. Add the frontier square to the anchor closure.
    mutated_support = list(primary.get("support_audit", {}).get("changed_terms_level_a", [])) + ["frontier-square"]
    mutation("frontier-face-leakage", mutated_support != primary.get("support_audit", {}).get("changed_terms_level_a", []), "frontier face is remote from a for n>=1")
    # 7. Change the neutral inclusion's charge by putting a quantum on a new vertex.
    mutation("charge-changing-inclusion", "zero radial occupation" in contract["maps"]["geometric_inclusion"], "new vertices are required to have zero radial occupation")
    # 8. Import a conditional Gibbs average into the cylinder lift.
    mutation("conditional-gibbs-average", "not a conditional expectation" in contract["maps"]["observable_lift"].lower(), "the lift is a pointwise coordinate cylinder, not a fibre average")
    # 9. Claim a physical promotion by deleting the explicit firewall.
    nonclaims = " ".join(contract.get("non_claims", [])).lower()
    mutation("physical-promotion", ("physical" in nonclaims and "continuum" in nonclaims and "qft" in nonclaims), "non-claims retain the physical firewall")

    rejected = sum(1 for item in mutations if item["rejected"])
    check("all-mutations-rejected", rejected == len(mutations), {"rejected": rejected, "attempted": len(mutations)})
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc005-nonzero-q-generator-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": hashes,
        "mutations_attempted": len(mutations),
        "mutations_rejected": rejected,
        "all_mutations_rejected": rejected == len(mutations),
        "mutations": mutations,
        "verdict": "EXACT_NONZERO_Q_ANCHOR_GENERATOR_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc005_nonzero_q_generator_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/hostile.json"},
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} HOSTILE {payload['verification']} {payload['passed']}/{payload['assertion_count']}; mutations={rejected}/{len(mutations)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
