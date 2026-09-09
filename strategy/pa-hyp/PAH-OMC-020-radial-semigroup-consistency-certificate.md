# PAH-OMC-020 restricted radial semigroup consistency

## Question and frozen scope

For a bounded gauge- and anchor-invariant cylinder `f` depending only on a
finite set of matter-amplitude coordinates, does the original finite PAH
stationary semigroup converge on compact external Markov-time intervals to
the identity action of the R-512 minimal-form semigroup?

The functional, directed PH/LK/AP/TR rates, mobility, labelled Gibbs state,
OMC-004 strip, normalization, external stochastic time and `j`-before-
anchored-`n` order are exactly those fixed by PAH-001 and the temporal
preregistration.  No root is deleted and no rate, carrier, state or time is
changed.

## Restricted proof

Let `S_nj f` be the original sampling of `f` at `h_j=2^-j` amplitudes.  PH,
LK and AP moves leave matter amplitudes unchanged, so their increments vanish
on `f`.  A TR move changes the amplitude `l1` coordinate by at most `2 h_j`.
For a support with `H_f` active directed roots and finite `l1` Lipschitz
constant `L_f`, the pinned R-511 inverse-pair estimate gives

```text
||L_TR,nj S_nj f||_L2(mu_nj) <= 2 H_f L_f h_j.
```

The complete finite stationary reversible semigroup `P_nj(t)` is an `L2` contraction.  The variation-of-constants identity therefore yields, for every finite `T`,

```text
sup_(0<=t<=T) ||P_nj(t) S_nj f - S_nj f||_L2(mu_nj)
    <= 2 T H_f L_f h_j.
```

For a bounded local cylinder `g`, the corresponding two-point correlation
defect is bounded by `||g||_2 2 T H_f L_f h_j` (or by the analogous bound
with the second observable as the amplitude-only argument).  The bound is
uniform in every stabilized `n>=N(f)` because `H_f` is support-dependent, not
volume-dependent.  It tends to zero as `j` tends to infinity.

R-512 places the amplitude-only subspace `H_rad` in the zero-energy subspace
of the minimal closed form.  By the spectral-semigroup consequence,
`T_min(t)g=g` for `g` in `H_rad`.  Thus the restricted correlation comparison
is exactly uniform on `[0,T]` in the registered order: the `j` limit is zero
at each fixed `n`, and the anchored `n` passage is then trivial for this
subspace.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_radial_semigroup_consistency.py --check
python -X utf8 codes/foundations/pah_omc020_radial_semigroup_consistency_independent.py --check
python -X utf8 codes/foundations/pah_omc020_radial_semigroup_consistency_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_radial_semigroup_consistency_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

The primary lane passes 21/21, the non-importing independent lane 14/14, the
hostile mutation lane 11/11, and the integrated verifier 29/29.  Lean 4.32.1
compiles seven finite rational declarations for the jump, residual,
compact-time, correlation and refinement inequalities.  The Lean file does
not formalize the PAH measure construction or the R-512 spectral theorem.

## Decision and boundary

This is `PASS_RESTRICTED` / `auxiliary_support`.  It closes only the
amplitude-only temporal sector.  It does not provide the non-radial PH/LK/AP
comparison maps, a common `U_n`, N2b liminf/recovery, N2c/N4 boundary escape,
N2d identification, or the full stationary semigroup convergence.

The next question is whether one source-authorized common-space or path-space
packet transfers the non-radial correlations to the same R-512 minimal
semigroup while preserving the radial identity above.  No physical Pre-A,
spacetime, QFT, gravity, continuum, mass-gap, Yang--Mills or TOE conclusion
follows.
