#!/usr/bin/env python3
"""Hostile factor mutation for the R-395 gentle bridge."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-gibbs-gentle-projection-bridge-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_gibbs_gentle_projection_bridge" / "hostile.json"


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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def ladder(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        lowering[index - 1, index] = np.sqrt(float(index))
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else eye)
    return result


def hamiltonian(n: int, volume: int, cfg: dict[str, Any]) -> np.ndarray:
    q, p = ladder(n)
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
    rest = [site for site in range(volume) if site not in keep]
    axes = keep + rest + [site + volume for site in keep] + [site + volume for site in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), axes)
    count = len(keep)
    for _ in rest:
        tensor = np.trace(tensor, axis1=count, axis2=tensor.ndim // 2 + count)
    return sym(tensor.reshape(n**len(keep), n**len(keep)))


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tolerance = float(cfg["numerical_tolerance"])
    threshold = float(cfg["hostile_threshold"])
    volume, dimension, width, beta, energy = 5, 4, 2, float(Fraction(cfg["beta_values"][-1])), 4.0
    values, vectors = np.linalg.eigh(hamiltonian(dimension, volume, cfg))
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    state = sym((vectors * weights) @ vectors.conj().T)
    raw = hamiltonian(dimension, width, cfg)
    local_values, local_vectors = np.linalg.eigh(raw)
    minimum = float(local_values.min())
    shifted = local_values - minimum
    identity = np.eye(dimension**width, dtype=complex)
    selected = shifted <= energy + float(cfg["positivity_tolerance"])
    projector = sym(local_vectors[:, selected] @ local_vectors[:, selected].conj().T)
    rho_core = reduce_sites(state, dimension, volume, list(range(width)))
    complement = sym(identity - projector)
    tail = max(0.0, float(np.trace(complement @ rho_core).real))
    disturbance = float(np.sum(np.abs(np.linalg.eigvalsh(sym(rho_core - projector @ rho_core @ projector)).real)))
    genuine_bound = 2.0 * np.sqrt(tail)
    mutated_bound = np.sqrt(tail)
    checks = [
        {"name": "finite disturbance visible", "status": "PASS" if disturbance > threshold else "FAIL", "actual": disturbance, "expected": f">{threshold}"},
        {"name": "genuine factor-two bound", "status": "PASS" if disturbance <= genuine_bound + tolerance else "FAIL", "actual": [disturbance, genuine_bound], "expected": "disturbance <= 2 sqrt(tail)"},
        {"name": "factor-one mutation caught", "status": "PASS" if disturbance > mutated_bound + threshold else "FAIL", "actual": [disturbance, mutated_bound, disturbance - mutated_bound], "expected": "disturbance > sqrt(tail)"}
    ]
    if any(row["status"] != "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r395-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-395", "exploration_id": "EXP-001238", "verdict": "PASS", "checks": checks, "derived": {"representative": {"volume": volume, "dimension": dimension, "core_width": width, "beta": beta, "energy_window": energy}, "tail_mass": tail, "trace_disturbance": disturbance, "genuine_bound": genuine_bound, "mutated_factor_one_bound": mutated_bound, "mutation_gap": disturbance - mutated_bound}}
    save(path, payload)
    print(f"R-395 HOSTILE PASS 3/3 representative=V{volume}/d{dimension}/w{width}/beta{beta:g}/E{energy:g} disturbance={disturbance:.6g} factor-one-mutation CAUGHT")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
