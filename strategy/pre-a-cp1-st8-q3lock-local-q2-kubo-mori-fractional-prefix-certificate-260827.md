# R-368 local Kubo-Mori weighted fractional shell certificate

## Result-first boundary

R-368 is a T0, claim-nonbearing finite result under EXP-001210.  It tests a
local Gibbs Kubo-Mori/Dirichlet topology on the doubled bond generator and
retains every split prefix.  The weighted finite bound is useful evidence for
the next theorem, but it is not a regulator-uniform estimate.

## 1. New perspective

R-367 measured an unweighted fractional Liouvillian norm and saw a finite
`V=2,d=6` value of `69.908699`.  R-368 asks whether that growth is a norm
artifact by inserting the Kubo-Mori logarithmic mean of local doubled-bond
Gibbs weights.  For bond eigenvalues `lambda_i`,

`p_i = exp(-beta*(lambda_i-min lambda))/sum_j exp(-beta*(lambda_j-min lambda))`,

`L_ij=(p_i-p_j)/(log p_i-log p_j)` with diagonal limit `L_ii=p_i`, and the
theta-half weighted shell is

`N_L(X)^2 = 2*sum_ij L_ij*|lambda_i-lambda_j|*|Xhat_ij|^2`.

The phase inequality `min(4,y^2)<=2*|y|` gives the finite weighted bound
`C_L <= 2^(1-theta)*|t/hbar|^theta*N_L` at `theta=1/2`.

## 2. Verification

The actual-Q3 fixture uses `V=2`, cutoffs `d=3,4,5,6`, and `V=4` on the
square graph at `d=2`, with both beta values, split orientations, time signs,
history adjoints, sites, and every prefix position from zero through full.
The primary and non-importing independent lanes each pass `4636/4636`
assertions over `656` contexts.  The integrated verifier passes `65/65`, and
Lean R368 compiles without forbidden declarations.  The largest numerical
difference between lanes is `1.705e-13`.

The maximum local Kubo-Mori weighted fractional norm is `1.208758407679001`,
with weighted finite-time bound `0.4029194692263337` and largest
finite-time-to-bound ratio `0.3868613066541026`.  The corresponding unweighted
maximum is `69.90869910391245`; the largest arithmetic-to-Kubo fractional
ratio is `1.7169449837129835`.  The smallest recorded Kubo weight is positive
at `3.6452675812342155e-14`, and the maximum symmetry residual is zero at the
reported precision.

## 3. Adversarial review

1. **Weight choice.**  The Gibbs weights are those of the doubled local bond
   generator, not the full interacting Hamiltonian.  This is stated as a
   local proxy and is not promoted to a global KMS state.
2. **Diagonal logarithmic mean.**  Equal probabilities use the arithmetic
   limit, and positivity/symmetry are checked in both executable lanes.
3. **Prefix completeness.**  Every position in both forward and reverse
   split orders is evaluated; no selected-prefix shortcut remains.
4. **Cutoff and volume.**  The finite `d=3..6` and `V=4,d=2` table cannot prove
   a supremum over regulators, graph shapes, sources, or volumes.
5. **Phase algebra.**  The matrix coefficient identity is checked directly
   against the doubled unitary, while Lean proves only the scalar envelope
   and weight conventions.
6. **QFT promotion.**  A local modular comparison, common core, common alpha,
   OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain
   open.

## 4. Next gate

Use this weighted table to formulate an analytic local Dirichlet comparison
with a cutoff-independent weight and then test source translations and
exhaustion shapes.  If the weighted norm grows in an enlarged family, record a
rigorous lower-growth obstruction rather than treating the finite suppression
as a uniform theorem.  No R-368 PDF is issued.

