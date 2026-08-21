# R-188 signed Jensen-defect telescope Lean cross-check

Version: R-188 v1.0  
Claim: `A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION`  
Task: `T-050`  
Tier: T0, claim-nonbearing  
Exploration: `EXP-000903`

## 1. Scope and question

R-081 identifies the nonlinear adapted coefficient split

`d_j H(A*) = integral_0^1 DH(a_(j-1)+t D_j) D_j dt + (J_j-J_(j-1))`,

where `a_j=P_j A*` and `J_j=P_j H(A*)-H(a_j)`. R-187 shows that the
conditional first variation can vanish while a root-square innovation remains.
This package asks a narrower algebraic question: in the finite quadratic
coefficient fixture, does the signed Jensen-defect increment telescope with the
secant to the endpoint difference, and does an absolute first-defect payment
artificially charge a strictly positive amount?

The answer is yes. This is a finite diagnostic for the signed complete packet,
not a production adapted-NEAR estimate.

## 2. Exact fixture

Take two independent Rademacher values `e1,e2` in `{-1,1}`, `c=2/5`, and
`A=e2(1+c e1)`. Let `H(x)=x^2`, with the trivial, first-root, and full
filtrations. The conditional quadratic values are

| object | exact value |
|---|---:|
| `J_0=E[A^2]` | `29/25` |
| `J_1(e1=-1)` | `9/25` |
| `J_1(e1=1)` | `49/25` |
| `J_2(e1=-1,e2=+-1)` | `9/25` |
| `J_2(e1=1,e2=+-1)` | `49/25` |
| first defect increment at `e1=-1` | `-4/5` |
| first defect increment at `e1=1` | `4/5` |
| second defect increment | `0` on every atom |

The first secant is zero because both `a_0` and `a_1` vanish. The second
secant is `A^2`; its Jensen defect increment is `-J_1`.

## 3. Signed telescope

For every rational `c,e1,e2`, the Lean theorem
`jensen_defect_telescope` proves

`dH1(c,e1)+dH2(c,e1,e2) = J_2(c,e1,e2)-J_0(c)`.

At `c=2/5`, the four-atom endpoint mean is exactly zero, while the mean
absolute value of the first Jensen-defect increment is exactly `4/5 > 0`.
Thus summing the signed packet can cancel at the endpoint, whereas an absolute
rootwise payment spends a nonzero amount that is absent from the signed mean.
The Lean theorem `secant_defect_recombination_fixture` also checks the exact
secant-plus-defect decomposition at both active roots.

## 4. Independent verification

The pinned source `verification/lean/Tect/R188.lean` compiles with
`leanprover/lean4:v4.32.1` and Mathlib. The primary lane derives all values from
the manifest with `Fraction` arithmetic and compiles the Lean entrypoint. The
independent lane uses only Python standard-library `Fraction` arithmetic. The
integrated lane checks source hashes, theorem markers, AST/import independence,
all eight hostile mutations, append-only EXP/event linkage, generated counts,
and stored-child freshness.

## 5. Adversarial review

1. **"The endpoint cancellation proves production positivity."** UPHELD as an
   objection. The fixture proves only an algebraic telescope; no production
   coefficient map, covariance root, heat lift, spatial response, or lower
   bound is supplied.
2. **"The positive absolute defect can be discarded because its mean is zero."
   UPHELD as a route warning. Its absolute mean is `4/5`, so discarding it
   requires the signed complete packet, not a rootwise absolute estimate.
3. **"The quadratic fixture is the full rational production coefficient."
   UPHELD as a scope objection. It is a canonical diagnostic for the R-081
   split, not an identification of the A1 production owner.
4. **"Temporal Douglas or overlap algebra now closes the route."** UPHELD as
   an overclaim objection. The production adapted operator and uniform
   overlap-stable packet estimate remain absent.

## 6. Boundary and next obligation

`A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION`,
`A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE`, and `OVERLAP_src` remain open.
R-188 does not prove root-resolved FAR, the complete signed NEAR owner, a
progressive/revisit theorem, Nelson, an interacting measure, any removal or
continuum limit, Sector-A, Pre-A, or a tier/gate change. The next analytic step
is to insert this signed telescope into one hash-pinned production cylinder
and either prove the full square-trace-forest cancellation or produce a
production-specific counterexample. No R-188 PDF is issued.
