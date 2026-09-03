#!/usr/bin/env python3
"""Primary finite local-state weighted commutator-sum audit.

The audit evaluates every overlapping onsite/bond commutator of the declared
finite Q3 Hamiltonian on its union support.  For each union U it constructs the
induced finite Gibbs matrix rho_U and positive shifted energy K_U, then reports
the raw operator norm, the two-sided Gibbs Hilbert--Schmidt seminorm, and the
four-leg K_U^(1/2)-Gibbs seminorm.  The weighted sums are candidate coefficients
only: no seminorm Trotter inequality or global-state identification is assumed.
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
SLUG = "pre_a_cp1_st8_q3lock_state_weighted_commutator_sum_audit"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-state-weighted-commutator-sum-audit-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-primary-{SLUG}" / "primary.json"
PHYSICAL_KEYS = ("c", "chi", "r", "g", "lambda", "hbar")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def hs_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    if float(np.min(values)) < -1.0e-8:
        raise ValueError(f"spectral input is not positive: min={float(np.min(values))}")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def positive_weight(matrix: np.ndarray) -> np.ndarray:
    value = hermitian(matrix)
    minimum = float(np.min(np.linalg.eigvalsh(value)))
    return value - minimum * np.eye(value.shape[0], dtype=complex) + np.eye(value.shape[0], dtype=complex)


def gibbs(matrix: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
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


def term_specs(volume: int) -> list[dict[str, Any]]:
    return [{"kind": "onsite", "support": [site]} for site in range(volume)] + [
        {"kind": "bond", "support": list(edge)} for edge in q3.graph_edges(volume)
    ]


def support_term(spec: dict[str, Any], union: list[int], cutoff: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(cutoff)
    identity = np.eye(cutoff, dtype=complex)
    q_ops = {site: q3.embed(q_single, index, len(union), identity) for index, site in enumerate(union)}
    p_ops = {site: q3.embed(p_single, index, len(union), identity) for index, site in enumerate(union)}
    if spec["kind"] == "onsite":
        site = int(spec["support"][0])
        q, p = q_ops[site], p_ops[site]
        chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
        return hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    left, right = (int(value) for value in spec["support"])
    return hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture))


def induced_hamiltonian(union: list[int], volume: int, cutoff: int, fixture: dict[str, Any]) -> np.ndarray:
    """Build H_U from onsite terms and graph bonds wholly contained in U."""
    zero = np.zeros((cutoff ** len(union), cutoff ** len(union)), dtype=complex)
    total = zero
    for site in union:
        total += support_term({"kind": "onsite", "support": [site]}, union, cutoff, fixture)
    union_set = set(union)
    for edge in q3.graph_edges(volume):
        if set(edge).issubset(union_set):
            total += support_term({"kind": "bond", "support": list(edge)}, union, cutoff, fixture)
    return hermitian(total)


def reference_localization(volume: int, cutoff: int, fixture: dict[str, Any], tolerance: float) -> float:
    """Check one full tensor embedding against union-support commutator norms."""
    q_single, p_single = q3.oscillator(cutoff)
    identity = np.eye(cutoff, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0) for q, p in zip(q_ops, p_ops)]
    bonds = [hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture)) for left, right in q3.graph_edges(volume)]
    terms = onsite + bonds
    specs = term_specs(volume)
    maximum = 0.0
    for left_index, left_spec in enumerate(specs):
        for right_index in range(left_index + 1, len(specs)):
            right_spec = specs[right_index]
            left_support, right_support = set(left_spec["support"]), set(right_spec["support"])
            if left_support.isdisjoint(right_support):
                continue
            union = sorted(left_support | right_support)
            local_norm = operator_norm(commutator(support_term(left_spec, union, cutoff, fixture), support_term(right_spec, union, cutoff, fixture)))
            full_norm = operator_norm(commutator(terms[left_index], terms[right_index]))
            residual = abs(local_norm - full_norm)
            maximum = max(maximum, residual)
            if residual > tolerance:
                raise AssertionError(f"reference localization residual {residual} > {tolerance}")
    return maximum


def source_supports(volume: int, manifest_source: dict[str, Any]) -> list[tuple[int, ...]]:
    values = manifest_source["source_supports_by_volume"][str(volume)]
    return [tuple(int(site) for site in support) for support in values]


def row(volume: int, cutoff: int, beta: float, fixture: dict[str, Any], manifest_source: dict[str, Any], exponent: float, positivity_tolerance: float, norm_floor: float) -> dict[str, Any]:
    specs = term_specs(volume)
    source_sets = source_supports(volume, manifest_source)
    all_raw = all_gibbs = all_weighted = 0.0
    all_max_raw = all_max_gibbs = all_max_weighted = 0.0
    source_accumulates = {"-".join(map(str, source)): {"pair_count": 0, "raw_sum": 0.0, "gibbs_sum": 0.0, "weighted_sum": 0.0, "max_raw": 0.0, "max_gibbs": 0.0, "max_weighted": 0.0} for source in source_sets}
    pair_count = 0
    context_cache: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray, np.ndarray, float]] = {}
    for left_index, left_spec in enumerate(specs):
        left_support = set(int(value) for value in left_spec["support"])
        for right_spec in specs[left_index + 1 :]:
            right_support = set(int(value) for value in right_spec["support"])
            if left_support.isdisjoint(right_support):
                continue
            pair_count += 1
            union = tuple(sorted(left_support | right_support))
            if union not in context_cache:
                local_h = induced_hamiltonian(list(union), volume, cutoff, fixture)
                local_rho = gibbs(local_h, beta)
                local_rho_sqrt = spectral_power(local_rho, 0.5)
                local_k = positive_weight(local_h)
                local_k_half = spectral_power(local_k, exponent)
                minimum = float(np.min(np.linalg.eigvalsh(local_k)))
                context_cache[union] = (local_rho, local_rho_sqrt, local_k_half, minimum)
            local_rho, local_rho_sqrt, local_k_half, minimum = context_cache[union]
            if minimum < 1.0 - positivity_tolerance:
                raise AssertionError(f"positive shift failed for union {union}: {minimum}")
            left = support_term(left_spec, list(union), cutoff, fixture)
            right = support_term(right_spec, list(union), cutoff, fixture)
            value = commutator(left, right)
            raw = operator_norm(value)
            gibbs_value = two_sided_gibbs(value, local_rho)
            weighted = weighted_two_sided(value, local_k_half, local_rho_sqrt)
            if not all(np.isfinite(item) and item >= -norm_floor for item in (raw, gibbs_value, weighted)):
                raise AssertionError(f"non-finite pair at V={volume}, n={cutoff}, beta={beta}, union={union}")
            all_raw += raw
            all_gibbs += gibbs_value
            all_weighted += weighted
            all_max_raw = max(all_max_raw, raw)
            all_max_gibbs = max(all_max_gibbs, gibbs_value)
            all_max_weighted = max(all_max_weighted, weighted)
            pair_union = set(union)
            for source_key, aggregate in source_accumulates.items():
                source = set(int(value) for value in source_key.split("-"))
                if pair_union.isdisjoint(source):
                    continue
                aggregate["pair_count"] += 1
                aggregate["raw_sum"] += raw
                aggregate["gibbs_sum"] += gibbs_value
                aggregate["weighted_sum"] += weighted
                aggregate["max_raw"] = max(aggregate["max_raw"], raw)
                aggregate["max_gibbs"] = max(aggregate["max_gibbs"], gibbs_value)
                aggregate["max_weighted"] = max(aggregate["max_weighted"], weighted)
    for aggregate in source_accumulates.values():
        aggregate["raw_sum_per_source_site"] = aggregate["raw_sum"] / len(source_sets[0])
        aggregate["gibbs_sum_per_source_site"] = aggregate["gibbs_sum"] / len(source_sets[0])
        aggregate["weighted_sum_per_source_site"] = aggregate["weighted_sum"] / len(source_sets[0])
    return {
        "volume": volume,
        "cutoff": cutoff,
        "beta": beta,
        "pair_count": pair_count,
        "context_count": len(context_cache),
        "all_pair": {
            "raw_sum": all_raw,
            "gibbs_sum": all_gibbs,
            "weighted_sum": all_weighted,
            "raw_sum_per_site": all_raw / volume,
            "gibbs_sum_per_site": all_gibbs / volume,
            "weighted_sum_per_site": all_weighted / volume,
            "max_raw": all_max_raw,
            "max_gibbs": all_max_gibbs,
            "max_weighted": all_max_weighted,
        },
        "source_touching": source_accumulates,
        "weight_exponent": exponent,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source, chain = load_fixture()
    source_manifest = manifest["source_fixture"]
    audit = manifest["audit_fixture"]
    volumes = [int(value) for value in source_manifest["volume_values"]]
    cutoffs = [int(value) for value in source_manifest["cutoff_values"]]
    betas = [float(value) for value in source_manifest["beta_values"]]
    exponent = float(Fraction(str(audit["weight_exponent"])))
    tolerance = float(audit["localization_tolerance"])
    positivity_tolerance = float(audit["positivity_tolerance"])
    floor = float(audit["commutator_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    scope = manifest["scope"]
    check("identity", manifest["exploration_id"] == "EXP-001164" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001164/T-054/false", "provenance")
    check("source chain", len(chain) >= 3 and all(Path(item["path"]).is_file() for item in chain), chain, "physical fixture chain present", "provenance")
    check("physical fixture", all(key in source for key in PHYSICAL_KEYS), sorted(source), PHYSICAL_KEYS, "fixture")
    check("graph volumes", volumes == [2, 4, 6] and all(len(q3.graph_edges(volume)) > 0 for volume in volumes), volumes, "registered Q3 graph volumes", "fixture")
    check("cutoff grid", cutoffs == [3, 4, 5, 6] and all(cutoff >= 3 for cutoff in cutoffs), cutoffs, "declared cutoff grid", "fixture")
    check("beta grid", betas == [0.5, 1.0, 2.0], betas, "declared beta grid", "fixture")
    check("source support coverage", all(source_supports(volume, source_manifest) for volume in volumes), {volume: source_supports(volume, source_manifest) for volume in volumes}, "nonempty declared supports", "fixture")
    check("scope firewall", scope["finite_local_gibbs_pair_rows_closed"] and scope["finite_local_energy_weighted_pair_rows_closed"] and scope["finite_source_beta_volume_cutoff_grid_closed"] and not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["pre_a_closed"], scope, "finite local proxy only", "scope")

    rows: list[dict[str, Any]] = []
    for volume in volumes:
        reference_residual = reference_localization(volume, cutoffs[0], source, tolerance)
        check(f"V={volume} reference localization", reference_residual <= tolerance, reference_residual, f"<={tolerance}", "locality")
        for beta in betas:
            for cutoff in cutoffs:
                value = row(volume, cutoff, beta, source, source_manifest, exponent, positivity_tolerance, floor)
                check(f"V={volume} n={cutoff} beta={beta} finite", all(np.isfinite(float(value["all_pair"][key])) for key in ("raw_sum", "gibbs_sum", "weighted_sum", "raw_sum_per_site", "gibbs_sum_per_site", "weighted_sum_per_site")), value, "finite", "numeric")
                check(f"V={volume} n={cutoff} beta={beta} pair coverage", value["pair_count"] > 0 and value["context_count"] > 0, [value["pair_count"], value["context_count"]], ">0", "coverage")
                check(f"V={volume} n={cutoff} beta={beta} nonnegative", all(float(value["all_pair"][key]) >= -floor for key in ("raw_sum", "gibbs_sum", "weighted_sum")), value["all_pair"], f">={-floor}", "norm")
                check(f"V={volume} n={cutoff} beta={beta} source rows", set(value["source_touching"]) == {"-".join(map(str, support)) for support in source_supports(volume, source_manifest)}, value["source_touching"], "declared source keys", "source")
                for source_key, aggregate in value["source_touching"].items():
                    check(f"V={volume} n={cutoff} beta={beta} source={source_key} finite", all(np.isfinite(float(aggregate[key])) for key in ("raw_sum", "gibbs_sum", "weighted_sum", "raw_sum_per_source_site", "gibbs_sum_per_source_site", "weighted_sum_per_source_site")), aggregate, "finite", "source")
                rows.append({"reference_localization_residual": reference_residual, **value})

    def rows_for(volume: int, beta: float) -> list[dict[str, Any]]:
        return [value for value in rows if int(value["volume"]) == volume and float(value["beta"]) == beta]

    summary: list[dict[str, Any]] = []
    for volume in volumes:
        for beta in betas:
            selected = rows_for(volume, beta)
            raw_values = [float(value["all_pair"]["raw_sum_per_site"]) for value in selected]
            gibbs_values = [float(value["all_pair"]["gibbs_sum_per_site"]) for value in selected]
            weighted_values = [float(value["all_pair"]["weighted_sum_per_site"]) for value in selected]
            first, last = weighted_values[0], weighted_values[-1]
            growth = last / max(first, np.finfo(float).tiny)
            summary.append({
                "volume": volume,
                "beta": beta,
                "cutoff_first": cutoffs[0],
                "cutoff_last": cutoffs[-1],
                "raw_per_site_max": max(raw_values),
                "gibbs_per_site_max": max(gibbs_values),
                "weighted_per_site_max": max(weighted_values),
                "weighted_cutoff_growth_ratio": growth,
                "weighted_cutoff_nondecreasing": all(weighted_values[index] + tolerance >= weighted_values[index - 1] for index in range(1, len(weighted_values))),
                "growth_threshold": float(audit["growth_ratio_threshold"]),
                "growth_threshold_crossed": growth >= float(audit["growth_ratio_threshold"]),
            })
            check(f"V={volume} beta={beta} summary coverage", len(selected) == len(cutoffs), len(selected), len(cutoffs), "coverage")
            check(f"V={volume} beta={beta} weighted summary finite", np.isfinite(growth), growth, "finite", "scaling")

    maximum_weighted = max(float(value["all_pair"]["weighted_sum_per_site"]) for value in rows)
    diagnostic = {
        "interpretation": "finite local-state weighted coefficient diagnostic; not a global-state or asymptotic bound",
        "maximum_weighted_sum_per_site": maximum_weighted,
        "any_cutoff_growth_threshold_crossed": any(item["growth_threshold_crossed"] for item in summary),
        "candidate_cutoff_volume_beta_uniform_bound": "not established by this audit",
        "global_gibbs_state_transfer": "open",
        "common_core_operator_embedding": "open",
    }
    check("finite-only diagnostic", diagnostic["candidate_cutoff_volume_beta_uniform_bound"] == "not established by this audit" and diagnostic["global_gibbs_state_transfer"] == "open" and diagnostic["common_core_operator_embedding"] == "open", diagnostic, "finite-only semantics", "scope")
    check("QFT firewall", not scope["candidate_cutoff_volume_beta_uniform_bound_closed"] and not scope["global_gibbs_state_transfer_closed"] and not scope["common_core_operator_embedding_closed"] and not scope["actual_q3_thermodynamic_history_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "weighted/domain/QFT gates remain open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-STATE-WEIGHTED-COMMUTATOR-SUM-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "source_chain": chain,
            "row_count": len(rows),
            "rows": rows,
            "summary": summary,
            "weight_exponent": exponent,
            "finite_local_gibbs_pair_rows_closed": True,
            "finite_local_energy_weighted_pair_rows_closed": True,
            "finite_source_beta_volume_cutoff_grid_closed": True,
            "candidate_weighted_coefficient_diagnostic_closed": True,
            "candidate_cutoff_volume_beta_uniform_bound_closed": False,
            "global_gibbs_state_transfer_closed": False,
            "common_core_operator_embedding_closed": False,
            "diagnostic": diagnostic,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY STATE-WEIGHTED-COMMUTATOR-SUM PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
