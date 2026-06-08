# 2026-06-08 -- DR-2 decoupling route: corrected-version re-evaluation

**Reviewer:** operator (Jusang Lee)
**Verdict:** the corrected note is ACCEPTABLE, registered as a CORRECTED CONDITIONAL
ROUTE NOTE (not a closure). Do NOT close DR2-SHARE; H-ADM-COH stays in B1. No tier
change (separated T6 conditional / unrestricted T4 / DR-2 OPEN). Plus a binding
process correction.

## Process correction (binding)
Version-ups were being done as IN-PLACE edits of one v1.0 file; from now on follow
the document versioning rule (versioned RE-ISSUE: new vN.M file + superseded
pointer). ACTION: this revision is issued as dr2-decoupling-closure-260608-260608-
v1.1 (v1.0 superseded). Saved to memory (feedback-tect-document-versioning).

## Confirmed good (the corrections held)
- the false torus identity E_+ = int_{[0,1]^3}|f|^4 is retracted; Besicovitch
  mean / Schwartz majorant used instead.
- separated vs unrestricted cases separated; separated = T6 PROVED CONDITIONAL,
  unrestricted = T4 STRONG EVIDENCE.
- N^{2+eps} distinguished from N^2 log^B N.
- 'This is NOT a DR-2 closure' stated; H-ADM-COH retained.

## Adversarial points and actions
1. **unrestricted DR-2 still open** (multi-scale cross-scale induction not written).
   Confirmed; no flip. T4 STRONG EVIDENCE recorded.
2. **affine-invariance lemma supports but does not replace the cross-scale proof.**
   Confirmed; R-023 is a structural ingredient, not the completion.
3. **Schwartz-majorant details need to be tighter for T6** (eta choice + Fourier
   scaling; R vs minimal sumset gap; uniformity when the gap is small; decoupling
   ball-scale compatibility). ACTION: v1.1 Section 2.1 addresses all four -- the
   upper bound E_+ <= C int|f|^4 eta_R holds GAP-INDEPENDENTLY because hat-eta >= 0
   (off-diagonal terms only add), with R ~ delta^{-1} the decoupling ball scale.
   This makes the separated-case majorant-to-decoupling link clean modulo the cited
   theorem.

## Operator-recommended status (recorded)
Accept the corrected note as a strong DR-2 ROUTE, but do not close DR2-SHARE. To
close, the single remaining item is the full cross-scale induction-on-scales energy
bound; with it DR-2 would reach T6 PROVED CONDITIONAL on decoupling.

## Credit
The versioning-rule correction and the four majorant-rigor sub-points are
reviewer-directed; v1.1 incorporates them.
