# R-367 larger-cutoff and volume stress for the fractional Liouvillian shell

## Result-first boundary

R-367 is a T0, claim-nonbearing finite stress under EXP-001209.  It tests the
`theta=1/2` R-366 square-function route on larger oscillator cutoffs and a
small graph-volume enlargement.  A bounded table is only a stress result;
it is not a uniform theorem.

## 1. Stress design

The exact Q3 builder is run for `V=2` with cutoffs `d=3,4,5,6`, and for the
square graph `V=4,d=2`.  For each regime, both beta values, both split
orientations, both time signs, both history adjoints, both measured sites
where available, and the `zero`, `first`, and `full` prefixes are checked.
Only `theta=1/2` is used because it is the proposed local Dirichlet target.

For every row the primary and independent lanes recompute the spectral phase
identity, the `min(2,|y|)` fractional envelope, the fractional shell bound,
the density-state trace bound, bond-unitary factorisation, and the R-364
spectral-commutant reduction.  The integrated lane compares all numeric
fields and compiles Lean R367's scalar envelope.

## 2. Adversarial review

1. **Volume interpretation.**  The `V=4,d=2` row is a finite square-graph
   stress, not an infinite-volume estimate and not a replacement for the
   allowed exhaustion family.
2. **Prefix coverage.**  The stress deliberately selects zero/first/full
   prefixes; arbitrary intermediate prefixes remain OPEN.
3. **Cutoff interpretation.**  The `d=3..6` values test growth but cannot
   prove a cutoff limit or a bounded supremum.
4. **Fractional endpoint.**  The result uses only `theta=1/2`; R-366's
   `theta=3/4,1` table is not silently extrapolated.
5. **State ordering.**  The trace estimate remains Hilbert--Schmidt Cauchy
   without assuming Gibbs/bond commutation.
6. **QFT promotion.**  A local modular comparison, common core, common
   alpha, OS/KMS/GNS, gap, continuum, C6, Sector-A and Pre-A remain OPEN.

## 3. Promotion and stop conditions

Promotion requires a genuine local Kubo--Mori/Dirichlet estimate with a
source-, cutoff-, volume-, history- and shape-independent constant.  If the
fractional norm grows along the tested cutoff or volume direction, preserve
that growth as a scoped obstruction; do not convert a finite maximum into a
uniform bound.  No R-367 PDF is issued.

