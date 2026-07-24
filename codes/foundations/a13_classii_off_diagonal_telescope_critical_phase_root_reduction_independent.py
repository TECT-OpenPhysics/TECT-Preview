#!/usr/bin/env python3
"""Non-importing audit of the A13 off-diagonal telescope reduction."""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-independent-off-diagonal-telescope-critical-phase-root-reduction/result.json"
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

# Independent regression inputs and tolerances.
SEED = 31077341
CASES = 96
TOL = 8.0e-10
NONZERO = 1.0e-8

# Independent diagnostic inputs, not theorem data: compare the raw H^{-1/2}
# root with R-063's idealized unshifted H^{-3/10} index only to audit the
# formula p=3/rho.  No adapted two-control gain is inferred.
RAW_ROOT_INDEX = 1.0 / 2.0
R063_DIAGNOSTIC_ROOT_INDEX = 3.0 / 10.0


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def production() -> tuple[np.ndarray, float]:
    parameters = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    q11 = float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2 / denominator
    q12 = float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]) / denominator
    q22 = float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2 / denominator
    return np.asarray([[q11, q12], [q12, q22]], dtype=np.float64), float(parameters["rho_regularizer"])


def realify(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.complex128)
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def generators() -> list[np.ndarray]:
    return [
        realify(np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128)),
        realify(np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128)),
    ]


def phases() -> tuple[np.ndarray, np.ndarray]:
    doublet = np.zeros((6, 6))
    singlet = np.zeros((6, 6))
    for real_index, imaginary_index in ((0, 3), (1, 4)):
        doublet[real_index, imaginary_index] = -1.0
        doublet[imaginary_index, real_index] = 1.0
    singlet[2, 5] = -1.0
    singlet[5, 2] = 1.0
    return doublet, singlet


def frames(z: np.ndarray, floor: float, direction: np.ndarray | None = None) -> tuple[list[np.ndarray], list[np.ndarray] | None]:
    z = np.asarray(z, dtype=np.float64)
    denominator = float(z @ z + floor)
    output: list[np.ndarray] = []
    derivative_output: list[np.ndarray] = []
    for symmetric in generators():
        sz = symmetric @ z
        q_value = float(z @ sz / denominator)
        residual = sz - q_value * z
        output.append(np.stack((2.0 * sz, 2.0 * residual), axis=-1))
        if direction is not None:
            h = np.asarray(direction, dtype=np.float64)
            dq = 2.0 * float(residual @ h) / denominator
            derivative_output.append(np.stack((2.0 * symmetric @ h, 2.0 * symmetric @ h - 2.0 * dq * z - 2.0 * q_value * h), axis=-1))
    return output, derivative_output if direction is not None else None


def derivative(z: np.ndarray, h: np.ndarray, floor: float) -> list[np.ndarray]:
    _, value = frames(z, floor, h)
    assert value is not None
    return value


def current(frame_values: list[np.ndarray], vector: np.ndarray) -> np.ndarray:
    return np.stack([frame.T @ vector for frame in frame_values], axis=0)


def inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(np.einsum("ri,ij,rj->", left, q_matrix, right))


def square(value: np.ndarray, q_matrix: np.ndarray) -> float:
    return inner(value, q_matrix, value)


def shell_audit(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    residuals = {name: 0.0 for name in (
        "e_total", "f_transport", "family_o1", "family_o2", "family_o3", "endpoint",
        "mixed", "control", "gaussian", "full", "p_mix", "restored", "completion",
    )}
    witnesses = {"o1": 0.0, "o2": 0.0, "o3": 0.0}
    for case_index in range(CASES):
        count = 2 + case_index % 3
        z0 = rng.normal(size=6)
        a = [0.22 * rng.normal(size=6) for _ in range(count)]
        b = [0.19 * rng.normal(size=6) for _ in range(count)]
        gaussian = rng.normal(size=6)
        z = [z0]
        for item in a:
            z.append(z[-1] + item)
        m = [frames(item, floor)[0] for item in z]
        d = [derivative(z[j], a[j], floor) for j in range(count)]
        e = [[m[j + 1][r] - m[j][r] - d[j][r] for r in range(3)] for j in range(count)]
        total_a = np.sum(a, axis=0)
        total_b = np.sum(b, axis=0)
        d0 = derivative(z0, total_a, floor)
        e_direct = [m[-1][r] - m[0][r] - d0[r] for r in range(3)]
        f: dict[tuple[int, int], list[np.ndarray]] = {}
        for k in range(count):
            for j in range(k + 1, count):
                after = derivative(z[k + 1], a[j], floor)
                before = derivative(z[k], a[j], floor)
                f[k, j] = [after[r] - before[r] for r in range(3)]
        e_expanded = [sum((e[j][r] for j in range(count)), np.zeros((6, 2))) for r in range(3)]
        for family in f.values():
            for r in range(3):
                e_expanded[r] += family[r]
        residuals["e_total"] = max(residuals["e_total"], *(float(np.linalg.norm(e_expanded[r] - e_direct[r])) for r in range(3)))
        for j in range(count):
            f_sum = [sum((f[k, j][r] for k in range(j)), np.zeros((6, 2))) for r in range(3)]
            dj = derivative(z[j], a[j], floor)
            db = derivative(z0, a[j], floor)
            residuals["f_transport"] = max(residuals["f_transport"], *(float(np.linalg.norm(f_sum[r] - dj[r] + db[r])) for r in range(3)))

        w = [current(item, gaussian) for item in m]
        diagonal = sum(inner(w[j], q_matrix, current(e[j], b[j])) for j in range(count))
        o1 = sum(inner(w[0] - w[j], q_matrix, current(e[j], b[j])) for j in range(count))
        o2 = sum(inner(w[0], q_matrix, current(e[j], b[ell])) for j in range(count) for ell in range(count) if ell != j)
        o3 = sum(inner(w[0], q_matrix, current(family, item)) for family in f.values() for item in b)
        linear = inner(w[0], q_matrix, current(d0, total_b))
        endpoint = inner(w[0], q_matrix, current([m[-1][r] - m[0][r] for r in range(3)], total_b))
        residuals["family_o1"] = max(residuals["family_o1"], abs(diagonal + o1 - sum(inner(w[0], q_matrix, current(e[j], b[j])) for j in range(count))))
        residuals["family_o2"] = max(residuals["family_o2"], abs(diagonal + o1 + o2 - sum(inner(w[0], q_matrix, current(e[j], b[ell])) for j in range(count) for ell in range(count))))
        residuals["family_o3"] = max(residuals["family_o3"], abs(linear + o3 - sum(inner(w[0], q_matrix, current(derivative(z[j], a[j], floor), b[ell])) for j in range(count) for ell in range(count))))
        residuals["endpoint"] = max(residuals["endpoint"], abs(linear + diagonal + o1 + o2 + o3 - endpoint))
        witnesses["o1"] = max(witnesses["o1"], abs(o1))
        witnesses["o2"] = max(witnesses["o2"], abs(o2))
        witnesses["o3"] = max(witnesses["o3"], abs(o3))

        accumulated = np.zeros(6)
        c = []
        for j in range(count + 1):
            c.append(current(m[j], accumulated))
            if j < count:
                accumulated += b[j]
        r_cross = sum(inner(c[j + 1], q_matrix, w[j + 1]) - inner(c[j], q_matrix, w[j]) for j in range(count))
        r_control = sum(0.5 * (square(c[j + 1], q_matrix) - square(c[j], q_matrix)) for j in range(count))
        r_gaussian = sum(0.5 * (square(w[j + 1], q_matrix) - square(w[j], q_matrix)) for j in range(count))
        delta_w = w[-1] - w[0]
        s_c = inner(w[0], q_matrix, current(m[0], total_b))
        s_g = inner(w[0], q_matrix, current(d0, gaussian))
        n_g = inner(w[0], q_matrix, current(e_direct, gaussian))
        residuals["mixed"] = max(residuals["mixed"], abs(r_cross - inner(c[-1], q_matrix, w[-1])))
        residuals["control"] = max(residuals["control"], abs(r_control - 0.5 * square(c[-1], q_matrix)))
        residuals["gaussian"] = max(residuals["gaussian"], abs(r_gaussian - s_g - n_g - 0.5 * square(delta_w, q_matrix)))
        lhs = linear + n_g + diagonal + o1 + o2 + o3 + 0.5 * square(delta_w + c[-1], q_matrix)
        rhs = r_gaussian + r_cross + r_control - s_g - s_c
        residuals["full"] = max(residuals["full"], abs(lhs - rhs))

        n_c = inner(w[0], q_matrix, current(e_direct, total_b))
        p_a = inner(c[-1], q_matrix, w[-1]) - inner(current(m[0], total_b), q_matrix, w[0]) - linear + 0.5 * square(c[-1], q_matrix)
        p_b = n_c + inner(c[-1], q_matrix, delta_w) + 0.5 * square(c[-1], q_matrix)
        restored = s_c + linear + p_a
        terminal = inner(c[-1], q_matrix, w[-1]) + 0.5 * square(c[-1], q_matrix)
        residuals["p_mix"] = max(residuals["p_mix"], abs(p_a - p_b))
        residuals["restored"] = max(residuals["restored"], abs(restored - terminal))
        residuals["completion"] = max(residuals["completion"], abs(0.5 * square(w[-1], q_matrix) + restored - 0.5 * square(w[-1] + c[-1], q_matrix)))
    return {"max_residuals": residuals, "off_diagonal_witnesses": witnesses}


def explicit_projector(value: np.ndarray) -> np.ndarray:
    j_doublet, j_singlet = phases()
    u_sq = float(value[[0, 1, 3, 4]] @ value[[0, 1, 3, 4]])
    s_sq = float(value[[2, 5]] @ value[[2, 5]])
    if u_sq < 1.0e-14:
        return np.eye(6)
    n_doublet = j_doublet @ value
    projector = np.outer(n_doublet, n_doublet) / u_sq
    if s_sq < 1.0e-14:
        projector[2, 2] += 1.0
        projector[5, 5] += 1.0
    else:
        n_singlet = j_singlet @ value
        projector += np.outer(n_singlet, n_singlet) / s_sq
    return projector


def phase_audit(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    strata = (
        np.asarray([0.8, -0.4, 0.7, 1.1, 0.3, -0.5]),
        np.asarray([0.8, -0.4, 0.0, 1.1, 0.3, 0.0]),
        np.asarray([0.0, 0.0, 0.7, 0.0, 0.0, -0.5]),
        np.zeros(6),
    )
    projector_residual = 0.0
    projector_idempotence = 0.0
    ranks: list[int] = []
    for value in strata:
        frame_values, _ = frames(value, floor)
        stacked = np.concatenate(frame_values, axis=1)
        projector = explicit_projector(value)
        svd_projector = np.eye(6) - stacked @ np.linalg.pinv(stacked)
        projector_residual = max(projector_residual, float(np.linalg.norm(projector - svd_projector)))
        projector_idempotence = max(projector_idempotence, float(np.linalg.norm(projector @ projector - projector)))
        ranks.append(int(round(float(np.trace(projector)))))

    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    x = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a = x - z
    gaussian = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    j_doublet, _ = phases()
    n = j_doublet @ x
    m0, d = frames(z, floor, a)
    mt, _ = frames(x, floor)
    assert d is not None
    e = [mt[r] - m0[r] - d[r] for r in range(3)]
    w = current(m0, gaussian)
    k_n = sum((e[r] @ q_matrix @ w[r] for r in range(3)), np.zeros(6))
    k_l = sum((d[r] @ q_matrix @ w[r] for r in range(3)), np.zeros(6))
    k_s = sum((m0[r] @ q_matrix @ w[r] for r in range(3)), np.zeros(6))

    e_formula = 0.0
    k_formula = np.zeros(6)
    eps_beta = 0.0
    ell_beta = 0.0
    for r, symmetric in enumerate(generators()):
        denominator = float(z @ z + floor)
        q0 = float(z @ (symmetric @ z) / denominator)
        residual = symmetric @ z - q0 * z
        ell = 2.0 * float(residual @ a) / denominator
        qt = float(x @ (symmetric @ x) / float(x @ x + floor))
        eps = qt - q0 - ell
        prediction = -2.0 * (eps * x + ell * a)
        e_formula = max(e_formula, float(np.linalg.norm(e[r][:, 0])), float(np.linalg.norm(e[r][:, 1] - prediction)))
        beta = float((q_matrix @ w[r])[1])
        eps_beta += beta * eps
        ell_beta += beta * ell
    k_formula = -2.0 * (eps_beta * x + ell_beta * a)
    return {
        "projector_residual": projector_residual,
        "projector_idempotence": projector_idempotence,
        "projector_ranks_encoded": float(sum((index + 1) * rank for index, rank in enumerate(ranks))),
        "expected_ranks_encoded": float(sum((index + 1) * rank for index, rank in enumerate((2, 3, 6, 6)))),
        "kernel_residual": float(np.linalg.norm(np.concatenate(mt, axis=1).T @ n)),
        "e_formula": e_formula,
        "k_formula": float(np.linalg.norm(k_n - k_formula)),
        "nonlinear_slope": float(n @ k_n),
        "linear_product": float((n @ k_n) * (n @ k_l)),
        "restored_cancellation": abs(float(n @ (k_n + k_l + k_s))),
    }


def exponent_audit() -> dict[str, float]:
    theta_o2 = 1.0 / 4.0
    theta_o3 = 1.0 / 2.0
    sigma = R063_DIAGNOSTIC_ROOT_INDEX
    rho = RAW_ROOT_INDEX - sigma
    return {
        "o2_decay": 2.0 * theta_o2 - 0.5,
        "o2_budget": 5.0 / 6.0 + 2.0 * theta_o2 / 3.0,
        "o3_decay": theta_o3 - 0.5,
        "o3_budget": 5.0 / 6.0 + theta_o3 / 3.0,
        "rho": rho,
        "sigma": sigma,
        "moment": 6.0 / (1.0 - 2.0 * sigma),
        "moment_target": 3.0 / rho,
    }


def main() -> int:
    q_matrix, floor = production()
    shell = shell_audit(q_matrix, floor)
    phase = phase_audit(q_matrix, floor)
    exponent = exponent_audit()
    rows: list[dict[str, Any]] = []
    add(rows, "independent_q_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "> 0")
    for name, value in shell["max_residuals"].items():
        add(rows, f"independent_{name}", value < TOL, value, TOL)
    add(rows, "independent_all_offdiagonal_nonzero", min(shell["off_diagonal_witnesses"].values()) > NONZERO, shell["off_diagonal_witnesses"], f"> {NONZERO}")
    for name in ("projector_residual", "projector_idempotence", "kernel_residual", "e_formula", "k_formula", "restored_cancellation"):
        add(rows, f"independent_{name}", phase[name] < TOL, phase[name], TOL)
    add(rows, "independent_rank_strata", phase["projector_ranks_encoded"] == phase["expected_ranks_encoded"], phase["projector_ranks_encoded"], phase["expected_ranks_encoded"])
    add(rows, "independent_nonlinear_phase_nonzero", abs(phase["nonlinear_slope"]) > NONZERO, phase["nonlinear_slope"], f"abs > {NONZERO}")
    add(rows, "independent_linear_reinforces", phase["linear_product"] > 0.0, phase["linear_product"], "> 0")
    add(rows, "independent_o2_endpoint", abs(exponent["o2_decay"]) < TOL and abs(exponent["o2_budget"] - 1.0) < TOL, [exponent["o2_decay"], exponent["o2_budget"]], [0.0, 1.0])
    add(rows, "independent_o3_endpoint", abs(exponent["o3_decay"]) < TOL and abs(exponent["o3_budget"] - 1.0) < TOL, [exponent["o3_decay"], exponent["o3_budget"]], [0.0, 1.0])
    add(rows, "independent_gain_moment", abs(exponent["moment"] - exponent["moment_target"]) < TOL, exponent["moment"], exponent["moment_target"])
    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-off-diagonal-telescope-critical-phase-root-independent/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {"random_seed": SEED, "random_cases": CASES, "floor": floor, "q_matrix": q_matrix.tolist()},
        "derived": {"shell": shell, "phase": phase, "critical_route": exponent},
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": "Non-importing finite-dimensional production audit of the exact R-073 algebra and scoped exponent conflict only; no stochastic terminal coercivity or downstream A13 theorem is asserted.",
    }
    atomic_json(OUT, payload)
    print(f"Independent assertions: {sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print(f"Independent full residual: {shell['max_residuals']['full']:.6g}")
    print(f"Independent phase cancellation: {phase['restored_cancellation']:.6g}")
    print("A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-INDEPENDENT-PASS" if passed else "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-INDEPENDENT-FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
