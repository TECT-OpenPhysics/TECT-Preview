# EXP-001070 Uniform finite-periodic single-character Duhamel remainder

## Decision

The exact finite Gibbs-isometric Duhamel theorem (EXP-001066) and the static full-character envelope (EXP-001069) combine to give a uniform finite-periodic Taylor remainder bound for one local configuration character.

## Exact interface

For a finite Gibbs member,
[
R_t(X)=\alpha_t(X)-X-t\delta_H(X)
=\int_0^t(t-s)\alpha_s(\delta_H^2(X))\,ds,
]
and Gibbs isometry gives
[
N_\beta(R_t(X))\le \frac{t^2}{2}N_\beta(\delta_H^2(X)).
]
For (X=W_a), EXP-001069 supplies (N_\rho(\delta_H^2(W_a))^2\le B_{\rm static}), so
[
N_\rho(R_t(W_a))^2\le \frac{t^4}{4}B_{\rm static}.
]

## Fixture and Lean cross-check

With (t=1/100) and the conservative static envelope (B_{\rm static}=53361),
[
\frac{t^4}{4}=\frac1{400000000},
qquad
N_\rho(R_t(W_a))^2\le\frac{53361}{400000000}=0.0001334025.
]
Lean R252 checks the rational time scaling and the conservative envelope.

## Adversarial review

- Finite member: the Duhamel/isometry theorem is used only at fixed finite Gibbs volume.
- Scaling: the squared factor is (t^4/4), not (t^2/2).
- Static input: the EXP-001069 estimate is not reused for evolved split histories.
- Observable class: only one local character is covered; products and density are open.
- Orientation: plus and minus finite members are not identified.
- Uniformity: the declared periodic compact-source family is not all exhaustions.
- Domain: no unbounded generator closure or modular multiplier is claimed.
- QFT: direct D/delta-D, OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open.

## Scope firewall

This closes a single-character finite-periodic remainder only. It does not close product/core density, split-history factorial summation, direct projected D or delta-D Cauchy, exhaustion independence, group law, common alpha, Hamiltonian-to-OS identification, KMS/GNS gap, continuum, C6, Sector A or Pre-A.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_single_character_uniform_duhamel_remainder.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_single_character_uniform_duhamel_remainder_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_single_character_uniform_duhamel_remainder_verify.py
lake env lean Tect/R252.lean
```

