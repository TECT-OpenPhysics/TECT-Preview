# R-375 odd-Matsubara Lipschitz-budget boundary

R-375 extracts a new QFT-facing stability interface from the R-374
positive-layer expansion.  For `Delta>=0` and `omega_n=(2n+1)pi`, define

```text
m_n(beta,Delta) = 8 Delta / (omega_n^2 + beta^2 Delta^2).
```

Its scalar derivative obeys

```text
|m_n'(beta,Delta)|
  = 8 |omega_n^2-beta^2 Delta^2|
      / (omega_n^2+beta^2 Delta^2)^2
  <= 8/omega_n^2.
```

Consequently a finite partial sum has the Lipschitz budget
`L_N=sum_(n<N) 8/omega_n^2`, while the odd-frequency identity records the
infinite budget `sum_(n>=0)8/omega_n^2=1`.  The exact capped kernel has the
independent derivative bound `|d[(2/beta)tanh(beta Delta/2)]/dDelta|<=1`.

Primary and independent lanes evaluate these envelopes on sampled transition
energies spanning every declared finite-Q3 spectrum and count every
all-prefix orientation/sign/adjoint context.  Lean R375 proves the scalar
nonnegativity and derivative envelope in an abstract positive-frequency
variable; it does not formalize eigenvector perturbation theory, spatial
commutators, infinite series, traces or limits.

This is T0 and claim-nonbearing.  It suggests that a successful cutoff
comparison may need only one first Liouvillian variation after an independent
eigenvector-rotation estimate, but it does not prove that reduction.  Common
core, common alpha, OS/KMS/GNS, gap, continuum, C6, Sector-A and Pre-A remain
open.
