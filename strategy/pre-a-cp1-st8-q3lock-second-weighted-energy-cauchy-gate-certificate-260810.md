# Second weighted-energy moment and thermodynamic-Cauchy gate split

**Result:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`  
**Task:** T-054  
**Date:** 2026-08-10  
**Tier:** T0, claim-nonbearing
**Scope correction:** `EXP-000795` corrects the cubic-domain wording in
`EXP-000794`; the result proves energy-domain propagation, not the cubic
multiplier embedding.

## 1. Result first

The exact ST8/Q3LOCK common-dynamics programme advances by one load-bearing
analytic step, but the thermodynamic automorphism is not yet constructed.
This continues
`PA-CP1-ST8-Q3LOCK-COMMON-LOCAL-DERIVATION-SOURCE-UNIFORM-WEIGHTED-FIRST-ENERGY-CONE-AND-FOURIER-CUTOFF-ROUTE-SPLIT`.

1. The first weighted-energy cone of `EXP-000792` can be upgraded, without a
   cutoff, to a volume- and compact-source-uniform second weighted-energy
   moment.  The proof uses the exact Schrödinger cross identity rather than
   the invalid implication `A <= B => A^2 <= B^2`.
2. Complex interpolation gives propagation of the energy domain
   `D(A^(3/4))`, equivalently propagation of the `3/2` energy moment.  Scalar
   power counting identifies `3/4` only as a necessary target for a one-sided
   cubic multiplier; the noncommuting bound `q^3A^(-3/4)` and the corresponding
   domain embedding remain open.  An exact Balakrishnan commutator estimate
   separately controls the position multiplier needed at a boundary bond.
3. A two-sided, energy-damped boundary Duhamel theorem reduces
   thermodynamic Cauchy convergence to two explicit spatial commutator
   estimates.  If those estimates hold, exhaustion independence, strong-star
   convergence on the regular core, products, adjoints, the group law and
   strong time continuity follow.
4. The remaining commutator hierarchy does not close at first and second
   position commutators: the cubic force produces a third commutator, or an
   infinite sequence of half-energy graph rungs.  A fixed-chain Gevrey
   estimate converges, but lattice-animal multiplicities, noncommuting energy
   allocation and finite-density topology prevent promotion to a common
   algebra without a new all-rung resummation theorem.

Thus the former higher-moment gate is partially resolved.  The new decisive
gate is
`PA-CP1-ST8-Q3LOCK-ENERGY-WEIGHTED-COMMUTATOR-GEVREY-LR-CLOSURE`.
Common `alpha`, common-alpha KMS identification, algebraic ground states, a
broken-sector GNS gap, continuum removal and physical empty space remain open.

## 2. Model and first-moment input

On a finite subset `Lambda` of the cubic lattice, let `q_x,p_x in R^8` and

\[
 H_\Lambda(h)=\sum_x\left{{|p_x|^2\over2\chi}
 +{r\over2}|q_x|^2+W_4(q_x)-h u\!\cdot q_x\right\}
 +{c\over2}\sum_{\langle xy\rangle}|q_x-q_y|^2,                 \tag{2.1}
\]

where `chi,c,g>0`, `lambda>=0`, and

\[
 W_4(q)={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{e\sim f}(q_e-q_f)^2(q_e^2+q_f^2).      \tag{2.2}
\]

Fix `0<gamma<g/32` and the source-uniform scalar shift from `EXP-000792`.
It gives positive local energies `e_x` satisfying

\[
 \sum_xe_x=K_{\Lambda,h},\qquad
 e_x\ge {|p_x|^2\over2\chi}+\gamma |q_x|^4
 +{c\over4}\sum_{y\sim x}|q_x-q_y|^2.                         \tag{2.3}
\]

Let `0<f_x<=1`, `e^{-mu}<=f_x/f_y<=e^mu` on neighboring sites, and
`S_f=sum_x f_x<=S_(mu,X)<infinity`; the standard centered choice is
`f_x=exp[-mu d(x,X)]` for finite `X`.  Define

\[
 E_f=\sum_x f_xe_x,\qquad A=1+E_f=T_f+U_f+1,                   \tag{2.4}
\]

where `T_f=sum_x f_x|p_x|^2/(2chi)` and `U_f` is multiplication.
With

\[
 v_\mu=6\sqrt{c\over2\chi}(e^\mu-1),                         \tag{2.5}
\]

`EXP-000792` proves, for both signs of time,

\[
 U_\Lambda(t)^*A U_\Lambda(t)\le e^{v_\mu|t|}A.              \tag{2.6}
\]

## 3. Why the first moment cannot simply be squared

Operator squaring is not order preserving.  An exact two-dimensional fixture
makes the logical gap explicit.  Put

\[
 E=\begin{pmatrix}1&0\\0&3\end{pmatrix},\quad
 U={1\over5}\begin{pmatrix}3&-4\\4&3\end{pmatrix},\quad
 A_1=U^*EU,\quad c_0={5\over2}.                               \tag{3.1}
\]

Then

\[
 c_0E-A_1>0,qquad
 \det(c_0E-A_1)={7\over20},                                  \tag{3.2}
\]

but

\[
 \det(c_0^2E^2-A_1^2)=-{127\over16}<0.                       \tag{3.3}
\]

Hence (2.6) alone cannot prove propagation of `A^2`.  The following exact
model identity supplies the missing information.

## 4. Exact second weighted-energy moment

Let `delta(B)=(i/hbar)[H_Lambda(h),B]` on the common Schwartz/form core and put
`B_f=delta(E_f)`.  All eight-component vector products below are Euclidean
row norms/products.  The identities are first proved on that core; (4.7)
then supplies the bounded closures of `B_fA^{-1}` and its adjoint
`A^{-1}B_f`, which are the operators used below.  The local continuity
equation and the fact that
`p_x+p_y` commutes with `q_x-q_y` give

\[
 B_f=-\sum_{\langle xy\rangle}(f_x-f_y){c\over2\chi}
       (p_x+p_y)\!\cdot(q_x-q_y).                              \tag{4.1}
\]

Write `theta=e^mu-1` and let `z=6`.  Weighted Cauchy--Schwarz, the degree
bound and the bond part of `U_f` give, pointwise and then in `L^2`,

\[
 \|B_f\psi\|^2\le {cz\theta^2\over\chi^2}
 \int U_f\sum_x f_x|p_x\psi|^2.                               \tag{4.2}
\]

The remaining cross term is exact:

\[
 D_f:=\int U_f\sum_x f_x|p_x\psi|^2
 =2\chi\,\Re\langle T_f\psi,U_f\psi\rangle
 +{\hbar^2\over2}\int\left(\sum_xf_x\Delta_xU_f\right)|\psi|^2.
                                                                    \tag{4.3}
\]

For one internal Q3 edge with coordinates `a,b`,

\[
 (\partial_a^2+\partial_b^2)
 {\lambda\over4}(a-b)^2(a^2+b^2)
 =\lambda(4a^2-6ab+4b^2)\le7\lambda(a^2+b^2).                 \tag{4.4}
\]

Since Q3 is three-regular,

\[
 \Delta W_4(q)\le C_2|q|^2,\qquad C_2=3g+21\lambda.           \tag{4.5}
\]

For every `epsilon>0`, the onsite and bond Laplacians therefore obey

\[
 \sum_x f_x\Delta_xU_f\le C_2\epsilon U_f
 +S_f\left(8r_++8cz+{C_2\over4\epsilon\gamma}\right).        \tag{4.6}
\]

Using `A>=1`, (4.2)--(4.6) yield

\[
 \|B_fA^{-1}\|=\|A^{-1}B_f\|\le M_\mu,                       \tag{4.7}
\]

where

\[
 M_\mu=\theta\left\{{cz\over\chi}\left[1+{\hbar^2\over2\chi}
 \left(C_2\epsilon+S_f\left(8r_++8cz+{C_2\over4\epsilon\gamma}\right)
 \right)\right]\right\}^{1/2}.                               \tag{4.8}
\]

Since `delta(A^2)=AB_f+B_fA`,

\[
 \|A^{-1}\delta(A^2)A^{-1}\|\le2M_\mu.                      \tag{4.9}
\]

Form Gronwall, applied for positive and negative time, proves

\[
 U_\Lambda(t)^*A^2U_\Lambda(t)\le e^{2M_\mu|t|}A^2,\qquad
 \|A U_\Lambda(t)A^{-1}\|\le e^{M_\mu|t|}.                  \tag{4.10}
\]

All constants are independent of `Lambda`, the sign phase and
`|h|<=h_0`; their only localization dependence is the finite `S_(mu,X)`.

## 5. Three-quarter energy-domain propagation and the position multiplier

Loewner--Heinz applied to (2.6) gives graph transport through exponent `1/2`.
Interpolating that endpoint with (4.10) gives

\[
 \|A^{3/4}U_\Lambda(t)A^{-3/4}\|
 \le\exp\left[\left({v_\mu\over4}+{M_\mu\over2}\right)|t|\right],
                                                                    \tag{5.1}
\]

or equivalently

\[
 U_\Lambda(t)^*A^{3/2}U_\Lambda(t)
 \le e^{(v_\mu/2+M_\mu)|t|}A^{3/2}.                           \tag{5.2}
\]

Scalar power counting gives a necessary threshold: for the commuting model
`A~1+gamma q^4`, a one-sided expression `q^3A^{-s}` can be bounded only if
`s>=3/4`, while a symmetric sandwich needs `s>=3/8`.  This calculation does
not prove the noncommuting operator estimate `q^3A^{-3/4}` for the anharmonic
Schroedinger energy, nor the embedding `D(A^(3/4)) subset D(q^3)`.  Those are
explicit obligations of the remaining commutator gate.  Equations
(5.1)--(5.2) prove energy-domain propagation only.

The position multiplier needed in the boundary formula also closes.  From
`A>=f_x gamma |q_x|^4` and `[A,q_x]=-i hbar f_xp_x/chi`, the Balakrishnan
formula gives

\[
 \|[A^{1/2},q_x]A^{-3/4}\|
 \le\hbar\sqrt{f_x\over2\chi}.                                \tag{5.3}
\]

Consequently

\[
 f_x^{1/4}\|A^{1/2}q_xA^{-3/4}\|
 \le Q_0:=\gamma^{-1/4}+{\hbar\over\sqrt{2\chi}},             \tag{5.4}
\]

with the adjoint orientation as well.  For a neighboring difference one loses
only the declared factor `1+e^(mu/4)`.

## 6. Exact conditional thermodynamic-Cauchy theorem

Let `Lambda subset Lambda'`, split the larger Hamiltonian into the two interior
Hamiltonians plus boundary bonds, and let `A_0` be a bounded local regular-core
observable supported in `X`.  The exact Duhamel identity is

\[
 \tau_t^{\Lambda'}(A_0)-\tau_t^\Lambda(A_0)
 ={i\over\hbar}\int_0^t\tau_{t-s}^{\Lambda'}
 [V_{\partial\Lambda},\tau_s^\Lambda(A_0)]\,ds.               \tag{6.1}
\]

For `R=q_x-q_y`, `C_1^a=[R_a,D]` and `C_2^a=[R_a,C_1^a]`,

\[
 [c|R|^2/2,D]={c\over2}\sum_a(C_2^a+2C_1^aR_a).              \tag{6.2}
\]

Assume, uniformly in finite volume, source and compact time, that for some
`rho>mu/4`

\[
 \|C_1^aA^{-1/2}\|+\|A^{-1/2}C_1^a\|
 \le C e^{-\rho(d(x,X)-v|t|)},                                \tag{6.3}
\]

\[
 \|C_2^aA^{-3/4}\|+\|A^{-3/4}C_2^a\|
 \le C e^{-\rho(d(x,X)-v|t|)}.                                \tag{6.4}
\]

Then (5.1), (5.4), (6.1), (6.2), and the cubic-lattice shell bound imply, for
every `k<rho-mu/4`,

\[
 \|[\tau_t^{\Lambda'}(A_0)-\tau_t^\Lambda(A_0)]A^{-3/4}\|
 +\|A^{-3/4}[\tau_t^{\Lambda'}(A_0)-\tau_t^\Lambda(A_0)]\|
 \le C_{A_0,T,k}e^{-k d(X,\Lambda^c)}.                         \tag{6.5}
\]

Union comparison makes the limit exhaustion independent.  The two one-sided
estimates, unlike symmetric sandwiches alone, give strong-star convergence on
the dense range of `A^{-3/4}`.  Uniform boundedness and core stability pass
products and adjoints; two-time approximation gives the group law and inverse;
compact-time uniformity gives strong continuity.  A C-star conclusion further
requires an invariant Hamiltonian-derived algebra or norm-tight energy tails.

## 7. The remaining infinite commutator ladder

Conditions (6.3)--(6.4) are not consequences of (5.1) alone.  In one component,

\[
 [q^3,D]=3[q,D]q^2+3[q,[q,D]]q+[q,[q,[q,D]]].                 \tag{7.1}
\]

Thus a first/double-commutator system misses the third commutator.  Keeping
left/right order instead introduces `A^(1/2)C_1A^(-1)`; differentiating that
rung creates another half-energy rung, and so on.  The finite hierarchy is not
closed by the cubic onsite force.

A natural first attempt would be the polynomial all-rung estimate

\[
 \sup_{|t|\le T}\|K_0^{j/2}V_e(t)K_0^{-(j+1)/2}\|
 \le C_T(j+1)^\alpha,\qquad j\ge0,\quad\alpha\le1/2,           \tag{7.2}
\]

but it is exactly false.  Let the positive confining one-site Hamiltonian `k`
have compact resolvent, `k phi_m=epsilon_m phi_m`, and real ground state
`phi_0`.  On two sites put

\[
 K=k\otimes1+1\otimes k,\qquad
 V=-c\sum_{a=1}^8q_a\otimes q_a.                              \tag{7.3}
\]

For some `n>0`, the real vector
`m_(n,a)=<phi_n,q_a phi_0>` is nonzero.  Thus
`b_n=c sum_a m_(n,a)^2>0`, and the matrix element between
`phi_0 tensor phi_0` and `phi_n tensor phi_n` gives

\[
 \|K^{j/2}V K^{-(j+1)/2}\|
 \ge {b_n\over\sqrt{2\epsilon_0}}
 \left({\epsilon_n\over\epsilon_0}\right)^{j/2}.             \tag{7.4}
\]

The ratio is strictly larger than one.  Since the onsite interaction-picture
unitary commutes with every power of `K`, the norm in (7.4) is unchanged by
time evolution.  The exact finite-dimensional fixture

\[
 K=\operatorname{diag}(1,4),\qquad
 V=\begin{pmatrix}0&1\\1&0\end{pmatrix}                     \tag{7.5}
\]

has norm exactly `2^j`.  No bound (7.2) can therefore hold for any finite
`alpha` in a nontrivial confining model.  Allowing a simple exponential in
`j` does not repair the sequential ladder: multiplying successive rungs
produces an `exp[O(n^2)]` cost.

One base rung does survive.  If
`K_(xy)>=gamma(|q_x|^4+|q_y|^4)`, then

\[
 \|V_{xy}(t)K_{xy}^{-1/2}\|+
 \|K_{xy}^{-1/2}V_{xy}(t)\|\le {2c\over\sqrt{2\gamma}},       \tag{7.6}
\]

where each orientation separately is at most `c/sqrt(2 gamma)`.  A viable
replacement must estimate the whole Volterra product without commuting a
growing power through every bond, for example by a heat/strip-loss analytic
ideal plus linked-cluster resummation, or by a KMS-specific state-weighted
positivity theorem.  It must still supply a noncollapsing Hamiltonian-derived
finite-density algebra.  The remaining obligations are:

1. unrestricted connected edge histories are lattice animals and can carry
   an additional factorial multiplicity unless branch and repeated-edge
   insertions are resummed into unitary cluster propagators;
2. moving a heat factor through noncommuting `V_e(t)` is not justified by the
   first graph rung, and a centered summable spatial weight can accumulate an
   `exp[O(mu n^2)]` backbone cost;
3. heat-smoothed finite-energy ideals are not norm dense in the unital
   resolvent/Weyl label algebra and do not automatically contain finite-density
   thermal phases.

These are proof obligations, not a no-dynamics theorem.

Registered route boundary:
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-POLYNOMIAL-ALL-RUNG-ONSITE-ENERGY-CONJUGATION`.

### 7.1 Convex subregime does not supply the missing weighted sign

There is a genuine alternative structural fact.  On each Q3 edge the quartic
is convex for `0<=lambda<=2g`, and

\[
 D^2W_4(q)[\xi,\xi]\ge
 3(g-\lambda/2)\sum_aq_a^2\xi_a^2.                           \tag{7.7}
\]

This gives a useful unweighted Hilbert--Schmidt monotonicity sign, but not the
operator/state-weighted sign needed in (6.3)--(6.4).  Indeed, take
`q=diag(0,1,2)`, `D=-1 1^T`, `C=[q,D]`, and `F=[q^3,D]`.  Then

\[
 X={C^*F+F^*C\over2}=
 \begin{pmatrix}17&11&-4\\11&8&5\\-4&5&23\end{pmatrix},     \tag{7.8}
\]

but `v^*Xv=-1` for `v=(-2,2,-1)` even though `tr X=48`.  Hence the faithful
weight `(vv^*+epsilon I)/(9+3epsilon)` has negative expectation whenever
`0<epsilon<1/48`.  Convexity alone cannot localize the Hilbert--Schmidt sign
through a general noncommuting energy or KMS weight, and it does not remove
the third commutator in (7.1).

Registered route boundary:
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONVEXITY-ONLY-WEIGHTED-COMMUTATOR-SIGN`.

## 8. Why symmetric damping is not enough

The order and topology counterexamples are registered as
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIRST-MOMENT-AUTOMATIC-POWER-UPGRADE` and
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-SYMMETRIC-SANDWICH-ONLY-THERMODYNAMIC-CAUCHY`.

Let `W e_n=(n+1)e_n` on `ell^2(N_0)` and
`D_n=|e_n><e_0|`.  For every `s>0`,

\[
 \|W^{-s}D_nW^{-s}\|=\|W^{-s}D_n^*W^{-s}\|=(n+1)^{-s}\to0,   \tag{8.1}
\]

but `D_ne_0=e_n` does not converge strongly.  Therefore symmetric sandwich
Cauchy convergence, even for operators and adjoints, does not imply the
strong convergence required for products, inverses or an automorphism.  This
is why (6.5) is explicitly two-sided and one-sided.

## 9. Prior-art boundary

The exact model is a known hard boundary, not a routine omitted citation.

- Nachtergaele--Raz--Schlein--Sims, arXiv:0712.3820, includes the harmonic
  pair base but requires an onsite derivative with integrable Fourier moment.
- Nachtergaele et al., arXiv:0909.2249, requires bounded Weyl-measure
  perturbations with uniform moments; `EXP-000792` proves the relevant quartic
  cutoff moment diverges.
- Amour--Levy-Bruhl--Nourrigat, arXiv:0904.2717, treats an exact quadratic
  pair base in a useful graph norm but assumes a subquadratic perturbation.
- Kanda--Matsui, arXiv:1601.04809, assumes one-dimensional Schwartz onsite and
  pair potentials.
- Buchholz, arXiv:1605.05259, proves a resolvent-algebra dynamics for bounded
  `C_0` pair interactions; its displayed unbounded onsite example is
  sublinear, not quartic.
- Deuchert--Lampart--Lemm, arXiv:2505.13170, provides a close state-dependent
  common-algebra architecture for number-conserving lattice bosons, but that
  conserved-number mechanism is absent for the Q3LOCK quartic oscillator.

Kondratiev--Kozitsky--Pasurek--Roeckner's exact-form quantum anharmonic-crystal
analysis explicitly uses Euclidean DLR equilibrium because the infinite-volume
real-time dynamics is unavailable.  This is an import gap, not a proof of
nonexistence.  The repository-specific advance is the exact second-moment and
three-quarter energy-domain propagation theorem above.

## 10. Adversarial review and scope

1. **Objection: the first-moment form order can simply be squared.**  
   **UPHELD against that route.**  Equations (3.1)--(3.3) are an exact
   counterexample.  The replacement proof is (4.1)--(4.10).
2. **Objection: a symmetric weighted limit already supplies an automorphism.**  
   **UPHELD.**  Equation (8.1) separates symmetric convergence from strong
   convergence.  The conditional Cauchy theorem requires both one-sided
   orientations.
3. **Objection: the second moment closes the cubic multiplier or the whole
   commutator hierarchy.**  
   **UPHELD.**  Equations (5.1)--(5.2) propagate `D(A^(3/4))`, but do not prove
   `q^3A^(-3/4)` bounded or `D(A^(3/4)) subset D(q^3)`.  Equation (7.1) then
   generates the next commutator rung.  The position multiplier closes, while
   the cubic multiplier and spatial LR remain open.
4. **Objection: the polynomial all-rung bound (7.2) is a viable remaining
   target.**  
   **UPHELD against that route.**  The spectral-transition lower bound (7.4)
   is exponential in `j` and time independent.  The replacement must be a
   product-level/heat-loss or state-weighted theorem, not separate rungs.
5. **Objection: quartic convexity for `lambda<=2g` closes the weighted
   commutator sign.**  
   **UPHELD against that route.**  Equation (7.8) has a faithful negative
   weighted expectation.  The exact convexity fact is retained only within
   its Hilbert--Schmidt scope.
6. **Objection: failure of the current norm routes proves that common dynamics
   does not exist.**  
   **DISMISSED.**  No nonexistence theorem is proved.  Product-level
   cancellations, heat/strip-loss analytic ideals, state-weighted methods and
   other Hamiltonian-derived topologies remain open.

This result is finite-regulator, fixed-spacing and claim-nonbearing.  It does
not prove the one-sided cubic multiplier/domain embedding, construct one
common thermodynamic `alpha`, identify the two phasewise
systems as KMS states of it, promote the time-zero tangents to algebraic ground
states, prove a GNS or physical mass gap, remove the regulator, define physical
empty space, establish a below-empty sign, select a candidate functional, or
prove C6, CP1, Sector A or Pre-A.
