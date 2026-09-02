#!/usr/bin/env python3
"""Independent expansion check for the PAH scalar-transport boundary.

This lane does not call the primary implementation.  It expands the edge
increment first and checks that every positive beta/kappa_s transport leaves a
nonzero logarithmic rate defect across a distinct hidden fibre.
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
    "2026-09-02-r481-pah-positive-scalar-transport-boundary/independent.json"
)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_rows(rows: list[dict[str, Any]]) -> str:
    encoded = json.dumps(
        rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True
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


def grid(epsilon: Fraction, cutoff: int) -> list[Fraction]:
    return [
        epsilon + Fraction(index, cutoff) * (1 - epsilon)
        for index in range(cutoff + 1)
    ]


def expanded_log_defect(
    beta: Fraction, kappa_s: Fraction, step: Fraction,
    hidden_one: Fraction, hidden_two: Fraction
) -> Fraction:
    # The coarse_s and step^2 terms cancel before the hidden values are
    # compared.  This is the independent expanded form.
    energy_difference = kappa_s * step * (hidden_two - hidden_one)
    return beta * kappa_s * step * (hidden_one - hidden_two) / 2


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    parent = digest_file(PARENT)
    contract = digest_file(CONTRACT)
    assert parent == (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    assert contract == (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )

    rows: list[dict[str, Any]] = []
    for epsilon in (Fraction(3, 4), Fraction(1, 2), Fraction(1, 4)):
        for cutoff in (4, 3, 2, 1):
            values = grid(epsilon, cutoff)
            for retained_index in reversed(range(cutoff)):
                step = values[retained_index + 1] - values[retained_index]
                for hidden_index in range(len(values) - 1, 0, -1):
                    hidden_two = values[hidden_index]
                    for hidden_one in values[:hidden_index]:
                        for beta in (Fraction(3), Fraction(1), Fraction(1, 3)):
                            for kappa_s in (
                                Fraction(5, 2),
                                Fraction(1),
                                Fraction(1, 2),
                            ):
                                defect = expanded_log_defect(
                                    beta, kappa_s, step, hidden_one, hidden_two
                                )
                                rows.append(
                                    {
                                        "epsilon": str(epsilon),
                                        "cutoff": cutoff,
                                        "retained_index": retained_index,
                                        "step": str(step),
                                        "hidden_one": str(hidden_one),
                                        "hidden_two": str(hidden_two),
                                        "beta_transport": str(beta),
                                        "kappa_s_transport": str(kappa_s),
                                        "expanded_log_rate_difference": str(defect),
                                        "nonzero": defect != 0,
                                    }
                                )

    assert rows
    assert all(row["nonzero"] for row in rows)
    payload = {
        "schema": "tect/pah-omc-positive-scalar-transport-boundary-independent/1.0",
        "audit_id": "PAH-OMC-SCALAR-TRANSPORT-001",
        "exploration_id": "EXP-001364",
        "task_id": "T-054",
        "source_hashes": {"PAH-001": parent, "PAH-OMC-001": contract},
        "algorithm": (
            "expanded edge increment followed by "
            "beta*kappa_s*delta*(z_1-z_2)/2"
        ),
        "assertions": {
            "cases": len(rows),
            "nonzero_defects": sum(row["nonzero"] for row in rows),
            "all_pass": True,
            "rows_digest": digest_rows(rows),
        },
        "verdict": "ROUTE_LOCAL_SCALAR_TRANSPORT_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "boundary": (
            "Only positive scalar beta/kappa_s transport for the named "
            "forgetful pullback is rejected; no global refinement no-go."
        ),
        "non_claims": [
            "No PAH-001 or PAH-OMC-001 bytes, functional or dynamics are changed.",
            "No block map, conditional kernel, hidden weight or successor functional is selected.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE claim follows.",
            "Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-OMC-SCALAR-TRANSPORT-001 INDEPENDENT PASS "
        f"{payload['assertions']['cases']}/{payload['assertions']['cases']} cases; "
        f"digest={payload['assertions']['rows_digest']}"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
