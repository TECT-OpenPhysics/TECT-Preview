# Q3LOCK local Q2 Kubo-Mori Gibbs-cancellation boundary

R-371 isolates the critical theta-half cancellation needed by the local
Kubo-Mori route.  For doubled-bond eigenvalues `lambda_i` and finite Gibbs
weights `p_i`,

`L_ij |lambda_i-lambda_j| = |p_i-p_j|/beta`,

where the diagonal case uses the logarithmic-mean limit.  Thus a centered
Hermitian witness with entries `X_ij` satisfies the finite bound

`2 sum L_ij |lambda_i-lambda_j| |X_ij|^2
 <= (4/beta) sum_i p_i sum_j |X_ij|^2
 = (4/beta) Tr(rho_bond X^2)`.

The primary and independent lanes each pass `14235/14235` assertions over
`2816` all-prefix contexts; integrated passes `129/129`; Lean R371 passes;
the largest lane difference is `2.771e-13`.  The maximum identity error is
`2.689e-17` and the bound has no positive violation.  The largest sampled
local second moment is `42.156906839727924` at edge `d=6`, after values
`2.751158478344597`, `3.43464599148746`, and `4.704458970507892` at
`d=3,4,5`.

This finite result changes the analytic target: uniformity requires a
source/volume/cutoff-uniform local Gibbs second-moment estimate on a common
Hamiltonian-derived core.  It does not follow from the cancellation itself,
and the observed second-moment growth keeps that gate open.  The Gibbs state
used here is a finite doubled local-bond proxy, not the full interacting KMS
state.  Common core, common alpha, OS/KMS/GNS dynamics, gap, continuum, C6,
Sector-A and Pre-A remain open.

