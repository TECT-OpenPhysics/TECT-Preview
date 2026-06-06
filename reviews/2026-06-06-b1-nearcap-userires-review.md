# Operator adversarial review — B1 / near-gap / U-series cluster (2026-06-06)

**Reviewer**: operator. **Scope**: 11 documents (robustness, near-gap, U-series, enumeration, consolidation). **Binding headline**: do NOT cite these documents in parallel — make the SUPERSESSION CHAIN explicit. Several are historical intermediates corrected by the triage and the common-mode resolution; they are NOT current proof/tooling sources. Canonical archive (CLAUDE.md §6.3.5).

## Reconciled official status (this review supersedes the H-A0-docs review on ROBUSTNESS-MU2)

- **Near-gap gate = RESOLVED** by common-mode cancellation (neargap-common-mode-resolution), NOT by U11's old x130 / 2.7e-5 estimate.
- **ROBUSTNESS-MU2 = CLOSED only on mu^2 in [x0.5, x2] AND at matched second-cumulant STEP-5B scope**, with the explicit qualifier "m(mu^2) bounded positive, not explicitly recomputed". (This dedicated robustness review is more specific than the earlier H-A0-docs "OPEN"; the gate is a SCOPED closure, not an unconditional one. The A=0-uniqueness component is robust wider, [x0.2, x10]; the gate range is the INTERSECTION [x0.5, x2].)
- **Reading-H T6 entry needs an updated theorem card**: H-A0 removed (demoted to verified dependency), ROBUSTNESS-MU2 closed on the stated neighbourhood, SC-SCOPE still OPEN for all-orders. Hypotheses: {H-LAYER, H-ADM-COH, SC-SCOPE}; verified dependencies: A1-KERNEL-CONV, m*>m_w, M_R>M_c.

## Supersession chains (the headline)

### Near-gap protection
U9 (t6-entry-composition-audit: identified the near-gap composition gap; Prop-A uniform floor vanishes as O(I)) -> U10 (neargap-protection-lemma: structural floor route, T3) -> U11 (neargap-residual-closure: residual numerical closure, 2.7e-5/x130 -- NUMERICALLY SUPERSEDED) -> useries-triage (corrected: remainder 1.65e-3, protection x2; M'=-J(0)/2 not -J(0); U7 ratio 1.13 not 1.34) -> neargap-common-mode-resolution (FINAL repair: the x2 was a common-mode mis-subtraction; floor protected unconditionally at the common dressing).
- Cite the near-gap closure ONLY via neargap-common-mode-resolution. neargap-residual-closure is a HISTORICAL attempted repair with invalidated numbers (R-U10-1). R-U10-2 split-alignment identity may be retained as algebraic support pending a line-by-line exhibit.

### Verification tooling
useries-verification-script v1.0 (U14 DRAFT, unexecuted; asserted -M'(r̂)=J(0), remainder<=3.3e-5, protection>100 -- all later shown wrong) -> useries-triage v0.2.0 (corrected, truth-asserting, 57/57). U14 v1.0 is OBSOLETE; use the corrected v0.2.0 script.
- "57/57 PASS" = the CORRECTED truth-asserting script passes, NOT that the original note claims were right.

### M'-usage factor-2 audit (operator-required grep)
The wrong identity M'(r̂)=-J(0) (true: -J(0)/2) appears in: neargap-residual-closure v1.0 (superseded), useries-verification-script v1.0 (superseded), sunset-endpoint-refinement v1.0 (live B5 draft -- its x1.34 endpoint estimate is affected and is marked correction-pending). The triage script t6_mainline_useries_checks.py is already corrected. No other live note carries it.

## Per-document required reinforcements (condensed)

1. robustness-mu2-step5b-remargin: keep "m(mu^2) bounded positive, not recomputed"; "monotone increasing" = sampled-sweep observation not interval theorem; J_eff 10% middle-quadrature difference -> verdict-insensitive only, no precision claim; closes second-cumulant STEP-5B scope only, NOT all-order.
2. robustness-mu2-offanchor: closes A=0-uniqueness robustness on [x0.2,x10] ALONE (not the gate); lambda' 1.5% variation is motivation not theorem; mu^2-cancellation identity gives margin positivity only; sweep may need interval arithmetic for a T6/T7 off-anchor theorem.
3. reading-h-t6-entry v2.0: hypothesis set outdated (drop H-A0); F[P]>F[R_H] strictness vs near-gap equality (use F[P]>=F[R_H], equality for the Reading-H representative / zero-equivalent config, then quotient); formalize the bulk/near-gap partition variable and matched normalization; SC-SCOPE = real physical assumption (matched second-cumulant only; all-order open); quantitative margins NOT in the theorem (sign theorem only).
4. neargap-common-mode-resolution: U11's numerical protection superseded; near-gap restored by common-mode; operator monotonicity needs a regularized trace/determinant-class statement for the continuum; machine n<=20 = sanity check not proof (carrier = PSD + operator monotonicity); Delta F -> 0+ is sign protection, NOT a finite uniform margin; depends on same-fixed-intensity comparison (fix the same-intensity slice then intensity minimization order).
5. useries-triage: actually LOWERS the numerical reliability of U7/U10/U11 (factor-2, 1.34->1.13, 2.7e-5->1.65e-3); cite later notes with corrected numbers only; R-U10-3 "blocked" is HISTORICAL (later resolved by common-mode); M'-grep required (done above).
6. enumeration-amended-class-recheck: decagonal endpoint margin 0.18% = BOUNDARY STRESS TEST not a robust member; "exact geometry" angle table is registered-not-executed (final release needs the script, esp. at 0.18%); two-shell inheritance is T3 (single-shell T4); criterion-band c_theta in [1,pi] ambiguity matters; in-class membership != energetic threat (decagonal = packing boundary, BCC/Prop-A = layer-energy).
7. t6-mainline-session-consolidation (U16): HISTORICAL pre-execution session map, NOT current status; "one machine check + sign-off away" broken by triage; shell-unverified volume is an attack point; T7-distance = roadmap not proof.
8. useries-verification-script v1.0 (U14): OBSOLETE draft (some asserts later shown wrong); unexecuted != verified; estimate-grade numbers should not be asserts (assert theorem-relevant inequalities like ratio>1, not ratio~1.34+-15%); single B1 artefact for B2/B5 checks = hygiene issue (split per claim).
9. neargap-residual-closure (U11): R-U10-1 numerical closure INVALIDATED (remainder 1.65e-3 not 2.7e-5; protection x2 not x130); (I/I_cal)^2 scaling over-optimistic; class-representativity leans on H-LAYER convention; R-U10-2 split-alignment retained as algebraic support pending exhibit; do NOT cite as latest near-gap closure.
10. neargap-protection-lemma (U10): core D+W=D_0+lambda'P^2>=D_0 strong but T3 (R-U10-1/2/3 residuals); "fluctuation never helps competitors" must be separated from the band-regime split delta F_off that DOES require STEP-5B; log monotonicity needs determinant-class; lambda'>0 load-bearing (anchor-band certified); P^2-representation dependency must stay visible ("within the chain's stated convention").
11. t6-entry-composition-audit (U9): showed the ORIGINAL U1 uniform-floor composition was defective (near-gap floor vanishes O(I)) -> U1 must be the CASE-SPLIT proof (bulk: Prop-A band + STEP-5B; near-gap: structural floor/common-mode); crossover arithmetic is estimate/alarm not proof; Prop A itself VALID, only the uniform-floor reading incomplete.

## Danger ranking (operator)

U11 numerical overclaim > U14 obsolete draft asserts > U1 outdated hypothesis set > near-gap trace-log regularization > ROBUSTNESS-MU2 exact m(mu^2) not recomputed > decagonal 0.18% boundary margin > two-shell inheritance T3.

## Actions taken (this commit)

- This review archived. Supersession markers added to neargap-residual-closure v1.0 and useries-verification-script v1.0 (HISTORICAL, corrected by triage + common-mode). sunset-endpoint-refinement v1.0 marked M'-correction-pending.
- ROBUSTNESS-MU2 reconciled to CLOSED on [x0.5,x2] at second-cumulant STEP-5B scope (scoped closure; m(mu^2) bounded-not-recomputed qualifier explicit); step5b note re-issued v1.2; removed from B1 open_gates.
- reading-h-t6-entry re-issued v2.1: hypothesis set {H-LAYER, H-ADM-COH, SC-SCOPE} + verified dependencies; equality-case + second-cumulant-only + sign-theorem-not-quantitative.
- The remaining per-document reinforcements are registered here and apply when each document is next advanced/graduated. No tier raised.
