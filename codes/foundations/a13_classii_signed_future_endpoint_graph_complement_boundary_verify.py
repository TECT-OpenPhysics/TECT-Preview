#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-139 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SIGNED-FUTURE-ENDPOINT-GRAPH-COMPLEMENT-BOUNDARY"
SCHEMA = "tect/a13-signed-future-endpoint-graph-complement-boundary-integrated/1.0"
LEDGER_ID = "R-139"
CLAIM_DIR = REPO / "claims" / CLAIM
NOTE = CLAIM_DIR / "notes/classii-signed-future-endpoint-graph-complement-boundary-260731-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
NEGATIVE_IDS = (
    "NG-2026-07-31-A13-WEDGE-ONLY-FUTURE-TELESCOPE",
    "NG-2026-07-31-A13-TAIL-ONLY-SHIFTED-DOUGLAS-HEADROOM",
)
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(552, 559))
SUCCESSOR = "A13-CLASSII-COMPLETE-RAW-DOOB-DIRECT-FUTURE-SPATIAL-ONE-USE-BOUND"
EXPECTED_PRIMARY_ASSERTIONS = 40
EXPECTED_INDEPENDENT_ASSERTIONS = 34
# Frozen after the first complete verifier run.
EXPECTED_INTEGRATOR_ASSERTIONS = 189
PRIMARY = REPO / "codes/foundations/a13_classii_signed_future_endpoint_graph_complement_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_signed_future_endpoint_graph_complement_boundary_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-signed-future-endpoint-graph-complement-boundary/result.json"
)
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-signed-future-endpoint-graph-complement-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-signed-future-endpoint-graph-complement-boundary/result.json"
)
R123_RESULT = CLAIM_DIR / "runs/2026-07-30-primary-six-row-trace-excess-direct-action-boundary/result.json"

AUTHORITIES = {
    "R-063": ("classii_balanced_coefficient_jet_continuum_manifest.json", "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION"),
    "R-079": ("classii_full_safe_packet_frame_current_doob_manifest.json", "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"),
    "R-087": ("classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json", "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION"),
    "R-093": ("classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json", "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY"),
    "R-102": ("classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json", "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"),
    "R-104": ("classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json", "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"),
    "R-123": ("classii_six_row_trace_excess_direct_action_boundary_manifest.json", "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"),
    "R-125": ("classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json", "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY"),
    "R-128": ("classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json", "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY"),
    "R-129": ("classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json", "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY"),
    "R-131": ("classii_owner_complete_physical_response_mixed_gram_shell_boundary_manifest.json", "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-SHELL-BOUNDARY"),
    "R-133": ("classii_affine_gaussian_score_feedback_collar_boundary_manifest.json", "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY"),
    "R-135": ("classii_variance_retained_sequential_atom_refinement_boundary_manifest.json", "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"),
    "R-136": ("classii_common_heat_replica_raw_sequential_owner_boundary_manifest.json", "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY"),
    "R-137": ("classii_raw_doob_triangle_spatial_carleson_boundary_manifest.json", "A13-CLASSII-RAW-DOOB-TRIANGLE-SPATIAL-CARLESON-BOUNDARY"),
    "R-138": ("classii_scale_graded_direct_future_reanchoring_boundary_manifest.json", "A13-CLASSII-SCALE-GRADED-DIRECT-FUTURE-REANCHORING-BOUNDARY"),
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        passed = bool(condition)
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        })
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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
    result = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
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


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_actions = {"/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData", "/Rendition", "/Movie", "/Sound", "/URI"}
    unsafe_keys = {"/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF", "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA", "/SubmitForm", "/ImportData"}

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, path: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action_type = resolve(value.get("/S"))
            if str(action_type) in unsafe_actions:
                findings.append(f"{path}/S={action_type}")
            for key, child in value.items():
                key_text = str(key)
                if key_text in unsafe_keys:
                    findings.append(f"{path}{key_text}")
                visit(child, f"{path}{key_text}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    root = resolve(reader.trailer["/Root"])
    visit(root, "/Root")
    open_action = resolve(root.get("/OpenAction"))
    if open_action is None:
        open_action_kind, safe_open_action = "absent", True
    elif isinstance(open_action, ArrayObject):
        open_action_kind, safe_open_action = "destination-array", True
    elif isinstance(open_action, DictionaryObject):
        open_action_kind = str(resolve(open_action.get("/S")))
        safe_open_action = open_action_kind == "/GoTo"
    else:
        open_action_kind, safe_open_action = type(open_action).__name__, False

    widgets = 0
    annotations: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        for annotation_index, annotation in enumerate(resolve(page.get("/Annots")) or []):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widgets += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                annotations.append(f"page-{page_index}/annot-{annotation_index}:{subtype}")
    return {
        "findings": sorted(set(findings + annotations)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widgets,
    }


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [runtime / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"]
    candidates.extend(runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def build_pdf() -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785456000"
    environment["FORCE_SOURCE_DATE"] = "1"
    return subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def render_pdf(output_dir: Path) -> tuple[int, str, list[Path]]:
    renderer = find_pdftoppm()
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    run = subprocess.run(
        [str(renderer), "-png", "-r", "130", str(PDF), str(output_dir / "page")],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), sorted(output_dir.glob("page-*.png"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-output", type=Path, default=DEFAULT_PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=DEFAULT_INDEPENDENT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_code, primary_stdout, primary_stderr = run_child(PRIMARY, args.primary_output)
    independent_code, independent_stdout, independent_stderr = run_child(INDEPENDENT, args.independent_output)
    for name, code, stdout, stderr, banner in (
        ("primary", primary_code, primary_stdout, primary_stderr, "R-139 primary PASS"),
        ("independent", independent_code, independent_stdout, independent_stderr, "R-139 independent PASS"),
    ):
        audit.check("children", f"{name} exit code", code == 0, code, 0)
        audit.check("children", f"{name} stderr empty", stderr == "", stderr, "")
        audit.check("children", f"{name} PASS banner", banner in stdout, stdout.strip(), banner)

    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    for name, child, suffix, count in (
        ("primary", primary, "-primary/1.0", EXPECTED_PRIMARY_ASSERTIONS),
        ("independent", independent, "-independent/1.0", EXPECTED_INDEPENDENT_ASSERTIONS),
    ):
        audit.check("children", f"{name} schema", child.get("schema", "").endswith(suffix), child.get("schema"), f"*{suffix}")
        audit.check("children", f"{name} result id", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} failures zero", child["assertions"]["failed"] == 0, child["assertions"]["failed"], 0)
        audit.check("children", f"{name} exact assertion count", child["assertions"]["total"] == count, child["assertions"]["total"], count)

    required_primary = {
        "future::complete insertion telescope",
        "trace_excess::future sign",
        "ownership::mean restores complete packet",
        "wedge::masked wedge does not telescope to terminal",
        "headroom::balanced determinant is zero",
        "robust::positive-gap scalar corollary accepted",
        "graph::graph robust condition is the narrow target",
        "riesz::projected adjoints agree",
    }
    required_independent = {
        "endpoint::independent owner telescope",
        "trace::independent sign and half factor",
        "owner::centered endpoint needs mean",
        "mask::positive increment mask accumulates",
        "gap::different balanced zero-gap fixture",
        "robust::finite robust equivalence",
        "graph::strict graph margin requires extra input",
        "riesz::non-Parseval candidate is rejected",
    }
    audit.check("contracts", "primary required assertions", required_primary <= assertion_names(primary), sorted(required_primary - assertion_names(primary)), [])
    audit.check("contracts", "independent required assertions", required_independent <= assertion_names(independent), sorted(required_independent - assertion_names(independent)), [])

    exact_shared = {
        "reveal_weight_exponent_fixture": "7/2",
        "tail_only_balanced_determinant": "0",
    }
    for key, expected in exact_shared.items():
        audit.check("cross", f"primary {key}", primary["computed"][key] == expected, primary["computed"][key], expected)
        audit.check("cross", f"independent {key}", independent["computed"][key] == expected, independent["computed"][key], expected)
        audit.check("cross", f"agreement {key}", primary["computed"][key] == independent["computed"][key], primary["computed"][key], independent["computed"][key])

    for name, child in (("primary", primary), ("independent", independent)):
        owner_sum = Fraction(child["computed"]["future_owner_sum"])
        endpoint = Fraction(child["computed"]["future_endpoint_difference"])
        trace_form = Fraction(child["computed"]["future_equals_minus_half_trace_excess_delta"])
        audit.check("cross", f"{name} endpoint owner trace equality", owner_sum == endpoint == trace_form, (owner_sum, endpoint, trace_form), "equal")
        audit.check("cross", f"{name} complete mask terminal equality", Fraction(child["computed"]["complete_mask_sum"]) == 0, child["computed"]["complete_mask_sum"], 0)
        far_square = Fraction(child["computed"]["far_square"])
        near_owner = Fraction(child["computed"]["near_cross_owner"])
        audit.check("cross", f"{name} far near cancellation", far_square + near_owner == 0, far_square + near_owner, 0)
        reveal_weight = float(child["computed"]["reveal_weight_fixture"])
        audit.check("cross", f"{name} actual reveal weight", abs(reveal_weight - math.sqrt(128.0)) <= 1.0e-14, reveal_weight, math.sqrt(128.0))

    floating_shared = (
        "reveal_weight_fixture",
        "r123_mean_square",
        "r123_d0",
        "r123_complete_packet",
        "r123_centered_k",
    )
    for key in floating_shared:
        left = float(primary["computed"][key])
        right = float(independent["computed"][key])
        tolerance = 1.0e-14 * max(1.0, abs(left), abs(right))
        audit.check("cross", f"finite primary {key}", abs(left) < float("inf"), left, "finite")
        audit.check("cross", f"finite independent {key}", abs(right) < float("inf"), right, "finite")
        audit.check("cross", f"agreement {key}", abs(left - right) <= tolerance, left - right, f"<={tolerance}")

    r123 = load_json(R123_RESULT)
    r123_rows = {f"{row['group']}::{row['name']}": row for row in r123["assertions"]}
    production_p = Fraction(r123_rows["six_row::mass_parameter"]["actual"])
    c_sum = Fraction(r123_rows["six_row::c_sum"]["actual"])
    audit.check("upstream", "R-123 c_sum derives from production P", c_sum == Fraction(339, 8000) / production_p, c_sum, Fraction(339, 8000) / production_p)
    upstream_s = float(c_sum)
    upstream_fixture = {
        "r123_mean_square": 16.0 * upstream_s * math.exp(-4.0),
        "r123_d0": 16.0 * upstream_s * (math.exp(-4.0) - 2.0 * math.exp(-8.0)),
        "r123_complete_packet": 16.0 * upstream_s * math.exp(-8.0),
    }
    upstream_fixture["r123_centered_k"] = -upstream_fixture["r123_d0"] / 2.0
    for key, expected in upstream_fixture.items():
        actual = float(primary["computed"][key])
        audit.check("upstream", f"R-123 fixture {key}", abs(actual - expected) <= 1.0e-15, actual - expected, "<=1e-15")

    shared_scope = {
        "signed_future_terminal_prefix_telescope": True,
        "insertion_reanchoring_removed_after_complete_signed_sum": True,
        "mean_low_forest_ownership_repaired": True,
        "wedge_only_telescope_rejected": True,
        "tail_only_headroom_rejected": True,
        "robust_graph_complement_criterion": True,
        "production_weighted_trace_excess": False,
        "production_graph_margin": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    for key, expected in shared_scope.items():
        audit.check("scope", f"primary {key}", primary["scope"][key] is expected, primary["scope"][key], expected)
        audit.check("scope", f"independent {key}", independent["scope"][key] is expected, independent["scope"][key], expected)
        audit.check("scope", f"agreement {key}", primary["scope"][key] is independent["scope"][key], primary["scope"][key], independent["scope"][key])

    imports = imported_roots(INDEPENDENT)
    allowed = {"__future__", "argparse", "fractions", "json", "math", "os", "pathlib", "tempfile"}
    audit.check("independence", "independent uses standard library only", imports <= allowed, sorted(imports), sorted(allowed))
    audit.check("independence", "independent does not import primary", "a13_classii_signed_future_endpoint_graph_complement_boundary.py" not in INDEPENDENT.read_text(encoding="utf-8"), "primary import absent", "absent")
    audit.check("independence", "source hashes differ", sha256(PRIMARY) != sha256(INDEPENDENT), (sha256(PRIMARY), sha256(INDEPENDENT)), "different")

    audit.check("document", "proof note exists", NOTE.is_file(), NOTE.relative_to(REPO) if NOTE.exists() else NOTE, "file")
    note_text = NOTE.read_text(encoding="utf-8")
    compact_note = "".join(note_text.split())
    footer_labels = (
        "Result ID:", "Ledger ID:", "Precise statement:", "Scope:", "Dependencies:",
        "Evidence grade:", "Reproduction command:", "Expected output:", "Falsification gate:",
        "Tier before / after:", "No-overclaim statement:", "Next required action:",
    )
    audit.check("document", "all footer labels present", all(label in note_text for label in footer_labels), [label for label in footer_labels if label not in note_text], [])
    audit.check("document", "result id pinned", RESULT_ID in compact_note, RESULT_ID in compact_note, True)
    audit.check("document", "ledger id pinned", "Ledger ID: R-139" in note_text and "% Ledger: R-139" in note_text, ("Ledger ID: R-139" in note_text, "% Ledger: R-139" in note_text), (True, True))
    audit.check("document", "endpoint theorem pinned", "Theorem 3.1 (endpoint-first future telescope)" in note_text, "Theorem 3.1" in note_text, True)
    audit.check("document", "legal future trace pinned", "legal future average" in note_text and "mathcal F_r" in note_text, "conditioning tokens", "present")
    audit.check("document", "mean owner correction pinned", "mean must be returned from its low/injected owner" in note_text, "mean/low owner", "present")
    audit.check("document", "wedge no-go pinned", "Wedge-only endpoint telescope" in note_text, "wedge no-go", "present")
    audit.check("document", "robust theorem pinned", "Theorem 8.1 (robust complement criterion)" in note_text, "Theorem 8.1" in note_text, True)
    audit.check("document", "positive-gap scalar correction pinned", "sigma_\\mu" in note_text and "d-\\mu" in note_text, "positive-gap denominator", "present")
    audit.check("document", "graph theorem pinned", "Theorem 10.1 (graph-robust complement)" in note_text, "Theorem 10.1" in note_text, True)
    audit.check("document", "successor pinned", SUCCESSOR.split("-SPATIAL")[0] in note_text and "SPATIAL-ONE-USE-BOUND" in note_text, SUCCESSOR, "line-wrapped present")
    audit.check("document", "sector remains open", "Sector-A closure" in note_text and "no promotion" in note_text, "no-overclaim clauses", "present")

    first_build = build_pdf()
    audit.check("pdf", "first deterministic build exits zero", first_build.returncode == 0, (first_build.returncode, first_build.stderr), 0)
    audit.check("pdf", "first form check", "FORM-CHECK: PASS" in first_build.stdout, first_build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "first zero overfull boxes", "OVERFULL-HBOX: 0" in first_build.stdout, first_build.stdout, "OVERFULL-HBOX: 0")
    first_hash = sha256(PDF) if PDF.is_file() else "missing"
    second_build = build_pdf()
    audit.check("pdf", "second deterministic build exits zero", second_build.returncode == 0, (second_build.returncode, second_build.stderr), 0)
    audit.check("pdf", "second form check", "FORM-CHECK: PASS" in second_build.stdout, second_build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "second zero overfull boxes", "OVERFULL-HBOX: 0" in second_build.stdout, second_build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "PDF exists", PDF.is_file(), PDF.relative_to(REPO) if PDF.exists() else PDF, "file")
    second_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild hash", first_hash == second_hash, (first_hash, second_hash), "equal")

    reader = PdfReader(str(PDF))
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    page_count = len(reader.pages)
    audit.check("pdf", "positive page count", page_count > 0, page_count, ">0")
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    audit.check("pdf", "all pages text nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], ">=20 each")
    extracted = "\n".join(extracted_pages)
    compact_extracted = "".join(extracted.split())
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "result id extracts", RESULT_ID in compact_extracted, RESULT_ID in compact_extracted, True)
    audit.check("pdf", "ledger id extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    fields = reader.get_fields()
    audit.check("pdf", "no form fields", fields in (None, {}), fields, None)
    security = pdf_security_audit(reader)
    audit.check("pdf", "no unsafe actions or embedded files", security["findings"] == [], security["findings"], [])
    audit.check("pdf", "safe open action", security["safe_open_action"] is True, security["open_action"], "absent, destination-array, or GoTo")
    audit.check("pdf", "no widgets", security["widget_count"] == 0, security["widget_count"], 0)
    with tempfile.TemporaryDirectory(prefix="tect-r139-render-") as temporary_render:
        render_code, render_log, rendered_pages = render_pdf(Path(temporary_render))
        audit.check("pdf", "Poppler render exits zero", render_code == 0, (render_code, render_log), 0)
        audit.check("pdf", "rendered page count", len(rendered_pages) == page_count, len(rendered_pages), page_count)
        audit.check("pdf", "rendered images nonempty", all(path.stat().st_size > 0 for path in rendered_pages), [path.stat().st_size for path in rendered_pages], "positive each")
        rendered_hashes = [sha256(path) for path in rendered_pages]

    pdf_audit = {
        "path": str(PDF.relative_to(REPO)),
        "sha256": second_hash,
        "size_bytes": PDF.stat().st_size,
        "pages": page_count,
        "deterministic_rebuild": True,
        "form_check": True,
        "overfull_hbox_count": 0,
        "all_pages_nonblank": True,
        "replacement_glyph": False,
        "encrypted": False,
        "form_fields": 0,
        "security_findings": security["findings"],
        "open_action": security["open_action"],
        "widget_count": security["widget_count"],
        "renderer": "Poppler pdftoppm",
        "dpi": 130,
        "rendered_pages": page_count,
        "page_sha256": rendered_hashes,
    }

    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        anchor = f'<a id="{negative_id.lower()}"></a>'
        audit.check("negative", f"{negative_id} registered", negative_id in negative_text and anchor in negative_text, (negative_id in negative_text, anchor in negative_text), (True, True))

    exploration_text = (REPO / "explorations/log.jsonl").read_text(encoding="utf-8")
    for exploration_id in EXPLORATION_IDS:
        audit.check("exploration", f"{exploration_id} registered", f'"id":"{exploration_id}"' in exploration_text, exploration_id in exploration_text, True)
    audit.check("exploration", "successful routes recorded", "terminal-minus-prefix" in exploration_text and "robust shifted-Douglas" in exploration_text, "success route terms", "present")
    audit.check("exploration", "failure routes recorded", "moving future wedge mask" in exploration_text and "Tail decay alone" in exploration_text, "failure route terms", "present")

    public_checks = {
        "result ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-139"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-139"),
        "lineage narrative": (CLAIM_DIR / "lineage-narrative.md", "R-139"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-139"),
        "changelog": (REPO / "CHANGELOG.md", "A13 R-139 signed future endpoint and graph-complement checkpoint"),
    }
    for name, (path, token) in public_checks.items():
        surface_text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in surface_text, token in surface_text, True)

    authority_hashes: dict[str, str] = {}
    for ledger_id, (filename, expected_result_id) in AUTHORITIES.items():
        path = CLAIM_DIR / filename
        audit.check("authority", f"{ledger_id} manifest exists", path.is_file(), path.relative_to(REPO) if path.exists() else path, "file")
        authority = load_json(path)
        audit.check("authority", f"{ledger_id} result id", authority.get("result_id") == expected_result_id, authority.get("result_id"), expected_result_id)
        audit.check("authority", f"{ledger_id} claim id", authority.get("claim_id") == CLAIM, authority.get("claim_id"), CLAIM)
        authority_hashes[ledger_id] = sha256(path)

    expected_count = len(audit.rows) + 1
    audit.check(
        "contracts",
        "integrator assertion count",
        EXPECTED_INTEGRATOR_ASSERTIONS == 0 or expected_count == EXPECTED_INTEGRATOR_ASSERTIONS,
        expected_count,
        EXPECTED_INTEGRATOR_ASSERTIONS if EXPECTED_INTEGRATOR_ASSERTIONS else "freeze after first complete run",
    )

    child_rows: list[dict[str, object]] = []
    for child_name, child in (("primary", primary), ("independent", independent)):
        for row in child["assertions"]["rows"]:
            child_rows.append({
                "group": f"{child_name}:{row['group']}",
                "name": row["name"],
                "status": row["status"],
                "actual": row["actual"],
                "expected": row["expected"],
            })

    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {"total": len(all_rows), "passed": len(all_rows) - failed, "failed": failed, "rows": all_rows},
        "children": {
            "primary": {"path": str(args.primary_output.relative_to(REPO)), "sha256": sha256(args.primary_output), "assertions": primary["assertions"]["total"], "stdout": primary_stdout},
            "independent": {"path": str(args.independent_output.relative_to(REPO)), "sha256": sha256(args.independent_output), "assertions": independent["assertions"]["total"], "stdout": independent_stdout},
        },
        "authority_hashes": authority_hashes,
        "source_hashes": {"primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT), "verifier": sha256(Path(__file__))},
        "pdf_audit": pdf_audit,
        "computed": {key: primary["computed"][key] for key in primary["computed"]},
        "assertion_accounting": {
            "unique_package_assertions": len(all_rows),
            "embedded_child_assertions": len(child_rows),
            "integrator_only_assertions": len(audit.rows),
        },
        "scope": {
            "children_pass": True,
            "signed_future_terminal_prefix_telescope": True,
            "insertion_reanchoring_removed_after_complete_signed_sum": True,
            "mean_low_forest_ownership_repaired": True,
            "wedge_only_telescope_rejected": True,
            "tail_only_headroom_rejected": True,
            "robust_graph_complement_criterion": True,
            "production_weighted_trace_excess": False,
            "production_graph_margin": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-139 integrated {payload['status']}: {len(all_rows)-failed}/{len(all_rows)}")
    print(f"primary={primary['assertions']['total']}; independent={independent['assertions']['total']}; integrator={len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
