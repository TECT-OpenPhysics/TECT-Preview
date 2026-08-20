#!/usr/bin/env python3
"""Integrated verifier for the A2/R-158 charge-ensemble theorem package."""

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
RESULT_ID = "A2-CHARGE-ENSEMBLE-FIRST-ORDER-SHELL-TRANSITION"
LEDGER_ID = "R-158"
SLUG = "charge-ensemble-first-order-shell-transition"
SCHEMA = f"tect/a2-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "charge_ensemble_first_order_shell_transition_manifest.json"
PRIMARY = REPO / "codes/foundations/a2_charge_ensemble_first_order_shell_transition.py"
INDEPENDENT = REPO / "codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py"
R157_VERIFY = REPO / "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py"
NOTE = CLAIM_DIR / "notes/a2-charge-ensemble-first-order-shell-transition-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 35, "independent": 24}
EXPLORATION_ID = "EXP-000686"


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
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    children: dict[str, dict[str, Any]] = {}
    embedded_rows = 0
    with tempfile.TemporaryDirectory(prefix="tect-r158-children-") as temporary:
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
    audit.check("independence", "no primary module import", "a2_charge_ensemble_first_order_shell_transition" not in roots, sorted(roots), "absent")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    key_pairs = (
        ("smallest_internal_eigenvalue_interval", "smallest_internal_eigenvalue_interval"),
        ("pi_interval", "pi_interval"),
        ("quadratic_ground_eigenvalue_interval", "quadratic_ground_eigenvalue_interval"),
        ("lattice_shell_norm_squared", "shell_norm_squared"),
        ("coexistence_density", "coexistence_density"),
        ("coexistence_charge", "coexistence_charge"),
        ("transition_chemical_potential_interval", "transition_chemical_potential_interval"),
        ("amplitude_saddle_node_chemical_potential_interval", "amplitude_saddle_node_chemical_potential_interval"),
        ("metastability_width", "metastability_width"),
    )
    for primary_key, independent_key in key_pairs:
        p_value = primary["derived"][primary_key]
        i_value = independent["derived"][independent_key]
        audit.check("parity", primary_key, p_value == i_value, p_value, i_value)

    rho_star = F(primary["derived"]["coexistence_density"])
    charge_star = F(primary["derived"]["coexistence_charge"])
    width = F(primary["derived"]["metastability_width"])
    saddle_drop = F(primary["derived"]["amplitude_saddle_node_drop"])
    lambda_lower, lambda_upper = map(F, primary["derived"]["quadratic_ground_eigenvalue_interval"])
    mu_lower, mu_upper = map(F, primary["derived"]["transition_chemical_potential_interval"])
    audit.check("oracle", "coexistence density exact", rho_star == F(43, 216), rho_star, F(43, 216))
    audit.check("oracle", "coexistence charge exact", charge_star == F(11008, 27), charge_star, F(11008, 27))
    audit.check("oracle", "coexistence width exact", width == F(1849, 86400), width, F(1849, 86400))
    audit.check("oracle", "amplitude saddle drop exact", saddle_drop == F(1849, 64800), saddle_drop, F(1849, 64800))
    audit.check("oracle", "transition precedes spinodal", mu_upper < lambda_lower and lambda_lower - mu_lower == width and lambda_upper - mu_upper == width, [mu_lower, mu_upper, lambda_lower, lambda_upper], "mu_t<lambda0 with exact width")
    audit.check("oracle", "neutral reference remains lower", mu_lower > 0 and charge_star > 0, mu_lower * charge_star, ">0")

    with tempfile.TemporaryDirectory(prefix="tect-r158-r157-") as temporary:
        old_output = Path(temporary) / "r157.json"
        old = subprocess.run([sys.executable, str(R157_VERIFY), "--output", str(old_output)], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    audit.check("regression", "R-157 verifier exits zero", old.returncode == 0, old.returncode, 0)
    audit.check("regression", "R-157 and legacy A2 retained", "integrated:" in old.stdout and "legacy A2 61/61 PASS" in old.stdout, old.stdout, "R-157 integrated and legacy A2 61/61")

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
        "exact identity", "11008", "1849", "first-order", "fixed-charge",
        "physical-vacuum", "common-phase winding", "gauge-invariant density",
        "R-157 is not contradicted", "Devil's-advocate", "Result footer",
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
    for token in ("R-158", "first-order", "fixed-charge", "physical-vacuum", "common-phase winding"):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r158-render-") as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == len(reader.pages), rendered_count, len(reader.pages))
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
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
    audit.check("records", "R-158 ledger entry", '<a id="r-158"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "common-phase winding" in claim_text.lower(), RESULT_ID, "registered with boundary")
    audit.check("records", "status synchronized", "R-158" in status.get("statement", "") and "physical conserved charge" in status.get("notes", ""), status.get("notes"), "R-158 with provenance boundary")
    t054 = todo_lookup.get("T-054", {})
    t054_current = (
        t054.get("status") == "in_progress"
        and t054.get("gate") == "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
        and "T-054" in str(t054.get("note", ""))
        and "Pre-A" in str(t054.get("note", ""))
    )
    audit.check("records", "T-054 current Round-1 scope", t054_current, t054, "in_progress on PA-ROUND1 evidence-role gate")
    audit.check("records", "changelog entry", "R-158" in changelog_text and "charge-ensemble" in changelog_text.lower(), LEDGER_ID, "registered")
    theorem_map_text = json.dumps(theorem_map, sort_keys=True)
    audit.check("records", "current theorem-map boundary", "R-157" in theorem_map_text and "R-170" in theorem_map_text, theorem_map_text, "current R-157/R-170 boundary retained")
    audit.check("records", "proof map", "R-158" in proof_map and EXPLORATION_ID in proof_map, [LEDGER_ID, EXPLORATION_ID], "registered")
    audit.check("records", "catalog manifest", relative(MANIFEST) in json.dumps(catalog, sort_keys=True), relative(MANIFEST), "registered")
    audit.check("records", "exploration record", EXPLORATION_ID in exploration_lookup, EXPLORATION_ID, "registered")
    if EXPLORATION_ID in exploration_lookup:
        record = exploration_lookup[EXPLORATION_ID]
        audit.check("records", "exploration verdict", record.get("verdict") == "advanced" and LEDGER_ID in record.get("formal_refs", {}).get("results", []), record.get("verdict"), "advanced with R-158")

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
        "r157_and_legacy_a2_regression": "PASS",
        "embedded_child_assertions": embedded_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_rows,
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "pdf": {"sha256": pdf_after, "pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only); R-157/A2 regression PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
