#!/usr/bin/env python3
"""Integrated audit for the Q3LOCK common-derivation weighted-energy split."""

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
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_common_local_derivation_weighted_energy_route_split.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_common_local_derivation_weighted_energy_route_split_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-manifest.json"
PRIMARY_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-primary-pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split/result.json"
INDEPENDENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-independent-pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split/result.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-10-integrated-pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split/result.json"


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
    process = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(output.read_text(encoding="utf-8")), process.stdout.strip().splitlines()[0]


def run() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    independent_imports = imports(INDEPENDENT)
    forbidden = {"sympy", "numpy", PRIMARY.stem}
    audit.check("independent import firewall", not (forbidden & independent_imports), sorted(forbidden & independent_imports), [], "independence")

    with tempfile.TemporaryDirectory(prefix="tect-energy-split-") as directory:
        temporary = Path(directory)
        primary, primary_stdout = execute(PRIMARY, temporary / "primary.json")
        independent, independent_stdout = execute(INDEPENDENT, temporary / "independent.json")

    audit.check("primary fresh execution", primary_stdout.startswith("PASS "), primary_stdout, "PASS *", "freshness")
    audit.check("independent fresh execution", primary_stdout.startswith("PASS ") and independent_stdout.startswith("PASS "), independent_stdout, "PASS *", "freshness")
    stored_primary = json.loads(PRIMARY_RESULT.read_text(encoding="utf-8"))
    stored_independent = json.loads(INDEPENDENT_RESULT.read_text(encoding="utf-8"))
    audit.check("primary stored result fresh", primary == stored_primary, primary["summary"], stored_primary["summary"], "freshness")
    audit.check("independent stored result fresh", independent == stored_independent, independent["assertions"]["passed"], stored_independent["assertions"]["passed"], "freshness")
    audit.check("common result id", primary["result_id"] == independent["result_id"] == manifest["result_id"], [primary["result_id"], independent["result_id"]], manifest["result_id"], "cross")

    primary_q3 = primary["derived"]
    independent_q3 = independent["derived"]["q3"]
    audit.check("Q3 vertex agreement", primary_q3["Q3_vertices"] == independent_q3["vertices"], primary_q3["Q3_vertices"], independent_q3["vertices"], "cross")
    audit.check("Q3 edge agreement", primary_q3["Q3_edges"] == independent_q3["edges"], primary_q3["Q3_edges"], independent_q3["edges"], "cross")
    audit.check("Q3 degree agreement", primary_q3["Q3_degrees"] == independent_q3["degrees"], primary_q3["Q3_degrees"], independent_q3["degrees"], "cross")
    audit.check("weighted degree agreement", primary_q3["weighted_degree"] == independent["derived"]["weighted_energy"]["nearest_neighbour_degree"], primary_q3["weighted_degree"], independent["derived"]["weighted_energy"]["nearest_neighbour_degree"], "cross")
    audit.check("coercivity coefficient independent", independent["derived"]["coercivity"]["W4_lower_coefficient_per_g"] == "1/32", independent["derived"]["coercivity"]["W4_lower_coefficient_per_g"], "1/32", "cross")
    audit.check("sharp current saturation independent", independent["derived"]["sharp_form_saturation"]["current_absolute"] == independent["derived"]["sharp_form_saturation"]["energy"], independent["derived"]["sharp_form_saturation"], "equality fixture", "cross")

    audit.check("scope agreement", independent["scope"] == manifest["scope"], independent["scope"], manifest["scope"], "scope")
    audit.check("common alpha remains open", primary_q3["common_alpha_closed"] is False and manifest["scope"]["common_state_independent_real_time_automorphism"] is False, False, False, "scope")
    audit.check("next gate exact", independent["next_gate"] == manifest["next_exact_gate"]["gate"], independent["next_gate"], manifest["next_exact_gate"]["gate"], "scope")
    audit.check("two negatives registered in package", len(manifest["negative_ids"]) == 2, manifest["negative_ids"], "two scoped route obstructions", "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-integrated-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "child_summaries": {
            "primary": primary["summary"],
            "independent": {"passed": independent["assertions"]["passed"], "failed": 0, "total": independent["assertions"]["total"]},
        },
        "derived": {
            "Q3_vertices": primary_q3["Q3_vertices"],
            "Q3_edges": primary_q3["Q3_edges"],
            "Q3_degrees": primary_q3["Q3_degrees"],
            "quartic_lower_coefficient": "1/32",
            "weighted_degree": primary_q3["weighted_degree"],
            "common_alpha_closed": False,
            "next_gate": independent["next_gate"],
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
