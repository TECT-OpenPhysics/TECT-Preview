#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-143 evidence package.

This reruns two non-importing certificates, checks the corrected coherence
geometry and the finite-feature/Feshbach/tail claims, audits authorities and
proof-route records, deterministically rebuilds and renders the PDF, and
requires every governed public surface to expose the same scoped result.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
import ast
from fractions import Fraction
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
RESULT_ID = (
    "A13-CLASSII-CORRECTED-Q567-FEATURE-CONTRACTION-COMMON-NOISE-"
    "ANISOTROPY-TAIL-BOUNDARY"
)
LEDGER_ID = "R-143"
SCHEMA = (
    "tect/a13-corrected-q567-feature-contraction-common-noise-"
    "anisotropy-tail-boundary-integrated/1.0"
)
SLUG = "corrected-q567-feature-contraction-common-noise-anisotropy-tail-boundary"
NOTE = CLAIM_DIR / f"notes/classii-{SLUG}-260802-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
MANIFEST = (
    CLAIM_DIR
    / "classii_corrected_q567_feature_contraction_common_noise_anisotropy_tail_boundary_manifest.json"
)
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = (
    REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
)
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(585, 593))
AUDIT_ID = "AUDIT-2026-08-02-A13-R142-Q567-PHYSICAL-OUTPUT-FACTOR-TWO"
AUTHORITIES = {
    "A1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "R-125": CLAIM_DIR / "classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json",
    "R-130": CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json",
    "R-140": CLAIM_DIR / "classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-142": CLAIM_DIR / "classii_innovation_compressed_common_feature_su2_covariance_signed_collar_band_boundary_manifest.json",
}

# Clearly labelled regression oracles, never production inputs.
TEST_ORACLES = {
    "old_output": 4_229_940,
    "new_gaps": [5, 6, 7],
    "old_gaps": [6, 7, 8],
    "rho_fail_squared": 1.125,
    "mixed_fail_min": -0.125,
    "thresholds": [27, 49],
    "safe_delta_sum": 0.221,
    "safe_delta_square_sum": 0.033805,
    "tail_27": 4.100062011735117e-8,
    "tail_49": 5.640592303064587e-10,
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions", {})
    rows = assertions.get("rows") if isinstance(assertions, dict) else assertions
    if not isinstance(rows, list):
        raise TypeError("child assertion rows unavailable")
    return rows


def assertion_total(payload: dict[str, Any]) -> int:
    assertions = payload.get("assertions", {})
    if isinstance(assertions, dict) and "total" in assertions:
        return int(assertions["total"])
    return len(assertion_rows(payload))


def run_child(script: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
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


def build_pdf() -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785628800"
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


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(
        "*/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ):
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def render_pdf(directory: Path) -> tuple[int, str, list[Path]]:
    renderer = find_pdftoppm()
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    run = subprocess.run(
        [str(renderer), "-png", "-r", "130", str(PDF), str(directory / "page")],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return (
        run.returncode,
        "\n".join((run.stdout, run.stderr)).strip(),
        sorted(directory.glob("page-*.png")),
    )


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData",
    }
    unsafe_actions = {
        "/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData",
        "/Rendition", "/Movie", "/Sound", "/URI",
    }

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, location: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action = resolve(value.get("/S"))
            if str(action) in unsafe_actions:
                findings.append(f"{location}/S={action}")
            for key, child in value.items():
                if str(key) in unsafe_keys:
                    findings.append(f"{location}{key}")
                visit(child, f"{location}{key}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]")

    visit(resolve(reader.trailer["/Root"]), "/Root")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-output", type=Path, default=PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=INDEPENDENT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY, args.primary_output)
    independent_run = run_child(INDEPENDENT, args.independent_output)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    for name, child, expected_count in (
        ("primary", primary, 52),
        ("independent", independent, 40),
    ):
        rows = assertion_rows(child)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} all pass", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        audit.check("children", f"{name} count", assertion_total(child) == expected_count, assertion_total(child), expected_count)
        audit.check("children", f"{name} count self-consistent", len(rows) == assertion_total(child), len(rows), assertion_total(child))

    roots, relative_import = imported_roots(INDEPENDENT)
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no numerical libraries", not (roots & {"numpy", "sympy", "scipy"}), sorted(roots & {"numpy", "sympy", "scipy"}), [])
    audit.check("independence", "does not import primary", not any("a13_classii" in root for root in roots), sorted(roots), "no primary")

    p = primary["diagnostics"]
    i = independent["computed"]
    audit.check("cross", "corrected gaps agree", p["corrected_q567"]["gaps"] == i["corrected_q567"]["gaps"] == TEST_ORACLES["new_gaps"], (p["corrected_q567"]["gaps"], i["corrected_q567"]["gaps"]), TEST_ORACLES["new_gaps"])
    audit.check("cross", "old gaps agree", p["superseded_r142_fixture"]["gaps"] == i["superseded_r142"]["gaps"] == TEST_ORACLES["old_gaps"], (p["superseded_r142_fixture"]["gaps"], i["superseded_r142"]["gaps"]), TEST_ORACLES["old_gaps"])
    audit.check("cross", "old physical output factor", p["superseded_r142_fixture"]["physical_output"] == i["superseded_r142"]["physical_output"] == TEST_ORACLES["old_output"], (p["superseded_r142_fixture"]["physical_output"], i["superseded_r142"]["physical_output"]), TEST_ORACLES["old_output"])
    audit.check("cross", "production coefficients P", p["production_coefficients"]["P"] == i["coefficients"]["P"], (p["production_coefficients"]["P"], i["coefficients"]["P"]), "equal")
    audit.check("cross", "production coefficient c0", p["production_coefficients"]["c0"] == i["coefficients"]["c0"], (p["production_coefficients"]["c0"], i["coefficients"]["c0"]), "equal")
    audit.check("cross", "production coefficient c1", p["production_coefficients"]["c1"] == i["coefficients"]["c1"], (p["production_coefficients"]["c1"], i["coefficients"]["c1"]), "equal")
    audit.check("cross", "alpha", p["production_coefficients"]["alpha"] == i["coefficients"]["alpha"], (p["production_coefficients"]["alpha"], i["coefficients"]["alpha"]), "equal")
    audit.check("cross", "mixed failure edge", abs(float(p["douglas"]["mixed_fail_eigenvalues"][0]) - TEST_ORACLES["mixed_fail_min"]) < 1e-14 and i["douglas"]["fail_eigenvalues"][0] == "-1/8", (p["douglas"]["mixed_fail_eigenvalues"][0], i["douglas"]["fail_eigenvalues"][0]), "-1/8")
    audit.check("cross", "rho failure edge", abs(float(p["douglas"]["rho_fail_squared"]) - TEST_ORACLES["rho_fail_squared"]) < 1e-14 and i["douglas"]["rho_fail_squared"] == "9/8", (p["douglas"]["rho_fail_squared"], i["douglas"]["rho_fail_squared"]), "9/8")
    audit.check("cross", "Feshbach block", abs(float(p["feshbach"]["effective_block"]) - float(Fraction(i["feshbach"]["effective"]))) < 1e-14, (p["feshbach"]["effective_block"], i["feshbach"]["effective"]), "equal")
    audit.check("cross", "mass spectra", max(abs(float(x) - float(y)) for x, y in zip(p["covariance"]["mass_eigenvalues"], i["covariance"]["mass_eigenvalues"])) < 2e-12, (p["covariance"]["mass_eigenvalues"], i["covariance"]["mass_eigenvalues"]), "within 2e-12")
    audit.check("cross", "safe delta sum", abs(float(i["covariance"]["safe_delta_sum"]) - TEST_ORACLES["safe_delta_sum"]) < 1e-15 and p["covariance"]["safe_delta_sum"] == "221/1000", (p["covariance"]["safe_delta_sum"], i["covariance"]["safe_delta_sum"]), TEST_ORACLES["safe_delta_sum"])
    audit.check("cross", "safe squared spread", abs(float(i["covariance"]["safe_delta_square_sum"]) - TEST_ORACLES["safe_delta_square_sum"]) < 1e-15 and p["covariance"]["safe_delta_square_sum"] == "6761/200000", (p["covariance"]["safe_delta_square_sum"], i["covariance"]["safe_delta_square_sum"]), TEST_ORACLES["safe_delta_square_sum"])
    audit.check("cross", "thresholds", [p["covariance"]["diagnostic_thresholds"]["large_first_N"], p["covariance"]["diagnostic_thresholds"]["small_first_N"]] == i["tails"]["thresholds"] == TEST_ORACLES["thresholds"], (p["covariance"]["diagnostic_thresholds"], i["tails"]["thresholds"]), TEST_ORACLES["thresholds"])
    audit.check("cross", "tail N27", abs(float(p["covariance"]["tail_table"]["27"]["synchronous_probe_squared_upper"]) - TEST_ORACLES["tail_27"]) < 1e-20 and abs(float(i["tails"]["N27"][1]) - TEST_ORACLES["tail_27"]) < 1e-20, (p["covariance"]["tail_table"]["27"]["synchronous_probe_squared_upper"], i["tails"]["N27"][1]), TEST_ORACLES["tail_27"])
    audit.check("cross", "tail N49", abs(float(p["covariance"]["tail_table"]["49"]["synchronous_probe_squared_upper"]) - TEST_ORACLES["tail_49"]) < 1e-21 and abs(float(i["tails"]["N49"][1]) - TEST_ORACLES["tail_49"]) < 1e-21, (p["covariance"]["tail_table"]["49"]["synchronous_probe_squared_upper"], i["tails"]["N49"][1]), TEST_ORACLES["tail_49"])

    for key in (
        "production_owner_matrix_assembled", "production_feature_contraction_proved",
        "production_adverse_direction_proved", "owner_preserving_su2_intertwiner_proved",
        "a13_gate_closed", "sector_a_closed",
    ):
        audit.check("scope", f"primary {key} false", primary["scope"].get(key) is False, primary["scope"].get(key), False)
    for key in (
        "production_matrix_assembled", "a13_gate_closed", "sector_a_closed",
    ):
        audit.check("scope", f"independent {key} false", independent["scope"].get(key) is False, independent["scope"].get(key), False)

    note_text = NOTE.read_text(encoding="utf-8")
    for label, token in (
        ("result", RESULT_ID), ("ledger", "Ledger: R-143"),
        ("audit", "section-2-audit"), ("sign", "section-3-sign"),
        ("feature", "section-4-feature"), ("Douglas", "section-5-douglas"),
        ("Feshbach", "section-6-feshbach"), ("covariance", "section-7-covariance"),
        ("tail", "section-8-tail"), ("production", "section-9-production"),
        ("PDE", "section-10-pde"), ("map", "section-11-map"),
        ("review", "Devil's-advocate review"), ("footer", "Result footer"),
    ):
        audit.check("note", label, token in note_text, token in note_text, True)

    manifest = load_json(MANIFEST)
    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check("pdf", "build exits zero", build.returncode == 0, (build.returncode, build.stderr), 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    rebuilt_pdf_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash, (initial_pdf_hash, rebuilt_pdf_hash), "equal")
    reader = PdfReader(str(PDF))
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "nine pages", len(reader.pages) == 9, len(reader.pages), 9)
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 20 for text in page_text), [len(text.strip()) for text in page_text], ">=20 each")
    audit.check("pdf", "ledger extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    audit.check("pdf", "scope extracts", "Sector-A closure" in extracted, "Sector-A closure" in extracted, True)
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security_findings = pdf_security(reader)
    audit.check("pdf", "no unsafe actions", security_findings == [], security_findings, [])
    with tempfile.TemporaryDirectory(prefix="tect-r143-render-") as temporary:
        render_code, render_log, rendered = render_pdf(Path(temporary))
        audit.check("pdf", "Poppler exits zero", render_code == 0, (render_code, render_log), 0)
        audit.check("pdf", "all pages rendered", len(rendered) == len(reader.pages), len(rendered), len(reader.pages))
        audit.check("pdf", "rendered pages nonempty", all(path.stat().st_size > 0 for path in rendered), [path.stat().st_size for path in rendered], "positive")
        rendered_hashes = [sha256(path) for path in rendered]

    exploration_records = {
        record["id"]: record
        for record in (
            json.loads(line)
            for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    expected_verdicts = {
        "EXP-000585": "failed", "EXP-000586": "advanced",
        "EXP-000587": "advanced", "EXP-000588": "advanced",
        "EXP-000589": "advanced", "EXP-000590": "failed",
        "EXP-000591": "inconclusive", "EXP-000592": "inconclusive",
    }
    for exploration_id in EXPLORATION_IDS:
        audit.check("exploration", f"{exploration_id} exists", exploration_id in exploration_records, exploration_id in exploration_records, True)
        record = exploration_records[exploration_id]
        audit.check("exploration", f"{exploration_id} verdict", record.get("verdict") == expected_verdicts[exploration_id], record.get("verdict"), expected_verdicts[exploration_id])
        audit.check("exploration", f"{exploration_id} evidence", len(record.get("evidence_refs", [])) >= 2, len(record.get("evidence_refs", [])), ">=2")
        audit.check("exploration", f"{exploration_id} next", bool(record.get("next_action")), record.get("next_action"), "nonempty")

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    audit.check("negative", "R142 audit registered", AUDIT_ID.lower() in registry.lower(), AUDIT_ID.lower() in registry.lower(), True)
    audit.check("negative", "factor-two finding", "4229940" in registry and "2114970" in registry, ("4229940" in registry, "2114970" in registry), (True, True))

    authority_hashes: dict[str, str] = {}
    for ledger_id, path in AUTHORITIES.items():
        audit.check("authority", f"{ledger_id} exists", path.is_file(), relative(path), "file")
        authority = load_json(path)
        audit.check("authority", f"{ledger_id} claim", bool(authority.get("claim_id")), authority.get("claim_id"), "nonempty")
        authority_hashes[ledger_id] = sha256(path)

    audit.check("manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    audit.check("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    audit.check("manifest", "Sector A open", manifest.get("sector_a_closed") is False, manifest.get("sector_a_closed"), False)
    audit.check("manifest", "visual QA", str(manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa", "")).startswith("PASS"), manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa"), "PASS*")
    audit.check("manifest", "exploration ids", set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])), sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [])
    audit.check("manifest", "audit id", AUDIT_ID in manifest.get("negative_results", []), manifest.get("negative_results"), AUDIT_ID)
    audit.check("manifest", "authority hashes", manifest.get("authority_hashes") == authority_hashes, manifest.get("authority_hashes"), authority_hashes)
    expected_files = {
        "primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__),
        "note": NOTE, "pdf": PDF, "primary_result": args.primary_output,
        "independent_result": args.independent_output,
    }
    for key, path in expected_files.items():
        entry = manifest.get("files", {}).get(key, {})
        audit.check("manifest", f"{key} path", str(entry.get("path", "")).replace("\\", "/") == relative(path), entry.get("path"), relative(path))
        audit.check("manifest", f"{key} hash", entry.get("sha256") == sha256(path), entry.get("sha256"), sha256(path))
    verification = manifest.get("verification", {})
    audit.check("manifest", "primary count", int(verification.get("primary_assertions", -1)) == assertion_total(primary), verification.get("primary_assertions"), assertion_total(primary))
    audit.check("manifest", "independent count", int(verification.get("independent_assertions", -1)) == assertion_total(independent), verification.get("independent_assertions"), assertion_total(independent))
    audit.check("manifest", "PDF hash", manifest["files"]["pdf"]["sha256"] == rebuilt_pdf_hash, manifest["files"]["pdf"]["sha256"], rebuilt_pdf_hash)

    public = {
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-143"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-143"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-143"),
        "changelog": (REPO / "CHANGELOG.md", "R-143"),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-143"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public.items():
        audit.check("surface", f"{name} file", path.is_file(), relative(path), "file")
        text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in text, token in text, True)

    child_rows: list[dict[str, object]] = []
    identities: set[str] = set()
    duplicates: list[str] = []
    for child_name, child in (("primary", primary), ("independent", independent)):
        for row in assertion_rows(child):
            identity = f"{child_name}:{row.get('group')}::{row.get('name')}"
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('group')}",
                    "name": row.get("name"), "status": row.get("status"),
                    "actual": row.get("actual"), "expected": row.get("expected"),
                }
            )
    audit.check("aggregation", "child identities unique", duplicates == [], duplicates, [])
    integrator_only = len(audit.rows)
    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)
    payload: dict[str, object] = {
        "schema": SCHEMA, "version": __version__, "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(all_rows), "passed": len(all_rows) - failed,
            "failed": failed, "rows": all_rows,
        },
        "assertion_accounting": {
            "embedded_child_assertions": len(child_rows),
            "integrator_only_assertions": integrator_only,
            "unique_package_assertions": len(all_rows),
        },
        "children": {
            "primary": {"path": relative(args.primary_output), "sha256": sha256(args.primary_output), "assertions": assertion_total(primary), "stdout": primary_run.stdout},
            "independent": {"path": relative(args.independent_output), "sha256": sha256(args.independent_output), "assertions": assertion_total(independent), "stdout": independent_run.stdout},
        },
        "source_hashes": {
            "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT),
            "verifier": sha256(Path(__file__)), "note": sha256(NOTE),
            "pdf": rebuilt_pdf_hash, "manifest": sha256(MANIFEST),
            "authorities": authority_hashes,
        },
        "pdf_audit": {
            "path": relative(PDF), "sha256": rebuilt_pdf_hash,
            "size_bytes": PDF.stat().st_size, "pages": len(reader.pages),
            "deterministic_rebuild": True, "form_check": True,
            "overfull_hbox_count": 0, "security_findings": security_findings,
            "renderer": "Poppler pdftoppm", "dpi": 130,
            "rendered_pages": len(rendered_hashes), "page_sha256": rendered_hashes,
            "manual_visual_qa": manifest["verification"]["pdf"]["manual_visual_qa"],
        },
        "scope": {
            "production_matrix": False, "production_contraction": False,
            "production_adverse_direction": False, "owner_intertwiner": False,
            "a13_gate_closed": False, "nelson": False, "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(
        f"{RESULT_ID}: {'PASS' if failed == 0 else 'FAIL'} "
        f"({len(all_rows) - failed}/{len(all_rows)}; "
        f"children={len(child_rows)}, integrator={integrator_only})"
    )
    print(f"output: {args.output}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
