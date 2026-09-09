# Q3LOCK DLR source-window topology and limit-order audit

**Status:** T0 internal audit; no claim-card promotion  
**Date:** 2026-09-08  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Primary source:** Kozitsky--Pasurek, arXiv:math-ph/0609045v1, Assumption
(A), Proposition 2.7, Lemma 2.8, Lemma 2.11, Lemma 4.1, Theorems 3.1--3.2,
and equations (2.47)--(2.67), (4.1)--(4.8)  
**PDF:** deferred until the mathematical content is frozen, independently
reviewed, replayed, and released

## 1. Question and strict boundary

Does the manuscript's source-window DLR construction use the correct KP
topology, source normalization, quantifiers, and limit order?  The audit
rechecks Sections 8--9 of `manuscript.tex` against the primary KP statements
and the existing source-window, compactness, and determining-class notes.

This is a bounded internal proof-text audit.  It does not certify KP's
applicability, the source-uniform constants, the pressure cusp, phase
coexistence, or any claim card.  It does not replace a signed mathematical
review and it creates no PDF.

## 2. Source and topology crosswalk

The manuscript uses the energy source `-h*(u,q)` and places the full imaginary
time integral in

```text
X_Delta = sum_(y in Delta) integral_0^beta (u,omega_y(tau)) d tau.
```

Thus the local factor is `exp(h*X_Delta)`, not `exp(beta*h*X_Delta)`.  The
finite-volume pressure dictionary in the manuscript uses the same convention,
so the normalized tangent identity has no extra factor of beta.

The declared `d_t` metric uses a countable cofinal sequence
`alpha_k=1/k`, all weighted `L2_beta` norms, and all local loop sup norms.
This is a countable presentation of the KP projective-limit topology.  The
manuscript's direct Feller argument is made on `Omega_t`; it is not a claim
that KP Lemma 2.11 alone supplies a source-varying limit.

The exact KP roles are separated as follows:

* Assumption (A) and finite-range weights provide fixed-source specification
  control and the general-vector DLR existence/compactness input.
* KP Lemma 4.1 and Theorem 3.2 provide the form of the one-site exponential
  estimate; the Q3LOCK source-window constants are re-derived locally.
* KP Lemma 2.8 and the manuscript's compact-boundary estimate control the
  source-dependent local kernel.
* KP Lemma 2.11 is used only as a determining-class/topology comparator; the
  source-to-zero DLR passage is the manuscript's own two-stage argument.

## 3. Quantifier and formula audit

### 3.1 Finite source-window estimate

The Q3LOCK lower envelope `A*|q|^4-C_0` and upper envelope `V^+` are
uniform for `|h|<=h_0`.  The nearest-neighbour row sum is `J_0=6c`; the
locking polynomial remains onsite and is not inserted into the spatial pair
matrix.  The one-site normalizer lower bound is written before the Holder
recursion.  With `theta=kappa/(2*J_0)`, the Holder exponent is one half and
the finite positive moment closes as `M<=exp(2*C_1)`.

The audit therefore found no sign, source-factor, or circular-division defect
in the displayed finite formulas.  Finiteness of the finite product integral
and the exact OU/Fernique constants remain external-review obligations.

### 3.2 Projective compactness

The compact set is defined by simultaneous weighted `C^sigma` bounds at every
`alpha_k`.  The tail estimate uses the stronger, slower-decaying weight at
`alpha_(k+1)<alpha_k`:

```text
sum_(|y|>R) exp(-alpha_k*|y|)*||omega_y||_L2^2
 <= beta*exp(-(alpha_k-alpha_(k+1))*R)*R_(k+1)^2.
```

This is the required direction.  A separate fixed `Omega_alpha` compact set
would not by itself give `W_t` tightness.  The diagonal extraction and
lower-semicontinuity steps are stated explicitly, but the exact equivalence
between this metric presentation and the KP projective topology remains a
review item.

### 3.3 Compact-boundary kernel passage

For a compact boundary set, finite-range boundary terms are uniformly bounded
and the quartic envelope gives a common coercive majorant.  A bounded Gaussian
interior event gives a positive normalizer lower bound before quotienting.
The mean-value estimate in the source factor then gives a uniform-on-compact
Lipschitz bound for `pi_Delta^h`.

The direct Feller proof for bounded continuous functions on `Omega_t` is
logically stronger than invoking pointwise KP Feller continuity at one fixed
source.  It is the needed input for the source-varying sequence; it is not
silently identified with a theorem about all source-dependent DLR families.

### 3.4 Limit order and determining class

The manuscript keeps the following order:

1. Fix `h` and take a periodic spatial-volume DLR accumulation point.
2. Identify its local source tangent using pressure convergence and clipping.
3. Choose differentiability points `h_j` decreasing to zero.
4. Extract a `W_t` subsequence using the common source-window compact set.
5. Remove the source difference on a compact boundary set, then pass the
   zero-source Feller kernel through weak convergence.
6. Use the common moment bound again to pass the unbounded local observable.

The equality for all bounded continuous functions on `Omega_t` determines the
probability measures on that Polish space; the product Borel sigma-field is
the declared trace.  Hence the resulting identity is a full zero-source DLR
identity once the topology and support inputs are accepted.  No total
variation convergence or arbitrary simultaneous `h=h(L)` limit is used.

## 4. Adversarial checks

| Objection | Disposition | Boundary |
|---|---|---|
| The local source is `beta*h` because the loop has length `beta` | **DISMISSED** | `X_Delta` already contains the time integral; the pressure dictionary agrees. |
| Finite-source Holder closure may divide by an unknown infinite moment | **DISMISSED** | The manuscript proves finite `M` before applying the recursion. |
| A fixed `Omega_alpha` compact set is enough for `W_t` tightness | **UPHELD AS FALSE** | The cofinal diagonal compact set is required. |
| Pointwise Feller continuity passes a source-varying DLR sequence | **UPHELD AS FALSE** | Uniform-on-compact source continuity plus a tightness split is required. |
| KP Lemma 2.11 by itself proves the source-to-zero limit | **UPHELD AS FALSE** | It is a fixed-specification accumulation/determining-class result; the source passage is local Q3LOCK work. |
| Weak convergence alone passes the unbounded tangent observable | **UPHELD AS FALSE** | The two clipping/UI estimates are required. |
| This audit certifies a cusp or two DLR phases | **UPHELD AS FALSE** | Pressure slope, FKG, infrared, collective, and parity witness gates remain open. |

## 5. Disposition and next gate

**No new local algebraic or limit-order defect was found in the bounded audit.**
The DLR source-window text is internally consistent at T0, with the important
boundary that the uniform constants, exact KP hypothesis map, projective
topology equivalence, and bounded-continuous-to-Borel passage still require
location-specific independent acceptance.

The next gate is a signed specialist review of the complete DLR packet,
including the finite form/trace interface and the source-window constants.
Only after all proof-audit rows are independently disposed, the literature
crosswalk is frozen, and the clean replay/release checks pass may the paper
enter content freeze and the final PDF stage.

## 6. Explicit nonclaims

No strict source cusp, positive-lambda phase theorem, DLR multiplicity,
extremality, purity, clustering, KMS state, ground-state phase, spectral gap,
continuum limit, physical vacuum, cosmological conclusion, C6, CP1, Sector A,
Pre-A, or Yang--Mills conclusion is asserted.  No theorem tier, claim card,
submission, upload, release, or PDF is created.
