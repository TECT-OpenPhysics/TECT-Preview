# EXP-001087 — finite actual-Q3 second Duhamel coefficient support audit

## Scope and reproduction

This claim-nonbearing T-054 package isolates the first nonzero Taylor
coefficient of the direct cutoff difference for the two-site local character
used in EXP-001086. With `H_sigma=H+sigma W_L` and
`A_2=exp(i*a*(q_0+q_1)/hbar)`, the configuration nature of `W_L` gives
`[W_L,A_2]=0`, hence

```text
D_sigma''(0) = -sigma/hbar^2 * [W_L,[H,A_2]]
delta D_sigma''(0) = -beta [H,D_sigma''(0)].
```

The cutoff is applied only to bond coordinates. The seminorm is the two-sided
uncut-H Gibbs seminorm `Tr(rho X*X)+Tr(rho XX*)`.

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_second_duhamel_coefficient_support_audit.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_second_duhamel_coefficient_support_audit_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_second_duhamel_coefficient_support_audit_verify.py
```

Primary: 52/52. Independent: 52/52. Integrated: 45/45 with Lean R269.

## Findings

For `L=0.5`, the largest two-sided coefficient norms are:

| volume | `||D''(0)||_(beta,#)` | `||delta D''(0)||_(beta,#)` |
|---:|---:|---:|
| 2 | 0.9410369228 | 2.1370416950 |
| 4 face | 1.7020060967 | 7.3775956341 |

The V=4/V=2 ratios are `1.8086496` for the direct second coefficient and
`3.4522469` for its modular derivative. At `L=1.0`, the corresponding direct
values are `0.2443220` and `0.4419211`, with modular values `0.5552562` and
`1.9163859`. At `L=2.0`, the bond tail and coefficient norms are at the
finite numerical floor.

For every volume, radius, and orientation, the direct finite matrix evaluation
agrees with the commutator identity within the declared tolerance. The source
commutator `[W_L,A_2]` vanishes to the same tolerance, and the disjoint `(2,3)`
tail on the four-site face commutes with `A_2`. The independent lane agrees with
all primary rows and summaries.

## Decision and next action

The source-character and disjoint-tail identities provide the correct local
algebraic seed for an analytic local-class proof. However, the finite Gibbs
seminorm of the first nonzero direct coefficient and especially its modular
companion increase from the two-site target to the four-site face. This is not a
thermodynamic lower-bound theorem, but it means the next proof must control the
Gibbs-weighted local energy and modular domain explicitly; a bare operator-norm
or static finite coefficient cannot be promoted to a volume-uniform history
bound.

The next action is to derive a source/volume-uniform weighted bound for
`[H,[W_L,[H,A_2]]]` on the declared common core, or to enlarge the structured
volume family and register a formal scaling obstruction if that weighted
constant also grows. Positive-time history, direct `D,delta-D` Cauchy,
exhaustion, common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A, and Pre-A
remain open.

## Devil's-advocate review

1. **Taylor identity:** the direct finite matrix second derivative is evaluated
   from both `H+W_L` and `H-W_L` and compared with the commutator formula.
   **UPHELD.**
2. **Configuration commutation:** `[W_L,A_2]=0` is checked numerically for every
   declared row; it is not inferred from an omitted term. **UPHELD.**
3. **Cutoff scope:** onsite terms are unchanged and only bond coordinates are
   tapered. **UPHELD.**
4. **Support locality:** the disjoint four-site tail is tested separately; the
   finite check does not claim an infinite-volume theorem. **UPHELD.**
5. **Modular derivative:** `-beta[H,D''(0)]` uses the same H that defines rho;
   it is not replaced by a scalar multiple of `D''(0)`. **UPHELD.**
6. **Scaling:** V=4/V=2 ratios are reported as finite diagnostics, not as
   monotone asymptotic lower bounds. **UPHELD.**
7. **Independence:** the second lane rebuilds all oscillator, Hamiltonian,
   cutoff, commutator, Gibbs, and seminorm operations without importing the
   primary module. **UPHELD.**
8. **Lean:** R269 checks rational coefficient, sign, commutation, and scope
   fixtures only; it does not formalize floating-point spectra or limits.
   **UPHELD.**
9. **QFT promotion:** no direct Cauchy, common dynamics, OS/KMS/GNS
   identification, mass gap, continuum, C6, Sector A, or Pre-A result follows.
   **UPHELD.**

