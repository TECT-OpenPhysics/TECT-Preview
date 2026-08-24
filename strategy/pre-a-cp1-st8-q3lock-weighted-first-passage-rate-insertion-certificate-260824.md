# Conditional insertion of the EXP-001045 rate into a first-passage bridge

**Exploration:** `EXP-001046`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Conditional response input

Assume the exact Q3 response obeys a factorial first-passage expansion with
one local weighted rate `B` per step, at most `z^n` paths of length `n`, and
two declared endpoint orientations.  This is the unresolved dynamical input;
the present package does not prove it.

The rate is not arbitrary.  EXP-001045 supplies, under R-167's weighted graph
hypotheses,

`B = 1382807/7168`

for one onsite, three Q3-edge, and six spatial-bond choices at source radius
`S=1/4`.  With `z=6`, orientation count `2`, spatial tilt base `2`, and
`t=1/1000`, the weighted exponent is

`E = 2*B*6*2/1000 = 4148421/896000`.

At distance `d=10`, the conditional pointwise envelope is

`2^(-10) exp(E) = (1/1024) exp(4148421/896000)`.

The primary and independent lanes also check the order-32 finite partial
series below `exp(E)`.  This confirms the exact arithmetic insertion and its
distance factor, not the response expansion itself.

## Adversarial review

1. **Rate provenance — UPHELD.** `B` is recomputed from the prior Q3
   onsite/edge/bond fixture.
2. **Orientation count — UPHELD.** The factor two is explicit and separate
   from the degree six path count.
3. **Path count — UPHELD.** `6^n` is conditional graph combinatorics only.
4. **Exponential promotion — UPHELD.** Finite partial sums do not prove an
   infinite operator series or a generator.
5. **Spatial tilt — UPHELD.** The `2^(-d)` cost remains visible.
6. **Lean — UPHELD.** R228 checks rational fixtures only.
7. **QFT promotion — UPHELD.** No common alpha, KMS/OS, GNS gap, continuum,
   C6, Sector A, Pre-A, or TECT production result follows.

## Decision

`EXP-001046` is advanced as a conditional rate-insertion checkpoint.  It
connects the actual Q3 weighted mixed source constant to the existing
first-passage bridge and leaves the central obligation explicit: prove the
factorial first-passage expansion for the actual two-orientation Q3 history.
