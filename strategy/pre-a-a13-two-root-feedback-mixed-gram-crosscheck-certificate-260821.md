# R-181 certificate: finite two-root feedback mixed-Gram Lean cross-check

## 1. Status and owner

R-181 / EXP-000896 is a T0 claim-nonbearing Lean cross-check of the actual
R-177 two-root incidence.  It closes no A13, Sector-A, T-050, physical-empty,
or Pre-A gate.

## 2. Exact finite operator

The registered owner order is `common_heat -> root_1 -> root_2 ->
future_residual`.  The actual R-177 feedback gain is `beta=1/2`, so the
finite owner-coordinate map is

`T(x,y)=(x,x/2+y)`.

With the Euclidean source norm, Lean proves

`T^T T = [[5/4,1/2],[1/2,1]]`,

and the exact defect identity

`2*(x^2+y^2) - (x^2+(x/2+y)^2) = (y-x/2)^2 + x^2/2`.

Consequently the finite envelope is strict off the zero vector, while its
constant `2` is the declared one-use bound.  The fixture `(x,y)=(1,2)` has
source norm `5`, output norm `29/4`, and defect `11/4`.

## 3. Verification lanes

The primary lane derives the matrix, Gram, defect, and fixture from the
registered R-177/R-176 inputs and compiles the pinned Lean entrypoint.  The
independent lane uses only the Python standard library and exact `Fraction`
arithmetic.  The integrated lane checks source hashes, theorem markers,
absence of Lean escape tokens, standard-library independence, derived-value
agreement, eight hostile mutations, and formal append-only topology.

## 4. Adversarial review

* The finite Gram is not the A1 production spatial mixed Gram.  UPHELD; the
  owner-coordinate boundary is explicit.
* A finite feedback envelope does not prove the source/sextic one-use ledger,
  the R-125 forest/variance owner, or the finite collar.  UPHELD; those remain
  separate obligations.
* The shared heat and retained root-1 term must not be charged twice or erased.
  UPHELD; the incidence order and mutation suite bind both facts.
* A kernel-checked algebraic lemma does not establish any regulator, matching,
  thermodynamic, continuum, physical-empty, Sector-A, or Pre-A conclusion.
  UPHELD as the release boundary.

## 5. Reusable conclusion and boundary

R-181 supplies the exact finite feedback block required by the next complete
owner construction: `T^T T` and its positive defect are now mechanically
auditable. It is not a proof of the production response or of A13. R-102,
R-125, R-063, source/sextic one-use, finite collar, T-050, matching, the
absolute anchor, Nelson, interacting measure, physical-empty comparison,
removal, continuum limits, Sector-A, and Pre-A remain open. No R-181 PDF is
issued.

<a id="feedback-mixed-gram"></a>
