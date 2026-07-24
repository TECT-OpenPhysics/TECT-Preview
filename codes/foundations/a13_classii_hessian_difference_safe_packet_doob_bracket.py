#!/usr/bin/env python3
"""Primary executable audit for the R-078 Hessian/Doob-bracket reduction.

All reported fractions and constants are derived from declared inputs.  The
program checks finite-dimensional algebra and exact probability fixtures; it
does not claim the open weighted innovation-Carleson inequality.
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
import sympy as sp

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-HESSIAN-DIFFERENCE-SAFE-PACKET-DOOB-BRACKET-REDUCTION"
OUTPUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-25-primary-hessian-difference-safe-packet-doob-bracket/result.json"
)
TOL = 2.0e-11


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
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def symbolic_hessian_fixture() -> dict[str, Any]:
    x, a, t = sp.symbols("x a t", real=True)
    # Coefficients are test-oracle inputs; every displayed remainder is derived.
    f = sp.Rational(2, 7) * x**7 - sp.Rational(3, 5) * x**5 + sp.Rational(11, 13) * x**3 + x
    direct = sp.expand(f.subs(x, x + a) - f - sp.diff(f, x) * a - sp.diff(f, x, 2) * a**2 / 2)
    cubic = sp.integrate(
        sp.Rational(1, 2) * (1 - t) ** 2 * sp.diff(f, x, 3).subs(x, x + t * a) * a**3,
        (t, 0, 1),
    )
    hessian = sp.integrate(
        (1 - t) * (sp.diff(f, x, 2).subs(x, x + t * a) - sp.diff(f, x, 2)) * a**2,
        (t, 0, 1),
    )
    d_a = sp.diff(direct, a)
    d_a_expected = (sp.diff(f, x).subs(x, x + a) - sp.diff(f, x) - sp.diff(f, x, 2) * a)
    d_x = sp.diff(direct, x)
    d_x_expected = (
        sp.diff(f, x).subs(x, x + a)
        - sp.diff(f, x)
        - sp.diff(f, x, 2) * a
        - sp.diff(f, x, 3) * a**2 / 2
    )
    return {
        "direct_minus_cubic": sp.simplify(direct - cubic),
        "direct_minus_hessian": sp.simplify(direct - hessian),
        "d_a_difference": sp.simplify(d_a - d_a_expected),
        "d_x_difference": sp.simplify(d_x - d_x_expected),
        "nonzero_remainder": bool(sp.Poly(direct, a).degree() >= 3),
    }


def packet_fixture() -> dict[str, float]:
    rng = np.random.default_rng(78025)
    dimension, frame = 5, 3
    q_raw = rng.normal(size=(frame, frame))
    q = q_raw.T @ q_raw + np.eye(frame)
    m0 = rng.normal(size=(dimension, frame))
    d = rng.normal(size=(dimension, frame))
    e2 = rng.normal(size=(dimension, frame))
    e3 = rng.normal(size=(dimension, frame))
    m1 = m0 + d + e2 + e3
    g = rng.normal(size=dimension)
    c_vec = rng.normal(size=dimension)
    gamma_raw = rng.normal(size=(dimension, dimension))
    gamma = gamma_raw @ gamma_raw.T

    b0 = m0 @ q @ m0.T
    b1 = m1 @ q @ m1.T
    db = d @ q @ m0.T + m0 @ q @ d.T
    f_a = b1 - b0 - db
    q_j = np.outer(g, g) - gamma
    w = m0.T @ g
    delta_w = (d + e2 + e3).T @ g
    c = m1.T @ c_vec

    v0 = 0.5 * np.sum(b0 * (np.outer(g, g) - gamma))
    v1 = 0.5 * np.sum(b1 * (np.outer(g + c_vec, g + c_vec) - gamma))
    delta_v = v1 - v0
    s0 = 0.5 * np.sum(db * q_j) + (m0.T @ g) @ q @ (m0.T @ c_vec)
    linear = w @ q @ (d.T @ c_vec)
    n2 = w @ q @ (e2.T @ c_vec)
    n3 = w @ q @ (e3.T @ c_vec)
    p = 0.5 * np.sum(f_a * q_j) + delta_w @ q @ c + 0.5 * c @ q @ c
    p_alt = (
        w @ q @ ((e2 + e3).T @ g)
        + 0.5 * (delta_w + c) @ q @ (delta_w + c)
        - 0.5 * np.sum(f_a * gamma)
    )
    return {
        "master_error": float(delta_v - (s0 + linear + n2 + n3 + p)),
        "p_reassembly_error": float(p - p_alt),
        "q_min_eigenvalue": float(np.linalg.eigvalsh(q).min()),
        "terminal_square": float(0.5 * (delta_w + c) @ q @ (delta_w + c)),
    }


def exponent_fixture() -> dict[str, Fraction]:
    s = Fraction(3, 5)
    a = (1 + s) / 4
    b = (5 - s) / 12
    slack = 1 - a - b
    epsilon = Fraction(1, 10)
    high_a = (1 + epsilon) / 4
    high_b = (5 - epsilon) / 12
    high_slack = 1 - high_a - high_b
    delta = Fraction(1, 100)
    q_shell = 1 + s + delta
    a_high_slack = (1 - q_shell) / 3
    return {
        "s": s,
        "payload_x": a,
        "payload_y": b,
        "payload_slack": slack,
        "payload_moment": 1 / slack,
        "payload_eta": a / slack,
        "payload_zeta": b / slack,
        "epsilon": epsilon,
        "high_u_x": high_a,
        "high_u_y": high_b,
        "high_u_slack": high_slack,
        "high_u_moment": 1 / high_slack,
        "high_u_eta": high_a / high_slack,
        "high_u_zeta": high_b / high_slack,
        "a_high_q": q_shell,
        "a_high_slack": a_high_slack,
        "a_high_bound": -s / 3,
    }


def conditional(values: np.ndarray, prefixes: list[tuple[int, ...]], depth: int) -> np.ndarray:
    result = np.empty_like(values, dtype=float)
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, prefix in enumerate(prefixes):
        groups.setdefault(prefix[:depth], []).append(index)
    for indices in groups.values():
        mean = float(np.mean(values[indices]))
        result[indices] = mean
    return result


def doob_fixture() -> dict[str, float]:
    prefixes = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    bits = np.asarray(prefixes, dtype=float)
    h = np.exp(0.31 * bits[:, 0] - 0.19 * bits[:, 0] * bits[:, 1] + 0.27 * bits[:, 2])
    y = bits[:, 0] + 0.4 * bits[:, 0] * bits[:, 1] - 0.3 * bits[:, 2]
    h_proj = [conditional(h, prefixes, depth) for depth in range(4)]
    y_proj = [conditional(y, prefixes, depth) for depth in range(4)]
    square_sum = 0.0
    bracket_error = 0.0
    product_error = 0.0
    for depth in range(1, 4):
        dh = h_proj[depth] - h_proj[depth - 1]
        dy = y_proj[depth] - y_proj[depth - 1]
        predictable = 1.0 + 0.2 * bits[:, 0] if depth >= 2 else np.ones(len(bits))
        lhs = float(np.mean(predictable * h * dy))
        rhs = float(np.mean(predictable * dh * dy))
        bracket_error = max(bracket_error, abs(lhs - rhs))
        increment = h_proj[depth] * y_proj[depth] - h_proj[depth - 1] * y_proj[depth - 1]
        product_error = max(product_error, abs(float(np.mean(increment - dh * dy))))
        square_sum += float(np.mean(dh**2))
    variance = float(np.mean((h - h_proj[0]) ** 2))
    return {
        "bracket_error": bracket_error,
        "product_error": product_error,
        "square_sum": square_sum,
        "terminal_variance": variance,
        "square_function_error": square_sum - variance,
    }


def gaussian_fixture() -> dict[str, float]:
    bracket = -1.0 / (3.0 * math.sqrt(3.0))
    innovation_variance = 1.0 / math.sqrt(5.0) - 1.0 / 3.0
    threshold = -4.0 * bracket / innovation_variance
    probe = threshold / 2.0
    charged = bracket * probe + 0.25 * innovation_variance * probe**2
    grid = np.linspace(0.0, 2.0 * math.pi, 8192, endpoint=False)
    zero_mode = float(np.mean(np.cos(37.0 * grid) ** 2))
    return {
        "bracket": bracket,
        "innovation_variance": innovation_variance,
        "negative_threshold": threshold,
        "probe_lambda": probe,
        "charged_value": charged,
        "opposite_carrier_zero_mode": zero_mode,
    }


def main() -> int:
    rows: list[dict[str, Any]] = []

    symbolic = symbolic_hessian_fixture()
    for key in ("direct_minus_cubic", "direct_minus_hessian", "d_a_difference", "d_x_difference"):
        add(rows, key, symbolic[key] == 0, str(symbolic[key]), "0")
    add(rows, "nonzero_test_remainder", symbolic["nonzero_remainder"], symbolic["nonzero_remainder"], True)

    packet = packet_fixture()
    add(rows, "endpoint_master_identity", abs(packet["master_error"]) < TOL, packet["master_error"], 0.0)
    add(rows, "endpoint_p_reassembly", abs(packet["p_reassembly_error"]) < TOL, packet["p_reassembly_error"], 0.0)
    add(rows, "metric_positive", packet["q_min_eigenvalue"] > 0.0, packet["q_min_eigenvalue"], ">0")
    add(rows, "terminal_square_nonnegative", packet["terminal_square"] >= 0.0, packet["terminal_square"], ">=0")

    ledger = exponent_fixture()
    expected = {
        "payload_x": Fraction(2, 5),
        "payload_y": Fraction(11, 30),
        "payload_slack": Fraction(7, 30),
        "payload_moment": Fraction(30, 7),
        "payload_eta": Fraction(12, 7),
        "payload_zeta": Fraction(11, 7),
        "high_u_x": Fraction(11, 40),
        "high_u_y": Fraction(49, 120),
        "high_u_slack": Fraction(19, 60),
        "high_u_moment": Fraction(60, 19),
        "high_u_eta": Fraction(33, 38),
        "high_u_zeta": Fraction(49, 38),
    }
    for key, value in expected.items():
        add(rows, key, ledger[key] == value, str(ledger[key]), str(value))
    add(rows, "payload_moment_below_old_15", ledger["payload_moment"] < 15, str(ledger["payload_moment"]), "<15")
    add(rows, "a_high_shell_constraint", ledger["a_high_q"] > 1 + ledger["s"], str(ledger["a_high_q"]), ">1+s")
    add(rows, "a_high_negative_slack", ledger["a_high_slack"] < ledger["a_high_bound"], str(ledger["a_high_slack"]), f"<{ledger['a_high_bound']}")

    doob = doob_fixture()
    add(rows, "doob_bracket_identity", doob["bracket_error"] < TOL, doob["bracket_error"], 0.0)
    add(rows, "doob_product_identity", doob["product_error"] < TOL, doob["product_error"], 0.0)
    add(rows, "doob_square_function", abs(doob["square_function_error"]) < TOL, doob["square_function_error"], 0.0)
    add(rows, "doob_square_nonzero", doob["square_sum"] > 0.0, doob["square_sum"], ">0")

    gaussian = gaussian_fixture()
    add(rows, "adapted_bracket_negative", gaussian["bracket"] < 0.0, gaussian["bracket"], "<0")
    add(rows, "innovation_variance_positive", gaussian["innovation_variance"] > 0.0, gaussian["innovation_variance"], ">0")
    add(rows, "threshold_value", abs(gaussian["negative_threshold"] - 6.75973469215555) < 5e-13, gaussian["negative_threshold"], "derived 6.75973469215555")
    add(rows, "bracket_plus_square_negative", gaussian["charged_value"] < 0.0, gaussian["charged_value"], "<0")
    add(rows, "opposite_carrier_low_mode", abs(gaussian["opposite_carrier_zero_mode"] - 0.5) < 2e-14, gaussian["opposite_carrier_zero_mode"], 0.5)

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-hessian-safe-packet-doob-primary/1.0",
        "result_id": RESULT_ID,
        "claim_id": CLAIM,
        "source_version": __version__,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "hessian_identity": {key: str(value) for key, value in symbolic.items()},
        "endpoint_packet": packet,
        "exponents": {key: str(value) for key, value in ledger.items()},
        "doob": doob,
        "anti_centering": gaussian,
        "claims_not_established": {
            "weighted_innovation_bracket": False,
            "complete_packet_lower_bound": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "sector_a_closure": False,
        },
    }
    atomic_json(OUTPUT, payload)
    print(f"[R-078 primary] {passed}/{len(rows)} {'PASS' if passed == len(rows) else 'FAIL'}")
    if passed == len(rows):
        print("A13-CLASSII-HESSIAN-SAFE-PACKET-DOOB-PRIMARY-PASS")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
