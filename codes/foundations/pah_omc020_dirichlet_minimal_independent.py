#!/usr/bin/env python3
"""Non-importing replay of the R-512 normal-contraction audit.

The derivation uses max/min clipping and an independently enumerated rational
grid.  It remains a conditional finite algebra check for the inherited
R-512 form, not a temporal convergence proof.
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
    "2026-09-08-pah-omc020-dirichlet-minimal/independent.json"
)

PINNED = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clip(value: Fraction) -> Fraction:
    # max/min is intentionally written independently from the primary.
    lower = value if value > 0 else Fraction(0)
    return lower if lower < 1 else Fraction(1)


def sq_energy(values: list[Fraction], edges: list[tuple[int, int, Fraction]], fn) -> Fraction:
    total = Fraction(0)
    for left, right, weight in edges:
        total += weight * (fn(values[left]) - fn(values[right])) ** 2
    return total


def atomic(path: Path, payload: dict) -> None:
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


def record(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows: list[dict] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    r511 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    hashes = {path: sha(ROOT / path) for path in PINNED}
    for path, expected in PINNED.items():
        record(rows, f"pinned source {path}", hashes[path], expected, hashes[path] == expected)

    record(rows, "contract identifier", contract["contract_id"],
           "PAH-OMC-020-DIRICHLET-MINIMAL-CONTRACTION",
           contract["contract_id"] == "PAH-OMC-020-DIRICHLET-MINIMAL-CONTRACTION")
    record(rows, "minimal target retained", "minimal closed" in r512["conclusion"], True,
           "minimal closed" in r512["conclusion"])
    record(rows, "R-511 form is root weighted", "c_r" in contract["fixed_scope"]["form_identity"], True,
           "c_r" in contract["fixed_scope"]["form_identity"])
    record(rows, "normal contraction has zero anchor", "eta(0)=0" in contract["fixed_scope"]["normal_contractions"], True,
           "eta(0)=0" in contract["fixed_scope"]["normal_contractions"])
    record(rows, "normal contraction has unit slope bound", "|eta(a)-eta(b)|<=|a-b|" in contract["fixed_scope"]["normal_contractions"], True,
           "|eta(a)-eta(b)|<=|a-b|" in contract["fixed_scope"]["normal_contractions"])
    record(rows, "domain stability retained", "D is stable" in contract["derivation"]["domain_stability"], True,
           "D is stable" in contract["derivation"]["domain_stability"])
    record(rows, "closure passage retained", "form-norm Cauchy" in contract["derivation"]["closure_passage"], True,
           "form-norm Cauchy" in contract["derivation"]["closure_passage"])
    record(rows, "constant-one conservation premise", "zero exact form energy" in contract["derivation"]["conservativity"], True,
           "zero exact form energy" in contract["derivation"]["conservativity"])

    # Independent exact edge fixture.  Weights and values are labelled test oracles only.
    values = [Fraction(-7, 3), Fraction(5, 2), Fraction(1, 4), Fraction(11, 6), Fraction(-2)]
    edges = [(0, 1, Fraction(3, 2)), (1, 2, Fraction(7, 4)), (2, 3, Fraction(5, 3)), (3, 4, Fraction(11, 5)), (4, 0, Fraction(13, 6))]
    before = sq_energy(values, edges, lambda x: x)
    after = sq_energy(values, edges, clip)
    record(rows, "all fixture weights positive", all(edge[2] > 0 for edge in edges), True,
           all(edge[2] > 0 for edge in edges))
    record(rows, "independent weighted square inequality", after <= before, True, after <= before)
    record(rows, "independent fixture strict decrease", after < before, True, after < before)

    # Exhaustive finite-difference check of the clipping map on an independent grid.
    grid = [Fraction(k, 3) for k in range(-12, 13)]
    checked = 0
    worst_slack = None
    for x in grid:
        for y in grid:
            lhs = abs(clip(x) - clip(y))
            rhs = abs(x - y)
            if lhs > rhs:
                raise AssertionError("max/min clipping failed the 1-Lipschitz grid test")
            slack = rhs - lhs
            worst_slack = slack if worst_slack is None or slack < worst_slack else worst_slack
            checked += 1
    record(rows, "independent clipping grid", checked, len(grid) ** 2, checked == len(grid) ** 2)
    record(rows, "grid slack nonnegative", worst_slack >= 0, True, worst_slack >= 0)

    # Form-norm contraction has an L2 component because eta(0)=0.
    l2_values = [Fraction(-5, 2), Fraction(3, 2), Fraction(1, 3), Fraction(-1, 4)]
    l2_before = sum(value * value for value in l2_values)
    l2_after = sum(clip(value) * clip(value) for value in l2_values)
    record(rows, "independent Hilbert contraction", l2_after <= l2_before, True, l2_after <= l2_before)
    constant = [Fraction(1)] * len(values)
    record(rows, "constant-one edge energy zero", sq_energy(constant, edges, lambda x: x) == 0, True,
           sq_energy(constant, edges, lambda x: x) == 0)

    temporal_text = " ".join(contract["missing_assumptions"])
    for marker in ("N2b", "N2c/N4", "N2d"):
        record(rows, f"open temporal field {marker}", marker in temporal_text, True, marker in temporal_text)
    record(rows, "no physical promotion", contract["provenance"]["physical_promotion"], False,
           contract["provenance"]["physical_promotion"] is False)
    record(rows, "no active gate change", contract["provenance"]["active_gate_change"], False,
           contract["provenance"]["active_gate_change"] is False)

    payload = {
        "schema": "tect/pah-omc020-dirichlet-minimal-independent/1.0",
        "status": "PASS_INDEPENDENT_DIRICHLET_SCOPE",
        "verdict": "PASS",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": hashes,
        "contract_sha256": sha(CONTRACT),
        "fixture": {
            "values": [str(value) for value in values],
            "edges": [[left, right, str(weight)] for left, right, weight in edges],
            "raw_energy": str(before),
            "clipped_energy": str(after),
            "grid_pair_count": checked,
            "minimum_grid_slack": str(worst_slack),
        },
        "finding": "Independent max/min derivation confirms the root-square normal-contraction inequality and constant-one zero energy under the inherited R-512 form; temporal comparison obligations remain open.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
    }
    atomic(args.output, payload)
    if args.check:
        replay = json.loads(args.output.read_text(encoding="utf-8"))
        if replay != payload:
            raise SystemExit("independent Dirichlet replay mismatch")
    print(f"PAH-OMC-020 DIRICHLET INDEPENDENT: {len(rows)} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
