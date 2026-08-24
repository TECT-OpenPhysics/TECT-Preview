# EXP-001075 / projected D,delta-D third-coefficient weighted seminorm bridge

## Decision

EXP-001074 supplies the finite pointwise coefficient envelope

```text
|A1| <= (7/8) A^(3/4)
|A0| <= (61/160) A^(3/4)
```

for `A(q,v)=1+q^4+v^4`, in the declared finite model
`chi=hbar=c=1`, `lambda=1/10`, and `|a|<=1/4`.  EXP-001075 does not
promote this pointwise statement to an operator bound.  Instead it isolates
the exact inputs needed for the first QFT-facing seminorm bridge.

Let

```text
Y_sigma = W_a*(A1*partial_q + A0),  sigma in {+,-}
N_beta,#(X)^2 = psi_beta,0(X^*X) + psi_beta,0(XX^*)
```

and assume, on a declared common Q3 core, a two-sided multiplication-
domination statement strong enough to provide the four mixed roots

```text
P_sigma >= N_beta,#(W_a*A^(3/4)*partial_q)
Q_sigma >= N_beta,#(W_a*A^(3/4)).
```

These are hypotheses, not values inferred from the fixture.  The pointwise
majorant and the seminorm triangle then give the conditional algebraic bridge

```text
M_sigma = (7/8) P_sigma + (61/160) Q_sigma
N_beta,#(Y_sigma) <= M_sigma.
```

For the modular companion, introduce independent roots `P_delta_sigma` and
`Q_delta_sigma` for the same domination statement applied to `delta(Y_sigma)`.
No Hamiltonian/modular commutation, equality of domains, or common generator
is assumed.  Its conditional bound is

```text
M_delta_sigma = (7/8) P_delta_sigma + (61/160) Q_delta_sigma.
```

Adding the plus and minus orientations by the seminorm triangle gives

```text
N_beta,#(Y_+ - Y_-) <= M_+ + M_-
N_beta,#(delta(Y_+) - delta(Y_-)) <= M_delta_+ + M_delta_-.
```

The factor `t^3/6` is retained only for the third Taylor boundary term:

```text
N_beta,#(t^3*(Y_+ - Y_-)/6)
  <= (t^3/6)*(M_+ + M_-),
```

with the analogous modular formula.  This is a boundary contribution, not a
positive-time Duhamel remainder or a factorial history estimate.

## Exact fixture and cross-checks

Use the declared test inputs

```text
P_+=5, Q_+=3, P_-=7, Q_-=4
P_delta_+=2, Q_delta_+=1, P_delta_-=3, Q_delta_-=2
t=1/100.
```

The exact derived values are

```text
M_+ = 883/160
M_- = 153/20
M_+ + M_- = 2107/160
M_delta_+ = 341/160
M_delta_- = 271/80
M_delta_+ + M_delta_- = 883/160
t^3/6 = 1/6000000
third two-orientation bound = 2107/960000000
third modular bound = 883/960000000.
```

The primary symbolic lane and the independent Fraction-only lane each pass
22/22 self-tests.  The integrated verifier passes 35/35 with Lean enabled.
Lean R257 compiles with exact rational arithmetic, and the registry metadata
passes with 93 entrypoints and 1374 assertions.

## Adversarial review

1. **Majorant transfer -- UPHELD.** The A1/A0 estimates enter only through an
   explicit two-sided multiplication-domination hypothesis; no operator
   monotonicity is silently inferred.
2. **Two orientations -- UPHELD.** Plus and minus roots stay separate and are
   added by the triangle inequality; no parity equality is assumed.
3. **Moment meaning -- UPHELD.** `P` and `Q` are declared weighted seminorm
   roots, not finite fixture measurements or an unstated higher moment.
4. **Modular companion -- UPHELD.** The delta roots are independent; no
   Hamiltonian/modular commutation or domain identification is assumed.
5. **Time order -- UPHELD.** `t^3/6` is only a third Taylor boundary scale and
   is not a positive-time remainder estimate.
6. **Finite fixture -- UPHELD.** The rational roots test the bridge algebra and
   do not represent volume-uniform Q3 estimates.
7. **Lean -- UPHELD.** R257 checks exact rational arithmetic only; it does not
   formalize states, unbounded domains, modular theory, or limits.
8. **QFT and TECT promotion -- UPHELD.** OS/KMS/GNS, the gap, continuum, C6,
   Sector A, Pre-A, and the canonical A1/R-192 production owner remain open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_seminorm_bridge.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_seminorm_bridge_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_seminorm_bridge_verify.py
lake env lean Tect/R257.lean
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

## Boundary and next gate

This is a T0, claim-nonbearing conditional finite QFT-interface checkpoint.
It does not close the actual mixed moments, multiplication domination on the
common Q3 core, modular domain, positive-time orbit or history, direct `D` or
`delta-D` Cauchy convergence, product/core density, exhaustion independence,
group law, common alpha, Hamiltonian-to-OS identification, KMS/GNS,
continuum, C6, Sector A, Pre-A, TECT production, or a Clay result.

The next live gate is to prove the four mixed moment and multiplication-
domination inputs on the actual common Q3 core, with the modular companion
separately.  If those inputs are not volume/source-uniform or fail on the
declared domain, record the exact obstruction instead of promoting this
conditional bridge.
