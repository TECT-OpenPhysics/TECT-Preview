# EXP-001068 uniform kinetic character moment corollary

## Decision

The registered finite-periodic Q3 inputs include the onsite form comparison

```text
k_x >= 1 + p_x^2/(2 chi) + gamma q_x^4
```

and the uniform fifth Gibbs moment

```text
m5 = sup phi_(Lambda,h)(k_x^5) < infinity.
```

Therefore, by functional calculus,

```text
phi(p_x^4) <= 4 chi^2 m5.
```

For the configuration character `W_a=exp(i*a*q_x/hbar)`, put
`P_plus=p_x+a/2` and `P_minus=p_x-a/2`. The Weyl relation gives

```text
N_rho(W_a P_plus^2)^2
 = phi(P_plus^4) + phi(P_minus^4).
```

Using `|u+v|^4 <= 8(|u|^4+|v|^4)` in both orientations yields

```text
N_rho(W_a P_plus^2)^2 <= 64 chi^2 m5 + a^4.
```

Consequently the kinetic summand of the EXP-001067 second commutator obeys

```text
N_rho((a^2/(chi^2*hbar^2)) W_a P_plus^2)^2
 <= (a^4/(chi^4*hbar^4)) (64 chi^2 m5 + a^4).
```

No modular multiplier estimate for `W_a` is used in this calculation.

## Scope boundary

This closes a uniform kinetic subgate over the registered finite periodic,
fixed-beta, compact-source family. It does not include the full Q3 force
summand, whose complete onsite-plus-edge second moment must still be derived.
It also does not construct a common OS representation, direct `D`/`delta-D`
exhaustion Cauchy theorem, common alpha, KMS/GNS identification, a gap,
continuum, C6, Sector A or Pre-A.

## Adversarial review

1. **Authority scope.** The upstream `m5` and onsite coercivity are not extended
   to arbitrary boundaries or all graph shapes. **UPHELD.**
2. **Moment reduction.** The implication from `p_x^2/(2 chi)<=k_x` and `k_x>=1`
   to `p_x^4<=4 chi^2 k_x^5` uses only functional calculus. **UPHELD.**
3. **Shift constant.** Both `p_x+a/2` and `p_x-a/2` use the same derived
   fourth-power inequality; the `a^4` term is retained. **UPHELD.**
4. **Weyl ordering.** `W_a p_x W_a^*=p_x-a` is used only after forming
   `W_a P_plus^4 W_a^*`, so the second orientation is exact. **UPHELD.**
5. **Modular shortcut.** No bound on `rho^t W_a rho^-t` is assumed. **UPHELD.**
6. **Force separation.** The force part is not hidden in the kinetic estimate;
   the full double commutator remains open. **UPHELD.**
7. **Thermodynamic promotion.** Uniform constants over the registered family do
   not by themselves give an exhaustion or OS identification theorem. **UPHELD.**
8. **Lean scope.** R250 checks exact rational fixtures only, not unbounded
   domains or the upstream Gibbs-moment theorem. **UPHELD.**
9. **QFT promotion.** No KMS, GNS-gap, continuum, C6, Sector A or Pre-A gate
   is closed by this subresult. **UPHELD.**

## Reproducibility

The primary and independent scripts, integrated verifier and Lean entrypoint
`verification/lean/Tect/R250.lean` are claim-nonbearing. No result, negative
record, changelog event or PDF is created by this package.

