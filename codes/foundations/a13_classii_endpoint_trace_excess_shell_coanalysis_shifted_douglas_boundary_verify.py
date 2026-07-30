#!/usr/bin/env python3
"""Integrated authority, PDF, ledger, and public-surface audit for R-129."""

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
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-"
    "SHIFTED-DOUGLAS-BOUNDARY"
)
SCHEMA = (
    "tect/a13-endpoint-trace-excess-shell-coanalysis-"
    "shifted-douglas-boundary-integrated/1.0"
)
MANIFEST_SCHEMA = (
    "tect/a13-endpoint-trace-excess-shell-coanalysis-"
    "shifted-douglas-boundary-manifest/1.0"
)
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / (
    "codes/foundations/a13_classii_endpoint_trace_excess_shell_coanalysis_"
    "shifted_douglas_boundary.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_endpoint_trace_excess_shell_coanalysis_"
    "shifted_douglas_boundary_independent.py"
)
PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-30-primary-endpoint-trace-excess-shell-coanalysis-"
    "shifted-douglas-boundary/result.json"
)
INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-30-independent-endpoint-trace-excess-shell-coanalysis-"
    "shifted-douglas-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-30-integrated-endpoint-trace-excess-shell-coanalysis-"
    "shifted-douglas-boundary/result.json"
)
MANIFEST = CLAIM_DIR / (
    "classii_endpoint_trace_excess_shell_coanalysis_"
    "shifted_douglas_boundary_manifest.json"
)
EXPECTED_AUTHORITY_KEYS = {
    "governance",
    "a1",
    "r093",
    "r103",
    "r104",
    "r119",
    "r120",
    "r122",
    "r123",
    "r125",
    "r127",
    "r127_primary",
    "r128",
    "r128_primary",
}
EXPECTED_FILE_KEYS = {
    "primary",
    "independent",
    "verifier",
    "note",
    "pdf",
    "primary_result",
    "independent_result",
}
EXPECTED_AUTHORITY_RESULT_IDS = {
    "r093": "A13-CLASSII-AUGMENTED-PERSPECTIVE-GIBBS-GAP-INFORMATION-BOUNDARY",
    "r103": "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE",
    "r104": "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY",
    "r119": "A13-CLASSII-LEGAL-ADAPTED-CLUSTER-SCORE-TRACE-TERMINAL-HESSIAN-FRONTIER",
    "r120": "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-LOW-CHAOS-CARTAN-HESSIAN-BOUNDARY",
    "r122": "A13-CLASSII-DERIVATIVE-FREE-LOW-CHAOS-ADAPTED-FIFTH-MOMENT-CARTAN-BOUNDARY",
    "r123": "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY",
    "r125": "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY",
    "r127": "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY",
    "r128": "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY",
}
EXPECTED_NEGATIVES = {
    "AUDIT-2026-07-30-A13-COVARIANCE-NORMAL-DOMINANCE-ACTION-DIRECTION",
    "NG-2026-07-30-A13-SEPARATE-VARIANCE-TRACE-HESSIAN-NORM-NECESSITY",
    "NG-2026-07-30-A13-CONDITIONAL-POINCARE-PARAMETER-SEMICONVEXITY",
    "NG-2026-07-30-A13-ENTROPY-SECOND-SCORE-CONTROL",
    "NG-2026-07-30-A13-TOTAL-COVARIANCE-TEMPORAL-SHELL-INTERTWINING",
    "NG-2026-07-30-A13-SWAPPED-GEOMETRIC-REVERSE-BAND-ADJOINT",
}
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(451, 469)}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


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


def confined_path(relative: str) -> tuple[Path, bool]:
    path = (REPO / relative).resolve()
    try:
        path.relative_to(REPO.resolve())
        return path, True
    except ValueError:
        return path, False


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_actions = {
        "/JavaScript",
        "/Launch",
        "/GoToR",
        "/SubmitForm",
        "/ImportData",
        "/Rendition",
        "/Movie",
        "/Sound",
        "/URI",
    }
    unsafe_keys = {
        "/JS",
        "/JavaScript",
        "/AA",
        "/Launch",
        "/AF",
        "/EF",
        "/EmbeddedFiles",
        "/RichMedia",
        "/Movie",
        "/Sound",
        "/XFA",
        "/SubmitForm",
        "/ImportData",
    }

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, path: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            try:
                value = value.get_object()
            except Exception as exc:  # pragma: no cover - corrupt-PDF guard
                findings.append(f"{path}:unreadable:{type(exc).__name__}")
                return
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
        open_action_kind = "absent"
        safe_open_action = True
    elif isinstance(open_action, ArrayObject):
        open_action_kind = "destination-array"
        safe_open_action = True
    elif isinstance(open_action, DictionaryObject):
        open_action_kind = str(resolve(open_action.get("/S")))
        safe_open_action = open_action_kind == "/GoTo"
    else:
        open_action_kind = type(open_action).__name__
        safe_open_action = False

    widget_count = 0
    annotation_findings: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        annotations = resolve(page.get("/Annots")) or []
        for annotation_index, annotation in enumerate(annotations):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widget_count += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                annotation_findings.append(
                    f"page-{page_index}/annot-{annotation_index}:{subtype}"
                )
    return {
        "findings": sorted(set(findings + annotation_findings)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widget_count,
    }


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [
        runtime
        / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(
        runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe")
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def render_pdf(pdf: Path, output_dir: Path, prefix: str) -> tuple[int, str, list[str]]:
    renderer = find_pdftoppm()
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    output_prefix = output_dir / prefix
    run = subprocess.run(
        [str(renderer), "-png", "-r", "130", str(pdf), str(output_prefix)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    images = sorted(output_dir.glob(f"{prefix}-*.png"))
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), [
        digest(image) for image in images
    ]


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.identifiers: set[str] = set()

    def check(
        self, group: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        identifier = f"{group}::{name}"
        if identifier in self.identifiers:
            raise ValueError(f"duplicate assertion identifier: {identifier}")
        self.identifiers.add(identifier)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(
        self,
        primary: dict[str, Any],
        independent: dict[str, Any],
        contract_observed: dict[str, Any],
    ) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        aggregate_total = (
            int(primary["assertions_total"])
            + int(independent["assertions_total"])
            + len(self.rows)
        )
        aggregate_passed = (
            int(primary["assertions_passed"])
            + int(independent["assertions_passed"])
            + passed
        )
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
            "aggregate": {
                "assertions_total": aggregate_total,
                "assertions_passed": aggregate_passed,
                "assertions_failed": aggregate_total - aggregate_passed,
            },
            "contract_observed": contract_observed,
            "scope": {
                "endpoint_owner_direction_proved": True,
                "direct_signed_hessian_identity_proved": True,
                "analytic_shortcut_boundaries_registered": True,
                "physical_shell_coanalysis_legal_reverse_proved_conditionally": True,
                "shifted_douglas_gap_criterion_proved": True,
                "production_forward_constants_proved": False,
                "balanced_low_anchor_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-129 proves endpoint direction, direct signed-Hessian algebra, "
                "conditional physical-shell/source-coanalysis legal reverse, and "
                "shifted-Douglas acceptance criteria. It does not transfer "
                "covariance-normal dominance to the smaller R-123 action owner and "
                "proves no production forward, balanced, low, absolute-anchor, "
                "OVERLAP_src, Nelson, removal, interacting-measure, or Sector-A theorem."
            ),
        }


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check("children", "primary_exit", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent_exit", independent_run.returncode == 0, independent_run.returncode, 0)
    audit.check("children", "primary_output_exists", PRIMARY_OUTPUT.is_file(), PRIMARY_OUTPUT.is_file(), True)
    audit.check("children", "independent_output_exists", INDEPENDENT_OUTPUT.is_file(), INDEPENDENT_OUTPUT.is_file(), True)
    if not PRIMARY_OUTPUT.is_file() or not INDEPENDENT_OUTPUT.is_file():
        print(primary_run.stdout, primary_run.stderr)
        print(independent_run.stdout, independent_run.stderr)
        return 1
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    for label, payload, count in (
        ("primary", primary, 50),
        ("independent", independent, 38),
    ):
        audit.check("children", f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        audit.check("children", f"{label}_result_id", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID)
        audit.check("children", f"{label}_count", payload.get("assertions_total") == count, payload.get("assertions_total"), count)
        audit.check("children", f"{label}_no_failures", payload.get("assertions_failed") == 0, payload.get("assertions_failed"), 0)

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    independent_tree = ast.parse(independent_source)
    imported_modules = {
        alias.name
        for node in ast.walk(independent_tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    audit.check(
        "children",
        "non_importing_independent",
        not any("endpoint_trace_excess_shell_coanalysis" in item for item in imported_modules)
        and PRIMARY.name not in independent_source,
        {
            "imports": sorted(imported_modules),
            "primary_filename_present": PRIMARY.name in independent_source,
        },
        "primary import/read absent",
    )
    audit.check(
        "children",
        "independent_no_sympy",
        "import sympy" not in independent_source,
        "sympy import absent" if "import sympy" not in independent_source else "present",
        "sympy import absent",
    )

    audit.check("manifest", "exists", MANIFEST.is_file(), MANIFEST.is_file(), True)
    if not MANIFEST.is_file():
        print("R-129 integrated BLOCKED: manifest missing")
        return 1
    manifest = load_json(MANIFEST)
    audit.check("manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA)
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger_id", manifest.get("result_ledger_id") == "R-129", manifest.get("result_ledger_id"), "R-129")
    audit.check("manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")
    audit.check("manifest", "evidence_grade", manifest.get("evidence_grade") == ["ANALYTIC", "EXACT", "EXECUTED"], manifest.get("evidence_grade"), ["ANALYTIC", "EXACT", "EXECUTED"])
    audit.check("manifest", "proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    manifest_no_overclaim = manifest.get("no_overclaim", "").lower()
    audit.check("manifest", "no_overclaim_semantics", all(token in manifest_no_overclaim for token in ("does not", "production", "nelson", "sector-a")), manifest.get("no_overclaim"), "explicit production/Nelson/Sector-A boundary")
    manifest_scope = manifest.get("scope", {})
    for field in (
        "production_forward_constants_proved",
        "balanced_low_and_absolute_anchor_proved",
        "production_common_terminal_matching_trace_proved",
        "overlap_src_proved",
        "nelson_proved",
        "sector_a_closed",
        "tier_promoted",
    ):
        audit.check("manifest_scope", field, manifest_scope.get(field) is False, manifest_scope.get(field), False)
    audit.check("manifest", "negative_set", set(manifest.get("negative_results", [])) == EXPECTED_NEGATIVES, manifest.get("negative_results", []), sorted(EXPECTED_NEGATIVES))
    audit.check("manifest", "exploration_set", set(manifest.get("exploration_ids", [])) == EXPECTED_EXPLORATIONS, manifest.get("exploration_ids", []), sorted(EXPECTED_EXPLORATIONS))

    verification = manifest.get("verification", {})
    audit.check("manifest", "primary_contract", verification.get("primary_assertions") == 50, verification.get("primary_assertions"), 50)
    audit.check("manifest", "independent_contract", verification.get("independent_assertions") == 38, verification.get("independent_assertions"), 38)
    audit.check("manifest", "primary_schema", verification.get("primary_schema") == primary.get("schema"), primary.get("schema"), verification.get("primary_schema"))
    audit.check("manifest", "independent_schema", verification.get("independent_schema") == independent.get("schema"), independent.get("schema"), verification.get("independent_schema"))
    audit.check("manifest", "integrated_schema", verification.get("integrated_schema") == SCHEMA, verification.get("integrated_schema"), SCHEMA)

    authorities = manifest.get("authorities", {})
    files = manifest.get("files", {})
    audit.check("manifest", "authority_keys", set(authorities) == EXPECTED_AUTHORITY_KEYS, sorted(authorities), sorted(EXPECTED_AUTHORITY_KEYS))
    audit.check("manifest", "file_keys", set(files) == EXPECTED_FILE_KEYS, sorted(files), sorted(EXPECTED_FILE_KEYS))
    audit.check("manifest", "declared_authority_keys", manifest.get("authority_keys") == list(authorities), manifest.get("authority_keys"), list(authorities))
    audit.check("manifest", "declared_file_keys", manifest.get("file_keys") == ["primary", "independent", "verifier", "note", "pdf", "primary_result", "independent_result"], manifest.get("file_keys"), ["primary", "independent", "verifier", "note", "pdf", "primary_result", "independent_result"])
    authority_paths = [str(entry.get("path", "")) for entry in authorities.values()]
    audit.check("manifest", "unique_authority_paths", len(authority_paths) == len(set(authority_paths)), authority_paths, "all unique")

    for group, entries in (("authority", authorities), ("files", files)):
        for name, entry in entries.items():
            expected_hash = str(entry.get("sha256", ""))
            audit.check(group, f"{name}_hash_format", SHA256_PATTERN.fullmatch(expected_hash) is not None, expected_hash, "64 lowercase hex")
            path, confined = confined_path(str(entry.get("path", "")))
            audit.check(group, f"{name}_confined", confined, str(path), str(REPO.resolve()))
            audit.check(group, f"{name}_exists", confined and path.is_file(), path.is_file(), True)
            if confined and path.is_file():
                actual_hash = digest(path)
                audit.check(group, f"{name}_sha256", actual_hash == expected_hash, actual_hash, expected_hash)

    for name, expected_result_id in EXPECTED_AUTHORITY_RESULT_IDS.items():
        authority_path, confined = confined_path(authorities[name]["path"])
        payload = load_json(authority_path) if confined and authority_path.is_file() else {}
        audit.check(
            "authority_semantics",
            f"{name}_result_id",
            payload.get("result_id") == expected_result_id,
            payload.get("result_id"),
            expected_result_id,
        )
    for name, manifest_name in (
        ("r127_primary", "r127"),
        ("r128_primary", "r128"),
    ):
        result_path, result_confined = confined_path(authorities[name]["path"])
        manifest_path, manifest_confined = confined_path(authorities[manifest_name]["path"])
        result_payload = load_json(result_path) if result_confined and result_path.is_file() else {}
        manifest_payload = load_json(manifest_path) if manifest_confined and manifest_path.is_file() else {}
        audit.check(
            "authority_semantics",
            f"{name}_matches_manifest",
            result_payload.get("result_id") == manifest_payload.get("result_id"),
            result_payload.get("result_id"),
            manifest_payload.get("result_id"),
        )

    note_path, note_confined = confined_path(files["note"]["path"])
    pdf_path, pdf_confined = confined_path(files["pdf"]["path"])
    if not note_confined or not pdf_confined or not note_path.is_file() or not pdf_path.is_file():
        print("R-129 integrated BLOCKED: note/PDF path contract invalid")
        return 1
    note_check = subprocess.run(
        [sys.executable, str(REPO / "verification/scripts/build_note_pdf.py"), str(note_path), "--no-compile"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    audit.check("note", "form_check_exit", note_check.returncode == 0, note_check.returncode, 0)
    audit.check("note", "form_check_banner", "FORM-CHECK: PASS" in note_check.stdout, note_check.stdout.strip(), "FORM-CHECK: PASS")
    note = note_path.read_text(encoding="utf-8")
    note_norm = normalized(note)
    note_phrases = (
        "Exact endpoint direction and the failed action transfer",
        "Direct signed covariance-normal differentiation",
        "Conditional Poincare does not give parameter semiconvexity",
        "Total covariance does not intertwine temporal increments",
        "physical-shell analysis and legal source coanalysis",
        "forward estimate transfers to the aggregate reverse",
        "Exact shifted-Douglas uniform-gap theorem",
        "Strongest current production criterion",
        "Evidence-map roadmap",
        "Devil's-advocate review",
        "R-129 closes an A13 gate",
        "A13-CLASSII-OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-",
    )
    for index, phrase in enumerate(note_phrases, start=1):
        present = normalized(phrase) in note_norm
        audit.check("note", f"phrase_{index:02d}", present, present, True)
    audit.check("note", "source_note_hash", verification.get("source_note_sha256") == digest(note_path), verification.get("source_note_sha256"), digest(note_path))

    reader = PdfReader(str(pdf_path))
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    fields = reader.get_fields() or {}
    pdf_contract = verification.get("pdf", {})
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "pages", len(reader.pages) == pdf_contract.get("pages"), len(reader.pages), pdf_contract.get("pages"))
    audit.check("pdf", "all_pages_nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], "all >= 20")
    audit.check("pdf", "no_form", not fields, sorted(fields), [])
    audit.check("pdf", "result_id_extracted", RESULT_ID in extracted.replace("\n", "").replace(" ", ""), RESULT_ID in extracted.replace("\n", "").replace(" ", ""), True)
    audit.check("pdf", "r129_extracted", "R-129" in extracted, "R-129" in extracted, True)
    security = pdf_security_audit(reader)
    audit.check("pdf", "safe_open_action", security["safe_open_action"], security["open_action"], "absent, destination-array, or /GoTo")
    audit.check("pdf", "no_unsafe_features", not security["findings"], security["findings"], [])
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)
    audit.check("pdf", "size", pdf_path.stat().st_size == pdf_contract.get("size_bytes"), pdf_path.stat().st_size, pdf_contract.get("size_bytes"))
    audit.check("pdf", "hash", digest(pdf_path) == pdf_contract.get("sha256"), digest(pdf_path), pdf_contract.get("sha256"))
    visual = pdf_contract.get("visual_qa", {})
    audit.check("pdf", "visual_status", visual.get("status") == "PASS", visual.get("status"), "PASS")
    audit.check("pdf", "visual_all_pages", visual.get("rendered_pages") == 11 and visual.get("inspected_pages") == 11, {"rendered": visual.get("rendered_pages"), "inspected": visual.get("inspected_pages")}, {"rendered": 11, "inspected": 11})
    audit.check("pdf", "visual_no_defects", visual.get("defects") == [], visual.get("defects"), [])
    audit.check("pdf", "overfull_zero", pdf_contract.get("overfull_hbox_count") == 0, pdf_contract.get("overfull_hbox_count"), 0)
    for field in (
        "form_check",
        "javascript_check",
        "unsafe_action_check",
        "widget_check",
        "embedded_file_check",
        "encryption_check",
    ):
        audit.check(
            "pdf_contract",
            field,
            pdf_contract.get(field) == "PASS",
            pdf_contract.get(field),
            "PASS",
        )

    with tempfile.TemporaryDirectory(
        prefix="r129-pdf-freshness-", dir=REPO / "internal"
    ) as temporary:
        temporary_root = Path(temporary)
        temporary_note = temporary_root / note_path.name
        temporary_note.write_text(note, encoding="utf-8", newline="\n")
        rebuild = subprocess.run(
            [
                sys.executable,
                str(REPO / "verification/scripts/build_note_pdf.py"),
                str(temporary_note),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        rebuilt_pdf = temporary_note.with_name(
            temporary_note.name.removesuffix(".tex.txt") + ".pdf"
        )
        audit.check(
            "pdf_freshness",
            "rebuild_exit",
            rebuild.returncode == 0,
            rebuild.returncode,
            0,
        )
        overfull_zero = "OVERFULL-HBOX: 0" in (rebuild.stdout or "")
        audit.check(
            "pdf_freshness",
            "rebuild_overfull_zero",
            overfull_zero,
            "OVERFULL-HBOX: 0" if overfull_zero else "missing",
            "OVERFULL-HBOX: 0",
        )
        audit.check(
            "pdf_freshness",
            "rebuilt_pdf_exists",
            rebuilt_pdf.is_file(),
            rebuilt_pdf.is_file(),
            True,
        )
        if rebuilt_pdf.is_file():
            rebuilt_reader = PdfReader(str(rebuilt_pdf))
            rebuilt_pages = [(page.extract_text() or "") for page in rebuilt_reader.pages]
            audit.check(
                "pdf_freshness",
                "rebuilt_page_count",
                len(rebuilt_pages) == len(extracted_pages),
                len(rebuilt_pages),
                len(extracted_pages),
            )
            audit.check(
                "pdf_freshness",
                "source_to_pdf_text_identity",
                [normalized(text) for text in rebuilt_pages]
                == [normalized(text) for text in extracted_pages],
                [len(normalized(text)) for text in rebuilt_pages],
                [len(normalized(text)) for text in extracted_pages],
            )

            pinned_render = temporary_root / "pinned-render"
            rebuilt_render = temporary_root / "rebuilt-render"
            pinned_render.mkdir()
            rebuilt_render.mkdir()
            pinned_exit, pinned_log, pinned_hashes = render_pdf(
                pdf_path, pinned_render, "page"
            )
            rebuilt_exit, rebuilt_log, rebuilt_hashes = render_pdf(
                rebuilt_pdf, rebuilt_render, "page"
            )
            expected_page_hashes = visual.get("page_sha256", [])
            audit.check(
                "pdf_freshness",
                "pinned_render_exit",
                pinned_exit == 0,
                {"exit": pinned_exit, "log": pinned_log},
                0,
            )
            audit.check(
                "pdf_freshness",
                "rebuilt_render_exit",
                rebuilt_exit == 0,
                {"exit": rebuilt_exit, "log": rebuilt_log},
                0,
            )
            audit.check(
                "pdf_freshness",
                "pinned_render_count",
                len(pinned_hashes) == 11,
                len(pinned_hashes),
                11,
            )
            audit.check(
                "pdf_freshness",
                "manual_visual_hash_binding",
                pinned_hashes == expected_page_hashes,
                pinned_hashes,
                expected_page_hashes,
            )
            audit.check(
                "pdf_freshness",
                "rebuilt_render_identity",
                rebuilt_hashes == pinned_hashes,
                rebuilt_hashes,
                pinned_hashes,
            )

    explorations: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            explorations[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = explorations.get(identifier)
        audit.check("exploration", f"{identifier}_exists", row is not None, row is not None, True)
        if row is None:
            continue
        audit.check("exploration", f"{identifier}_claim", CLAIM in row.get("claim_ids", []), row.get("claim_ids", []), CLAIM)
        audit.check("exploration", f"{identifier}_task", row.get("task_id") == "T-050", row.get("task_id"), "T-050")
        audit.check("exploration", f"{identifier}_evidence", bool(row.get("evidence_refs")), row.get("evidence_refs"), "nonempty")
        audit.check("exploration", f"{identifier}_boundary", bool(row.get("boundary")), row.get("boundary"), "nonempty")
        audit.check("exploration", f"{identifier}_next", bool(row.get("next_action")), row.get("next_action"), "nonempty")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in sorted(EXPECTED_NEGATIVES):
        heading = f"### {identifier}"
        audit.check("negatives", identifier, heading in negative_text, heading in negative_text, True)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("surface", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    audit.check("surface", "status_statement", "R-129" in status.get("statement", ""), "R-129" in status.get("statement", ""), True)
    audit.check("surface", "status_next_action", "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND" in status.get("next_action", ""), status.get("next_action"), "new successor ID")
    audit.check("surface", "status_no_overclaim", "does not" in status.get("no_overclaim", "").lower() and "sector-a" in status.get("no_overclaim", "").lower(), status.get("no_overclaim"), "open-scope statement")

    surface_contracts = (
        ("claim", CLAIM_DIR / "claim.md", ("R-129", RESULT_ID, "EXP-000451--EXP-000468")),
        ("lineage_narrative", CLAIM_DIR / "lineage-narrative.md", ("R-129", "shell coanalysis", "shifted-Douglas")),
        ("results_ledger", REPO / "RESULTS-LEDGER.md", ("## R-129", RESULT_ID)),
        ("todo", REPO / "todo/todo.json", ("T-050", "R-129", "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND")),
        ("changelog_source", REPO / "changelog/log.jsonl", ("R-129", "classii-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary")),
        ("changelog_render", REPO / "CHANGELOG.md", ("R-129", "eleven-page PDF")),
        ("claims_render", REPO / "CLAIMS.md", (CLAIM, "Class-II source, translated model", "T4")),
        ("proof_map", REPO / "theory/proof-evidence-map.md", ("R-129", "classii-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary", "EXP-000465")),
        ("proof_map_json", REPO / "verification/proof-evidence-map.json", (RESULT_ID, "EXP-000465")),
        ("catalog", REPO / "CATALOG.md", ("classii-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary",)),
        ("catalog_json", REPO / "verification/catalog.json", ("classii-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary",)),
    )
    for label, path, phrases in surface_contracts:
        audit.check("surface", f"{label}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for index, phrase in enumerate(phrases, start=1):
                audit.check("surface", f"{label}_phrase_{index}", phrase in text, phrase in text, True)

    changelog_rows = [
        json.loads(line)
        for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    latest_event = changelog_rows[-1]
    audit.check("surface_semantics", "latest_event_header", "R-129 verifier hardening" in latest_event.get("header", ""), latest_event.get("header"), "R-129 verifier hardening")
    audit.check("surface_semantics", "latest_event_claim", latest_event.get("claim_ids") == [CLAIM], latest_event.get("claim_ids"), [CLAIM])
    audit.check("surface_semantics", "latest_event_manifest", MANIFEST.relative_to(REPO).as_posix() in latest_event.get("notes", []), latest_event.get("notes"), MANIFEST.relative_to(REPO).as_posix())
    audit.check("surface_semantics", "latest_event_verifier", PRIMARY.with_name(PRIMARY.stem + "_verify.py").relative_to(REPO).as_posix() in latest_event.get("scripts", []), latest_event.get("scripts"), PRIMARY.with_name(PRIMARY.stem + "_verify.py").relative_to(REPO).as_posix())
    audit.check("surface_semantics", "latest_event_explorations", {"EXP-000466", "EXP-000467"}.issubset(set(latest_event.get("keywords", []))), latest_event.get("keywords"), ["EXP-000466", "EXP-000467"])

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    active = theorem_map.get("active_frontier", {})
    audit.check("surface", "theorem_map_latest", active.get("latest_result_id") == RESULT_ID, active.get("latest_result_id"), RESULT_ID)
    audit.check("surface", "theorem_map_successor", "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND" in active.get("success_condition", ""), active.get("success_condition"), "new successor ID")

    precontract_count = len(audit.rows)
    precontract_identifier_hash = hashlib.sha256(
        "\n".join(sorted(audit.identifiers)).encode("utf-8")
    ).hexdigest()
    contract_observed = {
        "integrated_precontract_assertions": precontract_count,
        "integrated_precontract_identifier_sha256": precontract_identifier_hash,
        "integrated_assertions": precontract_count + 4,
        "aggregate_assertions": 50 + 38 + precontract_count + 4,
    }
    audit.check("contract", "precontract_assertion_count", precontract_count == int(verification.get("integrated_precontract_assertions", -1)), precontract_count, verification.get("integrated_precontract_assertions"))
    audit.check("contract", "precontract_identifier_hash", precontract_identifier_hash == verification.get("integrated_precontract_identifier_sha256"), precontract_identifier_hash, verification.get("integrated_precontract_identifier_sha256"))
    audit.check("contract", "integrated_assertion_count", len(audit.rows) + 2 == int(verification.get("integrated_assertions", -1)), len(audit.rows) + 2, verification.get("integrated_assertions"))
    audit.check("contract", "aggregate_assertion_count", 50 + 38 + len(audit.rows) + 1 == int(verification.get("aggregate_assertions", -1)), 50 + 38 + len(audit.rows) + 1, verification.get("aggregate_assertions"))

    payload = audit.finish(primary, independent, contract_observed)
    atomic_json(arguments.output, payload)
    print(
        f"R-129 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} integrated; "
        f"aggregate {payload['aggregate']['assertions_passed']}/"
        f"{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(
                    f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} "
                    f"expected={row['expected']!r}"
                )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
