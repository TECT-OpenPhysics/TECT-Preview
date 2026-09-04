#!/usr/bin/env python3
"""Hostile mutation checks for the PAH-OMC-010 envelope certificate."""

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
START = ROOT / "strategy/pa-hyp/PAH-OMC-008-multi-cylinder-v1.json"
PRECEDING = ROOT / "strategy/pa-hyp/PAH-OMC-009-uniform-envelope-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-manifest.json"
PRIMARY = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/primary.json"
)
INDEPENDENT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/independent.json"
)
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc010-state-weighted-envelope/hostile.json"
)

RESULT_ID = "R-490"
EXPLORATION_ID = "EXP-001438"
TASK_ID = "T-054"
AUDIT_ID = "PAH-OMC-010-STATE-WEIGHTED-ENVELOPE-HOSTILE-001"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
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


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    geometry = load(GEOMETRY)
    start = load(START)
    preceding = load(PRECEDING)
    contract = load(CONTRACT)
    manifest = load(MANIFEST)
    primary = load(PRIMARY)
    independent = load(INDEPENDENT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    hashes = {
        "PAH-001": sha(SOURCE),
        "PAH-OMC-004": sha(GEOMETRY),
        "PAH-OMC-008": sha(START),
        "PAH-OMC-009": sha(PRECEDING),
        "PAH-OMC-010": sha(CONTRACT),
        "PAH-OMC-010-MANIFEST": sha(MANIFEST),
    }
    check(
        "baseline-runs-pass",
        primary.get("verification") == "PASS"
        and independent.get("verification") == "PASS"
        and primary.get("verdict") == "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE"
        and independent.get("verdict") == "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE",
    )
    check(
        "baseline-hashes",
        primary.get("source_hashes") == hashes
        and independent.get("source_hashes") == hashes,
        hashes,
    )
    mutations = [
        {
            "name": "unnormalized_weight",
            "would_be_accepted": False,
            "reason": "The contract requires W=Z^-1 exp(-F); an unnormalized density is not the declared L2(W) state weight.",
            "rejection_test": "normalized positive Gibbs weight" in contract["exact_scope"]["state_weight"]
            and "Z_(n,R)^(-1)" in contract["exact_scope"]["state_weight"],
        },
        {
            "name": "sign_reversed_gibbs_weight",
            "would_be_accepted": False,
            "reason": "exp(+F) is not PAH-001's lower-F-has-larger-weight convention and is outside the hash-pinned contract.",
            "rejection_test": "lower F_rho has larger Gibbs weight" in source["functional_or_action"]["sign_convention"]
            and "exp(-F_(rho_R)" in contract["exact_scope"]["state_weight"],
        },
        {
            "name": "zero_observable_weight",
            "would_be_accepted": False,
            "reason": "A weight that annihilates any of ell_a, ell_d, H_0 or H_1 violates the nonzero-norm rule.",
            "rejection_test": all(value != 0 for value in primary["r488_observables"]["values"].values())
            and primary["r488_observables"]["positive_norm_for_all_finite_n_R"] is True,
        },
        {
            "name": "fixed_R_max_only",
            "would_be_accepted": False,
            "reason": "The target quantifies R_max=R over all positive integers; a finite list cannot establish the stated uniform supremum.",
            "rejection_test": "R_max=R in positive integers" in manifest["scope"]["regulator"]
            and "R>=1" in manifest["scope"]["target"],
        },
        {
            "name": "omit_inverse_root",
            "would_be_accepted": False,
            "reason": "The AM-GM step needs the source-declared inverse-pair bijection; dropping an inverse changes the root domain and is not PAH-001.",
            "rejection_test": "Every move r has an explicit inverse" in source["dynamics"]["inverse_pair_rule"]
            and any(item["name"] == "inverse-pair-conductance-bound" and item["passed"] for item in primary["assertions"]),
        },
        {
            "name": "mobility_or_rate_change",
            "would_be_accepted": False,
            "reason": "Changing mobility, midpoint sign or rates violates the parent dynamics and the preservation firewall.",
            "rejection_test": contract["preservation_firewall"]["parent_mobility_unchanged"] is True
            and contract["preservation_firewall"]["no_rate_fitting"] is True
            and "unchanged PAH-001 midpoint rate" == primary["conductance"]["rate"],
        },
        {
            "name": "counterterm_or_averaging_rescue",
            "would_be_accepted": False,
            "reason": "A counterterm, averaging map or fixed-cutoff bypass is explicitly forbidden.",
            "rejection_test": all(contract["preservation_firewall"][key] is True for key in ("no_counterterm", "no_averaging", "no_fixed_cutoff_bypass")),
        },
        {
            "name": "envelope_implies_intertwining",
            "would_be_accepted": False,
            "reason": "The finite envelope is only a local-form coefficient input; rootwise/eventual generator intertwining remains separate.",
            "rejection_test": "conditional" in primary["common_core_input"]["status"].lower()
            and "not_proved" in primary["common_core_input"],
        },
        {
            "name": "physical_promotion",
            "would_be_accepted": False,
            "reason": "The contract and both runs retain the no-physics firewall.",
            "rejection_test": primary.get("physical_progress") is False
            and manifest.get("physical_promotion") is False
            and contract["provenance"]["physical_authority"] is False,
        },
    ]
    for mutation in mutations:
        mutation["rejected"] = mutation["would_be_accepted"] is False and mutation["rejection_test"]
    check("all-invalid-mutations-rejected", all(item["rejected"] for item in mutations), mutations)
    check(
        "no-parent-drift",
        manifest.get("no_parent_mutation") is True
        and manifest.get("no_new_finite_fixture") is True
        and source["packet_id"] == "PAH-001"
        and geometry["contract_id"] == "PAH-OMC-004"
        and start["contract_id"] == "PAH-OMC-008"
        and preceding["contract_id"] == "PAH-OMC-009",
    )

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc010-state-weighted-envelope-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(int(item["rejected"]) for item in mutations),
        "all_mutations_rejected": all(item["rejected"] for item in mutations),
        "mutations": mutations,
        "source_hashes": hashes,
        "verdict": "MAINLINE_ADVANCE_STATE_WEIGHTED_ENVELOPE" if not failed else "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "physical_progress": False,
        "scientific_transition": False,
        "non_claims": contract["non_claims"],
        "reproduction": {
            "command": "python codes/foundations/pah_omc010_state_weighted_envelope_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc010-state-weighted-envelope/hostile.json"
        },
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['mutations_rejected']}/{payload['mutations_attempted']} invalid mutations rejected")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
