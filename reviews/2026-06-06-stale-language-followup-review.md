# 2026-06-06 - Stale-language follow-up adversarial review (Sector-B corpus)

**Reviewer:** operator (Jusang Lee)
**Scope:** eight documents, per-document attack points only (no summary).
Delivered after the internal-consistency review; targets residual stale wording
that survived the previous round.
**Tier policy:** tiers FROZEN. No promotion. All actions are wording /
consistency / quarantine corrections.
**Reviewed documents:** sunset-endpoint-refinement v1.0; ga0-dui-closure v1.1;
ha0-removal-pathway v2.1; neargap-residual-closure v1.0; robustness-mu2-step5b-
remargin v1.0 (historical); useries-verification-script v1.0 (historical);
reading-h-t6-entry v2.2; robustness-mu2-step5b-remargin v1.3.

## Confirmed defects and actions

### Priority 1 - reading-h v2.2 footer
- DEFECT (reviewer): footer "Tier before/after" still listed H-A0 in the
  hypothesis set {H-LAYER, H-A0, H-ADM-COH, SC-SCOPE}, contradicting the body
  (three hypotheses); footer precise statement used strict `>` while the theorem
  uses `>=` (strict only on the sub-resolution quotient).
- ACTION: footer hypothesis set -> {H-LAYER, H-ADM-COH, SC-SCOPE}; precise
  statement -> `F_total[P] >= F_total[R_H]` with "(strict on the sub-resolution
  quotient)".

### Priority 2 - robustness v1.3 residual "closed" prose
- DEFECT (reviewer): section 1 "established robust", section 4 title "cannot
  break closure", section 4 closing "the closure is therefore robust", devil's-
  advocate (gamma)/(delta) "the gate closes", and the final line "ROBUSTNESS-MU2
  is closed" all contradicted the OPEN banner/footer.
- ACTION: section 1 -> "off-anchor evidence SUPPORTS robustness ... pending
  exact m(mu^2) recomputation ... robustness reserve, NOT a closure"; section 4
  title -> "Robustness reserve under a hypothetical exact m(mu^2) confirmation";
  section 4 closing -> reserve framing; (gamma) -> "off-anchor advance covers";
  (delta) -> "the advance is numerically-supported ... not a closure"; final
  line -> "the gate ROBUSTNESS-MU2 remains OPEN pending the exact m(mu^2)
  recomputation".

### Priority 3 - ga0-dui v1.1 / ha0-removal v2.1 status-update banners
- DEFECT (reviewer): both top banners said ROBUSTNESS-MU2 "was subsequently
  updated to a SCOPED CLOSURE (CLOSED@[x0.5,x2]-2ND-CUMULANT, v1.2)" - obsolete;
  the live status (v1.3) is OPEN.
- ACTION: banners -> "intermediate v1.2 scoped-closure claim WITHDRAWN; LIVE
  status (v1.3) is ROBUSTNESS-MU2 OPEN with a numerically-supported off-anchor
  advance on [x0.5,x2] (m(mu^2) bounded-not-recomputed, does not meet the
  closure bar)".

### Priority 4 - sunset v1.0 section 2 quarantine (M'=-J(0) factor-2)
- DEFECT (reviewer): section 2 used M'(r_hat) = -J(0) (true: -J(0)/2) and called
  it "EXACT"; the downstream x1.34 endpoint is therefore correction-pending, yet
  the section read as a live derivation (copy-paste risk).
- ACTION: HISTORICAL/INVALIDATED fbox at the head of section 2 listing every
  superseded number (u_eff^2, 1.977e-3, x1.34); inline factor-2 flag on the
  section 2 identity, the section 5 sanity-check identity, the section 6/footer
  mentions, and the header summary; "endpoint failure removed" -> "CANDIDATE ...
  correction-pending".

### Consistency - neargap-residual-closure v1.0 footer (already watermarked)
- DEFECT (reviewer): the HISTORICAL watermark contradicted the footer, whose
  title said "closes R-U10-1 + R-U10-2" and body said "R-U10-1 CLOSED / R-U10-2
  CLOSED".
- ACTION: footer -> "(unit U11; HISTORICAL/SUPERSEDED)"; "R-U10-1 INVALIDATED
  (useries-triage: remainder 1.65e-3 not 2.7e-5; protection x2 not x130;
  M'=-J(0)/2 not -J(0)); R-U10-2 RETAINED AS ALGEBRAIC SUPPORT pending a
  line-by-line exhibit; NOT a final closure"; Status line -> HISTORICAL/SUPERSEDED.

### robustness v1.0 / useries-verification-script v1.0 (historical)
- Reviewer note: watermarks adequate, but body numbers (x130, 2.7e-5, M'=-J(0),
  the un-executed asserts) remain copy-paste hazards. No new action beyond the
  existing watermarks; flagged for full quarantine if ever re-cited. Current
  sources are robustness v1.3 and the corrected useries-triage v0.2.0.

## Live ledger after this round (tiers unchanged)
- B1-RH-ENUM: T6 CONDITIONAL on {H-LAYER, H-ADM-COH, SC-SCOPE}.
- H-A0: DISCHARGED at the production anchor; H-ANCHOR: VERIFIED ANCHOR FACT.
- ROBUSTNESS-MU2: OPEN, numerically-supported off-anchor on [x0.5,x2].
- Near-gap proof source: neargap-common-mode-resolution (not U11).
- SC-SCOPE: OPEN; sunset refinement correction-pending (factor-2).

## Verification
lint 18 claims / 30 gates; catalog 308; lineage PASS; release-check PASS;
pytest 3 passed; FORM-CHECK PASS + OVERFULL-HBOX 0 on all six edited notes
(PDFs rebuilt).

## Credit
All defect classes above were reviewer-identified.

## Post-review completeness audit (operator: check for missed updates)

A corpus-wide scan for status-implying paraphrases (not just the literal gate
name) found the missed update: the intermediate flip-flop versions robustness
v1.1 and v1.2 carried SUPERSEDED forward-pointers but, unlike v1.0, lacked the
withdrawal WATERMARK; their bodies still asserted 'ROBUSTNESS-MU2 is closed'
(v1.1) and 'CLOSED@[x0.5,x2]' (v1.2).

ACTION: added the v1.0-style withdrawal watermark to both (line 2, after the
forward-pointer). FORM-CHECK PASS + OVERFULL 0 on v1.1/v1.2.

Post-fix invariant (verified): every live `is closed` / `CLOSED@` string in
claims/ now resides in a watermarked-historical note (robustness
v1.0/v1.1/v1.2) or names an explicitly WITHDRAWN claim (ga0-dui v1.1,
ha0-removal v2.1 status-update banners). release-check PASS; catalog 309.
