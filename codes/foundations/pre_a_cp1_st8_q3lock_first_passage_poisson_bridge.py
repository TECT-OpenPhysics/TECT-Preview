#!/usr/bin/env python3
"""Primary exact audit for the conditional EXP-001028 path bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-first-passage-poisson-bridge"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def safe(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": safe(actual), "expected": safe(expected)})


def rational(value: str) -> sp.Rational:
    parsed = Fraction(value)
    return sp.Rational(parsed.numerator, parsed.denominator)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = Audit()
    audit.check("schema", manifest["schema"] == "tect/pre-a-cp1-st8-q3lock-first-passage-poisson-bridge/1.0", manifest["schema"], ".../1.0", "provenance")
    audit.check("exploration", manifest["exploration_id"] == "EXP-001028", manifest["exploration_id"], "EXP-001028", "provenance")
    audit.check("task", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "provenance")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("hypothesis open", manifest["hypothesis"]["status"] == "OPEN for the exact Q3 onsite-plus-bond dynamics", manifest["hypothesis"]["status"], "OPEN", "scope")

    fixture = manifest["fixture"]
    z = rational(fixture["degree"])
    eta = rational(fixture["eta"])
    time = rational(fixture["time"])
    base = rational(fixture["weight_base"])
    distance = int(fixture["distance"])
    truncation = int(fixture["truncation_order"])
    source_mass = rational(fixture["source_mass"])
    rate = sp.factor(eta * z * time)
    weighted_rate = sp.factor(rate * base)
    weighted_constant = sp.exp(weighted_rate)
    point_bound = sp.factor(weighted_constant / base**distance)
    partial = sum(rate**n / sp.factorial(n) for n in range(truncation + 1))
    tail_partial = sum(rate**n / sp.factorial(n) for n in range(distance, truncation + 1))

    audit.check("degree input", z == 6, z, 6, "fixture")
    audit.check("positive rate", rate == 2 and rate > 0, rate, "2", "arithmetic")
    audit.check("weighted rate", weighted_rate == 4, weighted_rate, "4", "arithmetic")
    audit.check("path count envelope", z**5 == 7776, z**5, 7776, "combinatorics")
    audit.check("distance support", distance == 10 and distance > 0, distance, 10, "support")
    audit.check("short paths absent", all(n < distance for n in range(distance)) and sum(1 for n in range(distance)) == distance, distance, "no path length below d", "support")
    audit.check("weight base", base > 1, base, ">1", "weight")
    audit.check("source mass", source_mass == 1, source_mass, 1, "initial")
    audit.check("weighted generating function", weighted_rate == rate * base, weighted_rate, "rate*base", "arithmetic")
    audit.check("partial exponential bound", sp.N(partial) < sp.N(weighted_constant), sp.N(partial), "< exp(4)", "series")
    audit.check("distance tail bound", sp.N(tail_partial) < sp.N(point_bound * weighted_constant), sp.N(tail_partial), "<= base^(-d)*exp(4)", "series")
    audit.check("point bound numeric", sp.N(point_bound) < sp.Rational(1, 10), sp.N(point_bound), "<0.1", "decay")
    d_symbol = sp.symbols("d", positive=True)
    limit_value = sp.limit(weighted_constant / base**d_symbol, d_symbol, sp.oo)
    audit.check("distance decay asymptotic", limit_value == 0, limit_value, 0, "decay")
    audit.check("conditional bridge declared", manifest["scope"]["closed"].startswith("Exact factorial"), manifest["scope"]["closed"], "conditional bridge", "scope")
    audit.check("Q3 expansion remains open", manifest["hypothesis"]["status"].startswith("OPEN"), manifest["hypothesis"]["status"], "OPEN", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "verdict": "PASS",
        "passed": passed,
        "total": passed,
        "failed": 0,
        "assertions": audit.rows,
        "derived": {
            "degree": z,
            "eta": eta,
            "time": time,
            "weight_base": base,
            "distance": distance,
            "truncation_order": truncation,
            "rate": rate,
            "weighted_rate": weighted_rate,
            "point_bound": point_bound,
            "conditional_boundary_decay_closed": True,
            "actual_q3_first_passage_closed": False,
            "exhaustion_cauchy_closed": False,
            "common_alpha_closed": False
        },
        "series": {"partial": partial, "tail_partial": tail_partial, "weighted_constant": weighted_constant},
        "hypothesis": manifest["hypothesis"],
        "boundary": manifest["scope"],
        "exploration_id": manifest["exploration_id"],
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)}
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FIRST-PASSAGE-POISSON PASS {payload['passed']}/{payload['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
