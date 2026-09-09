"""Audit a conditional projective local-correlation envelope for PAH-OMC-020.

The calculation is deliberately smaller than the anchored-n objective.  It
combines the finite, grade-blind eventual intertwining recorded by R-493 with
the registered Gibbs word transport and two-copy factorial tail (R-515--R-517).
Only a scalar envelope for one finite-support non-radial cylinder is recorded.
No common U_n, completed Hilbert space, semigroup limit, or physical
interpretation is asserted.
"""

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
    "2026-09-07-pah-omc020-projective-correlation/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json":
        "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json":
        "8d005bea7ee33111712f58a32046cdb254f77bc8c17d8eb1a470abcc2adbbbc7",
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


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
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


def integer_from(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise AssertionError(f"missing source-derived integer: {label}")
    return int(match.group(1))


def tail(a: int, b: int, distance: int, horizon: Fraction) -> Fraction:
    """The registered factorial tail E_d(a,b,T), with exact arithmetic."""
    ratio = Fraction(b) * horizon / (distance + 1)
    if not ratio < 1:
        raise AssertionError("factorial tail ratio is not below one")
    numerator = Fraction(a * (b ** (distance - 1)), 1)
    numerator *= horizon ** distance
    numerator /= math.factorial(distance)
    return numerator / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc013 = json.loads(
        (ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json")
        .read_text(encoding="utf-8")
    )
    r493_run = json.loads(
        (
            ROOT
            / "claims/C6-SPACETIME-SIGNATURE/runs/"
            "2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json"
        ).read_text(encoding="utf-8")
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

    check(rows, "unchanged PAH packet", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check(
        rows,
        "OMC-013 contract identity",
        omc013["contract_id"],
        "PAH-OMC-013",
        omc013["contract_id"] == "PAH-OMC-013",
    )
    scope = omc013["exact_scope"]
    grade_blind_text = scope["common_cylinder_algebra"].lower()
    grade_blind_ok = "cannot inspect the disjoint-union grade" in grade_blind_text
    check(rows, "grade-blind cylinder is frozen", grade_blind_ok, True, grade_blind_ok)
    check(rows, "OMC-013 generator identity is present",
          "L_(n+1) I_(n,n+1) f" in omc013["eventual_intertwining_proof"]["generator_sum_identity"],
          True, "L_(n+1) I_(n,n+1) f" in omc013["eventual_intertwining_proof"]["generator_sum_identity"])
    check(rows, "OMC-013 has observable-dependent stabilization",
          "N(f)" in omc013["root_support_contract"]["N_of_f"], True,
          "N(f)" in omc013["root_support_contract"]["N_of_f"])
    check(rows, "OMC-013 finite-only limit",
          "No infinite-volume" in scope["limit"], True, "No infinite-volume" in scope["limit"])
    check(rows, "R-493 integrated replay passed", r493_run["verification"], "PASS",
          r493_run["verification"] == "PASS")
    check(rows, "R-493 remains non-bearing", r493_run["active_gate_change"], False,
          r493_run["active_gate_change"] is False)
    check(rows, "R-493 stage-2 semigroup is open",
          r493_run["stage2_status"], "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
          r493_run["stage2_status"] == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP")
    check(rows, "R-510 state passage is local",
          "fixed prefix" in r510["conclusion"]["answer"], True,
          "fixed prefix" in r510["conclusion"]["answer"])
    check(rows, "R-510 Cauchy bound is explicit",
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True,
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    check(rows, "R-515 exact word transport is retained",
          "squared word mass" in r515["conclusion"]["transport"], True,
          "squared word mass" in r515["conclusion"]["transport"])
    check(rows, "R-515 simplex is factorial",
          "T^k/k!" in r515["conclusion"]["simplex"], True,
          "T^k/k!" in r515["conclusion"]["simplex"])
    check(rows, "R-515 does not claim anchored n",
          "No anchored-n" in r515["exact_scope"]["order"], True,
          "No anchored-n" in r515["exact_scope"]["order"])
    footprint = r516["conclusion"]["footprint"]
    roots_per_column = integer_from(r"(?:at most )?(\d+) PH/AP/LK roots", footprint, "roots per column")
    edge_slots = integer_from(r"at most (\d+) edge slots", footprint, "edge slots")
    radius = integer_from(r"radius at most (\d+) columns", footprint, "footprint radius")
    overlap = roots_per_column * (edge_slots * radius + 1)
    check(rows, "source-derived roots per column", roots_per_column, 16, roots_per_column == 16)
    check(rows, "source-derived edge slots", edge_slots, 4, edge_slots == 4)
    check(rows, "source-derived footprint radius", radius, 2, radius == 2)
    check(rows, "R-516 overlap formula", overlap, 144, overlap == 144)
    overlap_text = r516["conclusion"]["overlap"].replace(" ", "")
    check(rows, "R-516 records same overlap", "=144" in overlap_text, True,
          "=144" in overlap_text)
    check(rows, "R-517 exposes two-copy factor",
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""), True,
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""))
    effective_branching = 2 * overlap
    check(rows, "effective branching is derived", effective_branching, 288, effective_branching == 288)
    bound_text = r517["conclusion"]["bound"].replace(" ", "")
    check(rows, "R-517 tail condition is retained", "2bT<d+1" in bound_text, True,
          "2bT<d+1" in bound_text)
    check(rows, "R-517 attribution is conditional",
          r517["conditional"] and r517["claim_bearing"] is False, [True, False],
          r517["conditional"] and r517["claim_bearing"] is False)
    check(rows, "external Markov time retained",
          "external unaccelerated Markov time" in prereg["scope"]["time"], True,
          "external unaccelerated Markov time" in prereg["scope"]["time"])
    check(rows, "no physical promotion in prereg",
          any("physical Pre-A" in item for item in prereg["non_claims"]), True,
          any("physical Pre-A" in item for item in prereg["non_claims"]))
    check(rows, "R-490 coefficient is not an equality input",
          "domination-only" in omc013["exact_scope"]["gibbs_norm"], True,
          "domination-only" in omc013["exact_scope"]["gibbs_norm"])

    # A fixed non-radial cylinder and a finite word cutoff are labelled
    # inputs.  The source-derived constants above are not fitted values.
    support_width = 2
    support_max_column = support_width
    stabilization = max(2, support_max_column + 1)
    word_cutoff = 6
    horizon = Fraction(1, 4)
    norm_f = Fraction(5, 4)
    norm_g = Fraction(3, 2)
    state_D = Fraction(3, 2)
    state_q = Fraction(1, 2)
    state_stage = 2
    first_roots = roots_per_column * (support_width + 2 * radius + 1)
    check(rows, "support-width first-root envelope", first_roots, 112, first_roots == 112)
    check(rows, "word cutoff is finite before n", word_cutoff < 12, True, word_cutoff < 12)
    check(rows, "stabilization stage is source formula", stabilization, 3, stabilization == 3)
    check(rows, "state fixture has a contraction factor", 0 < state_q < 1, True, 0 < state_q < 1)
    check(rows, "state fixture lies after local stage", stabilization >= state_stage, True,
          stabilization >= state_stage)

    def state_error(level: int) -> Fraction:
        # R-510 gives 4 ||h|| D q^(n-s) for one local observable.  For a
        # product f*g use ||f||_infinity ||g||_infinity as the labelled norm.
        return 4 * norm_f * norm_g * state_D * state_q ** (level - state_stage)

    def pair_state_error(level: int) -> Fraction:
        return state_error(level) + state_error(level + 1)

    distances = [128, 192, 256]
    tails = [tail(first_roots, effective_branching, distance, horizon) for distance in distances]
    check(rows, "all tail ratios are below one",
          [effective_branching * horizon / (distance + 1) < 1 for distance in distances],
          [True] * len(distances),
          all(effective_branching * horizon / (distance + 1) < 1 for distance in distances))
    check(rows, "factorial tail strictly decreases",
          all(tails[index + 1] < tails[index] for index in range(len(tails) - 1)),
          True, all(tails[index + 1] < tails[index] for index in range(len(tails) - 1)))
    check(rows, "tail remains nonnegative", all(value >= 0 for value in tails), True,
          all(value >= 0 for value in tails))
    levels = [stabilization, stabilization + 2, stabilization + 4]
    pair_errors = [pair_state_error(level) for level in levels]
    check(rows, "R-510 pair state envelope decreases",
          all(pair_errors[index + 1] < pair_errors[index] for index in range(len(pair_errors) - 1)),
          True, all(pair_errors[index + 1] < pair_errors[index] for index in range(len(pair_errors) - 1)))
    correlation_envelopes = [
        pair_state_error(levels[index]) + 8 * norm_f * norm_g * tails[-1]
        for index in range(len(levels))
    ]
    check(rows, "scalar correlation envelope is positive",
          all(value > 0 for value in correlation_envelopes), True,
          all(value > 0 for value in correlation_envelopes))
    check(rows, "scalar envelope decreases in n at fixed boundary",
          all(correlation_envelopes[index + 1] < correlation_envelopes[index]
              for index in range(len(correlation_envelopes) - 1)),
          True, all(correlation_envelopes[index + 1] < correlation_envelopes[index]
                    for index in range(len(correlation_envelopes) - 1)))
    check(rows, "two-copy tail multiplier is explicit", 8 * norm_f * norm_g,
          Fraction(15), 8 * norm_f * norm_g == Fraction(15))
    check(rows, "word cutoff does not erase tail",
          word_cutoff > 0 and tails[-1] > 0, True, word_cutoff > 0 and tails[-1] > 0)
    check(rows, "finite truncation and n passage are ordered",
          ("First j" in r510["exact_scope"]["order"]
           and "then n" in r510["exact_scope"]["order"]), True,
          ("First j" in r510["exact_scope"]["order"]
           and "then n" in r510["exact_scope"]["order"]))
    check(rows, "common U_n remains open",
          any("common U_n" in item for item in r517["missing_assumptions"]), True,
          any("common U_n" in item for item in r517["missing_assumptions"]))
    check(rows, "minimal-form identification remains open",
          any("minimal" in item.lower() for item in r517["missing_assumptions"]), True,
          any("minimal" in item.lower() for item in r517["missing_assumptions"]))

    return {
        "schema": "tect/pah-omc020-projective-correlation-primary/1.0",
        "status": "PASS_PROJECTIVE_LOCAL_CORRELATION_ENVELOPE",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "checks": rows,
        "scope": {
            "observable": "One fixed grade-blind, gauge-invariant, non-radial local cylinder pair with support width two; the cylinder cannot inspect the grade.",
            "model": "Exactly PAH-001 with the OMC-013 graded extension and the unchanged PH/LK/AP finite-fibre generator after the registered j-limit.",
            "cutoff": "A finite jump-word cutoff m=6 is fixed before the n comparison; words crossing the prefix boundary are retained in the R-517 tail.",
            "order": "At fixed finite word cutoff and fixed compact external Markov horizon, use R-493 eventual intertwining, R-510 local-state passage for truncated terms, then the conditional R-517 boundary tail.",
            "normalization": "R-510 local Gibbs normalization and R-515 Gibbs square transport are used unchanged; R-490 C_sw=540 remains domination-only.",
            "volume": "Finite OMC-004 strips G_n with n at the stabilization stage and above; no infinite-volume or physical volume is assigned.",
            "time": "External stochastic Markov time on a compact fixture horizon T=1/4 only.",
        },
        "derived_inputs": {
            "roots_per_column": roots_per_column,
            "edge_slots": edge_slots,
            "footprint_radius": radius,
            "overlap_branching": overlap,
            "effective_branching": effective_branching,
            "support_width": support_width,
            "first_root_bound": first_roots,
            "word_cutoff": word_cutoff,
            "stabilization_stage": stabilization,
            "tail_distances": distances,
            "tail_values": [str(value) for value in tails],
            "state_levels": levels,
            "pair_state_values": [str(value) for value in pair_errors],
            "correlation_envelopes": [str(value) for value in correlation_envelopes],
        },
        "proof": {
            "truncated_terms": "For every word of length at most m=6, R-493 supplies exact grade-blind generator intertwining after the support-dependent stage N(f)=3. The finite word terms therefore use the same projected cylinder expression at n and n+1.",
            "state_passage": "R-510 supplies the local-state Cauchy modulus for the product observable f*g. The displayed pair envelope is the triangle sum of the R-510 errors at n and n+1.",
            "boundary_tail": "R-516 derives b=144 from the exact footprint, and R-517 supplies b_eff=2b=288. With the labelled finite horizon T=1/4 and the factorial tail E_d, the omitted boundary words are bounded conditionally by 8||f||_infinity||g||_infinity E_d.",
            "envelope": "At fixed boundary distance d=256, the scalar envelope is pair_state_error(n)+8||f||_infinity||g||_infinity E_d. It decreases in the n fixture while the boundary tail decreases as d grows.",
        },
        "assumptions": [
            "R-493's finite grade-blind eventual intertwining applies term-by-term to every word up to the fixed cutoff for the chosen cylinder.",
            "The R-510 local-state Cauchy estimate applies to the product cylinder f*g and its displayed analytic constants.",
            "The conditional R-517 finite-fibre word-to-Duhamel attribution applies with the exact R-516 footprint and two-copy factor.",
            "The finite word expansion can be split at the fixed cutoff before the n comparison; no infinite series equality is inferred from the truncated identity.",
        ],
        "missing_assumptions": [
            "A source-authorized common U_n or completed Hilbert-space realization for the varying n spaces.",
            "An arbitrary-sequence liminf/recovery theorem and identification with the R-512 minimal closed form.",
            "A full, non-conditional anchored-n semigroup convergence theorem.",
        ],
        "non_claims": [
            "This is a conditional auxiliary scalar envelope for one non-radial local cylinder, not the full PAH-OMC-020 objective.",
            "The finite word cutoff, arithmetic fixtures and R-517 tail do not prove a common U_n, weak Gibbs-L2 convergence, minimal-form semigroup selection or an infinite-volume process.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "next_single_question": "Can a source-authorized common U_n and minimal-form comparison identify the fixed-cutoff projective envelope with the anchored R-512 semigroup for all local cylinders?",
        "revisit_condition": "Reopen only when a source-authorized common-space packet, terminal-square-compatible map or exact comparison counterexample is supplied; do not repeat the finite radial or word fixtures.",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_projective_correlation.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 projective primary replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 PROJECTIVE PRIMARY: PASS ({len(payload['checks'])} checks; auxiliary conditional)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
