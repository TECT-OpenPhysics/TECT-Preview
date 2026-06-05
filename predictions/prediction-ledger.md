# Prediction Ledger

No prediction is official unless its **input set is frozen before comparison**.
A freeze fixes: input parameters, calibration data, forbidden fitting knobs,
acceptable error band — recorded in `predictions/freezes/<PRED-ID>-freeze.md`
and stamped with a git tag (`freeze/<PRED-ID>/v<N>`) **before** the comparison
data is examined. Until then, every entry below is OPEN or SCAFFOLD and counts
for nothing.

Constants firewall labels (`governance/tier-system.md` §5) apply to every
number: DERIVED / MATCHED / INSERTED / PREDICTED.

| Prediction ID | Quantity | Allowed inputs (to be frozen) | Output | Status | Claim link |
|---|---|---|---|---|---|
| PRED-G | $G$ | $c,\ \hbar,\ a_{\rm BCC}$ (with $a_{\rm BCC}$ derived without $G_{\rm obs}$) | $G_{\rm pred}$ | OPEN | C5-NEWTON-G |
| PRED-NU | $m_\nu$ | TECT neutrino sector | $m_1,m_2,m_3$ | OPEN | — |
| PRED-CKM | CKM angles | flavor PDE coefficients | $\theta_{12},\theta_{23},\theta_{13},\delta$ | SCAFFOLD | — |
| PRED-DM | dark-matter relic | defect density + KZ scale | $\Omega_{\rm DM}$ | OPEN | F1-COSMO-DARK-SECTOR |
| PRED-GW | phase-transition relic | transition scale | GW spectrum | OPEN | F1-COSMO-DARK-SECTOR |

## Status vocabulary

OPEN (no scaffold) → SCAFFOLD (computation path exists) → FROZEN (input set
registered + tagged) → COMPARED (PASS/FAIL recorded; FAIL also goes to
`negative-results/`). Skipping FROZEN invalidates the entry permanently —
a post-hoc comparison can never be promoted to PREDICTED.

## History

- 2026-06-05 — Ledger seeded; all entries OPEN/SCAFFOLD; no freeze registered.
