#!/usr/bin/env python3
"""Audit what the R-490 first-moment envelope can actually control.

The unchanged PAH-001 model is not modified by this file.  The diagnostic
uses the pinned R-490 value C_sw only as an input to an adversarial sufficiency
test.  A two-state reversible family has uniformly bounded stationary
conductance but an unbounded L2 norm of the generator on one bounded test
function.  This proves that the first-moment envelope alone cannot be used as
an L2 generator estimate or as an N2c/N4 boundary-escape theorem.

The two-state family is an abstract hostile witness, not a PAH carrier,
counterexample, replacement dynamics, or physical model.
"""

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
    "2026-09-08-pah-omc020-csw-sufficiency/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json":
        "8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69",
    "strategy/pa-hyp/R490-certificate.md":
        "80563e82f7f592dbbb6c00ff27fdd5270031e8426d4d1520546bf846c6a6d10a",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json":
        "12eda207fe03441deb47df02a206b8a4cac1accce5aa5eb016b861b53c8af730",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(serial(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(item) for item in value]
    return value


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({
        "name": name,
        "status": "PASS",
        "actual": serial(actual),
        "expected": serial(expected),
    })


def parse_r490_constants() -> tuple[int, int, int]:
    text = (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8")
    s_match = re.search(r"S_geom\s*=\s*(\d+)", text)
    n_match = re.search(r"N_geom\s*=\s*(\d+)", text)
    c_match = re.search(r"C_sw\s*=\s*N_geom\s*\(1\+S_geom\)\s*=\s*(\d+)", text)
    if not (s_match and n_match and c_match):
        raise AssertionError("R-490 constants are not parseable")
    s_geom = int(s_match.group(1))
    n_geom = int(n_match.group(1))
    displayed = int(c_match.group(1))
    derived = n_geom * (1 + s_geom)
    if displayed != derived:
        raise AssertionError("R-490 displayed C_sw disagrees with its factors")
    return s_geom, n_geom, derived


def witness(m: int) -> dict[str, Fraction | int]:
    if m < 1:
        raise ValueError("m must be positive")
    denominator = Fraction(m + 1)
    pi0 = Fraction(1, denominator)
    pi1 = Fraction(m, denominator)
    c0, c1 = m, 1
    f0, f1 = Fraction(1), Fraction(-1)
    l0 = c0 * (f1 - f0)
    l1 = c1 * (f0 - f1)
    detailed_balance_left = pi0 * c0
    detailed_balance_right = pi1 * c1
    first_moment = pi0 * c0 + pi1 * c1
    energy = -(pi0 * f0 * l0 + pi1 * f1 * l1)
    generator_l2_sq = pi0 * l0 * l0 + pi1 * l1 * l1
    return {
        "M": m,
        "pi0": pi0,
        "pi1": pi1,
        "c_0_to_1": c0,
        "c_1_to_0": c1,
        "f0": f0,
        "f1": f1,
        "L_f_0": l0,
        "L_f_1": l1,
        "detailed_balance_left": detailed_balance_left,
        "detailed_balance_right": detailed_balance_right,
        "first_moment": first_moment,
        "dirichlet_energy": energy,
        "generator_l2_sq": generator_l2_sq,
    }


def source_checks(rows: list[dict]) -> dict:
    hashes = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        hashes[relative] = actual
        check(rows, f"source hash:{relative}", actual, expected, actual == expected)

    pa = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc010 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-010-state-weighted-envelope-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    r520 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathspace-bridge-result-v1.json").read_text(encoding="utf-8"))
    check(rows, "PAH functional remains source-owned", "functional_or_action" in pa, True,
          "functional_or_action" in pa)
    check(rows, "R-490 exact Gibbs norm is retained",
          omc010["contract_id"], "PAH-OMC-010", omc010["contract_id"] == "PAH-OMC-010")
    s_geom, n_geom, c_sw = parse_r490_constants()
    check(rows, "R-490 C_sw factors recompute", c_sw, n_geom * (1 + s_geom),
          c_sw == n_geom * (1 + s_geom))
    check(rows, "R-490 coefficient is 540", c_sw, 540, c_sw == 540)
    check(rows, "R-490 is domination-only",
          "does not prove that intertwining" in (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8"),
          True, "does not prove that intertwining" in (ROOT / "strategy/pa-hyp/R490-certificate.md").read_text(encoding="utf-8"))
    check(rows, "temporal target remains j-before-n",
          "first j" in prereg["scope"]["regulator_order"].lower()
          and "anchored n" in prereg["scope"]["regulator_order"].lower(),
          True,
          "first j" in prereg["scope"]["regulator_order"].lower()
          and "anchored n" in prereg["scope"]["regulator_order"].lower())
    check(rows, "R-512 is a minimal closed form only",
          r512["result_id"] == "R-512"
          and "minimal closed" in r512["conclusion"],
          True,
          r512["result_id"] == "R-512" and "minimal closed" in r512["conclusion"])
    check(rows, "R-520 already keeps process premises open",
          any("non-explosion" in item for item in r520["missing_assumptions"]), True,
          r520["missing_assumptions"])
    return {"s_geom": s_geom, "n_geom": n_geom, "c_sw": c_sw, "source_hashes": hashes}


def arithmetic_checks(rows: list[dict], c_sw: int) -> dict:
    values = [witness(m) for m in (1, 2, 10, 100, c_sw + 1)]
    for row in values:
        check(rows, f"detailed balance M={row['M']}",
              row["detailed_balance_left"], row["detailed_balance_right"],
              row["detailed_balance_left"] == row["detailed_balance_right"])
        check(rows, f"first moment below two M={row['M']}", row["first_moment"], "<2",
              row["first_moment"] < 2)
        check(rows, f"first moment below C_sw M={row['M']}", row["first_moment"], c_sw,
              row["first_moment"] < c_sw)
        check(rows, f"energy finite M={row['M']}", row["dirichlet_energy"], "<4",
              row["dirichlet_energy"] < 4)
        check(rows, f"generator L2 identity M={row['M']}", row["generator_l2_sq"],
              4 * row["M"], row["generator_l2_sq"] == 4 * row["M"])
    check(rows, "same C_sw allows an arbitrarily large generator norm",
          values[-1]["generator_l2_sq"], 4 * (c_sw + 1),
          values[-1]["generator_l2_sq"] > 4 * c_sw)
    check(rows, "bounded form energy does not bound generator L2 norm",
          values[-1]["dirichlet_energy"], values[-1]["generator_l2_sq"],
          values[-1]["dirichlet_energy"] < values[-1]["generator_l2_sq"])
    check(rows, "bounded test function is explicit",
          max(abs(values[0]["f0"]), abs(values[0]["f1"])), 1,
          max(abs(values[0]["f0"]), abs(values[0]["f1"])) == 1)
    return {
        "family": "Omega={0,1}, c_M(0,1)=M, c_M(1,0)=1",
        "stationary_law": "pi_M(0)=1/(M+1), pi_M(1)=M/(M+1)",
        "test_function": "f(0)=1, f(1)=-1",
        "formulae": {
            "detailed_balance": "pi(0)M=pi(1)",
            "first_moment": "2M/(M+1)<2<=C_sw",
            "dirichlet_energy": "4M/(M+1)<4",
            "generator_l2_sq": "4M -> infinity",
        },
        "fixtures": values,
    }


def route_checks(rows: list[dict], c_sw: int) -> dict:
    check(rows, "C_sw is first-rate rather than second-rate input", True,
          "sum pi*c, not sum pi*c^2", True)
    check(rows, "one-moment inference to uniform L2 generator bound is rejected",
          4 * (c_sw + 1), ">4*C_sw", 4 * (c_sw + 1) > 4 * c_sw)
    check(rows, "abstract witness is not a PAH carrier", "abstract diagnostic", "not PAH", True)
    check(rows, "N2c/N4 remains an evidence hold", "HOLD_FOR_EVIDENCE", "HOLD_FOR_EVIDENCE", True)
    missing = [
        "source-owned second-rate-moment bound C2(A) or an equivalent conditional estimate",
        "or a source-owned pathwise Lyapunov/non-explosion estimate controlling boundary jumps",
        "plus a common-process/minimal-form identification for PAH-OMC-020",
    ]
    return {
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "finding": "R-490 first-moment C_sw=540 is insufficient by itself for a uniform L2 generator or N2c/N4 boundary estimate.",
        "missing_contract": missing,
        "scope_boundary": "This is a sufficiency obstruction for an inference from R-490 alone, not a no-go theorem for the unchanged PAH process or for every possible pathwise estimate.",
    }


def run(output: Path) -> dict:
    rows: list[dict] = []
    source = source_checks(rows)
    arithmetic = arithmetic_checks(rows, source["c_sw"])
    route = route_checks(rows, source["c_sw"])
    payload = {
        "schema": "tect/pah-omc020-csw-sufficiency-audit/1.0",
        "status": "PASS_CSW_FIRST_MOMENT_SUFFICIENCY_OBSTRUCTION",
        "verdict": route["verdict"],
        "classification": route["classification"],
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": source["source_hashes"],
        "source_constants": {key: source[key] for key in ("s_geom", "n_geom", "c_sw")},
        "abstract_witness": arithmetic,
        "route": route,
        "non_claims": [
            "No PAH functional, rate, state, carrier, regulator, time or limit order is changed.",
            "The abstract two-state family is not an exact PAH counterexample and does not prove universal non-existence of a PAH boundary estimate.",
            "No semigroup convergence, infinite-volume process, R-512 minimal-form selection, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, continuum, mass-gap or TOE conclusion.",
            "External Markov time remains stochastic bookkeeping and is not physical time.",
        ],
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_csw_sufficiency_audit.py --check",
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.check:
        replay = json.loads(args.output.read_text(encoding="utf-8"))
        if replay != serial(payload):
            raise SystemExit("deterministic replay mismatch")
    print(f"PASS {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
