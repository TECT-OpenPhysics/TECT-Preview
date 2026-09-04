# Q3LOCK FKG time-grid normalizer and tightness check

**Status:** T0 research addendum; not a claim card or manuscript  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Scope:** finite spatial volume and compact source interval only  
**PDF:** deferred

## 1. Purpose

The continuous-loop FKG route uses a positive-harmonic time-grid reference.
The weak-limit argument requires a normalizer lower bound that includes both
the local potential and the finite-volume spatial bonds.  This addendum makes
that bound explicit and separates it from the still-open Feynman--Kac
identification and independent audit.

Let `Lambda` be a fixed finite spatial box with `V=|Lambda|` sites and
`E=|E(Lambda)|` nearest-neighbour bonds.  Set `epsilon=beta/N` and let
`G_N` be the product periodic Ornstein--Uhlenbeck reference with positive
harmonic split `a>0`.  For grid variables `x_(y,k) in R^8`, write the
interpolated weight as

```text
R_N(x) = exp[-epsilon sum_(y,k) V_h(x_(y,k))]
         * exp[-epsilon*c/2 sum_(k,<yz>) |x_(y,k)-x_(z,k)|^2].
```

The source interval `|h|<=h0` has a common quartic lower bound
`V_h(q)>=A|q|^4-C` and a common continuous quartic upper function.

## 2. Mesh-uniform lower bound

Choose `R` so that the piecewise-linear Gaussian interpolations have

```text
G_N(B_R) >= 1/2,
B_R = { max_(y) ||I_N x_y||_infinity <= R },
```

for all sufficiently large `N`.  At fixed finite `Lambda`, continuity of the
common upper function gives a finite `M_R` with `V_h(q)<=M_R` whenever
`||q||<=R` (with the component/norm convention fixed once in the
manuscript).  On `B_R`, every spatial difference is bounded by a constant
`K_R` depending only on `R` and the norm convention, so

```text
epsilon * sum_(k,<yz>) |x_(y,k)-x_(z,k)|^2
    <= beta * E * K_R^2.
```

Therefore the full weight, including all spatial bonds, obeys

```text
R_N(x) >= exp[-beta*V*M_R - beta*c*E*K_R^2/2]
```

on `B_R`, and hence

```text
Z_N(h) = integral R_N dG_N
      >= (1/2) exp[-beta*V*M_R - beta*c*E*K_R^2/2].
```

This lower bound is independent of the time-grid size `N`.  The upper bound
from the quartic lower control is likewise uniform:

```text
R_N(x) <= exp(beta*V*C),
```

because the spatial factor is at most one.  The ratio `R_N/Z_N(h)` is thus
uniformly bounded at fixed finite volume and compact source interval.

## 3. Tightness and moments

The positive-harmonic Gaussian interpolation has mesh-uniform modulus
estimates in the periodic continuous-loop sup-norm topology.  The preceding
normalizer bound and the uniform upper weight transfer tightness from `G_N` to
the weighted grid laws.  Gaussian polynomial moments are uniformly bounded;
the quartic lower control and the same ratio estimate give uniform moments for
the weighted laws.  In particular, coordinate clips can be removed after the
association inequality by uniform integrability of second moments.

This calculation closes the previously implicit spatial-factor part of the
normalizer obligation.  It does not prove the Gaussian modulus estimate or the
Feynman--Kac/Trotter identification.  Those remain external-audit inputs to
P-06, and the time-grid limit must still be taken before the spatial
thermodynamic limit.

## 4. Nonclaims and next gate

No path-space MTP2 or total-variation convergence is asserted.  No strict
infrared lower bound, pressure cusp, DLR multiplicity, independent claim, P2
manuscript, release, or PDF is created.  The next gate is an independent audit
of the interpolation modulus estimate, the exact Trotter theorem and the
uniform-integrability passage using this explicit finite-volume normalizer.

