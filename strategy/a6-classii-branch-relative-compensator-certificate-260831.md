# R-467 finite branch-relative Jacobian/entropy compensator certificate

## Role and method preservation

R-467 is an additive conditional interface downstream of R-466.  It keeps the
existing A1/A6/A7 functional, the T-054 forward owner order, the T-059/T-061
observation-first lane, and all promotion firewalls unchanged.  It does not
invent or admit a source-owned active branch.

## Exact finite statement

At a fixed cutoff `N`, let the ambient field space have `d_N` real
coordinates.  A later owner may provide an injective measurable chart
`Phi_N` with active dimension `k_N`, normal dimension `n_N`, a chart box with
side lengths `s_a,N` and `s_n,N`, and a Jacobian lower bound `J_N>0`.  Suppose
the image tube has pointwise energy `F_N <= E_N`.  Then the change-of-variables
lower bound is

```text
mu_N(Phi_N(U_N)) >=
  J_N * vol(U_N) * exp(-beta*E_N) / Z_upper_N(beta),
vol(U_N) = s_a,N^k_N * s_n,N^n_N.
```

The auditable logarithmic budget is

```text
L_branch,N(beta) =
  log(J_N) + k_N*log(s_a,N) + n_N*log(s_n,N)
  - beta*E_N - log(Z_upper_N(beta)).
```

Relative to a reference ambient box of volume `V_ref,N`, the explicit
Jacobian/entropy compensator is

```text
C_N = log(J_N * vol(U_N)) - log(V_ref,N).
```

The branch probability can be bounded away from zero only after a separate
uniform condition such as `liminf_N L_branch,N(beta)>-infinity` is proven.

## Audit fixtures and result

The primary and independent implementations use the owner-neutral fixtures
`active_side=1/8`, `normal_side=1/4`, `reference_side=1/8`, `J_min=1/2`, and
`E_tube=1`, with `k_N=2(2N+1)^3`, `n_N=d_N-k_N`, cutoffs
`[1,2,3,4,6,8,10]`, and beta `[1/2,1,2]`.  These values exercise the exact
finite formula only; they are not fitted, source-owned, or physical.

## Adversarial review

* **Dimension split:** dropping the normal coordinates is rejected by the
  exact `k_N+n_N=d_N` check.
* **Chart volume:** changing a side or corrupting the product volume is
  rejected by the exact rational identity.
* **Jacobian:** omitting the positive Jacobian factor is rejected by the log
  decomposition check.
* **Boltzmann sign:** reversing `-beta*E_N` is rejected.
* **Partition direction:** the upper comparison belongs in the denominator;
  reversing it is rejected.
* **Degenerate chart:** `J_N=0` is not a positive-volume chart and is
  rejected.
* **Source ownership:** the fixtures cannot be relabelled as a physical
  source-owned branch.
* **Uniformity:** finite rows do not prove a cutoff-uniform probability,
  entropy density, tightness, or continuum limit.

## Boundary and next gate

R-467 supplies only a finite conditional change-of-variables interface.  It
does not supply the source-owned embedding, actual Jacobian, correlated Gibbs
normalization, uniform compensator, tightness, floor removal, ordered limits,
physical-sector selection, QFT/Yang--Mills correspondence, or a mass gap.  The
next gate remains owner admission: hash-pin the actual active chart/tube and
ceiling, instantiate the R-467 budget with the R-463 metric, and then test the
branch-relative compensator.  If no owner fields arrive, retain this boundary
and keep the existing T-054, T-059, and T-061 methods parked at their current
locks rather than generating another synthetic proxy.
