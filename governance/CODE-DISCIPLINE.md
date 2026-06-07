# CODE-DISCIPLINE.md — binding code-writing policy

**Binding from**: 2026-06-07 (operator directive). Applies to every script under
`codes/` and `verification/scripts/`, written by any collaborator (human or AI).

**Why this exists.** Code errors have been the single largest time sink in this
programme: a factor-2 slip (`M' = -J(0)` where the truth is `-J(0)/2`)
propagated through several notes before it was caught; a layer margin hardcoded
at its anchor value (`MARGIN = 0.00432`) masked the fact that the off-anchor
quantity had never been recomputed. Both were preventable. This policy converts
"be careful" into four enforceable rules.

---

## 1. No hardcoding of derived numerical values

- A number that is the OUTPUT of a computation MUST be computed in the code, not
  pasted. Derive it from a single upstream source (the shared constants module,
  the gap solver, an integral) so that changing an input propagates.
  - *Canonical failure*: `MARGIN = 0.00432` pasted into a robustness script that
    then "checked" off-anchor robustness while never recomputing the margin.
    The fix recomputes `MARGIN(mu^2) = PB(M_+(mu^2)) - DIP_BAND(mu^2)`.
- **Permitted literals**: (a) physical/Lagrangian INPUTS defined once in the
  shared source (`U, V, q0, C, mu^2`); (b) **test oracles** — an expected value
  in a `--selftest`/assert that cross-checks an INDEPENDENTLY computed quantity,
  clearly labelled as a reproduction check (e.g. `assert abs(margin - 0.00432)
  < 5e-5  # reproduces the certified anchor`); (c) tooling thresholds
  (tolerances, grid sizes, min Python version) with a comment.
- A pasted derived constant with no recompute path is a defect, audit-flagged on
  first review.

## 2. Mandatory adversarial code review (no exceptions)

Before a script's numbers are cited as evidence anywhere, it gets an explicit
adversarial pass — written into the supporting Math note's devil's-advocate
section (≥3 concrete objections) and, where feasible, sent for external review.
The checklist (non-exhaustive; grows with each incident):

- **sign / direction**: is every inequality and rate in the physically correct
  direction? (the `M' < 0` vs magnitude trap.)
- **factor / convention**: any `1/2`, `2`, `2π`, normalisation, or
  per-volume/per-mode factor that could be off? (the `-J(0)` vs `-J(0)/2` trap.)
- **units / dimensions**: do both sides of every comparison carry the same units?
- **convergence**: are quadratures/grids resolution-independent? report a
  two-resolution envelope, not a single grid value.
- **hardcode masking**: does any literal hide a quantity that should be
  recomputed? (rule §1.)
- **limit cases**: does the code reproduce a known anchor / textbook limit?

## 3. Reproducible and reported

Every script MUST:

1. carry **self-test asserts** that fail loudly on wrong arithmetic, covering
   every numerical claim it supports (not a representative subset);
2. emit a **JSON artefact** under `claims/<ID>/runs/<date>-<task>/result.json`
   (or `--selftest` for pure tooling) with per-claim `pass` flags;
3. be **runnable standalone**: `python <script>.py` exits 0 iff all asserts pass;
4. be **reported in chat**: when code is written or changed, the response states
   (a) which file, (b) what it computes, (c) the exact command to run it, and
   (d) the key asserted results — so the operator can execute and verify
   directly without reverse-engineering.

## 4. External-review-ready

- Code is written to be audited by someone who did not write it: a top
  docstring stating purpose, convention, and the formula being evaluated;
  named intermediate quantities; no silent magic.
- The chat report explicitly **invites external review** and names the
  reproduction command, so a third party (or a different AI session) can
  re-run and attack the result. The `reviews/` archive records adversarial
  passes; reviewer-found defects are credited.

---

## Enforcement

- These rules are part of the §3 claim-first / numerical-claim discipline
  (`CLAUDE.md` §3, §6).
- A future automated check (`verification/scripts/check_code_discipline.py`,
  tracked as task T-006) will scan `codes/` for (a) suspect hardcoded literals
  outside the permitted classes, (b) scripts lacking self-test asserts or a JSON
  artefact, and run in `release_check.py`. Until then the rules are enforced at
  review time and via the supporting note's devil's-advocate section.

## History

- **2026-06-07**: created on operator directive after the `M' = -J(0)` factor-2
  and `MARGIN = 0.00432` frozen-hardcode incidents.
