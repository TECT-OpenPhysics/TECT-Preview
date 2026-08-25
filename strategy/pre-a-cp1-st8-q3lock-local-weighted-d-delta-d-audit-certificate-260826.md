# Actual Q3 local-energy four-leg D audit

## Result

EXP-001147 evaluates the four weighted Hilbert--Schmidt legs of the actual
finite Q3 history

\[
D_\sigma(t)=U(H+\sigma W_L,t) A U(H+\sigma W_L,t)^*
            -U(H,t) A U(H,t)^*
\]

with both the global shifted Hamiltonian weight and the positive local edge
weight.  The local weight is not diagonalized with the Gibbs Hamiltonian.

The primary matrix-product lane passes 105/105 checks over 36 rows (volumes
2, 4, 6; beta 0.5, 1, 2; radii 0.5, 1; time 0.05; both orientations).  The
independent trace lane passes 77/77 checks, the integrated verifier passes
13/13, and Lean R317 passes the finite four-leg arithmetic interface.

For the maximum four-leg sum at each beta, the local-weight rows are:

| volume | beta 0.5 | beta 1 | beta 2 |
|---:|---:|---:|---:|
| 2 | 1.5582388906e-05 | 1.7993155369e-05 | 2.1824228487e-05 |
| 4 | 3.5082596819e-05 | 5.9350271376e-05 | 1.0314165594e-04 |
| 6 | 4.5493115615e-05 | 9.0996077453e-05 | 1.7439045293e-04 |

The corresponding full-global maxima reach 7.0936355473e-04.  The finite
local-volume ratio is 11.1915, versus 45.5234 for the full-global baseline.
This is a route-selection diagnostic, not a uniformity theorem.

## Boundary

The result proves only finite actual-Q3 local-weight rows and their independent
trace reconstruction.  It does not prove a source-, volume-, cutoff-, or
beta-uniform estimate, modular-domain transfer, direct D/delta-D Cauchy,
product/core density, exhaustion independence, common alpha, OS/KMS/GNS
identification, a gap, continuum, C6, Sector A, or Pre-A.

The surviving proof target is a local/centered energy-weighted common-core
estimate, with the first weighted local-energy cone as upstream input.
