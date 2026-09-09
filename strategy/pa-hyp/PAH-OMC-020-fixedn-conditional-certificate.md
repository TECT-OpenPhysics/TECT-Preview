# PAH-OMC-020 fixed-n conditional temporal implication

This certificate records one bounded advance inside PAH-OMC-020.  It is a
conditional implication and is not the fixed-n theorem by itself.  The
functional, directed rates, state, carrier, external Markov time and the
`j`-before-`n` order are exactly the pinned PAH-001/OMC-016/OMC-018 sources.

## Statement

Fix `n >= 2`, a finite `T`, and `f,g` in the preregistered bounded,
gauge-invariant, globally amplitude-l1-Lipschitz finite-prefix cylinder
domain.  Keep the direct sampled observable `S_(n,j)` and the original finite
stationary generator `L_(n,j)`.  Let `A_n` be the exact PH/LK/AP part of the
same generator at continuous amplitudes and let `Q_n(t)` be its finite label
fibre semigroup.  The following implication is certified:

* if the inherited R-509/OMC-016 half-open cell and stationary-tail theorem is
  applied to the uniformly time-equicontinuous family `Q_n(t)g_K`,
* if the R-511 radial residual estimate applies to `Q_n(s)g_K` on the compact
  amplitude cutoff, and
* if the finite fibre rates have the compact amplitude modulus supplied by
  finite-state variation of constants,

then the three displayed terms (F7), (F8) and (F9) in the pinned temporal
work note imply

    sup_(0 <= t <= T) | C_(n,j)(f,g;t)
       - <f,Q_n(t)g>_(nu_n) | -> 0

as `j -> infinity`, followed by the cutoff removal `K -> infinity`.

The proof uses no conditional generator averaging, rate fitting, new carrier,
time acceleration, changed functional or changed limit order.  The endpoint
cell and the original labelled counting state remain included.

## Proof spine

Choose the bounded Lipschitz cutoff `chi_K` and write `g_K=chi_K g`.  The
finite label set at fixed `n` and compact amplitude box `B_(K+1)` make every
source rate continuous with a finite maximum and a finite first derivative
bound.  For a finite generator matrix `A_n(r)`, the variation-of-constants
identity gives a modulus for `exp(t A_n(r))` that is uniform on
`0 <= t <= T` and `r in B_(K+1)`.  Multiplication by the bounded Lipschitz
`g_K` therefore supplies the finite constant used in the radial residual
estimate.

The R-511 inverse-transport estimate then gives (F7), uniformly in time,
with a finite support-dependent constant.  Both finite semigroups are
stationary Markov contractions, so the stationary L1 tail theorem gives
(F8).  The R-509/OMC-016 endpoint-inclusive cell identity applies to each
fixed time.  The finite modulus provides a finite time net, so the same
cell convergence is uniform on `[0,T]`, giving (F9).  First let `j` tend to
infinity and then use the fixed-`n` tail theorem to let `K` tend to infinity.
The triangle inequality yields the displayed implication.

This is an implication from explicitly named inherited hypotheses.  It does
not silently promote the compact modulus, the Duhamel domain, or the
all-test cell theorem beyond their registered scopes.

## Verification

Primary, non-importing independent and hostile lanes are stored under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-fixedn-conditional/`.
Run the integrated verifier with:

    python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_verify.py
    python -X utf8 verification/scripts/pah_omc020_fixedn_temporal_verify.py --check

The primary lane checks all source pins, the F7--F10 quantifier structure,
the endpoint and stationary-tail requirements, finite reversible-fibre
algebra and exact rational diagnostic bounds.  The independent lane rebuilds
the fibre and error algebra with tuples and `Fraction` arithmetic without
importing the primary verifier.  The hostile lane rejects pointwise-tail
shortcuts, reversed order, full-exponent mutations and physical promotion.
The existing `PahOmc020.lean` source compiles in the same integrated run; its
scope remains finite algebra only.

## Boundary

The result is `AUXILIARY_SUPPORT` with `temporal_verdict=IN_PROGRESS`.
The certificate does not discharge the inherited all-test theorem, a full
common-Hilbert `U_n`, N2b weak liminf, N2c/N4 boundary escape, N2d minimal-form
identification, or the anchored `n` passage.  It therefore does not prove
PAH-OMC-020 completion and does not alter T-054.

There is no physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap,
Yang--Mills or TOE conclusion.  External Markov time remains a stochastic
parameter.
