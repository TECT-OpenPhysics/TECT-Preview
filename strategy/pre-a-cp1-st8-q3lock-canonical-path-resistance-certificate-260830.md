# R-407 certificate - canonical-path effective-resistance lower bound

## Scope

R-407 is a T0, claim-nonbearing finite checkpoint under EXP-001252.  It
continues the R-404 intrinsic momentum-graph lane and supplies a constructive
lower-bound certificate rather than relying only on a generalized eigenvalue.
For a conditional law `pi` and symmetric conductances `c`, a deterministic
maximum-conductance spanning tree routes each unordered pair `x<y` along its
unique tree path `gamma_xy` and records

```
load(e) = sum_{x<y:e in gamma_xy} pi[x] * pi[y] * len(gamma_xy)
rho = max_e load(e)/c_e.
```

The finite path inequality is `Var_pi(f) <= rho E(f)`, so `rho**(-1)` is a
valid lower bound for every finite test function.  The pair sum is unordered;
there is no hidden factor of two.

## Verification

The volume-two R-404 fixture uses oscillator dimensions `3,4,5,6,8,10,12`,
beta in `{1/2,1,2}`, both source signs, both history signs, both split orders,
all prefixes, both history adjoints and both collar orientations.  The
primary lane passes `22510/22510` assertions over `7` systems, `2688`
contexts and `21120` conditional rows.  The independent non-importing lane
passes `22509/22509` with identical aggregate values to the declared
`5e-6` tolerance; the hostile lane passes `6/6`; the integrated verifier
passes `35/35`; and Lean R407 compiles.

Across all rows, the exact intrinsic graph gap is
`[0.7570174175402339,5.647863075935321]`, while the constructive canonical
bound is `[0.2613815898804392,2.508986944248343]`.  The corresponding path
constant is `rho` in `[0.3985672393762041,3.825824154093709]`.  Every tree has
`d-1` positive edges; the minimum selected-tree conductance is
`0.0050691567477082625`, the maximum tree path length is `9`, and the smallest
conditional probability observed is `4.1034872011629017e-08`.  The minimum
finite path residual `E-rho**(-1)Var` is only roundoff (`-4.47e-26`).

## Adversarial review

1. **Pair normalization.**  Loads use unordered pairs and the exact graph
   energy uses unordered edges.  A three-node unit path rejects the doubled
   bound: the correct bound is `3`, whereas the doubled candidate leaves an
   energy-minus-bound residual of `-2`.
2. **Path construction.**  Kruskal is deterministic and the tree is checked
   for exactly `d-1` edges and connectivity.  A separate line tree remains a
   valid, generally weaker certificate on the selected `d=3` and `d=12` rows;
   no tree is assumed analytically optimal.
3. **Generator support.**  Replacing the momentum matrix by diagonal `q`
   produces zero off-diagonal conductances and is rejected by the hostile
   lane; connectivity is therefore not a cosmetic assumption.
4. **Numerical floors.**  Conditional probabilities and selected-tree
   conductances are checked against explicit floors, all loads and residuals
   are finite, and every actual likelihood row satisfies the path residual
   inequality within `1e-8`.
5. **Independent reconstruction.**  The second lane rebuilds the finite
   oscillator Hamiltonian, Gibbs state, history prefixes, conditional rows,
   graph and tree loads without importing the primary implementation.
6. **Uniform/QFT promotion.**  The observed finite envelope does not prove
   bounded `rho` for a cutoff-independent path family, volume/exhaustion
   control, a common core, phase selection, GNS gap, continuum, C6,
   Sector-A or Pre-A closure.

## Decision and next gate

R-407 advances a constructive finite interface.  It gives a directly
   auditable sufficient condition for a future analytic intrinsic-form lower
   bound: control the weighted path load `rho`, rather than only estimating an
   opaque smallest eigenvalue.  The next gate is to construct a
   cutoff/volume/phase-uniform path or flow family on one Hamiltonian common
   core and transfer its bound to the R-399 shell.  If `rho` grows or the
   probability/conductance floors collapse, the route must remain finite and
   cannot replace the shell proof.

## Boundary

No cutoff-independent, volume-independent, phase-uniform or exhaustion-
uniform gap is claimed.  No common-core/common-alpha estimate,
Hamiltonian-to-OS/KMS/GNS identification, physical mass gap, continuum, C6,
Sector-A or Pre-A closure follows.  No tier change, negative result or PDF is
issued.

Proven in the manifest, certificate, scope note, primary/independent/hostile
scripts, integrated verifier, Lean entrypoint and saved run artefacts.
