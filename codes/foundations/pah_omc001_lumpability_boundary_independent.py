#!/usr/bin/env python3
"""Non-importing independent check of the PAH lumpability boundary.

The primary audit evaluates the squared-difference expression directly.  This
lane expands the same expression first and checks the fibre defect from the
linear term, so it does not reuse the primary implementation.
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
    "2026-09-02-r480-pah-lumpability-boundary/independent.json"
)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_rows(rows: list[dict[str, Any]]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def grid_value(epsilon: Fraction, cutoff: int, index: int) -> Fraction:
    return epsilon + Fraction(index, cutoff) * (1 - epsilon)


def expanded_fibre_defect(
    kappa: Fraction, step: Fraction, hidden_one: Fraction, hidden_two: Fraction
) -> Fraction:
    # Expand (s+delta-z)^2-(s-z)^2 before subtracting the two fibre values.
    # The coarse_s and delta^2 terms cancel, leaving kappa*delta*(z2-z1).
    return kappa * step * (hidden_two - hidden_one)


def run() -> dict[str, Any]:
    parent = digest_file(PARENT)
    contract = digest_file(CONTRACT)
    assert parent == (
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
    )
    assert contract == (
        "948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f"
    )

    rows: list[dict[str, Any]] = []
    epsilons = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    cutoffs = (4, 3, 2, 1)
    kappas = (Fraction(5, 2), Fraction(2), Fraction(1))
    for epsilon in epsilons:
        for cutoff in cutoffs:
            grid = [grid_value(epsilon, cutoff, j) for j in range(cutoff + 1)]
            for coarse_index in reversed(range(cutoff)):
                coarse = grid[coarse_index]
                step = grid[coarse_index + 1] - coarse
                for i, hidden_one in enumerate(grid):
                    for hidden_two in grid[i + 1 :]:
                        for kappa in kappas:
                            defect = expanded_fibre_defect(
                                kappa, step, hidden_one, hidden_two
                            )
                            rows.append(
                                {
                                    "epsilon": str(epsilon),
                                    "cutoff": cutoff,
                                    "coarse_index": coarse_index,
                                    "step": str(step),
                                    "hidden_one": str(hidden_one),
                                    "hidden_two": str(hidden_two),
                                    "kappa_s": str(kappa),
                                    "expanded_defect": str(defect),
                                    "nonzero": defect != 0,
                                }
                            )

    assert rows
    assert all(row["nonzero"] for row in rows)
    return {
        "schema": "tect/pah-omc-lumpability-boundary-independent/1.0",
        "audit_id": "PAH-OMC-LUMP-AUDIT-001",
        "exploration_id": "EXP-001362",
        "source_hashes": {"PAH-001": parent, "PAH-OMC-001": contract},
        "algorithm": "expanded linear fibre defect kappa_s*delta*(z_2-z_1)",
        "assertions": {
            "cases": len(rows),
            "nonzero_defects": sum(row["nonzero"] for row in rows),
            "all_pass": True,
            "rows_digest": digest_rows(rows),
        },
        "verdict": "ROUTE_LOCAL_STRONG_LUMPABILITY_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "boundary": "Only the named forgetful pullback is rejected; no global refinement no-go is claimed.",
        "non_claims": [
            "No PAH-001 bytes, functional, dynamics, weights, or morphism are changed.",
            "No block map, conditional kernel, approximate defect, or successor functional is selected.",
            "No physical Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE claim follows.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    value = run()
    write_json(args.output, value)
    print(
        "PAH-OMC-LUMP-AUDIT-001 INDEPENDENT PASS "
        f"{value['assertions']['cases']}/{value['assertions']['cases']} cases; "
        f"digest={value['assertions']['rows_digest']}"
    )


if __name__ == "__main__":
    main()
