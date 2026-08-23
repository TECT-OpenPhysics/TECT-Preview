# Finite A1 `F_ref` nonlinear stochastic-quantization candidate

## Status

This is a T0, claim-nonbearing candidate under EXP-000962. It is a finite
Galerkin QFT interface and owner crosswalk, not a production-owner theorem.

## 1. Functional and coercivity

The hash-pinned A1 functional distinguishes `F_decl` from the proposed
reference functional `F_ref`. The candidate uses `F_ref` only. Its quadratic
Fourier part has

\[
K_n=Y(|k_n|^2-q_*^2)^2+\mu_*,\qquad
\mu_*=r-Z^2/(4Y)>0.
\]

Combining the completed-square mass with the local quartic/sextic terms gives

\[
w(\rho)=\frac{\mu_*}{2}\rho+\frac{\lambda}{4}\rho^2
          +\frac{\gamma}{6}\rho^3.
\]

The derivative has the sign of
\(\gamma\rho^2+\lambda\rho+\mu_*\). The exact registered parameters have
\(\gamma>0\) and negative discriminant
\(\lambda^2-4\gamma\mu_*<0\), so this polynomial is strictly positive for
all real \(\rho\). The Class-II coefficient matrix has \(a>0\) and
\(ac-b^2>0\), hence its quadratic current form is positive definite.
Family, lock and shell contributions are nonnegative in the registered
scope. This yields a finite-cutoff coercive candidate energy.

## 2. Finite stochastic candidate

For a finite real Galerkin coordinate \(x\), choose the explicitly declared
identity mobility and define

\[
L_N f(x)=-\langle \nabla F_{\rm ref,N}(x),\nabla f(x)\rangle
       +\beta^{-1}\Delta f(x),\qquad \beta>0.
\]

The formal adjoint cancellation is exact:

\[
L_N^*e^{-\beta F_{\rm ref,N}}=0.
\]

This is a finite-dimensional reversible Gibbs candidate. The Lean cross-check
proves the quadratic positivity criterion, the Class-II square completion,
and the algebraic Gibbs residual cancellation without `sorry`, `admit`,
`axiom`, or `unsafe`.

## 3. R-192 owner crosswalk

The candidate supplies a chosen finite generator and its finite heat semigroup.
It does not supply a canonical Fourier-root filtration or conditional replica
law. It also does not prove the spatial derivative/intertwining identity for
the nonlinear raw current: the required raw-current spatial intertwiner is
absent. Nor does it provide a once-owned nonnegative production \(q_k\) ledger
(the production q-ledger is absent). These missing canonical filtration,
raw-current, and q-ledger slots remain unresolved even before any continuum
passage. Translation covariance and finite Gibbs invariance are insufficient
for those slots. The unchanged R-192 first missing owner therefore remains
`heat_root_incidence`.

## 4. Adversarial boundary

Replacing `F_ref` by `F_decl` is invalid because the A1 manifest records a
factor-of-two local-gradient mismatch and a Class-II coefficient mismatch.
Choosing identity mobility is a declared model choice, not a deduction from
static A1 data. Finite-dimensional Gibbs invariance is not a thermodynamic or
interacting-measure limit. No A13/T-050, Sector-A, Pre-A, physical-empty,
removal, continuum, or real-time conclusion follows.

No PDF is issued at this exploratory checkpoint.
