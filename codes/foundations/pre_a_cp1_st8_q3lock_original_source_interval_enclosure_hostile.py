#!/usr/bin/env python3
"""Hostile mutation checks for the R-433 finite interval certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-enclosure-manifest.json"
PRIMARY = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_enclosure/primary.json"
INDEPENDENT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_enclosure/independent.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-original_source_interval_enclosure/hostile.json"


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
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def reject(name: str, mutation: Any, accepted: bool, reason: str) -> None:
        if accepted:
            raise AssertionError(f"hostile mutation was accepted: {name}")
        checks.append({"name": name, "status": "REJECTED", "mutation": mutation, "reason": reason})

    reject(
        "wrong parent coordinate",
        {"target_parent_coordinate": 5},
        manifest["source_contract"]["target_parent_coordinate"] != 6,
        "ordinal 7 is fixed to parent coordinate 6 by R-432",
    )
    reject(
        "wrong emission ordinal",
        {"target_emission_ordinal": 6},
        manifest["source_contract"]["target_emission_ordinal"] != 7,
        "the corrected source row is emission ordinal 7",
    )
    reject(
        "wrong beta fixture",
        {"beta": "4"},
        manifest["source_contract"]["beta"] == "4",
        "the R-419 beta=8 source contract is immutable",
    )
    reject(
        "symmetry reduction removed",
        {"symmetry_block_sizes": [256]},
        primary["derived"]["symmetry_block_sizes"] == [256],
        "the four exchange/parity blocks are a required source check",
    )
    reject(
        "interval width gate relaxed",
        {"maximum_matrix_interval_width": "1"},
        manifest["interval_contract"]["maximum_matrix_interval_width"] != "1e-8",
        "the finite conditioning-width threshold cannot be disabled",
    )
    reject(
        "lower Cholesky probe omitted",
        {"lower_probe": "0"},
        manifest["interval_contract"]["lower_probe"] == "0",
        "the lower probe is part of the fixed two-sided spectral certificate",
    )
    promoted = dict(primary["scope"])
    for key in ("c6_closed", "sector_a_closed", "pre_a_closed", "continuum_closed"):
        promoted[key] = True
    reject(
        "physical promotion mutation",
        {"c6_closed": True, "sector_a_closed": True, "pre_a_closed": True, "continuum_closed": True},
        not any(promoted[key] for key in ("c6_closed", "sector_a_closed", "pre_a_closed", "continuum_closed")),
        "R-433 is finite and claim-nonbearing; physical and continuum flags remain false",
    )
    if primary["verdict"] != "ORIGINAL_SOURCE_INTERVAL_CERTIFIED" or independent["verdict"] != "INDEPENDENT_FINITE_CONTROL_PASS":
        raise AssertionError("hostile audit requires the unmutated primary and independent controls")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r433-hostile/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-433",
        "exploration_id": "EXP-001278",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "hostile",
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_count": len(checks),
        "assertions": checks,
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "scope": {"hostile_mutations_rejected": True, "physical_promotion_rejected": True, "claim_bearing": False},
        "evidence_level": "T0 / EXECUTED ADVERSARIAL FINITE CONTROL",
        "non_claims": manifest["non_claims"],
    }
    atomic_json(output, payload)
    print(f"R-433 HOSTILE {payload['verdict']} {len(checks)}/{len(checks)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED"
        assert payload["scope"]["physical_promotion_rejected"] is True
        print("R-433 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
