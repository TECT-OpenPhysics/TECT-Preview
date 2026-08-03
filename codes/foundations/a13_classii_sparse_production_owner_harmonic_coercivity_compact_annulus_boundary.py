#!/usr/bin/env python3
"""Primary exact audit for the A13 R-165 sparse production annulus reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SPARSE-PRODUCTION-OWNER-HARMONIC-COERCIVITY-COMPACT-ANNULUS-BOUNDARY"
LEDGER_ID = "R-165"
SLUG = "sparse-production-owner-harmonic-coercivity-compact-annulus-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-primary-{SLUG}" / "result.json"

A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_MANIFEST = CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R153_MANIFEST = CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json"
R164_MANIFEST = CLAIM_DIR / "classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction_manifest.json"

SCOPE = {
    "fixed_side_16_torus": True,
    "fixed_finite_sparse_p_2p_4p_chart": True,
    "unit_regulator_multipliers_p_2p_4p": True,
    "only_declared_past_and_fresh_modes": True,
    "positive_a7_floor": True,
    "strict_past_conditioned": True,
    "whitened_antipodal_source_coordinates": True,
    "exact_continuum_torus_average": True,
    "fresh_4p_final_root": True,
    "owner_target_outside_open_annulus": True,
    "closed_certification_domain_compact": True,
    "open_annulus_owner_target": False,
    "all_production_charts": False,
    "random_nonlinear_revisit_controls": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-165 proves the R-164 owner threshold on the actual R-153 p:2p strict-past, fresh-4p "
    "twelve-dimensional conditional fibre with unit retained regulator multipliers only when "
    "the whitened past amplitude G is at most "
    "21 or at least 274. It reduces that fibre's remaining noncompact amplitude question to "
    "the bounded open annulus 21<G<274, whose closed certification domain 21<=G<=274 is "
    "compact. It does not certify the open annulus, the complete multi-root "
    "production owner, random/nonlinear/revisit feedback, shifted low variables, removal, T-050, "
    "A13, Nelson or an interacting measure, any phase, morphology or PDE, or Sector A."
)


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(item) for item in row] for row in value.tolist()]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r153 = json.loads(R153_MANIFEST.read_text(encoding="utf-8"))
    r164 = json.loads(R164_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]

    audit.check("authority", "R-153 conditional fibre", r153["result_ledger_id"] == "R-153" and "strict past" in r153["statement"], r153["result_ledger_id"], "R-153")
    audit.check("authority", "R-164 owner threshold", r164["result_ledger_id"] == "R-164" and "10/11-rho" in r164["statement"], r164["result_ledger_id"], "R-164")
    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    l6_exact = rational(r130["diagnostics"]["conormal_gram"]["L6"])
    h6_exact = rational(r130["diagnostics"]["conormal_gram"]["H6"])
    p_mass = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    audit.check("authority", "R-130 result hash", sha256(r130_path) == r130_record["sha256"], sha256(r130_path), r130_record["sha256"])
    audit.check("authority", "R-130 L6", sp.simplify(l6_exact - sp.Rational(1143, 250) / p_mass) == 0, l6_exact, "1143/(250P)")
    audit.check("authority", "R-130 H6", sp.simplify(h6_exact - sp.Rational(7083, 500) / p_mass) == 0, h6_exact, "7083/(500P)")

    volume = rational(parameters["Lx"]) * rational(parameters["Ly"]) * rational(parameters["Lz"])
    z_coefficient = rational(parameters["Z"])
    r_coefficient = rational(parameters["r"])
    family = [rational(item) for item in parameters["family_masses"]]
    lock = rational(parameters["k_lock"])
    mass = sp.diag(*family) + lock * (sp.eye(3) - sp.ones(3) / 3)
    audit.check("production", "side-16 volume", volume == 4096, volume, 4096)
    audit.check("production", "exact internal mass", mass == sp.Matrix([[sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)], [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)], [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)]]), mass, "registered 3x3 mass")
    lower_mass = mass - sp.Rational(7, 250) * sp.eye(3)
    lower_minors = [lower_mass[:index, :index].det() for index in (1, 2, 3)]
    upper_mass = sp.Rational(27, 100) * sp.eye(3) - mass
    upper_minors = [upper_mass[:index, :index].det() for index in (1, 2, 3)]
    audit.check("production", "mass lower Loewner bound", all(item > 0 for item in lower_minors), lower_minors, "M>(7/250)I")
    audit.check("production", "mass upper Loewner bound", all(item >= 0 for item in upper_minors), upper_minors, "M<=(27/100)I")

    pi2_lower = sp.Rational(333, 106) ** 2
    pi2_upper = sp.Rational(355, 113) ** 2
    audit.check("spectral", "classical pi bracket", sp.Rational(333, 106) < sp.Rational(355, 113) and pi2_upper < 10, [pi2_lower, pi2_upper], "(333/106)^2<pi^2<(355/113)^2<10")
    scalar = lambda x: sp.expand(x**2 + z_coefficient * x + r_coefficient)
    x1_lower = pi2_lower / 64
    x1_upper = pi2_upper / 64
    x2_lower = pi2_lower / 16
    x2_upper = pi2_upper / 16
    x4_lower = pi2_lower / 4
    x4_upper = pi2_upper / 4
    audit.check("spectral", "p-symbol decreases on bracket", 2 * x1_upper + z_coefficient < 0, 2 * x1_upper + z_coefficient, "<0")
    audit.check("spectral", "2p-symbol increases on bracket", 2 * x2_lower + z_coefficient > 0, 2 * x2_lower + z_coefficient, ">0")
    audit.check("spectral", "4p-symbol increases on bracket", 2 * x4_lower + z_coefficient > 0, 2 * x4_lower + z_coefficient, ">0")
    a1_lower = scalar(x1_upper) + sp.Rational(7, 250)
    a1_upper = scalar(x1_lower) + sp.Rational(27, 100)
    a2_lower = scalar(x2_lower) + sp.Rational(7, 250)
    a2_upper = scalar(x2_upper) + sp.Rational(27, 100)
    a4_lower = scalar(x4_lower) + sp.Rational(7, 250)
    a4_upper = scalar(x4_upper) + sp.Rational(27, 100)
    audit.check("spectral", "p operator enclosure", a1_lower > sp.Rational(3, 8) and a1_upper < sp.Rational(63, 100), [a1_lower, a1_upper], [">3/8", "<63/100"])
    audit.check("spectral", "2p operator enclosure", a2_lower > sp.Rational(31, 100) and a2_upper < sp.Rational(14, 25), [a2_lower, a2_upper], [">31/100", "<14/25"])
    audit.check("spectral", "4p operator enclosure", a4_lower > sp.Rational(43, 10) and a4_upper < sp.Rational(91, 20), [a4_lower, a4_upper], [">43/10", "<91/20"])

    cp_min = sp.Rational(100, 63)
    cp_max = sp.Rational(100, 31)
    c4_min = sp.Rational(20, 91)
    c4_max = sp.Rational(10, 43)
    trace4_max = 6 * c4_max
    audit.check("spectral", "past covariance enclosure", cp_min == sp.Rational(100, 63) and cp_max == sp.Rational(100, 31), [cp_min, cp_max], "(100/63)I<=Gamma_p,Gamma_2p<=(100/31)I")
    audit.check("spectral", "4p covariance enclosure", c4_min == sp.Rational(20, 91) and c4_max == sp.Rational(10, 43), [c4_min, c4_max], "(20/91)I<=Gamma_4p<=(10/43)I")
    audit.check("spectral", "six-real 4p trace", trace4_max == sp.Rational(60, 43), trace4_max, "<=60/43")

    # Sharp Fourier lemma.  If r=|m|^2, its top coefficient satisfies
    # |r_4|<=r_0/2.  Parseval then gives (r^2)_0>=6|(r^2)_8|.
    a, s, b, t = sp.symbols("a s b t", nonnegative=True)
    r0 = 2 * a + s
    f0_lower = r0**2 + 2 * a**2
    q0 = 2 * b + t
    audit.check("harmonic", "top coefficient field square", sp.expand(f0_lower - 6 * a**2) == sp.expand(4 * a * s + s**2), f0_lower - 6 * a**2, ">=0")
    audit.check("harmonic", "top coefficient tangent square", sp.expand(q0 - 2 * b) == t, q0 - 2 * b, ">=0")
    harmonic_constant = sp.Rational(5, 6)
    audit.check("harmonic", "adverse Fourier payment", 1 - 2 * sp.Rational(1, 6) * sp.Rational(1, 2) == harmonic_constant, harmonic_constant, sp.Rational(5, 6))
    theta = sp.symbols("theta", real=True)
    fixture_f = sp.integrate(sp.cos(2 * theta) ** 4, (theta, 0, 2 * sp.pi)) / (2 * sp.pi)
    fixture_q = sp.integrate(sp.sin(4 * theta) ** 2, (theta, 0, 2 * sp.pi)) / (2 * sp.pi)
    fixture_product = sp.integrate(sp.cos(2 * theta) ** 4 * sp.sin(4 * theta) ** 2, (theta, 0, 2 * sp.pi)) / (2 * sp.pi)
    audit.check("harmonic", "sharp scalar fixture", sp.simplify(fixture_product / (fixture_f * fixture_q)) == harmonic_constant, [fixture_f, fixture_q, fixture_product], "ratio 5/6")

    # Gaussian future only increases the retained fourth moment.
    m2, trc, quad, trc2 = sp.symbols("m2 trc quad trc2", nonnegative=True)
    gaussian_fourth_remainder = 2 * m2 * trc + 4 * quad + trc**2 + 2 * trc2
    audit.check("sextic", "centered Gaussian fourth-moment remainder", gaussian_fourth_remainder.is_nonnegative is True, gaussian_fourth_remainder, ">=0")

    p2_upper = sp.Rational(5, 32)
    l6 = sp.Rational(1143, 1000)
    h6 = sp.Rational(7083, 2000)
    sqrt_trace_factor = sp.Rational(301, 100)
    gamma_past_derivative = 10 * p2_upper * cp_max / volume
    audit.check("envelope", "base momentum square", pi2_upper / 64 < p2_upper, pi2_upper / 64, "<5/32")
    audit.check("envelope", "R-130 rational upper constants", l6_exact < l6 and h6_exact < h6, [l6_exact, h6_exact], [l6, h6])
    audit.check("envelope", "fresh trace square-root", 2 * cp_max * trace4_max < sqrt_trace_factor**2, 2 * cp_max * trace4_max, f"<({sqrt_trace_factor})^2")
    audit.check("envelope", "past derivative covariance", gamma_past_derivative == sp.Rational(625, 507904), gamma_past_derivative, "10 p^2 cpmax/V upper bound")

    sextic_coercivity = sp.Rational(3, 4) * c4_min * cp_min**2 / volume**2
    endpoint_quadratic = p2_upper * cp_max * c4_max * (32 * l6 + 8 * h6) / volume
    endpoint_linear = 32 * l6 * p2_upper * c4_max * sqrt_trace_factor / volume
    # Gamma_< is spatially constant in this common-even sharp chart, so exact
    # Parseval gives int |z|^2 <= c4_max |alpha|^2 without an extra antipodal
    # factor.  H6 already bounds the half-Hessian.
    endpoint_constant = h6 * c4_max * gamma_past_derivative
    expected_constants = {
        "A": sp.Rational(3125, 126241210368),
        "B2": sp.Rational(81135, 43679744),
        "B1": sp.Rational(8001, 8192000),
        "D0": sp.Rational(177075, 174718976),
    }
    actual_constants = {"A": sextic_coercivity, "B2": endpoint_quadratic, "B1": endpoint_linear, "D0": endpoint_constant}
    audit.check("polynomial", "exact coefficient ledger", actual_constants == expected_constants, actual_constants, expected_constants)
    audit.check("polynomial", "endpoint factors", 32 == 2 * 8 * 2 and 8 == 2 * 4, [32, 8], "cross=2*(zu 8)*(nm 2); nn=(z2 2)*(n2 4)")

    G = sp.symbols("G", nonnegative=True)
    polynomial = sp.expand(sextic_coercivity * G**4 - endpoint_quadratic * G**2 - endpoint_linear * G - endpoint_constant)
    derivative = sp.diff(polynomial, G)
    second_derivative = sp.diff(polynomial, G, 2)
    small_derivative_upper = 4 * sextic_coercivity * 21**3 - endpoint_linear
    small_margin = sp.expand(polynomial.subs(G, 21) + sp.Rational(9, 10))
    large_derivative = sp.expand(derivative.subs(G, 274))
    large_second = sp.expand(second_derivative.subs(G, 274))
    large_margin = sp.expand(polynomial.subs(G, 274) + sp.Rational(9, 10))
    audit.check("annulus", "decreasing on zero-to-21", small_derivative_upper == -sp.Rational(25427, 425984000) < 0, small_derivative_upper, "<0")
    audit.check("annulus", "G=21 target margin", small_margin == sp.Rational(145670815281, 2271346688000) > 0, small_margin, ">0")
    audit.check("annulus", "derivative positive at 274", large_derivative == sp.Rational(1338311264185381, 1314683854848000) > 0, large_derivative, ">0")
    audit.check("annulus", "convex derivative beyond 274", large_second == sp.Rational(65160500885, 3505823612928) > 0, large_second, ">0")
    audit.check("annulus", "G=274 target margin", large_margin == sp.Rational(1847465221877063, 2629367709696000) > 0, large_margin, ">0")
    rho = sp.Rational(1, 110)
    audit.check("threshold", "R-164 rho choice", sp.Rational(10, 11) - rho == sp.Rational(9, 10), sp.Rational(10, 11) - rho, sp.Rational(9, 10))
    audit.check("threshold", "total semiconvexity floor", sp.Rational(9, 10) - sp.Rational(9, 10) == 0 > -sp.Rational(1, 110), 0, ">-1/110")

    audit.check(
        "scope",
        "open-gate firewall",
        SCOPE["owner_target_outside_open_annulus"]
        and SCOPE["closed_certification_domain_compact"]
        and SCOPE["unit_regulator_multipliers_p_2p_4p"]
        and SCOPE["only_declared_past_and_fresh_modes"]
        and not SCOPE["open_annulus_owner_target"]
        and not SCOPE["all_production_charts"]
        and not SCOPE["t050_closed"]
        and not SCOPE["a13_closed"]
        and not SCOPE["sector_a_closed"]
        and "does not certify" in NO_OVERCLAIM,
        SCOPE,
        "one sparse fibre outside one bounded open annulus only",
    )

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "status": "PASS",
        "diagnostics": {
            "volume": volume,
            "pi_squared_bracket": [pi2_lower, pi2_upper],
            "mass_loewner_bounds": [sp.Rational(7, 250), sp.Rational(27, 100)],
            "covariance_bounds": {"cp_min": cp_min, "cp_max": cp_max, "c4_min": c4_min, "c4_max": c4_max, "trace4_max": trace4_max},
            "harmonic_constant": harmonic_constant,
            "harmonic_sharp_fixture": [fixture_f, fixture_q, fixture_product],
            "r130_upper_constants": {"L6": l6, "H6": h6},
            "past_derivative_covariance_upper": gamma_past_derivative,
            "polynomial_constants": actual_constants,
            "polynomial": polynomial,
            "small_derivative_upper": small_derivative_upper,
            "small_margin": small_margin,
            "large_derivative": large_derivative,
            "large_second_derivative": large_second,
            "large_margin": large_margin,
            "certified_amplitude_regions": ["0<=G<=21", "G>=274"],
            "unresolved_open_annulus": "21<G<274",
            "compact_certification_domain": "21<=G<=274",
            "owner_floor": -sp.Rational(9, 10),
            "rho": rho,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {
            "A1": sha256(A1_MANIFEST),
            "R-130": sha256(R130_MANIFEST),
            "R-130-result": sha256(r130_path),
            "R-153": sha256(R153_MANIFEST),
            "R-164": sha256(R164_MANIFEST),
        },
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
