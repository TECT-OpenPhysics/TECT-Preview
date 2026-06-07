# TODO -- TECT task ledger

Generated from `todo/todo.json` by `verification/scripts/todo.py` -- **never hand-edit**; run `todo.py render`.
Portable: copying the TECT folder carries this ledger; a fresh cowork session reads it in the session-entry prelude (CLAUDE.md §1).

Counts: In progress 0 · Next up 2 · Blocked 2 · Backlog 3 · Done (recent) 0

## Next up

- **T-003** Evaluate GHAT4-PERTRANSFER: per-transfer quartic-difference form factor  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: GHAT4-PERTRANSFER)_
  - Critical-path SC-SCOPE input. At sup-kernel grade the quartic-difference endpoint is x1.0 (marginal); the per-transfer form factor is load-bearing. Same direct-quadrature strategy that resolved M-ENDPOINT should apply.
  - _updated 2026-06-07_
- **T-006** De-hardcode codes/vacuum scripts (derive MARGIN/RHO from source) + add check_code_discipline.py to release_check  _(owner: unassigned; claim: B1-RH-ENUM)_
  - Per 2026-06-07 operator code-discipline policy (governance/CODE-DISCIPLINE.md): scscope_mendpoint_eval.py still pastes MARGIN=0.00432/RHO; import/derive them instead. Add an automated no-hardcoding + self-test + JSON-artefact check.
  - _updated 2026-06-07_

## Blocked

- **T-001** Flip ROBUSTNESS-MU2 -> CLOSED@[x0.5,x2]-2ND-CUMULANT (atomic GATES.md + card + CHANGELOG)  _(owner: operator; claim: B1-RH-ENUM; gate: ROBUSTNESS-MU2; blocked by: operator sign-off)_
  - Closure bar MET (robustness-mu2-margin-recompute v1.0, 11/11): exact m(mu^2) recomputed, min 0.945 m_anchor, STEP-5B ratio worst x2.41, J_eff envelope converged. Awaits operator authorization to flip.
  - _updated 2026-06-07_
- **T-002** Mark M-ENDPOINT gate RESOLVED (value computed)  _(owner: operator; claim: B5-BEYOND-LAYER-BOUND; gate: M-ENDPOINT; blocked by: operator sign-off)_
  - M(0.33675) = 0.10495 evaluated by direct quadrature (scscope-mendpoint-evaluation v1.0, 11/11); sunset axis positive x1.13. Awaits operator authorization to flip.
  - _updated 2026-06-07_

## Backlog

- **T-004** Prove R-U6-1: tadpole formal alignment (matched bookkeeping removes tadpole)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: R-U6-1)_
  - SC-SCOPE input. Written proof that normal-ordered matched bookkeeping removes the tadpole and competitors are at their own stationarity points.
  - _updated 2026-06-07_
- **T-005** Assemble the joint second+third-order endpoint inequality (SC-SCOPE all-orders lift)  _(owner: unassigned; claim: B5-BEYOND-LAYER-BOUND; gate: SC-SCOPE; blocked by: T-003, T-004)_
  - Closes SC-SCOPE once M-ENDPOINT (done), GHAT4-PERTRANSFER (T-003) and R-U6-1 (T-004) are in hand; re-assemble as one joint inequality.
  - _updated 2026-06-07_
- **T-007** ESTIMATOR-UPGRADE: controlled-error quantitative selection margins for B1  _(owner: unassigned; claim: B1-RH-ENUM; gate: ESTIMATOR-UPGRADE)_
  - Promote the estimator-grade selection margins to controlled-error bounds (separate from the T6 sign claim).
  - _updated 2026-06-07_
