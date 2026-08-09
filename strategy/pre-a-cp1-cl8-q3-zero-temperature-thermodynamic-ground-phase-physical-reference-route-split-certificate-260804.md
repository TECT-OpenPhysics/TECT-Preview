# Pre-A CP1/CL8 Q3 zero-temperature density and reference split

Date: 2026-08-04  
Candidate: `PA-CP1-CL8-Q3-ZERO-TEMPERATURE-THERMODYNAMIC-GROUND-PHASE-AND-PHYSICAL-REFERENCE-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-Q3-SHARP-CUTOFF-GRS-MONOTONE-STRICT-VACUUM-DENSITY-AND-PERIODIC-BRIDGE-REDUCTION`  
Exploration: `EXP-000777` corrects the overbroad `EXP-000776` route verdict
Authority: claim-nonbearing T0 analytic theorem

## 1. Scoped theorem

Fix

\[
 m_0>0,\qquad g>0,\qquad \lambda\geq0,                \tag{1.1}
\]

one real symmetric eight-by-eight matrix `K_pl`, and one scalar density
`e_pl`.  Let

\[
 W_4(q)={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{e\sim f}
 (q_e-q_f)^2(q_e^2+q_f^2),                             \tag{1.2}
\]

and use the same massive plane covariance and plane-Wick convention on every
volume.  Remove the field-independent scalar temporarily and write

\[
 u(x)=:\!\left({1\over2}\Phi(x)^TK_{\rm pl}\Phi(x)
                  +W_4(\Phi(x))\right)\!:\!_{\rm pl}. \tag{1.3}
\]

For the volume-coherent Q3 theory declared in EXP-000775, the following
statements hold.

1. Spatially sharp-cutoff line Hamiltonians exist for the eight-component
   nonradial interaction, and their open-rectangle vacuum amplitudes obey
   exact Nelson coordinate exchange.
2. The Guerra--Rosen--Simon spectral-Holder argument is component-blind and
   gives a bounded nondecreasing centered vacuum-energy density

\[
 \alpha(\ell)=-{E_\ell^\sharp\over\ell}
 \nearrow\alpha_\infty .                               \tag{1.4}
\]

3. The Q3 fourth chaos makes every `E_l^sharp` strictly negative in the
   centered convention.  Consequently

\[
 \boxed{0<\alpha_\infty<\infty.}                       \tag{1.5}
\]

4. The periodic-circle identification is reduced to one explicit uniform
   surface-pairing lemma.  That lemma is not supplied by the existing
   fixed-volume uniform-integrability theorem and remains open.  If it is
   proved, the EXP-000775 notation would obey

\[
 \boxed{\text{uniform surface-pairing lemma}\quad\Longrightarrow\quad
 \lim_{\beta\to\infty}{T_\beta-E_\beta\over\beta}
 =\alpha_\infty>0.}                                    \tag{1.6}
\]

5. The same open lemma would identify this scalar with the rectangular
   van Hove and two iterated periodic specific-KL limits.  Those periodic
   conclusions are reductions, not results of this certificate.

Equations (1.4)--(1.5) are a strict infinite-line sharp-cutoff result below
one named Gaussian reference in the scalar-invariant centered-variational
sense.  Equation (1.6) is conditional.  Neither statement identifies the
reference with physical empty space or fixes absolute gravitational vacuum
energy.

## 2. Why the multicomponent obstruction does not invalidate Q3

Ordinary pointwise stability is insufficient for a multivariate Wick Gibbs
law.  Nagoji's example

\[
 P(x_1,x_2)=x_1^2x_2^2\geq0                            \tag{2.1}
\]

can have a nonnormalizable Wick exponential in the `P(Phi)_2` regime.  Its
quartic vanishes on both coordinate axes.  It therefore cannot dominate the
full lower-monomial envelope created by Wick translation.

Q3 has the additional onsite term with `g>0`.  Cauchy gives

\[
 \sum_{e=1}^8q_e^4\geq {|q|^4\over8},\qquad
 W_4(q)\geq {g\over32}|q|^4.                           \tag{2.2}
\]

For arbitrary `K_pl`,

\[
 {1\over2}q^TK_{\rm pl}q+W_4(q)
 \geq {g\over32}|q|^4-{\|K_{\rm pl}\|\over2}|q|^2
 \geq-{2\|K_{\rm pl}\|^2\over g}.                   \tag{2.3}
\]

More importantly, (2.2) is radial coercivity of degree four, not merely the
last lower bound in (2.3).  Every strict lower multi-index has degree at most
three and is absorbed with exponent below four.  This is exactly the
multivariate normalizability interface verified in EXP-000769 and independently
closed by the cutoff-uniform Nelson--Boue--Dupuis estimate in EXP-000772.
The case `g=0` remains outside the theorem.

## 3. Sharp-cutoff line Hamiltonians

Let

\[
 {\cal h}=L^2(\mathbb R;\mathbb C^8),\qquad
 \omega=(-\partial_x^2+m_0^2)^{1/2}\otimes I_8,
 \qquad H_0=d\Gamma(\omega),                            \tag{3.1}
\]

and let `Omega0` be the free Fock vacuum.  For
`I_l=(-l/2,l/2)`, define the spatially cutoff form

\[
 q_\ell^\sharp=q_{H_0}
 +\int_{I_\ell}u(x)\,dx,qquad
 H_\ell^\sharp\leftrightarrow q_\ell^\sharp .        \tag{3.2}
\]

This is a new geometry relative to EXP-000774.  A compact-circle Hamiltonian
cannot simply be renamed as (3.2).

At a common spatial-mode and local mollifier cutoff, (3.2) is an ordinary
finite-chaos form.  The proof of its cutoff removal has the following exact
inputs.

- There are only eight component labels and finitely many monomials of degree
  at most four.
- Product hypercontractivity bounds every component-labelled Wick kernel by
  the corresponding scalar kernel times a finite constant.
- Wick translation produces random terms of degree at most three.  Equation
  (2.2), the one-dimensional form norm, and generalized Young inequalities
  absorb them into a fixed fraction of the quartic coercivity and free form.
- The EXP-000772 all-positive exponential estimate, restricted to a compact
  rectangle and then passed to an increasing time window, supplies the direct
  limiting Feynman--Kac--Nelson domination.

The cutoff forms therefore converge to a closed lower-bounded form.  The
standard massive spatial-cutoff compactness argument gives a normalized
ground `Omega_l`, and positivity improvement in Gaussian Q-space makes it
strictly positive.  Since `Omega0=1` is strictly positive in the same
representation,

\[
 \langle\Omega_0,\Omega_\ell\rangle>0.                 \tag{3.3}
\]

The next bounds are separate constructive inputs, not consequences of the
spectral-Holder argument below.  The support-uniform Glimm--Jaffe/Simon
localizability estimate applies after the finite Q3 component sum is bounded
by the radial coercivity (2.2); the eight labels change constants but not the
unit-block argument.  It gives, with constants independent of `l`,

\[
 H_\ell^\sharp\geq-C_1\ell-C_0.                       \tag{3.4}
\]

The ground-overlap estimate is another explicit finite-component Nelson
input.  Fix a positive time in the hypercontractive window.  Feynman--Kac,
product hypercontractivity and the same unit-block exponential estimate give

\[
 \|e^{-\tau H_\ell^\sharp}\|_{L^1(Q)\to L^2(Q)}
 \leq e^{C_2\ell+C_3}.                                \tag{3.5}
\]

Since `Omega_l` is positive, normalized in `L2`, and
`e^{-tau H_l^sharp}Omega_l=e^{-tau E_l^sharp}Omega_l`, while the centered
vacuum trial gives `E_l^sharp<=0`, (3.5) yields

\[
 \langle\Omega_0,\Omega_\ell\rangle
 =\|\Omega_\ell\|_{L^1(Q)}
 \geq e^{-C_2\ell-C_3}.                                \tag{3.6}
\]

The constants change with the finite internal index set and polynomial
coefficients but not with `l`.  No scalar field order, radial internal
symmetry or phase uniqueness is used.

## 4. Open-rectangle Feynman--Kac and Nelson symmetry

Put

\[
 Z^\sharp(t,\ell)
 =\langle\Omega_0,e^{-tH_\ell^\sharp}\Omega_0\rangle.
                                                                    \tag{4.1}
\]

Direct limiting Feynman--Kac--Nelson gives

\[
 Z^\sharp(t,\ell)=
 \mathbb E_{\mu_{\rm pl}}
 \exp\left[-\int_{-t/2}^{t/2}\int_{-\ell/2}^{\ell/2}
 u(s,x)\,dx\,ds\right].                               \tag{4.2}
\]

Every component has covariance

\[
 C_{\rm pl}(z)={1\over2\pi}K_0(m_0|z|),               \tag{4.3}
\]

and the internal covariance is `C_pl I8`.  The local Q3 polynomial has no
spacetime derivative or preferred Euclidean coordinate.  Rotating the common
cutoff rectangle and then removing the cutoff therefore proves the exact
identity

\[
 \boxed{Z^\sharp(t,\ell)=Z^\sharp(\ell,t).}            \tag{4.4}
\]

Internal nonradiality is irrelevant to (4.4): it concerns the eight component
indices, not the two Euclidean coordinates.  The common plane-Wick convention
is load-bearing; independently Wick-ordering the two rectangles would have
introduced a spurious scalar.

## 5. The component-blind GRS monotonicity proof

For `0<a<1`, a probability measure `rho` on the positive half-line obeys

\[
 \int x^a\,d\rho(x)\leq
 \left(\int x\,d\rho(x)\right)^a.                      \tag{5.1}
\]

This is Holder's inequality.  By the spectral theorem, for every positive
self-adjoint `A` and unit vector `psi`,

\[
 \langle\psi,A^a\psi\rangle
 \leq\langle\psi,A\psi\rangle^a.                     \tag{5.2}
\]

Take `A=exp(-l H_t^sharp)` and `psi=Omega0`.  First (5.2), then (4.4), gives

\[
 Z^\sharp(t,a\ell)
 =Z^\sharp(a\ell,t)
 \leq Z^\sharp(\ell,t)^a
 =Z^\sharp(t,\ell)^a.                                 \tag{5.3}
\]

Let `E_l^sharp=inf spec H_l^sharp`.  Equation (3.3) and the spectral theorem
give

\[
 e^{-tE_\ell^\sharp}
 \geq Z^\sharp(t,\ell)
 \geq e^{-tE_\ell^\sharp}
       |\langle\Omega_0,\Omega_\ell\rangle|^2.        \tag{5.4}
\]

Consequently

\[
 \lim_{t\to\infty}{1\over t}\log Z^\sharp(t,\ell)
 =-E_\ell^\sharp.                                     \tag{5.5}
\]

Take logarithms in (5.3), divide by `t`, and use (5.5):

\[
 -E_{a\ell}^\sharp\leq-aE_\ell^\sharp,
 \qquad
 \alpha(a\ell)\leq\alpha(\ell),
 \qquad
 \alpha(\ell):=-{E_\ell^\sharp\over\ell}.          \tag{5.6}
\]

Thus `alpha` is nondecreasing.  The linear lower bound in (3.4) makes it
bounded above, so
`alpha_infinity` in (1.4) exists and is finite.  Equations (5.1)--(5.6) are
the complete monotonicity core of the 1972 GRS theorem.  They contain no
scalar correlation inequality and no internal-component ordering.

For simultaneous `t,l->infinity`, (3.6) and (5.4) also give

\[
 -{E_\ell^\sharp\over\ell}-{2C_2\over t}
 -{2C_3\over t\ell}
 \leq {1\over t\ell}\log Z^\sharp(t,\ell)
 \leq-{E_\ell^\sharp\over\ell}.                      \tag{5.7}
\]

Hence every open-rectangle van Hove sequence has the same centered pressure
`alpha_infinity`, independently of aspect ratio.

## 6. Strictness from a local Q3 fourth-chaos vector

Plane-Wick centering gives

\[
 q_\ell^\sharp[\Omega_0]=0.                            \tag{6.1}
\]

For any component `e`, the coefficient of its pure quartic is

\[
 c_4={g+3\lambda\over4}>0.                             \tag{6.2}
\]

Let `Pi_(4,e)` project onto four particles of that component.  Wick's theorem
and the equal-time covariance `C_m(r)=K_0(m_0|r|)/(2 pi)` give

\[
 \|\Pi_{4,e}H_\ell^\sharp\Omega_0\|^2
 =c_4^2 4!\int_{I_\ell}\int_{I_\ell}
 C_m(x-y)^4\,dx\,dy>0.                                 \tag{6.3}
\]

The integral is finite because the logarithmic coincidence singularity is
locally integrable and the massive tail is exponential.  The quadratic part
has no vacuum-to-four-particle component and cannot cancel (6.3).  Therefore
`Omega0` is not an eigenvector of `H_l^sharp`.

If `E_l^sharp` were zero, (6.1) would attain the bottom of the spectrum and
the spectral measure of `Omega0` would be supported at zero, making it a
ground eigenvector.  This contradicts (6.3).  Hence

\[
 E_\ell^\sharp<0,
 \qquad \alpha(\ell)>0.                                \tag{6.4}
\]

Monotonicity then yields, for any fixed `l0>0`,

\[
 \alpha_\infty\geq\alpha(\ell_0)>0.                   \tag{6.5}
\]

This is the extensive strictness step.  The compact-circle zero-mode
amplitude in EXP-000775 is proportional to `beta^(-1)` and by itself does not
give (6.5).

## 7. Periodic-sharp surface-pairing reduction and open gate

The comparison starts from an exact finite-cutoff Gaussian covariance
interpolation, but its thermodynamic and ultraviolet limits require a new
uniform estimate.

The preceding theorem is for an interaction sharply supported on the line.
EXP-000775 uses a periodic spatial circle.  Equating these geometries without
a boundary theorem would be invalid.  This section records the exact missing
lemma and proves only the finite-cutoff reduction to it.

### 7.1 What is exact at common finite cutoff

Use one physical mollifier and finite Gaussian coordinate space.  On a
rectangle `Lambda`, let `C_0` be the restricted massive plane covariance and
`C_1` the periodic covariance.  Put

\[
 C_r=(1-r)C_0+rC_1,\qquad0\leq r\leq1.                 \tag{7.1}
\]

Let `Z_(r,N)` use the same plane-Wick action at common ultraviolet cutoff
`N`.  Finite-dimensional Gaussian differentiation is exact:

\[
 {d\over dr}\log Z_{r,N}={1\over2}\sum_{i,j}\dot C_{N,ij}
 \mathbb E_{\nu_{r,N}}
 \left[\partial_i I_N\,\partial_j I_N
       -\partial_i\partial_jI_N\right].                \tag{7.2}
\]

The Q3 derivatives in (7.2) are Wick polynomials of degrees at most three
and two.  The desired surface theorem would follow from the uniform estimate

\[
 \begin{split}
 \Big|&\iint D_N(x,y)
 \langle :P'_a(\Phi_N(x))::P'_b(\Phi_N(y)):\rangle_{\nu_{r,N}}
 \,dx\,dy\\
 &-\int D_N(x,x)
 \langle:P''_{ab}(\Phi_N(x)):\rangle_{\nu_{r,N}}dx\Big|
 \leq C(|\partial\Lambda|+1),                         \tag{7.3}
 \end{split}
\]

where `D_N=C_(1,N)-C_(0,N)`, with one constant uniform in `N`, `r` and the
rectangle dimensions.  Integrating (7.2) under (7.3) would give

\[
 |\log Z_\Lambda^{\rm per}-\log Z_\Lambda^\sharp|
 \leq C(|\partial\Lambda|+1).                         \tag{7.4}
\]

### 7.2 Why EXP-000772 does not close (7.3)

EXP-000772 proves all-positive exponential integrability at one fixed
`beta0,L` for its periodic covariance.  It does not provide a constant
simultaneously uniform in growing rectangle size, the interpolation `r`, and
the nonlocal mixed covariance `C_r`.  It also does not directly control the
normalized interacting quadratic and cubic insertions in (7.3).  Dividing a
global numerator bound by `Z_(r,N)` can reintroduce exponential volume
dependence.

Moreover, the restriction of the plane covariance is not the inverse of an
ordinary finite-volume Laplacian.  A statement that every resolvent path
crosses a seam is therefore not a proof.  A successful route must supply all
of the following:

1. a common-regulator image or Schur-complement bound for `D_N`, including
   the logarithmic seam singularity;
2. volume- and `r`-uniform local Gibbs/Wick moment or correlation estimates;
3. a uniform Cameron--Martin or negative-Sobolev comparison for `C_r`; and
4. uniform integrability for the derivative insertions in (7.3).

These four inputs are the named gate
`PA-CP1-CL8-Q3-CUTOFF-VOLUME-INTERPOLATION-UNIFORM-PERIODIC-SHARP-SURFACE-PAIRING`.

### 7.3 Conditional consequence, not a theorem here

If (7.3) is proved, (7.4) implies after the long-time ground projection

\[
 |E_s^{\rm per,u}-E_s^\sharp|=O(1),\qquad
 {E_s^{\rm per,u}-E_s^\sharp\over s}\to0.             \tag{7.5}
\]

Here `E_s^(per,u)` is the transfer ground energy of the scalar-removed plane
action (1.3), not yet the EXP-000775 whole-Wick centered energy.  The exact
Wick scalar ledger is

\[
 E_0(\widehat H_s)=E_s^{\rm per,u}-s c_s,\qquad
 c_s={a_s\over2}\operatorname{Tr}K_{\rm pl}
       +6a_s^2(g+4\lambda)=o(1).                      \tag{7.6}
\]

Thus (7.5), if proved, would also identify the centered periodic energy
density with the sharp one.  Together with (5.7), it would identify the
periodic and sharp rectangular pressure densities.  Equations (7.4)--(7.6)
are retained only as the exact target implication.  They are not registered
results of this certificate.

## 8. Conditional periodic zero-temperature composition and scalar ledger

EXP-000775 defined

\[
 T_\beta=\beta e_{*,\beta},\qquad
 \widehat H_\beta=H_\beta^\perp-T_\beta I,            \tag{8.1}
\]

and proved, at each fixed finite beta,

\[
 s_{\rm rel}(\beta)
 ={T_\beta-E_\beta\over\beta}
 =-{E_0(\widehat H_\beta)\over\beta}>0.              \tag{8.2}
\]

The coherent circle scalar is

\[
 {T_\beta\over\beta}=e_{*,\beta}
 =e_{\rm pl}+{a_\beta\over2}\operatorname{Tr}K_{\rm pl}
 +6a_\beta^2(g+4\lambda),                             \tag{8.3}
\]

where

\[
 a_\beta={1\over\pi}\sum_{n\geq1}K_0(m_0n\beta)
 =O(e^{-m_0\beta}/\sqrt\beta).                        \tag{8.4}
\]

If the open surface-pairing gate supplies (7.5), composition with
(1.4) gives

\[
 \lim_{\beta\to\infty}{E_0(\widehat H_\beta)\over\beta}
 =-\alpha_\infty.                                     \tag{8.5}
\]

Combining (8.2) and (8.5) would prove (1.6).  Restoring the scalar convention
would then give

\[
 \lim_{\beta\to\infty}{E_\beta\over\beta}
 =e_{\rm pl}-\alpha_\infty.                           \tag{8.6}
\]

Equations (8.5)--(8.6) are conditional targets, not registered conclusions.
The closed scalar statement is (8.3)--(8.4): `T_beta/beta` tends to `e_pl`.
All further conditional limit statements in this section concern scalar
densities only.
Adding a local scalar density `c` shifts both finite-beta trial and ground
terms by `c`; every centered difference is invariant, while every raw sign
is conventional.

Let

\[
 d(\beta,L)={D(\mu_{\beta,L}\Vert\nu_{\beta,L})
 \over\beta L}.                                        \tag{8.7}
\]

The exact plane-Wick rectangle is symmetric under `beta<->L`, and EXP-000775
gives `lim_(L->infinity)d(beta,L)=s_rel(beta)` at fixed beta.  If the uniform
surface-pairing gate proves (7.4), then (5.7) gives the joint rectangular van
Hove limit and hence

\[
 \lim_{\beta\to\infty}\lim_{L\to\infty}d(\beta,L)
 =\lim_{L\to\infty}\lim_{\beta\to\infty}d(\beta,L)
 =\lim_{\substack{\beta,L\to\infty\\\rm van\ Hove}}
 d(\beta,L)=\alpha_\infty>0.                          \tag{8.8}
\]

Equation (8.8) is therefore a conditional composition target.  It is not
proved here.  Even after its scalar proof, it would license no exchange of
limits for measures, states, vectors, gaps or correlators.

## 9. Independent reflection and curvature audits

The sharp-cutoff strict sign has two checks that do not replace the GRS proof
or close the periodic boundary gate.

First, for any fixed reflection block `B`, let `I_B=int_B u`.  Wick-chaos
orthogonality and (6.2) imply

\[
 \operatorname{Var}_{\mu_{\rm pl}}(I_B)
 \geq8\,4!\,c_4^2\int_B\int_B C_{\rm pl}(x-y)^4dxdy>0. \tag{9.1}
\]

Strict Jensen gives `z_B=E exp(-I_B)>1`.  A possible periodic successor uses
reflection positivity and repeated Cauchy--Schwarz to disseminate the block
over compatible dyadic tori:

\[
 \left(\mathbb E_{\mu_R^{\rm per}}e^{-I_B}\right)^{N_R}
 \leq Z_R^{\rm per}.                                  \tag{9.2}
\]

For this to be a theorem one must still verify, in the exact plane-Wick
volume-coherent family, both the reflected-factor identification in (9.2)
and fixed-block uniform integrability as the surrounding torus grows.  The
current executable rows check only the finite algebraic fixture.  Conditional
on those two analytic inputs, local covariance convergence would pass the
block expectation to `z_B` and give a positive pressure liminf along the
compatible dyadic tori.  No such periodic liminf is registered here.  This
route is only an independent strictness diagnostic and does not prove the
full periodic limit or the iterated limit (8.8).

Second, the free pressure curvature at zero coupling is

\[
 \sigma^2=\int_{\mathbb R^2}
 \operatorname{Cov}_{0}(u(x),u(0))\,dx.                \tag{9.3}
\]

Different Wiener chaoses and component tensors are orthogonal.  The eight
pure fourth-chaos channels alone give

\[
 \sigma^2\geq8\,4!\,c_4^2
 \int_{\mathbb R^2}C_{\rm pl}(x)^4\,dx.                \tag{9.4}
\]

Since

\[
 \int_0^\infty rK_0(r)^4dr={7\zeta(3)\over8},         \tag{9.5}
\]

we have

\[
 \int_{\mathbb R^2}C_{\rm pl}(x)^4dx
 ={7\zeta(3)\over64\pi^3m_0^2},                     \tag{9.6}
\]

and hence

\[
 \boxed{
 \sigma^2\geq {21\zeta(3)\over16\pi^3m_0^2}
 (g+3\lambda)^2>0.}                                   \tag{9.7}
\]

Positive curvature at one coupling point does not alone prove pressure at
unit coupling without a uniform remainder theorem.  It is retained as an
independent normalization, component-count and sign audit.

## 10. Phase and physical-reference firewall

The infinite-line sharp-cutoff centered density now exists and is strictly
separated from the named Gaussian reference.  Its periodic zero-temperature
identification remains behind (7.3).  Three still stronger interpretations
remain false or open.

1. **Physical empty space.**  The Gaussian law is fixed by inserted `m0`,
   Euclidean geometry and field normalization.  No theorem derives it as the
   cosmic no-condensate state.  The conditional raw target (8.6) changes
   under an additive scalar; the proved sharp centered density is invariant.
2. **Phase selection.**  A pressure can be unique while several Gibbs or
   vacuum phases coexist.  For arbitrary `K_pl`, the Q3 potential can contain
   double-well directions.  No order parameter, plus/minus boundary-state
   distinction or spontaneous-symmetry-breaking threshold is proved here.
3. **Cosmological cooling.**  `beta` is Euclidean inverse temperature in this
   inserted comparator.  No map from a Pre-A high-energy history to beta, and
   no dynamical cooling or quench theorem, has been constructed.

The following remain open: the uniform periodic-sharp surface pairing and
therefore the periodic zero-temperature scalar limit; a full infinite-volume
local KMS algebra; zero-temperature state/vector/gap/correlation convergence;
interacting microlocal spectrum; the original fixed-raw CL8 regulator; the
one-dimensional-to-three-dimensional Q3LOCK parent, C0, N1--N5, C6, CP1,
Sector A and Pre-A.

## 11. Prior-art boundary

Guerra, Rosen and Simon proved (5.1)--(5.6) and the scalar `P(phi)_2` vacuum
energy result in *Communications in Mathematical Physics* 27 (1972), 10--22,
DOI `10.1007/BF01649655`.  Their 1973 paper, DOI
`10.1007/BF01645249`, treats the infinite-volume vacuum energy and coupling
dependence.  Their 1976 boundary-condition work treats scalar `P(phi)_2`
boundary independence.

The support-uniform linear Hamiltonian lower bound used in (3.4) is a
separate constructive theorem; see Simon, *Journal of Functional Analysis*
10 (1972), 251--258, DOI `10.1016/0022-1236(72)90052-3`.  The scalar GRS
paper also proves exponential `L1(Q)` control of the cutoff ground.  Section 3
states the finite-component product-hypercontractive adaptation explicitly;
neither input is silently attributed to the spectral-Holder inequality.

Those sources state a one-real-scalar theorem.  They do not state an arbitrary
eight-component nonradial Q3 theorem.  The spectral-Holder step is exactly
component-blind, while Sections 2--4 discharge the sharp-cutoff interaction
inputs.  Section 7 isolates rather than closes the periodic boundary
geometry.  Nagoji's
`arXiv:2305.19583` is the reason the radial-coercivity check may not be
replaced by the phrase "bounded below."

Scalar phase transitions and multiple phases in `P(phi)_2` are established
prior art.  Their existence in other models is precisely why a pressure
limit cannot be promoted to phase uniqueness.  No located source proves the
complete TECT Pre-A chain, and this package makes no world-first claim.

## 12. Adversarial review

1. **The multicomponent polynomial is bounded below, so normalizability is
   automatic. UPHELD AS FALSE.**  Nagoji's mixed-axis example is a direct
   counterexample.  Q3 uses the stronger radial estimate (2.2) and the
   EXP-000772 uniform theorem.
2. **The GRS theorem can be cited verbatim for Q3. UPHELD AS FALSE.**  The
   source is scalar.  Sections 3 and 4 supply the finite-index Hamiltonian
   and open-rectangle interfaces; Section 7 keeps the periodic bridge open.
3. **Periodic traces obey the GRS spectral probability inequality.
   UPHELD AS FALSE.**  The proof uses the open-rectangle vacuum amplitude
   (4.1), not the EXP-000775 trace ratio.
4. **Internal Q3 nonradiality breaks Nelson symmetry. DISMISSED.**  It acts on
   component indices; the common plane action remains isotropic in the two
   Euclidean coordinates.
5. **The finite-circle zero mode proves a uniform density gap. UPHELD AS
   FALSE.**  Its amplitude is `O(beta^-1)`.  The sharp-cutoff monotonicity and
   local fourth-chaos witness supply extensivity.
6. **Strict finite-volume Jensen is automatically extensive. UPHELD AS
   FALSE.**  Reflection dissemination or GRS monotonicity is required.
7. **A Nelson normalization bound proves boundary independence. UPHELD AS
   FALSE.**  The uniform normalized derivative-insertion estimate (7.3) is
   still missing; fixed-volume EXP-000772 integrability does not imply it.
8. **The finite-cutoff interpolation already proves the continuum surface
   estimate. UPHELD AS FALSE.**  Gaussian differentiation (7.2) is exact,
   but cutoff-, volume- and `r`-uniform passage for its Wick insertions is the
   load-bearing open gate.
9. **Boundary independence proves phase uniqueness. UPHELD AS FALSE.**  Even
   if (7.3) is closed, it identifies one scalar pressure density only.
10. **The beta-L scalar iterated limits are already proved. UPHELD AS
    FALSE.**  Equation (8.8) is conditional on (7.3), and even its eventual
    scalar proof would exclude states, vectors, gaps and correlators.
11. **The centered density is absolute vacuum energy. UPHELD AS FALSE.**  A
    scalar shift changes every raw energy while leaving centered differences
    invariant.
12. **The Gaussian reference is physical empty space. UPHELD AS UNPROVED.**
    Its mass, geometry and field units are inserted.
13. **A beta limit is a cosmological phase transition. UPHELD AS FALSE.**
    No cooling map or order-parameter nonanalyticity is present.
14. **This closes Pre-A. UPHELD AS FALSE.**  The periodic surface bridge,
    phase/reference, state, microlocal, three-dimensional parent and
    C0/N1--N5 gates remain open.

## 13. Reproduction

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_zero_temperature_thermodynamic_ground_phase_physical_reference_route_split_verify.py --self-test
```

The scripts verify the exact Q3 factors, the spectral-Holder implication,
strict fourth-chaos witness, the formal surface-to-density scaling, the
conditional scalar ledger, Bessel curvature coefficient, mutations, record
integrity and scope firewalls.  They do not replace the analytic construction
in Sections 3--4 and do not certify the open uniform estimate (7.3).
