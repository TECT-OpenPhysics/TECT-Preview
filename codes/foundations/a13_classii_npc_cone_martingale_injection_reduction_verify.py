#!/usr/bin/env python3
"""Integrated verifier for the A13 NPC-cone/martingale-injection reduction."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import argparse
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_npc_cone_martingale_injection_reduction_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs/2026-07-23-integrated-npc-cone-martingale-injection-reduction/result.json"
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    actual: Any,
    expected: Any,
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def execute(script: Path) -> None:
    completed = subprocess.run([sys.executable, str(script)], cwd=REPO, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def imported_modules(script: Path) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(ast.parse(script.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    preflight_failures: list[tuple[str, str, str, str]] = []
    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            if actual != source["sha256"]:
                preflight_failures.append((group, key, actual, source["sha256"]))
    if preflight_failures:
        print(
            f"FAIL: hash preflight ({len(preflight_failures)} mismatch(es)); "
            "children not executed"
        )
        for group, key, actual, expected in preflight_failures:
            print(f" - {group}_{key}: {actual} != {expected}")
        return 1

    primary_script = REPO / manifest["sources"]["primary"]["path"]
    independent_script = REPO / manifest["sources"]["independent"]["path"]
    primary_output = REPO / manifest["run_contract"]["primary_output"]
    independent_output = REPO / manifest["run_contract"]["independent_output"]
    execute(primary_script)
    execute(independent_script)
    primary = json.loads(primary_output.read_text(encoding="utf-8"))
    independent = json.loads(independent_output.read_text(encoding="utf-8"))
    p = primary["computed"]
    i = independent["computed"]
    tolerance = float(manifest["integrated_audit"]["identity_tolerance"])
    rows: list[dict[str, Any]] = []

    for group in ("authority", "sources"):
        for key, source in manifest[group].items():
            actual = digest(REPO / source["path"])
            add(
                rows,
                f"{group}_{key}_hash",
                actual == source["sha256"],
                actual,
                source["sha256"],
            )

    contract = manifest["run_contract"]
    expected_primary = int(contract["primary_assertions"])
    expected_independent = int(contract["independent_assertions"])
    add(
        rows,
        "verifier_version",
        __version__ == manifest["sources"]["verifier"]["version"],
        __version__,
        manifest["sources"]["verifier"]["version"],
    )
    add(
        rows,
        "primary_schema",
        primary.get("schema") == contract["primary_schema"],
        primary.get("schema"),
        contract["primary_schema"],
    )
    add(
        rows,
        "independent_schema",
        independent.get("schema") == contract["independent_schema"],
        independent.get("schema"),
        contract["independent_schema"],
    )
    add(
        rows,
        "primary_version",
        primary.get("script_version") == manifest["sources"]["primary"]["version"],
        primary.get("script_version"),
        manifest["sources"]["primary"]["version"],
    )
    add(
        rows,
        "independent_version",
        independent.get("script_version")
        == manifest["sources"]["independent"]["version"],
        independent.get("script_version"),
        manifest["sources"]["independent"]["version"],
    )
    add(
        rows,
        "child_source_freshness",
        primary.get("source_sha256") == manifest["sources"]["primary"]["sha256"]
        and independent.get("source_sha256")
        == manifest["sources"]["independent"]["sha256"],
        [primary.get("source_sha256"), independent.get("source_sha256")],
        [
            manifest["sources"]["primary"]["sha256"],
            manifest["sources"]["independent"]["sha256"],
        ],
    )
    add(rows, "primary_pass", primary.get("pass") is True, primary.get("pass"), True)
    add(
        rows,
        "independent_pass",
        independent.get("pass") is True,
        independent.get("pass"),
        True,
    )
    add(
        rows,
        "primary_assertion_contract",
        primary.get("assertion_count") == expected_primary,
        primary.get("assertion_count"),
        expected_primary,
    )
    add(
        rows,
        "independent_assertion_contract",
        independent.get("assertion_count") == expected_independent,
        independent.get("assertion_count"),
        expected_independent,
    )
    add(
        rows,
        "primary_assertion_flags",
        len(primary.get("assertions", {})) == expected_primary
        and all(value is True for value in primary.get("assertions", {}).values()),
        {
            "length": len(primary.get("assertions", {})),
            "false": [
                key
                for key, value in primary.get("assertions", {}).items()
                if value is not True
            ],
        },
        {"length": expected_primary, "false": []},
    )
    add(
        rows,
        "independent_assertion_flags",
        len(independent.get("assertions", {})) == expected_independent
        and all(value is True for value in independent.get("assertions", {}).values()),
        {
            "length": len(independent.get("assertions", {})),
            "false": [
                key
                for key, value in independent.get("assertions", {}).items()
                if value is not True
            ],
        },
        {"length": expected_independent, "false": []},
    )
    result_id = manifest["result_id"]
    add(
        rows,
        "shared_result_id",
        primary.get("result_id") == independent.get("result_id") == result_id,
        [primary.get("result_id"), independent.get("result_id")],
        result_id,
    )

    strict_path = REPO / manifest["authority"]["a13_strict_past_manifest"]["path"]
    strict = json.loads(strict_path.read_text(encoding="utf-8"))
    expected_q = 1.0 / (2.0 * float(strict["audit"]["epsilon_control"]))
    add(
        rows,
        "q_derived_from_strict_past_authority",
        abs(float(primary["inputs"]["q"]) - expected_q) < tolerance
        and i["exact_model_arithmetic"]["q_fraction"] == "10/9",
        [primary["inputs"]["q"], i["exact_model_arithmetic"]["q_fraction"]],
        [expected_q, "10/9"],
    )
    add(
        rows,
        "child_authority_freshness",
        primary["inputs"]["translation_authority_sha256"]
        == independent["inputs"]["translation_authority_sha256"]
        == manifest["authority"]["a13_translation_manifest"]["sha256"]
        and primary["inputs"]["strict_past_authority_sha256"]
        == independent["inputs"]["strict_past_authority_sha256"]
        == manifest["authority"]["a13_strict_past_manifest"]["sha256"],
        {
            "translation": [
                primary["inputs"]["translation_authority_sha256"],
                independent["inputs"]["translation_authority_sha256"],
            ],
            "strict": [
                primary["inputs"]["strict_past_authority_sha256"],
                independent["inputs"]["strict_past_authority_sha256"],
            ],
        },
        "pinned authority hashes",
    )

    pf = p["factorisation"]
    ia = i["exact_model_arithmetic"]
    add(
        rows,
        "nelson_aligned_factorisation_exponent",
        abs(float(pf["alpha"]) - 5.0 / 9.0) < tolerance
        and abs(float(pf["nelson_exponent"]) - 10.0 / 9.0) < tolerance
        and ia["alpha_fraction"] == "5/9"
        and ia["two_alpha_fraction"] == "10/9",
        [pf["alpha"], pf["nelson_exponent"], ia["alpha_fraction"], ia["two_alpha_fraction"]],
        [5.0 / 9.0, 10.0 / 9.0, "5/9", "10/9"],
    )
    add(
        rows,
        "production_q_spd",
        float(pf["a"]) > 0.0
        and float(pf["c"]) > 0.0
        and float(pf["determinant"]) > 0.0
        and float(ia["determinant"]) > 0.0,
        [pf["a"], pf["c"], pf["determinant"], ia["determinant"]],
        "all positive",
    )
    add(
        rows,
        "independent_coefficients_agree",
        max(
            abs(float(pf[key]) - float(ia[key]))
            for key in ("a", "b", "c", "determinant")
        )
        < tolerance,
        {key: [pf[key], ia[key]] for key in ("a", "b", "c", "determinant")},
        f"pairwise residual<{tolerance}",
    )
    cone = p["cone"]
    geometry = i["geometry"]
    add(
        rows,
        "exact_production_cone_ratios",
        abs(float(cone["logarithmic_slope"]) - 9.0 / 5.0) < tolerance
        and abs(float(cone["sphere_ratio"]) - 113.0 / 32.0) < tolerance
        and abs(float(cone["line_ratio"]) - 25.0 / 32.0) < tolerance
        and ia["logarithmic_slope_fraction"] == "9/5"
        and ia["sphere_ratio_fraction"] == "113/32"
        and ia["line_ratio_fraction"] == "25/32",
        [
            cone["logarithmic_slope"],
            cone["sphere_ratio"],
            cone["line_ratio"],
            ia["logarithmic_slope_fraction"],
            ia["sphere_ratio_fraction"],
            ia["line_ratio_fraction"],
        ],
        [9.0 / 5.0, 113.0 / 32.0, 25.0 / 32.0, "9/5", "113/32", "25/32"],
    )
    add(
        rows,
        "cone_metric_and_factorisation_residuals",
        max(
            float(pf["maximum_factorisation_residual"]),
            float(pf["maximum_transformed_residual"]),
            float(cone["maximum_metric_residual"]),
            float(geometry["maximum_factorisation_residual"]),
            float(geometry["maximum_cone_residual"]),
        )
        < tolerance,
        {
            "primary_factor": pf["maximum_factorisation_residual"],
            "primary_weight": pf["maximum_transformed_residual"],
            "primary_cone": cone["maximum_metric_residual"],
            "independent_factor": geometry["maximum_factorisation_residual"],
            "independent_cone": geometry["maximum_cone_residual"],
        },
        f"<{tolerance}",
    )
    add(
        rows,
        "npc_and_cat1_diagnostics",
        float(cone["sphere_sectional_curvature"]) < 0.0
        and float(cone["sphere_line_sectional_curvature"]) < 0.0
        and float(geometry["sphere_plane_curvature_coefficient"]) < 0.0
        and float(cone["shortest_base_closed_geodesic"])
        > float(cone["cat1_closed_geodesic_threshold"]),
        {
            "primary_curvatures": [
                cone["sphere_sectional_curvature"],
                cone["sphere_line_sectional_curvature"],
            ],
            "independent_sphere_coefficient": geometry[
                "sphere_plane_curvature_coefficient"
            ],
            "closed_geodesic": cone["shortest_base_closed_geodesic"],
        },
        "negative smooth curvatures and base closed geodesic >2pi",
    )

    pw = p["positive_offset_witness"]
    iw = i["positive_offset_witness"]
    exact_witness = {
        "base": "12701/20000",
        "cross": "-3/800",
        "square": "81682713/204800000000",
        "increment": "-686317287/204800000000",
    }
    add(
        rows,
        "exact_positive_offset_witness",
        pw["base_I_fraction"] == iw["base_fraction"] == exact_witness["base"]
        and pw["cross_I_fraction"] == iw["cross_fraction"] == exact_witness["cross"]
        and pw["retained_square_I_fraction"]
        == iw["square_fraction"]
        == exact_witness["square"]
        and pw["increment_I_fraction"]
        == iw["increment_fraction"]
        == exact_witness["increment"],
        {
            "primary": [
                pw["base_I_fraction"],
                pw["cross_I_fraction"],
                pw["retained_square_I_fraction"],
                pw["increment_I_fraction"],
            ],
            "independent": [
                iw["base_fraction"],
                iw["cross_fraction"],
                iw["square_fraction"],
                iw["increment_fraction"],
            ],
        },
        exact_witness,
    )
    add(
        rows,
        "retained_square_positive_secant_negative",
        float(pw["retained_square_I"]) > 0.0
        and float(iw["square"]) > 0.0
        and float(pw["increment_I"]) < 0.0
        and float(iw["increment"]) < 0.0,
        [pw["retained_square_I"], iw["square"], pw["increment_I"], iw["increment"]],
        "squares positive, increments negative",
    )
    add(
        rows,
        "positive_floor_witness_certified",
        float(pw["interpolation_lower_bound"]) > 0.0
        and float(iw["interpolation_lower_bound"]) > 0.0
        and float(pw["certified_full_energy_increment_upper_bound"]) < 0.0
        and float(iw["certified_full_energy_increment_upper_bound"]) < 0.0,
        {
            "lower_bounds": [
                pw["interpolation_lower_bound"],
                iw["interpolation_lower_bound"],
            ],
            "energy_upper_bounds": [
                pw["certified_full_energy_increment_upper_bound"],
                iw["certified_full_energy_increment_upper_bound"],
            ],
        },
        "positive fields and strictly negative full-Q upper bounds",
    )
    add(
        rows,
        "independent_witness_quadratures_agree",
        abs(
            float(pw["numerical_full_energy_increment"])
            - float(iw["legendre_full_energy_increment"])
        )
        < tolerance,
        [pw["numerical_full_energy_increment"], iw["legendre_full_energy_increment"]],
        f"difference<{tolerance}",
    )

    pt = p["raw_energy_telescope"]
    it = i["raw_energy_telescope"]
    add(
        rows,
        "raw_energy_injection_telescopes",
        float(pt["controlled_telescope_residual"]) < tolerance
        and float(it["telescope_residual"]) < tolerance,
        [pt["controlled_telescope_residual"], it["telescope_residual"]],
        f"both<{tolerance}",
    )
    add(
        rows,
        "zero_control_terminal_injection_cancellation",
        float(pt["zero_control_cancellation_residual"]) < tolerance
        and abs(float(pt["zero_control_secant_expectation"])) < tolerance,
        [pt["zero_control_cancellation_residual"], pt["zero_control_secant_expectation"]],
        [f"<{tolerance}", f"abs<{tolerance}"],
    )
    add(
        rows,
        "injection_levels_positive",
        min(float(value) for value in pt["controlled_injection_levels"]) > 0.0
        and min(float(value) for value in it["injection_levels"]) > 0.0,
        [pt["controlled_injection_levels"], it["injection_levels"]],
        "all positive",
    )

    pr = p["isolated_resonance_diagnostic"]
    ir = i["isolated_resonance_diagnostic"]
    add(
        rows,
        "isolated_resonance_shell_powers",
        pr["mode_two_shell_loss_power"]
        == ir["shell_loss_powers"]["mode_two"]
        == -5
        and pr["mode_three_shell_loss_power"]
        == ir["shell_loss_powers"]["mode_three"]
        == -9,
        [
            pr["mode_two_shell_loss_power"],
            ir["shell_loss_powers"]["mode_two"],
            pr["mode_three_shell_loss_power"],
            ir["shell_loss_powers"]["mode_three"],
        ],
        [-5, -5, -9, -9],
    )
    add(
        rows,
        "isolated_resonance_completion_and_summability",
        float(pr["minimum_mode_two_completion_slack"]) >= 0.0
        and float(pr["minimum_mode_three_completion_slack"]) >= 0.0
        and float(ir["minimum_completion_slack"]) >= 0.0
        and max(float(value) for value in ir["dyadic_shell_ratios"].values()) < 1.0,
        {
            "primary_slacks": [
                pr["minimum_mode_two_completion_slack"],
                pr["minimum_mode_three_completion_slack"],
            ],
            "independent_slack": ir["minimum_completion_slack"],
            "ratios": ir["dyadic_shell_ratios"],
        },
        "nonnegative slacks and ratios<1",
    )
    pb = p["bare_npc_one_shot_countermodel"]
    ib = i["flat_cone_one_shot_countermodel"]
    add(
        rows,
        "bare_npc_one_shot_countermodels_diverge",
        float(pb["asymptotic_objective_slope"]) < 0.0
        and float(ib["asymptotic_slope"]) < 0.0
        and float(pb["allocated_objective"]) < 0.0
        and float(ib["allocated_objective"]) < 0.0,
        [
            pb["asymptotic_objective_slope"],
            ib["asymptotic_slope"],
            pb["allocated_objective"],
            ib["allocated_objective"],
        ],
        "all negative",
    )
    add(
        rows,
        "bare_npc_includes_additive_coordinate_sextic",
        float(pb["additive_coordinate_sixth_moment"])
        > float(pb["terminal_target_sixth_moment"])
        and float(ib["additive_coordinate_sixth_moment"]) > float(ib["sixth_moment"]),
        [
            pb["additive_coordinate_sixth_moment"],
            pb["terminal_target_sixth_moment"],
            ib["additive_coordinate_sixth_moment"],
            ib["sixth_moment"],
        ],
        "coordinate sextic grows with shell count",
    )
    add(
        rows,
        "weighted_carleson_completion_and_decay",
        float(pb["maximum_weighted_completion_residual"]) < tolerance
        and float(ib["maximum_weighted_completion_residual"]) < tolerance
        and float(pb["equal_coupling_partial_sum"])
        > float(pb["decaying_coupling_partial_sum"])
        and float(ib["equal_coupling_sum"]) > float(ib["decaying_coupling_sum"]),
        {
            "residuals": [
                pb["maximum_weighted_completion_residual"],
                ib["maximum_weighted_completion_residual"],
            ],
            "sums": [
                pb["equal_coupling_partial_sum"],
                pb["decaying_coupling_partial_sum"],
                ib["equal_coupling_sum"],
                ib["decaying_coupling_sum"],
            ],
        },
        "completion residuals small and decaying sums smaller",
    )

    note_path = REPO / manifest["sources"]["proof_note"]["path"]
    note_text = note_path.read_text(encoding="utf-8")
    required_tokens = tuple(manifest["integrated_audit"]["proof_note_required_tokens"])
    add(
        rows,
        "proof_note_required_content",
        all(token in note_text for token in required_tokens),
        [token for token in required_tokens if token not in note_text],
        [],
    )
    add(
        rows,
        "proof_note_mass_regularizer_boundary",
        "P=M_X^2+10^{-12}=4+10^{-12}" in note_text
        and "physical outer factor $1/2$" in note_text,
        [
            "P=M_X^2+10^{-12}=4+10^{-12}" in note_text,
            "physical outer factor $1/2$" in note_text,
        ],
        [True, True],
    )
    add(
        rows,
        "proof_note_strong_jacobi_remainder",
        "\\mathfrak J(U_0,U_1)" in note_text
        and "\\|\\nabla d_g(U_0,U_1)\\|_2^2" in note_text,
        [
            "\\mathfrak J(U_0,U_1)" in note_text,
            "\\|\\nabla d_g(U_0,U_1)\\|_2^2" in note_text,
        ],
        [True, True],
    )
    add(
        rows,
        "proof_note_bare_npc_and_carleson_boundary",
        "-1/2+\\eta+120\\zeta" in note_text
        and "NPC--Carleson/paradifferential" in note_text
        and "not a production counterexample:" in " ".join(note_text.split()),
        [
            "-1/2+\\eta+120\\zeta" in note_text,
            "NPC--Carleson/paradifferential" in note_text,
            "not a production counterexample:" in " ".join(note_text.split()),
        ],
        [True, True, True],
    )
    add(
        rows,
        "proof_note_no_overclaim",
        "It is not closed here." in note_text
        and "global injection balance" in note_text
        and "No claim:" in note_text,
        [
            "It is not closed here." in note_text,
            "global injection balance" in note_text,
            "No claim:" in note_text,
        ],
        [True, True, True],
    )

    pdf = manifest["proof_pdf"]
    pdf_path = REPO / pdf["path"]
    pdf_hash = digest(pdf_path)
    pdf_pages = len(PdfReader(str(pdf_path)).pages)
    add(rows, "proof_pdf_hash", pdf_hash == pdf["sha256"], pdf_hash, pdf["sha256"])
    add(
        rows,
        "proof_pdf_signature",
        pdf_path.read_bytes()[:5] == b"%PDF-",
        pdf_path.read_bytes()[:5].decode("ascii", errors="replace"),
        "%PDF-",
    )
    add(
        rows,
        "proof_pdf_size",
        pdf_path.stat().st_size == pdf["size_bytes"],
        pdf_path.stat().st_size,
        pdf["size_bytes"],
    )
    add(rows, "proof_pdf_pages", pdf_pages == pdf["pages"], pdf_pages, pdf["pages"])
    add(
        rows,
        "proof_pdf_qa",
        pdf["form_check"] == "PASS"
        and pdf["overfull_hbox_count"] == 0
        and pdf["visual_qa"] == "PASS",
        pdf,
        "form PASS, zero overfull, visual PASS",
    )

    status = json.loads((CLAIM / "status.json").read_text(encoding="utf-8"))
    claim_text = (CLAIM / "claim.md").read_text(encoding="utf-8")
    lineage_text = (CLAIM / "lineage-narrative.md").read_text(encoding="utf-8")
    gates_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    roadmap_text = (REPO / "ROADMAP.md").read_text(encoding="utf-8")
    todo_text = (REPO / "TODO.md").read_text(encoding="utf-8")
    todo_data = json.loads((REPO / "todo" / "todo.json").read_text(encoding="utf-8"))
    changelog_text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    changelog_records = [
        json.loads(line)
        for line in (REPO / "changelog" / "log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    results_text = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    negative_text = (REPO / "negative-results" / "registry.md").read_text(
        encoding="utf-8"
    )
    theorem_map = json.loads(
        (REPO / "governance" / "sector-a-theorem-map.json").read_text(encoding="utf-8")
    )
    next_gate = manifest["consequence"]["next_subgate"]
    umbrella = manifest["consequence"]["umbrella_gate"]
    negative_id = manifest["consequence"]["negative_result"]
    add(
        rows,
        "status_t4_and_umbrella_open",
        status.get("tier") == "T4" and status.get("open_gates") == [umbrella],
        [status.get("tier"), status.get("open_gates")],
        ["T4", [umbrella]],
    )
    add(
        rows,
        "status_records_result_and_next",
        result_id in status.get("statement", "")
        and next_gate in status.get("next_action", "")
        and status.get("reproduction", {}).get("command") == contract["command"],
        [
            result_id in status.get("statement", ""),
            next_gate in status.get("next_action", ""),
            status.get("reproduction", {}).get("command"),
        ],
        [True, True, contract["command"]],
    )
    add(
        rows,
        "claim_records_result_honesty_and_next",
        result_id in claim_text
        and next_gate in claim_text
        and "geodesic" in claim_text.lower()
        and "carleson" in claim_text.lower()
        and "one-use" in claim_text.lower(),
        [
            result_id in claim_text,
            next_gate in claim_text,
            "geodesic" in claim_text.lower(),
            "carleson" in claim_text.lower(),
            "one-use" in claim_text.lower(),
        ],
        [True, True, True, True, True],
    )
    add(
        rows,
        "gates_record_reduction_and_successor",
        result_id in gates_text
        and next_gate in gates_text
        and "REDUCED-NOT-CLOSED" in gates_text
        and "OPEN CURRENT CHILD" in gates_text,
        [
            result_id in gates_text,
            next_gate in gates_text,
            "REDUCED-NOT-CLOSED" in gates_text,
            "OPEN CURRENT CHILD" in gates_text,
        ],
        [True, True, True, True],
    )
    add(
        rows,
        "roadmap_records_new_frontier",
        result_id in roadmap_text and next_gate in roadmap_text,
        [result_id in roadmap_text, next_gate in roadmap_text],
        [True, True],
    )
    add(
        rows,
        "todo_keeps_t050_in_progress",
        "**T-050**" in todo_text
        and result_id in todo_text
        and next_gate in todo_text
        and any(
            item.get("id") == "T-050" and item.get("status") == "in_progress"
            for item in todo_data.get("tasks", [])
        ),
        [
            "**T-050**" in todo_text,
            result_id in todo_text,
            next_gate in todo_text,
            any(
                item.get("id") == "T-050" and item.get("status") == "in_progress"
                for item in todo_data.get("tasks", [])
            ),
        ],
        [True, True, True, True],
    )
    add(
        rows,
        "changelog_records_package",
        any(
            result_id in record.get("keywords", [])
            and negative_id in record.get("neg_results", [])
            for record in changelog_records
        )
        and "A13 NPC-cone and martingale-injection reduction" in changelog_text,
        [
            any(
                result_id in record.get("keywords", [])
                and negative_id in record.get("neg_results", [])
                for record in changelog_records
            ),
            "A13 NPC-cone and martingale-injection reduction" in changelog_text,
        ],
        [True, True],
    )
    ledger_id = manifest["consequence"]["result_ledger_id"]
    add(
        rows,
        "results_ledger_records_result",
        ledger_id in results_text and result_id in results_text,
        [ledger_id in results_text, result_id in results_text],
        [True, True],
    )
    add(
        rows,
        "negative_registry_records_no_go",
        negative_id in negative_text
        and "retained square" in negative_text.lower()
        and "flat" in negative_text.lower()
        and "production counterexample" in negative_text.lower(),
        [
            negative_id in negative_text,
            "retained square" in negative_text.lower(),
            "flat" in negative_text.lower(),
            "production counterexample" in negative_text.lower(),
        ],
        [True, True, True, True],
    )
    active_frontier = theorem_map["active_frontier"]
    add(
        rows,
        "sector_a_theorem_map_frontier",
        active_frontier.get("current_child") == next_gate
        and next_gate in active_frontier.get("success_condition", ""),
        [
            active_frontier.get("current_child"),
            next_gate in active_frontier.get("success_condition", ""),
        ],
        [next_gate, True],
    )
    add(
        rows,
        "lineage_records_reduction",
        result_id in lineage_text and next_gate in lineage_text,
        [result_id in lineage_text, next_gate in lineage_text],
        [True, True],
    )
    add(
        rows,
        "manifest_preserves_open_boundary",
        all(value is False for value in manifest["claims_not_established"].values()),
        manifest["claims_not_established"],
        "all false",
    )

    modules = imported_modules(independent_script)
    add(
        rows,
        "independent_does_not_import_primary",
        primary_script.stem not in modules,
        modules,
        f"{primary_script.stem} absent",
    )
    forbidden = tuple(manifest["independent_audit"]["forbidden_local_imports"])
    imported_forbidden = [module for module in modules if module in forbidden]
    add(
        rows,
        "independent_reconstructs_local_helpers",
        not imported_forbidden,
        imported_forbidden,
        [],
    )

    environment = manifest["environment_contract"]
    requirements_text = (REPO / environment["requirements_path"]).read_text(
        encoding="utf-8"
    )
    build_text = (REPO / environment["build_tool_path"]).read_text(encoding="utf-8")
    doctor_text = (REPO / environment["doctor_path"]).read_text(encoding="utf-8")
    note_check_text = (REPO / environment["note_pdf_check_path"]).read_text(
        encoding="utf-8"
    )
    add(
        rows,
        "pdf_environment_contract",
        all(package in requirements_text for package in environment["python_packages"])
        and "tectonic" in build_text.lower()
        and "pdf-python-runtime" in doctor_text
        and "tex-engine" in doctor_text
        and "tex_engine" in note_check_text,
        {
            "packages": [
                package in requirements_text for package in environment["python_packages"]
            ],
            "build_tectonic": "tectonic" in build_text.lower(),
            "doctor_pdf": "pdf-python-runtime" in doctor_text,
            "doctor_tex": "tex-engine" in doctor_text,
            "strict_tex": "tex_engine" in note_check_text,
        },
        "all true",
    )

    child_total = int(primary["assertion_count"]) + int(independent["assertion_count"])
    expected_integrated = int(contract["integrated_assertions"])
    add(
        rows,
        "integrated_assertion_contract",
        len(rows) + 2 == expected_integrated,
        len(rows) + 2,
        expected_integrated,
    )
    expected_aggregate = int(contract["aggregate_assertions"])
    add(
        rows,
        "aggregate_assertion_contract",
        child_total + len(rows) + 1 == expected_aggregate,
        child_total + len(rows) + 1,
        expected_aggregate,
    )
    failures = [row for row in rows if row["status"] != "PASS"]
    child_failed = 0 if primary.get("pass") and independent.get("pass") else child_total
    total = child_total + len(rows)
    failed = child_failed + len(failures)
    payload = {
        "schema": contract["integrated_schema"],
        "claim_id": manifest["claim_id"],
        "result_id": result_id,
        "script_version": __version__,
        "generated_at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "primary": primary,
        "independent": independent,
        "integrated_assertions": rows,
        "summary": {"passed": total - failed, "total": total, "failed": failed},
        "verdict": (
            f"{result_id}-INTEGRATED-PASS" if not failures and failed == 0 else "FAIL"
        ),
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures or failed:
        print(f"FAIL: integrated ({failed} total failures)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"ASSERTS: {total}/{total}")
    print(f"{result_id}-INTEGRATED-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
