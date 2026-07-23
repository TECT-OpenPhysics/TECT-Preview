#!/usr/bin/env python3
"""Primary audit of the A13 joint-score and heat-current reduction."""
from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import json, os, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "codes" / "foundations"))
import a13_classii_translation_model_reduction as tr  # noqa: E402

CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-STRICT-PAST-JOINT-SCORE-HEAT-CURRENT-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-23-primary-strict-past-joint-score-heat-current-reduction/result.json"
EPS, JOINT_CASES, HEAT_CASES = 0.45, 1000, 24


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


def params():
    path = REPO / "claims" / CLAIM / "classii_translation_model_reduction_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))["parameters"]


def sigma(covariance):
    dimension = len(covariance); factor = np.linalg.cholesky(covariance); atoms = []
    for column in range(dimension):
        atom = np.sqrt(float(dimension)) * factor[:, column]; atoms += [atom, -atom]
    atoms = np.asarray(atoms)
    return atoms, np.full(len(atoms), 1.0 / len(atoms))


def joint_audit(rng):
    q = 1.0 / (2.0 * EPS); worst = 0.0; minimum = float("inf")
    for _ in range(JOINT_CASES):
        dimension = int(rng.integers(1, 13)); raw = rng.normal(size=(dimension, dimension))
        t = raw.T @ raw / dimension; ell, score, shift = rng.normal(size=(3, dimension))
        metric = t + np.eye(dimension) / q; inverse = np.linalg.inv(metric)
        old = -EPS * shift @ shift - 0.5 * ell @ inverse @ ell + score @ shift + 0.5 * (shift + inverse @ ell) @ metric @ (shift + inverse @ ell)
        total = ell + score
        new = -EPS * shift @ shift - 0.5 * total @ inverse @ total + 0.5 * (shift + inverse @ total) @ metric @ (shift + inverse @ total)
        worst = max(worst, abs(float(old - new))); minimum = min(minimum, float(np.linalg.eigvalsh(metric).min()))
    ell = rng.normal(size=8); inverse = q * np.eye(8)
    ratio = ((2 * ell) @ inverse @ (2 * ell)) / (ell @ inverse @ ell)
    return {"q": q, "joint_residual": worst, "minimum_metric_eigenvalue": minimum, "factor_four_ratio": float(ratio)}


def heat_audit(rng, parameters):
    worst = 0.0; cross_worst = 0.0
    for _ in range(HEAT_CASES):
        vs, ds, ps = 10 ** rng.uniform(-2, 0), 10 ** rng.uniform(-2, .3), 10 ** rng.uniform(-2, .3)
        x, dx, h, dh = rng.normal(size=(4, 6)); values = rng.normal(scale=np.sqrt(vs), size=(48, 6))
        derivatives, weights = sigma(ds * np.eye(6)); old, _ = tr.coefficient_data(x, parameters)
        matrices, _ = tr.coefficient_data(x + h + values, parameters); direct = 0.0; cross = np.zeros((6, 6))
        for index, value in enumerate(values):
            delta = matrices[index] - old
            for derivative, weight in zip(derivatives, weights):
                gradient = dx + dh + derivative
                centered = np.outer(gradient, gradient) - (ps + ds) * np.eye(6)
                direct += .5 * weight * np.einsum("ij,ij->", delta, centered) / len(values)
                cross += weight * np.outer(value, derivative) / len(values)
        mean_delta = matrices.mean(axis=0) - old
        predicted = .5 * np.einsum("ij,ij->", mean_delta, np.outer(dx + dh, dx + dh) - ps * np.eye(6))
        worst = max(worst, abs(float(direct - predicted))); cross_worst = max(cross_worst, float(abs(cross).max()))
    return {"heat_current_residual": worst, "cross_covariance": cross_worst}


def positivity_nogo(parameters):
    values, vw = sigma(.3 * np.eye(6)); derivatives, dw = sigma(.2 * np.eye(6))
    past = .7 * np.eye(6); shell = .2 * np.eye(6); zero, _ = tr.coefficient_data(np.zeros(6), parameters)
    direct = 0.0; mean = np.zeros((6, 6))
    for value, a in zip(values, vw):
        matrix, _ = tr.coefficient_data(value, parameters); delta = matrix - zero; mean += a * matrix
        for derivative, b in zip(derivatives, dw):
            direct += .5 * a * b * np.einsum("ij,ij->", delta, np.outer(derivative, derivative) - shell - past)
    predicted = -.5 * np.trace(mean @ past)
    return {"direct_conditional_c": float(direct), "predicted_conditional_c": float(predicted), "nogo_residual": abs(float(direct - predicted)), "minimum_mean_b_eigenvalue": float(np.linalg.eigvalsh(mean).min())}


def main():
    rng = np.random.default_rng(26072321); parameters = params()
    joint = joint_audit(rng); heat = heat_audit(rng, parameters); nogo = positivity_nogo(parameters)
    checks = {
        "joint_recentring": joint["joint_residual"] < 5e-12,
        "q_ten_ninths": abs(joint["q"] - 10/9) < 1e-15,
        "metric_positive": joint["minimum_metric_eigenvalue"] > 0,
        "factor_four": abs(joint["factor_four_ratio"] - 4) < 1e-14,
        "heat_current_identity": heat["heat_current_residual"] < 3e-12,
        "value_derivative_independence": heat["cross_covariance"] < 1e-14,
        "conditional_c_negative": nogo["direct_conditional_c"] < -1e-5,
        "negative_fixture_matches_formula": nogo["nogo_residual"] < 2e-14,
        "mean_production_b_psd": nogo["minimum_mean_b_eigenvalue"] > -1e-14,
    }
    checks = {key: bool(value) for key, value in checks.items()}; assert all(checks.values()), checks
    data = {"schema": "tect/a13-joint-score-heat-current-primary/1.0", "result_id": RESULT_ID, "claim": CLAIM, "date": "2026-07-23", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "script_version": __version__, "inputs": {"epsilon_control": EPS, "joint_cases": JOINT_CASES, "heat_cases": HEAT_CASES}, "computed": {**joint, **heat, **nogo}, "assertions": checks, "assertion_count": len(checks), "pass": True, "honesty_boundary": "Exact joint-score and conditional heat-current reductions only; the cutoff-uniform joint-remainder/Cartan bound and one-use theorem remain open."}
    atomic_json(OUT, data)
    print(f"PRIMARY {len(checks)}/{len(checks)} PASS"); print(f"joint_residual={joint['joint_residual']:.3e}"); print(f"heat_residual={heat['heat_current_residual']:.3e}"); print(RESULT_ID + "-PRIMARY-PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
