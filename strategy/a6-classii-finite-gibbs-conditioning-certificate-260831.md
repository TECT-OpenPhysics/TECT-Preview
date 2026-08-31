# R-464 finite-cutoff Gibbs integrability and branch-conditioning certificate

## Role

R-464 is an additive finite-dimensional prerequisite for the existing A6
branch-aware concentration route. It keeps the A1 reference functional, the
T-054 forward owner order, and the T-059/T-061 observation-first inverse lane
unchanged. It does not replace the R-461 null-branch dichotomy or the R-463
active tube metric.

## Exact conditional statement

Let `m=(2N+1)^3` be the number of sites in a finite spectral Galerkin
realisation of the pinned A1 functional, and let `rho_x>=0` denote the local
three-component squared amplitude. The A1 quadratic symbol obeys

```text
K(k) >= mu2 = r - Z^2/(4Y) > 0.
```

The Class-II quadratic form, family term, and lock term are nonnegative. With
the pinned `lambda=-ell<=0` and `gamma>0`, the local radial polynomial obeys

```text
p(t) = mu2*t/2 - ell*t^2/4 + gamma*t^3/6
     >= gamma*t^3/12 - C,
T = 3*ell/gamma,  C = ell*T^2/4,  t>=0.
```

Using `sum_x rho_x^3 >= (sum_x rho_x)^3/m^2`, the finite-cutoff energy has
the coercive comparison

```text
F_N(z) >= [gamma*V/(12*m^3)]*||z||_2^6 - C*V.
```

Therefore the ordinary finite-dimensional Lebesgue Gibbs integral is finite
for every `beta>0` at each fixed cutoff. The radial comparison uses the
standard finite-dimensional formula

```text
integral exp(-a*||z||^6) dz
  = pi^(d/2)*Gamma(d/6)/(3*Gamma(d/2))*a^(-d/6).
```

This is a finite-cutoff existence result only. The coefficient decays with
the number of sites, so it is not a uniform cutoff estimate.

## Branch-conditioning firewall

An exact pure-singlet branch sets the first two complex components to zero at
every site. It has real codimension `4*m` in the ambient `6*m` coordinates and
therefore zero Lebesgue Gibbs mass. It cannot be conditioned on by division by
its mass. A branch-conditioned measure must instead use a measurable tube
`B_{b,N}(delta)` with a separately proved positive mass:

```text
mu_N(A | B) = mu_N(A intersect B) / mu_N(B),  mu_N(B)>0.
```

R-464 does not assert that the active null branch has zero mass; its tube
definition and quantitative mass remain owner inputs. This distinction is the
required bridge from the pathwise R-461/R-463 geometry to a genuine Gibbs
calculation.

## Evidence and limits

The primary and non-importing independent implementations use exact decimal
rational arithmetic, finite-cutoff norm bridges, a dense polynomial sweep,
and explicit codimension rows. Eight hostile mutations reject sign removal,
loss of the spectral lower bound, deletion of the sextic term, illegal exact
branch conditioning, and premature probability/uniformity promotion. Lean
R464 checks the two-branch polynomial inequality, the positive codimension,
and the positive-mass conditional ratio bound.

The evidence level is T0 exact finite-dimensional integrability and
conditioning prerequisite. It does not compute any correlated field Gibbs
tube probability, entropy density, partition asymptotic, tightness, floor
removal, continuum limit, physical branch, QFT/Yang--Mills correspondence, or
mass gap. The established T-054, T-059, and T-061 methods and owner order are
unchanged.

## Next gate

A source-owned branch map must provide a positive-mass tube and its correlated
finite-cutoff probability. Only then may the R-463 active metric enter a
quantitative branch estimate. If the tube mass or entropy grows without a
cutoff-uniform compensator, retain R-464 as a finite prerequisite and record
the branch-specific obstruction rather than promoting the result.
