# EXP-001126 Gibbs condition-number transfer certificate

## Question and scope

The preceding finite cross-term package gives an operator-norm second-order
bound for the evolved cutoff difference.  This checkpoint audits the common
finite-state transfer step: replacing unitary invariance by a two-sided Gibbs
seminorm comparison controlled by the global density-matrix condition number.
The package is T0 and claim-nonbearing.  It diagnoses one transfer route; it is
not a thermodynamic or OS/KMS/GNS theorem.

## Finite comparison lemma

Let `rho` be a faithful finite density matrix, let `U` be unitary, and set
`kappa(rho)=lambda_max(rho)/lambda_min(rho)`.  For any matrix `X`,

\[
\begin{aligned}
N_\rho(U^* X U)^2
&\le 2\lambda_{\max}(\rho)\,\|X\|_F^2,\\
N_\rho(X)^2
&\ge 2\lambda_{\min}(\rho)\,\|X\|_F^2,
\end{aligned}
\]

so

\[
N_\rho(U^* X U)\le \sqrt{\kappa(\rho)},N_\rho(X).
\]

For a unitary character `A`, `rho_dual=A rho A*` has the same spectrum and
the same condition number.  For a finite Gibbs state of `H`,

\[
\log\kappa(\rho)=\beta(E_{\max}-E_{\min}).
\]

The lemma is exact at finite matrix level, but it is a global spectral
comparison, not the local modular weight required by the Q3 common-core route.

## Reproducible evidence

- Primary: `codes/foundations/pre_a_cp1_st8_q3lock_gibbs_isometry_condition_number_audit.py`
  — 356/356 assertions.
- Independent: `codes/foundations/pre_a_cp1_st8_q3lock_gibbs_isometry_condition_number_audit_independent.py`
  — 356/356 assertions.
- Integrated: `codes/foundations/pre_a_cp1_st8_q3lock_gibbs_isometry_condition_number_audit_verify.py`
  — 31/31 assertions; Lean R297 PASS.
- Lean: `verification/lean/Tect/R297.lean` — exact rational condition-number,
  two-sided comparison, dual-spectrum, and scope fixtures.

The actual-Q3 finite fixture gives `log(kappa)` from
`3.7746480326544107` through `33.02174678003` across the declared edge and
square regulator rows.  The largest square-root factor is
`exp(16.510873390015)=14810891.644688701`.  The directly tested `C` and `E_L`
state-norm ratios remain finite (log range
`-0.012750309285080705` to `0.02167455105053474`), but those operator-specific
ratios do not replace a uniform comparison theorem.

## Adversarial review

1. **Condition-number algebra — UPHELD.**  Both trace legs are bounded using
   the extremal eigenvalues; no one-sided trace shortcut is used.
2. **Dual state — UPHELD.**  The dual spectrum is checked numerically and is
   used only through unitary spectral invariance.
3. **Faithfulness — UPHELD.**  Every finite Gibbs matrix in the fixture has a
   positive minimum eigenvalue; no infinite-volume faithfulness is inferred.
4. **Global/local distinction — UPHELD.**  The factor is based on the full H
   spectral range, not a local modular energy weight.
5. **Uniformity — UPHELD-OPEN.**  The finite log-condition range is not an
   asymptotic theorem, but it makes the global comparison unusable as a claimed
   uniform constant without a new argument.
6. **Truncated CCR — UPHELD.**  No unbounded common-core or exact CCR result is
   asserted.
7. **Lean boundary — UPHELD.**  R297 formalizes scalar bookkeeping only.
8. **QFT promotion — UPHELD-OPEN.**  Common alpha, OS/KMS/GNS identification,
   gap, continuum, C6, Sector A, and Pre-A remain open.

## Decision and next gate

The global Gibbs condition-number transfer is an exact finite lemma but is not
an acceptable uniform QFT bridge on the tested regulator family: its generic
factor reaches about 14.8 million.  The live proof must therefore use a local
energy/modular weight or a cancellation-aware state estimate on one common Q3
core.  This is a route boundary, not a refutation of all state-weighted or
analytic/Frechet routes, and no claim tier changes.
