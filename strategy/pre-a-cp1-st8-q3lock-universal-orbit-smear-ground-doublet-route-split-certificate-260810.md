# R-167 v1.6 certificate: finite raw-word completion, the universal zero-source orbit-smear carrier, and scoped ground doublets

## 0. Result identity and boundary

- **Result:** `R-167`, additive version `v1.6`; no new result number.
- **Stable result ID:**
  `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`.
  The historical ID is deliberately retained because v1.0--v1.6 are additive
  versions of the same common-dynamics route split.
- **Exploration:** `EXP-000803`.
- **Claim context:** `C6-SPACETIME-SIGNATURE`, `T0`, `claim_bearing: false`.
- **Exact model:** the registered finite periodic ST8/Q3LOCK Hamiltonians.
- **Source convention:** the universal carrier and ground-doublet theorem use
  only `H_Lambda(0)`.  The selected-tangent raw-word theorem separately uses
  the already frozen `+h_n/-h_n -> 0` nets of `EXP-000781`.

There are two independent positive conclusions.

1.  At fixed beta, the selected phase-tangent nets converge on every fixed
    finite raw configuration-orbit word kernel, not merely on one cyclic raw
    character.
2.  The complete family of exact zero-source finite Hamiltonians defines one
    beta- and state-independent `L1` orbit-smear C-star carrier.  The
    `EXP-000789` approximate broken doublets have two distinct weak-star
    cluster states on this carrier, and both are ground states of its common
    point-norm continuous time shift.

The second object is a **categorical carrier**.  It is not the missing
quasi-local thermodynamic oscillator algebra.  It supplies no all-exhaustion
spatial Cauchy theorem, canonical momentum representation, raw polynomial
generator, phase-envelope quotient theorem, or broken-sector GNS gap.

## 1. Inputs retained from v1.5 and EXP-000789

For a finite-volume Gibbs state, write

\[
 \alpha_t(A)=e^{itH/\hbar}Ae^{-itH/\hbar},\qquad
 \delta(A)={i\over\hbar}[H,A].                                      \tag{1.1}
\]

For a finite-support configuration character

\[
 W_\xi=\exp\!\left(i\sum_{x,e}\xi_{x,e}q_{x,e}\right),             \tag{1.2}
\]

R-167 v1.5 proved, for every q-only potential, source and boundary term,

\[
 [W_\xi^*,[H,W_\xi]]={\hbar^2\over\chi}\|\xi\|_2^2 I,
 \qquad
 \|\delta W_\xi\|_D^2={\|\xi\|_2^2\over\beta\chi}.              \tag{1.3}
\]

Its even Fejer filter has physical-frequency multiplier

\[
 g_R(\omega)=\left(1-{|\omega|\over R}\right)_+,
 \qquad
 f_R(t)={1-\cos Rt\over \pi R t^2},                                  \tag{1.4}
\]

and, with `a_xi=||xi||/sqrt(beta chi)`, gives the uniform cyclic bound

\[
 \epsilon_\xi(R):=
 \|W_\xi-W_\xi^{(R)}\|_\#
 \le a_\xi\sqrt{{2\over R^2}+{\beta\hbar\over R}}.                 \tag{1.5}
\]

The same package proves convergence of every fixed **bandlimited** word Gram
block along the selected `EXP-000781` tangent net.

For the zero-source ground sequence, `EXP-000789` supplies the even ground
vector `Omega_L`, the odd normalized trial vector `Phi_L`, and

\[
 \Psi_L^\pm={\Omega_L\pm\Phi_L\over\sqrt2},\qquad
 m_L^2={\langle S_L^2\rangle\over V^2},                              \tag{1.6}
\]

with

\[
 \liminf_Lm_L^2\ge\rho_*>0,qquad
 \epsilon_L:=\langle\Psi_L^\pm,(H_L(0)-E_{0,L})\Psi_L^\pm\rangle
 \le {\hbar^2\over4\chi V m_L^2}.                                  \tag{1.7}
\]

It also supplies the uniform local quartic moments needed below.  Concretely,
translation invariance, the uniform near-ground energy-density upper bound and
the registered coercivity `H_L+C V>=gamma sum_x|q_x|^4` give a volume-uniform
fourth moment at each fixed site, for both doublets.

## 2. The modular right-context lemma

Let `(M,Omega)` be the support-reduced faithful standard form of a beta-KMS
state.  We use

\[
 \sigma_s=\alpha_{-\beta\hbar s}.                                    \tag{2.1}
\]

For `C` entire analytic for `sigma`, Tomita's right-action identity gives

\[
 YC\Omega
 =J\sigma_{-i/2}(C^*)JY\Omega
 =J[\sigma_{i/2}(C)]^*JY\Omega.                                     \tag{2.2}
\]

Consequently

\[
 \|YC\Omega\|\le \|\sigma_{i/2}(C)\|\,\|Y\Omega\|.              \tag{2.3}
\]

If the physical Arveson spectrum of `C` is contained in `[-S,S]`, the
Bernstein--Phragmen--Lindelof estimate on the strip gives

\[
 \|\sigma_{i/2}(C)\|
 =\|\alpha_{-i\beta\hbar/2}(C)\|
 \le e^{\beta\hbar S/2}\|C\|.                                     \tag{2.4}
\]

No modular-domain hypothesis is imposed on `Y`.  Analyticity and finite
bandwidth are required only of the right context.

## 3. Right-to-left recovery of every fixed raw word

Consider one fixed raw orbit word

\[
 A_1A_2\cdots A_m,                                                     \tag{3.1}
\]

where each factor is a rational configuration character, its adjoint, or a
fixed real-time translate.  Replace factors by Fejer-smoothed contractions
`C_j` **from right to left** and put `Y_j=A_j-C_j`.  At the `j`-th step the
prefix is a product of raw unitaries, while the already smoothed right context
has norm at most one and bandwidth

\[
 S_j=\sum_{k>j}R_k.                                                    \tag{3.2}
\]

Equations (1.5) and (2.4) give the telescoping estimate

\[
 \left|\omega(A_1\cdots A_m)-\omega(C_1\cdots C_m)\right|
 \le \sum_{j=1}^m e^{\beta\hbar S_j/2}\epsilon_{\xi_j}(R_j).         \tag{3.3}
\]

Choose `R_m` first.  After `R_m,...,R_(j+1)` are fixed, `S_j` is a finite
constant, so choose `R_j` large enough to make the next summand arbitrarily
small.  This finite recursion proves that the right side of (3.3) can be made
arbitrarily small for every fixed word.

A common bandwidth for all factors would be a bad estimate: its exponential
right-context cost need not be beaten by the `R^(-1/2)` Fejer error.  The
ordered finite recursion is load bearing.

Fixed-band word kernels converge by v1.5, and the raw-to-smoothed error is
uniform in the selected finite volumes and their limiting KMS system.
Therefore every fixed finite raw orbit-word moment and every fixed raw Gram
entry converges.  Applying the same independent limiting-pivot construction
as v1.5 gives pointed finite-core Fell/GNS convergence on the algebraic raw
orbit-word span.  Equivalently, its cyclic subspace is identified in a GNS
ultraproduct.

This is not a globally compatible embedding of complete finite GNS spaces,
operator strong-star convergence in one common Hilbert space, an arbitrary
bounded-context estimate, or an all-exhaustion result.

## 4. The universal zero-source orbit-smear carrier

Let `Xi_Q` be the countable set of finite-support rational labels on
`Z^3 x {1,...,8}`.  For each finite periodic volume `Lambda`, periodize the
label and write `W_(Lambda,xi)` for the corresponding unitary.  Let
`H_Lambda(0)` be the exact zero-source Hamiltonian and `alpha^Lambda` its
real-time group.

For `f in L1(R)`, define the finite-volume weak-operator integral

\[
 \pi_\Lambda(A_{\xi,f})
 :=\int_{\mathbb R} f(t)\alpha_t^\Lambda(W_{\Lambda,\xi})\,dt.         \tag{4.1}
\]

Strong continuity of the finite Hamiltonian unitary group makes the integral
well defined and

\[
 \|\pi_\Lambda(A_{\xi,f})\|\le\|f\|_1.                              \tag{4.2}
\]

Start from the unital formal star algebra generated by these symbols, impose
linearity in `f` and

\[
 A_{\xi,f}^*=A_{-\xi,\bar f},                                        \tag{4.3}
\]

and define

\[
 \|a\|_{\mathcal H}:=\sup_\Lambda\|\pi_\Lambda(a)\|.                \tag{4.4}
\]

Every finite polynomial has finite supremum norm by (4.2).  Quotient the
common null ideal and complete.  The result is the unital separable C-star
algebra `A_H^0`.  The product representation of all finite volumes is
faithful by construction; individual quotient representations need not be.

Define translations of the kernel by

\[
 (\tau_s f)(t)=f(t-s),\qquad
 \theta_s(A_{\xi,f})=A_{\xi,\tau_sf}.                                \tag{4.5}
\]

Finite-volume equivariance gives

\[
 \pi_\Lambda(\theta_s a)=
 \alpha_s^\Lambda(\pi_\Lambda(a)),                                  \tag{4.6}
\]

so `theta_s` is isometric.  The `L1` translation theorem gives

\[
 \|\theta_s(A_{\xi,f})-A_{\xi,f}\|_{\mathcal H}
 \le\|\tau_sf-f\|_1\longrightarrow0.                               \tag{4.7}
\]

Product estimates extend (4.7) from the dense formal algebra to all of
`A_H^0`.  Thus `(A_H^0,theta)` is one beta- and state-independent point-norm
continuous C-star dynamical system.  On the `W^(1,1)` smear core,

\[
 \delta_{\mathcal H}(A_{\xi,f})=-A_{\xi,f'}.                          \tag{4.8}
\]

Every finite-volume Gibbs state pulls back to a beta-KMS state for `theta`.
For fixed beta the KMS condition is weak-star closed, so every weak-star
cluster of such pullbacks is again beta-KMS.

## 5. Why this carrier is not the thermodynamic quasi-local alpha

The construction in Section 4 is universal for the declared finite
Hamiltonian family.  That strength is also its boundary.

- The maps `pi_Lambda` are quotient representations, not an inductive system.
- Raw `W_xi` need not be present because its orbit can have norm jump two at
  every nonzero time.
- Temporal smearing can destroy spatial localization, so no commuting local
  net follows from the formal support of `xi`.
- Equation (4.8) differentiates the smear kernel; it does not identify the
  unbounded polynomial CCR derivation on raw characters or momenta.
- There is no finite-volume pairwise Cauchy estimate or exhaustion
  independence theorem.

The exact two-level fixture

\[
 (\beta_1,H_1)=(1,-\sigma_x),\qquad
 (\beta_2,H_2)=(2,-2\sigma_x)                                       \tag{5.1}
\]

has the common configuration label `sigma_z` but orbit frequencies two and
four.  Its orbit smears generate `M_2 direct-sum M_2` and carry one abstract
C0 shift with both KMS pullbacks.  Nevertheless the labelled Hamiltonian
generators differ nonscalarly.  Hence a universal carrier alone does not
prove one quasi-local thermodynamic Hamiltonian realization.  This is
consistent with, and does not overturn, the registered posthoc-direct-sum and
automatic-cross-beta-gluing no-go results.

## 6. A fixed bounded order witness from the EXP-000789 doublets

At one fixed site put

\[
 Q={1\over\sqrt8}\sum_{e=1}^8q_e,\qquad
 X=\sum_{e=1}^8q_e=\sqrt8Q.                                         \tag{6.1}
\]

Let

\[
 m_0=\sqrt{\rho_*/2},\qquad
 M_{4,Q}=\sup_{L,\pm}\omega_L^\pm(|Q|^4)<\infty,
 \qquad M_3=(64M_{4,Q})^{3/4}.                                      \tag{6.2}
\]

The last inequality follows from `X^4=64Q^4` and Lyapunov's moment
inequality.  Choose one fixed rational `r>0` such that

\[
 r^2M_3\le3\sqrt8m_0.                                                \tag{6.3}
\]

This is possible by density of the positive rationals.  Use the rational
one-site label

\[
 \xi=r(1,\ldots,1),                                                   \tag{6.4}
\]

not `r(1,...,1)/sqrt(8)`.  The latter is not a rational label.

For all sufficiently large volumes, `m_L>=m_0`.  Since

\[
 |\sin z-z|\le{|z|^3\over6},                                        \tag{6.5}
\]

the plus state satisfies

\[
 \omega_L^+(\sin rX)
 \ge r\sqrt8m_0-{r^3M_3\over6}
 \ge {r\sqrt8m_0\over2}=:d>0.                                     \tag{6.6}
\]

Parity exchanges the two doublets and makes the minus expectation at most
`-d`.

## 7. A single abstract smeared witness separates the cluster states

Fix `T>0` once and for all and take the triangular probability density

\[
 f_T(t)=T^{-1}(1-|t|/T)_+.                                           \tag{7.1}
\]

Direct integration gives

\[
 \int f_T(t)\,dt=1,qquad
 \int f_T(t)|t|^{1/2}\,dt={8\over15}\sqrt T.                        \tag{7.2}
\]

Let `K_L=H_L(0)-E_(0,L)>=0`.  The scalar inequality
`|e^{-is}-1|^2<=2|s|` gives

\[
 \|(e^{-itK_L/\hbar}-1)\Psi_L^\pm\|^2
 \le {2|t|\epsilon_L\over\hbar}.                                   \tag{7.3}
\]

Therefore, for every contraction `B`,

\[
 |\omega_L^\pm(\alpha_t^L(B))-\omega_L^\pm(B)|
 \le2\sqrt{{2|t|\epsilon_L\over\hbar}}.                            \tag{7.4}
\]

Integrating (7.4) against (7.1) and using (1.7) yields

\[
 {16\over15}\sqrt{{2T\epsilon_L\over\hbar}}
 \le {16\over15}\sqrt{{\hbar T\over\chi V\rho_*}}
 \longrightarrow0.                                                   \tag{7.5}
\]

The one fixed self-adjoint element

\[
 b={A_{\xi,f_T}-A_{-\xi,f_T}\over2i}\in\mathcal A_{\mathcal H}^0  \tag{7.6}
\]

is represented in every volume by the time-smear of `sin(rX)`.  Equations
(6.6) and (7.5) imply, eventually,

\[
 \omega_L^+(b)\ge d/2,qquad \omega_L^-(b)\le-d/2.                  \tag{7.7}
\]

Thus `b` is nonzero in the universal norm.  Any joint weak-star cluster pair
of the plus/minus states is separated by the same abstract observable.

## 8. The near-ground Arveson theorem

Let `a in A_H^0` have physical-frequency Arveson spectrum

\[
 \operatorname{Sp}_\theta(a)\subset(-\infty,-\nu],\qquad \nu>0.     \tag{8.1}
\]

Here the Fourier convention is
`hat f(nu)=int exp(+i nu t)f(t)dt`; negative support lowers energy under
`alpha_t(A)=exp(itH/hbar)A exp(-itH/hbar)`.

Equivariance implies the same spectral inclusion for `pi_L(a)`.  With energy
measured from the finite ground,

\[
 \pi_L(a)P_{[0,\hbar\nu)}(K_L)=0.                                   \tag{8.2}
\]

Markov's spectral inequality and (1.7) give

\[
 \omega_L^\pm(a^*a)
 \le\|a\|_{\mathcal H}^2
     \|P_{[\hbar\nu,\infty)}(K_L)\Psi_L^\pm\|^2
 \le\|a\|_{\mathcal H}^2{\epsilon_L\over\hbar\nu}
 \longrightarrow0.                                                   \tag{8.3}
\]

The standard negative-Arveson-spectrum characterization of C-star ground
states now shows that every weak-star cluster state of either doublet sequence
is a `theta`-ground state.  Equation (7.7) proves that a joint cluster pair is
distinct.

If the cutoff is expressed in energy units `eta=hbar nu`, the denominator in
(8.3) is `eta`.  This fixes the units and the sign: a negative-frequency
operator lowers energy and therefore annihilates an exact ground vector.

## 9. The projected-corridor route remains open

For completeness, the bounded coordinate-cutoff dynamics has a genuine
spatial estimate.  On a degree-`z` graph with pair norms at most `J_L`, put

\[
 \nu_L={4zJ_L\over\hbar}.                                            \tag{9.1}
\]

A conservative pairwise-union bound at bond distance `R` is

\[
 8\sqrt2|X|\|A\|e^{\nu_LT}{(\nu_LT)^R\over R!}.                      \tag{9.2}
\]

For the coordinate cutoff, `J_L<=4cL^2`, `z=6`, and hence
`nu_L<=96cL^2/hbar`.  Setting `L=R^alpha` makes (9.2) vanish on every compact
time interval whenever `0<alpha<1/2`.

What remains missing is removal of the cutoff in the evolved boundary term.
Static Gaussian tails do not supply it.  An exact four-dimensional hostile
fixture uses the basis `(|00>,|01>,|10>,|11>)`,

\[
 r_n=(2n+1)\pi,\quad \varepsilon_n=e^{-r_n^4},\quad
 \rho_n={\rm diag}(1,\varepsilon_n,\varepsilon_n,\varepsilon_n)
             /(1+3\varepsilon_n),                                   \tag{9.3}
\]

\[
 q_x=r_n{\rm diag}(0,0,1,1),\quad
 q_y=r_n{\rm diag}(0,1,0,1),\quad
 X_n=q_xq_y=r_n^2|11\rangle\langle11|.                              \tag{9.4}
\]

With `k=pi hbar/(4T)`, let `K_n` act as `k sigma_y` on the
`|00>,|11>` block, put `H_n=K_n+X_n`, and take
`W=diag(1,1,-1,-1)`.  Then

\[
 \|X_n\|_D^2={r_n^4\varepsilon_n\over1+3\varepsilon_n}\to0,
 \qquad [\log\rho_n,X_n]=0,                                         \tag{9.5}
\]

but, for `B_n=alpha_T^{K_n}(W)`,

\[
 \|[X_n,B_n]\|_D^2={2(1-\varepsilon_n)\over1+3\varepsilon_n}\to2.  \tag{9.6}
\]

All coordinate Gaussian moments are uniformly bounded for every fixed
coefficient, yet the full-versus-cutoff orbit two-sided distance tends to two.
This fixture is **not** a Q3LOCK counterexample: `rho_n` is not invariant Gibbs
data for the displayed `H_n` or `K_n`.  It proves only the route-level negative
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-ORBIT-LOCALITY`:
static tails, local normality and a zero first modular derivative do not imply
the required connected two-orientation dynamic tail estimate.

## 10. Closed subgates and the live successor

This package closes exactly:

1. `PA-CP1-ST8-Q3LOCK-SELECTED-TANGENT-RAW-FINITE-ORBIT-WORD-MOMENT-COMPLETION`;
2. `PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FINITE-HAMILTONIAN-L1-ORBIT-SMEAR-CSTAR-CARRIER`;
3. `PA-CP1-ST8-Q3LOCK-UNIVERSAL-ORBIT-SMEAR-DISTINCT-ALGEBRAIC-GROUND-DOUBLETS`.

The live successor is

`PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-COMMON-ALPHA-AND-BROKEN-GNS-GAP`.

The historical combined gate
`PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-BETA-INDEPENDENT-CSTAR-DYNAMICS`
is retained as provenance: v1.6 closes only its categorical carrier component,
not its spatial all-exhaustion obligation.

It requires a noncollapsing raw/resolvent oscillator carrier, spatial net and
all-exhaustion Cauchy theorem, identification of the finite Hamiltonian
generator and the phase KMS representations, followed by a genuine
broken-sector GNS spectral-gap analysis.  The categorical carrier does not
discharge those obligations.

## 11. Devil's-advocate audit

1. **Objection: the right-context estimate gives arbitrary multiplier
   control.**  **UPHELD as an overclaim.**  It applies only after the right
   context has been smoothed to finite bandwidth.  The proof recovers each
   fixed finite word by an ordered recursion and has no word-length-uniform
   completion.

2. **Objection: a universal supremum completion is just the desired
   thermodynamic algebra.**  **UPHELD as an overclaim.**  Quotient
   representations are not an inductive system; raw observables and spatial
   locality are absent.  The two-level frequency fixture makes the categorical
   versus Hamiltonian-identification distinction exact.

3. **Objection: the broken doublets use an irrational label.**  **DISMISSED.**
   The proof uses `xi=r(1,...,1)` with rational `r`, so the phase is `rX`.
   The normalized direction `u=(1,...,1)/sqrt(8)` appears only in the
   magnetization conversion `X=sqrt(8)Q`.

4. **Objection: time smearing can erase the order split.**  **DISMISSED.**
   One fixed compact probability kernel is used, and (7.5) is uniform along
   the doublet sequence and tends to zero as `V^(-1/2)`.

5. **Objection: vanishing energy expectation is weaker than the algebraic
   ground condition.**  **DISMISSED in this carrier.**  The spectral projection
   estimate (8.3) verifies the negative-Arveson condition for every abstract
   negative-frequency element before the weak-star limit.

6. **Objection: static coordinate tails close the original all-exhaustion
   route.**  **UPHELD as an overclaim.**  Section 9 gives an exact hostile
   fixture.  A dynamic, connected, two-orientation tail or quasi-invariance
   estimate remains irreducible.

7. **Objection: two ground states imply a positive mass gap.**  **UPHELD as an
   overclaim.**  Distinctness is proved only on the smear carrier.  No spectral
   gap in either broken GNS representation is estimated.

## 12. No-overclaim boundary

R-167 v1.6 does not prove the quasi-local raw oscillator thermodynamic
dynamics, all-shape exhaustion independence, a local net, a canonical
momentum/full Weyl representation, the polynomial local generator on raw
characters, the zero-source periodic phase mixture, identification of the
EXP-000800 phase KMS systems as quotient representations of `A_H^0`, a
broken-sector GNS or physical mass gap, regulator removal, a continuum,
physical empty space or a below-empty sign, Pre-A selection, C6, CP1 or
Sector-A closure.

## 13. Gate-level synthesis and PDF QA

The development phase used this manifest, certificate, the three run JSONs
and the append-only `EXP-000803` record without issuing a per-lemma or
intermediate PDF.  After all three verifier layers passed, the single
gate-level synthesis was issued as

- source: `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-universal-orbit-smear-ground-doublet-route-split-260810-v0.5.tex.txt`;
- PDF: `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-universal-orbit-smear-ground-doublet-route-split-260810-v0.5.pdf`.

The source-only form check passed, the build reported zero overfull boxes,
and all seven rendered pages were inspected for clipping, overlap, equation
breakage, identifier legibility, page numbering and the no-overclaim
boundary.  This is the one checkpoint synthesis PDF, not a new mathematical
result or an additional exploration.
