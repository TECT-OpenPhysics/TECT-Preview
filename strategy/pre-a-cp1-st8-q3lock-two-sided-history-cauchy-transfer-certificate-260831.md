# R-451 certificate — conditional two-sided history recurrence to all-shape Cauchy transfer

## Question and method

R-451 is an additive T-054 interface in the established forward proof order.
It does not revise the method, choose a new candidate, or replace the inverse
lane.  It takes the already audited R-450 two-orientation shell envelope and
tests the exact implication that would be used after a source-owned history
recurrence and one common domain are supplied.

The conditional history contract is the following.  For each orientation
`sigma`, and for any nested rectangular pair that agrees through radius `R-1`,
the difference is a finite additive sum of actual history terms
`X_(sigma,e)` over changed edges in one common `L4` space or form domain, with

`||X_(sigma,e)||_L4^4 <= C4_edge * w(e)^4`.

The R-444 tail is

`T(R)=3*(4R^2+8R+14)*2^(1-R)`.

The exact scalar ratio is

`T(R+1)/T(R) = (4R^2+16R+26)/(8R^2+16R+28) <= 23/26`

for every `R >= 1`; the difference from the upper bound is a nonnegative
multiple of `(R-1)(5R+2)`.  Hence

`T(R) <= 78*(23/26)^(R-1)`.

Applying the triangle inequality to the two orientation sums and the exact
fourth-power inequality `(a+b)^4 <= 8(a^4+b^4)` gives the root-free bound

`||Y_Lambda' - Y_Lambda||_L4^4 <= 16*C4_edge*T(R)^4`.

Thus, conditionally, any shape-consistent exhaustion whose pairwise changes
escape to radius infinity is `L4`-Cauchy.  No finite box grid is used as a
surrogate for that implication.

## Exact execution

The primary exact-Fraction lane passes `341/341` assertions over the complete
declared scalar range `R=1..64`.  It recomputes the base tail `78`, the sharp
base ratio `23/26`, every exact recurrence row, the geometric envelope, the
orientation-derived factor `16`, the parent `C4_edge`, the common-domain and
history-contract requirements, and all promotion firewalls.

The non-importing independent lane passes `332/332` assertions over the same
range and reconstructs the recurrence and fourth-power factor separately.  The
hostile lane rejects `9/9` mutations, including a non-decaying ratio, dropping
an orientation, adding an undeclared orientation, deleting the common domain or
history decomposition, promoting the conditional result to actual Q3/operator
scope, treating a finite grid as exhaustion, and changing the established
method.

Lean `R451.lean` compiles.  It checks the factor-16 fourth-power conversion,
the exact base tail, the ratio inequality, and the geometric envelope by
induction.  The integrated verifier passes `19/19`.

## Evidence level and boundary

Evidence level: **T0 exact conditional recurrence-to-Cauchy transfer with an
analytic geometric-tail envelope**.

This result is useful only as a plug-in theorem.  It does not provide a
source-owned Q3LOCK history, actual commutator coefficients, a common
unbounded operator/form domain, an exhaustion map, or uniform constants.  It
therefore does not establish common-alpha, OS/KMS/GNS identification, a
physical sector, continuum removal, Yang--Mills dynamics, or a mass gap.  The
existing T-054 forward method, T-059/T-061 inverse methods, owner order, and
promotion firewalls remain unchanged.

## Adversarial review

1. **Actual-history boundary — UPHELD-OPEN.** The recurrence is an explicit
   hypothesis; no actual Q3 history is substituted for it.
2. **Common-domain boundary — UPHELD-OPEN.** The triangle inequality is used
   only after a single common `L4` space/form domain is assumed.
3. **Shape-independence — UPHELD-OPEN.** Consistency of the edge decomposition
   on triple-nested boxes is assumed; production shape-independence is not
   inferred.
4. **Fourth-power conversion — UPHELD.** The factor `16` is derived as
   `8 * 2`, exposing both orientations and avoiding a hidden fitted constant.
5. **Finite-to-infinite boundary — UPHELD-OPEN.** The 64 ratio rows audit the
   scalar formula only; geometric vanishing is the analytic conditional bound.
6. **Method preservation — DISMISSED.** This is a composition of R-450 with
   an explicit recurrence implication and leaves the established proof order
   intact.
7. **Promotion firewall — UPHELD-REJECTED.** Actual history, operator domain,
   common alpha, physical, continuum and Clay flags stay false.

## Reproducibility

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_cp1_st8_q3lock_two_sided_history_cauchy_transfer_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R451.lean
```

No proof-note PDF is issued at this intermediate interface checkpoint.  A
future gate-level synthesis note will include the result only when the actual
source-owned history and common-domain obligations are discharged.
