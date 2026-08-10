#!/usr/bin/env python3
"""Integrated freshness and independence audit for the Pre-A Round-1 triage."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
PRIMARY = REPO / "codes/foundations/pre_a_round1_frozen_quadratic_causal_admission_triage.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_round1_frozen_quadratic_causal_admission_triage_independent.py"
MANIFEST = REPO / "strategy/pre-a-round1-frozen-quadratic-causal-admission-triage-manifest.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-primary-pre-a-round1-frozen-quadratic-causal-admission-triage/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-independent-pre-a-round1-frozen-quadratic-causal-admission-triage/result.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-integrated-pre-a-round1-frozen-quadratic-causal-admission-triage/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def execute(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    run = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(output.read_text(encoding="utf-8")), run.stdout.strip().splitlines()[-1]


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    forbidden = {"sympy", "numpy", PRIMARY.stem}
    independent_imports = imports(INDEPENDENT)
    audit.check("independent implementation import firewall", not (forbidden & independent_imports), sorted(forbidden & independent_imports), [], "independence")

    with tempfile.TemporaryDirectory(prefix="tect-prea-round1-") as directory:
        temporary = Path(directory)
        primary, primary_stdout = execute(PRIMARY, temporary / "primary.json")
        independent, independent_stdout = execute(INDEPENDENT, temporary / "independent.json")

    audit.check("primary execution", primary_stdout.startswith("PASS "), primary_stdout, "PASS *", "freshness")
    audit.check("independent execution", independent_stdout.startswith("PASS "), independent_stdout, "PASS *", "freshness")
    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check("primary stored result fresh", primary == stored_primary, primary["summary"], stored_primary["summary"], "freshness")
    audit.check("independent stored result fresh", independent == stored_independent, independent["summary"], stored_independent["summary"], "freshness")
    audit.check("common result id", primary["result_id"] == independent["result_id"] == manifest["result_id"], [primary["result_id"], independent["result_id"]], manifest["result_id"], "cross")
    for key in ("M2_node_hessian", "M2_speed_squared", "round1_outcome", "visible_target_interval"):
        audit.check(f"derived agreement {key}", primary["derived"][key] == independent["derived"][key], primary["derived"][key], independent["derived"][key], "cross")
    audit.check("primary no validation credit", primary["derived"]["validation_credit"] is False, False, False, "scope")
    audit.check("primary survivors empty", primary["derived"]["derived_survivors"] == [], primary["derived"]["derived_survivors"], [], "scope")
    audit.check("parent gate remains open", manifest["round1_verdict"]["freeze_gate_closed"] is False, False, False, "scope")
    audit.check("Pre-A remains open", manifest["round1_verdict"]["pre_a_exit_conditions_met"] is False, False, False, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-round1-frozen-quadratic-causal-admission-triage-integrated-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "child_summaries": {"primary": primary["summary"], "independent": independent["summary"]},
        "derived": {
            "M2_node_hessian": primary["derived"]["M2_node_hessian"],
            "M2_speed_squared": primary["derived"]["M2_speed_squared"],
            "round1_outcome": primary["derived"]["round1_outcome"],
            "visible_target_interval": primary["derived"]["visible_target_interval"],
            "validation_credit": False,
            "derived_survivors": [],
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
