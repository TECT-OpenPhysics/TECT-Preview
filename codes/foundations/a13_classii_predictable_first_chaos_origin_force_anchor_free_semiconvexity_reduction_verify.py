#!/usr/bin/env python3
"""Integrated verifier for the A13 R-164 predictable-first-chaos package."""

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
RESULT_ID = (
    "A13-CLASSII-PREDICTABLE-FIRST-CHAOS-ORIGIN-FORCE-"
    "ANCHOR-FREE-SEMICONVEXITY-REDUCTION"
)
LEDGER_ID = "R-164"
SLUG = "predictable-first-chaos-origin-force-anchor-free-semiconvexity-reduction"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction_independent.py"
NOTE = CLAIM_DIR / "notes/classii-predictable-first-chaos-origin-force-anchor-free-semiconvexity-reduction-260804-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-04-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 50, "independent": 47}
EXPLORATION_IDS = ("EXP-000744",)
EXACT_RATIONAL = re.compile(r"^[+-]?\d+(?:/[1-9]\d*)?$")


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
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def canonical_exact_json(value: Any) -> Any:
    """Compare exact diagnostics across SymPy-string and Fraction/int JSON."""
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return F(value, 1)
    if isinstance(value, float):
        raise TypeError(f"floating diagnostic is not exact: {value!r}")
    if isinstance(value, str):
        token = value.strip()
        return F(token) if EXACT_RATIONAL.fullmatch(token) else value
    if isinstance(value, list):
        return [canonical_exact_json(item) for item in value]
    if isinstance(value, dict):
        return {str(key): canonical_exact_json(item) for key, item in value.items()}
    raise TypeError(f"unsupported diagnostic type: {type(value).__name__}")


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


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
    roots = [Path.home() / ".cache/codex-runtimes", Path("C:/Users/NaEun/.cache/codex-runtimes")]
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


def open_action_ok(reader: PdfReader) -> tuple[bool, str]:
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
    first_reference = reader.pages[0].indirect_reference
    page_reference = action[0]
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
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    audit.check("manifest", "result identity", manifest.get("result_id") == RESULT_ID and manifest.get("result_ledger_id") == LEDGER_ID, [manifest.get("result_id"), manifest.get("result_ledger_id")], [RESULT_ID, LEDGER_ID])
    audit.check("manifest", "exploration IDs", manifest.get("exploration_ids") == list(EXPLORATION_IDS), manifest.get("exploration_ids"), list(EXPLORATION_IDS))
    audit.check("manifest", "child count contract", manifest["verification"].get("primary_assertions") == EXPECTED_CHILD_COUNTS["primary"] and manifest["verification"].get("independent_assertions") == EXPECTED_CHILD_COUNTS["independent"], [manifest["verification"].get("primary_assertions"), manifest["verification"].get("independent_assertions")], [EXPECTED_CHILD_COUNTS["primary"], EXPECTED_CHILD_COUNTS["independent"]])

    children: dict[str, dict[str, Any]] = {}
    embedded_rows = 0
    temp_parent = REPO / "internal/tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r164-child-", dir=temp_parent) as temporary:
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
    audit.check("scope", "no-overclaim parity", manifest.get("no_overclaim") == primary.get("no_overclaim") == independent.get("no_overclaim"), [manifest.get("no_overclaim"), primary.get("no_overclaim"), independent.get("no_overclaim")], "exact parity")
    for token in ("zero-control", "direct", "stationary reduced", "nonzero-feedback", "random", "pathwise", "T-050", "phase/PDE", "Sector-A"):
        audit.check("scope", f"boundary token {token}", token.lower() in manifest.get("no_overclaim", "").lower(), token, "present")

    roots, relative_import, floats = imported_roots_and_floats(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "none")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")
    audit.check("independence", "no floating constants", floats == [], floats, [])

    pd = primary["diagnostics"]
    ider = independent["diagnostics"]
    audit.check("parity", "exact canonicalizer integer string", canonical_exact_json("10395") == canonical_exact_json(10395), "10395", 10395)
    audit.check("parity", "exact canonicalizer nested signed integers", canonical_exact_json({"a": "-1", "b": ["2", 3]}) == canonical_exact_json({"a": -1, "b": [2, "3"]}), {"a": "-1", "b": ["2", 3]}, {"a": -1, "b": [2, "3"]})
    audit.check("parity", "exact canonicalizer preserves symbolic strings", canonical_exact_json("5/11 - rho/4") == "5/11 - rho/4", canonical_exact_json("5/11 - rho/4"), "5/11 - rho/4")
    try:
        canonical_exact_json(0.5)
    except TypeError:
        rejects_float = True
    else:
        rejects_float = False
    audit.check("parity", "exact canonicalizer rejects floats", rejects_float, rejects_float, True)
    for name in (
        "generic_real_twelfth_moment",
        "sextic_threshold",
        "origin_force_certificate_components",
        "direct_t050_constant_components",
        "graph_force_pullback_components",
    ):
        primary_value = pd.get(name)
        independent_value = ider.get(name)
        audit.check(
            "parity",
            name,
            canonical_exact_json(primary_value) == canonical_exact_json(independent_value),
            primary_value,
            independent_value,
        )
    audit.check("oracle", "primary projection bound", F(pd["fixture_projected_norm"]) <= F(pd["fixture_variance"]), pd["fixture_projected_norm"], f"<= {pd['fixture_variance']}")
    audit.check("oracle", "independent projection bound", F(ider["fixture_projected_norm"]) <= F(ider["fixture_variance"]), ider["fixture_projected_norm"], f"<= {ider['fixture_variance']}")
    audit.check("oracle", "general real moment", int(pd["generic_real_twelfth_moment"]) == 10395, pd["generic_real_twelfth_moment"], 10395)
    audit.check("oracle", "sextic threshold", F(pd["sextic_threshold"]) == F(3, 20), pd["sextic_threshold"], F(3, 20))

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
        "sharp predictable first-chaos bound", "independent-Gaussian linear/isometric",
        "Z_{K,0}=Z_0=S_\\pi\\xi", "11!!", "B_*:=", "{10\\over11}",
        "source Hessian is counted once", "exact metric/stabilizer transport",
        "Devil's-advocate", "T-050", "phase/PDE", "Result footer",
    ):
        haystack = note_text if "\\" in token else note_flat
        audit.check("note", f"token {token}", token.lower() in haystack.lower(), token, "present")
    malformed = re.search(r"(?<!\\)\bqquad\b", note_text)
    audit.check("note", "no malformed qquad", malformed is None, malformed.group(0) if malformed else "absent", "absent")

    pdf_contract = manifest["verification"]["pdf"]
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(pdf_contract["source_date_epoch"])
    environment["FORCE_SOURCE_DATE"] = "1"
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
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, "PASS" if "FORM-CHECK: PASS" in build.stdout else "missing", "PASS")
    audit.check("pdf", "zero overfull boxes", "OVERFULL-HBOX: 0" in build.stdout, "PASS" if "OVERFULL-HBOX: 0" in build.stdout else "missing", "PASS")
    audit.check("pdf", "deterministic rebuild", pdf_before == pdf_after, pdf_after, pdf_before)
    reader = PdfReader(str(PDF), strict=True)
    findings = pdf_security(reader)
    action_ok, action_summary = open_action_ok(reader)
    page_count = len(reader.pages)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan", findings == [] and action_ok, {"findings": findings, "open_action": action_summary}, {"findings": [], "open_action": "first page Fit"})
    audit.check("pdf", "page count", page_count == pdf_contract["pages"], page_count, pdf_contract["pages"])
    audit.check("pdf", "size", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    for token in ("R-164", "predictable", "11!!", "-1/110", "-10/11", "T-050", "phase/PDE"):
        audit.check("pdf", f"text {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="r164-render-", dir=temp_parent) as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", str(pdf_contract["render_dpi"]), str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == page_count, rendered_count, page_count)
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    claim_text = (CLAIM_DIR / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM_DIR / "lineage-narrative.md").read_text(encoding="utf-8")
    index_text = (CLAIM_DIR / "INDEX.md").read_text(encoding="utf-8")
    status = load_json(CLAIM_DIR / "status.json")
    todo = load_json(REPO / "todo/todo.json")
    changelog_rows = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog_text = json.dumps(load_json(REPO / "verification/catalog.json"), sort_keys=True)
    explorations = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_lookup = {row["id"]: row for row in explorations}
    audit.check("records", "R-164 ledger", '<a id="r-164"></a>' in results_text and RESULT_ID in results_text and "50/50" in results_text and "47/47" in results_text and "seven-page PDF" in results_text, LEDGER_ID, "registered with counts and PDF")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "B_*" in claim_text and "-10/11" in claim_text, RESULT_ID, "registered")
    audit.check("records", "lineage narrative", "R-164" in lineage_text and "first-chaos" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "generated index", RESULT_ID in index_text, RESULT_ID, "registered")
    audit.check("records", "status evidence", relative(MANIFEST) in status.get("legacy_evidence", []) and "R-164" in status.get("statement", ""), relative(MANIFEST), "registered")
    audit.check("records", "status remains T4 open", status.get("tier") == "T4" and status.get("proof_complete") is False and status.get("no_overclaim") == manifest.get("no_overclaim"), [status.get("tier"), status.get("proof_complete")], ["T4", False])
    audit.check("records", "TODO T-050", any(row.get("id") == "T-050" and "R-164" in row.get("note", "") and "owner" in row.get("note", "").lower() for row in todo.get("tasks", [])), LEDGER_ID, "registered")
    audit.check("records", "changelog", any(LEDGER_ID in json.dumps(row, sort_keys=True) and (RESULT_ID in json.dumps(row, sort_keys=True) or relative(MANIFEST) in json.dumps(row, sort_keys=True)) for row in changelog_rows), LEDGER_ID, "registered")
    audit.check("records", "theorem map", LEDGER_ID in json.dumps(theorem_map, sort_keys=True) and RESULT_ID in json.dumps(theorem_map, sort_keys=True) and "SUBPROOF" in json.dumps(theorem_map, sort_keys=True), LEDGER_ID, "registered as subproof")
    audit.check("records", "proof map", LEDGER_ID in proof_map and all(identifier in proof_map for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    package_paths = [relative(MANIFEST)] + [relative(path) for path in artifact_paths.values()] + [relative(DEFAULT_OUTPUT)]
    audit.check("records", "catalog package", all(path in catalog_text for path in package_paths), package_paths, "all catalogued")
    audit.check("records", "explorations", all(identifier in exploration_lookup for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(identifier in exploration_lookup for identifier in EXPLORATION_IDS):
        audit.check("records", "exploration verdicts", [exploration_lookup[item]["verdict"] for item in EXPLORATION_IDS] == ["advanced"], [exploration_lookup[item]["verdict"] for item in EXPLORATION_IDS], ["advanced"])

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
