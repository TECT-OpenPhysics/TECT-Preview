# R-403 certificate — increasing-cutoff Hamiltonian carré-du-champ stress

## Scope

R-403 is a T0, claim-nonbearing finite checkpoint under EXP-001248.  It
continues R-402 by asking whether the finite comparison

```
E_kin(f) = (2 chi)^(-1) Tr(diag(pi)[p,F]^*[p,F])
D_q(f)   = sum_k min(pi_k,pi_(k+1))
           * ((f_(k+1)-f_k)/(x_(k+1)-x_k))^2
```

has a cutoff-independent upper constant, rather than treating the R-402
finite ratio as one.  The volume-two actual Q3 chain is evaluated at oscillator
dimensions `3,4,5,6,8,10,12`, beta in `{1/2,1,2}`, both source signs, both
history signs, both split orders, every prefix, both history adjoints and both
collar orientations.  Only exact finite prefixes are cached.

## Verification

The primary lane passes `1397/1397` assertions over `7` systems, `2688`
contexts and `21120` conditional rows.  There are `15840` nonzero-coordinate
rows and `5280` rows below the declared ratio floor.  The nonzero-row ratio
range is
`[1.0461038216925114,109929.13074605557]`.  The maximum ratio by cutoff is:

| cutoff | minimum ratio | maximum ratio |
|---:|---:|---:|
| 3 | 1.0461038216925114 | 4.456994387884469 |
| 4 | 1.2714935607730453 | 12.5280087497725 |
| 5 | 1.1377093385797286 | 40.61057571176524 |
| 6 | 1.4413469154836225 | 105.5426991713365 |
| 8 | 2.492035505108385 | 569.2676339627882 |
| 10 | 4.606568993833506 | 5654.823321175287 |
| 12 | 4.663935150653593 | 109929.13074605557 |

Thus the late maximum is `24664.408607934973` times the cutoff-three maximum
on this finite grid.  The independent non-importing lane passes `1379/1379`
and agrees with the aggregate fields within the declared `5e-5` numerical
cross-check tolerance.  The hostile lane passes `7/7`; on a fixed source,
history and orientation it obtains a positive genuine late kinetic row and a
zero `p -> q` mutated form, while the selected fixed-context ratio grows from
`4.44402...` at cutoff three to `37605.8...` at cutoff twelve.  The integrated
verifier passes `37/37`, and Lean R403 compiles.

## Adversarial review

1. **Upper versus lower direction.**  The minimum ratio remains positive on
   the nonzero rows, but the maximum grows strongly.  The two directions are
   reported separately; neither finite observation is promoted to a uniform
   theorem.
2. **Denominator and underflow.**  Rows with `D_q` at or below the declared
   `1e-20` floor are counted separately and excluded from ratios.  The floor,
   probability tolerance and cross-check tolerance are manifest inputs, not
   hidden constants.
3. **Independent reconstruction.**  The independent lane rebuilds the Q3
   system, Gibbs state, prefixes and forms without importing the primary
   implementation; aggregate agreement is checked by the integrated verifier.
4. **Momentum mutation.**  Replacing `p` by the commuting coordinate `q`
   makes the mutated commutator zero while the genuine late kinetic form is
   positive, so the stress is not an artefact of a coordinate-only multiplier.
5. **Finite-cutoff interpretation.**  Growth across seven bounded oscillator
   matrices is evidence against automatic extrapolation of the R-402 upper
   interval, not a proof that an infinite-volume ratio diverges.
6. **QFT promotion.**  No cutoff-independent common core, phase or volume
   uniformity, common alpha, OS/KMS/GNS dynamics, mass gap, continuum, C6,
   Sector-A or Pre-A closure follows.

## Decision and next gate

R-403 advances the route-local diagnosis: the R-402 finite interval cannot be
used as a two-sided comparison constant without a new analytic estimate.  The
upper direction is now an explicit stress obstruction on the declared finite
ladder; a possible one-sided lower-form route remains open.  The result is
therefore recorded as an inconclusive finite stress, with no new negative
registry entry and no tier change.

The next gate is an analytic estimate on a cutoff-independent Hamiltonian
common core.  It must state the direction, constant, source/phase/volume and
exhaustion uniformity, and then be re-tested in both orientations and phases.
Only after that gate may the R-399 conditional shell transfer use `D_q` in a
regulator limit.

## Boundary

No uniform form comparison, cutoff or volume limit, common core, common alpha,
actual split limit, Hamiltonian-to-OS/KMS identification, GNS gap, continuum,
C6, Sector-A or Pre-A result is claimed.  Finite growth alone is not a
divergence theorem.

Proven in the manifest, primary/independent/hostile scripts, integrated
verifier, Lean entrypoint, scope note and saved run artefacts.
