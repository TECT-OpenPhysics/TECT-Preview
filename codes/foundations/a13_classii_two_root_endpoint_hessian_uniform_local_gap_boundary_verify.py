#!/usr/bin/env python3
"""Integrated verifier for the A13 R-151 two-root local-gap package."""

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
RESULT_ID = "A13-CLASSII-TWO-ROOT-ENDPOINT-HESSIAN-UNIFORM-LOCAL-GAP-BOUNDARY"
LEDGER_ID = "R-151"
SLUG = "two-root-endpoint-hessian-uniform-local-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
NOTE = CLAIM_DIR / "notes/classii-two-root-endpoint-hessian-uniform-local-gap-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 20, "independent": 19}
EXPLORATION_IDS = ("EXP-000657", "EXP-000658", "EXP-000659", "EXP-000660")
NEGATIVE_ID = "NG-2026-08-03-A13-INDEPENDENT-FOREST-BALANCED-OWNER-FABRICATION"


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


def find_poppler(name: str) -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(f"*/dependencies/native/poppler/Library/bin/{name}.exe"):
        if candidate.is_file():
            return candidate
    discovered = shutil.which(name)
    return Path(discovered) if discovered else None


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData",
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
    if not isinstance(action, ArrayObject) or len(action) != len(("page", "fit")):
        return False, "missing or non-destination OpenAction"
    page_reference = action[0]
    first_reference = reader.pages[0].indirect_reference
    same_page = (
        isinstance(page_reference, IndirectObject)
        and first_reference is not None
        and page_reference.idnum == first_reference.idnum
        and page_reference.generation == first_reference.generation
    )
    fit_mode = str(action[1])
    if same_page and fit_mode == "/Fit":
        return True, "first-page /Fit"
    return False, f"page_match={same_page}; mode={fit_mode}"


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


def multiply(left: list[F], right: list[F]) -> list[F]:
    result = [F(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            result[i + j] += first * second
    return result


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
    expected_embedded_child_rows = sum(EXPECTED_CHILD_COUNTS.values())
    audit.check(
        "children",
        "all child rows embedded once",
        embedded_child_rows == expected_embedded_child_rows,
        embedded_child_rows,
        expected_embedded_child_rows,
    )
    audit.check("children", "child scopes equal manifest", primary.get("scope") == independent.get("scope") == manifest.get("scope"), (primary.get("scope"), independent.get("scope")), manifest.get("scope"))
    audit.check("children", "child no-overclaim equals manifest", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), (primary.get("no_overclaim"), independent.get("no_overclaim")), manifest.get("no_overclaim"))

    roots, relative_import = imported_roots(INDEPENDENT)
    primary_text = PRIMARY.read_text(encoding="utf-8")
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no SymPy dependency", "sympy" not in roots, sorted(roots), "no sympy")
    audit.check("independence", "no primary import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "no a13_classii import")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    p_derived = primary["derived"]
    i_derived = independent["derived"]
    for key in (
        "mass_floor", "mass_floor_minors", "symbol_lower_discriminant",
        "hessian_constant_exact", "hessian_constant_upper",
        "sturm_zero_signs", "sturm_infinity_signs", "sturm_variations",
        "endpoint_hessian_loss_strict_upper", "source_hessian",
        "certified_augmented_local_gap_strict_lower", "first_variation_frequencies",
        "control_dimension",
    ):
        audit.check("parity", key, p_derived.get(key) == i_derived.get(key), p_derived.get(key), i_derived.get(key))
    audit.check("parity", "volume", F(p_derived["volume"]) == F(i_derived["volume"]), p_derived["volume"], i_derived["volume"])
    source_minus_endpoint = F(p_derived["source_hessian"]) - F(p_derived["endpoint_hessian_loss_strict_upper"])
    audit.check(
        "oracle",
        "source minus endpoint budget",
        source_minus_endpoint == F(p_derived["certified_augmented_local_gap_strict_lower"]),
        source_minus_endpoint,
        p_derived["certified_augmented_local_gap_strict_lower"],
    )
    audit.check(
        "oracle",
        "H6 strict upper",
        F(p_derived["hessian_constant_exact"]) < F(p_derived["hessian_constant_upper"]),
        p_derived["hessian_constant_exact"],
        f"<{p_derived['hessian_constant_upper']}",
    )
    parameters = load_json(REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json")["parameters"]
    complex_components = len(parameters["family_masses"])
    real_coordinates_per_complex = len(("real", "imaginary"))
    physical_real_dimension = complex_components * real_coordinates_per_complex
    taylor_half = F(1, len(("first", "second")))
    covariance_symmetrizations = len(("left", "adjoint"))
    current_symmetrizations = len(("left", "adjoint"))
    endpoint_polarizations = len(("forward", "reverse"))
    antipodal_multiplicity = len((-1, 1))
    earlier_frequency_multiplier = 1
    later_frequency_multiplier = 2
    mixed_norm_factor = (
        taylor_half
        * physical_real_dimension
        * covariance_symmetrizations
        * current_symmetrizations
        * endpoint_polarizations
    )
    cross_synthesis_norm_factor = endpoint_polarizations * physical_real_dimension
    owner_norm_factor = (
        mixed_norm_factor * earlier_frequency_multiplier * later_frequency_multiplier
        + cross_synthesis_norm_factor * (earlier_frequency_multiplier + later_frequency_multiplier) ** 2
    )
    antipodal_covariance_factor = antipodal_multiplicity**2
    covariance_normalized_factor = owner_norm_factor * antipodal_covariance_factor
    expected_factor_chain = {
        "mixed_norm_factor": F(mixed_norm_factor),
        "cross_synthesis_norm_factor": F(cross_synthesis_norm_factor),
        "owner_norm_factor": F(owner_norm_factor),
        "antipodal_covariance_factor": F(antipodal_covariance_factor),
        "covariance_normalized_factor": F(covariance_normalized_factor),
    }

    def normalized_factor_chain(derived: dict[str, Any]) -> dict[str, F]:
        return {key: F(str(derived[key])) for key in expected_factor_chain}

    audit.check(
        "oracle",
        "primary factor chain derived from dimensions",
        normalized_factor_chain(p_derived) == expected_factor_chain
        and "cross_synthesis_norm_factor = endpoint_polarizations * physical_real_dimension" in primary_text
        and "cross_synthesis_norm_factor = antipodal_multiplicity * physical_real_dimension" not in primary_text,
        normalized_factor_chain(p_derived),
        expected_factor_chain,
    )
    audit.check(
        "oracle",
        "independent factor chain derived from dimensions",
        normalized_factor_chain(i_derived) == expected_factor_chain
        and "cross_synthesis_norm_factor = endpoint_polarizations * physical_real_dimension" in independent_text
        and "cross_synthesis_norm_factor = antipodal_multiplicity * physical_real_dimension" not in independent_text,
        normalized_factor_chain(i_derived),
        expected_factor_chain,
    )
    audit.check("oracle", "Sturm root count", p_derived["sturm_variations"] == [2, 2], p_derived["sturm_variations"], [2, 2])
    z_value = F(str(parameters["Z"]))
    constant = F(str(parameters["r"])) + F(p_derived["mass_floor"])
    first = [constant, z_value, F(1)]
    later_frequency_square = later_frequency_multiplier**2
    second = [constant, later_frequency_square * z_value, F(later_frequency_square**2)]
    volume = F(str(parameters["Lx"])) * F(str(parameters["Ly"])) * F(str(parameters["Lz"]))
    polynomial = [F(p_derived["endpoint_hessian_loss_strict_upper"]) * volume * value for value in multiply(first, second)]
    polynomial[1] -= covariance_normalized_factor * F(p_derived["hessian_constant_upper"])
    expected_coefficients = [F(value) for value in i_derived["sturm_polynomial_coefficients_ascending"]]
    audit.check("oracle", "quartic reconstructed from A1", polynomial == expected_coefficients, polynomial, expected_coefficients)
    audit.check("oracle", "quartic constant positive", polynomial[0] > 0, polynomial[0], ">0")
    audit.check("oracle", "first variation has no zero frequency", 0 not in p_derived["first_variation_frequencies"], p_derived["first_variation_frequencies"], "no zero")

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
    form_check = "FORM-CHECK: PASS" in build.stdout
    overfull_check = "OVERFULL-HBOX: 0" in build.stdout
    audit.check("pdf", "form check", form_check, "present" if form_check else "absent", "present")
    audit.check("pdf", "zero overfull boxes", overfull_check, "present" if overfull_check else "absent", "present")
    audit.check("pdf", "deterministic rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    security_findings = pdf_security(reader)
    open_action_ok, open_action = open_action_summary(reader)
    page_count = len(reader.pages)
    pdf_manifest = manifest["verification"]["pdf"]
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check(
        "pdf",
        "security scan clear",
        security_findings == [] and open_action_ok,
        {"findings": security_findings, "open_action": open_action},
        {"findings": [], "open_action": "first-page /Fit"},
    )
    audit.check("pdf", "page count pinned", page_count == pdf_manifest.get("pages"), page_count, pdf_manifest.get("pages"))
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_manifest.get("size_bytes"), PDF.stat().st_size, pdf_manifest.get("size_bytes"))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    for token in ("Direct two-root endpoint Hessian", "R-151", "T-050 closed: false", "Sector A closed: false", "No phase ansatz"):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, "pdftoppm" if renderer is not None else "missing", "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r151-render-") as directory:
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
    integrator_count = contract["integrator_only_assertions"]
    required_evidence = {relative(MANIFEST), "RESULTS-LEDGER.md#r-151", f"negative-results/registry.md#{NEGATIVE_ID.lower()}", "explorations/log.jsonl#EXP-000657--EXP-000660"}
    required_evidence.update(record["path"] for record in manifest["files"].values())
    missing_evidence = sorted(required_evidence - set(status_card.get("legacy_evidence", [])))
    audit.check("records", "R-151 ledger entry", '<a id="r-151"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "R-151 claim narrative", RESULT_ID in claim_text and total_token in claim_text and "EXP-000657--EXP-000660" in claim_text, (RESULT_ID, total_token), "registered")
    audit.check("records", "R-151 lineage narrative", "R-151" in lineage_text and "uniform local" in lineage_text.lower(), "R-151", "registered")
    audit.check("records", "status synchronization", status_card.get("no_overclaim") == manifest.get("no_overclaim") and total_token in str(status_card.get("notes", "")) and not missing_evidence, (status_card.get("no_overclaim"), missing_evidence), "manifest and evidence synchronized")
    audit.check("records", "status reproduction", status_card.get("reproduction", {}).get("command") == contract.get("command") and total_token in str(status_card.get("reproduction", {}).get("expected", "")), status_card.get("reproduction"), contract.get("command"))
    audit.check("records", "status remains T4 and T-050 open", status_card.get("tier") == "T4" and "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE" in status_card.get("open_gates", []), (status_card.get("tier"), status_card.get("open_gates")), "T4 and T-050 open")
    audit.check("records", "TODO records R-151 boundary", all(token in todo_text for token in ("R-151", "nonzero strict-past", "T-054")), "R-151 route", "present")
    audit.check("records", "changelog records R-151", "R-151" in changelog_text and "two-root endpoint Hessian" in changelog_text, "R-151", "registered")
    audit.check("records", "negative route registered", NEGATIVE_ID in negatives_text, NEGATIVE_ID, "registered")
    audit.check("records", "theorem map frontier", theorem_map.get("active_frontier", {}).get("latest_result_id") == RESULT_ID, theorem_map.get("active_frontier", {}).get("latest_result_id"), RESULT_ID)
    for exploration_id in EXPLORATION_IDS:
        record = exploration_by_id.get(exploration_id, {})
        audit.check("records", f"{exploration_id} exists", bool(record), exploration_id, "registered")
        audit.check("records", f"{exploration_id} cites R-151", LEDGER_ID in record.get("formal_refs", {}).get("results", []), record.get("formal_refs", {}).get("results", []), LEDGER_ID)

    for key in ("nonlinear_feedback", "multi_root_aggregation", "historical_low_identified", "t050_closed", "sector_a_closed"):
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
            "mass_floor": p_derived["mass_floor"],
            "endpoint_hessian_loss_strict_upper": p_derived["endpoint_hessian_loss_strict_upper"],
            "source_hessian": p_derived["source_hessian"],
            "certified_augmented_local_gap_strict_lower": p_derived["certified_augmented_local_gap_strict_lower"],
            "control_dimension": p_derived["control_dimension"],
            "owner_norm_factor": p_derived["owner_norm_factor"],
            "covariance_normalized_factor": p_derived["covariance_normalized_factor"],
        },
        "pdf": {"sha256": pdf_after, "pages": page_count, "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": security_findings},
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
