# PAH-OMC-014 projective-kernel obligation

## Scope

This note derives a necessary acceptance condition for the existing PAH-OMC-014
full-Q cylinder test. It does not assign sector weights, change PAH-001, or
introduce a new Gibbs model.

The parent hashes used here are:

- PAH-001: `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- PAH-OMC-012: `180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72`
- PAH-OMC-014: `1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0`

## Exact finite maps

PAH-OMC-012 defines the graded unions

`Omega_n^gr(R) = disjoint_union_Q {Q} x Omega_(n,R,Q)`

and the neutral restriction that retains the old coordinates and recomputes
the coarse grade from them. Therefore a fine state can have a fine grade
`Q_f` and a coarse grade `Q_c` with `Q_c <= Q_f`; the dropped occupation is
`Q_f-Q_c`.

For a bounded grade-blind cylinder `f`, the exact projective requirement is

`sum_Qf w_(n+1,R,Qf) pi_(n+1,R,Qf)(f o p_(n+1,n))`

`= sum_Qc w_(n,R,Qc) pi_(n,R,Qc)(f)`.

This identity must hold for every finite-support cylinder, not only for the
four R-488 coordinates.

## Kernel form of the obligation

Weights alone are sufficient only if each fine component push-forward is known
to decompose into the coarse component Gibbs family. The required additional
source-owned statement is a stochastic kernel `K_n(Qc | Qf)` such that, for
every bounded cylinder `f`,

`pi_(n+1,R,Qf)(f o p_(n+1,n))`

`= sum_Qc K_n(Qc | Qf) pi_(n,R,Qc)(f)`,

with `K_n(Qc | Qf) >= 0` and `sum_Qc K_n(Qc | Qf)=1`. Only then does the weight
recursion

`w_(n,R,Qc) = sum_Qf w_(n+1,R,Qf) K_n(Qc | Qf)`

reduce the cylinder identity to a check on sector weights. If the component
push-forward identity fails, no choice of weights alone can establish exact
projective consistency.

## Boundary and scope firewall

The R-484 hidden-diagonal defect `16/9` remains part of the component
push-forward/error accounting. It may not be averaged away or replaced by a
counterterm. R-490 `C_sw=540` remains domination-only and cannot define `K_n`.
The OMC-011 Q=1 charge-loss witness shows why a fixed-Q lift is not a
substitute: the full graded map must be used, with the grade-changing kernel
explicitly proved rather than silently resetting `Q_f` to `Q_c`.

## Disposition

PAH-OMC-012 supplies the graded domain and grade balance, but it does not
supply `K_n`, a cross-Q law, or a global probability. Thus the projective
identity and the PAH cylinder Cauchy estimate remain untestable. This is a
sharper missing-input contract, not a universal no-go: a source owner may
still provide a compatible kernel and weight recursion.

## Non-claims

- No sector weights or projective kernel are instantiated here.
- No full-Q Gibbs state, positive normalized limit, weak cylinder convergence,
  R-488 global nonzero, or stationarity identity is proved.
- No infinite-volume semigroup, quantum real-time, physical Pre-A, spacetime,
  QFT, gravity, Yang--Mills, mass-gap, or TOE conclusion follows.

