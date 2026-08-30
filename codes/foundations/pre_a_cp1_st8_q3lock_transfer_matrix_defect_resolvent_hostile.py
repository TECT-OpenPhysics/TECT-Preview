#!/usr/bin/env python3
"""Hostile mutation lane for the R-455 transfer-matrix contract."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-transfer-matrix-defect-resolvent-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent/hostile.json"


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def valid(packet: dict[str, Any]) -> bool:
    if [packet.get("result_id"), packet.get("exploration_id"), packet.get("task_id"), packet.get("claim_bearing"), packet.get("tier")] != ["R-455", "EXP-001328", "T-054", False, "T0"]:
        return False
    contract = packet.get("matrix_contract", {})
    if contract.get("entries_nonnegative") is not True or contract.get("componentwise_recurrence") is not True or contract.get("induced_norm") != "infinity-row-sum" or contract.get("common_row_sum_bound") is not True or contract.get("source_and_defect_vectors_nonnegative") is not True or contract.get("path_order") != "K_R through K_(j+1) acts on a term born at j":
        return False
    theorem = packet.get("theorem", {})
    required = ("componentwise", "nonnegative", "row sum", "kappa_bar", "K_R...K_(j+1)", "resonance", "kappa_bar<1", "s<1")
    if not all(token.lower() in " ".join(str(value) for value in theorem.values()).lower() for token in required):
        return False
    scope = packet.get("scope", {})
    closed = ("nonnegative_transfer_matrix_contract_closed", "induced_infinity_norm_step_closed", "variable_matrix_path_product_bound_closed", "general_vector_defect_convolution_closed", "geometric_vector_defect_envelope_closed", "nonresonant_closed_form_closed", "resonant_closed_form_closed", "two_base_less_than_one_threshold_closed")
    if not all(scope.get(key) is True for key in closed):
        return False
    open_keys = [key for key, value in scope.items() if key.endswith("_closed") and key not in closed]
    if not all(scope.get(key) is False for key in open_keys):
        return False
    if scope.get("no_new_negative_result") is not True or scope.get("no_tier_change") is not True or scope.get("no_pdf") is not True:
        return False
    fixture = packet.get("finite_fixture", {})
    expected_patterns = ["zero", "diagonal", "permutation", "averaging", "triangular", "alternating", "ramp-four"]
    if fixture.get("no_new_finite_grid") is not True or fixture.get("matrix_patterns") != expected_patterns:
        return False
    preservation = packet.get("method_preservation", {})
    return all(preservation.get(key) is True for key in ("existing_forward_method_unchanged", "observation_first_inverse_lane_additive", "owner_order_unchanged", "no_physical_promotion"))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Any]] = []

    def mutate(name: str, change: Any) -> None:
        packet = copy.deepcopy(baseline)
        change(packet)
        mutations.append((name, packet))

    mutate("negative-entry-admitted", lambda p: p["matrix_contract"].__setitem__("entries_nonnegative", False))
    mutate("componentwise-dropped", lambda p: p["matrix_contract"].__setitem__("componentwise_recurrence", False))
    mutate("wrong-norm", lambda p: p["matrix_contract"].__setitem__("induced_norm", "one-column"))
    mutate("common-bound-dropped", lambda p: p["matrix_contract"].__setitem__("common_row_sum_bound", False))
    mutate("source-vector-sign-dropped", lambda p: p["matrix_contract"].__setitem__("source_and_defect_vectors_nonnegative", False))
    mutate("path-order-reversed", lambda p: p["matrix_contract"].__setitem__("path_order", "K_(j+1) through K_R acts in reverse order"))
    mutate("upper-bound-vacated", lambda p: p["theorem"].__setitem__("matrix_recurrence", "The row bound is omitted."))
    mutate("path-product-vacated", lambda p: p["theorem"].__setitem__("path_product_bound", "Products are left unbounded."))
    mutate("resonance-dropped", lambda p: p["theorem"].__setitem__("closed_form", "Only the unequal-base quotient is used."))
    mutate("unit-threshold-admitted", lambda p: p["theorem"].__setitem__("threshold", "Allow kappa_bar<=1 and s<=1."))
    mutate("finite-grid-substitution", lambda p: p["finite_fixture"].__setitem__("no_new_finite_grid", False))
    mutate("actual-history-claimed", lambda p: p["scope"].__setitem__("actual_q3_history_closed", True))
    mutate("source-transfer-claimed", lambda p: p["scope"].__setitem__("source_owned_transfer_closed", True))
    mutate("physical-promotion", lambda p: p["scope"].__setitem__("physical_sector_closed", True))
    mutate("tier-promotion", lambda p: p.__setitem__("tier", "T6"))
    mutate("claim-bearing", lambda p: p.__setitem__("claim_bearing", True))
    mutate("method-overhaul", lambda p: p["method_preservation"].__setitem__("existing_forward_method_unchanged", False))
    mutate("owner-order-change", lambda p: p["method_preservation"].__setitem__("owner_order_unchanged", False))
    mutate("negative-result-hidden", lambda p: p["scope"].__setitem__("no_new_negative_result", False))
    mutate("pdf-policy-changed", lambda p: p["scope"].__setitem__("no_pdf", False))

    rejected = []
    for name, packet in mutations:
        if valid(packet):
            raise AssertionError(f"hostile mutation accepted: {name}")
        rejected.append(name)
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": baseline["candidate_id"],
        "result_id": baseline["result_id"],
        "claim_id": baseline["claim_ids"][0],
        "task_id": baseline["task_id"],
        "exploration_id": baseline["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "mutation_count": len(mutations),
        "mutations_rejected": rejected,
        "assertion_count": len(mutations),
        "non_claims": baseline["non_claims"],
        "boundary": baseline["boundary"],
    }
    save(output, payload)
    print(f"R-455 HOSTILE {payload['verdict']} {len(rejected)}/{len(mutations)}", flush=True)
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)
