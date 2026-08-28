# R-381 endpoint modular moment to energy Cauchy bridge certificate

## Result-first boundary

R-381 is a T0, claim-nonbearing finite analytic/executable checkpoint under
EXP-001223.  It converts the endpoint modular-frequency moment isolated by
R-380 into a Gibbs energy-difference first moment and bounds it by a
state-weighted quadratic energy-commutator moment.  The bound is finite only;
no source/volume/cutoff/beta uniformity or common alpha is claimed.

## 1. Endpoint-energy identity

For a finite Gibbs spectrum

`p_i=Z^(-1) exp(-beta E_i)`,

normalization cancels in the difference of logarithms:

`|log(p_i)-log(p_j)|=beta |E_i-E_j|`.

For the centered Hermitian moved witness `X`, define

`D_1=sum_ij p_i |log(p_i)-log(p_j)| |X_ij|^2`,

`M_0=sum_ij p_i |X_ij|^2`, and

`M_2=sum_ij p_i (E_i-E_j)^2 |X_ij|^2`.

Then the endpoint is exactly

`D_1=beta sum_ij p_i |E_i-E_j| |X_ij|^2`,

and state-weighted Cauchy--Schwarz gives

`D_1<=beta sqrt(M_0 M_2)`.

Hermitian symmetry gives the same `M_0` and `M_2` from the right Gibbs leg.

## 2. Finite verification

The primary lane passes `17,931/17,931` assertions and the non-importing
independent lane passes `11/11` aggregate assertions over `2,560` all-prefix
actual-Q3 contexts on the edge (`d=3,6`) and square (`d=2`) fixtures.  The
integrated verifier passes `61/61`; Lean R381 compiles with the pinned
toolchain.  Primary and independent numerical fields agree within
`1.918465386552270e-13`.

The maximum Gibbs log-energy identity residual is
`7.105427357601002e-15`; endpoint reconstruction from energy differences has
error `8.881784197001252e-16`.  The maximum left/right moment orientation error
is `1.0658141036401503e-14`.  The largest endpoint moment is
`2.15358381458932`, the largest `M_0` is `41.64826651661874`, the largest
`M_2` is `17.719559304500326`, and the largest Cauchy envelope is
`27.165951639338186`.  The largest endpoint-to-Cauchy ratio is
`0.07927511037274983`; the aggregate Cauchy violation is
`-2.290857218268337e-16`.

## 3. Adversarial review

1. **Gibbs normalization.**  The partition-function and energy-shift terms
   cancel in the log difference; the cancellation is checked on every finite
   spectrum.
2. **Absolute value.**  The endpoint retains `|E_i-E_j|`; no ordering of
   eigenvalues is assumed.
3. **Cauchy direction.**  The quadratic envelope is one-sided and tested as
   `D_1<=beta sqrt(M_0 M_2)`, not treated as an equality.
4. **Weight orientation.**  Both `p_i` and `p_j` orientations are computed;
   Hermitian symmetry is checked rather than silently imposed.
5. **Energy shift.**  Only energy differences enter `M_2`, so shifted finite
   spectra cannot alter the identity.
6. **Noncommutativity.**  `X` is formed in the bond-Hamiltonian eigenbasis,
   with no commutation of `rho` through the witness.
7. **Zero gaps.**  Diagonal and degenerate entries remain in the sums and
   contribute zero to the energy first moment without a singular division.
8. **Finite growth.**  The observed `M_0`, `M_2` and endpoint values are
   parameter-dependent finite diagnostics, not uniform estimates.
9. **Independence.**  The independent lane rebuilds oscillator, graph,
   spectrum, prefixes and moments without importing the primary audit.
10. **Lean scope.**  R381 formalizes the scalar square-root Cauchy envelope;
    matrix Cauchy, Gibbs identities and all limits remain executable finite
    evidence.

## 4. Decision and next gate

R-381 advances R-380 by replacing the endpoint modular-frequency debt with a
quadratic energy-moment obligation.  The finite envelope is very loose on the
declared grid (maximum ratio `0.0792751104`), so sharpening the constant is not
the present blocker; proving a source-, volume-, cutoff- and beta-uniform
bound for `M_0` and `M_2` on one Hamiltonian-derived common core is.  Once
that premise exists, the endpoint bound can be inserted into the R-380
interpolation, then into the R-378 shell and R-377 resolvent telescope.

Source, volume, cutoff and beta uniformity, common core, common alpha,
OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain open.

No new negative result, tier change or proof-note PDF is issued.
