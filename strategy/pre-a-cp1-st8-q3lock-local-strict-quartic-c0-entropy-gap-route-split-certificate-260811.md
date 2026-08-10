# R-167 v1.7 certificate: local-strict carrier, quartic norm no-go, Gibbs tails, and gap split

## 0. Result identity and exact boundary

- **Result:** `R-167`, additive version `v1.7`; no new result number.
- **Stable result ID:**
  `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`.
- **Exploration:** `EXP-000804`.
- **Claim context:** `C6-SPACETIME-SIGNATURE`, `T0`,
  `claim_bearing: false`.
- **Exact model:** the registered fixed-spacing ST8/Q3LOCK oscillator with
  positive `g`, nonnegative Q3 coupling `lambda`, positive kinetic coefficient
  `chi`, and positive spatial harmonic coefficient `c`.

This version proves two finite-scope positive theorems and four independent
route boundaries.

1.  In each fixed finite region, the bounded local-strict, strong-star,
    compact-resolvent graph, and energy-constrained topologies agree.  The
    exact onsite and commuting all-bond subflows are continuous and energy
    controlled there.
2.  In one exact finite Gibbs system, a configuration character has a fixed
    relative-entropy cost and therefore an inverse-logarithmic two-orientation
    coordinate-tail bound.
3.  The full unsplit Q3 quartic onsite flow is not point-norm continuous on a
    carrier containing a raw momentum Weyl or a basic momentum resolvent.
4.  The pure quartic potential kick does not preserve the full finite-site
    Buchholz--Grundling resolvent algebra.
5.  Relative entropy plus finitely many tilted moments does not imply the
    dynamic Gaussian history tail required by the current corridor method.
6.  Distinct pure disjoint ordered ground states with a simple ground vector
    do not imply a positive broken-sector GNS gap.

The old combined successor
`PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-COMMON-ALPHA-AND-BROKEN-GNS-GAP`
is therefore split.  The dynamics successor and the spectral-gap successor
are logically independent.

## 1. Exact finite-region local-strict topology

Let `Y` be a finite ambient region, let

\[
 {\cal H}_Y=L^2(\mathbb R^{8|Y|}),\qquad K_Y\ge 1,                 \tag{1.1}
\]

where `K_Y` is any positive compact-resolvent control.  Put

\[
 {\cal M}_Y=B({\cal H}_Y)=M(K({\cal H}_Y)).                        \tag{1.2}
\]

On norm-bounded sets, the strict topology of this multiplier algebra is the
strong-star topology.  Fix `0<s<=1/2` and define

\[
 q_{s,Y}(A)=\|AK_Y^{-s}\|+\|K_Y^{-s}A\|.                          \tag{1.3}
\]

For `E>inf spec(K_Y)`, define the two-sided energy-constrained seminorm

\[
 e_{E,Y}(A)=\max\left\{
 \sup_{\substack{\|\psi\|=1\\\langle\psi,K_Y\psi\rangle\le E}}
        \|A\psi\|,
 \sup_{\substack{\|\psi\|=1\\\langle\psi,K_Y\psi\rangle\le E}}
        \|A^*\psi\|
 \right\}.                                                       \tag{1.4}
\]

If `||A||<=M`, spectral splitting at energy `E` gives

\[
 e_{E,Y}(A)
 \le E^s\max\{\|AK_Y^{-s}\|,\|K_Y^{-s}A\|\},                    \tag{1.5}
\]

and

\[
 q_{s,Y}(A)\le 2e_{E,Y}(A)+2ME^{-s}.                              \tag{1.6}
\]

Because `K_Y^{-s}` is compact with dense range, a norm-bounded net converges
strictly if and only if it converges in `q_(s,Y)`, and (1.5)--(1.6) show that
this is also equivalent to convergence in every `e_(E,Y)`.  This is a
finite-region theorem.  No uniformity in `Y` is hidden in the equivalence.

## 2. The exact subflows on the local-strict carrier

For the onsite subflow, choose the separate compact-resolvent control
`K_Y^os` to be a positive weighted sum of the exact zero-source onsite
Hamiltonians.  It commutes with the tensor onsite flow.  Onsite conjugation is
therefore an isometry for the versions of (1.3) and (1.4) defined by
`K_Y^os`, and is strict-`C0` because the finite-region implementing unitary
is strongly continuous.

For the commuting all-bond kick write

\[
 \beta_\delta(A)=B_\delta^*AB_\delta.                              \tag{2.1}
\]

Let an observable be supported in `X`, fix one finite ambient region `Y`
containing `N_1(X)`, and use the registered centered positive control
`K_(Y,mu)` of R-167 v1.3.  For `0<|delta|<=1`, its weighted-form
calculation gives, for both signs,

\[
 B_{\pm\delta}^*K_{Y,\mu}B_{\pm\delta}\le M_\delta K_{Y,\mu},
 \qquad M_\delta=1+C_b|\delta|,                                   \tag{2.2}
\]

where

\[
 C_b=1+{c^2z^2e^\mu\over2\chi\sqrt\gamma}.                       \tag{2.3}
\]

Consequently

\[
 e_{E,Y}(\beta_\delta A)\le e_{M_\delta E,Y}(A),
 \qquad
 q_{s,Y}(\beta_\delta A)\le M_\delta^s q_{s,Y}(A).               \tag{2.4}
\]

The support action is exact: onsite evolution fixes `X`, while the all-bond
kick sends it into `N_1(X)` inside `Y`.  For observables whose unbounded
commutators are defined on the common polynomial/Schwartz core,

\[
 [q_x,\beta_\delta(A)]=\beta_\delta([q_x,A]),                     \tag{2.5}
\]

\[
 [p_x,\beta_\delta(A)]
 =\beta_\delta\!\left([p_x,A]-\delta c\sum_{y\sim x}[q_y,A]\right).
                                                                        \tag{2.6}
\]

Thus the directed finite-region multiplier net is a genuine beta- and
phase-state-independent local-strict **subflow carrier**.  It is not yet a
continuous-time thermodynamic dynamics.  Split products have growing support,
and no all-shape exhaustion Cauchy estimate has been proved.

Uniformity over every locally normal state would not weaken the topology:
locally,

\[
 \sup_\rho\operatorname{Tr}(\rho D^*D)=\|D\|^2.                  \tag{2.7}
\]

The surviving infinite-volume route must therefore use compatible
energy-density/state-tempered families rather than the supremum over all
normal states.

## 3. Full-Q3 high-energy packet: the exact derivations

At one full eight-component Q3 site, let

\[
 h=\sum_j{p_j^2\over2\chi}+V(q),\qquad
 K=h-\inf\sigma(h)+1,\qquad
 \delta={i\over\hbar}[h,\,\cdot\,].                               \tag{3.1}
\]

Put `G=g+3lambda>0`,

\[
 W_a=e^{-iap_0/\hbar},\quad a\ne0,\quad
 R_0=(i+p_0)^{-1},\quad
 D_a(q)=V(q)-V(q-ae_0),\quad F_0=\partial_0V.                      \tag{3.2}
\]

The exact Q3 force is

\[
 F_0=(g+3\lambda)q_0^3
 -{3\lambda\over2}q_0^2\sum_{j\sim0}q_j
 +\lambda q_0\sum_{j\sim0}q_j^2
 -{\lambda\over2}\sum_{j\sim0}q_j^3
 +\text{terms of degree at most one}.                              \tag{3.3}
\]

On Schwartz space,

\[
 \delta W_a={i\over\hbar}D_aW_a,                                 \tag{3.4}
\]

\[
 \delta^2W_a={i\over2\chi\hbar}
    \sum_j\{p_j,\partial_jD_a\}W_a-\hbar^{-2}D_a^2W_a,           \tag{3.5}
\]

\[
 \delta R_0=R_0F_0R_0,                                           \tag{3.6}
\]

\[
 \delta^2R_0=2R_0F_0R_0F_0R_0
 +{1\over2\chi}R_0\sum_j\{p_j,\partial_jF_0\}R_0.              \tag{3.7}
\]

The signs in (3.4)--(3.7) follow from `[q_0,R_0]=-i hbar R_0^2` and
`[V,R_0]=-i hbar R_0F_0R_0`.

## 4. The quartic graph endpoint and packet limit

The symbol of `K` is globally elliptic for the anisotropic degree assigning
degree one to `q` and degree two to `p`.  The standard global polynomial
elliptic graph estimate implies that `K^(3/2)` controls every
polynomial-differential monomial of anisotropic degree at most six.  Equations
(3.5) and (3.7) contain only such terms; commuting `q_0` through `R_0` lowers
the coordinate degree.  A fixed translation `W_a` conjugates `K` to a
graph-equivalent shifted globally elliptic operator.  Therefore

\[
 \|\delta^2(A)K^{-3/2}\|<\infty,
 \qquad A\in\{W_a,R_0\}.                                         \tag{4.1}
\]

This is first proved on Schwartz space and extended by graph closure.  The
globally elliptic polynomial onsite propagator preserves Schwartz space;
equivalently, the commutator identities extend as graph-bounded maps on
`D(K^(3/2))`.  Thus the vector Taylor formula below has a common invariant
core and a closed graph-domain extension.

Fix a normalized Schwartz vector `psi` and translate it along the Q3 axis,

\[
 \psi_R=e^{-iRp_0/\hbar}\psi.                                    \tag{4.2}
\]

The exact leading force and quartic energy give

\[
 R^{-3}\|\delta W_a\psi_R\|\longrightarrow {|a|G\over\hbar},    \tag{4.3}
\]

\[
 R^{-3}\|\delta R_0\psi_R\|
 \longrightarrow G\|R_0^2\psi\|>0,                             \tag{4.4}
\]

and

\[
 \|K^{3/2}\psi_R\|=O(R^6).                                      \tag{4.5}
\]

Let `t_R=tau R^(-3)`.  The vector Taylor formula, (4.1), and conservation of
`K` under the onsite flow give

\[
 \|(\alpha_{t_R}(A)-A)\psi_R\|
 \ge \tau d_A-{\tau^2\over2}C_AM_\psi+o(1).                     \tag{4.6}
\]

Here

\[
 d_{W_a}={|a|G\over\hbar},\qquad
 d_{R_0}=G\|R_0^2\psi\|,\qquad
 C_A=\|\delta^2(A)K^{-3/2}\|,\qquad
 M_\psi=\limsup_{R\to\infty}R^{-6}\|K^{3/2}\psi_R\|<\infty. \tag{4.7}
\]

For each `A=W_a,R_0`, choose one fixed positive `tau` smaller than
`2d_A/(C_AM_psi)` (with the evident interpretation if the product vanishes).
Then

\[
 \liminf_{R\to\infty}
 \|\alpha_{\tau R^{-3}}(A)-A\|>0.                               \tag{4.8}
\]

Because `tau R^(-3)` tends to zero, the full unsplit quartic onsite flow is
not point-norm `C0` on any invariant concrete C-star subalgebra containing
either label.  Equation (4.8) asserts a positive discontinuity, not the exact
value one or two.  For the full resolvent algebra, the conclusion is
conditional on invariance: if the unsplit flow preserves it, its action is not
point-norm continuous.  This certificate does not decide unsplit
resolvent-algebra invariance.

## 5. The pure quartic kick leaves the resolvent algebra

There is a stronger exact statement for the pure potential subflow.  Let

\[
 W_4(re_0)={G\over4}r^4,\qquad
 U_t=e^{itW_4(Q)/\hbar},\qquad
 R_\mu=(i\mu-p_0)^{-1},\quad \mu\ne0,                             \tag{5.1}
\]

and put `A_t=U_tR_muU_t^*`.  For a nonzero configuration translation
`S_s=e^(-is p_0/hbar)`, direct multiplication gives

\[
 U_t^*S_sU_t=M_{\Phi_{s,t}}S_s,\qquad
 \Phi_{s,t}(q)={t\over\hbar}\{W_4(q-se_0)-W_4(q)\}.               \tag{5.2}
\]

Choose `eta in C_c^infinity(R^8)`, normalized, and

\[
 \psi_R(q)=R^{-2}\eta\!\left({q-Re_0\over R^{1/2}}\right).       \tag{5.3}
\]

Then `||p_0 psi_R||=O(R^(-1/2))`, while for
`chi_R=M_(Phi)^*psi_R` the induced momentum center is

\[
 k_R=-t\{\partial_0W_4((R-s)e_0)-\partial_0W_4(Re_0)\}
     =3tGsR^2+O(R),                                                \tag{5.4}
\]

and

\[
 \|(p_0-k_R)\chi_R\|=O(R^{3/2})=o(|k_R|).                        \tag{5.5}
\]

The resolvent identity therefore sends one packet asymptotically to
`(i mu)^(-1)` and the other to zero.  The Cayley-transform formula supplies
the matching upper bound.  For every nonzero `s,t`,

\[
 \|S_sA_tS_s^*-A_t\|={1\over|\mu|}.                              \tag{5.6}
\]

Every element of the finite-dimensional field/resolvent algebra has a
norm-continuous Weyl-conjugation orbit on finite-dimensional phase-space
subspaces; see Georgescu--Iftimovici, Proposition 2.38(2),
[arXiv:1902.10026](https://arxiv.org/abs/1902.10026).  Equation (5.6) thus
implies

\[
 U_tR_\mu U_t^*\notin{\cal R}(\mathbb R^{16},\sigma),
 \qquad t\ne0.                                                     \tag{5.7}
\]

The finite-dimensional resolvent algebra is unital, so its multiplier strict
topology is its norm topology.  Strict continuity cannot repair this kick
route.  The result blocks only a Trotter construction requiring the pure
quartic and kinetic subflows separately to be internal automorphisms of the
full resolvent algebra.  It does not imply (or deny) invariance under the
unsplit kinetic-plus-quartic flow.

## 6. Exact finite-Gibbs character relative entropy

Let `rho=Z^(-1)e^(-beta H)` be one exact finite-volume Q3LOCK Gibbs density and

\[
 A=W_\xi=e^{i\xi\cdot q}.                                         \tag{6.1}
\]

The exact momentum shift is

\[
 A^*HA-H={\hbar\over\chi}\xi\cdot p
          +{\hbar^2\over2\chi}\|\xi\|^2.                        \tag{6.2}
\]

The real Q3 Hamiltonian is time-reversal invariant, so `phi(p)=0`.  Unitary
covariance of logarithms gives both orientations

\[
 S(A\rho A^*\Vert\rho)
 =S(A^*\rho A\Vert\rho)
 ={\beta\hbar^2\over2\chi}\|\xi\|^2=:S_\xi.                    \tag{6.3}
\]

Because `rho` is invariant, the same formula holds for `A_t=alpha_t(A)`.

For any coordinate-tail projection `E`, put

\[
 p=\operatorname{Tr}(\rho E),\qquad
 q_+(t)=\operatorname{Tr}(A_t\rho A_t^*E),\qquad
 q_-(t)=\operatorname{Tr}(A_t^*\rho A_tE).                        \tag{6.4}
\]

Binary data processing and the elementary entropy bound give

\[
 S_\xi\ge d_{\rm bin}(q_\pm(t)\Vert p)
 \ge q_\pm(t)\log(1/p)-\log2.                                   \tag{6.5}
\]

Hence

\[
 q_\pm(t)\le\min\left\{1,{S_\xi+\log2\over\log(1/p)}\right\}. \tag{6.6}
\]

If the exact coordinate-tail theorem gives

\[
 p\le M_a|S|e^{-aL^2},\qquad aL^2>\log(M_a|S|),                   \tag{6.7}
\]

then

\[
 q_\pm(t)\le\min\left\{1,
 {S_\xi+\log2\over aL^2-\log(M_a|S|)}\right\}.                  \tag{6.8}
\]

This is a genuine finite-Gibbs, two-orientation, evolved-character theorem.
Its decay is inverse logarithmic, namely `O(L^(-2))` under (6.7), not
Gaussian.

## 7. Why entropy plus finite moments does not give a Gaussian history tail

For `n>=2` and any fixed integer `m>=3` on `C^2`, let

\[
 q_n=nP_1,\qquad H_n={n^4\over\beta}P_1,\qquad
 \rho_n={\operatorname{diag}(1,e^{-n^4})\over1+e^{-n^4}}.         \tag{7.1}
\]

Write `Delta_n=p_(0,n)-p_(1,n)=tanh(n^4/2)` and choose

\[
 \sin^2\theta_{n,m}={1\over\Delta_n n^{2m}},\qquad
 U_{n,m}^\pm=e^{\mp i\theta_{n,m}\sigma_y},\qquad
 \rho_{n,m}^\pm=U_{n,m}^\pm\rho_nU_{n,m}^{\pm*}.                 \tag{7.2}
\]

Direct two-by-two arithmetic gives, for both signs,

\[
 \operatorname{Tr}(\rho_{n,m}^\pm P_1)=p_{1,n}+n^{-2m},           \tag{7.3}
\]

\[
 S(\rho_{n,m}^\pm\Vert\rho_n)=n^{4-2m},\qquad
 \operatorname{Tr}(\rho_{n,m}^\pm H_n)-\operatorname{Tr}(\rho_nH_n)
 ={n^{4-2m}\over\beta},                                          \tag{7.4}
\]

\[
 \operatorname{Tr}(\rho_{n,m}^\pm q_n^r)
 =n^rp_{1,n}+n^{r-2m},\qquad 0<r\le2m,                           \tag{7.5}
\]

which is uniformly bounded in `n` for each fixed `m`.  The Gibbs reference
has every Gaussian coefficient:

\[
 \operatorname{Tr}(\rho_ne^{a q_n^2})
 \le1+e^{a^2/4},\qquad a>0.                                     \tag{7.6}
\]

For any fixed `T>0`, the two rotations are exact time-`T` flows of the
auxiliary bounded drives

\[
 K_{n,m}^\pm=\pm{\hbar\theta_{n,m}\over T}\sigma_y.            \tag{7.7}
\]

At `m=4`, equations (7.3)--(7.5) are the exact `n^(-8)` tail,
`n^(-4)` relative entropy, `1/(beta n^4)` energy excess, and uniform
eighth-moment fixture, with
`Tr(rho_(n,4)^+/- q_n^8)=1+n^8p_(1,n)<=1+4exp(-2)`. More
generally, for any preregistered finite moment
ceiling, choose fixed `m` above it.  A genuine Gibbs reference,
all-coefficient Gaussian reference tails, vanishing relative entropy and
energy excess, both orientations, and the corresponding uniform finite
tilted moments still allow only a polynomial tail.  This rejects the
inference from entropy plus an arbitrary fixed finite list of moments to a
dynamic Gaussian history tail.  The auxiliary drive is not the equilibrium
flow of `H_n`; the fixture tests only that inference.  It does not reject
the existence of stronger Q3LOCK character-orbit quasi-invariance estimates.

## 8. The remaining two-orientation history gate

For the coordinate cutoff, the existing safe bounded-interaction corridor is

\[
 B_{R,L}(T)=8\sqrt2|X|\|A\|
 e^{\nu_LT}{(\nu_LT)^R\over R!},\qquad
 \nu_L\le{96cL^2\over\hbar}.                                    \tag{8.1}
\]

Taking `L=R^alpha` makes (8.1) vanish on compact time intervals whenever
`0<alpha<1/2`.  But (8.1) pays `e^(C L^2)`.  The polynomial bounds (6.8) and
(7.3) cannot absorb that loss.

For the exact commuting bond kick the cutoff difference satisfies

\[
 D_\delta=ED_\delta E,\qquad
 \|D_\delta\|_{\#,\psi}^2\le8\psi(E),\qquad
 D_\delta^*D_\delta\le{\delta^2\over\hbar^2}(V-V_L)^2.           \tag{8.2}
\]

A Trotter telescope nevertheless requires uniform estimates for every
partial history `P` and its adjoint history:

\[
 \phi_0(P^*EP)+\phi_0(PEP^*),                                    \tag{8.3}
\]

and the corresponding `(V-V_L)^2`-weighted expressions.  Static Gaussian
tails, fixed finite-Gibbs entropy, finite moments, and one-step energy control
do not prove (8.3).  The next dynamics gate is therefore the explicit
two-orientation history/all-exhaustion theorem, or a state-weighted all-bond
resummation that avoids the exponential corridor loss.

## 9. Ordered ground states do not imply a GNS gap

Let

\[
 {\cal K}_0=\mathbb C\Omega\oplus L^2((0,1),dx),                  \tag{9.1}
\]

let `h_0 Omega=0` and `(h_0f)(x)=xf(x)`, and define

\[
 {\cal A}=B({\cal K}_0)\oplus B({\cal K}_0),\qquad
 \alpha_t=\operatorname{Ad}(e^{ith_0/\hbar})
            \oplus\operatorname{Ad}(e^{ith_0/\hbar}).            \tag{9.2}
\]

Here `h_0` is bounded with norm one, so (9.2) is a point-norm `C0`
C-star dynamics.

The component vector states

\[
 \omega_+(A\oplus B)=\langle\Omega,A\Omega\rangle,\qquad
 \omega_-(A\oplus B)=\langle\Omega,B\Omega\rangle               \tag{9.3}
\]

are pure, disjoint, exact ground states.  Summand-swap parity exchanges them,
and the central bounded order observable `Z=(1,-1)` separates them exactly.
In either GNS representation the ground vector is simple, but

\[
 \sigma(h_0)=\{0\}\cup[0,1],\qquad
 \inf(\sigma(h_0)\setminus\{0\})=0.                              \tag{9.4}
\]

Thus even purity, disjointness, parity breaking, a simple ground vector, and
a fixed nonzero order witness do not imply a positive GNS spectral gap.

With the repository convention `delta=(i/hbar)[H,.]`, an actual positive gap
requires an independent coercive estimate of the form

\[
 -i\hbar\,\omega(A^*\delta(A))
 \ge\Delta\{\omega(A^*A)-|\omega(A)|^2\}                          \tag{9.5}
\]

on a dense invariant core in each selected broken-sector GNS
representation.  Neither the v1.6 distinct algebraic ground states nor the
finite-volume doublet energy estimate proves (9.5).

## 10. Gate split and exact status

R-167 v1.7 closes only

- `PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-LOCAL-STRICT-ENERGY-SUBFLOW-CARRIER`,
- `PA-CP1-ST8-Q3LOCK-FIXED-GIBBS-CHARACTER-ENTROPY-TILTED-TAIL-BOUND`.

It splits the previous combined successor into

- `PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`,
- `PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`.

The first requires compatible exhaustion-level energy/state seminorms,
uniform two-orientation partial-history tails or a better resummation,
continuous-time group completion, a noncollapsing spatial algebra, and phase
KMS quotient identification.  The second requires (9.5) after the broken
ground representations themselves have been identified on that algebra.
Neither gate implies the other.

## 11. Registered negative results

This checkpoint registers exactly:

1. `NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-QUARTIC-POINT-NORM-C0`;
2. `NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-RESOLVENT-ALGEBRA-INVARIANCE`;
3. `NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-GAUSSIAN-TAIL-INFERENCE`;
4. `NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP`.

The first is a norm-topology no-go, not a dynamics nonexistence theorem.  The
second concerns the pure potential subflow, not the unsplit flow.  The third
rejects one tail inference, not stronger quasi-invariance.  The fourth
separates ordered-ground existence from spectral coercivity.

## 12. Devil's-advocate review

1. **Objection:** a strict topology on the full resolvent algebra could repair
   the norm discontinuity.  **DISMISSED.**  The finite-dimensional resolvent
   algebra is unital, so its multiplier strict topology equals norm.  The
   local `B(H_X)=M(K(H_X))` strict carrier is a different bounded local net.
2. **Objection:** pure-kick non-invariance proves the unsplit quartic flow does
   not preserve the resolvent algebra.  **UPHELD as an overreach.**  No such
   inference is made; unsplit invariance remains open.
3. **Objection:** the packet argument only tests a formal derivative.
   **DISMISSED.**  The `K^(3/2)` graph endpoint controls the second-order vector
   remainder at the exact shrinking time `t_R=tau R^(-3)`.
4. **Objection:** entropy data processing gives the Gaussian tail needed for
   the corridor.  **DISMISSED.**  It gives (6.8), only `O(L^(-2))`; the exact
   Gibbs fixture shows why finite tilted moments do not upgrade it.
5. **Objection:** two distinct exact ground states should have a positive
   sector gap.  **DISMISSED.**  Section 9 retains purity, disjointness, parity,
   a simple ground vector, and a fixed order witness while the positive
   spectrum still accumulates at zero.
6. **Objection:** the finite-region local-strict theorem already defines the
   thermodynamic dynamics.  **UPHELD as an overreach.**  Growing support and
   the missing two-orientation history estimate remain explicit open gates.

## 13. No-overclaim boundary and checkpoint workflow

This is a `T0`, claim-nonbearing route split.  It proves no all-exhaustion
thermodynamic dynamics, no quasi-local raw oscillator common alpha, no
finite-Hamiltonian-to-phase KMS quotient identification, no positive
broken-sector GNS or physical mass gap, no regulator removal, no continuum,
no physical-empty comparison or below-empty sign, and no C6, CP1, Sector-A,
or Pre-A closure.

Per the PDF-efficiency protocol, development uses this certificate, its
manifest, append-only exploration record, and the primary/independent/
integrated JSON runs.  No per-lemma or intermediate PDF is issued.  Exactly
one gate-level synthesis source/PDF pair is built and visually reviewed only
after those proof layers pass.
