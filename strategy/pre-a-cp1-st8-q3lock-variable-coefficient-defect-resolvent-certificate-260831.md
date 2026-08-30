# R-454 certificate — variable-coefficient defect-stable history-resolvent envelope

## Question and preserved method

R-454 is an additive T-054 interface downstream of R-453.  It does not alter
the Q3LOCK construction, the T-054 forward proof order, or the additive
T-059/T-061 observation-first inverse lane.  It removes an artificial
restriction in the owner contract: the history propagation coefficient may
vary with the step, provided one common upper bound is proved.

Let `H_0=0` and, for `R>=1`, suppose

`H_R <= kappa_R*H_(R-1) + A*r^(R-1) + delta_R`,

with `0<=kappa_R<=kappa_bar`, `delta_R>=0`, and the inherited R-451/R-450
source constants

`r=(23/26)^4=279841/456976`,

`A=16*C4_edge*78^4`.

Unrolling gives path products of the individual `kappa_R`.  Positivity and
`kappa_R<=kappa_bar` bound every product by
`kappa_bar^(R-j)`, hence

`H_R <= A*S_R(kappa_bar,r) + sum_(j=1)^R kappa_bar^(R-j)*delta_j`.

For a geometric residual `delta_R<=D*s^(R-1)`, this specializes to

`H_R <= A*S_R(kappa_bar,r) + D*S_R(kappa_bar,s)`.

The unequal-base kernel is
`S_R(kappa_bar,x)=(kappa_bar^R-x^R)/(kappa_bar-x)`; at resonance it is
`R*x^(R-1)`.  The sufficient scalar threshold is
`0<=kappa_bar<1` and `0<=s<1`.

## Exact execution

The primary exact-Fraction lane checks 88,391 assertions over 65 radii, 46
upper-bound/defect-base pairs, and five declared coefficient patterns
(`zero`, `constant`, `alternating`, `ramp-four`, `ramp-five`).  It recomputes
all inherited constants, checks each coefficient's lower and upper bounds,
path-product expansion, variable-to-constant domination, residual envelopes,
both closed-form branches, and unit/superunit controls.  `D=0` retains the
exact R-452 reduction.

The non-importing independent lane checks 58,939 assertions over the same
coverage.  The hostile lane rejects 16/16 mutations, including omitted or
super-bound coefficients, negative coefficients, dropped/shifted defects,
unit and superunit bases, nondecaying parent, fitted constants, finite rows
relabelled as exhaustion, method overhaul and physical promotion.  The
integrated verifier passes 19/19 and Lean `R454.lean` compiles.

## Evidence level and boundary

Evidence level: **T0 exact conditional variable-coefficient defect-stable
scalar history-resolvent envelope**.

R-454 makes the next source-owner submission more realistic: it may provide a
uniform upper bound on per-step coefficients rather than an equality.  It does
not supply the Q3LOCK recurrence, any coefficient, the common upper bound, the
residual, a common domain, an all-shape exhaustion map, common alpha, an
OS/KMS/GNS identification, a physical sector, a continuum limit,
Yang--Mills dynamics or a mass gap.

The finite pattern and radius rows are exact scalar checks only and are not an
exhaustion surrogate.  The T-054 forward method, T-059/T-061 inverse methods,
owner order, and promotion firewalls are unchanged.

## Adversarial review

1. **Coefficient order — DISMISSED.** Every pattern is checked to satisfy
   `0<=kappa_R<=kappa_bar` before product domination is used.
2. **Defect indexing — DISMISSED.** A residual born at step `j` receives
   exactly `kappa_bar^(R-j)`.
3. **Residual substitution — UPHELD-OPEN.** The variable bound is a contract,
   not a source-owned Q3 history.
4. **Resonant denominators — DISMISSED.** Source and defect resonances use
   `R*x^(R-1)` and never divide by zero.
5. **Threshold — UPHELD-REJECTED.** Unit and superunit controls are excluded
   from the vanishing conclusion.
6. **Finite-to-infinite boundary — UPHELD-OPEN.** Pattern/radius rows do not
   establish uniformity or exhaustion.
7. **Method preservation — DISMISSED.** This is an additive owner-bound
   refinement of R-453; T-054/T-059/T-061 are unchanged.
8. **Promotion firewall — UPHELD-REJECTED.** No physical, continuum, QFT,
   Yang--Mills, mass-gap, Pre-A, Sector-A or Clay conclusion follows.

## Reproducibility

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_variable_coefficient_defect_resolvent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_variable_coefficient_defect_resolvent_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_variable_coefficient_defect_resolvent_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_variable_coefficient_defect_resolvent_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R454.lean
```

No proof-note PDF is issued at this intermediate interface checkpoint.  A
future gate-level synthesis note may include R-454 only after the actual
source-owned recurrence and common-domain obligations are discharged.
