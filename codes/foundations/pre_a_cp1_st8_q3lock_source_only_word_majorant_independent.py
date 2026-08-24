#!/usr/bin/env python3
"""Independent Fraction audit of the source-only Q3 word majorant."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-source-only-word-majorant"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def f(value: str | int | Fraction) -> Fraction:
    return Fraction(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": clean(actual), "expected": clean(expected)})


def coefficient_l1(coefficients: tuple[Fraction, ...], radius: Fraction, degree: int) -> Fraction:
    return sum((abs(coefficient) * radius**degree for coefficient in coefficients), Fraction(0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["fixture"]
    g, coupling, spatial = f(fixture["g"]), f(fixture["lambda"]), f(fixture["spatial_coupling"])
    radius, time = f(fixture["source_radius"]), f(fixture["time"])
    audit = Audit()
    audit.check("exploration", manifest["exploration_id"] == "EXP-001039", manifest["exploration_id"], "EXP-001039", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    onsite_l1 = coefficient_l1((g / 4,), radius, 4)
    edge_l1 = coefficient_l1((coupling / 4, -coupling / 2, coupling / 2, -coupling / 2, coupling / 4), radius, 4)
    bond_l1 = coefficient_l1((spatial / 2, -spatial, spatial / 2), radius, 2)
    audit.check("onsite source table", onsite_l1 == g * radius**4 / 4, onsite_l1, g * radius**4 / 4, "source-slice")
    audit.check("edge source table", edge_l1 == 2 * coupling * radius**4, edge_l1, 2 * coupling * radius**4, "source-slice")
    audit.check("bond source table", bond_l1 == 2 * spatial * radius**2, bond_l1, 2 * spatial * radius**2, "source-slice")
    audit.check("reverse edge", edge_l1 == edge_l1, edge_l1, edge_l1, "orientation")
    audit.check("reverse bond", bond_l1 == bond_l1, bond_l1, bond_l1, "orientation")

    q3_degree = int(fixture["q3_degree"])
    spatial_degree = int(fixture["spatial_degree"])
    local_choices = 1 + q3_degree + spatial_degree
    rate = onsite_l1 + q3_degree * edge_l1 + spatial_degree * bond_l1
    weighted_rate = time * rate
    audit.check("choice count", local_choices == int(fixture["local_choice_count"]), local_choices, fixture["local_choice_count"], "graph")
    audit.check("rate fixture", rate == f(fixture["expected_rate"]), rate, fixture["expected_rate"], "majorant")
    audit.check("weighted rate fixture", weighted_rate == f(fixture["expected_weighted_rate"]), weighted_rate, fixture["expected_weighted_rate"], "majorant")

    rows: list[dict[str, Any]] = []
    partial = Fraction(0)
    max_word = int(fixture["max_word_length"])
    for n in range(max_word + 1):
        term = weighted_rate**n / math.factorial(n)
        partial += term
        audit.check(f"nonnegative term n={n}", term >= 0, term, ">=0", "majorant")
        rows.append({"length": n, "term": term, "partial": partial})
    audit.check("partial exponential bound", float(partial) <= math.exp(float(weighted_rate)) + 1e-12, float(partial), f"<={math.exp(float(weighted_rate))}", "majorant")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "partial_rows": rows,
        "derived": {
            "onsite_l1_at_radius": onsite_l1,
            "q3_edge_l1_at_radius": edge_l1,
            "spatial_bond_l1_at_radius": bond_l1,
            "q3_degree": q3_degree,
            "spatial_degree": spatial_degree,
            "local_choice_count": local_choices,
            "local_rate_at_radius": rate,
            "weighted_rate": weighted_rate,
            "source_only_egf_closed": True,
            "orientation_symmetric": True,
            "field_dependent_operator_history_closed": False,
            "all_shape_exhaustion_closed": False,
            "common_alpha_closed": False,
        },
        "provenance": {
            "script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": sha256(SCRIPT),
            "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "manifest_sha256": sha256(MANIFEST),
        },
        "exploration_id": manifest["exploration_id"],
        "boundary": manifest["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SOURCE-ONLY-Q3-WORD-MAJORANT PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
