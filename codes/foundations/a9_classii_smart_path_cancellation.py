#!/usr/bin/env python3
"""Primary audit for the Class-II self-coupling smart-path reduction.

This script verifies finite-dimensional identities used by the analytic proof:
the noncentral frozen-shell determinant, the independent-to-self-coupled
conditional determinant, the Gaussian-IBP cancellation of every apparent
trace-class term, and the common-even divergence cancellation.  It does not
claim the still-open tilted-law commutator estimate.
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
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-primary-smart-path" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def gaussian_grid(order: int, dimension: int) -> tuple[np.ndarray, np.ndarray]:
    nodes_1d, weights_1d = np.polynomial.hermite.hermgauss(order)
    nodes_1d = math.sqrt(2.0) * nodes_1d
    weights_1d = weights_1d / math.sqrt(math.pi)
    indices = np.asarray(list(itertools.product(range(order), repeat=dimension)), dtype=np.int64)
    nodes = nodes_1d[indices]
    weights = np.prod(weights_1d[indices], axis=1)
    return nodes, weights


class FourierToy:
    """A genuine same-noise value/derivative model with local evenness."""

    def __init__(self, audit: dict[str, Any], asymmetric: bool = False) -> None:
        self.dimension = 4
        positions = np.asarray(audit["positions"], dtype=np.float64)
        covariances = np.asarray(audit["mode_covariances"], dtype=np.float64)
        rows_k = []
        rows_g = []
        for position in positions:
            value = []
            derivative = []
            for frequency, covariance in enumerate(covariances, start=1):
                root = math.sqrt(float(covariance))
                value.extend([root * math.cos(frequency * position), root * math.sin(frequency * position)])
                derivative.extend(
                    [
                        -frequency * root * math.sin(frequency * position),
                        frequency * root * math.cos(frequency * position),
                    ]
                )
            rows_k.append(value)
            rows_g.append(derivative)
        self.k = np.asarray(rows_k, dtype=np.float64)
        self.g = np.asarray(rows_g, dtype=np.float64)
        if asymmetric:
            self.g = self.g + float(audit["asymmetric_mixing"]) * self.k
        self.site_weights = np.full(len(positions), 1.0 / len(positions), dtype=np.float64)
        self.coefficient_quadratic = float(audit["coefficient_quadratic"])
        self.coefficient_rational = float(audit["coefficient_rational"])
        self.coefficient_floor = float(audit["coefficient_floor"])
        self.quartic = float(audit["potential_quartic"])
        self.sextic = float(audit["potential_sextic"])

    def coefficient(self, value: np.ndarray) -> np.ndarray:
        squared = value * value
        return self.coefficient_quadratic * squared + self.coefficient_rational * squared * squared / (
            squared + self.coefficient_floor
        )

    def coefficient_prime(self, value: np.ndarray) -> np.ndarray:
        squared = value * value
        floor = self.coefficient_floor
        rational_derivative = 2.0 * value**3 * (squared + 2.0 * floor) / (squared + floor) ** 2
        return 2.0 * self.coefficient_quadratic * value + self.coefficient_rational * rational_derivative

    def operator_and_derivatives(self, white: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        values = self.k @ white
        coefficients = self.coefficient(values)
        derivatives = self.coefficient_prime(values)
        operator = np.zeros((self.dimension, self.dimension), dtype=np.float64)
        operator_derivatives = [np.zeros_like(operator) for _ in range(self.dimension)]
        for site, weight in enumerate(self.site_weights):
            outer = np.outer(self.g[site], self.g[site])
            operator += weight * coefficients[site] * outer
            for index in range(self.dimension):
                operator_derivatives[index] += weight * derivatives[site] * self.k[site, index] * outer
        return operator, operator_derivatives

    def potential_and_gradient(self, white: np.ndarray) -> tuple[float, np.ndarray]:
        values = self.k @ white
        potential = float(
            np.sum(self.site_weights * (self.quartic * values**4 / 4.0 + self.sextic * values**6 / 6.0))
        )
        force = self.site_weights * (self.quartic * values**3 + self.sextic * values**5)
        return potential, self.k.T @ force

    def local_cross_covariances(self) -> np.ndarray:
        return np.sum(self.k * self.g, axis=1)


def resolvents(operator: np.ndarray, p_value: float, t_value: float) -> tuple[np.ndarray, np.ndarray]:
    identity = np.eye(operator.shape[0])
    resolvent = np.linalg.inv(identity + p_value * t_value * operator)
    return resolvent, operator @ resolvent


def log_det2(operator: np.ndarray, scale: float) -> float:
    sign, logdet = np.linalg.slogdet(np.eye(operator.shape[0]) + scale * operator)
    if sign <= 0:
        raise ValueError("positive determinant expected")
    return float(logdet - scale * np.trace(operator))


def conditional_log_weight(model: FourierToy, white: np.ndarray, p_value: float, t_value: float) -> float:
    operator, _ = model.operator_and_derivatives(white)
    potential, _ = model.potential_and_gradient(white)
    _, smoothed = resolvents(operator, p_value, t_value)
    return float(
        -p_value * potential
        - 0.5 * log_det2(operator, p_value * t_value)
        + 0.5
        * p_value
        * (1.0 - t_value)
        * (np.trace(operator) - white @ smoothed @ white)
    )


def smart_path_terms(
    model: FourierToy, white: np.ndarray, p_value: float, t_value: float
) -> dict[str, Any]:
    operator, operator_derivatives = model.operator_and_derivatives(white)
    _, potential_gradient = model.potential_and_gradient(white)
    resolvent, smoothed = resolvents(operator, p_value, t_value)
    sx = smoothed @ white
    raw = 0.5 * p_value * (white @ sx - np.trace(smoothed))
    raw += 0.5 * p_value**2 * (1.0 - t_value) * float(sx @ sx)

    coefficient_gradient = np.zeros(model.dimension, dtype=np.float64)
    trace_decomposition_errors = []
    for index, derivative in enumerate(operator_derivatives):
        transformed = resolvent @ derivative @ resolvent
        direct_trace = np.trace(derivative) - white @ transformed @ white
        trace_pairing = np.trace((np.eye(model.dimension) - resolvent @ resolvent) @ derivative)
        centered = white @ transformed @ white - np.trace(transformed)
        trace_decomposition_errors.append(abs(direct_trace - (trace_pairing - centered)))
        coefficient_gradient[index] = (
            0.5 * p_value**2 * t_value**2 * np.trace(operator @ resolvent @ derivative)
            + 0.5 * p_value * (1.0 - t_value) * direct_trace
        )

    divergence = np.zeros(model.dimension, dtype=np.float64)
    for index, derivative in enumerate(operator_derivatives):
        derivative_smoothed = resolvent @ derivative @ resolvent
        divergence += derivative_smoothed[index, :]
    cancellation = 0.5 * p_value * (
        -p_value * float(potential_gradient @ sx)
        + float(coefficient_gradient @ sx)
        + float(divergence @ white)
    )
    divergence_bound = (
        p_value
        * t_value
        * np.linalg.norm(smoothed, ord="fro")
        * math.sqrt(sum(np.linalg.norm(item, ord="fro") ** 2 for item in operator_derivatives))
    )
    return {
        "raw": float(raw),
        "cancellation": float(cancellation),
        "divergence": divergence,
        "divergence_norm": float(np.linalg.norm(divergence)),
        "divergence_bound": float(divergence_bound),
        "trace_decomposition_error": float(max(trace_decomposition_errors)),
        "operator_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(operator))),
    }


def weighted_expectations(
    model: FourierToy, nodes: np.ndarray, weights: np.ndarray, p_value: float, t_value: float
) -> dict[str, float]:
    log_weights = np.asarray([conditional_log_weight(model, node, p_value, t_value) for node in nodes])
    terms = [smart_path_terms(model, node, p_value, t_value) for node in nodes]
    shift = float(np.max(log_weights))
    tilted = weights * np.exp(log_weights - shift)
    normalizer = float(np.sum(tilted))
    probabilities = tilted / normalizer
    return {
        "log_partition": shift + math.log(normalizer),
        "raw_expectation": float(np.sum(probabilities * np.asarray([item["raw"] for item in terms]))),
        "cancellation_expectation": float(
            np.sum(probabilities * np.asarray([item["cancellation"] for item in terms]))
        ),
        "maximum_trace_decomposition_error": float(max(item["trace_decomposition_error"] for item in terms)),
        "maximum_divergence_bound_excess": float(
            max(item["divergence_norm"] - item["divergence_bound"] for item in terms)
        ),
        "minimum_operator_eigenvalue": float(min(item["operator_minimum_eigenvalue"] for item in terms)),
    }


def conditional_quadrature_check(
    model: FourierToy, white: np.ndarray, p_value: float, t_value: float, order: int
) -> dict[str, float]:
    operator, _ = model.operator_and_derivatives(white)
    nodes, weights = gaussian_grid(order, model.dimension)
    correlated = math.sqrt(1.0 - t_value) * white[None, :] + math.sqrt(t_value) * nodes
    energies = 0.5 * (
        np.einsum("bi,ij,bj->b", correlated, operator, correlated) - np.trace(operator)
    )
    direct = float(np.sum(weights * np.exp(-p_value * energies)))
    _, smoothed = resolvents(operator, p_value, t_value)
    formula = math.exp(
        -0.5 * log_det2(operator, p_value * t_value)
        + 0.5
        * p_value
        * (1.0 - t_value)
        * (np.trace(operator) - white @ smoothed @ white)
    )
    return {"direct": direct, "formula": formula, "absolute_error": abs(direct - formula)}


def noncentral_shell_check(a_matrix: np.ndarray, source: np.ndarray, p_value: float, order: int) -> dict[str, float]:
    operator = a_matrix.T @ a_matrix
    q_vector = a_matrix.T @ source
    resolvent = np.linalg.inv(np.eye(operator.shape[0]) + p_value * operator)
    exact = (
        0.5 * (p_value * np.trace(operator) - np.linalg.slogdet(np.eye(operator.shape[0]) + p_value * operator)[1])
        - 0.5 * p_value * float(source @ source)
        + 0.5 * p_value**2 * float(q_vector @ resolvent @ q_vector)
    )
    nodes, weights = gaussian_grid(order, operator.shape[0])
    shifted = source[None, :] + nodes @ a_matrix.T
    energy = 0.5 * np.sum(shifted * shifted, axis=1) - 0.5 * np.trace(operator)
    direct = math.log(float(np.sum(weights * np.exp(-p_value * energy))))
    source_remainder = -0.5 * p_value * float(source @ source) + 0.5 * p_value**2 * float(
        q_vector @ resolvent @ q_vector
    )
    hs_upper = 0.25 * p_value**2 * float(np.sum(operator * operator))
    return {
        "direct_log_moment": direct,
        "formula": exact,
        "absolute_error": abs(direct - exact),
        "source_remainder": source_remainder,
        "hs_upper": hs_upper,
        "bound_gap": hs_upper - exact,
    }


def physical_constants(manifest: dict[str, Any]) -> dict[str, float]:
    a8_path = REPO / manifest["authority"]["a8_manifest"]["path"]
    a8 = json.loads(a8_path.read_text(encoding="utf-8"))
    a1_path = REPO / a8["authority"]["production_functional_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    beta_b = 12.0 * a_value + 48.0 * abs(b_value) + 48.0 * c_value
    beta_db = 24.0 * a_value + 192.0 * abs(b_value) + 288.0 * c_value
    c_symbol = float(manifest["oracles"]["c_symbol"])
    length = float(params["Lx"])
    alpha = 2.0 * math.pi / length
    lattice_upper = 1.0 + alpha**-4 * (4.0 * math.pi**2 + math.pi**4 / 45.0)
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    kappa_zero_upper = 6.0 * lattice_upper / (volume * c_symbol)
    return {
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "beta_B": beta_b,
        "beta_DB_linear": beta_db,
        "c_symbol": c_symbol,
        "lattice_sum_upper": lattice_upper,
        "kappa_zero_upper": kappa_zero_upper,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    audit = manifest["audit"]
    assertions: list[dict[str, Any]] = []

    for key in ("a7_manifest", "a8_manifest"):
        authority = manifest["authority"][key]
        actual_hash = sha256(REPO / authority["path"])
        add(f"authority_{key}_hash_matches", actual_hash == authority["sha256"], actual_hash, authority["sha256"], assertions)

    model = FourierToy(audit)
    local_cross = model.local_cross_covariances()
    add("common_even_local_value_derivative_covariance_vanishes", float(np.max(np.abs(local_cross))) < float(audit["even_tolerance"]), local_cross.tolist(), audit["even_tolerance"], assertions)

    probe = np.asarray(audit["probe_white"], dtype=np.float64)
    operator, derivatives = model.operator_and_derivatives(probe)
    add("coefficient_operator_is_positive_semidefinite", float(np.min(np.linalg.eigvalsh(operator))) >= -float(audit["matrix_tolerance"]), np.linalg.eigvalsh(operator).tolist(), ">=0", assertions)
    fd_step = float(audit["finite_difference_step"])
    derivative_errors = []
    for index in range(model.dimension):
        direction = np.zeros(model.dimension)
        direction[index] = fd_step
        plus = model.operator_and_derivatives(probe + direction)[0]
        minus = model.operator_and_derivatives(probe - direction)[0]
        derivative_errors.append(float(np.max(np.abs((plus - minus) / (2.0 * fd_step) - derivatives[index]))))
    add("analytic_operator_derivatives_match_central_difference", max(derivative_errors) < float(audit["derivative_tolerance"]), max(derivative_errors), audit["derivative_tolerance"], assertions)

    divergence_t = np.zeros(model.dimension)
    for index, derivative in enumerate(derivatives):
        divergence_t += derivative[index, :]
    add("common_even_operator_divergence_is_zero", float(np.linalg.norm(divergence_t)) < float(audit["divergence_tolerance"]), divergence_t.tolist(), audit["divergence_tolerance"], assertions)

    p_value = float(audit["p"])
    conditional_rows = [
        {"t": t_value, **conditional_quadrature_check(model, probe, p_value, t_value, int(audit["conditional_quadrature_order"]))}
        for t_value in audit["conditional_t_values"]
    ]
    add("conditional_noncentral_determinant_matches_gauss_hermite", max(row["absolute_error"] for row in conditional_rows) < float(audit["quadrature_tolerance"]), conditional_rows, audit["quadrature_tolerance"], assertions)

    shell_a = np.asarray(audit["shell_matrix"], dtype=np.float64)
    shell_source = np.asarray(audit["shell_source"], dtype=np.float64)
    shell = noncentral_shell_check(shell_a, shell_source, p_value, int(audit["shell_quadrature_order"]))
    add("noncentral_shell_formula_matches_direct_quadrature", shell["absolute_error"] < float(audit["quadrature_tolerance"]), shell, audit["quadrature_tolerance"], assertions)
    add("noncentral_source_term_is_nonpositive", shell["source_remainder"] <= float(audit["matrix_tolerance"]), shell["source_remainder"], "<=0", assertions)
    add("noncentral_shell_log_moment_obeys_HS_bound", shell["bound_gap"] >= -float(audit["matrix_tolerance"]), shell["bound_gap"], ">=0", assertions)

    nodes, weights = gaussian_grid(int(audit["partition_quadrature_order"]), model.dimension)
    interpolation_rows = []
    for t_value in audit["interpolation_t_values"]:
        t_float = float(t_value)
        row = weighted_expectations(model, nodes, weights, p_value, t_float)
        h = float(audit["partition_difference_step"])
        plus = weighted_expectations(model, nodes, weights, p_value, t_float + h)["log_partition"]
        minus = weighted_expectations(model, nodes, weights, p_value, t_float - h)["log_partition"]
        row["t"] = t_float
        row["finite_difference"] = (plus - minus) / (2.0 * h)
        row["raw_fd_error"] = abs(row["raw_expectation"] - row["finite_difference"])
        row["cancel_fd_error"] = abs(row["cancellation_expectation"] - row["finite_difference"])
        row["raw_cancel_error"] = abs(row["raw_expectation"] - row["cancellation_expectation"])
        interpolation_rows.append(row)
    coarse_nodes, coarse_weights = gaussian_grid(int(audit["coarse_partition_quadrature_order"]), model.dimension)
    coarse_cancellation_errors = []
    for t_value in audit["interpolation_t_values"]:
        coarse = weighted_expectations(model, coarse_nodes, coarse_weights, p_value, float(t_value))
        coarse_cancellation_errors.append(abs(coarse["raw_expectation"] - coarse["cancellation_expectation"]))
    add("raw_smart_path_derivative_matches_partition_difference", max(row["raw_fd_error"] for row in interpolation_rows) < float(audit["partition_tolerance"]), interpolation_rows, audit["partition_tolerance"], assertions)
    add("gaussian_IBP_cancellation_matches_partition_difference", max(row["cancel_fd_error"] for row in interpolation_rows) < float(audit["partition_tolerance"]), interpolation_rows, audit["partition_tolerance"], assertions)
    add("raw_and_cancelled_derivatives_agree", max(row["raw_cancel_error"] for row in interpolation_rows) < float(audit["partition_tolerance"]), interpolation_rows, audit["partition_tolerance"], assertions)
    add("IBP_quadrature_error_contracts_at_higher_order", max(row["raw_cancel_error"] for row in interpolation_rows) < float(audit["quadrature_convergence_factor"]) * max(coarse_cancellation_errors), {"coarse": coarse_cancellation_errors, "fine": [row["raw_cancel_error"] for row in interpolation_rows]}, f"fine < {audit['quadrature_convergence_factor']} * coarse", assertions)
    add("trace_difference_is_only_HS_pairing_plus_centered_quadratic", max(row["maximum_trace_decomposition_error"] for row in interpolation_rows) < float(audit["trace_tolerance"]), interpolation_rows, audit["trace_tolerance"], assertions)
    add("divergence_S_obeys_HS_bound", max(row["maximum_divergence_bound_excess"] for row in interpolation_rows) <= float(audit["matrix_tolerance"]), interpolation_rows, "excess<=0", assertions)

    asymmetric = FourierToy(audit, asymmetric=True)
    asym_rows = weighted_expectations(asymmetric, nodes, weights, p_value, float(audit["negative_control_t"]))
    asym_probe_terms = smart_path_terms(asymmetric, probe, p_value, float(audit["negative_control_t"]))
    add("asymmetric_regulator_breaks_local_evenness", float(np.max(np.abs(asymmetric.local_cross_covariances()))) > float(audit["negative_control_floor"]), asymmetric.local_cross_covariances().tolist(), f">{audit['negative_control_floor']}", assertions)
    add("asymmetric_regulator_produces_nonzero_divergence_correction", asym_probe_terms["divergence_norm"] > float(audit["negative_control_floor"]), asym_probe_terms["divergence_norm"], f">{audit['negative_control_floor']}", assertions)

    physical = physical_constants(manifest)
    add("physical_B_growth_constant_matches_A8", abs(physical["beta_B"] - float(manifest["oracles"]["beta_B"])) < float(audit["constant_tolerance"]), physical["beta_B"], manifest["oracles"]["beta_B"], assertions)
    add("physical_DB_linear_bound_is_finite", math.isfinite(physical["beta_DB_linear"]) and physical["beta_DB_linear"] > 0.0, physical["beta_DB_linear"], "finite positive", assertions)
    add("production_point_covariance_trace_upper_is_finite", math.isfinite(physical["kappa_zero_upper"]) and physical["kappa_zero_upper"] > 0.0, physical["kappa_zero_upper"], "finite positive", assertions)

    closed = manifest["honesty_boundary"]["closed"]
    excluded = manifest["honesty_boundary"]["excluded"]
    add("one_shell_noncentral_theorem_is_declared_closed", any("noncentral frozen-shell" in item for item in closed), closed, "declared", assertions)
    add("tilted_commutator_bound_remains_excluded", any("tilted-law" in item for item in excluded), excluded, "explicit exclusion", assertions)
    add("remaining_gate_is_named", manifest["open_followup"] == "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND", manifest["open_followup"], "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND", assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    verdict = "A9-CLASSII-SMART-PATH-PRIMARY-PASS" if not failures else "A9-CLASSII-SMART-PATH-PRIMARY-FAIL"
    config = {
        "p": p_value,
        "partition_quadrature_order": audit["partition_quadrature_order"],
        "conditional_quadrature_order": audit["conditional_quadrature_order"],
        "interpolation_t_values": audit["interpolation_t_values"],
        "negative_control_t": audit["negative_control_t"],
    }
    output = {
        "schema": "tect/a9-classii-smart-path-primary-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "config": config,
        "config_sha256": canonical_digest(config),
        "derived": {
            "local_cross_covariances": local_cross.tolist(),
            "conditional_determinant": conditional_rows,
            "noncentral_shell": shell,
            "interpolation": interpolation_rows,
            "asymmetric_control": asym_rows,
            "physical_constants": physical,
            "theorem": manifest["theorem"],
        },
        "assertions": assertions,
        "assertion_summary": {"passed": len(assertions) - len(failures), "total": len(assertions)},
        "failures": failures,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
        },
        "not_closed_here": excluded,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['assertion_summary']['passed']}/{output['assertion_summary']['total']} PASS")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
