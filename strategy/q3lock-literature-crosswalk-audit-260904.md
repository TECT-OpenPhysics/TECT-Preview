# Q3LOCK primary-literature crosswalk audit

**Status:** T0 research audit; source-scope and novelty boundary  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority under review:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred

## 1. Audit purpose

This note records what may be imported from the three primary references used
by the Q3LOCK paper and what must be reproved for the nonradial
eight-component model.  It is a scope audit, not a priority or novelty claim.

Primary references:

* Y. Kozitsky and T. Pasurek, *Euclidean Gibbs states of interacting quantum
  anharmonic oscillators*, arXiv:math-ph/0609045, DOI
  `10.1007/s10955-006-9274-9`.
* A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase Transitions and Quantum
  Stabilization in Quantum Anharmonic Crystals*, arXiv:0710.2303, DOI
  `10.1142/S0129055X08003353`.
* J. Froehlich, B. Simon and T. Spencer, *Infrared Bounds, Phase
  Transitions and Continuous Symmetry Breaking*, Commun. Math. Phys. 50
  (1976), 79--95, `https://math.caltech.edu/SimonPapers/65.pdf`.

The source PDFs were read on 2026-09-04.  Exact page/equation locators must be
checked once more against the final bibliography version before submission.

## 2. Kozitsky--Pasurek (KP) DLR theorem

KP assumes a countable embedded lattice, continuous single-site potentials
with a superquadratic lower bound and a common continuous upper bound, and a
summable interaction norm.  Their Theorem 3.1 gives nonemptiness and weak
compactness of the tempered Euclidean DLR set; Theorem 3.2 gives a common
exponential Holder/L2 moment bound, and Theorem 3.3 gives the tempered support
property.  The local specification is Feller on the weighted path spaces.

### Q3LOCK crosswalk

* `Lambda=Z^3` is a regular countable lattice.
* The eight-component mass is `m=chi/hbar^2>0` in the convention
  `[q,p]=i*hbar`.
* Nearest-neighbour spatial coupling is ferromagnetic with `J_yz=c`.
  Expanding `(c/2) sum_<yz> |q_y-q_z|^2` gives the KP form with an onsite
  diagonal contribution absorbed into the local potential.
* The Q3 term is continuous, nonnegative, and quartic.  The negative
  quadratic coefficient and compact source are absorbed by Young inequalities,
  leaving a uniform `A|q|^4-C` lower bound.  The elementary edge estimate
  `(x-y)^2(x^2+y^2)<=4(x^4+y^4)` gives a common continuous quartic upper
  function.
* Finite range implies every KP weighted interaction norm is finite.  The
  source family is compact and the constants used in the KP kernel estimates
  can be chosen uniformly over that family.

This licenses KP only for fixed-source DLR existence/compactness and common
moment/support estimates.  The source-to-zero tangent passage is a
paper-local extension; it is not attributed to KP without displaying the
uniform kernel estimate and its dominated convergence argument.

## 3. Kargol--Kondratiev--Kozitsky (KKK) pressure and Bruch--Falk tools

KKK Proposition 3.9 is a Griffiths moment-to-pressure subgradient statement.
It applies to the scaled log moment generating functions and allows the
second-moment limsup to be bounded by the square of the pressure subgradient
interval.  In Q3LOCK the random variable is the Euclidean time-integrated
collective coordinate

```text
X_L=sum_(y in Lambda_L) integral_0^beta u dot omega_y(tau) d tau,
```

and the exact conversion is
`V^(-1) log E exp(h X_L)=8 beta(P_(beta,L)(h)-P_(beta,L)(0))`.
The factor eight must be retained in the paper and in the independent
verifier.

KKK Proposition 3.18 is the Bruch--Falk inequality for bounded finite-volume
observables.  The Q3LOCK unbounded local coordinate is reached by the smooth
spectral cutoff `R*tanh(Q/R)` and a Duhamel-norm limit; this cutoff argument is
paper-local.

KKK Corollary 3.14, however, explicitly assumes translation **and rotation**
invariance before stating the vector infrared constant.  The Q3LOCK Q3 edge
interaction is nonradial, so that corollary and its O(8) covariance
diagonalization are excluded from the load-bearing proof.  Only the general
Griffiths and Bruch--Falk mechanisms may be cited directly.

## 4. Froehlich--Simon--Spencer (FSS) Gaussian domination

FSS works on finite periodic cubic lattices with a fixed finite-dimensional
spin at each site and a single-spin measure having all quadratic exponential
moments.  Their Gaussian-domination constant is independent of the
single-spin distribution, the number of components, and the internal
symmetry.  The crossing kernel factorization

```text
exp[-c||a-b||^2/2]
 = exp[-c||a||^2/2] exp[-c||b||^2/2] exp[c<a,b>]
```

is positive definite by the symmetric-tensor expansion of `exp[c<a,b>]`.
Therefore the theorem applies at each finite time grid after collecting the
`8N` temporal/component coordinates into one spin.

What FSS does **not** provide for this paper is an infinite-dimensional
path-space transfer theorem or a time-grid limit.  The finite-grid inequality
must be followed by the paper-local covariance/tightness, compact-set
Riemann-sum, normalizer, and shifted-source arguments recorded in the
Q3LOCK grid-to-loop notes.  The only source needed for the infrared estimate
is the time-constant zero-sum spatial source, not an arbitrary L2 edge-field
family.

## 5. Novelty and comparison boundary

The references establish the constituent methods: Euclidean DLR compactness,
Griffiths pressure conversion, Bruch--Falk, reflection positivity and
Gaussian domination.  The repository result is presently framed as a
model-specific composition for the nonradial positive-`lambda` Q3LOCK
interaction, with an explicit sufficient parameter regime and a fixed
collective direction.  No claim is made that this composition is new in the
global literature until a separate systematic search, priority audit, and
referee-level comparison are complete.  The paper must distinguish:

1. imported theorems whose hypotheses are explicitly satisfied;
2. Q3LOCK-specific lemmas (submodularity, finite-grid association passage,
   Hilbert-valued FSS transfer, double-commutator projection and threshold
   algebra); and
3. statements deliberately not obtained (all-parameter phase, extremality,
   common real-time KMS dynamics, ground phase/gap, continuum limit and any
   physical or cosmological interpretation).

## 6. Audit status

The source-scope audit is advanced at T0.  Before an independent claim is
registered, a reviewer must check the exact KP norm convention, the KKK source
normalization and Proposition 3.9 hypotheses, the Bruch--Falk cutoff passage,
and the FSS finite-grid moment assumptions against the final Hamiltonian.  No
claim card, P2 manuscript, release, or PDF is created by this audit.
