#!/usr/bin/env python3
"""Integrated verifier for the T0 PA-M5-NL3-SV candidate certificate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pypdf import PdfReader


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M5-NL3-SV-v0"
SLUG = "pre-a-pa-m5-nl3-sv-candidate"
SCHEMA = f"tect/{SLUG}-integrated/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
CLAIM_DIR = REPO / "claims" / CLAIM_CONTEXT
PRIMARY = REPO / "codes/foundations/pre_a_pa_m5_nl3_sv_candidate.py"
INDEPENDENT = REPO / "codes/foundations/pre_a_pa_m5_nl3_sv_candidate_independent.py"
VERIFIER = Path(__file__).resolve()
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-03-integrated-{SLUG}/result.json"
MANIFEST = REPO / "strategy/pre-a-pa-m5-nl3-sv-candidate-manifest.json"
NOTE = REPO / "strategy/pre-a-pa-m5-nl3-sv-candidate-certificate-260803-v0.1.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
CHARTER = REPO / "strategy/pre-a-evidence-first-model-selection-charter-260802.md"
BOUNDARY_SEED = REPO / "strategy/boundary-massless-mode-criticality-seed-260802.md"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R158_VERIFIER = REPO / "codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py"
NEGATIVE_ID = "NG-2026-08-03-PA-M5-BARE-ISOTROPIC-SHELL-CAUSAL-CONE"
EXPLORATION_ID = "EXP-000688"
EXPECTED_CHILD_COUNTS = {"primary": 41, "independent": 29}


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": stringify(actual),
                "expected": stringify(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def stringify(value: Any) -> Any:
    if isinstance(value, Path):
        return relative(value)
    if isinstance(value, dict):
        return {str(key): stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(stringify(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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
        rendered = path.relative_to(REPO)
    except ValueError:
        rendered = path
    return str(rendered).replace("\\", "/")


def imported_roots(path: Path) -> tuple[set[str], bool]:
    roots: set[str] = set()
    relative_import = False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            relative_import = relative_import or bool(node.level)
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
        "/SubmitForm", "/ImportData", "/GoToR", "/URI",
    }

    def walk(value: Any, location: str) -> None:
        try:
            obj = value.get_object()
        except Exception:
            obj = value
        identity = getattr(value, "idnum", None), getattr(value, "generation", None)
        if identity[0] is not None:
            if identity in visited:
                return
            visited.add(identity)
        if isinstance(obj, dict):
            for key, item in obj.items():
                if str(key) in unsafe:
                    findings.append(f"{location}/{key}")
                walk(item, f"{location}/{key}")
        elif isinstance(obj, (list, tuple)):
            for index, item in enumerate(obj):
                walk(item, f"{location}[{index}]")

    walk(reader.trailer, "trailer")
    return sorted(set(findings))


def exploration_lookup(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            records[record["id"]] = record
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    manifest = load_json(MANIFEST)

    tracked_children = {"primary": PRIMARY_OUTPUT, "independent": INDEPENDENT_OUTPUT}
    scripts = {"primary": PRIMARY, "independent": INDEPENDENT}
    children: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="tect-pa-m5-child-") as temporary:
        temporary_root = Path(temporary)
        for name, script in scripts.items():
            output = temporary_root / f"{name}.json"
            run = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=180,
            )
            audit.check("children", f"{name} exits zero", run.returncode == 0, run.returncode, 0)
            child = load_json(output)
            children[name] = child
            rows = child.get("assertions", [])
            audit.check("children", f"{name} schema", child.get("schema") == f"tect/{SLUG}-{name}/0.1", child.get("schema"), f"tect/{SLUG}-{name}/0.1")
            audit.check("children", f"{name} candidate", child.get("candidate_id") == CANDIDATE_ID, child.get("candidate_id"), CANDIDATE_ID)
            audit.check("children", f"{name} is non-claim-bearing", child.get("claim_bearing") is False, child.get("claim_bearing"), False)
            audit.check("children", f"{name} count", len(rows) == EXPECTED_CHILD_COUNTS[name], len(rows), EXPECTED_CHILD_COUNTS[name])
            audit.check("children", f"{name} summary", child.get("summary") == {"passed": len(rows), "failed": 0, "total": len(rows)}, child.get("summary"), "all pass")
            identities = [(row.get("group"), row.get("name")) for row in rows]
            audit.check("children", f"{name} row identities unique", len(identities) == len(set(identities)), len(identities), len(set(identities)))
            audit.check("children", f"{name} tracked result reproducible", child == load_json(tracked_children[name]), sha256(output), sha256(tracked_children[name]))
            for row in rows:
                audit.check(f"child-{name}/{row.get('group')}", str(row.get("name")), row.get("status") == "PASS", row.get("actual"), row.get("expected"))

    primary = children["primary"]
    independent = children["independent"]
    audit.check("parity", "child scopes agree", primary.get("scope") == independent.get("scope") == manifest.get("scope"), [primary.get("scope"), independent.get("scope")], manifest.get("scope"))
    audit.check("parity", "no-overclaim synchronized", primary.get("no_overclaim") == independent.get("no_overclaim") == manifest.get("no_overclaim"), "primary/independent/manifest", "equal")
    audit.check("parity", "all exact results agree", primary.get("exact_results") == independent.get("exact_results") == manifest.get("exact_results"), [primary.get("exact_results"), independent.get("exact_results")], manifest.get("exact_results"))

    roots, relative_import = imported_roots(INDEPENDENT)
    independent_text = INDEPENDENT.read_text(encoding="utf-8")
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no scientific package", not ({"sympy", "numpy", "scipy"} & roots), sorted(roots), "standard library only")
    audit.check("independence", "no primary module import", "pre_a_pa_m5_nl3_sv_candidate" not in roots, sorted(roots), "absent")
    primary_result_references = [relative(PRIMARY_OUTPUT.parent), relative(PRIMARY_OUTPUT)]
    audit.check(
        "independence",
        "no primary result read",
        not any(reference in independent_text for reference in primary_result_references),
        primary_result_references,
        "absent",
    )

    exact = primary["exact_results"]
    audit.check("oracle", "continuum shell condition", exact["continuous_shell_condition"] == "g>c*sigma", exact["continuous_shell_condition"], "g>c*sigma")
    audit.check("oracle", "finite torus gate separated", exact["finite_torus_nonzero_first_shell_condition"] == "g>c*(sigma+(2*pi/L)^2)", exact["finite_torus_nonzero_first_shell_condition"], "g>c*(sigma+s1)")
    audit.check("oracle", "neutral threshold", exact["finite_torus_zero_reference_threshold"] == "kappa_L>=3*u_minus^2/(16*v)", exact["finite_torus_zero_reference_threshold"], "3*u_minus^2/(16*v)")
    audit.check("oracle", "rank-one causal failure", exact["bare_shell_causal_verdict"].startswith("FAIL: rank-one"), exact["bare_shell_causal_verdict"], "FAIL: rank-one...")
    audit.check("oracle", "candidate narrowed not selected", exact["candidate_t054_verdict"] == "RETAIN STATIC MECHANISM; REJECT BARE JOINT T-053 SURVIVOR", exact["candidate_t054_verdict"], "retained static; rejected causal survivor")

    artifacts = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": VERIFIER,
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in artifacts.items():
        record = manifest["files"][key]
        audit.check("artifacts", f"{key} path", record.get("path") == relative(path), record.get("path"), relative(path))
        audit.check("artifacts", f"{key} hash", record.get("sha256") == sha256(path), record.get("sha256"), sha256(path))
    integrated_record = manifest["files"]["integrated_result"]
    audit.check("artifacts", "integrated result path", integrated_record.get("path") == relative(DEFAULT_OUTPUT), integrated_record.get("path"), relative(DEFAULT_OUTPUT))
    audit.check("artifacts", "integrated result has no self-cycle hash", "sha256" not in integrated_record, integrated_record, "path and schema only")

    authority_paths = {relative(CHARTER): CHARTER, relative(BOUNDARY_SEED): BOUNDARY_SEED, relative(A1_MANIFEST): A1_MANIFEST}
    for key, path in authority_paths.items():
        audit.check("authority-hashes", key, manifest["authority_hashes"].get(key) == sha256(path), manifest["authority_hashes"].get(key), sha256(path))

    note_text = NOTE.read_text(encoding="utf-8")
    required_note_tokens = [
        CANDIDATE_ID,
        NEGATIVE_ID,
        "g>c(\\sigma+s_1)",
        "rank one",
        "curved-shell square",
        "not locally",
        "thermodynamic",
        "phase transition",
        "REJECT BARE JOINT T-053",
        "41/41 PASS",
        "29/29 PASS",
    ]
    for token in required_note_tokens:
        audit.check("note", f"scope token {token}", token.lower() in note_text.lower(), token, "present")

    pdf_contract = manifest["verification"]["pdf"]
    pdf_before = sha256(PDF)
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(pdf_contract["source_date_epoch"])
    environment["FORCE_SOURCE_DATE"] = "1"
    build = subprocess.run(
        [sys.executable, str(PDF_BUILDER), relative(NOTE)],
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
    audit.check("pdf", "unencrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "security scan clear", findings == [], findings, [])
    audit.check("pdf", "page count pinned", len(reader.pages) == pdf_contract["pages"], len(reader.pages), pdf_contract["pages"])
    audit.check("pdf", "size pinned", PDF.stat().st_size == pdf_contract["size_bytes"], PDF.stat().st_size, pdf_contract["size_bytes"])
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    for token in [CANDIDATE_ID, "finite-torus zero selection", "rank one", "gauge connection", "Decision footer"]:
        audit.check("pdf", f"text contains {token}", token.lower() in extracted.lower(), token, "present")
    renderer = find_poppler("pdftoppm")
    audit.check("pdf", "Poppler available", renderer is not None, renderer, "pdftoppm")
    rendered_count = 0
    if renderer is not None:
        with tempfile.TemporaryDirectory(prefix="tect-pa-m5-render-") as temporary:
            target = Path(temporary) / "page"
            render = subprocess.run([str(renderer), "-png", "-r", "150", str(PDF), str(target)], cwd=REPO, capture_output=True, text=True, timeout=180)
            rendered_count = len(list(Path(temporary).glob("page-*.png")))
            audit.check("pdf", "Poppler exits zero", render.returncode == 0, render.returncode, 0)
            audit.check("pdf", "all pages rendered", rendered_count == len(reader.pages), rendered_count, len(reader.pages))
    audit.check("pdf", "manual visual QA pinned", str(pdf_contract.get("manual_visual_qa", "")).startswith("PASS"), pdf_contract.get("manual_visual_qa"), "PASS...")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    todo = load_json(REPO / "todo/todo.json")
    todo_lookup = {row["id"]: row for row in todo["tasks"]}
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    changelog_records = [
        json.loads(line)
        for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    strategy_index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    catalog = load_json(REPO / "verification/catalog.json")
    explorations = exploration_lookup(REPO / "explorations/log.jsonl")
    audit.check("records", "formal negative registered", NEGATIVE_ID in negative_text and "rank-one" in negative_text.lower(), NEGATIVE_ID, "registered")
    audit.check("records", "exploration registered", EXPLORATION_ID in explorations, EXPLORATION_ID, "registered")
    if EXPLORATION_ID in explorations:
        record = explorations[EXPLORATION_ID]
        audit.check("records", "exploration verdict and negative link", record.get("verdict") == "failed" and NEGATIVE_ID in record.get("formal_refs", {}).get("negatives", []), [record.get("verdict"), record.get("formal_refs")], "failed with formal negative")
    t054 = todo_lookup.get("T-054", {})
    t054_note = str(t054.get("note", ""))
    t054_current = (
        t054.get("status") == "in_progress"
        and t054.get("gate") == "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
        and "T-054" in t054_note
        and "Pre-A" in t054_note
    )
    audit.check("records", "T-054 current candidate-tournament scope", t054_current, t054, "in_progress on PA-ROUND1 evidence-role gate")
    changelog_decision = any(
        NEGATIVE_ID in record.get("neg_results", [])
        and "screened-shell" in record.get("raw", "")
        and relative(MANIFEST) in record.get("notes", [])
        and relative(PRIMARY) in record.get("scripts", [])
        for record in changelog_records
    )
    audit.check("records", "changelog decision", changelog_decision, [CANDIDATE_ID, NEGATIVE_ID], "registered with note and script evidence")
    audit.check("records", "strategy index", NOTE.name in strategy_index and MANIFEST.name in strategy_index, [NOTE.name, MANIFEST.name], "registered")
    audit.check("records", "proof map", EXPLORATION_ID in proof_map and NEGATIVE_ID in proof_map, [EXPLORATION_ID, NEGATIVE_ID], "registered")
    catalog_text = json.dumps(catalog, sort_keys=True)
    audit.check("records", "catalog manifest", relative(MANIFEST) in catalog_text, relative(MANIFEST), "registered")
    audit.check("records", "catalog note and PDF", relative(NOTE) in catalog_text and relative(PDF) in catalog_text, [relative(NOTE), relative(PDF)], "registered")

    with tempfile.TemporaryDirectory(prefix="tect-pa-m5-r158-") as temporary:
        regression_output = Path(temporary) / "r158.json"
        regression = subprocess.run(
            [sys.executable, str(R158_VERIFIER), "--output", str(regression_output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=360,
        )
        audit.check("regression", "R-158 integrated verifier exits zero", regression.returncode == 0, regression.returncode, 0)
        audit.check("regression", "R-158 and legacy A2 retained", "R-157/A2 regression PASS" in regression.stdout, regression.stdout, "R-157/A2 regression PASS")

    audit.require()
    embedded_rows = sum(EXPECTED_CHILD_COUNTS.values())
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "candidate_id": CANDIDATE_ID,
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "scope": manifest["scope"],
        "exact_results": manifest["exact_results"],
        "children": {
            "primary": {"path": relative(PRIMARY_OUTPUT), "sha256": sha256(PRIMARY_OUTPUT), "assertions": EXPECTED_CHILD_COUNTS["primary"]},
            "independent": {"path": relative(INDEPENDENT_OUTPUT), "sha256": sha256(INDEPENDENT_OUTPUT), "assertions": EXPECTED_CHILD_COUNTS["independent"]},
        },
        "embedded_child_assertions": embedded_rows,
        "integrator_only_assertions": len(audit.rows) - embedded_rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "assertions": audit.rows,
        "pdf": {"sha256": pdf_after, "pages": len(reader.pages), "size_bytes": PDF.stat().st_size, "rendered_pages": rendered_count, "security_findings": findings},
        "no_overclaim": manifest["no_overclaim"],
        "verdict": "PASS",
    }
    atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID} integrated: {len(audit.rows)}/{len(audit.rows)} PASS ({embedded_rows} child + {len(audit.rows)-embedded_rows} integrator-only); R-158/A2 regression PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
