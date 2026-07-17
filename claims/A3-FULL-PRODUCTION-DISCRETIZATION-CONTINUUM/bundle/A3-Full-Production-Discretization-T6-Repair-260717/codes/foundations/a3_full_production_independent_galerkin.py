#!/usr/bin/env python3
"""Stage-5 independent continuum-quadrature/Galerkin audit for P3.

For a field in S_N, this program prolongs it exactly to oversampled grids M,
evaluates the real gradient of an independently implemented trapezoid-quadrature
functional, and Fourier-projects the result back to S_N.  The resulting
P_N R_M^P is an independently implemented continuum-quadrature proxy, not an
assertion that the canonical collocation residual is already exact Galerkin.
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
import torch

import a3_full_production_portable_backend as portable
import a3_full_production_spatial_consistency as spatial

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BACKEND_PATH = REPO / "codes" / "foundations" / "n001_variational_backend.py"
PORTABLE_PATH = REPO / "codes" / "foundations" / "a3_full_production_portable_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-independent-galerkin" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_backend() -> Any:
    spec = importlib.util.spec_from_file_location("p3_independent_galerkin_canonical", BACKEND_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prolong(value: np.ndarray, target: int) -> np.ndarray:
    source = int(value.shape[-1])
    if value.shape[-3:] != (source, source, source) or target < source or (target - source) % 2:
        raise ValueError("prolongation requires same-parity cubic grids with target >= source")
    coefficients = spatial.fourier_coefficients(value)
    padded = np.zeros((*value.shape[:-3], target, target, target), dtype=np.complex128)
    start = (target - source) // 2
    padded[..., start:start + source, start:start + source, start:start + source] = coefficients
    axes = (-3, -2, -1)
    return np.fft.ifftn(np.fft.ifftshift(padded, axes=axes), axes=axes) * (target ** 3)


def observed_orders(grids: list[int], errors: list[float]) -> list[float]:
    return [math.log(errors[i] / errors[i + 1]) / math.log(grids[i + 1] / grids[i]) for i in range(len(errors) - 1)]


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
    stage = manifest["stage5"]
    acceptance = stage["acceptance"]
    grids = [int(value) for value in stage["grids"]]
    references = [int(value) for value in stage["reference_grids"]]
    canonical = load_backend()

    rows = []
    independent_errors = []
    reference_errors = []
    prolongation_errors = []
    portable_canonical_errors = []
    high_portable_canonical_errors = []
    for n in grids:
        low_field = spatial.manufactured_field(n, params)
        canonical_residual = canonical.residual(low_field, params)
        _, portable_low_residual = portable.energy_residual(low_field, params, "cpu", torch.complex128)
        portable_canonical_errors.append(spatial.relative_l2(portable_low_residual, canonical_residual, params))
        reference_residuals: dict[int, np.ndarray] = {}
        high_comparison: dict[int, float] = {}
        field_prolongation: dict[int, float] = {}
        for m in references:
            lifted = prolong(low_field, m)
            direct = spatial.manufactured_field(m, params)
            field_prolongation[m] = spatial.relative_l2(lifted, direct, params)
            _, portable_high_residual = portable.energy_residual(lifted, params, "cpu", torch.complex128)
            canonical_high_residual = canonical.residual(lifted, params)
            high_comparison[m] = spatial.relative_l2(portable_high_residual, canonical_high_residual, params)
            reference_residuals[m] = spatial.project(portable_high_residual, n)
        coarse, fine = references
        independent_error = spatial.relative_l2(canonical_residual, reference_residuals[fine], params)
        reference_error = spatial.relative_l2(reference_residuals[coarse], reference_residuals[fine], params)
        independent_errors.append(independent_error)
        reference_errors.append(reference_error)
        prolongation_errors.extend(field_prolongation.values())
        high_portable_canonical_errors.extend(high_comparison.values())
        rows.append({
            "grid": n,
            "collocation_to_independent_proxy_relative_l2": independent_error,
            "independent_reference_projection_relative_l2": reference_error,
            "portable_vs_canonical_low_relative_l2": portable_canonical_errors[-1],
            "prolongation_relative_l2": field_prolongation,
            "portable_vs_canonical_high_relative_l2": high_comparison,
        })

    orders = observed_orders(grids, independent_errors)
    assertions: list[dict[str, Any]] = []
    check("canonical_backend_hash", sha256(BACKEND_PATH) == manifest["authority"]["p1_backend"]["sha256"], sha256(BACKEND_PATH), assertions)
    check("portable_backend_hash", sha256(PORTABLE_PATH) == manifest["authority"]["portable_backend"]["sha256"], sha256(PORTABLE_PATH), assertions)
    check("positive_manufactured_density", min(float(np.min(np.sum(np.abs(spatial.manufactured_field(n, params)) ** 2, axis=0))) for n in grids) > 1000.0 * float(params["rho_regularizer"]), "all target fields remain far above rho floor", assertions)
    check("exact_fourier_prolongation", max(prolongation_errors) <= float(acceptance["prolongation_relative_error_max"]), f"max={max(prolongation_errors):.6e}", assertions)
    check("portable_canonical_low_agreement", max(portable_canonical_errors) <= float(acceptance["portable_vs_canonical_relative_error_max"]), f"max={max(portable_canonical_errors):.6e}", assertions)
    check("portable_canonical_high_agreement", max(high_portable_canonical_errors) <= float(acceptance["portable_vs_canonical_relative_error_max"]), f"max={max(high_portable_canonical_errors):.6e}", assertions)
    check("independent_reference_stable", max(reference_errors) <= float(acceptance["reference_projection_relative_error_max"]), f"max={max(reference_errors):.6e}", assertions)
    check("collocation_to_independent_proxy_monotone", all(independent_errors[i + 1] < independent_errors[i] for i in range(len(independent_errors) - 1)), f"errors={independent_errors}", assertions)
    check("final_collocation_to_independent_proxy", independent_errors[-1] <= float(acceptance["final_collocation_to_independent_proxy_relative_error_max"]), f"final={independent_errors[-1]:.6e}", assertions)
    check("independent_proxy_observed_order", min(orders) >= float(acceptance["minimum_observed_order"]), f"orders={orders}", assertions)
    check("proxy_scope_declared", "P_N R_M^P" in stage["independent_continuum_proxy"], "manifest fixes the independently implemented quadrature proxy", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-independent-galerkin-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-INDEPENDENT-GALERKIN-PASS" if passed == len(assertions) else "A3-FULL-INDEPENDENT-GALERKIN-FAIL",
        "scope": "analytic nonzero-density manufactured field; exact Fourier prolongation; independently implemented portable trapezoid-quadrature gradient on M=24,32; CPU complex128",
        "not_closed_here": ["analytic error bound uniform over P2 solution balls", "GPU cross-device rows", "historical solver convergence", "Sector-B candidate continuum certificate"],
        "rows": rows,
        "independent_errors": independent_errors,
        "reference_errors": reference_errors,
        "observed_orders": orders,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Independent-proxy errors: {independent_errors}")
    print(f"Observed orders: {orders}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
