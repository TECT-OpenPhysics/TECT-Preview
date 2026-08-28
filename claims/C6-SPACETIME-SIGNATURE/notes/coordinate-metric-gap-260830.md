# R-401 — Physical-coordinate metric for the conditional gap

R-401 adds a new perspective to the R-399/R-400 lane: use the oscillator's
physical coordinate eigenvalue spacing rather than the truncation-level index
as the one-dimensional edge metric.  On the same 32-system grid it computes
the index and coordinate conditional gaps for every prefix and both
orientations.  Primary passes 647/647, independent 647/647, hostile 3/3,
integrated 38/38, and Lean R401 compiles.

The worst finite index gap is `0.03136900665147795`, while the worst finite
coordinate-metric gap is `0.14052591590289856`.  At the selected high-cutoff
stress (`V=2,d=28,beta=2`) the coordinate gap is `0.3796020226627595` versus
index gap `0.06614420831951735`.  Low-cutoff profiles can have a coordinate /
index gain below one (`0.6666666666666661`), so this is a route diagnostic,
not a pointwise domination claim.

The missing theorem is an analytic comparison of this coordinate form with
the actual Q3 likelihood gradient and a phase-conditioned uniform bound.  No
common core, common alpha, OS/KMS/GNS reconstruction, mass gap, continuum,
C6, Sector-A or Pre-A closure follows.

**Authority:** [certificate](../../strategy/pre-a-cp1-st8-q3lock-coordinate-metric-gap-certificate-260830.md),
[primary run](../runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_coordinate_metric_gap/primary.json),
[integrated run](../runs/2026-08-30-integrated-pre_a_cp1_st8_q3lock_coordinate_metric_gap/integrated.json),
and [Lean R401](../../verification/lean/Tect/R401.lean).
