# R-167 v2.7 proof certificate: fixed-Ritz local-SW Gevrey-two truncation and the raw-configuration-Weyl norm boundary

**Date:** 2026-08-13  
**Task:** T-054  
**Exploration:** EXP-000828, continuing EXP-000827  
**Claim context:** C6-SPACETIME-SIGNATURE  
**Tier:** T0; `claim_bearing: false`  
**Result:** R-167 v2.7, additive to v2.6  
**Manifest:** `strategy/pre-a-cp1-st8-q3lock-fixed-ritz-gevrey-two-truncation-and-raw-configuration-weyl-c0-boundary-manifest.json`

## 1. Exact conclusion

This certificate closes exactly one additional child:

`PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-RITZ-LOCAL-SW-GEVREY-TWO-ADMISSIBLE-OPTIMAL-SCALE-TRUNCATION-EXTENSIVE-GROUND-ENERGY-REMAINDER`.

At every fixed finite parity-preserving onsite Ritz cutoff `M`, the local
Schrieffer--Wolff construction has a fixed-`M` Gevrey-two interaction
majorant.  At sufficiently small scaled coupling it admits an explicit
volume-extensive fixed-order remainder and a stretched-exponential
ground-energy remainder at one explicit admissible optimal-scale truncation.
This is a local-SW theorem, not a standard-SW optimal-scale theorem and not a convergent all-order
transformation.

Two independent boundaries are also registered:

1. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-GEVREY-TWO-ASYMPTOTIC-REMAINDER-AUTOMATIC-ALL-ORDER-SW-CONVERGENCE`;
2. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0`.

The first rejects an automatic Gevrey-to-convergence promotion.  The second
proves a sharp norm jump for raw configuration Weyl characters under the
exact finite-volume full Q3 Hamiltonian.  Neither says that common dynamics
on every other topology or carrier is impossible.

## 2. Literature authority and normalization

The literature input is S. Bravyi, D. P. DiVincenzo and D. Loss,
*Schrieffer--Wolff transformation for quantum many-body systems*, Annals of
Physics **326** (2011), 2793--2826, arXiv:1105.0675.  Section 4.4, especially
Lemma 4.2 and Eqs. (4.31)--(4.33), (4.36)--(4.38), is used below.  The
stretched-exponential corollary in Section 4 is an explicit algebraic
consequence of those displayed bounds; it is not quoted as a statement made
verbatim by the paper.

Fix one finite Ritz cutoff `M`.  Use the zero-source augmented-edge
decomposition proved in R-167 v2.6 and write

\[
 H_M(\lambda)=H_{0,M}+\lambda V_M,
 \qquad H_{0,M}=\sum_x k_{x,M},
 \qquad k_{x,M}\geq\Gamma(1-P_x).
 \tag{2.1}
\]

Put

\[
 J_M=\max_x\sum_{e\ni x}\|\widetilde B_{e,M}\|,
 \qquad \widehat V_M=V_M/J_M,
 \qquad \eta=\lambda J_M,
 \qquad \|\widehat V_M\|_1=1.
 \tag{2.2}
\]

The finite-dimensional onsite ratio
`h_M=sup_x ||k_(x,M)||/Gamma` is finite.  After `M`, the local decomposition,
the degree and this ratio are fixed, the proof of BDL Lemma 4.2 supplies
constants `alpha_M,beta_M>0` independent of the perturbative order `n`, the
volume and `eta`.  They are not asserted uniform in `M`.

## 3. Fixed-order local-SW remainder

Define

\[
 \rho_{n,M}=\frac{\beta_M\Gamma}{n^2}.
 \tag{3.1}
\]

BDL Eq. (4.32), with local strength one, is

\[
 \|V_M^{(j)}\|_1
 \leq \alpha_M\left(\frac{n^2}{\beta_M\Gamma}\right)^j .
 \tag{3.2}
\]

Eqs. (4.31)--(4.33) therefore give, whenever

\[
 |\eta|<\min\left\{\frac{\rho_{n,M}}4,
                         \frac{\Gamma}{32\alpha_M}\right\},
 \tag{3.3}
\]

the local-SW ground-energy remainder

\[
 \begin{split}
 &\left|E_0(H_M(\lambda))-
 E_0(H_{{\rm eff,loc},M}^{[n]}(\lambda))\right|\\
 &\quad\leq
 2\alpha_M\beta_M\Gamma |\Lambda|n^{-2}
 \left(\frac{|\eta|}{\rho_{n,M}}\right)^{n+1}\\
 &\quad=
 2\alpha_M|\Lambda||\eta|
 \left(\frac{|\eta|}{\rho_{n,M}}\right)^n .
 \end{split}
 \tag{3.4}
\]

The equality in the last line is useful: it removes a needless factor four
from the admissible optimal-scale truncation estimate.

## 4. Explicit admissible optimal-scale truncation

Assume

\[
 0<|\eta|<\min\left\{
 \frac{\beta_M\Gamma}{32},\frac{\Gamma}{32\alpha_M}
 \right\},
 \qquad
 x=\sqrt{\frac{\beta_M\Gamma}{8|\eta|}},
 \qquad n_*=\lfloor x\rfloor .
 \tag{4.1}
\]

Then `x>2`, hence `n_*>=2`, and

\[
 \frac{|\eta|}{\rho_{n_*,M}}
 =\frac{|\eta|n_*^2}{\beta_M\Gamma}\leq\frac18.
 \tag{4.2}
\]

Thus (3.3) holds.  Since `n_*>x-1`, Eq. (3.4) gives

\[
 \begin{split}
 \left|E_0(H_M(\lambda))-
 E_0(H_{{\rm eff,loc},M}^{[n_*]}(\lambda))\right|
 &\leq 2\alpha_M|\Lambda||\eta|8^{-n_*}\\
 &\leq 16\alpha_M|\Lambda||\eta|
 \exp\left[-(\log 8)
 \sqrt{\frac{\beta_M\Gamma}{8|\eta|}}\right].
 \end{split}
 \tag{4.3}
\]

This is a fixed-`M`, small-scaled-coupling, volume-extensive
stretched-exponential remainder.  The choice has the Gevrey-two scale
`n_*=O(|eta|^(-1/2))`; it is not claimed to be the exact discrete minimizer.
It is not uniform in the Ritz cutoff.  At
the physical zero-source fixed-`M` point `lambda=1`, the scaled coupling is
`eta=J_M`; no claim is made unless `J_M` satisfies (4.1).

## 5. Gevrey-two majorant

For `r>=1`, choose the proof truncation `n=r+1` in (3.2).  The recursion up to
order `r` is independent of later truncation, so

\[
 \|V_M^{(r)}\|_1
 \leq\alpha_M
 \left(\frac{(r+1)^2}{\beta_M\Gamma}\right)^r .
 \tag{5.1}
\]

Using `r+1<=2r` and the standard Stirling lower bound
`r!>=(r/e)^r`,

\[
 \|V_M^{(r)}\|_1
 \leq\alpha_M
 \left(\frac{4e^2}{\beta_M\Gamma}\right)^r(r!)^2 .
 \tag{5.2}
\]

Equation (5.2) is a Gevrey-two majorant for the fixed-`M` local-SW generated
interaction.  It is not an all-order convergence theorem.

## 6. Exact Fraction fixture

Set

\[
 \alpha=\beta=\Gamma=1,
 \qquad |\eta|=\frac1{800},
 \qquad |\Lambda|=12.
 \tag{6.1}
\]

Then `x=10`, `n_*=10`, `rho=1/100`, and `|eta|/rho=1/8`.  The exact
fixed-order bound and its stretched-exponential envelope are

\[
 B_{10}=\frac{3}{107374182400},
 \qquad
 B_{\rm env}=\frac{3}{13421772800},
 \qquad
 \frac{B_{10}}{B_{\rm env}}=\frac18.
 \tag{6.2}
\]

The primary and non-importing independent scripts reconstruct all six
rational values rather than reading them as derived constants.

## 7. A Gevrey-two asymptotic remainder does not imply convergence

For `t>=0`, consider the actual function

\[
 F(t)=\int_0^\infty\!\int_0^\infty
 \frac{e^{-s-u}}{1+tsu}\,ds\,du .
 \tag{7.1}
\]

The exact finite geometric identity gives, for every integer `N>=0`,

\[
 F(t)=\sum_{n=0}^{N}(-1)^n(n!)^2t^n+R_N(t),
 \qquad |R_N(t)|\leq t^{N+1}((N+1)!)^2 .
 \tag{7.2}
\]

Thus `F` has an exact Gevrey-two asymptotic remainder.  Nevertheless, for
every `t!=0` the ratio of successive absolute formal terms is
`(n+1)^2|t|`, which tends to infinity.  The formal convergence radius is
zero.  This proves

`NG-2026-08-13-PRE-A-ST8-Q3LOCK-GEVREY-TWO-ASYMPTOTIC-REMAINDER-AUTOMATIC-ALL-ORDER-SW-CONVERGENCE`.

The fixture does not prove that the actual Q3 series diverges.  It rejects
only the inference from a Gevrey-two asymptotic remainder to a convergent
all-order series.

## 8. Standard-SW firewall

BDL Theorem 4 compares fixed-order local and standard SW Hamiltonians through
a low-space unitary with a constant allowed to depend on the order.  Its
proof treats that order as fixed.  Since `n_*` in (4.1) grows as
`|eta|^(-1/2)`, this certificate does not transport (4.3) to standard SW.
Such a transport needs an explicit comparison constant controlled at the
growing admissible order.

## 9. Raw configuration Weyl characters have a sharp norm jump

Let a fixed finite Q3 volume have `d=8|Lambda|` real coordinates.  On
`L2(R^d)`, set

\[
 P=-i\hbar\nabla,
 \quad T=\frac{P^2}{2\chi},
 \quad H=T+V(Q),
 \quad U_t=e^{-itH/\hbar},
 \quad \alpha_t(A)=U_t^*AU_t,
 \tag{9.1}
\]

where `V` is the exact real zero- or compact-source Q3 polynomial, of degree
at most four.  Its finite-volume Schrodinger operator is essentially
self-adjoint on the Schwartz core.  For `xi!=0`, put

\[
 W_\xi=e^{i\xi\cdot Q}.
 \tag{9.2}
\]

For the free group `U_t^0=e^{-itT/hbar}`, the central BCH relation gives

\[
 D_t^0:=W_\xi^*\alpha_t^0(W_\xi)
 =e^{i\hbar t|\xi|^2/(2\chi)}
  e^{i(t/\chi)\xi\cdot P}.
 \tag{9.3}
\]

Fix `sigma>0` and the normalized Gaussian

\[
 \phi_\sigma(q)=(\pi\sigma^2)^{-d/4}
 e^{-|q|^2/(2\sigma^2)}.
 \tag{9.4}
\]

For `t!=0`, define

\[
 p_t=\left(\frac{\chi\pi}{t|\xi|^2}-\frac\hbar2\right)\xi,
 \qquad
 \psi_t=e^{ip_t\cdot Q/\hbar}\phi_\sigma.
 \tag{9.5}
\]

Momentum conjugation and the Gaussian translation overlap yield exactly

\[
 \langle\psi_t,D_t^0\psi_t\rangle
 =-\exp\left[-\frac{\hbar^2t^2|\xi|^2}
 {4\chi^2\sigma^2}\right].
 \tag{9.6}
\]

The interaction does not spoil this high-momentum test.  The Galilean
identity writes `U_s^0 exp(i p_t.Q/hbar)` as a phase, the same momentum
multiplier, a spatial translation by `s p_t/chi`, and `U_s^0`.  For
`|s|<=|t|`,

\[
 \left|\frac{s p_t}{\chi}\right|
 \leq \frac{\pi}{|\xi|}+O(|t|).
 \tag{9.7}
\]

Polynomial multiplication by `V` is therefore uniformly bounded on the
translated fixed Schwartz vectors `phi_sigma` and `W_xi phi_sigma` appearing
in Duhamel's formula.  Consequently

\[
 \|(U_t-U_t^0)\psi_t\|+
 \|(U_t-U_t^0)W_\xi\psi_t\|=O(|t|).
 \tag{9.8}
\]

With `D_t=W_xi^*alpha_t(W_xi)`, Eqs. (9.6)--(9.8) imply
`<psi_t,D_t psi_t> -> -1`.  Since both `D_t` and the identity are unitaries,

\[
 \boxed{
 \lim_{t\to0,\ t\neq0}\|\alpha_t(W_\xi)-W_\xi\|=2 .}
 \tag{9.9}
\]

This proves

`NG-2026-08-13-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-WEYL-FULL-HAMILTONIAN-POINT-NORM-C0`.

It is not a duplicate of the v1.7 momentum-label result, which used
high-position packets and obtained a positive lower bound for raw momentum
Weyl and basic momentum resolvent labels.  It is also stronger than the v1.5
generator-core observation that `[H,W_xi]` is unbounded: an unbounded
generator alone does not prove orbit norm discontinuity.

## 10. Surviving routes

For oscillator elimination, the missing all-order input is one support-aware
weighted interaction Banach scale in which:

1. the homological inverse is bounded;
2. commutators close with quantified scale loss;
3. every generated word has Ritz convergence in the same norm; and
4. connected aggregation leaves at most exponential, rather than raw
   factorial-squared, support growth.

For common dynamics, raw configuration characters may remain W-star,
local-strict or form-topology labels.  A norm-C0 algebra must instead be made
from Hamiltonian-derived temporal, energy or resolvent smoothed continuous
elements.  Spatial locality must be proved from two-sign propagation or
commutator decay; formal seed supports are insufficient.

## 11. Devil's-advocate audit

1. **Objection -- BDL already states the stretched-exponential bound.**
   **DISMISSED with provenance correction.**  BDL states (4.31)--(4.33); the
   floor estimate and the constant 16 are derived here.
2. **Objection -- the constants can secretly grow with the volume.**
   **DISMISSED at fixed M.**  The local-strength proof uses the fixed degree,
   local dimension, gap and onsite norm/gap ratio.  Dependence on `M` is
   retained explicitly.
3. **Objection -- the bound transfers to standard SW.**  **UPHELD as an
   overreach.**  The fixed-order comparison constant is not controlled at
   `n_*=O(|eta|^(-1/2))`.
4. **Objection -- an optimal-scale truncation proves convergence.**  **REFUTED.**
   Section 7 gives an exact zero-radius Gevrey-two series.
5. **Objection -- the physical point is proved.**  **UPHELD as an overreach.**
   At `lambda=1`, one still needs the fixed-`M` inequality for `J_M`.
6. **Objection -- an unbounded commutator alone proves (9.9).**  **DISMISSED.**
   The proof uses an explicit time-dependent packet and a Duhamel comparison.
7. **Objection -- (9.9) forbids common dynamics.**  **UPHELD as an
   overreach.**  It forbids point-norm C0 only for an equivariant concrete
   carrier containing the raw configuration label.
8. **Objection -- the new carrier result duplicates v1.7.**  **DISMISSED.**
   The label, packet scaling and sharp conclusion differ.

## 12. Boundary and lifecycle

This is R-167 v2.7, T0 and `claim_bearing:false`.  The only new positive gate
is the fixed-`M` local-SW Gevrey-two/admissible-optimal-scale energy remainder.  The
two new negatives reject automatic all-order convergence and one raw
configuration-Weyl point-norm carrier.  No `M`-uniform, physical-`lambda=1`,
standard-SW optimal-scale, convergent transformation, fifth-order unbounded-Q3,
phase transfer, common-alpha/KMS, spatial carrier, broken-sector GNS or
physical mass-gap, regulator-removal, continuum, physical-empty, Round-1,
C6, CP1, physical Sector A or Pre-A conclusion follows.

No per-lemma or intermediate PDF is issued.  The proof-first authority is
this certificate, its manifest, the primary and non-importing independent
executables, the integrated verifier, the formal R-167/gate/negative records
and their run JSON artefacts.

Machine-check tokens reproduce the formulas without TeX spacing:
`fixed-M`, `2alpha_M|Lambda||eta|`, `16alpha_M|Lambda||eta|`,
`lim_(t->0,t!=0)||alpha_t(W_xi)-W_xi||=2`, and `sharp norm limit two`.
