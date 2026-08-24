# EXP-001067 finite kinetic/force double-commutator split

## Decision

The exact finite polynomial-CCR calculation separates the second generator of
the local configuration character into a kinetic term and a local force term:

```text
delta_H^2(W_a(x))
 = -(a^2/(chi^2 hbar^2)) W_a(x) (p_x+a/2)^2
   -(i a/(chi hbar)) W_a(x) F_x,
F_x = partial_(q_x)V.
```

The force term is the interface already developed in EXP-001058--EXP-001061.
The kinetic term is independent and requires a fourth momentum moment together
with a modular multiplier or domain estimate before its two-sided Gibbs
seminorm can be made uniform.

## Exact adversarial witness

Take

```text
H_n = diag(0,n),  rho_n = diag(1,exp(-beta*n))/(1+exp(-beta*n)),
W = sigma_x,  hbar = 1.
```

The force is identically zero. Nevertheless,

```text
delta_n^2(W) = -n^2 W,
N_(rho_n)(W)^2 = 2,
N_(rho_n)(delta_n^2(W))^2 = 2 n^4.
```

For the exact rational fixture `n=4`, the last value is `512`. Thus a bound
that uses only a local force moment cannot control the kinetic contribution.
This is a route-local finite-dimensional witness, not a no-go theorem for the
canonical Q3 Hamiltonian.

## QFT interface

This checkpoint advances the QFT-facing Hamiltonian-to-OS route by identifying
the precise remaining static input after EXP-001066: a volume/source/cutoff-
uniform kinetic fourth-moment and modular multiplier estimate on the declared
word core. It does not prove that estimate, the actual Q3 four-context history,
direct `D` or `delta-D` Cauchy convergence, exhaustion independence, a common
alpha, KMS/GNS identification, a gap, a continuum, C6, Sector A or Pre-A.

## Adversarial review

1. **CCR sign.** The convention is `delta=i[H,.]/hbar`; using
   `[p,W_a]=a W_a` and `delta(p)=-F` gives the displayed signs. **UPHELD.**
2. **Ordering.** The force commutes with the configuration character, while
   the shifted momentum square is retained in its displayed order. **UPHELD.**
3. **Force reuse.** The endpoint moment is applied only to the force summand;
   no momentum moment is smuggled in. **UPHELD.**
4. **Witness interpretation.** The two-level family is an exact control model,
   not the spectrum of the Q3 lattice Hamiltonian. **UPHELD.**
5. **Two orientations.** Both terms of the two-sided seminorm are included,
   giving `2` and `2 n^4` exactly. **UPHELD.**
6. **Thermodynamic promotion.** Growth in the control family does not by
   itself prove growth in the Q3 volume sequence. **UPHELD.**
7. **Lean scope.** R249 checks rational scaling and fixtures only; it does not
   formalize unbounded CCR domains or Gibbs trace limits. **UPHELD.**
8. **QFT promotion.** No OS, KMS, GNS, continuum, C6, Sector A or Pre-A gate
   is closed by this package. **UPHELD.**
9. **Negative boundary.** The shortcut is rejected only as a route step; no
   global negative-result authority is created. **UPHELD.**

## Reproducibility

Primary and independent exact-arithmetic scripts are paired with an integrated
verifier and Lean entrypoint `verification/lean/Tect/R249.lean`. The package is
claim-nonbearing and creates no changelog event, result, negative record or PDF.

