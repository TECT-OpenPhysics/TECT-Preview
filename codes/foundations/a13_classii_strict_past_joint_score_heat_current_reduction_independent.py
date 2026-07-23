#!/usr/bin/env python3
"""Non-importing audit of the A13 joint-score and heat-current reduction."""
from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STRICT-PAST-JOINT-SCORE-HEAT-CURRENT-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-23-independent-strict-past-joint-score-heat-current-reduction/result.json"
EPS = 0.45


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.stem, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True); handle.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def load_parameters():
    manifest = json.loads((REPO / "claims" / CLAIM / "classii_translation_model_reduction_manifest.json").read_text(encoding="utf-8"))
    return json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))["parameters"]


def realify(matrix):
    matrix = np.asarray(matrix, dtype=np.complex128)
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def production_b(field, parameters):
    generators = (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], complex),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], complex),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], complex),
    )
    denominator = parameters["M_X"] ** 2 + parameters["classii_mass_regularizer"]
    q_matrix = np.array([
        [parameters["cJJ"] * parameters["alpha_X"] ** 2 / denominator, parameters["cJK"] * parameters["alpha_X"] * parameters["beta_X"] / denominator],
        [parameters["cJK"] * parameters["alpha_X"] * parameters["beta_X"] / denominator, parameters["cKK"] * parameters["beta_X"] ** 2 / denominator],
    ])
    value = np.asarray(field, float); flat = value.reshape(-1, 6); rho = np.sum(flat * flat, axis=1)
    result = np.zeros((len(flat), 6, 6))
    for generator in generators:
        symmetric = realify(generator); moment = np.einsum("ni,ij,nj->n", flat, symmetric, flat)
        p = 2 * np.einsum("ij,nj->ni", symmetric, flat)
        v = p - 2 * (moment / (rho + parameters["rho_regularizer"]))[:, None] * flat
        frame = np.stack((p, v), axis=-1); result += np.einsum("nia,ab,njb->nij", frame, q_matrix, frame)
    return result.reshape(value.shape[:-1] + (6, 6))


def sigma(scale):
    atoms = np.concatenate((np.sqrt(6 * scale) * np.eye(6), -np.sqrt(6 * scale) * np.eye(6)))
    return atoms, np.full(12, 1 / 12)


def main():
    rng = np.random.default_rng(26072322); parameters = load_parameters(); q = 1 / (2 * EPS)
    joint_residual = 0.0; omitted_score_residual = 0.0
    for _ in range(377):
        dimension = int(rng.integers(1, 10)); raw = rng.normal(size=(dimension, dimension))
        t = raw.T @ raw / dimension; ell, score, shift = rng.normal(size=(3, dimension))
        metric = t + np.eye(dimension) / q
        old_center = np.linalg.solve(metric, ell); joint_center = np.linalg.solve(metric, ell + score)
        lhs = -EPS * shift @ shift - .5 * ell @ old_center + score @ shift + .5 * (shift + old_center) @ metric @ (shift + old_center)
        rhs = -EPS * shift @ shift - .5 * (ell + score) @ joint_center + .5 * (shift + joint_center) @ metric @ (shift + joint_center)
        joint_residual = max(joint_residual, abs(float(lhs - rhs)))
        wrong = -EPS * shift @ shift - .5 * ell @ old_center + .5 * (shift + old_center) @ metric @ (shift + old_center)
        omitted_score_residual = max(omitted_score_residual, abs(float(lhs - wrong)))

    x, dx, h, dh = rng.normal(size=(4, 6)); values, vw = sigma(.31); derivatives, dw = sigma(.23)
    old = production_b(x, parameters); matrices = production_b(x + h + values, parameters); direct = 0.0
    for index, value_weight in enumerate(vw):
        delta = matrices[index] - old
        for derivative, derivative_weight in zip(derivatives, dw):
            gradient = dx + dh + derivative
            direct += .5 * value_weight * derivative_weight * np.einsum("ij,ij->", delta, np.outer(gradient, gradient) - .23 * np.eye(6) - .47 * np.eye(6))
    predicted = .5 * np.einsum("ij,ij->", sum(weight * matrix for weight, matrix in zip(vw, matrices)) - old, np.outer(dx + dh, dx + dh) - .47 * np.eye(6))
    heat_residual = abs(float(direct - predicted))

    correlated_direct = 0.0
    for value, weight in zip(values, vw):
        delta = production_b(x + h + value, parameters) - old; derivative = .4 * value
        gradient = dx + dh + derivative
        correlated_direct += .5 * weight * np.einsum("ij,ij->", delta, np.outer(gradient, gradient) - .4 ** 2 * .31 * np.eye(6) - .47 * np.eye(6))
    independence_prediction = .5 * np.einsum("ij,ij->", sum(weight * production_b(x + h + value, parameters) for value, weight in zip(values, vw)) - old, np.outer(dx + dh, dx + dh) - .47 * np.eye(6))
    correlated_failure = abs(float(correlated_direct - independence_prediction))

    zero = production_b(np.zeros(6), parameters); mean_b = sum(weight * production_b(value, parameters) for value, weight in zip(values, vw))
    negative_c = -.5 * float(np.trace((mean_b - zero) @ (.61 * np.eye(6))))
    ell = rng.normal(size=7); factor_four = float(((2 * ell) @ (q * np.eye(7)) @ (2 * ell)) / (ell @ (q * np.eye(7)) @ ell))
    checks = {
        "independent_joint_recentring": joint_residual < 5e-12,
        "omitting_coefficient_score_fails": omitted_score_residual > 1e-2,
        "independent_heat_current": heat_residual < 2e-14,
        "correlated_value_derivative_negative_control": correlated_failure > 1e-4,
        "conditional_c_is_strictly_negative": negative_c < -1e-5,
        "production_b_at_zero_vanishes": float(abs(zero).max()) < 1e-15,
        "mean_production_b_is_psd": float(np.linalg.eigvalsh(mean_b).min()) > -1e-14,
        "factor_four_reproduced": abs(factor_four - 4) < 1e-14,
        "q_reproduced": abs(q - 10/9) < 1e-15,
    }
    checks = {key: bool(value) for key, value in checks.items()}; assert all(checks.values()), checks
    computed = {"joint_residual": joint_residual, "omitted_score_residual": omitted_score_residual, "heat_current_residual": heat_residual, "correlated_failure": correlated_failure, "negative_conditional_c": negative_c, "factor_four_ratio": factor_four, "q": q}
    data = {"schema": "tect/a13-joint-score-heat-current-independent/1.0", "result_id": RESULT_ID, "claim": CLAIM, "date": "2026-07-23", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "script_version": __version__, "computed": computed, "assertions": checks, "assertion_count": len(checks), "pass": True, "honesty_boundary": "Independent finite-dimensional reduction audit only; no global joint-remainder bound or Nelson theorem."}
    atomic_json(OUT, data)
    print(f"INDEPENDENT {len(checks)}/{len(checks)} PASS"); print(f"joint_residual={joint_residual:.3e}"); print(f"heat_residual={heat_residual:.3e}"); print(RESULT_ID + "-INDEPENDENT-PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
