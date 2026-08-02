#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-146 evidence package."""

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
    "A13-CLASSII-CANONICAL-COVARIANCE-RELATIVE-ANCHOR-"
    "ANISOTROPIC-TEMPORAL-REDUCTION"
)
LEDGER_ID = "R-146"
SLUG = "canonical-covariance-relative-anchor-anisotropic-temporal-reduction"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST = CLAIM_DIR / (
    "classii_canonical_covariance_relative_anchor_"
    "anisotropic_temporal_reduction_manifest.json"
)
PRIMARY = REPO / (
    "codes/foundations/a13_classii_canonical_covariance_relative_anchor_"
    "anisotropic_temporal_reduction.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_canonical_covariance_relative_anchor_"
    "anisotropic_temporal_reduction_independent.py"
)
NOTE = CLAIM_DIR / (
    "notes/classii-canonical-covariance-relative-anchor-anisotropic-"
    "temporal-reduction-260802-v1.0.tex.txt"
)
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-08-02-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(608, 615))
NEGATIVE_IDS = (
    "AUDIT-2026-08-02-A13-R146-OUTPUT-PROJECTION-OMISSION",
    "AUDIT-2026-08-02-A13-ZERO-CONTROL-RELATIVE-ANCHOR",
    "NG-2026-08-02-A13-ARBITRARY-TEMPORAL-ANISOTROPIC-POSITIVE-SUBALLOCATION",
    "NG-2026-08-02-A13-CANONICAL-COVARIANCE-AUTOMATIC-SCALAR-CANCELLATION",
)


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


def run_child(script: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script)],
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


def find_poppler(name: str) -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    for candidate in runtime.glob(
        f"*/dependencies/native/poppler/Library/bin/{name}.exe"
    ):
        if candidate.is_file():
            return candidate
    discovered = shutil.which(name)
    return Path(discovered) if discovered else None


def render_pdf(directory: Path) -> tuple[int, str, list[Path]]:
    renderer = find_poppler("pdftoppm")
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
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), sorted(
        directory.glob("page-*.png")
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
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    for name, child, expected_count in (
        ("primary", primary, 88),
        ("independent", independent, 95),
    ):
        rows = assertion_rows(child)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} all pass", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        audit.check("children", f"{name} frozen count", assertion_total(child) == expected_count, assertion_total(child), expected_count)
        audit.check("children", f"{name} count self-consistent", len(rows) == assertion_total(child), len(rows), assertion_total(child))

    roots, relative_import = imported_roots(INDEPENDENT)
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    forbidden = roots & {"numpy", "sympy", "scipy"}
    audit.check("independence", "no numerical libraries", not forbidden, sorted(forbidden), [])
    audit.check("independence", "does not import primary", not any("a13_classii" in root for root in roots), sorted(roots), "no primary import")

    primary_values = primary.get("exact_values", {})
    independent_values = independent.get("exact_values", {})
    audit.check("cross", "exact-value keys agree", set(primary_values) == set(independent_values), sorted(set(primary_values) ^ set(independent_values)), [])
    for key in sorted(primary_values):
        audit.check("cross", f"{key} agrees", primary_values[key] == independent_values[key], (primary_values[key], independent_values[key]), "equal")
    expected_values = {
        "endpoint_first_anisotropic_source_coefficient": "0",
        "endpoint_first_anisotropic_sextic_allocation": "1/100",
        "endpoint_first_anisotropic_constant": "24",
        "remaining_scalar_source_window": "5/11",
        "remaining_scalar_sextic_window": "13/50",
        "endpoint_young_constant_ceiling": "24",
        "canonical_prefix_young_constant_ceiling_diagnostic": "67",
        "canonical_value_covariance_operator_upper": "4",
    }
    for key, expected in expected_values.items():
        audit.check("cross", key, primary_values.get(key) == expected, primary_values.get(key), expected)
    audit.check("cross", "child scope agrees", primary.get("scope") == independent.get("scope"), (primary.get("scope"), independent.get("scope")), "equal")

    manifest = load_json(MANIFEST)
    note_text = NOTE.read_text(encoding="utf-8")
    note_tokens = (
        RESULT_ID, "Ledger: R-146", "section-2-relative-anchor",
        "section-3-endpoint-anisotropy", "section-4-temporal-nogo",
        "section-5-canonical-covariance", "section-6-scalar",
        "section-7-roadmap", "section-8-map", "Devil's-advocate",
        "phase-neutral", "5/11", "13/50", r"P C_6(W)", "Result footer",
    )
    for token in note_tokens:
        audit.check("note", token, token in note_text, token in note_text, True)
    for negative_id in NEGATIVE_IDS:
        audit.check("note", negative_id, negative_id in note_text, negative_id in note_text, True)

    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check("pdf", "build exits zero", build.returncode == 0, (build.returncode, build.stderr), 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    rebuilt_pdf_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash, (initial_pdf_hash, rebuilt_pdf_hash), "equal")
    reader = PdfReader(str(PDF), strict=True)
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "eight pages", len(reader.pages) == 8, len(reader.pages), 8)
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 100 for text in page_text), [len(text.strip()) for text in page_text], ">=100 each")
    for token in (LEDGER_ID, "phase-neutral", "T-050 closed: false", "Sector A closed: false"):
        audit.check("pdf", f"extracts {token}", token in extracted, token in extracted, True)
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security_findings = pdf_security(reader)
    audit.check("pdf", "no unsafe actions", security_findings == [], security_findings, [])
    with tempfile.TemporaryDirectory(prefix="tect-r146-render-") as temporary:
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
        "EXP-000608": "advanced",
        "EXP-000609": "advanced",
        "EXP-000610": "failed",
        "EXP-000611": "advanced",
        "EXP-000612": "advanced",
        "EXP-000613": "failed",
        "EXP-000614": "advanced",
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
    for name, path_text in manifest.get("authorities", {}).items():
        path = REPO / path_text
        audit.check("authority", f"{name} exists", path.is_file(), relative(path), "file")
        authority_hashes[name] = sha256(path)
    audit.check("authority", "hashes pinned", manifest.get("authority_hashes") == authority_hashes, manifest.get("authority_hashes"), authority_hashes)

    audit.check("manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    audit.check("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    audit.check("manifest", "T-050 open", manifest.get("t050_closed") is False, manifest.get("t050_closed"), False)
    audit.check("manifest", "Sector A open", manifest.get("sector_a_closed") is False, manifest.get("sector_a_closed"), False)
    for key in (
        "separate_absolute_anchor_required_for_direct_route",
        "canonical_temporal_owner_reconstruction_proved",
        "arbitrary_temporal_chart_anisotropic_transfer_proved",
        "scalar_principal_signed_relative_owner_proved",
        "complete_progressive_low_owner_proved",
        "common_terminal_doob_reconstruction_proved",
        "physical_phase_or_bcc_selection_proved",
        "t050_closed", "a13_gate_closed", "nelson_proved", "sector_a_closed",
    ):
        audit.check("scope", f"manifest {key} false", manifest["scope"].get(key) is False, manifest["scope"].get(key), False)
    for key in (
        "zero_control_centering_used",
        "relative_anchor_reduction_proved",
        "endpoint_first_anisotropic_payment_proved",
        "canonical_covariance_variational_normal_form_proved",
        "canonical_proportional_covariance_increment_split_proved",
        "predictable_scalar_common_noise_sign_proved",
        "contemporaneous_scalar_counterfixture_proved",
    ):
        audit.check("scope", f"manifest {key} true", manifest["scope"].get(key) is True, manifest["scope"].get(key), True)
    audit.check("manifest", "visual QA", str(manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa", "")).startswith("PASS"), manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa"), "PASS*")
    audit.check("manifest", "exploration ids", set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])), sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [])
    audit.check("manifest", "negative ids", set(NEGATIVE_IDS) <= set(manifest.get("negative_results", [])), sorted(set(NEGATIVE_IDS) - set(manifest.get("negative_results", []))), [])
    expected_files = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": PRIMARY_OUTPUT,
        "independent_result": INDEPENDENT_OUTPUT,
    }
    for key, path in expected_files.items():
        entry = manifest.get("files", {}).get(key, {})
        audit.check("manifest", f"{key} path", str(entry.get("path", "")).replace("\\", "/") == relative(path), entry.get("path"), relative(path))
        audit.check("manifest", f"{key} hash", entry.get("sha256") == sha256(path), entry.get("sha256"), sha256(path))
    verification = manifest.get("verification", {})
    audit.check("manifest", "primary count", int(verification.get("primary_assertions", -1)) == assertion_total(primary), verification.get("primary_assertions"), assertion_total(primary))
    audit.check("manifest", "independent count", int(verification.get("independent_assertions", -1)) == assertion_total(independent), verification.get("independent_assertions"), assertion_total(independent))
    audit.check("manifest", "PDF hash", manifest["files"]["pdf"]["sha256"] == rebuilt_pdf_hash, manifest["files"]["pdf"]["sha256"], rebuilt_pdf_hash)
    pdf_meta = verification.get("pdf", {})
    audit.check("manifest", "PDF pages", int(pdf_meta.get("pages", -1)) == len(reader.pages), pdf_meta.get("pages"), len(reader.pages))
    audit.check("manifest", "PDF size", int(pdf_meta.get("size_bytes", -1)) == PDF.stat().st_size, pdf_meta.get("size_bytes"), PDF.stat().st_size)
    audit.check("manifest", "PDF rendered pages", int(pdf_meta.get("rendered_pages", -1)) == len(rendered_hashes), pdf_meta.get("rendered_pages"), len(rendered_hashes))

    public = {
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-146"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-146"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "T-050 task": (REPO / "todo/todo.json", "R-146"),
        "changelog": (REPO / "CHANGELOG.md", "R-146"),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-146"),
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
            identity = f"{child_name}:{row.get('category', row.get('group'))}::{row.get('name')}"
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('category', row.get('group'))}",
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                }
            )
    audit.check("aggregation", "child identities unique", duplicates == [], duplicates, [])
    integrator_only = len(audit.rows)
    all_rows = child_rows + audit.rows
    failed = sum(row["status"] != "PASS" for row in all_rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": __version_issued__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "tier": "T4",
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(all_rows),
            "passed": len(all_rows) - failed,
            "failed": failed,
            "rows": all_rows,
        },
        "assertion_accounting": {
            "embedded_child_assertions": len(child_rows),
            "integrator_only_assertions": integrator_only,
            "unique_package_assertions": len(all_rows),
        },
        "children": {
            "primary": {
                "path": relative(PRIMARY_OUTPUT),
                "sha256": sha256(PRIMARY_OUTPUT),
                "assertions": assertion_total(primary),
                "stdout": primary_run.stdout,
            },
            "independent": {
                "path": relative(INDEPENDENT_OUTPUT),
                "sha256": sha256(INDEPENDENT_OUTPUT),
                "assertions": assertion_total(independent),
                "stdout": independent_run.stdout,
            },
        },
        "source_hashes": {
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "verifier": sha256(Path(__file__)),
            "note": sha256(NOTE),
            "pdf": rebuilt_pdf_hash,
            "manifest": sha256(MANIFEST),
            "authorities": authority_hashes,
        },
        "pdf_audit": {
            "path": relative(PDF),
            "sha256": rebuilt_pdf_hash,
            "size_bytes": PDF.stat().st_size,
            "pages": len(reader.pages),
            "deterministic_rebuild": True,
            "form_check": True,
            "overfull_hbox_count": 0,
            "security_findings": security_findings,
            "renderer": "Poppler pdftoppm",
            "dpi": 130,
            "rendered_pages": len(rendered_hashes),
            "page_sha256": rendered_hashes,
            "manual_visual_qa": manifest["verification"]["pdf"]["manual_visual_qa"],
        },
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
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
