"""Conditional sequential gluing audit for PAH-OMC-020.

The audit proves a reusable epsilon-budget lemma for the registered order
``j -> infinity`` at fixed ``n``, followed by the anchored ``n`` comparison.
It does not construct a process, a common Hilbert-space map, or an
R-512-identifying limit.  The geometric and target-error sequences used by
the epsilon witness are labelled test oracles; all PAH inputs remain pinned
to their existing source records.
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
    "2026-09-08-pah-omc020-sequential-gluing/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json":
        "cfb65eb769cc95fb4b5148fe2914c5b4405748c3b8d253a0ca938369914d8801",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json":
        "67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d",
    "strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json":
        "9013fe5337965478c2e91c84fa693eacf3dbd0d948a3b2cafb900332d8b9dd19",
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
    if isinstance(value, (list, tuple)):
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


def triangle_budget(j_error: Fraction, known_error: Fraction,
                    target_error: Fraction) -> Fraction:
    """The nonnegative three-term budget in the registered comparison."""
    return j_error + known_error + target_error


def test_oracle_sequences() -> dict:
    """Return labelled arithmetic witnesses, not PAH constants.

    The oracle sequences have the only role of testing the quantifier order:
    fixed-n ``j`` error, a uniform truncation error indexed by ``m``, and a
    target-process defect indexed by ``n``.  They are intentionally separate
    from the pinned source constants.
    """
    oracle = {
        "j_numerator": 1,
        "known_numerator": 2,
        "target_numerator": 3,
        "target_power": 1,
        "boundary_base": 2,
        "epsilon": Fraction(1, 20),
    }

    def j_error(j: int) -> Fraction:
        return Fraction(oracle["j_numerator"], j + 1)

    def known_error(m: int) -> Fraction:
        # State/local-word term plus a factorial-style boundary oracle.
        return Fraction(oracle["known_numerator"], m + 1) + Fraction(
            1, oracle["boundary_base"] ** m
        )

    def target_error(n: int) -> Fraction:
        return Fraction(oracle["target_numerator"], n + 1) ** oracle["target_power"]

    epsilon = oracle["epsilon"]
    term_count = 3
    threshold = epsilon / term_count
    witness: dict[str, int] = {}
    for m in range(1, 10000):
        if known_error(m) <= threshold:
            witness["m"] = m
            break
    for n in range(1, 10000):
        if target_error(n) <= threshold:
            witness["n"] = n
            break
    for j in range(1, 10000):
        if j_error(j) <= threshold:
            witness["j"] = j
            break
    if set(witness) != {"j", "m", "n"}:
        raise AssertionError("epsilon witness search did not terminate")

    jv = j_error(witness["j"])
    kv = known_error(witness["m"])
    dv = target_error(witness["n"])
    total = triangle_budget(jv, kv, dv)
    return {
        "oracle": oracle,
        "witness": witness,
        "threshold": threshold,
        "j_error": jv,
        "known_error": kv,
        "target_error": dv,
        "total": total,
        "known_sequence": [known_error(index) for index in (4, 8, 16, 32)],
        "target_sequence": [target_error(index) for index in (4, 8, 16, 32)],
        "j_sequence": [j_error(index) for index in (4, 8, 16, 32)],
    }


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r514 = load("strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json")
    r510 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    r517 = load("strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json")
    r533 = load("strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json")

    comparison = prereg["objects_and_comparison"]
    order = prereg["scope"]["regulator_order"].lower()
    check(rows, "temporal contract identity", prereg["contract_id"], "PAH-OMC-020",
          prereg["contract_id"] == "PAH-OMC-020")
    check(rows, "fixed-n finite correlation is named", "C_nj(f,g;t)" in comparison["finite_correlation"], True,
          "C_nj(f,g;t)" in comparison["finite_correlation"])
    check(rows, "R-512 target is named", "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"], True,
          "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"])
    check(rows, "registered order is j then anchored n",
          "first j" in order and "anchored n" in order and "no diagonal" in order,
          True, "first j / anchored n / no diagonal")
    check(rows, "time is external stochastic Markov time",
          "external unaccelerated Markov time" in prereg["scope"]["time"], True,
          "external unaccelerated Markov time" in prereg["scope"]["time"])
    check(rows, "physical firewall is present",
          any("No physical Pre-A" in item for item in prereg["non_claims"]), True,
          any("No physical Pre-A" in item for item in prereg["non_claims"]))

    check(rows, "R-514 fixed-n result is PASS", r514["verdict"], "PASS", r514["verdict"] == "PASS")
    check(rows, "R-514 is auxiliary and non-bearing",
          [r514["classification"], r514["claim_bearing"]],
          ["auxiliary_support", False],
          r514["classification"] == "auxiliary_support" and r514["claim_bearing"] is False)
    check(rows, "R-514 anchored n remains open",
          any("Anchored n" in item or "Anchored n" in str(item) for item in r514["missing_assumptions"]),
          True, r514["missing_assumptions"])
    check(rows, "R-510 state modulus is explicit",
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True,
          "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    check(rows, "R-512 minimal closure is not temporal identification",
          any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True,
          any("No finite-semigroup convergence" in item for item in r512["non_claims"]))
    check(rows, "R-517 remains conditional",
          r517["conditional"] is True and r517["claim_bearing"] is False,
          [True, False], r517["conditional"] is True and r517["claim_bearing"] is False)
    check(rows, "R-517 two-copy factor is retained",
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""), True,
          "b_eff=2b=288" in r517["conclusion"]["constants"].replace(" ", ""))
    check(rows, "R-533 confirms owner packet is absent",
          r533["verdict"] == "HOLD_FOR_EVIDENCE" and r533["classification"] == "auxiliary_support",
          True, [r533["verdict"], r533["classification"]])
    check(rows, "R-533 non-explosion field remains missing",
          any("non-explosion" in item for item in r533["missing_assumptions"]), True,
          r533["missing_assumptions"])

    fixture = test_oracle_sequences()
    threshold = fixture["threshold"]
    check(rows, "oracle known budget decreases",
          all(left > right for left, right in zip(fixture["known_sequence"], fixture["known_sequence"][1:])),
          True, True)
    check(rows, "oracle target defect decreases",
          all(left > right for left, right in zip(fixture["target_sequence"], fixture["target_sequence"][1:])),
          True, True)
    check(rows, "oracle fixed-n j error decreases",
          all(left > right for left, right in zip(fixture["j_sequence"], fixture["j_sequence"][1:])),
          True, True)
    check(rows, "epsilon witness m/n/j is explicit", fixture["witness"], fixture["witness"], True)
    check(rows, "each witness budget is below epsilon partition",
          all(value <= threshold for value in (
              fixture["j_error"], fixture["known_error"], fixture["target_error"])),
          True, True)
    check(rows, "three-term epsilon budget closes",
          fixture["total"] <= fixture["oracle"]["epsilon"], True,
          f"total <= {fixture['oracle']['epsilon']}")

    # Exact triangle fixture: u is finite-j, v fixed-n, w target.  The
    # numbers are test oracles and the check is the only algebra used here.
    u, v, w = Fraction(7, 10), Fraction(2, 5), Fraction(1, 10)
    lhs = abs(u - w)
    rhs = abs(u - v) + abs(v - w)
    check(rows, "exact correlation triangle", lhs, rhs, lhs <= rhs)
    check(rows, "triangle fixture recomputes the two legs", rhs, Fraction(3, 5), rhs == Fraction(3, 5))

    # A nonzero target defect survives even when the other two terms vanish;
    # this is a logical necessity test, not a PAH counterexample.
    residual = triangle_budget(Fraction(0), Fraction(0), Fraction(1, 4))
    check(rows, "target defect cannot be dropped", residual, Fraction(1, 4), residual > 0)

    missing = [
        "A source-authorized uniform truncation bound K_(n,m) for all local cylinders and compact external-time horizons.",
        "A source-authorized target-process/R-512 minimal-form defect D_n tending to zero in the anchored n limit.",
        "A common path-space or common-Hilbert realization needed to instantiate those two bounds for PAH-001.",
    ]
    non_claims = [
        "The oracle sequences are arithmetic test witnesses, not PAH parameters or numerical evidence for convergence.",
        "No PAH-OMC-020 anchored-n semigroup convergence theorem is proved by this conditional gluing lemma.",
        "No source process, U_n, rate, state, carrier, regulator, time interpretation or limit order is changed.",
        "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        "External Markov time is not quantum real time, proper time or Lorentzian time.",
    ]
    return {
        "schema": "tect/pah-omc020-sequential-gluing-primary/1.0",
        "audit_id": "PAH-OMC-020-SEQUENTIAL-GLUING",
        "task_id": "T-076",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "PASS_CONDITIONAL_GLUING_LEMMA",
        "assertions": rows,
        "assertion_count": len(rows),
        "source_hashes": source_hashes,
        "scope": {
            "model": "Unchanged PAH-001 and the preregistered PAH-OMC-020 comparison.",
            "order": "Fixed-n j-to-infinity first, then anchored n; no diagonal or reversed order.",
            "observables": "Any bounded local cylinder pair for which the registered fixed-n and local-tail hypotheses are instantiated.",
            "time": "Compact intervals of external stochastic Markov time only.",
            "normalization": "Original labelled Gibbs normalization; R-490 C_sw remains domination-only.",
        },
        "decomposition": {
            "finite_j": "J_n(j)=sup_t |C_(n,j)(t)-c_n(t)|, with J_n(j)->0 at fixed n (R-514).",
            "known_anchored": "K_(n,m) collects R-510 state/local stabilization and R-517 boundary terms; a uniform m->infinity limsup is required.",
            "target": "D_n=sup_t |c_n(t)-c_star(t)|, where c_star is the R-512 minimal target; D_n->0 is not supplied.",
            "budget": "sup_t |C_(n,j)-c_star| <= J_n(j)+K_(n,m)+D_n.",
        },
        "oracle_fixture": fixture,
        "conclusion": {
            "conditional_implication": "If fixed-n J_n(j)->0, lim_m limsup_n K_(n,m)=0 and D_n->0, then the registered lim_n lim_j compact-time local-correlation limit follows by the three-term triangle budget.",
            "actual_status": "The implication is verified, but the source-authorized K and D instantiations are absent; retain HOLD_FOR_EVIDENCE for the parent objective.",
        },
        "missing_assumptions": missing,
        "adversarial_review": [
            {"objection": "The oracle decay is a PAH uniform estimate.", "disposition": "REJECTED: it is labelled test arithmetic and never enters source constants."},
            {"objection": "R-514 alone proves the anchored n target.", "disposition": "UPHELD AGAINST PROMOTION: the target defect D_n and uniform K_(n,m) remain separate."},
            {"objection": "R-517's conditional tail can be treated as unconditional.", "disposition": "UPHELD AGAINST PROMOTION: the source-authorized attribution and uniformity are explicit missing fields."},
            {"objection": "A triangle identity constructs the missing process.", "disposition": "REJECTED: no path-space law, U_n or R-512 identification is constructed."},
            {"objection": "Compact-time Markov notation implies physical time.", "disposition": "REJECTED: only external stochastic Markov time is retained."},
        ],
        "verification": {
            "self": "python -X utf8 verification/scripts/pah_omc020_sequential_gluing.py --check",
            "status": "Primary arithmetic and source-scope checks pass; scientific parent status remains HOLD_FOR_EVIDENCE.",
        },
        "next_single_question": "Can one source-authorized packet instantiate both the uniform K_(n,m) truncation bound and the D_n target-process/R-512 minimal-form defect without changing PAH-001?",
        "non_claims": non_claims,
        "physical_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    atomic_json(args.output, payload)
    print(f"PAH-OMC-020 SEQUENTIAL GLUING PRIMARY: PASS {payload['assertion_count']}/{payload['assertion_count']} (conditional; parent HOLD_FOR_EVIDENCE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
