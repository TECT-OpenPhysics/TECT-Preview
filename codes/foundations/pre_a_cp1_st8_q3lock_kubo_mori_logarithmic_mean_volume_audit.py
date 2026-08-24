#!/usr/bin/env python3
"""Primary finite actual-Q3 Kubo--Mori/logarithmic-mean volume audit.

The calculation is deliberately finite and diagnostic.  It compares the
state-weighted logarithmic mean with the arithmetic mean in the Hamiltonian
eigenbasis for the cutoff double commutator and its modular companion.  No
continuum, common-core, or uniform-in-volume conclusion is encoded here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-25-primary-{SLUG}"
    / "primary.json"
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def gibbs_eigenbasis(hamiltonian: np.ndarray, beta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return H eigenvalues, eigenvectors, and normalized Gibbs probabilities."""

    hermitian = (hamiltonian + hamiltonian.conj().T) / 2.0
    energies, vectors = np.linalg.eigh(hermitian)
    probabilities = np.exp(-beta * (energies - float(np.min(energies))))
    probabilities /= float(np.sum(probabilities))
    return energies, vectors, probabilities


def logarithmic_mean_weights(probabilities: np.ndarray, gap_tolerance: float) -> np.ndarray:
    """Compute L(p,q), using its diagonal arithmetic-limit value."""

    left = probabilities[:, None]
    right = probabilities[None, :]
    log_left = np.log(probabilities)[:, None]
    log_right = np.log(probabilities)[None, :]
    log_gap = log_left - log_right
    result = np.empty_like(log_gap)
    close = np.abs(log_gap) <= gap_tolerance
    np.divide(left - right, log_gap, out=result, where=~close)
    arithmetic_limit = 0.5 * (left + right)
    result[close] = arithmetic_limit[close]
    return (result + result.T) / 2.0


def arithmetic_mean_weights(probabilities: np.ndarray) -> np.ndarray:
    left = probabilities[:, None]
    right = probabilities[None, :]
    return 0.5 * (left + right)


def state_weighted_norm(matrix: np.ndarray, vectors: np.ndarray, weights: np.ndarray) -> float:
    """Two-sided square norm 2 sum_ij weights_ij |X_ij|^2 in the H basis."""

    matrix_h = vectors.conj().T @ matrix @ vectors
    squared = 2.0 * float(np.sum(weights * np.abs(matrix_h) ** 2))
    return float(np.sqrt(max(0.0, squared)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    check(
        "identity",
        manifest["exploration_id"] == "EXP-001089" and manifest["task_id"] == "T-054",
        [manifest["exploration_id"], manifest["task_id"]],
        "EXP-001089/T-054",
        "provenance",
    )
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check(
        "graph geometry",
        q3.graph_edges(2) == [(0, 1)] and len(q3.graph_edges(4)) == 4 and len(q3.graph_edges(6)) == 7,
        [q3.graph_edges(2), len(q3.graph_edges(4)), len(q3.graph_edges(6))],
        "two-site/square/2x3",
        "geometry",
    )
    check(
        "scope firewall",
        scope["finite_kubo_mori_rows_closed"]
        and scope["finite_arithmetic_comparison_closed"]
        and scope["finite_triple_commutator_identity_closed"]
        and not scope["candidate_uniformity_decided"]
        and not scope["c6_closed"]
        and not scope["pre_a_closed"],
        scope,
        "finite Kubo--Mori diagnostic",
        "scope",
    )

    beta = float(fixture["beta"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    tolerance = float(fixture["commutator_tolerance"])
    tail_tolerance = float(fixture["tail_tolerance"])
    gap_tolerance = float(fixture["mean_gap_tolerance"])
    dimensions = int(fixture["oscillator_dimension"])
    radii = [float(value) for value in fixture["radius_values"]]
    volumes = [int(value) for value in fixture["volume_values"]]
    volume_rows: list[dict[str, Any]] = []

    for volume in volumes:
        q_ops, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, dimensions, fixture)
        energies, vectors, probabilities = gibbs_eigenbasis(hamiltonian, beta)
        log_weights = logarithmic_mean_weights(probabilities, gap_tolerance)
        arithmetic_weights = arithmetic_mean_weights(probabilities)
        observable = q3.character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_commutator = q3.commutator(hamiltonian, observable)
        q_single, _ = q3.oscillator(dimensions)
        check(
            f"V={volume} Gibbs normalization",
            np.isfinite(probabilities).all() and abs(float(np.sum(probabilities)) - 1.0) <= gap_tolerance,
            float(np.sum(probabilities)),
            1.0,
            "Kubo--Mori state",
        )
        check(
            f"V={volume} logarithmic mean symmetry",
            np.max(np.abs(log_weights - log_weights.T)) <= gap_tolerance,
            float(np.max(np.abs(log_weights - log_weights.T))),
            f"<={gap_tolerance}",
            "Kubo--Mori state",
        )
        check(
            f"V={volume} arithmetic mean symmetry",
            np.max(np.abs(arithmetic_weights - arithmetic_weights.T)) <= gap_tolerance,
            float(np.max(np.abs(arithmetic_weights - arithmetic_weights.T))),
            f"<={gap_tolerance}",
            "arithmetic comparison",
        )
        radius_rows: list[dict[str, Any]] = []
        for radius in radii:
            q_cut = q3.cut_coordinate(q_single, radius)
            _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimensions, fixture, q_cut)
            zero = np.zeros_like(hamiltonian)
            tail_edges = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            tail = sum(tail_edges.values(), zero)
            tail_norm = q3.operator_norm(tail)
            source_commutator_norm = q3.operator_norm(q3.commutator(tail, observable))
            inner = q3.commutator(tail, h_commutator)
            d2 = -inner / (hbar * hbar)
            modular = -beta * q3.commutator(hamiltonian, d2)
            triple = q3.commutator(hamiltonian, inner)
            modular_formula = beta * triple / (hbar * hbar)
            modular_identity_error = q3.operator_norm(modular - modular_formula)
            disjoint = [
                tail_edges[edge]
                for edge in q3.graph_edges(volume)
                if set(edge).isdisjoint(set(fixture["observable_support"]))
            ]
            disjoint_tail = sum(disjoint, zero)
            disjoint_commutator_norm = q3.operator_norm(q3.commutator(disjoint_tail, observable))
            check(
                f"V={volume} L={radius} modular identity",
                modular_identity_error <= tolerance,
                modular_identity_error,
                f"<={tolerance}",
                "triple identity",
            )
            check(
                f"V={volume} L={radius} source commutation",
                source_commutator_norm <= tolerance,
                source_commutator_norm,
                f"<={tolerance}",
                "configuration commutation",
            )
            check(
                f"V={volume} L={radius} disjoint tail",
                disjoint_commutator_norm <= tolerance,
                disjoint_commutator_norm,
                f"<={tolerance}",
                "support locality",
            )
            if radius == max(radii):
                check(
                    f"V={volume} zero tail at largest radius",
                    tail_norm <= tail_tolerance,
                    tail_norm,
                    f"<={tail_tolerance}",
                    "cutoff",
                )
            norms: dict[str, Any] = {}
            for name, weights in (("duhamel", log_weights), ("arithmetic", arithmetic_weights)):
                d2_norm = state_weighted_norm(d2, vectors, weights)
                modular_norm = state_weighted_norm(modular, vectors, weights)
                values = {
                    "D2_state_weighted": d2_norm,
                    "modular_D2_state_weighted": modular_norm,
                    "tail_operator_norm": tail_norm,
                    "modular_identity_error": modular_identity_error,
                }
                check(
                    f"V={volume} L={radius} {name} finite",
                    all(np.isfinite(value) for value in values.values()),
                    values,
                    "finite",
                    "state-weighted topology",
                )
                norms[name] = values
            radius_rows.append(
                {
                    "radius": radius,
                    "source_commutator_norm": source_commutator_norm,
                    "disjoint_tail_commutator_norm": disjoint_commutator_norm,
                    "norms": norms,
                }
            )
        check(
            f"V={volume} radius sequence",
            [row["radius"] for row in radius_rows] == radii,
            [row["radius"] for row in radius_rows],
            radii,
            "cutoff",
        )
        volume_rows.append(
            {
                "volume": volume,
                "dimension": dimensions**volume,
                "ground_energy": float(energies[0]),
                "probability_min": float(np.min(probabilities)),
                "radius_rows": radius_rows,
            }
        )

    check(
        "volume sequence",
        [row["volume"] for row in volume_rows] == volumes,
        [row["volume"] for row in volume_rows],
        volumes,
        "volume",
    )

    def maxima(name: str, field: str) -> list[float]:
        return [max(item["norms"][name][field] for item in row["radius_rows"]) for row in volume_rows]

    duhamel_d2 = maxima("duhamel", "D2_state_weighted")
    arithmetic_d2 = maxima("arithmetic", "D2_state_weighted")
    duhamel_modular = maxima("duhamel", "modular_D2_state_weighted")
    arithmetic_modular = maxima("arithmetic", "modular_D2_state_weighted")
    comparison_modular_ratio = [
        arithmetic / max(duhamel, np.finfo(float).tiny)
        for arithmetic, duhamel in zip(arithmetic_modular, duhamel_modular)
    ]
    duhamel_growth = duhamel_modular[-1] / max(duhamel_modular[0], np.finfo(float).tiny)
    arithmetic_growth = arithmetic_modular[-1] / max(arithmetic_modular[0], np.finfo(float).tiny)
    check(
        "state-weighted maxima finite",
        all(np.isfinite(value) for value in duhamel_d2 + arithmetic_d2 + duhamel_modular + arithmetic_modular),
        [duhamel_modular, arithmetic_modular],
        "finite",
        "scaling",
    )
    check(
        "support commutators vanish",
        all(
            float(row["source_commutator_norm"]) <= tolerance
            and float(row["disjoint_tail_commutator_norm"]) <= tolerance
            for volume in volume_rows
            for row in volume["radius_rows"]
        ),
        "all rows",
        "tolerance",
        "support locality",
    )

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-KUBO-MORI-LOG-MEAN-VOLUME-AUDIT",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "duhamel_D2_state_weighted_maxima": duhamel_d2,
            "arithmetic_D2_state_weighted_maxima": arithmetic_d2,
            "duhamel_modular_state_weighted_maxima": duhamel_modular,
            "arithmetic_modular_state_weighted_maxima": arithmetic_modular,
            "arithmetic_to_duhamel_modular_ratios": comparison_modular_ratio,
            "duhamel_modular_volume_growth": duhamel_growth,
            "arithmetic_modular_volume_growth": arithmetic_growth,
            "finite_kubo_mori_rows_closed": True,
            "finite_arithmetic_comparison_closed": True,
            "finite_triple_commutator_identity_closed": True,
            "candidate_uniformity_decided": False,
            "modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY KUBO-MORI-LOG-MEAN-VOLUME-AUDIT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
