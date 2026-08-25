# EXP-001124 — static dual-tail identity for a commuting coordinate character

## Decision

Let `phi_A(X)=phi(A* X A)` with `A` unitary, and let `W=W*` be a bounded
coordinate cutoff tail satisfying `[A,W]=0`.  Then

```text
phi_A(W^2)=phi(A*W^2A)=phi(W^2).
```

Both legs of the two-sided seminorm therefore agree in the reference and dual
states.  The primary SymPy lane and the independent exact-Fraction lane pass,
and the integrated verifier passes with Lean R295.

The fixture uses a nontrivial rational rotation on a two-dimensional degenerate
tail block, a normalized noncommuting density matrix, and
`W=diag(1,1,-2)`.  The reference and dual tail squares are both exactly `1`.

## QFT-facing meaning

For the finite Q3 cutoff in EXP-001123, the local configuration character and
the bounded coordinate tail commute.  The static dual-tail hypothesis is thus
not an additional estimate for this carrier: the reference tail can be reused
exactly.  This does not control the evolved `D_sigma(t)` or
`delta_H D_sigma(t)`, because real-time evolution generally destroys the
coordinate commutation.

## Adversarial review

1. **Commutation — UPHELD.** The identity is applied only when `[A,W]=0`.
2. **State definition — UPHELD.** The dual state is defined by conjugation, so
   the argument needs no unlicensed trace cyclicity.
3. **Self-adjointness — UPHELD.** `W=W*` is explicit before reducing both
   seminorm legs to `W^2`.
4. **Evolved observable — UPHELD-OPEN.** No equality is asserted for evolved
   differences or modular derivatives.
5. **Uniformity — UPHELD-OPEN.** This removes only a duplicated static tail
   input; source, volume, beta, history, and exhaustion estimates remain open.
6. **Lean — UPHELD.** R295 checks the rational fixture and scope markers only,
   not a general C*-state theorem.
7. **QFT promotion — UPHELD-OPEN.** Common alpha, OS/KMS/GNS, gap, continuum,
   C6, Sector A and Pre-A remain open.

## Reproducibility

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_dual_tail_commuting_character_identity/integrated.json
```

Lean cross-check: `lake env lean Tect/R295.lean` from `verification/lean/`.

## Boundary and next gate

The live route still requires a dual estimate for the time-evolved `D` and
`delta_H D` on one unbounded common core, followed by exhaustion and common-
alpha identification.  The exact static identity should be used to avoid
duplicating a reference tail assumption in that next proof, but not to skip
the evolved-state estimate.

