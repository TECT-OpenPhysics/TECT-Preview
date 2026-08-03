#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-ST8-Q3LOCK-v0."""

from __future__ import annotations

import argparse
import ast
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
CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-v0"
PARENT_ID = "PA-CP1-ST8-CB-v0"
CANDIDATE_FAMILY = "PRE-A-Q3-NONLINEAR-SPECIES-LOCK"
SLUG = "pre-a-cp1-st8-q3lock"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-st8-q3lock-certificate-260803.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
STORED_PRIMARY = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
)
STORED_INDEPENDENT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-integrated-{SLUG}/result.json"
)
STORED_INTEGRATED = DEFAULT_OUTPUT
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-Q3LOCK-QUADRATIC-CONNECTIVITY-CI8"

# These are explicit test-oracle counts. A changed assertion surface requires
# conscious verifier review rather than silently weakening the package.
EXPECTED_PRIMARY_ASSERTIONS = 54
EXPECTED_INDEPENDENT_ASSERTIONS = 36


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted((serial(item) for item in value), key=str)
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
            raise AssertionError(
                f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}"
            )
        rows.append(
            {
                "name": name,
                "group": group,
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    required_files = (
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        STRATEGY_INDEX,
        NEGATIVE_REGISTRY,
        UPSTREAM,
    )
    for path in required_files:
        check(
            f"required file exists: {path.name}",
            path.is_file(),
            path.is_file(),
            True,
            "files",
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="tect-q3lock-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    check(
        "manifest identity tuple",
        (
            manifest["schema"],
            manifest["candidate_id"],
            manifest["parent_id"],
            manifest["candidate_family"],
            manifest["package_version"],
            manifest["task_id"],
            manifest["claim_bearing"],
        )
        == (
            MANIFEST_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            CANDIDATE_FAMILY,
            __version__,
            "T-054",
            False,
        ),
        (
            manifest["schema"],
            manifest["candidate_id"],
            manifest["parent_id"],
            manifest["candidate_family"],
            manifest["package_version"],
            manifest["task_id"],
            manifest["claim_bearing"],
        ),
        (MANIFEST_SCHEMA, CANDIDATE_ID, PARENT_ID, CANDIDATE_FAMILY, __version__, "T-054", False),
        "identity",
    )
    check("upstream identity", upstream["candidate_id"] == PARENT_ID, upstream["candidate_id"], PARENT_ID, "identity")
    check(
        "child identity tuples",
        (
            primary["schema"],
            primary["candidate_id"],
            primary["parent_id"],
            independent["schema"],
            independent["candidate_id"],
            independent["parent_id"],
        )
        == (
            PRIMARY_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
            INDEPENDENT_SCHEMA,
            CANDIDATE_ID,
            PARENT_ID,
        ),
        (
            primary["schema"],
            primary["candidate_id"],
            primary["parent_id"],
            independent["schema"],
            independent["candidate_id"],
            independent["parent_id"],
        ),
        (PRIMARY_SCHEMA, CANDIDATE_ID, PARENT_ID, INDEPENDENT_SCHEMA, CANDIDATE_ID, PARENT_ID),
        "identity",
    )

    check(
        "primary assertion oracle",
        primary["assertions"]["passed"] == primary["assertions"]["total"] == EXPECTED_PRIMARY_ASSERTIONS,
        (primary["assertions"]["passed"], primary["assertions"]["total"]),
        (EXPECTED_PRIMARY_ASSERTIONS, EXPECTED_PRIMARY_ASSERTIONS),
        "children",
    )
    check(
        "independent assertion oracle",
        independent["assertions"]["passed"] == independent["assertions"]["total"] == EXPECTED_INDEPENDENT_ASSERTIONS,
        (independent["assertions"]["passed"], independent["assertions"]["total"]),
        (EXPECTED_INDEPENDENT_ASSERTIONS, EXPECTED_INDEPENDENT_ASSERTIONS),
        "children",
    )

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    check(
        "independent does not import primary",
        not any("pre_a_cp1_st8_q3lock" in name for name in imported_modules),
        sorted(imported_modules),
        "no primary module",
        "independence",
    )

    comparable_keys = (
        "species_count",
        "cube_edge_count",
        "cube_laplacian_spectrum",
        "origin_lock_hessian",
        "ordered_minimum_count",
        "cut_histogram",
        "finite_collective_effective_quartic",
        "physical_diagonal_continuum_quartic",
        "pah1_collective_tangent_squared_frequencies",
        "quadratic_connected_control_nullity",
        "negative_lambda_bipartite_threshold",
    )
    for key in comparable_keys:
        check(
            f"children agree: {key}",
            primary["exact_results"][key] == independent["exact_results"][key],
            primary["exact_results"][key],
            independent["exact_results"][key],
            "cross_implementation",
        )

    expected_spectrum = {"0": 1, "2": 3, "4": 3, "6": 1}
    expected_histogram = {"0": 2, "3": 16, "4": 30, "5": 48, "6": 64, "7": 48, "8": 30, "9": 16, "12": 2}
    check("exact species spectrum", primary["exact_results"]["cube_laplacian_spectrum"] == expected_spectrum, primary["exact_results"]["cube_laplacian_spectrum"], expected_spectrum, "exact_result")
    check("exact cut histogram", primary["exact_results"]["cut_histogram"] == expected_histogram, primary["exact_results"]["cut_histogram"], expected_histogram, "exact_result")
    check("two ordered minima", primary["exact_results"]["ordered_minimum_count"] == 2, primary["exact_results"]["ordered_minimum_count"], 2, "exact_result")
    check("origin Hessian zero", primary["exact_results"]["origin_lock_hessian"] == "zero", primary["exact_results"]["origin_lock_hessian"], "zero", "exact_result")
    check("quadratic control nullity one", primary["exact_results"]["quadratic_connected_control_nullity"] == 1, primary["exact_results"]["quadratic_connected_control_nullity"], 1, "exact_result")
    expected_pah1_squares = ["9", "25", "25"]
    check("PA-H1 tangent fixture", primary["exact_results"]["pah1_collective_tangent_squared_frequencies"] == expected_pah1_squares, primary["exact_results"]["pah1_collective_tangent_squared_frequencies"], expected_pah1_squares, "exact_result")
    check("negative threshold fixture", primary["exact_results"]["negative_lambda_bipartite_threshold"] == "-1/12", primary["exact_results"]["negative_lambda_bipartite_threshold"], "-1/12", "exact_result")

    expected_artifacts = {
        "certificate": CERTIFICATE,
        "primary_script": PRIMARY,
        "independent_script": INDEPENDENT,
        "integrated_verifier": VERIFIER,
        "primary_result": STORED_PRIMARY,
        "independent_result": STORED_INDEPENDENT,
        "integrated_result": STORED_INTEGRATED,
    }
    check("manifest artifact keys", set(manifest["artifacts"]) == set(expected_artifacts), sorted(manifest["artifacts"]), sorted(expected_artifacts), "artifact_routing")
    for key, path in expected_artifacts.items():
        declared = (REPO / manifest["artifacts"][key]).resolve()
        check(
            f"manifest artifact route: {key}",
            declared == path.resolve(),
            manifest["artifacts"][key],
            str(path.relative_to(REPO)).replace("\\", "/"),
            "artifact_routing",
        )

    check(
        "manifest negative id",
        manifest["quadratic_connected_control"]["negative_id"] == NEGATIVE_ID,
        manifest["quadratic_connected_control"]["negative_id"],
        NEGATIVE_ID,
        "negative_registry",
    )
    check("negative registry entry", NEGATIVE_ID.lower() in negative_text.lower(), NEGATIVE_ID, "present", "negative_registry")
    check("strategy index entry", MANIFEST.name in index_text and CERTIFICATE.name in index_text, (MANIFEST.name in index_text, CERTIFICATE.name in index_text), (True, True), "index")

    required_anchors = (
        "section-3-candidate-definition",
        "section-4-complete-square-locking-theorem",
        "section-6-origin-and-ordered-hessians",
        "section-7-minimality-and-quadratic-fork",
        "section-9-collective-and-volume-ledgers",
        "section-10-pah1-tangent-calibration",
        "section-12-causal-and-cp1-boundary",
    )
    for anchor in required_anchors:
        check(
            f"certificate anchor: {anchor}",
            f'id="{anchor}"' in certificate_text,
            f'id="{anchor}"' in certificate_text,
            True,
            "anchors",
        )

    required_phrases = (
        "H_{\\min}=-\\frac{N^3r^2}{4g}<H_\\lambda(0,0)=0",
        "D^2\\Delta H_\\lambda(0)=0",
        "g_{\\rm eff}=\\frac g8",
        "h^3=\\frac{a^3}{8}",
        "lambda/g>16/9",
        "CP1 complete=false",
        "Pre-A complete=false",
        "physical empty space",
        "not an invariant full quantum Hilbert",
    )
    for phrase in required_phrases:
        check(
            f"certificate phrase: {phrase}",
            phrase in certificate_text,
            phrase in certificate_text,
            True,
            "certificate_scope",
        )

    scope = manifest["scope"]
    expected_false = (
        "inherits_original_fine_translation_symmetry",
        "thermodynamic_phase_transition",
        "interacting_classical_continuum_limit",
        "interacting_quantum_continuum_limit",
        "physical_vacuum",
        "below_empty_space",
        "event_horizon",
        "gravity",
        "cooling",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in expected_false:
        check(f"scope remains false: {key}", scope[key] is False, scope[key], False, "no_overclaim")
    check("no physical predictions", manifest["input_prediction_accounting"]["physical_predictions"] == [], manifest["input_prediction_accounting"]["physical_predictions"], [], "no_overclaim")
    check("no holdout prediction", manifest["input_prediction_accounting"]["holdout_prediction"] is False, manifest["input_prediction_accounting"]["holdout_prediction"], False, "no_overclaim")

    with tempfile.TemporaryDirectory(prefix="tect-q3lock-hash-") as temporary:
        temporary_path = Path(temporary)
        lf = temporary_path / "lf.txt"
        crlf = temporary_path / "crlf.txt"
        cr = temporary_path / "cr.txt"
        lf.write_bytes(b"alpha\nbeta\n")
        crlf.write_bytes(b"alpha\r\nbeta\r\n")
        cr.write_bytes(b"alpha\rbeta\r")
        check("portable LF CRLF CR hashes", sha256(lf) == sha256(crlf) == sha256(cr), (sha256(lf), sha256(crlf), sha256(cr)), "all equal", "portability")

    if STORED_PRIMARY.is_file():
        stored_primary = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
        check("stored primary is fresh", canonical(stored_primary) == canonical(primary), stored_primary["assertions"]["passed"], primary["assertions"]["passed"], "stored_children")
    if STORED_INDEPENDENT.is_file():
        stored_independent = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))
        check("stored independent is fresh", canonical(stored_independent) == canonical(independent), stored_independent["assertions"]["passed"], independent["assertions"]["passed"], "stored_children")

    authority_files = (VERIFIER,) + required_files
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_id": PARENT_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "integrated finite nonlinear locking and quadratic-fork audit; not CP1 or Pre-A closure",
        "claim_context": ["C6-SPACETIME-SIGNATURE", "A2-FULL-PRODUCTION-WELLPOSED"],
        "claim_bearing": False,
        "task_id": "T-054",
        "child_assertions": {
            "primary": primary["assertions"]["passed"],
            "independent": independent["assertions"]["passed"],
            "integrated": len(rows),
            "combined": primary["assertions"]["passed"] + independent["assertions"]["passed"] + len(rows),
        },
        "verdict": manifest["verdict"],
        "negative_id": NEGATIVE_ID,
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "sources": [
            {"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(path)}
            for path in authority_files
        ],
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = verify()
    if arguments.self_test and STORED_INTEGRATED.is_file():
        stored = json.loads(STORED_INTEGRATED.read_text(encoding="utf-8"))
        if canonical(stored) != canonical(payload):
            raise AssertionError("stored integrated artifact is stale; regenerate without --self-test")
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    counts = payload["child_assertions"]
    print(
        f"PASS {counts['integrated']}/{counts['integrated']} integrated | "
        f"{counts['combined']} combined | {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
