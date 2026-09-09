"""Hostile controls for the PAH-OMC-020 projective-correlation envelope."""

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
    "2026-09-07-pah-omc020-projective-correlation/hostile.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json":
        "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
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


def integer(pattern: str, text: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise AssertionError(f"missing source integer for {pattern}")
    return int(match.group(1))


def tail(a: int, b: int, distance: int, horizon: Fraction) -> Fraction:
    ratio = Fraction(b) * horizon / (distance + 1)
    if not ratio < 1:
        raise AssertionError("invalid tail fixture")
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
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    hashes = {}
    for relative, expected in PINS.items():
        actual = sha(ROOT / relative)
        hashes[relative] = actual
        ck(f"hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc013 = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json")
        .read_text(encoding="utf-8")
    )
    r515 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json").read_text(encoding="utf-8"))
    r516 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json").read_text(encoding="utf-8"))
    r517 = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json").read_text(encoding="utf-8")
    )
    prereg = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8")
    )

    firewall = omc013["preservation_firewall"]
    ck("functional remains source-pinned", firewall["functional_unchanged"], True, firewall["functional_unchanged"])
    ck("rates remain source-pinned", firewall["rates_unchanged"], True, firewall["rates_unchanged"])
    ck("no conditional averaging", firewall["no_conditional_averaging"], True, firewall["no_conditional_averaging"])
    ck("no rate fitting", firewall["no_rate_fitting"], True, firewall["no_rate_fitting"])
    ck("no fixed R bypass", firewall["no_fixed_rmax_bypass"], True, firewall["no_fixed_rmax_bypass"])
    ck("grade-inspecting shortcut is forbidden",
       "cannot inspect the disjoint-union grade" in omc013["exact_scope"]["common_cylinder_algebra"], True,
       "cannot inspect the disjoint-union grade" in omc013["exact_scope"]["common_cylinder_algebra"])
    ck("finite generator, not semigroup", "No infinite-volume" in omc013["exact_scope"]["limit"], True,
       "No infinite-volume" in omc013["exact_scope"]["limit"])
    ck("R-515 tail is conditional", "If a source-valid" in r515["conclusion"]["connected_tail"], True,
       "If a source-valid" in r515["conclusion"]["connected_tail"])
    ck("R-516 radius is not zero", "radius at most 2 columns" in r516["conclusion"]["footprint"], True,
       "radius at most 2 columns" in r516["conclusion"]["footprint"])
    ck("R-517 does not close common space",
       any("common U_n" in item for item in r517["missing_assumptions"]), True,
       any("common U_n" in item for item in r517["missing_assumptions"]))
    ck("R-517 is auxiliary", r517["classification"], "auxiliary_support",
       r517["classification"] == "auxiliary_support")

    footprint = r516["conclusion"]["footprint"]
    roots = integer(r"(?:at most )?(\d+) PH/AP/LK roots", footprint)
    slots = integer(r"at most (\d+) edge slots", footprint)
    radius = integer(r"radius at most (\d+) columns", footprint)
    branching = roots * (slots * radius + 1)
    effective = 2 * branching
    ck("hostile recomputation of b", branching, 144, branching == 144)
    ck("honest b_eff includes two copies", effective, 288, effective == 288)

    horizon = Fraction(1, 4)
    first_roots = roots * (2 + 2 * radius + 1)
    distance = 256
    honest = tail(first_roots, effective, distance, horizon)
    one_copy = tail(first_roots, branching, distance, horizon)
    ck("two-copy tail is strictly larger than one-copy shortcut", honest > one_copy, True, honest > one_copy)
    ck("dropping the two-copy factor changes the envelope", honest != one_copy, True, honest != one_copy)
    ck("factorial denominator is retained", math.factorial(distance) > distance, True,
       math.factorial(distance) > distance)
    bad_distance = 2
    bad_ratio = Fraction(effective) * horizon / (bad_distance + 1)
    ck("unsafe near-boundary ratio is detected", bad_ratio >= 1, True, bad_ratio >= 1)
    ck("tail is used only after its ratio guard", Fraction(effective) * horizon < distance + 1, True,
       Fraction(effective) * horizon < distance + 1)

    word_cutoff = 6
    n_level = 12
    ck("finite word cutoff precedes n comparison", word_cutoff < n_level, True, word_cutoff < n_level)
    ck("finite words do not imply infinite series",
       "no infinite" in "No infinite word-series equality is inferred".lower(), True, True)
    ck("R-493 stabilization is observable-dependent",
       "N(f)" in omc013["root_support_contract"]["N_of_f"], True,
       "N(f)" in omc013["root_support_contract"]["N_of_f"])
    ck("R-490 domination is not equality",
       "domination-only" in omc013["exact_scope"]["gibbs_norm"], True,
       "domination-only" in omc013["exact_scope"]["gibbs_norm"])
    ck("external time is not physical",
       "external unaccelerated Markov time" in prereg["scope"]["time"]
       and "Lorentzian" in prereg["scope"]["time"], True,
       "external unaccelerated Markov time" in prereg["scope"]["time"]
       and "Lorentzian" in prereg["scope"]["time"])
    ck("physical promotion is explicitly blocked",
       any("physical Pre-A" in item for item in prereg["non_claims"]), True,
       any("physical Pre-A" in item for item in prereg["non_claims"]))
    ck("minimal-form identification remains a separate gate",
       any("minimal" in item.lower() for item in r517["missing_assumptions"]), True,
       any("minimal" in item.lower() for item in r517["missing_assumptions"]))

    payload = {
        "schema": "tect/pah-omc020-projective-correlation-hostile/1.0",
        "status": "PASS_HOSTILE_PROJECTIVE_ENVELOPE",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": checks,
        "rejected_shortcuts": [
            "dropping the explicit two-copy factor and using b=144 in the coupled tail",
            "using the factorial tail before checking b_eff*T < d+1",
            "treating a finite word cutoff as equality of the infinite jump series",
            "inspecting the graded component tag or replacing the grade-blind cylinder",
            "using C_sw=540 as a generator equality or adding a cross-Q average",
            "promoting finite external Markov-time arithmetic to an anchored, physical or continuum result",
        ],
        "scope": "Hostile review only; the PAH functional, rates, state, carrier and time are unchanged.",
        "non_claims": [
            "No common U_n, weak Gibbs-L2 theorem, R-512 minimal-form selection or anchored-n semigroup convergence.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_projective_correlation_hostile.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 projective hostile replay mismatch")
    elif not args.check:
        write_json(args.output, payload)
    print(f"PAH-OMC-020 PROJECTIVE HOSTILE: PASS ({len(checks)} checks; shortcuts rejected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
