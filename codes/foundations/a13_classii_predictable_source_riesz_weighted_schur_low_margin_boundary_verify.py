#!/usr/bin/env python3
"""Integrated authority and release audit for the scoped R-127 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

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
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY"
SCHEMA = "tect/a13-predictable-source-riesz-weighted-schur-low-margin-boundary-integrated/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_predictable_source_riesz_weighted_schur_low_margin_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_predictable_source_riesz_weighted_schur_low_margin_boundary_independent.py"
PRIMARY_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-integrated-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"
MANIFEST = CLAIM_DIR / "classii_predictable_source_riesz_weighted_schur_low_margin_boundary_manifest.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def pdf_javascript_audit(reader: PdfReader) -> tuple[list[str], str, bool]:
    """Inspect the resolved PDF object graph, allowing only safe open destinations."""
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()

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
            except Exception as exc:  # pragma: no cover - corruption guard
                findings.append(f"{path}:unreadable:{type(exc).__name__}")
                return
        if isinstance(value, DictionaryObject):
            action_type = resolve(value.get("/S"))
            if str(action_type) == "/JavaScript":
                findings.append(f"{path}/S=/JavaScript")
            for key, child in value.items():
                key_text = str(key)
                if key_text in {"/JS", "/JavaScript"}:
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
    return sorted(set(findings)), open_action_kind, safe_open_action


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

    def finish(self, primary: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        aggregate_total = int(primary["assertions_total"]) + int(independent["assertions_total"]) + len(self.rows)
        aggregate_passed = int(primary["assertions_passed"]) + int(independent["assertions_passed"]) + passed
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
                "predictable_source_and_quotient_geometry_registered": True,
                "weighted_schur_and_augmented_loewner_registered": True,
                "gauge_and_curvature_boundaries_registered": True,
                "production_source_hessian_identification_proved": False,
                "production_projected_force_bound_proved": False,
                "unified_production_bound_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-127 is a chartwise structural and conditional-operator checkpoint. It proves "
                "no complete production source-Hessian identification, projected-force norm, "
                "unified forward/legal-reverse/balanced/low estimate, OVERLAP_src, Nelson bound, "
                "removal, interacting measure, Sector-A closure, or tier promotion."
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    audit.check("children", "primary_count", primary.get("assertions_total") == 52, primary.get("assertions_total"), 52)
    audit.check("children", "independent_count", independent.get("assertions_total") == 60, independent.get("assertions_total"), 60)
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    audit.check(
        "children",
        "non_importing_independent",
        "import a13_classii_predictable_source_riesz" not in independent_source,
        "primary import absent",
        "primary import absent",
    )
    audit.check("children", "independent_no_sympy", "import sympy" not in independent_source, "sympy import absent", "sympy import absent")

    audit.check("manifest", "exists", MANIFEST.is_file(), MANIFEST.is_file(), True)
    if not MANIFEST.is_file():
        print("R-127 integrated BLOCKED: manifest missing")
        return 1
    manifest = load_json(MANIFEST)
    audit.check(
        "manifest",
        "schema",
        manifest.get("schema") == "tect/a13-predictable-source-riesz-weighted-schur-low-margin-boundary-manifest/1.0",
        manifest.get("schema"),
        "tect/a13-predictable-source-riesz-weighted-schur-low-margin-boundary-manifest/1.0",
    )
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger_id", manifest.get("result_ledger_id") == "R-127", manifest.get("result_ledger_id"), "R-127")

    for name, entry in manifest.get("authorities", {}).items():
        path = REPO / entry["path"]
        audit.check("authority", f"{name}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            audit.check("authority", f"{name}_sha256", digest(path) == entry["sha256"], digest(path), entry["sha256"])

    for name, entry in manifest.get("files", {}).items():
        path = REPO / entry["path"]
        audit.check("files", f"{name}_exists", path.is_file(), path.is_file(), True)
        if path.is_file() and entry.get("sha256"):
            audit.check("files", f"{name}_sha256", digest(path) == entry["sha256"], digest(path), entry["sha256"])

    note_path = REPO / manifest["files"]["note"]["path"]
    pdf_path = REPO / manifest["files"]["pdf"]["path"]
    note = note_path.read_text(encoding="utf-8")
    for phrase in (
        "Exact predictable-source adjoint",
        "weighted triangular Schur bound",
        "augmented low/injected Loewner criterion",
        "normalized Gibbs--Doob absolute-anchor no-go",
        "coherent residual interpolation",
        "no complete production source-Hessian",
    ):
        audit.check("note", f"phrase_{phrase[:20]}", phrase.lower() in note.lower(), phrase in note, True)

    reader = PdfReader(str(pdf_path))
    fields = reader.get_fields() or {}
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    pdf_contract = manifest["verification"]["pdf"]
    audit.check("pdf", "pages", len(reader.pages) == pdf_contract["pages"], len(reader.pages), pdf_contract["pages"])
    audit.check("pdf", "ten_or_more_content", len(reader.pages) >= 10, len(reader.pages), ">= 10")
    audit.check("pdf", "all_pages_nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], "all >= 20")
    audit.check("pdf", "no_form", not fields, sorted(fields), [])
    javascript_paths, open_action_kind, safe_open_action = pdf_javascript_audit(reader)
    audit.check(
        "pdf",
        "no_javascript_and_safe_open_action",
        not javascript_paths and safe_open_action,
        {"javascript_paths": javascript_paths, "open_action": open_action_kind},
        {"javascript_paths": [], "open_action": "absent, destination-array, or /GoTo"},
    )
    audit.check("pdf", "title_text", "Predictable-source Riesz geometry" in extracted, "Predictable-source Riesz geometry" in extracted, True)
    audit.check("pdf", "footer_text", "R-127" in extracted and "Sector-A" in extracted, "R-127" in extracted and "Sector-A" in extracted, True)
    audit.check("pdf", "size", pdf_path.stat().st_size == pdf_contract["size_bytes"], pdf_path.stat().st_size, pdf_contract["size_bytes"])
    audit.check("pdf", "visual_qa", pdf_contract.get("visual_qa") == "PASS", pdf_contract.get("visual_qa"), "PASS")
    audit.check("pdf", "overfull", pdf_contract.get("overfull_hbox_count") == 0, pdf_contract.get("overfull_hbox_count"), 0)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("claim", "statement", status["statement"].startswith("R-127 advances A13"), status["statement"][:22], "R-127 advances A13")
    audit.check("claim", "reproduction", status["reproduction"]["command"].endswith("a13_classii_predictable_source_riesz_weighted_schur_low_margin_boundary_verify.py"), status["reproduction"]["command"], "R-127 verifier")
    audit.check("claim", "tier_unchanged", status["tier"] == "T4", status["tier"], "T4")
    audit.check(
        "claim",
        "gates_open",
        set(status["open_gates"]) == {"A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION", "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"},
        status["open_gates"],
        "both A13 gates",
    )

    surfaces = {
        "result_summary": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "exploration": REPO / "explorations/log.jsonl",
        "todo": REPO / "todo/todo.json",
        "claim_history": CLAIM_DIR / "claim.md",
        "narrative": CLAIM_DIR / "lineage-narrative.md",
        "changelog": REPO / "changelog/log.jsonl",
        "claims_generated": REPO / "CLAIMS.md",
        "index_generated": CLAIM_DIR / "INDEX.md",
        "lineage_generated": CLAIM_DIR / "LINEAGE.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "sector_map": REPO / "governance/sector-a-theorem-map.json",
    }
    needles = {
        "result_summary": "R-127",
        "negative": "NG-2026-07-30-A13-UNRESTRICTED-PREDICTABLE-COVARIANCE-COLLAPSE",
        "exploration": "EXP-000430",
        "todo": "R-127 proves",
        "claim_history": RESULT_ID,
        "narrative": "Predictable-source Riesz geometry",
        "changelog": "R-127",
        "claims_generated": CLAIM,
        "index_generated": "R-127 advances A13",
        "lineage_generated": "Predictable-source Riesz geometry",
        "proof_map": "R-127",
        "sector_map": RESULT_ID,
    }
    for name, path in surfaces.items():
        audit.check("surfaces", f"{name}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            present = needles[name] in path.read_text(encoding="utf-8")
            audit.check("surfaces", f"{name}_content", present, present, True)

    exploration_lines = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_ids = {record["id"] for record in exploration_lines}
    for identifier in manifest.get("exploration_ids", []):
        audit.check("explorations", identifier, identifier in exploration_ids, identifier in exploration_ids, True)

    negative = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in manifest.get("negative_results", []):
        audit.check("negatives", identifier, f"### {identifier}" in negative, f"### {identifier}" in negative, True)

    expected_integrated = int(manifest["verification"]["integrated_assertions"])
    audit.check("contract", "integrated_assertion_count", len(audit.rows) + 2 == expected_integrated, len(audit.rows) + 2, expected_integrated)
    expected_aggregate = int(manifest["verification"]["aggregate_assertions"])
    audit.check("contract", "aggregate_assertion_count", 52 + 60 + len(audit.rows) + 1 == expected_aggregate, 52 + 60 + len(audit.rows) + 1, expected_aggregate)

    payload = audit.finish(primary, independent)
    atomic_json(arguments.output, payload)
    print(
        f"R-127 integrated {payload['status']} "
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
