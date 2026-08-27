# R-364 finite bond-spectral pinching certificate

Date: 2026-08-27  
Exploration: EXP-001206  
Task: T-054  
Host claim: C6-SPACETIME-SIGNATURE  
Status: T0 claim-nonbearing finite exact refinement; no parent gate closes

## 1. Question

R-363 removes the coordinate-diagonal component of the moved doubled collision
witness. A bond has a larger commutant than the coordinate diagonal algebra
when its energy is degenerate. The question is whether pinching directly onto
that spectral commutant removes more shell without changing the exact bound.

## 2. Spectral pinching theorem

Let a finite Hermitian bond generator have spectral decomposition
`B=sum_lambda lambda P_lambda`. Define

```text
E_B(X) = sum_lambda P_lambda X P_lambda,
X_0   = X - Tr(omega X) I,
X_perp= X_0 - E_B(X_0).
```

`E_B` is the unital completely positive trace-preserving pinching onto the
bond commutant. Since `B E_B(X_0)=E_B(X_0) B`, and scalar centers commute,

```text
[B,X] = [B,X_perp].
```

The same two-sided weighted Hilbert--Schmidt Cauchy argument as R-363 gives

```text
|Tr(omega [B,X])|
  <= ||B||_omega (||omega^(1/2) X_perp||_HS
                  + ||X_perp omega^(1/2)||_HS),
```

with constant one and without assuming `[omega,B]=0`. When coordinate pinching
is also in the bond commutant, `E_B` is the Hilbert--Schmidt orthogonal
projection onto a larger block algebra, so its unweighted residual is no larger
than the coordinate-pinched residual. This comparison does not assert weighted
norm monotonicity.

## 3. Finite Q3 verification

The primary and independent lanes use the R-362 `V=2`, cutoff `3,4` fixture,
both beta values, both local sites, both split orientations, both time signs,
every prefix and both history adjoints. Each constructs the bond spectral
groups, the moved R-362 collision witness, the centered spectral residual, the
coordinate residual, and the state-weighted Cauchy bound.

Results:

- primary `777/777` and independent `776/776` assertions pass;
- both lanes cover `256` identical contexts;
- the bond has `6` to `15` spectral groups across the two cutoffs;
- maximum spectral reduction error is `1.713e-13` (independent
  `1.711e-13`), and maximum residual commutator is `1.715e-13`;
- maximum scalar-centering error is `8.489e-15`;
- maximum state-weighted bound violation is `-1.069e-14`;
- maximum spectral off-diagonal Frobenius norm is `2.092958`, while the
  maximum coordinate residual is `2.093142`;
- the largest spectral/coordinate weighted-residual ratio on this fixture is
  `0.999917`; the spectral residual remains nonzero with minimum `0.503109`;
- integrated verification passes `51/51`, Lean R364 compiles, and the largest
  primary/independent compared-field difference is `2.220e-15`.

## 4. Adversarial review

1. **Degenerate-spectrum objection — DISMISSED.** The construction uses spectral
   blocks, not individual eigenvectors; equal bond energies are retained inside
   one block.
2. **Reference-commutation objection — DISMISSED.** The trace bound factors
   left and right separately and never moves `omega` through `B`.
3. **Projection optimality objection — VALID WITH SCOPE.** Spectral pinching is
   Hilbert--Schmidt orthogonal and hence minimizes the unweighted residual among
   bond-commuting blocks; no weighted-norm minimization is claimed.
4. **Numerical grouping objection — VALID WITH MITIGATION.** The fixture uses a
   declared `1e-9` spectral grouping tolerance and checks residual commutators
   at roundoff. Exact degeneracy and asymptotic gaps still require an analytic
   owner.
5. **Uniformity objection — UPHELD-OPEN.** Cutoffs `3,4` and `V=2` do not give
   source-, volume-, cutoff-, prefix- or shape-uniform weighted norms.
6. **QFT promotion objection — UPHELD-OPEN.** No finite-time collar, common
   alpha, OS/KMS/GNS reconstruction, mass gap, continuum, C6, Sector-A or
   Pre-A closure follows.

## 5. Boundary and next gate

R-364 is a finite refinement of FI-2b. The next proof target is a bound on the
spectral off-block weighted norm that is uniform under cutoff, volume, source,
prefix and exhaustion shape, preferably through a modular or Lieb--Robinson
estimate. If the spectral residual grows, record the exact growth law rather
than promoting this finite reduction.

No R-364 PDF is issued.
