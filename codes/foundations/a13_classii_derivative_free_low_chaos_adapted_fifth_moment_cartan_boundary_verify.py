#!/usr/bin/env python3
"""Integrated verifier for the scoped R-122 A13 result."""

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
RESULT_ID = "A13-CLASSII-DERIVATIVE-FREE-LOW-CHAOS-ADAPTED-FIFTH-MOMENT-CARTAN-BOUNDARY"
SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-integrated/1.0"
MANIFEST_SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-manifest/1.0"
PRIMARY_SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-derivative-free-low-chaos-adapted-fifth-moment-cartan-independent/1.0"
PRIMARY_ASSERTIONS = 82
INDEPENDENT_ASSERTIONS = 57

CLAIM_DIR = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
PRIMARY = REPO / "codes/foundations/a13_classii_derivative_free_low_chaos_adapted_fifth_moment_cartan_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_derivative_free_low_chaos_adapted_fifth_moment_cartan_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary-260729-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
MANIFEST = CLAIM_DIR / "classii_derivative_free_low_chaos_adapted_fifth_moment_cartan_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-29-primary-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-29-independent-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-29-integrated-derivative-free-low-chaos-adapted-fifth-moment-cartan-boundary/result.json"

AUTHORITY_PATHS = {
    "governance": REPO / "GOVERNANCE.md",
    "a1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r071": CLAIM_DIR / "classii_one_form_sobolev_linear_closure_manifest.json",
    "r075": CLAIM_DIR / "classii_invariant_current_principal_oneform_graph_recovery_manifest.json",
    "r102": CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
    "r120": CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
    "r121": CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json",
}

NOTE_TOKENS = (
    "Theorem 2.1 (derivative-free $D_0,D_1$ reconstruction)",
    "D_0=\\E\\Theta_h-\\|A\\|_{\\rm HS}^2-\\E\\|R\\|^2",
    "D_1=\\E[\\xi\\Theta_h]",
    "h_n(\\xi)=\\frac{\\sin(n\\xi)}n",
    "Theorem 4.2 (coherent-amplitude graph nontransfer)",
    "c_J^5e^{20t^2}",
    "\\frac{128}{27}\\ne0",
    "Theorem 6.1 (exact normalized R-102 noncancellation)",
    "\\frac{1360}{729}J+\\frac{1320}{729}J",
    "correlation-preserving",
    "Sector-A closure remain open",
)


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "no_overclaim": (
                "R-122 leaves production cancellation, the complete signed one-use form, "
                "OVERLAP_src, Nelson, removals, measure construction, and Sector A open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r122-") as directory:
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
            return {"status": "MISSING", "returncode": completed.returncode}, completed.stdout, completed.stderr
        payload = load_json(output)
        payload["_returncode"] = completed.returncode
        return payload, completed.stdout, completed.stderr


def child_contract(
    audit: Audit,
    label: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    assertions: int,
) -> None:
    audit.check("child", f"{label}_returncode", fresh.pop("_returncode", None) == 0, fresh.get("_returncode"), 0)
    audit.check("child", f"{label}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{label}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{label}_assertions", fresh.get("assertions_total") == assertions, fresh.get("assertions_total"), assertions)
    audit.check("child", f"{label}_all_pass", fresh.get("assertions_passed") == assertions, fresh.get("assertions_passed"), assertions)
    audit.check("child", f"{label}_stored_reproduces", fresh == stored, fresh == stored, True)


def file_entry_ok(entry: Any, path: Path, version: str | None = None) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("path") != relative(path) or entry.get("sha256") != digest(path):
        return False
    return version is None or entry.get("version") == version


def verify_manifest(audit: Audit, manifest: dict[str, Any], pages: int, fields: Any) -> None:
    audit.check("manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA)
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "result_ledger_id", manifest.get("result_ledger_id") == "R-122", manifest.get("result_ledger_id"), "R-122")
    audit.check("manifest", "claim", manifest.get("claim") == CLAIM, manifest.get("claim"), CLAIM)
    audit.check("manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")

    authority = manifest.get("authority", {})
    for key, path in AUTHORITY_PATHS.items():
        audit.check("authority", key, file_entry_ok(authority.get(key), path), authority.get(key), {"path": relative(path), "sha256": digest(path)})

    sources = manifest.get("sources", {})
    for key, path, version in (
        ("primary", PRIMARY, "1.0.0"),
        ("independent", INDEPENDENT, "1.0.0"),
        ("verifier", VERIFIER, "1.0.0"),
        ("proof_note", NOTE, "1.0"),
    ):
        audit.check("source", key, file_entry_ok(sources.get(key), path, version), sources.get(key), {"path": relative(path), "sha256": digest(path), "version": version})

    children = manifest.get("child_results", {})
    for key, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        audit.check("child_result", key, file_entry_ok(children.get(key), path), children.get(key), {"path": relative(path), "sha256": digest(path)})

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
    audit.check("pdf", "manifest_entry", all(pdf_entry.get(key) == value for key, value in expected_pdf.items()), pdf_entry, expected_pdf)
    audit.check("pdf", "minimum_pages", pages >= 8, pages, ">=8")
    audit.check("pdf", "no_acroform_fields", not fields, bool(fields), False)

    contract = manifest.get("run_contract", {})
    expected_contract = {
        "primary_schema": PRIMARY_SCHEMA,
        "independent_schema": INDEPENDENT_SCHEMA,
        "integrated_schema": SCHEMA,
        "primary_assertions": PRIMARY_ASSERTIONS,
        "independent_assertions": INDEPENDENT_ASSERTIONS,
    }
    for key, value in expected_contract.items():
        audit.check("contract", key, contract.get(key) == value, contract.get(key), value)

    consequence = manifest.get("consequence", {})
    expected_consequence = {
        "derivative_free_D0_D1_representation": True,
        "production_D0_D1_cancellation": False,
        "feedback_derivative_graph_closure": False,
        "standalone_adapted_fifth_moment_from_source_and_sextic": False,
        "automatic_cartan_cancellation": False,
        "correlation_preserving_route_survives": True,
        "complete_one_use": False,
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
        REPO / "governance/sector-a-theorem-map.json",
        CLAIM_DIR / "claim.md",
        CLAIM_DIR / "status.json",
    ]
    required = [PRIMARY, INDEPENDENT, VERIFIER, NOTE, PDF, MANIFEST, PRIMARY_RESULT, INDEPENDENT_RESULT, *AUTHORITY_PATHS.values(), *surface_paths]
    for path in required:
        audit.check("filesystem", relative(path), path.is_file(), path.is_file(), True)
    if any(not path.is_file() for path in required):
        payload = audit.finish({"error": "required file missing"})
        atomic_json(arguments.output, payload)
        print(f"R-122 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
        return 1

    fresh_primary, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    fresh_independent, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    stored_primary = load_json(PRIMARY_RESULT)
    stored_independent = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", fresh_primary, stored_primary, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", fresh_independent, stored_independent, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    primary_diag = fresh_primary.get("diagnostics", {})
    independent_diag = fresh_independent.get("diagnostics", {})
    audit.check("cross", "primary_D0_law", primary_diag.get("derivative_free_low_chaos", {}).get("uses_feedback_derivatives") is False, primary_diag.get("derivative_free_low_chaos", {}).get("uses_feedback_derivatives"), False)
    audit.check("cross", "primary_owner_D1_opposite", primary_diag.get("bounded_owner_identifiability", {}).get("rows", {}).get("plus", {}).get("D1") != primary_diag.get("bounded_owner_identifiability", {}).get("rows", {}).get("minus", {}).get("D1"), primary_diag.get("bounded_owner_identifiability", {}).get("rows", {}), "opposite")
    audit.check("cross", "primary_ray", primary_diag.get("production_rational_ray", {}).get("coefficient_over_amplitude_squared_limit_at_pi_over_2") == "128/27", primary_diag.get("production_rational_ray", {}).get("coefficient_over_amplitude_squared_limit_at_pi_over_2"), "128/27")
    audit.check("cross", "independent_ray", independent_diag.get("production_and_cartan", {}).get("ray_coefficient") == "128/27", independent_diag.get("production_and_cartan", {}).get("ray_coefficient"), "128/27")
    audit.check("cross", "primary_A2", primary_diag.get("complete_cartan_operator", {}).get("A2") == [["0", "-2680/729"], ["2680/729", "0"]], primary_diag.get("complete_cartan_operator", {}).get("A2"), [["0", "-2680/729"], ["2680/729", "0"]])
    audit.check("cross", "independent_A2", independent_diag.get("production_and_cartan", {}).get("A2") == [["0/1", "-2680/729"], ["2680/729", "0/1"]], independent_diag.get("production_and_cartan", {}).get("A2"), [["0/1", "-2680/729"], ["2680/729", "0/1"]])
    audit.check("cross", "primary_joint_route_open", primary_diag.get("correlation_preserving_boundary", {}).get("full_production_bound") is False, primary_diag.get("correlation_preserving_boundary", {}).get("full_production_bound"), False)

    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    for token in ("import sympy", "import numpy", "import scipy", PRIMARY.name, relative(PRIMARY_RESULT)):
        audit.check("independence", token, token not in independent_text, token in independent_text, False)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        audit.check("note", token[:48], token in note_text, token in note_text, True)

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    fields = reader.get_fields()
    extracted = [(page.extract_text() or "").strip() for page in reader.pages]
    audit.check("pdf", "all_pages_extract", pages >= 8 and len(extracted) == pages and all(len(text) > 150 for text in extracted), [len(text) for text in extracted], "at least eight pages, each >150 chars")
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages, fields)

    surfaces = {relative(path): path.read_text(encoding="utf-8") for path in surface_paths}
    surface_tokens = {
        "RESULTS-LEDGER.md": ("<a id=\"r-122\"></a>", RESULT_ID),
        "ROADMAP.md": ("R-122", "correlation-preserving"),
        "negative-results/registry.md": (
            "NG-2026-07-29-A13-FEEDBACK-DERIVATIVE-GRAPH-CLOSURE",
            "NG-2026-07-29-A13-ADAPTED-CARTAN-FIFTH-MOMENT-GRAPH-TRANSFER",
            "NG-2026-07-29-A13-SELFADJOINTNESS-CARTAN-CANCELLATION",
        ),
        "explorations/log.jsonl": ("EXP-000381", "EXP-000385"),
        "todo/todo.json": ("R-122", "T-050"),
        "governance/sector-a-theorem-map.json": ("R-122", RESULT_ID),
        relative(CLAIM_DIR / "claim.md"): (RESULT_ID, "128/27", "correlation-preserving"),
        relative(CLAIM_DIR / "status.json"): (RESULT_ID, "EXP-000381--EXP-000385", "Tier stays T4"),
    }
    for surface, tokens in surface_tokens.items():
        text = surfaces[surface]
        for token in tokens:
            audit.check("surface", f"{surface}:{token[:28]}", token in text, token in text, True)

    lineage_token = "R-119--R-122"
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    audit.check("surface", "lineage-narrative.md:R-119--R-122", lineage_token in lineage_text, lineage_token in lineage_text, True)

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
        "derivative_free_representation": True,
        "standalone_adapted_fifth_moment": False,
        "automatic_cartan_cancellation": False,
        "complete_signed_one_use": False,
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-122 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}; "
        f"children {PRIMARY_ASSERTIONS}/{PRIMARY_ASSERTIONS}, {INDEPENDENT_ASSERTIONS}/{INDEPENDENT_ASSERTIONS}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
