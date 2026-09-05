# Q3LOCK KP source-window projective tightness diagonal audit

**Status:** T0 internal independent audit; source-to-zero DLR passage remains
conditional  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Companion inputs:** `q3lock-kp-vector-hypothesis-crosswalk-independent-audit-260905.md`,
`q3lock-kp-source-window-uniform-moment-audit-260905.md`, and
`q3lock-source-zero-dlr-kernel-determining-class-audit-260905.md`  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Question and strict boundary

The source-window audit derives a common quadratic Holder-moment bound for
all source DLR states with `|h| <= h_0`.  The source-to-zero argument also
needs an actual compactness statement in the projective-limit topology
`W_t`; relative compactness in one fixed `W_alpha` is not by itself enough.
This note makes the diagonal construction explicit and records exactly what
it permits.

The conclusion is a conditional extraction lemma: if the source-uniform
`Omega_(alpha,sigma)` estimates supplied by the preceding audit are accepted,
then every sequence of source DLR states with `h_n -> 0` has a `W_t`-
convergent subsequence.  Combined with the compact-boundary kernel estimate,
the limit satisfies the zero-source DLR equation.  No pressure cusp, phase
theorem, or claim promotion is made.

## 2. KP scales and the uniform estimates to be used

Use the exponential KP weights

```text
w_alpha(y,z) = exp(-alpha*|y-z|),       alpha in I=(0,alpha_max),
```

and fix `sigma in (0,1/2)`.  The KP stronger space has norm

```text
||omega||_(alpha,sigma)^2
  = sum_y |omega_y|_(C_beta^sigma)^2*w_alpha(0,y).
```

For `alpha < alpha'`, KP's compact embedding is
`Omega_(alpha,sigma) -> Omega_(alpha')`.  The source-window moment audit
supplies, conditionally on the exact Q3LOCK/KP hypotheses, constants

```text
M_k = sup_{|h|<=h_0} sup_{mu in G_t(h)}
      integral ||omega||_(alpha_k,sigma)^2 mu(domega) < infinity
```

for every member of one strictly decreasing sequence
`alpha_1 > alpha_2 > ... -> 0` contained in `I`.  The constants are allowed
to depend on `alpha_k`, `sigma`, and the model parameters, but not on `h`,
the selected DLR state, or the sequence index used in the source tangent.
This is the only source-uniform input used below.

The choice `alpha_k -> 0` is cofinal for the projective topology: for every
`alpha in I`, some `alpha_k < alpha`, and convergence or boundedness in the
stronger `Omega_(alpha_k,sigma)` scale controls the weaker `Omega_alpha`
scale.  No assertion is made for the endpoint `alpha=0`, which is not a KP
weight in `I`.

## 3. Explicit diagonal compact set

Let `epsilon_k > 0` be summable with
`sum_k epsilon_k <= epsilon`, where `epsilon` is an arbitrary target error.
Choose radii `R_k` so that

```text
M_k/R_k^2 <= epsilon_k.
```

Define the projective-limit set

```text
K(epsilon) = Omega_t cap intersection_k
             {omega : ||omega||_(alpha_k,sigma) <= R_k}.
```

The Markov inequality and the common moment bound give, simultaneously for
all `|h| <= h_0` and all `mu in G_t(h)`,

```text
mu(K(epsilon)^c)
 <= sum_k mu(||omega||_(alpha_k,sigma) > R_k)
 <= sum_k M_k/R_k^2
 <= epsilon.                                      (3.1)
```

The set in (3.1) is compact in `Omega_t` under the same compact-embedding
input used by KP.  To see the diagonal step, take any sequence in
`K(epsilon)`.  The bound at level `alpha_1` gives a subsequence converging in
the weaker `Omega_(alpha_2)` topology.  From that subsequence, the bound at
level `alpha_2` gives a further subsequence converging in
`Omega_(alpha_3)`, and so on.  The diagonal subsequence converges in every
`Omega_(alpha_j)` and in the local `C_beta` coordinates.  The lower
semicontinuity of the weighted Holder norms keeps the bounds `R_j` in the
limit, while cofinality of `alpha_j -> 0` places the limit in `Omega_t`.
The projective-limit metric then gives convergence in `Omega_t`.

This is the missing distinction between (i) a separate compact set for each
`W_alpha` and (ii) one compact set carrying all projective coordinates.  The
construction uses no finite-volume periodic state and no source monotonicity.

## 4. Source-varying DLR extraction

Let `h_n -> 0` with `|h_n| <= h_0`, and choose
`mu_n in G_t(h_n)`.  Equation (3.1) makes the family `{mu_n}` tight in the
Polish space `Omega_t`.  Prokhorov's theorem therefore gives a subsequence,
still denoted `mu_n`, and a probability measure `mu in P(Omega_t)` such that

```text
mu_n ==> mu             in W_t.                     (4.1)
```

For a finite region `Delta`, the preceding source-zero kernel audit gives,
for every `f in C_b(Omega_alpha)`,

```text
sup_{xi in K'}
 |pi_Delta^(h_n)(f|xi) - pi_Delta^0(f|xi)| -> 0      (4.2)
```

on each compact boundary set `K'` in a suitable `Omega_alpha` topology.
Choose `K'` from the tightness construction above and split each DLR
integral into `K'` and its complement.  The complement is uniformly small by
(3.1), while (4.2) controls the compact part.  KP Lemma 2.8 gives continuity
of `xi -> pi_Delta^0(f|xi)` in the topology used for the weak convergence.
Consequently the fixed-source DLR identities pass to the limit in (4.1):

```text
integral f(omega) mu(domega)
 = integral pi_Delta^0(f|omega) mu(domega).
```

KP Lemma 2.11 then supplies the measure-determining `C_b(Omega_alpha)`
class and identifies this identity with the full Borel DLR equation.  The
argument is a two-stage limit: first select a `W_t` subsequence using the
common source-window estimates, then send `h_n` to zero in the local kernel.
It does not exchange a source limit with the spatial pressure limit.

## 5. What this audit advances

The preceding source-window note stated a projective-limit diagonal only in
outline.  Equations (3.1) and (4.1) make the required extraction explicit:

* source-uniform `Omega_(alpha,sigma)` moments produce one compact
  `Omega_t` set with a prescribed tail budget;
* the source-varying family of tempered DLR states is `W_t`-tight;
* a source sequence `h_n -> 0` can be extracted in the topology required by
  the KP specification; and
* the compact-boundary kernel estimate and KP determining-class lemma can be
  applied after, and only after, that extraction.

This repairs a topology/quantifier seam in the source-tangent proof text.  It
does not make the moment constants unconditional: acceptance of the exact
Q3LOCK quartic bounds, the KP Holder estimate, the compact embedding, and the
source-continuity estimate remains an independent review obligation.

## 6. Adversarial checks

| Objection | Disposition |
|---|---|
| Relative compactness in one `W_alpha` automatically gives `W_t` tightness | **UPHELD AS FALSE:** the projective topology needs a cofinal diagonal compact set. |
| A separate compact set may be chosen after the source sequence is known | **UPHELD AS FALSE:** the radii and tail budgets are fixed uniformly over the whole source window. |
| Bounds only in `Omega_alpha` suffice for the compact embedding | **UPHELD AS FALSE:** the stronger Holder scale `Omega_(alpha,sigma)` is the compactness input. |
| The sequence `alpha_k -> 0` misses other KP weights | **DISMISSED:** cofinality and the compact embeddings control every `alpha in I`. |
| Pointwise Feller continuity at `h=0` passes the DLR identity without a tightness split | **UPHELD AS FALSE:** (3.1), the compact-boundary estimate, and the complement bound are all required. |
| This extraction proves a cusp or two distinct phases | **UPHELD AS FALSE:** the pressure slope, FKG, FSS, zero-mode and parity inputs remain separate. |
| The diagonal argument creates a manuscript PDF | **UPHELD AS FALSE:** claim registration, content freeze, clean replay, release and final PDF review remain ahead. |

## 7. Disposition and next gate

**Advanced at T0:** the source-window-to-`W_t` quantifier and topology seam is
made explicit by a uniform Markov tail budget and a cofinal compact-embedding
diagonal.  Conditional on the preceding moment estimate and KP hypotheses,
this supplies the subsequence needed by the EXP-001577 source-to-zero DLR
bridge.

**Still open:** independent acceptance of the common source-window constants,
the exact `Omega_(alpha,sigma)` compactness/lower-semicontinuity step, the
compact-boundary kernel estimate, and the pressure-to-tangent composition;
P-06, P-09, operator, KKK, claim, external-referee, content-freeze, release,
and PDF gates remain open.

## 8. Explicit nonclaims

No strict source cusp, positive zero-mode lower bound, positive-lambda phase
theorem, DLR multiplicity, extremality, purity, clustering, common real-time
dynamics, KMS state, ground-state phase, spectral gap, continuum limit,
physical vacuum, cosmological interpretation, C6, CP1, Sector A, Pre-A, or
Yang--Mills conclusion is asserted.  No claim card, manuscript, submission,
upload, release, tag, or PDF is created.
