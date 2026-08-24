#!/usr/bin/env python3
"""Independent Fraction/polynomial audit for EXP-001063."""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-orbit-egf-remainder-composition-manifest.json"
UPSTREAM = REPO / "strategy/pre-a-cp1-st8-q3lock-weighted-mixed-graph-lift-manifest.json"
PRIOR = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-two-sided-duhamel-remainder-bridge-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-independent-pre-a-cp1-st8-q3lock-conditional-orbit-egf-remainder-composition/independent.json"
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


Poly = dict[tuple[int, ...], F]


def clean(values: Poly) -> Poly:
    return {key: value for key, value in values.items() if value}


def add(left: Poly, right: Poly) -> Poly:
    output = dict(left)
    for key, value in right.items():
        output[key] = output.get(key, F(0)) + value
    return clean(output)


def scale(poly: Poly, value: F) -> Poly:
    return clean({key: value * coefficient for key, coefficient in poly.items()})


def mul(left: Poly, right: Poly) -> Poly:
    output: Poly = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key))
            output[key] = output.get(key, F(0)) + left_value * right_value
    return clean(output)


def power(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0,) * len(next(iter(poly))): F(1)}
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def weighted_rate(poly: Poly, source_radius: F, root_scale: int, neighbour_root: int, neighbour_index: int) -> F:
    total = F(0)
    for monomial, coefficient in poly.items():
        field_degree = sum(monomial[:-1])
        source_degree = monomial[-1]
        total += abs(coefficient) * F(root_scale) ** field_degree * F(neighbour_root) ** monomial[neighbour_index] * source_radius ** source_degree
    return total


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
    gamma = F(upstream_fixture["gamma"])
    kappa = F(upstream_fixture["kappa"])
    root_scale = int(upstream_fixture["root_scale"])
    neighbour_root = int(upstream_fixture["neighbor_factor_root"])
    source_radius = F(upstream_fixture["source_radius"])
    lam = F(upstream_fixture["lambda"])
    coupling = F(upstream_fixture["spatial_coupling"])
    g = F(fixture["onsite_g"])
    q = {(1, 0, 0): F(1)}
    v = {(0, 1, 0): F(1)}
    a = {(0, 0, 1): F(1)}
    zero = {}
    q_minus_v = add(q, scale(v, F(-1)))
    q_minus_a_minus_v = add(add(q, scale(a, F(-1))), scale(v, F(-1)))
    q_minus_a = add(q, scale(a, F(-1)))
    q_squared_plus_v_squared = add(power(q, 2), power(v, 2))
    q_minus_a_squared_plus_v_squared = add(power(q_minus_a, 2), power(v, 2))
    edge = scale(mul(power(q_minus_v, 2), q_squared_plus_v_squared), lam / 4)
    edge_shifted = scale(mul(power(q_minus_a_minus_v, 2), q_minus_a_squared_plus_v_squared), lam / 4)
    edge_difference = add(edge, scale(edge_shifted, F(-1)))
    r = {(0, 1, 0): F(1)}
    q_minus_r = add(q, scale(r, F(-1)))
    q_minus_a_minus_r = add(add(q, scale(a, F(-1))), scale(r, F(-1)))
    bond_difference = scale(add(power(q_minus_r, 2), scale(power(q_minus_a_minus_r, 2), F(-1))), coupling / 2)
    onsite_difference: dict[tuple[int, ...], F] = {
        (3, 1): g,
        (2, 2): -3 * g / 2,
        (1, 3): g,
        (0, 4): -g / 4,
    }
    edge_rate = weighted_rate(edge_difference, source_radius, root_scale, neighbour_root, 1)
    bond_rate = weighted_rate(bond_difference, source_radius, root_scale, neighbour_root, 1)
    onsite_rate = weighted_rate(onsite_difference, source_radius, root_scale, 1, 0)
    B = onsite_rate + 3 * edge_rate + 6 * bond_rate

    orientations = F(fixture["orientations"])
    degree = F(fixture["degree_bound"])
    spatial_base = F(fixture["spatial_base"])
    time_horizon = F(fixture["time_horizon"])
    K_initial = F(fixture["K_initial"])
    modular_multiplier = F(fixture["modular_multiplier"])
    eta = orientations * degree * spatial_base * B * time_horizon
    denominator = 1 - eta
    orbit_envelope = K_initial / denominator
    single = time_horizon**2 * orbit_envelope / 2
    two_orientation = time_horizon**2 * orbit_envelope
    modular = modular_multiplier * two_orientation

    check("identity", manifest["exploration_id"] == "EXP-001063" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001063/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("upstream identity", upstream["exploration_id"] == "EXP-001045", upstream["exploration_id"], "EXP-001045")
    check("prior remainder identity", prior["exploration_id"] == "EXP-001062" and prior["finite_fixture"]["orbit_bound_input"] == fixture["K_initial"], [prior["exploration_id"], prior["finite_fixture"]["orbit_bound_input"]], "EXP-001062/K_initial")
    check("positive inputs", all(value > 0 for value in (gamma, kappa, source_radius, g, B, orientations, degree, spatial_base, time_horizon, K_initial)), [gamma, kappa, source_radius, g, B, orientations, degree, spatial_base, time_horizon, K_initial], ">0")
    check("energy ratio", F(root_scale**4) == kappa / gamma, root_scale**4, kappa / gamma)
    check("rate recomputed", str(B) == upstream_fixture["expected_local_rate"], B, upstream_fixture["expected_local_rate"])
    check("rate fixture", str(B) == fixture["B"], B, fixture["B"])
    check("eta derivation", str(eta) == fixture["derived_eta"], eta, fixture["derived_eta"])
    check("eta small", 0 <= eta < 1, eta, "0<=eta<1")
    check("denominator derivation", str(denominator) == fixture["derived_one_minus_eta"], denominator, fixture["derived_one_minus_eta"])
    check("orbit envelope derivation", str(orbit_envelope) == fixture["derived_orbit_envelope"], orbit_envelope, fixture["derived_orbit_envelope"])
    check("single remainder derivation", str(single) == fixture["derived_single_remainder"], single, fixture["derived_single_remainder"])
    check("two orientation derivation", str(two_orientation) == fixture["derived_two_orientation_remainder"], two_orientation, fixture["derived_two_orientation_remainder"])
    check("modular derivation", str(modular) == fixture["derived_modular_remainder"], modular, fixture["derived_modular_remainder"])
    check("orientation triangle", two_orientation == 2 * single, two_orientation, 2 * single)
    check("modular multiplier", modular == modular_multiplier * two_orientation, modular, modular_multiplier * two_orientation)

    scope = manifest["scope"]
    check("conditional composition scope", scope["conditional_egf_to_remainder_composition_closed"] is True and scope["geometric_history_majorant_closed_conditionally"] is True, scope, "conditional composition")
    open_keys = ("actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_orbit_bound_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
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
    print(f"INDEPENDENT CONDITIONAL-ORBIT-EGF-REMAINDER PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
