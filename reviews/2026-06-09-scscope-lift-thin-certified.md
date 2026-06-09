# Operator decision -- SC-SCOPE lift @ THIN-CERTIFIED (2026-06-09)

**Context**: review of scscope-quartic-normalisation-certificate v1.0 (convention pinned by Parseval; R_max=0.385<0.634
certified; corrected additive joint x1.040-x1.082>1).

## Decision

ACCEPT the quartic certificate and LIFT SC-SCOPE with a THIN-CERTIFIED flag (this SUPERSEDES the earlier same-day HOLD).
B1 active hypothesis set {H-LAYER, SC-SCOPE} -> {H-LAYER}; tier UNCHANGED T6. Ledger flag: LIFTED@THIN-CERTIFIED, with a
sunset-limited near-critical margin.

## Why this differs from the retracted (2026-06-08) lift

The retracted lift used the LOCAL pairing formula paired=rho/2.872 globally. This certificate uses the CORRECTED additive
bookkeeping joint=MARGIN/(C2+C_sunset+C_quartic) and lowers C_quartic via the CERTIFIED quartic (Parseval-pinned
convention). The closure is genuine, not a formula artefact.

## Structural interpretation (operator)

The thin margin (x1.04 worst case) is not weak physics -- it is a near-critical structural selection boundary:
the joint saturates at x1.13 (sunset cap), and the certified endpoint sits at x1.04 just below it. Confirmed
(scscope_endpoint_sweep.py 4/4): sign-stable across I (endpoint thinnest; critical I~2.5e-3 beyond the certified
endpoint) and mu^2 [x0.5,x2] (worst x1.034). Points 1-4 of the operator's robustness list are met; the structural
explanation (point 5) is the sunset saturation.

## Honest ledger wording

SC-SCOPE: LIFTED@THIN-CERTIFIED, sunset-limited near-critical margin.
B1-RH-ENUM: T6 CONDITIONAL on {H-LAYER}. The all-orders selection is now certified at the endpoint (sunset rigorous +
certified quartic), thin but sign-stable; not estimate-grade.
