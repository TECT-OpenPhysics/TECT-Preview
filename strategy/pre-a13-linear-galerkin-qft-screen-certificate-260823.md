# Finite A1 Galerkin QFT candidate: exact scope certificate

## Status

This is a T0, claim-nonbearing exploration under EXP-000961. It is a
conditional finite-dimensional QFT interface, not a production-owner result.

## 1. A1 quadratic operator

For a Fourier mode (n\in\mathbb Z^3), (k_n=2\pi n/L) and the registered
quadratic kernel is

\[
 K_n=r+Z|k_n|^2+Y|k_n|^4
     =Y(|k_n|^2-q_*^2)^2+\mu_*,
 \quad q_*^2=-Z/(2Y),\quad \mu_*=r-Z^2/(4Y).
\]

The exact registered decimals give (Y>0) and (mu_*>0). The family,
lock, and nonnegative shell terms are positive semidefinite, hence the finite
linear Hessian satisfies (H_n\succeq K_n I_3\succ0).

## 2. Conditional QFT/OU interface

On a finite Galerkin set, identity-mobility Model-A stochastic quantization
of the quadratic part is the finite OU system

\[
 dX_t=-H X_t\,dt+\sqrt{2/\beta}\,dW_t.
\]

Its centered invariant complex Gaussian has covariance

\[
 C_n=\beta^{-1}H_n^{-1},\qquad
 \|C_n\|_{op}\le \beta^{-1}K_n^{-1}.
\]

This is a conditional construction from the A1 quadratic Hessian. The
nonlinear (\lambda,\gamma), Class-II, feedback, and conditional-replica
terms are not silently inserted into this OU law.

## 3. Current and one-use output charge

For the three embedded Hermitian generators (T_A),

\[
 \widehat J_A(r)=i k_r\sum_p X_p^\dagger T_A X_{p+r}.
\]

For independent proper complex Gaussian roots and (r\ne0), Wick's rule and
the operator bound give

\[
 \mathbb E\sum_A|\widehat J_A(r)|^2
 \le 6|k_r|^2\beta^{-2}
 \sum_p K_p^{-1}K_{p+r}^{-1}.
\]

The factor six is (3\) generators times Hilbert--Schmidt square (2); it is
not a rootwise double payment. Applying the scalar output heat
\(e^{-K_r t}\) and integrating (2e^{-2K_rt}) gives one charge

\[
 q_r=6|k_r|^2K_r^{-1}\beta^{-2}
       \sum_p K_p^{-1}K_{p+r}^{-1}\ge0.
\]

## 4. Tail screen

The completed square gives (K_n^{-1}=O(\langle n\rangle^{-4})) in three
dimensions. The convolution retains the fourth-order tail, so
\(\sum_pK_p^{-1}K_{p+r}^{-1}=O(\langle r\rangle^{-4})\). Since
\(|k_r|^2/K_r=O(\langle r\rangle^{-2})), the charge is
\(q_r=O(\langle r\rangle^{-6})\), and \(\sum_{r\ne0}q_r<\infty\).

The executable finite ledger checks positivity and monotone cutoff growth for
the registered cutoffs. The analytic tail statement is conditional on the
linear Gaussian covariance and scalar output-heat assumptions.

## 5. Adversarial boundary

The package does not prove that this OU semigroup is the nonlinear A1
production dynamics. It does not supply the missing `heat_root_incidence` map
for R-192, because that contract requires the full nonlinear heat/root,
feedback, forest, returned-low, source and sextic owners. A generic external
kinetic coefficient would be a different model. No A13 gate, T-050, Sector-A,
Pre-A, physical-empty, continuum, removal, or real-time conclusion follows.

## Reproduction

Use the pinned TECT runtime with the primary, non-importing independent, and
integrated scripts named in the manifest. The Lean entrypoint proves the exact
factor-six and heat-integral identities without `sorry`, `admit`, `axiom`, or
`unsafe`.
