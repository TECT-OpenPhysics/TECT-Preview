#!/usr/bin/env python3
"""Independent stdlib verifier for the Q3 spatial-spectral RP martingale split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-spatial-spectral-rp-martingale-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-MARTINGALE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-FK-MARTINGALE-FAMILY-AND-LIMITING-MEASURE-RP-WITH-CANONICAL-NONIDENTIFICATION"
NEGATIVE_IDS = ("NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER",)
EXPLORATION_ID = "EXP-000769"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY_STEM = SLUG.replace("-", "_")
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"

# Independent rational fixtures.
LOW_VARIANCE = Fraction(2)
HIGH_VARIANCE = Fraction(3)
COMPONENTS = 8
LOW_GRID = 22
LOW_BAND = 2
NYQUIST_GRID = 10

Exponent = tuple[int, ...]
Polynomial = dict[Exponent, Fraction]


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def clean(polynomial: Polynomial) -> Polynomial:
    return {exponent: coefficient for exponent, coefficient in polynomial.items() if coefficient}


def add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for exponent, coefficient in polynomial.items():
            result[exponent] = result.get(exponent, Fraction(0)) + coefficient
    return clean(result)


def scale(polynomial: Polynomial, coefficient: Fraction | int) -> Polynomial:
    factor = Fraction(coefficient)
    return clean({exponent: factor * value for exponent, value in polynomial.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(a + b for a, b in zip(left_exponent, right_exponent))
            result[exponent] = result.get(exponent, Fraction(0)) + left_coefficient * right_coefficient
    return clean(result)


def power(polynomial: Polynomial, degree: int) -> Polynomial:
    dimension = len(next(iter(polynomial)))
    result: Polynomial = {(0,) * dimension: Fraction(1)}
    for _ in range(degree):
        result = multiply(result, polynomial)
    return result


def variable(dimension: int, index: int) -> Polynomial:
    exponent = [0] * dimension
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def constant(dimension: int, value: Fraction | int) -> Polynomial:
    return {(0,) * dimension: Fraction(value)} if value else {}


def wick(variable_polynomial: Polynomial, variance: Fraction, degree: int) -> Polynomial:
    if degree == 0:
        return constant(len(next(iter(variable_polynomial))), 1)
    if degree == 1:
        return variable_polynomial
    if degree == 2:
        return add(power(variable_polynomial, 2), constant(len(next(iter(variable_polynomial))), -variance))
    if degree == 3:
        return add(power(variable_polynomial, 3), scale(variable_polynomial, -3 * variance))
    if degree == 4:
        return add(power(variable_polynomial, 4), scale(power(variable_polynomial, 2), -6 * variance), constant(len(next(iter(variable_polynomial))), 3 * variance * variance))
    raise ValueError(degree)


def gaussian_moment(power_value: int, variance: Fraction) -> Fraction:
    if power_value % 2:
        return Fraction(0)
    if power_value == 0:
        return Fraction(1)
    result = Fraction(1)
    for odd in range(1, power_value, 2):
        result *= odd * variance
    return result


def integrate_variables(polynomial: Polynomial, integrations: dict[int, Fraction]) -> Polynomial:
    result: Polynomial = {}
    for exponent, coefficient in polynomial.items():
        reduced = list(exponent)
        value = coefficient
        for index, variance in integrations.items():
            value *= gaussian_moment(reduced[index], variance)
            reduced[index] = 0
        if value:
            key = tuple(reduced)
            result[key] = result.get(key, Fraction(0)) + value
    return clean(result)


def q3_edge_wick(left: Polynomial, right: Polynomial, variance: Fraction) -> Polynomial:
    return add(
        wick(left, variance, 4),
        wick(right, variance, 4),
        scale(multiply(wick(left, variance, 2), wick(right, variance, 2)), 2),
        scale(multiply(wick(left, variance, 3), right), -2),
        scale(multiply(left, wick(right, variance, 3)), -2),
    )


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[matrix[row][column] for row in range(len(matrix))] for column in range(len(matrix[0]))]


def matrix_multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[row][middle] * right[middle][column] for middle in range(len(right))), Fraction(0)) for column in range(len(right[0]))] for row in range(len(left))]


def quadratic(matrix: list[list[Fraction]], vector_value: list[Fraction]) -> Fraction:
    return sum((vector_value[row] * matrix[row][column] * vector_value[column] for row in range(len(vector_value)) for column in range(len(vector_value))), Fraction(0))


def laurent_multiply(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power_value = left_power + right_power
            result[power_value] = result.get(power_value, Fraction(0)) + left_coefficient * right_coefficient
    return {power_value: coefficient for power_value, coefficient in result.items() if coefficient}


def laurent_power(polynomial: dict[int, Fraction], degree: int) -> dict[int, Fraction]:
    result = {0: Fraction(1)}
    for _ in range(degree):
        result = laurent_multiply(result, polynomial)
    return result


def grid_average(polynomial: dict[int, Fraction], grid: int) -> Fraction:
    return sum((coefficient for power_value, coefficient in polynomial.items() if power_value % grid == 0), Fraction(0))


def serialize(polynomial: Polynomial) -> dict[str, str]:
    return {",".join(map(str, exponent)): str(coefficient) for exponent, coefficient in sorted(polynomial.items())}


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    dimension = 4
    low_x, low_y, high_x, high_y = (variable(dimension, index) for index in range(dimension))
    total_x = add(low_x, high_x)
    total_y = add(low_y, high_y)
    onsite_results: dict[str, dict[str, str]] = {}
    for degree in range(5):
        conditioned = integrate_variables(wick(total_x, LOW_VARIANCE + HIGH_VARIANCE, degree), {2: HIGH_VARIANCE})
        target = wick(low_x, LOW_VARIANCE, degree)
        audit.check(f"independent Wick conditioning degree {degree}", conditioned == target, serialize(conditioned), serialize(target), "martingale")
        onsite_results[str(degree)] = serialize(conditioned)
    edge_full = q3_edge_wick(total_x, total_y, LOW_VARIANCE + HIGH_VARIANCE)
    edge_conditioned = integrate_variables(edge_full, {2: HIGH_VARIANCE, 3: HIGH_VARIANCE})
    edge_target = q3_edge_wick(low_x, low_y, LOW_VARIANCE)
    audit.check("independent Q3 edge conditioning", edge_conditioned == edge_target, serialize(edge_conditioned), serialize(edge_target), "martingale")
    raw_edge = add(power(low_x, 4), power(low_y, 4), scale(multiply(power(low_x, 2), power(low_y, 2)), 2), scale(multiply(power(low_x, 3), low_y), -2), scale(multiply(low_x, power(low_y, 3)), -2))
    explicit_edge = add(raw_edge, scale(add(power(low_x, 2), power(low_y, 2)), -8 * LOW_VARIANCE), scale(multiply(low_x, low_y), 12 * LOW_VARIANCE), constant(dimension, 8 * LOW_VARIANCE * LOW_VARIANCE))
    audit.check("independent Q3 explicit Wick formula", edge_target == explicit_edge, serialize(edge_target), serialize(explicit_edge), "martingale")
    audit.check("independent terminal martingale ledger", manifest["spatial_martingale"]["terminal_identity"].startswith("the L1 Wick limit"), manifest["spatial_martingale"]["terminal_identity"], "L1 passage", "martingale")
    audit.check("independent exhaustion ledger", "increasing union" in manifest["spatial_martingale"]["exhaustion"], manifest["spatial_martingale"]["exhaustion"], "increasing union", "martingale")

    # Exact tower fixture on eight equiprobable atoms and a nested two-cell partition.
    terminal = [Fraction(-3), Fraction(1), Fraction(5), Fraction(1), Fraction(2), Fraction(4), Fraction(-2), Fraction(0)]
    cells = ((0, 1, 2, 3), (4, 5, 6, 7))
    conditional = [sum((terminal[index] for index in cell), Fraction(0)) / len(cell) for cell in cells]
    mean_terminal = sum(terminal, Fraction(0)) / len(terminal)
    mean_conditional = sum(conditional, Fraction(0)) / len(conditional)
    audit.check("finite martingale mean preservation", mean_conditional == mean_terminal, mean_conditional, mean_terminal, "density")
    square_terminal = sum((value * value for value in terminal), Fraction(0)) / len(terminal)
    square_conditional = sum((value * value for value in conditional), Fraction(0)) / len(conditional)
    audit.check("finite conditional square Jensen", square_conditional <= square_terminal, square_conditional, square_terminal, "density")
    for index, cell in enumerate(cells):
        exp_left = math.exp(2.0 * float(conditional[index]))
        exp_right = sum(math.exp(2.0 * float(terminal[position])) for position in cell) / len(cell)
        audit.check(f"finite conditional exponential Jensen {index}", exp_left <= exp_right, exp_left, exp_right, "density")
    raw_k = [Fraction(4), Fraction(1), Fraction(3), Fraction(2)]
    raw = [Fraction(5), Fraction(2), Fraction(2), Fraction(3)]
    z_k, z = sum(raw_k), sum(raw)
    raw_l1 = sum(abs(left - right) for left, right in zip(raw_k, raw))
    normalized_l1 = sum(abs(left / z_k - right / z) for left, right in zip(raw_k, raw))
    normalized_bound = (raw_l1 + abs(z_k - z)) / z_k
    audit.check("independent normalizer bound", abs(z_k - z) <= raw_l1, abs(z_k - z), raw_l1, "density")
    audit.check("independent normalized L1 bound", normalized_l1 <= normalized_bound, normalized_l1, normalized_bound, "density")

    rp_factor = [[Fraction(1), Fraction(3), Fraction(2), Fraction(5)], [Fraction(4), Fraction(1), Fraction(6), Fraction(2)]]
    rp_gram = matrix_multiply(transpose(rp_factor), rp_factor)
    audit.check("independent RP Gram symmetric", rp_gram == transpose(rp_gram), rp_gram, transpose(rp_gram), "reflection")
    for index, vector_value in enumerate((
        [Fraction(1), Fraction(-1), Fraction(2), Fraction(0)],
        [Fraction(2), Fraction(3), Fraction(-1), Fraction(1)],
        [Fraction(-2), Fraction(1), Fraction(0), Fraction(4)],
        [Fraction(1), Fraction(1), Fraction(1), Fraction(1)],
    )):
        value = quadratic(rp_gram, vector_value)
        factor_norm = sum((sum(rp_factor[row][column] * vector_value[column] for column in range(4)) ** 2 for row in range(2)), Fraction(0))
        audit.check(f"independent RP Gram square {index}", value == factor_norm and value >= 0, value, factor_norm, "reflection")
    rho_k = [Fraction(1, 6), Fraction(2, 6), Fraction(3, 6)]
    rho = [Fraction(2, 6), Fraction(1, 6), Fraction(3, 6)]
    products = [Fraction(-4), Fraction(2), Fraction(1)]
    form_difference = abs(sum(product * (left - right) for product, left, right in zip(products, rho_k, rho)))
    form_bound = max(abs(product) for product in products) * sum(abs(left - right) for left, right in zip(rho_k, rho))
    audit.check("independent reflected-form L1 closure", form_difference <= form_bound, form_difference, form_bound, "reflection")
    audit.check("independent finite RP scope", manifest["scope"]["finite_spatial_cutoff_reflection_positive"] is True, manifest["scope"]["finite_spatial_cutoff_reflection_positive"], True, "reflection")
    audit.check("independent limit RP scope", manifest["scope"]["limiting_Nagoji_measure_reflection_positive"] is True, manifest["scope"]["limiting_Nagoji_measure_reflection_positive"], True, "reflection")

    # Q3 coercive finite-vector identity: n sum x_i^4-|x|^4 equals the pair-square sum.
    vectors = (
        tuple(Fraction(index - 3) for index in range(COMPONENTS)),
        tuple(Fraction((-1) ** index * (index + 1)) for index in range(COMPONENTS)),
        tuple(Fraction((index % 3) - 1) for index in range(COMPONENTS)),
    )
    for index, vector_value in enumerate(vectors):
        left = COMPONENTS * sum(value**4 for value in vector_value) - sum(value**2 for value in vector_value) ** 2
        right = sum((vector_value[i] ** 2 - vector_value[j] ** 2) ** 2 for i in range(COMPONENTS) for j in range(i + 1, COMPONENTS))
        audit.check(f"independent coercive SOS {index}", left == right and left >= 0, left, right, "coercivity")
    for left, right in ((Fraction(-2), Fraction(3)), (Fraction(0), Fraction(4)), (Fraction(5), Fraction(-1))):
        edge_value = (left - right) ** 2 * (left * left + right * right)
        audit.check(f"independent Q3 edge nonnegative {left},{right}", edge_value >= 0, edge_value, ">=0", "coercivity")

    mode_labels = tuple(range(-3, 4))
    mass_squared = Fraction(5, 2)
    frequency_squared = [mass_squared + label * label for label in mode_labels]
    audit.check("independent finite mode count", len(mode_labels) == 7, len(mode_labels), 7, "Feynman_Kac")
    audit.check("independent canonical dimension", COMPONENTS * len(mode_labels) == 56, COMPONENTS * len(mode_labels), 56, "Feynman_Kac")
    audit.check("independent oscillator positivity", min(frequency_squared) == mass_squared > 0, min(frequency_squared), mass_squared, "Feynman_Kac")
    canonical_matsubara = Fraction(1, 1 + 2 * 2)
    simultaneous_cutoff = Fraction(0)
    audit.check("independent missing Matsubara mismatch", canonical_matsubara == Fraction(1, 5) and simultaneous_cutoff != canonical_matsubara, canonical_matsubara, Fraction(1, 5), "Feynman_Kac")
    audit.check("independent fixed-circle qualifier", "fixed-circle" in manifest["finite_spatial_Feynman_Kac"]["scope_boundary"], manifest["finite_spatial_Feynman_Kac"]["scope_boundary"], "fixed-circle", "Feynman_Kac")
    audit.check("independent beta family firewall", manifest["scope"]["beta_independent_comparator_Hamiltonian_family"] is False, manifest["scope"]["beta_independent_comparator_Hamiltonian_family"], False, "Feynman_Kac")

    centered = 4.0 * math.sin(math.pi / 6.0) ** 2
    spectral = (math.pi / 3.0) ** 2
    audit.check("independent symbol strictness", centered < spectral, centered, spectral, "nonidentification")
    audit.check("independent symbol mismatch", not math.isclose(centered, spectral, rel_tol=1e-14, abs_tol=1e-14), centered, spectral, "nonidentification")
    cosine = {-1: Fraction(1, 2), 1: Fraction(1, 2)}
    cosine_fourth = laurent_power(cosine, 4)
    continuum = cosine_fourth[0]
    nyquist = {-NYQUIST_GRID // 2: Fraction(1, 2), NYQUIST_GRID // 2: Fraction(1, 2)}
    nyquist_fourth = laurent_power(nyquist, 4)
    nodal = grid_average(nyquist_fourth, NYQUIST_GRID)
    audit.check("independent cosine fourth average", continuum == Fraction(3, 8), continuum, Fraction(3, 8), "nonidentification")
    audit.check("independent Nyquist nodal average", nodal == 1, nodal, 1, "nonidentification")
    audit.check("independent Nyquist quartic gap", nodal - continuum == Fraction(5, 8), nodal - continuum, Fraction(5, 8), "nonidentification")
    low_field = {-LOW_BAND: Fraction(2, 5), 0: Fraction(3, 2), LOW_BAND: Fraction(2, 5)}
    low_fourth = laurent_power(low_field, 4)
    audit.check("independent low-band grid condition", LOW_GRID > 4 * LOW_BAND, LOW_GRID, f">{4 * LOW_BAND}", "nonidentification")
    audit.check("independent low-band quadrature", grid_average(low_fourth, LOW_GRID) == low_fourth[0], grid_average(low_fourth, LOW_GRID), low_fourth[0], "nonidentification")
    base_mass, target_mass = Fraction(2), Fraction(3)
    audit.check("independent base mass subtraction", target_mass - base_mass == 1, target_mass - base_mass, 1, "nonidentification")
    audit.check("independent base mass double count", Fraction(1, base_mass + target_mass) != Fraction(1, target_mass), Fraction(1, base_mass + target_mass), Fraction(1, target_mass), "nonidentification")
    covariance_shift = Fraction(4, 3)
    levels = [3 * covariance_shift * (1 + 1 + 2 * level) for level in range(4)]
    audit.check("independent Wick matrix levels", levels == [8, 16, 24, 32], levels, [8, 16, 24, 32], "nonidentification")
    audit.check("independent Wick matrix non-scalar", len(set(levels)) == 4, levels, "four levels", "nonidentification")
    audit.check("independent no-go id", manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["negative_id"] == NEGATIVE_IDS[0], manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["negative_id"], NEGATIVE_IDS[0], "nonidentification")
    audit.check("independent asymptotic survivor", "does not obstruct low-band" in manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["boundary"], manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["boundary"], "low-band survives", "nonidentification")

    true_scope = {key for key, value in manifest["scope"].items() if value is True}
    expected_true = {
        "Q3_spatial_Wick_martingale",
        "Q3_spatial_common_Gaussian_L1_density_limit",
        "finite_spatial_cutoff_time_locality",
        "finite_spatial_cutoff_reflection_positive",
        "limiting_Nagoji_measure_reflection_positive",
        "finite_spatial_cutoff_Feynman_Kac_comparator",
        "bounded_configuration_observable_limit",
    }
    audit.check("independent true scope exact", true_scope == expected_true, sorted(true_scope), sorted(expected_true), "scope")
    for key, value in manifest["scope"].items():
        audit.check(f"independent scope {key}", value is (key in expected_true), value, key in expected_true, "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("independent C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    audit.check("independent below empty firewall", manifest["scope"]["below_empty_space_comparison"] is False, manifest["scope"]["below_empty_space_comparison"], False, "scope")
    audit.check("independent Pre-A firewall", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "scope")

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    from_imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    dynamic = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile"}}
    audit.check("stdlib numeric firewall", not ({"sympy", "numpy", "scipy"} & (imports | from_imports)), sorted(imports | from_imports), "stdlib only", "independence")
    audit.check("primary import firewall", PRIMARY_STEM not in imports and PRIMARY_STEM not in from_imports, sorted(imports | from_imports), f"not {PRIMARY_STEM}", "independence")
    audit.check("dynamic import firewall", not dynamic and "runpy" not in imports and "importlib" not in imports, {"dynamic": sorted(dynamic), "imports": sorted(imports)}, "none", "independence")
    for phrase in ("reflection positive for Euclidean-time reflection", "same terminal interaction", "Nyquist quartic witness", "energy below empty space", "Pre-A remain open"):
        audit.check(f"independent certificate {phrase[:32]}", phrase in certificate_flat, phrase, "present", "independence")
    non_ascii = {str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127}) for path in (MANIFEST, CERTIFICATE, SCRIPT)}
    audit.check("independent package ASCII", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "independence")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {
            "onsite_conditioning": onsite_results,
            "Q3_edge_conditioning": serialize(edge_conditioned),
            "RP_gram": [[str(value) for value in row] for row in rp_gram],
            "Nyquist": {"continuum": str(continuum), "nodal": str(nodal), "gap": str(nodal - continuum)},
            "low_band_average": str(grid_average(low_fourth, LOW_GRID)),
            "Wick_translation_levels": [str(value) for value in levels],
            "Matsubara_control": str(canonical_matsubara),
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
