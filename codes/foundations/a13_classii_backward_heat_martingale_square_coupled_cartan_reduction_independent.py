#!/usr/bin/env python3
"""Independent six-real audit of the A13 backward-heat/Cartan reduction.

The script reconstructs the Pauli frames locally and checks the controlled
backward telescope, triangular entropy pullback, retained-square completion,
quartic factor-four identity, averaged frame secant, and shellwise heat no-go.
It does not prove the cutoff-uniform raw-current form or the Nelson theorem.
"""

from __future__ import annotations

__version__ = "1.1.0"
__first_issued__ = "2026-07-23"
__version_issued__ = "2026-07-23"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-BACKWARD-HEAT-MARTINGALE-SQUARE-COUPLED-CARTAN-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-23-independent-backward-heat-martingale-square-coupled-cartan-reduction/result.json"
)
STRICT_PAST_AUTHORITY = (
    REPO
    / "claims"
    / CLAIM
    / "classii_strict_past_signed_causal_reduction_manifest.json"
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def one_use_q() -> float:
    authority = json.loads(STRICT_PAST_AUTHORITY.read_text(encoding="utf-8"))
    epsilon_control = float(authority["audit"]["epsilon_control"])
    return 1.0 / (2.0 * epsilon_control)


Q_EXPONENT = one_use_q()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def parameters() -> dict[str, Any]:
    manifest = json.loads(
        (
            REPO
            / "claims"
            / CLAIM
            / "classii_translation_model_reduction_manifest.json"
        ).read_text(encoding="utf-8")
    )
    authority = REPO / manifest["authority"]["a1_manifest"]["path"]
    return json.loads(authority.read_text(encoding="utf-8"))["parameters"]


def hermite(dimension: int, order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, one_weights = np.polynomial.hermite.hermgauss(order)
    indices = np.indices((order,) * dimension, dtype=np.int16).reshape(dimension, -1).T
    points = math.sqrt(2.0) * nodes[indices]
    weights = np.prod(one_weights[indices], axis=1) / (math.pi ** (dimension / 2.0))
    return points, weights


def realify(matrix: np.ndarray) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def q_matrix(model: dict[str, Any]) -> np.ndarray:
    denominator = float(model["M_X"]) ** 2 + float(model["classii_mass_regularizer"])
    return np.asarray(
        [
            [
                float(model["cJJ"]) * float(model["alpha_X"]) ** 2 / denominator,
                float(model["cJK"])
                * float(model["alpha_X"])
                * float(model["beta_X"])
                / denominator,
            ],
            [
                float(model["cJK"])
                * float(model["alpha_X"])
                * float(model["beta_X"])
                / denominator,
                float(model["cKK"]) * float(model["beta_X"]) ** 2 / denominator,
            ],
        ]
    )


def frames_and_b(field: np.ndarray, model: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray]:
    values = np.asarray(field, dtype=float)
    flat = values.reshape(-1, 6)
    rho = np.sum(flat * flat, axis=1)
    floor = float(model["rho_regularizer"])
    matrix = q_matrix(model)
    result = np.zeros((len(flat), 6, 6))
    frames: list[np.ndarray] = []
    for generator in generators():
        symmetric = realify(generator)
        moment = np.einsum("ni,ij,nj->n", flat, symmetric, flat)
        ratio = moment / (rho + floor)
        first = 2.0 * np.einsum("ij,nj->ni", symmetric, flat)
        second = first - 2.0 * ratio[:, None] * flat
        frame = np.stack((first, second), axis=-1)
        frames.append(frame.reshape(values.shape[:-1] + (6, 2)))
        result += np.einsum("nia,ab,njb->nij", frame, matrix, frame)
    return frames, result.reshape(values.shape[:-1] + (6, 6))


def martingale_telescope() -> dict[str, float]:
    sigma = np.asarray([0.19, 0.08, 0.035])
    delta_gamma = np.asarray([0.28, 0.21, 0.13])
    points, weights = hermite(6, 4)
    value = np.zeros(len(points))
    derivative = np.zeros(len(points))
    drift = np.zeros(len(points))

    def w(stage: int, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return 0.5 * (1.0 + x * x + float(np.sum(sigma[stage:]))) * (
            y * y - float(np.sum(delta_gamma[:stage]))
        )

    for stage in range(3):
        if stage == 0:
            a = np.full(len(points), -0.06)
            b = np.full(len(points), 0.025)
        elif stage == 1:
            a = -0.035 * value + 0.018 * derivative
            b = 0.022 * value + 0.011 * derivative - 0.005
        else:
            a = 0.017 * value - 0.021 * derivative + 0.009
            b = -0.014 * value + 0.019 * derivative
        drift += w(stage, value + a, derivative + b) - w(stage, value, derivative)
        value += a + math.sqrt(float(sigma[stage])) * points[:, 2 * stage]
        derivative += b + math.sqrt(float(delta_gamma[stage])) * points[:, 2 * stage + 1]

    terminal = 0.5 * (1.0 + value * value) * (
        derivative * derivative - float(np.sum(delta_gamma))
    )
    return {
        "independent_telescope_residual": abs(float(weights @ (terminal - drift))),
        "terminal_expectation": float(weights @ terminal),
        "drift_expectation": float(weights @ drift),
    }


def triangular_entropy_chain() -> dict[str, float]:
    points, weights = hermite(2, 30)
    one_points, one_weights = hermite(1, 52)
    xi1, xi2 = points[:, 0], points[:, 1]
    first_shift = 0.17
    slope = -0.28
    z1 = xi1 + first_shift
    true_second_shift = slope * xi1
    z2 = xi2 + true_second_shift

    def f1(u: np.ndarray) -> np.ndarray:
        return 0.12 * (u * u - 1.0) + 0.08 * u + 0.01 * u**4

    def f2(past: np.ndarray, u: np.ndarray) -> np.ndarray:
        return 0.09 * (u * u - 1.0) + 0.06 * past * u + 0.015 * u**4 + 0.01 * past**2

    k1 = math.log(float(one_weights @ np.exp(-Q_EXPONENT * f1(one_points[:, 0])))) / Q_EXPONENT
    trial = one_points[:, 0]
    f2_grid = f2(z1[:, None], trial[None, :])
    k2 = np.log(np.exp(-Q_EXPONENT * f2_grid) @ one_weights) / Q_EXPONENT
    action = f1(z1) + f2(z1, z2)
    log_q_over_p = (
        first_shift * z1
        - 0.5 * first_shift**2
        + true_second_shift * z2
        - 0.5 * true_second_shift**2
        + Q_EXPONENT * action
        + Q_EXPONENT * (k1 + k2)
    )
    entropy = float(weights @ log_q_over_p)
    cost = float(weights @ (first_shift**2 + true_second_shift**2))
    lhs = float(weights @ action)
    rhs = -cost / (2.0 * Q_EXPONENT) - float(weights @ (k1 + k2)) + entropy / Q_EXPONENT

    wrong_second_shift = slope * z1
    wrong_log_q_over_p = (
        first_shift * z1
        - 0.5 * first_shift**2
        + wrong_second_shift * z2
        - 0.5 * wrong_second_shift**2
        + Q_EXPONENT * action
        + Q_EXPONENT * (k1 + k2)
    )
    wrong_entropy = float(weights @ wrong_log_q_over_p)
    wrong_cost = float(weights @ (first_shift**2 + wrong_second_shift**2))
    wrong_rhs = (
        -wrong_cost / (2.0 * Q_EXPONENT)
        - float(weights @ (k1 + k2))
        + wrong_entropy / Q_EXPONENT
    )
    return {
        "triangular_entropy_chain_residual": abs(lhs - rhs),
        "raw_past_without_pullback_failure": abs(lhs - wrong_rhs),
        "triangular_entropy": entropy,
        "triangular_control_cost": cost,
    }


def gibbs_and_quartic() -> dict[str, float]:
    points, weights = hermite(1, 88)
    u = points[:, 0]
    tangent = 0.63
    score = -0.41
    shift = 0.29
    nonlinear = 0.018 * u**4 + 0.007 * u**2
    interaction = 0.5 * tangent * u**2 - 0.5 * tangent + score * u + nonlinear
    partition = float(weights @ np.exp(-Q_EXPONENT * interaction))
    log_partition = math.log(partition) / Q_EXPONENT
    shifted_u = u + shift
    shifted_nonlinear = 0.018 * shifted_u**4 + 0.007 * shifted_u**2
    shifted_interaction = (
        0.5 * tangent * shifted_u**2
        - 0.5 * tangent
        + score * shifted_u
        + shifted_nonlinear
    )
    averaged = float(weights @ shifted_interaction)
    resolvent = 1.0 / (1.0 + Q_EXPONENT * tangent)
    metric = tangent + 1.0 / Q_EXPONENT
    positive_square = 0.5 * metric * (shift + Q_EXPONENT * resolvent * score) ** 2
    effective_charge = (
        0.5 * Q_EXPONENT * score**2 * resolvent
        - float(weights @ shifted_nonlinear)
        - positive_square
    )
    entropy_integrand = (
        shift * shifted_u
        - 0.5 * shift**2
        + Q_EXPONENT * shifted_interaction
        + Q_EXPONENT * log_partition
    )
    entropy = float(weights @ entropy_integrand)

    tilted = math.sqrt(resolvent) * u - Q_EXPONENT * resolvent * score
    tilted_nonlinear = 0.018 * tilted**4 + 0.007 * tilted**2
    det_two = (1.0 + Q_EXPONENT * tangent) * math.exp(-Q_EXPONENT * tangent)
    partition_formula = (
        det_two ** (-0.5)
        * math.exp(0.5 * Q_EXPONENT**2 * score**2 * resolvent)
        * float(weights @ np.exp(-Q_EXPONENT * tilted_nonlinear))
    )

    rng = np.random.default_rng(26072341)
    quartic_residual = 0.0
    minimum_remainder = float("inf")
    for _ in range(1200):
        coefficient = float(10 ** rng.uniform(-2.0, 0.2))
        base, displacement = rng.normal(size=2)
        shell_tangent = 2.0 * coefficient * base**2
        shell_score = 4.0 * coefficient * base**3
        shell_resolvent = 1.0 / (1.0 + Q_EXPONENT * shell_tangent)
        remainder = coefficient * displacement**2 * (
            (displacement + 2.0 * base) ** 2 + base**2
        )
        shell_square = 0.5 * (shell_tangent + 1.0 / Q_EXPONENT) * (
            displacement + Q_EXPONENT * shell_resolvent * shell_score
        ) ** 2
        shell_charge = (
            0.5 * Q_EXPONENT * shell_score**2 * shell_resolvent
            - remainder
            - shell_square
        )
        oracle = coefficient * base**4 - coefficient * (base + displacement) ** 4
        oracle -= displacement**2 / (2.0 * Q_EXPONENT)
        quartic_residual = max(quartic_residual, abs(shell_charge - oracle))
        minimum_remainder = min(minimum_remainder, remainder)

    return {
        "independent_completion_residual": abs(
            averaged + shift**2 / (2.0 * Q_EXPONENT) + effective_charge
        ),
        "independent_gibbs_pythagoras_residual": abs(
            effective_charge - (log_partition - entropy / Q_EXPONENT)
        ),
        "independent_partition_formula_residual": abs(partition - partition_formula),
        "independent_quartic_residual": quartic_residual,
        "independent_quartic_minimum_remainder": minimum_remainder,
    }


def frame_audit(model: dict[str, Any]) -> dict[str, float]:
    rng = np.random.default_rng(26072342)
    maximum_growth = 0.0
    maximum_lipschitz = 0.0
    for _ in range(600):
        value = rng.normal(size=6)
        increment = rng.normal(size=6)
        old_frames, _ = frames_and_b(value, model)
        new_frames, _ = frames_and_b(value + increment, model)
        for old, new in zip(old_frames, new_frames):
            maximum_growth = max(
                maximum_growth, float(np.linalg.norm(old) / np.linalg.norm(value))
            )
            maximum_lipschitz = max(
                maximum_lipschitz,
                float(np.linalg.norm(new - old) / np.linalg.norm(increment)),
            )

    floor = float(model["rho_regularizer"])
    unit_model = dict(model)
    unit_model["rho_regularizer"] = 1.0
    scaling_residual = 0.0
    for _ in range(30):
        value = rng.normal(size=6)
        _, scaled = frames_and_b(math.sqrt(floor) * value, model)
        _, unit = frames_and_b(value, unit_model)
        scaling_residual = max(scaling_residual, float(np.max(np.abs(scaled / floor - unit))))

    atoms = rng.normal(size=(47, 6))
    atom_weights = rng.uniform(size=47)
    atom_weights /= np.sum(atom_weights)
    x, y, a, b = rng.normal(size=(4, 6))
    gamma = np.diag(np.linspace(0.11, 0.61, 6))
    old_frames, old_b = frames_and_b(x + atoms, model)
    new_frames, new_b = frames_and_b(x + a + atoms, model)
    lhs = 0.5 * np.einsum("n,nij,ij->", atom_weights, new_b, np.outer(y + b, y + b) - gamma)
    lhs -= 0.5 * np.einsum("n,nij,ij->", atom_weights, old_b, np.outer(y, y) - gamma)
    matrix = q_matrix(model)
    rhs_samples = np.zeros(len(atoms))
    for old, new in zip(old_frames, new_frames):
        old_current = np.einsum("nia,i->na", old, y)
        new_current = np.einsum("nia,i->na", new, y + b)
        delta_current = new_current - old_current
        delta_frame = new - old
        rhs_samples += np.einsum("na,ab,nb->n", old_current, matrix, delta_current)
        rhs_samples += 0.5 * np.einsum("na,ab,nb->n", delta_current, matrix, delta_current)
        rhs_samples -= np.einsum("ab,nia,ij,njb->n", matrix, old, gamma, delta_frame)
        rhs_samples -= 0.5 * np.einsum("ab,nia,ij,njb->n", matrix, delta_frame, gamma, delta_frame)
    rhs = float(atom_weights @ rhs_samples)

    coefficients = matrix[0, 0], matrix[0, 1], matrix[1, 1]
    isotropic_trace_coefficient = 6.0 * (
        4.0 * coefficients[0] + 6.0 * coefficients[1] + 3.0 * coefficients[2]
    )
    return {
        "independent_frame_growth_maximum": maximum_growth,
        "independent_frame_lipschitz_maximum": maximum_lipschitz,
        "independent_floor_scaling_residual": scaling_residual,
        "independent_frame_secant_residual": abs(lhs - rhs),
        "zero_floor_isotropic_trace_coefficient": isotropic_trace_coefficient,
        "zero_floor_isotropic_deficit_coefficient": 0.75 * isotropic_trace_coefficient,
    }


def scalar_heat_nogo() -> dict[str, float]:
    shells = np.arange(8, 17)
    sigma = 2.0 ** (-shells)
    gamma = 2.0**shells
    heat = -0.5 * sigma * gamma
    sixth = 15.0 * sigma**3
    return {
        "independent_heat_plateau_deviation": float(np.max(np.abs(heat + 0.5))),
        "independent_heat_absolute_sum": float(np.sum(np.abs(heat))),
        "independent_shell_sixth_sum": float(np.sum(sixth)),
    }


def main() -> int:
    model = parameters()
    martingale = martingale_telescope()
    triangular = triangular_entropy_chain()
    gibbs = gibbs_and_quartic()
    frame = frame_audit(model)
    heat = scalar_heat_nogo()
    checks = {
        "independent_backward_telescope": martingale["independent_telescope_residual"] < 5.0e-12,
        "triangular_entropy_chain": triangular["triangular_entropy_chain_residual"] < 2.0e-12,
        "triangular_pullback_negative_control": triangular["raw_past_without_pullback_failure"] > 1.0e-4,
        "independent_square_completion": gibbs["independent_completion_residual"] < 2.0e-12,
        "independent_gibbs_pythagoras": gibbs["independent_gibbs_pythagoras_residual"] < 2.0e-12,
        "independent_partition_formula": gibbs["independent_partition_formula_residual"] < 2.0e-11,
        "independent_quartic_identity": gibbs["independent_quartic_residual"] < 2.0e-10,
        "independent_quartic_remainder_positive": gibbs["independent_quartic_minimum_remainder"] > -2.0e-13,
        "independent_frame_growth_bound": frame["independent_frame_growth_maximum"] <= math.sqrt(20.0) * (1.0 + 1.0e-12),
        "independent_frame_lipschitz_bound": frame["independent_frame_lipschitz_maximum"] <= math.sqrt(68.0) * (1.0 + 1.0e-12),
        "independent_floor_scaling": frame["independent_floor_scaling_residual"] < 2.0e-13,
        "independent_averaged_frame_secant": frame["independent_frame_secant_residual"] < 3.0e-12,
        "zero_floor_isotropic_trace_positive": frame["zero_floor_isotropic_trace_coefficient"] > 0.2,
        "zero_floor_isotropic_deficit_positive": frame["zero_floor_isotropic_deficit_coefficient"] > 0.15,
        "independent_scalar_heat_plateau": heat["independent_heat_plateau_deviation"] < 1.0e-15,
        "heat_absolute_sum_beats_shell_sixth": heat["independent_heat_absolute_sum"] > 1000.0 * heat["independent_shell_sixth_sum"],
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    assert all(checks.values()), {name: passed for name, passed in checks.items() if not passed}
    computed = {**martingale, **triangular, **gibbs, **frame, **heat}
    payload = {
        "schema": "tect/a13-backward-heat-martingale-square-coupled-independent/1.0",
        "claim": CLAIM,
        "result_id": RESULT_ID,
        "date": "2026-07-23",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {
            "q": Q_EXPONENT,
            "q_authority": str(STRICT_PAST_AUTHORITY.relative_to(REPO)).replace("\\", "/"),
            "q_authority_sha256": digest(STRICT_PAST_AUTHORITY),
            "imports_primary": False,
            "isotropic_diagnostic_floor": "e=0 identity; positive-floor lower-bound coefficient",
        },
        "computed": computed,
        "assertions": checks,
        "assertion_count": len(checks),
        "pass": True,
        "honesty_boundary": (
            "Non-importing finite-dimensional and production-frame audit only. The "
            "zero-floor diagnostic. The global adapted raw-current/Cartan-Jacobi "
            "form bound, arbitrary finite-energy drift extension, and Nelson theorem remain open."
        ),
    }
    atomic_json(OUT, payload)
    print(f"INDEPENDENT {len(checks)}/{len(checks)} PASS")
    print(f"telescope_residual={martingale['independent_telescope_residual']:.3e}")
    print(f"pullback_failure={triangular['raw_past_without_pullback_failure']:.6e}")
    print(RESULT_ID + "-INDEPENDENT-PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
