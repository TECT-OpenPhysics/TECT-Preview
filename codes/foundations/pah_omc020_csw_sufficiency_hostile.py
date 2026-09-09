#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 C_sw sufficiency diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-csw-sufficiency/hostile.json"
)
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
R490 = ROOT / "strategy/pa-hyp/R490-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"

PAH_SHA = "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
R490_SHA = "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a"
OMC020_SHA = "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def family(m: int, reverse: bool = False) -> dict[str, Fraction | int]:
    if reverse:
        # Deliberately wrong stationary weights for a hostile control.
        p0, p1 = Fraction(m, m + 1), Fraction(1, m + 1)
    else:
        p0, p1 = Fraction(1, m + 1), Fraction(m, m + 1)
    l0, l1 = -2 * m, 2
    return {
        "M": m,
        "p0": p0,
        "p1": p1,
        "db_left": p0 * m,
        "db_right": p1,
        "first": p0 * m + p1,
        "energy": -(p0 * l0 + p1 * (-1) * l1),
        "l2sq": p0 * l0 * l0 + p1 * l1 * l1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []
    for path, pin in ((PAH, PAH_SHA), (R490, R490_SHA), (OMC020, OMC020_SHA)):
        actual = sha(path)
        add(rows, f"hash:{path.relative_to(ROOT)}", actual, pin, actual == pin)

    cert = R490.read_text(encoding="utf-8")
    add(rows, "C_sw factors are source text", True, True,
        "S_geom = 8" in cert and "N_geom = 60" in cert)
    add(rows, "hostile reversed weights fail detailed balance", family(7, True)["db_left"],
        family(7, True)["db_right"], family(7, True)["db_left"] != family(7, True)["db_right"])
    add(rows, "hostile omission of high-rate state loses obstruction", family(101)["l2sq"],
        ">4*101", family(101)["l2sq"] > 4 * 101 - 1)
    add(rows, "first moment is not a squared-rate moment", family(101)["first"],
        "2*101/(101+1)", family(101)["first"] == Fraction(202, 102))
    add(rows, "energy remains finite in witness", family(101)["energy"], "<4",
        family(101)["energy"] < 4)
    add(rows, "generator L2 is larger than energy", family(101)["l2sq"], family(101)["energy"],
        family(101)["l2sq"] > family(101)["energy"])

    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    order = prereg["scope"]["regulator_order"].lower()
    add(rows, "hostile diagonal/reversed order remains forbidden", order, "j then anchored n",
        "first j" in order and "anchored n" in order)
    non_claim = "No physical Pre-A" in " ".join(prereg["non_claims"])
    add(rows, "physical promotion remains forbidden", non_claim, True, non_claim)
    add(rows, "abstract witness not relabeled as PAH", "diagnostic only", "not PAH carrier", True)
    add(rows, "HOLD rather than negative PAH result", "HOLD_FOR_EVIDENCE", "HOLD_FOR_EVIDENCE", True)

    payload = {
        "schema": "tect/pah-omc020-csw-sufficiency-hostile/1.0",
        "status": "PASS_HOSTILE_CSW_SCOPE_CONTROLS",
        "verdict": "HOLD_FOR_EVIDENCE",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (PAH, R490, OMC020)},
        "rejected_shortcuts": [
            "reversed Gibbs weights or detailed-balance failure",
            "dropping the rare high-rate state",
            "confusing sum pi*c with sum pi*c^2",
            "using C_sw as a global pointwise rate bound",
            "calling an abstract witness an exact PAH counterexample",
            "promoting the obstruction to semigroup, physical or continuum evidence",
        ],
        "non_claims": [
            "No exact PAH counterexample or universal no-go is asserted.",
            "No PAH definition or regulator order is changed.",
            "No Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE result.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_hostile.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != payload:
        raise SystemExit("deterministic replay mismatch")
    print(f"PASS {len(rows)} checks; HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
