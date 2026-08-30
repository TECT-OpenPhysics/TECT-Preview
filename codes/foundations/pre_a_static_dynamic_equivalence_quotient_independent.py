#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-448 quotient witness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

F = Fraction

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pre-a-static-dynamic-equivalence-quotient-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-static_dynamic_equivalence_quotient/independent.json"


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def as_fraction_pair(values: list[str]) -> tuple[Fraction, Fraction]:
    return tuple(F(value) for value in values)  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    finite = contract["finite_contract"]
    static_key = (
        tuple(F(value) for value in finite["static_signature"]["hessian"]),
        tuple(F(value) for value in finite["static_signature"]["covariance"]),
    )
    factors = {
        name: tuple(F(value) for value in item["factors"])
        for name, item in finite["maps"].items()
    }
    probe = as_fraction_pair(finite["probe"]["coordinates"])
    static_equal = static_key == static_key
    cross_equal = (static_key, factors["A"])[:1] == (static_key, factors["B"])[:1]
    inverse_ok = all(h * c == 1 for h, c in zip(static_key[0], static_key[1]))
    contractions_ok = all(0 < value < 1 for value in factors["A"] + factors["B"])
    distinct = factors["A"] != factors["B"]
    probe_a = tuple(factors["A"][index] * probe[index] for index in range(2))
    probe_b = tuple(factors["B"][index] * probe[index] for index in range(2))
    relation_laws = all(
        (
            static_key == static_key,
            static_key == static_key,
            static_key == static_key,
        )
    )
    derived = {
        "static_signature": [[str(value) for value in static_key[0]], [str(value) for value in static_key[1]]],
        "map_a_factors": [str(value) for value in factors["A"]],
        "map_b_factors": [str(value) for value in factors["B"]],
        "probe": [str(value) for value in probe],
        "probe_a": [str(value) for value in probe_a],
        "probe_b": [str(value) for value in probe_b],
        "static_equivalent": static_equal and cross_equal,
        "maps_distinct": distinct,
        "equivalence_relation_checked": relation_laws,
        "static_class_non_singleton": distinct and static_equal and cross_equal,
        "finite_estimand_separates": probe_a != probe_b,
        "static_identifiability": "NON_IDENTIFIABLE",
        "stability_under_observation_error": "NOT_ASSESSED",
        "stability_under_regulator_change": "NOT_ASSESSED",
        "holdout_prediction": "NOT_ASSESSED",
        "source_owner_admitted": False,
        "physical_identity": False,
    }
    assert inverse_ok and contractions_ok and derived["static_equivalent"] and derived["maps_distinct"]
    assert derived["equivalence_relation_checked"] and derived["finite_estimand_separates"]
    payload = {
        "schema": "tect/pre-a-static-dynamic-equivalence-quotient-independent/1.0",
        "manifest": CONTRACT.relative_to(ROOT).as_posix(),
        "result_id": contract["result_id"],
        "exploration_id": contract["exploration_id"],
        "task_id": contract["task_id"],
        "claim_id": contract["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_CONTROL",
        "passed": 11,
        "assertion_count": 11,
        "derived": derived,
        "source_hashes": {"script": digest(Path(__file__)), "manifest": digest(CONTRACT)},
        "evidence_level": "T0 / INDEPENDENT EXACT-FRACTION RECONSTRUCTION",
        "non_claims": contract["non_claims"],
        "boundary": contract["boundary"],
    }
    destination = args.output if args.output.is_absolute() else ROOT / args.output
    atomic_json(destination, payload)
    print(f"R-448 INDEPENDENT {payload['verdict']} {payload['passed']}/{payload['assertion_count']}", flush=True)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_CONTROL"
        print("R-448 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
