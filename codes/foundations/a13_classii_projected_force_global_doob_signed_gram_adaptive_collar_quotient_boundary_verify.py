#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-141 evidence package.

The verifier reruns the primary and non-importing independent certificates,
embeds every child row once, cross-checks their load-bearing values, audits
authorities and public surfaces, and deterministically rebuilds, extracts,
security-checks, and Poppler-renders the proof PDF.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
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
    "A13-CLASSII-PROJECTED-FORCE-GLOBAL-DOOB-SIGNED-GRAM-"
    "ADAPTIVE-COLLAR-QUOTIENT-BOUNDARY"
)
LEDGER_ID = "R-141"
SCHEMA = (
    "tect/a13-projected-force-global-doob-signed-gram-adaptive-collar-"
    "quotient-boundary-integrated/1.0"
)
SLUG = "projected-force-global-doob-signed-gram-adaptive-collar-quotient-boundary"
NOTE = CLAIM_DIR / f"notes/classii-{SLUG}-260731-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
MANIFEST = CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_independent.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(568, 578))

AUTHORITIES = {
    "R-063": (
        "classii_balanced_coefficient_jet_continuum_manifest.json",
        "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-AND-A7-RECONSTRUCTION",
    ),
    "R-102": (
        "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
        "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY",
    ),
    "R-118": (
        "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
        "A13-CLASSII-REVISIT-QUOTIENT-OPERATOR-CARLESON-SIGNED-SCORE-BOUNDARY",
    ),
    "R-125": (
        "classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json",
        "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY",
    ),
    "R-126": (
        "classii_total_symbol_euler_low_injected_loewner_boundary_manifest.json",
        "A13-CLASSII-TOTAL-SYMBOL-EULER-LOW-INJECTED-LOEWNER-BOUNDARY",
    ),
    "R-127": (
        "classii_predictable_source_riesz_weighted_schur_low_margin_boundary_manifest.json",
        "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY",
    ),
    "R-128": (
        "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json",
        "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY",
    ),
    "R-129": (
        "classii_endpoint_trace_excess_shell_coanalysis_shifted_douglas_boundary_manifest.json",
        "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY",
    ),
    "R-130": (
        "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json",
        "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-RESPONSE-BOUNDARY",
    ),
    "R-131": (
        "classii_owner_complete_physical_response_mixed_gram_shell_boundary_manifest.json",
        "A13-CLASSII-OWNER-COMPLETE-PHYSICAL-RESPONSE-MIXED-GRAM-SHELL-BOUNDARY",
    ),
    "R-132": (
        "classii_mixed_replica_gaussian_ray_sextic_shell_boundary_manifest.json",
        "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY",
    ),
    "R-136": (
        "classii_common_heat_replica_raw_sequential_owner_boundary_manifest.json",
        "A13-CLASSII-COMMON-HEAT-REPLICA-RAW-SEQUENTIAL-OWNER-BOUNDARY",
    ),
    "R-139": (
        "classii_signed_future_endpoint_graph_complement_boundary_manifest.json",
        "A13-CLASSII-SIGNED-FUTURE-ENDPOINT-GRAPH-COMPLEMENT-BOUNDARY",
    ),
    "R-140": (
        "classii_predictable_triangular_mixed_gram_source_graph_feshbach_boundary_manifest.json",
        "A13-CLASSII-PREDICTABLE-TRIANGULAR-MIXED-GRAM-SOURCE-GRAPH-FESHBACH-BOUNDARY",
    ),
}


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("assertions")
    if isinstance(block, dict) and isinstance(block.get("rows"), list):
        return block["rows"]
    if isinstance(block, list):
        return block
    raise TypeError("child assertion rows unavailable")


def assertion_total(payload: dict[str, Any]) -> int:
    block = payload.get("assertions")
    if isinstance(block, dict) and "total" in block:
        return int(block["total"])
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


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [
        runtime
        / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe"))
    for candidate in candidates:
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
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), sorted(directory.glob("page-*.png"))


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_actions = {
        "/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData",
        "/Rendition", "/Movie", "/Sound", "/URI",
    }
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData",
    }

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
            action = resolve(value.get("/S"))
            if str(action) in unsafe_actions:
                findings.append(f"{path}/S={action}")
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
    for page_number, page in enumerate(reader.pages, start=1):
        for annotation_number, annotation in enumerate(resolve(page.get("/Annots")) or []):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widgets += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                annotations.append(f"page-{page_number}/annotation-{annotation_number}:{subtype}")
    return {
        "findings": sorted(set(findings + annotations)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widgets,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-output", type=Path, default=PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=INDEPENDENT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY, args.primary_output)
    independent_run = run_child(INDEPENDENT, args.independent_output)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, (primary_run.returncode, primary_run.stderr), 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, (independent_run.returncode, independent_run.stderr), 0)
    audit.check("children", "primary output exists", args.primary_output.is_file(), relative(args.primary_output), "file")
    audit.check("children", "independent output exists", args.independent_output.is_file(), relative(args.independent_output), "file")
    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    for name, child in (("primary", primary), ("independent", independent)):
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} result id", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        rows = assertion_rows(child)
        audit.check("children", f"{name} rows all pass", all(row.get("status") == "PASS" for row in rows), [row.get("name") for row in rows if row.get("status") != "PASS"], [])
        audit.check("children", f"{name} row count self-consistent", len(rows) == assertion_total(child), len(rows), assertion_total(child))

    independent_roots, independent_relative = imported_roots(INDEPENDENT)
    audit.check("independence", "independent has no relative import", not independent_relative, independent_relative, False)
    audit.check("independence", "independent avoids numerical libraries", not (independent_roots & {"numpy", "sympy", "scipy"}), sorted(independent_roots & {"numpy", "sympy", "scipy"}), [])
    audit.check("independence", "independent does not import primary", not any("a13_classii_projected_force" in root for root in independent_roots), sorted(independent_roots), "no primary")

    pcomp = primary["computed"]
    icomp = independent["computed"]
    for collar in (7, 8, 9, 10):
        p_debt = float(pcomp["collar_debts"][str(collar)])
        i_debt = float(icomp["collar_table"][str(collar)]["debt"])
        audit.check("cross", f"C{collar} debt agreement", abs(p_debt - i_debt) <= 2.0e-12, (p_debt, i_debt), "within 2e-12")
    audit.check("cross", "C8 threshold agreement", abs(float(pcomp["max_cstar_c8"]) - float(icomp["cstar8"])) <= 2.0e-12, (pcomp["max_cstar_c8"], icomp["cstar8"]), "within 2e-12")
    audit.check("cross", "C10 threshold agreement", abs(float(pcomp["max_cstar_c10"]) - float(icomp["cstar10"])) <= 2.0e-12, (pcomp["max_cstar_c10"], icomp["cstar10"]), "within 2e-12")
    audit.check("cross", "source margin agreement", pcomp["conditional_graph_margin_with_kernel"] == icomp["penalized_source_margin"], (pcomp["conditional_graph_margin_with_kernel"], icomp["penalized_source_margin"]), "equal")
    audit.check("cross", "action half agreement", pcomp["conditional_action_margin"] == icomp["action_margin"], (pcomp["conditional_action_margin"], icomp["action_margin"]), "equal")
    audit.check("cross", "adverse correlation sign", float(pcomp["production_correlation_determinants"]["adverse"]) < 0 and float(icomp["correlation_schur_determinants"]["adverse"]) < 0, (pcomp["production_correlation_determinants"]["adverse"], icomp["correlation_schur_determinants"]["adverse"]), "both negative")
    audit.check("cross", "favorable correlation sign", float(pcomp["production_correlation_determinants"]["favorable"]) > 0 and float(icomp["correlation_schur_determinants"]["favorable"]) > 0, (pcomp["production_correlation_determinants"]["favorable"], icomp["correlation_schur_determinants"]["favorable"]), "both positive")

    required_false_scope = (
        "production_two_sided_factorization",
        "production_low_compatibility",
        "a13_gate_closed",
        "nelson",
        "sector_a_closed",
    )
    for key in required_false_scope:
        audit.check("scope", f"primary {key} false", primary["scope"].get(key) is False, primary["scope"].get(key), False)
        audit.check("scope", f"independent {key} false", independent["scope"].get(key) is False, independent["scope"].get(key), False)

    note_text = NOTE.read_text(encoding="utf-8")
    for label, token in (
        ("result id", RESULT_ID),
        ("ledger id", "Ledger: R-141"),
        ("purpose section", "Purpose and scope"),
        ("canonical lift", "actual common covariance/trace factor"),
        ("signed Gram theorem", "theorem-4.1-two-sided-signed-mixed-gram"),
        ("source-null theorem", "theorem-6.1-source-null-quotient"),
        ("collar theorem", "theorem-7.1-positive-collar-shift"),
        ("devil audit", "Devil's-advocate audit"),
        ("stop boundary", "This checkpoint stops here"),
        ("no overclaim", "No-overclaim statement"),
    ):
        audit.check("note", label, token in note_text, token in note_text, True)

    first_build = build_pdf()
    audit.check("pdf", "first build exits zero", first_build.returncode == 0, (first_build.returncode, first_build.stderr), 0)
    audit.check("pdf", "first form check", "FORM-CHECK: PASS" in first_build.stdout, first_build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "first zero overfull", "OVERFULL-HBOX: 0" in first_build.stdout, first_build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "PDF exists after first build", PDF.is_file(), relative(PDF), "file")
    first_pdf_hash = sha256(PDF)
    second_build = build_pdf()
    audit.check("pdf", "second build exits zero", second_build.returncode == 0, (second_build.returncode, second_build.stderr), 0)
    audit.check("pdf", "second form check", "FORM-CHECK: PASS" in second_build.stdout, second_build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "second zero overfull", "OVERFULL-HBOX: 0" in second_build.stdout, second_build.stdout, "OVERFULL-HBOX: 0")
    second_pdf_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild", first_pdf_hash == second_pdf_hash, (first_pdf_hash, second_pdf_hash), "equal")

    reader = PdfReader(str(PDF))
    page_count = len(reader.pages)
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    compact = "".join(extracted.split())
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "at least six pages", page_count >= 6, page_count, ">=6")
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], ">=20 each")
    audit.check(
        "pdf",
        "no replacement glyph or literal spacing command",
        "\ufffd" not in extracted and "qquad" not in extracted,
        {"replacement_glyph": "\ufffd" in extracted, "literal_qquad": "qquad" in extracted},
        {"replacement_glyph": False, "literal_qquad": False},
    )
    audit.check("pdf", "result id extracts", RESULT_ID in compact, RESULT_ID in compact, True)
    audit.check("pdf", "ledger id extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    audit.check("pdf", "scope boundary extracts", "Sector-A closure" in extracted and "remain" in extracted, "scope tokens", "present")
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security = pdf_security_audit(reader)
    audit.check("pdf", "no unsafe actions", security["findings"] == [], security["findings"], [])
    audit.check("pdf", "safe open action", security["safe_open_action"] is True, security["open_action"], "safe")
    audit.check("pdf", "no widgets", security["widget_count"] == 0, security["widget_count"], 0)
    with tempfile.TemporaryDirectory(prefix="tect-r141-render-") as temporary:
        render_code, render_log, rendered = render_pdf(Path(temporary))
        audit.check("pdf", "Poppler render exits zero", render_code == 0, (render_code, render_log), 0)
        audit.check("pdf", "rendered page count", len(rendered) == page_count, len(rendered), page_count)
        audit.check("pdf", "rendered pages nonempty", all(path.stat().st_size > 0 for path in rendered), [path.stat().st_size for path in rendered], "positive each")
        rendered_hashes = [sha256(path) for path in rendered]

    exploration_records = [
        json.loads(line)
        for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exploration_by_id = {str(record.get("id")): record for record in exploration_records}
    for exploration_id in EXPLORATION_IDS:
        audit.check("exploration", f"{exploration_id} exists", exploration_id in exploration_by_id, exploration_id in exploration_by_id, True)
        if exploration_id in exploration_by_id:
            record = exploration_by_id[exploration_id]
            audit.check("exploration", f"{exploration_id} claim", CLAIM in record.get("claim_ids", []), record.get("claim_ids"), CLAIM)
            audit.check("exploration", f"{exploration_id} evidence", len(record.get("evidence_refs", [])) >= 2, len(record.get("evidence_refs", [])), ">=2")
            audit.check("exploration", f"{exploration_id} next action", bool(str(record.get("next_action", "")).strip()), record.get("next_action"), "nonempty")

    authority_hashes: dict[str, str] = {}
    for ledger_id, (filename, expected_result) in AUTHORITIES.items():
        path = CLAIM_DIR / filename
        audit.check("authority", f"{ledger_id} manifest exists", path.is_file(), relative(path), "file")
        authority = load_json(path)
        audit.check("authority", f"{ledger_id} result id", authority.get("result_id") == expected_result, authority.get("result_id"), expected_result)
        audit.check("authority", f"{ledger_id} claim id", authority.get("claim_id") == CLAIM, authority.get("claim_id"), CLAIM)
        authority_hashes[ledger_id] = sha256(path)

    audit.check("manifest", "manifest exists", MANIFEST.is_file(), relative(MANIFEST), "file")
    manifest = load_json(MANIFEST)
    audit.check("manifest", "schema", str(manifest.get("schema", "")).endswith("-manifest/1.0"), manifest.get("schema"), "*-manifest/1.0")
    audit.check("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger id", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    manual_visual_qa = str(manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa", ""))
    audit.check(
        "manifest",
        "proof incomplete and manual visual QA pinned",
        manifest.get("proof_complete") is False
        and manifest.get("sector_a_closed") is False
        and manual_visual_qa.startswith("PASS"),
        (manifest.get("proof_complete"), manifest.get("sector_a_closed"), manual_visual_qa),
        (False, False, "PASS*"),
    )
    audit.check("manifest", "exploration ids", set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])), sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [])
    normalized_authorities = {
        f"R-{str(key).lower().removeprefix('r').removeprefix('-')}"
        for key in list(manifest.get("authority_keys", [])) + list(manifest.get("authorities", {}).keys())
    }
    audit.check("manifest", "authority set", set(AUTHORITIES) <= normalized_authorities, sorted(set(AUTHORITIES) - normalized_authorities), [])
    expected_files = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": args.primary_output,
        "independent_result": args.independent_output,
    }
    manifest_files = manifest.get("files", {})
    for key, path in expected_files.items():
        entry = manifest_files.get(key, {})
        audit.check("manifest", f"{key} path", str(entry.get("path", "")).replace("\\", "/") == relative(path), entry.get("path"), relative(path))
        if entry.get("sha256"):
            audit.check("manifest", f"{key} hash", entry.get("sha256") == sha256(path), entry.get("sha256"), sha256(path))
    verification = manifest.get("verification", {})
    audit.check("manifest", "primary count", int(verification.get("primary_assertions", -1)) == assertion_total(primary), verification.get("primary_assertions"), assertion_total(primary))
    audit.check("manifest", "independent count", int(verification.get("independent_assertions", -1)) == assertion_total(independent), verification.get("independent_assertions"), assertion_total(independent))
    audit.check("manifest", "negative list empty", manifest.get("negative_results") == [], manifest.get("negative_results"), [])

    public_checks = {
        "result ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-141"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-141"),
        "lineage narrative": (CLAIM_DIR / "lineage-narrative.md", "R-141"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-141"),
        "changelog": (REPO / "CHANGELOG.md", "R-141"),
        "proof evidence map": (REPO / "theory/proof-evidence-map.md", "R-141"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public_checks.items():
        audit.check("surface", f"{name} file", path.is_file(), relative(path), "file")
        text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in text, token in text, True)

    child_rows: list[dict[str, object]] = []
    child_names: set[str] = set()
    duplicates: list[str] = []
    for child_name, child in (("primary", primary), ("independent", independent)):
        for row in assertion_rows(child):
            identity = f"{child_name}:{row.get('group')}::{row.get('name')}"
            if identity in child_names:
                duplicates.append(identity)
            child_names.add(identity)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('group')}",
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                }
            )
    audit.check("aggregation", "child identities unique", duplicates == [], duplicates, [])
    embedded_child_assertions = len(child_rows)
    expected_embedded = assertion_total(primary) + assertion_total(independent)
    expected_integrator_only = len(audit.rows) + 1
    expected_unique = embedded_child_assertions + expected_integrator_only
    accounting_actual = {
        "embedded_runtime": embedded_child_assertions,
        "embedded_manifest": int(verification.get("embedded_child_assertions", -1)),
        "integrator_only_manifest": int(verification.get("integrator_only_assertions", -1)),
        "integrated_manifest": int(verification.get("integrated_assertions", -1)),
        "unique_manifest": int(verification.get("unique_package_assertions", -1)),
    }
    accounting_expected = {
        "embedded_runtime": expected_embedded,
        "embedded_manifest": expected_embedded,
        "integrator_only_manifest": expected_integrator_only,
        "integrated_manifest": expected_unique,
        "unique_manifest": expected_unique,
    }
    audit.check(
        "aggregation",
        "child and manifest counts dynamic",
        accounting_actual == accounting_expected,
        accounting_actual,
        accounting_expected,
    )
    integrator_only_assertions = len(audit.rows)
    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)

    pdf_audit = {
        "path": relative(PDF),
        "sha256": second_pdf_hash,
        "size_bytes": PDF.stat().st_size,
        "pages": page_count,
        "deterministic_rebuild": True,
        "form_check": True,
        "overfull_hbox_count": 0,
        "all_pages_nonblank": True,
        "security_findings": security["findings"],
        "open_action": security["open_action"],
        "widget_count": security["widget_count"],
        "renderer": "Poppler pdftoppm",
        "dpi": 130,
        "rendered_pages": page_count,
        "page_sha256": rendered_hashes,
    }
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(all_rows),
            "passed": len(all_rows) - failed,
            "failed": failed,
            "rows": all_rows,
        },
        "assertion_accounting": {
            "embedded_child_assertions": embedded_child_assertions,
            "integrator_only_assertions": integrator_only_assertions,
            "unique_package_assertions": len(all_rows),
        },
        "children": {
            "primary": {
                "path": relative(args.primary_output),
                "sha256": sha256(args.primary_output),
                "assertions": assertion_total(primary),
                "stdout": primary_run.stdout,
            },
            "independent": {
                "path": relative(args.independent_output),
                "sha256": sha256(args.independent_output),
                "assertions": assertion_total(independent),
                "stdout": independent_run.stdout,
            },
        },
        "source_hashes": {
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "verifier": sha256(Path(__file__)),
        },
        "authority_hashes": authority_hashes,
        "manifest_sha256": sha256(MANIFEST),
        "pdf_audit": pdf_audit,
        "cross_computed": {
            "collar_debts": pcomp["collar_debts"],
            "cstar8": pcomp["max_cstar_c8"],
            "cstar10": pcomp["max_cstar_c10"],
            "penalized_source_margin": pcomp["conditional_graph_margin_with_kernel"],
            "action_margin": pcomp["conditional_action_margin"],
            "correlation_determinants": pcomp["production_correlation_determinants"],
        },
        "scope": {
            "finite_chart_projected_force": True,
            "canonical_complete_signature": True,
            "conditional_signed_gram": True,
            "global_doob_conjugation": True,
            "source_null_and_low_kernel_tests": True,
            "positive_analysis_collar_shift": True,
            "production_factorization": False,
            "production_uniform_loewner": False,
            "positive_graph_gap": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
    }
    atomic_json(args.output, payload)
    print(f"R-141 integrated {payload['status']}: {len(all_rows)-failed}/{len(all_rows)}")
    print(
        f"embedded_child_assertions={embedded_child_assertions}; "
        f"integrator_only_assertions={integrator_only_assertions}; "
        f"unique_package_assertions={len(all_rows)}"
    )
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
