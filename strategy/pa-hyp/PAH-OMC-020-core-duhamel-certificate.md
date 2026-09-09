# PAH-OMC-020 common-core Duhamel transfer checkpoint

## Decision

`HOLD_FOR_EVIDENCE` / `auxiliary_support` for T-079.  This checkpoint closes
one conditional analytic transfer contract and leaves the parent temporal gate
unchanged.

## Exact question

What source-authorized common-core data are sufficient to make the anchored
PAH-OMC-020 correlation defect

`D_n(f,g;T) = sup_{0<=t<=T} |c_n(f,g;t) - <f,T_min(t)g>_H|`

vanish, where `T_min` is the exact R-512 minimal-form semigroup?

## Conditional transfer

Let `U_n` transport the fixed-n limiting correlation vectors into one Hilbert
space `H`.  For a local `g`, set

`u_n^g(s) = U_n P_n^infty(s) v_n(g)`,

and require an invariant cylinder core on which

`r_n^g(s) = d u_n^g(s)/ds + K_min u_n^g(s)`

is Bochner integrable.  If `T_min` is contractive and the source packet gives

`I_n(h) = ||U_n v_n(h)-h|| -> 0`,

`R_n(g;T) = integral_0^T ||r_n^g(s)|| ds -> 0`,

then the variation-of-constants identity gives

`sup_t ||u_n^g(t)-T_min(t)g|| <= I_n(g)+R_n(g;T)`.

With the original stationary correlation identity and
`N_f = sup_n ||U_n v_n(f)|| < infinity`,

`D_n(f,g;T) <= N_f [I_n(g)+R_n(g;T)] + I_n(f)||g||`.

This is an exact sufficient implication, not an assertion that the required
objects exist.

## Fixed scope and provenance

- PAH-001 `F_rho`, original directed PH/LK/AP/TR rates, labelled Gibbs state,
  OMC-010 regulator path, and OMC-004 relational strip are unchanged.
- The registered order is `j -> infinity` at fixed `n`, followed by anchored
  `n`; no diagonal or reversed limit is used.
- `T_min` is the R-512 minimal closed-form target only.  No maximal extension,
  phasewise direct sum, or new process is introduced.
- Time is external stochastic Markov time only.
- The current source status has `target_contraction=true` and all five other
  owner fields false: common space/core, correlation identity, initial recovery,
  residual domain, and uniform residual estimate.

## Diagnostics and hostile boundary

The rational test oracle computes
`(3/2)[1/32+1/128]+(1/64)2 = 23/256`.
It is labelled test arithmetic, not a PAH estimate.  Independent and hostile
replays show that removing either the initial or residual term produces a
strictly smaller unsound envelope.  A named R-512 target or a static L2
contraction cannot fill the missing dynamic fields.

## Reproduction

```
python -X utf8 verification/scripts/pah_omc020_core_duhamel.py --check
python -X utf8 codes/foundations/pah_omc020_core_duhamel_independent.py --check
python -X utf8 codes/foundations/pah_omc020_core_duhamel_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_core_duhamel_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Primary replay passes `51/51`, independent `33/33`, hostile `19/19`, and
integrated `22/22`.  Lean 4.32.1 compiles eight finite declarations in
`verification/lean/Tect/PahOmc020CoreDuhamel.lean`.

## Remaining gate and next question

The parent PAH-OMC-020 objective remains `HOLD_FOR_EVIDENCE`.  The single next
question is whether a source-authorized packet can provide `U_n`, the common
invariant cylinder core, the original correlation identity, and a vanishing
anchored-n residual `R_n(g;T)` for the exact PAH-001 semigroup.  Reopen only
after those fields are versioned and hash-pinned or an exact PAH-specific
residual contradiction is found.

No physical Pre-A, spacetime, event horizon, QFT, gravity, continuum,
mass-gap, Yang--Mills or TOE conclusion follows.
