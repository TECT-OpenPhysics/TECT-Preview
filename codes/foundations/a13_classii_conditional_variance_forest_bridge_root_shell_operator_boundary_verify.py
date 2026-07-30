#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-125 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

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

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-"
    "ROOT-SHELL-OPERATOR-BOUNDARY"
)
SCHEMA = (
    "tect/a13-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary-integrated/1.0"
)
MANIFEST_SCHEMA = (
    "tect/a13-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary-manifest/1.0"
)
PRIMARY_SCHEMA = (
    "tect/a13-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary-primary/1.0"
)
INDEPENDENT_SCHEMA = (
    "tect/a13-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary-independent/1.0"
)
PRIMARY_ASSERTIONS = 51
INDEPENDENT_ASSERTIONS = 39
# Set after the first complete inventory run.  Zero disables only this count gate.
INTEGRATED_ASSERTIONS = 164

CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / (
    "codes/foundations/a13_classii_conditional_variance_forest_bridge_"
    "root_shell_operator_boundary.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_conditional_variance_forest_bridge_"
    "root_shell_operator_boundary_independent.py"
)
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / (
    "notes/classii-conditional-variance-forest-bridge-root-shell-"
    "operator-boundary-260730-v1.0.tex.txt"
)
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
MANIFEST = CLAIM_DIR / (
    "classii_conditional_variance_forest_bridge_root_shell_"
    "operator_boundary_manifest.json"
)
PRIMARY_RESULT = CLAIM_DIR / (
    "runs/2026-07-30-primary-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)
INDEPENDENT_RESULT = CLAIM_DIR / (
    "runs/2026-07-30-independent-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-30-integrated-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)

AUTHORITY_PATHS = {
    "governance": REPO / "GOVERNANCE.md",
    "a1": REPO / (
        "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
        "production_functional_manifest.json"
    ),
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r074": CLAIM_DIR / "classii_resonant_phase_root_besov_reduction_manifest.json",
    "r079": CLAIM_DIR / "classii_full_safe_packet_frame_current_doob_manifest.json",
    "r093": CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r103": CLAIM_DIR / "classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r118": CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
    "r120": CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
    "r121": CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json",
    "r123": CLAIM_DIR / "classii_six_row_trace_excess_direct_action_boundary_manifest.json",
    "r124": CLAIM_DIR / "classii_stationary_polarized_trace_defect_replica_root_shell_boundary_manifest.json",
}

EXPECTED_SCOPE = {
    "finite_cutoff_bridge_proved": True,
    "conditional_variance_rebate_required": True,
    "finite_cutoff_adapted_partial_wick_identity_proved": True,
    "abstract_root_shell_operator_criterion_proved": True,
    "owner_complete_stationary_baseline_sum_proved": False,
    "adapted_forest_continuum_bound_proved": False,
    "production_root_shell_factorization_proved": False,
    "overlap_src_proved": False,
    "nelson_proved": False,
    "sector_a_closed": False,
}

PRIMARY_GROUPS = {
    "production": 5,
    "bridge": 6,
    "owners": 1,
    "counterfixture": 7,
    "baseline": 12,
    "clark_ocone": 3,
    "adapted_algebra": 2,
    "adapted_scope": 2,
    "cartan": 4,
    "operator": 9,
}
INDEPENDENT_GROUPS = {
    "production": 2,
    "bridge": 3,
    "owners": 2,
    "counterfixture": 3,
    "baseline": 15,
    "operator": 8,
    "adapted_algebra": 2,
    "adapted_scope": 1,
    "scope": 3,
}

NEGATIVE_IDS = (
    "NG-2026-07-30-A13-NAIVE-PRIMITIVE-TRACE-FOREST-IDENTIFICATION",
)
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(406, 414))

NOTE_TOKENS = (
    "R-125 conclusion",
    "Theorem 3.1 (primitive trace and future-variance rebate)",
    "Proposition 6.1 (exact production residual)",
    "Lemma 6.2 (conditional common-terminal low-plus-root diagnostic)",
    "Theorem 8.1 (far-tail Hilbert operator budget)",
    r"339\over4000P",
    r"2680\over729",
    "finite-cutoff adapted partial-Wick identity",
    r"K_{\rm far}",
    "16065",
    r"4\sqrt{\eta\zeta}",
    "nonnegative complete-low",
    "root-only",
    "production stationary baseline is excluded",
    "Sector-A closure remain open",
    "Tier stays T4",
    "Delta V_fut-Delta F063_ad",
)


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        count_ok = not INTEGRATED_ASSERTIONS or len(self.rows) == INTEGRATED_ASSERTIONS
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) and count_ok else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed + (0 if count_ok else 1),
            "assertions": self.rows,
            "aggregate_assertions": PRIMARY_ASSERTIONS + INDEPENDENT_ASSERTIONS + len(self.rows),
            "diagnostics": {
                **diagnostics,
                "expected_integrated_assertions": INTEGRATED_ASSERTIONS,
            },
            "scope": {**EXPECTED_SCOPE, "tier_promoted": False},
            "no_overclaim": (
                "R-125 proves finite-cutoff bridge and partial-Wick algebra, the exact "
                "stationary residual, a conditional low-plus-root diagnostic, and an "
                "abstract operator criterion. Production factorization, balanced band, "
                "root-only stationary baseline, OVERLAP_src, Nelson, removals, the "
                "interacting measure, and Sector A remain open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r125-") as directory:
        output = Path(directory) / "result.json"
        completed = subprocess.run(
            [sys.executable, "-B", str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if not output.is_file():
            return (
                {"status": "MISSING", "_returncode": completed.returncode},
                completed.stdout,
                completed.stderr,
            )
        payload = load_json(output)
        payload["_returncode"] = completed.returncode
        return payload, completed.stdout, completed.stderr


def group_counts(record: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in record.get("assertions", []):
        group = str(row.get("group"))
        counts[group] = counts.get(group, 0) + 1
    return counts


def assertion_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("name")): row for row in record.get("assertions", [])}


def child_contract(
    audit: Audit,
    label: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    count: int,
    groups: dict[str, int],
) -> None:
    returncode = fresh.pop("_returncode", None)
    checks = (
        ("returncode", returncode, 0),
        ("status", fresh.get("status"), "PASS"),
        ("schema", fresh.get("schema"), schema),
        ("claim", fresh.get("claim_id"), CLAIM),
        ("result", fresh.get("result_id"), RESULT_ID),
        ("total", fresh.get("assertions_total"), count),
        ("passed", fresh.get("assertions_passed"), count),
        ("failed", fresh.get("assertions_failed"), 0),
    )
    for name, actual, expected in checks:
        audit.check("child", f"{label}_{name}", actual == expected, actual, expected)
    rows = fresh.get("assertions", [])
    signatures = [(row.get("group"), row.get("name")) for row in rows]
    audit.check(
        "child",
        f"{label}_unique_all_pass",
        len(signatures) == count
        and len(set(signatures)) == count
        and all(row.get("status") == "PASS" for row in rows),
        len(set(signatures)),
        count,
    )
    audit.check(
        "child",
        f"{label}_groups",
        group_counts(fresh) == groups,
        group_counts(fresh),
        groups,
    )
    audit.check(
        "child",
        f"{label}_stored_reproduces",
        fresh == stored,
        fresh == stored,
        True,
    )
    audit.check(
        "scope",
        f"{label}_exact_scope",
        fresh.get("scope") == EXPECTED_SCOPE,
        fresh.get("scope"),
        EXPECTED_SCOPE,
    )
    boundary = str(fresh.get("no_overclaim", ""))
    required = ("production", "stationary", "Nelson", "Sector A")
    audit.check(
        "scope",
        f"{label}_no_overclaim",
        all(token in boundary for token in required),
        boundary,
        "production/stationary/Nelson/Sector A boundaries",
    )


def independent_imports(path: Path) -> tuple[bool, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {
        "__future__",
        "argparse",
        "fractions",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
        "typing",
    }
    source = path.read_text(encoding="utf-8")
    return roots <= allowed and PRIMARY.stem not in source, sorted(roots)


def file_entry_ok(entry: Any, path: Path, version: str | None = None) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("path") != relative(path) or entry.get("sha256") != digest(path):
        return False
    return version is None or entry.get("version") == version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=180)
    arguments = parser.parse_args()
    audit = Audit()

    package_files = (
        PRIMARY,
        INDEPENDENT,
        VERIFIER,
        NOTE,
        PDF,
        MANIFEST,
        PRIMARY_RESULT,
        INDEPENDENT_RESULT,
    )
    required = (*package_files, *AUTHORITY_PATHS.values())
    for path in required:
        audit.check("existence", relative(path), path.is_file(), path.is_file(), True)

    missing = [path for path in required if not path.is_file()]
    if missing:
        payload = audit.finish({"missing": [relative(path) for path in missing]})
        atomic_json(arguments.output, payload)
        print(
            f"R-125 integrated {payload['status']} "
            f"{payload['assertions_passed']}/{payload['assertions_total']}"
        )
        return 1

    primary_fresh, primary_stdout, primary_stderr = execute_child(
        PRIMARY, arguments.timeout
    )
    independent_fresh, independent_stdout, independent_stderr = execute_child(
        INDEPENDENT, arguments.timeout
    )
    primary_stored = load_json(PRIMARY_RESULT)
    independent_stored = load_json(INDEPENDENT_RESULT)
    child_contract(
        audit,
        "primary",
        primary_fresh,
        primary_stored,
        PRIMARY_SCHEMA,
        PRIMARY_ASSERTIONS,
        PRIMARY_GROUPS,
    )
    child_contract(
        audit,
        "independent",
        independent_fresh,
        independent_stored,
        INDEPENDENT_SCHEMA,
        INDEPENDENT_ASSERTIONS,
        INDEPENDENT_GROUPS,
    )

    imports_ok, imported_roots = independent_imports(INDEPENDENT)
    audit.check(
        "independence",
        "standard_library_and_no_primary_import",
        imports_ok,
        imported_roots,
        "standard library and no primary import",
    )
    audit.check(
        "independence",
        "source_hashes_differ",
        digest(PRIMARY) != digest(INDEPENDENT),
        digest(PRIMARY),
        "different from independent",
    )
    primary_signatures = set(
        (row.get("group"), row.get("name")) for row in primary_stored["assertions"]
    )
    independent_signatures = set(
        (row.get("group"), row.get("name"))
        for row in independent_stored["assertions"]
    )
    audit.check(
        "independence",
        "signature_sets_intentionally_differ",
        primary_signatures != independent_signatures,
        primary_signatures == independent_signatures,
        False,
    )

    primary_rows = assertion_map(primary_stored)
    independent_rows = assertion_map(independent_stored)
    witnesses = (
        ("mass", primary_rows["mass"].get("actual"), "4000000000001/1000000000000"),
        ("s", primary_rows["s"].get("actual"), "42375000000/4000000000001"),
        (
            "fixture_trace",
            primary_rows["theta"].get("actual"),
            "169500000000/4000000000001",
        ),
        (
            "missing_half_variance",
            primary_rows["naive_omission"].get("actual"),
            "84750000000/4000000000001",
        ),
        ("dyadic_factor", primary_rows["geometric_sum"].get("actual"), "64/16065"),
        (
            "trace_threshold",
            primary_rows["full_trace_threshold"].get("actual"),
            "3*sqrt(3)/5",
        ),
        (
            "action_threshold",
            primary_rows["action_threshold"].get("actual"),
            "3*sqrt(3)/10",
        ),
    )
    for name, actual, expected in witnesses:
        audit.check("witness", name, actual == expected, actual, expected)
    residual_actual = float(independent_rows["residual_threshold"].get("actual"))
    audit.check(
        "witness",
        "residual_threshold",
        abs(residual_actual - 0.9209323339075) < 2e-12,
        residual_actual,
        "0.9209323339075 +/- 2e-12",
    )

    manifest = load_json(MANIFEST)
    verification = manifest.get("verification", {})
    metadata_checks = (
        ("schema", manifest.get("schema"), MANIFEST_SCHEMA),
        ("package_version", manifest.get("package_version"), "1.0.0"),
        ("issued", manifest.get("issued"), "2026-07-30"),
        ("claim", manifest.get("claim_id"), CLAIM),
        ("result", manifest.get("result_id"), RESULT_ID),
        ("ledger", manifest.get("result_ledger_id"), "R-125"),
        ("tier", manifest.get("tier"), "T4"),
        (
            "evidence_grade",
            manifest.get("evidence_grade"),
            ["ANALYTIC", "EXACT", "EXECUTED"],
        ),
        ("primary_count", verification.get("primary_assertions"), PRIMARY_ASSERTIONS),
        (
            "independent_count",
            verification.get("independent_assertions"),
            INDEPENDENT_ASSERTIONS,
        ),
        ("primary_schema", verification.get("primary_schema"), PRIMARY_SCHEMA),
        (
            "independent_schema",
            verification.get("independent_schema"),
            INDEPENDENT_SCHEMA,
        ),
        ("integrated_schema", verification.get("integrated_schema"), SCHEMA),
    )
    for name, actual, expected in metadata_checks:
        audit.check("manifest", name, actual == expected, actual, expected)
    if INTEGRATED_ASSERTIONS:
        audit.check(
            "manifest",
            "integrated_count",
            verification.get("integrated_assertions") == INTEGRATED_ASSERTIONS,
            verification.get("integrated_assertions"),
            INTEGRATED_ASSERTIONS,
        )

    files = manifest.get("files", {})
    for label, path, version in (
        ("primary", PRIMARY, "1.0.0"),
        ("independent", INDEPENDENT, "1.0.0"),
        ("verifier", VERIFIER, "1.0.0"),
        ("note", NOTE, None),
        ("pdf", PDF, None),
        ("primary_result", PRIMARY_RESULT, None),
        ("independent_result", INDEPENDENT_RESULT, None),
    ):
        audit.check(
            "manifest_file",
            label,
            file_entry_ok(files.get(label), path, version),
            files.get(label),
            {"path": relative(path), "sha256": digest(path), "version": version},
        )
    authorities = manifest.get("authorities", {})
    for label, path in AUTHORITY_PATHS.items():
        audit.check(
            "authority",
            label,
            file_entry_ok(authorities.get(label), path),
            authorities.get(label),
            {"path": relative(path), "sha256": digest(path)},
        )
    audit.check(
        "manifest",
        "negatives",
        tuple(manifest.get("negative_results", [])) == NEGATIVE_IDS,
        manifest.get("negative_results"),
        list(NEGATIVE_IDS),
    )
    audit.check(
        "manifest",
        "explorations",
        tuple(manifest.get("exploration_ids", [])) == EXPLORATION_IDS,
        manifest.get("exploration_ids"),
        list(EXPLORATION_IDS),
    )
    audit.check(
        "manifest",
        "scope",
        manifest.get("scope") == {**EXPECTED_SCOPE, "tier_promoted": False},
        manifest.get("scope"),
        {**EXPECTED_SCOPE, "tier_promoted": False},
    )
    statement = str(manifest.get("statement", ""))
    audit.check(
        "manifest",
        "statement",
        all(
            token in statement
            for token in (
                "Delta V_fut-Delta F063_ad",
                "future-variance",
                "partial-Wick",
                "low-plus-root",
                "root-only",
                "4sqrt(eta zeta)",
            )
        ),
        statement,
        "bridge, algebra, baseline firewall, and operator threshold",
    )
    boundary = str(manifest.get("no_overclaim", ""))
    audit.check(
        "manifest",
        "no_overclaim",
        all(
            token in boundary
            for token in (
                "does not prove",
                "production root-shell",
                "stationary-baseline",
                "OVERLAP_src",
                "Sector-A closure",
            )
        ),
        boundary,
        "explicit open production and global boundaries",
    )

    note_text = NOTE.read_text(encoding="utf-8")
    for index, token in enumerate(NOTE_TOKENS, start=1):
        audit.check(
            "note",
            f"token_{index:02d}",
            token in note_text,
            token in note_text,
            True,
        )
    audit.check(
        "note",
        "unicode_hyphen_policy",
        "\u2011" not in note_text,
        "\u2011" in note_text,
        False,
    )

    reader = PdfReader(PDF)
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_contract = verification.get("pdf", {})
    expected_pages = int(pdf_contract.get("pages", -1))
    audit.check("pdf", "pages", len(reader.pages) == expected_pages, len(reader.pages), expected_pages)
    audit.check("pdf", "no_forms", not (reader.get_fields() or {}), bool(reader.get_fields() or {}), False)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    for token in (
        "R-125 conclusion",
        "primitive trace and future-variance rebate",
        "far-tail Hilbert operator budget",
        "Sector-A closure remain open",
    ):
        audit.check("pdf", f"text_{token[:14]}", token in pdf_text, token in pdf_text, True)
    audit.check(
        "pdf",
        "visual_review_contract",
        pdf_contract.get("visual_qa") == "PASS"
        and "all ten pages" in str(pdf_contract.get("visual_review", "")).lower(),
        pdf_contract,
        "PASS and all ten pages visually reviewed",
    )

    slug = "conditional-variance-forest-bridge-root-shell-operator-boundary"
    surfaces = {
        "claim": (CLAIM_DIR / "claim.md", RESULT_ID),
        "status": (CLAIM_DIR / "status.json", RESULT_ID),
        "results": (REPO / "RESULTS-LEDGER.md", "R-125"),
        "roadmap": (REPO / "ROADMAP.md", "R-125"),
        "todo_source": (REPO / "todo/todo.json", "R-125"),
        "todo_generated": (REPO / "TODO.md", "R-125"),
        "sector_map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "changelog_source": (REPO / "changelog/log.jsonl", "A13 R-125"),
        "changelog_generated": (REPO / "CHANGELOG.md", "A13 R-125"),
        "claims_generated": (REPO / "CLAIMS.md", CLAIM),
        "proof_map": (REPO / "theory/proof-evidence-map.md", "R-125"),
        "index": (CLAIM_DIR / "INDEX.md", slug),
        "lineage": (CLAIM_DIR / "LINEAGE.md", slug),
        "catalog": (REPO / "CATALOG.md", slug),
        "catalog_json": (REPO / "verification/catalog.json", slug),
    }
    surface_text: dict[str, str] = {}
    for label, (path, token) in surfaces.items():
        content = path.read_text(encoding="utf-8")
        surface_text[label] = content
        audit.check("surface", label, token in content, token in content, True)

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in NEGATIVE_IDS:
        audit.check("negative", identifier, identifier in registry, identifier in registry, True)
    exploration_records = [
        json.loads(line)
        for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exploration_map = {str(record.get("id")): record for record in exploration_records}
    for identifier in EXPLORATION_IDS:
        record = exploration_map.get(identifier, {})
        audit.check("exploration", identifier, bool(record), bool(record), True)
    audit.check(
        "exploration",
        "baseline_correction_is_append_only",
        exploration_map.get("EXP-000412", {}).get("related")
        == [{"id": "EXP-000410", "relation": "corrects"}],
        exploration_map.get("EXP-000412", {}).get("related"),
        [{"id": "EXP-000410", "relation": "corrects"}],
    )
    audit.check(
        "exploration",
        "owner_index_correction_is_append_only",
        exploration_map.get("EXP-000413", {}).get("related")
        == [{"id": "EXP-000406", "relation": "corrects"}],
        exploration_map.get("EXP-000413", {}).get("related"),
        [{"id": "EXP-000406", "relation": "corrects"}],
    )

    status = load_json(CLAIM_DIR / "status.json")
    audit.check(
        "semantic",
        "tier_lifecycle",
        status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE",
        (status.get("tier"), status.get("lifecycle")),
        ("T4", "ACTIVE"),
    )
    expected_gates = {
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
    }
    audit.check(
        "semantic",
        "open_gates",
        set(status.get("open_gates", [])) == expected_gates,
        status.get("open_gates"),
        sorted(expected_gates),
    )
    status_boundary = str(status.get("no_overclaim", ""))
    audit.check(
        "semantic",
        "status_no_overclaim",
        all(
            token in status_boundary
            for token in (
                "root-only",
                "production C0=0",
                "OVERLAP_src",
                "Sector-A closure",
            )
        ),
        status_boundary,
        "root-only C0 and global boundaries",
    )
    next_action = str(status.get("next_action", ""))
    audit.check(
        "semantic",
        "status_next_action",
        all(
            token in next_action
            for token in (
                "Delta V_fut-Delta F063_ad",
                "balanced",
                "stationary",
                "root k",
                "visit v",
            )
        ),
        next_action,
        "total symbol, far/balanced, baseline, and owner indices",
    )
    todo = load_json(REPO / "todo/todo.json")
    task = next(item for item in todo.get("tasks", []) if item.get("id") == "T-050")
    task_note = str(task.get("note", ""))
    audit.check(
        "semantic",
        "successor_alignment",
        all(
            token in surface_text["roadmap"] and token in task_note
            for token in ("R-125", "Delta V_fut-Delta F063_ad", "balanced")
        )
        and RESULT_ID in surface_text["sector_map"],
        task_note,
        "R-125 total-symbol successor aligned",
    )

    for key in (
        "adapted_forest_continuum_bound_proved",
        "production_root_shell_factorization_proved",
        "owner_complete_stationary_baseline_sum_proved",
        "overlap_src_proved",
        "nelson_proved",
        "sector_a_closed",
        "tier_promoted",
    ):
        audit.check(
            "firewall",
            key,
            manifest.get("scope", {}).get(key) is False,
            manifest.get("scope", {}).get(key),
            False,
        )

    if INTEGRATED_ASSERTIONS:
        audit.check(
            "contract",
            "integrated_assertion_count",
            len(audit.rows) + 1 == INTEGRATED_ASSERTIONS,
            len(audit.rows) + 1,
            INTEGRATED_ASSERTIONS,
        )

    diagnostics = {
        "child_stdout": {
            "primary": primary_stdout.strip(),
            "independent": independent_stdout.strip(),
        },
        "child_stderr": {
            "primary": primary_stderr.strip(),
            "independent": independent_stderr.strip(),
        },
        "pdf": {"pages": len(reader.pages), "sha256": digest(PDF)},
        "note_sha256": digest(NOTE),
        "manifest_sha256": digest(MANIFEST),
        "corrections": {
            "baseline": "EXP-000412",
            "root_visit_owner_index": "EXP-000413",
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    failed = [row for row in payload["assertions"] if row["status"] != "PASS"]
    for row in failed[:25]:
        print(
            f"FAIL {row['group']}: {row['name']}: "
            f"{row['actual']} != {row['expected']}"
        )
    print(
        f"R-125 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']}; "
        f"aggregate {PRIMARY_ASSERTIONS + INDEPENDENT_ASSERTIONS + payload['assertions_passed']}/"
        f"{payload['aggregate_assertions']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
