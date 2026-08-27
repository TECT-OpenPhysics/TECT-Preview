# Q3LOCK local Q2 Kubo-Mori energy-window boundary

R-370 adds a distinct frequency-space diagnostic to the R-368/R-369 local
Kubo-Mori route.  In the doubled selected-bond eigenbasis, with eigenvalues
`lambda_i` and centered witness entries `X_ij`, the theta-half shell is

`N^2 = 2 sum_ij L_ij |lambda_i-lambda_j| |X_ij|^2`.

For each fixed transition-energy threshold `E` in `{1,2,4}`, the executable
lanes retain the terms with `|lambda_i-lambda_j| <= E` as the low-gap part and
the complementary terms as the high-gap part.  The two parts are nonnegative
and their squared values add to the full shell up to floating-point residual
`4.441e-16`.

The actual-Q3 fixture is the R-369 V=2 edge at `d=3,4,5,6` plus the V=4
square at `d=2`, all translated source sites/bonds, both split orientations,
time signs, history adjoints, beta values and all prefix positions.  Primary
and independent lanes pass `50845/50845` assertions each; the integrated
verifier passes `236/236`; Lean R370 passes.  The largest primary/independent
numeric difference is `4.219e-15`.

At edge `d=6`, the maximum high-gap squared-norm fractions are
`0.891744980249774`, `0.7429364350925435`, and `0.49969239659272124` for
`E=1,2,4`; the corresponding high-gap norm maxima are
`1.1400602287279082`, `1.0418743270642477`, and `0.8544583112628602`.
At square `d=2`, the high-gap part is zero for `E>=2` and roundoff-sized for
`E=1`.

This is finite evidence that edge cutoff growth is carried substantially by
large transition-energy differences in the sampled contexts.  It is not a
Gibbs-tail theorem: the Kubo-Mori weights remain a finite doubled local-bond
proxy, and high-energy eigenpairs with small transition gap are not removed.
No cutoff/volume/source/shape uniformity, common core, common alpha,
OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A or Pre-A closure
follows.

