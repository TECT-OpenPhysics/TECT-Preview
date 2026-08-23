# EXP-001025 certificate: finite non-Leibniz energy-product envelope

## Finding

The finite positive control

\[
 K=\operatorname{diag}(1,4,9,16),\qquad K^{1/2}=\operatorname{diag}(1,2,3,4)
\]

supports the four discrete energy contexts

\[
 M_{a,b}(A)=\|K^a A K^{-b}\|_\infty,
 \qquad a,b\in\{0,\tfrac12\}.
\]

For an intermediate context `c`, exact insertion gives

\[
 K^aABK^{-b}=(K^aAK^{-c})(K^cBK^{-b}),
\]

and the induced matrix infinity norm is submultiplicative.  If a unitary bond
`B` and `B*` have ordinary norm at most one and both half-weighted endpoint
norms at most `G`, then the four contexts satisfy

\[
 M_{a,b}(B^*AB)\le G^{2a+2b}M_{a,b}(A).
\]

With `G^2 <= 1+C delta`, six matching layers and `N` split steps have factor

\[
 (1+C T/N)^{6N(a+b)}\le \exp(6CT(a+b)),
\]

which is independent of finite-box volume.  Primary and independent lanes
pass 37/37 and 34/34; the integrated reader passes 27/27 and Lean R209
compiles.

## Exact locality separation

The energy envelope is not a Lieb--Robinson estimate.  Take `K=I` on an
eight-dimensional cyclic-shift representation, `X=E_00`, and
`Y_d=E_(d,d+1)` with `d=3`.  Initially `[X,Y_d]=0`.  After the shift sends
`X` to `E_dd`, the commutator has induced norm one.  All energy contexts of
the shift remain unchanged.  Therefore an energy-product envelope controls
operator growth but supplies no spatial first-passage decay by itself.

## QFT boundary and decision

This is an advanced T0 claim-nonbearing algebraic checkpoint.  It closes a
finite non-Leibniz product subgate after EXP-001024 and fixes a necessary
separation: the actual Q3 first-passage/boundary estimate is independent.
It does not prove unbounded-domain closure, spatial commutator decay,
all-shape exhaustion Cauchy, a common `C*` alpha, KMS identification,
ground/GNS gap, continuum, C6, Sector A, Pre-A or the canonical TECT
production owner.  The next target is the two-sided first-passage response
estimate, with an exact obstruction recorded if branch/repeat resummation
fails.

## Adversarial review

- **Finite matrices to unbounded operators — UPHELD:** no form closure or
  domain theorem is inferred.
- **Proxy norm to physical topology — UPHELD:** the induced infinity norm is
  only a finite algebraic model.
- **Envelope to locality — UPHELD:** the cyclic-shift fixture gives an order-one
  distant commutator with unchanged energy seminorms.
- **Split product to thermodynamic limit — UPHELD:** volume independence does
  not imply exhaustion summability or generator identification.
- **Lean promotion — UPHELD:** R209 checks context algebra only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production map is present.
