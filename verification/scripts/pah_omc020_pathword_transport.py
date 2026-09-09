#!/usr/bin/env python3
"""Check the exact PAH-OMC-020 path-word transport envelope.

This is a bounded analytic sub-lemma for the anchored-n N2c/N4 problem.  It
does not replace the PAH generator.  For a prescribed admissible non-radial
root word, the detailed-balance square identity telescopes along the word;
the stationary L2 mass is therefore at most one when every source mobility is
at most one.  A connected-word count then gives an explicit factorial tail
once a root-overlap branching constant and a word-to-Duhamel attribution are
supplied.  Those two source-level inputs remain open here.
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
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-pathword/primary.json"
)

PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC018 = ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json"
OMC018_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
OMC020_WORK = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def product(values: list[Fraction]) -> Fraction:
    value = Fraction(1)
    for item in values:
        value *= item
    return value


def path_square_transport(weights: list[Fraction], mobilities: list[Fraction]) -> dict:
    """Return the exact telescoping sides for one root word.

    `weights[i]` stands for the stationary density at the state reached after
    i moves.  The source midpoint rate has squared factor
    m_i^2 * weights[i+1]/weights[i].
    """
    if len(weights) != len(mobilities) + 1:
        raise ValueError("word length mismatch")
    if any(weight <= 0 for weight in weights):
        raise ValueError("stationary weights must be positive")
    if any(mobility < 0 or mobility > 1 for mobility in mobilities):
        raise ValueError("mobility must lie in [0,1]")
    squared_rates = [
        mobility * mobility * weights[index + 1] / weights[index]
        for index, mobility in enumerate(mobilities)
    ]
    left = weights[0] * product(squared_rates)
    right = weights[-1] * product([mobility * mobility for mobility in mobilities])
    return {
        "left": left,
        "right": right,
        "squared_rates": squared_rates,
        "mobility_product_square": product([mobility * mobility for mobility in mobilities]),
    }


def factorial_tail(a: int, branching: int, time: Fraction, distance: int) -> Fraction:
    """Geometric-ratio upper bound for a connected-word simplex tail."""
    if a <= 0 or branching <= 0 or time < 0 or distance < 1:
        raise ValueError("positive tail inputs required")
    ratio = Fraction(branching) * time / (distance + 1)
    if ratio >= 1:
        raise ValueError("ratio condition is not met")
    first = Fraction(a * (branching ** (distance - 1))) * (time ** distance)
    first /= math.factorial(distance)
    return first / (1 - ratio)


def source_checks(rows: list[dict]) -> None:
    for relative, expected in PINS.items():
        path = ROOT / relative
        check(rows, "source:" + relative, path.is_file() and digest(path) == expected,
              digest(path) if path.is_file() else "MISSING", expected)
        if path.is_file() and path.suffix in {".json", ".md"}:
            check(rows, "LF:" + relative, b"\r" not in path.read_bytes(), True, "LF-only")
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    omc = json.loads(OMC004.read_text(encoding="utf-8"))
    omc18 = json.loads(OMC018.read_text(encoding="utf-8"))
    prereg = json.loads(OMC020.read_text(encoding="utf-8"))
    check(rows, "unchanged midpoint generator",
          pah["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r m_r(x) exp"),
          pah["dynamics"]["generator"], "PAH-001 midpoint rate")
    check(rows, "external Markov time retained",
          pah["dynamics"]["time"] == "t is external stochastic time; local clock accumulation is d tau_v=s_v^nu dt",
          pah["dynamics"]["time"], "external stochastic time")
    check(rows, "OMC-004 degree bound retained",
          omc["exact_scope"]["strip_family"]["degree_bound"] == 5,
          omc["exact_scope"]["strip_family"]["degree_bound"], 5)
    check(rows, "OMC-004 face bound retained",
          omc["exact_scope"]["strip_family"]["face_incidence_bound"] == 4,
          omc["exact_scope"]["strip_family"]["face_incidence_bound"], 4)
    check(rows, "R-511 inverse-square input named",
          "pi(x)c_r(x)^2=m_r(x)^2 pi(y)" in OMC018_CERT.read_text(encoding="utf-8"),
          True, True)
    check(rows, "N2c remains an open obligation",
          "N2c" in OMC020_WORK.read_text(encoding="utf-8"),
          True, "N2c present in anchored-n work contract")
    check(rows, "R-511 scope is pre-form only",
          "pre-form" in omc18["conclusion"].lower(), omc18["conclusion"], "pre-form")


def compute() -> dict:
    rows: list[dict] = []
    source_checks(rows)

    # A three-state cycle is a labelled exact fixture.  It is not a fitted PAH
    # state and is used only to test the algebraic transport identity.
    cycle_weights = [Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)]
    cycle_mobilities = [Fraction(3, 4), Fraction(2, 3)]
    cycle_rows = []
    stationary_mass = Fraction(0)
    terminal_mass = Fraction(0)
    for start in range(len(cycle_weights)):
        weights = [
            cycle_weights[start],
            cycle_weights[(start + 1) % len(cycle_weights)],
            cycle_weights[(start + 2) % len(cycle_weights)],
        ]
        transported = path_square_transport(weights, cycle_mobilities)
        check(rows, f"cycle telescoping row {start}", transported["left"] == transported["right"],
              str(transported["left"]), str(transported["right"]))
        stationary_mass += transported["left"]
        terminal_mass += transported["right"]
        cycle_rows.append({
            "start": start,
            "left": str(transported["left"]),
            "right": str(transported["right"]),
        })
    check(rows, "cycle stationary mass bound", stationary_mass <= sum(cycle_weights),
          str(stationary_mass), f"<= {sum(cycle_weights)}")
    check(rows, "cycle terminal mass accounting", terminal_mass <= sum(cycle_weights),
          str(terminal_mass), f"<= {sum(cycle_weights)}")

    # The simplex volume is exact.  The connected-word count is deliberately a
    # symbolic contract input; the fixture values below are test oracles.
    fixture_a = 3
    fixture_branching = 5
    fixture_time = Fraction(1)
    distances = [8, 12, 16]
    tails = []
    previous = None
    for distance in distances:
        volume = fixture_time ** distance / math.factorial(distance)
        check(rows, f"simplex volume k={distance}", volume == Fraction(1, math.factorial(distance)),
              str(volume), str(Fraction(1, math.factorial(distance))))
        bound = factorial_tail(fixture_a, fixture_branching, fixture_time, distance)
        # Check the geometric ratio used in the tail proof for several terms.
        ratio = Fraction(fixture_branching) * fixture_time / (distance + 1)
        for k in range(distance, distance + 5):
            term = Fraction(fixture_a * fixture_branching ** (k - 1)) * fixture_time ** k
            term /= math.factorial(k)
            next_term = Fraction(fixture_a * fixture_branching ** k) * fixture_time ** (k + 1)
            next_term /= math.factorial(k + 1)
            check(rows, f"tail ratio d={distance},k={k}", next_term <= ratio * term,
                  str(next_term / term), f"<= {ratio}")
        if previous is not None:
            check(rows, f"tail decreases {previous[0]}->{distance}", bound < previous[1],
                  str(bound), f"< {previous[1]}")
        previous = (distance, bound)
        tails.append({"distance": distance, "bound": str(bound), "ratio": str(ratio)})

    check(rows, "factorial tail decreases on fixture distances",
          all(Fraction(tails[index]["bound"]) > Fraction(tails[index + 1]["bound"])
              for index in range(len(tails) - 1)),
          [item["bound"] for item in tails], "strictly decreasing")

    return {
        "schema": "tect/pah-omc020-pathword-primary/1.0",
        "status": "PASS_PATHWORD_TRANSPORT",
        "verdict": "AUXILIARY_SUPPORT",
        "claim_bearing": False,
        "conditional": True,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": PINS,
        "checks": rows,
        "path_word_transport": {
            "identity": "nu(x) product_i c_{r_i}(x_{i-1})^2 = product_i m_{r_i}(x_{i-1})^2 nu(x_k)",
            "mobility_condition": "0 <= m_r <= 1 from the unchanged PAH aperture interval and source mobility rule",
            "fixed_word_l2_bound": "integrated squared word mass <= 1 after partial-bijection change of variables",
            "cycle_fixture": cycle_rows,
        },
        "connected_word_tail": {
            "count_contract": "N_k <= a b^(k-1) for connected words of length k",
            "simplex_contract": "jump-time simplex volume T^k/k!",
            "bound": "a b^(d-1) T^d/d! / (1-bT/(d+1)) when bT<d+1",
            "fixture": {"a": fixture_a, "branching": fixture_branching,
                        "time": str(fixture_time), "tails": tails},
        },
        "source_status": {
            "root_overlap_constant": "NOT_SOURCE_CERTIFIED",
            "connected_word_to_duhamel_attribution": "NOT_PROVED",
            "n2c_n4": "NOT_DISCHARGED",
        },
        "scope": "Exact non-radial PAH-001 root words on finite OMC-004 strips after the R-511 j-limit; algebraic stationary transport and a conditional connected-word tail envelope only.",
        "non_claims": [
            "No anchored-n semigroup convergence, N2a/N2b/N2c/N4 or N2d minimal-form selection.",
            "No common Hilbert-space realization, infinite-volume process, continuum or physical result.",
            "No physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap or TOE conclusion.",
            "External stochastic Markov time is not quantum, proper or Lorentzian time.",
        ],
        "next_single_question": "Can the exact OMC-004 root-incidence data supply one n-uniform overlap constant and a source-valid coupling/Duhamel lemma that attributes N2c boundary influence to connected words?",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    if args.check and args.output.exists():
        expected = args.output.read_bytes()
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 path-word primary replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 PATHWORD PRIMARY: PASS ({len(payload['checks'])} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
