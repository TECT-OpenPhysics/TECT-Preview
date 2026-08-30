# Finite rectangular-box matching-layer split envelope

**Result:** `R-440`  
**Exploration:** `EXP-001285`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Exact finite scope

The audit fixes the three-dimensional nearest-neighbour graph, the edge colour
`(axis, lower-endpoint-coordinate mod 2)`, the rational weighted form

```
K = sum_x w_x (1 + p_x^2/(2 chi) + gamma q_x^4),
w_x = 2^(-|x-(1,1,1)|_1),
```

and the matching shear with `delta=1/7`, `coupling=3/5`, `chi=7/4`,
`sqrt_gamma=2/5` and `kappa=2`.  The five separately fixed boxes are
`(2,2,2)`, `(3,3,3)`, `(4,4,4)`, `(5,4,3)` and `(6,5,4)`.  Four declared
rational phase-space seeds, both shear signs and both layer orders are run in
every box.  Empty parity layers in the smallest box are retained as explicit
zero-edge layers rather than silently dropped.

The derived one-layer coefficient is

```
C_match = 1 + kappa*coupling^2/(2*chi*sqrt_gamma) = 53/35,
1 + C_match*|delta| = 298/245.
```

Each matching layer satisfies the declared finite energy inequality on every
tested seed and sign, and sequential application in either layer order obeys
the product bound.  The exact edge counts are 12, 54, 144, 133 and 286 for the
five boxes; every nonempty layer has incidence at most one at every vertex.
The coefficient and six-layer endpoint exponent are unchanged across the
family.  The largest observed one-layer ratio is the exact finite fraction
`4034975/3832529`.

## Verification

- Primary exact `Fraction` lane: `1152/1152`.
- Non-importing independent `Fraction` lane: `652/652`.
- Hostile mutation firewall: `10/10` rejected, including one-sided shear,
  omitted reverse order, parity/layer corruption, full-graph-as-one-layer,
  coefficient mutation and physical/QFT promotion.
- Integrated verifier: `37/37`.
- Lean `R440`: PASS.  It checks the three representative edge-count formulas,
  the six-layer count and the exact rational coefficient.

The Lean file checks scalar and counting identities only.  The graph rows and
phase-space inequalities remain finite executable evidence.

## Adversarial review

- **Finite family versus arbitrary boxes — UPHELD:** the five boxes are an
  explicit test set; no universal quantifier over all rectangles is inferred.
- **Matching versus full graph — UPHELD:** only one coloured matching is
  sheared at a time; the full graph has degree up to six.
- **Form versus operator — UPHELD:** the inherited positive shifted form and
  tensor-local self-adjoint onsite hypothesis are not reproved here.
- **Coefficient versus convergence — UPHELD:** a finite product envelope does
  not prove Lie--Trotter convergence, boundary decay or exhaustion Cauchy.
- **Lean promotion — UPHELD:** R440 does not encode unbounded operators,
  domains, states or limits.
- **QFT/TECT promotion — UPHELD:** no physical-empty reference,
  `heat_root_incidence`, canonical A1 production owner, OS/KMS/GNS
  reconstruction or Yang--Mills map is present.

## Decision and boundary

`R-440` is an advanced T0 claim-nonbearing finite rectangular-box checkpoint.
It strengthens the finite matching-layer input behind the Q3LOCK common-core
route and keeps the split coefficient volume-independent on the declared
fixtures.  It does not close an arbitrary-box theorem, an unbounded common
core, weighted product-domain transfer, boundary commutator decay, a uniform
tail modulus, all-shape exhaustion Cauchy, common alpha, phase selection,
OS/KMS/GNS identification, a sector gap, continuum, C6, Sector A, Pre-A,
Yang--Mills dynamics or a mass gap.  No claim tier changes and no negative
result is issued.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family_hostile.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_rectangular_matching_layer_family_verify.py
```

