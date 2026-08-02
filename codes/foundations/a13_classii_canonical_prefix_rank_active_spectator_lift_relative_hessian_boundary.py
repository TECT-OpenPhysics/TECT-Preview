#!/usr/bin/env python3
"""Primary certificate for the phase-neutral A13 R-148 checkpoint.

The certificate proves three sharply scoped facts.  First, the exact R-147
fresh final scalar innovation cannot be realised by a nonzero final block of
the R-146 proportional-covariance canonical chart when the registered
covariance is positive definite on that plane.  Second, a noncanonical last-root Gaussian
coefficient completion has an exact positive trace-bracket mismatch for
pointwise sufficiently small noise at each fixed R-147 adverse point.  Third,
the negative absolute-owner curvature f'' does not identify a physical control
Hessian.  In a declared coefficient-background parameter family, the
parameter Hessian uses f'''' and is positive at small noise after source and
sextic terms are included, while its first derivative is nonzero (negative
for the oriented convention R>0).  No physical source synthesis is claimed.

No production owner transport, physical phase selection, or T-050 closure is
asserted.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass, field
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
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / (
    "classii_canonical_prefix_rank_active_spectator_lift_"
    "relative_hessian_boundary_manifest.json"
)
OUTPUT = REPO / "claims" / CLAIM / "runs" / (
    f"2026-08-02-primary-{SLUG}"
) / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                payload,
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                default=str,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(
        self, category: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        self.rows.append(
            {
                "category": category,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(
                json.dumps(failures, indent=2, ensure_ascii=True, default=str)
            )


def gaussian_expectation(function: Callable[[np.ndarray], np.ndarray], order: int) -> float:
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return float(np.dot(weights, function(np.sqrt(2.0) * nodes)) / math.sqrt(math.pi))


def main() -> int:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger id", manifest["result_ledger_id"] == "R-148", manifest["result_ledger_id"], "R-148")
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    for label, relative in manifest["authorities"].items():
        path = REPO / relative
        audit.check("authority", f"{label} exists", path.is_file(), relative, "file")
        actual = sha256(path)
        expected = manifest["authority_hashes"][label]
        audit.check("authority", f"{label} hash", actual == expected, actual, expected)

    # ------------------------------------------------------------------
    # 1. Registered covariance and the fresh-final-block rank obstruction.
    # ------------------------------------------------------------------
    a1 = json.loads(
        (REPO / manifest["authorities"]["a1_production_manifest"])
        .read_text(encoding="utf-8")
    )
    parameters = a1["parameters"]
    family = [sp.Rational(str(value)) for value in parameters["family_masses"]]
    lock = sp.Rational(str(parameters["k_lock"]))
    z0 = [sp.Rational(str(value)) for value in parameters["z0"]]
    z0_norm = sum(value**2 for value in z0)
    M = sp.Matrix(
        [
            [
                family[i] * int(i == j)
                + lock * (int(i == j) - z0[i] * z0[j] / z0_norm)
                for j in range(3)
            ]
            for i in range(3)
        ]
    )
    leading_minors = [sp.factor(M[:k, :k].det()) for k in (1, 2, 3)]
    expected_minors = [sp.Rational(1, 10), sp.Rational(21, 2000), sp.Rational(3, 3125)]
    audit.check("covariance", "A1 family-lock mass derived", M == sp.Matrix([[sp.Rational(10,100),-sp.Rational(5,100),-sp.Rational(5,100)],[-sp.Rational(5,100),sp.Rational(13,100),-sp.Rational(5,100)],[-sp.Rational(5,100),-sp.Rational(5,100),sp.Rational(17,100)]]), M.tolist(), "registered M")
    audit.check("covariance", "Sylvester minors", leading_minors == expected_minors, [str(x) for x in leading_minors], [str(x) for x in expected_minors])
    audit.check("covariance", "mass block positive definite", all(value > 0 for value in leading_minors), [str(x) for x in leading_minors], "all positive")

    kinetic = sp.symbols("a", nonnegative=True)
    Akin = kinetic * sp.eye(3) + M
    det_akin = sp.factor(Akin.det())
    expected_det = (25000 * kinetic**3 + 10000 * kinetic**2 + 1115 * kinetic + 24) / 25000
    audit.check("covariance", "kinetic determinant", sp.simplify(det_akin - expected_det) == 0, str(det_akin), str(expected_det))
    audit.check("covariance", "kinetic determinant coefficients positive", all(coefficient > 0 for coefficient in sp.Poly(sp.together(expected_det * 25000), kinetic).all_coeffs()), str(expected_det), "positive on a>=0")

    # The active-spectator plane is the first and third internal coordinates.
    selector = sp.Matrix([[1, 0], [0, 0], [0, 1]])
    C = sp.simplify(Akin.inv())
    C_rad = sp.simplify(selector.T * C * selector)
    det_c_rad = sp.factor(C_rad.det())
    expected_det_c_rad = 250 * (100 * kinetic + 13) / (
        25000 * kinetic**3 + 10000 * kinetic**2 + 1115 * kinetic + 24
    )
    audit.check("covariance", "radial restriction determinant", sp.simplify(det_c_rad - expected_det_c_rad) == 0, str(det_c_rad), str(expected_det_c_rad))
    audit.check("covariance", "radial restriction positive at audit points", all(C_rad.subs(kinetic, value).is_positive_definite for value in (0, sp.Rational(1, 2), 2)), [str(C_rad.subs(kinetic, value).det()) for value in (0, sp.Rational(1, 2), 2)], "positive definite")

    tau = sp.Rational(2, 5)
    canonical_block = sp.simplify(tau * C_rad.subs(kinetic, 1))
    w = sp.Matrix([1, 1])
    v = sp.Matrix([1, -1])
    rank_one_past = w * w.T
    rank_one_current = v * v.T
    audit.check("prefix-rank", "canonical block rank two", canonical_block.rank() == 2, canonical_block.rank(), 2)
    audit.check("prefix-rank", "canonical determinant scales by tau squared", sp.simplify(canonical_block.det() - tau**2 * C_rad.subs(kinetic, 1).det()) == 0, str(canonical_block.det()), str(tau**2 * C_rad.subs(kinetic, 1).det()))
    audit.check("prefix-rank", "no-correction past fixture rank one", rank_one_past.rank() == 1 and rank_one_past.det() == 0, rank_one_past.tolist(), "rank 1 fixture only")
    audit.check("prefix-rank", "fresh final line covariance rank one", rank_one_current.rank() == 1 and rank_one_current.det() == 0, rank_one_current.tolist(), "rank 1")
    audit.check("prefix-rank", "fresh line is not a proportional canonical final block", canonical_block != rank_one_current, canonical_block.tolist(), "different from fresh rank-one block")

    # ------------------------------------------------------------------
    # 2. Exact R-147 row, derivative thresholds, and interpretation audit.
    # ------------------------------------------------------------------
    q, radius, floor, p_norm = sp.symbols("q R e P", real=True, positive=True)
    r147_manifest = json.loads(
        (REPO / manifest["authorities"]["r147_manifest"])
        .read_text(encoding="utf-8")
    )
    coefficient_inputs = r147_manifest["audit_inputs"]
    alpha = sp.sympify(coefficient_inputs["production_alpha"])
    c0 = sp.sympify(
        coefficient_inputs["production_p_coefficient"].replace("P", "*P"),
        locals={"P": p_norm},
    )
    c1 = sp.sympify(
        coefficient_inputs["production_l_coefficient"].replace("P", "*P"),
        locals={"P": p_norm},
    )
    active = radius + q
    spectator = radius - q
    density = active**2 + spectator**2 + floor
    rational_row = active - alpha * active**2 * (active - spectator) / density
    f = sp.factor(4 * c0 * active**2 + 4 * c1 * rational_row**2)
    f2 = sp.factor(sp.diff(f, q, 2).subs(q, 0))
    f3 = sp.factor(sp.diff(f, q, 3).subs(q, 0))
    f4 = sp.factor(sp.diff(f, q, 4).subs(q, 0))
    expected_f2 = 3 * (-528 * radius**4 - 88 * radius**2 * floor + 113 * floor**2) / (1000 * p_norm * (2 * radius**2 + floor) ** 2)
    expected_f3 = -9 * radius * (16 * radius**2 + 27 * floor) / (50 * p_norm * (2 * radius**2 + floor) ** 2)
    expected_f4 = 18 * (112 * radius**4 + 48 * radius**2 * floor - 9 * floor**2) / (25 * p_norm * (2 * radius**2 + floor) ** 3)
    audit.check("row-jet", "exact second derivative", sp.simplify(f2 - expected_f2) == 0, str(f2), str(expected_f2))
    audit.check("row-jet", "exact third derivative", sp.simplify(f3 - expected_f3) == 0, str(f3), str(expected_f3))
    audit.check("row-jet", "third derivative strictly negative", sp.ask(sp.Q.negative(expected_f3)) is True, str(expected_f3), "<0")
    audit.check("row-jet", "exact fourth derivative", sp.simplify(f4 - expected_f4) == 0, str(f4), str(expected_f4))

    rho = sp.symbols("rho", real=True)
    p2 = -528 * rho**2 - 88 * rho + 113
    adverse_threshold = -sp.Rational(1, 12) + 5 * sp.sqrt(154) / 132
    audit.check("threshold", "R-147 threshold root", sp.simplify(p2.subs(rho, adverse_threshold)) == 0, str(adverse_threshold), "root")
    audit.check("threshold", "R-147 threshold interval", sp.Rational(3867, 10000) < adverse_threshold < sp.Rational(3868, 10000), str(sp.N(adverse_threshold, 16)), "(0.3867,0.3868)")

    p4 = 112 * rho**2 + 48 * rho - 9
    hessian_threshold = -sp.Rational(3, 14) + 3 * sp.sqrt(11) / 28
    audit.check("threshold", "fourth-derivative threshold root", sp.simplify(p4.subs(rho, hessian_threshold)) == 0, str(hessian_threshold), "root")
    audit.check("threshold", "fourth-derivative threshold interval", sp.Rational(1410, 10000) < hessian_threshold < sp.Rational(1411, 10000), str(sp.N(hessian_threshold, 16)), "(0.1410,0.1411)")
    audit.check("threshold", "adverse threshold above one third", sp.simplify(adverse_threshold - sp.Rational(1, 3)) > 0, str(adverse_threshold), ">1/3")
    audit.check("threshold", "fourth threshold below one seventh", sp.simplify(sp.Rational(1, 7) - hessian_threshold) > 0, str(hessian_threshold), "<1/7")
    audit.check("threshold", "R-147 adverse region has positive f4 at zero noise", adverse_threshold > hessian_threshold, [str(adverse_threshold), str(hessian_threshold)], "r147>r4")

    # ------------------------------------------------------------------
    # 3. Direct Gaussian mismatch in a declared noncanonical last-root chart.
    # ------------------------------------------------------------------
    fixture_inputs = manifest["audit_inputs"]["fixture"]
    fixture = {
        radius: sp.Rational(fixture_inputs["radius"]),
        floor: sp.Rational(fixture_inputs["floor"]),
        p_norm: sp.Rational(fixture_inputs["p_norm"]),
    }
    sigma = float(sp.Rational(fixture_inputs["sigma"]))
    row_p = sp.lambdify(q, (2 * sp.sqrt(c0) * active).subs(fixture), "numpy")
    row_l = sp.lambdify(q, (2 * sp.sqrt(c1) * rational_row).subs(fixture), "numpy")
    f_num = sp.lambdify(q, f.subs(fixture), "numpy")
    f2_num = sp.lambdify(q, sp.diff(f, q, 2).subs(fixture), "numpy")

    def a_values(g: np.ndarray) -> np.ndarray:
        values = sigma * g
        return np.vstack((row_p(values), row_l(values)))

    orders = (48, 80, 112)
    mismatch_table: list[dict[str, float]] = []
    for order in orders:
        bar_tau = sigma**2 * gaussian_expectation(lambda g: f_num(sigma * g), order)
        nodes, weights = np.polynomial.hermite.hermgauss(order)
        g = np.sqrt(2.0) * nodes
        Avals = a_values(g)
        norm = 1.0 / math.sqrt(math.pi)
        b = sigma * (Avals * (weights * g)[None, :]).sum(axis=1) * norm
        raw = sigma**2 * float(np.dot(weights, g**2 * f_num(sigma * g)) * norm)
        beta = raw - float(np.dot(b, b))
        delta = bar_tau - beta
        stein = -sigma**4 * gaussian_expectation(lambda x: f2_num(sigma * x), order) + float(np.dot(b, b))
        mismatch_table.append({"order": order, "bar_tau": bar_tau, "beta": beta, "b2": float(np.dot(b, b)), "delta": delta, "stein": stein})
        audit.check("mismatch", f"positive defect at GH{order}", delta > 0.0, delta, ">0")
        audit.check("mismatch", f"mean square positive at GH{order}", float(np.dot(b, b)) > 0.0, float(np.dot(b, b)), ">0")
        audit.check("mismatch", f"Stein identity at GH{order}", abs(delta - stein) < 2e-12, delta - stein, "abs<2e-12")
    audit.check("mismatch", "GH convergence", abs(mismatch_table[-1]["delta"] - mismatch_table[-2]["delta"]) < 1e-13, [row["delta"] for row in mismatch_table], "last two within 1e-13")
    audit.check("mismatch", "matching condition fails", mismatch_table[-1]["delta"] != 0.0, mismatch_table[-1]["delta"], "nonzero")

    # The diagonal coefficient energy f(q)=||A(q)||^2 cannot recover mixed
    # endpoint Grams or jet energies.  A q-dependent orthogonal gauge gives an
    # exact two-dimensional witness.
    gauge_q = sp.symbols("s", real=True)
    rotation = sp.Matrix(
        [
            [1 - gauge_q**2, -2 * gauge_q],
            [2 * gauge_q, 1 - gauge_q**2],
        ]
    ) / (1 + gauge_q**2)
    e1 = sp.Matrix([1, 0])
    gauged = sp.simplify(rotation * e1)
    audit.check("nonidentifiability", "rational gauge orthogonal", sp.simplify(rotation.T * rotation - sp.eye(2)) == sp.zeros(2), str(sp.simplify(rotation.T * rotation)), "I2")
    audit.check("nonidentifiability", "diagonal norm preserved", sp.simplify((gauged.T * gauged)[0]) == 1, str(sp.simplify((gauged.T * gauged)[0])), "1")
    audit.check("nonidentifiability", "mixed Gram changes", (e1.T * e1)[0] == 1 and sp.simplify((gauged.subs(gauge_q, 0).T * gauged.subs(gauge_q, 1))[0]) == 0, [str((e1.T * e1)[0]), str(sp.simplify((gauged.subs(gauge_q, 0).T * gauged.subs(gauge_q, 1))[0]))], ["1", "0"])
    gauge_derivative = sp.diff(gauged, gauge_q).subs(gauge_q, 0)
    audit.check("nonidentifiability", "jet energy changes", sp.simplify((gauge_derivative.T * gauge_derivative)[0]) == 4, str(sp.simplify((gauge_derivative.T * gauge_derivative)[0])), "4 versus zero")

    # ------------------------------------------------------------------
    # 4. Minimal relative-control diagnostic and no-stationarity warning.
    # ------------------------------------------------------------------
    m = sp.symbols("m", real=True)
    sig, kappa = sp.symbols("sigma kappa", positive=True)

    def gaussian_polynomial_expectation(expression: sp.Expr) -> sp.Expr:
        total = sp.Integer(0)
        # Expand first in a dummy Gaussian variable so moments are explicit.
        gsym = sp.symbols("g", real=True)
        expanded = sp.Poly(sp.expand(expression.subs(q, m + sig * gsym)), gsym)
        for (power,), coefficient in expanded.terms():
            if power % 2:
                continue
            moment = sp.factorial2(power - 1) if power else 1
            total += coefficient * moment
        return sp.expand(total)

    radial_sextic = sp.Rational(6, 5) * (radius**2 + q**2) ** 3
    sextic_expectation = gaussian_polynomial_expectation(radial_sextic)
    sextic_base = sp.simplify(sextic_expectation.subs(m, 0))
    sextic_difference = sp.factor(sextic_expectation - sextic_base)
    expected_sextic_difference = (
        sp.Rational(18, 5) * m**2 * (radius**4 + 6 * radius**2 * sig**2 + 15 * sig**4)
        + sp.Rational(18, 5) * m**4 * (radius**2 + 5 * sig**2)
        + sp.Rational(6, 5) * m**6
    )
    audit.check("relative-action", "terminal sextic difference", sp.simplify(sextic_difference - expected_sextic_difference) == 0, str(sextic_difference), str(expected_sextic_difference))
    source_difference = sp.Rational(9, 20) * kappa * m**2
    source_hessian = sp.diff(source_difference, m, 2)
    sextic_hessian = sp.factor(sp.diff(sextic_difference, m, 2).subs(m, 0))
    expected_sextic_hessian = sp.Rational(36, 5) * (radius**4 + 6 * radius**2 * sig**2 + 15 * sig**4)
    audit.check("relative-action", "source Hessian", source_hessian == sp.Rational(9, 10) * kappa, str(source_hessian), "9*kappa/10")
    audit.check("relative-action", "sextic Hessian", sp.simplify(sextic_hessian - expected_sextic_hessian) == 0, str(sextic_hessian), str(expected_sextic_hessian))

    # Stein gives Pcomp(m)=sigma^4 E f''(m+sigma g)/2.  Therefore its
    # first and second coefficient-parameter derivatives use f''' and f''''.
    gradient_small_noise = sp.factor(sig**4 * f3 / 2)
    hessian_small_noise = sp.factor(sig**4 * f4 / 2)
    audit.check("relative-action", "small-noise owner gradient negative", sp.ask(sp.Q.negative(gradient_small_noise)) is True, str(gradient_small_noise), "<0 for sigma>0")
    audit.check("relative-action", "owner Hessian uses fourth derivative", sp.simplify(hessian_small_noise - sig**4 * expected_f4 / 2) == 0, str(hessian_small_noise), "sigma^4*f4/2")
    audit.check("relative-action", "origin is not proved stationary", manifest["scope"]["minimal_last_root_origin_stationary_proved"] is False, manifest["scope"]["minimal_last_root_origin_stationary_proved"], False)

    h0 = sp.Rational(9, 10) * kappa + sp.Rational(36, 5) * radius**4
    audit.check("relative-action", "zero-noise source-sextic curvature positive", sp.ask(sp.Q.positive(h0.subs(kappa, 1))) is True, str(h0), ">0 for kappa>0 or R>0")

    scope = manifest["scope"]
    expected_false = (
        "adapted_past_rank_one_necessity_proved",
        "uniform_adverse_region_noise_threshold_proved",
        "physical_deterministic_control_hessian_identified",
        "exact_r147_line_is_r146_canonical_chart",
        "old_owner_transport_proved",
        "r063_production_forest_identified",
        "complete_owner_sign_determined",
        "physical_phase_selected",
        "t050_closed",
        "sector_a_closed",
    )
    for key in expected_false:
        audit.check("scope", key, scope[key] is False, scope[key], False)
    audit.check("scope", "fresh final prefix rank obstruction proved", scope["fresh_final_canonical_prefix_rank_obstruction_proved"] is True, scope["fresh_final_canonical_prefix_rank_obstruction_proved"], True)
    audit.check("scope", "no-correction past fixture proved", scope["no_correction_past_rank_fixture_proved"] is True, scope["no_correction_past_rank_fixture_proved"], True)
    audit.check("scope", "generic mismatch identity proved", scope["generic_last_root_mismatch_identity_proved"] is True, scope["generic_last_root_mismatch_identity_proved"], True)
    audit.check("scope", "coefficient-parameter Hessian diagnostic proved", scope["minimal_last_root_coefficient_parameter_hessian_diagnostic_proved"] is True, scope["minimal_last_root_coefficient_parameter_hessian_diagnostic_proved"], True)
    audit.check("scope", "coefficient jet does not identify full owner", scope["coefficient_diagonal_identifies_full_owner"] is False, scope["coefficient_diagonal_identifies_full_owner"], False)

    audit.require()
    payload = {
        "schema": SCHEMA,
        "script_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows),
            "failed": 0,
            "rows": audit.rows,
        },
        "exact_values": {
            "mass_leading_minors": [str(value) for value in leading_minors],
            "kinetic_determinant": str(det_akin),
            "radial_covariance_determinant": str(det_c_rad),
            "active_spectator_f2": str(f2),
            "active_spectator_f3": str(f3),
            "active_spectator_f4": str(f4),
            "r147_threshold": str(adverse_threshold),
            "relative_hessian_threshold": str(hessian_threshold),
            "sextic_difference": str(expected_sextic_difference),
            "sextic_hessian": str(expected_sextic_hessian),
        },
        "cross_values": {
            "r147_threshold": str(adverse_threshold),
            "relative_hessian_threshold": str(hessian_threshold),
            "fixture_delta": mismatch_table[-1]["delta"],
            "fixture_mean_square": mismatch_table[-1]["b2"],
        },
        "gauss_hermite": mismatch_table,
        "scope": scope,
        "theorem_summary": {
            "canonical_rank": "the exact rank-one fresh R-147 innovation is not a nonzero R-146 proportional-covariance final block",
            "generic_chart": "at each fixed adverse point a declared noncanonical last-root coefficient chart has positive trace-bracket mismatch for sufficiently small noise",
            "parameter_hessian": "f'' signs the absolute owner, while the coefficient-background parameter Hessian uses f''''; no physical control lift is identified",
            "phase_status": "neutral",
        },
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(OUTPUT, payload)
    print(f"PASS {RESULT_ID} ({len(audit.rows)}/{len(audit.rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
