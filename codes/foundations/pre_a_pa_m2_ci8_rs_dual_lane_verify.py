#!/usr/bin/env python3
"""Integrated verifier for the PA-M2-CI8-RS-v0 dual-lane package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M2-CI8-RS-v0"
SLUG = "pre-a-pa-m2-ci8-rs-dual-lane"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
PRIMARY = REPO / "codes/foundations/pre_a_pa_m2_ci8_rs_dual_lane.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_pa_m2_ci8_rs_dual_lane_independent.py"
MANIFEST = REPO / "strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json"
NOTE = REPO / "strategy/pre-a-dual-lane-horizon-origin-proof-programme-260803.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-integrated-{SLUG}"
    / "result.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def run_child(script: Path, output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"child failed: {script}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return json.loads(output.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": actual,
                "expected": expected,
                "group": group,
            }
        )

    for path in (PRIMARY, INDEPENDENT, MANIFEST, NOTE):
        check(f"required file exists: {path.name}", path.is_file(), path.is_file(), True, "authority")

    with tempfile.TemporaryDirectory(prefix="tect-pa-m2-ci8-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("primary candidate id", primary["candidate_id"] == CANDIDATE_ID, primary["candidate_id"], CANDIDATE_ID, "identity")
    check(
        "independent candidate id",
        independent["candidate_id"] == CANDIDATE_ID,
        independent["candidate_id"],
        CANDIDATE_ID,
        "identity",
    )
    check("manifest candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")

    shared = independent["shared_exact_results"]
    exact = primary["exact_results"]
    comparisons = {
        "node count": (exact["node_count"], shared["node_count"]),
        "cosine second moment": (exact["cosine_second_moment"], shared["cosine_second_moment"]),
        "cosine fourth moment": (exact["cosine_fourth_moment"], shared["cosine_fourth_moment"]),
        "stationary mean-square coefficient": (
            str(exact["minimizer_mean_square_upper_bound"]).replace("-r/g", "1"),
            str(shared["mean_square_upper_coefficient"]),
        ),
        "stable or critical Gaussian Lyapunov exponent": (
            str(exact["gaussian_lyapunov_exponent"]),
            str(shared["stable_or_critical_gaussian_lyapunov_exponent"]),
        ),
        "CI8 morphology minimizer": (
            exact["ci8_kernel_morphology_minimizer"].startswith("one antipodal node pair"),
            shared["ci8_kernel_morphology_minimizer"].startswith("one antipodal node pair"),
        ),
        "single-null completeness": (
            primary["scope"]["single_null_sheet_complete_initial_data"],
            shared["single_null_sheet_complete_initial_data"],
        ),
        "double-null toy reconstruction": (
            primary["scope"]["double_null_toy_reconstruction"],
            shared["double_null_polynomial_reconstruction"],
        ),
    }
    for name, (left, right) in comparisons.items():
        check(f"primary-independent {name}", left == right, left, right, "cross_implementation")

    check(
        "primary assertion count is nonzero",
        primary["assertions"]["passed"] == primary["assertions"]["total"] > 0,
        primary["assertions"],
        "all pass",
        "execution",
    )
    check(
        "independent assertion count is nonzero",
        independent["assertions"]["passed"] == independent["assertions"]["total"] > 0,
        independent["assertions"],
        "all pass",
        "execution",
    )
    check(
        "manifest forbids thermodynamic promotion",
        manifest["scope"]["thermodynamic_phase_transition"] is False,
        manifest["scope"]["thermodynamic_phase_transition"],
        False,
        "scope",
    )
    check(
        "manifest forbids nonlinear-chaos promotion",
        manifest["scope"]["nonlinear_quantum_chaos"] is False,
        manifest["scope"]["nonlinear_quantum_chaos"],
        False,
        "scope",
    )
    check(
        "manifest forbids cyclic-cosmology promotion",
        manifest["scope"]["cyclic_cosmology"] is False,
        manifest["scope"]["cyclic_cosmology"],
        False,
        "scope",
    )
    check(
        "manifest forbids event-horizon-origin promotion",
        manifest["scope"]["event_horizon_origin_selected"] is False,
        manifest["scope"]["event_horizon_origin_selected"],
        False,
        "scope",
    )
    check(
        "manifest records one-null-sheet insufficiency",
        manifest["scope"]["single_null_sheet_complete_initial_data"] is False,
        manifest["scope"]["single_null_sheet_complete_initial_data"],
        False,
        "scope",
    )
    check(
        "manifest permits only the double-null toy reconstruction",
        manifest["scope"]["double_null_toy_reconstruction"] is True
        and manifest["scope"]["gravitational_horizon_reconstruction"] is False,
        (
            manifest["scope"]["double_null_toy_reconstruction"],
            manifest["scope"]["gravitational_horizon_reconstruction"],
        ),
        (True, False),
        "scope",
    )
    check(
        "candidate family is aligned across primary and manifest",
        primary["candidate_family"] == manifest["candidate_family"],
        primary["candidate_family"],
        manifest["candidate_family"],
        "identity",
    )
    check(
        "manifest exposes the causal-structure and composition boundaries",
        manifest["scope"]["causal_structure_inserted_in_lane_h_toy"] is True
        and manifest["scope"]["lane_h_to_pa_m2_composition"] is False,
        (
            manifest["scope"]["causal_structure_inserted_in_lane_h_toy"],
            manifest["scope"]["lane_h_to_pa_m2_composition"],
        ),
        (True, False),
        "scope",
    )

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "verdict": "PASS: Lane-H scoped one-null insufficiency, Lane-F onset and kernel-restricted morphology, and the stable/critical Gaussian Lane-Q boundary reproduce independently; causal emergence, Lane-H-to-PA-M2 composition, gravitational horizon reconstruction, nonlinear chaos, and cyclic cosmology remain open",
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
            "integrator": len(rows),
            "combined": primary["assertions"]["passed"] + independent["assertions"]["passed"] + len(rows),
        },
        "authority_hashes": {
            str(PRIMARY.relative_to(REPO)).replace("\\", "/"): sha256(PRIMARY),
            str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"): sha256(INDEPENDENT),
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(MANIFEST),
            str(NOTE.relative_to(REPO)).replace("\\", "/"): sha256(NOTE),
        },
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['child_assertions']['combined']}/{payload['child_assertions']['combined']} | "
        f"integrated {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
