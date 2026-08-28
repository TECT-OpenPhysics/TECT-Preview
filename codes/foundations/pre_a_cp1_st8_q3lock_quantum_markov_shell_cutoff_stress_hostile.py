#!/usr/bin/env python3
"""Hostile product-state mutation for the R-393 cutoff-stress lane."""

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
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_quantum_markov_shell_cutoff_stress" / "hostile.json"


def save(path: Path, payload: dict[str, Any]) -> None:
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


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        a[index - 1, index] = np.sqrt(float(index))
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def embed(a: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, a if index == site else eye)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = oscillator(n)
    eye = np.eye(n, dtype=complex)
    qs = [embed(q, site, volume, eye) for site in range(volume)]
    ps = [embed(p, site, volume, eye) for site in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * qj @ qj / 2.0 + g * qj @ qj @ qj @ qj / 4.0
    for index in range(volume - 1):
        delta = qs[index] - qs[index + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[index] @ qs[index] + qs[index + 1] @ qs[index + 1]) / 4.0
    return sym(h)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    rest = [index for index in range(volume) if index not in keep]
    order = keep + rest + [index + volume for index in keep] + [index + volume for index in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), order)
    kept_count = len(keep)
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


def cmi(S: Any, a: list[int], b: list[int], c: list[int]) -> float:
    union = lambda *groups: sorted({item for group in groups for item in group})
    return S(union(a, b)) + S(union(b, c)) - S(b) - S(union(a, b, c))


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tol = float(cfg["numerical_tolerance"])
    threshold = float(cfg["hostile_threshold"])
    pairs = [(int(item["volume"]), int(dim)) for item in cfg["admissible_pairs"] for dim in item["cutoff_dimensions"]]
    volume, dimension = max(pairs, key=lambda item: (item[0], item[1]))
    beta = float(Fraction(cfg["beta_values"][-1]))
    values, vectors = np.linalg.eigh(hamiltonian(dimension, volume, cfg))
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    state = sym((vectors * weights) @ vectors.conj().T)
    marginals = [reduce_sites(state, dimension, volume, [site]) for site in range(volume)]
    product = marginals[0]
    for marginal in marginals[1:]:
        product = np.kron(product, marginal)
    product = sym(product)
    layouts_for_system = layouts(volume, [int(value) for value in cfg["core_widths"]], int(cfg["base_buffer_width"]))
    actual_rows: list[float] = []
    product_rows: list[float] = []
    for rho, destination in ((state, actual_rows), (product, product_rows)):
        cache: dict[tuple[int, ...], float] = {}

        def S(sites: list[int]) -> float:
            key = tuple(sorted(set(sites)))
            if key not in cache:
                cache[key] = entropy(reduce_sites(rho, dimension, volume, list(key)), tol)
            return cache[key]

        for layout in layouts_for_system:
            for index, site in enumerate(layout["shell"]):
                destination.append(cmi(S, layout["core"], layout["buffer"] + layout["shell"][:index], [site]))
    actual_max = max(actual_rows)
    product_max = max(abs(value) for value in product_rows)
    mismatch = actual_max - product_max
    checks = [
        {"name": "interacting shell signal", "status": "PASS" if actual_max > threshold else "FAIL", "actual": actual_max, "expected": f">{threshold}"},
        {"name": "product mutation collapses increments", "status": "PASS" if product_max <= tol else "FAIL", "actual": product_max, "expected": f"<={tol}"},
        {"name": "hostile mismatch caught", "status": "PASS" if mismatch > threshold else "FAIL", "actual": mismatch, "expected": f">{threshold}"},
    ]
    if any(row["status"] != "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r393-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-393", "exploration_id": "EXP-001236", "verdict": "PASS", "checks": checks, "derived": {"representative": {"volume": volume, "dimension": dimension, "beta": beta}, "layout_count": len(layouts_for_system), "actual_increment_max": actual_max, "product_increment_abs_max": product_max, "mismatch": mismatch}}
    save(path, payload)
    print(f"R-393 HOSTILE PASS 3/3 representative=V{volume}/d{dimension}/beta{beta:g} actual_max={actual_max:.6g} product_max={product_max:.6g} CAUGHT")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
