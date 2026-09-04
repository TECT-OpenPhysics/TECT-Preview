# Q3LOCK P-06/P-09 independent proof audit round 2

**Status:** T0 proof-text audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary sources:** Kozitsky--Pasurek (KP), Froehlich--Simon--Spencer
(FSS), and the source pins recorded in the preceding Q3LOCK audits  
**PDF:** explicitly deferred until content freeze, independent mathematical
review, deterministic replay, and release review

## 1. Audit purpose and strict boundary

This is a second, deliberately narrow audit of the two load-bearing seams that
remain before an independent Q3LOCK paper can be registered: (P-06) passage
from finite time-grid association to continuous-loop FKG, and (P-09) passage
from finite-dimensional FSS Gaussian domination to the continuous-loop
Duhamel bound.  It checks the displayed proof spine against the corrected
periodic edge convention, the KP loop topology, the FSS prior hypotheses, and
the KKK/KP Duhamel normalization.

The audit is not a claim card and is not an external referee response.  It
does not promote EXP-000782, does not create a P2 manuscript, and does not
assert a strict cusp or DLR multiplicity.  It records a proof-text decision
that can be re-audited after any change in the model, source convention,
topology, bibliography version, or order of limits.

## 2. Frozen conventions

The finite spatial volume is a periodic cube `Lambda_L` with `V=L^3`, and
the time mesh has `N` slices, `epsilon=beta/N`.  The eight-component field is
`x_(y,k) in R^8`, the collective unit vector is
`u=(1,...,1)/sqrt(8)`, and `m=chi/hbar^2>0`.

The periodic positive-direction edge multiset has `3V` bonds and six endpoint
incidences per site.  Consequently

```text
c/2 * sum_(y,z in E_plus) |q_y-q_z|^2
  = 3c * sum_y |q_y|^2 - c * sum_(y,z in E_plus) (q_y,q_z).
```

The ordered KP interaction uses `J_yz=c` on the six directed nearest-neighbour
edges, so `Jhat_0=6c`.  The positive `3c` term is assigned once to the local
potential.  Open boxes are a separate convention with diagonal
`(c/2)d_R(y)`; the periodic identity is not reused at an open boundary.

For the scalar collective loop covariance, use

```text
D_L(y,z) = (1/beta) * integral_0^beta C_(yz)(tau) d tau,
Var(X_L(a)) = beta^2 * <a,D_L a>,
```

where `X_L(a)=sum_y a_y integral (u,omega_y)` and `sum_y a_y=0`.  The KKK
source convention is a double-integral covariance, hence its unit-direction
projection is `D_KKK^u=beta^2 D_L`; no component-count factor is inserted into
the unit projection.  The spatial Laplacian eigenvalue is
`ell(p)=2 E(p)`, with `E(p)=sum_j(1-cos(p_j))`.

## 3. P-06: finite-grid association and the loop limit

### 3.1 Mixed-derivative ledger

At fixed `N`, finite `Lambda_L`, and source, the density relative to Lebesgue
measure is strictly positive and smooth.  Its log mixed derivatives have the
following signs.

| factor in the log density | distinct coordinates | mixed derivative |
|---|---|---|
| cyclic temporal kinetic form | adjacent time slices at one site and component | `+m/epsilon` per cyclic edge, with the declared multiplicity retained |
| spatial difference form | same component on a spatial bond | `+epsilon*c` |
| Q3 locking edge `W(x,y)` | an internal Q3 edge | `epsilon*lambda/4 * ((x+y)^2+5(x-y)^2)` |
| diagonal quadratic, scalar quartic, harmonic split, linear source | any distinct pair | `0` |

The third row follows from

```text
-partial_x partial_y [lambda/4*(x-y)^2*(x^2+y^2)]
  = lambda/4 * ((x+y)^2 + 5*(x-y)^2) >= 0.
```

The cyclic precision is an M-matrix, including the parallel-edge
multiplicity when a small torus is retained.  Thus the finite-grid log
density is supermodular in the coordinatewise order.

### 3.2 Finite-dimensional FKG without a path-space shortcut

For completeness, the finite-dimensional association step is made on a
compact cube.  Restrict the density `f_N` to `[-R,R]^M`, put a rectangular
mesh on that cube, and assign the weight `f_N(z)*delta^M` to each grid point.
The cube is a finite distributive lattice, and the mixed-derivative ledger
gives the FKG lattice condition by the usual coordinate-rectangle integral.
The finite FKG proposition therefore gives association for bounded
increasing grid functions.  Riemann-sum convergence gives the same inequality
for bounded continuous increasing functions under the normalized restricted
density.  Letting `R` increase uses bounded convergence, so the fixed-mesh
continuous law is associated.

This is a local finite-dimensional argument.  It does not cite the finite
FKG proposition as an already-proved theorem on `C_per`, does not assert
infinite-dimensional MTP2, and does not use total-variation convergence.

### 3.3 Interpolation and weighted-law convergence

Let `I_N` be periodic piecewise-linear interpolation.  It is order preserving
because every interpolated value is a convex combination of the two endpoint
coordinates.  The periodic Gaussian increment estimate gives, for any
`p>2`,

```text
E |I_N x(t)-I_N x(s)|^p <= C_p * d_circle(t,s)^(p/2),
```

uniformly in sufficiently large `N`.  Kolmogorov tightness is therefore in
the finite-volume periodic sup-norm topology, not in the global KP weighted
tempered topology.

On a compact equicontinuous set of interpolated loops, Arzela--Ascoli makes
the local and spatial Riemann sums converge uniformly to the KP Feynman--Kac
action.  The quartic lower bound gives a mesh-uniform upper weight bound
`R_(N,h)<=exp(beta*V*C)`.  A sup-norm Gaussian event and the common quartic
upper function give a positive normalizer lower bound independent of `N`.
Tightness, uniform-on-compact convergence, and the two-sided normalizer bound
then imply weak convergence of the normalized weighted grid laws on the finite
product `C_per` space.

This is exactly the interface needed before invoking the KP/KKK finite-volume
loop representation.  The later spatial accumulation is a separate use of
the weighted `W_t` compactness theorem and the Feller DLR equation.

### 3.4 Passing association and removing clips

For bounded continuous pointwise-increasing loop functionals `F` and `G`,
`F(I_N x)` and `G(I_N x)` are increasing grid functions.  Weak convergence
therefore passes the finite-grid association inequality to the exact loop
law.  At zero source, global parity gives zero mean for every component.
For a same-site pair use the nonnegative clips

```text
F_R(q)=max(-R,min(q,R))+R,
G_R(q)=max(-R,min(q,R))+R.
```

Association gives the nonnegative covariance of the odd clipped coordinates.
The common quartic moment bound supplies uniform integrability, so `R` can be
sent to infinity and
`E[q_(0,e) q_(0,f)]>=0`.  The argument proves only association and the
coordinate-product consequence needed by the collective double commutator.

### 3.5 P-06 disposition

The finite-grid-to-loop proof text is internally complete once the preceding
Gaussian, normalizer, KP-topology, and quartic-moment lemmas are inserted with
their exact constants.  The remaining gate is an independent mathematical
review of those insertions, especially the chosen KP bibliography version,
the cyclic precision convention, and the clipped uniform-integrability
passage.  P-06 is therefore **T0 proof-text assembled; external audit
required**, not a registered theorem.

## 4. P-09: finite FSS domination and Duhamel normalization

### 4.1 Finite-grid spin encoding

At one spatial site encode the full time history as

```text
s_y = sqrt(epsilon) * (x_(y,k))_(k=0,...,N-1) in R^(8N).
```

Then `s_y dot s_z=epsilon*sum_k (x_(y,k),x_(z,k))`.  All terms local in the
spatial decomposition, including the cyclic time kinetic form, Q3 polynomial,
scalar terms, and the single `3c` onsite allocation, form one finite
single-site prior.  For each fixed `N`, quartic confinement gives

```text
integral exp(alpha*|s_y|^2) d lambda_N(s_y) < infinity
```

for every finite `alpha`.  The source FSS theorem is applied mesh-by-mesh;
its domination constant is independent of the prior and component count,
which is what permits changing `8N` after each finite-dimensional application.
No radial or `O(8)` hypothesis is supplied by the Q3LOCK prior.

### 4.2 Crossing kernel and source vector

Across a spatial reflection plane,

```text
exp[-c*|a-b|^2/2]
 = exp[-c*|a|^2/2] * exp[-c*|b|^2/2] * exp[c*(a,b)].
```

The final kernel is positive definite by its nonnegative symmetric-tensor
series.  This is the reflection-positive input in the finite FSS transfer
argument; all anisotropic onsite factors stay within a single-site prior.

For `a:Lambda_L -> R` with `sum_y a_y=0`, the ordinary-coordinate source is

```text
eta_y = t*sqrt(epsilon) * (a_y*u)_(k=0,...,N-1).
```

Its pairing with the encoded spins is exactly `t*X_(N,L)(a)`, where

```text
X_(N,L)(a)=epsilon*sum_(y,k) a_y*(u,x_(y,k)).
```

Let `G:V_0 -> E` be the signed spatial gradient and let
`B_FSS=G^*` be the FSS edge-to-vertex divergence.  The positive vertex
Laplacian is

```text
L_sp=G^*G=B_FSS B_FSS^* on V_0.
```

Because `sum_y a_y=0`, the zero-sum Poisson solution is well-defined.  The
minimum-norm time-constant edge field is

```text
h_FSS=G L_sp^(-1)j=B_FSS^*L_sp^(-1)j.
```

It satisfies

```text
B_FSS h_FSS=j,
|h_FSS|_N^2=(j,L_sp^(-1)j)_N.
```

The bond completion-square field is `b=h_FSS/c`.  It therefore satisfies

```text
c*(G omega,b)_N=(j,omega)_N,
(c/2)*|b|_N^2=(1/(2c))*(j,L_sp^(-1)j)_N.
```

The finite FSS domination inequality consequently reads

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2c) * <a,L_sp^(-1)a>.
```

The `beta` is exactly `N*epsilon`; the graph eigenvalue contributes the later
factor `2` and is not hidden in the FSS constant.  Differentiating at zero
gives `Var(X_(N,L)(a)) <= beta/c * <a,L_sp^(-1)a>`.

### 4.3 Source-uniform integrability and the loop passage

Write `S_N=epsilon*sum_(y,k)|x_(y,k)|^4`.  Holder's inequality gives the
mesh-independent estimate

```text
|X_(N,L)(a)|
  <= (beta*sum_y |a_y|^(4/3))^(3/4) * S_N^(1/4).
```

If the residual potential obeys `V_(h,a)(q)>=A|q|^4-C` on a compact source
interval, Young's inequality gives, for fixed `T` and a sufficiently small
`delta`,

```text
T*|X_(N,L)(a)| <= delta*S_N + C_(T,delta),
|X_(N,L)(a)|^2*exp(T*|X_(N,L)(a)|)
  <= C'_(T,delta)*exp(2*delta*S_N).
```

Choosing `2*delta<A`, multiplying by the grid weight and using the positive
normalizer lower bound yields a mesh-uniform integrable majorant for the
source exponential and its second-derivative witness.  Thus bounded-test weak
convergence can be upgraded by truncation to

```text
E_(N,L,0) exp[t*X_(N,L)(a)] -> E_(L,0) exp[t*X_L(a)],
Var_(N,L,0)(X_(N,L)(a)) -> Var_(L,0)(X_L(a)).
```

The cyclic interpolation identity is exact:

```text
integral_0^beta (u,I_N x_y)(tau) d tau
  = epsilon*sum_k (u,x_(y,k)).
```

No `O(epsilon)` source error is present.  The finite-grid inequality therefore
passes to the exact finite-volume loop law.

### 4.4 Duhamel and Fourier ledger

Time-translation invariance of the periodic loop law gives

```text
Var(X_L(a))=beta^2*<a,D_L a>,
D_L=(1/beta)*integral_0^beta C(tau) d tau.
```

Hence

```text
<a,D_L a> <= (1/(beta*c))*<a,L_sp^(-1)a>,
Dhat_L(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

The zero-sum condition is essential: `L_sp^(-1)` is never applied to the
constant spatial mode.  The KKK full-vector coefficient is used only as a
normalization cross-check; its rotation-invariant corollary is not imported
for the nonradial Q3LOCK onsite law.

### 4.5 P-09 disposition

The finite-grid source scaling, FSS prior hypotheses, shifted-square cost,
source-uniform integrability, and Duhamel conversion form a coherent
paper-local proof spine.  The remaining gate is an independent review of the
exact FSS theorem statement and version, the finite-grid/Feynman--Kac
identification, and differentiation after the uniform-integrability passage.
P-09 is therefore **T0 proof-text assembled; external audit required**.

## 5. Adversarial decision table

| Objection | Disposition | Consequence |
|---|---|---|
| Finite FKG already proves a path-space theorem | **UPHELD AS FALSE** | The proof uses compact-cube finite FKG, interpolation, weak convergence, and clip removal as separate steps. |
| `W_t` compactness is the topology of the time-grid limit | **UPHELD AS FALSE** | The grid limit is finite-volume sup norm; `W_t` enters only in the later spatial DLR accumulation. |
| The Q3 prior must be `O(8)`-invariant for FSS | **UPHELD AS FALSE** | FSS is applied with an arbitrary finite single-site prior; the exact theorem/version still needs external sign-off. |
| Weak convergence alone passes `exp(tX)` and `X^2 exp(tX)` | **UPHELD AS FALSE** | Quartic Young absorption and the mesh-uniform normalizer lower bound are load-bearing. |
| The old `3c/2` onsite allocation can be retained | **UPHELD AS FALSE** | The periodic incidence count forces `3c`; open boxes require a degree-dependent diagonal. |
| A finite-grid IR cap already proves a cusp | **UPHELD AS FALSE** | Pressure convergence, Griffiths conversion, and source-tangent DLR construction remain separate. |

## 6. Current decision and next gate

The two proof seams are now written in a form suitable for manuscript
transcription, with the topology, edge, source, beta, and factor-two ledgers
exposed.  This is a substantive T0 advance in proof-text readiness, not a
mathematical certification.  The next gate is a genuinely independent audit
of the pinned KP/FSS statements and of the operator/form-domain passages; any
objection reopens the affected seam and invalidates downstream cusp/state
composition.  Until that audit passes, the bounded Q3LOCK result remains
unregistered and the P2 channel remains closed.

## 7. Final-stage PDF gate

No PDF is created in this audit.  PDF work is permitted only after all of the
following are true:

1. P-06 and P-09 proof text has passed independent mathematical review;
2. the bounded independent claim card and its result lineage are registered;
3. the manuscript text, bibliography versions, nonclaims, and source hashes
   are content-frozen;
4. primary, independent, and integrated verification rerun from a clean
   snapshot with byte-stable outputs;
5. the release check passes on the frozen tree.

Only then may the final LaTeX compilation, PDF rendering, page-by-page visual
review, and hash capture be performed.  A failed content or proof review
requires repair and re-review before any PDF is issued.

## 8. Explicit nonclaims

This audit does not assert an all-parameter phase theorem, phase absence below
the sufficient threshold, a continuum limit, a common real-time dynamics, a
common-alpha KMS state, a ground-state phase or gap, extremality, purity,
clustering, physical vacuum, cosmological interpretation, C6, CP1, Sector A,
or Pre-A closure.  It creates no claim card, P2 manuscript, release commit,
submission, upload, tag, or publication.
