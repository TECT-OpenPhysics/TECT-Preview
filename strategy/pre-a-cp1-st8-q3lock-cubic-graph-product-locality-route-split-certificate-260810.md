# ST8/Q3LOCK weighted cubic graph embedding and product-locality route split

**Result:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT` v1.1 (`R-167`)  
**Exploration:** `EXP-000796`  
**Task:** T-054  
**Date:** 2026-08-10  
**Tier:** T0, claim-nonbearing

## 1. Result first

This extension closes the cubic graph obligation left open by `EXP-000795`,
but it does not close common real-time dynamics.

1. The exact Schrödinger cross identity used in R-167 also controls the
   multiplication part `U_f` by the full weighted energy `A`. Heinz--Kato
   graph interpolation then proves the formerly missing one-sided bound
   `f_x^(3/4)|q_x|^3A^(-3/4)`, its adjoint orientation, and the Q3 cubic-force
   multiplier. The spatial factor is sharp: a moving-site unweighted bound
   must grow at least as `f_x^(-3/4)`.
2. Every prescribed bond word has an exact heat-simplex bound with
   `Gamma(1+n/2)` denominator. This is a genuine analytic input, not yet a
   connected-cluster theorem.
3. Two direct absolute-value continuations fail exactly. A single lattice
   animal has factorially many connected growth orders, giving a zero-radius
   raw-history majorant. Even after a hypothetical reduction to edge chains,
   absolute continuation to `epsilon+it` produces `exp(C/epsilon)`, which no
   finite Balakrishnan energy power can integrate.
4. The remaining phase-independent target is one first-passage theorem which
   sums all branches and repeated edges sharing a backbone before taking
   norms. Its exact sufficient coefficient and the resulting velocity are
   stated below.
5. A separate equilibrium route has a viable cutoff exponent balance if one
   first proves a uniform fifth local onsite-energy moment. That moment alone
   is not enough in a nontracial GNS topology: a two-sided modular/dual-state
   tail theorem is also required. An exact rank-shift fixture shows why the
   Kubo--Mori/Duhamel inner product alone cannot supply strong-star dynamics.

Thus the original order remains compulsory:

`phasewise OS/KMS -> common dynamics -> distinct ground states -> GNS gap ->
continuum/counterterms -> physical-empty comparison`.

## 2. Model and inherited inputs

On a finite `Lambda subset Z^3`, with `q_x,p_x in R^8`, use the exact
ST8/Q3LOCK Hamiltonian and the positive shifted local-energy decomposition of
`EXP-000792`. For a finite center `X`, set

\[
 f_x=e^{-\mu d(x,X)},\qquad
 A=1+E_f=1+T_f+U_f,\qquad
 U_f\ge\gamma f_x|q_x|^4,                                    \tag{2.1}
\]

where `0<gamma<g/32`, `z=6`, and

\[
 S_f:=\sum_xf_x\le |X|
 \left({1+e^{-\mu}\over1-e^{-\mu}}\right)^3.                \tag{2.2}
\]

The R-167 Laplacian estimate is

\[
 L_f:=\sum_xf_x\Delta_xU_f
 \le C_2\varepsilon U_f+S_f
 \left(8r_++8cz+{C_2\over4\varepsilon\gamma}\right),
 \qquad C_2=3g+21\lambda.                                    \tag{2.3}
\]

All operator statements below are first proved on the finite-volume
`C_c^infinity`/Schwartz core. The polynomial confining Schrödinger operator
has that core as an operator core, so the estimates pass to the closed
operators. Constants are uniform in the finite volume, `|h|<=h0`, and the
location of a center `X` of bounded cardinality.

## 3. Exact weighted cubic graph theorem

For `psi` in the common core, the exact cross identity gives

\[
\begin{aligned}
 \|A\psi\|^2={}&\|T_f\psi\|^2+\|U_f\psi\|^2+\|\psi\|^2
 +2\langle T_f\rangle_\psi+2\langle U_f\rangle_\psi\\
 &+{D_f\over\chi}-{\hbar^2\over2\chi}\langle L_f\rangle_\psi,
                                                                    \tag{3.1}
\end{aligned}
\]

with `D_f,T_f,U_f>=0`. Choose

\[
 \varepsilon_*={4\chi\over\hbar^2C_2},                         \tag{3.2}
\]

\[
 b_*:=S_f\left(8r_++8cz+{\hbar^2C_2^2\over16\chi\gamma}\right),
 \qquad
 \beta_*:={\hbar^2b_*\over2\chi}.                             \tag{3.3}
\]

The `U_f` term contributed by (2.3) then cancels exactly against
`2<U_f>`. Equation (3.1) implies

\[
 \|U_f\psi\|^2
 \le \|A\psi\|^2+(\beta_*-1)_+\|\psi\|^2
 \le\max(1,\beta_*)\|A\psi\|^2.                              \tag{3.4}
\]

Consequently, with

\[
 \kappa:=\sqrt{\max(1,\beta_*)},                              \tag{3.5}
\]

one has

\[
 \boxed{\ \|U_fA^{-1}\|\le\kappa.\ }                       \tag{3.6}
\]

The Heinz--Kato graph interpolation theorem now gives, for `0<=theta<=1`,

\[
 \|U_f^\theta A^{-\theta}\|\le\kappa^\theta.                \tag{3.7}
\]

Since `U_f` and every `q_x` commute as multiplication operators, (2.1) and
(3.7) give, for every `0<=m<=4`,

\[
 \boxed{
 f_x^{m/4}\bigl\||q_x|^mA^{-m/4}\bigr\|
 \le\gamma^{-m/4}\kappa^{m/4}.}                              \tag{3.8}
\]

The adjoint orientation is bounded by the same constant. In particular,

\[
 \boxed{
 f_x^{3/4}\bigl\||q_x|^3A^{-3/4}\bigr\|
 \le\gamma^{-3/4}\max(1,\beta_*)^{3/8}.}                     \tag{3.9}
\]

This proves the weighted graph-domain inclusion which R-167 v1.0 explicitly
left open.

For one Q3 internal edge,

\[
 \partial_a\left[{\lambda\over4}(a-b)^2(a^2+b^2)\right]
 =\lambda\left(a^3-{3\over2}a^2b+ab^2-{1\over2}b^3\right).
                                                                    \tag{3.10}
\]

Every internal vertex has degree three, so

\[
 |\partial_eW_4(q)|\le(g+12\lambda)|q|^3.                    \tag{3.11}
\]

Combining (3.9) and (3.11),

\[
 f_x^{3/4}\|\partial_eW_4(q_x)A^{-3/4}\|
 \le(g+12\lambda)\gamma^{-3/4}\kappa^{3/4}.                 \tag{3.12}
\]

The full eight-component gradient has the same bound multiplied by
`sqrt(8)`.

## 4. Sharp spatial boundary of the graph theorem

The factor `f_x^(3/4)` in (3.9) cannot be deleted uniformly over moving
sites. Fix a normalized compact product bump and translate one coordinate at
site `x` by amplitude `R`. Uniform weight-ratio estimates give constants
`C_0,C_1`, independent of the volume and site, such that

\[
 \|q_{x,e}^3\psi_{x,R}\|\ge(R-1)^3,
 \qquad
 \|A\psi_{x,R}\|\le C_0+C_1f_xR^4.                           \tag{4.1}
\]

Spectral interpolation gives

\[
 \|A^{3/4}\psi\|\le\|A\psi\|^{3/4}\|\psi\|^{1/4}.         \tag{4.2}
\]

Letting `R` tend to infinity shows that every constant in an unweighted
bound `||q_x^3A^(-3/4)||<=C_x` must obey

\[
 C_x\ge C_1^{-3/4}f_x^{-3/4}.                                \tag{4.3}
\]

This proves
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-MOVING-SITE-CUBIC-GRAPH-UNIFORMITY`.
It does not reject recentering the energy at each first-passage step.

That recentering can itself be controlled without appealing only to form
order. Let `A_x,A_y` be centered at neighboring sites and put
`theta=e^mu-1`. The nonnegative multiplication potentials and the commuting
kinetic pieces give

\[
 \|(U_x-U_y)A_y^{-1}\|\le\theta\kappa,
 \qquad
 \|(T_x-T_y)A_y^{-1}\|\le\theta(2+\kappa).                   \tag{4.4}
\]

Thus, in both center orientations,

\[
 \|A_xA_y^{-1}\|\le
 C_\mu:=1+2(e^\mu-1)(1+\kappa).                              \tag{4.5}
\]

Heinz--Kato now gives the genuine one-sided graph comparison

\[
 \boxed{\ \|A_x^sA_y^{-s}\|\le C_\mu^s,\qquad0\le s\le1.\ } \tag{4.6}
\]

The reverse orientation obeys the same bound. A fixed exponent therefore
pays only `C_mu^(sn)` along an `n`-step recentered backbone, rather than the
quadratic-in-`n` loss caused by an increasing half-energy ladder.

## 5. Exact prescribed-word heat-simplex lemma

Let `K>=1` be positive self-adjoint. Suppose every self-adjoint bond
interaction satisfies both

\[
 \|V_eK^{-1/2}\|,\ \|K^{-1/2}V_e\|\le b.                    \tag{5.1}
\]

For `s_j>=0` and `sum_(j=0)^n s_j=beta`, group each bond with the heat factor
on its left and use

\[
 \|K^{1/2}e^{-sK}\|\le(2es)^{-1/2}.                          \tag{5.2}
\]

This yields, almost everywhere on the simplex,

\[
 \|e^{-s_0K}V_{e_n}e^{-s_1K}\cdots V_{e_1}e^{-s_nK}\|
 \le b^n(2e)^{-n/2}\prod_{j=0}^{n-1}s_j^{-1/2}.              \tag{5.3}
\]

The Dirichlet integral is exact:

\[
 \int_{\sum s_j=\beta}\prod_{j=0}^{n-1}s_j^{-1/2}\,ds
 ={\pi^{n/2}\beta^{n/2}\over\Gamma(1+n/2)}.                 \tag{5.4}
\]

Hence every prescribed word obeys

\[
 \boxed{
 \|\mathcal I_{{\bf e},n}(\beta)\|
 \le{[b\sqrt{\pi/(2e)}\sqrt\beta]^n\over\Gamma(1+n/2)}.}  \tag{5.5}
\]

In Q3LOCK,

\[
 V_{xy}=-c q_x\!\cdot q_y,
 \qquad
 (q_x\!\cdot q_y)^2\le {|q_x|^4+|q_y|^4\over2}
 \le {K\over2\gamma},                                      \tag{5.6}
\]

so `b=c/sqrt(2gamma)`. Summing the two left/right commutator branches replaces
the activity by

\[
 \kappa_0=c\sqrt{\pi\over e\gamma}.                          \tag{5.7}
\]

Equations (5.5)--(5.7) are a positive theorem for a prescribed word only.

## 6. Raw connected-history animal majorant has zero radius

Build a length-`m` backbone along one lattice axis. At `m` selected backbone
vertices attach four distinct transverse leaves. The animal has `n=5m`
edges. After the backbone is grown in order, the `4m` leaves may be appended
in any order while every prefix stays connected. Thus this one animal has at
least `(4m)!` legal histories.

If each raw history is bounded separately by the positive activity from
(5.5), this animal alone contributes the majorant

\[
 M_m={(4m)!a^{5m}\over\Gamma(1+5m/2)}.                        \tag{6.1}
\]

Stirling's formula gives

\[
 \log M_m={3\over2}m\log m+O(m),                              \tag{6.2}
\]

so the terms fail to tend to zero for every `a>0`. This proves
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-ABSOLUTE-CONNECTED-HISTORY-ANIMAL-MAJORANT`.
The conclusion concerns the termwise-absolute proof method; cancellations
inside a unitary cluster propagator remain available.

## 7. Chain reduction does not repair absolute strip continuation

Suppose, more favorably, that an exact first-passage reorganization has
already reduced the combinatorics to edge chains. In degree `z=6`, use

\[
 P=2z-1=11.                                                   \tag{7.1}
\]

The Mittag--Leffler identity

\[
 E_{1/2}(x)=\sum_{n\ge0}{x^n\over\Gamma(1+n/2)}
 =e^{x^2}\operatorname{erfc}(-x)\le2e^{x^2}                 \tag{7.2}
\]

closes the positive-heat chain sum. At complex time
`zeta=epsilon+it/hbar`, however, (5.5) contains
`kappa_0|zeta|/sqrt(epsilon)`. A spatially tilted chain bound therefore has

\[
 2\exp\left[-\rho d+
 P^2\kappa_0^2e^{2\rho}{|\zeta|^2\over\varepsilon}\right]. \tag{7.3}
\]

For `t!=0`, a Balakrishnan energy power would require

\[
 \int_0^1\varepsilon^{s-1}e^{C/\varepsilon}\,d\varepsilon,
                                                                    \tag{7.4}
\]

which diverges for every finite `s`. This proves
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-ABSOLUTE-HEAT-STRIP-REAL-TIME-CONTINUATION`.
It is not a statement that the oscillatory real-time boundary value diverges.

## 8. The surviving first-passage real-time theorem

For `j=1,2`, put `s_1=1/2` and `s_2=3/4`. Let
`R_(pi,n)^(j)` denote the sum of every branch and repeated-edge history whose
first-passage backbone is the same path `pi`. The remaining load-bearing
hypothesis is the two-sided product estimate

\[
 \int_{\Delta_n(t)}\left(
 \|\mathscr R_{\pi,n}^{(j)}A^{-s_j}\|
 +\|A^{-s_j}\mathscr R_{\pi,n}^{(j)}\|\right)d{\bf t}
 \le C_j{[G_j\sqrt{|t|/\hbar}]^n\over\Gamma(1+n/2)}.          \tag{8.1}
\]

This is imposed after, not before, the branch/repeat resummation. Counting
chains and inserting an exponential spatial tilt gives

\[
 \mathcal C_j(d,t)\le {2C_jz|X|\over P}
 \exp\left[-\rho d+{P^2G_j^2e^{2\rho}\over\hbar}|t|\right]. \tag{8.2}
\]

Thus the velocity is

\[
 v_{\rho,j}={P^2G_j^2e^{2\rho}\over\rho\hbar}.              \tag{8.3}
\]

If `rho>mu/4`, (8.2) supplies the two spatial commutator hypotheses of the
R-167 conditional Duhamel theorem. Exhaustion independence, strong-star core
limits, adjoints, products, the group law, inverse and strong time continuity
then follow under its declared common-core assumptions.

The centered graph estimate (3.9) and (4.6) control ordered center changes by
replacing `G_j` with `C_mu^(s_j)G_j`. All branch/repeat resummations remain
obligations of (8.1), not consequences of the heat lemma. The new gate is
`PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-PRODUCT-AND-ENERGY-TAIL-CLOSURE`.

## 9. Equilibrium cutoff alternative and its topology boundary

There is a separate fixed-temperature route. Split

\[
 H_\Lambda(h)+C|\Lambda|=\sum_xk_{x,h}
 +\sum_{\langle xy\rangle}V_{xy},
 \qquad k_{x,h}\ge1+\gamma|q_x|^4.                           \tag{9.1}
\]

For `P_(x,R)=1_[k_(x,h)<=R]`,

\[
 \|q_xP_{x,R}\|\le\gamma^{-1/4}R^{1/4},
 \qquad
 \|V_{xy}P_{x,R}P_{y,R}\|=O(R^{1/2}).                       \tag{9.2}
\]

Assume, but do not yet claim for Q3LOCK, a uniform local moment

\[
 \sup_{\Lambda,|h|\le h_0,x}
 \varphi_{\Lambda,h}(k_{x,h}^{,p})\le M_p,
 \qquad p>d+1.                                                \tag{9.3}
\]

If an independently proved two-sided cutoff/Duhamel estimate has the form

\[
 C_{A,T}\left[m^dR_m^{(1-p)/2}
 +m^dR_m^{1/2}{(CTR_m^{1/2})^m\over m!}\right],              \tag{9.4}
\]

then `R_m=m^b` with

\[
 {2d\over p-1}<b<2                                           \tag{9.5}
\]

makes both terms vanish. In `d=3`, `p=5` and `b=7/4` give leakage exponent
`-1/2`, while Stirling leaves coefficient `b/2-1=-1/8` in the leading
`m log m` term.

Equations (9.3)--(9.5) are an exact scale balance, not a proof of (9.4).
Static Euclidean position-loop integrability does not by itself prove the
onsite-energy moment including momentum, and a nontracial state does not let
bounded factors move freely through the density matrix. The remaining gate
is
`PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-MODULAR-CUTOFF-LOCALITY`.
It must prove both the fifth energy moment and two-sided/dual-state or modular
tail control on a predeclared faithful phase-pair or separating state class.

The need for this topology input is exact. Let

\[
 He_n=ne_n,\qquad p_n=(1-e^{-\beta})e^{-\beta n},
 \qquad X_n=|e_n\rangle\langle e_0|.                          \tag{9.6}
\]

For the Kubo--Mori/Duhamel inner product,

\[
 (X_n,X_n)_D=(X_n^*,X_n^*)_D
 ={p_0-p_n\over\beta n}\longrightarrow0.                    \tag{9.7}
\]

Nevertheless `X_ne_0=e_n`, and the symmetric GNS square norm tends to
`p_0/2>0`. Thus Duhamel convergence in both adjoint labels does not imply
strong-star convergence, multiplication or an automorphism. This is
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-DUHAMEL-INNER-PRODUCT-ONLY-COMMON-DYNAMICS`.

If all matrix elements have modular bandwidth `|E_m-E_n|<=Omega`, the
arithmetic-mean/logarithmic-mean identity repairs the comparison:

\[
 \|X\|_{\rho,\#}^2
 \le\left[{\beta\Omega\over2}
 \coth\left({\beta\Omega\over2}\right)\right](X,X)_D.       \tag{9.8}
\]

Q3LOCK currently has no uniform bandwidth theorem; a high-modular-energy tail
is the appropriate replacement.

## 10. Adversarial review

1. **Objection: the cubic estimate still follows only from scalar power
   counting.**  
   **DISMISSED.** Equation (3.6) is an operator graph bound obtained from the
   exact cross identity. Heinz--Kato, followed by commuting multiplication
   order inside `U_f`, gives (3.9) on the closed operator domains.
2. **Objection: (3.9) is uniform at every site without a weight.**  
   **UPHELD against that wording.** Equations (4.1)--(4.3) force the optimal
   `f_x^(-3/4)` spatial cost.
3. **Objection: the heat-simplex denominator already proves real-time
   locality.**  
   **UPHELD.** The raw animal in Section 6 and the strip boundary in Section 7
   independently falsify the two corresponding absolute-value promotions.
4. **Objection: those failures prove that exact real-time dynamics does not
   exist.**  
   **DISMISSED.** They reject only termwise-absolute organizations. The
   first-passage response (8.1), unitary cancellation and equilibrium modular
   methods remain open.
5. **Objection: a fifth Gibbs moment alone constructs a common
   automorphism.**  
   **UPHELD.** The moment supplies cutoff leakage arithmetic only after a
   genuinely two-sided nontracial estimate is proved. Equation (9.7) rejects
   Duhamel norm alone.
6. **Objection: a fixed-beta phase-pair W-star result would finish Pre-A.**  
   **UPHELD.** It would still require KMS identification, a beta/ground limit,
   distinct algebraic ground states, a broken-sector GNS gap, continuum and a
   separately registered physical-empty comparison.

## 11. Scope and next order

The weighted cubic graph embedding and prescribed-word heat-simplex lemma are
proved. The four negative results reject only their named uniformity or proof
routes. Neither (8.1), (9.3), nor the nontracial estimate (9.4) is proved.

This result does not construct a phase- or beta-independent common C-star
`alpha`, identify common-alpha KMS states, select algebraic ground states,
prove a GNS or physical mass gap, remove the regulator, take the continuum
limit, define physical empty space, prove a below-empty sign, select a
functional, or prove C6, CP1, Sector A or Pre-A.
