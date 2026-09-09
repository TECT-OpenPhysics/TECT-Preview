"""Independent replay for the PAH-OMC-020 path-space bridge contract.

This lane deliberately reconstructs the finite triangle and factorial-tail
arithmetic without importing the primary checker.  It does not assert a
common U_n, an infinite process, or R-512 semigroup selection.
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
    "2026-09-08-pah-omc020-pathspace-bridge/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
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


def write_json(path: Path, payload: dict) -> None:
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
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def factorial_tail(a: int, b: int, distance: int, horizon: Fraction) -> Fraction:
    # Reconstruct the registered envelope from its first term and geometric
    # ratio, independently of the primary implementation.
    first = Fraction(a, 1)
    for _ in range(distance - 1):
        first *= b
    first *= horizon ** distance
    first /= math.factorial(distance)
    ratio = Fraction(b * horizon, distance + 1)
    if ratio >= 1:
        raise AssertionError("unsafe independent factorial ratio")
    return first / (1 - ratio)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict] = []
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(rows, f"hash:{relative}", actual, expected, actual == expected)

    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    r510 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    r516 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json").read_text(encoding="utf-8"))
    r517 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json").read_text(encoding="utf-8"))
    r519 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json").read_text(encoding="utf-8"))

    comparison = prereg["objects_and_comparison"]
    check(rows, "contract id", prereg["contract_id"], "PAH-OMC-020", prereg["contract_id"] == "PAH-OMC-020")
    check(rows, "finite correlation target", "C_nj(f,g;t)" in comparison["finite_correlation"], True, "C_nj(f,g;t)" in comparison["finite_correlation"])
    check(rows, "minimal target name", "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"], True, "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"])
    check(rows, "isometry not assumed", "Not assumed strong operator convergence" in comparison["topology_boundary"], True, "Not assumed strong operator convergence" in comparison["topology_boundary"])
    order = prereg["scope"]["regulator_order"].lower()
    ordered_ok = "first j" in order and "anchored n" in order and "no diagonal" in order
    check(rows, "ordered limits", ordered_ok, True, ordered_ok)
    stochastic_time_ok = "external unaccelerated markov time" in prereg["scope"]["time"].lower()
    check(rows, "stochastic time only", stochastic_time_ok, True, stochastic_time_ok)
    check(rows, "physical non-claim", any("No physical Pre-A" in item for item in prereg["non_claims"]), True, any("No physical Pre-A" in item for item in prereg["non_claims"]))

    check(rows, "R-510 transfer identity", "nu_n(f)" in r510["conclusion"]["transfer_identity"], True, "nu_n(f)" in r510["conclusion"]["transfer_identity"])
    check(rows, "R-510 modulus", "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True, "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    check(rows, "R-512 closure", "minimal closed nonnegative extension" in r512["conclusion"], True, "minimal closed nonnegative extension" in r512["conclusion"])
    check(rows, "R-512 temporal gap", any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True, any("No finite-semigroup convergence" in item for item in r512["non_claims"]))
    check(rows, "R-516 overlap", "=144" in r516["conclusion"]["overlap"].replace(" ", ""), True, "=144" in r516["conclusion"]["overlap"].replace(" ", ""))
    check(rows, "R-517 conditional", r517["conditional"] is True and r517["claim_bearing"] is False, [True, False], r517["conditional"] is True and r517["claim_bearing"] is False)
    check(rows, "R-517 two-copy", "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""), True, "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""))
    check(rows, "R-519 auxiliary", r519["classification"] == "auxiliary_support" and r519["conditional"] is True, True, r519["classification"] == "auxiliary_support" and r519["conditional"] is True)

    # Independent fixture: change only test-oracle width/horizon, then derive
    # the source footprint constants again.
    roots = 16
    edge_slots = 4
    radius = 2
    width = 3
    overlap = roots * (edge_slots * radius + 1)
    effective = 2 * overlap
    first_roots = roots * (width + 2 * radius + 1)
    horizon = Fraction(1, 6)
    distances = [96, 144, 192]
    tails = [factorial_tail(first_roots, effective, d, horizon) for d in distances]
    check(rows, "independent root reconstruction", roots, 16, roots == 16)
    check(rows, "independent overlap reconstruction", overlap, 144, overlap == 144)
    check(rows, "independent effective branching", effective, 288, effective == 288)
    check(rows, "independent first-root fixture", first_roots, 128, first_roots == 128)
    check(rows, "independent ratios safe", all(Fraction(effective) * horizon < d + 1 for d in distances), True, all(Fraction(effective) * horizon < d + 1 for d in distances))
    check(rows, "independent tails decrease", all(left > right for left, right in zip(tails, tails[1:])), True, all(left > right for left, right in zip(tails, tails[1:])))
    check(rows, "independent tails positive", all(item > 0 for item in tails), True, all(item > 0 for item in tails))

    # Triangle fixture keeps an explicit target defect.  It is never set to
    # zero, because minimal-form/process identification is not in the source.
    norm_f = Fraction(7, 6)
    norm_g = Fraction(4, 3)
    state_D = Fraction(4, 3)
    state_q = Fraction(1, 3)
    stage = 2
    levels = [3, 5, 7]

    def state_error(level: int) -> Fraction:
        return 4 * norm_f * norm_g * state_D * state_q ** (level - stage)

    pair = [state_error(level) + state_error(level + 1) for level in levels]
    boundary = 8 * norm_f * norm_g * tails[-1]
    bridge = [value + boundary for value in pair]
    check(rows, "independent state errors decrease", all(left > right for left, right in zip(pair, pair[1:])), True, all(left > right for left, right in zip(pair, pair[1:])))
    check(rows, "independent bridge values positive", all(value > 0 for value in bridge), True, all(value > 0 for value in bridge))
    check(rows, "minimal target remains open", any("minimal" in item.lower() for item in r519["missing_assumptions"]), True, any("minimal" in item.lower() for item in r519["missing_assumptions"]))
    check(rows, "common U remains open", any("common U_n" in item for item in r519["missing_assumptions"]), True, any("common U_n" in item for item in r519["missing_assumptions"]))

    payload = {
        "schema": "tect/pah-omc020-pathspace-bridge-independent/1.0",
        "status": "PASS_INDEPENDENT_PATHSPACE_BRIDGE_CONTRACT",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "checks": rows,
        "fixture": {
            "width": width,
            "horizon": str(horizon),
            "distances": distances,
            "roots_per_column": roots,
            "overlap_branching": overlap,
            "effective_branching": effective,
            "first_root_bound": first_roots,
            "tail_values": [str(item) for item in tails],
            "state_levels": levels,
            "state_pair_values": [str(item) for item in pair],
            "bridge_values_without_target_defect": [str(item) for item in bridge],
        },
        "finding": "An independent projective path-space triangle is arithmetically consistent, but it still requires process existence/uniqueness, unconditional boundary escape and identification with the R-512 minimal form.",
        "non_claims": [
            "No common U_n or Hilbert isometry.",
            "No PAH-OMC-020 semigroup convergence, N2b/N2c/N2d theorem or infinite-volume process.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "next_single_question": "Can a source-grounded projective path-space process be constructed and uniquely identified with the R-512 minimal closed-form semigroup?",
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_independent.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 independent path-space replay mismatch")
    else:
        write_json(args.output, payload)
    print("PAH-OMC-020 PATHSPACE INDEPENDENT: PASS (conditional contract)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
