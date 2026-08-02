#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-144 evidence package.

This reruns the exact primary and non-importing independent certificates,
cross-checks all shared values, pins the canonical T-050 gate and predecessor
authorities, audits route records and negative results, rebuilds/renders the
PDF deterministically, and checks every governed public surface.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

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
    "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-"
    "LOW-COMPLETION-BOUNDARY"
)
LEDGER_ID = "R-144"
SCHEMA = (
    "tect/a13-uniform-douglas-one-use-projected-force-"
    "low-completion-boundary-integrated/1.0"
)
SLUG = "uniform-douglas-one-use-projected-force-low-completion-boundary"
NOTE = CLAIM_DIR / f"notes/classii-{SLUG}-260802-v1.0.tex.txt"
PDF = CLAIM_DIR / f"notes/classii-{SLUG}-260802-v1.0.pdf"
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
MANIFEST = CLAIM_DIR / (
    "classii_uniform_douglas_one_use_projected_force_"
    "low_completion_boundary_manifest.json"
)
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / (
    f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
)
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(593, 603))
NEGATIVE_IDS = (
    "NG-2026-08-02-A13-LOCAL-STENCIL-PRODUCTION-SIGN-NONIDENTIFIABILITY",
    "AUDIT-2026-08-02-A13-R144-SEXTIC-THRESHOLD-CORRECTION",
    "AUDIT-2026-08-02-A13-R144-FIBRE-SCHUR-COEFFICIENT-CORRECTION",
)
AUTHORITIES = {
    "A1": REPO / (
        "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
        "production_functional_manifest.json"
    ),
    "GATES": REPO / "claims/GATES.md",
    "R-093": CLAIM_DIR / (
        "classii_augmented_perspective_gibbs_gap_"
        "information_boundary_manifest.json"
    ),
    "R-104": CLAIM_DIR / (
        "classii_lossless_progressive_complete_owner_assembly_"
        "heat_boundary_manifest.json"
    ),
    "R-130": CLAIM_DIR / (
        "classii_terminal_xi_conormal_gram_balanced_low_"
        "response_boundary_manifest.json"
    ),
    "R-140": CLAIM_DIR / (
        "classii_predictable_triangular_mixed_gram_source_graph_"
        "feshbach_boundary_manifest.json"
    ),
    "R-141": CLAIM_DIR / (
        "classii_projected_force_global_doob_signed_gram_"
        "adaptive_collar_quotient_boundary_manifest.json"
    ),
    "R-142": CLAIM_DIR / (
        "classii_innovation_compressed_common_feature_su2_"
        "covariance_signed_collar_band_boundary_manifest.json"
    ),
    "R-143": CLAIM_DIR / (
        "classii_corrected_q567_feature_contraction_common_noise_"
        "anisotropy_tail_boundary_manifest.json"
    ),
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


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
    audit.check(
        "children", "primary exits zero", primary_run.returncode == 0,
        primary_run.returncode, 0,
    )
    audit.check(
        "children", "independent exits zero", independent_run.returncode == 0,
        independent_run.returncode, 0,
    )
    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    for name, child, expected_count in (
        ("primary", primary, 61),
        ("independent", independent, 56),
    ):
        rows = assertion_rows(child)
        audit.check(
            "children", f"{name} status", child.get("status") == "PASS",
            child.get("status"), "PASS",
        )
        audit.check(
            "children", f"{name} result", child.get("result_id") == RESULT_ID,
            child.get("result_id"), RESULT_ID,
        )
        audit.check(
            "children", f"{name} all pass",
            all(row.get("status") == "PASS" for row in rows),
            [row for row in rows if row.get("status") != "PASS"], [],
        )
        audit.check(
            "children", f"{name} frozen count",
            assertion_total(child) == expected_count,
            assertion_total(child), expected_count,
        )
        audit.check(
            "children", f"{name} count self-consistent",
            len(rows) == assertion_total(child), len(rows), assertion_total(child),
        )

    roots, relative_import = imported_roots(INDEPENDENT)
    audit.check(
        "independence", "no relative imports", not relative_import,
        relative_import, False,
    )
    forbidden = roots & {"numpy", "sympy", "scipy"}
    audit.check(
        "independence", "no numerical libraries", not forbidden,
        sorted(forbidden), [],
    )
    audit.check(
        "independence", "does not import primary",
        not any("a13_classii" in root for root in roots), sorted(roots),
        "no primary import",
    )

    primary_values = primary.get("exact_values", {})
    independent_values = independent.get("exact_values", {})
    audit.check(
        "cross", "exact-value keys agree",
        set(primary_values) == set(independent_values),
        sorted(set(primary_values) ^ set(independent_values)), [],
    )
    for key in sorted(primary_values):
        audit.check(
            "cross", f"{key} agrees",
            primary_values[key] == independent_values[key],
            (primary_values[key], independent_values[key]), "equal",
        )
    audit.check(
        "cross", "canonical source margin",
        primary_values.get("source_threshold_margin") == "1/220",
        primary_values.get("source_threshold_margin"), "1/220",
    )
    audit.check(
        "cross", "canonical sextic margin",
        primary_values.get("hessian_sextic_margin") == "3/25",
        primary_values.get("hessian_sextic_margin"), "3/25",
    )
    audit.check(
        "cross", "phase inertia boundary",
        primary_values.get("phase_cycle_inertia") == [[12, 0, 0], [8, 4, 0]],
        primary_values.get("phase_cycle_inertia"), [[12, 0, 0], [8, 4, 0]],
    )

    primary_false = (
        "production_chart_registered", "production_contraction_proved",
        "production_residual_bound_proved", "production_anchor_proved",
        "production_hessian_gap_proved", "t050_closed", "a13_gate_closed",
        "production_origin_force_bound_proved", "sector_a_closed",
    )
    independent_false = (
        "production_bound_proved", "production_origin_force_bound_proved",
        "t050_closed", "sector_a_closed",
    )
    for key in primary_false:
        audit.check(
            "scope", f"primary {key} false",
            primary["scope"].get(key) is False, primary["scope"].get(key), False,
        )
    for key in independent_false:
        audit.check(
            "scope", f"independent {key} false",
            independent["scope"].get(key) is False,
            independent["scope"].get(key), False,
        )

    note_text = NOTE.read_text(encoding="utf-8")
    note_tokens = (
        RESULT_ID, "Ledger: R-144", "theorem-2.1-affine-residual-douglas",
        "corollary-2.2-t050-sufficient-condition",
        "theorem-3.1-source-gap-boundary", "section-4-domain",
        "section-5-secant", "section-6-phase", "section-7-low",
        "section-8-jets", "section-9-decision", "section-10-roadmap",
        "Devil's-advocate review", "Result footer", "1\\over220",
        "3\\over25", NEGATIVE_IDS[1], NEGATIVE_IDS[2],
    )
    for token in note_tokens:
        audit.check("note", token, token in note_text, token in note_text, True)

    manifest = load_json(MANIFEST)
    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check(
        "pdf", "build exits zero", build.returncode == 0,
        (build.returncode, build.stderr), 0,
    )
    audit.check(
        "pdf", "form check", "FORM-CHECK: PASS" in build.stdout,
        build.stdout, "FORM-CHECK: PASS",
    )
    audit.check(
        "pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout,
        build.stdout, "OVERFULL-HBOX: 0",
    )
    rebuilt_pdf_hash = sha256(PDF)
    audit.check(
        "pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash,
        (initial_pdf_hash, rebuilt_pdf_hash), "equal",
    )
    reader = PdfReader(str(PDF))
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    expected_pages = int(manifest.get("verification", {}).get("pdf", {}).get("pages", -1))
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "manifest page count", len(reader.pages) == expected_pages, len(reader.pages), expected_pages)
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 20 for text in page_text), [len(text.strip()) for text in page_text], ">=20 each")
    audit.check("pdf", "ledger extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    audit.check("pdf", "scope extracts", "Sector A remain open" in extracted, "Sector A remain open" in extracted, True)
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security_findings = pdf_security(reader)
    audit.check("pdf", "no unsafe actions", security_findings == [], security_findings, [])
    with tempfile.TemporaryDirectory(prefix="tect-r144-render-") as temporary:
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
        "EXP-000593": "advanced", "EXP-000594": "advanced",
        "EXP-000595": "advanced", "EXP-000596": "advanced",
        "EXP-000597": "failed", "EXP-000598": "failed",
        "EXP-000599": "failed", "EXP-000600": "advanced",
        "EXP-000601": "advanced", "EXP-000602": "advanced",
    }
    for exploration_id in EXPLORATION_IDS:
        audit.check("exploration", f"{exploration_id} exists", exploration_id in exploration_records, exploration_id in exploration_records, True)
        record = exploration_records[exploration_id]
        audit.check("exploration", f"{exploration_id} verdict", record.get("verdict") == expected_verdicts[exploration_id], record.get("verdict"), expected_verdicts[exploration_id])
        audit.check("exploration", f"{exploration_id} evidence", len(record.get("evidence_refs", [])) >= 1, len(record.get("evidence_refs", [])), ">=1")
        audit.check("exploration", f"{exploration_id} next", bool(record.get("next_action")), record.get("next_action"), "nonempty")

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check("negative", negative_id, negative_id.lower() in registry.lower(), negative_id.lower() in registry.lower(), True)

    authority_hashes: dict[str, str] = {}
    for ledger_id, path in AUTHORITIES.items():
        audit.check("authority", f"{ledger_id} exists", path.is_file(), relative(path), "file")
        if path.suffix == ".json":
            authority = load_json(path)
            audit.check("authority", f"{ledger_id} identity", bool(authority.get("claim_id")), authority.get("claim_id"), "nonempty")
        authority_hashes[ledger_id] = sha256(path)
    gates = AUTHORITIES["GATES"].read_text(encoding="utf-8")
    heading = "### **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE**"
    gate_start = gates.index(heading)
    gate_tail = gates[gate_start:]
    gate_stop = gate_tail.find("\n### ", len(heading))
    gate_section = gate_tail if gate_stop < 0 else gate_tail[:gate_stop]
    audit.check("authority", "T-050 source threshold", "epsilon_v<1/(2p)" in gate_section, "epsilon_v<1/(2p)" in gate_section, True)
    audit.check("authority", "T-050 sextic threshold", "epsilon_6<gamma/6=0.27" in gate_section, "epsilon_6<gamma/6=0.27" in gate_section, True)

    audit.check("manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    audit.check("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    audit.check("manifest", "T-050 open", manifest.get("t050_closed") is False, manifest.get("t050_closed"), False)
    audit.check("manifest", "Sector A open", manifest.get("sector_a_closed") is False, manifest.get("sector_a_closed"), False)
    audit.check("manifest", "visual QA", str(manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa", "")).startswith("PASS"), manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa"), "PASS*")
    audit.check("manifest", "exploration ids", set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])), sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [])
    audit.check("manifest", "negative ids", set(NEGATIVE_IDS) <= set(manifest.get("negative_results", [])), sorted(set(NEGATIVE_IDS) - set(manifest.get("negative_results", []))), [])
    audit.check("manifest", "authority hashes", manifest.get("authority_hashes") == authority_hashes, manifest.get("authority_hashes"), authority_hashes)
    expected_files = {
        "primary": PRIMARY, "independent": INDEPENDENT,
        "verifier": Path(__file__), "note": NOTE, "pdf": PDF,
        "primary_result": args.primary_output,
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
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-144"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-144"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-144"),
        "changelog": (REPO / "CHANGELOG.md", "R-144"),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-144"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public.items():
        audit.check("surface", f"{name} file", path.is_file(), relative(path), "file")
        surface_text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in surface_text, token in surface_text, True)

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
        "schema": SCHEMA, "version": __version__, "issued": __version_issued__,
        "claim_id": CLAIM, "result_id": RESULT_ID, "tier": "T4",
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
            "conditional_affine_residual_theorem": True,
            "conditional_reduced_hessian_theorem": True,
            "production_chart": False, "production_contraction": False,
            "production_residual_bound": False, "production_anchor": False,
            "production_hessian_gap": False, "t050_closed": False,
            "a13_gate_closed": False, "nelson": False,
            "sector_a_closed": False,
        },
        "no_overclaim": (
            "Integrated PASS certifies the conditional R-144 theorems and exact "
            "information boundaries only.  It supplies no production chart or "
            "uniform production hypotheses and does not close T-050, A13, Nelson, "
            "or Sector A."
        ),
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
