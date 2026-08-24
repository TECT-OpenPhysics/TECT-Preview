#!/usr/bin/env python3
"""Independent NumPy reconstruction for EXP-001087 (no primary import)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_second_duhamel_coefficient_support_audit"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "independent.json"


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


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    if volume == 4: return [(0, 1), (0, 2), (1, 3), (2, 3)]
    raise ValueError("unsupported finite volume")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]; result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def bond(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    d = left - right; c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * (d @ d) / 2.0 + lam * (d @ d) @ (left @ left + right @ right) / 4.0


def make_h(volume: int, n: int, fixture: dict[str, Any], replacement: np.ndarray | None = None) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q0, p0 = oscillator(n); identity = np.eye(n, dtype=complex)
    qs = [embed(q0, i, volume, identity) for i in range(volume)]; ps = [embed(p0, i, volume, identity) for i in range(volume)]
    b0 = q0 if replacement is None else replacement; bqs = [embed(b0, i, volume, identity) for i in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    terms = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    bs = [bond(bqs[x], bqs[y], fixture) for x, y in edges(volume)]; raw = sum(terms + bs, np.zeros_like(qs[0]))
    return qs, (raw + raw.conj().T) / 2.0, bs


def cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0); scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.conj().T) / 2.0); weights = np.exp(-beta * (values - float(np.min(values)))); weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def char(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.conj().T) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray: return a @ b - b @ a
def opnorm(a: np.ndarray) -> float: return float(np.linalg.svd(a, compute_uv=False)[0])


def snorm(a: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ a.conj().T @ a) + np.trace(rho @ a @ a.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); f, scope = manifest["finite_fixture"], manifest["scope"]; rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001087" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001087/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("two-site support", f["observable_support"] == [0, 1], f["observable_support"], [0, 1], "observable")
    check("finite graph", len(edges(2)) == 1 and len(edges(4)) == 4, [len(edges(2)), len(edges(4))], "1 and 4", "geometry")
    check("scope firewall", scope["finite_second_duhamel_coefficient_closed"] and scope["finite_modular_second_coefficient_closed"] and scope["source_character_commutation_closed"] and not scope["volume_uniform_direct_d_cauchy_closed"], scope, "finite coefficient diagnostic", "scope")
    beta, hbar, amplitude = float(f["beta"]), float(f["hbar"]), float(f["character_amplitude"]); tolerance = float(f["commutator_tolerance"]); tail_tolerance = float(f["tail_tolerance"]); volumes: list[dict[str, Any]] = []
    for volume in map(int, f["volume_values"]):
        qs, h, bs = make_h(volume, int(f["oscillator_dimension"]), f); rho = state(h, beta); a = char(qs[0] + qs[1], amplitude, hbar); hc = comm(h, a); q0, _ = oscillator(int(f["oscillator_dimension"])); radius_rows: list[dict[str, Any]] = []
        for radius in map(float, f["radius_values"]):
            _, hcut, bscut = make_h(volume, int(f["oscillator_dimension"]), f, cutoff(q0, radius)); tails = [x - y for x, y in zip(bs, bscut)]; w = sum(tails, np.zeros_like(h)); tail_norm = opnorm(w); source_norm = opnorm(comm(w, a)); base = -comm(w, hc) / (hbar * hbar); disjoint = sum([z for z, e in zip(tails, edges(volume)) if set(e).isdisjoint(set(f["observable_support"]))], np.zeros_like(h)); disjoint_norm = opnorm(comm(disjoint, a)); times: list[dict[str, Any]] = []
            for sign in (-1, 1):
                hs = h + sign * w; cs = comm(hs, a); d2 = -(comm(hs, cs) - comm(h, hc)) / (hbar * hbar); formula = sign * base; error = opnorm(d2 - formula); md2 = -beta * comm(h, d2); values = {"D2_norm": snorm(d2, rho), "modular_D2_norm": snorm(md2, rho), "D2_operator_norm": opnorm(d2), "identity_error": error}; check(f"V={volume} L={radius} sign={sign} finite", all(np.isfinite(v) for v in values.values()), values, "finite", "second coefficient"); check(f"V={volume} L={radius} sign={sign} identity", error <= tolerance, error, f"<={tolerance}", "CCR identity"); check(f"V={volume} L={radius} sign={sign} source commutation", source_norm <= tolerance, source_norm, f"<={tolerance}", "configuration commutation"); times.append({"sign": sign, "values": values})
            check(f"V={volume} L={radius} disjoint tail", disjoint_norm <= tolerance, disjoint_norm, f"<={tolerance}", "support locality")
            if radius == max(map(float, f["radius_values"])): check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            radius_rows.append({"radius": radius, "tail_operator_norm": tail_norm, "source_commutator_norm": source_norm, "disjoint_tail_commutator_norm": disjoint_norm, "times": times})
        volumes.append({"volume": volume, "dimension": int(f["oscillator_dimension"]) ** volume, "radius_rows": radius_rows}); check(f"V={volume} radius sequence", [x["radius"] for x in radius_rows] == list(map(float, f["radius_values"])), [x["radius"] for x in radius_rows], f["radius_values"], "cutoff")
    check("volume sequence", [x["volume"] for x in volumes] == f["volume_values"], [x["volume"] for x in volumes], f["volume_values"], "volume"); summary: list[dict[str, Any]] = []
    for volume in volumes:
        samples = [t["values"] for rr in volume["radius_rows"] for t in rr["times"]]; summary.append({"volume": volume["volume"], "max_D2_norm": max(x["D2_norm"] for x in samples), "max_modular_D2_norm": max(x["modular_D2_norm"] for x in samples), "max_identity_error": max(x["identity_error"] for x in samples)})
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SECOND-DUHAMEL-COEFFICIENT-SUPPORT-AUDIT", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volumes, "summary": summary, "finite_second_duhamel_coefficient_closed": True, "finite_modular_second_coefficient_closed": True, "source_character_commutation_closed": True, "disjoint_tail_support_fixture_closed": True, "coefficient_scaling_diagnostic_closed": True, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "positive_time_history_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-SECOND-DUHAMEL-COEFFICIENT PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())
