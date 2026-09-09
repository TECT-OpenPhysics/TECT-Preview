# PAH-OMC-020 source-local Duhamel and coupling attribution certificate

This certificate supplies a bounded finite-fibre locality argument for the
N2c/N4 boundary term.  It keeps the PAH-001 functional, root maps, rates,
Gibbs state, regulator and external stochastic time unchanged.  The result is
conditional at the source-local finite-fibre level and is not an anchored-`n`
semigroup theorem.

## Frozen sources and exact scope

The following source bytes are hash-pinned:

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
* `strategy/pa-hyp/PAH-OMC-020-temporal-work.md`
  (`45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b`);
* `strategy/pa-hyp/PAH-OMC-020-pathword-result-v1.json`
  (`114699a4554e45260a6a6632f44a32e9c0494a9274c27b561c676e93c5d247d9`);
* `strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json`
  (`9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11`).

The carrier is the exact OMC-004 two-row strip `G_n`, `n>=2`, including its
split triangle faces and terminal unsplit square.  The analysis is after the
registered R-511 `j` limit and retains only the original non-radial
`PH/LK/AP` fibre.  No new Hamiltonian, counterterm, projection, carrier,
rate, state or time scale is introduced.

## Finite-fibre coupling construction

Fix an amplitude vector.  The remaining PAH label space and its directed root
set are finite, so the source generator defines an ordinary finite-state
continuous-time jump chain.  For a root `r`, write `S_r` for the exact
dependency footprint of R-516 and `T_r` for the source partial map.  The
OMC-001 declarations say that `T_r` changes only its local coordinates and
that the midpoint rate depends only on the variables in `S_r`.

Take two copies of the chain, initially related by one admissible outside
root.  Use common jump clocks whenever the two local rates agree.  If a rate
differs, maximal coupling bounds the total disagreement intensity by

    |c_r(X)-c_r(Y)| <= c_r(X)+c_r(Y).

Thus a disagreement can reach a new root only through an overlapping
footprint.  Iterating over the finite jump histories gives the following
source-local influence bound for a bounded cylinder `g`:

    |Q_t g(T_r x)-Q_t g(x)|
      <= 2 ||g||_infinity
         sum_{omega:r first, omega connected to supp(g)}
         c_omega(x) t^(|omega|-1)/(|omega|-1)!.

The factor 2 is the two-copy triangle bound and is not hidden in a fitted rate.
Survival probabilities are at most one.  At fixed amplitudes this is the
ordinary finite jump expansion; no absolute generator-power series is used.

## Gibbs `L2` transport and the boundary term

R-515 gives the exact square-transport identity for every prescribed word
`omega`:

    integral c_omega^2 d nu_n <= 1.

Applying Minkowski to `A_n^(out,m)Q_n(t)g` and then this identity gives one
factor at most one for every word coefficient.  Overlap is symmetric, so the
words can be counted backwards from the fixed support of `g`.  If the support
occupies `w` consecutive columns, R-516 gives

    a_w <= 16*(w+2*2+1),       b = 144.

The two-copy triangle factor contributes at most `2^ell` to a word of length
`ell`; equivalently the effective branching is

    b_eff = 2*b = 288.

If `d_m` is the overlap-graph distance from the support to roots whose
footprint leaves `Lambda_m`, every contributing word has length at least
`d_m`.  A footprint has radius at most two columns, and two overlapping
footprints have base columns at distance at most four.  Therefore one may
take the conservative source-local distance

    d_m >= max(1, ceil((m-w-2*2)/4)),

which tends to infinity as the prefix boundary moves outward.  Integrating
the previous estimate over `0<=t<=T` gives, whenever
`b_eff*T < d_m+1`,

    integral_0^T ||A_n^(out,m) Q_n(t)g||_2 dt
      <= 4 ||g||_infinity E_(d_m)(a_w,b_eff,T),

where

    E_d(a,b,T) = [a*b^(d-1)*T^d/d!] / [1-b*T/(d+1)].

The factorial denominator makes the right side tend to zero with `d_m`,
uniformly in `n`, because `a_w`, `b_eff` and the footprint radius depend only
on the fixed source cylinder and local OMC-004 bounds.  The primary script
uses `w=2`, `a_w=112`, `b_eff=288`, `T=1/4` and distances 128, 192, 256 as
exact arithmetic fixtures.  These fixtures verify the ratio and monotone
tail; they are not fitted physical or PAH data.

This proves the **conditional source-local finite-fibre attribution** needed
to interpret the connected-word envelope as an N4 boundary estimate.  It
does not supply a comparison of the varying finite Hilbert spaces.

## Verification and adversarial review

The primary lane performs 61 exact source, geometry, coupling-factor,
distance and factorial-tail checks.  The non-importing independent lane
performs 25 arithmetic checks.  The hostile lane performs 18 checks and
rejects diagonal omission, radius-zero/under-radius locality, dropping the
two-copy factor, using the wrong integrated simplex power, violating the tail
ratio condition, and anchored-n or physical promotion.  The integrated runner
replays all three lanes, verifies that the independent lane does not import
the primary module, checks the Lean registry and compiles
`PahOmc020Duhamel.lean` under Lean 4.32.1.

Lean checks only the finite identities for the two-copy term, the integrated
simplex factor, the ratio condition, effective branching and connected-count
scaling.  It is not a formalization of maximal coupling or an infinite-volume
theorem.

## Remaining boundary

The finite-fibre N4 estimate is conditional on the source-local coupling
construction just stated.  The following remain open and are not inferred:

* a source-authorized common `U_n`/Hilbert realization and terminal-square
  compatible comparison map;
* N2b arbitrary-sequence liminf/recovery and N2d identification with the
  R-512 minimal closed form;
* anchored-`n` semigroup convergence and any infinite-volume process.

Accordingly this checkpoint is `auxiliary_support` only.  There is no physical
Pre-A, spacetime, QFT, gravity, continuum, Yang--Mills, mass-gap or TOE
conclusion, and external stochastic Markov time is not quantum real time,
proper time or Lorentzian time.

The single next question is:

> Can the conditional finite-fibre attribution be lifted through a
> source-authorized common `U_n`/Hilbert realization and a terminal-square
> compatible comparison map without changing the PAH model?

