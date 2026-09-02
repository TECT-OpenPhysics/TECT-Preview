#!/usr/bin/env python3
"""Exact strong-lumpability boundary check for the named PAH free-vertex route.

This is a route-local diagnostic for PAH-OMC-001's already specified
forgetful coarse map.  It does not add a Hamiltonian, a counterterm, a
coarse kernel, or a refinement rule.  For an aperture move at the retained
vertex, strong lumpability requires the total rate into the target coarse
fibre to be constant over every hidden fine fibre.  The unchanged positive
edge-stiffness term makes that requirement fail whenever the hidden aperture
values differ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r480-pah-lumpability-boundary/lumpability.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


def aperture(epsilon: Fraction, m_s: int, j: int) -> Fraction:
    return epsilon + Fraction(j) * (1 - epsilon) / m_s


def edge_increment(
    kappa_s: Fraction, coarse_s: Fraction, hidden_s: Fraction, step: Fraction
) -> Fraction:
    """Increment of the added edge's unchanged aperture energy."""

    return kappa_s * (
        (coarse_s + step - hidden_s) ** 2 - (coarse_s - hidden_s) ** 2
    ) / 2


def build_cases() -> list[dict[str, Any]]:
    # These are finite test inputs, not derived model constants.  Every case
    # uses two distinct values in the declared aperture grid and an interior
    # coarse aperture step so the move is admissible in both states.
    epsilons = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    cutoffs = (1, 2, 3, 4)
    kappas = (Fraction(1), Fraction(2), Fraction(5, 2))
    cases: list[dict[str, Any]] = []
    for epsilon in epsilons:
        for m_s in cutoffs:
            for coarse_j in range(m_s):
                coarse_s = aperture(epsilon, m_s, coarse_j)
                step = aperture(epsilon, m_s, coarse_j + 1) - coarse_s
                grid = [aperture(epsilon, m_s, j) for j in range(m_s + 1)]
                for z_index in range(len(grid)):
                    for z_other_index in range(z_index + 1, len(grid)):
                        z_one = grid[z_index]
                        z_two = grid[z_other_index]
                        for kappa_s in kappas:
                            difference = edge_increment(
                                kappa_s, coarse_s, z_one, step
                            ) - edge_increment(
                                kappa_s, coarse_s, z_two, step
                            )
                            factorized = -kappa_s * step * (z_one - z_two)
                            # The aperture mobility is hidden-state independent
                            # for this retained-vertex move, so log-rate
                            # differences are -beta/2 times this energy defect.
                            beta = Fraction(2)
                            log_rate_difference = -beta * difference / 2
                            cases.append(
                                {
                                    "epsilon": str(epsilon),
                                    "M_s": m_s,
                                    "coarse_j": coarse_j,
                                    "coarse_s": str(coarse_s),
                                    "step": str(step),
                                    "z_one": str(z_one),
                                    "z_two": str(z_two),
                                    "kappa_s": str(kappa_s),
                                    "edge_increment_difference": str(difference),
                                    "factorized_difference": str(factorized),
                                    "log_rate_difference_beta_2": str(
                                        log_rate_difference
                                    ),
                                    "nonzero": difference != 0,
                                }
                            )
    return cases


def run() -> dict[str, Any]:
    parent_sha = sha256_file(PARENT)
    contract_sha = sha256_file(CONTRACT)
    expected_parent = (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    expected_contract = (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )
    assert parent_sha == expected_parent
    assert contract_sha == expected_contract

    cases = build_cases()
    assert cases
    for case in cases:
        assert case["edge_increment_difference"] == case["factorized_difference"]
        assert case["nonzero"]
        assert case["log_rate_difference_beta_2"] != "0"

    case_digest = canonical_hash(cases)
    return {
        "schema": "tect/pah-omc-lumpability-boundary/1.0",
        "audit_id": "PAH-OMC-LUMP-AUDIT-001",
        "result_id": None,
        "exploration_id": "EXP-001362",
        "source_authorities": [
            {
                "source_id": "PAH-001",
                "path": "strategy/pa-hyp/PAH-001-v1.json",
                "sha256": parent_sha,
                "role": "immutable parent microscopic candidate",
            },
            {
                "source_id": "PAH-OMC-001",
                "path": "strategy/pa-hyp/PAH-OMC-001-v1.json",
                "sha256": contract_sha,
                "role": "separately versioned finite owner completion",
            },
        ],
        "question": (
            "Does the already named PAH-FREE-VERTEX-RESTRICTION route satisfy "
            "the strong-lumpability necessary condition for exact generator "
            "intertwining under the unchanged PAH functional?"
        ),
        "scope": {
            "coarse_map": "forget the freely varying adjacent fine vertex z",
            "observable_embedding": "iota_p f = f composed with p",
            "tested_move": "one admissible aperture step at the retained vertex",
            "hidden_fibre": "two distinct fine aperture values z_1 and z_2",
            "functional_part": "positive unchanged edge term kappa_s*(s_v-s_z)^2/2",
            "time": "external stochastic Markov time only",
            "limits": "none",
        },
        "assumptions": [
            "0 < epsilon < 1 and M_s is a positive finite cutoff",
            "the retained aperture move has a positive grid step",
            "kappa_s > 0 and beta = 2 in the finite test inputs",
            "the two hidden aperture values are distinct and lie in one coarse fibre",
            "no hidden-state-dependent counterterm, weight, rate rescaling or frozen field is inserted",
            "other fine moves do not change the retained coarse aperture destination fibre",
        ],
        "derivation": {
            "edge_increment": "kappa_s*((s+delta-z)^2-(s-z)^2)/2",
            "fibre_difference": "-kappa_s*delta*(z_1-z_2)",
            "strong_lumpability_requirement": (
                "the total fine rate from any two states in one coarse fibre "
                "to a fixed target coarse fibre must agree"
            ),
            "rate_test": (
                "aperture mobility is the same at z_1,z_2, while the log-rate "
                "difference is -beta/2 times the nonzero energy difference"
            ),
        },
        "assertions": {
            "cases": len(cases),
            "factorization_pass": len(cases),
            "nonzero_defects": len(cases),
            "all_pass": True,
            "case_digest": case_digest,
        },
        "verdict": "ROUTE_LOCAL_STRONG_LUMPABILITY_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "boundary": (
            "This rejects only the named forgetful pullback route. It is not a "
            "no-go for an owner-selected block map, conditional-expectation "
            "kernel, transported cell weights, approximate defect theorem, or "
            "a separately versioned successor functional."
        ),
        "non_claims": [
            "No change to PAH-001 or PAH-OMC-001 is made.",
            "No nontrivial refinement or uniform limit is admitted.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE conclusion follows.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run()
    atomic_json(args.output, result)
    print(
        "PAH-OMC-LUMP-AUDIT-001 PASS "
        f"{result['assertions']['cases']}/{result['assertions']['cases']} "
        f"cases; verdict={result['verdict']}; digest={result['assertions']['case_digest']}"
    )


if __name__ == "__main__":
    main()
