#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-121 A13 result."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
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
RESULT_ID = "A13-CLASSII-CARTAN-PATHSPACE-EXACTNESS-FIXED-SKEW-SOBOLEV-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-cartan-pathspace-exactness-fixed-skew-sobolev-boundary-260729-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-cartan-pathspace-exactness-fixed-skew-sobolev-boundary-260729-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-29-primary-cartan-pathspace-exactness-fixed-skew-sobolev-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-29-independent-cartan-pathspace-exactness-fixed-skew-sobolev-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-29-integrated-cartan-pathspace-exactness-fixed-skew-sobolev-boundary/result.json"

PRIMARY_SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-independent/1.0"
INTEGRATED_SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-integrated/1.0"
MANIFEST_SCHEMA = "tect/a13-cartan-pathspace-exactness-fixed-skew-sobolev-manifest/1.0"
PRIMARY_ASSERTIONS = 78
INDEPENDENT_ASSERTIONS = 64

AUTHORITY_PATHS = {
    "governance": REPO / "GOVERNANCE.md",
    "a1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r071": CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
    "r075": CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
    "r102": CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
    "r120": CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
}

NOTE_TOKENS = (
    "R-121 conclusion",
    "Theorem 2.1 (exact two-visit owner telescope)",
    "Theorem 4.1 (path-space exactness lemma)",
    "Theorem 5.2 (sharp fixed-skew Sobolev one-use boundary)",
    "20}{729}",
    "2720}{729}",
    "2680}{729}",
    "the coefficient moment is five",
    "R-120 zeroth-order coefficient class",
    "Devil's-advocate review",
    "Sector-A closure",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def payload_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
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
        return {
            "schema": INTEGRATED_SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "children": {
                "primary": {"path": relative(PRIMARY_RESULT), "sha256": digest(PRIMARY_RESULT)},
                "independent": {"path": relative(INDEPENDENT_RESULT), "sha256": digest(INDEPENDENT_RESULT)},
            },
            "no_overclaim": (
                "Integrated PASS certifies R-121's exact owner telescope, path-space correction, "
                "fixed-skew s<1 deterministic one-use theorem, and H^{-11/10} method boundary. "
                "It does not certify adapted D0/D1, an adapted R-063 forest, a production fifth "
                "H^{-3/5} moment, A13 one-use, Nelson, or Sector A closure."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r121-child-") as directory:
        output = Path(directory) / "result.json"
        try:
            process = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            return {"status": "EXECUTION_ERROR", "error": str(error)}, "", str(error)
        if process.returncode != 0:
            return {"status": "EXECUTION_ERROR", "returncode": process.returncode}, process.stdout, process.stderr
        if not output.is_file():
            return {"status": "MISSING_OUTPUT"}, process.stdout, process.stderr
        return load_json(output), process.stdout, process.stderr


def child_contract(
    audit: Audit,
    name: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    assertions: int,
) -> None:
    audit.check("child", f"{name}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{name}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{name}_result_id", fresh.get("result_id") == RESULT_ID, fresh.get("result_id"), RESULT_ID)
    audit.check("child", f"{name}_assertions", fresh.get("assertions_total") == assertions, fresh.get("assertions_total"), assertions)
    audit.check("child", f"{name}_all_passed", fresh.get("assertions_passed") == assertions, fresh.get("assertions_passed"), assertions)
    audit.check("child", f"{name}_deterministic_payload", fresh == stored, payload_digest(fresh), payload_digest(stored))


def manifest_file_entry_ok(entry: Any, path: Path, version: str | None = None) -> bool:
    if not isinstance(entry, dict):
        return False
    expected = {"path": relative(path), "sha256": digest(path)}
    if version is not None:
        expected["version"] = version
    return all(entry.get(key) == value for key, value in expected.items())


def verify_manifest(audit: Audit, manifest: dict[str, Any], pages: int, fields: Any) -> None:
    audit.check("manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA)
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "result_ledger_id", manifest.get("result_ledger_id") == "R-121", manifest.get("result_ledger_id"), "R-121")
    audit.check("manifest", "claim", manifest.get("claim") == CLAIM, manifest.get("claim"), CLAIM)
    audit.check("manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")

    authority = manifest.get("authority", {})
    for key, path in AUTHORITY_PATHS.items():
        audit.check("authority", key, manifest_file_entry_ok(authority.get(key), path), authority.get(key), {"path": relative(path), "sha256": digest(path)})

    source_paths = {
        "primary": (PRIMARY, "1.0.0"),
        "independent": (INDEPENDENT, "1.0.0"),
        "verifier": (VERIFIER, "1.0.0"),
        "proof_note": (NOTE, "1.0"),
    }
    sources = manifest.get("sources", {})
    for key, (path, version) in source_paths.items():
        audit.check("source", key, manifest_file_entry_ok(sources.get(key), path, version), sources.get(key), {"path": relative(path), "sha256": digest(path), "version": version})

    children = manifest.get("child_results", {})
    for key, path in {"primary": PRIMARY_RESULT, "independent": INDEPENDENT_RESULT}.items():
        audit.check("child_result", key, manifest_file_entry_ok(children.get(key), path), children.get(key), {"path": relative(path), "sha256": digest(path)})

    pdf_entry = manifest.get("proof_pdf", {})
    expected_pdf = {
        "path": relative(PDF),
        "sha256": digest(PDF),
        "version": "1.0",
        "pages": pages,
        "size_bytes": PDF.stat().st_size,
        "form_check": "PASS",
        "overfull_hbox_count": 0,
        "visual_qa": "PASS",
    }
    audit.check("pdf", "manifest_entry", all(pdf_entry.get(k) == v for k, v in expected_pdf.items()), pdf_entry, expected_pdf)
    audit.check("pdf", "page_count", pages == 8, pages, 8)
    audit.check("pdf", "no_acroform_fields", not fields, bool(fields), False)

    contract = manifest.get("run_contract", {})
    expected_contract = {
        "primary_schema": PRIMARY_SCHEMA,
        "independent_schema": INDEPENDENT_SCHEMA,
        "integrated_schema": INTEGRATED_SCHEMA,
        "primary_assertions": PRIMARY_ASSERTIONS,
        "independent_assertions": INDEPENDENT_ASSERTIONS,
    }
    for key, value in expected_contract.items():
        audit.check("contract", key, contract.get(key) == value, contract.get(key), value)

    correction = manifest.get("correction", {})
    expected_correction = {
        "mandatory_plus_40_over_729_companion": False,
        "isolated_minus_40_over_729_retained": True,
        "historical_r119_r120_artifacts_mutated": False,
    }
    for key, value in expected_correction.items():
        audit.check("correction", key, correction.get(key) is value, correction.get(key), value)

    consequence = manifest.get("consequence", {})
    expected_consequence = {
        "two_visit_owner_telescope": True,
        "pathspace_exactness_correction": True,
        "fixed_skew_s_less_than_one_theorem": True,
        "unshifted_r071_fifth_moment_sufficient": True,
        "hminus_11_over_10_first_order_reuse": False,
        "adapted_d0_d1": False,
        "adapted_cartan_fifth_moment": False,
        "one_use_source_sextic_aggregation": False,
        "full_overlap_src": False,
        "nelson": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    for key, value in expected_consequence.items():
        audit.check("consequence", key, consequence.get(key) is value, consequence.get(key), value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=120)
    arguments = parser.parse_args()
    audit = Audit()

    surface_paths = [
        REPO / "RESULTS-LEDGER.md",
        REPO / "ROADMAP.md",
        REPO / "negative-results/registry.md",
        REPO / "explorations/log.jsonl",
        REPO / "todo/todo.json",
        CLAIM_DIR / "claim.md",
        CLAIM_DIR / "status.json",
    ]
    required = [PRIMARY, INDEPENDENT, VERIFIER, NOTE, PDF, MANIFEST, PRIMARY_RESULT, INDEPENDENT_RESULT, *AUTHORITY_PATHS.values(), *surface_paths]
    for path in required:
        audit.check("filesystem", relative(path), path.is_file(), path.is_file(), True)
    if any(not path.is_file() for path in required):
        payload = audit.finish({"error": "required file missing"})
        atomic_json(arguments.output, payload)
        print(f"R-121 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
        return 1

    fresh_primary, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    fresh_independent, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", fresh_primary, stored_primary, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", fresh_independent, stored_independent, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    primary_diag = fresh_primary.get("diagnostics", {})
    independent_diag = fresh_independent.get("diagnostics", {})
    primary_owner = primary_diag.get("owner_current", {})
    independent_owner = independent_diag.get("owner_current", {})
    primary_skew = primary_diag.get("fixed_skew", {})
    independent_skew = independent_diag.get("path_skew_sobolev", {})
    audit.check("cross", "K_R_curl_primary", primary_owner.get("repo_curls", {}).get("K_R") == "-40/729", primary_owner.get("repo_curls", {}).get("K_R"), "-40/729")
    audit.check("cross", "K_R_curl_independent", independent_owner.get("repo_curls", {}).get("K_R") == "-40/729", independent_owner.get("repo_curls", {}).get("K_R"), "-40/729")
    audit.check("cross", "M_U_curl", primary_owner.get("repo_curls", {}).get("M_U") == "2720/729", primary_owner.get("repo_curls", {}).get("M_U"), "2720/729")
    audit.check("cross", "full_curl", independent_owner.get("repo_curls", {}).get("full") == "2680/729", independent_owner.get("repo_curls", {}).get("full"), "2680/729")
    audit.check("cross", "ellipse_hessian_primary", primary_owner.get("normalized_ellipse_mixed_hessian") == "20/729", primary_owner.get("normalized_ellipse_mixed_hessian"), "20/729")
    audit.check("cross", "ellipse_hessian_independent", independent_owner.get("normalized_ellipse_mixed_hessian") == "20/729", independent_owner.get("normalized_ellipse_mixed_hessian"), "20/729")
    audit.check("cross", "absolute_sum_primary", primary_skew.get("absolute_operator_sum") == "5/2", primary_skew.get("absolute_operator_sum"), "5/2")
    audit.check("cross", "absolute_sum_independent", independent_skew.get("absolute_operator_sum") == "5/2", independent_skew.get("absolute_operator_sum"), "5/2")
    audit.check("cross", "wedge_constant_primary", primary_skew.get("canonical_wedge_l2_constant") == "1/2", primary_skew.get("canonical_wedge_l2_constant"), "1/2")
    audit.check("cross", "wedge_constant_independent", independent_skew.get("canonical_wedge_l2_constant") == "1/2", independent_skew.get("canonical_wedge_l2_constant"), "1/2")
    audit.check("cross", "moment_primary", primary_skew.get("s_three_fifths", {}).get("moment") == "5", primary_skew.get("s_three_fifths", {}).get("moment"), "5")
    independent_moment = independent_skew.get("s_three_fifths", {}).get("moment")
    audit.check("cross", "moment_independent", independent_moment in {"5", "5/1"}, independent_moment, "5 exactly")

    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    forbidden = ("import sympy", "import numpy", "import scipy", PRIMARY.name, relative(PRIMARY_RESULT))
    for token in forbidden:
        audit.check("independence", token, token not in independent_text, token in independent_text, False)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        audit.check("note", token[:48], token in note_text, token in note_text, True)

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    fields = reader.get_fields()
    extracted = [(page.extract_text() or "").strip() for page in reader.pages]
    audit.check("pdf", "all_pages_extract", len(extracted) == 8 and all(len(text) > 200 for text in extracted), [len(text) for text in extracted], "eight pages, each >200 chars")
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages, fields)

    surfaces = {path.name if path.parent == REPO else relative(path): path.read_text(encoding="utf-8") for path in surface_paths}
    surface_tokens = {
        "RESULTS-LEDGER.md": ("<a id=\"r-121\"></a>", RESULT_ID),
        "ROADMAP.md": ("R-121", "fifth H^{-3/5} moment"),
        "negative-results/registry.md": (
            "AUDIT-2026-07-29-A13-R119-R120-CARTAN-COMPANION-INFERENCE",
            "NG-2026-07-29-A13-FIRST-ORDER-HMINUS-11-10-CARTAN-REUSE",
        ),
        "explorations/log.jsonl": ("EXP-000376", "EXP-000380", "R-121"),
        "todo/todo.json": ("R-121", "T-050"),
        relative(CLAIM_DIR / "claim.md"): (RESULT_ID, "20/729", "moment five"),
        relative(CLAIM_DIR / "status.json"): (RESULT_ID, "EXP-000376--EXP-000380", "Tier stays T4"),
    }
    for surface, tokens in surface_tokens.items():
        text = surfaces[surface]
        for token in tokens:
            audit.check("surface", f"{surface}:{token[:28]}", token in text, token in text, True)

    declared_total = manifest.get("run_contract", {}).get("integrated_assertions")
    final_total = len(audit.rows) + 1
    audit.check("contract", "integrated_assertions", declared_total == final_total, declared_total, final_total)

    diagnostics = {
        "primary_stdout": primary_stdout.strip(),
        "primary_stderr": primary_stderr.strip(),
        "independent_stdout": independent_stdout.strip(),
        "independent_stderr": independent_stderr.strip(),
        "pdf_pages": pages,
        "pdf_fields": bool(fields),
        "mandatory_companion": False,
        "adapted_d0_d1": "open",
        "adapted_fifth_moment": "open",
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-121 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}; "
        f"children {PRIMARY_ASSERTIONS}/{PRIMARY_ASSERTIONS}, {INDEPENDENT_ASSERTIONS}/{INDEPENDENT_ASSERTIONS}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
