# R-383 frequency-adapted endpoint filter boundary

R-383 tests a frequency-adapted endpoint shell on the same 2,816 finite
actual-Q3 histories used by R-382.  For `u=|E_i-E_j|`, entries are weighted
by `(1+u)^(-s)` with `s=1/2,1,3/2`; endpoint, `M_0`, `M_2` and the Cauchy
envelope are recomputed from the squared weight.  The primary lane passes
59,169/59,169 assertions, the independent lane 39,458/39,458, the
integrated verifier 514/514, and Lean R383 compiles.

At the edge cutoff d=6, the reference `s=1` profile has maximum filtered
`M_0=41.57042344053405`, filtered `M_2=0.24919044409881133`, and filtered
endpoint `0.09311499130513236`; the raw R-382 values are `41.64826651661874`,
`17.719559304500326`, and `2.153583814589319`.  The filter therefore
attenuates the energy-weighted shell but leaves a large low-frequency `M_0`.
The raw d=5 to d=6 growth warning remains true.

Lean R383 proves the scalar nonnegativity and unit/half-unit filter factors
used in the finite checks.  This is not a filter-removal estimate, a
cutoff-uniform result, or a QFT conclusion.  Source/volume/cutoff/beta
uniformity, common core, common alpha, OS/KMS/GNS dynamics, gap, continuum,
C6, Sector-A and Pre-A remain open.

**Next gate.**  Prove a Hamiltonian-derived common-core estimate for the
low-frequency remainder and a uniform `Y_s -> X` filter-removal bound, then
connect the filtered endpoint to the R-377 resolvent telescope.  If this
fails, register the precise obstruction rather than promoting the finite
profiles.
