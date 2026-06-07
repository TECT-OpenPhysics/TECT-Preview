# 2026-06-06 - Stale-language round 2 + appendix-lemma adversarial review

**Reviewer:** operator (Jusang Lee)
**Scope:** seven documents, per-document attack points only (no summary).
Second pass after the stale-language follow-up; targets residual closure
implications that survived in titles / section bodies / tables / footers, plus
two functional-analytic gaps in reading-h.
**Tier policy:** tiers FROZEN. The two reading-h appendix lemmas DISCHARGE
flagged sub-gaps within the existing T6-conditional structure; they do NOT
change the tier.
**Reviewed:** neargap-residual-closure v1.0; reading-h-t6-entry v2.2;
robustness-mu2-step5b-remargin v1.3; ga0-dui-closure v1.1; ha0-removal-pathway
v2.1; sunset-endpoint-refinement v1.0; robustness-mu2-step5b-remargin v1.2.

## Confirmed defects and actions (four priority directives)

### Priority 1 - robustness v1.3 title + Section 2 still imply closure
- DEFECT: title "Closing ROBUSTNESS-MU2"; Section 2 "the closure holds
  throughout with room"; Section 3 m(mu^2)=O(anchor) read as theorem; 5-point
  sweep read as monotonicity proof.
- ACTION: title -> "Advancing ROBUSTNESS-MU2: off-anchor STEP-5B re-margin
  evidence, gate stays open"; Section 2 -> "the STEP-5B off-anchor ratio stays
  above unity throughout, but ROBUSTNESS-MU2 remains OPEN pending the exact
  m(mu^2)"; 5-point sweep marked "sampled trend, not an interval-certified
  monotonicity proof"; Section 3 marked T4 EVIDENCE (not an analytic
  lower-bound theorem; closure would need m(mu^2) >= 0.4 m_anchor analytic /
  interval-certified + a certified J_eff envelope).

### Priority 2 - neargap v1.0 invalidated R-U10-1 body / expected-output
- DEFECT: Section 1 "This note closes both"; Section 2 full invalidated cascade
  (2.7e-5, x130, M'=-J(0)); footer Expected/Falsification quoted the stale
  ~2.7e-5 / ~3e-5 targets; R-U10-2 read as finished.
- ACTION: Section 1 -> historical framing (R-U10-1 INVALIDATED, near-gap
  protection now from common-mode resolution, only R-U10-2 retained as
  algebraic support pending a line-by-line exhibit); INVALIDATED fbox atop
  Section 2 listing the superseded numbers; footer Expected output -> "R-U10-1
  numerical targets INVALIDATED; not applicable", Falsification gate -> "R-U10-1
  INVALIDATED, no live numerical target"; Section 3 closes with an explicit
  "algebraic SUPPORT, not a final proof carrier" caveat.

### Priority 3 - sunset v1.0 invalidated x1.34 survives in table + footer
- DEFECT: Section 4 table still showed ~x3.2 / ~x1.34 as live; the feasibility
  sentence relied on them; footer precise-statement, M-ENDPOINT bracket,
  Expected output, and no-overclaim all carried the invalidated x1.34 /
  [0.1001,0.1094].
- ACTION: table cells -> "(INVALID)"; bold table note flags all U7
  intensity-dressed entries INVALIDATED; feasibility -> "third-cumulant sign at
  I>=1e-3 UNDETERMINED pending the corrected endpoint"; footer precise ->
  "OLD candidate ... INVALIDATED by the factor-2"; bracket note -> corrected
  lower end ~0.1047 (bracket narrows to ~[0.1047,0.1094] under M'=-J(0)/2);
  Expected output + no-overclaim aligned. (A self-introduced 90-char overfull
  hbox in the footer was caught by FORM-CHECK and fixed in the same turn.)

### Priority 4 - reading-h two appendix lemmas (re-issue v2.2 -> v2.3)
- DEFECT: equality classification relied on finite-matrix strict
  operator-monotonicity without stating the determinant/trace-class hypotheses
  for the continuum/per-volume trace-log; case-split crossover left as a
  "registered refinement".
- ACTION: re-issued as v2.3 (v2.2 superseded with forward-pointer) adding:
  * Appendix A (trace-log equality, determinant class): A = D0^{-1/2} lam' P^2
    D0^{-1/2} >= 0, trace-class (the finiteness already certified for Delta F);
    Tr ln(1+A)=0 => all eigenvalues 0 => A=0 => P^2=0. Renormalisation remark:
    the order-n minimal-subtraction remainder R_n(a) has R_n'(a)=(-1)^n
    a^n/(1+a), single-signed with R_n(a)=0 iff a=0, so the equality
    classification is scheme-independent.
  * Appendix B (sign-invariant covering partition): existence of M_- <= M_+
    with bulk bound for M>=M_-, near-gap floor for M<=M_+, cover
    A_adm = {M>=M_-} U {M<=M_+}; the verdict consumes only the overlap
    M_-<=M_+ (certified), the exact crossover is estimator-grade and
    verdict-irrelevant.
  Body equality-lemma and case-split paragraph now cite the appendices.

## Reviewer-confirmed (no action needed)
- reading-h v2.2 footer H-A0 removed + strict ">" -> ">=" : confirmed fixed.
- ga0-dui v1.1 / ha0-removal v2.1 status banners: confirmed ROBUSTNESS-MU2 OPEN.
- robustness v1.2 watermark: confirmed historical-overclaim withdrawn.
- DUI proof (three-region domination): defensible. M' sign-only (no auto-link to
  M'=-J(0)). H-ANCHOR must stay a VERIFIED-FACT dependency (not deleted).
  H-ADM-COH / SC-SCOPE remain substantive: T6 conditional, NOT T7.

## Verification
lint 18 claims / 30 gates; catalog 311; lineage PASS; release-check PASS;
pytest 3 passed; FORM-CHECK PASS + OVERFULL-HBOX 0 on all five edited/new notes
(reading-h v2.3 + v2.2, robustness v1.3, neargap v1.0, sunset v1.0).

## Credit
All four priority defects reviewer-identified.
