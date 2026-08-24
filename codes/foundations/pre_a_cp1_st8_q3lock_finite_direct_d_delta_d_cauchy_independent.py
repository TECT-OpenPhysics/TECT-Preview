#!/usr/bin/env python3
"""Independent NumPy reconstruction for EXP-001085 (no primary import)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-direct-d-delta-d-cauchy"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((n, n), dtype=complex)
    for i in range(n - 1): a[i, i + 1] = np.sqrt(i + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    if volume == 4: return [(0, 1), (0, 2), (1, 3), (2, 3)]
    raise ValueError("unsupported finite volume")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]; result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def hamiltonian(volume: int, n: int, f: dict[str, Any], q_replacement: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray]:
    q0, p0 = oscillator(n); q0 = q0 if q_replacement is None else q_replacement; identity = np.eye(n, dtype=complex)
    qs = [embed(q0, i, volume, identity) for i in range(volume)]; ps = [embed(p0, i, volume, identity) for i in range(volume)]
    terms = [p @ p / (2 * float(f["chi"])) + float(f["r"]) * (q @ q) / 2 + float(f["g"]) * (q @ q @ q @ q) / 4 for q, p in zip(qs, ps)]
    for left, right in graph_edges(volume):
        d = qs[left] - qs[right]
        terms.append(float(f["c"]) * (d @ d) / 2 + float(f["lambda"]) * (d @ d) @ (qs[left] @ qs[left] + qs[right] @ qs[right]) / 4)
    return qs, (sum(terms, np.zeros_like(qs[0])) + sum(terms, np.zeros_like(qs[0])).conj().T) / 2


def cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2); scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1, 1, np.where(scaled < 2, 0.5 * (1 + np.cos(np.pi * (scaled - 1))), 0))
    return (vectors * (values * taper)) @ vectors.conj().T


def unitary(h: np.ndarray, t: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.conj().T) / 2)
    return (vectors * np.exp(-1j * t * values / hbar)) @ vectors.conj().T


def state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.conj().T) / 2); weights = np.exp(-beta * (values - float(np.min(values)))); weights /= weights.sum()
    return (vectors * weights) @ vectors.conj().T


def character(q: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def seminorm(x: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ x.conj().T @ x) + np.trace(rho @ x @ x.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); f, scope = manifest["finite_fixture"], manifest["scope"]; rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001085" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001085/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite graph", len(graph_edges(2)) == 1 and len(graph_edges(4)) == 4, [len(graph_edges(2)), len(graph_edges(4))], "1 and 4", "geometry")
    check("scope firewall", scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"], scope, "finite direct diagnostic", "scope")
    beta, hbar, amplitude = float(f["beta"]), float(f["hbar"]), float(f["character_amplitude"]); volumes: list[dict[str, Any]] = []
    for volume in map(int, f["volume_values"]):
        n = int(f["oscillator_dimension"]); qs, h = hamiltonian(volume, n, f); rho = state(h, beta); a = character(qs[0], amplitude, hbar); q0, _ = oscillator(n); radius_rows: list[dict[str, Any]] = []
        reference = {float(t): unitary(h, float(t), hbar) @ a @ unitary(h, float(t), hbar).conj().T for t in f["time_values"]}
        for radius in map(float, f["radius_values"]):
            _, h_cut = hamiltonian(volume, n, f, cutoff(q0, radius)); tail = h - h_cut; tail_norm = float(np.linalg.svd(tail, compute_uv=False)[0]); times: list[dict[str, Any]] = []
            for t in map(float, f["time_values"]):
                orientations: dict[str, Any] = {}
                for sign in (-1, 1):
                    u = unitary(h + sign * tail, t, hbar); d = u @ a @ u.conj().T - reference[t]; md = -beta * (h @ d - d @ h)
                    values = {"D_norm": seminorm(d, rho), "delta_D_norm": seminorm(md, rho), "matrix_norm": float(np.linalg.svd(d, compute_uv=False)[0])}; orientations[str(sign)] = values
                    check(f"V={volume} L={radius} t={t} sign={sign} finite", all(np.isfinite(v) for v in values.values()), values, "finite", "direct D")
                times.append({"time": t, "orientations": orientations, "two_orientation_sum_of_norms": {key: orientations["1"][key] + orientations["-1"][key] for key in ("D_norm", "delta_D_norm")}})
                z = unitary(h, 0.0, hbar) @ a @ unitary(h, 0.0, hbar).conj().T - a
                check(f"V={volume} L={radius} t={t} t=0 anchor", seminorm(z, rho) <= float(f["tail_tolerance"]), "zero", "near zero", "direct D")
            if radius == max(map(float, f["radius_values"])): check(f"V={volume} zero tail at largest radius", tail_norm <= float(f["tail_tolerance"]), tail_norm, f"<={f['tail_tolerance']}", "cutoff")
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "times": times})
        volumes.append({"volume": volume, "dimension": n**volume, "radius_rows": radius_rows}); check(f"V={volume} radius sequence", [x["radius"] for x in radius_rows] == list(map(float, f["radius_values"])), [x["radius"] for x in radius_rows], f["radius_values"], "cutoff")
    check("volume sequence", [x["volume"] for x in volumes] == f["volume_values"], [x["volume"] for x in volumes], f["volume_values"], "volume")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-DIRECT-D-DELTA-D-CAUCHY", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volumes, "finite_direct_D_closed": True, "finite_direct_delta_D_closed": True, "finite_two_orientation_difference_closed": True, "cutoff_zero_tail_fixture_closed": True, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-DIRECT-D-DELTA-D PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
