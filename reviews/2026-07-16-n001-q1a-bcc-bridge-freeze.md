# N-001 q1a BCC-bridge evidence freeze (2026-07-16)

## Decision record

This record freezes the presently available N-001 q1a evidence.  It makes no
decision to continue or stop Sector A.  It creates no claim, tier, theorem, or
Reading-H conclusion.  Its sole purpose is to preserve a restartable and
auditable boundary between the settled evidence and the still-open BCC bridge.

The authoritative entry point is
`reviews/n001-q1a-bcc-bridge-freeze-260716/README.md`.  Its manifest fixes the
input evidence by SHA-256 and its runbook distinguishes a repository-only
integrity check from rerunning the external PDE computation.

## Frozen observations

1. The uploaded N-001 runs contain a nonzero homogeneous condensate candidate.
   At N32, N64, and N128 they record projected residuals near `8.22e-09`,
   free energy `-496.6861610721164`, and nonnegative values in the recorded
   projected Ritz audit.  N64 and N128 are Fourier prolongations which stopped
   at Newton step zero; they are representation-transfer evidence, not three
   independent nonlinear solves.
2. The stored-field structure audit is
   `NONUNIFORM_BUT_NO_Q0_SHELL`: DC power is approximately one and q0-shell and
   BCC power are approximately zero.  Therefore this candidate is not BCC
   evidence.
3. The full N32 commensurate BCC `{110}` star probe evaluated all six
   antipodal pairs.  Its lowest recorded projected curvature is
   `+52.12042392718455`, with no recorded negative or near-zero directions.
   This is an operator-level local stop signal around this homogeneous branch
   at this parameter point.
4. The stored BCC-seed sweep did not retain q0-shell BCC modulation and is
   registered as `R-2026-07-16-N001-BCC-SEED-COLLAPSE`.

## What remains open

The evidence does not decide whether an N-001 BCC-modulated branch exists in a
different parameter regime, box, discretisation, or seed family.  It does not
decide its stability, global selection, or any Reading-H/BCC downstream
conclusion.  Those questions are deliberately left open, rather than converted
into a mandatory next task.

## Resume contract

Do not repeat the frozen N32 run merely to rediscover the same local result.
Resume this thread only for a new, explicitly recorded question: a grid-transfer
audit, a changed parameter/operator regime, or a genuinely BCC-structured
candidate.  Begin with the package runbook; preserve its source hashes; run the
structure audit before using solver convergence or projected Hessian output as
BCC evidence.  A new result must be recorded separately and must not overwrite
this freeze.

## Prohibited shortcuts

- Do not call the homogeneous candidate a BCC condensate.
- Do not call the N32 projected-star result a full-spectrum stability proof.
- Do not infer global minimality, BCC nonexistence, or Reading-H selection.
- Do not use this package to promote any Sector A or Sector B claim.
