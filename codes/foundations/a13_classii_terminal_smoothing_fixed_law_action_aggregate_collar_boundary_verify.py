#!/usr/bin/env python3
"""Integrated authority, PDF, ledger, and surface audit for A13 R-134."""

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
import math
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
RESULT_ID = "A13-CLASSII-TERMINAL-SMOOTHING-FIXED-LAW-ACTION-AGGREGATE-COLLAR-BOUNDARY"
SUCCESSOR_ID = "A13-CLASSII-SIGNED-FOREST-TERMINAL-INNOVATION-ONE-USE-HEADROOM-BOUND"
SCHEMA = "tect/a13-terminal-smoothing-fixed-law-action-aggregate-collar-boundary-integrated/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_terminal_smoothing_fixed_law_action_aggregate_collar_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_terminal_smoothing_fixed_law_action_aggregate_collar_boundary_independent.py"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-31-primary-terminal-smoothing-fixed-law-action-aggregate-collar-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-31-independent-terminal-smoothing-fixed-law-action-aggregate-collar-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-31-integrated-terminal-smoothing-fixed-law-action-aggregate-collar-boundary/result.json"
NOTE = CLAIM_DIR / "notes/classii-terminal-smoothing-fixed-law-action-aggregate-collar-boundary-260731-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(514, 525)}
EXPECTED_NEGATIVES = {
    "NG-2026-07-31-A13-ELLIPTIC-GAUSSIAN-D4-FLOOR-UNIFORMITY",
    "NG-2026-07-31-A13-SEPARATE-FLOOR-WEIGHTED-CURRENT-ENERGY-ABSORPTION",
    "NG-2026-07-31-A13-POINTWISE-ELLIPTICITY-SPATIAL-FRACTIONAL-TRANSFER",
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


def pdf_security_audit(reader: PdfReader) -> dict[str, Any]:
    findings: list[str] = []
    visited: set[tuple[int, int]] = set()
    unsafe_actions = {
        "/JavaScript", "/Launch", "/GoToR", "/SubmitForm", "/ImportData",
        "/Rendition", "/Movie", "/Sound", "/URI",
    }
    unsafe_keys = {
        "/JS", "/JavaScript", "/AA", "/Launch", "/AF", "/EF",
        "/EmbeddedFiles", "/RichMedia", "/Movie", "/Sound", "/XFA",
        "/SubmitForm", "/ImportData",
    }

    def resolve(value: Any) -> Any:
        return value.get_object() if isinstance(value, IndirectObject) else value

    def visit(value: Any, path: str) -> None:
        if isinstance(value, IndirectObject):
            marker = (value.idnum, value.generation)
            if marker in visited:
                return
            visited.add(marker)
            value = value.get_object()
        if isinstance(value, DictionaryObject):
            action = resolve(value.get("/S"))
            if str(action) in unsafe_actions:
                findings.append(f"{path}/S={action}")
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
    for page_index, page in enumerate(reader.pages, start=1):
        annotations = resolve(page.get("/Annots")) or []
        for annotation_index, annotation in enumerate(annotations):
            annotation = resolve(annotation)
            subtype = str(resolve(annotation.get("/Subtype")))
            if subtype == "/Widget":
                widget_count += 1
            if subtype in {"/FileAttachment", "/RichMedia", "/Movie", "/Sound"}:
                findings.append(f"page-{page_index}/annot-{annotation_index}:{subtype}")
    return {
        "findings": sorted(set(findings)),
        "open_action": open_action_kind,
        "safe_open_action": safe_open_action,
        "widget_count": widget_count,
    }


def find_pdftoppm() -> Path | None:
    runtime = Path.home() / ".cache" / "codex-runtimes"
    candidates = [
        runtime / "codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"
    ]
    candidates.extend(runtime.glob("*/dependencies/native/poppler/Library/bin/pdftoppm.exe"))
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
    return run.returncode, "\n".join((run.stdout, run.stderr)).strip(), sorted(output_dir.glob("page-*.png"))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.identifiers: set[str] = set()

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        identifier = f"{group}::{name}"
        if identifier in self.identifiers:
            raise ValueError(f"duplicate assertion identifier: {identifier}")
        self.identifiers.add(identifier)
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": actual,
            "expected": expected,
        })


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
        ("primary", primary, 44),
        ("independent", independent, 35),
    ):
        audit.check("children", f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS")
        audit.check("children", f"{label}_claim", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM)
        audit.check("children", f"{label}_result", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID)
        audit.check("children", f"{label}_count", payload.get("assertions_total") == count, payload.get("assertions_total"), count)
        audit.check("children", f"{label}_no_failures", payload.get("assertions_failed") == 0, payload.get("assertions_failed"), 0)
        for field in (
            "production_terminal_ellipticity",
            "production_signed_forest_bound" if label == "primary" else "production_signed_forest",
            "production_one_use_q_ledger",
            "sector_a_closed",
        ):
            audit.check("scope", f"{label}_{field}", payload.get("scope", {}).get(field) is False, payload.get("scope", {}).get(field), False)

    source = INDEPENDENT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    audit.check("children", "independent_nonimporting", PRIMARY.name not in source and not any("terminal_smoothing_fixed_law_action" in item for item in imports), {"imports": sorted(imports)}, "primary import/read absent")
    audit.check("children", "independent_no_sympy", "sympy" not in imports, sorted(imports), "sympy absent")

    pdiag = primary["diagnostics"]
    idiag = independent["diagnostics"]
    audit.check("cross", "alpha", pdiag["inputs"]["alpha"] == idiag["inputs"]["alpha"] == "5/9", {"primary": pdiag["inputs"]["alpha"], "independent": idiag["inputs"]["alpha"]}, "5/9")
    audit.check("cross", "beta_operator", pdiag["inputs"]["beta_operator"] == idiag["inputs"]["beta_operator"], pdiag["inputs"]["beta_operator"], idiag["inputs"]["beta_operator"])
    audit.check("cross", "sharp_floor_constant", pdiag["fixed_law_action"]["remainder_norm_squared_coefficient"] == idiag["inputs"]["sharp_floor_constant"], pdiag["fixed_law_action"]["remainder_norm_squared_coefficient"], idiag["inputs"]["sharp_floor_constant"])
    audit.check("cross", "q_comp_fixture", abs(float(pdiag["finite_moment_no_go"]["q_comp"]) - float(idiag["finite_moment_no_go"]["q_comp"])) < 2e-9, pdiag["finite_moment_no_go"]["q_comp"], idiag["finite_moment_no_go"]["q_comp"])
    audit.check("cross", "q2", pdiag["six_real_smoothing"]["q2"] == "1/4" and abs(float(idiag["six_real_smoothing"]["q2_quadrature"]) - 0.25) < 2e-8, {"primary": pdiag["six_real_smoothing"]["q2"], "independent": idiag["six_real_smoothing"]["q2_quadrature"]}, "1/4")
    audit.check("cross", "q4", pdiag["six_real_smoothing"]["q4"] == "1/8" and abs(float(idiag["six_real_smoothing"]["q4_quadrature"]) - 0.125) < 2e-7, {"primary": pdiag["six_real_smoothing"]["q4"], "independent": idiag["six_real_smoothing"]["q4_quadrature"]}, "1/8")
    audit.check("cross", "d2_l2", pdiag["six_real_smoothing"]["d2f_l2_over_lambda"] == "49" and idiag["six_real_smoothing"]["d2_l2_over_lambda"] == 49.0, {"primary": pdiag["six_real_smoothing"]["d2f_l2_over_lambda"], "independent": idiag["six_real_smoothing"]["d2_l2_over_lambda"]}, "49")
    audit.check("cross", "d3_l2", pdiag["six_real_smoothing"]["d3f_l2_over_lambda_squared"] == "3249/2" and idiag["six_real_smoothing"]["d3_l2_over_lambda_squared"] == 3249.0 / 2.0, {"primary": pdiag["six_real_smoothing"]["d3f_l2_over_lambda_squared"], "independent": idiag["six_real_smoothing"]["d3_l2_over_lambda_squared"]}, "3249/2")
    primary_fpp_l1 = float(Fraction(pdiag["density_repair"]["fpp_l1"]))
    independent_delta = float(idiag["finite_moment_no_go"]["delta"])
    expected_sfpp_l1 = 5.0 * math.sqrt(3.0) * independent_delta / 6.0
    audit.check("cross", "density_fpp_l1", abs(primary_fpp_l1 - float(idiag["density_repair"]["fpp_l1"])) < 2e-14, {"primary": pdiag["density_repair"]["fpp_l1"], "independent": idiag["density_repair"]["fpp_l1"]}, "25/18")
    audit.check("cross", "density_sfpp_l1", pdiag["density_repair"]["s_fpp_l1"] == "5*sqrt(3)*delta/6" and abs(float(idiag["density_repair"]["s_fpp_l1"]) - expected_sfpp_l1) < 2e-14, {"primary": pdiag["density_repair"]["s_fpp_l1"], "independent": idiag["density_repair"]["s_fpp_l1"]}, "5sqrt(3)delta/6")
    audit.check("cross", "pointwise_ellipticity_spatial_boundary", pdiag["fractional_route"]["pointwise_ellipticity_alone_controls_spatial_fractional_norm"] is False and idiag["fractional_route"]["pointwise_ellipticity_alone_controls_spatial_fractional_norm"] is False, {"primary": pdiag["fractional_route"]["pointwise_ellipticity_alone_controls_spatial_fractional_norm"], "independent": idiag["fractional_route"]["pointwise_ellipticity_alone_controls_spatial_fractional_norm"]}, False)
    for p_key, i_key, expected in (
        ("conditional_B_constant_decimal", "B_constant", 0.6588816258726145),
        ("conditional_B_amplitude_decimal", "B_amplitude", 0.811715236935106),
        ("direct_fixed_collar_constant_decimal", "direct_constant", 0.28592888585547915),
        ("direct_fixed_collar_amplitude_decimal", "direct_amplitude", 0.534723186195885),
    ):
        p_value = float(pdiag["aggregate_shell"][p_key])
        i_value = float(idiag["aggregate_shell"][i_key])
        audit.check("cross", p_key, abs(p_value - i_value) < 2e-15 and abs(p_value - expected) < 2e-15, {"primary": p_value, "independent": i_value}, expected)
    audit.check("cross", "separate_absorption", pdiag["separate_absorption"]["standalone_A2_plus_eB2_absorption"] is False and idiag["separate_absorption"]["cutoff_uniform_bound"] is False, {"primary": pdiag["separate_absorption"]["standalone_A2_plus_eB2_absorption"], "independent": idiag["separate_absorption"]["cutoff_uniform_bound"]}, False)

    note_text = NOTE.read_text(encoding="utf-8")
    note_norm = normalized(note_text)
    audit.check("note", "english_ascii", note_text.isascii(), note_text.isascii(), True)
    phrases = (
        RESULT_ID,
        "Sharp six-row floor decomposition",
        "Root- and visit-free direct action inequality",
        "Uniform finite-moment caps do not repair fixed-law curvature",
        "Sharp six-real Gaussian negative moments",
        "Normalized quotient jet threshold",
        "Conditional fractional",
        "Conditional one-use square summation",
        "Why separate action payments diverge",
        "Absolute terminal packet and production scope",
        "Devil's-advocate review",
        "Proof complete: false. Sector A closed: false.",
    )
    for index, phrase in enumerate(phrases, start=1):
        present = normalized(phrase) in note_norm
        audit.check("note", f"phrase_{index:02d}", present, present, True)

    pdf_env = os.environ.copy()
    issued_utc = datetime.strptime(__version_issued__, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    pdf_env["SOURCE_DATE_EPOCH"] = str(int(issued_utc.timestamp()))
    pdf_env["FORCE_SOURCE_DATE"] = "1"
    build_command = [sys.executable, str(REPO / "verification/scripts/build_note_pdf.py"), str(NOTE)]
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
    audit.check("pdf", "all_pages_nonblank", all(len(page.strip()) >= 20 for page in extracted_pages), [len(page.strip()) for page in extracted_pages], "all>=20")
    audit.check("pdf", "no_fields", not fields, sorted(fields), [])
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check("pdf", "r134_extracted", "R-134" in extracted, "R-134" in extracted, True)
    security = pdf_security_audit(reader)
    audit.check("pdf", "safe_open_action", security["safe_open_action"], security["open_action"], "absent, destination-array, or /GoTo")
    audit.check("pdf", "no_unsafe_features", not security["findings"], security["findings"], [])
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)

    internal = REPO / "internal"
    internal.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r134-render-", dir=internal) as temporary:
        render_exit, render_log, images = render_pdf(PDF, Path(temporary))
        page_hashes = [digest(image) for image in images]
        audit.check("pdf", "render_exit", render_exit == 0, {"exit": render_exit, "log": render_log}, 0)
        audit.check("pdf", "render_count", len(images) == len(reader.pages), len(images), len(reader.pages))

    explorations: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            explorations[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = explorations.get(identifier)
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
    audit.check("surface", "status_statement", "R-134" in status.get("statement", ""), "R-134" in status.get("statement", ""), True)
    audit.check("surface", "status_next", SUCCESSOR_ID in status.get("next_action", ""), status.get("next_action"), SUCCESSOR_ID)
    audit.check("surface", "status_sector_open", "sector a" in status.get("no_overclaim", "").lower() or "sector-a" in status.get("no_overclaim", "").lower(), status.get("no_overclaim"), "Sector A remains open")

    contracts = (
        ("claim", CLAIM_DIR / "claim.md", ("R-134", RESULT_ID, "EXP-000514--EXP-000524")),
        ("results_ledger", REPO / "RESULTS-LEDGER.md", ("### R-134", RESULT_ID)),
        ("todo", REPO / "todo/todo.json", ("T-050", "R-134", SUCCESSOR_ID)),
        ("changelog_source", REPO / "changelog/log.jsonl", ("R-134", "classii-terminal-smoothing-fixed-law-action-aggregate-collar-boundary")),
        ("changelog_render", REPO / "CHANGELOG.md", ("R-134", "six-real")),
        ("claims_render", REPO / "CLAIMS.md", (CLAIM, "T4")),
        ("proof_map", REPO / "theory/proof-evidence-map.md", ("R-134", "EXP-000521", "classii-terminal-smoothing-fixed-law-action-aggregate-collar-boundary")),
        ("proof_map_json", REPO / "verification/proof-evidence-map.json", (RESULT_ID, "EXP-000521")),
        ("catalog", REPO / "CATALOG.md", ("classii-terminal-smoothing-fixed-law-action-aggregate-collar-boundary",)),
        ("catalog_json", REPO / "verification/catalog.json", ("classii-terminal-smoothing-fixed-law-action-aggregate-collar-boundary",)),
    )
    for label, path, required in contracts:
        audit.check("surface", f"{label}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for index, phrase in enumerate(required, start=1):
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
            "assertions_total": 44 + 35 + len(audit.rows),
            "assertions_passed": int(primary["assertions_passed"]) + int(independent["assertions_passed"]) + passed,
            "assertions_failed": 44 + 35 + len(audit.rows) - int(primary["assertions_passed"]) - int(independent["assertions_passed"]) - passed,
        },
        "children": {
            "primary": {"path": PRIMARY_RESULT.relative_to(REPO).as_posix(), "sha256": digest(PRIMARY_RESULT), "assertions": 44},
            "independent": {"path": INDEPENDENT_RESULT.relative_to(REPO).as_posix(), "sha256": digest(INDEPENDENT_RESULT), "assertions": 35},
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
            "fixed_law_six_row_action_bridge_proved": True,
            "six_real_subcritical_pointwise_jet_theorem_proved": True,
            "fractional_window_under_joint_spatial_hypotheses_proved": True,
            "pointwise_ellipticity_spatial_transfer_rejected": True,
            "production_joint_value_gradient_hypotheses": False,
            "elliptic_fourth_jet_route_rejected": True,
            "conditional_gamma_7_12_summation_proved": True,
            "production_terminal_ellipticity": False,
            "production_signed_forest": False,
            "production_one_use_q_ledger": False,
            "near_balanced_headroom": False,
            "absolute_anchor": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closed": False,
        },
        "no_overclaim": "R-134 is a scoped T4 action, anti-concentration, jet-threshold, and conditional-shell result. It proves no production terminal reservation, signed forest-current bound, one-use q-ledger, headroom, anchor, Nelson theorem, or Sector A closure.",
    }
    atomic_json(arguments.output, payload)
    print(
        f"R-134 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} integrated; "
        f"aggregate {payload['aggregate']['assertions_passed']}/{payload['aggregate']['assertions_total']}"
    )
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} expected={row['expected']!r}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
