# EXP-001094 truncated-CCR boundary certificate

## Decision

The finite oscillator truncation has an exact boundary defect

`[q_n,p_n] = i (I - n P_top)`,

so

`[q_n,p_n] - i I = -i n P_top` and
`||[q_n,p_n]-iI|| = n`.

For a cutoff vector `psi_n`, the defect acts as
`-i n P_top psi_n`. Therefore a common-core transfer must prove the
weighted top-state condition `n |<top_n,psi_n>| -> 0`; in a squared Gibbs or
Hilbert norm this becomes the stronger-looking condition
`n^2 <psi_n,P_top psi_n> -> 0`.

## Reproduction

The primary lane passes `37/37`, the independently reconstructed lane passes
`31/31`, and the integrated verifier passes `17/17` with Lean `R275`.
The tested dimensions are the manifest inputs `n=2,3,4,6,8`. Every row checks
the exact residual matrix, its operator norm, its top-state action, its
bottom-state annihilation, and rank one. The independent lane initially
exposed a reversed momentum convention; that implementation error was
corrected before the final PASS and is retained as an adversarial review
lesson rather than hidden.

## QFT boundary

This is a T0, claim-nonbearing common-core interface. It proves neither the
actual unbounded Q3 domain transfer nor a source/volume-uniform modular-history
estimate. It does not close all-shape exhaustion, common alpha, Hamiltonian to
OS/KMS identification, GNS gap, continuum, C6, Sector A, Pre-A, TECT
production, or a Clay problem.

The result does not show that the canonical Q3 common core fails. It shows that
finite matrix CCR identities cannot be used in that proof without an explicit
top-boundary/domain estimate. The next legal step is to prove the weighted tail
condition for the chosen local carrier or record its route-specific failure.

## Lean scope

`verification/lean/Tect/R275.lean` checks exact rational defect coefficients,
their squared values, and the scaled tail fixtures. It does not formalize
infinite-dimensional operator domains, Gibbs limits, modular histories, or QFT
reconstruction.
