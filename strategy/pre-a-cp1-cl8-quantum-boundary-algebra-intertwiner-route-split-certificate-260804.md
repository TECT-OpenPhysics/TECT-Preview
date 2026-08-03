# Pre-A CP1 CL8 quantum boundary-algebra intertwiner route split

**Candidate:** `PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-ORDERED-TANGENT-FINITE-IMAGE-WEYL-STATE-PULLBACK-AND-ROUTE-NOGOS`  
**Authority:** T0 exact restricted finite-image construction and scoped route no-gos; claim-nonbearing  
**Date:** 2026-08-04

<a id="section-1-verdict"></a>
## 1. Verdict

The parent quantum-boundary gate splits rather than closing globally.

There is one exact positive composition.  On the inserted ordered collective
CL8 background, the three real modes `1`, `cos(4x)`, and `sin(4x)` form a
six-dimensional linearized characteristic image with frequencies `(3,5,5)`.
For every even `M>=4`, collective point sampling is injective and exactly
symplectic on this band.  The characteristic-to-slice map followed by sampling
therefore induces an exact Weyl monomorphism into the fixed-regulator bulk
algebra.  Any already constructed interacting ground or Gibbs normal state can
be restricted and pulled back to an exact state on this finite boundary image.

Three larger routes fail exactly:

1. unrestricted point sampling is not an exact Weyl homomorphism;
2. the nonlinear Goursat map cannot act by direct Weyl-generator relabelling;
3. the current centered lattice does not exactly intertwine even the first
   nonzero ordered-tangent continuum mode.

The full interacting boundary algebra, exact dynamics, regulator-compatible
state family, physical state criterion, and continuum/Hadamard limit remain
open.  This closes neither C0 nor N1--N5 and does not complete Pre-A.

<a id="section-2-authorities-and-sign"></a>
## 2. Authorities and the load-bearing sign

The construction composes five existing authorities without promoting any of
them beyond their registered scope:

- the finite-triangle classical CL8 Goursat solution and variational flux;
- the exact ordered collective Q3 reduction and `(3,5,5)` tangent calibration;
- the PA-H1 three-mode characteristic map `P_tau T=S_tau`;
- the classical boundary-to-lattice sampling and `O(a^2)` theorem;
- the fixed-regulator interacting ground and Gibbs normal states.

The classical CL8 convention is

\[
 \Omega_{\rm var}={1\over8}\sum_e\int d\Pi_e\wedge dq_e,
 \qquad
 \Omega_{\rm var}(v,w)={1\over8}\sum_e\int
 (\Pi_{v,e}q_{w,e}-\Pi_{w,e}q_{v,e}).
\]

The quantum CCR convention used here is the negative form

\[
 \sigma=-\Omega_{\rm var},
 \qquad
 W(z)W(w)=e^{-i\sigma(z,w)/(2\hbar)}W(z+w),
 \qquad W(z)^*=W(-z).                         \tag{2.1}
\]

This makes the canonical variables obey `[q,p]=i hbar`.  On the eight-species
collective diagonal, the species sum cancels `1/8` and leaves the scalar
integral used below.  The earlier PA-H1
certificate used the corresponding `dq wedge dp` sign with unit inertia.  Both
the boundary and slice CL8 variational forms are its negative.  For general
`chi`, the canonical-momentum transfer below is the conjugate
`diag(I,chi I) S_PAH1 diag(I,chi^(-1) I)` and remains symplectic.  No sign or
inertia factor is silently moved between the classical flux and the Weyl
phase.

The algebra types are also fixed.  The source is the universal finite-
dimensional Weyl CCR C-star algebra.  The target is the concrete unital
Weyl-generated C-star algebra inside the regular Schrodinger `B(H_a)`.  It is
not silently replaced by `B(H_a)`, the compact operators, or a multiplier
algebra when a dynamics statement is made.

<a id="section-3-ordered-tangent"></a>
## 3. Ordered collective tangent

Take

\[
 r<0,\quad g>0,\quad \lambda\ge0,\quad \chi>0,
 \qquad {c\over\chi}=1,
 \qquad {-2r\over\chi}=9,                    \tag{3.1}
\]

and the collective ordered equilibrium

\[
 \bar\psi_e=v=\sqrt{-r/g},\qquad e=1,\ldots,8. \tag{3.2}
\]

The Q3 edge-lock force vanishes identically on the collective diagonal.  The
onsite curvature at (3.2) is

\[
 r+3gv^2=-2r.
\]

Thus a collective tangent field `eta_e=xi` obeys

\[
 \xi_{tt}-\xi_{xx}+9\xi=0                    \tag{3.3}
\]

on the inserted circle

\[
 L={\pi\over2}.
\]

Because all eight species vary equally, the factor `1/8` in the CL8 continuum
ledger cancels the species sum.  The collective symplectic form is exactly the
ordinary scalar form, not eight times it and not one eighth of it.

Use the orthonormal real modes

\[
 e_0=\sqrt{2/\pi},\qquad
 e_c={2\over\sqrt\pi}\cos4x,\qquad
 e_s={2\over\sqrt\pi}\sin4x.                \tag{3.4}
\]

Equation (3.3) gives the exact frequencies

\[
 \Omega=\operatorname{diag}(3,5,5).          \tag{3.5}
\]

The circle, background, collective sector, and tuning (3.1) are inputs.  This
is an exact tangent theorem after those inputs, not a derivation of them.

<a id="section-4-characteristic-image"></a>
## 4. Exact finite characteristic image

Let `Y=R^6` with coefficient order `(q0,qc,qs,p0,pc,ps)`, where `p` is the
coefficient of the canonical momentum `Pi=chi*xi_t`, not the velocity.  For
`y=(q,p)`, set

\[
 \xi_y(t,x)=\sum_{j=0,c,s}e_j(x)
 \left(q_j\cos\omega_jt+{p_j\over\chi\omega_j}\sin\omega_jt\right). \tag{4.1}
\]

At `tau=pi/4`, let `T(y)` be the two complete null traces of (4.1), and let
`P_tau` reconstruct the final Cauchy phase.  The inherited characteristic
uniqueness theorem gives

\[
 P_\tau T=S_\tau.                             \tag{4.2}
\]

Writing `d=sqrt(2)/2`, the oscillator blocks of `S_tau` are

\[
 S_3=\begin{pmatrix}-d&d/(3\chi)\\-3\chi d&-d\end{pmatrix},
 \qquad
 S_5=\begin{pmatrix}-d&-d/(5\chi)\\5\chi d&-d\end{pmatrix}. \tag{4.3}
\]

Each block has determinant one.  Direct characteristic flux gives

\[
 \sigma_H(Ty,Tz)=\sigma_Y(y,z)
 =\sigma_\Sigma(S_\tau y,S_\tau z).          \tag{4.4}
\]

Hence `B_6=T(Y)` and `P_6=S_tau(Y)` are nondegenerate six-dimensional
symplectic spaces, and `P_tau:B_6->P_6` is an exact symplectic isomorphism.
The Weyl functor gives a star-isomorphism between their Weyl algebras.  In
regular irreducible Schrodinger representations of these finite-dimensional
symplectic spaces, whose Hilbert spaces are infinite-dimensional, it has a
metaplectic unitary implementer, unique only projectively.

This is a finite tangent image.  It is not a Banach-manifold quantization of
the nonlinear global Goursat map and it says nothing about continuum Fock
implementability, which would require a chosen complex structure and a
Shale--Stinespring condition.

<a id="section-5-restricted-sampling"></a>
## 5. Exact restricted finite-regulator sampling

Let `M>=4` be even,

\[
 a={L\over M},\qquad x_j=ja,qquad j=0,\ldots,M-1. \tag{5.1}
\]

Identify the final interval `[-tau,tau)` with `[0,L)` by the exact `M/2`-node
origin shift, which is available because `M` is even.  For a three-mode
collective phase `(q(x),Pi(x))`, define `R_a` by sampling at the nodes and
copying the same value to all eight species.  The lattice CCR form is

\[
 \sigma_a(v,w)={a\over8}\sum_{j,e}
 (q_{v,j,e}\Pi_{w,j,e}-q_{w,j,e}\Pi_{v,j,e}). \tag{5.2}
\]

The species sum again cancels `1/8`.  Products of the functions in (3.4) have
Fourier orders only `0`, `1`, and `2`.  For even `M>=4`, none of the nonzero
product orders is congruent to zero modulo `M`, so the roots-of-unity identity
gives exact trapezoidal orthogonality.  At `M=4`, order two is the Nyquist
order but its grid average is still zero:

\[
 a\sum_{j=0}^{M-1}e_\alpha(x_j)e_\beta(x_j)
 =\int_0^L e_\alpha e_\beta\,dx
 =\delta_{\alpha\beta}.                       \tag{5.3}
\]

Consequently `R_a` is injective on `P_6` and

\[
 \sigma_a(R_av,R_aw)=\sigma_\Sigma(v,w).      \tag{5.4}
\]

Define

\[
 K_a=R_aP_\tau:B_6\longrightarrow V_a.       \tag{5.5}
\]

Equations (4.4) and (5.4) make `K_a` a linear symplectic embedding.  Therefore

\[
 \alpha_a(W_H(b))=W_a(K_ab)                   \tag{5.6}
\]

extends to an injective unital star-homomorphism onto its finite-image Weyl
subalgebra.

The restriction in Section 5 is load-bearing.  It is a one-slice kinematic
map, not an exact continuum-to-lattice evolution theorem.

<a id="section-6-state-pullback"></a>
## 6. Actual interacting bulk-state pullback

For fixed `M`, the earlier quantum package constructed a normal state

\[
 \omega_a(A)=\operatorname{Tr}(\rho_aA)
\]

on `B(H_a)` for either the simple interacting ground projector or any
finite-temperature Gibbs density.  Restrict it to the concrete Weyl-generated
target algebra and define

\[
 \omega_{H,a}=\omega_a\circ\alpha_a.          \tag{6.1}
\]

Because `alpha_a` is a unital star-homomorphism, (6.1) is normalized and
positive.  Normality of the bulk density and strong continuity of the finite
Schrodinger Weyl operators make the restricted boundary state regular.

This is an actual interacting-bulk-state pullback, not the earlier supplied
Gaussian comparator state.  Its observable map is nevertheless only the
ordered-tangent finite image.  No dynamics intertwining is inferred, and the
map does not reconstruct the bulk state's symplectic complement.  Ground and
temperature criteria, `hbar`, and the boundary background remain inputs.  The
construction therefore transports a state but does not select the physical
state.

<a id="section-7-sampling-no-go"></a>
## 7. Unrestricted point-sampling Weyl no-go

The positive band theorem cannot be extended to the full admitted periodic
phase space with the current point sampler.  Let

\[
 f_M(x)=\sin(2\pi Mx/L).                       \tag{7.1}
\]

Every node sample vanishes, but

\[
 \int_0^Lf_M^2dx={L\over2}.                   \tag{7.2}
\]

For one species, take `v_1=(f_M,0)` and `v_2=(0,f_M)` in `(q,Pi)` order.  Then

\[
 \Omega_{\rm var}(v_1,v_2)=-{L\over16},
 \qquad \sigma(v_1,v_2)={L\over16},           \tag{7.3}
\]

while both sampled vectors are zero.  Replace `v_2` by
`(16*pi*hbar/L)v_2`.  The source Weyl commutator is

\[
 e^{-i\sigma(v_1,v_2)/\hbar}=e^{-i\pi}=-1,    \tag{7.4}
\]

but both target generators are the identity and their commutator is `+1`.
Thus

\[
 W_{\rm per}(v)\longmapsto W_a(R_av)           \tag{7.5}
\]

is not an exact Weyl star-homomorphism on the unrestricted source.

This establishes
`NG-2026-08-04-PRE-A-CP1-CL8-OA2-SAMPLING-EXACT-WEYL`.  It does not reject the
restricted band theorem, an opposite-direction symplectic reconstruction, a
new exact characteristic regulator, or an explicitly approximate theorem.
The original form cannot descend directly to the sampling quotient because
the kernel is not even isotropic, much less contained in the radical.

<a id="section-8-nonlinear-relabel-no-go"></a>
## 8. Direct nonlinear Weyl-generator relabelling no-go

Suppose a unital star-homomorphism has the generator form

\[
 \alpha(W(z))=e^{i\theta(z)}W(F(z)).           \tag{8.1}
\]

Assume additionally that the generator-label map `F` is continuous in the
ordinary real phase-space topology, equivalently that the relabelling respects
the regular/strong Weyl parametrization.  Norm continuity of an abstract
C-star homomorphism alone is not used as a substitute for this hypothesis.

Comparing `alpha(W(z)W(w))` with `alpha(W(z))alpha(W(w))` and using uniqueness
of Weyl labels forces

\[
 F(z+w)=F(z)+F(w).                             \tag{8.2}
\]

Continuity makes `F` real-linear.  Comparing commutators forces exact
symplectic preservation; `theta` supplies only the compatible phase character.
Thus a genuinely nonlinear classical map cannot act by (8.1).

The fixed ordered CL8 phase map is genuinely nonlinear.  Write the collective
ordered amplitude as

\[
 v_0=\sqrt{-r/g}
\]

and take collective traces `A=B=v_0+epsilon`.  Let `eta` and `z` be the first
and second `epsilon` derivatives at zero.  The first variation equals one on
both axes, while the second variation has zero axis traces and satisfies

\[
 4\chi z_{u\nu}+(-2r)z=-6gv_0\eta^2.          \tag{8.3}
\]

Here `nu` denotes the second null coordinate and is not the ordered amplitude
`v_0`.  On `nu=0`, equation (8.3) gives

\[
 z_{u\nu}(u,0)=-{3gv_0\over2\chi},
 \qquad
 z_\nu(u,0)=-{3gv_0\over2\chi}u.             \tag{8.4}
\]

Parameterize the final slice by `(u,nu)=(2tau-nu,nu)`.  Because
`z_u(u,0)=0`, its endpoint derivative is

\[
 {d\over d\nu}z(2\tau-\nu,\nu)\big|_{\nu=0}
 =-{3gv_0\tau\over\chi}\ne0.                 \tag{8.5}
\]

Thus the second data derivative of the actual ordered final phase is a
nonzero function for every `tau>0`.  The ordered characteristic-to-phase map
is not affine and cannot satisfy (8.1).

As an independent cubic control, set `r=lambda=0`, take one active species,
and use constant compatible traces `A=B=epsilon`.  The equation is

\[
 4\chi\psi_{uv}+g\psi^3=0.                    \tag{8.6}
\]

At `epsilon=0`, the third derivative
`w=partial_epsilon^3 psi|_0` satisfies

\[
 4\chi w_{uv}+6g=0,
 \qquad w(u,0)=w(0,v)=0,
\]

so

\[
 w(u,v)=-{3g\over2\chi}uv.                    \tag{8.7}
\]

At the final-slice midpoint `u=v=tau`,

\[
 \partial_\epsilon^3q(0)|_0=-{3g\tau^2\over2\chi},
 \qquad
 \partial_\epsilon^3\Pi(0)|_0=-3g\tau.       \tag{8.8}
\]

The ordered second-variation witness already proves the result; the cubic
fixture independently checks the nonlinear convention.  Equations
(8.1)--(8.8) establish
`NG-2026-08-04-PRE-A-CP1-CL8-DIRECT-NONLINEAR-WEYL-RELABEL`.

The no-go is deliberately narrow.  For example, a nonlinear canonical shear
can be implemented by a unitary on `B(L2)` while sending a Weyl generator to a
more complicated operator rather than to one relabelled Weyl generator.
Deformation quantization, perturbative algebraic QFT, path-integral, and
semiclassical Fourier-integral routes remain logically open.

<a id="section-9-dynamics-no-go"></a>
## 9. Current exact dynamics intertwiner no-go

The first nonzero collective continuum mode has

\[
 \omega_{\rm cont}^2=9+4^2=25.                \tag{9.1}
\]

The current centered lattice on spacing `a` gives instead

\[
 \omega_a^2=9+{4\over a^2}\sin^2(2a).         \tag{9.2}
\]

For every finite even `M>=4`, `0<2a<=pi/4`, and the strict inequality
`sin(2a)<2a` gives

\[
 \omega_a^2<25.                               \tag{9.3}
\]

An intertwiner of the linear generators would preserve their frequency
polynomials on the injected mode, contradicting (9.1)--(9.3).  Hence the
current `K_a` is not an exact dynamics intertwiner even before the quartic
interaction is restored.  This establishes
`NG-2026-08-04-PRE-A-CP1-CL8-CURRENT-SAMPLING-EXACT-DYNAMICS`.

The registered `O(a^2)` theorem remains valid.  A symbol-matched spectral or
light-cone regulator could also evade this no-go, but it would be a new model.

<a id="section-10-groenewold-boundary"></a>
## 10. Groenewold hostile boundary

On a common Schwartz core, define

\[
 A={1\over2}(Q^2P+PQ^2),\quad
 B={1\over2}(QP^2+P^2Q),
\]

\[
 E={1\over4}(Q^2P^2+2PQ^2P+P^2Q^2).
\]

Exact normal ordering, or the terminating cubic Moyal expansion, gives

\[
 {[Q^3,P^3]\over9i\hbar}=E-{\hbar^2\over6}I,
 \qquad
 {[A,B]\over3i\hbar}=E+{\hbar^2\over6}I.     \tag{10.1}
\]

The classical expressions on the left both represent `q^2 p^2`, while their
quantum values differ by `hbar^2 I/3`.  This is a hostile control against an
exact full-polynomial Dirac quantization.  It is not a claim that nonlinear
quantum dynamics or formal star quantization is impossible.

<a id="section-11-gate-and-chain"></a>
## 11. Gate and Pre-A chain placement

The parent `PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER` gate remains open.
Three restricted subgates close, and three overbroad routes are formally
refuted.  The next constructive gate is

`PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL`,

followed by a full finite-`a` boundary algebra and exact CCR map.

The exact next contract must name both phase spaces and forms, both algebra
types, the map direction and image, star/CCR preservation, boundary and bulk
dynamics, one actual state pullback, complement data, one Hamiltonian and
energy-reference ledger, and all inter-regulator embeddings and counterterms.

For the programme chain:

- C0 remains open because Lorentzian null sheets and `hbar` are inputs.
- N1 gains a conditional cutoff finite-image ingredient, but the full boundary
  algebra, physical state, and regulator compatibility are absent.
- N2 remains open because neither the full algebra nor dynamics and constraints
  are intertwined.
- N3--N5 receive no result.
- No event-horizon or cyclic-cosmology inference is licensed.

<a id="section-12-adversarial-review"></a>
## 12. Devil's-advocate and code review

1. **The PA-H1 and CL8 symplectic signs are opposite.**  
   **VALID WITH MITIGATION.**  Section 2 explicitly sets the CCR form to
   `sigma=-Omega_var` on every CL8 space.  Both sides change sign together, so
   the transfer remains symplectic and the Weyl phase is fixed once.

2. **Point sampling is not exact on the full phase space.**  
   **UPHELD.**  Section 7 is an exact counterexample.  The positive theorem is
   explicitly restricted to the three-mode spectral image.

3. **A kinematic symplectic embedding was called a dynamics intertwiner.**  
   **DISMISSED.**  Section 9 proves the opposite by an exact dispersion
   mismatch.  No interacting or linear time intertwining is claimed.

4. **A pulled-back interacting state quantizes the nonlinear Goursat map.**  
   **DISMISSED.**  The state is restricted along the tangent finite-image map
   only.  Section 8 formally rejects direct nonlinear generator relabelling.

5. **A state on the image selects a physical vacuum.**  
   **DISMISSED.**  Ground versus Gibbs criteria, beta, `hbar`, the background,
   and the large symplectic complement remain inputs or undetermined.

6. **A Weyl algebra, `B(H)`, and the compact operators were interchanged.**  
   **DISMISSED.**  Section 2 fixes the source and target algebra types.  The
   `B(H_a)` state is first restricted to the concrete Weyl-generated algebra.

7. **The collective normalization lost a factor eight or one eighth.**  
   **DISMISSED.**  Sections 3 and 5 carry all eight equal species explicitly;
   their sum cancels the inherited `1/8` once and only once.

8. **The Groenewold witness rules out every nonlinear quantum construction.**  
   **DISMISSED.**  Section 10 confines it to exact full-polynomial Dirac rules
   on the stated domain.

The primary verifier derives the transfer blocks, exact collective sampling
Gram, kernel phase, nonlinear third derivative, shear control, Moyal anomaly,
and dispersion mismatch symbolically.  The independent verifier uses rational
block determinants, modular Fourier sums, direct monomial derivative counts,
and a different exact fixture.  No finite matrix is used as an exact CCR
representation.

<a id="section-13-reproduction"></a>
## 13. Reproduction

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_quantum_boundary_algebra_intertwiner_route_split_verify.py
```

Each command writes its JSON artifact under
`claims/C6-SPACETIME-SIGNATURE/runs/`.  The integrated verifier reruns both
children, compares them with the stored artifacts, checks all parent identities
and hashes, confirms the three formal negatives and strategy record, and
asserts that C6 remains `T1`, `ACTIVE`, `CONDITIONAL` with only
`C6-BCC-PREMISE-BLOCKED` open.

<a id="section-14-no-overclaim"></a>
## 14. No-overclaim statement

This certificate proves only an inserted-background, ordered-tangent,
six-dimensional characteristic Weyl image, its exact restricted sampling
monomorphism for even `M>=4`, and state pullbacks from already constructed
fixed-regulator bulk densities.  It does not quantize the nonlinear Goursat
map, define the full finite-`a` boundary algebra, intertwine the current
continuum and lattice dynamics, prove interacting Weyl-algebra invariance,
select a physical state or reference energy, establish a regulator limit or
Hadamard state, identify physical empty space or a below-empty-space sign,
derive `hbar`, Lorentzian nullness, cooling, a phase transition, full 3+1
dynamics, gravity, an event horizon or a cycle, close C0 or N1--N5, advance C6,
complete CP1, or complete Pre-A.
