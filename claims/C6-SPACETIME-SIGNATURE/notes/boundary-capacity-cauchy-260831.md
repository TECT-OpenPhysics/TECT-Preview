# R-423 -- Finite directed boundary-capacity Cauchy envelope

R-423 / EXP-001268 is a T0, claim-nonbearing finite interface.  On the
fixed R-419 conditional law and R-422 residual core/tail split, the transformed
cross block is bounded by the directed capacity

```text
rho_C = max_i sum_{j in T} c_ij/pi_i
rho_T = max_j sum_{i in C} c_ij/pi_j
eta_capacity = sqrt(rho_C*rho_T).
```

The finite edgewise Cauchy--Schwarz factorization gives
`|B[x,y]| <= eta_capacity ||x|| ||y||`, so the conservative reserve is
`min(a,kappa)-eta_capacity`.  Primary execution passes 2209/2209 assertions
over 858 conditional rows and 114 eligible rows; the exact R-422 cross norm is
dominated on every eligible row, but all 114 capacity reserves are nonpositive
(`[-3650.2671476576393,-1.7429838727911164]`).  Independent 40/40, hostile
7/7, integrated 18/18 and Lean R423 pass.

This is a finite boundary of a sufficient estimate.  It does not provide a
cutoff-, volume-, phase- or exhaustion-uniform capacity, a common Hamiltonian
core, a coarse Schur theorem, OS/KMS/GNS reconstruction, a continuum limit,
C6, Sector-A, Pre-A, Yang--Mills or mass-gap conclusion.

**Authority:** [R-423 certificate](../../strategy/pre-a-cp1-st8-q3lock-boundary-capacity-cauchy-certificate-260831.md), [machine manifest](../../strategy/pre-a-cp1-st8-q3lock-boundary-capacity-cauchy-manifest.json), [integrated run](../runs/2026-08-31-integrated-boundary_capacity_cauchy/integrated.json), and [Lean R423](../../verification/lean/Tect/R423.lean).
