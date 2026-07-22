#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# === TECT VERSION HEADER BEGIN ===
# Theory tag    : Math56-Addendum-v2p4-2026-04-20
# Regime        : Brazovskii (lambda<0, gamma>0 sizeable)
# Module version: v1.1
# Sync doc      : /Contents/docs/status/TECT-Theory-Code-Sync.md
# Last synced   : 2026-04-20
# Notes         : Code is version-locked to the above theory tag.
#                 The module-version field tracks the file's own API
#                 generation (filename = <module>_v<N>.py); the theory
#                 tag is global. Re-run PDE/stamp_version_headers.py
#                 after any tag bump or version-table edit.
# === TECT VERSION HEADER END ===
"""
bloch_linearization.py — Stage U2, Module 1
============================================
TECT Bloch-operator extraction: construct L(k) at ordering wavevectors G*.

Physical background
-------------------
At a converged condensate Ψ₀ the second variation of the Brazovskii action
defines the linearised operator

    L[Ψ₀] : δΨ ↦ δR[Ψ₀+εδΨ]/dε|_{ε=0}

which is implemented numerically by `backend.hessian_vec(Ψ₀, v, params)`.

For a translationally invariant condensate the operator is block-diagonal in
k-space; for a structured BCC condensate it has weak off-diagonal coupling.
We extract the (k, k)-block at each ordering wavevector G*:

    L_{ab}(G*) = [FFT(hessian_vec(Ψ₀, e_b·δ_{k,G*}))]_a(G*)

where e_b is the b-th standard basis vector in component space (b = 0,1,2)
and δ_{k,G*} denotes a probe field with a single nonzero Fourier mode at G*.

The analytical (linear-operator) contribution can also be computed without
Ψ₀; this serves as a sanity check and allows decomposing L(G*) into linear
and nonlinear corrections.

API
---
- kgrid_1d(N, L)                  → 1-D k-axis (numpy)
- kgrid_3d(params, Nx, Ny, Nz)   → (kx, ky, kz) triple of 1-D arrays
- nearest_grid_index(k_cont, kgrid_1d) → int (1-D)
- k_to_grid_idx(G_star_cont, kx, ky, kz) → (ix, iy, iz)
- bloch_matrix_at_idx(Psi0, idx, hessian_fn, params) → 3×3 complex ndarray
- bloch_matrix_linear(G_star_cont, params) → 3×3 complex ndarray (linear only)
- bloch_derivative_linear(G_star_cont, direction, params, dk) → 3×3 (linear ∂L/∂k_i)
- bloch_derivative_numerical(Psi0, idx, direction, hessian_fn, params,
                              n_steps=2, order=4) → 3×3 complex ndarray
- bloch_matrices_all_patches(Psi0, patch_centers, q0, hessian_fn, params,
                              dk_steps=1) → list of dicts

Usage
-----
    import importlib, sys
    sys.path.insert(0, "/path/to/PDE")
    backend = importlib.import_module("real_backend_pt_bcc_mixed_v3")

    import numpy as np
    from bloch_linearization import bloch_matrices_all_patches

    Psi0  = np.load("Psi_final.npy")          # shape (3, Nx, Ny, Nz)
    pc    = np.load("patch_centers.npy")       # shape (Npatch, 3)
    q0    = params["q0"]

    results = bloch_matrices_all_patches(
        Psi0, pc, q0,
        hessian_fn=lambda v: backend.hessian_vec(Psi0, v, params),
        params=params,
    )
    # results[i]["L"]  → 3×3 Bloch matrix at G*_i
    # results[i]["G_star"] → continuous k-vector (3,)
    # results[i]["grid_idx"] → (ix, iy, iz)
"""

from __future__ import annotations

import math
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# ============================================================
# k-grid utilities
# ============================================================

def kgrid_1d(N: int, L: float) -> np.ndarray:
    """Standard FFT frequency axis: 2π/L · fftfreq(N)·N."""
    return 2.0 * math.pi * np.fft.fftfreq(N, d=L / N)


def kgrid_3d(
    params: Dict[str, Any],
    Nx: int,
    Ny: int,
    Nz: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (kx, ky, kz) 1-D frequency arrays for the given grid."""
    Lx = float(params["Lx"])
    Ly = float(params["Ly"])
    Lz = float(params["Lz"])
    return kgrid_1d(Nx, Lx), kgrid_1d(Ny, Ly), kgrid_1d(Nz, Lz)


def nearest_grid_index(k_val: float, kaxis: np.ndarray) -> int:
    """Return the index in *kaxis* closest to the continuous value *k_val*."""
    return int(np.argmin(np.abs(kaxis - k_val)))


def k_to_grid_idx(
    G_star: np.ndarray,
    kx: np.ndarray,
    ky: np.ndarray,
    kz: np.ndarray,
) -> Tuple[int, int, int]:
    """
    Map a continuous ordering wavevector G* = (kx*, ky*, kz*) to the
    nearest grid indices (ix, iy, iz).

    Parameters
    ----------
    G_star : (3,) array   continuous k-vector [rad/length]
    kx, ky, kz            1-D frequency axes from kgrid_3d()

    Returns
    -------
    (ix, iy, iz) : int-triple   indices into the 3-D k-array
    """
    ix = nearest_grid_index(G_star[0], kx)
    iy = nearest_grid_index(G_star[1], ky)
    iz = nearest_grid_index(G_star[2], kz)
    return ix, iy, iz


# ============================================================
# Analytical stiffness symbol and its derivatives
# ============================================================

def _s2_spectral(k: np.ndarray) -> float:
    """Spectral Laplacian symbol at a single k-vector (3,)."""
    return float(np.dot(k, k))


def _s2_bcc(k: np.ndarray, a_bcc: float) -> float:
    """BCC Laplacian symbol: (8/a²)(1 − cos(akx/2)cos(aky/2)cos(akz/2))."""
    c = (math.cos(0.5 * a_bcc * k[0]) *
         math.cos(0.5 * a_bcc * k[1]) *
         math.cos(0.5 * a_bcc * k[2]))
    return (8.0 / a_bcc**2) * (1.0 - c)


def _s2_mixed(k: np.ndarray, params: Dict[str, Any]) -> float:
    """mixed_bcc stiffness symbol at a single k-vector."""
    mode = str(params.get("laplacian_mode", "spectral")).lower()
    if mode == "spectral":
        return _s2_spectral(k)
    a_bcc = float(params.get("a_bcc", 1.0))
    s2_bcc = _s2_bcc(k, a_bcc)
    if mode == "bcc_symbol":
        return s2_bcc
    if mode == "mixed_bcc":
        eps = float(params.get("bcc_mix_epsilon", 0.0))
        return (1.0 - eps) * _s2_spectral(k) + eps * s2_bcc
    raise ValueError(f"Unknown laplacian_mode: {mode}")


def _ds2_dk_spectral(k: np.ndarray, i: int) -> float:
    """∂(k²)/∂k_i = 2k_i."""
    return 2.0 * float(k[i])


def _ds2_dk_bcc(k: np.ndarray, i: int, a_bcc: float) -> float:
    """∂s2_bcc/∂k_i using chain rule."""
    kx, ky, kz = k[0], k[1], k[2]
    # s2 = (8/a²)(1 - cx·cy·cz)  where cj = cos(a*kj/2)
    # ∂s2/∂k_i = (8/a²)·cx·cy·cz·(a/2)·tan(a*k_i/2)   ... careful:
    # ∂/∂k_i of cx·cy·cz = -sin(a*k_i/2)·(a/2)·∏_{j≠i} cos(a*k_j/2)
    # so ∂s2/∂k_i = (8/a²)·sin(a*k_i/2)·(a/2)·∏_{j≠i} cos(a*k_j/2)
    c = [math.cos(0.5 * a_bcc * k[j]) for j in range(3)]
    s_i = math.sin(0.5 * a_bcc * k[i])
    prod_others = math.prod(c[j] for j in range(3) if j != i)
    return (8.0 / a_bcc**2) * s_i * (0.5 * a_bcc) * prod_others


def _ds2_dk_mixed(k: np.ndarray, i: int, params: Dict[str, Any]) -> float:
    """∂s₂/∂k_i for the current laplacian_mode."""
    mode = str(params.get("laplacian_mode", "spectral")).lower()
    if mode == "spectral":
        return _ds2_dk_spectral(k, i)
    a_bcc = float(params.get("a_bcc", 1.0))
    d_bcc = _ds2_dk_bcc(k, i, a_bcc)
    if mode == "bcc_symbol":
        return d_bcc
    if mode == "mixed_bcc":
        eps = float(params.get("bcc_mix_epsilon", 0.0))
        return (1.0 - eps) * _ds2_dk_spectral(k, i) + eps * d_bcc
    raise ValueError(f"Unknown laplacian_mode: {mode}")


# ============================================================
# Analytical Bloch matrix: linear operator only
# ============================================================

def bloch_matrix_linear(
    G_star: np.ndarray,
    params: Dict[str, Any],
) -> np.ndarray:
    """
    Compute the 3×3 Bloch matrix arising from the *linear* part of the
    Brazovskii operator at wavevector G*.

    The backend/solver implements the quadratic symbol as
        L_lin(G*) = [r + Z·s₂(G*) + Y·s₂(G*)²] · I₃
                  + M_family + M_lock + M_shellbias

    Note: with the conventional TECT default Z = −1, this gives
        L_lin(G*) = r − |Z|·s₂ + Y·s₂²
    which is negative in the mass term and produces the Brazovskii
    shell instability at the s₂ minimum.

    This sign convention matches _brazovskii_linear_term_t in the backend:
        residual += r*Psi − Z*Laplacian(Psi) + Y*Biharmonic(Psi)
    i.e. L_lin·Ψ = rΨ + Z·(−∇²Ψ) + Y·∇⁴Ψ = (r + Z·s₂ + Y·s₂²)·Ψ_k.

    Parameters
    ----------
    G_star : (3,) ndarray    continuous ordering wavevector
    params : dict            solver parameter dictionary

    Returns
    -------
    L_lin : (3,3) complex128 ndarray
    """
    G = np.asarray(G_star, dtype=float)

    r = float(params.get("r", params.get("mu2", 0.25)))
    Z = float(params.get("Z", -1.0))
    Y = float(params.get("Y", 1.0))

    s2 = _s2_mixed(G, params)
    # FIX(sign): matches backend: L = r + Z*s2 + Y*s2^2
    scalar_diag = r + Z * s2 + Y * s2**2

    L = scalar_diag * np.eye(3, dtype=np.complex128)

    # Family mass matrix
    fam = np.asarray(params.get("family_masses", [0.0, 0.0, 0.0]), dtype=float)
    L += np.diag(fam.astype(np.complex128))

    # Locked-internal penalty  k_lock·(I − P₀)
    k_lock = float(params.get("k_lock", 0.15))
    if abs(k_lock) > 1e-18:
        z0 = np.asarray(params.get("z0", [1.0, 1.0, 1.0]), dtype=np.complex128)
        z0 /= np.linalg.norm(z0)
        P0 = np.outer(z0, np.conj(z0))
        L += k_lock * (np.eye(3, dtype=np.complex128) - P0)

    # Shell-bias penalty  η_shell·(|G*| − q₀)²·I  (if non-zero)
    eta_shell = float(params.get("eta_shell", 0.0))
    if abs(eta_shell) > 1e-18:
        q0 = float(params["q0"])
        kmag = float(np.linalg.norm(G))
        L += eta_shell * (kmag - q0)**2 * np.eye(3, dtype=np.complex128)

    return L


def bloch_derivative_linear(
    G_star: np.ndarray,
    direction: int,
    params: Dict[str, Any],
    dk: float = 1e-4,
) -> np.ndarray:
    """
    Compute K_i^lin = ∂L_lin/∂k_i |_{G*} analytically.

    FIX(sign): matches backend  L = r + Z*s2 + Y*s2^2, so:

    K_i^lin(G*) = [Z·∂s₂/∂k_i + 2Y·s₂·∂s₂/∂k_i]|_{G*} · I₃
                = (Z + 2Y·s₂(G*)) · (∂s₂/∂k_i)|_{G*} · I₃

    The shell-bias and lock terms contribute zero derivative (they depend on
    |k| not k_i individually in a way that also contributes, but the lock
    and family terms are k-independent).  Shell-bias contributes:
        ∂/∂k_i [η·(|k|−q₀)²] = η·2·(|k|−q₀)·k_i/|k|

    Parameters
    ----------
    G_star    : (3,) ndarray    continuous ordering wavevector
    direction : int             0=x, 1=y, 2=z
    params    : dict
    dk        : float           (unused; kept for API symmetry)

    Returns
    -------
    K_i_lin : (3,3) complex128 ndarray
    """
    G = np.asarray(G_star, dtype=float)
    i = int(direction)

    Z = float(params.get("Z", -1.0))
    Y = float(params.get("Y", 1.0))

    s2      = _s2_mixed(G, params)
    ds2_dki = _ds2_dk_mixed(G, i, params)
    # FIX(sign): +Z not -Z, matching L = r + Z*s2 + Y*s2^2
    scalar  = (Z + 2.0 * Y * s2) * ds2_dki

    K = scalar * np.eye(3, dtype=np.complex128)

    # Shell-bias contribution: ∂/∂k_i [η·(|k|−q₀)²] at k=G*
    eta_shell = float(params.get("eta_shell", 0.0))
    if abs(eta_shell) > 1e-18:
        q0   = float(params["q0"])
        kmag = float(np.linalg.norm(G))
        if kmag > 1e-14:
            dkd_ki = G[i] / kmag          # ∂|k|/∂k_i = k_i/|k|
            K += eta_shell * 2.0 * (kmag - q0) * dkd_ki * np.eye(3, dtype=np.complex128)

    return K


# ============================================================
# Numerical Bloch matrix via hessian_vec probing
# ============================================================

def _fft3(arr: np.ndarray) -> np.ndarray:
    """3-D FFT over the last three axes of a (3, Nx, Ny, Nz) array."""
    return np.fft.fftn(arr, axes=(-3, -2, -1))


def _ifft3(arr: np.ndarray) -> np.ndarray:
    """3-D IFFT over the last three axes of a (3, Nx, Ny, Nz) array."""
    return np.fft.ifftn(arr, axes=(-3, -2, -1))


def _probe_field_for_idx(
    comp: int,
    idx: Tuple[int, int, int],
    shape: Tuple[int, int, int],
) -> np.ndarray:
    """
    Build a real-space field v with a single nonzero Fourier mode:

        v̂_b(k) = δ_{b, comp} · δ_{k, idx}

    The resulting real-space field has shape (3, Nx, Ny, Nz).
    """
    Nx, Ny, Nz = shape
    v_kspace = np.zeros((3, Nx, Ny, Nz), dtype=np.complex128)
    v_kspace[comp][idx[0], idx[1], idx[2]] = 1.0
    # Real-space probe: IFFT of k-space delta
    v = np.zeros((3, Nx, Ny, Nz), dtype=np.complex128)
    v[comp] = np.fft.ifftn(v_kspace[comp])
    return v


def bloch_matrix_at_idx(
    Psi0: np.ndarray,
    idx: Tuple[int, int, int],
    hessian_fn: Callable[[np.ndarray], np.ndarray],
    params: Dict[str, Any],
    *,
    verbose: bool = False,
) -> np.ndarray:
    """
    Extract the 3×3 Bloch matrix L(G*) at grid index *idx* by probing
    hessian_vec with plane-wave test fields.

    Algorithm
    ---------
    For each component b = 0, 1, 2:
        1. Build probe  v_b(x) = e_b · exp(i G* · x) / N³   (via IFFT of δ_{k,G*})
        2. Apply        w_b = hessian_fn(v_b)
        3. FFT(w_b)[a, idx] = L_{a b}(G*)

    Parameters
    ----------
    Psi0       : (3, Nx, Ny, Nz) ndarray   converged condensate (real-space)
    idx        : (ix, iy, iz)               grid index of G*
    hessian_fn : callable  v → hessian_vec(Psi0, v, params)
    params     : dict
    verbose    : print intermediate eigenvalues for debugging

    Returns
    -------
    L_bloch : (3,3) complex128 ndarray
    """
    if Psi0.ndim != 4 or Psi0.shape[0] != 3:
        raise ValueError("Psi0 must have shape (3, Nx, Ny, Nz)")
    _, Nx, Ny, Nz = Psi0.shape
    shape = (Nx, Ny, Nz)
    L = np.zeros((3, 3), dtype=np.complex128)

    for b in range(3):
        v_b = _probe_field_for_idx(b, idx, shape)
        w_b = np.asarray(hessian_fn(v_b), dtype=np.complex128)
        if w_b.shape != (3, Nx, Ny, Nz):
            raise ValueError(
                f"hessian_fn output shape {w_b.shape} does not match "
                f"expected (3, {Nx}, {Ny}, {Nz})"
            )
        w_b_k = _fft3(w_b)
        for a in range(3):
            L[a, b] = w_b_k[a, idx[0], idx[1], idx[2]]

    if verbose:
        evals = np.linalg.eigvalsh(0.5 * (L + L.conj().T))
        print(f"  L(G*) eigenvalues: {evals}")

    return L


# ============================================================
# Numerical k-derivative of L via Richardson extrapolation
# ============================================================

def _shifted_idx(
    idx: Tuple[int, int, int],
    direction: int,
    step: int,
    shape: Tuple[int, int, int],
) -> Tuple[int, int, int]:
    """Shift index by *step* in *direction* with periodic wrapping."""
    idx_list = list(idx)
    idx_list[direction] = (idx_list[direction] + step) % shape[direction]
    return tuple(idx_list)


def bloch_derivative_numerical(
    Psi0: np.ndarray,
    idx: Tuple[int, int, int],
    direction: int,
    hessian_fn: Callable[[np.ndarray], np.ndarray],
    params: Dict[str, Any],
    *,
    n_steps: int = 2,
    order: int = 4,
    verbose: bool = False,
) -> np.ndarray:
    """
    Numerically compute K_i^full(G*) = ∂L(k)/∂k_i |_{k=G*} using
    Richardson-extrapolated finite differences on the discrete k-grid.

    Each finite-difference point is obtained by probing bloch_matrix_at_idx
    at the shifted grid index (idx[direction] ± step).  The physical dk for
    step n is dk_n = n · Δk_i where Δk_i = 2π / (N_i · dx_i) = 2π/L_i.

    Parameters
    ----------
    Psi0      : (3, Nx, Ny, Nz) converged condensate
    idx       : (ix, iy, iz)    grid index of G*
    direction : int             0=x, 1=y, 2=z
    hessian_fn: callable
    params    : dict
    n_steps   : int             number of Richardson levels (default 2 → O4)
    order     : int             target order of extrapolation (2 or 4)
    verbose   : bool

    Returns
    -------
    K_i : (3,3) complex128 ndarray
    """
    _, Nx, Ny, Nz = Psi0.shape
    shape = (Nx, Ny, Nz)
    N_dir = shape[direction]

    # Physical dk per grid step in the given direction
    Ldirs = [float(params["Lx"]), float(params["Ly"]), float(params["Lz"])]
    Ndirs = [Nx, Ny, Nz]
    dk_grid = 2.0 * math.pi / Ldirs[direction]   # spacing of 1 grid step

    # Gather L at multiple offsets for Richardson extrapolation
    L_plus  = {}
    L_minus = {}
    for step in range(1, n_steps + 1):
        idx_p = _shifted_idx(idx, direction, +step, shape)
        idx_m = _shifted_idx(idx, direction, -step, shape)
        L_plus[step]  = bloch_matrix_at_idx(Psi0, idx_p, hessian_fn, params)
        L_minus[step] = bloch_matrix_at_idx(Psi0, idx_m, hessian_fn, params)

    if n_steps == 1 or order == 2:
        # Second-order central difference: (L(+1) - L(-1)) / (2 dk)
        K = (L_plus[1] - L_minus[1]) / (2.0 * dk_grid)
    elif n_steps >= 2 and order >= 4:
        # Fourth-order Richardson: (−L(+2)+8L(+1)−8L(−1)+L(−2)) / (12 dk)
        K = (
            -L_plus[2] + 8.0 * L_plus[1]
            - 8.0 * L_minus[1] + L_minus[2]
        ) / (12.0 * dk_grid)
    else:
        raise ValueError(f"Unsupported combination n_steps={n_steps}, order={order}")

    if verbose:
        print(f"  K_{direction} max |element|: {np.abs(K).max():.4e}")

    return K


# ============================================================
# High-level: compute Bloch matrices for all patches
# ============================================================

def bloch_matrices_all_patches(
    Psi0: np.ndarray,
    patch_centers: np.ndarray,
    q0: float,
    hessian_fn: Callable[[np.ndarray], np.ndarray],
    params: Dict[str, Any],
    *,
    dk_steps: int = 2,
    fd_order: int = 4,
    compute_K: bool = True,
    verbose: bool = False,
) -> List[Dict]:
    """
    Compute Bloch matrices L(G*_α) and optional derivatives K_i(G*_α) for
    all patches defined by *patch_centers*.

    Parameters
    ----------
    Psi0          : (3, Nx, Ny, Nz) converged condensate
    patch_centers : (Npatch, 3) unit vectors ĝ_α  (from extractor output)
    q0            : float   shell radius [rad/length]
    hessian_fn    : callable  v → hessian_vec(Psi0, v, params)
    params        : dict
    dk_steps      : int     Richardson steps for K_i computation
    fd_order      : int     2 or 4
    compute_K     : bool    if False, skip K_i computation (faster)
    verbose       : bool

    Returns
    -------
    results : list of dicts, one per patch, each containing:
        "patch_idx"  : int
        "G_star"     : (3,) ndarray   continuous G* = q0 * ĝ_α
        "grid_idx"   : (ix, iy, iz)
        "G_grid"     : (3,) ndarray   actual k-vector at grid_idx
        "snap_error" : float          |G_grid - G_star| / q0 (relative)
        "L"          : (3,3) complex128   full Bloch matrix
        "L_lin"      : (3,3) complex128   analytical linear part
        "L_nl"       : (3,3) complex128   nonlinear correction (L - L_lin)
        "K"          : (3, 3, 3) complex128  K[i] = ∂L/∂k_i (if compute_K)
        "K_lin"      : (3, 3, 3) complex128  analytical linear K[i] (if compute_K)
    """
    if Psi0.ndim != 4 or Psi0.shape[0] != 3:
        raise ValueError("Psi0 must have shape (3, Nx, Ny, Nz)")
    _, Nx, Ny, Nz = Psi0.shape

    kx, ky, kz = kgrid_3d(params, Nx, Ny, Nz)

    results = []
    Npatch = patch_centers.shape[0]

    for alpha, gc in enumerate(patch_centers):
        gc = np.asarray(gc, dtype=float)
        # Normalise to unit vector then scale by q0
        nrm = np.linalg.norm(gc)
        if nrm < 1e-14:
            warnings.warn(f"Patch {alpha}: zero patch_center vector; skipping.")
            continue
        G_star = q0 * gc / nrm

        # Snap to nearest grid point
        ix, iy, iz = k_to_grid_idx(G_star, kx, ky, kz)
        G_grid = np.array([kx[ix], ky[iy], kz[iz]])
        snap_err = float(np.linalg.norm(G_grid - G_star)) / max(q0, 1e-14)

        if snap_err > 0.15:
            warnings.warn(
                f"Patch {alpha}: G* snap error = {snap_err:.3f} (>15%%). "
                f"Grid resolution may be insufficient.  |G*|={np.linalg.norm(G_star):.4f}, "
                f"|G_grid|={np.linalg.norm(G_grid):.4f}"
            )

        if verbose:
            print(f"Patch {alpha}: G*={G_star}  →  grid ({ix},{iy},{iz})  "
                  f"G_grid={G_grid}  snap_err={snap_err:.3e}")

        # Full numerical Bloch matrix
        L_full = bloch_matrix_at_idx(Psi0, (ix, iy, iz), hessian_fn, params, verbose=verbose)
        # Analytical linear part
        L_lin  = bloch_matrix_linear(G_grid, params)
        L_nl   = L_full - L_lin

        entry: Dict = {
            "patch_idx"  : alpha,
            "G_star"     : G_star,
            "grid_idx"   : (ix, iy, iz),
            "G_grid"     : G_grid,
            "snap_error" : snap_err,
            "L"          : L_full,
            "L_lin"      : L_lin,
            "L_nl"       : L_nl,
        }

        if compute_K:
            K_num = np.zeros((3, 3, 3), dtype=np.complex128)
            K_lin_arr = np.zeros((3, 3, 3), dtype=np.complex128)
            for i in range(3):
                K_num[i] = bloch_derivative_numerical(
                    Psi0, (ix, iy, iz), i, hessian_fn, params,
                    n_steps=dk_steps, order=fd_order, verbose=verbose,
                )
                K_lin_arr[i] = bloch_derivative_linear(G_grid, i, params)
            entry["K"]     = K_num
            entry["K_lin"] = K_lin_arr

        results.append(entry)

    return results


# ============================================================
# Utility: quick sanity check
# ============================================================

def check_hermiticity(L: np.ndarray, tol: float = 1e-8) -> Tuple[bool, float]:
    """
    Check whether L is Hermitian: ||L − L†|| / ||L|| < tol.

    The full Hessian of a real-valued action should be Hermitian.  A
    non-Hermitian Bloch matrix signals either a non-converged Ψ₀ or a
    numerical probe error.

    Returns
    -------
    (is_hermitian, relative_deviation)
    """
    diff  = L - L.conj().T
    nrm_L = max(np.linalg.norm(L), 1e-14)
    rdev  = float(np.linalg.norm(diff)) / nrm_L
    return rdev < tol, rdev


def symmetrise(L: np.ndarray) -> np.ndarray:
    """Return (L + L†) / 2 for downstream eigenvalue computation."""
    return 0.5 * (L + L.conj().T)
