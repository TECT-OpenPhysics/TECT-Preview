#!/usr/bin/env python3
"""Hostile mutation for R-391.

The actual interacting Gibbs state is compared with a product of its one-site
marginals.  The mutation has zero conditional mutual information by
construction, so it must not be accepted as evidence for the interacting
boundary-transfer route when the true state has a nonzero QCMI signal.
"""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-quantum-markov-blanket-boundary-transfer-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_quantum_markov_blanket_boundary_transfer" / "hostile.json"


def save(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((n, n), dtype=complex)
    for j in range(1, n):
        lowering[j - 1, j] = np.sqrt(float(j))
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else eye)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = oscillator(n)
    eye = np.eye(n, dtype=complex)
    qs = [lift(q, site, volume, eye) for site in range(volume)]
    ps = [lift(p, site, volume, eye) for site in range(volume)]
    h = np.zeros((n**volume, n**volume), dtype=complex)
    chi, r, g, c, lam = (float(cfg[key]) for key in ("chi", "r", "g", "c", "lambda"))
    for qj, pj in zip(qs, ps):
        h += pj @ pj / (2.0 * chi) + r * qj @ qj / 2.0 + g * qj @ qj @ qj @ qj / 4.0
    for site in range(volume - 1):
        delta = qs[site] - qs[site + 1]
        delta2 = delta @ delta
        h += c * delta2 / 2.0 + lam * delta2 @ (qs[site] @ qs[site] + qs[site + 1] @ qs[site + 1]) / 4.0
    return sym(h)


def gibbs(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h)
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    return sym((vectors * weights) @ vectors.conj().T)


def reduce_sites(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    rest = [site for site in range(volume) if site not in keep]
    axes = keep + rest + [site + volume for site in keep] + [site + volume for site in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), axes)
    k = len(keep)
    for _ in rest:
        tensor = np.trace(tensor, axis1=k, axis2=tensor.ndim // 2 + k)
    size = n**k
    return sym(tensor.reshape(size, size))


def entropy(rho: np.ndarray, tol: float) -> float:
    values = np.maximum(np.linalg.eigvalsh(sym(rho)).real, 0.0)
    total = values.sum()
    probabilities = values / total
    probabilities = probabilities[probabilities > tol]
    return float(-np.dot(probabilities, np.log(probabilities)))


def layouts(volume: int, cores: list[int], buffers: list[int]) -> list[dict[str, Any]]:
    answer: list[dict[str, Any]] = []
    for core_width in cores:
        for buffer_width in buffers:
            for start in range(max(0, volume - core_width - buffer_width)):
                core = list(range(start, start + core_width))
                buffer = list(range(start + core_width, start + core_width + buffer_width))
                environment = list(range(start + core_width + buffer_width, volume))
                if environment:
                    answer.append({"core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": buffer_width})
            for end in range(core_width + buffer_width, volume + 1):
                core = list(range(end - core_width, end))
                buffer = list(range(end - core_width - buffer_width, end - core_width))
                environment = list(range(0, end - core_width - buffer_width))
                if environment:
                    answer.append({"core": core, "buffer": buffer, "environment": environment, "core_width": core_width, "buffer_width": buffer_width})
    return answer


def qcmI(rho: np.ndarray, n: int, volume: int, layout: dict[str, Any], tol: float) -> float:
    core, buffer, environment = layout["core"], layout["buffer"], layout["environment"]
    return entropy(reduce_sites(rho, n, volume, core + buffer), tol) + entropy(reduce_sites(rho, n, volume, buffer + environment), tol) - entropy(reduce_sites(rho, n, volume, buffer), tol) - entropy(reduce_sites(rho, n, volume, core + buffer + environment), tol)


def one_site_product(rho: np.ndarray, n: int, volume: int) -> np.ndarray:
    marginals = [reduce_sites(rho, n, volume, [site]) for site in range(volume)]
    result = marginals[0]
    for marginal in marginals[1:]:
        result = np.kron(result, marginal)
    return sym(result)


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tolerance = float(cfg["numerical_tolerance"])
    hostile_threshold = float(cfg["hostile_threshold"])
    pairs = [(int(item["volume"]), int(dim)) for item in cfg["admissible_pairs"] for dim in item["cutoff_dimensions"]]
    volume, dimension = max(pairs, key=lambda item: (item[0], item[1]))
    beta = float(Fraction(cfg["beta_values"][-1]))
    state = gibbs(hamiltonian(dimension, volume, cfg), beta)
    mutated = one_site_product(state, dimension, volume)
    layouts_for_system = layouts(volume, [int(value) for value in cfg["core_widths"]], [int(value) for value in cfg["buffer_widths"]])
    actual = [(layout, qcmI(state, dimension, volume, layout, tolerance)) for layout in layouts_for_system]
    product = [(layout, qcmI(mutated, dimension, volume, layout, tolerance)) for layout in layouts_for_system]
    actual_max = max(value for _, value in actual)
    product_max = max(abs(value) for _, value in product)
    actual_positive = sum(value > hostile_threshold for _, value in actual)
    width_max = {str(width): max(value for layout, value in actual if layout["buffer_width"] == width) for width in [int(value) for value in cfg["buffer_widths"]] if any(layout["buffer_width"] == width for layout, _ in actual)}
    checks = [
        {"name": "actual interacting QCMI is nonzero", "status": "PASS" if actual_max > hostile_threshold else "FAIL", "actual": actual_max, "expected": f">{hostile_threshold}"},
        {"name": "product mutation collapses QCMI", "status": "PASS" if product_max <= tolerance else "FAIL", "actual": product_max, "expected": f"<={tolerance}"},
        {"name": "hostile mismatch caught", "status": "PASS" if actual_max - product_max > hostile_threshold else "FAIL", "actual": actual_max - product_max, "expected": f">{hostile_threshold}"},
        {"name": "all product rows finite", "status": "PASS" if all(np.isfinite(value) for _, value in product) else "FAIL", "actual": len(product), "expected": "finite"}
    ]
    if any(row["status"] != "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r391-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-391", "exploration_id": "EXP-001234", "verdict": "PASS", "checks": checks, "derived": {"representative": {"volume": volume, "dimension": dimension, "beta": beta}, "actual_qcmI_max": actual_max, "product_qcmI_abs_max": product_max, "actual_positive_rows": actual_positive, "layout_count": len(layouts_for_system), "buffer_width_max": width_max, "mismatch": actual_max - product_max}}
    save(path, payload)
    print(f"R-391 HOSTILE PASS {len(checks)}/{len(checks)} representative=V{volume}/d{dimension}/beta{beta:g} actual_max={actual_max:.6g} product_max={product_max:.6g} CAUGHT")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
