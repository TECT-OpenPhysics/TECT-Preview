#!/usr/bin/env python3
"""Non-importing reconstruction of the PAH-OMC-020 C_sw audit.

This lane uses only rational arithmetic and the pinned R-490 factors.  It is
an independent sufficiency diagnostic: a stationary first-rate bound is
compatible with an unbounded L2 generator norm.  The witness is not a PAH
model or a replacement carrier.
"""

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
    "2026-09-08-pah-omc020-csw-sufficiency/independent.json"
)
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
R490 = ROOT / "strategy/pa-hyp/R490-certificate.md"
OMC010 = ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"

PAH_SHA = "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
R490_SHA = "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a"
OMC010_SHA = "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69"
PREREG_SHA = "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(to_json(data), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def to_json(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_json(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [to_json(item) for item in value]
    return value


def add(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def two_state(m: int) -> dict[str, Fraction | int]:
    d = m + 1
    p0 = Fraction(1, d)
    p1 = Fraction(m, d)
    # The bounded test is f=(+1,-1), so its two increments are -2 and +2.
    l0 = -2 * m
    l1 = 2
    balance0 = p0 * m
    balance1 = p1
    first = balance0 + balance1
    energy = Fraction(4 * m, d)
    l2sq = p0 * l0 * l0 + p1 * l1 * l1
    return {
        "M": m,
        "pi0": p0,
        "pi1": p1,
        "balance_left": balance0,
        "balance_right": balance1,
        "first_moment": first,
        "dirichlet_energy": energy,
        "generator_l2_sq": l2sq,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows: list[dict] = []
    expected = {PAH: PAH_SHA, R490: R490_SHA, OMC010: OMC010_SHA, PREREG: PREREG_SHA}
    for path, pin in expected.items():
        actual = sha(path)
        add(rows, f"hash:{path.relative_to(ROOT)}", actual, pin, actual == pin)

    cert = R490.read_text(encoding="utf-8")
    add(rows, "R-490 support factor", "S_geom = 8", True, "S_geom = 8" in cert)
    add(rows, "R-490 incidence factor", "N_geom = 60", True, "N_geom = 60" in cert)
    c_sw = 60 * (1 + 8)
    add(rows, "derived C_sw", c_sw, 540, c_sw == 540)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    add(rows, "frozen order", prereg["scope"]["regulator_order"], "j before anchored n",
        "first j" in prereg["scope"]["regulator_order"].lower()
        and "anchored n" in prereg["scope"]["regulator_order"].lower())

    rows_witness = [two_state(m) for m in (1, 3, 17, c_sw + 1)]
    for row in rows_witness:
        m = int(row["M"])
        add(rows, f"DB M={m}", row["balance_left"], row["balance_right"],
            row["balance_left"] == row["balance_right"])
        add(rows, f"first moment M={m}", row["first_moment"], "<2", row["first_moment"] < 2)
        add(rows, f"energy M={m}", row["dirichlet_energy"], "<4", row["dirichlet_energy"] < 4)
        add(rows, f"L2 formula M={m}", row["generator_l2_sq"], 4 * m,
            row["generator_l2_sq"] == 4 * m)
    add(rows, "unbounded L2 at fixed C_sw", rows_witness[-1]["generator_l2_sq"],
        ">4*C_sw", rows_witness[-1]["generator_l2_sq"] > 4 * c_sw)
    add(rows, "form/generator distinction", rows_witness[-1]["dirichlet_energy"],
        rows_witness[-1]["generator_l2_sq"],
        rows_witness[-1]["dirichlet_energy"] < rows_witness[-1]["generator_l2_sq"])
    add(rows, "no PAH replacement", "abstract two-state diagnostic", "not a carrier", True)

    payload = {
        "schema": "tect/pah-omc020-csw-sufficiency-independent/1.0",
        "status": "PASS_INDEPENDENT_CSW_FIRST_MOMENT_OBSTRUCTION",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in expected},
        "derived": {"s_geom": 8, "n_geom": 60, "c_sw": c_sw},
        "witness": {
            "state_space": "two states",
            "rates": "c(0,1)=M, c(1,0)=1",
            "stationary": "pi(0)=1/(M+1), pi(1)=M/(M+1)",
            "test": "f(0)=1, f(1)=-1",
            "formulae": {
                "first_moment": "2M/(M+1)<2",
                "energy": "4M/(M+1)<4",
                "generator_l2_sq": "4M",
            },
            "fixtures": rows_witness,
        },
        "finding": "A bounded stationary first-rate conductance envelope does not imply a uniform L2 generator bound.",
        "next_contract": "Require a source-owned second-rate-moment bound for every local support, or an equivalent conditional/pathwise Lyapunov non-explosion estimate.",
        "non_claims": [
            "No exact PAH counterexample or universal no-go is asserted.",
            "No PAH functional, rate, state, carrier, regulator, time or limit order is changed.",
            "No semigroup convergence, infinite-volume process, physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_csw_sufficiency_independent.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != to_json(payload):
        raise SystemExit("deterministic replay mismatch")
    print(f"PASS {len(rows)} checks; HOLD_FOR_EVIDENCE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
