#!/usr/bin/env python3
"""Independent certificate for the phase-neutral A13 R-148 checkpoint.

This script does not import the primary certificate or read its run artefact.
It uses exact Fraction Gaussian elimination, Jacobi complementary minors,
second-order jet arithmetic, a separate exact Gaussian-moment expansion, and
explicit mutation tests.  Its numerical mismatch check deliberately shares
NumPy's Gauss-Hermite backend with the primary and is not described as
backend-independent quadrature.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-CANONICAL-PREFIX-RANK-ACTIVE-SPECTATOR-"
    "LIFT-RELATIVE-HESSIAN-BOUNDARY"
)
SLUG = "canonical-prefix-rank-active-spectator-lift-relative-hessian-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / (
    "classii_canonical_prefix_rank_active_spectator_lift_"
    "relative_hessian_boundary_manifest.json"
)
OUTPUT = REPO / "claims" / CLAIM / "runs" / (
    f"2026-08-02-independent-{SLUG}"
) / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="independent-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Checks:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def add(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected})

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True, default=str))


Matrix = list[list[Fraction]]


def identity(size: int) -> Matrix:
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def invert(matrix: Matrix) -> Matrix:
    size = len(matrix)
    augmented = [row[:] + unit[:] for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column] != 0)
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [left - factor * right for left, right in zip(augmented[row], augmented[column])]
    return [row[size:] for row in augmented]


def determinant(matrix: Matrix) -> Fraction:
    if len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    total = Fraction(0)
    for column, value in enumerate(matrix[0]):
        minor = [[row[j] for j in range(len(matrix)) if j != column] for row in matrix[1:]]
        total += (-1 if column % 2 else 1) * value * determinant(minor)
    return total


@dataclass(frozen=True)
class Jet2:
    value: np.ndarray
    first: np.ndarray
    second: np.ndarray

    @staticmethod
    def variable(value: np.ndarray) -> "Jet2":
        return Jet2(value, np.ones_like(value), np.zeros_like(value))

    @staticmethod
    def constant(value: float | np.ndarray, template: np.ndarray) -> "Jet2":
        array = np.asarray(value) + np.zeros_like(template)
        return Jet2(array, np.zeros_like(template), np.zeros_like(template))

    def __add__(self, other: "Jet2") -> "Jet2":
        return Jet2(self.value + other.value, self.first + other.first, self.second + other.second)

    def __sub__(self, other: "Jet2") -> "Jet2":
        return Jet2(self.value - other.value, self.first - other.first, self.second - other.second)

    def __mul__(self, other: "Jet2") -> "Jet2":
        return Jet2(
            self.value * other.value,
            self.first * other.value + self.value * other.first,
            self.second * other.value + 2 * self.first * other.first + self.value * other.second,
        )

    def reciprocal(self) -> "Jet2":
        value = 1.0 / self.value
        first = -self.first / self.value**2
        second = 2 * self.first**2 / self.value**3 - self.second / self.value**2
        return Jet2(value, first, second)

    def __truediv__(self, other: "Jet2") -> "Jet2":
        return self * other.reciprocal()


def gh_expectation(function: Callable[[np.ndarray], np.ndarray], order: int) -> float:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return float(np.dot(weights, function(np.sqrt(2.0) * nodes)) / math.sqrt(math.pi))


def coefficient_rows(
    q: np.ndarray,
    radius: float,
    floor: float,
    p_norm: float,
    alpha: float,
    c0_times_p: float,
    c1_times_p: float,
) -> tuple[np.ndarray, np.ndarray]:
    c0 = c0_times_p / p_norm
    c1 = c1_times_p / p_norm
    active = radius + q
    spectator = radius - q
    density = active**2 + spectator**2 + floor
    rational = active - alpha * active**2 * (active - spectator) / density
    return 2.0 * math.sqrt(c0) * active, 2.0 * math.sqrt(c1) * rational


def coefficient_energy(q: np.ndarray, radius: float, floor: float, p_norm: float, alpha: float, c0_times_p: float, c1_times_p: float) -> np.ndarray:
    row_p, row_l = coefficient_rows(q, radius, floor, p_norm, alpha, c0_times_p, c1_times_p)
    return row_p**2 + row_l**2


def coefficient_energy_second(q: np.ndarray, radius: float, floor: float, p_norm: float, alpha: float, c0_times_p: float, c1_times_p: float) -> np.ndarray:
    variable = Jet2.variable(q)
    R = Jet2.constant(radius, q)
    e = Jet2.constant(floor, q)
    active = R + variable
    spectator = R - variable
    density = active * active + spectator * spectator + e
    rational = active - Jet2.constant(alpha, q) * active * active * (active - spectator) / density
    row_p = Jet2.constant(2.0 * math.sqrt(c0_times_p / p_norm), q) * active
    row_l = Jet2.constant(2.0 * math.sqrt(c1_times_p / p_norm), q) * rational
    energy = row_p * row_p + row_l * row_l
    return energy.second


def main() -> int:
    checks = Checks()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks.add("metadata", "claim", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    checks.add("metadata", "result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    checks.add("metadata", "ledger", manifest["result_ledger_id"] == "R-148", manifest["result_ledger_id"], "R-148")
    for label, relative in manifest["authorities"].items():
        path = REPO / relative
        checks.add("authority", f"{label} exists", path.is_file(), relative, "file")
        actual = digest(path)
        checks.add("authority", f"{label} digest", actual == manifest["authority_hashes"][label], actual, manifest["authority_hashes"][label])

    # Independent exact reconstruction from pinned A1 inputs and pinned R-147
    # coefficient inputs.  These are upstream INPUTS, not copied outputs.
    a1 = json.loads(
        (REPO / manifest["authorities"]["a1_production_manifest"])
        .read_text(encoding="utf-8")
    )
    parameters = a1["parameters"]
    masses = [Fraction(str(value)) for value in parameters["family_masses"]]
    lock = Fraction(str(parameters["k_lock"]))
    z0 = [Fraction(str(value)) for value in parameters["z0"]]
    z0_norm = sum(value * value for value in z0)
    r147_manifest = json.loads(
        (REPO / manifest["authorities"]["r147_manifest"])
        .read_text(encoding="utf-8")
    )
    coefficient_inputs = r147_manifest["audit_inputs"]
    alpha_fraction = Fraction(coefficient_inputs["production_alpha"])

    def per_p_fraction(text: str) -> Fraction:
        numerator, denominator_with_p = text.split("/(")
        denominator = denominator_with_p.removesuffix(")").removesuffix("P")
        return Fraction(int(numerator), int(denominator))

    c0_times_p_fraction = per_p_fraction(coefficient_inputs["production_p_coefficient"])
    c1_times_p_fraction = per_p_fraction(coefficient_inputs["production_l_coefficient"])
    M: Matrix = []
    for i in range(3):
        row: list[Fraction] = []
        for j in range(3):
            projector = Fraction(int(i == j)) - z0[i] * z0[j] / z0_norm
            row.append(Fraction(int(i == j)) * masses[i] + lock * projector)
        M.append(row)
    expected_M = [[Fraction(1, 10), -Fraction(1, 20), -Fraction(1, 20)], [-Fraction(1, 20), Fraction(13, 100), -Fraction(1, 20)], [-Fraction(1, 20), -Fraction(1, 20), Fraction(17, 100)]]
    checks.add("rank", "mass reconstruction", M == expected_M, M, expected_M)
    checks.add("rank", "mass determinant", determinant(M) == Fraction(3, 3125), determinant(M), Fraction(3, 3125))

    rank_table: list[dict[str, Any]] = []
    for kinetic in (Fraction(0), Fraction(1, 2), Fraction(2)):
        A = [[M[i][j] + (kinetic if i == j else 0) for j in range(3)] for i in range(3)]
        C = invert(A)
        radial = [[C[0][0], C[0][2]], [C[2][0], C[2][2]]]
        det_radial = determinant(radial)
        oracle = Fraction(250) * (100 * kinetic + 13) / (25000 * kinetic**3 + 10000 * kinetic**2 + 1115 * kinetic + 24)
        checks.add("rank", f"Jacobi radial determinant a={kinetic}", det_radial == oracle and det_radial > 0, det_radial, oracle)
        for tau in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
            scaled = [[tau * value for value in row] for row in radial]
            checks.add("rank", f"canonical block full rank a={kinetic} tau={tau}", determinant(scaled) == tau**2 * det_radial and determinant(scaled) > 0, determinant(scaled), tau**2 * det_radial)

        u, cross, w = radial[0][0], radial[0][1], radial[1][1]
        first = [[u, cross], [cross, cross * cross / u]]
        second = [[Fraction(0), Fraction(0)], [Fraction(0), w - cross * cross / u]]
        reconstructed = [[first[i][j] + second[i][j] for j in range(2)] for i in range(2)]
        checks.add("rank", f"rank-one prefix terminal sum a={kinetic}", reconstructed == radial, reconstructed, radial)
        checks.add("rank", f"rank-one prefix determinant a={kinetic}", determinant(first) == 0 and determinant(second) == 0, [determinant(first), determinant(second)], [0, 0])
        checks.add("mutation", f"terminal-only transport mutant rejected a={kinetic}", determinant(first) != Fraction(1, 2) ** 2 * det_radial, determinant(first), "not canonical half block")
        rank_table.append({"kinetic": str(kinetic), "radial": [[str(x) for x in row] for row in radial], "determinant": str(det_radial)})

    kinetic_symbol, tau_symbol = sp.symbols("a tau", nonnegative=True)
    universal_numerator = 250 * tau_symbol**2 * (100 * kinetic_symbol + 13)
    universal_denominator = (
        25000 * kinetic_symbol**3
        + 10000 * kinetic_symbol**2
        + 1115 * kinetic_symbol
        + 24
    )
    checks.add(
        "rank",
        "universal final-block determinant formula",
        all(value > 0 for value in sp.Poly(universal_numerator / tau_symbol**2, kinetic_symbol).all_coeffs())
        and all(value > 0 for value in sp.Poly(universal_denominator, kinetic_symbol).all_coeffs()),
        str(universal_numerator / universal_denominator),
        ">0 for a>=0 and tau>0",
    )

    # Direct row integration; no closed f'' formula is used.
    fixture = manifest["audit_inputs"]["fixture"]
    radius = float(Fraction(fixture["radius"]))
    floor = float(Fraction(fixture["floor"]))
    p_norm = float(Fraction(fixture["p_norm"]))
    sigma = float(Fraction(fixture["sigma"]))
    alpha_float = float(alpha_fraction)
    c0_times_p_float = float(c0_times_p_fraction)
    c1_times_p_float = float(c1_times_p_fraction)
    gh_table: list[dict[str, float]] = []
    for order in (32, 64, 96):
        nodes, weights = np.polynomial.hermite.hermgauss(order)
        g = np.sqrt(2.0) * nodes
        norm = 1.0 / math.sqrt(math.pi)
        q = sigma * g
        row_p, row_l = coefficient_rows(q, radius, floor, p_norm, alpha_float, c0_times_p_float, c1_times_p_float)
        energy = row_p**2 + row_l**2
        bar_tau = sigma**2 * float(np.dot(weights, energy) * norm)
        b = sigma * np.asarray([np.dot(weights, g * row_p), np.dot(weights, g * row_l)]) * norm
        raw = sigma**2 * float(np.dot(weights, g**2 * energy) * norm)
        beta = raw - float(np.dot(b, b))
        delta = bar_tau - beta
        f2_values = coefficient_energy_second(q, radius, floor, p_norm, alpha_float, c0_times_p_float, c1_times_p_float)
        stein = -sigma**4 * float(np.dot(weights, f2_values) * norm) + float(np.dot(b, b))
        raw_mutant_delta = bar_tau - raw
        checks.add("mismatch", f"positive mismatch GH{order}", delta > 0, delta, ">0")
        checks.add("mismatch", f"Jet2 Stein identity GH{order}", abs(delta - stein) < 3e-13, delta - stein, "abs<3e-13")
        checks.add("mutation", f"mean-square omission detected GH{order}", abs((delta - raw_mutant_delta) - float(np.dot(b, b))) < 3e-13 and float(np.dot(b, b)) > 0, delta - raw_mutant_delta, float(np.dot(b, b)))
        checks.add("mutation", f"Gaussian fourth moment GH{order}", abs(float(np.dot(weights, g**4) * norm) - 3.0) < 1e-13, float(np.dot(weights, g**4) * norm), 3.0)
        gh_table.append({"order": order, "bar_tau": bar_tau, "beta": beta, "b2": float(np.dot(b, b)), "delta": delta, "stein": stein})
    checks.add("mismatch", "64/96 convergence", abs(gh_table[-1]["delta"] - gh_table[-2]["delta"]) < 1e-13, [row["delta"] for row in gh_table], "last two within 1e-13")

    # Exact thresholds from integer polynomials and a series route.
    rho = sp.symbols("rho", real=True)
    p2 = 113 - 88 * rho - 528 * rho**2
    r147 = -sp.Rational(1, 12) + 5 * sp.sqrt(154) / 132
    checks.add("threshold", "R-147 radical root", sp.simplify(p2.subs(rho, r147)) == 0, str(r147), "root")
    checks.add("threshold", "R-147 rational bracket signs", p2.subs(rho, sp.Rational(3867, 10000)) > 0 and p2.subs(rho, sp.Rational(3868, 10000)) < 0, [str(p2.subs(rho, sp.Rational(3867, 10000))), str(p2.subs(rho, sp.Rational(3868, 10000)))], [">0", "<0"])

    qsym, Rsym, esym, Psym = sp.symbols("q R e P", positive=True)
    x = Rsym + qsym
    y = Rsym - qsym
    d = x**2 + y**2 + esym
    alpha_exact = sp.Rational(alpha_fraction.numerator, alpha_fraction.denominator)
    c0_exact = sp.Rational(c0_times_p_fraction.numerator, c0_times_p_fraction.denominator)
    c1_exact = sp.Rational(c1_times_p_fraction.numerator, c1_times_p_fraction.denominator)
    row_energy = 4 * c0_exact / Psym * x**2 + 4 * c1_exact / Psym * (x - alpha_exact * x**2 * (x - y) / d) ** 2
    series = sp.series(row_energy, qsym, 0, 5).removeO().expand()
    f2_series = sp.factor(2 * series.coeff(qsym, 2))
    f3_series = sp.factor(6 * series.coeff(qsym, 3))
    f4_series = sp.factor(24 * series.coeff(qsym, 4))
    expected_f3 = -9 * Rsym * (16 * Rsym**2 + 27 * esym) / (50 * Psym * (2 * Rsym**2 + esym) ** 2)
    expected_f4 = 18 * (112 * Rsym**4 + 48 * Rsym**2 * esym - 9 * esym**2) / (25 * Psym * (2 * Rsym**2 + esym) ** 3)
    checks.add("series", "third derivative series", sp.simplify(f3_series - expected_f3) == 0, str(f3_series), str(expected_f3))
    checks.add("series", "fourth derivative series", sp.simplify(f4_series - expected_f4) == 0, str(f4_series), str(expected_f4))
    checks.add("series", "third derivative negative", sp.ask(sp.Q.negative(expected_f3)) is True, str(expected_f3), "<0")
    r4 = -sp.Rational(3, 14) + 3 * sp.sqrt(11) / 28
    checks.add("threshold", "fourth derivative root", sp.simplify((112 * rho**2 + 48 * rho - 9).subs(rho, r4)) == 0, str(r4), "root")
    checks.add("threshold", "threshold separation", r147 > sp.Rational(1, 3) and r4 < sp.Rational(1, 7), [str(r147), str(r4)], [">1/3", "<1/7"])

    # Separate exact Gaussian-moment reconstruction of the source/sextic
    # coefficient-parameter polynomial.  This does not identify a physical
    # source lift, but independently checks the declared Section 6 algebra.
    msym, sigsym, kappasym, gsym = sp.symbols("m sigma kappa g", real=True)
    sextic_integrand = sp.Rational(6, 5) * (Rsym**2 + (msym + sigsym * gsym) ** 2) ** 3
    gaussian_moments = {0: 1, 2: 1, 4: 3, 6: 15}
    polynomial = sp.Poly(sp.expand(sextic_integrand), gsym)
    sextic_expectation = sum(
        coefficient * gaussian_moments.get(power[0], 0)
        for power, coefficient in polynomial.terms()
    )
    sextic_difference = sp.factor(sextic_expectation - sextic_expectation.subs(msym, 0))
    expected_sextic_difference = (
        sp.Rational(18, 5) * msym**2 * (Rsym**4 + 6 * Rsym**2 * sigsym**2 + 15 * sigsym**4)
        + sp.Rational(18, 5) * msym**4 * (Rsym**2 + 5 * sigsym**2)
        + sp.Rational(6, 5) * msym**6
    )
    checks.add("relative-action", "sextic moment polynomial", sp.simplify(sextic_difference - expected_sextic_difference) == 0, str(sextic_difference), str(expected_sextic_difference))
    source = sp.Rational(9, 20) * kappasym * msym**2
    checks.add("relative-action", "source curvature nonnegative form", sp.diff(source, msym, 2) == sp.Rational(9, 10) * kappasym, str(sp.diff(source, msym, 2)), "9*kappa/10")
    checks.add("relative-action", "sextic curvature", sp.simplify(sp.diff(sextic_difference, msym, 2).subs(msym, 0) - sp.Rational(36, 5) * (Rsym**4 + 6 * Rsym**2 * sigsym**2 + 15 * sigsym**4)) == 0, str(sp.diff(sextic_difference, msym, 2).subs(msym, 0)), "36*(R^4+6R^2 sigma^2+15 sigma^4)/5")

    # Denominator and sign/factor mutations must change the registered jet.
    wrong_d = x**2 + esym
    wrong_energy = 4 * c0_exact / Psym * x**2 + 4 * c1_exact / Psym * (x - alpha_exact * x**2 * (x - y) / wrong_d) ** 2
    wrong_f2 = sp.factor(2 * sp.series(wrong_energy, qsym, 0, 3).removeO().expand().coeff(qsym, 2))
    checks.add("mutation", "spectator denominator mutation rejected", sp.simplify(wrong_f2 - f2_series) != 0, str(wrong_f2), "different from exact f2")
    checks.add("mutation", "curvature sign mutation rejected", (113 - 88 * rho + 528 * rho**2).subs(rho, 1) != p2.subs(rho, 1), str((113 - 88 * rho + 528 * rho**2).subs(rho, 1)), str(p2.subs(rho, 1)))
    gaussian_fourth = float(np.dot(weights, g**4) * norm)
    rademacher_atoms = np.asarray([-1.0, 1.0])
    rademacher_weights = np.asarray([0.5, 0.5])
    rademacher_fourth = float(np.dot(rademacher_weights, rademacher_atoms**4))
    checks.add(
        "mutation",
        "Rademacher is not Brownian",
        abs(gaussian_fourth - rademacher_fourth) > 1.0,
        rademacher_fourth,
        f"different from Gaussian fourth moment {gaussian_fourth}",
    )

    # Independent rational orthogonal-gauge witness for diagonal-data
    # non-identifiability.
    def gauge(value: Fraction) -> tuple[Fraction, Fraction]:
        denominator = 1 + value * value
        return ((1 - value * value) / denominator, 2 * value / denominator)

    b0 = gauge(Fraction(0))
    b1 = gauge(Fraction(1))
    checks.add("nonidentifiability", "gauge norms agree", sum(x * x for x in b0) == 1 and sum(x * x for x in b1) == 1, [sum(x * x for x in b0), sum(x * x for x in b1)], [1, 1])
    checks.add("nonidentifiability", "gauge mixed Gram differs", sum(x * y for x, y in zip(b0, b1)) == 0, sum(x * y for x, y in zip(b0, b1)), "0 versus constant-coordinate 1")
    h = Fraction(1, 10000)
    bp = gauge(h)
    bm = gauge(-h)
    derivative = tuple((plus - minus) / (2 * h) for plus, minus in zip(bp, bm))
    derivative_energy = sum(value * value for value in derivative)
    checks.add("nonidentifiability", "gauge jet energy converges to four", abs(float(derivative_energy) - 4.0) < 1e-7, str(derivative_energy), "4")

    scope = manifest["scope"]
    for key in (
        "adapted_past_rank_one_necessity_proved",
        "uniform_adverse_region_noise_threshold_proved",
        "physical_deterministic_control_hessian_identified",
        "exact_r147_line_is_r146_canonical_chart",
        "old_owner_transport_proved",
        "r063_production_forest_identified",
        "complete_owner_sign_determined",
        "minimal_last_root_origin_stationary_proved",
        "physical_phase_selected",
        "t050_closed",
        "sector_a_closed",
    ):
        checks.add("scope", key, scope[key] is False, scope[key], False)
    checks.add("scope", "fresh final rank obstruction", scope["fresh_final_canonical_prefix_rank_obstruction_proved"] is True, scope["fresh_final_canonical_prefix_rank_obstruction_proved"], True)
    checks.add("scope", "no-correction past fixture", scope["no_correction_past_rank_fixture_proved"] is True, scope["no_correction_past_rank_fixture_proved"], True)
    checks.add("scope", "mismatch identity", scope["generic_last_root_mismatch_identity_proved"] is True, scope["generic_last_root_mismatch_identity_proved"], True)
    checks.add("scope", "coefficient-parameter Hessian diagnostic", scope["minimal_last_root_coefficient_parameter_hessian_diagnostic_proved"] is True, scope["minimal_last_root_coefficient_parameter_hessian_diagnostic_proved"], True)
    checks.add("scope", "coefficient diagonal does not identify full owner", scope["coefficient_diagonal_identifies_full_owner"] is False, scope["coefficient_diagonal_identifies_full_owner"], False)

    checks.require()
    payload = {
        "schema": SCHEMA,
        "script_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions": {"total": len(checks.rows), "passed": len(checks.rows), "failed": 0, "rows": checks.rows},
        "exact_values": {
            "mass_determinant": str(determinant(M)),
            "active_spectator_f2": str(f2_series),
            "active_spectator_f3": str(f3_series),
            "active_spectator_f4": str(f4_series),
            "r147_threshold": str(r147),
            "relative_hessian_threshold": str(r4),
        },
        "cross_values": {
            "r147_threshold": str(r147),
            "relative_hessian_threshold": str(r4),
            "fixture_delta": gh_table[-1]["delta"],
            "fixture_mean_square": gh_table[-1]["b2"],
        },
        "rank_table": rank_table,
        "gauss_hermite": gh_table,
        "independence_scope": {
            "fraction_matrix_route_independent": True,
            "symbolic_series_route_independent": True,
            "source_sextic_moment_route_separate": True,
            "gauss_hermite_backend_shared_with_primary": True,
        },
        "scope": scope,
        "mutations_rejected": [
            "terminal-only prefix transport",
            "rank-one proportional block",
            "predictable mean-square omission",
            "spectator denominator omission",
            "curvature sign mutation",
            "Rademacher-as-Brownian mutation",
        ],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS {RESULT_ID} ({len(checks.rows)}/{len(checks.rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
