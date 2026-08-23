# Exact nonlinear F_ref mode-mixing witness

## Status

This is a T0, claim-nonbearing finite Fourier witness under EXP-000963. It
tests the smallest root chart against the actual local nonlinear term of the
hash-pinned proposed `F_ref`; it is not a production-owner theorem.

## Exact calculation

Use the integer frequency variable `z=exp(i k x)` and the registered input

\[
\phi(z)=z+z^2=z(1+z),\qquad \rho=\overline{\phi}\phi.
\]

The conjugate Fourier rule gives

\[
\rho(z)=2+z+z^{-1}=z^{-1}(1+z)^2.
\]

For the local sextic contribution in the proposed reference functional, the
real gradient contains `gamma*rho^2*Psi`. On this one-component chart,

\[
\rho^2\phi=z^{-1}(1+z)^5
 =z^{-1}+5+10z+10z^2+5z^3+z^4.
\]

Thus the input root support `{1,2}` is not invariant: the nonlinear drift
creates modes `-1`, `0`, `3`, and `4` in addition to the original modes. The
calculation is exact over integer Laurent coefficients, and R198 checks the
polynomial identity after multiplying by the invertible factor `z^2`.

## Owner consequence

This does not show that a suitable filtration is impossible. It shows that the
naive R-192 two-root filtration cannot be the filtration of the nonlinear
`F_ref` drift. A valid production owner must explicitly include the generated
frequency blocks, define conditional projections/replicas for them, and prove
that the raw-current derivative and one-use nonnegative `q_k` ledger (the
production q-ledger) respect
that enlarged order. The finite witness supplies none of those owners.

## Adversarial boundary

Dropping the conjugate factor, replacing the sextic power by a linear term, or
declaring the output support to equal the input roots changes the model. A
finite mode-mixing identity is not a heat-root incidence theorem, an interacting
Gibbs construction, an A13/T-050 estimate, a Sector-A or Pre-A closure, or a
continuum/real-time result. No PDF is issued at this checkpoint.
