# R-473 HOLD-LC-001 TTE Event-Row Feature Index

## Status

R-473 / EXP-001348 is a claim-nonbearing T0 finite source-feature result for
T-061.  It reads only the two byte-frozen Fermi EVENTS tables and derives a
candidate-neutral detector-frame, one-second trigger-relative histogram.  The
result is an intake artifact, not a physical or statistical conclusion.

## Exact question and scope

The audit asks whether the pinned `TIME` (1D) and `PHA` (1I) rows can be decoded
reproducibly and converted into a deterministic feature index.  The parser
derives the lower and upper bin edges from `floor(TSTART-TRIGTIME)` and
`ceil(TSTOP-TRIGTIME)`, uses left-closed/right-open one-second bins, requires
finite nondecreasing event times in the header interval, and requires PHA in
`[0,127]`.  It reads no response coefficients and performs no geocentre,
time-standard, calibration, likelihood, covariance, nuisance, or candidate
scoring operation.

The two products are the hash-pinned Fermi GBM NaI N0 and BGO B0 TTE files in
the local gitignored HOLD-LC-001 cache.  The decoded tables contain 272,615 and
394,501 rows respectively, for 667,116 rows total, and the common derived
feature range has 263 one-second bins.

## Verification dispositions

- **Primary:** `verification/scripts/hold_lc_001_tte_event_feature_index.py`
  independently checks FITS spans, schema, metadata, monotonicity, PHA range,
  conservation, common edges, and histogram digests.
- **Independent:** `codes/foundations/hold_lc_001_tte_event_feature_index_independent.py`
  uses a separate card scanner and `struct.iter_unpack` implementation.  Its
  canonical feature core must match the primary byte-for-byte at the JSON value
  level.
- **Hostile:** `codes/foundations/hold_lc_001_tte_event_feature_index_hostile.py`
  applies twelve temporary-file or manifest mutations: row order, out-of-range
  and non-finite time, PHA, truncation, byte hash, schema, parent hash,
  candidate score, prospective lock, method-preservation, and physical-scope
  promotion.  Every mutation must be rejected.
- **Lean:** `verification/lean/Tect/R473.lean` proves the one-second positivity,
  half-open-bin disjointness, pinned bin-count and row-total fixtures, and a
  conservation arithmetic fixture.  These are cross-checks of parser arithmetic,
  not a physical theorem.
- **Integrated:** `verification/scripts/hold_lc_001_tte_event_feature_index_verify.py`
  runs the three children, checks exact-core parity and admission firewalls, and
  compiles the pinned Lean entrypoint.

The run JSON files under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-*-hold-lc-tte-event-feature-index/`
are the executable evidence.  Their assertions and SHA-256 provenance are the
authoritative counts for this checkpoint.

## Assumptions and missing assumptions

The byte-freeze manifest remains authoritative; FITS scalar values are decoded
big-endian as declared; `TSCAL/TZERO` and `TRIGTIME` are used only for the
detector-frame feature; and the histogram rule was frozen before any candidate
comparison.  Still missing are source-owned calibration validity, a common
time-standard and detector-to-geocentre map, a fixed detector/energy/background
selection rule, a joint timing likelihood and covariance, an intrinsic-emission
lag nuisance law, complete `F_reg/F_lim/F_eff/F_obs`, and a prospective holdout.

## Adversarial review

1. **Byte substitution:** a changed file could preserve row counts.  The parent
   SHA-256 and byte length are checked before decoding, and a byte-flip mutation
   is rejected.
2. **Layout ambiguity:** a plausible histogram could result from a wrong offset.
   The EVENTS header must declare TIME 1D then PHA 1I, with row width derived
   from all columns; a TFORM mutation is rejected.
3. **Endpoint leakage:** changing a closed/open convention after inspection
   could change counts.  The edge rule is contract-frozen, derived from headers,
   and protected by mutation tests and the Lean half-open fixture.
4. **Statistical overreach:** a descriptive histogram could be called a timing
   likelihood.  All likelihood, covariance, nuisance, and prospective flags are
   false and hostile promotion mutations are rejected.
5. **Method replacement:** a source-feature packet could silently replace the
   established proof program.  The manifest records every preservation flag and
   the audit rejects method or physical-scope promotion.

## Non-claims and boundary

This result does not identify microscopic dynamics, select a candidate, supply a
physical propagation law, close Pre-A, C6, Sector-A, QFT, Yang--Mills, gravity,
continuum, cosmic-origin, theory-of-everything, or mass-gap claims.  It does not
replace the Reading-H physical-empty branch or any T-054 forward step.  The
T-054 forward route, T-059/T-061 observation-first inverse route, owner order,
and promotion firewalls are unchanged.  `HOLD-LC-001` remains retrospective and
`PROS-LOCK-001` remains empty.

## Next action

Keep this feature index frozen as a candidate-neutral `F_reg` intake.  Request
the missing owner, calibration, time-standard, geocentre, statistical and
prospective contracts before any score.  In parallel, continue the unchanged
T-054 source-owned Q3LOCK -> common-core -> uniform-estimate order; do not
re-enter a repeated finite mobility or physical-empty loop.
