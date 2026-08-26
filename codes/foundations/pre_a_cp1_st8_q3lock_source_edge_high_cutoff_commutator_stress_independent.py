#!/usr/bin/env python3
"""Independent reconstruction of EXP-001198; no primary imports."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-edge-high-cutoff-commutator-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def symmetric(a: np.ndarray) -> np.ndarray:
    return (a + a.conj().T) / 2.0


def qp(d: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((d, d), dtype=complex)
    for k in range(d - 1): lowering[k, k + 1] = np.sqrt(float(k + 1))
    return (lowering + lowering.conj().T) / np.sqrt(2.0), (lowering - lowering.conj().T) / (1j * np.sqrt(2.0))


def kron_site(one: np.ndarray, site: int, d: int) -> np.ndarray:
    eye = np.eye(d, dtype=complex)
    return np.kron(one if site == 0 else eye, one if site == 1 else eye) if site == 0 else np.kron(eye, one)


def edge_term(q0: np.ndarray, q1: np.ndarray, f: dict[str, Any]) -> np.ndarray:
    delta = q0 - q1
    square = delta @ delta
    return float(f["c"]) * square / 2.0 + float(f["lambda"]) * square @ (q0 @ q0 + q1 @ q1) / 4.0


def matrices(d: int, f: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q0, p0 = qp(d)
    q = [kron_site(q0, 0, d), kron_site(q0, 1, d)]
    p = [kron_site(p0, 0, d), kron_site(p0, 1, d)]
    r, g, chi = float(f["r"]), float(f["g"]), float(f["chi"])
    potential = sum((r * (q[site] @ q[site]) / 2.0 + g * (q[site] @ q[site] @ q[site] @ q[site]) / 4.0 for site in range(2)), np.zeros((d * d, d * d), dtype=complex))
    kinetic = sum((p[site] @ p[site] / (2.0 * chi) for site in range(2)), np.zeros_like(potential))
    bond = edge_term(q[0], q[1], f)
    return q, symmetric(kinetic + potential + bond), symmetric(potential + bond)


def shifted(a: np.ndarray) -> tuple[np.ndarray, float]:
    h = symmetric(a); m = float(np.min(np.linalg.eigvalsh(h)))
    return h + (1.0 - m) * np.eye(h.shape[0], dtype=complex), m


def spectral_inverse(k: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    values, vectors = np.linalg.eigh(symmetric(k))
    return ((vectors * (1.0 / values)) @ vectors.conj().T, (vectors * (1.0 / np.sqrt(values))) @ vectors.conj().T, float(np.min(values)))


def matrix_norm(a: np.ndarray) -> float:
    return float(np.linalg.svd(a, compute_uv=False)[0])


def vector(index: tuple[int, int], d: int) -> np.ndarray:
    out = np.zeros(d * d, dtype=complex); out[index[0] * d + index[1]] = 1.0; return out


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    f, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001198" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001198/T-054", "provenance")
    check("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope", scope["finite_high_cutoff_rows_closed"] and scope["explicit_high_core_lower_bound_rows_closed"] and not scope["uniform_commutator_bound_closed"], scope, "finite-only", "scope")

    tolerance = float(f["tolerance"]); slope = float(f["core_linear_slope_threshold"]); offset = int(f["core_linear_offset"])
    rows: list[dict[str, Any]] = []
    for dim_value in f["oscillator_dimensions"]:
        d = int(dim_value)
        q, hamiltonian, source_base = matrices(d, f)
        full, full_floor = shifted(hamiltonian); source, source_floor = shifted(source_base)
        inverse, inverse_sqrt, inverse_floor = spectral_inverse(full)
        comm = full @ source - source @ full
        comm_bound = matrix_norm(comm @ inverse)
        graph_bound = matrix_norm(source @ inverse)
        form_bound = float(np.max(np.linalg.eigvalsh(symmetric(inverse_sqrt @ source @ inverse_sqrt))))
        check(f"d={d} full floor", inverse_floor >= 1.0 - tolerance, inverse_floor, ">=1", "full")
        check(f"d={d} source floor", float(np.min(np.linalg.eigvalsh(source))) >= 1.0 - tolerance, source_floor, ">=1", "source")
        check(f"d={d} finite", all(np.isfinite(value) and value >= 0.0 for value in (comm_bound, graph_bound, form_bound)), [comm_bound, graph_bound, form_bound], "finite nonnegative", "constants")
        vector_rows: list[dict[str, Any]] = []
        for label in f["high_core_indices"]:
            index = (d - 1, d - 1) if label == "diagonal_top" else (d - 1, 0)
            state = vector(index, d)
            ratio = float(np.linalg.norm(comm @ state) / np.linalg.norm(full @ state))
            check(f"d={d} {label} dominated", ratio <= comm_bound * (1.0 + tolerance) + tolerance, ratio, f"<={comm_bound}", "core")
            vector_rows.append({"label": label, "index": list(index), "ratio": ratio, "scaled_ratio": ratio / max(float(d - offset), 1.0)})
        diagonal = next(item for item in vector_rows if item["label"] == "diagonal_top")
        lower = slope * float(d - offset)
        check(f"d={d} diagonal lower", diagonal["ratio"] + tolerance >= lower, diagonal["ratio"], f">={lower}", "cutoff lower bound")
        rows.append({"dimension": d, "global_graph_constant": graph_bound, "form_constant": form_bound, "global_commutator_constant": comm_bound, "vectors": vector_rows, "diagonal_lower_bound": lower, "full_floor": full_floor, "source_floor": source_floor})

    dimensions = [int(value) for value in f["oscillator_dimensions"]]
    check("dimension coverage", [row["dimension"] for row in rows] == dimensions, [row["dimension"] for row in rows], dimensions, "coverage")
    check("vector coverage", all(len(row["vectors"]) == len(f["high_core_indices"]) for row in rows), [len(row["vectors"]) for row in rows], len(f["high_core_indices"]), "coverage")
    first = next(row for row in rows if row["dimension"] == dimensions[0]); last = next(row for row in rows if row["dimension"] == dimensions[-1])
    first_ratio = next(v["ratio"] for v in first["vectors"] if v["label"] == "diagonal_top")
    last_ratio = next(v["ratio"] for v in last["vectors"] if v["label"] == "diagonal_top")
    growth = last_ratio / max(first_ratio, np.finfo(float).tiny)
    check("growth diagnostic", growth >= 1.0, growth, ">=1", "cutoff")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"dimension_count": len(rows), "vector_row_count": sum(len(row["vectors"]) for row in rows), "high_cutoff_rows": rows, "max_global_graph_constant": max(row["global_graph_constant"] for row in rows), "max_form_constant": max(row["form_constant"] for row in rows), "max_global_commutator_constant": max(row["global_commutator_constant"] for row in rows), "diagonal_first_ratio": first_ratio, "diagonal_last_ratio": last_ratio, "diagonal_growth_ratio": growth, "finite_high_cutoff_rows_closed": True, "explicit_high_core_lower_bound_rows_closed": True, "cutoff_growth_diagnostic_closed": True, "uniform_commutator_bound_closed": False, "cutoff_removal_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR PASS {payload['passed']}/{payload['assertion_count']} dimensions={payload['derived']['dimension_count']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())