#!/usr/bin/env python3
"""Integrated authority, PDF, ledger, and surface audit for scoped A13 R-133."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction
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
RESULT_ID = "A13-CLASSII-AFFINE-GAUSSIAN-SCORE-FEEDBACK-COLLAR-BOUNDARY"
SUCCESSOR_ID = "A13-CLASSII-BLOCKWISE-SIGNED-SCORE-FOREST-AGGREGATE-COLLAR-BOUND"
SCHEMA = "tect/a13-affine-gaussian-score-feedback-collar-boundary-integrated/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_affine_gaussian_score_feedback_collar_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_affine_gaussian_score_feedback_collar_boundary_independent.py"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-31-primary-affine-gaussian-score-feedback-collar-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-31-independent-affine-gaussian-score-feedback-collar-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-31-integrated-affine-gaussian-score-feedback-collar-boundary/result.json"
NOTE = CLAIM_DIR / "notes/classii-affine-gaussian-score-feedback-collar-boundary-260731-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(504, 514)}
EXPECTED_NEGATIVES = {
    "AUDIT-2026-07-31-A13-R132-POLYNOMIAL-RESPONSE-INTERTWINER-SCOPE",
    "NG-2026-07-31-A13-PREDICTABLE-SCORE-FINITE-ENERGY-TRANSFER",
    "NG-2026-07-31-A13-GAMMA-FOUR-SIXTH-AMPLITUDE-ROUTE",
    "AUDIT-2026-07-31-A13-R132-GAMMA-FOUR-SUCCESSOR-SCOPE",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


def assertion_actual(payload: dict[str, Any], group: str, name: str) -> Any:
    for row in payload.get("assertions", []):
        if row.get("group") == group and row.get("name") == name:
            return row.get("actual")
    raise KeyError(f"missing assertion {group}::{name}")


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
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

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, path: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            try:
                value = value.get_object()
            except Exception as exc:  # pragma: no cover - corrupt-PDF guard
                findings.append(f"{path}:unreadable:{type(exc).__name__}")
                return
        if isinstance(value, DictionaryObject):
            action_type = resolve(value.get("/S"))
            if str(action_type) in unsafe_actions:
                findings.append(f"{path}/S={action_type}")
            for key, child in value.items():
                key_text = str(key)
                if key_text in unsafe_keys:
                    findings.append(f"{path}{key_text}")
                visit(child, f"{path}{key_text}")
        elif isinstance(value, ArrayObject):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    root = resolve(reader.trailer["/Root"])
    visit(root, "/Root")
    open_action = resolve(root.get("/OpenAction"))
    if open_action is None:
        open_action_kind = "absent"
        safe_open_action = True
    elif isinstance(open_action, ArrayObject):
        open_action_kind = "destination-array"
        safe_open_action = True
    elif isinstance(open_action, DictionaryObject):
        open_action_kind = str(resolve(open_action.get("/S")))
        safe_open_action = open_action_kind == "/GoTo"
    else:
        open_action_kind = type(open_action).__name__
        safe_open_action = False

    widget_count = 0
    annotation_findings: list[str] = []
    for page_index, page in enumerate(reader.pages, start=1):
        annotations = resolve(page.get("/Annots")) or []
        for annotation_index, annotation in enumerate(annotations):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widget_count += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                annotation_findings.append(
                    f"page-{page_index}/annot-{annotation_index}:{subtype}"
                )
    return {
        "findings": sorted(set(findings + annotation_findings)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widget_count,
    }


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [
        runtime
        / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(
        runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe")
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    discovered = shutil.which("pdftoppm")
    return Path(discovered) if discovered else None


def render_pdf(pdf: Path, output_dir: Path) -> tuple[int, str, list[Path]]:
    renderer = find_pdftoppm()
    if renderer is None:
        return 127, "pdftoppm unavailable", []
    output_prefix = output_dir / "page"
    run = subprocess.run(
        [str(renderer), "-png", "-r", "130", str(pdf), str(output_prefix)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    images = sorted(output_dir.glob("page-*.png"))
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), images


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.identifiers: set[str] = set()

    def check(
        self, group: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        identifier = f"{group}::{name}"
        if identifier in self.identifiers:
            raise ValueError(f"duplicate assertion identifier: {identifier}")
        self.identifiers.add(identifier)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, script, output in (
        ("primary", PRIMARY, PRIMARY_RESULT),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT),
    ):
        run = run_child(script, output)
        audit.check("children", f"{label}_exit", run.returncode == 0, run.returncode, 0)
        audit.check("children", f"{label}_output", output.is_file(), output.is_file(), True)

    primary = load_json(PRIMARY_RESULT)
    independent = load_json(INDEPENDENT_RESULT)
    for label, payload, count in (
        ("primary", primary, 42),
        ("independent", independent, 38),
    ):
        audit.check("children", f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        audit.check("children", f"{label}_claim", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM)
        audit.check("children", f"{label}_result", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID)
        audit.check("children", f"{label}_count", payload.get("assertions_total") == count, payload.get("assertions_total"), count)
        audit.check("children", f"{label}_no_failures", payload.get("assertions_failed") == 0, payload.get("assertions_failed"), 0)
        scope = payload.get("scope", {})
        for field in (
            "production_one_use_bound",
            "production_c_mix",
            "production_c_far",
            "production_c_bal",
            "absolute_anchor",
            "sector_a_closed",
        ):
            audit.check("scope", f"{label}_{field}", scope.get(field) is False, scope.get(field), False)

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    independent_tree = ast.parse(independent_source)
    imports = {
        alias.name
        for node in ast.walk(independent_tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    audit.check(
        "children",
        "independent_nonimporting",
        PRIMARY.name not in independent_source
        and not any("affine_gaussian_score_feedback" in item for item in imports),
        {"imports": sorted(imports), "primary_name_present": PRIMARY.name in independent_source},
        "primary import/read absent",
    )
    audit.check("children", "independent_no_sympy", "sympy" not in imports, sorted(imports), "sympy absent")

    pdiag = primary["diagnostics"]
    idiag = independent["diagnostics"]
    audit.check("cross", "outer_half", pdiag["affine_score"].get("paired_direct") == "-40/3" and assertion_actual(primary, "affine_score", "combined_owner_identity") == idiag["score"].get("combined_owner_with_outer_half") == "-5/6", {"primary": assertion_actual(primary, "affine_score", "combined_owner_identity"), "independent": idiag["score"].get("combined_owner_with_outer_half")}, "-5/6")
    audit.check("cross", "single_score_l2", pdiag["affine_score"]["single_score_l2_squared"] == idiag["score"]["single_l2_squared"] == "97/12", {"primary": pdiag["affine_score"]["single_score_l2_squared"], "independent": idiag["score"]["single_l2_squared"]}, "97/12")
    audit.check("cross", "pair_score_l2", pdiag["affine_score"]["pair_score_l2_squared"] == idiag["score"]["pair_l2_squared"] == "97/3", {"primary": pdiag["affine_score"]["pair_score_l2_squared"], "independent": idiag["score"]["pair_l2_squared"]}, "97/3")
    audit.check("cross", "common_heat", pdiag["polynomial_response"]["common_heat_gram"] == idiag["polynomial_response"]["common_heat_gram"], pdiag["polynomial_response"]["common_heat_gram"], idiag["polynomial_response"]["common_heat_gram"])
    audit.check("cross", "adapted_defect", pdiag["polynomial_response"]["adapted_covariance_defect_at_lambda_one"] == idiag["polynomial_response"]["adapted_defect"], pdiag["polynomial_response"]["adapted_covariance_defect_at_lambda_one"], idiag["polynomial_response"]["adapted_defect"])
    h4_primary = float(Fraction(pdiag["gamma_four"]["H4_integral"].replace("*pi", "")))
    h4_independent = float(idiag["gamma_four"]["H4_integral_exact_float"] / 3.141592653589793)
    audit.check("cross", "h4_rational_coefficient", abs(h4_primary - h4_independent) < 1e-10, h4_independent, h4_primary)
    audit.check("cross", "sextic_ratio", abs(float(Fraction(pdiag["gamma_four"]["ratio_coefficient"])) - float(idiag["gamma_four"]["sextic_ratio_coefficient"])) < 2e-12, float(Fraction(pdiag["gamma_four"]["ratio_coefficient"])), idiag["gamma_four"]["sextic_ratio_coefficient"])
    for field, expected in (
        ("far_effective_growth_exponent", "41/12"),
        ("mix_effective_growth_exponent", "17/12"),
        ("offset_exponent", "35/12"),
    ):
        independent_field = field.replace("effective_", "")
        audit.check("cross", field, pdiag["aggregate_collar"][field] == idiag["aggregate_collar"][independent_field] == expected, {"primary": pdiag["aggregate_collar"][field], "independent": idiag["aggregate_collar"][independent_field]}, expected)
    audit.check("cross", "strict_integer_example", pdiag["aggregate_collar"]["minimum_integer_example"] == idiag["aggregate_collar"]["strict_integer_example"] == 18, {"primary": pdiag["aggregate_collar"]["minimum_integer_example"], "independent": idiag["aggregate_collar"]["strict_integer_example"]}, 18)

    note_text = NOTE.read_text(encoding="utf-8")
    note_norm = normalized(note_text)
    audit.check("note", "english_ascii", note_text.isascii(), note_text.isascii(), True)
    note_phrases = (
        RESULT_ID,
        "Exact affine common-heat Gaussian score theorem",
        "Exact predictable-feedback divergence theorem",
        "Finite-energy score-transfer no-go and sufficient gate",
        "Polynomial response support and the noncommuting square",
        "Joint rational boundary layer and the",
        "Exact aggregate collar-to-gap theorem",
        "Proof-search evidence map",
        "Devil's-advocate review",
        "Proof complete: false. Sector A closed: false.",
    )
    for index, phrase in enumerate(note_phrases, start=1):
        present = normalized(phrase) in note_norm
        audit.check("note", f"phrase_{index:02d}", present, present, True)

    pdf_env = os.environ.copy()
    issued_utc = datetime.strptime(__version_issued__, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    pdf_env["SOURCE_DATE_EPOCH"] = str(int(issued_utc.timestamp()))
    pdf_env["FORCE_SOURCE_DATE"] = "1"
    build_command = [
        sys.executable,
        str(REPO / "verification/scripts/build_note_pdf.py"),
        str(NOTE),
    ]
    builds = []
    pdf_hashes = []
    for _ in range(2):
        build = subprocess.run(
            build_command,
            cwd=REPO,
            env=pdf_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        builds.append(build)
        pdf_hashes.append(digest(PDF) if PDF.is_file() else None)
    audit.check("pdf", "build_exit", all(build.returncode == 0 for build in builds), [build.returncode for build in builds], [0, 0])
    audit.check("pdf", "form_check", all("FORM-CHECK: PASS" in build.stdout for build in builds), ["FORM-CHECK: PASS" in build.stdout for build in builds], [True, True])
    audit.check("pdf", "overfull_zero", all("OVERFULL-HBOX: 0" in build.stdout for build in builds), ["OVERFULL-HBOX: 0" in build.stdout for build in builds], [True, True])
    audit.check("pdf", "deterministic_rebuild", PDF.is_file() and pdf_hashes[0] == pdf_hashes[1], pdf_hashes, "two identical non-null SHA-256 values")
    reader = PdfReader(str(PDF))
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    fields = reader.get_fields() or {}
    audit.check("pdf", "pages", len(reader.pages) >= 10, len(reader.pages), ">=10")
    audit.check("pdf", "all_pages_nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], "all >=20")
    audit.check("pdf", "no_fields", not fields, sorted(fields), [])
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "result_extracted", RESULT_ID in extracted.replace("\n", "").replace(" ", ""), RESULT_ID in extracted.replace("\n", "").replace(" ", ""), True)
    audit.check("pdf", "r133_extracted", "R-133" in extracted, "R-133" in extracted, True)
    security = pdf_security_audit(reader)
    audit.check("pdf", "safe_open_action", security["safe_open_action"], security["open_action"], "absent, destination-array, or /GoTo")
    audit.check("pdf", "no_unsafe_features", not security["findings"], security["findings"], [])
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)

    with tempfile.TemporaryDirectory(prefix="r133-render-", dir=REPO / "internal") as temporary:
        render_dir = Path(temporary)
        render_exit, render_log, images = render_pdf(PDF, render_dir)
        page_hashes = [digest(image) for image in images]
        audit.check("pdf", "render_exit", render_exit == 0, {"exit": render_exit, "log": render_log}, 0)
        audit.check("pdf", "render_count", len(images) == len(reader.pages), len(images), len(reader.pages))

    exploration_rows: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            exploration_rows[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = exploration_rows.get(identifier)
        audit.check("exploration", f"{identifier}_exists", row is not None, row is not None, True)
        if row is not None:
            audit.check("exploration", f"{identifier}_task", row.get("task_id") == "T-050", row.get("task_id"), "T-050")
            audit.check("exploration", f"{identifier}_claim", CLAIM in row.get("claim_ids", []), row.get("claim_ids", []), CLAIM)
            audit.check("exploration", f"{identifier}_evidence", bool(row.get("evidence_refs")), row.get("evidence_refs"), "nonempty")
            audit.check("exploration", f"{identifier}_boundary", bool(row.get("boundary")), row.get("boundary"), "nonempty")
            audit.check("exploration", f"{identifier}_next", bool(row.get("next_action")), row.get("next_action"), "nonempty")

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in sorted(EXPECTED_NEGATIVES):
        heading = f"### {identifier}"
        audit.check("negative", identifier, heading in registry, heading in registry, True)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("surface", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    audit.check("surface", "status_statement", "R-133" in status.get("statement", ""), "R-133" in status.get("statement", ""), True)
    audit.check("surface", "status_next", SUCCESSOR_ID in status.get("next_action", ""), status.get("next_action"), SUCCESSOR_ID)
    audit.check("surface", "status_no_overclaim", "sector a" in status.get("no_overclaim", "").lower() or "sector-a" in status.get("no_overclaim", "").lower(), status.get("no_overclaim"), "Sector A remains open")

    surface_contracts = (
        ("claim", CLAIM_DIR / "claim.md", ("R-133", RESULT_ID, "EXP-000504--EXP-000513")),
        ("results_ledger", REPO / "RESULTS-LEDGER.md", ("## R-133", RESULT_ID)),
        ("todo", REPO / "todo/todo.json", ("T-050", "R-133", SUCCESSOR_ID)),
        ("changelog_source", REPO / "changelog/log.jsonl", ("R-133", "classii-affine-gaussian-score-feedback-collar-boundary")),
        ("changelog_render", REPO / "CHANGELOG.md", ("R-133", "eleven-page PDF")),
        (
            "claims_render",
            REPO / "CLAIMS.md",
            (CLAIM, "Class-II source, translated model", "T4"),
        ),
        ("proof_map", REPO / "theory/proof-evidence-map.md", ("R-133", "EXP-000513", "classii-affine-gaussian-score-feedback-collar-boundary")),
        ("proof_map_json", REPO / "verification/proof-evidence-map.json", (RESULT_ID, "EXP-000513")),
        ("catalog", REPO / "CATALOG.md", ("classii-affine-gaussian-score-feedback-collar-boundary",)),
        ("catalog_json", REPO / "verification/catalog.json", ("classii-affine-gaussian-score-feedback-collar-boundary",)),
    )
    for label, path, phrases in surface_contracts:
        audit.check("surface", f"{label}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for index, phrase in enumerate(phrases, start=1):
                audit.check("surface", f"{label}_phrase_{index}", phrase in text, phrase in text, True)

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    active = theorem_map.get("active_frontier", {})
    audit.check("surface", "theorem_map_latest", active.get("latest_result_id") == RESULT_ID, active.get("latest_result_id"), RESULT_ID)
    audit.check("surface", "theorem_map_successor", SUCCESSOR_ID in active.get("success_condition", ""), active.get("success_condition"), SUCCESSOR_ID)

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(audit.rows) else "FAIL",
        "assertions_total": len(audit.rows),
        "assertions_passed": passed,
        "assertions_failed": len(audit.rows) - passed,
        "assertions": audit.rows,
        "aggregate": {
            "assertions_total": 42 + 38 + len(audit.rows),
            "assertions_passed": int(primary["assertions_passed"]) + int(independent["assertions_passed"]) + passed,
            "assertions_failed": 42 + 38 + len(audit.rows) - int(primary["assertions_passed"]) - int(independent["assertions_passed"]) - passed,
        },
        "children": {
            "primary": {"path": PRIMARY_RESULT.relative_to(REPO).as_posix(), "sha256": digest(PRIMARY_RESULT), "assertions": 42},
            "independent": {"path": INDEPENDENT_RESULT.relative_to(REPO).as_posix(), "sha256": digest(INDEPENDENT_RESULT), "assertions": 38},
        },
        "note": {"path": NOTE.relative_to(REPO).as_posix(), "sha256": digest(NOTE)},
        "pdf": {
            "path": PDF.relative_to(REPO).as_posix(),
            "sha256": digest(PDF),
            "size_bytes": PDF.stat().st_size,
            "pages": len(reader.pages),
            "overfull_hbox_count": 0,
            "page_sha256_130dpi": page_hashes,
            "security": security,
        },
        "exploration_ids": sorted(EXPECTED_EXPLORATIONS),
        "negative_results": sorted(EXPECTED_NEGATIVES),
        "scope": {
            "affine_gaussian_score_identity_proved": True,
            "predictable_feedback_score_identity_proved_on_cylindrical_core": True,
            "finite_energy_global_score_transfer_from_declared_data_rejected": True,
            "conditional_polynomial_response_zero_proved": True,
            "sixth_amplitude_gamma_four_route_rejected": True,
            "aggregate_positive_gamma_collar_criterion_proved": True,
            "production_one_use_bound": False,
            "production_c_mix": False,
            "production_c_far": False,
            "production_c_bal": False,
            "absolute_anchor": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closed": False,
        },
        "no_overclaim": "R-133 is a scoped T4 score, feedback, support, method-no-go, and conditional-collar result. It proves no production one-use estimate, absolute anchor, Nelson theorem, or Sector A closure.",
    }
    atomic_json(arguments.output, payload)
    print(
        f"R-133 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} integrated; "
        f"aggregate {payload['aggregate']['assertions_passed']}/"
        f"{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(
                    f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} "
                    f"expected={row['expected']!r}"
                )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
