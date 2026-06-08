# 2026-06-08 -- DR-2 decoupling route: critical audit

**Reviewer:** operator (Jusang Lee)
**Verdict:** the l2-decoupling route is PROMISING (T5-T6 candidate) but the first
draft (dr2-decoupling-closure v1.0) is NOT a closure -- it has a fatal formal
error. DO NOT flip DR2-SHARE; do NOT remove H-ADM-COH from B1. No tier change.

## Three findings (all UPHELD, all actioned)
1. **The E_+ = integral_{[0,1]^3} |f|^4 identity is FALSE.** Torus orthogonality
   needs q in Z^3; q in S^2 is generally non-integer, so the exponential integral
   is a sinc product, not a Kronecker delta. CORRECTION: the exact additive energy
   is the Besicovitch mean lim_R (1/|B_R|) int_{B_R} |f|^4, and the decoupling-
   usable upper bound is the Schwartz majorant E_+ <= C int |f|^4 eta_R
   (eta nonneg Schwartz, hat-eta >= 1 near 0). Applied in note v1.0 (corrected),
   Section 2.
2. **The non-separated multi-scale reduction was omitted** but is load-bearing for
   'arbitrary finite Q' (the actual DR-2). CORRECTION: note Section 4 now writes
   the dyadic-separation-scale reduction (rescale each cap to a paraboloid patch),
   with the CROSS-SCALE energy step explicitly marked OPEN. Hence the unrestricted
   DR-2 is T3 PROOF SKETCH; only the SEPARATED case is T6 PROVED CONDITIONAL.
3. **N^{2+eps} is not N^2 log^B N.** N^2 log^B => N^{2+eps}, not conversely.
   CORRECTION: note Section 5 distinguishes them; the route delivers N^{2+eps}
   only. For the finite-n_adm TECT application N^eps is a bounded constant, but the
   asymptotic theorem must state N^{2+eps}.

## Operator-recommended status (recorded)
DR-2 via decoupling: RECOMMENDED CONDITIONAL CLOSURE pending the corrected
localisation (done) and the multi-scale cross-scale write-out (OPEN). Do not flip
DR2-SHARE; keep H-ADM-COH in B1. Three lemmas to finish: correct energy-norm
localisation (done), separated discrete decoupling bound (done, cited), non-
separated multi-scale reduction (cross-scale step remaining).

## Actions
- Note v1.0 corrected same-session (Section 2 majorant; Section 4 multi-scale
  sketch with OPEN cross-scale step; Section 5 N^{2+eps} vs N^2 log^B; tier split
  separated-T6 / unrestricted-T3; first-draft over-claim retracted).
- R-022 downgraded T6 -> T4. DR2-SHARE annotation corrected; NO flip. B5 T5, B1 T6,
  H-ADM-COH retained.

## Credit
The L^4-localisation correction, the multi-scale-reduction requirement, and the
N^{2+eps} vs N^2 log^B distinction are reviewer-directed; they prevented an
over-claimed gate flip.
