# R-189 certificate: A1 e3 two-mode production-cylinder positivity

## 1. Status and frozen object

R-189 / EXP-000904 is a T0, claim-nonbearing diagnostic.  It freezes the
hash-pinned standalone A1 `F_ref`, the side-16 torus, the one-dimensional
Fourier modes `n=1,2`, and the internal polarization `e3=(0,0,1)`.  The
normalization is energy density (the positive torus volume is omitted).

The shell penalty is disabled exactly as in the A1 manifest (`eta_shell=0`).
The Class-II generators act on the first two internal components, so the e3
slice has no Class-II current term.  This is a slice premise, not an assertion
about arbitrary polarization or the complete production owner.

## 2. Exact polynomial

Write `phi(x)=a cos(k x)+b cos(2 k x)` with `k=2 pi/16` and
`t=a^2`, `u=b^2`.  Period averaging gives

```
<phi^2> = (t+u)/2
<|d phi|^2> = k^2 (t+4u)/2
<|Delta phi|^2> = k^4 (t+16u)/2
<phi^4> = 3 t^2/8 + 3tu/2 + 3u^2/8
<phi^6> = 5t^3/16 + 105t^2u/32 + 45tu^2/16 + 5u^3/16.
```

Using the A1 `F_ref` nonlinear prefactors, the exact density is

```
F(t,u) = q1*t + q2*u - (129/3200)(t^2+4tu+u^2)
         + (27/320)(t^3 + (21/2)t^2u + 9tu^2 + u^3),
```

where `q1` and `q2` are derived from the A1 values `r`, the e3 family mass,
the lock factor `2/3`, `Z`, `Y`, `L=16`, and `k=2 pi/L`.  The script derives
them; no quadratic coefficient is copied from a historical solver.

## 3. Certified lower bound

A rational Machin enclosure proves `6283/2000 < pi < 22/7`.  On that interval
the derived coefficient monotonicities give `q1 > 1/10` and `q2 > 1/10`.
For `s=t+u`, `t,u>=0`,

```
t^2+4tu+u^2 <= (3/2)s^2,
t^3+(21/2)t^2u+9tu^2+u^3 >= s^3/4.
```

Therefore `F(t,u)` is bounded below by

```
P(s) = s/10 - (387/6400)s^2 + (27/1280)s^3.
```

The quadratic factor is positive because its discriminant is exactly
`-195831/40960000`; hence `P(s)>0` for `s>0` and `P(0)=0`.  The algebraic
factorization and the resulting cylinder nonnegativity are checked by the
pinned Lean entrypoint `Tect.R189`.

## 4. Adversarial review and boundary

* The result uses `F_ref`, not the mismatched historical `F_decl`; UPHELD.
* `e3` removes Class-II terms but does not control active polarizations; UPHELD.
* The two-mode cylinder is not the A13 adapted NEAR/FOREST owner; UPHELD.
* Positivity of this slice cannot prove a global minimum, a transverse
  Hessian bound, a controlled-shell one-use estimate, or a continuum result;
  UPHELD.

The A13 controlled-shell and full progressive/revisit gates remain OPEN.  No
new negative, tier change, physical-empty comparison, or R-189 PDF follows.

<a id="exact-polynomial"></a>
<a id="lean-lower-bound"></a>
