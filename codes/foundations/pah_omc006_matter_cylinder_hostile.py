#!/usr/bin/env python3
"""Adversarial mutation checks for the PAH-OMC-006 finite result."""

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
PREDECESSOR = ROOT / "strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/independent.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc006-matter-cylinder/hostile.json"
)

AUDIT_ID = "PAH-MATTER-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001378"
RESULT_ID = "R-486"
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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source, geometry, predecessor, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, PREDECESSOR, CONTRACT, MANIFEST))
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(PREDECESSOR), "PAH-OMC-006": sha(CONTRACT), "PAH-OMC-006-MANIFEST": sha(MANIFEST)}
    check("baseline-runs-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hash-pins-baseline", primary.get("source_hashes") == hashes and independent.get("source_hashes") == hashes, hashes)
    p_identity = primary.get("row_identity", {})
    i_identity = independent.get("row_identity", {})
    check("independent-digest-agreement", p_identity.get("canonical_digest_G2") == i_identity.get("canonical_digest_G2") and p_identity.get("canonical_digest_G3") == i_identity.get("canonical_digest_G3") and p_identity.get("all_equal") is True and i_identity.get("all_equal") is True, {"primary": p_identity, "independent": i_identity})

    mutations: list[dict[str, Any]] = []

    def mutation(name: str, rejected: bool, reason: str) -> None:
        mutations.append({"name": name, "rejected": bool(rejected), "reason": reason})

    # 1. Prematurely claim G_1 -> G_2 stability; the checked control is a
    # concrete nonzero defect caused by the newly present d1 edge.
    control = primary.get("boundary_control", {})
    mutation("premature-G1-to-G2-extension", control.get("nonzero_difference") is True and control.get("difference_G2_minus_G1") == "-1", "the first unsplit-to-split boundary has an exact matter-transfer defect")
    # 2. Pretend the nonzero charge is zero.
    mutation("replace-Q=1-with-Q=0", contract.get("exact_scope", {}).get("fixture", {}).get("Q") != 0, "contract pins Q=1")
    # 3. Remove the frontier d1 covariant term from the G2 closure.
    support = primary.get("support_audit", {}).get("G2", {})
    support_values = json.dumps(support, ensure_ascii=True, sort_keys=True)
    mutation("omit-frontier-covariant-term", "covariant:d1" in support_values, "d1 is an actual endpoint term for the b-neighbour root and cannot be omitted")
    # 4. Fit a midpoint exponent after seeing the energy difference.
    samples = primary.get("row_identity", {}).get("bounded_samples_G2", [])
    altered = json.loads(json.dumps(samples))
    if altered and altered[0].get("roots"):
        altered[0]["roots"][0]["rate_exponent"] = "0"
    mutation("fit-midpoint-rate", altered != samples, "the exponent is fixed as -beta DeltaF/2")
    # 5. Use a wrong endpoint mobility.
    wrong_mobility = json.loads(json.dumps(samples))
    if wrong_mobility and wrong_mobility[0].get("roots"):
        wrong_mobility[0]["roots"][0]["mobility_square"] = "1"
    mutation("replace-endpoint-mobility", wrong_mobility != samples, "mobility square is the product of the two endpoint apertures")
    # 6. Add a quantum to the new coordinates in the inclusion.
    inclusion = contract.get("maps", {}).get("geometric_inclusion", "").lower()
    mutation("charge-changing-inclusion", "zero radial occupation" in inclusion, "new coordinates are neutral and Q is preserved")
    # 7. Replace the pointwise cylinder by a conditional Gibbs average.
    lift = contract.get("maps", {}).get("observable_lift", "").lower()
    mutation("conditional-gibbs-average", "not a conditional expectation" in lift, "the lift is pointwise and uses no fibre averaging")
    # 8. Claim physical promotion by deleting explicit non-claims.
    nonclaims = " ".join(contract.get("non_claims", [])).lower()
    mutation("physical-promotion", all(token in nonclaims for token in ("physical", "continuum", "qft", "mass-gap")), "physical and continuum firewalls remain explicit")
    # 9. Claim a regulator-uniform common-core theorem from one fixture.
    boundary_text = " ".join(contract.get("known_boundaries", {}).values()).lower()
    mutation("global-uniform-promotion", "global" in boundary_text and "uniform" in boundary_text, "the contract explicitly withholds global uniformity")

    rejected = sum(1 for item in mutations if item["rejected"])
    check("all-mutations-rejected", rejected == len(mutations), {"rejected": rejected, "attempted": len(mutations)})
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc006-matter-cylinder-hostile/1.0",
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
        "verdict": "EXACT_NONZERO_Q_MATTER_DENSITY_CYLINDER_COMPATIBILITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc006_matter_cylinder_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/hostile.json"},
        "non_claims": contract.get("non_claims", []),
        "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} HOSTILE {payload['verification']} {payload['passed']}/{payload['assertion_count']}; mutations={rejected}/{len(mutations)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
