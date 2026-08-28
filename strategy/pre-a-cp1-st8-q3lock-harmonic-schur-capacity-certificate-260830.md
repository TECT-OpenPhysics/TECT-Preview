# R-406 certificate - harmonic-extension Schur capacity decomposition

## Scope

R-406 is a T0, claim-nonbearing finite checkpoint under EXP-001251.  It
continues R-405 but replaces the unsafe block-constant shortcut by a
Dirichlet-principle construction.  For each conditional momentum graph, the
weighted operator is

```
A = diag(pi)^(-1/2) L diag(pi)^(-1/2),
```

where `L` is the symmetric conductance Laplacian.  The weighted block
constant subspace `U` contains the lower, neutral (when present), and upper
q-coordinate sectors; `V` is its Euclidean orthogonal complement.

## Finite construction

For fixed block coordinates `z`, the unique block-mean-zero minimizer is

```
w_h = - A_VV^(-1) A_VU z.
```

The Schur operator is

```
S = A_UU - A_UV A_VV^(-1) A_VU.
```

Its generalized first positive eigenvalue, using the norm of the harmonic
extension rather than the norm of the coarse coordinates alone, is
`kappa_coarse`.  The least eigenvalue of `A_VV` is `kappa_residual`.
Energy orthogonality is exact up to floating-point residuals.  Because the
harmonic and residual vectors need not be orthogonal in the variance norm,
the finite lower envelope used by the audit is the safe triangle estimate

```
E(f) >= (1/2) min(kappa_coarse, kappa_residual) Var_pi(f).
```

No equality of coarse and residual variances is asserted.

## Finite verification

The primary lane covers eight finite Q3 Gibbs systems: volume two with
dimensions `4,5,6,8,10,12`, and volume three with dimensions `4,5`; beta is
`{1/2,1,2,4,8}`, both collar orientations are used, and every prefix
conditional row is retained.  The primary passes `4267/4267` assertions over
`1030` rows and `80` profiles.  The non-importing independent lane passes
`2114/2114`, the hostile lane passes `6/6`, the integrated verifier passes
`38/38`, and Lean R406 compiles.

The aggregate finite ranges are:

| quantity | minimum | maximum |
|---|---:|---:|
| full intrinsic gap | 0.6310329497027756 | 6.229495058532403 |
| harmonic Schur coarse gap | 0.634590321876555 | 18.727067154255124 |
| block-mean-zero residual gap | 2.0000155411351734 | 30.07649788337455 |
| safe corrected lower envelope | 0.3172951609382775 | 3.232260013170645 |
| naive block-constant Ritz gap | 0.859366031221583 | 35.521614497313294 |

All `1030` rows have a strict naive-Ritz-over-full separation.  The hostile
representative `(V=2,d=12,beta=8)` has full gap `3.38789`, corrected envelope
`1.77408`, and a naive false-lower-bound margin `1.09327`; deleting every
inter-block edge exposes two zero modes, while replacing momentum by diagonal
q gives zero edges.

## Adversarial review

1. **Weighted block basis.**  Each block column is normalized by its
   conditional mass and the Gram matrix is checked before the complement is
   formed.
2. **Schur invertibility.**  The residual block is required to have a
   strictly positive spectrum; a disconnected graph fails rather than being
   pseudo-inverted silently.
3. **Harmonic correction.**  The primary checks the energy residual of
   `f=h+g` and the lower-bound margin on deterministic centered probes for
   every conditional row.
4. **Variance norm.**  The harmonic and residual pieces are not assumed
   variance-orthogonal.  The factor `1/2` triangle envelope is explicit, so a
   Schur eigenvalue is not misreported as a full variance gap.
5. **Naive shortcut.**  The uncorrected block-constant Ritz value is retained
   only as an upper restriction diagnostic; the Fiedler vector gives a
   concrete finite violation of the corresponding lower-bound claim.
6. **Connectivity mutations.**  Removing all inter-block edges exposes one
   zero mode per block, and the diagonal-q mutation produces no kinetic edges.
7. **Physical boundary.**  All checks are finite conditional Gibbs checks.
   No source/volume/cutoff/exhaustion uniformity, common core, common alpha,
   phase selection, OS/KMS/GNS reconstruction, mass gap, continuum, C6,
   Sector-A or Pre-A conclusion follows.

## Decision and next gate

R-406 advances a corrected finite interface.  It shows how to separate a
coarse phase-capacity mode from block-mean-zero fluctuations without treating
a restricted Ritz eigenvalue as a lower bound.  The next analytic target is
to prove uniform lower bounds for the Schur coarse operator and residual form
on one Hamiltonian common core, then identify the coarse variables with a
controlled phase boundary condition and transfer the centered split to the
R-399 shell.

The finite corrected envelope is not a thermodynamic constant.  If either
Schur or residual gap collapses along a validated cutoff/volume sequence, the
route remains diagnostic only.

## Boundary

No cutoff-independent or volume-independent sector gap, phase-selection
theorem, common core, common alpha, Hamiltonian-to-OS/KMS identification,
broken-sector GNS gap, continuum, C6, Sector-A or Pre-A result is claimed.

Proven in the manifest, primary/independent/hostile scripts, integrated
verifier, Lean entrypoint, scope note and saved run artefacts.
