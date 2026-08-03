#!/usr/bin/env python3
"""Integrated verifier for PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0."""

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
CANDIDATE_ID = "PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0"
SLUG = "pre-a-c0b-equivariant-causal-selection-nogo"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo_independent.py"
MANIFEST = REPO / "strategy/pre-a-c0b-equivariant-causal-selection-nogo-manifest.json"
NOTE = REPO / "strategy/pre-a-c0b-equivariant-causal-selection-nogo-certificate-260803.md"
C0A_MANIFEST = REPO / "strategy/pre-a-c0a-reflection-positive-transfer-manifest.json"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-primary-pre-a-c0b-equivariant-causal-selection-nogo/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / "2026-08-03-independent-pre-a-c0b-equivariant-causal-selection-nogo/result.json"
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
        C0A_MANIFEST,
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
    check(
        "stored child result paths are distinct and repo-relative",
        STORED_PRIMARY != STORED_INDEPENDENT
        and STORED_PRIMARY.is_relative_to(REPO)
        and STORED_INDEPENDENT.is_relative_to(REPO),
        (
            str(STORED_PRIMARY.relative_to(REPO)),
            str(STORED_INDEPENDENT.relative_to(REPO)),
        ),
        "two distinct repo-relative paths",
        "authority",
    )
    independent_source_text = INDEPENDENT.read_text(encoding="utf-8")
    check(
        "independent source does not import or execute primary",
        PRIMARY.stem not in independent_source_text
        and "runpy" not in independent_source_text
        and "subprocess" not in independent_source_text,
        (
            PRIMARY.stem in independent_source_text,
            "runpy" in independent_source_text,
            "subprocess" in independent_source_text,
        ),
        (False, False, False),
        "independence",
    )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    c0a_manifest = json.loads(C0A_MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-pa-c0b-selection-") as temporary:
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
    oracles = {
        "event count": (
            exact["fixture_event_count"],
            shared["fixture_event_count"],
            manifest["finite_fixture"]["event_count"],
            4,
        ),
        "symmetry group size": (
            exact["fixture_symmetry_group_size"],
            shared["symmetry_group_size"],
            manifest["finite_fixture"]["permutation_group_size"],
            24,
        ),
        "ordered pair orbit size": (
            exact["ordered_pair_orbit_size"],
            shared["ordered_pair_orbit_size"],
            manifest["finite_fixture"]["ordered_off_diagonal_pairs"],
            12,
        ),
    }
    for name, values in oracles.items():
        expected = values[-1]
        actual = values[:-1]
        check(
            f"cross-authority exact oracle: {name}",
            all(value == expected for value in actual),
            actual,
            tuple(expected for _ in actual),
            "cross_implementation",
        )
    check(
        "independent exhaustive relation and poset counts",
        (
            shared["relation_count"],
            shared["strict_partial_order_count"],
            shared["invariant_irreflexive_relation_count"],
        )
        == (4096, 219, 2),
        (
            shared["relation_count"],
            shared["strict_partial_order_count"],
            shared["invariant_irreflexive_relation_count"],
        ),
        (4096, 219, 2),
        "cross_implementation",
    )
    check(
        "manifest pins exhaustive S4 fixture counts",
        (
            manifest["finite_fixture"]["enumerated_irreflexive_relations"],
            manifest["finite_fixture"]["labelled_strict_partial_orders"],
            manifest["finite_fixture"]["invariant_irreflexive_relations"],
            manifest["finite_fixture"]["invariant_strict_partial_orders"],
        )
        == (4096, 219, 2, 1),
        (
            manifest["finite_fixture"]["enumerated_irreflexive_relations"],
            manifest["finite_fixture"]["labelled_strict_partial_orders"],
            manifest["finite_fixture"]["invariant_irreflexive_relations"],
            manifest["finite_fixture"]["invariant_strict_partial_orders"],
        ),
        (4096, 219, 2, 1),
        "cross_implementation",
    )
    check(
        "only invariant strict order is empty",
        exact["invariant_strict_partial_orders"]
        == shared["invariant_strict_partial_orders"]
        == [[]],
        (exact["invariant_strict_partial_orders"], shared["invariant_strict_partial_orders"]),
        ([[]], [[]]),
        "cross_implementation",
    )
    check(
        "only self-opposite strict order is empty",
        shared["self_opposite_strict_partial_orders"] == [[]],
        shared["self_opposite_strict_partial_orders"],
        [[]],
        "cross_implementation",
    )
    check(
        "uniform random-order pair probability",
        exact["uniform_total_order_pair_probability"]
        == shared["uniform_pair_probability"]
        == "1/2",
        (exact["uniform_total_order_pair_probability"], shared["uniform_pair_probability"]),
        ("1/2", "1/2"),
        "cross_implementation",
    )
    check(
        "finite-transitive C4 fixture agrees across authorities",
        (
            exact["c4_group_size"],
            exact["c4_vertex_orbit_size"],
            exact["c4_ordered_pair_orbit_sizes"],
            exact["c4_invariant_irreflexive_relation_count"],
            exact["c4_invariant_strict_partial_orders"],
        )
        == (
            shared["c4_group_size"],
            shared["c4_vertex_orbit_size"],
            shared["c4_ordered_pair_orbit_sizes"],
            shared["c4_invariant_relation_count"],
            shared["c4_invariant_strict_partial_orders"],
        )
        == (
            manifest["finite_fixture"]["c4_group_size"],
            manifest["finite_fixture"]["c4_vertex_orbit_size"],
            manifest["finite_fixture"]["c4_ordered_pair_orbit_sizes"],
            manifest["finite_fixture"]["c4_invariant_irreflexive_relations"],
            [[]],
        )
        == (4, 4, [4, 4, 4], 8, [[]]),
        (
            exact["c4_group_size"],
            exact["c4_vertex_orbit_size"],
            exact["c4_ordered_pair_orbit_sizes"],
            exact["c4_invariant_irreflexive_relation_count"],
            exact["c4_invariant_strict_partial_orders"],
        ),
        (4, 4, [4, 4, 4], 8, [[]]),
        "cross_implementation",
    )
    expected_two_orbit_order = [[0, 2], [0, 3], [1, 2], [1, 3]]
    check(
        "two-orbit positive control agrees across implementations",
        exact["two_orbit_invariant_strict_order"]
        == shared["two_orbit_invariant_strict_order"]
        == expected_two_orbit_order,
        (
            exact["two_orbit_invariant_strict_order"],
            shared["two_orbit_invariant_strict_order"],
        ),
        (expected_two_orbit_order, expected_two_orbit_order),
        "cross_implementation",
    )
    expected_marked_order = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    check(
        "primary-independent-manifest marked tuple and order agree",
        exact["symmetry_broken_marks"]
        == manifest["escape_routes"]["marked_tuple"]
        == [0, 1, 4, 9]
        and exact["symmetry_broken_total_order"]
        == shared["marked_total_order"]
        == manifest["escape_routes"]["marked_total_order"]
        == expected_marked_order,
        (
            exact["symmetry_broken_marks"],
            exact["symmetry_broken_total_order"],
            shared["marked_total_order"],
            manifest["escape_routes"]["marked_total_order"],
        ),
        ([0, 1, 4, 9], expected_marked_order, expected_marked_order, expected_marked_order),
        "cross_implementation",
    )
    check(
        "marked stabilizer and invariant random-order support are pinned",
        exact["marked_control_stabilizer_size"]
        == shared["marked_control_stabilizer_size"]
        == manifest["escape_routes"]["marked_control_stabilizer_size"]
        == 1
        and exact["random_total_order_support_size"]
        == shared["random_total_order_support_size"]
        == manifest["escape_routes"]["random_total_order_support_size"]
        == 24
        and exact["random_total_order_law_s4_invariant"]
        is shared["random_total_order_law_s4_invariant"]
        is manifest["escape_routes"]["random_total_order_law_s4_invariant"]
        is True,
        (
            exact["marked_control_stabilizer_size"],
            exact["random_total_order_support_size"],
            exact["random_total_order_law_s4_invariant"],
        ),
        (1, 24, True),
        "cross_implementation",
    )

    check(
        "manifest pins the finite-orbit theorem and infinite boundary",
        "same automorphism orbit" in manifest["statement"]
        and "vertex-transitive" in manifest["statement"]
        and "finite order of g" in manifest["general_theorem"]["proof"]
        and "translations act transitively on Z" in manifest["general_theorem"]["infinite_boundary"]
        and "fixed labels" in manifest["general_theorem"]["reversal_corollary"],
        manifest["general_theorem"],
        "finite-orbit, vertex-transitive, infinite-Z, and fixed-label boundaries",
        "theorem_surface",
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
        "ordered-pair orbit is every off-diagonal pair",
        "only invariant strict partial order is empty",
        "C4 action is vertex-transitive",
        "C4 action is not 2-transitive",
        "C4 ordered-pair orbit sizes are 4,4,4",
        "C4 invariant irreflexive relation count is 8",
        "C4 only invariant strict order is empty",
        "two-orbit symmetry-reduction control is invariant and strict",
        "strict relation equal to its opposite must be empty",
        "distinct clock marks define a strict total order",
        "marked control has trivial stabilizer",
        "uniform random-order support contains 24 distinct orders",
        "uniform random-order law is invariant under every S4 relabeling",
        "uniform random total orders have unbiased pair 0-1",
    }
    required_independent_rows = {
        "independent relation enumeration count",
        "independent strict partial-order enumeration oracle",
        "independent invariant irreflexive relations",
        "independent only invariant strict order is empty",
        "independent only self-opposite strict order is empty",
        "independent C4 action is vertex-transitive",
        "independent C4 action is not 2-transitive",
        "independent C4 invariant irreflexive relation count",
        "independent C4 only invariant strict order is empty",
        "independent two-orbit control is invariant and strict",
        "independent marked relation is a total strict order",
        "independent marked control has trivial stabilizer",
        "independent random-order support contains 24 distinct orders",
        "independent random-order law is S4 invariant",
        "independent uniform random total-order distribution is pair-unbiased",
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

    required_scope = {
        "deterministic_equivariant_comparison_within_finite_automorphism_orbit": False,
        "deterministic_equivariant_nonempty_order_from_finite_transitive_state": False,
        "deterministic_equivariant_nonempty_order_from_2transitive_state": False,
        "reversal_invariant_state_selects_unique_nonempty_arrow": False,
        "extra_asymmetry_or_sector_required_for_excluded_symmetric_input": True,
        "finite_transitive_nogo_extended_to_infinite_transitive_state": False,
        "random_invariant_order_distribution_excluded": False,
        "quotient_set_valued_or_coherent_sector_selector_excluded": False,
        "richer_relational_c0b_model_excluded": False,
        "causal_set_program_invalidated": False,
        "quantum_graphity_program_invalidated": False,
        "gft_tensor_program_invalidated": False,
        "causal_order_derived": False,
        "null_structure_derived": False,
        "c0b_candidate_selected": False,
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
        "C0-A remains temporal calibration without causal branch selection",
        c0a_manifest["scope"]["c0_a_temporal_transfer_benchmark_instantiated"] is True
        and c0a_manifest["scope"]["c0_a_causal_structure_instantiated"] is False
        and c0a_manifest["scope"]["tect_c0_branch_selected"] is False,
        (
            c0a_manifest["scope"]["c0_a_temporal_transfer_benchmark_instantiated"],
            c0a_manifest["scope"]["c0_a_causal_structure_instantiated"],
            c0a_manifest["scope"]["tect_c0_branch_selected"],
        ),
        (True, False, False),
        "branch_coordination",
    )
    check(
        "each prose authority disclaims scientific novelty and global coverage",
        "no global novelty" in manifest["prior_art_boundary"]
        and "not claimed as scientific novelty"
        in " ".join(NOTE.read_text(encoding="utf-8").split())
        and "world-first" not in manifest["statement"].lower()
        and "proves c0-b impossible" not in manifest["no_overclaim"].lower(),
        (
            manifest["prior_art_boundary"],
            "not claimed as scientific novelty"
            in " ".join(NOTE.read_text(encoding="utf-8").split()),
        ),
        ("contains no global novelty", True),
        "scope",
    )

    expected_artifacts = {
        "certificate_note": "strategy/pre-a-c0b-equivariant-causal-selection-nogo-certificate-260803.md",
        "primary_script": "codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo.py",
        "independent_script": "codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo_independent.py",
        "integrated_verifier": "codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo_verify.py",
        "primary_result": "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-primary-pre-a-c0b-equivariant-causal-selection-nogo/result.json",
        "independent_result": "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-independent-pre-a-c0b-equivariant-causal-selection-nogo/result.json",
        "integrated_result": "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-c0b-equivariant-causal-selection-nogo/result.json",
    }
    check(
        "manifest artifact paths are exact",
        manifest["artifacts"] == expected_artifacts,
        manifest["artifacts"],
        expected_artifacts,
        "authority",
    )

    note_text = " ".join(NOTE.read_text(encoding="utf-8").split())
    for phrase in (
        "finite-orbit obstruction",
        "vertex-transitive but not 2-transitive",
        "translations act transitively",
        "fixed event labels",
        "`C(s)` is empty",
        "219 labelled strict partial orders",
        "random C0-B model",
        "C0-B_spatial/C0-A_time",
        "does not exclude C0-B",
        "C0-B remains live",
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
        "verdict": "PASS: deterministic equivariant comparison within a finite automorphism orbit is excluded, hence finite transitive selection is empty; the infinite transitive, smaller-orbit, reversal-permuted, stochastic, and non-single-valued C0-B routes remain open, and no causal order or Pre-A completion is claimed",
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
            str(C0A_MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(C0A_MANIFEST),
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
