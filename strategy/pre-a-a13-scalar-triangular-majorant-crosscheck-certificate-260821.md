# R-180 certificate: scalar triangular majorant Lean cross-check

## 1. Status and owner

R-180 / EXP-000895 is a T0 claim-nonbearing Lean cross-check for the
predictable triangular scalar majorant used by R-140.  The current A13 and
Sector-A gates remain open.  This certificate does not promote the R-140
conditional theorem to a production theorem.

## 2. Exact kernel content

`verification/lean/Tect/R180.lean` proves the finite geometric identity
`(1-r) sum_(i<n) r^i = 1-r^n`, nonnegativity and the upper geometric bound
for `0<=r<1`, positivity of the closed C=5 majorant under
`0<u<1`, `0<v<u`, `1<q`, and `0<rho<1`, and the exact fixture
`near=8/3`, `far_high=6`, `H5=26/3`, `sum_(i<4) (1/2)^i=15/8`.
It also proves the registered production exponent margins
`(7/5)/2-7/12=7/60` and `2/3-7/12=1/12`.

The Lean file contains no `sorry`, `admit`, `axiom`, or `unsafe`.  Its
hypotheses are explicit: the kernel check does not silently construct the
missing production mixed-Gram operator.

## 3. Independent and integrated checks

The primary lane derives all rational fixture values and exponent margins
from the manifest and compiles the pinned Lean source.  The independent lane
uses only the Python standard library and `Fraction`; it does not import the
primary lane, SymPy, or Lean.  The integrated verifier checks source hashes,
Lean theorem markers and escape tokens, independent imports, derived-value
agreement, eight hostile mutations, formal event/result topology and stored
child freshness.

## 4. Adversarial review

* A positive scalar majorant is not an owner-complete production estimate.
  This objection is upheld as a scope boundary.
* The exponent margins do not prove the R-102 conditional factorisation or
  the finite-collar constant.  This objection is upheld; those are the next
  analytic obligations.
* A finite geometric fixture cannot certify a cutoff or refinement limit.
  This objection is upheld; no limit statement is imported.
* The R-125 variance rebate cannot be spent a second time as a source reserve.
  This is retained as an explicit boundary and is checked by the predecessor
  R-179 owner-half ledger.

## 5. Reusable conclusion and boundary

R-180 makes the scalar summation step mechanically auditable and confirms
that the registered exponent gaps are strictly positive.  It does not prove
the production mixed-Gram envelope, source/sextic one-use, finite-collar
headroom, matching, absolute anchor, T-050, A13, Nelson, an interacting
measure, physical-empty, Sector-A, Pre-A, or any continuum/thermodynamic
limit.  No R-180 PDF is issued.
