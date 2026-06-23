# B3-RH-TESTED-STRUCTURE-RANKING — Reading-H is selected within the tested ordered-reading ensemble (estimator grade)

**Tier**: T4 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(dependent projection of B1-RH-ENUM; created 2026-06-23 by operator verdict)*

## Statement

$\Delta F_{\rm enum}[\mathcal R]:=F_{\rm TECT}[\mathcal R]-F_{\rm TECT}[\mathcal R_H]>0$ for every $\mathcal R$ in the **tested** ordered-reading ensemble $\mathcal E_{\rm tested}$ (LAM/HEX/FCC explicit via Math431), at **estimator grade** — i.e. Reading-H is the lowest-energy reading *within the tested ensemble*. A dependent projection of B1-RH-ENUM.

## Scope (strict)

Relative ranking within the tested ordered-reading ensemble **only**. "Continuum-anchored" here means the estimator is built on the continuum functional/convention — **not** that an $a\to0$ PDE continuum limit has been certified (it has not). The result does **not** imply $F[\mathcal R_H]<F[0]$, nor $H_{\mathcal R_H}\succeq0$ under unrestricted variations, nor BCC phase existence/stability/global selection. Estimator error bound: uncontrolled (ESTIMATOR-UPGRADE / GAP-2).

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, B1-RH-ENUM
- Soft dependencies: B1-RH-ENUM (this card is its projection)
- Hypotheses: none · Open gates: ESTIMATOR-UPGRADE

## Evidence

Grades: EXECUTED, ESTIMATOR. Surviving B1 chain (migration-clean):

- `archive/legacy/notes/Math431/...LAM-HEX-FCC-PASS...` — LAM/HEX/FCC races
- `archive/legacy/notes/Math436/...HEX-Exact-Wick-Bracket...`
- `archive/legacy/notes/Math432/...Two-Shell-Ensemble-Race...`
- `archive/legacy/notes/Math434/...ReadingH-Selection...`

## Falsifier

A tested-ensemble reading $\mathcal R\in\mathcal E_{\rm tested}$ with $F_{\rm TECT}[\mathcal R]<F_{\rm TECT}[\mathcal R_H]$ at estimator grade (a ranking inversion). NOTE: a falsifier of the **ranking only**, not of any BCC phase/minimum/global-selection claim.

## Reproduction

Status: **AVAILABLE**. `cd archive/legacy/scripts && python Math431_g1pp3_lam_hex_fcc.py` (estimator grade).

## No-overclaim

BCC phase/minimum existence, stability, or **global** selection; $F[\mathcal R_H]<F[0]$; a symmetry-projected PSD Hessian under unrestricted variations; any completed $a\to0$ PDE continuum limit; independence from B1-RH-ENUM.

## History

- 2026-06-23 — Created by operator verdict as the only surviving projection of the retired B3-BCC-STRUCT (`R-2026-06-23-b3-bcc-structural-selection`). Strictly a B1 projection; no independent evidence.

## Next required action

Tighten the estimator error bound (ESTIMATOR-UPGRADE). A physical BCC structural claim must be re-established as a separate new card by certifying $F[\Psi_{\min}]<F[0]$, $\lambda_{\min}^\perp\ge0$ (symmetry-projected), $N\to\infty$ on the canonical PDE background.
