#!/usr/bin/env python3
"""Independent reconstruction of the EXP-001164 local weighted audit.

This file deliberately does not import the primary audit.  It reconstructs
the oscillator, graph terms, local Gibbs contexts, and all aggregate norms from
the manifest so the integrated lane can detect a shared implementation error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_state_weighted_commutator_sum_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-commutator-sum-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"
PHYSICAL_KEYS = ("c", "chi", "r", "g", "lambda", "hbar")


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("declared graph has only volumes 2, 4, and 6")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def hs_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    if float(np.min(values)) < -1.0e-8:
        raise ValueError(f"spectral input is not positive: min={float(np.min(values))}")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def positive_weight(matrix: np.ndarray) -> np.ndarray:
    value = hermitian(matrix)
    minimum = float(np.min(np.linalg.eigvalsh(value)))
    return value - minimum * np.eye(value.shape[0], dtype=complex) + np.eye(value.shape[0], dtype=complex)


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def two_sided_gibbs(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def weighted_two_sided(matrix: np.ndarray, weight_power: np.ndarray, rho_sqrt: np.ndarray) -> float:
    legs = (
        weight_power @ matrix @ rho_sqrt,
        weight_power @ matrix.conj().T @ rho_sqrt,
        matrix @ weight_power @ rho_sqrt,
        matrix.conj().T @ weight_power @ rho_sqrt,
    )
    return float(np.sqrt(sum(hs_norm(leg) ** 2 for leg in legs)))


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


def specs(volume: int) -> list[tuple[str, tuple[int, ...]]]:
    return [("onsite", (site,)) for site in range(volume)] + [("bond", edge) for edge in graph_edges(volume)]


def bond_term(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (left @ left + right @ right) / 4.0


def local_term(spec: tuple[str, tuple[int, ...]], union: list[int], cutoff: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = oscillator(cutoff)
    identity = np.eye(cutoff, dtype=complex)
    q_ops = {site: embed(q_single, index, len(union), identity) for index, site in enumerate(union)}
    p_ops = {site: embed(p_single, index, len(union), identity) for index, site in enumerate(union)}
    kind, support = spec
    if kind == "onsite":
        q, p = q_ops[support[0]], p_ops[support[0]]
        chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
        return hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    return hermitian(bond_term(q_ops[support[0]], q_ops[support[1]], fixture))


def induced_hamiltonian(union: list[int], volume: int, cutoff: int, fixture: dict[str, Any]) -> np.ndarray:
    zero = np.zeros((cutoff ** len(union), cutoff ** len(union)), dtype=complex)
    total = zero
    for site in union:
        total += local_term(("onsite", (site,)), union, cutoff, fixture)
    union_set = set(union)
    for edge in graph_edges(volume):
        if set(edge).issubset(union_set):
            total += local_term(("bond", edge), union, cutoff, fixture)
    return hermitian(total)


def reference_localization(volume: int, cutoff: int, fixture: dict[str, Any], tolerance: float) -> float:
    q_single, p_single = oscillator(cutoff)
    identity = np.eye(cutoff, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0) for q, p in zip(q_ops, p_ops)]
    bonds = [hermitian(bond_term(q_ops[left], q_ops[right], fixture)) for left, right in graph_edges(volume)]
    terms = onsite + bonds
    declared = specs(volume)
    maximum = 0.0
    for left_index, left_spec in enumerate(declared):
        for right_index in range(left_index + 1, len(declared)):
            right_spec = declared[right_index]
            if set(left_spec[1]).isdisjoint(right_spec[1]):
                continue
            union = sorted(set(left_spec[1]) | set(right_spec[1]))
            local_norm = operator_norm(commutator(local_term(left_spec, union, cutoff, fixture), local_term(right_spec, union, cutoff, fixture)))
            full_norm = operator_norm(commutator(terms[left_index], terms[right_index]))
            residual = abs(local_norm - full_norm)
            maximum = max(maximum, residual)
            if residual > tolerance:
                raise AssertionError(f"reference localization residual {residual} > {tolerance}")
    return maximum


def row(volume: int, cutoff: int, beta: float, fixture: dict[str, Any], source_manifest: dict[str, Any], exponent: float, positivity_tolerance: float, norm_floor: float) -> dict[str, Any]:
    declared = specs(volume)
    source_sets = [tuple(int(site) for site in support) for support in source_manifest["source_supports_by_volume"][str(volume)]]
    aggregates = {"-".join(map(str, support)): {"pair_count": 0, "raw_sum": 0.0, "gibbs_sum": 0.0, "weighted_sum": 0.0, "max_raw": 0.0, "max_gibbs": 0.0, "max_weighted": 0.0} for support in source_sets}
    total = {"raw_sum": 0.0, "gibbs_sum": 0.0, "weighted_sum": 0.0, "max_raw": 0.0, "max_gibbs": 0.0, "max_weighted": 0.0}
    cache: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray, np.ndarray, float]] = {}
    pair_count = 0
    for left_index, left_spec in enumerate(declared):
        for right_spec in declared[left_index + 1 :]:
            if set(left_spec[1]).isdisjoint(right_spec[1]):
                continue
            pair_count += 1
            union = tuple(sorted(set(left_spec[1]) | set(right_spec[1])))
            if union not in cache:
                local_h = induced_hamiltonian(list(union), volume, cutoff, fixture)
                rho = gibbs(local_h, beta)
                rho_sqrt = spectral_power(rho, 0.5)
                k_half = spectral_power(positive_weight(local_h), exponent)
                minimum = float(np.min(np.linalg.eigvalsh(positive_weight(local_h))))
                cache[union] = (rho, rho_sqrt, k_half, minimum)
            rho, rho_sqrt, k_half, minimum = cache[union]
            if minimum < 1.0 - positivity_tolerance:
                raise AssertionError(f"positive shift failed for union {union}: {minimum}")
            value = commutator(local_term(left_spec, list(union), cutoff, fixture), local_term(right_spec, list(union), cutoff, fixture))
            raw = operator_norm(value)
            gibbs_value = two_sided_gibbs(value, rho)
            weighted = weighted_two_sided(value, k_half, rho_sqrt)
            if not all(np.isfinite(item) and item >= -norm_floor for item in (raw, gibbs_value, weighted)):
                raise AssertionError(f"non-finite pair at V={volume}, n={cutoff}, beta={beta}, union={union}")
            total["raw_sum"] += raw
            total["gibbs_sum"] += gibbs_value
            total["weighted_sum"] += weighted
            total["max_raw"] = max(total["max_raw"], raw)
            total["max_gibbs"] = max(total["max_gibbs"], gibbs_value)
            total["max_weighted"] = max(total["max_weighted"], weighted)
            for key, aggregate in aggregates.items():
                support = set(int(site) for site in key.split("-"))
                if set(union).isdisjoint(support):
                    continue
                aggregate["pair_count"] += 1
                aggregate["raw_sum"] += raw
                aggregate["gibbs_sum"] += gibbs_value
                aggregate["weighted_sum"] += weighted
                aggregate["max_raw"] = max(aggregate["max_raw"], raw)
                aggregate["max_gibbs"] = max(aggregate["max_gibbs"], gibbs_value)
                aggregate["max_weighted"] = max(aggregate["max_weighted"], weighted)
    for aggregate in aggregates.values():
        source_size = len(source_sets[0])
        aggregate["raw_sum_per_source_site"] = aggregate["raw_sum"] / source_size
        aggregate["gibbs_sum_per_source_site"] = aggregate["gibbs_sum"] / source_size
        aggregate["weighted_sum_per_source_site"] = aggregate["weighted_sum"] / source_size
    return {
        "volume": volume,
        "cutoff": cutoff,
        "beta": beta,
        "pair_count": pair_count,
        "context_count": len(cache),
        "all_pair": {
            "raw_sum": total["raw_sum"],
            "gibbs_sum": total["gibbs_sum"],
            "weighted_sum": total["weighted_sum"],
            "raw_sum_per_site": total["raw_sum"] / volume,
            "gibbs_sum_per_site": total["gibbs_sum"] / volume,
            "weighted_sum_per_site": total["weighted_sum"] / volume,
            "max_raw": total["max_raw"],
            "max_gibbs": total["max_gibbs"],
            "max_weighted": total["max_weighted"],
        },
        "source_touching": aggregates,
        "weight_exponent": exponent,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, chain = load_fixture()
    source_manifest, audit, scope = manifest["source_fixture"], manifest["audit_fixture"], manifest["scope"]
    volumes = [int(value) for value in source_manifest["volume_values"]]
    cutoffs = [int(value) for value in source_manifest["cutoff_values"]]
    betas = [float(value) for value in source_manifest["beta_values"]]
    exponent = float(Fraction(str(audit["weight_exponent"])))
    tolerance, positivity_tolerance, floor = float(audit["localization_tolerance"]), float(audit["positivity_tolerance"]), float(audit["commutator_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001164" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001164/T-054/false", "provenance")
    check("source chain", len(chain) >= 3 and all(Path(item["path"]).is_file() for item in chain), chain, "physical fixture chain present", "provenance")
    check("physical fixture", all(key in fixture for key in PHYSICAL_KEYS), sorted(fixture), PHYSICAL_KEYS, "fixture")
    check("graph volumes", volumes == [2, 4, 6] and all(graph_edges(volume) for volume in volumes), volumes, "registered Q3 graph volumes", "fixture")
    check("cutoff grid", cutoffs == [3, 4, 5, 6], cutoffs, "declared cutoff grid", "fixture")
    check("beta grid", betas == [0.5, 1.0, 2.0], betas, "declared beta grid", "fixture")
    check("source support coverage", all(source_manifest["source_supports_by_volume"].get(str(volume)) for volume in volumes), source_manifest["source_supports_by_volume"], "nonempty source supports", "fixture")
    check("scope firewall", scope["finite_local_gibbs_pair_rows_closed"] and scope["finite_local_energy_weighted_pair_rows_closed"] and scope["finite_source_beta_volume_cutoff_grid_closed"] and not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["pre_a_closed"], scope, "finite local proxy only", "scope")
    rows: list[dict[str, Any]] = []
    for volume in volumes:
        reference = reference_localization(volume, cutoffs[0], fixture, tolerance)
        check(f"V={volume} reference localization", reference <= tolerance, reference, f"<={tolerance}", "locality")
        for beta in betas:
            for cutoff in cutoffs:
                value = row(volume, cutoff, beta, fixture, source_manifest, exponent, positivity_tolerance, floor)
                check(f"V={volume} n={cutoff} beta={beta} finite", all(np.isfinite(float(value["all_pair"][key])) for key in ("raw_sum", "gibbs_sum", "weighted_sum", "raw_sum_per_site", "gibbs_sum_per_site", "weighted_sum_per_site")), value, "finite", "numeric")
                check(f"V={volume} n={cutoff} beta={beta} coverage", value["pair_count"] > 0 and value["context_count"] > 0, [value["pair_count"], value["context_count"]], ">0", "coverage")
                check(f"V={volume} n={cutoff} beta={beta} nonnegative", all(float(value["all_pair"][key]) >= -floor for key in ("raw_sum", "gibbs_sum", "weighted_sum")), value["all_pair"], f">={-floor}", "norm")
                rows.append({"reference_localization_residual": reference, **value})
    summary: list[dict[str, Any]] = []
    for volume in volumes:
        for beta in betas:
            selected = [value for value in rows if int(value["volume"]) == volume and float(value["beta"]) == beta]
            weighted = [float(value["all_pair"]["weighted_sum_per_site"]) for value in selected]
            raw = [float(value["all_pair"]["raw_sum_per_site"]) for value in selected]
            gibbs_values = [float(value["all_pair"]["gibbs_sum_per_site"]) for value in selected]
            growth = weighted[-1] / max(weighted[0], np.finfo(float).tiny)
            summary.append({"volume": volume, "beta": beta, "cutoff_first": cutoffs[0], "cutoff_last": cutoffs[-1], "raw_per_site_max": max(raw), "gibbs_per_site_max": max(gibbs_values), "weighted_per_site_max": max(weighted), "weighted_cutoff_growth_ratio": growth, "weighted_cutoff_nondecreasing": all(weighted[index] + tolerance >= weighted[index - 1] for index in range(1, len(weighted))), "growth_threshold": float(audit["growth_ratio_threshold"]), "growth_threshold_crossed": growth >= float(audit["growth_ratio_threshold"])})
            check(f"V={volume} beta={beta} summary", len(selected) == len(cutoffs) and np.isfinite(growth), [len(selected), growth], [len(cutoffs), "finite"], "scaling")
    maximum_weighted = max(float(value["all_pair"]["weighted_sum_per_site"]) for value in rows)
    diagnostic = {"interpretation": "finite local-state weighted coefficient diagnostic; not a global-state or asymptotic bound", "maximum_weighted_sum_per_site": maximum_weighted, "any_cutoff_growth_threshold_crossed": any(item["growth_threshold_crossed"] for item in summary), "candidate_cutoff_volume_beta_uniform_bound": "not established by this audit", "global_gibbs_state_transfer": "open", "common_core_operator_embedding": "open"}
    check("finite-only diagnostic", diagnostic["candidate_cutoff_volume_beta_uniform_bound"] == "not established by this audit" and diagnostic["global_gibbs_state_transfer"] == "open" and diagnostic["common_core_operator_embedding"] == "open", diagnostic, "finite-only semantics", "scope")
    check("QFT firewall", not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["common_core_operator_embedding_closed"] and not scope["actual_q3_thermodynamic_history_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "weighted/domain/QFT gates remain open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-COMMUTATOR-SUM-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"source_chain": chain, "row_count": len(rows), "rows": rows, "summary": summary, "weight_exponent": exponent, "finite_local_gibbs_pair_rows_closed": True, "finite_local_energy_weighted_pair_rows_closed": True, "finite_source_beta_volume_cutoff_grid_closed": True, "candidate_weighted_coefficient_diagnostic_closed": True, "candidate_cutoff_volume_beta_uniform_bound_closed": False, "global_gibbs_state_transfer_closed": False, "common_core_operator_embedding_closed": False, "diagnostic": diagnostic}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT STATE-WEIGHTED-COMMUTATOR-SUM PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
