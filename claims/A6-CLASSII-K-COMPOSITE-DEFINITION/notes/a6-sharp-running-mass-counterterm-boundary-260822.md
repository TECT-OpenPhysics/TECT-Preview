# A6 sharp running-mass counterterm boundary

## Scope

This note is a T0, claim-nonbearing cross-check of the fixed-floor A6
Fierz algebra. It uses the hash-pinned A1 production coefficients and the
exact `W_eps` identity already recorded by the A6 composite claim. It is not
a renormalised-energy or Gibbs-measure construction.

## Exact statement

Write

```text
s = |Psi_1|^2 + |Psi_2|^2,
rho = s + |Psi_3|^2,
g = a + 2*b + c,
W_eps = 9*g*s - 6*b*s^2/(rho+eps)
        - 3*c*s^2*(rho+2*eps)/(rho+eps)^2.
```

For a running relevant coefficient `h`, set `D_h = h*s-W_eps`. On the
registered production scope `b>0` and `c>0`. The exact threshold

```text
h_min = 9*(a+2*b+c)
```

gives

```text
D_h_min = 6*b*s^2/(rho+eps)
          + 3*c*s^2*(rho+2*eps)/(rho+eps)^2 >= 0.
```

If `h<h_min`, keep any fixed `s>0` and let `|Psi_3|^2` grow. The rational
terms vanish relative to `s`, so `D_h/s -> h-h_min<0`; no smaller coefficient
can dominate the leading contraction on all fields. At the threshold,
however, `D_h_min/s -> 0` along the same third-component escape. Thus the
minimal repair is pointwise nonnegative but not uniformly coercive in the
first-doublet variable.

## Verification

`verification/lean/Tect/R194.lean` proves the exact endpoint identity and
nonnegativity under `b,c>=0`, and checks a pinned rational witness for a
sub-threshold coefficient. The primary Fraction lane derives `a,b,c` from
the A1 manifest, checks the identity on exact rational samples, checks the
sub-threshold witness, and verifies the decreasing escape ratio. The
non-importing independent lane repeats the derivation without importing the
primary module. The integrated lane checks source hashes, Lean compilation,
child agreement, hostile mutations and the no-overclaim boundary.

## Boundary

The result does not prove a full coefficient trajectory, spatially
correlated partition control, tightness, full-field bare concentration, a
Gibbs measure, floor removal, infinite volume, a phase transition, BCC,
physical-empty ordering, Sector-A or Pre-A closure. The A6 counterterm and
full-field concentration gates remain OPEN.

No PDF is issued for this intermediate route boundary.
