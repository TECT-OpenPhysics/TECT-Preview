# R-468 HOLD-LC-001 rsp2 segment index certificate

## Role and method preservation

R-468 is an additive T-061 owner-intake record.  It leaves the established
T-054 forward method, T-059/T-061 observation-first inverse method, owner
order, and promotion firewalls unchanged.  It does not choose a response
segment, fit a candidate, or reinterpret a response history as a timing
likelihood.

## Exact finite scope

The parent byte-freeze manifest identifies two Fermi GBM event-trigger
response histories, one for NaI N0 and one for BGO B0.  The primary and an
independent standard-library parser verify their recorded bytes, inspect the
binary-table row layout, and record only compact metadata:

* one EBOUNDS table per product; all 128 channel energy intervals are read as
  scalar values and checked for finite ordered bounds and monotonicity;
* eight ordered SPECRESP MATRIX segments per product, each with 140 scalar
  energy rows and valid nonempty P-descriptors for `F_CHAN`, `N_CHAN`, and
  `MATRIX` within the declared heap;
* each segment's `RSP_NUM`, `TSTART`, `TSTOP`, center, duration, energy range,
  descriptor counts, and heap bounds.

The variable-array heap is not followed: `F_CHAN`, `N_CHAN`, and all MATRIX
response coefficients remain unread and uninterpreted.  A fixed audit grid of
relative offsets `[-30,-15,0,15,30]` seconds from the FITS `TRIGTIME` is used
only to expose three alternatives:

```text
covering: every segment with TSTART <= query <= TSTOP (zero-duration only at
          its exact endpoint)
nearest:  the segment with minimum absolute distance to its interval center,
          ties resolved by the smaller RSP_NUM
bracket:  adjacent ordered centers around the query, with linear weights
          (c_upper-query)/(c_upper-c_lower) and
          (query-c_lower)/(c_upper-c_lower)
```

All alternatives are retained.  No alternative is marked as a production
selection, and no score is computed.

## Audit result

The primary audit passes 35 structural/selection assertions.  The independent
non-importing parser passes its four core assertions and agrees on the core
digest.  The hostile lane rejects 10/10 mutations, including a byte hash,
segment numbering and overlap, missing alternatives, matrix admission,
candidate scoring, production selection, candidate-dependent query, and
prospective credit.  The integrated verifier passes 10/10 and the Lean
kernel `R468.lean` compiles.

## Assumptions and missing assumptions

The parent manifest is authoritative for product identity, locators and byte
hashes; FITS scalar/table declarations are descriptive; the query grid is a
fixed reproducibility fixture; and all existing methods and firewalls remain
controlling.  Still missing are a source-owned response-validity/interpolation
rule, detector-to-geocenter conversion and uncertainty, frozen event windows,
a joint timing likelihood or covariance with nuisance terms, the complete
`F_reg/F_lim/F_eff/F_obs` map, and a prospective holdout.

## Evidence level, boundary, and next gate

Evidence level is T0 exact public-product byte verification plus finite
binary-table structure and selection-ambiguity metadata.  It does not admit a
calibration law, timing uncertainty, likelihood, covariance, nuisance model,
candidate, prediction, microscopic dynamics, causal propagation, physical
sector, Pre-A, QFT, Yang--Mills, gravity, continuum, or mass gap.  The next
gate is an owner-supplied validity/interpolation and timing-uncertainty
contract; until then the response alternatives and all scoring remain locked.

## Adversarial review

* **Byte provenance:** a changed hash or length is rejected against the parent
  manifest.
* **Table geometry:** wrong row widths, channel ordering, nonmonotone energies,
  segment numbering, overlap, or descriptor heap bounds are rejected.
* **Heap leakage:** setting matrix coefficients to read or interpreting the
  heap is rejected; only descriptors are inspected.
* **Boundary semantics:** removing the covering/bracket alternative or changing
  query offsets is rejected; endpoint rules remain explicit.
* **Interpolation arithmetic:** negative/out-of-range weights or a non-unit
  weight sum are rejected by the Lean and runtime checks.
* **Selection leakage:** replacing `NONE_SELECTED` with a nearest/covering
  choice or enabling a candidate score is rejected.
* **Prospective leakage:** marking the empty prospective lock admitted is
  rejected.
* **Physical overreach:** the owner and physical map remain unadmitted; a
  finite response index cannot promote T-061 or any Pre-A/QFT/Yang--Mills
  claim.
