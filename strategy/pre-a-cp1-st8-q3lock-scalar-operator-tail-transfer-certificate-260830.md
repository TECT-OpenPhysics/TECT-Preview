# R-445 — Conditional scalar-to-operator tail transfer

## Result and scope

R-445 is a T0, claim-nonbearing finite lemma recorded under EXP-001297 for
T-054 and C6-SPACETIME-SIGNATURE. It keeps the established T-054 forward
method unchanged and only audits the next explicit implication after R-444.
For a finite positive-coordinate nearest-neighbour edge family in a rectangular
three-dimensional box, with `w(e)=2^(-||lower(e)||_1)` and a declared common
constant `C >= 0`, assume the per-edge norm majorant

```
||K_e|| <= C*w(e).
```

The finite triangle inequality then gives

```
||sum_tail K_e|| <= sum_tail ||K_e||
                  <= C*sum_tail w(e)
                  <= C*T(R),
```

where R-444 supplies the scalar ambient majorant
`T(R)=3*(4*R^2+8*R+14)*2^(1-R)` for `R >= 1`.

The finite contract is the exact box range `[2,8]^3`, radii `1..12`, and
majorant constants `1`, `3/2`, and `7/3`. The primary Fraction lane covers
343 boxes, 102900 edges, and 4116 tail rows. The independent lane rebuilds the
same objects without importing the primary implementation. The Lean theorem
`weighted_tail_transfer` proves the abstract finite triangle-inequality step;
`scaled_tail_r1_bound` checks the R-444 arithmetic fixture.

## Evidence

- Primary: `pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer.py --self-test`.
- Independent reconstruction: `pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer_independent.py --self-test`.
- Hostile scope firewall: `pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer_hostile.py --self-test`, 8/8 mutations rejected.
- Integrated verifier: `pre_a_cp1_st8_q3lock_scalar_operator_tail_transfer_verify.py --self-test`.
- Lean: `lake env lean Tect/R445.lean`, PASS with no `sorry`, `admit`, `axiom`, or
  `unsafe` tokens.
- Saved machine evidence is under
  `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-*scalar_operator_tail_transfer/`.

## Assumptions and missing assumptions

The edge family, weight, finite boxes, radius range, and scalar R-444 bound are
frozen. The per-edge Banach/seminorm majorant is an explicit assumption, not a
derived Q3LOCK fact. The additive seminorm obeys the triangle inequality.

Still missing are an actual Q3LOCK commutator/history-tail derivation, a
representation-independent weighted operator domain and common core, uniform
source/cutoff/volume/shape/history constants, exhaustion-Cauchy and common
alpha estimates, OS/KMS/GNS identification, sector coercivity, and physical
empty/continuum conclusions.

## Adversarial review

1. **Could the assumed majorant be silently treated as a Q3LOCK estimate?**
   Rejected: the manifest and every verifier require
   `operator_norm_of_actual_q3_terms=false` and
   `q3lock_commutator_identification=false`.
2. **Could a finite dominated table be promoted to an exhaustion or continuum
   result?** Rejected: the scope firewall keeps exhaustion, common-core,
   common-alpha, continuum, Pre-A and Sector-A flags false.
3. **Could cancellation or a signed sum invalidate the transfer?** Rejected at
   this finite level by the triangle inequality; no cancellation is used, and
   the ambient bound is only conditional on the declared termwise majorant.
4. **Could a later reader mistake this for a physical mass-gap result?**
   Rejected: the non-claims explicitly exclude physical-empty, Yang--Mills and
   mass-gap conclusions, and the hostile lane rejects those promotions.

## Boundary and next gate

R-445 advances only the reusable finite contract. It does not identify the
actual Q3LOCK terms with `K_e`. The next forward gate is therefore an owner-
supplied Q3LOCK-specific per-edge bound on the common weighted operator domain,
followed by a representation-independent common-core check. If that bound is
not supplied, retain R-445 as conditional and do not repeat equivalent finite
tables. No claim tier, negative result, or PDF is issued here.
