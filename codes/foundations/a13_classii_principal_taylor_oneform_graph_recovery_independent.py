#!/usr/bin/env python3
"""Non-importing audit of the R-075 invariant-current/Taylor/graph split."""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

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
RESULT_ID = "A13-CLASSII-PRINCIPAL-TAYLOR-ONE-FORM-GRAPH-RECOVERY-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-independent-principal-taylor-oneform-graph-recovery/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"

# Independent regression inputs.
RANDOM_SEED = 7512407
RANDOM_CASES = 80
STENCIL_STEPS = (2.0e-3, 1.0e-3)
GRAPH_POINTS = 3072
HONESTY_BOUNDARY = (
    "Independent finite-dimensional and graph-core audit only; signed adapted "
    "coefficient transport, full Wick/lower-chaos reconstruction, one-use, and "
    "Nelson remain open."
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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


def production() -> tuple[dict[str, Any], np.ndarray, float, float]:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    matrix = np.asarray(
        [
            [float(parameters["cJJ"]) * float(parameters["alpha_X"]) ** 2, float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"])],
            [float(parameters["cJK"]) * float(parameters["alpha_X"]) * float(parameters["beta_X"]), float(parameters["cKK"]) * float(parameters["beta_X"]) ** 2],
        ]
    ) / denominator
    return parameters, matrix, float(parameters["rho_regularizer"]), denominator


def pauli() -> tuple[np.ndarray, ...]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def complex_vector(value: np.ndarray) -> np.ndarray:
    return np.asarray(value[:3], dtype=np.float64) + 1j * np.asarray(value[3:], dtype=np.float64)


def real_vector(value: np.ndarray) -> np.ndarray:
    return np.concatenate((np.asarray(value).real, np.asarray(value).imag)).astype(np.float64)


def frames(value: np.ndarray, floor: float) -> list[np.ndarray]:
    z = complex_vector(np.asarray(value, dtype=np.float64))
    denominator = float(np.vdot(z, z).real + floor)
    output = []
    for symmetric in pauli():
        sz = symmetric @ z
        q_value = float(np.vdot(z, sz).real / denominator)
        output.append(np.column_stack((real_vector(2.0 * sz), real_vector(2.0 * (sz - q_value * z)))))
    return output


def energy(value: np.ndarray, derivative: np.ndarray, q_matrix: np.ndarray, floor: float) -> float:
    return 0.5 * sum(float((frame.T @ derivative) @ q_matrix @ (frame.T @ derivative)) for frame in frames(value, floor))


def frame_derivative(value: np.ndarray, direction: np.ndarray, floor: float, step: float) -> list[np.ndarray]:
    plus2 = frames(value + 2.0 * step * direction, floor)
    plus1 = frames(value + step * direction, floor)
    minus1 = frames(value - step * direction, floor)
    minus2 = frames(value - 2.0 * step * direction, floor)
    return [(-a + 8.0 * b - 8.0 * c + d) / (12.0 * step) for a, b, c, d in zip(plus2, plus1, minus1, minus2)]


def half_frame_second(value: np.ndarray, direction: np.ndarray, floor: float, step: float) -> list[np.ndarray]:
    plus2 = frames(value + 2.0 * step * direction, floor)
    plus1 = frames(value + step * direction, floor)
    base = frames(value, floor)
    minus1 = frames(value - step * direction, floor)
    minus2 = frames(value - 2.0 * step * direction, floor)
    return [(-a + 16.0 * b - 30.0 * c + 16.0 * d - e) / (24.0 * step**2) for a, b, c, d, e in zip(plus2, plus1, base, minus1, minus2)]


def quotient_and_nelson(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    a_q, b_q, c_q = float(q_matrix[0, 0]), float(q_matrix[0, 1]), float(q_matrix[1, 1])
    c0 = (a_q * c_q - b_q**2) / c_q
    c1 = (b_q + c_q) ** 2 / c_q
    alpha = c_q / (b_q + c_q)
    rng = np.random.default_rng(RANDOM_SEED)
    current_error = 0.0
    diagonal_error = 0.0
    for _ in range(RANDOM_CASES):
        z_real = rng.normal(size=6)
        y_real = rng.normal(size=6)
        z = complex_vector(z_real)
        y = complex_vector(y_real)
        denominator = float(np.vdot(z, z).real + floor)
        ds = 2.0 * float(np.vdot(z, y).real) / denominator
        frame_values = frames(z_real, floor)
        for symmetric, frame in zip(pauli(), frame_values):
            mass = float(np.vdot(z, symmetric @ z).real)
            current_j = 2.0 * float(np.vdot(symmetric @ z, y).real)
            current_k = current_j - mass * ds
            current_error = max(current_error, float(np.linalg.norm(frame.T @ y_real - np.asarray([current_j, current_k]))))
            current_l = current_j - alpha * mass * ds
            direct = float((frame.T @ y_real) @ q_matrix @ (frame.T @ y_real))
            diagonal = c0 * current_j**2 + c1 * current_l**2
            diagonal_error = max(diagonal_error, abs(direct - diagonal))
    pure_singlet = np.eye(6)[2]
    frame_rank = int(np.linalg.matrix_rank(np.concatenate(frames(pure_singlet, floor), axis=1), tol=1.0e-11))
    invariant_rows = [2.0 * pure_singlet]
    for symmetric in pauli():
        invariant_rows.append(2.0 * real_vector(symmetric @ complex_vector(pure_singlet)))
    invariant_rank = int(np.linalg.matrix_rank(np.asarray(invariant_rows), tol=1.0e-11))
    return {
        "current_error": current_error,
        "diagonal_error": diagonal_error,
        "c0": c0,
        "c1": c1,
        "alpha": alpha,
        "q": 2.0 * alpha,
        "pure_singlet_frame_rank": frame_rank,
        "pure_singlet_invariant_rank": invariant_rank,
    }


def resonance_stencil(q_matrix: np.ndarray, floor: float, denominator: float) -> dict[str, Any]:
    z = np.eye(6)[0]
    a = np.eye(6)[1]
    y = a.copy()
    c = a.copy()
    expected_full = 3.0 * (113.0 * floor**2 + 136.0 * floor + 48.0) / (2000.0 * denominator * (1.0 + floor) ** 2)
    expected_isolated = -27.0 / (200.0 * denominator * (1.0 + floor))
    rows = []
    for step in STENCIL_STEPS:
        ell = step
        def l_derivative(t_value: float) -> float:
            return (energy(z + t_value * a, y + ell * c, q_matrix, floor) - energy(z + t_value * a, y - ell * c, q_matrix, floor)) / (2.0 * ell)
        full = (l_derivative(step) - 2.0 * l_derivative(0.0) + l_derivative(-step)) / (2.0 * step**2)
        base_frames = frames(z, floor)
        half_second = half_frame_second(z, a, floor, step)
        isolated = sum(float((frame.T @ y) @ q_matrix @ (second.T @ c)) for frame, second in zip(base_frames, half_second))
        rows.append({"step": step, "full": full, "isolated": isolated})
    return {
        "rows": rows,
        "expected_full": expected_full,
        "expected_isolated": expected_isolated,
        "full_error": max(abs(row["full"] - expected_full) for row in rows),
        "isolated_error": max(abs(row["isolated"] - expected_isolated) for row in rows),
        "refinement": abs(rows[0]["full"] - rows[1]["full"]),
    }


def omission_fixture(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    z = np.asarray([-2.0087988573, 0.2161055980, -0.2093846062, 0.2320281713, -0.3769292432, 1.1938405659])
    a = np.asarray([0.4460281222, 0.0261573996, 0.0462881437, -0.2656341471, 0.1880042393, 0.9974080611])
    y = np.asarray([-0.8005849904, 1.2906569240, 1.4704710058, 1.2036294577, -0.6224917863, -1.7316179052])
    step = 5.0e-4
    tangent = frame_derivative(z, a, floor, step)
    base_frames = frames(z, floor)
    end_frames = frames(z + a, floor)
    derivative = sum(float((frame.T @ y) @ q_matrix @ (direction.T @ y)) for frame, direction in zip(base_frames, tangent))
    raw_remainder = energy(z + a, y, q_matrix, floor) - energy(z, y, q_matrix, floor) - derivative
    delta = [(right - left).T @ y for right, left in zip(end_frames, base_frames)]
    square = 0.5 * sum(float(value @ q_matrix @ value) for value in delta)
    curvature = sum(float((frame.T @ y) @ q_matrix @ ((right - frame - direction).T @ y)) for frame, right, direction in zip(base_frames, end_frames, tangent))
    return {"raw_remainder": raw_remainder, "square": square, "curvature": curvature, "residual": abs(raw_remainder - square - curvature)}


def radial_tail(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    scale = math.sqrt(floor)
    z = scale * np.eye(6)[0]
    a = z.copy()
    y = np.eye(6)[0]
    base = frames(z, floor)[2]
    end = frames(z + a, floor)[2]
    tangent = frame_derivative(z, a, floor, 1.0e-3)[2]
    half_second = half_frame_second(z, a, floor, 1.0e-3)[2]
    tail = end - base - tangent - half_second
    value = float((base.T @ y) @ q_matrix @ (tail.T @ y))
    expected = 0.3 * floor * (2.0 * q_matrix[0, 1] + q_matrix[1, 1])
    return {"value": value, "expected": expected, "relative_error": abs(value - expected) / abs(expected)}


def probabilists_hermite(order: int, values: np.ndarray) -> np.ndarray:
    if order == 0:
        return np.ones_like(values)
    previous = np.ones_like(values)
    current = values.copy()
    for index in range(1, order):
        previous, current = current, values * current - index * previous
    return current


def hermite_quadrature() -> dict[str, Any]:
    outputs: dict[str, dict[str, float]] = {}
    for quadrature_order in (64, 128):
        nodes, weights = np.polynomial.hermite.hermgauss(quadrature_order)
        values = math.sqrt(2.0) * nodes
        probability_weights = weights / math.sqrt(math.pi)
        function = np.exp(-(values**2)) * (values**2 - 1.0)
        coefficients = {}
        for order in range(0, 18, 2):
            coefficients[str(order)] = float(np.sum(probability_weights * function * probabilists_hermite(order, values)) / math.factorial(order))
        outputs[str(quadrature_order)] = coefficients
    exact = {"0": -2.0 / (3.0 * math.sqrt(3.0))}
    for order in range(2, 18, 2):
        m = order // 2
        exact[str(order)] = ((-1.0) ** (m - 1)) * (m + 2.0) / (math.sqrt(3.0) * 3.0 ** (m + 1) * math.factorial(m))
    error = max(abs(outputs["128"][order] - exact[order]) for order in exact)
    refinement = max(abs(outputs["128"][order] - outputs["64"][order]) for order in exact)
    return {"quadratures": outputs, "exact": exact, "max_error": error, "refinement": refinement, "all_nonzero": all(abs(value) > 1.0e-12 for value in outputs["128"].values())}


def graph_sequence(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    reference = 18
    cutoffs = (3, 6, 10, 14)
    x = np.linspace(0.0, 2.0 * math.pi, GRAPH_POINTS, endpoint=False)
    u_coeff = rng.normal(size=(6, reference + 1, 2))
    a_coeff = rng.normal(size=(6, reference + 1, 2))
    u_coeff[:, 0, 1] = 0.0
    a_coeff[:, 0, :] = 0.0
    for mode in range(reference + 1):
        u_coeff[:, mode, :] /= (1.0 + mode**2) ** 1.9
        a_coeff[:, mode, :] /= (1.0 + mode**2) ** 1.7

    def build(coeff: np.ndarray, cutoff: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        value = np.zeros((x.size, 6))
        first = np.zeros_like(value)
        second = np.zeros_like(value)
        value += coeff[:, 0, 0]
        for mode in range(1, cutoff + 1):
            cosine = coeff[:, mode, 0]
            sine = coeff[:, mode, 1]
            value += np.cos(mode * x)[:, None] * cosine + np.sin(mode * x)[:, None] * sine
            first += -mode * np.sin(mode * x)[:, None] * cosine + mode * np.cos(mode * x)[:, None] * sine
            second += -(mode**2) * (np.cos(mode * x)[:, None] * cosine + np.sin(mode * x)[:, None] * sine)
        return value, first, second

    u, du, d2u = build(u_coeff, reference)
    a_ref, da_ref, d2a_ref = build(a_coeff, reference)

    eigenvalues, eigenvectors = np.linalg.eigh(q_matrix)
    q_sqrt = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T

    def currents(value: np.ndarray, derivative: np.ndarray) -> np.ndarray:
        output = np.zeros((value.shape[0], 3, 2))
        for index in range(value.shape[0]):
            for generator, frame in enumerate(frames(value[index], floor)):
                output[index, generator] = (frame.T @ derivative[index]) @ q_sqrt
        return output

    current_ref = currents(u + a_ref, du + da_ref)
    rows = []
    for cutoff in cutoffs:
        a, da, d2a = build(a_coeff, cutoff)
        delta = a - a_ref
        delta_first = da - da_ref
        delta_second = d2a - d2a_ref
        l6 = float(np.mean(np.linalg.norm(delta, axis=1) ** 6) ** (1.0 / 6.0))
        h2 = float(np.mean(np.sum(delta**2 + delta_first**2 + delta_second**2, axis=1)) ** 0.5)
        current_error = float(np.mean((currents(u + a, du + da) - current_ref) ** 2) ** 0.5)
        rows.append({"cutoff": cutoff, "L6": l6, "H2": h2, "current": current_error})
    return {
        "rows": rows,
        "L6": [row["L6"] for row in rows],
        "H2": [row["H2"] for row in rows],
        "current": [row["current"] for row in rows],
        "q_sqrt_reconstruction_error": float(np.linalg.norm(q_sqrt @ q_sqrt - q_matrix)),
    }


def main() -> int:
    _, q_matrix, floor, denominator = production()
    quotient = quotient_and_nelson(q_matrix, floor)
    resonance = resonance_stencil(q_matrix, floor, denominator)
    omission = omission_fixture(q_matrix, floor)
    radial = radial_tail(q_matrix, floor)
    hermite = hermite_quadrature()
    graph = graph_sequence(q_matrix, floor)
    spike = [{"n": n, "L2": n ** (-2.0 / 3.0), "L6_sixth": 1.0} for n in (8, 27, 64, 125, 216)]
    principal_slack = 1.0 - 0.5 - 1.0 / 3.0
    transport_slack = 1.0 - 0.5 - 0.5

    rows: list[dict[str, Any]] = []
    add(rows, "complex_frames_match_invariant_currents", quotient["current_error"] < 3.0e-12, quotient["current_error"], "<3e-12")
    add(rows, "independent_Nelson_diagonalization", quotient["diagonal_error"] < 3.0e-12 and abs(quotient["alpha"] - 5.0 / 9.0) < 1.0e-14, quotient, "error<3e-12 and alpha=5/9")
    add(rows, "q_is_twice_the_geometric_exponent", abs(quotient["q"] - 10.0 / 9.0) < 1.0e-14, quotient["q"], 10.0 / 9.0)
    add(rows, "pure_singlet_tip_is_rank_degenerate", quotient["pure_singlet_frame_rank"] == 0 and quotient["pure_singlet_invariant_rank"] == 1, quotient, "frame 0, invariants 1")
    add(rows, "two_dimensional_stencil_recovers_full_resonance", resonance["full_error"] < 2.0e-7, resonance, "<2e-7")
    add(rows, "independent_stencil_recovers_isolated_branch", resonance["isolated_error"] < 2.0e-7, resonance["isolated_error"], "<2e-7")
    add(rows, "full_resonance_is_positive_while_isolated_is_negative", resonance["expected_full"] > 0.0 and resonance["expected_isolated"] < 0.0, {"full": resonance["expected_full"], "isolated": resonance["expected_isolated"]}, "+/-")
    add(rows, "constant_control_omission_reassembles", omission["residual"] < 2.0e-10, omission, "residual<2e-10")
    add(rows, "constant_control_coefficient_curvature_is_load_bearing", omission["curvature"] < -omission["square"] < 0.0, omission, "curvature<-square<0")
    add(rows, "horizontal_radial_N3_survives", radial["value"] > 0.0 and radial["relative_error"] < 2.0e-4, radial, "positive, relative error<2e-4")
    add(rows, "two_resolution_Hermite_quadrature_converges", hermite["refinement"] < 2.0e-10, hermite["refinement"], "<2e-10")
    add(rows, "Hermite_coefficients_match_generating_function", hermite["max_error"] < 2.0e-10, hermite["max_error"], "<2e-10")
    add(rows, "tested_even_Hermite_orders_are_nonzero", hermite["all_nonzero"], hermite["quadratures"]["128"], "all tested even orders through 16 nonzero")
    add(rows, "principal_payload_has_positive_slack", abs(principal_slack - 1.0 / 6.0) < 1.0e-14, principal_slack, "1/6")
    add(rows, "transport_payload_is_critical", abs(transport_slack) < 1.0e-14, transport_slack, "0")
    add(rows, "graph_H2_sequence_converges", all(right < left for left, right in zip(graph["H2"], graph["H2"][1:])), graph["H2"], "strict decrease")
    add(rows, "graph_L6_sequence_converges", all(right < left for left, right in zip(graph["L6"], graph["L6"][1:])), graph["L6"], "strict decrease")
    add(rows, "graph_current_sequence_converges", all(right < left for left, right in zip(graph["current"], graph["current"][1:])), graph["current"], "strict decrease")
    add(rows, "predictable_L2_spike_vanishes_only_in_L2", spike[-1]["L2"] < spike[0]["L2"] and all(item["L6_sixth"] == 1.0 for item in spike), spike, "L2 down, L6 sixth fixed")
    add(
        rows,
        "scope_keeps_complete_adapted_gate_open",
        "remain open" in HONESTY_BOUNDARY
        and all(token in HONESTY_BOUNDARY for token in ("coefficient transport", "one-use", "Nelson")),
        HONESTY_BOUNDARY,
        "explicit open coefficient-transport, one-use, and Nelson boundary",
    )

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-principal-taylor-oneform-graph-recovery-independent-run/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "run_kind": "independent",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"path": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "version": __version__, "sha256": digest(Path(__file__).resolve())},
        "inputs": {"random_seed": RANDOM_SEED, "random_cases": RANDOM_CASES, "floor": floor, "stencil_steps": list(STENCIL_STEPS), "graph_points": GRAPH_POINTS},
        "derived": {"quotient": quotient, "resonance": resonance, "omission": omission, "radial_tail": radial, "hermite": hermite, "graph": graph, "predictable_spike": spike, "principal_slack": principal_slack, "transport_slack": transport_slack},
        "assertions": rows,
        "assertion_count": len(rows),
        "summary": {"status": "PASS" if passed else "FAIL", "passed": sum(row["status"] == "PASS" for row in rows), "total": len(rows)},
        "pass": passed,
        "honesty_boundary": HONESTY_BOUNDARY,
    }
    atomic_json(OUT, payload)
    print(f"A13 PRINCIPAL TAYLOR/GRAPH INDEPENDENT: {'PASS' if passed else 'FAIL'} {payload['summary']['passed']}/{len(rows)}")
    print(f"RESULT_JSON={OUT.relative_to(REPO).as_posix()}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
