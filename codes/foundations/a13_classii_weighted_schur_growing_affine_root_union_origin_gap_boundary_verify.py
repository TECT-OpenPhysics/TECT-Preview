#!/usr/bin/env python3
"""Integrated verifier for the A13 R-160 weighted-Schur package."""

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
RESULT_ID = "A13-CLASSII-WEIGHTED-SCHUR-GROWING-AFFINE-ROOT-UNION-ORIGIN-GAP-BOUNDARY"
LEDGER_ID = "R-160"
SLUG = "weighted-schur-growing-affine-root-union-origin-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / "classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_manifest.json"
PRIMARY = REPO / "codes/foundations/a13_classii_weighted_schur_growing_affine_root_union_origin_gap_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_weighted_schur_growing_affine_root_union_origin_gap_boundary_independent.py"
NOTE = CLAIM_DIR / "notes/classii-weighted-schur-growing-affine-root-union-origin-gap-boundary-260803-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
EXPECTED_CHILD_COUNTS = {"primary": 51, "independent": 59}
EXPLORATION_IDS = ("EXP-000698", "EXP-000699", "EXP-000700")


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
    for candidate in runtime.glob(f"*/dependencies/native/poppler/Library/bin/{name}.exe"):
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
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)
    audit.check("manifest", "exploration ID parity", manifest.get("exploration_ids") == list(EXPLORATION_IDS), manifest.get("exploration_ids"), list(EXPLORATION_IDS))

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
        audit.check("children", f"{name} schema", child.get("schema") == f"tect/a13-{SLUG}-{name}/1.0", child.get("schema"), f"tect/a13-{SLUG}-{name}/1.0")
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} ledger", child.get("result_ledger_id") == LEDGER_ID, child.get("result_ledger_id"), LEDGER_ID)
        audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
        audit.check("children", f"{name} summary", child.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, child.get("summary"), "all pass")
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
    for token in ("source-target reuse", "nonzero radius", "realised-past", "T-050", "phase/PDE", "Sector-A"):
        audit.check("scope", f"boundary token {token}", token.lower() in str(manifest.get("no_overclaim", "")).lower(), token, "present")

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", not any(root.startswith("a13_classii") for root in roots), sorted(roots), "none")
    audit.check("independence", "no primary artifact read", PRIMARY.name not in independent_text and PRIMARY_OUTPUT.parent.name not in independent_text, PRIMARY.name, "absent")

    p = primary["diagnostics"]
    i = independent["derived"]
    parity = {
        "volume": (p["volume"], i["volume"]),
        "H6 upper": (p["H6_strict_upper"], i["H6_strict_upper"]),
        "diagonal factor": (p["diagonal_radial_factor"], i["diagonal_radial_factor"]),
        "edge factor": (p["edge_radial_factor"], i["edge_radial_factor"]),
        "diagonal numerator": (p["diagonal_numerator"], i["diagonal_numerator"]),
        "edge numerator": (p["edge_numerator"], i["edge_numerator"]),
        "Schur ratio": (p["schur_weight_ratio"], i["schur_weight_ratio"]),
        "nonzero floor": (p["nonzero_mode_floor"], i["nonzero_mode_floor"]),
        "unit shell interval": (p["unit_shell_interval"], i["unit_shell_interval"]),
        "higher shell floor": (p["higher_shell_floor"], i["higher_shell_floor"]),
        "source Hessian": (p["source_hessian"], i["source_hessian"]),
        "continuous budget": (p["continuous_endpoint_loss_budget"], i["continuous_endpoint_loss_budget"]),
        "continuous gap": (p["continuous_certified_gap"], i["continuous_certified_gap"]),
        "continuous headroom": (p["continuous_threshold_headroom"], i["continuous_threshold_headroom"]),
        "lattice budget": (p["lattice_endpoint_loss_budget"], i["lattice_endpoint_loss_budget"]),
        "lattice gap": (p["lattice_certified_gap"], i["lattice_certified_gap"]),
        "lattice headroom": (p["lattice_threshold_headroom"], i["lattice_threshold_headroom"]),
        "interior loss": (p["interior_loss_upper"], i["interior_loss_upper"]),
        "floor-removal witness": (p["floor_removal_majorant_witness"], i["floor_removal_majorant_witness"]),
    }
    for name, (left, right) in parity.items():
        audit.check("parity", name, normalize_exact(left) == normalize_exact(right), normalize_exact(left), normalize_exact(right))
    audit.check("parity", "exact lower symbol", p["lower_symbol"] == "x**2 - 4626377063*x/5000000000 + 5020336473/10000000000" and normalize_exact(i["lower_symbol"]) == ["5020336473/10000000000", "-4626377063/5000000000", "1"], [p["lower_symbol"], i["lower_symbol"]], "exact authority symbol")
    for label, bounds in (("primary", p["pi_bounds"]), ("independent", i["pi_bounds"])):
        audit.check("pi", f"{label} rational enclosure", F(bounds[0]) > F(157, 50) and F(bounds[1]) < F(22, 7), bounds, [">157/50", "<22/7"])
    audit.check("oracle", "continuous gap exact", F(p["continuous_certified_gap"]) == F(19, 160), p["continuous_certified_gap"], "19/160")
    audit.check("oracle", "actual-lattice gap exact", F(p["lattice_certified_gap"]) == F(4, 25), p["lattice_certified_gap"], "4/25")
    audit.check("oracle", "both gaps exceed target", F(p["continuous_certified_gap"]) > F(1, 10) and F(p["lattice_certified_gap"]) > F(p["continuous_certified_gap"]), [p["continuous_certified_gap"], p["lattice_certified_gap"]], ">1/10 and ordered")
    audit.check("oracle", "coarse symbol correction exact", p["coarse_surrogate_difference"] == "138622937*x/5000000000 + 7336473/10000000000" and normalize_exact(i["coarse_surrogate_difference"]) == ["7336473/10000000000", "138622937/5000000000"], [p["coarse_surrogate_difference"], i["coarse_surrogate_difference"]], "exact positive affine correction")
    audit.check("adversarial", "independent unweighted fixture strict", F(i["wrong_unweighted_floor_excess"]) > 0, i["wrong_unweighted_floor_excess"], ">0")
    audit.check("adversarial", "floor-removal fixture strict", F(p["floor_removal_majorant_witness"]["cleared_excess"]) > 0, p["floor_removal_majorant_witness"], "method obstruction only")

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
        "Weighted Schur", "19\\over160", "4\\over25", "source-target reuse",
        "adverse scalar comparison", "coarse scratch", "Bernstein", "Devil's-advocate",
        "T-050", "phase or PDE verdict", "Result footer",
    ):
        haystack = note_text if "\\" in token else note_flat
        audit.check("note", f"scope token {token}", token.lower() in haystack.lower(), token, "present")

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
    action_ok, action = open_action_summary(reader)
    page_count = len(reader.pages)
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [] and action_ok, {"findings": findings, "open_action": action}, {"findings": [], "open_action": "first page Fit"})
    audit.check("pdf", "page count pinned", page_count == pdf_contract["pages"], page_count, pdf_contract["pages"])
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    for token in ("R-160", "19/160", "4/25", "source-target", "coarse scratch", "T-050", "phase/PDE"):
        audit.check("pdf", f"text contains {token}", token in extracted, token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-r160-render-") as temporary:
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
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog = load_json(REPO / "verification/catalog.json")
    explorations = [json.loads(line) for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    exploration_lookup = {row["id"]: row for row in explorations}
    audit.check("records", "R-160 ledger entry", '<a id="r-160"></a>' in results_text and RESULT_ID in results_text, LEDGER_ID, "registered")
    audit.check("records", "claim narrative", RESULT_ID in claim_text and "4/25" in claim_text, RESULT_ID, "registered")
    audit.check("records", "lineage narrative", "R-160" in lineage_text and "weighted-schur" in lineage_text.lower(), LEDGER_ID, "registered")
    audit.check("records", "status synchronization", status.get("no_overclaim") == manifest.get("no_overclaim") and "R-160" in status.get("statement", ""), status.get("statement"), "R-160/current no-overclaim")
    audit.check("records", "claim remains T4 open", status.get("tier") == "T4" and status.get("proof_complete") is False, [status.get("tier"), status.get("proof_complete")], ["T4", False])
    audit.check("records", "TODO route", "R-160" in todo_text and "T-050" in todo_text and "T-054" in todo_text, "R-160/T-050/T-054", "registered")
    audit.check("records", "changelog entry", "R-160" in changelog_text and RESULT_ID in changelog_text, LEDGER_ID, "registered")
    audit.check("records", "theorem map", "R-160" in json.dumps(theorem_map, sort_keys=True), LEDGER_ID, "registered")
    audit.check("records", "proof map", "R-160" in proof_map and all(identifier in proof_map for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    audit.check("records", "catalog manifest", relative(MANIFEST) in json.dumps(catalog, sort_keys=True), relative(MANIFEST), "registered")
    audit.check("records", "exploration records", all(identifier in exploration_lookup for identifier in EXPLORATION_IDS), EXPLORATION_IDS, "registered")
    if all(identifier in exploration_lookup for identifier in EXPLORATION_IDS):
        audit.check("records", "exploration verdicts", [exploration_lookup[identifier]["verdict"] for identifier in EXPLORATION_IDS] == ["advanced", "advanced", "failed"], [exploration_lookup[identifier]["verdict"] for identifier in EXPLORATION_IDS], ["advanced", "advanced", "failed"])

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
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
