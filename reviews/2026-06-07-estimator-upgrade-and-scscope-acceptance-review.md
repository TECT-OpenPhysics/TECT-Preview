# 2026-06-07 — ESTIMATOR-UPGRADE single-shell advance + SC-SCOPE scope-decision acceptance review

**Reviewer:** operator (Jusang Lee)
**Format:** evaluation summary -> per-document adversarial review (two documents).
**Verdict:** both documents accepted. ESTIMATOR-UPGRADE: single-shell M-quadrature
subgate marked CONTROLLED-ERROR ADVANCED, gate KEEP OPEN. SC-SCOPE scope-decision
wording (estimate-feasible, NOT proved) accepted; scope accepted, no mainline
action. No tier change on either.

---

## Document 1 — estimator-upgrade-enumerated v1.0 (B1 ESTIMATOR-UPGRADE)

### Evaluation summary
A good reinforcement note. It lifts the single-shell enumerated readings
(LAM/HEX/FCC/BCC) from an estimator-grade dF>0 verdict to an M-quadrature
controlled-error bound, via the curvature kappa_R := dF_R''(0) = 2 dF_R(h)/h^2 +
O(h^2). Result table (fast N_PT=6000 vs hires N_PT=20000): kappa = 0.851 / 2.554 /
3.408 / 5.116 with envelope < 1.2e-4; binding LAM kappa = 0.851 +/- 1.7e-5. No
condensate at either resolution (global best at A=0). Honest verdict:
single-shell M-quadrature ADVANCED to controlled-error positive; full
ESTIMATOR-UPGRADE OPEN pending the two-shell ensemble and dI/grid knobs.

### Adversarial points and actions
1. **"controlled-error" scope is limited to the M-quadrature knob.** The most
   important caveat. The note is strong against the M-quadrature knob but does not
   close the full numerical uncertainty; the remaining knobs are {two-shell
   ensemble, dI quadrature, amplitude grid}. Correct ledger phrasing: "single-shell
   enumerated margins are controlled with respect to the dominant M-quadrature
   knob." Forbidden over-claim: "B1 estimator uncertainty is fully closed."
   ACTION: GATES.md ESTIMATOR-UPGRADE status marked "OPEN (single-shell M-quad
   subgate: CONTROLLED-ERROR ADVANCED)" with the precise scope sentence; the B1
   card notes carry the same; no "fully closed" phrasing exists anywhere (verified).
2. **The no-condensate scan is still grid evidence.** kappa_R>0 secures A=0 as a
   strict LOCAL minimum, but "no deeper minimum at A>0" rests on the amplitude scan
   (two resolutions), not a continuum proof. Best (non-essential, publication-grade)
   reinforcement: a no-condensate interval/Lipschitz bound dF_R(A) >= 0 on each
   amplitude interval [A_j, A_{j+1}]. ACTION: registered as a publication-grade
   follow-up in T-010 (not required for the current advance).
3. **h-finite-difference A^4 contamination is well defended.** kappa(h) vs kappa(h/2)
   agree to <2% for every reading, so this attack is weak at the current step.
   No action.

### Operator verdict
ESTIMATOR-UPGRADE: KEEP OPEN, but mark the single-shell M-quadrature subgate as
controlled-error advanced. Next mainline = two-shell ensemble + dI envelope +
amplitude-grid envelope (the note's own roadmap).

---

## Document 2 — scscope-scope-decision v1.0 (SC-SCOPE wording precision)

### Evaluation summary
More accurate than the prior scope-decision. The key fix is lowering "FEASIBLE"
to "ESTIMATE-FEASIBLE, NOT proved". The note records that the all-orders
third-order lift is estimate-feasible for I<=1e-3 but NOT proved, and that at the
I=2e-3 endpoint the paired result is x0.905 < 1, so all-orders closure is not
possible and second-cumulant scope is accepted by operator decision. B1 T6
unchanged.

### Adversarial points
1. **Lowering to "estimate-feasible" was a required fix.** A bare "feasible" could
   be misread as proved. The note now repeatedly pins "ESTIMATE-FEASIBLE
   (estimate-grade, NOT proved)" and the self-review concedes the I<=1e-3 claim
   rests on R_sup and the sunset/quartic estimates. Accepted.
2. **The endpoint is "accepted at second-cumulant scope", not "closed".** The
   load-bearing inequality rho/(1+max_t(R_s+R_q)) = 2.6/2.872 = x0.905 < 1 shows the
   endpoint is NOT all-orders closed; the "closure" is an operational scope decision,
   not a mathematical closure. Correct phrasing: "the endpoint is not all-orders
   closed; it is accepted at second-cumulant scope." Forbidden: "SC-SCOPE is closed
   all-orders."
3. **B1 T6 is unaffected.** B1-RH-ENUM stays T6 conditional on {H-LAYER, H-ADM-COH,
   SC-SCOPE}; SC-SCOPE remains the named second-cumulant hypothesis; no tier change.
   Logically correct.

### Operator canonical ledger section (recorded verbatim)
\section{SC-SCOPE Scope Decision}
The SC-SCOPE endpoint arc is closed as a scope decision, not as an all-orders
proof. The all-orders third-cumulant lift is estimate-feasible for I<=1e-3, with
paired joint ratios x20.7 at I=4e-4 and x3.1 at I=1e-3. At the thinnest endpoint
I=2e-3 the most favourable paired joint estimate gives 2.6/2.872 = x0.905 < 1.
Hence the endpoint is not all-orders closed. The accepted scope is second-cumulant
selection at the endpoint, by operator decision. B1 Reading-H T6 is unchanged
because SC-SCOPE is its named second-cumulant hypothesis.

### Operator verdict
SC-SCOPE: scope accepted; no required mainline action. Acceptable as ledger
wording. Next = continue B1 ESTIMATOR-UPGRADE as planned.

---

## Actions taken this turn
- GATES.md ESTIMATOR-UPGRADE: single-shell M-quadrature subgate marked
  CONTROLLED-ERROR ADVANCED; gate stays OPEN; precise M-quadrature-only scope
  sentence + named remaining knobs added.
- B1 card notes: same operator-review annotation; last_review 2026-06-07; no tier/
  gate flip; ESTIMATOR-UPGRADE remains in open_gates.
- T-010: extended with the publication-grade no-condensate interval/Lipschitz
  follow-up.
- SC-SCOPE: no change required (the v1.0 wording is already accepted); the operator
  canonical section is recorded here.

## Credit
The M-quadrature-only scoping, the interval/Lipschitz no-condensate suggestion,
and the "scope decision not all-orders closure" framing are reviewer-directed.
