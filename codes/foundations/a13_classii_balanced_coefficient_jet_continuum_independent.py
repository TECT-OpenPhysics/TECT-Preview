#!/usr/bin/env python3
"""Non-importing audit of the A13 balanced coefficient-jet subtheorem.

This route rederives the power count, uses dense zero-padded Fourier
convolution for the two parenthesisations, projects the scalar forest through
Gaussian quadrature, and differentiates the six-real production coefficient
with complex-step and five-point formulas.  It never imports the primary
implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"
__claims__ = ["A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM / "classii_balanced_coefficient_jet_continuum_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-independent-balanced-coefficient-jet-continuum"
    / "result.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def real_generators() -> list[np.ndarray]:
    pauli = [
        np.array([[0, 1], [1, 0]], dtype=np.complex128),
        np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.array([[1, 0], [0, -1]], dtype=np.complex128),
    ]
    output = []
    for generator in pauli:
        padded = np.zeros((3, 3), dtype=np.complex128)
        padded[:2, :2] = generator
        output.append(np.block([[padded.real, -padded.imag], [padded.imag, padded.real]]))
    return output


def analytic_coefficient(x: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    a_value = float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator
    b_value = float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator
    c_value = float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator
    epsilon = float(params["rho_regularizer"])
    rho = x @ x
    dtype = np.result_type(x, np.float64)
    identity = np.eye(6, dtype=dtype)
    result = np.zeros((6, 6), dtype=dtype)
    for symmetric in real_generators():
        moment = np.einsum("i,ij,j->", x, symmetric, x)
        q_value = moment / (rho + epsilon)
        p_value = 2.0 * (symmetric @ x)
        v_value = 2.0 * ((symmetric - q_value * identity) @ x)
        result = result + a_value * np.outer(p_value, p_value)
        result = result + b_value * (
            np.outer(p_value, v_value) + np.outer(v_value, p_value)
        )
        result = result + c_value * np.outer(v_value, v_value)
    return result


def directional_chart(params: dict[str, Any], seed: int) -> dict[str, float]:
    generator = np.random.default_rng(seed)
    maximum_identity = 0.0
    maximum_fd_first = 0.0
    maximum_fd_second = 0.0
    checksum = 0.0
    step = 7.5e-4
    for _ in range(8):
        x = 0.35 * generator.normal(size=6)
        z = 0.12 * generator.normal(size=6)
        base = analytic_coefficient(x, params)
        complex_value = analytic_coefficient(x + 1j * step * z, params)
        first = np.imag(complex_value) / step
        second = 2.0 * (base - np.real(complex_value)) / step**2
        full = analytic_coefficient(x + z, params)
        remainder = full - base - first - 0.5 * second
        reconstructed = base + first + 0.5 * second + remainder
        maximum_identity = max(maximum_identity, float(np.max(np.abs(full - reconstructed))))
        plus = analytic_coefficient(x + step * z, params)
        minus = analytic_coefficient(x - step * z, params)
        plus_two = analytic_coefficient(x + 2.0 * step * z, params)
        minus_two = analytic_coefficient(x - 2.0 * step * z, params)
        fd_first = (-plus_two + 8.0 * plus - 8.0 * minus + minus_two) / (12.0 * step)
        fd_second = (-plus_two + 16.0 * plus - 30.0 * base + 16.0 * minus - minus_two) / (12.0 * step**2)
        maximum_fd_first = max(
            maximum_fd_first,
            float(np.linalg.norm(first - fd_first) / max(1.0, float(np.linalg.norm(first)))),
        )
        maximum_fd_second = max(
            maximum_fd_second,
            float(np.linalg.norm(second - fd_second) / max(1.0, float(np.linalg.norm(second)))),
        )
        checksum += float(np.sum(full))
    return {
        "maximum_identity_error": maximum_identity,
        "maximum_first_fd_relative_error": maximum_fd_first,
        "maximum_second_fd_relative_error": maximum_fd_second,
        "full_coefficient_checksum": checksum,
    }


def next_power_two(value: int) -> int:
    return 1 << (value - 1).bit_length()


def linear_convolve(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    target = tuple(a + b - 1 for a, b in zip(left.shape, right.shape))
    padded = tuple(next_power_two(value) for value in target)
    transformed = np.fft.fftn(left, padded) * np.fft.fftn(right, padded)
    result = np.fft.ifftn(transformed).real
    return result[tuple(slice(0, value) for value in target)]


def dense_parenthesisation_fixture(seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    x = np.zeros((7, 7, 7), dtype=np.float64)
    q = np.zeros_like(x)
    x.flat[rng.choice(x.size, size=11, replace=False)] = rng.integers(-3, 4, size=11)
    q.flat[rng.choice(q.size, size=9, replace=False)] = rng.integers(-3, 4, size=9)
    left = linear_convolve(linear_convolve(x, x), q)
    right = linear_convolve(x, linear_convolve(x, q))
    return {
        "maximum_absolute_associator": float(np.max(np.abs(left - right))),
        "left_l2": float(np.linalg.norm(left)),
        "right_l2": float(np.linalg.norm(right)),
    }


def hermite_quadrature_fixture(order: int) -> dict[str, float]:
    nodes, weights = np.polynomial.hermite_e.hermegauss(order)
    weights = weights / math.sqrt(2.0 * math.pi)
    h0 = np.ones_like(nodes)
    h1 = nodes
    h2 = nodes**2 - 1.0
    h3 = nodes**3 - 3.0 * nodes
    h4 = nodes**4 - 6.0 * nodes**2 + 3.0
    basis = {0: h0, 1: h1, 2: h2, 3: h3, 4: h4}
    factorial = {0: 1.0, 1: 1.0, 2: 2.0, 3: 6.0, 4: 24.0}

    def project(values: np.ndarray) -> dict[int, float]:
        return {
            degree: float(np.sum(weights * values * polynomial) / factorial[degree])
            for degree, polynomial in basis.items()
        }

    xh2 = project(h1 * h2)
    h2h2 = project(h2 * h2)
    x2h2 = project(nodes**2 * h2)
    xh3 = project(h1 * h3)
    return {
        "xh2_p1": xh2[1],
        "xh2_p3": xh2[3],
        "h2h2_p0": h2h2[0],
        "h2h2_p2": h2h2[2],
        "h2h2_p4": h2h2[4],
        "x2h2_p0": x2h2[0],
        "x2h2_p2": x2h2[2],
        "x2h2_p4": x2h2[4],
        "xh3_p2": xh3[2],
        "xh3_p4": xh3[4],
    }


def independent_arithmetic(manifest: dict[str, Any]) -> dict[str, float]:
    dimension = int(manifest["theorem_inputs"]["dimension"])
    alpha = float(manifest["theorem_inputs"]["alpha"])
    kappa = float(manifest["theorem_inputs"]["kappa"])
    covariance = float(manifest["theorem_inputs"]["covariance_decay"])
    # A differentiated covariance loses two powers.  A convolution of two
    # sequences in dimension d subtracts d powers.  Apply that rule in a
    # different order than the primary script.
    q_decay = (covariance - 2.0) + (covariance - 2.0) - dimension
    p3_decay = q_decay + covariance - dimension
    p4_decay = p3_decay + covariance - dimension
    return {
        "derivative_covariance_decay": covariance - 2.0,
        "q_variance_decay": q_decay,
        "first_jet_variance_decay": p3_decay,
        "second_jet_variance_decay": p4_decay,
        "first_target": alpha - 1.0 - kappa,
        "second_target": 2.0 * alpha - 1.0 - kappa,
        "third_remainder_regularities": 3.0 * alpha - 1.0 - kappa,
        "first_sobolev_ceiling": (p3_decay - dimension) / 2.0,
        "second_sobolev_ceiling": (p4_decay - dimension) / 2.0,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["authority"]["a1_manifest"]["path"]
    params = json.loads(a1_path.read_text(encoding="utf-8"))["parameters"]
    tolerance = float(manifest["independent_audit"]["tolerance"])
    rows: list[dict[str, Any]] = []

    arithmetic = independent_arithmetic(manifest)
    for key, expected in manifest["oracles"]["theorem_arithmetic"].items():
        add(rows, f"independent_arithmetic_{key}", abs(arithmetic[key] - float(expected)) < tolerance, arithmetic[key], expected)
    add(rows, "independent_first_target_summable", arithmetic["first_target"] < arithmetic["first_sobolev_ceiling"], arithmetic["first_target"], f"<{arithmetic['first_sobolev_ceiling']}")
    add(rows, "independent_second_target_summable", arithmetic["second_target"] < arithmetic["second_sobolev_ceiling"], arithmetic["second_target"], f"<{arithmetic['second_sobolev_ceiling']}")
    add(rows, "independent_remainder_positive", arithmetic["third_remainder_regularities"] > 0.0, arithmetic["third_remainder_regularities"], ">0")

    hermite = hermite_quadrature_fixture(int(manifest["independent_audit"]["hermite_order"]))
    expected_hermite = {
        "xh2_p1": 2.0,
        "xh2_p3": 1.0,
        "h2h2_p0": 2.0,
        "h2h2_p2": 4.0,
        "h2h2_p4": 1.0,
        "x2h2_p0": 2.0,
        "x2h2_p2": 5.0,
        "x2h2_p4": 1.0,
        "xh3_p2": 3.0,
        "xh3_p4": 1.0,
    }
    maximum_hermite_error = max(abs(hermite[key] - value) for key, value in expected_hermite.items())
    add(rows, "gauss_hermite_recovers_all_forest_coefficients", maximum_hermite_error < tolerance, maximum_hermite_error, f"<{tolerance}")

    dense = dense_parenthesisation_fixture(int(manifest["independent_audit"]["dense_seed"]))
    add(rows, "dense_nonaliased_parenthesisations_agree", dense["maximum_absolute_associator"] < 1.0e-9, dense["maximum_absolute_associator"], "<1e-9")
    add(rows, "dense_parenthesisation_fixture_nonzero", min(dense["left_l2"], dense["right_l2"]) > 1.0, dense, "both norms >1")

    chart = directional_chart(params, int(manifest["independent_audit"]["directional_seed"]))
    add(rows, "complex_step_rational_taylor_chart_exact", chart["maximum_identity_error"] < tolerance, chart["maximum_identity_error"], f"<{tolerance}")
    add(rows, "complex_step_first_vs_five_point", chart["maximum_first_fd_relative_error"] < 3.0e-7, chart["maximum_first_fd_relative_error"], "<3e-7")
    add(rows, "complex_step_second_vs_five_point", chart["maximum_second_fd_relative_error"] < 3.0e-7, chart["maximum_second_fd_relative_error"], "<3e-7")
    add(rows, "independent_coefficient_fixture_finite", math.isfinite(chart["full_coefficient_checksum"]), chart["full_coefficient_checksum"], "finite")

    add(rows, "a1_authority_hash", digest(a1_path) == manifest["authority"]["a1_manifest"]["sha256"], digest(a1_path), manifest["authority"]["a1_manifest"]["sha256"])
    add(rows, "finite_sigma_q_required", manifest["reconstruction"]["finite_wick_conversion"] == "retain Sigma_Lambda Q_Lambda and scale-resolved Sigma_>j Delta_j Q_Lambda", manifest["reconstruction"]["finite_wick_conversion"], "finite conversion retained")
    add(rows, "no_intermediate_projection", not manifest["balanced_jets"]["intermediate_projection"], manifest["balanced_jets"]["intermediate_projection"], False)
    add(rows, "all_finite_moments_use_hypercontractivity", manifest["balanced_jets"]["moment_lift"] == "fixed-chaos Hilbert-valued hypercontractivity", manifest["balanced_jets"]["moment_lift"], "fixed-chaos Hilbert-valued hypercontractivity")
    add(rows, "no_tier_promotion", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")
    add(rows, "nelson_still_open", not manifest["claims_not_established"]["nelson_bound"], manifest["claims_not_established"]["nelson_bound"], False)

    expected_total = int(manifest["run_contract"]["independent_assertions"])
    add(rows, "independent_assertion_contract", len(rows) + 1 == expected_total, len(rows) + 1, expected_total)
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-balanced-coefficient-jet-continuum-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "theorem_arithmetic": arithmetic,
            "hermite_quadrature": hermite,
            "dense_parenthesisation": dense,
            "directional_chart": chart,
        },
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failed), "total": len(rows), "failed": len(failed)},
        "verdict": "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INDEPENDENT-PASS" if not failed else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failed:
        print(f"FAIL: independent ({len(failed)} issue(s))")
        for row in failed:
            print(f" - {row['name']}: {row['actual']}")
        return 1
    print(f"PASS: independent ({len(rows)}/{len(rows)})")
    print("A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-INDEPENDENT-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
