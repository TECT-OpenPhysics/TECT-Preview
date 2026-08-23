# R-204 / EXP-000978 — Cutoff-uniform Gaussian Fourier heat comparison

## Status and owner boundary

This is a T0, claim-nonbearing proxy result for the A13 comparison lane.  The
object is the explicit diagonal Gaussian Fourier covariance

\[
  \gamma_n=(1+|n|_2^2)^{-2},\qquad n\in\mathbb Z^3,
\]

and the finite-cutoff charge used by the registered heat-screen package.  It is
not the hash-pinned nonlinear A1 production mobility, heat-root incidence,
conditional-replica filtration, raw-current spatial intertwiner, or the
once-owned production q-ledger.  Consequently it does not close either A13
gate, Sector-A, Pre-A, the physical-empty comparison, or a continuum/QFT
construction.

## Exact majorant

For the max-norm shell \(\|n\|_\infty=m\),

\[
 (2m+1)^3-(2m-1)^3=24m^2+2.
\]

Since \(|n|_2^2\ge m^2\), the shell contribution is bounded by

\[
 \frac{24m^2+2}{(1+m^2)^2}\le \frac{26}{m^2},
 \qquad m\ge1.
\]

The partial inverse-square sum obeys

\[
 \sum_{m=1}^{M}m^{-2}<2,
\]

because the terms from \(m=2\) onward are bounded by
\(1/[m(m-1)]\) and telescope.  Therefore the full proxy \(\ell^1\) bound is

\[
 A=\sum_n\gamma_n\le 1+26\cdot2=53,
 \qquad
 \sum_{n\ne0}\gamma_n\le52.
\]

Let
\[
 S(r)=\sum_p\gamma_p\gamma_{r-p},\qquad R=\|r\|_\infty.
\]
Split the sum into \(\|p\|_\infty\le R/2\) and its complement.  In the
first branch \(\|r-p\|_\infty\ge R/2\), and in the second branch the same
bound applies to \(p\).  The elementary denominator comparison gives a factor
\(4^2=16\) in either branch, hence

\[
 S(r)\le 2\cdot4^2\,A(1+R^2)^{-2}
      =32A(1+R^2)^{-2}.
\]

The registered generator profile has two cross channels and one diagonal
channel, so its current factor is

\[
 2\,\mathrm{cross}+2\,\mathrm{diag}=2\cdot2+2\cdot1=6.
\]

For every real heat exponent \(s\ge2\),

\[
 \frac{|r|_2^2}{1+(1+|r|_2^2)^{s/2}}\le1.
\]

Consequently every finite cutoff \(N\) satisfies the same comparison bound

\[
 0\le Q_N(s)
 \le 6\cdot32\cdot53\cdot52
 =529152.
\]

The primary and independent lanes also evaluate the registered finite tables
at cutoffs \(N=1,\ldots,5\) and exponents \(s=2,4\); every table entry is
below this derived majorant.

## Lean cross-check

`verification/lean/Tect/R204.lean` checks the shell polynomial, the rational
pointwise shell majorant for \(m\ge1\), the multiplier \(2\cdot4^2=32\),
the bounds \(1+26\cdot2=53\) and \(26\cdot2=52\), the assembled integer
\(529152\), and the elementary heat-ratio inequality.  It intentionally does
not introduce a production mobility or an interacting measure.

## Reproduction and adversarial review

Run the three lanes from the repository root with the pinned runtime:

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_a1_gaussian_fourier_uniform_heat_bound.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_a1_gaussian_fourier_uniform_heat_bound_independent.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/a13_a1_gaussian_fourier_uniform_heat_bound_verify.py --no-store
```

The current fresh results are `45/45`, `40/40`, and `24/24` respectively.
The independent lane uses only the Python standard library and exact
`Fraction` arithmetic.  The integrated lane rejects mutations that replace the
proxy by the full interacting Gibbs law, remove one convolution branch, alter
the covariance power, erase the q-ledger boundary, admit zero heat, use an
axis-only shell count, promote the proxy to A13/Sector-A/Pre-A, or insert a
Lean escape token.

The decisive scope objections remain upheld:

1. A uniform bound for this explicit proxy does not identify the A1 production
   heat/root map.
2. The finite bound is not a proof of a root filtration, conditional replicas,
   raw-current identity, or production q-ledger.
3. It does not compare a Reading-H/Gaussian reference with physical empty
   space and does not establish OS/KMS, real-time, thermodynamic, or continuum
   limits.

## Decision and next obligation

Retain this result as an exploration-only comparison input.  Do not rerun the
R-192 production owner order as if the missing field had been supplied.  The
next load-bearing obligation is still a hash-pinned nonlinear A1 production
mobility together with `heat_root_incidence`, a compatible root-labelled
filtration, the raw-current spatial intertwiner, and a once-owned nonnegative
q-ledger.  Only after those data are registered should the unchanged R-192
owner audit be rerun.

No PDF is issued at this intermediate checkpoint.
