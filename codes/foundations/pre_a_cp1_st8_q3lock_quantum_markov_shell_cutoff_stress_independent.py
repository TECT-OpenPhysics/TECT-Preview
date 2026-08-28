#!/usr/bin/env python3
"""Non-importing independent reconstruction for R-393."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-shell-cutoff-stress-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-independent-pre_a_cp1_st8_q3lock_quantum_markov_shell_cutoff_stress" / "independent.json"


def dump_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sym(a: np.ndarray) -> np.ndarray:
    return (a + a.conj().T) / 2.0


def ladder(n: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        a[index - 1, index] = np.sqrt(float(index))
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def embed(a: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    factors = [a if index == site else eye for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = ladder(n)
    eye = np.eye(n, dtype=complex)
    qs = [embed(q, index, volume, eye) for index in range(volume)]
    ps = [embed(p, index, volume, eye) for index in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[name]) for name in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * qj @ qj / 2.0 + g * qj @ qj @ qj @ qj / 4.0
    for index in range(volume - 1):
        delta = qs[index] - qs[index + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[index] @ qs[index] + qs[index + 1] @ qs[index + 1]) / 4.0
    return sym(h)


def gibbs(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h)
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    return sym((vectors * weights) @ vectors.conj().T)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    kept = list(keep)
    rest = [index for index in range(volume) if index not in kept]
    order = kept + rest + [index + volume for index in kept] + [index + volume for index in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), order)
    kept_count = len(kept)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    return sym(tensor.reshape(n**kept_count, n**kept_count))


def entropy(rho: np.ndarray, tol: float) -> float:
    values = np.maximum(np.linalg.eigvalsh(sym(rho)).real, 0.0)
    probabilities = values / values.sum()
    probabilities = probabilities[probabilities > tol]
    return float(-np.sum(probabilities * np.log(probabilities)))


def layouts(volume: int, cores: list[int], buffer_width: int) -> list[dict[str, Any]]:
    answer: list[dict[str, Any]] = []
    for width in cores:
        for start in range(max(0, volume - width - buffer_width)):
            core = list(range(start, start + width))
            buffer = list(range(start + width, start + width + buffer_width))
            shell = list(range(start + width + buffer_width, volume))
            if shell:
                answer.append({"core": core, "buffer": buffer, "shell": shell, "orientation": "right", "core_width": width, "buffer_width": buffer_width})
        for end in range(width + buffer_width, volume + 1):
            core = list(range(end - width, end))
            buffer = list(range(end - width - buffer_width, end - width))
            shell = list(reversed(range(0, end - width - buffer_width)))
            if shell:
                answer.append({"core": core, "buffer": buffer, "shell": shell, "orientation": "left", "core_width": width, "buffer_width": buffer_width})
    return answer


def union(*groups: list[int]) -> list[int]:
    return sorted({item for group in groups for item in group})


def cmi(S: Any, a: list[int], b: list[int], c: list[int]) -> float:
    return S(union(a, b)) + S(union(b, c)) - S(b) - S(union(a, b, c))


def profile(rows: list[dict[str, Any]], field: str, keys: tuple[str, ...]) -> dict[str, Any]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = tuple(tuple(row[name]) if isinstance(row[name], list) else row[name] for name in keys)
        groups.setdefault(key, []).append(float(row[field]))
    records = []
    for key, values in sorted(groups.items(), key=lambda item: str(item[0])):
        records.append({"key": list(key), "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
    return {"profiles": records, "maximum_range": max((record["range"] for record in records), default=0.0)}


def cutoff_profiles(rows: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], dict[int, list[float]]] = {}
    for row in rows:
        key = (row["volume"], row["core_width"], row["orientation"], row["beta"], row["shell_index"])
        grouped.setdefault(key, {}).setdefault(int(row["dimension"]), []).append(float(row["qcmI_increment"]))
    records = []
    for key, by_dimension in sorted(grouped.items(), key=lambda item: str(item[0])):
        dimensions = []
        for dimension, values in sorted(by_dimension.items()):
            dimensions.append({"dimension": dimension, "count": len(values), "minimum": min(values), "maximum": max(values), "range": max(values) - min(values)})
        ratios = []
        for left, right in zip(dimensions, dimensions[1:]):
            denominator = float(left["maximum"])
            ratio = float(right["maximum"]) / denominator if denominator > tolerance else 0.0
            ratios.append({"from_dimension": left["dimension"], "to_dimension": right["dimension"], "ratio": ratio})
        all_values = [value for values in by_dimension.values() for value in values]
        records.append({"key": list(key), "dimensions": dimensions, "minimum": min(all_values), "maximum": max(all_values), "range": max(all_values) - min(all_values), "adjacent_ratios": ratios, "maximum_adjacent_ratio": max((item["ratio"] for item in ratios), default=0.0)})
    return {"profiles": records, "count": len(records), "maximum_range": max((row["range"] for row in records), default=0.0), "maximum_adjacent_ratio": max((row["maximum_adjacent_ratio"] for row in records), default=0.0)}


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tol = float(cfg["numerical_tolerance"])
    pairs = [(int(item["volume"]), int(dim)) for item in cfg["admissible_pairs"] for dim in item["cutoff_dimensions"]]
    betas = [float(Fraction(value)) for value in cfg["beta_values"]]
    rows: list[dict[str, Any]] = []
    q_values: list[float] = []
    increments: list[float] = []
    budgets: list[float] = []
    residuals: list[float] = []
    negative_inc = 0
    negative_cumulative = 0
    partition_count = 0
    for volume, n in pairs:
        layouts_for_system = layouts(volume, [int(value) for value in cfg["core_widths"]], int(cfg["base_buffer_width"]))
        partition_count += len(layouts_for_system)
        for beta in betas:
            rho = gibbs(hamiltonian(n, volume, cfg), beta)
            cache: dict[tuple[int, ...], float] = {}

            def S(sites: list[int]) -> float:
                key = tuple(sorted(set(sites)))
                if key not in cache:
                    cache[key] = entropy(reduce_sites(rho, n, volume, list(key)), tol)
                return cache[key]

            for layout in layouts_for_system:
                partial: list[float] = []
                for index, site in enumerate(layout["shell"]):
                    delta = cmi(S, layout["core"], layout["buffer"] + layout["shell"][:index], [site])
                    cumulative = cmi(S, layout["core"], layout["buffer"], layout["shell"][: index + 1])
                    budget = float(sum(partial) + delta)
                    residual = cumulative - budget
                    q_values.append(cumulative)
                    increments.append(delta)
                    budgets.append(budget)
                    residuals.append(residual)
                    negative_inc += int(delta < -tol)
                    negative_cumulative += int(cumulative < -tol)
                    rows.append({"volume": volume, "dimension": n, "beta": beta, "orientation": layout["orientation"], "core_width": layout["core_width"], "buffer_width": layout["buffer_width"], "shell_index": index + 1, "qcmI_increment": delta, "qcmI_cumulative": cumulative, "l1_budget_to_shell": budget, "chain_rule_residual": residual})
                    partial.append(delta)
    if negative_inc or negative_cumulative or max(abs(value) for value in residuals) > tol:
        raise AssertionError("independent QCMI shell check failed")
    if not all(np.isfinite(value) for value in q_values + increments + budgets):
        raise AssertionError("non-finite independent value")
    derived = {
        "admissible_pairs": [{"volume": v, "dimension": n} for v, n in pairs], "system_count": len(pairs), "base_partition_count": partition_count, "beta_values": betas,
        "qcmI_record_count": len(q_values), "row_count": len(rows), "qcmI_min": min(q_values), "qcmI_max": max(q_values), "increment_min": min(increments), "increment_max": max(increments), "l1_budget_min": min(budgets), "l1_budget_max": max(budgets),
        "max_chain_rule_residual": max(abs(value) for value in residuals), "negative_increment_count": negative_inc, "negative_cumulative_count": negative_cumulative,
        "qcmI_shell_profile": profile(rows, "qcmI_increment", ("core_width", "shell_index")), "cumulative_shell_profile": profile(rows, "qcmI_cumulative", ("core_width", "shell_index")), "budget_shell_profile": profile(rows, "l1_budget_to_shell", ("core_width", "shell_index")), "cutoff_profiles": cutoff_profiles(rows, tol),
    }
    payload = {"schema": "tect/pre-a-r393-independent/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-393", "exploration_id": "EXP-001236", "verdict": "PASS", "checks": 6, "derived": derived}
    dump_atomic(path, payload)
    print(f"R-393 INDEPENDENT PASS 6/6 systems={len(pairs)} partitions={partition_count} qcmI={len(q_values)} rows={len(rows)} qcmI_max={max(q_values):.6g} cutoff_ratio={derived['cutoff_profiles']['maximum_adjacent_ratio']:.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
