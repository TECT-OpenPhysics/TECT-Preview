# Faris--Minlos multidimensional ground-state boundary

Date: 2026-09-07. Exploration: EXP-001651. Task: T-054.
Status: T0, claim_bearing=false, comparison-only, no priority claim.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497. PDF deferred.

## Primary source

W. G. Faris and R. A. Minlos, *A quantum crystal with multidimensional
anharmonic oscillators*, [public PDF](https://math.arizona.edu/~faris/Crystal.pdf).
The source introduces multi-dimensional anharmonic oscillators at lattice
sites, with single-site Hilbert space L^2(R^nu), a nearest-neighbour
symmetric bilinear coupling, and a confining potential comparable to
|x|^(2s), s>1. Its Theorem 1.1 gives a convergent small-coupling cluster
expansion for local ground-state observables in the infinite crystal, with
bounds independent of finite-volume size. The paper explicitly remarks that
related techniques may be usable at nonzero temperature, but that remark is
not a finite-temperature theorem.

## Q3LOCK interface

The source is a useful multidimensional unbounded-oscillator comparator, but
it does not provide the result required by this paper:

* it is a zero-temperature ground-state construction, not a finite-beta
  Euclidean Gibbs/DLR compactness and source-tangent theorem;
* its perturbative parameter is a sufficiently small quadratic coupling,
  whereas Q3LOCK's load-bearing regime uses positive spatial ferromagnetic
  coupling together with a non-radial Q3 onsite locking polynomial and a
  collective source;
* it does not prove continuous-loop FKG, the three-dimensional infrared
  zero-mode subtraction, a strict finite-temperature pressure cusp, or two
  parity-related tempered DLR states.

The older Kargol--Kozitsky asymmetric-potential comparator remains scalar:
its displacement variable is one-dimensional even though its potential may be
asymmetric. Faris--Minlos therefore does not supply a hidden reduction of the
eight-component Q3LOCK polynomial.

## Disposition and nonclaims

Disposition: COMPARISON-ONLY; DOES-NOT-APPLY-DIRECTLY to the Q3LOCK
finite-temperature phase-coexistence theorem. This is not a claim that the
Faris--Minlos method cannot be extended, and the source's nonzero-temperature
remark is not treated as a theorem. No novelty or priority statement follows.

No theorem tier, claim card, TECT sector, or R-497 authority changes. No
ground-state gap, KMS dynamics, continuum limit, extremality, purity,
clustering, physical vacuum, cosmology, Sector A/C6/CP1 closure, or
publication conclusion is added. No paper PDF was generated.

## Next gate

Ask the specialist reviewer to distinguish this ground-state multidimensional
comparison from any finite-temperature continuous-oscillator theorem that
could cover the exact Q3LOCK quantifiers. Keep the literature gate open until
that signed disposition is returned.
