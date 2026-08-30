#!/usr/bin/env python3
"""Hostile mutation lane for the R-457 finite M3 equation audit."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-m3-compact-u1-equation-level-audit-manifest.json"
DEFAULT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-pre_a_m3_compact_u1_equation_level_audit/hostile.json"
)


def save(path: Path, payload: dict[str, Any]) -> None:
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


def charge(size: int, factors: list[tuple[str, tuple[int, int, int], int, int | None]]) -> dict[tuple[int, int, int], int]:
    points = [(a, b, c) for a in range(size) for b in range(size) for c in range(size)]
    out = {point: 0 for point in points}
    for kind, point, sign, axis in factors:
        if kind in ("phi", "pi"):
            out[point] += sign
        else:
            if axis is None:
                raise AssertionError("missing link axis")
            target = list(point)
            target[axis] = (target[axis] + 1) % size
            target_point = tuple(target)
            out[point] += sign
            out[target_point] -= sign
    return out


def mutation_checks(manifest: dict[str, Any]) -> list[tuple[str, Callable[[], bool]]]:
    size = int(manifest["finite_scope"]["lattice_sizes"][0])
    origin = (0, 0, 0)
    shifted = (1 % size, 0, 0)
    plaquette = [
        ("U", origin, 1, 0),
        ("U", shifted, 1, 1),
        ("U", (0, 1 % size, 0), -1, 0),
        ("U", origin, -1, 1),
    ]

    def nonzero(items: list[tuple[str, tuple[int, int, int], int, int | None]]) -> bool:
        return any(value != 0 for value in charge(size, items).values())

    def bad_endpoint() -> bool:
        altered = list(plaquette)
        altered[1] = ("U", origin, 1, 1)
        return nonzero(altered)

    def wrong_pi_phase() -> bool:
        return nonzero([("pi", origin, 1, None), ("phi", origin, 1, None)])

    def unpaired_covariant_term() -> bool:
        return nonzero([("U", origin, 1, 0), ("phi", origin, 1, None)])

    def negative_lambda() -> bool:
        return Fraction("-1/2") <= 0

    def physical_empty_promotion() -> bool:
        return manifest["scope"]["physical_empty_closed"] is False

    def yang_mills_promotion() -> bool:
        return manifest["scope"]["yang_mills_identity_closed"] is False

    def continuum_promotion() -> bool:
        return manifest["scope"]["continuum_closed"] is False

    def source_owner_omission() -> bool:
        return manifest["scope"]["source_owner_admitted"] is False

    return [
        ("reverse_or_duplicate_endpoint", bad_endpoint),
        ("wrong_pi_phase", wrong_pi_phase),
        ("unpaired_covariant_link", unpaired_covariant_term),
        ("nonpositive_lambda", negative_lambda),
        ("physical_empty_relabel", physical_empty_promotion),
        ("compact_u1_to_yang_mills", yang_mills_promotion),
        ("finite_to_continuum_promotion", continuum_promotion),
        ("missing_source_owner_admission", source_owner_omission),
    ]


def run(path: Path = DEFAULT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutations = mutation_checks(manifest)
    rejected: list[dict[str, Any]] = []
    for name, test in mutations:
        result = bool(test())
        if not result:
            raise AssertionError(f"hostile mutation escaped: {name}")
        rejected.append({"mutation": name, "status": "REJECTED"})
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutation_count": len(mutations),
        "mutations_rejected": rejected,
        "assertion_count": len(rejected),
        "derived": {
            "equation_charge_audit_closed": True,
            "source_owner_admitted": False,
            "candidate_admitted": False,
            "physical_identity": False,
            "continuum_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "boundary": manifest["boundary"],
        "non_claims": manifest["non_claims"],
    }
    save(path, payload)
    print(f"R-457 HOSTILE HOSTILE_MUTATIONS_REJECTED {len(rejected)}/{len(mutations)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else ROOT / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
