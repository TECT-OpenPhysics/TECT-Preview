# R-380 Renyi interpolation bridge certificate

## Result-first boundary

R-380 is a T0, claim-nonbearing finite analytic/executable checkpoint under
EXP-001222.  It unfolds the beta/2 midpoint channel from R-379 into the full
modular-frequency weighted Renyi interpolation and identifies the endpoint
modular moment that an eventual uniform estimate must control.  No endpoint
uniformity, common core, common alpha or QFT limit is claimed.

## 1. Interpolation identity

Let `p_i>0` be the normalized Gibbs eigenvalues and let `X` be the centered
Hermitian moved witness.  Put

`G(s)=sum_ij |log(p_i)-log(p_j)| p_i^s p_j^(1-s) |X_ij|^2`,

for `0<=s<=1`.  Hermitian symmetry gives `G(s)=G(1-s)`.  The endpoints and
midpoint are

`G(0)=sum_ij p_j |log(p_i)-log(p_j)| |X_ij|^2`,

`G(1)=sum_ij p_i |log(p_i)-log(p_j)| |X_ij|^2`,

`G(1/2)=sum_ij sqrt(p_i p_j) |log(p_i)-log(p_j)| |X_ij|^2`.

Pairwise integration uses

`integral_0^1 p_i^s p_j^(1-s) ds=(p_i-p_j)/(log(p_i)-log(p_j))`,

with the continuous diagonal value, hence

`integral_0^1 G(s) ds=sum_ij |p_i-p_j| |X_ij|^2`.

Each summand is convex in `s`, so the finite envelope is

`G(1/2) <= integral_0^1 G(s) ds <= (G(0)+G(1))/2`,

and `G(s)<=(1-s)G(0)+sG(1)`.  The original R-378 shell is exactly
`(2/beta)` times this integral.

## 2. Finite verification

The primary lane passes `30,733/30,733` assertions and the non-importing
independent lane passes `14/14` aggregate assertions over `2,560` all-prefix
actual-Q3 contexts on the edge (`d=3,6`) and square (`d=2`) fixtures.  The
integrated verifier passes `69/69`; Lean R380 compiles with the pinned
toolchain.  Primary and independent numerical fields agree within
`1.554312234475219e-14`.

The largest endpoint modular moment is `2.15358381458932`, the largest
midpoint modular moment is `0.360525986123478`, and the largest integrated
modular shell is `0.7305484440673373` before the `(2/beta)` shell factor.  The
largest shell is `1.4610968881346746`.  The largest meaningful midpoint to
integral ratio is `0.9594837421464463`, while the largest integral to endpoint
ratio is `0.9240035972845281`; the midpoint therefore does not supply an
endpoint upper bound on this grid.

The maximum endpoint and quarter-point symmetry errors are respectively
`4.440892098500626e-16` and `1.1102230246251565e-16`.  The convex-chord,
midpoint-lower and integral-upper violations are at most
`9.860761315262648e-32`, `1.5974244787049213e-16` and
`6.376313427723079e-16`.  The direct Kubo modular identity error is
`1.3877787807814457e-17`; 12-node Gauss--Legendre reconstruction has maximum
error `1.726396803292118e-12`.

## 3. Adversarial review

1. **Logarithmic-mean diagonal.**  Equal eigenvalues use the continuous
   arithmetic value in the Kubo weight; no `0/0` division is accepted.
2. **Absolute modular frequency.**  The factor is
   `|log(p_i)-log(p_j)|`; the sign is not silently dropped before taking the
   absolute shell.
3. **Trace ordering.**  The interpolation is evaluated entrywise in the
   Hamiltonian eigenbasis; no unlicensed commutation of `rho` and `X` occurs.
4. **Endpoint orientation.**  `G(0)` uses `p_j` and `G(1)` uses `p_i`; their
   equality is checked from Hermitian matrix entries rather than assumed.
5. **Convexity direction.**  The midpoint is a lower bound for the integral,
   whereas the endpoint chord is the upper bound; the two directions are
   tested separately.
6. **Quadrature versus identity.**  The shell integral is computed exactly
   from `|p_i-p_j|`; quadrature is only an independent reconstruction check.
7. **Near-zero ratios.**  Midpoint/integral ratios omit only values below the
   declared finite tolerance, preventing roundoff zeros from becoming a
   false large ratio.
8. **Finite state scope.**  Gibbs weights are normalized finite doubled-bond
   proxies; no thermodynamic KMS or OS reconstruction is inferred.
9. **Independence.**  The independent lane rebuilds the oscillator, graph,
   spectrum, prefixes and interpolation without importing the primary audit.
10. **Lean scope.**  R380 formalizes the scalar geometric-mean and chord
    envelopes only; logarithmic integrals, matrix traces and all limits remain
    executable finite evidence.

## 4. Decision and next gate

R-380 advances the route by showing that the R-379 beta/2 channel is the
midpoint of a full symmetric modular-frequency interpolation.  On the tested
grid the midpoint captures at most `0.95948` of the integrated shell, and the
integral captures at most `0.92400` of the endpoint modular moment.  Therefore
the next analytic obligation is an endpoint modular-frequency bound on a
Hamiltonian-derived common core (or a source-local substitute), not another
midpoint-only estimate.  That bound must then feed the R-377 resolvent
telescope and the R-378 geometric shell.

Source, volume, cutoff and beta uniformity, common core, common alpha,
OS/KMS/GNS dynamics, mass gap, continuum, C6, Sector-A and Pre-A remain open.

No new negative result, tier change or proof-note PDF is issued.
