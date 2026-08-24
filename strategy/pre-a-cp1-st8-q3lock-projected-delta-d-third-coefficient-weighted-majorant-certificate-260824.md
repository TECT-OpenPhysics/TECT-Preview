# EXP-001074 / projected D,delta-D third-coefficient weighted majorant

## Decision

The exact finite CCR coefficient from EXP-001073 can be placed in a
derivative-weighted pointwise envelope on the declared polynomial core.  This
is a coefficient majorant, not a positive-time orbit theorem.

For the canonical bond

```text
B(q,v)=c*(q-v)^2/2+lambda*(q-v)^2*(q^2+v^2)/4
```

and the boundary character `W_a=exp(i*a*q/hbar)`, EXP-001073 gives

```text
D'''(0)=W_a*(A1*partial_q+A0)
A1=-a*F'/chi^2-3*i*a^2*F/(chi^2*hbar)
A0=-a*F''/(2*chi^2)-2*i*a^2*F'/(chi^2*hbar)+3*a^3*F/(2*chi^2*hbar^2)
```

Specialise only the coefficient audit to `chi=hbar=c=1`, `lambda=1/10` and
`|a|<=1/4`.  With `A(q,v)=1+q^4+v^4`, the four real component polynomials
have coefficient majorants

```text
|Re A1| <= (17/40) A^(3/4)
|Im A1| <= (9/20) A^(3/4)
|Re A0| <= (27/160) A^(3/4)
|Im A0| <= (17/80) A^(3/4).
```

Every monomial has field degree at most three.  For nonnegative
`x=q^4`, `y=v^4`, the weighted AM-GM inequality gives
`|q|^i*|v|^j <= (1+q^4+v^4)^((i+j)/4) <= A^(3/4)` whenever
`i+j<=3`.  Multiplying each coefficient by the declared source-radius power
and summing gives the four displayed constants.  The triangle inequality then
gives

```text
|A1| <= (7/8) A^(3/4)
|A0| <= (61/160) A^(3/4).
```

Consequently, for a polynomial-core test function `f`, the pointwise estimate

```text
|D'''(0)f| <= A^(3/4)*((7/8)*|partial_q f|+(61/160)*|f|)
```

holds in this finite coefficient model because `|W_a|=1`.  It does not assert
that the weighted multiplication or derivative is bounded in a Gibbs,
modular, GNS, or thermodynamic topology.

## Exact fixture and independent checks

At `(q,v,a)=(3,-2,1/4)`,

```text
A1=-59/40-(9/4)i
A0=-3/160-(59/80)i
A(q,v)=98.
```

The `6 x 6 x 2` rational grid has 72 points and exact component ceilings
`59/40`, `9/4`, `9/80`, and `59/80`.  The primary symbolic lane derives the
component polynomials and coefficient sums.  The independent lane rebuilds
the bond, differentiates a rational polynomial dictionary, and evaluates all
grid points using `Fraction` only.  Lean R256 checks the rational majorants,
their sums, the selected weight, and the derivative-weighted fixture.

## Adversarial review

1. **Coefficient source — UPHELD.** A1 and A0 are reused exactly from
   EXP-001073; no fourth generator or unregistered background derivative is
   added.
2. **All-real versus grid — UPHELD.** The all-real conclusion comes from the
   degree/majorant argument; the grid is only a reproducible self-test.
3. **Source radius — UPHELD.** The constants use `|a|<=1/4` and do not cover
   unrestricted characters.
4. **Complex norm — UPHELD.** The complex estimate uses the conservative
   `|z|<=|Re z|+|Im z|` triangle bound.
5. **Derivative domain — UPHELD.** The statement is pointwise on the
   polynomial CCR core, not an operator-closure or modular-domain theorem.
6. **Lean — UPHELD.** R256 is exact rational arithmetic and does not formalise
   unbounded domains, Gibbs traces, or limits.
7. **Orbit promotion — UPHELD.** A boundary coefficient is not summed into an
   evolved-force, factorial-history, or Duhamel estimate.
8. **QFT and TECT promotion — UPHELD.** OS/KMS/GNS, the gap, continuum, C6,
   Sector A, Pre-A, and the canonical A1/R-192 production owner remain open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_majorant.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_majorant_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_weighted_majorant_verify.py
lake env lean Tect/R256.lean
```

## Boundary and next gate

This is a T0, claim-nonbearing finite CCR coefficient checkpoint.  It does not
close a positive-time evolved-force estimate, modular-domain control, the
actual Q3 four-context history, direct `D` or `delta-D` Cauchy convergence,
exhaustion independence, Hamiltonian-to-OS identification, KMS/GNS, the
continuum, C6, Sector A, Pre-A, TECT production, or a Clay result.

The next live step is to use this derivative-weighted seed only inside a
separately proved mixed orbit estimate, with an explicit modular-domain input
and history recurrence.  If those inputs cannot be made volume/source
uniform, the obstruction must be recorded rather than inferred away.
