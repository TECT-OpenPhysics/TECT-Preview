# DR-2 external research assessment: the reduction to Pencil Rigidity / Pair-Sum Surface Multiplicity

**Kind**: strategy / external-input review (non-tier-bearing,
governance/development-history.md §7). Cites claims/gates/results by ID; performs
NO tier or gate action.
**Bears on**: gate DR2-SHARE, B5-BEYOND-LAYER-BOUND, B1-RH-ENUM, results
R-002..R-009.
**First issued**: 2026-06-08.
**Source**: operator-supplied external research log "Math447 -- DR-2
Unrestricted-Class Direct Attack" (Math447--Math469, ~17k lines, autonomous
multi-pass). The raw log is bilingual and is NOT tracked in this repository
(English-only policy); this note is the English assessment of its mathematical
content and its incorporability.

## 1. What the external research is

A ~23-note multi-pass attack on DR-2 -- the *unrestricted-class* sphere
additive-energy bound `E_+(Q) <= C N^2 log^B N` for arbitrary finite `Q ⊂ S^2`,
the open route to closing STEP-5B without the H-ADM-COH amended class. The log
never closes DR-2; every pass ends OPEN. Its product is a sequence of
*reductions* of DR-2 to successively-named hard conjectures:

- a **sphere structure dichotomy** (Type I: `E_+ <= C N^2 log^B N`; or Type II:
  `Q` decomposes into `O(log^B N)` circle/coaxial clusters + a Type-I remainder);
- equivalently a **Pencil Rigidity Conjecture** / **Pair-Sum Surface Multiplicity
  (PSM) theorem** (Math452, the cleanest consolidated form);
- and several alternative equivalents explored in later passes (MCI averaged
  polar incidence, DSAO difference-support almost-orthogonality, translation-
  design rigidity, no-extremizer, right-rectangle count, moving-plane summation,
  rich-midpoint approximate-group / RMAG).

The consolidated reduction theorem (Math452) is:
`Pencil Rigidity ⇒ PSM ⇒ DR-2`.

## 2. Devil's-advocate verdict on the mathematics

**Honest and sound, at reduction/proof-sketch grade.** Specific findings:

- **The reduction `dichotomy ⇒ DR-2` is correct.** Decompose `Q = Q_rem ∪ ⋃_α
  Q_α` into `M = O(log^B N)` controlled clusters; each cluster obeys
  `E_+(Q_α) <= C_α |Q_α|^2` (the repo's closed circle/coaxial estimates); cross
  terms obey `E_+(Q_α,Q_β) <= sqrt(E_+(Q_α) E_+(Q_β))` (Cauchy--Schwarz on the
  representation functions). Summation gives `E_+(Q) <= C' N^2 log^{B'} N`. This
  is standard additive combinatorics and is valid.
- **The consolidated `Pencil Rigidity ⇒ PSM ⇒ DR-2` is a clean conditional
  theorem**, explicitly labelled "this note does not prove DR-2; it proves only
  the reduction". No over-closure.
- **Spot-checked sub-lemma (Pass 4, non-parallel circle cross-energy):**
  `E_+(A,B) <= 2|A||B|` for `A ⊂ C_1`, `B ⊂ C_2`, via `r_A(w) <= 2` (a circle and
  its translate meet in `<= 2` points). The bound is CORRECT. Minor imprecision:
  the stated bound uses only `r <= 2` and does NOT actually require the
  non-parallel hypothesis (`Π_1 ∩ Π_2 = line`) that the pass sets up; the
  hypothesis would be needed only for a sharper-than-`2|A||B|` estimate. This is
  representative -- the lemmas are sound but several carry non-load-bearing
  hypotheses or are proof-sketches, so each requires a per-lemma audit before any
  formal registration.

**Caveats to flag (must not be adopted verbatim):**

1. **Tier-language mismatch.** The log writes the Reading-H/B5 sector as
   `T7_conditional-robust`. The repository's canonical TSv2 tiers are **B5 = T5
   PINNED-CLOSURE @ H-ADM-COH amended class**, **B1 = T6 CONDITIONAL on {H-LAYER,
   H-ADM-COH, SC-SCOPE}**. The external `T7` label is aspirational and is NOT
   adopted; the repo tiers are canonical.
2. **Unverified "PROVED" labels.** Per TECT discipline, the sub-lemmas the log
   marks PROVED are not yet repository-grade; they need devil's-advocate +
   (where numerical) reproducible-script verification before a RESULTS-LEDGER row.
3. **Overlap with the existing chain.** The early content (single-circle
   `K=14` = R-002; antipodal-carrier partition = R-003; `ν*=μ_C` = R-004;
   stereographic incidence = R-006; rectangle reformulation + triple count =
   R-007; amplitude-dyadic lift = R-008; coherence-resolution / "finite coherent
   capacity" = R-009) DUPLICATES results already in the repo. The genuinely NEW
   content is the *reduction to Pencil Rigidity / PSM* and the alternative
   equivalent conjectures.

## 3. Strategic conclusion (matches the research's own decision)

The log's final decision is verbatim: *stop pushing unrestricted DR-2 as the
mainline closure route; register it as a support theorem and an independent math
branch; use H-ADM-COH + finite coherent capacity as the official STEP-5B closure
route.* This is **exactly the repository's current position**: DR2-SHARE is OPEN,
off the critical path; STEP-5B is CLOSED-CONDITIONAL on H-ADM-COH; B5 is T5. The
external research therefore CONFIRMS and REINFORCES the repo state with ~23
passes of evidence that DR-2 is genuinely hard, and it CONTRIBUTES one concrete
sharpening: the DR2-SHARE residual is now reducible to a single named conjecture
(Pencil Rigidity / PSM), rather than the looser "carrier-richness `χ(P) =
O(polylog)`" framing of dr2-extraction-lemmas v1.0.

## 4. Incorporability recommendation

- **TIER 1 -- done in this note (no tier/gate change).** Record the assessment;
  annotate DR2-SHARE with the sharpened residual (DR-2 ⇐ Pencil Rigidity / PSM,
  conditional reduction at proof-sketch grade) and a pointer here. DR-2 stays
  OPEN, off critical path; B5 stays T5; B1 stays T6.
- **TIER 2 -- operator decision.** Register "DR-2 ⇐ Pencil Rigidity / PSM" as a
  formal **CONJECTURE (T2)** with a pre-registered falsification gate, and seed a
  standalone math-paper note "Additive Energy and Spherical Rectangle Counts on
  `S^2`" (the log's own proposed independent-branch title). This formalizes the
  residual but does not close it.
- **TIER 3 -- later, per-lemma.** Verify (devil's-advocate + reproduction) any
  genuinely-new sub-lemma not already covered by R-002..R-009 -- candidate: the
  non-parallel circle cross-energy bound `E_+(A,B) <= 2|A||B|` -- before any
  RESULTS-LEDGER registration.
- **NOT done.** Wholesale import of the 23 notes (exploratory, unverified, and
  largely redundant with R-002..R-009); adoption of the `T7_conditional-robust`
  label; any claim of DR-2 closure.

## 5. Bottom line

The external research is honest, mathematically sound at reduction grade, and
strategically aligned with the repository. It does not move any tier. Its
incorporable value is (i) confirmation that DR-2 is correctly OPEN and
off-critical-path, and (ii) a sharpened, single-named residual for DR2-SHARE
(Pencil Rigidity / PSM). Recommended action: adopt Tier 1 now (this note +
gate annotation); decide Tier 2 (formal CONJECTURE registration + independent
math-branch paper) explicitly; defer Tier 3 (per-lemma verification) until a
specific lemma is needed.
