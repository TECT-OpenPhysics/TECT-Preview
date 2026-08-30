# R-455 certificate: nonnegative transfer-matrix defect-resolvent envelope

## Identity and route role

- Result: `R-455`
- Candidate: `PA-CP1-ST8-Q3LOCK-NONNEGATIVE-TRANSFER-MATRIX-DEFECT-RESOLVENT-v0`
- Exploration: `EXP-001328`
- Task: `T-054`
- Claim bearing: `false`; tier: `T0`
- Status: `CONDITIONAL_NONNEGATIVE_TRANSFER_MATRIX_RESOLVENT_AUDITED`
- Route role: additive input interface for the existing T-054 forward method. It does not replace T-054, T-059, T-061, or their owner order.

## Exact conditional statement

Let `h_0=0` and let the componentwise nonnegative vector history obey

`h_R <= K_R h_(R-1) + u_R + d_R`.

Assume every `K_R` is entrywise nonnegative with maximum absolute row sum at
most one common `kappa_bar`, and that `||u_R||_infinity <= A*r^(R-1)` and
`||d_R||_infinity <= D*s^(R-1)`. The induced infinity norm gives

`||K_R ... K_(j+1)||_infinity <= kappa_bar^(R-j)`

and therefore

`||h_R||_infinity <= A*S_R(kappa_bar,r) + D*S_R(kappa_bar,s)`,

where `S_R(kappa_bar,x)` is the finite geometric convolution. For unequal
bases it is `(kappa_bar^R-x^R)/(kappa_bar-x)`; at resonance it is
`R*x^(R-1)`. The sufficient decay threshold is
`0 <= kappa_bar < 1` and `0 <= s < 1`.

## Reproducible evidence

The exact-Fraction primary lane passes `373915/373915` assertions over 65
radii, 46 bound/defect pairs, dimensions 1--3, seven matrix patterns, and
`61824` terminal path checks. The non-importing independent lane passes
`250290/250290` assertions with the same coverage and path count. The hostile
lane rejects `20/20` mutations, including negative entries, reversed path
order, missing common bounds, resonance omission, unit thresholds, finite-grid
substitution, owner-history claims, method changes, and promotion attempts.
The integrated verifier passes and Lean `R455.lean` compiles with the pinned
Lean 4.32.1/Mathlib lock.

Run commands:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_transfer_matrix_defect_resolvent_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean verification/lean/Tect/R455.lean
```

The machine manifest, four run artifacts, and Lean source are the authority;
the finite fixture is an algebra check and not an exhaustion surrogate.

## Assumptions and missing assumptions

The result assumes the unchanged R-454 scalar interface, nonnegative common
norm data, entrywise nonnegative transfer matrices, one common row-sum bound,
geometric source/defect norms, and finite-sum manipulations before any limit.
It does not provide a source-owned Q3LOCK transfer law, componentwise history,
common `kappa_bar<1`, vector residual, common unbounded domain, shape/volume/
cutoff/beta/history uniformity, production exhaustion map, OS/KMS/GNS link,
common alpha, physical sector, continuum, Yang--Mills, or mass-gap result.

## Adversarial disposition

Entry signs, row-sum domination, path order, defect indexing, and resonant
closed forms are checked and dismissed as implementation errors. The
componentwise recurrence and finite-to-infinite interpretation remain
owner-open. The matrix lift is explicitly additive, and all physical,
continuum, Yang--Mills, mass-gap, Pre-A, Sector-A, and Clay promotion paths are
rejected.

## Next gate

When a source-owned Q3 history supplies coupled matrices, the common
`kappa_bar<1`, vector source and defect bounds, instantiate R-455 and feed the
envelope through R-454/R-453/R-451. Until that packet exists, keep the existing
T-054 owner-intake boundary and additive T-059/T-061 observation-source lock;
do not manufacture another finite mobility or geometry table.
