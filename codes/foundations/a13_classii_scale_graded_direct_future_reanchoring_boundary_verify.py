#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-138 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from decimal import Decimal
import hashlib
import json
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
RESULT_ID = "A13-CLASSII-SCALE-GRADED-DIRECT-FUTURE-REANCHORING-BOUNDARY"
SCHEMA = "tect/a13-scale-graded-direct-future-reanchoring-boundary-integrated/1.0"
LEDGER_ID = "R-138"
CLAIM_DIR = REPO / "claims" / CLAIM
NOTE = CLAIM_DIR / "notes/classii-scale-graded-direct-future-reanchoring-boundary-260731-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
NEGATIVE_IDS = (
    "NG-2026-07-31-A13-CHRONOLOGY-ONLY-SPATIAL-GRADE",
    "NG-2026-07-31-A13-BARE-LAST-INSERTION-R135-REANCHORING",
)
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(546, 552))
SUCCESSOR = "A13-CLASSII-COMPLETE-RAW-DOOB-DIRECT-FUTURE-SPATIAL-ONE-USE-BOUND"
EXPECTED_PRIMARY_ASSERTIONS = 65
EXPECTED_INDEPENDENT_ASSERTIONS = 48
# A tooling oracle, filled from the verifier's own explicit checks and then frozen.
EXPECTED_INTEGRATOR_ASSERTIONS = 179
PRIMARY = REPO / "codes/foundations/a13_classii_scale_graded_direct_future_reanchoring_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_scale_graded_direct_future_reanchoring_boundary_independent.py"
DEFAULT_PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-scale-graded-direct-future-reanchoring-boundary/result.json"
)
DEFAULT_INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-scale-graded-direct-future-reanchoring-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-scale-graded-direct-future-reanchoring-boundary/result.json"
)

AUTHORITIES = {
    "R-063": ("classii_balanced_coefficient_jet_continuum_manifest.json", "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION"),
    "R-079": ("classii_full_safe_packet_frame_current_doob_manifest.json", "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION"),
    "R-084": ("classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json", "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION"),
    "R-087": ("classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json", "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION"),
    "R-088": ("classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json", "A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION"),
    "R-102": ("classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json", "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY"),
    "R-104": ("classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json", "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"),
    "R-123": ("classii_six_row_trace_excess_direct_action_boundary_manifest.json", "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"),
    "R-125": ("classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json", "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY"),
    "R-129": ("classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json", "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY"),
    "R-134": ("classii_terminal_smoothing_fixed_law_action_aggregate_collar_boundary_manifest.json", "A13-CLASSII-TERMINAL-SMOOTHING-FIXED-LAW-ACTION-AGGREGATE-COLLAR-BOUNDARY"),
    "R-135": ("classii_variance_retained_sequential_atom_refinement_boundary_manifest.json", "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"),
    "R-136": ("classii_common_heat_replica_raw_sequential_owner_boundary_manifest.json", "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY"),
    "R-137": ("classii_raw_doob_triangle_spatial_carleson_boundary_manifest.json", "A13-CLASSII-RAW-DOOB-TRIANGLE-SPATIAL-CARLESON-BOUNDARY"),
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
        ("primary", primary_code, primary_stdout, primary_stderr, "R-138 primary PASS"),
        ("independent", independent_code, independent_stdout, independent_stderr, "R-138 independent PASS"),
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
        "direct::raw six-row factor",
        "grading_nogo::contradiction ratio power",
        "signed_owner::opposite second owner",
        "future_telescope::finite Fubini equality",
        "reanchoring::causal factor at gap six",
        "carleson::minimal direct total",
        "collar::direct collar constant value",
        "scope::sector_a_closed",
    }
    required_independent = {
        "frame::outer OU factor retained",
        "obstruction::ratio power",
        "ownership::opposite owners",
        "telescope::event coordinate is signed",
        "weights::reveal-far insertion-near wedge",
        "charges::minimal scalar cost",
        "collar::constant",
        "scope::sector_a_closed",
    }
    audit.check("contracts", "primary required assertions", required_primary <= assertion_names(primary), sorted(required_primary - assertion_names(primary)), [])
    audit.check("contracts", "independent required assertions", required_independent <= assertion_names(independent), sorted(required_independent - assertion_names(independent)), [])

    exact_shared = {
        "raw_six_row_factor": "75000000000/4000000000001",
        "beta": "7/5",
        "grading_ratio_power": "38/15",
        "margins": ["1/15", "4/15", "16/15"],
        "opposite_signed_owners": ["1/2", "-1/2"],
        "coherent_signed_owners": ["1/2", "3/2"],
        "future_reveal_total": "1",
        "future_insertion_total": "1",
        "reanchoring_causal_exponent_gap_6": "7",
        "minimal_direct_charge_total": "534/385",
    }
    for key, expected in exact_shared.items():
        audit.check("cross", f"primary {key}", primary["computed"][key] == expected, primary["computed"][key], expected)
        audit.check("cross", f"independent {key}", independent["computed"][key] == expected, independent["computed"][key], expected)
        audit.check("cross", f"agreement {key}", primary["computed"][key] == independent["computed"][key], primary["computed"][key], independent["computed"][key])
    decimal_shared = {
        "reanchoring_causal_factor_gap_6": Decimal("128"),
        "direct_collar_constant": Decimal("0.28592888585547915"),
    }
    for key, expected in decimal_shared.items():
        left = Decimal(str(primary["computed"][key]))
        right = Decimal(str(independent["computed"][key]))
        audit.check("cross", f"primary {key}", abs(left - expected) <= Decimal("1e-15"), left - expected, "<=1e-15")
        audit.check("cross", f"independent {key}", abs(right - expected) <= Decimal("1e-15"), right - expected, "<=1e-15")
        audit.check("cross", f"agreement {key}", abs(left - right) <= Decimal("1e-15"), left - right, "<=1e-15")

    shared_scope = {
        "scale_graded_raw_direct_transfer": True,
        "signed_future_last_insertion_telescope": True,
        "chronology_only_spatial_grade_rejected": True,
        "bare_r135_future_reanchoring_rejected": True,
        "production_scale_grade_intertwiner": False,
        "production_q_sum": False,
        "positive_headroom": False,
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
    audit.check("independence", "independent does not import primary", "a13_classii_scale_graded_direct_future_reanchoring_boundary" not in INDEPENDENT.read_text(encoding="utf-8"), "primary import absent", "absent")
    audit.check("independence", "source hashes differ", sha256(PRIMARY) != sha256(INDEPENDENT), (sha256(PRIMARY), sha256(INDEPENDENT)), "different")

    audit.check("document", "proof note exists", NOTE.is_file(), NOTE.relative_to(REPO) if NOTE.exists() else NOTE, "file")
    note_text = NOTE.read_text(encoding="utf-8")
    footer_labels = (
        "Result ID:", "Ledger ID:", "Precise statement:", "Scope:", "Dependencies:",
        "Evidence grade:", "Reproduction command:", "Expected output:", "Falsification gate:",
        "Tier before / after:", "No-overclaim statement:", "Next required action:",
    )
    audit.check("document", "all footer labels present", all(label in note_text for label in footer_labels), [label for label in footer_labels if label not in note_text], [])
    audit.check("document", "result id pinned", RESULT_ID.replace("-BOUNDARY", "-") in note_text, RESULT_ID, "line-wrapped result id")
    audit.check("document", "ledger id pinned", "Ledger ID: R-138" in note_text, "R-138" in note_text, True)
    audit.check("document", "direct theorem pinned", "scale-graded raw direct Cartan estimate" in note_text, "Theorem 3.1", "present")
    audit.check("document", "chronology no-go pinned", "Chronology does not imply spatial grade" in note_text, "chronology no-go", "present")
    audit.check("document", "signed future transpose pinned", "complete signed last-insertion transpose" in note_text, "Theorem 6.1", "present")
    audit.check("document", "reanchoring wedge pinned", "FAR relative to the reveal but" in note_text and "not relative to the last insertion" in note_text, "future wedge", "present")
    audit.check("document", "sharp charge criterion pinned", "Sharp scalar charge criteria" in note_text, "charge criterion", "present")
    audit.check("document", "conditional collar pinned", "Conditional finite-collar consequence" in note_text, "collar criterion", "present")
    audit.check("document", "successor pinned", SUCCESSOR.split("-SPATIAL")[0] in note_text and "SPATIAL-ONE-USE-BOUND" in note_text, SUCCESSOR, "line-wrapped present")
    audit.check("document", "sector remains open", "Sector A closed: false" in note_text and "no Sector-A closure" in note_text, "no-overclaim clauses", "present")

    first_build = build_pdf()
    audit.check("pdf", "first deterministic build exits zero", first_build.returncode == 0, first_build.returncode, 0)
    audit.check("pdf", "first form check", "FORM-CHECK: PASS" in first_build.stdout, first_build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "first zero overfull boxes", "OVERFULL-HBOX: 0" in first_build.stdout, first_build.stdout, "OVERFULL-HBOX: 0")
    first_hash = sha256(PDF) if PDF.is_file() else "missing"
    second_build = build_pdf()
    audit.check("pdf", "second deterministic build exits zero", second_build.returncode == 0, second_build.returncode, 0)
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
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "result id extracts", "A13-CLASSII-SCALE-GRADED-DIRECT-FUTURE-REANCHORING" in extracted.replace("\n", ""), RESULT_ID, "present")
    audit.check("pdf", "ledger id extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    fields = reader.get_fields()
    audit.check("pdf", "no form fields", fields in (None, {}), fields, None)
    security = pdf_security_audit(reader)
    audit.check("pdf", "no unsafe actions or embedded files", security["findings"] == [], security["findings"], [])
    audit.check("pdf", "safe open action", security["safe_open_action"] is True, security["open_action"], "absent, destination-array, or GoTo")
    audit.check("pdf", "no widgets", security["widget_count"] == 0, security["widget_count"], 0)
    with tempfile.TemporaryDirectory(prefix="tect-r138-render-") as temporary_render:
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
    audit.check("exploration", "successful routes recorded", "scale-graded raw direct" in exploration_text and "signed last-insertion" in exploration_text, "success route terms", "present")
    audit.check("exploration", "failure routes recorded", "chronology-only" in exploration_text and "reanchoring" in exploration_text, "failure route terms", "present")

    public_checks = {
        "result ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-138"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-138"),
        "lineage narrative": (CLAIM_DIR / "lineage-narrative.md", "R-138"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-138"),
    }
    for name, (path, token) in public_checks.items():
        text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in text, token in text, True)

    authority_hashes: dict[str, str] = {}
    for ledger_id, (filename, expected_result_id) in AUTHORITIES.items():
        path = CLAIM_DIR / filename
        audit.check("authority", f"{ledger_id} manifest exists", path.is_file(), path.relative_to(REPO) if path.exists() else path, "file")
        authority = load_json(path)
        audit.check("authority", f"{ledger_id} result id", authority.get("result_id") == expected_result_id, authority.get("result_id"), expected_result_id)
        audit.check("authority", f"{ledger_id} claim id", authority.get("claim_id") == CLAIM, authority.get("claim_id"), CLAIM)
        authority_hashes[ledger_id] = sha256(path)

    audit.check(
        "contracts",
        "integrator assertion count",
        len(audit.rows) + 1 == EXPECTED_INTEGRATOR_ASSERTIONS,
        len(audit.rows) + 1,
        EXPECTED_INTEGRATOR_ASSERTIONS,
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
        "source_hashes": {"primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "pdf_audit": pdf_audit,
        "computed": {key: primary["computed"][key] for key in primary["computed"]},
        "assertion_accounting": {
            "unique_package_assertions": len(all_rows),
            "embedded_child_assertions": len(child_rows),
            "integrator_only_assertions": len(audit.rows),
        },
        "scope": {
            "children_pass": True,
            "scale_graded_raw_direct_transfer": True,
            "signed_future_last_insertion_telescope": True,
            "chronology_only_spatial_grade_rejected": True,
            "bare_r135_future_reanchoring_rejected": True,
            "production_scale_grade_intertwiner": False,
            "production_one_use_q_ledger": False,
            "positive_headroom": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-138 integrated {payload['status']}: {len(all_rows)-failed}/{len(all_rows)}")
    print(f"primary={primary['assertions']['total']}; independent={independent['assertions']['total']}; integrator={len(audit.rows)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
