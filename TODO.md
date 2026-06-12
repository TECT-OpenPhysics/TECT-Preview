# TODO -- TECT task ledger

Generated from `todo/todo.json` by `verification/scripts/todo.py` -- **never hand-edit**; run `todo.py render`.
Portable: copying the TECT folder carries this ledger; a fresh cowork session reads it in the session-entry prelude (CLAUDE.md §1).

Counts: In progress 0 · Next up 2 · Blocked 0 · Backlog 3 · Done (recent) 26

## Next up

- **T-006** De-hardcode codes/vacuum scripts (derive MARGIN/RHO from source) + add check_code_discipline.py to release_check  _(owner: unassigned; claim: B1-RH-ENUM)_
  - MARGIN de-hardcoded 2026-06-07 (codes/vacuum/sectorb_common.py single source; scscope+robustness import margin_of). REMAINING: RHO consolidation + automated check_code_discipline.py wired into release_check (no-hardcoding + self-test + JSON-artefact scan).
  - _updated 2026-06-07_
- **T-013** Author SYNTHESIS.tex.txt layer: per-sub-proof + claim-level synthesis (the parent 'jong-hap' proof) for B1/B2/B5, citing each sub-proof's notes at their tiers  _(claim: B5-BEYOND-LAYER-BOUND)_
  - Parent main-line synthesis DONE 2026-06-12 (theory/main-line-synthesis-260612-v1.0, capstone over the 5 PUBLISHED bundles). REMAINING: per-claim SYNTHESIS layers for B1/B2/B5 (one note per turn).
  - _updated 2026-06-12_

## Backlog

- **T-004** Prove R-U6-1: tadpole formal alignment (matched bookkeeping removes tadpole)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: R-U6-1)_
  - SC-SCOPE input. Written proof that normal-ordered matched bookkeeping removes the tadpole and competitors are at their own stationarity points.
  - _updated 2026-06-07_
- **T-030** Arbitrary-Q DR-2 (frontier): remove the admissibility cap from Lemma 1's backing; currently T6-conditional on Bourgain-Demeter decoupling. NOT load-bearing for the C_full main theorem (Lemma 2 caps T'<=10 in-class; main-line-synthesis Sec.4b).  _(claim: B5-BEYOND-LAYER-BOUND)_
  - _updated 2026-06-12_
- **T-031** Full STEP-5B closure decision layer: budget comparison machine-closed (x55.6/x8.8/x2.1-2.6); remaining = admissible-class exhaustiveness operator-decision items (H-ADM-COH adoption record) + backlog lemma R-U6-1 (T-004).  _(claim: B5-BEYOND-LAYER-BOUND)_
  - _updated 2026-06-12_

## Done (recent)

- **T-001** Flip ROBUSTNESS-MU2 -> CLOSED@[x0.5,x2]-2ND-CUMULANT (atomic GATES.md + card + CHANGELOG)  _(owner: operator; claim: B1-RH-ENUM; gate: ROBUSTNESS-MU2; blocked by: operator sign-off)_
  - Closure bar MET (robustness-mu2-margin-recompute v1.0, 11/11): exact m(mu^2) recomputed, min 0.945 m_anchor, STEP-5B ratio worst x2.41, J_eff envelope converged. Awaits operator authorization to flip.
  - _updated 2026-06-07_
- **T-002** Mark M-ENDPOINT gate RESOLVED (value computed)  _(owner: operator; claim: B5-BEYOND-LAYER-BOUND; gate: M-ENDPOINT; blocked by: operator sign-off)_
  - M(0.33675) = 0.10495 evaluated by direct quadrature (scscope-mendpoint-evaluation v1.0, 11/11); sunset axis positive x1.13. Awaits operator authorization to flip.
  - _updated 2026-06-07_
- **T-003** Evaluate GHAT4-PERTRANSFER: per-transfer quartic-difference form factor  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: GHAT4-PERTRANSFER)_
  - Critical-path SC-SCOPE input. At sup-kernel grade the quartic-difference endpoint is x1.0 (marginal); the per-transfer form factor is load-bearing. Same direct-quadrature strategy that resolved M-ENDPOINT should apply.
  - _updated 2026-06-07_
- **T-005** Assemble the joint second+third-order endpoint inequality (SC-SCOPE all-orders lift)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: SC-SCOPE; blocked by: T-003, T-004)_
  - SUPERSEDED by the 2026-06-07 SC-SCOPE scope decision: 2nd-cumulant accepted at the I=2e-3 endpoint; all-orders feasible for I<=1e-3. Joint inequality not pursued to closure (paired x0.905 exhausted). Reopen only via STEP-5B endpoint floor rho>~3.9.
  - _updated 2026-06-07_
- **T-007** ESTIMATOR-UPGRADE: controlled-error quantitative selection margins for B1  _(owner: unassigned; claim: B1-RH-ENUM; gate: ESTIMATOR-UPGRADE)_
  - Promote the estimator-grade selection margins to controlled-error bounds (separate from the T6 sign claim).
  - _updated 2026-06-07_
- **T-008** SC-SCOPE joint incompatible-pairing argument: bound max_t[c_sunset(t)+c_quartic(t)] (sunset peaks small-t, quartic large-t) to recover the x1.32 joint endpoint deficit  _(claim: B5-BEYOND-LAYER-BOUND; gate: SC-SCOPE)_
  - Next critical path after the 2026-06-07 joint honest-negative. Sunset bound largest at small transfers, quartic-difference Phi peaks at t=2q0; the joint per-transfer sum should be below the sum of individual maxima.
  - _updated 2026-06-07_
- **T-009** SC-SCOPE endpoint decision: sharpen STEP-5B endpoint floor to rho>~3.9 at I=2e-3 (B5) OR accept second-cumulant scope at the I=2e-3 endpoint  _(claim: B5-BEYOND-LAYER-BOUND; gate: SC-SCOPE)_
  - Per-transfer + joint-pairing exhausted (paired x0.905). Non-per-transfer routes only. Operator decision: sharper second-order endpoint floor vs accept 2nd-cumulant at the thinnest endpoint (all-orders feasible for I<=1e-3).
  - _updated 2026-06-07_
- **T-010** ESTIMATOR-UPGRADE finish: extend the curvature-certified controlled-error bound to the two-shell ensemble + dI/amplitude-grid quadrature knobs  _(claim: B1-RH-ENUM; gate: ESTIMATOR-UPGRADE)_
  - DONE: single-shell knobs (ii)/(iii)+continuum (estimator-upgrade-knobs v1.0); two-shell (0,0) PD + diagonal global continuum no-condensate at the B1 point r=0.219 (twoshell-continuum-bound v1.0); EXACT-Wick anchored no-condensate at r=0.219 -- min +6.7e-4>0, bracket O(A^4) near origin (twoshell-anchored-bracket v1.0, 7/7). REMAINING (refinement only): a curvature-chord continuum bound on the exact anchored BULK surface (finer exact scan). Then ESTIMATOR-UPGRADE closure is an operator decision.
  - _updated 2026-06-08_
- **T-011** Execute claims sub-proof reorg: move notes into sub-theorem folders + per-sub-proof/claim SYNTHESIS, per the confirmed taxonomy  _(claim: B5-BEYOND-LAYER-BOUND)_
  - claims-restructure-proposal-260609; tooling ready (build_index/lineage nesting-aware, os.replace moves work); BLOCKED on operator taxonomy confirmation (operator chose 'adjust taxonomy then execute')
  - _updated 2026-06-09_
- **T-012** Resolve B1/B5 SC-SCOPE chronicle duplicate via Windows-side Remove-Item  _(claim: B1-RH-ENUM)_
  - sandbox cannot unlink; B5 copy canonical; DEFERRED per operator (deletions later)
  - _updated 2026-06-09_
- **T-014** RES-5 endpoint full-lattice theorem (1/2): pin C_eps R^eps < 26.2 over the admissible R-range (R-026 constant sufficiency); upgrades the lattice-class endpoint from STRONG EVIDENCE to theorem  _(claim: B1-RH-ENUM; gate: RES-5-ENDPOINT)_
  - res5-dr2-kappa-bound-v1.2
  - _updated 2026-06-09_
- **T-015** RES-5 endpoint full-lattice theorem (2/2): weighted/non-uniform amplitude bridge (R-027) -- include non-uniform amplitude competitors in B1's lattice scope (uniform-only at present)  _(claim: B1-RH-ENUM; gate: RES-5-ENDPOINT)_
  - res5-dr2-kappa-bound-v1.2
  - _updated 2026-06-09_
- **T-016** H-LAYER core: Prop-A / RES-1 (diagonal-Gaussian infimum) -- the deepest remaining H-LAYER axis (RES-5 now EXACT for enumerated / strong-evidence lattice; this is the next mainline)  _(claim: B2-PROPA-HLAYER; gate: RES-1)_
  - res5-dr2-kappa-bound-v1.2
  - _updated 2026-06-09_
- **T-017** H-LAYER residual 1 (carrier-richness link): prove chi(P) <~ T'(Q) -- connect the pinned additive-energy floor E_+/T' to the actual STEP-5B physical floor (B5 operator-decision). Makes RES-5 endpoint + H-diag physical-floor theorems over the admissible lattice class.  _(claim: B1-RH-ENUM; gate: CHI-LINK)_
  - res5-arc-consolidation
  - _updated 2026-06-09_
- **T-018** H-LAYER residual 2 (off-diagonal operator norm): upgrade R_lead<1 (leading condensate-direction ratio) to the full worst-direction ||O_offdiag||_op<1 (complete Bogoliubov Hessian) for H-diag/RES-1.  _(claim: B2-PROPA-HLAYER; gate: OFFDIAG-OPNORM)_
  - hdiag-offdiag-floor-bound
  - _updated 2026-06-09_
- **T-019** T-019: off-diagonal exchange-scalar identification (no A-independent Fock exchange; reframe b_exch onto R_lead + SC-SCOPE two-loop)
  - _updated 2026-06-10_
- **T-020** T-020: class-wide second-cumulant off-diagonal stability (rho*R_lead<1; extends Math428 to all admissible)
  - _updated 2026-06-10_
- **T-021** T-021: SC-SCOPE third-cumulant endpoint class-wide (joint(rho_lat); T'<=13<60.4)
  - _updated 2026-06-10_
- **T-022** T-022: H-LAYER analytic-closure consolidation + competitor-class formalisation (milestone)
  - _updated 2026-06-10_
- **T-023** T-023: A_adm exclusion-boundary refinement (2/3 derived; sign-off -> crystalline-order assumption)
  - _updated 2026-06-10_
- **T-024** T-024: operator decision on off-shell competitors (A_adm primary shell-supported + A_ext adversarial fallback)
  - _updated 2026-06-10_
- **T-025** T-025: H-LAYER closure Final Consolidation (complete milestone T-016..T-024)
  - _updated 2026-06-10_
- **T-026** T-026: off-shell domination theorem (T7 Step 1; Blocker A removed)
  - _updated 2026-06-10_
- **T-027** T-027: Blocker B hardening (T7 Step 3; Parseval+R_max+anchoring theorem-grade)
  - _updated 2026-06-10_
- **T-028** T-028: T7 proposition assembly (Step 4; residual = operator sign-off)
  - _updated 2026-06-10_
- **T-029** T-029: paper-grade internal audit of the H-LAYER->T7 route (5 axes, 61/61, certified)
  - _updated 2026-06-10_
