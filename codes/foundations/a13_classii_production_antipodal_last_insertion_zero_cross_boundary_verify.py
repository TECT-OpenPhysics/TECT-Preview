#!/usr/bin/env python3
"""Integrated verifier for the phase-neutral A13 R-150 evidence package."""

from __future__ import annotations

__version__ = "1.0.0"

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
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
RESULT_ID = "A13-CLASSII-PRODUCTION-ANTIPODAL-LAST-INSERTION-ZERO-CROSS-BOUNDARY"
LEDGER_ID = "R-150"
SLUG = "production-antipodal-last-insertion-zero-cross-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json"
PRIMARY = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/a13_classii_{SLUG.replace('-', '_')}_independent.py"
NOTE = CLAIM_DIR / "notes/classii-production-antipodal-last-insertion-zero-cross-boundary-260802-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"

# Verification metadata and exact hostile-fixture test oracles, never production
# inputs or fitted quantities.
EXPECTED_CHILD_COUNTS = {"primary": 34, "independent": 29}
EXPLORATION_IDS = tuple(f"EXP-{value:06d}" for value in range(640, 648))
NEGATIVE_IDS = (
    "AUDIT-2026-08-02-A13-R150-SCALAR-SLICE-AS-FULL-PRODUCTION-COVARIANCE",
    "AUDIT-2026-08-02-A13-R150-COINCIDENT-CROSS-AS-PROJECTED-CROSS",
    "AUDIT-2026-08-02-A13-R150-ABSOLUTE-ATOM-AS-RELATIVE-SECANT",
    "NG-2026-08-02-A13-R150-LAST-ROOT-POSITIVITY-TO-FUTURE-FEEDBACK",
)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self, group: str, name: str, condition: bool, actual: object, expected: object
    ) -> None:
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


def find_poppler(name: str) -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(
        f"*/dependencies/native/poppler/Library/bin/{name}.exe"
    ):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    audit = Audit()

    manifest = load_json(MANIFEST)
    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    children = {"primary": primary, "independent": independent}

    embedded_child_rows = 0
    for child_name, child in children.items():
        rows = child.get("assertions", [])
        expected_count = EXPECTED_CHILD_COUNTS[child_name]
        expected_schema = f"tect/a13-{SLUG}-{child_name}/1.0"
        audit.check("children", f"{child_name} schema", child.get("schema") == expected_schema, child.get("schema"), expected_schema)
        audit.check("children", f"{child_name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{child_name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{child_name} exact count", child.get("assertions_total") == len(rows) == expected_count, (child.get("assertions_total"), len(rows)), expected_count)
        audit.check("children", f"{child_name} every row passes", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        identities = [(row.get("group"), row.get("name")) for row in rows]
        audit.check("children", f"{child_name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
        for row in rows:
            embedded_child_rows += 1
            audit.check(
                f"child-{child_name}/{row.get('group')}",
                str(row.get("name")),
                row.get("status") == "PASS",
                row.get("actual"),
                row.get("expected"),
            )

    audit.check("children", "all child rows embedded exactly once", embedded_child_rows == sum(EXPECTED_CHILD_COUNTS.values()), embedded_child_rows, sum(EXPECTED_CHILD_COUNTS.values()))
    audit.check("children", "child scopes agree", primary.get("scope") == independent.get("scope") == manifest.get("scope"), (primary.get("scope"), independent.get("scope")), manifest.get("scope"))
    audit.check("children", "child no-overclaim agrees", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), (primary.get("no_overclaim"), independent.get("no_overclaim")), manifest.get("no_overclaim"))

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "independent does not import primary", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "no a13_classii import")
    audit.check("independence", "independent does not read primary artifact", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, [token for token in (PRIMARY.name, PRIMARY_OUTPUT.parent.name) if token in independent_text], [])

    # Independent exact aggregation checks.  They restate the theorem and the
    # three signed boundaries without importing either implementation.
    c11, c12, c22, p = sp.symbols("c11 c12 c22 p", real=True)
    gamma = sp.Matrix([[c11, c12], [c12, c22]])
    coefficient_cross = p * sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(2), -gamma),
        sp.Matrix.hstack(gamma, sp.zeros(2)),
    )
    audit.check("oracle", "coefficient cross is skew", coefficient_cross.T == -coefficient_cross, coefficient_cross.T, -coefficient_cross)
    audit.check("oracle", "coefficient cross is nonzero polynomial", coefficient_cross != sp.zeros(4), coefficient_cross, "nonzero")
    theta = sp.symbols("theta", real=True)
    local_cross = sp.simplify(2 * p * gamma * sp.sin(theta - theta))
    audit.check("oracle", "coincident cross vanishes", local_cross == sp.zeros(2), local_cross, sp.zeros(2))
    delta = sp.pi / 2
    remote_cross = sp.simplify(2 * p * gamma * sp.sin(delta))
    audit.check("oracle", "two-point cross survives", remote_cross == 2 * p * gamma, remote_cross, 2 * p * gamma)

    past_current, gram_mean = sp.symbols("v Bbar", real=True, nonnegative=True)
    absolute_atom = sp.Rational(1, 2) * past_current**2 * gram_mean
    audit.check("oracle", "absolute final atom nonnegative", absolute_atom.is_nonnegative is True, absolute_atom, ">=0")
    previous_atom = sp.Rational(1, 2) * 2**2
    final_atom = sp.Rational(1, 2) * 1**2
    audit.check("oracle", "relative secant counterfixture", final_atom - previous_atom == -sp.Rational(3, 2), final_atom - previous_atom, -sp.Rational(3, 2))
    audit.check("oracle", "projected-output opposite signs", independent["derived"]["projected_output_expectations"] == {"zero": "-1/2", "two": "1/2"}, independent["derived"]["projected_output_expectations"], {"zero": "-1/2", "two": "1/2"})
    audit.check("oracle", "future-feedback exact adverse owner", sp.sympify(independent["derived"]["earlier_future_feedback_unhalved_owner"]) == -sp.sqrt(6) / 8, independent["derived"]["earlier_future_feedback_unhalved_owner"], -sp.sqrt(6) / 8)
    audit.check("oracle", "zero atom suballocation", primary["derived"]["absolute_final_atom_budget_allocation"] == {"eta": 0, "zeta": 0}, primary["derived"]["absolute_final_atom_budget_allocation"], {"eta": 0, "zeta": 0})

    # Authority and artifact hash gates.
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

    # Deterministic PDF build, security, extraction, and renderer verification.
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = "1785628800"
    environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    pdf_after = sha256(PDF)
    audit.check("pdf", "builder exits zero", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "form check passes", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull boxes", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "deterministic hash rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    page_count = len(reader.pages)
    security_findings = pdf_security(reader)
    pdf_manifest = manifest.get("verification", {}).get("pdf", {})
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", security_findings == [], security_findings, [])
    audit.check("pdf", "page count pinned", page_count == pdf_manifest.get("pages"), page_count, pdf_manifest.get("pages"))
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_manifest.get("size_bytes"), PDF.stat().st_size, pdf_manifest.get("size_bytes"))
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    for token in (
        "Production antipodal last-insertion zero-cross boundary",
        "relative secant is still open",
        "future-feedback",
        "R-150",
        "Sector A",
    ):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler renderer available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r150-render-") as directory:
            target = Path(directory) / "page"
            render = subprocess.run(
                [str(renderer), "-png", "-r", "130", str(PDF), str(target)],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
            rendered_count = len(list(Path(directory).glob("page-*.png")))
            audit.check("pdf", "Poppler render exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_manifest.get("manual_visual_qa", "")).startswith("PASS"), pdf_manifest.get("manual_visual_qa"), "PASS...")

    # Public record, exploration, and scope firewalls.
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negatives_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status_card = load_json(CLAIM_DIR / "status.json")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    verification_contract = manifest.get("verification", {})
    integrated_count = verification_contract.get("integrated_assertions")
    integrator_count = verification_contract.get("integrator_only_assertions")
    count_token = f"{integrated_count}/{integrated_count}"
    r150_claim = claim_text[claim_text.find(RESULT_ID):] if RESULT_ID in claim_text else ""
    status_expected = str(status_card.get("reproduction", {}).get("expected", ""))
    status_notes = str(status_card.get("notes", ""))
    required_evidence = {
        relative(MANIFEST),
        "RESULTS-LEDGER.md#r-150",
        "explorations/log.jsonl#EXP-000640--EXP-000647",
    }
    required_evidence.update(record["path"] for record in manifest.get("files", {}).values())
    required_evidence.update(
        f"negative-results/registry.md#{negative_id.lower()}"
        for negative_id in NEGATIVE_IDS
    )
    missing_evidence = sorted(required_evidence - set(status_card.get("legacy_evidence", [])))
    exploration_lines = [
        json.loads(line)
        for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    exploration_by_id = {record["id"]: record for record in exploration_lines}
    audit.check("records", "R-150 ledger entry", '<a id="r-150"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "R-150 claim narrative and counts", RESULT_ID in claim_text and "EXP-000640--EXP-000647" in r150_claim and count_token in r150_claim and f"`{integrator_count}` integrator-only" in r150_claim, (RESULT_ID, count_token, integrator_count), "claim narrative, exploration range, and manifest-derived counts")
    audit.check("records", "status no-overclaim, notes, and evidence synchronized", status_card.get("no_overclaim") == manifest.get("no_overclaim") and f"integrated {count_token}" in status_notes and f"adds {integrator_count} " in status_notes and "six-page" in status_notes and not missing_evidence, (status_card.get("no_overclaim"), count_token, integrator_count, "six-page", missing_evidence), "manifest no-overclaim, metadata, and complete R-150 evidence set")
    audit.check("records", "status reproduction synchronized", status_card.get("reproduction", {}).get("command") == verification_contract.get("command") and f"with {count_token} PASS" in status_expected and f"adds {integrator_count} " in status_expected and "six-page" in status_expected, (status_card.get("reproduction", {}).get("command"), count_token, integrator_count, "six-page"), "manifest command and metadata")
    audit.check("records", "status remains T4 with T-050 gate open", status_card.get("tier") == "T4" and "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE" in status_card.get("open_gates", []), (status_card.get("tier"), status_card.get("open_gates")), "T4 and T-050 gate open")
    audit.check("records", "TODO routes to relative secant and feedback", all(token in todo_text for token in ("R-150", "relative final endpoint secant", "future-feedback")), "R-150 reduced target", "present")
    changelog_title = "production antipodal last-insertion zero-cross boundary"
    audit.check("records", "changelog contains R-150", "R-150" in changelog_text and changelog_title in changelog_text.lower(), changelog_title, "registered")
    for negative_id in NEGATIVE_IDS:
        audit.check("records", f"negative {negative_id}", negative_id in negatives_text, negative_id, "registered")
    for exploration_id in EXPLORATION_IDS:
        audit.check("records", f"exploration {exploration_id}", exploration_id in exploration_by_id, exploration_id, "registered")
        formal_results = exploration_by_id.get(exploration_id, {}).get(
            "formal_refs", {}
        ).get("results", [])
        audit.check("records", f"exploration {exploration_id} references R-150", LEDGER_ID in formal_results, formal_results, LEDGER_ID)

    scope = manifest["scope"]
    for key in (
        "relative_final_endpoint_secant_signed",
        "nonlocal_projected_owner_sign_proved",
        "earlier_root_future_feedback_connection_closed",
        "full_two_root_owner_closed",
        "historical_complete_low_closed",
        "balanced_response_closed",
        "global_source_sextic_windows_tested",
        "physical_phase_selected",
        "t050_closed",
        "a13_gate_closed",
        "nelson_proved",
        "sector_a_closed",
    ):
        audit.check("scope", key, scope.get(key) is False, scope.get(key), False)
    audit.check("scope", "phase-neutral no-overclaim", all(token in manifest["no_overclaim"] for token in ("BCC", "uniform state", "another phase", "PDE replacement")), manifest["no_overclaim"], "phase-neutral firewall")

    expected_total = len(audit.rows) + 1
    expected_integrator_only = expected_total - embedded_child_rows
    audit.check("aggregation", "manifest integrated and integrator-only assertion counts", verification_contract.get("integrated_assertions") == expected_total and verification_contract.get("integrator_only_assertions") == expected_integrator_only, (verification_contract.get("integrated_assertions"), verification_contract.get("integrator_only_assertions")), (expected_total, expected_integrator_only))
    status = "PASS" if all(row["status"] == "PASS" for row in audit.rows) else "FAIL"
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": status,
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions_failed": sum(row["status"] != "PASS" for row in audit.rows),
        "embedded_child_assertions": embedded_child_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_child_rows,
        "assertions": audit.rows,
        "exact_values": {
            "absolute_endpoint_oracle": str(absolute_atom),
            "relative_secant_fixture": str(final_atom - previous_atom),
            "future_feedback_fixture": independent["derived"]["earlier_future_feedback_unhalved_owner"],
        },
        "pdf": {
            "sha256": pdf_after,
            "pages": page_count,
            "size_bytes": PDF.stat().st_size,
            "rendered_pages": rendered_count,
            "security_findings": security_findings,
        },
        "scope": scope,
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(options.output, payload)
    print(f"{status}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
