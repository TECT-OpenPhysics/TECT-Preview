#!/usr/bin/env python3
"""Positive-time uniform P2 solution-ball Galerkin/quadrature bound audit.

For the P2 canonical gradient flow, this audit records the Sobolev-order
accounting behind the analytic statement

  sup_{u0 in B_R(H2), tau <= t <= T}
  || P_N R(u(t)) - R_N^C(P_N u(t)) ||_L2 <= C(R,tau,T) N^-2.

P2 smoothing supplies the finite H6 envelope on every positive-time interval.
The fourth-order residual maps H6 to H2; H2 is above the three-dimensional
aliasing summability threshold.  The script checks the exact exponent and
Fourier-tail bookkeeping against the hash-pinned P1/P2/P3 authorities.  It
does not invent a numerical value for C(R,tau,T), so it is not a controlled
numerical error certificate for Sector-B solver output.
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
BACKEND = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-solution-ball-bound" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: str, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    p2 = json.loads(P2_MANIFEST.read_text(encoding="utf-8"))
    stage = manifest["stage6"]
    acceptance = stage["acceptance"]
    authority = manifest["authority"]
    assertions: list[dict[str, Any]] = []

    for key, path in (("p1_backend", BACKEND), ("p1_manifest", P1_MANIFEST), ("p2_manifest", P2_MANIFEST)):
        actual = sha256(path)
        expected = authority[key]["sha256"]
        check(f"{key}_hash", actual == expected, f"actual={actual}; expected={expected}", assertions)

    solution = stage["solution_ball"]
    sobolev_order = int(solution["positive_time_sobolev_order"])
    residual_order = int(stage["residual_differential_order"])
    projection_target_order = int(stage["projection_target_sobolev_order"])
    alias_order = sobolev_order - residual_order
    tail_order = sobolev_order - projection_target_order
    required_alias_order = float(acceptance["strict_alias_sobolev_order_min"])
    expected_rate = float(acceptance["uniform_rate_min"])
    computed_rate = float(alias_order)

    check("p2_declares_global_h2_and_positive_time_smoothing", p2["theorem_target"]["initial_space"] == "H^2(T^3;C^3)" and "C-infinity" in p2["theorem_target"]["solution"], "P2 provides global H2 flow and C-infinity smoothing for t>0", assertions)
    check("positive_time_interval_is_excluded_from_t0", float(solution["tau"]) > 0.0 and float(solution["T"]) >= float(solution["tau"]), f"tau={solution['tau']}; T={solution['T']}", assertions)
    check("residual_order_matches_pinned_fourth_order_principal_part", residual_order == int(acceptance["pinned_residual_order"]), f"residual_order={residual_order}", assertions)
    check("positive_time_regularisation_is_sufficient", sobolev_order >= residual_order + math.ceil(required_alias_order), f"H{sobolev_order} -> H{alias_order}; alias threshold>{required_alias_order}", assertions)
    check("residual_alias_regularity_exceeds_dimension_threshold", float(alias_order) > required_alias_order, f"alias regularity={alias_order}; threshold={required_alias_order}", assertions)
    check("projection_tail_controls_h2_difference", tail_order > 0, f"H{sobolev_order} to H{projection_target_order} tail order={tail_order}", assertions)
    check("uniform_alias_rate_is_declared", computed_rate >= expected_rate, f"computed N^(-{computed_rate:g}); minimum N^(-{expected_rate:g})", assertions)

    periods = [float(p1["parameters"][key]) for key in ("Lx", "Ly", "Lz")]
    grids = [int(value) for value in stage["audit_grids"]]
    rows: list[dict[str, Any]] = []
    for grid in grids:
        cutoff = min(math.pi * grid / period for period in periods)
        tail_factor = (1.0 + cutoff * cutoff) ** (-0.5 * tail_order)
        alias_factor = (1.0 + cutoff * cutoff) ** (-0.5 * alias_order)
        rows.append({"grid": grid, "cutoff_lower_bound": cutoff, "h2_projection_tail_factor": tail_factor, "h2_alias_factor": alias_factor})
    check("fourier_cutoff_increases_with_grid", all(rows[index + 1]["cutoff_lower_bound"] > rows[index]["cutoff_lower_bound"] for index in range(len(rows) - 1)), f"cutoffs={[row['cutoff_lower_bound'] for row in rows]}", assertions)
    check("tail_and_alias_envelopes_decrease_with_grid", all(rows[index + 1]["h2_alias_factor"] < rows[index]["h2_alias_factor"] and rows[index + 1]["h2_projection_tail_factor"] < rows[index]["h2_projection_tail_factor"] for index in range(len(rows) - 1)), f"alias={[row['h2_alias_factor'] for row in rows]}", assertions)
    check("positive_regularisers_remain_pinned", float(p1["parameters"]["rho_regularizer"]) > 0.0 and float(p1["parameters"]["classii_mass_regularizer"]) > 0.0, "rho and Class-II mass floors are positive", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-solution-ball-bound-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-SOLUTION-BALL-BOUND-PASS" if passed == len(assertions) else "A3-FULL-SOLUTION-BALL-BOUND-FAIL",
        "scope": "analytic positive-time H2 initial-data ball; fixed torus; eta_shell=0; qualitative constant C(R,tau,T) not numerically enclosed",
        "theorem_statement": stage["theorem_statement"],
        "constant_status": stage["constant_status"],
        "sobolev_accounting": {"solution_order": sobolev_order, "residual_order": residual_order, "alias_order": alias_order, "projection_tail_order": tail_order, "uniform_rate": computed_rate},
        "rows": rows,
        "not_closed_here": ["a numerical enclosure of C(R,tau,T)", "a controlled error bar for a historical Sector-B solver run", "all-time t=0 H2 aliasing control", "P3 tier promotion"],
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Uniform positive-time rate: N^(-{computed_rate:g}) times C(R,tau,T)")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
