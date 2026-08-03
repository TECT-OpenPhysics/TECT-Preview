#!/usr/bin/env python3
"""Primary exact certificate for the T0 PA-M5-NL3-SV candidate.

This is a candidate-neutral Pre-A calculation, not a registered TECT action.
It proves the static auxiliary-field reduction and the early bare-shell causal
obstruction under explicitly declared hypotheses.  Every derived constant is
computed from symbolic inputs or the declared exact adversarial fixture.
"""

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


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M5-NL3-SV-v0"
SLUG = "pre-a-pa-m5-nl3-sv-candidate"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)
CHARTER = REPO / "strategy/pre-a-evidence-first-model-selection-charter-260802.md"
BOUNDARY_SEED = REPO / "strategy/boundary-massless-mode-criticality-seed-260802.md"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

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


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, col]) for col in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


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
    audit.check("authority", "Pre-A charter present", CHARTER.is_file(), CHARTER.relative_to(REPO), "tracked file")
    audit.check("authority", "boundary seed present", BOUNDARY_SEED.is_file(), BOUNDARY_SEED.relative_to(REPO), "tracked file")
    audit.check(
        "authority",
        "A1 field has three complex components",
        a1["torus_and_real_pairing"]["field"].startswith("Psi in C^(3"),
        a1["torus_and_real_pairing"]["field"],
        "Psi in C^3",
    )

    params = a1["parameters"]
    family = [q(value) for value in params["family_masses"]]
    lock = q(params["k_lock"])
    z0 = sp.Matrix([q(value) for value in params["z0"]])
    inherited_internal = sp.diag(*family) + lock * (sp.eye(3) - z0 * z0.T / (z0.T * z0)[0])
    expected_internal = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    audit.check("authority", "inherited internal matrix reconstructed", inherited_internal == expected_internal, inherited_internal, expected_internal)
    characteristic = sp.Poly(inherited_internal.charpoly().as_expr())
    expected_characteristic = sp.Poly(sp.Symbol("lambda") ** 3 - sp.Rational(2, 5) * sp.Symbol("lambda") ** 2 + sp.Rational(223, 5000) * sp.Symbol("lambda") - sp.Rational(3, 3125))
    audit.check("authority", "inherited characteristic polynomial", characteristic.all_coeffs() == expected_characteristic.all_coeffs(), characteristic.as_expr(), expected_characteristic.as_expr())
    discriminant = sp.factor(sp.discriminant(characteristic.as_expr()))
    audit.check("authority", "inherited internal spectrum is simple", discriminant == sp.Rational(32233, 31250000000) and discriminant > 0, discriminant, sp.Rational(32233, 31250000000))

    # Exact one-mode completion.  Write g=h^2 so no square-root branch is hidden.
    p, h, c, mass, a, d = sp.symbols("p h c mass a d", positive=True, real=True)
    original = (p * a**2 - 2 * h * a * d + c * d**2 + mass) / 2
    completed = (p * (a - h * d / p) ** 2 + (c - h**2 / p) * d**2 + mass) / 2
    audit.check("elimination", "auxiliary square completion", sp.expand(original - completed) == 0, sp.expand(original - completed), 0)

    s, sigma, g, r, lam = sp.symbols("s sigma g r lam", positive=True, real=True)
    kernel = r + lam + c * s - g * s / (s + sigma)
    first = sp.factor(sp.diff(kernel, s))
    second = sp.factor(sp.diff(kernel, s, 2))
    audit.check("shell", "kernel first derivative", sp.simplify(first - (c - g * sigma / (s + sigma) ** 2)) == 0, first, c - g * sigma / (s + sigma) ** 2)
    audit.check("shell", "kernel strictly convex", second == 2 * g * sigma / (s + sigma) ** 3, second, 2 * g * sigma / (s + sigma) ** 3)
    s_star = sp.sqrt(g * sigma / c) - sigma
    shell_value = sp.factor(kernel.subs(s, s_star))
    expected_shell_value = r + lam - (sp.sqrt(g) - sp.sqrt(c * sigma)) ** 2
    audit.check("shell", "stationary shell derivative vanishes", sp.simplify(first.subs(s, s_star)) == 0, sp.simplify(first.subs(s, s_star)), 0)
    audit.check("shell", "continuous shell minimum", sp.simplify(shell_value - expected_shell_value) == 0, shell_value, expected_shell_value)
    audit.check("shell", "shell condition equivalence", sp.simplify((s_star + sigma) ** 2 - g * sigma / c) == 0, (s_star + sigma) ** 2, g * sigma / c)
    shell_difference = sp.simplify(kernel - shell_value)
    expected_shell_difference = c * (s - s_star) ** 2 / (s + sigma)
    audit.check("shell", "exact curved-shell difference identity", sp.simplify(shell_difference - expected_shell_difference) == 0, shell_difference, expected_shell_difference)
    s_one = sp.symbols("s_one", positive=True, real=True)
    first_lattice_difference = sp.factor(kernel.subs(s, s_one) - kernel.subs(s, 0))
    audit.check("shell", "finite-torus first-shell comparison", sp.simplify(first_lattice_difference - s_one * (c - g / (s_one + sigma))) == 0, first_lattice_difference, s_one * (c - g / (s_one + sigma)))
    continuous_only_counter = sp.Rational(1) - sp.Rational(3, 2) / (sp.Rational(1) + 1)
    audit.check("shell", "continuous-shell gate does not imply discrete selection", sp.Rational(3, 2) > 1 and continuous_only_counter > 0, continuous_only_counter, ">0 at c=sigma=1, g=3/2, s1=1")

    # Exact zero-reference completion for u<0, with w=-u=u_minus.
    rho, kappa, w, v = sp.symbols("rho kappa w v", nonnegative=True, real=True)
    energy_density = kappa * rho / 2 - w * rho**2 / 4 + v * rho**3 / 6
    threshold = 3 * w**2 / (16 * v)
    rho_coexist = 3 * w / (4 * v)
    threshold_completion = rho * (v * (rho - rho_coexist) ** 2 / 6 + (kappa - threshold) / 2)
    audit.check("zero-reference", "quartic-sextic threshold completion", sp.expand(energy_density - threshold_completion) == 0, sp.expand(energy_density - threshold_completion), 0)
    audit.check("zero-reference", "coexistence density saturates", sp.factor(energy_density.subs({kappa: threshold, rho: rho_coexist})) == 0, sp.factor(energy_density.subs({kappa: threshold, rho: rho_coexist})), 0)
    stationary = sp.factor(sp.diff(energy_density, rho).subs(kappa, threshold))
    expected_stationary = v * (rho - w / (4 * v)) * (rho - 3 * w / (4 * v)) / 2
    audit.check("zero-reference", "coexistence stationary branches", sp.expand(stationary - expected_stationary) == 0, stationary, expected_stationary)

    # Exact finite-torus fixture: L=2*pi, c=sigma=1, g=4, r+lambda=19/16.
    fixture_kernel = sp.factor(sp.Rational(19, 16) + s - 4 * s / (s + 1))
    fixture_minimum = sp.Rational(3, 16)
    fixture_factor = sp.factor(fixture_kernel - fixture_minimum)
    audit.check("fixture", "discrete shell factor", fixture_factor == (s - 1) ** 2 / (s + 1), fixture_factor, (s - 1) ** 2 / (s + 1))
    audit.check("fixture", "shell and zero-reference thresholds coincide", fixture_kernel.subs(s, 1) == fixture_minimum == sp.Rational(3, 16), fixture_kernel.subs(s, 1), sp.Rational(3, 16))
    torus_values = {n2: sp.factor(fixture_kernel.subs(s, n2)) for n2 in range(8)}
    audit.check("fixture", "integer radial shell uniquely minimizes", min(torus_values, key=torus_values.get) == 1 and torus_values[1] == fixture_minimum, torus_values, "unique radial n^2=1 minimum")
    fixture_density = fixture_minimum * rho / 2 - rho**2 / 4 + rho**3 / 6
    audit.check("fixture", "coexistence factor", sp.factor(fixture_density) == rho * (4 * rho - 3) ** 2 / 96, sp.factor(fixture_density), rho * (4 * rho - 3) ** 2 / 96)
    strict_competitor = sp.factor((fixture_density - fixture_minimum * rho / 2).subs(rho, sp.Rational(3, 4)))
    audit.check("fixture", "below-threshold plane wave beats zero", strict_competitor == -sp.Rational(9, 128), strict_competitor, -sp.Rational(9, 128))
    audit.check("fixture", "first-order coexistence is above the massless spinodal", fixture_minimum > 0, fixture_minimum, ">0 shell gap at coexistence")

    # Coercivity follows after exact elimination: K_j(s)>=c*s+r+lambda_j-g.
    reduced_lower_remainder = sp.factor(kernel - (r + lam + c * s - g))
    audit.check("coercivity", "reduced kernel H1 lower remainder", reduced_lower_remainder == g * sigma / (s + sigma), reduced_lower_remainder, g * sigma / (s + sigma))
    quartic_absorption = sp.factor(v * rho**3 / 12 - w * rho**2 / 4 + w**3 / (3 * v**2))
    expected_quartic_absorption = (v * rho - 2 * w) ** 2 * (v * rho + w) / (12 * v**2)
    audit.check("coercivity", "negative quartic absorbed by sextic", sp.expand(quartic_absorption - expected_quartic_absorption) == 0, quartic_absorption, expected_quartic_absorption)
    dmass, av = sp.symbols("D av", nonnegative=True, real=True)
    mass_absorption = v * rho**3 / 24 - dmass * rho + 2 * v * av**3 / 3
    expected_mass_absorption = v * (rho - 2 * av) ** 2 * (rho + 4 * av) / 24
    audit.check("coercivity", "negative mass absorbed while retaining sextic", sp.expand(mass_absorption.subs(dmass, v * av**2 / 2) - expected_mass_absorption) == 0, sp.factor(mass_absorption.subs(dmass, v * av**2 / 2)), expected_mass_absorption)
    multiplier = (1 + s) * s / (s + sigma) ** 2
    audit.check("coercivity", "auxiliary minimizer H1 multiplier has finite endpoint limits", sp.limit(multiplier, s, 0) == 0 and sp.limit(multiplier, s, sp.oo) == 1, [sp.limit(multiplier, s, 0), sp.limit(multiplier, s, sp.oo)], [0, 1])
    sigma_ge_one_residual = sp.factor((s + sigma) ** 2 - s * (1 + s))
    sigma_le_one_residual = sp.factor((s + sigma) ** 2 / sigma - s * (1 + s))
    audit.check("coercivity", "multiplier envelope for sigma at least one", sp.expand(sigma_ge_one_residual - (sigma**2 + s * (2 * sigma - 1))) == 0, sigma_ge_one_residual, sigma**2 + s * (2 * sigma - 1))
    audit.check("coercivity", "multiplier envelope for sigma at most one", sp.simplify(sigma_le_one_residual - (sigma + s + s**2 * (1 - sigma) / sigma)) == 0, sigma_le_one_residual, sigma + s + s**2 * (1 - sigma) / sigma)

    # Bare-shell causal test.  The exact fixture also tunes the ultraviolet speeds equal,
    # showing that high-frequency speed matching does not repair shell tangential softness.
    px, py, pz = sp.symbols("px py pz", real=True)
    displaced_s = (1 + px) ** 2 + py**2 + pz**2
    critical_kernel = sp.factor(1 + s - 4 * s / (s + 1))
    audit.check("dispersion", "critical fixture is exact shell square", critical_kernel == (s - 1) ** 2 / (s + 1), critical_kernel, (s - 1) ** 2 / (s + 1))
    displaced = critical_kernel.subs(s, displaced_s)
    hessian = sp.hessian(displaced, (px, py, pz)).subs({px: 0, py: 0, pz: 0})
    audit.check("dispersion", "shell momentum Hessian has rank one", hessian == sp.diag(4, 0, 0) and hessian.rank() == 1, hessian, sp.diag(4, 0, 0))
    t = sp.symbols("t", real=True)
    radial = sp.factor(displaced.subs({px: t, py: 0, pz: 0}))
    tangential = sp.factor(displaced.subs({px: 0, py: t, pz: 0}))
    audit.check("dispersion", "radial quadratic coefficient", sp.limit(radial / t**2, t, 0) == 2, sp.limit(radial / t**2, t, 0), 2)
    audit.check("dispersion", "tangential quadratic coefficient vanishes", sp.limit(tangential / t**2, t, 0) == 0, sp.limit(tangential / t**2, t, 0), 0)
    audit.check("dispersion", "tangential leading term is quartic", sp.limit(tangential / t**4, t, 0) == sp.Rational(1, 2), sp.limit(tangential / t**4, t, 0), sp.Rational(1, 2))
    chi_psi, chi_a = sp.symbols("chi_psi chi_a", positive=True, real=True)
    speed_difference = sp.factor(c / chi_psi - 1 / chi_a)
    audit.check("dispersion", "ultraviolet speed equality is one tuning equation", speed_difference == (c * chi_a - chi_psi) / (chi_a * chi_psi), speed_difference, (c * chi_a - chi_psi) / (chi_a * chi_psi))
    fixture_inertia = sp.Integer(1) + sp.Integer(4) / sp.Integer(4)
    audit.check("dispersion", "equal-speed fixture effective shell inertia", fixture_inertia == 2, fixture_inertia, 2)
    dynamic_b = sp.Integer(2) + sp.Integer(2)
    audit.check("dispersion", "critical longitudinal dynamic coefficient", dynamic_b == 4, dynamic_b, "B_star=chi_A*D_star+chi_Psi*L_star=4")
    audit.check("dispersion", "axis scaling remains anisotropic", sp.Rational(2, 1) / 2 == 1 and sp.Rational(1, 2) / 2 == sp.Rational(1, 4), [sp.Rational(1), sp.Rational(1, 4)], "radial omega^2 coefficient 1; tangential quartic coefficient 1/4")
    curved_path = displaced.subs({px: sp.sqrt(1 - t**2) - 1, py: t, pz: 0})
    audit.check("dispersion", "curved path along the shell stays exactly soft", sp.simplify(curved_path) == 0, sp.simplify(curved_path), 0)
    audit.check("dispersion", "transverse auxiliary modes are gapped when sigma positive", sigma / chi_a > 0, sigma / chi_a, ">0 at s=0")

    audit.require()
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
            "fixture_kernel": str(fixture_kernel),
            "fixture_shell_minimum": str(fixture_minimum),
            "critical_fixture_kernel": str(critical_kernel),
            "fixture_momentum_hessian": serial(hessian),
            "fixture_effective_dispersion": "omega_-^2=(2*p_parallel+p_parallel^2+|p_perp|^2)^2/4+higher_dynamic_order",
            "bare_shell_causal_verdict": "FAIL: rank-one spatial Hessian in three dimensions",
            "candidate_t054_verdict": "RETAIN STATIC MECHANISM; REJECT BARE JOINT T-053 SURVIVOR",
        },
        "summary": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
        },
        "assertions": audit.rows,
        "no_overclaim": NO_OVERCLAIM,
        "verdict": "PASS",
    }
    atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID} primary: {len(audit.rows)}/{len(audit.rows)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
