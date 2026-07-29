#!/usr/bin/env python3
"""Integrated verifier for the scoped R-123 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

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
RESULT_ID = "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY"
SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-integrated/1.0"
MANIFEST_SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-manifest/1.0"
PRIMARY_SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-primary/1.0"
INDEPENDENT_SCHEMA = "tect/a13-six-row-trace-excess-direct-action-boundary-independent/1.0"
PRIMARY_ASSERTIONS = 47
INDEPENDENT_ASSERTIONS = 42

CLAIM_DIR = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
PRIMARY = REPO / "codes/foundations/a13_classii_six_row_trace_excess_direct_action_boundary.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_six_row_trace_excess_direct_action_boundary_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-six-row-trace-excess-direct-action-correlation-boundary-260730-v1.0.tex.txt"
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
MANIFEST = CLAIM_DIR / "classii_six_row_trace_excess_direct_action_boundary_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-30-primary-six-row-trace-excess-direct-action-boundary/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-30-independent-six-row-trace-excess-direct-action-boundary/result.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-integrated-six-row-trace-excess-direct-action-boundary/result.json"

AUTHORITY_PATHS = {
    "governance": REPO / "GOVERNANCE.md",
    "a1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "r063": CLAIM_DIR / "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r083": CLAIM_DIR / "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
    "r093": CLAIM_DIR / "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r107": CLAIM_DIR / "classii_coherent_output_cluster_predictable_baseline_boundary_manifest.json",
    "r109": CLAIM_DIR / "classii_square_first_pair_score_transfer_filtration_boundary_manifest.json",
    "r118": CLAIM_DIR / "classii_revisit_quotient_operator_carleson_signed_score_boundary_manifest.json",
    "r119": CLAIM_DIR / "classii_legal_adapted_cluster_score_trace_terminal_hessian_frontier_manifest.json",
    "r120": CLAIM_DIR / "classii_covariance_horizontal_synthesis_stationary_low_chaos_cartan_hessian_boundary_manifest.json",
    "r121": CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json",
    "r122": CLAIM_DIR / "classii_derivative_free_low_chaos_adapted_fifth_moment_cartan_boundary_manifest.json",
}

NOTE_TOKENS = (
    "R-123 conclusion",
    "Round one: fixed six-row endpoint law and owner incidence",
    "\\Lambda=\\Theta-\\|Y\\|^2",
    "D_0=\\E_0\\Lambda",
    "direct action removes the first-chaos burden",
    "bounded full-six-row noncancellation fixture",
    "\\frac{\\kappa^4}{16\\sqrt{\\eta\\zeta}}",
    "multiplicity-free directed-union criterion",
    "-\\frac{117}{500P}H^2",
    "\\eta\\zeta\\ge c^2/4",
    "complete trace-excess reduction",
    "Devil's-advocate review",
    "Sector-A closure remain open",
)

NEGATIVE_IDS = (
    "NG-2026-07-30-A13-STATIONARY-SIX-ROW-TO-ADAPTED-LOW-CHAOS-TRANSFER",
    "NG-2026-07-30-A13-RAW-SIX-CURRENT-HESSIAN-POSITIVITY",
    "NG-2026-07-30-A13-FIXED-PROFILE-CORRELATION-YOUNG-CUTOFF-UNIFORMITY",
)

EXPLORATION_IDS = tuple(f"EXP-{number:06d}" for number in range(386, 396))


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "no_overclaim": (
                "R-123 leaves the cutoff-uniform complete production trace-excess estimate, "
                "OVERLAP_src, Nelson, removals, measure construction, and Sector A open."
            ),
        }


def execute_child(script: Path, timeout: int) -> tuple[dict[str, Any], str, str]:
    with tempfile.TemporaryDirectory(prefix="tect-r123-") as directory:
        output = Path(directory) / "result.json"
        completed = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if not output.is_file():
            return {"status": "MISSING", "returncode": completed.returncode}, completed.stdout, completed.stderr
        payload = load_json(output)
        payload["_returncode"] = completed.returncode
        return payload, completed.stdout, completed.stderr


def child_contract(
    audit: Audit,
    label: str,
    fresh: dict[str, Any],
    stored: dict[str, Any],
    schema: str,
    assertions: int,
) -> None:
    returncode = fresh.pop("_returncode", None)
    audit.check("child", f"{label}_returncode", returncode == 0, returncode, 0)
    audit.check("child", f"{label}_status", fresh.get("status") == "PASS", fresh.get("status"), "PASS")
    audit.check("child", f"{label}_schema", fresh.get("schema") == schema, fresh.get("schema"), schema)
    audit.check("child", f"{label}_assertions", fresh.get("assertions_total") == assertions, fresh.get("assertions_total"), assertions)
    audit.check("child", f"{label}_all_pass", fresh.get("assertions_passed") == assertions, fresh.get("assertions_passed"), assertions)
    audit.check("child", f"{label}_stored_reproduces", fresh == stored, fresh == stored, True)
    flags = fresh.get("diagnostics", {}).get("scope_flags", {})
    for name in ("complete_production_trace_excess_proved", "directed_union_nelson_proved", "sector_a_closed", "tier_promoted"):
        audit.check("scope", f"{label}_{name}", flags.get(name) is False, flags.get(name), False)


def file_entry_ok(entry: Any, path: Path, version: str | None = None) -> bool:
    if not isinstance(entry, dict):
        return False
    if entry.get("path") != relative(path) or entry.get("sha256") != digest(path):
        return False
    return version is None or entry.get("version") == version


def verify_manifest(audit: Audit, manifest: dict[str, Any]) -> None:
    audit.check("manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA)
    audit.check("manifest", "result_id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    audit.check("manifest", "ledger", manifest.get("result_ledger_id") == "R-123", manifest.get("result_ledger_id"), "R-123")
    audit.check("manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")
    audit.check("manifest", "issued", manifest.get("issued") == "2026-07-30", manifest.get("issued"), "2026-07-30")
    audit.check("manifest", "primary_count", manifest.get("verification", {}).get("primary_assertions") == PRIMARY_ASSERTIONS, manifest.get("verification", {}).get("primary_assertions"), PRIMARY_ASSERTIONS)
    audit.check("manifest", "independent_count", manifest.get("verification", {}).get("independent_assertions") == INDEPENDENT_ASSERTIONS, manifest.get("verification", {}).get("independent_assertions"), INDEPENDENT_ASSERTIONS)

    files = manifest.get("files", {})
    for label, path, version in (
        ("primary", PRIMARY, "1.0.0"),
        ("independent", INDEPENDENT, "1.0.0"),
        ("verifier", VERIFIER, "1.0.0"),
        ("note", NOTE, None),
        ("pdf", PDF, None),
        ("primary_result", PRIMARY_RESULT, None),
        ("independent_result", INDEPENDENT_RESULT, None),
    ):
        audit.check("manifest_file", label, file_entry_ok(files.get(label), path, version), files.get(label), {"path": relative(path), "sha256": digest(path), "version": version})

    authorities = manifest.get("authorities", {})
    for label, path in AUTHORITY_PATHS.items():
        audit.check("authority", label, file_entry_ok(authorities.get(label), path), authorities.get(label), {"path": relative(path), "sha256": digest(path)})

    audit.check("manifest", "negatives", tuple(manifest.get("negative_results", [])) == NEGATIVE_IDS, manifest.get("negative_results"), list(NEGATIVE_IDS))
    audit.check("manifest", "explorations", tuple(manifest.get("exploration_ids", [])) == EXPLORATION_IDS, manifest.get("exploration_ids"), list(EXPLORATION_IDS))
    boundary = str(manifest.get("no_overclaim", ""))
    audit.check("manifest", "no_overclaim", all(token in boundary for token in ("does not prove", "OVERLAP_src", "Sector-A closure")), boundary, "explicit open boundaries")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=180)
    arguments = parser.parse_args()
    audit = Audit()

    required = [PRIMARY, INDEPENDENT, VERIFIER, NOTE, PDF, MANIFEST, PRIMARY_RESULT, INDEPENDENT_RESULT, *AUTHORITY_PATHS.values()]
    for path in required:
        audit.check("existence", relative(path), path.is_file(), path.is_file(), True)

    if any(not path.is_file() for path in required):
        payload = audit.finish({"missing": [relative(path) for path in required if not path.is_file()]})
        atomic_json(arguments.output, payload)
        print(f"R-123 integrated {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
        return 1

    primary_fresh, primary_stdout, primary_stderr = execute_child(PRIMARY, arguments.timeout)
    independent_fresh, independent_stdout, independent_stderr = execute_child(INDEPENDENT, arguments.timeout)
    child_contract(audit, "primary", primary_fresh, load_json(PRIMARY_RESULT), PRIMARY_SCHEMA, PRIMARY_ASSERTIONS)
    child_contract(audit, "independent", independent_fresh, load_json(INDEPENDENT_RESULT), INDEPENDENT_SCHEMA, INDEPENDENT_ASSERTIONS)

    manifest = load_json(MANIFEST)
    verify_manifest(audit, manifest)

    note_text = NOTE.read_text(encoding="utf-8")
    for index, token in enumerate(NOTE_TOKENS, start=1):
        audit.check("note", f"token_{index:02d}", token in note_text, token in note_text, True)
    audit.check("note", "ascii_hyphen_policy", "‑" not in note_text, "‑" in note_text, False)

    reader = PdfReader(PDF)
    pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    audit.check("pdf", "pages", len(reader.pages) == 10, len(reader.pages), 10)
    audit.check("pdf", "no_forms", not (reader.get_fields() or {}), bool(reader.get_fields() or {}), False)
    for token in ("R-123 conclusion", "complete trace-excess reduction", "Sector-A closure remain open"):
        audit.check("pdf", f"text_{token[:12]}", token in pdf_text, token in pdf_text, True)

    surfaces = {
        "claim": CLAIM_DIR / "claim.md",
        "status": CLAIM_DIR / "status.json",
        "results": REPO / "RESULTS-LEDGER.md",
        "negative": REPO / "negative-results/registry.md",
        "roadmap": REPO / "ROADMAP.md",
        "todo_source": REPO / "todo/todo.json",
        "todo_generated": REPO / "TODO.md",
        "sector_map": REPO / "governance/sector-a-theorem-map.json",
        "changelog_source": REPO / "changelog/log.jsonl",
        "changelog_generated": REPO / "CHANGELOG.md",
        "explorations": REPO / "explorations/log.jsonl",
        "claims_generated": REPO / "CLAIMS.md",
        "proof_map": REPO / "theory/proof-evidence-map.md",
        "index": CLAIM_DIR / "INDEX.md",
        "lineage": CLAIM_DIR / "LINEAGE.md",
    }
    surface_text = {label: path.read_text(encoding="utf-8") for label, path in surfaces.items()}
    for label in ("claim", "status", "results", "roadmap", "todo_source", "todo_generated", "sector_map", "changelog_source", "changelog_generated", "claims_generated", "proof_map", "index", "lineage"):
        token = (
            CLAIM
            if label == "claims_generated"
            else "six-row-trace-excess-direct-action"
            if label == "lineage"
            else "R-123"
        )
        audit.check("surface", f"{label}_R123", token in surface_text[label], token in surface_text[label], True)
    for identifier in NEGATIVE_IDS:
        audit.check("negative", identifier, identifier in surface_text["negative"], identifier in surface_text["negative"], True)
    for identifier in EXPLORATION_IDS:
        audit.check("exploration", identifier, f'"id":"{identifier}"' in surface_text["explorations"], f'"id":"{identifier}"' in surface_text["explorations"], True)
    audit.check("surface", "sector_result_id", RESULT_ID in surface_text["sector_map"], RESULT_ID in surface_text["sector_map"], True)
    audit.check("surface", "status_open", "remain open" in surface_text["status"], "remain open" in surface_text["status"], True)
    audit.check("surface", "roadmap_target", "stationary-subtracted" in surface_text["roadmap"], "stationary-subtracted" in surface_text["roadmap"], True)
    audit.check("surface", "todo_target", "trace-excess" in surface_text["todo_source"], "trace-excess" in surface_text["todo_source"], True)

    diagnostics = {
        "child_stdout": {"primary": primary_stdout.strip(), "independent": independent_stdout.strip()},
        "child_stderr": {"primary": primary_stderr.strip(), "independent": independent_stderr.strip()},
        "pdf": {"pages": len(reader.pages), "sha256": digest(PDF)},
        "note_sha256": digest(NOTE),
        "manifest_sha256": digest(MANIFEST),
        "scope_flags": {
            "complete_production_trace_excess_proved": False,
            "overlap_src_proved": False,
            "nelson_proved": False,
            "sector_a_closed": False,
            "tier_promoted": False,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-123 integrated {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
