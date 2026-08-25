# EXP-001152 — Registered-family full Q3 character double-commutator bound

## Decision

This checkpoint composes two previously registered inputs:

1. EXP-001068 gives the two-sided kinetic character estimate from the uniform
   onsite fifth Gibbs moment.
2. EXP-001061 gives the compact-source endpoint pair third-moment bound.

The missing full force term is supplied by an independent global polynomial
estimate.  Put `S=1+q^4+v^4`.  Since `S>=1`,

```text
|q-v| <= 2 S^(1/4),
|2q^2-qv+v^2| <= 4 S^(1/2),
```

and therefore the Q3 edge force obeys

```text
|B'_xy| <= (2c+4lambda) S^(3/4),
|B'_xy|^4 <= (2c+4lambda)^4 S^3.
```

For the onsite force `G_x=r q_x+g q_x^3`, the registered split
`k_x>=1+gamma q_x^4` gives

```text
|G_x|^4 <= 8 (r^4/gamma + g^4/gamma^3) k_x^5.
```

The EXP-001061 pair bridge controls the `S^3` moment by
`M_pair=9(C0^3+2 a_gamma^3 m5)`.  With at most `z` neighbours,
`|sum_y B'_xy|^4 <= z^3 sum_y |B'_xy|^4`, giving a `z^4` edge factor.

For the declared fixture
`(chi,hbar,g,r,gamma,c,lambda,m5,z,a)=(1,1,3/5,-9/2,1/100,1,1/10,3,6,1/4)`,
the exact derived values are:

* onsite-force fourth coefficient: `1364850`;
* pair third-moment bound: `35834571/64`;
* one-edge fourth bound: `220167604224/5`;
* six-neighbour edge-sum fourth bound: `285337215074304/5`;
* complete onsite-plus-edge force fourth bound:
  `2282697884376432/5`;
* kinetic character second-norm bound: `49153/65536`;
* rational safe force second-norm bound: `285337235547054/5`;
* rational safe full second-norm bound:
  `18699861068811976709/163840`.

The safe force and full bounds deliberately replace square roots by the valid
looser inequality `sqrt(X)<=X` for `X>=1`, followed by
`(u+v)^2<=2(u^2+v^2)`.  They are not claimed sharp.

## Verification

Primary: `190/190` assertions.  Independent Fraction-only lane: `187/187`.
Integrated verifier: `33/33`; Lean R322 compiles.  Both numerical lanes rebuild
the constants independently and check the global polynomial envelopes on the
9-by-9 field grid as a sanity test.  The grid is not used as a substitute for
the analytic inequalities.

## Scope boundary

The closed statement is limited to the registered finite periodic, fixed-beta,
compact-source family and its uniform site translates, conditional on the
registered `m5` and onsite-split authorities.  It is a static second-
commutator input.  It does not establish arbitrary-boundary or all-shape
uniformity, exact CCR/common-core closure, modular-domain transfer, a complete
four-context history, direct `D`/`delta-D` Cauchy, exhaustion independence,
common `alpha_t`, OS/KMS/GNS reconstruction, a gap, continuum, C6, Sector A,
Pre-A or the TECT production owner.

## Adversarial review

1. **Global edge force — UPHELD.**  The edge coefficient `2c+4lambda` is
   derived from elementary global `S` inequalities, not fitted to the grid.
2. **Onsite cubic force — UPHELD.**  Both `q^4` and `q^12` are reduced through
   the registered `k_x` lower bound; the negative quadratic coefficient is not
   dropped with an invalid sign.
3. **Neighbour counting — UPHELD.**  The `z^3` fourth-power sum inequality and
   the `z` edge count are both retained, producing `z^4`.
4. **Moment authority — UPHELD-OPEN.**  Pair `E_xy^3` control is inherited only
   from EXP-001061's registered periodic compact-source scope.  No arbitrary
   boundary or all-shape extension is inferred.
5. **Kinetic/force split — UPHELD.**  The exact shifted-momentum kinetic term
   and the complete onsite-plus-edge force term are kept separate until the
   final triangle inequality.
6. **Orientation — UPHELD.**  Both Weyl-shifted kinetic orientations and the
   commuting configuration-force character legs are included.
7. **Safe constants — UPHELD.**  The reported rational full bound is explicitly
   loose; no sharpness or optimality claim is made.
8. **QFT promotion — UPHELD-OPEN.**  Static control is not history summation,
   direct Cauchy, common dynamics, OS/KMS/GNS, a gap, continuum, C6, Sector A
   or Pre-A closure.
9. **Lean — UPHELD.**  R322 checks exact rational composition only and contains
   no analytic axiom, `sorry`, operator-domain theorem or limit claim.

## Next gate

Insert this complete static second-commutator envelope into a genuinely
two-sided finite-time Duhamel/history estimate on the registered periodic
compact-source word class.  Track the additional product, modular and shape
costs explicitly; do not promote the static coefficient to common `alpha_t`
until that history/Cauchy gate is proved.

## Reproduction

```text
python codes/foundations/pre_a_cp1_st8_q3lock_full_character_double_commutator_bound.py
python codes/foundations/pre_a_cp1_st8_q3lock_full_character_double_commutator_bound_independent.py
python codes/foundations/pre_a_cp1_st8_q3lock_full_character_double_commutator_bound_verify.py
lake env lean verification/lean/Tect/R322.lean
```

Formal integration adds no result, negative record, changelog event, tier
change or PDF.
