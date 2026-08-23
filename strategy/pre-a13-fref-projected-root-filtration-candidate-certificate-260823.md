# EXP-000993 — Finite projected root filtration candidate

## Scope

This T0, claim-nonbearing package constructs a finite comparison object for the
QFT connection.  On the one-dimensional slice (k=(n,0,0)) of the side-16
torus, start with (S_0=\{1,2\}) and define

\[
  S_{j+1}=S_j+2(S_j-S_j)\pmod {16},\qquad
  V_j=\{f:\operatorname{supp}f\subseteq S_j\}.
\]

The exact supports are

\[
 S_0=\{1,2\},\quad
 S_1=\{15,0,1,2,3,4\},\quad
 S_2=\mathbb Z/16\mathbb Z.
\]

The rule is the support upper bound for
\(N(f)=(\bar f*f)^2*f\).  It records nonlinear level-raising, not a claim
that coefficients never cancel.

## Heat-root candidate

For the quadratic A1 core, set

\[
 \omega(n)=r+Z(2\pi n/16)^2+Y(2\pi n/16)^4.
\]

Since (Y>0) and
\(r-Z^2/(4Y)=26000000000947494031/10^{20}>0), every real frequency has
positive quadratic rate.  The diagonal semigroup
\((H_t f)(n)=e^{-t\omega(n)}f(n)) preserves every (V_j), because it does
not create Fourier support.  This is an explicit finite quadratic-core
heat-root incidence candidate.

## What is and is not supplied

The nonlinear drift maps (V_j) into (V_{j+1}), while the linear heat proxy
preserves each (V_j).  This separates a valid finite projected filtration from
the missing production construction.  No conditional replica law, nonlinear
production heat-root map, raw-current spatial intertwiner, or one-use
nonnegative (q)-ledger is supplied.  The slice is not the full three-dimensional
A1 cylinder, and the identity/diagonal heat choice is not deduced from static
Gibbs or Hessian data.

R-202 and R-203 already establish full-residue saturation and the frequency
convention crosswalk; this package adds the explicit nested projection and the
diagonal-support preservation statement.  It does not close R-192 or either A13
gate, and it makes no OS/KMS, real-time, physical-empty, removal, continuum,
Sector-A or Pre-A claim.

## Reproduction and adversarial checks

The primary and independent lanes use exact integer/Fraction support arithmetic;
the integrated lane reruns both without importing either implementation,
checks all source/file hashes, checks stdlib-only imports, and compiles
`verification/lean/Tect/R205.lean`.  The Lean file proves the general diagonal
support-preservation lemma and the positive quadratic-core lower bound in exact
rational arithmetic.  Hostile mutations cover modular aliasing, the proper
intermediate level, nesting, nonlinear-versus-linear scope, dimensional
promotion, replica invention, q-ledger invention and Lean escape tokens.

No result ledger entry, new negative, tier change or PDF is issued at this
intermediate exploration checkpoint.
