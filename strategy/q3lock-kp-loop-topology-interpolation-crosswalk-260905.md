# Q3LOCK KP loop topology and interpolation crosswalk

**Status:** T0 source/topology audit; P-04/P-09 remain pending independent review  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kozitsky--Kondratiev--Kozitsky, [arXiv:0710.2303](https://arxiv.org/pdf/0710.2303)  
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and strict separation of limits

The Q3LOCK time-grid construction uses periodic piecewise-linear paths, while
the Euclidean DLR theorem is formulated on the weighted tempered path space of
Kozitsky--Kondratiev--Kozitsky (KKK).  This note checks the topology in which
each statement is valid and prevents the following invalid shortcut:

```text
finite-grid weak convergence  =  KKK W_t compactness  =  DLR closure.
```

The correct order is:

1. at fixed finite spatial `Lambda`, prove grid convergence in the periodic
   continuous-loop topology needed for the Feynman--Kac weight;
2. identify that finite-volume loop law with the KKK Feynman--Kac law;
3. only then take spatial-volume accumulation points in the KKK weighted
   tempered topology and invoke the DLR theorem.

This is an audit of the interface, not a new DLR or infrared theorem.

## 2. Exact KKK path spaces and cited statements

For one `nu`-component oscillator, KKK defines the periodic loop space

```text
C_beta = {phi in C([0,beta];R^nu): phi(0)=phi(beta)}
```

with the usual sup norm (equations (2.16)--(2.18)).  The Holder subspace
`C_beta^sigma`, `0<sigma<1/2`, has norm `|phi(0)|+K_sigma(phi)` (2.19)--
(2.20).  The finite-volume path space `Omega_Lambda` is a finite product of
these loops with its product topology and Borel sigma algebra (2.21)--(2.22).
For finite `Lambda`, this is a Polish space equivalent to a finite-dimensional
product of the sup-norm loop spaces.

KKK's harmonic reference operator is

```text
A = (-m*d^2/dtau^2 + a) tensor I,
```

with periodic Fourier eigenvalues `m(2*pi*l/beta)^2+a` (2.24)--(2.25).  Its
Gaussian measure is first constructed on `L2_beta` by (2.26).  The increment
estimate (2.27) and Kolmogorov's lemma imply full measure of
`C_beta^sigma` for every `sigma<1/2` (2.28); the measure is then regarded as a
measure on `(C_beta,B(C_beta))`.

The interacting finite-volume law is the Feynman--Kac modification

```text
nu_Lambda(domega) = exp[-I_Lambda(omega)] chi_Lambda(domega)/N_Lambda
```

with the action and normalization in (2.33)--(2.37).  The Feller property of
the conditional specification is Proposition 2.4, equations (2.53)--(2.54).
The global tempered space is built from weighted `L2_beta` norms (2.45)--
(2.48), with projective-limit topology; the corresponding weak topology is
`W_t` (2.87 and the discussion preceding Proposition 2.12).  Proposition 2.12
gives nonemptiness, convexity and `W_t`-compactness of tempered Euclidean Gibbs
measures, while Proposition 2.21 puts spatial periodic accumulation points in
the DLR set.

The finite-volume `C_beta` statements and the infinite-volume `W_t` statements
are therefore different interfaces and must be cited separately.

## 3. Q3LOCK grid interpolation in the finite-volume topology

Fix finite periodic `Lambda`, `beta`, and a positive harmonic split `a>0`.
For `epsilon=beta/N`, let `G_(a,N)` be the periodic Gaussian grid law and let
`I_N` be periodic piecewise-linear interpolation.  The Q3LOCK covariance audit
gives finite-dimensional covariance convergence to the Green kernel of
`-m*d^2/dtau^2+a`, together with, for every `p>2`,

```text
E_(G_(a,N)) |I_Nx(t)-I_Nx(s)|^p <= C_p*d_circle(t,s)^(p/2),
```

uniformly in sufficiently large `N`.  Kolmogorov tightness in the periodic
sup-norm topology and Gaussian finite-dimensional identification therefore
give

```text
I_N#G_(a,N) => chi_a
```

on `C_beta^8` for each site and on the finite product `Omega_Lambda`.
This is exactly the finite-volume topology in which the KKK Feynman--Kac
weight is a measurable functional.  The grid proof does not need, and does
not claim, convergence in the Holder norm `C_beta^sigma`.

For a compact set `K` in the finite product sup-norm space, Arzela--Ascoli
gives common boundedness and equicontinuity.  Hence the local potential and
spatial-bond Riemann sums converge uniformly on `K` to their loop integrals.
The global quartic upper bound on the weight and the mesh-uniform normalizer
lower bound control the complement of `K`.  The normalized weighted laws thus
converge weakly on `Omega_Lambda` for bounded continuous tests.  No indicator of
an arbitrary sup-norm ball is used as a continuous test.

## 4. Continuity of the Q3LOCK Feynman--Kac action

The KKK action contains the local integrals and the pair term

```text
-1/2*sum_(y,z) J_yz*(omega_y,omega_z)_(L2_beta)
 +sum_y integral_0^beta V_(h,a)(omega_y(tau)) d tau.
```

For a finite `Lambda`, uniform convergence of loops implies convergence of
the `L2_beta` inner products and, because the image of a compact family of
loops lies in a common compact subset of `R^8`, uniform convergence of the
continuous local-potential integrals.  The Q3LOCK expansion assigns the
positive `3c` onsite term once to `V_(h,a)` and uses `J_yz=c` for each
ordered nearest-neighbour pair in the KKK convention.  The notation refers to
the explicit positive-direction edge multiset and retains periodic multiplicity
when `L=2`, as fixed by EXP-001512.  Thus the action in the grid limit is
exactly the action in the finite-volume crosswalk, with no
additional boundary or time-topology term.

The action itself is generally unbounded on the full loop space.  Weak
convergence of bounded continuous tests therefore does not imply convergence
of `exp(-I)` or of a source exponential without the quartic uniform-
integrability and normalizer estimates recorded in the Q3LOCK weighted-limit
and P-09 audits.

## 5. Exact source functional and interpolation order

For the collective zero-sum spatial coefficient `a_y` and
`u=(1,...,1)/sqrt(8)`, define

```text
X_L(omega) = sum_y a_y*integral_0^beta (u dot omega_y(tau)) d tau.
```

This is a continuous linear functional on the finite-volume sup-norm space.
For periodic piecewise-linear interpolation, the interval trapezoid identity
and cyclic endpoint telescope give

```text
X_L(I_Nx) = epsilon*sum_(y,k) a_y*(u dot x_(y,k))
```

exactly for every grid configuration.  Thus the source observable is
continuous in the topology used in Section 3 and has no separate Riemann-sum
error.  The exponential `exp(t X_L)` is unbounded, so its convergence still
uses the source-uniform quartic Young estimate and normalizer lower bound,
not weak convergence alone.

The interpolation is order preserving: on each interval it is a convex
combination of the two endpoint values.  This is sufficient to pass bounded
continuous increasing observables from the finite-grid association inequality
to the finite-volume loop law.  It does not define a lattice order on the
infinite-dimensional path space and does not imply path-space MTP2.

## 6. Interface with KKK tempered topology and DLR compactness

The finite-volume convergence above is a statement on `Omega_Lambda` with
finite `Lambda`.  To construct an infinite-volume state, use the KKK periodic
box laws and their weighted moment estimates in the global tempered space.
The quartic Q3LOCK bounds match the KKK hypotheses and give the required
uniform local Holder/L2 moments.  Proposition 2.21 then puts any `W_t`
accumulation point of periodic laws in the DLR set; Proposition 2.12 gives
the compactness of the resulting tempered state set.

The Q3LOCK source-tangent argument takes source values to zero only after the
finite-volume pressure and fixed-source DLR steps.  A compact-source uniform
integrability estimate is needed to pass the local linear observable through
this source limit.  The finite-volume sup-norm convergence in Section 3 does
not by itself prove this global `W_t` compactness or the DLR equation.

## 7. Adversarial checks

1. **The grid weak limit must be taken in `W_t`.**  False: the time-grid
   argument is first a fixed-finite-volume weak convergence on `Omega_Lambda`
   with the sup-norm topology; `W_t` enters only in the later spatial DLR
   accumulation step.
2. **Sup-norm convergence automatically gives Holder-norm convergence.**
   False: the grid proof uses sup-norm tightness; KKK's Holder support and
   exponential moment bounds are separate imported properties of the exact
   loop law.
3. **Uniform Riemann sums hold on every bounded sup-norm ball.**  False:
   equicontinuity is needed, so the proof uses compact sets supplied by
   Gaussian tightness.
4. **Weak convergence of bounded tests passes the unbounded source
   exponential.**  False: quartic uniform integrability and the normalizer
   lower bound are required.
5. **The exact interpolation identity proves the DLR equation.**  False: it
   identifies a local source functional only; DLR closure is the KKK Feller
   and weighted-compactness argument.
6. **The KKK `W_t` compactness theorem proves Q3LOCK FSS.**  False: FSS is a
   finite-grid spatial reflection argument and its loop limit is Q3LOCK-local.

## 8. Remaining independent-audit obligations

* Match the final bibliography version and exact equation/proposition numbers
  in the KKK source.
* Reproduce the grid covariance/tightness proof and verify that the chosen
  interpolation topology is the one used by every finite-volume test.
* Check the compact-set Riemann-sum argument for the full Q3LOCK action,
  including the periodic spatial edge list and the `3c` onsite allocation.
* Verify the source-uniform quartic and normalizer estimates needed for
  unbounded exponential and clipped coordinate observables.
* Keep the finite-volume grid limit, the KKK `W_t` spatial accumulation and
  the source-tangent limit in the declared order during the independent proof
  audit.

P-04 and P-09 remain **PROOF TEXT AND EXTERNAL AUDIT REQUIRED**.  No claim,
manuscript release, or PDF is created by this crosswalk.

## 9. Nonclaims and publication boundary

This note does not prove a strict source cusp, an infrared zero-mode lower
bound, DLR multiplicity, extremality, purity, clustering, a common real-time
dynamics, a KMS state, a ground-state phase, a mass gap, a continuum limit,
physical vacuum, cosmological interpretation, or Sector-A/Pre-A closure.
PDF compilation, rendering and visual review remain reserved for the final
content-frozen stage after all mathematical and independent audits pass.
