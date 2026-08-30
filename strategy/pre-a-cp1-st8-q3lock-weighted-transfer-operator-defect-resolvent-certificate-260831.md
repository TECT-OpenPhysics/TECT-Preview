# R-456 certificate: weighted positive transfer-operator defect-resolvent envelope

## Identity and route role

- Result: `R-456`
- Candidate: `PA-CP1-ST8-Q3LOCK-WEIGHTED-TRANSFER-OPERATOR-DEFECT-RESOLVENT-v0`
- Exploration: `EXP-001329`
- Task: `T-054`
- Claim bearing: `false`; tier: `T0`
- Status: `CONDITIONAL_WEIGHTED_TRANSFER_OPERATOR_RESOLVENT_AUDITED`
- Route role: additive input interface above R-455 for the existing T-054 forward method. It does not replace T-054, T-059, T-061, or their owner order.

## Exact conditional statement

Let `h_0=0` and let the componentwise nonnegative vector history obey

`h_R <= K_R h_(R-1) + u_R + d_R`.

For strictly positive coordinate weights `w_i`, define
`||x||_w=max_i |x_i|/w_i`. Assume each `K_R` is entrywise nonnegative and

`sum_j K_R[i,j] w_j <= kappa_bar*w_i`

for every row and one common `kappa_bar`. Then the diagonal conjugate
`D_w^(-1) K_R D_w` has ordinary infinity row bound at most `kappa_bar`, so

`||K_R ... K_(j+1)||_w <= kappa_bar^(R-j)`

and, when `||u_R||_w <= A*r^(R-1)` and
`||d_R||_w <= D*s^(R-1)`,

`||h_R||_w <= A*S_R(kappa_bar,r) + D*S_R(kappa_bar,s)`.

Unequal bases use `(kappa_bar^R-x^R)/(kappa_bar-x)` and resonance uses
`R*x^(R-1)`. The sufficient decay threshold remains `0 <= kappa_bar < 1`
and `0 <= s < 1`.

The weighted form is a finite coordinate contract. It is not an assertion
that a Q3 owner has supplied weights or a common unbounded operator domain.

## Reproducible evidence

The exact-Fraction primary lane passes `290560/290560` assertions over 17
radius rows, 46 bound/defect pairs, dimensions 1--3, five positive weight
patterns, seven transfer patterns, and `77280` terminal path checks. The
non-importing independent lane passes `231840` exact assertions with the same
coverage and path count. The hostile lane rejects `22/22` mutations, including
nonpositive weights, sign/order/bound omissions, reversed diagonal direction,
resonance and threshold weakening, finite-grid substitution, owner/domain and
physical promotions, tier changes, and method/owner-order changes. The
integrated verifier passes `22/22`; Lean `R456.lean` compiles with the pinned
Lean 4.32.1/Mathlib lock.

Run commands:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_weighted_transfer_operator_defect_resolvent_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean verification/lean/Tect/R456.lean
```

The manifest, three run artefacts, integrated run, and Lean source are the
authority. The finite fixture tests coordinate algebra only; it is not an
exhaustion or continuum surrogate.

## Assumptions and missing assumptions

The result assumes the unchanged R-455/R-454/R-451 interfaces, strictly
positive finite coordinate weights, nonnegative finite transfer matrices and
vectors, one common weighted row bound, geometric weighted source/defect norms,
and finite-sum manipulations before any limit. It does not provide a
source-owned Q3LOCK transfer law, owner weights, componentwise history,
common `kappa_bar<1`, vector residual, common unbounded weighted domain,
shape/volume/cutoff/beta/history uniformity, production exhaustion map,
OS/KMS/GNS link, common alpha, physical sector, continuum, Yang--Mills, or
mass-gap result.

## Adversarial disposition

Strict weight positivity, entry signs, weighted row domination, diagonal
direction, path order, defect indexing, and resonant closed forms are checked
and rejected as implementation errors when mutated. The componentwise
recurrence, owner packet, common domain, and finite-to-infinite interpretation
remain open. The weighted coordinate lift is explicitly additive; all
physical, continuum, Yang--Mills, mass-gap, Pre-A, Sector-A, and Clay
promotion paths remain rejected.

## Next gate

When a source-owned Q3 history supplies positive weights, coupled transfer
matrices, a common weighted `kappa_bar<1`, weighted source/residual bounds and
a common domain, instantiate R-456 and feed its envelope through R-455,
R-454, R-453 and R-451. Until that packet exists, continue the unchanged
T-054 owner-intake boundary and additive T-059/T-061 observation-source lock;
do not manufacture another finite mobility or geometry table.
