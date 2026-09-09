# PAH-OMC-020 path-word transport and boundary-tail certificate

This certificate is a bounded analytic sub-lemma for the anchored-`n`
N2c/N4 question.  It keeps the exact PAH-001 non-radial PH/LK/AP rates after
the registered R-511 `j` limit.  It does not introduce a rate envelope,
truncate the source process, change the state, or identify Markov time with a
physical time.

## Frozen source and scope

The source pins are:

* `strategy/pa-hyp/PAH-001-v1.json`
  (`03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`);
* `strategy/pa-hyp/PAH-OMC-004-v1.json`
  (`38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`);
* `strategy/pa-hyp/PAH-OMC-018-result-v1.json`
  (`d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65`);
* `strategy/pa-hyp/PAH-OMC-018-generator-certificate.md`
  (`18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264`);
* `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json`
  (`906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`).

The finite carrier is the exact OMC-004 two-row relational strip `G_n`,
`n>=2`, with its unsplit terminal square.  The state is the R-510/R-511
`j`-limit state `nu_n`; the source PH/LK/AP root labels, partial domains,
midpoint rates, mobility and external stochastic time are unchanged.  The
radial roots have already been removed only in the registered R-511 `j`-limit
pre-form; this certificate does not add a time rescaling.

## Exact path-word identity

For an admissible non-radial root word
`omega=(r_1,...,r_k)`, put `x_0=x` and
`x_i=T_(r_i)(x_(i-1))` on the composition domain, and define

    C_omega(x) = product_i c_(r_i)(x_(i-1)).

R-511 gives, for every source root and its inverse partial bijection,

    nu_n(x) c_r(x)^2 = m_r(x)^2 nu_n(T_r x).

Multiplying this identity along the word gives the exact telescoping relation

    nu_n(x) C_omega(x)^2
      = [product_i m_(r_i)(x_(i-1))^2] nu_n(x_k)
      <= nu_n(x_k),

because the frozen PAH mobility satisfies `0<=m_r<=1`.  The composition of
partial root bijections is again injective and measure preserving on its
domain.  Integration and a change of variables therefore yield

    integral C_omega^2 d nu_n <= 1,
    integral C_omega d nu_n <= 1.

The first inequality is the useful point: it controls every prescribed word
without assuming a bounded pointwise rate.  It is an algebraic consequence of
the original Gibbs state and the original midpoint exponent, not a fitted
constant.

At fixed amplitudes the non-radial label fibre is finite.  Its ordinary
continuous-time jump expansion assigns a word of length `k` a time-simplex
factor `T^k/k!`; the no-jump survival factor is at most one.  The displayed
transport bound consequently gives the word-level probability envelope

    Prob_n,T(omega) <= T^k/k!.

This is a path-word statement.  It is not yet a statement about the full
backward semigroup on the varying `n` spaces.

## Conditional connected-word tail

Suppose a source-valid local graphical or Duhamel construction supplies the
following *additional* data for a fixed local observable:

1. every root support has a uniformly bounded overlap graph;
2. at most `b` next roots overlap a previously reached support, uniformly in
   `n`;
3. at most `a` first roots leave the local support, and a word that reaches a
   boundary at distance `d` has length at least `d`.

Then the number of connected words of length `k` is at most `a b^(k-1)`.
Summing the word envelopes and using the ratio of successive terms gives, for
`b*T < d+1`,

    E_d(a,b,T)
      = [a b^(d-1) T^d / d!] / [1 - b*T/(d+1)].

Indeed the ratio at `k>=d` is `b*T/(k+1) <= b*T/(d+1)`.  For fixed finite
`a,b,T`, the factorial denominator makes `E_d` tend to zero as `d` tends to
infinity.  This is the precise unbounded-rate part of a possible boundary
escape argument: the source rates enter through the exact square transport,
while locality enters only through the overlap data.

The executable primary uses the labelled test inputs `a=3`, `b=5`, `T=1`
and distances `8,12,16`; the independent lane uses `a=4`, `b=6`, `T=3/4`
and distances `10,14,18`.  These are arithmetic fixtures, not estimates of
the PAH strip.  Both lanes verify the simplex ratio and the decreasing
factorial envelope exactly.

## What this does and does not close

The path-word identity removes one previously suspected obstruction: an
unbounded pointwise PAH rate does **not** by itself prevent an `L2` word
estimate.  It supplies a reusable input for N2c/N4.

It does not discharge N2c/N4.  The exact source has not yet supplied (i) an
`n`-uniform root-overlap constant and boundary distance count for all PH/LK/AP
supports, or (ii) a proved coupling/Duhamel identity showing that the
`A_n^{out,m} Q_n(s)g` boundary term is bounded by the connected-word event.
The common `U_n`/Hilbert realization, N2b liminf/recovery and N2d minimal-form
identification also remain open.  A finite path expansion, by itself, cannot
be relabelled as the anchored semigroup limit.

## Adversarial review

1. **Wrong exponent or direction.**  Replacing the midpoint square ratio by a
   one-sided Gibbs ratio breaks the telescoping equality; the hostile lane
   mutates the ratio and observes a nonzero defect.
2. **Mobility shortcut.**  The mass bound uses only the source condition
   `0<=m<=1`; a mobility above one is rejected rather than hidden in a
   constant.
3. **Diagonal-rate expansion.**  No absolute generator-power series is used;
   survival factors in the finite-fibre jump expansion are bounded by one.
4. **Finite fixture promotion.**  The arithmetic values for `a,b,T,d` are
   explicitly test inputs.  They do not certify a source overlap constant or
   an `n`-uniform boundary distance.
5. **N2c promotion.**  Connected-word counting is marked conditional until a
   source-valid coupling/Duhamel attribution is proved.
6. **Physical interpretation.**  No Pre-A, spacetime, QFT, gravity,
   continuum, Yang--Mills, mass-gap or TOE statement follows; Markov time is
   external stochastic time.

The single next question is:

> Can the exact OMC-004 root-incidence data provide an `n`-uniform overlap
> constant and a source-valid coupling/Duhamel lemma that turns this
> connected-word envelope into the required N2c/N4 boundary estimate?

