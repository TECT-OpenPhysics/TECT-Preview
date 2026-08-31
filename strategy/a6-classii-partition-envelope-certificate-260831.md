# R-465 finite-cutoff partition comparison envelope certificate

## Role

R-465 is an additive T0 diagnostic for the existing A6 route. It reuses the
R-464 finite-cutoff coercive comparison and leaves the established T-054
forward lane, T-059/T-061 observation-first inverse lane, owner order, and
promotion firewalls unchanged. It is not a replacement for any of those
methods.

## Exact finite comparison

For the pinned A1 functional, R-464 supplies at fixed cutoff

```text
F_N(z) >= a_N ||z||^6 - K,
a_N = gamma*V/(12*m^3),
m = (2N+1)^3,
d = 6*m.
```

Consequently, for beta>0, the finite-dimensional radial comparison is

```text
Z_N(beta) <= exp(beta*K)
  * pi^(d/2)*Gamma(d/6)/(3*Gamma(d/2))
  * (beta*a_N)^(-d/6).
```

The script evaluates this expression in log form for the preregistered audit
cutoffs `N=[1,2,3,4,5,6,8,10,12,16,20]` and inverse temperatures
`beta=[1/2,1,2]`. These are fixed audit inputs, not fitted parameters.

The exact coefficient identity is

```text
a_N*m^3 = gamma*V/12,
```

so the coefficient decreases strictly over the declared cutoffs. The term

```text
P_N(beta) = -(d/6)*log(beta*a_N)
```

is reported as a norm-volume pressure diagnostic. It is not called an entropy
density and is not used as a uniform estimate.

## What the checks establish

The primary and non-importing independent lanes recompute the A1-derived
volume, positive spectral floor, sextic coefficient, exact `m^-3` scaling,
radial log envelope, and finite-row presence. The hostile lane rejects a sign
flip, a wrong power of `m`, a wrong coordinate dimension, omission of `beta`,
omission of the additive shift, a false cutoff-uniform assertion, relabelling
the comparison as the actual partition, and promotion of finite rows to
entropy/tightness/continuum evidence. Lean R465 checks positivity of the
coefficient, the exact scale identity, strict decrease under a cutoff increase,
and positivity after multiplication by beta.

## Assumptions

* The hash-pinned R-464 lower comparison holds at each fixed cutoff.
* The standard finite-dimensional radial integral is used only as an upper
  comparison for that lower bound.
* The declared cutoffs and beta values are audit fixtures.

## Missing assumptions and boundary

This certificate does not provide the actual correlated full-field partition
asymptotic, a positive-mass active-branch tube, a branch probability, entropy or
Jacobian control, a cutoff/volume-uniform compensator, tightness, floor removal,
or a continuum limit. It does not select a physical-empty or Reading-H branch
and does not establish Pre-A, Sector A, QFT, Yang--Mills, gravity, or a mass
gap. The `m^-3` decrease diagnoses the present comparison only; it is not a
no-go theorem for a later common norm or source-owned dynamics.

## Next gate

A source owner must supply a measurable positive-mass branch tube and its
correlated finite-cutoff probability/entropy estimate. Only then can the
R-463 active metric be inserted into a branch calculation. If no
cutoff-uniform compensator is supplied, retain R-465 as a finite boundary
diagnostic and record the obstruction rather than changing the research method
or promoting the tier.
