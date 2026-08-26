#!/usr/bin/env python3
"""Independent reconstruction of EXP-001197; no primary-script imports."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-local-graph-norm-transfer-stress-manifest.json"
SLUG = "pre_a_cp1_st8_q3lock_source_local_graph_norm_transfer_stress"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-independent-{SLUG}" / "independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def sym(a: np.ndarray) -> np.ndarray:
    return (a + a.conj().T) / 2.0


def make_qp(d: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((d, d), dtype=complex)
    for k in range(1, d): a[k - 1, k] = np.sqrt(float(k))
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def edges(v: int) -> list[tuple[int, int]]:
    tables = {
        2: [(0, 1)],
        4: [(0, 1), (0, 2), (1, 3), (2, 3)],
        6: [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)],
    }
    return tables[v]


def lift(one: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    answer = None
    for position in range(volume):
        factor = one if position == site else eye
        answer = factor if answer is None else np.kron(answer, factor)
    return answer


def make_bond(q_left: np.ndarray, q_right: np.ndarray, f: dict[str, Any]) -> np.ndarray:
    delta = q_left - q_right
    square = delta @ delta
    c, lam = float(f["c"]), float(f["lambda"])
    return c * square / 2.0 + lam * square @ (q_left @ q_left + q_right @ q_right) / 4.0


def construct(v: int, d: int, f: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], dict[tuple[int, int], np.ndarray], np.ndarray]:
    q0, p0 = make_qp(d)
    eye = np.eye(d, dtype=complex)
    q = [lift(q0, site, v, eye) for site in range(v)]
    p = [lift(p0, site, v, eye) for site in range(v)]
    chi, r, g = float(f["chi"]), float(f["r"]), float(f["g"])
    potentials = [r * (q[site] @ q[site]) / 2.0 + g * (q[site] @ q[site] @ q[site] @ q[site]) / 4.0 for site in range(v)]
    kinetic = [p[site] @ p[site] / (2.0 * chi) for site in range(v)]
    bond = {edge: make_bond(q[edge[0]], q[edge[1]], f) for edge in edges(v)}
    zero = np.zeros_like(q[0])
    total = sum(kinetic, zero) + sum(potentials, zero) + sum(bond.values(), zero)
    return q, potentials, bond, sym(total)


def shift(a: np.ndarray) -> tuple[np.ndarray, float]:
    h = sym(a); minimum = float(np.min(np.linalg.eigvalsh(h)))
    return h + (1.0 - minimum) * np.eye(h.shape[0], dtype=complex), minimum


def norm(a: np.ndarray) -> float:
    return float(np.linalg.svd(a, compute_uv=False)[0])


def vnorm(a: np.ndarray) -> float:
    return float(np.linalg.norm(a))


def spectral_inverse(k: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    value, vector = np.linalg.eigh(sym(k))
    return ((vector * (1.0 / value)) @ vector.conj().T, (vector * (1.0 / np.sqrt(value))) @ vector.conj().T, float(np.min(value)))


def core(v: int, d: int, degree: int) -> list[tuple[int, ...]]:
    return [idx for idx in product(range(d), repeat=v) if sum(idx) <= degree]


def flat(idx: tuple[int, ...], d: int) -> int:
    answer = 0
    for value in idx: answer = answer * d + value
    return answer


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    f, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001197" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001197/T-054", "provenance")
    check("nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph tables", edges(2) == [(0, 1)] and len(edges(4)) == 4 and len(edges(6)) == 7, [edges(2), len(edges(4)), len(edges(6))], "registered", "geometry")
    check("scope", scope["finite_source_graph_form_rows_closed"] and scope["finite_source_graph_norm_rows_closed"] and scope["finite_source_commutator_rows_closed"] and not scope["uniform_common_core_graph_bound_closed"], scope, "finite-only", "scope")

    tol, ptol = float(f["graph_norm_tolerance"]), float(f["positive_tolerance"])
    degree = int(f["core_total_occupation"])
    summary: list[dict[str, Any]] = []
    cutoff: list[tuple[int, float]] = []
    core_count = 0
    dimensions = f["oscillator_dimensions_by_volume"]
    supports = f["source_supports_by_volume"]
    for volume_value in f["volume_values"]:
        v = int(volume_value)
        for dimension_value in dimensions[str(v)]:
            d = int(dimension_value)
            q, potentials, bond, h = construct(v, d, f)
            k_full, full_floor = shift(h)
            k_inv, k_inv_sqrt, shifted_floor = spectral_inverse(k_full)
            check(f"V={v} d={d} full floor", np.isfinite(full_floor), full_floor, "finite", "full")
            check(f"V={v} d={d} full positivity", shifted_floor >= 1.0 - ptol, shifted_floor, ">=1", "full")
            for support_value in supports[str(v)]:
                support = tuple(int(site) for site in support_value)
                local_v = sum((potentials[site] for site in support), np.zeros_like(h))
                inside = [edge for edge in edges(v) if edge[0] in support and edge[1] in support]
                local_e = local_v + sum((bond[edge] for edge in inside), np.zeros_like(h))
                for kind, base in (("onsite", local_v), ("edge", local_e)):
                    k_source, source_floor = shift(base)
                    comm = k_full @ k_source - k_source @ k_full
                    form = float(np.max(np.linalg.eigvalsh(sym(k_inv_sqrt @ k_source @ k_inv_sqrt))))
                    graph = norm(k_source @ k_inv)
                    comm_bound = norm(comm @ k_inv)
                    check(f"V={v} d={d} S={support} {kind} source floor", np.min(np.linalg.eigvalsh(k_source)) >= 1.0 - ptol, source_floor, ">=1", "source")
                    check(f"V={v} d={d} S={support} {kind} finite constants", all(np.isfinite(x) and x >= 0.0 for x in (form, graph, comm_bound)), [form, graph, comm_bound], "finite", "transfer")
                    basis = core(v, d, degree)
                    for idx in basis:
                        vector = np.zeros(k_full.shape[0], dtype=complex); vector[flat(idx, d)] = 1.0
                        denominator = vnorm(k_full @ vector)
                        graph_ratio = vnorm(k_source @ vector) / denominator
                        comm_ratio = vnorm(comm @ vector) / denominator
                        check(f"core graph {v}/{d}/{support}/{kind}/{idx}", graph_ratio <= graph * (1.0 + tol) + tol, graph_ratio, f"<={graph}", "core")
                        check(f"core comm {v}/{d}/{support}/{kind}/{idx}", comm_ratio <= comm_bound * (1.0 + tol) + tol, comm_ratio, f"<={comm_bound}", "core")
                    core_count += len(basis)
                    summary.append({"volume": v, "oscillator_dimension": d, "support": list(support), "kind": kind, "internal_edges": [list(edge) for edge in inside], "form_constant": form, "graph_constant": graph, "commutator_constant": comm_bound, "core_count": len(basis)})
                    if v == 2 and support == (0, 1) and kind == "edge": cutoff.append((d, comm_bound))

    expected_scenarios = sum(len(dimensions[str(v)]) * len(supports[str(v)]) * 2 for v in f["volume_values"])
    expected_core = sum(len(core(int(v), int(d), degree)) for v in f["volume_values"] for d in dimensions[str(v)] for _ in supports[str(v)] for _ in (0, 1))
    check("scenario count", len(summary) == expected_scenarios, len(summary), expected_scenarios, "coverage")
    check("core count", core_count == expected_core, core_count, expected_core, "coverage")
    expected_cutoff_dimensions = [int(value) for value in dimensions["2"]]
    check("cutoff dimensions", [d for d, _ in cutoff] == expected_cutoff_dimensions, cutoff, expected_cutoff_dimensions, "cutoff")
    positive = [(d, value) for d, value in cutoff if value > ptol]
    growth = positive[-1][1] / positive[0][1]
    check("cutoff growth", growth >= float(f["cutoff_growth_threshold"]), growth, f">={f['cutoff_growth_threshold']}", "cutoff")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-GRAPH-NORM-TRANSFER-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks,
        "derived": {"scenario_count": len(summary), "core_row_count": core_count, "summary_rows": summary, "max_form_constant": max(r["form_constant"] for r in summary), "max_graph_constant": max(r["graph_constant"] for r in summary), "max_commutator_constant": max(r["commutator_constant"] for r in summary), "cutoff_edge_commutator_rows": [{"dimension": d, "commutator_constant": value} for d, value in cutoff], "cutoff_commutator_growth": growth, "cutoff_growth_first_dimension": positive[0][0], "cutoff_growth_last_dimension": positive[-1][0], "finite_source_graph_form_rows_closed": True, "finite_source_graph_norm_rows_closed": True, "finite_source_commutator_rows_closed": True, "explicit_polynomial_core_rows_closed": True, "uniform_common_core_graph_bound_closed": False, "uniform_commutator_bound_closed": False, "cutoff_removal_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SOURCE-LOCAL-GRAPH-NORM-TRANSFER PASS {payload['passed']}/{payload['assertion_count']} scenarios={payload['derived']['scenario_count']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())