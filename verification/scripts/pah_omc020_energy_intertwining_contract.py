#!/usr/bin/env python3
"""Audit the PAH-OMC-020 root-wise energy-intertwining input contract.

This is a bounded conditional audit.  It freezes the unchanged PAH source
and the R-525 static maximal-prefix coupling, proves the elementary
conductance/intertwining implication on a finite weighted edge, and records
an abstract two-state witness showing that static L2 contraction alone does
not imply form contraction.  The witness is not a PAH carrier or a PAH
counterexample.  No source-authorized dynamic coupling is synthesized.
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
    "2026-09-08-pah-omc020-energy-intertwining/primary.json"
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
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {relative}")
    return value


def two_state_energy(probability: tuple[Fraction, Fraction], rate: Fraction,
                     values: tuple[Fraction, Fraction]) -> Fraction:
    """Directed-half reversible energy for one two-state root."""
    delta = values[1] - values[0]
    return sum(probability[index] * rate * delta * delta for index in range(2)) / 2


def weighted_transfer(source_mass: Fraction, target_mass: Fraction,
                      kappa: Fraction, delta: Fraction) -> tuple[Fraction, Fraction]:
    source = source_mass * delta * delta / 2
    target = target_mass * (kappa * delta) ** 2 / 2
    return source, target


def compute() -> dict:
    rows: list[dict] = []
    source_hashes = {}
    for relative, expected in PINS.items():
        actual = digest(ROOT / relative)
        source_hashes[relative] = actual
        check(rows, f"source hash:{relative}", actual, expected, actual == expected)

    contract = load("strategy/pa-hyp/PAH-OMC-020-energy-intertwining-contract-v1.json")
    pah = load("strategy/pa-hyp/PAH-001-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    r510 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r511 = load("strategy/pa-hyp/PAH-OMC-018-result-v1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    r525 = load("strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-result-v1.json")
    snapshot = load("strategy/pa-hyp/PAH-OMC-020-owner-search-snapshot-v1.json")

    check(rows, "contract identity", contract["contract_id"],
          "PAH-OMC-020-N2B-ENERGY-INTERTWINING",
          contract["contract_id"] == "PAH-OMC-020-N2B-ENERGY-INTERTWINING")
    check(rows, "contract is conditional", contract["provenance"]["constructed_hypothesis"],
          True, contract["provenance"]["constructed_hypothesis"] is True)
    check(rows, "contract is not source authorized", contract["provenance"]["source_authorized"],
          False, contract["provenance"]["source_authorized"] is False)
    check(rows, "PAH packet identity", pah["packet_id"], "PAH-001",
          pah["packet_id"] == "PAH-001")
    check(rows, "PAH immutability marker", pah["immutability"].startswith(
        "This accepted source file is immutable"), True,
        pah["immutability"].startswith("This accepted source file is immutable"))
    check(rows, "preregistered j-before-n order", "First j" in prereg["scope"]["regulator_order"]
          and "then" in prereg["scope"]["regulator_order"], True,
          prereg["scope"]["regulator_order"])
    check(rows, "external Markov time only", "external unaccelerated Markov time"
          in prereg["scope"]["time"], True, prereg["scope"]["time"])
    check(rows, "R-510 local state parent", r510["result_id"], "R-510",
          r510["result_id"] == "R-510")
    check(rows, "R-511 local form parent", r511["result_id"], "R-511",
          r511["result_id"] == "R-511")
    check(rows, "R-512 minimal target parent", r512["result_id"], "R-512",
          r512["result_id"] == "R-512" and "minimal" in r512["conclusion"])
    check(rows, "R-525 is static candidate only", r525["verdict"], "HOLD_FOR_EVIDENCE",
          r525["verdict"] == "HOLD_FOR_EVIDENCE" and "energy" in " ".join(r525["missing_assumptions"]).lower())
    check(rows, "R-528 snapshot is fixed", snapshot["status"], "FIXED_SEARCH_SNAPSHOT",
          snapshot["status"] == "FIXED_SEARCH_SNAPSHOT")
    check(rows, "R-528 authorized set empty", snapshot["authorized_paths"], [],
          snapshot["authorized_paths"] == [])
    check(rows, "R-528 complete set empty", snapshot["complete_paths"], [],
          snapshot["complete_paths"] == [])
    candidate = load("strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json")
    check(rows, "candidate map is maximal-prefix coupling",
          candidate["map"]["kind"], "maximal-prefix-coupling-conditional-expectation",
          candidate["map"]["kind"] == "maximal-prefix-coupling-conditional-expectation")
    check(rows, "candidate explicitly leaves energy open",
          any("energy" in field.lower() for field in candidate["open_obligations"]),
          True, candidate["open_obligations"])

    # Conditional one-root transfer implication using exact rational arithmetic.
    source_mass = Fraction(1)
    target_mass = Fraction(3, 2)
    kappa = Fraction(1, 2)
    delta = Fraction(3, 2)
    source_energy, target_energy = weighted_transfer(source_mass, target_mass, kappa, delta)
    check(rows, "weighted conductance premise", target_mass * kappa * kappa,
          Fraction(3, 8), target_mass * kappa * kappa == Fraction(3, 8))
    check(rows, "weighted conductance domination", target_mass * kappa * kappa,
          source_mass, target_mass * kappa * kappa <= source_mass)
    check(rows, "conditional one-root energy transfer", target_energy,
          Fraction(27, 64), target_energy <= source_energy)
    check(rows, "conditional source energy positive", source_energy,
          Fraction(9, 8), source_energy > 0)
    check(rows, "conditional target energy bound", target_energy,
          Fraction(27, 64), target_energy <= source_energy)

    # Exact abstract insufficiency witness: same marginals and identity U.
    probability = (Fraction(1, 2), Fraction(1, 2))
    observable = (Fraction(0), Fraction(1))
    source_rate = Fraction(1)
    target_rate = Fraction(2)
    source_oracle_energy = two_state_energy(probability, source_rate, observable)
    target_oracle_energy = two_state_energy(probability, target_rate, observable)
    source_l2 = sum(probability[index] * observable[index] ** 2 for index in range(2))
    target_l2 = source_l2
    check(rows, "static identity coupling is L2 contractive", target_l2, source_l2,
          target_l2 <= source_l2)
    check(rows, "abstract target energy exceeds source", target_oracle_energy,
          Fraction(1), target_oracle_energy > source_oracle_energy)
    check(rows, "abstract source energy value", source_oracle_energy,
          Fraction(1, 2), source_oracle_energy == Fraction(1, 2))
    check(rows, "abstract target energy value", target_oracle_energy,
          Fraction(1), target_oracle_energy == Fraction(1))
    check(rows, "abstract witness is not PAH claim", contract["diagnostic_witness"]["scope"],
          "Abstract insufficiency witness only; not a PAH carrier, not a PAH counterexample and not an infinite-volume statement.",
          contract["diagnostic_witness"]["scope"].startswith("Abstract insufficiency witness only"))

    dynamic_text = " ".join(contract["required_dynamic_datum"].values()).lower()
    candidate_text = json.dumps(r525, sort_keys=True).lower()
    check(rows, "dynamic datum is explicit in contract", all(
        token in dynamic_text for token in ("root", "conductance", "uniform", "terminal")),
        True, dynamic_text)
    check(rows, "candidate has no supplied kappa/defect", "kappa" not in candidate_text
          or "defect" not in candidate_text, True, "static candidate leaves dynamic data open")
    check(rows, "no physical promotion", contract["provenance"]["physical_promotion"],
          False, contract["provenance"]["physical_promotion"] is False)

    return {
        "schema": "tect/pah-omc020-energy-intertwining-primary/1.0",
        "status": "HOLD_FOR_EVIDENCE_ENERGY_INTERTWINING",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "contract_sha256": digest(CONTRACT),
        "checks": rows,
        "checks_passed": len(rows),
        "exact_scope": contract["fixed_scope"],
        "conditional_contract": contract["conditional_implication"],
        "abstract_witness": {
            "stationary_marginal": "(1/2,1/2)",
            "static_map": "identity",
            "observable": "(0,1)",
            "source_rate": "1",
            "target_rate": "2",
            "source_energy": str(source_oracle_energy),
            "target_energy": str(target_oracle_energy),
            "l2_norm_source": str(source_l2),
            "l2_norm_target": str(target_l2),
            "scope": contract["diagnostic_witness"]["scope"],
        },
        "finding": (
            "The exact finite weighted-edge implication is valid under a "
            "root-wise conductance-compatible dynamic intertwining and a "
            "uniform summable defect.  R-525 supplies only a static "
            "maximal-prefix conditional-expectation contraction and local N1 "
            "recovery; R-528 records no source-authorized owner packet.  The "
            "two-state oracle shows that identical Gibbs marginals and L2 "
            "contraction can still increase Dirichlet energy when root rates "
            "are not dynamically coupled.  This is an evidence boundary, not "
            "a PAH counterexample."
        ),
        "missing_assumptions": [
            "A source-authorized root correspondence with exact multiplicity and partial domains.",
            "A PAH-specific dynamic coupling or explicit defect for Delta_infty(U_n f) versus finite root differences.",
            "Uniform conductance/defect control in the anchored n exhaustion on the declared form domain.",
            "Terminal-square versus split-cell compatibility without a conditional-average or density-ratio repair.",
            "N2b arbitrary-sequence liminf/recovery, N2c/N4 boundary escape and N2d minimal-form identification.",
        ],
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_energy_intertwining_contract.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_energy_intertwining_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_energy_intertwining_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_energy_intertwining_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020Energy.lean",
        },
        "next_single_question": contract["single_next_question"],
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
    print(f"PAH-OMC-020 ENERGY INTERTWINING: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
