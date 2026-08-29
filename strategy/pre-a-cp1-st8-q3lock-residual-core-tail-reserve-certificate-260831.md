# R-422 -- Finite residual core-tail coercivity reserve

## Decision

R-422 / EXP-001267 is a T0, claim-nonbearing finite interface.  It combines
the R-421 tail-supported Hardy input with a block-mean-zero core form and keeps
the core-tail cross block explicitly.  The conservative reserve is

```text
lambda_safe = min(a, kappa) - eta,
```

where `a` is the smallest core restricted form eigenvalue, `kappa` is the
R-421 tail drift floor, and `eta` is the restricted cross-block operator norm.
For any residual vector `(x,y)`, `2 |x^T A_CT y| <= eta (||x||^2+||y||^2)`
and therefore

```text
q(x,y) >= lambda_safe (||x||^2 + ||y||^2).
```

The sharper two-by-two eigenvalue is recorded as a diagnostic only and is not
used as a promoted bound.

## Fixed scope and inputs

The R-419 Q3 conditional law, projected momentum conductance, `alpha=1/40`,
`theta=4`, beta values `{1/2, 2, 8}`, both collar orientations, and the six
systems `(V,d)=(2,3),(2,6),(2,12),(3,3),(3,4),(4,4)` are reused without
retuning.  The residual split is the orthogonal complement of the two weighted
block-constant modes: each component is supported on the declared core or
tail and has zero weighted block mean.  The square-root-of-`pi` transform is
used only to identify weighted norm with Euclidean norm in this finite matrix.

The tail block has at least two indices and the core block at least two indices
for an eligible row.  Rows without both block-mean-zero subspaces are counted
but are not silently treated as a positive reserve.

## Executed evidence

The primary lane passes `3522/3522` assertions over 858 conditional rows and
114 eligible residual rows.  It retains both outcomes: 24 positive sufficient
reserves and 90 nonpositive sufficient-reserve diagnostics.  The minimum
tail Hardy floor is `0.7542512249663605`, the minimum core gap is
`2.203488739285131`, the maximum cross norm is `362.5494732750524`, and the
safe reserve range is
`[-358.3346630467536, 1.5835608118417415]`.  The minimum actual residual
matrix gap in the eligible finite rows is `2.065902330731274`; this does not
replace the conservative reserve and is not a uniform statement.

The non-importing independent lane passes `43/43` assertions on three
reversible graph fixtures, all with positive safe reserves; its minimum safe
reserve is `0.06027756573732857`.  The hostile lane rejects `7/7` mutations,
including negative inputs, nonfinite cross norm, omitted cross term, forged
upward reserve, and an uncertified tail floor.  The integrated verifier passes
`20/20`, and `lake env lean Tect/R422.lean` passes.

## Lean cross-check

`verification/lean/Tect/R422.lean` proves the scalar budget
`2*abs(x*y) <= x^2+y^2`, the conservative two-block reserve implication, the
nonnegative-reserve condition, and a finite-scope marker.  It does not claim to
formalize the Q3 eigensolver or any limiting construction.

## Adversarial review

1. **Cross-term omission.**  Dropping `eta` would turn a sufficient bound into
   an invalid one.  The hostile lane rejects the omitted-cross candidate;
   disposition: DISMISSED-FINITE.
2. **Reserve sign.**  A negative `lambda_safe` is retained as a failed
   sufficient budget and is never clipped to zero; disposition:
   DISMISSED-FINITE.
3. **Tail-floor inflation.**  A declared `kappa` above the direct tail form
   floor is rejected; disposition: DISMISSED-FINITE.
4. **Nonpositive input.**  Negative core, tail, or cross inputs are rejected
   before the inequality is applied; disposition: DISMISSED-FINITE.
5. **Numerical sharpness.**  The sharper eigenvalue is diagnostic only; the
   certified lane uses the conservative `min(a,kappa)-eta` formula;
   disposition: DISMISSED-FINITE.
6. **Coarse sector leakage.**  The two block-mean coarse modes are excluded
   from this residual calculation and no coarse gap is inferred;
   disposition: UPHELD-OPEN.
7. **Uniform/physical promotion.**  Positive finite rows do not establish a
   cutoff-, volume-, phase- or exhaustion-uniform reserve, a common core, a
   GNS gap, or a Yang-Mills mass gap; disposition: UPHELD-OPEN.

## Boundary and next action

R-422 closes only the finite scalar reserve inequality and the declared Q3
diagnostic.  The 90 nonpositive rows show that the conservative budget is not
uniform on the tested cutoff grid, especially at `(V,d)=(2,12)`; this is a
finite route boundary, not a theorem of physical gaplessness.  The two-
dimensional block-mean coarse Schur sector, Hamiltonian common core, actual
R-399 history transfer, phase selection, OS/KMS/GNS identification, continuum
limit, C6, Sector-A, and Pre-A remain open.

The next unlock is an analytic boundary-capacity estimate that controls
`eta` relative to the core and tail floors on one Q3 common core, followed by
the coarse Schur sector and the R-399/R-415 history transfer.  Until those
inputs are uniform and domain-controlled, no physical or Yang-Mills claim is
permitted.
