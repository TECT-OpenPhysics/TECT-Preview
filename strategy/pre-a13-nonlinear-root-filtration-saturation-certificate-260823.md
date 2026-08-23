# Two-step nonlinear support saturation on the side-16 torus

## Status

This is a T0, claim-nonbearing support-closure witness under EXP-000964. It
tests an invariant-space requirement for the nonlinear `F_ref` term; it is not
a time-discretized dynamics or a production-owner theorem.

## Exact closure

Start with `phi_0=z+z^2=z(1+z)` and define

\[
S(\phi)=(\overline\phi\,\phi)^2\phi.
\]

The first closure is

\[
\phi_1=z^{-1}(1+z)^5,
\]

with support from `-1` through `4`. Applying the same algebraic closure again
gives

\[
\phi_2=z^{-11}(1+z)^{25},
\]

with support from `-11` through `14`. All coefficients are strictly positive,
so there is no cancellation in these support intervals. Modulo the registered
side-16 torus, the interval `[-11,14]` contains every residue class. Thus the
small two-root seed saturates the entire one-dimensional side-16 residue
lattice after two support closures.

## Owner consequence

This is a necessary invariant-space test, not a claim that the stochastic flow
has been iterated twice. Any filtration that is invariant under the local
nonlinear F_ref drift must contain the generated blocks and, on the declared
side-16 slice, all residue classes from this witness. A valid production owner
must still specify projections, conditional replicas, heat-root incidence,
raw-current spatial intertwining, and a one-use nonnegative `q_k` ledger on that
enlarged space. Saturation alone supplies none of them.

## Boundary

The proof is finite and algebraic. It does not imply a continuum or infinite
volume statement, nor does it close A13/T-050, Sector-A, Pre-A, physical-empty,
removal, or real-time dynamics. No PDF is issued at this checkpoint.
