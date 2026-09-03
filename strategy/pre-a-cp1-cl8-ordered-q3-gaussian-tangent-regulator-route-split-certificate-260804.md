# Pre-A CP1 CL8 ordered-Q3 Gaussian tangent regulator route split

**Candidate:** `PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-SPECTRAL-GAUSSIAN-PROJECTIVE-FAMILY-HADAMARD-COMPARATOR-BARE-CRITICAL-SPEED-CENTERED-PROJECTIVITY-AND-CRITICAL-ZERO-MODE-NOGOS`  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE`  
**Authority:** claim-nonbearing `T0`, quadratic-tangent scope  
**Date:** 2026-08-04

<a id="section-1-verdict"></a>
## 1. Verdict

This checkpoint closes a real but deliberately narrow part of the Pre-A state
and critical-boundary programme.

For the actual Q3-locked ordered well, it proves:

1. the exact eight-branch Q3 Hessian spectrum;
2. the Fourier canonical normalization forced by the inherited `a/8`
   symplectic weight;
3. an exact projective Gaussian ground-state family for a continuum-symbol
   spectral cutoff;
4. identification of its direct-limit state with a standard massive Hadamard
   ground-state comparator on the inserted flat `1+1` cylinder;
5. fixed-finite-mode and fixed-finite-time `O(a^2)` convergence of the actual
   centered CL8 quadratic states to that comparator;
6. the bare Gaussian critical exponents `nu_corr=1/2`, `z=1`, and the common
   tangent speed `v_bare=sqrt(c/chi)`; and
7. two exact obstructions: natural exact projectivity of the centered states,
   and a normalizable full compact Gaussian ground at the critical zero mode.

It does **not** prove that the exact interacting ground or Gibbs states converge.
It does not prove that the full nonlinear history-cut state is compatible across
regulators.  It does not derive physical light, a Lorentz cone, a phase
transition, a physical vacuum, or Pre-A.

<a id="section-2-authorities-and-prior-art"></a>
## 2. Authorities and prior-art boundary

The exact Q3 potential and ordered Hessian convention come from
`PA-CP1-ST8-Q3LOCK-v0`.  The centered one-dimensional Hamiltonian and its
`a/8` phase-space weight come from
`PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0` and
`PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0`.  The earlier Gaussian CCR
and finite-image comparison is `PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0`.
Fixed-regulator cut transport is owned by
`PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0`.

Fourier diagonalization of harmonic lattices, quasi-free CCR states, spectral
cutoffs, Gaussian critical scaling, and massless scalar zero-mode problems are
standard mathematics.  The massive ground-state Hadamard property is imported
from the static-spacetime theorem of
[Fulling, Narcowich and Wald (1981)](https://doi.org/10.1016/0003-4916(81)90098-1),
with an additional static-ground/KMS formulation in
[Junker (1995)](https://arxiv.org/abs/hep-th/9507097).
The compact massless zero-mode interpretation is consistent with the explicit
Einstein-cylinder analysis of
[Alonso-Serrano et al. (2021)](https://arxiv.org/abs/2108.07274).

No new general theorem and no world-first claim is made.  The repository-specific
content is the exact composition of those tools with the Q3 ordered Hessian,
the CL8 normalization, the spectral-versus-centered regulator split, and the
Pre-A gate audit.

<a id="section-3-model-and-scope"></a>
## 3. Model and scope

Work on a periodic circle of fixed circumference `L`, with even

\[
 M={L\over a}.
\]

The field has a spatial node `j` and a Q3 species label
`e in {0,1}^3`.  The admitted domain is

\[
 L,\chi,c,g,\hbar>0,\qquad \lambda\ge 0,\qquad r<0.
\]

The two common-sign ordered configurations are

\[
 q^*_{j,e}=\sigma v,
 \qquad \sigma\in\{+1,-1\},
 \qquad v^2=-{r\over g}.                                    \tag{3.1}
\]

For `lambda>0`, Q3 connectivity makes these the two global classical minima.
For `lambda=0`, additional independent sign wells return; the Hessian at either
common-sign well below remains valid.

Write

\[
 q_{j,e}=q^*_{j,e}+\varphi_{j,e}.
\]

Every state in this certificate is a state of the quadratic Hessian Hamiltonian
in `varphi`.  It is not the exact ground of the quartic finite-volume
Hamiltonian.  In particular, the exact finite-volume ground remains unique and
global-Z2 even, whereas choosing one Hessian well is an inserted comparison
choice.

<a id="section-4-exact-q3-ordered-hessian"></a>
## 4. Exact Q3 ordered Hessian

Let `L_Q3` be the graph Laplacian of the cube.  Its Walsh characters are

\[
 \chi_\alpha(e)=(-1)^{\alpha\cdot e},
 \qquad \alpha\in\{0,1\}^3.                                \tag{4.1}
\]

If `s=|alpha|`, then

\[
 L_{Q3}\chi_\alpha=2s\chi_\alpha.                          \tag{4.2}
\]

The eigenvalues `0,2,4,6` have multiplicities `1,3,3,1`.

For one Q3 edge `{e,f}`, the locking polynomial has the ordered expansion

\[
 {\lambda\over4}(q_e-q_f)^2(q_e^2+q_f^2)
 = {\lambda v^2\over2}(\varphi_e-\varphi_f)^2
   +O(\varphi^3).                                           \tag{4.3}
\]

The onsite Hessian is `-2r`.  Therefore the complete species Hessian is

\[
 K_*=(-2r)I_8+\lambda v^2L_{Q3}.                            \tag{4.4}
\]

On the Walsh branch `s`, its stiffness is

\[
 \begin{aligned}
 \nu_s
   &= -2r+2s\lambda v^2\\
   &= -2r\left(1+s{\lambda\over g}\right)>0,
 \end{aligned}                                               \tag{4.5}
\]

again with multiplicities `1,3,3,1`.  The extra factor two in (4.5) is the
Q3 Laplacian eigenvalue; it is not an additional edge-Hessian factor.

<a id="section-5-canonical-mode-normalization"></a>
## 5. Canonical mode normalization

The inherited phase-space weight and canonical nodal momentum are

\[
 w={a\over8},
 \qquad p_{j,e}=w\Pi_{j,e},
 \qquad [q_{j,e},p_{k,f}]=i\hbar\delta_{jk}\delta_{ef}.      \tag{5.1}
\]

For even `M`, choose the centered representatives

\[
 I_M=\{-M/2,-M/2+1,\ldots,M/2-1\},
 \qquad k_n={2\pi n\over L}.                               \tag{5.2a}
\]

All Fourier indices below are understood modulo `M`.  Reality pairs `n` with
`-n` modulo `M`; the representative `n=-M/2` is the self-conjugate Nyquist
mode.  Take the orthonormal spatial/Q3 transform

\[
 y_{n\alpha}
 ={1\over\sqrt{8M}}
 \sum_{j,e}e^{-ik_nx_j}\chi_\alpha(e)\varphi_{j,e},         \tag{5.2}
\]

and the same transform of `p`, denoted `p_(n alpha)`.  The necessary
continuum-normalized canonical variables are

\[
 \boxed{\Phi_{n\alpha}=\sqrt{a\over8}\,y_{n\alpha}},
 \qquad
 \boxed{P_{n\alpha}=\sqrt{8\over a}\,p_{n\alpha}}.         \tag{5.3}
\]

The scaling factors multiply to one, so

\[
 [\Phi_{n\alpha},P_{m\beta}]
 =i\hbar\delta_{\alpha\beta}\delta^{(M)}_{n+m,0}.          \tag{5.4}
\]

Here `delta^(M)` is the modular Kronecker delta.  The complex notation is only
shorthand for the real zero coordinate, the real cosine/sine pairs, and the
one real Nyquist coordinate; it does not double count a physical oscillator.

The centered symbol is

\[
 \widehat k_a(n)^2
 ={4\over a^2}\sin^2\left({k_na\over2}\right).            \tag{5.5}
\]

After (5.3), each real oscillator has mass `chi`, not `chi*a/8`, and

\[
 H_a^{(2)}={1\over2}\sum_{n,\alpha}
 \left[
 {P_{-n,\alpha}P_{n,\alpha}\over\chi}
 +\left(\nu_\alpha+c\widehat k_a(n)^2\right)
  \Phi_{-n,\alpha}\Phi_{n,\alpha}
 \right].                                                    \tag{5.6}
\]

Thus

\[
 \boxed{
 \omega_{a,n,\alpha}^2
 ={\nu_\alpha+c\widehat k_a(n)^2\over\chi}}
 .                                                           \tag{5.7}
\]

The ordered-tangent Gaussian covariances are

\[
 C^\Phi_{a,n,\alpha}
 ={\hbar\over2\chi\omega_{a,n,\alpha}},
 \qquad
 C^P_{a,n,\alpha}
 ={\hbar\chi\omega_{a,n,\alpha}\over2},                   \tag{5.8}
\]

with zero symmetrized cross covariance and

\[
 C^\Phi C^P={\hbar^2\over4}.                                \tag{5.9}
\]

<a id="section-6-spectral-projective-state-theorem"></a>
## 6. Spectral projective state theorem

Define the continuum frequencies

\[
 \omega_{0,n,\alpha}^2
 ={\nu_\alpha+ck_n^2\over\chi}.                             \tag{6.1}
\]

Let `V_K` be the real symplectic direct sum containing, for all eight Walsh
species, the zero cosine coordinate and the cosine/sine pairs for
`1<=n<=K`.  For `K' >= K`, let

\[
 j_{K'\leftarrow K}:V_K\longrightarrow V_{K'}               \tag{6.2}
\]

pad the missing modes by zero.  It is symplectic and induces the typed Weyl
monomorphism

\[
 \iota_{K'\leftarrow K}(W_K(F))
 =W_{K'}(j_{K'\leftarrow K}F).                              \tag{6.3}
\]

Use the convention

\[
 W(f,g)=\exp\left[{i\over\hbar}
 \sum(fP-g\Phi)\right].                                    \tag{6.4}
\]

Define

\[
 \omega_K(W(f,g))
 =\exp\left[-{1\over4\hbar}
 \sum_{|n|\le K,\alpha}
 \left(
 \chi\omega_{0,n,\alpha}f_{n\alpha}^2
 +{g_{n\alpha}^2\over\chi\omega_{0,n,\alpha}}
 \right)\right],                                           \tag{6.5}
\]

with the usual real-mode counting.  Positivity is the standard oscillator
Gaussian positivity, and strict positive frequency makes every finite
restriction regular.

### Theorem 6.1 -- exact spectral projectivity

For all `K' >= K`,

\[
 \boxed{
 \omega_{K'}\circ\iota_{K'\leftarrow K}=\omega_K}.
                                                                    \tag{6.6}
\]

### Proof

Every term in (6.5) belonging to an old mode is independent of the cutoff.
The embedding (6.2) gives every newly added coordinate coefficient zero.
Therefore the quadratic exponent on the embedded label is exactly the old
quadratic exponent.  This proves (6.6) generator by generator and hence on the
finite Weyl algebra.  Composition of zero-padding embeddings is exact, so the
identity is coherent for every triple of cutoffs.  `QED`

This is a restriction identity of algebraic states.  It is not an untyped
density-matrix partial trace.  It also uses the continuum symbol `k_n^2`; it is
not yet a theorem about the inherited centered nodal regulator.

The compatible states define a state on the inductive-limit Weyl algebra of
finite Fourier test data.  The positive **frequency operator** is

\[
 \Omega=\left[\chi^{-1}(-c\partial_x^2+K_*)\right]^{1/2}.    \tag{6.7}
\]

It is not itself a covariance.  With phase-space order `(Phi,P)`, the
equal-time symmetrized Cauchy covariance block is

\[
 \Gamma={\hbar\over2}
 \begin{pmatrix}
  (\chi\Omega)^{-1}&0\\[2pt]
  0&\chi\Omega
 \end{pmatrix}.                                             \tag{6.8}
\]

This is not merely a formal dense-union identification.  On the compact circle,
`omega_(0,n,alpha)` grows linearly in `|n|`, while strict mass positivity bounds
its inverse at `n=0`.  The two quadratic covariance forms are therefore
continuous on smooth Cauchy data in the usual Frechet topology.  They extend
uniquely from finite Fourier data to the smooth-data Weyl algebra, and the
extension has exactly (6.8).  Its spacetime two-point distribution in species
`alpha` is

\[
 W_\alpha(t,x;t',x')={\hbar\over2\chi L}
 \sum_{n\in\mathbb Z}{
  e^{-i\omega_{0,n,\alpha}[(t-t')-i0]+ik_n(x-x')}
  \over \omega_{0,n,\alpha}}.                               \tag{6.9}
\]

Every finite-mode restriction of (6.8)--(6.9) is exactly `omega_K`; conversely,
Fourier truncations converge to these objects as quadratic forms and
distributions on smooth test data.  This is the explicit bridge from the
finite projective family to the smooth Cauchy and spacetime state used below.

<a id="section-7-hadamard-comparator"></a>
## 7. Hadamard comparator

In the Walsh basis, (6.7) is the direct sum of eight strictly massive scalar
operators.  To compare it with the standard Klein--Gordon theorem, insert the
flat ultrastatic cylinder

\[
 ds^2=-dt^2+{\chi\over c}\,dx^2,
 \qquad x\sim x+L,                                          \tag{7.1}
\]

whose proper spatial circumference is `sqrt(chi/c)*L`, and rescale each Walsh
field by

\[
 \phi_\alpha=(\chi c)^{1/4}\Phi_\alpha,
 \qquad m_\alpha^2={\nu_\alpha\over\chi}.                  \tag{7.2}
\]

The standard Klein--Gordon action on (7.1) then reproduces the quadratic
coefficients `chi`, `c`, and `nu_alpha`, and (6.9) is its positive-frequency
ground-state two-point distribution.  The metric, time coordinate, and this
geometric interpretation are inserted comparator data; they are not derived
from CL8.

### Corollary 7.1 -- massive ordered-tangent Hadamard comparator

For `r<0`, the direct-limit state of Section 6 is Hadamard.

### Justification

Equation (4.5) makes the spatial operator strictly positive.  The background is
smooth, static, globally hyperbolic, and spatially compact.  The state is the
standard static ground state for that operator.  These are the hypotheses of
the established static massive scalar ground-state Hadamard theorem cited in
Section 2.  A finite orthogonal Q3 change of basis and a finite direct sum do not
add wavefront directions.  `QED`

This imports the microlocal theorem; the new executable does not pretend to
derive wavefront-set calculus numerically.  The repository contribution is the
exact match of the Q3/CL8 operator to the theorem's inputs.

The corollary certifies only a **free ordered-tangent comparator**.  A finite
lattice state is not itself called Hadamard.  No Hadamard property is inferred
for the nonlinear CL8 ground, Gibbs state, cut-transported state, or critical
zero-mode theory.

<a id="section-8-centered-fixed-mode-limit"></a>
## 8. Centered fixed-mode limit

For `|k a|<=pi`, the elementary sine estimates give

\[
 0\le k^2-\widehat k_a^2
 \le {a^2k^4\over12}.                                      \tag{8.1}
\]

The exact expansion is

\[
 \widehat k_a^2
 =k^2-{a^2k^4\over12}+{a^4k^6\over360}
  -{a^6k^8\over20160}+O(a^8).                              \tag{8.2}
\]

Put

\[
 m_\alpha=\sqrt{\nu_\alpha\over\chi}>0.                  \tag{8.3}
\]

Rationalizing the square roots and using (8.1) yields

\[
 0\le\omega_{0,n,\alpha}-\omega_{a,n,\alpha}
 \le {ca^2k_n^4\over24\chi m_\alpha},                     \tag{8.4}
\]

\[
 0\le C^\Phi_{a,n,\alpha}-C^\Phi_{0,n,\alpha}
 \le {\hbar ca^2k_n^4\over48\chi^2m_\alpha^3},            \tag{8.5}
\]

and

\[
 0\le C^P_{0,n,\alpha}-C^P_{a,n,\alpha}
 \le {\hbar ca^2k_n^4\over48m_\alpha}.                    \tag{8.6}
\]

For any fixed finite set of real modes, summing (8.5)--(8.6) gives an `O(a^2)`
bound on the difference of Gaussian characteristic exponents for every fixed
Weyl label.  The bound is uniform when those labels range over a bounded subset
of that finite-dimensional label space.  Hence the centered Gaussian states
converge weak-star on each fixed finite-mode Weyl algebra to the
spectral/Hadamard comparator.  No uniformity over unbounded Weyl labels is
claimed.

The positive-frequency coefficient at time separation `tau` is

\[
 C^\Phi_a e^{-i\omega_a\tau}.
\]

The elementary inequality

\[
 \left|C^\Phi_a e^{-i\omega_a\tau}
       -C^\Phi_0 e^{-i\omega_0\tau}\right|
 \le |C^\Phi_a-C^\Phi_0|
     +C^\Phi_0|\tau|\,|\omega_a-\omega_0|                  \tag{8.7}
\]

therefore gives `O(a^2)` convergence for fixed labels, uniformly on bounded
label subsets, on a fixed mode set and compact time-separation interval.

This is a cylindrical finite-mode result.  It is not uniform over modes that
grow with the cutoff, through `r=0`, in total zero-point energy, or for the
interacting state.

<a id="section-9-centered-projectivity-no-go"></a>
## 9. Centered projectivity no-go

Compare spacing `a` with spacing `a/2` at fixed `L`, using the natural identity
of the shared normalized Fourier field and momentum generators.  Directly,

\[
 \boxed{
 \widehat k_{a/2}^2-\widehat k_a^2
 ={16\over a^2}\sin^4\left({ka\over4}\right)}.             \tag{9.1}
\]

For every shared nonzero, non-Nyquist mode

\[
 0<|n|<{M\over2},                                           \tag{9.2}
\]

the right side is positive.  Consequently, for `c>0`,

\[
 \omega_{a/2,n,\alpha}>\omega_{a,n,\alpha},                \tag{9.3}
\]

\[
 C^\Phi_{a/2,n,\alpha}<C^\Phi_{a,n,\alpha},
 \qquad
 C^P_{a/2,n,\alpha}>C^P_{a,n,\alpha}.                      \tag{9.4}
\]

One real cosine or sine quadrature already distinguishes the characteristic
functions.  Therefore

\[
 \boxed{
 \omega^{\rm lat}_{a/2}\circ\iota^{\rm natural}_{a/2\leftarrow a}
 \ne\omega^{\rm lat}_{a}}.                                 \tag{9.5}
\]

An exact rational-trigonometric witness avoids the Nyquist subtlety:

\[
 L=6,\quad M=6,\quad n=2,
\]

gives

\[
 \widehat k_a^2=3,
 \qquad \widehat k_{a/2}^2=4.                              \tag{9.6}
\]

This registers
`NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY`.
It rejects only natural exact state equality for the centered ground states.
It does not reject the `O(a^2)` limit, spectral regulator, mode-dependent
symplectic squeeze, perfect action, counterterm family, or interacting
renormalized construction.

<a id="section-10-bare-critical-scaling-and-speed"></a>
## 10. Bare critical scaling and speed

Write `rho=-r>0`.  Equation (4.5) becomes

\[
 \nu_s=2\rho\left(1+s{\lambda\over g}\right).              \tag{10.1}
\]

The Gaussian correlation length and zero-momentum gap are

\[
 \xi_s=\sqrt{c\over\nu_s}
 \propto\rho^{-1/2},
 \qquad
 \Delta_s=\sqrt{\nu_s\over\chi}
 \propto\rho^{1/2}.                                        \tag{10.2}
\]

Thus the **bare tangent** exponents are

\[
 \nu_{\rm corr}^{\rm bare}={1\over2},
 \qquad z_{\rm bare}=1,                                   \tag{10.3}
\]

because

\[
 \Delta_s\xi_s=\sqrt{c\over\chi}.                         \tag{10.4}
\]

All eight masses vanish as `r` approaches zero from below.  At the critical
quadratic level and nonzero continuum momentum,

\[
 \omega_s(k)=v_{\rm bare}|k|,
 \qquad
 \boxed{v_{\rm bare}=\sqrt{c\over\chi}}.                   \tag{10.5}
\]

The same value is the large-`|k|` limiting group and phase speed of every
massive continuum branch.

This is a structural clue, not physical light.  The equality follows because
the candidate starts with one species-independent inertia coefficient `chi`
and one species-independent principal gradient coefficient `c`.  Q3 symmetry
alone permits additional Q3-invariant derivative operators, and no loop, RG,
regulator, Lorentz, or physical-cone protection theorem has been shown.

At finite centered spacing and on the positive Brillouin branch,

\[
 \omega_a(k)=v_{\rm bare}{2\over a}\sin{ka\over2},
 \qquad
 {d\omega_a\over dk}
 =v_{\rm bare}\cos{ka\over2}.                              \tag{10.6}
\]

The group velocity reaches zero at the Brillouin boundary.  The finite lattice
does not carry one constant speed at all wave numbers.

Finally, the Hessian bifurcation and (10.3) are not a proof of a thermodynamic
or quantum phase transition.  They are tree-level Gaussian scaling data.  The
finite interacting model still has one even ground state.

<a id="section-11-critical-zero-mode-no-go"></a>
## 11. Critical compact zero-mode no-go

At `r=0`, the ordered amplitude and every stiffness vanish:

\[
 v=0,
 \qquad \nu_s=0.                                           \tag{11.1}
\]

For the spatial zero mode, the quadratic Hamiltonian is

\[
 H_{0,s}={P_{0,s}^2\over2\chi}.                             \tag{11.2}
\]

This is the free particle on the real line.  Its zero-energy solutions are
affine functions, none of which is a nonzero `L2(R)` vector.  Equivalently,

\[
 C^\Phi_{0,s}
 ={\hbar\over2\sqrt{\chi\nu_s}}\longrightarrow+\infty,
 \qquad
 C^P_{0,s}\longrightarrow0.                                \tag{11.3}
\]

Along any nonzero Weyl label coupled to the zero-mode field, the Gaussian
characteristic function tends to zero, while its value at label zero remains
one.  The limiting functional is not regular.

Therefore the full periodic quadratic tangent has no normalizable Gaussian
ground at criticality, and the massive ground family has no regular
full-field ground-state limit through `r=0`.  This registers
`NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND`.

The no-go does not reject the exact quartic finite-volume ground, a squeezed or
non-ground zero-mode prescription, decompactification, constraints, a compact
target field, or a deliberately reduced mean-zero algebra.  Those are
different theories or state-selection inputs and must be tested separately.

<a id="section-12-history-cut-composition-boundary"></a>
## 12. History-cut composition boundary

At each fixed finite centered regulator, the quadratic Gaussian density can be
inserted into the already proved cut transport theorem.  If

\[
 \Gamma_{a,C}^{[n]}:\mathcal H_{a,C}\to\mathcal H_a
\]

is the typed phase anchor, then a density `rho_(a,n)` defines

\[
 \rho_{a,C}^{[n]}
 =\Gamma_{a,C}^{[n]*}\rho_{a,n}\Gamma_{a,C}^{[n]}.          \tag{12.1}
\]

Same-time re-slicing and physical-step covariance follow from the registered
fixed-`a` diagrams.  But three facts prevent promotion to the parent
inter-regulator history-state gate:

1. the natural centered Gaussian states already fail exact projectivity by
   Section 9;
2. no square between coarse/fine embeddings and every typed `Lambda_C` or
   `Gamma_C` decoder has been proved; and
3. the full nonlinear D-K-D unitary generally transports a Gaussian into a
   non-Gaussian state, which need not be stationary for either the unchanged
   tangent Hamiltonian or the interacting Hamiltonian.

The exact spectral family of Section 6 is a bulk free comparator, not a
substitute for that missing nonlinear cut square.

<a id="section-13-input-output-ledger"></a>
## 13. Input/output ledger

### Inputs

- the one-dimensional periodic background and its time coordinate;
- `L, chi, c, g, lambda, r`, and the regulator family;
- the Q3 locking polynomial and one ordered well;
- `hbar` and the ground-state criterion;
- the common species principal coefficients;
- the continuum static metric used by the Hadamard theorem.

### Derived outputs

- the Q3 stiffnesses and their multiplicities;
- the exact canonical Fourier normalization;
- the centered and spectral dispersions and Gaussian covariances;
- exact spectral projectivity;
- the standard massive Hadamard comparator identification;
- explicit centered fixed-mode convergence bounds;
- the exact centered projectivity witness;
- bare critical exponents and common tangent speed;
- the critical compact zero-mode obstruction.

### Not derived

- time, `hbar`, physical light speed, or Lorentzian signature;
- a loop- or RG-protected cone;
- the interacting continuum or Hadamard state;
- the original `3+1` Q3 parent;
- phase-transition dynamics, cooling, gravity, or a horizon;
- a physical vacuum, empty-space reference, or below-empty-space sign.

<a id="section-14-adversarial-review"></a>
## 14. Adversarial review

### Objection 1: the lock Hessian has an extra factor two

**DISMISSED.**  Equation (4.3) fixes the edge quadratic coefficient.  The only
factor two in (4.5) comes from the cube eigenvalue `2s`.  Both primary and
independent graph implementations verify every Walsh eigenvector.

### Objection 2: the `a/8` weight was lost in the continuum variables

**DISMISSED.**  Equation (5.3) is a symplectic rescaling whose two factors
multiply to one.  Substitution independently gives oscillator kinetic term
`P^2/(2chi)` and potential term `(nu+c khat^2)Phi^2/2`.

### Objection 3: spectral projectivity proves centered projectivity

**UPHELD AS A FIREWALL.**  It does not.  The spectral cutoff uses `k_n^2`; the
centered Hamiltonian uses `khat_a(n)^2`.  Section 9 proves the latter states are
not naturally exactly projective.

### Objection 4: the Nyquist convention creates the no-go

**DISMISSED.**  The exact witness `M=6,n=2` satisfies `0<n<M/2`; it is not a
Nyquist mode.  One real quadrature suffices.

### Objection 5: fixed-mode convergence is a full UV limit

**UPHELD AS A LIMITATION.**  The constants grow with momentum and with inverse
mass.  No cutoff-uniform energy, stress tensor, partition function, or
interacting weak-star theorem is claimed.

### Objection 6: a finite lattice state is Hadamard

**DISMISSED.**  Hadamard is a microlocal property of the continuum two-point
distribution.  The certified object is the continuum static ground comparator;
finite lattice states merely converge to its fixed-mode restrictions.

### Objection 7: the common speed is the speed of light

**UPHELD AS AN OVERCLAIM.**  It is named `v_bare`, not physical `c_light`.
It follows from inserted equal principal coefficients and lacks loop/RG,
regulator, Lorentz, and `3+1` protection.

### Objection 8: `z=1` proves a physical phase transition

**UPHELD AS AN OVERCLAIM.**  Equations (10.2)--(10.3) are Gaussian Hessian
scaling.  No thermodynamic limit, nonanalytic free energy, interacting
critical exponent, or cooling trajectory has been proved.

### Objection 9: the critical covariance defines a singular but acceptable Fock vacuum

**DISMISSED FOR THE DECLARED TARGET.**  Its characteristic functional is not
regular on the full zero-mode Weyl line and the free particle has no normalized
ground vector.  Alternative IR prescriptions are left open, not silently
identified with the massive ground limit.

### Objection 10: the quadratic state approximates the interacting ground as `a->0`

**UPHELD AS A MISSING THEOREM.**  Cubic and quartic fluctuations around the
ordered well do not disappear merely because the spatial spacing tends to
zero.  Uniform comparison estimates, counterterms, and phase selection are
still absent.

### Objection 11: the history-cut theorem supplies inter-regulator compatibility

**UPHELD AS A MISSING SQUARE.**  It supplies exact transport at each fixed
regulator.  The coarse/fine maps have not been shown to commute with every
typed history and phase decoder.

<a id="section-15-verification"></a>
## 15. Verification

Run:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_ordered_q3_gaussian_tangent_regulator_route_split_verify.py
```

The primary route uses SymPy for exact graph, Hessian, normalization,
trigonometric, series, covariance, critical-limit, and scope checks.  The
independent route imports no SymPy and reconstructs the Q3 spectrum, stiffness
fixture, symplectic scaling, spectral nesting, refinement identity, centered
series, convergence rates, and critical scaling with standard-library integer,
`Fraction`, and floating-point hostile fixtures.  The integrated verifier
reruns both children and audits freshness, records, generated surfaces, parent
hashes, and unchanged C6 status.

<a id="section-16-next-gate"></a>
## 16. Next gate

The parent
`PA-CP1-CL8-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY` remains open for the
interacting theory.  The immediate successor is

`PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY`.

It must either construct or honestly block:

1. renormalized interacting states on a declared regulator family;
2. cutoff-uniform moment, local-energy, and state-compactness estimates;
3. coarse/fine algebra maps and commuting typed cut squares;
4. counterterm and physical-reference conventions;
5. compatibility with the original three-dimensional Q3 parent; and
6. a regulator/loop protection test for the common principal cone.

Until those conditions are met, C0 and N1--N5 remain open, C6 remains at its
existing conditional status, and neither CP1 nor Pre-A is complete.
