# Formal bi-entire coefficient majorant for actual Q3 local words

## Scope

EXP-001040 controlled the actual field-dependent coefficients only on a
pointwise field window.  This checkpoint replaces that window by a formal
coefficient radius.  For a polynomial in field variables and a source
variable define

```text
||P||_(R,S) = sum |coefficient| R^(total field degree) S^(source degree).
```

This is a candidate analytic/Frechet norm on formal polynomials; `R` is not a
bound on the physical field.

## Exact local rates

The actual shifted potential coefficient tables give

```text
B_on   = g*(R^3*S + 3*R^2*S^2/2 + R*S^3 + S^4/4)
B_edge = lambda*(4*R^3*S + 7*R^2*S^2/2 + 3*R*S^3/2 + S^4/4)
B_bond = c*(2*R*S + S^2/2).
```

For the fixture `g=3/5`, `lambda=2/7`, `c=2/3`, `R=1/2`, `S=1/3`,

```text
B_on = 17/270,  B_edge = 191/2268,  B_bond = 7/27,
C(R,S) = B_on + 3*B_edge + 6*B_bond = 7073/3780,
t*C(R,S) = 7073/18900  (t=1/5).
```

The weighted coefficient l1 norm is submultiplicative.  Hence a length-`n`
local multiplication word is bounded by `C(R,S)^n`, and the factorial time
series is bounded by `exp(t*C(R,S))`.  Reversing either endpoint preserves the
same absolute norm.

## Verification

The primary SymPy lane constructs the full multivariate polynomials and checks
their coefficient tables, formal norms, endpoint reversals, product
submultiplicativity and factorial envelope.  The independent Fraction lane
reconstructs the coefficient sums without importing the primary implementation.
Lean R223 checks the exact rational rate fixtures.

## Boundary

This removes the finite pointwise field window only at the formal polynomial
level.  It does not prove that the norm is closable or representation
independent on the Q3 CCR core, nor that it controls `q^3 A^(-3/4)`.  It also
does not supply the actual operator commutator/Duhamel history, spatial
first-passage decay, all-shape exhaustion Cauchy, common alpha, KMS,
ground/GNS gap, continuum, C6, Sector A or Pre-A.

## Adversarial review

- **Formal radius — UPHELD:** a coefficient radius is not a field cutoff or a
  physical bound.
- **Coefficient/operator lift — UPHELD:** no unbounded CCR domain theorem is
  inferred.
- **Product completion — UPHELD:** the formal l1 algebra is not silently
  identified with the physical Q3 observable algebra.
- **Orientation — UPHELD:** absolute reversal is not adjoint dynamics.
- **QFT promotion — UPHELD:** no OS/KMS, GNS, continuum or TECT claim is made.

This is a T0 claim-nonbearing checkpoint and no PDF is issued.
