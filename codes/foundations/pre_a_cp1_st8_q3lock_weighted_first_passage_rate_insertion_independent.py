#!/usr/bin/env python3
"""Independent Fraction audit for the EXP-001046 rate insertion."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-weighted-first-passage-rate-insertion"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def rate(coefficients: list[tuple[F, int, int, int]], source_radius: F, root_scale: F, neighbour_root: F) -> F:
    return sum(abs(coefficient) * root_scale**field_degree * neighbour_root**neighbour_degree * source_radius**source_degree for coefficient, field_degree, neighbour_degree, source_degree in coefficients)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    source_radius = F(fixture["source_radius"])
    time = F(fixture["time"])
    root_scale = F(4)
    neighbour_root = F(2)
    orientation_count = F(fixture["orientation_count"])
    degree = F(fixture["degree"])
    base = F(fixture["base"])
    distance = int(fixture["distance"])
    truncation = int(fixture["truncation_order"])
    onsite_coefficients = [(F(3, 5), 3, 0, 1), (-F(9, 10), 2, 0, 2), (F(3, 5), 1, 0, 3), (-F(3, 20), 0, 0, 4)]
    edge_coefficients = [(F(2, 7), 3, 0, 1), (-F(3, 7), 3, 1, 1), (-F(3, 7), 2, 0, 2), (F(2, 7), 3, 2, 1), (F(3, 7), 2, 1, 2), (F(2, 7), 1, 0, 3), (-F(1, 7), 3, 3, 1), (-F(1, 7), 2, 2, 2), (-F(1, 7), 1, 1, 3), (-F(1, 14), 0, 0, 4)]
    bond_coefficients = [(F(2, 3), 1, 0, 1), (-F(2, 3), 1, 1, 1), (-F(1, 3), 0, 0, 2)]
    onsite_rate = rate(onsite_coefficients, source_radius, root_scale, F(1))
    edge_rate = rate(edge_coefficients, source_radius, root_scale, neighbour_root)
    bond_rate = rate(bond_coefficients, source_radius, root_scale, neighbour_root)
    local_rate = onsite_rate + 3 * edge_rate + 6 * bond_rate
    exponent = orientation_count * local_rate * degree * base * time
    distance_factor = base ** (-distance)
    partial = F(0)
    partial_rows: list[dict[str, Any]] = []
    for n in range(truncation + 1):
        term = exponent**n / math.factorial(n)
        partial += term
        partial_rows.append({"n": n, "term": term, "partial": partial})
    boundary_partial = distance_factor * partial
    audit = Audit()
    audit.check("identity", manifest["exploration_id"] == "EXP-001046" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001046/T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("response hypothesis explicit", manifest["scope"]["factorial_first_passage_expansion_supplied"] is False, manifest["scope"]["factorial_first_passage_expansion_supplied"], False, "hypothesis")
    audit.check("rate provenance", local_rate == F(1382807, 7168), local_rate, "1382807/7168", "rate")
    audit.check("edge rate provenance", edge_rate == F(203393, 3584), edge_rate, "203393/3584", "rate")
    audit.check("bond rate provenance", bond_rate == F(97, 48), bond_rate, "97/48", "rate")
    audit.check("orientation count", orientation_count == 2, orientation_count, 2, "graph")
    audit.check("degree", degree == 6, degree, 6, "graph")
    audit.check("spatial base", base == 2 and distance_factor == F(1, 1024), [base, distance_factor], "2,1/1024", "space")
    audit.check("exact exponent", exponent == F(4148421, 896000), exponent, "4148421/896000", "bridge")
    audit.check("finite truncation order", truncation == 32 and truncation >= distance, [truncation, distance], "32>=10", "bridge")
    audit.check("partial terms nonnegative", all(row["term"] >= 0 for row in partial_rows), True, True, "bridge")
    audit.check("partial below exponential", float(partial) <= math.exp(float(exponent)) + 1e-12, float(partial), "<=exp(E)", "bridge")
    audit.check("boundary partial below exponential envelope", float(boundary_partial) <= float(distance_factor) * math.exp(float(exponent)) + 1e-12, float(boundary_partial), "<=2^-d exp(E)", "space")
    audit.check("history remains open", manifest["scope"]["actual_q3_recurrence_closed"] is False and manifest["scope"]["boundary_commutator_decay_closed"] is False, manifest["scope"], "false/false", "scope")
    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "partial_rows": partial_rows,
        "derived": {
            "onsite_rate": onsite_rate,
            "edge_rate": edge_rate,
            "bond_rate": bond_rate,
            "local_rate": local_rate,
            "orientation_count": orientation_count,
            "degree": degree,
            "base": base,
            "time": time,
            "distance": distance,
            "exponent": exponent,
            "distance_factor": distance_factor,
            "partial_order": truncation,
            "boundary_partial": boundary_partial,
            "rate_insertion_closed_conditionally": True,
            "finite_poisson_arithmetic_closed": True,
            "factorial_first_passage_expansion_supplied": False,
            "actual_q3_recurrence_closed": False,
            "boundary_commutator_decay_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT Q3-WEIGHTED-FIRST-PASSAGE-RATE PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
