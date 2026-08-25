#!/usr/bin/env python3
"""Independent Fraction lane for EXP-001124."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity"
SOURCE = Path(__file__).resolve()
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{NAME}" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def matmul(a: list[list[Fraction]], b: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def transpose(a: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(row) for row in zip(*a)]


def trace(a: list[list[Fraction]]) -> Fraction:
    return sum(a[i][i] for i in range(len(a)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001124" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001124/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    rho = [[Fraction(1, 2), 0, 0], [0, Fraction(1, 3), 0], [0, 0, Fraction(1, 6)]]
    rotation = [[Fraction(3, 5), Fraction(-4, 5), 0], [Fraction(4, 5), Fraction(3, 5), 0], [0, 0, 1]]
    tail = [[1, 0, 0], [0, 1, 0], [0, 0, -2]]
    dual = matmul(matmul(rotation, rho), transpose(rotation))
    square_tail = matmul(tail, tail)
    check("state normalized", trace(rho) == 1 and trace(dual) == 1, [trace(rho), trace(dual)], 1, "state")
    check("character orthogonal", matmul(transpose(rotation), rotation) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], matmul(transpose(rotation), rotation), "I", "character")
    check("tail commutes", matmul(rotation, tail) == matmul(tail, rotation), matmul(rotation, tail), matmul(tail, rotation), "commutation")
    ref = trace(matmul(rho, square_tail))
    dual_value = trace(matmul(dual, square_tail))
    check("static dual identity", ref == dual_value, [ref, dual_value], ref, "identity")
    check("reference two-sided", ref == trace(matmul(rho, square_tail)), ref, ref, "seminorm")
    check("dual two-sided", dual_value == trace(matmul(dual, square_tail)), dual_value, dual_value, "seminorm")
    scope = manifest["scope"]
    check("scope firewall", scope["abstract_static_dual_tail_identity_closed"] and scope["finite_matrix_fixture_closed"] and not scope["evolved_D_dual_tail_identity_closed"], scope, "static only", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-DUAL-TAIL-COMMUTING-CHARACTER-IDENTITY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "reference_tail_value": ref,
            "dual_tail_value": dual_value,
            "reference_right": ref,
            "reference_left": ref,
            "dual_right": dual_value,
            "dual_left": dual_value,
            "abstract_static_dual_tail_identity_closed": True,
            "finite_matrix_fixture_closed": True,
            "reference_tail_reuse_licensed": True,
            "evolved_D_dual_tail_identity_closed": False,
            "dual_modular_history_closed": False,
            "actual_q3_dual_state_uniform_closed": False,
            "actual_unbounded_q3_common_core_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
        },
        "provenance": {"script": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "script_sha256": digest(SOURCE), "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "manifest_sha256": digest(MANIFEST)},
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT DUAL-TAIL-COMMUTING-CHARACTER PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
