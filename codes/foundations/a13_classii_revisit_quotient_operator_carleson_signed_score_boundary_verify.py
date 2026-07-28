#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-118 A13 result."""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
from fractions import Fraction
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
RESULT_ID = "A13-CLASSII-REVISIT-QUOTIENT-OPERATOR-CARLESON-SIGNED-SCORE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_revisit_quotient_operator_carleson_signed_score_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_revisit_quotient_operator_carleson_signed_score_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-revisit-quotient-operator-carleson-signed-score-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-revisit-quotient-operator-carleson-signed-score-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-revisit-quotient-operator-carleson-signed-score-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-revisit-quotient-operator-carleson-signed-score-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-revisit-quotient-operator-carleson-signed-score-boundary/result.json"

PRIMARY_SCHEMA = "tect/a13-revisit-quotient-operator-carleson-signed-score-boundary-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-revisit-quotient-operator-carleson-signed-score-boundary-independent/1.0"
INTEGRATED_SCHEMA = "tect/a13-revisit-quotient-operator-carleson-signed-score-boundary-integrated/1.0"
PRIMARY_ASSERTIONS = 33
INDEPENDENT_ASSERTIONS = 27

NOTE_TOKENS = (
    "R-118",
    RESULT_ID,
    "Theorem 2.1 (quadratic quotient factorisation)",
    "Theorem 4.1 (visit-count-free operator R-068 extension)",
    "Theorem 6.1 (canonical second-divergence decomposition)",
    "zero and first Wiener chaoses",
    "33/33",
    "27/27",
    "Sector-A closure",
)

AUTHORITY_PATHS = {
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r068": CLAIM_DIR / "classii_tip_safe_grouped_harvest_carleson_reduction_manifest.json",
    "r093": CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r102": CLAIM_DIR / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
    "r104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "r107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r110": CLAIM_DIR / "classii_random_w_skorohod_diagonal_crossmode_boundary_manifest.json",
    "r116": CLAIM_DIR / "classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_manifest.json",
    "r117": CLAIM_DIR / "classii_rational_horizon_uniform_root_trace_margin_boundary_manifest.json",
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


def assertion_status(payload: dict[str, Any], name: str) -> str | None:
    for row in payload.get("assertions", []):
        if isinstance(row, dict) and row.get("name") == name:
            return str(row.get("status"))
    return None


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
                "Integrated PASS certifies R-118's abstract quotient theorem, "
                "operator R-068 extension, canonical Gaussian range, and signed "
                "method boundaries only. The complete adapted owner, one-use, "
                "Nelson, and Sector A remain open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r118-child-") as directory:
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
    for name, path in {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": VERIFIER,
        "proof_note": NOTE,
    }.items():
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
    pdf_ok = (
        isinstance(pdf_entry, dict)
        and pdf_entry.get("path") == relative(PDF)
        and pdf_entry.get("sha256") == digest(PDF)
        and pdf_entry.get("pages") == pages
        and pdf_entry.get("size_bytes") == PDF.stat().st_size
        and pdf_entry.get("form_check") == "PASS"
        and pdf_entry.get("overfull_hbox_count") == 0
        and pdf_entry.get("visual_qa") == "PASS"
        and fields in (None, {})
    )
    audit.check("manifest", "proof_pdf", pdf_ok, pdf_entry, "final non-form PDF hash, size, pages, form, and visual QA pinned")

    consequence = manifest.get("consequence", {})
    prohibited = (
        "complete_adapted_owner",
        "production_specific_positive_random_w_factorization_proved",
        "full_progressive_revisit_extension",
        "one_use_source_sextic_aggregation",
        "full_overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    )
    flags_ok = isinstance(consequence, dict) and all(consequence.get(key) is False for key in prohibited)
    audit.check("manifest", "prohibited_flags_false", flags_ok, {key: consequence.get(key) for key in prohibited} if isinstance(consequence, dict) else consequence, "all false")

    negative_refs = manifest.get("method_boundaries", [])
    expected_negatives = {
        "NG-2026-07-28-A13-UNIVERSAL-PSD-RANDOM-W-DOUBLE-DIVERGENCE",
        "NG-2026-07-28-A13-UNIVERSAL-NONLINEAR-TANGENT-SQUARE-FIRST-NORMALIZER",
        "NG-2026-07-28-A13-FULL-HESSIAN-CARTAN-CHAIN-PRIMITIVE",
    }
    audit.check("manifest", "method_boundaries", expected_negatives.issubset(set(negative_refs)) if isinstance(negative_refs, list) else False, negative_refs, sorted(expected_negatives))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=180)
    arguments = parser.parse_args()

    audit = Audit()
    primary_fresh, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    independent_fresh, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    primary_stored = load_json(PRIMARY_RESULT)
    independent_stored = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", primary_fresh, primary_stored, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", independent_fresh, independent_stored, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    cross_checks = (
        ("primary_quotient", primary_fresh, "fibre_invariance"),
        ("independent_quotient", independent_fresh, "fibre_invariance"),
        ("primary_spectral_power", primary_fresh, "spectral_constant_power"),
        ("independent_spectral_power", independent_fresh, "spectral_constant_power"),
        ("primary_opposite", primary_fresh, "terminal_aggregate_zero"),
        ("independent_opposite", independent_fresh, "terminal_zero"),
        ("primary_mean", primary_fresh, "mean_debt"),
        ("independent_mean", independent_fresh, "mean_debt"),
        ("primary_divergence", primary_fresh, "double_divergence_identity"),
        ("independent_divergence", independent_fresh, "double_divergence"),
        ("independent_homotopy", independent_fresh, "homotopy_remainder"),
    )
    for label, payload, assertion in cross_checks:
        status = assertion_status(payload, assertion)
        audit.check("cross", label, status == "PASS", status, "PASS")

    primary_interpolation = primary_fresh.get("diagnostics", {}).get("interpolation", {})
    independent_interpolation = independent_fresh.get("diagnostics", {}).get("interpolation", {})
    expected_tuple = {
        "theta": "11/20",
        "terminal_sextic_power": "3/20",
        "model_moment": "10/3",
        "eta_power": "11/6",
        "zeta_power": "1/2",
    }
    for name, values in (("primary", primary_interpolation), ("independent", independent_interpolation)):
        observed = {key: values.get(key) for key in expected_tuple}
        audit.check("cross", f"{name}_interpolation_tuple", observed == expected_tuple, observed, expected_tuple)

    note_text = NOTE.read_text(encoding="utf-8")
    missing_note = [token for token in NOTE_TOKENS if token not in note_text]
    audit.check("note", "required_tokens", not missing_note, missing_note, [])
    audit.check("note", "ascii_only", all(ord(character) < 128 for character in note_text), "ASCII" if all(ord(character) < 128 for character in note_text) else "non-ASCII", "ASCII")

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    fields = reader.get_fields()
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_tokens = ("R-118", "operator R-068", "Sector-A closure")
    missing_pdf = [token for token in pdf_tokens if token not in pdf_text]
    audit.check("pdf", "page_count", pages == 8, pages, 8)
    audit.check("pdf", "text_tokens", not missing_pdf, missing_pdf, [])
    audit.check("pdf", "no_form_fields", fields in (None, {}), bool(fields), False)

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages, fields)

    diagnostics = {
        "primary_stdout": primary_stdout.strip(),
        "primary_stderr": primary_stderr.strip(),
        "independent_stdout": independent_stdout.strip(),
        "independent_stderr": independent_stderr.strip(),
        "interpolation_tuple": expected_tuple,
        "note_sha256": digest(NOTE),
        "pdf_sha256": digest(PDF),
        "pdf_pages": pages,
        "pdf_size_bytes": PDF.stat().st_size,
        "manifest_sha256": digest(MANIFEST),
        "runtime": {"python": sys.version.split()[0]},
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Integrated R-118 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
