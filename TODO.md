# TODO -- TECT task ledger

Generated from `todo/todo.json` by `verification/scripts/todo.py` -- **never hand-edit**; run `todo.py render`.
Portable: copying the TECT folder carries this ledger; a fresh cowork session reads it in the session-entry prelude (CLAUDE.md §1).

Counts: In progress 0 · Next up 1 · Blocked 0 · Backlog 3 · Done (recent) 41

## Next up

- **T-006** De-hardcode codes/vacuum scripts (derive MARGIN/RHO from source) + add check_code_discipline.py to release_check  _(owner: unassigned; claim: B1-RH-ENUM)_
  - MARGIN de-hardcoded 2026-06-07 (codes/vacuum/sectorb_common.py single source; scscope+robustness import margin_of). REMAINING: RHO consolidation + automated check_code_discipline.py wired into release_check (no-hardcoding + self-test + JSON-artefact scan).
  - _updated 2026-06-07_

## Backlog

- **T-030** Arbitrary-Q DR-2 (frontier): remove the admissibility cap from Lemma 1's backing; currently T6-conditional on Bourgain-Demeter decoupling. NOT load-bearing for the C_full main theorem (Lemma 2 caps T'<=10 in-class; main-line-synthesis Sec.4b).  _(claim: B5-BEYOND-LAYER-BOUND)_
  - OPEN FRONTIER (arbitrary-Q DR-2). D2-A 2026-06-12: DR2-SHARE gate formally rescoped here as NON-LOAD-BEARING for the published C_full head (Lemma 2 caps T'<=10 in-class). Content: BD-conditional T6 (separated Q); PSM conjecture T2; elementary route open.
  - _updated 2026-06-12_
- **T-045** A6: decide full-field bare concentration with partition-function tube bounds and tightness  _(owner: unassigned; claim: A6-CLASSII-K-COMPOSITE-DEFINITION; gate: A6-CLASSII-FULL-FIELD-BARE-CONCENTRATION)_
  - _updated 2026-07-20_
- **T-046** A7: prove the frozen-energy relative commutator bound, then construct the fixed-volume Gibbs limit  _(owner: Codex; claim: A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE; gate: A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND)_
  - The former commutator-alone all-eta target is falsified by the 2026-07-21 same-shell resonant covariance-contracted Gaussian tilt with a Cameron-Martin mean (A9 no-go addendum: primary 24/24, independent 17/17, integrated 56/56). A9 scoped T5 remains valid. Next determine the all-ray critical retained fraction and its budget tradeoff, exclude zero-frozen/negative-commutator directions, and prove a trace-safe conditional log-Laplace bound for theta Q_fr+C with explicit production entropy, quartic, and sextic budgets. Keep rho-floor removal and infinite volume separate.
  - _updated 2026-07-21_

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
- **T-004** Prove R-U6-1: tadpole formal alignment (matched bookkeeping removes tadpole)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: R-U6-1)_
  - PROOF WRITTEN 2026-06-12 (tadpole-reabsorption-lemma v1.1: Hermite normal-ordering alignment + self-caught 15vM^2 mechanism correction; ru61_tadpole_alignment.py 8/8 PASS). R-U6-1/R-U6-2 residuals discharged PENDING OPERATOR REVIEW; gate flip is the operator's.
  - _updated 2026-06-12_
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
- **T-013** Author SYNTHESIS.tex.txt layer: per-sub-proof + claim-level synthesis (the parent 'jong-hap' proof) for B1/B2/B5, citing each sub-proof's notes at their tiers  _(claim: B5-BEYOND-LAYER-BOUND)_
  - COMPLETE 2026-06-12: parent capstone PUBLISHED as Main-Line-Synthesis-T013-260612 + three claim-level SYNTHESIS notes issued (claims/<ID>/SYNTHESIS-260612-v1.0).
  - _updated 2026-06-12_
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
- **T-031** Full STEP-5B closure decision layer: budget comparison machine-closed (x55.6/x8.8/x2.1-2.6); remaining = admissible-class exhaustiveness operator-decision items (H-ADM-COH adoption record) + backlog lemma R-U6-1 (T-004).  _(claim: B5-BEYOND-LAYER-BOUND)_
  - CLOSED AS DECISION LAYER 2026-06-12: operator verdicts D1-A (lattice H-ADM-COH discharge re-affirmed, residual (a) pinned), D2-A (DR2-SHARE -> T-030 non-load-bearing), D3-A (B5 -> T6 PROVED-CONDITIONAL on H_B5^T6, label B5-BeyondLayer-T6Conditional-260612). Atomic flip set enacted.
  - _updated 2026-06-12_
- **T-033** N-001: evaluate projected Hessian/Rayleigh curvature of the homogeneous branch on the commensurate q0/BCC-star subspace  _(owner: unassigned)_
  - N32 full-star COMPLETE 2026-07-16: all six commensurate BCC {110} antipodal pairs around the uploaded homogeneous branch have positive projected Hessian curvature. Minimum curvature +52.12042392718455; no negative/near-zero directions. Evidence: reviews/2026-07-16-n001-bcc-star-curvature-n32-fullstar.json. This is the current operator-level stop signal for this parameter point; N64/N128 projected star checks are optional grid-transfer follow-up, and no tier or claim action is authorized.
  - _updated 2026-07-16_
- **T-034** Audit the full Class-II Euler-Lagrange map H2 to L2  _(owner: unassigned; claim: A2-FULL-PRODUCTION-WELLPOSED; gate: A2-FULL-NONLINEAR-MAPPING-AUDIT)_
  - First P2 analytic gate after the 2026-07-17 coercivity baseline: expand the six-real-component operator term by term and independently verify local Lipschitz continuity without derivative loss.
  - _updated 2026-07-17_
- **T-035** Audit full Class-II Galerkin energy identity and global continuation  _(claim: A2-FULL-PRODUCTION-WELLPOSED; gate: A2-FULL-ENERGY-CONTINUATION-AUDIT)_
  - Next P2 gate after the closed nonlinear H2-to-L2 audit: verify the finite-dimensional chain rule, compactness passage, and coercive continuation argument for the canonical eta_shell=0 functional.
  - _updated 2026-07-17_
- **T-036** Audit full Class-II continuous dependence and positive-time smoothing  _(claim: A2-FULL-PRODUCTION-WELLPOSED; gate: A2-FULL-SMOOTHING-AUDIT)_
  - Final P2 analytic gate: establish finite-interval continuous H2 dependence, the first t>0 H4 gain, and the higher-order bootstrap for the canonical eta_shell=0 flow.
  - _updated 2026-07-17_
- **T-037** P3: close full-production spectral discretization-to-continuum package  _(claim: A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM; gate: A3-FULL-DISCRETIZATION-CLOSURE)_
  - Closed at T6 CONDITIONAL-THEOREM after adversarial repair. The v2.1 Galerkin-ball underbound is registered as AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND. Corrected primary 21/21, non-importing full-chain 24/24, and integrated 124/124 audits pass. Replacement PUBLISHED bundle has 42 files and nine entry scripts ALL PASS, source-pinned to d4c7b3149fe56293ab2c88464c931d64c2e614e3 with digest 6d15d165a73d3a2af07e10fce07394ce8b83311e571ba2aae2fbbc61c31d2e41. Practical sharpness and historical-solver certification remain separate work.
  - _updated 2026-07-17_
- **T-038** P4: close finite-volume real-scalar spectral constructive Gibbs measure  _(claim: A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE; gate: A4-CONSTRUCTIVE-MEASURE-CLOSURE)_
  - Trace class, L6 interaction, partition bounds, full-sequence limit, dual audit, and proof PDF.
  - _updated 2026-07-18_
- **T-039** P4: enact scoped T6 after independent operator reproduction  _(claim: A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE; gate: A4-CONSTRUCTIVE-MEASURE-CLOSURE)_
  - Bind Jusang operator evidence, issue T6 enactment addendum, and preserve scalar-only exclusions.
  - _updated 2026-07-18_
- **T-040** Publish the A4 T6 support bundle, then build the confirmed A5 scoped T5 capstone bundle  _(claim: A5-SECTOR-A-SYNTHESIS)_
  - COMPLETE 2026-07-19: corrected A4 v2.1 support is PUBLISHED; A5 schema 1.2 attests all six support bundles; exact v1.2 is operator-confirmed by batch authorization and passes FORM-CHECK, zero overfull, six-page visual QA, and direct 32/32. Initial packaging omitted the paired original-path A4 PDF; the note-PDF gate caught it and AUDIT-2026-07-19-A5-BUNDLE-NOTE-PDF-COMPLETENESS records the rebuild. Final PUBLISHED bundle A5-Sector-A-Synthesis-T5-260719 passes standalone 32/32, all 155 file hashes, all 190 current-note PDF pairs, and digest 5cf4397c38fb316ec108447404531e649e628d6fcc62d67e613d060b70b24ea5. Next is T-041, the separate branch-aware T6 conditional-composition package.
  - _updated 2026-07-19_
- **T-041** A5: prepare branch-aware T6 conditional-composition theorem package  _(owner: Jusang Lee; claim: A5-SECTOR-A-SYNTHESIS; gate: A5-T6-CONDITIONAL-COMPOSITION-OPERATOR-CONFIRMATION)_
  - COMPLETE 2026-07-20: Jusang Lee confirmed the exact A5 T6 v1.0 source/PDF and authorized PUBLISHED bundle creation. Manifest schema 1.1 binds candidate commit fb776bff6b161178a6328570af3ef9529b44a2df and reviewed hashes. The v1.1 enactment issue passes FORM-CHECK, zero overfull, and five-page visual QA. Direct and bundle-root verification pass primary 22/22 plus independent 13/13 equals 35/35. PUBLISHED bundle A5-Sector-A-Conditional-Composition-T6-260720 contains 307 hashed files and digest 7779f98a945cf1b393023ab7d41cd30af6e68572797ab698368265a392f4a526. Immutable T5 capstone remains unchanged. Full derivative Class-II constructive measure, parameter identity, regulariser removal, t0/historical rates, Route B, infinite volume/phase transition, BCC/Sector-B, physical closure, and T7 remain excluded.
  - _updated 2026-07-19_
- **T-042** A6: full Class-II UV power counting and renormalisation decision  _(owner: Codex; claim: A6-CLASSII-UV-POWER-COUNTING; gate: A6-CLASSII-COUNTERTERM-CLOSURE)_
  - Derive the production Gaussian cutoff asymptotics, independently verify J/K current growth, and register the necessary leading counterterm without claiming a constructive measure.
  - _updated 2026-07-20_
- **T-043** A6: close the fixed-floor canonical K composite and split counterterm versus bare concentration  _(owner: Codex; claim: A6-CLASSII-K-COMPOSITE-DEFINITION; gate: A6-CLASSII-K-COMPOSITE-DEFINITION)_
  - _updated 2026-07-20_
- **T-044** A6/A7: define the exact counterterm and close renormalised J*K and K^2 composites  _(owner: Codex; claim: A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE; gate: A6-CLASSII-COUNTERTERM-CLOSURE)_
  - Composite and divergent-subgraph subgate closed at scoped T5; interacting stability, density convergence, and tightness move to the A7 Nelson gate.
  - _updated 2026-07-20_
