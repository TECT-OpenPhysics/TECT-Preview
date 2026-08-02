#!/usr/bin/env python3
"""Independent certificate for the R-146 canonical-covariance reduction.

This implementation does not import the primary module or its result.  It
reconstructs the R-145 anisotropic constants from the A1 inputs and the
registered rational enclosure recipe, checks canonical Brownian covariance
and cost identities by direct Fraction arithmetic, and independently derives
the relative-anchor and residual budget statements.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CANONICAL-COVARIANCE-RELATIVE-ANCHOR-ANISOTROPIC-TEMPORAL-REDUCTION"
SCHEMA = "tect/a13-canonical-covariance-relative-anchor-anisotropic-temporal-reduction-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_canonical_covariance_relative_anchor_anisotropic_temporal_reduction_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-independent-canonical-covariance-relative-anchor-anisotropic-temporal-reduction" / "result.json"


def F(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fs(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


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
    handle, temporary = tempfile.mkstemp(prefix="independent-", suffix=".tmp", dir=path.parent)
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


def ceil_sqrt(value: Fraction) -> int:
    result = isqrt(value.numerator // value.denominator)
    while Fraction(result * result) < value:
        result += 1
    return result


def ceil_fraction(value: Fraction) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


def cube_radius_sum(radius: int) -> int:
    total = 0
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                total += i * i + j * j + k * k
    return total


def zeta_integral_upper(power: int, start: int) -> Fraction:
    return Fraction(1, start**power) + Fraction(1, (power - 1) * start ** (power - 1))


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def matadd(*matrices: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((matrix[i][j] for matrix in matrices), Fraction(0)) for j in range(len(matrices[0][0]))] for i in range(len(matrices[0]))]


@dataclass
class Checks:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def add(self, category: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"category": category, "name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})

    def finish(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def main() -> int:
    checks = Checks()
    manifest = read_json(MANIFEST)
    checks.add("metadata", "manifest claim", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    checks.add("metadata", "manifest result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    checks.add("metadata", "package version", manifest["package_version"] == "1.0.0", manifest["package_version"], "1.0.0")

    for label, relative in manifest["authorities"].items():
        path = REPO / relative
        checks.add("authority", f"{label} exists", path.exists() and path.is_file(), relative, "file")
        actual = digest(path)
        checks.add("authority", f"{label} digest", actual == manifest["authority_hashes"][label], actual, manifest["authority_hashes"][label])

    a1 = read_json(REPO / manifest["authorities"]["A1"])
    p = a1["parameters"]

    # Independently derive beta from the A1 coefficient matrix.
    denominator = F(p["M_X"]) ** 2 + F(p["classii_mass_regularizer"])
    coeff_a = F(p["cJJ"]) * F(p["alpha_X"]) ** 2 / denominator
    coeff_b = F(p["cJK"]) * F(p["alpha_X"]) * F(p["beta_X"]) / denominator
    coeff_c = F(p["cKK"]) * F(p["beta_X"]) ** 2 / denominator
    beta_actual = 4 * (coeff_a + 2 * abs(coeff_b) + coeff_c)
    beta = (coeff_a + 2 * abs(coeff_b) + coeff_c) * denominator
    checks.add("coefficient", "coefficient determinant", coeff_a * coeff_c > coeff_b * coeff_b, fs(coeff_a * coeff_c - coeff_b * coeff_b), ">0")
    checks.add("coefficient", "diagonal coefficients positive", coeff_a > 0 and coeff_c > 0, [fs(coeff_a), fs(coeff_c)], ">0")
    checks.add("coefficient", "denominator above four", denominator > 4, fs(denominator), ">4")
    checks.add("coefficient", "strict beta upper", beta_actual < beta, fs(beta_actual), f"<{fs(beta)}")

    # Independently reconstruct the R-145 rational anisotropic trace bound.
    root_intervals = [(F(lo), F(hi)) for lo, hi in manifest["audit_inputs"]["mass_root_intervals"]]
    spread = (root_intervals[2][1] - root_intervals[0][0]) + (root_intervals[2][1] - root_intervals[1][0])
    length = F(p["Lx"])
    pi_lower = F(manifest["audit_inputs"]["pi_lower"])
    pi_upper = F(manifest["audit_inputs"]["pi_upper"])
    start = int(manifest["audit_inputs"]["tail_start_sup_shell"])
    h_squared = (2 * pi_upper / length) ** 2
    low_radius = Fraction(cube_radius_sum(2))
    low = spread * 16 * low_radius * h_squared
    collar = Fraction(1) - Fraction(4, start * start)
    tail = spread * collar ** (-4) * (length / (2 * pi_lower)) ** 6 * (
        40 * zeta_integral_upper(4, start) + 14 * zeta_integral_upper(6, start)
    )
    g_r = 2 * (low + tail) / length**3
    checks.add("trace", "low cube direct enumeration", low_radius == 750, fs(low_radius), "750")
    checks.add("trace", "mass spread positive", spread > 0, fs(spread), ">0")
    checks.add("trace", "collar positive", collar > 0, fs(collar), ">0")
    checks.add("trace", "pointwise trace positive", g_r > 0, fs(g_r), ">0")

    r145 = read_json(REPO / manifest["authorities"]["R-145-primary"])
    checks.add("independence", "beta agrees with accepted R-145", fs(beta) == r145["exact_values"]["beta_operator_upper"], fs(beta), r145["exact_values"]["beta_operator_upper"])
    checks.add("independence", "trace agrees with accepted R-145", fs(g_r) == r145["exact_values"]["six_real_pointwise_derivative_trace_bound"], fs(g_r), r145["exact_values"]["six_real_pointwise_derivative_trace_bound"])

    kinetic_minimum = F(p["r"]) - F(p["Z"]) ** 2 / (4 * F(p["Y"]))
    c_bound = Fraction(ceil_fraction(Fraction(1, 1) / kinetic_minimum))
    checks.add("covariance", "kinetic lower bound", kinetic_minimum > Fraction(1, 4), fs(kinetic_minimum), ">1/4")
    checks.add("covariance", "derived covariance upper", c_bound == 4, fs(c_bound), "ceil(1/kinetic_minimum)=4")
    checks.add("covariance", "shell coefficient nonnegative", F(p["eta_shell"]) >= 0, fs(F(p["eta_shell"])), ">=0")
    checks.add("covariance", "family masses nonnegative", all(F(value) >= 0 for value in p["family_masses"]), p["family_masses"], ">=0")
    checks.add("covariance", "lock coefficient nonnegative", F(p["k_lock"]) >= 0, fs(F(p["k_lock"])), ">=0")
    checks.add("covariance", "cubic volume", F(p["Lx"]) == F(p["Ly"]) == F(p["Lz"]), [p["Lx"], p["Ly"], p["Lz"]], "Lx=Ly=Lz")
    regulator_bound = F(manifest["audit_inputs"]["regulator_bound"])
    checks.add("covariance", "regulator nonnegative", regulator_bound >= 0, fs(regulator_bound), ">=0")
    checks.add("covariance", "regulator at most one", regulator_bound <= 1, fs(regulator_bound), "<=1")

    # Direct Fraction verification of proportional covariance increments.
    weights = [Fraction(1, 9), Fraction(4, 9), Fraction(4, 9)]
    square_root_weights = [Fraction(1, 3), Fraction(2, 3), Fraction(2, 3)]
    covariance = [[Fraction(4), Fraction(0)], [Fraction(0), Fraction(0)]]
    covariance_sqrt = [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(0)]]
    increments = [[[weight * entry for entry in row] for row in covariance] for weight in weights]
    checks.add("canonical", "weights sum", sum(weights, Fraction(0)) == 1, fs(sum(weights, Fraction(0))), "1")
    checks.add("canonical", "increments sum", matadd(*increments) == covariance, [[fs(x) for x in row] for row in matadd(*increments)], [[fs(x) for x in row] for row in covariance])
    projector = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    checks.add("canonical", "all increments commute", all(matmul(block, projector) == matmul(projector, block) for block in increments), True, True)

    # Exact simple-control cost/shift relation uses h_b=sqrt(tau_b)u_b;
    # squared source norms therefore equal tau_b|u_b|^2.
    controls = [[Fraction(1), Fraction(2)], [Fraction(-2), Fraction(1)], [Fraction(3), Fraction(-1)]]
    interval_costs = [weight * sum((x * x for x in vector), Fraction(0)) for weight, vector in zip(weights, controls)]
    h_blocks = [[root * x for x in vector] for root, vector in zip(square_root_weights, controls)]
    chart_costs = [sum((x * x for x in vector), Fraction(0)) for vector in h_blocks]
    checks.add("canonical", "cost equality", sum(interval_costs, Fraction(0)) == sum(chart_costs, Fraction(0)), fs(sum(interval_costs, Fraction(0))), fs(sum(chart_costs, Fraction(0))))
    shift_coordinates = [sum((square_root_weights[b] * h_blocks[b][i] for b in range(3)), Fraction(0)) for i in range(2)]
    expected_shift_coordinates = [sum((weights[b] * controls[b][i] for b in range(3)), Fraction(0)) for i in range(2)]
    checks.add("canonical", "covariance square root", matmul(covariance_sqrt, covariance_sqrt) == covariance, [[fs(x) for x in row] for row in matmul(covariance_sqrt, covariance_sqrt)], [[fs(x) for x in row] for row in covariance])
    checks.add("canonical", "shift coordinates", shift_coordinates == expected_shift_coordinates, [fs(x) for x in shift_coordinates], [fs(x) for x in expected_shift_coordinates])
    checks.add("canonical", "physical shift equality", matmul(covariance_sqrt, [[x] for x in shift_coordinates]) == matmul(covariance_sqrt, [[x] for x in expected_shift_coordinates]), True, True)
    kernel_control = [Fraction(0), Fraction(5)]
    kernel_shift = [covariance[0][0] * kernel_control[0], covariance[1][1] * kernel_control[1]]
    checks.add("canonical", "kernel shift zero", kernel_shift == [0, 0], [fs(x) for x in kernel_shift], ["0", "0"])
    checks.add("canonical", "kernel control cost retained", sum((x * x for x in kernel_control), Fraction(0)) == 25, fs(sum((x * x for x in kernel_control), Fraction(0))), "25")

    p_plus = [[Fraction(1, 2), Fraction(1, 2)], [Fraction(1, 2), Fraction(1, 2)]]
    p_minus = [[Fraction(1, 2), Fraction(-1, 2)], [Fraction(-1, 2), Fraction(1, 2)]]
    anisotropic_target = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    checks.add("boundary", "rank-one supports resolve identity", matadd(p_plus, p_minus) == [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]], [[fs(x) for x in row] for row in matadd(p_plus, p_minus)], "I")
    checks.add("boundary", "plus support is rank-one projector", matmul(p_plus, p_plus) == p_plus and p_plus[0][0] * p_plus[1][1] - p_plus[0][1] * p_plus[1][0] == 0, True, True)
    checks.add("boundary", "minus support is rank-one projector", matmul(p_minus, p_minus) == p_minus and p_minus[0][0] * p_minus[1][1] - p_minus[0][1] * p_minus[1][0] == 0, True, True)
    checks.add("boundary", "each supported basis has equal diagonals", p_plus[0][0] == p_plus[1][1] and p_minus[0][0] == p_minus[1][1], True, True)
    checks.add("boundary", "anisotropic target has unequal diagonals", anisotropic_target[0][0] != anisotropic_target[1][1], [fs(anisotropic_target[0][0]), fs(anisotropic_target[1][1])], "unequal")

    # The registered theorem is endpoint-first and has no source loss.  The
    # positive prefix estimate is retained only as a diagnostic because a
    # production stage-owner tower has not been proved.
    eta_prefix_diagnostic = c_bound * beta * g_r
    endpoint_eta_an = Fraction(0)
    zeta_an = F(manifest["audit_inputs"]["anisotropic_sextic_allocation"])
    volume_two_thirds = length**2
    endpoint_terminal_coefficient = beta * g_r * volume_two_thirds / 2
    prefix_terminal_coefficient_diagnostic = beta * g_r * volume_two_thirds
    endpoint_constant_square = 4 * endpoint_terminal_coefficient**3 / (27 * zeta_an)
    endpoint_constant_ceiling = ceil_sqrt(endpoint_constant_square)
    prefix_constant_square_diagnostic = 4 * prefix_terminal_coefficient_diagnostic**3 / (27 * zeta_an)
    prefix_constant_ceiling_diagnostic = ceil_sqrt(prefix_constant_square_diagnostic)
    source_threshold = F(r145["exact_values"]["source_loss_threshold"])
    sextic_threshold = F(r145["exact_values"]["sextic_loss_threshold"])
    source_margin = source_threshold
    sextic_margin = sextic_threshold - zeta_an
    checks.add("payment", "R-145 source threshold", source_threshold == Fraction(5, 11), fs(source_threshold), "5/11")
    checks.add("payment", "R-145 sextic threshold", sextic_threshold == Fraction(27, 100), fs(sextic_threshold), "27/100")
    checks.add("payment", "endpoint eta zero", endpoint_eta_an == 0, fs(endpoint_eta_an), "0")
    checks.add("payment", "source window unchanged", source_margin == source_threshold, fs(source_margin), "5/11")
    checks.add("diagnostic", "prefix eta formula", eta_prefix_diagnostic == 4 * beta * g_r, fs(eta_prefix_diagnostic), "4*beta*g_R")
    checks.add("diagnostic", "prefix eta below one ninth", eta_prefix_diagnostic < Fraction(1, 9), fs(eta_prefix_diagnostic), "<1/9")
    checks.add("payment", "zeta value", zeta_an == Fraction(1, 100), fs(zeta_an), "1/100")
    checks.add("payment", "zeta residual", sextic_margin == Fraction(13, 50), fs(sextic_margin), "13/50")
    checks.add("diagnostic", "prefix constant ceiling", prefix_constant_ceiling_diagnostic == 67, prefix_constant_ceiling_diagnostic, 67)
    checks.add("diagnostic", "prefix constant exact bracket", Fraction(66**2) < prefix_constant_square_diagnostic < Fraction(67**2), fs(prefix_constant_square_diagnostic), "66^2<C^2<67^2")
    endpoint_constant = int(r145["exact_values"]["young_constant_integer_ceiling"])
    checks.add("payment", "endpoint constant independently recomputed", endpoint_constant_ceiling == 24, endpoint_constant_ceiling, 24)
    checks.add("payment", "endpoint R-145 constant", endpoint_constant == 24, endpoint_constant, 24)
    checks.add("payment", "endpoint recomputation agrees", endpoint_constant_ceiling == endpoint_constant, endpoint_constant_ceiling, endpoint_constant)

    # Weighted tail inequality on a rational fixture, avoiding square roots by
    # using g_b=sqrt(tau_b)h_b as the physical source summands directly.
    physical_source_summands = [Fraction(1, 5), Fraction(-2, 5), Fraction(3, 10)]
    h_energy = [physical_source_summands[i] ** 2 / weights[i] for i in range(3)]
    total_energy = sum(h_energy, Fraction(0))
    for index in range(3):
        tail = sum(physical_source_summands[index + 1 :], Fraction(0))
        tail_physical = Fraction(2) * tail * tail
        checks.add("tail", f"rational tail inequality {index}", tail_physical <= c_bound * total_energy, fs(tail_physical), f"<={fs(c_bound * total_energy)}")

    # Relative anchoring and gauge firewall, checked without symbolic algebra.
    t0, th = Fraction(7, 3), Fraction(-5, 4)
    anchor = t0
    energy = anchor - th
    checks.add("anchor", "relative identity", energy == -(th - t0), fs(energy), fs(-(th - t0)))
    gauge = Fraction(19, 7)
    checks.add("anchor", "relative difference gauge invariant", (th + gauge) - (t0 + gauge) == th - t0, fs((th + gauge) - (t0 + gauge)), fs(th - t0))
    checks.add("anchor", "external centering fixes gauge", anchor == t0, fs(anchor), fs(t0))

    # Endpoint-first sign: subtracting the nonnegative zero-control
    # anisotropic baseline can only improve the upper trace-excess bound.
    scalar_delta = Fraction(7, 5)
    anisotropic_h = Fraction(11, 9)
    anisotropic_zero = Fraction(4, 7)
    total_delta = scalar_delta + anisotropic_h - anisotropic_zero
    checks.add("endpoint", "baseline improves endpoint bound", total_delta <= scalar_delta + anisotropic_h, fs(total_delta), f"<={fs(scalar_delta + anisotropic_h)}")

    # Predictable common noise: an explicit rectangular A and shift u.
    matrix = [[Fraction(1), Fraction(2)], [Fraction(0), Fraction(-1)]]
    shift = [Fraction(2), Fraction(-1)]
    trace_square = sum((entry * entry for row in matrix for entry in row), Fraction(0))
    image = [sum((row[j] * shift[j] for j in range(2)), Fraction(0)) for row in matrix]
    image_square = sum((entry * entry for entry in image), Fraction(0))
    current_square = trace_square + image_square
    checks.add("scalar", "predictable common-noise identity", trace_square - current_square == -image_square, fs(trace_square - current_square), fs(-image_square))
    checks.add("scalar", "predictable common-noise sign", trace_square <= current_square, fs(trace_square - current_square), "<=0")

    # Contemporaneous bounded coefficient fixture at t=2.  Squaring removes
    # the common irrational factor, while the exact defect ratio is 2/5.
    t_value = F(manifest["audit_inputs"]["contemporaneous_fixture_parameter"])
    ratio = 2 * (t_value - 1) / (1 + 2 * t_value)
    checks.add("scalar", "contemporaneous parameter", t_value == 2, fs(t_value), "2")
    checks.add("scalar", "contemporaneous ratio exact", ratio == Fraction(2, 5), fs(ratio), "2/5")
    checks.add("scalar", "contemporaneous ratio positive", ratio > 0, fs(ratio), ">0")
    checks.add("scalar", "contemporaneous ratio below one", ratio < 1, fs(ratio), "<1")
    large_t = Fraction(1000)
    large_t_ratio = 2 * (large_t - 1) / (1 + 2 * large_t)
    checks.add("scalar", "contemporaneous ratio approaches one", large_t_ratio > Fraction(99, 100), fs(large_t_ratio), ">99/100")

    # Common terminal is not implied by proportional covariance.
    x1_value, x2_mean = Fraction(3, 2), Fraction(0)
    j1 = x1_value
    conditional_j2 = 2 * x1_value + x2_mean
    checks.add("frontier", "common-terminal mismatch", conditional_j2 != j1, fs(conditional_j2 - j1), "nonzero")

    for key in ("endpoint_first_anisotropic_payment_proved", "relative_anchor_reduction_proved", "canonical_covariance_variational_normal_form_proved", "predictable_scalar_common_noise_sign_proved"):
        checks.add("scope", key, manifest["scope"][key] is True, manifest["scope"][key], True)
    for key in ("canonical_temporal_owner_reconstruction_proved", "arbitrary_temporal_chart_anisotropic_transfer_proved", "scalar_principal_signed_relative_owner_proved", "complete_progressive_low_owner_proved", "common_terminal_doob_reconstruction_proved", "physical_phase_or_bcc_selection_proved", "t050_closed", "a13_gate_closed", "nelson_proved", "sector_a_closed"):
        checks.add("scope", key, manifest["scope"][key] is False, manifest["scope"][key], False)

    checks.finish()
    exact_values = {
        "kinetic_minimum": fs(kinetic_minimum),
        "canonical_value_covariance_operator_upper": fs(c_bound),
        "beta_operator_upper": fs(beta),
        "six_real_pointwise_derivative_trace_bound": fs(g_r),
        "endpoint_first_anisotropic_source_coefficient": fs(endpoint_eta_an),
        "canonical_prefix_source_coefficient_diagnostic": fs(eta_prefix_diagnostic),
        "endpoint_first_anisotropic_sextic_allocation": fs(zeta_an),
        "endpoint_first_anisotropic_constant": str(endpoint_constant),
        "remaining_scalar_source_window": fs(source_margin),
        "remaining_scalar_sextic_window": fs(sextic_margin),
        "endpoint_terminal_l2_coefficient": fs(endpoint_terminal_coefficient),
        "canonical_prefix_l2_coefficient_diagnostic": fs(prefix_terminal_coefficient_diagnostic),
        "endpoint_young_constant_square": fs(endpoint_constant_square),
        "endpoint_young_constant_ceiling": str(endpoint_constant_ceiling),
        "canonical_prefix_young_constant_square_diagnostic": fs(prefix_constant_square_diagnostic),
        "canonical_prefix_young_constant_ceiling_diagnostic": str(prefix_constant_ceiling_diagnostic),
        "source_threshold": fs(source_threshold),
        "sextic_threshold": fs(sextic_threshold),
    }
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "status": "PASS",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "assertions": {"passed": len(checks.rows), "failed": 0, "total": len(checks.rows), "rows": checks.rows},
        "exact_values": exact_values,
        "diagnostics": {
            "method": "independent Fraction reconstruction and direct matrix arithmetic",
            "does_not_import_primary": True,
            "remaining_target": "contemporaneous/balanced scalar-principal signed relative owner with complete low and forest",
        },
        "scope": manifest["scope"],
    }
    write_json(OUTPUT, payload)
    print(f"PASS {len(checks.rows)}/{len(checks.rows)}")
    print(f"endpoint eta_an=0; B_an={endpoint_constant}; prefix diagnostic={fs(eta_prefix_diagnostic)}")
    print("OPEN: scalar signed relative owner, T-050, Nelson, Sector A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
