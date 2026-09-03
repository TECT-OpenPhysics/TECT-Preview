# EXP-000789 certificate: fixed-lattice ground equal-time order, approximate doublets, full-gap collapse, and continuum counterterm obstruction

Candidate: `PA-CP1-ST8-Q3LOCK-GROUND-EQUAL-TIME-ORDER-GAP-CONTINUUM-COUNTERTERM-ROUTE-SPLIT-v0`  
Result: `PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-GROUND-EQUAL-TIME-LRO-APPROXIMATE-DOUBLETS-FULL-GAP-COLLAPSE-AND-CONTINUUM-BASIS-OBSTRUCTION`  
Tier: T0, claim-nonbearing  
Date: 2026-08-09

<a id="section-1-result-first"></a>
## 1. Result first

This certificate advances two independent parts of the EXP-000782 successor
gate and records their exact boundary.

For the exact fixed-spacing positive-`lambda` ST8/Q3LOCK Hamiltonian, put

\[
 u={1\over\sqrt8}(1,\ldots,1),\qquad Q_y=u\cdot q_y,
 \qquad \theta_Q={-r\over3(g+\lambda)},                 \tag{1.1}
\]

\[
 A_0={8c\chi\theta_Q^2\over\hbar^2},\qquad
 E(p)=\sum_{j=1}^3(1-\cos p_j).                        \tag{1.2}
\]

Define

\[
 J_3={1\over(2\pi)^3}\int_{(-\pi,\pi]^3}{d^3p\over\sqrt{E(p)}}
 =0.643953733381468096\ldots .                         \tag{1.3}
\]

Assume

\[
 \hbar,\chi,c,g,\lambda>0,\qquad r<0,\qquad A_0>J_3^2. \tag{1.4}
\]

On the dyadic periodic cubes used by the reflection-positive construction,
let `Omega_L` be the unique finite-volume ground vector, let
`S_L=sum_y Q_y`, `V=L^3`, and set

\[
 m_L^2={\langle\Omega_L,S_L^2\Omega_L\rangle\over V^2}. \tag{1.5}
\]

Then

\[
 \liminf_{L\to\infty}m_L^2\ge \rho_*,\qquad
 \rho_*:=\theta_Q-{\hbar J_3\over2\sqrt{2\chi c}}
 ={\hbar\over\sqrt{8\chi c}}(\sqrt{A_0}-J_3)>0.       \tag{1.6}
\]

Thus the symmetric finite-volume ground sequence has nonzero equal-time
long-range order in the iterated limit `beta -> infinity` first and then
`L -> infinity`.

The odd variational vector

\[
 \Phi_L={S_L\Omega_L\over\|S_L\Omega_L\|}              \tag{1.7}
\]

gives

\[
 \Delta_L^{\rm full}\le\Delta_L^{\rm odd}
 \le {\hbar^2\over2\chi V m_L^2},\qquad
 \limsup_{L\to\infty}V\Delta_L^{\rm full}
 \le {\hbar^2\over2\chi\rho_*}.                      \tag{1.8}
\]

There is therefore no positive volume-uniform full finite-volume spectral
gap in this regime.  This says nothing against a positive excitation gap in
either symmetry-broken infinite-volume GNS sector.

The vectors

\[
 \Psi_L^\pm={\Omega_L\pm\Phi_L\over\sqrt2}             \tag{1.9}
\]

are translation invariant and satisfy

\[
 \langle\Psi_L^\pm,Q_y\Psi_L^\pm\rangle=\pm m_L,
 \qquad
 \langle\Psi_L^\pm,H_L\Psi_L^\pm\rangle-E_{0,L}
 \le {\hbar^2\over4\chi V m_L^2}.                    \tag{1.10}
\]

They are symmetry-broken approximate ground doublets with vanishing *total*
energy excess.  They are not yet algebraic ground states because a common
infinite-volume dynamics and its ground-state condition have not been
constructed.

Separately, the original continuum ansatz with only the two quartic
couplings `g` and `lambda` is not closed under the standard local four-
dimensional one-loop counterterm test.  For Q3 vertices `e,f` at Hamming
distance two,

\[
 [q_e^2q_f^2]\,\operatorname{tr}\big[(W_4''(q))^2\big]
 =4\lambda^2\ne0,                                     \tag{1.11}
\]

while the original quartic span contains no distance-two monomial.  This is
a counterterm-basis obstruction, not a no-continuum theorem.

<a id="section-2-old-beta-bound"></a>
## 2. Why the old finite-temperature lower bound is not the ground proof

EXP-000782 used

\[
 x_\beta\tanh x_\beta={\beta\hbar^2\over4\chi\theta_Q},
 \qquad
 \delta_\beta=\theta_Q{\tanh x_\beta\over x_\beta}
 -{{\cal I}_3\over2\beta c},                           \tag{2.1}
\]

where

\[
 {\cal I}_3={1\over(2\pi)^3}\int {d^3p\over E(p)}
 =0.505462019717326006\ldots .                         \tag{2.2}
\]

Since `x_beta -> infinity` and `x_beta=beta hbar^2/(4 chi theta_Q)+o(1)`, one
gets the exact asymptotic

\[
 \lim_{\beta\to\infty}\beta\delta_\beta
 ={A_0-{\cal I}_3\over2c}.                             \tag{2.3}
\]

Hence, in the EXP-000782 phase regime `A_0>I_3`, its certified magnetization
lower bound `sqrt(delta_beta)` is only `O(beta^(-1/2))`.  It does not prove
that the two finite-temperature tangent DLR phases remain distinct at zero
temperature.  The proof below repairs equal-time ground order by a different
inequality; it does not silently interchange the old phase-state limits.

<a id="section-3-inverse-falk-bruch"></a>
## 3. Inverse Falk--Bruch at nonzero momentum

Use the Fourier convention

\[
 \widehat Q_p=V^{-1/2}\sum_y e^{-ip\cdot y}Q_y.         \tag{3.1}
\]

For a real sine or cosine Fourier coordinate, and hence for their complex
combination, put

\[
 D_{\beta,L}(p)=(\widehat Q_p,\widehat Q_{-p})_D,
 \quad C_{\beta,L}(p)=\langle\widehat Q_p\widehat Q_{-p}\rangle,
 \quad K_{\beta,L}(p)=\langle[\widehat Q_p,[\beta H_L,
 \widehat Q_{-p}]]\rangle.                             \tag{3.2}
\]

The potential commutes with every configuration coordinate and the kinetic
normalization gives

\[
 K_{\beta,L}(p)={\beta\hbar^2\over\chi}.               \tag{3.3}
\]

The exact Falk--Bruch relation can be written in the inverse form

\[
 C\le {1\over2}\sqrt{DK}\,
 \coth\!\left({1\over2}\sqrt{K/D}\right).             \tag{3.4}
\]

One direct derivation starts from the positive spectral measure.  If `D=b`,
`C=c` and `K=a`, concavity of
`phi(s)=sqrt(s)coth(1/sqrt(s))` gives
`phi(4b/a)>=4c/a`, which is exactly (3.4).  The right side of (3.4) is
increasing in `D` at fixed `K`.

EXP-000782 proved, for every nonzero spatial momentum,

\[
 D_{\beta,L}(p)\le {1\over2\beta cE(p)}.               \tag{3.5}
\]

Substitution into (3.4), with no use of the zero mode, yields

\[
 C_{\beta,L}(p)\le
 {\hbar\over2\sqrt{2\chi cE(p)}}
 \coth\!\left(\beta\hbar\sqrt{{cE(p)\over2\chi}}\right),
 \qquad p\ne0.                                        \tag{3.6}
\]

At fixed finite `L`, every nonzero momentum has `E(p)>0`, so

\[
 C_{0,L}(p)\le {\hbar\over2\sqrt{2\chi cE(p)}}.        \tag{3.7}
\]

Finite-volume compact resolvent makes the Gibbs state converge to the unique
ground vector.  Quartic confinement supplies uniform integrability for the
quadratic observables in (3.2).  Thus the passage from (3.6) to (3.7) does not
replace an unbounded observable by a merely weak bounded-observable limit.

<a id="section-4-ground-order"></a>
## 4. The ground equal-time order lower bound

EXP-000782 also proved, uniformly in finite volume and temperature,

\[
 \langle Q_0^2\rangle_{\beta,L}\ge\theta_Q.            \tag{4.1}
\]

The same finite-volume integrability gives its ground limit.  Fourier
inversion separates the zero mode without estimating it:

\[
 \langle Q_0^2\rangle_{0,L}
 ={1\over V}\sum_p C_{0,L}(p)
 =m_L^2+{1\over V}\sum_{p\ne0}C_{0,L}(p).              \tag{4.2}
\]

Therefore (3.7) and (4.1) give

\[
 m_L^2\ge\theta_Q- {\hbar\over2\sqrt{2\chi c}}J_{3,L},
 \qquad
 J_{3,L}={1\over V}\sum_{p\ne0}{1\over\sqrt{E(p)}}.  \tag{4.3}
\]

The singularity is `|p|^-1`, hence integrable in three dimensions, and along
the declared dyadic cubes `J_(3,L)->J_3`.  With normalized Brillouin measure,
Cauchy--Schwarz gives

\[
 J_3^2\le {\cal I}_3.                                  \tag{4.4}
\]

Equation (1.6) follows.  The intrinsic ground-order condition is the weaker
`A_0>J_3^2`.  The previously certified finite-temperature phase condition
`A_0>I_3` implies it by (4.4), but is not needed for this ground equal-time
theorem.

The order of limits is load-bearing: `beta -> infinity` at each fixed `L`,
then `L -> infinity`.  No thermodynamic-first state limit, arbitrary joint
path, or equality of state-limit orders is asserted.

<a id="section-5-doublets-gap"></a>
## 5. Approximate broken doublets and the full-gap no-go

The finite-volume Hamiltonian is a real confining Schrodinger operator on
`R^(8V)`.  Its Feynman--Kac semigroup is positivity improving, so its ground
vector is unique and strictly positive.  Global parity and translations
therefore fix `Omega_L`; it is even and translation invariant.  Consequently
`Phi_L` in (1.7) is odd, normalized and translation invariant.

The collective coordinate has the exact double commutator

\[
 [S_L,[H_L,S_L]]={V\hbar^2\over\chi}.                  \tag{5.1}
\]

The Rayleigh quotient in the odd subspace is

\[
 {\langle S_L\Omega_L,(H_L-E_{0,L})S_L\Omega_L\rangle
  \over\langle\Omega_L,S_L^2\Omega_L\rangle}
 ={\langle\Omega_L,[S_L,[H_L,S_L]]\Omega_L\rangle
  \over2\langle\Omega_L,S_L^2\Omega_L\rangle},       \tag{5.2}
\]

which proves (1.8).  Since the full first gap minimizes over more vectors than
the odd subspace, `Delta_full<=Delta_odd`.  This is an upper bound; it does not
claim that the tunnelling splitting is exactly `1/V`.

Parity kills the diagonal order expectations of `Omega_L` and `Phi_L`, while

\[
 \langle\Omega_L,S_L\Phi_L\rangle=\|S_L\Omega_L\|.    \tag{5.3}
\]

Translation invariance then gives the magnetizations in (1.10).  The energy
of either superposition is the average of the even and odd trial energies,
which gives the extra factor `1/2` in (1.10).

Uniform local quartic moments follow from translation invariance, the
ground-energy-density bounds of EXP-000780 and quartic coercivity.  Hence
bounded-local state subsequences exist, and the order observable is uniformly
integrable.  The two subsequences are distinct by their opposite local
magnetizations.  They remain **approximate-ground candidates**, not certified
ground states of an infinite system: the repository has not yet built the one
state-independent infinite-volume automorphism group needed to state and test
the algebraic ground condition.

For the same reason, (1.8) is not a mass-gap result.  Symmetry tunnelling makes
the full finite-volume gap close even when each pure broken sector could have
a positive bulk excitation gap.  The latter must be tested as

\[
 \Delta_\omega=\inf\big(\sigma(H_\omega)\setminus\{0\}\big)             \tag{5.4}
\]

after the common dynamics and pure ground sectors exist.

<a id="section-6-kms-boundary"></a>
## 6. Euclidean equilibrium, KMS, and the remaining real-time gate

Nothing above identifies the EXP-000781/782 Euclidean DLR phases as two KMS
states of one pre-existing real-time dynamics.  The available thermodynamic-
dynamics theorems for oscillator lattices use interaction/observable
hypotheses that have not been matched to the exact quartic onsite plus
unbounded bilinear Q3LOCK parent.

The closest next theorem is phasewise periodic OS reconstruction.  For each
fixed `beta` and each DLR phase separately, one can test temporal translation
invariance, **temporal** reflection positivity, strong continuity, the sharp-
time algebra, and generation by its translates.  If these close, they produce
separate stochastically positive systems

\[
 (\mathcal M_{\beta,+},\alpha_t^{\beta,+},\omega_{\beta,+}),\qquad
 (\mathcal M_{\beta,-},\alpha_t^{\beta,-},\omega_{\beta,-}).            \tag{6.1}
\]

That still would not establish two KMS states on one beta-independent common
`alpha_t`.  The common-algebra, thermodynamic-limit dynamics and DLR-to-common-
KMS identification remain separate open subgates.

<a id="section-7-wick-counterterms"></a>
## 7. Exact Wick contraction and the minimum quadratic counterterms

Let Q3 have vertices `{0,1}^3`, twelve undirected Hamming-one edges, adjacency
`A`, and graph Laplacian `L_Q3=3I-A`, so

\[
 q^TL_{Q3}q=\sum_{e\sim f}(q_e-q_f)^2.                 \tag{7.1}
\]

The onsite quartic is

\[
 W_4(q)={g\over4}\sum_eq_e^4
 +{\lambda\over4}\sum_{e\sim f}(q_e-q_f)^2(q_e^2+q_f^2).              \tag{7.2}
\]

For a common diagonal contraction covariance `C I_8`, Wick ordering is

\[
 :W_4:_C=e^{-(C/2)\Delta}W_4
 =W_4-{C\over2}\Delta W_4+{C^2\over8}\Delta^2W_4.     \tag{7.3}
\]

Direct differentiation gives

\[
 \Delta W_4=3(g+\lambda)|q|^2+3\lambda q^TL_{Q3}q,
 \qquad \Delta^2W_4=48(g+4\lambda),                   \tag{7.4}
\]

and hence

\[
 :W_4:_C=W_4-{3C\over2}\big[(g+\lambda)|q|^2
 +\lambda q^TL_{Q3}q\big]+6C^2(g+4\lambda).           \tag{7.5}
\]

Thus even the first contraction needs a scalar counterterm and two independent
quadratic directions, `I` and `L_Q3`.  A reverse raw-to-Wick convention reverses
the displayed counterterm sign but cannot remove either direction.

<a id="section-8-one-loop-basis"></a>
## 8. The four-dimensional one-loop quartic-basis obstruction

For a local multi-scalar quartic potential, the standard four-dimensional
background-field one-loop logarithmic quartic polynomial is a nonzero
universal factor times

\[
 T(q)=\operatorname{tr}\big[(W_4''(q))^2\big]
 =\sum_{a,b}(\partial_a\partial_bW_4)^2.                \tag{8.1}
\]

Take Q3 vertices `e,f` at Hamming distance two.  They have exactly two common
neighbours.  For one edge `i~j`,

\[
 \partial_i^2\left[{\lambda\over4}(q_i-q_j)^2(q_i^2+q_j^2)\right]
 =\lambda(3q_i^2-3q_iq_j+q_j^2).                       \tag{8.2}
\]

At each common neighbour `i`, the diagonal Hessian entry contains
`lambda q_e^2+lambda q_f^2`; its square contributes
`2lambda^2 q_e^2q_f^2`.  Two common neighbours yield

\[
 [q_e^2q_f^2]T=4\lambda^2.                             \tag{8.3}
\]

There is no cancellation because (8.1) is a sum of squares, and the
off-diagonal Hessian entries involve adjacent endpoint pairs.  The bare
two-invariant span in (7.2) contains distance-zero fourth powers and
distance-one edge monomials, but no distance-two `q_e^2q_f^2`.  Therefore it
is not counterterm closed when `lambda>0`.

A minimum enlargement contains

\[
 \sum_{d(e,f)=2}q_e^2q_f^2,                             \tag{8.4}
\]

while the safe target is the complete `Aut(Q3) x Z2`-invariant quartic tensor
basis together with all required quadratic, kinetic and scalar terms.

This is a perturbative algebraic route filter.  It does not refute an enlarged
renormalized trajectory, `lambda(a)->0`, a nonperturbative cancellation, a
different regulator, a constrained/gauge parent, or another UV completion.
For the declared spatial-lattice/time-continuum regulator, the nonzero
logarithmic loop factor and all uniform constructive estimates still have to
be derived.

<a id="section-9-continuum-physical"></a>
## 9. Continuum, physical empty space, and the emergence firewall

EXP-000780--EXP-000782 and EXP-000789 use lattice spacing one.  Sending `a` to zero is not a limit of
the present theorem until an `a`-dependent Hamiltonian, field normalization,
bare-parameter trajectory, enlarged counterterm basis, state family and
uniform estimates are declared.  In four Euclidean dimensions the scalar
`phi^4` and `O(n)` results are severe Gaussian/triviality route filters, but
their hypotheses do not automatically cover the present nonradial Q3 tensor.

Physical empty space is a further, independent comparison.  It requires a
predeclared normalized empty/no-condensate reference under the same
Hamiltonian, regulator, counterterms, volume and boundary convention, and an
additive-scalar-invariant free-energy or energy difference whose sign survives
the controlled `L`, `beta` and `a` limits.  Relative Reading-H candidate
ranking or the named mathematical Gaussian comparators do not supply that
theorem.

Only after a regular Lorentzian continuum state and the C6 causal/signature
gate close may the following identifications be tested:

- a protected massless mode and common characteristic speed as physical light;
- GNS excitations or stable defects as physical mass;
- the common unitary group and Lorentzian causal order as time;
- C4/C5 composition on the same vacuum as gravity;
- global Lorentzian causal geometry as an event horizon.

None of these is derived by this certificate.

<a id="section-10-prior-art"></a>
## 10. Prior-art boundary

The ingredients are established mathematics and field-theory diagnostics:

- Falk--Bruch and the reflection-positive infrared method;
- finite-volume positivity-improving Schrodinger semigroups;
- the general multi-scalar one-loop quartic-tensor renormalization test;
- constructive and scaling-limit work on scalar and `O(n)` four-dimensional
  `phi^4` models.

The repository-specific content is the exact normalization and composition
for the nonradial positive-`lambda` ST8/Q3LOCK Hamiltonian, the half-Watson
threshold, the parity-gap coefficient, and the Q3 distance-two counterterm
witness.  No general-method novelty, world-first statement or historical-
priority claim is made.

Primary sources and route comparators:

- A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase Transitions and Quantum
  Stabilization in Quantum Anharmonic Crystals*, arXiv `0710.2303`, especially
  Proposition 3.18.
- J. E. Bjornberg and D. Ueltschi, *Reflection positivity and infrared bounds
  for quantum spin systems*, arXiv `2204.12896`, Section 4.1.
- B. Nachtergaele, B. Schlein, R. Sims, S. Starr and V. Zagrebnov, *On the
  Existence of the Dynamics for Anharmonic Quantum Oscillator Systems*,
  arXiv `0909.2249`; its exact hypotheses must still be matched.
- M. E. Machacek and M. T. Vaughn, *Two-loop renormalization group equations
  in a general quantum field theory. III. Scalar quartic couplings*, Nuclear
  Physics B 249 (1985), 70--92, DOI `10.1016/0550-3213(85)90040-9`.
- M. Aizenman and H. Duminil-Copin, *Marginal triviality of the scaling limits
  of critical 4D Ising and phi4 models*, Annals of Mathematics 194 (2021),
  163--235, with its 2024 corrigendum.  This is a scalar route filter, not a
  theorem for the Q3 anisotropic tensor.

<a id="section-11-devils-advocate"></a>
## 11. Devil's-advocate audit

1. **Objection: the EXP-000782 order bound vanishes as temperature goes to
   zero.**  
   **UPHELD.**  Section 2 records the exact `1/beta` asymptotic.  The ground
   theorem uses the inverse equal-time conversion, not that bound.

2. **Objection: the zero mode was assumed to prove the zero mode.**  
   **DISMISSED.**  Equation (3.6) is used only for `p!=0`; Fourier inversion
   isolates rather than bounds the zero mode.

3. **Objection: an upper bound on the Duhamel function may point the wrong way
   after Falk--Bruch.**  
   **DISMISSED.**  The exact coth expression is increasing in `D`, and the
   harmonic oscillator saturates every factor.

4. **Objection: weak Gibbs convergence does not control unbounded `Q^2`.**  
   **VALID, mitigated.**  Fixed-volume compact resolvent and quartic
   confinement supply the required uniform integrability before taking the
   ground limit.

5. **Objection: `A_0>I_3` is stronger than needed.**  
   **VALID.**  The theorem is stated at the intrinsic `A_0>J_3^2` threshold;
   normalized Cauchy embeds the older finite-temperature regime.

6. **Objection: broken symmetry means every gap vanishes.**  
   **UPHELD against that overclaim.**  Only the full finite-volume gap is
   forced to close.  A broken-sector GNS gap remains open.

7. **Objection: the vectors `Psi_L^plus/minus` are already infinite-volume
   ground states.**  
   **UPHELD.**  They have vanishing total energy excess and distinct local
   limits, but the common dynamics and algebraic ground condition are absent.

8. **Objection: the one-loop witness depends on a trace factor convention.**  
   **VALID but harmless.**  A global `1/2` changes `4lambda^2` to
   `2lambda^2`; it cannot put the missing monomial into the original span.

9. **Objection: one-loop nonclosure proves no continuum exists.**  
   **UPHELD.**  It refutes only the `g,lambda`-only local perturbative route.
   Enlarged, nonperturbative and alternative-parent routes remain open.

10. **Objection: fixed-lattice order, a KMS system, physical vacuum and
    spacetime emergence are the same theorem.**  
    **UPHELD.**  Sections 6 and 9 keep every reconstruction and composition
    map explicit.

<a id="section-12-reproduction"></a>
## 12. Reproduction

Run from the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_ground_equal_time_order_gap_continuum_counterterm_route_split_verify.py
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/regen_all.py
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/release_check.py
```

The executables recompute the half-Watson and Watson constants, exact
normalizations, harmonic equality, threshold, gap quotient, Wick contractions,
Q3 monomial witnesses, hostile mutations, provenance, scope and repository
synchronization.  They are regression witnesses, not substitutes for the
analytic proof above.
