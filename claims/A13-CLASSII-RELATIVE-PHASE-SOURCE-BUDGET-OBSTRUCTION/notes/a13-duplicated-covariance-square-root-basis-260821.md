# R-175 note: duplicated covariance square-root basis

This note records the exact interface needed after R-174. For a supplied
square-root witness `L L^T=C`, the duplicated basis `G=diag(L,L)` satisfies
`G G^T=diag(C,C)`. The same duplicated basis commutes with the realification
complex structure `J=[[0,-I],[I,0]]`, so phase rotations `cI+sJ` can be moved
through `G` without selecting an internal gauge.

The result is deliberately an interface lemma. The actual A1 covariance
matrices contain the registered kinetic symbol and family-lock matrix; R-175
does not claim that the supplied lower-triangular fixture is their square root.
The next proof step must supply and hash the actual two roots, then add heat,
root, complement, low, forest and returned-mean data before the complete scalar
action is differentiated.

The exact theorem is Lean-checked over arbitrary finite index types and
commutative rings, and independently rebuilt with Fraction matrix arithmetic.
No A13/T-050, physical-vacuum, Sector-A or Pre-A conclusion follows.
