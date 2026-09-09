# PAH-OMC-020 Mosco variational resolvent bridge checkpoint

## Decision

`HOLD_FOR_EVIDENCE` / `auxiliary_support` for T-080.  This checkpoint closes
the conditional variational selection implication and leaves the parent
PAH-OMC-020 temporal gate unchanged.

## Exact question

For the unchanged PAH-001 finite reversible forms, can a source-authorized
common comparison `U_n` identify the anchored resolvent minimizers with the
R-512 minimal-form resolvent in the registered order `j -> infinity` first,
then anchored `n`?

## Conditional variational bridge

For fixed `lambda > 0`, let

`J_n(u) = E_n(u) + lambda ||u - U_n f_n||^2`

and

`J(u) = E_min(u) + lambda ||u - f||^2`,

where `E_min` is exactly the R-512 minimal closed nonnegative form.  If one
common Hilbert space and comparison maps provide equicoercive minimizers,
the arbitrary-sequence anchored liminf inequality, recovery sequences for
every local target vector, and strong data recovery, then every weak cluster
point of a minimizer of `J_n` minimizes `J`.  Since the terminal square is
strictly convex for `lambda > 0`, that minimizer is the unique
`R_min^lambda f`.  A source-authorized norm-upgrade argument would then yield
strong resolvent convergence.

The semigroup or compact-time correlation conclusion is deliberately a
separate bridge.  The variational implication does not identify a process,
does not replace the Duhamel residual in R-537, and does not import a generic
Mosco theorem whose hypotheses are not present in the source packet.

## Fixed scope and provenance

- PAH-001 `F_rho`, original directed PH/LK/AP/TR rates, labelled Gibbs state,
  OMC-010 regulator path and OMC-004 strip are unchanged.
- The registered order is `j -> infinity` at fixed `n`, followed by anchored
  `n`; no diagonal, reversed or joint limit is used.
- `U_n`, the common Hilbert space and all liminf/recovery/norm estimates are
  source-authorized antecedents only; this checkpoint constructs none of
  them.
- The resolvent parameter is static and the time variable remains external
  stochastic Markov time.  No quantum, proper or Lorentzian interpretation is
  introduced.

## Evidence and hostile boundary

The exact rational diagnostic uses `lambda=1`, `k_limit=2`,
`k_values=(3, 5/2, 9/4)` and `f=3`.  It gives target minimizer `1`, sequence
minimizers `(3/4, 6/7, 12/13)`, and strictly decreasing errors.  This is an
algebraic test oracle only, not a PAH estimate or an infinite-volume result.

Primary replay passes `47/47`, the non-importing independent replay `33/33`,
the hostile replay `25/25`, and the integrated replay `23/23`.  Lean 4.32.1
compiles the six finite declarations registered for this checkpoint.
The hostile lane rejects liminf-only, recovery-only, weak-only, named-target,
semigroup-shortcut and displaced-minimizer arguments.

## Missing owner fields

The pinned corpus currently supplies only the exact target-form uniqueness
field.  The following seven fields remain false:

1. common-space equicoercivity;
2. arbitrary-sequence anchored liminf;
3. all-local recovery sequence;
4. strong data recovery preserving the stationary normalization;
5. target exactness beyond the inherited R-512 form (the only currently true
   field is the inherited target uniqueness marker);
6. a source-authorized weak-to-strong norm upgrade;
7. a separate resolvent-to-compact-time-correlation semigroup bridge.

Accordingly the resolvent limit, the PAH-OMC-020 `D_n` defect limit and the
parent semigroup convergence remain unproved.

## Reproduction

```
python -X utf8 verification/scripts/pah_omc020_mosco_resolvent.py --check
python -X utf8 codes/foundations/pah_omc020_mosco_resolvent_independent.py --check
python -X utf8 codes/foundations/pah_omc020_mosco_resolvent_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_mosco_resolvent_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

## Remaining gate and next question

The parent PAH-OMC-020 objective remains `HOLD_FOR_EVIDENCE`.  Reopen only
when a source-authorized N2b/form packet versions and hash-pins the common
`H`, `U_n`, arbitrary-sequence liminf, all-local recovery and norm-upgrade
fields together with the separate semigroup bridge, or when an exact
PAH-specific liminf/recovery contradiction is found.  Do not repeat finite
carrier, physical-empty, BCC or Reading-H calculations.

The single next question is:

> Can a source-authorized N2b packet supply the common `U_n/H` space,
> arbitrary-sequence liminf, all-local recovery and norm upgrade needed to
> identify the R-512 resolvent, without changing PAH-001?

No physical Pre-A, spacetime, event horizon, QFT, gravity, continuum,
mass-gap, Yang--Mills or TOE conclusion follows.
