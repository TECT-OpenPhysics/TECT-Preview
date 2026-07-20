# A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE -- full Class-II energy composite

**Tier**: T5 PINNED-CLOSURE@FIXED-FLOOR-COVARIANCE-NORMAL-ENERGY-COMPOSITE
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-20

## Result

Let the three-complex-component A1 production Gaussian be realified as
$X:\mathbb T^3_L\to\mathbb R^6$. For each realified embedded Pauli generator
$S_A$, put

\[
\rho=X^TX,\quad q_A={X^TS_AX\over\rho+\varepsilon_\rho},\quad
p_A=2S_AX,\quad v_A=2(S_A-q_AI)X.
\]

The complete production Class-II density is

\[
e_{{\rm II},\Lambda}
={1\over2}\sum_i(\partial_iX_\Lambda)^TB(X_\Lambda)\partial_iX_\Lambda,
\]

\[
B(X)=\sum_A\{a\,p_Ap_A^T+b(p_Av_A^T+v_Ap_A^T)+c\,v_Av_A^T\}.
\]

For the six-real derivative covariance

\[
\Gamma_{\Lambda,i}
=\mathbb E[\partial_iX_\Lambda\partial_iX_\Lambda^T],
\]

common evenness gives
$\mathbb E[X_\Lambda\partial_iX_\Lambda^T]=0$. Hence the exact finite-cutoff
conditional counterterm is

\[
{\cal C}_\Lambda(X)
={1\over2}\sum_i\operatorname{Tr}[B(X)\Gamma_{\Lambda,i}]
=\mathbb E[e_{{\rm II},\Lambda}(x)\mid X_\Lambda(x)=X].
\]

Covariance-normal ordering jointly defines $J_{A,i}^2$,
$J_{A,i}K_{A,i}$, and $K_{A,i}^2$. For every $\kappa>0$,

\[
e_{{\rm II},\Lambda}-{\cal C}_\Lambda(X_\Lambda)
\longrightarrow e_{\rm II}^{\rm ren}
\quad\hbox{in}\quad
L^2(\Omega;H^{-1-\kappa}(\mathbb T_L^3)).
\]

The limit is common to the declared common real-even scalar spectral
regulator class. Its spatial integral converges in $L^2(\Omega)$ and has mean
zero. The $H^{-1}$ endpoint is excluded.

## Why one counterterm is sufficient

The production covariance is $O(|k|^{-4})$. In the Gaussian two-point
composite construction, the only divergent local contraction is the
one-vertex pairing of the two differentiated legs, and it is exactly the
conditional counterterm above. A same-point value-derivative contraction
vanishes by evenness. This statement does not classify or sum an interacting
perturbation series.

After subtraction, the worst two-vertex Fourier-Wick convolution is

\[
\sum_\ell
{\langle\ell\rangle^2\langle k-\ell\rangle^2
\over
\langle\ell\rangle^4\langle k-\ell\rangle^4}
\lesssim\langle k\rangle^{-1}.
\]

Fixed positive $\varepsilon_\rho$ makes the rational coefficient matrix
smooth with uniform Gaussian Sobolev moments through order two. An exact
finite Gaussian integration-by-parts identity exhausts the three surviving
connection families $Q^2$, $QPR$, and $P^2R^2$ without a Hermite-tail
assumption. Bessel-weighted discrete convolution bounds and cross-cutoff
polarisation then give the stated $H^{-1-\kappa}$ Cauchy convergence. The
full proof is in the
[proof note](notes/classii-renormalised-energy-composite-260720-v1.0.tex.txt).

This is a direct pinned Fourier-Wick construction. It is consistent with the
general stochastic BPHZ convergence framework of
[Chandra and Hairer](https://arxiv.org/abs/1612.08138), but it does not import
an interacting-measure theorem from that work.

## Exact convention firewall

The A6 complex covariance is
$D_{\Lambda,i}=\mathbb E[\partial_i\Psi\partial_i\Psi^\dagger]$. The relation
is

\[
\Gamma_{\Lambda,i}={1\over2}\operatorname{realify}(D_{\Lambda,i}).
\]

Using the complex covariance directly in the six-real trace would double the
subtraction. In complex notation the correct counterterm is

\[
\sum_{i,A}\left[
aU_A^\dagger D_{\Lambda,i}U_A
+2b\operatorname{Re}(U_A^\dagger D_{\Lambda,i}V_A)
+cV_A^\dagger D_{\Lambda,i}V_A\right].
\]

The exact covariance of each admitted regulator is used. The leading sharp
cube asymptotic

\[
{\cal C}_N/N\to\delta_{\rm cube}W_\varepsilon
\]

is a check, not the definition.

## Stability and bare-route boundaries

At the production point,

~~~text
a = 0.0045
b = 0.001875
c = 0.00234375
h = sup W_eps/s = 0.09534375
2 h delta_cube = 0.00308894422882794
~~~

The sharp leading pointwise running-mass threshold is $m=h$. Every $m<h$
admits a mixed-orientation homogeneous $-\Theta(N^{3/2})$ trial. At $m=h$,

\[
hs-W_\varepsilon
={6bs^2\over\rho+\varepsilon_\rho}
+{3cs^2(\rho+2\varepsilon_\rho)
\over(\rho+\varepsilon_\rho)^2}\ge0.
\]

This pointwise-coercive route can suppress the first doublet and is not chosen
as a nondegenerate physical prescription.

The bare concentration branch also has a decisive negative control:
$\Psi(x)=e^{ik\cdot x}u$ has $J_A=K_A=F_{\rm II}=0$ while
$W_\varepsilon(u)>0$ whenever the first doublet is active. Therefore
$W_\varepsilon^{-1}(0)$ is not the pathwise Class-II null set, and the
conditional Gaussian mean alone cannot prove pure-third bare concentration.

## Interacting-measure gate

The exact centering and local Gaussian moments give a uniform positive Jensen
lower bound on finite-cutoff partition functions. Finite-cutoff
normalisability follows from the positive sextic. The missing constructive
estimate is

\[
\sup_\Lambda\mathbb E
\exp\{-p[U_\Lambda+{\cal V}_\Lambda^{\rm ren}]\}<\infty
\quad\hbox{for some }p>1.
\]

This is A7-CLASSII-NELSON-EXPONENTIAL-BOUND. Until it is proved, no
interacting density convergence, tightness, or Gibbs measure is claimed.

## Reproduction

~~~powershell
python codes/foundations/a7_classii_renormalised_energy_verify.py
~~~

Expected:

~~~text
PASS: primary (29/29)
PASS: independent (17/17)
ASSERTS: 74/74
A7-CLASSII-RENORMALISED-ENERGY-INTEGRATED-PASS
~~~

The primary route uses FFT multiplicities, exact matrix algebra, conditional
Monte Carlo, three regulator tails, finite connection-pattern enumeration, a frozen-background
Carleman-Fredholm determinant, the mass threshold, and the plane-wave
negative control. The non-importing route uses direct mode enumeration and
separately coded generators, coefficients, covariance, recursive pattern
enumeration, a three-dimensional parity matrix, determinant, and random
stream.

## Devil's-advocate

1. **DISMISSED -- the complex and six-real covariances use the same trace
   formula.** They differ by the explicit one-half realification factor,
   checked independently.
2. **VALID-with-mitigation -- leading $\delta NW$ subtraction can retain a
   finite scheme term.** Every admitted regulator uses its exact derivative
   covariance, fixing the finite covariance-normal condition.
3. **DISMISSED in the Gaussian-composite scope -- the rational coefficient
   leaves an uncontrolled Hermite tail.** The exact finite integration-by-
   parts identity acts directly on $B$, needs at most two derivatives on each
   coefficient, and exhausts all two-point connection families. Interacting
   perturbation-order summation is not claimed.
4. **VALID-with-mitigation -- regulator universality is restricted.** The
   theorem inherits the common bounded real-even scalar multiplier and
   exact/dealiased-product class; asymmetric component-split schemes remain
   excluded.
5. **UPHELD -- composite convergence is not a Gibbs theorem.** The named
   uniform negative-exponential gate remains open.
6. **VALID-with-mitigation -- the frozen determinant might be mistaken for
   the self-coupled law.** It is proved only for deterministic frozen $B(u)$
   and used as a Hilbert-Schmidt audit.
7. **UPHELD -- the pointwise running-mass repair can be physically
   degenerate.** It is recorded as a threshold/no-go result, not adopted as
   the continuum prescription.
8. **UPHELD -- $W$ does not classify the pathwise bare null set.** The exact
   plane-wave counterexample keeps full-field bare concentration open.
9. **VALID-with-mitigation -- floor removal can destroy uniform coefficient
   bounds.** The floor is fixed and no $\varepsilon_\rho\to0$ result is
   asserted.

## Promotion rationale

This is a one-shot scoped T5 closure: the exact counterterm and convergence
proof are self-contained at fixed floor, the note and source hashes are
pinned, the primary 29/29 and non-importing 17/17 routes pass, the integrated
74/74 verifier fails closed on all authority hashes and conventions, and the
PDF passes FORM-CHECK, zero-overfull, and complete visual QA. It does not meet T6
because the interacting exponential estimate and measure construction are
open.

## No-overclaim

No uniform negative-exponential bound, interacting Gibbs density, full
three-component constructive measure, full-field bare concentration,
floor removal, arbitrary regulator universality, infinite-volume limit,
phase transition, BCC state, T6, or T7 follows from this card.

## Next required action

Prove A7-CLASSII-NELSON-EXPONENTIAL-BOUND for the random coefficient $B(X)$,
while keeping the bare-concentration branch and floor removal separate.
