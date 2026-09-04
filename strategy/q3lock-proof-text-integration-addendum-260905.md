# Q3LOCK proof-text integration addendum: Jensen normalizer and coercivity insertion map

**Status:** T0 manuscript-integration audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782, with the P-06/P-09
round-2 audit and the two local analytic audits listed below  
**PDF:** deferred until mathematical content freeze, independent review,
clean replay and release review

## 1. Purpose and strict boundary

The P-06/P-09 proof text is now assembled, but its older prose still describes
the normalizer lower bound through a Gaussian sup-norm event and leaves the
quartic form-domain input implicit.  This addendum gives a manuscript-level
insertion map for the two stronger local inputs:

1. the centered positive-harmonic Gaussian Jensen estimate for the
   time-mesh normalizer; and
2. the explicit Q3LOCK quartic coercivity and finite-volume closed-form
   domain.

The map is intended to make the eventual paper internally auditable.  It does
not itself prove the imported KP or FSS theorems, does not replace the
finite-grid-to-loop and operator audits, and does not certify EXP-000782.  It
creates no claim card, P2 manuscript, submission package or PDF.

## 2. Frozen conventions that every insertion must preserve

The spatial volume is the periodic cube `Lambda_L=(Z/LZ)^3` with `V=L^3`.
The time mesh is `epsilon=beta/N`, the onsite field is `q_y in R^8`,
`u=(1,...,1)/sqrt(8)`, and `m=chi/hbar^2>0`.  The positive-direction
periodic edge multiset has `3V` undirected bonds and six endpoint incidences
per site.  Consequently

```text
c/2 * sum_<yz> |q_y-q_z|^2
  = 3c * sum_y |q_y|^2 - c * sum_<yz> (q_y,q_z).
```

The ordered KP interaction therefore uses `J_yz=c` on the six directed
nearest-neighbour incidences and has `Jhat_0=6c`.  The positive `3c` term is
assigned once to the local potential.  Open boxes are a different convention
with sitewise diagonal `(c/2)d_R(y)` and must not be silently substituted into
the periodic formula.

The auxiliary temporal harmonic split is fixed at `a>0`.  Its terms are
recombined before the exact Hamiltonian is stated, so `a` is a proof device,
not a model parameter.  The source is `-h sum_y (u,q_y)` in the Hamiltonian,
and the corresponding loop exponential has `+h X_L`.  All time-grid limits
below occur at fixed finite `Lambda_L`; only afterwards may the spatial DLR
accumulation and source-tangent limits be taken.

## 3. Insertion A: exact local potential and form-domain block

For a compact source interval `|h|<=h_0`, the residual one-site potential to
insert after the `3c` allocation and harmonic split is

```text
V_(h,a)(q) = ((r+6c-a)/2)*|q|^2
             + (g/4)*sum_i q_i^4
             + W_Q3(q) - h*(u,q),
```

where

```text
W_Q3(q) = (lambda/4) sum_{ {i,j} in E(Q3) }
             (q_i-q_j)^2*(q_i^2+q_j^2).
```

The exact graph inequalities are

```text
sum_i q_i^4 >= |q|^4/8,
W_Q3(q) >= 0,
(q_i-q_j)^2*(q_i^2+q_j^2) <= 4*(q_i^4+q_j^4).
```

Since the internal Q3 graph has degree three,
`W_Q3(q)<=3*lambda*sum_i q_i^4`.  Put
`b_a=abs(r+6c-a)/2`.  The scalar bounds

```text
b_a*|q|^2 <= (g/64)*|q|^4 + 16*b_a^2/g,
h_0*|q| <= (g/128)*|q|^4
                 + (3/4)*h_0^(4/3)*(32/g)^(1/3)
```

give the source-uniform lower estimate

```text
V_(h,a)(q) >= (g/128)*|q|^4 - C_(a,h_0),
C_(a,h_0) = 16*b_a^2/g
             + (3/4)*h_0^(4/3)*(32/g)^(1/3).
```

The matching continuous upper function may be taken as

```text
V_(h,a)(q) <= (g/4 + 3*lambda)*sum_i q_i^4
             + b_a*|q|^2 + h_0*|q|.
```

For `V=L^3` sites, the finite-volume potential

```text
U_(L,h)(q) = sum_y V_(h,a)(q_y)
             + (c/2)*sum_<yz> |q_y-q_z|^2
```

satisfies

```text
U_(L,h)(q) >= (g/128)*sum_y |q_y|^4 - V*C_(a,h_0).
```

Thus the finite Hamiltonian form is written on

```text
Q_L = H^1(R^(8V))
      cap L^2(R^(8V), (sum_y |q_y|^4)dq),
```

with the kinetic coefficient `hbar^2/(2*chi)` and potential `U_(L,h)`.
The form is densely defined, closed and lower bounded after adding the finite
constant `V*C_(a,h_0)`.  The confining lower bound is the local input for the
finite-volume compact-resolvent and heat-trace result imported from KP.  The
exact KP theorem number, bibliography version and any additional operator
hypotheses must still be written into the paper and independently checked.

## 4. Insertion B: mesh-uniform Jensen normalizer block

At fixed `Lambda_L`, use the centered product Gaussian with reference action

```text
S_G,N(x) = (1/2) sum_(y,k)
              [(m/epsilon)|x_(y,k+1)-x_(y,k)|^2
               + a*epsilon*|x_(y,k)|^2].
```

The scalar cyclic precision eigenvalues are

```text
kappa_(N,j) = 4*m/epsilon*sin^2(pi*j/N) + a*epsilon.
```

The exact csc-squared identity gives the diagonal covariance bound

```text
g_N(0) = (1/N)*sum_j kappa_(N,j)^(-1)
       <= 1/(beta*a) + beta/(12*m) =: K_(m,a,beta).
```

Consequently every Gaussian coordinate has second moment at most `K` and
fourth moment at most `3K^2`.  The Q3 edge estimate and independence across
sites then give a finite fixed-volume constant `C_(L,h_0)` such that, for
all `N>=1` and `|h|<=h_0`,

```text
(1/(beta*V))*E_gamma[S_(N,L,h)] <= C_(L,h_0),
```

where `S_(N,L,h)` is the residual local-plus-spatial action and the centered
source term has zero Gaussian expectation.  Jensen's inequality now yields

```text
Z_(N,L)(h) = E_gamma[exp(-S_(N,L,h))]
            >= exp(-beta*V*C_(L,h_0)).
```

The quartic lower bound gives the complementary pointwise estimate

```text
exp(-S_(N,L,h)) <= exp(beta*V*C_(a,h_0)),
```

after enlarging the constant if necessary.  Hence the normalized density is
uniformly bounded in the mesh at fixed volume and compact source interval.
This Jensen block supersedes the former sup-norm-event estimate as the
primary manuscript denominator proof; the event argument may remain only as a
clearly labelled backup check.

## 5. Consequences for P-06 and P-09 transcription

The insertion order is part of the proof and must remain visible:

1. establish the Gaussian covariance/tightness and interpolation lemmas;
2. insert the form-domain block and invoke the exact KP finite-volume theorem;
3. insert the Jensen normalizer and quartic uniform-integrability bounds;
4. prove finite-grid association from the M-matrix and Q3 mixed derivatives;
5. pass weighted grid laws to periodic continuous loops on the finite-volume
   sup-norm space and remove coordinate clips;
6. encode each time history as an `8N`-dimensional FSS spin, apply the
   reflection-positive tensor-kernel inequality, and only then take the mesh
   limit;
7. convert the resulting variance to the Duhamel covariance and Fourier IR
   cap, with `D_L=(1/beta) integral C` and spatial eigenvalue `2E(p)`;
8. compose these finite-volume statements with pressure convergence,
   Griffiths/Falk--Bruch, and the source-tangent DLR construction.

For P-06, the interpolation is order preserving and the finite-grid mixed
derivative ledger remains

```text
temporal kinetic: +m/epsilon,
spatial difference: +epsilon*c,
Q3 edge: epsilon*lambda/4*((x+y)^2+5*(x-y)^2),
all onsite and linear terms: 0.
```

For P-09, the encoded source is exactly
`eta_y=t*sqrt(epsilon)*(a_y*u)` at every time slice, so its pairing is
`t*epsilon*sum_(y,k) a_y*(u,x_(y,k))` with no `O(epsilon)` source error.
The finite FSS inequality therefore gives

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2c) * <a,L_sp^(-1)a>,
```

for zero-sum `a`.  The source exponential and its second derivative are
passed through the weak limit only after the Jensen denominator and quartic
Young bound have supplied uniform integrability.

## 6. Dependency and audit matrix

| Manuscript statement | Local evidence | Imported or remaining gate |
|---|---|---|
| finite-volume local potential is coercive | `q3lock-quartic-coercivity-form-domain-audit-260905.md` | exact KP theorem/version and form-domain review |
| finite-volume loop law exists | Q3LOCK/KP crosswalk | KP Assumption (A), heat trace and source sign audit |
| time-grid Gaussian converges | covariance, increment and interpolation audits | independent Fourier/seam check |
| weighted grid normalizer is mesh-uniform | `q3lock-normalizer-jensen-uniformity-audit-260905.md` | confirm the same split in the final Hamiltonian |
| continuous-loop FKG | P-06 round-2 proof text | external theorem and clip/UI audit |
| Hilbert-valued FSS/Duhamel cap | P-09 round-2 proof text | exact FSS version, transfer and differentiation audit |
| strict cusp and two parity states | EXP-000782 composition | all upstream audits, source tangents and operator review |
| paper readiness | this insertion map | bounded claim card, clean replay, content freeze and release review |

No row in this table is a claim-card promotion.  A failure in any imported
theorem hypothesis reopens every downstream row that depends on it.

## 7. Adversarial checks

1. **The Jensen step needs a nonnegative residual action.** Rejected: it needs
   only finite Gaussian expectation of the residual action; the quartic and
   Gaussian moment bounds provide that finiteness.
2. **The `3c` onsite term can be counted as `3c/2`.** Rejected: six periodic
   endpoint incidences force `3c`; open boundaries require their own degree
   formula.
3. **The auxiliary `a` changes the model.** Rejected: it is recombined with
   the residual potential before the exact Hamiltonian is stated.
4. **A finite-volume compact resolvent proves the thermodynamic DLR theorem.**
   Rejected: KP compactness, specification continuity, source removal and
   spatial accumulation remain separate.
5. **The finite-grid IR cap alone proves a pressure cusp.** Rejected:
   pressure limits, Griffiths/Falk--Bruch, source tangents and the strict
   threshold composition are still required.
6. **Content integration authorizes a PDF.** Rejected: PDF compilation and
   visual review remain blocked until the final content-freeze gates pass.

## 8. Current disposition and next gate

The Jensen normalizer and quartic form-domain inputs are now mapped into a
single ordered proof spine.  This is a T0 manuscript-readiness advance, not a
certified theorem or publication-ready paper.  The next gate is an
independent, source-level audit of the KP/FSS statements and the unbounded
operator/common-core passages, followed by a line-by-line content review of
the complete paper draft.  Only if those reviews pass may a bounded claim card,
content freeze, clean replay and release review be considered.  PDF creation,
rendering and page-by-page inspection are explicitly reserved for the final
stage after those gates.

## 9. Explicit nonclaims

This addendum does not assert a strict infrared lower bound, strict source
cusp, phase coexistence, DLR multiplicity, extremality, purity, clustering,
real-time dynamics, KMS state, ground state, spectral gap, continuum limit,
physical vacuum, cosmological interpretation, C6, CP1, Sector A or Pre-A
closure.  It creates no claim card, P2 manuscript, submission, upload, tag,
release or PDF.
