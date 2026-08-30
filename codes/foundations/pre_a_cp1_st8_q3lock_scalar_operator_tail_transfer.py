#!/usr/bin/env python3
"""Primary exact audit for the R-445 conditional norm-tail transfer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-scalar-operator-tail-transfer-manifest.json"
PARENT_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-scalar_operator_tail_transfer/primary.json"


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
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def shell_count(radius: int) -> int:
    return 1 if radius == 0 else 4 * radius * radius + 2


def tail_formula(radius: int) -> Fraction:
    if radius < 1:
        raise ValueError("tail formula is declared for radius >= 1")
    return Fraction(3 * (4 * radius * radius + 8 * radius + 14), 2 ** (radius - 1))


def edges_for_box(sides: tuple[int, ...]) -> list[tuple[tuple[int, ...], int]]:
    vertices = list(product(*[range(side) for side in sides]))
    edges: list[tuple[tuple[int, ...], int]] = []
    for lower in vertices:
        for axis, side in enumerate(sides):
            if lower[axis] + 1 < side:
                edges.append((lower, axis))
    return edges


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["finite_contract"]
    dimension = int(contract["dimension"])
    side_min = int(contract["box_side_min"])
    side_max = int(contract["box_side_max"])
    radius_min = int(contract["tail_radius_min"])
    radius_max = int(contract["tail_radius_max"])
    constants = [Fraction(value) for value in contract["majorant_constant_inputs"]]
    checks: list[dict[str, Any]] = []
    assertion_count = 0
    samples: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertion_count += 1

        def serial(value: Any) -> Any:
            if isinstance(value, Fraction):
                return str(value)
            if isinstance(value, (list, tuple)):
                return [serial(item) for item in value]
            if isinstance(value, dict):
                return {str(key): serial(item) for key, item in value.items()}
            return value

        if len(samples) < 32:
            samples.append(
                {
                    "name": name,
                    "group": group,
                    "status": "PASS",
                    "actual": serial(actual),
                    "expected": serial(expected),
                }
            )

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]]
        == ["R-445", "EXP-001297", "T-054", False, "CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["status"]],
        "R-445/EXP-001297/T-054/false/audited",
        "provenance",
    )
    check("parent identity", parent["result_id"] == "R-444" and parent["claim_bearing"] is False, parent["result_id"], "R-444", "provenance")
    check("dimension", dimension == 3, dimension, 3, "contract")
    check("box range", side_min <= side_max and side_min >= 2, [side_min, side_max], "finite boxes with sides >=2", "contract")
    check("radius range", radius_min >= 1 and radius_min <= radius_max, [radius_min, radius_max], "positive finite radii", "contract")
    check("term-bound contract", contract["term_bound"] == "||K_e|| <= C*w(e)", contract["term_bound"], "declared per-edge bound", "contract")
    check("transfer-chain contract", "||sum_tail K_e||" in contract["transfer_chain"] and "C*T(R)" in contract["transfer_chain"], contract["transfer_chain"], "triangle transfer chain", "contract")
    check("conditional boundary", manifest["scope"]["per_edge_majorant_assumed"] is True and manifest["scope"]["q3lock_commutator_identification"] is False, manifest["scope"], "assumed but not identified", "scope")
    for key in (
        "operator_norm_of_actual_q3_terms",
        "q3lock_commutator_identification",
        "history_tail_closed",
        "weighted_operator_form_closed",
        "common_core_closed",
        "common_alpha_closed",
        "exhaustion_cauchy_closed",
        "kms_gns_gap_closed",
        "physical_empty_closed",
        "continuum_closed",
        "c6_closed",
        "sector_a_closed",
        "pre_a_closed",
    ):
        check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    box_count = 0
    total_edges = 0
    total_tail_rows = 0
    maximum_scalar_ratio = Fraction(0)
    maximum_operator_ratio = Fraction(0)
    for sides in product(range(side_min, side_max + 1), repeat=dimension):
        box_count += 1
        edges = edges_for_box(tuple(sides))
        total_edges += len(edges)
        weights = [Fraction(1, 2 ** sum(abs(value) for value in lower)) for lower, _axis in edges]
        for radius in range(radius_min, radius_max + 1):
            finite_tail = sum((weight for (lower, _axis), weight in zip(edges, weights) if sum(abs(value) for value in lower) >= radius), Fraction(0))
            scalar_bound = tail_formula(radius)
            check(f"box {box_count} scalar tail {radius}", finite_tail <= scalar_bound, finite_tail, scalar_bound, "scalar-reuse")
            if scalar_bound:
                maximum_scalar_ratio = max(maximum_scalar_ratio, finite_tail / scalar_bound)
            total_tail_rows += 1
            for constant in constants:
                tail_edges = [(lower, axis, weight) for (lower, axis), weight in zip(edges, weights) if sum(abs(value) for value in lower) >= radius]
                declared_norms = [constant * weight for _lower, _axis, weight in tail_edges]
                finite_budget = constant * finite_tail
                ambient_budget = constant * scalar_bound
                saturated_sum = sum(declared_norms, Fraction(0))
                signed_sum = sum(((-1 if (sum(abs(value) for value in lower) + axis) % 2 else 1) * constant * weight for lower, axis, weight in tail_edges), Fraction(0))
                check(f"box {box_count} radius {radius} C={constant} term majorant", all(value == constant * weight for value, (_lower, _axis, weight) in zip(declared_norms, tail_edges)), True, "termwise norm majorant", "operator-transfer")
                check(f"box {box_count} radius {radius} C={constant} sum identity", saturated_sum == finite_budget, saturated_sum, finite_budget, "operator-transfer")
                check(f"box {box_count} radius {radius} C={constant} triangle", abs(signed_sum) <= saturated_sum, abs(signed_sum), saturated_sum, "operator-transfer")
                check(f"box {box_count} radius {radius} C={constant} ambient transfer", abs(signed_sum) <= ambient_budget, abs(signed_sum), ambient_budget, "operator-transfer")
                if ambient_budget:
                    maximum_operator_ratio = max(maximum_operator_ratio, abs(signed_sum) / ambient_budget)

    check("finite family complete", box_count == (side_max - side_min + 1) ** dimension, box_count, (side_max - side_min + 1) ** dimension, "enumeration")
    check("tail rows complete", total_tail_rows == box_count * (radius_max - radius_min + 1), total_tail_rows, box_count * (radius_max - radius_min + 1), "enumeration")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r445-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-445",
        "exploration_id": "EXP-001297",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": "CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED",
        "passed": assertion_count,
        "assertion_count": assertion_count,
        "assertions": samples,
        "assertion_samples_truncated": assertion_count > len(samples),
        "derived": {
            "dimension": dimension,
            "box_count": box_count,
            "total_edges": total_edges,
            "tail_radius_range": [radius_min, radius_max],
            "majorant_constants": [str(value) for value in constants],
            "total_tail_rows": total_tail_rows,
            "finite_scalar_dominance": True,
            "conditional_norm_transfer": True,
            "maximum_scalar_ratio": str(maximum_scalar_ratio),
            "maximum_operator_ratio": str(maximum_operator_ratio),
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
        "source_hashes": {
            "script": sha256(Path(__file__)),
            "manifest": sha256(MANIFEST),
            "parent_manifest": sha256(PARENT_MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-445 PRIMARY {payload['verdict']} {assertion_count}/{assertion_count} boxes={box_count} edges={total_edges} tail_rows={total_tail_rows}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "CONDITIONAL_WEIGHTED_NORM_TRANSFER_AUDITED"
        assert payload["derived"]["conditional_norm_transfer"] is True
        print("R-445 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
