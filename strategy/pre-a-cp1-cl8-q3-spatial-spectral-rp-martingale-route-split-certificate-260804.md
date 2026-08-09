# Pre-A CL8 Q3 spatial-spectral reflection-positive martingale route-split certificate

**Candidate:** `PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-MARTINGALE-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-FK-MARTINGALE-FAMILY-AND-LIMITING-MEASURE-RP-WITH-CANONICAL-NONIDENTIFICATION`  
**Date:** 2026-08-04  
**Scope:** claim-nonbearing T0 theorem for the fixed-torus Q3 comparator; no C6,
CP1 or Pre-A advancement

<a id="section-1-verdict"></a>
## 1. Verdict

The eight-component Q3 `P(Phi)_2` measure constructed in EXP-000766/760 is
reflection positive for Euclidean-time reflection on its fixed two-torus.
The proof does not use the simultaneous sharp Euclidean cutoffs that failed
reflection positivity.  It conditions the terminal Wick interaction on all
temporal modes and finitely many spatial modes.  These spatial conditional
interactions are time local, converge as a martingale to the same terminal
interaction, have a uniform `L2` density bound, and define
reflection-positive measures at every spatial cutoff.  Common-Gaussian `L1`
density convergence then passes the reflected quadratic form to the limit.

At every finite spatial cutoff the retained field is a finite collection of
continuous oscillator loops.  The local Wick density is therefore the exact
Feynman--Kac loop density of a finite-dimensional Schrodinger operator.  This
closes a regulator-compatible spectral-spatial comparator family and the
reflection positivity of its limiting configuration measure.

It does not identify that family with the centered nodal CL8 Hamiltonians.
Their finite-spacing spatial symbols, Wick covariances, counterterms and unit
normalizations differ.  Nor does reflection positivity alone construct the
full canonical momentum/Weyl limit, establish all Osterwalder--Schrader or
Markov hypotheses, prove a Hadamard state, select a physical state, or compare
its energy with empty space.  Those are successor gates.

<a id="section-2-prior-art"></a>
## 2. Prior art and attribution boundary

The imported ingredients are established mathematics:

1. H. Nagoji, *Construction of the Gibbs measures associated with Euclidean
   quantum field theory with various polynomial interactions in the Wick
   renormalizable regime*, arXiv:2305.19583v2,
   <https://arxiv.org/pdf/2305.19583>, Theorem 1.7(i) and Proposition A.1,
   supplies the multivariate finite-torus normalizability and Wick limit used
   in EXP-000766/760.  That paper explicitly studies measure construction, not
   the dynamics, and supplies no reflection-positivity, Hamiltonian, KMS,
   momentum or Weyl theorem.
2. Scalar `P(phi)_2` reflection positivity, Hamiltonian reconstruction and
   thermal systems are classical constructive field theory.  A directly
   relevant modern source is C. D. Jaekel and J. Robl, *The relativistic KMS
   condition for the thermal P(phi)2 model*, arXiv:1103.3609,
   <https://arxiv.org/pdf/1103.3609>.  Its scalar theorems are not silently
   promoted to the present arbitrary eight-component Q3 polynomial.
3. Gaussian and multiplicative reflection-positivity frameworks include
   A. Jaffe and G. Ritter, *Reflection positivity and monotonicity*,
   arXiv:0705.0712, <https://arxiv.org/abs/0705.0712>, and A. Jaffe,
   C. D. Jaekel and R. E. Martinez II, *Complex classical fields: a framework
   for reflection positivity*, arXiv:1201.6003,
   <https://arxiv.org/abs/1201.6003>.  The finite-mode and limit forms below
   are nevertheless proved directly.
4. The finite-dimensional Schrodinger Feynman--Kac formula is used in its
   standard scope; see B. Simon, *Schrodinger semigroups*, Bull. Amer. Math.
   Soc. 7 (1982), 447--526,
   <https://www.ams.org/bull/1982-07-03/S0273-0979-1982-15041-8/S0273-0979-1982-15041-8.pdf>.

Spectrally cutting all Euclidean directions is not a harmless intermediate
step.  Bailleul, Dang, Ferdinand, Leclerc and Lin prove that spectrally cut
massive Gaussian fields fail reflection positivity, arXiv:2312.15511,
<https://arxiv.org/abs/2312.15511>.  This agrees with the explicit projected
`N=1` failure already registered by EXP-000767.  It does not imply that the
uncut limit fails reflection positivity.

No world-first general constructive-QFT theorem is claimed.  The
repository-specific result is the exact spatial conditional-martingale route
for the typed Q3 polynomial, the direct reflected-kernel factorization, and
the separation from centered CL8 regulators.

<a id="section-3-input"></a>
## 3. Input already closed by EXP-000766/760

Let the fixed Euclidean torus be written as

\[
 {mathbb T}_{\beta_0}\mathbin{\times}{\mathbb T}_{L_0},
\]

with one coordinate designated Euclidean time.  Let `mu` be the product of
eight independent centered massive Gaussian fields with covariance

\[
 C=(m_0^2-\partial_t^2-\partial_x^2)^{-1},\qquad m_0>0.       \tag{3.1}
\]

Use the local Q3 polynomial

\[
 P_{\rm int}(y)={1\over2}y^TK_{\rm int}y+W_4(y),             \tag{3.2}
\]

\[
 W_4(y)={g\over4}\sum_e y_e^4
 +{\lambda\over4}\sum_{e\sim f}(y_e-y_f)^2(y_e^2+y_f^2),  \tag{3.3}
\]

where `g>0`, `lambda>=0` and `K_int` is a real symmetric Q3 matrix.  Put
`F=-P_int`.  EXP-000766/760 constructs

\[
 R=\int_{{\mathbb T}^2}:F(\Phi(z)):\,dz                    \tag{3.4}
\]

as the almost-sure and `L1` Wick limit and proves

\[
 {mathbb E}_\mu e^{2R}<\infty.                             \tag{3.5}
\]

It also proves that the normalized density

\[
 \rho={e^R\over Z},\qquad Z={\mathbb E}_\mu e^R             \tag{3.6}
\]

is the full-sequence common-Gaussian `L1` limit of the original Nagoji
approximants.  Equation (3.5), not a formal power-series assertion, is the
load-bearing margin below.

<a id="section-4-spatial-martingale"></a>
## 4. Spatial-only Wick martingale

Let `P_K^x` retain the spatial Fourier modes `|k|<=K` and retain every
temporal Fourier mode.  Let

\[
 {cal G}_K^x=\sigma(P_K^x\Phi).                            \tag{4.1}
\]

The sigma-fields are nested.  Their increasing union contains every
spacetime Fourier coordinate, hence generates the full Gaussian field
sigma-field modulo null sets.

For one centered Gaussian variable, write `H_n(X;C)` for the Wick/Hermite
polynomial of degree `n` and variance `C`.  If `X=L+H`, with independent
centered Gaussians of variances `C_L` and `C_H`, then the generating function
or direct degree-zero-through-four calculation gives

\[
 {mathbb E}\left[H_n(L+H;C_L+C_H)\mid L\right]
 =H_n(L;C_L).                                                \tag{4.2}
\]

Products across the eight independent components give the multivariate
identity.  Spatial integration and linearity therefore yield, first at two
finite spatial cutoffs,

\[
 {mathbb E}_\mu[R_M^x\mid{cal G}_K^x]=R_K^x,
 \qquad M\ge K.                                             \tag{4.3}
\]

The `L1` convergence of Wick monomials used in EXP-000767 permits passage
`M->infinity` through conditional expectation.  Thus

\[
 R_K^x={\mathbb E}_\mu[R\mid{cal G}_K^x].                  \tag{4.4}
\]

Equivalently, `R_K^x` is the spacetime integral of the same polynomial
evaluated on `P_K^x Phi`, Wick ordered with its retained coincidence
covariance.  Since `P_K^x` acts only in space, this expression is local in
Euclidean time.  The martingale convergence theorem now gives

\[
 R_K^x\longrightarrow R
 \quad\hbox{almost surely and in }L^1(\mu).                 \tag{4.5}
\]

This alternate approximation has the same terminal interaction by (4.4).
It is not an assertion that the finite spatial approximants equal the finite
simultaneous sharp Euclidean approximants.

<a id="section-5-density"></a>
## 5. Uniform density control and total-variation limit

Conditional Jensen and (3.5) give the exact uniform estimate

\[
 \begin{split}
 {mathbb E}_\mu e^{2R_K^x}
 &= {mathbb E}_\mu\exp\bigl(2{mathbb E}[R\mid{cal G}_K^x]\bigr)\\
 &\le {mathbb E}_\mu e^{2R}<\infty.                       \tag{5.1}
 \end{split}
\]

Hence `{e^(R_K^x)}` is uniformly `L2` and uniformly integrable.  Equations
(4.5) and (5.1), followed by Vitali convergence, prove

\[
 \|e^{R_K^x}-e^R\|_{L^1(\mu)}\longrightarrow0.             \tag{5.2}
\]

Every positive-degree Wick monomial is centered, so
`E R_K^x=E R=0`.  Jensen then gives `Z_K=E exp(R_K^x)>=1`.
Consequently

\[
 \left\|{e^{R_K^x}\over Z_K}-{e^R\over Z}\right\|_1
 \le {\|e^{R_K^x}-e^R\|_1+|Z_K-Z|\over Z_K}
 \longrightarrow0.                                        \tag{5.3}
\]

This is total variation for densities on one common Gaussian probability
space.  It is not trace norm between density matrices on changing Hilbert
spaces.

<a id="section-6-free-rp"></a>
## 6. Direct Gaussian reflection positivity

Let

\[
 (\theta\Phi)(t,x)=\Phi(-t,x)                              \tag{6.1}
\]

modulo the time circumference, and take `0<=t<=beta_0/2` as the positive
half-circle.  For a fixed spatial mode, set

\[
 \omega_k=(m_0^2+k^2)^{1/2}.                               \tag{6.2}
\]

The periodic oscillator covariance evaluated across the reflection is

\[
 C_k(t+s)=
 {e^{-\omega_k(t+s)}+e^{-\omega_k(\beta_0-t-s)}
  \over2\omega_k(1-e^{-\beta_0\omega_k})}.                 \tag{6.3}
\]

Writing

\[
 a_k={1\over2\omega_k(1-e^{-\beta_0\omega_k})},\quad
 u_k(t)=e^{-\omega_kt},\quad
 v_k(t)=e^{-\omega_k(\beta_0/2-t)},                        \tag{6.4}
\]

gives

\[
 C_k(t+s)=a_ku_k(t)u_k(s)+a_kv_k(t)v_k(s).                 \tag{6.5}
\]

Thus every finite matrix `[C_k(t_i+t_j)]` is positive semidefinite.  The
spatial Fourier sum, its finite projections, and the product over eight
components preserve this property.  The Gaussian exponential-vector
identity then proves

\[
 {mathbb E}_\mu[\overline{A\circ\theta}\,A]\ge0            \tag{6.6}
\]

for bounded positive-half Gaussian cylinders, by bounded approximation when
needed.  This is Euclidean-time reflection positivity, not a Lorentzian cone
or an arrow of time.

<a id="section-7-interacting-rp"></a>
## 7. Finite-cutoff and limiting interacting reflection positivity

At finite `K`, every retained spatial coefficient is a one-dimensional
massive periodic Gaussian process.  Its increment moments imply a continuous
version.  The projected Q3 field is therefore a finite spatial sum of
continuous time paths, and its interaction is an ordinary time integral.
Up to the two reflection circles, which have zero spacetime measure,

\[
 R_K^x=R_{K,+}+\theta R_{K,+}.                              \tag{7.1}
\]

Finite Wick corrections add only quadratic and scalar terms.  The exact Q3
coercivity `W_4(y)>=g|y|^4/32` implies that the pointwise Wick interaction
`-:P_int(y):` is bounded above at each fixed `K`.  Hence `R_(K,+)` is bounded
above on the compact half-circle.  If `A` is a bounded positive-half
configuration cylinder, then `A exp(R_(K,+))` belongs to the positive-half
Gaussian `L2` space.  Equations (6.6) and (7.1) give

\[
 \begin{split}
 Q_K(A)
 &:={1\over Z_K}{\mathbb E}_\mu[
       \overline{A\circ\theta}\,A e^{R_K^x}]\\
 &={1\over Z_K}{\mathbb E}_\mu[
       \overline{(Ae^{R_{K,+}})\circ\theta}
       (Ae^{R_{K,+}})]\ge0.                                \tag{7.2}
 \end{split}
\]

One may equivalently insert bounded truncations and remove them by dominated
convergence; no formal multiplication of undefined half-space distributions
is used.

Let `Q(A)` be the same form with the terminal density `rho`.  From (5.3),

\[
 |Q_K(A)-Q(A)|
 \le \|A\|_\infty^2\|\rho_K^x-\rho\|_{L^1(\mu)}
 \longrightarrow0.                                        \tag{7.3}
\]

The nonnegative numbers in (7.2) therefore converge to a nonnegative limit.
The terminal Nagoji Q3 measure `rho mu` is reflection positive on bounded
positive-half configuration cylinders.

This conclusion does not contradict the EXP-000767 no-go.  That no-go is for
the induced finite-dimensional law of a simultaneous time-and-space sharp
cutoff.  Reflection positivity need not hold at those approximants for the
common limit to be reflection positive.

<a id="section-8-fk"></a>
## 8. Finite spatial cutoff Feynman--Kac comparator

Choose a real orthonormal basis of spatial modes in `P_K^x`.  For all eight
components, the retained field becomes a finite vector `q(t)` with dimension
`D_K`.  Let

\[
 A_K=(m_0^2-\partial_x^2)|_{P_K^x},\qquad
 H_{0,K}={1\over2}(-\Delta_q+q\mathbin{\cdot}A_Kq).         \tag{8.1}
\]

The normalized periodic Gaussian loop law of `H_(0,K)` has covariance
`(-partial_t^2+A_K)^(-1)`, exactly the `P_K^x` marginal of `mu`.
Let

\[
 C_K^{(\beta_0)}
 ={mathbb E}_\mu[(P_K^x\Phi_e)(t,x)^2]                    \tag{8.2}
\]

be its finite, spacetime-independent coincidence covariance and define the
ordinary polynomial

\[
 V_K^{(\beta_0)}(q)
 =\int_{{\mathbb T}_{L_0}}
   :P_{\rm int}(\phi_K(x;q)):_{C_K^{(\beta_0)}}\,dx.        \tag{8.3}
\]

Q3 coercivity makes `V_K` bounded below.  The Friedrichs form therefore
defines

\[
 H_K^{(\beta_0)}=H_{0,K}+V_K^{(\beta_0)}.                  \tag{8.4}
\]

The finite-dimensional Feynman--Kac formula identifies the interacting loop
density exactly:

\[
 {Z_K\,\operatorname{Tr}e^{-\beta_0H_{0,K}}}
 =\operatorname{Tr}e^{-\beta_0H_K^{(\beta_0)}},            \tag{8.5}
\]

with the consistent normalization convention, and bounded ordered
configuration cylinders have the corresponding heat-kernel trace formula.
Thus every spatial cutoff has a canonical finite-dimensional Schrodinger
realization.

The superscript in (8.4) is essential.  Wick ordering uses the thermal
coincidence covariance (8.2), which depends on the fixed time circumference.
This certificate does not turn these operators into one beta-independent
Hamiltonian family and does not infer a physical KMS temperature.

<a id="section-9-nonidentification"></a>
## 9. Why this is not yet the centered CL8 family

The spectral-spatial comparator uses the continuum symbol

\[
 k^2.                                                       \tag{9.1}
\]

The registered centered nodal CL8 family uses

\[
 \widehat k_a^2={4\over a^2}\sin^2{ak\over2}.              \tag{9.2}
\]

For `0<|ak|<2pi`, the strict inequality `|sin(ak/2)|<|ak/2|`
gives

\[
 \widehat k_a^2<k^2.                                       \tag{9.3}
\]

Therefore there is no finite-regulator natural equality.  Fixed-mode
`O(a^2)` convergence from EXP-000762 is not the same statement.

There is also an exact quartic obstruction, independent of the quadratic
symbol.  Take even `M`, `a=L/M`, the Q3 species singlet, and the centered
Nyquist interpolant

\[
 \phi(x)=A\cos(\pi Mx/L),\qquad \phi(x_j)=A(-1)^j.          \tag{9.4}
\]

The nodal and spectral-spatial quartic functionals are

\[
 a\sum_{j=0}^{M-1}\phi(x_j)^4=LA^4,
 \qquad
 \int_0^L\phi(x)^4dx={3\over8}LA^4.                        \tag{9.5}
\]

Their difference `(5/8)LA^4` is quartic in the amplitude.  No scalar energy
shift or scalar/Q3-quadratic counterterm can cancel it as a polynomial.  This
registers

`NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER`.

The witness is deliberately a cutoff-scale mode.  It does not obstruct the
surviving universality route: for a trigonometric field of bandwidth `K`, its
quartic has bandwidth at most `4K`, so nodal quadrature is exact when
`M>4K`.  The required bridge is asymptotic and low-local, not an exact
finite-`M` relabelling.

There are further load-bearing dictionaries still to prove:

* the `chi`, `c`, `hbar`, field and coordinate normalization;
* the subtraction of the base Gaussian mass from the target quadratic form;
* the thermal, zero-temperature and centered-lattice Wick covariance change;
* the scalar and Q3-matrix counterterm flow
  `K_(C+D)=K_C+3D[(g+lambda)I+lambda L_Q3]`;
* full-sequence state identification on a common local algebra; and
* canonical momentum and the joint Weyl functional.

Scalar energy shifts disappear from normalized configuration measures but
remain decisive for an absolute energy reference.  Nothing in this package
proves an energy below empty space.

<a id="section-10-adversarial"></a>
## 10. Adversarial review

1. **Objection: the finite simultaneous sharp cutoff is not reflection
   positive.** `DISMISSED` for the theorem actually stated.  The proof uses a
   spatial-only conditional martingale, retains all temporal modes, and never
   identifies its finite measures with the simultaneous cutoff laws.  The
   registered no-go remains valid.
2. **Objection: a local Wick density at finite spatial cutoff may not split at
   the reflection boundaries.** `DISMISSED` in the stated integral scope.
   Spatial projection commutes with time reflection and is exactly local in
   time; the two fixed circles have zero spacetime measure.  The finite-mode
   time paths are continuous and the half interactions are ordinary
   integrals.  This differs from a time-smearing mollifier, which would need
   shrinking boundary strips.
3. **Objection: `exp(R_(K,+))` may be outside the Gaussian positive-half
   algebra.** `DISMISSED` at each fixed `K`.  The negative coercive quartic
   dominates every finite Wick lower term, so the half interaction is bounded
   above.  Bounded truncation supplies an independent limiting justification.
4. **Objection: reflection positivity may be lost in the UV limit.**
   `DISMISSED` for bounded cylinders because the normalized common-base
   densities converge in `L1` and (7.3) is quantitative.  No stronger
   unbounded-observable or complete OS-topology claim is made.
5. **Objection: the Feynman--Kac Hamiltonian is automatically the registered
   CL8 Hamiltonian.** `UPHELD`.  The finite symbols, Wick schemes and unit
   dictionaries differ, and the Nyquist quartic witness rules out repair by
   scalar or quadratic counterterms at finite `M`.  Section 9 retains only an
   asymptotic universality route.
6. **Objection: configuration-measure reflection positivity supplies the
   full momentum Weyl state.** `UPHELD`.  OS reconstruction needs additional
   hypotheses, and convergence of the canonical momentum/twisted sectors is
   not proved here.
7. **Objection: the theorem selects the physical vacuum or proves a negative
   vacuum energy.** `UPHELD`.  The fixed torus, circumference and polynomial
   parameters are inputs, and no common physical reference has been built.

<a id="section-11-verification"></a>
## 11. Reproducible verification

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_rp_martingale_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_rp_martingale_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_rp_martingale_route_split_verify.py --self-test
```

The primary verifier checks the Gaussian Hermite conditional identities,
Q3 edge Wick conditioning, exact reflected-kernel Gram factorization,
martingale/Jensen and normalized-density inequalities, reflected-form `L1`
stability, finite-mode oscillator bookkeeping, the symbol mismatch, scope and
C6 firewalls.  The independent verifier uses only the Python standard
library, rational Gaussian moments and distinct finite fixtures.  The
integrated verifier reruns both children, checks stored-result freshness,
source diversity, formal records, generated surfaces and the unchanged C6
card.

<a id="section-12-next"></a>
## 12. Next proof gate

The next gate is

`PA-CP1-CL8-CENTERED-NODAL-TO-SPATIAL-SPECTRAL-RP-UNIVERSALITY-AND-TWISTED-WEYL-LIMIT`.

It must compare the centered nodal and spectral-spatial families only in a
controlled limit, with the full unit and covariance-scheme translation
declared, and prove tightness plus full-sequence state identification.  The
canonical momentum/full Weyl part must be attacked through off-diagonal or
twisted Euclidean kernels rather than Brownian path velocities.  Hadamard
form, the one-dimensional-to-three-dimensional Q3 parent, physical
preparation, energy reference and below-empty-space sign remain separate
gates.  C0, N1--N5, C6, CP1 and Pre-A remain open.
