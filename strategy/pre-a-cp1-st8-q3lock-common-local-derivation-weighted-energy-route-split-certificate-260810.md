# Common local derivation and weighted-energy route split

**Result:** `PA-CP1-ST8-Q3LOCK-COMMON-LOCAL-DERIVATION-SOURCE-UNIFORM-WEIGHTED-FIRST-ENERGY-CONE-AND-FOURIER-CUTOFF-ROUTE-SPLIT`  
**Task:** T-054  
**Date:** 2026-08-10  
**Tier:** T0, claim-nonbearing

## 1. Result first

The common-dynamics step in `EXP-000790` advances, but does not close.

1. The exact ST8/Q3LOCK finite-volume Hamiltonians induce one local
   polynomial CCR derivation before either sign phase is selected.
2. A sharp source-uniform coercive shift gives a positive local-energy
   decomposition and an exact continuity equation.
3. Its current obeys a volume-, phase- and source-uniform quadratic-form
   bound.  In three dimensions this proves an exponential first weighted
   local-energy cone.
4. The most direct bounded-Weyl cutoff route cannot be uniform: every cutoff
   agreeing with the quartic on a radius-`R` ball has global Fourier second
   moment at least `3(g+3 lambda)R^2`.

The missing theorem is now smaller and explicit: propagate higher weighted
energy moments and prove a thermodynamic Cauchy estimate on one declared
regular algebra.  Only then may the local derivation be exponentiated to a
common real-time automorphism and compared with the two phasewise KMS
reconstructions.  No Pre-A or C6 status changes.

## 2. Exact fixed-lattice model

At every coarse site `x`, let `q_x,p_x in R8`, with canonical commutators.
Write

\[
 W_4(q)={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{\substack{e\sim f\\ e,f\in Q_3}}
 (q_e-q_f)^2(q_e^2+q_f^2),                            \tag{2.1}
\]

where `g>0`, `lambda>=0`, `c>0`, and `chi>0`.  With
`u=8^{-1/2}(1,...,1)` and `|h|<=h_0`,

\[
 H_{\Lambda}(h)=\sum_{x\in\Lambda}
 \left[{|p_x|^2\over2\chi}+{r\over2}|q_x|^2+W_4(q_x)
 -h\,u\!\cdot q_x\right]
 +{c\over2}\sum_{\langle xy\rangle}|q_x-q_y|^2.     \tag{2.2}
\]

The Q3 term is nonnegative and the power-mean inequality gives

\[
 W_4(q)\ge {g\over4}\sum_e q_e^4
 \ge {g\over32}|q|^4.                                \tag{2.3}
\]

## 3. One common local derivation

Let `P_loc` be the finite-support polynomial CCR star-algebra.  If `A` is
supported in `X`, then

\[
 \delta_h(A)={i\over\hbar}[H_\Lambda(h),A]            \tag{3.1}
\]

is independent of `Lambda` once `Lambda` contains `X` and its nearest
neighbours.  Finite range removes every exterior term from the commutator.
On generators,

\[
 \delta_h(q_x)={p_x\over\chi},\qquad
 \delta_h(p_x)=-r q_x-\nabla W_4(q_x)
 -c\sum_{y\sim x}(q_x-q_y)+h u.                       \tag{3.2}
\]

Thus `delta_0` is fixed before selecting the `+` or `-` phase.  This is a
common local star-derivation, not yet its thermodynamic-limit exponentiation
on a C-star algebra.

## 4. Sharp source-uniform coercivity

Fix `0<gamma<g/32`, put `a_gamma=g/32-gamma`, and define the finite constant

\[
 C_\gamma(r,h_0)=\max_{\rho\ge0}
 \left[h_0\rho-{r\over2}\rho^2-a_\gamma\rho^4\right]. \tag{4.1}
\]

Since `|u dot q|<=|q|`, equations (2.3)--(4.1) imply

\[
 K_{\Lambda,h}:=H_\Lambda(h)+C_\gamma|\Lambda|
 \ge\sum_x\left[{|p_x|^2\over2\chi}+\gamma|q_x|^4\right]
 +{c\over2}\sum_{\langle xy\rangle}|q_x-q_y|^2.     \tag{4.2}
\]

The bound is uniform in `Lambda` and `|h|<=h_0`.  Scalar Young inequalities
then yield, for every `epsilon>0`,

\[
 \sum_{x\in X}|q_x|^2\le\epsilon K_{\Lambda,h}
 +{|X|\over4\epsilon\gamma},                         \tag{4.3}
\]

\[
 \pm q_x\!\cdot q_y\le\epsilon K_{\Lambda,h}
 +{1\over8\epsilon\gamma},\qquad
 \pm c q_x\!\cdot q_y\le\epsilon K_{\Lambda,h}
 +{c^2\over8\epsilon\gamma}.                        \tag{4.4}
\]

Moreover `(q_x dot q_y)^2<=K/(2 gamma)`, so

\[
 \|(q_x\!\cdot q_y)(1+K_{\Lambda,h})^{-1/2}\|
 \le(2\gamma)^{-1/2}.                                \tag{4.5}
\]

## 5. Exact local-energy current

Define

\[
 e_x={|p_x|^2\over2\chi}+{r\over2}|q_x|^2+W_4(q_x)
 -h u\!\cdot q_x+C_\gamma
 +{c\over4}\sum_{y\sim x}|q_x-q_y|^2.               \tag{5.1}
\]

Then `e_x>=0` as a quadratic form and `sum_x e_x=K`.  On the common
Schwartz/form core, direct commutator cancellation of the onsite force gives

\[
 {d e_x\over dt}=-\sum_{y\sim x}J_{xy},\qquad
 J_{xy}={c\over4\chi}\{p_x+p_y,q_x-q_y\},
 \quad J_{yx}=-J_{xy}.                                \tag{5.2}
\]

Here the total bond momentum commutes with the relative bond position.
Because

\[
 |p_x+p_y|^2\le4\chi(e_x+e_y),\qquad
 |q_x-q_y|^2\le {2\over c}(e_x+e_y),                 \tag{5.3}
\]

the simultaneous kinetic--bond quadratic form and the optimized Young
inequality prove the sharp bound

\[
 \pm J_{xy}\le\sqrt{{c\over2\chi}}(e_x+e_y)         \tag{5.4}
\]

## 6. First weighted local-energy cone

Let `E_f=sum_x f_x e_x`, with positive weights satisfying
`exp(-mu)<=f_x/f_y<=exp(mu)` on every adjacent pair.  From (5.2),

\[
 \delta_h(E_f)=-\sum_{\langle xy\rangle}(f_x-f_y)J_{xy}. \tag{6.1}
\]

Equation (5.4), the adjacent-ratio bound, and degree six of `Z^3` give

\[
 \pm\delta_h(E_f)\le
 6\sqrt{{c\over2\chi}}(e^\mu-1)E_f.                 \tag{6.2}
\]

Finite-volume form-domain Gronwall therefore yields

\[
 \tau_t^\Lambda(E_f)\le
 \exp\!\left[6\sqrt{{c\over2\chi}}(e^\mu-1)|t|\right]E_f. \tag{6.3}
\]

This is the first genuinely phase-independent, source-uniform propagation
estimate for the exact quartic model in this route.  It controls one local
energy moment.  It does not by itself control the cubic force in all nested
commutators or make the finite-volume automorphisms Cauchy.

## 7. Exact obstruction to the simplest cutoff import

Suppose a smooth cutoff has Fourier--Stieltjes form

\[
 V_R(q)=\int e^{ik\cdot q}\,\mu_R(dk),\qquad
 \kappa_R=\int|k|^2|\mu_R|(dk),                       \tag{7.1}
\]

and equals `W4` on `|q|<=R`.  Differentiating under the integral gives

\[
 \sup_{q,|v|=1}|v^TD^2V_R(q)v|\le\kappa_R.           \tag{7.2}
\]

Along a Q3 coordinate ray, exactly three Q3 edges meet the occupied vertex,
so

\[
 W_4(t e)={g+3\lambda\over4}t^4,\qquad
 {d^2\over dt^2}W_4(t e)=3(g+3\lambda)t^2.           \tag{7.3}
\]

Taking `t` to `R` from below proves

\[
 \kappa_R\ge3(g+3\lambda)R^2.                        \tag{7.4}
\]

The Lieb--Robinson exponent in Nachtergaele et al., arXiv:0909.2249,
Theorem 4.2 depends linearly on this global second moment.  Hence that theorem
cannot supply an `R`-uniform operator-norm speed for cutoffs agreeing with the
quartic on expanding balls.  This is a route obstruction only.  It is not a
nonexistence theorem for common dynamics or energy-weighted locality.

There is a second, independent warning against an unweighted core.  Put
`L=a dot P+b dot Q`, take `a` nonzero, and fix `z` in the complex plane with
nonzero imaginary part.  The basic resolvent

\[
 R_z=(L-z)^{-1}
\]

is bounded, and the Schwartz-core resolvent identity gives

\[
 [W_4(Q),R_z]=-i\hbar R_z(D_aW_4)(Q)R_z.              \tag{7.5}
\]

Here the operator-norm obstruction is not inferred from the leading
polynomial alone.  Choose a normalized nonzero
`xi in C_c^infty(R^8)` whose configuration support lies in a ball of radius
`r_0`.  Let `U_s` be the Weyl unitary satisfying

\[
 U_s^*QU_s=Q+s a,\qquad U_s^*PU_s=P-s b,
 \qquad U_s^*LU_s=L.                                  \tag{7.6}
\]

Thus `U_s` commutes with `L` and its resolvents.  Define the two bounded-norm
input families

\[
 \psi_s=U_s(L-z)\xi,\qquad
 \phi_s=U_s(L-\bar z)\xi .                            \tag{7.7}
\]

Their norms are independent of `s`.  Cancelling the two resolvents on the
Schwartz core and conjugating by `U_s` gives the exact matrix-element identity

\[
 \langle\phi_s,R_z(D_aW_4)(Q)R_z\psi_s\rangle
 =\langle\xi,(D_aW_4)(Q+s a)\xi\rangle
 =4W_4(a)s^3+O(s^2),                                  \tag{7.8}
\]

where quartic homogeneity gives `D_aW_4(a)=4W_4(a)` and positivity gives
`W_4(a)>0`.  Dividing (7.8) by the two fixed input norms proves that the exact
sandwich in (7.5) has no bounded extension.

The same test also proves the cutoff statement rather than merely suggesting
it.  If a smooth cutoff `V_R` equals `W_4` on the configuration ball `B_R`,
then for `0 <= s <= (R-r_0)/|a|` the displaced support stays inside `B_R`, so
(7.8) holds with `V_R`.  Taking `s=(R-r_0)/(2|a|)` and then `R` large yields

\[
 \|R_z(D_aV_R)(Q)R_z\|\ge c_{\xi,z,a}R^3.             \tag{7.9}
\]

Consequently the corresponding basic-resolvent commutator norms grow at
least cubically.  This rules out that standard **unweighted** generator-core
estimate.  It does not rule out finite-time resolvent-algebra invariance by
another proof or an energy-damped core.

## 8. Exact remaining gate

The next sufficient target is: for a predeclared dense local
resolvent/regular core `A_0`, prove some finite `s` and all required energy
moments satisfy uniform propagation together with

\[
 \|(1+E_{\mu,X})^{-s}
 [\tau_t^{\Lambda'}(A)-\tau_t^\Lambda(A)]
 (1+E_{\mu,X})^{-s}\|
 \le C_{A,T}e^{-\mu(d(X,\Lambda^c)-vT)}.              \tag{8.1}
\]

The constants must be uniform in the larger volume, source compact and any
auxiliary cutoff.  This would close the energy-weighted thermodynamic Cauchy
step and permit a common automorphism construction.  A fixed local `A` and
compact time interval for which every finite energy weight fails to make the
volume net Cauchy is the minimal falsifier.

## 9. Prior-art boundary

The closest imported quantum results do not directly cover the exact model.
Nachtergaele et al. (arXiv:0909.2249) use bounded Weyl-integral perturbations;
Buchholz (arXiv:1605.05259) treats bounded `C_0` interactions in the global
resolvent-algebra theorem; Kanda--Matsui (arXiv:1601.04809) assume Schwartz
onsite and pair potentials; and Amour--Levy-Bruhl--Nourrigat
(arXiv:0904.2717) impose subquadratic/Fourier-derivative conditions.
Butta--Marchioro (arXiv:1602.01294) support the local-energy route for the
classical quartic-plus-harmonic crystal only.  None is imported as a quantum
common-alpha closure.

## 10. Adversarial review and no-overclaim boundary

1. **Could the factor in the current be wrong?**  No.  Each bond contributes
   half its energy to each endpoint.  The total bond momentum commutes with
   the relative coordinate, giving exactly `c/(4 chi)` times the
   anticommutator.
2. **Does first-moment propagation exponentiate `delta_0`?**  No.  Cubic
   onsite forces require higher graph norms and a spatial Cauchy theorem.
3. **Does divergence of `kappa_R` refute exact dynamics?**  No.  It refutes
   only one uniform operator-norm cutoff import.
4. **Are phasewise KMS systems now known to use one alpha?**  No.  That
   identification remains downstream of (8.1).

This package proves no algebraic ground state, GNS or physical mass gap,
continuum limit, physical empty-space comparison, light, mass, time, gravity,
event horizon, C6, CP1, Sector-A or Pre-A completion.
