# EXP-001084 — finite Q3 all-bond support-local weight recurrence

## Scope

This is a claim-nonbearing finite matrix diagnostic for T-054. It compares
endpoint, one-layer, and full support energy weights under the exact commuting
all-bond bilinear kick on the two-site target, a four-site square face, and the
eight-site Q3 cube. Both kick orientations are evaluated. The (n=3) rows are
used for nontrivial kinetic structure; the full eight-site row uses (n=2) and
is retained as an exact-cube coverage row only.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_q3_all_bond_support_local_weight_recurrence.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_q3_all_bond_support_local_weight_recurrence_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_q3_all_bond_support_local_weight_recurrence_verify.py
```

Primary: 167/167. Independent: 166/166. Integrated: 183/183 with Lean R266.

## Findings

The exact p-recurrence is checked with its finite-truncation CCR residual
retained, while q-invariance is checked to numerical tolerance. The largest
form ratio is the maximum of

```text
spec(K_S^(-1/2) B_delta^* K_S B_delta K_S^(-1/2))
```

over all bonds and both signs of delta; the graph ratio is the corresponding
`K_S^(1/2) B_delta K_S^(-1/2)` norm.

| volume | oscillator n | bonds | max CCR residual | endpoint (form, graph) | one-layer (form, graph) |
|---:|---:|---:|---:|---:|---:|
| 2 | 3 | 1 | 0.27537395 | (1.08474437, 1.04151062) | (1.08474437, 1.04151062) |
| 4 square face | 3 | 4 | 0.54958861 | (1.12461836, 1.06048025) | (1.15620360, 1.07526908) |
| 8 cube | 2 | 12 | 0.31786266 | (1.00000000, 1.00000000) | (1.00000000, 1.00000000) |

The full support row equals the one-layer row on the four-site face and is
approximately one on the n=2 cube. The latter is a degeneracy diagnostic:
the n=2 truncated onsite kinetic and quartic terms are too small to resolve a
nontrivial local topology, so it is not evidence of a thermodynamic bound.

## Decision

`EXP-001084` advances the finite route only. Both orientations and every
tested bond have finite support-weight ratios, but the one-layer enlargement
does not improve the V=4 ratio, the CCR residual grows in the nontrivial rows,
and the exact cube row is cutoff-degenerate. No source-, volume-, cutoff-, or
beta-uniform all-bond topology has been proved. The all-bond common-alpha gate
and the direct projected `D,delta D` gate remain open.

The next non-redundant step is a direct projected `D,delta D` Cauchy audit on
the structured local test class, using the n=3 nontrivial face as the first
finite model and retaining the modular/domain residual. A failure must be
recorded as a route obstruction rather than repaired by enlarging support
without a new estimate.

## Devil's-advocate review

1. **Exact Q3 geometry:** the eight-site row has all twelve Hamming-one bonds;
   the face row is explicitly labeled a square-face subvolume. **UPHELD.**
2. **Orientation:** both positive and negative kicks are evaluated for every
   edge and support. **UPHELD.**
3. **CCR:** the finite p-recurrence residual is measured, never set to zero.
   **UPHELD.**
4. **Weight embedding:** each local Hamiltonian is embedded in the full tensor
   product before spectral powers. **UPHELD.**
5. **n=2 degeneracy:** the full-cube row is not used as a uniformity claim.
   **UPHELD.**
6. **Independence:** the second lane rebuilds oscillator, graph, weights, and
   kick without importing the primary script. **UPHELD.**
7. **Lean scope:** R266 proves only rational arithmetic and graph/support
   fixture facts, not a matrix or QFT theorem. **UPHELD.**
8. **QFT promotion:** common alpha, direct `D,delta D`, OS/KMS/GNS, gap,
   continuum, C6, Sector A, and Pre-A remain open. **UPHELD.**

