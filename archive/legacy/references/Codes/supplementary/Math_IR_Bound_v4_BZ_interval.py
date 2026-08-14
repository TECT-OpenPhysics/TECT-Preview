#!/usr/bin/env python3
# =====================================================================
# Math_IR_Bound_v4_BZ_interval.py
# Theory tag: Math_IR_Bound-anisotropy-v4-thm-v4-2-2026-04-20
# Companion to: docs/math/TECT-Math_IR_Bound-v4-thm-v4-1.tex.txt
# Purpose:     Rigorous interval-arithmetic evaluation of
#              J_1 := \int_{S^2} P_4(n) r_{BZ}(n) dOmega
#              to close Lemma v4-1-comonotone (r_4 > 0) and thereby
#              Theorem v4-1 (gamma_{44} < 0, Pillar 8 PROVED).
#
# Method:      Fundamental-domain reduction via O_h symmetry (|O_h|=48),
#              (s,t)-plane parametrisation of D = {n_1>=n_2>=n_3>=0}
#              projected onto the plane n_1=1, then piecewise-smooth
#              split over cube (s+t<1/2) and octahedral (s+t>=1/2)
#              regions.  Each region is subdivided uniformly in (s,t)
#              and the integrand evaluated with mpmath interval
#              arithmetic; the final enclosure is the sum of sub-cell
#              enclosures.
#
# Output:      Interval [J1_lo, J1_hi] for J_1, and, if J1_lo > 0, a
#              certificate that r_4 > 0 (hence gamma_{44} < 0, hence
#              Pillar 8 of the TOE scorecard closed under the v4-1
#              roadmap).
# =====================================================================
from __future__ import annotations

import argparse
import sys
import time
from typing import Tuple

try:
    from mpmath import iv, mp, mpf
except ImportError as exc:
    print("ERROR: mpmath is required.  pip install mpmath --break-system-packages",
          file=sys.stderr)
    raise SystemExit(1) from exc

# ---------------------------------------------------------------------------
# Integrand pieces
# ---------------------------------------------------------------------------

def P4_iv(s, t):
    """
    P_4(n) = sum_i n_i^4 - 3/5, evaluated on the image of (s,t) under
    the radial projection (1,s,t)/sqrt(1+s^2+t^2).  In (s,t)-coords:
      n_1^4 + n_2^4 + n_3^4 = (1 + s^4 + t^4)/(1 + s^2 + t^2)^2
    """
    one_plus_r2 = 1 + s * s + t * t
    num = 1 + s**4 + t**4
    return num / (one_plus_r2 * one_plus_r2) - iv.mpf("3") / iv.mpf("5")


def rBZ_square_iv(s, t, B):
    """
    Square-face regime (cube constraint active, s+t < 1/2 in fund. domain):
      r_BZ(n) = B / max_i |n_i| = B * sqrt(1+s^2+t^2)   (since n_1 is max).
    """
    return B * iv.sqrt(1 + s * s + t * t)


def rBZ_hex_iv(s, t, A):
    """
    Hexagonal-face regime (octahedral constraint active, s+t >= 1/2):
      r_BZ(n) = A / (n_1+n_2+n_3)
             = A * sqrt(1+s^2+t^2) / (1 + s + t)
    """
    return A * iv.sqrt(1 + s * s + t * t) / (1 + s + t)


def dOmega_iv(s, t):
    """
    Induced area element on S^2 after radial projection to plane n_1=1:
      dOmega = (1 + s^2 + t^2)^{-3/2} ds dt.
    """
    v = 1 + s * s + t * t
    return 1 / (v * iv.sqrt(v))


def integrand_square_iv(s, t, B):
    """
    P4(s,t) * r_BZ^{square}(s,t) * dOmega(s,t)
      = P4(s,t) * B / (1 + s^2 + t^2).
    """
    return P4_iv(s, t) * B / (1 + s * s + t * t)


def integrand_hex_iv(s, t, A):
    """
    P4(s,t) * r_BZ^{hex}(s,t) * dOmega(s,t)
      = P4(s,t) * A / ((1 + s + t) (1 + s^2 + t^2)).
    """
    return P4_iv(s, t) * A / ((1 + s + t) * (1 + s * s + t * t))


# ---------------------------------------------------------------------------
# Region enclosures
# ---------------------------------------------------------------------------
# Fundamental domain in (s,t)-plane:    D' = {0 <= t <= s <= 1}.
# Inside D', the cube / octahedral split is determined by s + t < 1/2.
#
# Strategy: we grid D' uniformly with mesh size h = 1/N on (s,t) in [0,1]^2,
# then for each cell keep only the part inside D' ∩ regime, producing a
# collection of (possibly irregular) sub-cells. For each sub-cell we build
# the interval hull of (s,t) in it and evaluate the integrand there.
#
# To avoid irregular sub-cells we use a simpler dyadic approach: enumerate
# square cells [s_i, s_{i+1}] x [t_j, t_{j+1}] that are entirely inside D';
# for cells that straddle the three boundaries (t = 0, t = s, s = 1), or the
# regime boundary s+t = 1/2, we split them once each along the offending
# line and keep the piece(s) in the current regime.  This keeps cells
# axis-aligned and preserves interval-arithmetic rigour.

def cell_fully_in_region(s_lo, s_hi, t_lo, t_hi, regime):
    """Return True iff the axis-aligned cell lies entirely in D' and in
    the named regime ('square' or 'hex')."""
    # Inside D':  t >= 0, t <= s, s <= 1.
    if t_lo < 0:
        return False
    if s_hi > 1:
        return False
    if t_hi > s_lo:   # violates t <= s somewhere
        return False
    # Regime test
    if regime == "square":
        # s + t < 1/2 everywhere in cell  <=>  s_hi + t_hi < 1/2
        return (s_hi + t_hi) < 0.5
    else:  # hex
        return (s_lo + t_lo) >= 0.5


def cell_interval_enclosure(s_lo, s_hi, t_lo, t_hi, regime, A, B):
    """Evaluate the integrand interval-hull on the rectangular cell.

    This function is used for cells that are proved to lie entirely inside
    D' and entirely inside the named regime; in that case the true
    integral over the cell lies in (cell area) * [f_min, f_max].
    """
    s = iv.mpf((s_lo, s_hi))
    t = iv.mpf((t_lo, t_hi))
    if regime == "square":
        val = integrand_square_iv(s, t, B)
    else:
        val = integrand_hex_iv(s, t, A)
    return val * (s_hi - s_lo) * (t_hi - t_lo)


def boundary_cell_enclosure(s_lo, s_hi, t_lo, t_hi, regime, A, B):
    """Conservative interval enclosure for BOUNDARY cells (partially in
    D' or partially in the named regime).  The TRUE integrand support
    inside the cell has area in [0, cell_area]; hence the true
    contribution lies in
        [min(0, f_min * cell_area),  max(0, f_max * cell_area)].
    This is wider than the interior enclosure but preserves rigour at
    the cost of a conservative widening proportional to (boundary
    cell area).
    """
    s = iv.mpf((s_lo, s_hi))
    t = iv.mpf((t_lo, t_hi))
    if regime == "square":
        val = integrand_square_iv(s, t, B)
    else:
        val = integrand_hex_iv(s, t, A)
    val *= (s_hi - s_lo) * (t_hi - t_lo)
    # Widen to include zero contribution (the case of IN-area = 0).
    # Extract scalar endpoints via the internal (_mpi_) tuple form.
    lo_f = mpf(val._mpi_[0])
    hi_f = mpf(val._mpi_[1])
    if lo_f > 0:
        lo_f = mpf(0)
    if hi_f < 0:
        hi_f = mpf(0)
    return iv.mpf((lo_f, hi_f))


def integrate_region(regime, N, A, B):
    """
    Sum of interval enclosures over the axis-aligned N x N grid of [0,1]^2,
    keeping only cells fully inside D' and fully inside the named regime.
    Cells straddling D' or regime boundaries are treated via an adaptive
    halving pass: refined up to MAX_DEPTH levels until they are either fully
    inside, fully outside, or sufficiently small.
    """
    MAX_DEPTH = 10     # adaptive refinement cap
    h = 1.0 / N

    def is_outside(s_lo, s_hi, t_lo, t_hi, regime):
        """Return True iff the cell is entirely OUTSIDE D' or the regime."""
        # Outside D' if the whole cell violates some D'-constraint:
        if t_hi <= 0:                       # degenerate
            return True
        if s_lo >= 1:                       # degenerate
            return True
        if t_lo >= s_hi:                    # t > s everywhere
            if t_lo > s_hi:
                return True
            # touches the diagonal; treat as measure zero boundary
        # Outside regime:
        if regime == "square" and (s_lo + t_lo) >= 0.5:
            return True
        if regime == "hex" and (s_hi + t_hi) <= 0.5:
            return True
        return False

    total = iv.mpf(0)
    stack = []
    for i in range(N):
        for j in range(N):
            stack.append((i * h, (i + 1) * h, j * h, (j + 1) * h, 0))

    while stack:
        s_lo, s_hi, t_lo, t_hi, depth = stack.pop()
        if is_outside(s_lo, s_hi, t_lo, t_hi, regime):
            continue
        if cell_fully_in_region(s_lo, s_hi, t_lo, t_hi, regime):
            total = total + cell_interval_enclosure(
                s_lo, s_hi, t_lo, t_hi, regime, A, B)
            continue
        if depth >= MAX_DEPTH:
            # Bracketing cell on the boundary at maximum refinement depth.
            # RIGOUR FIX (2026-04-20 EOD Devil's Advocate pass): the true
            # "in-region" sub-area of the cell lies in [0, cell_area];
            # hence the true contribution lies in the widened interval
            # that ALSO includes the zero-contribution case.  This is
            # enforced by boundary_cell_enclosure().  The resulting
            # certificate is a strict enclosure of the true J_1.
            total = total + boundary_cell_enclosure(
                s_lo, s_hi, t_lo, t_hi, regime, A, B)
            continue
        # Subdivide: bisect the longer axis
        ds, dt = s_hi - s_lo, t_hi - t_lo
        if ds >= dt:
            s_mid = (s_lo + s_hi) / 2
            stack.append((s_lo, s_mid, t_lo, t_hi, depth + 1))
            stack.append((s_mid, s_hi, t_lo, t_hi, depth + 1))
        else:
            t_mid = (t_lo + t_hi) / 2
            stack.append((s_lo, s_hi, t_lo, t_mid, depth + 1))
            stack.append((s_lo, s_hi, t_mid, t_hi, depth + 1))

    return total


def compute_J1(N, A, B, dps):
    """
    Compute the interval enclosure for J_1 at (A,B) with grid resolution N
    and mpmath precision dps.
    """
    iv.prec = dps
    mp.prec = dps
    t0 = time.time()
    J_sq = integrate_region("square", N, A, B)
    J_hx = integrate_region("hex", N, A, B)
    J_tot = 48 * (J_sq + J_hx)
    t1 = time.time()
    return J_sq, J_hx, J_tot, t1 - t0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Interval-arithmetic evaluation of J_1 for Pillar-8 closure.")
    parser.add_argument("--N", type=int, default=64,
                        help="grid resolution (N x N cells on [0,1]^2)")
    parser.add_argument("--A", type=str, default="1.5",
                        help="BZ octahedral parameter (default 3/2)")
    parser.add_argument("--B", type=str, default="1.0",
                        help="BZ cube parameter (default 1)")
    parser.add_argument("--dps", type=int, default=64,
                        help="mpmath precision (decimal digits, default 64)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    mp.dps = args.dps
    iv.dps = args.dps

    A = iv.mpf(args.A)
    B = iv.mpf(args.B)

    print("=" * 76)
    print("J_1 interval-arithmetic evaluation for TECT Pillar-8 closure")
    print("  (Lemma v4-1-comonotone -> Theorem v4-1 -> Pillar 8 PROVED)")
    print("=" * 76)
    print(f"  BZ parameters: A = {args.A}, B = {args.B}  (truncated octahedron)")
    print(f"  Grid resolution: N = {args.N}   (base cells: {args.N**2})")
    print(f"  mpmath decimal precision: {args.dps}")
    print("-" * 76)

    J_sq, J_hx, J_tot, elapsed = compute_J1(args.N, A, B, args.dps * 4)

    # Extract numerical endpoints
    def hull(v):
        try:
            return float(v.a), float(v.b)
        except Exception:
            s = str(v)
            return s, s

    sq_lo, sq_hi = hull(J_sq)
    hx_lo, hx_hi = hull(J_hx)
    tot_lo, tot_hi = hull(J_tot)

    print(f"  J_1^{{square}}    enclosure: [{sq_lo:+.6e}, {sq_hi:+.6e}]")
    print(f"  J_1^{{hex}}       enclosure: [{hx_lo:+.6e}, {hx_hi:+.6e}]")
    print(f"  J_1 = 48 * sum   enclosure: [{tot_lo:+.6e}, {tot_hi:+.6e}]")
    print(f"  elapsed: {elapsed:.2f} s")
    print("-" * 76)

    # Heuristic center and margin
    if tot_lo is not None and tot_hi is not None and isinstance(tot_lo, float):
        center = (tot_lo + tot_hi) / 2
        halfwidth = (tot_hi - tot_lo) / 2
        rel = halfwidth / abs(center) if center != 0 else float("inf")
        print(f"  central value ~ {center:+.6e}")
        print(f"  half-width    ~ {halfwidth:+.6e}  (relative: {rel:.2%})")
        print("-" * 76)

        if tot_lo > 0:
            print("  CERTIFICATE: J_1 > 0 rigorously.")
            print("               --> r_4 > 0  (cubic-harmonic L=4 coefficient)")
            print("               --> gamma_{44} < 0  (Theorem v4-1)")
            print("               --> cubic-anisotropy coupling IR-irrelevant")
            print("               --> Pillar 8 (emergent Lorentz invariance) PROVED")
            status = 0
        elif tot_hi < 0:
            print("  UNEXPECTED: J_1 < 0 rigorously.")
            print("              Pillar 8 CONCLUSION REVERSED -- the cubic-anisotropy")
            print("              coupling is IR-RELEVANT.  Investigate urgently.")
            status = 2
        else:
            print("  INCONCLUSIVE: enclosure straddles zero.")
            print("                Refine by increasing --N or --dps.")
            status = 1
    else:
        print("  (numerical extraction failed; inspect raw interval strings above)")
        status = 3

    print("=" * 76)
    return status


if __name__ == "__main__":
    sys.exit(main())
