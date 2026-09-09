#!/usr/bin/env python3
"""Audit a non-coordinate common-space coupling candidate for PAH-OMC-020.

The candidate is a researcher-owned construction, not a source-authorized
owner packet and not a semigroup theorem.  It couples a finite prefix of the
R-510 state to the compatible limiting prefix by maximal overlap, extends the
two tails through regular conditional laws, and takes conditional expectation
as a contraction into the R-510 Hilbert space.  Only the finite coupling
algebra and the local-cylinder recovery estimate are checked here.  N2b,
N2c/N4, N2d and the temporal target remain explicitly open.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-noncoordinate-coupling/result.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md":
        "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json":
        "638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a",
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-n2b-common-space-audit/result.json":
        "034f5fc35a88a4431ee1594c8a25e0d7bcf6c75b055ec2b21bbf30daf636dc7f",
    "strategy/pa-hyp/PAH-OMC-020-boundary-kernel-obstruction-result-v1.json":
        "3497fb5b0e6ea99add8fd4b0f6cbef124eaadf1d33ec7cadc9b5c798a316748b",
}


def sha256(path: Path) -> str:
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


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def delta(d_value: Fraction, q_value: Fraction, n_value: int, m_value: int) -> Fraction:
    """R-510 bounded-measurable prefix modulus, capped at one."""
    raw = 4 * d_value * q_value ** (n_value - m_value)
    return min(Fraction(1), raw)


def stabilization_index(d_value: Fraction, q_value: Fraction, n_value: int) -> int:
    candidates = [
        m_value for m_value in range(n_value)
        if delta(d_value, q_value, n_value, m_value) <= Fraction(1, (m_value + 1) ** 2)
    ]
    if not candidates:
        raise AssertionError("diagonal coupling index set must be nonempty")
    return max(candidates)


def conditional_expectation(gamma: list[list[Fraction]], row_mass: list[Fraction], values: list[Fraction]) -> list[Fraction]:
    return [
        sum(gamma[row][col] * values[col] for col in range(len(values))) / row_mass[row]
        for row in range(len(row_mass))
    ]


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = sha256(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    contract = load("strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r510 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    intake = load("strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json")
    n2b = load(
        "claims/C6-SPACETIME-SIGNATURE/runs/"
        "2026-09-07-pah-omc020-n2b-common-space-audit/result.json"
    )
    r524 = load("strategy/pa-hyp/PAH-OMC-020-boundary-kernel-obstruction-result-v1.json")

    check(rows, "candidate identity", contract.get("contract_id"),
          "PAH-OMC-020-NONCOORDINATE-COUPLING-CANDIDATE",
          contract.get("contract_id") == "PAH-OMC-020-NONCOORDINATE-COUPLING-CANDIDATE")
    check(rows, "candidate is not source-authorized", contract["provenance"]["source_authorized_packet_present"], False,
          contract["provenance"]["source_authorized_packet_present"] is False)
    check(rows, "candidate model is unchanged", contract["provenance"]["model_change"], False,
          contract["provenance"]["model_change"] is False)
    check(rows, "candidate is non-coordinate", contract["map"]["kind"],
          "maximal-prefix-coupling-conditional-expectation",
          contract["map"]["kind"] == "maximal-prefix-coupling-conditional-expectation")
    check(rows, "PAH functional/rates remain frozen",
          "No functional, rate, state, carrier, regulator, counterterm or time change" in contract["fixed_scope"]["model_firewall"], True,
          "No functional, rate, state, carrier, regulator, counterterm or time change" in contract["fixed_scope"]["model_firewall"])
    check(rows, "R-510 modulus is the stated input", "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True,
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    check(rows, "R-510 bounded-measurable scope is retained",
          "bounded measurable" in r510["proof_coverage"]["normalization"].lower()
          or "bounded measurable" in " ".join(r510.get("assumptions", [])).lower()
          or "bounded measurable" in " ".join(contract["assumptions"]).lower(), True,
          "bounded-measurable prefix modulus is required")
    check(rows, "R-512 target remains minimal closure",
          "minimal" in json.dumps(r512["conclusion"]).lower(), True,
          "minimal closure")
    check(rows, "N2b parent remains hold", n2b["verdict"], "HOLD_FOR_EVIDENCE",
          n2b["verdict"] == "HOLD_FOR_EVIDENCE")
    check(rows, "R-524 remains route-local", r524["claim_bearing"], False,
          r524["claim_bearing"] is False)
    check(rows, "intake still says owner packet absent",
          intake["provenance"]["source_authorized_packet_present"], False,
          intake["provenance"]["source_authorized_packet_present"] is False)

    # Exact finite prefix fixture.  These are labelled test oracles, not PAH
    # parameters.  The coupling matrix has row law p_infty=(3/5,2/5) and
    # column law p_n=(1/2,1/2), with maximal diagonal overlap.
    p_infty = [Fraction(3, 5), Fraction(2, 5)]
    p_n = [Fraction(1, 2), Fraction(1, 2)]
    gamma = [[Fraction(1, 2), Fraction(1, 10)], [Fraction(0), Fraction(2, 5)]]
    row_sums = [sum(row) for row in gamma]
    column_sums = [sum(gamma[row][col] for row in range(2)) for col in range(2)]
    check(rows, "maximal coupling row law", row_sums, p_infty, row_sums == p_infty)
    check(rows, "maximal coupling column law", column_sums, p_n, column_sums == p_n)
    overlap = sum(min(p_infty[index], p_n[index]) for index in range(2))
    mismatch = 1 - overlap
    tv = sum(abs(p_infty[index] - p_n[index]) for index in range(2)) / 2
    check(rows, "overlap mass", overlap, Fraction(9, 10), overlap == Fraction(9, 10))
    check(rows, "mismatch equals total variation", mismatch, tv, mismatch == tv)
    check(rows, "mismatch fixture", mismatch, Fraction(1, 10), mismatch == Fraction(1, 10))

    # Jensen/conditional-expectation contraction on an exact rational grid.
    values = [Fraction(value, 2) for value in range(-4, 5)]
    contraction_cases = 0
    for left in values:
        for right in values:
            image = conditional_expectation(gamma, p_infty, [left, right])
            source_norm = sum(p_n[index] * [left, right][index] ** 2 for index in range(2))
            target_norm = sum(p_infty[index] * image[index] ** 2 for index in range(2))
            if target_norm > source_norm:
                raise AssertionError("conditional expectation contraction failed")
            contraction_cases += 1
    check(rows, "conditional-expectation contraction grid", contraction_cases, 81, contraction_cases == 81)

    f_values = [Fraction(1), Fraction(-1)]
    image_f = conditional_expectation(gamma, p_infty, f_values)
    recovery_sq = sum(
        p_infty[index] * (image_f[index] - f_values[index]) ** 2 for index in range(2)
    )
    bound_sq = 4 * max(abs(value) for value in f_values) ** 2 * mismatch
    check(rows, "local recovery image", image_f, [Fraction(2, 3), Fraction(-1)], image_f == [Fraction(2, 3), Fraction(-1)])
    check(rows, "local recovery squared error", recovery_sq, Fraction(1, 15), recovery_sq == Fraction(1, 15))
    check(rows, "local recovery coupling bound", recovery_sq <= bound_sq, True, recovery_sq <= bound_sq)

    # Diagonal threshold fixture for m_n.  D=1 and q=1/2 are labelled test
    # oracles; the packet's actual diagonal argument is symbolic in D_m and q.
    d_fixture = Fraction(1)
    q_fixture = Fraction(1, 2)
    levels = list(range(8, 41))
    indices = [stabilization_index(d_fixture, q_fixture, n_value) for n_value in levels]
    check(rows, "diagonal index set is nonempty", all(index >= 0 for index in indices), True,
          all(index >= 0 for index in indices))
    check(rows, "diagonal index is below n", all(index < n_value for index, n_value in zip(indices, levels)), True,
          all(index < n_value for index, n_value in zip(indices, levels)))
    check(rows, "diagonal index is eventually increasing", indices[-1] > indices[0], True,
          indices[-1] > indices[0])
    check(rows, "diagonal threshold is met", all(
        delta(d_fixture, q_fixture, n_value, index) <= Fraction(1, (index + 1) ** 2)
        for n_value, index in zip(levels, indices)
    ), True, all(
        delta(d_fixture, q_fixture, n_value, index) <= Fraction(1, (index + 1) ** 2)
        for n_value, index in zip(levels, indices)
    ))
    for fixed_m in range(5):
        threshold = next(
            n_value for n_value in range(fixed_m + 1, 80)
            if delta(d_fixture, q_fixture, n_value, fixed_m)
            <= Fraction(1, (fixed_m + 1) ** 2)
        )
        check(rows, f"fixed-prefix diagonal threshold m={fixed_m}",
              delta(d_fixture, q_fixture, threshold, fixed_m)
              <= Fraction(1, (fixed_m + 1) ** 2), True,
              delta(d_fixture, q_fixture, threshold, fixed_m)
              <= Fraction(1, (fixed_m + 1) ** 2))

    # The candidate deliberately stops before the hard analytic obligations.
    missing = contract["open_obligations"]
    for keyword in ("N2b", "N2c/N4", "N2d", "source authorization"):
        check(rows, f"open obligation retained: {keyword}", keyword.lower() in " ".join(missing).lower(), True,
              keyword.lower() in " ".join(missing).lower())
    check(rows, "physical firewall", any("physical Pre-A" in item for item in contract["non_claims"]), True,
          any("physical Pre-A" in item for item in contract["non_claims"]))
    check(rows, "temporal firewall", any("semigroup" in item.lower() for item in contract["non_claims"]), True,
          any("semigroup" in item.lower() for item in contract["non_claims"]))

    return {
        "schema": "tect/pah-omc020-noncoordinate-coupling-candidate/1.0",
        "status": "PASS_SCOPED_NONCOORDINATE_LOCAL_COUPLING",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "candidate_sha256": sha256(CONTRACT),
        "checks": rows,
        "finding": (
            "A non-coordinate maximal-prefix coupling gives a positive unital "
            "L2 contraction and an explicit local-cylinder recovery bound, "
            "conditional on the R-510 bounded-measurable prefix modulus and "
            "standard-Borel disintegration.  The candidate is not source-"
            "authorized and supplies no energy intertwining, N2b liminf, "
            "N2c/N4 boundary escape, N2d minimal identification or temporal "
            "semigroup convergence."
        ),
        "map_scope": contract["map"],
        "fixture": {
            "row_law": serial(p_infty),
            "column_law": serial(p_n),
            "coupling": serial(gamma),
            "total_variation": serial(tv),
            "mismatch": serial(mismatch),
            "diagonal_indices_n8_to_n40": indices,
        },
        "open_obligations": missing,
        "next_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_noncoordinate_coupling_candidate.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_noncoordinate_coupling_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_noncoordinate_coupling_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_noncoordinate_coupling_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 non-coordinate coupling replay mismatch")
    else:
        atomic_json(args.output, payload)
    print(
        "PAH-OMC-020 NONCOORDINATE COUPLING: "
        f"PASS {len(payload['checks'])}/{len(payload['checks'])}; "
        f"verdict={payload['verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
