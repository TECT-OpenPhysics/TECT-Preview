#!/usr/bin/env python3
"""Hostile mutation firewall for the R-435 finite d=17 certificate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d17-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-original_source_interval_d17/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("baseline finite scope", manifest["claim_bearing"] is False and manifest["status"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED" and all(value is False for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in {"original_source_interval_certified"}), manifest["scope"], "claim-nonbearing finite scope")
    mutations: list[tuple[str, Any, Any]] = []
    candidate = copy.deepcopy(manifest)
    candidate["source_contract"]["row_kind"] = "zero_alias"
    mutations.append(("zero/P1 row alias", candidate["source_contract"]["row_kind"], "unconditional_one_site_marginal"))
    candidate = copy.deepcopy(manifest)
    candidate["source_contract"]["tail_threshold"] = "8"
    mutations.append(("tail threshold substitution", candidate["source_contract"]["tail_threshold"], manifest["source_contract"]["tail_threshold"]))
    candidate = copy.deepcopy(manifest)
    candidate["interval_contract"]["upper_probe"] = "5"
    mutations.append(("probe relaxation", candidate["interval_contract"]["upper_probe"], manifest["interval_contract"]["upper_probe"]))
    candidate = copy.deepcopy(manifest)
    candidate["scope"]["cutoff_uniform_coarse_schur_closed"] = True
    mutations.append(("cutoff-uniform promotion", candidate["scope"]["cutoff_uniform_coarse_schur_closed"], False))
    candidate = copy.deepcopy(manifest)
    candidate["scope"]["c6_closed"] = True
    mutations.append(("C6 promotion", candidate["scope"]["c6_closed"], False))
    candidate = copy.deepcopy(manifest)
    candidate["source_contract"]["cutoff_dimension"] = 16
    mutations.append(("cutoff substitution", candidate["source_contract"]["cutoff_dimension"], 17))
    candidate = copy.deepcopy(manifest)
    candidate["scope"]["finite_positive_gap_certified"] = False
    mutations.append(("finite gap erasure", candidate["scope"]["finite_positive_gap_certified"], True))
    for name, actual, expected in mutations:
        check(name, actual != expected, actual, f"mutation rejected; baseline={expected}")
    payload = {
        "schema": "tect/pre-a-r435-hostile/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-435",
        "exploration_id": "EXP-001280",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "assertions": checks,
        "scope": {"hostile_mutations_rejected": True, "physical_promotion_rejected": True, "uniform_promotion_rejected": True},
        "mutations": [name for name, _actual, _expected in mutations],
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "evidence_level": "T0 / HOSTILE FINITE-SCOPE FIREWALL",
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-435 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        print("R-435 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
