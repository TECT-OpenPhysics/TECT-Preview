# Pre-A CL8 classical boundary-to-lattice composition certificate

Date: 2026-08-03  
Candidate: `PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0`  
Internal result: `PA-CP1-CL8-GOURSAT-PHASE-SLICE-SEMIDISCRETE-COMPOSITION-OA2`  
Parents: `PA-CP1-CL8-GOURSAT-v0` and
`PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0`  
Context only: `C6-SPACETIME-SIGNATURE`  
Task: `T-054`  
Authority: claim-nonbearing `T0` exact analytic classical candidate certificate

<a id="section-1-verdict"></a>
## 1. Verdict

The classical part of the boundary-to-lattice composition can be closed, but
only after exposing a boundary choice that the two parent packages did not
contain.

There are two honest branches.

1. On a strongly correlated class whose final Goursat phase slice has matching
   periodic jets, the slice is a periodic Cauchy datum on the natural circle.
   Exact sampling initializes the inherited semidiscrete flow with zero initial
   modified error.  The Goursat energy and variational symplectic flux become
   the periodic continuum ledgers exactly before sampling and agree with the
   finite ledgers at order `O(a^2)` for every fixed smooth family.
2. Generic admitted Goursat data do not have matching endpoint jets.  They can
   still be initialized on a larger circle by a declared finite-degree Hermite
   fill.  That branch is mathematically well defined, but its exterior energy
   and symplectic contributions must remain in a separate ledger.  It is not a
   canonical or same-global-state construction.

In both branches, periodic trigonometric reconstruction upgrades the inherited
grid-phase estimate to `O(a^2)` in one common continuum
`H1 x L2` phase space.  A newly supplied compactly supported classical phase
measure then converges in `W1` at `O(a^2)` by the identity coupling.

The old mixed gate is therefore resolved by a scope split:

- `PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-COMPOSITION` is closed at the
  declared smooth, fixed-background, fixed-domain, fixed-time scope;
- `PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION` remains open for both
  preferred or invariant classical-measure selection and quantum-state
  composition.

This is not a finite-`a` Goursat scheme and does not advance the authority or
tier of `C6`.

<a id="section-2-prior-art"></a>
## 2. Prior-art and novelty boundary

The proof uses standard mathematics: characteristic-to-Cauchy slicing,
two-endpoint Hermite interpolation, semilinear wave wellposedness on a torus,
periodic finite differences, trapezoidal quadrature, trigonometric
interpolation, Hamiltonian and variational symplectic conservation, finite
propagation, and deterministic-coupling Wasserstein estimates.

No world-first or new general theorem is claimed.  The repository-specific
content is the exact CL8/Q3 phase convention, the physical `1/8` ledger, the
direct-seam versus extension split, the fixed-smooth-family hostile controls,
and the exact incompatibility of the present one-patch contraction certificate
with the inserted full-circumference ordered PA-H1 calibration.

<a id="section-3-generic-obstruction"></a>
## 3. Why generic direct periodic composition fails

Write

\[
 s=\sqrt{c/\chi},\qquad I_\tau=[-s\tau,s\tau],
\]

and on the final Goursat slice define

\[
 u=\tau+x/s,\qquad v=\tau-x/s,
\]

\[
 q(x)=\psi(u,v),\qquad
 \Pi(x)=\chi(\psi_u+\psi_v)(u,v).                 \tag{3.1}
\]

The Goursat integral equation gives

\[
 \psi_u(u,v)=A'(u)-{1\over4\chi}
 \int_0^v\nabla W(\psi(u,\nu))\,d\nu,
\]

\[
 \psi_v(u,v)=B'(v)-{1\over4\chi}
 \int_0^u\nabla W(\psi(\sigma,v))\,d\sigma.       \tag{3.2}
\]

Set

\[
 I_A={1\over4\chi}\int_0^{2\tau}\nabla W(A(\sigma))\,d\sigma,
 \qquad
 I_B={1\over4\chi}\int_0^{2\tau}\nabla W(B(\nu))\,d\nu.
\]

At the right endpoint,

\[
 q(s\tau)=A(2\tau),
\]

\[
 {\Pi(s\tau)\over\chi}=A'(2\tau)+B'(0)-I_A,
\]

\[
 s q_x(s\tau)=A'(2\tau)-B'(0)+I_A.              \tag{3.3}
\]

At the left endpoint,

\[
 q(-s\tau)=B(2\tau),
\]

\[
 {\Pi(-s\tau)\over\chi}=A'(0)+B'(2\tau)-I_B,
\]

\[
 s q_x(-s\tau)=A'(0)-B'(2\tau)-I_B.             \tag{3.4}
\]

The parent Goursat theorem assumes only `A(0)=B(0)`.  It does not imply any of
the endpoint equalities in (3.3)--(3.4).

### 3.1 Field-jump divergence

Let

\[
 \delta=B(2\tau)-A(2\tau)\ne0.
\]

On the natural periodic grid, the wrap bond has difference
`delta+O(a)`.  Its physical gradient contribution is

\[
 {a\over8}{c\over2}
 \left|{\delta+O(a)\over a}\right|^2
 ={c|\delta|^2\over16a}+O(1).                  \tag{3.5}
\]

Thus a generic field seam makes the finite energy diverge as `a^{-1}`.  If the
field values match but the first spatial derivatives do not, the seam
Laplacian contains

\[
 {q_x(0^+)-q_x(L^-)\over a}+O(1),               \tag{3.6}
\]

which destroys the parent's `O(a^2)` residual estimate.

### 3.2 A field-value measure is not a phase measure

The Goursat parent's measure statement uses the sup topology and pushes only
the field value.  Momentum depends on derivatives.  For example,

\[
 A_n(u)=n^{-1}\sin(nu),\qquad B_n=0
\]

converges uniformly to zero while `A_n'` does not.  More strongly, around the
massless zero solution one can choose tangent traces whose final field
variation vanishes while the final momentum variation is nonzero.  Therefore
the old field-value pushforward cannot initialize a phase-space probability
law.

### 3.3 Point sampling is never exact on arbitrary frequencies

For a grid with `M` nodes,

\[
 f_M(x)=\sin(2\pi Mx/L)
\]

vanishes at every node.  Nevertheless

\[
 \int_0^L f_M^2\,dx={L\over2}.
\]

For tangent phases `v_1=(f_M,0)` and `v_2=(0,f_M)`, the sampled symplectic form
is zero while

\[
 \Omega(v_1,v_2)=-{1\over8}\int_0^L f_M^2\,dx=-{L\over16}.    \tag{3.7}
\]

Energy has the same sampling kernel.  Exact finite-`a` energy or symplectic
matching is therefore impossible on arbitrary-frequency families.  The
positive theorem below is deliberately restricted to fixed smooth families.

<a id="section-4-phase-map"></a>
## 4. The strong phase-slice map

Assume

\[
 A,B\in C^8([0,2\tau];\mathbb R^8),\qquad A(0)=B(0),          \tag{4.1}
\]

and assume the common strict Goursat self-map and contraction gates of the
parent certificate.  Its regularity bootstrap gives

\[
 \psi\in C^8(D_\tau;\mathbb R^8).
\]

Consequently (3.1) gives

\[
 q\in C^8(I_\tau;\mathbb R^8),\qquad
 \Pi\in C^7(I_\tau;\mathbb R^8).                \tag{4.2}
\]

The map

\[
 S_\tau:(A,B)\longmapsto(q,\Pi)                 \tag{4.3}
\]

is continuous from the `C8` trace topology into `C7 x C6` on every common
strict gate.  To see this, differentiate the Volterra equation successively.
At each order the highest derivative satisfies a linear Volterra equation with
continuous coefficients determined by lower derivatives.  The factorial
Volterra estimate used for parent uniqueness gives continuous dependence;
induction closes through order seven.  No higher-derivative smallness gate is
needed, although the constants depend on the common compact derivative range.

This stronger topology and full phase map are new inputs to the measure result
in Section 11.  They are not consequences of the parent's field-value measure.

<a id="section-5-domain-branches"></a>
## 5. Two domain branches

### 5.1 Direct periodic-seam branch

Set

\[
 L=2s\tau
\]

and identify the endpoints of `I_tau`.  Require

\[
 \partial_x^m q(-s\tau)=\partial_x^m q(s\tau),
 \qquad 0\le m\le7,                              \tag{5.1}
\]

\[
 \partial_x^m\Pi(-s\tau)=\partial_x^m\Pi(s\tau),
 \qquad 0\le m\le6.                              \tag{5.2}
\]

Then

\[
 q\in C^7_{\rm per}(\mathbb T_L),\qquad
 \Pi\in C^6_{\rm per}(\mathbb T_L).             \tag{5.3}
\]

Conditions (5.1)--(5.2) are a strong correlated-data restriction.  They are
not a derived periodic boundary law or a state-selection theorem.

### 5.2 Deterministic Hermite-extension branch

For arbitrary data satisfying (4.1), choose `L>2s tau` and put

\[
 d=L-2s\tau>0.
\]

On the complementary arc set

\[
 y={x-s\tau\over d}\in[0,1].
\]

For an integer `m`, let `V_m` be the `2(m+1)` square confluent matrix that maps
the coefficients of a polynomial of degree at most `2m+1` to its derivatives
of order `0,...,m` at `y=0` and `y=1`.  If `p` had all these endpoint jets zero,
it would have zeros of multiplicity `m+1` at both endpoints and hence degree at
least `2m+2` unless `p=0`.  Thus `V_m` is invertible.

Use `m=7` for `q` and prescribe

\[
 p_q^{(k)}(0)=d^k q^{(k)}(s\tau),\qquad
 p_q^{(k)}(1)=d^k q^{(k)}(-s\tau),
 \quad0\le k\le7.                                \tag{5.4}
\]

Use `m=6` for `Pi` and prescribe the analogous jets through order six.  The
resulting extension operators satisfy

\[
 E_7q\in C^7_{\rm per}(\mathbb T_L),\qquad
 E_6\Pi\in C^6_{\rm per}(\mathbb T_L).           \tag{5.5}
\]

For fixed `d>0`, the coefficient maps are finite-dimensional linear maps, so

\[
 \|E_m f\|_{C^m(\mathbb T_L)}
 \le C_{m,d}\|f\|_{C^m(I_\tau)}.                 \tag{5.6}
\]

The primary and independent executables invert `V_7` and `V_6` by unrelated
exact-arithmetic implementations and reproduce every declared jet.

The extension is deterministic after `L` and the Hermite convention are
declared, but it is not canonical physics.  A different extension changes the
global periodic state outside `I_tau`.

<a id="section-6-cauchy"></a>
## 6. Smooth periodic Cauchy continuation

Either branch gives phase data

\[
 q_0\in H^7(\mathbb T_L;\mathbb R^8),\qquad
 v_0=\Pi_0/\chi\in H^6(\mathbb T_L;\mathbb R^8).               \tag{6.1}
\]

Consider

\[
 \chi\Psi_{tt}-c\Psi_{xx}+\nabla W(\Psi)=0.       \tag{6.2}
\]

Standard semilinear-wave contraction gives a unique local solution in

\[
 C^0_tH^7_x\cap C^1_tH^6_x\cap C^2_tH^5_x.       \tag{6.3}
\]

For completeness, the continuation mechanism is recorded.  The Hamiltonian

\[
 H={1\over8}\int_{\mathbb T_L}
 \left({|\Pi|^2\over2\chi}+{c\over2}|\Psi_x|^2+W(\Psi)\right)dx
                                                               \tag{6.4}
\]

is conserved.  The Q3 lock is nonnegative and the onsite quartic is coercive
up to a finite additive lower bound.  Therefore (6.4) controls the velocity
`L2` norm, the spatial derivative `L2` norm, and the field `L4` norm up to a
constant.  On a finite circle this controls `H1`, and one-dimensional Sobolev
embedding controls `L-infinity`.

Differentiate (6.2).  Polynomial Moser estimates and the already controlled
lower norms give, successively,

\[
 {d\over dt}Y_m(t)\le C_m(1+Y_{m-1}(t))Y_m(t),
 \qquad2\le m\le7,                                \tag{6.5}
\]

where `Y_m` is equivalent to
`||Psi||_{H^m}^2+||Psi_t||_{H^(m-1)}^2` after an additive lower-order term.
Induction and Gronwall prevent finite-time blowup of any `Y_m`.  Thus (6.3)
extends across every fixed finite interval `[0,T]`.

In one dimension, `H7` embeds into `C6`.  Hence the solution satisfies the
semidiscrete parent's requirements

\[
 \Psi\in C^0([0,T];C^6_{\rm per})
 \cap C^2([0,T];C^0).                             \tag{6.6}
\]

Its fixed-`T` component-max radius and derivative bounds `M_4,M_6` are finite.
On a compact `C8` boundary-data set inside common strict Goursat gates, all
these quantities are uniform by continuity of the slice, extension, and
Cauchy flow maps.

<a id="section-7-sampling"></a>
## 7. Exact initialization and inherited `O(a^2)` convergence

On the direct branch, take even `M` and

\[
 a={L\over M}={2s\tau\over M},\qquad
 x_j=-s\tau+ja.                                   \tag{7.1}
\]

Then the null coordinates of every grid node are exactly

\[
 u_j={2\tau j\over M},\qquad
 v_j=2\tau-u_j.                                   \tag{7.2}
\]

The inherited fine size is `N=2M`, hence divisible by four.  On the extension
branch, use the same periodic grid on the declared larger circle.

In either branch initialize

\[
 \psi_j^a(0)=q_0(x_j),\qquad
 \Pi_j^a(0)=\Pi_0(x_j).                           \tag{7.3}
\]

Relative to the sampled continuum Cauchy solution,

\[
 e(0)=0,\qquad e_t(0)=0,
\]

so the modified initial error energy is exactly zero.  The parent theorem
therefore gives

\[
 \sup_{0\le t\le T}
 \left(
 \|\psi^a-R_a\Psi\|_{H_a^1}
 +\|\psi_t^a-R_a\Psi_t\|_a
 \right)
 \le C_Ta^2.                                      \tag{7.4}
\]

This is continuum-solve, phase-slice, then sample.  It does not discretize the
null triangle and says nothing about sample-boundary-then-solve.

<a id="section-8-energy"></a>
## 8. Energy consistency and the extension ledger

For any fixed smooth periodic phase pair, periodic composite trapezoidal
quadrature gives

\[
 \left|a\sum_jF(x_j)-\int_0^L F(x)dx\right|
 \le {La^2\over12}\|F''\|_\infty.                \tag{8.1}
\]

For the gradient term, `D_a^+q_j` is the cell average of `q_x`, so

\[
 \int_0^L|q_x|^2dx-a\sum_j|D_a^+q_j|^2
 =\sum_j\int_{x_j}^{x_{j+1}}
 |q_x-(q_x)_{\rm cell\ avg}|^2dx.                \tag{8.2}
\]

The mean-zero Poincare inequality on each cell gives

\[
 0\le(8.2)\le {a^2\over\pi^2}\|q_{xx}\|_{L^2}^2.             \tag{8.3}
\]

With

\[
 F={|\Pi|^2\over2\chi}+W(q),
\]

the physical normalization yields

\[
 |H_a(R_aq,R_a\Pi)-H(q,\Pi)|\le C_Ea^2,          \tag{8.4}
\]

\[
 C_E={L\over96}\|F''\|_\infty
 +{c\over16\pi^2}\|q_{xx}\|_{L^2}^2.           \tag{8.5}
\]

Let `(psi^a(t),Pi^a(t))` be the finite flow initialized by the sampled phase,
and let `(Psi(t),Pi(t))` be the continuum flow.  Separate conservation gives
the precise transported identity

\[
 H_a(\psi^a(t),\Pi^a(t))-H(\Psi(t),\Pi(t))
 =H_a(R_aq_0,R_a\Pi_0)-H(q_0,\Pi_0).             \tag{8.6}
\]

Thus the absolute value in (8.6) is bounded by `C_E a^2` at every paired
time.  The sampled continuum expression `H_a(R_a Psi(t),R_a Pi(t))` is not
itself asserted to be conserved.

On the direct branch, the continuum identity from the Goursat parent gives

\[
 H(q,\Pi)=E_\tau=\mathcal F_H,                   \tag{8.7}
\]

where `F_H` denotes the exact two-sheet null flux.

On the extension branch, the circle splits into the original slice and its
complementary arc:

\[
 H(E_7q,E_6\Pi)=E_\tau+H_{\rm ext}.              \tag{8.8}
\]

The signed quantity `H_ext` is the same Hamiltonian density integrated over
the Hermite fill.  It is generally nonzero, may depend strongly on the gap
length, and cannot be discarded or called physical boundary energy.

<a id="section-9-symplectic"></a>
## 9. Variational symplectic consistency

On the direct branch, take boundary variations `(delta A_i,delta B_i)` tangent
to every seam constraint (5.1)--(5.2), and let
`(xi_i,varpi_i)=D S_tau[A,B](delta A_i,delta B_i)`.  This restriction matters:
an arbitrary Goursat variation around a seam-compatible background need not be
periodic.  On the extension branch, apply the fixed linear Hermite extension
to arbitrary admitted Goursat tangent phases.  Define

\[
 G_\Omega=\varpi_1\mathbin\cdot\xi_2
 -\varpi_2\mathbin\cdot\xi_1.
\]

The same periodic quadrature estimate gives

\[
 |\Omega_a(R_av_1,R_av_2)-\Omega(v_1,v_2)|
 \le {La^2\over96}\|G_\Omega''\|_\infty.        \tag{9.1}
\]

On the direct branch, the parent's flux theorem gives

\[
 \Omega=\Omega_H                                  \tag{9.2}
\]

before sampling.  On the extension branch,

\[
 \Omega=\Omega_H+\Omega_{\rm ext}.               \tag{9.3}
\]

Let `(xi_i^a(t),varpi_i^a(t))` be the two finite variational flows initialized
by sampling `(xi_i(0),varpi_i(0))`, and let `(xi_i(t),varpi_i(t))` be the
corresponding continuum variational flows.  Separate symplectic conservation
gives

\[
 \begin{split}
 &\Omega_a((\xi_1^a(t),\varpi_1^a(t)),
                 (\xi_2^a(t),\varpi_2^a(t)))
 -\Omega((\xi_1(t),\varpi_1(t)),
                (\xi_2(t),\varpi_2(t)))\\
 &\quad=
 \Omega_a(R_av_1(0),R_av_2(0))-\Omega(v_1(0),v_2(0)).          \tag{9.4}
 \end{split}
\]

The right side is bounded by (9.1).  The form evaluated on a freshly sampled
continuum tangent at each time is not asserted to be conserved.  Equation
(3.7) forbids replacing `O(a^2)` by exact finite-`a` equality on
arbitrary-frequency families.

<a id="section-10-reconstruction"></a>
## 10. A common continuum phase space

Let `J_a` be the real periodic trigonometric interpolant of the `M` grid
values, using the standard even-`M` cosine Nyquist convention.  If `z_N`
denotes the Nyquist component, discrete Parseval and the half-weight of the
real Nyquist cosine give

\[
 \|f\|_{L^2_8}^2={1\over8}\int_{\mathbb T_L}|f|^2dx,
 \qquad
 \|f\|_{H^1_8}^2={1\over8}\int_{\mathbb T_L}
 (|f|^2+|f_x|^2)dx.                              \tag{10.0}
\]

\[
 \|J_az\|_{L^2_8}^2
 =\|z\|_a^2-{1\over2}\|z_N\|_a^2,
 \qquad
 {1\over2}\|z\|_a^2\le\|J_az\|_{L^2_8}^2
 \le\|z\|_a^2.                                  \tag{10.1}
\]

For every grid Fourier mode with `|ka|<=pi`,

\[
 {|k|\over 2|\sin(ka/2)|/a}\le{\pi\over2},       \tag{10.2}
\]

because `sin y >= 2y/pi` on `[0,pi/2]`.  Hence

\[
 \|\partial_xJ_az\|_{L^2_8}
 \le{\pi\over2}\|D_a^+z\|_a.                   \tag{10.3}
\]

Periodic Fourier interpolation also gives

\[
 \|J_aR_af-f\|_{H^1_8}\le C a^2\|f\|_{H^3},
\]

\[
 \|J_aR_ah-h\|_{L^2_8}\le C a^2\|h\|_{H^2}.    \tag{10.4}
\]

Only the upper bound in (10.1) is needed.  Combining (7.4),
(10.1)--(10.4), and the regularity of Section 6 yields

\[
 \sup_{0\le t\le T}
 \left(
 \|J_a\psi^a-\Psi\|_{H^1_8}
 +\|J_a\psi_t^a-\Psi_t\|_{L^2_8}
 \right)\le C_T'a^2.                             \tag{10.5}
\]

This does not contradict the parent warning about ordinary piecewise-linear
reconstruction, whose continuous `H1` derivative error is generally only
first order.  `J_a` is a separately declared, nonlocal reconstruction.

<a id="section-11-measure"></a>
## 11. Supplied classical phase-measure convergence

Let `K` be a compact subset of the `C8` boundary-data space inside common
strict Goursat gates.  On the direct branch, require `K` to be supported on the
seam conditions (5.1)--(5.2).  Let `mu` be any supplied Borel probability
measure on `K`.

Let

\[
 F_t:K\longrightarrow
 X=H^1_8(\mathbb T_L;\mathbb R^8)
 \times L^2_8(\mathbb T_L;\mathbb R^8)
\]

be the phase-slice, chosen-domain, continuum-flow map.  Let `F_a,t` additionally
sample, evolve by the semidiscrete equation, and reconstruct by `J_a`.

Compactness and Section 6 make the constant in (10.5) uniform on `K`.  Couple
`F_a,t(z)` with `F_t(z)` using the same `z`.  Then

\[
 W_1^X((F_{a,t})_*\mu,(F_t)_*\mu)
 \le\int_K\|F_{a,t}(z)-F_t(z)\|_X\,d\mu(z)
 \le C_{K,T}a^2.                                  \tag{11.1}
\]

The measure, compact support, seam correlation or extension rule, and
classical topology are inputs.  Equation (11.1) selects no invariant,
thermal, vacuum, Hadamard, or quantum state.

<a id="section-12-tail"></a>
## 12. Extension independence inside the continuum cone and finite-`a` tails

Two smooth extensions that agree on `I_tau` produce identical continuum
solutions at points whose backward cone remains inside `I_tau`.  If a compact
subinterval lies a distance `rho` from both endpoints, the solutions agree
there for elapsed times not exceeding `rho/s`.

Their matched semidiscrete solutions need not agree exactly at any positive
time.  Applying (7.4) to both and restricting to nodes in the common continuum
region gives an aggregate `O(a^2)` difference.  This is the strongest
extension-independence statement supplied here.

The registered finite-`a` variational witness tails remain nonzero.  Neither
the direct branch nor the extension branch proves exact support, a pointwise
distance-decay rate, a Lieb--Robinson estimate, or a finite-`a` characteristic
sheet.

<a id="section-13-calibration"></a>
## 13. Exact PA-H1 full-circumference gate obstruction

The direct branch has natural length `L=2s tau`.  The inserted PA-H1 tangent
calibration uses

\[
 L={\pi\over2},\qquad {c\over\chi}=1,
 \qquad {-2r\over\chi}=9.                        \tag{13.1}
\]

Thus `s=1` and covering the full circle by one final Goursat slice requires

\[
 \tau={\pi\over4}.                               \tag{13.2}
\]

To include the ordered amplitude, the parent max ball must have

\[
 R\ge v=\sqrt{-r/g}.
\]

Because `lambda>=0`,

\[
 \ell_R=|r|+(3g+36\lambda)R^2
 \ge4(-r)=18\chi.                                \tag{13.3}
\]

The current one-patch contraction factor therefore obeys

\[
 q={\tau^2\ell_R\over4\chi}
 \ge{9\pi^2\over32}>1.                           \tag{13.4}
\]

Even if the fixed point is shifted to the ordered equilibrium, the collective
Hessian magnitude is `-2r=9chi`, so a direct local Lipschitz contraction still
has

\[
 q_{\rm shifted}\ge{9\pi^2\over64}>1.            \tag{13.5}
\]

Equations (13.4)--(13.5) reject only the current single-patch Banach
certificate for a nontrivial full-circumference ordered neighborhood.  The
exact constant ordered equilibrium is a special solution, and existence itself
is not disproved.  The next classical target is a multi-patch, continuation,
or global Goursat theorem:

`PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE`.

<a id="section-14-gate-split"></a>
## 14. Composition-gate scope split

The parent gate combined classical and quantum requirements.  It is not
honest to mark that mixed object simply closed.  Its obligations are routed as
follows.

| Parent obligation | Disposition |
|---|---|
| Finite-`a` characteristic scheme or proved boundary-to-Cauchy initialization | `PROVED` by the second alternative only; no finite-`a` characteristic scheme |
| Same-domain sampling and required regularity | `PROVED` on the direct seam branch and the declared larger-circle extension branch |
| Energy and symplectic consistency | `PROVED` at `O(a^2)` for fixed smooth families; exact finite-`a` equality rejected |
| Classical measure convergence | `PROVED` for a newly supplied compact `C8` phase measure |
| Common selected state | `MOVED` to `PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION`, covering preferred or invariant classical-measure selection and quantum-state composition |
| Finite-`a` regulator tail | `CONTROLLED` only in inherited aggregate convergence; registered nonzero witnesses retained |
| Moving characteristic boundary or ghost values | `NOT REQUIRED` on the continuum-slice-then-fixed-Cauchy branch; no moving-boundary theorem |

The original route ID
`PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION` is therefore
`RESOLVED BY SCOPE SPLIT`, not unconditionally closed.

<a id="section-15-devil"></a>
## 15. Devil's-advocate review

1. **Generic Goursat endpoints are not periodic.**  **UPHELD.**  Direct
   composition is restricted by (5.1)--(5.2); generic data use a declared
   extension with an exterior ledger.
2. **A Hermite fill silently adds energy.**  **UPHELD AND EXPOSED.**  Equation
   (8.7) retains `H_ext`; no same-global-state claim is made.
3. **The old field measure loses momentum.**  **UPHELD.**  Section 11 requires
   a new phase-capable measure in the stronger `C8` topology.
4. **Sampling cannot be exactly symplectic.**  **UPHELD.**  The explicit
   high-frequency kernel (3.7) forbids exactness; only fixed-smooth-family
   `O(a^2)` consistency is claimed.
5. **The parent warned that reconstruction is only first order in `H1`.**
   **MITIGATED.**  That warning concerns piecewise-linear reconstruction.  The
   separately declared trigonometric `J_a` obeys (10.1)--(10.4).
6. **Periodic future regularity was merely assumed.**  **DISMISSED at the
   declared class.**  Section 6 records the coercive-energy continuation and
   higher-Sobolev induction from the constructed `H7 x H6` data.
7. **The PA-H1 full circle is now proved.**  **UPHELD AS FALSE.**  Equations
   (13.4)--(13.5) show that the current single-patch certificate does not cover
   its ordered neighborhood.
8. **The extension removes finite-`a` tails.**  **UPHELD AS FALSE.**  Section 12
   retains the registered nonzero variational witnesses and claims only
   aggregate convergence.
9. **A convergent classical phase measure is a vacuum state.**  **UPHELD AS
   FALSE.**  The probability measure is supplied and remains classical.
10. **This closes CP1 or Pre-A.**  **UPHELD AS FALSE.**  Preferred-state and
    measure selection, quantum composition, full-circumference,
    full-dimensional, physical-reference, and cosmological gates remain open.

<a id="section-16-reproduction"></a>
## 16. Reproduction

Run from the repository root with the repository virtual environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_classical_boundary_lattice_oa2.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_classical_boundary_lattice_oa2_independent.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_classical_boundary_lattice_oa2_verify.py --selftest
```

The primary executable uses symbolic exact arithmetic.  The independent
executable imports neither the primary code nor SymPy/flint and rebuilds the
Hermite systems by `Fraction` Gaussian elimination.  The integrated verifier
reruns both children, compares common exact outputs, audits parent provenance
and every scope flag, and rejects stale stored JSON.

<a id="section-17-no-overclaim"></a>
## 17. No-overclaim boundary

This certificate proves a smooth classical fixed-background composition only
after either strong periodic seam correlations or a declared extension with
explicit exterior ledgers.  It does not prove generic direct periodic
composition, a canonical extension, a finite-`a` Goursat scheme, exact
finite-`a` energy or symplectic matching, arbitrary-frequency convergence,
exact finite-`a` support, the current one-patch theorem at the full ordered
PA-H1 circumference, growing-time or thermodynamic regulator removal, full
`3+1` dynamics, a quantum continuum or selected state, physical empty space or
a below-empty-space sign, cooling, gravity, an event horizon, advancement of
`C6`, CP1, or Pre-A.
