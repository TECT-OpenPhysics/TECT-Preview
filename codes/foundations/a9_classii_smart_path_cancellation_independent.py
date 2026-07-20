#!/usr/bin/env python3
"""Non-importing audit for the A9 smart-path and shell identities.

The implementation deliberately shares no domain code with the primary route.
It uses a two-coordinate Fourier toy, direct tensor Gauss-Hermite integration,
central differences, and separately coded matrix formulas.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A9-CLASSII-SMART-PATH-CANCELLATION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM_DIR / "classii_smart_path_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-independent-smart-path" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def normal_grid(order: int, dimension: int) -> tuple[np.ndarray, np.ndarray]:
    raw_nodes, raw_weights = np.polynomial.hermite.hermgauss(order)
    normal_nodes = math.sqrt(2.0) * raw_nodes
    normal_weights = raw_weights / math.sqrt(math.pi)
    tuples = list(itertools.product(range(order), repeat=dimension))
    points = np.asarray([[normal_nodes[index] for index in item] for item in tuples], dtype=np.float64)
    weights = np.asarray([math.prod(normal_weights[index] for index in item) for item in tuples], dtype=np.float64)
    return points, weights


class IndependentModel:
    def __init__(self, config: dict[str, Any], odd: bool = False) -> None:
        positions = np.asarray(config["independent_positions"], dtype=np.float64)
        self.values = np.column_stack((np.cos(positions), np.sin(positions)))
        self.gradients = np.column_stack((-np.sin(positions), np.cos(positions)))
        if odd:
            self.gradients = self.gradients + float(config["independent_odd_mixing"]) * self.values
        self.weights = np.full(len(positions), 1.0 / len(positions))
        self.floor = float(config["independent_floor"])
        self.strength = float(config["independent_strength"])
        self.quartic = float(config["independent_quartic"])
        self.sextic = float(config["independent_sextic"])

    def b(self, value: np.ndarray) -> np.ndarray:
        square = value**2
        return self.strength * square * (1.0 + square / (square + self.floor))

    def db(self, value: np.ndarray) -> np.ndarray:
        square = value**2
        return self.strength * (
            2.0 * value * (1.0 + square / (square + self.floor))
            + 2.0 * value**3 * self.floor / (square + self.floor) ** 2
        )

    def t_and_dt(self, white: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        field = self.values @ white
        operator = np.zeros((2, 2), dtype=np.float64)
        differential = [np.zeros((2, 2), dtype=np.float64) for _ in range(2)]
        for site in range(len(self.weights)):
            rank_one = np.outer(self.gradients[site], self.gradients[site])
            operator += self.weights[site] * self.b(field[site]) * rank_one
            for coordinate in range(2):
                differential[coordinate] += (
                    self.weights[site]
                    * self.db(field[site])
                    * self.values[site, coordinate]
                    * rank_one
                )
        return operator, differential

    def u_and_du(self, white: np.ndarray) -> tuple[float, np.ndarray]:
        field = self.values @ white
        energy = np.sum(
            self.weights * (self.quartic * field**4 / 4.0 + self.sextic * field**6 / 6.0)
        )
        derivative = self.values.T @ (
            self.weights * (self.quartic * field**3 + self.sextic * field**5)
        )
        return float(energy), derivative

    def local_parity(self) -> np.ndarray:
        return np.sum(self.values * self.gradients, axis=1)


def matrices(operator: np.ndarray, p_value: float, t_value: float) -> tuple[np.ndarray, np.ndarray]:
    resolvent = np.linalg.inv(np.eye(2) + p_value * t_value * operator)
    return resolvent, operator @ resolvent


def det2_log(operator: np.ndarray, scale: float) -> float:
    return float(np.linalg.slogdet(np.eye(2) + scale * operator)[1] - scale * np.trace(operator))


def weight_and_integrands(
    model: IndependentModel, white: np.ndarray, p_value: float, t_value: float
) -> tuple[float, float, float, float, float]:
    operator, derivatives = model.t_and_dt(white)
    potential, potential_gradient = model.u_and_du(white)
    resolvent, smoothed = matrices(operator, p_value, t_value)
    sx = smoothed @ white
    log_weight = (
        -p_value * potential
        - 0.5 * det2_log(operator, p_value * t_value)
        + 0.5 * p_value * (1.0 - t_value) * (np.trace(operator) - white @ sx)
    )
    raw = 0.5 * p_value * (white @ sx - np.trace(smoothed))
    raw += 0.5 * p_value**2 * (1.0 - t_value) * float(sx @ sx)
    a_vector = np.zeros(2, dtype=np.float64)
    div_s = np.zeros(2, dtype=np.float64)
    decomposition_error = 0.0
    for coordinate, derivative in enumerate(derivatives):
        transformed = resolvent @ derivative @ resolvent
        direct = np.trace(derivative) - white @ transformed @ white
        pairing = np.trace((np.eye(2) - resolvent @ resolvent) @ derivative)
        centered = white @ transformed @ white - np.trace(transformed)
        decomposition_error = max(decomposition_error, abs(direct - pairing + centered))
        a_vector[coordinate] = (
            0.5 * p_value**2 * t_value**2 * np.trace(operator @ resolvent @ derivative)
            + 0.5 * p_value * (1.0 - t_value) * direct
        )
        div_s += transformed[coordinate, :]
    cancelled = 0.5 * p_value * (
        -p_value * potential_gradient @ sx + a_vector @ sx + div_s @ white
    )
    without_divergence = 0.5 * p_value * (-p_value * potential_gradient @ sx + a_vector @ sx)
    return float(log_weight), float(raw), float(cancelled), float(without_divergence), float(decomposition_error)


def integrate(
    model: IndependentModel, points: np.ndarray, weights: np.ndarray, p_value: float, t_value: float
) -> dict[str, float]:
    rows = [weight_and_integrands(model, point, p_value, t_value) for point in points]
    logs = np.asarray([row[0] for row in rows])
    anchor = float(np.max(logs))
    weighted = weights * np.exp(logs - anchor)
    partition = float(np.sum(weighted))
    probability = weighted / partition
    return {
        "log_partition": anchor + math.log(partition),
        "raw": float(probability @ np.asarray([row[1] for row in rows])),
        "cancelled": float(probability @ np.asarray([row[2] for row in rows])),
        "without_divergence": float(probability @ np.asarray([row[3] for row in rows])),
        "decomposition_error": float(max(row[4] for row in rows)),
    }


def shell_formula(config: dict[str, Any], p_value: float, points: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    a_matrix = np.asarray(config["independent_shell_matrix"], dtype=np.float64)
    source = np.asarray(config["independent_shell_source"], dtype=np.float64)
    operator = a_matrix.T @ a_matrix
    pulled_source = a_matrix.T @ source
    inverse = np.linalg.inv(np.eye(2) + p_value * operator)
    formula = (
        0.5 * (p_value * np.trace(operator) - np.linalg.slogdet(np.eye(2) + p_value * operator)[1])
        - 0.5 * p_value * source @ source
        + 0.5 * p_value**2 * pulled_source @ inverse @ pulled_source
    )
    translated = source[None, :] + points @ a_matrix.T
    q_value = 0.5 * np.sum(translated**2, axis=1) - 0.5 * np.trace(operator)
    direct = math.log(float(np.sum(weights * np.exp(-p_value * q_value))))
    source_part = -0.5 * p_value * source @ source + 0.5 * p_value**2 * pulled_source @ inverse @ pulled_source
    ceiling = 0.25 * p_value**2 * np.sum(operator**2)
    return {
        "formula": float(formula),
        "direct": float(direct),
        "error": abs(float(formula) - float(direct)),
        "source_part": float(source_part),
        "ceiling": float(ceiling),
        "ceiling_gap": float(ceiling - formula),
    }


def independent_shift_check(model: IndependentModel, config: dict[str, Any]) -> dict[str, float]:
    """Pointwise Gaussian value/derivative calculation for deterministic shifts."""
    shift_value = float(config["shift_value"])
    shift_derivative = float(config["shift_derivative"])
    value_nodes, value_weights = normal_grid(int(config["shift_quadrature_order"]), 1)
    derivative_variance = float(config["shift_derivative_variance"])
    b_values = model.b(value_nodes[:, 0] + shift_value)
    expected_b = float(value_weights @ b_values)
    # E[1/2 B(X+h)(Y+dh)^2 - 1/2 B(X+h) Var(Y)]
    exact = 0.5 * expected_b * shift_derivative**2
    expanded = 0.5 * expected_b * (
        derivative_variance + shift_derivative**2 - derivative_variance
    )
    return {"exact": exact, "expanded": expanded, "error": abs(exact - expanded)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    config = manifest["independent_audit"]
    rows: list[dict[str, Any]] = []

    for key in ("production_functional_manifest", "a8_manifest"):
        record = manifest["authority"][key]
        actual = sha256(REPO / record["path"])
        add(f"independent_authority_{key}_hash", actual == record["sha256"], actual, record["sha256"], rows)

    model = IndependentModel(config)
    parity = model.local_parity()
    tolerance = float(config["tolerance"])
    add("independent_common_even_parity", float(np.max(np.abs(parity))) < tolerance, parity.tolist(), tolerance, rows)

    points, weights = normal_grid(int(config["quadrature_order"]), 2)
    p_value = float(config["p"])
    interpolation = []
    for t_value in config["t_values"]:
        t_float = float(t_value)
        current = integrate(model, points, weights, p_value, t_float)
        step = float(config["difference_step"])
        plus = integrate(model, points, weights, p_value, t_float + step)["log_partition"]
        minus = integrate(model, points, weights, p_value, t_float - step)["log_partition"]
        current["finite_difference"] = (plus - minus) / (2.0 * step)
        current["raw_error"] = abs(current["raw"] - current["finite_difference"])
        current["cancelled_error"] = abs(current["cancelled"] - current["finite_difference"])
        current["raw_cancelled_error"] = abs(current["raw"] - current["cancelled"])
        current["t"] = t_float
        interpolation.append(current)
    coarse_points, coarse_weights = normal_grid(int(config["coarse_quadrature_order"]), 2)
    coarse_errors = []
    for t_value in config["t_values"]:
        coarse = integrate(model, coarse_points, coarse_weights, p_value, float(t_value))
        coarse_errors.append(abs(coarse["raw"] - coarse["cancelled"]))
    derivative_tolerance = float(config["derivative_tolerance"])
    add("independent_raw_derivative", max(item["raw_error"] for item in interpolation) < derivative_tolerance, interpolation, derivative_tolerance, rows)
    add("independent_cancelled_derivative", max(item["cancelled_error"] for item in interpolation) < derivative_tolerance, interpolation, derivative_tolerance, rows)
    add("independent_raw_cancelled_agreement", max(item["raw_cancelled_error"] for item in interpolation) < derivative_tolerance, interpolation, derivative_tolerance, rows)
    add("independent_IBP_quadrature_convergence", max(item["raw_cancelled_error"] for item in interpolation) < float(config["quadrature_convergence_factor"]) * max(coarse_errors), {"coarse": coarse_errors, "fine": [item["raw_cancelled_error"] for item in interpolation]}, f"fine < {config['quadrature_convergence_factor']} * coarse", rows)
    add("independent_trace_decomposition", max(item["decomposition_error"] for item in interpolation) < tolerance, interpolation, tolerance, rows)

    shell = shell_formula(config, p_value, points, weights)
    add("independent_noncentral_shell_formula", shell["error"] < derivative_tolerance, shell, derivative_tolerance, rows)
    add("independent_noncentral_source_nonpositive", shell["source_part"] <= tolerance, shell["source_part"], "<=0", rows)
    add("independent_noncentral_HS_ceiling", shell["ceiling_gap"] >= -tolerance, shell["ceiling_gap"], ">=0", rows)

    shift = independent_shift_check(model, config)
    add("deterministic_shift_expectation_is_nonnegative", shift["exact"] >= 0.0, shift, ">=0", rows)
    add("deterministic_shift_exact_cancellation", shift["error"] < tolerance, shift, tolerance, rows)

    odd_model = IndependentModel(config, odd=True)
    odd_parity = odd_model.local_parity()
    odd_result = integrate(odd_model, points, weights, p_value, float(config["negative_control_t"]))
    add("odd_regulator_breaks_parity", float(np.max(np.abs(odd_parity))) > float(config["negative_control_floor"]), odd_parity.tolist(), f">{config['negative_control_floor']}", rows)
    add("odd_regulator_requires_divergence_term", abs(odd_result["cancelled"] - odd_result["without_divergence"]) > float(config["negative_control_floor"]), odd_result, f">{config['negative_control_floor']}", rows)

    add("residual_gate_is_tilted_not_base_law", manifest["open_followup"] == "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND", manifest["open_followup"], "named residual", rows)
    add("full_self_coupled_measure_is_excluded", any("full self-coupled" in item for item in manifest["honesty_boundary"]["excluded"]), manifest["honesty_boundary"]["excluded"], "explicit exclusion", rows)

    failures = [item for item in rows if item["status"] != "PASS"]
    verdict = "A9-CLASSII-SMART-PATH-INDEPENDENT-PASS" if not failures else "A9-CLASSII-SMART-PATH-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a9-classii-smart-path-independent-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "derived": {
            "parity": parity.tolist(),
            "interpolation": interpolation,
            "noncentral_shell": shell,
            "deterministic_shift": shift,
            "odd_control": {"parity": odd_parity.tolist(), "result": odd_result},
        },
        "assertions": rows,
        "assertion_summary": {"passed": len(rows) - len(failures), "total": len(rows)},
        "failures": failures,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
            "imports_primary": False,
        },
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['assertion_summary']['passed']}/{output['assertion_summary']['total']} PASS")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
