#!/usr/bin/env python3
# =====================================================================
# Math374_canonical_BCC_hessian.py
#
# Canonical TECT Brazovskii BCC-Hessian computation - replaces the
# audit-flagged toy form of Math369/Math370/Math371. Implements the
# free energy actually used by the production backend
# Codes/pde/real_backend_pt_bcc_mixed_v3.py:shell_free_energy
#
#   F[Psi] = integral over V of [
#                (r/2)  Psi^2
#              + (Z/2)  |grad Psi|^2
#              + (Y/2)  |laplacian Psi|^2
#              + (lam/2) Psi^4
#              + (gam/3) Psi^6
#           ]
#
# Locked canonical parameters (config_template_brazovskii.json):
#   q0   = 0.6801747616
#   Y    = 1.0
#   Z    = -2 * Y * q0**2 = -0.9252754126
#   r    = mu2 + Y * q0**4
#   lam  = -0.43   (negative quartic - first-order transition driver)
#   gam  = +1.62   (positive sextic - condensate stabiliser)
#
# Default mu2 = +0.005 (Math82-AddH analytical operating point).
# Override via --mu2.
#
# Pre-registered success criterion (CLAUDE.md 6.3.3):
#   lambda_min(Hess) >= -1e-6 * |lambda_top|
#   AND >= 3 eigenvalues within |lambda| < 1e-3 * |lambda_top|.
# Pre-registered falsification criterion:
#   any lambda < -1e-3 * |lambda_top| with non-Goldstone Ritz overlap > 0.5.
#
# Math note linkage: Math373 (RETRACTION + canonical free-energy
# restoration). Canonical source: real_backend_pt_bcc_mixed_v3.py
# (shell_free_energy, lines 532-602).
#
# Usage:
#   python -u Codes/supplementary/Math374_canonical_BCC_hessian.py \
#       --N 16 --mu2 0.005 --eigs 30 --relax-iters 200
#
# Dependencies: numpy. scipy.sparse.linalg required for N > 12;
# falls back to dense numpy.linalg.eigvalsh for smaller grids.
# =====================================================================
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# --- Canonical locked parameters (config_template_brazovskii.json) ---
Q0_PHYSICAL: float = 0.6801747616
Y_LOCKED: float = 1.0
LAM_LOCKED: float = -0.43
GAM_LOCKED: float = +1.62
K4_BCC: float = 1.0
K6_BCC: float = 2.5


def setup_grid(N: int, q0: float = Q0_PHYSICAL):
    a_BCC = 2.0 * np.pi / q0
    L = 2.0 * a_BCC
    dx = L / N
    x = np.arange(N) * dx - 0.5 * L
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    k1d = 2.0 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY, KZ = np.meshgrid(k1d, k1d, k1d, indexing="ij")
    K2 = KX**2 + KY**2 + KZ**2
    return {
        "N": N, "L": L, "dx": dx, "dV": dx**3,
        "X": X, "Y": Y, "Z": Z,
        "KX": KX, "KY": KY, "KZ": KZ, "K2": K2,
    }


def bcc_primitive_q(q0: float = Q0_PHYSICAL) -> np.ndarray:
    inv_sqrt2 = 1.0 / np.sqrt(2.0)
    qhat = np.array([
        [+1, +1,  0],
        [+1, -1,  0],
        [+1,  0, +1],
        [+1,  0, -1],
        [ 0, +1, +1],
        [ 0, +1, -1],
    ], dtype=np.float64) * inv_sqrt2
    return q0 * qhat


def bcc_initial_state(grid, A_per_cosine, q0=Q0_PHYSICAL):
    qvecs = bcc_primitive_q(q0)
    Psi = np.zeros_like(grid["X"])
    for q in qvecs:
        phase = q[0] * grid["X"] + q[1] * grid["Y"] + q[2] * grid["Z"]
        Psi += A_per_cosine * np.cos(phase)
    return Psi


def deep_bcc_amplitude(mu2, lam=LAM_LOCKED, gam=GAM_LOCKED):
    """BCC per-cosine amplitude A_0 from full 1-mode reduction quadratic.

    Solves a*x^2 + b*x + c = 0 with a=gam*K6, b=lam*K4, c=mu2/2,
    x=phi_0^2=3*A_0^2; takes the larger positive root (local-min branch).
    Falls back to cold-limit phi_0^2 = -4*lam/(15*gam) if no real root.
    """
    a = gam * K6_BCC
    b = lam * K4_BCC
    c = 0.5 * mu2
    disc = b**2 - 4.0 * a * c
    if disc <= 0:
        phi0_sq = max(-4.0 * lam / (15.0 * gam), 0.0)
        return math.sqrt(phi0_sq / 3.0)
    x_pos = (-b + math.sqrt(disc)) / (2.0 * a)
    if x_pos <= 0:
        phi0_sq = max(-4.0 * lam / (15.0 * gam), 0.0)
        return math.sqrt(phi0_sq / 3.0)
    return math.sqrt(x_pos / 3.0)


def free_energy_canonical(Psi, grid, params):
    """Canonical TECT Brazovskii F (faithful to shell_free_energy)."""
    r = params["r"]; Z = params["Z"]; Y = params["Y"]
    lam = params["lam"]; gam = params["gam"]
    K2 = grid["K2"]

    Psi_k = np.fft.fftn(Psi)
    grad_sq = (K2 * np.abs(Psi_k)**2).sum() / Psi.size
    lap_sq = ((K2**2) * np.abs(Psi_k)**2).sum() / Psi.size

    F_quad = 0.5 * r * np.sum(Psi**2)
    F_grad = 0.5 * Z * grad_sq
    F_bi = 0.5 * Y * lap_sq
    F_q4 = 0.5 * lam * np.sum(Psi**4)
    F_q6 = (gam / 3.0) * np.sum(Psi**6)

    return float(grid["dV"] * (F_quad + F_grad + F_bi + F_q4 + F_q6))


def free_energy_gradient(Psi, grid, params):
    """delta F / delta Psi(x): r*Psi - Z*lap(Psi) + Y*lap^2(Psi)
                              + 2*lam*Psi^3 + 2*gam*Psi^5"""
    r = params["r"]; Z = params["Z"]; Y = params["Y"]
    lam = params["lam"]; gam = params["gam"]
    K2 = grid["K2"]

    Psi_k = np.fft.fftn(Psi)
    lap_Psi = np.real(np.fft.ifftn(-K2 * Psi_k))
    lap2_Psi = np.real(np.fft.ifftn((K2**2) * Psi_k))

    return r * Psi - Z * lap_Psi + Y * lap2_Psi + 2.0*lam*Psi**3 + 2.0*gam*Psi**5


def relax_to_minimum(Psi0, grid, params, n_iters=200, alpha=0.0, verbose=True):
    Psi = Psi0.copy()
    F_prev = free_energy_canonical(Psi, grid, params)
    if alpha <= 0.0:
        g0 = free_energy_gradient(Psi, grid, params)
        alpha = 0.01 / (np.max(np.abs(g0)) + 1e-12)

    for it in range(n_iters):
        g = free_energy_gradient(Psi, grid, params)
        gnorm = np.sqrt(np.sum(g**2) / Psi.size)
        alpha_try = alpha * 2.0
        for _ in range(20):
            Psi_new = Psi - alpha_try * g
            F_new = free_energy_canonical(Psi_new, grid, params)
            if F_new < F_prev:
                break
            alpha_try *= 0.5
        else:
            if verbose:
                print(f"    iter {it:4d}: line-search failed; halting")
            break
        Psi = Psi_new
        if verbose and (it % max(1, n_iters // 10) == 0 or it == n_iters - 1):
            print(f"    iter {it:4d}: F = {F_new:+.6e}, |grad|/sqrt(N3) = {gnorm:.4e}, alpha = {alpha_try:.2e}")
        F_prev = F_new
        alpha = alpha_try
        if gnorm < 1e-10:
            if verbose:
                print(f"    iter {it:4d}: converged (|grad| < 1e-10)")
            break
    return Psi


def hessian_apply(delta, Psi, grid, params):
    """H delta = r*delta - Z*lap(delta) + Y*lap^2(delta)
              + 6*lam*Psi^2 * delta + 10*gam*Psi^4 * delta"""
    r = params["r"]; Z = params["Z"]; Y = params["Y"]
    lam = params["lam"]; gam = params["gam"]
    K2 = grid["K2"]

    delta_k = np.fft.fftn(delta)
    lap_delta = np.real(np.fft.ifftn(-K2 * delta_k))
    lap2_delta = np.real(np.fft.ifftn((K2**2) * delta_k))

    return (r * delta - Z * lap_delta + Y * lap2_delta
            + 6.0 * lam * (Psi**2) * delta
            + 10.0 * gam * (Psi**4) * delta)


def lowest_eigenvalues(Psi, grid, params, n_eigs):
    N = grid["N"]; size = N**3
    try:
        from scipy.sparse.linalg import LinearOperator, eigsh
    except ImportError:
        if size <= 12**3:
            print("  scipy unavailable; falling back to dense eigvalsh")
            H = np.zeros((size, size))
            for i in range(size):
                e = np.zeros(size); e[i] = 1.0
                H[:, i] = hessian_apply(e.reshape(N, N, N), Psi, grid, params).ravel()
            return np.linalg.eigvalsh(0.5 * (H + H.T))[:n_eigs]
        raise RuntimeError(
            "scipy.sparse.linalg required for N > 12; install via "
            "'pip install scipy --user'"
        )

    def matvec(v):
        return hessian_apply(v.reshape(N, N, N), Psi, grid, params).ravel()

    op = LinearOperator((size, size), matvec=matvec, dtype=np.float64)
    try:
        eigs = eigsh(op, k=n_eigs, which="SA", return_eigenvectors=False,
                     maxiter=5000, tol=1e-8)
        return np.sort(eigs)
    except Exception as e1:
        print(f"  SA mode failed ({e1}); trying shift-invert sigma=-0.1")
        try:
            eigs = eigsh(op, k=n_eigs, sigma=-0.1, which="LM",
                         return_eigenvectors=False, maxiter=5000, tol=1e-6)
            return np.sort(eigs)
        except Exception as e2:
            raise RuntimeError(f"both Lanczos modes failed: SA={e1}; SI={e2}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=16,
                        help="grid size N (cubic N^3); default 16")
    parser.add_argument("--mu2", type=float, default=0.005,
                        help="Brazovskii mu^2 (default 0.005, Math82-AddH point)")
    parser.add_argument("--lam", type=float, default=LAM_LOCKED)
    parser.add_argument("--gam", type=float, default=GAM_LOCKED)
    parser.add_argument("--Y", type=float, default=Y_LOCKED)
    parser.add_argument("--q0", type=float, default=Q0_PHYSICAL)
    parser.add_argument("--A0", type=float, default=None,
                        help="per-cosine BCC amplitude (default: 1-mode quadratic)")
    parser.add_argument("--eigs", type=int, default=30)
    parser.add_argument("--relax-iters", type=int, default=200)
    parser.add_argument("--out-dir", default="Runs/math374")
    parser.add_argument("--out-tag", default=None)
    args = parser.parse_args()

    r_eff = args.mu2 + args.Y * args.q0**4
    Z_eff = -2.0 * args.Y * args.q0**2
    params = {
        "r": r_eff, "Z": Z_eff, "Y": args.Y,
        "lam": args.lam, "gam": args.gam, "q0": args.q0,
        "mu2": args.mu2,
    }

    print("=" * 76)
    print(" Math374 canonical Brazovskii BCC Hessian - sextic-included form")
    print("=" * 76)
    print(f" Grid:           {args.N}x{args.N}x{args.N} = {args.N**3} points")
    print(f" Canonical params:")
    print(f"   mu2  = {args.mu2:+.6f}")
    print(f"   lam  = {args.lam:+.6f}    (quartic, negative = first-order)")
    print(f"   gam  = {args.gam:+.6f}    (sextic, positive = stabiliser)")
    print(f"   Y    = {args.Y:+.6f}")
    print(f"   Z    = {Z_eff:+.6f}    (= -2 Y q0^2)")
    print(f"   r    = {r_eff:+.6f}    (= mu2 + Y q0^4)")
    print(f"   q0   = {args.q0:+.6f}")

    grid = setup_grid(args.N, args.q0)
    print(f" Box L = {grid['L']:.4f}, dx = {grid['dx']:.4f}")

    A0 = args.A0 if args.A0 is not None else deep_bcc_amplitude(args.mu2, args.lam, args.gam)
    phi0_predicted = math.sqrt(3.0) * A0
    cold_limit_phi0 = math.sqrt(max(-4.0 * args.lam / (15.0 * args.gam), 0.0))
    print(f" Per-cosine BCC amplitude A0 = {A0:.6f}")
    print(f" => predicted phi_0 = sqrt(3)*A0 = {phi0_predicted:.6f}")
    print(f"    (cold-limit value = {cold_limit_phi0:.6f}; Math82-AddH cites ~0.266 at mu2=+0.005)")

    print(f"\n[1/4] Initialising 6-cosine BCC ansatz ...")
    Psi = bcc_initial_state(grid, A0, args.q0)
    F0 = free_energy_canonical(Psi, grid, params)
    g0 = free_energy_gradient(Psi, grid, params)
    print(f"      Initial F = {F0:+.6e}, "
          f"<Psi^2> = {np.mean(Psi**2):.6e}, "
          f"|grad|/sqrt(V) = {np.sqrt(np.sum(g0**2)/Psi.size):.4e}")

    if args.relax_iters > 0:
        print(f"\n[2/4] Relaxing via adaptive steepest descent ({args.relax_iters} iters) ...")
        Psi = relax_to_minimum(Psi, grid, params, n_iters=args.relax_iters)
        F1 = free_energy_canonical(Psi, grid, params)
        g1 = free_energy_gradient(Psi, grid, params)
        print(f"      Relaxed: F: {F0:+.4e} -> {F1:+.4e}  (DeltaF = {F1 - F0:+.4e})")
    else:
        print("\n[2/4] (skipped relaxation; --relax-iters=0)")
        F1 = F0
        g1 = g0

    print(f"\n[3/4] Stationarity check at final state:")
    gnorm = np.sqrt(np.sum(g1**2) / Psi.size)
    print(f"      |grad F|/sqrt(V) = {gnorm:.4e}  (ideally << 1)")
    print(f"      <Psi^2>  = {np.mean(Psi**2):.6e}  (target phi_0^2 ~ {phi0_predicted**2:.4f})")
    print(f"      <Psi^4>  = {np.mean(Psi**4):.6e}")
    print(f"      <Psi^6>  = {np.mean(Psi**6):.6e}")

    print(f"\n[4/4] Computing {args.eigs} lowest Hessian eigenvalues (Lanczos) ...")
    try:
        eigs = lowest_eigenvalues(Psi, grid, params, args.eigs)
    except Exception as exc:
        print(f"\n  ERROR: eigenvalue extraction failed: {exc}")
        return 2

    lam_top = float(np.max(np.abs(eigs)))
    tol_zero = 1e-3 * lam_top
    tol_neg = 1e-6 * lam_top

    print(f"\n  Lowest {args.eigs} eigenvalues:")
    for i, e in enumerate(eigs):
        if e < -tol_zero:
            tag = "  <- NEGATIVE (instability!)"
        elif abs(e) < tol_zero:
            tag = "  <- Goldstone-zero candidate"
        else:
            tag = ""
        print(f"    lam_{i+1:2d} = {e:+.6e}{tag}")

    n_neg = int(np.sum(eigs < -tol_neg))
    n_zero = int(np.sum(np.abs(eigs) < tol_zero))
    n_pos = int(np.sum(eigs > tol_zero))
    print(f"\n  Classification (with tol_zero = 1e-3 * |lam_top|):")
    print(f"    negative-and-significant : {n_neg}")
    print(f"    near-zero (Goldstone)    : {n_zero}")
    print(f"    positive                 : {n_pos}")

    success = (n_neg == 0) and (n_zero >= 3)
    falsified = any(e < -tol_zero for e in eigs)

    print(f"\n=== PRE-REGISTERED VERDICT (CLAUDE.md 6.3.3) ===")
    if success:
        print(f"  PASS: BCC IS local minimum of canonical Brazovskii F.")
        print(f"        (>= 3 Goldstone modes + no negative significant eigenvalues)")
        verdict = "PASS"
    elif falsified:
        print(f"  FAIL: {n_neg} eigenvalue(s) below -1e-3*|lam_top|.")
        print(f"        BCC is NOT a local minimum at this operating point.")
        verdict = "FAIL"
    else:
        print(f"  INDETERMINATE: no significant negative eigenvalues but only "
              f"{n_zero} Goldstone candidates (need >= 3).")
        verdict = "INDETERMINATE"

    out_tag = args.out_tag or f"N{args.N}_mu2_{args.mu2:+.4f}"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "kind": "Math374-canonical-BCC-Hessian",
        "generated": datetime.now(timezone.utc).isoformat(),
        "params": {**params, "N": args.N, "L": grid["L"]},
        "A0_init": A0,
        "F_initial": F0,
        "F_relaxed": F1,
        "grad_norm_relaxed": gnorm,
        "eigenvalues": [float(e) for e in eigs],
        "n_neg_significant": n_neg,
        "n_zero_goldstone": n_zero,
        "n_pos": n_pos,
        "tol_zero": tol_zero,
        "lam_top": lam_top,
        "verdict": verdict,
    }
    out_path = out_dir / f"math374_{out_tag}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Result saved: {out_path}")

    return 0 if verdict == "PASS" else (1 if verdict == "FAIL" else 3)


if __name__ == "__main__":
    sys.exit(main())
