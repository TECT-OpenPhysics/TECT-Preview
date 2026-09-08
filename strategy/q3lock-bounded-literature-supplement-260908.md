# Q3LOCK bounded literature supplement: multidimensional oscillators and anisotropic spin systems

**Date:** 2026-09-08  
**Status:** T0 comparison-only source audit / no priority claim / PDF deferred  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 (R-497, claim_bearing=false)

## Question

Do two additional primary sources provide a direct finite-temperature phase
theorem for the positive-lambda, non-radial, eight-component Q3LOCK model, or
do they remain comparison-only references? The audit is intentionally bounded:
it records the exact source scope inspected and does not claim that the
anisotropic continuous-oscillator literature has been exhausted.

## Faris--Minlos: multidimensional anharmonic oscillators

Primary source: W. G. Faris and R. A. Minlos, *A quantum crystal with
multidimensional anharmonic oscillators*, Journal of Statistical Physics 94
(1999), 365--387, DOI
[`10.1023/A:1004588002407`](https://doi.org/10.1023/A:1004588002407),
[author-hosted source PDF](https://math.arizona.edu/~faris/Crystal.pdf).

The inspected abstract and opening theorem state a periodic lattice of
multidimensional anharmonic oscillators with nearest-neighbour quadratic
coupling. For sufficiently small coupling, the authors construct a convergent
ground-state cluster expansion with estimates independent of the crystal
size. The source uses a Feynman--Kac/diffusion representation and assumes a
single-site potential with superquadratic growth. The displayed Hamiltonian
has a finite-dimensional oscillator at each site and a bilinear spatial
coupling; the stated theorem is a zero-temperature ground-state limit in a
small-coupling regime.

The result is therefore a useful domain and method comparator for the
Q3LOCK form, but it does not directly supply any of the following:

* finite-temperature Euclidean DLR existence or source-window continuity for
  the Q3LOCK source family;
* continuous-loop FKG, the collective Falk--Bruch/infrared lower bound, a
  strict source cusp, or a parity-related DLR pair;
* the positive-lambda non-radial Q3 interaction at the paper's explicit
  low-temperature threshold; or
* a common infinite-volume real-time dynamics, KMS identification, gap, or
  continuum limit.

The paper remarks that related techniques may be useful at non-zero
temperature, but that remark is not a theorem matching the present target.
No direct analytic import is made.

## Fröhlich--Lieb: anisotropic lattice spin systems

Primary source: J. Fröhlich and E. H. Lieb, *Phase transitions in anisotropic
lattice spin systems*, Communications in Mathematical Physics 60 (1978),
233--267, DOI
[`10.1007/BF01612891`](https://doi.org/10.1007/BF01612891),
[IHES primary record/PDF](https://repo-archives.ihes.fr/FONDS_IHES/I_Prepublications/FROHLICH/1978-1980/P_78_199/P_78_199_web.pdf).

The primary abstract describes a general low-temperature phase-transition
method applied to six nearest-neighbour classical and quantum spin models on
the two-dimensional square lattice. The models have finitely degenerate
anisotropic ground states. The method combines a Peierls argument,
reflection-positivity/chessboard estimates, and exponential localization; the
source reports long-range order for five of the six models at sufficiently low
temperature, with a separate reflection-positivity qualification for the
remaining quantum Heisenberg case.

This is prior art for combining reflection positivity with contour and
localization arguments in anisotropic spin systems. It is not a direct source
for the Q3LOCK theorem: the inspected source is a two-dimensional spin-model
family, whereas the manuscript treats an unbounded continuous
`R^8` oscillator at every site, a three-dimensional spatial lattice,
Euclidean loop measures, a source-pressure cusp, and a DLR-state construction.
No Q3LOCK reduction to one of the Fröhlich--Lieb models is supplied. The
source is retained as a comparison-only citation and no result is imported.

## Schneider--Beck--Stoll access boundary

The publisher record for Schneider--Beck--Stoll, *Quantum effects in an
n-component vector model for structural phase transitions*, Physical Review B
13 (1976), 1123, DOI
[`10.1103/PhysRevB.13.1123`](https://doi.org/10.1103/PhysRevB.13.1123), is
available. The full article was not available in the current source capture.
Its hypotheses and conclusions therefore remain **NOT-YET-ASSESSED**; no
statement is inferred from the abstract or title. A specialist must resolve
this access item before any novelty or direct-coverage conclusion is made.

## Disposition and next gate

The supplement narrows two plausible direct-import shortcuts but does not
close the literature audit. Faris--Minlos is a small-coupling ground-state
cluster-expansion comparator; Fröhlich--Lieb is a two-dimensional anisotropic
spin-model phase-transition comparator. Neither replaces the model-specific
Q3LOCK collective lower bound and loop/DLR composition. The paper remains T0,
claim-non-bearing, internal-review only, and PDF-deferred.

The next publication gate is a signed specialist disposition that either
identifies an exact covering anisotropic continuous-oscillator theorem (with a
hypothesis-by-hypothesis reduction) or confirms the residual model-specific
content. Content and notation must then be frozen, all replay hashes renewed,
and the final PDF generated and visually reviewed only at that terminal stage.

