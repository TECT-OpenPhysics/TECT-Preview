# Formal bi-entire weighted-coefficient completion and radius-loss bridge

## Scope

EXP-001041 supplied a formal bi-entire coefficient norm but left its
completion explicit only as a candidate.  This checkpoint completes the
coefficient-level construction without identifying it with an unbounded Q3
operator representation.

For nonnegative field and source degrees define

```text
A_(R,S) = { c_(m,n) : ||c||_(R,S) = sum_(m,n) |c_(m,n)| R^m S^n < infinity }.
```

The weighted coefficient map `c_(m,n) -> c_(m,n) R^m S^n` identifies this
space with weighted `l1(N^2)`.  Therefore it is complete.  Finite-support
truncations converge because their omitted weighted tail tends to zero.
The Cauchy product is the convolution on `N^2`, and Tonelli plus the triangle
inequality gives

```text
||c*d||_(R,S) <= ||c||_(R,S) ||d||_(R,S).
```

For `0<R'<R` and `0<S'<S`, the formal derivatives satisfy

```text
||D_q c||_(R',S') <= R/(R-R')^2 ||c||_(R,S),
||D_a c||_(R',S') <= S/(S-S')^2 ||c||_(R,S).
```

The constants follow from `m x^(m-1) <= sum_(k>=1) k x^(k-1) =
(1-x)^(-2)` with `x=R'/R`, and the analogous source estimate.  Thus the
formal entire family has a radius-loss differential calculus.

## Exact fixture

The primary and independent lanes use `R=1/2`, `S=1/3`, `R'=1/3`, `S'=1/4`.
For the finite test polynomials

```text
p = 1 - q + a + 2 q^2 a,
q = 1 + q - a + q a^2,
```

the weighted norms are `||p||=2`, `||q||=17/9`, the product norm is `19/9`,
and the product bound is `34/9`.  The derivative fixture norms are `4/3` and
`11/9`; the radius-loss constants are `18` and `48`.

For the geometric coefficient family with ratios `1/5` and `1/7`, the full
weighted norm is `7/6`.  Total-degree truncation through degree three leaves
tail `1919/9261000 < 1/100`, with exact nonnegative monotone tails at every
preceding degree in the fixture.

## Verification

`pre_a_cp1_st8_q3lock_bientire_coefficient_completion.py` computes the finite
coefficient algebra and the geometric tail with SymPy.  The independent
`Fraction` lane reconstructs the product, derivatives, bounds, and tails
without importing the primary implementation.  The integrated verifier
passes `37/37`; Lean R224 checks the rational product, radius-loss, geometric
norm, tail, and scope fixtures.

## Boundary

This is a representation-independent completion only for the formal weighted
coefficient algebra.  It does not construct a CCR common core, prove that the
actual Q3 force maps into this completion, or establish Duhamel convergence,
six-neighbour first-passage decay, all-shape exhaustion Cauchy, common alpha,
KMS/OS reconstruction, a GNS gap, a continuum limit, C6, Sector A or Pre-A.

## Adversarial review

- **Completion meaning — UPHELD:** weighted `l1` completeness is not operator
  closure or a physical observable algebra.
- **Density — UPHELD:** the theorem uses absolute weighted summability; the
  finite geometric fixture is only a reproducible check.
- **Radius loss — UPHELD:** strict smaller radii are required; no same-radius
  unbounded derivative estimate is inferred.
- **History promotion — UPHELD:** algebra multiplication does not prove Q3
  commutator incidence, cancellation, or spatial decay.
- **Lean promotion — UPHELD:** R224 checks encoded rational identities, not the
  infinite-dimensional theorem in full generality.
- **QFT promotion — UPHELD:** no KMS, OS, GNS, continuum, C6, Sector A or
  Pre-A claim is made.

This is a T0 claim-nonbearing checkpoint and no PDF is issued.
