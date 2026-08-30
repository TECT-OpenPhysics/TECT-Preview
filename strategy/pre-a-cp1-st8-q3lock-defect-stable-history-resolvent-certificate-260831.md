# R-453 certificate — defect-stable history-resolvent recurrence envelope

## Question and preserved method

R-453 is an additive T-054 interface.  It does not replace the established
Q3LOCK owner order, the T-054 forward method, or the additive T-059/T-061
observation-first inverse lane.  It sharpens the next owner obligation after
R-452 by allowing an explicitly bounded residual in the one-step history
recurrence.

Let `H_0=0` and suppose that, for `R>=1`,

`H_R <= kappa*H_(R-1) + A*r^(R-1) + delta_R`,

where the nonnegative source term is inherited from R-451/R-450:

`r=(23/26)^4=279841/456976`,

`A=16*C4_edge*78^4`.

Unrolling the recurrence gives the exact general defect envelope

`H_R <= A*S_R(kappa,r) + sum_(j=1)^R kappa^(R-j)*delta_j`,

where `S_R(kappa,x)=sum_(j=0)^(R-1) kappa^(R-1-j)*x^j`.

If the owner supplies the geometric residual bound

`0 <= delta_R <= D*s^(R-1)`,

then the second term is bounded by `D*S_R(kappa,s)`, so

`H_R <= A*S_R(kappa,r) + D*S_R(kappa,s)`.

For unequal bases the exact kernel is

`S_R(kappa,x)=(kappa^R-x^R)/(kappa-x)`;

at resonance it is `R*x^(R-1)`.  Thus `0<=kappa<1` and `0<=s<1` are
sufficient for the two terms to vanish.  The contract makes no claim when a
propagation base reaches or exceeds one.

## Exact execution

The primary exact-Fraction lane checks 29,752 assertions over 65 radii and 46
declared/parent-derived `(kappa,s)` pairs.  It recomputes `q`, the parent
fourth-power decay `r`, the two-orientation factor, `C4_edge`, and `A`; checks
both kernel closed forms, both recurrence identities, exact equality
recurrences, arbitrary sub-envelope residuals, residual indexing, positivity,
and the two-base threshold controls.  It exercises both `kappa=r` and
`kappa=s` resonance and includes `D=0` as the exact R-452 reduction.

The non-importing independent lane checks 14,827 assertions over the same 65
radii and 46 pairs.  The hostile lane rejects 14/14 mutations, including a
dropped defect, shifted residual weight, unit/superunit propagation bases,
nondecaying parent, fitted constants, resonant denominator, unbounded residual,
finite rows relabelled as exhaustion, method overhaul, and physical promotion.
The integrated verifier passes 19/19 and Lean `R453.lean` compiles.

## Evidence level and boundary

Evidence level: **T0 exact conditional defect-stable scalar
history-resolvent envelope**.

The result is a reusable admission contract: a future source owner may submit
either a direct residual sequence in the weighted convolution or a common
geometric defect bound.  Neither the recurrence, `kappa`, residual, `D`, nor
`s` is supplied by this packet.  The common domain, all-shape exhaustion,
uniformity in beta/cutoff/volume/phase/history, common alpha, OS/KMS/GNS
identification, physical sector, continuum, Yang--Mills and mass-gap gates
remain open.

The finite rows are exact scalar algebra only; they are not an exhaustion
surrogate.  The established T-054 forward method, T-059/T-061 inverse methods,
owner order, and all promotion firewalls are unchanged.

## Adversarial review

1. **Defect indexing — DISMISSED.**  The step-`j` residual receives exactly
   `kappa^(R-j)`; the direct and geometric convolutions are checked.
2. **Residual substitution — UPHELD-OPEN.**  A residual allowance does not
   construct the missing source-owned Q3 history; all such fields remain
   explicit hypotheses.
3. **Resonant denominators — DISMISSED.**  Source and defect resonances use
   `R*x^(R-1)` and never evaluate a zero denominator.
4. **Threshold — UPHELD-REJECTED.**  Unit and superunit controls remain outside
   the sufficient vanishing conclusion.
5. **Fitted constants — DISMISSED.**  `A` is recomputed from R-451/R-450;
   `D` and `s` are declared owner-side inputs, not post-fit values.
6. **Finite-to-infinite boundary — UPHELD-OPEN.**  Radius rows audit algebra;
   uniform owner hypotheses are still required for a limit.
7. **Method preservation — DISMISSED.**  R-453 is downstream of R-452 and
   leaves T-054, T-059, T-061 and their owner order intact.
8. **Promotion firewall — UPHELD-REJECTED.**  No physical, continuum, QFT,
   Yang--Mills, mass-gap, Pre-A, Sector-A or Clay conclusion follows.

## Reproducibility

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_defect_stable_history_resolvent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_defect_stable_history_resolvent_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_defect_stable_history_resolvent_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_defect_stable_history_resolvent_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R453.lean
```

No proof-note PDF is issued at this intermediate interface checkpoint.  A
future gate-level synthesis note may include R-453 only after an actual
source-owned recurrence and common-domain obligations are discharged.
