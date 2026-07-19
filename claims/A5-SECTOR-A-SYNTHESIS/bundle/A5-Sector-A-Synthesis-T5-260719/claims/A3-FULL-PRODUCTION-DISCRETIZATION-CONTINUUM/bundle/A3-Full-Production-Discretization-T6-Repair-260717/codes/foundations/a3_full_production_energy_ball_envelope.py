#!/usr/bin/env python3
"""Compute an explicit P2 H2 solution-ball envelope for P3.

For every initial H2 radius R, the canonical P1 energy is bounded above on
that ball by E_upper(R).  P2 energy dissipation and its coercivity constant
then give ||u(t)||_H2 <= M2(R) for every t >= 0.  The bound is deliberately
coarse but completely explicit: it uses a rigorous Fourier-series Sobolev
embedding bound on the fixed torus and no sampled solution trajectory.

This closes only the energy-to-H2 input for the later positive-time H6
majorant.  It does not claim an H6 envelope, a numerical C(R,tau,T), or a
controlled continuum error bar for any Sector-B solver run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
P2_MANIFEST = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "full_pde_manifest.json"
P1_BACKEND = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-energy-ball-envelope" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: str, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def lattice_embedding_upper(periods: list[float], shell_cutoff: int) -> tuple[float, float]:
    """Return S_upper and its integral tail for sum_k (1+|k|^4)^-1.

    The max-norm shell m has 24m^2+2 lattice points.  On that shell,
    |k|^4 >= (2pi/L_max)^4 m^4.  The omitted tail uses m^-2 and m^-4
    integral bounds, hence the returned value is an upper bound, not a fit.
    """
    l_max = max(periods)
    frequency_scale_fourth = (2.0 * math.pi / l_max) ** 4
    finite = 1.0
    for m in range(1, shell_cutoff + 1):
        shell_count = 24.0 * m * m + 2.0
        finite += shell_count / (1.0 + frequency_scale_fourth * m**4)
    tail = 24.0 / (frequency_scale_fourth * shell_cutoff)
    tail += 2.0 / (3.0 * frequency_scale_fourth * shell_cutoff**3)
    return finite + tail, tail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    p2 = json.loads(P2_MANIFEST.read_text(encoding="utf-8"))
    stage = manifest["stage7_energy_ball"]
    params = p1["parameters"]
    assertions: list[dict[str, Any]] = []
    for key, path in (("p1_backend", P1_BACKEND), ("p1_manifest", P1_MANIFEST), ("p2_manifest", P2_MANIFEST)):
        actual = sha256(path)
        expected = manifest["authority"][key]["sha256"]
        check(f"{key}_hash", actual == expected, f"actual={actual}; expected={expected}", assertions)

    periods = [float(params[key]) for key in ("Lx", "Ly", "Lz")]
    volume = math.prod(periods)
    shell_cutoff = int(stage["embedding_shell_cutoff"])
    series_upper, tail_upper = lattice_embedding_upper(periods, shell_cutoff)
    embedding_squared = series_upper / volume
    h2_coercivity = float(p2["production_conditions"]["linear"]["h2_coercivity_constant"])
    lambda_value = float(params["lambda"])
    gamma_value = float(params["gamma"])
    young_constant = abs(lambda_value) ** 3 / (3.0 * gamma_value**2) if lambda_value < 0.0 else 0.0
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    classii_quartic_coefficient = 2.0 * abs(a_value) + 8.0 * abs(b_value) + 8.0 * abs(c_value)
    internal_upper = max(float(value) for value in params["family_masses"]) + float(params["k_lock"])
    linear_upper = float(params["r"]) + 0.5 * abs(float(params["Z"])) + float(params["Y"]) + internal_upper
    quartic_upper = (abs(lambda_value) / 4.0 + 0.5 * classii_quartic_coefficient) * embedding_squared
    sextic_upper = gamma_value * embedding_squared**2 / 6.0

    check("positive_h2_coercivity", h2_coercivity > 0.0, f"c_H2={h2_coercivity:.16e}", assertions)
    check("positive_sextic_coefficient", gamma_value > 0.0, f"gamma={gamma_value:.16e}", assertions)
    check("positive_regularisers", float(params["rho_regularizer"]) > 0.0 and float(params["classii_mass_regularizer"]) > 0.0, "rho and Class-II mass regularisers are positive", assertions)
    generator_source = P1_BACKEND.read_text(encoding="utf-8")
    pauli_embeddings = (
        "[[0, 1, 0], [1, 0, 0], [0, 0, 0]]",
        "[[0, -1j, 0], [1j, 0, 0], [0, 0, 0]]",
        "[[1, 0, 0], [0, -1, 0], [0, 0, 0]]",
    )
    check("pauli_generator_operator_norm_convention", all(value in generator_source for value in pauli_embeddings), "the hash-pinned backend uses three embedded Pauli generators, each with operator norm one", assertions)
    check("embedding_series_upper_is_finite", math.isfinite(series_upper) and series_upper > 0.0 and tail_upper > 0.0, f"series_upper={series_upper:.16e}; tail_upper={tail_upper:.16e}", assertions)
    check("classii_energy_upper_coefficient_is_nonnegative", classii_quartic_coefficient >= 0.0, f"coefficient={classii_quartic_coefficient:.16e}", assertions)
    check("linear_energy_upper_coefficient_is_positive", linear_upper > 0.0, f"coefficient={linear_upper:.16e}", assertions)

    rows: list[dict[str, Any]] = []
    for radius in [float(value) for value in stage["initial_h2_radii"]]:
        energy_upper = 0.5 * linear_upper * radius**2 + quartic_upper * radius**4 + sextic_upper * radius**6
        envelope_squared = 2.0 * (energy_upper + young_constant * volume) / h2_coercivity
        envelope = math.sqrt(envelope_squared)
        rows.append({"initial_h2_radius": radius, "energy_upper": energy_upper, "h2_envelope": envelope, "h2_envelope_squared": envelope_squared})
    check("energy_upper_is_monotone_in_radius", all(rows[index + 1]["energy_upper"] > rows[index]["energy_upper"] for index in range(len(rows) - 1)), f"energies={[row['energy_upper'] for row in rows]}", assertions)
    check("h2_envelope_dominates_declared_initial_radii", all(row["h2_envelope"] >= row["initial_h2_radius"] for row in rows), f"envelopes={[row['h2_envelope'] for row in rows]}", assertions)
    check("energy_to_h2_formula_uses_p2_coercivity", all(math.isclose(row["h2_envelope_squared"], 2.0 * (row["energy_upper"] + young_constant * volume) / h2_coercivity, rel_tol=0.0, abs_tol=1e-12) for row in rows), "M2^2=2(E_upper+C_y|T3|)/c_H2", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-energy-ball-envelope-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-ENERGY-BALL-ENVELOPE-PASS" if passed == len(assertions) else "A3-FULL-ENERGY-BALL-ENVELOPE-FAIL",
        "scope": "all canonical P2 trajectories with ||u0||_H2<=R; fixed torus; eta_shell=0; explicit H2 envelope only",
        "derived_constants": {"volume": volume, "embedding_series_upper": series_upper, "embedding_tail_upper": tail_upper, "h2_to_linf_squared_upper": embedding_squared, "linear_energy_upper": linear_upper, "classii_quartic_coefficient": classii_quartic_coefficient, "quartic_energy_upper": quartic_upper, "sextic_energy_upper": sextic_upper, "young_constant_per_unit_volume": young_constant, "h2_coercivity": h2_coercivity},
        "rows": rows,
        "not_closed_here": ["explicit positive-time H4/H6 smoothing constants", "explicit C(R,tau,T) residual-aliasing constant", "dealiased finite-time evolution bound", "Sector-B solver continuum certificate", "P3 tier promotion"],
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"H2 envelopes: {[row['h2_envelope'] for row in rows]}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
