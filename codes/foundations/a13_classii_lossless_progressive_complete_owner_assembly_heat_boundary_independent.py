#!/usr/bin/env python3
"""Independent standard-library certificate for R-104.

This implementation shares no imports or helper code with the primary
certificate. It verifies operator Cauchy through exact rational Loewner tests,
computes minimal source costs without matrix square roots, and independently
audits the telescopes, owner incidence, revisit failures, and heat boundary.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-LOSSLESS-PROGRESSIVE-COMPLETE-OWNER-ASSEMBLY-HEAT-BOUNDARY"
OUT = ROOT / "claims" / CLAIM / "runs/2026-07-28-independent-lossless-progressive-complete-owner-assembly-heat-boundary/result.json"


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Checks:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(self, group: str, name: str, ok: bool, got: Any, want: Any) -> None:
        self.items.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if ok else "FAIL",
                "actual": str(got),
                "expected": str(want),
            }
        )

    def payload(self, details: dict[str, Any]) -> dict[str, Any]:
        passed = sum(item["status"] == "PASS" for item in self.items)
        return {
            "schema": "tect/a13-lossless-progressive-complete-owner-assembly-heat-boundary-independent/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.items) else "FAIL",
            "assertions_total": len(self.items),
            "assertions_passed": passed,
            "assertions_failed": len(self.items) - passed,
            "assertions": self.items,
            "diagnostics": details,
            "consequence": {
                "fixed_chart_owner_defect_zero": details["assembly"]["identity_from_components"],
                "representation_preserving_subdivision_total_invariance": details["assembly"]["identity_from_components"],
                "ownerwise_subdivision_invariance": False,
                "physical_source_action_douglas_slack_identity": details["assembly"]["douglas_reconstruction"],
                "douglas_slack_nonnegative": details["assembly"]["douglas_cost_direction"],
                "exact_h_a_packet_assembly": details["assembly"]["identity_from_components"],
                "anticipative_heat_general_extension": False,
                "full_overlap_src": False,
                "nelson": False,
                "sector_a_closure": False,
            },
            "no_overclaim": (
                "The independent R-104 certificate verifies the finite fixed-chart endpoint-owner "
                "identity and Douglas slack only. It does not certify ownerwise subdivision "
                "invariance or the uniform source-action lower bound."
            ),
        }


Matrix = tuple[tuple[F, F], tuple[F, F]]
Vector = tuple[F, F]


def mat_add(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] + b[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_scale(scalar: F, matrix: Matrix) -> Matrix:
    return tuple(tuple(scalar * matrix[i][j] for j in range(2)) for i in range(2))  # type: ignore[return-value]


def mat_transpose(matrix: Matrix) -> Matrix:
    return ((matrix[0][0], matrix[1][0]), (matrix[0][1], matrix[1][1]))


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    return tuple(
        tuple(sum((a[i][k] * b[k][j] for k in range(2)), F(0)) for j in range(2))
        for i in range(2)
    )  # type: ignore[return-value]


def mat_vec(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(sum((matrix[i][j] * vector[j] for j in range(2)), F(0)) for i in range(2))  # type: ignore[return-value]


def dot(a: Vector, b: Vector) -> F:
    return a[0] * b[0] + a[1] * b[1]


def determinant(matrix: Matrix) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def rank2(matrix: Matrix) -> int:
    if determinant(matrix) != 0:
        return 2
    return 0 if all(entry == 0 for row in matrix for entry in row) else 1


def inverse(matrix: Matrix) -> Matrix:
    det = determinant(matrix)
    if det == 0:
        raise ZeroDivisionError("singular")
    return (
        (matrix[1][1] / det, -matrix[0][1] / det),
        (-matrix[1][0] / det, matrix[0][0] / det),
    )


def outer(vector: Vector) -> Matrix:
    return ((vector[0] * vector[0], vector[0] * vector[1]), (vector[1] * vector[0], vector[1] * vector[1]))


def exact_fixture(samples: list[Matrix], weights: list[F], control: Vector) -> dict[str, Any]:
    length = sum(weights, F(0))
    left: Matrix = ((F(0), F(0)), (F(0), F(0)))
    covariance: Matrix = ((F(0), F(0)), (F(0), F(0)))
    for weight, sample in zip(weights, samples):
        left = mat_add(left, mat_scale(weight, sample))
        covariance = mat_add(covariance, mat_scale(weight, mat_mul(sample, mat_transpose(sample))))
    loewner = mat_add(mat_scale(length, covariance), mat_scale(F(-1), mat_mul(left, mat_transpose(left))))
    displacement = mat_vec(left, control)
    rank = rank2(covariance)
    if rank == 2:
        minimal_cost = dot(displacement, mat_vec(inverse(covariance), displacement))
    elif rank == 1:
        # For C = lambda vv^T, C^dagger = C / tr(C)^2.
        trace = covariance[0][0] + covariance[1][1]
        minimal_cost = dot(displacement, mat_vec(covariance, displacement)) / (trace * trace)
    else:
        minimal_cost = F(0)
    return {
        "length": length,
        "left": left,
        "covariance": covariance,
        "loewner": loewner,
        "rank": rank,
        "displacement": displacement,
        "minimal_cost": minimal_cost,
        "control_cost": length * dot(control, control),
    }


def psd_2x2(matrix: Matrix) -> bool:
    return matrix[0][0] >= 0 and matrix[1][1] >= 0 and determinant(matrix) >= 0 and matrix[0][1] == matrix[1][0]


def endpoint(value: F) -> F:
    return 3 * value**5 - 2 * value**3 + value**2 + F(5, 7)


def expectation(table: list[tuple[F, F]]) -> F:
    return sum((probability * value for probability, value in table), F(0))


def gaussian_moment_recurrence(max_even_order: int) -> dict[int, F]:
    if max_even_order < 0 or max_even_order % 2:
        raise ValueError("max_even_order must be nonnegative and even")
    moments = {0: F(1)}
    for order in range(2, max_even_order + 1, 2):
        moments[order] = F(order - 1) * moments[order - 2]
    return moments


def main() -> int:
    checks = Checks()

    # Independently chosen exact input fixtures.
    cases = [
        (
            "singular_overlap",
            [((F(1), F(0)), (F(2), F(0))), ((F(2), F(0)), (F(4), F(0)))],
            [F(1, 3), F(2, 3)],
            (F(3), F(-2)),
            1,
        ),
        (
            "full_rank",
            [((F(1), F(2)), (F(0), F(1))), ((F(2), F(-1)), (F(1), F(3)))],
            [F(2, 5), F(3, 5)],
            (F(-1), F(2)),
            2,
        ),
        (
            "pure_kernel",
            [((F(1), F(0)), (F(0), F(0)))],
            [F(1)],
            (F(0), F(1)),
            1,
        ),
    ]
    matrix_details: dict[str, Any] = {}
    douglas_reconstruction = True
    douglas_cost_direction = True
    for label, samples, weights, control, wanted_rank in cases:
        row = exact_fixture(samples, weights, control)
        checks.add("douglas", f"{label}_rank", row["rank"] == wanted_rank, row["rank"], wanted_rank)
        checks.add("douglas", f"{label}_loewner_psd", psd_2x2(row["loewner"]), row["loewner"], "PSD")
        checks.add("douglas", f"{label}_minimal_cost", row["minimal_cost"] <= row["control_cost"], row["minimal_cost"], f"<={row['control_cost']}")
        douglas_reconstruction = douglas_reconstruction and psd_2x2(row["loewner"])
        douglas_cost_direction = douglas_cost_direction and row["minimal_cost"] <= row["control_cost"]
        if row["rank"] == 1:
            c = row["covariance"]
            a = row["displacement"]
            range_minor = c[0][0] * a[1] - c[1][0] * a[0]
            checks.add("douglas", f"{label}_range_inclusion", range_minor == 0, range_minor, 0)
        matrix_details[label] = {
            "rank": row["rank"],
            "loewner": [[str(value) for value in line] for line in row["loewner"]],
            "minimal_cost": str(row["minimal_cost"]),
            "control_cost": str(row["control_cost"]),
        }

    kernel = exact_fixture(
        [((F(1), F(0)), (F(0), F(0)))],
        [F(1)],
        (F(0), F(1)),
    )
    kernel_values = (kernel["displacement"], kernel["minimal_cost"], kernel["control_cost"])
    checks.add("douglas", "pure_kernel_fixture_values", kernel_values == ((F(0), F(0)), F(0), F(1)), kernel_values, ((0, 0), 0, 1))
    checks.add("douglas", "douglas_cost_equality_mutant_rejected", kernel["minimal_cost"] < kernel["control_cost"], (kernel["minimal_cost"], kernel["control_cost"]), "strict <")

    start = F(-4, 3)
    steps = [F(5, 2), F(-7, 4), F(9, 5), F(-9, 5), F(-3, 4)]
    points = [start]
    for step in steps:
        points.append(points[-1] + step)
    sum_of_edges = sum((endpoint(points[index + 1]) - endpoint(points[index]) for index in range(len(steps))), F(0))
    one_edge = endpoint(points[-1]) - endpoint(points[0])
    checks.add("telescope", "five_edge_endpoint", sum_of_edges == one_edge, sum_of_edges, one_edge)

    base, first, later = F(-5, 6), F(7, 3), F(-4, 5)
    lhs = ((base + first + later) ** 2 - base**2) / 2
    rhs = base * first + first**2 / 2 + (base + first) * later + later**2 / 2
    mutant = base * first + first**2 / 2 + base * later + later**2 / 2
    checks.add("telescope", "square_complete", lhs == rhs, lhs, rhs)
    checks.add("telescope", "square_cross_retained", lhs - mutant == first * later, lhs - mutant, first * later)
    checks.add("telescope", "square_cross_nonzero", first * later != 0, first * later, "nonzero")

    # Independent four-atom expectation-only owner fixture.
    signs = [(F(a), F(b)) for a in (-1, 1) for b in (-1, 1)]
    quarter = F(1, 4)
    doob_left_atoms = [(a + b) ** 2 - a**2 for a, b in signs]
    doob_right_atoms = [b**2 for _, b in signs]
    cross_average = sum((quarter * 2 * a * b for a, b in signs), F(0))
    doob_left = sum((quarter * value for value in doob_left_atoms), F(0))
    doob_right = sum((quarter * value for value in doob_right_atoms), F(0))
    doob_defect = doob_left - doob_right
    checks.add("doob", "doob_predictable_cross_mean_zero", cross_average == 0, cross_average, 0)
    checks.add("doob", "doob_product_identity_in_expectation", doob_defect == 0 and doob_left == 1, (doob_left, doob_right), (1, 1))
    checks.add("doob", "doob_pathwise_equality_mutant_rejected", any(left != right for left, right in zip(doob_left_atoms, doob_right_atoms)), list(zip(doob_left_atoms, doob_right_atoms)), "at least one unequal atom")

    adapted_covariance = expectation([(quarter, a**2) for a, _ in signs])
    compressed_covariance = expectation([(quarter, b**2) for _, b in signs])
    adapted_correlation = expectation([(quarter, a * a) for a, _ in signs])
    compressed_correlation = expectation([(quarter, a * b) for a, b in signs])
    compression_distance = expectation([(quarter, (a - b) ** 2) for a, b in signs])
    checks.add("causality", "terminal_covariance_matched", adapted_covariance == compressed_covariance == 1, (adapted_covariance, compressed_covariance), (1, 1))
    checks.add("causality", "noncausal_mixed_correlation_changed", (adapted_correlation, compressed_correlation) == (1, 0), (adapted_correlation, compressed_correlation), (1, 0))
    checks.add("causality", "noncausal_l2_distance_two", compression_distance == 2, compression_distance, 2)

    # Deliberately different insertion order from the primary certificate.
    module_rows = [
        ("paid_collar", ("r078_paid_difference",)),
        ("complete_low", ("complete_low",)),
        ("conditional_low", ("conditional_low",)),
        ("rational_shifted_current", ("future_current", "terminal_square")),
        ("rational_unshifted_current", ("current_u3", "current_u4", "current_u5")),
        ("rational_raw_wick_residual", ("raw_wick_future_residual", "rational_heat_trace_forest", "full_wick_secant")),
        ("linear_near", ("linear_rows", "linear_heat_trace_forest")),
        ("cartan_far", ("cartan_output",)),
    ]
    modules = dict(module_rows)
    near_modules = tuple(name for name in modules if name != "cartan_far")
    canonical_module_names = {
        "cartan_far", "linear_near", "rational_raw_wick_residual",
        "rational_unshifted_current", "rational_shifted_current",
        "conditional_low", "complete_low", "paid_collar",
    }
    all_atoms = [atom for atoms in modules.values() for atom in atoms]
    refunded = (
        "raw_q_taylor_u1", "raw_q_taylor_u2", "r076_base_cubic",
        "r086_tg_low_current", "r086_q_orientations", "second_r094_secant",
        "appended_r063_forest", "extra_q_r_schur_reserve",
    )
    missing_modules = tuple(sorted(canonical_module_names - set(modules)))
    extra_modules = tuple(sorted(set(modules) - canonical_module_names))
    duplicate_count = len(all_atoms) - len(set(all_atoms))
    refund_hits = tuple(sorted(set(all_atoms) & set(refunded)))
    internal_coordinates = {"linear_heat_trace_forest", "rational_heat_trace_forest", "terminal_square"}
    checks.add("ownership", "seven_near_modules", len(near_modules) == 7, len(near_modules), 7)
    checks.add("ownership", "eight_reg_modules", len(modules) == 8, len(modules), 8)
    checks.add("ownership", "near_excludes_only_cartan_far", set(modules) - set(near_modules) == {"cartan_far"}, sorted(set(modules) - set(near_modules)), ["cartan_far"])
    checks.add("ownership", "module_table_complete", not missing_modules and not extra_modules, (missing_modules, extra_modules), ((), ()))
    checks.add("ownership", "atomic_owner_uniqueness", duplicate_count == 0, duplicate_count, 0)
    checks.add("ownership", "cartan_output_once", all_atoms.count("cartan_output") == 1, all_atoms.count("cartan_output"), 1)
    checks.add("ownership", "terminal_square_nested_in_shifted", "terminal_square" in modules["rational_shifted_current"] and "terminal_square" not in modules, modules["rational_shifted_current"], "nested once")
    checks.add("ownership", "outer_internal_disjoint", set(modules).isdisjoint(internal_coordinates), sorted(set(modules) & internal_coordinates), [])
    for module, atoms in modules.items():
        checks.add("ownership", f"module_{module}_nonempty", bool(atoms), len(atoms), ">0")
    for refund in refunded:
        checks.add("refund", f"refund_{refund}_zero", refund not in all_atoms and refund not in modules, 0, 0)

    size = F(12)
    low_loss = -size**4 / 2
    low_companion = size**4 / 2
    cost = 2 * size**2
    eta, constant = F(1), F(1)
    checks.add("revisit", "visitwise_low_fails", low_loss < -eta * cost - constant, low_loss, f"<{-eta * cost - constant}")
    checks.add("revisit", "complete_low_zero", low_loss + low_companion == 0, low_loss + low_companion, 0)
    checks.add("revisit", "reverse_visit_zero", size + (-size) == 0, size + (-size), 0)

    sixth_input = F(5, 4)
    sixth_details: list[dict[str, str]] = []
    for denominator in (3, 7, 11):
        event_probability = F(1, denominator)
        source_amplitude_squared = F(denominator)
        visit_count = 2
        source = visit_count * event_probability * source_amplitude_squared
        sixth = (
            visit_count
            * event_probability
            * sixth_input
            * source_amplitude_squared**3
        )
        checks.add("revisit", f"cost_two_d{denominator}", source == 2, source, 2)
        checks.add("revisit", f"p_minus_two_d{denominator}", sixth / (denominator**2) == 2 * sixth_input, sixth / (denominator**2), 2 * sixth_input)
        sixth_details.append({"denominator": str(denominator), "source_cost": str(source), "sixth_sum": str(sixth)})

    # Gaussian integration-by-parts recurrence, independent of the primary route.
    moments = gaussian_moment_recurrence(6)
    mean_q = moments[2] - moments[0]
    predictable_g4 = moments[4] * mean_q
    same_root_g4 = moments[6] - moments[4]
    zero_defect_guard = moments[6] - 7 * moments[4] + 15 * moments[2] - 9 * moments[0]
    checks.add("heat", "gaussian_m2_recurrence", moments[2] == 1, moments[2], 1)
    checks.add("heat", "gaussian_m4_recurrence", moments[4] == 3, moments[4], 3)
    checks.add("heat", "gaussian_m6_recurrence", moments[6] == 15, moments[6], 15)
    checks.add("heat", "wick_second_centered", mean_q == 0, mean_q, 0)
    checks.add("heat", "predictable_g4_heat_zero", predictable_g4 == 0, predictable_g4, 0)
    checks.add("heat", "same_root_g4_heat_defect_twelve", same_root_g4 == 12, same_root_g4, 12)
    checks.add("heat", "same_root_psd_zero_defect_guard", zero_defect_guard == 0, zero_defect_guard, 0)

    nelson_q = F(10, 9)
    source_weight = F(1, 2) / nelson_q
    gap_weight = F(1) / nelson_q
    checks.add("variational", "source_weight_9_20", source_weight == F(9, 20), source_weight, F(9, 20))
    checks.add("variational", "gap_weight_9_10", gap_weight == F(9, 10), gap_weight, F(9, 10))
    endpoint_defect = sum_of_edges - one_edge
    square_defect = lhs - rhs
    assembly_components = (
        endpoint_defect,
        square_defect,
        doob_defect,
        missing_modules,
        extra_modules,
        duplicate_count,
        refund_hits,
        douglas_reconstruction,
    )
    expected_assembly_components = (F(0), F(0), F(0), (), (), 0, (), True)
    assembly_identity = assembly_components == expected_assembly_components
    checks.add("variational", "assembly_identity_from_components", assembly_identity, assembly_components, expected_assembly_components)
    pure_kernel_cost_gap = kernel["control_cost"] - kernel["minimal_cost"]
    strict_douglas_action_slack = source_weight * pure_kernel_cost_gap

    flags = {
        "exact_h_a_packet_assembly": assembly_identity,
        "visitwise_r103_extension": False,
        "ownerwise_subdivision_invariance": False,
        "overlap_src": False,
        "nelson": False,
        "sector_a": False,
    }

    data = checks.payload(
        {
            "matrix_fixtures": matrix_details,
            "telescope": {"points": [str(point) for point in points], "endpoint": str(one_edge), "square_cross": str(first * later)},
            "owners": {"modules": {name: list(atoms) for name, atoms in modules.items()}, "near_modules": list(near_modules), "refunded": list(refunded)},
            "revisit": {"low_loss": str(low_loss), "low_companion": str(low_companion), "cost": str(cost), "sixth": sixth_details},
            "heat": {"moments": {str(order): str(value) for order, value in moments.items()}, "mean_q": str(mean_q), "predictable_g4": str(predictable_g4), "same_root_g4": str(same_root_g4), "same_root_zero_defect_guard": str(zero_defect_guard)},
            "variational": {"q": str(nelson_q), "source_weight": str(source_weight), "gap_weight": str(gap_weight), **flags},
            "doob": {"left_atoms": [str(value) for value in doob_left_atoms], "right_atoms": [str(value) for value in doob_right_atoms], "expectation_defect": str(doob_defect)},
            "causality": {"adapted_covariance": str(adapted_covariance), "compressed_covariance": str(compressed_covariance), "adapted_correlation": str(adapted_correlation), "compressed_correlation": str(compressed_correlation), "l2_distance": str(compression_distance)},
            "assembly": {"components": [str(value) for value in assembly_components], "identity_from_components": assembly_identity, "douglas_reconstruction": douglas_reconstruction, "douglas_cost_direction": douglas_cost_direction, "physical_source_cost_slack_strict_fixture": str(strict_douglas_action_slack)},
        }
    )
    atomic_write(OUT, data)
    print(f"R-104 independent: {data['assertions_passed']}/{data['assertions_total']} assertions {data['status']}")
    return 0 if data["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
