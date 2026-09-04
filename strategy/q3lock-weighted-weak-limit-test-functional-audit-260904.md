# Q3LOCK weighted weak-limit test-functional audit

**Status:** T0 research audit; no claim-card promotion  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until the final mathematical and independent-audit stage

## 1. Purpose and scope

The grid-to-loop argument needs more than weak convergence of the reference
Gaussian measures.  The finite-grid laws contain a bounded, positive local and
spatial weight, and the manuscript must show that both the numerator tested
against a bounded continuous functional and the denominator converge.  This
note writes that passage as a separate epsilon argument so that no hidden
uniform Riemann-sum assertion on a noncompact sup-norm ball is used.

The statement is only for a fixed finite spatial box `Lambda`, a fixed
`beta`, a fixed harmonic split `a>0`, and a compact source interval.  It does
not prove the Feynman--Kac identification, a spatial thermodynamic limit, or
any strict cusp or DLR multiplicity statement.

## 2. Measures and weights

Let `G_N` denote the law of the periodic piecewise-linear interpolation
`I_N x` of the time-grid Gaussian, viewed as a probability measure on
`X_Lambda = C_per([0,beta]; R^8)^Lambda`.  The finite-grid residual weight,
including the onsite term, source term, and spatial bonds, is denoted by
`r_N,h(I_N x)`.  The limiting loop weight is `r_h(omega)`.  The quartic lower
bound gives a source-uniform constant `B<infinity` such that

```text
0 <= r_N,h <= B,       0 <= r_h <= B.
```

The exact value of `B` is not needed here; it is obtained from the common
lower bound on the residual potential after the positive harmonic split.  Set

```text
Z_N(h) = integral r_N,h dG_N,
Z(h)   = integral r_h dG_a.
```

The target weighted measures are

```text
nu_N,h = r_N,h G_N / Z_N(h),
nu_h   = r_h G_a   / Z(h).
```

The previously recorded sup-norm event supplies a common positive lower bound
`Z_N(h)>=z_*>0`.  The same compact/tightness argument below gives
`Z_N(h)->Z(h)`, hence `Z(h)>=z_*` once the limit argument is established.

## 3. Compact-set decomposition

Fix a bounded continuous test functional `F` on `X_Lambda`, with
`||F||_infty <= M_F`.  For a compact set `K` and `N` large enough that
`K` is a common domain for the uniform Riemann-sum estimate, write

```text
| integral F r_N,h dG_N - integral F r_h dG_a |
 <= | integral_K F (r_N,h-r_h) dG_N |
  + | integral_K F r_h dG_N - integral_K F r_h dG_a |
  + 2 M_F B max(G_N(K^c), G_a(K^c)).
```

This display is shorthand for inserting a continuous cutoff equal to one on
`K` and supported in a small neighbourhood; the cutoff avoids treating the
indicator of `K` as a continuous test function.  The three terms are handled
in different ways:

1. **Weight term.**  Arzela--Ascoli gives boundedness and equicontinuity on
   `K`.  Therefore the local and spatial Riemann sums converge uniformly on
   `K`, so
   `sup_{omega in K, |h|<=h0}|r_N,h(omega)-r_h(omega)| -> 0`.

2. **Reference-law term.**  The Gaussian grid laws satisfy
   `G_N => G_a`.  The function `F r_h` times the cutoff is bounded and
   continuous, so its integrals converge.

3. **Tail term.**  The common bound `B` controls the tail without requiring
   pointwise convergence outside `K`.

Tightness of `{G_N}` and the limit law allows `K` to be chosen so that the
tail term is arbitrarily small, uniformly for all sufficiently large `N`.
Consequently,

```text
integral F r_N,h dG_N  ->  integral F r_h dG_a.
```

The same argument with `F=1` proves `Z_N(h)->Z(h)`.  It is important that
`K` is compact and equicontinuous; an arbitrary bounded sup-norm ball is not
enough for uniform Riemann-sum convergence.

## 4. Division by the normalizer

Since `Z_N(h)>=z_*>0` and `Z_N(h)->Z(h)`, the limit also obeys
`Z(h)>=z_*>0` after possibly decreasing `z_*` by a harmless fixed factor.
For every bounded continuous `F`,

```text
| integral F dnu_N,h - integral F dnu_h |
 <= z_*^(-1) | integral F r_N,h dG_N - integral F r_h dG_a |
  + M_F |Z_N(h)-Z(h)| / z_*^2.
```

Both terms vanish.  Thus `nu_N,h => nu_h` for each source in the compact
source interval.  If a source-uniform conclusion is required later, the
compact-set estimates must be written with constants uniform in `|h|<=h0`;
pointwise-in-`h` weak convergence alone does not provide that stronger
statement.

## 5. Increasing functionals and association passage

If `F` and `G` are bounded continuous pointwise-increasing functionals of the
loop, first add constants so that both are nonnegative.  The covariance form
of association is unchanged by these shifts, and then `FG` is again bounded,
continuous and increasing.  The finite-grid association inequality applies to
the corresponding interpolated functionals.  Applying the preceding
weak-limit result to `F`, `G`, and `FG` gives

```text
E_h[FG] >= E_h[F] E_h[G].
```

For coordinate products that are unbounded, use monotone bounded clips
`F_R=max(-R,min(F,R))` and the common quartic second-moment bound.  The proof
must record the uniform-integrability estimate that removes the clips; weak
convergence by itself is insufficient for unbounded observables.

This establishes only the bounded-continuous association route needed for the
collective Q3 projection.  It does not imply total-variation convergence,
path-space MTP2, or an independent infinite-dimensional FKG theorem.

## 6. Remaining audit obligations

* State the exact Gaussian tightness result used to choose the common compact
  set and verify the interpolation topology.
* Give the uniform Arzela--Ascoli Riemann-sum estimate for both onsite and
  spatial terms, including the source-uniform version if differentiation in
  `h` is later attempted.
* Record the quartic moment estimate used in the clip-removal step with all
  constants and its self-test.
* Separately identify the finite-volume Feynman--Kac/Trotter theorem and check
  its form-domain hypotheses; this note does not close that operator gate.

Until these items are independently audited, P-06 remains `PROOF TEXT AND
EXTERNAL AUDIT REQUIRED`, and no strict cusp or phase-coexistence claim may be
registered from this note.

## 7. Nonclaims and publication boundary

No new claim card, tier change, result promotion, manuscript release, commit,
or PDF is created by this audit.  PDF generation and visual review remain
reserved for the final stage after the mathematical text, literature
crosswalk, independent proof audit, and reproducibility checks are complete.
