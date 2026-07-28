#!/usr/bin/env python3
"""Integrated hash-pinned verifier for the scoped R-113 scalar package."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SCALAR-K2K-EFFECTIVE-BOUNDARY-DIRECTED-ROUNDING-SEED"
NEGATIVE_ID = "NG-2026-07-28-A13-K2K-BESSEL-CROSS-CONTRACTION-ORIGIN-DEBT"
CLAIM_DIR = REPO / "claims" / CLAIM
PRIMARY = REPO / "codes/foundations/a13_classii_scalar_k2k_effective_boundary_interval_seed.py"
INDEPENDENT = REPO / "codes/foundations/a13_classii_scalar_k2k_effective_boundary_interval_seed_independent.py"
VERIFIER = Path(__file__).resolve()
NOTE = CLAIM_DIR / "notes/classii-scalar-k2k-effective-boundary-and-directed-rounding-seed-260728-v1.0.tex.txt"
PDF = CLAIM_DIR / "notes/classii-scalar-k2k-effective-boundary-and-directed-rounding-seed-260728-v1.0.pdf"
MANIFEST = CLAIM_DIR / "classii_scalar_k2k_effective_boundary_interval_seed_manifest.json"
PRIMARY_RESULT = CLAIM_DIR / "runs/2026-07-28-primary-scalar-k2k-effective-boundary-interval-seed/result.json"
INDEPENDENT_RESULT = CLAIM_DIR / "runs/2026-07-28-independent-scalar-k2k-effective-boundary-interval-seed/result.json"
OUTPUT = CLAIM_DIR / "runs/2026-07-28-integrated-scalar-k2k-effective-boundary-interval-seed/result.json"

# Test-count oracles are tooling metadata, not theorem constants.
PRIMARY_ASSERTION_ORACLE = 75
INDEPENDENT_ASSERTION_ORACLE = 64
INTEGRATED_ASSERTION_ORACLE = 180

AUTHORITY_MANIFESTS = {
    "r063": f"claims/{CLAIM}/classii_balanced_coefficient_jet_continuum_manifest.json",
    "r087": f"claims/{CLAIM}/classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json",
    "r103": f"claims/{CLAIM}/classii_regular_complete_packet_ownership_hn_reg_closure_manifest.json",
    "r105": f"claims/{CLAIM}/classii_cartan_rational_subdivision_smart_path_boundary_manifest.json",
    "r111": f"claims/{CLAIM}/classii_scalar_k2k_projective_compact_core_boundary_manifest.json",
    "r112": f"claims/{CLAIM}/classii_scalar_k2k_covariance_simplex_uniform_compact_core_manifest.json",
}

NOTE_TOKENS = (
    "R-113",
    "A13-CLASSII-SCALAR-K2K-EFFECTIVE-BOUNDARY-",
    "DIRECTED-ROUNDING-SEED",
    "Effective projective wedges",
    "Effective origin and covariance faces",
    "Sharper phase-minimum floors",
    "First directed-rounding mixed box",
    "Failed contraction and remaining theorem",
    "global-cover flag false",
    "does not prove the mixed",
    "zero-amplitude boundary",
    "Arb union",
    "Sector A remain open",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def canonical_results_hash(record: dict[str, Any]) -> str:
    encoded = json.dumps(record.get("results"), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def result_passes(record: dict[str, Any], expected: int) -> bool:
    assertions = record.get("assertions")
    names = record.get("assertion_names")
    return (
        record.get("status") == "PASS"
        and record.get("assertions_total") == expected
        and record.get("assertions_passed") == expected
        and record.get("assertions_failed") == 0
        and isinstance(assertions, list)
        and len(assertions) == expected
        and isinstance(names, list)
        and len(names) == expected
        and len(set(map(str, names))) == expected
        and all(isinstance(row, dict) and row.get("status") == "PASS" for row in assertions)
        and record.get("results_sha256") == canonical_results_hash(record)
    )


def execute_child(script: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tect-r113-child-") as directory:
        output = Path(directory) / "result.json"
        process = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=360,
        )
        if process.returncode != 0:
            return {"execution_error": process.stderr or process.stdout, "returncode": process.returncode}
        record = load_json(output)
        record["returncode"] = process.returncode
        record["stdout"] = process.stdout.strip()
        return record


def compact(value: object) -> str:
    return "".join(str(value).replace("^", "**").split())


def arb_text_upper(value: object) -> Decimal:
    text = str(value).strip()
    match = re.fullmatch(r"\[([^\s]+) \+/- ([^\]]+)\]", text)
    if match:
        return Decimal(match.group(1)) + Decimal(match.group(2))
    return Decimal(text)


def main() -> int:
    rows: list[dict[str, object]] = []

    def add(group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    manifest = load_json(MANIFEST)
    pinned_primary = load_json(PRIMARY_RESULT)
    pinned_independent = load_json(INDEPENDENT_RESULT)

    source_paths = {
        "primary": PRIMARY,
        "independent": INDEPENDENT,
        "verifier": VERIFIER,
        "proof_note": NOTE,
    }
    for label, path in source_paths.items():
        item = manifest.get("sources", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("preflight", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("preflight", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    child_paths = {"primary": PRIMARY_RESULT, "independent": INDEPENDENT_RESULT}
    for label, path in child_paths.items():
        item = manifest.get("child_results", {}).get(label, {})
        relative = path.relative_to(REPO).as_posix()
        add("preflight", f"{label} result path", item.get("path") == relative, item.get("path"), relative)
        add("preflight", f"{label} result digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    for label, relative in AUTHORITY_MANIFESTS.items():
        item = manifest.get("authority", {}).get(label, {}).get("manifest", {})
        path = REPO / relative
        add("authority", f"{label} path", item.get("path") == relative, item.get("path"), relative)
        add("authority", f"{label} digest", item.get("sha256") == digest(path), item.get("sha256"), digest(path))

    pdf_item = manifest.get("proof_pdf", {})
    pdf_relative = PDF.relative_to(REPO).as_posix()
    add("preflight", "PDF path", pdf_item.get("path") == pdf_relative, pdf_item.get("path"), pdf_relative)
    add("preflight", "PDF digest", pdf_item.get("sha256") == digest(PDF), pdf_item.get("sha256"), digest(PDF))

    preflight_failed = [row for row in rows if row["status"] != "PASS"]
    if preflight_failed:
        print("R-113 preflight hash/authority gate failed; child execution was not started.")
        for row in preflight_failed:
            print(f"  {row['group']}::{row['name']}: {row['actual']} != {row['expected']}")
        return 1

    executed_primary = execute_child(PRIMARY)
    executed_independent = execute_child(INDEPENDENT)
    child_contracts = (
        ("primary", pinned_primary, executed_primary, PRIMARY_ASSERTION_ORACLE, manifest["run_contract"]["primary_schema"]),
        ("independent", pinned_independent, executed_independent, INDEPENDENT_ASSERTION_ORACLE, manifest["run_contract"]["independent_schema"]),
    )
    for label, pinned, executed, expected, schema in child_contracts:
        add("execution", f"{label} pinned PASS contract", result_passes(pinned, expected), pinned.get("assertions_total"), expected)
        add("execution", f"{label} fresh PASS contract", result_passes(executed, expected), executed.get("assertions_total"), expected)
        add("execution", f"{label} pinned schema", pinned.get("schema") == schema, pinned.get("schema"), schema)
        add("execution", f"{label} fresh schema", executed.get("schema") == schema, executed.get("schema"), schema)
        source_version = manifest["sources"][label]["version"]
        add("execution", f"{label} pinned version", pinned.get("version") == source_version, pinned.get("version"), source_version)
        add("execution", f"{label} fresh version", executed.get("version") == source_version, executed.get("version"), source_version)
        add("execution", f"{label} return code", executed.get("returncode") == 0, executed.get("returncode"), 0)
        add("execution", f"{label} deterministic results", executed.get("results_sha256") == pinned.get("results_sha256"), executed.get("results_sha256"), pinned.get("results_sha256"))
        add("execution", f"{label} assertion-name stability", executed.get("assertion_names") == pinned.get("assertion_names"), len(executed.get("assertion_names", [])), len(pinned.get("assertion_names", [])))

    primary = pinned_primary["results"]
    independent = pinned_independent["results"]
    p_projective = primary["effective_projective_patches"]
    i_projective = independent["effective_projective_patches"]
    add("cross", "four projective wedges", len(p_projective) == len(i_projective) == 4, (len(p_projective), len(i_projective)), 4)
    for index, (p_row, i_row) in enumerate(zip(p_projective, i_projective)):
        for key in ("x_interval", "tau_over_x_max", "derivative_envelope_q_star_cap", "exact_sixth_log_constant", "certified_gap_lower"):
            add("cross", f"projective wedge {index} {key}", p_row.get(key) == i_row.get(key), p_row.get(key), i_row.get(key))

    add("cross", "origin square threshold", primary["origin_square_threshold"] == independent["origin_square_threshold"] == "16/285418875", (primary["origin_square_threshold"], independent["origin_square_threshold"]), "16/285418875")
    add("cross", "eight origin cones", len(primary["origin_cones"]) == 8, len(primary["origin_cones"]), 8)
    add("cross", "central c floor", primary["quantitative_faces"]["uniform_c_interior_floor"] == independent["uniform_c_interior_floor"] == "1/100552401097327200", (primary["quantitative_faces"]["uniform_c_interior_floor"], independent["uniform_c_interior_floor"]), "1/100552401097327200")
    add("cross", "face margins", primary["quantitative_faces"]["margins"] == independent["quantitative_faces"]["margins"], primary["quantitative_faces"]["margins"], independent["quantitative_faces"]["margins"])
    add("cross", "face Lipschitz bound", primary["quantitative_faces"]["lipschitz"] == independent["quantitative_faces"]["lipschitz"], primary["quantitative_faces"]["lipschitz"], independent["quantitative_faces"]["lipschitz"])
    add("cross", "four face width lower bounds", primary["quantitative_faces"]["four_width_lower_bounds"] == independent["quantitative_faces"]["four_width_lower_bounds"], primary["quantitative_faces"]["four_width_lower_bounds"], independent["quantitative_faces"]["four_width_lower_bounds"])
    add("cross", "B6 completion", compact(primary["sharper_phase_floors"]["B6"]) == compact(independent["sharper_phase_floors"]["B6"]), primary["sharper_phase_floors"]["B6"], independent["sharper_phase_floors"]["B6"])
    add("cross", "B10 completion", compact(primary["sharper_phase_floors"]["B10"]) == compact(independent["sharper_phase_floors"]["B10"]), primary["sharper_phase_floors"]["B10"], independent["sharper_phase_floors"]["B10"])
    add("cross", "zero-amplitude threshold", primary["sharper_phase_floors"]["zero_amplitude_uniform_tau"] == independent["sharper_phase_floors"]["zero_amplitude_uniform_tau"] == ">=13", (primary["sharper_phase_floors"]["zero_amplitude_uniform_tau"], independent["sharper_phase_floors"]["zero_amplitude_uniform_tau"]), ">=13")
    add("cross", "runtime versions agree", primary["runtime_versions"] == independent["runtime_versions"] == {"sympy": "1.14.0", "python-flint": "0.9.0"}, (primary["runtime_versions"], independent["runtime_versions"]), {"sympy": "1.14.0", "python-flint": "0.9.0"})

    p_seed = primary["directed_rounding_seed"]
    i_seed = independent["directed_rounding_seed"]
    expected_box = {"c": "[49/100,51/100]", "x": "[99/100,101/100]", "tau": "[99/100,101/100]"}
    add("cross", "same exact strict mixed box", p_seed["parameter_box"] == i_seed["parameter_box"] == expected_box, (p_seed["parameter_box"], i_seed["parameter_box"]), expected_box)
    add("cross", "same radial radius", p_seed["radial_radius"] == i_seed["radial_radius"] == 50, (p_seed["radial_radius"], i_seed["radial_radius"]), 50)
    add("cross", "same Arb precision", p_seed["precision_dps"] == i_seed["precision_dps"] == 40, (p_seed["precision_dps"], i_seed["precision_dps"]), 40)
    add("cross", "same residual enclosure", p_seed["residual_ball"] == i_seed["residual_ball"] and p_seed["residual_upper"] == i_seed["residual_upper"], (p_seed["residual_ball"], p_seed["residual_upper"]), (i_seed["residual_ball"], i_seed["residual_upper"]))
    add("cross", "same analytic tail enclosure", p_seed["tail_upper"] == i_seed["tail_upper"], p_seed["tail_upper"], i_seed["tail_upper"])
    add("cross", "both residual strict", p_seed["residual_strict"] is i_seed["residual_strict"] is True, (p_seed["residual_strict"], i_seed["residual_strict"]), True)
    add("cross", "both target strict", p_seed["target_strict"] is i_seed["target_strict"] is True, (p_seed["target_strict"], i_seed["target_strict"]), True)
    add("cross", "primary Arb upper below one", arb_text_upper(p_seed["normalized_total_upper"]) < Decimal(1), p_seed["normalized_total_upper"], "<1")
    add("cross", "independent Arb upper below one", arb_text_upper(i_seed["normalized_total_upper"]) < Decimal(1), i_seed["normalized_total_upper"], "<1")
    add("cross", "primary published cutoff", arb_text_upper(p_seed["normalized_total_upper"]) < Decimal("0.966850"), p_seed["normalized_total_upper"], "<0.966850")
    add("cross", "independent published cutoff", arb_text_upper(i_seed["normalized_total_upper"]) < Decimal("0.976002"), i_seed["normalized_total_upper"], "<0.976002")
    add("cross", "primary core below total", arb_text_upper(p_seed["core_upper"]) < arb_text_upper(p_seed["normalized_total_upper"]), (p_seed["core_upper"], p_seed["normalized_total_upper"]), "core<total")
    add("cross", "independent core below total", arb_text_upper(i_seed["core_upper"]) < arb_text_upper(i_seed["normalized_total_upper"]), (i_seed["core_upper"], i_seed["normalized_total_upper"]), "core<total")
    add("cross", "different cell budgets", p_seed["cells"] == 20_000 and i_seed["cells"] == 30_000, (p_seed["cells"], i_seed["cells"]), (20_000, 30_000))
    add("cross", "independent partition declared", "initial_partition" in i_seed and "refinement_priority" in i_seed, sorted(i_seed), "two independent routing fields")
    independent_source = INDEPENDENT.read_text(encoding="utf-8")
    add("cross", "independent does not import primary", PRIMARY.stem not in independent_source, PRIMARY.stem in independent_source, False)
    add("scope", "primary global cover false", primary["central_residual_set"]["global_interval_cover_complete"] is False, primary["central_residual_set"]["global_interval_cover_complete"], False)
    add("scope", "independent global cover false", independent["global_interval_cover_complete"] is False, independent["global_interval_cover_complete"], False)
    add("scope", "failed contraction is not counterexample", primary["method_boundary"]["target_counterexample"] is independent["target_counterexample"] is False, (primary["method_boundary"]["target_counterexample"], independent["target_counterexample"]), False)

    note_text = NOTE.read_text(encoding="utf-8")
    for token in NOTE_TOKENS:
        add("note", f"token {token}", token in note_text, token in note_text, True)
    add("note", "forbid boundary-free overclaim", "boundary-free rational compact set" not in note_text, "boundary-free rational compact set" in note_text, False)

    reader = PdfReader(str(PDF))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    add("pdf", "page count", len(reader.pages) == 7, len(reader.pages), 7)
    add("pdf", "manifest page count", pdf_item.get("pages") == len(reader.pages), pdf_item.get("pages"), len(reader.pages))
    add("pdf", "size", pdf_item.get("size_bytes") == PDF.stat().st_size, pdf_item.get("size_bytes"), PDF.stat().st_size)
    add("pdf", "visual QA", pdf_item.get("visual_qa") == "PASS", pdf_item.get("visual_qa"), "PASS")
    add("pdf", "form check", pdf_item.get("form_check") == "PASS", pdf_item.get("form_check"), "PASS")
    add("pdf", "zero overfull", pdf_item.get("overfull_hbox_count") == 0, pdf_item.get("overfull_hbox_count"), 0)
    add("pdf", "no forms", not bool(reader.get_fields()), bool(reader.get_fields()), False)
    add("pdf", "title extracted", "directed-rounding seed" in extracted.lower(), "directed-rounding seed" in extracted.lower(), True)
    add("pdf", "R-113 extracted", "R-113" in extracted, "R-113" in extracted, True)
    add("pdf", "no literal qquad debris", "qquad" not in extracted, "qquad" in extracted, False)

    requirements = (REPO / "requirements.txt").read_text(encoding="utf-8")
    doctor = (REPO / "verification/scripts/doctor.py").read_text(encoding="utf-8")
    add("environment", "sympy pinned", "sympy==1.14.0" in requirements, "sympy==1.14.0" in requirements, True)
    add("environment", "python-flint pinned", "python-flint==0.9.0" in requirements, "python-flint==0.9.0" in requirements, True)
    add("environment", "doctor checks sympy", 'find_spec("sympy")' in doctor, 'find_spec("sympy")' in doctor, True)
    add("environment", "doctor checks flint", 'find_spec("flint")' in doctor, 'find_spec("flint")' in doctor, True)

    contract = manifest.get("run_contract", {})
    add("contract", "primary assertions", contract.get("primary_assertions") == PRIMARY_ASSERTION_ORACLE, contract.get("primary_assertions"), PRIMARY_ASSERTION_ORACLE)
    add("contract", "independent assertions", contract.get("independent_assertions") == INDEPENDENT_ASSERTION_ORACLE, contract.get("independent_assertions"), INDEPENDENT_ASSERTION_ORACLE)
    add("contract", "primary output", contract.get("primary_output") == PRIMARY_RESULT.relative_to(REPO).as_posix(), contract.get("primary_output"), PRIMARY_RESULT.relative_to(REPO).as_posix())
    add("contract", "independent output", contract.get("independent_output") == INDEPENDENT_RESULT.relative_to(REPO).as_posix(), contract.get("independent_output"), INDEPENDENT_RESULT.relative_to(REPO).as_posix())
    add("contract", "integrated output", contract.get("integrated_output") == OUTPUT.relative_to(REPO).as_posix(), contract.get("integrated_output"), OUTPUT.relative_to(REPO).as_posix())
    canonical_command = r"E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/a13_classii_scalar_k2k_effective_boundary_interval_seed_verify.py"
    add("contract", "reproduction command", contract.get("command") == canonical_command, contract.get("command"), canonical_command)

    public_checks = {
        "claim card": (CLAIM_DIR / "claim.md", "R-113"),
        "status card": (CLAIM_DIR / "status.json", "R-113"),
        "results ledger": (REPO / "RESULTS-LEDGER.md", '<a id="r-113"></a>'),
        "negative registry": (REPO / "negative-results/registry.md", NEGATIVE_ID),
        "exploration ledger first": (REPO / "explorations/log.jsonl", '"id":"EXP-000318"'),
        "exploration ledger last": (REPO / "explorations/log.jsonl", '"id":"EXP-000324"'),
        "roadmap": (REPO / "ROADMAP.md", "R-113"),
        "theorem map": (REPO / "governance/sector-a-theorem-map.json", "R-113"),
        "todo": (REPO / "TODO.md", "R-113"),
        "main proof line": (REPO / "theory/main-proof-line.md", "R-113"),
        "proof map markdown": (REPO / "theory/proof-evidence-map.md", "R-113"),
        "proof map json": (REPO / "verification/proof-evidence-map.json", "R-113"),
        "changelog": (REPO / "CHANGELOG.md", "R-113 effective scalar boundary and directed-rounding seed"),
    }
    for name, (path, token) in public_checks.items():
        body = path.read_text(encoding="utf-8")
        add("public", name, token in body, token in body, True)

    add("manifest", "claim id", manifest.get("claim_id") == CLAIM, manifest.get("claim_id"), CLAIM)
    add("manifest", "result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID)
    add("manifest", "result ledger id", manifest.get("consequence", {}).get("result_ledger_id") == "R-113", manifest.get("consequence", {}).get("result_ledger_id"), "R-113")
    add("manifest", "negative record", manifest.get("negative_results") == [NEGATIVE_ID], manifest.get("negative_results"), [NEGATIVE_ID])
    add("manifest", "exploration range", manifest.get("explorations") == [f"EXP-{index:06d}" for index in range(318, 325)], manifest.get("explorations"), "EXP-000318--EXP-000324")
    add("manifest", "proof incomplete", manifest.get("proof_complete") is False, manifest.get("proof_complete"), False)
    add("manifest", "tier unchanged", manifest.get("tier_before") == manifest.get("tier_after") == "T4", (manifest.get("tier_before"), manifest.get("tier_after")), "T4/T4")

    consequence = manifest.get("consequence", {})
    for name in (
        "effective_projective_wedges",
        "effective_origin_cover",
        "effective_covariance_face_widths",
        "sharper_phase_minimum_floor",
        "zero_amplitude_tau_ge_13",
        "first_strict_mixed_arb_box",
        "independent_directed_rounding_reproduction",
    ):
        add("scope", f"established {name}", consequence.get(name) is True, consequence.get(name), True)
    for name in (
        "global_mixed_scalar_interval_cover",
        "mixed_all_q_scalar_k2k",
        "full_a1_embedding",
        "adapted_production_cluster",
        "one_use_source_sextic_aggregation",
        "full_overlap_src",
        "nelson",
        "sector_a_closure",
        "reg_scope_newly_closed",
        "fixed_cutoff_core_newly_closed",
    ):
        add("scope", f"consequence remains false {name}", consequence.get(name) is False, consequence.get(name), False)
    for name, value in manifest.get("claims_not_established", {}).items():
        add("scope", f"not established {name}", value is False, value, False)

    if INTEGRATED_ASSERTION_ORACLE:
        predicted_total = len(rows) + 3
        add("contract", "integrated assertion oracle", predicted_total == INTEGRATED_ASSERTION_ORACLE, predicted_total, INTEGRATED_ASSERTION_ORACLE)
        add("contract", "manifest integrated assertions", contract.get("integrated_assertions") == INTEGRATED_ASSERTION_ORACLE, contract.get("integrated_assertions"), INTEGRATED_ASSERTION_ORACLE)
        add("contract", "aggregate assertions", contract.get("aggregate_assertions") == PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE, contract.get("aggregate_assertions"), PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + INTEGRATED_ASSERTION_ORACLE)

    failed = [row for row in rows if row["status"] != "PASS"]
    integrated_total = len(rows)
    aggregate = PRIMARY_ASSERTION_ORACLE + INDEPENDENT_ASSERTION_ORACLE + integrated_total
    results = {
        "result_id": RESULT_ID,
        "preflight_hash_gate": "PASS",
        "children_reexecuted": True,
        "child_results_match_pins": not any(row["status"] != "PASS" for row in rows if row["group"] == "execution"),
        "effective_boundary_cross_audit": "PASS" if not failed else "FAIL",
        "proof_pdf_pages": len(reader.pages),
        "first_strict_mixed_arb_box": not any(row["status"] != "PASS" for row in rows if row["group"] == "cross"),
        "global_mixed_scalar_interval_cover": False,
        "mixed_all_q_scalar_k2k": False,
        "target_counterexample": False,
        "full_a1_embedding": False,
        "sector_a_closure": False,
    }
    payload: dict[str, Any] = {
        "schema": "tect/a13-scalar-k2k-effective-boundary-interval-seed-integrated/1.0",
        "version": __version__,
        "status": "PASS" if not failed else "FAIL",
        "assertions_total": integrated_total,
        "assertions_passed": integrated_total - len(failed),
        "assertions_failed": len(failed),
        "assertions": rows,
        "assertion_names": [f"{row['group']}::{row['name']}" for row in rows],
        "aggregate_assertions": aggregate,
        "child_assertions": {"primary": PRIMARY_ASSERTION_ORACLE, "independent": INDEPENDENT_ASSERTION_ORACLE},
        "source_hashes": {label: digest(path) for label, path in {**source_paths, "proof_pdf": PDF}.items()},
        "results": results,
        "results_sha256": hashlib.sha256(json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
    }
    atomic_json(OUTPUT, payload)
    for row in failed:
        print(f"FAIL {row['group']}::{row['name']}: {row['actual']} != {row['expected']}")
    print(f"Integrated R-113: {payload['assertions_passed']}/{integrated_total} PASS; aggregate {aggregate}/{aggregate}")
    print("global mixed scalar interval cover: false")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
