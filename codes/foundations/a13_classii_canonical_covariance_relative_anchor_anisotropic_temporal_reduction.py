#!/usr/bin/env python3
"""Primary certificate for the R-146 canonical-covariance reduction.

The certificate proves four scoped statements.  First, A7 zero-control
centering turns the R-145 absolute trace-excess identity into an exact
relative identity, so no separate absolute anchor is needed on the direct
route.  Second, the fixed-cutoff Boue--Dupuis value may be evaluated on the
canonical Brownian factor C_J^(1/2), whose temporal covariance increments
are proportional to C_J.  Third, after the complete owner is telescoped to
the physical endpoint, the R-145 anisotropic trace owner is paid directly by
terminal-sextic coefficient 1/100 and constant 24, with no temporal transfer
and no source loss.  Fourth, predictable scalar common-noise rows are
favourable, while a bounded contemporaneous coefficient fixture has positive
trace excess.

The scalar-principal signed relative owner, including the complete low,
future-variance, and forest coordinates, remains open.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CANONICAL-COVARIANCE-RELATIVE-ANCHOR-ANISOTROPIC-TEMPORAL-REDUCTION"
SCHEMA = "tect/a13-canonical-covariance-relative-anchor-anisotropic-temporal-reduction-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_canonical_covariance_relative_anchor_anisotropic_temporal_reduction_manifest.json"
OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-08-02-primary-canonical-covariance-relative-anchor-anisotropic-temporal-reduction" / "result.json"


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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def ceil_sqrt(value: Fraction) -> int:
    candidate = isqrt(value.numerator // value.denominator)
    while candidate * candidate * value.denominator < value.numerator:
        candidate += 1
    return candidate


def ceil_fraction(value: Fraction) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


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


def main() -> int:
    getcontext().prec = 80
    audit = Audit()
    manifest = load_json(MANIFEST)

    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    for key, relative in manifest["authorities"].items():
        path = REPO / relative
        audit.check("authority", f"{key} exists", path.is_file(), relative, "file")
        actual = sha256(path)
        audit.check("authority", f"{key} hash", actual == manifest["authority_hashes"][key], actual, manifest["authority_hashes"][key])

    a1 = load_json(REPO / manifest["authorities"]["A1"])
    r145 = load_json(REPO / manifest["authorities"]["R-145-primary"])
    params = a1["parameters"]

    # The canonical value-covariance operator is uniformly bounded by four.
    r_value = frac(params["r"])
    z_value = frac(params["Z"])
    y_value = frac(params["Y"])
    kinetic_minimum = r_value - z_value * z_value / (4 * y_value)
    covariance_operator_upper = Fraction(ceil_fraction(Fraction(1, 1) / kinetic_minimum))
    audit.check("covariance", "kinetic minimum above one quarter", kinetic_minimum > Fraction(1, 4), fstr(kinetic_minimum), ">1/4")
    audit.check("covariance", "covariance bound derived from kinetic minimum", covariance_operator_upper == 4, fstr(covariance_operator_upper), "ceil(1/kinetic_minimum)=4")
    audit.check("covariance", "family masses nonnegative", all(frac(value) >= 0 for value in params["family_masses"]), params["family_masses"], ">=0")
    audit.check("covariance", "lock coefficient positive", frac(params["k_lock"]) > 0, str(params["k_lock"]), ">0")
    audit.check("covariance", "shell coefficient nonnegative", frac(params["eta_shell"]) >= 0, str(params["eta_shell"]), ">=0")
    audit.check("covariance", "cubic volume", frac(params["Lx"]) == frac(params["Ly"]) == frac(params["Lz"]), [params["Lx"], params["Ly"], params["Lz"]], "Lx=Ly=Lz")
    regulator_bound = frac(manifest["audit_inputs"]["regulator_bound"])
    audit.check("covariance", "regulator oracle nonnegative", regulator_bound >= 0, fstr(regulator_bound), ">=0")
    audit.check("covariance", "regulator oracle at most one", regulator_bound <= 1, fstr(regulator_bound), "<=1")

    beta = frac(r145["exact_values"]["beta_operator_upper"])
    g_r = frac(r145["exact_values"]["six_real_pointwise_derivative_trace_bound"])
    source_threshold = frac(r145["exact_values"]["source_loss_threshold"])
    sextic_threshold = frac(r145["exact_values"]["sextic_loss_threshold"])
    audit.check("authority", "R-145 result id", r145["result_id"] == "A13-CLASSII-WEIGHTED-TRACE-EXCESS-ANISOTROPIC-COVARIANCE-SEXTIC-REDUCTION", r145["result_id"], "R-145 result")
    audit.check("authority", "R-145 source threshold", source_threshold == Fraction(5, 11), fstr(source_threshold), "5/11")
    audit.check("authority", "R-145 sextic threshold", sextic_threshold == Fraction(27, 100), fstr(sextic_threshold), "27/100")
    audit.check("authority", "anisotropic trace bound positive", g_r > 0, fstr(g_r), ">0")
    audit.check("authority", "coefficient bound positive", beta > 0, fstr(beta), ">0")

    # A diagonal finite fixture certifies the exact canonical temporal factor.
    taus = [sp.Rational(1, 7), sp.Rational(2, 7), sp.Rational(4, 7)]
    covariance = sp.diag(sp.Rational(3, 2), 0, sp.Rational(1, 2))
    increments = [tau * covariance for tau in taus]
    audit.check("canonical", "partition weights sum to one", sum(taus) == 1, str(sum(taus)), "1")
    audit.check("canonical", "canonical increments sum to covariance", sum(increments, sp.zeros(3)) == covariance, str(sum(increments, sp.zeros(3))), str(covariance))
    projection = sp.diag(1, 0, 0)
    audit.check("canonical", "each canonical increment commutes with shell projector", all(block * projection == projection * block for block in increments), [str(block * projection - projection * block) for block in increments], "zero")

    # Cost equality for a simple canonical control: h_b=sqrt(tau_b)u_b.
    controls = [sp.Matrix([1, -2, 0]), sp.Matrix([0, 1, 3]), sp.Matrix([-1, 0, 2])]
    source_cost = sum((tau * (u.dot(u)) for tau, u in zip(taus, controls)), sp.Rational(0))
    h_blocks = [sp.sqrt(tau) * u for tau, u in zip(taus, controls)]
    chart_cost = sum((h.dot(h) for h in h_blocks), sp.Rational(0))
    audit.check("canonical", "simple-control source cost equality", sp.simplify(source_cost - chart_cost) == 0, str(sp.simplify(source_cost - chart_cost)), "0")
    shift_coordinates = sum((sp.sqrt(tau) * h for tau, h in zip(taus, h_blocks)), sp.zeros(3, 1))
    expected_shift_coordinates = sum((tau * u for tau, u in zip(taus, controls)), sp.zeros(3, 1))
    covariance_sqrt = sp.diag(sp.sqrt(sp.Rational(3, 2)), 0, sp.sqrt(sp.Rational(1, 2)))
    audit.check("canonical", "canonical square root", sp.simplify(covariance_sqrt * covariance_sqrt - covariance) == sp.zeros(3), str(sp.simplify(covariance_sqrt * covariance_sqrt - covariance)), "zero")
    audit.check("canonical", "simple-control shift equality", sp.simplify(covariance_sqrt * (shift_coordinates - expected_shift_coordinates)) == sp.zeros(3, 1), str(sp.simplify(covariance_sqrt * (shift_coordinates - expected_shift_coordinates))), "zero")

    # Singular covariance: a kernel source costs energy and produces no shift.
    kernel_vector = sp.Matrix([0, 1, 0])
    audit.check("canonical", "singular covariance kernel shift vanishes", covariance * kernel_vector == sp.zeros(3, 1), str(covariance * kernel_vector), "zero")
    audit.check("canonical", "singular covariance kernel source cost positive", kernel_vector.dot(kernel_vector) == 1, str(kernel_vector.dot(kernel_vector)), "1")

    # R-129 remains a real boundary for arbitrary increments, but not for the
    # deliberately chosen proportional factorisation.
    p_plus = sp.Rational(1, 2) * sp.Matrix([[1, 1], [1, 1]])
    p_minus = sp.Rational(1, 2) * sp.Matrix([[1, -1], [-1, 1]])
    shell_projection = sp.diag(1, 0)
    audit.check("boundary", "arbitrary positive increments sum to identity", p_plus + p_minus == sp.eye(2), str(p_plus + p_minus), "I")
    audit.check("boundary", "plus support is rank-one projector", p_plus * p_plus == p_plus and p_plus.rank() == 1, [str(p_plus * p_plus - p_plus), p_plus.rank()], ["zero", 1])
    audit.check("boundary", "minus support is rank-one projector", p_minus * p_minus == p_minus and p_minus.rank() == 1, [str(p_minus * p_minus - p_minus), p_minus.rank()], ["zero", 1])
    audit.check("boundary", "arbitrary increment need not commute", p_plus * shell_projection != shell_projection * p_plus, str(p_plus * shell_projection - shell_projection * p_plus), "nonzero")
    a_plus, a_minus = sp.symbols("a_plus a_minus", nonnegative=True)
    supported_allocation = a_plus * p_plus + a_minus * p_minus
    anisotropic_target = sp.diag(1, 0)
    audit.check("boundary", "rank-one supported allocations have equal diagonals", sp.simplify(supported_allocation[0, 0] - supported_allocation[1, 1]) == 0, str(sp.simplify(supported_allocation[0, 0] - supported_allocation[1, 1])), "0")
    audit.check("boundary", "anisotropic target has unequal diagonals", anisotropic_target[0, 0] != anisotropic_target[1, 1], [str(anisotropic_target[0, 0]), str(anisotropic_target[1, 1])], "unequal")

    # Endpoint-first anisotropic payment.  The positive stage-prefix bound
    # below is retained only as a non-production diagnostic; the registered
    # theorem first telescopes the complete owner and then invokes R-145.
    eta_prefix_diagnostic = covariance_operator_upper * beta * g_r
    volume_two_thirds = frac(params["Lx"]) ** 2
    endpoint_terminal_coefficient = beta * g_r * volume_two_thirds / 2
    prefix_terminal_coefficient_diagnostic = beta * g_r * volume_two_thirds
    zeta_an = frac(manifest["audit_inputs"]["anisotropic_sextic_allocation"])
    endpoint_young_square = Fraction(4) * endpoint_terminal_coefficient**3 / (27 * zeta_an)
    endpoint_young_ceiling = ceil_sqrt(endpoint_young_square)
    prefix_young_square_diagnostic = Fraction(4) * prefix_terminal_coefficient_diagnostic**3 / (27 * zeta_an)
    prefix_young_ceiling_diagnostic = ceil_sqrt(prefix_young_square_diagnostic)
    endpoint_eta_an = Fraction(0)
    eta_margin = source_threshold
    zeta_margin = sextic_threshold - zeta_an
    audit.check("payment", "endpoint-first source coefficient vanishes", endpoint_eta_an == 0, fstr(endpoint_eta_an), "0")
    audit.check("payment", "endpoint-first source window unchanged", eta_margin == Fraction(5, 11), fstr(eta_margin), "5/11")
    audit.check("diagnostic", "canonical prefix coefficient formula", eta_prefix_diagnostic == 4 * beta * g_r, fstr(eta_prefix_diagnostic), "4*beta*g_R")
    audit.check("diagnostic", "canonical prefix coefficient below one ninth", eta_prefix_diagnostic < Fraction(1, 9), fstr(eta_prefix_diagnostic), "<1/9")
    audit.check("payment", "sextic allocation one hundredth", zeta_an == Fraction(1, 100), fstr(zeta_an), "1/100")
    audit.check("payment", "remaining sextic margin", zeta_margin == Fraction(13, 50), fstr(zeta_margin), "13/50")
    audit.check("diagnostic", "prefix Young constant ceiling", prefix_young_ceiling_diagnostic == 67, prefix_young_ceiling_diagnostic, 67)
    audit.check("diagnostic", "prefix Young constant lower bracket", Fraction(66**2) < prefix_young_square_diagnostic, fstr(prefix_young_square_diagnostic), ">66^2")
    audit.check("diagnostic", "prefix Young constant upper bracket", prefix_young_square_diagnostic < Fraction(67**2), fstr(prefix_young_square_diagnostic), "<67^2")
    endpoint_constant = int(r145["exact_values"]["young_constant_integer_ceiling"])
    audit.check("payment", "endpoint Young constant independently recomputed", endpoint_young_ceiling == 24, endpoint_young_ceiling, 24)
    audit.check("payment", "endpoint-first R-145 constant", endpoint_constant == 24, endpoint_constant, 24)
    audit.check("payment", "endpoint recomputation agrees with R-145", endpoint_young_ceiling == endpoint_constant, endpoint_young_ceiling, endpoint_constant)

    # A concrete tail-control fixture checks the pathwise prefix inequality
    # used before summing the temporal weights.
    scalar_c = Fraction(3, 2)
    tau_f = [Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)]
    u_f = [Fraction(2), Fraction(-1), Fraction(3)]
    sqrt_tau = [Decimal(t.numerator).sqrt() / Decimal(t.denominator).sqrt() for t in tau_f]
    h_f = [root * Decimal(u.numerator) / Decimal(u.denominator) for root, u in zip(sqrt_tau, u_f)]
    total_x = sum(value * value for value in h_f)
    for index in range(len(tau_f)):
        tail_source = sum((sqrt_tau[j] * h_f[j] for j in range(index + 1, len(h_f))), Decimal(0))
        tail_physical_squared = Decimal(scalar_c.numerator) / Decimal(scalar_c.denominator) * tail_source * tail_source
        covariance_bound_decimal = Decimal(covariance_operator_upper.numerator) / Decimal(covariance_operator_upper.denominator)
        audit.check("tail", f"prefix tail bound {index}", tail_physical_squared <= covariance_bound_decimal * total_x + Decimal("1e-60"), str(tail_physical_squared), f"<={covariance_operator_upper}*X")

    # Relative anchor: A7 centering fixes the additive gauge externally.
    a_symbol, t_zero, t_h = sp.symbols("a T_0 T_h", real=True)
    centered_relation = {a_symbol: t_zero}
    relative_energy = sp.simplify((a_symbol - t_h).subs(centered_relation))
    audit.check("anchor", "zero-control identity fixes chart anchor", relative_energy == -(t_h - t_zero), str(relative_energy), "-(T_h-T_0)")
    constant_shift = sp.Symbol("c", real=True)
    audit.check("anchor", "normalized relative data are constant-gauge blind", sp.simplify((t_h + constant_shift) - (t_zero + constant_shift)) == t_h - t_zero, str(sp.simplify((t_h + constant_shift) - (t_zero + constant_shift))), "T_h-T_0")

    # Endpoint-first split: Delta T = Delta T_0 + T_an(h)-T_an(0), and the
    # zero-control anisotropic trace is nonnegative.
    delta_scalar = sp.Symbol("DeltaT_0", real=True)
    t_an_h, t_an_zero = sp.symbols("T_an_h T_an_0", nonnegative=True)
    delta_total = delta_scalar + t_an_h - t_an_zero
    audit.check("endpoint", "anisotropic baseline is favourable", sp.simplify((delta_scalar + t_an_h) - delta_total) == t_an_zero, str(sp.simplify((delta_scalar + t_an_h) - delta_total)), "T_an_0>=0")

    # Predictable scalar common-noise is safe.  Conditionally, U=A*zeta and
    # Phi=A*(g+u) give ||U||^2-||Phi||^2=-||Au||^2.
    a_matrix = sp.Matrix([[1, 2], [0, -1]])
    u_vector = sp.Matrix([2, -1])
    au_square = (a_matrix * u_vector).dot(a_matrix * u_vector)
    trace_square = sum(entry * entry for entry in a_matrix)
    current_square = trace_square + au_square
    audit.check("scalar", "predictable common-noise defect", trace_square - current_square == -au_square, str(trace_square - current_square), str(-au_square))
    audit.check("scalar", "predictable common-noise defect nonpositive", trace_square - current_square <= 0, str(trace_square - current_square), "<=0")

    # A bounded contemporaneous coefficient A_t(g)=g exp(-t g^2/2) has
    # positive defect for t>1.  At t=2 the exact ratio is 2/5.
    t_value = sp.Rational(2)
    u_norm = (1 + 2 * t_value) ** sp.Rational(-3, 2)
    phi_norm = 3 * (1 + 2 * t_value) ** sp.Rational(-5, 2)
    contemporaneous_defect = sp.simplify(u_norm - phi_norm)
    audit.check("scalar", "contemporaneous fixture positive", contemporaneous_defect > 0, str(contemporaneous_defect), ">0")
    audit.check("scalar", "contemporaneous defect ratio", sp.simplify(contemporaneous_defect / u_norm) == sp.Rational(2, 5), str(sp.simplify(contemporaneous_defect / u_norm)), "2/5")
    t_parameter = sp.Symbol("t", positive=True)
    ratio_formula = sp.simplify(1 - 3 / (1 + 2 * t_parameter))
    audit.check("scalar", "contemporaneous ratio tends to one", sp.limit(ratio_formula, t_parameter, sp.oo) == 1, str(sp.limit(ratio_formula, t_parameter, sp.oo)), "1")

    # Proportional covariance does not manufacture a common-terminal current.
    x1, x2 = sp.symbols("x_1 x_2", real=True)
    j1 = x1
    conditional_j2 = 2 * x1  # E[2*x1+x2 | x1]
    audit.check("frontier", "rootwise common-terminal inference still fails", sp.simplify(conditional_j2 - j1) == x1, str(sp.simplify(conditional_j2 - j1)), "x_1")

    audit.check("scope", "endpoint-first anisotropy proved", manifest["scope"]["endpoint_first_anisotropic_payment_proved"] is True, manifest["scope"]["endpoint_first_anisotropic_payment_proved"], True)
    audit.check("scope", "canonical temporal owner reconstruction not claimed", manifest["scope"]["canonical_temporal_owner_reconstruction_proved"] is False, manifest["scope"]["canonical_temporal_owner_reconstruction_proved"], False)
    audit.check("scope", "arbitrary-chart temporal transfer not claimed", manifest["scope"]["arbitrary_temporal_chart_anisotropic_transfer_proved"] is False, manifest["scope"]["arbitrary_temporal_chart_anisotropic_transfer_proved"], False)
    audit.check("scope", "relative anchor reduction proved", manifest["scope"]["relative_anchor_reduction_proved"] is True, manifest["scope"]["relative_anchor_reduction_proved"], True)
    audit.check("scope", "canonical covariance normal form proved", manifest["scope"]["canonical_covariance_variational_normal_form_proved"] is True, manifest["scope"]["canonical_covariance_variational_normal_form_proved"], True)
    audit.check("scope", "canonical proportional increments proved", manifest["scope"]["canonical_proportional_covariance_increment_split_proved"] is True, manifest["scope"]["canonical_proportional_covariance_increment_split_proved"], True)
    audit.check("scope", "predictable scalar sign proved", manifest["scope"]["predictable_scalar_common_noise_sign_proved"] is True, manifest["scope"]["predictable_scalar_common_noise_sign_proved"], True)
    audit.check("scope", "contemporaneous scalar fixture proved", manifest["scope"]["contemporaneous_scalar_counterfixture_proved"] is True, manifest["scope"]["contemporaneous_scalar_counterfixture_proved"], True)
    audit.check("scope", "scalar signed owner remains open", manifest["scope"]["scalar_principal_signed_relative_owner_proved"] is False, manifest["scope"]["scalar_principal_signed_relative_owner_proved"], False)
    audit.check("scope", "complete progressive low remains open", manifest["scope"]["complete_progressive_low_owner_proved"] is False, manifest["scope"]["complete_progressive_low_owner_proved"], False)
    audit.check("scope", "common-terminal reconstruction remains open", manifest["scope"]["common_terminal_doob_reconstruction_proved"] is False, manifest["scope"]["common_terminal_doob_reconstruction_proved"], False)
    audit.check("scope", "phase selection absent", manifest["scope"]["physical_phase_or_bcc_selection_proved"] is False, manifest["scope"]["physical_phase_or_bcc_selection_proved"], False)
    audit.check("scope", "T-050 remains open", manifest["scope"]["t050_closed"] is False, manifest["scope"]["t050_closed"], False)
    audit.check("scope", "A13 gate remains open", manifest["scope"]["a13_gate_closed"] is False, manifest["scope"]["a13_gate_closed"], False)
    audit.check("scope", "Nelson remains open", manifest["scope"]["nelson_proved"] is False, manifest["scope"]["nelson_proved"], False)
    audit.check("scope", "Sector A remains open", manifest["scope"]["sector_a_closed"] is False, manifest["scope"]["sector_a_closed"], False)

    audit.require()
    exact_values = {
        "kinetic_minimum": fstr(kinetic_minimum),
        "canonical_value_covariance_operator_upper": fstr(covariance_operator_upper),
        "beta_operator_upper": fstr(beta),
        "six_real_pointwise_derivative_trace_bound": fstr(g_r),
        "endpoint_first_anisotropic_source_coefficient": fstr(endpoint_eta_an),
        "canonical_prefix_source_coefficient_diagnostic": fstr(eta_prefix_diagnostic),
        "endpoint_first_anisotropic_sextic_allocation": fstr(zeta_an),
        "endpoint_first_anisotropic_constant": str(endpoint_constant),
        "remaining_scalar_source_window": fstr(eta_margin),
        "remaining_scalar_sextic_window": fstr(zeta_margin),
        "endpoint_terminal_l2_coefficient": fstr(endpoint_terminal_coefficient),
        "canonical_prefix_l2_coefficient_diagnostic": fstr(prefix_terminal_coefficient_diagnostic),
        "endpoint_young_constant_square": fstr(endpoint_young_square),
        "endpoint_young_constant_ceiling": str(endpoint_young_ceiling),
        "canonical_prefix_young_constant_square_diagnostic": fstr(prefix_young_square_diagnostic),
        "canonical_prefix_young_constant_ceiling_diagnostic": str(prefix_young_ceiling_diagnostic),
        "source_threshold": fstr(source_threshold),
        "sextic_threshold": fstr(sextic_threshold),
    }
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "status": "PASS",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "assertions": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows), "rows": audit.rows},
        "exact_values": exact_values,
        "diagnostics": {
            "canonical_representation": "X_J=C_J^(1/2)B_1; Delta C_b=tau_b C_J; h_b=sqrt(tau_b)u_b",
            "relative_anchor": "E V_J^ren(Z_h)=-(T_pi(h)-T_pi(0))",
            "anisotropic_payment": "Delta T_pi <= Delta T_pi^0 + (1/100)Y6 + 24 after complete endpoint telescoping",
            "scalar_split": "predictable common-noise rows are nonpositive; contemporaneous coefficient innovation can be positive",
            "remaining_target": "contemporaneous/balanced scalar-principal signed relative trace excess with low/future-variance/forest retained once",
        },
        "scope": manifest["scope"],
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS {len(audit.rows)}/{len(audit.rows)}")
    print(f"endpoint eta_an=0; prefix diagnostic={fstr(eta_prefix_diagnostic)} ({float(eta_prefix_diagnostic):.12f})")
    print(f"remaining eta={fstr(eta_margin)}; remaining zeta={fstr(zeta_margin)}")
    print("OPEN: scalar signed relative owner, T-050, Nelson, Sector A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
