# R-422 -- Finite residual core-tail coercivity reserve

R-422 / EXP-001267 is a T0 claim-nonbearing finite interface.  It reuses the
R-419 Q3 conditional rows and the R-421 Lyapunov tail without changing their
normalization, beta grid, orientation grid, alpha, or tail threshold.

For the block-mean-zero residual split, let `a` be the smallest core
restricted form eigenvalue, `kappa` the R-421 tail Hardy floor, and `eta` the
operator norm of the restricted core-tail cross block.  The finite inequality

```text
q(x,y) >= (min(a,kappa)-eta) (||x||^2+||y||^2)
```

follows from the retained cross term and `2|x y| <= x^2+y^2`.  The sharper
two-by-two eigenvalue is reported only as a diagnostic.

The primary executable passes `3522/3522` assertions over 858 rows and 114
eligible rows.  Twenty-four rows have positive conservative reserve and 90
have nonpositive reserve; the latter are retained as finite sufficient-budget
failures rather than clipped or hidden.  The safe reserve range is
`[-358.3346630467536, 1.5835608118417415]`.  The non-importing independent
lane passes `43/43` on three fixtures, the hostile lane passes `7/7`, the
integrated verifier passes `20/20`, and Lean R422 compiles.

This does not control the two-dimensional block-mean coarse sector, a common
Hamiltonian core, cutoff/volume/phase/exhaustion uniformity, R-399 history
limits, OS/KMS/GNS reconstruction, a physical gap, C6, Sector-A, Pre-A,
Yang-Mills, or mass gap.  The high-cutoff nonpositive reserve is a route
boundary only, not a physical gaplessness result.

**Authority:** [R-422 certificate](../../strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-certificate-260831.md), [machine manifest](../../strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json), [integrated run](../runs/2026-08-31-integrated-residual_core_tail_reserve/integrated.json), and [Lean R422](../../verification/lean/Tect/R422.lean).
