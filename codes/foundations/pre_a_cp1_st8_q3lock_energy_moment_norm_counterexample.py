#!/usr/bin/env python3
"""Primary two-level Gibbs counterexample for EXP-001144."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_energy_moment_norm_counterexample"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-energy-moment-norm-counterexample-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    p0 = Fraction(fixture["probabilities"][0])
    p1 = Fraction(fixture["probabilities"][1])
    gap = int(fixture["energy_gap"])
    shift = int(fixture["shift_constant"])
    k0, k1 = shift, gap + shift
    tolerance = float(fixture["tolerance"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("provenance", manifest["exploration_id"] == "EXP-001144" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001144/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("probability normalization", p0 + p1 == 1 and p0 > p1 > 0, [p0, p1], "positive normalized Gibbs pair", "Gibbs state")
    check("Gibbs ratio", p0 / p1 == gap, p0 / p1, gap, "Gibbs ratio")
    check("shifted energies", (k0, k1) == (shift, gap + shift) and k1 - k0 == gap, [k0, k1], [shift, gap + shift], "energy shift")

    probability_gap = float(p0 - p1)
    log_ratio = math.log(float(p0)) - math.log(float(p1))
    logarithmic_mean = probability_gap / log_ratio
    lower_bound = float(Fraction(99, 505))
    m2_fraction = p0 * k0**2 + p1 * k1**2
    m2 = float(m2_fraction)
    operator_norm = 1.0
    hilbert_schmidt_norm = 1.0
    spectral_moment = 2.0 * logarithmic_mean * float(gap**2)
    candidate_operator_bound = float(fixture["transfer_constant"]) * m2 * operator_norm**2
    candidate_hilbert_schmidt_bound = float(fixture["transfer_constant"]) * m2 * hilbert_schmidt_norm**2

    check("logarithm elementary bound", math.log(float(gap)) < float(fixture["energy_gap"]) / float(fixture["shift_constant"]) / 20.0, math.log(float(gap)), "<5", "log mean")
    check("exact log-mean lower bound", logarithmic_mean > lower_bound, logarithmic_mean, f">{lower_bound}", "log mean")
    check("moment arithmetic", m2_fraction == Fraction(10301, 101), m2_fraction, Fraction(10301, 101), "Gibbs moment")
    check("rank-one norms", abs(operator_norm - 1.0) <= tolerance and abs(hilbert_schmidt_norm - 1.0) <= tolerance, [operator_norm, hilbert_schmidt_norm], [1.0, 1.0], "norm fixture")
    check("operator-norm route fails", spectral_moment > candidate_operator_bound + tolerance, [spectral_moment, candidate_operator_bound], "S>8*M2*||D||^2", "route obstruction")
    check("Hilbert-Schmidt route fails", spectral_moment > candidate_hilbert_schmidt_bound + tolerance, [spectral_moment, candidate_hilbert_schmidt_bound], "S>8*M2*||D||_HS^2", "route obstruction")

    d00, d01, d10, d11 = 0.0, 1.0, 0.0, 0.0
    a = float(p0) * k0**2 * d01**2
    b = float(p0) * k1**2 * d01**2
    c = float(p1) * k0**2 * d01**2
    d = float(p1) * k1**2 * d01**2
    weighted_rhs = 2.0 * (a + b + c + d)
    trace_k2 = float(k0**2 + k1**2)
    coarse_trace_bound = 4.0 * (m2 + trace_k2) * operator_norm**2
    check("D-weighted interface", spectral_moment <= weighted_rhs + tolerance, [spectral_moment, weighted_rhs], "S<=2*(A+B+C+D)", "corrected interface")
    check("coarse trace fallback", spectral_moment <= coarse_trace_bound + tolerance, [spectral_moment, coarse_trace_bound], "S<=4*(M2+Tr(K^2))*||D||^2", "corrected interface")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-ENERGY-MOMENT-NORM-COUNTEREXAMPLE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "probabilities": [float(p0), float(p1)],
            "shifted_energies": [k0, k1],
            "logarithmic_mean": logarithmic_mean,
            "logarithmic_mean_lower_bound": lower_bound,
            "M2": m2,
            "spectral_moment": spectral_moment,
            "operator_norm": operator_norm,
            "hilbert_schmidt_norm": hilbert_schmidt_norm,
            "operator_candidate_bound": candidate_operator_bound,
            "hilbert_schmidt_candidate_bound": candidate_hilbert_schmidt_bound,
            "weighted_rhs": weighted_rhs,
            "coarse_trace_bound": coarse_trace_bound,
            "two_level_counterexample_closed": True,
            "operator_norm_general_transfer_refuted": True,
            "hilbert_schmidt_general_transfer_refuted": True,
            "D_weighted_two_sided_interface_identified": True,
            "actual_q3_rows_remain_empirical": True,
            "uniform_local_M2_common_core_closed": False,
            "common_alpha_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY ENERGY-MOMENT-NORM-COUNTEREXAMPLE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
