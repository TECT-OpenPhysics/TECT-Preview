#!/usr/bin/env python3
"""Integrated fail-closed verifier for the scoped R-116 A13 boundary."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import argparse
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
RESULT_ID = "A13-CLASSII-ONE-FRESH-ROOT-OWNER-QUOTIENT-WICK-NULLCONE-BOUNDARY"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_one_fresh_root_owner_quotient_wick_nullcone_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-one-fresh-root-owner-quotient-wick-nullcone-boundary-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-one-fresh-root-owner-quotient-wick-nullcone-boundary-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_one_fresh_root_owner_quotient_wick_nullcone_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-one-fresh-root-owner-quotient-wick-nullcone-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-one-fresh-root-owner-quotient-wick-nullcone-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-one-fresh-root-owner-quotient-wick-nullcone-boundary/result.json"

PRIMARY_SCHEMA = "tect/a13-one-fresh-root-owner-quotient-wick-nullcone-boundary-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-one-fresh-root-owner-quotient-wick-nullcone-boundary-independent/1.0"
INTEGRATED_SCHEMA = "tect/a13-one-fresh-root-owner-quotient-wick-nullcone-boundary-integrated/1.0"
PRIMARY_ASSERTIONS = 30
INDEPENDENT_ASSERTIONS = 23

NOTE_TOKENS = (
    "R-116",
    RESULT_ID,
    "Theorem 2.1 (same-root visit endpoint quotient)",
    "Theorem 5.1 (exact parabolic-tangent recession)",
    "Proposition 6.1 (exactly centered quadratic null-cone divergence)",
    "Theorem 7.1 (pointwise and finite-Fourier null classification)",
    "metric error bound",
    "30/30",
    "23/23",
    "Sector-A closure",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": INTEGRATED_SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "children": {
                "primary": {"path": relative(PRIMARY_RESULT), "sha256": digest(PRIMARY_RESULT)},
                "independent": {"path": relative(INDEPENDENT_RESULT), "sha256": digest(INDEPENDENT_RESULT)},
            },
            "no_overclaim": (
                "Integrated PASS certifies the scoped R-116 identities, tail classifier, "
                "and method boundaries only.  Full A1 progressive/revisit normalization, "
                "one-use source/sextic aggregation, and Sector A remain open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r116-child-") as directory:
        output = Path(directory) / "result.json"
        try:
            process = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            return {"status": "EXECUTION_ERROR", "error": str(error)}, "", str(error)
        if process.returncode != 0:
            return {"status": "EXECUTION_ERROR", "returncode": process.returncode}, process.stdout, process.stderr
        if not output.is_file():
            return {"status": "MISSING_OUTPUT"}, process.stdout, process.stderr
        return load_json(output), process.stdout, process.stderr


def child_contract(
    audit: Audit,
    name: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    assertions: int,
) -> None:
    audit.check("child", f"{name}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{name}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{name}_result_id", fresh.get("result_id") == RESULT_ID, fresh.get("result_id"), RESULT_ID)
    audit.check("child", f"{name}_assertions", fresh.get("assertions_total") == assertions, fresh.get("assertions_total"), assertions)
    audit.check("child", f"{name}_all_passed", fresh.get("assertions_passed") == assertions, fresh.get("assertions_passed"), assertions)
    audit.check("child", f"{name}_deterministic_payload", fresh == stored, digest_payload(fresh), digest_payload(stored))


def digest_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_manifest(audit: Audit, manifest: dict[str, Any], pages: int) -> None:
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "claim_id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    audit.check("manifest", "tier_boundary", "T4" in str(manifest.get("status")) and "SECTOR A OPEN" in str(manifest.get("status")), manifest.get("status"), "T4 ... SECTOR A OPEN")

    sources = manifest.get("sources", {})
    expected_sources = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": VERIFIER,
        "proof_note": NOTE,
    }
    for name, path in expected_sources.items():
        entry = sources.get(name, {}) if isinstance(sources, dict) else {}
        ok = entry.get("path") == relative(path) and entry.get("sha256") == digest(path)
        audit.check("manifest", f"source_{name}", ok, entry, {"path": relative(path), "sha256": digest(path)})

    children = manifest.get("child_results", {})
    for name, path in (("primary", PRIMARY_RESULT), ("independent", INDEPENDENT_RESULT)):
        entry = children.get(name, {}) if isinstance(children, dict) else {}
        ok = entry.get("path") == relative(path) and entry.get("sha256") == digest(path)
        audit.check("manifest", f"child_{name}", ok, entry, {"path": relative(path), "sha256": digest(path)})

    pdf_entry = manifest.get("proof_pdf", {})
    pdf_ok = (
        isinstance(pdf_entry, dict)
        and pdf_entry.get("path") == relative(PDF)
        and pdf_entry.get("sha256") == digest(PDF)
        and pdf_entry.get("pages") == pages
        and pdf_entry.get("size_bytes") == PDF.stat().st_size
        and pdf_entry.get("form_check") == "PASS"
        and pdf_entry.get("overfull_hbox_count") == 0
        and pdf_entry.get("visual_qa") == "PASS"
    )
    audit.check("manifest", "proof_pdf", pdf_ok, pdf_entry, "final PDF hash, metadata, form, and visual QA pinned")

    consequence = manifest.get("consequence", {})
    prohibited = (
        "full_a1_embedding",
        "adapted_production_cluster",
        "one_use_source_sextic_aggregation",
        "full_overlap_src",
        "nelson",
        "cutoff_removal",
        "floor_removal",
        "interacting_measure",
        "sector_a_closure",
        "tier_promotion",
    )
    flags_ok = isinstance(consequence, dict) and all(consequence.get(key) is False for key in prohibited)
    audit.check("manifest", "prohibited_flags_false", flags_ok, {key: consequence.get(key) for key in prohibited} if isinstance(consequence, dict) else consequence, "all false")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=180)
    arguments = parser.parse_args()

    audit = Audit()
    primary_fresh, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    independent_fresh, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    primary_stored = load_json(PRIMARY_RESULT)
    independent_stored = load_json(INDEPENDENT_RESULT)
    child_contract(audit, "primary", primary_fresh, primary_stored, PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", independent_fresh, independent_stored, INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    note_text = NOTE.read_text(encoding="utf-8")
    missing_note = [token for token in NOTE_TOKENS if token not in note_text]
    audit.check("note", "required_tokens", not missing_note, missing_note, [])
    audit.check("note", "ascii_only", all(ord(character) < 128 for character in note_text), "ASCII" if all(ord(character) < 128 for character in note_text) else "non-ASCII", "ASCII")

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_tokens = ("R-116", "parabolic", "null-cone", "Sector A")
    missing_pdf = [token for token in pdf_tokens if token not in pdf_text]
    audit.check("pdf", "page_count_positive", pages > 0, pages, ">0")
    audit.check("pdf", "text_tokens", not missing_pdf, missing_pdf, [])

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest, pages)

    diagnostics = {
        "primary_stdout": primary_stdout.strip(),
        "primary_stderr": primary_stderr.strip(),
        "independent_stdout": independent_stdout.strip(),
        "independent_stderr": independent_stderr.strip(),
        "note_sha256": digest(NOTE),
        "pdf_sha256": digest(PDF),
        "pdf_pages": pages,
        "pdf_size_bytes": PDF.stat().st_size,
        "manifest_sha256": digest(MANIFEST),
        "runtime": {"python": sys.version.split()[0]},
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"Integrated R-116 PASS={payload['status'] == 'PASS'}; "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
