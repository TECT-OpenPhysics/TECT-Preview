# R-450 certificate — conditional two-orientation shell transfer

## Question and method

R-450 tests the next two-orientation interface in the existing T-054 proof
order. It composes the already registered EXP-001320 state-weighted
per-edge fourth-power majorant with the R-444 rectangular shell tail and the
R-445 finite triangle-transfer contract. No new dynamics, candidate functional,
physical reference, or inverse-lane method is introduced.

For an edge term `X_(sigma,e)` in either orientation, the only input is the
explicit conditional hypothesis

`||X_(sigma,e)||_L4^4 <= C4_edge * w(e)^4`,

where `w(e)=2^(-||lower(e)||_1)` and `C4_edge` is recomputed from the EXP-001320
parents. The R-444 scalar tail is

`T(R)=3*(4*R^2+8*R+14)*2^(1-R)`.

Therefore each orientation has the symbolic envelope
`B_sigma(R)=C4_edge^(1/4)*sum_e w(e)`, and the root-free machine certificate
checks `B_sigma(R)^4 <= C4_edge*T(R)^4`; counting the two orientations gives
`B_+(R)^4+B_-(R)^4 <= 2*C4_edge*T(R)^4`.

## Exact execution

The parent force constant is `122099/35840`, `D=max(1,8/g)=40/3`, and the
endpoint bridge is `M_bridge=1179`. Recomputing rather than copying gives

`C4_edge = 29115196389063882279731/77341623582720`.

The primary Fraction lane passes `12742/12742` assertions. It checks all 343
ordered boxes in `[2,8]^3`, all 102900 positive-coordinate edges, all 4116
radius rows for `R=1..12`, both orientations, the coefficient/weight rows from
EXP-001320, shell recurrences, and the root-free fourth-power envelope. The
non-importing independent lane passes `12731/12731` with the same 343 boxes,
102900 edges, and 4116 rows. The hostile lane rejects `9/9` mutations,
including dropping an orientation, changing the shell tail or `C4_edge`,
violating coefficient domination, and promoting the conditional hypothesis to
an actual Q3 or method change. The integrated verifier passes `19/19`; Lean
`R450.lean` compiles.

## Evidence level and boundary

Evidence level: **T0 exact conditional two-orientation root-free fourth-power
shell-envelope transfer**. This is a finite geometric and algebraic interface.
It does not show that the exact Q3LOCK history supplies the per-edge hypothesis,
does not construct a common weighted operator/form domain, and does not prove a
history recurrence, Duhamel/Volterra convergence, exhaustion, common alpha,
OS/KMS/GNS identification, a physical sector, continuum, Yang–Mills dynamics,
or a mass gap. The T-054 forward method, owner order, and additive
observation-first inverse lane are unchanged.

## Adversarial review

1. **Conditional-majorant boundary — UPHELD-OPEN.** The per-edge L4
   fourth-power inequality is an assumption, not an exact-Q3 conclusion.
2. **Two-orientation accounting — UPHELD.** Both orientations are counted
   explicitly; the factor two is not hidden in a fitted constant.
3. **Finite-to-infinite boundary — UPHELD-OPEN.** The box sweep is not an
   exhaustion or thermodynamic limit.
4. **Root handling — UPHELD.** Machine inequalities are checked without
   numerical fourth-root approximations.
5. **Method preservation — DISMISSED.** This is a composition of existing
   R-444/R-445/EXP-001320 interfaces and leaves the established theorem order
   intact.
6. **QFT promotion — UPHELD-OPEN.** All operator, physical, continuum and
   Yang–Mills flags remain false.

## Reproducibility

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_two_orientation_shell_transfer_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R450.lean
```

No proof-note PDF is issued at this intermediate interface checkpoint. A
future gate-level synthesis note will carry the result only if the actual
owner/domain obligation is discharged.
