#!/usr/bin/env python3
"""Integrated verifier for the A13 R-153 strict-past Hessian package."""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import ast
from fractions import Fraction as F
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
CLAIM_DIR = REPO / "claims" / CLAIM
RESULT_ID = "A13-CLASSII-PRODUCTION-STRICT-PAST-CONDITIONAL-HESSIAN-WEIGHTED-COLLAR-BOUNDARY"
LEDGER_ID = "R-153"
SLUG = "production-strict-past-conditional-hessian-weighted-collar-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
NOTE = CLAIM_DIR / "notes/classii-production-strict-past-conditional-hessian-weighted-collar-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 33, "independent": 27}
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(666, 671))
NEW_NEGATIVE_ID = "NG-2026-08-03-A13-NONDEGENERATE-GAUSSIAN-PAST-CURRENT-DETERMINISTIC-LINFTY-COLLAR"
REUSED_NEGATIVE_ID = "NG-2026-07-31-A13-SEPARATE-FLOOR-WEIGHTED-CURRENT-ENERGY-ABSORPTION"


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


def run_child(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path)], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )


def imported_roots(path: Path) -> tuple[set[str], bool]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    relative_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_import = relative_import or node.level > 0
            if node.module:
                roots.add(node.module.split(".")[0])
    return roots, relative_import


def find_poppler(name: str) -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(f"*/dependencies/native/poppler/Library/bin/{name}.exe"):
        if candidate.is_file():
            return candidate
    found = shutil.which(name)
    return Path(found) if found else None


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData", "/URI", "/GoToR",
    }
    allowed_actions = {"/GoTo"}

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, location: str, action_context: bool = False) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action = resolve(value.get("/S"))
            if action_context and action is not None and str(action) not in allowed_actions:
                findings.append(f"{location}/S={action}")
            for key, child in value.items():
                if str(key) in unsafe_keys:
                    findings.append(f"{location}{key}")
                visit(child, f"{location}{key}", action_context or str(key) in {"/A", "/AA", "/OpenAction", "/Next"})
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]", action_context)

    visit(resolve(reader.trailer["/Root"]), "/Root")
    return sorted(set(findings))


def open_action_summary(reader: PdfReader) -> tuple[bool, str]:
    root = reader.trailer["/Root"].get_object()
    action = root.get("/OpenAction")
    if not isinstance(action, ArrayObject) or len(action) != 2:
        return False, "missing or non-destination OpenAction"
    page_reference = action[0]
    first_reference = reader.pages[0].indirect_reference
    same_page = (
        isinstance(page_reference, IndirectObject)
        and first_reference is not None
        and page_reference.idnum == first_reference.idnum
        and page_reference.generation == first_reference.generation
    )
    mode = str(action[1])
    return same_page and mode == "/Fit", f"page_match={same_page}; mode={mode}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)
    contract = manifest["verification"]

    child_payloads: dict[str, dict[str, Any]] = {}
    embedded_child_rows = 0
    for name, path, output in (
        ("primary", PRIMARY, PRIMARY_OUTPUT),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT),
    ):
        run = run_child(path)
        audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
        child = load_json(output)
        child_payloads[name] = child
        rows = child.get("assertions", [])
        expected_count = EXPECTED_CHILD_COUNTS[name]
        expected_schema = f"tect/a13-{SLUG}-{name}/1.0"
        audit.check("children", f"{name} schema", child.get("schema") == expected_schema, child.get("schema"), expected_schema)
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} ledger", child.get("ledger_id") == LEDGER_ID, child.get("ledger_id"), LEDGER_ID)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} exact count", child.get("assertions_total") == len(rows) == expected_count, (child.get("assertions_total"), len(rows)), expected_count)
        audit.check("children", f"{name} every row passes", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        identities = [(row.get("group"), row.get("name")) for row in rows]
        audit.check("children", f"{name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
        embedded_child_rows += len(rows)
        for row in rows:
            audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))

    primary = child_payloads["primary"]
    independent = child_payloads["independent"]
    audit.check("children", "all child rows embedded once", embedded_child_rows == sum(EXPECTED_CHILD_COUNTS.values()), embedded_child_rows, sum(EXPECTED_CHILD_COUNTS.values()))
    audit.check("children", "child scopes equal manifest", primary.get("scope") == independent.get("scope") == manifest.get("scope"), (primary.get("scope"), independent.get("scope")), manifest.get("scope"))
    audit.check("children", "child no-overclaim equals manifest", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), (primary.get("no_overclaim"), independent.get("no_overclaim")), manifest.get("no_overclaim"))

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "standard-library only", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "no scientific package")
    audit.check("independence", "no primary import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "no a13_classii import")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    p = primary["derived"]
    i = independent["derived"]
    parity_pairs = {
        "volume": (p["volume"], i["volume"]),
        "conditional endpoint": (p["conditional_endpoint"], i["conditional_endpoint"]),
        "first coefficients": (p["first_variation_coefficients"], i["first_variation_coefficients"]),
        "bilinear coefficients": (p["bilinear_hessian_coefficients"], i["bilinear_hessian_coefficients"]),
        "diagonal coefficients": (p["diagonal_hessian_coefficients"], i["diagonal_hessian_coefficients"]),
        "sixth first": (p["sixth_first_factor"], i["sixth_first_factor"]),
        "sixth Hessian": (p["sixth_hessian_factors"], i["sixth_hessian_factors"]),
        "source Hessian": (p["source_hessian"], i["source_hessian"]),
        "operator threshold": (p["endpoint_plus_sixth_threshold"], i["endpoint_plus_sixth_threshold"]),
        "gradient upper": (p["control_mean_gradient_rational_upper"], i["control_mean_gradient_rational_upper"]),
        "gradient discriminant": (p["gradient_certificate_discriminant"], i["gradient_certificate_discriminant"]),
        "cube sums": (p["cube_reciprocal_sums"], i["cube_reciprocal_sums"]),
        "signed determinant": (p["signed_row_determinant"], i["signed_row_determinant"]),
    }
    for name, (left, right) in parity_pairs.items():
        audit.check("parity", name, left == right, left, right)
    audit.check("parity", "R-130 L6", F(p["r130_L6"]) == F(i["R130_L6"]), p["r130_L6"], i["R130_L6"])
    audit.check("parity", "R-130 H6", F(p["r130_H6"]) == F(i["R130_H6"]), p["r130_H6"], i["R130_H6"])
    audit.check("oracle", "source threshold exact", F(p["source_hessian"]) - F(1, 10) == F(4, 5), p["source_hessian"], "9/10 with 4/5 residual")
    audit.check("oracle", "gradient rational bound exact", F(p["control_mean_gradient_rational_upper"]) == F(41, 20), p["control_mean_gradient_rational_upper"], "41/20")
    audit.check("oracle", "signed row is indefinite", F(p["signed_row_determinant"]) == -3, p["signed_row_determinant"], -3)

    file_records = manifest["files"]
    artifact_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in artifact_paths.items():
        record = file_records[key]
        audit.check("artifacts", f"{key} path", record.get("path") == relative(path), record.get("path"), relative(path))
        audit.check("artifacts", f"{key} hash", record.get("sha256") == sha256(path), record.get("sha256"), sha256(path))
    for key, expected_hash in manifest["authority_hashes"].items():
        authority_path = REPO / manifest["authorities"][key]
        audit.check("authority-hashes", key, sha256(authority_path) == expected_hash, sha256(authority_path), expected_hash)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in (
        "future-current/trace cancellation", "bilinear Hessian", "spatial $L^2$ collar",
        "41\\over20", "positive-probability violation", "T-050 remains open",
        "No phase or PDE verdict", "Devil's-advocate", "Result footer",
    ):
        audit.check("note", f"scope token {token}", token.lower() in note_text.lower(), token, "present")

    pdf_manifest = contract["pdf"]
    pdf_before = sha256(PDF)
    build_environment = os.environ.copy()
    build_environment["SOURCE_DATE_EPOCH"] = str(pdf_manifest["source_date_epoch"])
    build_environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
        env=build_environment,
    )
    pdf_after = sha256(PDF)
    audit.check("pdf", "builder exits zero", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull boxes", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "deterministic rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    findings = pdf_security(reader)
    action_ok, action = open_action_summary(reader)
    page_count = len(reader.pages)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [] and action_ok, {"findings": findings, "open_action": action}, {"findings": [], "open_action": "first-page /Fit"})
    audit.check("pdf", "page count pinned", page_count == pdf_manifest.get("pages"), page_count, pdf_manifest.get("pages"))
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_manifest.get("size_bytes"), PDF.stat().st_size, pdf_manifest.get("size_bytes"))
    for token in ("R-153", "future-current/trace cancellation", "41/20", "positive-probability violation", "T-050 remains open", "No phase or PDE verdict"):
        audit.check("pdf", f"text contains {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r153-render-") as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_manifest.get("manual_visual_qa", "")).startswith("PASS"), pdf_manifest.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    status_card = load_json(CLAIM_DIR / "status.json")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    negatives_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    exploration_records = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    total_token = f"{contract['integrated_assertions']}/{contract['integrated_assertions']}"
    audit.check("records", "R-153 ledger entry", '<a id="r-153"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "R-153 claim narrative", RESULT_ID in claim_text and total_token in claim_text and "EXP-000666--EXP-000670" in claim_text, (RESULT_ID, total_token), "registered")
    audit.check("records", "R-153 lineage narrative", "R-153" in lineage_text and "weighted-collar" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check(
        "records",
        "status synchronization",
        status_card.get("no_overclaim") == manifest.get("no_overclaim")
        and total_token in str(status_card.get("notes", ""))
        and RESULT_ID in str(status_card.get("statement", "")),
        (status_card.get("no_overclaim"), status_card.get("statement")),
        "manifest, current result, and assertion count synchronized",
    )
    audit.check("records", "status reproduction", status_card.get("reproduction", {}).get("command") == contract.get("command") and total_token in str(status_card.get("reproduction", {}).get("expected", "")), status_card.get("reproduction"), contract.get("command"))
    audit.check("records", "status remains T4 with T-050 open", status_card.get("tier") == "T4" and "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE" in status_card.get("open_gates", []), (status_card.get("tier"), status_card.get("open_gates")), "T4 and T-050 open")
    audit.check("records", "TODO keeps route parked", all(token in todo_text for token in ("R-153", "T-054", "T-050", "parked")), "R-153/T-054/T-050/parked", "present")
    audit.check("records", "changelog records R-153", "R-153" in changelog_text and "conditional Hessian" in changelog_text, LEDGER_ID, "registered")
    audit.check("records", "new and reused negative routes registered", NEW_NEGATIVE_ID in negatives_text and REUSED_NEGATIVE_ID in negatives_text, [NEW_NEGATIVE_ID, REUSED_NEGATIVE_ID], "registered")
    audit.check("records", "theorem map frontier", theorem_map.get("active_frontier", {}).get("latest_result_id") == RESULT_ID, theorem_map.get("active_frontier", {}).get("latest_result_id"), RESULT_ID)
    audit.check(
        "records",
        "proof map contains R-153",
        "[R-153]" in proof_map
        and "Production strict-past conditional Hessian and weighted-collar boundary" in proof_map,
        LEDGER_ID,
        "generated",
    )
    for exploration_id in EXPLORATION_IDS:
        record = next((item for item in exploration_records if item.get("id") == exploration_id), None)
        audit.check("records", f"{exploration_id} exists", bool(record), exploration_id, "registered")
        if record:
            audit.check("records", f"{exploration_id} cites R-153", LEDGER_ID in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), LEDGER_ID)

    for key in ("uniform_absolute_gaussian_past_collar", "complete_progressive_owner_assembly", "production_loewner_gap", "t050_closed", "a13_closed", "sector_a_closed"):
        audit.check("scope", key, manifest["scope"].get(key) is False, manifest["scope"].get(key), False)
    audit.check("scope", "phase-neutral firewall", all(token in manifest["no_overclaim"] for token in ("select any phase", "validate or replace a PDE", "close Sector A")), manifest["no_overclaim"], "phase and PDE neutral")

    expected_total = len(audit.rows) + 1
    expected_integrator_only = expected_total - embedded_child_rows
    audit.check("aggregation", "manifest assertion counts", contract.get("integrated_assertions") == expected_total and contract.get("integrator_only_assertions") == expected_integrator_only, (contract.get("integrated_assertions"), contract.get("integrator_only_assertions")), (expected_total, expected_integrator_only))
    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "ledger_id": LEDGER_ID,
        "status": status,
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in audit.rows),
        "embedded_child_assertions": embedded_child_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_child_rows,
        "assertions": audit.rows,
        "children": {
            "primary": {"path": relative(PRIMARY_OUTPUT), "sha256": sha256(PRIMARY_OUTPUT)},
            "independent": {"path": relative(INDEPENDENT_OUTPUT), "sha256": sha256(INDEPENDENT_OUTPUT)},
        },
        "pdf": {"sha256": pdf_after, "pages": page_count, "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(arguments.output, payload)
    print(f"{status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    print(f"embedded child rows: {embedded_child_rows}; integrator-only: {payload['integrator_only_assertions']}")
    print(f"artifact: {arguments.output}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
