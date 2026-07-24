#!/usr/bin/env python3
"""Non-importing audit for R-078.

This implementation deliberately does not import the primary executable.  It
uses Gauss-Legendre/Gauss-Hermite quadrature, a four-bit probability tree,
separate endpoint algebra, and complex Fourier carriers.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-independent-hessian-difference-safe-packet-doob-bracket/result.json"
)
TOL = 3.0e-10


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="independent-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def integrate_unit(function: Any, order: int = 96) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    points = 0.5 * (nodes + 1.0)
    return float(0.5 * np.dot(weights, function(points)))


def taylor_quadrature() -> dict[str, float]:
    # An independently specified degree-six polynomial and its derivatives.
    x, a = 0.37, -0.81

    def f(z: np.ndarray | float) -> np.ndarray | float:
        return 0.17 * z**6 - 0.23 * z**4 + 0.41 * z**2 - 0.07 * z

    def f1(z: np.ndarray | float) -> np.ndarray | float:
        return 1.02 * z**5 - 0.92 * z**3 + 0.82 * z - 0.07

    def f2(z: np.ndarray | float) -> np.ndarray | float:
        return 5.10 * z**4 - 2.76 * z**2 + 0.82

    def f3(z: np.ndarray | float) -> np.ndarray | float:
        return 20.40 * z**3 - 5.52 * z

    direct = float(f(x + a) - f(x) - f1(x) * a - 0.5 * f2(x) * a * a)
    cubic = integrate_unit(lambda t: 0.5 * (1.0 - t) ** 2 * f3(x + t * a) * a**3)
    hessian = integrate_unit(lambda t: (1.0 - t) * (f2(x + t * a) - f2(x)) * a**2)
    step = 2.0e-5

    def remainder(x_value: float, a_value: float) -> float:
        return float(
            f(x_value + a_value)
            - f(x_value)
            - f1(x_value) * a_value
            - 0.5 * f2(x_value) * a_value**2
        )

    d_a_fd = (remainder(x, a + step) - remainder(x, a - step)) / (2.0 * step)
    d_a_formula = float(f1(x + a) - f1(x) - f2(x) * a)
    d_x_fd = (remainder(x + step, a) - remainder(x - step, a)) / (2.0 * step)
    d_x_formula = float(f1(x + a) - f1(x) - f2(x) * a - 0.5 * f3(x) * a**2)
    return {
        "direct": direct,
        "cubic_error": cubic - direct,
        "hessian_error": hessian - direct,
        "d_a_error": d_a_fd - d_a_formula,
        "d_x_error": d_x_fd - d_x_formula,
    }


def endpoint_algebra() -> dict[str, float]:
    rng = np.random.default_rng(50781)
    d, qdim = 4, 2
    factor = rng.normal(size=(qdim, qdim))
    metric = factor.T @ factor + 0.3 * np.eye(qdim)
    old = rng.normal(size=(d, qdim))
    first = rng.normal(size=(d, qdim))
    second = rng.normal(size=(d, qdim))
    third = rng.normal(size=(d, qdim))
    new = old + first + second + third
    g = rng.normal(size=d)
    c = rng.normal(size=d)
    covariance = np.diag(0.4 + rng.random(d))

    b_old = old @ metric @ old.T
    b_new = new @ metric @ new.T
    db = first @ metric @ old.T + old @ metric @ first.T
    f_rem = b_new - b_old - db
    wick = np.outer(g, g) - covariance

    energy_old = 0.5 * np.sum(b_old * wick)
    energy_new = 0.5 * np.sum(b_new * (np.outer(g + c, g + c) - covariance))
    first_variation = 0.5 * np.sum(db * wick) + g @ b_old @ c
    w = old.T @ g
    delta = (first + second + third).T @ g
    current_c = new.T @ c
    mixed_first = w @ metric @ (first.T @ c)
    mixed_second = w @ metric @ (second.T @ c)
    mixed_third = w @ metric @ (third.T @ c)
    complete_p = 0.5 * np.sum(f_rem * wick) + delta @ metric @ current_c + 0.5 * current_c @ metric @ current_c
    residual = energy_new - energy_old - (
        first_variation + mixed_first + mixed_second + mixed_third + complete_p
    )
    return {"residual": float(residual), "metric_floor": float(np.linalg.eigvalsh(metric).min())}


def project(values: np.ndarray, states: np.ndarray, depth: int) -> np.ndarray:
    answer = np.zeros_like(values, dtype=float)
    labels: dict[tuple[int, ...], list[int]] = {}
    for index, state in enumerate(states.astype(int)):
        labels.setdefault(tuple(state[:depth]), []).append(index)
    for indices in labels.values():
        answer[indices] = float(np.mean(values[indices]))
    return answer


def probability_tree() -> dict[str, float]:
    states = np.asarray(
        [(a, b, c, d) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1) for d in (-1, 1)],
        dtype=float,
    )
    h = np.tanh(0.43 * states[:, 0] + 0.21 * states[:, 1] * states[:, 2] - 0.17 * states[:, 3])
    y = states[:, 0] * states[:, 1] + 0.6 * states[:, 2] - 0.2 * states[:, 1] * states[:, 3]
    hp = [project(h, states, depth) for depth in range(5)]
    yp = [project(y, states, depth) for depth in range(5)]
    bracket_error = 0.0
    polarization_error = 0.0
    square_sum = 0.0
    for depth in range(1, 5):
        dh = hp[depth] - hp[depth - 1]
        dy = yp[depth] - yp[depth - 1]
        predictable = 1.0 + (0.13 * states[:, 0] if depth > 1 else 0.0)
        bracket_error = max(
            bracket_error,
            abs(float(np.mean(predictable * h * dy) - np.mean(predictable * dh * dy))),
        )
        left = dh * dy + 0.5 * dh**2
        right = 0.5 * ((dh + dy) ** 2 - dy**2)
        polarization_error = max(polarization_error, float(np.max(np.abs(left - right))))
        square_sum += float(np.mean(dh**2))
    variance = float(np.mean((h - hp[0]) ** 2))
    return {
        "bracket_error": bracket_error,
        "polarization_error": polarization_error,
        "square_error": square_sum - variance,
        "square_sum": square_sum,
    }


def exponent_route() -> dict[str, Fraction]:
    # Derive with common denominators rather than importing the primary route.
    s_num, s_den = 3, 5
    s = Fraction(s_num, s_den)
    payload_x = Fraction(s_den + s_num, 4 * s_den)
    payload_y = Fraction(5 * s_den - s_num, 12 * s_den)
    payload_slack = Fraction(1) - payload_x - payload_y
    eps_num, eps_den = 1, 10
    eps = Fraction(eps_num, eps_den)
    high_x = Fraction(eps_den + eps_num, 4 * eps_den)
    high_y = Fraction(5 * eps_den - eps_num, 12 * eps_den)
    high_slack = Fraction(1) - high_x - high_y
    q = Fraction(1) + s + Fraction(1, 200)
    return {
        "payload_x": payload_x,
        "payload_y": payload_y,
        "payload_slack": payload_slack,
        "payload_moment": 1 / payload_slack,
        "high_x": high_x,
        "high_y": high_y,
        "high_slack": high_slack,
        "high_moment": 1 / high_slack,
        "a_high_slack": (1 - q) / 3,
        "a_high_limit": -s / 3,
    }


def gauss_hermite_fixture() -> dict[str, float]:
    nodes, weights = np.polynomial.hermite.hermgauss(128)
    gaussian_x = math.sqrt(2.0) * nodes
    gaussian_w = weights / math.sqrt(math.pi)
    h = np.exp(-(gaussian_x**2))
    y = gaussian_x**2 - 1.0
    mean_h = float(np.dot(gaussian_w, h))
    bracket_point = float(np.dot(gaussian_w, h * y))
    variance_h = float(np.dot(gaussian_w, (h - mean_h) ** 2))
    spatial_factor = 0.5
    bracket = spatial_factor * bracket_point
    variance = spatial_factor * variance_h
    threshold = -2.0 * bracket / variance
    probe = threshold * 0.6
    charged = probe * bracket + 0.5 * probe**2 * variance

    grid = np.arange(4096)
    mode = 43
    positive = np.exp(2j * np.pi * mode * grid / len(grid))
    negative = np.conjugate(positive)
    low_mode = complex(np.mean(positive * negative))
    return {
        "mean_h": mean_h,
        "bracket": bracket,
        "variance": variance,
        "threshold": threshold,
        "charged": charged,
        "carrier_real": low_mode.real,
        "carrier_imag": low_mode.imag,
    }


def main() -> int:
    rows: list[dict[str, Any]] = []
    taylor = taylor_quadrature()
    add(rows, "quadrature_cubic_identity", abs(taylor["cubic_error"]) < TOL, taylor["cubic_error"], 0.0)
    add(rows, "quadrature_hessian_identity", abs(taylor["hessian_error"]) < TOL, taylor["hessian_error"], 0.0)
    add(rows, "finite_difference_dA_identity", abs(taylor["d_a_error"]) < 2e-8, taylor["d_a_error"], 0.0)
    add(rows, "finite_difference_dU_identity", abs(taylor["d_x_error"]) < 2e-8, taylor["d_x_error"], 0.0)

    endpoint = endpoint_algebra()
    add(rows, "independent_endpoint_identity", abs(endpoint["residual"]) < TOL, endpoint["residual"], 0.0)
    add(rows, "independent_metric_positive", endpoint["metric_floor"] > 0.0, endpoint["metric_floor"], ">0")

    tree = probability_tree()
    add(rows, "independent_doob_bracket", tree["bracket_error"] < TOL, tree["bracket_error"], 0.0)
    add(rows, "independent_polarization", tree["polarization_error"] < TOL, tree["polarization_error"], 0.0)
    add(rows, "independent_square_function", abs(tree["square_error"]) < TOL, tree["square_error"], 0.0)
    add(rows, "independent_square_nonzero", tree["square_sum"] > 0.0, tree["square_sum"], ">0")

    exponents = exponent_route()
    expected = {
        "payload_x": Fraction(2, 5),
        "payload_y": Fraction(11, 30),
        "payload_slack": Fraction(7, 30),
        "payload_moment": Fraction(30, 7),
        "high_x": Fraction(11, 40),
        "high_y": Fraction(49, 120),
        "high_slack": Fraction(19, 60),
        "high_moment": Fraction(60, 19),
    }
    for key, target in expected.items():
        add(rows, f"independent_{key}", exponents[key] == target, str(exponents[key]), str(target))
    add(rows, "independent_a_high_negative", exponents["a_high_slack"] < exponents["a_high_limit"], str(exponents["a_high_slack"]), f"<{exponents['a_high_limit']}")

    gaussian = gauss_hermite_fixture()
    add(rows, "gh_mean", abs(gaussian["mean_h"] - 1.0 / math.sqrt(3.0)) < 2e-14, gaussian["mean_h"], "1/sqrt(3)")
    add(rows, "gh_negative_bracket", abs(gaussian["bracket"] + 1.0 / (3.0 * math.sqrt(3.0))) < 2e-14, gaussian["bracket"], "-1/(3sqrt(3))")
    add(rows, "gh_variance_positive", gaussian["variance"] > 0.0, gaussian["variance"], ">0")
    add(rows, "gh_charged_negative", gaussian["charged"] < 0.0, gaussian["charged"], "<0")
    add(rows, "complex_carrier_one", abs(gaussian["carrier_real"] - 1.0) < TOL and abs(gaussian["carrier_imag"]) < TOL, [gaussian["carrier_real"], gaussian["carrier_imag"]], [1.0, 0.0])

    passed = sum(row["status"] == "PASS" for row in rows)
    report = {
        "schema": "tect/a13-hessian-safe-packet-doob-independent/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "source_version": __version__,
        "imports_primary": False,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "taylor": taylor,
        "endpoint": endpoint,
        "doob": tree,
        "exponents": {key: str(value) for key, value in exponents.items()},
        "anti_centering": gaussian,
        "claims_not_established": {
            "weighted_innovation_bracket": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "sector_a_closure": False,
        },
    }
    write_json(OUTPUT, report)
    print(f"[R-078 independent] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    if passed == len(rows):
        print("A13-CLASSII-HESSIAN-SAFE-PACKET-DOOB-INDEPENDENT-PASS")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
