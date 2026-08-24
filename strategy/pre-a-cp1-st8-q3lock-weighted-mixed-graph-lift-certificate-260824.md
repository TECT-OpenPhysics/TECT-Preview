# Conditional R-167 weighted-energy lift for mixed Q3 graph monomials

**Exploration:** `EXP-001045`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` (T0, claim-nonbearing)

## Input theorem and scalar lift

Use the registered R-167 input on a finite common core:

`U_f >= gamma sum_x f_x |q_x|^4`, `A=1+E_f >= 1`, and
`||U_f^theta A^(-theta)|| <= kappa^theta` for `0<=theta<=1`, together with
the adjoint orientation.  For `m=i+j<=3`, put

`x=f_u^(1/4)|q_u|` and `y=f_v^(1/4)|q_v|`.

The binomial expansion gives the exact scalar inequality

`(x^i y^j)^4 <= (x^4+y^4)^m`.

Therefore, by multiplication-operator order,

`f_u^(i/4) f_v^(j/4)|q_u|^i|q_v|^j`
`<= (f_u|q_u|^4+f_v|q_v|^4)^(m/4)`
`<= gamma^(-m/4) U_f^(m/4)`.

Multiplying on the right by `A^(-3/4)` and using

`U_f^(m/4)A^(-3/4)`
`=(U_f^(m/4)A^(-m/4))A^(-(3-m)/4)`

gives the conditional mixed bound

`||q_u^i q_v^j A^(-3/4)||`
`<= f_u^(-i/4)f_v^(-j/4) gamma^(-m/4)kappa^(m/4)`.

The adjoint orientation follows from the corresponding R-167 adjoint graph
input.  The spatial weight factors remain explicit and are not discarded.

## Exact fixture

Take `gamma=1/128`, `kappa=2`, so `(kappa/gamma)^(1/4)=4`.  Set the
source-centered edge weights to `f_u=1`, `f_v=1/16`; hence the neighbor
factor is `2` per neighbor field power.  With `lambda=2/7`, `c=2/3`, and
`S=1/4`, the independent exact lanes obtain

* source at the centered edge endpoint: `B_e=203393/3584`,
* source at the relabelled endpoint: the same `203393/3584`,
* spatial bond: `B_b=97/48`,
* one onsite, three edges and six bonds: `1382807/7168`,
* at `t=1/8`: `1382807/57344`.

The rates are larger than the unweighted EXP-001044 fixture precisely because
the neighbor weight cost is retained.

## Adversarial review

1. **Inherited theorem — UPHELD.** The lift does not independently prove
   R-167's weighted energy or Heinz--Kato hypotheses.
2. **Operator order — UPHELD.** Multiplication domination is applied to the
   vector `A^(-3/4)psi`; the remaining negative power is contractive only
   because `A>=1`.
3. **Spatial cost — UPHELD.** The factors `f_u^(-i/4)f_v^(-j/4)` remain in
   the bound, so moving-site uniformity is not claimed.
4. **Orientation — UPHELD.** Endpoint relabelling and adjoint order are
   separate checks, not a hidden locality theorem.
5. **History — UPHELD.** The recurrence, factorial resummation, first passage,
   exhaustion and common alpha remain open.
6. **Lean — UPHELD.** R227 is a rational fixture cross-check, not a formal
   unbounded-operator proof.
7. **QFT promotion — UPHELD.** No KMS, OS, GNS gap, continuum, C6, Sector A,
   Pre-A or TECT production result follows.

## Decision

`EXP-001045` is advanced as a conditional T0 weighted mixed graph lift.  It
removes the independent mixed-table hypothesis from EXP-001044 only under
R-167's weighted-energy theorem and exposes the exact spatial weight cost.
The next obligation is the actual two-orientation history recurrence with that
cost retained.
