# PAH-OMC-030 finite-strip dynamics to the unique Markov extension

## Frozen question and source contract

This is one bounded temporal attempt for the unchanged PAH-001 model. The
source pins and scope are in `PAH-OMC-030-prereg-v1.json`. R-514 supplies the
fixed-`n` correlation passage

`lim_(K->infinity) lim_(j->infinity) sup_(t<=T) |C_(n,j)(f,g;t)-<f,Q_n(t)g>_(nu_n)|=0`.

R-510 supplies local stationary-state convergence with the terminal unsplit
square retained. R-511 supplies the original local pre-form on `D`. R-568 says
that any symmetric Markov semigroup already acting on the same
`H=L2(mu)` and extending the same `A` on all `D` must equal `T_min`.

The requested anchored statement needs, after the fixed-`n` passage, a
comparison of `Q_n` with `T_min` in one Hilbert space. The cylinder pullback
used by R-510 is valid for fixed local observables, but it is explicitly not a
bounded or isometric map on the completed finite `L2(nu_n)` spaces.

## Exact comparison decomposition

For a legitimate common-space map `U_n`, the missing second term would have to
be controlled by

`|<f,U_n Q_n(t) U_n^* g>_mu - <f,T_min(t)g>_mu|`.

R-568 can identify this term only after existence of a subsequential or full
limit semigroup on `H` whose generator extends `A` on all `D`. It does not
construct `U_n`, a subsequence, a resolvent limit, a Mosco limit, or an
anchored temporal process.

## Boundary and amplitude estimates actually available

The R-514 compact Duhamel estimate is

`2 T H_(n,K,g) L_(n,K,T,g) h_j`.

Both constants are finite only for fixed `n` and compact amplitude cutoff `K`.
The source certificate does not provide a bound uniform in `n` after `K` is
removed. R-514 therefore cannot be re-used as the `n`-uniform N2c/N4 estimate.
R-510 supplies fixed-`n` stationary tails; R-568 supplies a tail and factorial
boundary estimate for the already constructed target `H`, not for the family
of finite `nu_n` spaces. These are different estimates and neither implies
the other.

The terminal-square audit also remains decisive: the finite strip retains an
unsplit terminal `S` factor, while the infinite transfer prefix uses split
`K` cells and an additional diagonal invisible to a fixed local cylinder. A
full-space Radon--Nikodym/bounded-energy realization compatible with both is
not present in the pinned inputs.

## Verdict

`HOLD_FOR_EVIDENCE`.

This is not a PAH counterexample. The fixed-`n` passage is source-compatible
and the R-568 uniqueness theorem is source-compatible, but the comparison
quantity is not yet defined on one completed Hilbert space with the required
uniform boundary control. The single missing proposition is:

> There exists a source-authorized family `U_n` compatible with the retained
> terminal square such that local cylinder pullbacks extend with a uniform
> bounded-energy estimate, the associated forms satisfy arbitrary-sequence
> liminf and recovery, and the original unbounded rates obey compact-time
> N2c/N4 boundary escape.

Re-entry requires a changed, hash-pinned source packet proving this proposition
or an exact PAH counterexample to one of its clauses. Do not re-run fixed-n
tables, static-state checks or R-568 uniqueness as substitutes.

## Verification boundary

Primary and hostile compatibility audits are executable. The independent audit
reconstructs the source hashes and the missing-bridge logic without importing
the primary verifier. Existing R-514 and R-568 Lean declarations remain useful
for finite algebra and fixed-target uniqueness. No Lean theorem in this attempt
formalizes `U_n`, Mosco liminf/recovery, the unbounded finite-rate boundary
escape, or the anchored limit. External Markov time remains stochastic.

No physical Pre-A, Sector-A, spacetime, QFT, gravity, continuum,
Yang--Mills, mass-gap or TOE claim follows.
