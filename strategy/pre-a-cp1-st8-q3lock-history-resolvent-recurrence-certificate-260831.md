# R-452 certificate — conditional history-resolvent recurrence envelope

## Question and method

R-452 is an additive T-054 interface in the existing forward proof order.  It
does not alter the Q3LOCK construction, select a candidate, or replace the
observation-first inverse lane.  It asks for the smallest scalar contract that
would let a source-owned history estimate use the already audited R-451
two-sided Cauchy interface without assuming a complete additive history sum at
every radius.

Let `H_R` be the total two-orientation fourth-power history error after radius
`R`, with `H_0=0`.  R-451 supplies

`T(R) <= B*q^(R-1)`, with `B=78` and `q=23/26`.

After taking the fourth power, set `r=q^4=279841/456976`.  The R-451 source
term is then bounded by

`A*r^(R-1)`, where the constant is recomputed from the R-450 parent as

`A = 16*C4_edge*78^4`.

The owner-level contract tested here is the one-step recurrence

`H_R <= kappa*H_(R-1) + A*r^(R-1)`.

For equality recurrence data, the exact resolvent kernel is

`S_R(kappa,r) = sum_(j=0)^(R-1) kappa^(R-1-j)*r^j`.

Therefore the comparison estimate is

`H_R <= A*S_R(kappa,r)`.

For `kappa != r`,

`S_R=(kappa^R-r^R)/(kappa-r)`;

for the resonant case `kappa=r`,

`S_R=R*r^(R-1)`.

Because `0<r<1`, every owner recurrence with `0 <= kappa < 1` has
`max(kappa,r)<1`, so the resolvent tends to zero.  If `kappa<r`, the parent
shell rate is retained; if `r<kappa<1`, propagation is slower but still
vanishing.  This is a conditional admission criterion, not a value of
`kappa` for the TECT dynamics.

## Exact execution

The primary exact-Fraction lane checks 1,614 assertions over 65 radii and eight
cases: the seven declared threshold controls plus the parent-derived resonant
case `kappa=r`.  It recomputes `q`, `B`, the two-orientation factor, `C4_edge`,
`r`, and `A`; checks the recurrence and both closed-form branches at every
radius; and keeps the owner and promotion firewalls explicit.

The non-importing independent lane checks 1,572 assertions over the same 65
radii and eight cases.  The hostile lane rejects 11/11 mutations, including
`kappa=1`, `kappa>1`, a nondecaying parent base, dropped or added orientations,
division by zero at resonance, deletion of the recurrence term, fitted source
constants, radius rows relabelled as exhaustion, Q3 promotion, and method
replacement.  The integrated verifier passes 19/19 and Lean `R452.lean`
compiles.

## Evidence level and boundary

Evidence level: **T0 exact conditional scalar history-resolvent recurrence
envelope**.

The result supplies a reusable analytic plug-in and narrows the missing
owner-level obligation to a uniform recurrence with `kappa<1`.  It does not
supply that recurrence or coefficient, a common unbounded operator/form
domain, a production observable, an exhaustion map, or a physical state.
Nothing here establishes common-alpha, OS/KMS/GNS identification, a physical
sector, continuum removal, Yang–Mills dynamics, or a mass gap.

The established T-054 forward method, the T-059/T-061 inverse methods, their
owner order, and all promotion firewalls are unchanged.

## Adversarial review

1. **Recurrence substitution — UPHELD-OPEN.**  `kappa` and the one-step
   recurrence are explicit source-owner hypotheses; they are not presented as
   an actual Q3LOCK history.
2. **Resonant denominator — DISMISSED.**  The `kappa=r` branch is checked as
   `R*r^(R-1)` and never evaluates the nonresonant quotient at zero
   denominator.
3. **Threshold — UPHELD-REJECTED.**  The `kappa=1` and `kappa>1` controls are
   not admitted to the vanishing conclusion.
4. **Source constant — DISMISSED.**  `A` is recomputed from the R-450
   two-orientation factor, the parent `C4_edge`, and the R-451 base tail.
5. **Finite-to-infinite boundary — UPHELD-OPEN.**  The radius rows audit exact
   recurrence algebra only; they are not an exhaustion or continuum result.
6. **Method preservation — DISMISSED.**  The packet is an additive T-054
   interface and leaves T-054/T-059/T-061 methods and owner order intact.
7. **Promotion firewall — UPHELD-REJECTED.**  Actual Q3 history, common
   operator domain, common alpha, physical, continuum, and Clay flags remain
   false.

## Reproducibility

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_history_resolvent_recurrence.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_history_resolvent_recurrence_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_history_resolvent_recurrence_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_history_resolvent_recurrence_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R452.lean
```

No proof-note PDF is issued at this intermediate interface checkpoint.  A
future gate-level synthesis note will include R-452 only after the actual
source-owned recurrence and common-domain obligations are discharged.
