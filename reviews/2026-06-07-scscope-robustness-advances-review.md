# 2026-06-07 — SC-SCOPE / ROBUSTNESS-MU2 advances review (eval summary + per-doc attacks)

**Reviewer:** operator (Jusang Lee)
**Format (new standard):** evaluation summary first, then per-document adversarial
attacks.
**Verdict:** both documents are real progress; tiers/gates FROZEN until operator
sign-off. Four priority reinforcements required (all applied → v1.1 re-issues).

**Reviewed:** scscope-mendpoint-evaluation v1.0; robustness-mu2-margin-recompute
v1.0.

## Evaluation summary (operator)
- M-ENDPOINT document: ONE SC-SCOPE channel (the sunset axis) resolved; not SC-SCOPE.
- ROBUSTNESS-MU2 document: closure bar met; gate flip recommended but pre-authorization.
- Correct live ledger: M-ENDPOINT RESOLVED; sunset axis POSITIVE (sign level);
  SC-SCOPE OPEN on GHAT4-PERTRANSFER + R-U6-1. ROBUSTNESS-MU2: CLOSURE BAR MET,
  CLOSE RECOMMENDED, gate OPEN until operator sign-off.

## Four priority reinforcements and actions
1. **M-ENDPOINT certificate** — attach quadrature/tail/error provenance behind the
   cross-check (interval-grade, not just an executed value).
   - ACTION (scscope v1.1): provenance recorded (cutoffs $k_{\max}\in[30,60]$,
     $n$ up to $10^6$); independent radial trapezoid vs production M_fast agree to
     **0.61%**; analytic tail bound $8.4\times10^{-4}$; M-ENDPOINT reported as an
     EXECUTED value cross-checked at ~1% (NOT a 0.1% interval constant), and the
     sunset VERDICT certified robust to the full raw envelope (x1.10 worst).
2. **Single-$J_0$ conservatism** — verify/tabulate $J(\hat r(I)) \le J_0$ at the endpoint.
   - ACTION (scscope v1.1): direct table $J(\hat r(10^{-3}))=0.2764$,
     $J(\hat r(2\times10^{-3}))=0.2565 \le J_0=0.2896$; per-dressing-$J$ ratio
     (x1.28) $\ge$ the $J_0$ ratio (x1.13) confirms $J_0$ is conservative.
3. **m(mu^2) minimum location** — derivative/interval proof that the minimum is at
   mu^2 = 0.0025.
   - ACTION (robustness v1.1): central-difference certificate
     $\partial_{\mu^2} m > 0$ at all 61 grid points (min $9.5\times10^{-2}$) plus
     the closed-form $\mathrm{DIP}_{\rm BAND}$-decreasing piece ⇒ minimum is the
     LEFT endpoint, not interior.
4. **Do NOT flip ROBUSTNESS-MU2 in GATES.md until operator sign-off.**
   - ACTION: GATES.md status remains OPEN; only a dated ADVANCE + recommendation
     recorded. No flip performed.

## Additional per-document attacks addressed
- **scscope** wording restricted to the SUNSET axis: "the U4 SUNSET-AXIS marginal
  failure was a frozen-coupling artefact" (NOT the third-cumulant endpoint);
  x1.13 stated as a SIGN result, not a comfortable margin; U4 reproduction flagged
  as a REGRESSION sanity check, not load-bearing.
- **robustness**: "three certified intensities" qualifier retained (not a
  continuous-intensity claim); $J_{\rm eff}$ envelope now reported across the
  WHOLE $5\times3$ grid (max < 0.01%), not only the thinnest corner; Prop-A
  branch invariance asserted (disc > 0, $M_+ > M_c$ on the whole band).

## Code-discipline application (2026-06-07 policy)
- The pasted `MARGIN = 0.00432` in scscope was REMOVED; both scripts now derive
  the margin from the single-source `codes/vacuum/sectorb_common.py`
  (`margin_of`), whose `--selftest` reproduces 0.00432.
- The build's return-code gate caught a self-introduced prose math-char bug
  (`m(mu^2)` / `J_eff` outside `$...$`) in the robustness note — fixed before
  commit. (An instance of "reproducible + adversarial review catches code errors".)

## Verification
scscope_mendpoint_eval.py v1.1 (12/12); robustness_mu2_margin_recompute.py v1.1
(9/9); sectorb_common.py --selftest PASS; FORM-CHECK PASS + OVERFULL 0 on both
v1.1 notes; release-check PASS; pytest 3.

## Ledger after this round (UNCHANGED tiers/gates)
- M-ENDPOINT: value RESOLVED (recommend); sunset axis POSITIVE at sign level.
- SC-SCOPE: OPEN on GHAT4-PERTRANSFER + R-U6-1 (+ joint inequality).
- ROBUSTNESS-MU2: OPEN, closure bar MET, CLOSE@[x0.5,x2]-2ND-CUMULANT RECOMMENDED
  pending operator sign-off.

## Credit
All four priority reinforcements reviewer-identified.
