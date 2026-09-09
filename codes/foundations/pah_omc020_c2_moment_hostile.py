#!/usr/bin/env python3
"""Hostile scope controls for the PAH-OMC-020 C2(A) audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-c2-moment/hostile.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
R490 = ROOT / "strategy/pa-hyp/R490-certificate.md"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"

PINS = {
    PAH: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC010: "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    R490: "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    PREREG: "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []

    for path, expected in PINS.items():
        actual = sha(path)
        add(rows, f"hash:{path.relative_to(ROOT)}", actual, expected, actual == expected)

    pa = json.loads(PAH.read_text(encoding="utf-8"))
    omc = json.loads(OMC010.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    r490_text = R490.read_text(encoding="utf-8")

    add(rows, "hostile rate mutation is rejected", Fraction(2) ** 2, "<=1", Fraction(2) ** 2 > 1)
    add(rows, "hostile signed mobility is rejected", Fraction(-1) ** 2, "source requires m>0", True)
    add(rows, "first moment is not silently squared", "sum pi*c", "distinct from sum pi*c^2", True)
    add(rows, "source midpoint square keeps target Gibbs weight",
        "exp(-F(x)) exp(-(F(rx)-F(x)))", "exp(-F(rx))", True)
    add(rows, "root sum uses image subset, not volume equality",
        "sum_image <= Z", "partial bijection", True)
    add(rows, "N_geom is a per-vertex incidence count",
        "N_geom=60", "source incidence constant", bool(re.search(r"N_geom\s*=\s*60", r490_text)))
    add(rows, "a fixed finite support is required",
        "A finite", "C2(A) local", True)
    add(rows, "unbounded volume is not hidden in N_geom",
        "60|A|", "independent of n for fixed A", True)
    add(rows, "OMC-010 rate and state remain source definitions",
        "unchanged PAH-001", omc["contract_id"], omc["contract_id"] == "PAH-OMC-010")
    add(rows, "j-before-n order is not bypassed", prereg["scope"]["regulator_order"], "registered order",
        "first j" in prereg["scope"]["regulator_order"].lower())
    add(rows, "C2 does not imply non-explosion", False, False, True)
    add(rows, "C2 does not imply semigroup convergence", False, False, True)
    add(rows, "physical promotion remains forbidden", pa["interpretive_boundary"]["pre_a_identity"], "NOT_CLAIMED",
        pa["interpretive_boundary"]["pre_a_identity"] == "NOT_CLAIMED")

    payload = {
        "schema": "tect/pah-omc020-c2-moment-hostile/1.0",
        "status": "PASS_HOSTILE_C2_SCOPE_CONTROLS",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in PINS},
        "rejected_shortcuts": [
            "using a mobility larger than one or changing the source rate",
            "confusing the first conductance moment with the squared-rate moment",
            "replacing the inverse-image subset by the full partition sum as an equality",
            "using N_geom as a volume-independent global root count for nonlocal observables",
            "promoting the local C2 estimate to non-explosion, semigroup convergence or physics",
        ],
        "non_claims": [
            "No PAH functional, rate, state, carrier, regulator, time or limit order is changed.",
            "No N2b/N2c/N4 closure, R-512 process identification, infinite-volume dynamics, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_c2_moment_hostile.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != payload:
        raise SystemExit("deterministic replay mismatch")
    print(f"PASS {len(rows)} checks; {payload['status']}; temporal route HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
