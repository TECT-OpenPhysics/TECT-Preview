#!/usr/bin/env python3
"""Hostile mutation for the R-394 Gibbs spectral-tail audit."""

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
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-gibbs-spectral-tail-energy-markov-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / "2026-08-30-hostile-pre_a_cp1_st8_q3lock_gibbs_spectral_tail_energy_markov" / "hostile.json"


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


def ladder(n: int) -> tuple[np.ndarray, np.ndarray]:
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


def trace_to_core(rho: np.ndarray, n: int, volume: int, keep: list[int]) -> np.ndarray:
    rest = [site for site in range(volume) if site not in keep]
    axes = keep + rest + [site + volume for site in keep] + [site + volume for site in rest]
    tensor = np.transpose(rho.reshape((n,) * (2 * volume)), axes)
    kept_count = len(keep)
    for _ in rest:
        tensor = np.trace(tensor, axis1=kept_count, axis2=tensor.ndim // 2 + kept_count)
    return sym(tensor.reshape(n**kept_count, n**kept_count))


def run(path: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cfg = manifest["finite_fixture"]
    tolerance = float(cfg["numerical_tolerance"])
    threshold = float(cfg["hostile_threshold"])
    volume, dimension = max((int(item["volume"]), int(dim)) for item in cfg["admissible_pairs"] for dim in item["cutoff_dimensions"])
    beta = float(Fraction(cfg["beta_values"][-1]))
    values, vectors = np.linalg.eigh(hamiltonian(dimension, volume, cfg))
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    state = sym((vectors * weights) @ vectors.conj().T)
    width = max(int(value) for value in cfg["core_widths"])
    local_raw = hamiltonian(dimension, width, cfg)
    local_values, local_vectors = np.linalg.eigh(local_raw)
    local_minimum = float(local_values.min())
    shifted = local_values - local_minimum
    identity = np.eye(dimension**width, dtype=complex)
    rho_core = trace_to_core(state, dimension, volume, list(range(width)))
    first_moment = float(np.trace((local_raw - local_minimum * identity) @ rho_core).real)
    second_moment = float(np.trace((local_raw - local_minimum * identity) @ (local_raw - local_minimum * identity) @ rho_core).real)
    candidates = []
    for raw_window in cfg["energy_windows"]:
        energy = float(Fraction(raw_window))
        selector = shifted <= energy + float(cfg["positivity_tolerance"])
        projector = sym(local_vectors[:, selector] @ local_vectors[:, selector].conj().T)
        complement = sym(identity - projector)
        tail = float(np.trace(complement @ rho_core).real)
        weighted_tail = float(np.trace((local_raw - local_minimum * identity) @ complement @ rho_core).real)
        candidates.append({"energy": energy, "tail": tail, "weighted_tail": weighted_tail, "mass_bound": first_moment / energy, "weighted_bound": second_moment / energy, "rank": int(np.count_nonzero(np.linalg.eigvalsh(projector) > 0.5))})
    representative = max(candidates, key=lambda row: row["tail"])
    mutated_bound = 0.0
    mismatch = representative["tail"] - mutated_bound
    checks = [
        {"name": "interacting tail is visible", "status": "PASS" if representative["tail"] > threshold else "FAIL", "actual": representative["tail"], "expected": f">{threshold}"},
        {"name": "positive Markov bound survives", "status": "PASS" if representative["tail"] <= representative["mass_bound"] + tolerance and representative["weighted_tail"] <= representative["weighted_bound"] + tolerance else "FAIL", "actual": representative, "expected": "both moment bounds hold"},
        {"name": "zero-moment mutation caught", "status": "PASS" if mismatch > threshold else "FAIL", "actual": mismatch, "expected": f">{threshold}"},
    ]
    if any(row["status"] != "PASS" for row in checks):
        raise AssertionError(checks)
    payload = {"schema": "tect/pre-a-r394-hostile/1.0", "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"), "result_id": "R-394", "exploration_id": "EXP-001237", "verdict": "PASS", "checks": checks, "derived": {"representative": {"volume": volume, "dimension": dimension, "beta": beta, "core_width": width}, "selected": representative, "first_moment": first_moment, "second_moment": second_moment, "mutated_zero_moment_bound": mutated_bound, "mismatch": mismatch}}
    save(path, payload)
    print(f"R-394 HOSTILE PASS 3/3 representative=V{volume}/d{dimension}/beta{beta:g} tail={representative['tail']:.6g} zero_bound={mutated_bound:.6g} CAUGHT")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
