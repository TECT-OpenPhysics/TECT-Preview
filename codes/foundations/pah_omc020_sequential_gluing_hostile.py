"""Hostile controls for the PAH-OMC-020 sequential gluing contract.

The controls deliberately remove one term of the budget, reverse the declared
limit order, or relabel a test oracle as source evidence.  Each mutation is
rejected.  None is a counterexample to PAH-001; they are safeguards against
invalid promotion of the conditional lemma.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-sequential-gluing/hostile.json"
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


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict] = []
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        check(rows, f"hash:{relative}", actual, expected, actual == expected)

    prereg = read("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r514 = read("strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json")
    r512 = read("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    r517 = read("strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json")
    r533 = read("strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json")
    order = prereg["scope"]["regulator_order"].lower()

    check(rows, "source order is not reversible", "first j" in order and "anchored n" in order, True, "first j" in order and "anchored n" in order)
    check(rows, "fixed-n result does not close anchored n", r514["verdict"], "PASS", r514["verdict"] == "PASS" and any("Anchored n" in str(item) for item in r514["missing_assumptions"]))
    check(rows, "R-517 tail cannot be made unconditional", r517["conditional"], True, r517["conditional"] is True)
    check(rows, "R-512 target gap is explicit", any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True, any("No finite-semigroup convergence" in item for item in r512["non_claims"]))
    check(rows, "R-533 owner gap remains", r533["verdict"], "HOLD_FOR_EVIDENCE", r533["verdict"] == "HOLD_FOR_EVIDENCE")

    # Mutation 1: dropping the known truncation term would falsely certify a
    # nonzero error.  The control detects the contradiction exactly.
    actual = Fraction(1, 2)
    j_term = Fraction(0)
    target_term = Fraction(0)
    dropped_budget = j_term + target_term
    check(rows, "dropping K is rejected", dropped_budget, Fraction(0), abs(actual) > dropped_budget)

    # Mutation 2: dropping D_n is equally unsound even with perfect finite-j
    # and boundary terms.
    actual_target = Fraction(1, 4)
    known_term = Fraction(0)
    finite_term = Fraction(0)
    check(rows, "dropping D is rejected", known_term + finite_term, Fraction(0), abs(actual_target) > known_term + finite_term)

    # Mutation 3: reversing the registered order changes the answer for the
    # exact indicator matrix J(n,j)=1_{j<n}; this is a generic order control.
    def j_indicator(n: int, j: int) -> int:
        return int(j < n)

    fixed_n_limit = [j_indicator(4, j) for j in (1, 4, 8)]
    reversed_limit = [j_indicator(n, 1) for n in (1, 4, 8)]
    check(rows, "fixed-n j limit can vanish", fixed_n_limit, [1, 0, 0], fixed_n_limit == [1, 0, 0])
    check(rows, "reversed n-first limit is different", reversed_limit, [0, 1, 1], reversed_limit == [0, 1, 1])

    # Mutation 4: the oracle witness is not allowed to alter the source
    # constants or be called a uniform theorem.
    check(rows, "finite result remains auxiliary", (r514["classification"], r514["claim_bearing"]), ("auxiliary_support", False), r514["classification"] == "auxiliary_support" and not r514["claim_bearing"])
    check(rows, "external time firewall", "external unaccelerated Markov time" in prereg["scope"]["time"], True, "external unaccelerated Markov time" in prereg["scope"]["time"])
    check(rows, "physical promotion is forbidden", any("No physical Pre-A" in item for item in prereg["non_claims"]), True, any("No physical Pre-A" in item for item in prereg["non_claims"]))

    payload = {
        "schema": "tect/pah-omc020-sequential-gluing-hostile/1.0",
        "audit_id": "PAH-OMC-020-SEQUENTIAL-GLUING",
        "task_id": "T-076",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "PASS_HOSTILE_CONTROLS",
        "assertions": rows,
        "assertion_count": len(rows),
        "source_hashes": {relative: digest(ROOT / relative) for relative in PINS},
        "rejected_mutations": [
            "drop the known K_(n,m) term",
            "drop the target D_n term",
            "reverse the j-before-n order",
            "promote test oracles or fixed-n evidence to a uniform/physical theorem",
        ],
        "scope_boundary": "Hostile promotion controls only; no PAH-specific counterexample and no physical conclusion.",
        "non_claims": [
            "These controls do not prove a PAH-OMC-020 anchored-n limit.",
            "No PAH-001 functional, rate, state, carrier, regulator, time or order change.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
    }
    atomic_json(args.output, payload)
    print(f"PAH-OMC-020 SEQUENTIAL GLUING HOSTILE: PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
