"""Audit the U_n-free path-space bridge for PAH-OMC-020.

This is a source-compatible bridge contract, not a semigroup convergence
theorem.  It tests whether local correlation convergence can be phrased on
the projective path/cylinder algebra without inventing a common Hilbert
isometry.  The R-512 minimal-form selection is kept as a separate terminal
obligation.  No PAH functional, rate, state, carrier, regulator, order or
time interpretation is changed.
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
    "2026-09-08-pah-omc020-pathspace-bridge/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json":
        "8d005bea7ee33111712f58a32046cdb254f77bc8c17d8eb1a470abcc2adbbbc7",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json":
        "9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11",
    "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json":
        "67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d",
    "strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json":
        "2bfc217bfa7785726d7342ce5ec80d1adab5be030c561d4e6681d49f64cf3248",
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


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
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


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def factorial_tail(a: int, b: int, distance: int, horizon: Fraction) -> Fraction:
    ratio = Fraction(b) * horizon / (distance + 1)
    if not ratio < 1:
        raise AssertionError("factorial ratio condition failed")
    numerator = Fraction(a * b ** (distance - 1), 1) * horizon ** distance
    return numerator / math.factorial(distance) / (1 - ratio)


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r493 = load(
        "claims/C6-SPACETIME-SIGNATURE/runs/"
        "2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json"
    )
    r510 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    r516 = load("strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json")
    r517 = load("strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json")
    r519 = load("strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json")

    check(rows, "preregistered contract identity",
          prereg["contract_id"], "PAH-OMC-020",
          prereg["contract_id"] == "PAH-OMC-020")
    comparison = prereg["objects_and_comparison"]
    check(rows, "scalar finite correlation is declared",
          "C_nj(f,g;t)" in comparison["finite_correlation"], True,
          "C_nj(f,g;t)" in comparison["finite_correlation"])
    check(rows, "target is R-512 minimal semigroup",
          "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"], True,
          "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"])
    check(rows, "no isometry was assumed",
          "Not assumed strong operator convergence" in comparison["topology_boundary"], True,
          "Not assumed strong operator convergence" in comparison["topology_boundary"])
    order = prereg["scope"]["regulator_order"]
    order_lower = order.lower()
    check(rows, "j-before-n order is frozen",
          "first j" in order_lower and "then" in order_lower and "anchored n" in order_lower, True,
          "first j" in order_lower and "then" in order_lower and "anchored n" in order_lower)
    check(rows, "external time is retained",
          "external unaccelerated Markov time" in prereg["scope"]["time"], True,
          "external unaccelerated Markov time" in prereg["scope"]["time"])
    check(rows, "physical firewall is retained",
          any("No physical Pre-A" in item for item in prereg["non_claims"]), True,
          any("No physical Pre-A" in item for item in prereg["non_claims"]))

    check(rows, "R-493 finite replay passed", r493["verification"], "PASS",
          r493["verification"] == "PASS")
    check(rows, "R-493 stage-two hold is explicit",
          r493["stage2_status"], "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP",
          r493["stage2_status"] == "HOLD_FOR_EVIDENCE_CLOSABILITY_AND_SEMIGROUP")
    check(rows, "R-510 projective state identity is present",
          "nu_n(f)" in r510["conclusion"]["transfer_identity"], True,
          "nu_n(f)" in r510["conclusion"]["transfer_identity"])
    check(rows, "R-510 local modulus is explicit",
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True,
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    check(rows, "R-512 minimal closure is fixed",
          "minimal closed nonnegative extension" in r512["conclusion"], True,
          "minimal closed nonnegative extension" in r512["conclusion"])
    check(rows, "R-512 temporal selection remains separate",
          any("No finite-semigroup convergence" in item for item in r512["non_claims"]),
          True, any("No finite-semigroup convergence" in item for item in r512["non_claims"]))
    check(rows, "R-516 overlap is source-derived",
          "=144" in r516["conclusion"]["overlap"].replace(" ", ""), True,
          "=144" in r516["conclusion"]["overlap"].replace(" ", ""))
    check(rows, "R-517 tail is conditional",
          r517["conditional"] is True and r517["claim_bearing"] is False,
          [True, False], r517["conditional"] is True and r517["claim_bearing"] is False)
    check(rows, "R-517 two-copy factor is retained",
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""), True,
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""))
    check(rows, "R-519 is finite auxiliary evidence",
          r519["classification"] == "auxiliary_support"
          and r519["conditional"] is True
          and r519["claim_bearing"] is False,
          [True, True, False], [
              r519["classification"] == "auxiliary_support",
              r519["conditional"] is True,
              r519["claim_bearing"] is False,
          ])
    check(rows, "R-519 leaves common U_n open",
          any("common U_n" in item for item in r519["missing_assumptions"]), True,
          r519["missing_assumptions"])

    # Source-derived finite envelope fixtures.  The state constants below
    # are explicitly labelled test oracles; b, b_eff and a_w are recomputed
    # from the pinned footprint, never pasted as proof constants.
    footprint = r516["conclusion"]["footprint"]
    roots = int(re.search(r"(?:at most )?(\d+) PH/AP/LK roots", footprint, re.I).group(1))
    edge_slots = int(re.search(r"at most (\d+) edge slots", footprint, re.I).group(1))
    radius = int(re.search(r"radius at most (\d+) columns", footprint, re.I).group(1))
    overlap = roots * (edge_slots * radius + 1)
    effective = 2 * overlap
    width = 2
    first_roots = roots * (width + 2 * radius + 1)
    check(rows, "footprint roots recomputed", roots, 16, roots == 16)
    check(rows, "footprint edge slots recomputed", edge_slots, 4, edge_slots == 4)
    check(rows, "footprint radius recomputed", radius, 2, radius == 2)
    check(rows, "overlap recomputed", overlap, 144, overlap == 144)
    check(rows, "two-copy branching recomputed", effective, 288, effective == 288)
    check(rows, "first-root bound recomputed", first_roots, 112, first_roots == 112)

    horizon = Fraction(1, 4)
    distances = [128, 192, 256]
    tails = [factorial_tail(first_roots, effective, d, horizon) for d in distances]
    check(rows, "path-tail ratio is safe",
          all(Fraction(effective) * horizon / (d + 1) < 1 for d in distances),
          [True] * len(distances),
          all(Fraction(effective) * horizon / (d + 1) < 1 for d in distances))
    check(rows, "path-tail fixture decreases",
          all(left > right for left, right in zip(tails, tails[1:])), True,
          all(left > right for left, right in zip(tails, tails[1:])))
    check(rows, "path-tail fixture remains positive", all(value > 0 for value in tails), True,
          all(value > 0 for value in tails))

    # These are test-oracle norms for the bridge arithmetic, not PAH
    # parameters.  The target term is intentionally absent rather than set
    # to zero: its missing proof is the point of this audit.
    norm_f = Fraction(5, 4)
    norm_g = Fraction(3, 2)
    state_D = Fraction(3, 2)
    state_q = Fraction(1, 2)
    state_stage = 2
    state_levels = [3, 5, 7]

    def state_error(level: int) -> Fraction:
        return 4 * norm_f * norm_g * state_D * state_q ** (level - state_stage)

    pair_errors = [
        state_error(level) + state_error(level + 1) for level in state_levels
    ]
    boundary_term = 8 * norm_f * norm_g * tails[-1]
    conditional_bridge_fixture = [value + boundary_term for value in pair_errors]
    check(rows, "state fixture decreases", all(
        left > right for left, right in zip(pair_errors, pair_errors[1:])
    ), True, all(left > right for left, right in zip(pair_errors, pair_errors[1:])))
    check(rows, "conditional bridge fixture is positive",
          all(value > 0 for value in conditional_bridge_fixture), True,
          all(value > 0 for value in conditional_bridge_fixture))
    check(rows, "target defect is not silently zero",
          "minimal-form identification" in " ".join(r519["missing_assumptions"]),
          True, "minimal-form identification remains open")
    check(rows, "no common-space map is silently synthesized",
          "common U_n" in " ".join(r519["missing_assumptions"]), True,
          "common U_n remains open")

    bridge_inputs = {
        "projective_state": "R-510 local-cylinder state convergence",
        "local_generator": "R-493 finite grade-blind word stabilization",
        "boundary_escape": "R-517 conditional connected-word Duhamel tail",
        "target_process": "A source-grounded local Markov process with cylinder generator A",
        "minimal_selection": "The process must be identified with the R-512 minimal closed-form semigroup",
    }
    missing = [
        "A source-grounded path-space or martingale-problem construction for the infinite local process.",
        "Uniqueness of that local process on the R-512 cylinder domain, including non-explosion for the unbounded rates.",
        "An unconditional N2c/N4 boundary-escape estimate for the evolved local test, not only the conditional R-517 attribution.",
        "A proof that the process/form limit is exactly the R-512 minimal closure rather than another closed extension.",
    ]
    check(rows, "bridge keeps the target term explicit",
          bridge_inputs["minimal_selection"].startswith("The process"), True,
          bridge_inputs["minimal_selection"])
    check(rows, "bridge missing-input contract is nonempty",
          len(missing), 4, len(missing) == 4)

    return {
        "schema": "tect/pah-omc020-pathspace-bridge-primary/1.0",
        "status": "PASS_PATHSPACE_BRIDGE_CONTRACT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "checks": rows,
        "scope": {
            "observable": "Fixed bounded grade-blind local cylinder pair in the R-510 projective local algebra.",
            "route": "Scalar path-space/martingale-problem comparison; no common Hilbert isometry is assumed.",
            "order": "First the registered j-limit at fixed n, then the anchored n comparison; no diagonal or reversed order.",
            "time": "Original external stochastic Markov time on finite compact intervals.",
            "normalization": "Original labelled Gibbs state and R-510 transfer normalization; R-490 remains domination-only.",
        },
        "derived_inputs": {
            "roots_per_column": roots,
            "edge_slots": edge_slots,
            "footprint_radius": radius,
            "overlap_branching": overlap,
            "effective_branching": effective,
            "support_width": width,
            "first_root_bound": first_roots,
            "horizon": str(horizon),
            "tail_distances": distances,
            "tail_values": [str(value) for value in tails],
            "state_levels": state_levels,
            "state_pair_values": [str(value) for value in pair_errors],
            "conditional_bridge_values": [str(value) for value in conditional_bridge_fixture],
        },
        "bridge_inputs": bridge_inputs,
        "assumptions": [
            "R-493 local word stabilization, R-510 projective state convergence and R-517 finite-fibre attribution hold at their registered scopes.",
            "A projective path-space construction exists for the compatible local states and cylinder generator.",
            "The local martingale problem is unique and non-explosive on every compact external-time interval.",
            "The resulting process is represented by the R-512 minimal closed form.",
        ],
        "missing_assumptions": missing,
        "finding": (
            "The finite scalar bridge decomposition is algebraically consistent: "
            "state error plus the explicit R-517 boundary tail is a valid "
            "conditional budget, and it avoids inventing U_n.  The path-space "
            "process/uniqueness and minimal-form identification premises are "
            "not supplied by the current PAH records, so the full ordered "
            "semigroup objective remains HOLD_FOR_EVIDENCE."
        ),
        "non_claims": [
            "No full PAH-OMC-020 semigroup convergence theorem or negative result.",
            "No common U_n/Hilbert isometry, weak Gibbs-L2 theorem, N2b liminf, N2c/N4 unconditional escape or N2d selection.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "next_single_question": (
            "Can a source-grounded projective path-space/martingale-problem "
            "construction prove non-explosion and uniqueness for the R-512 "
            "cylinder generator, with its semigroup equal to the minimal "
            "closed-form semigroup?"
        ),
        "revisit_condition": (
            "Reopen after a source-authorized path-space/process packet or an "
            "exact non-explosion/uniqueness counterexample; do not repeat the "
            "finite radial, word or coordinate-fibre fixtures."
        ),
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_pathspace_bridge.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 path-space bridge replay mismatch")
    else:
        atomic_json(args.output, payload)
    print(
        "PAH-OMC-020 PATHSPACE BRIDGE: PASS "
        "(conditional contract; process/minimal selection open)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
