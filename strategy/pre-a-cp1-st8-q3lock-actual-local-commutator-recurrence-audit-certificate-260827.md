# EXP-001155 — actual finite-Q3 recurrence audit

## Question

Can the one-layer recurrence registered in EXP-001151 be applied directly to
the exact unsplit finite Q3 Hamiltonian flow on the four-context (q/p) Gibbs
commutator seminorm?

## Computation

The audit uses the canonical quartic Q3 Hamiltonian on volumes 2, 4 and 6,
oscillator dimension 3, (eta=1), character amplitude (1/3), six steps of
(delta=1/18), both time signs, and both (A,A^*) contexts.  For each site,

\[
L_x(t)^2=\|[q_x,A_t]\|_{\beta,#}^2+\|[p_x,A_t]\|_{\beta,#}^2,
\quad
\|X\|_{\beta,#}^2=\operatorname{Tr}(\rho X^*X)+\operatorname{Tr}(\rho XX^*).
\]

The tested recurrence is

\[
L_x(n+1)\le (1+C\delta)L_x(n)+J\delta\sum_{y\sim x}L_y(n),
\qquad C=J=1.
\]

## Result

The primary lane passes 98/98 finite-audit assertions, the independent lane
passes 92/92, the integrated lane passes 36/36, and Lean R325 compiles.  The
finite outcome is `FAIL_ON_GRID_ROUTE_LOCAL` for the unsplit flow.  At volume 6,
site 5, step 0, all four contexts have

| quantity | value |
|---|---:|
| left-hand side | (6.5371290\times10^{-7}) |
| recurrence right-hand side | (1.4959333\times10^{-14}) |
| residual | (6.5371289\times10^{-7}) |

Volumes 2 and 4 have no positive residual in this grid.

## Adversarial boundary

This is not a failure of the registered split recurrence.  The calculation
uses (e^{-itH}) for the full unsplit Hamiltonian, whereas EXP-001151 concerns
partial onsite/bond Trotter histories whose bond step has one-layer support
transfer.  The result therefore proves only that the unsplit flow cannot be
silently substituted for that split premise.  The next test is the same audit
with one exact onsite-plus-all-bond Trotter step.

No common-core, thermodynamic, common-α, OS/KMS/GNS, gap, continuum, C6,
Sector-A or Pre-A conclusion is claimed.
