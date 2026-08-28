#!/usr/bin/env python3
"""Finite high-cutoff QCMI shell stress for R-393.

The R-392 shell budget is recomputed on a deliberately higher oscillator
cutoff grid.  The output retains adjacent-cutoff profiles as diagnostics; no
finite profile is promoted to a cutoff-independent estimate.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-shell-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-primary-pre_a_cp1_st8_q3lock_quantum_markov_shell_cutoff_stress" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(index + 1.0)
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def build_hamiltonian(dimension: int, volume: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    coordinates = [lift(q_single, site, volume, identity) for site in range(volume)]
    momenta = [lift(p_single, site, volume, identity) for site in range(volume)]
    hamiltonian = np.zeros((dimension**volume, dimension**volume), dtype=complex)
    chi, r, g, c, lam = (float(fixture[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for q, p in zip(coordinates, momenta):
        hamiltonian += p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0
    for site in range(volume - 1):
        difference = coordinates[site] - coordinates[site + 1]
        difference2 = difference @ difference
        hamiltonian += c * difference2 / 2.0 + lam * difference2 @ (coordinates[site] @ coordinates[site] + coordinates[site + 1] @ coordinates[site + 1]) / 4.0
    return hermitian(hamiltonian)


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hamiltonian)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def partial_trace_sites(state: np.ndarray, dimension: int, volume: int, keep: Iterable[int]) -> np.ndarray:
    kept = list(keep)
    rest = [site for site in range(volume) if site not in kept]
    axes = kept + rest + [site + volume for site in kept] + [site + volume for site in rest]
    tensor = np.transpose(state.reshape([dimension] * (2 * volume)), axes)
    kept_count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    size = dimension**kept_count
    return hermitian(tensor.reshape(size, size))


def entropy(state: np.ndarray, tolerance: float) -> float:
    values = np.maximum(np.linalg.eigvalsh(hermitian(state)).real, 0.0)
    total = float(np.sum(values))
    if total <= tolerance:
        raise AssertionError("zero reduced state")
    probabilities = values / total
    positive = probabilities[probabilities > tolerance]
    return float(-np.sum(positive * np.log(positive)))


def shell_layouts(volume: int, core_widths: list[int], buffer_width: int) -> list[dict[str, Any]]:
    layouts: list[dict[str, Any]] = []
    for core_width in core_widths:
        for start in range(max(0, volume - core_width - buffer_width)):
            core = list(range(start, start + core_width))
            buffer = list(range(start + core_width, start + core_width + buffer_width))
            shell = list(range(start + core_width + buffer_width, volume))
            if shell:
                layouts.append({"core": core, "buffer": buffer, "shell": shell, "orientation": "right", "core_width": core_width, "buffer_width": buffer_width})
        for end in range(core_width + buffer_width, volume + 1):
            core = list(range(end - core_width, end))
            buffer = list(range(end - core_width - buffer_width, end - core_width))
            shell = list(reversed(range(0, end - core_width - buffer_width)))
            if shell:
                layouts.append({"core": core, "buffer": buffer, "shell": shell, "orientation": "left", "core_width": core_width, "buffer_width": buffer_width})
    return layouts


def canonical_sites(*groups: Iterable[int]) -> list[int]:
    return sorted({site for group in groups for site in group})


def qcmI(entropy_of: Any, core: list[int], condition: list[int], shell: list[int]) -> float:
    return entropy_of(canonical_sites(core, condition)) + entropy_of(canonical_sites(condition, shell)) - entropy_of(canonical_sites(condition)) - entropy_of(canonical_sites(core, condition, shell))


def profile(rows: list[dict[str, Any]], field: str, keys: tuple[str, ...]) -> dict[str, Any]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = tuple(tuple(row[name]) if isinstance(row[name], list) else row[name] for name in keys)
        groups.setdefault(key, []).append(float(row[field]))
    output: list[dict[str, Any]] = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        output.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
    return {"profiles": output, "maximum_range": max((row["range"] for row in output), default=0.0)}


def cutoff_profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["shell_index"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row["qcmI_increment"]))
    records: list[dict[str, Any]] = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimension_records = []
        for dimension, values in sorted(by_dimension.items()):
            dimension_records.append({"dimension": dimension, "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
        adjacent: list[dict[str, Any]] = []
        for left, right in zip(dimension_records, dimension_records[1:]):
            denominator = float(left["maximum"])
            ratio = float(right["maximum"]) / denominator if denominator > tolerance else 0.0
            adjacent.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "ratio": ratio})
        all_values = [value for values in by_dimension.values() for value in values]
        records.append({"key": list(key), "dimensions": dimension_records, "minimum": min(all_values), "maximum": max(all_values), "range": max(all_values) - min(all_values), "adjacent_ratios": adjacent, "maximum_adjacent_ratio": max((item["ratio"] for item in adjacent), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_range": max((row["range"] for row in records), default=0.0), "maximum_adjacent_ratio": max((row["maximum_adjacent_ratio"] for row in records), default=0.0)}


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    tolerance = float(fixture["numerical_tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001236" and manifest["result_id"] == "R-393" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["result_id"], manifest["claim_bearing"]], "EXP-001236/R-393/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all cutoff-stress rows", "coverage")
    finite_flags = ("finite_qcmI_shell_nonnegativity_closed", "finite_qcmI_chain_rule_closed", "finite_l1_boundary_budget_closed", "finite_buffer_shell_stress_closed", "finite_cutoff_profile_closed", "finite_product_hostile_closed")
    open_flags = tuple(name for name in scope if name.endswith("_closed") and name not in finite_flags)
    check("scope firewall", all(scope[name] for name in finite_flags) and not any(scope[name] for name in open_flags), "finite cutoff stress only", "all promoted flags false", "scope")

    pairs = [(int(item["volume"]), int(dimension)) for item in fixture["admissible_pairs"] for dimension in item["cutoff_dimensions"]]
    expected_system_count = sum(len(item["cutoff_dimensions"]) for item in fixture["admissible_pairs"])
    check("pair grid", len(pairs) == expected_system_count and len(set(pairs)) == len(pairs), pairs, f"{expected_system_count} distinct systems", "fixture")
    betas = [float(Fraction(value)) for value in fixture["beta_values"]]
    core_widths = [int(value) for value in fixture["core_widths"]]
    rows: list[dict[str, Any]] = []
    qcmI_records: list[float] = []
    increment_records: list[float] = []
    budgets: list[float] = []
    residuals: list[float] = []
    negative_increments = 0
    negative_cumulative = 0
    base_partition_count = 0

    for volume, dimension in pairs:
        layouts = shell_layouts(volume, core_widths, int(fixture["base_buffer_width"]))
        base_partition_count += len(layouts)
        for beta in betas:
            state = gibbs(build_hamiltonian(dimension, volume, fixture), beta)
            entropy_cache: dict[tuple[int, ...], float] = {}

            def S(sites: list[int]) -> float:
                key = tuple(sorted(set(sites)))
                if key not in entropy_cache:
                    entropy_cache[key] = entropy(partial_trace_sites(state, dimension, volume, key), tolerance)
                return entropy_cache[key]

            for layout in layouts:
                core, buffer, shell = layout["core"], layout["buffer"], layout["shell"]
                increments: list[float] = []
                for index, shell_site in enumerate(shell):
                    increment = qcmI(S, core, buffer + shell[:index], [shell_site])
                    cumulative = qcmI(S, core, buffer, shell[: index + 1])
                    budget = float(np.sum(increments) + increment)
                    chain_residual = cumulative - budget
                    qcmI_records.append(cumulative)
                    increment_records.append(increment)
                    residuals.append(chain_residual)
                    negative_increments += int(increment < -tolerance)
                    negative_cumulative += int(cumulative < -tolerance)
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} shell={index + 1} increment", np.isfinite(increment) and increment >= -tolerance, increment, ">=-tolerance", "QCMI increment")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} shell={index + 1} cumulative", np.isfinite(cumulative) and cumulative >= -tolerance, cumulative, ">=-tolerance", "QCMI cumulative")
                    check(f"V={volume} d={dimension} beta={beta} {layout['orientation']} shell={index + 1} chain rule", np.isfinite(chain_residual) and abs(chain_residual) <= tolerance, chain_residual, f"<={tolerance}", "chain rule")
                    rows.append({"volume": volume, "dimension": dimension, "beta": beta, "orientation": layout["orientation"], "core_width": int(layout["core_width"]), "buffer_width": int(layout["buffer_width"]), "shell_index": index + 1, "core": core, "buffer": buffer, "shell_site": shell_site, "qcmI_increment": increment, "qcmI_cumulative": cumulative, "l1_budget_to_shell": budget, "chain_rule_residual": chain_residual})
                    increments.append(increment)
                budgets.append(float(np.sum(increments)))

    check("partition aggregate", base_partition_count > 0 and len(qcmI_records) == len(rows) and len(qcmI_records) > 0, [base_partition_count, len(qcmI_records), len(rows)], "positive and aligned", "coverage")
    check("nonnegative aggregate", negative_increments == 0 and negative_cumulative == 0, [negative_increments, negative_cumulative], "zero negative rows", "QCMI")
    check("chain aggregate", max(abs(value) for value in residuals) <= tolerance, max(abs(value) for value in residuals), f"<={tolerance}", "chain rule")
    check("budget aggregate", min(budgets) >= -tolerance and all(np.isfinite(value) for value in budgets), [min(budgets), max(budgets)], "finite nonnegative budgets", "l1 budget")
    profiles = cutoff_profiles(rows, tolerance)
    check("cutoff profiles", profiles["count"] > 0 and all(np.isfinite(row["maximum_adjacent_ratio"]) for row in profiles["profiles"]), profiles["count"], "finite profile records", "cutoff stress")

    derived = {
        "admissible_pairs": [{"volume": volume, "dimension": dimension} for volume, dimension in pairs],
        "system_count": len(pairs), "base_partition_count": base_partition_count, "beta_values": betas,
        "qcmI_record_count": len(qcmI_records), "row_count": len(rows), "qcmI_min": min(qcmI_records), "qcmI_max": max(qcmI_records),
        "increment_min": min(increment_records), "increment_max": max(increment_records), "l1_budget_min": min(budgets), "l1_budget_max": max(budgets),
        "max_chain_rule_residual": max(abs(value) for value in residuals), "negative_increment_count": negative_increments, "negative_cumulative_count": negative_cumulative,
        "qcmI_shell_profile": profile(rows, "qcmI_increment", ("core_width", "shell_index")),
        "cumulative_shell_profile": profile(rows, "qcmI_cumulative", ("core_width", "shell_index")),
        "budget_shell_profile": profile(rows, "l1_budget_to_shell", ("core_width", "shell_index")),
        "cutoff_profiles": profiles,
    }
    payload = {"schema": "tect/pre-a-r393-primary/1.0", "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "result_id": "R-393", "exploration_id": "EXP-001236", "verdict": "PASS", "checks": checks, "derived": derived, "scope": scope, "records": rows}
    atomic_json(output, payload)
    print(f"R-393 PRIMARY PASS {len(checks)}/{len(checks)} systems={len(pairs)} partitions={base_partition_count} qcmI={len(qcmI_records)} rows={len(rows)} qcmI_max={max(qcmI_records):.6g} cutoff_ratio={profiles['maximum_adjacent_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
