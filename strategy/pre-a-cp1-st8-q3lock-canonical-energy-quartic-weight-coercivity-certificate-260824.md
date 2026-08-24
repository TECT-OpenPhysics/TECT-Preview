# EXP-001057 / canonical Q3 energy--quartic weight coercivity

## Finding

This checkpoint connects the finite-volume multiplication interface from
EXP-001055 to the actual canonical ST8/Q3LOCK Hamiltonian form.  For

\[
u(q)=\frac r2q^2+\frac g4q^4,\qquad r<0,
\]

completion of the square gives

\[
u(q)+\frac{r^2}{4g}=\frac g4\left(q^2+\frac r g\right)^2.
\]

The elementary square remainder

\[
2\left(q^2+\frac r g\right)^2+2\left(\frac r g\right)^2-q^4
 =\left(q^2+\frac{2r}{g}\right)^2\ge 0
\]

therefore yields, for a finite volume with `n` sites,

\[
1+\sum_xq_x^4
\le 1+\frac8g\left(H_\Lambda+\frac{n r^2}{2g}\right).
\]

Only the nonnegativity of the kinetic, spatial quadratic, and Q3 edge terms
is used.  The exact extensive shift is part of the statement; it is not
absorbed into a claimed volume-uniform constant.

For the registered fixture `g=3/5`, `r=-9/2`, `chi=1`, `c=1`, and
`lambda=1/10`, the derived values are `v^2=15/2`, shift per site `135/8`,
and weight coefficient `8/g=40/3`.

## Verification

- Primary exact SymPy lane: 284/284.
- Independent Fraction lane: 289/289.
- Integrated verifier: 22/22; Lean R239 compiles.
- Lean checks exact rational shift, coefficient, completed-square fixture,
  nonnegative remainder, and the explicit scope firewall.

## Adversarial review

1. **Sign/shift:** `r<0` is retained and produces the stated extensive shift.
   UPHELD.
2. **Coefficient:** `8/g` is derived from the square remainder, not pasted.
   UPHELD.
3. **Positive interactions:** kinetic, spatial, and Q3 edge terms enter only
   through nonnegativity.  UPHELD.
4. **Volume:** the shift scales with `n`; no unshifted uniform bound is
   claimed.  UPHELD.
5. **Domain:** this is a finite form-core inequality, not a self-adjoint
   thermodynamic domain theorem.  UPHELD.
6. **Lean:** R239 checks arithmetic fixtures only, not unbounded operator
   closure.  UPHELD.
7. **QFT promotion:** no Duhamel locality, OS identification, KMS/GNS gap,
   continuum, C6, Sector A, or Pre-A closure follows.  UPHELD.
8. **TECT owner:** no `heat_root_incidence` or A1/R-192 production owner is
   supplied.  UPHELD.

## Boundary and next gate

This is a claim-nonbearing T0 QFT-facing energy interface.  The next proof
step is to insert the shifted form into a finite-volume Duhamel estimate and
test whether the extensive normalization can be made compatible with the
fixed-beta OS mixture.  The direct projected `D,delta-D` locality gate and the
Hamiltonian-to-OS thermodynamic identification remain open.
