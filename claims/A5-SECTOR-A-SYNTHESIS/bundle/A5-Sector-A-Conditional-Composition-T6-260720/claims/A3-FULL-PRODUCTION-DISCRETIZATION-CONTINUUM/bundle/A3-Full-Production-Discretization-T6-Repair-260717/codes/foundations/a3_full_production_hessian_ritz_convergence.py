#!/usr/bin/env python3
"""Stage-3 Hessian/Ritz convergence audit for the full-production P3 claim.

The audit separates two statements.  At a homogeneous Class-II-active
background, a complete real Fourier block is tested for invariance and an
isolated lowest Ritz cluster receives a residual/gap certificate.  At the
nonuniform manufactured background, a fixed low-frequency Ritz matrix is
tested only for grid convergence; it is not relabelled as a full-spectrum
eigenvalue calculation.
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

import a3_full_production_spatial_consistency as spatial

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BACKEND_PATH = REPO / "codes" / "foundations" / "n001_variational_backend.py"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-hessian-ritz-convergence" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_backend() -> Any:
    spec = importlib.util.spec_from_file_location("p3_ritz_backend", BACKEND_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned P1 backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dvol(n: int, params: dict[str, Any]) -> float:
    return math.prod(float(params[key]) / n for key in ("Lx", "Ly", "Lz"))


def pairing(left: np.ndarray, right: np.ndarray, params: dict[str, Any]) -> float:
    return dvol(int(left.shape[-1]), params) * float(np.vdot(left, right).real)


def normalize(value: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    length = math.sqrt(pairing(value, value, params))
    if length <= 0.0:
        raise ValueError("zero real basis vector")
    return value / length


def gram_error(basis: list[np.ndarray], params: dict[str, Any]) -> float:
    gram = np.array([[pairing(left, right, params) for right in basis] for left in basis])
    return float(np.linalg.norm(gram - np.eye(len(basis)), ord=np.inf))


def profile(n: int, mode: tuple[int, int, int], kind: str, params: dict[str, Any]) -> np.ndarray:
    xyz = spatial.coordinates(n, params)
    angle = sum(2.0 * math.pi * component * coord / float(params[key]) for component, coord, key in zip(mode, xyz, ("Lx", "Ly", "Lz")))
    return np.cos(angle) if kind == "cos" else np.sin(angle)


def homogeneous_basis(n: int, mode: tuple[int, int, int], params: dict[str, Any]) -> list[np.ndarray]:
    basis = []
    for kind in ("cos", "sin"):
        wave = profile(n, mode, kind, params)
        for channel in range(3):
            for factor in (1.0 + 0.0j, 0.0 + 1.0j):
                value = np.zeros((3, n, n, n), dtype=np.complex128)
                value[channel] = factor * wave
                basis.append(normalize(value, params))
    return basis


def manufactured_basis(n: int, params: dict[str, Any]) -> list[np.ndarray]:
    specifications = [
        ((0, 0, 0), "cos", 0, 1.0 + 0.0j),
        ((1, 0, 0), "cos", 1, 0.0 + 1.0j),
        ((0, 1, 0), "sin", 2, 1.0 + 0.0j),
        ((0, 0, 1), "cos", 0, 0.0 + 1.0j),
        ((1, 1, 0), "sin", 1, 1.0 + 0.0j),
        ((1, 0, -1), "cos", 2, 0.0 + 1.0j),
        ((-1, 1, 0), "sin", 0, 1.0 + 0.0j),
        ((0, 1, 1), "cos", 1, 0.0 + 1.0j),
    ]
    basis = []
    for mode, kind, channel, factor in specifications:
        value = np.zeros((3, n, n, n), dtype=np.complex128)
        value[channel] = factor * profile(n, mode, kind, params)
        basis.append(normalize(value, params))
    return basis


def hessian_stress_field(n: int, params: dict[str, Any]) -> np.ndarray:
    """Declared nonuniform test input with enough bandwidth to expose N=8 aliasing."""
    xyz = spatial.coordinates(n, params)
    value = np.zeros((3, n, n, n), dtype=np.complex128)
    value[0] = 0.35 + 0.080 * spatial.phase((2, 0, 0), xyz, params) + 0.060j * spatial.phase((0, -3, 0), xyz, params) + 0.040 * spatial.phase((2, 2, 0), xyz, params)
    value[1] = 0.28 * np.exp(0.2j) + 0.070 * spatial.phase((0, 0, 3), xyz, params) - 0.050j * spatial.phase((2, 0, -2), xyz, params)
    value[2] = 0.22 * np.exp(-0.1j) + 0.060 * spatial.phase((-2, 2, 0), xyz, params) + 0.040j * spatial.phase((0, 2, 2), xyz, params)
    return value


def ritz_data(backend: Any, field: np.ndarray, basis: list[np.ndarray], params: dict[str, Any]) -> dict[str, Any]:
    images = [backend.hessian_vec(field, vector, params) for vector in basis]
    matrix = np.array([[pairing(left, image, params) for image in images] for left in basis])
    symmetric = 0.5 * (matrix + matrix.T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    scale = max(float(np.linalg.norm(symmetric, ord=2)), 1e-30)
    antisymmetry = float(np.linalg.norm(matrix - matrix.T, ord=2) / scale)
    complement_defects = []
    for image in images:
        projected = sum(pairing(vector, image, params) * vector for vector in basis)
        complement_defects.append(spatial.l2_norm(image - projected, params) / max(spatial.l2_norm(image, params), 1e-30))
    ritz_residuals = []
    for index, eigenvalue in enumerate(eigenvalues):
        coefficients = eigenvectors[:, index]
        vector = sum(coefficients[i] * basis[i] for i in range(len(basis)))
        image = sum(coefficients[i] * images[i] for i in range(len(basis)))
        ritz_residuals.append(spatial.l2_norm(image - eigenvalue * vector, params))
    return {
        "dimension": len(basis),
        "gram_error": gram_error(basis, params),
        "antisymmetry_relative": antisymmetry,
        "subspace_invariance_defect": max(complement_defects),
        "eigenvalues": [float(value) for value in eigenvalues],
        "ritz_residuals": [float(value) for value in ritz_residuals],
    }


def eigenvalue_relative_error(values: list[float], reference: list[float]) -> float:
    left = np.asarray(values, dtype=np.float64)
    right = np.asarray(reference, dtype=np.float64)
    return float(np.max(np.abs(left - right)) / max(float(np.max(np.abs(right))), 1.0))


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
    backend = load_backend()
    stage = manifest["stage3"]
    acceptance = stage["acceptance"]
    grids = [int(value) for value in stage["grids"]]
    reference_grid = int(stage["reference_grid"])
    mode = tuple(int(value) for value in stage["homogeneous_block"]["fourier_mode"])
    multiplicity = int(stage["homogeneous_block"]["lowest_cluster_multiplicity"])

    homogeneous_rows = []
    manufactured_rows = []
    for n in grids + [reference_grid]:
        manufactured = hessian_stress_field(n, params)
        homogeneous = np.broadcast_to(np.mean(manufactured, axis=(-3, -2, -1), keepdims=True), manufactured.shape).copy()
        homogeneous_rows.append({"grid": n, **ritz_data(backend, homogeneous, homogeneous_basis(n, mode, params), params)})
        manufactured_rows.append({"grid": n, **ritz_data(backend, manufactured, manufactured_basis(n, params), params)})

    homogeneous_reference = homogeneous_rows[-1]
    manufactured_reference = manufactured_rows[-1]
    homogeneous_errors = [eigenvalue_relative_error(row["eigenvalues"], homogeneous_reference["eigenvalues"]) for row in homogeneous_rows[:-1]]
    manufactured_errors = [eigenvalue_relative_error(row["eigenvalues"], manufactured_reference["eigenvalues"]) for row in manufactured_rows[:-1]]
    manufactured_orders = observed_orders(grids, manufactured_errors)

    reference_eigenvalues = homogeneous_reference["eigenvalues"]
    cluster_gap = float(reference_eigenvalues[multiplicity] - reference_eigenvalues[multiplicity - 1])
    cluster_residual = max(homogeneous_reference["ritz_residuals"][:multiplicity])
    cluster_ratio = cluster_residual / max(cluster_gap, 1e-30)

    step_rows = []
    step_eigenvalues = []
    n_step = grids[0]
    manufactured_step = spatial.manufactured_field(n_step, params)
    homogeneous_step = np.broadcast_to(np.mean(manufactured_step, axis=(-3, -2, -1), keepdims=True), manufactured_step.shape).copy()
    basis_step = homogeneous_basis(n_step, mode, params)
    for step in stage["hessian_steps"]:
        step_params = dict(params)
        step_params["reference_hessian_step"] = float(step)
        data = ritz_data(backend, homogeneous_step, basis_step, step_params)
        step_eigenvalues.append(data["eigenvalues"])
        step_rows.append({"step": step, "eigenvalues": data["eigenvalues"], "antisymmetry_relative": data["antisymmetry_relative"]})
    step_reference = step_eigenvalues[1]
    step_spread = max(eigenvalue_relative_error(values, step_reference) for values in step_eigenvalues)

    assertions: list[dict[str, Any]] = []
    check("backend_hash", sha256(BACKEND_PATH) == manifest["authority"]["p1_backend"]["sha256"], sha256(BACKEND_PATH), assertions)
    check("declared_homogeneous_dimension", all(row["dimension"] == int(stage["homogeneous_block"]["real_dimension"]) for row in homogeneous_rows), f"dimensions={[row['dimension'] for row in homogeneous_rows]}", assertions)
    check("basis_gram", max(row["gram_error"] for row in homogeneous_rows + manufactured_rows) <= float(acceptance["real_pairing_gram_error_max"]), f"max={max(row['gram_error'] for row in homogeneous_rows + manufactured_rows):.6e}", assertions)
    check("hessian_symmetry", max(row["antisymmetry_relative"] for row in homogeneous_rows + manufactured_rows) <= float(acceptance["hessian_antisymmetry_relative_max"]), f"max={max(row['antisymmetry_relative'] for row in homogeneous_rows + manufactured_rows):.6e}", assertions)
    check("homogeneous_block_invariant", max(row["subspace_invariance_defect"] for row in homogeneous_rows) <= float(acceptance["homogeneous_invariance_defect_max"]), f"max={max(row['subspace_invariance_defect'] for row in homogeneous_rows):.6e}", assertions)
    check("isolated_lowest_cluster_gap", cluster_gap >= float(acceptance["lowest_cluster_gap_min"]), f"gap={cluster_gap:.6e}; multiplicity={multiplicity}", assertions)
    check("cluster_residual_gap_certificate", cluster_ratio <= float(acceptance["cluster_residual_to_gap_max"]), f"residual={cluster_residual:.6e}; gap={cluster_gap:.6e}; ratio={cluster_ratio:.6e}", assertions)
    check("homogeneous_ritz_grid_convergence", homogeneous_errors[-1] <= float(acceptance["final_homogeneous_ritz_relative_error_max"]), f"errors={homogeneous_errors}", assertions)
    check("manufactured_ritz_error_monotone", all(manufactured_errors[i + 1] < manufactured_errors[i] for i in range(len(manufactured_errors) - 1)), f"errors={manufactured_errors}", assertions)
    check("manufactured_ritz_grid_convergence", manufactured_errors[-1] <= float(acceptance["final_manufactured_ritz_relative_error_max"]), f"errors={manufactured_errors}", assertions)
    check("manufactured_ritz_observed_order", min(manufactured_orders) >= float(acceptance["minimum_manufactured_ritz_order"]), f"orders={manufactured_orders}", assertions)
    check("hessian_step_stability", step_spread <= float(acceptance["hessian_step_ritz_relative_spread_max"]), f"spread={step_spread:.6e}", assertions)
    check("nonuniform_ritz_no_full_spectrum_label", "no full-spectrum eigenvalue claim" in stage["manufactured_ritz"]["purpose"], "manifest keeps non-invariant Ritz values scoped", assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-hessian-ritz-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-HESSIAN-RITZ-CONVERGENCE-PASS" if passed == len(assertions) else "A3-FULL-HESSIAN-RITZ-CONVERGENCE-FAIL",
        "scope": "homogeneous invariant Fourier-block residual/gap certificate plus nonuniform fixed-subspace Ritz self-convergence; CPU complex128",
        "not_closed_here": ["full Hessian spectrum at a Sector-B candidate", "independent continuum residual", "CPU/GPU and precision cross-check", "uniform spectral-pollution theorem"],
        "homogeneous_rows": homogeneous_rows,
        "homogeneous_grid_errors": homogeneous_errors,
        "lowest_cluster": {"multiplicity": multiplicity, "gap": cluster_gap, "maximum_ritz_residual": cluster_residual, "residual_to_gap": cluster_ratio},
        "manufactured_rows": manufactured_rows,
        "manufactured_grid_errors": manufactured_errors,
        "manufactured_observed_orders": manufactured_orders,
        "hessian_step_rows": step_rows,
        "hessian_step_relative_spread": step_spread,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)}
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Homogeneous Ritz errors: {homogeneous_errors}")
    print(f"Manufactured Ritz errors: {manufactured_errors}; orders: {manufactured_orders}")
    print(f"Cluster gap/residual ratio: {cluster_gap:.6e} / {cluster_ratio:.6e}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
