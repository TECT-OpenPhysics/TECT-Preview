# R-407 canonical-path resistance note

R-407 is a finite, claim-nonbearing T0 checkpoint.  It adds a constructive
canonical-path lower bound to the R-404 intrinsic momentum graph.  For a
conditional probability vector `pi` and graph conductance `c`, a deterministic
maximum-conductance spanning tree routes each unordered pair `x<y` along its
tree path.  The load and path constant are

```
load(e) = sum_{x<y:e in path(x,y)} pi_x*pi_y*length(path(x,y))
rho = max_e load(e)/c_e.
```

The finite path argument gives `Var_pi(f) <= rho E(f)`, hence the constructive
finite lower bound `rho^{-1}`.  This is a lower-bound certificate for the
actual graph energy, not an eigenvalue surrogate and not a thermodynamic
statement.

The primary audit passes 22510/22510 assertions over 7 volume-two cutoffs,
2688 contexts and 21120 rows.  The independent lane passes 22509/22509, the
hostile lane 6/6, the integrated verifier 35/35, and Lean R407 compiles.  The
exact intrinsic gap range is `[0.7570174175402339,5.647863075935321]`; the
canonical lower-bound range is `[0.2613815898804392,2.508986944248343]`; and
`rho` ranges from `0.3985672393762041` to `3.825824154093709`.  The minimum
tree conductance is `0.0050691567477082625`, the largest tree path has length
`9`, and the minimum path residual is roundoff (`-4.47e-26`).

The hostile lane checks three load-bearing assumptions: a q-for-p mutation
has no graph edges, a line-tree alternative remains a valid finite certificate,
and doubling the unordered-pair bound fails on a three-node unit path.  These
tests prevent a hidden factor or connectivity assumption from entering the
route.

The finite result advances the route only as an explicit interface.  The open
analytic debt is a cutoff-, volume-, phase- and exhaustion-uniform path/flow
family with bounded `rho`, positive weighted conductance, and an invariant
common-core identification with the R-399 shell.  No claim tier changes and no
QFT, physical mass-gap, continuum, C6, Sector-A or Pre-A conclusion is made.
