#!/usr/bin/env python3
"""Primary exact audit for EXP-001063.

The audit composes two explicitly conditional scalar envelopes: the registered
four-context/factorial history rate and the EXP-001062 finite-time remainder.
It does not assert either operator-level history hypothesis.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-orbit-egf-remainder-composition-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
PRIOR = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-two-sided-duhamel-remainder-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-primary-pre-a-cp1-st8-q3lock-conditional-orbit-egf-remainder-composition/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def weighted_rate(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], source_radius: sp.Rational, root_scale: sp.Integer, neighbour_root: sp.Integer, neighbour_index: int) -> sp.Rational:
    total = sp.Rational(0)
    for monomial, coefficient in sp.Poly(sp.expand(polynomial), *variables).terms():
        field_degree = sum(monomial[:-1])
        source_degree = monomial[-1]
        total += abs(coefficient) * root_scale**field_degree * neighbour_root**monomial[neighbour_index] * source_radius**source_degree
    return sp.factor(total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    fixture = manifest["finite_fixture"]
    upstream_fixture = upstream["fixture"]
    gamma = sp.Rational(upstream_fixture["gamma"])
    kappa = sp.Rational(upstream_fixture["kappa"])
    root_scale = sp.Integer(upstream_fixture["root_scale"])
    neighbour_root = sp.Integer(upstream_fixture["neighbor_factor_root"])
    source_radius = sp.Rational(upstream_fixture["source_radius"])
    lam = sp.Rational(upstream_fixture["lambda"])
    coupling = sp.Rational(upstream_fixture["spatial_coupling"])
    q, v, r, a = sp.symbols("q v r a")
    edge = lam * (q - v) ** 2 * (q**2 + v**2) / 4
    edge_u = sp.expand(edge - lam * (q - a - v) ** 2 * ((q - a) ** 2 + v**2) / 4)
    bond = coupling * (q - r) ** 2 / 2
    bond_u = sp.expand(bond - coupling * (q - a - r) ** 2 / 2)
    onsite_q = sp.symbols("onsite_q")
    onsite = sp.Rational(3, 5) * (onsite_q**4 - (onsite_q - a) ** 4) / 4
    edge_rate = weighted_rate(edge_u, (q, v, a), source_radius, root_scale, neighbour_root, 1)
    bond_rate = weighted_rate(bond_u, (q, r, a), source_radius, root_scale, neighbour_root, 1)
    onsite_rate = weighted_rate(onsite, (onsite_q, a), source_radius, root_scale, sp.Integer(1), 0)
    B = sp.factor(onsite_rate + 3 * edge_rate + 6 * bond_rate)

    orientations = sp.Rational(fixture["orientations"])
    degree = sp.Rational(fixture["degree_bound"])
    spatial_base = sp.Rational(fixture["spatial_base"])
    time_horizon = sp.Rational(fixture["time_horizon"])
    K_initial = sp.Rational(fixture["K_initial"])
    modular_multiplier = sp.Rational(fixture["modular_multiplier"])
    eta = sp.factor(orientations * degree * spatial_base * B * time_horizon)
    denominator = sp.factor(1 - eta)
    orbit_envelope = sp.factor(K_initial / denominator)
    single = sp.factor(time_horizon**2 * orbit_envelope / 2)
    two_orientation = sp.factor(time_horizon**2 * orbit_envelope)
    modular = sp.factor(modular_multiplier * time_horizon**2 * orbit_envelope)

    check("identity", manifest["exploration_id"] == "EXP-001063" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001063/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045")
    check("prior remainder identity", prior["exploration_id"] == "EXP-001062" and prior["finite_fixture"]["orbit_bound_input"] == fixture["K_initial"], [prior["exploration_id"], prior["finite_fixture"]["orbit_bound_input"]], "EXP-001062/K_initial")
    check("positive inputs", all(value > 0 for value in (gamma, kappa, source_radius, B, orientations, degree, spatial_base, time_horizon, K_initial)), [gamma, kappa, source_radius, B, orientations, degree, spatial_base, time_horizon, K_initial], ">0")
    check("energy ratio", root_scale**4 == kappa / gamma, root_scale**4, kappa / gamma)
    check("rate recomputed", B == sp.Rational(upstream_fixture["expected_local_rate"]), B, upstream_fixture["expected_local_rate"])
    check("rate fixture", str(B) == fixture["B"], B, fixture["B"])
    check("eta derivation", eta == sp.Rational(fixture["derived_eta"]), eta, fixture["derived_eta"])
    check("eta small", 0 <= eta < 1, eta, "0<=eta<1")
    check("denominator derivation", denominator == sp.Rational(fixture["derived_one_minus_eta"]), denominator, fixture["derived_one_minus_eta"])
    check("orbit envelope derivation", orbit_envelope == sp.Rational(fixture["derived_orbit_envelope"]), orbit_envelope, fixture["derived_orbit_envelope"])
    check("single remainder derivation", single == sp.Rational(fixture["derived_single_remainder"]), single, fixture["derived_single_remainder"])
    check("two orientation derivation", two_orientation == sp.Rational(fixture["derived_two_orientation_remainder"]), two_orientation, fixture["derived_two_orientation_remainder"])
    check("modular derivation", modular == sp.Rational(fixture["derived_modular_remainder"]), modular, fixture["derived_modular_remainder"])
    check("orientation triangle", two_orientation == 2 * single, two_orientation, 2 * single)
    check("modular multiplier", modular == modular_multiplier * two_orientation, modular, modular_multiplier * two_orientation)

    scope = manifest["scope"]
    check("conditional composition scope", scope["conditional_egf_to_remainder_composition_closed"] is True and scope["geometric_history_majorant_closed_conditionally"] is True, scope, "conditional composition")
    open_keys = ("actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_orbit_bound_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-CONDITIONAL-ORBIT-EGF-REMAINDER-COMPOSITION",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "B": str(B),
            "onsite_rate": str(onsite_rate),
            "edge_rate": str(edge_rate),
            "bond_rate": str(bond_rate),
            "eta": str(eta),
            "one_minus_eta": str(denominator),
            "orbit_envelope": str(orbit_envelope),
            "single_remainder": str(single),
            "two_orientation_remainder": str(two_orientation),
            "modular_remainder": str(modular),
            "conditional_egf_to_remainder_composition_closed": True,
            "actual_q3_four_context_theorem_proved": False,
            "actual_q3_factorial_history_proved": False,
            "all_time_orbit_bound_proved": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY CONDITIONAL-ORBIT-EGF-REMAINDER PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
