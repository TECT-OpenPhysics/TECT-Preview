# Exact exponential shell-tail majorant

**Result:** `R-444`  
**Exploration:** `EXP-001289`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Exact scope

Use the scalar edge weight

```
w(x) = 2^(-||x||_1)
```

on the integer lattice `Z^3`.  The number of lattice points at radius zero is
one and for `n >= 1` is `N_3(n)=4*n^2+2`.  Since a site has at most three
positive-coordinate outgoing edges, the ambient tail outside radius `R >= 1`
is

```
T(R) = 3 * sum_(n>=R) (4*n^2+2) * 2^(-n)
     = 3 * (4*R^2 + 8*R + 14) * 2^(1-R).
```

Every positive-coordinate finite rectangular box is a subset of this ambient
edge set, so its finite tail is bounded by `T(R)`.  The executable lane checks
the shell counts, the exact tail recurrence, and all ordered boxes in
`[2,8]^3` for radii `1..12`.

## Evidence

- Primary exact Fraction lane: `4519/4519` assertions.
- Independent integer-loop lane: `4505/4505` assertions.
- Hostile contract firewall: `8/8` mutations rejected.
- Integrated verifier: `27/27` assertions.
- Lean `R444`: PASS for shell-count and closed-form arithmetic fixtures.

The finite sweep covers 343 boxes, 102,900 edges in aggregate, and 4,116
box/radius tail rows.  These are scalar geometric totals; no operator norm is
hidden in the bound.

## Assumptions

1. The ambient lattice is `Z^3` with the stated l1 shell count.
2. Edges are positive-coordinate nearest-neighbour increments, counted through
   their lower endpoints.
3. Weights are nonnegative and depend only on the lower endpoint l1 radius.
4. Finite rectangular boxes are subsets of the translated ambient edge set.
5. Lean checks arithmetic fixtures; Python checks exact finite dominance and
   shell recurrences.

## Missing assumptions

- An identification of the actual Q3LOCK interaction or commutator with this
  scalar edge weight.
- Representation-independent common-core, product-domain and self-adjointness
  estimates.
- Source-, cutoff-, phase-, volume-, shape- and history-uniform commutator
  bounds and a transfer from scalar tails to operator tails.
- All-shape exhaustion Cauchy, Lie--Trotter/common-alpha convergence,
  OS/KMS/GNS identification and sector coercivity.

## Adversarial review

- **Shell count — UPHELD:** `n=0` is treated separately and the positive shell
  formula is checked independently through radius 12.
- **Tail recurrence — UPHELD:** the exact closed form is compared to each
  one-shell decrement; no fitted decay constant is used.
- **Finite box dominance — UPHELD:** every `[2,8]^3` box and every tested
  radius is checked against the ambient bound.
- **Scalar versus commutator — UPHELD-OPEN:** the hostile lane rejects
  commutator/history-tail and weighted-operator promotion.
- **QFT promotion — UPHELD:** physical-empty, continuum, Yang--Mills and
  mass-gap flags remain false.

## Decision and boundary

`R-444` advances the scalar geometric tail input needed by a possible
boundary/history-tail proof.  It does not prove a Q3LOCK commutator estimate,
common core, common alpha, exhaustion, OS/KMS/GNS, physical-empty comparison,
`C6`, Pre-A, Sector-A, Yang--Mills dynamics or a mass gap.  No claim tier
changes and no negative result is issued.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_exponential_shell_tail.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_exponential_shell_tail_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_exponential_shell_tail_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_exponential_shell_tail_verify.py
lake env lean Tect/R444.lean
```
