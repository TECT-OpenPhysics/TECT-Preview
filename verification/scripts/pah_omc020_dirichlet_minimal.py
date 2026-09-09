#!/usr/bin/env python3
"""Replay the R-512 minimal-form normal-contraction contract.

The source form, state and domain are inherited from PAH-OMC-018/019.  This
checker verifies exact scalar and finite weighted-edge consequences and the
immutable source boundary.  It is not a measure-construction or temporal
convergence proof.
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
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-contract-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-dirichlet-minimal/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-closure-prereg-v1.json":
        "4337e21a140206956ea52ee10e20d04358af868969e3edb9f055e5ea64b055b7",
    "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md":
        "593785ba86d0bf1b36541e62879a966062282c55cfbb990a805539b27955b8af",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
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


def clip01(value: Fraction) -> Fraction:
    return min(Fraction(1), max(Fraction(0), value))


def edge_energy(pairs: list[tuple[Fraction, Fraction]], weights: list[Fraction], fn) -> Fraction:
    return sum(
        weight * (fn(left) - fn(right)) ** 2
        for (left, right), weight in zip(pairs, weights)
    )


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
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def compute() -> dict:
    rows: list[dict] = []
    contract = load("strategy/pa-hyp/PAH-OMC-020-dirichlet-minimal-contract-v1.json")
    r511 = load("strategy/pa-hyp/PAH-OMC-018-result-v1.json")
    r512 = load("strategy/pa-hyp/PAH-OMC-019-result-v1.json")
    closure_prereg = load("strategy/pa-hyp/PAH-OMC-019-closure-prereg-v1.json")
    prereg = load("strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json")
    closure = (ROOT / "strategy/pa-hyp/PAH-OMC-019-closure-certificate.md").read_text(encoding="utf-8")

    source_hashes = {relative: digest(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        check(rows, f"source hash:{relative}", source_hashes[relative], expected,
              source_hashes[relative] == expected)
    check(rows, "contract identity", contract["contract_id"],
          "PAH-OMC-020-DIRICHLET-MINIMAL-CONTRACTION",
          contract["contract_id"] == "PAH-OMC-020-DIRICHLET-MINIMAL-CONTRACTION")
    check(rows, "contract has no model change", contract["provenance"]["model_change"], False,
          contract["provenance"]["model_change"] is False)
    check(rows, "contract is non-bearing", contract["provenance"]["claim_bearing"], False,
          contract["provenance"]["claim_bearing"] is False)
    frozen_text = contract["fixed_scope"]["functional_and_rates"].lower()
    check(rows, "PAH-001 functional/rates frozen",
          "no new move, rate, counterterm or averaging" in frozen_text,
          True, "no new move, rate, counterterm or averaging" in frozen_text)
    check(rows, "normal contraction definition",
          contract["fixed_scope"]["normal_contractions"], "eta(0)=0 and 1-Lipschitz",
          "eta(0)=0" in contract["fixed_scope"]["normal_contractions"]
          and "|eta(a)-eta(b)|<=|a-b|" in contract["fixed_scope"]["normal_contractions"])
    check(rows, "R-511 root-square form source",
          "(1/2)" in contract["fixed_scope"]["form_identity"]
          and "c_r" in contract["fixed_scope"]["form_identity"], True,
          "(1/2)" in contract["fixed_scope"]["form_identity"]
          and "c_r" in contract["fixed_scope"]["form_identity"])
    check(rows, "R-512 is minimal closed target",
          "minimal closed" in r512["conclusion"], True,
          "minimal closed" in r512["conclusion"])
    check(rows, "R-512 target semigroup is fixed",
          "T_min(t)=exp(-t K_min)" in prereg["objects_and_comparison"]["target_semigroup"], True,
          "T_min(t)=exp(-t K_min)" in prereg["objects_and_comparison"]["target_semigroup"])
    check(rows, "closure passage is explicit", "form norm" in closure
          and "Cauchy" in closure and "minimal form completion" in closure, True,
          "form norm" in closure and "Cauchy" in closure and "minimal form completion" in closure)
    check(rows, "domain stability is declared", "stable under" in contract["derivation"]["domain_stability"], True,
          "stable under" in contract["derivation"]["domain_stability"])
    check(rows, "external Markov time retained", "external stochastic" in contract["fixed_scope"]["time"], True,
          "external stochastic" in contract["fixed_scope"]["time"])
    check(rows, "no limit in this contract", "No j or n limit" in contract["fixed_scope"]["limit_order"], True,
          "No j or n limit" in contract["fixed_scope"]["limit_order"])

    # Exact labelled test oracle: the weights are positive conductances, not PAH parameters.
    pairs = [
        (Fraction(-2), Fraction(3, 2)),
        (Fraction(-1, 3), Fraction(5, 4)),
        (Fraction(7, 3), Fraction(1, 5)),
        (Fraction(0), Fraction(-5, 2)),
    ]
    weights = [Fraction(2), Fraction(5, 3), Fraction(7, 4), Fraction(11, 6)]
    raw = edge_energy(pairs, weights, lambda value: value)
    truncated = edge_energy(pairs, weights, clip01)
    check(rows, "positive fixture conductances", all(weight > 0 for weight in weights), True,
          all(weight > 0 for weight in weights))
    check(rows, "canonical truncation fixes zero", clip01(Fraction(0)), Fraction(0),
          clip01(Fraction(0)) == Fraction(0))
    check(rows, "canonical truncation fixes one", clip01(Fraction(1)), Fraction(1),
          clip01(Fraction(1)) == Fraction(1))
    check(rows, "weighted normal-contraction inequality", truncated <= raw, True, truncated <= raw)
    check(rows, "weighted inequality is strict on fixture", truncated < raw, True, truncated < raw)

    grid = [Fraction(k, 2) for k in range(-8, 9)]
    pair_count = 0
    for left in grid:
        for right in grid:
            pair_count += 1
            check_value = abs(clip01(left) - clip01(right)) <= abs(left - right)
            if not check_value:
                raise AssertionError("clip is not 1-Lipschitz on exact grid")
    check(rows, "clip 1-Lipschitz exact grid", pair_count, len(grid) ** 2, pair_count == len(grid) ** 2)

    # The form-norm closure uses both the H part and the energy part.
    h_pairs = [(Fraction(-3, 2), Fraction(2)), (Fraction(1, 4), Fraction(-1, 3))]
    h_before = sum(value * value for pair in h_pairs for value in pair)
    h_after = sum(clip01(value) ** 2 for pair in h_pairs for value in pair)
    check(rows, "eta(0)=0 gives Hilbert contraction fixture", h_after <= h_before, True,
          h_after <= h_before)
    check(rows, "constant energy is zero", edge_energy(pairs, weights, lambda _: Fraction(1)), Fraction(0),
          edge_energy(pairs, weights, lambda _: Fraction(1)) == Fraction(0))
    check(rows, "constant one belongs to declared domain", "Constants included" in closure_prereg["objects"]["D"], True,
          "Constants included" in closure_prereg["objects"]["D"])

    expected_missing = ["N2b", "N2c/N4", "N2d"]
    missing_text = " ".join(contract["missing_assumptions"])
    for marker in expected_missing:
        check(rows, f"remaining temporal obligation {marker}", marker in missing_text, True, marker in missing_text)
    check(rows, "physical firewall", any("physical Pre-A" in text for text in contract["non_claims"]), True,
          any("physical Pre-A" in text for text in contract["non_claims"]))
    check(rows, "QFT/gravity firewall", any("QFT" in text and "gravity" in text for text in contract["non_claims"]), True,
          any("QFT" in text and "gravity" in text for text in contract["non_claims"]))

    return {
        "schema": "tect/pah-omc020-dirichlet-minimal-primary/1.0",
        "status": "PASS_SCOPED_DIRICHLET_MINIMAL",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": source_hashes,
        "contract_sha256": digest(CONTRACT),
        "fixture": {
            "pairs": [[str(left), str(right)] for left, right in pairs],
            "weights": [str(weight) for weight in weights],
            "raw_energy": str(raw),
            "truncated_energy": str(truncated),
            "grid_pair_count": pair_count,
        },
        "finding": (
            "Under the exact inherited R-511 root-square form, normal contractions "
            "are form-contracting on D and the inequality passes through the R-512 "
            "minimal form completion.  The constant one has zero energy, so the "
            "associated target spectral semigroup is structurally Markov and "
            "conservative.  The finite-to-anchored-n comparison remains open."
        ),
        "closed_scoped_gate": "Conditional Dirichlet/Markov structure and conservativity of the R-512 minimal target.",
        "missing_assumptions": contract["missing_assumptions"],
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
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
            raise SystemExit("PAH-OMC-020 Dirichlet replay mismatch")
    print(f"PAH-OMC-020 DIRICHLET MINIMAL: {payload['checks_passed']} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
