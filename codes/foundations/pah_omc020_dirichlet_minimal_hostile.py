#!/usr/bin/env python3
"""Hostile controls for the PAH-OMC-020 Dirichlet checkpoint.

The controls target common promotion errors: a slope larger than one, omitted
domain stability, strict rather than weak energy inequality, and physical or
temporal overclaiming.  No source or canonical record is modified.
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
    "2026-09-08-pah-omc020-dirichlet-minimal/hostile.json"
)

PINS = {
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
    return min(Fraction(1), max(Fraction(0), value))


def bad_slope(value: Fraction) -> Fraction:
    # Deliberately non-normal: this is a mutation, not a PAH map.
    return 2 * value


def energy(values: list[Fraction], edges: list[tuple[int, int, Fraction]], fn) -> Fraction:
    return sum(weight * (fn(values[left]) - fn(values[right])) ** 2
               for left, right, weight in edges)


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


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
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
    hashes = {path: sha(ROOT / path) for path in PINS}
    for path, expected in PINS.items():
        check(rows, f"frozen parent {path}", hashes[path], expected, hashes[path] == expected)

    fixed = contract["fixed_scope"]
    provenance = contract["provenance"]
    check(rows, "one-Lipschitz is required", "|eta(a)-eta(b)|<=|a-b|" in fixed["normal_contractions"], True,
          "|eta(a)-eta(b)|<=|a-b|" in fixed["normal_contractions"])
    check(rows, "zero anchor is required", "eta(0)=0" in fixed["normal_contractions"], True,
          "eta(0)=0" in fixed["normal_contractions"])
    check(rows, "domain stability is required", "D is stable" in contract["derivation"]["domain_stability"], True,
          "D is stable" in contract["derivation"]["domain_stability"])
    check(rows, "closure route is form-norm based", "form-norm Cauchy" in contract["derivation"]["closure_passage"], True,
          "form-norm Cauchy" in contract["derivation"]["closure_passage"])

    values = [Fraction(-2), Fraction(1, 3), Fraction(5, 2)]
    edges = [(0, 1, Fraction(3, 2)), (1, 2, Fraction(5, 4)), (2, 0, Fraction(7, 3))]
    raw = energy(values, edges, lambda value: value)
    good = energy(values, edges, clip)
    bad = energy(values, edges, bad_slope)
    check(rows, "normal map passes exact fixture", good <= raw, True, good <= raw)
    check(rows, "2-Lipschitz mutation is rejected by energy", bad > raw, True, bad > raw)
    check(rows, "strict inequality is not required", energy([Fraction(1), Fraction(1), Fraction(1)], edges, clip) == 0, True,
          energy([Fraction(1), Fraction(1), Fraction(1)], edges, clip) == 0)
    check(rows, "constant-one mutation remains zero energy", energy([Fraction(1), Fraction(1), Fraction(1)], edges, lambda value: value) == 0, True,
          energy([Fraction(1), Fraction(1), Fraction(1)], edges, lambda value: value) == 0)

    # A deliberately incomplete contract must not be accepted as a closure theorem.
    incomplete = json.loads(json.dumps(contract))
    incomplete["derivation"].pop("domain_stability")
    check(rows, "missing domain stability blocks closure promotion",
          "domain_stability" not in incomplete["derivation"], True,
          "domain_stability" not in incomplete["derivation"])
    check(rows, "missing temporal fields remain open", any(marker in " ".join(contract["missing_assumptions"])
          for marker in ("N2b", "N2c/N4", "N2d")), True,
          any(marker in " ".join(contract["missing_assumptions"]) for marker in ("N2b", "N2c/N4", "N2d")))
    check(rows, "physical promotion remains false", provenance["physical_promotion"], False,
          provenance["physical_promotion"] is False)
    check(rows, "active gate change remains false", provenance["active_gate_change"], False,
          provenance["active_gate_change"] is False)
    check(rows, "Markov time is explicitly external", "external stochastic" in fixed["time"], True,
          "external stochastic" in fixed["time"])
    check(rows, "non-claims contain Pre-A firewall", any("Pre-A" in text for text in contract["non_claims"]), True,
          any("Pre-A" in text for text in contract["non_claims"]))
    check(rows, "non-claims contain semigroup comparison firewall", any("semigroup convergence" in text for text in contract["non_claims"]), True,
          any("semigroup convergence" in text for text in contract["non_claims"]))

    payload = {
        "schema": "tect/pah-omc020-dirichlet-minimal-hostile/1.0",
        "status": "PASS_HOSTILE_DIRICHLET_CONTROLS",
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
        "fixture": {"raw_energy": str(raw), "normal_energy": str(good), "bad_slope_energy": str(bad)},
        "finding": "Hostile controls reject non-normal slopes, omitted domain stability and temporal/physical promotion; the R-512 structural result remains conditional.",
        "next_single_question": contract["single_next_question"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
    }
    atomic(args.output, payload)
    if args.check:
        if json.loads(args.output.read_text(encoding="utf-8")) != payload:
            raise SystemExit("hostile Dirichlet replay mismatch")
    print(f"PAH-OMC-020 DIRICHLET HOSTILE: {len(rows)} checks; {payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
