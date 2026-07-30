#!/usr/bin/env python3
"""Integrated authority, PDF, ledger, and public-surface audit for R-130."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import ast
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-TERMINAL-XI-CONORMAL-GRAM-BALANCED-LOW-"
    "RESPONSE-BOUNDARY"
)
LEDGER_ID = "R-130"
SLUG = "terminal-xi-conormal-gram-balanced-low-response-boundary"
SCHEMA = f"tect/a13-{SLUG}-integrated/1.0"
MANIFEST_SCHEMA = f"tect/a13-{SLUG}-manifest/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / (
    "codes/foundations/a13_classii_terminal_xi_conormal_gram_"
    "balanced_low_response_boundary.py"
)
INDEPENDENT = REPO / (
    "codes/foundations/a13_classii_terminal_xi_conormal_gram_"
    "balanced_low_response_boundary_independent.py"
)
HELPER = REPO / (
    "codes/foundations/a13_classii_endpoint_trace_excess_shell_"
    "coanalysis_shifted_douglas_boundary_verify.py"
)
PRIMARY_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-"
    "low-response-boundary/result.json"
)
INDEPENDENT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-terminal-xi-conormal-gram-balanced-"
    "low-response-boundary/result.json"
)
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-integrated-terminal-xi-conormal-gram-balanced-"
    "low-response-boundary/result.json"
)
MANIFEST = CLAIM_DIR / (
    "classii_terminal_xi_conormal_gram_balanced_low_"
    "response_boundary_manifest.json"
)
EXPECTED_AUTHORITY_KEYS = {
    "governance",
    "a1",
    "a8",
    "a8_primary",
    "r079",
    "r082",
    "r103",
    "r103_primary",
    "r104",
    "r120",
    "r121",
    "r123",
    "r124",
    "r124_primary",
    "r128",
    "r129",
    "r129_verifier",
}
EXPECTED_FILE_KEYS = {
    "primary",
    "independent",
    "verifier",
    "note",
    "pdf",
    "primary_result",
    "independent_result",
}
EXPECTED_AUTHORITY_RESULT_IDS = {
    "r079": "A13-CLASSII-FULL-SAFE-PACKET-FRAME-CURRENT-DOOB-DECOMPOSITION",
    "r082": "A13-CLASSII-STOPPED-CURRENT-FAR-COMPLETE-CURRENT-NEAR-COORDINATE-REDUCTION",
    "r103": "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE",
    "r104": "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY",
    "r120": "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-LOW-CHAOS-CARTAN-HESSIAN-BOUNDARY",
    "r121": "A13-CLASSII-CARTAN-PATHSPACE-EXACTNESS-FIXED-SKEW-SOBOLEV-BOUNDARY",
    "r123": "A13-CLASSII-SIX-ROW-TRACE-EXCESS-DIRECT-ACTION-CORRELATION-BOUNDARY",
    "r124": "A13-CLASSII-STATIONARY-POLARIZED-TRACE-DEFECT-REPLICA-ROOT-SHELL-BOUNDARY",
    "r128": "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY",
    "r129": "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY",
}
EXPECTED_NEGATIVES = {
    "NG-2026-07-31-A13-UNWEIGHTED-RATIONAL-D2-FLOOR-UNIFORMITY",
    "NG-2026-07-31-A13-COMPLETE-LOW-SQUARE-STRICT-GAP-REFINEMENT",
}
EXPECTED_EXPLORATIONS = {f"EXP-{number:06d}" for number in range(469, 483)}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("r129_verify_helper", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned R-129 verifier helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


H = load_helper()
digest = H.digest
load_json = H.load_json
confined_path = H.confined_path
pdf_security_audit = H.pdf_security_audit
render_pdf = H.render_pdf
normalized = H.normalized


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

    def finish(
        self,
        primary: dict[str, Any],
        independent: dict[str, Any],
        contract_observed: dict[str, Any],
    ) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        child_total = int(primary["assertions_total"]) + int(
            independent["assertions_total"]
        )
        child_passed = int(primary["assertions_passed"]) + int(
            independent["assertions_passed"]
        )
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
            "aggregate": {
                "assertions_total": child_total + len(self.rows),
                "assertions_passed": child_passed + passed,
                "assertions_failed": child_total + len(self.rows) - child_passed - passed,
            },
            "contract_observed": contract_observed,
            "scope": {
                "post_recombined_terminal_trace_recode_proved": True,
                "finite_cylinder_response_order_proved": True,
                "fixed_six_row_pointwise_gram_envelopes_proved": True,
                "sharp_balanced_bridge_proved": True,
                "centered_heat_direct_low_candidate_proved": True,
                "complete_gram_schur_psd_proved": True,
                "production_uniform_response_proved": False,
                "complete_global_balanced_low_closure_proved": False,
                "matching_energy_and_strict_gap_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-130 proves a fixed post-recombined terminal trace recode, "
                "finite-cylinder response order, fixed-Q pointwise Gram envelopes, "
                "the sharp balanced bridge, a centered-heat direct-low candidate, "
                "and complete-Gram semidefiniteness. It proves no cutoff-uniform "
                "production response, complete global balanced or historical low "
                "closure, matching energy, strict gap, absolute anchor, "
                "OVERLAP_src, Nelson, removal, interacting measure, or Sector-A theorem."
            ),
        }


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    primary_run = run_child(PRIMARY)
    independent_run = run_child(INDEPENDENT)
    audit.check(
        "children", "primary_exit", primary_run.returncode == 0, primary_run.returncode, 0
    )
    audit.check(
        "children",
        "independent_exit",
        independent_run.returncode == 0,
        independent_run.returncode,
        0,
    )
    for label, path in (
        ("primary", PRIMARY_OUTPUT),
        ("independent", INDEPENDENT_OUTPUT),
    ):
        audit.check("children", f"{label}_output_exists", path.is_file(), path.is_file(), True)
    if not PRIMARY_OUTPUT.is_file() or not INDEPENDENT_OUTPUT.is_file():
        print("R-130 integrated BLOCKED: a child output is missing")
        return 1
    primary = load_json(PRIMARY_OUTPUT)
    independent = load_json(INDEPENDENT_OUTPUT)
    for label, payload, count, schema_suffix in (
        ("primary", primary, 58, "primary/1.0"),
        ("independent", independent, 90, "independent/1.0"),
    ):
        audit.check(
            "children", f"{label}_status", payload.get("status") == "PASS", payload.get("status"), "PASS"
        )
        audit.check(
            "children", f"{label}_claim", payload.get("claim_id") == CLAIM, payload.get("claim_id"), CLAIM
        )
        audit.check(
            "children", f"{label}_result", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID
        )
        audit.check(
            "children", f"{label}_schema", payload.get("schema") == f"tect/a13-{SLUG}-{schema_suffix}", payload.get("schema"), f"tect/a13-{SLUG}-{schema_suffix}"
        )
        audit.check(
            "children", f"{label}_count", payload.get("assertions_total") == count, payload.get("assertions_total"), count
        )
        audit.check(
            "children", f"{label}_passed", payload.get("assertions_passed") == count, payload.get("assertions_passed"), count
        )
        audit.check(
            "children", f"{label}_no_failures", payload.get("assertions_failed") == 0, payload.get("assertions_failed"), 0
        )

    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    independent_tree = ast.parse(independent_source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(independent_tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    audit.check(
        "independence", "no_sympy_import", "sympy" not in imported_roots, sorted(imported_roots), "sympy absent"
    )
    audit.check(
        "independence", "no_primary_filename", PRIMARY.name not in independent_source, PRIMARY.name in independent_source, False
    )
    audit.check(
        "independence", "jet2_present", "class Jet2" in independent_source, "class Jet2" in independent_source, True
    )
    for token in (
        "adaptive_simpson",
        "terminal8",
        "response3",
        "circle_points = 4096",
        "rank_one_schur",
    ):
        audit.check(
            "independence", f"fixture_{token.split()[0]}", token in independent_source, token in independent_source, True
        )

    primary_diagnostics = primary.get("diagnostics", {})
    independent_diagnostics = independent.get("diagnostics", {})
    exact_pairs = (
        (
            "production_P",
            primary_diagnostics.get("production", {}).get("P"),
            independent_diagnostics.get("production", {}).get("P"),
        ),
        (
            "production_floor",
            primary_diagnostics.get("production", {}).get("density_floor"),
            independent_diagnostics.get("production", {}).get("density_floor"),
        ),
        (
            "production_c0",
            primary_diagnostics.get("production", {}).get("c0"),
            independent_diagnostics.get("production", {}).get("c0"),
        ),
        (
            "production_c1",
            primary_diagnostics.get("production", {}).get("c1"),
            independent_diagnostics.get("production", {}).get("c1"),
        ),
        (
            "production_beta_operator",
            primary_diagnostics.get("production", {}).get("beta_operator"),
            independent_diagnostics.get("production", {}).get("beta_operator"),
        ),
        (
            "gram_L6",
            primary_diagnostics.get("conormal_gram", {}).get("L6"),
            independent_diagnostics.get("gram", {}).get("L6"),
        ),
        (
            "gram_H6",
            primary_diagnostics.get("conormal_gram", {}).get("H6"),
            independent_diagnostics.get("gram", {}).get("H6"),
        ),
        (
            "gram_physical_force",
            primary_diagnostics.get("conormal_gram", {}).get(
                "physical_force_constant"
            ),
            independent_diagnostics.get("gram", {}).get("physical_force"),
        ),
        (
            "gram_physical_remainder",
            primary_diagnostics.get("conormal_gram", {}).get(
                "physical_taylor_remainder_constant"
            ),
            independent_diagnostics.get("gram", {}).get("physical_remainder"),
        ),
        (
            "response_q_comp",
            primary_diagnostics.get("response", {}).get("q_comp_matrix"),
            independent_diagnostics.get("response", {}).get("q_comp"),
        ),
        (
            "response_pullback",
            primary_diagnostics.get("response", {}).get("pulled_hessian"),
            independent_diagnostics.get("response", {}).get("pulled"),
        ),
        (
            "terminal_square_difference",
            primary_diagnostics.get("terminal", {}).get("square_difference"),
            independent_diagnostics.get("terminal", {}).get("square_difference"),
        ),
        (
            "terminal_trace_total",
            primary_diagnostics.get("terminal", {}).get("trace_total"),
            independent_diagnostics.get("terminal", {}).get("trace_total"),
        ),
        (
            "low_coefficient",
            primary_diagnostics.get("direct_low_candidate", {}).get(
                "a_low_per_g_low"
            ),
            independent_diagnostics.get("low", {}).get("a_low_per_g"),
        ),
        (
            "low_schur",
            primary_diagnostics.get("complete_low_gram", {}).get("schur_fixture"),
            independent_diagnostics.get("low", {}).get("schur"),
        ),
        (
            "low_rank_one_zero",
            primary_diagnostics.get("complete_low_gram", {}).get(
                "rank_one_schur"
            ),
            independent_diagnostics.get("low", {}).get("rank_one_schur"),
        ),
    )
    for name, primary_value, independent_value in exact_pairs:
        audit.check(
            "cross_child",
            name,
            primary_value == independent_value,
            independent_value,
            primary_value,
        )
    balanced_primary = primary_diagnostics.get("balanced", {})
    balanced_independent = independent_diagnostics.get("balanced", {})
    oriented = float(Fraction(balanced_primary["oriented_local_cartan_diagnostic"]))
    eta = float(Fraction(balanced_primary["eta_available"]))
    zeta = float(Fraction(balanced_primary["zeta_available"]))
    bridge = math.sqrt(32.0 * float(Fraction(balanced_primary["A0"])))
    ceiling = 2.0 * math.sqrt(eta * zeta) / bridge
    ratio = oriented / ceiling
    for name, calculated, observed in (
        ("balanced_oriented", oriented, balanced_independent.get("oriented_diagnostic")),
        ("balanced_ceiling", ceiling, balanced_independent.get("ceiling")),
        ("balanced_ratio", ratio, balanced_independent.get("diagnostic_ratio")),
    ):
        audit.check(
            "cross_child",
            name,
            math.isclose(calculated, float(observed), rel_tol=0.0, abs_tol=2e-15),
            observed,
            calculated,
        )

    audit.check("manifest", "exists", MANIFEST.is_file(), MANIFEST.is_file(), True)
    if not MANIFEST.is_file():
        print("R-130 integrated BLOCKED: manifest missing")
        return 1
    manifest = load_json(MANIFEST)
    verification = manifest.get("verification", {})
    audit.check(
        "manifest", "schema", manifest.get("schema") == MANIFEST_SCHEMA, manifest.get("schema"), MANIFEST_SCHEMA
    )
    audit.check(
        "manifest", "claim", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM
    )
    audit.check(
        "manifest", "result", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID
    )
    audit.check(
        "manifest", "ledger", manifest.get("result_ledger_id") == LEDGER_ID, manifest.get("result_ledger_id"), LEDGER_ID
    )
    audit.check("manifest", "tier", manifest.get("tier") == "T4", manifest.get("tier"), "T4")
    audit.check(
        "manifest",
        "evidence_grade",
        manifest.get("evidence_grade") == ["ANALYTIC", "EXACT", "EXECUTED"],
        manifest.get("evidence_grade"),
        ["ANALYTIC", "EXACT", "EXECUTED"],
    )
    audit.check(
        "manifest", "proof_incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False
    )
    scope = manifest.get("scope", {})
    for field in (
        "production_uniform_response_proved",
        "complete_global_c_mix_c_far_c_bal_proved",
        "historical_r079_low_owner_equivalence_proved",
        "production_matching_energy_proved",
        "strict_augmented_gap_proved",
        "absolute_anchor_proved",
        "overlap_src_proved",
        "nelson_proved",
        "removals_proved",
        "interacting_measure_proved",
        "sector_a_closed",
        "tier_promoted",
    ):
        audit.check("manifest_scope", field, scope.get(field) is False, scope.get(field), False)
    for field in (
        "post_recombined_terminal_trace_recode_proved",
        "finite_cylinder_response_order_proved",
        "fixed_six_row_pointwise_gram_envelopes_proved",
        "sharp_balanced_bridge_proved",
        "centered_heat_direct_low_candidate_proved",
        "complete_gram_schur_psd_proved",
    ):
        audit.check("manifest_scope", field, scope.get(field) is True, scope.get(field), True)
    no_overclaim = str(manifest.get("no_overclaim", "")).lower()
    audit.check(
        "manifest",
        "no_overclaim_semantics",
        all(token in no_overclaim for token in ("does not", "production", "nelson", "sector-a")),
        manifest.get("no_overclaim"),
        "explicit production/Nelson/Sector-A boundary",
    )
    audit.check(
        "manifest", "negative_set", set(manifest.get("negative_results", [])) == EXPECTED_NEGATIVES, manifest.get("negative_results", []), sorted(EXPECTED_NEGATIVES)
    )
    audit.check(
        "manifest", "exploration_set", set(manifest.get("exploration_ids", [])) == EXPECTED_EXPLORATIONS, manifest.get("exploration_ids", []), sorted(EXPECTED_EXPLORATIONS)
    )
    audit.check(
        "manifest", "primary_contract", verification.get("primary_assertions") == 58, verification.get("primary_assertions"), 58
    )
    audit.check(
        "manifest", "independent_contract", verification.get("independent_assertions") == 90, verification.get("independent_assertions"), 90
    )
    audit.check(
        "manifest", "primary_schema", verification.get("primary_schema") == primary.get("schema"), verification.get("primary_schema"), primary.get("schema")
    )
    audit.check(
        "manifest", "independent_schema", verification.get("independent_schema") == independent.get("schema"), verification.get("independent_schema"), independent.get("schema")
    )
    audit.check(
        "manifest", "integrated_schema", verification.get("integrated_schema") == SCHEMA, verification.get("integrated_schema"), SCHEMA
    )

    authorities = manifest.get("authorities", {})
    files = manifest.get("files", {})
    audit.check(
        "manifest", "authority_keys", set(authorities) == EXPECTED_AUTHORITY_KEYS, sorted(authorities), sorted(EXPECTED_AUTHORITY_KEYS)
    )
    audit.check(
        "manifest", "file_keys", set(files) == EXPECTED_FILE_KEYS, sorted(files), sorted(EXPECTED_FILE_KEYS)
    )
    audit.check(
        "manifest", "declared_authority_keys", manifest.get("authority_keys") == list(authorities), manifest.get("authority_keys"), list(authorities)
    )
    expected_file_order = [
        "primary",
        "independent",
        "verifier",
        "note",
        "pdf",
        "primary_result",
        "independent_result",
    ]
    audit.check(
        "manifest", "declared_file_keys", manifest.get("file_keys") == expected_file_order, manifest.get("file_keys"), expected_file_order
    )
    authority_paths = [entry.get("path") for entry in authorities.values()]
    audit.check(
        "manifest", "unique_authority_paths", len(authority_paths) == len(set(authority_paths)), authority_paths, "all unique"
    )
    for group, entries in (("authority", authorities), ("files", files)):
        for name, entry in entries.items():
            expected_hash = str(entry.get("sha256", ""))
            audit.check(
                group, f"{name}_hash_format", SHA256_PATTERN.fullmatch(expected_hash) is not None, expected_hash, "64 lowercase hex"
            )
            path, confined = confined_path(str(entry.get("path", "")))
            audit.check(group, f"{name}_confined", confined, confined, True)
            audit.check(group, f"{name}_exists", confined and path.is_file(), path.is_file(), True)
            if confined and path.is_file():
                actual_hash = digest(path)
                audit.check(group, f"{name}_sha256", actual_hash == expected_hash, actual_hash, expected_hash)

    for name, expected_result_id in EXPECTED_AUTHORITY_RESULT_IDS.items():
        authority_path, confined = confined_path(authorities[name]["path"])
        payload = load_json(authority_path) if confined and authority_path.is_file() else {}
        audit.check(
            "authority_semantics", f"{name}_result_id", payload.get("result_id") == expected_result_id, payload.get("result_id"), expected_result_id
        )
    for result_name, manifest_name in (
        ("r103_primary", "r103"),
        ("r124_primary", "r124"),
    ):
        result_path, result_confined = confined_path(authorities[result_name]["path"])
        manifest_path, manifest_confined = confined_path(authorities[manifest_name]["path"])
        result_payload = load_json(result_path) if result_confined and result_path.is_file() else {}
        manifest_payload = load_json(manifest_path) if manifest_confined and manifest_path.is_file() else {}
        audit.check(
            "authority_semantics",
            f"{result_name}_matches_manifest",
            result_payload.get("result_id") == manifest_payload.get("result_id"),
            result_payload.get("result_id"),
            manifest_payload.get("result_id"),
        )

    note_path, note_confined = confined_path(files["note"]["path"])
    pdf_path, pdf_confined = confined_path(files["pdf"]["path"])
    if not note_confined or not pdf_confined or not note_path.is_file() or not pdf_path.is_file():
        print("R-130 integrated BLOCKED: note/PDF path contract invalid")
        return 1
    note_check = subprocess.run(
        [
            sys.executable,
            str(REPO / "verification/scripts/build_note_pdf.py"),
            str(note_path),
            "--no-compile",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    audit.check("note", "form_check_exit", note_check.returncode == 0, note_check.returncode, 0)
    audit.check(
        "note", "form_check_banner", "FORM-CHECK: PASS" in note_check.stdout, "FORM-CHECK: PASS" in note_check.stdout, True
    )
    note = note_path.read_text(encoding="utf-8")
    note_norm = normalized(note)
    for index, phrase in enumerate(
        (
            "Purpose and scope",
            "Owner and coordinate firewall",
            "The post-recombined $\\Xi$ terminal",
            "Boundary 3.1: this is not a legacy-root transport theorem",
            "matching trace is not matching energy",
            "The physical response must precede pullback",
            "Exact fixed-six-row conormal Gram envelopes",
            "Theorem 5.1 (pointwise Gram envelopes)",
            "A floor-uniform separated rational $H^2$ no-go",
            "The sharp balanced bridge and its present boundary",
            "A centered-heat direct-low candidate",
            "Complete-square Gram Schur and two exact failures",
            "Proof-search evidence map",
            "Devil's-advocate review",
            "Executed evidence and reproduction",
            "Result footer",
            "Proof complete: false",
        ),
        start=1,
    ):
        present = normalized(phrase) in note_norm
        audit.check("note", f"phrase_{index:02d}", present, present, True)
    audit.check(
        "note", "source_note_hash", verification.get("source_note_sha256") == digest(note_path), verification.get("source_note_sha256"), digest(note_path)
    )

    reader = PdfReader(str(pdf_path))
    extracted_pages = [(page.extract_text() or "") for page in reader.pages]
    extracted = "\n".join(extracted_pages)
    compact_extracted = extracted.replace("\n", "").replace(" ", "")
    fields = reader.get_fields() or {}
    pdf_contract = verification.get("pdf", {})
    audit.check("pdf", "not_encrypted", not reader.is_encrypted, reader.is_encrypted, False)
    audit.check(
        "pdf", "pages", len(reader.pages) == pdf_contract.get("pages"), len(reader.pages), pdf_contract.get("pages")
    )
    audit.check(
        "pdf", "all_pages_nonblank", all(len(text.strip()) >= 20 for text in extracted_pages), [len(text.strip()) for text in extracted_pages], "all >= 20"
    )
    audit.check("pdf", "no_form", not fields, sorted(fields), [])
    audit.check(
        "pdf", "claim_id_extracted", CLAIM in compact_extracted, CLAIM in compact_extracted, True
    )
    audit.check("pdf", "r130_extracted", LEDGER_ID in extracted, LEDGER_ID in extracted, True)
    security = pdf_security_audit(reader)
    audit.check(
        "pdf", "safe_open_action", security["safe_open_action"], security["open_action"], "safe"
    )
    audit.check("pdf", "no_unsafe_features", not security["findings"], security["findings"], [])
    audit.check("pdf", "no_widgets", security["widget_count"] == 0, security["widget_count"], 0)
    audit.check(
        "pdf", "size", pdf_path.stat().st_size == pdf_contract.get("size_bytes"), pdf_path.stat().st_size, pdf_contract.get("size_bytes")
    )
    audit.check(
        "pdf", "hash", digest(pdf_path) == pdf_contract.get("sha256"), digest(pdf_path), pdf_contract.get("sha256")
    )
    visual = pdf_contract.get("visual_qa", {})
    audit.check("pdf", "visual_status", visual.get("status") == "PASS", visual.get("status"), "PASS")
    audit.check(
        "pdf",
        "visual_all_pages",
        visual.get("rendered_pages") == 11 and visual.get("inspected_pages") == 11,
        {"rendered": visual.get("rendered_pages"), "inspected": visual.get("inspected_pages")},
        {"rendered": 11, "inspected": 11},
    )
    audit.check("pdf", "visual_no_defects", visual.get("defects") == [], visual.get("defects"), [])
    audit.check(
        "pdf", "overfull_zero", pdf_contract.get("overfull_hbox_count") == 0, pdf_contract.get("overfull_hbox_count"), 0
    )
    for field in (
        "form_check",
        "javascript_check",
        "unsafe_action_check",
        "widget_check",
        "embedded_file_check",
        "encryption_check",
    ):
        audit.check(
            "pdf_contract", field, pdf_contract.get(field) == "PASS", pdf_contract.get(field), "PASS"
        )

    tmp_parent = REPO / "internal" / "tmp"
    tmp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="r130-pdf-freshness-", dir=tmp_parent) as temporary:
        temporary_root = Path(temporary)
        temporary_note = temporary_root / note_path.name
        temporary_note.write_text(note, encoding="utf-8", newline="\n")
        rebuild = subprocess.run(
            [
                sys.executable,
                str(REPO / "verification/scripts/build_note_pdf.py"),
                str(temporary_note),
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        rebuilt_pdf = temporary_note.with_name(
            temporary_note.name.removesuffix(".tex.txt") + ".pdf"
        )
        audit.check(
            "pdf_freshness", "rebuild_exit", rebuild.returncode == 0, rebuild.returncode, 0
        )
        overfull_zero = "OVERFULL-HBOX: 0" in (rebuild.stdout or "")
        audit.check(
            "pdf_freshness", "rebuild_overfull_zero", overfull_zero, overfull_zero, True
        )
        audit.check(
            "pdf_freshness", "rebuilt_pdf_exists", rebuilt_pdf.is_file(), rebuilt_pdf.is_file(), True
        )
        if rebuilt_pdf.is_file():
            rebuilt_reader = PdfReader(str(rebuilt_pdf))
            rebuilt_pages = [(page.extract_text() or "") for page in rebuilt_reader.pages]
            audit.check(
                "pdf_freshness", "rebuilt_page_count", len(rebuilt_pages) == len(extracted_pages), len(rebuilt_pages), len(extracted_pages)
            )
            pinned_text = [normalized(text) for text in extracted_pages]
            rebuilt_text = [normalized(text) for text in rebuilt_pages]
            audit.check(
                "pdf_freshness", "source_to_pdf_text_identity", rebuilt_text == pinned_text, [len(text) for text in rebuilt_text], [len(text) for text in pinned_text]
            )
            pinned_render = temporary_root / "pinned-render"
            rebuilt_render = temporary_root / "rebuilt-render"
            pinned_render.mkdir()
            rebuilt_render.mkdir()
            pinned_exit, _pinned_log, pinned_hashes = render_pdf(
                pdf_path, pinned_render, "page"
            )
            rebuilt_exit, _rebuilt_log, rebuilt_hashes = render_pdf(
                rebuilt_pdf, rebuilt_render, "page"
            )
            expected_page_hashes = visual.get("page_sha256", [])
            audit.check(
                "pdf_freshness", "pinned_render_exit", pinned_exit == 0, pinned_exit, 0
            )
            audit.check(
                "pdf_freshness", "rebuilt_render_exit", rebuilt_exit == 0, rebuilt_exit, 0
            )
            audit.check(
                "pdf_freshness", "pinned_render_count", len(pinned_hashes) == 11, len(pinned_hashes), 11
            )
            audit.check(
                "pdf_freshness", "manual_visual_hash_binding", pinned_hashes == expected_page_hashes, pinned_hashes, expected_page_hashes
            )
            audit.check(
                "pdf_freshness", "rebuilt_render_identity", rebuilt_hashes == pinned_hashes, rebuilt_hashes, pinned_hashes
            )

    explorations: dict[str, dict[str, Any]] = {}
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            explorations[str(row.get("id"))] = row
    for identifier in sorted(EXPECTED_EXPLORATIONS):
        row = explorations.get(identifier)
        audit.check(
            "exploration", f"{identifier}_exists", row is not None, row is not None, True
        )
        if row is None:
            continue
        audit.check(
            "exploration", f"{identifier}_claim", CLAIM in row.get("claim_ids", []), row.get("claim_ids", []), CLAIM
        )
        audit.check(
            "exploration", f"{identifier}_task", row.get("task_id") == "T-050", row.get("task_id"), "T-050"
        )
        for field in ("question", "finding", "decision_reason", "boundary", "evidence_refs", "next_action"):
            audit.check(
                "exploration", f"{identifier}_{field}", bool(row.get(field)), bool(row.get(field)), True
            )

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for identifier in sorted(EXPECTED_NEGATIVES):
        heading = f"### {identifier}"
        audit.check("negatives", identifier, heading in negative_text, heading in negative_text, True)

    status = load_json(CLAIM_DIR / "status.json")
    audit.check("surface", "status_tier", status.get("tier") == "T4", status.get("tier"), "T4")
    audit.check(
        "surface", "status_statement", LEDGER_ID in status.get("statement", ""), LEDGER_ID in status.get("statement", ""), True
    )
    audit.check(
        "surface", "status_next_action", "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND" in status.get("next_action", ""), status.get("next_action"), "successor ID"
    )
    audit.check(
        "surface",
        "status_no_overclaim",
        "does not" in status.get("no_overclaim", "").lower()
        and "sector-a" in status.get("no_overclaim", "").lower(),
        status.get("no_overclaim"),
        "open-scope statement",
    )

    surface_contracts = (
        ("claim", CLAIM_DIR / "claim.md", (LEDGER_ID, RESULT_ID, "EXP-000469--EXP-000482")),
        ("lineage", CLAIM_DIR / "lineage-narrative.md", (LEDGER_ID, "R-082 `Xi`", "balanced bridge")),
        ("results_ledger", REPO / "RESULTS-LEDGER.md", (f"## {LEDGER_ID}", RESULT_ID)),
        ("todo", REPO / "todo/todo.json", ("T-050", LEDGER_ID, "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND")),
        ("changelog_source", REPO / "changelog/log.jsonl", (LEDGER_ID, SLUG)),
        ("changelog_render", REPO / "CHANGELOG.md", (LEDGER_ID, "eleven-page PDF")),
        ("claims_render", REPO / "CLAIMS.md", (CLAIM, "Class-II source, translated model", "T4")),
        ("proof_map", REPO / "theory/proof-evidence-map.md", (LEDGER_ID, SLUG, "EXP-000482")),
        ("proof_map_json", REPO / "verification/proof-evidence-map.json", (RESULT_ID, "EXP-000482")),
        ("catalog", REPO / "CATALOG.md", (SLUG,)),
        ("catalog_json", REPO / "verification/catalog.json", (SLUG,)),
    )
    for label, path, phrases in surface_contracts:
        audit.check("surface", f"{label}_exists", path.is_file(), path.is_file(), True)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for index, phrase in enumerate(phrases, start=1):
                audit.check(
                    "surface", f"{label}_phrase_{index}", phrase in text, phrase in text, True
                )

    changelog_rows = [
        json.loads(line)
        for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching_events = [
        row for row in changelog_rows if "R-130 terminal Xi" in row.get("header", "")
    ]
    audit.check(
        "surface_semantics",
        "unique_r130_event",
        len(matching_events) == 1,
        len(matching_events),
        1,
    )
    latest_event = matching_events[-1] if matching_events else {}
    audit.check(
        "surface_semantics", "latest_event_header", "R-130 terminal Xi" in latest_event.get("header", ""), latest_event.get("header"), "R-130 terminal Xi"
    )
    audit.check(
        "surface_semantics", "latest_event_claim", latest_event.get("claim_ids") == [CLAIM], latest_event.get("claim_ids"), [CLAIM]
    )
    audit.check(
        "surface_semantics", "latest_event_manifest", MANIFEST.relative_to(REPO).as_posix() in latest_event.get("notes", []), latest_event.get("notes"), MANIFEST.relative_to(REPO).as_posix()
    )
    audit.check(
        "surface_semantics", "latest_event_verifier", Path(__file__).relative_to(REPO).as_posix() in latest_event.get("scripts", []), latest_event.get("scripts"), Path(__file__).relative_to(REPO).as_posix()
    )
    audit.check(
        "surface_semantics", "latest_event_explorations", {"EXP-000476", "EXP-000481", "EXP-000482"}.issubset(set(latest_event.get("keywords", []))), latest_event.get("keywords"), ["EXP-000476", "EXP-000481", "EXP-000482"]
    )

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json")
    active = theorem_map.get("active_frontier", {})
    audit.check(
        "surface", "theorem_map_latest", active.get("latest_result_id") == RESULT_ID, active.get("latest_result_id"), RESULT_ID
    )
    audit.check(
        "surface", "theorem_map_successor", "OWNER-COMPLETE-TRACE-EXCESS-PHYSICAL-RESPONSE-FORWARD-BALANCED-LOW-BOUND" in active.get("success_condition", ""), active.get("success_condition"), "successor ID"
    )

    precontract_count = len(audit.rows)
    precontract_identifier_hash = hashlib.sha256(
        "\n".join(sorted(audit.identifiers)).encode("utf-8")
    ).hexdigest()
    contract_observed = {
        "integrated_precontract_assertions": precontract_count,
        "integrated_precontract_identifier_sha256": precontract_identifier_hash,
        "integrated_assertions": precontract_count + 4,
        "aggregate_assertions": 58 + 90 + precontract_count + 4,
    }
    audit.check(
        "contract",
        "precontract_assertion_count",
        precontract_count == int(verification.get("integrated_precontract_assertions", -1)),
        precontract_count,
        verification.get("integrated_precontract_assertions"),
    )
    audit.check(
        "contract",
        "precontract_identifier_hash",
        precontract_identifier_hash == verification.get("integrated_precontract_identifier_sha256"),
        precontract_identifier_hash,
        verification.get("integrated_precontract_identifier_sha256"),
    )
    audit.check(
        "contract",
        "integrated_assertion_count",
        len(audit.rows) + 2 == int(verification.get("integrated_assertions", -1)),
        len(audit.rows) + 2,
        verification.get("integrated_assertions"),
    )
    audit.check(
        "contract",
        "aggregate_assertion_count",
        58 + 90 + len(audit.rows) + 1 == int(verification.get("aggregate_assertions", -1)),
        58 + 90 + len(audit.rows) + 1,
        verification.get("aggregate_assertions"),
    )

    payload = audit.finish(primary, independent, contract_observed)
    atomic_json(arguments.output, payload)
    print(
        f"R-130 integrated {payload['status']}: "
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
