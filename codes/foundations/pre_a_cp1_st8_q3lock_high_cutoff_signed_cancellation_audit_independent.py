#!/usr/bin/env python3
"""Independent reconstruction of EXP-001199.

The current audit logic is rebuilt on the previous audit's independently
implemented oscillator/term primitives, without importing the EXP-001199
primary module.  This keeps the signed grouping and reverse-order checks on a
separate computational lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_high_cutoff_signed_cancellation_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-signed-cancellation-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"
PHYSICAL_KEYS = ("c", "chi", "r", "g", "lambda", "hbar")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_state_weighted_commutator_sum_audit_independent as base  # noqa: E402


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_fixture() -> tuple[dict[str, Any], list[dict[str, str]]]:
    current_path = MANIFEST
    chain: list[dict[str, str]] = []
    while True:
        current = json.loads(current_path.read_text(encoding="utf-8"))
        source = current.get("source_fixture")
        if not isinstance(source, dict) or "manifest" not in source:
            raise ValueError(f"source fixture chain ended before physical fixture: {current_path}")
        next_path = REPO / str(source["manifest"])
        chain.append({"path": next_path.relative_to(REPO).as_posix(), "sha256": normalized_sha256(next_path)})
        if all(key in source for key in PHYSICAL_KEYS):
            return source, chain
        current_path = next_path


def source_supports(volume: int, source_manifest: dict[str, Any]) -> list[tuple[int, ...]]:
    return [tuple(int(site) for site in support) for support in source_manifest["source_supports_by_volume"][str(volume)]]


def term_groups(order: list[tuple[str, tuple[int, ...]]], volume: int, cutoff: int, fixture: dict[str, Any]) -> tuple[dict[tuple[int, ...], list[np.ndarray]], float]:
    groups: dict[tuple[int, ...], list[np.ndarray]] = {}
    absolute_sum = 0.0
    for left_index, left_spec in enumerate(order):
        left_support = set(left_spec[1])
        for right_spec in order[left_index + 1 :]:
            right_support = set(right_spec[1])
            if left_support.isdisjoint(right_support):
                continue
            union = tuple(sorted(left_support | right_support))
            value = base.commutator(base.local_term(left_spec, list(union), cutoff, fixture), base.local_term(right_spec, list(union), cutoff, fixture))
            groups.setdefault(union, []).append(value)
            absolute_sum += base.operator_norm(value)
    return groups, absolute_sum


def row(volume: int, cutoff: int, beta: float, fixture: dict[str, Any], source_manifest: dict[str, Any], exponent: float, positivity_tolerance: float, norm_floor: float) -> dict[str, Any]:
    declared = base.specs(volume)
    forward_groups, absolute_raw_sum = term_groups(declared, volume, cutoff, fixture)
    reverse_groups, reverse_absolute_raw_sum = term_groups(list(reversed(declared)), volume, cutoff, fixture)
    sources = source_supports(volume, source_manifest)
    source_keys = ["-".join(map(str, support)) for support in sources]
    source_aggregates = {key: {"group_count": 0, "signed_raw_sum": 0.0, "signed_gibbs_sum": 0.0, "signed_weighted_sum": 0.0, "absolute_raw_sum": 0.0, "absolute_gibbs_sum": 0.0, "absolute_weighted_sum": 0.0, "max_signed_raw": 0.0, "max_signed_gibbs": 0.0, "max_signed_weighted": 0.0} for key in source_keys}
    all_metrics = {"signed_raw_sum": 0.0, "signed_gibbs_sum": 0.0, "signed_weighted_sum": 0.0, "absolute_raw_sum": absolute_raw_sum, "absolute_gibbs_sum": 0.0, "absolute_weighted_sum": 0.0, "max_signed_raw": 0.0, "max_signed_gibbs": 0.0, "max_signed_weighted": 0.0}
    group_rows: list[dict[str, Any]] = []
    orientation_raw_residual = orientation_gibbs_difference = orientation_weighted_difference = 0.0
    cache: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray, np.ndarray, float]] = {}
    for union in sorted(forward_groups):
        forward = sum(forward_groups[union], np.zeros_like(forward_groups[union][0]))
        reverse = sum(reverse_groups[union], np.zeros_like(reverse_groups[union][0]))
        local_h = base.induced_hamiltonian(list(union), volume, cutoff, fixture)
        rho = base.gibbs(local_h, beta)
        rho_sqrt = base.spectral_power(rho, 0.5)
        k_positive = base.positive_weight(local_h)
        k_power = base.spectral_power(k_positive, exponent)
        minimum = float(np.min(np.linalg.eigvalsh(k_positive)))
        cache[union] = (rho, rho_sqrt, k_power, minimum)
        if minimum < 1.0 - positivity_tolerance:
            raise AssertionError(f"positive shift failed for union {union}: {minimum}")
        signed_raw = base.operator_norm(forward)
        signed_gibbs = base.two_sided_gibbs(forward, rho)
        signed_weighted = base.weighted_two_sided(forward, k_power, rho_sqrt)
        reverse_raw = base.operator_norm(reverse)
        reverse_gibbs = base.two_sided_gibbs(reverse, rho)
        reverse_weighted = base.weighted_two_sided(reverse, k_power, rho_sqrt)
        absolute_gibbs = sum(base.two_sided_gibbs(value, rho) for value in forward_groups[union])
        absolute_weighted = sum(base.weighted_two_sided(value, k_power, rho_sqrt) for value in forward_groups[union])
        absolute_raw = sum(base.operator_norm(value) for value in forward_groups[union])
        if not all(np.isfinite(value) and value >= -norm_floor for value in (signed_raw, signed_gibbs, signed_weighted, reverse_raw, reverse_gibbs, reverse_weighted, absolute_raw, absolute_gibbs, absolute_weighted)):
            raise AssertionError(f"non-finite group at V={volume}, n={cutoff}, beta={beta}, union={union}")
        raw_residual = base.operator_norm(forward + reverse)
        orientation_raw_residual = max(orientation_raw_residual, raw_residual)
        orientation_gibbs_difference = max(orientation_gibbs_difference, abs(signed_gibbs - reverse_gibbs))
        orientation_weighted_difference = max(orientation_weighted_difference, abs(signed_weighted - reverse_weighted))
        all_metrics["signed_raw_sum"] += signed_raw
        all_metrics["signed_gibbs_sum"] += signed_gibbs
        all_metrics["signed_weighted_sum"] += signed_weighted
        all_metrics["absolute_gibbs_sum"] += absolute_gibbs
        all_metrics["absolute_weighted_sum"] += absolute_weighted
        all_metrics["max_signed_raw"] = max(all_metrics["max_signed_raw"], signed_raw)
        all_metrics["max_signed_gibbs"] = max(all_metrics["max_signed_gibbs"], signed_gibbs)
        all_metrics["max_signed_weighted"] = max(all_metrics["max_signed_weighted"], signed_weighted)
        group_rows.append({"union": list(union), "pair_count": len(forward_groups[union]), "signed_raw": signed_raw, "signed_gibbs": signed_gibbs, "signed_weighted": signed_weighted, "absolute_raw": absolute_raw, "absolute_gibbs": absolute_gibbs, "absolute_weighted": absolute_weighted, "reverse_raw": reverse_raw, "reverse_gibbs": reverse_gibbs, "reverse_weighted": reverse_weighted, "orientation_raw_residual": raw_residual, "orientation_gibbs_difference": abs(signed_gibbs - reverse_gibbs), "orientation_weighted_difference": abs(signed_weighted - reverse_weighted)})
        for key, aggregate in source_aggregates.items():
            support = set(int(site) for site in key.split("-"))
            if set(union).isdisjoint(support):
                continue
            aggregate["group_count"] += 1
            aggregate["signed_raw_sum"] += signed_raw
            aggregate["signed_gibbs_sum"] += signed_gibbs
            aggregate["signed_weighted_sum"] += signed_weighted
            aggregate["absolute_raw_sum"] += absolute_raw
            aggregate["absolute_gibbs_sum"] += absolute_gibbs
            aggregate["absolute_weighted_sum"] += absolute_weighted
            aggregate["max_signed_raw"] = max(aggregate["max_signed_raw"], signed_raw)
            aggregate["max_signed_gibbs"] = max(aggregate["max_signed_gibbs"], signed_gibbs)
            aggregate["max_signed_weighted"] = max(aggregate["max_signed_weighted"], signed_weighted)
    for aggregate in source_aggregates.values():
        source_size = len(sources[0])
        aggregate["signed_weighted_sum_per_source_site"] = aggregate["signed_weighted_sum"] / source_size
        aggregate["signed_gibbs_sum_per_source_site"] = aggregate["signed_gibbs_sum"] / source_size
        aggregate["signed_raw_sum_per_source_site"] = aggregate["signed_raw_sum"] / source_size
    all_metrics["signed_raw_sum_per_site"] = all_metrics["signed_raw_sum"] / volume
    all_metrics["signed_gibbs_sum_per_site"] = all_metrics["signed_gibbs_sum"] / volume
    all_metrics["signed_weighted_sum_per_site"] = all_metrics["signed_weighted_sum"] / volume
    all_metrics["absolute_raw_sum_per_site"] = all_metrics["absolute_raw_sum"] / volume
    all_metrics["absolute_gibbs_sum_per_site"] = all_metrics["absolute_gibbs_sum"] / volume
    all_metrics["absolute_weighted_sum_per_site"] = all_metrics["absolute_weighted_sum"] / volume
    return {"volume": volume, "cutoff": cutoff, "beta": beta, "group_count": len(forward_groups), "pair_count": sum(len(values) for values in forward_groups.values()), "context_count": len(cache), "all_group": all_metrics, "groups": group_rows, "source_touching": source_aggregates, "orientation_raw_residual": orientation_raw_residual, "orientation_gibbs_difference": orientation_gibbs_difference, "orientation_weighted_difference": orientation_weighted_difference, "absolute_raw_sum_forward": absolute_raw_sum, "absolute_raw_sum_reverse": reverse_absolute_raw_sum, "weight_exponent": exponent}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, chain = load_fixture()
    source_manifest, audit, scope = manifest["source_fixture"], manifest["audit_fixture"], manifest["scope"]
    volumes = [int(value) for value in source_manifest["volume_values"]]
    cutoffs = [int(value) for value in source_manifest["cutoff_values"]]
    betas = [float(value) for value in source_manifest["beta_values"]]
    exponent = float(Fraction(str(audit["weight_exponent"])))
    tolerance, positivity_tolerance, orientation_tolerance, floor = float(audit["localization_tolerance"]), float(audit["positivity_tolerance"]), float(audit["orientation_tolerance"]), float(audit["commutator_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001199" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001199/T-054/false", "provenance")
    check("source chain", len(chain) >= 4 and all(Path(item["path"]).is_file() for item in chain), chain, "physical fixture chain present", "provenance")
    check("physical fixture", all(key in fixture for key in PHYSICAL_KEYS), sorted(fixture), PHYSICAL_KEYS, "fixture")
    check("graph volumes", volumes == [2] and all(base.graph_edges(volume) for volume in volumes), volumes, "registered fixed Q3 graph volume", "fixture")
    check("cutoff grid", cutoffs == [3, 4, 5, 6, 8, 10, 12, 16, 20, 24], cutoffs, "declared cutoff grid", "fixture")
    check("beta grid", betas == [0.5, 1.0, 2.0], betas, "declared beta grid", "fixture")
    check("source support coverage", all(source_manifest["source_supports_by_volume"].get(str(volume)) for volume in volumes), source_manifest["source_supports_by_volume"], "nonempty source supports", "fixture")
    check("scope firewall", scope["finite_signed_union_rows_closed"] and scope["finite_reverse_order_antisymmetry_closed"] and scope["finite_source_beta_volume_cutoff_grid_closed"] and scope["cancellation_diagnostic_closed"] and not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["pre_a_closed"], scope, "finite high-cutoff signed proxy only", "scope")
    rows: list[dict[str, Any]] = []
    for volume in volumes:
        reference = base.reference_localization(volume, cutoffs[0], fixture, tolerance)
        check(f"V={volume} reference localization", reference <= tolerance, reference, f"<={tolerance}", "locality")
        for beta in betas:
            for cutoff in cutoffs:
                value = row(volume, cutoff, beta, fixture, source_manifest, exponent, positivity_tolerance, floor)
                check(f"V={volume} n={cutoff} beta={beta} finite", all(np.isfinite(float(value["all_group"][key])) for key in ("signed_raw_sum", "signed_gibbs_sum", "signed_weighted_sum", "absolute_raw_sum", "absolute_gibbs_sum", "absolute_weighted_sum", "signed_weighted_sum_per_site")), value, "finite", "numeric")
                check(f"V={volume} n={cutoff} beta={beta} coverage", value["pair_count"] > 0 and value["group_count"] > 0 and value["context_count"] > 0, [value["pair_count"], value["group_count"], value["context_count"]], ">0", "coverage")
                check(f"V={volume} n={cutoff} beta={beta} reverse antisymmetry", value["orientation_raw_residual"] <= orientation_tolerance and value["orientation_gibbs_difference"] <= orientation_tolerance and value["orientation_weighted_difference"] <= orientation_tolerance, [value["orientation_raw_residual"], value["orientation_gibbs_difference"], value["orientation_weighted_difference"]], f"<={orientation_tolerance}", "orientation")
                check(f"V={volume} n={cutoff} beta={beta} source keys", set(value["source_touching"]) == {"-".join(map(str, support)) for support in source_supports(volume, source_manifest)}, value["source_touching"], "declared source keys", "source")
                rows.append({"reference_localization_residual": reference, **value})
    summary: list[dict[str, Any]] = []
    for volume in volumes:
        for beta in betas:
            selected = [value for value in rows if int(value["volume"]) == volume and float(value["beta"]) == beta]
            signed = [float(value["all_group"]["signed_weighted_sum_per_site"]) for value in selected]
            absolute = [float(value["all_group"]["absolute_weighted_sum_per_site"]) for value in selected]
            ratio = signed[-1] / max(signed[0], np.finfo(float).tiny)
            reduction = signed[-1] / max(absolute[-1], np.finfo(float).tiny)
            summary.append({"volume": volume, "beta": beta, "cutoff_first": cutoffs[0], "cutoff_last": cutoffs[-1], "signed_weighted_per_site_max": max(signed), "absolute_weighted_per_site_max": max(absolute), "signed_cutoff_growth_ratio": ratio, "signed_to_absolute_endpoint_ratio": reduction, "signed_cutoff_nondecreasing": all(signed[index] + tolerance >= signed[index - 1] for index in range(1, len(signed))), "growth_threshold": float(audit["growth_ratio_threshold"]), "growth_threshold_crossed": ratio >= float(audit["growth_ratio_threshold"])})
            check(f"V={volume} beta={beta} summary", len(selected) == len(cutoffs) and np.isfinite(ratio) and np.isfinite(reduction), [len(selected), ratio, reduction], [len(cutoffs), "finite", "finite"], "scaling")
    diagnostic = {"interpretation": "finite high-cutoff signed-union cancellation diagnostic; not a global-state or asymptotic bound", "maximum_signed_weighted_sum_per_site": max(float(value["all_group"]["signed_weighted_sum_per_site"]) for value in rows), "maximum_absolute_weighted_sum_per_site": max(float(value["all_group"]["absolute_weighted_sum_per_site"]) for value in rows), "any_cutoff_growth_threshold_crossed": any(item["growth_threshold_crossed"] for item in summary), "candidate_cutoff_volume_beta_uniform_bound": "not established by this audit", "global_gibbs_state_transfer": "open", "common_core_operator_embedding": "open", "actual_q3_trotter_defect": "open"}
    check("finite-only diagnostic", diagnostic["candidate_cutoff_volume_beta_uniform_bound"] == "not established by this audit" and diagnostic["global_gibbs_state_transfer"] == "open" and diagnostic["common_core_operator_embedding"] == "open" and diagnostic["actual_q3_trotter_defect"] == "open", diagnostic, "finite-only semantics", "scope")
    check("QFT firewall", not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["common_core_operator_embedding_closed"] and not scope["actual_q3_trotter_defect_closed"] and not scope["actual_q3_thermodynamic_history_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "signed/domain/QFT gates remain open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-HIGH-CUTOFF-SIGNED-CANCELLATION-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"source_chain": chain, "row_count": len(rows), "rows": rows, "summary": summary, "weight_exponent": exponent, "finite_signed_union_rows_closed": True, "finite_reverse_order_antisymmetry_closed": True, "finite_source_beta_volume_cutoff_grid_closed": True, "cancellation_diagnostic_closed": True, "candidate_cutoff_volume_beta_uniform_bound_closed": False, "global_gibbs_state_transfer_closed": False, "common_core_operator_embedding_closed": False, "diagnostic": diagnostic}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT HIGH-CUTOFF-SIGNED-CANCELLATION PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
