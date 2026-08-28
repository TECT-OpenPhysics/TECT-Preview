# R-400 certificate — increasing-cutoff conditional birth-death gap stress

## Scope

R-400 is a T0, claim-nonbearing finite static diagnostic.  It removes the
source-history and Duhamel layers from R-399 and stresses only the conditional
reference geometry of the finite Q3 Gibbs law.  For every oriented prefix it
forms the conditional law `pi_a` and the ordered-level birth-death Laplacian
with conductance `min(pi_a(k), pi_a(k+1))`.

The certificate is intentionally a stress profile, not a lower-bound theorem.
The cutoff ladder has volume two with dimensions 3 through 28 and volume three
with dimensions 3 through 8, beta in `{1/2,1,2}`, and both left/right
orientations.  There are 32 systems, 192 profiles and 180 adjacent ratios.

## Finite verification

The primary lane passes 519/519 assertions.  The non-importing independent
lane passes 614/614 assertions and reconstructs the same profile fields.  The
hostile lane passes 3/3 assertions: reusing the lowest-cutoff gap produces a
deficit of `0.5222806648401578`, and using an unconditional one-site law
instead of the conditional parent mismatches the selected profile by
`0.07359455021663167`.  The integrated verifier passes 29/29 assertions and
Lean R400 compiles.

Observed finite values are:

* minimum conditional gap: `0.03136900665147795`;
* maximum conditional gap: `0.8039838752304234`;
* minimum conditional atom: `7.164643893391813e-15`;
* minimum reference atom: `5.5141812380298005e-28`;
* minimum adjacent gap ratio: `0.2845843803693108`;
* maximum adjacent gap ratio: `3.9052452930797186`.

The profile is positive on the declared finite grid, but it is not monotone in
the cutoff and its adjacent ratios oscillate.  In particular, the finite
minimum is not a cutoff- or volume-uniform constant.

## Adversarial review

1. **Low-cutoff extrapolation.**  The hostile fixed-gap mutation is separated
   from the target by the recorded deficit, so the finite profile cannot be
   silently replaced by its first point.
2. **Lost conditioning.**  The hostile unconditional-parent mutation is
   detectably different, preserving the distinction between a collar law and
   a one-site marginal.
3. **Numerical positivity.**  Every reference marginal and conditional atom is
   checked above the declared floor; the independent lane uses a separate
   reconstruction and the Lean lane checks only scalar positivity.
4. **Promotion boundary.**  A positive finite gap is not a thermodynamic
   theorem.  Phase conditioning, gradient decay, a common core, common alpha,
   OS/KMS/GNS transfer, a mass gap, continuum, C6, Sector-A and Pre-A remain
   open.

## Exact next gate

Either prove a phase-conditioned, cutoff/volume/shape-uniform lower bound for
an analytically justified local form, or replace the level-index form by a
physically grounded metric.  R-401 tests the latter possibility.

No tier change, negative result or PDF is issued.
