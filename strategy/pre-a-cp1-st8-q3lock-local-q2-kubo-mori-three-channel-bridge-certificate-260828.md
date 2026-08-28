# R-379 three-channel anticommutator bridge certificate

## Result-first boundary

R-379 is a T0, claim-nonbearing finite analytic/executable checkpoint under
EXP-001221.  It decomposes the R-378 Gibbs half-density costs into left and
right GNS legs and a positive beta/2 two-slice leg.  The identity is exact in
finite dimension and cross-checked independently and in Lean; no uniform
modular-tail estimate is claimed.

## 1. Three-channel identity

Let `R=rho^(1/2)` and `Q=rho^(1/4)` in the bond-Hamiltonian eigenbasis, and
let `X` be the centered Hermitian moved witness.  Define

`L=||R X||_2^2`, `Rr=||X R||_2^2`, and `T=||Q X Q||_2^2`.

The two half-density combinations satisfy

`||{R,X}||_2^2 = L+Rr+2T`,

`||[R,X]||_2^2 = L+Rr-2T`,

and therefore

`||{R,X}||_2^2+||[R,X]||_2^2=2(L+Rr)`.

Entrywise arithmetic--geometric mean gives `0<=T<=(L+Rr)/2`.  The `T` term
is the beta/2 Euclidean two-slice channel and cannot be discarded when
estimating the anticommutator leg.

## 2. Finite verification

The primary lane passes `23050/23050` assertions and the non-importing
independent lane passes `8/8` aggregate assertions over `2560` all-prefix
contexts on the actual-Q3 edge (`d=3,6`) and square (`d=2`) fixtures.  The
integrated verifier passes `69/69`; Lean R379 compiles.  Primary and
independent values agree within `5.684e-13`.

The largest left and right GNS legs are both `41.6482665166188`; the largest
two-slice leg is `41.57042344053425`.  The corresponding largest commutator
leg is `0.5097575476240509`, while the largest anticommutator leg is
`166.281693762137`.  The two-slice fraction reaches
`1.0000000000000004` (roundoff at the exact envelope), so saturation is
observed in the finite grid and the cross term must remain in the analytic
ledger.

The largest decomposition residuals are `5.684341886080801e-13` for the
anticommutator, `2.4202861936828413e-13` for the commutator, and
`3.979039320256561e-13` for their sum.  The two-slice spectral residual is
`1.7053025658242404e-13`, and the envelope violation is only
`8.881784197001252e-16`.

## 3. Adversarial review

1. **Cross-term sign.**  The anticommutator uses `+2T` and the commutator
   uses `-2T`; both signs are checked from actual matrix products.
2. **Quarter-root placement.**  `Q` is inserted on both sides of `X`; no
   one-sided quarter-root surrogate is substituted.
3. **Noncommutativity.**  The matrices `R`, `Q` and `X` are not assumed to
   commute; spectral forms are compared with direct products.
4. **Envelope direction.**  The two-slice inequality is one-sided
   `T<=(L+Rr)/2`; saturation is retained rather than interpreted as slack.
5. **Positivity.**  Nonnegative Hilbert--Schmidt squares and the finite
   two-slice leg are checked separately, including the zero-commutator rows.
6. **Centering.**  The same bond-Gibbs centered witness is used in every
   channel; centering is not moved through the Gibbs factors.
7. **Finite growth.**  The edge cutoff-6 costs remain large, so no cutoff
   uniformity is inferred from exact finite decomposition.
8. **State scope.**  The Gibbs density is a doubled-bond finite proxy, not a
   thermodynamic KMS state or OS/GNS reconstruction.
9. **Independence.**  The independent lane rebuilds the oscillator, graph,
   spectrum, prefixes and three products without importing the primary audit.
10. **Lean scope.**  Lean proves the scalar channel identities and AM--GM
    envelope only; matrix limits, modular tails, common cores, common alpha,
    gap and continuum remain open.

## 4. Decision and next gate

R-379 sharpens R-378 into three separately auditable analytic obligations.  The
commutator leg is small on this finite grid, but the two-slice cross leg tracks
the large anticommutator and reaches the AM--GM envelope.  The next proof step
is therefore a beta/2 Euclidean two-slice tail estimate on the same
Hamiltonian-derived core, followed by left/right GNS control and insertion
into the R-378 geometric shell and R-377 resolvent telescope.  Source,
volume, cutoff and beta uniformity, common core, common alpha, OS/KMS/GNS
dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain open.

No new negative result, tier change or proof-note PDF is issued.
