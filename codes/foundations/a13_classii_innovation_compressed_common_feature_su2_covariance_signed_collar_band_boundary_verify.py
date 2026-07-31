#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-142 evidence package.

The verifier reruns both child certificates, checks their independence and
load-bearing values, audits the pinned authorities and exploration records,
rebuilds and renders every PDF page, and checks all generated public surfaces.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

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
    "A13-CLASSII-INNOVATION-COMPRESSED-COMMON-FEATURE-SU2-"
    "COVARIANCE-SIGNED-COLLAR-BAND-BOUNDARY"
)
LEDGER_ID = "R-142"
SCHEMA = (
    "tect/a13-innovation-compressed-common-feature-su2-covariance-"
    "signed-collar-band-boundary-integrated/1.0"
)
SLUG = (
    "innovation-compressed-common-feature-su2-covariance-"
    "signed-collar-band-boundary"
)
NOTE = CLAIM_DIR / f"notes/classii-{SLUG}-260731-v1.0.tex.txt"
PDF = NOTE.with_suffix("").with_suffix(".pdf")
PDF_BUILDER = REPO / "verification/scripts/build_note_pdf.py"
MANIFEST = (
    CLAIM_DIR
    / "classii_innovation_compressed_common_feature_su2_covariance_signed_collar_band_boundary_manifest.json"
)
PRIMARY = (
    REPO
    / "codes/foundations/a13_classii_innovation_compressed_common_feature_su2_covariance_signed_collar_band_boundary.py"
)
INDEPENDENT = (
    REPO
    / "codes/foundations/a13_classii_innovation_compressed_common_feature_su2_covariance_signed_collar_band_boundary_independent.py"
)
PRIMARY_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-primary-{SLUG}/result.json"
INDEPENDENT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / f"runs/2026-07-31-integrated-{SLUG}/result.json"
EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(578, 585))
AUTHORITIES = {
    "R-102": (
        CLAIM_DIR
        / "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
        "A13-CLASSII-FULL-HESSIAN-LAPLACE-WICK-FUTURE-FEEDBACK-BOUNDARY",
    ),
    "R-125": (
        CLAIM_DIR
        / "classii_conditional_variance_forest_bridge_root_shell_operator_boundary_manifest.json",
        "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY",
    ),
    "R-132": (
        CLAIM_DIR
        / "classii_mixed_replica_gaussian_ray_sextic_shell_boundary_manifest.json",
        "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY",
    ),
    "R-133": (
        CLAIM_DIR
        / "classii_affine_gaussian_score_feedback_collar_boundary_manifest.json",
        "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY",
    ),
    "R-141": (
        CLAIM_DIR
        / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
        "A13-CLASSII-PROJECTED-FORCE-GLOBAL-DOOB-SIGNED-GRAM-ADAPTIVE-COLLAR-QUOTIENT-BOUNDARY",
    ),
}
A1_AUTHORITY = (
    REPO
    / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
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
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def run_child(script: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
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
    environment["SOURCE_DATE_EPOCH"] = "1785456000"
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


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = list(
        runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe")
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def render_pdf(directory: Path) -> tuple[int, str, list[Path]]:
    renderer = find_pdftoppm()
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
    return (
        run.returncode,
        "\n".join((run.stdout, run.stderr)).strip(),
        sorted(directory.glob("page-*.png")),
    )


def pdf_security(reader: PdfReader) -> list[str]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_keys = {
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
    }
    unsafe_actions = {
        "/JavaScript",
        "/Launch",
        "/GoToR",
        "/SubmitForm",
        "/ImportData",
        "/Rendition",
        "/Movie",
        "/Sound",
        "/URI",
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
    parser.add_argument("--primary-output", type=Path, default=PRIMARY_OUTPUT)
    parser.add_argument("--independent-output", type=Path, default=INDEPENDENT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY, args.primary_output)
    independent_run = run_child(INDEPENDENT, args.independent_output)
    audit.check("children", "primary exits zero", primary_run.returncode == 0, primary_run.returncode, 0)
    audit.check("children", "independent exits zero", independent_run.returncode == 0, independent_run.returncode, 0)
    audit.check("children", "primary output exists", args.primary_output.is_file(), relative(args.primary_output), "file")
    audit.check("children", "independent output exists", args.independent_output.is_file(), relative(args.independent_output), "file")
    primary = load_json(args.primary_output)
    independent = load_json(args.independent_output)
    for name, child in (("primary", primary), ("independent", independent)):
        rows = assertion_rows(child)
        audit.check("children", f"{name} status", child.get("status") == "PASS", child.get("status"), "PASS")
        audit.check("children", f"{name} result id", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        audit.check("children", f"{name} rows all pass", all(row.get("status") == "PASS" for row in rows), [row for row in rows if row.get("status") != "PASS"], [])
        audit.check("children", f"{name} count self-consistent", len(rows) == assertion_total(child), len(rows), assertion_total(child))

    roots, relative_import = imported_roots(INDEPENDENT)
    audit.check("independence", "no relative imports", not relative_import, relative_import, False)
    audit.check("independence", "no numerical libraries", not (roots & {"numpy", "sympy", "scipy"}), sorted(roots & {"numpy", "sympy", "scipy"}), [])
    audit.check("independence", "does not import primary", not any("a13_classii" in root for root in roots), sorted(roots), "no primary")

    p = primary["computed"]
    i = independent["computed"]
    audit.check("cross", "scalar mG agreement", abs(float(p["scalar_translation_lower_bound"]) - float(i["scalar_translation_lower_bound"])) < 2.0e-12, (p["scalar_translation_lower_bound"], i["scalar_translation_lower_bound"]), "within 2e-12")
    audit.check("cross", "lambda c exact agreement", p["scalar_covariance_lower_bound"] == i["scalar_covariance_lower_bound"], (p["scalar_covariance_lower_bound"], i["scalar_covariance_lower_bound"]), "equal")
    audit.check("cross", "commutator agreement", abs(float(p["commutator_norm_squared"]) - float(i["commutator_norm_squared"])) < 2.0e-12, (p["commutator_norm_squared"], i["commutator_norm_squared"]), "within 2e-12")
    audit.check("cross", "mass spectra agreement", max(abs(float(x) - float(y)) for x, y in zip(p["mass_eigenvalues"], i["mass_eigenvalues"])) < 2.0e-12, (p["mass_eigenvalues"], i["mass_eigenvalues"]), "within 2e-12")
    audit.check("cross", "C8 symbols both adverse", float(p["c8_symbol_pi_over_two"]) < 0 and float(i["c8_symbol_pi_over_two"]) < 0, (p["c8_symbol_pi_over_two"], i["c8_symbol_pi_over_two"]), "both negative")
    audit.check("cross", "C10 symbols both adverse", float(p["c10_symbol_pi_over_two"]) < 0 and float(i["c10_symbol_pi_over_two"]) < 0, (p["c10_symbol_pi_over_two"], i["c10_symbol_pi_over_two"]), "both negative")
    audit.check("cross", "coherent carriers agree", p["coherent_carriers"] == i["coherent_carriers"], (p["coherent_carriers"], i["coherent_carriers"]), "equal")

    for key in (
        "full_production_common_feature_matrix_assembled",
        "uniform_production_loewner_bound",
        "scalar_chart_extends_to_transverse_su2",
        "coefficient_band_is_full_owner_counterexample",
        "positive_production_graph_gap",
        "a13_gate_closed",
        "nelson",
        "sector_a_closed",
    ):
        audit.check("scope", f"primary {key} false", primary["scope"].get(key) is False, primary["scope"].get(key), False)
    for key in (
        "full_production_matrix",
        "uniform_production_bound",
        "scalar_to_full_su2",
        "band_to_full_owner_counterexample",
        "a13_gate_closed",
        "nelson",
        "sector_a_closed",
    ):
        audit.check("scope", f"independent {key} false", independent["scope"].get(key) is False, independent["scope"].get(key), False)

    note_text = NOTE.read_text(encoding="utf-8")
    for label, token in (
        ("result id", RESULT_ID),
        ("ledger", "Ledger: R-142"),
        ("purpose", "Purpose and scope"),
        ("compression", "section-2-innovation-compression"),
        ("trace feature", "canonical-actual-trace-feature"),
        ("two feature Hessian", "two-feature-hessian"),
        ("SU2 block", "section-4-su2-fibre"),
        ("covariance split", "section-5-covariance-split"),
        ("scalar chart", "section-6-scalar-chart"),
        ("signed band", "section-7-signed-band"),
        ("evidence map", "section-8-evidence-map"),
        ("devil audit", "Devil's-advocate audit"),
        ("footer", "Result footer"),
    ):
        audit.check("note", label, token in note_text, token in note_text, True)

    manifest = load_json(MANIFEST)
    initial_pdf_hash = sha256(PDF)
    build = build_pdf()
    audit.check("pdf", "build exits zero", build.returncode == 0, (build.returncode, build.stderr), 0)
    audit.check("pdf", "form check", "FORM-CHECK: PASS" in build.stdout, build.stdout, "FORM-CHECK: PASS")
    audit.check("pdf", "zero overfull", "OVERFULL-HBOX: 0" in build.stdout, build.stdout, "OVERFULL-HBOX: 0")
    rebuilt_pdf_hash = sha256(PDF)
    audit.check("pdf", "deterministic rebuild", rebuilt_pdf_hash == initial_pdf_hash, (initial_pdf_hash, rebuilt_pdf_hash), "equal")
    reader = PdfReader(str(PDF))
    page_text = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(page_text)
    audit.check("pdf", "not encrypted", reader.is_encrypted is False, reader.is_encrypted, False)
    audit.check("pdf", "nine pages", len(reader.pages) == 9, len(reader.pages), 9)
    audit.check("pdf", "all pages nonblank", all(len(text.strip()) >= 20 for text in page_text), [len(text.strip()) for text in page_text], ">=20 each")
    audit.check("pdf", "ledger extracts", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    audit.check("pdf", "scope boundary extracts", "Sector-A closure" in extracted, "Sector-A closure" in extracted, True)
    audit.check("pdf", "no replacement glyph", "\ufffd" not in extracted, "\ufffd" in extracted, False)
    audit.check("pdf", "no form fields", reader.get_fields() in (None, {}), reader.get_fields(), None)
    security_findings = pdf_security(reader)
    audit.check("pdf", "no unsafe actions", security_findings == [], security_findings, [])
    with tempfile.TemporaryDirectory(prefix="tect-r142-render-") as temporary:
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
    for exploration_id in EXPLORATION_IDS:
        audit.check("exploration", f"{exploration_id} exists", exploration_id in exploration_records, exploration_id in exploration_records, True)
        record = exploration_records[exploration_id]
        audit.check("exploration", f"{exploration_id} claim", CLAIM in record.get("claim_ids", []), record.get("claim_ids"), CLAIM)
        audit.check("exploration", f"{exploration_id} evidence", len(record.get("evidence_refs", [])) >= 2, len(record.get("evidence_refs", [])), ">=2")
        audit.check("exploration", f"{exploration_id} next", bool(record.get("next_action")), record.get("next_action"), "nonempty")

    authority_hashes: dict[str, str] = {}
    for ledger_id, (path, expected_result) in AUTHORITIES.items():
        audit.check("authority", f"{ledger_id} exists", path.is_file(), relative(path), "file")
        authority = load_json(path)
        audit.check("authority", f"{ledger_id} result", authority.get("result_id") == expected_result, authority.get("result_id"), expected_result)
        audit.check("authority", f"{ledger_id} claim", authority.get("claim_id") == CLAIM, authority.get("claim_id"), CLAIM)
        authority_hashes[ledger_id] = sha256(path)
    a1 = load_json(A1_AUTHORITY)
    parameters = a1.get("parameters", {})
    audit.check("authority", "A1 claim id", a1.get("claim_id") == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1.get("claim_id"), "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    audit.check("authority", "A1 family masses", parameters.get("family_masses") == [0.0, 0.03, 0.07], parameters.get("family_masses"), [0.0, 0.03, 0.07])
    audit.check("authority", "A1 lock", parameters.get("k_lock") == 0.15, parameters.get("k_lock"), 0.15)
    audit.check("authority", "A1 lock vector", parameters.get("z0") == [1.0, 1.0, 1.0], parameters.get("z0"), [1.0, 1.0, 1.0])
    authority_hashes["A1"] = sha256(A1_AUTHORITY)

    audit.check("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger id", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID)
    audit.check("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    audit.check("manifest", "Sector A open", manifest.get("sector_a_closed") is False, manifest.get("sector_a_closed"), False)
    audit.check("manifest", "manual visual QA", str(manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa", "")).startswith("PASS"), manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa"), "PASS*")
    audit.check("manifest", "exploration ids", set(EXPLORATION_IDS) <= set(manifest.get("exploration_ids", [])), sorted(set(EXPLORATION_IDS) - set(manifest.get("exploration_ids", []))), [])
    expected_files = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": Path(__file__),
        "note": NOTE,
        "pdf": PDF,
        "primary_result": args.primary_output,
        "independent_result": args.independent_output,
    }
    for key, path in expected_files.items():
        entry = manifest.get("files", {}).get(key, {})
        audit.check("manifest", f"{key} path", str(entry.get("path", "")).replace("\\", "/") == relative(path), entry.get("path"), relative(path))
        audit.check("manifest", f"{key} hash", entry.get("sha256") == sha256(path), entry.get("sha256"), sha256(path))
    verification = manifest.get("verification", {})
    audit.check("manifest", "primary assertion count", int(verification.get("primary_assertions", -1)) == assertion_total(primary), verification.get("primary_assertions"), assertion_total(primary))
    audit.check("manifest", "independent assertion count", int(verification.get("independent_assertions", -1)) == assertion_total(independent), verification.get("independent_assertions"), assertion_total(independent))
    audit.check("manifest", "PDF hash", manifest.get("files", {}).get("pdf", {}).get("sha256") == rebuilt_pdf_hash, manifest.get("files", {}).get("pdf", {}).get("sha256"), rebuilt_pdf_hash)

    public = {
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-142"></a>'),
        "claim status": (CLAIM_DIR / "status.json", RESULT_ID),
        "claim chronology": (CLAIM_DIR / "claim.md", "R-142"),
        "lineage": (CLAIM_DIR / "LINEAGE.md", SLUG),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", RESULT_ID),
        "task ledger": (REPO / "todo/todo.json", "R-142"),
        "changelog": (REPO / "CHANGELOG.md", "R-142"),
        "proof map": (REPO / "theory/proof-evidence-map.md", "R-142"),
        "catalog": (REPO / "CATALOG.md", MANIFEST.name),
    }
    for name, (path, token) in public.items():
        audit.check("surface", f"{name} file", path.is_file(), relative(path), "file")
        text = path.read_text(encoding="utf-8")
        audit.check("surface", name, token in text, token in text, True)

    child_rows: list[dict[str, object]] = []
    identities: set[str] = set()
    duplicates: list[str] = []
    for child_name, child in (("primary", primary), ("independent", independent)):
        for row in assertion_rows(child):
            identity = f"{child_name}:{row.get('group')}::{row.get('name')}"
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
            child_rows.append(
                {
                    "group": f"{child_name}:{row.get('group')}",
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
        "result_id": RESULT_ID,
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
                "path": relative(args.primary_output),
                "sha256": sha256(args.primary_output),
                "assertions": assertion_total(primary),
                "stdout": primary_run.stdout,
            },
            "independent": {
                "path": relative(args.independent_output),
                "sha256": sha256(args.independent_output),
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
            "manual_visual_qa": manifest.get("verification", {}).get("pdf", {}).get("manual_visual_qa"),
        },
        "scope": {
            "full_production_matrix": False,
            "uniform_production_bound": False,
            "positive_graph_gap": False,
            "a13_gate_closed": False,
            "nelson": False,
            "sector_a_closed": False,
        },
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
