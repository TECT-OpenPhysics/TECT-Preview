# Q3LOCK KP source-window uniform-moment and tempered-tightness audit

**Status:** T0 independent source-window estimate; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kozitsky--Pasurek, arXiv:math-ph/0609045v1, equations
(2.5)--(2.6), (2.27), (2.39)--(2.41), (2.47)--(2.49), Lemmas 2.6, 2.8 and
2.11, Lemmas 4.1--4.5, Corollary 5.1, and Theorems 3.1--3.3  
**PDF:** deferred until content freeze, independent mathematical review, clean
replay and final release review

## 1. Question and boundary

The KP vector theorem-domain crosswalk shows that every fixed-source Q3LOCK
model satisfies the hypotheses of the general Euclidean-Gibbs construction.
The source-tangent argument needs the stronger statement that the estimates
can be chosen uniformly for `h` in a compact interval, so that DLR states at
`h_n -> 0` have a common tempered compactness bound.  This note derives that
uniformity directly from the proof of KP Lemma 4.1 and Theorem 3.2.

The result is a **T0 source-window estimate**, conditional on the hash-frozen
KP theorem and the Q3LOCK quartic/form-domain audit.  It does not by itself
prove the source-to-zero DLR identity, a pressure cusp, phase coexistence or a
claim card.  No manuscript or PDF is created.

## 2. Uniform Q3LOCK potential bounds on a source window

Fix `a>0`, `beta>0`, and a compact energy-source interval `|h|<=h_0`.  The
Q3LOCK residual one-site potential is

```text
V_(h,a)(q) = ((r+6c-a)/2)*|q|^2
             + (g/4)*sum_e q_e^4
             + W_Q3(q) - h*(u,q),
```

with `q in R^8`, `u=(1,...,1)/sqrt(8)`, and `W_Q3>=0`.  The explicit
quartic audit supplies constants independent of `h` in this interval,

```text
V_(h,a)(q) >= A_4*|q|^4 - C_0,
A_4=g/128>0,
```

and the continuous upper function

```text
V_(h,a)(q) <= V^+_(a,h_0)(q)
 = (g/4+3*lambda)*sum_e q_e^4
   + R_a*|q|^2 + h_0*|q|.
```

Both bounds are uniform in `h`, and the upper function vanishes at the
origin.  The spatial interaction remains the fixed finite-range matrix with
`Jhat_0=6c`; no source-dependent interaction constant is introduced.

## 3. Uniformity of the KP one-site kernel estimate

KP Lemma 4.1 bounds the one-site conditional kernel by a constant built from
the Gaussian reference, the lower/upper bounds in (2.5), and

```text
Y_(h,a)(vartheta)
 = integral exp(-Jhat_0/(2*vartheta)*|omega|^2_L2
                - integral_0^beta V_(h,a)(omega(tau))dtau)
             chi(domega).
```

For every fixed positive `vartheta`, the window upper bound gives the uniform
positive denominator estimate

```text
Y_(h,a)(vartheta) >= Y^-_(a,h_0,vartheta) > 0,
```

where `Y^-` is the same Gaussian integral with `V^+_(a,h_0)` in place of
`V_(h,a)`.  Positivity is strict because the integrand is positive on the
periodic OU loop space; finiteness follows from the Gaussian reference and the
polynomial upper function.

In the numerator of KP's equation (4.3), the uniform lower bound gives

```text
exp(-integral V_(h,a)(omega))
 <= exp(beta*C_0 - A_4*integral |omega(tau)|^4dtau).
```

Together with KP Proposition 2.2 and the fixed positive parameters `kappa` and
`vartheta`, this is an integrable majorant independent of `h`.  Therefore the
constant in KP Lemma 4.1 can be replaced by one number
`C_4.1(a,h_0,beta,kappa,vartheta)` valid simultaneously for every
`|h|<=h_0`, every site and every tempered boundary configuration.  The
dependence on the boundary configuration remains exactly the displayed KP
term

```text
exp(vartheta*sum_z |J_(y,z)|*|xi_z|^2_L2).
```

No differentiability of `V_(h,a)` is used in this step.

## 4. Uniform KP exponential moments for all source DLR states

Choose an exponential weight `w_alpha(y,z)=exp(-alpha*|y-z|)` with
`alpha>0`.  Finite range gives finite `Jhat_alpha=6c*exp(alpha)`.  For any
fixed `kappa>0`, choose `vartheta>0` small enough that

```text
vartheta*Jhat_alpha < kappa.
```

The proof of KP Lemma 4.3 then uses only `C_4.1`, `Jhat_alpha`, and the weight
sum.  Since all three are source-window uniform, its bound
`C_4.7(alpha)` is also uniform in `h`.  Integrating the resulting estimate
through the DLR equation exactly as in the proof of KP Theorem 3.2 gives one
constant `C_3.1(h_0,alpha,kappa,sigma)` such that, for every
`|h|<=h_0` and every `mu in G_t(h)`,

```text
integral exp(lambda_sigma*|omega_y|^2_Csigma
             + kappa*|omega_y|^2_L2) mu(domega)
 <= C_3.1(h_0,alpha,kappa,sigma),
```

uniformly in the site `y`.  Here `lambda_sigma` is the same OU/Fernique
constant as in KP (2.27); it depends on the reference oscillator and `sigma`,
not on the source.  The proof uses no KP scalar order or phase theorem.

## 5. A common weighted-tempered tightness bound

The preceding exponential estimate implies the quadratic bound

```text
integral |omega_y|^2_Csigma mu(domega)
 <= C_3.1/lambda_sigma.
```

Consequently, for every fixed `alpha>0`,

```text
integral ||omega||^2_(alpha,sigma) mu(domega)
 <= (C_3.1/lambda_sigma)
    *sum_y w_alpha(y_0,y),
```

with the right side independent of `h` and of `mu in G_t(h)`.  The sum is
finite for the exponential weights on `Z^3`.

Let `alpha<alpha'`.  KP's compact embedding
`Omega_(alpha,sigma) -> Omega_(alpha')` and Markov's inequality therefore give
uniform tightness of the union

```text
{ G_t(h) : |h|<=h_0 }
```

in each `W_(alpha')` topology.  Taking a countable decreasing family of
weights and assigning tail budgets summing to a prescribed epsilon yields a
single projective-limit compact set in `Omega_t` outside of which every source
DLR state has probability at most epsilon.  Thus the source-varying family
needed for `h_n -> 0` has a common `W_t` tightness bound; this is stronger than
the pointwise compactness in KP Theorem 3.1.

This argument does not identify the compact set with a finite-volume family of
periodic measures.  It applies after the fixed-source DLR accumulation has
been taken, exactly as required by the two-stage source-tangent order.

## 6. Consequence for the source-to-zero specification step

For a finite region `Delta`, the KP Feller kernel is continuous in the
boundary configuration by Lemma 2.8.  The source-window Feller audit supplies
the additional uniform-on-compact estimate

```text
sup_(xi in K)
 |pi_Delta^h(f|xi)-pi_Delta^0(f|xi)| -> 0
```

for bounded continuous local `f`, using the same quartic constants and a
compact boundary set `K`.  The common `W_t` tightness proved in Section 5
provides the required choice of `K` for any sequence `mu_n in G_t(h_n)` with
`h_n -> 0`.  Hence, **conditional on the source-window Feller estimate and
the KP specification identity**, the usual compact-boundary split passes the
DLR equation from `mu_n` at `h_n` to a zero-source weak limit.

This is a composition interface, not a new infinite-volume theorem: the
monotone-class extension from bounded continuous local functions and the exact
periodic-volume selection remain explicit review obligations.

## 7. Scope firewall and remaining checks

The uniform estimate uses only the general-vector KP construction.  KP's
`nu=1` ferroelectric FKG, pressure equality and scalar phase theorems are not
used.  The estimate also does not supply the FSS infrared cap, the KKK
endpoint inequality, or a positive pressure slope.

An external reviewer must still check the source-window lower/upper envelopes
against the exact canonical mass convention, the compact embedding used for
the chosen weight sequence, the projective-limit tightness construction, and
the bounded-continuous-to-Borel DLR extension.  These are review gates rather
than silently assumed conclusions.

## 8. Adversarial checks

1. **KP Theorem 3.1's fixed-source compactness automatically gives a common
   source-window compact set.**  Rejected: the common estimate is derived from
   the proof of KP Theorem 3.2 and the source-uniform Q3LOCK envelopes.
2. **The source term changes `Jhat_0` or the weighted interaction norm.**
   Rejected: it is a one-site linear term; the finite-range pair matrix is
   unchanged.
3. **A lower quartic bound alone gives a positive KP denominator.**  Rejected:
   the denominator uses the upper envelope and its positive Gaussian integral;
   both sides are needed.
4. **A per-site exponential moment is already a `W_t` compactness proof.**
   Rejected: one must sum with a summable weight and use KP's compact embedding
   for a weaker target topology, then diagonalize over the projective limit.
5. **The uniform source estimate proves the cusp or phase transition.**
   Rejected: it only enables the source-tangent DLR composition; FKG, FSS,
   zero-mode and KKK pressure steps remain separate.
6. **The scalar KP phase theorem can be invoked after this estimate.**
   Rejected: the field remains eight-component and nonradial.
7. **The uniform estimate authorizes manuscript or PDF generation.** Rejected:
   claim registration, external referee review, content freeze, clean replay,
   release review and PDF generation remain deferred.

## 9. Disposition

The source-window constants and the common weighted-tempered tightness input
are now explicit at T0, conditional on the hash-frozen KP proof and the exact
Q3LOCK quartic/form-domain bounds.  This advances the source-tangent gate but
does not promote a theorem or claim.  The next gate is independent acceptance
of this uniformity, the compact-boundary specification passage, and the full
pressure-to-cusp composition.

## 10. Explicit nonclaims

No strict source cusp, positive-lambda phase theorem, DLR multiplicity,
extremality, purity, clustering, common real-time dynamics, KMS state,
ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, C6/CP1/Sector-A/Pre-A closure, or Yang--Mills
conclusion is asserted.  No claim card, P2 manuscript, submission, upload,
tag, release or PDF is created.
