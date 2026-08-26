#!/usr/bin/env python3
"""Independent reconstruction of EXP-001200.

The current audit logic is rebuilt on the previous audit's independently
implemented oscillator/term primitives, without importing the EXP-001200
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
SLUG = "pre_a_cp1_st8_q3lock_low_energy_spectral_window_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-low-energy-spectral-window-audit-manifest.json"
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



def window_metric(matrix: np.ndarray, weight_power: np.ndarray, rho_sqrt: np.ndarray, projector: np.ndarray, rho: np.ndarray, energy_values: np.ndarray, threshold: float, volume: int, tolerance: float) -> dict[str, Any]:
    selected = energy_values <= threshold + tolerance
    rank = int(np.count_nonzero(selected))
    projected = projector @ rho_sqrt @ projector
    mass = float(np.real(np.trace(projector @ rho)))
    signed = base.weighted_two_sided(matrix, weight_power, projected)
    conditional = signed / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
    if rank <= 0 or not np.isfinite(mass) or mass <= -tolerance or mass > 1.0 + tolerance:
        raise AssertionError(f"invalid spectral window threshold={threshold}: rank={rank}, mass={mass}")
    if not all(np.isfinite(float(value)) and float(value) >= -tolerance for value in (signed, conditional)):
        raise AssertionError(f"non-finite projected weighted norm threshold={threshold}")
    return {"energy_threshold": threshold, "rank": rank, "window_mass": mass, "tail_mass": max(0.0, 1.0 - mass), "signed_weighted": signed, "signed_weighted_per_site": signed / volume, "conditional_signed_weighted": conditional, "conditional_signed_weighted_per_site": conditional / volume}


def row(volume: int, cutoff: int, beta: float, fixture: dict[str, Any], source_manifest: dict[str, Any], exponent: float, energy_windows: list[float], tolerance: float, positivity_tolerance: float, orientation_tolerance: float, norm_floor: float) -> dict[str, Any]:
    declared = base.specs(volume)
    reversed_order = list(reversed(declared))
    forward_groups, absolute_raw_sum = term_groups(declared, volume, cutoff, fixture)
    reverse_groups, reverse_absolute_raw_sum = term_groups(reversed_order, volume, cutoff, fixture)
    if set(forward_groups) != set(reverse_groups):
        raise AssertionError("forward and reverse union-group keys differ")
    sources = source_supports(volume, source_manifest)
    source_keys = ["-".join(map(str, support)) for support in sources]
    source_aggregates = {key: {"group_count": 0, "signed_weighted_sum": 0.0, "absolute_weighted_sum": 0.0, "window_signed_weighted": {}, "window_absolute_weighted": {}} for key in source_keys}
    all_metrics = {"signed_raw_sum": 0.0, "signed_gibbs_sum": 0.0, "signed_weighted_sum": 0.0, "absolute_raw_sum": absolute_raw_sum, "absolute_gibbs_sum": 0.0, "absolute_weighted_sum": 0.0, "max_signed_weighted": 0.0}
    group_rows: list[dict[str, Any]] = []
    orientation_raw_residual = orientation_gibbs_difference = orientation_weighted_difference = 0.0
    window_rows: dict[str, dict[str, Any]] = {}
    context_cache: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    for union in sorted(forward_groups):
        forward = sum(forward_groups[union], np.zeros_like(forward_groups[union][0]))
        reverse = sum(reverse_groups[union], np.zeros_like(reverse_groups[union][0]))
        local_h = base.induced_hamiltonian(list(union), volume, cutoff, fixture)
        energy_values, energy_vectors = np.linalg.eigh(base.hermitian(local_h))
        shifted = energy_values - float(np.min(energy_values))
        rho = base.gibbs(local_h, beta)
        rho_sqrt = base.spectral_power(rho, 0.5)
        k_power = base.spectral_power(base.positive_weight(local_h), exponent)
        context_cache[union] = (energy_values, shifted, energy_vectors, rho, rho_sqrt)
        if float(np.min(np.linalg.eigvalsh(base.positive_weight(local_h)))) < 1.0 - positivity_tolerance:
            raise AssertionError(f"positive shift failed for union {union}")
        signed_raw = base.operator_norm(forward)
        signed_gibbs = base.two_sided_gibbs(forward, rho)
        signed_weighted = base.weighted_two_sided(forward, k_power, rho_sqrt)
        reverse_raw = base.operator_norm(reverse)
        reverse_gibbs = base.two_sided_gibbs(reverse, rho)
        reverse_weighted = base.weighted_two_sided(reverse, k_power, rho_sqrt)
        absolute_raw = sum(base.operator_norm(value) for value in forward_groups[union])
        absolute_gibbs = sum(base.two_sided_gibbs(value, rho) for value in forward_groups[union])
        absolute_weighted = sum(base.weighted_two_sided(value, k_power, rho_sqrt) for value in forward_groups[union])
        finite_values = (signed_raw, signed_gibbs, signed_weighted, reverse_raw, reverse_gibbs, reverse_weighted, absolute_raw, absolute_gibbs, absolute_weighted)
        if not all(np.isfinite(value) and value >= -norm_floor for value in finite_values):
            raise AssertionError(f"non-finite group at V={volume}, n={cutoff}, beta={beta}, union={union}")
        orientation_raw_residual = max(orientation_raw_residual, base.operator_norm(forward + reverse))
        orientation_gibbs_difference = max(orientation_gibbs_difference, abs(signed_gibbs - reverse_gibbs))
        orientation_weighted_difference = max(orientation_weighted_difference, abs(signed_weighted - reverse_weighted))
        all_metrics["signed_raw_sum"] += signed_raw; all_metrics["signed_gibbs_sum"] += signed_gibbs; all_metrics["signed_weighted_sum"] += signed_weighted
        all_metrics["absolute_gibbs_sum"] += absolute_gibbs; all_metrics["absolute_weighted_sum"] += absolute_weighted; all_metrics["max_signed_weighted"] = max(all_metrics["max_signed_weighted"], signed_weighted)
        group_windows: dict[str, dict[str, Any]] = {}
        for threshold in energy_windows:
            key = format(threshold, "g")
            selector = shifted <= threshold + tolerance
            projector = energy_vectors[:, selector] @ energy_vectors[:, selector].conj().T
            signed_window = window_metric(forward, k_power, rho_sqrt, projector, rho, shifted, threshold, volume, tolerance)
            absolute_window = sum(window_metric(value, k_power, rho_sqrt, projector, rho, shifted, threshold, volume, tolerance)["signed_weighted"] for value in forward_groups[union])
            signed_window["absolute_weighted"] = absolute_window; signed_window["absolute_weighted_per_site"] = absolute_window / volume; signed_window["signed_to_absolute"] = signed_window["signed_weighted"] / max(absolute_window, np.finfo(float).tiny)
            group_windows[key] = signed_window
            if key not in window_rows:
                window_rows[key] = {"energy_threshold": threshold, "rank": signed_window["rank"], "window_mass": signed_window["window_mass"], "tail_mass": signed_window["tail_mass"], "signed_weighted": 0.0, "absolute_weighted": 0.0, "conditional_signed_weighted": 0.0, "signed_weighted_per_site": 0.0, "absolute_weighted_per_site": 0.0, "conditional_signed_weighted_per_site": 0.0, "group_count": 0}
            window_rows[key]["signed_weighted"] += signed_window["signed_weighted"]; window_rows[key]["absolute_weighted"] += absolute_window; window_rows[key]["conditional_signed_weighted"] += signed_window["conditional_signed_weighted"]; window_rows[key]["group_count"] += 1
        group_rows.append({"union": list(union), "pair_count": len(forward_groups[union]), "signed_raw": signed_raw, "signed_gibbs": signed_gibbs, "signed_weighted": signed_weighted, "absolute_raw": absolute_raw, "absolute_gibbs": absolute_gibbs, "absolute_weighted": absolute_weighted, "reverse_raw": reverse_raw, "reverse_gibbs": reverse_gibbs, "reverse_weighted": reverse_weighted, "orientation_raw_residual": base.operator_norm(forward + reverse), "orientation_gibbs_difference": abs(signed_gibbs - reverse_gibbs), "orientation_weighted_difference": abs(signed_weighted - reverse_weighted), "windows": group_windows})
        for key, aggregate in source_aggregates.items():
            support = set(int(site) for site in key.split("-"))
            if set(union).isdisjoint(support): continue
            aggregate["group_count"] += 1; aggregate["signed_weighted_sum"] += signed_weighted; aggregate["absolute_weighted_sum"] += absolute_weighted
            for threshold in energy_windows:
                window_key = format(threshold, "g"); aggregate["window_signed_weighted"].setdefault(window_key, 0.0); aggregate["window_absolute_weighted"].setdefault(window_key, 0.0)
                aggregate["window_signed_weighted"][window_key] += group_windows[window_key]["signed_weighted"]; aggregate["window_absolute_weighted"][window_key] += group_windows[window_key]["absolute_weighted"]
    all_metrics["signed_raw_sum_per_site"] = all_metrics["signed_raw_sum"] / volume; all_metrics["signed_gibbs_sum_per_site"] = all_metrics["signed_gibbs_sum"] / volume; all_metrics["signed_weighted_sum_per_site"] = all_metrics["signed_weighted_sum"] / volume; all_metrics["absolute_raw_sum_per_site"] = all_metrics["absolute_raw_sum"] / volume; all_metrics["absolute_gibbs_sum_per_site"] = all_metrics["absolute_gibbs_sum"] / volume; all_metrics["absolute_weighted_sum_per_site"] = all_metrics["absolute_weighted_sum"] / volume
    for key, metric in window_rows.items(): metric["signed_weighted_per_site"] = metric["signed_weighted"] / volume; metric["absolute_weighted_per_site"] = metric["absolute_weighted"] / volume; metric["conditional_signed_weighted_per_site"] = metric["signed_weighted_per_site"] / max(np.sqrt(metric["window_mass"]), np.finfo(float).tiny); metric["signed_to_absolute"] = metric["signed_weighted"] / max(metric["absolute_weighted"], np.finfo(float).tiny)
    for aggregate in source_aggregates.values():
        source_size = len(sources[0]); aggregate["signed_weighted_sum_per_source_site"] = aggregate["signed_weighted_sum"] / source_size; aggregate["absolute_weighted_sum_per_source_site"] = aggregate["absolute_weighted_sum"] / source_size
    return {"volume": volume, "cutoff": cutoff, "beta": beta, "group_count": len(forward_groups), "pair_count": sum(len(values) for values in forward_groups.values()), "context_count": len(context_cache), "all_group": all_metrics, "groups": group_rows, "windows": window_rows, "source_touching": source_aggregates, "orientation_raw_residual": orientation_raw_residual, "orientation_gibbs_difference": orientation_gibbs_difference, "orientation_weighted_difference": orientation_weighted_difference, "absolute_raw_sum_forward": absolute_raw_sum, "absolute_raw_sum_reverse": reverse_absolute_raw_sum, "weight_exponent": exponent}


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, chain = load_fixture(); source_manifest, audit, scope = manifest["source_fixture"], manifest["audit_fixture"], manifest["scope"]
    volumes = [int(value) for value in source_manifest["volume_values"]]; cutoffs = [int(value) for value in source_manifest["cutoff_values"]]; betas = [float(value) for value in source_manifest["beta_values"]]; energy_windows = [float(value) for value in audit["energy_windows"]]; tail_cutoff_start = int(audit["tail_cutoff_start"]); exponent = float(Fraction(str(audit["weight_exponent"])))
    tolerance = float(audit["localization_tolerance"]); positivity_tolerance = float(audit["positivity_tolerance"]); orientation_tolerance = float(audit["orientation_tolerance"]); norm_floor = float(audit["commutator_floor"]); checks: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001200" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001200/T-054/false", "provenance")
    check("source chain", len(chain) >= 4 and all(Path(item["path"]).is_file() for item in chain), chain, "physical fixture chain present", "provenance")
    check("physical fixture", all(key in fixture for key in PHYSICAL_KEYS), sorted(fixture), PHYSICAL_KEYS, "fixture")
    check("graph volume", volumes == [2] and all(base.graph_edges(volume) for volume in volumes), volumes, "fixed two-site Q3 graph", "fixture")
    check("cutoff grid", cutoffs == [3, 4, 5, 6, 8, 10, 12, 16, 20, 24], cutoffs, "declared high-cutoff grid", "fixture")
    check("beta grid", betas == [0.5, 1.0, 2.0], betas, "declared beta grid", "fixture")
    check("energy-window grid", energy_windows == [0.5, 1.0, 2.0, 4.0], energy_windows, "declared fixed-energy windows", "fixture")
    check("tail cutoff", tail_cutoff_start == 12 and tail_cutoff_start in cutoffs, tail_cutoff_start, "registered tail cutoff", "fixture")
    check("source support coverage", all(source_manifest["source_supports_by_volume"].get(str(volume)) for volume in volumes), source_manifest["source_supports_by_volume"], "nonempty source supports", "fixture")
    check("scope firewall", scope["finite_spectral_window_rows_closed"] and scope["finite_reverse_order_antisymmetry_closed"] and scope["finite_window_mass_rank_closed"] and scope["finite_high_cutoff_window_stability_closed"] and not scope["candidate_global_state_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["pre_a_closed"], scope, "finite spectral-window proxy only", "scope")
    rows: list[dict[str, Any]] = []
    for volume in volumes:
        reference = base.reference_localization(volume, cutoffs[0], fixture, tolerance); check(f"V={volume} reference localization", reference <= tolerance, reference, f"<={tolerance}", "locality")
        for beta in betas:
            for cutoff in cutoffs:
                value = row(volume, cutoff, beta, fixture, source_manifest, exponent, energy_windows, tolerance, positivity_tolerance, orientation_tolerance, norm_floor); all_group = value["all_group"]
                check(f"V={volume} n={cutoff} beta={beta} finite", all(np.isfinite(float(all_group[key])) and float(all_group[key]) >= -norm_floor for key in ("signed_raw_sum", "signed_gibbs_sum", "signed_weighted_sum", "absolute_raw_sum", "absolute_gibbs_sum", "absolute_weighted_sum", "signed_weighted_sum_per_site")), all_group, "finite", "numeric")
                check(f"V={volume} n={cutoff} beta={beta} coverage", value["pair_count"] > 0 and value["group_count"] > 0 and value["context_count"] > 0, [value["pair_count"], value["group_count"], value["context_count"]], ">0", "coverage")
                check(f"V={volume} n={cutoff} beta={beta} reverse antisymmetry", value["orientation_raw_residual"] <= orientation_tolerance and value["orientation_gibbs_difference"] <= orientation_tolerance and value["orientation_weighted_difference"] <= orientation_tolerance, [value["orientation_raw_residual"], value["orientation_gibbs_difference"], value["orientation_weighted_difference"]], f"<={orientation_tolerance}", "orientation")
                check(f"V={volume} n={cutoff} beta={beta} window keys", set(value["windows"]) == {format(window, "g") for window in energy_windows}, value["windows"], "declared windows", "window")
                check(f"V={volume} n={cutoff} beta={beta} window mass/rank", all(item["rank"] > 0 and -tolerance <= float(item["window_mass"]) <= 1.0 + tolerance and np.isfinite(float(item["window_mass"])) for item in value["windows"].values()), value["windows"], "positive rank and mass in [0,1]", "window")
                rows.append({"reference_localization_residual":reference, **value})
    summaries: list[dict[str, Any]] = []; threshold = float(audit["tail_stability_ratio_threshold"])
    for beta in betas:
        for energy in energy_windows:
            key = format(energy, "g"); selected = [item for item in rows if float(item["beta"]) == beta]; window_values = [item["windows"][key] for item in selected]; tail = [item["windows"][key] for item in selected if int(item["cutoff"]) >= tail_cutoff_start]; signed_tail = [float(item["signed_weighted_per_site"]) for item in tail]; conditional_tail = [float(item["conditional_signed_weighted_per_site"]) for item in tail]; ratio = max(signed_tail) / max(min(signed_tail), np.finfo(float).tiny); conditional_ratio = max(conditional_tail) / max(min(conditional_tail), np.finfo(float).tiny); endpoint = float(window_values[-1]["signed_weighted_per_site"]) / max(float(window_values[0]["signed_weighted_per_site"]), np.finfo(float).tiny); stable = ratio <= threshold and conditional_ratio <= threshold
            summary={"beta":beta,"energy_threshold":energy,"cutoff_first":cutoffs[0],"cutoff_last":cutoffs[-1],"tail_cutoff_start":tail_cutoff_start,"tail_row_count":len(tail),"signed_weighted_tail_max_per_site":max(signed_tail),"signed_weighted_tail_min_per_site":min(signed_tail),"tail_stability_ratio":ratio,"conditional_tail_stability_ratio":conditional_ratio,"full_endpoint_ratio":endpoint,"window_mass_min":min(float(item["window_mass"]) for item in window_values),"window_mass_max":max(float(item["window_mass"]) for item in window_values),"rank_min":min(int(item["rank"]) for item in window_values),"rank_max":max(int(item["rank"]) for item in window_values),"stability_threshold":threshold,"tail_stable":stable}; summaries.append(summary)
            check(f"beta={beta} E={energy} summary coverage", len(selected)==len(cutoffs) and len(tail)==sum(int(cutoff>=tail_cutoff_start) for cutoff in cutoffs) and np.isfinite(ratio) and np.isfinite(conditional_ratio), summary, "finite summary", "scaling"); check(f"beta={beta} E={energy} tail stability", stable, summary, f"<= {threshold} for signed and conditional tails", "window stability")
    diagnostic={"interpretation":"finite fixed-energy spectral-window state-weighted diagnostic; not a global KMS or asymptotic theorem","row_count":len(rows),"window_row_count":len(rows)*len(energy_windows),"all_tail_windows_stable":all(item["tail_stable"] for item in summaries),"maximum_tail_stability_ratio":max(item["tail_stability_ratio"] for item in summaries),"maximum_conditional_tail_stability_ratio":max(item["conditional_tail_stability_ratio"] for item in summaries),"candidate_global_state_uniform_bound":"not established by this audit","global_gibbs_state_transfer":"open","common_core_operator_embedding":"open","actual_q3_trotter_defect":"open"}
    check("finite-only diagnostic", diagnostic["all_tail_windows_stable"] and diagnostic["candidate_global_state_uniform_bound"]=="not established by this audit" and diagnostic["global_gibbs_state_transfer"]=="open" and diagnostic["common_core_operator_embedding"]=="open" and diagnostic["actual_q3_trotter_defect"]=="open", diagnostic, "finite-only semantics", "scope")
    check("QFT firewall", not scope["candidate_global_state_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["common_core_operator_embedding_closed"] and not scope["actual_q3_trotter_defect_closed"] and not scope["actual_q3_thermodynamic_history_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "state/window/QFT gates remain open", "scope")
    return {"schema":"tect/foundation-audit/1.0","run_kind":"independent","audit_id":"PA-CP1-ST8-Q3LOCK-LOW-ENERGY-SPECTRAL-WINDOW-AUDIT","claim_id":manifest["claim_ids"][0],"task_id":manifest["task_id"],"exploration_id":manifest["exploration_id"],"verdict":"PASS","passed":len(checks),"assertion_count":len(checks),"assertions":checks,"derived":{"source_chain":chain,"row_count":len(rows),"window_row_count":len(rows)*len(energy_windows),"rows":rows,"summary":summaries,"energy_windows":energy_windows,"tail_cutoff_start":tail_cutoff_start,"finite_spectral_window_rows_closed":True,"finite_reverse_order_antisymmetry_closed":True,"finite_window_mass_rank_closed":True,"finite_high_cutoff_window_stability_closed":diagnostic["all_tail_windows_stable"],"candidate_global_state_uniform_bound_closed":False,"global_gibbs_state_transfer_closed":False,"common_core_operator_embedding_closed":False,"actual_q3_trotter_defect_closed":False,"diagnostic":diagnostic},"boundary":scope}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args(); payload=run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO/args.output,payload)
    print(f"INDEPENDENT LOW-ENERGY-SPECTRAL-WINDOW PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']} windows={payload['derived']['window_row_count']}"); return 0

if __name__ == "__main__": raise SystemExit(main())
