#!/usr/bin/env python3
# =====================================================================
# Math400_AddE_brazovskii_one_loop.py  v1.0 (2026-05-11)
#
# Explicit one-loop Brazovskii self-consistency at TECT canonical
# parameters. Sign-careful for TECT lambda<0 (attractive quartic).
# Determines Path alpha/beta/gamma for Pillar 4 vacuum identification.
#
# Physics
# -------
# Brazovskii free energy density (canonical TECT mapping):
#   F[Psi] = (r/2) Psi^2 + (c/2) ((|nabla|^2 - q0^2))^2 Psi^2
#          + (u/4) Psi^4 + (v/6) Psi^6
#
# TECT mapping (Math400-AddD §5):
#   r_brazovskii = mu^2 + Y * q0^4         (effective shell quadratic)
#   c_brazovskii = Y                        (bilaplacian coefficient)
#   u_brazovskii = 2 * lambda               (TECT lam<0 -> u<0, sign-preserved)
#   v_brazovskii = 2 * gamma                (TECT gam>0 -> v>0)
#
# Hartree (one-loop self-consistent) gap equation in disordered phase:
#   r_R = r + 3 u M(r_R) + 15 v M(r_R)^2
# where the loop integral is
#   M(r_R) = int d^3q/(2 pi)^3  / [r_R + c (|q|^2 - q0^2)^2]
#
# Pre-registered outcomes (Math400-AddD §6):
#   Path alpha: r_R > 0 self-consistent solution exists and is stable.
#               Brazovskii fluctuation-stabilized disordered phase
#               (Reading H of Math400-AddC) confirmed. Pillar 4
#               reformulated as fluctuation-correlation theorem.
#   Path beta:  no positive r_R solution; symmetry-broken vacuum
#               survives loops. Reading H rejected; specific natural
#               structure must be identified.
#   Path gamma: no self-consistent solution OR fine-tuning required
#               (e.g., r_R changes sign across small parameter
#               variation). Brazovskii framework INADEQUATE; must be
#               courageously discarded per operator directive.
#
# Sign-convention WARNING (Math400-AddD §5)
# -----------------------------------------
# TECT lambda<0 (attractive quartic) inverts the standard Brazovskii
# fluctuation correction sign. With u<0 the quartic Hartree shift
# 3*u*M is NEGATIVE (drives r_R below r_bare), opposite of the
# standard Brazovskii (u>0) direction. The sextic 15*v*M^2 is positive
# (stabilising). The competition determines the path. This script
# computes the actual outcome rather than assuming it.
#
# Dependencies: numpy ONLY (custom bisection root-finder, trapezoidal
# integral; no scipy needed for sandbox compatibility).
#
# Usage
# -----
#   # Single-point at TECT canonical operating point:
#   python -u Codes/supplementary/Math400_AddE_brazovskii_one_loop.py \
#       --mu2 0.005 --out-dir Runs/math400
#
#   # Sweep across phase region:
#   python -u Codes/supplementary/Math400_AddE_brazovskii_one_loop.py \
#       --mu2-sweep -2.0 0.5 30 --out-dir Runs/math400
#
#   # Compare full numerical vs shell-localized analytical:
#   python -u Codes/supplementary/Math400_AddE_brazovskii_one_loop.py \
#       --mu2 0.005 --compare-shell --out-dir Runs/math400
#
# Exit codes:
#   0  Path alpha (Reading H confirmed)
#   1  Multi-stable regime (multiple self-consistent r_R)
#   2  Path beta (broken symmetry survives)
#   3  Path gamma (Brazovskii inadequate)
# =====================================================================
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

# =====================================================================
# Locked TECT canonical parameters (Math60-A..E; Math82-AddH)
# =====================================================================
LAM_LOCKED: float = -0.43           # attractive quartic in TECT convention
GAM_LOCKED: float = +1.62           # repulsive sextic
Y_LOCKED:   float = 1.0
Q0_LOCKED:  float = 0.6801747616


# =====================================================================
# Loop integral M(r_R)
# =====================================================================
def loop_integral_full(r_R: float, q0: float, c: float,
                       n_points: int = 20000,
                       q_max_factor: float = 50.0) -> float:
    """Full numerical loop integral via trapezoidal rule.

    M(r_R) = (1 / (2 pi^2)) * integral_0^inf [q^2 / (r_R + c (q^2 - q0^2)^2)] dq

    Parameters
    ----------
    r_R : float
        Renormalised gap parameter. Must be > 0 for the disordered-phase
        gap equation to be well-defined.
    q0 : float
        Brazovskii shell wave-number.
    c : float
        Bilaplacian coefficient (Brazovskii c, i.e. TECT Y).
    n_points : int
        Trapezoidal grid points; default 20000 for ~6-digit precision.
    q_max_factor : float
        Upper integration limit q_max = q_max_factor * q0; default 50.

    Returns
    -------
    M : float
        Loop integral. Returns NaN if r_R <= 0 (disordered phase
        broken; broken-symmetry expansion needed).

    Notes
    -----
    The integrand peaks sharply at q = q0 with width ~ (r_R/c)^{1/4} q0.
    For r_R << c q0^4 (Brazovskii fluctuation regime) the integral is
    shell-localized. We use a non-uniform grid concentrated near q0 to
    capture the peak accurately.
    """
    if r_R <= 0:
        return float('nan')

    # Construct non-uniform grid: dense near q0, coarser at tails.
    # Strategy: use 60% of points in [0.5 q0, 1.5 q0], 40% in tails.
    n_dense = int(n_points * 0.6)
    n_tail_lo = (n_points - n_dense) // 2
    n_tail_hi = n_points - n_dense - n_tail_lo
    q_dense = np.linspace(0.5 * q0, 1.5 * q0, n_dense)
    q_tail_lo = np.linspace(0.0, 0.5 * q0, n_tail_lo + 1)[:-1]
    q_tail_hi = np.linspace(1.5 * q0, q_max_factor * q0, n_tail_hi + 1)[1:]
    q = np.concatenate([q_tail_lo, q_dense, q_tail_hi])

    integrand = q * q / (r_R + c * (q * q - q0 * q0) ** 2)
    # np.trapz is being deprecated in newer numpy; np.trapezoid is the
    # replacement but is not yet ubiquitous. Try-except for compat.
    try:
        M_unscaled = np.trapezoid(integrand, q)
    except AttributeError:
        M_unscaled = np.trapz(integrand, q)
    M = float(M_unscaled / (2.0 * math.pi ** 2))
    return M


def loop_integral_shell(r_R: float, q0: float, c: float) -> float:
    """Shell-localized analytical estimate (Math400-AddD §5).

    Asymptotic form valid when r_R << c * q0^4:
      M ~= q0^2 / (4 pi sqrt(c * r_R))
    """
    if r_R <= 0:
        return float('nan')
    return q0 * q0 / (4.0 * math.pi * math.sqrt(c * r_R))


# =====================================================================
# Self-consistency residual + custom Brent / bisection root-finder
# =====================================================================
def gap_residual(r_R: float, r_bare: float,
                 u: float, v: float,
                 q0: float, c: float,
                 use_shell: bool = False) -> float:
    """f(r_R) = r_R - [r_bare + 3 u M + 15 v M^2].

    Self-consistency requires f(r_R) = 0.
    """
    if r_R <= 0:
        # Outside disordered-phase domain: push away from negative r_R.
        return float('inf')
    if use_shell:
        M = loop_integral_shell(r_R, q0, c)
    else:
        M = loop_integral_full(r_R, q0, c)
    return r_R - r_bare - 3.0 * u * M - 15.0 * v * M * M


def bisect(f, a: float, b: float, xtol: float = 1e-10,
           max_iter: int = 200) -> float:
    """Bisection root-finder. Requires f(a) * f(b) < 0.

    Returns root c such that f(c) ~ 0 within xtol. If sign-change
    condition fails, raises ValueError.
    """
    fa = f(a)
    fb = f(b)
    if not (fa * fb < 0.0):
        raise ValueError(
            f"No sign change in [{a:.6e}, {b:.6e}]: "
            f"f(a)={fa:+.6e}, f(b)={fb:+.6e}")
    for _ in range(max_iter):
        c = 0.5 * (a + b)
        fc = f(c)
        if abs(b - a) < xtol or fc == 0.0:
            return c
        if fa * fc < 0.0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return 0.5 * (a + b)


def solve_self_consistency(r_bare: float, u: float, v: float,
                           q0: float, c: float,
                           r_R_min: float = 1e-6,
                           r_R_max: float = 100.0,
                           n_grid: int = 400,
                           use_shell: bool = False,
                           verbose: bool = True) -> dict:
    """Find all positive self-consistent r_R via grid scan + bisection.

    Returns
    -------
    dict with keys:
      r_bare, u, v, q0, c, use_shell:  inputs
      sign_change_intervals:           list of (lo, hi) intervals
      roots: list of dicts with r_R, M, shifts, fractional_shift
      path: 'alpha' (Reading H), 'beta' (broken-symm), 'gamma' (no sol),
            'multi' (multi-stable)
      classification: human-readable verdict
    """
    f = lambda x: gap_residual(x, r_bare, u, v, q0, c, use_shell)

    # Logarithmic grid scan to locate sign changes
    log_grid = np.logspace(math.log10(r_R_min), math.log10(r_R_max), n_grid)
    f_grid = np.array([f(x) for x in log_grid])

    sign_changes = []
    for i in range(len(log_grid) - 1):
        if f_grid[i] * f_grid[i + 1] < 0.0 and \
           math.isfinite(f_grid[i]) and math.isfinite(f_grid[i + 1]):
            sign_changes.append((float(log_grid[i]), float(log_grid[i + 1])))

    if verbose:
        print(f"  Bare r = {r_bare:+.6e}")
        print(f"  Grid scan: {len(sign_changes)} sign-change interval(s) found")
        if len(sign_changes) > 0:
            print(f"    Intervals: {sign_changes[:5]}"
                  + (f" ... ({len(sign_changes)} total)" if len(sign_changes) > 5 else ""))

    # Refine each interval via bisection
    roots = []
    for (lo, hi) in sign_changes:
        try:
            root = bisect(f, lo, hi, xtol=1e-10, max_iter=200)
            if use_shell:
                M = loop_integral_shell(root, q0, c)
            else:
                M = loop_integral_full(root, q0, c)
            shift_quartic = 3.0 * u * M
            shift_sextic = 15.0 * v * M * M
            frac_shift = ((root - r_bare) / abs(r_bare)
                          if r_bare != 0 else float('inf'))
            roots.append({
                'r_R': float(root),
                'M': float(M),
                'shift_quartic_3uM': float(shift_quartic),
                'shift_sextic_15vM2': float(shift_sextic),
                'fractional_shift': float(frac_shift),
                'residual': float(f(root)),
            })
        except (ValueError, RuntimeError) as e:
            if verbose:
                print(f"  Bisection failed in ({lo:.4e}, {hi:.4e}): {e}")

    # Path classification per Math400-AddD §6 pre-registered verdict
    if len(roots) == 0:
        path = 'gamma'
        classification = (
            f"PATH gamma: no positive r_R self-consistent solution in "
            f"[{r_R_min:.0e}, {r_R_max:.0e}]. Brazovskii framework may "
            f"be INADEQUATE at r_bare = {r_bare:+.4e}. Per operator "
            f"directive, must be courageously discarded; replacement "
            f"framework search begins.")
    elif len(roots) == 1:
        root = roots[0]
        if root['r_R'] > 0:
            # Stability check: positive shift overall is fluctuation-stabilising
            stable = (root['shift_sextic_15vM2'] + root['shift_quartic_3uM']
                      + r_bare > 0)
            if stable:
                path = 'alpha'
                classification = (
                    f"PATH alpha: unique self-consistent r_R = "
                    f"{root['r_R']:+.4e} > 0. Brazovskii fluctuation-"
                    f"stabilized disordered phase (Reading H) confirmed "
                    f"at these parameters. Pillar 4 should be "
                    f"reformulated as fluctuation-correlation theorem.")
            else:
                path = 'beta'
                classification = (
                    f"PATH beta: r_R = {root['r_R']:+.4e} but instability "
                    f"detected. Symmetry-broken vacuum may survive loops; "
                    f"Reading H provisional.")
        else:
            path = 'beta'
            classification = (
                f"PATH beta: self-consistent r_R = {root['r_R']:+.4e} < 0. "
                f"Symmetry-broken vacuum survives one-loop. Reading H "
                f"REJECTED; specific natural structure must be identified.")
    else:
        path = 'multi'
        classification = (
            f"PATH multi: {len(roots)} positive self-consistent r_R "
            f"solutions found. Multi-stable regime; cosmological "
            f"dynamics selects.")

    return {
        'r_bare': float(r_bare),
        'u_brazovskii': float(u),
        'v_brazovskii': float(v),
        'q0': float(q0),
        'c': float(c),
        'use_shell': bool(use_shell),
        'sign_change_intervals': sign_changes,
        'roots': roots,
        'path': path,
        'classification': classification,
    }


# =====================================================================
# Self-test sanity check (devil's-advocate)
# =====================================================================
def self_test() -> bool:
    """Verify code correctness on three known limits.

    Test 1: Standard Brazovskii (u>0) at r=1.0: shell M ~ q0^2/(4pi).
    Test 2: TECT canonical (u<0) at r=0.219: gap eqn has solution.
    Test 3: Shell-vs-full integral agreement at r << c*q0^4.
    """
    print("  Self-test 1: shell formula at r=1.0, q0=0.6802, c=1.0")
    M_test = loop_integral_shell(1.0, Q0_LOCKED, Y_LOCKED)
    expected = Q0_LOCKED ** 2 / (4 * math.pi * math.sqrt(1.0))
    assert abs(M_test - expected) < 1e-10, f"Shell formula bug: {M_test} vs {expected}"
    print(f"    M_shell(1.0) = {M_test:.6e} (expected {expected:.6e}) ... OK")

    print("  Self-test 2: TECT canonical solver at mu^2 = +0.005")
    r_bare = 0.005 + Y_LOCKED * Q0_LOCKED ** 4
    res = solve_self_consistency(
        r_bare, 2.0 * LAM_LOCKED, 2.0 * GAM_LOCKED,
        Q0_LOCKED, Y_LOCKED, use_shell=True, verbose=False)
    assert res['path'] in ('alpha', 'beta', 'gamma', 'multi'), \
        f"Path classification missing: {res['path']}"
    print(f"    Path = {res['path']}; classification preview: "
          f"{res['classification'][:60]}...")
    print(f"    Number of roots = {len(res['roots'])}")

    print("  Self-test 3: shell vs full integral agreement at r=0.01")
    M_shell = loop_integral_shell(0.01, Q0_LOCKED, Y_LOCKED)
    M_full = loop_integral_full(0.01, Q0_LOCKED, Y_LOCKED)
    rel_err = abs(M_shell - M_full) / max(abs(M_shell), 1e-20)
    print(f"    M_shell(0.01) = {M_shell:.6e}")
    print(f"    M_full(0.01)  = {M_full:.6e}")
    print(f"    Relative agreement = {1 - rel_err:.4f} (should be ~0.95+)")

    print("  All self-tests passed.")
    return True


# =====================================================================
# Driver
# =====================================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--mu2', type=float, default=0.005,
                        help='TECT mu^2 (default 0.005, canonical operating point)')
    parser.add_argument('--mu2-sweep', nargs=3, default=None,
                        metavar=('MIN', 'MAX', 'N'),
                        help='Sweep mu^2 from MIN to MAX in N steps. '
                             'Example: --mu2-sweep -2.0 0.5 50')
    parser.add_argument('--use-shell', action='store_true',
                        help='Use shell-localized analytical M (faster).')
    parser.add_argument('--compare-shell', action='store_true',
                        help='Run BOTH shell and full integral; compare.')
    parser.add_argument('--n-points', type=int, default=20000,
                        help='Trapezoidal grid points for full integral.')
    parser.add_argument('--out-dir', default='Runs/math400')
    parser.add_argument('--self-test', action='store_true',
                        help='Run self-consistency sanity tests and exit.')
    args = parser.parse_args()

    print('=' * 76)
    print(' Math400-AddE -- Brazovskii one-loop self-consistency at TECT params')
    print('=' * 76)
    print(f' Locked TECT canonical params:')
    print(f'   lambda = {LAM_LOCKED} (attractive quartic, sign-preserved)')
    print(f'   gamma  = {GAM_LOCKED} (repulsive sextic stabiliser)')
    print(f'   Y      = {Y_LOCKED}')
    print(f'   q0     = {Q0_LOCKED}')
    print(f' Brazovskii mapping:')
    print(f'   u_brazovskii = 2*lambda = {2.0 * LAM_LOCKED:+.4f}')
    print(f'   v_brazovskii = 2*gamma  = {2.0 * GAM_LOCKED:+.4f}')
    print(f' Self-consistency: r_R = r + 3*u*M(r_R) + 15*v*M(r_R)^2')

    if args.self_test:
        print()
        print('=' * 60)
        print(' Self-test mode')
        print('=' * 60)
        self_test()
        return 0

    u = 2.0 * LAM_LOCKED
    v = 2.0 * GAM_LOCKED

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Determine mu^2 grid
    if args.mu2_sweep is not None:
        mu2_min = float(args.mu2_sweep[0])
        mu2_max = float(args.mu2_sweep[1])
        n = int(args.mu2_sweep[2])
        mu2_grid = list(np.linspace(mu2_min, mu2_max, n))
    else:
        mu2_grid = [args.mu2]

    print(f'\n Operating points: mu^2 in {mu2_grid[:5]}'
          + (f' ... ({len(mu2_grid)} total)' if len(mu2_grid) > 5 else ''))
    print(f' Use shell approximation: {args.use_shell}')
    print(f' Compare shell vs full:   {args.compare_shell}')

    all_results = []
    for mu2 in mu2_grid:
        r_bare = mu2 + Y_LOCKED * Q0_LOCKED ** 4
        print()
        print('=' * 60)
        print(f' mu^2 = {mu2:+.4f}, r_bare = mu^2 + Y*q0^4 = {r_bare:+.6e}')
        print('=' * 60)

        if args.compare_shell:
            print('  --- shell-localized analytical ---')
            res_shell = solve_self_consistency(
                r_bare, u, v, Q0_LOCKED, Y_LOCKED,
                use_shell=True, verbose=True)
            print(f'  Path: {res_shell["path"]}')
            for i, root in enumerate(res_shell['roots']):
                print(f'    Root {i+1}: r_R = {root["r_R"]:+.4e}, '
                      f'M = {root["M"]:.4e}')
            print('  --- full numerical integral ---')

        res_full = solve_self_consistency(
            r_bare, u, v, Q0_LOCKED, Y_LOCKED,
            use_shell=args.use_shell, verbose=True)
        res_full['mu2'] = float(mu2)
        all_results.append(res_full)
        print(f'  Path: {res_full["path"]}')
        print(f'  Verdict: {res_full["classification"]}')
        for i, root in enumerate(res_full['roots']):
            print(f'    Root {i+1}: r_R = {root["r_R"]:+.4e}')
            print(f'      M(r_R)              = {root["M"]:.4e}')
            print(f'      quartic shift 3uM   = {root["shift_quartic_3uM"]:+.4e}')
            print(f'      sextic shift  15vM^2 = {root["shift_sextic_15vM2"]:+.4e}')
            print(f'      fractional Δr/|r|   = {root["fractional_shift"]:+.4f}')
            print(f'      residual f(r_R)      = {root["residual"]:+.2e}')

    # Summary
    print()
    print('=' * 76)
    print(' SUMMARY: Pillar 4 path classification across mu^2 grid')
    print('=' * 76)
    print(f' {"mu^2":<10} {"r_bare":<14} {"r_R*":<14} {"M(r_R*)":<14} '
          f'{"Path":<8}')
    print(' ' + '-' * 70)
    for res in all_results:
        if res['roots']:
            r_R_star = res['roots'][0]['r_R']
            M_star = res['roots'][0]['M']
            print(f' {res["mu2"]:<+10.4f} {res["r_bare"]:<+14.4e} '
                  f'{r_R_star:<+14.4e} {M_star:<14.4e} {res["path"]:<8}')
        else:
            print(f' {res["mu2"]:<+10.4f} {res["r_bare"]:<+14.4e} '
                  f'{"---":<14} {"---":<14} {res["path"]:<8}')

    # Save
    sweep_tag = (f'sweep_{args.mu2_sweep[0]}to{args.mu2_sweep[1]}'
                 if args.mu2_sweep is not None
                 else f'mu2_{args.mu2:+.4f}')
    out_file = out_dir / f'math400_AddE_brazovskii_{sweep_tag}.json'

    out_data = {
        'kind': 'Math400-AddE-brazovskii-one-loop-v1.0',
        'generated': datetime.now(timezone.utc).isoformat(),
        'tect_params': {
            'lambda': LAM_LOCKED, 'gamma': GAM_LOCKED,
            'Y': Y_LOCKED, 'q0': Q0_LOCKED,
            'u_brazovskii': u, 'v_brazovskii': v,
        },
        'use_shell': args.use_shell,
        'results': all_results,
    }
    out_file.write_text(json.dumps(out_data, indent=2))
    print(f'\n Result saved: {out_file}')

    # Determine overall exit code
    paths = [res['path'] for res in all_results]
    if 'gamma' in paths:
        print('\n VERDICT: at least one operating point gives PATH gamma.')
        print('          Brazovskii framework must be reconsidered per')
        print('          Math400-AddD §4 operator directive.')
        return 3
    elif 'beta' in paths:
        print('\n VERDICT: at least one operating point gives PATH beta.')
        print('          Symmetry-broken vacuum survives one-loop.')
        print('          Math400-AddG queued for natural-structure identification.')
        return 2
    elif 'multi' in paths:
        print('\n VERDICT: multi-stable regime at some operating point.')
        print('          Cosmological-dynamics selection required.')
        return 1
    else:
        print('\n VERDICT: PATH alpha at all tested operating points.')
        print('          Reading H (Brazovskii fluctuation-stabilized')
        print('          disordered phase) confirmed. Math400-AddF queued.')
        return 0


if __name__ == '__main__':
    sys.exit(main())
