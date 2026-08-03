#!/usr/bin/env python3
"""Integrated verifier for PA-CP1-FD-C1-STRICT-CONE-NOGO-v0."""

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
CANDIDATE_ID = "PA-CP1-FD-C1-STRICT-CONE-NOGO-v0"
CANDIDATE_FAMILY = "PRE-A-FINITE-CONTINUOUS-TIME-CAUSALITY-AUDIT"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-FINITE-C1-EQUILIBRIUM-STRICT-CONE"
SLUG = "pre-a-cp1-fdan-strict-cone-nogo"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
MANIFEST_SCHEMA = f"tect/{SLUG}-manifest/0.1"
PRIMARY_SCHEMA = f"tect/{SLUG}-primary/0.1"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent/0.1"
VERIFIER = Path(__file__).resolve()
PRIMARY = REPO / "codes/foundations/pre_a_cp1_fdan_strict_cone_nogo.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_cp1_fdan_strict_cone_nogo_independent.py"
MANIFEST = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-manifest.json"
CERTIFICATE = REPO / "strategy/pre-a-cp1-fdan-strict-cone-nogo-certificate-260803.md"
STRATEGY_INDEX = REPO / "strategy/INDEX.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
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

# Explicit test oracles: changing an assertion surface requires conscious
# integrated-review updates rather than silently shrinking the package.
EXPECTED_PRIMARY_ASSERTIONS = 39
EXPECTED_INDEPENDENT_ASSERTIONS = 31


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serial(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        serial(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
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


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


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
    )
    for path in required_files:
        check(f"required file: {path.name}", path.is_file(), path.is_file(), True, "files")

    with tempfile.TemporaryDirectory(prefix="tect-fdan-cone-") as temporary:
        temporary_path = Path(temporary)
        primary = run_child(PRIMARY, temporary_path / "primary.json")
        independent = run_child(INDEPENDENT, temporary_path / "independent.json")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    registry_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    index_text = STRATEGY_INDEX.read_text(encoding="utf-8")

    check("primary schema", primary["schema"] == PRIMARY_SCHEMA, primary["schema"], PRIMARY_SCHEMA, "identity")
    check("independent schema", independent["schema"] == INDEPENDENT_SCHEMA, independent["schema"], INDEPENDENT_SCHEMA, "identity")
    check("manifest schema", manifest["schema"] == MANIFEST_SCHEMA, manifest["schema"], MANIFEST_SCHEMA, "identity")
    for label, payload in (("primary", primary), ("independent", independent), ("manifest", manifest)):
        check(f"{label} candidate id", payload["candidate_id"] == CANDIDATE_ID, payload["candidate_id"], CANDIDATE_ID, "identity")
    check("candidate family", manifest["candidate_family"] == CANDIDATE_FAMILY, manifest["candidate_family"], CANDIDATE_FAMILY, "identity")
    check("negative id", manifest["negative_id"] == NEGATIVE_ID, manifest["negative_id"], NEGATIVE_ID, "identity")

    primary_count = primary["assertions"]["passed"]
    independent_count = independent["assertions"]["passed"]
    check("primary assertion oracle", primary_count == EXPECTED_PRIMARY_ASSERTIONS, primary_count, EXPECTED_PRIMARY_ASSERTIONS, "children")
    check("independent assertion oracle", independent_count == EXPECTED_INDEPENDENT_ASSERTIONS, independent_count, EXPECTED_INDEPENDENT_ASSERTIONS, "children")
    check("primary all pass", primary["assertions"]["passed"] == primary["assertions"]["total"], primary["assertions"], "all pass", "children")
    check("independent all pass", independent["assertions"]["passed"] == independent["assertions"]["total"], independent["assertions"], "all pass", "children")

    primary_exact = primary["exact_results"]
    independent_exact = independent["exact_results"]
    exact_pairs = (
        ("CP1a axis kernel", primary_exact["CP1a_axis_collocation_kernel"], independent_exact["CP1a_collocation_kernel"]["axis"], "28/9"),
        ("CP1a face kernel", primary_exact["CP1a_face_collocation_kernel"], independent_exact["CP1a_collocation_kernel"]["face"], "-19/9"),
        ("CP1a corner square", primary_exact["CP1a_corner_kernel_square"], independent_exact["CP1a_corner_kernel_square"], "-38/3"),
        ("CP1a corner response", primary_exact["CP1a_corner_displacement_leading_response"], independent_exact["CP1a_corner_fourth_order_response"], "-19/36"),
        ("Q3 ordered first power", primary_exact["Q3_ordered_species_first_power"], independent_exact["Q3_ordered_edge_first_power"], 2),
    )
    for name, first, second, expected in exact_pairs:
        check(f"primary independent agreement: {name}", first == second == expected, (first, second), expected, "cross_route")

    modules = imported_modules(INDEPENDENT)
    check("independent does not import primary", not any(module.endswith("pre_a_cp1_fdan_strict_cone_nogo") for module in modules), sorted(modules), "no primary import", "independence")
    check("independent avoids sympy", "sympy" not in modules, sorted(modules), "no sympy", "independence")

    check("negative registry entry", NEGATIVE_ID.lower() in registry_text.lower(), NEGATIVE_ID, "present", "registration")
    check("strategy index manifest", MANIFEST.name in index_text, MANIFEST.name, "present", "registration")
    check("strategy index certificate", CERTIFICATE.name in index_text, CERTIFICATE.name, "present", "registration")

    anchors = (
        "section-3-theorem",
        "section-4-hamiltonian-corollary",
        "section-5-st8-q3lock",
        "section-6-cp1a",
        "section-7-quantum-control",
        "section-8-controls-scope",
        "section-9-cp1-decision",
        "section-10-adversarial-review",
    )
    for anchor in anchors:
        check(f"certificate anchor: {anchor}", f'id="{anchor}"' in certificate_text, anchor, "present", "certificate")

    phrases = (
        "P_yA^nP_x=0",
        "K_{100}=\\frac{28}{9}",
        "(K^2)_{111}=-\\frac{38}{3}",
        "D^2W(0,0)=0",
        "Lieb-Robinson",
        "physical empty space",
        "CP1 complete=false",
        "Pre-A complete=false",
    )
    for phrase in phrases:
        check(f"certificate phrase: {phrase}", phrase in certificate_text, phrase, "present", "certificate")

    scope = manifest["scope"]
    check("exact scoped no-go true", scope["exact_finite_C1_equilibrium_variational_nogo"] is True, scope["exact_finite_C1_equilibrium_variational_nogo"], True, "scope")
    for key in (
        "single_finite_amplitude_trajectory_nogo",
        "Lieb_Robinson_quasi_locality_rejected",
        "controlled_hyperbolic_continuum_limit_rejected",
        "discrete_time_exact_causality_rejected",
        "unbounded_QFT_microcausality_rejected",
        "physical_vacuum",
        "below_empty_space",
        "event_horizon",
        "gravity",
        "CP1_complete",
        "Pre_A_complete",
    ):
        check(f"scope remains false: {key}", scope[key] is False, scope[key], False, "scope")
    check("no physical predictions", manifest["input_prediction_accounting"]["physical_predictions"] == [], manifest["input_prediction_accounting"]["physical_predictions"], [], "scope")
    check("no holdout prediction", manifest["input_prediction_accounting"]["holdout_prediction"] is False, manifest["input_prediction_accounting"]["holdout_prediction"], False, "scope")

    if STORED_PRIMARY.is_file():
        stored = json.loads(STORED_PRIMARY.read_text(encoding="utf-8"))
        check("stored primary fresh", canonical(stored) == canonical(primary), stored["assertions"]["passed"], primary_count, "stored")
    if STORED_INDEPENDENT.is_file():
        stored = json.loads(STORED_INDEPENDENT.read_text(encoding="utf-8"))
        check("stored independent fresh", canonical(stored) == canonical(independent), stored["assertions"]["passed"], independent_count, "stored")

    authority_files = (VERIFIER,) + required_files
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "integrated finite C1 equilibrium strict-cone audit; not CP1 or Pre-A closure",
        "claim_context": ["C6-SPACETIME-SIGNATURE", "A2-FULL-PRODUCTION-WELLPOSED"],
        "claim_bearing": False,
        "task_id": "T-054",
        "negative_id": NEGATIVE_ID,
        "child_assertions": {
            "primary": primary_count,
            "independent": independent_count,
            "integrated": len(rows),
            "combined": primary_count + independent_count + len(rows),
        },
        "verdict": manifest["verdict"],
        "scope": scope,
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
