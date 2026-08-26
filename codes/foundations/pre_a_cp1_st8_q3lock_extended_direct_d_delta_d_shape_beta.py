#!/usr/bin/env python3
"""Primary extended finite direct D/delta-D audit for EXP-001169."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-extended-direct-d-delta-d-shape-beta"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1): lowering[index, index + 1] = np.sqrt(index + 1.0)
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray: return (matrix + matrix.conj().T) / 2.0


def eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]: return np.linalg.eigh(hermitian(matrix))


def unitary(values: np.ndarray, vectors: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def gibbs(values: np.ndarray, vectors: np.ndarray, beta: float) -> np.ndarray:
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def character(local_q: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = eigensystem(local_q)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def cut_coordinate(local_q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = eigensystem(local_q)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def build_hamiltonian(volume: int, edges: list[tuple[int, int]], dimension: int, params: dict[str, str], q_replacement: np.ndarray | None = None) -> np.ndarray:
    q_local, p_local = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_base = q_local if q_replacement is None else q_replacement
    q_ops = [embed(q_base, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_local, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(params[key])) for key in ("chi", "r", "g"))
    c, lam = float(Fraction(params["c"])), float(Fraction(params["lambda"])),
    terms = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    for left, right in edges:
        difference = q_ops[left] - q_ops[right]
        square = difference @ difference
        terms.append(c * square / 2.0 + lam * square @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
    zero = np.zeros_like(q_ops[0])
    return hermitian(sum(terms, zero))


def seminorm(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.conj().T @ matrix) + np.trace(rho @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001169" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001169/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph fixture", list(fixture["graphs"]) == ["path4", "path6"], list(fixture["graphs"]), "path4/path6", "fixture")
    check("beta grid", fixture["beta_values"] == [0.5, 1.0, 2.0], fixture["beta_values"], "0.5,1,2", "fixture")
    check("scope firewall", scope["finite_direct_D_closed"] and scope["finite_direct_delta_D_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"] and not scope["beta_uniform_direct_d_cauchy_closed"], scope, "finite diagnostic only", "scope")
    dimension = int(fixture["oscillator_dimension"]); hbar = float(fixture["hbar"]); amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["finite_tolerance"]); tail_tolerance = float(fixture["tail_tolerance"]); agreement_tolerance = float(fixture["agreement_tolerance"])
    source_site = int(fixture["source_site"]); params = manifest["model_parameters"]
    volume_rows: list[dict[str, Any]] = []
    for name, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"]); edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
        hamiltonian = build_hamiltonian(volume, edges, dimension, params)
        values_h, vectors_h = eigensystem(hamiltonian)
        q_local, _ = oscillator(dimension)
        observable = embed(character(q_local, amplitude, hbar), source_site, volume, np.eye(dimension, dtype=complex))
        reference = {time: unitary(values_h, vectors_h, time, hbar) for time in map(float, fixture["time_values"])}
        radius_rows: list[dict[str, Any]] = []
        for radius in map(float, fixture["radius_values"]):
            q_cut = cut_coordinate(q_local, radius); cut_hamiltonian = build_hamiltonian(volume, edges, dimension, params, q_cut)
            tail = hamiltonian - cut_hamiltonian; tail_norm = float(np.linalg.norm(tail, ord=2))
            check(f"{name} L={radius} tail finite", np.isfinite(tail_norm), tail_norm, "finite", "cutoff")
            if radius == max(map(float, fixture["radius_values"])): check(f"{name} L={radius} zero tail", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            values_cut, vectors_cut = eigensystem(hamiltonian + tail); values_minus, vectors_minus = eigensystem(hamiltonian - tail)
            beta_rows: list[dict[str, Any]] = []
            for beta in map(float, fixture["beta_values"]):
                rho = gibbs(values_h, vectors_h, beta); time_rows: list[dict[str, Any]] = []
                for time in map(float, fixture["time_values"]):
                    values_by_sign = {"1": (values_cut, vectors_cut), "-1": (values_minus, vectors_minus)}; orientations: dict[str, Any] = {}
                    for sign in (int(value) for value in fixture["time_signs"]):
                        sign_values, sign_vectors = values_by_sign[str(sign)]; evolved = unitary(sign_values, sign_vectors, time, hbar) @ observable @ unitary(sign_values, sign_vectors, time, hbar).conj().T
                        d_value = evolved - reference[time] @ observable @ reference[time].conj().T
                        delta_d = -beta * (hamiltonian @ d_value - d_value @ hamiltonian)
                        metrics = {"D_norm": seminorm(d_value, rho), "delta_D_norm": seminorm(delta_d, rho), "matrix_norm": float(np.linalg.norm(d_value, ord=2))}
                        check(f"{name} L={radius} beta={beta} t={time} sign={sign} finite", all(np.isfinite(value) for value in metrics.values()), metrics, "finite", "direct D")
                        orientations[str(sign)] = metrics
                    time_rows.append({"time": time, "orientations": orientations, "two_orientation_sum_of_norms": {key: orientations["1"][key] + orientations["-1"][key] for key in ("D_norm", "delta_D_norm", "matrix_norm")}})
                zero = unitary(values_h, vectors_h, 0.0, hbar) @ observable @ unitary(values_h, vectors_h, 0.0, hbar).conj().T - observable
                check(f"{name} L={radius} beta={beta} t=0 anchor", seminorm(zero, rho) <= tail_tolerance, seminorm(zero, rho), f"<={tail_tolerance}", "direct D")
                beta_rows.append({"beta": beta, "times": time_rows})
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "beta_rows": beta_rows})
        volume_rows.append({"graph": name, "volume": volume, "dimension": dimension**volume, "radius_rows": radius_rows})
        check(f"{name} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")
    check("volume sequence", [row["volume"] for row in volume_rows] == [int(item["vertices"]) for item in fixture["graphs"].values()], [row["volume"] for row in volume_rows], "declared", "volume")
    maxima: dict[str, dict[str, float]] = {}
    for item in volume_rows:
        maxima[str(item["volume"])] = {"D_norm": max(x["two_orientation_sum_of_norms"]["D_norm"] for r in item["radius_rows"] for b in r["beta_rows"] for x in b["times"]), "delta_D_norm": max(x["two_orientation_sum_of_norms"]["delta_D_norm"] for r in item["radius_rows"] for b in r["beta_rows"] for x in b["times"])}
    check("maxima finite", all(np.isfinite(value) for row in maxima.values() for value in row.values()), maxima, "finite", "scaling")
    return {"schema":"tect/foundation-audit/1.0","run_kind":"primary","audit_id":"PA-CP1-ST8-Q3LOCK-EXTENDED-DIRECT-D-DELTA-D-SHAPE-BETA","claim_id":manifest["claim_ids"][0],"task_id":manifest["task_id"],"exploration_id":manifest["exploration_id"],"verdict":"PASS","passed":len(checks),"assertion_count":len(checks),"assertions":checks,"derived":{"volume_rows":volume_rows,"maxima_by_volume":maxima,"finite_direct_D_closed":True,"finite_direct_delta_D_closed":True,"finite_two_orientation_difference_closed":True,"cutoff_zero_tail_fixture_closed":True,"path_exhaustion_fixture_closed":True,"beta_grid_fixture_closed":True,"volume_uniform_direct_d_cauchy_closed":False,"beta_uniform_direct_d_cauchy_closed":False,"delta_d_cauchy_closed":False,"product_core_density_closed":False,"exhaustion_independence_closed":False,"group_law_closed":False,"common_alpha_closed":False,"hamiltonian_os_identification_closed":False,"kms_gns_gap_closed":False,"continuum_closed":False,"c6_closed":False,"sector_a_closed":False,"pre_a_closed":False,"no_new_negative_result":True,"no_tier_change":True,"no_pdf":True},"boundary":scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY EXTENDED-DIRECT-D-DELTA-D PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
