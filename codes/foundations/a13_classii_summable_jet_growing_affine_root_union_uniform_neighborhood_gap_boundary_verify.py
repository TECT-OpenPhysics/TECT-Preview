#!/usr/bin/env python3
"""Integrated verifier for the A13 R-161 summable-jet package."""

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
RESULT_ID = "A13-CLASSII-SUMMABLE-JET-GROWING-AFFINE-ROOT-UNION-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-161"
SLUG = "summable-jet-growing-affine-root-union-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_summable_jet_growing_affine_root_union_uniform_neighborhood_gap_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-summable-jet-growing-affine-root-union-uniform-neighborhood-gap-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 65, "independent": 56}
EXPLORATION_IDS = ("EXP-000704", "EXP-000705", "EXP-000706")


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
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


def normalize_exact(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_exact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_exact(item) for item in value]
    try:
        return str(F(str(value)))
    except (ValueError, ZeroDivisionError):
        return value


def run_child(path: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(path), "--output", str(output)],
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
    roots = [Path.home() / ".cache" / "codex-runtimes", Path("C:/Users/NaEun/.cache/codex-runtimes")]
    for root in roots:
        for candidate in root.glob(f"*/dependencies/native/poppler/Library/bin/{name}.exe"):
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
    if isinstance(action, IndirectObject):
        action = action.get_object()
    if isinstance(action, DictionaryObject):
        if str(action.get("/S")) != "/GoTo":
            return False, f"non-GoTo OpenAction: {action.get('/S')}"
        action = action.get("/D")
        if isinstance(action, IndirectObject):
            action = action.get_object()
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
    parser.add_argument("--self-test", action="store_true", help="compare a fresh payload with the stored integrated result")
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    audit.check("manifest", "result identity", manifest.get("result_id") == RESULT_ID and manifest.get("result_ledger_id") == LEDGER_ID, [manifest.get("result_id"), manifest.get("result_ledger_id")], [RESULT_ID, LEDGER_ID])
    audit.check("manifest", "exploration ID parity", manifest.get("exploration_ids") == list(EXPLORATION_IDS), manifest.get("exploration_ids"), list(EXPLORATION_IDS))

    children: dict[str, dict[str, Any]] = {}
    embedded_rows = 0
    temp_parent = REPO / "internal" / "tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r161-child-", dir=temp_parent) as temporary:
        for name, path, stored_output in (
            ("primary", PRIMARY, PRIMARY_OUTPUT),
            ("independent", INDEPENDENT, INDEPENDENT_OUTPUT),
        ):
            fresh_output = Path(temporary) / f"{name}.json"
            run = run_child(path, fresh_output)
            audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
            fresh = load_json(fresh_output)
            stored = load_json(stored_output)
            audit.check("children", f"{name} fresh equals stored", fresh == stored, sha256(fresh_output), sha256(stored_output))
            children[name] = fresh
            rows = fresh.get("assertions", [])
            expected_schema = f"tect/a13-{SLUG}-{name}/1.0"
            audit.check("children", f"{name} schema", fresh.get("schema") == expected_schema, fresh.get("schema"), expected_schema)
            audit.check("children", f"{name} identity", fresh.get("result_id") == RESULT_ID and fresh.get("result_ledger_id") == LEDGER_ID, [fresh.get("result_id"), fresh.get("result_ledger_id")], [RESULT_ID, LEDGER_ID])
            audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
            audit.check("children", f"{name} summary", fresh.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, fresh.get("summary"), "all pass")
            identities = [(row.get("group"), row.get("name")) for row in rows]
            audit.check("children", f"{name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
            for row in rows:
                audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))
            embedded_rows += len(rows)

    primary = children["primary"]
    independent = children["independent"]
    audit.check("scope", "primary scope equals manifest", primary.get("scope") == manifest.get("scope"), primary.get("scope"), manifest.get("scope"))
    audit.check("scope", "independent scope equals manifest", independent.get("scope") == manifest.get("scope"), independent.get("scope"), manifest.get("scope"))
    audit.check("scope", "common no-overclaim", manifest.get("no_overclaim") == primary.get("no_overclaim") == independent.get("no_overclaim"), [manifest.get("no_overclaim"), primary.get("no_overclaim"), independent.get("no_overclaim")], "equal")
    for token in ("fixed spatial dimension three", "global terminal", "local root E_CN", "realised-past", "T-050/A13", "phase/PDE", "Sector-A"):
        audit.check("scope", f"boundary token {token}", token.lower() in str(manifest.get("no_overclaim", "")).lower(), token, "present")

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "none")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    pd = primary["derived"]
    ider = independent["derived"]
    parity = {
        "symbol minimum": (pd["symbol_minimum"], ider["symbol_minimum"]),
        "symbol kappa": (pd["symbol_global_envelope_kappa"], ider["symbol_global_envelope_kappa"]),
        "symbol discriminant": (pd["symbol_global_envelope_discriminant"], ider["symbol_global_envelope_discriminant"]),
        "lattice floor": (pd["side16_lattice_floor_c0"], ider["side16_lattice_floor_c0"]),
        "synthesis g": (pd["synthesis_envelope_g"], ider["synthesis_envelope_g"]),
        "shell constants": (pd["shell_upper_constants"], ider["shell_upper_constants"]),
        "jet bounds": (pd["jet_bounds"], ider["jet_bounds"]),
        "product a squared": (pd["product_data_a_squared"], ider["product_data_a_squared"]),
        "product b squared": (pd["product_data_b_squared"], ider["product_data_b_squared"]),
        "origin gap": (pd["origin_gap"], ider["origin_gap"]),
        "target gap": (pd["target_gap"], ider["target_gap"]),
        "modulus allowance": (pd["uniform_modulus_allowance"], ider["uniform_modulus_allowance"]),
        "retained gap": (pd["retained_gap"], ider["retained_gap"]),
    }
    for name, (left, right) in parity.items():
        audit.check("parity", name, normalize_exact(left) == normalize_exact(right), normalize_exact(left), normalize_exact(right))
    audit.check("oracle", "retained gap exact", F(pd["retained_gap"]) == F(13, 100) > F(1, 10), pd["retained_gap"], "13/100 > 1/10")
    audit.check("oracle", "fixed d3 load-bearing", primary["scope"].get("fixed_spatial_dimension_three") is True and ider["shell_polynomials"]["d4"] != ider["shell_polynomials"]["d3"], ider["shell_polynomials"], "d3 theorem with d4 harmonic boundary")
    audit.check("oracle", "formal modulus present", "M_2" in str(pd["formal_L_star"]) and "M_3" in str(pd["formal_L_star"]) and bool(ider["formal_L_star"]), [pd["formal_L_star"], ider["formal_L_star"]], "positive formal L-star")

    artifact_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__).resolve(),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in artifact_paths.items():
        record = manifest["files"][key]
        audit.check("artifacts", f"{key} path", record.get("path") == relative(path), record.get("path"), relative(path))
        audit.check("artifacts", f"{key} hash", record.get("sha256") == sha256(path), record.get("sha256"), sha256(path))
    for key, expected_hash in manifest["authority_hashes"].items():
        authority = REPO / manifest["authorities"][key]
        audit.check("authority-hashes", key, sha256(authority) == expected_hash, sha256(authority), expected_hash)

    note_text = NOTE.read_text(encoding="utf-8")
    note_flat = " ".join(note_text.split())
    for token in (
        "Summable covariance jets", "global terminal action", "local-owner firewall",
        "5g^2\\over8x^3", "4096", "L_*", "13\\over100", "three-dimensional",
        "Per-family continuity is not enough", "Devil's-advocate", "phase/PDE", "Result footer",
    ):
        haystack = note_text if "\\" in token else note_flat
        audit.check("note", f"scope token {token}", token.lower() in haystack.lower(), token, "present")

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
    action_ok, action = open_action_summary(reader)
    page_count = len(reader.pages)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [] and action_ok, {"findings": findings, "open_action": action}, {"findings": [], "open_action": "first page Fit"})
    audit.check("pdf", "page count pinned", page_count == pdf_contract["pages"], page_count, pdf_contract["pages"])
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    for token in ("R-161", "Summable covariance", "global terminal", "family-cardinality-free", "T-050", "phase/PDE"):
        audit.check("pdf", f"text contains {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r161-render-", dir=temp_parent) as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    changelog_rows = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog = load_json(REPO / "verification/catalog.json")
    explorations = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_lookup = {row["id"]: row for row in explorations}
    audit.check("records", "R-161 ledger entry", '<a id="r-161"></a>' in results_text and RESULT_ID in results_text, LEDGER_ID, "registered")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "13/100" in claim_text, RESULT_ID, "registered")
    audit.check("records", "lineage narrative", "R-161" in lineage_text and "summable" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "status immutable evidence", relative(MANIFEST) in status.get("legacy_evidence", []), relative(MANIFEST), "registered")
    audit.check("records", "claim remains T4 open", status.get("tier") == "T4" and status.get("proof_complete") is False, [status.get("tier"), status.get("proof_complete")], ["T4", False])
    audit.check("records", "append-only changelog entry", any(LEDGER_ID in json.dumps(row, sort_keys=True) and RESULT_ID in json.dumps(row, sort_keys=True) for row in changelog_rows), LEDGER_ID, "registered")
    audit.check("records", "theorem map registration", LEDGER_ID in json.dumps(theorem_map, sort_keys=True) and RESULT_ID in json.dumps(theorem_map, sort_keys=True), LEDGER_ID, "registered")
    audit.check("records", "proof map", LEDGER_ID in proof_map and all(identifier in proof_map for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    audit.check("records", "catalog manifest", relative(MANIFEST) in json.dumps(catalog, sort_keys=True), relative(MANIFEST), "registered")
    audit.check("records", "exploration records", all(identifier in exploration_lookup for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(identifier in exploration_lookup for identifier in EXPLORATION_IDS):
        verdicts = [exploration_lookup[identifier]["verdict"] for identifier in EXPLORATION_IDS]
        audit.check("records", "exploration verdicts", verdicts == ["advanced", "advanced", "failed"], verdicts, ["advanced", "advanced", "failed"])

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
        "pdf": {"sha256": pdf_after, "pages": page_count, "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
    }
    if arguments.self_test:
        stored = load_json(arguments.output)
        if stored != payload:
            raise AssertionError("stored integrated result differs from fresh self-test payload")
        print(f"{RESULT_ID} integrated self-test: {len(audit.rows)}/{len(audit.rows)} PASS")
        return 0
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
