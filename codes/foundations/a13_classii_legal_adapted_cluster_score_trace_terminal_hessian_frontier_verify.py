#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-119 A13 result."""

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
RESULT_ID = "A13-CLASSII-LEGAL-ADAPTED-CLUSTER-SCORE-TRACE-TERMINAL-HESSIAN-FRONTIER"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-legal-adapted-cluster-score-trace-terminal-hessian-frontier-260729-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-legal-adapted-cluster-score-trace-terminal-hessian-frontier-260729-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-29-primary-legal-adapted-cluster-score-trace-terminal-hessian-frontier/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-29-independent-legal-adapted-cluster-score-trace-terminal-hessian-frontier/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-29-integrated-legal-adapted-cluster-score-trace-terminal-hessian-frontier/result.json"

PRIMARY_SCHEMA = "tect/a13-legal-adapted-cluster-score-trace-terminal-hessian-frontier-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-legal-adapted-cluster-score-trace-terminal-hessian-frontier-independent/1.0"
INTEGRATED_SCHEMA = "tect/a13-legal-adapted-cluster-score-trace-terminal-hessian-frontier-integrated/1.0"
PRIMARY_ASSERTIONS = 45
INDEPENDENT_ASSERTIONS = 28

NOTE_TOKENS = (
    "R-119",
    RESULT_ID,
    "Theorem 3.1 (aggregate zero and first chaos)",
    "Theorem 4.1 (bare Jacobian heat no-go)",
    "Theorem 5.1 (global terminal-Hessian factorization)",
    "mixed interior",
    "45/45",
    "28/28",
    "Sector-A closure",
)

AUTHORITY_PATHS = {
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r068": CLAIM_DIR / "classii_tip_safe_grouped_harvest_carleson_reduction_manifest.json",
    "r082": CLAIM_DIR / "classii_stopped_current_far_complete_current_near_reduction_manifest.json",
    "r093": CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r102": CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r108": CLAIM_DIR / "classii_complete_cluster_quotient_carleson_frontier_manifest.json",
    "r115": CLAIM_DIR / "classii_scalar_k2k_four_moment_radau_all_amplitude_manifest.json",
    "r116": CLAIM_DIR / "classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_manifest.json",
    "r118": CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
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
                "Integrated PASS certifies R-119's legal-chart reconstruction, exact "
                "score--trace criterion, bare-heat no-go, scoped positive diagnostics, "
                "and global quotient-Hessian theorem only. The production A1 low-chaos "
                "identities, spatial multiplier/synthesis, one-use, Nelson, and Sector A remain open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r119-child-") as directory:
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


def verify_manifest(audit: Audit, manifest: dict[str, Any], pages: int, fields: Any) -> None:
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "claim_id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    status = str(manifest.get("status", ""))
    audit.check("manifest", "tier_boundary", "T4" in status and "SECTOR A OPEN" in status, status, "T4 ... SECTOR A OPEN")

    authorities = manifest.get("authority", {})
    for name, path in AUTHORITY_PATHS.items():
        entry = authorities.get(name, {}).get("manifest", {}) if isinstance(authorities, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        audit.check("authority", name, entry == expected, entry, expected)

    sources = manifest.get("sources", {})
    for name, path in {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": VERIFIER, "proof_note": NOTE}.items():
        entry = sources.get(name, {}) if isinstance(sources, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        ok = entry.get("path") == expected["path"] and entry.get("sha256") == expected["sha256"]
        audit.check("manifest", f"source_{name}", ok, entry, expected)

    children = manifest.get("child_results", {})
    for name, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        entry = children.get(name, {}) if isinstance(children, dict) else {}
        expected = {"path": relative(path), "sha256": digest(path)}
        ok = entry.get("path") == expected["path"] and entry.get("sha256") == expected["sha256"]
        audit.check("manifest", f"child_{name}", ok, entry, expected)

    pdf_entry = manifest.get("proof_pdf", {})
    expected_pdf = {"path": relative(PDF), "sha256": digest(PDF), "pages": pages, "size_bytes": PDF.stat().st_size}
    pdf_ok = all(pdf_entry.get(key) == value for key, value in expected_pdf.items())
    audit.check("manifest", "proof_pdf", pdf_ok, pdf_entry, expected_pdf)
    audit.check("manifest", "pdf_no_forms", not fields and pdf_entry.get("form_check") == "PASS", bool(fields), False)
    audit.check("manifest", "visual_qa", pdf_entry.get("visual_qa") == "PASS", pdf_entry.get("visual_qa"), "PASS")

    consequence = manifest.get("consequence", {})
    expected_false = (
        "full_a1_low_chaos_cancellation",
        "mixed_interior_psd",
        "spatial_multiplier_bound",
        "one_use_source_sextic_aggregation",
        "full_overlap_src",
        "nelson",
        "sector_a_closure",
        "tier_promotion",
    )
    for name in expected_false:
        audit.check("scope", name, consequence.get(name) is False, consequence.get(name), False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=120)
    arguments = parser.parse_args()
    audit = Audit()

    required = [PRIMARY, INDEPENDENT, VERIFIER, NOTE, PDF, MANIFEST, PRIMARY_RESULT, INDEPENDENT_RESULT, *AUTHORITY_PATHS.values()]
    for path in required:
        audit.check("preflight", f"exists_{path.name}", path.is_file(), relative(path) if path.exists() else str(path), "file exists")

    if any(not path.is_file() for path in required):
        payload = audit.finish({"preflight": "missing required file"})
        atomic_json(arguments.output, payload)
        print(f"{payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
        return 1

    primary_fresh, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    independent_fresh, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    primary_stored = load_json(PRIMARY_RESULT)
    independent_stored = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", primary_fresh, primary_stored, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", independent_fresh, independent_stored, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    primary_diag = primary_fresh.get("diagnostics", {})
    independent_diag = independent_fresh.get("diagnostics", {})
    audit.check(
        "cross",
        "one_pair_cost",
        primary_diag.get("one_pair", {}).get("unit_sigma_double_divergence_cost") == "2"
        and independent_diag.get("one_pair_cost") == "2/1",
        [primary_diag.get("one_pair", {}).get("unit_sigma_double_divergence_cost"), independent_diag.get("one_pair_cost")],
        ["2", "2/1"],
    )
    audit.check("cross", "mixed_interior_boundary", primary_diag.get("scalar_model", {}).get("mixed_interior_psd_proved") is False and independent_diag.get("mixed_interior_psd_proved") is False, [primary_diag.get("scalar_model", {}).get("mixed_interior_psd_proved"), independent_diag.get("mixed_interior_psd_proved")], [False, False])
    audit.check("cross", "sector_a_open", primary_diag.get("consequence", {}).get("sector_a_closure") is False and independent_diag.get("sector_a_closure") is False, [primary_diag.get("consequence", {}).get("sector_a_closure"), independent_diag.get("sector_a_closure")], [False, False])

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        audit.check("note", f"token_{hashlib.sha256(token.encode()).hexdigest()[:10]}", token in note_text, token if token in note_text else "missing", token)
    audit.check("note", "english_only_no_hangul", not any("\uac00" <= character <= "\ud7a3" for character in note_text), "Hangul absent", "Hangul absent")

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    fields = reader.get_fields()
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "nonempty", PDF.stat().st_size > 50_000, PDF.stat().st_size, ">50000")
    audit.check("pdf", "page_range", 8 <= pages <= 16, pages, "8..16")
    audit.check("pdf", "no_forms", not fields, bool(fields), False)
    for token in ("R-119", "bare Jacobian heat no-go", "global terminal-Hessian", "Sector-A closure"):
        audit.check("pdf", f"text_{hashlib.sha256(token.encode()).hexdigest()[:10]}", token in extracted, token if token in extracted else "missing", token)
    audit.check("pdf", "no_literal_tex_debris", "qquad" not in extracted and "textwidth" not in extracted, "clean", "clean")

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages, fields)

    ledger = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negative = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    explorations = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    todo = (REPO / "TODO.md").read_text(encoding="utf-8")
    main_line = (REPO / "theory/main-proof-line.md").read_text(encoding="utf-8")
    audit.check("public", "results_ledger", '<a id="r-119"></a>' in ledger and RESULT_ID in ledger, "R-119" in ledger, True)
    audit.check("public", "negative_registry", "NG-2026-07-29-A13-BARE-JACOBIAN-HEAT-LOW-CHAOS-CANCELLATION" in negative, "negative present" if "NG-2026-07-29-A13-BARE-JACOBIAN-HEAT-LOW-CHAOS-CANCELLATION" in negative else "missing", "negative present")
    audit.check("public", "claim_card", "R-119" in claim_text and RESULT_ID in claim_text, "R-119" in claim_text, True)
    audit.check("public", "status_card", "R-119" in str(status.get("statement")) and status.get("tier") == "T4", [status.get("tier"), "R-119" in str(status.get("statement"))], ["T4", True])
    audit.check("public", "exploration_range", all(f"EXP-{number:06d}" in explorations for number in range(364, 371)), "EXP-000364--EXP-000370", "present")
    audit.check("public", "todo_checkpoint", "R-119" in todo and "T-050" in todo, "R-119" in todo, True)
    audit.check("public", "main_proof_line", "R-119" in main_line, "R-119" in main_line, True)

    diagnostics = {
        "child_stdout": {"primary": primary_stdout.strip(), "independent": independent_stdout.strip()},
        "child_stderr": {"primary": primary_stderr.strip(), "independent": independent_stderr.strip()},
        "pdf": {"pages": pages, "size_bytes": PDF.stat().st_size, "forms": bool(fields)},
        "manifest_sha256": digest(MANIFEST),
        "production_boundary": {
            "legal_chart_reconstructed": True,
            "score_trace_criterion_proved": True,
            "bare_heat_route_failed": True,
            "global_terminal_hessian_proved": True,
            "full_a1_low_chaos_cancellation": False,
            "one_use_source_sextic_aggregation": False,
            "sector_a_closure": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"{payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
