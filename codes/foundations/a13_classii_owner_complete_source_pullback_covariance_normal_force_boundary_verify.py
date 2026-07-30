#!/usr/bin/env python3
"""Integrated authority and release audit for the scoped R-128 checkpoint."""

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
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY"
SCHEMA = "tect/a13-owner-complete-source-pullback-covariance-normal-force-boundary-integrated/1.0"
MANIFEST_SCHEMA = "tect/a13-owner-complete-source-pullback-covariance-normal-force-boundary-manifest/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_owner_complete_source_pullback_covariance_normal_force_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_owner_complete_source_pullback_covariance_normal_force_boundary_independent.py"
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-integrated-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"
MANIFEST = CLAIM_DIR / "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json"
EXPECTED_AUTHORITY_KEYS = {
    "governance",
    "a1",
    "r079",
    "r093",
    "r103",
    "r103_primary",
    "r104",
    "r119",
    "r120",
    "r121",
    "r122",
    "r123",
    "r124",
    "r124_primary",
    "r125",
    "r126",
    "r126_primary",
    "r127",
    "r127_primary",
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


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    """Traverse resolved objects and reject executable or embedded PDF features."""
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
        "/EmbeddedFiles",
        "/RichMedia",
        "/Movie",
        "/Sound",
        "/XFA",
        "/SubmitForm",
        "/ImportData",
    }

    def resolve(value: Any) -> Any:
        if isinstance(value, IndirectObject):
            return value.get_object()
        return value

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

    annotation_findings: list[str] = []
    widget_count = 0
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


def confined_path(relative: str) -> tuple[Path, bool]:
    path = (REPO / relative).resolve()
    try:
        path.relative_to(REPO.resolve())
        return path, True
    except ValueError:
        return path, False


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
        self, primary: dict[str, Any], independent: dict[str, Any]
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
            "scope": {
                "fixed_chart_owner_pullback_registered": True,
                "control_and_malliavin_derivatives_separated": True,
                "covariance_normal_force_repaired": True,
                "refinement_naturality_registered": True,
                "conditional_strict_margin_registered": True,
                "production_root_shell_intertwiner_proved": False,
                "production_covariance_normal_bound_proved": False,
                "balanced_and_low_uniform_bound_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-128 is a fixed-chart structural and force-repair checkpoint. It proves "
                "no production root-shell intertwiner, corrected covariance-normal "
                "operator bound, balanced/low uniform closure, absolute low anchor, "
                "OVERLAP_src, Nelson bound, removal, interacting measure, Sector-A "
                "closure, or tier promotion."
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
    audit.check("children", "primary_status", primary.get("status") == "PASS", primary.get("status"), "PASS")
    audit.check("children", "independent_status", independent.get("status") == "PASS", independent.get("status"), "PASS")
    audit.check("children", "primary_result_id", primary.get("result_id") == RESULT_ID, primary.get("result_id"), RESULT_ID)
    audit.check("children", "independent_result_id", independent.get("result_id") == RESULT_ID, independent.get("result_id"), RESULT_ID)
    audit.check("children", "primary_count", primary.get("assertions_total") == 43, primary.get("assertions_total"), 43)
    audit.check("children", "independent_count", independent.get("assertions_total") == 32, independent.get("assertions_total"), 32)
    audit.check("children", "primary_no_failures", primary.get("assertions_failed") == 0, primary.get("assertions_failed"), 0)
    audit.check("children", "independent_no_failures", independent.get("assertions_failed") == 0, independent.get("assertions_failed"), 0)
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
        not any("a13_classii_owner_complete_source_pullback" in name for name in imported_modules)
        and PRIMARY.name not in independent_source,
        {"imports": sorted(imported_modules), "primary_filename_present": PRIMARY.name in independent_source},
        "primary import/read absent",
    )
    audit.check("children", "independent_no_sympy", "import sympy" not in independent_source, "sympy import absent", "sympy import absent")

    audit.check("manifest", "exists", MANIFEST.is_file(), MANIFEST.is_file(), True)
    if not MANIFEST.is_file():
        print("R-128 integrated BLOCKED: manifest missing")
        return 1
    manifest = load_json(MANIFEST)
    audit.check("manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA)
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger_id", manifest.get("result_ledger_id") == "R-128", manifest.get("result_ledger_id"), "R-128")
    verification = manifest.get("verification", {})
    audit.check("manifest", "primary_contract", verification.get("primary_assertions") == 43, verification.get("primary_assertions"), 43)
    audit.check("manifest", "independent_contract", verification.get("independent_assertions") == 32, verification.get("independent_assertions"), 32)
    audit.check("manifest", "primary_schema", verification.get("primary_schema") == primary.get("schema"), primary.get("schema"), verification.get("primary_schema"))
    audit.check("manifest", "independent_schema", verification.get("independent_schema") == independent.get("schema"), independent.get("schema"), verification.get("independent_schema"))

    authorities = manifest.get("authorities", {})
    files = manifest.get("files", {})
    audit.check("manifest", "authority_keys", set(authorities) == EXPECTED_AUTHORITY_KEYS, sorted(authorities), sorted(EXPECTED_AUTHORITY_KEYS))
    audit.check("manifest", "file_keys", set(files) == EXPECTED_FILE_KEYS, sorted(files), sorted(EXPECTED_FILE_KEYS))
    authority_paths = [str(entry.get("path", "")) for entry in authorities.values()]
    audit.check("manifest", "unique_authority_paths", len(authority_paths) == len(set(authority_paths)), authority_paths, "all unique")

    for name, entry in authorities.items():
        expected_hash = str(entry.get("sha256", ""))
        audit.check("authority", f"{name}_hash_format", SHA256_PATTERN.fullmatch(expected_hash) is not None, expected_hash, "64 lowercase hex")
        path, confined = confined_path(str(entry.get("path", "")))
        audit.check("authority", f"{name}_confined", confined, str(path), str(REPO.resolve()))
        audit.check("authority", f"{name}_exists", confined and path.is_file(), path.is_file(), True)
        if confined and path.is_file():
            actual_hash = digest(path)
            audit.check("authority", f"{name}_sha256", actual_hash == expected_hash, actual_hash, expected_hash)

    for name, entry in files.items():
        expected_hash = str(entry.get("sha256", ""))
        audit.check("files", f"{name}_hash_format", SHA256_PATTERN.fullmatch(expected_hash) is not None, expected_hash, "64 lowercase hex")
        path, confined = confined_path(str(entry.get("path", "")))
        audit.check("files", f"{name}_confined", confined, str(path), str(REPO.resolve()))
        audit.check("files", f"{name}_exists", confined and path.is_file(), path.is_file(), True)
        if confined and path.is_file() and expected_hash:
            actual_hash = digest(path)
            audit.check("files", f"{name}_sha256", actual_hash == expected_hash, actual_hash, expected_hash)

    audit.check(
        "manifest",
        "pdf_contract_path_matches_file",
        verification.get("pdf", {}).get("path") == files.get("pdf", {}).get("path"),
        verification.get("pdf", {}).get("path"),
        files.get("pdf", {}).get("path"),
    )
    audit.check(
        "manifest",
        "pdf_contract_hash_matches_file",
        verification.get("pdf", {}).get("sha256") == files.get("pdf", {}).get("sha256"),
        verification.get("pdf", {}).get("sha256"),
        files.get("pdf", {}).get("sha256"),
    )

    note_path, note_confined = confined_path(manifest["files"]["note"]["path"])
    pdf_path, pdf_confined = confined_path(manifest["files"]["pdf"]["path"])
    if not note_confined or not pdf_confined or not note_path.is_file() or not pdf_path.is_file():
        print("R-128 integrated BLOCKED: note/PDF path contract invalid")
        return 1
    note_check = subprocess.run(
        [
            sys.executable,
            str(REPO / "verification/scripts/build_note_pdf.py"),
            str(note_path),
            "--no-compile",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    audit.check("note", "form_check_exit", note_check.returncode == 0, note_check.returncode, 0)
    audit.check("note", "form_check_banner", "FORM-CHECK: PASS" in note_check.stdout, note_check.stdout.strip(), "FORM-CHECK: PASS")
    note = note_path.read_text(encoding="utf-8")
    normalized_note = " ".join(note.lower().split())
    for phrase in (
        "Differentiated complete-owner control pullback",
        "Control-shift versus Malliavin-source firewall",
        "Covariance-normal force and the missing future variance",
        "Common terminal and legal reverse firewalls",
        "Corrected augmented Loewner target",
        "Source-allocation firewall",
        "fixed bounded linear admissible",
        "scalar \\(R=S=0\\) specialization",
        "A13-CLASSII-PRODUCTION-AUGMENTED-SOURCE-HESSIAN",
        "no production root/shell intertwiner",
    ):
        present = " ".join(phrase.lower().split()) in normalized_note
        audit.check("note", f"phrase_{phrase[:22]}", present, present, True)

    audit.check("note", "source_note_hash", verification.get("source_note_sha256") == digest(note_path), verification.get("source_note_sha256"), digest(note_path))

    reader = PdfReader(str(pdf_path))
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    fields = reader.get_fields() or {}
    pdf_contract = verification["pdf"]
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "pages", len(reader.pages) == pdf_contract["pages"], len(reader.pages), pdf_contract["pages"])
    audit.check("pdf", "all_pages_nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], "all >= 20")
    audit.check("pdf", "no_form", not fields, sorted(fields), [])
    page_geometry = [
        {
            "width": float(page.mediabox.width),
            "height": float(page.mediabox.height),
            "rotation": int(page.get("/Rotate", 0) or 0) % 360,
        }
        for page in reader.pages
    ]
    audit.check("pdf", "positive_page_boxes", all(item["width"] > 0 and item["height"] > 0 for item in page_geometry), page_geometry, "positive dimensions")
    audit.check("pdf", "page_rotation", all(item["rotation"] == 0 for item in page_geometry), [item["rotation"] for item in page_geometry], "all zero")
    security = pdf_security_audit(reader)
    audit.check(
        "pdf",
        "no_unsafe_features_and_safe_open_action",
        not security["findings"] and security["safe_open_action"],
        security,
        {"findings": [], "open_action": "absent, destination-array, or /GoTo", "widget_count": 0},
    )
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)
    audit.check("pdf", "title_text", "complete-owner control-shift naturality" in extracted, "complete-owner control-shift naturality" in extracted, True)
    audit.check("pdf", "footer_text", "R-128" in extracted and "Sector-A" in extracted, "R-128" in extracted and "Sector-A" in extracted, True)
    audit.check("pdf", "size", pdf_path.stat().st_size == pdf_contract["size_bytes"], pdf_path.stat().st_size, pdf_contract["size_bytes"])
    visual = pdf_contract.get("visual_qa", {})
    audit.check("pdf", "visual_status", visual.get("status") == "PASS", visual.get("status"), "PASS")
    audit.check("pdf", "visual_renderer", visual.get("renderer") == "Poppler pdftoppm", visual.get("renderer"), "Poppler pdftoppm")
    audit.check("pdf", "visual_dpi", int(visual.get("dpi", 0)) >= 120, visual.get("dpi"), ">= 120")
    audit.check("pdf", "visual_page_counts", visual.get("rendered_pages") == len(reader.pages) and visual.get("inspected_pages") == len(reader.pages), {"rendered": visual.get("rendered_pages"), "inspected": visual.get("inspected_pages")}, len(reader.pages))
    audit.check("pdf", "visual_manual_all_pages", visual.get("method") == "manual-all-pages", visual.get("method"), "manual-all-pages")
    audit.check("pdf", "visual_no_defects", visual.get("defects") == [], visual.get("defects"), [])
    audit.check("pdf", "visual_summary", len(str(visual.get("summary", "")).strip()) >= 40, visual.get("summary"), "nonempty detailed summary")
    audit.check("pdf", "overfull", pdf_contract.get("overfull_hbox_count") == 0, pdf_contract.get("overfull_hbox_count"), 0)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("claim", "statement", status["statement"].startswith("R-128 advances A13"), status["statement"][:22], "R-128 advances A13")
    audit.check("claim", "reproduction", status["reproduction"]["command"].endswith("a13_classii_owner_complete_source_pullback_covariance_normal_force_boundary_verify.py"), status["reproduction"]["command"], "R-128 verifier")
    audit.check("claim", "tier_unchanged", status["tier"] == "T4", status["tier"], "T4")
    expected_gates = {
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
    }
    audit.check("claim", "gates_open", set(status["open_gates"]) == expected_gates, status["open_gates"], "both A13 gates")

    surfaces = {
        "result_summary": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "exploration": REPO / "explorations/log.jsonl",
        "todo": REPO / "todo/todo.json",
        "claim_history": CLAIM_DIR / "claim.md",
        "changelog": REPO / "changelog/log.jsonl",
        "claims_generated": REPO / "CLAIMS.md",
        "index_generated": CLAIM_DIR / "INDEX.md",
        "lineage_generated": CLAIM_DIR / "LINEAGE.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "sector_map": REPO / "governance/sector-a-theorem-map.json",
        "sector_dossier": REPO / "theory/sectors/A.md",
    }
    needles = {
        "result_summary": "R-128",
        "negative": "AUDIT-2026-07-30-A13-R126-COVARIANCE-NORMAL-FORCE-OMISSION",
        "exploration": "EXP-000446",
        "todo": "R-128 proves",
        "claim_history": RESULT_ID,
        "changelog": "R-128",
        "claims_generated": CLAIM,
        "index_generated": "R-128 advances A13",
        "lineage_generated": "Differentiated complete-owner",
        "proof_map": "R-128",
        "sector_map": RESULT_ID,
        "sector_dossier": "NG-2026-07-30-A13-CONTROL-MALLIAVIN-DERIVATIVE-CONFLATION",
    }
    for name, path in surfaces.items():
        audit.check("surfaces", f"{name}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            present = needles[name] in path.read_text(encoding="utf-8")
            audit.check("surfaces", f"{name}_content", present, present, True)

    exploration_records = [
        json.loads(line)
        for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exploration_ids = {record["id"] for record in exploration_records}
    for identifier in manifest.get("exploration_ids", []):
        audit.check("explorations", identifier, identifier in exploration_ids, identifier in exploration_ids, True)

    negative = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in manifest.get("negative_results", []):
        audit.check("negatives", identifier, f"### {identifier}" in negative, f"### {identifier}" in negative, True)

    precontract_count = len(audit.rows)
    precontract_identifier_hash = hashlib.sha256(
        "\n".join(sorted(audit.identifiers)).encode("utf-8")
    ).hexdigest()
    audit.check("contract", "precontract_assertion_count", precontract_count == int(verification["integrated_precontract_assertions"]), precontract_count, int(verification["integrated_precontract_assertions"]))
    audit.check("contract", "precontract_identifier_hash", precontract_identifier_hash == verification["integrated_precontract_identifier_sha256"], precontract_identifier_hash, verification["integrated_precontract_identifier_sha256"])
    expected_integrated = int(verification["integrated_assertions"])
    audit.check("contract", "integrated_assertion_count", len(audit.rows) + 2 == expected_integrated, len(audit.rows) + 2, expected_integrated)
    expected_aggregate = int(verification["aggregate_assertions"])
    audit.check("contract", "aggregate_assertion_count", 43 + 32 + len(audit.rows) + 1 == expected_aggregate, 43 + 32 + len(audit.rows) + 1, expected_aggregate)

    payload = audit.finish(primary, independent)
    atomic_json(arguments.output, payload)
    print(
        f"R-128 integrated {payload['status']} "
        f"{payload['assertions_passed']}/{payload['assertions_total']}; "
        f"primary {primary['assertions_passed']}/{primary['assertions_total']}; "
        f"independent {independent['assertions_passed']}/{independent['assertions_total']}; "
        f"aggregate {payload['aggregate']['assertions_passed']}/{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} expected={row['expected']!r}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
