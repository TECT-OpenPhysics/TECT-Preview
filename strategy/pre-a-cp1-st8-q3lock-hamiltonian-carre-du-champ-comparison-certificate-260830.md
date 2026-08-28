# R-402 certificate — finite Hamiltonian carré-du-champ comparison

## Scope

R-402 is a T0, claim-nonbearing finite checkpoint under EXP-001247.  It is a
follow-up to R-401.  The question is whether the proposed physical-coordinate
form is connected to the actual Q3 generator, rather than only to an arbitrary
ordered-level graph.

For a conditional coordinate law `pi` and likelihood row `f`, let
`F=diag(f)` in the one-site q eigenbasis.  The two finite quadratic forms are

```
D_q(f)   = sum_k min(pi_k,pi_(k+1))
          * ((f_(k+1)-f_k)/(x_(k+1)-x_k))^2
E_kin(f) = (2 chi)^(-1) Tr(diag(pi) [p,F]^*[p,F]).
```

The second form is the carré-du-champ associated with the kinetic term
`p^2/(2 chi)`.  On the declared finite coordinate tensor basis, the onsite
quartic and quadratic potentials and the Q3 spatial bond polynomial commute
with `F`; this is checked explicitly rather than assumed for a general
observable class.

## Verification

The R-399 finite fixture contains five volume/cutoff systems, beta in
`{1/2,1}`, two source supports, both source and history signs, both split
orders, every prefix, both history adjoints and both collar orientations.
The primary lane passes `5410/5410` assertions over `3584` contexts and
`71680` conditional rows.  The non-importing independent lane passes
`1815/1815` assertions with matching aggregate fields.  The hostile lane
passes `4/4`; the integrated verifier passes `33/33`; and Lean R402 compiles.

The finite rows contain `57680` nonzero-coordinate comparisons and `14000`
constant-coordinate rows.  Across the nonzero rows,

* `E_kin/D_q` ranges from `1.0087179063711833` to `11.074061483593928`;
* the coordinate form ranges from `0` to `0.0001812074563822086`;
* the kinetic form ranges from `0` to `0.000685033566446745`;
* the maximum potential-commutator Frobenius residual is `0`.

The hostile mutation replaces `p` by `q` in the carré-du-champ.  It finds a
genuine kinetic value `0.0004306559...` while the mutated value is exactly
zero, so the momentum identification is load-bearing on the finite fixture.

## Adversarial review

1. **Form identity versus comparison.**  The kinetic trace form and the
   coordinate nearest-neighbour form are computed independently; their ratio
   is reported, not silently identified with one.
2. **Potential contamination.**  A coordinate multiplier is used, and both a
   site potential and a Q3 bond are checked for a zero commutator.  This does
   not extend to non-coordinate observables.
3. **Truncation boundary.**  The oscillator matrices are finite and bounded.
   The observed ratio interval is not a cutoff-independent constant and no
   exact CCR or unbounded form-domain assertion is made.
4. **History and orientation.**  All registered source/history signs,
   prefixes, adjoints and left/right collars are retained; the independent
   lane rebuilds them without importing the primary implementation.
5. **Mutation.**  Replacing momentum by coordinate kills the commutator for
   `F=f(q)` and is rejected by the hostile lane; this validates the structural
   dependence on the kinetic term only within the declared class.
6. **QFT promotion.**  No finite ratio supplies a phase-conditioned uniform
   bound, an invariant common core, a common alpha, OS/KMS/GNS dynamics, a
   mass gap, a continuum limit, C6, Sector-A or Pre-A closure.

## Decision and next gate

R-402 advances the route from a proposed metric to a finite Hamiltonian-derived
interface.  It does **not** close the comparison gate.  The next mathematical
obligation is an analytic two-sided comparison on a cutoff-independent
Hamiltonian common core, with constants uniform in source, volume, cutoff,
phase, orientation and exhaustion shape.  If the ratio collapses or diverges
under a validated increasing-cutoff/phase stress, retain R-401 only as a
diagnostic and record the route-specific obstruction.  Only after that gate can
the R-399 conditional transfer be combined with a shell summability argument.

## Boundary

No uniform form comparison, phase or exhaustion theorem, common-core/domain
embedding, common alpha, direct `D`/`delta-D` Cauchy limit, Hamiltonian-to-
OS/KMS identification, GNS gap, continuum, C6, Sector-A or Pre-A result is
claimed.

Proven in the manifest, primary/independent/hostile scripts, integrated
verifier, Lean entrypoint, scope note and saved run artefacts.
