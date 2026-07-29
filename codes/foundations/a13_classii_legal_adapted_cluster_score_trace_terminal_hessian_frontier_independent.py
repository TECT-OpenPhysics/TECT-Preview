#!/usr/bin/env python3
"""Non-importing exact audit for the scoped R-119 A13 proof frontier.

This implementation uses only the standard library, exact fractions, and
small polynomial/matrix routines.  It does not import SymPy or the primary
certificate.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LEGAL-ADAPTED-CLUSTER-SCORE-TRACE-TERMINAL-HESSIAN-FRONTIER"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-29-independent-legal-adapted-cluster-score-trace-terminal-hessian-frontier/result.json"
)
R102_RESULT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-28-primary-full-hessian-laplace-wick-future-feedback-boundary/result.json"
)
SCHEMA = "tect/a13-legal-adapted-cluster-score-trace-terminal-hessian-frontier-independent/1.0"


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
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
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "This non-importing audit checks exact R-119 fixtures and polynomial "
                "identities. It does not certify the full production A1 coefficients, "
                "mixed-interior PSD, spatial multipliers, one-use, Nelson, or Sector A closure."
            ),
        }


Poly1 = tuple[Fraction, ...]
Poly2 = dict[tuple[int, int], Fraction]
PolyN = dict[tuple[int, ...], Fraction]


def trim(poly: list[Fraction] | tuple[Fraction, ...]) -> Poly1:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def add1(*polys: Poly1) -> Poly1:
    size = max(len(poly) for poly in polys)
    return trim(
        [
            sum((poly[index] if index < len(poly) else Fraction(0)) for poly in polys)
            for index in range(size)
        ]
    )


def scale1(value: Fraction, poly: Poly1) -> Poly1:
    return trim([value * coefficient for coefficient in poly])


def sub1(left: Poly1, right: Poly1) -> Poly1:
    return add1(left, scale1(Fraction(-1), right))


def mul1(left: Poly1, right: Poly1) -> Poly1:
    values = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            values[i + j] += a * b
    return trim(values)


def derivative1(poly: Poly1) -> Poly1:
    if len(poly) == 1:
        return (Fraction(0),)
    return trim([Fraction(index) * poly[index] for index in range(1, len(poly))])


def x_times1(poly: Poly1) -> Poly1:
    return (Fraction(0),) + poly


def gaussian_mean1(poly: Poly1) -> Fraction:
    total = Fraction(0)
    for degree, coefficient in enumerate(poly):
        if degree % 2:
            continue
        moment = 1
        for factor in range(1, degree, 2):
            moment *= factor
        total += coefficient * moment
    return total


def add2(*polys: Poly2) -> Poly2:
    result: Poly2 = {}
    for poly in polys:
        for key, value in poly.items():
            result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scale2(value: Fraction, poly: Poly2) -> Poly2:
    return {key: value * coefficient for key, coefficient in poly.items() if value * coefficient}


def mul2(left: Poly2, right: Poly2) -> Poly2:
    result: Poly2 = {}
    for (i, j), a in left.items():
        for (k, ell), b in right.items():
            key = (i + k, j + ell)
            result[key] = result.get(key, Fraction(0)) + a * b
    return {key: value for key, value in result.items() if value}


def derivative2(poly: Poly2, axis: int) -> Poly2:
    result: Poly2 = {}
    for (i, j), coefficient in poly.items():
        degree = i if axis == 0 else j
        if degree == 0:
            continue
        key = (i - 1, j) if axis == 0 else (i, j - 1)
        result[key] = coefficient * degree
    return result


def coordinate_times2(poly: Poly2, axis: int) -> Poly2:
    return {((i + 1, j) if axis == 0 else (i, j + 1)): value for (i, j), value in poly.items()}


def gaussian_mean2(poly: Poly2) -> Fraction:
    def moment(degree: int) -> int:
        if degree % 2:
            return 0
        value = 1
        for factor in range(1, degree, 2):
            value *= factor
        return value

    return sum(coefficient * moment(i) * moment(j) for (i, j), coefficient in poly.items())


def evaluate2(poly: Poly2, x: Fraction, y: Fraction) -> Fraction:
    return sum(coefficient * x**i * y**j for (i, j), coefficient in poly.items())


def delta2_matrix2(weight: list[list[Poly2]]) -> Poly2:
    result: Poly2 = {}
    for i in range(2):
        for j in range(2):
            wij = weight[i][j]
            xixj = coordinate_times2(coordinate_times2(wij, i), j)
            if i == j:
                xixj = add2(xixj, scale2(Fraction(-1), wij))
            first = coordinate_times2(derivative2(wij, j), i)
            second = coordinate_times2(derivative2(wij, i), j)
            mixed = derivative2(derivative2(wij, i), j)
            result = add2(result, xixj, scale2(Fraction(-1), first), scale2(Fraction(-1), second), mixed)
    return result


def matrix_multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def addn(*polys: PolyN) -> PolyN:
    result: PolyN = {}
    for poly in polys:
        for key, value in poly.items():
            result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scalen(value: Fraction, poly: PolyN) -> PolyN:
    return {key: value * coefficient for key, coefficient in poly.items() if value * coefficient}


def muln(left: PolyN, right: PolyN) -> PolyN:
    result: PolyN = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key))
            result[key] = result.get(key, Fraction(0)) + left_value * right_value
    return {key: value for key, value in result.items() if value}


def derivativen(poly: PolyN, axis: int) -> PolyN:
    result: PolyN = {}
    for key, coefficient in poly.items():
        degree = key[axis]
        if degree == 0:
            continue
        derived_key = list(key)
        derived_key[axis] -= 1
        result[tuple(derived_key)] = coefficient * degree
    return result


def evaluaten(poly: PolyN, point: tuple[Fraction, ...]) -> Fraction:
    total = Fraction(0)
    for key, coefficient in poly.items():
        term = coefficient
        for degree, value in zip(key, point):
            term *= value**degree
        total += term
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    # Independent scalar reconstruction of the two-visit telescope.
    x0, x1, xs = Fraction(2), Fraction(-1), Fraction(5)
    t0, t1, ts = Fraction(3), Fraction(7), Fraction(-2)
    first_visit = x0 * (x1 - x0) + (x1 - x0) ** 2 / 2 - (t1 - t0) / 2
    second_visit = x1 * (xs - x1) + (xs - x1) ** 2 / 2 - (ts - t1) / 2
    endpoint = (xs**2 - x0**2) / 2 - (ts - t0) / 2
    audit.check("legal_chart", "two_visit_telescope", first_visit + second_visit == endpoint, first_visit + second_visit, endpoint)
    def adapted_second_visit(root_one: Fraction, unrevealed_root: Fraction) -> Fraction:
        del unrevealed_root
        return root_one**2 - 1

    audit.check(
        "legal_chart",
        "second_visit_uses_first_root",
        adapted_second_visit(Fraction(2), Fraction(-5))
        != adapted_second_visit(Fraction(3), Fraction(-5)),
        adapted_second_visit(Fraction(2), Fraction(-5)),
        "nonconstant",
    )
    audit.check(
        "legal_chart",
        "second_visit_ignores_unrevealed_root",
        adapted_second_visit(Fraction(2), Fraction(-5))
        == adapted_second_visit(Fraction(2), Fraction(11)),
        adapted_second_visit(Fraction(2), Fraction(-5)),
        adapted_second_visit(Fraction(2), Fraction(11)),
    )

    one = (Fraction(1),)
    G = (Fraction(0), Fraction(1))
    H2 = (Fraction(-1), Fraction(0), Fraction(1))
    H3 = (Fraction(0), Fraction(-3), Fraction(0), Fraction(1))

    def make_residual(a: Fraction, b: Fraction, alpha: Fraction, beta: Fraction, q0: Fraction, q1: Fraction) -> Poly1:
        remainder = add1(scale1(alpha, H2), scale1(beta, H3))
        affine = add1(scale1(b, one), scale1(a, G))
        trace = add1(scale1(q0, one), scale1(q1, G))
        return add1(mul1(affine, remainder), scale1(Fraction(1, 2), mul1(remainder, remainder)), scale1(Fraction(-1, 2), trace))

    grid_ok = True
    cancellation_ok = True
    tested = 0
    for a in (Fraction(-2, 3), Fraction(0), Fraction(5, 4)):
        for b in (Fraction(-1, 2), Fraction(3, 2)):
            for alpha in (Fraction(-2, 5), Fraction(1, 3)):
                for beta in (Fraction(-1, 4), Fraction(2, 7)):
                    q0 = Fraction(7, 11)
                    q1 = Fraction(-5, 13)
                    residual = make_residual(a, b, alpha, beta, q0, q1)
                    mean = gaussian_mean1(residual)
                    first = gaussian_mean1(mul1(G, residual))
                    expected_mean = (2 * alpha**2 + 6 * beta**2 - q0) / 2
                    expected_first = 2 * a * alpha + 6 * alpha * beta - q1 / 2
                    grid_ok = grid_ok and mean == expected_mean and first == expected_first
                    required_q0 = 2 * alpha**2 + 6 * beta**2
                    required_q1 = 4 * a * alpha + 12 * alpha * beta
                    cancelled = make_residual(a, b, alpha, beta, required_q0, required_q1)
                    cancellation_ok = cancellation_ok and gaussian_mean1(cancelled) == 0
                    cancellation_ok = cancellation_ok and gaussian_mean1(mul1(G, cancelled)) == 0
                    tested += 1
    audit.check("score_trace", "exact_parameter_grid", grid_ok, tested, "all exact identities")
    audit.check("score_trace", "exact_cancellation_grid", cancellation_ok, tested, "all zero and first projections vanish")

    eps = Fraction(3, 7)
    first_fixture = add1(mul1(G, scale1(eps, H2)), scale1(Fraction(1, 2), mul1(scale1(eps, H2), scale1(eps, H2))), scale1(-eps**2, one))
    audit.check("counterfixtures", "centered_first_mean", gaussian_mean1(first_fixture) == 0, gaussian_mean1(first_fixture), 0)
    audit.check("counterfixtures", "centered_first_debt", gaussian_mean1(mul1(G, first_fixture)) == 2 * eps, gaussian_mean1(mul1(G, first_fixture)), 2 * eps)

    alpha, beta = Fraction(2, 5), Fraction(-3, 7)
    remainder = add1(scale1(alpha, H2), scale1(beta, H3))
    mean_trace = 2 * alpha**2 + 6 * beta**2
    adjacent = add1(scale1(Fraction(1, 2), mul1(remainder, remainder)), scale1(Fraction(-1, 2) * mean_trace, one))
    audit.check("counterfixtures", "adjacent_mean", gaussian_mean1(adjacent) == 0, gaussian_mean1(adjacent), 0)
    audit.check("counterfixtures", "adjacent_first_debt", gaussian_mean1(mul1(G, adjacent)) == 6 * alpha * beta, gaussian_mean1(mul1(G, adjacent)), 6 * alpha * beta)

    a, b = Fraction(4, 9), Fraction(-5, 8)
    derivative = derivative1(remainder)
    bare_heat = add1(scale1(2 * a, derivative), mul1(derivative, derivative))
    bare_residual = add1(mul1(add1(scale1(b, one), scale1(a, G)), remainder), scale1(Fraction(1, 2), mul1(remainder, remainder)), scale1(Fraction(-1, 2), bare_heat))
    bare_expected = -alpha**2 - 6 * beta**2
    audit.check("bare_heat", "exact_mean", gaussian_mean1(bare_residual) == bare_expected, gaussian_mean1(bare_residual), bare_expected)
    audit.check("bare_heat", "strict_negative", bare_expected < 0, bare_expected, "<0")

    # Independent bivariate reconstruction of the one-pair canonical W.
    one2: Poly2 = {(0, 0): Fraction(1)}
    x2: Poly2 = {(2, 0): Fraction(1)}
    y2: Poly2 = {(0, 2): Fraction(1)}
    radius = add2(x2, y2)
    radius_sq = mul2(radius, radius)
    packet = scale2(Fraction(1, 16), add2(radius_sq, scale2(Fraction(-4), radius)))
    h2x = add2(x2, scale2(Fraction(-1), one2))
    h2y = add2(y2, scale2(Fraction(-1), one2))
    h4x: Poly2 = {(4, 0): Fraction(1), (2, 0): Fraction(-6), (0, 0): Fraction(3)}
    h4y: Poly2 = {(0, 4): Fraction(1), (0, 2): Fraction(-6), (0, 0): Fraction(3)}
    pair_chaos2 = scale2(Fraction(1, 4), add2(h2x, h2y))
    pair_chaos4 = scale2(Fraction(1, 16), add2(h4x, h4y, scale2(Fraction(2), mul2(h2x, h2y))))
    weight = [
        [
            add2(
                derivative2(derivative2(pair_chaos2, i), j),
                scale2(Fraction(1, 6), derivative2(derivative2(pair_chaos4, i), j)),
            )
            for j in range(2)
        ]
        for i in range(2)
    ]
    w11, w12, w22 = weight[0][0], weight[0][1], weight[1][1]
    delta2 = delta2_matrix2(weight)
    chaos_error = add2(packet, scale2(Fraction(-1), pair_chaos2), scale2(Fraction(-1), pair_chaos4))
    audit.check(
        "one_pair_w",
        "packet_chaos_reconstruction",
        gaussian_mean2(packet) == 0 and not chaos_error,
        [gaussian_mean2(packet), chaos_error],
        [0, {}],
    )
    audit.check("one_pair_w", "delta2_identity", delta2 == scale2(Fraction(2), packet), delta2, scale2(Fraction(2), packet))
    audit.check("one_pair_w", "cost", gaussian_mean2(mul2(delta2, delta2)) == 2, gaussian_mean2(mul2(delta2, delta2)), 2)
    audit.check("one_pair_w", "origin_strict", evaluate2(w11, Fraction(0), Fraction(0)) == Fraction(1, 3), evaluate2(w11, Fraction(0), Fraction(0)), Fraction(1, 3))
    px, py = Fraction(2), Fraction(3)
    s = px**2 + py**2
    matrix_at = [[evaluate2(weight[i][j], px, py) for j in range(2)] for i in range(2)]
    tangent = [-py, px]
    radial = [px, py]
    tangent_form = sum(tangent[i] * matrix_at[i][j] * tangent[j] for i in range(2) for j in range(2)) / s
    radial_form = sum(radial[i] * matrix_at[i][j] * radial[j] for i in range(2) for j in range(2)) / s
    audit.check("one_pair_w", "tangential_eigenvalue", tangent_form == (s + 8) / 24, tangent_form, (s + 8) / 24)
    audit.check("one_pair_w", "radial_eigenvalue", radial_form == (3 * s + 8) / 24, radial_form, (3 * s + 8) / 24)

    # Independently derive both scalar-face Hessians as exact polynomials in
    # (x,y,b), then compare their radial/tangential forms with the claimed
    # closed forms.  The oracle coefficients are never used to build a weight.
    one3: PolyN = {(0, 0, 0): Fraction(1)}
    x3: PolyN = {(1, 0, 0): Fraction(1)}
    y3: PolyN = {(0, 1, 0): Fraction(1)}
    b3: PolyN = {(0, 0, 1): Fraction(1)}
    radius3 = addn(muln(x3, x3), muln(y3, y3))
    radius3_sq = muln(radius3, radius3)
    centered_radius3 = addn(radius3, scalen(Fraction(-2), one3))
    fourth_radial3 = addn(radius3_sq, scalen(Fraction(-8), radius3), scalen(Fraction(8), one3))

    def face_weight(f2: PolyN, f4: PolyN) -> list[list[PolyN]]:
        return [
            [
                addn(
                    derivativen(derivativen(f2, i), j),
                    scalen(Fraction(1, 6), derivativen(derivativen(f4, i), j)),
                )
                for j in range(2)
            ]
            for i in range(2)
        ]

    face0_f2 = scalen(
        Fraction(1, 16),
        muln(addn(scalen(Fraction(4), b3), one3), centered_radius3),
    )
    face0_f4 = scalen(Fraction(1, 64), fourth_radial3)
    face1_f2 = scalen(
        Fraction(1, 4),
        muln(addn(b3, one3), centered_radius3),
    )
    face1_f4 = scalen(Fraction(1, 16), fourth_radial3)
    face0_weight = face_weight(face0_f2, face0_f4)
    face1_weight = face_weight(face1_f2, face1_f4)

    radial3 = [x3, y3]
    tangent3 = [scalen(Fraction(-1), y3), x3]

    def form3(weight3: list[list[PolyN]], vector3: list[PolyN]) -> PolyN:
        terms = [
            muln(muln(vector3[i], weight3[i][j]), vector3[j])
            for i in range(2)
            for j in range(2)
        ]
        return addn(*terms)

    actual_face_forms = [
        form3(face0_weight, tangent3),
        form3(face0_weight, radial3),
        form3(face1_weight, tangent3),
        form3(face1_weight, radial3),
    ]
    expected_face_forms = [
        scalen(Fraction(1, 96), muln(radius3, addn(scalen(Fraction(48), b3), radius3, scalen(Fraction(8), one3)))),
        scalen(Fraction(1, 96), muln(radius3, addn(scalen(Fraction(48), b3), scalen(Fraction(3), radius3), scalen(Fraction(8), one3)))),
        scalen(Fraction(1, 24), muln(radius3, addn(scalen(Fraction(12), b3), radius3, scalen(Fraction(8), one3)))),
        scalen(Fraction(1, 24), muln(radius3, addn(scalen(Fraction(12), b3), scalen(Fraction(3), radius3), scalen(Fraction(8), one3)))),
    ]
    face_errors = [addn(actual, scalen(Fraction(-1), expected)) for actual, expected in zip(actual_face_forms, expected_face_forms)]
    face_count = len(face_errors)
    audit.check(
        "scalar_faces",
        "both_faces_symbolic_eigenforms",
        all(not error for error in face_errors),
        face_errors,
        [{}, {}, {}, {}],
    )
    mixed_interior_proved = False
    audit.check("scalar_faces", "mixed_interior_not_promoted", not mixed_interior_proved, mixed_interior_proved, False)

    # Exact terminal-Hessian and quotient-norm fixture without a matrix library.
    L = [[Fraction(1), Fraction(1), Fraction(0)], [Fraction(0), Fraction(1), Fraction(1)]]
    vertical = [[Fraction(1)], [Fraction(-1)], [Fraction(1)]]
    audit.check("terminal_hessian", "vertical_kernel", matrix_multiply(L, vertical) == [[0], [0]], matrix_multiply(L, vertical), [[0], [0]])
    endpoint_u: Poly2 = {(1, 0): Fraction(1)}
    endpoint_v: Poly2 = {(0, 1): Fraction(1)}
    endpoint_potential = add2(
        mul2(mul2(endpoint_u, endpoint_u), endpoint_u),
        scale2(Fraction(2), mul2(endpoint_u, endpoint_v)),
        mul2(mul2(mul2(endpoint_v, endpoint_v), endpoint_v), endpoint_v),
    )
    endpoint_hessian = [
        [evaluate2(derivative2(derivative2(endpoint_potential, i), j), Fraction(1), Fraction(2)) for j in range(2)]
        for i in range(2)
    ]
    control0: PolyN = {(1, 0, 0): Fraction(1)}
    control1: PolyN = {(0, 1, 0): Fraction(1)}
    control2: PolyN = {(0, 0, 1): Fraction(1)}
    composed_u = addn(control0, control1)
    composed_v = addn(control1, control2)
    composed_potential = addn(
        muln(muln(composed_u, composed_u), composed_u),
        scalen(Fraction(2), muln(composed_u, composed_v)),
        muln(muln(muln(composed_v, composed_v), composed_v), composed_v),
    )
    control_point = (Fraction(1), Fraction(0), Fraction(2))
    visit_hessian = [
        [evaluaten(derivativen(derivativen(composed_potential, i), j), control_point) for j in range(3)]
        for i in range(3)
    ]
    chain_hessian = matrix_multiply(matrix_multiply(transpose(L), endpoint_hessian), L)
    visit_kernel = matrix_multiply(visit_hessian, vertical)
    audit.check(
        "terminal_hessian",
        "global_hessian_kernel",
        visit_hessian == chain_hessian and visit_kernel == [[0], [0], [0]],
        [visit_hessian, visit_kernel],
        [chain_hessian, [[0], [0], [0]]],
    )
    sample = [Fraction(2), Fraction(-3), Fraction(5)]
    endpoint_sample = [sample[0] + sample[1], sample[1] + sample[2]]
    multiplier = [(2 * endpoint_sample[0] - endpoint_sample[1]) / 3, (-endpoint_sample[0] + 2 * endpoint_sample[1]) / 3]
    minimal = [multiplier[0], multiplier[0] + multiplier[1], multiplier[1]]
    reconstructed = [minimal[0] + minimal[1], minimal[1] + minimal[2]]
    quotient_norm = endpoint_sample[0] * multiplier[0] + endpoint_sample[1] * multiplier[1]
    minimal_norm = sum(value**2 for value in minimal)
    audit.check("terminal_hessian", "minimal_endpoint", reconstructed == endpoint_sample, reconstructed, endpoint_sample)
    audit.check("terminal_hessian", "quotient_norm", quotient_norm == minimal_norm, quotient_norm, minimal_norm)
    discarded = [sample[index] - minimal[index] for index in range(3)]
    audit.check("terminal_hessian", "discarded_vertical", [discarded[0] + discarded[1], discarded[1] + discarded[2]] == [0, 0], discarded, "kernel of L")

    r102 = json.loads(R102_RESULT.read_text(encoding="utf-8"))
    inherited = Fraction(r102["diagnostics"]["cartan_boundary"]["full_remainder_one_form_curl"])
    required = -inherited
    audit.check("cartan_checksum", "authority_pass", r102.get("status") == "PASS", r102.get("status"), "PASS")
    audit.check("cartan_checksum", "isolated_curl", inherited == Fraction(-40, 729), inherited, Fraction(-40, 729))
    audit.check("cartan_checksum", "required_curl", required == Fraction(40, 729), required, Fraction(40, 729))
    audit.check("cartan_checksum", "zero_total_required", inherited + required == 0, inherited + required, 0)

    diagnostics = {
        "parameter_grid_cases": tested,
        "one_pair_cost": gaussian_mean2(mul2(delta2, delta2)),
        "scalar_face_cases": face_count,
        "mixed_interior_psd_proved": False,
        "full_a1_low_chaos_cancellation": False,
        "spatial_multiplier_bound": False,
        "one_use_source_sextic_aggregation": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"{payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
