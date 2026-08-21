# R-190 A1 arbitrary-polarization two-mode positivity Lean cross-check

`EXP-000905` records a T0, claim-nonbearing extension of the R-189 finite
production-cylinder diagnostic. The object is the hash-pinned A1 standalone
`F_ref`, on the side-16 one-dimensional n=1,2 cylinder

`Psi(x)=v1 cos(2 pi x/16)+v2 cos(4 pi x/16)`,

with arbitrary complex `v1,v2` in `C^3`, normalized x-average, `eta_shell=0`,
and the actual family, lock, and Class-II coefficients. This is a finite
field-space slice, not the complete A13 owner.

## 1. Exact input and quadratic margin

The A1 mass, family, and lock matrices are used without replacing them by the
historical `F_decl` convention. The family diagonal is nonnegative and
`k_lock (I-P0)` is positive semidefinite. For mode `n=1,2`, the scalar
dispersion part is

`r/4 + Z n^2 pi^2/L^2 + 4 Y n^4 pi^4/L^4`.

The 32-term Machin enclosure gives `6283/2000 < pi < 22/7`. Since `Z<0` and
`Y>0`, interval arithmetic derived from the registered inputs gives lower
bounds

`q1 >= 162860800858012247/1835008000000000000 > 1/16`,

`q2 >= 8122120422709847/114688000000000000 > 1/16`.

Dropping the nonnegative family and lock pieces is therefore conservative.

The active Class-II quadratic form has coefficients

`a=cJJ alpha_X^2/(M_X^2+rho_X)`,
`b=cJK alpha_X beta_X/(M_X^2+rho_X)`,
`c=cKK beta_X^2/(M_X^2+rho_X)`,

with the registered positive regularizer `rho_X=1e-12`. Exact arithmetic gives
`a*c-b^2 > 0`, so every `a|J|^2/2+b Re(conj(J).K)+c|K|^2/2`
is nonnegative. This is a coefficient check, not a proof of the nonlinear
Class-II owner outside this slice.

## 2. Polarization-independent moments

Put `A=||v1||^2`, `B=||v2||^2`, `C=Re <v1,v2>`, and `s=A+B`. Orthogonality of
the two cosines gives `average(rho)=s/2` and the exact quartic identity

`average(rho^2)=3(A^2+B^2)/8 + AB/2 + C^2`.

The Cauchy inequality `C^2<=AB` and a square completion imply
`average(rho^2)<=9 s^2/16`. Jensen for the nonnegative density gives
`average(rho^3)>=(average(rho))^3=s^3/8`.

Because `lambda=-43/100` and `gamma=81/50`, the full finite-slice energy obeys

`F_ref >= s/16 - (387/6400)s^2 + (27/800)s^3`.

The Lean entrypoint `Tect/R190.lean` factors this as

`s (864 s^2 - 1548 s + 1600) / 25600`.

The quadratic factor has discriminant
`-195831/40960000 < 0` and positive leading coefficient. Hence the lower
bound is strictly positive for `s>0` and zero only at `s=0`.

## 3. Cross-verification and hostile review

The primary lane derives all fractions from the A1 manifest, compiles the
pinned Lean theorem, and checks the source hashes. The independent lane uses
stdlib `Fraction` arithmetic only and does not import the primary lane. The
integrated lane checks the exploration/event topology, manifest bridges,
stored-scope boundaries, Lean escape absence, source hashes, and eight hostile
mutations: coefficient drift, `eta_shell`/`F_decl` substitution, weakened
Machin or quadratic target, dropped PSD pieces, indefinite Class-II form,
weakened moment bounds, premature A13 gate closure, and Lean escape tokens.

A successful Lean check proves only the rational cubic proposition encoded in
`R190.lean`; the field moment and Class-II bridges remain explicit hypotheses
of this finite diagnostic and are independently derived in the Python lanes.

## 4. Boundary

R-190 does not prove arbitrary-spectrum positivity, the complete heat/root/
forest/complement/returned-low/source/sextic production owner, a controlled-
shell one-use estimate, progressive/revisit uniformity, A13/T-050, Nelson,
an interacting measure, physical-empty comparison, Sector-A, Pre-A, or any
continuum/thermodynamic limit. No gate closes, no tier changes, no negative
result is registered. No R-190 PDF is issued.

<a id="exact-cubic-positivity"></a>
