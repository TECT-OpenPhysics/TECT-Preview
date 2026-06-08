# TODO -- TECT task ledger

Generated from `todo/todo.json` by `verification/scripts/todo.py` -- **never hand-edit**; run `todo.py render`.
Portable: copying the TECT folder carries this ledger; a fresh cowork session reads it in the session-entry prelude (CLAUDE.md §1).

Counts: In progress 0 · Next up 1 · Blocked 0 · Backlog 2 · Done (recent) 7

## Next up

- **T-006** De-hardcode codes/vacuum scripts (derive MARGIN/RHO from source) + add check_code_discipline.py to release_check  _(owner: unassigned; claim: B1-RH-ENUM)_
  - MARGIN de-hardcoded 2026-06-07 (codes/vacuum/sectorb_common.py single source; scscope+robustness import margin_of). REMAINING: RHO consolidation + automated check_code_discipline.py wired into release_check (no-hardcoding + self-test + JSON-artefact scan).
  - _updated 2026-06-07_

## Backlog

- **T-004** Prove R-U6-1: tadpole formal alignment (matched bookkeeping removes tadpole)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: R-U6-1)_
  - SC-SCOPE input. Written proof that normal-ordered matched bookkeeping removes the tadpole and competitors are at their own stationarity points.
  - _updated 2026-06-07_
- **T-010** ESTIMATOR-UPGRADE finish: extend the curvature-certified controlled-error bound to the two-shell ensemble + dI/amplitude-grid quadrature knobs  _(claim: B1-RH-ENUM; gate: ESTIMATOR-UPGRADE)_
  - Single-shell + M-quadrature done (estimator-upgrade-enumerated v1.0). REMAINING for full closure: (i) two-shell ensemble (same kappa=dF''(0)>0 + no-condensate method); (ii) dI quadrature + amplitude-grid envelopes; (iii) [operator review 2026-06-07, publication-grade] a no-condensate interval/Lipschitz bound dF_R(A)>=0 on each amplitude interval [A_j,A_{j+1}], replacing the grid-scan no-condensate evidence with a continuum guarantee. Then ESTIMATOR-UPGRADE closure is an operator decision.
  - _updated 2026-06-08_

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
