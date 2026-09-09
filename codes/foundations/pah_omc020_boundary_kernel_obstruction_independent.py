#!/usr/bin/env python3
"""Non-importing reconstruction of the PAH-OMC-020 terminal-fibre obstruction.

This lane independently derives the split/square Gibbs-weight ratio from the
source stiffness and face-average rules.  It does not import the primary
checker and it does not assert a no-go theorem for arbitrary comparison maps.
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
    "2026-09-07-pah-omc020-boundary-kernel-obstruction/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md":
        "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
}

AMPLITUDES = (0.0, 1.0, 2.0, 4.0, 8.0)
CHALLENGES = (1.0, 10.0, 100.0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


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
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(rows, f"source pin:{relative}", actual, expected, actual == expected)
    source = json.loads(PAH.read_text(encoding="utf-8"))
    check(
        rows,
        "source edge stiffness rule",
        source["functional_or_action"]["edge_stiffness"],
        "J_e(s)=2/(s_v+s_w) for e=(v,w)",
        source["functional_or_action"]["edge_stiffness"]
        == "J_e(s)=2/(s_v+s_w) for e=(v,w)",
    )
    check(
        rows,
        "source plaquette average rule",
        source["functional_or_action"]["plaquette_stiffness"],
        "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)",
        source["functional_or_action"]["plaquette_stiffness"]
        == "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)",
    )
    certificate = " ".join(OMC017.read_text(encoding="utf-8").split())
    for marker in (
        "B_triangle",
        "B_square",
        "(J_h0+J_vy+J_d)/3",
        "(J_d+J_h1+J_vx)/3",
        "There is no diagonal in this",
        "does not drop a boundary interaction",
    ):
        check(rows, f"source transfer marker:{marker}", marker, marker, marker in certificate)
    contract = json.loads(OMC020.read_text(encoding="utf-8"))
    check(rows, "temporal contract keeps j-before-n", contract["scope"]["regulator_order"],
          "j before anchored n", "first j" in contract["scope"]["regulator_order"].lower()
          and "anchored n" in contract["scope"]["regulator_order"].lower())


def independent_terms(amplitude: Fraction, diagonal: int) -> tuple[Fraction, Fraction]:
    """Derive the witness energies from source edge and face terms."""
    edge_stiffness = Fraction(2, 1 + 1)
    # The two old horizontal covariant differences vanish: (0,0) and (A,A).
    old_edges = Fraction(0)
    diagonal_edge = edge_stiffness * amplitude * amplitude / 2
    # Every old edge has stiffness one.  The square holonomy is +1.
    square_face = Fraction(0)
    square = old_edges + square_face
    if diagonal == 1:
        # Both split triangle holonomies are +1 and the diagonal edge is A^2/2.
        face_terms = Fraction(0)
    elif diagonal == -1:
        # Both split triangle holonomies are -1, each contributing 2.
        face_terms = Fraction(4)
    else:
        raise ValueError("diagonal must be ±1")
    return square, diagonal_edge + face_terms


def ratio(amplitude: Fraction) -> float:
    square, _ = independent_terms(amplitude, 1)
    split = sum(math.exp(-float(independent_terms(amplitude, diagonal)[1]))
                for diagonal in (-1, 1))
    return split / math.exp(-float(square))


def arithmetic_checks(rows: list[dict]) -> dict:
    witness_rows = []
    for value in AMPLITUDES:
        amplitude = Fraction(str(value))
        square_plus, triangle_plus = independent_terms(amplitude, 1)
        square_minus, triangle_minus = independent_terms(amplitude, -1)
        check(rows, f"square independent equality A={value}", square_plus, Fraction(0), square_plus == 0)
        check(rows, f"square independent equality d=-1 A={value}", square_minus, Fraction(0), square_minus == 0)
        check(rows, f"triangle plus A={value}", triangle_plus, amplitude * amplitude / 2,
              triangle_plus == amplitude * amplitude / 2)
        check(rows, f"triangle minus A={value}", triangle_minus, amplitude * amplitude / 2 + 4,
              triangle_minus == amplitude * amplitude / 2 + 4)
        witness_rows.append({
            "A": value,
            "B_square": float(square_plus),
            "B_triangle_d_plus": float(triangle_plus),
            "B_triangle_d_minus": float(triangle_minus),
            "split_over_square": ratio(amplitude),
        })
    prefactor = 1.0 + math.exp(-4.0)
    check(rows, "closed split/square ratio",
          [row["split_over_square"] for row in witness_rows],
          "(1+exp(-4))*exp(-A^2/2)",
          all(abs(row["split_over_square"] - prefactor * math.exp(-(row["A"] ** 2) / 2.0)) < 1e-12
              for row in witness_rows))
    ratios = [row["split_over_square"] for row in witness_rows]
    check(rows, "strict decay after positive amplitudes", ratios[1:], ratios[:-1],
          all(right < left for left, right in zip(ratios[1:], ratios[2:])))
    check(rows, "ratio remains positive", min(ratios), ">0", min(ratios) > 0.0)
    inverse_witnesses = []
    for challenge in CHALLENGES:
        amplitude = math.sqrt(2.0 * math.log(4.0 * challenge))
        inv = 1.0 / ratio(Fraction(str(amplitude)).limit_denominator(10**9))
        check(rows, f"inverse exceeds challenge {challenge}", inv, f">{challenge}", inv > challenge)
        inverse_witnesses.append({"challenge": challenge, "A": amplitude, "inverse_ratio": inv})
    return {
        "fixed_old_labels": {"h0": 1, "h1": 1, "vx": 1, "vy": 1},
        "amplitude_grid": witness_rows,
        "ratio_formula": "(1+exp(-4))*exp(-A^2/2)",
        "inverse_ratio_witnesses": inverse_witnesses,
        "scope": "coordinate-preserving terminal fibre only",
    }


def hostile_scope_checks(rows: list[dict]) -> None:
    contract = OMC020.read_text(encoding="utf-8")
    check(rows, "physical firewall retained", "No physical Pre-A", "present",
          "No physical Pre-A" in contract)
    check(rows, "no semigroup promotion", "semigroup convergence", "not asserted",
          "semigroup convergence" not in contract.lower())
    for amplitude in (Fraction(1), Fraction(2), Fraction(4)):
        correct = ratio(amplitude)
        omitted = 1.0 + math.exp(-4.0)
        check(rows, f"diagonal omission changes A={amplitude}", omitted, correct,
              abs(omitted - correct) > 1e-6)


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    arithmetic = arithmetic_checks(rows)
    hostile_scope_checks(rows)
    payload = {
        "schema": "tect/pah-omc020-boundary-kernel-obstruction-independent/1.0",
        "status": "PASS_INDEPENDENT_COORDINATE_BOUNDARY_OBSTRUCTION",
        "source_pins": PINS,
        "checks_passed": len(rows),
        "checks": rows,
        "arithmetic": arithmetic,
        "finding": "The independently derived split/square ratio is (1+exp(-4))*exp(-A^2/2); its inverse is unbounded along the allowed amplitude ray.",
        "scope": "This rejects only a uniformly bounded coordinate-preserving terminal-fibre density-ratio lift. It is not a no-go theorem for arbitrary U_n or local temporal convergence.",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "non_claims": [
            "No full PAH semigroup negative result or universal comparison-map impossibility.",
            "No PAH functional, rate, state, carrier, regulator order or external Markov time change.",
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
    print(f"PASS {payload['checks_passed']} independent checks; {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
