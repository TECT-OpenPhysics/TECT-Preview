#!/usr/bin/env python3
"""Hostile mutation lane for the R-456 weighted transfer contract."""

from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-weighted-transfer-operator-defect-resolvent-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-hostile-pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent/hostile.json"


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def valid(packet: dict[str, Any]) -> bool:
    identity = [packet.get("result_id"), packet.get("exploration_id"), packet.get("task_id"), packet.get("claim_bearing"), packet.get("tier"), packet.get("status")]
    if identity != ["R-456", "EXP-001329", "T-054", False, "T0", "CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED"]:
        return False
    contract = packet.get("weighted_contract", {})
    required_contract = {
        "weights_strictly_positive": True,
        "entries_nonnegative": True,
        "componentwise_recurrence": True,
        "weighted_row_sum_bound": True,
        "common_kappa_bar": True,
        "path_order": "K_R through K_(j+1) acts on a term born at j",
        "source_and_defect_vectors_nonnegative": True,
        "finite_dimension_only": True,
    }
    if any(contract.get(key) != value for key, value in required_contract.items()):
        return False
    theorem = packet.get("theorem", {})
    theorem_text = " ".join(str(value) for value in theorem.values()).lower()
    if not all(token in theorem_text for token in ("nonnegative", "row", "sum_j", "||k_r x||_w", "kappa_bar", "path", "s_r", "vanishes", "d_w^(-1)", "coordinate")):
        return False
    scope = packet.get("scope", {})
    closed = (
        "positive_weight_contract_closed",
        "weighted_row_sum_step_closed",
        "diagonal_conjugation_closed",
        "weighted_path_product_bound_closed",
        "weighted_vector_defect_convolution_closed",
        "weighted_geometric_defect_envelope_closed",
        "nonresonant_closed_form_closed",
        "resonant_closed_form_closed",
        "two_base_less_than_one_threshold_closed",
    )
    if not all(scope.get(key) is True for key in closed):
        return False
    open_keys = [key for key, value in scope.items() if key.endswith("_closed") and key not in closed]
    if not all(scope.get(key) is False for key in open_keys):
        return False
    if any(scope.get(key) is not True for key in ("no_new_negative_result", "no_tier_change", "no_pdf")):
        return False
    fixture = packet.get("finite_fixture", {})
    if fixture.get("no_new_finite_grid") is not True:
        return False
    if fixture.get("weight_patterns") != ["unit", "dyadic", "affine", "geometric", "alternating"]:
        return False
    preservation = packet.get("method_preservation", {})
    return all(preservation.get(key) is True for key in ("existing_forward_method_unchanged", "observation_first_inverse_lane_additive", "owner_order_unchanged", "no_physical_promotion"))


def run(output: Path = DEFAULT) -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Any]] = []

    def mutate(name: str, change: Any) -> None:
        packet = copy.deepcopy(baseline)
        change(packet)
        mutations.append((name, packet))

    mutate("nonpositive-weights-admitted", lambda p: p["weighted_contract"].__setitem__("weights_strictly_positive", False))
    mutate("negative-entry-admitted", lambda p: p["weighted_contract"].__setitem__("entries_nonnegative", False))
    mutate("componentwise-dropped", lambda p: p["weighted_contract"].__setitem__("componentwise_recurrence", False))
    mutate("weighted-bound-dropped", lambda p: p["weighted_contract"].__setitem__("weighted_row_sum_bound", False))
    mutate("common-bound-dropped", lambda p: p["weighted_contract"].__setitem__("common_kappa_bar", False))
    mutate("source-vector-sign-dropped", lambda p: p["weighted_contract"].__setitem__("source_and_defect_vectors_nonnegative", False))
    mutate("finite-dimension-firewall-dropped", lambda p: p["weighted_contract"].__setitem__("finite_dimension_only", False))
    mutate("path-order-reversed", lambda p: p["weighted_contract"].__setitem__("path_order", "K_(j+1) through K_R acts in reverse order"))
    mutate("diagonal-direction-reversed", lambda p: p["theorem"].__setitem__("diagonal_conjugation", "Use D_w K D_w^(-1) without checking the norm."))
    mutate("weighted-row-theorem-vacated", lambda p: p["theorem"].__setitem__("weighted_matrix_contract", "The weighted row bound is omitted."))
    mutate("path-product-vacated", lambda p: p["theorem"].__setitem__("weighted_recurrence", "Products are left unbounded."))
    mutate("threshold-weakened", lambda p: p["theorem"].__setitem__("threshold", "Allow kappa_bar<=1 and s<=1."))
    mutate("finite-grid-substitution", lambda p: p["finite_fixture"].__setitem__("no_new_finite_grid", False))
    mutate("actual-history-claimed", lambda p: p["scope"].__setitem__("actual_q3_history_closed", True))
    mutate("source-transfer-claimed", lambda p: p["scope"].__setitem__("source_owned_transfer_closed", True))
    mutate("weighted-domain-claimed", lambda p: p["scope"].__setitem__("common_weighted_operator_domain_closed", True))
    mutate("physical-promotion", lambda p: p["scope"].__setitem__("physical_sector_closed", True))
    mutate("tier-promotion", lambda p: p.__setitem__("tier", "T6"))
    mutate("claim-bearing", lambda p: p.__setitem__("claim_bearing", True))
    mutate("method-overhaul", lambda p: p["method_preservation"].__setitem__("existing_forward_method_unchanged", False))
    mutate("owner-order-change", lambda p: p["method_preservation"].__setitem__("owner_order_unchanged", False))
    mutate("negative-result-hidden", lambda p: p["scope"].__setitem__("no_new_negative_result", False))

    rejected: list[str] = []
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
    print(f"R-456 HOSTILE {payload['verdict']} {len(rejected)}/{len(mutations)}", flush=True)
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--self-test", action="store_true")
    run(parser.parse_args().output)
