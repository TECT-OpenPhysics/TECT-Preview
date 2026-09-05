# Q3LOCK KP/FSS external source and theorem-scope audit

**Status:** T0 source-level audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Sources:** Kozitsky--Pasurek arXiv:math-ph/0609045v1 and
Froehlich--Simon--Spencer, Commun. Math. Phys. 50 (1976), 79--95  
**PDF:** deferred until content freeze and final release review

## 1. Purpose and boundary

The Q3LOCK manuscript needs two distinct external inputs: the general
finite-volume/Euclidean-DLR construction of Kozitsky--Pasurek (KP), and the
finite-dimensional Gaussian-domination estimate of Froehlich--Simon--Spencer
(FSS).  This note checks their stated theorem locations and records a firewall
against importing KP's separate scalar correlation results into the
nonradial eight-component Q3LOCK argument.

This is a source-scope audit, not an independent proof of the Q3LOCK phase
route.  It does not close P-04, P-06, P-09 or P-12, and it creates no claim
card, manuscript release or PDF.

## 2. KP version and general finite-volume input

The audited KP PDF is identified on its first page as
`arXiv:math-ph/0609045v1`, 16 September 2006.  The source defines the
finite-volume Hamiltonian in (2.2)--(2.3) as a finite collection of
`nu`-component harmonic oscillators with continuous local potentials and a
symmetric pair matrix.  Assumption (A), equations (2.5)--(2.6), requires

```text
V_l continuous, V_l(0)=0,
A_V*|x|^(2*r_KP) + B_V <= V_l(x) <= V(x),  r_KP>1,
Jhat_0 = sup_l sum_l' |J_(l,l')| < infinity.
```

The source then states in (2.8) that the finite-volume Hamiltonian is
self-adjoint, lower bounded, has discrete spectrum, generates a positivity
preserving semigroup and has finite heat trace.  The periodic Ornstein--Uhlenbeck
reference and Feynman--Kac loop representation are given in (2.16), with the
local specification and partition-function continuity in (2.53)--(2.59) and
the DLR accumulation implication in Lemma 2.11.  The general-vector
nonemptiness, moment and support results are Theorems 3.1--3.3.

The Q3LOCK map is therefore conditional but direct: `nu=8`,
`m=chi/hbar^2>0`, the explicit quartic lower/upper bounds supply
`r_KP=2`, the corrected periodic pair convention gives `Jhat_0=6c`, and the
cubic lattice satisfies the geometric regularity condition.  The harmonic
split parameter `a>0` is recombined before the exact Hamiltonian is stated.

## 3. KP scalar-correlation firewall

KP's later correlation propositions are not the same theorem as the general
finite-volume input.  In Section 7, Proposition 7.1 states path-space FKG in
the scalar ordered setting, and Proposition 7.2 assumes

```text
V_l(x) = v_l(x^2) - h_l*x,  h_l>=0,
```

with scalar continuous `v_l`.  Proposition 7.4 gives Gaussian domination and
Lebowitz inequalities under the same scalar form with `h_l=0` and convex
`v_l`.  These hypotheses are not supplied by the anisotropic Q3LOCK
`W_Q3(q)` on `R^8`.  The manuscript must not cite KP Propositions 7.1--7.4 as
the Q3LOCK continuous-loop FKG or infrared theorem.  Those passages remain
Q3LOCK-local obligations.

## 4. FSS theorem locations and hypotheses

The audited FSS source is the 18-page paper
*Infrared Bounds, Phase Transitions and Continuous Symmetry Breaking*,
Commun. Math. Phys. 50 (1976), 79--95.  Section 2 defines a periodic
rectilinear torus with ferromagnetic nearest-neighbour coupling and a finite
vector spin `sigma_alpha in R^d`.  The a-priori single-site measure is
arbitrary subject to

```text
integral exp(a*|sigma|^2) d lambda(sigma) < infinity
```

for every finite `a`; magnetic fields may be placed in that single-site
measure.  Theorem 2.1 is the vector-valued exponential Gaussian-domination
inequality, Theorem 2.2 its translation-invariant form, and Theorem 2.3 the
discrete-Laplacian estimate used for infrared bounds.  The source explicitly states that the constants are independent of the
single-site distribution, the number of components and the internal symmetry,
while the geometry is the cubic nearest-neighbour torus.  A direct recheck of
the pinned Caltech PDF confirms this reading: Section 2 defines the periodic
torus with an arbitrary one-site measure having all quadratic exponential
moments, and its Theorems 2.1--2.3 are stated for finite vector spins without
an O(d)-invariance hypothesis.  The introductory discussion separately warns
that the geometry and nearest-neighbour restrictions remain essential.  Thus
nonradial Q3LOCK history priors are within the finite-grid source theorem's
prior class, but the source still supplies neither the time-grid-to-loop limit
nor any Q3LOCK-specific pressure, cusp or DLR conclusion.

For Q3LOCK, the scaled history spin

```text
s_y = sqrt(epsilon)*(x_(y,k))_(k=0,...,N-1) in R^(8N)
```

maps the spatial action to `-c*sum_<yz> s_y dot s_z`.  The quartic local
bound supplies the required quadratic exponential moments for each fixed
`N`; no uniform-in-`N` prior constant is silently assumed.  The source vector
`eta_y=t*sqrt(epsilon)*(a_y*u)` pairs exactly with
`X_(N,L)(a)=epsilon*sum_(y,k) a_y*(u,x_(y,k))`.  With `sum_y a_y=0`, the
Poisson shift and Theorem 2.3 give the finite-grid bound

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2c) * <a,L_sp^(-1)a>,
```

and hence `Dhat(p)<=1/(2*beta*c*E(p))` after the separately audited Duhamel
conversion.

## 5. Exact source URLs and version obligations

The source pages used for this audit are:

* KP PDF: `https://arxiv.org/pdf/math-ph/0609045` (v1, accessed 2026-09-05).
* FSS PDF: `https://math.caltech.edu/SimonPapers/65.pdf` (Commun. Math. Phys.
  50, 1976, accessed 2026-09-05).

The final manuscript must replace these access references with a pinned
bibliography entry, exact version/checksum, and stable theorem/equation
locations.  A web-readable source check is not a substitute for that release
artifact.

## 6. Disposition and remaining gates

The audit advances the source crosswalk in two ways: KP (2.5)--(2.8), (2.16),
Lemma 2.11 and Theorems 3.1--3.3 are valid candidates for the general
finite-volume and fixed-source Euclidean-DLR inputs after the Q3LOCK potential
map; FSS Theorems 2.1--2.3 are a compatible finite-grid vector ingredient
under the scaled-spin and zero-sum-source map.  KP's scalar Proposition
7.1--7.4 route is explicitly excluded from the Q3LOCK vector proof.

Still open are the exact release-version/checksum capture, the Q3LOCK
finite-grid-to-loop limit, the common-core and unbounded differentiation
argument, pressure/source-tangent composition, and independent external
mathematical sign-off.  The disposition is **T0 source crosswalk advanced;
P-06, P-09, P-12, claim registration and publication remain open**.

## 7. Adversarial checks

1. **KP Assumption (A) is scalar.** Rejected: its finite-volume statement is
   written for `R^nu`; the scalar restriction occurs in the later order
   propositions and is kept separate.
2. **KP Proposition 7.4 can replace the Q3LOCK FSS proof.** Rejected: it
   assumes scalar convex `v_l(x^2)` potentials, while Q3LOCK uses the
   nonradial eight-component Q3 locking term.
3. **FSS requires O(8) invariance.** Rejected: its Section 2 prior is
   arbitrary with all quadratic exponential moments and its constants are
   independent of internal symmetry; the exact theorem version still needs
   release sign-off.
4. **A source URL alone is a release citation.** Rejected: version, checksum,
   theorem locations and the final bibliography entry remain required.
5. **Source audit closes the phase result.** Rejected: all Q3LOCK-local limit,
   operator, pressure, cusp and DLR-state composition gates remain open.

## 8. Explicit nonclaims and PDF boundary

This source audit does not assert a strict infrared lower bound, source cusp,
phase coexistence, DLR multiplicity, extremality, purity, clustering,
real-time dynamics, KMS state, ground state, spectral gap, continuum limit,
physical vacuum, cosmological interpretation, C6, CP1, Sector A or Pre-A
closure.  It creates no claim card, P2 manuscript, submission, upload, tag,
release or PDF.  PDF compilation, rendering and visual review remain final
stage actions after content freeze, independent proof review, clean replay and
release check.
