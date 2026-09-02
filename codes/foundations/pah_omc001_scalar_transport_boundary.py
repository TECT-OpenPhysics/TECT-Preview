#!/usr/bin/env python3
"""Check the positive scalar-transport boundary for the PAH free-vertex route.

The named free-vertex pullback already fails strong lumpability because an
added positive aperture edge makes the retained-vertex energy increment depend
on the hidden aperture.  This audit asks whether changing only the transported
positive beta and kappa_s scalars can remove that fibre dependence.  It uses
the unchanged PAH-001 edge term and introduces no new map, weight, carrier or
functional.
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
    "2026-09-02-r481-pah-positive-scalar-transport-boundary/primary.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def aperture(epsilon: Fraction, cutoff: int, index: int) -> Fraction:
    return epsilon + Fraction(index) * (1 - epsilon) / cutoff


def edge_increment(
    kappa_s: Fraction, retained: Fraction, hidden: Fraction, step: Fraction
) -> Fraction:
    return kappa_s * (
        (retained + step - hidden) ** 2 - (retained - hidden) ** 2
    ) / 2


def build_cases() -> list[dict[str, Any]]:
    epsilons = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    cutoffs = (1, 2, 3, 4)
    transported_betas = (Fraction(1, 3), Fraction(1), Fraction(3))
    transported_kappas = (Fraction(1, 2), Fraction(1), Fraction(5, 2))
    cases: list[dict[str, Any]] = []
    for epsilon in epsilons:
        for cutoff in cutoffs:
            grid = [aperture(epsilon, cutoff, index) for index in range(cutoff + 1)]
            for retained_index in range(cutoff):
                retained = grid[retained_index]
                step = grid[retained_index + 1] - retained
                for hidden_index, hidden_one in enumerate(grid):
                    for hidden_two in grid[hidden_index + 1 :]:
                        for beta in transported_betas:
                            for kappa_s in transported_kappas:
                                difference = edge_increment(
                                    kappa_s, retained, hidden_one, step
                                ) - edge_increment(
                                    kappa_s, retained, hidden_two, step
                                )
                                log_rate_difference = -beta * difference / 2
                                factorized = (
                                    beta
                                    * kappa_s
                                    * step
                                    * (hidden_one - hidden_two)
                                    / 2
                                )
                                cases.append(
                                    {
                                        "epsilon": str(epsilon),
                                        "cutoff": cutoff,
                                        "retained_index": retained_index,
                                        "step": str(step),
                                        "hidden_one": str(hidden_one),
                                        "hidden_two": str(hidden_two),
                                        "beta_transport": str(beta),
                                        "kappa_s_transport": str(kappa_s),
                                        "energy_difference": str(difference),
                                        "log_rate_difference": str(log_rate_difference),
                                        "factorized_log_rate_difference": str(factorized),
                                        "nonzero": log_rate_difference != 0,
                                    }
                                )
    return cases


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
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
        assert case["energy_difference"] != "0"
        assert (
            case["log_rate_difference"]
            == case["factorized_log_rate_difference"]
        )
        assert case["nonzero"]

    payload = {
        "schema": "tect/pah-omc-positive-scalar-transport-boundary/1.0",
        "audit_id": "PAH-OMC-SCALAR-TRANSPORT-001",
        "result_id": None,
        "exploration_id": "EXP-001364",
        "task_id": "T-054",
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
            }
        ],
        "question": (
            "Can any strictly positive scalar transport of beta and kappa_s "
            "repair exact strong lumpability for the named free-vertex "
            "forgetful pullback?"
        ),
        "scope": {
            "route": "PAH-FREE-VERTEX-RESTRICTION",
            "coarse_map": "forget the freely varying adjacent hidden vertex",
            "observable_embedding": "iota_p f = f composed with p",
            "functional_part": "unchanged positive edge term kappa_s*(s_v-s_z)^2/2",
            "transport": "fine beta>0 and fine kappa_s>0 are arbitrary positive scalars",
            "other_terms": "fibre-independent in the R-480 local test scope",
            "time": "external stochastic Markov time only",
            "limits": "none",
        },
        "derivation": {
            "energy_fibre_difference": (
                "DeltaF_1-DeltaF_2=-kappa_s*delta*(z_1-z_2)"
            ),
            "log_rate_difference": (
                "log(c_1)-log(c_2)=beta*kappa_s*delta*(z_1-z_2)/2"
            ),
            "criterion": (
                "exact pullback intertwining requires equal total rates into "
                "each target coarse fibre for every pair in one hidden fibre"
            ),
        },
        "test_oracle": {
            "epsilon_inputs": ["1/4", "1/2", "3/4"],
            "cutoff_inputs": [1, 2, 3, 4],
            "beta_transport_inputs": ["1/3", "1", "3"],
            "kappa_transport_inputs": ["1/2", "1", "5/2"],
            "all_inputs_positive": True,
        },
        "assertions": {
            "cases": len(cases),
            "factorization_pass": len(cases),
            "nonzero_defects": len(cases),
            "all_pass": True,
            "case_digest": canonical_hash(cases),
        },
        "verdict": "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "boundary": (
            "Positive scalar beta or kappa_s transport cannot repair this "
            "forgetful pullback. A block/conditional kernel, hidden-state "
            "weight, or separately versioned functional remains outside scope."
        ),
        "assumptions": [
            "0<epsilon<1, positive finite aperture step and distinct hidden values",
            "fine beta and fine kappa_s remain strictly positive",
            "the retained aperture mobility is hidden-state independent",
            "no hidden-state-dependent counterterm or weight cancels the edge defect",
        ],
        "non_claims": [
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "No global PAH no-go is claimed.",
            "No nontrivial refinement, uniform limit, continuum or observable law is admitted.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-OMC-SCALAR-TRANSPORT-001 PASS "
        f"{payload['assertions']['cases']}/{payload['assertions']['cases']} cases; "
        f"verdict={payload['verdict']}; "
        f"digest={payload['assertions']['case_digest']}"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
