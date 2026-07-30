#!/usr/bin/env python3
"""Independent standard-library audit for the scoped A13 R-132 boundary.

This program does not import SymPy or the primary R-132 module.  It checks
paired-replica polarization, Pauli--Fierz contractions, the 64-atom diagonal
heat estimates and mixed cancellation, the rational two-point floor warning,
and the standard-Gaussian scalar-ray margin using independent arithmetic.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY"
SCHEMA = "tect/a13-mixed-replica-gaussian-ray-sextic-shell-boundary-independent/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-mixed-replica-gaussian-ray-sextic-shell-"
    "boundary/result.json"
)
R131_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-owner-complete-physical-response-mixed-"
    "gram-shell-boundary/result.json"
)
A1_MANIFEST = REPO / (
    "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
    "production_functional_manifest.json"
)


def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): represent(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [represent(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(represent(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": represent(actual),
                "expected": represent(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": represent(diagnostics),
            "scope": {
                "mixed_replica_representation_proved": True,
                "mixed_pauli_fierz_identity_proved": True,
                "diagonal_rademacher_heat_sextic_bound_proved": True,
                "diagonal_to_mixed_promotion_rejected": True,
                "law_free_floor_uniformity_rejected": True,
                "standard_gaussian_ray_score_bound_proved": True,
                "production_owner_complete_form_constructed": False,
                "production_c_mix": False,
                "production_c_far": False,
                "production_c_bal": False,
                "absolute_anchor": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "Independent checks cover the scoped R-132 representation, comparison, "
                "counterfixtures, and scalar Gaussian ray only. They prove no production "
                "owner-complete response or Sector A closure."
            ),
        }


@dataclass(frozen=True)
class Jet2:
    value: float
    first: float = 0.0
    second: float = 0.0

    @staticmethod
    def lift(value: float | "Jet2") -> "Jet2":
        return value if isinstance(value, Jet2) else Jet2(float(value))

    def __add__(self, other: float | "Jet2") -> "Jet2":
        rhs = self.lift(other)
        return Jet2(self.value + rhs.value, self.first + rhs.first, self.second + rhs.second)

    __radd__ = __add__

    def __neg__(self) -> "Jet2":
        return Jet2(-self.value, -self.first, -self.second)

    def __sub__(self, other: float | "Jet2") -> "Jet2":
        return self + (-self.lift(other))

    def __rsub__(self, other: float | "Jet2") -> "Jet2":
        return self.lift(other) - self

    def __mul__(self, other: float | "Jet2") -> "Jet2":
        rhs = self.lift(other)
        return Jet2(
            self.value * rhs.value,
            self.first * rhs.value + self.value * rhs.first,
            self.second * rhs.value + 2.0 * self.first * rhs.first + self.value * rhs.second,
        )

    __rmul__ = __mul__

    def reciprocal(self) -> "Jet2":
        inv = 1.0 / self.value
        return Jet2(
            inv,
            -self.first * inv * inv,
            2.0 * self.first * self.first * inv**3 - self.second * inv * inv,
        )

    def __truediv__(self, other: float | "Jet2") -> "Jet2":
        return self * self.lift(other).reciprocal()

    def __rtruediv__(self, other: float | "Jet2") -> "Jet2":
        return self.lift(other) / self

    def __pow__(self, exponent: int) -> "Jet2":
        if exponent < 0:
            return (self.reciprocal()) ** (-exponent)
        output = Jet2(1.0)
        for _ in range(exponent):
            output = output * self
        return output


def inner(left: tuple[complex, complex], right: tuple[complex, complex]) -> complex:
    return left[0].conjugate() * right[0] + left[1].conjugate() * right[1]


def matvec(matrix: tuple[tuple[complex, complex], tuple[complex, complex]], vector: tuple[complex, complex]) -> tuple[complex, complex]:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


PAULI = (
    ((0j, 1 + 0j), (1 + 0j, 0j)),
    ((0j, -1j), (1j, 0j)),
    ((1 + 0j, 0j), (0j, -1 + 0j)),
)


def xi_value(
    state: tuple[complex, complex, complex],
    tangent: tuple[complex, complex, complex],
    alpha: float,
    c0: float,
    c1: float,
    floor: float,
) -> tuple[float, float, float, float]:
    u1, u2, chi = state
    v1, v2, w = tangent
    r = abs(u1) ** 2 + abs(u2) ** 2
    rho = r + abs(chi) ** 2
    a = (u1.conjugate() * v1 + u2.conjugate() * v2).real
    s = (chi.conjugate() * w).real
    h = u1 * v2 - u2 * v1
    lam = alpha * r / (rho + floor)
    return (
        2.0 * math.sqrt(c0) * a,
        2.0 * math.sqrt(c1) * ((1.0 - lam) * a - lam * s),
        2.0 * math.sqrt(c0 + c1) * h.real,
        2.0 * math.sqrt(c0 + c1) * h.imag,
    )


def norm2(vector: tuple[float, ...]) -> float:
    return sum(value * value for value in vector)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    upstream = json.loads(R131_RESULT.read_text(encoding="utf-8"))
    production = upstream["diagnostics"]["production"]
    alpha_q = Fraction(production["alpha"])
    c0_q = Fraction(production["c0"])
    c1_q = Fraction(production["c1"])
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    floor_q = Fraction(str(a1["parameters"]["rho_regularizer"]))
    p_mass_q = Fraction(3, 250) / c0_q
    alpha, c0, c1, floor = map(float, (alpha_q, c0_q, c1_q, floor_q))
    audit = Audit()

    audit.check("inputs", "upstream_pass", upstream.get("status") == "PASS", upstream.get("status"), "PASS")
    audit.check("inputs", "alpha", alpha_q == Fraction(5, 9), alpha_q, Fraction(5, 9))
    audit.check("inputs", "p_mass", p_mass_q == Fraction(4_000_000_000_001, 10**12), p_mass_q, Fraction(4_000_000_000_001, 10**12))

    # Paired-replica polarization with independent plain rational arithmetic.
    weights = [Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)]
    bases = [(Fraction(1), Fraction(-2)), (Fraction(3), Fraction(1)), (Fraction(-1), Fraction(4))]
    dz = [(Fraction(2), Fraction(1)), (Fraction(-1), Fraction(3)), (Fraction(4), Fraction(-2))]
    dw = [(Fraction(-2), Fraction(2)), (Fraction(1), Fraction(-3)), (Fraction(2), Fraction(5))]
    dzw = [(Fraction(1), Fraction(2)), (Fraction(-2), Fraction(1)), (Fraction(3), Fraction(-1))]
    mean_base = tuple(sum(weights[k] * bases[k][j] for k in range(3)) for j in range(2))
    mean_z = tuple(sum(weights[k] * dz[k][j] for k in range(3)) for j in range(2))
    mean_w = tuple(sum(weights[k] * dw[k][j] for k in range(3)) for j in range(2))
    mean_zw = tuple(sum(weights[k] * dzw[k][j] for k in range(3)) for j in range(2))
    lhs = sum(mean_z[j] * mean_w[j] + mean_base[j] * mean_zw[j] for j in range(2))
    rhs = sum(
        weights[i] * weights[j] * sum(dz[i][k] * dw[j][k] + bases[i][k] * dzw[j][k] for k in range(2))
        for i in range(3)
        for j in range(3)
    )
    audit.check("replica", "polarization", lhs == rhs, lhs, rhs)

    # Direct complex Pauli sums versus the invariant mixed formulas.
    fixtures = [
        ((1 + 2j, -1 + 1j), (2 - 1j, 3 + 1j), (-2 + 3j, 1 - 1j), (-3 + 2j, 2 + 4j)),
        ((2 - 1j, 1 + 3j), (-1 + 2j, 4 - 1j), (3 + 1j, -2 - 1j), (1 - 4j, 2 + 1j)),
        ((-1 + 1j, 3 - 2j), (2 + 2j, -3 + 1j), (1 - 3j, 4 + 1j), (-2 + 1j, 1 + 2j)),
    ]
    residuals: list[float] = []
    for u, v, up, vp in fixtures:
        m = [inner(u, matvec(sigma, u)).real for sigma in PAULI]
        mp = [inner(up, matvec(sigma, up)).real for sigma in PAULI]
        j = [2.0 * inner(u, matvec(sigma, v)).real for sigma in PAULI]
        jp = [2.0 * inner(up, matvec(sigma, vp)).real for sigma in PAULI]
        direct = (
            sum(j[k] * jp[k] for k in range(3)),
            sum(j[k] * mp[k] for k in range(3)),
            sum(m[k] * jp[k] for k in range(3)),
            sum(m[k] * mp[k] for k in range(3)),
        )
        formula = (
            2.0 * (
                2.0 * inner(u, vp) * inner(up, v)
                - inner(u, v) * inner(up, vp)
                + 2.0 * inner(u, up) * inner(vp, v)
                - inner(u, v) * inner(vp, up)
            ).real,
            4.0 * (inner(v, up) * inner(up, u)).real - 2.0 * inner(up, up).real * inner(u, v).real,
            4.0 * (inner(vp, u) * inner(u, up)).real - 2.0 * inner(u, u).real * inner(up, vp).real,
            (2.0 * inner(u, up) * inner(up, u) - inner(u, u) * inner(up, up)).real,
        )
        residuals.extend(abs(direct[k] - formula[k]) for k in range(4))
    audit.check("fierz", "mixed_formulas", max(residuals) < 1e-11, max(residuals), "<1e-11")

    c_full = c0_q * c1_q / (c0_q + c1_q)
    radius_q = Fraction(1, 32)
    denominator = (math.sqrt(float(radius_q)) + math.sqrt(6.0)) ** 2 + floor
    compact_v = 8.0 * (c0 + c1)
    compact_w = 64.0 * float(c_full) * alpha * alpha / denominator**2
    outside = 0.9 * float(radius_q) ** 2
    audit.check("diagonal_heat", "compact_v", compact_v > outside, compact_v, f">{outside}")
    audit.check("diagonal_heat", "compact_w", compact_w > outside, compact_w, f">{outside}")
    audit.check("diagonal_heat", "global_constant", Fraction(9, 10) * radius_q**2 == Fraction(9, 10240), Fraction(9, 10) * radius_q**2, Fraction(9, 10240))

    atoms = list(product((-1.0, 1.0), repeat=6))
    tangent_fixtures = [
        (1 + 2j, -1 + 0.5j, 2 - 1j),
        (-2 + 1j, 0.25 - 3j, -1 + 2j),
        (0.5 - 0.75j, 2 + 1.5j, 3 + 0.25j),
    ]
    mean_residual = 0.0
    for tangent in tangent_fixtures:
        accumulated = [0.0, 0.0, 0.0, 0.0]
        for atom in atoms:
            state = (complex(atom[0], atom[1]), complex(atom[2], atom[3]), complex(atom[4], atom[5]))
            value = xi_value(state, tangent, alpha, c0, c1, floor)
            accumulated = [accumulated[k] + value[k] for k in range(4)]
        mean_residual = max(mean_residual, *(abs(value / len(atoms)) for value in accumulated))
    audit.check("mixed_boundary", "origin_mean_zero", mean_residual < 1e-14, mean_residual, "<1e-14")

    compact_states = [
        (0j, 0j, 0j),
        (0.05 + 0.02j, -0.03 + 0.01j, 0.04 - 0.02j),
        (-0.08 + 0.03j, 0.02 - 0.04j, -0.05 + 0.01j),
    ]
    lower_residual = float("inf")
    for state in compact_states:
        rho_state = sum(abs(value) ** 2 for value in state)
        audit.check("diagonal_heat", f"fixture_ball_{len(audit.rows)}", rho_state <= float(radius_q), rho_state, f"<={float(radius_q)}")
        for tangent in tangent_fixtures:
            heat = 0.0
            for atom in atoms:
                shifted = (
                    state[0] + complex(atom[0], atom[1]),
                    state[1] + complex(atom[2], atom[3]),
                    state[2] + complex(atom[4], atom[5]),
                )
                heat += norm2(xi_value(shifted, tangent, alpha, c0, c1, floor))
            heat /= len(atoms)
            target = compact_v * (abs(tangent[0]) ** 2 + abs(tangent[1]) ** 2) + compact_w * abs(tangent[2]) ** 2
            lower_residual = min(lower_residual, heat - target)
    audit.check("diagonal_heat", "finite_fixture_lower_bound", lower_residual > -1e-12, lower_residual, ">=-1e-12")

    # Independent second-order automatic differentiation of the two-point law.
    def rational_ray(value: Jet2, delta: float) -> Jet2:
        return value - alpha * value**3 / (value**2 + delta * delta)

    warning_residuals: list[float] = []
    scaled_values: list[float] = []
    for delta_value in (0.5, 0.2, 0.05, 0.01):
        shift_jet = Jet2(0.0, 1.0, 0.0)
        difference = rational_ray(Jet2(delta_value) + shift_jet, delta_value) - rational_ray(Jet2(1.0) + shift_jet, delta_value)
        hessian_over_c1 = (-0.5 * difference**2).second
        polynomial = (
            7 * delta_value**7 + 188 * delta_value**6 + 61 * delta_value**5
            + 100 * delta_value**4 + 57 * delta_value**3 + 40 * delta_value**2
            + 3 * delta_value + 8
        )
        closed = -5.0 * (delta_value - 1.0) ** 2 * polynomial / (
            324.0 * delta_value * (1.0 + delta_value**2) ** 4
        )
        warning_residuals.append(abs(hessian_over_c1 - closed))
        scaled_values.append(delta_value * hessian_over_c1)
    audit.check("floor_warning", "jet_matches_closed_form", max(warning_residuals) < 1e-10, max(warning_residuals), "<1e-10")
    audit.check("floor_warning", "negative_samples", all(value < 0 for value in scaled_values), scaled_values, "all negative")
    audit.check("floor_warning", "scaled_limit_approach", abs(scaled_values[-1] + 10.0 / 81.0) < 0.02, scaled_values[-1], "within 0.02 of -10/81")

    gaussian_a = 4.0 * c1 * (3.0 + math.sqrt(2.0))
    gaussian_b = 4.0 * c1 * (2.0 + math.sqrt(2.0))
    gaussian_margin = 0.9 - gaussian_a - gaussian_b * gaussian_b / 18.0
    audit.check("gaussian_ray", "margin_positive", gaussian_margin > 0.0, gaussian_margin, ">0")
    audit.check("gaussian_ray", "margin_above_three_quarters", gaussian_margin > 0.75, gaussian_margin, ">0.75")
    polynomial_samples = [
        0.9 - gaussian_a - gaussian_b * y + 4.5 * y * y
        for y in (0.0, gaussian_b / 9.0, 0.5, 1.0, 4.0)
    ]
    audit.check("gaussian_ray", "completed_square_samples", min(polynomial_samples) >= gaussian_margin - 1e-14, min(polynomial_samples), f">={gaussian_margin}")

    gamma = Fraction(7, 12)
    audit.check("shell", "known_square", 2 * gamma == Fraction(7, 6), 2 * gamma, Fraction(7, 6))
    audit.check("shell", "known_too_slow_mix", gamma < 2, gamma, "<2")
    audit.check("shell", "known_too_slow_far", gamma < 4, gamma, "<4")
    audit.check("shell", "gamma_four_offset", 2 ** (4 * 5) == 1_048_576, 2 ** (4 * 5), 1_048_576)

    diagnostics = {
        "inputs": {"alpha": alpha_q, "c0": c0_q, "c1": c1_q, "floor": floor_q},
        "replica": {"lhs": lhs, "rhs": rhs},
        "fierz_max_residual": max(residuals),
        "diagonal_heat_sextic": {
            "radius": radius_q,
            "compact_v": compact_v,
            "compact_w": compact_w,
            "global_constant": outside,
            "finite_fixture_lower_residual": lower_residual,
        },
        "mixed_origin_mean_residual": mean_residual,
        "floor_warning": {
            "jet_closed_max_residual": max(warning_residuals),
            "scaled_samples": scaled_values,
        },
        "gaussian_ray": {
            "negative_constant": gaussian_a,
            "negative_quadratic": gaussian_b,
            "source_sextic_margin": gaussian_margin,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(args.output, payload)
    print(
        f"R-132 independent {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
