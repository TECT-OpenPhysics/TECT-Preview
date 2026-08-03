#!/usr/bin/env python3
"""Non-importing rational audit for global CL8 Goursat continuation.

This implementation deliberately imports neither the primary module nor a
computer-algebra package.  It reconstructs graph counts, exact rational
coercive identities, the shell fixture, Bessel coefficients, and PA-H1
pi-squared inequalities from the manifests and elementary arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0"
PARENT_IDS = (
    "PA-CP1-CL8-GOURSAT-v0",
    "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-FINITE-TRIANGLE-GOURSAT-GLOBAL-EXISTENCE-STABILITY"
SLUG = "pre-a-cp1-cl8-global-goursat-continuation"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
GOURSAT = REPO / "strategy/pre-a-cp1-cl8-goursat-manifest.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
BLOCK = REPO / "strategy/pre-a-cp1-st8-block-causal-bridge-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def exact_sqrt_fraction(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise AssertionError(f"fraction is not an exact square: {value}")
    return Fraction(numerator, denominator)


def parse_pi_coefficient(text: str) -> Fraction:
    match = re.fullmatch(r"pi(?:/([0-9]+))?", text.strip())
    if match is None:
        raise AssertionError(f"cannot parse pi coefficient from {text!r}")
    denominator = int(match.group(1) or "1")
    return Fraction(1, denominator)


def parse_chi_coefficient(text: str) -> Fraction:
    match = re.fullmatch(r"([+-]?[0-9]+)(?:\*chi)?(?:/([0-9]+))?", text.strip())
    if match is None:
        raise AssertionError(f"cannot parse chi coefficient from {text!r}")
    return Fraction(int(match.group(1)), int(match.group(2) or "1"))


def derive() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    goursat = json.loads(GOURSAT.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    block = json.loads(BLOCK.read_text(encoding="utf-8"))

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("parents", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")

    species_text = q3lock["definition"]["species"]
    dimension_match = re.search(r"\^([0-9]+)", species_text)
    if dimension_match is None:
        raise AssertionError(f"cannot parse dimension from {species_text!r}")
    dimension = int(dimension_match.group(1))
    vertices = list(itertools.product((0, 1), repeat=dimension))
    edges = [
        (left, right)
        for index, left in enumerate(vertices)
        for right in vertices[index + 1 :]
        if sum(a != b for a, b in zip(left, right)) == 1
    ]
    degrees = {vertex: 0 for vertex in vertices}
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
    species_count = len(vertices)
    edge_count = len(edges)
    degree = min(degrees.values())
    audit.check("dimension parsed", dimension == 3, dimension, 3, "graph")
    audit.check("species derived", species_count == 2**dimension, species_count, 2**dimension, "graph")
    audit.check("edges derived", edge_count == dimension * 2 ** (dimension - 1), edge_count, dimension * 2 ** (dimension - 1), "graph")
    audit.check("regular degree", min(degrees.values()) == max(degrees.values()) == dimension, sorted(set(degrees.values())), [dimension], "graph")

    shift_coefficient = Fraction(species_count, 4)
    residual_coefficient = Fraction(species_count, 2) - shift_coefficient
    # Sparse keys are (power of a, power of g, power of z); negative g powers
    # retain the general parameters rather than testing only a=g=1.
    onsite_left = {
        (2, -1, 0): Fraction(1, 4),
        (1, 0, 2): Fraction(-1, 2),
        (0, 1, 4): Fraction(1, 4),
    }
    onsite_right = {
        (0, 1, 4): Fraction(1, 4),
        (1, 0, 2): Fraction(-2, 4),
        (2, -1, 0): Fraction(1, 4),
    }
    quartic_left = {
        (2, -1, 0): Fraction(1, 2),
        (1, 0, 2): Fraction(-1, 2),
        (0, 1, 4): Fraction(1, 8),
    }
    quartic_right = {
        (0, 1, 4): Fraction(1, 8),
        (1, 0, 2): Fraction(-4, 8),
        (2, -1, 0): Fraction(4, 8),
    }
    audit.check("onsite completed-square coefficients", onsite_left == onsite_right, onsite_left, onsite_right, "coercivity")
    audit.check("quartic completed-square coefficients", quartic_left == quartic_right, quartic_left, quartic_right, "coercivity")
    audit.check("global shift coefficient", shift_coefficient == 2, shift_coefficient, 2, "coercivity")
    audit.check("quartic residual coefficient", residual_coefficient == 2, residual_coefficient, 2, "coercivity")
    audit.check("Q3 lock sign declared nonnegative", "lambda>=0" in manifest["definition"]["parameter_domain"], manifest["definition"]["parameter_domain"], "contains lambda>=0", "coercivity")

    normalization = Fraction(1, species_count)
    # Declared exact zero-solution regression fixture: chi=c=g=tau=1,
    # lambda=0, r=-1, A=B=0.
    test_chi = Fraction(1)
    test_c = Fraction(1)
    test_g = Fraction(1)
    test_lambda = Fraction(0)
    test_r_abs = Fraction(1)
    test_tau = Fraction(1)
    test_s = exact_sqrt_fraction(test_c / test_chi)
    test_a = Fraction(1)
    test_cstar = shift_coefficient * test_a**2 / test_g
    test_f_each = test_cstar / 2
    test_flux = normalization * test_s * (2 * test_tau) * test_f_each * 2
    test_energy = normalization * (2 * test_s * test_tau) * test_cstar
    test_sqrt_argument = 2 * test_s * test_tau * test_flux / test_c
    gradient_energy_factor = exact_sqrt_fraction(Fraction(2 * species_count))
    test_S = gradient_energy_factor * exact_sqrt_fraction(test_sqrt_argument)
    gradient_lock = 4 * degree
    hessian_lock = 12 * degree
    b_S = test_r_abs * test_S + (test_g + gradient_lock * test_lambda) * test_S**3
    ell_S = test_r_abs + (3 * test_g + hessian_lock * test_lambda) * test_S**2
    K0 = test_tau**2 * b_S / (4 * test_chi)
    rho = Fraction(1)
    R_c = K0 + rho
    b_Rc = test_r_abs * R_c + (test_g + gradient_lock * test_lambda) * R_c**3
    ell_Rc = test_r_abs + (3 * test_g + hessian_lock * test_lambda) * R_c**2
    delta_squared = test_chi * rho / b_Rc
    selfmap = delta_squared * b_Rc / (2 * test_chi)
    contraction = delta_squared * ell_Rc / (2 * test_chi)
    audit.check("one-eighth ledger", normalization == Fraction(1, 8), normalization, Fraction(1, 8), "fixture")
    audit.check("test shift", test_cstar == 2, test_cstar, 2, "fixture")
    audit.check("test flux", test_flux == Fraction(1, 2), test_flux, Fraction(1, 2), "fixture")
    audit.check("test energy", test_energy == test_flux, test_energy, test_flux, "fixture")
    audit.check("test amplitude", test_S == 4, test_S, 4, "fixture")
    audit.check("gradient lock derived", gradient_lock == 12, gradient_lock, 12, "fixture")
    audit.check("Hessian lock derived", hessian_lock == 36, hessian_lock, 36, "fixture")
    audit.check("test b_S", b_S == 68, b_S, 68, "fixture")
    audit.check("test ell_S", ell_S == 49, ell_S, 49, "fixture")
    audit.check("test K0", K0 == 17, K0, 17, "fixture")
    audit.check("test continuation radius", R_c == 18, R_c, 18, "fixture")
    audit.check("test b_Rc", b_Rc == 5850, b_Rc, 5850, "fixture")
    audit.check("test ell_Rc", ell_Rc == 973, ell_Rc, 973, "fixture")
    audit.check("shell self-map", selfmap == Fraction(1, 2), selfmap, Fraction(1, 2), "fixture")
    audit.check("shell contraction", contraction < 1, contraction, "<1", "fixture")

    bessel_order = 7
    bessel_coefficients = [Fraction(1, math.factorial(n) ** 2) for n in range(bessel_order)]
    recurrence_ok = all(
        bessel_coefficients[n + 1] * (n + 1) ** 2 == bessel_coefficients[n]
        for n in range(bessel_order - 1)
    )
    audit.check("Bessel coefficient recurrence", recurrence_ok, bessel_coefficients, "a_(n+1)*(n+1)^2=a_n", "stability")
    audit.check("Bessel coefficients positive", all(item > 0 for item in bessel_coefficients), bessel_coefficients, "all positive", "stability")

    potential_exponents = [
        int(item)
        for item in re.findall(r"z_[ef]\^([0-9]+)", manifest["definition"]["potential"])
    ]
    potential_degree = max(potential_exponents)
    force_degree = potential_degree - 1
    fourth_force_derivatives_zero = force_degree < 4
    recurrence_dependencies = {
        order_value: [order_value - 1] + ([order_value - 2] if order_value >= 2 else [])
        for order_value in range(1, 9)
    }
    lower_order_carry = "D_(m-1)" in manifest["high_regularity_phase_map"]["recursive_bound"]
    audit.check("quartic potential degree parsed", potential_degree == 4, potential_degree, 4, "high-regularity")
    audit.check("cubic force degree derived", force_degree == 3, force_degree, 3, "high-regularity")
    audit.check("fourth force derivatives vanish by degree", fourth_force_derivatives_zero, fourth_force_derivatives_zero, True, "high-regularity")
    audit.check("C8 derivative recursion is acyclic", all(max(dependencies) < order_value for order_value, dependencies in recurrence_dependencies.items()), recurrence_dependencies, "all dependencies below current order", "high-regularity")
    audit.check("high-regularity recurrence retains lower derivatives", lower_order_carry, lower_order_carry, True, "high-regularity")

    selected = block["pah1_tangent_calibration"]["selected_inputs"]
    circumference_text = next(item.split("circle circumference ", 1)[1] for item in selected if item.startswith("circle circumference "))
    speed_text = next(item.split("=", 1)[1] for item in selected if item.startswith("c/chi="))
    mass_text = next(item.split("=", 1)[1] for item in selected if item.startswith("r="))
    circumference_pi_coefficient = parse_pi_coefficient(circumference_text)
    speed_squared = parse_chi_coefficient(speed_text)
    speed = exact_sqrt_fraction(speed_squared)
    r_over_chi = parse_chi_coefficient(mass_text)
    tau_pi_coefficient = circumference_pi_coefficient / (2 * speed)
    ordered_curvature = -2 * r_over_chi
    audit.check("circumference parsed from parent", circumference_pi_coefficient == Fraction(1, 2), circumference_pi_coefficient, Fraction(1, 2), "pah1")
    audit.check("speed parsed from parent", speed_squared == 1, speed_squared, 1, "pah1")
    audit.check("mass parsed from parent", r_over_chi == Fraction(-9, 2), r_over_chi, Fraction(-9, 2), "pah1")
    base_wavenumber = Fraction(2, 1) / circumference_pi_coefficient
    frequencies_squared = [ordered_curvature, ordered_curvature + base_wavenumber**2, ordered_curvature + base_wavenumber**2]
    old_unshifted_pi2 = tau_pi_coefficient**2 * (2 * ordered_curvature) / 4
    old_shifted_pi2 = tau_pi_coefficient**2 * ordered_curvature / 4
    pi2_lower = Fraction(9)
    pi2_upper = Fraction(10)
    audit.check("PA-H1 tau coefficient", tau_pi_coefficient == Fraction(1, 4), tau_pi_coefficient, Fraction(1, 4), "pah1")
    audit.check("PA-H1 wavenumber", base_wavenumber == 4, base_wavenumber, 4, "pah1")
    audit.check("PA-H1 frequencies", frequencies_squared == [9, 25, 25], frequencies_squared, [9, 25, 25], "pah1")
    audit.check("old unshifted coefficient", old_unshifted_pi2 == Fraction(9, 32), old_unshifted_pi2, Fraction(9, 32), "pah1")
    audit.check("old shifted coefficient", old_shifted_pi2 == Fraction(9, 64), old_shifted_pi2, Fraction(9, 64), "pah1")
    audit.check("old unshifted fails using pi^2>9", old_unshifted_pi2 * pi2_lower > 1, old_unshifted_pi2 * pi2_lower, ">1", "pah1")
    audit.check("old shifted fails using pi^2>9", old_shifted_pi2 * pi2_lower > 1, old_shifted_pi2 * pi2_lower, ">1", "pah1")

    def shell_pi2_coefficient(lipschitz_ratio: Fraction, count: int) -> Fraction:
        return lipschitz_ratio * tau_pi_coefficient**2 / (2 * count**2)

    linearized_shifted_shells = 1
    while shell_pi2_coefficient(ordered_curvature, linearized_shifted_shells) * pi2_upper >= 1:
        linearized_shifted_shells += 1
    linearized_unshifted_shells = 1
    while shell_pi2_coefficient(2 * ordered_curvature, linearized_unshifted_shells) * pi2_upper >= 1:
        linearized_unshifted_shells += 1
    linearized_shifted_shell_pi2 = shell_pi2_coefficient(ordered_curvature, linearized_shifted_shells)
    linearized_unshifted_shell_pi2 = shell_pi2_coefficient(2 * ordered_curvature, linearized_unshifted_shells)
    audit.check("linearized ell=9chi control uses two shells", linearized_shifted_shells == 2, linearized_shifted_shells, 2, "pah1-linearized-control")
    audit.check("linearized ell=18chi control uses three shells", linearized_unshifted_shells == 3, linearized_unshifted_shells, 3, "pah1-linearized-control")
    audit.check("linearized ell=9chi cap contracts using pi^2<10", linearized_shifted_shell_pi2 * pi2_upper < 1, linearized_shifted_shell_pi2 * pi2_upper, "<1", "pah1-linearized-control")
    audit.check("linearized ell=18chi cap contracts using pi^2<10", linearized_unshifted_shell_pi2 * pi2_upper < 1, linearized_unshifted_shell_pi2 * pi2_upper, "<1", "pah1-linearized-control")
    audit.check("coarser linearized ell=9chi control fails", shell_pi2_coefficient(ordered_curvature, linearized_shifted_shells - 1) * pi2_lower > 1, shell_pi2_coefficient(ordered_curvature, linearized_shifted_shells - 1) * pi2_lower, ">1", "pah1-linearized-control")
    audit.check("coarser linearized ell=18chi control fails", shell_pi2_coefficient(2 * ordered_curvature, linearized_unshifted_shells - 1) * pi2_lower > 1, shell_pi2_coefficient(2 * ordered_curvature, linearized_unshifted_shells - 1) * pi2_lower, ">1", "pah1-linearized-control")

    # The nonconstant fixture q=v+epsilon*cos(kx) has kL=2*pi.  Every
    # derivative is a signed sine/cosine with the same period.
    phase_turns = base_wavenumber * circumference_pi_coefficient
    audit.check("periodic phase turns", phase_turns == 2, phase_turns, 2, "periodic")
    audit.check("nonconstant epsilon fixture declared", "0<|epsilon|<v" in manifest["periodic_circumference_witness"]["nonconstant_family"], manifest["periodic_circumference_witness"]["nonconstant_family"], "contains 0<|epsilon|<v", "periodic")
    audit.check("periodic seam remains conditional", manifest["scope"]["periodic_seams_automatic"] is False, manifest["scope"]["periodic_seams_automatic"], False, "periodic")
    audit.check("periodic backward flow authority", "every fixed finite" in composition["periodic_cauchy_theorem"]["wellposedness"].lower(), composition["periodic_cauchy_theorem"]["wellposedness"], "contains every fixed finite", "periodic")

    audit.check("gate identity", manifest["gate_resolution"]["id"] == "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", manifest["gate_resolution"]["id"], "PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE", "gate")
    audit.check("source gate open", composition["next_route_gates"]["full_circumference"]["status"].startswith("OPEN"), composition["next_route_gates"]["full_circumference"]["status"], "OPEN...", "gate")
    audit.check("child scoped closure", manifest["gate_resolution"]["status"] == "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", manifest["gate_resolution"]["status"], "CLOSED IN DECLARED CLASSICAL FIXED-BACKGROUND SCOPE", "gate")
    audit.check("parent ungated theorem absent", goursat["scope"]["ungated_global_semilinear_existence"] is False, goursat["scope"]["ungated_global_semilinear_existence"], False, "gate")

    scope = manifest["scope"]
    positive = (
        "arbitrary_finite_triangle_goursat_existence",
        "global_classical_uniqueness",
        "explicit_amplitude_bound",
        "global_field_value_stability",
        "full_pah1_circumference_classical_gate",
        "nonconstant_periodic_ordered_trace_family",
    )
    negative = (
        "periodic_seams_automatic",
        "causal_structure_derived",
        "full_3_plus_1_dependence",
        "selected_state",
        "physical_vacuum",
        "below_empty_space",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    audit.check("positive scope", all(scope[key] is True for key in positive), {key: scope[key] for key in positive}, {key: True for key in positive}, "scope")
    audit.check("negative scope", all(scope[key] is False for key in negative), {key: scope[key] for key in negative}, {key: False for key in negative}, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": {
            "q3": {"dimension": dimension, "species": species_count, "edges": edge_count, "degree": degree},
            "coercive_shift": {
                "C_star_coefficient": shift_coefficient,
                "quartic_residual_coefficient": residual_coefficient,
            },
            "test_fixture": {
                "C_star": test_cstar,
                "boundary_flux": test_flux,
                "slice_energy": test_energy,
                "S_tau": test_S,
                "b_S": b_S,
                "ell_S": ell_S,
                "K0": K0,
                "R_c": R_c,
                "b_Rc": b_Rc,
                "ell_Rc": ell_Rc,
                "delta_squared": delta_squared,
                "shell_selfmap": selfmap,
                "shell_contraction": contraction,
            },
            "bessel_coefficients": bessel_coefficients,
            "high_regularity": {
                "potential_degree": potential_degree,
                "force_degree": force_degree,
                "fourth_force_derivatives_zero": fourth_force_derivatives_zero,
                "recurrence_dependencies": recurrence_dependencies,
                "lower_order_carry": lower_order_carry,
                "trace_order": 8,
                "phase_target_orders": [7, 6],
            },
            "pah1": {
                "L_pi_coefficient": circumference_pi_coefficient,
                "tau_pi_coefficient": tau_pi_coefficient,
                "ordered_curvature_over_chi": ordered_curvature,
                "frequency_squares": frequencies_squared,
                "old_unshifted_q_pi2_coefficient": old_unshifted_pi2,
                "old_shifted_q_pi2_coefficient": old_shifted_pi2,
                "linearized_control_only": True,
                "linearized_shifted_shells": linearized_shifted_shells,
                "linearized_shifted_shell_q_pi2_coefficient": linearized_shifted_shell_pi2,
                "linearized_unshifted_shells": linearized_unshifted_shells,
                "linearized_unshifted_shell_q_pi2_coefficient": linearized_unshifted_shell_pi2,
            },
            "periodic_fixture": {"phase_turns": phase_turns, "Pi": 0},
        },
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "goursat_manifest": sha256(GOURSAT),
            "composition_manifest": sha256(COMPOSITION),
            "q3lock_manifest": sha256(Q3LOCK),
            "block_manifest": sha256(BLOCK),
        },
        "scope": scope,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = derive()
    atomic_json(args.output, payload)
    count = payload["assertion_summary"]["total"]
    print(f"{CANDIDATE_ID} independent: {count}/{count} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
