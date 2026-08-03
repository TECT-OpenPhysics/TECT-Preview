#!/usr/bin/env python3
"""Integrated verifier for PA-C0A-RPTM-FS-v0."""

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
CANDIDATE_ID = "PA-C0A-RPTM-FS-v0"
SLUG = "pre-a-c0a-reflection-positive-transfer"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_c0a_reflection_positive_transfer.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_c0a_reflection_positive_transfer_independent.py"
MANIFEST = REPO / "strategy/pre-a-c0a-reflection-positive-transfer-manifest.json"
NOTE = REPO / "strategy/pre-a-c0a-reflection-positive-transfer-certificate-260803.md"
C0_NOGO_MANIFEST = REPO / "strategy/pre-a-c0-dynamical-completion-underdetermination-manifest.json"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-c0a-reflection-positive-transfer/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-independent-pre-a-c0a-reflection-positive-transfer/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-integrated-{SLUG}"
    / "result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT


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

    required_files = (
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        NOTE,
        C0_NOGO_MANIFEST,
        STORED_PRIMARY,
        STORED_INDEPENDENT,
    )
    for path in required_files:
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "authority",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    c0_nogo = json.loads(C0_NOGO_MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-pa-c0a-rptm-") as temporary:
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
    check(
        "primary-independent probability",
        primary["primitive_inputs"]["static_probability"]
        == [["1/2"], ["1/3"], ["1/6"]]
        and shared["probability"] == ["1/2", "1/3", "1/6"],
        (primary["primitive_inputs"]["static_probability"], shared["probability"]),
        ([['1/2'], ['1/3'], ['1/6']], ['1/2', '1/3', '1/6']),
        "cross_implementation",
    )
    check(
        "positive transfer alpha",
        exact["same_static_marginal_distinct_transfer_parameters"][0]
        == shared["alpha"]
        == "2/3",
        (exact["same_static_marginal_distinct_transfer_parameters"][0], shared["alpha"]),
        ("2/3", "2/3"),
        "cross_implementation",
    )
    check(
        "negative-control alpha",
        exact["negative_control_alpha"]
        == shared["negative_control_alpha"]
        == "-1/10",
        (exact["negative_control_alpha"], shared["negative_control_alpha"]),
        ("-1/10", "-1/10"),
        "cross_implementation",
    )
    check(
        "negative-control link form",
        exact["negative_control_link_form"]
        == shared["negative_control_link_form"]
        == "-1/8",
        (exact["negative_control_link_form"], shared["negative_control_link_form"]),
        ("-1/8", "-1/8"),
        "cross_implementation",
    )
    check(
        "zero-spectrum link-positive finite-log boundary",
        exact["zero_spectrum_control_spectrum"] == {"0": 2, "1": 1}
        and exact["zero_spectrum_control_link_form"] == "0"
        and shared["zero_spectrum_markov_link_positive_boundary"] is True,
        (
            exact["zero_spectrum_control_spectrum"],
            exact["zero_spectrum_control_link_form"],
            shared["zero_spectrum_markov_link_positive_boundary"],
        ),
        ({"0": 2, "1": 1}, "0", True),
        "cross_implementation",
    )
    check(
        "operator-positive non-Markov boundary",
        exact["operator_positive_non_markov_control_spectrum"]
        == {"1": 2, "2/5": 1}
        and exact["operator_positive_non_markov_negative_entry"] == "-1/10"
        and shared["operator_positive_non_markov_boundary"] is True,
        (
            exact["operator_positive_non_markov_control_spectrum"],
            exact["operator_positive_non_markov_negative_entry"],
            shared["operator_positive_non_markov_boundary"],
        ),
        ({"1": 2, "2/5": 1}, "-1/10", True),
        "cross_implementation",
    )
    check(
        "positive transfer spectrum pinned",
        exact["transfer_spectrum"] == {"1": 1, "2/3": 2}
        and shared["positive_transfer_spectrum"] == ["1", "2/3", "2/3"],
        (exact["transfer_spectrum"], shared["positive_transfer_spectrum"]),
        ({"1": 1, "2/3": 2}, ["1", "2/3", "2/3"]),
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

    required_primary_rows = {
        "transfer is stochastic",
        "static energy representative reproduces the probability",
        "detailed balance",
        "positive transfer spectrum",
        "operator-positive row-preserving control is not entrywise Markov",
        "projector logarithm reconstructs the transfer",
        "generator is weighted-self-adjoint",
        "generator spectrum and gap",
        "generator kernel is one-dimensional span of constants",
        "weighted complement is exactly the variance form",
        "spectral-projector real-time group is unitary",
        "same static probability supports distinct positive transfers",
        "same static probability supports distinct gaps",
        "site-reflection Gram fixture is positive definite",
        "link-reflection Gram fixture is positive definite",
        "zero-spectrum control is Markov and link-positive but not strictly positive",
        "negative-control transfer remains stochastic and reversible",
        "negative-control transfer has a negative eigenvalue",
        "negative-control link-reflection form is negative",
    }
    required_independent_rows = {
        "independent stochastic transfer",
        "independent operator-positive control is not entrywise Markov",
        "independent detailed balance",
        "independent transfer minimal polynomial",
        "independent complement kernel is exactly span of constants",
        "independent weighted generator form is the pair variance",
        "independent transfer spectral decomposition",
        "independent unitary projector algebra",
        "independent site-reflection Gram fixture",
        "independent link-reflection Gram fixture",
        "independent zero-spectrum control is Markov and link-positive",
        "independent negative control remains stochastic and reversible",
        "independent negative control has the pinned minimal polynomial",
        "independent negative control violates link positivity",
        "independent same static marginal has distinct positive transfers",
    }
    for label, payload, required_names in (
        ("primary", primary, required_primary_rows),
        ("independent", independent, required_independent_rows),
    ):
        actual_names = {row["name"] for row in payload["assertions"]["rows"]}
        check(
            f"{label} retains all load-bearing assertion rows",
            required_names <= actual_names,
            sorted(required_names - actual_names),
            [],
            "assertion_surface",
        )

    check(
        "independent shared theorem booleans are pinned",
        shared["positive_weighted_self_adjoint_transfer"] is True
        and shared["projector_log_generator"] is True
        and shared["one_dimensional_constant_ground_space"] is True
        and shared["site_reflection_positive_fixture"] is True
        and shared["link_reflection_positive_fixture"] is True
        and shared["same_static_marginal_distinct_positive_transfer"] is True
        and shared["operator_positive_non_markov_boundary"] is True
        and shared["pre_a_complete"] is False,
        shared,
        "all pinned theorem booleans and pre_a_complete=false",
        "cross_implementation",
    )

    required_scope = {
        "c0_a_temporal_transfer_benchmark_instantiated": True,
        "c0_a_causal_structure_instantiated": False,
        "time_order_and_spacing_inserted": True,
        "markov_entrywise_nonnegative_input": True,
        "static_functional_selects_transfer": False,
        "positive_self_adjoint_generator_reconstructed": True,
        "unitary_group_reconstructed": True,
        "site_reflection_positive": True,
        "link_reflection_requires_positive_transfer": True,
        "reversibility_alone_implies_positive_generator": False,
        "spatial_locality_derived": False,
        "causal_cone_derived": False,
        "lorentzian_signature_derived": False,
        "physical_quantum_dynamics_selected": False,
        "preferred_hadamard_state_selected": False,
        "pa_h1_state_supplied": False,
        "pa_m2_composition": False,
        "tect_c0_branch_selected": False,
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
        "C0-A benchmark respects the predecessor underdetermination theorem",
        c0_nogo["scope"]["static_functional_selects_kinetic_law"] is False
        and manifest["scope"]["static_functional_selects_transfer"] is False,
        (
            c0_nogo["scope"]["static_functional_selects_kinetic_law"],
            manifest["scope"]["static_functional_selects_transfer"],
        ),
        (False, False),
        "predecessor",
    )
    check(
        "manifest names established prior art rather than novelty",
        "established prior art" in manifest["prior_art_boundary"]
        and "not a novelty claim" in manifest["prior_art_boundary"],
        manifest["prior_art_boundary"],
        "contains established-prior-art and no-novelty boundaries",
        "scope",
    )

    note_text = NOTE.read_text(encoding="utf-8")
    for phrase in (
        "ordering, a reflection, and a positive time spacing as C0-A primitives",
        "temporal calibration rather than a full C0-A causal candidate",
        "P_xy>=0",
        "logically independent",
        "unique real self-adjoint logarithm",
        "site-reflection positivity",
        "link-reflection positivity",
        "alpha_bad=-1/10",
        "P_0=Pi_pi",
        "does not by itself select a positive ground state",
        "selection remains open and C0-B",
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
        "verdict": "PASS: the declared positive reversible transfer reconstructs a unique nonnegative self-adjoint generator and unitary group; time data are C0-A inputs and locality, a cone, PA-H1 state supply, PA-M2 composition, and Pre-A remain open",
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
            str(VERIFIER.relative_to(REPO)).replace("\\", "/"): sha256(VERIFIER),
            str(PRIMARY.relative_to(REPO)).replace("\\", "/"): sha256(PRIMARY),
            str(INDEPENDENT.relative_to(REPO)).replace("\\", "/"): sha256(INDEPENDENT),
            str(MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(MANIFEST),
            str(NOTE.relative_to(REPO)).replace("\\", "/"): sha256(NOTE),
            str(C0_NOGO_MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(C0_NOGO_MANIFEST),
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
    if arguments.self_test:
        if not STORED_INTEGRATED.is_file():
            raise AssertionError(f"stored integrated artifact missing: {STORED_INTEGRATED}")
        stored_integrated = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        json_normalized_payload = json.loads(
            json.dumps(payload, sort_keys=True, ensure_ascii=True)
        )
        if stored_integrated != json_normalized_payload:
            raise AssertionError("stored integrated artifact differs from fresh verifier output")
    else:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['child_assertions']['combined']}/"
        f"{payload['child_assertions']['combined']} | integrated {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
