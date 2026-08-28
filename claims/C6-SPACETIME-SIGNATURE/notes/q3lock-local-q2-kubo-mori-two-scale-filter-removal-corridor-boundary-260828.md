# R-384 two-scale filter-removal corridor boundary

R-384 applies a two-scale split to the R-383 reference filter on the same
2,816 finite actual-Q3 histories.  For `u=|E_i-E_j|`, `Y_1,ij=X_ij/(1+u)`.
The exact `M_0` removal is bounded for each transition energy `E` by
`E^2 M0_{u<=E}+E^(-2) M2_{u>E}`.  The endpoint removal is bounded by
`beta (2 M2_{u<=E}+E^(-1) M2_{u>E})`.

The primary lane passes 67,623/67,623 assertions, the independent lane
47,912/47,912, the integrated verifier 801/801, and Lean R384 compiles.  The
primary/independent numeric agreement is 2.160049e-12 in the integrated run.
For transition energies `E=1,2,4`, the primary maximum actual `M_0` removal is
0.3745334781395842, while the corresponding envelopes are
58.957472534179225, 169.83677583776642 and 665.126775048548.  The maximum
actual endpoint removal is 2.060468823284187, with envelopes
17.762698152215687, 9.211990331976548 and 6.479291851990611.  Low/high
partition residuals remain at roundoff.  The raw R-382 d=5-to-d=6 growth
warning remains true.

Lean R384 proves the scalar nonnegativity, low-frequency factor, high-tail
factor, quadratic `M_0` envelope, and the two endpoint factors.  These are
pointwise ingredients for the finite checks only.  The large low-frequency
`M_0`, the high-frequency tail, source/volume/cutoff/beta uniformity, common
core, common alpha, OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A and
Pre-A remain open.

**Next gate.** Establish a Hamiltonian-derived common-core low-frequency
modulus and a source-/cutoff-independent high-frequency tail estimate.  Then
test whether the corridor can be inserted into the R-377 resolvent telescope
and whether the filter can be removed.  A finite envelope alone cannot close
that gate.
