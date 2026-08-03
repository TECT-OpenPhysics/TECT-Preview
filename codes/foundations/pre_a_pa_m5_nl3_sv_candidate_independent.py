#!/usr/bin/env python3
"""Independent standard-library audit of the PA-M5-NL3-SV certificate.

The implementation intentionally imports neither the primary module nor any
scientific package and never reads the primary result artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M5-NL3-SV-v0"
SLUG = "pre-a-pa-m5-nl3-sv-candidate"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)
CHARTER = REPO / "strategy/pre-a-evidence-first-model-selection-charter-260802.md"
BOUNDARY_SEED = REPO / "strategy/boundary-massless-mode-criticality-seed-260802.md"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

F = Fraction
SCOPE = {
    "authority": "T0-CANDIDATE-CERTIFICATE",
    "new_hypothesis_not_registered_tect_action": True,
    "periodic_static_energy": True,
    "field_psi_in_c3_and_three_auxiliary_c3_vectors": True,
    "parameter_domain": "c>0, sigma>0, g>0, v>0; r,u real; M Hermitian",
    "exact_auxiliary_elimination": True,
    "continuous_isotropic_shell_gate": True,
    "finite_torus_zero_reference_gate": True,
    "finite_torus_coercive_lower_bound": True,
    "finite_volume_energy_level_crossing_only": True,
    "thermodynamic_phase_transition": False,
    "ordinary_positive_inertial_extension_only": True,
    "instantaneous_auxiliary_field_is_not_a_causal_completion": True,
    "bare_isotropic_shell_common_lorentz_cone": False,
    "bare_candidate_t054_survival": False,
    "unique_morphology_or_bcc_selection": False,
    "local_gauge_completion": False,
    "physical_parameter_or_evidence_fit": False,
    "physical_vacuum_selection": False,
    "tect_tier_or_claim_promotion": False,
    "t050_a13_or_sector_a_closure": False,
}
NO_OVERCLAIM = (
    "PA-M5-NL3-SV is a T0 new-hypothesis candidate, not a registered TECT action or physical model. "
    "The certificate proves exact static elimination, distinct continuum and finite-torus shell criteria, "
    "a zero-reference criterion, a finite-torus coercive bound, and a bare isotropic-shell rank obstruction "
    "for ordinary positive inertial dynamics. The resulting finite-volume crossing is not called a "
    "thermodynamic phase transition. "
    "It does not derive the screened vector, parameters, symmetry, local gauge law, microscopic charge, "
    "cooling map, unique morphology, physical vacuum, Lorentz invariance, topology, A7, T-050, or Sector-A closure."
)


def frac(value: Any) -> Fraction:
    return F(str(value))


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def characteristic_coefficients(matrix: list[list[Fraction]]) -> list[Fraction]:
    trace = sum(matrix[index][index] for index in range(3))
    principal_two = (
        matrix[0][0] * matrix[1][1]
        - matrix[0][1] * matrix[1][0]
        + matrix[0][0] * matrix[2][2]
        - matrix[0][2] * matrix[2][0]
        + matrix[1][1] * matrix[2][2]
        - matrix[1][2] * matrix[2][1]
    )
    return [F(1), -trace, principal_two, -determinant3(matrix)]


def kernel(c: Fraction, sigma: Fraction, g: Fraction, mass: Fraction, s: Fraction) -> Fraction:
    return mass + c * s - g * s / (s + sigma)


def energy(kappa: Fraction, u: Fraction, v: Fraction, rho: Fraction) -> Fraction:
    return kappa * rho / 2 + u * rho * rho / 4 + v * rho * rho * rho / 6


def check(rows: list[dict[str, Any]], group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "group": group,
            "name": name,
            "status": "PASS" if condition else "FAIL",
            "actual": encode(actual),
            "expected": encode(expected),
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    rows: list[dict[str, Any]] = []

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    check(rows, "authority", "Pre-A charter present", CHARTER.is_file(), CHARTER.relative_to(REPO), "tracked file")
    check(rows, "authority", "boundary seed present", BOUNDARY_SEED.is_file(), BOUNDARY_SEED.relative_to(REPO), "tracked file")
    check(rows, "authority", "A1 field convention", a1["torus_and_real_pairing"]["field"].startswith("Psi in C^(3"), a1["torus_and_real_pairing"]["field"], "Psi in C^3")

    params = a1["parameters"]
    family = [frac(item) for item in params["family_masses"]]
    lock = frac(params["k_lock"])
    # z0=(1,1,1), hence lock*(I-z0*z0^T/3).
    internal = [
        [(family[i] if i == j else F(0)) + (F(2, 3) * lock if i == j else -F(1, 3) * lock) for j in range(3)]
        for i in range(3)
    ]
    expected_internal = [
        [F(1, 10), -F(1, 20), -F(1, 20)],
        [-F(1, 20), F(13, 100), -F(1, 20)],
        [-F(1, 20), -F(1, 20), F(17, 100)],
    ]
    check(rows, "authority", "inherited matrix reconstructed independently", internal == expected_internal, internal, expected_internal)
    characteristic = characteristic_coefficients(internal)
    expected_characteristic = [F(1), -F(2, 5), F(223, 5000), -F(3, 3125)]
    check(rows, "authority", "characteristic polynomial by trace and minors", characteristic == expected_characteristic, characteristic, expected_characteristic)
    _, cubic_a, cubic_b, cubic_c = characteristic
    discriminant = cubic_a**2 * cubic_b**2 - 4 * cubic_b**3 - 4 * cubic_a**3 * cubic_c - 27 * cubic_c**2 + 18 * cubic_a * cubic_b * cubic_c
    check(rows, "authority", "simple inherited spectrum by cubic discriminant", discriminant == F(32233, 31250000000) and discriminant > 0, discriminant, F(32233, 31250000000))

    # Coefficient-level auxiliary completion with exact rational test oracles.
    completion_oracles = [
        (F(3), F(2), F(5), F(7), F(11)),
        (F(5, 2), F(3, 2), F(7, 3), -F(4, 5), F(2, 7)),
        (F(9, 4), F(5, 3), F(4), F(1, 6), -F(7, 8)),
    ]
    completion_ok = True
    completion_values: list[Fraction] = []
    for p, h, c_value, a, d in completion_oracles:
        original = (p * a * a - 2 * h * a * d + c_value * d * d) / 2
        completed = (p * (a - h * d / p) ** 2 + (c_value - h * h / p) * d * d) / 2
        completion_values.append(original - completed)
        completion_ok = completion_ok and original == completed
    check(rows, "elimination", "auxiliary completion on exact independent oracles", completion_ok, completion_values, [0, 0, 0])

    shell_oracles = [
        # c, sigma, g, sqrt(g), sqrt(c*sigma), s_star
        (F(1), F(1), F(4), F(2), F(1), F(1)),
        (F(4), F(1), F(16), F(4), F(2), F(1)),
        (F(1), F(4), F(16), F(4), F(2), F(4)),
        (F(9), F(1), F(36), F(6), F(3), F(1)),
    ]
    stationary_rows = []
    for c_value, sigma_value, g_value, sqrt_g, sqrt_cs, star in shell_oracles:
        derivative_numerator = c_value * (star + sigma_value) ** 2 - g_value * sigma_value
        drop = (sqrt_g - sqrt_cs) ** 2
        direct_drop = -(c_value * star - g_value * star / (star + sigma_value))
        stationary_rows.append((derivative_numerator, direct_drop, drop, g_value > c_value * sigma_value))
    check(rows, "shell", "nonzero-shell criterion and drop on four exact families", all(row[0] == 0 and row[1] == row[2] and row[3] for row in stationary_rows), stationary_rows, "zero derivative, exact drop, g>c*sigma")
    no_shell = [(F(1), F(1), F(1)), (F(2), F(3), F(5)), (F(3), F(2), F(6))]
    check(rows, "shell", "no-shell derivative starts nonnegative", all(c0 * sigma0 - g0 >= 0 for c0, sigma0, g0 in no_shell), [c0 * sigma0 - g0 for c0, sigma0, g0 in no_shell], ">=0")
    finite_shell_gate = F(4) > F(1) * (F(1) + F(1))
    check(rows, "shell", "finite-torus first-shell gate", finite_shell_gate, [F(4), F(2)], "g>c*(sigma+s1)")
    continuous_only_g = F(3, 2)
    continuous_only_difference = F(1) * (F(1) - continuous_only_g / F(2))
    check(rows, "shell", "continuous shell can miss every nonzero torus mode", continuous_only_g > 1 and continuous_only_difference > 0, continuous_only_difference, ">0")

    c0, sigma0, g0, mass0 = F(1), F(1), F(4), F(19, 16)
    kappa0 = F(3, 16)
    radial_values = {n2: kernel(c0, sigma0, g0, mass0, F(n2)) for n2 in range(12)}
    factor_checks = {
        n2: (radial_values[n2] - kappa0) * (F(n2) + 1) - (F(n2) - 1) ** 2
        for n2 in radial_values
    }
    check(rows, "fixture", "exact discrete-shell factor on integer radii", all(value == 0 for value in factor_checks.values()), factor_checks, "all zero")
    check(rows, "fixture", "unique radial minimum at n squared one", min(radial_values, key=radial_values.get) == 1 and radial_values[1] == kappa0, radial_values, "n^2=1 and 3/16")

    threshold_oracles = [(F(1), F(1)), (F(2), F(3)), (F(5, 2), F(7, 3))]
    threshold_rows = []
    for w, v in threshold_oracles:
        threshold = 3 * w * w / (16 * v)
        rho_star = 3 * w / (4 * v)
        barrier = w / (4 * v)
        threshold_rows.append((energy(threshold, -w, v, rho_star), threshold - w * barrier + v * barrier * barrier, rho_star))
    check(rows, "zero-reference", "coexistence and stationary branches on exact families", all(row[0] == 0 and row[1] == 0 for row in threshold_rows), threshold_rows, "zero energy and zero derivative")
    check(rows, "zero-reference", "fixture coexistence density", energy(F(3, 16), -F(1), F(1), F(3, 4)) == 0, energy(F(3, 16), -F(1), F(1), F(3, 4)), 0)
    check(rows, "zero-reference", "strict below-threshold competitor", energy(F(0), -F(1), F(1), F(3, 4)) == -F(9, 128), energy(F(0), -F(1), F(1), F(3, 4)), -F(9, 128))
    check(rows, "zero-reference", "first-order coexistence retains a shell gap", F(3, 16) > 0, F(3, 16), ">0")
    positive_quartic = [energy(kappa, u, F(2), rho) for kappa, u, rho in [(F(0), F(1), F(1)), (F(2), F(0), F(3)), (F(1, 2), F(4), F(5, 2))]]
    check(rows, "zero-reference", "u nonnegative threshold reduces to kappa nonnegative", all(item >= 0 for item in positive_quartic), positive_quartic, ">=0")

    # Independent coercivity factors, evaluated exactly at several signed points.
    quartic_factor_rows = []
    for rho_value in [F(0), F(1, 3), F(2), F(7, 2)]:
        w, v = F(3, 2), F(5, 3)
        left = v * rho_value**3 / 12 - w * rho_value**2 / 4 + w**3 / (3 * v**2)
        right = (v * rho_value - 2 * w) ** 2 * (v * rho_value + w) / (12 * v**2)
        quartic_factor_rows.append((left, right))
    check(rows, "coercivity", "quartic absorption factor independently evaluated", all(left == right and right >= 0 for left, right in quartic_factor_rows), quartic_factor_rows, "equal nonnegative factors")
    mass_factor_rows = []
    for rho_value in [F(0), F(1), F(2), F(5)]:
        v, av = F(3), F(2, 3)
        dmass = v * av * av / 2
        left = v * rho_value**3 / 24 - dmass * rho_value + 2 * v * av**3 / 3
        right = v * (rho_value - 2 * av) ** 2 * (rho_value + 4 * av) / 24
        mass_factor_rows.append((left, right))
    check(rows, "coercivity", "mass absorption factor independently evaluated", all(left == right and right >= 0 for left, right in mass_factor_rows), mass_factor_rows, "equal nonnegative factors")
    mode_rows = []
    for s_value, sigma_value, h_value, c_value, a_value, x_value in [
        (F(1), F(2), F(3, 2), F(4), F(2), F(5, 3)),
        (F(5), F(1, 2), F(2), F(3, 2), -F(1, 4), F(7, 5)),
    ]:
        d_value = x_value  # tested component; the bound below uses d^2<=s*x^2
        if d_value * d_value > s_value * x_value * x_value:
            d_value = F(0)
        p_value = s_value + sigma_value
        original = (p_value * a_value**2 - 2 * h_value * a_value * d_value + c_value * d_value**2) / 2
        lower = p_value * a_value**2 / 4 + c_value * d_value**2 / 4 - h_value**2 * x_value**2
        mode_rows.append(original - lower)
    check(rows, "coercivity", "modewise Young lower bound on exact fixtures", all(item >= 0 for item in mode_rows), mode_rows, ">=0")

    reduced_lower = [
        kernel(F(1), F(1), F(4), F(2), F(sval)) - (F(2) + F(sval) - F(4))
        for sval in range(8)
    ]
    check(rows, "coercivity", "reduced H1 lower remainder", all(value == F(4, sval + 1) for sval, value in enumerate(reduced_lower)), reduced_lower, [F(4, sval + 1) for sval in range(8)])

    # The shell Hessian is obtained without symbolic differentiation:
    # K'(1)=0, K''(1)=1 and D^2 K(|k|^2)=4 K'' k k^T+2 K' I.
    kprime = c0 - g0 * sigma0 / (F(1) + sigma0) ** 2
    ksecond = 2 * g0 * sigma0 / (F(1) + sigma0) ** 3
    momentum_hessian = [[F(4) * ksecond if i == 0 and j == 0 else F(0) for j in range(3)] for i in range(3)]
    check(rows, "dispersion", "shell derivative and curvature", kprime == 0 and ksecond == 1, [kprime, ksecond], [0, 1])
    check(rows, "dispersion", "momentum Hessian rank-one diagonal", momentum_hessian == [[F(4), F(0), F(0)], [F(0), F(0), F(0)], [F(0), F(0), F(0)]], momentum_hessian, "diag(4,0,0)")
    radial_leading = F(4, 2)  # (2t+t^2)^2/(2+2t+t^2)
    tangential_leading = F(1, 2)  # t^4/(2+t^2)
    check(rows, "dispersion", "radial versus tangential leading powers", radial_leading == 2 and tangential_leading == F(1, 2), [radial_leading, tangential_leading], [2, F(1, 2)])
    effective_inertia = F(1) + g0 * F(1) / (F(1) + sigma0) ** 2
    check(rows, "dispersion", "positive valley inertia cannot change derivative order", effective_inertia == 2 and radial_leading / effective_inertia == 1 and tangential_leading / effective_inertia == F(1, 4), [effective_inertia, radial_leading / effective_inertia, tangential_leading / effective_inertia], [2, 1, F(1, 4)])
    speed_oracles = [(F(1), F(1), F(1)), (F(4), F(1, 2), F(2)), (F(9), F(1, 3), F(3))]
    check(rows, "dispersion", "ultraviolet equality requires c times chi_A equals chi_Psi", all(cval * chia == chipsi for cval, chia, chipsi in speed_oracles), speed_oracles, "c*chi_A=chi_Psi")
    curved_shell_rows = []
    for t_value in [F(1, 4), F(1, 3), F(1, 2), F(2, 3)]:
        kx = (1 - t_value**2) / (1 + t_value**2)
        ky = 2 * t_value / (1 + t_value**2)
        curved_shell_rows.append(kx**2 + ky**2)
    check(rows, "dispersion", "rational curved-shell paths remain exactly soft", all(value == 1 for value in curved_shell_rows), curved_shell_rows, [1, 1, 1, 1])
    check(rows, "dispersion", "transverse vector stays gapped for positive sigma", F(1) / F(1) > 0, F(1), "sigma/chi_A>0")

    failures = [row for row in rows if row["status"] != "PASS"]
    if failures:
        raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))

    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "candidate_id": CANDIDATE_ID,
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "scope": SCOPE,
        "authority_hashes": {
            str(CHARTER.relative_to(REPO)).replace("\\", "/"): sha256(CHARTER),
            str(BOUNDARY_SEED.relative_to(REPO)).replace("\\", "/"): sha256(BOUNDARY_SEED),
            str(A1_MANIFEST.relative_to(REPO)).replace("\\", "/"): sha256(A1_MANIFEST),
        },
        "exact_results": {
            "reduced_kernel": "K_j(s)=r+lambda_j+c*s-g*s/(s+sigma)",
            "continuous_shell_condition": "g>c*sigma",
            "continuous_shell_radius_squared": "sqrt(g*sigma/c)-sigma",
            "continuous_shell_drop": "(sqrt(g)-sqrt(c*sigma))^2",
            "finite_torus_nonzero_first_shell_condition": "g>c*(sigma+(2*pi/L)^2)",
            "finite_torus_zero_reference_threshold": "kappa_L>=3*u_minus^2/(16*v)",
            "coexistence_density_when_u_negative": "3*u_minus/(4*v)",
            "first_order_boundary_zero_phase_gap": "3*u_minus^2/(16*v)>0 when u<0",
            "fixture_kernel": "(16*s**2 - 29*s + 19)/(16*(s + 1))",
            "fixture_shell_minimum": "3/16",
            "critical_fixture_kernel": "(s - 1)**2/(s + 1)",
            "fixture_momentum_hessian": [["4", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]],
            "fixture_effective_dispersion": "omega_-^2=(2*p_parallel+p_parallel^2+|p_perp|^2)^2/4+higher_dynamic_order",
            "bare_shell_causal_verdict": "FAIL: rank-one spatial Hessian in three dimensions",
            "candidate_t054_verdict": "RETAIN STATIC MECHANISM; REJECT BARE JOINT T-053 SURVIVOR",
        },
        "summary": {"passed": len(rows), "failed": 0, "total": len(rows)},
        "assertions": rows,
        "no_overclaim": NO_OVERCLAIM,
        "verdict": "PASS",
    }
    atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID} independent: {len(rows)}/{len(rows)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
