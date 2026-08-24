# EXP-001077 / noncommutative fifth-moment-to-Q transfer obstruction

## Decision

EXP-001076 produced a scalar commuting candidate for the mixed seminorm input

```text
Q_sigma <= 3/2  when m5 = 1,
```

so its squared comparison threshold is `9/4`.  The next required step was to
justify this candidate from an actual noncommutative Q3 form order.  This
checkpoint tests the weaker inference

```text
K = A + P,  A >= 0,  P >= 0,  phi(K^5) <= 1
    => 2*phi(A^(3/2)) <= 9/4.
```

That inference is false for a finite exact matrix family.  It is a route-local
obstruction, not a Q3 counterexample.

## Exact witness

For a Pell pair `(t,s)` satisfying `t^2 - 2*s^2 = -1`, let `L=t^2` and set

```text
K   = diag(1,L)
A   = (1/2) [[1,t],[t,L]] = (1/2) (1,t)^T (1,t)
P   = (1/2) [[1,-t],[-t,L]] = (1/2) (1,-t)^T (1,-t)
rho = diag(1,0).
```

The rank-one factors give `A >= 0` and `P >= 0`, while direct addition gives
`K=A+P`.  The state `rho` is positive and trace one but is deliberately
nontracial with respect to `A`; no Gibbs interpretation is claimed.  The Pell
identity gives

```text
A^2 = s^2 A,
A^(3/2) = s A,
phi_rho(K^5) = 1,
2*phi_rho(A^(3/2)) = s.
```

The three exact fixtures are:

```text
(t,s)       Q^2       Q^2/(9/4)
(7,5)         5            20/9
(41,29)      29           116/9
(239,169)   169           676/9
```

Already the first row has `Q^2=5>9/4` despite the unit fifth moment.  The
growth rows show that the issue is structural rather than a rounding edge.

## Adversarial review

1. **Positivity — UPHELD.** Both source forms are explicit rank-one matrices;
   their sum is the positive diagonal `K`.
2. **State — UPHELD.** `rho` is positive trace one and nontracial.  The witness
   does not silently replace it with a Gibbs trace.
3. **Moment — UPHELD.** The fifth moment and the target power are exact matrix
   identities, recomputed in SymPy and in an independent Fraction-only lane.
4. **Candidate comparison — UPHELD.** The threshold `9/4` is the square of
   EXP-001076's declared `m5=1` candidate `Q_sigma<=3/2`.
5. **Growth — UPHELD.** Pell inputs, powers, and ratios are exact rationals;
   no floating-point cut-off or hardcoded derived decimal is used.
6. **Q3 identification — UPHELD.** The family is abstract finite-dimensional
   form data, not a canonical Q3 Hamiltonian, local field algebra, or Gibbs
   state.
7. **Lean — UPHELD.** R259 proves the rational fixtures and inequalities only;
   it does not encode the Q3 representation or promote the obstruction to QFT.
8. **QFT promotion — UPHELD.** OS/KMS/GNS, the gap, continuum, C6, Sector A,
   Pre-A, and the TECT A1/R-192 production owner are unchanged and open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_noncommutative_moment_transfer_obstruction.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_noncommutative_moment_transfer_obstruction_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_noncommutative_moment_transfer_obstruction_verify.py
lake env lean Tect/R259.lean
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

The primary and independent lanes each pass `48/48`; integrated verification
passes `18/18` with Lean R259 passing.  The registry reports 95 Lean entrypoints
and 1420 assertions after the addition.

## Boundary and next gate

This is a T0, claim-nonbearing finite obstruction.  It refutes only the
form-order-plus-one-nontracial-moment shortcut.  It does not refute the actual
Q3 Gibbs-weighted transfer and does not close any QFT or Clay gate.

The next gate is an actual Gibbs-weighted noncommutative Holder/commutator
theorem on the common Q3 core, including the multiplication and domain
hypotheses needed for `P_sigma` and `Q_sigma`.  If that stronger statement is
also false, its obstruction must be recorded separately; until then the
EXP-001076 scalar values remain candidates only.
