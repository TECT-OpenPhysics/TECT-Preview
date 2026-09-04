# Q3LOCK continuous-loop weak-limit versus total-variation audit

**Status:** T0 proof-text correction; no claim-card promotion; PDF deferred  
**Scope:** P-06 finite time-grid to continuous-loop passage in the EXP-000782
authority chain  
**Authority boundary:** This note audits the wording and limit mechanism of
EXP-000782. It does not add a phase theorem, replace the source chain, or close
the independent-review gate.

## 1. Audit question

The EXP-000782 certificate states in its continuous-loop FKG section that the
time-sliced laws converge in total variation to the exact Feynman--Kac loop
law. The current P-06 companion notes use the weaker and appropriate language
of tightness, weak convergence, compact residual convergence, and uniform
integrability. These two statements are not equivalent. The audit asks which
limit is mathematically possible for the actual polygonal interpolation and
which replacement is admissible in the proof.

The model, source convention, harmonic split, and quartic bounds are unchanged.
The only issue here is the topology and the mode of convergence in the time
mesh `N` at fixed spatial volume, inverse temperature, and compact source set.

## 2. The two measures have incompatible supports

Let `C_per` be the periodic continuous-loop space with the sup norm. For a
time mesh with `N` intervals, let `I_N` be the order-preserving periodic
polygonal interpolation of the `N` oscillator coordinates, and write

```
nu_N = law of I_N(s_0,...,s_{N-1})
```

for the interpolated grid law. Its support is contained in the finite
dimensional closed set `PL_N` of periodic piecewise-linear loops with the
prescribed mesh breakpoints.

The positive harmonic reference used in the P-06 split is a nondegenerate
periodic Ornstein--Uhlenbeck Gaussian loop law `gamma_a`. On every mesh
interval, conditional on its two endpoint values, the OU bridge has a
nonzero continuous Gaussian fluctuation. The event that this bridge is exactly
the affine segment joining its endpoints has probability zero. Consequently,

```
gamma_a(PL_N) = 0                                           (2.1)
```

for every finite `N`. The exact interacting finite-volume Feynman--Kac loop
law has density proportional to the positive residual weight with respect to
`gamma_a`. The quartic lower bound makes this density finite and integrable,
and it is strictly positive `gamma_a`-almost everywhere. Hence the same
support-null statement holds for the exact loop law `mu_h`:

```
mu_h(PL_N) = 0.                                             (2.2)
```

This is a support statement, not a numerical approximation claim. It is
unchanged by the nonradial Q3 term or by a compact source interval.

## 3. Total variation convergence is impossible

Because `nu_N(PL_N)=1` and `mu_h(PL_N)=0`, the total variation distance is
maximal for every finite mesh:

```
sup_A |nu_N(A)-mu_h(A)| >= |nu_N(PL_N)-mu_h(PL_N)| = 1.   (3.1)
```

Under the convention `||nu-mu||_TV = (1/2)||dnu-dmu||_1`, the corresponding
distance is also one. Therefore the sentence “dominated convergence gives
total variation convergence to the exact Feynman--Kac loop law” in the
EXP-000782 proof text is false as written. It must not be used to pass FKG or
source derivatives.

This does not refute the desired loop limit. It identifies the correct mode:
polygonal laws can converge weakly in `C_per` even though they remain singular
at every finite `N`.

## 4. Correct weak-limit route

The replacement proof has four separate ingredients.

1. **Reference tightness and weak convergence.** The mesh-uniform Gaussian
   increment estimate gives tightness of `gamma_{a,N}` in the periodic sup-norm
   topology. Fourier covariance convergence identifies every subsequential
   limit with `gamma_a`; therefore `gamma_{a,N}` converges weakly, not in total
   variation.

2. **Residual convergence on compact loop sets.** On a common compact,
   equicontinuous set of loops, the spatial and local time Riemann sums of the
   residual Q3LOCK action converge uniformly to the Feynman--Kac action. The
   interpolation map is order-preserving, so finite-grid increasing
   functionals remain increasing after pullback.

3. **Normalization and bounded tests.** The Jensen lower bound for the
   residual normalizer and the quartic upper envelope give a positive,
   mesh-uniform denominator and a uniform tail bound. Weak convergence on
   compact sets plus this envelope yields convergence of bounded continuous
   loop observables under the weighted laws. No total-variation assertion is
   needed.

4. **Unbounded source witnesses.** For `X_N(a)` and `X_N(a)^2`, first truncate
   the source exponential and the polynomial observable. The quartic
   Holder--Young estimate and the mesh-uniform normalizer bound give uniform
   integrability of the discarded tails. Remove the truncation after taking the
   weak limit. This is the only legitimate passage for the first and second
   source derivatives.

With these replacements, the finite-grid association inequality passes to
bounded continuous increasing loop functionals by weak convergence. Polynomial
coordinates are obtained by the same clipping and uniform-integrability
argument. The statement is fixed spatial volume; the later spatial KKK
tempered compactness and source-tangent limits remain separate.

## 5. Exact manuscript replacement

Replace the EXP-000782 sentence

> “Dominated convergence gives total variation convergence to the exact
> Feynman--Kac loop law.”

with:

> “The interpolated Gaussian reference laws are tight in the periodic
> sup-norm topology and converge weakly to the nondegenerate periodic
> Ornstein--Uhlenbeck loop law. On compact equicontinuous sets the residual
> Riemann sums converge uniformly; the quartic envelope and the
> mesh-uniform Jensen denominator give the required weighted weak limit. For
> source exponentials and their first two polynomial witnesses, the passage is
> made after truncation and uniform-integrability control. Total variation
> convergence is neither asserted nor needed.”

The finite-grid MTP2/association argument is then transferred using bounded
continuous increasing tests and the order-preserving interpolation. This
replacement is consistent with the P-06 Gaussian tightness, reference-
convergence, and source-UI audits and does not alter any source normalization.

## 6. Adversarial checks

| objection | disposition | reason |
|---|---|---|
| A dominated density limit automatically gives TV convergence | **UPHELD AS FALSE** | The interpolated and exact loop laws are supported on mutually singular sets at every finite mesh. |
| Weak convergence alone passes `exp(t X_N)` or `X_N^2 exp(t X_N)` | **UPHELD AS FALSE** | Truncation and a mesh-uniform quartic UI estimate are required. |
| Replacing TV by weak convergence loses finite-grid FKG | **DISMISSED WITH CONDITIONS** | Pull back bounded continuous increasing tests through the order-preserving interpolation and use weak convergence. |
| The support argument depends on radial Q3 symmetry | **DISMISSED** | It uses only the nondegenerate harmonic reference and positivity of the residual density. |
| The corrected route already proves the spatial thermodynamic phase | **UPHELD AS FALSE** | All statements here are fixed spatial volume and finite source; DLR, cusp, and multiplicity remain downstream. |

## 7. Disposition and boundary

The total-variation phrase is a genuine proof-text error and is retired. The
weak-limit/UI replacement is an explicit insertion, not a new theorem claim.
P-06 remains **T0 proof-text corrected; independent mathematical review
required** because the reference covariance, compact residual convergence, and
uniform-integrability constants still need a clean, line-by-line replay.

This audit proves no strict source cusp, positive zero-mode density, DLR
multiplicity, real-time dynamics, KMS state, ground-state gap, continuum limit,
physical-vacuum statement, or cosmological conclusion. PDF and manuscript
publication remain deferred until content freeze and external review.

## 8. Evidence and reproduction

The audited sentence is in the EXP-000782 certificate pinned by the R-497
manifest (`b6487a9381bef20cdf1a9abc4dfdec9aa40f69b0b73697595c263ffe574a4d89`).
The corrected route is cross-referenced to the fixed-volume P-06 audits
`EXP-001530` and `EXP-001531`, and to the P-06/P-09 round-2 audit
`EXP-001516`. These references are proof-text authorities only; no claim-card
or publication artifact is created by this note.
