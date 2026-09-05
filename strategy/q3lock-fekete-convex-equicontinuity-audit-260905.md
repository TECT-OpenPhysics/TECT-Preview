# Q3LOCK multidimensional Fekete and moving-temperature convexity audit

**Status:** T0 proof-text audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Related result:** R-498 (periodic/open seam and min--max audit)  
**PDF:** deferred until mathematical content freeze, external review, and final release review

## 1. Question and strict boundary

EXP-000780 uses two analytic bridges after the finite-volume form estimates:
the multidimensional Fekete argument for even open rectangles and a convexity
argument that absorbs the moving inverse temperature `beta*(1+eta)` in the
periodic/open heat-trace comparison.  This audit writes those bridges as
standalone lemmas and checks the signs, remainder volumes, parity convention,
and temperature interval needed by the argument.

The audit is not a new pressure theorem.  It does not independently establish
the EXP-000780 form-domain hypotheses, the finite-volume linear bounds, or the
periodic seam inequality; R-498 checks only the finite seam algebra and its
scaling.  It supplies no cusp, phase, DLR multiplicity, or publication claim.

## 2. Even rectangular semigroup and the two Fekete directions

Let

```text
E = {(L1,L2,L3): each Li is a positive even integer},
|L| = L1*L2*L3.
```

For fixed source `J`, write `A(L)=E_0^op(L,J)` and
`B_beta(L)=log Z_L^op(beta,J)`.  Cutting a rectangle across a coordinate
plane deletes only nonnegative spatial difference squares.  The common
polynomial form therefore gives the two inequalities used by EXP-000780:

```text
A(L+M) >= A(L) + A(M),
B_beta(L+M) <= B_beta(L) + B_beta(M),
```

whenever the rectangles are concatenated along one coordinate.  The first is
superadditivity of the ground energy and the second is subadditivity of the
log partition function.  The min--max eigenvalue ordering is the source of the
second inequality; no operator monotonicity of `exp(-beta H)` is used.

The finite-volume source coercivity and product trial in EXP-000780 supply
constants `C_A,C_B<infinity`, locally uniform on compact source sets, such
that

```text
-C_A*|L| <= A(L) <= C_A*|L|,
-C_B*|L| <= B_beta(L) <= C_B*|L|.
```

Only the lower bound on `A` and the upper bound on `B_beta` are needed for the
remainder estimates below; the opposite bounds make the corresponding
supremum or infimum finite.

## 3. Explicit three-dimensional tiling

Fix a block `M=(M1,M2,M3)` in `E` and a large even rectangle `L`.  Set

```text
qi = floor(Li/Mi),
ri = Li - qi*Mi,
Ti = qi*Mi,
V = |L|,
Vtile = T1*T2*T3,
Vrem = V - Vtile.
```

Every nonzero `ri` is even.  Partition each coordinate into `qi` intervals of
length `Mi` and, when present, one interval of length `ri`.  Cartesian products
of these intervals form admissible even rectangles.  The full-block products
give exactly `q1*q2*q3` copies of `M`; all other products have total volume
`Vrem`.  The elementary product estimate is

```text
0 <= Vrem/V = 1 - product_i(Ti/Li)
             <= sum_i ri/Li
             < sum_i Mi/Li.
```

Repeated use of superadditivity and the lower bound on each remainder block
gives

```text
A(L)/V >= (Vtile/V)*(A(M)/|M|) - C_A*(Vrem/V).       (3.1)
```

The analogous repeated subadditivity and upper bound give

```text
B_beta(L)/V <= (Vtile/V)*(B_beta(M)/|M|)
               + C_B*(Vrem/V).                       (3.2)
```

For a fixed `M`, `Vtile/V` tends to one and `Vrem/V` tends to zero as all
three side lengths tend independently to infinity.  Since every normalized
finite value is bounded above by `sup_M A(M)/|M|`, (3.1) proves the
superadditive limit equals that supremum.  Since every normalized finite value
is bounded below by `inf_M B_beta(M)/|M|`, (3.2) proves the subadditive limit
equals that infimum.  The restriction to even side lengths is preserved at
every step; no odd remainder is silently introduced.

After division by the eight fine oscillators per coarse cell, these are the
open pressure and ground-density limits in the EXP-000780 normalization.

## 4. Convex equicontinuity for the moving beta

For an open rectangle define

```text
a_L(beta,J) = |L|^(-1) log Z_L^op(beta,J).
```

At fixed `J`, `a_L` is convex in `beta`: its second derivative is the finite
volume energy variance.  Let `[beta_minus,beta_plus]` be a compact interval
with `0<beta_minus<beta_plus`, and let `K` be a compact source set.  The
EXP-000780 coercive lower comparison and product trace upper comparison give
finite constants `m_K,M_K`, independent of `L`, with

```text
m_K <= a_L(beta,J) <= M_K
```

for `(beta,J)` in this rectangle.  For an interior `beta`, put
`d_beta=min(beta-beta_minus,beta_plus-beta)`.  Secant monotonicity for a convex
function gives, for `|h|<=d_beta`,

```text
|a_L(beta+h,J)-a_L(beta,J)|
    <= (M_K-m_K)*|h|/d_beta.                          (4.1)
```

The constant is uniform in `L` and in `J in K`.  In the seam comparison choose
`eta=L^(-1/2)` and `h=beta*eta`.  For sufficiently large `L`, `h<=d_beta`, so
(4.1) yields an `O(eta)` moving-temperature error.  Combined with R-498's
finite form sandwich,

```text
exp(-beta*D_L) Z_L^op(beta*(1+eta),J)
    <= Z_L^per(beta,J) <= Z_L^op(beta,J),
```

and `D_L/|L|=O(eta)+O(L^(-1)/(eta))`, the periodic and open log-density
limits agree at fixed positive beta, provided the EXP-000780 common form core,
coercive bounds, and open limit are accepted.

The temperature argument is local in the interior of `(0,infinity)`; it does
not justify a uniform statement as `beta` approaches zero.  It also does not
interchange a source limit with a volume limit.

## 5. Independent executable evidence

The auxiliary verifier is

```text
verification/scripts/q3lock_fekete_convex_equicontinuity_audit.py
```

Run from the repository root with:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_fekete_convex_equicontinuity_audit.py
```

The verifier constructs explicit even tilings for several block and large-box
families, checks exact volume partition and the super/subadditive remainder
inequalities on rational synthetic envelopes, evaluates the convex secant
bound on piecewise-linear convex functions, and checks the moving-temperature
seam scale.  It derives all tile counts, remainder volumes, convex constants,
and seam factors from the declared inputs.  The result JSON records the full
assertion rows and source hash; it is a diagnostic fixture, not a proof of the
analytic hypotheses.

## 6. Adversarial checks

| Objection | Disposition |
|---|---|
| A one-dimensional Fekete statement can be quoted without a three-dimensional tiling | **UPHELD AS FALSE:** the product partition and remainder estimate (3.1)--(3.2) are required. |
| An odd remainder can be discarded because it is a boundary layer | **UPHELD AS FALSE:** evenness of every `ri` is checked and odd pieces are rejected. |
| Superadditivity alone controls the remainder contribution | **UPHELD AS FALSE:** the linear lower bound on `A` is used explicitly. |
| Subadditivity alone controls the remainder contribution | **UPHELD AS FALSE:** the linear upper bound on `B_beta` is used explicitly. |
| Pointwise pressure convergence automatically controls `beta*(1+eta)` | **UPHELD AS FALSE:** the interior convex secant estimate (4.1) is required. |
| The convex Lipschitz constant is uniform up to `beta=0` | **UPHELD AS FALSE:** it depends on the interior distance `d_beta`. |
| The finite tiling and convex fixtures prove the EXP-000780 pressure theorem | **UPHELD AS FALSE:** common form-domain, coercivity, trace, and analytic limit inputs remain conditional. |

## 7. Disposition and next gate

The explicit even-box tiling and moving-temperature convex estimate are
consistent with the EXP-000780 proof spine under its stated form and linear
bound hypotheses.  This advances the proof-text audit of P-02 but does not
promote the pressure result or close the paper.

The next gate is an independent line-by-line acceptance that the actual
EXP-000780 open Hamiltonians satisfy the common form core, the min--max trace
ordering, the locally uniform compact-source bounds, and the multidimensional
Fekete hypotheses used here.  The P-06/P-09, KKK, source-window, and external
referee gates remain open.

## 8. Explicit nonclaims

No unconditional pressure theorem, strict cusp, positive-lambda phase theorem,
DLR multiplicity, extremality, purity, clustering, real-time dynamics, KMS
state, ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, Sector A, CP1, C6, or Pre-A conclusion is
asserted.  No manuscript, submission, upload, release, tag, or PDF is created.
