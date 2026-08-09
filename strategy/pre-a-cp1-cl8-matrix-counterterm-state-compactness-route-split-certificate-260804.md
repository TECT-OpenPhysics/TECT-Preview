# Pre-A CL8 matrix-counterterm state-compactness route-split certificate

**Candidate:** `PA-CP1-CL8-MATRIX-COUNTERTERM-STATE-COMPACTNESS-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-UNIFORM-COERCIVE-SHIFT-WEAKSTAR-SUBNET-CUT-DEFECT-IDENTITY-REGULARITY-AND-DYNAMICS-NOGOS`  
**Exploration:** `EXP-000765`
**Claim context:** `C6-SPACETIME-SIGNATURE`  
**Authority:** claim-nonbearing `T0`

## 1. Verdict

The Q3 matrix direction found in the preceding Wick audit can be inserted with
an explicit scalar-energy convention so that every finite cutoff obeys the
same quartic form lower bound:

\[
 \boxed{V_C(q)\ge {g\over64}|q|^4}.                         \tag{1.1}
\]

This closes cutoff-uniform **lower stability** in the inserted one-dimensional
regulator convention.  It does not close a uniform energy upper bound or a
moment theorem.

For any states chosen on the resulting dyadic finite-regulator algebras, state
space compactness supplies a compatible subnet on the inductive `C*` limit.
Conjugating the bulk embedding by the registered fixed-regulator cut anchors
also supplies an exact matched-reference-cut algebra square.  The cut anchors
add exactly zero comparison error.  The corresponding exact natural dynamics
square is impossible, however, because the interacting fine force sends one
retained momentum generator into an operator containing the added Nyquist
coordinate.

These statements are intentionally weaker than a regular interacting
continuum state.  A squeezed-oscillator family proves that normality at every
cutoff, a uniform spectral lower bound and gap, and weak-star compactness can
still converge to a nonregular Weyl state.  Uniform fixed-mode moments or
characteristic equicontinuity and a full-sequence identification theorem remain
open.

<a id="section-2-authorities-and-scope"></a>
## 2. Authorities and scope

The inputs are:

1. the exact common-diagonal Q3 Wick contraction from `EXP-000764`;
2. the registered finite CL8 Schrodinger ground/Gibbs theorem;
3. the natural dyadic low-mode embedding, including its exceptional coarse
   Nyquist squeeze; and
4. the registered unitary fixed-regulator reference-cut anchors
   `Gamma_(M,C):H_(M,C)->H_M`.

The package does not import a constructive `P(phi)_2` limit theorem.  Standard
multicomponent polynomial-field constructions are a positive successor route,
but their domination, cutoff convergence, reflection positivity, canonical
identification and history-cut hypotheses must be checked against this exact
Q3 convention before they become repository authority.

<a id="section-3-matrix-counterterm-convention"></a>
## 3. Matrix-counterterm convention

At one spatial point, let

\[
 W_4(q)={g\over4}\sum_{e=1}^8q_e^4
 +{\lambda\over4}\sum_{e\sim f}
 (q_e-q_f)^2(q_e^2+q_f^2),                                \tag{3.1}
\]

where the second sum is over the twelve undirected Q3 edges.  The declared
common-diagonal reference has coincident covariance `C>=0`.  The preceding
exact Wick calculation is

\[
 :W_4:_C
 =W_4+{1\over2}q^T\delta K_Cq+6C^2(g+4\lambda),           \tag{3.2}
\]

\[
 \delta K_C=-3C[(g+\lambda)I+\lambda L_{Q3}].              \tag{3.3}
\]

Declare a fixed renormalized quadratic matrix

\[
 K_R=m_RI+\eta_RL_{Q3}.                                   \tag{3.4}
\]

This package Wick-orders `W_4` only; the finite quadratic (3.4) remains outside
the Wick operator.  If instead the whole quadratic-plus-quartic polynomial
were Wick ordered, one would also obtain the scalar

\[
 -{C\over2}\operatorname{Tr}K_R=-4Cm_R-12C\eta_R.          \tag{3.4a}
\]

That is a different declared energy convention and must not be silently mixed
with the present one.

With this sign convention, the raw polynomial representation of
`(1/2)q^T K_R q+:W_4:_C` has

\[
 K_{\rm raw}(C)=K_R+\delta K_C.                            \tag{3.5}
\]

The Q3 Walsh levels are `2s`, `s=0,1,2,3`, of multiplicities `1,3,3,1`.
Therefore the four raw quadratic eigenvalues are

\[
 \kappa_s(C)=m_R+2s\eta_R
 -3C(g+\lambda+2s\lambda).                                \tag{3.6}
\]

No sign is hidden here: (3.5) is the exact identity obtained by expanding the
normal-ordered expression back into raw powers.

<a id="section-4-uniform-coercive-shift"></a>
## 4. Uniform coercive-shift theorem

Define

\[
 b_C={1\over2}\max\{0,-\min_{0\le s\le3}\kappa_s(C)\},    \tag{4.1}
\]

\[
 \epsilon_C={16b_C^2\over g}-6C^2(g+4\lambda),             \tag{4.2}
\]

and

\[
 V_C(q)={1\over2}q^TK_Rq+:W_4:_C(q)+\epsilon_C.            \tag{4.3}
\]

### Theorem 4.1

For `g>0`, `lambda>=0`, arbitrary real `m_R,eta_R`, and every `C>=0`,

\[
 \boxed{V_C(q)\ge {g\over64}|q|^4\quad\hbox{for all }q\in R^8}. \tag{4.4}
\]

### Proof

Put `x_e=q_e^2`.  The exact sum-of-squares identity

\[
 \sum_eq_e^4-{|q|^4\over8}
 ={1\over8}\sum_{e<f}(q_e^2-q_f^2)^2                     \tag{4.5}
\]

and nonnegativity of every Q3 edge polynomial give

\[
 W_4(q)\ge {g\over32}|q|^4.                               \tag{4.6}
\]

Equation (4.1) gives

\[
 {1\over2}q^T[K_R+\delta K_C]q\ge-b_C|q|^2.               \tag{4.7}
\]

The Wick constant in (3.2) cancels the second term of (4.2).  With
`R^2=|q|^2`, the remaining scalar completion is the exact identity

\[
 {gR^4\over32}-b_CR^2+{16b_C^2\over g}
 ={gR^4\over64}+{(gR^2-32b_C)^2\over64g}.                 \tag{4.8}
\]

Equations (4.6)--(4.8) prove (4.4). `QED`

For the finite spatial regulator with spacing `a`, the registered Hamiltonian
has the weight `a/8`.  Its kinetic and centered spatial-gradient forms are
nonnegative, so (4.4) gives

\[
 \boxed{
 \widehat H_{a,C}\ge {ag\over512}\sum_j|q_j|^4\ge0}.      \tag{4.9}
\]

The coefficient in (4.9) is exactly the Riemann-sum coefficient of one fixed
continuum `L4` density; it is not the deteriorating full-configuration radial
coefficient used by the earlier finite-dimensional heat-trace comparison.

The scalar `epsilon_C` changes all energies and free energies by the same
constant.  It leaves normalized ground projectors and Gibbs densities
unchanged.  For the centered reference `C_N=Theta(log N)`, both `b_C` and the
quadratic coefficients are `O(log N)`, while this sufficient scalar convention
is `O((log N)^2)`.

### Theorem 4.2: Q3-anisotropic strengthening

For `lambda>0`, put

\[
 S=|q|^2,
 \qquad
 T=q^TL_{Q3}q=\sum_{e\sim f}(q_e-q_f)^2.                   \tag{4.10}
\]

Each edge obeys `q_e^2+q_f^2>=(q_e-q_f)^2/2`.  Cauchy over
the twelve Q3 edges then gives

\[
 \sum_{e\sim f}(q_e-q_f)^2(q_e^2+q_f^2)
 \ge {1\over2}\sum_{e\sim f}(q_e-q_f)^4
 \ge {T^2\over24}.                                        \tag{4.11}
\]

Together with (4.5),

\[
 W_4(q)\ge {gS^2\over32}+{\lambda T^2\over96}.            \tag{4.12}
\]

Define

\[
 \alpha_C=[3C(g+\lambda)-m_R]_+,
 \qquad
 \beta_C=[3C\lambda-\eta_R]_+,                            \tag{4.13}
\]

and replace (4.2) by

\[
 \epsilon_C^{\rm aniso}
 ={4\alpha_C^2\over g}+{12\beta_C^2\over\lambda}
 -6C^2(g+4\lambda).                                       \tag{4.14}
\]

Completing one square in `S` and one in `T` yields

\[
 \boxed{
 V_C(q)\ge {gS^2\over64}+{\lambda T^2\over192}}.          \tag{4.15}
\]

Both inequalities in (4.11)--(4.12) are sharp on the Q3 bipartite Walsh ray
`q_e=+x` on one parity and `q_e=-x` on the other.  Equation (4.15) therefore
retains a genuine cutoff-uniform Q3-variation quartic control rather than only
the total-amplitude control (4.4).

At `lambda=0`, (4.14) is not used.  The general Walsh-minimum completion
(4.1)--(4.4) remains valid and absorbs any negative `eta_R` through
`min_s kappa_s` without division by `lambda`.

<a id="section-5-finite-state-and-moment-reduction"></a>
## 5. Finite state and moment reduction

At every fixed regulator, (4.4) is a coercive real polynomial bound.  The
registered Friedrichs, compact-resolvent and positivity-improving arguments
therefore apply unchanged.  There is one simple strictly positive ground and a
faithful trace-class Gibbs density for every positive inverse temperature.

For any normalized state `rho_a` with finite shifted energy,

\[
 {ag\over512}\sum_j
 \operatorname{Tr}(\rho_a|q_j|^4)
 \le\operatorname{Tr}(\rho_a\widehat H_{a,C}).              \tag{5.1}
\]

Thus a cutoff-uniform upper bound on the shifted energy would immediately give
the required Riemann-sum fourth-moment bound.  This package proves the
reduction (5.1), not that upper bound.  A lower form bound alone cannot control
the expectation of the upper side of the spectrum.

The anisotropic bound (4.15) gives a sharper conditional ledger.  With
`w=a/8`, use field values `q_j` and coefficient momenta `Pi_j`, related to the
canonical momenta by `p_j=w Pi_j`.  For vector labels define

\[
 \|f\|_{p,w}=\left(w\sum_j|f_j|^p\right)^{1/p},\qquad
 \Phi_a(f)=w\sum_j f_j\mathbin{\cdot}q_j,                 \tag{5.2a}
\]

\[
 \Pi_a(h)=w\sum_j h_j\mathbin{\cdot}\Pi_j,\qquad
 Z_a^{ef}(l)=w\sum_jl_j(q_{j,e}-q_{j,f}).                 \tag{5.2b}
\]

For `Z`, the label `l` is scalar and the same weighted norm convention is
used.  Suppose a normalized vector state in the Hamiltonian form domain, or a
normal density with finite form expectation, obeys

\[
 \omega_a(\widehat H_{a,C})\le E,                         \tag{5.2}
\]

The form inequality (4.15) contains

\[
 {g\over64}\|q\|_{4,w}^4,\qquad
 {1\over2\chi}\|\Pi\|_{2,w}^2,\qquad
 {\lambda\over192}w\sum_jT_j^2.                         \tag{5.2c}
\]

Weighted Holder gives
`|Phi_a(f)|<=||f||_(4/3,w)||q||_(4,w)`.  Since
`T_j^2>=(q_(j,e)-q_(j,f))^4` for each edge, the same argument and
Cauchy--Schwarz give

\[
 \omega_a(|\Phi_a(f)|^4)
 \le {64E\over g}\|f\|_{4/3,w}^4,                         \tag{5.3}
\]

\[
 \omega_a(|\Pi_a(h)|^2)
 \le2\chi E\|h\|_{2,w}^2,                                \tag{5.4}
\]

and, for any one Q3 edge when `lambda>0`,

\[
 \omega_a(|Z_a^{ef}(l)|^4)
 \le {192E\over\lambda}\|l\|_{4/3,w}^4.                 \tag{5.5}
\]

For the Weyl convention
`W(f,h)=exp[i(Phi_a(f)+Pi_a(h))/hbar]`, the spectral inequality
`||(e^(iR/hbar)-1)Omega||<=||R Omega||/hbar`, the GNS triangle inequality,
and `omega(Phi^2)^(1/2)<=omega(Phi^4)^(1/4)` imply

\[
 |\omega_a(W(f,h))-1|
 \le {1\over\hbar}\left[
 \left({64E\over g}\right)^{1/4}\|f\|_{4/3,w}
 +(2\chi E)^{1/2}\|h\|_{2,w}\right].                    \tag{5.6}
\]

Thus one uniform energy upper bound would close fixed-label Weyl
equicontinuity and all positive local subform controls displayed above.  It is
the missing input, not a conclusion of (4.15).

### 5.1 Pointwise-stability plus Gaussian-trial no-go

There is an exact obstruction to obtaining that input from the simplest two
ingredients alone.  Before an added scalar shift, define the local polynomial

\[
 P_C(q):={1\over2}q^TK_Rq+:W_4:_C(q),                    \tag{5.6a}
\]

and restrict it to the species singlet `q_e=x`.  The Q3 quadratic and quartic
terms vanish and

\[
 F_C(x)=2gx^4+[4m_R-12C(g+\lambda)]x^2
 +6C^2(g+4\lambda).                                      \tag{5.7}
\]

When `12C(g+lambda)>4m_R`,

\[
 \min_xF_C(x)=6C^2(g+4\lambda)
 -{[12C(g+\lambda)-4m_R]^2\over8g}.                       \tag{5.8}
\]

The full eight-component reference Gaussian has `E[:W_4:_C]=0` and hence the
full-polynomial mean

\[
 \mu_C:=\mathbb E_C P_C=C(4m_R+12\eta_R).                 \tag{5.9}
\]

This is not the one-variable Gaussian expectation of the restricted
polynomial `F_C`.  Rather, since
`inf_(q in R^8) P_C(q)<=min_x F_C(x)`, one has

\[
 \mu_C-\inf_qP_C(q)\ge\mu_C-\min_xF_C(x).                 \tag{5.9a}
\]

The lower bound on the right is unchanged by every scalar energy shift and has
leading term

\[
 \left(12g+12\lambda+{18\lambda^2\over g}\right)C^2
 +O(C).                                                    \tag{5.10}
\]

Since `C_N=Theta(log N)`, one scalar cannot make the full pointwise polynomial
uniformly lower bounded and at the same time make the full reference-Gaussian
variational expectation uniformly upper bounded.  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-POINTWISE-STABILITY-GAUSSIAN-TRIAL-UNIFORM-ENERGY`.
It does not exclude Nelson/spatial-kinetic cancellation, a non-Gaussian trial,
or a constructive vector polynomial-field proof.

More explicitly, fix `g,lambda,m_R,eta_R`.  If a scalar `s_C` obeys

\[
 \inf_q[P_C(q)+s_C]\ge-B,
\]

then (5.9a) implies

\[
 \mathbb E_C[P_C+s_C]
 \ge\left(12g+12\lambda+{18\lambda^2\over g}\right)C^2
 +O(C)-B.                                                  \tag{5.11}
\]

Thus the excluded route is exactly a pointwise local bound plus the same Wick
Gaussian and scalar-only normalization.  A sharper global operator bound,
kinetic/Nelson cancellation, different normalization, or different trial state
remains open.

<a id="section-6-ground-entanglement-distance"></a>
## 6. Ground-entanglement distance gate

At cutoff `M`, let `P_(0,M)` abbreviate the ground projector of the present
Wick/matrix-counterterm family with its declared `C_M,K_R`.  For one strict
refinement let `iota_(M,2M,*)` be the predual state restriction of the natural
low-mode embedding and set

\[
 \sigma_M=\iota_{M,2M,*}(P_{0,2M}),
 \quad
 \eta_M=1-\operatorname{Tr}(P_{0,M}\sigma_M),
 \quad
 d_M=\|\sigma_M-P_{0,M}\|_1.                              \tag{6.1}
\]

If the embedding is written in a factorizing chart as

\[
 \iota_{M,2M}(A)=V_{M,2M}(A\otimes I)V_{M,2M}^*,
\]

then

\[
 \sigma_M=\operatorname{Tr}_{\rm add}
 (V_{M,2M}^*P_{0,2M}V_{M,2M}).                            \tag{6.1a}
\]

Bare `Tr_add P_(0,2M)` is generally wrong when the chart has not already
absorbed the reciprocal Nyquist-squeeze unitary.

Since the difference has trace zero, testing the two-outcome effect `P_(0,M)`
gives

\[
 d_M\ge2\eta_M.                                            \tag{6.2}
\]

The upper Fuchs--van de Graaf inequality against the pure state `P_(0,M)`
gives

\[
 d_M\le2\sqrt{\eta_M}.                                    \tag{6.3}
\]

Consequently

\[
 \boxed{d_M\to0\quad\Longleftrightarrow\quad\eta_M\to0}. \tag{6.4}
\]

The preceding collective mixed-derivative theorem proves `eta_M>0` at every
strict refinement for this enlarged family as well: the added quadratic and
scalar counterterms do not change the nonzero `X^2Y^2` derivative.  It proves
neither a cutoff-independent positive lower
bound nor decay to zero.  Exact finite-pair projectivity is closed negatively;
asymptotic trace-norm projectivity is still an explicit quantitative gate.

For any norm-one Weyl observable `W(F)` in the retained factor,

\[
 |\operatorname{Tr}[(\sigma_M-P_{0,M})W(F)]|
 \le d_M\le2\sqrt{\eta_M}.                                \tag{6.5}
\]

No converse lower bound for one preselected Weyl label is claimed.

<a id="section-7-abstract-compatible-subnet"></a>
## 7. Abstract compatible-subnet theorem

Let `M_0,2M_0,4M_0,...` be the dyadic regulators.  Write

\[
 \mathcal A_M=B(\mathcal H_M),                              \tag{7.1}
\]

and let `iota_(M,N)` be the natural unital low-mode monomorphism.  The coarse
self-conjugate Nyquist oscillator uses

\[
 \iota(\Phi^M_{M/2})=\sqrt2\Phi^N_{M/2},
 \qquad
 \iota(\Pi^M_{M/2})={1\over\sqrt2}\Pi^N_{M/2}.            \tag{7.2}
\]

At later refinements that frequency is non-Nyquist, so the following maps are
the identity on its continuum-normalized pair.  Hence (7.2) composes
transitively with all later embeddings.

Choose any state `omega_N` on every finite `A_N`, for example the ground or a
fixed-`beta` Gibbs state of Section 5.  For fixed `M`, consider the tail

\[
 \omega_N\circ\iota_{M,N}\in S(\mathcal A_M),\qquad N\ge M. \tag{7.3}
\]

### Theorem 7.1

There is a cofinal subnet `N_alpha` and states `omega_M^(infinity)` such that

\[
 \omega_{N_\alpha}(\iota_{M,N_\alpha}A)
 \longrightarrow\omega_M^{(\infty)}(A)                    \tag{7.4}
\]

for every fixed `M` and every `A in A_M`.  The limits are compatible and define
a state on the unital inductive `C*` limit.

### Proof

Each state space `S(A_M)` is weak-star compact.  Their Cartesian product is
compact by Tychonoff.  Regard every cutoff state as the tuple of all available
lower-regulator restrictions, filling its as-yet unavailable higher-regulator
coordinates arbitrarily.  For each fixed coordinate those fillers disappear
on a tail.  A cofinal subnet converges in the product.  For
`M<=K` and `A in A_M`, transitivity gives

\[
 \omega_N(\iota_{M,N}A)
 =\omega_N(\iota_{K,N}(\iota_{M,K}A)).                     \tag{7.5}
\]

Taking the subnet limit proves

\[
 \omega_M^{(\infty)}(A)
 =\omega_K^{(\infty)}(\iota_{M,K}A).                       \tag{7.6}
\]

The compatible positive norm-one functionals define the claimed inductive
limit state. `QED`

This theorem is deliberately abstract.  The subnet may depend on the chosen
cofinal refinement, and the limit can be singular on every type-I factor or
nonregular on the Weyl generators.  It contains no local-energy, dynamics,
microlocal or physical-state information.

### 7.1 The incomparable cylindrical full-sequence topology

For a fixed cutoff-independent real mode space `V_K` and radius `R`, define

\[
 \varepsilon_{M,N;K,R}
 =\sup_{\substack{F\in V_K\\\|F\|\le R}}
 |\omega_N(W(\iota_{M,N}F))-\omega_M(W(F))|.               \tag{7.7}
\]

Fixed `K` eventually lies strictly below the moving coarse Nyquist mode, so its
labels use only the identity part of the continuum-normalized embedding.  For
a Weyl polynomial `B=sum_l c_l W(F_l)`,

\[
 |\Delta_{M,N}(B)|
 \le\sum_l|c_l|\varepsilon_{M,N}(F_l).                     \tag{7.8}
\]

If `A` is an arbitrary element of the fixed-`K` Weyl `C*` algebra, norm
approximation by `B` gives

\[
 |\Delta_{M,N}(A)|
 \le2\|A-B\|+\sum_l|c_l|\varepsilon_{M,N}(F_l).            \tag{7.9}
\]

The full-sequence target is the Cauchy condition

\[
 \lim_{n\to\infty}\sup_{m\ge n}
 \varepsilon_{M_n,M_m;K,R}=0.                             \tag{7.10}
\]

Adjacent defects merely tending to zero do not imply (7.10).  Because the
embeddings compose, a summable dyadic estimate such as

\[
 \varepsilon_{M_n,M_{n+1};K,R}=O(a_n^p),\qquad p>0,        \tag{7.11}
\]

is sufficient by telescoping.  Compactness plus uniqueness of the cluster
state gives pointwise full-sequence convergence; to upgrade that conclusion to
the uniform-on-label-ball supremum in (7.10), one also needs uniform
equicontinuity on the fixed finite-dimensional `V_K` ball (or another direct
uniformity theorem).

The overlap `eta_M` of Section 6 controls the stronger **full retained-factor**
trace norm.  It is not necessary for (7.10): global ultraviolet entanglement
can stay nonzero while every fixed-`K` marginal converges.

<a id="section-8-matched-reference-cut-square"></a>
## 8. Matched-reference-cut square and exact defect identity

Fix matched typed cut data `c_M=(C_M,n_M)` and `c_N=(C_N,n_N)` at regulators
`M<=N`.  Their registered unitary anchors have the exact type

\[
 \Gamma_{M,C_M}^{[n_M]}:
 \mathcal H_{M,C_M}\longrightarrow\mathcal H_M.           \tag{8.1}
\]

Below, `Gamma_(M,C)` abbreviates this full typed datum and likewise at `N`;
"matched" means precisely that this chosen pair is used to transport the one
declared bulk embedding.  It does not assert a regulator-independent physical
identification of cut combinatorics.

Define the normal isomorphism

\[
 \theta_{M,C}(A)=\Gamma_{M,C}^*A\Gamma_{M,C}.              \tag{8.2}
\]

The inter-regulator cut monomorphism is now a definition with no missing
orientation:

\[
 j_{M,N,C}
 =\theta_{N,C}\circ\iota_{M,N}\circ\theta_{M,C}^{-1}.     \tag{8.3}
\]

It obeys the exact square

\[
 j_{M,N,C}(\Gamma_{M,C}^*A\Gamma_{M,C})
 =\Gamma_{N,C}^*\iota_{M,N}(A)\Gamma_{N,C}.                \tag{8.4}
\]

For a bulk state `omega_M`, define the anchored cut state

\[
 \Omega_{M,C}=\omega_M\circ\theta_{M,C}^{-1}.              \tag{8.5}
\]

If `B=theta_(M,C)(A)`, direct substitution gives

\[
 \boxed{
 \Omega_{N,C}(j_{M,N,C}B)-\Omega_{M,C}(B)
 =\omega_N(\iota_{M,N}A)-\omega_M(A)}.                    \tag{8.6}
\]

Thus the cut anchors add exactly zero comparison error.  Because every theta is
isometric, the same identity holds for the corresponding dual state norm.
Along the subnet of Theorem 7.1, every fixed cut observable therefore converges
to the cut pullback of the compatible limit state.

For normal densities let `iota_(M,N,*)` denote the predual restriction,
characterized by
`Tr[iota_(M,N,*)(rho_N)A]=Tr[rho_N iota_(M,N)(A)]`.  The exact dual-norm form is

\[
 \|\Omega_{N,C}\circ j_{M,N,C}-\Omega_{M,C}\|
 =\|\iota_{M,N,*}(\rho_N)-\rho_M\|_1.                    \tag{8.7}
\]

If `iota_(M,N)(A)=V_(M,N)(A tensor I)V_(M,N)^*`, then the first density is
`Tr_add[V_(M,N)^* rho_N V_(M,N)]`.  It becomes bare `Tr_add rho_N` only when
the chosen tensor-factor chart has already absorbed `V_(M,N)`, including the
unitary which implements the exceptional reciprocal Nyquist squeeze.

The registered same-time re-slicing maps are natural for these embeddings as
well.  At regulator `M`, the two cut anchors `C_M,D_M` must carry the same
history index `n_M`; at `N` they must carry the same `n_N`.  With those typed
data, put

\[
 S^M_{D\leftarrow C}=\Gamma_{M,D}^*\Gamma_{M,C},
 \qquad
 \beta^M_{D\leftarrow C}(B)=S^M_{D\leftarrow C}B
 (S^M_{D\leftarrow C})^*.                                \tag{8.8}
\]

Anchor cancellation gives the exact all-same-time-cut square

\[
 \boxed{
 j_{M,N,D}\circ\beta^M_{D\leftarrow C}
 =\beta^N_{D\leftarrow C}\circ j_{M,N,C}}.                \tag{8.9}
\]

Equations (8.3) and (8.9) construct only matched same-time cut squares.  They do
not identify unmatched cut combinatorics between regulators, intertwine a
physical step, or turn the original finite states into an exact projective
family.

<a id="section-8a-natural-dynamics-no-go"></a>
### 8.1 Exact natural interacting dynamics no-go

For the declared inserted-one-dimensional Hamiltonians with `g>0`, the natural
low-mode embedding, and the allowed scalar-energy plus scalar/Q3-quadratic
counterterm class, exact Heisenberg equivariance would require

\[
 \iota_{M,N}\circ\operatorname{Ad}(e^{itH_M/\hbar})
 =\operatorname{Ad}(e^{itH_N/\hbar})\circ\iota_{M,N}       \tag{8.10}
\]

and therefore invariance of the type-I factor `B(H_low) tensor I`.  The
normalizer theorem for type-I tensor factors then forces, up to phase,

\[
 e^{-itH_N/\hbar}=e^{i\alpha(t)}u_{\rm low}(t)\otimes
 u_{\rm add}(t).                                          \tag{8.10a}
\]

Strong continuity makes the generator additive on the common invariant
Schwartz tensor core.  After subtracting the already additive kinetic and
quadratic pieces, the multiplication potential would have to be a sum of a
low-only and an added-only polynomial.

On the exact collective plane of `EXP-000764`, the fine potential contains

\[
 {3g\over2L}X^2Y^2.                                       \tag{8.11}
\]

Here `X` is retained and `Y` is the added fine Nyquist coordinate.  Thus

\[
 {i\over\hbar}[H_N,P_X]
 =-\partial_XU_N
 \supset-{3g\over L}XY^2.                                 \tag{8.12}
\]

Equivalently, its exact mixed derivative is

\[
 \partial_X^2\partial_Y^2U_N={6g\over L}>0,               \tag{8.12a}
\]

which is impossible for an additive low-plus-added potential.  The force in
(8.12) is a cubic term, quadratic in the added coordinate, and is not
affiliated with the retained factor.  A scalar energy
has zero force.  Scalar and Q3-Laplacian quadratic counterterms have only
linear forces, and the Q3 term vanishes on this collective species-singlet
plane.  They cannot cancel (8.12).

Consequently (8.10) is impossible for `g>0`.  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-EXACT-DYNAMICS-EQUIVARIANCE`.
The result does not exclude asymptotic fixed-observable dynamics, dressed or
nonnatural embeddings, completely positive reduced dynamics, Hamiltonians of
mean force, or a different perfect-action regulator.

<a id="section-9-regularity-no-go"></a>
## 9. Abstract compactness does not prove regularity

Set `hbar=1` and take one oscillator with

\[
 h_N={1\over2}\left(NP^2+{Q^2\over N}\right).             \tag{9.1}
\]

Its spectrum is

\[
 \operatorname{spec}(h_N)=\{n+1/2:n=0,1,2,\ldots\},        \tag{9.2}
\]

so the lower spectral value and the gap are independent of `N`.  Its unique
ground is a regular normal squeezed Gaussian with

\[
 \langle Q^2\rangle_N={N\over2},
 \qquad
 \langle P^2\rangle_N={1\over2N}.                          \tag{9.3}
\]

For `W(u,v)=exp[i(uQ+vP)]`,

\[
 \omega_N(W(u,v))
 =\exp\left[-{Nu^2+v^2/N\over4}\right].                   \tag{9.4}
\]

The pointwise limit is zero for every `u!=0` and one for `u=0`.  It is
discontinuous at the Weyl identity.  Being a pointwise limit of states, it is
a state, but it is nonregular.

This proves
`NG-2026-08-04-PRE-A-CP1-CL8-ABSTRACT-COMPACTNESS-ONLY-REGULAR-CONTINUUM-STATE`:
finite-cutoff normality, uniform lower stability or even a uniform gap, and
abstract state-space compactness do not imply a regular continuum state.  The
witness is an abstract one-mode control, not a claim that the CL8 limit is
nonregular.

<a id="section-10-positive-regularity-gate"></a>
## 10. Positive regularity and full-sequence gates

For `F=(f,h)` in a fixed finite mode space `V_K`, define the dimensionless
self-adjoint generator and its Weyl unitary by

\[
 R(F)={\Phi_a(f)+\Pi_a(h)\over\hbar},\qquad W(F)=e^{iR(F)}.
\]

Functional calculus and Cauchy--Schwarz give

\[
 |1-\omega_N(W(F))|
 \le\omega_N(|e^{iR(F)}-1|)
 \le\sqrt{\omega_N(R(F)^2)}.                              \tag{10.1}
\]

Therefore one sufficient mechanism is the cutoff-uniform estimate

\[
 \omega_N(R(F)^2)\le C_K\|F\|^2                           \tag{10.2}
\]

which implies uniform Weyl equicontinuity on `V_K` and regularity of every
pointwise cluster state there.  This particular quadratic-moment bound is not
claimed necessary.  Higher moments or local energy are separate requirements
for composite fields and dynamics.

Equicontinuity does not remove subnet dependence.  Full-sequence convergence
still needs a Cauchy estimate, uniqueness of a Euclidean/DLR state, a
Hamiltonian convergence theorem, or another exact identification principle.
For the stronger full retained-factor ground route, (6.4) names the exact
missing quantity `eta_M->0`.  It is not necessary for the weaker fixed-`K`
cylindrical route, which instead needs local reduced-density or direct
characteristic estimates.

<a id="section-11-constructive-positive-branch"></a>
## 11. Constructive positive branch, not yet imported

The inserted model has one spatial dimension, finitely many field components,
and a local quartically coercive polynomial.  Multicomponent `P(phi)_2`
construction and Osterwalder--Schrader reconstruction are established prior
art, not TECT novelties.  This places a finite-torus vector `P(phi)_2`
construction among the serious positive candidates.  To use such a theorem
here, the next package must still:

1. declare one positive massive eight-component Gaussian covariance;
2. verify the external theorem's polynomial domination hypothesis for the
   exact Q3 edge polynomial and the sign convention (3.2)--(3.5);
3. prove uniform exponential integrability and cutoff convergence in the
   theorem's stated topology;
4. verify time-reflection positivity for the chosen approximation if an
   Osterwalder--Schrader Hamiltonian is claimed;
5. identify the resulting Euclidean cutoff with the canonical CL8 regulator
   rather than merely sharing a polynomial;
6. prove that the Euclidean convergence induces equal-time Weyl convergence in
   topology (7.7), rather than assuming that Schwinger-function or density
   convergence alone suffices; and
7. combine the resulting fixed-observable convergence with (8.6).

A finite Euclidean-time circle targets a `beta`-KMS state, whereas an infinite
Euclidean-time construction is needed for a ground/vacuum target.  OS
reconstruction, Lorentzian continuation, and the Hadamard/microlocal condition
remain separate gates.  A finite-torus construction alone cannot establish a
thermodynamic phase transition.

The equal-time `C_N` in this package is the vacuum covariance used by the
Hamiltonian Wick convention.  A finite-temperature Euclidean-torus covariance
contains an additional cutoff-convergent thermal term.  The logarithmic matrix
direction agrees, but the finite scalar, mass and Q3-Laplacian conventions do
not agree automatically.  A Euclidean import must either use the Hamiltonian
vacuum convention and construct thermal states afterward or write the finite
scheme translation explicitly.

There is also a dynamics boundary.  Holding `K_R` fixed makes the raw scalar
and Q3-Laplacian coefficients in (3.5) run like `-C_N`, hence like `-log N`.
The registered classical `O(a^2)` and history-dynamics theorems use a fixed
bare polynomial.  They cannot be imported uniformly into this running family
without a new force, flow and cut-convergence proof.

Until those checks are registered, constructive field theory is prior-art
guidance, not a TECT proof.

<a id="section-12-input-output-ledger"></a>
## 12. Input/output ledger

### Inputs

- the inserted one-dimensional finite CL8 Hamiltonian and `a/8` weight;
- the exact Q3 Wick matrix from `EXP-000764`;
- arbitrary fixed real renormalized `m_R,eta_R`;
- the natural dyadic type-I low-mode embeddings; and
- matched typed registered unitary fixed-regulator cut anchors, including their
  history indices.

### Derived

- the exact raw/renormalized matrix-counterterm sign convention;
- the uniform isotropic and Q3-anisotropic lower bounds (4.4) and (4.15);
- fixed-regulator ground/Gibbs existence for the enlarged candidate;
- the conditional moment and Weyl-equicontinuity reductions (5.3)--(5.6);
- the scalar-shift/reference-Gaussian uniform-energy no-go;
- the exact ground entanglement-distance bounds (6.2)--(6.4);
- an abstract compatible subnet state on the inductive algebra;
- the cylindrical full-sequence Cauchy and summable-adjacent criteria;
- exact matched same-time cut squares and cut/bulk defect identities;
- the exact natural interacting dynamics-equivariance no-go; and
- the squeezed-state regularity no-go.

### Not derived

- a uniform shifted-energy upper bound or moment/local-energy estimate;
- fixed-`K` convergence, full-factor decay of `eta_M`, or a normal regular
  cluster state;
- uniqueness or a full-sequence interacting limit;
- asymptotic/dressed dynamics equivariance or arbitrary cut comparison;
- a constructive `P(phi)_2`, OS, continuum-QFT or Hadamard theorem;
- the original three-dimensional Q3 parent;
- a physical vacuum or below-empty-space comparison; or
- C0, N1--N5, C6 advancement, CP1 or Pre-A completion.

<a id="section-13-adversarial-review"></a>
## 13. Adversarial review

1. **Wick counterterm sign reversed? DISMISSED.**  Equation (3.5) is obtained
   by expanding the declared normal-ordered expression, and the scripts derive
   its four Walsh coefficients from (3.3).
2. **The Q3 quartic could be negative? DISMISSED for `lambda>=0`.**  Every edge
   term is a square times a sum of squares; (4.5) controls the onsite part.
3. **The quadratic Wick scalar was omitted? DISMISSED BY SCHEME TYPING.**  This
   package Wick-orders `W_4` only.  Equation (3.4a) records the extra scalar
   required by a whole-polynomial Wick convention.
4. **The scalar completion lost a factor two? DISMISSED.**  Expanding the exact
   square in (4.8) returns all three coefficients.
5. **The `a` coefficient is nonuniform? DISMISSED AS A CONVENTION ERROR.**
   `a sum_j` is the fixed-volume Riemann sum.  No full-configuration Euclidean
   radial constant is claimed.
6. **A lower bound proves moments of the ground? UPHELD AS AN OVERCLAIM.**
   Equation (5.1) also needs a uniform upper bound on the shifted ground energy.
7. **One scalar plus the reference Gaussian supplies that upper bound?
   DISMISSED.**  The exact invariant gap (5.10) grows as `C_N^2`.
8. **Exact finite-pair failure forbids asymptotic convergence? UPHELD AS AN
   OVERCLAIM.**  Strict `eta_M>0` does not decide whether `eta_M->0`.
9. **Full-factor `eta_M` is necessary for fixed-`K` convergence? UPHELD AS
   FALSE.**  Ultraviolet entanglement can remain while every fixed low-mode
   marginal converges.
10. **Tychonoff compactness gives a normal state? UPHELD AS FALSE.**  Normal
   states are not closed in the full state-space weak-star topology.
11. **The cut square proves state projectivity? UPHELD AS FALSE.**  Equation
   (8.6) transfers the bulk defect unchanged; it does not cancel it.
12. **Quadratic counterterms restore exact dynamics equivariance? DISMISSED.**
    The retained force leakage (8.12) is a cubic force term, quadratic in the
    added mode and arising from the quartic interaction; it cannot be canceled
    by a linear counterterm force.
13. **Uniform gap forces Weyl regularity? DISMISSED.**  Equations (9.1)--(9.4)
   are an exact counterexample.
14. **Regular cluster implies a unique physical vacuum? UPHELD AS FALSE.**
    Full-sequence identification and a physical state criterion are separate.
15. **Constructive `P(phi)_2` applies automatically? UPHELD AS AN UNCHECKED
    IMPORT.**  Section 11 lists the coefficient, domination, positivity and
    canonical-composition checks still required.
16. **The running family inherits fixed-bare dynamics? UPHELD AS FALSE.**  The
    raw coefficients run with `C_N`; the existing fixed-parameter convergence
    theorem is not uniform in that new input.
17. **The energy shift identifies empty space? DISMISSED.**  It is a stability
    convention and does not identify a physical reference or energy sign.

<a id="section-14-verification"></a>
## 14. Verification

Run:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_matrix_counterterm_state_compactness_route_split_verify.py
```

The primary route uses exact symbolic Q3 matrices, polynomial identities,
state-distance controls, cut-anchor matrices and squeezed covariance limits.
The independent route imports neither SymPy nor NumPy and rebuilds the Q3,
Fraction polynomial, trace, cut-square and squeezed fixtures independently.

<a id="section-15-next-gate"></a>
## 15. Next gate

The active gate becomes

`PA-CP1-CL8-UNIFORM-WEYL-EQUICONTINUITY-AND-INTERACTING-LIMIT-IDENTIFICATION`.

The most promising positive branch is a fully typed finite-torus
eight-component constructive polynomial-field construction.  It must first
prove uniform exponential/moment estimates and cutoff convergence for the
exact Q3 Wick polynomial.  Only then can (8.6) move that convergence to the
matched history-cut algebras.  The one-dimensional-to-three-dimensional Q3
parent and physical state/reference gates remain parallel and independent.
