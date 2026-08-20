#!/usr/bin/env python3
"""Integrated verifier for the A2/R-157 pinned-functional theorem package."""

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
CLAIM = "A2-FULL-PRODUCTION-WELLPOSED"
CLAIM_DIR = REPO / "claims" / CLAIM
RESULT_ID = "A2-PINNED-FUNCTIONAL-UNIQUE-ZERO-GLOBAL-MINIMIZER"
LEDGER_ID = "R-157"
SLUG = "pinned-functional-unique-zero-global-minimizer"
SCHEMA = f"tect/a2-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "pinned_functional_unique_zero_global_minimizer_manifest.json"
PRIMARY = REPO / "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py"
INDEPENDENT = REPO / "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py"
OLD_A2_VERIFY = REPO / "codes/foundations/a2_full_production_verify.py"
NOTE = CLAIM_DIR / "notes/a2-pinned-functional-unique-zero-global-minimizer-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 26, "independent": 24}
EXPLORATION_IDS = ("EXP-000681", "EXP-000682", "EXP-000683", "EXP-000684")
NEGATIVE_ID = "NG-2026-08-03-M1-PINNED-FUNCTIONAL-NONZERO-EQUILIBRIUM"


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        })


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


def current_round1_task_scope(todo_lookup: dict[str, dict[str, Any]]) -> tuple[bool, bool]:
    """Read the rolling T-054/T-050 state without requiring retired prose."""
    t054 = todo_lookup.get("T-054", {})
    t050 = todo_lookup.get("T-050", {})
    t054_note = str(t054.get("note", ""))
    t050_note = str(t050.get("note", ""))
    t054_current = (
        t054.get("status") == "in_progress"
        and t054.get("gate") == "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
        and "T-054" in t054_note
        and "Pre-A" in t054_note
    )
    t050_parked = (
        t050.get("status") == "backlog"
        and t050.get("gate") == "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"
        and "A13" in t050_note
        and "parked" in t050_note.lower()
        and "complete finite production cylinder" in t050_note
    )
    return t054_current, t050_parked


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


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
    unsafe = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData", "/URI", "/GoToR",
    }

    def visit(value: Any, location: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            for key, child in value.items():
                if str(key) in unsafe:
                    findings.append(f"{location}{key}")
                visit(child, f"{location}{key}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]")

    visit(reader.trailer["/Root"], "/Root")
    return sorted(set(findings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    children: dict[str, dict[str, Any]] = {}
    embedded_rows = 0
    with tempfile.TemporaryDirectory(prefix="tect-r157-children-") as temporary:
        temporary_root = Path(temporary)
        for name, script, tracked in (
            ("primary", PRIMARY, PRIMARY_OUTPUT),
            ("independent", INDEPENDENT, INDEPENDENT_OUTPUT),
        ):
            output = temporary_root / f"{name}.json"
            run = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
            audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
            child = load_json(output)
            children[name] = child
            rows = child.get("assertions", [])
            expected_schema = f"tect/a2-{SLUG}-{name}/1.0"
            audit.check("children", f"{name} schema", child.get("schema") == expected_schema, child.get("schema"), expected_schema)
            audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
            audit.check("children", f"{name} ledger", child.get("result_ledger_id") == LEDGER_ID, child.get("result_ledger_id"), LEDGER_ID)
            audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
            audit.check("children", f"{name} summary", child.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, child.get("summary"), "all pass")
            identities = [(row.get("group"), row.get("name")) for row in rows]
            audit.check("children", f"{name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
            audit.check("children", f"{name} tracked result reproducible", child == load_json(tracked), sha256(output), sha256(tracked))
            for row in rows:
                audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))
            embedded_rows += len(rows)

    primary = children["primary"]
    independent = children["independent"]
    audit.check("scope", "primary scope equals manifest", primary.get("scope") == manifest.get("scope"), primary.get("scope"), manifest.get("scope"))
    audit.check("scope", "independent scope equals manifest", independent.get("scope") == manifest.get("scope"), independent.get("scope"), manifest.get("scope"))
    audit.check("scope", "no-overclaim synchronized", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), "child/manifest", "equal")

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", "a2_pinned_functional_unique_zero_global_minimizer" not in roots, sorted(roots), "absent")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    exact_keys = (
        ("shell_minimum", "shell_minimum"),
        ("internal_mass_lower_bound", "internal_lower"),
        ("total_quadratic_mass_lower_bound", "total_mass"),
        ("potential_completion_vertex", "rho_star"),
        ("strict_l2_gap", "strict_l2_gap"),
        ("strict_radial_derivative_gap", "strict_radial_derivative_gap"),
        ("classii_determinant", "classii_determinant"),
    )
    for primary_key, independent_key in exact_keys:
        p_value = primary["derived"][primary_key]
        i_value = independent["derived"][independent_key]
        audit.check("parity", primary_key, F(p_value) == F(i_value), p_value, i_value)
    gap = F(primary["derived"]["strict_l2_gap"])
    radial_gap = F(primary["derived"]["strict_radial_derivative_gap"])
    audit.check("oracle", "strict L2 gap exact", gap == F(719818750025582338837, 5400000000000000000000) and gap > F(1, 8), gap, "exact and >1/8")
    audit.check("oracle", "strict radial gap exact", radial_gap == F(2101675000076747016511, 8100000000000000000000) and radial_gap > F(1, 4), radial_gap, "exact and >1/4")
    audit.check("oracle", "radial determinant polynomial exact", independent["derived"]["classii_radial_determinant_coefficients"] == [
        "112500000000000000000/16000000000008000000000001",
        "112500000000000000000/16000000000008000000000001",
        "-71191406250000000000/16000000000008000000000001",
    ], independent["derived"]["classii_radial_determinant_coefficients"], "pinned exact coefficients")

    old = subprocess.run([sys.executable, str(OLD_A2_VERIFY)], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    audit.check("regression", "existing A2 verifier exits zero", old.returncode == 0, old.returncode, 0)
    audit.check("regression", "existing A2 61 assertions retained", "ASSERTS: 61/61" in old.stdout and "A2-FULL-PRODUCTION-VERIFY-PASS" in old.stdout, old.stdout, "61/61 and PASS")

    artifacts = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in artifacts.items():
        record = manifest["files"][key]
        audit.check("artifacts", f"{key} path", record.get("path") == relative(path), record.get("path"), relative(path))
        audit.check("artifacts", f"{key} hash", record.get("sha256") == sha256(path), record.get("sha256"), sha256(path))
    for key, expected_hash in manifest["authority_hashes"].items():
        authority = REPO / manifest["authorities"][key]
        audit.check("authority-hashes", key, sha256(authority) == expected_hash, sha256(authority), expected_hash)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in (
        "unique global minimizer", "unique critical point", "719818750025582338837",
        "2101675000076747016511", "componentwise", "exponential", "T-052",
        "A7", "physical-vacuum", "fixed norm", "Result footer",
    ):
        audit.check("note", f"scope token {token}", token.lower() in note_text.lower(), token, "present")

    pdf_contract = manifest["verification"]["pdf"]
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(pdf_contract["source_date_epoch"])
    environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        env=environment,
    )
    pdf_after = sha256(PDF)
    audit.check("pdf", "builder exits zero", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull boxes", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "deterministic rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    findings = pdf_security(reader)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [], findings, [])
    audit.check("pdf", "page count pinned", len(reader.pages) == pdf_contract["pages"], len(reader.pages), pdf_contract["pages"])
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    for token in ("R-157", "unique critical point", "global minimizer", "T-052", "A7", "physical vacuum"):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r157-render-") as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == len(reader.pages), rendered_count, len(reader.pages))
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    todo = load_json(REPO / "todo/todo.json")
    todo_lookup = {row["id"]: row for row in todo["tasks"]}
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog = load_json(REPO / "verification/catalog.json")
    explorations = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_lookup = {row["id"]: row for row in explorations}
    audit.check("records", "R-157 ledger entry", '<a id="r-157"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "negative registered", NEGATIVE_ID in negative_text, NEGATIVE_ID, "registered")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "exponential" in claim_text.lower(), RESULT_ID, "registered")
    audit.check("records", "status synchronized", status.get("no_overclaim") == manifest.get("no_overclaim") and "R-157" in status.get("statement", ""), status.get("no_overclaim"), manifest.get("no_overclaim"))
    audit.check("records", "T-052 analytically superseded", todo_lookup["T-052"]["status"] == "done" and "R-157" in todo_lookup["T-052"]["note"], todo_lookup["T-052"], "done by R-157")
    t054_current, t050_parked = current_round1_task_scope(todo_lookup)
    audit.check("records", "T-054 current Round-1 scope", t054_current, todo_lookup.get("T-054"), "in_progress on PA-ROUND1 evidence-role gate")
    audit.check("records", "T-050 parked complete-cylinder boundary", t050_parked, todo_lookup.get("T-050"), "backlog A13 with complete finite production-cylinder reopen condition")
    audit.check("records", "changelog entry", "R-157" in changelog_text and "unique-zero" in changelog_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "theorem map", "R-157" in json.dumps(theorem_map, sort_keys=True), LEDGER_ID, "registered")
    audit.check("records", "proof map", "R-157" in proof_map and all(identifier in proof_map for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    audit.check("records", "catalog manifest", relative(MANIFEST) in json.dumps(catalog, sort_keys=True), relative(MANIFEST), "registered")
    audit.check("records", "exploration records", all(identifier in exploration_lookup for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(identifier in exploration_lookup for identifier in EXPLORATION_IDS):
        audit.check("records", "exploration verdicts", [exploration_lookup[x]["verdict"] for x in EXPLORATION_IDS] == ["parked", "inconclusive", "failed", "parked"], [exploration_lookup[x]["verdict"] for x in EXPLORATION_IDS], ["parked", "inconclusive", "failed", "parked"])

    failures = [row for row in audit.rows if row["status"] != "PASS"]
    if failures:
        raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
        "children": {
            "primary": {"path": relative(PRIMARY_OUTPUT), "sha256": sha256(PRIMARY_OUTPUT), "assertions": EXPECTED_CHILD_COUNTS["primary"]},
            "independent": {"path": relative(INDEPENDENT_OUTPUT), "sha256": sha256(INDEPENDENT_OUTPUT), "assertions": EXPECTED_CHILD_COUNTS["independent"]},
        },
        "legacy_a2_regression_assertions": 61,
        "embedded_child_assertions": embedded_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_rows,
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "pdf": {"sha256": pdf_after, "pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
    }
    atomic_json(args.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only); legacy A2 61/61 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
