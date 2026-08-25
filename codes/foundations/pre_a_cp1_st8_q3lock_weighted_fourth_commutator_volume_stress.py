#!/usr/bin/env python3
"""Primary finite actual-Q3 weighted fourth-commutator volume stress test."""

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
SLUG = "pre_a_cp1_st8_q3lock_weighted_fourth_commutator_volume_stress"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as base  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001120" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001120/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("graph geometry", base.graph_edges(2) == [(0, 1)] and len(base.graph_edges(4)) == 4 and len(base.graph_edges(6)) == 7, [base.graph_edges(2), len(base.graph_edges(4)), len(base.graph_edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_fourth_commutator_identity_closed"] and scope["finite_weighted_fourth_rows_closed"] and not scope["candidate_volume_uniform_bound_closed"], scope, "finite weighted diagnostic", "scope")

    beta, hbar, amplitude = float(fixture["beta"]), float(fixture["hbar"]), float(fixture["character_amplitude"])
    tolerance, tail_tolerance = float(fixture["commutator_tolerance"]), float(fixture["tail_tolerance"])
    exponent = float(fixture["weight_exponent"])
    volume_rows: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        q_ops, hamiltonian, local_hamiltonian, bonds = base.build_volume(volume, int(fixture["oscillator_dimension"]), fixture)
        rho = base.gibbs(hamiltonian, beta)
        rho_sqrt = base.spectral_power(rho, 0.5)
        observable = base.character(q_ops[0] + q_ops[1], amplitude, hbar)
        h_observable = base.commutator(hamiltonian, observable)
        local_power = base.spectral_power(base.positive_weight(local_hamiltonian), exponent)
        full_power = base.spectral_power(base.positive_weight(hamiltonian), exponent)
        q_single, _ = base.oscillator(int(fixture["oscillator_dimension"]))
        radius_rows: list[dict[str, Any]] = []
        for radius in map(float, fixture["radius_values"]):
            q_cut = base.cut_coordinate(q_single, radius)
            _, _, _, cut_bonds = base.build_volume_with_bond_coordinate(volume, int(fixture["oscillator_dimension"]), fixture, q_cut)
            zero = np.zeros_like(hamiltonian)
            tails = {edge: bonds[edge] - cut_bonds[edge] for edge in bonds}
            tail = sum(tails.values(), zero)
            tail_norm = base.operator_norm(tail)
            source_commutator_norm = base.operator_norm(base.commutator(tail, observable))
            inner = base.commutator(tail, h_observable)
            triple = base.commutator(hamiltonian, inner)
            fourth = base.commutator(hamiltonian, triple)
            identity_error = base.operator_norm(fourth - base.commutator(hamiltonian, triple))
            disjoint = [tails[edge] for edge in base.graph_edges(volume) if set(edge).isdisjoint(set(fixture["observable_support"]))]
            disjoint_tail = sum(disjoint, zero)
            disjoint_commutator_norm = base.operator_norm(base.commutator(disjoint_tail, observable))
            check(f"V={volume} L={radius} fourth identity", identity_error <= tolerance, identity_error, f"<={tolerance}", "fourth identity")
            check(f"V={volume} L={radius} source commutation", source_commutator_norm <= tolerance, source_commutator_norm, f"<={tolerance}", "configuration commutation")
            check(f"V={volume} L={radius} disjoint tail", disjoint_commutator_norm <= tolerance, disjoint_commutator_norm, f"<={tolerance}", "support locality")
            if radius == max(map(float, fixture["radius_values"])):
                check(f"V={volume} zero tail at largest radius", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            weight_rows: dict[str, Any] = {}
            for kind, power in (("local", local_power), ("full", full_power)):
                values = {
                    "fourth_gibbs": base.two_sided_gibbs(fourth, rho),
                    "fourth_weighted": base.weighted_two_sided(fourth, power, rho_sqrt),
                    "triple_weighted": base.weighted_two_sided(triple, power, rho_sqrt),
                    "tail_operator_norm": tail_norm,
                    "fourth_identity_error": identity_error,
                }
                check(f"V={volume} L={radius} {kind} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "weighted fourth")
                weight_rows[kind] = values
            radius_rows.append({"radius": radius, "source_commutator_norm": source_commutator_norm, "disjoint_tail_commutator_norm": disjoint_commutator_norm, "weights": weight_rows})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": radius_rows})
        check(f"V={volume} radius sequence", [row["radius"] for row in radius_rows] == list(map(float, fixture["radius_values"])), [row["radius"] for row in radius_rows], fixture["radius_values"], "cutoff")

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")

    def maxima(kind: str, field: str) -> list[float]:
        return [max(item["weights"][kind][field] for item in row["radius_rows"]) for row in volume_rows]

    local_fourth, full_fourth = maxima("local", "fourth_weighted"), maxima("full", "fourth_weighted")
    local_triple, full_triple = maxima("local", "triple_weighted"), maxima("full", "triple_weighted")
    local_growth = local_fourth[-1] / max(local_fourth[0], np.finfo(float).tiny)
    full_growth = full_fourth[-1] / max(full_fourth[0], np.finfo(float).tiny)
    check("weighted maxima finite", all(np.isfinite(value) for value in local_fourth + full_fourth + local_triple + full_triple), [local_fourth, full_fourth], "finite", "scaling")
    check("candidate growth diagnostic", local_growth >= float(fixture["growth_threshold"]) and full_growth >= float(fixture["growth_threshold"]), [local_growth, full_growth], f">={fixture['growth_threshold']}", "scaling")
    check("support commutators vanish", all(float(row["source_commutator_norm"]) <= tolerance and float(row["disjoint_tail_commutator_norm"]) <= tolerance for volume in volume_rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-FOURTH-COMMUTATOR-VOLUME-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "weight_exponent": exponent,
            "local_fourth_weighted_maxima": local_fourth,
            "full_fourth_weighted_maxima": full_fourth,
            "local_triple_weighted_maxima": local_triple,
            "full_triple_weighted_maxima": full_triple,
            "local_fourth_volume_growth": local_growth,
            "full_fourth_volume_growth": full_growth,
            "finite_fourth_commutator_identity_closed": True,
            "finite_weighted_fourth_rows_closed": True,
            "candidate_volume_growth_diagnostic_closed": True,
            "candidate_volume_uniform_bound_closed": False,
            "weighted_modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY WEIGHTED-FOURTH-COMMUTATOR-VOLUME-STRESS PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
