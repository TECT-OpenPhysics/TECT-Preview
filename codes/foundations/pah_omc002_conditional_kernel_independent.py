#!/usr/bin/env python3
"""Non-importing independent audit of the PAH-OMC-002 Gibbs-kernel witness.

This lane derives the witness by polynomial expansion of the two aperture
edges instead of enumerating the primary implementation's transition code.
It is intentionally independent of ``pah_omc002_conditional_kernel.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-conditional-kernel/independent.json"
)


# Independent fixture inputs.  They are explicit test inputs; all increments
# below are derived from the unchanged PAH aperture terms.
EPS = Fraction(1, 2)
LAMBDA_S = Fraction(1)
KAPPA_S = Fraction(1)
BETA = Fraction(1)
K = 2
M_S = 1


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def aperture(j: int) -> Fraction:
    return EPS + Fraction(j) * (1 - EPS) / M_S


def vertex_term(j: int) -> Fraction:
    return LAMBDA_S * (aperture(j) - 1) ** 2 / 2


def edge_term(j_left: int, j_right: int) -> Fraction:
    return KAPPA_S * (aperture(j_left) - aperture(j_right)) ** 2 / 2


def coarse_energy(jv: int, jw: int) -> Fraction:
    return vertex_term(jv) + vertex_term(jw) + edge_term(jv, jw)


def fine_energy(jv: int, jz: int, jw: int) -> Fraction:
    return coarse_energy(jv, jw) + vertex_term(jz) + edge_term(jv, jz)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    contract = load(CONTRACT)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-002": digest(CONTRACT),
        "PAH-OMC-002-MANIFEST": digest(MANIFEST),
    }
    expected = {
        "PAH-001": manifest["parent"]["sha256"],
        "PAH-OMC-001": manifest["finite_completion"]["sha256"],
        "PAH-OMC-002": manifest["contract"]["sha256"],
        "PAH-OMC-002-MANIFEST": source_hashes["PAH-OMC-002-MANIFEST"],
    }
    check("source-hashes", source_hashes == expected, source_hashes)
    check("contract-status", contract["status"]["contract"] == "CANDIDATE_NOT_ADMITTED")
    check("projected-target-pending", contract["status"]["conditional_projected_intertwining"] == "PENDING_EXACT_AUDIT")
    check("parent-functional-preserved", all(contract["preservation_firewall"][key] is True for key in ("functional_unchanged", "move_families_unchanged", "mobility_exponent_nu_unchanged", "no_new_hamiltonian_or_counterterm")))
    check("fixed-q-fixture", K == 2 and M_S == 1)
    check("aperture-grid", aperture(0) == Fraction(1, 2) and aperture(1) == Fraction(1))

    # Expand the exact PAH aperture polynomial independently of the primary
    # state enumerator.  The witness coarse state is (j_v,j_w)=(0,0).
    coarse_before = coarse_energy(0, 0)
    coarse_after = coarse_energy(1, 0)
    check("coarse-energy-before", coarse_before == Fraction(1, 4), str(coarse_before))
    check("coarse-energy-after", coarse_after == Fraction(1, 4), str(coarse_after))
    check("coarse-increment", coarse_after - coarse_before == 0, str(coarse_after - coarse_before))

    hidden_before = {jz: vertex_term(jz) + edge_term(0, jz) for jz in (0, 1)}
    hidden_after = {jz: vertex_term(jz) + edge_term(1, jz) for jz in (0, 1)}
    delta = {jz: hidden_after[jz] - hidden_before[jz] for jz in (0, 1)}
    check("hidden-before-equal", hidden_before == {0: Fraction(1, 8), 1: Fraction(1, 8)}, {str(k): str(v) for k, v in hidden_before.items()})
    check("hidden-after-values", hidden_after == {0: Fraction(1, 4), 1: Fraction(0)}, {str(k): str(v) for k, v in hidden_after.items()})
    check("hidden-increment-values", delta == {0: Fraction(1, 8), 1: Fraction(-1, 8)}, {str(k): str(v) for k, v in delta.items()})
    check("hidden-increment-difference", delta[0] - delta[1] == Fraction(1, 4), str(delta[0] - delta[1]))

    # The omitted phase n_z and fine link u_d each have K labels and carry no
    # energy in this Q=0/no-plaquette fixture, giving K^2 equal-weight copies
    # for each hidden aperture value.
    copies_per_hidden = K * K
    fibre_size = 2 * copies_per_hidden
    check("fibre-degeneracy", copies_per_hidden == 4 and fibre_size == 8, [copies_per_hidden, fibre_size])
    check("conditional-hidden-probability", Fraction(copies_per_hidden, fibre_size) == Fraction(1, 2))

    # Rate ratio: the retained aperture mobility is common.  With the exact
    # PAH midpoint rate, the conditional expectation multiplies the coarse
    # rate by the stated exponential average.
    ratio = (math.exp(-1 / 16) + math.exp(1 / 16)) / 2
    defect = math.sqrt(0.5) * (ratio - 1)
    check("mobility-square", aperture(0) * aperture(1) == Fraction(1, 2), str(aperture(0) * aperture(1)))
    check("conditional-rate-ratio-not-one", ratio > 1, ratio)
    check("positive-defect-interval", 0.00138 < defect < 0.00139, defect)
    check("strong-and-projected-separated", "strong_mainline" in contract["compatibility_targets"] and "conditional_projected" in contract["compatibility_targets"])
    check("no-limit-in-fixture", "uniform_target" in contract["compatibility_targets"] and contract["status"]["uniform_limit"] == "NOT_ADMITTED")

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/pah-omc002-conditional-kernel-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-COND-GIBBS-BLOCK-001",
        "exploration_id": "EXP-001367",
        "result_id": "R-480",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": source_hashes,
        "derivation": {
            "coarse_state": {"j_v": 0, "j_w": 0, "n_v": 0, "n_w": 0, "u_e": 0},
            "coarse_delta_F": str(coarse_after - coarse_before),
            "hidden_delta_F": {str(key): str(value) for key, value in delta.items()},
            "conditional_factor_exact": "(exp(-1/16)+exp(1/16))/2 > 1",
            "normalized_defect_exact": "(exp(-1/16)+exp(1/16))/2 - 1 > 0",
            "numeric_defect_observed": defect,
        },
        "verdict": "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "non_claims": [
            "The computation is only a finite route-local defect for the PAH-OMC-002 conditional diagnostic.",
            "It is not a no-go theorem for PAH-001 or for all successor block kernels.",
            "No uniform limit, continuum, physical Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
            "No Q3LOCK result is imported; Markov time remains external stochastic time.",
        ],
        "next_question": "Can a separately owner-authorized block kernel satisfy the projected identity without altering PAH-001 and without substituting it for strong intertwining?",
    }
    atomic_json(output, payload)
    print(
        "PAH-COND-GIBBS-BLOCK-001 INDEPENDENT "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"verdict={payload['verdict']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
