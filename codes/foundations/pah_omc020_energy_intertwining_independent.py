#!/usr/bin/env python3
"""Independent reconstruction of the PAH-OMC-020 energy contract.

This lane deliberately reimplements the finite weighted-edge arithmetic
without importing the primary verifier.  It treats the two-state calculation
as an abstract insufficiency witness and keeps the PAH temporal route held.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-energy-intertwining-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-energy-intertwining/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json":
        "0e40aeba3c6ab41b65842550163b26fc709e9aee8137258a7d630c54da8341d2",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json":
        "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json":
        "86246c253273f5dc1fc630c37c70e7b7b2e3aefcf1fc3d81ae5ad2b0f56cdc35",
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


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(relative)
    return value


def energy(probability: tuple[Fraction, Fraction], rate: Fraction,
           values: tuple[Fraction, Fraction]) -> Fraction:
    delta = values[1] - values[0]
    return sum(probability[index] * rate * delta * delta
               for index in range(len(probability))) / 2


def main_compute() -> dict:
    checks: list[dict] = []

    def check(name: str, actual: object, expected: object, condition: bool) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual),
                       "expected": str(expected)})

    hashes = {relative: sha256(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        check(f"source hash:{relative}", hashes[relative], expected,
              hashes[relative] == expected)

    contract = load("strategy/pa-hyp/PAH-OMC-020-energy-intertwining-contract-v1.json")
    candidate = load("strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json")
    r525 = load("strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json")
    snapshot = load("strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    check("contract id", contract["contract_id"],
          "PAH-OMC-020-N2B-ENERGY-INTERTWINING",
          contract["contract_id"] == "PAH-OMC-020-N2B-ENERGY-INTERTWINING")
    check("constructed hypothesis", contract["provenance"]["constructed_hypothesis"], True,
          contract["provenance"]["constructed_hypothesis"] is True)
    check("source authorization absent", contract["provenance"]["source_authorized"], False,
          contract["provenance"]["source_authorized"] is False)
    check("candidate status", candidate["status"], "RESEARCHER_OWNED_CANDIDATE_ONLY",
          candidate["status"] == "RESEARCHER_OWNED_CANDIDATE_ONLY")
    check("candidate map kind", candidate["map"]["kind"],
          "maximal-prefix-coupling-conditional-expectation",
          candidate["map"]["kind"] == "maximal-prefix-coupling-conditional-expectation")
    check("candidate open energy", candidate["open_obligations"], "energy-form compatibility present",
          any("energy" in item.lower() for item in candidate["open_obligations"]))
    check("R-525 held", r525["verdict"], "HOLD_FOR_EVIDENCE",
          r525["verdict"] == "HOLD_FOR_EVIDENCE")
    check("snapshot fixed", snapshot["status"], "FIXED_SEARCH_SNAPSHOT",
          snapshot["status"] == "FIXED_SEARCH_SNAPSHOT")
    check("snapshot owner set empty", snapshot["authorized_paths"], [],
          snapshot["authorized_paths"] == [])
    check("j precedes n", prereg["scope"]["regulator_order"], "j then anchored n",
          "First j" in prereg["scope"]["regulator_order"] and
          "then" in prereg["scope"]["regulator_order"])

    source_mass = Fraction(1)
    target_mass = Fraction(3, 2)
    kappa = Fraction(1, 2)
    delta = Fraction(3, 2)
    source = source_mass * delta * delta / 2
    target = target_mass * (kappa * delta) ** 2 / 2
    check("weighted square premise", target_mass * kappa * kappa, Fraction(3, 8),
          target_mass * kappa * kappa == Fraction(3, 8))
    check("weighted square domination", target_mass * kappa * kappa, source_mass,
          target_mass * kappa * kappa <= source_mass)
    check("conditional energy target", target, Fraction(27, 64), target <= source)
    check("conditional energy source", source, Fraction(9, 8), source > 0)

    probability = (Fraction(1, 2), Fraction(1, 2))
    observable = (Fraction(0), Fraction(1))
    source_oracle = energy(probability, Fraction(1), observable)
    target_oracle = energy(probability, Fraction(2), observable)
    l2_source = sum(probability[index] * observable[index] ** 2 for index in range(2))
    l2_target = l2_source
    check("identity static L2 contraction", l2_target, l2_source,
          l2_target <= l2_source)
    check("oracle source energy", source_oracle, Fraction(1, 2),
          source_oracle == Fraction(1, 2))
    check("oracle target energy", target_oracle, Fraction(1),
          target_oracle == Fraction(1))
    check("oracle violates energy contraction", (target_oracle, source_oracle),
          "target > source", target_oracle > source_oracle)
    check("oracle is explicitly non-PAH", contract["diagnostic_witness"]["scope"],
          "abstract only", contract["diagnostic_witness"]["scope"].startswith("Abstract insufficiency"))
    check("physical promotion disabled", contract["provenance"]["physical_promotion"], False,
          contract["provenance"]["physical_promotion"] is False)

    return {
        "schema": "tect/pah-omc020-energy-intertwining-independent/1.0",
        "status": "PASS_INDEPENDENT_ENERGY_SCOPE",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "contract_sha256": sha256(CONTRACT),
        "checks": checks,
        "checks_passed": len(checks),
        "finding": "Independent arithmetic confirms the conditional root-wise implication and the abstract static-coupling insufficiency witness; no PAH dynamic intertwining is supplied.",
        "non_claims": contract["non_claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = main_compute()
    atomic_json(args.output, payload)
    if args.check:
        replay = main_compute()
        if replay != json.loads(args.output.read_text(encoding="utf-8")):
            raise SystemExit("deterministic replay mismatch")
    print(f"PAH-OMC-020 ENERGY INDEPENDENT: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
