# R-469 HOLD-LC-001 GDT Rsp2 selection-owner crosswalk

R-469 is an additive T-061 provenance result. It preserves the established
T-054 forward method, the T-059/T-061 observation-first inverse method, owner
order, and promotion firewalls. It does not replace or redesign any research
method.

## Exact source pin

The audited public implementation is `USRA-STI/gdt-core`, commit
`ad506a4a45016bda720ff8d722e9ada49fd32191`, file
`src/gdt/core/response.py`, SHA-256
`2a5581e8a0b68a5b0eeaa513ec479fef3e6735b04125968ba9f58f89d3e45833`,
25574 bytes. The source locator and line ranges are recorded in the JSON
contract. The local copy is gitignored under the HOLD-LC-001 source cache.

## What the implementation actually says

`Rsp2.drm_index` uses strict interval overlap
`(tstop > start) and (tstart < stop)`, returns all matching indices in stored
order, and clamps an empty query to the first or last segment. `nearest_drm`
delegates to the first index of `drm_index((atime, atime))`; despite its
docstring, the implementation does not compute an absolute-distance-to-center
argmin. At an exact adjacent-segment endpoint, strict inequalities can produce
no match and therefore the last-segment fallback. `interpolate` and `weighted`
read response matrices and are therefore not executed by this audit.

The crosswalk reproduces these semantics from R-468 interval metadata only.
It records the difference from R-468's candidate-neutral closed-covering and
center-distance alternatives, but leaves `production_selection=NONE_SELECTED`.
The two products' interior audit offsets remain segment-consistent; endpoint
and overlapping synthetic probes expose the implementation boundary behavior.

## Evidence and adversarial review

The primary and independent lanes verify the source/file pin, parent R-468 SHA,
two products and sixteen finite segments, exact strict-overlap fallback,
the docstring/implementation mismatch fixture, and the no-matrix/no-score
firewall. The hostile lane mutates source identity, interval rule, nearest
semantics, boundary record, matrix admission, production selection, methods,
and prospective status; every mutation is rejected. Lean R469 checks the strict
overlap boundary, fallback split, and first-index delegation.

This is T0 finite source-semantic evidence only. It does not admit calibration
validity, interpolation policy, detector-to-geocenter timing, uncertainty,
likelihood, covariance, nuisance, a complete inverse map, scoring, a holdout,
or any physical/QFT/Yang--Mills/continuum/mass-gap claim. The next gate remains
an owner-supplied validity/interpolation and timing-uncertainty contract.
