#!/usr/bin/env python3
"""Hostile mutation firewall for the R-437 finite support-boundary audit."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-support-cross-cutoff-boundary-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-fixed_support_cross_cutoff_boundary/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def accepted(candidate: dict[str, Any]) -> bool:
    contract = candidate["comparison_contract"]
    expected = candidate["expected_relation"]
    scope = candidate["scope"]
    if candidate["claim_bearing"] or candidate["status"] != "FIXED_SUPPORT_ROUTE_LOCAL_BOUNDARY":
        return False
    if contract["crossing_index"] != 4 or contract["tail_threshold"] != "4":
        return False
    if expected["d17_index_status"] != "core" or expected["d18_index_status"] != "tail":
        return False
    if not expected["d17_phi_upper_below_threshold"] or not expected["d18_phi_lower_above_threshold"]:
        return False
    if expected["fixed_support_uniformity_closed"]:
        return False
    closed = {key: value for key, value in scope.items() if key.endswith("_closed")}
    return all(value is False for value in closed.values())


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("baseline accepted", accepted(manifest), manifest["status"], "route-local finite boundary")
    mutations: list[tuple[str, dict[str, Any]]] = []

    candidate = copy.deepcopy(manifest)
    candidate["scope"]["fixed_support_uniformity_closed"] = True
    mutations.append(("fixed-support promotion", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["scope"]["increasing_core_tail_modulus_closed"] = True
    mutations.append(("increasing-core promotion", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["expected_relation"]["d17_index_status"] = "tail"
    candidate["expected_relation"]["d18_index_status"] = "core"
    mutations.append(("status swap", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["comparison_contract"]["crossing_index"] = 3
    mutations.append(("crossing-index substitution", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["expected_relation"]["d18_index_status"] = "core"
    mutations.append(("d18 core substitution", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["expected_relation"]["d17_index_status"] = "tail"
    mutations.append(("d17 tail substitution", candidate))
    candidate = copy.deepcopy(manifest)
    candidate["scope"]["c6_closed"] = True
    mutations.append(("C6 promotion", candidate))

    for name, candidate in mutations:
        check(name, not accepted(candidate), candidate["status"], "mutation rejected")

    payload = {
        "schema": "tect/pre-a-r437-hostile/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-437",
        "exploration_id": "EXP-001282",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "assertions": checks,
        "scope": {"hostile_mutations_rejected": True, "uniform_promotion_rejected": True, "physical_promotion_rejected": True},
        "mutations": [name for name, _candidate in mutations],
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "evidence_level": "T0 / HOSTILE FINITE-SCOPE FIREWALL",
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-437 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        assert payload["assertion_count"] == 8
        print("R-437 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
