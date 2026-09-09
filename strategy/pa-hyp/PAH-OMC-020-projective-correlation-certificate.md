# PAH-OMC-020 projective local-correlation envelope

## Result and boundary

This checkpoint records a conditional scalar envelope for one non-radial,
grade-blind local cylinder. It is an auxiliary result, not a completion of
the anchored-n PAH-OMC-020 objective. The PAH-001 functional, directed rates,
labelled Gibbs state, partial domains, carrier, regulator order and external
stochastic time are unchanged.

The exact source bytes used here are:

* strategy/pa-hyp/PAH-001-v1.json
  (03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37);
* strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json
  (e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc);
* the R-493 integrated replay
  (8d005bea7ee33111712f58a32046cdb254f77bc8c17d8eb1a470abcc2adbbbc7);
* strategy/pa-hyp/PAH-OMC-017-result-v1.json
  (4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb);
* strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json
  (114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9);
* strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json
  (9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11);
* strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json
  (67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d);
* strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json
  (906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3).

The common cylinder is grade-blind: it can use finitely many retained
occupations and closed-face holonomies, but cannot inspect the disjoint-union
grade, aperture, open links or phases. Choose a non-radial cylinder of
support width two and use the finite jump-word cutoff m=6 before comparing
levels n. R-493 gives an eventual identity for every retained finite word
after N(f)=max(2,m(f)+1); for the displayed support fixture this is N=3.

## Envelope

R-516 derives the local data directly from the OMC-004 strip:

    roots per column = 16
    edge slots       = 4
    footprint radius = 2
    b                = 16*(4*2+1) = 144.

The two-copy triangle in R-517 is retained, so the effective branching is
b_eff=2b=288. For support width w, the first-root count is derived as
a_w=16*(w+2*2+1); the width-two fixture gives a_w=112.

For a compact external Markov horizon T, the conditional boundary remainder
uses the registered factorial envelope

    E_d(a,b,T) = [a*b^(d-1)*T^d/d!] / [1-b*T/(d+1)]

whenever b*T<d+1. The primary lane uses the labelled arithmetic fixture
T=1/4 and distances d=128,192,256; the tail is positive and strictly
decreasing. These are reproducibility fixtures, not fitted physical
constants.

For a local product f*g, R-510 supplies the local-state Cauchy term
4 ||f||_infinity ||g||_infinity D q^(n-s). The pair comparison at n and
n+1 is bounded by the sum of those two terms. Combining it with the two
R-517 boundary remainders gives the conditional scalar envelope

    |C_(n+1)^(m)(f,g;t) - C_n^(m)(f,g;t)|
     <= e_state(n) + e_state(n+1)
        + 8 ||f||_infinity ||g||_infinity E_d(a_w,b_eff,T).

Here C_n^(m) denotes only the finite-word-truncated local correlation. The
R-493 identity justifies the equality of the retained word terms; the R-510
term controls the local Gibbs-state passage; the R-517 term is the stated
conditional word-to-Duhamel attribution for words that reach the prefix
boundary.

## Verification lanes

verification/scripts/pah_omc020_projective_correlation.py performs 50 source
and exact-arithmetic checks. The non-importing reconstruction
codes/foundations/pah_omc020_projective_correlation_independent.py performs
35 checks using a width-three and T=1/6 fixture. The hostile lane performs
31 checks and rejects dropping the two-copy factor, using the factorial tail
before its ratio condition, treating a finite cutoff as an infinite series,
reading the grade, using C_sw=540 as an equality, or promoting external
Markov time.

verification/lean/Tect/PahOmc020Projective.lean compiles eleven finite
rational declarations under Lean 4.32.1. Lean checks the branching
arithmetic, factorial-term positivity, two-copy algebra and finite fixture
inequalities only; it does not formalize the coupling, the state limit, a
common Hilbert space or an infinite-volume process.

The integrated verifier reports 23/23 checks after replaying all three lanes
and the Lean registry. The exact run artifacts and hashes are recorded in
the R-519 result card.

## Adversarial review

1. One-copy shortcut. Replacing b_eff=288 by b=144 gives a smaller tail and
   is rejected; the explicit two-copy rate-difference triangle is part of
   the bound.
2. Finite-word overreach. Equality through m=6 does not imply equality of
   the infinite jump series. The remainder is retained and bounded only
   conditionally.
3. State-space overreach. R-510 controls fixed local products, not a
   completed common U_n or arbitrary weakly convergent sequences.
4. Boundary overreach. The R-517 word-to-Duhamel construction is a
   finite-fibre conditional input; it is not an independent N2b or N2d
   proof.
5. Physical overreach. No physical sector, Pre-A, spacetime, QFT, gravity,
   continuum, Yang--Mills, mass-gap or TOE statement is made.

## Remaining question

Can a source-authorized common U_n and a terminal-square-compatible
comparison identify this fixed-cutoff projective envelope with the R-512
minimal-form semigroup for all local cylinders? Reopen only when such a
packet or an exact comparison counterexample is supplied; do not repeat the
radial or finite word fixtures.
