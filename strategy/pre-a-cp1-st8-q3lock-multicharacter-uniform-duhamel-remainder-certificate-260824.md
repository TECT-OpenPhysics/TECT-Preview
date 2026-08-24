# EXP-001072 Finite-support multi-character Duhamel remainder

## Decision

The exact finite Gibbs-isometric Duhamel theorem (EXP-001066) and the static finite-support multi-character envelope (EXP-001071) combine to give an explicit finite-periodic Taylor remainder bound for the declared support and amplitude vector.

## Exact interface

For a finite Gibbs member,

\[
R_t(X)=\alpha_t(X)-X-t\delta_H(X)
 =\int_0^t(t-s)\alpha_s(\delta_H^2(X))\,ds,
\]

and Gibbs isometry gives

\[
N_\beta(R_t(X))\le \frac{t^2}{2}N_\beta(\delta_H^2(X)).
\]

For the finite-support character \(W_{\mathbf a}\), EXP-001071 supplies
\(N_\rho(\delta_H^2(W_{\mathbf a}))^2\le B_{\rm static}\). Therefore

\[
N_\rho(R_t(W_{\mathbf a}))^2
 \le \frac{t^4}{4}B_{\rm static}.
\]

## Fixture and Lean cross-check

With support size two, amplitudes \((1/4,-1/3)\), \(t=1/100\), and the conservative static envelope \(B_{\rm static}=293764\),

\[
\frac{t^4}{4}=\frac1{400000000},
\qquad
\frac{t^4}{4}B_{\rm static}
 =\frac{293764}{400000000}
 =\frac{73441}{100000000}=0.00073441.
\]

Lean R254 checks the time factor, both forms of the rational product, positivity and strict smallness.

## Adversarial review

- Finite member: the Duhamel/isometry theorem is used only at fixed finite Gibbs volume.
- Scaling: squaring the \(t^2/2\) inequality produces \(t^4/4\), not \(t^2/4\).
- Static versus history: the EXP-001071 input is not promoted to evolved split histories.
- Support: the result is for the declared finite support and amplitudes, not an arbitrary product algebra.
- Orientation: no identification of plus and minus finite Gibbs carriers is made.
- Uniformity: the periodic compact-source fixture is not an all-exhaustion theorem.
- Domain: no unbounded generator closure or modular multiplier is claimed.
- QFT: direct \(D/\delta D\), OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open.

## Scope firewall

This closes a finite-support finite-periodic remainder only. It does not close product/core density, split-history factorial summation, direct projected \(D\) or \(\delta D\) Cauchy, exhaustion independence, group law, common alpha, Hamiltonian-to-OS identification, KMS/GNS gap, continuum, C6, Sector A or Pre-A.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_uniform_duhamel_remainder.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_uniform_duhamel_remainder_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_uniform_duhamel_remainder_verify.py
lake env lean Tect/R254.lean
```

## QFT boundary

This is a finite QFT-facing interface checkpoint. It is not a product-class dynamics theorem, an OS reconstruction, a KMS/GNS result, a mass-gap proof, a continuum result, a C6/Sector-A/Pre-A result, a TECT production map or a Clay result.
