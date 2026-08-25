# EXP-001156 - actual finite Q3 split-step recurrence audit

## Question

Does one exact onsite-plus-all-bond finite Q3 Lie-Trotter step satisfy the
registered four-context local q/p commutator recurrence without replacing the
split product by the unsplit Hamiltonian flow?

## Computation

The audit uses the canonical quartic Q3 Hamiltonian on volumes 2, 4 and 6,
oscillator dimension 3, beta=1, character amplitude 1/3, six steps of
delta=1/18, both real-time signs, both A/A* contexts, and two exact term
orders.  Each step is a product of exact matrix exponentials for every onsite
term and every full bond term.  The tested quantity is

\[
L_x^2=\|[q_x,A]\|_{\beta,#}^2+\|[p_x,A]\|_{\beta,#}^2,
\qquad
\|X\|_{\beta,#}^2=\operatorname{Tr}(\rho X^*X)+\operatorname{Tr}(\rho XX^*).
\]

The recurrence is

\[
L_x(n+1)\le (1+C\delta)L_x(n)+J\delta\sum_{y\sim x}L_y(n),
\qquad C=J=1.
\]

The primary lane also verifies that the onsite-plus-bond decomposition
reconstructs the canonical finite Hamiltonian before testing any row.

## Result

The primary lane passes 190/190 assertions, the independent lane passes
181/181, the integrated lane passes 60/60, and Lean R326 compiles.  Both term
orders pass every recurrence row in all four contexts and all three volumes.

| term order | V=2 maximum residual | V=4 maximum residual | V=6 maximum residual |
|---|---:|---:|---:|
| onsite then lexicographic bonds | -0.06071861939721224 | -0.02715599082635401 | 1.533017413440373e-14 |
| reverse term order | -0.06093425967767341 | -0.027845919416709303 | 1.645530484965069e-14 |

The declared recurrence tolerance is 1e-9; hence no positive residual occurs
on this finite grid.

## Adversarial boundary

This advances the applicability of the registered split-history recurrence only
for the stated finite matrices and term orders.  It does not establish a
volume-, cutoff- or beta-uniform estimate, an exact CCR common core, a
thermodynamic dynamics, a common alpha, OS/KMS/GNS reconstruction, a spectral
gap, a continuum limit, C6, Sector A or Pre-A.  The next audit varies source,
beta and volume/shape before any common-alpha promotion.

No claim tier changes, new result authority or negative-result authority are
created by this package.
