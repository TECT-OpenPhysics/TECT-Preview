#!/usr/bin/env python3
"""Integrated verifier for the A13 R-165 sparse production annulus package."""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import re
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
RESULT_ID = "A13-CLASSII-SPARSE-PRODUCTION-OWNER-HARMONIC-COERCIVITY-COMPACT-ANNULUS-BOUNDARY"
LEDGER_ID = "R-165"
SLUG = "sparse-production-owner-harmonic-coercivity-compact-annulus-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_sparse_production_owner_harmonic_coercivity_compact_annulus_boundary_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_sparse_production_owner_harmonic_coercivity_compact_annulus_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_sparse_production_owner_harmonic_coercivity_compact_annulus_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-sparse-production-owner-harmonic-coercivity-compact-annulus-boundary-260804-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 38, "independent": 30}
EXPLORATION_IDS = ("EXP-000746", "EXP-000747", "EXP-000748")
EXACT_RATIONAL = re.compile(r"^[+-]?\d+(?:/[1-9]\d*)?$")


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": str(actual), "expected": str(expected)})


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
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


def canonical_exact(value: Any) -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return F(value)
    if isinstance(value, float):
        raise TypeError("floating diagnostic is forbidden")
    if isinstance(value, str):
        token = value.strip()
        return F(token) if EXACT_RATIONAL.fullmatch(token) else value
    if isinstance(value, list):
        return [canonical_exact(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonical_exact(item) for key, item in value.items()}
    raise TypeError(type(value).__name__)


def run_child(path: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(path), "--output", str(output)], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)


def imported_roots_and_floats(path: Path) -> tuple[set[str], bool, list[float]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    relative_import = False
    floats: list[float] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_import = relative_import or node.level > 0
            if node.module:
                roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Constant) and isinstance(node.value, float):
            floats.append(node.value)
    return roots, relative_import, floats


def find_poppler(name: str) -> Path | None:
    for root in (Path.home() / ".cache/codex-runtimes", Path("C:/Users/NaEun/.cache/codex-runtimes")):
        for candidate in root.glob(f"*/dependencies/native/poppler/Library/bin/{name}.exe"):
            if candidate.is_file():
                return candidate
    found = shutil.which(name)
    return Path(found) if found else None


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe = {"/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF", "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA", "/SubmitForm", "/ImportData", "/URI", "/GoToR"}

    def visit(value: Any, location: str, action_context: bool = False) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action = value.get("/S")
            if isinstance(action, IndirectObject):
                action = action.get_object()
            if action_context and action is not None and str(action) != "/GoTo":
                findings.append(f"{location}/S={action}")
            for key, child in value.items():
                if str(key) in unsafe:
                    findings.append(f"{location}{key}")
                visit(child, f"{location}{key}", action_context or str(key) in {"/A", "/AA", "/OpenAction", "/Next"})
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]", action_context)

    visit(reader.trailer["/Root"].get_object(), "/Root")
    return sorted(set(findings))


def open_action_ok(reader: PdfReader) -> bool:
    action = reader.trailer["/Root"].get_object().get("/OpenAction")
    if isinstance(action, IndirectObject):
        action = action.get_object()
    if isinstance(action, DictionaryObject):
        if str(action.get("/S")) != "/GoTo":
            return False
        action = action.get("/D")
        if isinstance(action, IndirectObject):
            action = action.get_object()
    if not isinstance(action, ArrayObject) or len(action) != 2:
        return False
    first = reader.pages[0].indirect_reference
    return isinstance(action[0], IndirectObject) and first is not None and action[0].idnum == first.idnum and str(action[1]) == "/Fit"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)
    audit.check("manifest", "identity", manifest.get("result_id") == RESULT_ID and manifest.get("result_ledger_id") == LEDGER_ID, [manifest.get("result_id"), manifest.get("result_ledger_id")], [RESULT_ID, LEDGER_ID])
    audit.check("manifest", "exploration IDs", manifest.get("exploration_ids") == list(EXPLORATION_IDS), manifest.get("exploration_ids"), list(EXPLORATION_IDS))
    audit.check("manifest", "child counts", [manifest["verification"].get("primary_assertions"), manifest["verification"].get("independent_assertions")] == [38, 30], [manifest["verification"].get("primary_assertions"), manifest["verification"].get("independent_assertions")], [38, 30])

    children: dict[str, dict[str, Any]] = {}
    embedded = 0
    temp_parent = REPO / "internal/tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r165-child-", dir=temp_parent) as temporary:
        for name, script, stored_path in (("primary", PRIMARY, PRIMARY_OUTPUT), ("independent", INDEPENDENT, INDEPENDENT_OUTPUT)):
            fresh_path = Path(temporary) / f"{name}.json"
            run = run_child(script, fresh_path)
            audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
            fresh = load_json(fresh_path)
            stored = load_json(stored_path)
            audit.check("children", f"{name} fresh equals stored", fresh == stored, sha256(fresh_path), sha256(stored_path))
            rows = fresh.get("assertions", [])
            audit.check("children", f"{name} schema", fresh.get("schema") == f"tect/a13-{SLUG}-{name}/1.0", fresh.get("schema"), f"tect/a13-{SLUG}-{name}/1.0")
            audit.check("children", f"{name} identity", fresh.get("result_id") == RESULT_ID and fresh.get("result_ledger_id") == LEDGER_ID, [fresh.get("result_id"), fresh.get("result_ledger_id")], [RESULT_ID, LEDGER_ID])
            audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
            audit.check("children", f"{name} summary", fresh.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, fresh.get("summary"), "all pass")
            identities = [(row.get("group"), row.get("name")) for row in rows]
            audit.check("children", f"{name} unique rows", len(identities) == len(set(identities)), len(identities), len(set(identities)))
            for row in rows:
                audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))
            children[name] = fresh
            embedded += len(rows)

    primary = children["primary"]
    independent = children["independent"]
    audit.check("scope", "scope parity", primary.get("scope") == independent.get("scope") == manifest.get("scope"), [primary.get("scope"), independent.get("scope")], manifest.get("scope"))
    audit.check("scope", "no-overclaim parity", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), [primary.get("no_overclaim"), independent.get("no_overclaim")], manifest.get("no_overclaim"))
    for token in ("p:2p", "21", "274", "annulus", "multi-root", "T-050", "phase", "PDE", "Sector A"):
        audit.check("scope", f"boundary {token}", token.lower() in manifest.get("no_overclaim", "").lower(), token, "present")

    roots, relative_import, floats = imported_roots_and_floats(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "standard library only", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "no scientific package")
    audit.check("independence", "no primary import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "none")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")
    audit.check("independence", "no float literals", floats == [], floats, [])

    shared_diagnostics = ("volume", "pi_squared_bracket", "mass_loewner_bounds", "covariance_bounds", "harmonic_constant", "harmonic_sharp_fixture", "r130_upper_constants", "past_derivative_covariance_upper", "polynomial_constants", "small_derivative_upper", "small_margin", "large_derivative", "large_second_derivative", "large_margin", "certified_amplitude_regions", "unresolved_open_annulus", "compact_certification_domain", "owner_floor", "rho")
    for name in shared_diagnostics:
        left = primary["diagnostics"].get(name)
        right = independent["diagnostics"].get(name)
        audit.check("parity", name, canonical_exact(left) == canonical_exact(right), left, right)
    constants = primary["diagnostics"]["polynomial_constants"]
    audit.check("oracle", "quartic positive", F(constants["A"]) > 0, constants["A"], ">0")
    audit.check("oracle", "open annulus exact", primary["diagnostics"]["unresolved_open_annulus"] == "21<G<274", primary["diagnostics"]["unresolved_open_annulus"], "21<G<274")
    audit.check("oracle", "compact closure exact", primary["diagnostics"]["compact_certification_domain"] == "21<=G<=274", primary["diagnostics"]["compact_certification_domain"], "21<=G<=274")

    artifact_paths = {"primary": PRIMARY, "independent": INDEPENDENT, "verifier": Path(__file__).resolve(), "note": NOTE, "pdf": PDF, "primary_result": PRIMARY_OUTPUT, "independent_result": INDEPENDENT_OUTPUT}
    for key, path in artifact_paths.items():
        record = manifest["files"][key]
        audit.check("artifacts", f"{key} path", record.get("path") == relative(path), record.get("path"), relative(path))
        audit.check("artifacts", f"{key} hash", record.get("sha256") == sha256(path), record.get("sha256"), sha256(path))
    for key, expected_hash in manifest["authority_hashes"].items():
        authority = REPO / manifest["authorities"][key]
        audit.check("authority-hashes", key, sha256(authority) == expected_hash, sha256(authority), expected_hash)

    note_text = NOTE.read_text(encoding="utf-8")
    note_flat = " ".join(note_text.split())
    for token in ("R-165", "5/6", "3125", "126241210368", "21<G<274", "10/11-1/110=9/10", "Devil's-advocate", "T-050", "No BCC", "phase or PDE"):
        audit.check("note", f"token {token}", token.lower() in note_flat.lower(), token, "present")
    audit.check("note", "no control characters", not any(ord(char) < 9 or 13 < ord(char) < 32 for char in note_text), "clean", "clean")

    pdf_contract = manifest["verification"]["pdf"]
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(pdf_contract["source_date_epoch"])
    environment["FORCE_SOURCE_DATE"] = "1"
    environment["PATH"] = str(Path(sys.executable).resolve().parent)
    build = subprocess.run([sys.executable, str(PDF_BUILDER), str(NOTE.relative_to(REPO))], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env=environment)
    pdf_after = sha256(PDF)
    audit.check("pdf", "builder exits zero", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    audit.check("pdf", "deterministic rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    findings = pdf_security(reader)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security", findings == [] and open_action_ok(reader), findings, [])
    audit.check("pdf", "page count", len(reader.pages) == pdf_contract["pages"], len(reader.pages), pdf_contract["pages"])
    audit.check("pdf", "size", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    for token in ("R-165", "5/6", "21 < G < 274", "T-050", "No BCC", "Sector A"):
        audit.check("pdf", f"text {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r165-render-", dir=temp_parent) as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", str(pdf_contract["render_dpi"]), str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered == len(reader.pages), rendered, len(reader.pages))
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    index_text = (CLAIM_DIR / "INDEX.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    todo = load_json(REPO / "todo/todo.json")
    changelog = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog_text = json.dumps(load_json(REPO / "verification/catalog.json"), sort_keys=True)
    explorations = {row["id"]: row for row in (json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())}
    audit.check("records", "ledger", '<a id="r-165"></a>' in results_text and RESULT_ID in results_text and "38/38" in results_text and "30/30" in results_text, LEDGER_ID, "registered")
    audit.check("records", "claim", RESULT_ID in claim_text and "21<G<274" in claim_text, RESULT_ID, "registered")
    audit.check("records", "lineage", "R-165" in lineage_text and "closed certification domain" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "index", RESULT_ID in index_text, RESULT_ID, "generated")
    audit.check("records", "status", relative(MANIFEST) in status.get("legacy_evidence", []) and "R-165" in status.get("statement", ""), relative(MANIFEST), "registered")
    audit.check("records", "status open T4", status.get("tier") == "T4" and status.get("proof_complete") is False and status.get("no_overclaim") == manifest.get("no_overclaim"), [status.get("tier"), status.get("proof_complete")], ["T4", False])
    audit.check("records", "TODO", any(row.get("id") == "T-050" and "R-165" in row.get("note", "") and "21<G<274" in row.get("note", "") for row in todo.get("tasks", [])), LEDGER_ID, "registered")
    audit.check("records", "changelog", any(LEDGER_ID in json.dumps(row, sort_keys=True) and RESULT_ID in json.dumps(row, sort_keys=True) for row in changelog), LEDGER_ID, "registered")
    audit.check("records", "theorem map", LEDGER_ID in json.dumps(theorem_map, sort_keys=True) and RESULT_ID in json.dumps(theorem_map, sort_keys=True), LEDGER_ID, "subproof")
    audit.check("records", "proof map", LEDGER_ID in proof_map and all(item in proof_map for item in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    # The integrated output is written only after this audit succeeds; cataloguing
    # that output is enforced by the subsequent full regeneration/release gate.
    package_paths = [relative(MANIFEST)] + [relative(path) for path in artifact_paths.values()]
    audit.check("records", "catalog", all(path in catalog_text for path in package_paths), package_paths, "catalogued")
    audit.check("records", "explorations", all(item in explorations for item in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(item in explorations for item in EXPLORATION_IDS):
        audit.check("records", "exploration verdicts", [explorations[item]["verdict"] for item in EXPLORATION_IDS] == ["advanced", "inconclusive", "advanced"], [explorations[item]["verdict"] for item in EXPLORATION_IDS], ["advanced", "inconclusive", "advanced"])

    failures = [row for row in audit.rows if row["status"] != "PASS"]
    if failures:
        raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
        "children": {"primary": {"path": relative(PRIMARY_OUTPUT), "sha256": sha256(PRIMARY_OUTPUT), "assertions": 38}, "independent": {"path": relative(INDEPENDENT_OUTPUT), "sha256": sha256(INDEPENDENT_OUTPUT), "assertions": 30}},
        "embedded_child_assertions": embedded,
        "integrator_only_assertions": len(audit.rows) - embedded,
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "pdf": {"sha256": pdf_after, "pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "rendered_pages": rendered, "security_findings": findings},
    }
    if arguments.self_test:
        stored = load_json(arguments.output)
        if stored != payload:
            raise AssertionError("stored integrated result differs from fresh self-test payload")
        print(f"{RESULT_ID} integrated self-test: {len(audit.rows)}/{len(audit.rows)} PASS")
        return 0
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded} child + {len(audit.rows)-embedded} integrator-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
