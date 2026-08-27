# q3lock-local-q2-fractional-liouvillian-stress-boundary

R-367 is a T0 finite stress for EXP-001209.  It extends the R-366
`theta=1/2` fractional Liouvillian pilot to V=2 cutoffs 3 through 6 and a
V=4 square graph at cutoff 2, using zero/first/full split prefixes.

The stress is designed to decide whether the fractional square-function
route immediately exhibits cutoff or volume growth.  It is not an analytic
uniformity proof.  In particular, arbitrary intermediate prefixes, source
families, exhaustion shapes, common cores, common alpha and the modular
weight comparison remain open.

The primary and independent scripts must be non-importing at the lane level;
the integrated script must compare every stored scalar and compile Lean R367.
Any growth is recorded with its exact regime rather than hidden in a single
diagnostic threshold.

