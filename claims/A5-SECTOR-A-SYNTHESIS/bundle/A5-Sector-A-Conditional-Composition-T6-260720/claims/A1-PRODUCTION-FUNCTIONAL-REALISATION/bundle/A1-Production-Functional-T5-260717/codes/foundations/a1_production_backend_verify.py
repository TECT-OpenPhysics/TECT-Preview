#!/usr/bin/env python3
"""Independent multi-grid verifier for the P1 standalone variational backend.

The verifier imports only ``n001_variational_backend``.  It independently
constructs fields, finite differences, the real torus pairing, and the analytic
one-component scalar reduction.  It refuses to run if the backend SHA-256 does
not match the P1 manifest and persists every tested value as claim evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
FOUNDATIONS = REPO / "codes" / "foundations"
if str(FOUNDATIONS) not in sys.path:
    sys.path.insert(0, str(FOUNDATIONS))

import n001_variational_backend as backend  # noqa: E402

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

CLAIM = "A1-PRODUCTION-FUNCTIONAL-REALISATION"
MANIFEST = REPO / "claims" / CLAIM / "production_functional_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / "2026-07-17-production-backend-multigrid" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def real_pairing(u: np.ndarray, v: np.ndarray, dvol: float) -> float:
    return float(dvol * np.real(np.vdot(u, v)))


def relative_scalar(lhs: float, rhs: float) -> float:
    return float(abs(lhs - rhs) / max(1.0, abs(lhs), abs(rhs)))


def relative_field(lhs: np.ndarray, rhs: np.ndarray) -> float:
    return float(np.linalg.norm((lhs - rhs).ravel()) / max(1.0, np.linalg.norm(lhs.ravel()), np.linalg.norm(rhs.ravel())))


def dvol(n: int, params: dict[str, Any]) -> float:
    return math.prod(float(params[key]) / n for key in ("Lx", "Ly", "Lz"))


def unit_direction(rng: np.random.Generator, shape: tuple[int, ...], volume_element: float) -> np.ndarray:
    value = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    return value / math.sqrt(real_pairing(value, value, volume_element))


def make_fields(n: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(260717 + n)
    axes = np.arange(n, dtype=float)
    x, y, z = np.meshgrid(axes, axes, axes, indexing="ij")
    base = np.asarray([0.55 + 0.15j, 0.35 - 0.20j, 0.25 + 0.10j], dtype=np.complex128)[:, None, None, None]
    homogeneous = np.broadcast_to(base, (3, n, n, n)).copy()
    random = homogeneous + 0.05 * (rng.normal(size=homogeneous.shape) + 1j * rng.normal(size=homogeneous.shape))
    shell_phase = np.exp(2j * math.pi * (x + y + z) / n)
    q0_shell = homogeneous + np.asarray([0.11, -0.07j, 0.05], dtype=np.complex128)[:, None, None, None] * shell_phase
    classii = homogeneous.copy()
    classii[0] += 0.10 * shell_phase
    classii[1] += 0.08j * np.conj(shell_phase)
    classii[2] += 0.04 * np.exp(2j * math.pi * (x - y) / n)
    return {
        "zero": np.zeros_like(homogeneous),
        "homogeneous": homogeneous,
        "random": random,
        "q0-shell": q0_shell,
        "classII-active": classii,
    }


def analytic_scalar_residual(psi: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    """Independent one-component Brazovskii residual in Fourier form."""
    n = int(psi.shape[1])
    axes = [
        2.0 * math.pi * np.fft.fftfreq(n, d=float(params[key]) / n)
        for key in ("Lx", "Ly", "Lz")
    ]
    kx, ky, kz = np.meshgrid(*axes, indexing="ij")
    k2 = kx * kx + ky * ky + kz * kz
    symbol = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2 * k2
    out = np.zeros_like(psi)
    out[0] = np.fft.ifftn(symbol * np.fft.fftn(psi[0]))
    rho = np.abs(psi[0]) ** 2
    out[0] += float(params["lambda"]) * rho * psi[0] + float(params["gamma"]) * rho * rho * psi[0]
    return out


def scalar_reduction_case(n: int, params: dict[str, Any]) -> float:
    rng = np.random.default_rng(117 + n)
    psi = np.zeros((3, n, n, n), dtype=np.complex128)
    psi[0] = 0.45 + 0.06 * (rng.normal(size=(n, n, n)) + 1j * rng.normal(size=(n, n, n)))
    scalar = dict(params)
    scalar.update({
        "family_masses": [0.0, 0.0, 0.0],
        "k_lock": 0.0,
        "eta_shell": 0.0,
        "alpha_X": 0.0,
        "beta_X": 0.0,
        "cJJ": 0.0,
        "cJK": 0.0,
        "cKK": 0.0,
    })
    return relative_field(backend.residual(psi, scalar), analytic_scalar_residual(psi, scalar))


def run_case(n: int, variant: str, params: dict[str, Any], field_name: str, psi: np.ndarray, rng: np.random.Generator, steps: list[float]) -> dict[str, Any]:
    volume_element = dvol(n, params)
    direction = unit_direction(rng, psi.shape, volume_element)
    other = unit_direction(rng, psi.shape, volume_element)
    residual = backend.residual(psi, params)
    hv = backend.hessian_vec(psi, direction, params)
    hu = backend.hessian_vec(psi, other, params)
    records = []
    for step in steps:
        fd_energy = (backend.energy(psi + step * direction, params) - backend.energy(psi - step * direction, params)) / (2.0 * step)
        fd_residual = (backend.residual(psi + step * direction, params) - backend.residual(psi - step * direction, params)) / (2.0 * step)
        records.append({
            "step": step,
            "energy_directional": fd_energy,
            "variational_rel_error": relative_scalar(fd_energy, real_pairing(residual, direction, volume_element)),
            "dr_hessian_rel_error": relative_field(fd_residual, hv),
        })
    return {
        "grid": n,
        "variant": variant,
        "field": field_name,
        "symmetry_rel_error": relative_scalar(
            real_pairing(other, hv, volume_element),
            real_pairing(hu, direction, volume_element),
        ),
        "steps": records,
    }


def maximum(rows: list[dict[str, Any]], metric: str) -> float:
    values: list[float] = []
    for row in rows:
        if metric == "symmetry_rel_error":
            values.append(float(row[metric]))
        else:
            values.extend(float(record[metric]) for record in row["steps"])
    return max(values, default=0.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grids", nargs="+", type=int, default=[4, 6, 8])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if sorted(set(args.grids)) != sorted(args.grids) or any(n < 4 for n in args.grids):
        raise SystemExit("--grids must be unique integers >=4")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = REPO / manifest["production_reference_backend"]["path"]
    expected_hash = manifest["production_reference_backend"]["sha256"]
    checks: dict[str, bool] = {
        "backend_source_exists": source.is_file(),
        "backend_source_hash": source.is_file() and sha256(source) == expected_hash,
        "backend_version": backend.__version__ == manifest["production_reference_backend"]["version"],
    }
    params = manifest["parameters"]
    steps = [float(value) for value in manifest["test_matrix"]["finite_difference_steps"]]
    rows: list[dict[str, Any]] = []
    scalar_errors: dict[str, float] = {}
    for n in args.grids:
        scalar_errors[str(n)] = scalar_reduction_case(n, params)
        fields = make_fields(n)
        rng = np.random.default_rng(991 + n)
        variants = [("pinned-production", dict(params)), ("shell-bias-activation", dict(params))]
        variants[1][1]["eta_shell"] = 0.07  # manifest-declared audit activation
        for variant, configured in variants:
            for field_name, psi in fields.items():
                rows.append(run_case(n, variant, configured, field_name, psi, rng, steps))

    thresholds = {
        "variational": 2e-6,
        "hessian": 2e-5,
        "symmetry": 5e-8,
        "scalar_reduction": 2e-11,
    }
    checks.update({
        "three_or_more_grids": len(args.grids) >= 3,
        "all_required_fields": {row["field"] for row in rows} == {"zero", "homogeneous", "random", "q0-shell", "classII-active"},
        "all_couplings_active": all(float(params[key]) != 0.0 for key in ("lambda", "gamma", "cJJ", "cJK", "cKK", "alpha_X", "beta_X", "M_X")),
        "variational_identity": maximum(rows, "variational_rel_error") < thresholds["variational"],
        "hessian_identity": maximum(rows, "dr_hessian_rel_error") < thresholds["hessian"],
        "real_hessian_symmetry": maximum(rows, "symmetry_rel_error") < thresholds["symmetry"],
        "exact_scalar_reduction": max(scalar_errors.values()) < thresholds["scalar_reduction"],
    })
    assertions = [
        {"name": name, "pass": passed}
        for name, passed in checks.items()
    ]
    all_pass = all(item["pass"] for item in assertions)
    result = {
        "schema": "tect/a1-production-variational-backend-multigrid/1.0",
        "date": "2026-07-17",
        "claim_id": CLAIM,
        "verdict": "PRODUCTION-BACKEND-MULTIGRID-PASS" if all_pass else "PRODUCTION-BACKEND-MULTIGRID-FAIL",
        "grids": args.grids,
        "source": {"path": source.relative_to(REPO).as_posix(), "sha256": sha256(source), "version": backend.__version__},
        "thresholds": thresholds,
        "maxima": {
            "variational_rel_error": maximum(rows, "variational_rel_error"),
            "dr_hessian_rel_error": maximum(rows, "dr_hessian_rel_error"),
            "symmetry_rel_error": maximum(rows, "symmetry_rel_error"),
            "scalar_reduction_rel_error": max(scalar_errors.values()),
        },
        "scalar_reduction_by_grid": scalar_errors,
        "assertions": assertions,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for item in assertions:
        print(f"{'PASS' if item['pass'] else 'FAIL'}: {item['name']}")
    print(f"P1 production backend: {result['verdict']}")
    print(f"  grids: {args.grids}")
    print(f"  max variational error: {result['maxima']['variational_rel_error']:.3e}")
    print(f"  max Hessian error: {result['maxima']['dr_hessian_rel_error']:.3e}")
    print(f"  max symmetry error: {result['maxima']['symmetry_rel_error']:.3e}")
    print(f"  max scalar-reduction error: {result['maxima']['scalar_reduction_rel_error']:.3e}")
    print(f"  evidence: {args.output}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
