# A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE -- finite-volume constructive measure

**Tier**: T5 CLOSED@FINITE-VOLUME-REAL-SCALAR-SPECTRAL (TSv2) |
**Lifecycle**: ACTIVE |
**Last review**: 2026-07-18

## Closed statement

On the fixed three-torus, let the real scalar covariance be the inverse of
the positive Brazovskii operator

`K(k) = m_sh^2 + Y (|k|^2-q0^2)^2`,

with `m_sh^2 > 0` and `Y > 0`.  For the local interaction

`V(phi) = integral [lambda phi^4/4 + gamma phi^6/6]`,

with arbitrary real `lambda` and `gamma > 0`, the full sharp spectral
Galerkin sequence converges weakly on real `L2` to a non-perturbative
finite-volume Gibbs measure.  The common-Gaussian lifted densities converge
in `L1`/total variation.  Partition functions and finite-degree smeared
cylinder-polynomial correlations converge along the full cutoff sequence.

## Scope and separation

This is a new claim.  It does not widen the perturbative A3 theorem or the P3
PDE-discretization theorem.  The scalar local interaction is isolated first
because a `q^-4` Gaussian covariance is trace class in three dimensions and
the local polynomial is defined on its samples.

The full production Class-II energy contains derivative currents.  Typical
samples of the scalar `q^-4` Gaussian have only `H^s`, `s<1/2`, regularity, so
the derivative-current squares are not automatically defined.  That extension
requires a separate divergence/renormalisation analysis and is excluded here.

## Closed proof chain

1. The exact max-shell count `24 m^2+2` and the `q^-4` covariance tail prove
   `Tr K^-1 < infinity`; the covariance is trace class on `H^s` exactly below
   the `s=1/2` threshold.
2. A direct Gaussian sixth-moment tail proves `P_N phi -> phi` in
   `L6(Omega x T3)`.  No false `H^(1/2-) -> L6` embedding is used.
3. The exact pointwise minimum
   `lambda phi^4/4+gamma phi^6/6 >= -|min(lambda,0)|^3/(12 gamma^2)`
   bounds every Gibbs weight, while Jensen gives a uniform positive lower
   bound for every partition function.
4. Common-Gaussian `L6` convergence gives interaction convergence; uniform
   weight domination then gives `L1` convergence of normalized densities.
5. The density limit identifies the full sequence.  Projected laws converge
   weakly on `L2`, and uniform Gaussian moments give the declared smeared
   cylinder-polynomial correlations.
6. The 17/17 primary audit and non-importing 14/14 reconstruction are rerun
   together by the 31/31 one-command verifier.

## Dependencies and gates

- Hard dependency: `A1-SCALAR-ANALYTIC-BRANCH`.
- Named hypotheses: `A1-SHELL-POSITIVITY`,
  `A2-H2-SEXTIC-COERCIVITY`.
- Soft anchors: `A1-PRODUCTION-KERNEL-MANIFEST`,
  `A1-PRODUCTION-FUNCTIONAL-REALISATION`, and
  `A3-PERTURBATIVE-CONTINUUM-CORRELATORS`.
- Closed gate: `A4-CONSTRUCTIVE-MEASURE-CLOSURE` at the pinned T5 scalar scope.

## Devil's-advocate record

1. **"Trace class alone proves the local sextic is defined."** UPHELD as
   false.  The proof separately establishes Gaussian `L6` convergence from
   the pointwise sixth-moment identity.
2. **"The proof can use `H^(1/2-) -> L6` in three dimensions."** UPHELD as
   false.  That embedding is unavailable; the direct Gaussian route repairs
   this likely hidden error.
3. **"A negative quartic leaves the Gibbs weight unbounded."** DISMISSED under
   the stated hypotheses.  The positive sextic supplies the exact global
   lower bound and a deterministic uniform weight ceiling.
4. **"Tightness of one subsequence is regulator removal."** UPHELD as false.
   `L1` convergence of the common-space densities identifies the full
   sequence before tightness is invoked.
5. **"The embedded Galerkin laws converge in total variation."** UPHELD as
   false.  Only lifted common-Gaussian laws have total-variation convergence;
   the actual finite-dimensional laws converge weakly on `L2`.
6. **"All local correlations and derivative Class-II terms are included."**
   UPHELD as false.  Only finite-degree smeared cylinder polynomials are
   closed; derivative currents require a separate construction or
   renormalization analysis.
7. **"A finite-volume Gibbs measure proves a phase transition or BCC
   selection."** UPHELD as false.  Both require additional limits or
   selection arguments and are excluded.

## Quantitative sanity checks

- The independent scalar-loop traces agree with the vectorized traces to at
  most `1.32e-16` relative error at cutoff 8.
- The production-local shell mass is independently reconstructed as
  `0.260000000009475`, agreeing with the stored `mu2=0.26` within the declared
  upstream decimal tolerance.
- The conservative covariance-trace upper bounds are `3029.399163006103` for
  the perturbative mass and `596.857766699839` for the production-local mass.
- The exact pinned-coefficient stability constant is
  `0.0025246087994716246` per unit volume.  These values are derived sanity
  checks, not physical predictions.

## Promotion rationale

The T3-to-T5 transition uses the tier-system exception for a one-shot
textbook argument.  The proof is self-contained, the package has two
non-importing executable reconstructions, all 31 integrated assertions pass,
and the visually checked PDF has no overfull boxes.  T6 is deliberately not
claimed: independent operator execution was pre-registered before that
review.

## Reproduction

The available one-command reproduction is:

```bash
python codes/foundations/a4_scalar_constructive_measure_verify.py
```

It must print:

```text
PASS: primary (17/17)
PASS: independent (14/14)
ASSERTS: 31/31
A4-SCALAR-CONSTRUCTIVE-INTEGRATED-PASS
```

## No-overclaim

This T5 pinned scalar closure does not cover the full three-component
derivative Class-II functional, unsmeared composite operators, infinite
volume, phase transition, finite-difference Route B, BCC existence or
selection, T6/T7, or the future P5 Sector-A synthesis.

## Next required action

Run the one-command verifier independently from a normal operator checkout
and preserve that output in a new operator-evidence run directory.  Then
perform the separately recorded scoped T6 conditional-theorem review.
