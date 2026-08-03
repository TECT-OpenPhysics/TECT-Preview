# Pre-A CL8 global Goursat-continuation certificate

**Candidate:** `PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0`  
**Internal result:**
`PA-CP1-CL8-FINITE-TRIANGLE-GOURSAT-GLOBAL-EXISTENCE-STABILITY`  
**Parents:** `PA-CP1-CL8-GOURSAT-v0`,
`PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0`  
**Claim context:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Date:** 2026-08-03
**Package version:** `0.1.1` (revised 2026-08-04)

<a id="section-1-verdict"></a>
## 1. Verdict

The CL8 characteristic solution does not need the former one-patch smallness
condition on the whole null triangle.  For the declared signs

\[
 \chi>0,\qquad c>0,\qquad g>0,\qquad \lambda\ge0,
 \qquad r\in\mathbb R,
\]

every compatible `C1` trace pair on every finite triangle `D_tau` has a
unique classical integral solution.  The proof shifts the potential by an
explicit constant, derives a nonnegative exact null-flux ledger, obtains a
uniform amplitude bound by one-dimensional energy coercivity, and then tiles
the triangle with finitely many translated local Volterra patches.  The same
amplitude bound turns the factorial-squared Volterra comparison into a global
Bessel-`I0` stability estimate.  Section 7.1 supplies a theorem-neutral second
proof of the same finite-triangle existence conclusion by a whole-triangle
clipped Bielecki fixed point and a shifted-energy first-exit contradiction.

This closes the manifest-local
`PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE` gate in its declared
classical fixed-background scope.  It covers the inserted `L=pi/2` ordered
PA-H1 circumference even though the old single-patch contraction factor is
larger than one.

It does not select the characteristic traces, a probability measure, or a
quantum state.  It does not derive the Lorentzian cone, a horizon, gravity, or
the physical energy reference.  CP1 and Pre-A remain open.

<a id="section-2-prior-art"></a>
## 2. Prior-art and novelty boundary

Global energy continuation for defocusing semilinear waves, local
characteristic rectangle constructions, one-dimensional Sobolev estimates,
Bielecki-weighted contractions, clipping/first-exit arguments, and
factorial/Bessel bounds for Volterra equations are established mathematics.  The parent certificate already cites characteristic Goursat
analysis, including Gerard and Wrochna, <https://arxiv.org/abs/1409.6691>.
No world-first or new general PDE theorem is claimed.

The repository-specific content is narrower: the exact Q3 eight-species
potential, the `1/8` physical ledger, the sharp additive coercive shift, the
explicit continuation constants, and the repair of the exact PA-H1
calibration gate without changing the model or hiding a state-selection
assumption.

<a id="section-3-model"></a>
## 3. Inherited fixed-background problem

Let

\[
 W(z)=\sum_{e=1}^{8}\left({r\over2}z_e^2+{g\over4}z_e^4\right)
 +{\lambda\over4}\sum_{e\sim f}
 (z_e-z_f)^2(z_e^2+z_f^2),                                      \tag{3.1}
\]

where the last sum is over the twelve undirected edges of `Q3`.  On the
inserted `1+1` Lorentzian background,

\[
 \chi\psi_{tt}-c\psi_{xx}+\nabla W(\psi)=0,
 \qquad s=\sqrt{c/\chi}.                                       \tag{3.2}
\]

With `u=t+x/s`, `v=t-x/s`, equation (3.2) becomes

\[
 4\chi\psi_{uv}+\nabla W(\psi)=0.                              \tag{3.3}
\]

For arbitrary finite `tau>0`, set

\[
 D_\tau=\{u\ge0,\ v\ge0,\ u+v\le2\tau\}.                    \tag{3.4}
\]

The supplied data are

\[
 \psi(u,0)=A(u),\qquad \psi(0,v)=B(v),\qquad A(0)=B(0)=C,      \tag{3.5}
\]

with `A,B in C1([0,2tau];R8)`.  The theorem takes (3.1)--(3.5) as
inputs.  In particular it does not derive the cone or the traces.

<a id="section-4-shift"></a>
## 4. Exact coercive shift

Write

\[
 a=r_-:=\max\{-r,0\},\qquad C_*= {2a^2\over g},\qquad
 \widehat W=W+C_*.                                             \tag{4.1}
\]

For `r<0`, each onsite term satisfies the exact identity

\[
 {r\over2}z^2+{g\over4}z^4+{a^2\over4g}
 ={(gz^2-a)^2\over4g}\ge0.                                   \tag{4.2}
\]

For `r>=0` the unshifted onsite term is already nonnegative.  The Q3
locking polynomial is nonnegative when `lambda>=0`.  Summing (4.2) over eight
species proves

\[
 \widehat W(z)\ge0.                                            \tag{4.3}
\]

A second completed square gives

\[
 {r\over2}z^2+{g\over4}z^4
 \ge {g\over8}z^4-{a^2\over2g}.                               \tag{4.4}
\]

Consequently

\[
 \widehat W(z)\ge {g\over8}\sum_e z_e^4-{2a^2\over g}.        \tag{4.5}
\]

The shift changes no equation because `grad W_hat=grad W`.  It is a proof
normalization, not an observed vacuum energy or a comparison with physical
empty space.

<a id="section-5-flux"></a>
## 5. Nonnegative null-flux ledger

For `0<t<=tau`, define

\[
 \widehat E(t)={1\over8}\int_{-st}^{st}
 \left({\chi\over2}|\psi_t|^2+{c\over2}|\psi_x|^2
 +\widehat W(\psi)\right)dx.                                  \tag{5.1}
\]

The parent current identity is unchanged by a constant potential shift.
Its exact triangle integral is

\[
 \widehat E(t)={s\over8}\int_0^{2t}
 \left(\chi|A'|^2+{\widehat W(A)\over2}\right)du
 +{s\over8}\int_0^{2t}
 \left(\chi|B'|^2+{\widehat W(B)\over2}\right)dv.             \tag{5.2}
\]

The shift is consistent on both sides: the slice receives
`(1/8)(2st)C_*`, while the two null sides together receive
`2(s/8)(2t)(C_*/2)`, the same number.

Set the total available boundary flux

\[
 \mathcal F_\tau={s\over8}\int_0^{2\tau}
 \left(\chi|A'|^2+{\widehat W(A)\over2}\right)du
 +{s\over8}\int_0^{2\tau}
 \left(\chi|B'|^2+{\widehat W(B)\over2}\right)dv.             \tag{5.3}
\]

Equations (4.3) and (5.2) give the uniform finite-time bound

\[
 0\le\widehat E(t)\le\mathcal F_\tau.                         \tag{5.4}
\]

<a id="section-6-amplitude"></a>
## 6. Explicit amplitude bound

Let `I_t=[-st,st]`.  The spatial-gradient part of (5.1) gives

\[
 \|\psi_x(t)\|_{L^2(I_t)}^2
 \le {16\mathcal F_\tau\over c}.                              \tag{6.1}
\]

The right endpoint of the slice lies on the supplied null trace:

\[
 \psi(t,st)=A(2t).                                             \tag{6.2}
\]

For every component and every `x in I_t`, the fundamental theorem of
calculus and Cauchy--Schwarz therefore give

\[
 |\psi_e(t,x)|\le\|A\|_{L^\infty(\ell^\infty_8)}
 +\sqrt{2st}\,\|\psi_x(t)\|_2.                               \tag{6.3}
\]

Using either null endpoint symmetrically, set

\[
 M_\partial=\max\{\|A\|_\infty,\|B\|_\infty\}.              \tag{6.4}
\]

Equations (6.1)--(6.4) imply the uniform max-ball

\[
 \sup_{D_\tau}|\psi|_{\ell^\infty_8}\le S_\tau:=M_\partial
 +4\sqrt{{2s\tau\mathcal F_\tau\over c}}.                   \tag{6.5}
\]

The quartic inequality (4.5) additionally controls the slice `L4` norm, but
the endpoint-anchored estimate (6.5) is already sufficient for continuation.
It also avoids any degenerating interval constant near `t=0`.  This is the a
priori estimate that the one-patch argument lacked.

<a id="section-7-continuation"></a>
## 7. Uniform shell continuation

Let `D_T` be a maximal locally constructed triangle, with `T<tau`.  For a
point in the new shell `D_(T+delta) minus D_T`, its Volterra rectangle has an
unknown cap of area

\[
 \operatorname{area}_{\rm cap}
 \le{(u+v-2T)^2\over2}\le2\delta^2.                           \tag{7.1}
\]

Let

\[
 M_0=\|A+B-C\|_\infty,\quad
 K_0=M_0+{\tau^2b_{S_\tau}\over4\chi},\quad R_c=K_0+\rho,    \tag{7.2}
\]

where `rho>0` and the parent functions are

\[
 b_R=|r|R+(g+12\lambda)R^3,\qquad
 \ell_R=|r|+(3g+36\lambda)R^2.                                \tag{7.3}
\]

The part of the integral inside `D_T` is known and is bounded by `K_0`.
The unknown cap defines a self-map and contraction whenever

\[
 {\delta^2b_{R_c}\over2\chi}\le\rho,
 \qquad {\delta^2\ell_{R_c}\over2\chi}<1.                    \tag{7.4}
\]

The constants in (7.4) do not depend on `T`, so a positive common `delta`
exists.  Moreover, (6.5) bounds the field at the frontier, and the integral
derivative identities

\[
 \psi_u=A'(u)-{1\over4\chi}\int_0^v\nabla W(\psi(u,y))dy,
 \quad
 \psi_v=B'(v)-{1\over4\chi}\int_0^u\nabla W(\psi(x,v))dx       \tag{7.5}
\]

give uniform first-derivative bounds.  The solution extends continuously to
the frontier and (7.4) adds another shell, contradicting maximality.  Thus it
exists on all of `D_tau`.  A causally ordered translated-rectangle tiling is
an equivalent finite construction; uniqueness makes overlaps and admissible
tiling orders agree.

The parent variational symplectic current extends across the finite solution
because its linearized coefficients stay bounded on the same max-ball.  When
the domain is decomposed into shells or translated rectangles, every internal
interface occurs twice with opposite orientation.  Those fluxes cancel,
leaving exactly the two supplied null sides and the final-slice identity.
This is an inherited classical flux statement, not a state-selection theorem.

The parent factorial-squared argument makes any two continuous solutions on
their compact common range identical.  `C1` traces give continuous first and
mixed derivatives through (7.5) and the equation.  Higher trace regularity
bootstraps as in the parent certificate.

<a id="section-7-1-bielecki"></a>
### 7.1 Alternate whole-triangle clipped-Bielecki audit

This lemma is an alternate proof of the finite-triangle existence and
uniqueness conclusion already recorded in EXP-000734.  The alternate route is
recorded in EXP-000737.  It introduces no new theorem, result ID, gate closure,
data class, or physical scope.

Fix any `R_bar>S_tau` and let
`kappa_Rbar:R8 -> [-R_bar,R_bar]^8` be componentwise clipping.  Define

\[
 F_{\bar R}(z)=\nabla W(\kappa_{\bar R}z),\qquad
 G(u,v)=A(u)+B(v)-C.
\]

Componentwise clipping is one-Lipschitz in the max norm.  The registered
Hessian row bound on the cube therefore gives

\[
 |F_{\bar R}(z)-F_{\bar R}(\widetilde z)|_\infty
 \le \ell_{\bar R}|z-\widetilde z|_\infty,\qquad
 \ell_{\bar R}=|r|+(3g+36\lambda)\bar R^2.                    \tag{7.6}
\]

Moreover, `F_Rbar` is globally bounded.  Hence the clipped Volterra map

\[
 (\mathcal T_{\bar R}\phi)(u,v)
 =G(u,v)-{1\over4\chi}\int_0^u\int_0^v
 F_{\bar R}(\phi(\sigma,\nu))\,d\nu\,d\sigma                 \tag{7.7}
\]

acts on the whole Banach space `C(D_tau;R8)`, without a whole-triangle
sup-ball self-map condition.

For `beta>0`, equip this space with the equivalent Bielecki norm

\[
 \|\phi\|_\beta
 =\sup_{D_\tau}e^{-\beta(u+v)}|\phi(u,v)|_\infty.
\]

The exact weighted kernel is

\[
 e^{-\beta(u+v)}
 \int_0^u\int_0^v e^{\beta(\sigma+\nu)}\,d\nu\,d\sigma
 ={(1-e^{-\beta u})(1-e^{-\beta v})\over\beta^2}
 \le {1\over\beta^2}.                                        \tag{7.8}
\]

Consequently,

\[
 \|\mathcal T_{\bar R}\phi-\mathcal T_{\bar R}\widetilde\phi\|_\beta
 \le {\ell_{\bar R}\over4\chi\beta^2}
 \|\phi-\widetilde\phi\|_\beta.                              \tag{7.9}
\]

Since `g>0` and `R_bar>S_tau>=0`, one has `ell_Rbar>0`.  Choosing
`beta=sqrt(ell_Rbar/(2chi))` gives contraction factor `1/2`, so Banach's
theorem supplies a unique clipped solution on all of `D_tau`.

It remains to show that clipping never activates.  If activation occurred,
let `t_*<=tau` be the first slice time for which

\[
 \sup_{D_{t_*}}|\psi_{\bar R}|_\infty=\bar R.
\]

Because `M_partial<=S_tau<R_bar`, one has `t_*>0`.  On all of `D_(t_*)`,
including the first-contact set, `kappa_Rbar psi_Rbar=psi_Rbar`; thus the
clipped solution satisfies the original equation there.  The shifted-energy
argument of Sections 4--6 applies and yields

\[
 \sup_{D_{t_*}}|\psi_{\bar R}|_\infty\le S_\tau<\bar R,
\]

contradicting first contact.  Hence clipping is everywhere inactive, and the
clipped fixed point is the original solution.  Conversely, every original
solution obeys the same amplitude bound and is therefore a fixed point of
(7.7), so clipped uniqueness also gives original uniqueness.

This alternate audit stops at the `C1` existence level.  Every
`C8 x C8 -> C7 x C6` assertion continues to rely exclusively on the corrected
Section 8.1 recursion

\[
 D_m\le\max\{D_{m-1},
 T_m+\tau P_{m-1}/(2\chi),P_{m-2}/(4\chi)\},
\]

with its final entry omitted at `m=1`, as required by EXP-000735.  The
contraction factor can be fixed at `1/2`, but `R_bar`, `ell_Rbar`, `beta`, and
the equivalence constant between the Bielecki and sup norms remain
finite-horizon and trace dependent.


<a id="section-8-stability"></a>
## 8. Global field-value stability

Let `psi` and `psi_tilde` be solutions for two compatible trace pairs.  Put

\[
 R=\max\{S_\tau(A,B),S_\tau(\widetilde A,\widetilde B)\},\qquad
 \ell_R=|r|+(3g+36\lambda)R^2.                                 \tag{8.1}
\]

For the two free lifts, let

\[
 \delta_G=\|A+B-C-(\widetilde A+\widetilde B-\widetilde C)
             \|_\infty.                                      \tag{8.2}
\]

Iterating the Volterra difference inequality yields

\[
 |\psi-\widetilde\psi|(u,v)
 \le\delta_G\sum_{n=0}^\infty
 {\bigl(\ell_Ruv/(4\chi)\bigr)^n\over(n!)^2}.                 \tag{8.3}
\]

Because `uv<=tau^2` on `D_tau`, the exact Bessel majorant is

\[
 \|\psi-\widetilde\psi\|_\infty
 \le\delta_G I_0\!\left(\tau\sqrt{\ell_R/\chi}\right).       \tag{8.4}
\]

No whole-triangle smallness condition occurs in (8.4).  This certificate
claims field-value stability.  Derivative and phase-space stability need
higher trace norms and are not silently included.

### 8.1 High-regularity phase-map lemma

For the composition route, now assume `A,B in C8`.  Let

\[
 D_m=\max_{p+q\le m}\|\partial_u^p\partial_v^q\psi\|_\infty,
 \qquad
 T_m=\max\{\|A\|_{C^m},\|B\|_{C^m}\}.                         \tag{8.5}
\]

Let `P_j(D_0,...,D_j)` denote the Faà di Bruno upper polynomial for `j`
derivatives of `grad W(psi)` on the `S_tau` ball.  Because `grad W` is cubic,
its derivative tensors of order four and higher vanish, and every monomial in
`P_j` contains at most three field derivatives whose total order is `j`.
Differentiating the two pure Volterra formulas and the mixed equation gives

\[
 D_m\le\max\left\{
 D_{m-1},
 T_m+{\tau\over2\chi}P_{m-1},
 {1\over4\chi}P_{m-2}\right\},                               \tag{8.6}
\]

with the third entry omitted for `m=1`.  The explicit `D_(m-1)` entry retains
all lower derivatives already included in the definition of `D_m`.  Thus the right side for `D_m`
depends only on `D_0,...,D_(m-1)`, so (8.6) closes inductively through
`m=8`.

For two trace pairs, subtract the same recursions.  Polynomial Lipschitz
bounds on a common derivative ball, starting from (8.4), give continuity at
each successive order.  Hence

\[
 (A,B)\longmapsto(q,\Pi):C^8\times C^8\longrightarrow C^7\times C^6
                                                                  \tag{8.7}
\]

is continuous.  Every compact `C8` source subset therefore has common trace,
flux, amplitude, and derivative bounds.  On its seam-compatible trace image,
these are the uniform fixed-family inputs required by the inherited
`O(a^2)` composition theorem.  This is a high-regularity classical statement,
not derivative stability for merely `C1` traces.

<a id="section-9-pah1"></a>
## 9. Full ordered PA-H1 circumference

The inserted tangent calibration fixes

\[
 L={\pi\over2},\qquad {c\over\chi}=1,
 \qquad {-2r\over\chi}=9.                                    \tag{9.1}
\]

Thus `s=1` and the direct characteristic slice has `tau=L/(2s)=pi/4`.
The former whole-triangle factors remain

\[
 q\ge{9\pi^2\over32}>1,
 \qquad q_{\rm shifted}\ge{9\pi^2\over64}>1.                 \tag{9.2}
\]

Equation (9.2) is not repaired by pretending it is small.  It is bypassed by
the energy continuation theorem, which applies to every finite `tau` and
every compatible `C1` trace pair with finite `F_tau`.  It therefore includes
nonconstant smooth perturbations of the ordered equilibrium on the full
inserted circumference.

As an illustrative constant-curvature **linearized control only**, splitting
`tau` into two equal shells makes the cap factor for `ell=9chi` equal to
`9pi^2/128<1`, while three equal shells make the `ell=18chi` factor
`pi^2/16<1`.  These are not nonlinear or universal patch counts.  The actual
nonlinear continuation uses the trace-dependent `b_(R_c)`, `ell_(R_c)`, and
self-map reserve in (7.2)--(7.4).

For example, on the collective branch let

\[
 q_e(x)=v+\epsilon\cos(4x),\qquad \Pi_e(x)=0,qquad
 0<|\epsilon|<v=\sqrt{-r/g},                                   \tag{9.3}
\]

for all eight species on the `L=pi/2` circle.  The inherited global periodic
classical Cauchy theorem evolves these smooth data backward from `t=tau`.
Restricting that solution to the two null sides produces compatible,
nonconstant traces, and Goursat uniqueness reconstructs the same periodic
final phase.  More generally, take the trace image of an open periodic
`C8 x C7` Cauchy neighborhood and equip that image only with the
pullback/relative topology from its Cauchy data.  No independent
embedded-manifold or openness theorem inside unconstrained trace space is
claimed.  On each compact source subset, differentiated Volterra induction
gives common `C8`-to-`C7 x C6` phase-map bounds as well as common flux and
amplitude bounds.

Arbitrary Goursat traces do not automatically lie in that trace image.  Literal
direct-circle composition still requires

\[
 \partial_x^m q(-s\tau)=\partial_x^m q(s\tau),\quad0\le m\le7,
\qquad
 \partial_x^m\Pi(-s\tau)=\partial_x^m\Pi(s\tau),\quad0\le m\le6. \tag{9.4}
\]

At first order this includes `A(2tau)=B(2tau)` and the integral-corrected
derivative conditions already derived in the composition certificate.
The registered
`NG-2026-08-03-PRE-A-CP1-CL8-UNMATCHED-PERIODIC-COMPOSITION` remains in force
for generic admitted traces; global existence does not weaken that no-go.

This coverage does not derive the PA-H1 circumference, the tuning, the
collective species, the characteristic role, or a state on the trace space.

<a id="section-10-gate"></a>
## 10. Gate resolution and remaining route

The child resolution is:

- `PA-CP1-CL8-FULL-CIRCUMFERENCE-GOURSAT-EXISTENCE`:
  **closed in the declared classical fixed-background scope**;
- `PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION`:
  **open**.

The first statement means finite-triangle existence, uniqueness, explicit
amplitude control, and field-value stability, including the inserted PA-H1
length.  It does not mean a finite-`a` Goursat scheme, a full-dimensional
Einstein characteristic theorem, or a physical state.

EXP-000736 has since split the second gate: finite-regulator classical
invariant measures exist, but invariance, the declared symmetries, smooth seam
support, and regulator compatibility do not uniquely select a preferred one.
The parent preferred-state gate therefore remains open.  Its next bounded
child is `PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE`, which must declare the
exact CCR normalization and `hbar` before any quantum state is imported.  It
must not use the arbitrary proof shift `C_*` as an absolute vacuum-energy
choice.

<a id="section-11-adversarial"></a>
## 11. Devil's-advocate review

1. **Adding `C_*` changes the dynamics.**  **DISMISSED.**  Its gradient is
   zero.  The slice and both null ledgers acquire exactly the same geometric
   constant.
2. **The shifted energy proves energy below physical empty space.**
   **UPHELD AS FALSE.**  The shift is an arbitrary proof normalization and no
   physical reference state is selected.
3. **A negative quadratic term can cause finite-time blow-up.**
   **DISMISSED FOR THE DECLARED SIGN CLASS.**  Positive `g` and nonnegative
   Q3 locking make `W` bounded below and give (4.5); (6.5) prevents amplitude
   blow-up on every finite triangle.
4. **The local patch radius grows after every tile.**  **DISMISSED.**  The
   exact flux identity restores the same global bound `S_tau` after each
   causal band, and the shell radius `R_c` is computed once from that bound.
5. **Energy control alone does not provide a continuation trace.**
   **DISMISSED.**  The Volterra derivative formulas (7.5), the amplitude
   bound, and bounded boundary derivatives give uniform Lipschitz control up
   to a finite frontier.
6. **The theorem also works for `g<=0` or `lambda<0`.**  **UPHELD AS FALSE.**
   Those signs remove the declared coercive argument and are excluded.
7. **Finite `tau` implies a uniform cosmological history.**  **UPHELD AS
   FALSE.**  `S_tau` and the stability factor may grow with `tau`; no
   infinite-time or thermodynamic bound is claimed.
8. **Field-value stability is full phase-space stability.**  **UPHELD AS
   FALSE.**  Derivative stability requires stronger trace norms.
9. **Full PA-H1 length closes the state bridge.**  **UPHELD AS FALSE.**  The
   trace pair and every measure or quantum state remain inputs or open gates.
10. **Existence makes arbitrary final slices periodic.**  **UPHELD AS FALSE.**
    Only the seam-compatible trace subset composes directly; generic
    traces still require the recorded extension branch.
11. **This proves C6, CP1, or Pre-A.**  **UPHELD AS FALSE.**  The background
    cone, physical state/reference, quantum composition, phase transition,
    cooling, gravity, and emergence links remain open.

12. **Componentwise clipping destroys the gradient structure, so the shifted
    energy identity cannot be applied to the clipped equation.**  **VALID WITH
    MITIGATION.**  In general `F_Rbar=grad W composed with kappa_Rbar` need not
    be the gradient of a scalar potential, and no energy identity is asserted
    after clipping activates.  The energy estimate is used only on the closed
    pre-exit triangle, where `kappa_Rbar psi=psi` and
    `F_Rbar(psi)=grad W(psi)`, including at first contact.  The strict bound
    `S_tau<R_bar` rules out that contact, so the non-gradient region is never
    entered.

<a id="section-12-reproduction"></a>
## 12. Reproduction

Run from the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_global_goursat_continuation.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_verify.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_verify.py --check-stored
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_global_goursat_continuation_pdf.py
```

The primary implementation uses symbolic polynomial identities.  The
non-importing implementation reconstructs the Q3 counts, rational completed
squares, continuation fixture, and Volterra coefficients without importing
the primary module.  The integrated verifier reruns both into temporary
files, compares fresh and stored artifacts, audits parent hashes, scope flags,
certificate anchors, and independent-source separation.

<a id="section-13-no-overclaim"></a>
## 13. No-overclaim boundary

This certificate proves only global classical existence, uniqueness and
field-value stability on each finite null triangle of an inserted fixed
`1+1` CL8 theory and exhibits a nonconstant seam-compatible periodic trace
family.  It does not make arbitrary Goursat traces periodic, derive the cone,
a horizon, spacetime, gravity, full `3+1` dynamics, a finite-regulator
characteristic scheme, a preferred boundary measure, a quantum or Hadamard
state, physical empty space, an absolute energy zero, a below-empty-space
sign, cooling, a phase transition, C6 advancement, CP1, or Pre-A.

The clipped-Bielecki lemma is only an alternate verification of the
finite-triangle classical statement already recorded in EXP-000734.  It
does not alter EXP-000735, provide a horizon-uniform bound as `tau` tends
to infinity, make generic final traces periodic, select a seam, extension,
classical measure, quantum or Hadamard state, or physical vacuum, derive
the inserted Lorentzian background or PA-H1 parameters, reach full `3+1`
dynamics, advance C6, complete CP1 or Pre-A, or create a new theorem,
result, or gate.
