# Pre-A ST8/Q3LOCK Euclidean-DLR and tangent-state route split

Date: 2026-08-04  
Candidate: `PA-CP1-ST8-Q3LOCK-EUCLIDEAN-DLR-TANGENT-STATE-AND-PHASE-BOUNDARY-ROUTE-SPLIT-v0`  
Result: `PA-CP1-ST8-Q3LOCK-TEMPERED-EUCLIDEAN-DLR-TANGENT-STATES-AND-LAMBDA0-PHASE-BOUNDARY`  
Exploration: `EXP-000781`
Authority: claim-nonbearing T0 exact external-theorem instantiation plus
self-contained tangent-selection and local-normality corollaries

<a id="section-1-result-first"></a>
## 1. Result first

Fix the exact unweighted, fixed-spacing, fixed-block-origin ST8/Q3LOCK
Hamiltonian from EXP-000780, with

\[
 \hbar,\chi,c,g,\lambda>0,\qquad r\in\mathbb R,          \tag{1.1}
\]

and fix `beta>0`.  Group the eight fine oscillators in each Q3 block into one
coarse vector `q_y in R8`.  The model then lies exactly in the general
finite-component quantum-anharmonic-crystal class treated by
Kozitsky and Pasurek.  Consequently, for every constant source, the set of
tempered Euclidean DLR measures is nonempty and compact, all its elements obey
the cited uniform exponential one-site estimates, and every accumulation
point of periodic finite-volume loop laws is a translation-invariant tempered
DLR measure.

This imported result combines with the locally uniform convex source pressure
proved in EXP-000780.  For every direction `v in R8`, let

\[
 P_{\beta,L}(h)={1\over \beta,8L^3}
 \log\operatorname{Tr}e^{-\beta H_L(hv)},                \tag{1.2}
\]

where the energy-source convention is

\[
 H_L(hv)=H_L(0)-h\sum_y v\mathbin\cdot q_y.              \tag{1.3}
\]

The limiting pressure `P_beta(h)` is finite, convex, and even.  Its endpoint
slopes satisfy

\[
 m_+(v):=D_+P_\beta(0)\ge0,
 \qquad D_-P_\beta(0)=-m_+(v).                           \tag{1.4}
\]

There are zero-source tempered Euclidean DLR measures `mu_plus` and
`mu_minus` such that

\[
 {1\over8}\int v\mathbin\cdot\omega_0(0)\,d\mu_+
 =m_+(v),
 \qquad
 {1\over8}\int v\mathbin\cdot\omega_0(0)\,d\mu_-
 =-m_+(v).                                               \tag{1.5}
\]

The second measure is the global-field-inversion image of the first.  Thus a
strictly positive endpoint slope would prove a directional pressure cusp and
two distinct zero-source Euclidean equilibrium states.  This package does not
prove that strict sign.  If `m_+(v)=0`, neither uniqueness nor absence of a
phase transition follows.

Along the same finite-volume sequences, compact local energy balls give
compatible locally normal time-zero states.  Their bounded configuration
observables agree with the time-zero marginals of `mu_plus` and `mu_minus`,
and their `q` expectations satisfy (1.5).  This does not construct an
infinite-volume real-time dynamics and does not promote these states to KMS
states on a pre-existing full quasi-local oscillator algebra.

There is also a rigorous phase-transition anchor on the boundary
`lambda=0`.  In that limit the eight species decouple into scalar quantum
`phi4` crystals.  If

\[
 r+6c<0,
 \qquad
 \vartheta_*=-{r+6c\over3g},
 \qquad
 8{\chi\over\hbar^2}c\,\vartheta_*^2>{\cal J}(3),       \tag{1.6}
\]

the established scalar theorem supplies a finite `beta_star` and more than
one tempered Euclidean Gibbs measure for every `beta>beta_star`.  This is a
boundary comparator, not a theorem for the registered `lambda>0` Q3LOCK
model.

Accordingly, the exact positive-`lambda` equilibrium-state and
pressure-tangent existence gate is closed, while the strict Q3 phase sign,
extremality, purity, clustering, algebraic KMS identification, ground-state
phase, continuum, physical reference, and the rest of Pre-A remain open.

<a id="section-2-exact-coarse-cell-map"></a>
## 2. Exact coarse-cell Hamiltonian map

Write `q_y=(q_{y,e})` with `e in {0,1}^3`.  Expanding every spatial
difference square on the infinite coarse lattice gives

\[
 {c\over2}\sum_{\langle yz\rangle}|q_y-q_z|^2
 =3c\sum_y|q_y|^2-c\sum_{\langle yz\rangle}q_y\cdot q_z. \tag{2.1}
\]

The formal translation-invariant Hamiltonian is therefore

\[
 H=\sum_y\left[-{\hbar^2\over2\chi}\Delta_y+U_h(q_y)\right]
 -c\sum_{\langle yz\rangle}q_y\cdot q_z,                \tag{2.2}
\]

where

\[
\begin{aligned}
 U_h(q)={}&{r+6c\over2}|q|^2+{g\over4}\sum_e q_e^4-hv\cdot q\\
 &+{\lambda\over4}\sum_{\{e,f\}\in E(Q_3)}
 (q_e-q_f)^2(q_e^2+q_f^2).                             \tag{2.3}
\end{aligned}
\]

Equation (2.1) fixes the factor `6c`: `3c|q|^2` equals
`(6c/2)|q|^2`.  It also fixes the intersite intensity.  In the convention

\[
 -{1\over2}\sum_{y,z}J_{yz}q_y\cdot q_z,               \tag{2.4}
\]

take `J_yz=c` for nearest neighbours and zero otherwise.  The ordered sum in
(2.4) counts each undirected edge twice and therefore reproduces the last
term of (2.2).

<a id="section-3-external-hypotheses"></a>
## 3. Exact external-theorem hypotheses

The primary external authority is:

- Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of Interacting
  Quantum Anharmonic Oscillators*,
  <https://arxiv.org/pdf/math-ph/0609045>.

The package uses its general-case Theorems 3.1--3.3: existence and compactness
of tempered Euclidean Gibbs measures, their uniform exponential moment
estimate, and their support theorem.  For the periodic approximation statement
it uses Propositions 2.12, 2.13, and 2.21 of:

- A. Kargol, Y. Kondratiev, and Y. Kozitsky, *Phase Transitions and Quantum
  Stabilization in Quantum Anharmonic Crystals*,
  <https://arxiv.org/pdf/0710.2303>.

Here is the full parameter map.

1. The external reduced mass is

\[
 m={\chi\over\hbar^2},                                  \tag{3.1}
\]

because `-(2m)^(-1)Delta=-hbar^2(2chi)^(-1)Delta`.

2. Choose any harmonic rigidity `a>0` and write

\[
 U_h(q)={a\over2}|q|^2+V_h(q),                           \tag{3.2}
\]

with

\[
\begin{aligned}
 V_h(q)={}&{r+6c-a\over2}|q|^2+{g\over4}\sum_e q_e^4-hv\cdot q\\
 &+{\lambda\over4}\sum_{\{e,f\}\in E(Q_3)}
 (q_e-q_f)^2(q_e^2+q_f^2).                              \tag{3.3}
\end{aligned}
\]

This is continuous and `V_h(0)=0`.

3. The cube-edge term is nonnegative, and Cauchy--Schwarz gives

\[
 \sum_{e=1}^8q_e^4\ge{|q|^4\over8}.                    \tag{3.4}
\]

Thus the leading part of (3.3) is at least `g|q|^4/32`.  After retaining half
of this quartic, the remaining quadratic and linear terms have a finite
minimum.  Hence, for every compact source interval `|h|<=h0`, there are
common constants `A_V>0` and `B_V in R` such that

\[
 V_h(q)\ge A_V|q|^4+B_V.                                \tag{3.5}
\]

Translation invariance lets one choose `V_h` itself as the common continuous
upper function required by the external assumption.

4. The coarse lattice is `Z3`, and

\[
 \sup_y\sum_z|J_{yz}|=6c<\infty.                        \tag{3.6}
\]

These are exactly the general vector-oscillator hypotheses, with component
dimension `nu=8` and polynomial exponent two.  Therefore the external
existence, compactness, exponential-moment, support, and periodic-accumulation
conclusions apply to the exact Q3LOCK onsite polynomial.  No radial symmetry
is needed for these general conclusions.

The constants in (3.5) can be chosen uniformly on a compact source interval.
Inspection of the cited moment proof shows that its constants use these
uniform stability data, `m`, `a`, `beta`, and the summable interaction norm.
The resulting exponential estimate and path-space compactness are therefore
uniform for `|h|<=h0`.  This uniformity is the load-bearing input when the
source tends to zero below.

<a id="section-4-periodic-pressure-derivative"></a>
## 4. Periodic pressure derivative and factor eight

Let

\[
 M_{v,L}=\sum_{y\in\Lambda_L}v\cdot q_y.                \tag{4.1}
\]

At finite volume the Gibbs trace is analytic in `h`.  Duhamel differentiation
and cyclicity of the trace give

\[
 {d\over dh}\log Z_L(h)=\beta\langle M_{v,L}\rangle_{L,h}. \tag{4.2}
\]

The sign is positive because the Hamiltonian contains `-hM`.  Dividing by
the fine-oscillator normalization in (1.2),

\[
 P'_{\beta,L}(h)
 ={1\over8L^3}\langle M_{v,L}\rangle_{L,h}.             \tag{4.3}
\]

The periodic state is invariant under coarse translations, so

\[
 P'_{\beta,L}(h)={1\over8}
 \langle v\cdot q_0\rangle_{L,h}.                       \tag{4.4}
\]

There is no extra factor of `beta` in (4.4), because `P` is the physical
pressure `log Z/(beta n)`.  For the dimensionless log density
`pi=log Z/n`, the derivative is instead

\[
 \pi'_{\beta,L}(h)={\beta\over8}
 \langle v\cdot q_0\rangle_{L,h}.                       \tag{4.5}
\]

This distinction is audited explicitly by all three verifiers.

<a id="section-5-convex-tangent-selection"></a>
## 5. Convex tangent selection

EXP-000780 proves local-uniform convergence

\[
 P_{\beta,L}(h)\longrightarrow P_\beta(h)               \tag{5.1}
\]

on every compact `h` interval, and the limit is finite, convex, and even.
Consequently, both one-sided derivatives at zero exist and satisfy (1.4).

For a convex function the nondifferentiability set is at most countable.
Choose differentiability points `h_k down to 0` such that

\[
 P_\beta'(h_k)\longrightarrow D_+P_\beta(0).            \tag{5.2}
\]

At a differentiability point, the derivative of every differentiable convex
approximant converging locally uniformly to the limit converges to the limit
derivative.  This follows directly by squeezing the derivative between left
and right secant slopes.  Thus

\[
 \lim_{L\to\infty}P'_{\beta,L}(h_k)=P_\beta'(h_k).       \tag{5.3}
\]

For fixed `h_k`, take a path-space accumulation point of the periodic
finite-volume Euclidean laws.  Proposition 2.21 of the cited review makes it a
translation-invariant tempered DLR measure `mu_hk`.  The external exponential
moment estimate gives uniform integrability of `v dot omega_0(0)`, so (4.4)
and (5.3) pass to the limit:

\[
 {1\over8}\int v\cdot\omega_0(0)\,d\mu_{h_k}
 =P_\beta'(h_k).                                         \tag{5.4}
\]

The family `{mu_hk}` is relatively compact because all `h_k` lie in one
compact interval with common external stability constants.  Pass to a
subsequence converging to `mu_plus`.  For every finite region, the local
specification at source `h` differs from that at zero by the continuous factor

\[
 \exp\left[h\sum_{y\in\Delta}
 \int_0^\beta v\cdot\omega_y(\tau)\,d\tau\right].       \tag{5.5}
\]

The common exponential estimate supplies domination.  Hence the local
specifications are continuous as `h_k to 0`, and the DLR equation passes to
the limit.  Therefore `mu_plus` is a zero-source tempered DLR measure.
Uniform integrability in (5.4) gives the first identity in (1.5).

At zero source, global inversion

\[
 \Theta:\omega\mapsto-\omega                              \tag{5.6}
\]

preserves the specification.  Define `mu_minus=Theta_*mu_plus`.  This proves
the second identity in (1.5).

If `m_+(v)>0`, the two expectations have opposite nonzero signs and the states
are distinct.  Evenness gives the opposite left and right pressure slopes, so
the same strict sign is exactly a directional cusp.  This implication is
proved.  The premise `m_+(v)>0` is not proved for positive `lambda` here.

<a id="section-6-local-normal-corollary"></a>
## 6. Locally normal time-zero corollary

The Euclidean DLR result is already an equilibrium-state construction on loop
configuration space.  A separate compactness argument records what can be
said on the quantum local algebras without claiming an infinite-volume
dynamics.

For the finite periodic Gibbs density matrix, set

\[
 K_L=\sum_{y,e}\left[{p_{y,e}^2\over2\chi}
             +{g\over8}q_{y,e}^4\right].                \tag{6.1}
\]

EXP-000780 gives, as quadratic forms,

\[
 K_L\le H_L(hv)+b_{hv}L^3.                              \tag{6.2}
\]

Let `Phi_L(t)=log Tr exp[-tH_L(hv)]`.  It is convex and
`Phi_L'(beta)=-<H_L>`.  Therefore

\[
 \langle H_L\rangle_{\beta,h}
 \le {2\over\beta}\,[\Phi_L(\beta/2)-\Phi_L(\beta)].    \tag{6.3}
\]

The two linear-volume bounds from EXP-000780 make the right side at most
`C L^3`, uniformly for `h` in a compact interval.  Equations (6.2)--(6.3) and
coarse translation invariance imply, for every fixed finite coarse region
`Delta`,

\[
 \operatorname{Tr}(\rho_{L,h}^{\Delta}K_\Delta)
 \le C|\Delta|.                                         \tag{6.4}
\]

The local operator `K_Delta` has compact resolvent.  If `E_R` is its spectral
projection below energy `R`, then

\[
 \operatorname{Tr}\rho_{L,h}^{\Delta}(1-E_R)
 \le {C|\Delta|\over R}.                                \tag{6.5}
\]

The finite-dimensional compressions are compact, while (6.5) controls the
trace-norm tail.  Thus the local reduced density matrices are trace-norm
precompact.  A diagonal extraction over finite regions gives a compatible,
coarse-translation-invariant, locally normal state on the inductive bounded
local algebra.

Take this extraction along the same finite-volume subsequences used in
Section 5.  Finite-volume Feynman--Kac correspondence identifies every
bounded time-zero multiplication observable in the density-matrix and loop
descriptions, so the limits agree on that subalgebra.  Finally, (6.4) gives a
uniform fourth moment.  Truncating `q` at magnitude `R` leaves a tail bounded
by `C/R^3`, and hence the unbounded first moment also passes.  The resulting
locally normal states realize (1.5).

This is not a KMS theorem.  A KMS statement requires either reconstruction of
a stochastically positive system from a fully verified Euclidean structure or
an independently constructed infinite-volume real-time automorphism group.
Neither is supplied by local normality alone.

<a id="section-7-lambda-zero-phase-boundary"></a>
## 7. The rigorous `lambda=0` phase boundary

The positive-`lambda` model is nonradial, but its decoupled boundary has a
direct established phase theorem.  Set `lambda=0`.  Then the eight species do
not interact onsite and the model is a tensor product of eight scalar
nearest-neighbour quantum `phi4` crystals.

Use the notation of Lemma 3.15 and Theorem 3.20 in
<https://arxiv.org/pdf/0710.2303>.  Split the scalar onsite potential as

\[
 {a\over2}x^2+V(x),\qquad
 V(x)=-b x^2+b_2x^4,                                    \tag{7.1}
\]

and match the exact Q3LOCK boundary polynomial:

\[
 b={a-r-6c\over2},qquad b_2={g\over4}.                 \tag{7.2}
\]

The external double-well condition `b>a/2` is exactly `r+6c<0`.  Its explicit
one-site moment parameter is

\[
 \vartheta_*={2b-a\over4b_2(1+2)}
             =-{r+6c\over3g}.                           \tag{7.3}
\]

With reduced mass and nearest-neighbour intensity

\[
 m={\chi\over\hbar^2},\qquad J=c,                       \tag{7.4}
\]

the phase condition is exactly (1.6).  The theorem then supplies the finite
critical inverse temperature through its stated Falk--Bruch equation and
proves more than one tempered Euclidean Gibbs measure above it.

This phase theorem is prior art.  The TECT calculation is only the exact
parameter substitution and the explicit statement of its boundary scope.
The registered candidate assumes `lambda>0`; the Q3 quartic coupling is
unbounded and does not meet a small bounded-perturbation hypothesis.  No
continuity theorem transporting the `lambda=0` coexistence region to
`lambda>0` was located or proved.

<a id="section-8-positive-lambda-structure"></a>
## 8. Exact positive-`lambda` structural lemmas

Two algebraic facts identify a plausible next phase route but do not close it.

First, Q3LOCK is not `O(8)` invariant.  For equal-norm vectors

\[
 q=(R,0,\ldots,0),qquad
 q'={R\over\sqrt8}(1,\ldots,1),                         \tag{8.1}
\]

the quartic onsite energies are

\[
 W_4(q)={g+3\lambda\over4}R^4,
 \qquad W_4(q')={g\over32}R^4.                          \tag{8.2}
\]

Thus the vector rotation-invariant phase theorems, including Theorems
3.20--3.21 of the cited review, cannot simply be imported for positive
`lambda`.

Second, every internal Q3 edge is coordinatewise attractive.  For

\[
 W(x,y)={\lambda\over4}(x-y)^2(x^2+y^2),                \tag{8.3}
\]

one has

\[
 \partial_x\partial_yW
 =-{\lambda\over2}(3x^2-4xy+3y^2)\le0,                 \tag{8.4}
\]

because the quadratic form in parentheses has eigenvalues `1` and `5`.
The spatial and time-sliced quadratic bonds have the same attractive mixed
sign.  Hence every finite Trotter discretization has the algebraic
log-supermodularity needed for an MTP2/FKG argument.

What remains before this becomes a phase theorem is load-bearing:

1. pass the finite time-slice FKG and spatial reflection-positive inequalities
   to the continuous loop law with the exact normalizations;
2. justify the collective unbounded double commutator by a common core and
   bounded approximation;
3. prove the exact three-dimensional infrared estimate for the collective Q3
   field and certify every Fourier constant; and
4. map positive long-range order to the source subgradient and to distinct
   zero-source DLR states without assuming extremality.

These are the next proof obligations, not assumptions silently used in this
package.

<a id="section-9-proof-boundary"></a>
## 9. Exact proof boundary

The following are proved here or imported with an exact hypothesis map:

- nonempty compact positive-`lambda` tempered Euclidean DLR state sets at
  every positive `beta` and constant source;
- uniform exponential local moments and path-space compactness on compact
  source intervals;
- translation-invariant DLR accumulation points of periodic finite-volume
  loop laws;
- zero-source DLR states realizing both directional endpoint pressure slopes;
- the factor-eight pressure--magnetization normalization and parity relation;
- compatible locally normal time-zero tangent states; and
- a nonempty low-temperature phase regime on the decoupled `lambda=0`
  boundary.

The following remain open:

- strict positivity of a positive-`lambda` source slope;
- positive-`lambda` spontaneous global-Z2 breaking or phase coexistence;
- extremality of the constructed tangent states;
- C-star purity, rank-one character, or spatial/exponential clustering;
- an infinite-volume real-time dynamics and an algebraic KMS theorem;
- a ground-state phase, degeneracy, uniform gap, or ground-state clustering;
- continuum regulator removal and counterterms;
- a physical empty-space reference, absolute vacuum energy, or a
  below-empty-space inequality;
- a controlled `3D -> 1+1` effective reduction; and
- C0, N1--N5, C6, CP1, Sector A, or Pre-A closure.

In particular, an additive scalar still shifts the pressure and energy
density while leaving every normalized Gibbs or DLR law unchanged.  Nothing
in the state construction selects physical empty space.

<a id="section-10-devils-advocate"></a>
## 10. Devil's-advocate audit

1. **Objection: the general quantum-crystal theorem may require a radial
   onsite potential.**  **DISMISSED.**  Radial or scalar hypotheses enter the
   cited phase and ordering theorems, not the general existence, compactness,
   moment, support, or periodic-accumulation results.  Section 3 verifies the
   latter hypotheses directly for the nonradial Q3 polynomial.

2. **Objection: the source destroys the uniform coercive constants needed as
   `h to 0`.**  **DISMISSED.**  On `|h|<=h0`, the linear term is uniformly
   dominated by a retained part of `g|q|^4/32`; common lower and upper data
   feed the same external moment proof.

3. **Objection: existence of some DLR state and existence of a pressure
   tangent do not show that one state realizes the tangent.**  **DISMISSED
   WITH THE PERIODIC BRIDGE.**  At differentiability points, the actual
   periodic finite-volume pressure derivatives converge.  The same periodic
   laws have DLR accumulation points, and uniform integrability passes their
   one-site magnetization.  Compact source-to-zero limits then give (1.5).

4. **Objection: a factor `beta` or eight has been lost.**  **DISMISSED.**
   Equations (4.2)--(4.5) separately audit dimensionless log density and
   thermodynamic pressure.  The source is an energy source and the density is
   per fine oscillator, producing exactly the factor `1/8` in (4.4).

5. **Objection: a Euclidean DLR state is automatically a KMS state on the
   desired infinite oscillator algebra.**  **UPHELD AS A BOUNDARY.**  The
   cited Euclidean construction describes equilibrium Matsubara data but does
   not construct the required pre-existing infinite-volume real-time
   automorphism group.  KMS is kept open.

6. **Objection: the `lambda=0` theorem proves the positive-`lambda` phase by
   continuity.**  **UPHELD.**  The perturbation is an unbounded quartic.  No
   applicable coexistence-stability theorem was located or proved.  The
   boundary result remains a comparator only.

7. **Objection: local normality makes the tangent state extreme, pure, or
   clustering.**  **UPHELD.**  None of those implications holds.  They remain
   separate gates.

8. **Objection: a state theorem fixes an absolute vacuum energy.**
   **UPHELD.**  Normalized states are invariant under additive scalar shifts;
   physical empty-space selection remains external.

<a id="section-11-reproduction"></a>
## 11. Reproduction

Run from the repository root:

```powershell
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split.py
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split_independent.py
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_q3lock_euclidean_dlr_tangent_state_phase_boundary_route_split_verify.py
```

The scripts audit the exact Hamiltonian expansion, Q3 graph and coercivity,
external-theorem parameter map, finite Gibbs source derivative, factor-eight
normalization, convex derivative selection, local compactness bounds, parity,
nonradial witness, edge submodularity, `lambda=0` parameter substitution,
scope firewalls, record integration, and unchanged C6 status.

This package advances a proof route but remains claim-nonbearing.  It does not
change the C6 card.
