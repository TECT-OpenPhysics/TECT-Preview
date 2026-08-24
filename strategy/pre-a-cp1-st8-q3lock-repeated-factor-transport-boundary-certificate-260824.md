# EXP-001047 certificate: repeated cubic graph-factor transport boundary

## Finding

The centered R-167 graph estimate and the EXP-001045 mixed lift control one
factor in the two displayed orientations, but those estimates do not by
themselves control a repeated product.  The exact finite family below makes
the missing transport visible without using floating-point powers.

For a base `b>=2` and integer `n>=1`, let

\[
A_n=\operatorname{diag}(1,b^{4n},b^{8n}),\qquad
S e_0=e_1,\; S e_1=e_2,\; S e_2=0,
\]

and set

\[
Q_n=S A_n^{3/4}=S\operatorname{diag}(1,b^{3n},b^{6n}).
\]

The exact matrix actions give

\[
\|Q_nA_n^{-3/4}\|_\infty=1,
\qquad
\|A_n^{-3/4}Q_n\|_\infty=b^{-3n}\le 1,
\]

while

\[
\|Q_n^2A_n^{-3/2}\|_\infty=b^{3n}.
\]

For the recorded fixture `b=2`, the first repeated product has norm `8`, and
the family grows as `8^n`, although both one-factor bounds remain at most
one.  Thus a proof that only repeats the separate `A^(-3/4)` bounds cannot
close the history.  It needs a Q3-specific A-power transport estimate, higher
weighted energy moments, a non-Leibniz analytic/Frechet composition theorem,
or a proved cancellation.

## Exact scope

This is an inference boundary in finite-dimensional operator arithmetic.  The
abstract `Q_n` is not identified with an actual Q3 cubic multiplier, and the
target `Q_n^2 A_n^(-3/2)` is the minimal naive repeated-factor composition,
not a claim that every successful history topology must use that norm.  The
actual Q3 word incidence, domain theorem, factorial first-passage resummation,
exhaustion Cauchy estimate, common alpha, KMS/OS reconstruction, GNS gap,
continuum, C6, Sector A and Pre-A remain open.

## Adversarial review

- **Abstract-witness promotion — UPHELD:** the family rejects an inference
  rule only; it does not model the full Q3 operator.
- **Orientation — UPHELD:** right and left one-factor norms are calculated
  separately, with the left value `b^(-3n)` retained.
- **Fractional power — UPHELD:** `A_n^(3/4)` is encoded by the exact integer
  powers `b^(3n)` and `b^(6n)`.
- **Target necessity — UPHELD:** an analytic/Frechet or cancellation route may
  avoid the displayed repeated-product norm; no universal impossibility is
  claimed.
- **Lean — UPHELD:** R229 checks rational fixture arithmetic and inequalities,
  not unbounded domains or Q3 dynamics.
- **QFT firewall — UPHELD:** no thermodynamic QFT or downstream physical gate
  is promoted.

## Next gate

Derive either a genuine Q3 higher-energy/A-power transport theorem or a
history composition estimate in an analytic/Frechet topology.  The actual
two-orientation first-passage recurrence cannot be called closed before that
step.
