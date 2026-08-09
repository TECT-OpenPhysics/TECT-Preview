# Pre-A CP1/CL8 Q3 beta-independent Hamiltonian and ground reference

**Candidate:** `PA-CP1-CL8-Q3-BETA-INDEPENDENT-HAMILTONIAN-GROUND-REFERENCE-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-Q3-COMPACT-CIRCLE-FIXED-HAMILTONIAN-FK-GIBBS-AND-STRICT-GROUND-REFERENCE-ADVANTAGE`  
**Exploration:** `EXP-000774`
**Authority:** claim-nonbearing T0 analytic theorem

## 1. The theorem and its new input

Fix one spatial circle `S_L`, one `m0>0`, and the one-particle data

\[
 \mathfrak h=L^2(S_L;\mathbb C^8),\qquad
 \omega=(-\partial_x^2+m_0^2)^{1/2}\otimes I_8.          \tag{1.1}
\]

Let `F=Gamma_s(h)`, `H0=dGamma(omega)`, and let `Omega0` be the free Fock
vacuum.  For the Q3 quartic

\[
 W_4(q)={g\over4}\sum_eq_e^4
 +{\lambda\over4}\sum_{e\sim f}(q_e-q_f)^2(q_e^2+q_f^2),
 \qquad g>0,\quad\lambda\geq0,                           \tag{1.2}
\]

fix a real symmetric matrix `K_*` and put

\[
 P_*(q)={1\over2}q^TK_*q+W_4(q).                         \tag{1.3}
\]

The new input, absent from EXP-000773, is **Wick coherence across beta**.  It
is not inferred from the fact that one fixed-beta matrix family was bounded.
With that coherence imposed, this certificate constructs one self-adjoint
lower-bounded compact-circle Hamiltonian

\[
 H_L=H_0+\int_{S_L}:P_*(\phi(x)):_{vac}\,dx              \tag{1.4}
\]

independent of inverse temperature.  Its normalized Feynman--Kac loop laws
are exactly the coherent all-beta extension of the EXP-000773 Q3 state.  Its
finite-volume ground state is unique, and

\[
 \boxed{E_0(H_L)-\langle\Omega_0,H_L\Omega_0\rangle<0.} \tag{1.5}
\]

This is a strict ground-reference theorem.  It is not a physical-empty-space
or absolute-vacuum-energy theorem.

## 2. Exact Q3 Wick dictionary

Define

\[
 A_{Q3}=(g+\lambda)I_8+\lambda L_{Q3},qquad
 G=g+4\lambda,qquad \operatorname{Tr}A_{Q3}=8G.         \tag{2.1}
\]

At a common spatial cutoff `N`, the equal-time vacuum and periodic thermal
coincidence covariances are

\[
 C_{*,N}={1\over L}\sum_{|k|\leq N}{1\over2\omega_k},
\quad
 C_{\beta,N}={1\over L}\sum_{|k|\leq N}
 {\coth(\beta\omega_k/2)\over2\omega_k},                \tag{2.2}
\]

where `omega_k=sqrt(m0^2+(2 pi k/L)^2)`.  The two sums diverge separately,
but their common-regulator difference has the finite limit

\[
 D_{\beta,L}={1\over L}\sum_{k\in\mathbb Z}
 {1\over\omega_k(e^{\beta\omega_k}-1)}>0.               \tag{2.3}
\]

It decays exponentially as `beta -> infinity`.  The high-temperature end is
not uniform: `D_beta` grows as `beta -> 0`.

For common diagonal covariance `C`, the already verified Q3 identities are

\[
 :W_4:_C=W_4-{3C\over2}q^TA_{Q3}q+6C^2G,                \tag{2.4}
\]

\[
 :{1\over2}q^TKq:_C={1\over2}q^TKq-{C\over2}\operatorname{Tr}K. \tag{2.5}
\]

Applying the Wick heat operator once more, with `D=C_beta-C_*`, gives the
exact change of coordinates

\[
 \boxed{
 :P_{K_\beta}:_{C_\beta}
 =:P_{K_\beta-3D_\beta A_{Q3}}:_{C_*}
   +6D_\beta^2G-{D_\beta\over2}\operatorname{Tr}K_\beta.} \tag{2.6}
\]

The `+6D^2G` sign in (2.6) is essential.

## 3. Necessary and sufficient coherence

Equality of the quadratic Wick coefficients in (2.6) shows that one fixed
vacuum-Wick matrix exists if and only if

\[
 \boxed{K_\beta=K_*+3D_{\beta,L}A_{Q3}.}                 \tag{3.1}
\]

Substitution into (2.6) gives

\[
 :P_{K_\beta}:_{C_\beta}
 =:P_*:_{C_*}-{D_\beta\over2}\operatorname{Tr}K_*
               -6D_\beta^2G.                            \tag{3.2}
\]

If the thermal density includes a scalar `e_beta` and the fixed Hamiltonian a
scalar `e_*`, exact unnormalized equality requires and is guaranteed by

\[
 \boxed{e_\beta=e_*+{D_\beta\over2}\operatorname{Tr}K_*
                    +6D_\beta^2G.}                       \tag{3.3}
\]

For normalized Gibbs states and commutator dynamics, (3.1) is necessary and
sufficient because a field-independent scalar cancels.  For an absolute
partition-function convention, (3.3) is also necessary.

When `K_*=m_*I+eta_*L_Q3`, (3.1) reads

\[
 m_\beta=m_*+3D_\beta(g+\lambda),\qquad
 \eta_\beta=\eta_*+3D_\beta\lambda.                     \tag{3.4}
\]

Thus `lambda>0` forces both the identity and cube-Laplacian channels.  A
scalar mass counterterm cannot supply a common Hamiltonian.  A beta-dependent
matrix is only a change of Wick coordinates when it obeys (3.1); an arbitrary
bounded `K_beta` is a different family of theories.

Given the EXP-000773 terminal matrix at its fixed `beta0`, the unique coherent
embedding is

\[
 K_*=K_{\beta_0}-3D_{\beta_0,L}A_{Q3},                  \tag{3.5}
\]

followed by (3.1) at all other beta.  This is a newly declared extension, not
a retrospective claim about every EXP-000772 approximating family.

## 4. Eight-component Hamiltonian construction

Use the standard Gaussian `Q`-space representation of `F`.  Let `V_N` be the
vacuum-Wick spatial-mode cutoff of the interaction in (1.4).  Three facts make
the scalar and charged `P(phi)_2` construction apply componentwise:

1. every Q3 Wick kernel is one of finitely many component-labelled scalar
   kernels of degree at most four;
2. product-Gaussian hypercontractivity and the `N_tau` estimates are unchanged
   except for finite constants depending on eight components and the finite
   Q3 monomial list;
3. the actual nonradial polynomial has the cutoff-independent stability bound

\[
 W_4(q)\geq {g\over32}|q|^4.                             \tag{4.1}
\]

The cutoff interactions converge in every finite Gaussian `Lp` required by
the form argument.  Stability plus the standard Nelson estimate gives a
closed lower-bounded limiting form and, for every `epsilon>0`, a constant
`C_epsilon` such that after a harmless common lower-bound shift,

\[
 H_0\leq(1+\epsilon)H_L+C_\epsilon.                      \tag{4.2}
\]

The associated self-adjoint generator is (1.4); the cutoff Hamiltonians
converge to it in strong resolvent, hence semigroup, sense.  The same
componentwise `Lp` convergence of the Wick interaction and Nelson domination
are the hypotheses of the direct limiting Feynman--Kac--Nelson theorem.  This
paragraph is the explicit finite-index adaptation: no radial `O(8)` symmetry
is used.

The free heat trace is

\[
 \operatorname{Tr}e^{-sH_0}
 =\prod_{k\in\mathbb Z}(1-e^{-s\omega_k})^{-8}<\infty.  \tag{4.3}
\]

Equation (4.2), min--max, and (4.3) imply compact resolvent and
`Tr exp(-sH_L)<infinity` for every `s>0`.

The massive free Mehler semigroup is positivity improving in `Q`-space.  Its
Feynman--Kac multiplier is strictly positive.  Therefore `exp(-sH_L)` is
positivity improving.  Compactness and the Jentzsch/Perron--Frobenius theorem
give a ground eigenvector unique up to phase and strictly positive in
`Q`-space.  The unique ground is invariant under every symmetry shared by
`K_*` and `W_4`.  Global `Z2` is always shared; full Q3 graph invariance is
asserted only when `K_*` also commutes with that graph action.  Uniqueness
excludes a finite-volume spontaneous degeneracy but does not create a symmetry
that an arbitrary real symmetric `K_*` explicitly breaks.

## 5. Feynman--Kac--Nelson identification

For every `beta>0`, apply the limiting Feynman--Kac--Nelson theorem directly
to the `Lp` limit of the eight-component Wick interaction.  Its standard
Nelson domination supplies the trace-ideal control for the periodic formula;
the identity below is not inferred from strong-resolvent convergence alone:

\[
 {\operatorname{Tr}e^{-\beta H_L}\over
  \operatorname{Tr}e^{-\beta H_0}}
 =\mathbb E_{\mu_{\beta,L}}
 \exp\left[-\int_{\mathbb T_\beta\times S_L}
 :P_*(\Phi):_{C_*}\,dt\,dx\right].                      \tag{5.1}
\]

The same identity holds with ordered bounded sharp-time multiplication
observables.  Applying (3.1)--(3.3) converts the right-hand side exactly to the
coherent whole-thermal-Wick Q3 law.  Consequently

\[
 \rho_{\beta,L}={e^{-\beta H_L}\over
                       \operatorname{Tr}e^{-\beta H_L}} \tag{5.2}
\]

is a faithful normal beta-KMS state on `B(F)`, and at `beta0` its periodic OS
reconstruction agrees with EXP-000773.  The Hamiltonian, Hilbert space and
field units do not depend on beta.

All four analytic gates are used: the common free loop family, the form
construction, cutoff semigroup convergence/trace class, and Feynman--Kac
identification.  The Wick dictionary alone would not have proved (5.1).

## 6. Strict compact-circle ground advantage

Let `q_L` denote the closed Hamiltonian form.  The free vacuum belongs to its
form domain, and vacuum Wick ordering gives

\[
 q_L[\Omega_0]=0.                                       \tag{6.1}
\]

This zero is a declared reference convention.  Strictness does not come from
the convention.  Choose one species `e` and the normalized four-particle
zero-momentum vector

\[
 \chi_e={(a_{e,0}^*)^4\Omega_0\over\sqrt{4!}}.          \tag{6.2}
\]

Every Q3 vertex has three incident edges, so the coefficient of `phi_e^4`
when all other components vanish is `(g+3lambda)/4`.  With

\[
 \phi_e(x)={1\over\sqrt L}\sum_k{a_{e,k}e^{ikx}
 +a_{e,k}^*e^{-ikx}\over\sqrt{2\omega_k}},              \tag{6.3}
\]

the cutoff-independent cross-form limit is

\[
 A:=q_L(\chi_e,\Omega_0)
 ={(g+3\lambda)\sqrt{4!}\over16Lm_0^2}>0.              \tag{6.4}
\]

The free and quadratic terms have no vacuum-to-four-particle contribution, so
they cannot cancel (6.4).  Both vectors lie in the finite-particle Wick form
core.  Put `B=q_L[chi_e]`, which is finite, and

\[
 \psi_t={\Omega_0-t\chi_e\over\sqrt{1+t^2}}.            \tag{6.5}
\]

Then

\[
 q_L[\psi_t]
 ={ -2tA+t^2B\over1+t^2}<0                              \tag{6.6}
\]

for every sufficiently small positive `t`.  Rayleigh--Ritz gives

\[
 \boxed{E_0(H_L)<0=q_L[\Omega_0].}                       \tag{6.7}
\]

Writing the result as (1.5) makes it invariant under `H_L -> H_L+cI`.  It is
therefore stronger than an absolute sign tied only to a normal-ordering
constant: the interacting minimizer lies strictly below its specified free
vacuum trial inside the same Hamiltonian.

## 7. Ground limit and the finite-beta scalar firewall

Compact resolvent and trace class give

\[
 F_H(\beta)=-{1\over\beta}\log\operatorname{Tr}e^{-\beta H_L}
 \longrightarrow E_0(H_L),                              \tag{7.1}
\]

while the free quantity tends to zero.  Hence

\[
 \lim_{\beta\to\infty}[F_H(\beta)-F_0(\beta)]
 =E_0(H_L)<0.                                            \tag{7.2}
\]

Also `D_beta -> 0` and the scalar in (3.2) tends to zero, so the coherent
thermal-Wick representation has the same ground limit.

At finite beta one must keep the scalar ledger.  With no added scalar, write

\[
 s_\beta=-{D_\beta\over2}\operatorname{Tr}K_*-6D_\beta^2G. \tag{7.3}
\]

Then `R_th=R_vac-beta L s_beta` and

\[
 \Delta f_{vac}=\Delta f_{th}
 +{D_\beta\over2}\operatorname{Tr}K_*+6D_\beta^2G.     \tag{7.4}
\]

Thus EXP-000773's strict centered `Delta f_th<0` cannot be copied blindly to
the raw vacuum-Wick partition difference; the correction can change its sign.
The scalar-gauge-invariant Gibbs variational gap remains

\[
 -{1\over\beta}D(\rho_{0,\beta}\|\rho_{H,\beta})<0,    \tag{7.5}
\]

and (6.7) closes the independent ground-reference sign.

## 8. What is still not physical empty space

This package now has one beta-independent Hamiltonian, not merely a
fixed-beta path measure.  Even so, `Omega0` was selected by inserted
`m0,L`, field units and the chosen free operator.  Nothing here derives it as
the no-condensate state of the universe or as cosmic empty space.

Likewise, (1.5) does not choose an absolute gravitational vacuum-energy zero.
It says that, after any common scalar shift, the exact interacting ground is
strictly below its own named Gaussian trial.  Coupling that difference to
gravity requires a separately defined stress tensor and renormalization
condition.

The theorem is also finite volume.  It does not prove

\[
 \lim_{L\to\infty}{1\over L}
 [E_0(H_L)-\langle\Omega_0,H_L\Omega_0\rangle]<0.        \tag{8.1}
\]

Nor does its unique symmetric finite-volume ground prove spontaneous symmetry
breaking, a condensate, or a phase transition.  These are the next pressure,
relative-entropy-density and phase-selection gates.

## 9. Prior art and adversarial review

Glimm--Jaffe prove the scalar `P(phi)_2` Hamiltonian construction.  Gerard's
charged model treats a genuinely nonradial polynomial in two real components,
showing that radiality is not the analytic mechanism.  Gerard--Jaekel give the
compact/thermal Feynman--Kac precedents.  The extension from two to eight
components uses only a finite component index and the explicit Q3 coercivity
(4.1).  These are prior-art mechanisms, not a world-first claim.

Hostile objections resolved or retained are:

1. **Both covariance diagonals diverge. DISMISSED.**  Their common-cutoff
   difference (2.3) is finite and exponentially convergent.
2. **The Wick scalar has the opposite sign. DISMISSED.**  Equations
   (2.6), (3.2) and (3.3) separately track the uncorrected and compensating
   scalars.
3. **One scalar mass counterterm is enough. UPHELD AS FALSE FOR
   `lambda>0`.**  Equation (3.4) requires the Q3 Laplacian channel.
4. **Every bounded `K_beta` describes one Hamiltonian. UPHELD AS FALSE.**
   The affine coherence law (3.1) is necessary.
5. **The dictionary alone constructs the continuum operator. UPHELD AS
   FALSE.**  Section 4 verifies the independent form, semigroup, trace and
   positivity gates.
6. **Scalar P(phi)2 automatically covers a nonradial eight-vector. UPHELD AS
   INCOMPLETE BY CITATION ALONE.**  Section 4 writes the finite-index
   hypercontractive/stability adaptation, supported by the charged precedent.
7. **The finite-volume ground can retain 256 ordered sectors. UPHELD AS
   FALSE.**  Positivity improvement makes it unique and symmetric.
8. **Vacuum Wick centering alone proves strict lowering. DISMISSED AS
   INSUFFICIENT BUT REPAIRED.**  The nonzero four-particle matrix element and
   Rayleigh--Ritz prove strictness.
9. **The finite-beta centered sign transfers unchanged between Wick schemes.
   UPHELD AS FALSE.**  Equation (7.4) is mandatory.
10. **A negative compact-circle ground advantage is physical empty space or
    a phase transition. UPHELD AS FALSE.**  Section 8 retains both gates.

This theorem does not prove a thermodynamic limit or energy density,
spontaneous phase transition, physical empty-space reference, absolute vacuum
energy, interacting Hadamard/microlocal spectrum, the original fixed-raw or
three-dimensional Q3 parent, physical light, C0, N1--N5, C6, CP1, Sector A,
or Pre-A.

## 10. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_beta_independent_hamiltonian_ground_reference_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_beta_independent_hamiltonian_ground_reference_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_beta_independent_hamiltonian_ground_reference_route_split_verify.py --self-test
```
