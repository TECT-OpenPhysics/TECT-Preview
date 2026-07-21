#!/usr/bin/env python3
"""Non-importing independent audit for A12 source-square reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


VERSION = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_source_square_reduction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "runs" / "2026-07-21-independent-source-square" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def record(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


SIGMA = [
    np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
    np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
    np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
]


def six_real(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def raw_constants(params: dict[str, Any]) -> dict[str, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    x_star = max(0.0, (2.0 * float(params["r"]) - float(params["Z"])) / (2.0 * float(params["Y"]) - float(params["Z"])))
    candidates = [0.0, x_star]
    ratios = [
        (float(params["Y"]) * x_value**2 + float(params["Z"]) * x_value + float(params["r"])) / (1.0 + x_value) ** 2
        for x_value in candidates
    ] + [float(params["Y"])]
    beta = 4.0 * (a_value + 2.0 * abs(b_value) + c_value)
    c_symbol = min(ratios)
    return {"a": a_value, "b": b_value, "c": c_value, "beta_operator": beta, "c_symbol": c_symbol, "source_base_constant": beta**2 / c_symbol}


def direct_metric(psi: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    coefficients = np.asarray([
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]),
        float(params["cKK"]) * float(params["beta_X"]) ** 2,
    ]) / denominator
    x = np.concatenate((psi.real, psi.imag))
    rho = float(np.real(np.vdot(psi, psi)))
    result = np.zeros((6, 6))
    for small in SIGMA:
        generator = np.pad(small, ((0, 1), (0, 1)))
        symmetric = six_real(generator)
        moment = float(np.real(np.vdot(psi, generator @ psi)))
        q_value = moment / (rho + float(params["rho_regularizer"]))
        current = 2.0 * symmetric @ x
        tangent = 2.0 * (symmetric - q_value * np.eye(6)) @ x
        result += coefficients[0] * np.outer(current, current)
        result += coefficients[1] * (np.outer(current, tangent) + np.outer(tangent, current))
        result += coefficients[2] * np.outer(tangent, tangent)
    return result


def random_fierz(params: dict[str, Any], seed: int, samples: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    constants = raw_constants(params)
    maximum = 0.0
    minimum = math.inf
    maximum_derivative_error = 0.0
    floor = float(params["rho_regularizer"])
    for _ in range(samples):
        psi = rng.normal(size=3) + 1j * rng.normal(size=3)
        h = rng.normal(size=3) + 1j * rng.normal(size=3)
        norm = float(np.real(np.vdot(psi, psi)))
        eigenvalues = np.linalg.eigvalsh(direct_metric(psi, params))
        maximum = max(maximum, float(eigenvalues[-1]) / norm)
        minimum = min(minimum, float(eigenvalues[0]))
        z = psi[:2]
        eta = h[:2]
        rho = norm
        step = 1e-6 / max(1.0, float(np.linalg.norm(h)))
        for sigma in SIGMA:
            def quotient(value: np.ndarray) -> float:
                zz = value[:2]
                return float(np.real(np.vdot(zz, sigma @ zz))) / (float(np.real(np.vdot(value, value))) + floor)
            finite = (quotient(psi + step * h) - quotient(psi - step * h)) / (2.0 * step)
            moment = float(np.real(np.vdot(z, sigma @ z)))
            current = 2.0 * float(np.real(np.vdot(sigma @ z, eta)))
            drho = 2.0 * float(np.real(np.vdot(psi, h)))
            exact = (current * (rho + floor) - moment * drho) / (rho + floor) ** 2
            maximum_derivative_error = max(maximum_derivative_error, abs(finite - exact))
    return {"maximum_operator_ratio": maximum, "minimum_eigenvalue": minimum, "maximum_q_derivative_error": maximum_derivative_error, "beta_operator": constants["beta_operator"]}


def multiplier_audit(seed: int, samples: int, extra_scales: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    maximum = 0.0
    maximum_closed_form_error = 0.0
    tested = 0
    for _ in range(samples):
        frequencies = rng.integers(-24, 25, size=(5, 3))
        sixth = -np.sum(frequencies, axis=0)
        all_frequencies = np.vstack((frequencies, sixth))
        maximum_index = int(np.max(np.abs(all_frequencies)))
        if maximum_index == 0:
            continue
        j0 = max(1, int(math.ceil(math.log2(maximum_index))) + 1)
        terminal = j0 + extra_scales
        scale_sum = sum(2.0 ** (-2 * j) for j in range(j0, terminal + 1))
        multiplier = float(np.dot(all_frequencies[4], all_frequencies[5])) * scale_sum
        closed = float(np.dot(all_frequencies[4], all_frequencies[5])) * (4.0 / 3.0) * 2.0 ** (-2 * j0) * (1.0 - 4.0 ** (-(terminal - j0 + 1)))
        maximum = max(maximum, abs(multiplier))
        maximum_closed_form_error = max(maximum_closed_form_error, abs(multiplier - closed))
        tested += 1
    return {"maximum_absolute_multiplier": maximum, "maximum_closed_form_error": maximum_closed_form_error, "tested": tested}


def spectral_prefix(field: np.ndarray, cutoff: int) -> np.ndarray:
    grid = field.shape[0]
    modes = np.fft.fftfreq(grid) * grid
    transformed = np.fft.fft(field, axis=0)
    transformed[np.abs(modes) > cutoff] = 0.0
    return np.fft.ifft(transformed, axis=0)


def derivative(field: np.ndarray, length: float) -> np.ndarray:
    grid = field.shape[0]
    modes = 2.0 * math.pi * np.fft.fftfreq(grid, d=length / grid)
    return np.fft.ifft(1j * modes[:, None] * np.fft.fft(field, axis=0), axis=0)


def finite_holder_fixture(length: float, grid: int) -> dict[str, float]:
    angle = 2.0 * math.pi * np.arange(grid) / grid
    field = np.zeros((grid, 3), dtype=np.complex128)
    field[:, 0] = 0.7 + 0.22 * np.exp(1j * angle) + 0.13 * np.exp(-4j * angle)
    field[:, 1] = 0.19j * np.exp(2j * angle) + 0.11 * np.exp(-7j * angle)
    field[:, 2] = 0.09 * np.cos(3.0 * angle)
    cutoffs = [1, 2, 4, 8]
    prefixes = [spectral_prefix(field, cutoff) for cutoff in cutoffs]
    point_norms = [np.sqrt(np.sum(np.abs(value) ** 2, axis=1)) for value in prefixes]
    maximum_function = np.max(np.stack(point_norms), axis=0)
    m_norm = float(np.mean(maximum_function**6) ** (1.0 / 6.0))
    field_norm6 = float(np.mean(np.sum(np.abs(field) ** 2, axis=1) ** 3))
    alpha = 2.0 * math.pi / length
    weights = [1.0 / math.sqrt(1.0 + (alpha * (cutoff + 1)) ** 2) for cutoff in cutoffs]
    derivatives = [derivative(value, length) for value in prefixes]
    square = np.sqrt(sum(weight**2 * np.sum(np.abs(dvalue) ** 2, axis=1) for weight, dvalue in zip(weights, derivatives)))
    q_norm = float(np.mean(square**6) ** (1.0 / 6.0))
    form = float(np.mean(sum(weight**2 * norm**4 * np.sum(np.abs(dvalue) ** 2, axis=1) for weight, norm, dvalue in zip(weights, point_norms, derivatives))))
    holder_upper = m_norm**4 * q_norm**2
    return {
        "field_L6_sixth": field_norm6,
        "maximal_L6": m_norm,
        "weighted_derivative_square_L6": q_norm,
        "source_envelope": form,
        "holder_upper": holder_upper,
        "holder_ratio": form / holder_upper,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for key in ("a1_manifest", "a7_manifest", "a8_manifest", "a9_manifest", "a10_manifest", "a11_manifest"):
        item = manifest["authority"][key]
        value = digest(REPO / item["path"])
        record(rows, f"authority_{key}_independent", value == item["sha256"], value, item["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    params = a1["parameters"]
    constants = raw_constants(params)
    record(rows, "independent_beta_operator", abs(constants["beta_operator"] - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, constants["beta_operator"], manifest["derived_oracles"]["beta_operator"])
    record(rows, "independent_c_symbol", abs(constants["c_symbol"] - float(manifest["derived_oracles"]["c_symbol"])) < 1e-14, constants["c_symbol"], manifest["derived_oracles"]["c_symbol"])
    record(rows, "independent_source_base", abs(constants["source_base_constant"] - float(manifest["derived_oracles"]["source_base_constant"])) < 1e-14, constants["source_base_constant"], manifest["derived_oracles"]["source_base_constant"])

    fierz = random_fierz(params, int(manifest["independent_audit"]["seed"]), int(manifest["independent_audit"]["fierz_samples"]))
    record(rows, "independent_metric_positive", fierz["minimum_eigenvalue"] >= -float(manifest["independent_audit"]["matrix_tolerance"]), fierz["minimum_eigenvalue"], ">=0")
    record(rows, "independent_operator_bound", fierz["maximum_operator_ratio"] <= constants["beta_operator"] * (1.0 + 1e-10), fierz["maximum_operator_ratio"], constants["beta_operator"])
    record(rows, "independent_q_derivative", fierz["maximum_q_derivative_error"] < float(manifest["independent_audit"]["derivative_tolerance"]), fierz["maximum_q_derivative_error"], manifest["independent_audit"]["derivative_tolerance"])

    multiplier = multiplier_audit(int(manifest["independent_audit"]["multiplier_seed"]), int(manifest["independent_audit"]["multiplier_samples"]), int(manifest["independent_audit"]["extra_scales"]))
    record(rows, "six_linear_scale_sum_closed_form", multiplier["maximum_closed_form_error"] < 1e-14, multiplier["maximum_closed_form_error"], "<1e-14")
    record(rows, "six_linear_multiplier_pointwise_unit_bound", multiplier["maximum_absolute_multiplier"] <= 1.0 + 1e-12, multiplier["maximum_absolute_multiplier"], "<=1")
    record(rows, "six_linear_multiplier_sample_count", multiplier["tested"] == int(manifest["independent_audit"]["multiplier_samples"]), multiplier["tested"], manifest["independent_audit"]["multiplier_samples"])

    fixture = finite_holder_fixture(float(params["Lx"]), int(manifest["independent_audit"]["fixture_grid"]))
    record(rows, "finite_fixture_holder_step", fixture["holder_ratio"] <= 1.0 + 1e-12, fixture["holder_ratio"], "<=1")
    record(rows, "finite_fixture_nonzero", fixture["source_envelope"] > 0.0 and fixture["field_L6_sixth"] > 0.0, fixture, "positive")

    p_value = float(manifest["derived_oracles"]["budget_reference_p"])
    threshold = float(params["gamma"]) / (3.0 * p_value) / constants["source_base_constant"]
    record(rows, "independent_budget_threshold", abs(threshold - float(manifest["derived_oracles"]["source_only_H6_ceiling_at_reference_p"])) < 1e-10, threshold, manifest["derived_oracles"]["source_only_H6_ceiling_at_reference_p"])
    record(rows, "symbolic_constant_not_misreported_numeric", manifest["honesty_boundary"]["numerical_enclosure"] == "OPEN", manifest["honesty_boundary"]["numerical_enclosure"], "OPEN")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a12-classii-source-square-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": VERSION,
        "git_commit": head(),
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertion_count": len(rows),
        "passed": passed,
        "failed": len(rows) - passed,
        "assertions": rows,
        "derived": {**constants, "fierz": fierz, "multiplier": multiplier, "finite_holder_fixture": fixture, "reference_H6_ceiling": threshold},
        "non_importing": "This script imports neither the primary A12 audit nor A10 implementation code.",
    }
    write_json(args.output, payload)
    print(f"PASS: independent ({passed}/{len(rows)})" if payload["status"] == "PASS" else f"FAIL: independent ({passed}/{len(rows)})")
    print(f"six-linear |m| max={multiplier['maximum_absolute_multiplier']:.12g}; finite Holder ratio={fixture['holder_ratio']:.12g}")
    print(f"Evidence: {args.output}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
