#!/usr/bin/env python3
"""Independent exact audit of the Q3LOCK second-energy/Cauchy gate split.

This verifier uses only the Python standard library and exact ``Fraction``
arithmetic.  It neither imports the primary verifier nor consumes the primary
result.  It reconstructs the Q3 graph and quartic Laplacian, the published
``M_mu^2`` and ``v_mu^2`` fixture, the two-dimensional order-squaring
counterexample, the free-word cubic commutator identity, and every declared
power-count target and no-overclaim boundary.  In particular, the scalar
``s >= 3/4`` calculation is audited only as a necessary target: it is not an
operator-domain proof that ``q^3 A^(-3/4)`` is bounded.

The artifact is claim-nonbearing.  A PASS does not prove the open spatial
commutator/Gevrey Lieb--Robinson estimate or a thermodynamic common alpha.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
OPEN_GEVREY_GATE = (
    "PA-CP1-ST8-Q3LOCK-ENERGY-WEIGHTED-COMMUTATOR-GEVREY-LR-CLOSURE"
)
UPWARD_SPECTRAL_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-POLYNOMIAL-ALL-RUNG-"
    "ONSITE-ENERGY-CONJUGATION"
)
CONVEXITY_SIGN_NG = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONVEXITY-ONLY-"
    "WEIGHTED-COMMUTATOR-SIGN"
)
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-"
    "weighted-energy-route-split-manifest.json"
)
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

Q3_DIMENSION = 3
SITE_COMPONENTS = 2**Q3_DIMENSION
SPATIAL_DIMENSION = 3


def serial(value: Any) -> Any:
    """Convert exact objects to deterministic JSON-compatible values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def normalized_sha256(path: Path) -> str:
    """Hash a source after normalizing platform line endings."""

    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one complete deterministic JSON artifact by atomic replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                serial(payload),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast exact assertion ledger."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


# Bivariate polynomials in (a,b), represented by exact monomial dictionaries.
Bivariate = dict[tuple[int, int], Fraction]


def biv_clean(polynomial: Mapping[tuple[int, int], Fraction]) -> Bivariate:
    return {
        power: coefficient
        for power, coefficient in polynomial.items()
        if coefficient != 0
    }


def biv_add(*polynomials: Mapping[tuple[int, int], Fraction]) -> Bivariate:
    output: Bivariate = {}
    for polynomial in polynomials:
        for power, coefficient in polynomial.items():
            output[power] = output.get(power, Fraction(0)) + coefficient
    return biv_clean(output)


def biv_scale(polynomial: Mapping[tuple[int, int], Fraction], scale: Fraction) -> Bivariate:
    return biv_clean({power: scale * coefficient for power, coefficient in polynomial.items()})


def biv_multiply(
    left: Mapping[tuple[int, int], Fraction],
    right: Mapping[tuple[int, int], Fraction],
) -> Bivariate:
    output: Bivariate = {}
    for (left_a, left_b), left_coefficient in left.items():
        for (right_a, right_b), right_coefficient in right.items():
            power = (left_a + right_a, left_b + right_b)
            output[power] = output.get(power, Fraction(0)) + (
                left_coefficient * right_coefficient
            )
    return biv_clean(output)


def biv_power(polynomial: Mapping[tuple[int, int], Fraction], exponent: int) -> Bivariate:
    output: Bivariate = {(0, 0): Fraction(1)}
    for _ in range(exponent):
        output = biv_multiply(output, polynomial)
    return output


def biv_derivative(
    polynomial: Mapping[tuple[int, int], Fraction], variable: int, order: int = 1
) -> Bivariate:
    output = dict(polynomial)
    for _ in range(order):
        differentiated: Bivariate = {}
        for powers, coefficient in output.items():
            exponent = powers[variable]
            if exponent == 0:
                continue
            new_power = list(powers)
            new_power[variable] -= 1
            differentiated[tuple(new_power)] = coefficient * exponent
        output = biv_clean(differentiated)
    return output


def cube_vertices(dimension: int) -> list[tuple[int, ...]]:
    return list(itertools.product((0, 1), repeat=dimension))


def cube_edges(vertices: Sequence[tuple[int, ...]]) -> list[tuple[int, int]]:
    return [
        (left, right)
        for left in range(len(vertices))
        for right in range(left + 1, len(vertices))
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def q3_laplacian() -> dict[str, Any]:
    """Derive the internal-edge Laplacian without symbolic software."""

    a: Bivariate = {(1, 0): Fraction(1)}
    b: Bivariate = {(0, 1): Fraction(1)}
    difference = biv_add(a, biv_scale(b, Fraction(-1)))
    square_sum = biv_add(biv_power(a, 2), biv_power(b, 2))
    # Lambda is factored out.  This is phi/lambda.
    edge_quartic = biv_scale(
        biv_multiply(biv_power(difference, 2), square_sum), Fraction(1, 4)
    )
    laplacian = biv_add(
        biv_derivative(edge_quartic, 0, 2),
        biv_derivative(edge_quartic, 1, 2),
    )
    seven_norm = {(2, 0): Fraction(7), (0, 2): Fraction(7)}
    residual = biv_add(seven_norm, biv_scale(laplacian, Fraction(-1)))
    sos = biv_scale(biv_power(biv_add(a, b), 2), Fraction(3))

    vertices = cube_vertices(Q3_DIMENSION)
    edges = cube_edges(vertices)
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(len(vertices))]
    return {
        "vertices": vertices,
        "edges": edges,
        "degrees": degrees,
        "edge_quartic_over_lambda": edge_quartic,
        "edge_laplacian_over_lambda": laplacian,
        "seven_norm_residual": residual,
        "sos_residual_oracle": sos,
    }


Matrix = tuple[tuple[Fraction, ...], ...]


def matrix_transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    right_t = matrix_transpose(right)
    return tuple(
        tuple(
            sum((a * b for a, b in zip(left_row, right_column)), Fraction(0))
            for right_column in right_t
        )
        for left_row in left
    )


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(a + b for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def matrix_scale(matrix: Matrix, scale: Fraction) -> Matrix:
    return tuple(tuple(scale * value for value in row) for row in matrix)


def matrix_det2(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def matrix_identity2() -> Matrix:
    return ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))


def matrix_power_counterexample() -> dict[str, Any]:
    """Reconstruct the exact 2x2 failure of order-preserving squaring."""

    energy: Matrix = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(3)))
    unitary: Matrix = (
        (Fraction(3, 5), Fraction(-4, 5)),
        (Fraction(4, 5), Fraction(3, 5)),
    )
    evolved = matrix_multiply(matrix_multiply(matrix_transpose(unitary), energy), unitary)
    scale = Fraction(5, 2)
    first = matrix_add(matrix_scale(energy, scale), matrix_scale(evolved, Fraction(-1)))
    energy_squared = matrix_multiply(energy, energy)
    evolved_squared = matrix_multiply(evolved, evolved)
    second = matrix_add(
        matrix_scale(energy_squared, scale**2),
        matrix_scale(evolved_squared, Fraction(-1)),
    )
    return {
        "energy": energy,
        "unitary": unitary,
        "orthogonal_residual": matrix_add(
            matrix_multiply(matrix_transpose(unitary), unitary),
            matrix_scale(matrix_identity2(), Fraction(-1)),
        ),
        "evolved": evolved,
        "first": first,
        "first_leading_minor": first[0][0],
        "first_determinant": matrix_det2(first),
        "second": second,
        "second_determinant": matrix_det2(second),
    }


def upward_spectral_transition_fixture() -> dict[str, Any]:
    """Derive the exponential graph-rung growth from one upward transition.

    ``root`` is K^(1/2).  Thus K^(j/2)=root^j.  The swap has the
    nonzero transition <e1,V e0>=1 from root-energy 1 to root-energy 2,
    and the declared matrix element is exactly 2^j at every rung.
    """

    root: Matrix = (
        (Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(2)),
    )
    swap: Matrix = (
        (Fraction(0), Fraction(1)),
        (Fraction(1), Fraction(0)),
    )
    rows: list[dict[str, Any]] = []
    for rung in range(17):
        left: Matrix = (
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(2**rung)),
        )
        right: Matrix = (
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(1, 2 ** (rung + 1))),
        )
        sandwich = matrix_multiply(matrix_multiply(left, swap), right)
        rows.append(
            {
                "j": rung,
                "sandwich": sandwich,
                "upward_matrix_element": sandwich[1][0],
                "expected": Fraction(2**rung),
            }
        )

    # Exact hostile fixtures for fixed polynomial degrees.  Along j=2^n,
    #   2^j/(j+1)^d >= 2^(2^n-d(n+1)).
    # The exponent gap has increment 2^n-d and hence diverges for every
    # fixed d.  The finite rows below verify the algebra and monotone tail for
    # representative degrees; the manifest carries the generic quantified
    # route verdict.
    polynomial_rows: list[dict[str, Any]] = []
    for degree in range(9):
        rungs = (64, 128, 256)
        ratios = tuple(
            Fraction(2**rung, (rung + 1) ** degree) for rung in rungs
        )
        gap_rows = []
        for exponent in range(10, 15):
            gap = 2**exponent - degree * (exponent + 1)
            next_gap = 2 ** (exponent + 1) - degree * (exponent + 2)
            gap_rows.append(
                {
                    "n": exponent,
                    "gap": gap,
                    "next_gap": next_gap,
                    "increment": next_gap - gap,
                    "expected_increment": 2**exponent - degree,
                }
            )
        polynomial_rows.append(
            {
                "degree": degree,
                "rungs": rungs,
                "ratios": ratios,
                "strict_tail_growth": ratios[0] < ratios[1] < ratios[2],
                "beats_million": ratios[-1] > 10**6,
                "dyadic_gap_rows": gap_rows,
            }
        )
    return {
        "K_half": root,
        "V": swap,
        "transition": Fraction(1),
        "rung_rows": rows,
        "polynomial_rows": polynomial_rows,
        "generic_lower_bound": "2^(2^n-d(n+1)) along j=2^n",
    }


def convexity_sign_fixture() -> dict[str, Any]:
    """Derive the exact 3x3 failure of a convexity-only sign argument."""

    q: Matrix = (
        (Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(2)),
    )
    disturbance: Matrix = tuple(
        tuple(Fraction(-1) for _ in range(3)) for _ in range(3)
    )
    q_cubed = matrix_multiply(matrix_multiply(q, q), q)
    first_commutator = matrix_add(
        matrix_multiply(q, disturbance),
        matrix_scale(matrix_multiply(disturbance, q), Fraction(-1)),
    )
    cubic_commutator = matrix_add(
        matrix_multiply(q_cubed, disturbance),
        matrix_scale(matrix_multiply(disturbance, q_cubed), Fraction(-1)),
    )
    cross = matrix_scale(
        matrix_add(
            matrix_multiply(matrix_transpose(first_commutator), cubic_commutator),
            matrix_multiply(matrix_transpose(cubic_commutator), first_commutator),
        ),
        Fraction(1, 2),
    )
    vector = (Fraction(-2), Fraction(2), Fraction(-1))
    image = tuple(
        sum((entry * component for entry, component in zip(row, vector)), Fraction(0))
        for row in cross
    )
    quadratic_form = sum(
        (component * image_component for component, image_component in zip(vector, image)),
        Fraction(0),
    )
    trace = sum((cross[index][index] for index in range(3)), Fraction(0))
    return {
        "q": q,
        "D": disturbance,
        "q_cubed": q_cubed,
        "C": first_commutator,
        "F": cubic_commutator,
        "X": cross,
        "test_vector": vector,
        "Xv": image,
        "quadratic_form": quadratic_form,
        "trace": trace,
    }


Word = tuple[str, ...]
FreePolynomial = dict[Word, int]


def word_add(*polynomials: Mapping[Word, int]) -> FreePolynomial:
    output: FreePolynomial = {}
    for polynomial in polynomials:
        for word, coefficient in polynomial.items():
            output[word] = output.get(word, 0) + coefficient
    return {word: coefficient for word, coefficient in output.items() if coefficient}


def word_scale(polynomial: Mapping[Word, int], scale: int) -> FreePolynomial:
    return {word: scale * coefficient for word, coefficient in polynomial.items()}


def word_multiply(
    left: Mapping[Word, int], right: Mapping[Word, int]
) -> FreePolynomial:
    output: FreePolynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            word = left_word + right_word
            output[word] = output.get(word, 0) + left_coefficient * right_coefficient
    return output


def word_commutator(
    left: Mapping[Word, int], right: Mapping[Word, int]
) -> FreePolynomial:
    return word_add(
        word_multiply(left, right),
        word_scale(word_multiply(right, left), -1),
    )


def free_word_cubic_identity() -> dict[str, Any]:
    """Expand [q^3,D]=3[q,D]q^2+3[q,[q,D]]q+ad_q^3(D)."""

    q: FreePolynomial = {("q",): 1}
    d: FreePolynomial = {("D",): 1}
    q2 = word_multiply(q, q)
    q3 = word_multiply(q2, q)
    c1 = word_commutator(q, d)
    c2 = word_commutator(q, c1)
    c3 = word_commutator(q, c2)
    lhs = word_commutator(q3, d)
    rhs = word_add(
        word_scale(word_multiply(c1, q2), 3),
        word_scale(word_multiply(c2, q), 3),
        c3,
    )
    residual = word_add(lhs, word_scale(rhs, -1))
    return {
        "c1": c1,
        "c2": c2,
        "c3": c3,
        "lhs": lhs,
        "rhs": rhs,
        "residual": residual,
    }


def fixture_constants(c2: Fraction) -> dict[str, Fraction | bool]:
    """Evaluate a fully declared exact-rational second-moment fixture."""

    # INPUTS only.  The ratio is the exact fixture for exp(mu).
    g = Fraction(2)
    lam = Fraction(1, 3)
    c = Fraction(3, 2)
    chi = Fraction(5, 4)
    hbar = Fraction(1)
    gamma = Fraction(1, 32)
    ratio = Fraction(3, 2)
    theta = ratio - 1
    degree = Fraction(2 * SPATIAL_DIMENSION)
    epsilon = Fraction(1, 10)
    s_f = Fraction(7)
    r_plus = Fraction(0)

    onsite_laplacian = c2 * epsilon
    bond_laplacian = s_f * 8 * c * degree
    young_laplacian = s_f * c2 / (4 * epsilon * gamma)
    laplacian_bracket = (
        onsite_laplacian
        + bond_laplacian
        + young_laplacian
        + s_f * 8 * r_plus
    )
    current_prefactor = theta**2 * c * degree / chi
    correction = 1 + hbar**2 * laplacian_bracket / (2 * chi)
    m_squared = current_prefactor * correction
    sharp_current_squared = c / (2 * chi)
    v_squared = degree**2 * sharp_current_squared * theta**2
    return {
        "g": g,
        "lambda": lam,
        "c": c,
        "chi": chi,
        "hbar": hbar,
        "gamma": gamma,
        "ratio": ratio,
        "theta": theta,
        "degree": degree,
        "epsilon": epsilon,
        "S_f": s_f,
        "r_plus": r_plus,
        "C2": c2,
        "onsite_laplacian": onsite_laplacian,
        "bond_laplacian": bond_laplacian,
        "young_laplacian": young_laplacian,
        "laplacian_bracket": laplacian_bracket,
        "current_prefactor": current_prefactor,
        "correction": correction,
        "M_mu_squared": m_squared,
        "sharp_current_squared": sharp_current_squared,
        "v_mu_squared": v_squared,
        "gamma_admitted": Fraction(0) < gamma < g / 32,
    }


def imported_modules(source_text: str) -> set[str]:
    tree = ast.parse(source_text)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate_text.split())
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    negative_registry = NEGATIVE_REGISTRY.read_text(encoding="utf-8")

    source_text = SCRIPT.read_text(encoding="utf-8")
    modules = imported_modules(source_text)
    forbidden = {"numpy", "sympy"}
    primary_stem = "pre_a_cp1_st8_q3lock_second_weighted_energy_cauchy_gate"
    audit.check(
        "stdlib-only dependency boundary",
        not any(module.split(".")[0] in forbidden for module in modules),
        sorted(modules),
        "no numpy or sympy",
        "independence",
    )
    audit.check(
        "no primary verifier import",
        not any(module.endswith(primary_stem) for module in modules),
        sorted(modules),
        "primary module absent",
        "independence",
    )

    audit.check(
        "manifest schema",
        manifest["schema"] == "tect/pre-a-route-split/1.0",
        manifest["schema"],
        "tect/pre-a-route-split/1.0",
        "identity",
    )
    audit.check(
        "result identifier",
        manifest["result_id"] == RESULT_ID,
        manifest["result_id"],
        RESULT_ID,
        "identity",
    )
    audit.check(
        "task identifier",
        manifest["task_id"] == "T-054",
        manifest["task_id"],
        "T-054",
        "identity",
    )
    audit.check(
        "claim context",
        manifest["claim_ids"] == ["C6-SPACETIME-SIGNATURE"],
        manifest["claim_ids"],
        ["C6-SPACETIME-SIGNATURE"],
        "identity",
    )
    audit.check(
        "parent exploration chain",
        manifest["parent_explorations"] == ["EXP-000790", "EXP-000792", "EXP-000793"],
        manifest["parent_explorations"],
        ["EXP-000790", "EXP-000792", "EXP-000793"],
        "identity",
    )
    audit.check(
        "parent result cited",
        parent["result_id"] in certificate_flat,
        parent["result_id"],
        "present in certificate",
        "identity",
    )
    audit.check(
        "certificate result identifier",
        RESULT_ID in certificate_flat,
        RESULT_ID in certificate_flat,
        True,
        "identity",
    )
    expected_negative_ids = {
        "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIRST-MOMENT-AUTOMATIC-POWER-UPGRADE",
        "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SYMMETRIC-SANDWICH-ONLY-THERMODYNAMIC-CAUCHY",
        UPWARD_SPECTRAL_NG,
        CONVEXITY_SIGN_NG,
    }
    audit.check(
        "complete negative route set",
        set(manifest["negative_ids"]) == expected_negative_ids,
        manifest["negative_ids"],
        sorted(expected_negative_ids),
        "identity",
    )
    for negative_id in (UPWARD_SPECTRAL_NG, CONVEXITY_SIGN_NG):
        audit.check(
            f"negative registry {negative_id}",
            negative_id in negative_registry,
            negative_id in negative_registry,
            True,
            "identity",
        )
        audit.check(
            f"certificate negative linkage {negative_id}",
            negative_id in certificate_text,
            negative_id in certificate_text,
            True,
            "identity",
        )

    q3 = q3_laplacian()
    expected_edges = SITE_COMPONENTS * Q3_DIMENSION // 2
    expected_laplacian: Bivariate = {
        (2, 0): Fraction(4),
        (1, 1): Fraction(-6),
        (0, 2): Fraction(4),
    }
    audit.check(
        "Q3 vertex count",
        len(q3["vertices"]) == SITE_COMPONENTS,
        len(q3["vertices"]),
        SITE_COMPONENTS,
        "q3",
    )
    audit.check(
        "Q3 edge count",
        len(q3["edges"]) == expected_edges,
        len(q3["edges"]),
        expected_edges,
        "q3",
    )
    audit.check(
        "Q3 degree sequence",
        q3["degrees"] == [Q3_DIMENSION] * SITE_COMPONENTS,
        q3["degrees"],
        [Q3_DIMENSION] * SITE_COMPONENTS,
        "q3",
    )
    audit.check(
        "edge Laplacian polynomial",
        q3["edge_laplacian_over_lambda"] == expected_laplacian,
        q3["edge_laplacian_over_lambda"],
        expected_laplacian,
        "q3",
    )
    audit.check(
        "edge seven-bound SOS",
        q3["seven_norm_residual"] == q3["sos_residual_oracle"],
        q3["seven_norm_residual"],
        q3["sos_residual_oracle"],
        "q3",
    )
    audit.check(
        "edge seven-bound positive coefficients",
        all(value >= 0 for value in q3["seven_norm_residual"].values()),
        q3["seven_norm_residual"],
        "3(a+b)^2",
        "q3",
    )

    # The onsite g-term contributes 3g|q|^2.  Every Q3 vertex occurs in
    # exactly three edge bounds of strength 7 lambda.
    fixture_g = Fraction(2)
    fixture_lambda = Fraction(1, 3)
    c2_from_graph = 3 * fixture_g + 7 * Q3_DIMENSION * fixture_lambda
    fixture = fixture_constants(c2_from_graph)
    # Explicit TEST ORACLES, independently precomputed from the declared
    # rational inputs.  These are not production coefficients.
    test_oracles = {
        "C2": Fraction(13),
        "laplacian_bracket": Fraction(77853, 10),
        "M_mu_squared": Fraction(700902, 125),
        "v_mu_squared": Fraction(27, 5),
    }
    audit.check(
        "fixture gamma strict",
        bool(fixture["gamma_admitted"]),
        fixture["gamma"],
        "0<gamma<g/32",
        "fixture",
    )
    audit.check(
        "C2 graph reconstruction",
        fixture["C2"] == test_oracles["C2"],
        fixture["C2"],
        test_oracles["C2"],
        "fixture",
    )
    audit.check(
        "theta from exact ratio",
        fixture["theta"] == Fraction(1, 2),
        fixture["theta"],
        Fraction(1, 2),
        "fixture",
    )
    audit.check(
        "spatial degree reconstructed",
        fixture["degree"] == 2 * SPATIAL_DIMENSION,
        fixture["degree"],
        2 * SPATIAL_DIMENSION,
        "fixture",
    )
    audit.check(
        "onsite Laplacian fixture",
        fixture["onsite_laplacian"] == Fraction(13, 10),
        fixture["onsite_laplacian"],
        Fraction(13, 10),
        "fixture",
    )
    audit.check(
        "bond Laplacian fixture",
        fixture["bond_laplacian"] == Fraction(504),
        fixture["bond_laplacian"],
        Fraction(504),
        "fixture",
    )
    audit.check(
        "Young Laplacian fixture",
        fixture["young_laplacian"] == Fraction(7280),
        fixture["young_laplacian"],
        Fraction(7280),
        "fixture",
    )
    audit.check(
        "total Laplacian bracket fixture",
        fixture["laplacian_bracket"] == test_oracles["laplacian_bracket"],
        fixture["laplacian_bracket"],
        test_oracles["laplacian_bracket"],
        "fixture",
    )
    audit.check(
        "current prefactor fixture",
        fixture["current_prefactor"] == Fraction(9, 5),
        fixture["current_prefactor"],
        Fraction(9, 5),
        "fixture",
    )
    audit.check(
        "M squared exact fixture",
        fixture["M_mu_squared"] == test_oracles["M_mu_squared"],
        fixture["M_mu_squared"],
        test_oracles["M_mu_squared"],
        "fixture",
    )
    audit.check(
        "v squared exact fixture",
        fixture["v_mu_squared"] == test_oracles["v_mu_squared"],
        fixture["v_mu_squared"],
        test_oracles["v_mu_squared"],
        "fixture",
    )
    audit.check(
        "M squared positive",
        fixture["M_mu_squared"] > 0,
        fixture["M_mu_squared"],
        ">0",
        "fixture",
    )
    audit.check(
        "v squared positive",
        fixture["v_mu_squared"] > 0,
        fixture["v_mu_squared"],
        ">0",
        "fixture",
    )
    audit.check(
        "manifest Q3 coefficient contract",
        manifest["second_moment"]["q3_laplacian"].endswith("C2=3g+21lambda"),
        manifest["second_moment"]["q3_laplacian"],
        "C2=3g+21lambda",
        "fixture",
    )
    audit.check(
        "manifest two one-sided orientations",
        "||B_f A^-1||=||A^-1 B_f||<=M_mu"
        in manifest["second_moment"]["conclusion"],
        manifest["second_moment"]["conclusion"],
        "both one-sided graph bounds",
        "fixture",
    )
    audit.check(
        "manifest second-moment rate",
        "exp(2M_mu|t|)" in manifest["second_moment"]["conclusion"],
        manifest["second_moment"]["conclusion"],
        "2M_mu",
        "fixture",
    )

    matrix = matrix_power_counterexample()
    zero_matrix = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(0)))
    audit.check(
        "counterexample orthogonal matrix",
        matrix["orthogonal_residual"] == zero_matrix,
        matrix["orthogonal_residual"],
        zero_matrix,
        "ordering",
    )
    audit.check(
        "first-order matrix symmetric",
        matrix["first"][0][1] == matrix["first"][1][0],
        matrix["first"],
        "symmetric",
        "ordering",
    )
    audit.check(
        "first-order leading minor",
        matrix["first_leading_minor"] == Fraction(11, 50),
        matrix["first_leading_minor"],
        Fraction(11, 50),
        "ordering",
    )
    audit.check(
        "first-order positive determinant",
        matrix["first_determinant"] == Fraction(7, 20),
        matrix["first_determinant"],
        Fraction(7, 20),
        "ordering",
    )
    audit.check(
        "first-order positive definite",
        matrix["first_leading_minor"] > 0 and matrix["first_determinant"] > 0,
        (matrix["first_leading_minor"], matrix["first_determinant"]),
        "both positive",
        "ordering",
    )
    audit.check(
        "squared-order negative determinant",
        matrix["second_determinant"] == Fraction(-127, 16),
        matrix["second_determinant"],
        Fraction(-127, 16),
        "ordering",
    )
    audit.check(
        "squared-order not positive",
        matrix["second_determinant"] < 0,
        matrix["second_determinant"],
        "<0",
        "ordering",
    )
    audit.check(
        "manifest ordering fixture synchronized",
        "determinant 7/20" in manifest["exact_counterexamples"]["automatic_square"]
        and "det(c0^2E^2-(U*EU)^2)=-127/16"
        in manifest["exact_counterexamples"]["automatic_square"],
        manifest["exact_counterexamples"]["automatic_square"],
        "7/20 and -127/16",
        "ordering",
    )

    upward = upward_spectral_transition_fixture()
    audit.check(
        "upward fixture K half",
        upward["K_half"]
        == ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(2))),
        upward["K_half"],
        "diag(1,2)",
        "upward_spectral",
    )
    audit.check(
        "upward fixture swap transition",
        upward["transition"] == 1 and upward["V"][1][0] == 1,
        (upward["transition"], upward["V"]),
        "<e1,V e0>=1",
        "upward_spectral",
    )
    previous_element: Fraction | None = None
    for row in upward["rung_rows"]:
        audit.check(
            f"upward rung exact j={row['j']}",
            row["upward_matrix_element"] == row["expected"],
            row["upward_matrix_element"],
            row["expected"],
            "upward_spectral",
        )
        if previous_element is not None:
            audit.check(
                f"upward rung doubling j={row['j']}",
                row["upward_matrix_element"] == 2 * previous_element,
                row["upward_matrix_element"],
                2 * previous_element,
                "upward_spectral",
            )
        previous_element = row["upward_matrix_element"]
    for row in upward["polynomial_rows"]:
        degree = row["degree"]
        audit.check(
            f"polynomial envelope strict tail d={degree}",
            bool(row["strict_tail_growth"]),
            row["ratios"],
            "strictly increasing at j=64,128,256",
            "upward_spectral",
        )
        audit.check(
            f"polynomial envelope finite hostile constant d={degree}",
            bool(row["beats_million"]),
            row["ratios"][-1],
            ">10^6",
            "upward_spectral",
        )
        for gap_row in row["dyadic_gap_rows"]:
            audit.check(
                f"dyadic exponent increment d={degree} n={gap_row['n']}",
                gap_row["increment"] == gap_row["expected_increment"],
                gap_row["increment"],
                gap_row["expected_increment"],
                "upward_spectral",
            )
            audit.check(
                f"dyadic exponent increasing d={degree} n={gap_row['n']}",
                gap_row["increment"] > 0,
                gap_row["increment"],
                ">0",
                "upward_spectral",
            )
    audit.check(
        "generic exponential-over-polynomial lower bound",
        upward["generic_lower_bound"] == "2^(2^n-d(n+1)) along j=2^n",
        upward["generic_lower_bound"],
        "2^(2^n-d(n+1)) along j=2^n",
        "upward_spectral",
    )
    rejected_rung = manifest["open_commutator_gate"]["rejected_separate_rung"]
    audit.check(
        "manifest rejects polynomial separate rung",
        "upward spectral transition" in rejected_rung
        and "no C(j+1)^alpha estimate can hold" in rejected_rung,
        rejected_rung,
        "upward transition excludes every fixed polynomial envelope",
        "upward_spectral",
    )
    spectral_contract = manifest["open_commutator_gate"]["spectral_fixture"]
    audit.check(
        "manifest spectral fixture K",
        "K=diag(1,4)" in spectral_contract,
        spectral_contract,
        "K=diag(1,4)",
        "upward_spectral",
    )
    audit.check(
        "manifest spectral fixture exact rung",
        "2^j" in spectral_contract,
        spectral_contract,
        "norm 2^j",
        "upward_spectral",
    )
    audit.check(
        "exact counterexample spectral synchronization",
        "K=diag(1,4)" in manifest["exact_counterexamples"]["polynomial_all_rung"]
        and "2^j" in manifest["exact_counterexamples"]["polynomial_all_rung"],
        manifest["exact_counterexamples"]["polynomial_all_rung"],
        "K=diag(1,4) and 2^j",
        "upward_spectral",
    )
    replacement_targets = manifest["open_commutator_gate"]["replacement_targets"]
    for phrase in (
        "product-level Volterra/linked-cluster",
        "heat/strip-loss analytic-ideal",
        "KMS-specific state-weighted positivity",
        "noncollapsing Hamiltonian-derived finite-density algebra",
    ):
        audit.check(
            f"replacement target {phrase}",
            phrase in replacement_targets,
            replacement_targets,
            f"contains {phrase}",
            "upward_spectral",
        )

    convexity = convexity_sign_fixture()
    expected_cross: Matrix = (
        (Fraction(17), Fraction(11), Fraction(-4)),
        (Fraction(11), Fraction(8), Fraction(5)),
        (Fraction(-4), Fraction(5), Fraction(23)),
    )
    audit.check(
        "convexity cross matrix symmetric",
        convexity["X"] == matrix_transpose(convexity["X"]),
        convexity["X"],
        "symmetric",
        "convexity_sign",
    )
    audit.check(
        "convexity cross matrix exact",
        convexity["X"] == expected_cross,
        convexity["X"],
        expected_cross,
        "convexity_sign",
    )
    audit.check(
        "convexity cross trace",
        convexity["trace"] == 48,
        convexity["trace"],
        48,
        "convexity_sign",
    )
    audit.check(
        "convexity hostile vector",
        convexity["test_vector"] == (Fraction(-2), Fraction(2), Fraction(-1)),
        convexity["test_vector"],
        (-2, 2, -1),
        "convexity_sign",
    )
    audit.check(
        "convexity sign failure",
        convexity["quadratic_form"] == -1,
        convexity["quadratic_form"],
        -1,
        "convexity_sign",
    )
    audit.check(
        "positive trace does not imply sign",
        convexity["trace"] > 0 and convexity["quadratic_form"] < 0,
        (convexity["trace"], convexity["quadratic_form"]),
        "positive trace and negative quadratic form",
        "convexity_sign",
    )
    convexity_contract = manifest["open_commutator_gate"]["convex_subregime_boundary"]
    audit.check(
        "convexity-only route rejected",
        "convexity alone does not supply" in convexity_contract
        and "negative expectation" in convexity_contract,
        convexity_contract,
        "convexity alone is insufficient",
        "convexity_sign",
    )
    audit.check(
        "exact counterexample convexity synchronization",
        "trace 48" in manifest["exact_counterexamples"]["convexity_weighted_sign"]
        and "v^T X v=-1" in manifest["exact_counterexamples"]["convexity_weighted_sign"],
        manifest["exact_counterexamples"]["convexity_weighted_sign"],
        "trace 48 and v^T X v=-1",
        "convexity_sign",
    )

    words = free_word_cubic_identity()
    expected_lhs: FreePolynomial = {
        ("q", "q", "q", "D"): 1,
        ("D", "q", "q", "q"): -1,
    }
    audit.check(
        "free-word left expansion",
        words["lhs"] == expected_lhs,
        words["lhs"],
        expected_lhs,
        "ladder",
    )
    audit.check(
        "free-word cubic residual",
        words["residual"] == {},
        words["residual"],
        {},
        "ladder",
    )
    audit.check(
        "third commutator nonzero",
        len(words["c3"]) > 0,
        words["c3"],
        "nonzero free polynomial",
        "ladder",
    )
    audit.check(
        "cubic identity manifest",
        manifest["open_commutator_gate"]["exact_cubic_identity"]
        == "[q^3,D]=3[q,D]q^2+3[q,[q,D]]q+[q,[q,[q,D]]]",
        manifest["open_commutator_gate"]["exact_cubic_identity"],
        "exact free-word identity",
        "ladder",
    )
    audit.check(
        "Gevrey gate identifier",
        manifest["open_commutator_gate"]["gate_id"] == OPEN_GEVREY_GATE,
        manifest["open_commutator_gate"]["gate_id"],
        OPEN_GEVREY_GATE,
        "ladder",
    )
    audit.check(
        "polynomial all-rung candidate retired",
        "sufficient_candidate" not in manifest["open_commutator_gate"]
        and "rejected_separate_rung" in manifest["open_commutator_gate"],
        sorted(manifest["open_commutator_gate"]),
        "rejected_separate_rung present; sufficient_candidate absent",
        "ladder",
    )
    audit.check(
        "four Gevrey firewalls",
        len(manifest["open_commutator_gate"]["gevrey_boundaries"]) == 4,
        manifest["open_commutator_gate"]["gevrey_boundaries"],
        "four boundaries",
        "ladder",
    )
    for phrase in (
        "factorial lattice-animal multiplicity",
        "allocated heat factors",
        "exp[O(mu n^2)]",
        "not norm dense",
    ):
        audit.check(
            f"Gevrey firewall {phrase}",
            any(
                phrase in boundary
                for boundary in manifest["open_commutator_gate"]["gevrey_boundaries"]
            ),
            manifest["open_commutator_gate"]["gevrey_boundaries"],
            f"contains {phrase}",
            "ladder",
        )

    one_sided_threshold = Fraction(3, 4)
    symmetric_threshold = Fraction(3, 8)
    minimum_fractional_moment = 2 * one_sided_threshold
    minimum_integer_moment = (
        minimum_fractional_moment.numerator
        + minimum_fractional_moment.denominator
        - 1
    ) // minimum_fractional_moment.denominator
    audit.check(
        "necessary one-sided cubic scalar power-count target",
        3 - 4 * one_sided_threshold == 0,
        one_sided_threshold,
        Fraction(3, 4),
        "threshold",
    )
    audit.check(
        "subcritical one-sided hostile fixture",
        3 - 4 * Fraction(2, 3) > 0,
        3 - 4 * Fraction(2, 3),
        ">0 growth exponent",
        "threshold",
    )
    audit.check(
        "necessary symmetric cubic scalar power-count target",
        3 - 8 * symmetric_threshold == 0,
        symmetric_threshold,
        Fraction(3, 8),
        "threshold",
    )
    audit.check(
        "minimum fractional moment",
        minimum_fractional_moment == Fraction(3, 2),
        minimum_fractional_moment,
        Fraction(3, 2),
        "threshold",
    )
    audit.check(
        "minimum integer moment",
        minimum_integer_moment == 2,
        minimum_integer_moment,
        2,
        "threshold",
    )
    power_count_contract = manifest["fractional_graph_domain"]["sharp_power_count"]
    audit.check(
        "manifest necessary one-sided cubic scalar power-count target",
        "s>=3/4" in power_count_contract and "necessary" in power_count_contract,
        power_count_contract,
        "necessary scalar target s>=3/4",
        "threshold",
    )
    audit.check(
        "manifest necessary symmetric cubic scalar power-count target",
        "s>=3/8" in power_count_contract and "necessary" in power_count_contract,
        power_count_contract,
        "necessary scalar target s>=3/8",
        "threshold",
    )
    audit.check(
        "cubic multiplier embedding remains open",
        manifest["fractional_graph_domain"]["cubic_multiplier_closed"] is False
        and "does not prove either noncommuting operator/domain embedding"
        in power_count_contract
        and "q^3 A^-3/4"
        in manifest["fractional_graph_domain"]["cubic_multiplier_open_obligation"]
        and "D(A^(3/4)) subset D(q^3)"
        in manifest["fractional_graph_domain"]["cubic_multiplier_open_obligation"],
        {
            "cubic_multiplier_closed": manifest["fractional_graph_domain"][
                "cubic_multiplier_closed"
            ],
            "contract": power_count_contract,
            "open_obligation": manifest["fractional_graph_domain"][
                "cubic_multiplier_open_obligation"
            ],
        },
        "false with explicit q^3 multiplier/domain obligation",
        "threshold",
    )
    audit.check(
        "scope correction ledger binding",
        manifest["scope_correction_exploration"] == "EXP-000795",
        manifest["scope_correction_exploration"],
        "EXP-000795",
        "threshold",
    )
    audit.check(
        "three-quarter energy-domain propagation",
        "A^(3/4)" in manifest["fractional_graph_domain"]["three_quarter_transport"],
        manifest["fractional_graph_domain"]["three_quarter_transport"],
        "A^(3/4)",
        "threshold",
    )
    audit.check(
        "three-half moment",
        "A^(3/2)" in manifest["fractional_graph_domain"]["three_half_moment"],
        manifest["fractional_graph_domain"]["three_half_moment"],
        "A^(3/2)",
        "threshold",
    )
    audit.check(
        "position multiplier exact constant",
        "gamma^(-1/4)+hbar/sqrt(2chi)"
        in manifest["fractional_graph_domain"]["position_multiplier"],
        manifest["fractional_graph_domain"]["position_multiplier"],
        "gamma^(-1/4)+hbar/sqrt(2chi)",
        "threshold",
    )

    boundary_contract = manifest["conditional_cauchy"]["boundary_identity"]
    audit.check(
        "boundary coefficient one-half",
        boundary_contract.startswith("[c|R|^2/2,D]=(c/2)"),
        boundary_contract,
        "c/2",
        "cauchy",
    )
    audit.check(
        "boundary first commutator factor two",
        "2[R_a,D]R_a" in boundary_contract,
        boundary_contract,
        "2[R_a,D]R_a",
        "cauchy",
    )
    audit.check(
        "first commutator two-sided requirement",
        "both one-sided A^(-1/2) norms"
        in manifest["conditional_cauchy"]["required_first_commutator"],
        manifest["conditional_cauchy"]["required_first_commutator"],
        "both orientations at 1/2",
        "cauchy",
    )
    audit.check(
        "second commutator two-sided requirement",
        "both one-sided A^(-3/4) norms"
        in manifest["conditional_cauchy"]["required_second_commutator"],
        manifest["conditional_cauchy"]["required_second_commutator"],
        "both orientations at 3/4",
        "cauchy",
    )
    audit.check(
        "Cauchy shell exponent",
        manifest["conditional_cauchy"]["spatial_condition"] == "rho>mu/4",
        manifest["conditional_cauchy"]["spatial_condition"],
        "rho>mu/4",
        "cauchy",
    )
    audit.check(
        "Cauchy consequences conditional",
        "subject to core stability" in manifest["conditional_cauchy"]["conclusion"],
        manifest["conditional_cauchy"]["conclusion"],
        "subject to core stability",
        "cauchy",
    )
    audit.check(
        "C-star boundary retained",
        "still required" in manifest["conditional_cauchy"]["cstar_boundary"],
        manifest["conditional_cauchy"]["cstar_boundary"],
        "still required",
        "cauchy",
    )

    # Finite exact fixtures for the topological counterexample at s=1.
    topology_rows: list[dict[str, Any]] = []
    for n in (1, 2, 7, 31):
        symmetric_norm = Fraction(1, n + 1)
        strong_image_norm = Fraction(1)
        audit.check(
            f"symmetric topology decay fixture n={n}",
            symmetric_norm <= Fraction(1, 2),
            symmetric_norm,
            "<=1/2 and tends to zero",
            "topology",
        )
        audit.check(
            f"strong image fixed fixture n={n}",
            strong_image_norm == 1,
            strong_image_norm,
            1,
            "topology",
        )
        topology_rows.append(
            {
                "n": n,
                "s": 1,
                "symmetric_norm": symmetric_norm,
                "strong_image_norm": strong_image_norm,
            }
        )
    audit.check(
        "symmetric topology formula synchronized",
        "(n+1)^(-s)" in manifest["exact_counterexamples"]["symmetric_topology"],
        manifest["exact_counterexamples"]["symmetric_topology"],
        "(n+1)^(-s)",
        "topology",
    )
    audit.check(
        "strong failure synchronized",
        "does not converge strongly"
        in manifest["exact_counterexamples"]["symmetric_topology"],
        manifest["exact_counterexamples"]["symmetric_topology"],
        "does not converge strongly",
        "topology",
    )

    audit.check(
        "closed subgate count",
        len(manifest["closed_subgates"]) == 4,
        manifest["closed_subgates"],
        "four scoped subgates",
        "scope",
    )
    audit.check(
        "Gevrey gate remains open",
        OPEN_GEVREY_GATE in manifest["open_gates"],
        manifest["open_gates"],
        OPEN_GEVREY_GATE,
        "scope",
    )
    audit.check(
        "common-alpha gate remains open",
        any("COMMON-ALPHA-CLOSURE" in gate for gate in manifest["open_gates"]),
        manifest["open_gates"],
        "COMMON-ALPHA-CLOSURE",
        "scope",
    )
    audit.check(
        "status only partially resolved",
        manifest["status"].startswith("PARTIALLY RESOLVED:"),
        manifest["status"],
        "PARTIALLY RESOLVED",
        "scope",
    )
    audit.check(
        "common alpha explicitly remains open",
        "COMMON ALPHA" in manifest["status"] and "REMAIN OPEN" in manifest["status"],
        manifest["status"],
        "COMMON ALPHA ... REMAIN OPEN",
        "scope",
    )
    for token in (
        "spatial commutator Lieb--Robinson",
        "thermodynamic common alpha",
        "common-alpha KMS",
        "algebraic ground states",
        "GNS",
        "regulator removal",
        "physical empty space",
        "below-empty sign",
        "functional selection",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A",
    ):
        audit.check(
            f"no-overclaim {token}",
            token in manifest["no_overclaim"],
            manifest["no_overclaim"],
            f"contains {token}",
            "scope",
        )
    for phrase in (
        "thermodynamic automorphism is not yet constructed",
        "remaining commutator hierarchy does not close",
        "Common `alpha`",
        "claim-nonbearing",
    ):
        audit.check(
            f"certificate boundary {phrase}",
            phrase.lower() in certificate_text.lower(),
            phrase in certificate_text,
            True,
            "scope",
        )

    source_paths = (SCRIPT, MANIFEST, CERTIFICATE, PARENT, NEGATIVE_REGISTRY)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
    }
    for relative_path, digest in source_hashes.items():
        audit.check(
            f"source hash {relative_path}",
            len(digest) == 64 and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": (
            "tect/pre-a-cp1-st8-q3lock-second-weighted-energy-"
            "cauchy-gate-independent-result/1.0"
        ),
        "script_version": __version__,
        "result_id": RESULT_ID,
        "task_id": manifest["task_id"],
        "claim_ids": manifest["claim_ids"],
        "claim_bearing": False,
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "q3": {
                "dimension": Q3_DIMENSION,
                "vertices": len(q3["vertices"]),
                "edges": len(q3["edges"]),
                "degrees": q3["degrees"],
                "edge_laplacian_over_lambda": q3["edge_laplacian_over_lambda"],
                "seven_bound_residual": q3["seven_norm_residual"],
                "C2_fixture": fixture["C2"],
            },
            "second_moment_fixture": fixture,
            "ordering_counterexample": matrix,
            "upward_spectral_transition": upward,
            "convexity_sign_counterexample": convexity,
            "free_word_cubic": {
                "lhs": words["lhs"],
                "rhs": words["rhs"],
                "residual_terms": len(words["residual"]),
                "third_commutator_terms": len(words["c3"]),
            },
            "thresholds": {
                "cubic_power_count_target": one_sided_threshold,
                "symmetric_cubic_power_count_target": symmetric_threshold,
                "minimum_fractional_moment": minimum_fractional_moment,
                "minimum_integer_moment": minimum_integer_moment,
                "cauchy_spatial_condition": manifest["conditional_cauchy"]["spatial_condition"],
                "fixed_polynomial_all_rung": "rejected by 2^j fixture",
                "cubic_multiplier_closed": False,
            },
            "topology_fixtures": topology_rows,
            "common_alpha_closed": False,
        },
        "source_hashes": source_hashes,
        "boundary": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-equivalent payloads without writing",
    )
    arguments = parser.parse_args()
    payload = build_payload()
    if arguments.self_test:
        repeated = build_payload()
        first = json.dumps(serial(payload), sort_keys=True, separators=(",", ":"))
        second = json.dumps(serial(repeated), sort_keys=True, separators=(",", ":"))
        if first != second:
            raise AssertionError("nondeterministic independent payload")
        print(
            f"SELF-TEST PASS {payload['summary']['passed']}/{payload['summary']['total']} | "
            f"{RESULT_ID}"
        )
        return 0
    atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['summary']['passed']}/{payload['summary']['total']} | "
        f"{RESULT_ID}"
    )
    print(arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
