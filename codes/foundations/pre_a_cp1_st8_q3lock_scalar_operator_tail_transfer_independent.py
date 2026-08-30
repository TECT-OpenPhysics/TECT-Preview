#!/usr/bin/env python3
"""Independent reconstruction of the R-445 finite conditional transfer.

This control intentionally does not import the primary implementation.  It
rebuilds the rectangular edge families and the weighted triangle bound from
the manifest, so agreement is evidence about the finite contract only.
"""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-scalar_operator_tail_transfer/independent.json"


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
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def integer_points(sides: tuple[int, ...]) -> list[tuple[int, ...]]:
    points: list[tuple[int, ...]] = [()]
    for side in sides:
        points = [prefix + (coordinate,) for prefix in points for coordinate in range(side)]
    return points


def shell_weight(point: tuple[int, ...]) -> Fraction:
    radius = sum(abs(coordinate) for coordinate in point)
    return Fraction(1, 2**radius)


def tail_majorant(radius: int) -> Fraction:
    return Fraction(3 * (4 * radius * radius + 8 * radius + 14), 2 ** (radius - 1))


def reconstruct(sides: tuple[int, ...], radius: int, constant: Fraction) -> tuple[Fraction, Fraction, int]:
    points = integer_points(sides)
    tail_weights: list[tuple[tuple[int, ...], Fraction, int]] = []
    for point in points:
        point_radius = sum(abs(coordinate) for coordinate in point)
        if point_radius < radius:
            continue
        for axis, side in enumerate(sides):
            if point[axis] + 1 < side:
                tail_weights.append((point, shell_weight(point), axis))
    scalar_tail = sum((weight for _point, weight, _axis in tail_weights), Fraction(0))
    signed_tail = sum(
        (
            (1 if (sum(abs(coordinate) for coordinate in point) + axis) % 2 == 0 else -1)
            * constant
            * weight
            for point, weight, axis in tail_weights
        ),
        Fraction(0),
    )
    return scalar_tail, signed_tail, len(tail_weights)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["finite_contract"]
    dimension = int(contract["dimension"])
    side_min = int(contract["box_side_min"])
    side_max = int(contract["box_side_max"])
    radius_min = int(contract["tail_radius_min"])
    radius_max = int(contract["tail_radius_max"])
    constants = [Fraction(value) for value in contract["majorant_constant_inputs"]]
    boxes = 0
    edges = 0
    tail_rows = 0
    max_scalar_ratio = Fraction(0)
    max_operator_ratio = Fraction(0)
    checks = 0
    samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal checks
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks += 1
        if len(samples) < 24:
            samples.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]] == ["R-445", "EXP-001297", "T-054", False], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "R-445/EXP-001297/T-054/false", "provenance")
    check("contract bound", contract["term_bound"] == "||K_e|| <= C*w(e)", contract["term_bound"], "||K_e|| <= C*w(e)", "contract")
    check("contract chain", "C*T(R)" in contract["transfer_chain"], contract["transfer_chain"], "ambient scalar bound", "contract")
    check("conditional scope", manifest["scope"]["per_edge_majorant_assumed"] is True and manifest["scope"]["operator_norm_of_actual_q3_terms"] is False, manifest["scope"], "assumed per-edge majorant only", "scope")
    for key in ("q3lock_commutator_identification", "history_tail_closed", "weighted_operator_form_closed", "common_core_closed", "common_alpha_closed", "exhaustion_cauchy_closed", "kms_gns_gap_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        check(f"firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    for first in range(side_min, side_max + 1):
        for second in range(side_min, side_max + 1):
            for third in range(side_min, side_max + 1):
                sides = (first, second, third)
                boxes += 1
                vertices = integer_points(sides)
                edges += sum(1 for point in vertices for axis, side in enumerate(sides) if point[axis] + 1 < side)
                for radius in range(radius_min, radius_max + 1):
                    scalar_tail, _signed_unused, edge_count = reconstruct(sides, radius, Fraction(1))
                    scalar_bound = tail_majorant(radius)
                    check(f"box {boxes} radius {radius} scalar", scalar_tail <= scalar_bound, scalar_tail, scalar_bound, "scalar-reuse")
                    max_scalar_ratio = max(max_scalar_ratio, scalar_tail / scalar_bound)
                    tail_rows += 1
                    for constant in constants:
                        scalar_tail, signed_tail, counted_edges = reconstruct(sides, radius, constant)
                        finite_budget = constant * scalar_tail
                        ambient_budget = constant * scalar_bound
                        check(f"box {boxes} radius {radius} C={constant} edge count", counted_edges == edge_count, counted_edges, edge_count, "operator-transfer")
                        check(f"box {boxes} radius {radius} C={constant} signed triangle", abs(signed_tail) <= finite_budget, abs(signed_tail), finite_budget, "operator-transfer")
                        check(f"box {boxes} radius {radius} C={constant} ambient", abs(signed_tail) <= ambient_budget, abs(signed_tail), ambient_budget, "operator-transfer")
                        max_operator_ratio = max(max_operator_ratio, abs(signed_tail) / ambient_budget)

    check("box enumeration", boxes == (side_max - side_min + 1) ** dimension, boxes, (side_max - side_min + 1) ** dimension, "enumeration")
    check("tail enumeration", tail_rows == boxes * (radius_max - radius_min + 1), tail_rows, boxes * (radius_max - radius_min + 1), "enumeration")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r445-independent/1.0",
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "result_id": "R-445",
        "exploration_id": "EXP-001297",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_CONDITIONAL_WEIGHTED_NORM_TRANSFER_CONTROL",
        "passed": checks,
        "assertion_count": checks,
        "assertions": samples,
        "assertion_samples_truncated": checks > len(samples),
        "derived": {
            "dimension": dimension,
            "box_count": boxes,
            "total_edges": edges,
            "total_tail_rows": tail_rows,
            "majorant_constants": [str(value) for value in constants],
            "finite_scalar_dominance": True,
            "conditional_norm_transfer": True,
            "maximum_scalar_ratio": str(max_scalar_ratio),
            "maximum_operator_ratio": str(max_operator_ratio),
            "operator_norm_of_actual_q3_terms": False,
            "q3lock_commutator_identification": False,
            "history_tail_closed": False,
            "weighted_operator_form_closed": False,
            "common_core_closed": False,
            "common_alpha_closed": False,
            "exhaustion_cauchy_closed": False,
            "physical_empty_closed": False,
            "continuum_closed": False,
            "pre_a_closed": False,
            "sector_a_closed": False,
        },
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else ROOT / output
    atomic_json(destination, payload)
    print(f"R-445 INDEPENDENT {payload['verdict']} {checks}/{checks} boxes={boxes} edges={edges} tail_rows={tail_rows}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_CONDITIONAL_WEIGHTED_NORM_TRANSFER_CONTROL"
        assert payload["derived"]["conditional_norm_transfer"] is True
        print("R-445 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
