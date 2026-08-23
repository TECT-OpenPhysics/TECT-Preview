# EXP-001028 certificate: conditional first-passage Poisson bridge

## Finding

Assume a nonnegative response has a factorial first-passage expansion

\[
 R_x(t)\le \sum_{n\ge0}\frac{(\eta t)^n}{n!}
 \sum_{\substack{\gamma:\,\gamma_n=x\\|\gamma|=n}}R_{\gamma_0}(0),
\]

with at most `z^n` paths leaving a source site and with every path reaching
`x` from the source set `X` having length at least `d=d(x,X)`.  Multiplying
by `base^d`, `base>1`, gives the exponential generating bound

\[
 \sum_{n\ge0}\frac{(\eta z t\,base)^n}{n!}
 =\exp(\eta z t\,base).
\]

Therefore the conditional site response is bounded by

\[
 R_x(t)\le base^{-d(x,X)}\exp(\eta z t\,base)R_X(0).
\]

For the registered fixture `z=6`, `eta=1`, `t=1/3`, `base=2`, and `d=10`,
the weighted rate is `4` and the envelope is `exp(4)/2^10<0.1`.

The primary lane passes 20/20 and independent lane passes 19/19; the integrated lane passes
25/25, and Lean R212 passes its scalar checks.

## Actual Q3 boundary

The factorial path expansion, the two-orientation operator response, and a
volume/source-uniform path-count coefficient have not been proved for the
exact Q3 onsite-plus-bond dynamics.  EXP-001028 therefore closes only the
branch/repeat arithmetic after EXP-001024--001027.  It does not close spatial
commutator decay, all-shape exhaustion Cauchy, common alpha, KMS, ground/GNS
gap, continuum, C6, Pre-A, Sector A or the TECT production owner.

## Adversarial review

- **Path expansion — UPHELD:** it is an explicit hypothesis, not a consequence
  of the finite energy envelope or the conditional recurrence bridge.
- **Path count — UPHELD:** `z^n` is only a degree envelope; no domain or
  cancellation theorem is inferred.
- **Fixture constants — UPHELD:** the rate and distance are test fixtures,
  not universal Q3 constants.
- **Lean promotion — UPHELD:** R212 proves scalar rate, weight and fixture
  arithmetic only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production map is supplied.

## Next gate

Prove or falsify the declared factorial response expansion on a common core,
including both bond orientations and a volume/source-uniform path coefficient.
Only that analytic result can promote this conditional bridge to a QFT locality
input.
