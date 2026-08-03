#!/usr/bin/env python3
"""Integrated verifier for PA-C0-DYNAMICAL-COMPLETION-NOGO-v0."""

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


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0-DYNAMICAL-COMPLETION-NOGO-v0"
SLUG = "pre-a-c0-dynamical-completion-underdetermination"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
PRIMARY = REPO / "codes/foundations/pre_a_c0_dynamical_completion_underdetermination.py"
INDEPENDENT = (
    REPO
    / "codes/foundations/pre_a_c0_dynamical_completion_underdetermination_independent.py"
)
MANIFEST = REPO / "strategy/pre-a-c0-dynamical-completion-underdetermination-manifest.json"
NOTE = REPO / "strategy/pre-a-c0-dynamical-completion-underdetermination-certificate-260803.md"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-c0-dynamical-completion-underdetermination/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-independent-pre-a-c0-dynamical-completion-underdetermination/result.json"
)
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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

    for path in (PRIMARY, INDEPENDENT, MANIFEST, NOTE, STORED_PRIMARY, STORED_INDEPENDENT):
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "authority",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-pa-c0-dynamics-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
    stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))
    for label, stored, fresh in (
        ("primary", stored_primary, primary),
        ("independent", stored_independent, independent),
    ):
        check(
            f"stored {label} artifact equals fresh child output",
            stored == fresh,
            stored == fresh,
            True,
            "stored_artifact_integrity",
        )

    for label, actual in (
        ("primary", primary["candidate_id"]),
        ("independent", independent["candidate_id"]),
        ("manifest", manifest["candidate_id"]),
    ):
        check(
            f"{label} candidate id",
            actual == CANDIDATE_ID,
            actual,
            CANDIDATE_ID,
            "identity",
        )

    primary_exact = primary["exact_results"]
    independent_exact = independent["shared_exact_results"]
    exact_oracles = {
        "same static equilibria and Hessian": (
            primary_exact["same_static_equilibria_and_hessian"],
            independent_exact["same_static_equilibria_and_hessian"],
            True,
        ),
        "gradient Gaussian exponent": (
            primary_exact["pa_m2_gradient_dynamic_exponent"],
            independent_exact["pa_m2_gradient_dynamic_exponent"],
            2,
        ),
        "inertial Gaussian exponent": (
            primary_exact["pa_m2_inertial_dynamic_exponent"],
            independent_exact["pa_m2_inertial_dynamic_exponent"],
            1,
        ),
        "global PA-M2 limiting speed": (
            primary_exact["pa_m2_global_limiting_speed"],
            not independent_exact["pa_m2_ultraviolet_group_speed_unbounded"],
            False,
        ),
    }
    for name, (left, right, expected) in exact_oracles.items():
        check(
            f"primary-independent exact oracle: {name}",
            left == right == expected,
            (left, right),
            (expected, expected),
            "cross_implementation",
        )

    check(
        "independent two-copy relative-speed fixture",
        independent_exact["two_copy_relative_speed_squared_fixture"] == "4",
        independent_exact["two_copy_relative_speed_squared_fixture"],
        "4",
        "cross_implementation",
    )
    check(
        "q-zero exponent boundary",
        (
            primary_exact["q_zero_gaussian_exponents"]["gradient"],
            primary_exact["q_zero_gaussian_exponents"]["inertial"],
            independent_exact["q_zero_gradient_dynamic_exponent"],
            independent_exact["q_zero_inertial_dynamic_exponent"],
        )
        == (4, 2, 4, 2),
        (
            primary_exact["q_zero_gaussian_exponents"]["gradient"],
            primary_exact["q_zero_gaussian_exponents"]["inertial"],
            independent_exact["q_zero_gradient_dynamic_exponent"],
            independent_exact["q_zero_inertial_dynamic_exponent"],
        ),
        (4, 2, 4, 2),
        "cross_implementation",
    )

    for label, payload in (("primary", primary), ("independent", independent)):
        assertion_count = payload["assertions"]
        check(
            f"{label} assertions all pass",
            assertion_count["passed"] == assertion_count["total"] > 0,
            assertion_count["passed"],
            assertion_count["total"],
            "execution",
        )

    required_scope = {
        "static_data_map_noninjective": True,
        "static_functional_selects_kinetic_law": False,
        "inertial_speed_is_inserted": True,
        "z_is_linearized_and_gapless_only": True,
        "finite_torus_z_requires_limit": True,
        "pa_m2_cone_is_ir_only": True,
        "time_orientation_derived": False,
        "dynamical_exponent_uniquely_derived": False,
        "physical_speed_derived": False,
        "global_causal_structure_derived": False,
        "c0_branch_selected": False,
        "pa_m2_invalidated": False,
        "physical_time_and_causal_emergence": False,
        "pre_a_complete": False,
    }
    for key, expected in required_scope.items():
        values = (
            primary["scope"][key],
            independent["scope"][key],
            manifest["scope"][key],
        )
        check(
            f"scope pinned across all authorities: {key}",
            all(value is expected for value in values),
            values,
            (expected, expected, expected),
            "scope",
        )

    check(
        "manifest excludes a Schrodinger branch from the core theorem",
        "not used in the core theorem" in manifest["dynamical_completions"]["schrodinger_branch"],
        manifest["dynamical_completions"]["schrodinger_branch"],
        "contains explicit exclusion from the core theorem",
        "scope",
    )

    note_text = NOTE.read_text(encoding="utf-8")
    for phrase in (
        "commensurate volume family",
        "Gaussian, tree-level, gapless-boundary exponents",
        "unbounded as `R->infinity`",
        "C0-A",
        "C0-B",
        "does not invalidate the PA-M2 variational theorem",
        "Pre-A is therefore not complete",
        "A cone may still emerge",
    ):
        check(
            f"certificate contains required scope boundary: {phrase}",
            phrase in note_text,
            phrase in note_text,
            True,
            "scope",
        )

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "verdict": "PASS: the static-to-dynamics map is non-injective in the declared exact witnesses; PA-M2's z=1 node slope requires inserted inertia and is not a global causal cone; C0 and Pre-A remain open",
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
            "integrator": len(rows),
            "combined": primary["assertions"]["passed"]
            + independent["assertions"]["passed"]
            + len(rows),
        },
        "authority_hashes": {
            str(PRIMARY.relative_to(REPO)).replace("\\", "/"): sha256(PRIMARY),
            str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"): sha256(INDEPENDENT),
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(MANIFEST),
            str(NOTE.relative_to(REPO)).replace("\\", "/"): sha256(NOTE),
            str(STORED_PRIMARY.relative_to(REPO)).replace("\\", "/"): sha256(STORED_PRIMARY),
            str(STORED_INDEPENDENT.relative_to(REPO)).replace("\\", "/"): sha256(STORED_INDEPENDENT),
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
        f"PASS {payload['child_assertions']['combined']}/"
        f"{payload['child_assertions']['combined']} | integrated {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
