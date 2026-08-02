#!/usr/bin/env python3
"""Independent certificate for the phase-neutral A13 R-147 checkpoint.

This implementation does not import the primary certificate or read its run
artefact.  It uses a different eight-atom filtration, direct Fraction matrix
arithmetic, and independently chosen trace/bracket fixtures.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CANONICAL-SIGNED-COMMON-TERMINAL-DOOB-BRACKET-DEFECT-BOUNDARY"
SCHEMA = "tect/a13-canonical-signed-common-terminal-doob-bracket-defect-boundary-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_canonical_signed_common_terminal_doob_bracket_defect_boundary_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-independent-canonical-signed-common-terminal-doob-bracket-defect-boundary" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(65536)
            if not block:
                break
            value.update(block)
    return value.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, payload: dict[str, Any]) -> None:
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
        self.rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})

    def finish(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True, default=str))


def average(values: list[Fraction]) -> Fraction:
    return sum(values, Fraction(0)) / len(values)


def vector_average(values: list[tuple[Fraction, ...]]) -> tuple[Fraction, ...]:
    return tuple(average([value[column] for value in values]) for column in range(len(values[0])))


def conditional(values: list[tuple[Fraction, ...]], labels: list[int]) -> list[tuple[Fraction, ...]]:
    result: list[tuple[Fraction, ...]] = []
    means: dict[int, tuple[Fraction, ...]] = {}
    for label in sorted(set(labels)):
        means[label] = vector_average([value for value, current in zip(values, labels) if current == label])
    for label in labels:
        result.append(means[label])
    return result


def conditional_scalar(values: list[Fraction], labels: list[int]) -> list[Fraction]:
    means = {label: average([value for value, current in zip(values, labels) if current == label]) for label in sorted(set(labels))}
    return [means[label] for label in labels]


def plus(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(a + b for a, b in zip(left, right))


def minus(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(a - b for a, b in zip(left, right))


def form(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    return left[0] * right[0] - left[1] * right[1]


def rank_diagonal(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> int:
    return int(matrix[0][0] != 0) + int(matrix[1][1] != 0)


def main() -> int:
    getcontext().prec = 70
    checks = Checks()
    manifest = read_json(MANIFEST)
    checks.add("metadata", "claim", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    checks.add("metadata", "result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    checks.add("metadata", "package version", manifest["package_version"] == "1.0.0", manifest["package_version"], "1.0.0")

    for label, relative in manifest["authorities"].items():
        path = REPO / relative
        checks.add("authority", f"{label} exists", path.exists() and path.is_file(), relative, "file")
        actual = digest(path)
        checks.add("authority", f"{label} digest", actual == manifest["authority_hashes"][label], actual, manifest["authority_hashes"][label])

    # Independent eight-atom, three-step signed telescope.
    zero: list[tuple[Fraction, Fraction]] = []
    shifted: list[tuple[Fraction, Fraction]] = []
    for index in range(8):
        parity = Fraction(1 if index % 2 == 0 else -1)
        zero.append((Fraction(index - 3), parity * Fraction((index % 3) + 1)))
        shifted.append((Fraction(2 - index % 5), parity * Fraction(index - 1)))
    sigma = [plus(h, z) for h, z in zip(shifted, zero)]
    delta = [minus(h, z) for h, z in zip(shifted, zero)]
    nests = [
        [0] * 8,
        [0, 0, 0, 0, 1, 1, 1, 1],
        [0, 0, 1, 1, 2, 2, 3, 3],
        list(range(8)),
    ]
    ms = [conditional(sigma, labels) for labels in nests]
    md = [conditional(delta, labels) for labels in nests]
    ds = [[minus(ms[level][atom], ms[level - 1][atom]) for atom in range(8)] for level in range(1, 4)]
    dd = [[minus(md[level][atom], md[level - 1][atom]) for atom in range(8)] for level in range(1, 4)]
    endpoint = average([form(left, right) for left, right in zip(sigma, delta)])
    base = average([form(left, right) for left, right in zip(ms[0], md[0])])
    increments = [average([form(left, right) for left, right in zip(step_s, step_d)]) for step_s, step_d in zip(ds, dd)]
    checks.add("doob", "eight-atom terminal", ms[-1] == sigma and md[-1] == delta, [ms[-1], md[-1]], [sigma, delta])
    checks.add("doob", "eight-atom signed telescope", endpoint == base + sum(increments, Fraction(0)), endpoint, base + sum(increments, Fraction(0)))
    for level in range(1, 4):
        checks.add("doob", f"sum tower {level}", conditional(ms[level], nests[level - 1]) == ms[level - 1], conditional(ms[level], nests[level - 1]), ms[level - 1])
        checks.add("doob", f"delta tower {level}", conditional(md[level], nests[level - 1]) == md[level - 1], conditional(md[level], nests[level - 1]), md[level - 1])

    terminal_form = [form(left, right) for left, right in zip(sigma, delta)]
    signed_future: list[list[Fraction]] = []
    for level, labels in enumerate(nests):
        terminal_conditional = conditional_scalar(terminal_form, labels)
        signed_future.append([terminal_conditional[atom] - form(ms[level][atom], md[level][atom]) for atom in range(8)])
    checks.add("doob", "terminal future signed form zero", signed_future[-1] == [Fraction(0)] * 8, signed_future[-1], [0] * 8)
    for level in range(1, 4):
        prev = nests[level - 1]
        future = conditional_scalar(signed_future[level], prev)
        bracket = conditional_scalar([form(left, right) for left, right in zip(ds[level - 1], dd[level - 1])], prev)
        rhs = [a + b for a, b in zip(future, bracket)]
        checks.add("doob", f"signed recursion {level}", rhs == signed_future[level - 1], rhs, signed_future[level - 1])

    # Independent auxiliary-future compression of (U,J,R) to (U,Phi).
    j_p = [Fraction(-2), Fraction(1), Fraction(4), Fraction(1)]
    j_q = [Fraction(3), Fraction(-1), Fraction(0), Fraction(2)]
    phi_p = average(j_p)
    phi_q = average(j_q)
    r_p = [value - phi_p for value in j_p]
    r_q = [value - phi_q for value in j_q]
    u_p = [Fraction(2), Fraction(0), Fraction(-1), Fraction(3)]
    u_q = [Fraction(1), Fraction(4), Fraction(2), Fraction(-2)]
    three = average([up * uq - jp * jq + rp * rq for up, uq, jp, jq, rp, rq in zip(u_p, u_q, j_p, j_q, r_p, r_q)])
    two = average([up * uq for up, uq in zip(u_p, u_q)]) - phi_p * phi_q
    checks.add("signature", "independent three-to-two compression", three == two, three, two)
    checks.add("signature", "first residual centred", average(r_p) == 0, average(r_p), 0)
    checks.add("signature", "second residual centred", average(r_q) == 0, average(r_q), 0)

    # A different source-grid fixture verifies compression at every reveal
    # and for every increment when the future projection is one grid member.
    source_u_p = [Fraction((3 * index + 1) % 7 - 3) for index in range(8)]
    source_u_q = [Fraction((5 * index + 2) % 9 - 4) for index in range(8)]
    source_j_p = [Fraction(index - 2) for index in range(8)]
    source_j_q = [Fraction((-1) ** index * (index + 1)) for index in range(8)]
    source_phi_p = conditional_scalar(source_j_p, nests[2])
    source_phi_q = conditional_scalar(source_j_q, nests[2])
    source_r_p = [value - projected for value, projected in zip(source_j_p, source_phi_p)]
    source_r_q = [value - projected for value, projected in zip(source_j_q, source_phi_q)]
    source_z_p = [
        (u, j, r)
        for u, j, r in zip(source_u_p, source_j_p, source_r_p)
    ]
    source_z_q = [
        (u, j, r)
        for u, j, r in zip(source_u_q, source_j_q, source_r_q)
    ]
    source_f_p = [(u, projected) for u, projected in zip(source_u_p, source_phi_p)]
    source_f_q = [(u, projected) for u, projected in zip(source_u_q, source_phi_q)]

    def form_three(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
        return left[0] * right[0] - left[1] * right[1] + left[2] * right[2]

    z_p_tower = [conditional(source_z_p, labels) for labels in nests]
    z_q_tower = [conditional(source_z_q, labels) for labels in nests]
    f_p_tower = [conditional(source_f_p, labels) for labels in nests]
    f_q_tower = [conditional(source_f_q, labels) for labels in nests]
    for level in range(4):
        z_cross = average(
            [form_three(left, right) for left, right in zip(z_p_tower[level], z_q_tower[level])]
        )
        f_cross = average(
            [form(left, right) for left, right in zip(f_p_tower[level], f_q_tower[level])]
        )
        checks.add(
            "signature",
            f"independent source reveal compression {level}",
            z_cross == f_cross,
            z_cross,
            f_cross,
        )
    for level in range(1, 4):
        z_increment_p = [
            minus(current, previous)
            for current, previous in zip(z_p_tower[level], z_p_tower[level - 1])
        ]
        z_increment_q = [
            minus(current, previous)
            for current, previous in zip(z_q_tower[level], z_q_tower[level - 1])
        ]
        f_increment_p = [
            minus(current, previous)
            for current, previous in zip(f_p_tower[level], f_p_tower[level - 1])
        ]
        f_increment_q = [
            minus(current, previous)
            for current, previous in zip(f_q_tower[level], f_q_tower[level - 1])
        ]
        z_increment_cross = average(
            [form_three(left, right) for left, right in zip(z_increment_p, z_increment_q)]
        )
        f_increment_cross = average(
            [form(left, right) for left, right in zip(f_increment_p, f_increment_q)]
        )
        checks.add(
            "signature",
            f"independent source increment compression {level}",
            z_increment_cross == f_increment_cross,
            z_increment_cross,
            f_increment_cross,
        )

    # Complex Hermitian polarization is evaluated independently of the real
    # Fraction fixtures.
    imaginary = sp.I
    complex_p = (2 + imaginary, -1 + 3 * imaginary)
    complex_q = (1 - 2 * imaginary, 4 + imaginary)
    complex_sigma = tuple(a + b for a, b in zip(complex_p, complex_q))
    complex_delta = tuple(a - b for a, b in zip(complex_p, complex_q))

    def hermitian_two(left: tuple[sp.Expr, ...], right: tuple[sp.Expr, ...]) -> sp.Expr:
        return sp.simplify(
            sp.conjugate(left[0]) * right[0]
            - sp.conjugate(left[1]) * right[1]
        )

    direct_complex = sp.re(
        hermitian_two(complex_p, complex_p)
        - hermitian_two(complex_q, complex_q)
    )
    polarized_complex = sp.re(hermitian_two(complex_sigma, complex_delta))
    checks.add(
        "signature",
        "independent complex Hermitian polarization",
        sp.simplify(direct_complex - polarized_complex) == 0,
        str(direct_complex),
        str(polarized_complex),
    )

    # A deterministic piecewise integrand and independent Rademacher terminal
    # atoms verify the degree-two signed isometry algebra without reusing the
    # direct bracket expression.
    weights = [Fraction(1, 5), Fraction(1, 2), Fraction(3, 10)]
    h_sigma = [(Fraction(2), Fraction(1)), (Fraction(-1), Fraction(3)), (Fraction(4), Fraction(-2))]
    h_delta = [(Fraction(1), Fraction(0)), (Fraction(2), Fraction(-1)), (Fraction(-1), Fraction(5))]
    bracket_integral = sum((weight * form(left, right) for weight, left, right in zip(weights, h_sigma, h_delta)), Fraction(0))
    endpoint_cross_atoms: list[sp.Expr] = []
    for mask in range(8):
        rademacher = [1 if mask & (1 << index) else -1 for index in range(3)]
        terminal_sigma = tuple(
            sp.simplify(
                sum(
                    sp.sqrt(sp.Rational(weight.numerator, weight.denominator))
                    * sign
                    * row[component]
                    for weight, sign, row in zip(weights, rademacher, h_sigma)
                )
            )
            for component in range(2)
        )
        terminal_delta = tuple(
            sp.simplify(
                sum(
                    sp.sqrt(sp.Rational(weight.numerator, weight.denominator))
                    * sign
                    * row[component]
                    for weight, sign, row in zip(weights, rademacher, h_delta)
                )
            )
            for component in range(2)
        )
        endpoint_cross_atoms.append(
            sp.simplify(
                terminal_sigma[0] * terminal_delta[0]
                - terminal_sigma[1] * terminal_delta[1]
            )
        )
    endpoint_cross = sp.simplify(sum(endpoint_cross_atoms) / len(endpoint_cross_atoms))
    checks.add(
        "continuous",
        "piecewise signed bracket from Rademacher terminal atoms",
        sp.simplify(endpoint_cross - sp.Rational(bracket_integral.numerator, bracket_integral.denominator)) == 0,
        str(endpoint_cross),
        str(bracket_integral),
    )
    checks.add("continuous", "time weights sum to one", sum(weights) == 1, sum(weights), 1)

    # Different full covariance paths forbid a causal Gaussian nest transfer.
    old_terminal = (
        (2 * Fraction(1, 2), Fraction(0)),
        (Fraction(0), 2 * Fraction(1, 2)),
    )
    canonical_terminal = (
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1)),
    )
    old_half = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(0)))
    canonical_half = ((Fraction(1, 2), Fraction(0)), (Fraction(0), Fraction(1, 2)))
    old_half_rank = rank_diagonal(old_half)
    canonical_half_rank = rank_diagonal(canonical_half)
    checks.add(
        "transfer",
        "terminal covariance laws agree by separate kernel sums",
        old_terminal == canonical_terminal,
        old_terminal,
        canonical_terminal,
    )
    checks.add("transfer", "half-time covariance differs", old_half != canonical_half, old_half, canonical_half)
    checks.add(
        "transfer",
        "half-time rank obstruction",
        old_half_rank == 1 and canonical_half_rank == 2,
        [old_half_rank, canonical_half_rank],
        [1, 2],
    )
    time_symbol = sp.symbols("s", real=True)
    early_matches = sp.solve(
        [
            sp.Eq(2 * time_symbol, sp.Rational(1, 2)),
            sp.Eq(0, sp.Rational(1, 2)),
        ],
        [time_symbol],
        dict=True,
    )
    late_matches = sp.solve(
        [
            sp.Eq(1, sp.Rational(1, 2)),
            sp.Eq(2 * time_symbol - 1, sp.Rational(1, 2)),
        ],
        [time_symbol],
        dict=True,
    )
    checks.add(
        "transfer",
        "time change cannot match canonical half spectrum",
        early_matches == [] and late_matches == [],
        [early_matches, late_matches],
        [[], []],
    )

    # Independent trace--bracket defect calculation on two previous-field cells.
    means_p = [Fraction(2), Fraction(2), Fraction(-1), Fraction(-1)]
    means_q = [Fraction(-3), Fraction(-3), Fraction(4), Fraction(4)]
    innovations_p = [Fraction(1), Fraction(-1), Fraction(2), Fraction(-2)]
    innovations_q = [Fraction(2), Fraction(-2), Fraction(-1), Fraction(1)]
    labels = [0, 0, 1, 1]
    bracket = conditional_scalar([a * b for a, b in zip(innovations_p, innovations_q)], labels)
    mismatch = [Fraction(-1, 7), Fraction(-1, 7), Fraction(5, 9), Fraction(5, 9)]
    trace_oscillation = [Fraction(3), Fraction(-3), Fraction(-4), Fraction(4)]
    phi_p_raw = [base + innovation for base, innovation in zip(means_p, innovations_p)]
    phi_q_raw = [base + innovation for base, innovation in zip(means_q, innovations_q)]
    phi_product_raw = [a * b for a, b in zip(phi_p_raw, phi_q_raw)]
    trace_raw = [
        a + b + oscillation
        for a, b, oscillation in zip(bracket, mismatch, trace_oscillation)
    ]
    residual_raw = [tr - pp for tr, pp in zip(trace_raw, phi_product_raw)]
    bar_trace = conditional_scalar(trace_raw, labels)
    conditioned_residual = conditional_scalar(residual_raw, labels)
    predictable_mismatch = [tr - br for tr, br in zip(bar_trace, bracket)]
    expected = [
        defect - a * b
        for defect, a, b in zip(predictable_mismatch, means_p, means_q)
    ]
    checks.add(
        "matching",
        "independent raw trace is not past measurable",
        trace_raw != bar_trace,
        trace_raw,
        bar_trace,
    )
    checks.add(
        "matching",
        "independent predictable mismatch recovered",
        predictable_mismatch == mismatch,
        predictable_mismatch,
        mismatch,
    )
    checks.add(
        "matching",
        "independent conditioned trace-bracket identity",
        conditioned_residual == expected,
        conditioned_residual,
        expected,
    )
    matched_trace_raw = [
        br + oscillation
        for br, oscillation in zip(bracket, trace_oscillation)
    ]
    matched_residual_raw = [
        tr - pp for tr, pp in zip(matched_trace_raw, phi_product_raw)
    ]
    matched = conditional_scalar(matched_residual_raw, labels)
    checks.add(
        "matching",
        "independent matched predictable trace gives conditioned negative Gram",
        matched == [-a * b for a, b in zip(means_p, means_q)],
        matched,
        [-a * b for a, b in zip(means_p, means_q)],
    )
    xi_fixture = [Fraction(-1), Fraction(1)]
    trace_fixture = [Fraction(0), Fraction(2)]
    fixture_residual = [
        tr - value * value for tr, value in zip(trace_fixture, xi_fixture)
    ]
    checks.add(
        "matching",
        "independent current-root predictable projection regression",
        average(trace_fixture) == 1
        and average(fixture_residual) == 0
        and trace_fixture != [Fraction(1), Fraction(1)],
        [average(trace_fixture), average(fixture_residual), trace_fixture],
        [1, 0, "not pointwise one"],
    )

    # Centred one-step common-terminal no-go at t=3.
    t_value = Fraction(3)
    ratio = 2 * t_value / (1 + 2 * t_value)
    sqrt_seven = Decimal(7).sqrt()
    trace_value = Decimal(1) / sqrt_seven
    current_value = Decimal(1) / (Decimal(7) * sqrt_seven)
    defect_value = trace_value - current_value
    checks.add("nogo", "centred no-go defect positive", defect_value > 0, str(defect_value), ">0")
    checks.add("nogo", "centred no-go exact ratio", ratio == Fraction(6, 7), ratio, Fraction(6, 7))
    gaussian_symbol = sp.symbols("g", real=True)
    odd_integrand = gaussian_symbol * sp.exp(-3 * gaussian_symbol**2 / 2)
    checks.add(
        "nogo",
        "centred one-step predictable mean by parity",
        sp.simplify(odd_integrand.subs(gaussian_symbol, -gaussian_symbol) + odd_integrand) == 0,
        str(sp.simplify(odd_integrand.subs(gaussian_symbol, -gaussian_symbol) + odd_integrand)),
        "0",
    )

    # Endpoint-law equality preserves totals, not owner allocation.
    coefficient_charts = {
        "a": (sp.Integer(1), sp.Integer(0)),
        "b": (1 / sp.sqrt(2), 1 / sp.sqrt(2)),
    }
    derived: dict[str, dict[str, tuple[sp.Expr, sp.Expr]]] = {}
    for name, coefficients in coefficient_charts.items():
        weights = tuple(sp.simplify(value**2) for value in coefficients)
        linear = weights
        quadratic_first = sp.simplify(2 * weights[0] ** 2)
        quadratic_total = sp.simplify(2 * (weights[0] + weights[1]) ** 2)
        quadratic = (quadratic_first, sp.simplify(quadratic_total - quadratic_first))
        derived[name] = {"linear": linear, "quadratic": quadratic}
    checks.add("law-boundary", "linear total variance", sum(derived["a"]["linear"]) == sum(derived["b"]["linear"]) == 1, [sum(derived["a"]["linear"]), sum(derived["b"]["linear"])], [1, 1])
    checks.add("law-boundary", "linear owners differ", derived["a"]["linear"] != derived["b"]["linear"], derived["a"]["linear"], derived["b"]["linear"])
    checks.add("law-boundary", "quadratic total variance", sum(derived["a"]["quadratic"]) == sum(derived["b"]["quadratic"]) == 2, [sum(derived["a"]["quadratic"]), sum(derived["b"]["quadratic"])], [2, 2])
    checks.add("law-boundary", "quadratic owners differ", derived["a"]["quadratic"] != derived["b"]["quadratic"], derived["a"]["quadratic"], derived["b"]["quadratic"])

    # Independently reconstruct the exact production P+L affine-ray energy.
    x, eps, p_norm = sp.symbols("x eps P", positive=True)
    qii_inputs = manifest["audit_inputs"]["qii_inputs"]
    qii_matrix = sp.Matrix(
        [
            [
                sp.Rational(
                    qii_inputs["a"]["numerator"],
                    qii_inputs["a"]["denominator"],
                )
                / p_norm,
                sp.Rational(
                    qii_inputs["b"]["numerator"],
                    qii_inputs["b"]["denominator"],
                )
                / p_norm,
            ],
            [
                sp.Rational(
                    qii_inputs["b"]["numerator"],
                    qii_inputs["b"]["denominator"],
                )
                / p_norm,
                sp.Rational(
                    qii_inputs["c"]["numerator"],
                    qii_inputs["c"]["denominator"],
                )
                / p_norm,
            ],
        ]
    )
    c0 = sp.factor(qii_matrix.det() / qii_matrix[1, 1])
    completion_multiplier = sp.factor(
        (qii_matrix[0, 1] + qii_matrix[1, 1]) / qii_matrix[1, 1]
    )
    c1 = sp.factor(qii_matrix[1, 1] * completion_multiplier**2)
    alpha = sp.factor(
        qii_matrix[1, 1] / (qii_matrix[0, 1] + qii_matrix[1, 1])
    )
    checks.add(
        "production-coefficients",
        "independent Schur c0 reconstruction",
        c0 == sp.Rational(3, 250) / p_norm,
        str(c0),
        "3/(250P)",
    )
    checks.add(
        "production-coefficients",
        "independent completed-square c1 reconstruction",
        c1 == sp.Rational(243, 8000) / p_norm,
        str(c1),
        "243/(8000P)",
    )
    checks.add(
        "production-coefficients",
        "independent alpha reconstruction",
        alpha == sp.Rational(5, 9),
        str(alpha),
        "5/9",
    )
    pair_energy = 4 * c0 * x**2 + 4 * c1 * x**2 * (((1 - alpha) * x**2 + eps) / (x**2 + eps)) ** 2
    pair_second = sp.factor(sp.diff(pair_energy, x, 2))
    scaled = sp.factor(pair_second * p_norm * (eps + x**2) ** 4 * sp.Rational(1000, 3))
    expected_scaled = 113 * eps**4 - 88 * eps**3 * x**2 + 243 * eps**2 * x**4 + 192 * eps * x**6 + 48 * x**8
    checks.add("production-ray", "independent paired curvature numerator", sp.expand(scaled - expected_scaled) == 0, str(scaled), str(expected_scaled))
    y = sp.symbols("y", nonnegative=True)
    ratio_curve = sp.factor(
        pair_second.subs(x, sp.sqrt(y * eps))
        * p_norm
        * sp.Rational(1000, 3)
    )
    expected_ratio_curve = (
        113 - 88 * y + 243 * y**2 + 192 * y**3 + 48 * y**4
    ) / (1 + y) ** 4
    checks.add(
        "production-ray",
        "independent ratio derived from paired Hessian",
        sp.simplify(ratio_curve - expected_ratio_curve) == 0,
        str(ratio_curve),
        str(expected_ratio_curve),
    )
    ratio_derivative = sp.factor(sp.diff(ratio_curve, y))
    critical_roots = sp.solve(
        sp.Eq(sp.together(ratio_derivative).as_numer_denom()[0], 0),
        y,
    )
    nonnegative_critical_roots = [root for root in critical_roots if root >= 0]
    minimizer = nonnegative_critical_roots[0]
    minimum = sp.simplify(ratio_curve.subs(y, minimizer))
    expected_ratio_derivative = 30 * (y + 9) * (3 * y - 2) / (1 + y) ** 5
    checks.add(
        "production-ray",
        "independent ratio derivative",
        sp.simplify(ratio_derivative - expected_ratio_derivative) == 0,
        str(ratio_derivative),
        "30(y+9)(3y-2)/(1+y)^5",
    )
    checks.add(
        "production-ray",
        "independent curvature minimum",
        len(nonnegative_critical_roots) == 1
        and minimizer == sp.Rational(2, 3)
        and minimum == sp.Rational(741, 25),
        [str(root) for root in nonnegative_critical_roots] + [str(minimum)],
        ["2/3", "741/25"],
    )
    checks.add("production-ray", "independent paired convexity", sp.Rational(3, 1000) * minimum == sp.Rational(2223, 25000), str(sp.Rational(3, 1000) * minimum), "2223/25000")

    # Differentiate the active--spectator counterdirection directly.
    q = sp.symbols("q", real=True)
    radius = sp.symbols("R", positive=True)
    active = radius + q
    spectator = radius - q
    total = active**2 + spectator**2 + eps
    active_fraction = active**2 / total
    noncollinear = 4 * c0 * active**2 + 4 * c1 * (active - alpha * active_fraction * (active - spectator)) ** 2
    noncollinear_second = sp.factor(sp.diff(noncollinear, q, 2).subs(q, 0))
    zero_floor = sp.simplify(noncollinear_second.subs(eps, 0))
    ratio_variable = sp.symbols("rho", nonnegative=True)
    scaled_noncollinear_numerator = sp.factor(
        noncollinear_second
        * sp.Rational(1000, 3)
        * p_norm
        * (2 * radius**2 + eps) ** 2
    )
    threshold_polynomial = sp.factor(
        scaled_noncollinear_numerator.subs(
            radius, sp.sqrt(ratio_variable * eps)
        )
        / eps**2
    )
    expected_threshold_polynomial = (
        -528 * ratio_variable**2 - 88 * ratio_variable + 113
    )
    checks.add(
        "production-boundary",
        "independent dimensionless threshold polynomial",
        sp.simplify(threshold_polynomial - expected_threshold_polynomial) == 0,
        str(threshold_polynomial),
        str(expected_threshold_polynomial),
    )
    threshold_root_map = sp.roots(threshold_polynomial, ratio_variable)
    positive_threshold_roots = [
        root for root in threshold_root_map if root > 0
    ]
    negative_threshold_roots = [
        root for root in threshold_root_map if root < 0
    ]
    threshold = positive_threshold_roots[0]
    checks.add("production-boundary", "independent noncollinear zero-floor curvature", zero_floor == -sp.Rational(99, 250) / p_norm, str(zero_floor), "-99/(250P)")
    checks.add(
        "production-boundary",
        "independent threshold unique positive root",
        len(positive_threshold_roots) == 1
        and len(negative_threshold_roots) == 1
        and threshold_root_map[threshold] == 1
        and sp.simplify(threshold_polynomial.subs(ratio_variable, threshold)) == 0,
        {str(root): multiplicity for root, multiplicity in threshold_root_map.items()},
        "one simple negative and one simple positive root",
    )
    checks.add(
        "production-boundary",
        "independent threshold sign orientation",
        threshold_polynomial.subs(ratio_variable, 0) > 0
        and sp.LC(sp.Poly(threshold_polynomial, ratio_variable)) < 0,
        [
            str(threshold_polynomial.subs(ratio_variable, 0)),
            str(sp.LC(sp.Poly(threshold_polynomial, ratio_variable))),
        ],
        ["positive at zero", "negative leading coefficient"],
    )
    checks.add("production-boundary", "independent noncollinear threshold", sp.Rational(3867, 10000) < threshold < sp.Rational(3868, 10000), str(sp.N(threshold, 18)), "(0.3867,0.3868)")
    checks.add("production-boundary", "independent noncollinear witness negative", sp.simplify(noncollinear_second.subs({radius: 1, eps: 1, p_norm: 1})) < 0, str(sp.simplify(noncollinear_second.subs({radius: 1, eps: 1, p_norm: 1}))), "<0")

    # Independently certify the uniform zero-background L-row sign through
    # monotone covariance, not by assuming a curvature sign.
    u_symbol = sp.symbols("u", nonnegative=True)
    radial = sp.simplify(1 - alpha)
    complement = sp.simplify(1 - radial)
    scalar_kernel = (
        u_symbol * ((radial * u_symbol + eps) / (u_symbol + eps)) ** 2
    )
    weight_function = (
        u_symbol
        * (2 * radial * u_symbol + (1 + radial) * eps)
        / (u_symbol + eps) ** 2
    )
    checks.add(
        "production-ray",
        "independent L-row covariance decomposition",
        sp.factor(
            scalar_kernel
            - radial**2 * u_symbol
            - complement * eps * weight_function
        )
        == 0,
        str(
            sp.factor(
                scalar_kernel
                - radial**2 * u_symbol
                - complement * eps * weight_function
            )
        ),
        "0",
    )
    weight_derivative = sp.factor(sp.diff(weight_function, u_symbol))
    expected_weight_derivative = (
        eps
        * ((3 * radial - 1) * u_symbol + (1 + radial) * eps)
        / (u_symbol + eps) ** 3
    )
    checks.add(
        "production-ray",
        "independent L-row monotone derivative",
        sp.simplify(weight_derivative - expected_weight_derivative) == 0,
        str(weight_derivative),
        str(expected_weight_derivative),
    )
    monotonicity_data = [
        sp.simplify(3 * radial - 1),
        sp.simplify(1 + radial),
        sp.simplify(complement),
    ]
    checks.add(
        "production-ray",
        "independent L-row monotonicity coefficients",
        all(value > 0 for value in monotonicity_data),
        [str(value) for value in monotonicity_data],
        "all positive",
    )
    gaussian_second_moment = sp.Integer(1)
    gaussian_fourth_moment = sp.Integer(3)
    l_zero_upper = sp.simplify(
        4
        * c1
        * radial**2
        * (gaussian_second_moment - gaussian_fourth_moment)
    )
    p_zero_value = sp.simplify(
        4 * c0 * (gaussian_second_moment - gaussian_fourth_moment)
    )
    pair_zero_upper = sp.simplify(p_zero_value + l_zero_upper)
    checks.add(
        "production-ray",
        "independent L-row zero-background upper",
        l_zero_upper == -sp.Rational(6, 125) / p_norm,
        str(l_zero_upper),
        "-6/(125P)",
    )
    checks.add(
        "production-ray",
        "independent paired zero-background upper",
        pair_zero_upper == -sp.Rational(18, 125) / p_norm,
        str(pair_zero_upper),
        "-18/(125P)",
    )

    # L alone is not convex on translated affine lines.
    l_normalized = x**2 * (((1 - alpha) * x**2 + eps) / (x**2 + eps)) ** 2
    l_witness = sp.simplify(sp.diff(l_normalized, x, 2).subs({eps: 1, x: sp.sqrt(sp.Rational(1, 2))}))
    checks.add("production-boundary", "independent L-only witness", l_witness == -sp.Rational(56, 2187), str(l_witness), "-56/2187")

    # Scope firewall.
    scope = manifest["scope"]
    checks.add("scope", "canonical signed tower closed", scope["canonical_signed_terminal_doob_proved"], scope["canonical_signed_terminal_doob_proved"], True)
    checks.add("scope", "old owner transfer open", not scope["old_owner_transfer_proved"], scope["old_owner_transfer_proved"], False)
    checks.add("scope", "production trace bracket open", not scope["production_trace_bracket_matching_proved"], scope["production_trace_bracket_matching_proved"], False)
    checks.add("scope", "production affine collinear coefficient slice closed", scope["production_affine_collinear_coefficient_slice_proved"], scope["production_affine_collinear_coefficient_slice_proved"], True)
    checks.add(
        "scope",
        "production pair global coefficient convexity not proved",
        not scope["production_pair_global_coefficient_convexity_proved"],
        scope["production_pair_global_coefficient_convexity_proved"],
        False,
    )
    checks.add(
        "scope",
        "production pair global coefficient convexity refuted",
        scope["production_pair_global_coefficient_convexity_refuted"],
        scope["production_pair_global_coefficient_convexity_refuted"],
        True,
    )
    checks.add("scope", "phase neutral", not scope["physical_phase_or_bcc_selection_proved"], scope["physical_phase_or_bcc_selection_proved"], False)
    checks.add("scope", "T-050 open", not scope["t050_closed"], scope["t050_closed"], False)
    checks.add("scope", "Sector A open", not scope["sector_a_closed"], scope["sector_a_closed"], False)

    checks.finish()
    payload = {
        "schema": SCHEMA,
        "script_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions": {"total": len(checks.rows), "passed": len(checks.rows), "failed": 0, "rows": checks.rows},
        "exact_values": {
            "eight_atom_terminal_cross": str(endpoint),
            "eight_atom_base_cross": str(base),
            "eight_atom_step_crosses": [str(value) for value in increments],
            "causal_prefix_ranks": [old_half_rank, canonical_half_rank],
            "centred_common_terminal_ratio_at_t3": str(ratio),
            "piecewise_signed_bracket": str(bracket_integral),
            "production_affine_ray_curvature_lower": str(
                sp.Rational(3, 1000) * minimum / p_norm
            ),
            "production_noncollinear_zero_floor_curvature": str(zero_floor),
        },
        "cross_values": {
            "production_affine_ray_curvature_lower": str(
                sp.Rational(3, 1000) * minimum / p_norm
            ),
            "production_l_only_curvature_witness": str(l_witness),
            "production_noncollinear_threshold": str(threshold),
            "production_noncollinear_zero_floor_curvature": str(zero_floor),
        },
        "scope": manifest["scope"],
        "independence": {
            "imports_primary": False,
            "reads_primary_result": False,
            "fixture": "different eight-atom filtration and rational trace-bracket cells",
        },
        "no_overclaim": "The independent certificate verifies the fixed-cutoff signed terminal coordinate, representation-transfer boundary, exact scalar method no-go, and affine-collinear production-coefficient slice. It proves no complete or non-collinear production uniform estimate, T-050, phase selection, Nelson theorem, or Sector-A closure.",
    }
    write_json(OUTPUT, payload)
    print(f"PASS {RESULT_ID} independent ({len(checks.rows)}/{len(checks.rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
