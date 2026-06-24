# A1-SCALAR-ANALYTIC-BRANCH — K ≥ m_sh² > 0 (the precise A2/A3 hypothesis)

**Tier**: T6 PROVED CONDITIONAL (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(A1 split; submitted for sign-off; A2/A3 re-link here)*

## Statement

Assume $Y>0$, $Z<0$, $m_{\rm sh}^2>0$. Then $K(q)=m_{\rm sh}^2+Y(|q|^2-q_\star^2)^2\ge m_{\rm sh}^2>0$ for all $q$, and on a fixed periodic cell $\lambda_0(L)=\min_k K(k)\ge m_{\rm sh}^2>0$ (equality only if a lattice mode lies exactly on the shell). This is the precise positivity input of A2 (sectoriality) and A3 (IR finiteness).

## Scope

Stated in the **shell mass** $m_{\rm sh}^2$ (= old $\mu^2$ = $K(q_\star)$), **not** the zero-momentum $r=K(0)$ nor the solver's `mu2`$=r$. Production-config certification is A1-PRODUCTION-KERNEL-MANIFEST (separate).

## Dependencies and hypotheses
- Hard dependencies: A1-KERNEL-IDENTITY
- Hypotheses (registered): A1-SHELL-POSITIVITY (Y>0, Z<0, m_sh²>0) — SATISFIED@anchor
- Open gates: none

## Evidence
Grades: ANALYTIC, EXECUTED. `claims/A1-SCALAR-ANALYTIC-BRANCH/notes/a1-scalar-analytic-branch-260623-260623-v1.0.tex.txt`; `codes/foundations/a1_kernel_checks.py` (4/4).

## Falsifier
A kernel with $Y>0,Z<0,m_{\rm sh}^2>0$ yet $\inf_q K<m_{\rm sh}^2$ or $\lambda_0(L)<m_{\rm sh}^2$.

## Reproduction
Status: **AVAILABLE**. `python codes/foundations/a1_kernel_checks.py` → 4/4 PASS.

## No-overclaim
$m_{\rm sh}^2>0$ (shell), not the solver `mu2`$=r$; no production-config certification; positivity only.

## History
- 2026-06-23 — Created in the A1 split: the precise positivity hypothesis A2/A3 rely on, in the shell mass.

## Next required action
Operator sign-off; A2 and A3 depend on this card.
