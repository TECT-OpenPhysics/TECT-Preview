# R-408 effective-resistance note

R-408 is a finite, claim-nonbearing T0 checkpoint.  It uses the Moore--Penrose
inverse of the intrinsic momentum conductance Laplacian rather than a chosen
spanning tree.  For a conditional law `pi`,

```
R_xy=(e_x-e_y)^T L^+(e_x-e_y)
Rbar_pi=sum_{x<y} pi_x*pi_y*R_xy
```

and pairwise Cauchy--Schwarz gives `Var_pi(f)<=Rbar_pi E(f)`.  Thus
`Rbar_pi**(-1)` is a constructive finite lower bound, independent of tree
choice.  The unordered-pair convention is explicit.

The primary audit passes `43630/43630` assertions over `7` volume-two
cutoffs, `2688` contexts and `21120` conditional rows.  The independent lane
passes `43630/43630`, the hostile lane `6/6`, the integrated verifier `37/37`,
and Lean R408 compiles.  The exact intrinsic gap range is
`[0.7570174175402339,5.647863075935321]`; the resistance-average range is
`[0.44413751605180657,2.0052069566897672]`; and the resulting lower-bound
range is `[0.49870164107689835,2.251554898783544]`.  The smallest positive
Laplacian eigenvalue is `0.020747640155030216`, the largest resistance is
`85.99011817086337`, and the minimum residual is roundoff
(`-1.0641664309263875e-25`).

The hostile lane checks the disconnected diagonal-q mutation, the exact
three-node pair normalization (`Rbar=4/9`, bound `9/4`), and rejection of a
doubled bound.  The independent lane rebuilds the finite data without the
R-408 primary module and agrees within `5e-6`.

This is only a finite electrical interface.  The open debt is a
cutoff-, volume-, phase- and exhaustion-uniform resistance/Green-kernel bound
on a common Hamiltonian core, its transfer to the R-399 shell, and the later
OS/KMS/GNS and physical-sector obligations.  No claim tier changes and no
continuum or physical mass-gap conclusion is made.
