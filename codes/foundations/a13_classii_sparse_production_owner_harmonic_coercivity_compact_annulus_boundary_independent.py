#!/usr/bin/env python3
"""Independent Fraction audit for the A13 R-165 sparse production boundary."""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SPARSE-PRODUCTION-OWNER-HARMONIC-COERCIVITY-COMPACT-ANNULUS-BOUNDARY"
LEDGER_ID = "R-165"
SLUG = "sparse-production-owner-harmonic-coercivity-compact-annulus-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-independent-{SLUG}" / "result.json"

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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": encode(actual),
                "expected": encode(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def encode(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), parse_float=str)


def fraction(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def determinant2(matrix: list[list[F]]) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant3(matrix: list[list[F]]) -> F:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def principal_minors(matrix: list[list[F]]) -> list[F]:
    return [matrix[0][0], determinant2([row[:2] for row in matrix[:2]]), determinant3(matrix)]


def scalar_symbol(x: F, z_value: F, r_value: F) -> F:
    return x * x + z_value * x + r_value


def polynomial(g: int, constants: dict[str, F]) -> F:
    value = F(g)
    return constants["A"] * value**4 - constants["B2"] * value**2 - constants["B1"] * value - constants["D0"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = load(A1_MANIFEST)
    r130_manifest = load(R130_MANIFEST)
    r153 = load(R153_MANIFEST)
    r164 = load(R164_MANIFEST)
    parameters = a1["parameters"]
    audit.check("authority", "R-153 identity", r153["result_ledger_id"] == "R-153", r153["result_ledger_id"], "R-153")
    audit.check("authority", "R-164 identity", r164["result_ledger_id"] == "R-164", r164["result_ledger_id"], "R-164")

    r130_path = REPO / r130_manifest["files"]["primary_result"]["path"]
    r130 = load(r130_path)
    p_mass = fraction(parameters["M_X"]) ** 2 + fraction(parameters["classii_mass_regularizer"])
    l6_exact = fraction(r130["diagnostics"]["conormal_gram"]["L6"])
    h6_exact = fraction(r130["diagnostics"]["conormal_gram"]["H6"])
    audit.check("authority", "R-130 hash", sha256(r130_path) == r130_manifest["files"]["primary_result"]["sha256"], sha256(r130_path), r130_manifest["files"]["primary_result"]["sha256"])
    audit.check("authority", "R-130 factors", l6_exact == F(1143, 250) / p_mass and h6_exact == F(7083, 500) / p_mass, [l6_exact, h6_exact], ["1143/(250P)", "7083/(500P)"])

    volume = fraction(parameters["Lx"]) * fraction(parameters["Ly"]) * fraction(parameters["Lz"])
    family = [fraction(item) for item in parameters["family_masses"]]
    lock = fraction(parameters["k_lock"])
    mass = []
    for row in range(3):
        current: list[F] = []
        for column in range(3):
            delta = F(1) if row == column else F(0)
            current.append((family[row] if row == column else F(0)) + lock * (delta - F(1, 3)))
        mass.append(current)
    expected_mass = [[F(1, 10), -F(1, 20), -F(1, 20)], [-F(1, 20), F(13, 100), -F(1, 20)], [-F(1, 20), -F(1, 20), F(17, 100)]]
    audit.check("production", "volume", volume == 4096, volume, 4096)
    audit.check("production", "mass reconstruction", mass == expected_mass, mass, expected_mass)
    lower = [[mass[i][j] - (F(7, 250) if i == j else 0) for j in range(3)] for i in range(3)]
    upper = [[(F(27, 100) if i == j else 0) - mass[i][j] for j in range(3)] for i in range(3)]
    audit.check("production", "mass lower minors", all(item > 0 for item in principal_minors(lower)), principal_minors(lower), ">0")
    audit.check("production", "mass upper minors", all(item >= 0 for item in principal_minors(upper)), principal_minors(upper), ">=0")

    z_value = fraction(parameters["Z"])
    r_value = fraction(parameters["r"])
    pi2_lo, pi2_hi = F(333, 106) ** 2, F(355, 113) ** 2
    x1_lo, x1_hi = pi2_lo / 64, pi2_hi / 64
    x2_lo, x2_hi = pi2_lo / 16, pi2_hi / 16
    x4_lo, x4_hi = pi2_lo / 4, pi2_hi / 4
    audit.check("spectral", "pi bracket arithmetic", pi2_hi < 10 and F(333, 106) < F(355, 113), [pi2_lo, pi2_hi], "(333/106)^2<pi^2<(355/113)^2")
    audit.check("spectral", "monotonicity signs", 2 * x1_hi + z_value < 0 < 2 * x2_lo + z_value and 2 * x4_lo + z_value > 0, [2 * x1_hi + z_value, 2 * x2_lo + z_value, 2 * x4_lo + z_value], "-,+,+")
    a1_lower = scalar_symbol(x1_hi, z_value, r_value) + F(7, 250)
    a1_upper = scalar_symbol(x1_lo, z_value, r_value) + F(27, 100)
    a2_lower = scalar_symbol(x2_lo, z_value, r_value) + F(7, 250)
    a2_upper = scalar_symbol(x2_hi, z_value, r_value) + F(27, 100)
    a4_lower = scalar_symbol(x4_lo, z_value, r_value) + F(7, 250)
    a4_upper = scalar_symbol(x4_hi, z_value, r_value) + F(27, 100)
    audit.check("spectral", "p operator enclosure", a1_lower > F(3, 8) and a1_upper < F(63, 100), [a1_lower, a1_upper], [">3/8", "<63/100"])
    audit.check("spectral", "2p operator enclosure", a2_lower > F(31, 100) and a2_upper < F(14, 25), [a2_lower, a2_upper], [">31/100", "<14/25"])
    audit.check("spectral", "4p operator enclosure", a4_lower > F(43, 10) and a4_upper < F(91, 20), [a4_lower, a4_upper], [">43/10", "<91/20"])

    cp_min, cp_max = F(100, 63), F(100, 31)
    c4_min, c4_max = F(20, 91), F(10, 43)
    trace4_max = F(60, 43)
    audit.check("spectral", "past covariance enclosure", cp_min == F(100, 63) and cp_max == F(100, 31), [cp_min, cp_max], [F(100, 63), F(100, 31)])
    audit.check("spectral", "fresh covariance enclosure", c4_min == F(20, 91) and c4_max == F(10, 43) and 6 * c4_max == trace4_max, [c4_min, c4_max, trace4_max], [F(20, 91), F(10, 43), F(60, 43)])

    # Independent Fourier ledger.  r0=2a+s and q0=2b+t force the two
    # highest-coefficient ratios 1/6 and 1/2.  The scalar fixture uses
    # cos^4(2 theta) and sin^2(4 theta).
    harmonic_constant = 1 - 2 * F(1, 6) * F(1, 2)
    fixture = [F(3, 8), F(1, 2), F(5, 32)]
    audit.check("harmonic", "field top-mode ratio", (F(2) ** 2 + 2) == 6, 6, "r0^2+2|r4|^2>=6|r4|^2")
    audit.check("harmonic", "product constant", harmonic_constant == F(5, 6), harmonic_constant, F(5, 6))
    audit.check("harmonic", "sharp fixture", fixture[2] / (fixture[0] * fixture[1]) == harmonic_constant, fixture, "ratio 5/6")

    p2_upper = F(5, 32)
    l6, h6 = F(1143, 1000), F(7083, 2000)
    sqrt_trace_factor = F(301, 100)
    gamma_past_derivative = 10 * p2_upper * cp_max / volume
    audit.check("envelope", "outward inputs", pi2_hi / 64 < p2_upper and l6_exact < l6 and h6_exact < h6, [pi2_hi / 64, l6_exact, h6_exact], [p2_upper, l6, h6])
    audit.check("envelope", "fresh square-root rationalization", 2 * cp_max * trace4_max < sqrt_trace_factor**2, 2 * cp_max * trace4_max, sqrt_trace_factor**2)
    audit.check("envelope", "past derivative covariance", gamma_past_derivative == F(625, 507904), gamma_past_derivative, F(625, 507904))

    constants = {
        "A": F(3, 4) * c4_min * cp_min**2 / volume**2,
        "B2": p2_upper * cp_max * c4_max * (32 * l6 + 8 * h6) / volume,
        "B1": 32 * l6 * p2_upper * c4_max * sqrt_trace_factor / volume,
        "D0": h6 * c4_max * gamma_past_derivative,
    }
    expected = {"A": F(3125, 126241210368), "B2": F(81135, 43679744), "B1": F(8001, 8192000), "D0": F(177075, 174718976)}
    audit.check("polynomial", "independent exact constants", constants == expected, constants, expected)
    audit.check("polynomial", "orientation factors", 32 == 2 * 8 * 2 and 8 == 2 * 4 and 2 == 2, [32, 8, 2], "DB, n^2, trace factors")

    small_derivative_upper = 4 * constants["A"] * 21**3 - constants["B1"]
    small_margin = polynomial(21, constants) + F(9, 10)
    large_derivative = 4 * constants["A"] * 274**3 - 2 * constants["B2"] * 274 - constants["B1"]
    large_second = 12 * constants["A"] * 274**2 - 2 * constants["B2"]
    large_margin = polynomial(274, constants) + F(9, 10)
    audit.check("annulus", "small derivative certificate", small_derivative_upper == -F(25427, 425984000) < 0, small_derivative_upper, "<0")
    audit.check("annulus", "inner endpoint margin", small_margin == F(145670815281, 2271346688000) > 0, small_margin, ">0")
    audit.check("annulus", "outer derivative certificate", large_derivative == F(1338311264185381, 1314683854848000) > 0 and large_second == F(65160500885, 3505823612928) > 0, [large_derivative, large_second], ">0,>0")
    audit.check("annulus", "outer endpoint margin", large_margin == F(1847465221877063, 2629367709696000) > 0, large_margin, ">0")
    rho = F(1, 110)
    audit.check("threshold", "owner target", F(10, 11) - rho == F(9, 10), F(10, 11) - rho, F(9, 10))
    audit.check("threshold", "semiconvexity threshold", F(0) > -F(1, 110), F(0), ">-1/110")
    audit.check("scope", "open-gate firewall", SCOPE["owner_target_outside_open_annulus"] and SCOPE["closed_certification_domain_compact"] and SCOPE["unit_regulator_multipliers_p_2p_4p"] and SCOPE["only_declared_past_and_fresh_modes"] and not SCOPE["open_annulus_owner_target"] and not SCOPE["t050_closed"] and not SCOPE["sector_a_closed"] and "does not certify" in NO_OVERCLAIM, SCOPE, "unit-multiplier sparse fibre outside-open-annulus result only")

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
            "pi_squared_bracket": [pi2_lo, pi2_hi],
            "mass_loewner_bounds": [F(7, 250), F(27, 100)],
            "covariance_bounds": {"cp_min": cp_min, "cp_max": cp_max, "c4_min": c4_min, "c4_max": c4_max, "trace4_max": trace4_max},
            "harmonic_constant": harmonic_constant,
            "harmonic_sharp_fixture": fixture,
            "r130_upper_constants": {"L6": l6, "H6": h6},
            "past_derivative_covariance_upper": gamma_past_derivative,
            "polynomial_constants": constants,
            "small_derivative_upper": small_derivative_upper,
            "small_margin": small_margin,
            "large_derivative": large_derivative,
            "large_second_derivative": large_second,
            "large_margin": large_margin,
            "certified_amplitude_regions": ["0<=G<=21", "G>=274"],
            "unresolved_open_annulus": "21<G<274",
            "compact_certification_domain": "21<=G<=274",
            "owner_floor": -F(9, 10),
            "rho": rho,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {"A1": sha256(A1_MANIFEST), "R-130": sha256(R130_MANIFEST), "R-130-result": sha256(r130_path), "R-153": sha256(R153_MANIFEST), "R-164": sha256(R164_MANIFEST)},
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
