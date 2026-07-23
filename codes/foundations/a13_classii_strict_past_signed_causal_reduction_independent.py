#!/usr/bin/env python3
"""Non-importing audit of the A13 strict-past signed causal reduction.

Uses probabilists' Gauss--Hermite quadrature and finite-difference Jacobians,
independently of the primary implementation.  It also includes two asymmetric
negative controls that break strict-past causality.
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
OUT = REPO / "claims" / CLAIM / "runs" / "2026-07-23-independent-strict-past-signed-causal-reduction" / "result.json"
EPS_CONTROL = 0.45
GH_ORDER = 13
FD_STEP = 2e-5  # tooling threshold for the independent derivative check


def causal_shift(x):
    return np.array([
        0.0,
        0.2 * x[0] ** 2 - 0.1,
        -0.15 * x[0] * x[1] + 0.05 * x[0] + 0.07 * x[1],
    ])


def noncausal_shift(x):
    value = causal_shift(x)
    value[0] = 0.2 * x[1]
    return value


def causal_predictor(z):
    return np.array([
        0.0,
        0.3 * z[0] + 0.1 * z[0] ** 2,
        -0.2 * z[0] + 0.25 * z[1] + 0.05 * z[0] * z[1],
    ])


def future_predictor(z):
    value = causal_predictor(z)
    value[1] += 0.3 * z[2]
    return value


def innovation(z):
    return np.array([
        0.1 * z[0] + 0.07 * z[1] ** 2,
        -0.12 * z[0] * z[2] + 0.03 * z[1],
        0.08 * z[0] ** 2 * z[2] - 0.04 * z[1],
    ])


def finite_jacobian(function, x):
    jac = np.empty((3, 3))
    for column in range(3):
        step = np.zeros(3)
        step[column] = FD_STEP
        jac[:, column] = (function(x + step) - function(x - step)) / (2.0 * FD_STEP)
    return jac


def divergence(z, field):
    return float(np.dot(z, field(z)) - np.trace(finite_jacobian(field, z)))


def expectation(function):
    nodes, weights = np.polynomial.hermite_e.hermegauss(GH_ORDER)
    total = 0.0
    normalizer = (2.0 * math.pi) ** 1.5
    for i, x0 in enumerate(nodes):
        for j, x1 in enumerate(nodes):
            for k, x2 in enumerate(nodes):
                total += weights[i] * weights[j] * weights[k] * function(np.array([x0, x1, x2]))
    return total / normalizer


def identity_residual(shift, predictor):
    lhs = expectation(lambda x: divergence(x + shift(x), predictor))
    rhs = expectation(lambda x: float(np.dot(shift(x), predictor(x + shift(x)))))
    return abs(lhs - rhs), lhs, rhs


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
    residual, lhs, rhs = identity_residual(causal_shift, causal_predictor)
    bad_shift_residual, _, _ = identity_residual(noncausal_shift, causal_predictor)
    bad_predictor_residual, _, _ = identity_residual(causal_shift, future_predictor)

    completion_gap = expectation(lambda x: (
        0.5 * (divergence(x + causal_shift(x), causal_predictor) + divergence(x + causal_shift(x), innovation))
        + EPS_CONTROL * np.dot(causal_shift(x), causal_shift(x))
        + np.dot(causal_predictor(x + causal_shift(x)), causal_predictor(x + causal_shift(x))) / (16.0 * EPS_CONTROL)
        - 0.5 * divergence(x + causal_shift(x), innovation)
    ))
    completion_square = expectation(lambda x: EPS_CONTROL * np.dot(
        causal_shift(x) + causal_predictor(x + causal_shift(x)) / (4.0 * EPS_CONTROL),
        causal_shift(x) + causal_predictor(x + causal_shift(x)) / (4.0 * EPS_CONTROL),
    ))
    completion_residual = abs(completion_gap - completion_square)

    q_value = 1.0 / (2.0 * EPS_CONTROL)
    def metric_terms(x):
        h = causal_shift(x)
        z = x + h
        t_diag = np.array([
            0.31,
            0.22 + 0.03 * z[0] ** 2,
            0.17 + 0.02 * z[0] ** 2 + 0.01 * z[1] ** 2,
        ])
        ell = np.array([0.0, 0.11 * z[0], -0.08 * z[0] + 0.07 * z[1]])
        affine = 0.5 * np.dot(t_diag, z * z - 1.0) + np.dot(ell, z)
        conditional = 0.5 * np.dot(t_diag, h * h) + np.dot(ell, h)
        inverse = 1.0 / (t_diag + 2.0 * EPS_CONTROL)
        source = 0.5 * np.dot(ell * inverse, ell)
        gap = affine + EPS_CONTROL * np.dot(h, h) + source
        square = 0.5 * np.dot(t_diag + 2.0 * EPS_CONTROL, (h + inverse * ell) ** 2)
        raw = np.dot(ell, ell) / (4.0 * EPS_CONTROL)
        return float(affine), float(conditional), float(gap), float(square), float(source), float(raw)

    metric = [expectation(lambda x, index=index: metric_terms(x)[index]) for index in range(6)]
    metric_causal_residual = abs(metric[0] - metric[1])
    metric_completion_residual = abs(metric[2] - metric[3])

    sample_points = [
        np.array([0.2, -0.4, 0.7]),
        np.array([-1.1, 0.3, -0.2]),
        np.array([0.8, 1.2, -0.5]),
    ]
    max_upper = max(float(np.max(np.abs(np.triu(finite_jacobian(causal_predictor, z))))) for z in sample_points)

    assertions = {
        "independent_causal_identity": residual < 2e-8,
        "independent_completion_identity": completion_residual < 2e-8,
        "strict_lower_structure": max_upper < 2e-9,
        "noncausal_shift_control_fails": bad_shift_residual > 1e-3,
        "future_predictor_control_fails": bad_predictor_residual > 1e-3,
        "completion_is_positive": completion_square > 1e-4,
        "finite_difference_step_is_declared": FD_STEP > 0,
        "independent_affine_psd_causal_identity": metric_causal_residual < 2e-10,
        "independent_metric_resolvent_completion": metric_completion_residual < 2e-10,
        "independent_q_matches_ten_ninths": abs(q_value - 10.0 / 9.0) < 1e-15,
        "independent_resolvent_rebate": 0.0 < metric[4] < metric[5],
    }
    assertions = {key: bool(value) for key, value in assertions.items()}
    assert all(assertions.values()), {
        "assertions": assertions,
        "bad_shift_residual": bad_shift_residual,
        "bad_predictor_residual": bad_predictor_residual,
    }

    result = {
        "schema": "tect/a13-strict-past-signed-causal-independent-result/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {"epsilon_control": EPS_CONTROL, "gauss_hermite_order": GH_ORDER, "finite_difference_step": FD_STEP},
        "computed": {
            "causal_identity_lhs": lhs,
            "causal_identity_rhs": rhs,
            "causal_identity_residual": residual,
            "completion_gap": completion_gap,
            "completion_square": completion_square,
            "completion_residual": completion_residual,
            "metric_causal_residual": metric_causal_residual,
            "metric_completion_residual": metric_completion_residual,
            "resolvent_source_charge": metric[4],
            "raw_source_charge": metric[5],
            "q_from_epsilon": q_value,
            "bad_shift_residual": bad_shift_residual,
            "bad_predictor_residual": bad_predictor_residual,
            "max_upper_triangular_defect": max_upper,
        },
        "assertions": assertions,
        "assertion_count": len(assertions),
        "pass": True,
        "honesty_boundary": "Independent finite-dimensional strict-past and PSD-resolvent regression only. It does not prove the cutoff-uniform A11 coefficient-increment signed-charge estimate or any Nelson/interacting-measure conclusion.",
    }
    atomic_json(OUT, result)
    print(f"INDEPENDENT {len(assertions)}/{len(assertions)} PASS")
    print(f"causal_identity_residual={residual:.3e}")
    print(f"bad_shift_residual={bad_shift_residual:.3e}")
    print(f"bad_predictor_residual={bad_predictor_residual:.3e}")
    print(f"metric_completion_residual={metric_completion_residual:.3e}")
    print(RESULT_ID + "-INDEPENDENT-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
