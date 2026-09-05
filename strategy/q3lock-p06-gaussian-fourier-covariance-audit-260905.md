# Q3LOCK P-06 Gaussian Fourier covariance audit

**Status:** T0 fixed-mesh diagnostic audit; P-06 remains open  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Related notes:** strategy/q3lock-p06-gaussian-tightness-normalizer-audit-260905.md; strategy/q3lock-p06-gaussian-reference-convergence-260905.md  
**PDF:** deferred until mathematical content freeze, external review, and final release review

## 1. Question and strict boundary

The two P-06 Gaussian notes use several exact Fourier and cyclic-graph
identities before passing a time-grid law to a continuous periodic loop.  This
audit rechecks those identities and their finite consequences independently:

1. the csc-squared sum and the mesh-uniform diagonal covariance bound;
2. the least-representative Fourier reindexing and a closed-form periodic
   massive covariance;
3. the n^-2 high-mode majorant;
4. the cyclic resistance identity and the increment bound; and
5. the exact source integral of periodic piecewise-linear interpolation.

All checks are fixed spatial volume and finite mesh.  Numerical convergence
fixtures and floating-point tolerances are diagnostic evidence; they are not
an analytic dominated-convergence proof.  No spatial thermodynamic limit,
weighted-tempered compactness, source cusp, phase coexistence, DLR
multiplicity, or publication status is changed.

## 2. Frozen Gaussian convention

For beta>0, m>0, a>0, N time slices, and epsilon=beta/N, use

    S_G,N(x) = (1/2) sum_k [
        (m/epsilon) (x_(k+1)-x_k)^2 + a*epsilon*x_k^2
    ],

with k+N identified with k.  The scalar precision eigenvalue is

    kappa_(N,j) = (4*m/epsilon)*sin^2(pi*j/N) + a*epsilon.

The vertex covariance at cyclic separation r is

    G_N(r) = (1/N) sum_(j=0)^(N-1)
             cos(2*pi*j*r/N) / kappa_(N,j).

The zero mode contributes exactly 1/(beta*a).  For j!=0, dropping the
positive a*epsilon term and using

    sum_(j=1)^(N-1) csc^2(pi*j/N) = (N^2-1)/3

gives the derived bound

    G_N(0) <= 1/(beta*a) + beta/(12*m).

For the continuous periodic operator -m*d^2/dt^2+a, the corresponding
closed-form covariance at circle distance d in [0,beta/2] is

    G_a(d) = cosh(sqrt(a/m)*(beta/2-d))
             / (2*sqrt(a*m)*sinh(beta*sqrt(a/m)/2)).

The verifier compares the finite covariance to this formula and to
truncated Fourier sums.  These comparisons test the written convention;
they do not replace the analytic summable-majorant argument.

## 3. Cyclic resistance and interpolation identities

For 1<=r<=N-1, the finite Fourier identity used for increments is

    sum_(j=1)^(N-1)
      [1-cos(2*pi*j*r/N)] / sin^2(pi*j/N)
      = 2*r*(N-r).

It yields

    Var_gamma(x_k-x_(k+r))
      <= epsilon*r*(N-r)/(m*N)
      <= epsilon*min(r,N-r)/m.

The periodic piecewise-linear interpolation on a cell is

    I_N(x)(t_k+theta*epsilon)
      = (1-theta)*x_k + theta*x_(k+1),
      0<=theta<=1.

The integral identity is exact after summing all cyclic cells:

    integral_0^beta I_N(x)(t) dt
      = epsilon * sum_k x_k.

The verifier checks these formulas on several even meshes and exact rational
interpolation fixtures.  It also checks that the negative interpolation
coefficient used in a hostile mutation reverses an order relation.

## 4. Executable evidence

The independent verifier is

    verification/scripts/q3lock_p06_gaussian_fourier_covariance_audit.py

Run from the repository root with

    E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/q3lock_p06_gaussian_fourier_covariance_audit.py

It derives every covariance, bound, Fourier tail, resistance value, and
convergence error from the declared inputs.  The result JSON records all
assertion rows and the verifier hash.  A second clean replay is compared
byte-for-byte before this result is cited.

## 5. Adversarial checks

| Objection | Disposition |
|---|---|
| The pure periodic kinetic Gaussian can be used without an auxiliary mass | **UPHELD AS FALSE:** the constant mode is singular; a>0 is explicit. |
| The diagonal bound hides an N-dependent constant | **UPHELD AS FALSE:** the zero mode and csc² sum are recomputed for every tested N. |
| A direct Fourier sum is enough; reindexing and high modes need no check | **UPHELD AS FALSE:** direct and least-representative sums and the n^-2 majorant are checked separately. |
| The resistance formula has an unverified factor of two | **UPHELD AS FALSE:** the cyclic sum is evaluated for every tested r and compared with 2*r*(N-r). |
| Vertex covariance convergence automatically implies sup-norm loop convergence | **UPHELD AS FALSE:** interpolation increments and tightness hypotheses remain separate analytic obligations. |
| The source integral incurs an untracked epsilon error | **UPHELD AS FALSE:** the cyclic trapezoid sum is checked exactly with rational arithmetic. |
| Finite floating-point fixtures prove the Gaussian weak-limit theorem | **UPHELD AS FALSE:** they are diagnostic; the analytic majorant, tightness, and weighted-law argument remain open for independent review. |

## 6. Disposition and next gate

The stated finite Gaussian convention, csc² normalization, Fourier
reindexing, n^-2 tail scale, cyclic resistance factor, increment upper bound,
and exact source interpolation identity are internally consistent on the
declared fixtures.  This is an advanced T0 audit, not a theorem certification.
The next gate is a line-by-line mathematical review of the summable-majorant
argument, the Gaussian-to-loop tightness passage, the residual compact
Riemann-sum convergence, and the source-uniform integrability estimates at
fixed spatial volume.  P-06/P-09, pressure, KKK, source-window, claim
registration, external referee, content-freeze, and final PDF gates remain
open.

## 7. Explicit nonclaims

No unconditional Gaussian loop-limit theorem, continuous-loop FKG theorem,
FSS theorem, pressure limit, infrared lower bound, strict source cusp, phase
coexistence, DLR multiplicity, extremality, purity, clustering, KMS state,
real-time dynamics, ground-state phase, spectral gap, continuum limit,
physical-vacuum, cosmological, Sector A, CP1, C6, Pre-A, Yang--Mills, or
mass-gap conclusion is asserted.  No claim card, manuscript, submission,
upload, release, tag, or PDF is created.
