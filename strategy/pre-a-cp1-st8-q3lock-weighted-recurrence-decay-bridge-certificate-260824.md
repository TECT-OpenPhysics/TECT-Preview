# EXP-001026 certificate: conditional weighted recurrence to distance decay

## Finding

Assume a nonnegative local seminorm vector satisfies

\[
 L_x(n+1)\le(1+C\delta)L_x(n)+J\delta\sum_{y\sim x}L_y(n),
 \qquad L_x(n)\ge0,
\]

on a graph of degree at most `z`.  For

\[
 W_\rho(L)=\sum_x e^{\rho d(x,X)}L_x,
\]

the neighbor relation `d(x,X)<=d(y,X)+1` gives

\[
 W_\rho(L(n+1))
 \le[1+(C+Jze^\rho)\delta]W_\rho(L(n)).
\]

Consequently, after `N` steps with `T=N delta`,

\[
 W_\rho(L_N)\le e^{(C+Jze^\rho)T}W_\rho(L_0),
\]

and each site at distance `d` obeys

\[
 L_x(T)\le e^{-\rho d+(C+Jze^\rho)T}W_\rho(L_0).
\]

The primary and independent exact lanes pass 20/20 each, the integrated
reader passes 25/25, and Lean R210 compiles.  The degree/weight constants
are the same for induced cubic boxes of side 3 and 5, so this conditional
calculation is volume-uniform.

## Actual Q3 boundary

The recurrence is an input, not a consequence of R-208 or EXP-001025.  The
exact Q3 onsite flow has not been shown to preserve a suitable non-Leibniz or
state-weighted local commutator seminorm with this one-step recurrence.  The
EXP-001025 cyclic-shift fixture independently shows why the energy-product
envelope cannot substitute for the missing spatial statement.

## Decision

`EXP-001026` is an advanced T0 claim-nonbearing conditional bridge.  It
clarifies the precise theorem that would yield a Lieb--Robinson-style
boundary decay once the Q3 recurrence is proved.  It does not close the
first-passage product, actual boundary commutator decay, exhaustion Cauchy,
common alpha, KMS, ground/GNS gap, continuum, C6, Sector A, Pre-A or the
canonical TECT production owner.

## Adversarial review

- **Conditional recurrence — UPHELD:** `supplied_by_q3=false` is explicit.
- **Recurrence to operator theorem — UPHELD:** this is a finite nonnegative
  vector calculation, not an unbounded-domain proof.
- **Volume-uniform constant to exhaustion — UPHELD:** degree uniformity does
  not establish Q3 generator convergence or boundary summability.
- **Energy envelope substitution — UPHELD:** EXP-001025 rejects that shortcut.
- **Lean promotion — UPHELD:** R210 checks scalar identities only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production map is supplied.
