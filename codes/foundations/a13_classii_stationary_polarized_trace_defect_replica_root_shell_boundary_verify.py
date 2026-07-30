#!/usr/bin/env python3
"""Integrated verifier for the scoped R-124 A13 checkpoint."""

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
    "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-"
    "REPLICA-ROOT-SHELL-BOUNDARY"
)
SCHEMA = (
    "tect/a13-stationary-polarized-trace-defect-"
    "replica-root-shell-boundary-integrated/1.0"
)
MANIFEST_SCHEMA = (
    "tect/a13-stationary-polarized-trace-defect-"
    "replica-root-shell-boundary-manifest/1.0"
)
PRIMARY_SCHEMA = (
    "tect/a13-stationary-polarized-trace-defect-"
    "replica-root-shell-boundary-primary/1.0"
)
INDEPENDENT_SCHEMA = (
    "tect/a13-stationary-polarized-trace-defect-"
    "replica-root-shell-boundary-independent/1.0"
)
PRIMARY_ASSERTIONS = 55
INDEPENDENT_ASSERTIONS = 55
INTEGRATED_ASSERTIONS = 140

CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_stationary_polarized_trace_defect_replica_root_shell_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_stationary_polarized_trace_defect_replica_root_shell_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-stationary-polarized-trace-defect-replica-root-shell-boundary-260730-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
MANIFEST = CLAIM_DIR / "classii_stationary_polarized_trace_defect_replica_root_shell_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-30-independent-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-integrated-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"

AUTHORITY_PATHS = {
    "governance": REPO / "GOVERNANCE.md",
    "a1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r093": CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r108": CLAIM_DIR / "classii_complete_cluster_quotient_carleson_frontier_manifest.json",
    "r116": CLAIM_DIR / "classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_manifest.json",
    "r118": CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
    "r120": CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
    "r121": CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json",
    "r122": CLAIM_DIR / "classii_derivative_free_low_chaos_adapted_fifth_moment_cartan_boundary_manifest.json",
    "r123": CLAIM_DIR / "classii_six_row_trace_excess_direct_action_boundary_manifest.json",
}

NOTE_TOKENS = (
    "R-124 conclusion",
    "Theorem 2.1 (stationary-polarized trace secant)",
    "Theorem 3.1 (moving-endpoint subdivision invariance)",
    "moving endpoint",
    "2680/729",
    "critical resonance blocks zeroth-order reuse",
    "rare-event obstruction to separated Carleson moments",
    "signed aggregate route and its acceptance test",
    "replica/Hermite normal form",
    "sharp legal first-linear-row theorem",
    "\\eta_{\\rm row}",
    "REPLICA-VARIANCE-AUTOMATIC-TRACE-DOMINATION",
    "covariant-Hessian and OU/Follmer fallbacks",
    "-15CH^2",
    "Exact OU Hessian representation",
    "Ten-round synthesis",
    "Sector-A closure remain open",
)

NEGATIVE_IDS = (
    "AUDIT-2026-07-29-A13-R119-R120-CARTAN-COMPANION-INFERENCE",
    "NG-2026-07-29-A13-FIRST-ORDER-HMINUS-11-10-CARTAN-REUSE",
    "NG-2026-07-29-A13-BARE-JACOBIAN-HEAT-LOW-CHAOS-CANCELLATION",
    "NG-2026-07-28-A13-RATIONAL-TAYLOR-OWNER-SUBDIVISION",
    "NG-2026-07-29-A13-ADAPTED-CARTAN-FIFTH-MOMENT-GRAPH-TRANSFER",
    "NG-2026-07-25-A13-GENERIC-WEIGHTED-DOOB-SHORTCUTS",
    "NG-2026-07-30-A13-RAW-SIX-CURRENT-HESSIAN-POSITIVITY",
    "NG-2026-07-28-A13-ALL-LAW-POINTWISE-RELATIVE-BRACKET",
    "NG-2026-07-28-A13-TOTAL-A9-TIME-INTEGRATION-IDENTITY",
    "NG-2026-07-30-A13-REPLICA-VARIANCE-AUTOMATIC-TRACE-DOMINATION",
)

EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(396, 406))

EXPECTED_SCOPE = {
    "coefficient_identity_proved": False,
    "complete_production_trace_excess_proved": False,
    "correlated_root_shell_proved": False,
    "stationary_baseline_sum_proved": False,
    "overlap_src_proved": False,
    "nelson_proved": False,
    "sector_a_closed": False,
    "tier_promoted": False,
}


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
        count_ok = len(self.rows) == INTEGRATED_ASSERTIONS
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
            "diagnostics": {**diagnostics, "expected_assertions": INTEGRATED_ASSERTIONS},
            "no_overclaim": (
                "R-124 leaves the coefficient identity, correlated signed root-shell "
                "estimate, separate stationary-baseline sum bound, OVERLAP_src, "
                "Nelson, removals, interacting measure, and Sector A open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r124-") as directory:
        output = Path(directory) / "result.json"
        completed = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
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


def child_contract(
    audit: Audit,
    label: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
) -> None:
    returncode = fresh.pop("_returncode", None)
    audit.check("child", f"{label}_returncode", returncode == 0, returncode, 0)
    audit.check("child", f"{label}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{label}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{label}_total", fresh.get("assertions_total") == 55, fresh.get("assertions_total"), 55)
    audit.check("child", f"{label}_passed", fresh.get("assertions_passed") == 55, fresh.get("assertions_passed"), 55)
    audit.check("child", f"{label}_stored_reproduces", fresh == stored, fresh == stored, True)
    flags = fresh.get("diagnostics", {}).get("scope_flags", {})
    for name in (
        "complete_production_trace_excess_proved",
        "overlap_src_proved",
        "nelson_proved",
        "sector_a_closed",
        "tier_promoted",
    ):
        audit.check("scope", f"{label}_{name}", flags.get(name) is False, flags.get(name), False)


def file_entry_ok(entry: Any, path: Path, version: str | None = None) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("path") != relative(path) or entry.get("sha256") != digest(path):
        return False
    return version is None or entry.get("version") == version


def verify_manifest(audit: Audit, manifest: dict[str, Any]) -> None:
    verification = manifest.get("verification", {})
    metadata_checks = (
        ("schema", manifest.get("schema"), MANIFEST_SCHEMA),
        ("package_version", manifest.get("package_version"), "1.0.0"),
        ("issued", manifest.get("issued"), "2026-07-30"),
        ("claim", manifest.get("claim_id"), CLAIM),
        ("result", manifest.get("result_id"), RESULT_ID),
        ("ledger", manifest.get("result_ledger_id"), "R-124"),
        ("tier", manifest.get("tier"), "T4"),
        ("evidence_grade", manifest.get("evidence_grade"), ["ANALYTIC", "EXACT", "EXECUTED"]),
        ("primary_count", verification.get("primary_assertions"), PRIMARY_ASSERTIONS),
        ("independent_count", verification.get("independent_assertions"), INDEPENDENT_ASSERTIONS),
        ("integrated_count", verification.get("integrated_assertions"), INTEGRATED_ASSERTIONS),
        ("primary_schema", verification.get("primary_schema"), PRIMARY_SCHEMA),
        ("independent_schema", verification.get("independent_schema"), INDEPENDENT_SCHEMA),
        ("integrated_schema", verification.get("integrated_schema"), SCHEMA),
    )
    for name, actual, expected in metadata_checks:
        audit.check("manifest", name, actual == expected, actual, expected)
    pdf_contract = verification.get("pdf", {})
    audit.check(
        "manifest",
        "pdf_contract",
        pdf_contract.get("pages") == 10
        and "all ten pages" in str(pdf_contract.get("visual_review", "")).lower(),
        pdf_contract,
        {"pages": 10, "visual_review": "all ten pages visually reviewed"},
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

    audit.check("manifest", "negatives", tuple(manifest.get("negative_results", [])) == NEGATIVE_IDS, manifest.get("negative_results"), list(NEGATIVE_IDS))
    audit.check("manifest", "explorations", tuple(manifest.get("exploration_ids", [])) == EXPLORATION_IDS, manifest.get("exploration_ids"), list(EXPLORATION_IDS))
    audit.check("manifest", "scope", manifest.get("scope") == EXPECTED_SCOPE, manifest.get("scope"), EXPECTED_SCOPE)
    boundary = str(manifest.get("no_overclaim", ""))
    audit.check("manifest", "no_overclaim", all(token in boundary for token in ("does not prove", "stationary-baseline", "OVERLAP_src", "Sector-A closure")), boundary, "explicit open boundaries")
    statement = str(manifest.get("statement", ""))
    audit.check("manifest", "statement", all(token in statement for token in ("stationary-polarized", "3/(125P)", "correlated signed root-shell", "remain open")), statement, "theorem, sharp row, and open boundary")


def independent_imports_ok(path: Path) -> tuple[bool, list[str]]:
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
        "dataclasses",
        "fractions",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
        "typing",
    }
    return roots <= allowed, sorted(roots)


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

    if any(not path.is_file() for path in required):
        payload = audit.finish(
            {"missing": [relative(path) for path in required if not path.is_file()]}
        )
        atomic_json(arguments.output, payload)
        print(
            f"R-124 integrated {payload['status']}: "
            f"{payload['assertions_passed']}/{payload['assertions_total']}"
        )
        return 1

    primary_fresh, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    independent_fresh, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    primary_stored = load_json(PRIMARY_RESULT)
    independent_stored = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", primary_fresh, primary_stored, PRIMARY_SCHEMA)
    child_contract(audit, "independent", independent_fresh, independent_stored, INDEPENDENT_SCHEMA)

    imports_ok, imported_roots = independent_imports_ok(INDEPENDENT)
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    audit.check(
        "independence",
        "standard_library_only",
        imports_ok and PRIMARY.stem not in independent_source,
        imported_roots,
        "standard library and no primary import",
    )
    primary_signatures = [
        (row.get("group"), row.get("name")) for row in primary_stored["assertions"]
    ]
    independent_signatures = [
        (row.get("group"), row.get("name"))
        for row in independent_stored["assertions"]
    ]
    signature_ok = (
        len(primary_signatures) == 55
        and len(independent_signatures) == 55
        and len(set(primary_signatures)) == 55
        and len(set(independent_signatures)) == 55
        and set(primary_signatures) == set(independent_signatures)
    )
    audit.check("independence", "matching_unique_signatures", signature_ok, signature_ok, True)

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest)

    note_text = NOTE.read_text(encoding="utf-8")
    for index, token in enumerate(NOTE_TOKENS, start=1):
        audit.check("note", f"token_{index:02d}", token in note_text, token in note_text, True)
    audit.check("note", "unicode_hyphen_policy", "\u2011" not in note_text, "\u2011" in note_text, False)

    reader = PdfReader(PDF)
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "pages", len(reader.pages) == 10, len(reader.pages), 10)
    audit.check("pdf", "no_forms", not (reader.get_fields() or {}), bool(reader.get_fields() or {}), False)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    for token in (
        "R-124 conclusion",
        "Exact OU Hessian representation",
        "Sector-A closure remain open",
    ):
        audit.check("pdf", f"text_{token[:12]}", token in pdf_text, token in pdf_text, True)

    surfaces = {
        "claim": (CLAIM_DIR / "claim.md", RESULT_ID),
        "status": (CLAIM_DIR / "status.json", RESULT_ID),
        "results": (REPO / "RESULTS-LEDGER.md", "R-124"),
        "roadmap": (REPO / "ROADMAP.md", "R-124"),
        "todo_source": (REPO / "todo/todo.json", "R-124"),
        "todo_generated": (REPO / "TODO.md", "R-124"),
        "sector_map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "changelog_source": (REPO / "changelog/log.jsonl", "A13 R-124"),
        "changelog_generated": (REPO / "CHANGELOG.md", "A13 R-124"),
        "claims_generated": (REPO / "CLAIMS.md", CLAIM),
        "proof_map": (REPO / "theory/proof-evidence-map.md", "R-124"),
        "index": (CLAIM_DIR / "INDEX.md", "stationary-polarized-trace-defect-replica-root-shell-boundary"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", "stationary-polarized-trace-defect-replica-root-shell-boundary"),
        "catalog": (REPO / "CATALOG.md", "stationary-polarized-trace-defect-replica-root-shell-boundary"),
        "catalog_json": (REPO / "verification/catalog.json", "stationary-polarized-trace-defect-replica-root-shell-boundary"),
    }
    surface_text: dict[str, str] = {}
    for label, (path, token) in surfaces.items():
        text = path.read_text(encoding="utf-8")
        surface_text[label] = text
        audit.check("surface", label, token in text, token in text, True)

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    audit.check("negative", "all_registered", all(identifier in negative_text for identifier in NEGATIVE_IDS), [identifier for identifier in NEGATIVE_IDS if identifier not in negative_text], [])
    exploration_text = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    for identifier in EXPLORATION_IDS:
        audit.check("exploration", identifier, f'"id":"{identifier}"' in exploration_text, f'"id":"{identifier}"' in exploration_text, True)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("semantic", "tier_lifecycle", status.get("tier") == "T4" and status.get("lifecycle") == "ACTIVE", (status.get("tier"), status.get("lifecycle")), ("T4", "ACTIVE"))
    expected_gates = {
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
    }
    audit.check("semantic", "open_gates", set(status.get("open_gates", [])) == expected_gates, status.get("open_gates"), sorted(expected_gates))
    no_overclaim = str(status.get("no_overclaim", ""))
    audit.check("semantic", "no_overclaim", all(token in no_overclaim for token in ("coefficient identity", "stationary-baseline", "OVERLAP_src", "Sector-A closure")), no_overclaim, "all open boundaries")
    next_action = str(status.get("next_action", ""))
    audit.check("semantic", "next_action", all(token in next_action for token in ("R-121 rational", "R-123 primitive trace", "R-063 forest", "root and shell sums", "stationary baseline")), next_action, "coefficient identity, signed sums, and baseline")
    todo_source = load_json(REPO / "todo/todo.json")
    task = next(item for item in todo_source.get("tasks", []) if item.get("id") == "T-050")
    task_note = str(task.get("note", ""))
    alignment_tokens = ("coefficient-level identity", "R-121 rational", "R-123 primitive trace", "stationary-baseline")
    alignment_ok = (
        all(token in surface_text["roadmap"] for token in alignment_tokens)
        and all(token in task_note for token in alignment_tokens)
        and RESULT_ID in surface_text["sector_map"]
    )
    audit.check("semantic", "successor_alignment", alignment_ok, alignment_ok, True)

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
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "overlap_src_proved": False,
            "nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-124 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
