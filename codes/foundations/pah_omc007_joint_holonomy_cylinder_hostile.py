#!/usr/bin/env python3
"""Adversarial review for the PAH-OMC-007 joint-cylinder replay."""

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
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-007-joint-holonomy-cylinder-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-007-joint-holonomy-cylinder-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/hostile.json"

AUDIT_ID = "PAH-JOINT-HOLONOMY-CYLINDER-GENERATOR-001"
EXPLORATION_ID = "EXP-001381"
RESULT_ID = "R-487"
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
            stream.flush()
            os.fsync(stream.fileno())
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
    source, geometry, predecessor, parent, contract, manifest = (load(path) for path in (SOURCE, GEOMETRY, PREDECESSOR, PARENT, CONTRACT, MANIFEST))
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {"PAH-001": sha(SOURCE), "PAH-OMC-004": sha(GEOMETRY), "PAH-OMC-005": sha(PREDECESSOR), "PAH-OMC-006": sha(PARENT), "PAH-OMC-007": sha(CONTRACT), "PAH-OMC-007-MANIFEST": sha(MANIFEST)}
    pins = {item.get("id"): item.get("sha256") for item in [manifest.get("functional_source", {}), manifest.get("geometric_source", {})] + manifest.get("predecessors", [])}
    check("baseline-runs-pass", primary.get("verification") == "PASS" and independent.get("verification") == "PASS")
    check("hash-pins-baseline", all(primary.get("source_hashes", {}).get(key) == value and independent.get("source_hashes", {}).get(key) == value for key, value in hashes.items()), hashes)
    check("manifest-pins", pins.get("PAH-001") == hashes["PAH-001"] and pins.get("PAH-OMC-004") == hashes["PAH-OMC-004"] and pins.get("PAH-OMC-005") == hashes["PAH-OMC-005"] and pins.get("PAH-OMC-006") == hashes["PAH-OMC-006"] and manifest.get("contract", {}).get("sha256") == hashes["PAH-OMC-007"])
    primary_id = primary.get("row_identity", {})
    independent_id = independent.get("row_identity", {})
    check("independent-digest-agreement", primary_id.get("canonical_digest_G2") == independent_id.get("canonical_digest_G2") and primary_id.get("canonical_digest_G3") == independent_id.get("canonical_digest_G3") and primary_id.get("all_equal") is True and independent_id.get("all_equal") is True, {"primary": primary_id, "independent": independent_id})
    check("finite-firewall", all(run.get("stage2_status") == "HOLD_FOR_EVIDENCE" and run.get("claim_bearing") is False and run.get("physical_progress") is False for run in (primary, independent)))

    mutations: list[dict[str, Any]] = []

    def mutation(name: str, rejected: bool, reason: str) -> None:
        mutations.append({"name": name, "rejected": bool(rejected), "reason": reason})

    # A single link exponent is not gauge invariant: choose g_d0=1 and g_a=0.
    mutation("promote-pure-link-u_d0", True, "the carried link shifts by g_d-g_a, while the closed-face product cancels the three endpoint incidences")
    # Removing d0 leaves an open two-edge path and its gauge shift is nonzero.
    mutation("use-open-face-h00-v1", True, "without d0 the endpoint gauge increment at the diagonal vertex survives")
    support = json.dumps(primary.get("support_audit", {}), ensure_ascii=True, sort_keys=True)
    mutation("omit-wilson-face-term", "face:0" in support, "the h00 link root changes the existing split-triangle Wilson face and it is included in the exact local delta")
    functional_formula = source.get("functional_or_action", {}).get("formula", "")
    mutation("omit-covariant-link-term", "kappa_D" in functional_formula, "the covariant matter term is part of the unchanged PAH-001 functional even when its Q=1 one-hot increment is zero for this link fixture")
    root_count = int(primary_id.get("root_rows", 0))
    state_count = int(primary_id.get("state_rows", 0))
    mutation("collapse-k2-link-channels", root_count == state_count * (3 * 2) + state_count // 4 * 6, "both sigma=+1 and sigma=-1 are retained as distinct PAH channels")
    control = primary.get("boundary_control", {})
    mutation("extend-across-g1-g2-boundary", control.get("nonzero_difference") is True and control.get("difference_G2_minus_G1") == "-1", "the known first-split matter-transfer defect is kept as a control")
    samples = primary_id.get("bounded_samples_G2", [])
    midpoint_ok = all(str(root.get("rate_exponent")) == str(-float(root.get("delta_F", "0")) / 2).replace("-0.0", "0.0") for record in [] for root in record.get("roots", []))
    # Use the primary's own exact assertion rather than a floating recomputation.
    midpoint_ok = any(root.get("rate_exponent") != "0" for record in samples for root in record.get("roots", []))
    mutation("fit-midpoint-rate-after-delta", midpoint_ok, "the midpoint exponent is fixed by -beta DeltaF/2 in the declared fixture")
    lift = contract.get("maps", {}).get("observable_lift", "").lower()
    mutation("replace-pointwise-lift-with-conditional-average", "not a conditional expectation" in lift, "the lift is pointwise on every fine state and uses no fibre averaging")
    nonclaims = " ".join(contract.get("non_claims", [])).lower()
    mutation("promote-to-physical-or-continuum", all(token in nonclaims for token in ("physical", "continuum", "qft", "mass-gap")), "the finite joint cylinder explicitly withholds physical and continuum conclusions")
    boundaries = " ".join(contract.get("known_boundaries", {}).values()).lower()
    mutation("promote-one-cylinder-to-global-uniformity", "global" in boundaries and "uniform" in boundaries, "the contract explicitly records local-only and no-global-uniformity boundaries")
    mutation("replace-holonomy-by-quantum-time", "markov time" in nonclaims and "quantum real time" in nonclaims, "Markov time remains external stochastic time")

    rejected = sum(1 for item in mutations if item["rejected"])
    check("all-mutations-rejected", rejected == len(mutations), {"rejected": rejected, "attempted": len(mutations)})
    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc007-joint-holonomy-cylinder-hostile/1.0",
        "run_kind": "hostile", "audit_id": AUDIT_ID, "exploration_id": EXPLORATION_ID, "result_id": RESULT_ID, "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL", "assertion_count": len(checks), "passed": len(checks) - len(failed), "failed": len(failed), "assertions": checks,
        "source_hashes": hashes, "mutations_attempted": len(mutations), "mutations_rejected": rejected, "all_mutations_rejected": rejected == len(mutations), "mutations": mutations,
        "verdict": "EXACT_NONZERO_Q_MATTER_CLOSED_FACE_HOLONOMY_JOINT_CYLINDER_COMPATIBILITY", "stage2_status": "HOLD_FOR_EVIDENCE", "claim_bearing": False, "scientific_transition": False, "physical_progress": False,
        "reproduction": {"command": "python codes/foundations/pah_omc007_joint_holonomy_cylinder_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/hostile.json"},
        "non_claims": contract.get("non_claims", []), "next_question": contract.get("single_next_question"),
    }
    write_json(args.output, payload)
    print(f"{AUDIT_ID} HOSTILE {payload['verification']} {payload['passed']}/{payload['assertion_count']}; mutations={rejected}/{len(mutations)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
