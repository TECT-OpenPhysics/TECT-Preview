# Pre-A CP1/CL8 Q3 fixed-torus OS, KMS, Markov and reference split

**Candidate:** `PA-CP1-CL8-Q3-FIXED-TORUS-OS-KMS-MARKOV-REFERENCE-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-Q3-FIXED-TORUS-PERIODIC-OS-DOMAIN-MARKOV-KMS-AND-STRICT-CENTERED-FREE-ENERGY-COMPARATOR`  
**Exploration:** `EXP-000773`
**Authority:** claim-nonbearing T0 analytic theorem

## 1. Result and exact scope

Let

\[
 Q=\mathcal S'(\mathbb T_{\beta _0}\mathbin\times\mathbb S_L)^8,
 \qquad C=(m_0^2-\partial_t^2-\partial_x^2)^{-1},
 \qquad m_0>0,                                             \tag{1.1}
\]

and let `mu` be the centered Gaussian law with covariance `C`.  On the fixed
finite torus, take the EXP-000772 tuned bounded-renormalized-matrix Q3 limit

\[
 R=-\int :P(\Phi):\,dt\,dx,\qquad
 d\nu=Z^{-1}e^R d\mu,\qquad Z=\mathbb E_\mu e^R.          \tag{1.2}
\]

The inputs from EXP-000772 are

\[
 e^R\in L^p(\mu)\quad(1\leq p<\infty),                  \tag{1.3}
\]

full-sequence `L1` and total-variation density convergence, time-reflection
positivity, and a full-sequence regular fixed-band Weyl limit.

This certificate proves four consequences at fixed `beta0,L`:

1. the limiting Schwinger functions have the regularity and symmetries needed
   for a periodic generalized path space;
2. the measure has a sharp-time algebra, closed `L2` reflection positivity,
   and a two-sided germ-domain Markov property;
3. periodic Osterwalder--Schrader reconstruction gives an abstract
   stochastically positive `beta0`-KMS system;
4. in the fixed whole-Wick convention, its free energy is strictly lower than
   that of the named Gaussian reference, with a scalar-gauge-invariant
   relative-entropy formulation.

The fourth statement is the previously missing *below-reference* theorem.  It
does not identify the Gaussian reference with physical empty space.

## 2. Schwinger regularity and torus covariance

For smooth real test functions `f_j`, Holder's inequality, (1.3), and Gaussian
hypercontractivity give

\[
 |\mathbb E_\nu\prod_{j=1}^n\Phi(f_j)|
 \leq C_{n,p}\prod_{j=1}^n\langle f_j,Cf_j\rangle^{1/2}. \tag{2.1}
\]

Thus every `n`-point form is a continuous distribution.  The same estimate
with an exponential of one finite-dimensional Gaussian vector shows that its
characteristic functional has all finite real exponential moments.  Bosonic
permutation symmetry and reality are automatic.

The identified terminal spectral law restores continuous translations in
both torus coordinates.  It is covariant under the rectangular-torus
isometries that preserve the periods and the local Q3 action.  This is not
full `E(2)` covariance: when `beta0` and `L` are not interchangeable, a
quarter rotation is not a torus symmetry.  The internal symmetry is likewise
only the symmetry of the Q3 polynomial and renormalized matrix; no `O(8)`
claim is made.

## 3. Closed reflection-positive algebra

Let `theta` reflect the beta circle through a time diameter and let
`A_+^cyl` be bounded cylinders supported in the positive open semicircle.
EXP-000772 gives

\[
 \langle F,F\rangle_{OS}
 :=\mathbb E_\nu[\overline{F\circ\theta}F]\geq0,
 \qquad F\in A_+^{cyl}.                                  \tag{3.1}
\]

Reflection invariance and Cauchy--Schwarz give

\[
 |\mathbb E_\nu[\overline{F\circ\theta}G]|
 \leq\|F\|_{L^2(\nu)}\|G\|_{L^2(\nu)}.                \tag{3.2}
\]

Consequently (3.1) extends by density to the closed positive-half `L2`
algebra.  Time translations conjugate the result to every diameter.  This is
thermal, beta-periodic reflection positivity.  It is not a Lorentzian
positivity or spectrum condition.

## 4. Sharp-time fields and generation

For spatial Fourier momentum `k`, put

\[
 \omega_k=(m_0^2+k^2)^{1/2}.
\]

The free sharp-time covariance is

\[
 c_k(0)={1\over\beta_0}\sum_{n\in\mathbb Z}
 {1\over(2\pi n/\beta_0)^2+\omega_k^2}
 ={1\over2\omega_k}\coth {\beta_0\omega_k\over2}.      \tag{4.1}
\]

For a smooth spatial `f`, let `eta_epsilon` approach `delta_t`.  Formula
(4.1) and its unequal-time version make
`Phi(eta_epsilon tensor f)` Cauchy in Gaussian `L2`, hence in every finite
Gaussian `Lq`.  With `rho=dnu/dmu` and `rho in Lp(mu)` for every finite `p`,

\[
 \|X\|_{L^2(\nu)}^2
 =\mathbb E_\mu[\rho |X|^2]
 \leq\|\rho\|_{L^p(\mu)}\|X\|_{L^{2p'}(\mu)}^2.        \tag{4.2}
\]

Therefore the mollified fields converge in `L2(nu)` to a well-defined
`Phi_t(f)`.  Covariance differences in (4.1), followed by (4.2), prove
`L2(nu)` continuity in `t`.

For smooth `F(t,x)`, spatial-mode truncation followed by temporal Riemann
sums gives

\[
 \Phi(F)=\lim_N\sum_j\Delta t_j\,\Phi_{t_j}(F(t_j,\cdot))
 \quad\hbox{in }L^2(\nu).                               \tag{4.3}
\]

Thus time translates of the sharp-time algebra generate the full field
sigma algebra and the OS cyclic subspace.  Equivalently, one may use the
boundary-germ algebra; no pathwise trace of a two-dimensional distribution is
being assumed.

## 5. Two-sided germ-domain Markov theorem

Let `D` be a time slab whose boundary consists of two time circles, and let
`G_boundary` be the decreasing germ sigma algebra of those boundary slices.
The inverse free covariance

\[
 C^{-1}=m_0^2-\Delta                                      \tag{5.1}
\]

is local.  The standard orthogonal decomposition of its Cameron--Martin
space into the harmonic boundary extension plus zero-boundary fields on `D`
and `D^c` proves Gaussian conditional independence across `G_boundary`.

The interaction contains no derivatives.  For every small `epsilon>0`, its
Wick chaoses lie in `H^{-epsilon}`, while a Lipschitz slab indicator lies in
`H^s` for every `s<1/2`.  Choosing `epsilon<s` defines the exact local split

\[
 R=R_D+R_{D^c}.                                          \tag{5.2}
\]

Condition the Gaussian law on the boundary germ.  Its inside and outside
laws factor, while the Radon--Nikodym weight factorizes as
`exp(R_D)exp(R_Dc)`.  Bayes' formula therefore gives, for bounded inside `F`
and outside `G`,

\[
 \boxed{
 \mathbb E_\nu[FG\mid G_{boundary}]
 =\mathbb E_\nu[F\mid G_{boundary}]
  \mathbb E_\nu[G\mid G_{boundary}].}                   \tag{5.3}
\]

This is a two-sided domain-Markov theorem.  The two boundary components are
essential on a closed beta circle.  Equation (5.3) is not being advertised
as an ordinary one-sided homogeneous Markov-chain statement after the
closing boundary is forgotten.

## 6. Periodic OS reconstruction and the KMS result

Sections 2--5 verify the periodic generalized-path-space inputs:

- a normalized beta-periodic probability space;
- a strongly continuous measure-preserving time-translation group;
- time reflection and closed positive-half reflection positivity;
- a sharp-time or boundary-germ algebra;
- generation and cyclicity by its translates.

The periodic Osterwalder--Schrader reconstruction theorem therefore gives,
uniquely up to the usual reconstruction equivalence,

\[
 (\mathcal H_{OS},\mathcal A,\Omega,\alpha_t),           \tag{6.1}
\]

a stochastically positive `W*`-dynamical system whose vector state is
`beta0`-KMS.  The local symmetric semigroups are the OS compressions of the
circle translations, and their gluing gives the thermal Liouvillean.

The affine seam of EXP-000772 identifies its fixed-band Weyl matrix elements
with the reconstructed sharp-time elements.  Hence the previously obtained
regular Weyl state is not merely an unrelated cluster state on those bands.

This theorem reconstructs a thermal Liouvillean.  It does not assert that the
generator is nonnegative, that the state is pure, or that `beta0` was selected
by physics.  A finite beta circle is not a positive-energy vacuum theorem.

## 7. Strict free-energy ordering below the named reference

At every centered regulator, write

\[
 R_M=-\int :P_M(Y_M):\,dz_M,
 \qquad Z_M=\mathbb E_{\mu_M}e^{R_M}.                    \tag{7.1}
\]

Whole-polynomial Wick centering gives `E_muM R_M=0`.  The fourth Wiener chaos
is nonzero.  Indeed, restrict its homogeneous quartic to one species and the
constant normalized spacetime mode.  The three Q3 edges incident on that
species give

\[
 \operatorname{Proj}_4 R_M
 \supset -{g+3\lambda\over4\beta_0L}:z^4:,
 \qquad g>0,\quad\lambda\geq0.                           \tag{7.2}
\]

Thus `R_M` is not constant.  Strict Jensen yields

\[
 Z_M>e^{\mathbb E R_M}=1,
 \qquad
 \Delta F_M^W=-{1\over\beta_0}\log Z_M<0,              \tag{7.3}
\]

and the free-energy density obeys

\[
 \Delta f_M^W=-{1\over\beta_0L}\log Z_M<0.             \tag{7.4}
\]

EXP-000772 proves `R_M -> R` in `L2` and `exp(R_M) -> exp(R)` in `L1`.
The constant-mode projection (7.2) survives in the terminal fourth chaos, so
`R` is also nonconstant.  Hence, on the fixed continuum torus,

\[
 \boxed{Z>1,\qquad\Delta F_{\beta_0,L}^W<0,
 \qquad\Delta f_{\beta_0,L}^W<0.}                       \tag{7.5}
\]

This is a strict result, not a candidate ranking or numerical indication.

## 8. Scalar-gauge-invariant statement and the physical firewall

The raw number in (7.5) depends on the declared whole-Wick scalar convention.
The convention-independent comparison is relative entropy.  Since

\[
 {d\nu\over d\mu}={e^R\over Z},
\]

we have

\[
 D(\mu\|\nu)=\mathbb E_\mu\log {d\mu\over d\nu}
 =\log Z-\mathbb E_\mu R.                               \tag{8.1}
\]

Therefore

\[
 \boxed{
 \Delta F_{ref}:=-{1\over\beta_0}D(\mu\|\nu)
 =-{1\over\beta_0}(\log Z-\mathbb E_\mu R)<0.}        \tag{8.2}
\]

Under `R -> R-C`, both `log Z` and `E R` decrease by `C`; (8.2) is invariant.
In the centered representative, `E R=0`, so (8.2) equals (7.5).  It is the
Gibbs variational statement that the exact tilted law has strictly lower
variational free energy than the specified Gaussian trial law.

The distinction is decisive:

- **proved:** the tuned Q3 law is strictly below its explicitly named
  Gaussian reference at fixed `beta0,L`;
- **not proved:** that this Gaussian law is the physical no-condensate state,
  cosmic empty space, or a gravitationally normalized vacuum.

The reference contains inserted `m0,beta0,L`.  Adding a local scalar to a
candidate action preserves every normalized state and correlation while
moving its raw energy.  The existing
`NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR` therefore remains
the correct absolute-energy obstruction.  The next physical comparison must
derive a common reference and one beta-independent Hamiltonian rather than
rename `mu` as empty space.

## 9. Vacuum, Hadamard, phase-transition and dimensional boundaries

Regular Weyl continuity controls the identity on fixed canonical modes.  It
does not control ultraviolet wavefront sets.  The standard theorem taking
passive ground/KMS states to a Hadamard two-point function assumes fields
obeying a linear hyperbolic equation.  The nonlinear interacting Q3
`P(phi)_2` field does not satisfy that hypothesis.  No Hadamard claim can be
imported from it.

The appropriate later target is an interacting `n`-point microlocal spectrum
condition or relativistic-KMS tube analyticity after a local Lorentzian net is
constructed.  A vacuum target additionally requires `beta0 -> infinity` for
one beta-independent renormalized Hamiltonian, with tightness, uniqueness,
reflection positivity and a positive-energy spectral theorem.

Likewise, one fixed compact torus proves no thermodynamic phase transition.
That requires a controlled `L -> infinity`, zero-temperature, or other
declared nonanalytic limit and an order parameter.  This package does not
construct the original three-dimensional Q3 parent, derive physical light,
or advance C6.

## 10. Prior art and adversarial review

Periodic OS/KMS reconstruction, Gaussian domain Markov, and the Gibbs
variational identity are established mathematics.  Gerard--Jaekel and
Jaekel--Robl provide scalar thermal `P(phi)_2` precedents; Nagoji provides the
multivariate constructive-measure input used upstream.  This certificate
checks the exact Q3 interface and scope.  It is not a novelty claim.

Hostile objections resolved or retained are:

1. **Reflection positivity only held on bounded cylinders. DISMISSED.**
   Equation (3.2) gives the closed `L2` extension.
2. **A two-dimensional distribution has no naive time trace. DISMISSED.**
   Equations (4.1)--(4.3) construct an `L2` sharp-time boundary value.
3. **Time-zero observables may fail to generate the field. DISMISSED.**
   Smooth spacetime smearings are `L2` limits of temporal Riemann sums.
4. **Total variation automatically preserves Markov conditional
   independence. UPHELD AS A WARNING.**  Markov is proved separately from
   Gaussian locality, local Wick-action additivity and Bayes.
5. **A circle process is ordinary one-sided Markov. UPHELD AS TOO STRONG.**
   The proved statement conditions on both boundary slices.
6. **KMS means vacuum. UPHELD AS FALSE.**  The reconstructed generator is a
   thermal Liouvillean, not a nonnegative vacuum Hamiltonian.
7. **Regular Weyl implies Hadamard. UPHELD AS FALSE.**  Identity continuity
   supplies no microlocal spectrum bound.
8. **Jensen gives only a non-strict sign. DISMISSED.**  The nonzero fourth
   chaos (7.2) gives strictness.
9. **A scalar convention can fake a physical energy. UPHELD.**  Equation
   (8.2) is gauge invariant, but physical-empty identification remains open.
10. **The strict fixed-torus sign proves a phase transition. UPHELD AS
    FALSE.**  No thermodynamic or ground limit is present.

This theorem does not prove a beta-independent Hamiltonian, physical beta,
positive-energy vacuum, Hadamard or interacting microlocal spectrum, physical
empty space, absolute vacuum energy, thermodynamic limit, phase transition,
original fixed-raw or three-dimensional Q3 parent, physical light, C0,
N1--N5, C6, CP1, Sector A, or Pre-A.

## 11. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split_verify.py --self-test
```
