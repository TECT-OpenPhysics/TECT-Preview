# R-474 — Conditional ordered-limit rectangular-tail bridge

## Result and boundary

`R-474` (`EXP-001353`) is a T0, claim-nonbearing auxiliary result for the
ordered-limit portion of the T-054 forward contract.  It states the final
epsilon bookkeeping in both directions for two regulator indices.  If the
source owner supplies a strict `epsilon/2` cutoff tail and a strict
`epsilon/2` volume tail in one common norm, the triangle inequality gives a
strict rectangular tail.  The reverse volume-then-cutoff statement is proved
with a separate intermediate observable, so the order is not silently
swapped.

This is a logical interface, not an owner packet.  It supplies no TECT
functional, generator, transfer, state, projection, heat-root map, common
domain, uniform constant, physical sector or observation map.  Passing the
fixture does not establish a thermodynamic, continuum, QFT, Yang--Mills or
mass-gap limit.

## Fixed contract

Let `A(n,m)` be a two-index observable and `L` the proposed limit.  For the
cutoff-then-volume order, the owner must provide `B(m)` and, for every
positive epsilon, an `N` with

`|A(n,m)-B(m)| < epsilon/2` for every `n >= N` and every `m`,

then an `M` with `|B(m)-L| < epsilon/2` for every `m >= M`.  R-474 proves
`|A(n,m)-L| < epsilon` on the rectangle `n >= N, m >= M`.  The reverse order
uses `C(n)` and swaps the two uniform hypotheses.  These are owner obligations
in the eventual common norm; the scalar absolute value is only the formal
placeholder.

## Verification

The primary exact Fraction lane derives every threshold for the fixture
`A(n,m)=1/2^(n+1)+1/3^(m+1)`, rather than inserting thresholds.  It passes
33/33 assertions.  A non-importing independent lane passes 16/16 and agrees
on the canonical threshold/rectangle fingerprint.  The hostile lane rejects
10/10 mutations: identity, claim-bearing promotion, tier promotion, unsafe
epsilon split, non-decaying bases, formula mutation, order swap, uniformity
promotion and method mutation.  The integrated verifier passes 13/13 and
compiles `R474.lean` with Lean 4.32.1.

Reproduction from the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_q3lock_ordered_limit_rectangle.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_q3lock_ordered_limit_rectangle_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_q3lock_ordered_limit_rectangle_hostile.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_q3lock_ordered_limit_rectangle_verify.py --self-test
```

The Lean entrypoint is:

```powershell
Push-Location verification/lean
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean Tect/R474.lean
Pop-Location
```

## Adversarial review

1. **Epsilon split.** The proof uses two strict half-epsilon bounds; a
   non-strict or altered split is rejected by Lean and the hostile harness.
2. **Order direction.** The intermediate functions `B` and `C` are distinct
   and the two order labels are frozen; a swap is rejected.
3. **Finite-to-infinite leap.** Geometric rows only exercise the algebra.  The
   owner-uniformity and ordered-limit flags remain false.
4. **Norm/domain leap.** Absolute values do not provide an operator or field
   norm.  The common norm and common domain are explicit missing inputs.
5. **Promotion.** The result is claim-nonbearing T0 auxiliary support and does
   not close T-054, Pre-A, Sector A, QFT, Yang--Mills, gravity or mass gap.

## Next gate

When a real source-owned dynamics packet is admitted, instantiate the two
contracts in its pinned common norm and prove the required uniform tails over
cutoff, lattice, volume, boundary, phase and beta.  Only then may the ordered
limit be attempted.  Until that packet exists, the T-054 owner gate remains
open and no new physical-empty or BCC variant is justified.
