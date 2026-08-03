#!/usr/bin/env python3
"""Integrated verifier for the A13 R-159 uniform-neighbourhood package."""

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
RESULT_ID = "A13-CLASSII-PURE-DYADIC-REGULATOR-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-159"
SLUG = "pure-dyadic-regulator-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_pure_dyadic_regulator_uniform_neighborhood_gap_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-pure-dyadic-regulator-uniform-neighborhood-gap-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 34, "independent": 31}
EXPLORATION_IDS = ("EXP-000689", "EXP-000690", "EXP-000691")
EXPECTED_INDEPENDENT_SCOPE = {
    "uniform_in_cutoff_regulator_and_retained_p": True,
    "multiplier_bound_abs_le_one": True,
    "fixed_floor": True,
    "exact_continuum_torus_integration": True,
    "centered_single_p_2p_4p_chart": True,
    "existential_radius_only": True,
    "uses_covariance_inverse": False,
    "raw_derivative_covariance_compact": False,
    "t050_closed": False,
    "sector_a_closed": False,
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


def normalize_exact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_exact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_exact(item) for item in value]
    try:
        return str(F(str(value)))
    except (ValueError, ZeroDivisionError):
        return value


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
    for candidate in runtime.glob(
        f"*/dependencies/native/poppler/Library/bin/{name}.exe"
    ):
        if candidate.is_file():
            return candidate
    found = shutil.which(name)
    return Path(found) if found else None


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe = {
        "/JS",
        "/JavaScript",
        "/AA",
        "/Launch",
        "/AF",
        "/EF",
        "/EmbeddedFiles",
        "/RichMedia",
        "/Movie",
        "/Sound",
        "/XFA",
        "/SubmitForm",
        "/ImportData",
        "/URI",
        "/GoToR",
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
    for name, path, output in (
        ("primary", PRIMARY, PRIMARY_OUTPUT),
        ("independent", INDEPENDENT, INDEPENDENT_OUTPUT),
    ):
        run = run_child(path)
        audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
        child = load_json(output)
        children[name] = child
        rows = child.get("assertions", [])
        audit.check(
            "children",
            f"{name} schema",
            child.get("schema") == f"tect/a13-{SLUG}-{name}/1.0",
            child.get("schema"),
            f"tect/a13-{SLUG}-{name}/1.0",
        )
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} ledger", child.get("result_ledger_id") == LEDGER_ID, child.get("result_ledger_id"), LEDGER_ID)
        audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
        audit.check("children", f"{name} summary", child.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, child.get("summary"), "all pass")
        identities = [(row.get("group"), row.get("name")) for row in rows]
        audit.check("children", f"{name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
        for row in rows:
            audit.check(
                f"child-{name}/{row.get('group')}",
                str(row.get("name")),
                row.get("status") == "PASS",
                row.get("actual"),
                row.get("expected"),
            )
        embedded_rows += len(rows)

    primary = children["primary"]
    independent = children["independent"]
    audit.check("scope", "primary scope equals manifest", primary.get("scope") == manifest.get("scope"), primary.get("scope"), manifest.get("scope"))
    audit.check("scope", "independent scope pinned", independent.get("scope") == EXPECTED_INDEPENDENT_SCOPE, independent.get("scope"), EXPECTED_INDEPENDENT_SCOPE)
    audit.check("scope", "manifest no-overclaim equals primary", manifest.get("no_overclaim") == primary.get("no_overclaim"), manifest.get("no_overclaim"), primary.get("no_overclaim"))
    independent_no = str(independent.get("no_overclaim", ""))
    for token in ("existential", "raw-Q", "finite-grid alias", "T-050", "Sector-A"):
        audit.check("scope", f"independent boundary token {token}", token.lower() in independent_no.lower(), token, "present")

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "none")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    p = primary["diagnostics"]
    i = independent["diagnostics"]
    for name in (
        "symbol_discriminant",
        "uniform_symbol_minimum",
        "origin_gap",
        "target_gap",
        "uniform_modulus_allowance",
        "retained_gap",
    ):
        audit.check("parity", name, normalize_exact(p[name]) == normalize_exact(i[name]), normalize_exact(p[name]), normalize_exact(i[name]))
    independent_degree = dict(i["degree_audit"])
    independent_degree["gaussian_sixth_moment"] = independent_degree.pop("sixth")
    expected_degree = {**independent_degree, "value_synthesis": 2}
    audit.check("parity", "degree audit", p["degree_audit"] == expected_degree, p["degree_audit"], expected_degree)
    audit.check("oracle", "origin gap exact", F(p["origin_gap"]) == F(147, 1000), p["origin_gap"], "147/1000")
    audit.check("oracle", "target exact", F(p["target_gap"]) == F(1, 10), p["target_gap"], "1/10")
    audit.check("oracle", "allowance exact", F(p["uniform_modulus_allowance"]) == F(47, 2000), p["uniform_modulus_allowance"], "47/2000")
    audit.check("oracle", "retained gap exact", F(p["retained_gap"]) == F(247, 2000), p["retained_gap"], "247/2000")
    audit.check("oracle", "retained gap above target", F(p["retained_gap"]) > F(p["target_gap"]), p["retained_gap"], ">1/10")
    audit.check("oracle", "all-state Gaussian residual zero", p["gaussian_ibp_residual"] == "0", p["gaussian_ibp_residual"], "0")
    audit.check("oracle", "Q0 cancellation residual zero", p["covariance_normal_residual"] == "0", p["covariance_normal_residual"], "0")
    audit.check("oracle", "value tail vanishes", p["compactified_value_tail"] == "0", p["compactified_value_tail"], "0")
    audit.check("oracle", "derivative tail vanishes", p["compactified_derivative_tail"] == "0", p["compactified_derivative_tail"], "0")

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
        "all-state Gaussian identity",
        "Q-Q_0",
        "all covariance jets",
        "exact continuum torus",
        "source-Gram",
        "forward",
        "legal reverse",
        "balanced",
        "47\\over2000",
        "247\\over2000",
        "Devil's-advocate",
        "T-050",
        "PDE",
        "Result footer",
    ):
        audit.check("note", f"scope token {token}", token.lower() in note_text.lower(), token, "present")

    pdf_contract = manifest["verification"]["pdf"]
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(pdf_contract["source_date_epoch"])
    environment["FORCE_SOURCE_DATE"] = "1"
    # The shared builder prefers a host pdflatex when it is visible on PATH.
    # Pin this certificate to the venv-local Tectonic engine so that an
    # escalated Windows shell and a restricted sandbox produce identical PDFs.
    environment["PATH"] = str(Path(sys.executable).resolve().parent)
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
    for token in ("R-159", "uniform", "Q0", "T-050", "PDE"):
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    compact_lines = " ".join(extracted.split())
    audit.check("pdf", "text contains 47 over 2000", "47 2000" in compact_lines, "47/2000", "present as extracted numerator/denominator")
    audit.check("pdf", "text contains 247 over 2000", "247 2000" in compact_lines, "247/2000", "present as extracted numerator/denominator")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r159-render-") as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == len(reader.pages), rendered_count, len(reader.pages))
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog = load_json(REPO / "verification/catalog.json")
    explorations = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_lookup = {row["id"]: row for row in explorations}
    audit.check("records", "R-159 ledger entry", '<a id="r-159"></a>' in results_text, LEDGER_ID, "registered")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "247/2000" in claim_text, RESULT_ID, "registered")
    status_evidence = status.get("legacy_evidence", [])
    audit.check("records", "status historical registration", relative(MANIFEST) in status_evidence, relative(MANIFEST), "registered without mutable top-statement coupling")
    audit.check("records", "TODO route", "R-159" in todo_text and "T-050" in todo_text and "T-054" in todo_text, "R-159/T-050/T-054", "registered")
    audit.check("records", "changelog entry", "R-159" in changelog_text and "uniform neighbourhood" in changelog_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "theorem map latest result", theorem_map.get("active_frontier", {}).get("latest_result_id") == RESULT_ID, theorem_map.get("active_frontier", {}).get("latest_result_id"), RESULT_ID)
    audit.check("records", "proof map", "R-159" in proof_map and all(identifier in proof_map for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    audit.check("records", "catalog manifest", relative(MANIFEST) in json.dumps(catalog, sort_keys=True), relative(MANIFEST), "registered")
    audit.check("records", "exploration records", all(identifier in exploration_lookup for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(identifier in exploration_lookup for identifier in EXPLORATION_IDS):
        verdicts = [exploration_lookup[x]["verdict"] for x in EXPLORATION_IDS]
        expected_verdicts = ["advanced", "failed", "advanced"]
        audit.check("records", "exploration verdicts", verdicts == expected_verdicts, verdicts, expected_verdicts)

    projected_integrator_only = len(audit.rows) - embedded_rows + 3
    projected_total = len(audit.rows) + 3
    verification = manifest["verification"]
    audit.check("aggregation", "embedded child count pinned", embedded_rows == verification["embedded_child_assertions"], embedded_rows, verification["embedded_child_assertions"])
    audit.check("aggregation", "integrator-only count pinned", projected_integrator_only == verification["integrator_only_assertions"], projected_integrator_only, verification["integrator_only_assertions"])
    audit.check("aggregation", "integrated count pinned", projected_total == verification["integrated_assertions"], projected_total, verification["integrated_assertions"])

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
        "embedded_child_assertions": embedded_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_rows,
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "pdf": {"sha256": pdf_after, "pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
