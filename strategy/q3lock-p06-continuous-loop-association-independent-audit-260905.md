# Q3LOCK P-06 continuous-loop association independent audit

**Status:** T0 internal independent audit; P-06 remains open  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Companion proof text:** `strategy/q3lock-p06-p09-independent-proof-audit-round2-260905.md`  
**PDF:** deferred until mathematical content freeze and external review

## 1. Question and strict boundary

This audit rechecks the complete fixed-spatial-volume association chain for the
nonradial eight-component Q3LOCK time-grid law.  The chain is deliberately
split into (i) a finite lattice argument, (ii) compact-cube and full-space
limits, (iii) order-preserving interpolation, (iv) weak passage to the
continuous periodic loop law, and (v) removal of coordinate clips.  No
path-space MTP2 theorem is imported.  This is an internal proof-text audit,
not external referee sign-off and not a phase or DLR result.

## 2. Finite-mesh sign and finite FKG

At fixed `N`, periodic spatial volume and source, the time-grid density has the
form `f_N=exp(Phi_N)` with a strictly positive smooth density on the full
finite-dimensional Euclidean space.  The cyclic temporal kinetic form and the
spatial difference form have positive off-diagonal mixed derivatives in the
log density.  For a Q3 edge,

```text
W(x,y)=lambda/4*(x-y)^2*(x^2+y^2),
-partial_x partial_y W
  =lambda/4*((x+y)^2+5*(x-y)^2) >= 0.
```

Diagonal quadratic, quartic, harmonic-split and linear terms have zero mixed
derivative.  Thus every distinct-coordinate mixed derivative of `Phi_N` is
nonnegative.  Integrating one mixed derivative over a coordinate rectangle
and applying a finite sequence of coordinate interchanges gives

```text
Phi_N(x meet y)+Phi_N(x join y) >= Phi_N(x)+Phi_N(y).
```

Consequently the density obeys the finite lattice condition on every
rectangular coordinate grid in a cube `K_R=[-R,R]^M`.  The grid weights
`f_N(z)*delta^M` are positive and form a finite distributive lattice.  The
finite FKG proposition in the pinned FKG source therefore gives association
for increasing grid functions.  This step uses no rotation invariance of the
Q3 prior.

## 3. Compact-cube and full-space passage

Let `F` and `G` be bounded continuous coordinatewise-increasing functions on
`R^M`.  On each fixed cube, ordinary Riemann-sum convergence applies to
`F`, `G` and `F*G`; the normalization also converges because `f_N` is locally
integrable.  The finite-grid covariance inequality therefore holds for the
conditional density on `K_R`.  As `R` increases, the indicators of `K_R`
converge pointwise and all three observables are bounded.  Dominated
convergence gives association for the full fixed-mesh law.  No unbounded
observable is used in this passage.

For bounded `F,G`, the product need not be increasing and does not need to be:
the finite FKG proposition is a covariance inequality for the two increasing
arguments, while `F*G` is only an integrable test whose expectation is taken.
For unbounded coordinate products, clips are introduced separately below.

## 4. Interpolation and weak loop limit

Let `I_N` be periodic piecewise-linear interpolation.  Its coefficients on
one time cell are `(1-theta,theta)` with both entries nonnegative, so
coordinatewise grid order implies pointwise loop order.  Hence `F o I_N` and
`G o I_N` are increasing whenever `F,G` are pointwise-increasing loop
functionals.

Assume the fixed-volume weighted grid laws satisfy

```text
(I_N)_# mu_(N,L,h) ==> mu_(L,h)
```

in the periodic sup-norm topology, and let `F,G` be bounded and continuous in
that topology.  Then `F`, `G`, and `F*G` are bounded continuous.  Applying the
finite-mesh association inequality to `F o I_N` and `G o I_N` and taking the
weak limit gives

```text
E_(L,h)[F G] >= E_(L,h)[F] E_(L,h)[G].
```

This passage requires only the stated weak convergence and bounded
continuity; it does not require total-variation convergence or a path-space
lattice theorem.  The convergence itself remains a separate analytic input:
the Gaussian covariance/interpolation estimates, compact residual Riemann
sums, and source-uniform normalizer bounds must be supplied at fixed spatial
volume.

## 5. Clip removal and the zero-source coordinate product

For a coordinate `Y=q_(y,e)` define `phi_R(Y)=max(-R,min(Y,R))` and use the
nonnegative increasing functions

```text
F_R=phi_R(Y)+R,
G_R=phi_R(Z)+R,
```

for `Z=q_(y,f)`.  Association is unchanged by the constant shifts.  At zero
source, global parity gives `E[Y]=E[Z]=0`, so the clipped covariance is
nonnegative.  The quartic coercivity and fixed-volume normalizer estimates give
finite, uniformly bounded second moments for the exact loop law.  Since
`|phi_R(Y) phi_R(Z)| <= |Y Z|` and
`E|Y Z| <= (E Y^2+E Z^2)/2`, dominated convergence yields

```text
E[Y Z] >= 0.
```

The same second-moment bound is obtained uniformly along the time-grid
sequence from the Gaussian envelope and quartic normalizer, but the loop
covariance conclusion needs only the limiting law after its fixed-volume
existence has been established.

## 6. Exact Q3 collective consequence

With `S_y=sum_e q_(y,e)^2` and
`D_y=sum_{{e,f} in E(Q3)}(q_(y,e)-q_(y,f))^2`, the three-regular Q3 graph
identity is

```text
D_y=3*S_y-2*sum_{{e,f} in E(Q3)}q_(y,e)q_(y,f).
```

The nonnegative zero-source coordinate products imply
`E[D_y] <= 3 E[S_y]`.  For
`Q_y=8^(-1/2)*sum_e q_(y,e)`,

```text
E[Q_y^2]
 = (E[S_y]+2*sum_(e<f)E[q_(y,e)q_(y,f)])/8
 >= E[S_y]/8.
```

These are precisely the local association inputs used by the collective
Falk--Bruch/double-commutator route.  No spatial thermodynamic limit is used
in this section.

## 7. Hypothesis ledger and unresolved seam

| Link | Required input | Independent disposition |
|---|---|---|
| mixed derivatives to finite FKG | positive smooth density and finite distributive grid | algebraically consistent at fixed mesh |
| cube to full space | local integrability and bounded tests | dominated-convergence step is valid |
| grid to loop | order-preserving interpolation and weak sup-norm convergence | conditional on fixed-volume Gaussian/residual audit |
| bounded association | bounded continuity of `F`, `G`, `F*G` | weak passage is valid under the stated topology |
| coordinate product | finite second moments and parity | clip removal is valid at fixed volume |
| spatial accumulation | volume-uniform weighted-tempered bounds | not supplied here; separate open gate |

The remaining P-06 gate is therefore not the finite FKG algebra.  It is the
independent verification of the exact KP/Feynman--Kac topology and the
fixed-volume Gaussian/residual convergence with constants compatible with the
source window, followed by the spatial weighted-tempered accumulation.  None
of those inputs is silently promoted by this audit.

## 8. Adversarial checks

| Objection | Disposition |
|---|---|
| The cited FKG proposition is already a theorem on continuous loops | **UPHELD AS FALSE:** only its finite-distributive-lattice statement is used. |
| `F*G` must be increasing to use association | **UPHELD AS FALSE:** the two arguments are increasing; `F*G` is only an integrable expectation. |
| Weak convergence automatically handles coordinate products | **UPHELD AS FALSE:** clips and a second-moment/UI bound are explicit. |
| Q3LOCK requires O(8) symmetry for the sign calculation | **UPHELD AS FALSE:** the Q3 mixed-derivative identity is nonradial and pointwise. |
| Fixed-volume loop association gives an infinite-volume DLR phase | **UPHELD AS FALSE:** spatial compactness, source tangents and DLR selection remain separate. |
| This audit closes the strict cusp or authorizes a PDF | **UPHELD AS FALSE:** all pressure, cusp, claim, external-review and final-PDF gates remain open. |

## 9. Disposition and next gate

The finite-grid-to-fixed-loop association chain is internally coherent under its
explicit fixed-volume weak-convergence and moment hypotheses.  This is an
**advanced T0 internal audit** that strengthens the proof text; it is not an
external mathematical certification.  Next, an independent reviewer must
check the KP topology, the Gaussian reference and residual convergence, and
the volume-uniform tempered estimates before P-06 can be treated as a
registered theorem input.

## 10. Explicit nonclaims

No strict source cusp, positive infrared zero mode, phase coexistence, DLR
multiplicity, extremality, purity, clustering, KMS state, real-time dynamics,
ground-state phase, spectral gap, continuum limit, physical-vacuum or
cosmological conclusion is asserted.  No claim card, manuscript release,
submission package, or PDF is created.
