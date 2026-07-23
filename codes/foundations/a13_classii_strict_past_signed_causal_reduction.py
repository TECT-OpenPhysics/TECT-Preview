#!/usr/bin/env python3
"""Primary audit for the A13 strict-past signed causal reduction.

For a standard Gaussian vector xi ordered by shell and strictly lower-
triangular maps h and b_<, verify

    E delta b_<(xi+h(xi)) = E <h(xi), b_<(xi+h(xi))>.

It also retains a strictly-past positive affine block

    a_j(z)=T_j(z_<j) z_j + 2 ell_j(z_<j),  T_j>=0,

and verifies the exact metric completion with
q=1/(2 eps):

    q/2 <ell_j,(I+qT_j)^(-1)ell_j>.

For the A11 telescope, delta a/2 is I_j and the remaining divergence is the
coefficient increment C_j.  The production bound on the resulting coupled
signed charge remains open.
"""

__version__ = "1.1.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STRICT-PAST-RESOLVENT-SIGNED-CHARGE-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs" / "2026-07-23-primary-strict-past-signed-causal-reduction" / "result.json"
EPS_CONTROL = 0.45  # declared production stress input from the A13 gate
GH_ORDER = 12  # tooling threshold: exact for the fixture polynomial degree


def shift(x):
    x0, x1, _ = x
    return np.array([
        0.0,
        0.2 * x0 * x0 - 0.1,
        -0.15 * x0 * x1 + 0.05 * x0 + 0.07 * x1,
    ])


def jac_shift(x):
    x0, x1, _ = x
    return np.array([
        [0.0, 0.0, 0.0],
        [0.4 * x0, 0.0, 0.0],
        [-0.15 * x1 + 0.05, -0.15 * x0 + 0.07, 0.0],
    ])


def predictor(z):
    z0, z1, _ = z
    return np.array([
        0.0,
        0.3 * z0 + 0.1 * z0 * z0,
        -0.2 * z0 + 0.25 * z1 + 0.05 * z0 * z1,
    ])


def jac_predictor(z):
    z0, z1, _ = z
    return np.array([
        [0.0, 0.0, 0.0],
        [0.3 + 0.2 * z0, 0.0, 0.0],
        [-0.2 + 0.05 * z1, 0.25 + 0.05 * z0, 0.0],
    ])


def remainder(z):
    z0, z1, z2 = z
    return np.array([
        0.1 * z0 + 0.07 * z1 * z1,
        -0.12 * z0 * z2 + 0.03 * z1,
        0.08 * z0 * z0 * z2 - 0.04 * z1,
    ])


def jac_remainder(z):
    z0, z1, z2 = z
    return np.array([
        [0.1, 0.14 * z1, 0.0],
        [-0.12 * z2, 0.03, -0.12 * z0],
        [0.16 * z0 * z2, -0.04, 0.08 * z0 * z0],
    ])


def divergence(z, field, jacobian):
    return float(np.dot(z, field(z)) - np.trace(jacobian(z)))


def gaussian_grid(order):
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    nodes = math.sqrt(2.0) * nodes
    weights = weights / math.sqrt(math.pi)
    for i, x0 in enumerate(nodes):
        for j, x1 in enumerate(nodes):
            for k, x2 in enumerate(nodes):
                yield np.array([x0, x1, x2]), weights[i] * weights[j] * weights[k]


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.stem + "-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def main():
    totals = {
        "delta_predictor": 0.0,
        "shift_pairing": 0.0,
        "energy": 0.0,
        "shift_energy": 0.0,
        "signed_charge": 0.0,
        "completion_gap": 0.0,
        "completion_square": 0.0,
        "metric_affine_divergence": 0.0,
        "metric_conditional_energy": 0.0,
        "metric_completion_gap": 0.0,
        "metric_completion_square": 0.0,
        "resolvent_source_charge": 0.0,
        "raw_source_charge": 0.0,
    }
    max_triangular_defect = 0.0
    max_trace_feedback = 0.0
    min_pointwise_gap = float("inf")

    for x, weight in gaussian_grid(GH_ORDER):
        h = shift(x)
        z = x + h
        bp = predictor(z)
        jp = jac_predictor(z)
        jh = jac_shift(x)
        dr = divergence(z, remainder, jac_remainder)
        dp = divergence(z, predictor, jac_predictor)
        energy = 0.5 * (dp + dr)
        signed_charge = np.dot(bp, bp) / (16.0 * EPS_CONTROL) - 0.5 * dr
        gap = energy + EPS_CONTROL * np.dot(h, h) + signed_charge
        square = EPS_CONTROL * np.dot(h + bp / (4.0 * EPS_CONTROL), h + bp / (4.0 * EPS_CONTROL))

        totals["delta_predictor"] += weight * dp
        totals["shift_pairing"] += weight * float(np.dot(h, bp))
        totals["energy"] += weight * energy
        totals["shift_energy"] += weight * float(np.dot(h, h))
        totals["signed_charge"] += weight * signed_charge
        totals["completion_gap"] += weight * gap
        totals["completion_square"] += weight * square
        max_triangular_defect = max(
            max_triangular_defect,
            float(np.max(np.abs(np.triu(jp)))),
            float(np.max(np.abs(np.triu(jh)))),
        )
        max_trace_feedback = max(max_trace_feedback, abs(float(np.trace(jp @ jh))))
        min_pointwise_gap = min(min_pointwise_gap, gap)

        q_value = 1.0 / (2.0 * EPS_CONTROL)
        t_diag = np.array([
            0.31,
            0.22 + 0.03 * z[0] * z[0],
            0.17 + 0.02 * z[0] * z[0] + 0.01 * z[1] * z[1],
        ])
        ell = np.array([0.0, 0.11 * z[0], -0.08 * z[0] + 0.07 * z[1]])
        resolvent = 1.0 / (1.0 + q_value * t_diag)
        affine_divergence = 0.5 * float(np.dot(t_diag, z * z - 1.0)) + float(np.dot(ell, z))
        conditional_energy = 0.5 * float(np.dot(t_diag, h * h)) + float(np.dot(ell, h))
        source_charge = 0.5 * q_value * float(np.dot(ell * resolvent, ell))
        raw_source_charge = 0.5 * q_value * float(np.dot(ell, ell))
        metric_gap = affine_divergence + EPS_CONTROL * float(np.dot(h, h)) + source_charge
        metric_square = 0.5 * float(np.dot(
            t_diag + 2.0 * EPS_CONTROL,
            (h + ell / (t_diag + 2.0 * EPS_CONTROL)) ** 2,
        ))
        totals["metric_affine_divergence"] += weight * affine_divergence
        totals["metric_conditional_energy"] += weight * conditional_energy
        totals["metric_completion_gap"] += weight * metric_gap
        totals["metric_completion_square"] += weight * metric_square
        totals["resolvent_source_charge"] += weight * source_charge
        totals["raw_source_charge"] += weight * raw_source_charge

    identity_residual = abs(totals["delta_predictor"] - totals["shift_pairing"])
    completion_residual = abs(totals["completion_gap"] - totals["completion_square"])
    metric_causal_residual = abs(totals["metric_affine_divergence"] - totals["metric_conditional_energy"])
    metric_completion_residual = abs(totals["metric_completion_gap"] - totals["metric_completion_square"])
    q_value = 1.0 / (2.0 * EPS_CONTROL)
    assertions = {
        "predictor_is_strict_lower_triangular": max_triangular_defect < 1e-14,
        "strict_triangular_feedback_trace_vanishes": max_trace_feedback < 1e-14,
        "gaussian_divergence_identity": identity_residual < 1e-11,
        "single_use_completion_identity": completion_residual < 1e-11,
        "completion_is_expectation_only_not_pointwise": min_pointwise_gap < -1e-3,
        "completion_is_nontrivial": totals["completion_square"] > 1e-4,
        "signed_charge_is_retained": abs(totals["signed_charge"]) > 1e-4,
        "remainder_divergence_is_retained": abs(totals["energy"] - 0.5 * totals["delta_predictor"]) > 1e-4,
        "affine_psd_causal_identity": metric_causal_residual < 1e-11,
        "metric_resolvent_completion_identity": metric_completion_residual < 1e-11,
        "production_q_matches_ten_ninths": abs(q_value - 10.0 / 9.0) < 1e-15,
        "resolvent_strictly_rebates_raw_source": 0.0 < totals["resolvent_source_charge"] < totals["raw_source_charge"],
    }
    assertions = {key: bool(value) for key, value in assertions.items()}
    assert all(assertions.values()), assertions

    result = {
        "schema": "tect/a13-strict-past-signed-causal-primary-result/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {"epsilon_control": EPS_CONTROL, "gauss_hermite_order": GH_ORDER},
        "computed": {
            **totals,
            "identity_residual": identity_residual,
            "completion_residual": completion_residual,
            "metric_causal_residual": metric_causal_residual,
            "metric_completion_residual": metric_completion_residual,
            "q_from_epsilon": q_value,
            "max_triangular_defect": max_triangular_defect,
            "max_trace_feedback": max_trace_feedback,
            "min_pointwise_gap": min_pointwise_gap,
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "pass": True,
        "honesty_boundary": "Exact finite-dimensional strict-past and PSD-resolvent reduction only. A11 identifies the remainder with the signed coefficient increment, but its cutoff-uniform production bound, the one-use inequality, Nelson moment, and interacting measure remain open.",
    }
    atomic_json(OUT, result)
    print(f"PRIMARY {len(assertions)}/{len(assertions)} PASS")
    print(f"identity_residual={identity_residual:.3e}")
    print(f"completion_residual={completion_residual:.3e}")
    print(f"metric_completion_residual={metric_completion_residual:.3e}")
    print(RESULT_ID + "-PRIMARY-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
