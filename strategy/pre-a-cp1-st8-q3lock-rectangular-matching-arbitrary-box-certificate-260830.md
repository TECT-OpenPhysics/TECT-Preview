# Arbitrary finite rectangular axis-parity matching theorem

**Result:** `R-443`  
**Exploration:** `EXP-001288`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Exact scope

For a finite rectangular integer box with side function `s`, vertices are
coordinate vectors and edges are nearest-neighbour one-coordinate increments.
Each edge is represented by its unique lower endpoint and its axis.  The colour
is `(axis, lower_endpoint_coordinate mod 2)`.  The two parity layers for each
axis are retained even when one layer is empty.

The Lean theorem quantifies over arbitrary finite dimension, side functions,
vertices and bounded incident lower endpoints.  If two incident lower
endpoints have the same axis and parity, their axis coordinates cannot be the
forward and backward candidates simultaneously; they are therefore equal.
This is exactly the per-colour matching condition.  A separate arithmetic
lemma records the six layers in dimension three.

The executable cross-check enumerates all 343 ordered side triples in
`[2,8]^3`, recomputes

```
|E| = sum_axis ((s_axis - 1) * product_other_axes s_other),
```

and checks every retained colour layer and local two-candidate incidence.

## Evidence

- Primary compact aggregate: `235319/235319` assertions.
- Non-importing mixed-radix reconstruction: `132418/132418` assertions.
- Hostile contract firewall: `8/8` mutations rejected.
- Integrated verifier: `34/34` assertions.
- Lean `R443`: PASS (`same_colour_incident_unique`,
  `arbitrary_box_layer_matching`, `six_colour_layers`).

The 343-box sweep contains 42,875 vertices and 102,900 edges in aggregate,
with six colour layers, maximum graph degree six, and exact edge-count and
matching checks on every box.  These are finite combinatorial aggregates.

## Assumptions

1. The box is finite and rectangular, with every side length at least two.
2. Only nearest-neighbour coordinate increments are edges; diagonal and
   periodic edges are excluded.
3. The lower endpoint and axis representation is unique.
4. The parity colour convention and empty-layer retention are fixed before the
   enumeration.
5. The Lean statement is abstract combinatorics and does not define a Q3LOCK
   Hamiltonian, representation, state or limiting procedure.

## Missing assumptions

- Transfer from the matching partition to the weighted Q3LOCK interaction and
  a representation-independent product/common domain.
- Onsite self-adjointness and common-core estimates for layer subflows.
- Source-, cutoff-, volume-, shape- and exhaustion-uniform boundary commutator
  and history-tail estimates.
- All-shape exhaustion Cauchy, Lie--Trotter convergence and common alpha.
- OS/KMS/GNS identification, sector coercivity, phase selection,
  physical-empty comparison, continuum passage and Yang--Mills inputs.

## Adversarial review

- **Arbitrary finite box versus thermodynamic limit — UPHELD:** the Lean
  implication is local finite combinatorics; no volume limit is inferred.
- **Matching versus full graph — UPHELD:** incidence is bounded per colour;
  the full graph can have degree six.
- **Endpoint convention — UPHELD:** upper-endpoint parity is rejected by the
  hostile lane.
- **Empty layers — UPHELD:** removing empty slots is rejected as a contract
  change.
- **Combinatorics versus operator theory — UPHELD-OPEN:** no domains,
  commutator decay, history tail or common generator is proved.
- **QFT promotion — UPHELD:** all weighted, physical, Yang--Mills and mass-gap
  flags remain false.

## Decision and boundary

`R-443` advances the pure finite combinatorial input by closing the arbitrary
finite-box axis-parity matching property.  It does not close the weighted
Q3LOCK form, any operator/common-core or history-tail gate, common alpha,
OS/KMS/GNS, physical-empty branch, `C6`, Pre-A, Sector-A, Yang--Mills dynamics
or a mass gap.  No claim tier changes and no negative result is issued.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_arbitrary_box_verify.py
lake env lean Tect/R443.lean
```
