# CHANGELOG — TECT (verification-first repository)

One entry per accepted change set. Newest first. Entries reference claim IDs,
not pillar counts.

---

## [B5-AddA-v1.2] Verdict-#11 repairs + H-KBAL lift theorem (unconditional amplitudes) — 2026-06-05

- **OPERATOR REVIEW VERDICT #11 archived**: AddA v1.1 = PASS as repaired
  T4+ support; official basis = c_R = 4 sqrt(14) route; three stale spots
  flagged: (i) section-1 28/13 + "astronomically weak" remnant,
  (ii) section-5 sanity check still using 28/13 and the withdrawn 7.9e16
  ratio, (iii) footer "ANALYTIC (both routes)" overstatement — ALL
  REPAIRED (evidence grade now split ANALYTIC / PROVISIONAL-CITED).
- **NEW: H-KBAL LIFT THEOREM** — for ARBITRARY positive amplitudes:
  sum_{t!=0} w^2 <= 64 sqrt(7) lam^2 I^2 sqrt(n) log^2(2n) + O(lam^2 I^2)
  (amplitude-dyadic classes; per-class operator interpolation; bilinear
  energy E(A,B) <= sqrt(E(A)E(B)) machine-verified; Minkowski; tail
  absorption). **kappa-balance is no longer load-bearing** — it affects
  constants, not the architecture. Measured worst unbalanced ratio 0.03
  (powerlaw/exp/two-scale) vs theorem ceiling 2929: amplitude conspiracies
  cannot beat sqrt(n) polylog scaling; unbalanced profiles in fact reduce
  the ratio.
- Ledger threshold UNCHANGED (1.59e5, sharp-constant balanced route);
  lift-constant sharpening registered as follow-up.
- AddA note v1.2 re-issue (FORM-CHECK PASS, Overfull 0); script v1.10.0
  (170/170). **B5 = T4+ . Residual = {H-ADM} + DR-2 + constant
  follow-ups. STEP-5B remains OPEN.**

## [B5-AddA-v1.1] Verdict-#10 repairs: exponent 20/9 (catch #7); 7.9e16 withdrawn; dichotomy program registered — 2026-06-05

- **OPERATOR REVIEW VERDICT #10 archived**: AddA v1.0 = PARTIAL PASS.
  c_R = 4 sqrt(14) ACCEPTED at theorem grade (official ledger threshold
  n <= 1.59e5 at the anchor under H-KBAL). The 28/13 incidence exponent
  REJECTED — **operator-caught arithmetic slip (verify-loop catch #7)**:
  the correct pair-cap/AS crossover is r1 = (NL/2)^{2/9}, exponent 20/9.
- **Repairs (operator choices A + C)**: exponent fixed to 20/9 with a
  numerical dyadic self-check (ratio 1.1 at N = 4096); the 7.9e16 reach
  WITHDRAWN; repaired provisional reach 2.2e10 (conservative c = 30),
  excluded from ledger thresholds until the Aronov-Sharir constant is
  pinned; verified closure condition restated with the sqrt-n route
  (mode separation >~ 5e-3).
- **NEW dichotomy program (the better-method search)**: DR-1 (no small
  doubling on circles — proved in substance by the fiber rigidity of the
  universal single-circle theorem) + DR-2 (sphere Freiman-type structure
  dichotomy — OPEN, multi-turn designated attack) => would force the
  sharp O(N^2 polylog) unconditionally, bypassing open incidence
  conjectures.
- AddA note v1.1 re-issue (FORM-CHECK PASS, Overfull 0); script v1.9.1
  (167/167). **B5 = T4+ (theorem-supported) per the verdict-#10 ledger.
  STEP-5B remains OPEN.**

## [B5-AddA] Rectangle-constant closure: operator-derived c_R = 4 sqrt(14); incidence route 28/13; conditional closure — 2026-06-05

- **OPERATOR REVIEW VERDICT #9 archived**: v2.0 = PASS as major strengthened
  T4. The operator SUPPLIED the theorem-grade derivation c_R = 4 sqrt(14)
  (sum p^3 <= 7 N^3 via triple count + thin class; Cauchy-Schwarz
  interpolation) and the Route-A/Route-B closure analysis — archived with
  attribution in the AddA note (CLAUDE.md section-4 discipline).
- **Operator derivation VERIFIED**: sum p^3 <= 7N^3 and the interpolation
  hold on all configs; region n <= 1.59e5 at the anchor (operator quoted
  1.58e5 — reproduced).
- **NEW INCIDENCE ROUTE (this session)**: stereographic projection maps
  carriers to plane circles EXACTLY (residuals 1e-30); planar
  Aronov-Sharir-type rich-circle bounds + the pair cap give
  sum_C p_C^2 = O(N^{28/13} polylog) — exponent 2.154 < 5/2 — pushing the
  theorem-grade reach to **7.9e16 modes at the anchor** (eleven orders
  beyond the sqrt-n route).
- **CONDITIONAL CLOSURE registered**: STEP-5B holds under named
  {H-KBAL (kappa-balance), H-ADM (n <= n_adm)} for ANY n_adm < 7.9e16 —
  operator packing form: mode separation >~ 1e-8 suffices. Sharp O(n^2)
  conjecture pre-registered (measured growth exponents 2.04/2.06/2.08 on
  rand/ring/coax; falsification gate: exponent >= 2.3).
- New AddA note rectangle-constant-closure-260605-v1.0 (.tex.txt + PDF,
  FORM-CHECK PASS, Overfull 0); script v1.9.0 (166/166). LaTeX catch:
  raw math in the banner title broke text-mode \title — reworded.
- **Tier: T4 with TIER PROPOSAL submitted (T5, or T6 CONDITIONAL on
  {H-KBAL, H-ADM}) — decision is the operator's. STEP-5B: residual is now
  CONDITIONALITY ONLY.**

## [B5-v2.0] MAJOR: rectangle reformulation; triple-count R=O(n^{5/2}); coaxial H*-repair; region ~2.2e6 — 2026-06-05

- **OPERATOR REVIEW VERDICT #8 archived**: v1.9 = PASS as major strengthened
  T4; two audit requests: (i) prove height coincidences cannot create
  hidden carrier multiplicity, (ii) amplitude-weighted coaxial bound.
- **Coaxial lemma REPAIRED (H*-explicit)**: the v1.9 uniqueness step now
  carries the height-sum multiplicity H*(c). AP-HEIGHT AUDIT with FORCED
  coincidences (m=3/5/7 stacks): off-axis carriers stay at 4 ordered pairs
  (H*=1) — the in-plane reflection condition separates cluster pairs;
  K decreases with m (9.25/8.75/8.54); random-amplitude stack K=8.31.
- **RECTANGLE REFORMULATION THEOREM**: off-diagonal carrier energy =
  weighted count of rectangles inscribed in sphere circles (two antipodal
  pairs = two diameters); diagonal <= 8I^2 unconditional; split exact to
  1e-15.
- **TRIPLE-COUNT THEOREM**: three points determine at most one circle =>
  sum_C k_C^3 = O(n^3); dyadic optimization => **R = O(n^{5/2})
  UNCONDITIONAL** (extremal profile forced to richness <= sqrt(n)).
- **sqrt(n) corollary**: kappa-balanced K(n) <= 8 + c_R sqrt(n) (c_R
  measured ~4) => closed region upgraded THREE ORDERS OF MAGNITUDE:
  ~2.2e6 / 5.3e4 / 2.8e3 modes at I = 4e-4 / 1e-3 / 2e-3 (K-budget 5972
  at the anchor).
- Note v2.0 MAJOR re-issue (FORM-CHECK PASS, Overfull 0); script v1.8.0
  (155/155). **Tier stays T4 (T5-candidacy flagged). STEP-5B remains
  OPEN** on the extreme-n corner + first-principles c_R.

## [B5-v1.9] Antipodal-carrier partition; nu*=mu_C; coaxial-class closure; G1'''-AE sharpened to p_0 — 2026-06-05

- **OPERATOR REVIEW VERDICT #7 archived**: v1.8 = PASS as major strengthened
  T4; flagged (i) footer no-overclaim still carrying 'anomalous-block
  sub-check is open' (conflicts with the v1.8 discharge) and (ii) the
  section-6 (alpha) stale 'residual is exactly G1-prime thin-spread' —
  both REPAIRED in v1.9.
- **Antipodal-carrier partition theorem**: every ordered pair (u,v),
  u+v != 0, is an antipodal pair of exactly ONE circle (centre (u+v)/2);
  the pair set partitions; Phi_s = Psi_{C_s}; l1/l2 reconstructions
  machine-exact (1e-12/1e-15).
- **Identity nu* = mu_C**: the transversality parameter equals the
  max-points-on-a-circle parameter (shifted-shell overlaps ARE circles) —
  the Lemma-E route and the circle route are governed by one parameter.
- **Coaxial-class closure theorem**: off-axis carriers of coaxial unions
  hold <= 2 unordered antipodal pairs (reflected-circle intersection <= 2;
  coincidence forces on-axis centre); equal-radius +/-z mirror carrier
  sits at s = 0 (excluded); K <= 30 absolute, measured 9.40/10.73.
  **The pre-registered suspected-hard class is CLOSED.**
- **Honest falsification record**: H-GEN(2) (naive thin-carrier hypothesis
  for arbitrary multi-circle unions) is FALSE — 10 ordered pairs observed
  on a non-cluster carrier of ring8+ring10+rand6; K stays < 32 throughout.
  **G1'''-AE sharpened to: bound the carrier-richness p_0(P) class-wide.**
- Verify-loop catch #6: first mirror-pair test config degenerate
  (duplicate points: ring(pi-0.7) == -ring(0.7) at n=10); rebuilt with
  phase offset + nondegeneracy assert.
- Note v1.9 re-issue (FORM-CHECK PASS, Overfull 0); script v1.7.1
  (145/145). **Tier stays T4 (T5-candidacy flagged). STEP-5B remains
  OPEN** on the p_0 corner.

## [B5-v1.8] Position-space structure; universal single-circle theorem (K=14 sharp); G1'''-AE = discrete sphere L^4 — 2026-06-05

- **OPERATOR REVIEW VERDICT #6 archived**: v1.7 = PASS as a major
  strengthened T4; flagged the Gershgorin-led section-4 statement —
  section 4 REWRITTEN around the structural floor (Gershgorin demoted to
  superseded auxiliary route, retained as route history/cross-check).
- **Position-space structure**: P = multiplication by F(x) = phi_n(x), so
  W = lam(F^2 - 2I) is a multiplication operator and D + W >= D_0 holds
  POINTWISE. **Nambu/anomalous objection DISCHARGED**: real scalar order
  parameter => single real symmetric Hessian (Math427 K-hat); no
  independent pairing block exists at this scope.
- **Parseval reformulation**: sum_{t!=0} w^2 = lam^2(<F^4> - 4I^2) —
  G1'''-AE IS the discrete sphere L^4-extension problem (Stein-Tomas
  exponent q = 4 at d = 3; curvature = circle-fiber rigidity). MC-verified
  0.5%/7.5%.
- **UNIVERSAL SINGLE-CIRCLE THEOREM (sharp)**: any amplitudes, any n, any
  height on one circle: sum_{t!=0} w^2 <= 14 lam^2 I_c^2, by fiber
  enumeration (top-top/bottom-bottom <= 2 ordered pairs -> 4 I_c^2;
  cross <= 4 -> 8 I_c^2; two axial -> 2 I_c^2). Equal-amplitude rings
  attain 14 - 18/n: constant SHARP. The equal-amplitude caveat of the
  ring family is REMOVED; all single-circle patterns are closed.
- **Coaxial falsification probe** (pre-registered): K = 9.9/10.4/10.7 at
  2x8/16/32 — bounded; supports absolute-K, NOT a proof.
- Note v1.8 re-issue (FORM-CHECK PASS, Overfull 0); script v1.6.0
  (132/132). **Tier stays T4 (T5-candidacy flagged). STEP-5B remains OPEN**
  on the multi-circle corner (G1'''-AE).

## [B5-v1.7] P^2-representation theorem: structural spectral floor closes G1''-M4; N_max x46 — 2026-06-05

- **OPERATOR REVIEW VERDICT #5 archived**: B5 v1.6 = PASS as strengthened T4;
  STEP-5B not closed; Reading-H selection unchanged (T5). Two flagged stale
  sentences (section 1 "two named gaps"; section 5 "thin-spread remaining")
  repaired in the v1.7 re-issue.
- **Structural theorem (the key)**: $W = \lambda'(P^2 - 2I\,\mathrm{Id})$,
  $P = \sum_u A_u S_u = P^\dagger$ — the matched transfer weights are
  exactly the off-diagonal coefficients of $\lambda' P^2$ and the $t=0$
  coefficient $2\lambda' I$ is exactly the dressing $\hat r - r_R$ (the
  Lemma-C' l1 identity was this structure in disguise). Hence
  $D + W = D_0 + \lambda' P^2 \ge D_0 > 0$ UNCONDITIONALLY and
  $X \ge -a_0$, $a_0 = 2\lambda' I/\hat r \approx 0.021$ at the anchor —
  n-free, pattern-free. **Gershgorin obsolete; G1''-M4 CLOSED BY STRUCTURE.**
- Machine verification (script v1.5.0, 126/126): P^2 identity exact
  (mismatch 0 over all transfers; t=0 = 2I to 1e-12); spectral floor holds
  on every adversarial finite section (rings near-sharp -0.0123 vs -0.0207;
  composites; near-coincident pairs; 75-dim stressed section) — sections can
  only falsify the floor, and none does.
- **Enlarged closed region**: N_max(I) = 12133/3017/746/115/27 at
  I = 1e-4..2e-3 (vs 62/31/16/6/3 Gershgorin: x46 at the production anchor).
- **Residual reduced to a single gap**: G1'''-AE — class-wide weighted
  sphere additive-energy bound sum w^2 <= K (lam I)^2 on the corner
  {n > N_max(I), non-transversal, non-ring}; G-DEC demoted to sub-route.
  Anomalous-block scope sub-check registered (devil's-advocate delta).
- Note v1.7 re-issue (FORM-CHECK PASS, Overfull 0); **tier stays T4 with
  T5-candidacy flagged for operator. STEP-5B remains OPEN.**

## [B5-v1.6] STEP-5B closing sweep: G2 bookkeeping closed; glue l2 theorem; row route refuted (registered negative result) — 2026-06-05

- **Operator directive**: "prove in order through to closing" (row -> glue -> G2).
- **Lemma F** (collar heavy-mass bound, provable bilinear constant
  $2\lambda'I(\kappa+\nu_S^{\ne})$): the on-pattern rows $k=-u$ genuinely see
  $2n$ on-shell partners; their MASS is n-free by the diagonal/off-diagonal
  centre split.
- **Registered NEGATIVE result**: the row/collar-ladder route FAILS $a<1$ at
  production $I$ with the provable constant ($a_{\rm prov}=2.20/4.68$ at
  $n=12/24$). Verify-loop catch #4 (collar functional included the $c=0$
  centre) and catch #5 (the exploratory $\sqrt{\nu}$ ladder constant was NOT
  a theorem — caught by the devil's-advocate pass BEFORE registration; with
  the rigorous constant the certificate fails). G1''(row) reduced to the
  $\mathrm{tr}\,X^4$ additive-energy ($E_4$) moment problem = designated
  attack **G1''-M4**.
- **G2 CLOSED at second-cumulant bookkeeping level**: Lemma H (sextic
  $\varepsilon_4 = 60vnI/\lambda' \le 0.16$ on the closed region), Lemma I
  ($\sigma$-channel completeness, exact to $10^{-12}$), Lemma J (two-shell
  denominator floor $\times 1.70$).
- **Composite-glue l2 theorem**: $\nu_{\rm cross} \le 4$ (distinct circles);
  certificate validated (measured 9.27 vs certificate 34.23). Residual
  G-DEC = decomposition existence.
- Note v1.6 re-issue (FORM-CHECK PASS, Overfull 0, PDF beside source);
  script `beyond_layer_gershgorin_bound.py` v1.4.4 (111/111 asserts);
  artefact refreshed. **Tier stays T4. STEP-5B remains OPEN** — residual =
  G1''-M4 + G-DEC; any tier action requires operator sign-off.

## [Claim-Package] Run artefacts moved into claim packages; banner-loss caught and restored — 2026-06-05

- **Operator design decision**: `runs/` relocated into the claim package —
  `claims/<ID>/runs/<YYMMDD>-<descriptive-tag>/` — completing the package
  principle (card + status + notes + runs in one folder; code stays shared in
  `codes/`). The original size rationale for a separate top-level `runs/` is
  void since large binaries are git-ignored wherever they live. 16 artefact
  files moved (A1/B1/B2/B5); 25 reference files swept; policies
  (claim-standard §1, verification-standard §4, naming §6), catalog v1.1.3,
  producing script v1.3.1, .gitignore patterns updated; top-level `runs/`
  retired.
- **Three path-consistency note re-issues** (current versions cite artefact
  paths): B1 record → v1.1, B2 record → v1.4, B5 reduction → v1.5; superseded
  versions keep the OLD paths (historical record) with forward pointers.
- **Verify-loop catch #3 (process)**: the B5 re-issue's anchor assert exposed
  that the v1.2–v1.4 revision-history entries had been silently LOST by
  assert-less banner edits in earlier re-issues; the v1.5 banner restores the
  full cumulative history from the CHANGELOG record. Lesson recorded: banner
  edits in re-issues must use asserted anchors (no silent .replace).
- No tier changes; linter PASS; all generated surfaces in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [STEP-5B/Ring-Theorem] Exact ring-family closed form; G1''(ring) canonical-family CLOSED — 2026-06-05

- **Third operator verdict archived**: B5 v1.3 = "PASS as strengthened T4";
  footer staleness flagged (54/54, pre-Lemma-E residual) — repaired in v1.4.
- **Ring-family proposition PROVEN** [B5-BEYOND-LAYER-BOUND v1.4]: for the
  canonical equal-amplitude two-ring pattern (regular n-gon at height z plus
  antipodal image), the five-orbit decomposition of the transfer set gives
  the EXACT closed form **c_ring(n) = 14 - 18/n (n even) / 8 - 6/n (n odd)**,
  both < 14, any height (theta-independent orbit combinatorics) — verified
  to 1e-10 at n = 7..64 (script v1.3.0, 94/94 asserts). Structure: even n
  carries exactly two heavy axial transfers t = (0,0,±2z) with w = lam I
  (the n-fold collapse of antipodal same-ring pairs); odd n has NO axial
  resonance (c < 8). The earlier hand count missed the even-n antipodal
  index-shift collapse (e_{k+n/2} = -e_k => cross transfers carry 4A^2) —
  found by exact orbit enumeration.
- **Residual now**: G1''(row) (heavy-transfer row count for transversal
  patterns) + G1''(glue) (general decomposition; subsumes ring
  amplitude/tilt generality) + G2 (vertex bookkeeping). STEP-5B stays OPEN;
  B5 stays T4; no tier action on B1/B2.
- Note v1.4 re-issued (FORM-CHECK PASS, Overfull 0, PDF beside source;
  v1.3 superseded, kept).

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [STEP-5B/Additive-Energy] Lemma E n-free split; transversal corollary; batch-1 signed — 2026-06-05

- **Second operator verdict archived**: "B2-PROPA-HLAYER migration v1.3 =
  PASS" — batch-1 ledger rows SIGNED; "B5 v1.2 = PASS as T4 reduction";
  G1' attack directed.
- **Lemma E (sphere additive energy, rigorous)** [B5-BEYOND-LAYER-BOUND
  v1.3]: writing w_t/lam = (f*f)(t), AM-GM over energy quadruples
  x+y = x'+y' with the diagonal/off-diagonal split gives
  **sum_t |w_t|^2 <= 4 lam^2 I^2 (phi + nu*)**, phi = n sum A^4/I^2
  (participation, = 1 for equal spread), nu* = max nonzero discrete-translate
  overlap of Qhat. n enters ONLY through nu*.
- **Transversal n-FREE corollary**: for nu* <= 4, phi <= 1 (random shells
  measure nu* = 2, c_meas = 7.5–7.75 <= 12): margin ratios **131x/16x/2x**
  at I = 4e-4/1e-3/2e-3 — modulo the G1''(row) heavy-transfer row count.
- **Ring/degenerate family separated** (nu* ~ n there via the vertical
  antipodal displacement): c(n) measured 11.75 -> 13.72 saturating over
  n = 8..64, <= 16; designated route = rotation-orbit decomposition
  (G1'b proposition).
- **Verify loop catch #2**: the v1.2.0 circle count included the c = 0
  diagonal (nu = 2n everywhere); failed transversal asserts exposed it;
  corrected in v1.2.1 (69/69). Template gained the corollary theorem env
  (one-place extension per the standard-LaTeX rule).
- Residual now: G1''(row) + G1'b(ring) + G1''(glue) + G2. STEP-5B stays
  OPEN; B5 stays T4; no tier action on B1/B2. Note v1.3 re-issued
  (FORM-CHECK PASS; Overfull 1 -> 0 via display split; PDF beside source).

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Operator-Review] B1 migration PASS; B5 confirmed T4; consistency re-issue v1.2 — 2026-06-05

- **Operator review verdict archived**: "B1-RH-ENUM migration = PASS"
  (evidence chain migration-clean and reproducible; 167/167) — migration
  batch-2 ledger rows signed; "B5 / STEP-5B Gershgorin reduction = T4 valid
  reduction, not closure" — tier T4 confirmed; "remaining blockers sharply
  reduced to G1' + G2"; Reading-H selection stays T5 CLOSED@ESTIMATOR-GRADE.
- **Two documentation defects flagged by the review, repaired in the v1.2
  consistency re-issue** [B5-BEYOND-LAYER-BOUND]: (i) section 1 still said
  "registered at T3" — now "registered at T4 because Lemmas A/B/C'/D and the
  closed-region theorem are now derived"; (ii) section 5 still carried the
  v1.0 sentence "calibrated boxes are stated regions, not derived caps" —
  now "the v1.0 boxes are DERIVED within the closed-region theorem; the
  non-derived residual is the thin-spread regime n > n_max(I), recorded as
  G1'". No mathematical change; v1.1 superseded, kept; FORM-CHECK PASS,
  Overfull 0, PDF re-issued beside source.
- Next mathematical target (operator-confirmed): **G1'** — the n-free l2
  theorem sum_t |w_t|^2 <= c (lam I)^2 (ring evidence c ~ 13.5) plus a
  second-moment spectral bound; then **G2** vertex-bookkeeping completeness
  (O(w_4) sextic transfers, two-shell cross transfers, sigma-inhomogeneity
  channel).

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [STEP-5B/Closed-Region] Matching lemmas + derived n_max(I) region; B5 promoted T3->T4 — 2026-06-05

- **G1 attack landed** [B5-BEYOND-LAYER-BOUND v1.1]: Lemma C' (transfer
  matching — |w_t| <= 2 lam I, multiplicity <= 2n, exact ordered-pair l1
  identity sum|w_t| <= lam(4S^2-2I), equality on rings to 1e-12) and Lemma D
  (l2 mass <= 8n (lam I)^2) are rigorous and pattern-independent.
  **Closed-region theorem DERIVED**: STEP-5B holds for every admissible
  single-shell pattern with n <= n_max(I) = **62/31/16/6/3** at
  I = 1e-4/2e-4/4e-4/1e-3/2e-3 (a <= 0.75); the v1.0 calibrated boxes are
  superseded by derivation (12-mode box now a theorem, margin ratio >= 13).
- **Residual narrowed to G1'** (thin-spread, n > n_max(I)) **+ G2**: measured
  l2 mass is n-UNIFORM on adversarial rings (12.9–13.5 (lam I)^2 at
  n = 16/24/32 vs the 8n bound — 19x slack and growing) — recorded as the
  designated-attack signal: an n-free l2 theorem (c ~ 14) + a second-moment
  spectral bound would close G1'.
- **Verification loop caught an author error**: the v1.1.0 l1 assert with
  constant 2S^2 FAILED on every config; ring measurements matched the
  corrected identity exactly — fixed in script v1.1.1 (54/54 asserts) and
  recorded as DA exhibit alpha' in the note and card.
- **B5 promoted T3 -> T4** (claim-standard §5: DA >= 3 with verdicts +
  quantitative sanity in card and note). STEP-5B gate stays OPEN; no tier
  action on B1/B2. Note v1.1 re-issued (FORM-CHECK PASS, Overfull 0, PDF
  beside source; v1.0 superseded, kept).

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [STEP-5B/Reduction] Pattern-generic Gershgorin reduction registered at T3 — 2026-06-05

- **New claim B5-BEYOND-LAYER-BOUND (T3 proof sketch)** [serving gate STEP-5B;
  soft-supports B1-RH-ENUM, B2-PROPA-HLAYER]: two rigorous pattern-independent
  lemmas — (A) Gershgorin–Schur row bound ||X|| ≤ W_l1(P)·g(r̂) with the
  two-term envelope g, (B) second-order log-det envelope
  |δF_off| ≤ tr X²/(4V(1−a)) with the isotropic trace identity
  tr X²/V = Σ_t |w_t|² J(|t|) — reduce STEP-5B to the explicit bound
  |δF_off(P)| ≤ W_l1² J_max/(4(1−a)) plus exactly two named gaps:
  **G1** (class-wide weighted-ℓ¹ cap over the threat region) and
  **G2** (vertex bookkeeping completeness: sextic transfers, two-shell cross
  terms, σ-inhomogeneity channel).
- **Numerical certification at the anchor** (`codes/vacuum/
  beyond_layer_gershgorin_bound.py` v1.0.1, 20/20 asserts; artefact under
  `runs/B5-BEYOND-LAYER-BOUND/260605-gershgorin-reduction/`): Math434-audit
  calibration reproduced (row terms to ≤4e-6; ||X|| ≤ 3.1e-3); J(|t|) table
  with grid-refinement drift <6e-6 and analytic shell-estimate bracket;
  calibrated boxes n_res=12: margin ratio **18.2×** at I=4e-4, 2.2× at
  I=1e-3; LAM second order = margin/64,000.
- **Honest scope**: STEP-5B stays OPEN (gate annotated, no closure claimed);
  no tier action on B1/B2; calibrated boxes are stated regions, not derived
  caps — G1 is the genuine remaining mathematics.
- Note (FORM-CHECK PASS; Overfull 7→0 in-session via tabularx/url fixes; PDF
  beside source): `claims/B5-BEYOND-LAYER-BOUND/notes/
  beyond-layer-gershgorin-reduction-260605-v1.0.tex.txt`.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Migration-2] Enumerated-reading chain migrated; B1-RH-ENUM migration-clean (167/167) — 2026-06-05

- **Migration batch 2** (plan phase M1) [B1-RH-ENUM; supports H-LAYER of
  B2-PROPA-HLAYER]: 32 files — 14 notes (Math427 v1.0/v1.1, Math428 v1.0/v1.1,
  Math429 v1.0/v1.1, Math430, Math431 LAM/HEX/FCC, Math432 v1.0/v1.1,
  Math434 §15.5 audit + AddA T5-promotion record, Math436 HEX exact-Wick
  v1.0/v1.1), 8 verification scripts, 10 artefacts (incl. two checkpoint
  `state.json` provenance files) — MIGRATED-VERBATIM into the per-tag layout.
- **Re-validation: 167/167 asserts PASS** (5+21+19+11+15+25+22+49) by fresh
  re-execution, no legacy checkpoint state used; all 8 regenerated JSONs
  identical to archive within rel_tol 1e-9 — zero diffs, zero stale-artefact
  findings (contrast batch 1's F-1). Math434/436 checkpoint-resumable;
  completed in one budget window here. Fresh artefacts + summary under
  `runs/B1-RH-ENUM/260605-migration-revalidation/`.
- **B1-RH-ENUM is migration-clean**: `legacy:` pointer resolved; reproduction
  **AVAILABLE** (8-script chain with resume note); card/ledger/INDEX updated;
  ESTIMATOR-UPGRADE gate source resolved to archive. H-LAYER's two
  justification legs (Math427 infimum; enumerated refinements) now grounded
  in-archive.
- Batch record note (standard form, FORM-CHECK PASS, Overfull 0, PDF beside
  source): `claims/B1-RH-ENUM/notes/enumerated-readings-migration-revalidation-260605-v1.0.tex.txt`.
- No tier changes: B1 stays T5 CLOSED@ESTIMATOR-GRADE; STEP-5B remains the
  gateway. Sign-off: batch-2 rows PENDING (H-LAYER) per migration-plan §6.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Note-Form] Machine-enforced standard note form; PDFs live beside sources; build/ retired — 2026-06-05

- **Standard note form (binding, `naming-and-versioning.md` §3; authoring
  skeleton `verification/templates/note-skeleton.tex.txt`)**: banner fields
  `% Title:` (the PDF title is the proper human-readable title, never the
  filename), `% Claim:`, `% Version: vN.M -- first issued D1; this version
  issued D2` (rendered in the PDF date field as "first issued D1 · this
  version issued D2 · vN.M"), `% Status:`, cumulative revision history;
  mandatory sections Purpose-and-scope / content / Numerical-verification
  (when numbers) / Devil's-advocate / Result-footer-in-verbatim.
- **`build_note_pdf.py` v1.1.0 FORM-CHECK** enforces the form AND cross-checks
  banner version/dates against the two-date filename (mismatch refuses the
  build); compiles in a TEMPORARY directory; gates on zero Overfull-hbox;
  places the PDF **next to its source** (`claims/<ID>/notes/<stem>.pdf`;
  current version's PDF only — superseded PDFs removed, sources reproducible).
- **`build/` area retired repo-wide**: LaTeX intermediates never touch the
  repository; `build_wiki.py` v1.1.0 emits to a temp dir (`--out` override);
  `.gitignore` build/ entry removed; catalog v1.1.2 parses note-PDF filenames.
- Batch record re-issued v1.3 (standard-form banner; FORM-CHECK PASS;
  PDF title/date verified via text extraction) [A1-KERNEL-CONV,
  B2-PROPA-HLAYER]; v1.2 superseded, all versions kept.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Publication-Surfaces] Standard-LaTeX table rule; live-fetch website; wiki generator — 2026-06-05

- **Standard LaTeX + width-bounded tables (binding,
  `naming-and-versioning.md` §3)**: notes compile under the standard template
  alone (required/tools packages only; per-note preambles forbidden — extend
  the template); every table is `tabularx{\textwidth}` with wrapping `Y`
  columns; long paths use `\url{}`; acceptance = ZERO `Overfull \hbox`
  (`build_note_pdf.py` v1.0.2 prints the count and fails on nonzero).
  Proven [A1-KERNEL-CONV, B2-PROPA-HLAYER]: batch-1 record v1.1 built with 7
  overfull boxes → **v1.2 width-compliance re-issue builds with 0**
  (v1.1 superseded, kept).
- **Website rebuilt as LIVE-FETCH static shell** (`publish/website/`:
  index.html + app.js v1.0.1 + style.css; `publication-tiers.md` W1′/W2′):
  no content files exist — at view time the shell fetches `main` directly
  (catalog.json manifest → status.json cards, Markdown registries; marked +
  MathJax). Push = site current, by construction; owner/repo auto-detected
  from the Pages URL. Deployment workflow `.github/workflows/pages.yml`
  (Actions Pages) fully replaces the legacy website.
- **Wiki = the one generated snapshot channel**: `build_wiki.py` v1.0.1 emits
  8 pages to `build/wiki/` from the same sources, AUTO-GENERATED banners,
  hand-editing forbidden; publish command in the docstring.
- Defect caught in-session: `_TEMPLATE` counted as an 18th claim by the wiki
  generator (and would have been by the site) — fixed in build_wiki v1.0.1 /
  app.js v1.0.1. release_check v1.0.3 extends the English-only scan to
  .html/.js/.css.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Note-Format] Proof notes return to .tex.txt; PDF pipeline; SAME-REPO confirmed — 2026-06-05

- **Operator decisions**: (i) GitHub continuity = SAME-REPO option (legacy
  default branch → `legacy-archive`; this tree becomes the new `main`);
  (ii) the bootstrap `.md` choice for proof notes is REVISED — **working proof
  notes are `.tex.txt` LaTeX body fragments** (`naming-and-versioning.md` §3):
  full math fidelity (theorem envs, align, refs), uniformity with the ~440-note
  legacy corpus, and direct PDF builds. **Division of labour**: claim card
  (.md) = web-readable surface; note (.tex.txt) = formal document; synthesis
  documents stay .md until they transition to `publish/papers/`.
- **PDF pipeline shipped and proven**: `verification/templates/note-preamble.tex`
  + `verification/scripts/build_note_pdf.py` (v1.0.1) wrap a fragment and
  compile into git-ignored `build/` — the batch-1 record built to PDF (157 KB)
  in-session.
- **First versioned re-issue executed end-to-end** [A1-KERNEL-CONV,
  B2-PROPA-HLAYER]: batch-1 record re-issued as
  `proposition-a-migration-revalidation-260605-260605-v1.1.tex.txt` (two-date
  filename); v1.0 `.md` carries the SUPERSEDED forward pointer and is kept;
  catalog auto-detects the supersession (now 4 superseded versions tracked).
- Housekeeping: `build_catalog.py` v1.1.1 + `release_check.py` v1.0.2 skip the
  git-ignored `build/` area; ledger/card references updated; release gate PASS.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Release-Gate] Publication procedure decided + pre-push gate script — 2026-06-05

- **Decision** (`governance/publication-tiers.md` §GitHub release procedure):
  this repository IS the public repository — push = publish; **no curation
  script into the legacy public repo** (a one-direction mirror would re-create
  the legacy mirror-drift failure class). Continuity options sanctioned:
  SAME-REPO (legacy default branch renamed `legacy-archive`, this tree pushed
  as the new `main`; keeps URL/stars/issues) or NEW-REPO (fresh repo; legacy
  repo archived with a forward banner). Legacy public repo is never written
  again except the archival banner.
- **New gate** `verification/scripts/release_check.py` v1.0.1 (mandatory
  before every push; also a CI step): ledger+catalog sync, P0 fence (no file
  under `internal/` cited from public surfaces), English-only scan,
  no-overclaim phrase scan, P2-cites-migration-clean-claims rule, hygiene
  (NUL/JSON/AST/oversize). First run caught 3 genuine self-defects (stale
  catalog; over-broad fence; Hangul literal in own regex) — fixed in v1.0.1;
  gate now PASS.
- No tier changes; all generated surfaces in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Code-Versioning] Uniform date+version management extended to code and results — 2026-06-05

- **Operator directive**: everything — documents, code, scripts, results —
  carries date+version management. **Mechanism differs by artefact class**
  (`governance/naming-and-versioning.md` §5, binding):
  documents = filename two-date re-issue (citable immutable artefacts);
  **code = in-place evolution under git + mandatory version header**
  (`__version__`, `__first_issued__`, `__version_issued__`, optional
  `__claims__`, docstring changelog) — filename re-issue of code is FORBIDDEN
  (breaks imports/reproduction; side-by-side copies = the stale-physics drift
  class behind the legacy corrected-convention cascade);
  **results = immutable run folders** (new run = new
  `runs/<claim>/<YYMMDD>-<descriptive-tag>/`), artefacts record producing-code
  versions (+ git commit when available) — `verification-standard.md` §4.
- **Catalog upgraded** (`build_catalog.py` v1.1.0): parses python version
  headers and run-artefact dates, so code and results now show the same
  first-issue / version-issue / version columns as documents in `CATALOG.md`
  — uniform visibility without uniform mechanism. Harness scripts carry their
  headers (lint_claims v1.2.0, build_catalog v1.1.0).
- Archive scripts stay verbatim-immutable (no headers; dates in the ledger).
- No tier changes; linter PASS; catalog + ledger views in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Catalog] Derived artefact catalog — database capability without a database — 2026-06-05

- **Binding rule** (`governance/verification-standard.md` §8): the repository
  gets database-grade indexing as a DERIVED, disposable index only — the files,
  `claims/*/status.json`, and git history remain the sole sources of truth;
  authoritative stores beside them are forbidden (same single-source principle
  as `CLAIMS.md`/`BY-CLAIM.md`; kills the legacy mirror-drift class).
- **New generator** `verification/scripts/build_catalog.py` → `CATALOG.md`
  (human view, by artefact kind) + `verification/catalog.json` (machine twin):
  path, kind, claim links, theory tag, two-date fields, version, lifecycle
  (SUPERSEDED auto-detected from banners — currently 3), size, sha256/12.
  105 artefacts at first issue. CI `--check` step + smoke test added;
  `CATALOG.md` joins the root canonical set.
- No tier changes; linter PASS; all generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Naming] Human-readable filenames + first-issue-date convention — 2026-06-05

- **Binding naming rules added** (operator directive;
  `governance/naming-and-versioning.md` §3): (i) file/folder names and document
  headings lead with DESCRIPTIVE English slugs — internal codes (claim IDs,
  gate IDs, migration-phase labels) are never the sole identifying token
  outside the registry layer, and every code is expanded at first use in
  document bodies; (ii) two-date rule (refined same
  day by operator): first issue carries `-<YYMMDD-first>-v1.0`; every later
  version carries BOTH the first-issue date and its own issue date —
  `<slug>-<YYMMDD-first>-<YYMMDD-current>-vN.M.md` — so the filename shows the
  document's birth date and the currency of the version at a glance.
- **Renames applied**: batch-1 record note →
  `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-v1.0.md`;
  run folders → `runs/<claim>/260605-migration-revalidation/`; all references
  swept (ledger, index, cards, note body); older CHANGELOG entries left
  untouched as historical record.
- Future claim IDs use fully descriptive slugs (`claim-standard.md` §2);
  seeded IDs grandfathered. Run-folder tags must be descriptive words
  (`naming-and-versioning.md` §6). Synthesis-document pattern now
  `<descriptive-slug>-synthesis-<YYMMDD>-vN.M.md`.
- No tier changes; linter PASS; generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Layers] Three-layer architecture: claim packages, synthesis theory/, BY-CLAIM view — 2026-06-05

- **Layer model formalised** (operator design): L1 proof system (`claims/` +
  `archive/` + `codes/` + `runs/` + `verification/` + ledgers) → L2 theory
  synthesis (`theory/`, consolidated sector expositions citing only claim IDs
  at registered tiers) → L3 publication (`publish/`). Documented in
  `theory/README.md`; sector READMEs updated.
- **Working proof notes now live with their claim**:
  `claims/<ID>/notes/<claimID>-<slug>-vN.M.md` (claim folder = complete
  verification package: card + state + notes). The batch-1 record moved to
  `claims/B2-PROPA-HLAYER/notes/B2-PROPA-HLAYER-m1-revalidation-v1.0.md`;
  all references updated. Policies: `naming-and-versioning.md` §3/§8,
  `claim-standard.md` §1, `migration-plan.md` §2.
- **Per-claim archive view is GENERATED, not physical**: archive stays in the
  per-tag layout (one legacy file can serve several claims; scripts must stay
  co-located to remain runnable; archive keyed by immutable theory tags, not
  mutable claim structure). New generated reverse-lookup
  `archive/legacy/BY-CLAIM.md` (claim → migrated files + reproduction command
  + unresolved `legacy:` debt), emitted and sync-checked by
  `lint_claims.py --render [--check]`.
- Housekeeping: orphan `pytest-cache-files-*/` + `.pytest_cache/` (from the
  sandbox pytest cacheprovider crash) moved out of the tree and gitignored.
- No tier changes; linter PASS; generated files in sync.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [M1/Reorg] Archive per-tag layout + first TSv2 theory note — 2026-06-05

- **Archive reorganised** (operator request): `archive/legacy/` moved from the
  flat original-path mirror to the per-tag layout `notes/<TheoryTag>/` (all
  versions of a tag together, superseded banners intact), `scripts/` (flat,
  runnable as-is — sibling imports preserved; re-verified 10/10 post-move),
  `artefacts/<TheoryTag>/`. Original legacy paths remain recorded per file in
  `archive/MIGRATION-LEDGER.md`; new lookup table `archive/legacy/INDEX.md`;
  layout documented in `archive/README.md` and reflected in
  `governance/migration-plan.md` §1/§2 and `governance/naming-and-versioning.md` §8.
- **All evidence paths updated** [A1-KERNEL-CONV, B1-RH-ENUM, B2-PROPA-HLAYER]:
  status.json + claim.md + runs summaries + GATES.md source pointers now cite
  the per-tag paths; reproduction commands now `cd archive/legacy/scripts`.
- **First TSv2 theory note issued**:
  `theory/sector-B-vacuum/B2-PROPA-HLAYER-m1-revalidation-v1.0.md` — the
  permanent batch-1 record (re-validation table, STALE-ARTEFACT finding F-1,
  hypothesis transcription, devil's-advocate α/β/γ, §6 result footer),
  demonstrating the versioned-re-issue scheme (`-v<major>.<minor>.md`, full
  revision banner, all versions kept).
- No tier changes; linter PASS.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [M1/Migration] Sector-B evidence chain migrated + re-validated (277/277 asserts) — 2026-06-05

- **Batch 1 of pull-based migration** (`governance/migration-plan.md` §4 priority 1):
  23 legacy files (11 notes: Math426+AddA/AddB, Math435 v1.0–v1.1, Math437
  v1.0–v1.2, Math440, Math441, Math442; 7 scripts incl. 3 import dependencies;
  5 run JSONs) copied MIGRATED-VERBATIM to `archive/legacy/` at original paths.
- **Re-validation**: all four verification scripts re-run in a fresh
  environment — 10/10 (Math426), 101/101 (Math435), 91/91 (Math437),
  75/75 (Math440) self-test asserts PASS; regenerated JSONs identical to
  archived artefacts within rel_tol 1e-9. Artefacts:
  `runs/A1-KERNEL-CONV/260605-m1-reval/`, `runs/B2-PROPA-HLAYER/260605-m1-reval/`.
- **Finding (STALE-ARTEFACT)**: archived Math437 `step5_class_closure.json`
  predates the R1 repair (v1.0-era verdict string; numerics identical). Fresh
  artefact under `runs/` is canonical for TSv2 citation.
- **Claim updates** [A1-KERNEL-CONV, B1-RH-ENUM, B2-PROPA-HLAYER]: A1 and B2
  are migration-clean with reproduction **AVAILABLE** (two-script commands +
  expected outputs on the cards); B1 partially resolved (Math431-HEX chain
  still `legacy:` — next M1 batch). No tier changes.
- **H-LAYER / H-A0 transcribed verbatim** into `claims/GATES.md` from Math437
  v1.2 §Hypotheses (the H-LAYER beyond-layer residual is exactly STEP-5B).
- Migration ledger: 23 rows added; B2-feeding rows flagged
  **operator sign-off PENDING** per migration-plan §6.

Maintainer: Jusang Lee <jtkor@outlook.com>

---

## [Bootstrap] Repository structure, governance v2.0, seeded claim ledger — 2026-06-05

- Created the P0/P1/P2 three-tier repository layout (`internal/` local-only,
  repository = public verification surface, `publish/{website,papers}` curated).
- Issued `GOVERNANCE.md` v2.0 integrating the "TOE Proof Governance v1.0" and
  "Verification-First" drafts: Master Theorem + sectors A–F + GAP gates +
  TSv2 tier scale + evidence grades + claim-registration rule + no-overclaim +
  competition-closure + negative-result duty.
- Issued detailed policies under `governance/`: publication tiers, tier system
  (with legacy→TSv2 translation table), claim standard, verification standard,
  naming/versioning, migration plan.
- Seeded 17 claim cards (sectors A–F) translated conservatively from the legacy
  `TOE-FACT-SHEET.md` snapshot of 2026-06-05 (last theory tag Math442):
  Reading-H T5 estimator-grade; Prop-A T6 certified on {H-layer, H-A0};
  legacy-PROVED pillars enter as T6 with T7-candidate flags pending
  verification packages (no auto-T7 rule).
- Seeded `claims/GATES.md` (Step-5b gateway, G3'-b(iii), GAP-1..4 and named
  sub-gates), `predictions/prediction-ledger.md` (all OPEN/SCAFFOLD),
  `negative-results/registry.md` (six seeded entries incl. the Math245
  rollback and the eight failed classical-ħ routes).
- Built `verification/scripts/lint_claims.py` (schema + DAG acyclicity +
  tier-monotonicity/hypothesis rule + `--render` generator for `CLAIMS.md`);
  CI workflow at `.github/workflows/verify.yml`.
- `CLAIMS.md` is generated; hand-editing forbidden.

Maintainer: Jusang Lee <jtkor@outlook.com>
