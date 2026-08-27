# R-369 Kubo-Mori translation and shape stress certificate

## Result-first boundary

R-369 is a T0, claim-nonbearing finite stress under EXP-001211.  It asks
whether the R-368 local Kubo-Mori fractional topology is an artefact of one
bond and one source position.  The stress passes, but it still displays
cutoff growth and therefore does not close a uniform comparison.

## 1. Fixture and question

The actual-Q3 edge uses `V=2`, cutoffs `d=3,4,5,6`, both sites and its bond
term.  The square shape uses `V=4,d=2`, all four sites and all four bond
terms.  Both beta values, split orientations, time signs, history adjoints,
and every prefix position are retained.  For each selected bond the doubled
bond spectrum supplies the normalized Gibbs probabilities and the
Kubo-Mori logarithmic-mean weights used by R-368.

## 2. Verification

Primary and non-importing independent lanes each pass `8601/8601` assertions
over `2816` contexts.  The integrated verifier passes `104/104`, Lean R369
compiles, and the largest primary-independent numeric difference is
`4.219e-15`.  Kubo weight symmetry is exact at the reported precision; the
smallest weight is `3.6452675812342155e-14`.

The global maximum weighted fractional norm is `1.208758407679001`, with
weighted finite-time bound `0.4029194692263337` and maximum change-to-bound
ratio `0.3868613066541026`.  On the edge, the per-cutoff maxima are
`0.0896064105`, `0.2005166806`, `0.3423910272`, and `1.2087584077` for
`d=3,4,5,6`.  On the square, the four bond maxima lie between
`3.1737537048e-08` and `3.5303692708e-08`.

## 3. Adversarial review

1. **Bond translation.**  All four square bond terms are diagonalized and
   compared; no single last-bond convention is silently reused.
2. **Source translation.**  Every square site and both edge sites are used as
   measured locations.  Unlisted graph shapes remain outside the fixture.
3. **Prefix completeness.**  Every prefix position in both split orders is
   evaluated, including the zero and full endpoints.
4. **Cutoff growth.**  The edge sequence grows by more than an order of
   magnitude from `d=3` to `d=6`; this is recorded as finite growth, not as an
   asymptotic divergence theorem.
5. **Weight scope.**  Kubo-Mori weights are from a finite doubled local bond
   Gibbs proxy, not the full interacting KMS state.
6. **Independent arithmetic.**  The second lane rebuilds the oscillator,
   graph, Gibbs weights, witnesses, spectra and all prefixes without importing
   the primary R-369 module.
7. **Lean scope.**  Lean R369 proves the scalar envelope and fixture arithmetic
   only; numerical spectra and limits remain executable evidence.
8. **QFT promotion.**  Source/shape/cutoff/volume uniformity, common core,
   common alpha, OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and
   Pre-A remain open.

## 4. Next gate

The weighted suppression is position-stable on the finite square, but the
cutoff sequence is not evidence of a uniform bound.  The next proof task is
an analytic local Dirichlet collar with a cutoff-independent weight, followed
by a source-complete exhaustion argument.  If a lower-growth estimate can be
proved, register it as a separate scoped obstruction.  No R-369 PDF is issued.

