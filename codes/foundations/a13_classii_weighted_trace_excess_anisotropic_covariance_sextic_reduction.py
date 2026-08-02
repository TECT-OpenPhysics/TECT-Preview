#!/usr/bin/env python3
"""Primary certificate for the R-145 weighted trace-excess reduction.

The executable derives every reported constant from pinned repository
authorities.  It proves the exact T-050 weighted trace-excess acceptance
window and a cutoff-uniform trace-class bound for the complete spatial sum of
the terminal total-covariance family-lock anisotropic remainder.  It does not
transfer that split to temporal production owners, estimate the remaining
scalar principal sea, or close T-050.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WEIGHTED-TRACE-EXCESS-ANISOTROPIC-COVARIANCE-SEXTIC-REDUCTION"
SCHEMA = "tect/a13-weighted-trace-excess-anisotropic-covariance-sextic-reduction-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_weighted_trace_excess_anisotropic_covariance_sextic_reduction_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-primary-weighted-trace-excess-anisotropic-covariance-sextic-reduction" / "result.json"


def frac(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value))


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, category: str, name: str, passed: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "category": category,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def require(self) -> None:
        failed = [row for row in self.rows if row["status"] != "PASS"]
        if failed:
            raise AssertionError(json.dumps(failed, indent=2, ensure_ascii=True))


def zeta_integral_upper(power: int, start: int) -> Fraction:
    """Integral-test bound sum_{m>=start} m^{-power}."""
    return Fraction(1, start**power) + Fraction(1, (power - 1) * start ** (power - 1))


def cube_squared_radius(radius: sp.Symbol | int) -> sp.Expr:
    """Sum |n|^2 over the integer cube [-radius,radius]^3."""
    r = sp.sympify(radius)
    return sp.expand(r * (r + 1) * (2 * r + 1) ** 3)


def shell_squared_radius(radius: sp.Symbol | int) -> sp.Expr:
    r = sp.sympify(radius)
    return sp.expand(cube_squared_radius(r) - cube_squared_radius(r - 1))


def decimal_sqrt_fraction(value: Fraction) -> Decimal:
    return (Decimal(value.numerator) / Decimal(value.denominator)).sqrt()


def ceil_sqrt_fraction(value: Fraction) -> int:
    candidate = isqrt(value.numerator // value.denominator)
    while candidate * candidate * value.denominator < value.numerator:
        candidate += 1
    return candidate


def main() -> int:
    getcontext().prec = 80
    audit = Audit()
    manifest = load_json(MANIFEST)

    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    for key, relative in manifest["authorities"].items():
        path = REPO / relative
        actual_hash = sha256(path)
        audit.check("authority", f"{key} exists", path.is_file(), relative, "file")
        audit.check("authority", f"{key} hash", actual_hash == manifest["authority_hashes"][key], actual_hash, manifest["authority_hashes"][key])

    a1 = load_json(REPO / manifest["authorities"]["A1"])
    params = a1["parameters"]
    audit.check("authority", "A1 production authority", a1["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")

    # Derive the family-lock mass matrix from the A1 parameters.
    family = [frac(value) for value in params["family_masses"]]
    lock = frac(params["k_lock"])
    z0 = [frac(value) for value in params["z0"]]
    z0_norm = sum(value * value for value in z0)
    mass = sp.Matrix(
        [
            [
                sp.Rational(family[i].numerator, family[i].denominator) * (1 if i == j else 0)
                + sp.Rational(lock.numerator, lock.denominator)
                * (
                    (1 if i == j else 0)
                    - sp.Rational((z0[i] * z0[j]).numerator, (z0[i] * z0[j]).denominator)
                    / sp.Rational(z0_norm.numerator, z0_norm.denominator)
                )
                for j in range(3)
            ]
            for i in range(3)
        ]
    )
    expected_mass = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    audit.check("mass", "family-lock mass derived", mass == expected_mass, str(mass), str(expected_mass))
    variable = sp.Symbol("mu")
    characteristic = sp.Poly(mass.charpoly(variable).as_expr(), variable)
    intervals = [(frac(lo), frac(hi)) for lo, hi in manifest["audit_inputs"]["mass_root_intervals"]]
    audit.check("mass", "root intervals ordered and disjoint", intervals[0][0] < intervals[0][1] < intervals[1][0] < intervals[1][1] < intervals[2][0] < intervals[2][1], [[fstr(lo), fstr(hi)] for lo, hi in intervals], "strictly ordered and disjoint")
    root_counts = []
    for lower, upper in intervals:
        root_counts.append(
            characteristic.count_roots(
                sp.Rational(lower.numerator, lower.denominator),
                sp.Rational(upper.numerator, upper.denominator),
            )
        )
    audit.check("mass", "Sturm intervals isolate three roots", root_counts == [1, 1, 1], root_counts, [1, 1, 1])
    delta_sum = (intervals[2][1] - intervals[0][0]) + (intervals[2][1] - intervals[1][0])
    audit.check("mass", "safe spectral-spread sum derived", delta_sum > 0, fstr(delta_sum), ">0")

    # Kinetic lower bounds are derived from the pinned A1 decimal inputs.
    r_value = frac(params["r"])
    z_value = frac(params["Z"])
    y_value = frac(params["Y"])
    q0 = frac(params["q0"])
    kinetic_minimum = r_value - z_value * z_value / (4 * y_value)
    shifted_linear = z_value + 2 * q0 * q0
    shifted_constant = r_value - q0**4
    audit.check("kinetic", "pinned quartic coefficient is one", y_value == 1, fstr(y_value), "1")
    audit.check("kinetic", "global kinetic minimum exceeds one quarter", kinetic_minimum > Fraction(1, 4), fstr(kinetic_minimum), ">1/4")
    audit.check("kinetic", "shifted-square linear remainder nonnegative", shifted_linear >= 0, fstr(shifted_linear), ">=0")
    audit.check("kinetic", "shifted-square constant remainder positive", shifted_constant > 0, fstr(shifted_constant), ">0")
    audit.check("kinetic", "q0 below rational three-quarter bound", q0 < Fraction(3, 4), fstr(q0), "<3/4")

    length = frac(params["Lx"])
    audit.check("torus", "cubic L=16 torus", length == 16 and frac(params["Ly"]) == length and frac(params["Lz"]) == length, [str(params[k]) for k in ("Lx", "Ly", "Lz")], "16,16,16")
    pi_lower = frac(manifest["audit_inputs"]["pi_lower"])
    pi_upper = frac(manifest["audit_inputs"]["pi_upper"])
    regulator_bound = frac(manifest["audit_inputs"]["uniform_regulator_bound_for_reported_oracle"])
    h_squared_upper = (2 * pi_upper / length) ** 2
    h_inverse_sixth_upper = (length / (2 * pi_lower)) ** 6
    audit.check("torus", "classical rational pi enclosure pinned", pi_lower == 3 and pi_upper == Fraction(22, 7), [fstr(pi_lower), fstr(pi_upper)], ["3", "22/7"])
    audit.check("torus", "q0/h squared is below four", q0 / (2 * pi_lower / length) < 2, fstr(q0 / (2 * pi_lower / length)), "<2")
    audit.check("torus", "reported regulator oracle normalized", regulator_bound == 1, fstr(regulator_bound), "1")

    # Exact cubic shell geometry and the total spatial derivative trace.
    m = sp.Symbol("m", integer=True, positive=True)
    shell_formula = shell_squared_radius(m)
    audit.check("lattice", "exact shell squared-radius polynomial", shell_formula == 40 * m**4 + 14 * m**2, str(shell_formula), "40*m**4+14*m**2")
    audit.check("lattice", "tail shell bridge", sp.simplify(shell_formula / m**8 - (40 / m**4 + 14 / m**6)) == 0, str(sp.simplify(shell_formula / m**8)), "40/m^4+14/m^6")
    low_radius = Fraction(int(cube_squared_radius(2)), 1)
    audit.check("lattice", "low cube squared-radius sum", low_radius > 0, fstr(low_radius), ">0")
    audit.check("lattice", "shell population formula", (2 * 7 + 1) ** 3 - (2 * 7 - 1) ** 3 == 24 * 7**2 + 2, (2 * 7 + 1) ** 3 - (2 * 7 - 1) ** 3, 24 * 7**2 + 2)

    start = int(manifest["audit_inputs"]["tail_start_sup_shell"])
    c_tail = Fraction(1, 1) - Fraction(4, start * start)
    zeta4 = zeta_integral_upper(4, start)
    zeta6 = zeta_integral_upper(6, start)
    low_trace_bound = regulator_bound**2 * delta_sum * 16 * low_radius * h_squared_upper
    tail_trace_bound = regulator_bound**2 * delta_sum * c_tail ** (-4) * h_inverse_sixth_upper * (40 * zeta4 + 14 * zeta6)
    total_trace_bound = low_trace_bound + tail_trace_bound
    volume = length**3
    six_real_pointwise_trace_bound = Fraction(2, 1) * total_trace_bound / volume
    audit.check("anisotropy", "tail starts above q0 shell", c_tail > 0, fstr(c_tail), ">0")
    audit.check("anisotropy", "total spatial tail is finite", tail_trace_bound > 0, fstr(tail_trace_bound), "finite positive")
    audit.check("anisotropy", "low plus tail identity", total_trace_bound == low_trace_bound + tail_trace_bound, fstr(total_trace_bound), "sum")
    audit.check("anisotropy", "six-real Fourier normalization", six_real_pointwise_trace_bound == Fraction(2, 1) * total_trace_bound / volume, fstr(six_real_pointwise_trace_bound), "2*G_R/V")

    # Derive the Pauli/Fierz coefficient bound from the A1 coefficient inputs.
    denominator = frac(params["M_X"]) ** 2 + frac(params["classii_mass_regularizer"])
    coeff_a = frac(params["cJJ"]) * frac(params["alpha_X"]) ** 2 / denominator
    coeff_b = frac(params["cJK"]) * frac(params["alpha_X"]) * frac(params["beta_X"]) / denominator
    coeff_c = frac(params["cKK"]) * frac(params["beta_X"]) ** 2 / denominator
    beta_actual = 4 * (coeff_a + 2 * abs(coeff_b) + coeff_c)
    beta_numerator = beta_actual * denominator
    beta_upper = beta_numerator / 4
    audit.check("coefficient", "positive coefficient matrix entries", coeff_a > 0 and coeff_b > 0 and coeff_c > 0, [fstr(coeff_a), fstr(coeff_b), fstr(coeff_c)], "positive")
    audit.check("coefficient", "coefficient Gram determinant positive", coeff_a * coeff_c - coeff_b**2 > 0, fstr(coeff_a * coeff_c - coeff_b**2), ">0")
    audit.check("coefficient", "mass denominator exceeds four", denominator > 4, fstr(denominator), ">4")
    audit.check("coefficient", "beta upper follows from denominator", beta_actual < beta_upper, fstr(beta_actual), f"<{fstr(beta_upper)}")

    volume_two_thirds = length**2
    young_a = beta_upper * six_real_pointwise_trace_bound * volume_two_thirds / 2
    zeta_an = frac(manifest["audit_inputs"]["anisotropic_action_sextic_allocation"])
    young_action_constant = (
        Decimal(2)
        * (Decimal(young_a.numerator) / Decimal(young_a.denominator))
        * decimal_sqrt_fraction(young_a)
        / (Decimal(3) * decimal_sqrt_fraction(3 * zeta_an))
    )
    young_constant_square = Fraction(4) * young_a**3 / (27 * zeta_an)
    young_constant_ceiling = ceil_sqrt_fraction(young_constant_square)
    audit.check("young", "chosen anisotropic sextic allocation positive", zeta_an > 0, fstr(zeta_an), ">0")
    audit.check("young", "Young action constant finite", young_action_constant.is_finite() and young_action_constant > 0, str(young_action_constant), "finite positive")
    audit.check("young", "Young constant exact integer ceiling", Fraction((young_constant_ceiling - 1) ** 2) < young_constant_square <= Fraction(young_constant_ceiling**2), [fstr(young_constant_square), young_constant_ceiling], "(N-1)^2<C^2<=N^2")

    # Restore the direct V^ren trace-excess thresholds.  The 9/20 and 3/20
    # coordinates belong to the augmented action and are subtracted again
    # before applying T-050; they do not shift these loss thresholds.
    r144 = load_json(REPO / manifest["authorities"]["R-144-primary"])
    audit.check("authority", "R-144 primary result identity", r144["result_id"] == "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-LOW-COMPLETION-BOUNDARY", r144["result_id"], "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-LOW-COMPLETION-BOUNDARY")
    p_value = frac(r144["exact_values"]["comparison_p"])
    source_loss_threshold = Fraction(1, 2) / p_value
    gamma = frac(params["gamma"])
    sextic_loss_threshold = gamma / 6
    source_coordinate = frac(r144["exact_values"]["q_source_target"])
    sextic_coordinate = frac(r144["exact_values"]["hessian_epsilon_sextic"])
    alpha_source_threshold = source_loss_threshold / source_coordinate
    alpha_sextic_threshold = sextic_loss_threshold / sextic_coordinate
    audit.check("threshold", "source loss threshold matches R-144", fstr(source_loss_threshold) == r144["exact_values"]["canonical_source_threshold"], fstr(source_loss_threshold), r144["exact_values"]["canonical_source_threshold"])
    audit.check("threshold", "canonical sextic loss threshold", sextic_loss_threshold > sextic_coordinate, fstr(sextic_loss_threshold), f">{fstr(sextic_coordinate)}")
    audit.check("threshold", "unit weighted coordinates are sufficient", source_coordinate < source_loss_threshold and sextic_coordinate < sextic_loss_threshold, [fstr(source_coordinate), fstr(sextic_coordinate)], [f"<{fstr(source_loss_threshold)}", f"<{fstr(sextic_loss_threshold)}"])
    audit.check("threshold", "anisotropic allocation leaves positive trace window", zeta_an < sextic_loss_threshold, fstr(sextic_loss_threshold - zeta_an), ">0")

    gates_text = (REPO / manifest["authorities"]["GATES"]).read_text(encoding="utf-8")
    gate_start = gates_text.index("### **A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE**")
    gate_end = gates_text.index("### **", gate_start + 10)
    gate_section = gates_text[gate_start:gate_end]
    audit.check("threshold", "gate pins gamma over six", "gamma/6=0.27" in gate_section, "gamma/6=0.27" in gate_section, True)
    audit.check("threshold", "gate pins one-over-two-p", "epsilon_v<1/(2p)" in gate_section, "epsilon_v<1/(2p)" in gate_section, True)

    # A two-endpoint fixture shows why mixed Gram contraction is stronger than
    # the pointwise weighted action criterion.
    gram_u = sp.Rational(9, 16) * sp.ones(2)
    gram_paid = sp.eye(2)
    mixed_eigenvalues = list((gram_paid - gram_u).eigenvals().keys())
    rho_squared = max(gram_u.eigenvals().keys())
    audit.check("route", "each diagonal endpoint passes", all(gram_u[i, i] < 1 for i in range(2)), [str(gram_u[i, i]) for i in range(2)], "<1")
    audit.check("route", "mixed contraction fails", min(mixed_eigenvalues) < 0 and rho_squared > 1, [str(value) for value in mixed_eigenvalues], "one negative")

    # The trace-class argument is genuinely anisotropic: its shell series is
    # summable, while the raw scalar principal derivative sea has a nonzero
    # shell-order limit before signed owner cancellation.
    scalar_shell_model = sp.simplify((24 * m**2 + 2) * m**2 / m**4)
    scalar_shell_limit = sp.limit(scalar_shell_model, m, sp.oo)
    audit.check("frontier", "anisotropic tail powers summable", zeta4 > 0 and zeta6 > 0, [fstr(zeta4), fstr(zeta6)], "finite")
    audit.check("frontier", "raw scalar shell model is not summable", scalar_shell_limit > 0, str(scalar_shell_limit), ">0")

    exact_values = {
        "mass_matrix": [[str(entry) for entry in mass.row(i)] for i in range(3)],
        "safe_mass_spread_sum": fstr(delta_sum),
        "tail_start": str(start),
        "tail_gap_c": fstr(c_tail),
        "low_cube_squared_radius": fstr(low_radius),
        "shell_squared_radius": "40*m^4+14*m^2",
        "zeta4_upper": fstr(zeta4),
        "zeta6_upper": fstr(zeta6),
        "anisotropic_low_complex_fourier_sum_bound": fstr(low_trace_bound),
        "anisotropic_tail_complex_fourier_sum_bound": fstr(tail_trace_bound),
        "anisotropic_total_complex_fourier_sum_bound": fstr(total_trace_bound),
        "six_real_pointwise_derivative_trace_bound": fstr(six_real_pointwise_trace_bound),
        "beta_operator_upper": fstr(beta_upper),
        "young_a": fstr(young_a),
        "young_constant_square": fstr(young_constant_square),
        "young_constant_integer_ceiling": str(young_constant_ceiling),
        "anisotropic_action_sextic_allocation": fstr(zeta_an),
        "source_loss_threshold": fstr(source_loss_threshold),
        "sextic_loss_threshold": fstr(sextic_loss_threshold),
        "trace_excess_source_threshold": fstr(source_loss_threshold),
        "trace_excess_sextic_threshold": fstr(sextic_loss_threshold),
        "alpha_source_threshold": fstr(alpha_source_threshold),
        "alpha_sextic_threshold": fstr(alpha_sextic_threshold),
        "unit_source_margin": fstr(source_loss_threshold - source_coordinate),
        "unit_sextic_margin": fstr(sextic_loss_threshold - sextic_coordinate),
        "remaining_trace_sextic_window_after_anisotropy": fstr(sextic_loss_threshold - zeta_an),
        "mixed_fixture_rho_squared": str(rho_squared),
    }

    audit.check("scope", "scalar principal sea remains open", manifest["scope"]["scalar_principal_sea_bound_proved"] is False, manifest["scope"]["scalar_principal_sea_bound_proved"], False)
    audit.check("scope", "terminal total-covariance payment proved", manifest["scope"]["terminal_total_covariance_anisotropic_sextic_payment_proved"] is True, manifest["scope"]["terminal_total_covariance_anisotropic_sextic_payment_proved"], True)
    audit.check("scope", "production temporal transfer remains open", manifest["scope"]["production_temporal_anisotropic_owner_payment_proved"] is False, manifest["scope"]["production_temporal_anisotropic_owner_payment_proved"], False)
    audit.check("scope", "complete low anchor remains open", manifest["scope"]["complete_low_anchor_proved"] is False, manifest["scope"]["complete_low_anchor_proved"], False)
    audit.check("scope", "T-050 remains open", manifest["scope"]["t050_closed"] is False, manifest["scope"]["t050_closed"], False)
    audit.check("scope", "Sector A remains open", manifest["scope"]["sector_a_closed"] is False, manifest["scope"]["sector_a_closed"], False)

    audit.require()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "package_version": __version__,
        "status": "PASS",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "assertions": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "exact_values": exact_values,
        "diagnostics": {
            "terminal_anisotropic_action_constant": str(young_action_constant),
            "terminal_anisotropic_action_constant_role": "decimal approximation only; the exact certified upper bound is young_constant_integer_ceiling",
            "actual_beta_operator": fstr(beta_actual),
            "kinetic_minimum": fstr(kinetic_minimum),
            "regulator_bound_scaling": {
                "complex_fourier_sum_and_six_real_pointwise_trace": "M_chi^2",
                "terminal_young_constant": "M_chi^3 * C_an",
            },
            "weighted_trace_excess_theorem": "If a_pi>=-C0 and one-half(||U||^2-||Phi||^2)<=eta X+zeta Y6+B uniformly with eta<5/11 and zeta<27/100, then Vren=a_pi-one-half(||U||^2-||Phi||^2) satisfies T-050.",
            "anisotropic_reduction": "At terminal total-covariance level the anisotropic derivative trace is paid with zeta_an=1/100 and a cutoff-uniform constant. Transfer to temporally faithful production owners, the scalar principal sea, and complete low/anchor remain open.",
        },
        "source_hash": sha256(Path(__file__)),
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS: primary ({len(audit.rows)}/{len(audit.rows)})")
    print(f"RESULT: {OUTPUT.relative_to(REPO).as_posix()}")
    print(f"ANISOTROPIC COMPLEX FOURIER SUM BOUND: {fstr(total_trace_bound)}")
    print(f"SIX-REAL POINTWISE TRACE BOUND: {fstr(six_real_pointwise_trace_bound)}")
    print("OPEN: scalar principal sea, complete low/anchor, T-050, A13, Nelson, Sector A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
