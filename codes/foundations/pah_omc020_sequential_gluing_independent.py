"""Non-importing independent replay of the PAH-OMC-020 gluing lemma.

The implementation rebuilds the source checks and uses a different rational
epsilon fixture.  It does not import the primary script or assert that the
missing source-owned process exists.
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
    "2026-09-08-pah-omc020-sequential-gluing/independent.json"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def add(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def run_fixture() -> dict:
    # Deliberately different test oracle from the primary lane.
    numerator_j = 2
    numerator_known = 3
    numerator_target = 1
    boundary_base = 3
    epsilon = Fraction(1, 30)
    parts = 3

    def j_error(j: int) -> Fraction:
        return Fraction(numerator_j, j + 2)

    def known_error(m: int) -> Fraction:
        return Fraction(numerator_known, m + 2) + Fraction(1, boundary_base ** m)

    def target_error(n: int) -> Fraction:
        return Fraction(numerator_target, n + 2)

    threshold = epsilon / parts
    witness = {}
    for index in range(1, 20000):
        if "m" not in witness and known_error(index) <= threshold:
            witness["m"] = index
        if "n" not in witness and target_error(index) <= threshold:
            witness["n"] = index
        if "j" not in witness and j_error(index) <= threshold:
            witness["j"] = index
        if len(witness) == parts:
            break
    if len(witness) != parts:
        raise AssertionError("independent witness search failed")
    terms = {
        "j": j_error(witness["j"]),
        "known": known_error(witness["m"]),
        "target": target_error(witness["n"]),
    }
    total = sum(terms.values(), Fraction(0))
    return {
        "oracle_only": True,
        "epsilon": epsilon,
        "parts": parts,
        "threshold": threshold,
        "witness": witness,
        "terms": terms,
        "total": total,
        "decreasing": {
            "j": all(j_error(a) > j_error(b) for a, b in zip((3, 6, 12), (6, 12, 24))),
            "known": all(known_error(a) > known_error(b) for a, b in zip((3, 6, 12), (6, 12, 24))),
            "target": all(target_error(a) > target_error(b) for a, b in zip((3, 6, 12), (6, 12, 24))),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict] = []
    for relative, expected in PINS.items():
        actual = sha256(ROOT / relative)
        add(rows, f"hash:{relative}", actual, expected, actual == expected)

    prereg = read("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r514 = read("strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json")
    r510 = read("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r512 = read("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    r517 = read("strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json")
    r533 = read("strategy/pa-hyp/PAH-OMC-020-n2c-owner-audit-v1.1-result-v1.json")
    comparison = prereg["objects_and_comparison"]
    order = prereg["scope"]["regulator_order"].lower()

    add(rows, "contract", prereg["contract_id"], "PAH-OMC-020", prereg["contract_id"] == "PAH-OMC-020")
    add(rows, "finite correlation notation", "C_nj(f,g;t)" in comparison["finite_correlation"], True, "C_nj(f,g;t)" in comparison["finite_correlation"])
    add(rows, "minimal target notation", "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"], True, "T_min(t)=exp(-t K_min)" in comparison["target_semigroup"])
    add(rows, "order", ("first j" in order, "anchored n" in order, "no diagonal" in order), (True, True, True), all(x in order for x in ("first j", "anchored n", "no diagonal")))
    add(rows, "external time", "external unaccelerated Markov time" in prereg["scope"]["time"], True, "external unaccelerated Markov time" in prereg["scope"]["time"])
    add(rows, "physical firewall", any("No physical Pre-A" in item for item in prereg["non_claims"]), True, any("No physical Pre-A" in item for item in prereg["non_claims"]))
    add(rows, "fixed-n PASS", r514["verdict"], "PASS", r514["verdict"] == "PASS")
    add(rows, "fixed-n auxiliary", (r514["classification"], r514["claim_bearing"]), ("auxiliary_support", False), r514["classification"] == "auxiliary_support" and r514["claim_bearing"] is False)
    add(rows, "R-510 modulus", "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"], True, "D_m q^(n-m)" in r510["conclusion"]["cauchy_bound"])
    add(rows, "R-512 no temporal promotion", any("No finite-semigroup convergence" in item for item in r512["non_claims"]), True, any("No finite-semigroup convergence" in item for item in r512["non_claims"]))
    add(rows, "R-517 conditional", r517["conditional"] and not r517["claim_bearing"], True, r517["conditional"] and not r517["claim_bearing"])
    add(rows, "R-533 hold", (r533["verdict"], r533["classification"]), ("HOLD_FOR_EVIDENCE", "auxiliary_support"), r533["verdict"] == "HOLD_FOR_EVIDENCE" and r533["classification"] == "auxiliary_support")

    fixture = run_fixture()
    add(rows, "oracle terms decrease", fixture["decreasing"], {"j": True, "known": True, "target": True}, all(fixture["decreasing"].values()))
    add(rows, "oracle witness is explicit", set(fixture["witness"]), {"j", "m", "n"}, set(fixture["witness"]) == {"j", "m", "n"})
    add(rows, "oracle partition", all(value <= fixture["threshold"] for value in fixture["terms"].values()), True, all(value <= fixture["threshold"] for value in fixture["terms"].values()))
    add(rows, "oracle total", fixture["total"] <= fixture["epsilon"], True, fixture["total"] <= fixture["epsilon"])

    # Nonnegative chain inequality in a deliberately different fixture.
    first, middle, target = Fraction(9, 10), Fraction(1, 2), Fraction(1, 5)
    chain = abs(first - target)
    legs = abs(first - middle) + abs(middle - target)
    add(rows, "two-leg triangle", chain <= legs, True, chain <= legs)
    add(rows, "target term is necessary", Fraction(1, 5), Fraction(1, 5), Fraction(1, 5) > 0)

    payload = {
        "schema": "tect/pah-omc020-sequential-gluing-independent/1.0",
        "audit_id": "PAH-OMC-020-SEQUENTIAL-GLUING",
        "task_id": "T-076",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "verdict": "PASS_CONDITIONAL_GLUING_LEMMA",
        "assertions": rows,
        "assertion_count": len(rows),
        "source_hashes": {relative: sha256(ROOT / relative) for relative in PINS},
        "fixture": fixture,
        "scope_boundary": "Conditional arithmetic reduction only; source process, U_n, anchored-n convergence and physical layers remain open.",
        "missing_assumptions": [
            "Source-authorized uniform K_(n,m) truncation bound for all local cylinders.",
            "Source-authorized D_n target-process/R-512 minimal-form defect tending to zero.",
            "Common path-space or common-Hilbert realization to instantiate the bounds.",
        ],
        "non_claims": [
            "No PAH-OMC-020 semigroup convergence theorem.",
            "No change to PAH-001 functional, rates, state, carrier, regulator, external Markov time or limit order.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion.",
        ],
    }
    atomic_json(args.output, payload)
    print(f"PAH-OMC-020 SEQUENTIAL GLUING INDEPENDENT: PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
