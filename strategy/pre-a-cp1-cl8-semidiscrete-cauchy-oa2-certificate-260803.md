# Pre-A CL8 fixed-domain semidiscrete Cauchy convergence certificate

**Candidate:** `PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0`  
**Internal result:**
`PA-CP1-CL8-FIXED-DOMAIN-SEMIDISCRETE-CAUCHY-OA2`  
**Continuum-definition parent:** `PA-CP1-CL8-GOURSAT-v0`  
**Task:** `T-054`  
**Context only:** `C6-SPACETIME-SIGNATURE`  
**Authority:** T0 exact analytic classical semidiscrete candidate certificate;
no TECT claim or tier change  
**Date:** 2026-08-03

## 1. Verdict

The CL8 centered spatial semidiscretization converges at second order to a
separately supplied smooth continuum Cauchy solution on every fixed periodic
physical domain and fixed finite time interval.  The norm is the weighted
discrete `H1_a x L2_a` phase norm dictated by the one-eighth physical ledger.
Each finite regulator also conserves its declared Hamiltonian and the
variational symplectic form exactly.

This is not a semidiscrete Goursat theorem.  No characteristic trace is turned
into lattice initial data here.  The continuum Goursat theorem and this Cauchy
convergence theorem are deliberately separate; their missing composition is
`PA-CP1-CL8-BOUNDARY-TO-LATTICE-COMPOSITION`.

The registered strict-cone package supplies particular variational witness
channels whose tails are nonzero at every fixed lattice spacing.  The present
theorem does not assert a nonzero tail for every matched datum.  For smooth
matched Cauchy data, it proves only that the aggregate weighted norm is
`O(a^2)` on any region where the continuum solution is zero.  Exact finite-`a`
support is not recovered.

## 2. Prior-art and novelty boundary

Second-order centered-difference consistency, periodic summation by parts,
modified-energy estimates for semilinear wave equations, Gronwall closure,
Hamiltonian semidiscretization, and interval-arithmetic regression are
established techniques.  Relevant primary entry points include

- Ignat and Zuazua on semidiscrete wave dispersion:
  <https://arxiv.org/abs/1008.0197>;
- Marsden, Patrick, and Shkoller on discrete variational field theories:
  <https://arxiv.org/abs/math/9807080>;
- recent rigorous discrete nonlinear Klein-Gordon continuum analysis:
  <https://arxiv.org/abs/2402.13663>.

No world-first or new general theorem is claimed.  The repository-specific
advance is the exact CL8/Q3 convention audit: the physical `a/8` weight,
derived nonlinear constants, exact Hamiltonian orientation, explicit
second-order bound, and separation of Cauchy convergence from characteristic
boundary composition.

<a id="section-3-grid"></a>
## 3. Grid, norm, and equations

Let

\[
 \mathbb T_L=\mathbb R/(L\mathbb Z),\qquad
 a={L\over M},\qquad x_j=ja,
\]

with indices periodic modulo `M`.  The analytic theorem holds for all
sufficiently fine periodic grids.  The inherited CP1 regulator subsequence
uses even `M`, so the fine size `N=2M` remains divisible by four.

For grid vectors `u_j in R^8`, define

\[
 \langle u,v\rangle_a={a\over8}\sum_{j=0}^{M-1}u_j\cdot v_j,
 \qquad \|u\|_a^2=\langle u,u\rangle_a,          \tag{3.1}
\]

\[
 D_a^+u_j={u_{j+1}-u_j\over a},
 \qquad
 \Delta_au_j={u_{j+1}-2u_j+u_{j-1}\over a^2},  \tag{3.2}
\]

\[
 \|u\|_{H_a^1}^2=\|u\|_a^2+\|D_a^+u\|_a^2.   \tag{3.3}
\]

For a continuum function `f`, let `(R_a f)_j=f(x_j)`.

The continuum Cauchy equation is

\[
 \chi\psi_{tt}-c\psi_{xx}+\nabla W(\psi)=0,     \tag{3.4}
\]

and the semidiscrete equation is

\[
 \chi\ddot\psi_j^a-c\Delta_a\psi_j^a
 +\nabla W(\psi_j^a)=0.                          \tag{3.5}
\]

Here `W` is exactly the eight-species Q3 potential declared in the continuum
Goursat certificate, with `chi,c,g>0`, `lambda>=0`, and real `r`.

<a id="section-4-hamiltonian"></a>
## 4. Exact finite-regulator Hamiltonian and symplectic structure

Per unit transverse area, set

\[
 H_a={a\over8}\sum_j\left{
 { |\Pi_j|^2\over2\chi}
 +{c\over2}|D_a^+\psi_j|^2+W(\psi_j)
 \right},                                     \tag{4.1}
\]

\[
 \Omega_a={a\over8}\sum_jd\Pi_j\wedge d\psi_j.
                                                               \tag{4.2}
\]

With the inherited convention

\[
 \iota_{X_H}\Omega_a=-dH_a,                    \tag{4.3}
\]

Hamilton's equations are

\[
 \dot\psi_j={\Pi_j\over\chi},
 \qquad
 \dot\Pi_j=c\Delta_a\psi_j-\nabla W(\psi_j),  \tag{4.4}
\]

which are equivalent to (3.5).  The common `a/8` factor cancels in (4.4) but
must remain in energy and symplectic comparisons.

The antisymmetry of the Hamiltonian matrix gives

\[
 {dH_a\over dt}=0.                              \tag{4.5}
\]

For two variational solutions `(xi,varpi)` and `(eta,vartheta)`, define

\[
 \Omega_a((\xi,\varpi),(\eta,\vartheta))
 ={a\over8}\sum_j
 (\varpi_j\cdot\eta_j-\vartheta_j\cdot\xi_j). \tag{4.6}
\]

Because `D^2W` and the discrete spatial operator are symmetric,

\[
 {d\over dt}\Omega_a((\xi,\varpi),(\eta,\vartheta))=0.          \tag{4.7}
\]

Equivalently, for `z=(psi,Pi)`,

\[
 S={a\over8}\begin{pmatrix}0&-I\\I&0\end{pmatrix},
 \qquad
 A={8\over a}JH_a'',
 \qquad
 A^TS+SA=0.                                    \tag{4.8}
\]

The onsite identity

\[
 {r\over2}q^2+{g\over4}q^4+{r^2\over4g}
 ={g\over4}(q^2+r/g)^2                         \tag{4.9}
\]

for `r<0`, together with the nonnegative lock and positive kinetic term,
makes every finite-regulator Hamiltonian coercive up to an additive constant.
Conservation therefore gives global existence for the finite ODE.

<a id="section-5-consistency"></a>
## 5. Exact centered-difference consistency

Taylor expansion with a two-sided sixth-derivative remainder gives

\[
 \Delta_aR_af-R_af''={a^2\over12}R_af^{(4)}+\mathcal R_a,
\]

\[
 \|\mathcal R_a\|_\infty
 \le{a^4\over360}\|f^{(6)}\|_\infty.           \tag{5.1}
\]

The coefficients are derived as

\[
 {1\over12}={2\over4!},\qquad
 {1\over360}={2\over6!}.                       \tag{5.2}
\]

The exact polynomial controls are

\[
 \Delta_ax^0=0,\quad \Delta_ax=0,\quad
 \Delta_ax^2=2,
\]

\[
 \Delta_ax^4=12x^2+2a^2,
\]

\[
 \Delta_ax^6=30x^4+30a^2x^2+2a^4.             \tag{5.3}
\]

The positive Fourier symbol independently gives

\[
 {4\sin^2(ka/2)\over a^2}
 =k^2-{k^4a^2\over12}+{k^6a^4\over360}+O(a^6).
                                                               \tag{5.4}
\]

For the nonlinear manufactured field

\[
 \psi_\epsilon(t,x)=\alpha_\epsilon(1+t)x^4,
\]

the nonlinear Q3 force is evaluated pointwise in both equations and cancels
from the discrete-minus-continuum residual.  The remaining exact difference is

\[
 -c(\Delta_a-\partial_x^2)\psi_\epsilon
 =-2c\alpha_\epsilon(1+t)a^2.                  \tag{5.5}
\]

This is a consistency control, not a convergence proof.

<a id="section-6-theorem"></a>
## 6. Fixed-domain nonlinear `O(a^2)` theorem

Assume that a solution of (3.4) is supplied with

\[
 \psi\in C^2([0,T];C^0(\mathbb T_L;\mathbb R^8))
 \cap C^0([0,T];C^6_{\rm per}(\mathbb T_L;\mathbb R^8)),        \tag{6.1}
\]

and

\[
 \|\psi\|_{L^\infty([0,T]\times\mathbb T_L;\ell^\infty_8)}
 \le R_0<R.                                      \tag{6.2}
\]

Let

\[
 e=\psi^a-R_a\psi,
\]

and fix `alpha>0`.  Suppose the initial lattice data obey

\[
 E_\alpha(0)^{1/2}\le C_{\rm init}a^2,          \tag{6.3}
\]

where exact sampled initial data give `C_init=0` and

\[
 E_\alpha={\chi\over2}\|e_t\|_a^2
 +{c\over2}\|D_a^+e\|_a^2
 +{\alpha\over2}\|e\|_a^2.                    \tag{6.4}
\]

Define

\[
 M_k=\sup_{0\le t\le T,\ x\in\mathbb T_L}
 |\partial_x^k\psi(t,x)|_{\mathbb R^8}.
\]

### Theorem CL8-SD

There are `a_*>0` and `C_T<infinity`, independent of `a`, such that for every
admitted `a<=a_*`,

\[
 \sup_{0\le t\le T}E_\alpha(t)^{1/2}\le C_Ta^2.                \tag{6.5}
\]

In particular,

\[
 \sup_{0\le t\le T}
 \left(
 \|e_t\|_a+\|D_a^+e\|_a+\|e\|_a
 \right)\le C'_{T,L,\psi}a^2.                 \tag{6.6}
\]

This is a weighted discrete `H1_a x L2_a` result.  It is not a claim about
piecewise-linear reconstruction in continuous `H1`, whose derivative
interpolation error is generally only first order.

### Proof

Let

\[
 \tau_a=\Delta_aR_a\psi-R_a\psi_{xx}.
\]

Equations (5.1) and (3.1) give

\[
 \|\tau_a(t)\|_a\le a^2C_{\rm res}(a),
\]

\[
 C_{\rm res}(a)=\sqrt{L/8}
 \left({M_4\over12}+{a^2M_6\over360}\right).  \tag{6.7}
\]

Fix `a_bar` and use the `a`-independent upper bound

\[
 C_{\rm res}^*=\sqrt{L/8}
 \left({M_4\over12}+{\bar a^2M_6\over360}\right).              \tag{6.8}
\]

Subtracting the sampled continuum equation from (3.5) gives

\[
 \chi e_{tt}-c\Delta_ae+
 \{\nabla W(\psi^a)-\nabla W(R_a\psi)\}
 =c\tau_a.                                      \tag{6.9}
\]

On the bootstrap interval where both fields lie in the component max ball of
radius `R`, the symmetric Hessian row bound from the Goursat certificate gives

\[
 |\nabla W(z)-\nabla W(y)|_{\mathbb R^8}
 \le\ell_R|z-y|_{\mathbb R^8},
\]

\[
 \ell_R=|r|+(3g+36\lambda)R^2.                 \tag{6.10}
\]

Periodic summation by parts yields the exact identity

\[
 E_\alpha'=-\langle\nabla W(\psi^a)-\nabla W(R_a\psi),e_t\rangle_a
 +c\langle\tau_a,e_t\rangle_a
 +\alpha\langle e,e_t\rangle_a.               \tag{6.11}
\]

The first and third terms are bounded using the three positive pieces of
(6.4).  For the residual term, write it as the product of
`sqrt(chi/2)||e_t||` and `c sqrt(2/chi)||tau_a||`, then apply `AB<=(A^2+B^2)/2`.
This gives

\[
 E_\alpha'\le\Gamma_RE_\alpha
 +{c^2\over\chi}\|\tau_a\|_a^2,               \tag{6.12}
\]

with the explicit safe value

\[
 \Gamma_R=2\sqrt{\alpha/\chi}
 +{2\ell_R\over\sqrt{\alpha\chi}}+{1\over2}. \tag{6.13}
\]

Gronwall and (6.3), (6.8) give

\[
 E_\alpha(t)\le e^{\Gamma_Rt}C_{\rm init}^2a^4
 +{c^2\over\chi}{e^{\Gamma_Rt}-1\over\Gamma_R}
 (C_{\rm res}^*)^2a^4.                         \tag{6.14}
\]

Thus (6.5) holds with

\[
 C_T^2=e^{\Gamma_RT}C_{\rm init}^2
 +{c^2\over\chi}{e^{\Gamma_RT}-1\over\Gamma_R}
 (C_{\rm res}^*)^2.                            \tag{6.15}
\]

It remains to close the radius bootstrap.  The physical grid norm obeys the
uniform one-dimensional inequality

\[
 \|u\|_{\ell^\infty}
 \le C_S(L)\|u\|_{H_a^1},
 \qquad C_S(L)=\sqrt{8(L+L^{-1})}.              \tag{6.16}
\]

Also,

\[
 \|e\|_{H_a^1}
 \le\sqrt{2(\alpha^{-1}+c^{-1})}\,E_\alpha^{1/2}.              \tag{6.17}
\]

Choose `a_*<=a_bar` so that

\[
 C_S(L)\sqrt{2(\alpha^{-1}+c^{-1})}C_Ta_*^2<R-R_0.             \tag{6.18}
\]

If the maximal bootstrap interval ended before `T`, (6.5)--(6.18) would keep
the solution strictly inside the radius-`R` ball at that endpoint, a
contradiction.  This proves (6.5) on the whole fixed interval.

<a id="section-7-tail"></a>
## 7. Honest regulator-tail corollary

Let `K_a(t)` be any set of grid nodes on which the supplied continuum solution
vanishes.  Restriction cannot increase the weighted norm, so

\[
 \|\psi^a(t)\|_{L_a^2(K_a(t))}
 =\|e(t)\|_{L_a^2(K_a(t))}
 \le\|e(t)\|_a\le C a^2.                       \tag{7.1}
\]

For smooth compactly supported continuum Cauchy data, the inserted continuum
wave equation has finite propagation.  Before periodic wraparound, a compact
set a positive distance outside that continuum cone supplies an instance of
`K_a(t)`.

Equation (7.1) is only aggregate weighted `L2` disappearance for a matched
smooth Cauchy family.  It is not a pointwise, exponential, operator-norm,
arbitrary-frequency, or exact-support bound.  Separately, the registered
finite-`a` strict-cone theorem retains its particular nonzero variational
witness channels at every fixed `a`.  Equation (7.1) neither proves nor
requires a nonzero tail for each matched smooth datum.

Nothing in (7.1) composes Goursat boundary traces with the lattice.

<a id="section-8-arb"></a>
## 8. Rigorous one-mode regression

The primary script uses `python-flint` Arb at 160-bit precision, with no time
stepper.  At the zero background the positive `g` and `lambda` quartics have
zero Hessian, so one spatial Fourier variation with

```text
L=2*pi, chi=c=r=1, xi(0,x)=cos(x), xi_t(0,x)=0, T=1/2
```

has the exact semidiscrete frequency

\[
 k_a={2\sin(a/2)\over a},\qquad
 \omega_a=\sqrt{1+k_a^2}.
\]

The exact-time error is

\[
 e_M=\cos(\omega_aT)-\cos(\sqrt2T).
\]

For `M=16,32,64,128,256`, Arb certifies that every error interval is positive
and strictly decreases, every successive ratio lies in `(3.97,4.01)`, and

\[
 \left|{e_{256}\over a_{256}^2}
 -{\sin(\sqrt2/2)\over48\sqrt2}\right|<10^{-5}.                \tag{8.1}
\]

The non-importing implementation derives the coefficient in (8.1) from the
exact Fourier series with rational arithmetic.  This regression isolates the
spatial consistency order.  It does not prove the nonlinear theorem; the
modified-energy argument in Section 6 does.

<a id="section-9-composition"></a>
## 9. Open composition and quantum boundary

The continuum Goursat package maps compatible traces to a continuum slice.
This package assumes a smooth continuum Cauchy solution and matched lattice
Cauchy data.  No theorem yet proves that the first output supplies the second
input with all of the following properties:

- a common periodic domain and boundary convention;
- `C6` spatial regularity and an `a`-uniform max ball;
- the required sampling and reconstruction maps;
- convergence of continuum and lattice energy and symplectic forms;
- convergence of a supplied classical measure;
- one selected quantum state on both sides;
- a moving-characteristic boundary or ghost-value prescription.

Until those are proved, there is no boundary-to-lattice state theorem and no
CP1 completion.

## 10. Devil's-advocate review

1. **A convergence slope from five grids is not a theorem.**
   **DISMISSED.**  Section 6 is the analytic proof.  Arb is labelled only as a
   one-mode regression.
2. **Negative `r` makes the physical error energy indefinite.**
   **MITIGATED.**  The proof uses the positive modified error energy (6.4),
   while (4.9) separately gives global finite-ODE control.
3. **The nonlinear Lipschitz constant could depend on `a`.**
   **DISMISSED under the stated hypotheses.**  It is the explicit Q3 max-ball
   constant (6.10), and the discrete Sobolev bootstrap closes the same `R` for
   all sufficiently small `a`.
4. **Piecewise-linear `H1` error is generally only first order.**
   **UPHELD.**  The theorem is explicitly restricted to the weighted discrete
   `H1_a` phase norm.
5. **Global `L2` convergence does not prove pointwise causal tails.**
   **UPHELD.**  Section 7 states only an aggregate conditional corollary.
6. **The fixed periodic Cauchy theorem is not a moving-null Goursat scheme.**
   **UPHELD.**  The missing boundary composition is a named route gate.
7. **The result could be mistaken for quantum regulator removal.**
   **UPHELD and excluded.**  The theorem is classical, smooth-data,
   fixed-domain, and fixed-time only.

## 11. Reproduction

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_semidiscrete_cauchy_oa2.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_semidiscrete_cauchy_oa2_independent.py --selftest
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_semidiscrete_cauchy_oa2_verify.py
```

The primary script uses SymPy for exact Hamiltonian and consistency identities
and Arb for the rigorous mode enclosure.  The independent script imports
neither primary code nor symbolic/numerical regression machinery; it rebuilds
the finite matrices, factorial coefficients, and asymptotic multiplier with
`Fraction`.  The integrated verifier reruns both, compares exact results,
audits scope and composition flags, and matches fresh output to stored JSON.

## 12. No-overclaim boundary

This package proves a fixed-domain, fixed-time smooth classical Cauchy
semidiscretization theorem in a weighted discrete norm.  It does not prove an
exact finite-`a` cone, a semidiscrete Goursat problem, pointwise or exponential
tails, convergence for nonsmooth or arbitrary lattice-frequency data,
continuous piecewise-linear `H1 O(a^2)`, growing-time or thermodynamic
uniformity, full `3+1` or quantum regulator removal, a boundary-to-lattice
state map, physical empty space, a below-empty-space sign, cooling, gravity,
CP1, or Pre-A.
