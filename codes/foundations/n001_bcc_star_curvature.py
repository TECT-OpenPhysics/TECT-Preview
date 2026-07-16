#!/usr/bin/env python3
"""Projected q0/BCC-star curvature audit for an N-001 homogeneous branch.

This is an experimental diagnostic.  It evaluates the solver's matrix-free
projected Hessian on the commensurate BCC {110} Fourier-star subspace around
stored ``Psi_star.npy`` fields.  It does not create or promote a claim.
"""

__version__ = "1.0.0"
__claims__ = []

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ROOT = Path(r"C:\Dev\Runs\q1a_final_pubgrade_compat_v2\refinement")
DEFAULT_PDE_ROOT = Path(r"C:\Dev\Codes\PDE")
DEFAULT_OUTPUT = REPO / "reviews" / "2026-07-16-n001-bcc-star-curvature.json"
DEFAULT_GRIDS = (32,)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def import_solver(pde_root: Path):
    if str(pde_root) not in sys.path:
        sys.path.insert(0, str(pde_root))
    solver_path = pde_root / "tect_newton_krylov.py"
    spec = importlib.util.spec_from_file_location("tect_newton_krylov_external", solver_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import solver from {solver_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_bcc_pairs() -> list[tuple[int, int, int]]:
    pairs: list[tuple[int, int, int]] = []
    base = (1, 1, 0)
    seen: set[tuple[int, int, int]] = set()
    for zero_pos in range(3):
        idx = [0, 1, 2]
        idx.remove(zero_pos)
        for s0 in (-1, 1):
            for s1 in (-1, 1):
                vec = [0, 0, 0]
                vec[idx[0]] = s0
                vec[idx[1]] = s1
                t = tuple(vec)
                neg = tuple(-x for x in t)
                key = min(t, neg)
                if key not in seen:
                    seen.add(key)
                    pairs.append(t)
    if len(pairs) != 6:
        raise AssertionError(f"expected 6 antipodal BCC pairs, got {len(pairs)}")
    return pairs


def real_basis_for_pair(
    solver: Any,
    shape: tuple[int, int, int, int],
    pair: tuple[int, int, int],
) -> list[np.ndarray]:
    channels, n, _, _ = shape
    if channels != 3:
        raise ValueError(f"expected 3 channels, got {channels}")
    grid = np.indices((n, n, n), dtype=np.float64)
    phase = (2.0 * math.pi / n) * (
        pair[0] * grid[0] + pair[1] * grid[1] + pair[2] * grid[2]
    )
    cos_phase = np.cos(phase)
    sin_phase = np.sin(phase)
    vectors: list[np.ndarray] = []
    for channel in range(channels):
        for profile in (cos_phase, sin_phase):
            for factor in (1.0 + 0.0j, 0.0 + 1.0j):
                field = np.zeros(shape, dtype=np.complex128)
                field[channel] = factor * profile
                x = solver.flatten_complex_field(field)
                norm = solver.real_norm(x)
                if norm <= 0.0:
                    raise ValueError("zero BCC-star basis vector")
                vectors.append(x / norm)
    return vectors


def gram_schmidt(solver: Any, vectors: list[np.ndarray], tol: float) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for vector in vectors:
        w = np.array(vector, dtype=np.float64, copy=True)
        for q in out:
            w -= solver.real_inner(q, w) * q
        norm = solver.real_norm(w)
        if norm > tol:
            out.append(w / norm)
    return out


def pair_matrix(
    solver: Any,
    operator: Any,
    projector: Any,
    pair: tuple[int, int, int],
    shape: tuple[int, int, int, int],
    tol: float,
) -> dict[str, Any]:
    basis = gram_schmidt(solver, real_basis_for_pair(solver, shape, pair), tol)
    projected: list[np.ndarray] = []
    for vector in basis:
        pv = projector.project(vector) if projector is not None else vector
        norm = solver.real_norm(pv)
        if norm > tol:
            projected.append(pv / norm)
    basis = gram_schmidt(solver, projected, tol)
    dim = len(basis)
    matrix = np.zeros((dim, dim), dtype=np.float64)
    images: list[np.ndarray] = []
    for vector in basis:
        images.append(operator.matvec(vector))
    for i, left in enumerate(basis):
        for j, image in enumerate(images):
            matrix[i, j] = solver.real_inner(left, image)
    sym = 0.5 * (matrix + matrix.T)
    eigvals = np.linalg.eigvalsh(sym)
    return {
        "pair": list(pair),
        "subspace_dim": dim,
        "lambda_min": float(eigvals[0]),
        "lambda_max": float(eigvals[-1]),
        "eigenvalues": [float(x) for x in eigvals],
        "antisymmetry_fro_norm": float(np.linalg.norm(matrix - matrix.T)),
    }


def analyze_grid(
    solver: Any,
    run_root: Path,
    grid_n: int,
    *,
    zero_tol: float,
    pair_limit: int | None,
) -> dict[str, Any]:
    grid_dir = run_root / f"N{grid_n}"
    psi_path = grid_dir / "Psi_star.npy"
    config_path = grid_dir / "config.json"
    proof_path = grid_dir / "proof_results.json"
    if not psi_path.exists() or not config_path.exists() or not proof_path.exists():
        raise FileNotFoundError(f"missing N{grid_n} run artefacts under {grid_dir}")

    params = load_json(config_path)
    params.setdefault("L", float(params.get("Lx", 1.0)))
    proof = load_json(proof_path)
    psi = np.load(psi_path, allow_pickle=False)
    solver.validate_tect_field(psi, expected_n=grid_n, label=f"N{grid_n} Psi_star")

    projector = solver.build_zero_mode_projector(
        psi,
        params,
        include_translations=True,
        include_global_phase=False,
    )
    operator = solver.HessianOperator(
        Psi=psi,
        params=params,
        projector=projector,
        use_symmetrised_cII=False,
    )

    q0 = float(params["q0"])
    length = float(proof.get("L", params.get("L", params.get("Lx"))))
    fundamental = 2.0 * math.pi / length
    m_bcc = int(round(q0 / (math.sqrt(2.0) * fundamental)))
    if m_bcc < 1:
        raise ValueError(f"computed invalid BCC integer m={m_bcc}")
    pairs = [(m_bcc * a, m_bcc * b, m_bcc * c) for a, b, c in canonical_bcc_pairs()]
    if pair_limit is not None:
        pairs = pairs[:pair_limit]
    shell_k = math.sqrt(2.0) * m_bcc * fundamental
    pair_results = []
    for index, pair in enumerate(pairs, start=1):
        print(f"N{grid_n}: BCC pair {index}/{len(pairs)} {pair}", flush=True)
        pair_results.append(pair_matrix(solver, operator, projector, pair, psi.shape, zero_tol))
    lambda_min = min(item["lambda_min"] for item in pair_results)
    return {
        "grid": grid_n,
        "L": length,
        "q0": q0,
        "fundamental_k": fundamental,
        "bcc_integer_m": m_bcc,
        "bcc_shell_k": shell_k,
        "relative_q0_mismatch": abs(shell_k - q0) / q0,
        "projector_zero_modes": int(getattr(projector, "n_basis", projector.basis.shape[0])),
        "phase1_projected_residual": proof.get("phase1", {}).get("final_projected_grad_norm"),
        "phase2_lambda_min_recorded": proof.get("phase2", {}).get("lambda_min"),
        "star_pairs": pair_results,
        "bcc_star_pairs_evaluated": len(pair_results),
        "bcc_star_pairs_total": len(canonical_bcc_pairs()),
        "bcc_star_lambda_min": float(lambda_min),
        "bcc_star_n_negative": int(sum(1 for item in pair_results for x in item["eigenvalues"] if x < -zero_tol)),
        "bcc_star_n_near_zero": int(sum(1 for item in pair_results for x in item["eigenvalues"] if abs(x) <= zero_tol)),
        "diagnosis": "BCC_STAR_POSITIVE" if lambda_min > zero_tol else ("BCC_STAR_NEGATIVE" if lambda_min < -zero_tol else "BCC_STAR_NEAR_ZERO"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--pde-root", type=Path, default=DEFAULT_PDE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--grids", nargs="+", type=int, default=list(DEFAULT_GRIDS))
    parser.add_argument("--pair-limit", type=int, default=None,
                        help="limit the number of antipodal BCC {110} pairs; use 1 for a fast representative audit")
    parser.add_argument("--zero-tol", type=float, default=1e-8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    solver = import_solver(args.pde_root)
    results = [
        analyze_grid(solver, args.run_root, grid, zero_tol=args.zero_tol,
                     pair_limit=args.pair_limit)
        for grid in args.grids
    ]
    min_curvature = min(item["bcc_star_lambda_min"] for item in results)
    if min_curvature > args.zero_tol:
        diagnosis = "POSITIVE_Q0_BCC_STAR_CURVATURE"
    elif min_curvature < -args.zero_tol:
        diagnosis = "NEGATIVE_Q0_BCC_STAR_CURVATURE"
    else:
        diagnosis = "NEAR_ZERO_Q0_BCC_STAR_CURVATURE"

    sources = {
        str(args.pde_root / "tect_newton_krylov.py"): sha256(args.pde_root / "tect_newton_krylov.py"),
        str(args.pde_root / "real_backend_pt_bcc_mixed_v3.py"): sha256(args.pde_root / "real_backend_pt_bcc_mixed_v3.py"),
        str(args.pde_root / "v24_thresholds.py"): sha256(args.pde_root / "v24_thresholds.py"),
        str(Path(__file__).resolve()): sha256(Path(__file__).resolve()),
    }
    evidence = {
        "schema": "TECT-N001-bcc-star-curvature-v1",
        "date_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "status": "experimental_diagnostic_only_no_claim_or_tier_change",
        "script_version": __version__,
        "run_root": str(args.run_root),
        "pde_root": str(args.pde_root),
        "pair_limit": args.pair_limit,
        "grids": results,
        "minimum_recorded_bcc_star_curvature": float(min_curvature),
        "diagnosis": diagnosis,
        "scope_exclusions": [
            "No global-minimum conclusion.",
            "No full-spectrum stability conclusion.",
            "No BCC branch existence or nonexistence theorem.",
            "No Reading-H/BCC downstream claim.",
        ],
        "source_sha256": sources,
    }
    output = args.output if args.output.is_absolute() else REPO / args.output
    write_json(output, evidence)
    print(f"Diagnosis: {diagnosis}")
    print(f"Minimum q0/BCC-star curvature: {min_curvature:.12g}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
