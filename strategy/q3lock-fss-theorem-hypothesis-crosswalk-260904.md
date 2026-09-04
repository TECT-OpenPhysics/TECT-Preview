# Q3LOCK FSS theorem hypothesis crosswalk

**Status:** T0 independent source audit; P-09 remains open
**Date:** 2026-09-04
**Owner task:** T-054
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782
**Primary source:** Froehlich--Simon--Spencer, *Infrared Bounds, Phase
Transitions and Continuous Symmetry Breaking*, Commun. Math. Phys. 50
(1976), [source PDF](https://math.caltech.edu/SimonPapers/65.pdf)
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Purpose and boundary

The Q3LOCK manuscript invokes the Froehlich--Simon--Spencer (FSS) Gaussian
domination estimate at each finite Euclidean time mesh.  This note is a
source-version and hypothesis crosswalk.  It records exactly which parts of
the FSS theorem are being used, maps their variables to the Q3LOCK finite
grid, and separates the finite-grid theorem from the still-open loop limit.

This is a T0 proof-text audit.  It does not register a new mathematical claim,
does not promote P-09, and does not imply a spatial thermodynamic limit,
strict source cusp, infrared zero-mode lower bound, or DLR multiplicity.

## 2. FSS source hypotheses and theorem locations

The audited source is the 18-page paper identified on its first page as
Commun. Math. Phys. 50, 79--95 (1976).  The finite-volume setup is in Section
2, pages 81--82 of the printed pagination.

### 2.1 Finite-volume model

FSS takes a rectilinear parallelepiped `A` with `L_1 x ... x L_v` sites and
periodic identification, so that `A` is a discrete torus.  At each site
`α` the spin is a vector `σ_α in R^d` for a fixed finite component number
`d`.  The Hamiltonian is the ferromagnetic nearest-neighbour form

```text
H(σ) = -J * sum_<α,β> σ_α dot σ_β,
```

where each nearest-neighbour pair is counted once, including the wrap-around
pairs.  Magnetic fields are not a separate interaction in the theorem; FSS
states that they may be absorbed into the single-spin measure `dλ`.

The a-priori measure is an arbitrary finite measure on `R^d` satisfying

```text
integral exp(a*|u|^2) dλ(u) < infinity  for every finite a.
```

After normalization by the finite-volume partition function this produces the
Gibbs state used in the theorem.  No radiality, `O(d)` invariance, or special
single-spin density is assumed.  The source itself emphasizes that the
Gaussian-domination constants are independent of the single-spin measure, the
number of components, and internal symmetry.  It also explicitly limits the
result to cubic nearest-neighbour geometry; no general non-cubic or arbitrary
non-nearest-neighbour extension is imported here.

### 2.2 Exact theorem block used by Q3LOCK

The theorem block is Theorems 2.1--2.3, equations (2.1)--(2.3), followed by
the finite-volume-to-infinite-volume remark immediately after Theorem 2.3.
The paper's Theorem 2.1 is the exponential Gaussian-domination (gradient)
inequality for arbitrary vector-valued test fields.  Theorem 2.2 is its
translation-invariant integrated form, and Theorem 2.3 gives the Laplacian
form used for infrared bounds.  In the source normalization, the theorem is
written with coupling `J` and the discrete Laplacian `-Delta`; the Q3LOCK
manuscript must quote these equations in the bibliography's pinned version
and then perform the explicit substitution `J = c` and `d = 8*N_t`.

The source also states that (2.1)--(2.3) pass to infinite-volume limits of
periodic states.  That statement is not used as a shortcut for the Q3LOCK
time-grid limit or for its spatial pressure limit: those passages have their
own topology and uniform-integrability obligations below.

## 3. Q3LOCK finite-grid map

Let `N_t` be the number of Euclidean time slices and
`epsilon=beta/N_t`.  At spatial site `y`, encode the complete grid history by

```text
s_y = (sqrt(epsilon)*x_(y,k))_(k=0,...,N_t-1) in R^(8*N_t).
```

The ordinary Euclidean dot product satisfies

```text
s_y dot s_z = epsilon * sum_k x_(y,k) dot x_(z,k).
```

Under this isometry the Q3LOCK spatial bond is exactly

```text
-c * sum_<yz> s_y dot s_z,
```

so the FSS coupling is `J=c` with no time-slice-dependent correction.  All
terms local in the spatial decomposition are placed in one single-site prior
`d lambda_(N_t)`: the cyclic temporal kinetic term, the scalar and Q3LOCK
onsite terms, the positive harmonic split, and the source-free compensating
quadratic factors.  The declared quartic lower bound gives, for every fixed
`N_t` and every finite `a`,

```text
integral exp(a*|s|^2) d lambda_(N_t)(s) < infinity.
```

The bound may depend on `N_t`; FSS independence of the prior and component
number is what permits applying the theorem separately at each finite mesh.
No `O(8)` or radial symmetry is inserted.

## 4. Source normalization and Poisson shift

Let `a:Lambda_L -> R` be spatially zero-sum and let
`u=(1,...,1)/sqrt(8)`.  The load-bearing time-constant observable is

```text
X_(N_t,L)(a) = epsilon * sum_(y,k) a_y * (u dot x_(y,k)).
```

There are two equivalent coordinate conventions.  In the epsilon-weighted
inner product the source is `j_y(k)=t*a_y*u`, while in the ordinary
`R^(8*N_t)` coordinates required by the FSS theorem it is

```text
eta_y = t*sqrt(epsilon)*(a_y*u)_(k=0,...,N_t-1).
```

In either convention the source pairing is exactly `t*X_(N_t,L)(a)`, and
`Σ_y |eta_y|^2 = beta * Σ_y |a_y|^2`.  This is the source-scaling correction
recorded in the companion audit
`q3lock-fss-source-scaling-normalization-correction-260904.md`.

Orient the spatial edges once, write `D` for incidence and
`L_sp=D^*D`, and use `L_sp^(-1)` only on the zero-sum subspace.  The FSS
gradient/Laplacian inequality with the Poisson shift then gives, at fixed
`N_t` and `Lambda_L`,

```text
log E_(N_t,L,0) exp[t*X_(N_t,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>,

Var_(N_t,L,0)(X_(N_t,L)(a))
  <= beta/c * <a,L_sp^(-1)a>.
```

If `D_(N_t,L)` is defined by
`Var(X_(N_t,L)(a))=beta^2*<a,D_(N_t,L)a>`, then for a nonzero spatial
Fourier mode `p`, with `E(p)=sum_i(1-cos(p_i))` and graph eigenvalue
`2*E(p)`,

```text
Dhat_(N_t,L)(p) <= 1/(2*beta*c*E(p)).
```

The factor `beta` comes from `N_t*epsilon=beta`; the factor `2` comes from
the graph Laplacian eigenvalue.  Both factors are theorem bookkeeping, not
fit parameters.

## 5. Hypothesis-by-hypothesis disposition

| FSS requirement | Q3LOCK map | Disposition |
|---|---|---|
| finite periodic rectilinear/cubic box | even periodic `Lambda_L`, wrap-around edge list | usable only with the stated periodic convention; open boxes need separate degree accounting |
| finite component number | `d=8*N_t` at each mesh | satisfied mesh-by-mesh; no uniform moment constant is claimed |
| ferromagnetic NN coupling | `J=c>0` after the scaled-spin isometry | satisfied for the declared spatial bond |
| arbitrary prior with all exponential quadratic moments | `d lambda_(N_t)` containing temporal and Q3LOCK onsite factors | conditional on the uniform quartic lower bound and finite normalizer proof |
| magnetic/source factors | source inserted as ordinary vector `eta` above | source differentiation is finite-dimensional; the loop passage is separate |
| no radial/internal symmetry assumption | anisotropic Q3LOCK prior | satisfied; only the crossing kernel supplies positivity |
| Laplacian zero mode | `sum_y a_y=0` | satisfied; inverse restricted to zero-sum subspace |

The only rows not yet closed at paper level are the exact quartic constants,
the normalizer lower bound uniform in `N_t` at fixed `L`, and the final
independent audit of the edge convention in every pressure volume.

## 6. What FSS does not provide

The FSS theorem is a finite-dimensional spatial statement.  It does not by
itself provide:

1. convergence of the weighted grid measures to Q3LOCK continuous loops;
2. uniform integrability for the unbounded source exponential or its second
   derivative;
3. identification of the limiting variance with the KP Duhamel covariance;
4. a spatial thermodynamic-pressure limit or differentiation of that pressure;
5. a strict source cusp, a positive infrared zero mode, or two distinct DLR
   states.

The grid-to-loop argument must therefore use the declared Feynman--Kac/Trotter
identification, Gaussian increment tightness, quartic Young absorption,
source-uniform normalizer bounds, and a separate covariance convergence proof.
The independent KP theorem-number/form-domain audit
`q3lock-kp-theorem-number-and-form-domain-independent-audit-260904.md` supplies
the fixed-source Euclidean-DLR crosswalk but does not close these Q3LOCK-local
steps.

## 7. Final manuscript transcription requirements

Before any claim registration or PDF generation, the manuscript must:

* pin the exact FSS bibliography version and checksum;
* state the periodic edge convention and distinguish it from any open-volume
  pressure convention;
* choose either the weighted or ordinary source convention and display the
  conversion `eta=sqrt(epsilon)*j`;
* quote Theorems 2.1--2.3 with the source's `J`, `Delta`, and Fourier
  normalizations before substituting `c`, `L_sp`, and `E(p)`;
* provide the quartic uniform-integrability constants and fixed-volume
  normalizer lower bound with every epsilon factor;
* independently verify the finite-grid variance to KP Duhamel covariance
  normalization, including `beta` and the graph factor `2`;
* retain the explicit nonclaims in Section 6 and keep P-06/P-09 open until
  the proof audit signs off.

## 8. Audit verdict

The FSS theorem is a compatible finite-grid ingredient under the displayed
map: its prior, component-count, nonradial, ferromagnetic and periodic-box
hypotheses can be met conditionally by Q3LOCK.  The source-scaling ambiguity is
resolved, and the finite-grid infrared normalization is fixed.  This is not a
closed continuous-loop theorem.  The remaining loop-limit, covariance,
pressure, cusp, and DLR-multiplicity obligations remain explicit gates.

**Status after this audit:** T0 `advanced` as a source crosswalk; P-09,
P-06, the independent proof audit, claim registration, manuscript release,
and PDF generation remain open/deferred.
