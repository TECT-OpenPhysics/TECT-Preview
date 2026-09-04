# Q3LOCK FSS theorem-factor transcription audit

**Status:** T0 source transcription audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**External source:** Froehlich--Simon--Spencer, *Infrared Bounds, Phase
Transitions and Continuous Symmetry Breaking*, Commun. Math. Phys. 50 (1976),
79--95  
**PDF:** deliberately deferred until content freeze, independent proof audit,
clean replay, and release review

## 1. Purpose and strict boundary

The Q3LOCK finite-grid proof uses the FSS Gaussian-domination theorem.  The
existing crosswalk had the intended constants, but a release-quality audit
must pin the theorem display itself before any manuscript text is frozen.  This
note records a visual transcription of the hash-frozen FSS source and performs
the source-coordinate, incidence-operator, and Duhamel-factor substitution
explicitly.

This is a T0 source-and-normalization audit.  It is not an independent proof
of the Q3LOCK loop limit, a pressure theorem, a strict cusp, or DLR-state
multiplicity.  It does not promote P-06 or P-09, create a claim card, authorize
manuscript release, or authorize PDF generation.

## 2. Frozen source and visual check

The source bytes are the Caltech copy captured in the literature source freeze:

```text
URL:      https://math.caltech.edu/SimonPapers/65.pdf
bytes:    1404869
SHA-256:  108b70f69d707c77c46bb4d4870c9df43be635394d3013be043f8f1a566178e1
```

The theorem block was rendered from PDF page 3, whose printed pagination is
page 81.  The first-page masthead says `79--85`, while the body continues to
printed page 95; the pinned bibliography and source-freeze note retain the
79--95 range and record that discrepancy.

The Section 2 hypotheses visible before the theorem block are: a periodic
rectilinear parallelepiped; a vector spin `sigma_alpha in R^d` at each site; a
ferromagnetic nearest-neighbour Hamiltonian with coupling `J`; and an
arbitrary one-site measure `d lambda` with all finite quadratic exponential
moments.  Magnetic fields may be absorbed into that one-site measure.  No
radiality or internal `O(d)` invariance is assumed.

## 3. Exact theorem display used in this audit

With spacing normalized but source symbols retained, the printed theorem
displays are:

```text
Theorem 2.1.  For any h_1,...,h_v with values in R^d,

  < exp[ sigma( sum_i partial_i h_i ) ] >_Lambda
    <= exp[ (2J)^(-1) sum_(alpha,i) |h_i(alpha)|^2 ].

Theorem 2.2.  Under the hypotheses of Theorem 2.1,

  < [ sigma( sum_i partial_i h_i ) ]^2 >_Lambda
    <= J^(-1) sum_(alpha,i) |h_i(alpha)|^2.

Theorem 2.3.  For any h with values in R^d,

  < sigma(h) sigma(-Delta h) >_Lambda
    <= J^(-1) sum_(alpha,i) |h_i(alpha)|^2.
```

Here `sigma(h)` denotes the spin pairing with the site field `h`, and
`partial_i h_i` is the source divergence in the chosen coordinate direction.
The Q3LOCK manuscript must state its edge orientation and identify this
divergence with the corresponding incidence operator before applying the
display.  Reversing every edge orientation replaces the field by its negative
and leaves all norms and inequalities unchanged.

The factors are therefore source-level facts: `(2J)^(-1)` belongs to the
exponential theorem, `J^(-1)` belongs to the second-moment and Laplacian
theorems, and the factor `2` in a Fourier denominator is not an FSS constant.
It comes later from the cubic graph eigenvalue.

## 4. Q3LOCK ordinary-coordinate substitution

Let `N_t` be the Euclidean time-grid size and `epsilon=beta/N_t`.  At a
spatial site `y`, encode the complete history by

```text
s_y = (sqrt(epsilon) x_(y,k))_(k=0,...,N_t-1) in R^(8*N_t).
```

Then

```text
s_y dot s_z = epsilon sum_k x_(y,k) dot x_(z,k),
```

so the spatial Q3LOCK bond is exactly `-c sum_<yz> s_y dot s_z`.  The FSS
parameters are consequently

```text
J = c,                 d = 8*N_t,
```

mesh by mesh.  The temporal kinetic term, scalar terms, Q3-locking term,
positive harmonic split, and the single-site quadratic allocation belong to
the one-site prior.  The quartic confinement gives the FSS moment hypothesis
for each fixed `N_t`; no uniform-in-`N_t` prior constant is inferred.

For a zero-sum spatial source `a` and the unit component direction
`u=(1,...,1)/sqrt(8)`, define

```text
X_(N_t,L)(a) = epsilon sum_(y,k) a_y (u dot x_(y,k)).
```

The weighted-coordinate source is `j_y(k)=a_y*u` with
`<j,x>_epsilon=X_(N_t,L)(a)`.  In the ordinary FSS coordinates the source at
parameter `t` is instead

```text
eta_y(t) = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N_t-1).
```

The square root is forced by the isometry above, and the source pairing is
exactly

```text
sum_y s_y dot eta_y(t) = t*X_(N_t,L)(a).
```

## 5. Domain-correct Poisson field and exact constants

Fix an orientation of the spatial periodic edges.  Let `V_0` be the
zero-sum vertex space and let `E` be the oriented edge space.  Write

```text
G: V_0 -> E,             B_FSS = G^*: E -> V_0,
L_sp = G^* G = B_FSS B_FSS^* on V_0.
```

These maps act componentwise on `R^(8*N_t)`-valued fields.  Because `a` is
zero-sum, `eta(t)` lies in the domain of `L_sp^(-1)`.  The edge-valued field
used in the FSS display is

```text
h_t = G L_sp^(-1) eta(t) = B_FSS^* L_sp^(-1) eta(t),
```

not `G^* L_sp^(-1) eta(t)` under this declared convention.  It satisfies
`B_FSS h_t=eta(t)` and

```text
sum_e |h_t(e)|^2
  = <eta(t), L_sp^(-1) eta(t)>_ordinary
  = beta*t^2 <a, L_sp^(-1) a>_spatial,
```

because `sum_k epsilon=beta` and `|u|=1`.

Applying Theorem 2.1 with `J=c` gives the finite-grid bound

```text
log E_(N_t,L,0) exp[t*X_(N_t,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>_spatial.
```

Theorem 2.2, or the second derivative at `t=0` of this finite-dimensional
bound, gives

```text
Var_(N_t,L,0)(X_(N_t,L)(a))
  <= beta/c * <a,L_sp^(-1)a>_spatial.
```

The preceding two displays are finite-grid statements only.  They use the
zero-source parity to identify the first derivative with zero; the source
exponential is analytic at fixed finite volume and mesh.

## 6. Duhamel conversion and the Fourier factor

For the continuous-loop law at fixed spatial volume, define the scalar
unit-direction Duhamel covariance by

```text
D_L(y,z) = (1/beta) integral_0^beta C_(yz)(tau) d tau,
```

where `C` is the connected correlation of `(u,omega_y(tau))` and
`(u,omega_z(0))`.  Periodicity and time-translation invariance give

```text
Var(X_L(a)) = beta^2 <a,D_L a>_spatial.
```

Thus, after a separately justified grid-to-loop covariance passage,

```text
<a,D_L a>_spatial
  <= 1/(beta*c) * <a,L_sp^(-1)a>_spatial.
```

For a nonzero spatial Fourier mode `p`, the cubic periodic graph has

```text
ell(p) = 2*E(p),       E(p)=sum_i (1-cos(p_i)).
```

Consequently the scalar unit-direction projection obeys the finite-volume
upper bound

```text
Dhat_L(p) <= 1/(2*beta*c*E(p)),       p != 0.
```

The bookkeeping is now explicit: `beta` comes from the source norm and the
two time integrations divided by the declared Duhamel normalization; the
Fourier `2` comes solely from `ell(p)=2*E(p)`.  The zero mode is excluded
because `L_sp^(-1)` is defined only on `V_0`.

## 7. Hypothesis and scope disposition

| FSS item | Q3LOCK correspondence | disposition |
|---|---|---|
| periodic rectilinear box | periodic cubic `Lambda_L` and fixed edge orientation | usable only for the stated periodic convention |
| finite vector dimension | `d=8*N_t` | mesh-by-mesh; no uniform dimension limit imported |
| ferromagnetic nearest-neighbour coupling | `J=c>0` after scaled-spin isometry | conditional on the declared spatial action |
| all quadratic exponential moments of the prior | fixed-`N_t` local prior with quartic confinement | requires the Q3LOCK normalizer and quartic audit |
| source divergence and Poisson field | `B_FSS=G^*`, `h_t=G L_sp^(-1)eta(t)` | domain fixed here; source passage remains local |
| zero mode | `sum_y a_y=0` | inverse restricted to `V_0` |
| component/internal symmetry | anisotropic Q3 prior | no `O(8)` or radial assumption imported |

This audit fixes the theorem factor and the local map.  It does not establish
the hypotheses uniformly in the time mesh, nor does it turn the FSS theorem
into a path-space theorem.

## 8. Remaining gates and explicit nonclaims

The following remain open: independent finite-grid-to-loop FKG and FSS
passages; source-uniform integrability and normalizer bounds; covariance and
Duhamel identification; operator/form-domain control; spatial pressure and
source-tangent composition; strict cusp and DLR-state separation; claim-card
and result-lineage review; clean replay; and external mathematical referee
review.

Accordingly this note does not certify a strict cusp, positive infrared
zero-mode lower bound, phase coexistence, DLR multiplicity, extremality,
purity, clustering, KMS or real-time dynamics, a ground state or gap, a
continuum limit, a physical vacuum, cosmology, C6, CP1, Sector A, or Pre-A
closure.  No manuscript, submission, upload, release, or PDF is created.

## 9. Adversarial checks

1. **The first-page range can be copied as 79--85.**  Rejected: the rendered
   body reaches printed page 95 and the source freeze records the discrepancy.
2. **The graph factor `2` is hidden in Theorem 2.1.**  Rejected: the theorem
   has `(2J)^(-1)`; the later factor `2` is the eigenvalue of `L_sp`.
3. **The ordinary source can omit `sqrt(epsilon)`.**  Rejected: that would
   break the scaled-spin isometry and change the source pairing by a mesh
   factor.
4. **`G^* L_sp^(-1)eta` is the edge-valued Poisson field.**  Rejected under
   the declared domains: `G` is vertex-to-edge and `G^*` is edge-to-vertex.
5. **The finite-grid variance bound is already a loop theorem.**  Rejected:
   weak convergence, source-uniform integrability, and Duhamel identification
   are separate obligations.
6. **The FSS prior hypothesis is uniform in `N_t` for free.**  Rejected: the
   theorem is applied at each finite dimension; uniform mesh constants are a
   Q3LOCK-local gate.
7. **The zero mode is controlled by this Poisson shift.**  Rejected: only
   `V_0` is inverted, so `p=0` is outside the displayed bound.

## 10. Disposition

The visual source check and the explicit coordinate calculation agree with the
existing Q3LOCK constants: `beta/(2c)` in the exponential bound,
`beta/c` in the variance bound, and `1/(2*beta*c*E(p))` after Duhamel and
Fourier conversion.  The result is recorded at T0 as a reproducibility aid;
P-06, P-09, the independent proof audit, claim registration, content freeze,
external review, and final PDF remain deferred.
