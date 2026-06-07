# 2026-06-07 — ROBUSTNESS-MU2 close authorization + SC-SCOPE partial (operator review)

**Reviewer:** operator (Jusang Lee)
**Format:** evaluation summary → per-document adversarial review.
**Operational verdict (binding):** ROBUSTNESS-MU2 **may be CLOSED**;
SC-SCOPE **must stay OPEN**.

**Reviewed:** robustness-mu2-margin-recompute v1.1; scscope-mendpoint-evaluation v1.1.

## Evaluation summary
- **robustness-mu2-margin-recompute v1.1 — STRONG.** The bounded-anchor argument
  was replaced by an actual recomputation $m(\mu^2) = P_B(M_+(\mu^2)) -
  \mathrm{DIP}_{\rm BAND}(\mu^2)$; reproduces $m(0.005)=0.004320$; over
  $[\times0.5,\times2]$, $\min m = 0.004082$ at $\mu^2=0.0025$, i.e.
  $\ge 0.945\,m_{\rm anchor} \gg 0.4\,m_{\rm anchor}$; central-difference
  derivative positive; full $5\times3$ grid $J_{\rm eff}$ envelope $< 0.01\%$;
  worst STEP-5B ratio $\times2.41 > 1$. **ROBUSTNESS-MU2 may be passed to
  `CLOSED@[x0.5,x2]-2ND-CUMULANT` after operator authorization** (given here).
  Scope qualifier: second-cumulant order, three certified intensities,
  $[\times0.5,\times2]$ — NOT all-orders.
- **scscope-mendpoint-evaluation v1.1 — PARTIAL.** M-ENDPOINT and the SUNSET
  axis pass; SC-SCOPE is NOT closed. $M(0.33675)=0.104953$ direct quadrature
  (independent trapezoid $0.105589$, $0.61\%$; tail bound $8.4\times10^{-4}$) is
  a reliable EXECUTED constant. Sunset axis $\times0.970$ (frozen) $\to
  \times1.13$ (dressed) $\to \times1.28$ (per-$J$), envelope-worst
  $\times1.096 > 1$: positive at SIGN level. But $\times1.13$ is a sign, not a
  margin; the joint inequality can consume the $\sim13\%$, and SC-SCOPE stays
  OPEN on GHAT4-PERTRANSFER + R-U6-1.

## Adversarial review (key points)
- **ROBUSTNESS-MU2**: (1) derivative-positive certificate is grid-based, not a
  full analytic proof — but the structural DIP_BAND-decrease / $P_B(M_+)$-increase
  explanation + "grid evaluates, not searches" logic is adequate; not a fatal
  weakness. (2) Only three intensities closed — do NOT later write
  "intensity-robust"; the precise statement is "closed on $[\times0.5,\times2]$
  at second-cumulant order for the three certified intensities." (3) Not flipping
  the gate in the document was correct discipline.
- **SC-SCOPE / M-ENDPOINT**: (1) $\times1.13$ is thin (biggest weakness);
  (2) M-ENDPOINT is an executed $\sim1\%$ value, not a $0.1\%$ interval constant
  — in the final all-orders proof either promote it to an interval certificate
  or carry the envelope into the joint inequality; (3) only the SUNSET axis is
  resolved — closing SC-SCOPE on this basis would be overclaim.

## Operational verdict and actions (this turn)
- **ROBUSTNESS-MU2 → CLOSED@[x0.5,x2]-2ND-CUMULANT** (operator-authorized):
  GATES.md status flipped; removed from B1 open_gates; B1 scope/no-overclaim
  updated to "mu^2-robust on [x0.5,x2] at second-cumulant, not all-orders".
- **M-ENDPOINT → RESOLVED** (operator ledger): GATES.md status flipped; sunset
  axis positive at sign level recorded.
- **SC-SCOPE stays OPEN** (no flip) on GHAT4-PERTRANSFER + R-U6-1 + the joint
  second+third-order endpoint inequality.

## Honest ledger after this round
- ROBUSTNESS-MU2: CLOSED@[x0.5,x2]-2ND-CUMULANT (operator-authorized 2026-06-07).
- M-ENDPOINT: RESOLVED (direct quadrature, ~1% cross-check).
- SUNSET axis: positive at sign level (thin).
- SC-SCOPE: OPEN on GHAT4-PERTRANSFER and R-U6-1.

## Next critical path
GHAT4-PERTRANSFER → R-U6-1 → joint second+third-order endpoint inequality.
