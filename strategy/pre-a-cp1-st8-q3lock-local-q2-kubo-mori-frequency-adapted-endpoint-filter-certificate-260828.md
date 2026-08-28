# R-383 frequency-adapted endpoint filter certificate

## Result-first boundary

R-383 is a T0, claim-nonbearing finite spectral-filter checkpoint under
EXP-001225.  It tests whether the cutoff-sensitive endpoint shell in R-382
can be separated into a low-frequency moment and a resolvent-compatible
high-frequency filter.  The checkpoint does not prove filter removal,
cutoff uniformity, a common core, a common alpha, or any QFT conclusion.

## 1. New diagnostic viewpoint

For a matrix entry with energy difference `u = |E_i-E_j|`, define

`Y_s,ij = X_ij/(1+u)^s`,

and evaluate the endpoint and moments with the squared weight
`(1+u)^(-2s)`.  The finite fixture uses `s=1/2, 1, 3/2`, with `s=1` as
the reference profile.  Pointwise, for `u >= 0`,

`u/(1+u)^(2s) <= 1` for `s >= 1/2`, and
`u^2/(1+u)^(2s) <= 1` for `s >= 1`.

This is a finite spectral analogue of the energy/resolvent smoothing used by
R-377.  It changes the observable before taking the cutoff profile; it does
not assert that the filter can be removed on the Hamiltonian-derived common
core.

## 2. Finite verification

The primary lane passes `59,169/59,169` assertions and the non-importing
independent lane passes `39,458/39,458` over `2,816` contexts.  The
integrated verifier passes `514/514`; Lean R383 compiles with the pinned
toolchain.  Primary and independent numeric fields agree within
`1.9184653865522705e-13`.

The edge profiles (maximum over all declared histories at each cutoff) are:

| cutoff | filter `s` | max filtered `M_0` | max filtered `M_2` | max filtered endpoint |
|---:|---:|---:|---:|---:|
| 3 | 1/2 | 2.733031855844074 | 0.002752402260688318 | 0.001625287872206596 |
| 3 | 1 | 2.733031855844073 | 0.000943817740587793 | 0.000727140511809271 |
| 3 | 3/2 | 2.733031855844071 | 0.0003568904908915179 | 0.000370250020917753 |
| 4 | 1/2 | 3.428320857961583 | 0.01565361137092488 | 0.008147040592980078 |
| 4 | 1 | 3.428320857961578 | 0.004571545715589676 | 0.003699231112018352 |
| 4 | 3/2 | 3.428320857961573 | 0.001689958935826130 | 0.002009272176192223 |
| 5 | 1/2 | 4.701587609555782 | 0.07415192037209425 | 0.02416006916084898 |
| 5 | 1 | 4.701587609555772 | 0.01510742340612509 | 0.009052645754723932 |
| 5 | 3/2 | 4.701587609555763 | 0.004480232632361372 | 0.004572413122362568 |
| 6 | 1/2 | 41.57042344053415 | 1.811278379185376 | 0.3423054354039437 |
| 6 | 1 | 41.57042344053405 | 0.2491904440988113 | 0.09311499130513236 |
| 6 | 3/2 | 41.57042344053396 | 0.05359492459214677 | 0.03952006671298558 |

Across all shapes and filters the maxima are filtered `M_0`
`41.57042344053415`, filtered `M_2` `1.8112783791853755`, and filtered
endpoint `0.34230543540394365`.  At the reference `s=1`, the corresponding
maxima are `41.57042344053405`, `0.24919044409881133`, and
`0.09311499130513236`.  Thus the filter strongly reduces the energy-weighted
shell in this finite fixture, while the low-frequency `M_0` remains as large
as the unfiltered profile.  The R-382 raw d=5 to d=6 growth warning remains
true and is not reinterpreted as a divergence theorem.

## 3. Adversarial review

1. **Exponent convention.**  The implementation forms the squared filter
   weight `(1+|E_i-E_j|)^(-2s)` from the declared fractional powers; the
   `1/2`, `1`, and `3/2` labels are parsed as exact fractions in both lanes.
2. **Low-frequency hiding.**  Filtering does not erase the low-frequency
   contribution: the large d=6 `M_0` is retained and reported.  No claim of
   uniform boundedness is made.
3. **Envelope direction.**  The endpoint envelope is checked only for
   `s >= 1/2`, and the `M_2` envelope only for `s >= 1`; Lean R383 proves the
   scalar unit and half-unit factors used by those checks.
4. **Cauchy consistency.**  Each filtered profile recomputes its own `M_0`,
   `M_2`, endpoint and Cauchy bound; it is not inferred from the raw profile.
5. **History coverage.**  Both beta values, translated sites, selected bond
   terms, both orders, both time signs, every prefix and both adjoints remain
   in every filtered profile.
6. **Independent reconstruction.**  The independent lane rebuilds the
   oscillator, graph, spectrum, prefixes and filter profiles without importing
   the primary audit.
7. **Lean and QFT promotion.**  Lean formalizes scalar positivity/envelopes
   only.  Filter removal, source/volume/cutoff/beta uniformity, common core,
   common alpha, OS/KMS/GNS dynamics, gap, continuum, C6, Sector-A and Pre-A
   remain open.

## 4. Decision and next gate

R-383 advances R-382 by isolating a concrete frequency-adapted diagnostic:
the reference filter reduces the maximum finite `M_2` from the raw R-382
value `17.719559304500326` to `0.24919044409881133`, and the endpoint from
`2.153583814589319` to `0.09311499130513236`, but leaves `M_0` at about
`41.57`.  This identifies low-frequency control and filter removal as the
next analytic bottlenecks rather than treating the filtered data as a
continuum bound.

The next gate is a Hamiltonian-derived common-core estimate that bounds the
low-frequency remainder and proves `Y_s -> X` in the required form; only
after that can the filtered endpoint be connected to the R-377 resolvent
telescope.  If that estimate fails, record the obstruction as a named gate
instead of promoting the finite profile.

No new negative result, tier change or proof-note PDF is issued.  All
source/volume/cutoff/beta uniformity, common core, common alpha, OS/KMS/GNS
dynamics, mass gap, continuum, C6, Sector-A and Pre-A flags remain open.
