# Field-window actual-Q3 word-majorant certificate

## Scope

This checkpoint keeps the field variables rather than setting them to zero,
but restricts every active local coordinate to a declared window
`|q|,|v|,|r| <= Q` and every source amplitude to `|a| <= S`.  It is a scalar
coefficient statement for local multiplication words, not an operator-domain
or thermodynamic theorem.

## Exact coefficient envelope

For the canonical local potential differences, the source coefficients are

```text
onsite:  g*(q^3, -3*q^2/2, q, -1/4),
edge:    lambda*(q^3-3*q^2*v/2+q*v^2-v^3/2,
                 -3*q^2/2+3*q*v/2-v^2/2, q-v, -1/4),
bond:    (c*(q-r), -c/2).
```

The triangle inequality on the field window gives

```text
B_on  = g*(Q^3*S + 3*Q^2*S^2/2 + Q*S^3 + S^4/4)
B_edge= lambda*(4*Q^3*S + 7*Q^2*S^2/2 + 3*Q*S^3/2 + S^4/4)
B_bond= c*(2*Q*S + S^2/2)
B(Q,S)=B_on + 3*B_edge + 6*B_bond.
```

For `g=3/5`, `lambda=2/7`, `c=2/3`, `Q=3/2`, `S=1/2`, the exact fixture is

```text
B_on = 105/64,  B_edge = 577/224,  B_bond = 13/12,
B(Q,S) = 7109/448,  t*B(Q,S) = 7109/1344  (t=1/3).
```

The coefficient l1 norm is submultiplicative.  Therefore a length-`n` local
word is bounded by `B(Q,S)^n`, and the factorial time series is bounded by
`exp(t*B(Q,S))`.  Reversing an edge or bond endpoint gives the same absolute
bound.

## Verification

The primary SymPy lane checks the exact source tables, the window inequalities
on a five-point rational grid, both orientations, and the factorial envelope.
The independent Fraction lane reconstructs the tables without importing the
primary implementation.  Lean R222 checks the rational coefficient and rate
fixtures.

## Boundary

The result is uniform in the declared finite field window only.  Its leading
growth is `B(Q,S)=O(Q^3)` for fixed `S`, so it does not remove the field window
or establish `q^3 A^(-3/4)` boundedness.  It does not prove repeated operator
commutator/Duhamel histories, spatial first-passage decay, exhaustion Cauchy,
common alpha, KMS, ground/GNS gap, continuum, C6, Sector A or Pre-A.

## Adversarial review

- **Window removal — UPHELD:** no energy or state weight has been silently
  substituted for `Q`.
- **Coefficient/operator lift — UPHELD:** polynomial coefficient l1 control is
  not an unbounded CCR operator estimate.
- **Choice count — UPHELD:** ten local choices is a bounded-degree envelope,
  not a support-growth theorem.
- **Orientation — UPHELD:** absolute reversal symmetry is not adjoint dynamics.
- **QFT promotion — UPHELD:** no OS/KMS, GNS, continuum or physical claim is
  promoted.

This is a T0 claim-nonbearing finite interface and no PDF is issued.
