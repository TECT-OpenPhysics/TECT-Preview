# Operator adversarial review — internal-consistency pass (2026-06-06)

**Reviewer**: operator. **Finding**: CRITICAL internal contradictions I introduced via flip-flopping; superseded-document body errors create reuse risk. **Binding**: ROBUSTNESS-MU2 = OPEN (FINAL); remove all "CLOSED" wording from the robustness note; fix the reading-h footer. Canonical archive (CLAUDE.md §6.3.5).

## FINAL official status (this review is decisive on ROBUSTNESS-MU2)

- **ROBUSTNESS-MU2 = OPEN**, numerically supported on [x0.5,x2] but m(mu^2) NOT recomputed. The earlier "CLOSED for [x0.5,x2]" and "scoped closure CLOSED@[x0.5,x2]-2ND-CUMULANT" wordings are WITHDRAWN. (My flip-flop closed -> reopened -> scoped-closed -> now OPEN; this review is the decisive final.)
- B1 = T6 CONDITIONAL on {H-LAYER, H-ADM-COH, SC-SCOPE}.
- H-A0 = DISCHARGED at the anchor; H-ANCHOR = VERIFIED ANCHOR FACT.
- Near-gap gate = RESOLVED by common-mode cancellation, not by U11's old x130 claim.
- U14 v1.0 and robustness v1.0 = HISTORICAL/SUPERSEDED.

## reading-h v2.1 — attacks

1. body says {H-LAYER, H-ADM-COH, SC-SCOPE} but footer still said "four hypotheses" / listed H-A0 -- internal inconsistency. FIX: footer + no-overclaim to three hypotheses.
2. ROBUSTNESS-MU2 status (footer "open") is consistent with the FINAL gate state (OPEN) -- keep.
3. F[P] >= F[R_H] equality classification needs a lemma: Tr[ln(D_0+lambda'P^2)-ln D_0]=0 => P^2=0 (strict operator-monotonicity). ADDED.
4. case split needs an explicit partition A_adm = A_bulk U A_near with no double-count. ADDED (paper-grade threshold registered as refinement).
5. H-ADM-COH remains a class amendment; title says "class-wide within the H-ADM-COH amended class" not unrestricted.
6. SC-SCOPE is the largest substantive hypothesis; second-cumulant scope only.

## robustness v1.2 — attacks (CRITICAL)

1. Section 1 "This note closes ROBUSTNESS-MU2" vs banner "stays OPEN" -- contradiction. FIXED (v1.3: "advances ... does NOT close").
2. footer "CLOSED@[x0.5,x2]-2ND-CUMULANT" vs no-overclaim "NOT a closure: stays OPEN" -- contradiction. FIXED (v1.3: OPEN -> OPEN, no CLOSED@).
3. m(mu^2) bounded-not-recomputed => below the closure bar => ADVANCE not closure. Held.
4. 5-point table is not an interval theorem (sampled-sweep). Held.
5. J_eff 10% middle-intensity discrepancy = verdict-insensitive only, no precision claim. Held.
6. closes nothing outside second-cumulant scope. Held.

## superseded documents — attacks

- neargap-residual-closure v1.0: HISTORICAL; R-U10-1 numbers (2.7e-5, x130) and M'=-J(0) INVALIDATED; only R-U10-2 split-alignment survives. Body WATERMARK added.
- useries-verification-script v1.0: HISTORICAL; body asserts (-M'(r_hat)=J(0), remainder<=3.3e-5, protection>100) WRONG; never executed; use v0.2.0. Body WATERMARK added.
- robustness-mu2-step5b-remargin v1.0: HISTORICAL OVERCLAIM (declared CLOSED, removed from open_gates); WITHDRAWN. Body WATERMARK added.

## Actions taken (this commit)

- ROBUSTNESS-MU2 set to OPEN (FINAL) in GATES + B1 card + B1 open_gates restored.
- robustness note re-issued v1.3: all "CLOSED" wording removed; consistent "OPEN, numerically-supported advance" throughout (body, footer, no-overclaim).
- reading-h re-issued v2.2: footer/no-overclaim to three hypotheses (H-A0 removed); equality-classification lemma + explicit case-split partition added.
- WATERMARK lines added to the three superseded documents flagging their invalidated body numbers.
- review archived. No tier raised.
