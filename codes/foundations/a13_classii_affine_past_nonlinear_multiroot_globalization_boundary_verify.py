#!/usr/bin/env python3
"""Integrated verifier for the A13 R-152 globalization-boundary package."""

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
RESULT_ID = "A13-CLASSII-AFFINE-PAST-NONLINEAR-MULTIROOT-GLOBALIZATION-BOUNDARY"
LEDGER_ID = "R-152"
SLUG = "affine-past-nonlinear-multiroot-globalization-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_affine_past_nonlinear_multiroot_globalization_boundary_manifest.json"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
NOTE = CLAIM_DIR / "notes/classii-affine-past-nonlinear-multiroot-globalization-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 32, "independent": 26}
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(661, 666))
NEGATIVE_IDS = (
    "NG-2026-08-03-A13-LINEAR-PAIR-TESTS-DO-NOT-IMPLY-NONLINEAR-PREDICTABLE-GAP",
    "NG-2026-08-03-A13-PAIRWISE-LOCAL-GAPS-DO-NOT-IMPLY-MULTIROOT-GLOBAL-GAP",
)


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
    options = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    child_runs = {"primary": run_child(PRIMARY), "independent": run_child(INDEPENDENT)}
    for name, run in child_runs.items():
        audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = {"primary": primary, "independent": independent}
    embedded_child_rows = 0
    for name, child in children.items():
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
        for row in rows:
            embedded_child_rows += 1
            audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))
    expected_embedded = sum(EXPECTED_CHILD_COUNTS.values())
    audit.check("children", "all child rows embedded once", embedded_child_rows == expected_embedded, embedded_child_rows, expected_embedded)
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
    common_keys = (
        "mass_floor", "mass_floor_minors", "affine_past_delta_coefficients",
        "endpoint_loss_strict_upper", "loss_sturm_coefficients_ascending",
        "loss_sturm_zero_signs", "loss_sturm_infinity_signs", "lower_symbol_minimum",
        "inverse_lambda2_strict_upper", "p_over_lambda2_strict_upper",
        "zero_current_affine_past_gap_strict_lower", "source_hessian",
        "retained_gap_strict_lower", "conditional_operator_endpoint_threshold",
        "multi_root_augmented_matrix", "multi_root_augmented_eigenvalues",
    )
    for key in common_keys:
        audit.check("parity", key, p.get(key) == i.get(key), p.get(key), i.get(key))
    audit.check("parity", "volume", F(p["volume"]) == F(i["volume"]), p["volume"], i["volume"])
    audit.check("parity", "R-130 L6", F(p["r130_L6"]) == F(i["R130_L6"]), p["r130_L6"], i["R130_L6"])
    audit.check("parity", "R-130 H6", F(p["r130_H6"]) == F(i["R130_H6"]), p["r130_H6"], i["R130_H6"])
    audit.check("parity", "collar N-MW rational part", p["uniform_past_collar_coefficients"]["N_MW"].endswith("*sqrt(3)/125") and i["uniform_past_collar_rational_coefficients"]["N_MW_times_sqrt3"] == "1524/125", (p["uniform_past_collar_coefficients"]["N_MW"], i["uniform_past_collar_rational_coefficients"]["N_MW_times_sqrt3"]), "1524 sqrt(3)/125")
    audit.check("parity", "collar N-MY rational part", p["uniform_past_collar_coefficients"]["N_MY"].endswith("*sqrt(3)/16") and i["uniform_past_collar_rational_coefficients"]["N_MY_times_sqrt3"] == "787/16", (p["uniform_past_collar_coefficients"]["N_MY"], i["uniform_past_collar_rational_coefficients"]["N_MY_times_sqrt3"]), "787 sqrt(3)/16")
    audit.check("parity", "collar N-square", p["uniform_past_collar_coefficients"]["N_squared"] == i["uniform_past_collar_rational_coefficients"]["N_squared"], p["uniform_past_collar_coefficients"]["N_squared"], i["uniform_past_collar_rational_coefficients"]["N_squared"])
    audit.check("parity", "nonlinear fixture c", p["nonlinear_fixture_c"] == i["nonlinear_fixture"]["c"], p["nonlinear_fixture_c"], i["nonlinear_fixture"]["c"])
    audit.check("parity", "nonlinear fixture linear loss", p["nonlinear_linear_test_loss"] == i["nonlinear_fixture"]["linear_loss"], p["nonlinear_linear_test_loss"], i["nonlinear_fixture"]["linear_loss"])
    audit.check("parity", "nonlinear fixture bump", p["nonlinear_bump_augmented_upper"] == i["nonlinear_fixture"]["bump_augmented_upper"], p["nonlinear_bump_augmented_upper"], i["nonlinear_fixture"]["bump_augmented_upper"])

    # Named exact test oracles; production constants themselves come from pinned upstream results.
    source = F(p["source_hessian"])
    loss = F(p["endpoint_loss_strict_upper"])
    collar = F(p["past_collar_budget"])
    audit.check("oracle", "affine delta factors", p["affine_past_delta_coefficients"] == [2, 1, "1/2"], p["affine_past_delta_coefficients"], [2, 1, "1/2"])
    audit.check("oracle", "source minus endpoint loss", source - loss == F(p["zero_current_affine_past_gap_strict_lower"]) == F(7, 50), source - loss, F(7, 50))
    audit.check("oracle", "collar retains target gap", source - loss - collar == F(p["retained_gap_strict_lower"]) == F(1, 10), source - loss - collar, F(1, 10))
    audit.check("oracle", "conditional endpoint threshold", -F(p["conditional_operator_endpoint_threshold"]) == source - F(1, 10) == F(4, 5), p["conditional_operator_endpoint_threshold"], -F(4, 5))
    c = F(p["nonlinear_fixture_c"])
    center = F(p["nonlinear_bump_center"])
    audit.check("oracle", "nonlinear linear test arithmetic", 3 * c == F(p["nonlinear_linear_test_loss"]) < F(4, 5), 3 * c, "<4/5")
    audit.check("oracle", "translated bump arithmetic", source - c * (center - 1) ** 2 == F(p["nonlinear_bump_augmented_upper"]) < 0, source - c * (center - 1) ** 2, "<0")
    matrix = [[F(value) for value in row] for row in p["multi_root_augmented_matrix"]]
    eigenvalues = sorted([matrix[0][0] + matrix[0][1], matrix[0][0] - matrix[0][1]])
    audit.check("oracle", "two-edge eigenvalues reconstructed", eigenvalues == [F(-1, 20), F(7, 20)], eigenvalues, [F(-1, 20), F(7, 20)])

    for key, path_text in manifest.get("authorities", {}).items():
        path = REPO / path_text
        audit.check("authority", f"{key} exists", path.is_file(), relative(path), "file")
        audit.check("authority", f"{key} hash", manifest.get("authority_hashes", {}).get(key) == sha256(path), manifest.get("authority_hashes", {}).get(key), sha256(path))
    for key, record in manifest.get("files", {}).items():
        path = REPO / record["path"]
        audit.check("artifact", f"{key} exists", path.is_file(), relative(path), "file")
        if "sha256" in record:
            audit.check("artifact", f"{key} hash", record["sha256"] == sha256(path), record["sha256"], sha256(path))
        if key in {"primary", "independent", "verifier"}:
            audit.check("artifact", f"{key} version", record.get("version") == "1.0.0", record.get("version"), "1.0.0")

    note_text = NOTE.read_text(encoding="utf-8")
    audit.check("note", "primitive trace outside spatial sum", "\\}\\ -{1\\over2}\\Tr" in note_text and "\\sum_i\\{&U_i^*BU_i" in note_text, "one primitive trace", "outside sum_i")
    for token in ("production synthesis one", "n_i=\\partial_i m", "finite cylindrical/root-coordinate", "closed-range compatibility", "not an A1 production counterexample"):
        audit.check("note", f"scope token {token}", token.lower() in note_text.lower(), token, "present")

    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785715200"
    environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO, env=environment, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
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
    pdf_manifest = manifest["verification"]["pdf"]
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [] and action_ok, {"findings": findings, "open_action": action}, {"findings": [], "open_action": "first-page /Fit"})
    audit.check("pdf", "page count pinned", page_count == pdf_manifest.get("pages"), page_count, pdf_manifest.get("pages"))
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_manifest.get("size_bytes"), PDF.stat().st_size, pdf_manifest.get("size_bytes"))
    extracted = " ".join(
        "\n".join((page.extract_text() or "") for page in reader.pages).lower().split()
    )
    for token in ("nonlinear conditional operator", "r-152", "form domain", "not an a1 production counterexample", "t-050", "sector a closed: false", "no-overclaim"):
        audit.check("pdf", f"text contains {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r152-render-") as directory:
            target = Path(directory) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(directory).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_manifest.get("manual_visual_qa", "")).startswith("PASS"), pdf_manifest.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    status_card = load_json(CLAIM_DIR / "status.json")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    exploration_rows = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_by_id = {row["id"]: row for row in exploration_rows}
    contract = manifest["verification"]
    total_token = f"{contract['integrated_assertions']}/{contract['integrated_assertions']}"
    required_evidence = {relative(MANIFEST), "RESULTS-LEDGER.md#r-152", "explorations/log.jsonl#EXP-000661--EXP-000665"}
    required_evidence.update(f"negative-results/registry.md#{item.lower()}" for item in NEGATIVE_IDS)
    required_evidence.update(record["path"] for record in manifest["files"].values())
    missing_evidence = sorted(required_evidence - set(status_card.get("legacy_evidence", [])))
    audit.check("records", "R-152 ledger entry", '<a id="r-152"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "R-152 claim narrative", RESULT_ID in claim_text and total_token in claim_text and "EXP-000661--EXP-000665" in claim_text, (RESULT_ID, total_token), "registered")
    audit.check("records", "R-152 lineage narrative", "R-152" in lineage_text and "globalization boundary" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "status synchronization", status_card.get("no_overclaim") == manifest.get("no_overclaim") and total_token in str(status_card.get("notes", "")) and not missing_evidence, (status_card.get("no_overclaim"), missing_evidence), "manifest and evidence synchronized")
    audit.check("records", "status reproduction", status_card.get("reproduction", {}).get("command") == contract.get("command") and total_token in str(status_card.get("reproduction", {}).get("expected", "")), status_card.get("reproduction"), contract.get("command"))
    audit.check("records", "status remains T4 with T-050 open", status_card.get("tier") == "T4" and "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE" in status_card.get("open_gates", []), (status_card.get("tier"), status_card.get("open_gates")), "T4 and T-050 open")
    audit.check("records", "TODO route transition", all(token in todo_text for token in ("R-152", "T-054", "T-052", "parked")), "R-152/T-054/T-052", "present")
    audit.check("records", "changelog records R-152", "R-152" in changelog_text and "globalization boundary" in changelog_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "negative routes registered", all(item in negatives_text for item in NEGATIVE_IDS), NEGATIVE_IDS, "registered")
    audit.check("records", "theorem map frontier", theorem_map.get("active_frontier", {}).get("latest_result_id") == RESULT_ID, theorem_map.get("active_frontier", {}).get("latest_result_id"), RESULT_ID)
    for exploration_id in EXPLORATION_IDS:
        record = exploration_by_id.get(exploration_id, {})
        audit.check("records", f"{exploration_id} exists", bool(record), exploration_id, "registered")
        audit.check("records", f"{exploration_id} cites R-152", LEDGER_ID in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), LEDGER_ID)

    for key in ("all_nonlinear_predictable_controls", "production_multi_root_aggregation", "t050_closed", "a13_closed", "sector_a_closed"):
        audit.check("scope", key, manifest["scope"].get(key) is False, manifest["scope"].get(key), False)
    audit.check("scope", "phase-neutral firewall", all(token in manifest["no_overclaim"] for token in ("select any phase", "validate or replace a PDE", "close Sector A")), manifest["no_overclaim"], "phase and PDE neutral")

    expected_total = len(audit.rows) + 1
    expected_integrator_only = expected_total - embedded_child_rows
    audit.check("aggregation", "manifest assertion counts", contract.get("integrated_assertions") == expected_total and contract.get("integrator_only_assertions") == expected_integrator_only, (contract.get("integrated_assertions"), contract.get("integrator_only_assertions")), (expected_total, expected_integrator_only))
    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "package_version": __version__,
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
        "exact_values": {
            "endpoint_loss_strict_upper": p["endpoint_loss_strict_upper"],
            "source_hessian": p["source_hessian"],
            "zero_current_gap_strict_lower": p["zero_current_affine_past_gap_strict_lower"],
            "retained_gap_strict_lower": p["retained_gap_strict_lower"],
            "conditional_operator_endpoint_threshold": p["conditional_operator_endpoint_threshold"],
            "multi_root_augmented_eigenvalues": p["multi_root_augmented_eigenvalues"],
        },
        "pdf": {"sha256": pdf_after, "pages": page_count, "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(options.output, payload)
    output_hash = sha256(options.output)[:12]
    catalog = load_json(REPO / "verification/catalog.json")
    catalog_record = next((entry for entry in catalog.get("entries", []) if entry.get("path") == relative(options.output)), None)
    catalog_hash = catalog_record.get("sha256_12") if catalog_record else None
    if catalog_hash != output_hash:
        print(f"FAIL: catalog hash is {catalog_hash}; generated result hash is {output_hash}; regenerate catalog and rerun")
        return 1
    print(f"{status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
