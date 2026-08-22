# R-192 / T-058 bounded complete finite production-cylinder trial

## 1. Contract

R-192 is a T0, claim-nonbearing integration audit.  It freezes the A1
side-16 two-root chart (`k`, `2k`, `L=16`, `V=4096`) and requires one owner
slot for heat/root incidence, covariance bases, complement, historical low,
forest, returned mean, source, and sextic.  A slot is never treated as zero
merely because an earlier endpoint identity set it to zero.

The finite prerequisites are imported by hash from R-176, R-177, R-178,
R-183, R-184, R-125, R-136, R-150, and R-191.  The Lean entrypoint is
`verification/lean/Tect/R192.lean`; the primary lane uses the pinned Lean
toolchain and exact `Fraction` arithmetic, while the independent lane is
stdlib-only and rederives the ledger and fixtures without importing the
primary lane.

## 2. Exact finite checks

Lean proves the R-183 reserve threshold fixture at cross scale `a=8`: the
isotropic diagonal `d=16` is nonnegative, while `d=15` has the exact witness
value `-2`.  Lean also proves the R-184 two-block Douglas identity and its
registered gap `676`, and imports the R-191 exact endpoint telescope.  These
checks are prerequisites only; none is silently promoted to a production
bound.

The owner-slot order is fixed as

`heat_root_incidence -> covariance_bases -> complement -> historical_low -> forest -> returned_mean -> source -> sextic`.

The first slot is not complete.  R-177 supplies the finite structural order
and feedback coefficient, but explicitly does not supply the production
raw-current spatial map or q-ledger.  R-136 independently records the same
production one-use q-ledger as unproved.  Therefore the trial verdict is
`FAIL_FIRST_MISSING_PRODUCTION_MAP` (first missing production map); the later slots are not evaluated as if
they were zero.

## 3. Adversarial review

1. **Structural ledger promoted to production map:** UPHELD against the
   promotion.  R-177's boundary is explicit.
2. **Endpoint complement promoted to full-cylinder complement:** UPHELD
   against the promotion.  R-150 is an absolute final endpoint only.
3. **Historical low silently discarded:** UPHELD against the discard.  R-125
   and R-150 leave the complete low owner open.
4. **Reserve threshold weakened:** UPHELD against replacing `d=15` by zero;
   the Lean witness is exactly `-2`.
5. **Temporal overlap inferred from a scalar identity:** UPHELD against the
   inference.  R-184 is only a two-block contraction fixture.
6. **Finite endpoint telescope promoted to A13/T-050:** UPHELD against the
   promotion.  R-191 explicitly retains negative intermediate stages and the
   missing production q-ledger.

## 4. Boundary and next proof obligation

This is a reproducible finite integration failure, not a new negative result
and not a counterexample to the complete production action.  This trial does not close A13;
no A13 gate,
T-050, OVERLAP_src, Nelson, measure, Sector-A, Pre-A, physical-empty,
removal, continuum, tier, or phase conclusion follows.  The next proof
obligation is concrete: provide the actual production heat/root raw-current
map and once-owned nonnegative q-ledger on this same cylinder, then rerun the
unchanged owner order and only afterward apply the R-183 reserve to mapped
diagonal owners.

No R-192 PDF is issued.
