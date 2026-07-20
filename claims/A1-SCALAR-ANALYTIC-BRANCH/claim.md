# A1-SCALAR-ANALYTIC-BRANCH — K ≥ m_sh² > 0 (the precise A2/A3 hypothesis)

**Tier**: T6 PROVED CONDITIONAL (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-07-20 · *(operator-approved 2026-06-23)*

## Statement

Assume $Y>0$, $Z<0$, $m_{\rm sh}^2>0$. Then $K(q)=m_{\rm sh}^2+Y(|q|^2-q_\star^2)^2\ge m_{\rm sh}^2>0$ for all $q$, and on a fixed periodic cell $\lambda_0(L)=\min_k K(k)\ge m_{\rm sh}^2>0$ (equality only if a lattice mode lies exactly on the shell). This is the precise positivity input of the scalar A2/A3/A4 branch. The separate full-production A2/A3 branch uses its own hash-pinned functional and shell-mass anchor.

## Scope

Stated in the **shell mass** $m_{\rm sh}^2$ (= legacy $\mu^2$ = $K(q_\star)$), **not** the zero-momentum $r=K(0)$. In the canonical N-001 scalar manifest, `mu2_shell` is the shell mass and `kinetic_coefficients(mu2_shell,Y,q0)` reconstructs `r_zero=mu2_shell+Y*q0^4`; the alias `mu2=r` is forbidden. Only the failed legacy template carried that conflation. Production-config certification is A1-PRODUCTION-KERNEL-MANIFEST (separate).

## Dependencies and hypotheses
- Hard dependencies: A1-KERNEL-IDENTITY
- Hypotheses (registered): A1-SHELL-POSITIVITY (Y>0, Z<0, m_sh²>0) — SATISFIED@anchor
- Open gates: none

## Evidence
Grades: ANALYTIC, EXECUTED. `claims/A1-SCALAR-ANALYTIC-BRANCH/notes/a1-scalar-analytic-branch-260623-260720-v1.1.tex.txt`; `codes/foundations/a1_kernel_checks.py` v1.7.0 (14/14 overall; both named positivity assertions PASS).

## Falsifier
A kernel with $Y>0,Z<0,m_{\rm sh}^2>0$ yet $\inf_q K<m_{\rm sh}^2$ or $\lambda_0(L)<m_{\rm sh}^2$.

## Reproduction
Status: **AVAILABLE**. `python codes/foundations/a1_kernel_checks.py` → 14/14 PASS overall, including `analytic_branch_D_ge_mu2shell_positive` and `lambda0_ge_mu2shell_equality_onshell_only`.

## No-overclaim
$m_{\rm sh}^2>0$ is the shell condition; `mu2_shell` is not `r_zero`. This card proves scalar-kernel positivity only and does not certify a production config, full functional, dynamics, or measure.

## History
- 2026-06-23 — Created in the A1 split: the precise positivity hypothesis A2/A3 rely on, in the shell mass.
- 2026-06-23 — Operator approved T6 PROVED CONDITIONAL; no sign-off remains pending.
- 2026-07-20 — Administrative v1.1 corrects the current N-001 `mu2_shell`/`r_zero` description and aligns the card with the current 14/14 checker; theorem and tier unchanged.

## Next required action
Preserve as the scalar A2/A3/A4 positivity input. Any parameter-identical bridge to the full-production branch remains a separate claim.
