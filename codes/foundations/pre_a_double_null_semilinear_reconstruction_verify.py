#!/usr/bin/env python3
"""Integrated verifier for the PA-H1-DNKG4-v0 Lane-H bridge."""

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
CANDIDATE_ID = "PA-H1-DNKG4-v0"
SLUG = "pre-a-double-null-semilinear-reconstruction"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
PRIMARY = REPO / "codes/foundations/pre_a_double_null_semilinear_reconstruction.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_double_null_semilinear_reconstruction_independent.py"
MANIFEST = REPO / "strategy/pre-a-double-null-semilinear-reconstruction-manifest.json"
NOTE = REPO / "strategy/pre-a-double-null-semilinear-reconstruction-certificate-260803.md"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-double-null-semilinear-reconstruction/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-independent-pre-a-double-null-semilinear-reconstruction/result.json"
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

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for path in (PRIMARY, INDEPENDENT, MANIFEST, NOTE, STORED_PRIMARY, STORED_INDEPENDENT):
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "authority",
        )

    with tempfile.TemporaryDirectory(prefix="tect-pa-h1-dnkg4-") as temporary:
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

    exact = primary["exact_results"]
    shared = independent["shared_exact_results"]
    # These exact rationals are labelled test oracles for the declared sample
    # U=V=1/4, kappa=g=R=1, M=1/2; they are not physical inputs.
    fixture_oracles = {
        "sample self-map value": (
            str(exact["sample_self_map_value"]),
            str(shared["sample_self_map_value"]),
            "5/8",
        ),
        "sample Lipschitz constant": (
            str(exact["sample_lipschitz_constant"]),
            str(shared["sample_lipschitz_constant"]),
            "1/4",
        ),
        "sample stability factor": (
            str(exact["sample_stability_factor"]),
            str(shared["sample_stability_factor"]),
            "4/3",
        ),
    }
    for name, (left, right, oracle) in fixture_oracles.items():
        check(
            f"primary-independent {name}",
            left == right == oracle,
            (left, right),
            (oracle, oracle),
            "cross_implementation",
        )

    comparisons = {
        "global linear reconstruction": (
            primary["scope"]["global_linear_rectangle_reconstruction"],
            shared["global_linear_rectangle_reconstruction"],
            manifest["scope"]["global_linear_rectangle_reconstruction"],
            True,
        ),
        "linear uniqueness and stability": (
            primary["scope"]["linear_uniqueness_and_stability"],
            shared["linear_uniqueness"],
            manifest["scope"]["linear_uniqueness_and_stability"],
            True,
        ),
        "classical state map": (
            primary["scope"]["classical_state_output"],
            shared["classical_slice_state_map"],
            manifest["scope"]["classical_state_output"],
            True,
        ),
        "massive symplectic current and algebraic state transport support": (
            primary["scope"]["linear_algebraic_boundary_state_transport"],
            shared["massive_symplectic_current_identity"]
            and shared["massless_symplectic_boundary_to_slice_fixture"],
            manifest["scope"]["linear_algebraic_boundary_state_transport"],
            True,
        ),
        "local semilinear reconstruction": (
            primary["scope"]["local_semilinear_reconstruction_under_explicit_gates"],
            shared["local_semilinear_reconstruction"],
            manifest["scope"]["local_semilinear_reconstruction_under_explicit_gates"],
            True,
        ),
        "Pre-A incomplete": (
            primary["scope"]["pre_a_complete"],
            shared["pre_a_complete"],
            manifest["scope"]["pre_a_complete"],
            False,
        ),
    }
    for name, (left, right, declared, expected) in comparisons.items():
        check(
            f"primary-independent-manifest {name}",
            left is expected and right is expected and declared is expected,
            (left, right, declared),
            (expected, expected, expected),
            "cross_implementation",
        )

    exact_support = {
        "Riemann-Bessel equation and axes": exact["riemann_bessel_kernel_equation_and_axes"],
        "left and right null energy-flux factors": exact[
            "left_and_right_null_energy_flux_factors"
        ]
        and shared["left_and_right_null_energy_flux_factors"],
        "massive symplectic current": exact["massive_symplectic_current_identity"]
        and shared["massive_symplectic_current_identity"],
        "injective slice map": exact["linear_state_map_injective"]
        and manifest["scope"]["linear_state_map_injective"],
    }
    for name, actual in exact_support.items():
        check(
            f"exact analytic support: {name}",
            actual is True,
            actual,
            True,
            "analytic_support",
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
        "fixed_1_plus_1_minkowski_background": True,
        "causal_structure_inserted": True,
        "global_linear_rectangle_reconstruction": True,
        "linear_uniqueness_and_stability": True,
        "local_semilinear_reconstruction_under_explicit_gates": True,
        "linear_state_map_injective": True,
        "linear_algebraic_boundary_state_transport": True,
        "selected_hadamard_state": False,
        "einstein_reconstruction": False,
        "event_horizon_identified": False,
        "high_energy_cosmic_state_derived": False,
        "cooling_map_derived": False,
        "map_to_pa_m2": False,
        "spacetime_emergence": False,
        "pre_a_complete": False,
    }
    for key, expected in required_scope.items():
        actual = manifest["scope"][key]
        check(
            f"manifest scope: {key}",
            actual is expected,
            actual,
            expected,
            "scope",
        )

    note_text = NOTE.read_text(encoding="utf-8")
    for phrase in (
        "u+v=2 tau",
        "Causal-structure circularity gate",
        "composition arrow",
        "trace-class density matrix",
        "0<2 tau<=min(U,V)",
        "||partial_x delta phi_tau||_infinity",
        "||delta Pi_tau||_infinity",
        "same `kappa,g,R`",
    ):
        check(
            f"certificate contains required boundary: {phrase}",
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
        "verdict": "PASS: fixed-background global linear characteristic reconstruction, linear state transport, and gated local semilinear reconstruction reproduce independently; causal emergence, gravity, state selection, cosmic scale, cooling, and PA-M2 composition remain open",
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
            str(STORED_PRIMARY.relative_to(REPO)).replace("\\", "/"): sha256(
                STORED_PRIMARY
            ),
            str(STORED_INDEPENDENT.relative_to(REPO)).replace("\\", "/"): sha256(
                STORED_INDEPENDENT
            ),
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
