# Operator decision -- SC-SCOPE lift authorization (2026-06-08)

**Context**: review of scscope-floor-sharpening v1.0 (R-029, candidate). Operator accepted the route and
directed the single next step: reconcile the constant map K(n) <-> 1+T' inside the STEP-5B floor formula,
with conditional authorization: "if this reconciliation passes, then you may lift the SC-SCOPE endpoint to
all-orders."

## Reconciliation result (PASSED)

In the STEP-5B convention w_t = lambda' sum_{u+v=t} A_u A_v and
sum_{t!=0} w_t^2 = lambda'^2 (<F^4> - 4 I^2), the floor's additive-energy constant is exactly
K = sum_{t!=0} w_t^2 / (lambda' I)^2. The weighted Lemma A (R-027) t!=0 part gives
sum_{t!=0} |w_t|^2 <= T'(M) I^2, hence K <= T'(M) -- the sum-circle richness, NOT the kappa-balanced
8 + c_R sqrt(n). Verified (scscope_constant_map.py 3/3): K_floor/T' <= 0.52, w_0 = I (so the -4I^2 is
conservative). With K <= T' <= n_pack = 40.7 (separated) or T' ~ tens (lattice): rho_lat >= 6.55 >= 3.9,
paired >= 2.28 > 1 -- the all-orders endpoint floor obstruction is PROVED removed.

## Enactment

- SC-SCOPE LIFTED: B1 active hypothesis set {H-LAYER, SC-SCOPE} -> {H-LAYER}; B1 tier UNCHANGED T6.
- scscope-floor-sharpening re-issued v1.0 -> v1.1 (reconciliation proved; v1.0 superseded).
- GATES SC-SCOPE -> LIFTED; RESULTS-LEDGER R-029 updated.

## Honest caveat (recorded)

The all-orders selection's THIRD cumulant rests on the estimate-grade inflation (1+max[R_s+R_q]=2.872;
R_s, R_q cited estimates) -- the operator-accepted basis (scscope-scope-decision v1.0 'estimate-feasible
for I<=1e-3'), now extended uniformly to the endpoint by the PROVED floor sharpening. The SECOND-order
floor and the selection SIGN are rigorous; the third cumulant is estimate-grade. B1's all-orders scope
carries this caveat. Optional follow-up: promote R_s,R_q from estimate-grade to proved.
