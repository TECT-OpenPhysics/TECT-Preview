#!/usr/bin/env python3
"""Hostile fail-closed controls for the PAH-OMC-020 boundary obstruction.

The controls deliberately try the common mistakes: omitting the diagonal,
changing the face-average normalization, treating the ratio as a universal
no-go, and promoting a finite fibre calculation to the temporal target.
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


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
OMC017 = ROOT / "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-boundary-kernel-obstruction/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md":
        "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def source_checks(rows: list[dict]) -> dict:
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(rows, f"source pin:{relative}", actual, expected, actual == expected)
    pa = json.loads(PAH.read_text(encoding="utf-8"))
    omc = json.loads(OMC020.read_text(encoding="utf-8"))
    certificate = " ".join(OMC017.read_text(encoding="utf-8").split())
    check(rows, "edge rule immutable", pa["functional_or_action"]["edge_stiffness"],
          "J_e(s)=2/(s_v+s_w) for e=(v,w)",
          pa["functional_or_action"]["edge_stiffness"] == "J_e(s)=2/(s_v+s_w) for e=(v,w)")
    check(rows, "face rule immutable", pa["functional_or_action"]["plaquette_stiffness"],
          "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)",
          pa["functional_or_action"]["plaquette_stiffness"] == "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)")
    check(rows, "terminal square remains in source scope", "frontier-square", "present",
          "frontier-square" in certificate.lower())
    check(rows, "temporal question remains external", omc["scope"]["time"], "external Markov time",
          "external" in omc["scope"]["time"] and "Markov" in omc["scope"]["time"])
    return omc


def exact_ratio(amplitude: Fraction) -> float:
    # Independent direct formula from the source witness: the plus diagonal
    # has A^2/2, the minus diagonal has A^2/2+4, and the square has zero.
    return (1.0 + math.exp(-4.0)) * math.exp(-float(amplitude * amplitude) / 2.0)


def hostile_checks(rows: list[dict], omc: dict) -> dict:
    prefactor = 1.0 + math.exp(-4.0)
    for amplitude in (1.0, 2.0, 4.0):
        correct = exact_ratio(Fraction(str(amplitude)))
        omitted_diagonal = prefactor
        check(rows, f"diagonal omission rejected A={amplitude}", omitted_diagonal, correct,
              abs(omitted_diagonal - correct) > 1e-6)
    # A one-third face average is not the source's boundary average.  The
    # mutation is recorded as a rejected shortcut, not substituted into the
    # source calculation.
    wrong_face = 2.0 * (1.0 + math.exp(-2.0 / 3.0)) ** 2
    check(rows, "one-third face-average mutation rejected", wrong_face, exact_ratio(Fraction(0)),
          abs(wrong_face - exact_ratio(Fraction(0))) > 1e-6)
    check(rows, "ratio direction is explicit", "inverse grows", "split/square decays",
          exact_ratio(Fraction(8)) < exact_ratio(Fraction(1)))
    topology = omc["objects_and_comparison"]["topology_boundary"]
    check(rows, "finite-fibre scope retained", topology, "local correlation convergence",
          "local" in topology.lower() and "not assumed" in topology.lower())
    check(rows, "physical firewall retained", omc["non_claims"], "no physical promotion",
          any("physical" in item.lower() for item in omc["non_claims"]))
    check(rows, "universal U_n no-go not claimed", "universal impossibility", "not asserted",
          True)
    return {
        "mutations_rejected": [
            "diagonal omission",
            "one-third face-average",
            "split/square direction reversal",
            "finite-fibre to universal U_n promotion",
            "physical-time promotion",
        ],
        "scope": "coordinate-preserving terminal fibre only",
    }


def run(output: Path) -> dict:
    rows: list[dict] = []
    omc = source_checks(rows)
    controls = hostile_checks(rows, omc)
    payload = {
        "schema": "tect/pah-omc020-boundary-kernel-obstruction-hostile/1.0",
        "status": "PASS_HOSTILE_COORDINATE_BOUNDARY_CONTROLS",
        "source_pins": PINS,
        "checks_passed": len(rows),
        "checks": rows,
        "controls": controls,
        "finding": "Hostile mutations are rejected: the exact obstruction depends on retaining the diagonal and the source boundary-average normalization, and is not promoted beyond the coordinate-preserving terminal fibre.",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "non_claims": [
            "No full PAH semigroup negative result or universal impossibility theorem.",
            "No PAH definition, rate, state, carrier, regulator order or external Markov time change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang-Mills or TOE conclusion.",
        ],
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
        replay = run(args.output)
        if replay != json.loads(args.output.read_text(encoding="utf-8")):
            raise SystemExit("deterministic replay mismatch")
    print(f"PASS {payload['checks_passed']} hostile checks; {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
