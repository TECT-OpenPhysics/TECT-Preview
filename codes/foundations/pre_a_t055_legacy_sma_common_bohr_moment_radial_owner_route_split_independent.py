#!/usr/bin/env python3
"""Independently audit the exact R-169 v1.4 common-Bohr route split.

Purpose: recount every declared signed support and reconstruct the corrected
legacy scalar polynomial with standard-library integer and Fraction algebra.
Convention: Math396 cosine amplitude is twice a signed Fourier coefficient;
HEX relation coordinates count resonances but are not Euclidean momenta.
Formula: f=(mu2/2)I+(lambda/2)(N4/N2^2)I^2
+(gamma/3)(N6/N2^3)I^3, with no primary-lane import.
"""

from __future__ import annotations

import argparse
import ast
import base64
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
from math import isqrt
import os
from pathlib import Path
import re
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-14-independent-{SLUG}/result.json"
)
FAMILY_ORDER = ("BCC", "FCC", "HEX", "LAM")


def normalized_sha256(path: Path) -> str:
    """Return the repository LF-normalized SHA-256 digest of one file."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def source_payload(path: Path) -> bytes:
    """Return preserved source bytes, validating an ASCII base64 wrapper."""
    raw = path.read_bytes()
    if not path.name.endswith(".source.json"):
        return raw
    wrapper = json.loads(raw.decode("ascii"))
    if wrapper.get("encoding") != "base64":
        raise AssertionError(f"unsupported wrapper encoding: {path}")
    payload = base64.b64decode(wrapper["payload_base64"], validate=True)
    expected_bytes = int(wrapper["bytes"])
    expected_hash = wrapper["sha256"]
    actual_hash = hashlib.sha256(payload).hexdigest()
    if len(payload) != expected_bytes or actual_hash != expected_hash:
        raise AssertionError(f"invalid wrapper payload: {path}")
    return payload


def source_content_sha256(path: Path) -> str:
    """Hash original content, decoded from a wrapper when necessary."""
    return hashlib.sha256(source_payload(path)).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically store one UTF-8/LF JSON result."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fraction_text(value: Fraction) -> str:
    """Render a Fraction in the same canonical form as exact symbolic output."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def pi_quotient_text(value: Fraction) -> str:
    """Render value/pi in the exact canonical symbolic string form."""
    if value.denominator == 1:
        return f"{value.numerator}/pi"
    return f"{value.numerator}/({value.denominator}*pi)"


def parse_fraction(value: str | int) -> Fraction:
    """Reject inexact numeric inputs and parse an exact registered scalar."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise TypeError(f"exact rational input required, got {type(value).__name__}")
    return Fraction(value)


class Audit:
    """Fail-fast assertion ledger used by the stored verifier result."""

    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


@dataclass(frozen=True)
class Surd:
    """Exact element rational + coefficient*sqrt(radicand)."""

    rational: Fraction
    coefficient: Fraction = Fraction(0)
    radicand: int = 1


def squarefree_split(value: int) -> tuple[int, int]:
    """Return outside, inside with value=outside^2*inside and inside squarefree."""
    if value <= 0:
        raise ValueError("squarefree_split requires a positive integer")
    outside = 1
    inside = 1
    remainder = value
    prime = 2
    while prime * prime <= remainder:
        exponent = 0
        while remainder % prime == 0:
            remainder //= prime
            exponent += 1
        outside *= prime ** (exponent // 2)
        if exponent % 2:
            inside *= prime
        prime += 1
    if remainder > 1:
        inside *= remainder
    return outside, inside


def make_surd(
    rational: Fraction,
    coefficient: Fraction = Fraction(0),
    radicand: int = 1,
) -> Surd:
    """Normalize a quadratic surd without numerical approximation."""
    if radicand <= 0:
        raise ValueError("radicand must be positive")
    if coefficient == 0:
        return Surd(rational, Fraction(0), 1)
    outside, inside = squarefree_split(radicand)
    coefficient *= outside
    if inside == 1:
        return Surd(rational + coefficient, Fraction(0), 1)
    return Surd(rational, coefficient, inside)


def add_surd(left: Surd, right: Surd) -> Surd:
    """Add exact surds, allowing either operand to be rational."""
    if left.coefficient and right.coefficient and left.radicand != right.radicand:
        raise ValueError("addition across different quadratic fields is unsupported")
    radicand = left.radicand if left.coefficient else right.radicand
    return make_surd(
        left.rational + right.rational,
        left.coefficient + right.coefficient,
        radicand,
    )


def scale_surd(value: Surd, scalar: Fraction) -> Surd:
    """Multiply an exact surd by a rational scalar."""
    return make_surd(
        value.rational * scalar,
        value.coefficient * scalar,
        value.radicand,
    )


def multiply_surd(left: Surd, right: Surd) -> Surd:
    """Multiply exact surds in one quadratic field."""
    if not left.coefficient:
        return scale_surd(right, left.rational)
    if not right.coefficient:
        return scale_surd(left, right.rational)
    if left.radicand != right.radicand:
        raise ValueError("multiplication across different quadratic fields is unsupported")
    radicand = left.radicand
    rational = (
        left.rational * right.rational
        + left.coefficient * right.coefficient * radicand
    )
    coefficient = (
        left.rational * right.coefficient
        + left.coefficient * right.rational
    )
    return make_surd(rational, coefficient, radicand)


def power_surd(value: Surd, exponent: int) -> Surd:
    """Raise an exact surd to a nonnegative integer power."""
    if exponent < 0:
        raise ValueError("negative surd exponent is unsupported")
    result = Surd(Fraction(1))
    base = value
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = multiply_surd(result, base)
        base = multiply_surd(base, base)
        remaining //= 2
    return result


def compare_surd_zero(value: Surd) -> int:
    """Return the exact sign of a normalized real quadratic surd."""
    rational = value.rational
    coefficient = value.coefficient
    if coefficient == 0:
        return (rational > 0) - (rational < 0)
    if coefficient > 0:
        if rational >= 0:
            return 1
        comparison = coefficient * coefficient * value.radicand - rational * rational
        return (comparison > 0) - (comparison < 0)
    if rational <= 0:
        return -1
    comparison = rational * rational - coefficient * coefficient * value.radicand
    return (comparison > 0) - (comparison < 0)


def subtract_rational(value: Surd, rational: Fraction) -> Surd:
    """Subtract a rational scalar from an exact surd."""
    return make_surd(value.rational - rational, value.coefficient, value.radicand)


def floor_scaled(value: Surd, scale: int) -> int:
    """Find floor(scale*value) by exact integer bracketing and bisection."""
    scaled = scale_surd(value, Fraction(scale))
    if compare_surd_zero(scaled) >= 0:
        lower = 0
        upper = 1
        while compare_surd_zero(subtract_rational(scaled, Fraction(upper))) >= 0:
            lower = upper
            upper *= 2
    else:
        upper = 0
        lower = -1
        while compare_surd_zero(subtract_rational(scaled, Fraction(lower))) < 0:
            upper = lower
            lower *= 2
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if compare_surd_zero(subtract_rational(scaled, Fraction(middle))) >= 0:
            lower = middle
        else:
            upper = middle
    if compare_surd_zero(subtract_rational(scaled, Fraction(lower))) == 0:
        return lower
    return lower


def sqrt_fraction_parts(value: Fraction) -> tuple[Fraction, int]:
    """Return coefficient, radicand with sqrt(value)=coefficient*sqrt(radicand)."""
    if value <= 0:
        raise ValueError("positive discriminant required")
    combined = value.numerator * value.denominator
    outside, inside = squarefree_split(combined)
    return Fraction(outside, value.denominator), inside


def surd_parts(value: Surd) -> dict[str, Any]:
    """Return the canonical serializable exact representation."""
    return {
        "rational": fraction_text(value.rational),
        "sqrt_coefficient": fraction_text(value.coefficient),
        "sqrt_radicand": value.radicand,
    }


def parse_published_surd(text: str) -> Surd:
    """Parse the manifest's deliberately small exact radical grammar."""
    try:
        return Surd(Fraction(text))
    except ValueError:
        pass
    pattern = re.compile(
        r"(?P<sign>-?)\((?P<rational>\d+)\+"
        r"(?:(?P<coefficient>\d+))?sqrt\((?P<radicand>\d+)\)\)"
        r"/(?P<denominator>\d+)"
    )
    match = pattern.fullmatch(text)
    if match is None:
        raise ValueError(f"unsupported published surd: {text}")
    sign = -1 if match.group("sign") else 1
    numerator = int(match.group("rational"))
    coefficient_text = match.group("coefficient")
    coefficient = int(coefficient_text) if coefficient_text else 1
    denominator = int(match.group("denominator"))
    return make_surd(
        Fraction(sign * numerator, denominator),
        Fraction(sign * coefficient, denominator),
        int(match.group("radicand")),
    )


def declared_supports(inputs: dict[str, Any]) -> dict[str, tuple[tuple[int, ...], ...]]:
    """Construct the four declared supports from registered structural inputs."""
    dimension = int(inputs["dimension"])
    coordinate_values = tuple(range(-1, 2))
    bcc_norm = int(inputs["bcc_norm_square"])
    fcc_norm = int(inputs["fcc_norm_square"])
    bcc = tuple(
        sorted(
            vector
            for vector in itertools.product(coordinate_values, repeat=dimension)
            if sum(component * component for component in vector) == bcc_norm
        )
    )
    fcc = tuple(
        sorted(
            vector
            for vector in itertools.product((-1, 1), repeat=dimension)
            if sum(component * component for component in vector) == fcc_norm
        )
    )
    relation_dimension = len(inputs["hex_euclidean_vectors_r_plus_s_sqrt3"][0])
    relation_basis = tuple(
        tuple(int(row == column) for column in range(relation_dimension))
        for row in range(relation_dimension)
    )
    relation_closure = tuple(-sum(vector[column] for vector in relation_basis) for column in range(relation_dimension))
    positive_hex = relation_basis + (relation_closure,)
    hex_support = tuple(
        sorted(
            set(
                positive_hex
                + tuple(tuple(-component for component in vector) for vector in positive_hex)
            )
        )
    )
    lamellar = ((-1,), (1,))
    return {"BCC": bcc, "FCC": fcc, "HEX": hex_support, "LAM": lamellar}


def zero_sum_count(support: tuple[tuple[int, ...], ...], order: int) -> int:
    """Count ordered zero-sum tuples by an independently implemented DP."""
    dimension = len(support[0])
    counts: dict[tuple[int, ...], int] = {(0,) * dimension: 1}
    for _ in range(order):
        updated: defaultdict[tuple[int, ...], int] = defaultdict(int)
        for total, multiplicity in counts.items():
            for vector in support:
                target = tuple(
                    total[index] + vector[index] for index in range(dimension)
                )
                updated[target] += multiplicity
        counts = dict(updated)
    return counts.get((0,) * dimension, 0)


def polynomial_at(
    coefficients: tuple[Fraction, Fraction, Fraction],
    value: Fraction,
) -> Fraction:
    """Evaluate a rational cubic with no constant term."""
    linear, quadratic, cubic = coefficients
    return linear * value + quadratic * value * value + cubic * value * value * value


def polynomial_at_surd(
    coefficients: tuple[Fraction, Fraction, Fraction],
    value: Surd,
) -> Surd:
    """Evaluate the cubic exactly inside one quadratic field."""
    linear, quadratic, cubic = coefficients
    return add_surd(
        add_surd(
            scale_surd(value, linear),
            scale_surd(power_surd(value, 2), quadratic),
        ),
        scale_surd(power_surd(value, 3), cubic),
    )


def parse_hex_vectors(inputs: dict[str, Any]) -> list[tuple[tuple[Fraction, Fraction], ...]]:
    """Parse coordinates a+b*sqrt(3) without evaluating the radical."""
    vectors: list[tuple[tuple[Fraction, Fraction], ...]] = []
    for vector in inputs["hex_euclidean_vectors_r_plus_s_sqrt3"]:
        coordinates = tuple(
            (parse_fraction(rational), parse_fraction(sqrt_coefficient))
            for rational, sqrt_coefficient in vector
        )
        vectors.append(coordinates)
    return vectors


def quadratic_dot(
    left: tuple[tuple[Fraction, Fraction], ...],
    right: tuple[tuple[Fraction, Fraction], ...],
) -> tuple[Fraction, Fraction]:
    """Dot vectors in Q(sqrt(3)) and return rational and radical parts."""
    rational = Fraction(0)
    radical = Fraction(0)
    radicand = Fraction(3)
    for (left_r, left_s), (right_r, right_s) in zip(left, right, strict=True):
        rational += left_r * right_r + radicand * left_s * right_s
        radical += left_r * right_s + left_s * right_r
    return rational, radical


def v2(value: int) -> int:
    """Return the exact two-adic valuation of a positive integer."""
    if value <= 0:
        raise ValueError("v2 requires a positive integer")
    valuation = 0
    remainder = value
    while remainder % 2 == 0:
        remainder //= 2
        valuation += 1
    return valuation


def derive_fraction_exact(manifest: dict[str, Any]) -> dict[str, Any]:
    """Derive the substantive payload before consulting any test oracle."""
    inputs = manifest["registered_inputs"]
    mu2 = parse_fraction(inputs["mu2"])
    coupling_quartic = parse_fraction(inputs["lambda"])
    coupling_sextic = parse_fraction(inputs["gamma"])
    intensity = parse_fraction(inputs["production_intensity"])
    cap_marker = parse_fraction(inputs["b1_intensity_cap"])
    conversion = int(inputs["amplitude_conversion"])
    support_map = declared_supports(inputs)

    moments: dict[str, dict[str, Any]] = {}
    coefficients: dict[str, list[str]] = {}
    fixed_values: dict[str, str] = {}
    fixed_derivatives: dict[str, str] = {}
    radial_minimizers: dict[str, dict[str, Any]] = {}
    radial_minimum_energies: dict[str, dict[str, Any]] = {}
    root_brackets: dict[str, list[int]] = {}
    energy_brackets: dict[str, list[int]] = {}
    root_objects: dict[str, Surd] = {}
    energy_objects: dict[str, Surd] = {}
    support_invariants: dict[str, bool] = {}
    amplitude_checks: dict[str, bool] = {}

    for family in FAMILY_ORDER:
        support = support_map[family]
        zero = (0,) * len(support[0])
        support_invariants[family] = (
            len(support) == len(set(support))
            and zero not in support
            and all(tuple(-component for component in vector) in support for vector in support)
        )
        n2 = zero_sum_count(support, 2)
        n4 = zero_sum_count(support, 4)
        n6 = zero_sum_count(support, 6)
        k4 = Fraction(n4, n2 * n2)
        k6 = Fraction(n6, n2 * n2 * n2)
        moments[family] = {
            "N2": n2,
            "N4": n4,
            "N6": n6,
            "K4": fraction_text(k4),
            "K6": fraction_text(k6),
        }

        linear = mu2 / 2
        quadratic = coupling_quartic * k4 / 2
        cubic = coupling_sextic * k6 / 3
        polynomial = (linear, quadratic, cubic)
        coefficients[family] = [fraction_text(item) for item in polynomial]
        fixed = polynomial_at(polynomial, intensity)
        derivative = linear + 2 * quadratic * intensity + 3 * cubic * intensity * intensity
        fixed_values[family] = fraction_text(fixed)
        fixed_derivatives[family] = fraction_text(derivative)

        discriminant = quadratic * quadratic - 3 * linear * cubic
        radical_coefficient, radicand = sqrt_fraction_parts(discriminant)
        rational_part = -quadratic / (3 * cubic)
        radical_part = radical_coefficient / (3 * cubic)
        smaller = make_surd(rational_part, -radical_part, radicand)
        larger = make_surd(rational_part, radical_part, radicand)
        smaller_second = add_surd(
            Surd(2 * quadratic), scale_surd(smaller, 6 * cubic)
        )
        larger_second = add_surd(
            Surd(2 * quadratic), scale_surd(larger, 6 * cubic)
        )
        minimum_energy = polynomial_at_surd(polynomial, larger)
        radial_minimizers[family] = {
            **surd_parts(larger),
            "f_second_positive": compare_surd_zero(larger_second) > 0,
            "smaller_f_second_negative": compare_surd_zero(smaller_second) < 0,
        }
        radial_minimum_energies[family] = surd_parts(minimum_energy)
        root_floor = floor_scaled(larger, 10**6)
        energy_floor = floor_scaled(minimum_energy, 10**6)
        root_brackets[family] = [root_floor, root_floor + 1]
        energy_brackets[family] = [energy_floor, energy_floor + 1]
        root_objects[family] = larger
        energy_objects[family] = minimum_energy

        signed_intensity_coefficient = Fraction(n2, conversion * conversion)
        cosine_intensity_coefficient = Fraction(n2, 2) / 2
        amplitude_checks[family] = (
            signed_intensity_coefficient == cosine_intensity_coefficient
        )

    fixed_order = sorted(FAMILY_ORDER, key=lambda family: Fraction(fixed_values[family]))
    radial_order = sorted(FAMILY_ORDER, key=lambda family: energy_brackets[family][0])

    hex_vectors = parse_hex_vectors(inputs)
    hex_gram = [
        [quadratic_dot(left, right) for right in hex_vectors]
        for left in hex_vectors
    ]
    hex_equal_shell = all(
        hex_gram[index][index] == (Fraction(1), Fraction(0))
        for index in range(len(hex_vectors))
    )
    hex_pair_angles = sorted(
        {
            fraction_text(hex_gram[left][right][0])
            for left in range(len(hex_vectors))
            for right in range(left + 1, len(hex_vectors))
            if hex_gram[left][right][1] == 0
        }
    )
    hex_all_dots_rational = all(
        radical == 0
        for row in hex_gram
        for _, radical in row
    )

    q0 = parse_fraction(inputs["math396_q0"])
    box_length = parse_fraction(inputs["math396_box_length"])
    grid_n = int(inputs["math396_grid_N"])
    shell_ratio_coefficient = q0 * box_length / 2
    bcc_parity = v2(int(inputs["bcc_norm_square"])) % 2
    fcc_parity = v2(int(inputs["fcc_norm_square"])) % 2

    all_fixed_positive = all(Fraction(fixed_values[name]) > 0 for name in FAMILY_ORDER)
    all_fixed_nonstationary = all(
        Fraction(fixed_derivatives[name]) != 0 for name in FAMILY_ORDER
    )
    all_radial_negative = all(
        compare_surd_zero(energy_objects[name]) < 0 for name in FAMILY_ORDER
    )
    all_radial_above_cap = all(
        compare_surd_zero(subtract_rational(root_objects[name], cap_marker)) > 0
        for name in FAMILY_ORDER
    )

    return {
        "moments": moments,
        "polynomial_coefficients": coefficients,
        "fixed_values": fixed_values,
        "fixed_derivatives": fixed_derivatives,
        "fixed_order": fixed_order,
        "radial_minimizers": radial_minimizers,
        "radial_minimum_energies": radial_minimum_energies,
        "root_brackets_millionths": root_brackets,
        "energy_brackets_millionths": energy_brackets,
        "radial_order": radial_order,
        "all_fixed_values_positive": all_fixed_positive,
        "all_fixed_derivatives_nonzero": all_fixed_nonstationary,
        "all_radial_energies_negative": all_radial_negative,
        "all_radial_minima_above_cap_marker": all_radial_above_cap,
        "support_invariants": support_invariants,
        "amplitude_crosswalk": all(amplitude_checks.values()),
        "hex_equal_shell": hex_equal_shell,
        "hex_pair_angles": hex_pair_angles,
        "hex_all_dots_rational": hex_all_dots_rational,
        "offgrid_transcendence_form": (
            q0 != 0 and box_length != 0 and grid_n > 0
        ),
        "bcc_component_offgrid": (
            q0 != 0 and box_length != 0 and int(inputs["bcc_norm_square"]) > 0
        ),
        "fcc_component_offgrid": (
            q0 != 0 and box_length != 0 and int(inputs["fcc_norm_square"]) > 0
        ),
        "standard_cubic_torus_valuation_obstruction": bcc_parity != fcc_parity,
        "standard_cubic_torus_v2_parities": [bcc_parity, fcc_parity],
        "math396_grid_N": grid_n,
        "shell_ratio_form": pi_quotient_text(shell_ratio_coefficient),
    }


def ast_contract() -> dict[str, Any]:
    """Audit the independent-lane source discipline through its own AST."""
    raw = SCRIPT.read_bytes()
    text = raw.decode("ascii")
    tree = ast.parse(text)
    imported_roots: set[str] = set()
    dynamic_calls: list[str] = []
    inexact_literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "compile", "__import__", "float", "complex"}:
                dynamic_calls.append(node.func.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
            inexact_literals.append(repr(node.value))
    docstring = ast.get_docstring(tree, clean=False) or ""
    forbidden_imports = {"sympy", "numpy", "scipy", "mpmath", "cmath", "importlib"}
    primary_module = SLUG.replace("-", "_")
    return {
        "ascii": text.encode("ascii") == raw,
        "lf_only": b"\r" not in raw,
        "final_lf": raw.endswith(b"\n"),
        "forbidden_imports": sorted(imported_roots & forbidden_imports),
        "primary_imported": primary_module in imported_roots,
        "dynamic_or_inexact_calls": dynamic_calls,
        "inexact_literals": inexact_literals,
        "docstring_contract": all(
            token in docstring for token in ("Purpose:", "Convention:", "Formula:")
        ),
    }


def load_json_lines(path: Path) -> list[dict[str, Any]]:
    """Load nonempty JSONL records with line-local parsing errors."""
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"invalid JSONL {path}:{line_number}: {exc}") from exc
    return records


def gate_section(markdown: str, heading: str) -> str:
    """Extract exactly one canonical gate section."""
    pattern = re.compile(
        rf"^### \*\*{re.escape(heading)}\*\*\s*$([\s\S]*?)(?=^### |\Z)",
        re.MULTILINE,
    )
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one gate section {heading}, found {len(matches)}")
    return matches[0]


def formal_lifecycle(manifest: dict[str, Any], audit: Audit) -> None:
    """Check exact formal authorities after integration, without run-order coupling."""
    closed = manifest["closed_gate_ids"]
    opened = manifest["open_gate_ids"]
    gates_text = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    for gate in closed:
        section = gate_section(gates_text, gate)
        audit.check(
            f"formal closed gate {gate}",
            "**Status:** CLOSED" in section,
            section[:240],
            "one CLOSED gate section",
            "formal",
        )
    for gate in opened:
        section = gate_section(gates_text, gate)
        open_marker = "**Status:** OPEN" in section or (
            gate == "C6-BCC-PREMISE-BLOCKED"
            and "**Discharge path:** BLOCKED" in section
            and "remain OPEN" in section
        )
        audit.check(
            f"formal open gate {gate}",
            open_marker,
            section[:240],
            "one OPEN gate section",
            "formal",
        )

    ledger = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    result_tokens = (
        manifest["version"],
        manifest["exploration_id"],
        "current proof-first authority",
        "R-169 v1.3 certificate",
        "prior proof-first authority",
        "No R-169 v1.4 PDF",
    )
    audit.check(
        "formal result authority",
        all(token in ledger for token in result_tokens),
        [token for token in result_tokens if token in ledger],
        list(result_tokens),
        "formal",
    )

    explorations = [
        record
        for record in load_json_lines(REPO / "explorations/log.jsonl")
        if record.get("id") == manifest["exploration_id"]
    ]
    audit.check(
        "formal exploration unique",
        len(explorations) == 1,
        len(explorations),
        1,
        "formal",
    )
    exploration = explorations[0]
    formal_refs = exploration.get("formal_refs", {})
    exploration_ok = (
        exploration.get("task_id") == manifest["task_id"]
        and manifest["result_id"] in formal_refs.get("results", [])
        and set(manifest["reused_negative_ids"]).issubset(
            formal_refs.get("negatives", [])
        )
        and set(closed + opened).issubset(exploration.get("gate_ids", []))
    )
    audit.check(
        "formal exploration topology",
        exploration_ok,
        {
            key: exploration.get(key)
            for key in ("task_id", "verdict", "gate_ids", "formal_refs")
        },
        "T-055 with exact result, negative and gate bindings",
        "formal",
    )

    event_contract = manifest["formal_integration"]
    events = load_json_lines(REPO / "changelog/log.jsonl")
    matches = [
        (ordinal, event)
        for ordinal, event in enumerate(events, start=1)
        if event.get("id") == event_contract["event_id"]
    ]
    unique_event = len(matches) == 1
    ordinal, event = matches[0] if unique_event else (None, {})
    exact_header = f"[{event_contract['event_title']}] - 2026-08-14"
    audit.check(
        "formal changelog identity",
        unique_event
        and ordinal == event_contract["event_ordinal"]
        and event.get("header") == exact_header,
        {"total_events": len(events), "matches": matches},
        {"ordinal": event_contract["event_ordinal"], "header": exact_header},
        "formal",
    )

    legacy_contract = manifest["legacy_assessment"]
    record_path = REPO / legacy_contract["path"]
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record_ok = (
        record.get("record_id") == legacy_contract["record_id"]
        and record.get("source_ids") == legacy_contract["source_ids"]
        and record.get("pinned_source_ids_sha256")
        == legacy_contract["pinned_source_ids_sha256"]
        and record.get("claims") == legacy_contract["claims"]
        and record.get("gates") == legacy_contract["gates"]
        and record.get("current_assessment") == legacy_contract["assessment"]
        and record.get("status_axes", {}).get("revalidation") == "pass"
    )
    audit.check(
        "formal legacy assessment",
        record_ok,
        {
            key: record.get(key)
            for key in (
                "record_id",
                "source_ids",
                "pinned_source_ids_sha256",
                "claims",
                "gates",
                "current_assessment",
                "status_axes",
            )
        },
        "exact narrow reviewed legacy record",
        "formal",
    )


def run(staged: bool) -> dict[str, Any]:
    """Execute the independent arithmetic, provenance and lifecycle audit."""
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    certificate = CERTIFICATE.read_text(encoding="ascii")
    derived = derive_fraction_exact(manifest)

    identity_ok = (
        manifest.get("schema")
        == "tect/pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split/1.0"
        and manifest.get("version") == "R-169 v1.4"
        and manifest.get("exploration_id") == "EXP-000862"
        and manifest.get("tier") == "T0"
        and manifest.get("claim_bearing") is False
        and manifest.get("new_negative_ids") == []
        and manifest.get("reused_negative_ids")
        == ["R-2026-06-23-b3-bcc-structural-selection"]
    )
    audit.check(
        "manifest identity",
        identity_ok,
        {
            key: manifest.get(key)
            for key in (
                "schema",
                "version",
                "exploration_id",
                "tier",
                "claim_bearing",
                "new_negative_ids",
                "reused_negative_ids",
            )
        },
        "exact R-169 v1.4 T0 no-new-negative identity",
        "identity",
    )

    source_hashes = {
        name: normalized_sha256(REPO / authority["path"])
        for name, authority in manifest["source_authorities"].items()
    }
    expected_hashes = {
        name: authority["sha256"]
        for name, authority in manifest["source_authorities"].items()
    }
    audit.check(
        "frozen normalized source hashes",
        source_hashes == expected_hashes,
        source_hashes,
        expected_hashes,
        "provenance",
    )

    content_hashes = {
        name: source_content_sha256(REPO / authority["path"])
        for name, authority in manifest["source_authorities"].items()
        if "source_content_sha256" in authority
    }
    expected_content_hashes = {
        name: authority["source_content_sha256"]
        for name, authority in manifest["source_authorities"].items()
        if "source_content_sha256" in authority
    }
    audit.check(
        "preserved raw or decoded source hashes",
        content_hashes == expected_content_hashes,
        content_hashes,
        expected_content_hashes,
        "provenance",
    )

    math396 = source_payload(
        REPO / manifest["source_authorities"]["math396_source_wrapper"]["path"]
    )
    math424 = source_payload(
        REPO / manifest["source_authorities"]["math424_exact_counter"]["path"]
    )
    math400 = source_payload(
        REPO / manifest["source_authorities"]["math400_hartree_owner"]["path"]
    )
    a1_manifest = source_payload(
        REPO / manifest["source_authorities"]["a1_production_manifest"]["path"]
    )
    provenance_tokens_ok = (
        all(
            token in math396
            for token in (
                b'"K4": 1.0',
                b'"K6": 2.5',
                b"free_energy_canonical",
                b"mu2 + Y_LOCKED * Q0_PHYSICAL**4",
            )
        )
        and all(
            token in math424
            for token in (
                b"def n_tuples_zero_sum",
                b"N4 = n_tuples_zero_sum",
                b"N6 = n_tuples_zero_sum",
                b'SHELLS["BCC"]',
            )
        )
        and all(
            token in math400
            for token in (
                b"r_bare = mu2 + Y_LOCKED * Q0_LOCKED ** 4",
                b"def solve_self_consistency",
            )
        )
        and all(
            token in a1_manifest
            for token in (
                b'"mu2": 0.26',
                b"F_family",
                b"F_lock",
                b"F_ClassII",
            )
        )
    )
    audit.check(
        "source-role firewall",
        provenance_tokens_ok,
        provenance_tokens_ok,
        "Math396 stale table/grid, Math424 counts, Math400 Hartree and A1 owner tokens",
        "provenance",
    )

    oracle = manifest["test_oracles"]
    oracle_moments = {
        family: {
            "N2": values[0],
            "N4": values[1],
            "N6": values[2],
            "K4": values[3],
            "K6": values[4],
        }
        for family, values in oracle["moments"].items()
    }
    audit.check(
        "independent exact zero-sum moments",
        derived["moments"] == oracle_moments
        and all(derived["support_invariants"].values()),
        {
            "moments": derived["moments"],
            "support_invariants": derived["support_invariants"],
        },
        oracle_moments,
        "moments",
    )

    manifest_moments = {
        family: values
        for family, values in manifest["exact_moments"].items()
        if family in FAMILY_ORDER
    }
    audit.check(
        "manifest moment and nonduplication crosswalk",
        derived["moments"] == manifest_moments
        and "Math424 already owns" in manifest["exact_moments"]["nonduplication"],
        derived["moments"],
        manifest_moments,
        "moments",
    )

    audit.check(
        "corrected polynomial coefficients",
        derived["polynomial_coefficients"] == manifest["polynomials"],
        derived["polynomial_coefficients"],
        manifest["polynomials"],
        "polynomial",
    )

    fixed_values_oracle = dict(zip(FAMILY_ORDER, oracle["fixed_values"], strict=True))
    fixed_derivatives_oracle = dict(
        zip(FAMILY_ORDER, oracle["fixed_derivatives"], strict=True)
    )
    fixed_ok = (
        derived["fixed_values"] == fixed_values_oracle
        and derived["fixed_derivatives"] == fixed_derivatives_oracle
        and derived["fixed_order"] == oracle["fixed_order"]
        and derived["all_fixed_values_positive"]
        and derived["all_fixed_derivatives_nonzero"]
    )
    audit.check(
        "fixed-intensity endpoint and owner split",
        fixed_ok,
        {
            key: derived[key]
            for key in (
                "fixed_values",
                "fixed_derivatives",
                "fixed_order",
                "all_fixed_values_positive",
                "all_fixed_derivatives_nonzero",
            )
        },
        "oracle values with strict positive order and no stationary derivative",
        "endpoint",
    )

    published_roots = {
        family: surd_parts(parse_published_surd(text))
        for family, text in manifest["radial_owner"]["positive_radial_minimizers"].items()
    }
    published_energies = {
        family: surd_parts(parse_published_surd(text))
        for family, text in manifest["radial_owner"]["minimum_energies"].items()
    }
    derived_roots = {
        family: {
            key: value
            for key, value in data.items()
            if key in {"rational", "sqrt_coefficient", "sqrt_radicand"}
        }
        for family, data in derived["radial_minimizers"].items()
    }
    root_oracle = dict(
        zip(FAMILY_ORDER, oracle["root_brackets_millionths"], strict=True)
    )
    energy_oracle = dict(
        zip(oracle["radial_order"], oracle["energy_brackets_millionths"], strict=True)
    )
    radial_ok = (
        derived_roots == published_roots
        and derived["radial_minimum_energies"] == published_energies
        and derived["root_brackets_millionths"] == root_oracle
        and derived["energy_brackets_millionths"] == energy_oracle
        and derived["radial_order"] == oracle["radial_order"]
        and derived["all_radial_energies_negative"]
        and all(
            item["f_second_positive"] and item["smaller_f_second_negative"]
            for item in derived["radial_minimizers"].values()
        )
    )
    audit.check(
        "exact radial surds, brackets, Hessians and order",
        radial_ok,
        {
            "roots": derived_roots,
            "energies": derived["radial_minimum_energies"],
            "root_brackets": derived["root_brackets_millionths"],
            "energy_brackets": derived["energy_brackets_millionths"],
            "order": derived["radial_order"],
        },
        {
            "roots": published_roots,
            "energies": published_energies,
            "root_brackets": root_oracle,
            "energy_brackets": energy_oracle,
            "order": oracle["radial_order"],
        },
        "radial",
    )

    representation_ok = (
        derived["amplitude_crosswalk"]
        and derived["hex_equal_shell"]
        and derived["hex_all_dots_rational"]
        and derived["hex_pair_angles"] == ["-1/2"]
    )
    audit.check(
        "amplitude and HEX type firewalls",
        representation_ok,
        {
            key: derived[key]
            for key in (
                "amplitude_crosswalk",
                "hex_equal_shell",
                "hex_all_dots_rational",
                "hex_pair_angles",
            )
        },
        "a_cos=2c and exact equal-shell Euclidean HEX Gram",
        "convention",
    )

    owner_ok = (
        derived["all_radial_minima_above_cap_marker"]
        and derived["offgrid_transcendence_form"]
        and derived["bcc_component_offgrid"]
        and derived["fcc_component_offgrid"]
        and derived["standard_cubic_torus_valuation_obstruction"]
        and derived["standard_cubic_torus_v2_parities"] == [1, 0]
    )
    audit.check(
        "cap, finite-grid and v2 owner firewalls",
        owner_ok,
        {
            key: derived[key]
            for key in (
                "all_radial_minima_above_cap_marker",
                "offgrid_transcendence_form",
                "bcc_component_offgrid",
                "fcc_component_offgrid",
                "standard_cubic_torus_valuation_obstruction",
                "standard_cubic_torus_v2_parities",
                "shell_ratio_form",
            )
        },
        "cross-owner cap only, exact off-grid obstruction and odd/even v2 parity",
        "scope",
    )

    certificate_flat = " ".join(certificate.split())
    certificate_tokens = (
        "reconstructed and corrected equal-amplitude",
        "a_cos=2c",
        "relation coordinates as Euclidean momenta would be a type error",
        "0 < BCC < FCC < HEX < LAM",
        "LAM < HEX < FCC < BCC < 0",
        "off-grid-confounded",
        "only nonapplicability is established",
        "B3 remains `REFUTED/RETIRED`",
        "Math424 already owns",
        "physical empty space",
        "Devil's-advocate audit",
        "External review is invited",
        "No v1.4 PDF is issued",
    )
    audit.check(
        "certificate theorem, nonduplication and scope",
        all(token in certificate_flat for token in certificate_tokens),
        [token for token in certificate_tokens if token in certificate_flat],
        list(certificate_tokens),
        "scope",
    )

    owner_text = " ".join(manifest["owner_definition"].values())
    boundary_text = " ".join(manifest["owner_firewalls"].values())
    no_overclaim_ok = all(
        token in owner_text + " " + boundary_text + " " + manifest["no_overclaim"]
        for token in (
            "not the obsolete Math396 coefficient table",
            "raw finite-grid output",
            "not the A1 side-16",
            "full Reading-H Hartree functional",
            "physical-empty",
            "transverse/PDE/continuum stability",
            "no present physical-empty sign",
        )
    )
    audit.check(
        "owner and no-overclaim prose contract",
        no_overclaim_ok,
        no_overclaim_ok,
        "all declared owner exclusions retained",
        "scope",
    )

    legacy = manifest["legacy_assessment"]
    legacy_digest = hashlib.sha256(
        "\n".join(legacy["source_ids"]).encode("utf-8")
    ).hexdigest()
    legacy_contract_ok = (
        legacy["record_id"] == "LEG-T055-COMMON-BOHR-FDECL-001"
        and legacy_digest == legacy["pinned_source_ids_sha256"]
        and legacy["gates"] == ["C6-BCC-PREMISE-BLOCKED"]
        and legacy["assessment"] == "partially-reusable"
        and "A1-PRODUCTION-FUNCTIONAL-REALISATION" not in legacy["claims"]
    )
    audit.check(
        "narrow legacy assessment contract",
        legacy_contract_ok,
        {
            "digest": legacy_digest,
            "source_ids": legacy["source_ids"],
            "claims": legacy["claims"],
            "gates": legacy["gates"],
            "assessment": legacy["assessment"],
        },
        "nine pinned sources and existing legacy views only",
        "legacy",
    )

    ast_report = ast_contract()
    ast_ok = (
        ast_report["ascii"]
        and ast_report["lf_only"]
        and ast_report["final_lf"]
        and ast_report["forbidden_imports"] == []
        and not ast_report["primary_imported"]
        and ast_report["dynamic_or_inexact_calls"] == []
        and ast_report["inexact_literals"] == []
        and ast_report["docstring_contract"]
    )
    audit.check(
        "independent AST and text discipline",
        ast_ok,
        ast_report,
        "ASCII LF final-LF, Fraction-only, no primary/dynamic/inexact lane",
        "code-discipline",
    )

    if staged:
        authority_text = "\n".join(
            (REPO / path).read_text(encoding="utf-8")
            for path in (
                "claims/GATES.md",
                "RESULTS-LEDGER.md",
                "explorations/log.jsonl",
                "changelog/log.jsonl",
            )
        )
        absent_paths = [
            REPO / legacy["path"],
            REPO
            / "claims/C6-SPACETIME-SIGNATURE/runs"
            / f"2026-08-14-primary-{SLUG}/result.json",
            DEFAULT_OUTPUT,
            REPO
            / "claims/C6-SPACETIME-SIGNATURE/runs"
            / f"2026-08-14-integrated-{SLUG}/result.json",
        ]
        new_tokens = [
            manifest["exploration_id"],
            manifest["version"],
            *manifest["closed_gate_ids"],
        ]
        events = load_json_lines(REPO / "changelog/log.jsonl")
        matches = [(ordinal, event) for ordinal, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
        if matches:
            audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        else:
            lifecycle_ok = (
                all(token not in authority_text for token in new_tokens)
                and not any(path.exists() for path in absent_paths)
            )
            audit.check(
                "preformal lifecycle absence",
                lifecycle_ok,
                {
                    "tokens_absent": all(token not in authority_text for token in new_tokens),
                    "absent_paths": {
                        str(path.relative_to(REPO)): not path.exists()
                        for path in absent_paths
                    },
                },
                "new authorities, legacy record and all runs absent",
                "lifecycle",
            )
    else:
        formal_lifecycle(manifest, audit)

    return {
        "schema": "tect/pre-a-t055-legacy-sma-common-bohr-moment-radial-owner-route-split-independent/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": derived,
        "source_hash": normalized_sha256(SCRIPT),
        "manifest_hash": normalized_sha256(MANIFEST),
        "certificate_hash": normalized_sha256(CERTIFICATE),
        "verdict": "PASS",
    }


def main() -> int:
    """Parse CLI options, run the audit and optionally store atomically."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(
        f"INDEPENDENT PASS {payload['assertions']}/{payload['assertions']} "
        f"mode={payload['mode']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
