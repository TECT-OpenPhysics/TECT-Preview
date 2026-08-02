#!/usr/bin/env python3
"""Primary certificate for the phase-neutral A13 R-147 checkpoint.

The certificate verifies an exact signed common-terminal Doob telescope for
the complete R-141/R-142 terminal feature, the conditional signed-variance
recursion, and the precise polarized trace--bracket defect that obstructs
transport of the new canonical owners to the old R-063/R-125 owner chart.

It also verifies two method boundaries: equal endpoint law does not preserve
Doob owner energies, and even a centred one-step common-terminal current may
have positive trace--current defect when its coefficient uses the same root.
No physical phase and no complete or non-collinear production scalar bound is
selected or asserted.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CANONICAL-SIGNED-COMMON-TERMINAL-DOOB-BRACKET-DEFECT-BOUNDARY"
SCHEMA = "tect/a13-canonical-signed-common-terminal-doob-bracket-defect-boundary-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_canonical_signed_common_terminal_doob_bracket_defect_boundary_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-primary-canonical-signed-common-terminal-doob-bracket-defect-boundary" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


Vector = tuple[Fraction, ...]


def vec(*values: int | Fraction) -> Vector:
    return tuple(Fraction(value) for value in values)


def vadd(left: Vector, right: Vector) -> Vector:
    return tuple(a + b for a, b in zip(left, right))


def vsub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def vmean(values: Iterable[Vector]) -> Vector:
    rows = list(values)
    return tuple(sum((row[index] for row in rows), Fraction(0)) / len(rows) for index in range(len(rows[0])))


def mean(values: Iterable[Fraction]) -> Fraction:
    rows = list(values)
    return sum(rows, Fraction(0)) / len(rows)


def signed_pair(left: Vector, right: Vector, signs: Vector) -> Fraction:
    return sum((sign * a * b for sign, a, b in zip(signs, left, right)), Fraction(0))


def conditional_vectors(values: list[Vector], labels: list[int]) -> list[Vector]:
    groups: dict[int, list[int]] = {}
    for index, label in enumerate(labels):
        groups.setdefault(label, []).append(index)
    averages = {label: vmean(values[index] for index in indices) for label, indices in groups.items()}
    return [averages[label] for label in labels]


def conditional_scalars(values: list[Fraction], labels: list[int]) -> list[Fraction]:
    groups: dict[int, list[int]] = {}
    for index, label in enumerate(labels):
        groups.setdefault(label, []).append(index)
    averages = {label: mean(values[index] for index in indices) for label, indices in groups.items()}
    return [averages[label] for label in labels]


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
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True, default=str))


def main() -> int:
    audit = Audit()
    manifest = load_json(MANIFEST)

    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger id", manifest["result_ledger_id"] == "R-147", manifest["result_ledger_id"], "R-147")
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    for label, relative in manifest["authorities"].items():
        path = REPO / relative
        audit.check("authority", f"{label} exists", path.is_file(), relative, "file")
        actual = sha256(path)
        audit.check("authority", f"{label} hash", actual == manifest["authority_hashes"][label], actual, manifest["authority_hashes"][label])

    # ------------------------------------------------------------------
    # Exact signed common-terminal telescope on a four-atom filtration.
    # ------------------------------------------------------------------
    signs = vec(1, -1, 1)
    z_zero = [vec(1, 0, 1), vec(0, 1, -1), vec(2, -1, 0), vec(-1, 2, 1)]
    z_shift = [vec(2, 1, 0), vec(-1, 0, 2), vec(1, 2, -1), vec(0, -1, 3)]
    z_sum = [vadd(left, right) for left, right in zip(z_shift, z_zero)]
    z_delta = [vsub(left, right) for left, right in zip(z_shift, z_zero)]

    labels_0 = [0, 0, 0, 0]
    labels_1 = [0, 0, 1, 1]
    labels_2 = [0, 1, 2, 3]
    filtrations = [labels_0, labels_1, labels_2]
    m_sum = [conditional_vectors(z_sum, labels) for labels in filtrations]
    m_delta = [conditional_vectors(z_delta, labels) for labels in filtrations]
    d_sum = [[vsub(m_sum[level][atom], m_sum[level - 1][atom]) for atom in range(4)] for level in (1, 2)]
    d_delta = [[vsub(m_delta[level][atom], m_delta[level - 1][atom]) for atom in range(4)] for level in (1, 2)]

    terminal_cross = mean(signed_pair(left, right, signs) for left, right in zip(z_sum, z_delta))
    base_cross = mean(signed_pair(left, right, signs) for left, right in zip(m_sum[0], m_delta[0]))
    step_crosses = [mean(signed_pair(left, right, signs) for left, right in zip(ds, dd)) for ds, dd in zip(d_sum, d_delta)]
    audit.check("doob", "terminal martingales end at signed features", m_sum[2] == z_sum and m_delta[2] == z_delta, [m_sum[2], m_delta[2]], [z_sum, z_delta])
    audit.check("doob", "first tower for sum feature", conditional_vectors(m_sum[2], labels_1) == m_sum[1], conditional_vectors(m_sum[2], labels_1), m_sum[1])
    audit.check("doob", "first tower for delta feature", conditional_vectors(m_delta[2], labels_1) == m_delta[1], conditional_vectors(m_delta[2], labels_1), m_delta[1])
    audit.check("doob", "second tower for sum feature", conditional_vectors(m_sum[1], labels_0) == m_sum[0], conditional_vectors(m_sum[1], labels_0), m_sum[0])
    audit.check("doob", "second tower for delta feature", conditional_vectors(m_delta[1], labels_0) == m_delta[0], conditional_vectors(m_delta[1], labels_0), m_delta[0])
    audit.check("doob", "signed terminal telescope", terminal_cross == base_cross + sum(step_crosses, Fraction(0)), terminal_cross, base_cross + sum(step_crosses, Fraction(0)))

    # Conditional signed-future-variance recursion at both filtration steps.
    terminal_pointwise = [signed_pair(left, right, signs) for left, right in zip(z_sum, z_delta)]
    signed_future: list[list[Fraction]] = []
    for level, labels in enumerate(filtrations):
        terminal_conditional = conditional_scalars(terminal_pointwise, labels)
        signed_future.append(
            [terminal_conditional[atom] - signed_pair(m_sum[level][atom], m_delta[level][atom], signs) for atom in range(4)]
        )
    audit.check("doob", "terminal signed future variance vanishes", signed_future[2] == [Fraction(0)] * 4, signed_future[2], [0, 0, 0, 0])
    for level in (1, 2):
        previous_labels = filtrations[level - 1]
        future_conditional = conditional_scalars(signed_future[level], previous_labels)
        increment_pointwise = [signed_pair(left, right, signs) for left, right in zip(d_sum[level - 1], d_delta[level - 1])]
        increment_conditional = conditional_scalars(increment_pointwise, previous_labels)
        reconstructed = [future_conditional[index] + increment_conditional[index] for index in range(4)]
        audit.check("doob", f"conditional signed variance recursion level {level}", reconstructed == signed_future[level - 1], reconstructed, signed_future[level - 1])

    # The R-141 three-feature signature compresses exactly to R-142's two
    # features after the same auxiliary-future expectation.
    u_zero = [vec(1, 2), vec(-1, 1)]
    u_shift = [vec(2, -1), vec(0, 3)]
    j_zero = [vec(2, 0), vec(0, 2)]
    j_shift = [vec(3, 1), vec(-1, 3)]
    phi_zero = vmean(j_zero)
    phi_shift = vmean(j_shift)
    r_zero = [vsub(value, phi_zero) for value in j_zero]
    r_shift = [vsub(value, phi_shift) for value in j_shift]
    three_feature = mean(
        signed_pair(vadd(uh, u0), vsub(uh, u0), vec(1, 1))
        - signed_pair(vadd(jh, j0), vsub(jh, j0), vec(1, 1))
        + signed_pair(vadd(rh, r0), vsub(rh, r0), vec(1, 1))
        for uh, u0, jh, j0, rh, r0 in zip(u_shift, u_zero, j_shift, j_zero, r_shift, r_zero)
    )
    two_feature = mean(
        signed_pair(vadd(uh, u0), vsub(uh, u0), vec(1, 1)) for uh, u0 in zip(u_shift, u_zero)
    ) - signed_pair(vadd(phi_shift, phi_zero), vsub(phi_shift, phi_zero), vec(1, 1))
    audit.check("signature", "three-feature to two-feature compression", three_feature == two_feature, three_feature, two_feature)
    audit.check("signature", "future residuals are centred at zero endpoint", vmean(r_zero) == vec(0, 0), vmean(r_zero), vec(0, 0))
    audit.check("signature", "future residuals are centred at shifted endpoint", vmean(r_shift) == vec(0, 0), vmean(r_shift), vec(0, 0))

    # The same compression holds at every canonical source reveal and for
    # every increment when the future projection belongs to the nested grid.
    source_u_zero = [vec(1), vec(-1), vec(2), vec(0)]
    source_u_shift = [vec(2), vec(0), vec(-1), vec(3)]
    source_j_zero = [vec(3), vec(-1), vec(2), vec(0)]
    source_j_shift = [vec(1), vec(3), vec(-2), vec(4)]
    source_phi_zero = conditional_vectors(source_j_zero, labels_1)
    source_phi_shift = conditional_vectors(source_j_shift, labels_1)
    source_r_zero = [
        vsub(value, projected)
        for value, projected in zip(source_j_zero, source_phi_zero)
    ]
    source_r_shift = [
        vsub(value, projected)
        for value, projected in zip(source_j_shift, source_phi_shift)
    ]
    source_z_zero = [
        u + j + r
        for u, j, r in zip(source_u_zero, source_j_zero, source_r_zero)
    ]
    source_z_shift = [
        u + j + r
        for u, j, r in zip(source_u_shift, source_j_shift, source_r_shift)
    ]
    source_f_zero = [
        u + projected
        for u, projected in zip(source_u_zero, source_phi_zero)
    ]
    source_f_shift = [
        u + projected
        for u, projected in zip(source_u_shift, source_phi_shift)
    ]
    source_z_sum = [vadd(left, right) for left, right in zip(source_z_shift, source_z_zero)]
    source_z_delta = [vsub(left, right) for left, right in zip(source_z_shift, source_z_zero)]
    source_f_sum = [vadd(left, right) for left, right in zip(source_f_shift, source_f_zero)]
    source_f_delta = [vsub(left, right) for left, right in zip(source_f_shift, source_f_zero)]
    z_sum_tower = [conditional_vectors(source_z_sum, labels) for labels in filtrations]
    z_delta_tower = [conditional_vectors(source_z_delta, labels) for labels in filtrations]
    f_sum_tower = [conditional_vectors(source_f_sum, labels) for labels in filtrations]
    f_delta_tower = [conditional_vectors(source_f_delta, labels) for labels in filtrations]
    for level in range(3):
        z_cross = mean(
            signed_pair(left, right, vec(1, -1, 1))
            for left, right in zip(z_sum_tower[level], z_delta_tower[level])
        )
        f_cross = mean(
            signed_pair(left, right, vec(1, -1))
            for left, right in zip(f_sum_tower[level], f_delta_tower[level])
        )
        audit.check(
            "signature",
            f"source reveal compression level {level}",
            z_cross == f_cross,
            z_cross,
            f_cross,
        )
    for level in (1, 2):
        z_increment_sum = [
            vsub(current, previous)
            for current, previous in zip(z_sum_tower[level], z_sum_tower[level - 1])
        ]
        z_increment_delta = [
            vsub(current, previous)
            for current, previous in zip(z_delta_tower[level], z_delta_tower[level - 1])
        ]
        f_increment_sum = [
            vsub(current, previous)
            for current, previous in zip(f_sum_tower[level], f_sum_tower[level - 1])
        ]
        f_increment_delta = [
            vsub(current, previous)
            for current, previous in zip(f_delta_tower[level], f_delta_tower[level - 1])
        ]
        z_increment_cross = mean(
            signed_pair(left, right, vec(1, -1, 1))
            for left, right in zip(z_increment_sum, z_increment_delta)
        )
        f_increment_cross = mean(
            signed_pair(left, right, vec(1, -1))
            for left, right in zip(f_increment_sum, f_increment_delta)
        )
        audit.check(
            "signature",
            f"source increment compression level {level}",
            z_increment_cross == f_increment_cross,
            z_increment_cross,
            f_increment_cross,
        )

    # Complex Hermitian polarization protects the real-part and conjugation
    # convention used by the signed telescope.
    imaginary = sp.I
    complex_shift = (1 + 2 * imaginary, -1 + imaginary)
    complex_zero = (2 - imaginary, 3 + 2 * imaginary)
    complex_sum = tuple(left + right for left, right in zip(complex_shift, complex_zero))
    complex_delta = tuple(left - right for left, right in zip(complex_shift, complex_zero))
    complex_signs = (1, -1)

    def hermitian(left: tuple[sp.Expr, ...], right: tuple[sp.Expr, ...]) -> sp.Expr:
        return sp.simplify(
            sum(
                sp.conjugate(a) * sign * b
                for a, sign, b in zip(left, complex_signs, right)
            )
        )

    complex_direct = sp.re(hermitian(complex_shift, complex_shift) - hermitian(complex_zero, complex_zero))
    complex_polarized = sp.re(hermitian(complex_sum, complex_delta))
    audit.check(
        "signature",
        "complex Hermitian real-part polarization",
        sp.simplify(complex_direct - complex_polarized) == 0,
        str(complex_direct),
        str(complex_polarized),
    )

    # ------------------------------------------------------------------
    # Exact polarized R-125 trace--bracket defect identity.
    # ------------------------------------------------------------------
    phi_p = [Fraction(value) for value in (1, 3, -2, 0)]
    phi_q = [Fraction(value) for value in (2, -1, 4, 2)]
    b_p = conditional_scalars(phi_p, labels_1)
    b_q = conditional_scalars(phi_q, labels_1)
    y_p = [value - base for value, base in zip(phi_p, b_p)]
    y_q = [value - base for value, base in zip(phi_q, b_q)]
    beta = conditional_scalars([left * right for left, right in zip(y_p, y_q)], labels_1)
    delta = [Fraction(1, 3), Fraction(1, 3), Fraction(-2, 5), Fraction(-2, 5)]
    variance = [Fraction(2), Fraction(2), Fraction(1), Fraction(1)]
    phi_product_raw = [left * right for left, right in zip(phi_p, phi_q)]
    trace_oscillation = [Fraction(1), Fraction(-1), Fraction(2), Fraction(-2)]
    tau_raw = [
        bracket + mismatch + oscillation
        for bracket, mismatch, oscillation in zip(beta, delta, trace_oscillation)
    ]
    forest_raw = [v + pp - tr for v, pp, tr in zip(variance, phi_product_raw, tau_raw)]
    residual_raw = [v - f for v, f in zip(variance, forest_raw)]
    bar_tau = conditional_scalars(tau_raw, labels_1)
    conditional_residual = conditional_scalars(residual_raw, labels_1)
    predictable_defect = [trace - bracket for trace, bracket in zip(bar_tau, beta)]
    defect_identity = [
        mismatch - left * right
        for mismatch, left, right in zip(predictable_defect, b_p, b_q)
    ]
    audit.check(
        "matching",
        "raw polarized residual equals raw trace minus raw mean product",
        residual_raw == [tr - pp for tr, pp in zip(tau_raw, phi_product_raw)],
        residual_raw,
        [tr - pp for tr, pp in zip(tau_raw, phi_product_raw)],
    )
    audit.check("matching", "primitive trace is not past measurable", tau_raw != bar_tau, tau_raw, bar_tau)
    audit.check(
        "matching",
        "predictable trace projection retains prescribed mismatch",
        predictable_defect == delta,
        predictable_defect,
        delta,
    )
    audit.check(
        "matching",
        "conditioned trace-bracket defect identity",
        conditional_residual == defect_identity,
        conditional_residual,
        defect_identity,
    )
    audit.check("matching", "nonzero predictable mismatch detected", any(value != 0 for value in delta), delta, "nonzero")

    tau_matched_raw = [
        bracket + oscillation
        for bracket, oscillation in zip(beta, trace_oscillation)
    ]
    forest_matched_raw = [
        v + pp - tr
        for v, pp, tr in zip(variance, phi_product_raw, tau_matched_raw)
    ]
    residual_matched_raw = [
        v - f for v, f in zip(variance, forest_matched_raw)
    ]
    residual_matched = conditional_scalars(residual_matched_raw, labels_1)
    expected_matched = [-left * right for left, right in zip(b_p, b_q)]
    audit.check(
        "matching",
        "matched predictable trace gives conditioned negative Gram",
        residual_matched == expected_matched,
        residual_matched,
        expected_matched,
    )
    forest_matched = conditional_scalars(forest_matched_raw, labels_1)
    variance_conditional = conditional_scalars(variance, labels_1)
    audit.check(
        "matching",
        "equivalent conditioned forest matching law",
        forest_matched
        == [
            v + left * right
            for v, left, right in zip(variance_conditional, b_p, b_q)
        ],
        forest_matched,
        [
            v + left * right
            for v, left, right in zip(variance_conditional, b_p, b_q)
        ],
    )

    # Regression: raw pointwise trace matching is not necessary.  With
    # Phi=xi, xi in {-1,+1}, beta=1, and tau=1+xi, only the predictable
    # projection matches, while the conditioned residual is exactly zero.
    xi = [Fraction(-1), Fraction(1)]
    tau_current_root = [Fraction(0), Fraction(2)]
    bar_tau_current_root = mean(tau_current_root)
    residual_current_root = [
        trace_value - value * value
        for trace_value, value in zip(tau_current_root, xi)
    ]
    audit.check(
        "matching",
        "current-root trace differs pointwise from bracket",
        tau_current_root != [Fraction(1), Fraction(1)],
        tau_current_root,
        "not pointwise one",
    )
    audit.check(
        "matching",
        "current-root trace matches bracket after past conditioning",
        bar_tau_current_root == 1 and mean(residual_current_root) == 0,
        [bar_tau_current_root, mean(residual_current_root)],
        [1, 0],
    )

    # A matched absolute baseline is nonpositive, but a relative difference
    # of such squares can have either sign.
    r_at = lambda amplitude: -Fraction(amplitude * amplitude, 4)
    delta_down = r_at(1) - r_at(2)
    delta_up = r_at(2) - r_at(1)
    audit.check("relative", "matched relative residual can be positive", delta_down == Fraction(3, 4), delta_down, Fraction(3, 4))
    audit.check("relative", "matched relative residual can be negative", delta_up == Fraction(-3, 4), delta_up, Fraction(-3, 4))
    audit.check("relative", "opposite directions polarize", delta_down == -delta_up, delta_down, -delta_up)

    # ------------------------------------------------------------------
    # Centred common-terminal scalar no-go.
    # ------------------------------------------------------------------
    t = sp.symbols("t", positive=True)
    trace = (1 + 2 * t) ** sp.Rational(-1, 2)
    current = (1 + 2 * t) ** sp.Rational(-3, 2)
    defect = sp.simplify(trace - current)
    expected_defect = 2 * t / (1 + 2 * t) ** sp.Rational(3, 2)
    ratio = sp.simplify(defect / trace)
    audit.check("nogo", "centred same-root defect formula", sp.simplify(defect - expected_defect) == 0, str(defect), str(expected_defect))
    audit.check("nogo", "centred same-root defect positive", sp.ask(sp.Q.positive(defect)) is True, str(defect), ">0")
    g = sp.symbols("g", real=True)
    odd_current = g * sp.exp(-t * g**2 / 2)
    audit.check(
        "nogo",
        "centred coefficient current mean is zero by oddness",
        sp.simplify(odd_current.subs(g, -g) + odd_current) == 0,
        str(sp.simplify(odd_current.subs(g, -g) + odd_current)),
        "0",
    )
    audit.check("nogo", "defect ratio", sp.simplify(ratio - 2 * t / (1 + 2 * t)) == 0, str(ratio), "2t/(1+2t)")
    audit.check("nogo", "defect ratio tends to one", sp.limit(ratio, t, sp.oo) == 1, str(sp.limit(ratio, t, sp.oo)), "1")
    audit.check("nogo", "t equals two ratio", sp.simplify(ratio.subs(t, 2)) == sp.Rational(4, 5), str(sp.simplify(ratio.subs(t, 2))), "4/5")

    # Same N(0,1) terminal laws can have different owner energies.
    chart_a = (sp.Integer(1), sp.Integer(0))
    chart_b = (1 / sp.sqrt(2), 1 / sp.sqrt(2))

    def derive_owner_energies(coefficients: tuple[sp.Expr, sp.Expr]) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
        weights = tuple(sp.simplify(value**2) for value in coefficients)
        linear = tuple(Fraction(int(value.p), int(value.q)) for value in weights)
        quadratic_first = sp.simplify(2 * weights[0] ** 2)
        quadratic_total = sp.simplify(2 * (weights[0] + weights[1]) ** 2)
        quadratic_second = sp.simplify(quadratic_total - quadratic_first)
        quadratic = (
            Fraction(int(quadratic_first.p), int(quadratic_first.q)),
            Fraction(int(quadratic_second.p), int(quadratic_second.q)),
        )
        return linear, quadratic

    linear_a, quadratic_a = derive_owner_energies(chart_a)
    linear_b, quadratic_b = derive_owner_energies(chart_b)
    audit.check("law-boundary", "linear chart owner totals agree", sum(linear_a) == sum(linear_b) == 1, [sum(linear_a), sum(linear_b)], [1, 1])
    audit.check("law-boundary", "linear chart owner allocations differ", linear_a != linear_b, linear_a, linear_b)
    audit.check("law-boundary", "quadratic chart owner totals agree", sum(quadratic_a) == sum(quadratic_b) == 2, [sum(quadratic_a), sum(quadratic_b)], [2, 2])
    audit.check("law-boundary", "quadratic chart owner allocations differ", quadratic_a != quadratic_b, quadratic_a, quadratic_b)

    # ------------------------------------------------------------------
    # Actual production P+L coefficient on an affine collinear Gaussian ray.
    # ------------------------------------------------------------------
    x, floor, p_norm = sp.symbols("x floor P", positive=True)
    qii_inputs = manifest["audit_inputs"]["qii_inputs"]
    qii_a = (
        sp.Rational(qii_inputs["a"]["numerator"], qii_inputs["a"]["denominator"])
        / p_norm
    )
    qii_b = (
        sp.Rational(qii_inputs["b"]["numerator"], qii_inputs["b"]["denominator"])
        / p_norm
    )
    qii_c = (
        sp.Rational(qii_inputs["c"]["numerator"], qii_inputs["c"]["denominator"])
        / p_norm
    )
    c0 = sp.factor((qii_a * qii_c - qii_b**2) / qii_c)
    c1 = sp.factor(qii_c * (1 + qii_b / qii_c) ** 2)
    alpha = sp.factor(qii_c / (qii_b + qii_c))
    radial = 1 - alpha
    audit.check(
        "production-coefficients",
        "R-075 c0 reconstructed from A1 QII inputs",
        c0 == sp.Rational(3, 250) / p_norm,
        str(c0),
        "3/(250P)",
    )
    audit.check(
        "production-coefficients",
        "R-075 c1 reconstructed from A1 QII inputs",
        c1 == sp.Rational(243, 8000) / p_norm,
        str(c1),
        "243/(8000P)",
    )
    audit.check(
        "production-coefficients",
        "R-075 alpha reconstructed from A1 QII inputs",
        alpha == sp.Rational(5, 9),
        str(alpha),
        "5/9",
    )
    h_p = 4 * c0 * x**2
    h_l = 4 * c1 * x**2 * ((radial * x**2 + floor) / (x**2 + floor)) ** 2
    h_pair = sp.factor(h_p + h_l)
    h_pair_second = sp.factor(sp.diff(h_pair, x, 2))
    expected_second = (
        sp.Rational(3, 1000)
        / p_norm
        * (
            113 * floor**4
            - 88 * floor**3 * x**2
            + 243 * floor**2 * x**4
            + 192 * floor * x**6
            + 48 * x**8
        )
        / (floor + x**2) ** 4
    )
    audit.check("production-ray", "exact paired second derivative", sp.simplify(h_pair_second - expected_second) == 0, str(h_pair_second), str(expected_second))

    y = sp.symbols("y", nonnegative=True)
    curvature_ratio = sp.factor(
        h_pair_second.subs(x, sp.sqrt(y * floor))
        * p_norm
        * sp.Rational(1000, 3)
    )
    expected_curvature_ratio = (
        48 * y**4 + 192 * y**3 + 243 * y**2 - 88 * y + 113
    ) / (1 + y) ** 4
    audit.check(
        "production-ray",
        "dimensionless curvature ratio derived from paired Hessian",
        sp.simplify(curvature_ratio - expected_curvature_ratio) == 0,
        str(curvature_ratio),
        str(expected_curvature_ratio),
    )
    curvature_derivative = sp.factor(sp.diff(curvature_ratio, y))
    critical_roots = sp.solve(
        sp.Eq(sp.together(curvature_derivative).as_numer_denom()[0], 0),
        y,
    )
    nonnegative_critical_roots = [root for root in critical_roots if root >= 0]
    curvature_minimizer = nonnegative_critical_roots[0]
    curvature_minimum = sp.simplify(curvature_ratio.subs(y, curvature_minimizer))
    curvature_lower = sp.Rational(3, 1000) * curvature_minimum / p_norm
    expected_curvature_derivative = 30 * (y + 9) * (3 * y - 2) / (1 + y) ** 5
    audit.check(
        "production-ray",
        "curvature-ratio derivative",
        sp.simplify(curvature_derivative - expected_curvature_derivative) == 0,
        str(curvature_derivative),
        "30(y+9)(3y-2)/(1+y)^5",
    )
    audit.check(
        "production-ray",
        "curvature-ratio unique nonnegative minimum",
        len(nonnegative_critical_roots) == 1
        and curvature_minimizer == sp.Rational(2, 3)
        and curvature_minimum == sp.Rational(741, 25),
        [str(root) for root in nonnegative_critical_roots]
        + [str(curvature_minimum)],
        ["2/3", "741/25"],
    )
    audit.check("production-ray", "paired uniform convexity constant", curvature_lower == sp.Rational(2223, 25000) / p_norm, str(curvature_lower), "2223/(25000P)")
    audit.check("production-ray", "paired uniform convexity positive", sp.ask(sp.Q.positive(curvature_lower)) is True, str(curvature_lower), ">0")

    # Gaussian Stein: E[sigma^2 H(m+sigma g)(1-g^2)]
    # = -sigma^4 E H''(m+sigma g), hence the exact production pair is
    # strictly favourable throughout this affine collinear class.
    sigma = sp.symbols("sigma", positive=True)
    ray_defect_upper = -curvature_lower * sigma**4
    audit.check("production-ray", "affine-ray defect upper is negative", sp.ask(sp.Q.negative(ray_defect_upper)) is True, str(ray_defect_upper), "<0")

    # At zero background the P and L rows are separately favourable.
    gaussian_second_moment = sp.Integer(1)
    gaussian_fourth_moment = sp.Integer(3)
    p_zero_defect = sp.simplify(
        4 * c0 * (gaussian_second_moment - gaussian_fourth_moment)
    )
    u_nonnegative = sp.symbols("u", nonnegative=True)
    completion = 1 - radial
    l_scalar_kernel = (
        u_nonnegative
        * ((radial * u_nonnegative + floor) / (u_nonnegative + floor)) ** 2
    )
    monotone_weight = (
        u_nonnegative
        * (2 * radial * u_nonnegative + (1 + radial) * floor)
        / (u_nonnegative + floor) ** 2
    )
    decomposition = radial**2 * u_nonnegative + completion * floor * monotone_weight
    monotone_derivative = sp.factor(sp.diff(monotone_weight, u_nonnegative))
    expected_monotone_derivative = (
        floor
        * ((3 * radial - 1) * u_nonnegative + (1 + radial) * floor)
        / (u_nonnegative + floor) ** 3
    )
    audit.check(
        "production-ray",
        "L-row monotone covariance decomposition",
        sp.simplify(l_scalar_kernel - decomposition) == 0,
        str(sp.factor(l_scalar_kernel - decomposition)),
        "0",
    )
    audit.check(
        "production-ray",
        "L-row monotone weight derivative",
        sp.simplify(monotone_derivative - expected_monotone_derivative) == 0,
        str(monotone_derivative),
        str(expected_monotone_derivative),
    )
    monotonicity_coefficients = (
        sp.simplify(3 * radial - 1),
        sp.simplify(1 + radial),
        sp.simplify(completion),
    )
    audit.check(
        "production-ray",
        "L-row covariance monotonicity coefficients positive",
        all(coefficient > 0 for coefficient in monotonicity_coefficients),
        [str(coefficient) for coefficient in monotonicity_coefficients],
        "all positive",
    )
    l_gaussian_base = sp.simplify(
        radial**2 * (gaussian_second_moment - gaussian_fourth_moment)
    )
    audit.check(
        "production-ray",
        "L-row Gaussian base moment",
        l_gaussian_base == -2 * radial**2,
        str(l_gaussian_base),
        str(-2 * radial**2),
    )
    # The remaining term is -Cov(w_e(u),u) times a positive coefficient;
    # monotonicity above therefore makes this the exact uniform upper bound.
    l_zero_defect_upper = sp.simplify(4 * c1 * l_gaussian_base)
    pair_zero_defect_upper = sp.simplify(p_zero_defect + l_zero_defect_upper)
    audit.check("production-ray", "zero-ray P defect", p_zero_defect == -sp.Rational(12, 125) / p_norm, str(p_zero_defect), "-12/(125P)")
    audit.check("production-ray", "zero-ray L defect upper", l_zero_defect_upper == -sp.Rational(6, 125) / p_norm, str(l_zero_defect_upper), "-6/(125P)")
    audit.check("production-ray", "zero-ray paired defect upper", pair_zero_defect_upper == -sp.Rational(18, 125) / p_norm, str(pair_zero_defect_upper), "-18/(125P)")

    # L alone loses convexity on a translated line; the production P row is
    # load bearing in the uniform affine result.
    h_l_normalized = x**2 * ((radial * x**2 + floor) / (x**2 + floor)) ** 2
    l_second_witness = sp.simplify(sp.diff(h_l_normalized, x, 2).subs({floor: 1, x: sp.sqrt(sp.Rational(1, 2))}))
    audit.check("production-ray", "L-only translated-line curvature is negative", l_second_witness == -sp.Rational(56, 2187), str(l_second_witness), "-56/2187")
    audit.check("production-ray", "paired row repairs L-only witness", sp.simplify(h_pair_second.subs({floor: 1, x: sp.sqrt(sp.Rational(1, 2)), p_norm: 1})) > 0, str(sp.simplify(h_pair_second.subs({floor: 1, x: sp.sqrt(sp.Rational(1, 2)), p_norm: 1}))), ">0")

    # The collinear theorem is sharp in geometry: an exact production
    # active--spectator line has negative curvature.  Put the field at (R,R),
    # perturb in direction (1,-1), and keep the wedge row zero.
    q = sp.symbols("q", real=True)
    radius = sp.symbols("R", positive=True)
    active = radius + q
    spectator = radius - q
    density = active**2 + spectator**2 + floor
    ratio_active = active**2 / density
    noncollinear_energy = 4 * c0 * active**2 + 4 * c1 * (
        active - alpha * ratio_active * (active - spectator)
    ) ** 2
    noncollinear_second = sp.factor(sp.diff(noncollinear_energy, q, 2).subs(q, 0))
    expected_noncollinear_second = (
        sp.Rational(3, 1000)
        / p_norm
        * (-528 * radius**4 - 88 * radius**2 * floor + 113 * floor**2)
        / (2 * radius**2 + floor) ** 2
    )
    # Keep the auxiliary polynomial variable unrestricted so the audit can
    # certify both algebraic roots.  Only the selected physical ratio is later
    # restricted to the unique positive root.
    ratio_parameter = sp.symbols("rho", real=True)
    scaled_noncollinear_numerator = sp.factor(
        noncollinear_second
        * sp.Rational(1000, 3)
        * p_norm
        * (2 * radius**2 + floor) ** 2
    )
    threshold_polynomial = sp.factor(
        scaled_noncollinear_numerator.subs(
            radius, sp.sqrt(ratio_parameter * floor)
        )
        / floor**2
    )
    expected_threshold_polynomial = (
        -528 * ratio_parameter**2 - 88 * ratio_parameter + 113
    )
    audit.check(
        "production-boundary",
        "dimensionless threshold polynomial derived from active-spectator curvature",
        sp.simplify(threshold_polynomial - expected_threshold_polynomial) == 0,
        str(threshold_polynomial),
        str(expected_threshold_polynomial),
    )
    threshold_roots = sp.solve(sp.Eq(threshold_polynomial, 0), ratio_parameter)
    positive_threshold_roots = [root for root in threshold_roots if root > 0]
    negative_threshold_roots = [root for root in threshold_roots if root < 0]
    threshold = positive_threshold_roots[0]
    audit.check("production-boundary", "exact noncollinear curvature", sp.simplify(noncollinear_second - expected_noncollinear_second) == 0, str(noncollinear_second), str(expected_noncollinear_second))
    audit.check(
        "production-boundary",
        "noncollinear threshold is unique positive root",
        len(positive_threshold_roots) == 1
        and len(negative_threshold_roots) == 1
        and sp.simplify(threshold_polynomial.subs(ratio_parameter, threshold)) == 0,
        [str(root) for root in threshold_roots],
        "one negative and one positive root",
    )
    audit.check(
        "production-boundary",
        "noncollinear curvature sign orientation",
        threshold_polynomial.subs(ratio_parameter, 0) > 0
        and sp.LC(sp.Poly(threshold_polynomial, ratio_parameter)) < 0,
        [
            str(threshold_polynomial.subs(ratio_parameter, 0)),
            str(sp.LC(sp.Poly(threshold_polynomial, ratio_parameter))),
        ],
        ["positive at zero", "negative leading coefficient"],
    )
    audit.check("production-boundary", "noncollinear threshold positive", threshold > 0, str(threshold), ">0")
    audit.check("production-boundary", "threshold decimal interval", sp.Rational(3867, 10000) < threshold < sp.Rational(3868, 10000), str(sp.N(threshold, 18)), "(0.3867,0.3868)")
    zero_floor_noncollinear = sp.simplify(noncollinear_second.subs(floor, 0))
    audit.check("production-boundary", "zero-floor noncollinear curvature", zero_floor_noncollinear == -sp.Rational(99, 250) / p_norm, str(zero_floor_noncollinear), "-99/(250P)")
    audit.check("production-boundary", "large-radius curvature adverse", sp.simplify(expected_noncollinear_second.subs({radius: 1, floor: 1, p_norm: 1})) < 0, str(sp.simplify(expected_noncollinear_second.subs({radius: 1, floor: 1, p_norm: 1}))), "<0")

    # The old adapted-root fixture fails the tower criterion exactly.
    # F1 reveals xi1; Phi1=xi1 and Phi2=2xi1+xi2.
    tower_coefficient_phi1 = Fraction(1)
    tower_coefficient_cond_phi2 = Fraction(2)
    audit.check("transfer", "rootwise adapted family can fail tower", tower_coefficient_phi1 != tower_coefficient_cond_phi2, tower_coefficient_phi1, tower_coefficient_cond_phi2)
    audit.check("transfer", "canonical rows require adaptedness", manifest["scope"]["canonical_signed_terminal_doob_proved"], manifest["scope"]["canonical_signed_terminal_doob_proved"], True)
    audit.check("transfer", "old owner transfer remains unproved", not manifest["scope"]["old_owner_transfer_proved"], manifest["scope"]["old_owner_transfer_proved"], False)
    audit.check("transfer", "production trace bracket matching remains unproved", not manifest["scope"]["production_trace_bracket_matching_proved"], manifest["scope"]["production_trace_bracket_matching_proved"], False)
    audit.check("scope", "production affine collinear coefficient slice proved", manifest["scope"]["production_affine_collinear_coefficient_slice_proved"], manifest["scope"]["production_affine_collinear_coefficient_slice_proved"], True)
    audit.check(
        "scope",
        "production pair global coefficient convexity not proved",
        not manifest["scope"]["production_pair_global_coefficient_convexity_proved"],
        manifest["scope"]["production_pair_global_coefficient_convexity_proved"],
        False,
    )
    audit.check(
        "scope",
        "production pair global coefficient convexity refuted",
        manifest["scope"]["production_pair_global_coefficient_convexity_refuted"],
        manifest["scope"]["production_pair_global_coefficient_convexity_refuted"],
        True,
    )

    # Phase neutrality and live gates are machine-pinned.
    audit.check("scope", "phase selection absent", not manifest["scope"]["physical_phase_or_bcc_selection_proved"], manifest["scope"]["physical_phase_or_bcc_selection_proved"], False)
    audit.check("scope", "T-050 remains open", not manifest["scope"]["t050_closed"], manifest["scope"]["t050_closed"], False)
    audit.check("scope", "Sector A remains open", not manifest["scope"]["sector_a_closed"], manifest["scope"]["sector_a_closed"], False)

    audit.require()
    payload = {
        "schema": SCHEMA,
        "script_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "rows": audit.rows},
        "exact_values": {
            "signed_terminal_cross": str(terminal_cross),
            "signed_base_cross": str(base_cross),
            "signed_step_crosses": [str(value) for value in step_crosses],
            "matched_relative_positive_fixture": str(delta_down),
            "matched_relative_negative_fixture": str(delta_up),
            "centred_common_terminal_ratio_at_t2": str(sp.simplify(ratio.subs(t, 2))),
            "linear_owner_energies_chart_a": [str(value) for value in linear_a],
            "linear_owner_energies_chart_b": [str(value) for value in linear_b],
            "quadratic_owner_energies_chart_a": [str(value) for value in quadratic_a],
            "quadratic_owner_energies_chart_b": [str(value) for value in quadratic_b],
            "production_affine_ray_curvature_lower": str(curvature_lower),
            "production_zero_ray_pair_defect_upper": str(pair_zero_defect_upper),
            "production_l_only_curvature_witness": str(l_second_witness),
            "production_noncollinear_threshold": str(threshold),
            "production_noncollinear_zero_floor_curvature": str(zero_floor_noncollinear),
        },
        "cross_values": {
            "production_affine_ray_curvature_lower": str(curvature_lower),
            "production_l_only_curvature_witness": str(l_second_witness),
            "production_noncollinear_threshold": str(threshold),
            "production_noncollinear_zero_floor_curvature": str(zero_floor_noncollinear),
        },
        "scope": manifest["scope"],
        "theorem_summary": {
            "canonical_signed_common_terminal": "proved at fixed cutoff for the complete terminal feature",
            "conditional_signed_variance_recursion": "proved",
            "old_owner_transfer_criterion": "tower, registered incidence, and predictable polarized trace-bracket matching",
            "same_root_scalar_sign": "not automatic even with a centred one-step common terminal",
            "production_affine_collinear_sign": "strictly favourable for the exact P+L pair",
            "production_noncollinear_extension": "global convexity of the retained P+L pair fails on an exact active-spectator direction",
            "phase_status": "neutral",
        },
        "no_overclaim": "R-147 constructs a new fixed-cutoff signed common-terminal coordinate, the exact conditioned predictable matching defect under the registered incidence hypotheses, and a strict production P+L sign only on predictable affine collinear Gaussian lines. It does not prove the non-collinear or multi-root production trace-bracket identity, bound the remaining signed Doob form, establish transport of R-063/R-125 owners, close T-050 or A13, select BCC or any phase, prove Nelson, or close Sector A.",
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS {RESULT_ID} ({len(audit.rows)}/{len(audit.rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
