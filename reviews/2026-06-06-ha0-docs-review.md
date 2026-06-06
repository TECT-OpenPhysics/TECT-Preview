# Operator adversarial review — H-A0 documents (2026-06-06)

**Reviewer**: operator. **Documents**: ga0-dui-closure, ha0-removal-pathway v2.0.
**Binding outcome**: H-A0 DISCHARGED AT THE PRODUCTION ANCHOR mu^2=0.005 ONLY;
G-A0-DUI CLOSED; H-ANCHOR DEMOTED to a verified anchor fact; ROBUSTNESS-MU2 OPEN;
full H-LAYER / B1 exact theorem NOT closed by these documents. This file is the
canonical archive (CLAUDE.md §6.3.5).

## Required official status (operator, verbatim intent)

- H-A0: DISCHARGED at the production anchor mu^2 = 0.005 (NOT on a full mu^2 interval).
- G-A0-DUI: CLOSED.
- H-ANCHOR: DEMOTED to VERIFIED ANCHOR FACT (anchor only, dependent on A1-KERNEL-CONV).
- ROBUSTNESS-MU2: OPEN.
- Full H-LAYER / B1 exact theorem: NOT closed by these documents.
- Any "H-A0 fully removed" statement MUST be followed by "at the production anchor (mu^2=0.005)".

## ga0-dui-closure — attack points

1. DUI local-differentiability must be two-sided: fix m>0, m0=m/2, |h|<m/2 ⇒ all
   intermediate ∈[m/2,3m/2] ≥ m0; same dominator both sides.
2. State all three domination regions: k→0 (O(k²)), k→q0 (D≥m0), k→∞ (k^-6).
3. "A=0 uniqueness unconditional" is anchor-pinned (mu^2=0.005 only); off-anchor
   is ROBUSTNESS-MU2.
4. H-ANCHOR demotion valid, but the anchor dependency is RETAINED (m*>m_w, M_R>M_c
   under A1-KERNEL-CONV at mu^2=0.005); must stay visible in B1/B2 cards.
5. machine 23/23 = proof AUDIT (quadrature sanity); the proof carrier is dominated
   convergence, not the PASS count.
6. T4 doc reducing B2/B1 hypotheses does NOT promote them by itself: it replaces a
   named hypothesis by a verified anchor dependency inside the already-T6 theorem;
   no tier-number change.
7. "A=0 uniqueness unconditional" ≠ "H-LAYER solved": forbidden to write "H-LAYER
   is now unconditional"; allowed "A=0 uniqueness unconditional at the anchor".

## ha0-removal-pathway v2.0 — attack points

1. v2.0 alone is H-A0 → H-ANCHOR + G-A0-DUI (a replacement, NOT a full discharge);
   full discharge needs the ga0-dui-closure note. Do not cite v2.0 alone as "H-A0
   fully discharged".
2. H-ANCHOR weakened to one inequality m*>m_w, but pinned to mu^2=0.005; the
   sharpened residual is ROBUSTNESS-MU2 (OPEN) — H-A0 vanishing does not weaken or
   auto-close ROBUSTNESS-MU2.
3. L2/L3 gluing (M≥M_c ⟺ m≤m_c) relies on M strictly decreasing = L1; in v2.0
   alone (L1 = G-A0-DUI residual) the gluing is conditional, closed by ga0-dui.
4. m_c=19.96 is the monotone threshold solving M(m_c)=M_c, NOT an operating mass
   (m*=0.3045, m_w=0.0392) — state this to avoid the "outside physical interval?"
   confusion.
5. sign-decomposition applies to the A=0 section only — not A≠0, anisotropic,
   off-diagonal covariance, or full H-LAYER competitor class.
6. "quadrature-scheme systematic exits the chain" holds for curve-shape
   certification; anchor-constant provenance (m*, M_R) remains under A1-KERNEL-CONV
   and the gap equation — not "all numerical dependence removed".
7. "G-A0-VER CLOSED" + "G-A0-DUI residual" can confuse externally: G-A0-VER = the
   sign-decomposition/machine arithmetic (closed here); G-A0-DUI = analytic
   regularity (closed only in the follow-up). v2.0 = execution; ga0-dui = completion.

## Combined verdict

- ha0-removal v2.0: H-A0 → H-ANCHOR + G-A0-DUI.
- ga0-dui v1.0: G-A0-DUI closed; H-ANCHOR → verified anchor fact.
- ⇒ H-A0 removed AT mu^2=0.005, NOT on a full mu^2 interval. ROBUSTNESS-MU2 stays OPEN.
- B1/B2 hypothesis-set reduction is a STRENGTHENING, not a TOE closure (B1 keeps
  H-LAYER, H-ADM-COH, SC-SCOPE; B2 keeps H-LAYER).
- "verified fact" is tracked, not deleted: GATES H-ANCHOR row kept as VERIFIED FACT,
  anchor-only, dependent on A1-KERNEL-CONV.

## Actions taken (this commit)

- **ROBUSTNESS-MU2 RE-OPENED**: the prior [x0.5,x2] "closure" rested on a
  bounded-not-recomputed exact m(mu^2); reclassified to a numerically-supported
  ADVANCE (note robustness-mu2-step5b-remargin re-issued v1.1; gate OPEN; B1
  open_gates += ROBUSTNESS-MU2).
- **ga0-dui-closure re-issued v1.1**: two-sided differentiability + three-region
  domination + prominent anchor-only + verified-fact-retained + A=0≠H-LAYER +
  23/23=audit.
- **ha0-removal-pathway re-issued v2.1**: scope-fence banner (replacement not
  discharge; anchor-only; A=0 section only; constants retained) + m_c-threshold and
  G-A0-VER/DUI clarifications.
- **B1/B2 cards**: anchor-dependency-retained-as-verified-fact language; H-A0
  discharged at anchor only; ROBUSTNESS-MU2 OPEN. No tier changed.
