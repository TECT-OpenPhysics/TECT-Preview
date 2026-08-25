# EXP-001095 finite-particle core-domain certificate

## Decision

For the algebraic finite-particle core `D_fin`, a fixed vector supported on
levels `0` through `K` is annihilated by the truncated-CCR top projector as
soon as the oscillator dimension satisfies `n >= K+2`. Consequently

`([q_n,p_n]-iI)e_k = 0` for every `k <= K` and `n >= K+2`.

Thus the exact truncated CCR defect converges strongly to zero on each fixed
finite-particle core vector. This is weaker than a uniform estimate for evolved
Q3 histories or Gibbs-weighted vectors.

## Reproduction

The primary lane passes `93/93`, the independent lane passes `62/62`, and the
integrated stored result passes `13/13` with Lean `R276`. The dimensions and
support levels are manifest inputs. The top-level boundary witness remains
nonzero at `k=n-1`, so the statement is about fixed core vectors, not uniform
operator-norm convergence.

## Remaining QFT gate

The missing step is a source-, volume-, orientation-, and history-uniform
weighted tail estimate showing that the selected Q3 local carrier remains in a
domain where the `n`-weighted top boundary vanishes. Without that estimate one
cannot exchange oscillator cutoff with dynamics, Gibbs state, volume, or time
limits. The result does not close the common core, modular history, common
alpha, OS/KMS/GNS, gap, continuum, C6, Sector A, or Pre-A.

## Lean scope

`verification/lean/Tect/R276.lean` checks only the natural-number implication
`k <= K` and `K+1 < n` imply zero top overlap, plus finite boundary fixtures.
It does not encode Q3 evolution, Gibbs tails, operator closures, or QFT.
