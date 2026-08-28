# R-384 two-scale filter-removal corridor certificate

## Result-first boundary

R-384 is a T0, claim-nonbearing finite spectral diagnostic under
EXP-001226.  It splits the R-383 reference-filter remainder at a transition
energy `E` and checks separate low-frequency and high-frequency envelopes.
The checkpoint does not prove filter removal, a cutoff-uniform tail, a common
core, a common alpha, or any QFT conclusion.

## 1. New diagnostic viewpoint

For `u=|E_i-E_j|`, let `X` denote the centered matrix entry and define the
reference filtered entry by

`Y_1,ij = X_ij/(1+u)`.

With the state-weighted quadratic moment `M_0`, the exact finite removal term is

`||X-Y_1||^2_M0 = sum_ij p_i (u/(1+u))^2 |X_ij|^2`.

For every `E>0`, the pointwise split gives the finite corridor

`||X-Y_1||^2_M0 <= E^2 M0_{u<=E} + E^(-2) M2_{u>E}`.

For the endpoint first moment `D_1`, the corresponding finite bound is

`D_1(X)-D_1(Y_1) <= beta (2 M2_{u<=E} + E^(-1) M2_{u>E})`.

The first term exposes the low-frequency remainder; the second is a
resolvent-like high-frequency tail.  This is a two-scale finite identity and
not a statement that either term is uniform in source, volume or cutoff.

## 2. Finite verification

The primary lane passes `67,623/67,623` assertions and the non-importing
independent lane passes `47,912/47,912` over `2,816` contexts.  The integrated
verifier passes `801/801`; Lean R384 compiles with the pinned toolchain.
Primary and independent numeric fields agree within `2.160049e-12` in the
integrated run.

The maximum profiles over all declared shapes, cutoffs and histories are:

| transition `E` | low `M_0` | high `M_0` | low `M_2` | high `M_2` | actual removal `M_0` | removal envelope | actual endpoint removal | endpoint envelope |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 41.57042344053425 | 0.36721443922448294 | 0.04313884771535939 | 17.676420456784967 | 0.3745334781395842 | 58.957472534179225 | 2.060468823284187 | 17.762698152215687 |
| 2 | 41.57042344053425 | 0.28186956871981417 | 0.23480711981759037 | 17.484752184682733 | 0.3745334781395842 | 169.83677583776642 | 2.060468823284187 | 9.211990331976548 |
| 4 | 41.57042344053425 | 0.18291599980841583 | 1.17108687192316 | 16.548472432577167 | 0.3745334781395842 | 665.126775048548 | 2.060468823284187 | 6.479291851990611 |

All low/high partition residuals are at roundoff (`<=1.20e-14` for `M_0`
and `<=7.11e-15` for `M_2` in the primary lane).  The corridor inequalities
pass in both implementations.  The R-382 d=5-to-d=6 growth warning remains
true; it is retained as finite evidence rather than interpreted as a limit or
divergence result.

## 3. Adversarial review

1. **Filter algebra.**  The removal weight is computed as the squared
   difference `1-(1+u)^(-2)`, while the endpoint uses the unsquared filter
   weight.  Both lanes construct these expressions directly from `u`.
2. **Envelope direction.**  Low modes use `(u/(1+u))^2<=E^2`; high modes use
   `(u/(1+u))^2<=1<=u^2/E^2`.  The endpoint bounds use
   `u(1-(1+u)^(-2))<=2u^2` below `E` and `<=u^2/E` above `E`; Lean R384
   formalizes these scalar inequalities.
3. **Boundary leakage.**  The large low-frequency `M_0` is reported rather
   than hidden by the filter.  No finite maximum is re-labelled as a uniform
   bound.
4. **Partition completeness.**  The masks `u<=E` and `u>E` are complementary
   up to the declared gap tolerance; both partition residuals are asserted at
   every context and cutoff.
5. **Endpoint subtraction.**  The actual removal is recomputed as
   `max(0,D_1(X)-D_1(Y_1))`; the clamp only removes negative floating-point
   roundoff and is not used to manufacture an envelope.
6. **History and state coverage.**  Both beta values, translated sites,
   selected bond terms, both orders, both time signs, every prefix and both
   history adjoints are retained.
7. **Independent reconstruction.**  The independent lane rebuilds the
   oscillator, graph, spectrum, prefixes and corridor profiles without
   importing the primary audit.
8. **Lean and promotion.**  Lean proves scalar factors only.  A common-core
   estimate, high-frequency tail theorem, filter removal, source/volume/
   cutoff/beta uniformity, KMS/GNS dynamics, gap, continuum, C6, Sector-A and
   Pre-A remain open.

## 4. Decision and next gate

R-384 advances R-383 by turning the qualitative low-frequency/high-frequency
split into an explicit finite corridor.  The finite remainder is small compared
with its deliberately loose envelope, but the low `M_0` maximum remains
`41.57042344053425`, and the raw cutoff growth warning persists.  Thus the
new viewpoint isolates, rather than resolves, the analytic bottleneck.

The next gate is a Hamiltonian-derived common-core estimate that supplies a
cutoff/source-independent low-frequency modulus and a resolvent-controlled
high-frequency tail.  Only after those estimates are proved can `Y_1 -> X`
be used in the R-377 telescope.  If either modulus fails, record the precise
obstruction as a named gate rather than promoting this finite corridor.

No new negative result or tier change is issued, and no proof-note PDF is
created for this finite checkpoint.  All limiting/QFT flags remain open.
