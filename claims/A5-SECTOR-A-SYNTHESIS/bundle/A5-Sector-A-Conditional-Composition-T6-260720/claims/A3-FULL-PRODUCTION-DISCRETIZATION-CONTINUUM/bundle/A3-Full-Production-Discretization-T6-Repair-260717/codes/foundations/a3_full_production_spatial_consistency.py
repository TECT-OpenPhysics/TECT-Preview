#!/usr/bin/env python3
"""Stage-1 spatial consistency audit for the full-production P3 package.

The hash-pinned P1 backend is a Fourier-collocation gradient.  It is not
silently relabelled as an exact Galerkin method.  This audit compares its
residual with an oversampled approximation to

    R_N^G(Psi_N) = P_N R(Psi_N),

checks reference-grid stability, checks the discrete energy/gradient identity,
and measures spatial convergence on an analytic manufactured field with all
three Class-II generators active.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
P2_MANIFEST = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "full_pde_manifest.json"
BACKEND_PATH = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-spatial-consistency" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_backend() -> Any:
    spec = importlib.util.spec_from_file_location("p3_pinned_backend", BACKEND_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned P1 backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coordinates(n: int, params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    axes = [np.arange(n, dtype=np.float64) * float(params[key]) / n for key in ("Lx", "Ly", "Lz")]
    return tuple(np.meshgrid(*axes, indexing="ij"))


def phase(k: tuple[int, int, int], xyz: tuple[np.ndarray, np.ndarray, np.ndarray], params: dict[str, Any]) -> np.ndarray:
    argument = sum(2.0 * math.pi * component * coord / float(params[key]) for component, coord, key in zip(k, xyz, ("Lx", "Ly", "Lz")))
    return np.exp(1j * argument)


def manufactured_field(n: int, params: dict[str, Any]) -> np.ndarray:
    xyz = coordinates(n, params)
    value = np.zeros((3, n, n, n), dtype=np.complex128)
    value[0] = 0.35 + 0.040 * phase((1, 0, 0), xyz, params) + 0.025j * phase((0, -1, 0), xyz, params) + 0.018 * phase((1, 1, 0), xyz, params)
    value[1] = 0.28 * np.exp(0.2j) + 0.032 * phase((0, 0, 1), xyz, params) - 0.021j * phase((1, 0, -1), xyz, params)
    value[2] = 0.22 * np.exp(-0.1j) + 0.027 * phase((-1, 1, 0), xyz, params) + 0.019j * phase((0, 1, 1), xyz, params)
    return value


def manufactured_direction(n: int, params: dict[str, Any]) -> np.ndarray:
    xyz = coordinates(n, params)
    value = np.zeros((3, n, n, n), dtype=np.complex128)
    value[0] = 0.7 * phase((0, 1, 0), xyz, params) + 0.3j * phase((-1, 0, 1), xyz, params)
    value[1] = -0.4j * phase((1, -1, 0), xyz, params) + 0.2 * phase((0, 0, -1), xyz, params)
    value[2] = 0.5 * phase((1, 0, 1), xyz, params) - 0.25j * phase((-1, -1, 0), xyz, params)
    dvol = math.prod(float(params[key]) / n for key in ("Lx", "Ly", "Lz"))
    return value / math.sqrt(dvol * float(np.vdot(value, value).real))


def fourier_coefficients(value: np.ndarray) -> np.ndarray:
    axes = (-3, -2, -1)
    count = math.prod(value.shape[-3:])
    return np.fft.fftshift(np.fft.fftn(value, axes=axes), axes=axes) / count


def project(value: np.ndarray, n: int) -> np.ndarray:
    source = int(value.shape[-1])
    if value.shape[-3:] != (source, source, source) or n > source or (source - n) % 2:
        raise ValueError("projection requires same-parity cubic grids with n <= source")
    coeff = fourier_coefficients(value)
    start = (source - n) // 2
    cropped = coeff[..., start:start + n, start:start + n, start:start + n]
    axes = (-3, -2, -1)
    return np.fft.ifftn(np.fft.ifftshift(cropped, axes=axes), axes=axes) * (n ** 3)


def l2_norm(value: np.ndarray, params: dict[str, Any]) -> float:
    n = int(value.shape[-1])
    dvol = math.prod(float(params[key]) / n for key in ("Lx", "Ly", "Lz"))
    return math.sqrt(dvol * float(np.vdot(value, value).real))


def relative_l2(value: np.ndarray, reference: np.ndarray, params: dict[str, Any]) -> float:
    return l2_norm(value - reference, params) / max(l2_norm(reference, params), 1e-30)


def observed_orders(grids: list[int], errors: list[float]) -> list[float | None]:
    orders = []
    for i in range(len(grids) - 1):
        left, right = errors[i], errors[i + 1]
        if right == 0.0:
            orders.append(None)
        elif left == 0.0:
            orders.append(None)
        else:
            orders.append(math.log(left / right) / math.log(grids[i + 1] / grids[i]))
    return orders


def check(name: str, passed: bool, detail: str, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    params = dict(p1["parameters"])
    params["eta_shell"] = 0.0
    backend = load_backend()
    grids = [int(n) for n in manifest["stage1"]["grids"]]
    reference_grids = [int(n) for n in manifest["stage1"]["reference_grids"]]
    acceptance = manifest["stage1"]["acceptance"]

    reference_data: dict[int, dict[str, Any]] = {}
    for n in reference_grids:
        field = manufactured_field(n, params)
        reference_data[n] = {"residual": backend.residual(field, params), "energy": backend.energy(field, params)}

    finest_reference = reference_grids[-1]
    coarser_reference = reference_grids[-2]
    rows: list[dict[str, Any]] = []
    residual_errors: list[float] = []
    energy_errors: list[float] = []
    reference_errors: list[float] = []
    gradient_errors: list[float] = []
    for n in grids:
        field = manufactured_field(n, params)
        direction = manufactured_direction(n, params)
        residual = backend.residual(field, params)
        energy = backend.energy(field, params)
        projected_finest = project(reference_data[finest_reference]["residual"], n)
        projected_coarser = project(reference_data[coarser_reference]["residual"], n)
        residual_error = relative_l2(residual, projected_finest, params)
        reference_error = relative_l2(projected_coarser, projected_finest, params)
        energy_error = abs(energy - reference_data[finest_reference]["energy"]) / max(abs(reference_data[finest_reference]["energy"]), 1e-30)
        pairing = math.prod(float(params[key]) / n for key in ("Lx", "Ly", "Lz")) * float(np.vdot(residual, direction).real)
        fd_rows = []
        for step in manifest["stage1"]["finite_difference_steps"]:
            derivative = (backend.energy(field + step * direction, params) - backend.energy(field - step * direction, params)) / (2.0 * step)
            rel_error = abs(derivative - pairing) / max(abs(derivative), abs(pairing), 1e-30)
            fd_rows.append({"step": step, "energy_derivative": derivative, "gradient_pairing": pairing, "relative_error": rel_error})
        gradient_error = min(row["relative_error"] for row in fd_rows)
        residual_errors.append(residual_error)
        reference_errors.append(reference_error)
        energy_errors.append(energy_error)
        gradient_errors.append(gradient_error)
        rows.append({
            "grid": n,
            "collocation_to_projected_oversampled_reference_relative_l2": residual_error,
            "reference_projection_relative_l2": reference_error,
            "energy_relative_error_to_finest_reference": energy_error,
            "gradient_identity_best_relative_error": gradient_error,
            "gradient_identity_steps": fd_rows,
            "energy": energy,
            "residual_l2": l2_norm(residual, params)
        })

    orders = observed_orders(grids, residual_errors)
    energy_orders = observed_orders(grids, energy_errors)
    assertions: list[dict[str, Any]] = []
    authority = manifest["authority"]
    hash_rows = {
        "p1_backend": sha256(BACKEND_PATH),
        "p1_manifest": sha256(P1_MANIFEST),
        "p2_manifest": sha256(P2_MANIFEST)
    }
    for key, actual in hash_rows.items():
        expected = authority[key]["sha256"]
        check(f"{key}_hash", actual == expected, f"actual={actual}; expected={expected}", assertions)
    check("all_classii_channels_active", all(float(params[key]) != 0.0 for key in ("cJJ", "cJK", "cKK", "alpha_X", "beta_X")), "all pinned Class-II coefficients are nonzero", assertions)
    check("positive_manufactured_density", min(float(np.min(np.sum(np.abs(manufactured_field(n, params)) ** 2, axis=0))) for n in grids) > 1000.0 * float(params["rho_regularizer"]), "manufactured density stays far above the rho floor", assertions)
    check("reference_projection_stable", max(reference_errors) <= float(acceptance["reference_projection_relative_error_max"]), f"max={max(reference_errors):.6e}", assertions)
    check("residual_error_monotone", all(residual_errors[i + 1] < residual_errors[i] for i in range(len(residual_errors) - 1)), f"errors={residual_errors}", assertions)
    energy_floor = float(acceptance["energy_roundoff_floor"])
    energy_monotone = all(
        energy_errors[i + 1] < energy_errors[i] or max(energy_errors[i], energy_errors[i + 1]) <= energy_floor
        for i in range(len(energy_errors) - 1)
    )
    check("energy_error_monotone_above_roundoff", energy_monotone, f"errors={energy_errors}; floor={energy_floor}", assertions)
    check("final_residual_error", residual_errors[-1] <= float(acceptance["final_collocation_to_projected_reference_relative_error_max"]), f"final={residual_errors[-1]:.6e}", assertions)
    check("final_energy_error", energy_errors[-1] <= float(acceptance["final_energy_relative_error_max"]), f"final={energy_errors[-1]:.6e}", assertions)
    check("gradient_identity", max(gradient_errors) <= float(acceptance["gradient_identity_relative_error_max"]), f"max={max(gradient_errors):.6e}", assertions)
    check("observed_spatial_order", min(orders) >= float(acceptance["minimum_observed_spatial_order"]), f"orders={orders}", assertions)
    check("spectral_not_exact_galerkin_label", manifest["spatial_discretization"]["honesty_boundary"].startswith("R_N^C is not called exact Galerkin"), "collocation and Galerkin residuals remain distinct", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-spatial-consistency-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-SPATIAL-CONSISTENCY-PASS" if passed == len(assertions) else "A3-FULL-SPATIAL-CONSISTENCY-FAIL",
        "scope": "analytic manufactured field; same-backend oversampled projected reference; pinned full-production parameters; eta_shell=0; CPU complex128",
        "not_closed_here": ["independent continuum-residual implementation", "finite-time convergence", "Hessian/Ritz convergence", "CPU/GPU and complex precision cross-check", "full P3 tier review"],
        "authority_hashes": hash_rows,
        "grids": grids,
        "reference_grids": reference_grids,
        "rows": rows,
        "residual_observed_orders": orders,
        "energy_observed_orders": energy_orders,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Residual errors: {residual_errors}")
    print(f"Observed orders: {orders}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
