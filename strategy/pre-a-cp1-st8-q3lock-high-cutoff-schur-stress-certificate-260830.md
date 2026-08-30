# R-426 -- High-cutoff finite harmonic coarse-Schur stress

## Decision

R-426 / EXP-001271 is a T0, claim-nonbearing high-cutoff stress test of the
R-425 harmonic coarse-Schur construction.  The R-419 conditional law, the
R-416 log-domain Gibbs rows, the R-422 block-mean-zero residual split, the
`alpha=1/40` tail rule, `theta=4`, the beta grid `{1/2,2,8}`, both history
orientations, and the declared comparison tolerance `5e-7` were held fixed.
The only extension was the volume-two cutoff sample
`d={14,16,18,20,24,28,30,32}`.

The lane does not pass as a positive finite closure.  It stops at the first
declared residual-reuse disagreement:

```text
volume             V = 2
cutoff             d = 16
beta               8
orientation        right
conditional row    7
core/tail sizes    7 / 9
R-422 residual     5.363184967163699
direct residual    5.363188350047810
absolute gap       3.382884111502449e-06
fixed tolerance    5.000000000000000e-07
```

The mismatch is larger than the preregistered tolerance by a factor of about
6.77.  The tolerance was not relaxed, no values were clipped, and no positive
Schur envelope was promoted beyond the route-local failure.  The exact
finite values are retained as a diagnostic for repairing the basis/precision
convention; this is not a physical no-go result.

## Executed evidence

The primary lane evaluates the fixed grid until the declared failing row and
records `1175` assertions before stopping.  It writes verdict
`FAIL_ROUTE_LOCAL` with the exact failure contract above.  The independent
non-importing lane passes `28/28` reversible Schur-fixture checks and records
`FAIL_ROUTE_LOCAL_EXPECTED`; it is an algebraic control and does not pretend
to reconstruct the high-cutoff Q3 Gibbs grid.  The hostile lane rejects
`7/7` input, support, envelope and singular-graph mutations.  The integrated
verifier passes `15/15` checks and Lean R426 compiles.

The Lean file proves only the finite cutoff ordering, the scalar
`min(a,b)` lower-envelope inequality, and positivity of the declared scalar
inputs.  It does not formalize the numerical matrix spectra or any limit.

## Adversarial review

1. **Tolerance relaxation.**  Replacing `5e-7` by a larger threshold would
   hide the declared failure; disposition: **UPHELD-OPEN**.  The exact
   tolerance remains in the manifest and failure payload.
2. **Basis/precision mismatch.**  The direct residual is recomputed from a
   separately constructed block-mean-zero basis; a high-cutoff convention or
   conditioning issue may explain the disagreement, but no repair is assumed;
   disposition: **UPHELD-OPEN**.
3. **Orientation and row selection.**  The failure is tied to the first
   reproducible `right` row at `(V,d,beta)=(2,16,8)`; the row index, core size
   and tail size are recorded, and the `left` orientation is not substituted;
   disposition: **UPHELD-OPEN**.
4. **Clipping or forged positivity.**  No clipping, upward rounding or
   forged envelope is used; disposition: **DISMISSED-FINITE**.
5. **Finite-to-uniform promotion.**  A finite failure cannot establish a
   cutoff-uniform no-go or a physical gap statement; disposition:
   **UPHELD-OPEN**.
6. **QFT/physical promotion.**  The route-local numerical mismatch is not a
   Hamiltonian, OS/KMS/GNS, sector, Yang--Mills or mass-gap conclusion;
   disposition: **UPHELD-OPEN**.

## Assumptions and missing assumptions

Assumptions used:

- the hash-pinned R-419, R-416, R-422 and R-425 manifests are the intended
  parent inputs;
- conditional weights are positive and normalized, and projected
  conductances are finite, symmetric and nonnegative;
- beta, orientation, alpha, tail threshold, probability floor, gap floor and
  comparison tolerance are fixed for the entire declared stress;
- a residual block is only admitted when its core and tail each have at least
  two coordinates;
- the comparison threshold is an audit threshold, not a license to alter the
  computed values.

Missing for any promotion are a cutoff/volume/phase/exhaustion-uniform
analytic bound on one unbounded common core, a reconciled high-cutoff residual
basis/precision convention, a common split-limit map, history transfer,
Hamiltonian-to-OS/KMS/GNS identification, physical-sector projection, and a
sectorwise coercive theorem.

## Boundary and next action

R-426 records a route-local finite construction failure.  It does not close
the Q3LOCK broken-sector, higher-moment, common-alpha, C6, Sector-A or Pre-A
gates, and it adds no negative-result authority, tier change or PDF.  The next
action is to reconcile the R-422 and direct residual representations at high
cutoff under an explicit precision/basis contract, rerun with the unchanged
`5e-7` tolerance, and only then revisit an analytic common-core estimate.

Evidence level: `T0 / executed finite stress with an exact route-local
residual-reuse failure`.

No cutoff-, volume-, phase- or exhaustion-uniform bound, continuum result,
physical-sector result, Yang--Mills result, or mass-gap result is claimed.
