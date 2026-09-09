# PAH-OMC-024 anchored-n persistence certificate

## Decision

`R-564` is `HOLD_FOR_EVIDENCE`.  The finite positive derivative gap recorded
by R-552 does not, by itself, imply a gap that survives the anchored `n`
limit on a fixed compact Markov-time interval.  An exact reversible two-state
oracle has a positive gap at every finite `n` but a geometrically vanishing gap
and uniform convergence to a common identity target.

This is a logical non-implication diagnostic.  The oracle is not a PAH
carrier, not a PAH rate or state, and not a counterexample to an owner-fixed
PAH completion.

## Pinned source scope

- `PAH-001-v1.json`: SHA-256
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`.
- `PAH-OMC-020-temporal-prereg-v1.json`: SHA-256
  `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`.
- R-552 result: SHA-256
  `44a5f7aefb4da95e7ae0fd8c690da33132b645bfbf8b528b7a01688585cb89ee`.

The PAH functional, transition rates, all-Q Gibbs state, carrier, external
Markov time and registered `j`-before-anchored-`n` order are unchanged.

## Exact diagnostic

Use the abstract reversible two-state chain with stationary state
`pi=(1/2,1/2)`, observable `f=(0,1)`, and rates

```text
r_A(n)=2^(-n),       r_B(n)=2^(-(n+1)).
C_r(t)=1/4 + 1/4 exp(-2 r t).
```

Then

```text
|C'_A(0)-C'_B(0)| = (r_A(n)-r_B(n))/2 = 2^(-(n+2)) > 0
```

for each finite `n`, while for `0 <= t <= T`,

```text
0 <= C_0(t)-C_r(t) <= T*r/2,
```

using `1-exp(-x) <= x`.  Both families therefore converge uniformly on every
fixed compact interval to the same identity target as `n` grows.  The finite
R-552 gap alone cannot rule out this pattern.

## Verification and boundary

The primary, independent and hostile lanes rebuild the rational formulas and
reject constant-gap, physical-time relabelling, oracle-as-PAH-carrier and
universal-promotion mutations.  Lean checks positivity, dyadic halving, the
finite rational value at `n=8`, and its smallness relative to `1/1000`.

The missing source-specific evidence is a uniform-in-`n` positive local
correlation lower bound (or a uniform derivative/remainder estimate that
prevents collapse), together with the root multiplicity and measure fields
and the R-557 common-realization/boundary/target fields.

Reproduce the integrated audit with:

```text
python -X utf8 verification/scripts/pah_omc024_anchored_n_persistence_verify.py
```

No R-512 convergence, infinite-volume, continuum, physical Pre-A, spacetime,
QFT, gravity, Yang--Mills, mass-gap or TOE conclusion is made.
