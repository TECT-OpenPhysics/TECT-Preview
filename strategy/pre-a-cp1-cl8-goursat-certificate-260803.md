# Pre-A CL8 continuum Goursat certificate

**Candidate:** `PA-CP1-CL8-GOURSAT-v0`  
**Internal result:**
`PA-CP1-CL8-CONTINUUM-GOURSAT-ENERGY-SYMPLECTIC-FLUX`  
**Parent:** `PA-CP1-ST8-Q3LOCK-v0`  
**Task:** `T-054`  
**Context only:** `C6-SPACETIME-SIGNATURE`  
**Authority:** T0 exact classical continuum candidate certificate; no TECT
claim or tier change  
**Date:** 2026-08-03

## 1. Verdict

The Q3-locked eight-species classical field has a valid local
characteristic reconstruction theorem after a fixed `1+1` Lorentzian
background and the transverse-zero sector are supplied.  Compatible values
on two intersecting null segments determine one continuous interior solution
whenever explicit max-ball self-map and contraction inequalities hold.  For
`C1` traces the solution satisfies an exact energy balance, and `C1`
variations about it satisfy the derivative-first symplectic-flux identity
required by the inherited `dPi wedge dpsi` convention.

This is the continuum side of the finite-regulator fork.  It does not yet
answer how characteristic data initialize the finite lattice.  The separate
fixed-domain Cauchy convergence theorem therefore must not be silently
composed with this result.  That missing arrow is named
`PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION`.

The fixed Lorentzian background supplies the cone.  The theorem does not
derive spacetime, an event horizon, or a physical state.

## 2. Prior-art and novelty boundary

Characteristic Volterra equations, Banach fixed-point arguments for
semilinear hyperbolic equations, energy currents, covariant symplectic
currents, and measurable pushforwards are established mathematics.
`PA-H1-DNKG4-v0` already registered the scalar fixed-background version of
the method.  Relevant entry points include the characteristic initial-value
literature cited in that certificate and standard Goursat results such as
Gerard and Wrochna's characteristic Cauchy analysis:
<https://arxiv.org/abs/1409.6691>.

No world-first or new general theorem is claimed.  The repository-specific
advance is the exact convention-level bridge to the Q3-locked eight-species
candidate: the one-eighth normalization, Q3 force and Hessian constants,
energy sign boundary, inherited symplectic orientation, and explicit
separation from the finite regulator.

<a id="section-3-model"></a>
## 3. Declared continuum model and physical ledger

Let `Q3={0,1}^3`, with two vertices adjacent when their Hamming distance is
one.  It has eight vertices, twelve undirected edges, and degree three.  For
`z in R^8`, define

\[
 W(z)=\sum_{\epsilon\in Q_3}
 \left({r\over2}z_\epsilon^2+{g\over4}z_\epsilon^4\right)
 +{\lambda\over4}\sum_{\epsilon\sim\eta}
 (z_\epsilon-z_\eta)^2(z_\epsilon^2+z_\eta^2),
\]

with

\[
 \chi>0,\qquad c>0,\qquad g>0,\qquad
 \lambda\ge0,\qquad r\in\mathbb R.
\]

The declared continuum equation is

\[
 \chi\psi_{tt}-c\psi_{xx}+\nabla W(\psi)=0,
 \qquad \psi(t,x)\in\mathbb R^8.                 \tag{3.1}
\]

It is a one-axis, transverse-zero model.  It is not a proof of full
three-dimensional dependence.

The Q3LOCK fine spacing is `h=a/2`, so one fine-cell volume is

\[
 h^3={a^3\over8},\qquad \rho=h^3\Pi.
\]

After summing a transverse-zero configuration and dividing by its physical
transverse area, the one-dimensional cell weight is `a/8`, not `a^3/8`.
Thus the continuum energy and symplectic forms per unit transverse area carry

\[
 {1\over8}\sum_{\epsilon=1}^8\int dx.
\]

On the equal-species diagonal, the eight weights cancel the one-eighth factor,
so the physical onsite quartic coefficient remains `g`.  The finite normalized
collective coordinate's `g/8` is a different convention and is not imported.

Set

\[
 s=\sqrt{c/\chi},\qquad
 u=t+x/s,\qquad v=t-x/s.
\]

Then

\[
 t={u+v\over2},\qquad x={s(u-v)\over2},
\]

and direct substitution gives

\[
 \chi\partial_t^2-c\partial_x^2=4\chi\partial_u\partial_v.
\]

Equation (3.1) therefore becomes

\[
 4\chi\psi_{uv}+\nabla W(\psi)=0.               \tag{3.2}
\]

The speed and null coordinates are inputs.  This calculation does not derive
them from the finite lattice.

<a id="section-4-bounds"></a>
## 4. Exact Q3 max-ball constants

For one Q3 edge, write

\[
 P(a,b)={\lambda\over4}(a-b)^2(a^2+b^2).
\]

Direct differentiation gives

\[
 \partial_aP={\lambda\over2}(a-b)(2a^2-ab+b^2),
\]

\[
 \partial_{aa}P=\lambda(3a^2-3ab+b^2),
\]

\[
 \partial_{ab}P=-{\lambda\over2}(3a^2-4ab+3b^2).
\]

On `|a|,|b|<=R`, coefficient absolute sums give

\[
 |\partial_aP|\le4\lambda R^3,
\]

\[
 |\partial_{aa}P|\le7\lambda R^2,\qquad
 |\partial_{ab}P|\le5\lambda R^2.
\]

Each species has three neighbours.  Hence

\[
 \|\nabla W(z)\|_{\ell^\infty_8}\le
 b_R:=|r|R+(g+12\lambda)R^3,                    \tag{4.1}
\]

and the symmetric Hessian has row sum at most

\[
 \ell_R:=|r|+(3g+36\lambda)R^2.                 \tag{4.2}
\]

Consequently

\[
 \|\nabla W(z)-\nabla W(y)\|_\infty
 \le\ell_R\|z-y\|_\infty                       \tag{4.3}
\]

on the radius-`R` max ball.  The lock parts of (4.1) and (4.2) are saturated
by the bipartite Q3 assignment whose adjacent endpoints are `+R` and `-R`.
Thus `12` and `36` are derived graph-polynomial constants, not fitted margins.

<a id="section-5-goursat"></a>
## 5. Gated CL8 Goursat theorem

For `tau>0`, let

\[
 D_\tau=\{(u,v):u\ge0,\ v\ge0,\ u+v\le2\tau\}.
\]

Let

\[
 A,B\in C^k([0,2\tau];\mathbb R^8),
 \qquad A(0)=B(0)=C,                            \tag{5.1}
\]

and define

\[
 G(u,v)=A(u)+B(v)-C,\qquad M_0=\|G\|_\infty.
\]

Assume that some `R>0` obeys

\[
 M_0+{\tau^2b_R\over4\chi}\le R,               \tag{5.2}
\]

\[
 q:={\tau^2\ell_R\over4\chi}<1.                \tag{5.3}
\]

### Theorem CL8-G

Under (5.1)--(5.3):

1. there is a continuous solution on `D_tau` with `||psi||<=R` and the two
   declared traces;
2. it is the fixed point of

   \[
   (\mathcal T\phi)(u,v)=G(u,v)-{1\over4\chi}
   \int_0^u\int_0^v\nabla W(\phi(\sigma,\nu))
   \,d\nu\,d\sigma;                             \tag{5.4}
   \]

3. it is unique among all continuous integral solutions with those traces,
   not only among solutions in the radius-`R` ball;
4. two data sets admitted by the same `R,q` satisfy

   \[
   \|\psi-\widetilde\psi\|_\infty
   \le{\|G-\widetilde G\|_\infty\over1-q};     \tag{5.5}
   \]

5. `C1` traces give continuous `psi_u`, `psi_v`, and `psi_uv`; `Ck` traces
   with `k>=2` give a `Ck` solution, and smooth traces give a smooth solution.

Only the corner value in (5.1) is common data.  No third corner value or null
normal derivative is supplied.  Mixed derivatives at the corner are fixed by
the equation.

### Proof

For `(u,v) in D_tau`, the Volterra rectangle `[0,u]x[0,v]` remains in
`D_tau`.  Moreover,

\[
 4uv=(u+v)^2-(u-v)^2\le4\tau^2.                 \tag{5.6}
\]

Equations (4.1), (4.3), and (5.6) imply

\[
 \|\mathcal T\phi\|_\infty
 \le M_0+{\tau^2b_R\over4\chi}\le R,
\]

and

\[
 \|\mathcal T\phi-\mathcal T\widetilde\phi\|_\infty
 \le q\|\phi-\widetilde\phi\|_\infty.
\]

The closed sup-norm ball is complete, so Banach's theorem gives the admitted
fixed point and (5.5).

For the stronger uniqueness statement, let `psi` and `psi_tilde` be any two
continuous integral solutions with the same traces.  Their compact ranges fit
inside some radius-`S` ball, where the polynomial gradient has finite
Lipschitz constant `ell_S`.  Their difference `d` obeys, after `n` Volterra
iterations,

\[
 |d(u,v)|_\infty\le\|d\|_\infty
 {\{\ell_Suv/(4\chi)\}^n\over(n!)^2}.           \tag{5.7}
\]

The coefficient tends to zero for fixed `(u,v)`, hence `d=0`.  This proves
uniqueness conditional on continuous existence.  It does not prove ungated
existence.

Differentiating (5.4) gives

\[
 \psi_u(u,v)=A'(u)-{1\over4\chi}
 \int_0^v\nabla W(\psi(u,\nu))d\nu,
\]

\[
 \psi_v(u,v)=B'(v)-{1\over4\chi}
 \int_0^u\nabla W(\psi(\sigma,v))d\sigma,
\]

and (3.2).  Repeated differentiation and the polynomial nonlinearity give the
regularity bootstrap.

The exact rational gate fixture

```text
r=g=lambda=chi=R=1, M0=1/2, tau=1/10
```

gives

\[
 b_R=14,\qquad \ell_R=40,
\]

\[
 M_0+{\tau^2b_R\over4\chi}={107\over200},
 \qquad q={1\over10},
 \qquad (1-q)^{-1}={10\over9}.
\]

The primary and non-importing scripts independently derive these values.

<a id="section-6-energy"></a>
## 6. Exact continuum energy and null flux

For compatible `C1` traces, define the per-unit-transverse-area density

\[
 e={1\over8}\left\{
 {\chi\over2}|\psi_t|^2+{c\over2}|\psi_x|^2+W(\psi)
 \right\}.
\]

Direct differentiation gives the off-shell identity

\[
 \partial_te-\partial_x\left({c\over8}\psi_t\cdot\psi_x\right)
 ={1\over8}\psi_t\cdot
 (\chi\psi_{tt}-c\psi_{xx}+\nabla W).           \tag{6.1}
\]

Equivalently, on a solution of (3.2),

\[
 \partial_v(\chi|\psi_u|^2)+\partial_u(W/2)=0,
\]

\[
 \partial_u(\chi|\psi_v|^2)+\partial_v(W/2)=0. \tag{6.2}
\]

Integrating over `D_tau` and using `dx=s du` on `u+v=2tau` yields

\[
 E_\tau={1\over8}\int_{-s\tau}^{s\tau}
 \left\{{\chi\over2}|\psi_t|^2+{c\over2}|\psi_x|^2+W(\psi)\right\}dx
\]

\[
 ={s\over8}\int_0^{2\tau}
 \left\{\chi|A'|^2+{W(A)\over2}\right\}du
 +
 {s\over8}\int_0^{2\tau}
 \left\{\chi|B'|^2+{W(B)\over2}\right\}dv.    \tag{6.3}
\]

For `r<0`, each onsite quartic is bounded below by `-r^2/(4g)` and the
Q3 lock is nonnegative.  Equality is attained by all eight species at the
same `plus-or-minus sqrt(-r/g)` value, so

\[
 \min W=-{2r^2\over g}.                          \tag{6.4}
\]

Thus (6.3) is an exact balance but not a positivity theorem.  Adding a shift
would change both the slice and boundary ledgers and would have to be declared
separately.  No physical-empty-space comparison follows.

For the exact massless fixture with only one species nonzero,

```text
chi=2, s=3, c=18, tau=1, A(u)=u, B(v)=2v,
```

the slice and boundary sides of (6.3) both equal `15/2`.  With `r=-1`,
`g=1`, and all eight species fixed at `1`, both unshifted sides equal `-3/2`.

<a id="section-7-symplectic"></a>
## 7. Variational symplectic flux and orientation

The inherited convention is

\[
 \Omega={1\over8}\int\delta\Pi\wedge\delta\psi,
 \qquad \Pi=\chi\psi_t,
 \qquad \iota_{X_H}\Omega=-dH.                 \tag{7.1}
\]

Let `eta_1,eta_2` be two variations around the same nonlinear solution.  Define
their compatible `C1` tangent traces by
`a_i(u)=eta_i(u,0)` and `b_i(v)=eta_i(0,v)`, with
`a_i(0)=b_i(0)`.  They solve

\[
 4\chi\eta_{uv}+D^2W(\psi)\eta=0.               \tag{7.2}
\]

Symmetry of the Hessian cancels the potential contribution in the bilinear
current.  Stokes' theorem, or direct integration of that current, gives

\[
 \Omega_\Sigma(\eta_1,\eta_2)
 ={1\over8}\int_{-s\tau}^{s\tau}
 \{(\chi\eta_{1,t})\cdot\eta_2
 -(\chi\eta_{2,t})\cdot\eta_1\}dx              \tag{7.3}
\]

\[
 ={\chi s\over8}\left[
 \int_0^{2\tau}(a_1'\cdot a_2-a_2'\cdot a_1)du
 +\int_0^{2\tau}(b_1'\cdot b_2-b_2'\cdot b_1)dv
 \right].                                      \tag{7.4}
\]

The derivative-first order in (7.4) is load-bearing.  The value-first form is
its negative and belongs to the opposite `dpsi wedge dPi` convention.

For `chi=2`, `s=3`, `tau=1`, and the one-species massless variations

\[
 a_1(u)=u,\quad b_1(v)=2v,
 \qquad a_2(u)=u^2,\quad b_2(v)=3v^2,
\]

both (7.3) and (7.4) equal `-14`; the hostile value-first control is `+14`.

This is a classical variational statement.  A nonlinear solution map does not
automatically define a linear Weyl-algebra isomorphism or a quantum state.

<a id="section-8-measure"></a>
## 8. Supplied classical measure pushforward

On a Borel subset of compatible boundary data supported inside common strict
gates, (5.5) makes the solution map into `C(D_tau;R^8)` continuous.  Define

\[
 P_\tau(A,B)(x)=
 \psi(\tau+x/s,\tau-x/s),\qquad
 P_\tau:\mathcal D_\tau\longrightarrow
 C([-s\tau,s\tau];\mathbb R^8),
\]

where `mathcal D_tau` denotes the admitted Borel subset of compatible boundary
data with the sup topology.  The field-value slice restriction `P_tau` is
continuous and hence Borel measurable.  If a classical Borel probability
measure `mu_H` is supplied on that data set, then

\[
 \mu_\Sigma=(P_\tau)_*\mu_H
\]

is a well-defined classical probability measure on the reconstructed image.
This is functorial bookkeeping, not selection: `mu_H` remains an input.  The
statement proves no preferred, invariant, equilibrium, thermal, Hadamard,
vacuum, or quantum state.

<a id="section-9-composition"></a>
## 9. The open boundary-to-lattice composition

The next package proves a different theorem: fixed-domain semidiscrete Cauchy
convergence for a separately supplied smooth continuum solution.  It does not
receive `(A,B)` from this Goursat map.  The following remain unproved:

- a finite-`a` characteristic scheme or boundary-to-Cauchy initialization;
- compatible continuum and lattice domains and boundary conditions;
- uniform regularity of the Goursat slice in the convergence theorem's norms;
- energy and symplectic consistency under sampling and reconstruction;
- convergence of the supplied classical measure;
- one common selected quantum state;
- moving-null-boundary or ghost-value control.

These obligations define the manifest-local route gate
`PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION`.  It is not a claim-card gate and
does not alter C6's tier or existing `C6-BCC-PREMISE-BLOCKED` status.

## 10. Devil's-advocate review

1. **The theorem assumes the Lorentz cone that Pre-A is meant to explain.**
   **UPHELD.**  The background and `s=sqrt(c/chi)` are explicit inputs.  This
   is a compatibility theorem inside that background, not spacetime emergence.
2. **A transverse-zero `1+1` field is not a full `3+1` bulk.**
   **UPHELD.**  Transverse perturbations, isotropy, fine-translation
   restoration, and the full continuum limit remain open.
3. **The local contraction gate is not global nonlinear existence.**
   **UPHELD.**  Existence is asserted only under (5.2)--(5.3).  The stronger
   uniqueness statement is conditional on a continuous solution existing.
4. **The flux can be negative for the ordered potential.**
   **UPHELD.**  Equation (6.4) is recorded and no positivity or vacuum argument
   uses the unshifted flux.
5. **The symplectic sign could drift from Q3LOCK.**
   **DISMISSED in the declared convention.**  Both implementations derive
   `-14`; the opposite sign is retained as an explicit hostile control.
6. **Pushing forward a measure does not select a state.**
   **UPHELD.**  The measure is supplied and remains classical.
7. **The continuum theorem might be mistaken for finite-regulator causality.**
   **MITIGATED.**  The finite-`a` map is absent, both strict-cone no-gos remain
   authoritative, and the missing composition has a stable route ID.

## 11. Reproduction

Run with the repository environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_goursat.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_goursat_independent.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_goursat_verify.py
```

The primary implementation uses symbolic polynomial and current identities.
The non-importing implementation reconstructs the Q3 polynomial, Volterra
coefficients, energy, and symplectic fixtures using rational sparse algebra.
The integrated verifier reruns both into temporary files, compares exact
outputs, audits authority and scope text, and compares fresh results with the
stored JSON artifacts.

## 12. No-overclaim boundary

This certificate proves a gated classical continuum Goursat theorem on an
inserted fixed `1+1` Lorentzian background.  It does not prove ungated
existence, a finite-regulator Goursat map or exact cone, boundary-to-lattice
composition, regulator removal, full `3+1` dynamics, restoration of fine
translation symmetry, a quantum continuum or selected state, physical empty
space or a below-empty-space sign, cooling, gravity, an event horizon, CP1, or
Pre-A.
