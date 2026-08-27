# Q3LOCK local Q2 Kubo-Mori translation and shape boundary

R-369 stress-tests the R-368 local Kubo-Mori fractional topology against bond
and source translations.  The actual-Q3 edge uses both sites at cutoffs
3,4,5,6; the square uses all four sites and all four bond terms at cutoff 2.
All split prefix positions, orientations, signs, adjoints and beta values are
retained.

Both executable lanes pass 8601/8601 assertions over 2816 contexts; the
integrated verifier passes 104/104 and Lean R369 compiles.  The maximum
weighted fractional norm is 1.208758407679001, with finite-time bound
0.4029194692263337 and change-to-bound ratio 0.3868613066541026.  The edge
cutoff maxima are 0.0896064105, 0.2005166806, 0.3423910272 and 1.2087584077
for d=3 through d=6.  The square bond maxima are all about 3.2--3.5e-08.

The finite square variation is a useful position-stability diagnostic, while
the edge cutoff growth keeps the analytic uniformity gate open.  The weight
is a doubled local bond Gibbs proxy and is not a global KMS state.  No
source/shape/cutoff/volume-uniform comparison, common core, common alpha,
OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A or Pre-A closure
follows.

