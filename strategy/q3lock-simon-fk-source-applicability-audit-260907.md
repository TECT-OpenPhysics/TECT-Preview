# Q3LOCK Simon Feynman--Kac source-applicability audit

Date: 2026-09-07. Exploration: EXP-001626. Task: T-054.
Status: T0, claim_bearing=false, conditional source and normalization audit.
The sole Q3LOCK authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
This note does not promote the theorem, close a proof-audit gate, or create a
paper PDF.

## Primary source and exact scope

The source is B. Simon, *A Feynman--Kac Formula for Unbounded Semigroups*,
arXiv:math-ph/9907022v1, https://arxiv.org/pdf/math-ph/9907022v1.

The manuscript uses Theorem 1.1 and equations (1.1)--(1.3), printed page 2.
That theorem assumes a continuous potential on finite-dimensional Euclidean
space which is bounded below and the kinetic operator `-Delta/2`.  Simon's
stronger Theorem 1.2 treats the lower bound (1.4) and compactly supported test
vectors, but it is not needed for the Q3LOCK finite-volume application.

## Hypothesis map

| Source requirement | Q3LOCK finite-volume check | Disposition |
|---|---|---|
| Finite Euclidean dimension | `D=8V` for fixed even spatial volume | Satisfied conditionally |
| Kinetic term `-Delta/2` | The unitary scaling `z=sqrt(m) q` maps `-Delta_q/(2m)` to `-Delta_z/2`; the unitary amplitude is `m^(-D/4)` | Exact |
| Continuous potential bounded below | `U_{L,h}(z/sqrt(m))` is a polynomial; the retained quartic dominates the negative quadratic and linear source terms at every fixed `L,h` | Exact at fixed finite volume/source |
| Positive finite time | `t=beta>0` | Exact |
| Absolute kernel normalization | The coordinate change restores `(m/(2 pi beta))^(D/2)` in the original coordinates | Exact |

The source therefore supports the free-bridge heat-kernel identity used by
the manuscript at the finite-volume level.  It does not by itself prove the
harmonic split, mesh limit, thermodynamic pressure limit, or DLR statement.

## Harmonic reweighting and absolute trace

The manuscript defines the normalized harmonic bridge by multiplying the free
bridge by

`exp(-integral a |omega(t)|^2/2 dt)`

and dividing by the corresponding free expectation.  Applying the same
finite-dimensional formula to the harmonic operator identifies that
denominator with `K_a/K_0`.  The residual `R_{a,h}` has a finite lower bound,
so the bridge factor is bounded by `exp(-beta inf R_{a,h})`.

The manuscript then uses monotone form convergence for upper truncations of
the residual, symmetry of the positive semigroup kernel, and Tonelli to get

`integral K_H(beta;q,q) dq = ||exp(-beta H/2)||_HS^2 = Tr exp(-beta H)`.

This is the correct route to the absolute partition function rather than a
normalized correlation formula.  The trace bound is independently supplied
by the form inequality `H >= H_a - V C`, not by operator monotonicity of the
exponential.

## Adversarial checks

1. A mass-one convention cannot be inserted: omitting the `sqrt(m)` change
   loses both the kinetic normalization and the original-coordinate heat
   kernel prefactor.
2. Theorem 1.1 cannot be invoked merely from a polynomial expression: the
   fixed-volume lower bound must be stated before applying it.  The manuscript
   supplies that bound in `eq:residual-lower`.
3. Simon's Theorem 1.1 alone does not justify an unbounded residual without
   the manuscript's truncation and form-limit argument; that interface remains
   open to independent review.
4. A normalized harmonic path law does not determine an absolute trace.  The
   factor `Z_a` and the diagonal-kernel/Tonelli step must remain visible.
5. This source contains no spatial thermodynamic limit, DLR compactness,
   FKG, infrared, cusp, or phase-coexistence conclusion.

## Remaining acceptance boundary

At internal level the mass, dimension, lower-bound, and absolute-normalization
interfaces are consistent with Simon's Theorem 1.1.  The following remain
OPEN in `proof-audit.md`: the form-core and monotone-form passage for the
unbounded residual, kernel continuity and mesh identification, and the
independent acceptance of the complete finite-volume argument.  This audit
does not change the source ledger's conditional status or the literature and
mathematics signatures.

No priority claim, novelty certificate, real-time KMS statement, ground-state
gap, continuum limit, physical vacuum, C6, CP1, or Sector A conclusion follows.
