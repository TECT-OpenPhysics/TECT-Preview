# EXP-000790 certificate: ordered OS, dynamics, ground, gap, counterterm, and empty-reference route split

**Candidate:** `PA-CP1-ST8-Q3LOCK-ORDERED-OS-DYNAMICS-GROUND-GAP-CONTINUUM-EMPTY-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-ST8-Q3LOCK-PHASEWISE-OS-KMS-ZERO-T-GROUND-CUSP-FULL-Q3-COUNTERTERM-AND-EMPTY-REFERENCE-SPLIT`  
**Task:** T-054  
**Date:** 2026-08-09  
**Tier:** T0, claim-nonbearing

## 1. Result first

This certificate resumes from `EXP-000789` and follows the requested order:

1. phasewise periodic Osterwalder--Schrader/KMS reconstruction;
2. one common real-time dynamics;
3. distinct ground-state selection;
4. the broken-sector GNS gap;
5. an enlarged-counterterm continuum;
6. physical empty-space comparison.

Four exact advances and four route obstructions result.

First, each of the two positive-`lambda` Euclidean DLR phases from
`EXP-000782` separately satisfies the periodic OS hypotheses.  Each therefore
reconstructs an abstract stochastically positive `beta`-KMS system.  This is
**phasewise, not common**: it does not construct one phase-independent
thermodynamic-limit dynamics on a predeclared oscillator algebra.

Second, the currently cited infinite-oscillator dynamics theorems cannot be
directly imported.  Their bounded-Weyl-integral, bounded-`C_0` interaction, or
subquadratic-force hypotheses do not simultaneously include the exact
unbounded Q3 quartic onsite term and the unbounded bilinear spatial coupling.
This is an import obstruction, not a proof that common dynamics cannot exist.
The best next algebra is the resolvent algebra, with a new energy-weighted
polynomial-force locality estimate.

Third, the `EXP-000780` all-source ground-energy density and the `EXP-000789`
ordered doublets compose to a strict zero-temperature source cusp.  They
select two parity-related, locally normal zero-source time-zero tangent
candidates with opposite nonzero magnetization.  Calling them algebraic ground
states still requires the common dynamics and a common generator core.

Fourth, the symmetry-allowed counterterm classification is exact.  The
homogeneous `Aut(Q3) x Z2` quartic invariant space is **19-dimensional**.
Starting from the original `g,lambda` span, repeated closure under

\[
 B(P,Q)=\operatorname{tr}(P''Q'')
\]

has exact ranks

\[
 2\longrightarrow4\longrightarrow9\longrightarrow19
 \longrightarrow19.
\]

The full invariant quadratic space is four-dimensional.  This closes the
operator-basis question, not the regulator-removal problem.

Finally, the earliest honest physical-reference comparison is frozen.  At a
finite spatial volume and finite common regulator it is the same Hamiltonian
Gibbs relative-entropy identity or its ground variational analogue.  The symmetric `EXP-000789`
ground already has long-range order and is not physical empty space.  Another
equilibrium phase of the same Hamiltonian cannot be a strict below-empty
comparator because equilibrium phases have the same equilibrium density.

No C6, CP1, Sector-A or Pre-A claim changes.

## 2. Inherited exact model and limits

One coarse site carries `q_y in R8` and Hilbert space `L2(R8)`.  At zero source
the formal fixed-spacing Hamiltonian is

\[
 H_\Lambda(0)
 =\sum_{y\in\Lambda}
 \left[-{\hbar^2\over2\chi}\Delta_y+U_{Q3}(q_y)\right]
 +{c\over2}\sum_{\langle yz\rangle}|q_y-q_z|^2,       \tag{2.1}
\]

where `g>0`, `lambda>0`, and the onsite Q3 polynomial is quartically
coercive.  The energy source is

\[
 H_\Lambda(h)=H_\Lambda(0)-hS_\Lambda,
 \qquad
 S_\Lambda=\sum_{y\in\Lambda}Q_y,
 \quad Q_y={1\over\sqrt8}\sum_{e=1}^8q_{y,e}.          \tag{2.2}
\]

The finite-temperature phase regime inherited from `EXP-000782` is

\[
 \theta_Q={-r\over3(g+\lambda)},\qquad
 A_0={8c\chi\theta_Q^2\over\hbar^2}>I_3,
 \qquad \beta>\beta_*.                                \tag{2.3}
\]

It supplies two zero-source, parity-related, tempered Euclidean DLR measures
`mu_(beta,+)` and `mu_(beta,-)` with opposite collective expectations.  The
ground-order regime inherited from `EXP-000789` only needs

\[
 A_0>J_3^2,
 \qquad
 \rho_*={\hbar[\sqrt{A_0}-J_3]\over\sqrt{8\chi c}}>0. \tag{2.4}
\]

All fixed-lattice statements below retain the order of limits declared in the
parent packages.  No spacing-zero limit is hidden in this certificate.

## 3. Phasewise temporal reflection positivity

Let

\[
 \Omega_\beta^{\rm t}
 \subset
 \prod_{y\in\mathbb Z^3}
 C(\mathbb R/\beta\mathbb Z;\mathbb R^8)               \tag{3.1}
\]

be the tempered loop space.  Define

\[
 (T_s\omega)_y(\tau)=\omega_y(\tau+s),\qquad
 (\Theta\omega)_y(\tau)=\omega_y(-\tau),\qquad
 (P\omega)_y(\tau)=-\omega_y(\tau).                   \tag{3.2}
\]

Let `D_+` be the bounded continuous local cylinder functions whose time
arguments lie in `[0,beta/2]`.

### Lemma 3.1 -- finite-volume temporal reflection form

For every finite periodic volume and every constant source `h`, the exact
Feynman--Kac loop law satisfies

\[
 \int\overline{F(\Theta\omega)}F(\omega)\,d\mu_{L,h}
 ={1\over Z_{L,h}}\operatorname{Tr}(B_F^*B_F)\ge0,
 \qquad F\in D_+.                                      \tag{3.3}
\]

The proof cuts the thermal circle along the two reflection-fixed time slices.
The real time-independent onsite, spatial and source actions split into the
two reflected half-actions.  The exact heat kernel is symmetric.  The
positive-half insertion is therefore one Hilbert--Schmidt amplitude `B_F`,
and the reflected insertion is its adjoint.  This is the same transfer
factorization already verified at every fixed regulator in `EXP-000768`.

### Lemma 3.2 -- passage to the two tangent phases

The `EXP-000781` construction takes periodic finite-volume limits at fixed
source and then source limits `h -> 0+` or `h -> 0-`.  For fixed `F in D_+`,
the integrand in (3.3) is a bounded continuous local cylinder.  Both weak
limits therefore preserve its nonnegative expectation.  Hence

\[
 \int\overline{F(\Theta\omega)}F(\omega)\,d\mu_{\beta,\pm}
 \ge0.                                                  \tag{3.4}
\]

The same bounded-cylinder limit proves time-translation invariance and
time-reflection invariance.  Cauchy--Schwarz extends (3.4) from `D_+` to the
closed positive-half subspace in `L2(mu_(beta,+/-))`.

### Lemma 3.3 -- strong continuity

For a bounded continuous cylinder `F`, continuity of every loop gives

\[
 F(T_s\omega)\longrightarrow F(\omega)\quad(s\to0).
\]

Bounded convergence yields

\[
 \|F\circ T_s-F\|_{L^2(\mu_{\beta,\pm})}\longrightarrow0. \tag{3.5}
\]

The cylinders are dense, so the translation group is strongly continuous on
the full `L2` path space.

## 4. Sharp time, generation, and periodic OS/KMS reconstruction

Let

\[
 \Sigma_0=\sigma\{\omega_y(0):y\in\mathbb Z^3\}.       \tag{4.1}
\]

Fix one phase-independent sharp-time C-star algebra before reconstructing
either sign.  Let `S_conf` be the norm closure of the unital star-algebra
generated by all finite-site configuration characters

\[
 W_\xi(q)=\exp\!\left(i\sum_y\xi_y\mathbin\cdot q_y\right),
 \qquad \xi_y\in\mathbb Q^8,\quad |\operatorname{supp}\xi|<\infty. \tag{4.2}
\]

This is a separable unital commutative C-star algebra.  It is fixed before the
choice of `mu_(beta,+/-)` and supplies the algebraic labels in the thermal
Green functions.

Unlike a two-dimensional distribution-valued `P(phi)_2` field, the oscillator
paths are continuous.  Sharp-time bounded local configuration functions are
therefore literal measurable functions.  For `f in L2(Sigma_0)`, reflection
fixes time zero and

\[
 \|[f]\|_{\rm OS,\pm}^2
 =\int |f(\omega(0))|^2d\mu_{\beta,\pm}.               \tag{4.3}
\]

Thus the sharp-time embedding is injective modulo the standard null ideal.
Continuous loops are determined by their values at rational times.  Hence the
rational-time translates of `Sigma_0` generate the full path-space Borel
sigma algebra.

For completeness, the positive-temperature reconstruction hypotheses map as
follows.

1. `P1`: multilinearity and joint `S_conf` norm continuity follow from the
   product sup-norm bound; time continuity follows from continuous paths and
   dominated convergence, including coincident-time limits.
2. `P2`: the loop laws are invariant under a common time translation.
3. `P3`: periodicity of every loop and commutativity of configuration
   insertions give the cyclic beta-shift identity.
4. `P4`: Lemmas 3.1--3.2 give the positive reflection matrix, not only its
   diagonal quadratic form.
5. `P-star`: coincident-time insertions multiply in `S_conf`, insertion of the
   unit does nothing, and every ordered Green function is bounded by the
   product of the C-star norms.

Thus the cyclic condition and the equal-time multiplication/unit/norm axioms
are explicit; they are not inferred from reflection positivity alone.

Define the two OS forms

\[
 \langle F,G\rangle_{{\rm OS},\pm}
 =\int\overline{F(\Theta\omega)}G(\omega)
 d\mu_{\beta,\pm}(\omega).                             \tag{4.4}
\]

The periodic positive-temperature reconstruction theorem now applies to each
sign separately.  The quotient and completion yield

\[
 (\mathcal M_{\beta,+},\mathcal B_{\beta,+},
   \alpha_t^{\beta,+},\omega_{\beta,+}),
 \qquad
 (\mathcal M_{\beta,-},\mathcal B_{\beta,-},
   \alpha_t^{\beta,-},\omega_{\beta,-}),               \tag{4.5}
\]

uniquely up to the standard reconstruction equivalence.  They are
stochastically positive W-star dynamical systems, and each vector state is a
`beta`-KMS state.  For bounded local sharp-time functions and ordered
`0<=tau_1<=...<=tau_n<=beta`, their imaginary-time Green functions reproduce

\[
 \int\prod_{j=1}^nF_j(\omega_\Lambda(\tau_j))
 d\mu_{\beta,\pm}.                                     \tag{4.6}
\]

This is the applicable content of Kozitsky's phasewise reconstruction theorem
and the Birke--Froehlich positive-temperature reconstruction.  The generator
in (4.5) is a thermal Liouvillean.  It is not asserted nonnegative and is not a
vacuum Hamiltonian.

No temporal domain-Markov theorem is needed for the abstract reconstruction.
Such a theorem would be useful for a canonical Feynman--Kac identification,
but it is not silently assumed here.  Configuration characteristics are
regular because the parent DLR theorem gives uniform exponential local
moments.  Momentum and a full canonical Weyl algebra are not reconstructed by
that statement alone.

## 5. The phases remain distinct and parity-conjugate

The parent phase theorem gives

\[
 \int Q_0\,d\mu_{\beta,+}\ge\sqrt{\delta_\beta}>0,
 \qquad
 \int Q_0\,d\mu_{\beta,-}\le-\sqrt{\delta_\beta}.      \tag{5.1}
\]

Finite first moments make the collective characteristic function
differentiable at zero, with derivative `i` times (5.1).  The two derivatives
have opposite signs, so continuity leaves some sufficiently small rational
frequency `t` for which the bounded character `exp(i t Q_0)` has different
expectations.  That character lies in `S_conf`.  Thus the reconstructed
phasewise states are distinguished inside the declared C-star algebra without
invoking an unbounded operator.

Moreover,

\[
 P_*\mu_{\beta,+}=\mu_{\beta,-},\qquad
 PT_s=T_sP,\qquad P\Theta=\Theta P.                    \tag{5.3}
\]

The map `[F]_+ -> [F after P]_-` is therefore an OS isometry and extends to a
unitary intertwining the two reconstructed systems.  Their parity equivalence
is exact.  It is not a common-dynamics theorem.

## 6. Why the post-hoc direct sum is not the common dynamics

For any two dynamical systems one may form

\[
 (\mathcal M,\alpha)
 =(\mathcal M_{\beta,+}\oplus\mathcal M_{\beta,-},
   \alpha^{\beta,+}\oplus\alpha^{\beta,-}).            \tag{6.1}
\]

This construction carries the phase label as a central projection and depends
on the already reconstructed phase and temperature.  It does not arise as

\[
 \alpha_t(A)=\lim_{\Lambda\uparrow\mathbb Z^3}
 e^{itH_\Lambda(0)/\hbar}A e^{-itH_\Lambda(0)/\hbar}   \tag{6.2}
\]

on one label-preserving local oscillator algebra.  Because (6.1) is available
for arbitrary unrelated systems, accepting it would make the common-dynamics
gate vacuous.  The **post-hoc direct sum** route is registered negatively.

The required object is one phase-, state- and `beta`-independent quasi-local
algebra, one automorphism group derived from (2.1), a weakly dense
norm-continuous subalgebra, and a common local generator core.

## 7. Current dynamics-theorem import audit

The exact Q3LOCK Hamiltonian lies between standard theorem classes.

1. Nachtergaele--Schlein--Sims--Starr--Zagrebnov represent the anharmonic
   perturbations used in their Lieb--Robinson theorem by finite-measure Weyl
   integrals.  Those perturbations are bounded.  The quartic Q3 onsite
   polynomial is unbounded.
2. Moving the quartic into arbitrary onsite Hamiltonians leaves the spatial
   interaction `-c q_y dot q_z` unbounded.  The complementary general theorem
   with arbitrary onsite terms assumes bounded intersite interactions.
3. The audited subquadratic perturbation theorem assumes growth smaller than
   `|q|^2`; the exact force is cubic.
4. Buchholz's resolvent algebra is the best algebraic candidate and closes
   thermodynamic dynamics for bounded `C_0` nearest-neighbour interactions.
   Its displayed unbounded one-particle extension has derivative in `C_0` and
   does not include the quartic/cubic-force parent.

Therefore a direct import is invalid.  This does not prove nonexistence.

The next constructive gate is

`PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE`.

A viable route is:

1. fix the resolvent or explicitly energy-damped quasi-local algebra;
2. replace the polynomial forces by smooth compact-support truncations;
3. construct their common finite-range thermodynamic dynamics;
4. prove truncation-uniform, energy-weighted Lieb--Robinson and Cauchy bounds,
   uniformly for sources in a compact interval;
5. remove the truncation and identify a common generator core;
6. compare the phasewise Matsubara functions with the analytic continuations
   of KMS states for this one `alpha`.

## 8. A strict zero-temperature source cusp

Let `V=L^3` and

\[
 e_L(h)={E_{0,L}(h)\over8V},\qquad
 e(h)=\lim_{L\to\infty}e_L(h).                         \tag{8.1}
\]

The all-source limit exists locally uniformly by `EXP-000780`.  From
`EXP-000789`, the symmetric ground `Omega_L` obeys

\[
 m_L^2={\langle\Omega_L,S_L^2\Omega_L\rangle\over V^2},
 \qquad \liminf_Lm_L^2\ge\rho_*>0.                    \tag{8.2}
\]

The normalized broken doublet `Psi_L^+` satisfies

\[
 \langle\Psi_L^+,S_L\Psi_L^+\rangle=Vm_L             \tag{8.3}
\]

and has total zero-source energy excess

\[
 \epsilon_L
 \le {\hbar^2\over4\chi Vm_L^2}.                     \tag{8.4}
\]

Use it as a trial vector for `H_L(h)` with `h>0`:

\[
 e_L(h)-e_L(0)
 \le {\epsilon_L\over8V}-{h m_L\over8}.               \tag{8.5}
\]

The first term is `O(V^-2)`.  Taking the dyadic thermodynamic limit gives

\[
 e(h)-e(0)\le-{h\over8}\sqrt{\rho_*},\qquad h>0.      \tag{8.6}
\]

Parity gives the opposite-source statement:

\[
 \boxed{e(h)-e(0)\le-{|h|\over8}\sqrt{\rho_*}.}       \tag{8.7}
\]

The ground energy is even and concave in `h`.  Consequently

\[
 D_+e(0)\le-{\sqrt{\rho_*}\over8},\qquad
 D_-e(0)\ge+{\sqrt{\rho_*}\over8}.                    \tag{8.8}
\]

This is a strict fixed-spacing zero-temperature source cusp.  It is a new
route: it does not take the vanishing `EXP-000782` finite-temperature
magnetization lower bound to `beta=infinity`.

## 9. Distinct time-zero tangent candidates and the algebraic boundary

Choose differentiability points `h_k downarrow 0`.  At finite volume,
Hellmann--Feynman gives

\[
 e_L'(h_k)=-{1\over8}\langle Q_0\rangle_{L,h_k}.       \tag{9.1}
\]

The ground-energy coercivity estimates give uniform local fourth moments and
trace-norm compactness of local reduced density matrices.  First take
`L -> infinity`, then `h_k -> 0+`.  Convex tangent selection and uniform
integrability yield a locally normal zero-source time-zero state candidate
`omega_+` with

\[
 \omega_+(Q_0)\ge\sqrt{\rho_*}.                        \tag{9.2}
\]

Parity yields `omega_-` with the opposite sign.  Bounded truncations again
separate the two states on the bounded local algebra.

These are distinct source-tangent ground **candidates**.  If common dynamics
`alpha^h` exists near zero source and its generators converge on one local
core,

\[
 \delta^h(A)\longrightarrow\delta^0(A),               \tag{9.3}
\]

then the finite-volume ground inequalities pass to `omega_+/-`, making them
distinct algebraic `alpha^0` ground states.  Until (9.3) is proved, that last
sentence is a conditional corollary rather than a closed theorem.

An alternative backup filters the `EXP-000789` doublets into an energy window
`eta_L=C_*/sqrt(V)`.  Their discarded norm is at most `V^-1/4` and their
residual energy is `O(V^-1/2)`, while bounded local order witnesses survive.
This also needs common-core convergence before producing algebraic ground
states.

## 10. The exact broken-sector GNS Poincare-gap test

For a selected algebraic ground state `omega`, write its positive GNS
generator as `H_omega` and define the state-vector Poincare gap

\[
 \Delta_\omega^{P}
 :=\inf\sigma\!\left(H_\omega|_{\Omega_\omega^\perp}\right). \tag{10.1}
\]

A positive value forces `ker H_omega=C Omega_omega` and then agrees with
`inf(sigma(H_omega) minus {0})`.  If another zero vector is orthogonal to
`Omega_omega`, the Poincare gap is zero.  On a generator core, (10.1) is
equivalent to

\[
 \langle A\Omega_\omega,H_\omega A\Omega_\omega\rangle
 \ge\Delta_\omega^{P}
 \left[\omega(A^*A)-|\omega(A)|^2\right].              \tag{10.2}
\]

For a finite block `B`, set `S_B=sum_(y in B)Q_y`.  Locality of the kinetic
term gives the exact identity

\[
 [S_B,[H,S_B]]={\hbar^2\over\chi}|B|.                 \tag{10.3}
\]

The Rayleigh quotient in the GNS representation yields

\[
 \boxed{\Delta_\omega^{P}
 \le{\hbar^2|B|\over2\chi\operatorname{Var}_\omega(S_B)}.} \tag{10.4}
\]

Thus

\[
 {\operatorname{Var}_\omega(S_B)\over|B|}\to\infty
 \quad\Longrightarrow\quad\Delta_\omega^{P}=0.       \tag{10.5}
\]

A positive state-vector Poincare gap necessarily implies a uniform linear
connected-variance bound.  That bound is **necessary, not sufficient**: the full Poincare
inequality (10.2) must hold for every local core observable.

If one instead defines an excitation gap only above a degenerate full kernel,
ordinary variance must be replaced by the norm after projection with
`1-P_0`, where `P_0=1_{\{0\}}(H_omega)`.  The present package does not prove
kernel simplicity and does not use ordinary variance to decide that different
notion.

The collective classical ordered point has `q_e=x`, `x^2=-r/g`.  Its Q3 Walsh
Hessian levels are

\[
 K_\ell(k)=-2r+\lambda{-r\over g}\ell+2cE(k),
 \qquad \ell=0,2,4,6,                                 \tag{10.6}
\]

with multiplicities `1,3,3,1`.  The minimum is `-2r>0`.  Hence there is no
immediate tree-level Goldstone obstruction, but (10.6) is not a quantum GNS
gap proof.

The `O(1/V)` full finite-volume gap collapse from `EXP-000789` is the global
symmetry-tunnelling channel.  It determines neither sign of (10.5) in a pure
phase nor the full inequality (10.2).

## 11. The complete Q3 quartic invariant space

Identify the eight Q3 vertices with `F_2^3`.  The group

\[
 G=\operatorname{Aut}(Q_3)=F_2^3\rtimes S_3            \tag{11.1}
\]

has order 48.  There are

\[
 \left|\{e\in\mathbb N^8:\sum_ve_v=4\}\right|
 ={11\choose7}=330                                    \tag{11.2}
\]

degree-four monomials.  Exact orbit enumeration gives 19 orbits.  A convenient
orbit-sum basis is:

- `O4=sum_v q_v^4`;
- `O31^(d)=sum_(d(v,w)=d)(q_v^3q_w+q_w^3q_v)`,
  `d=1,2,3`;
- `O22^(d)=sum_(d(v,w)=d)q_v^2q_w^2`, `d=1,2,3`;
- six `O211^(a,b;c)` orbits with signatures
  `(1,1;2)`, `(1,2;1)`, `(2,2;2)`, `(1,2;3)`, `(2,3;1)`,
  `(1,3;2)`;
- six `O1111` orbits, classified by the six pair-distance multisets of four
  distinct cube vertices.

The counts are `1+3+3+6+6=19`.  Global `Z2` adds no further restriction at
degree four.

The original bare directions are

\[
 P_g={1\over4}O_4,
 \qquad
 P_\lambda={3\over4}O_4-{1\over2}O_{31}^{(1)}
                  +{1\over2}O_{22}^{(1)}.              \tag{11.3}
\]

This follows by expanding all twelve undirected Q3 edges once.

## 12. Exact one-loop polynomial and all-scale closure

Use the symmetric bilinear operation

\[
 B(P,Q)=\sum_{i,j=1}^8
 (\partial_i\partial_jP)(\partial_i\partial_jQ).       \tag{12.1}
\]

All 64 ordered Hessian entries occur; there is no extra factor `1/2`.  Exact
rational expansion gives

\[
\begin{aligned}
 B(W_4,W_4)={}&
 \left(9g^2+54g\lambda+{195\over2}\lambda^2\right)O_4\\
 &-(18g\lambda+72\lambda^2)O_{31}^{(1)}
 +(12g\lambda+71\lambda^2)O_{22}^{(1)}\\
 &+18\lambda^2O_{211}^{(1,1;2)}
 -6\lambda^2O_{211}^{(1,2;1)}
 +4\lambda^2O_{22}^{(2)}.                             \tag{12.2}
\end{aligned}
\]

This strengthens the first witness in `EXP-000789`.  Adding only
`O22^(2)` is not first-loop complete because both `O211` terms remain.

Let

\[
 U_0=\operatorname{span}_{\mathbb Q}\{P_g,P_\lambda\},
 \qquad
 U_{n+1}=U_n+\operatorname{span}_{\mathbb Q}
 \{B(x,y):x,y\in U_n\}.                               \tag{12.3}
\]

Two independent exact-arithmetic implementations give

\[
 \dim U_0=2,\quad\dim U_1=4,\quad\dim U_2=9,
 \quad\dim U_3=19,\quad\dim U_4=19.                   \tag{12.4}
\]

Since the whole invariant space has dimension 19, `U_3` is the complete
homogeneous invariant quartic space.  Without another proved symmetry or Ward
identity, every all-scale one-loop-closed basis containing the original
couplings must admit all 19 directions.

## 13. Quadratic and kinetic counterterms

The invariant symmetric matrices are the Bose--Mesner distance matrices

\[
 A_d(v,w)=\mathbf1_{d(v,w)=d},\qquad d=0,1,2,3.        \tag{13.1}
\]

They span a four-dimensional space.  The current bare Wick contraction only
exposes the two directions `I=A_0` and `L_Q3=3A_0-A_1`, but contractions of the
full 19-dimensional quartic space span all four directions.  A scalar vacuum
counterterm is separate.

Before Euclidean `O(4)` restoration is proved, the safe power-counting
declaration independently allows

\[
 (\partial_\tau q)^TZ_t(\partial_\tau q),\qquad
 \sum_{i=1}^3(\partial_iq)^TZ_s(\partial_iq),
 \quad Z_t,Z_s\in\operatorname{span}\{A_0,A_1,A_2,A_3\}. \tag{13.2}
\]

An actual continuum theorem still requires an `a`-dependent Hamiltonian,
field normalization, bare trajectory, the regulator's nonzero logarithmic
loop coefficient, uniform coercivity and kinetic positivity, reflection
positivity, tightness, critical correlation-length divergence, full-sequence
OS convergence and a non-Gaussianity test.  The enlarged flow must also be
retested against the FKG/submodularity and order hypotheses.  The invariant
basis theorem is not a continuum theorem.

## 14. The same Hamiltonian reference identity

At a fixed finite spatial volume `L` and finite regulator let

\[
 \rho_{\beta,L}={e^{-\beta H_L}\over\operatorname{Tr}e^{-\beta H_L}},
 \qquad
 \mathcal F_\beta(\sigma_L;H_L)
 =\operatorname{Tr}(\sigma_L H_L)
 +\beta^{-1}\operatorname{Tr}(\sigma_L\log\sigma_L).   \tag{14.1}
\]

For any normalized candidate empty state whose support is admissible,

\[
 \boxed{\mathcal F_\beta(\sigma_{\emptyset,L};H_L)
 -\mathcal F_\beta(\rho_{\beta,L};H_L)
 =\beta^{-1}D(\sigma_{\emptyset,L}\Vert\rho_{\beta,L})\ge0.} \tag{14.2}
\]

At zero temperature,

\[
 \boxed{\operatorname{Tr}(\sigma_{\emptyset,L}H_L)-E_{0,L}(H_L)\ge0.} \tag{14.3}
\]

Both differences are invariant under `H_L -> H_L+cV I`.  Thus they solve the
additive scalar-gauge problem that invalidates absolute Gibbs/Doob anchors.

A strict bulk comparison requires a positive specific limit such as

\[
 {D(\sigma_{\emptyset,L}\Vert\rho_{\beta,L})\over\beta V}
 \longrightarrow\delta_\emptyset>0                    \tag{14.4}
\]

or

\[
 {\operatorname{Tr}(\sigma_{\emptyset,L}H_L)-E_{0,L}\over V}
 \longrightarrow\delta_\emptyset>0.                   \tag{14.5}
\]

Finite-volume strictness of order one is insufficient after division by
volume.

## 15. Why another equilibrium phase cannot be the strict empty comparator

Two equilibrium KMS phases for the same Hamiltonian and temperature have the
same equilibrium free-energy density.  Two ground phases of the same
Hamiltonian have the same ground-energy density.  Therefore another
equilibrium phase cannot produce the strict positive density in (14.4) or
(14.5).

A future strict physical-empty comparator must be independently registered as
a constrained, metastable or preparation branch.  It must not be chosen after
seeing the desired sign.

Nor is one-point magnetization `m=0` sufficient.  A symmetric cat or mixture
can have zero one-point order while retaining long-range order, and the convex
effective potential is Maxwell-flat through a coexistence interval.

In particular,

\[
 {\langle\Omega_L,S_L^2\Omega_L\rangle\over V^2}
 \ge\rho_*>0                                           \tag{15.1}
\]

along the `EXP-000789` sequence.  Hence `Omega_L` is not a no-condensate state.
The doublets `Psi_L^+/-` have nonnegative `O(1/V)` total energy excess above
`Omega_L`; they cannot yield a below-`Omega_L` sign.  The classical
configuration `q=0` is not a normalized quantum state.

The minimum future contract freezes the same algebra, Hamiltonian, regulator,
counterterms, geometry, boundary, units, stress tensor and `(L,beta,a)` limit
path; selects a normalized empty/preparation branch independently; tests local
LRO and clustering rather than one-point order alone; and proves a positive
specific scalar-shift-invariant difference.  Until then, named Gaussian
comparators remain mathematical references, **not physical empty space**.

## 16. Evidence map and failure roadmap

### Closed here

- phasewise temporal RP, sharp-time generation and periodic OS/KMS;
- bounded sharp-time phase separation and parity unitary equivalence;
- the fixed-lattice strict zero-temperature source cusp;
- parity-related locally normal zero-source time-zero tangent candidates;
- the complete 19-dimensional quartic and four-dimensional quadratic
  invariant counterterm spaces;
- the same Hamiltonian finite-volume finite-regulator thermal and ground reference
  identities.

### Failed routes registered here

1. A post-hoc direct sum is not common dynamics.
2. The presently cited bounded-perturbation dynamics theorems cannot be
   directly imported into the exact polynomial parent.
3. Adding only the distance-two quartic witness is not an all-scale closed
   counterterm basis.
4. Another equilibrium phase cannot be a strict physical-empty comparator.

### Still open

- exact polynomial common `alpha` on a phase-independent resolvent/energy-
  damped quasi-local algebra;
- identification of both phasewise Euclidean states as KMS states of that same
  `alpha`;
- distinct algebraic ground states on the common algebra;
- extremality, purity and clustering;
- GNS ground-vector simplicity, connected susceptibility and the full
  broken-sector state-vector Poincare inequality;
- an `a -> 0` enlarged-counterterm regular, reflection-positive non-Gaussian
  continuum;
- a normalized physical empty/preparation branch and positive specific
  comparison;
- C0/N1--N5, C6, CP1, Sector A and Pre-A.

## 17. Prior-art and novelty boundary

Periodic OS/KMS reconstruction, Euclidean Gibbs measures for quantum
anharmonic crystals, Lieb--Robinson thermodynamic dynamics on suitable
oscillator algebras, resolvent algebras, ground-state variational principles,
GNS Poincare criteria, multiscalar one-loop renormalization and Gibbs relative
entropy are established mathematics.

The repository-specific content is the exact passage of the selected
positive-`lambda` Q3LOCK phases through the temporal OS hypotheses; the
`EXP-000780`/`EXP-000789` source-cusp composition; and the exact `Aut(Q3)`
orbit and counterterm-closure computation.  No general-method novelty,
world-first assertion or historical-priority claim is made.

Primary sources used for the route boundary include:

- Y. Kozitsky, *Equilibrium States, Phase Transitions and Dynamics in Quantum
  Anharmonic Crystals*, arXiv `1806.08264`, especially Theorem 2.3;
- L. Birke and J. Froehlich, *KMS, etc.*, arXiv `math-ph/0204023`;
- B. Nachtergaele, B. Schlein, R. Sims, S. Starr and V. Zagrebnov,
  *On the Existence of the Dynamics for Anharmonic Quantum Oscillator
  Systems*, arXiv `0909.2249`;
- D. Buchholz, *The Resolvent Algebra for Oscillating Lattice Systems:
  Dynamics, Ground and Equilibrium States*, arXiv `1605.05259`.

## 18. Devil's-advocate audit

1. **Objection: spatial reflection positivity from EXP-000782 is being reused
   as temporal positivity.**  
   **DISMISSED.**  Equation (3.3) is a separate time-cut transfer identity for
   every finite source law.  The limit proof uses that temporal identity, not
   the spatial infrared form.

2. **Objection: weak convergence need not preserve unbounded reflection
   forms.**  
   **DISMISSED WITH SCOPE.**  The core uses bounded continuous local
   cylinders.  Positivity is then closed under both weak limits and extended
   only afterward by `L2` density.

3. **Objection: the two KMS systems already solve common dynamics.**  
   **UPHELD AS FALSE.**  They are reconstructed separately from phase-labelled
   measures.  Section 6 records why the direct sum is vacuous.

4. **Objection: a KMS Liouvillean is a positive vacuum Hamiltonian.**  
   **UPHELD AS FALSE.**  No positive spectrum or ground state follows from the
   periodic reconstruction.

5. **Objection: source-cusp tangent states are automatically algebraic ground
   states.**  
   **UPHELD AS TOO STRONG.**  Common dynamics and local-generator convergence
   are explicitly required in (9.3).

6. **Objection: the full finite-volume gap collapse refutes a pure-sector
   gap.**  
   **UPHELD AS FALSE.**  The full gap is the tunnelling channel.  Section 10
   supplies the separate connected-variance falsifier.

7. **Objection: the positive ordered Hessian proves the GNS gap.**  
   **UPHELD AS FALSE.**  It is a tree-level viability control and not the
   operator inequality (10.1).

8. **Objection: the distance-two quartic added after EXP-000789 is enough.**  
   **DISMISSED BY EXACT COMPUTATION.**  Equation (12.2) already contains two
   new `O211` terms, and repeated closure reaches all 19 directions.

9. **Objection: 19 dimensions are an arbitrary safe overbasis.**  
   **DISMISSED.**  The 19 orbit sums are the exact invariant space, and the
   basis-independent rational rank reaches 19.

10. **Objection: a named Gaussian comparator is physical empty space.**  
    **UPHELD AS UNPROVED.**  Sections 14--15 freeze the additional selection
    and specific-limit requirements.

11. **Objection: a scalar counterterm can reverse the comparison.**  
    **DISMISSED.**  Equations (14.2)--(14.3) are invariant under a common
    extensive scalar shift.

12. **Objection: this advances C6 or selects the Pre-A winner.**  
    **UPHELD AS FALSE.**  The package is T0 and leaves both gates unchanged.

13. **Objection: ordinary connected variance bounds the positive spectrum
    even if the GNS zero eigenspace is degenerate.**  
    **UPHELD AS FALSE.**  Section 10 defines the state-vector Poincare gap.
    A gap only above a degenerate full kernel needs the explicit `1-P_0`
    projection and is left open.

## 19. Reproduction

Run from the repository root with the shared UTF-8 virtual environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_os_dynamics_ground_gap_counterterm_empty_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_os_dynamics_ground_gap_counterterm_empty_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_os_dynamics_ground_gap_counterterm_empty_route_split_verify.py
```

The primary route constructs the 48 cube automorphisms directly as
`F_2^3 semidirect S3`, partitions all 330 degree-four monomials, and uses
symbolic rational row reduction.  The independent route enumerates
adjacency-preserving permutations from vertex permutations, uses a recursive
composition generator, a non-importing `Fraction` polynomial engine and its
own Gaussian elimination.  The integrated verifier reruns both, compares all
derived invariants, checks stored-result freshness, formal records and the
unchanged C6 firewall.
