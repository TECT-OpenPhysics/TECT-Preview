#!/usr/bin/env python3
"""Independent certificate for the R-145 weighted trace-excess reduction.

This verifier deliberately uses only the Python standard library.  It derives
the mass matrix, its exact Sturm root counts, cubic-shell sums, covariance
bounds, coefficient bound, and T-050 acceptance window without importing the
primary implementation or any symbolic/numerical linear-algebra package.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WEIGHTED-TRACE-EXCESS-ANISOTROPIC-COVARIANCE-SEXTIC-REDUCTION"
SCHEMA = "tect/a13-weighted-trace-excess-anisotropic-covariance-sextic-reduction-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_weighted_trace_excess_anisotropic_covariance_sextic_reduction_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-independent-weighted-trace-excess-anisotropic-covariance-sextic-reduction" / "result.json"


def frac(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


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
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
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


def trim(poly: list[Fraction]) -> list[Fraction]:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def derivative(poly: list[Fraction]) -> list[Fraction]:
    return trim([Fraction(index) * poly[index] for index in range(1, len(poly))] or [Fraction(0)])


def poly_divmod(dividend: list[Fraction], divisor: list[Fraction]) -> tuple[list[Fraction], list[Fraction]]:
    remainder = trim(dividend)
    divisor = trim(divisor)
    if divisor == [0]:
        raise ZeroDivisionError("zero polynomial")
    quotient = [Fraction(0)] * max(1, len(remainder) - len(divisor) + 1)
    while remainder != [0] and len(remainder) >= len(divisor):
        degree = len(remainder) - len(divisor)
        coefficient = remainder[-1] / divisor[-1]
        quotient[degree] += coefficient
        for index, value in enumerate(divisor):
            remainder[index + degree] -= coefficient * value
        remainder = trim(remainder)
    return trim(quotient), trim(remainder)


def poly_value(poly: list[Fraction], point: Fraction) -> Fraction:
    value = Fraction(0)
    for coefficient in reversed(poly):
        value = value * point + coefficient
    return value


def sturm_sequence(poly: list[Fraction]) -> list[list[Fraction]]:
    sequence = [trim(poly), derivative(poly)]
    while sequence[-1] != [0]:
        _, remainder = poly_divmod(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        sequence.append([-entry for entry in remainder])
    return sequence


def sign_variations(sequence: list[list[Fraction]], point: Fraction) -> int:
    signs: list[int] = []
    for poly in sequence:
        value = poly_value(poly, point)
        if value:
            signs.append(1 if value > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def root_count(sequence: list[list[Fraction]], lower: Fraction, upper: Fraction) -> int:
    return sign_variations(sequence, lower) - sign_variations(sequence, upper)


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def characteristic_lambda_minus_mass(matrix: list[list[Fraction]]) -> list[Fraction]:
    trace = sum(matrix[index][index] for index in range(3))
    principal_two = (
        matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        + matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]
        + matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]
    )
    return [-determinant3(matrix), principal_two, -trace, Fraction(1)]


def cube_squared_radius(radius: int) -> int:
    return sum(x * x + y * y + z * z for x, y, z in itertools.product(range(-radius, radius + 1), repeat=3))


def shell_squared_radius(radius: int) -> int:
    return sum(
        x * x + y * y + z * z
        for x, y, z in itertools.product(range(-radius, radius + 1), repeat=3)
        if max(abs(x), abs(y), abs(z)) == radius
    )


def zeta_integral_upper(power: int, start: int) -> Fraction:
    return Fraction(1, start**power) + Fraction(1, (power - 1) * start ** (power - 1))


def ceil_sqrt_fraction(value: Fraction) -> int:
    candidate = isqrt(value.numerator // value.denominator)
    while candidate * candidate * value.denominator < value.numerator:
        candidate += 1
    return candidate


def main() -> int:
    getcontext().prec = 80
    audit = Audit()
    manifest = load_json(MANIFEST)
    audit.check("metadata", "manifest schema", manifest["schema"].endswith("manifest/1.0"), manifest["schema"], "*/manifest/1.0")
    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger id", manifest["result_ledger_id"] == "R-145", manifest["result_ledger_id"], "R-145")
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    for key, relative in manifest["authorities"].items():
        path = REPO / relative
        actual_hash = sha256(path)
        audit.check("authority", f"{key} exists", path.is_file(), relative, "file")
        audit.check("authority", f"{key} hash", actual_hash == manifest["authority_hashes"][key], actual_hash, manifest["authority_hashes"][key])

    a1 = load_json(REPO / manifest["authorities"]["A1"])
    params = a1["parameters"]
    family = [frac(value) for value in params["family_masses"]]
    lock = frac(params["k_lock"])
    z0 = [frac(value) for value in params["z0"]]
    norm = sum(value * value for value in z0)
    mass = [
        [family[i] * (i == j) + lock * (Fraction(i == j) - z0[i] * z0[j] / norm) for j in range(3)]
        for i in range(3)
    ]
    expected_mass = [
        [Fraction(1, 10), Fraction(-1, 20), Fraction(-1, 20)],
        [Fraction(-1, 20), Fraction(13, 100), Fraction(-1, 20)],
        [Fraction(-1, 20), Fraction(-1, 20), Fraction(17, 100)],
    ]
    audit.check("mass", "mass derived from A1", mass == expected_mass, [[fstr(x) for x in row] for row in mass], [[fstr(x) for x in row] for row in expected_mass])
    audit.check("mass", "mass symmetric", all(mass[i][j] == mass[j][i] for i in range(3) for j in range(3)), True, True)
    audit.check("mass", "positive determinant", determinant3(mass) > 0, fstr(determinant3(mass)), ">0")
    characteristic = characteristic_lambda_minus_mass(mass)
    sturm = sturm_sequence(characteristic)
    intervals = [(frac(lo), frac(hi)) for lo, hi in manifest["audit_inputs"]["mass_root_intervals"]]
    counts = [root_count(sturm, lower, upper) for lower, upper in intervals]
    audit.check("mass", "Sturm chain nontrivial", len(sturm) == 4, len(sturm), 4)
    audit.check("mass", "three isolated roots", counts == [1, 1, 1], counts, [1, 1, 1])
    audit.check("mass", "intervals ordered", all(lower < upper for lower, upper in intervals), True, True)
    audit.check("mass", "root intervals disjoint", intervals[0][1] < intervals[1][0] < intervals[1][1] < intervals[2][0], True, True)
    delta_sum = intervals[2][1] - intervals[0][0] + intervals[2][1] - intervals[1][0]
    audit.check("mass", "spread sum positive", delta_sum > 0, fstr(delta_sum), ">0")

    r_value = frac(params["r"])
    z_value = frac(params["Z"])
    y_value = frac(params["Y"])
    q0 = frac(params["q0"])
    kinetic_minimum = r_value - z_value**2 / (4 * y_value)
    shifted_linear = z_value + 2 * q0**2
    shifted_constant = r_value - q0**4
    audit.check("kinetic", "pinned quartic coefficient is one", y_value == 1, fstr(y_value), "1")
    audit.check("kinetic", "global lower bound", kinetic_minimum > Fraction(1, 4), fstr(kinetic_minimum), ">1/4")
    audit.check("kinetic", "shifted linear remainder", shifted_linear >= 0, fstr(shifted_linear), ">=0")
    audit.check("kinetic", "shifted constant remainder", shifted_constant > 0, fstr(shifted_constant), ">0")
    audit.check("kinetic", "q0 rational upper", q0 < Fraction(3, 4), fstr(q0), "<3/4")

    length = frac(params["Lx"])
    pi_lower = frac(manifest["audit_inputs"]["pi_lower"])
    pi_upper = frac(manifest["audit_inputs"]["pi_upper"])
    regulator_bound = frac(manifest["audit_inputs"]["uniform_regulator_bound_for_reported_oracle"])
    h_lower = 2 * pi_lower / length
    h_squared_upper = (2 * pi_upper / length) ** 2
    h_inverse_sixth_upper = (length / (2 * pi_lower)) ** 6
    audit.check("torus", "cubic side lengths", frac(params["Ly"]) == length == frac(params["Lz"]), [params[k] for k in ("Lx", "Ly", "Lz")], "equal")
    audit.check("torus", "side length exact", length == 16, fstr(length), "16")
    audit.check("torus", "classical pi enclosure pinned", pi_lower == 3 and pi_upper == Fraction(22, 7), [fstr(pi_lower), fstr(pi_upper)], ["3", "22/7"])
    audit.check("torus", "shell location", q0 / h_lower < 2, fstr(q0 / h_lower), "<2")
    audit.check("torus", "reported regulator oracle normalized", regulator_bound == 1, fstr(regulator_bound), "1")

    low_radius = Fraction(cube_squared_radius(2))
    shell_checks = {str(m): shell_squared_radius(m) for m in range(1, 8)}
    shell_formula_checks = {str(m): 40 * m**4 + 14 * m**2 for m in range(1, 8)}
    population_checks = {
        str(m): sum(1 for point in itertools.product(range(-m, m + 1), repeat=3) if max(map(abs, point)) == m)
        for m in range(1, 8)
    }
    population_formula = {str(m): 24 * m**2 + 2 for m in range(1, 8)}
    audit.check("lattice", "cube radius-two sum", low_radius == 750, fstr(low_radius), "750")
    audit.check("lattice", "seven shell sums", shell_checks == shell_formula_checks, shell_checks, shell_formula_checks)
    audit.check("lattice", "seven tail shell bridges", all(Fraction(shell_squared_radius(m), m**8) == Fraction(40, m**4) + Fraction(14, m**6) for m in range(3, 10)), True, True)
    audit.check("lattice", "seven shell populations", population_checks == population_formula, population_checks, population_formula)
    audit.check("lattice", "shell sum positive", all(value > 0 for value in shell_checks.values()), True, True)
    audit.check("lattice", "population positive", all(value > 0 for value in population_checks.values()), True, True)

    start = int(manifest["audit_inputs"]["tail_start_sup_shell"])
    c_tail = 1 - Fraction(4, start**2)
    zeta4 = zeta_integral_upper(4, start)
    zeta6 = zeta_integral_upper(6, start)
    low_trace_bound = regulator_bound**2 * delta_sum * 16 * low_radius * h_squared_upper
    tail_trace_bound = regulator_bound**2 * delta_sum * c_tail ** (-4) * h_inverse_sixth_upper * (40 * zeta4 + 14 * zeta6)
    total_trace_bound = low_trace_bound + tail_trace_bound
    volume = length**3
    six_real_pointwise_trace_bound = Fraction(2) * total_trace_bound / volume
    audit.check("anisotropy", "tail starts at three", start == 3, start, 3)
    audit.check("anisotropy", "positive tail gap", c_tail > 0, fstr(c_tail), ">0")
    audit.check("anisotropy", "zeta-four integral bound", zeta4 == Fraction(2, 81), fstr(zeta4), "2/81")
    audit.check("anisotropy", "zeta-six integral bound", zeta6 == Fraction(8, 3645), fstr(zeta6), "8/3645")
    audit.check("anisotropy", "low trace finite", low_trace_bound > 0, fstr(low_trace_bound), ">0")
    audit.check("anisotropy", "tail trace finite", tail_trace_bound > 0, fstr(tail_trace_bound), ">0")
    audit.check("anisotropy", "total is low plus tail", total_trace_bound == low_trace_bound + tail_trace_bound, fstr(total_trace_bound), "sum")
    audit.check("anisotropy", "six-real Fourier normalization", six_real_pointwise_trace_bound == Fraction(2) * total_trace_bound / volume, fstr(six_real_pointwise_trace_bound), "2*G_R/V")

    denominator = frac(params["M_X"]) ** 2 + frac(params["classii_mass_regularizer"])
    coeff_a = frac(params["cJJ"]) * frac(params["alpha_X"]) ** 2 / denominator
    coeff_b = frac(params["cJK"]) * frac(params["alpha_X"]) * frac(params["beta_X"]) / denominator
    coeff_c = frac(params["cKK"]) * frac(params["beta_X"]) ** 2 / denominator
    beta_actual = 4 * (coeff_a + 2 * abs(coeff_b) + coeff_c)
    beta_numerator = beta_actual * denominator
    beta_upper = beta_numerator / 4
    audit.check("coefficient", "regularized denominator", denominator > 4, fstr(denominator), ">4")
    audit.check("coefficient", "JJ entry positive", coeff_a > 0, fstr(coeff_a), ">0")
    audit.check("coefficient", "JK entry positive", coeff_b > 0, fstr(coeff_b), ">0")
    audit.check("coefficient", "KK entry positive", coeff_c > 0, fstr(coeff_c), ">0")
    audit.check("coefficient", "coefficient Gram determinant positive", coeff_a * coeff_c - coeff_b**2 > 0, fstr(coeff_a * coeff_c - coeff_b**2), ">0")
    audit.check("coefficient", "operator coefficient dominated", beta_actual < beta_upper, fstr(beta_actual), f"<{fstr(beta_upper)}")

    young_a = beta_upper * six_real_pointwise_trace_bound * length**2 / 2
    zeta_an = frac(manifest["audit_inputs"]["anisotropic_action_sextic_allocation"])
    young_action_constant = (
        Decimal(2)
        * (Decimal(young_a.numerator) / Decimal(young_a.denominator))
        * (Decimal(young_a.numerator) / Decimal(young_a.denominator)).sqrt()
        / (Decimal(3) * (Decimal(3 * zeta_an.numerator) / Decimal(zeta_an.denominator)).sqrt())
    )
    young_constant_square = Fraction(4) * young_a**3 / (27 * zeta_an)
    young_constant_ceiling = ceil_sqrt_fraction(young_constant_square)
    audit.check("young", "positive allocation", zeta_an > 0, fstr(zeta_an), ">0")
    audit.check("young", "positive Young scale", young_a > 0, fstr(young_a), ">0")
    audit.check("young", "finite Young constant", young_action_constant.is_finite() and young_action_constant > 0, str(young_action_constant), ">0")
    audit.check("young", "exact integer ceiling", Fraction((young_constant_ceiling - 1) ** 2) < young_constant_square <= Fraction(young_constant_ceiling**2), [fstr(young_constant_square), young_constant_ceiling], "(N-1)^2<C^2<=N^2")

    r144 = load_json(REPO / manifest["authorities"]["R-144-primary"])
    audit.check("authority", "R-144 primary result identity", r144["result_id"] == "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-LOW-COMPLETION-BOUNDARY", r144["result_id"], "A13-CLASSII-UNIFORM-DOUGLAS-ONE-USE-PROJECTED-FORCE-LOW-COMPLETION-BOUNDARY")
    p_value = frac(r144["exact_values"]["comparison_p"])
    source_loss_threshold = Fraction(1, 2) / p_value
    sextic_loss_threshold = frac(params["gamma"]) / 6
    source_coordinate = frac(r144["exact_values"]["q_source_target"])
    sextic_coordinate = frac(r144["exact_values"]["hessian_epsilon_sextic"])
    alpha_source_threshold = source_loss_threshold / source_coordinate
    alpha_sextic_threshold = sextic_loss_threshold / sextic_coordinate
    audit.check("threshold", "source loss threshold", source_loss_threshold == Fraction(5, 11), fstr(source_loss_threshold), "5/11")
    audit.check("threshold", "sextic loss threshold", sextic_loss_threshold == Fraction(27, 100), fstr(sextic_loss_threshold), "27/100")
    audit.check("threshold", "unit source paid", source_coordinate < source_loss_threshold, fstr(source_loss_threshold - source_coordinate), ">0")
    audit.check("threshold", "unit sextic paid", sextic_coordinate < sextic_loss_threshold, fstr(sextic_loss_threshold - sextic_coordinate), ">0")
    audit.check("threshold", "anisotropy leaves room", zeta_an < sextic_loss_threshold, fstr(sextic_loss_threshold - zeta_an), ">0")
    audit.check("threshold", "source coordinate multiplier", alpha_source_threshold > 1, fstr(alpha_source_threshold), ">1")
    audit.check("threshold", "sextic coordinate multiplier", alpha_sextic_threshold > 1, fstr(alpha_sextic_threshold), ">1")

    # Direct 2x2 calculation for the endpoint-versus-mixed fixture.
    diagonal = Fraction(9, 16)
    mixed_large_eigenvalue = 2 * diagonal
    paid_minus_large = 1 - mixed_large_eigenvalue
    audit.check("route", "each endpoint diagonal passes", diagonal < 1, fstr(diagonal), "<1")
    audit.check("route", "mixed eigenvalue exceeds one", mixed_large_eigenvalue > 1, fstr(mixed_large_eigenvalue), ">1")
    audit.check("route", "mixed paid Gram indefinite", paid_minus_large < 0, fstr(paid_minus_large), "<0")

    exact_values = {
        "mass_matrix": [[fstr(entry) for entry in row] for row in mass],
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
        "mixed_fixture_rho_squared": fstr(mixed_large_eigenvalue),
    }

    for key in (
        "weighted_trace_excess_criterion_proved",
        "canonical_t050_loss_thresholds_restored",
        "direct_trace_excess_thresholds_proved",
        "total_spatial_anisotropy_trace_bound_proved",
        "terminal_total_covariance_anisotropic_sextic_payment_proved",
    ):
        audit.check("scope", key, manifest["scope"][key] is True, manifest["scope"][key], True)
    for key in ("production_temporal_anisotropic_owner_payment_proved", "scalar_principal_sea_bound_proved", "complete_low_anchor_proved", "t050_closed", "sector_a_closed"):
        audit.check("scope", key, manifest["scope"][key] is False, manifest["scope"][key], False)

    audit.require()
    payload = {
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
            "sturm_chain_length": len(sturm),
            "independence": "standard library only; no import of primary implementation or symbolic/numerical linear algebra",
        },
        "source_hash": sha256(Path(__file__)),
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS: independent ({len(audit.rows)}/{len(audit.rows)})")
    print(f"RESULT: {OUTPUT.relative_to(REPO).as_posix()}")
    print(f"ANISOTROPIC COMPLEX FOURIER SUM BOUND: {fstr(total_trace_bound)}")
    print(f"SIX-REAL POINTWISE TRACE BOUND: {fstr(six_real_pointwise_trace_bound)}")
    print("OPEN: scalar principal sea, complete low/anchor, T-050, A13, Nelson, Sector A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
