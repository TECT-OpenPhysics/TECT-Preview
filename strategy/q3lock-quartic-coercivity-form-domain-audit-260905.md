# Q3LOCK quartic coercivity and finite-volume form-domain audit

**Status:** T0 operator/form-domain audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until all content and independent-review gates close

## 1. Purpose and boundary

This note supplies explicit source-uniform polynomial bounds for the local
Q3LOCK potential after the positive harmonic split used in the KP and
finite-grid arguments.  It also records the corresponding finite-volume
quadratic-form domain.  The calculation removes an implicit ``quartic
coercivity'' phrase from the proof text, but it is still a T0 audit: the exact
KP bibliography version, the finite-volume boundary convention and the
operator trace-class passage require independent sign-off.

No infrared estimate, pressure cusp, DLR multiplicity, claim-tier change,
manuscript release or PDF is produced here.

## 2. Local potential and graph inequalities

For `q in R^8`, let

```text
W_Q3(q) = (lambda/4) sum_{ {i,j} in E(Q3) }
             (q_i-q_j)^2*(q_i^2+q_j^2),
```

where `Q3` has twelve edges and degree three at every vertex.  After the
periodic spatial difference is split into its positive onsite part `3c|q|^2`
and its ordered pair term, and after subtracting the auxiliary harmonic
rigidity `a|q|^2/2`, the one-site residual at source `h` is

```text
V_(h,a)(q) = ((r+6c-a)/2)*|q|^2
             + (g/4)*sum_i q_i^4
             + W_Q3(q) - h*(u,q),
u=(1,...,1)/sqrt(8).
```

The formula is for the declared periodic convention.  In an open box the
coefficient `3c` is replaced sitewise by `(c/2)d_R(y)` and the same estimates
hold with the maximum degree bound; the two conventions are not mixed.

The following elementary inequalities are exact:

```text
sum_i q_i^4 >= |q|^4/8,
W_Q3(q) >= 0,
(q_i-q_j)^2*(q_i^2+q_j^2) <= 4*(q_i^4+q_j^4).
```

The last inequality and degree three imply

```text
W_Q3(q) <= 3*lambda*sum_i q_i^4.                    (2.1)
```

## 3. Explicit lower bound on compact source intervals

Set

```text
b_a = abs(r+6c-a)/2,
t = |q|,
h_0 >= 0.
```

For `|h|<=h_0`, the Cauchy--Schwarz inequality and the first two graph
inequalities give

```text
V_(h,a)(q) >= (g/32)*t^4 - b_a*t^2 - h_0*t.        (3.1)
```

Two scalar Young inequalities with their constants displayed are

```text
b_a*t^2 <= (g/64)*t^4 + 16*b_a^2/g,

h_0*t <= (g/128)*t^4
          + (3/4)*h_0^(4/3)*(32/g)^(1/3).           (3.2)
```

Combining (3.1)--(3.2) yields the uniform lower bound

```text
V_(h,a)(q) >= A_4*|q|^4 - C_(a,h_0),
A_4 = g/128,
C_(a,h_0) = 16*b_a^2/g
             + (3/4)*h_0^(4/3)*(32/g)^(1/3).         (3.3)
```

The constant is finite for every `g>0`, every fixed `a`, and every compact
source interval.  The positive `lambda` term is not spent in the lower bound;
its only role there is to preserve nonnegativity.  Thus (3.3) remains valid
for all `lambda>=0`, while the phase argument later requires `lambda>0`.

## 4. Continuous quartic upper function

Let `R_a=abs(r+6c-a)/2`.  Using (2.1), `|(u,q)|<=|q|` and the finite-dimensional
Young inequality, one may take the continuous upper function

```text
V_(h,a)(q) <= (g/4 + 3*lambda)*sum_i q_i^4
             + R_a*|q|^2 + h_0*|q|,                (4.1)
```

for every `|h|<=h_0`.  This function is finite on compact sets and is the
upper-side input required in the KP finite-volume/Feynman--Kac construction.
No radial or `O(8)` invariance is used; the estimate only uses the finite Q3
edge list.

## 5. Finite-volume form domain

For `V` sites, define the polynomial potential

```text
U_(L,h)(q) = sum_y V_(h,a)(q_y)
             + (c/2)*sum_{<yz>} |q_y-q_z|^2,
q in R^(8V),
```

with the declared finite-volume edge list.  The spatial term is nonnegative,
so summing (3.3) gives

```text
U_(L,h)(q) >= A_4*sum_y |q_y|^4 - V*C_(a,h_0).       (5.1)
```

The finite Hamiltonian form is therefore defined on

```text
Q_(L) = H^1(R^(8V))
        cap L^2(R^(8V), (sum_y |q_y|^4)dq),          (5.2)
```

by

```text
q_L[psi] = (hbar^2/(2*chi))*integral |grad psi|^2 dq
           + integral U_(L,h)(q)*|psi(q)|^2 dq.
```

The lower bound (5.1) makes this form densely defined, closed and bounded
below after adding the finite constant `V*C_(a,h_0)`.  The associated
self-adjoint operator is the finite-volume Q3LOCK Hamiltonian used by
EXP-000780.  Since (5.1) tends to infinity along every escape direction, the
standard confining-potential theorem gives compact resolvent; KP's finite
volume result then supplies the heat-trace and Feynman--Kac conclusions under
its remaining stated hypotheses.

The form calculation does not prove a thermodynamic limit and does not
replace the operator-domain audit of the collective commutator.  In
particular, differentiating an unbounded source or removing the Falk--Bruch
cutoff still requires the common-core argument recorded in the P-07/P-08
audits.

## 6. Compatibility with the Jensen normalizer lemma

The finite-grid residual action uses the same `V_(h,a)` at each time slice.
Equation (3.3) supplies the source-uniform quartic lower coefficient `A_4`
used in the weighted-law upper bound.  The centered Gaussian moment estimate
in the Jensen normalizer audit bounds the expectation of (4.1) and of the
spatial difference term by `beta*V` times a finite constant.  Therefore the
two inputs are consistent:

```text
Z_(N,L)(h) >= exp(-beta*V*C_(L,h_0)),
exp(-S_(N,L,h))/Z_(N,L)(h)
    <= exp(beta*V*(C_(L,h_0)+C_(a,h_0))).            (6.1)
```

The constants in (6.1) may depend on fixed finite volume and the declared
source interval, but not on the time-grid size `N`.  This is precisely the
scope needed before the time-grid-to-loop limit; no spatial-volume-uniform
claim is made here.

## 7. Adversarial checks

1. **The `3c` periodic onsite term can be replaced by `3c/2`.** Rejected:
   six endpoint incidences force the `3c` coefficient; the open-box formula
   is degree dependent.
2. **The positive Q3 locking term is needed to prove coercivity.** Rejected:
   the component quartic already supplies `g|q|^4/32`; `W_Q3>=0` is retained
   but not spent in the lower bound.
3. **A source-uniform bound holds for unbounded `h`.** Not claimed:
   `C_(a,h_0)` is uniform only on a compact interval `|h|<=h_0`.
4. **Compact resolvent alone proves the infinite-volume DLR theorem.**
   Rejected: KP compactness and the DLR passage require their separate lattice,
   interaction and moment hypotheses.
5. **The form-domain estimate closes P-06/P-09.** Rejected: finite-grid FKG,
   interpolation, FSS transfer, differentiation and independent review remain
   open.

## 8. Disposition and next gate

The Q3LOCK quartic lower/upper bounds and the finite-volume form domain are
now explicit and consistent with the Jensen normalizer estimate.  The
disposition is **T0 operator/form-domain input advanced; P-04, P-06, P-09 and
P-12 remain conditional pending independent review**.

The next audit must compare the exact Hamiltonian in the content draft with
(2.1)--(5.2), verify the KP theorem version and heat-trace hypotheses, and
check that the same harmonic split is used in every source and limit passage.
Only after that review and the remaining proof gates may a claim card or
content-frozen manuscript be considered.  PDF compilation and visual review
remain final-stage actions only.

## 9. Explicit nonclaims

This note proves no phase transition, infrared lower bound, strict pressure
cusp, DLR multiplicity, extremality, purity, clustering, real-time dynamics,
KMS state, ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, C6, CP1, Sector A or Pre-A closure.  It creates
no claim card, P2 manuscript, submission, upload, tag, release or PDF.
