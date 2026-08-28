# R-378 half-density Hellinger bridge certificate

## Result-first boundary

R-378 is a T0, claim-nonbearing finite analytic/executable checkpoint under
EXP-001220.  It rewrites the absolute theta-half Kubo--Mori shell as a
geometric mean of two explicit Gibbs half-density costs.  The finite bridge is
verified independently and in Lean, but no uniform modular-tail or
common-alpha theorem is claimed.

## 1. Exact bridge

Let `rho=diag(p_i)` in the bond-Hamiltonian eigenbasis and let `X` be the
centered Hermitian moved witness.  With `R=rho^(1/2)`,

`[R,X]_ij=(sqrt(p_i)-sqrt(p_j)) X_ij`,

`{R,X}_ij=(sqrt(p_i)+sqrt(p_j)) X_ij`, and

`|p_i-p_j|=|sqrt(p_i)-sqrt(p_j)| (sqrt(p_i)+sqrt(p_j))`.

The shell therefore obeys the finite Cauchy bound

`S_(1/2)=(2/beta) sum_ij |p_i-p_j| |X_ij|^2`

`<= (2/beta)||[R,X]||_2 ||{R,X}||_2`

`<= beta^(-1)(||[R,X]||_2^2+||{R,X}||_2^2)`.

For Hermitian `X`, the last sum is exactly `4 Tr(rho X^2)`, recovering the
R-371 arithmetic second-moment envelope while retaining the sharper geometric
two-sided interface.

## 2. Finite verification

The primary lane passes `25454/25454` assertions and the non-importing
independent lane passes `8/8` aggregate assertions over `2816` all-prefix
contexts on the actual-Q3 edge and square fixtures.  The integrated verifier
passes `68/68`; Lean R378 compiles.  Primary and independent values agree
within the registered tolerance (`1.137e-12` maximum reported difference).

The maximum shell is `1.4610968881346746`.  The maximum geometric
half-density bound is `18.402415064535205`, while the maximum recovered
arithmetic bound is `166.59306606647507`.  The largest half-density commutator
square is `0.5097575476240509`; the largest anticommutator square is
`166.281693762137`.  The shell/geometric-bound ratio never exceeds
`0.5380346350964185`; the shell/arithmetic ratio never exceeds
`0.008770454393051757`.

Pair factorization residual is at most `8.806090776978568e-18`, the largest
commutator and anticommutator spectral-form residuals are
`7.771561172373096e-16` and `2.2737367544323206e-13`, and the arithmetic
second-moment recovery residual is `2.5579538487363607e-13`.

## 3. Adversarial review

1. **Absolute-value sign.**  The pair identity is evaluated with absolute
   probability differences and the nonnegative square-root sum; no energy
   ordering is assumed.
2. **Cauchy direction.**  The shell is bounded by Cauchy applied to the two
   nonnegative spectral rows; the geometric mean is not treated as an
   equality.
3. **Operator ordering.**  The commutator and anticommutator are formed as
   actual matrix products with the same Gibbs half-density on both sides; no
   commuting through `X` is used.
4. **Hermiticity.**  The moved witness is explicitly Hermitian, so the
   commutator is anti-Hermitian and the anticommutator Hermitian; both defects
   are checked numerically.
5. **Diagonal gaps.**  Zero transition gaps are retained; no division by an
   energy difference occurs in the half-density factorization.
6. **Arithmetic recovery.**  The identity
   `||[R,X]||_2^2+||{R,X}||_2^2=4 Tr(rho X^2)` is checked in the bond Gibbs
   eigenbasis, not inferred from a commuting approximation.
7. **Finite versus uniform.**  The cutoff-6 edge cost is finite but the
   anticommutator term still grows across the declared finite cutoffs; no
   cutoff or volume uniformity is inferred.
8. **State scope.**  `rho` is the finite doubled-bond Gibbs proxy, not a
   thermodynamic KMS state or a phasewise OS state.
9. **Independence.**  The independent lane rebuilds the oscillator, graph,
   Gibbs spectrum, prefixes and half-density products without importing the
   primary audit.
10. **Lean scope.**  Lean proves the scalar pair factorization and arithmetic
    envelope only; matrix spectra, modular tails, common cores, limits and
    QFT conclusions remain outside the formal cross-check.

## 4. Decision and next gate

R-378 advances the direct `D,delta D` corridor by separating the square-root
locality debt into a half-density commutator leg and a dual anticommutator leg.
The next analytic target is a source-, volume- and cutoff-uniform estimate for
both legs on one Hamiltonian-derived core.  If those two estimates hold, the
geometric bound can be inserted into the R-377 odd-resolvent telescope without
reintroducing an absolute-value eigenvector derivative.  Common core, common
alpha, global KMS/GNS identification, mass gap, continuum, C6, Sector-A and
Pre-A remain open.

No new negative result, tier change or proof-note PDF is issued.
