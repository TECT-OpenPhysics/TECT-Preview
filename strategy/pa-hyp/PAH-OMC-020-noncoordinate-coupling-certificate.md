# PAH-OMC-020 non-coordinate maximal-prefix coupling candidate

## Decision

`HOLD_FOR_EVIDENCE` for the full PAH-OMC-020 objective.  This checkpoint
records a researcher-owned non-coordinate comparison candidate and proves
only its finite conditional-expectation contraction and local-cylinder
recovery algebra.  It is not a source-authorized owner packet.  The missing
energy intertwining, N2b liminf/recovery, N2c/N4 boundary escape and N2d
minimal-form identification are not inferred.

## Frozen source and scope

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md` | `49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf` |
| `strategy/pa-hyp/PAH-OMC-019-result-v1.json` | `82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd` |
| `strategy/pa-hyp/PAH-OMC-020-N2a-owner-packet-intake-v1.json` | `638379f3ecafdab8d11aa63ef4ad0ab6346640226ffa6c93825ec5a1f04d489a` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-n2b-common-space-audit/result.json` | `034f5fc35a88a4431ee1594c8a25e0d7bcf6c75b055ec2b21bbf30daf636dc7f` |
| `strategy/pa-hyp/PAH-OMC-020-boundary-kernel-obstruction-result-v1.json` | `3497fb5b0e6ea99add8fd4b0f6cbef124eaadf1d33ec7cadc9b5c798a316748b` |

The PAH functional, original directed rates, labelled Gibbs states, external
unaccelerated Markov time, carrier and `j`-before-`n` order are unchanged.  The
target is the R-510/R-512 local-state Hilbert completion, but the candidate
does not assume that the R-512 semigroup has already been selected.

## Candidate map

For each prefix `Lambda_m`, let `p_(n,m)` and `p_(infty,m)` be the exact
finite and limiting marginal densities relative to their common labelled
Lebesgue reference.  Use the R-510 bounded-measurable prefix modulus

    delta_(n,m) = min(1, 4 D_m q^(n-m)).

Choose the deterministic diagonal index

    m_n = max { 0 <= m < n : delta_(n,m) <= 1/(m+1)^2 }.

The set is nonempty because the modulus is capped at one.  For each fixed
`m`, the R-510 exponential factor eventually satisfies the displayed
threshold, so `m_n` tends to infinity.  Couple the two `Lambda_(m_n)`
marginals by their maximal overlap, and extend the finite and infinite tails
by their regular conditional laws.  If `(X_infty,Y_n)` has this coupling,
define

    (U_n f)(X_infty) = E[f(Y_n) | X_infty].

This is a genuinely non-coordinate Markov-kernel lift.  Conditional Jensen
gives `||U_n f||_2 <= ||f||_2`.  If a bounded cylinder `f` is supported in
`Lambda_k` and `k <= m_n`, then the coupling mismatch event has probability
`TV_(n,m_n)`, and

    ||U_n f - f||_2^2
      <= 4 ||f||_infinity^2 TV_(n,m_n)
      <= 2 ||f||_infinity^2/(m_n+1)^2.

The same estimate combined with the R-510 local state error gives an explicit
N1 local norm/inner-product recovery bound.  No density-ratio multiplier and
no direct-sum phase or charge rescue is used.

## Finite verification

The exact two-point fixture uses limiting prefix law `(3/5,2/5)`, finite law
`(1/2,1/2)`, and maximal-overlap matrix

    [[1/2, 1/10],
     [0,   2/5 ]].

Its overlap is `9/10` and mismatch/total variation is `1/10`.  The primary
lane checks the row and column laws, an exact conditional-Jensen contraction
grid, the bounded-cylinder recovery inequality, and the diagonal threshold
construction.  The non-importing independent lane rebuilds these facts with
a different rational grid.  The hostile lane rejects ratio reversal,
coordinate-density shortcuts, direct-sum or fitted-weight repairs, and any
promotion of local contraction to energy or temporal claims.

| artefact | SHA-256 |
|---|---|
| primary run | `22fa2ca9a61cd17e771cc40d55495c12f2c9faab6a5b0168bdd21672e1e49fb4` |
| independent run | `a6db1ed9a4edf726dc5c1d3b50e16b3762a0af7d242452449c754283f71c3d2b` |
| hostile run | `6884f98bb0481cff531a1fd4cde59a81cd3874eca426e2b671b259d61dfdf8ce` |
| integrated run | `03bc2d6557071d700351fc24660bfc16074e49f50b0e14a6c549b5cd37412abc` |

Reproduce with:

```text
python -X utf8 verification/scripts/pah_omc020_noncoordinate_coupling_candidate.py --check
python -X utf8 codes/foundations/pah_omc020_noncoordinate_coupling_independent.py --check
python -X utf8 codes/foundations/pah_omc020_noncoordinate_coupling_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_noncoordinate_coupling_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Lean 4.32.1 compiles
`verification/lean/Tect/PahOmc020Coupling.lean`, whose registered declarations
are finite overlap, marginal, Jensen-contraction and recovery inequalities.
The Lean source hash is `934969892038278f0358f1d3595cb12747250a1efcd81df88d867a0bfafd4b44`.

## Adversarial boundary

1. **Map identity.**  The operator is a conditional-expectation kernel, not
   the coordinate pullback or its unbounded terminal density ratio.
2. **Measure mismatch.**  Maximal overlap gives mismatch exactly equal to
   total variation; the finite fixture checks both row and column marginals.
3. **Diagonal choice.**  `m_n` is defined from the exact R-510 modulus before
   any energy calculation; fixture values are test oracles, not PAH constants.
4. **Scope.**  Local contraction and N1 recovery do not imply form-energy
   intertwining, arbitrary-sequence liminf or boundary escape.
5. **Promotion firewall.**  No source-owner sign-off, semigroup convergence,
   physical time, Pre-A, spacetime, QFT, gravity, continuum, mass-gap,
   Yang--Mills or TOE claim is made.

## Next question

Can the source owner authorize this exact maximal-prefix coupling and provide a
PAH-specific energy-intertwining estimate that upgrades its local recovery to
N2b, N2c/N4 and N2d without changing PAH-001?

## Non-claims

- No source-authorized full `U_n` owner packet, Mosco theorem, N2b liminf or
  recovery, N2c/N4 boundary escape, N2d minimal-form identification, or
  PAH-OMC-020 semigroup convergence is proved.
- R-524 remains a separate coordinate-preserving obstruction; it is not a
  universal no-go for this non-coordinate candidate.
- No PAH-001 functional, rate, state, carrier, regulator, counterterm,
  external Markov time or limit order is changed.
- No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap,
  Yang--Mills or TOE conclusion follows.
