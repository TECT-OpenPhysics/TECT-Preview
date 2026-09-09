# PAH-OMC-020 exact root-footprint overlap certificate

This certificate records one bounded locality input for the PAH-OMC-020
anchored-`n` question.  It keeps the source PAH-001 generator, labelled Gibbs
state, mobility and external stochastic time unchanged.  It does not add a
carrier, interaction, counterterm, rate envelope or physical interpretation.

## Frozen source and scope

The source pins are:

* `strategy/pa-hyp/PAH-001-v1.json`
  (`03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`);
* `strategy/pa-hyp/PAH-OMC-001-v1.json`
  (`948a87092f7393e5214a375d66295237e5c8be1b018b8788d3e6785d696e774f`);
* `strategy/pa-hyp/PAH-OMC-004-v1.json`
  (`38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`);
* `strategy/pa-hyp/PAH-OMC-018-generator-certificate.md`
  (`18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264`);
* `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json`
  (`906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`);
* `strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json`
  (`114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9`);
* `strategy/pa-hyp/PAH-OMC-020-pathword-certificate.md`
  (`05abbf6379da1ad8fdd562da9198bc3a961d19ba929dda201b160d2728fe3845`).

The finite carrier is exactly the OMC-004 two-row relational strip `G_n`,
`n>=2`, with split triangular faces and the terminal unsplit square.  The
registered R-511 `j` limit has already removed the radial `TR` roots from the
non-radial fibre.  The remaining roots are `PH(v,+/-)`, `AP(v,+/-)` and
`LK(q,+/-)` with the source `K=2` channel multiplicity.  No new finite model
is proposed.

## Dependency footprint

For a root, define its proof footprint as the local source variables needed to
evaluate its unchanged move and its displayed functional increment:

* a `PH` root at a vertex sees the incident edges and endpoint vertices;
* an `LK` root at an edge sees that edge and all edges in incident faces;
* an `AP` root at a vertex sees the incident edges and all edges in incident
  faces;
* every retained edge contributes both endpoint vertices.

This is a dependency set for a locality proof, not an alteration of the PAH
functional.  OMC-004 gives at most four edge slots in one base column.  There
are two vertices per column, four PH/AP directions per vertex, and two LK
directions per edge.  Therefore

    roots_per_base_column = 2*(2+2) + 4*2 = 16.

The footprint reaches no more than two columns from its base: an incident edge
is one column away and an incident face edge adds at most one more column.
Consequently a footprint can overlap only roots based in the nine columns
from `base-2` through `base+2`, and the conservative branching bound is

    b = 16*(4*2 + 1) = 144.

The same calculation for a two-column local support gives

    a = 16*(2 + 2*2 + 1) = 112

possible first roots.  These are source-derived bounds; they are not fitted
from rate values.

## Exact reconstruction and independent checks

The primary reconstruction enumerates the exact strip for `n` equal to
`2,3,4,6,10,20`.  It verifies the source root count
`2*(2|V|+|E|)`, at most four edge slots per column, at most sixteen roots per
column and radius at most two.  The exact maximum overlap degree including
self is 56 for `n=2` and 70 for every tested `n>=3`, so all enumerations lie
below the derived 144 bound.

The non-importing independent lane reconstructs the interval overlap and edge
slot arithmetic separately.  It obtains 16 roots per column, radius 2,
`b=144`, and a distinct three-column fixture with first-root bound 128.  It
does not import the primary module.  The hostile lane removes the diagonal,
mutates the radius and violates the factorial ratio condition; each mutation
is rejected.

Lean 4.32.1 compiles the finite declarations
`overlap_branching_bound` and `connected_word_count_bound`.  Those declarations
check the arithmetic only; they do not purport to formalize a Duhamel theorem.

## What the bound supplies

R-515 gives every prescribed non-radial word a Gibbs `L2` square-transport
bound and, conditionally on a connected-word count, a factorial tail.  The
present result supplies the source-derived overlap branch `b=144` and a
fixed-support first-root bound.  Thus, if a source-valid construction proves
that a boundary influence is represented by connected root words, the R-515
tail can be instantiated without a global pointwise rate bound.

The arithmetic tail condition is `b*T < d+1`; the primary and independent
large-distance fixtures verify exact decreasing tails.  The fixture values are
test inputs and are not a PAH estimate.

## Boundary and missing theorem

The essential remaining question is not combinatorial.  The source still has
to provide a coupling or Duhamel identity that bounds the exact
`A_n^(out,m) Q_n(s) g` term by the connected-word event controlled by this
footprint.  Without that attribution, the present result cannot discharge
N2c/N4, cannot establish anchored-`n` convergence, and cannot select the
R-512 minimal closed form.  A common `U_n`/Hilbert realization, N2b
liminf/recovery and N2d identification also remain open.

## Adversarial review

1. **Finite-table promotion.**  The six enumerated strips are diagnostics;
   the all-`n` bound is derived from the source degree/incidence inequalities.
2. **Hidden model change.**  The footprint is a proof dependency set only;
   every PAH label, rate, state, mobility, regulator and time convention is
   hash-pinned.
3. **Missing diagonal.**  The hostile lane rejects a diagonal-omission
   mutation because it changes the exact source root count.
4. **Tuned radius or tail.**  The hostile lane rejects an under-radius bound and
   enforces `b*T/(d+1)<1` before evaluating a tail.
5. **N2c promotion.**  The word-to-Duhamel/coupling attribution is explicitly
   unproved; `b=144` is an input, not N2c/N4 closure.
6. **Physical promotion.**  No Pre-A, spacetime, QFT, gravity, continuum,
   Yang--Mills, mass-gap or TOE statement follows.  Markov time remains
   external stochastic time.

The single next question is:

> Can a source-authorized coupling or Duhamel construction use this exact
> OMC-004 footprint and `b=144` to bound `A_n^(out,m) Q_n(s) g`, without
> changing the PAH model or interpreting Markov time physically?

