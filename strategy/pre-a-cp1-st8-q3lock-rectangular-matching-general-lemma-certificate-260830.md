# General rectangular axis-parity matching lemma

**Result:** `R-442`  
**Exploration:** `EXP-001287`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Exact finite scope

The audit fixes the three-dimensional nearest-neighbour graph on every ordered
rectangular side triple in `[2,6]^3` (125 boxes).  Vertices are integer
coordinate vectors.  An edge is a single-coordinate increment and is stored
with its unique lower endpoint.  Its colour is
`(axis, lower_endpoint_coordinate mod 2)`, so six colour slots are retained,
including empty slots.

For a box with sides `s_0,s_1,s_2`, the executable edge count is recomputed as

```
sum_axis ((s_axis - 1) * product_other_axes s_other)
```

The local incidence statement is checked independently in Python and proved
in Lean: at a fixed vertex and axis the only possible lower endpoints are the
forward and backward candidates, whose coordinates differ by one and hence
cannot have the same parity.  Therefore each colour layer has incidence at
most one at every vertex.

## Executed evidence

- Primary all-box enumeration: `67,398/67,398` assertions.
- Non-importing coordinate-index reconstruction: `67,268/67,268` assertions.
- Hostile contract firewall: `8/8` mutations rejected.
- Integrated verifier: `26/26` assertions.
- Lean `R442`: PASS (`same_colour_incident_unique` and
  `six_colour_layers`).

Across the 125 boxes the sweep totals 8,000 vertices and 18,000 edges, with
six retained layers, maximum graph degree six, and 75 empty layer slots counted
across the family.  These totals are bookkeeping aggregates, not asymptotic
or thermodynamic estimates.

## Assumptions

1. The graph is the finite integer rectangular nearest-neighbour graph stated
   above, with side lengths at least two.
2. Every edge has one lower endpoint and one axis; no diagonal or periodic
   edges are included.
3. Colours use the lower endpoint coordinate modulo two; empty colour slots
   remain part of the declared layer family.
4. The Lean proposition is an abstract incidence/parity lemma and does not
   define the Q3LOCK Hamiltonian, a representation, a state, or a limit.
5. The range `[2,6]^3` is exhaustive only for this executable finite sweep.

## Missing assumptions and open gates

- An analytic arbitrary-box edge-colouring theorem connected to the full
  weighted Q3LOCK interaction.
- Representation-independent common cores and weighted product-domain
  estimates for the layer subflows.
- Cutoff-, source-, phase-, volume- and exhaustion-uniform boundary
  commutator and history-tail bounds.
- All-shape exhaustion Cauchy, Lie--Trotter convergence and a common alpha.
- Hamiltonian-to-OS/KMS/GNS identification, sector coercivity and phase
  selection.

## Adversarial review

- **Finite sweep versus universal theorem — UPHELD:** the Python quantifier is
  exactly the 125 boxes in `[2,6]^3`; no arbitrary-volume conclusion is drawn.
- **Layer versus full graph — UPHELD:** matching is asserted per colour; the
  full graph reaches degree six and is not one matching.
- **Lower versus upper endpoint — UPHELD:** the hostile lane rejects changing
  the declared lower-endpoint colour rule.
- **Empty-slot handling — UPHELD:** dropping empty layers changes the declared
  six-slot contract and is rejected.
- **Combinatorics versus operator theory — UPHELD:** neither Python nor Lean
  supplies domains, self-adjointness, boundary decay, or a common generator.
- **QFT promotion — UPHELD:** no physical sector, continuum limit,
  Yang--Mills statement, or mass-gap statement is admitted.

## Decision and boundary

`R-442` is an advanced T0 claim-nonbearing finite combinatorial checkpoint. It
removes the finite rectangular matching bookkeeping gap left by `R-440` and
provides a reusable local lemma, while the analytic Q3LOCK history/common-core
route remains open. No claim tier changes and no negative result is issued.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_general_lemma_verify.py
lake env lean Tect/R442.lean
```

## Non-claims

This result does not establish a Q3LOCK weighted operator, Friedrichs domain,
common core, boundary/history-tail estimate, exhaustion limit, common alpha,
OS/KMS/GNS reconstruction, physical-empty comparison, broken-sector gap,
continuum limit, `C6`, Pre-A, Sector-A, Yang--Mills dynamics, or a mass gap.
