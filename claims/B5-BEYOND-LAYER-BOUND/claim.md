# B5-BEYOND-LAYER-BOUND — Pattern-generic Gershgorin reduction of the beyond-layer bound

**Tier**: T7 (TSv2; T7-SCOPE on the admissibility-bounded statement, operator route-3 promotion 2026-06-13; label B5-BeyondLayer-T7Scope-260613) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-13

> CANONICAL CURRENT STATE: `status.json` (T6 PROVED-CONDITIONAL, label `B5-BeyondLayer-T6Conditional-260612`; dossier `T5-DOSSIER/notes/t6-conditional-assignment-260612-v1.0`). The Statement/Scope prose below is the historical T4-era card retained as record; the header had been stale at T4 since 2026-06-05 (sync defect, fixed at this card edit).

## Statement

Lemmas A (Gershgorin--Schur row bound), B (second-order log-det envelope with the isotropic trace identity), C$'$ (transfer matching: $|w_t|\le 2\lambda' I$, $m_t\le 2n$, exact $\ell^1$ identity $\sum_t|w_t| \le \lambda'(4S^2-2I)$), and D ($\ell^2$ mass $\le 8n(\lambda' I)^2$) are rigorous and pattern-independent. They yield the DERIVED closed-region theorem: STEP-5B holds for every admissible single-shell pattern with $n \le n_{\max}(I)$ = 62/31/16/6/3 at $I = 10^{-4}..2\times10^{-3}$ ($a\le0.75$). Residual: G1$'$ (thin-spread, $n > n_{\max}(I)$) + G2 (vertex bookkeeping). v1.3 adds Lemma E (sphere additive energy, diagonal/off-diagonal split): $\sum_t|w_t|^2 \le 4\lambda'^2I^2(\varphi+\nu^*)$ with participation $\varphi=n\sum A_i^4/I^2$ and discrete nonzero-translate overlap $\nu^*$ — giving the transversal n-FREE corollary ($\nu^*\le4$, $\varphi\le1$: margin ratios 131x/16x/2x at $I=4\times10^{-4}/10^{-3}/2\times10^{-3}$). v1.4 closes G1''(ring) for the canonical family: the equal-amplitude two-ring pattern has the EXACT closed form $c_{\rm ring}(n) = 14-18/n$ (n even; two heavy axial transfers $w=\lambda' I$) and $8-6/n$ (n odd; no axial resonance), both $<14$, any height — proven by five-orbit decomposition and verified to $10^{-10}$ at $n=7..64$.

## Scope

T4: Lemmas A/B/C'/D/E rigorous; closed region n<=n_max(I) DERIVED; transversal n-free corollary DERIVED modulo G1''(row); ring family CLOSED for the canonical equal-amplitude two-ring family (exact closed form < 14, both parities, theta-independent orbit combinatorics). NOT class-wide: G1''(row), G1''(glue: general decomposition incl. ring amplitude/tilt generality), G2 open.

**Notes**: v1.1 (same day): G1 attack landed — matching lemmas + derived n_max(I) region; tier T3->T4 with DA (incl. the in-session l1-constant correction caught by the verify loop) and quantitative sanity (exact ring identity match) recorded in the note and below. OPERATOR REVIEW VERDICT 2026-06-05: 'T4 valid reduction, not closure' — tier confirmed; two v1.0-era consistency sentences repaired in the v1.2 re-issue (section 1 tier sentence; section 5 boxes-now-derived sentence). v1.3: Lemma E landed (verify loop caught the c=0 diagonal contamination — second in-session catch); script v1.2.1, 69/69. v1.4: ring-family proposition CLOSED (exact c_ring(n), five-orbit proof; the missing hand-count piece was the even-n antipodal index-shift collapse); operator-flagged v1.3 footer staleness repaired; script v1.3.0, 94/94.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): A1-KERNEL-CONV only (the named DEFINITIONAL input, identical to the B1/B2 head; NOT a conditional proof hypothesis). No substantive conditional hypotheses. Definitional scope: the coherence-resolution admissible class C_adm. H-ENDPOINT-THINNESS-ACCEPTED removed (sunset hardening 2026-06-12); H-NONLATTICE-REMAINDER-EXCLUDED reclassified to definitional scope (route-3 2026-06-13, R-037: Lemma 2 caps T'<=10 for all admissible competitors). MANDATORY SCOPE QUALIFIER: B5 does NOT claim unrestricted arbitrary-Q DR-2; T-030 stays OPEN as a frontier strengthening
- Soft dependencies (context only): B1-RH-ENUM, B2-PROPA-HLAYER
- Open gates: STEP-5B

## Evidence

Grades: ANALYTIC, EXECUTED.

- `claims/B5-BEYOND-LAYER-BOUND/notes/beyond-layer-gershgorin-reduction-260605-260605-v1.5.tex.txt` (+ PDF)
- `codes/vacuum/beyond_layer_gershgorin_bound.py` (v1.0.1, 20 self-test asserts)
- `claims/B5-BEYOND-LAYER-BOUND/runs/260605-gershgorin-reduction/result.json`

## Falsifier

An admissible pattern inside a certified box (a(P)<1) whose exact off-diagonal Bloch correction exceeds the Lemma-B envelope; or any pattern undercutting the +0.00432 band margin at the anchor.

## Reproduction

Status: **AVAILABLE**. Command: `python codes/vacuum/beyond_layer_gershgorin_bound.py`.

Expected: claims 94/94 PASS (exit 0); artefact claims/B5-BEYOND-LAYER-BOUND/runs/260605-gershgorin-reduction/result.json; ring closed forms exact to 1e-10 at n=7..64; Lemma-E split verified on rings and random shells

## No-overclaim

Does NOT close STEP-5B; no promotion of Reading-H (B1 stays T5). The closed region is single-shell and anchor-pinned; the n-free l2 constant c~14 is measured evidence only; G1' and G2 are open.

## Devil's-advocate record (T3 -> T4 promotion, claim-standard §5)

1. (alpha) l1 growth in n — VALID-with-mitigation, SHARPENED: converted into
   the derived region n <= n_max(I); residual precisely G1' (thin-spread).
2. (alpha') "the author's constants may be wrong" — EXHIBIT: the v1.1.0
   assert with the wrong l1 constant (2S^2) FAILED on every config; ring
   measurement matched the corrected identity lam(4S^2-2I) to 1e-12. Caught
   by the verification loop pre-registration.
3. (beta) J(|t|) numerical only — DISMISSED (refinement drift < 6e-6;
   analytic shell estimate brackets J_max within 1.7x).
4. (gamma) global-minimum margin vs interval-wise floors —
   VALID-with-mitigation (conservative direction).

Quantitative sanity (mandatory): exact l1 identity equality on rings (1e-12);
n_max monotone in I asserted; a <= 0.75 at every certified point; 54/54.

## History

- 2026-06-05 — First issue at T3 (proof-sketch reduction): Lemmas A/B proven;
  STEP-5B reduced to gaps G1/G2; constants certified at the anchor
  (Math434 calibration reproduced; 20/20 asserts).
- 2026-06-05 — v1.1 (G1 attack): Lemmas C'/D + DERIVED closed-region theorem
  n_max(I) = 62/31/16/6/3; v1.0 boxes superseded by derivation; residual G1'
  named with n-uniform l2 ring evidence (c ~ 13.5); **T3 -> T4** (DA + sanity
  above; script v1.1.1, 54/54).
- 2026-06-05 — OPERATOR REVIEW VERDICT: "B1 migration revalidation passes;
  B5 Gershgorin reduction = T4 valid reduction, not closure; remaining
  blockers sharply reduced to G1' + G2." Tier T4 confirmed. v1.2 consistency
  re-issue repairs two stale v1.0 sentences flagged by the review.
- 2026-06-05 — v1.3 (G1' attack): Lemma E sphere-additive-energy split
  (sum w^2 <= 4 lam^2 I^2 (phi + nu*)) + transversal n-FREE corollary
  (ratios 131x/16x/2x); ring family separated onto the orbit route
  (c(n) saturates <= 13.72, n=8..64); residual restructured to
  G1''(row) + G1'b(ring proposition) + G1''(glue). Verify loop caught the
  c=0 diagonal contamination (second in-session catch). Script v1.2.1,
  69/69. Tier stays T4.
- 2026-06-05 — Third operator verdict: v1.3 "PASS as strengthened T4";
  footer staleness flagged. v1.4: footer repaired + **G1''(ring) CLOSED for
  the canonical family** — exact closed form c_ring(n) = 14-18/n (even) /
  8-6/n (odd) < 14, five-orbit decomposition proof (the hand-count gap was
  the even-n antipodal index-shift collapse, found by exact enumeration);
  verified 1e-10 at n=7..64. Script v1.3.0, 94/94. Tier stays T4.

## Next required action

G1''(row): heavy-transfer row-count theorem for the transversal class; then G1''(glue): transversal+cluster decomposition with bilinear cross-term control (subsumes ring amplitude/tilt generality); then G2 vertex completeness.


## Devil's-advocate record (T5 -> T6-CONDITIONAL promotion, 2026-06-12)

Full promotion-grade pass in `T5-DOSSIER/notes/t6-conditional-assignment-260612-v1.0` Sec.4
(three objections: (alpha) thinness-as-hypothesis -- VALID-with-mitigation, named in
H_B5^T6, T7 path = harden the sunset; (beta) estimate-grade inflation basis -- ADDRESSED,
the certified Parseval-pinned joint replaced it on W_SC; (gamma) evidence double-counting
vs the 2026-06-08 discharge -- DISMISSED, every promotion row is post-T5 evidence).
Quantitative sanity: the promotion changes no number; all values are published-bundle
values. Operator verdicts D1-A/D2-A/D3-A (T-031, 2026-06-12).


## Tier note (T6-conditional -> T7-SCOPE, route-3 promotion 2026-06-13)

Full record in `T5-DOSSIER/notes/b5-t7scope-assignment-260613-v1.0` (devil's-advocate
pass: alpha admissibility-is-definitional-scope-not-hypothesis ADDRESSED; beta A1 is a
definitional input like the head; gamma T-030-open-coexists-with-T7-SCOPE DISMISSED).
Attack-4 (T',n)-only chain audit discharged (dr2_t030_route3_nonloadbearing.py v1.1.0,
6/6). B5 = T7-SCOPE_{admissibility-bounded}, NOT unrestricted arbitrary-Q.
