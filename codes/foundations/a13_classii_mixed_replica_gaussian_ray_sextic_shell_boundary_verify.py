#!/usr/bin/env python3
"""Integrated verifier for the scoped A13 R-132 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY"
SCHEMA = "tect/a13-mixed-replica-gaussian-ray-sextic-shell-boundary-integrated/1.0"
PRIMARY = REPO / "codes/foundations/a13_classii_mixed_replica_gaussian_ray_sextic_shell_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_mixed_replica_gaussian_ray_sextic_shell_boundary_independent.py"
PRIMARY_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-mixed-replica-gaussian-ray-sextic-shell-boundary/result.json"
)
INDEPENDENT_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-mixed-replica-gaussian-ray-sextic-shell-boundary/result.json"
)
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-integrated-mixed-replica-gaussian-ray-sextic-shell-boundary/result.json"
)
NOTE = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/notes/"
    "classii-mixed-replica-gaussian-ray-sextic-shell-boundary-260731-v1.0.tex.txt"
)
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(496, 504)}
EXPECTED_NEGATIVES = {
    "NG-2026-07-31-A13-DIAGONAL-HEAT-SEXTIC-TO-MIXED-RESPONSE",
    "NG-2026-07-31-A13-LAW-FREE-MIXED-RESPONSE-FLOOR-UNIFORMITY",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    for label, script, output in (
        ("primary", PRIMARY, PRIMARY_RESULT),
        ("independent", INDEPENDENT, INDEPENDENT_RESULT),
    ):
        run = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        audit.check("child", f"{label}_exit", run.returncode == 0, run.returncode, 0)
        audit.check("child", f"{label}_output", output.is_file(), output.is_file(), True)

    primary = load_json(PRIMARY_RESULT)
    independent = load_json(INDEPENDENT_RESULT)
    audit.check("child", "primary_status", primary.get("status") == "PASS", primary.get("status"), "PASS")
    audit.check("child", "independent_status", independent.get("status") == "PASS", independent.get("status"), "PASS")
    audit.check("child", "primary_count", primary.get("assertions_total") == 36, primary.get("assertions_total"), 36)
    audit.check("child", "independent_count", independent.get("assertions_total") == 23, independent.get("assertions_total"), 23)
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check("child", f"{label}_claim", child.get("claim_id") == CLAIM, child.get("claim_id"), CLAIM)
        audit.check("child", f"{label}_result", child.get("result_id") == RESULT_ID, child.get("result_id"), RESULT_ID)
        scope = child.get("scope", {})
        for field in ("production_owner_complete_form_constructed", "production_c_mix", "production_c_far", "production_c_bal", "absolute_anchor", "sector_a_closed"):
            audit.check("scope", f"{label}_{field}", scope.get(field) is False, scope.get(field), False)

    primary_diag = primary["diagnostics"]["diagonal_heat_sextic"]
    independent_diag = independent["diagnostics"]["diagonal_heat_sextic"]
    audit.check("cross", "radius", primary_diag["radius"] == independent_diag["radius"], primary_diag["radius"], independent_diag["radius"])
    audit.check("cross", "global_constant", abs(float(Fraction(primary_diag["global_constant"])) - float(independent_diag["global_constant"])) < 1e-15, primary_diag["global_constant"], independent_diag["global_constant"])
    primary_margin = float(primary["diagnostics"]["standard_gaussian_ray"]["source_sextic_margin_decimal"])
    independent_margin = float(independent["diagnostics"]["gaussian_ray"]["source_sextic_margin"])
    audit.check("cross", "gaussian_margin", abs(primary_margin - independent_margin) < 1e-13, primary_margin, independent_margin)
    audit.check("cross", "gaussian_margin_positive", primary_margin > 0.75, primary_margin, ">0.75")
    audit.check("cross", "origin_mean_zero", primary["diagnostics"]["mixed_cancellation"]["mean_xi_at_origin"] == ["0", "0", "0", "0"], primary["diagnostics"]["mixed_cancellation"]["mean_xi_at_origin"], ["0", "0", "0", "0"])
    audit.check("cross", "independent_origin_residual", independent["diagnostics"]["mixed_origin_mean_residual"] < 1e-14, independent["diagnostics"]["mixed_origin_mean_residual"], "<1e-14")

    note_text = NOTE.read_text(encoding="utf-8")
    audit.check("note", "english_ascii", note_text.isascii(), note_text.isascii(), True)
    for token in (RESULT_ID, "paired-replica polarization", "Standard-Gaussian score transfer", "No-overclaim footer", "Proof complete: false"):
        audit.check("note", token[:24], token in note_text, token in note_text, True)

    build = subprocess.run(
        [sys.executable, str(REPO / "verification/scripts/build_note_pdf.py"), str(NOTE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    audit.check("pdf", "build_exit", build.returncode == 0, build.returncode, 0)
    audit.check("pdf", "overfull_zero", "OVERFULL-HBOX: 0" in build.stdout, "OVERFULL-HBOX: 0" in build.stdout, True)
    audit.check("pdf", "exists", PDF.is_file(), PDF.is_file(), True)
    page_count = 0
    fields: dict[str, Any] = {}
    encrypted = None
    extracted = ""
    if PDF.is_file():
        reader = PdfReader(str(PDF))
        page_count = len(reader.pages)
        fields = reader.get_fields() or {}
        encrypted = reader.is_encrypted
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "pages", page_count >= 8, page_count, ">=8")
    audit.check("pdf", "no_fields", not fields, sorted(fields), [])
    audit.check("pdf", "not_encrypted", encrypted is False, encrypted, False)
    audit.check("pdf", "claim_extracted", CLAIM in extracted.replace("\n", ""), CLAIM in extracted.replace("\n", ""), True)
    audit.check("pdf", "r132_extracted", "R-132" in extracted, "R-132" in extracted, True)

    exploration_rows: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            exploration_rows[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = exploration_rows.get(identifier)
        audit.check("exploration", identifier, row is not None, row is not None, True)
        if row is not None:
            audit.check("exploration", f"{identifier}_task", row.get("task_id") == "T-050", row.get("task_id"), "T-050")
            audit.check("exploration", f"{identifier}_claim", CLAIM in row.get("claim_ids", []), row.get("claim_ids", []), CLAIM)

    registry = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in sorted(EXPECTED_NEGATIVES):
        audit.check("negative", identifier, identifier in registry, identifier in registry, True)

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
        "children": {
            "primary": {"path": PRIMARY_RESULT.relative_to(REPO).as_posix(), "sha256": digest(PRIMARY_RESULT), "assertions": primary.get("assertions_total")},
            "independent": {"path": INDEPENDENT_RESULT.relative_to(REPO).as_posix(), "sha256": digest(INDEPENDENT_RESULT), "assertions": independent.get("assertions_total")},
        },
        "note": {"path": NOTE.relative_to(REPO).as_posix(), "sha256": digest(NOTE)},
        "pdf": {"path": PDF.relative_to(REPO).as_posix(), "sha256": digest(PDF), "size_bytes": PDF.stat().st_size, "pages": page_count, "overfull_hbox_count": 0},
        "exploration_ids": sorted(EXPECTED_EXPLORATIONS),
        "negative_results": sorted(EXPECTED_NEGATIVES),
        "scope": {
            "production_owner_complete_form_constructed": False,
            "production_c_mix": False,
            "production_c_far": False,
            "production_c_bal": False,
            "absolute_anchor": False,
            "overlap_src": False,
            "nelson": False,
            "sector_a_closed": False,
        },
        "no_overclaim": "R-132 is a scoped T4 replica, comparison, no-go, Gaussian-ray, and shell-boundary result; production response and Sector A remain open.",
    }
    atomic_json(args.output, payload)
    print(
        f"R-132 integrated {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
