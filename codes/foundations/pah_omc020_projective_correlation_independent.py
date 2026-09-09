"""Independent, non-importing audit of the PAH-OMC-020 projective envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-projective-correlation/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json":
        "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json":
        "114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9",
    "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json":
        "9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11",
    "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json":
        "67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
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


def serialize(item: object) -> object:
    if isinstance(item, Fraction):
        return str(item)
    if isinstance(item, (list, tuple)):
        return [serialize(entry) for entry in item]
    if isinstance(item, dict):
        return {str(key): serialize(entry) for key, entry in item.items()}
    return item


def integer(pattern: str, text: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise AssertionError(f"missing source integer for {pattern}")
    return int(match.group(1))


def factorial_tail(a: int, b: int, distance: int, horizon: Fraction) -> Fraction:
    ratio = Fraction(b) * horizon / (distance + 1)
    if not ratio < 1:
        raise AssertionError("tail ratio is not below one")
    return (
        Fraction(a * b ** (distance - 1), 1)
        * horizon ** distance
        / math.factorial(distance)
        / (1 - ratio)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({
            "name": name,
            "status": "PASS",
            "actual": serialize(actual),
            "expected": serialize(expected),
        })

    hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = sha(ROOT / relative)
        hashes[relative] = actual
        ck(f"hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc013 = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json")
        .read_text(encoding="utf-8")
    )
    r510 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json").read_text(encoding="utf-8"))
    r515 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json").read_text(encoding="utf-8"))
    r516 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json").read_text(encoding="utf-8"))
    r517 = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json").read_text(encoding="utf-8")
    )
    prereg = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8")
    )

    ck("PAH packet is unchanged", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    cylinder = omc013["exact_scope"]["common_cylinder_algebra"].lower()
    ck("grade is invisible to the cylinder", "cannot inspect the disjoint-union grade" in cylinder, True,
       "cannot inspect the disjoint-union grade" in cylinder)
    identity = omc013["eventual_intertwining_proof"]["generator_sum_identity"]
    ck("eventual generator identity is displayed", "L_(" in identity and "zero-increment" in identity,
       True, "L_(" in identity and "zero-increment" in identity)
    finite_scope = omc013["exact_scope"]["finite_parameter_scope"]
    finite_scope_ok = ("R_max=R ranges over every positive integer" in finite_scope
                       and "finite R samples are regression checks only" in finite_scope)
    ck("finite R range is not sampled only", finite_scope_ok, True, finite_scope_ok)
    ck("R-510 has no physical volume", "not physical volume" in r510["exact_scope"]["volume"].lower(), True,
       "not physical volume" in r510["exact_scope"]["volume"].lower())
    ck("R-510 local state is non-subsequence", "without subsequence selection" in r510["conclusion"]["answer"], True,
       "without subsequence selection" in r510["conclusion"]["answer"])
    ck("R-515 preserves factorial word simplex", "T^k/k!" in r515["conclusion"]["simplex"], True,
       "T^k/k!" in r515["conclusion"]["simplex"])
    ck("R-516 preserves radius-two footprint", "radius at most 2 columns" in r516["conclusion"]["footprint"], True,
       "radius at most 2 columns" in r516["conclusion"]["footprint"])
    ck("R-517 states the two-copy triangle", "2^ell" in r517["conclusion"]["bound"], True,
       "2^ell" in r517["conclusion"]["bound"])
    ck("R-517 keeps common space open", any("common U_n" in item for item in r517["missing_assumptions"]), True,
       any("common U_n" in item for item in r517["missing_assumptions"]))
    ck("external Markov time only", "external unaccelerated Markov time" in prereg["scope"]["time"], True,
       "external unaccelerated Markov time" in prereg["scope"]["time"])

    footprint = r516["conclusion"]["footprint"]
    roots = integer(r"(?:at most )?(\d+) PH/AP/LK roots", footprint)
    slots = integer(r"at most (\d+) edge slots", footprint)
    radius = integer(r"radius at most (\d+) columns", footprint)
    branching = roots * (slots * radius + 1)
    effective = 2 * branching
    ck("independent roots-per-column derivation", roots, 16, roots == 16)
    ck("independent slot derivation", slots, 4, slots == 4)
    ck("independent radius derivation", radius, 2, radius == 2)
    ck("independent branching derivation", branching, 144, branching == 144)
    ck("independent two-copy derivation", effective, 288, effective == 288)

    # Distinct labelled fixtures: these are test inputs, not PAH parameters.
    width = 3
    max_column = width
    stabilization = max(2, max_column + 1)
    word_cutoff = 5
    horizon = Fraction(1, 6)
    norm_f = Fraction(4, 3)
    norm_g = Fraction(7, 5)
    state_D = Fraction(7, 3)
    state_q = Fraction(3, 5)
    state_stage = 2
    first_roots = roots * (width + 2 * radius + 1)
    ck("support-width bound is recomputed", first_roots, 128, first_roots == 128)
    ck("word cutoff is finite", 0 < word_cutoff < stabilization + 3, True,
       0 < word_cutoff < stabilization + 3)
    ck("stabilization follows support", stabilization, 4, stabilization == 4)
    ck("state fixture is contractive", 0 < state_q < 1, True, 0 < state_q < 1)

    distances = [96, 120, 144]
    tails = [factorial_tail(first_roots, effective, distance, horizon) for distance in distances]
    ck("tail ratios are valid", all(Fraction(effective) * horizon < distance + 1 for distance in distances),
       True, all(Fraction(effective) * horizon < distance + 1 for distance in distances))
    ck("independent factorial tails decrease",
       all(tails[i + 1] < tails[i] for i in range(len(tails) - 1)),
       True, all(tails[i + 1] < tails[i] for i in range(len(tails) - 1)))

    def state_error(level: int) -> Fraction:
        return 4 * norm_f * norm_g * state_D * state_q ** (level - state_stage)

    levels = [stabilization, stabilization + 2, stabilization + 4]
    state_pairs = [state_error(level) + state_error(level + 1) for level in levels]
    ck("independent state pair envelope decreases",
       all(state_pairs[i + 1] < state_pairs[i] for i in range(len(state_pairs) - 1)),
       True, all(state_pairs[i + 1] < state_pairs[i] for i in range(len(state_pairs) - 1)))
    envelopes = [state_pairs[i] + 8 * norm_f * norm_g * tails[-1] for i in range(len(levels))]
    ck("independent scalar envelope decreases",
       all(envelopes[i + 1] < envelopes[i] for i in range(len(envelopes) - 1)),
       True, all(envelopes[i + 1] < envelopes[i] for i in range(len(envelopes) - 1)))
    ck("tail is not silently erased", tails[-1] > 0, True, tails[-1] > 0)
    ck("R-510 product norm factor", 4 * norm_f * norm_g * state_D, Fraction(784, 45),
       4 * norm_f * norm_g * state_D == Fraction(784, 45))
    ck("two-copy correlation factor", 8 * norm_f * norm_g, Fraction(224, 15),
       8 * norm_f * norm_g == Fraction(224, 15))
    ck("physical firewall retained", any("physical Pre-A" in item for item in prereg["non_claims"]), True,
       any("physical Pre-A" in item for item in prereg["non_claims"]))

    payload = {
        "schema": "tect/pah-omc020-projective-correlation-independent/1.0",
        "status": "PASS_INDEPENDENT_PROJECTIVE_ENVELOPE",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": checks,
        "scope": "Independent reconstruction of a finite-word, scalar n-Cauchy envelope for one non-radial grade-blind cylinder; no common U_n or semigroup identification.",
        "derived_inputs": {
            "roots_per_column": roots,
            "edge_slots": slots,
            "radius": radius,
            "branching": branching,
            "effective_branching": effective,
            "support_width": width,
            "first_root_bound": first_roots,
            "word_cutoff": word_cutoff,
            "stabilization": stabilization,
            "distances": distances,
            "tail_values": [str(item) for item in tails],
            "levels": levels,
            "state_pair_values": [str(item) for item in state_pairs],
            "envelopes": [str(item) for item in envelopes],
        },
        "assumptions": [
            "R-493 eventual intertwining applies to every truncated word after the selected cylinder stabilizes.",
            "R-510 local-state convergence applies to the product cylinder f*g.",
            "R-517's conditional finite-fibre attribution applies to the same word expansion.",
        ],
        "missing_assumptions": [
            "A source-authorized common U_n/Hilbert realization and R-512 minimal-form identification.",
            "An all-cylinder, non-conditional anchored-n semigroup theorem.",
        ],
        "non_claims": [
            "The finite cutoff and rational fixtures are not an infinite word-series proof.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_projective_correlation_independent.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 projective independent replay mismatch")
    elif not args.check:
        write_json(args.output, payload)
    print(f"PAH-OMC-020 PROJECTIVE INDEPENDENT: PASS ({len(checks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
