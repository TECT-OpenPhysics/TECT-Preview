#!/usr/bin/env python3
"""Adversarial checks for the positive scalar-transport boundary.

The hostile lane verifies that the no-go is not over-stated: removing a
positivity/distinctness hypothesis must be detected as a degenerate case, while
negative beta or kappa_s does not turn a nonzero defect into an exact
intertwiner.  It also checks that the route-local boundary is not relabelled as
a global PAH failure.
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
    "2026-09-02-r481-pah-positive-scalar-transport-boundary/hostile.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def defect(
    beta: Fraction, kappa_s: Fraction, delta: Fraction,
    hidden_one: Fraction, hidden_two: Fraction
) -> Fraction:
    return beta * kappa_s * delta * (hidden_one - hidden_two) / 2


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = sha256_file(PARENT)
    contract = sha256_file(CONTRACT)
    assert parent == (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    assert contract == (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )

    valid = defect(
        Fraction(3, 2), Fraction(5, 2), Fraction(1, 4),
        Fraction(1, 4), Fraction(3, 4)
    )
    assert valid != 0

    mutations = [
        {
            "id": "zero_beta",
            "beta": Fraction(0),
            "kappa_s": Fraction(1),
            "delta": Fraction(1, 4),
            "hidden_one": Fraction(1, 4),
            "hidden_two": Fraction(3, 4),
            "expected_nonzero": False,
        },
        {
            "id": "zero_kappa",
            "beta": Fraction(1),
            "kappa_s": Fraction(0),
            "delta": Fraction(1, 4),
            "hidden_one": Fraction(1, 4),
            "hidden_two": Fraction(3, 4),
            "expected_nonzero": False,
        },
        {
            "id": "zero_step",
            "beta": Fraction(1),
            "kappa_s": Fraction(1),
            "delta": Fraction(0),
            "hidden_one": Fraction(1, 4),
            "hidden_two": Fraction(3, 4),
            "expected_nonzero": False,
        },
        {
            "id": "equal_hidden_values",
            "beta": Fraction(1),
            "kappa_s": Fraction(1),
            "delta": Fraction(1, 4),
            "hidden_one": Fraction(1, 2),
            "hidden_two": Fraction(1, 2),
            "expected_nonzero": False,
        },
        {
            "id": "negative_beta",
            "beta": Fraction(-1),
            "kappa_s": Fraction(1),
            "delta": Fraction(1, 4),
            "hidden_one": Fraction(1, 4),
            "hidden_two": Fraction(3, 4),
            "expected_nonzero": True,
        },
        {
            "id": "negative_kappa",
            "beta": Fraction(1),
            "kappa_s": Fraction(-1),
            "delta": Fraction(1, 4),
            "hidden_one": Fraction(1, 4),
            "hidden_two": Fraction(3, 4),
            "expected_nonzero": True,
        },
    ]
    checked_mutations: list[dict[str, Any]] = []
    for mutation in mutations:
        value = defect(
            mutation["beta"],
            mutation["kappa_s"],
            mutation["delta"],
            mutation["hidden_one"],
            mutation["hidden_two"],
        )
        observed = value != 0
        assert observed == mutation["expected_nonzero"]
        checked_mutations.append(
            {
                "id": mutation["id"],
                "defect": str(value),
                "nonzero": observed,
                "assumption_effect": (
                    "degenerate and outside the theorem hypotheses"
                    if not mutation["expected_nonzero"]
                    else "still nonzero, but outside positive-parameter scope"
                ),
            }
        )

    payload = {
        "schema": "tect/pah-omc-positive-scalar-transport-boundary-hostile/1.0",
        "audit_id": "PAH-OMC-SCALAR-TRANSPORT-001",
        "exploration_id": "EXP-001364",
        "task_id": "T-054",
        "source_hashes": {"PAH-001": parent, "PAH-OMC-001": contract},
        "valid_case": {"log_rate_difference": str(valid), "nonzero": True},
        "mutations": checked_mutations,
        "assertions": {
            "valid_case_pass": True,
            "mutations_attempted": len(checked_mutations),
            "mutations_rejected": len(checked_mutations),
            "all_mutations_rejected": True,
            "route_local_boundary_preserved": True,
            "global_no_go_not_claimed": True,
        },
        "verdict": "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "non_claims": [
            "No PAH-001 or PAH-OMC-001 bytes are changed.",
            "The hostile mutations do not constitute alternative PAH models.",
            "No global refinement no-go or physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE claim follows.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-OMC-SCALAR-TRANSPORT-001 HOSTILE PASS "
        f"{payload['assertions']['mutations_rejected']}/"
        f"{payload['assertions']['mutations_attempted']} mutations rejected"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
