# EXP-001125 finite evolved dual-integrand cross-term certificate

## Question and scope

This checkpoint asks what the first nonzero term is in the finite Q3 cutoff
difference

\[
D_\sigma(t)=\alpha_t^{H+\sigma W_L}(A)-\alpha_t^H(A),
\qquad A=\exp(i a q_0/\hbar),
\]

when the coordinate tail `W_L` commutes with the local configuration character
`A`.  The package is T0 and claim-nonbearing.  It is a finite matrix bridge
toward the projected-Duhamel gate, not a thermodynamic, OS, KMS, GNS, gap,
continuum, C6, Sector-A, or Pre-A result.

## Exact finite identity

Write `delta_K(X)=i[K,X]/hbar`, `B=delta_H(A)`,
`C=delta_H(B)`, and `E_L=delta_W_L(B)`.  The finite coordinate construction
checks `[W_L,A]=0`.  Consequently, for each `sigma` in `{-1,+1}`,

\[
\delta_{H+\sigma W_L}^2(A)=C+\sigma E_L,
\qquad D_\sigma(0)=0,
\qquad D_\sigma'(0)=0.
\]

For finite unitary conjugation, the second derivative of `D_sigma` is

\[
D_\sigma''(s)=\alpha_s^{H+\sigma W_L}(C+\sigma E_L)
                 -\alpha_s^H(C).
\]

The operator norm is invariant under both finite unitary conjugations, so the
triangle inequality gives the honest finite bound

\[
\|D_\sigma(t)\|_{op}
\leq \frac{t^2}{2}\bigl(2\|C\|_{op}+\|E_L\|_{op}\bigr).
\]

This is deliberately an operator-norm statement.  It is not transferred to a
Gibbs or dual-state seminorm, because the signed dynamics need not preserve
the reference state.

## Reproducible evidence

- Primary: `codes/foundations/pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit.py`
  — 469/469 assertions.
- Independent: `codes/foundations/pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit_independent.py`
  — 321/321 assertions.
- Integrated: `codes/foundations/pre_a_cp1_st8_q3lock_evolved_dual_integrand_cross_term_audit_verify.py`
  — 32/32 integration assertions; Lean R296 PASS.
- Lean: `verification/lean/Tect/R296.lean` — exact rational fixture for the
  cross-term algebra, second-order coefficient, initial cancellation, and
  scope firewall.

The fixture covers the registered edge and square graphs, oscillator dimensions
3--7 on volume 2 and 3--4 on volume 4, cutoff radii 0.75, 0.9, and 1.0, times
0.1 and 0.2, and both signs.  The largest finite operator-bound ratio is
`0.32770398902982883`.  The finite state-seminorm cross-term-to-static-tail
ratio ranges from `0.7201853381375809` to `3.27318205723085`; the maximum is
the dual row `(volume=2, oscillator dimension=6, radius=1.0)`.  These are
finite diagnostics, not asymptotic constants.

## Adversarial review

1. **Generator algebra — UPHELD.**  The `delta_W delta_H(A)` term is retained;
   it is not erased after using coordinate commutation.
2. **Initial cancellation — UPHELD.**  Both `D(0)` and `D'(0)` are checked
   for both orientations.
3. **Norm transfer — UPHELD.**  The second-order bound is stated only in
   finite operator norm; state seminorm rows are separately reported.
4. **Dual state — UPHELD.**  `A rho A*` is evaluated separately and both
   trace legs are retained.
5. **Truncated CCR — UPHELD.**  No exact infinite-dimensional CCR or domain
   statement is inferred.
6. **Uniformity — UPHELD-OPEN.**  The finite cross-term ratio does not supply a
   source-, volume-, beta-, cutoff-, or exhaustion-uniform common-core bound.
7. **Lean boundary — UPHELD.**  R296 checks scalar bookkeeping only.
8. **QFT promotion — UPHELD-OPEN.**  Common alpha, OS/KMS/GNS identification,
   gap, continuum, C6, Sector A, and Pre-A remain open.

## Decision and next gate

The evolved route is advanced to an exact finite cross-term identity and a
finite operator-norm second-order bound.  The state-level QFT route is narrowed:
static tail control alone is insufficient; a separate common-core weighted
estimate for `E_L` and a comparison/isometry for the signed dynamics are
required.  The next gate is to prove such a state-norm transfer with a uniform
constant or to record a route-specific scaling obstruction.  No claim tier is
changed by this certificate.
