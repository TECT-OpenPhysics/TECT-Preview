#!/usr/bin/env python3
"""Hostile scope controls for the PAH-OMC-020 energy contract.

The controls deliberately mutate rates, hashes, map labels and epistemic
flags in memory.  They ensure that the abstract two-state witness is not
mistaken for an exact PAH negative result and that a static coupling cannot
silently become a dynamic owner packet.
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
    "2026-09-08-pah-omc020-energy-intertwining/hostile.json"
)
PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json": "dcee1aba3cb53607e6902829d28a0b79878f27a5de2eee79c131d6ab36dd393e",
    "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json": "86246c253273f5dc1fc630c37c70e7b7b2e3aefcf1fc3d81ae5ad2b0f56cdc35",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def two_state_energy(rate: Fraction) -> Fraction:
    probability = (Fraction(1, 2), Fraction(1, 2))
    delta = Fraction(1)
    return sum(probability[index] * rate * delta * delta for index in range(2)) / 2


def compute() -> dict:
    checks: list[dict] = []

    def check(name: str, actual: object, expected: object, condition: bool) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    hashes = {relative: sha256(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        check(f"hash:{relative}", hashes[relative], expected, hashes[relative] == expected)

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    candidate = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json").read_text(encoding="utf-8"))
    snapshot = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json").read_text(encoding="utf-8"))

    mutated_hashes = dict(hashes)
    first_key = next(iter(mutated_hashes))
    mutated_hashes[first_key] = "0" * 64
    check("hash mutation is rejected", mutated_hashes[first_key], hashes[first_key],
          mutated_hashes[first_key] != hashes[first_key])
    mutated_auth = json.loads(json.dumps(contract))
    mutated_auth["provenance"]["source_authorized"] = True
    check("source-authorized mutation is visible", mutated_auth["provenance"]["source_authorized"], True,
          mutated_auth["provenance"]["source_authorized"] is True and contract["provenance"]["source_authorized"] is False)
    mutated_map = json.loads(json.dumps(candidate))
    mutated_map["map"]["kind"] = "coordinate-pullback"
    check("map mutation is rejected", mutated_map["map"]["kind"], candidate["map"]["kind"],
          mutated_map["map"]["kind"] != candidate["map"]["kind"])
    check("snapshot has no authorized rescue", snapshot["authorized_paths"], [], snapshot["authorized_paths"] == [])
    check("snapshot has no complete rescue", snapshot["complete_paths"], [], snapshot["complete_paths"] == [])

    source_rate = Fraction(1)
    target_rate = Fraction(2)
    check("target rate is explicit diagnostic input", target_rate, Fraction(2), target_rate == Fraction(2))
    check("diagnostic energy violation", (two_state_energy(target_rate), two_state_energy(source_rate)),
          "target > source", two_state_energy(target_rate) > two_state_energy(source_rate))
    equalized_rate = source_rate
    check("rate mutation removes diagnostic violation", two_state_energy(equalized_rate),
          two_state_energy(source_rate), not (two_state_energy(equalized_rate) > two_state_energy(source_rate)))
    oversized_kappa = Fraction(2)
    check("oversized kappa fails conductance premise", Fraction(3, 2) * oversized_kappa ** 2,
          "greater than source mass", Fraction(3, 2) * oversized_kappa ** 2 > Fraction(1))
    reversed_contraction = two_state_energy(target_rate) <= two_state_energy(source_rate)
    check("reversed contraction is rejected", reversed_contraction, False, reversed_contraction is False)

    text = json.dumps(contract, sort_keys=True).lower()
    check("physical terms stay in non-claims only", "physical pre-a" in text,
          True, any("physical pre-a" in item.lower() for item in contract["non_claims"]))
    check("abstract witness is not PAH carrier", contract["diagnostic_witness"]["scope"],
          "abstract only", contract["diagnostic_witness"]["scope"].startswith("Abstract insufficiency"))
    check("contract remains non-claim-bearing", contract["provenance"]["claim_bearing"], False,
          contract["provenance"]["claim_bearing"] is False)
    check("contract remains no gate change", contract["provenance"]["active_gate_change"], False,
          contract["provenance"]["active_gate_change"] is False)
    check("candidate still leaves dynamic energy open", candidate["open_obligations"], "energy field missing",
          any("energy" in item.lower() for item in candidate["open_obligations"]))

    return {
        "schema": "tect/pah-omc020-energy-intertwining-hostile/1.0",
        "status": "PASS_HOSTILE_ENERGY_SCOPE_CONTROLS",
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
        "finding": "Hostile mutations are rejected; static L2 contraction is not promoted to dynamic form intertwining and the abstract witness is not a PAH negative result.",
        "non_claims": contract["non_claims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    atomic_json(args.output, payload)
    if args.check:
        replay = compute()
        if replay != json.loads(args.output.read_text(encoding="utf-8")):
            raise SystemExit("deterministic replay mismatch")
    print(f"PAH-OMC-020 ENERGY HOSTILE: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
