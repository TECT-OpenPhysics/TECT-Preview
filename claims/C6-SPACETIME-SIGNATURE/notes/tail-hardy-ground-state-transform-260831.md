# R-421 finite tail-supported Hardy interface

## Result and scope

R-421 is a T0, claim-nonbearing finite algebra checkpoint for T-054.  On the
hash-pinned R-419 parent, with no change to the Q3 functional, conductance or
log-domain normalization, it verifies the reversible ground-state transform

```text
E(f) = sum_i pi_i h_i f_i^2
       + 1/2 sum_ij c_ij V_i V_j (f_i/V_i - f_j/V_j)^2,
h_i = -[pi_i^(-1) sum_j c_ij(V_j-V_i)]/V_i,
E(f) = 1/2 sum_ij c_ij(f_i-f_j)^2.
```

The weighted-square remainder is nonnegative.  Therefore, for a declared tail
`T`, `f_i=0` off `T`, and `h_i>=kappa>0` on `T`, the finite Hardy consequence
`E(f)>=kappa sum_{i in T} pi_i f_i^2` follows.  The statement is tail-only;
it does not control a general observable's core mean or boundary term.

## Executed verification

The primary lane covers six selected Q3 volume/cutoff systems, three beta
values and both collar orientations: 858 conditional rows and 1128
tail-supported vectors, with 6544/6544 assertions passing.  The minimum tail
rate is `0.4188403678721089`, the maximum identity residual is
`1.4210854715202004e-14`, and the minimum remainder/Hardy slack is
`0.004172932635476484`/`0.004172932635476481`.

The non-importing independent lane passes 63/63 assertions on three
reversible graph fixtures and twelve vectors.  Its maximum identity residual
is `2.220446049250313e-16`; its minimum tail rate is `5.039999999999998`.
The hostile lane rejects all 7/7 invalid mutations.  The integrated verifier
passes 19/19 and `verification/lean/Tect/R421.lean` compiles.

## Adversarial review

- Reversed generator sign: rejected.
- Omitted ground-state remainder: rejected.
- Asymmetric conductance: rejected.
- Nonpositive weights or Lyapunov vector: rejected.
- Non-tail-supported test vector: rejected.
- Forged rate floor: rejected.
- Uniform or physical promotion: explicitly withheld.

## Boundary

The result does not prove a cutoff-, volume-, phase- or exhaustion-uniform
Hardy constant, a global Poincare or Schur inequality, a common Hamiltonian
core, a split-limit dynamics, OS/KMS/GNS reconstruction, a sector gap, a
continuum limit, C6, Sector-A, Pre-A, Yang--Mills or mass-gap closure.

The next mathematical step is to establish this transform on a domain-controlled
unbounded Q3 common core and add a uniform variance decomposition paying the
core and boundary terms for the actual R-399/R-415 history observables.
