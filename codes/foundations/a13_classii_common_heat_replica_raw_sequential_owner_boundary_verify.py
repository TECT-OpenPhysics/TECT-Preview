#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-136 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY"
SCHEMA = "tect/a13-common-heat-replica-raw-sequential-owner-boundary-integrated/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
NOTE = CLAIM_DIR / "notes/classii-common-heat-replica-raw-sequential-owner-boundary-260731-v1.0.tex.txt"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
NEGATIVE_ID = "NG-2026-07-31-A13-POSTHEAT-MEAN-ONLY-FUTURE-VARIANCE-RECOVERY"
EXPECTED_PRIMARY_ASSERTIONS = 71
EXPECTED_INDEPENDENT_ASSERTIONS = 71
EXPECTED_INTEGRATED_ASSERTIONS = 225
PRIMARY = REPO / "codes/foundations/a13_classii_common_heat_replica_raw_sequential_owner_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_common_heat_replica_raw_sequential_owner_boundary_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-common-heat-replica-raw-sequential-owner-boundary/result.json"
)
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-common-heat-replica-raw-sequential-owner-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-common-heat-replica-raw-sequential-owner-boundary/result.json"
)

AUTHORITIES = {
    "R-079": ("classii_full_safe_packet_frame_current_doob_manifest.json", "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"),
    "R-084": ("classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json", "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION"),
    "R-088": ("classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json", "A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION"),
    "R-099": ("classii_extended_state_cartan_doob_rational_recovery_manifest.json", "A13-CLASSII-EXTENDED-STATE-CARTAN-DOOB-RATIONAL-RECOVERY"),
    "R-102": ("classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json", "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"),
    "R-104": ("classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json", "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"),
    "R-119": ("classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json", "A13-CLASSII-LEGAL-ADAPTED-CLUSTER-SCORE-TRACE-TERMINAL-HESSIAN-FRONTIER"),
    "R-123": ("classii_six_row_trace_excess_direct_action_boundary_manifest.json", "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"),
    "R-125": ("classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json", "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY"),
    "R-127": ("classii_predictable_source_riesz_weighted_schur_low_margin_boundary_manifest.json", "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY"),
    "R-128": ("classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json", "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY"),
    "R-129": ("classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json", "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY"),
    "R-132": ("classii_mixed_replica_gaussian_ray_sextic_shell_boundary_manifest.json", "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY"),
    "R-135": ("classii_variance_retained_sequential_atom_refinement_boundary_manifest.json", "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"),
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_child(script: Path, output: Path) -> tuple[int, str, str]:
    command = [sys.executable, str(script), "--output", str(output)]
    result = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=120,
    )
    return result.returncode, result.stdout, result.stderr


def assertion_names(payload: dict[str, Any]) -> set[str]:
    return {
        f"{row.get('group')}::{row.get('name')}"
        for row in payload.get("assertions", {}).get("rows", [])
    }


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-output", type=Path, default=DEFAULT_PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=DEFAULT_INDEPENDENT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_code, primary_stdout, primary_stderr = run_child(PRIMARY, args.primary_output)
    independent_code, independent_stdout, independent_stderr = run_child(
        INDEPENDENT, args.independent_output
    )
    audit.check("children", "primary exit code", primary_code == 0, primary_code, 0)
    audit.check("children", "independent exit code", independent_code == 0, independent_code, 0)
    audit.check("children", "primary stderr empty", primary_stderr == "", primary_stderr, "")
    audit.check("children", "independent stderr empty", independent_stderr == "", independent_stderr, "")
    audit.check("children", "primary PASS banner", "R-136 primary PASS" in primary_stdout, primary_stdout.strip(), "R-136 primary PASS")
    audit.check("children", "independent PASS banner", "R-136 independent PASS" in independent_stdout, independent_stdout.strip(), "R-136 independent PASS")

    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    audit.check("children", "primary schema", primary.get("schema", "").endswith("-primary/1.0"), primary.get("schema"), "*-primary/1.0")
    audit.check("children", "independent schema", independent.get("schema", "").endswith("-independent/1.0"), independent.get("schema"), "*-independent/1.0")
    audit.check("children", "primary result id", primary.get("result_id") == RESULT_ID, primary.get("result_id"), RESULT_ID)
    audit.check("children", "independent result id", independent.get("result_id") == RESULT_ID, independent.get("result_id"), RESULT_ID)
    audit.check("children", "primary status", primary.get("status") == "PASS", primary.get("status"), "PASS")
    audit.check("children", "independent status", independent.get("status") == "PASS", independent.get("status"), "PASS")
    audit.check("children", "primary failures zero", primary["assertions"]["failed"] == 0, primary["assertions"]["failed"], 0)
    audit.check("children", "independent failures zero", independent["assertions"]["failed"] == 0, independent["assertions"]["failed"], 0)
    audit.check("children", "primary exact assertion count", primary["assertions"]["total"] == EXPECTED_PRIMARY_ASSERTIONS, primary["assertions"]["total"], EXPECTED_PRIMARY_ASSERTIONS)
    audit.check("children", "independent exact assertion count", independent["assertions"]["total"] == EXPECTED_INDEPENDENT_ASSERTIONS, independent["assertions"]["total"], EXPECTED_INDEPENDENT_ASSERTIONS)

    primary_names = assertion_names(primary)
    independent_names = assertion_names(independent)
    required_primary = {
        "centring::conditional Pythagoras",
        "post_heat::post-heat future centring vanishes",
        "mean_only_nogo::future-current variance",
        "replica::half replica difference is variance",
        "owner::replica owner coefficient",
        "raw_telescope::replica difference telescopes",
        "doob::owner sum equals reveal transpose",
        "feedback::missing connection correction",
        "graph::full product PSD is not graph-necessary",
        "taylor::full force completion coefficient",
        "scope::sector_a_closed",
    }
    required_independent = {
        "matrix::future residual kills retained range",
        "commutator::exact random-projection defect",
        "post_heat::future-centred atom is zero",
        "mean_only_nogo::second variance",
        "replica::replica-difference variance",
        "owner::replica owner identity",
        "raw_telescope::replica difference",
        "doob::transpose equality",
        "feedback::connection correction",
        "graph::ambient PSD not necessary",
        "taylor::quadratic Taylor equality",
        "scope::sector_a_closed",
    }
    audit.check("contracts", "primary required assertions", required_primary <= primary_names, sorted(required_primary - primary_names), [])
    audit.check("contracts", "independent required assertions", required_independent <= independent_names, sorted(required_independent - independent_names), [])

    shared = (
        ("replica_variance", "2"),
        ("owner_trace_excess", "1"),
        ("owner_reveal_total", "14"),
    )
    for key, expected in shared:
        audit.check("cross", f"primary {key}", str(primary["computed"][key]) == expected, primary["computed"][key], expected)
        audit.check("cross", f"independent {key}", str(independent["computed"][key]) == expected, independent["computed"][key], expected)
        audit.check("cross", f"agreement {key}", str(primary["computed"][key]) == str(independent["computed"][key]), primary["computed"][key], independent["computed"][key])
    audit.check("cross", "feedback correction", str(independent["computed"]["feedback_correction"]) == "3", independent["computed"]["feedback_correction"], 3)
    audit.check("cross", "post-heat residual", str(primary["computed"]["post_heat_future_residual"]) == "0", primary["computed"]["post_heat_future_residual"], 0)
    audit.check("cross", "physical terminal energy gap", primary["computed"]["terminal_energy"] - primary["computed"]["physical_only_energy"] == 3, (primary["computed"]["physical_only_energy"], primary["computed"]["terminal_energy"]), "gap 3")

    independent_imports = imported_roots(INDEPENDENT)
    allowed_stdlib = {
        "__future__",
        "argparse",
        "fractions",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
    }
    audit.check("independence", "independent uses standard library only", independent_imports <= allowed_stdlib, sorted(independent_imports), sorted(allowed_stdlib))
    audit.check("independence", "independent does not import primary", "a13_classii_common_heat_replica_raw_sequential_owner_boundary" not in INDEPENDENT.read_text(encoding="utf-8"), "primary import absent", "absent")
    audit.check("independence", "source hashes differ", sha256(PRIMARY) != sha256(INDEPENDENT), (sha256(PRIMARY), sha256(INDEPENDENT)), "different")

    audit.check("document", "proof note exists", NOTE.is_file(), NOTE.relative_to(REPO) if NOTE.exists() else NOTE, "file")
    note_text = NOTE.read_text(encoding="utf-8")
    required_footer_labels = (
        "Result ID:",
        "Precise statement:",
        "Scope:",
        "Dependencies:",
        "Evidence grade:",
        "Reproduction command:",
        "Expected output:",
        "Falsification gate:",
        "Tier before / after:",
        "No-overclaim statement:",
        "Next required action:",
    )
    audit.check("document", "result id is pinned", RESULT_ID in note_text, RESULT_ID in note_text, True)
    audit.check("document", "all footer labels are present", all(label in note_text for label in required_footer_labels), [label for label in required_footer_labels if label not in note_text], [])
    audit.check("document", "deterministic post-heat scope", "deterministic R-088 target heat" in note_text, "deterministic R-088 target heat" in note_text, True)
    audit.check("document", "production one-use remains open", "No production raw spatial intertwiner" in note_text and "Sector-A closure" in note_text, "open-scope clauses present", "present")
    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    negative_anchor = f'<a id="{NEGATIVE_ID.lower()}"></a>'
    audit.check("negative", "mean-only negative registered", NEGATIVE_ID in negative_text and negative_anchor in negative_text, (NEGATIVE_ID in negative_text, negative_anchor in negative_text), (True, True))
    negative_section = negative_text.split(negative_anchor, 1)[1].split("<a id=", 1)[0] if negative_anchor in negative_text else ""
    audit.check("negative", "required fields registered", all(label in negative_section for label in ("**Failure mode.**", "**Evidence.**", "**Consequence.**")), [label for label in ("**Failure mode.**", "**Evidence.**", "**Consequence.**") if label not in negative_section], [])

    authority_hashes: dict[str, str] = {}
    for ledger_id, (filename, expected_result_id) in AUTHORITIES.items():
        path = CLAIM_DIR / filename
        audit.check("authority", f"{ledger_id} manifest exists", path.is_file(), path.relative_to(REPO) if path.exists() else path, "file")
        payload = load_json(path)
        audit.check("authority", f"{ledger_id} result id", payload.get("result_id") == expected_result_id, payload.get("result_id"), expected_result_id)
        audit.check("authority", f"{ledger_id} claim id", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM)
        authority_hashes[ledger_id] = sha256(path)

    audit.check(
        "contracts",
        "integrated assertion count",
        len(primary["assertions"]["rows"])
        + len(independent["assertions"]["rows"])
        + len(audit.rows)
        + 1
        == EXPECTED_INTEGRATED_ASSERTIONS,
        len(primary["assertions"]["rows"])
        + len(independent["assertions"]["rows"])
        + len(audit.rows)
        + 1,
        EXPECTED_INTEGRATED_ASSERTIONS,
    )

    # Child assertions are copied into the integrated evidence so the count is
    # transparent and no narrow integrator row is mistaken for broad coverage.
    child_rows: list[dict[str, object]] = []
    for child_name, payload in (("primary", primary), ("independent", independent)):
        for row in payload["assertions"]["rows"]:
            child_rows.append(
                {
                    "group": f"{child_name}:{row['group']}",
                    "name": row["name"],
                    "status": row["status"],
                    "actual": row["actual"],
                    "expected": row["expected"],
                }
            )

    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(all_rows),
            "passed": len(all_rows) - failed,
            "failed": failed,
            "rows": all_rows,
        },
        "children": {
            "primary": {
                "path": str(args.primary_output.relative_to(REPO)),
                "sha256": sha256(args.primary_output),
                "assertions": primary["assertions"]["total"],
                "stdout": primary_stdout,
            },
            "independent": {
                "path": str(args.independent_output.relative_to(REPO)),
                "sha256": sha256(args.independent_output),
                "assertions": independent["assertions"]["total"],
                "stdout": independent_stdout,
            },
        },
        "authority_hashes": authority_hashes,
        "source_hashes": {
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
        },
        "computed": {
            "replica_variance": "2",
            "owner_trace_excess": "1",
            "owner_reveal_total": "14",
            "feedback_connection_gap": "3",
            "post_heat_future_residual": "0",
            "graph_compressed_value": "1",
        },
        "scope": {
            "children_pass": True,
            "common_heat_replica_identity": True,
            "raw_replica_telescope": True,
            "post_heat_mean_only_no_go": True,
            "r102_transpose_reused_not_reclaimed": True,
            "production_raw_spatial_intertwiner": False,
            "production_one_use_q_ledger": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-136 integrated {payload['status']}: {len(all_rows)-failed}/{len(all_rows)}")
    print(
        f"primary={primary['assertions']['total']}; independent={independent['assertions']['total']}; "
        f"integrator={len(audit.rows)}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
