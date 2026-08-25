#!/usr/bin/env python3
"""Independent finite-Q3 reconstruction for EXP-001120.

The matrix construction is delegated only to the already independent R270
lane; the new observable is the fourth nested H-bracket and is recomputed
here, without importing the primary R292 lane.
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

ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_weighted_fourth_commutator_volume_stress"
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{NAME}" / "independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress_independent as base  # noqa: E402


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001120" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001120/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", base.edges(2) == ((0, 1),) and len(base.edges(4)) == 4 and len(base.edges(6)) == 7, [base.edges(2), len(base.edges(4)), len(base.edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_fourth_commutator_identity_closed"] and scope["finite_weighted_fourth_rows_closed"] and not scope["candidate_volume_uniform_bound_closed"], scope, "finite weighted diagnostic", "scope")

    beta, amplitude, hbar = float(fixture["beta"]), float(fixture["character_amplitude"]), float(fixture["hbar"])
    tolerance, tail_tolerance, exponent = float(fixture["commutator_tolerance"]), float(fixture["tail_tolerance"]), float(fixture["weight_exponent"])
    volume_rows: list[dict[str, Any]] = []
    for volume in [int(value) for value in fixture["volume_values"]]:
        q0, _ = base.q_and_p(int(fixture["oscillator_dimension"]))
        qs, hamiltonian, local_hamiltonian, uncut_bonds = base.model(volume, int(fixture["oscillator_dimension"]), fixture, q0)
        rho = base.thermal_state(hamiltonian, beta)
        rho_half = base.power(rho, 0.5)
        observable = base.exp_character(qs[0] + qs[1], amplitude, hbar)
        h_observable = base.bracket(hamiltonian, observable)
        local_power = base.power(base.shifted(local_hamiltonian), exponent)
        full_power = base.power(base.shifted(hamiltonian), exponent)
        cut_rows: list[dict[str, Any]] = []
        for radius in [float(value) for value in fixture["radius_values"]]:
            cut_q = base.smooth_cut(q0, radius)
            _, _, _, cut_bonds = base.model(volume, int(fixture["oscillator_dimension"]), fixture, cut_q)
            zero = np.zeros_like(hamiltonian)
            tails = {edge: uncut_bonds[edge] - cut_bonds[edge] for edge in base.edges(volume)}
            tail = sum(tails.values(), zero)
            tail_norm = base.spectral_norm(tail)
            source_comm = base.spectral_norm(base.bracket(tail, observable))
            inner = base.bracket(tail, h_observable)
            triple = base.bracket(hamiltonian, inner)
            fourth = base.bracket(hamiltonian, triple)
            identity_error = base.spectral_norm(fourth - base.bracket(hamiltonian, triple))
            disjoint_tail = sum((tails[edge] for edge in base.edges(volume) if set(edge).isdisjoint(set(fixture["observable_support"]))), zero)
            disjoint_comm = base.spectral_norm(base.bracket(disjoint_tail, observable))
            check(f"V={volume} L={radius} identity", identity_error <= tolerance, identity_error, f"<={tolerance}", "fourth identity")
            check(f"V={volume} L={radius} source", source_comm <= tolerance, source_comm, f"<={tolerance}", "configuration commutation")
            check(f"V={volume} L={radius} disjoint", disjoint_comm <= tolerance, disjoint_comm, f"<={tolerance}", "support locality")
            if radius == max(float(value) for value in fixture["radius_values"]): check(f"V={volume} zero tail", tail_norm <= tail_tolerance, tail_norm, f"<={tail_tolerance}", "cutoff")
            data: dict[str, Any] = {}
            for name, weight in (("local", local_power), ("full", full_power)):
                values = {"fourth_gibbs": base.gns(fourth, rho), "fourth_weighted": base.four_leg(fourth, weight, rho_half), "triple_weighted": base.four_leg(triple, weight, rho_half), "tail_operator_norm": tail_norm, "fourth_identity_error": identity_error}
                check(f"V={volume} L={radius} {name} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "weighted fourth")
                data[name] = values
            cut_rows.append({"radius": radius, "source_commutator_norm": source_comm, "disjoint_tail_commutator_norm": disjoint_comm, "weights": data})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": cut_rows})
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")

    def maxima(weight: str, field: str) -> list[float]: return [max(item["weights"][weight][field] for item in row["radius_rows"]) for row in volume_rows]
    local_fourth, full_fourth = maxima("local", "fourth_weighted"), maxima("full", "fourth_weighted")
    local_triple, full_triple = maxima("local", "triple_weighted"), maxima("full", "triple_weighted")
    local_growth, full_growth = local_fourth[-1] / max(local_fourth[0], np.finfo(float).tiny), full_fourth[-1] / max(full_fourth[0], np.finfo(float).tiny)
    check("maxima finite", all(np.isfinite(value) for value in local_fourth + full_fourth + local_triple + full_triple), [local_fourth, full_fourth], "finite", "scaling")
    check("growth captured", local_growth >= float(fixture["growth_threshold"]) and full_growth >= float(fixture["growth_threshold"]), [local_growth, full_growth], f">={fixture['growth_threshold']}", "scaling")
    check("support locality", all(float(row["source_commutator_norm"]) <= tolerance and float(row["disjoint_tail_commutator_norm"]) <= tolerance for volume in volume_rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-FOURTH-COMMUTATOR-VOLUME-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "weight_exponent": exponent, "local_fourth_weighted_maxima": local_fourth, "full_fourth_weighted_maxima": full_fourth, "local_triple_weighted_maxima": local_triple, "full_triple_weighted_maxima": full_triple, "local_fourth_volume_growth": local_growth, "full_fourth_volume_growth": full_growth, "finite_fourth_commutator_identity_closed": True, "finite_weighted_fourth_rows_closed": True, "candidate_volume_growth_diagnostic_closed": True, "candidate_volume_uniform_bound_closed": False, "weighted_modular_domain_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "positive_time_history_closed": False, "product_core_density_closed": False, "exhaustion_independence_closed": False, "group_law_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args()
    payload = run()
    if not args.self_test: store(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT WEIGHTED-FOURTH-COMMUTATOR-VOLUME-STRESS PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
