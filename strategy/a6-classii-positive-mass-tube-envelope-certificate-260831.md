# R-466 finite positive-mass tube lower-bound interface certificate

## Role and method preservation

R-466 is an additive finite interface in the existing A6 branch-aware route.
It does not replace the A1/A6/A7 functional, the T-054 forward owner order, the
T-059/T-061 observation-first lane, or any promotion firewall. It turns the
positive-mass-tube prerequisite named by R-464/R-465 into an explicit
inequality with auditable owner fields.

## Exact conditional statement

At a fixed spectral cutoff `N`, let `m=(2N+1)^3`, `d=6m`, and retain the
R-464/R-465 comparison

```text
F_N(z) >= a_N ||z||^6 - K,
a_N = gamma*V/(12*m^3).
```

The resulting radial comparison gives an upper envelope `Z_upper_N(beta)` for
the actual finite partition function. Let a later owner supply a measurable
box-like branch tube

```text
B_N(c,delta) = c + [-delta,delta]^d,
```

with `delta>0` and an energy ceiling `F_N(z)<=E_tube` on that tube. Its
Lebesgue volume is exactly `(2*delta)^d`, so the unmodified finite Gibbs law
satisfies

```text
mu_N(B_N) >= (2*delta)^d * exp(-beta*E_tube) / Z_upper_N(beta).
```

In log form the auditable lower-bound budget is

```text
L_N(beta) = d*log(2*delta) - beta*E_tube - log(Z_upper_N(beta)).
```

The condition needed for a nonvanishing branch mass is therefore a separate
uniformity requirement such as `liminf_N L_N(beta)>-infinity`. R-466 does not
assert that condition.

## Audit fixtures and result

The primary and independent lanes use the same declared owner-neutral fixtures
`delta=1/16` and `E_tube=1` only to exercise the formula over cutoffs
`[1,2,3,4,6,8,10]` and beta `[1/2,1,2]`. They do not claim that this box is an
active branch, that its ceiling is valid for the A1 field, or that it is a
source-owned physical tube. The coarse log lower bound is finite and strictly
decreases with the cutoff in every fixture row; this exposes the entropy and
normalization cost that a later branch-relative estimate must overcome.

## Adversarial review

* **Volume exponent:** the box volume is `(2*delta)^d`; dropping one real
  coordinate is rejected.
* **Half-width versus side:** replacing `2*delta` by `delta` is rejected.
* **Boltzmann factor:** omitting `beta*E_tube` is rejected.
* **Partition direction:** the lower tube numerator and upper partition
  denominator have the displayed directions; reversing them is rejected.
* **Source ownership:** the fixture is explicitly owner-neutral, so it cannot
  be relabelled as an admitted active branch.
* **Uniformity:** finite decreasing rows are not a uniform positive-mass
  theorem; the required `liminf` condition remains open.
* **Null branch:** an exact zero-Lebesgue-mass branch is not conditionable by
  this box inequality.
* **Method scope:** the result is a conditional consequence of R-464/R-465 and
  leaves all existing methods and owner order unchanged.

## Boundary and next gate

R-466 proves only a fixed-cutoff conditional lower-bound interface. It does not
provide the source-owned active embedding, an actual A1 energy ceiling, a
correlated partition asymptotic, an entropy/Jacobian compensator, cutoff or
volume uniformity, tightness, floor removal, a continuum limit, physical branch
selection, QFT/Yang--Mills correspondence, or a mass gap. The next gate is to
obtain and hash-pin those owner fields, then instantiate this inequality with
the R-463 metric. If the owner fields cannot be supplied, retain R-466 as an
explicit finite boundary and do not repeat the same finite proxy.
