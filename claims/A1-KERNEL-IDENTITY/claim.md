# A1-KERNEL-IDENTITY — kernel complete-the-square identity (zero-momentum vs shell mass)

**Tier**: T6 PROVED (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-07-20 · *(operator-approved 2026-06-23)*

## Statement

For $Y>0$, $Z<0$: $K(q)=r+Z|q|^2+Y|q|^4 = m_{\rm sh}^2+Y(|q|^2-q_\star^2)^2$ with $q_\star^2=-Z/(2Y)$, $m_{\rm sh}^2=r-Z^2/(4Y)$, and $r=K(0)=m_{\rm sh}^2+Y q_\star^4$. The **zero-momentum mass** $r$ and the **shell mass** $m_{\rm sh}^2$ are distinct.

## Scope

Algebraic identity; $Y>0$, $Z<0$ (so $q_\star^2>0$). Naming: $\mu^2$ deprecated for A1 → $m_{\rm sh}^2$ (`mu2_shell`) for $K(q_\star)$, $r$ (`r_zero`) for $K(0)$.

## Dependencies and hypotheses
- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered): A1-KERNEL-CONV (definitional kernel form) · Open gates: none

## Evidence
Grades: ANALYTIC, EXECUTED. `claims/A1-KERNEL-IDENTITY/notes/a1-kernel-identity-260623-260720-v1.1.tex.txt`; `codes/foundations/a1_kernel_checks.py` v1.7.0 (14/14 overall; named identity residual $5.68\times10^{-14}$).

## Falsifier
A counterexample to the identity (none possible) or to $r=K(0)=m_{\rm sh}^2+Yq_\star^4$.

## Reproduction
Status: **AVAILABLE**. `python codes/foundations/a1_kernel_checks.py` → 14/14 PASS overall, including `kernel_identity_complete_square`.

## No-overclaim
Identity/naming only; positivity → A1-SCALAR-ANALYTIC-BRANCH; production consistency → A1-PRODUCTION-KERNEL-MANIFEST.

## History
- 2026-06-23 — Created in the A1 split (operator review): separates $r=K(0)$ from $m_{\rm sh}^2=K(q_\star)$ (both were called $\mu^2$).
- 2026-06-23 — Operator approved T6 PROVED; no sign-off remains pending.
- 2026-07-20 — Administrative v1.1 aligns the live card with that approval and the current 14/14 checker; theorem and tier unchanged.

## Next required action
Preserve the approved identity and naming firewall; downstream scalar positivity uses A1-SCALAR-ANALYTIC-BRANCH and production parameters use A1-PRODUCTION-KERNEL-MANIFEST.
