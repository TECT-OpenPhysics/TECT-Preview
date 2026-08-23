# Q3 matching-layer common-core envelope checkpoint

**Exploration:** `EXP-001024`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Finding

The finite induced box `{0,1,2}^3` has 27 vertices and 54 nearest-neighbor
edges.  Coloring an edge by its axis and the parity of its lower endpoint
coordinate partitions all edges into six matchings of nine edges each.  Thus
each matching layer has incidence at most one at every vertex, while the full
graph still has degree six.

For `K_f=sum_x f_x k_x` with
`k_x >= 1+p_x^2/(2 chi)+gamma q_x^4`, adjacent weight ratio at most `kappa`,
and the exact matching shear, the two scalar identities

`(1+d)p^2+(d^2+d)(c q)^2-(p+d c q)^2`
`= d(p-cq)^2+d^2(cq)^2`

and

`1+sqrt(gamma)^2 q^4-2 sqrt(gamma)q^2`
`=(sqrt(gamma)q^2-1)^2`

give the two-sided form factor
`1+C_match*d`, where
`C_match=1+kappa*c^2/(2 chi sqrt(gamma))`.  For the registered exact
fixture `(c,chi,sqrt(gamma),kappa)=(3/5,7/4,2/5,2)`, this is `53/35`.

The primary SymPy lane and the non-importing Fraction lane check the graph
partition, weight ratios, scalar identities, both signs, four rational
phase-space fixtures, and the six-layer product.  A six-layer endpoint graph
factor is `(1+C_match*d)^3`; an `N`-step split with `d=T/N` is bounded by
`exp(3*C_match*T)`, independent of the finite-box volume.  The onsite factor
has graph norm one only under the explicitly declared tensor-local
self-adjoint/affine-shift hypothesis.

## Lean cross-check

`verification/lean/Tect/R208.lean` kernel-checks `shift_square`,
`quartic_absorb`, and `matching_weight_transfer`.  These are scalar
inequalities only; no unbounded operator, form closure, Trotter limit,
exhaustion, KMS state, or thermodynamic assertion is encoded.

## Adversarial review

- **Matching versus full graph — UPHELD:** the full box is not a matching;
  all estimates are layerwise.
- **Form versus induced norm — UPHELD:** the endpoint norm requires the
  declared positive self-adjoint common-core hypotheses.
- **Onsite isometry — UPHELD:** norm one is conditional on affine local
  energies and tensor commutation, not a numerical inference.
- **Finite box versus exhaustion — UPHELD:** volume-independent constants do
  not control boundary leakage or all-shape summability.
- **Envelope versus convergence — UPHELD:** a graph envelope does not prove
  Lie--Trotter convergence or identify the limiting generator.
- **Lean promotion — UPHELD:** R208 checks only the scalar algebra.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production owner is supplied.

## Decision

`EXP-001024` is an advanced T0 claim-nonbearing finite common-core
checkpoint.  It supplies the missing volume-uniform matching-layer induced
norm envelope requested by `EXP-001023`, under explicit operator hypotheses.
The next proof target is the boundary commutator decay and the resulting
all-shape exhaustion Cauchy theorem.  Common alpha, KMS, ground/gap,
continuum, physical empty space and the TECT production route remain open.
