# R-167 v1.8 certificate: fixed-Trotter exhaustion, Renyi history tails, and OS/GNS gap reduction

- **Exploration:** `EXP-000805`
- **Result:** `R-167`, additive version `v1.8`; no new result number
- **Stable result ID:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

This certificate narrows the two independent successors left by R-167 v1.7.
It proves exact fixed-level split compatibility and an exact
sandwiched-Renyi sufficient condition for the missing two-orientation history
tail.  Separately, it proves the zero-temperature OS temporal-mass/GNS-gap
equivalence, the exact one-site Q3 instanton action, and a conditional
low-doublet Ising reference gap.  It proves neither the required Q3LOCK Renyi
estimate nor the actual broken-sector gap.

The closed narrow subgates are exactly:

1. `PA-CP1-ST8-Q3LOCK-FIXED-TROTTER-LOCAL-STRICT-INDUCTIVE-EXHAUSTION-COMPATIBILITY`;
2. `PA-CP1-ST8-Q3LOCK-SANDWICHED-RENYI-TO-TWO-ORIENTATION-HISTORY-TAIL-CORRIDOR-REDUCTION`;
3. `PA-CP1-ST8-Q3LOCK-PHASEWISE-GNS-GAP-OS-TEMPORAL-MASS-EQUIVALENCE`;
4. `PA-CP1-ST8-Q3LOCK-ONE-SITE-Q3-INSTANTON-ACTION-MINIMUM`;
5. `PA-CP1-ST8-Q3LOCK-CONDITIONAL-DOUBLET-ISING-REFERENCE-GAP`.

The parent gates remain open:

- `PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`;
- `PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`;
- `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`.

## 1. Exact compatibility at every fixed Trotter level

For finite `X`, put

\[
 \mathcal A_X=B(L^2(\mathbb R^{8|X|}))
\]

and use the unital inclusions `A -> A tensor I`.  The exact onsite subflow
`sigma_t` acts stagewise because onsite terms outside `X` commute with
`A in A_X`.  The exact cross-bond generators

\[
 v_{xy}=-c\,q_x\mathbin\cdot q_y
\]

commute even when two bonds share a vertex.  Hence the all-bond subflow on a
seed `A in A_X` is exactly the finite product over bonds incident on `X`; all
other bond factors commute with the seed and with every included factor.  It
lands in `A_(N_1(X))` and agrees with every finite-volume action once the
volume contains `N_1(X)`.

Local Weyl and basic-resolvent labels may be used as bounded inputs after
embedding them in these finite-region multiplier algebras.  This statement
does not assert that the outputs preserve an inductive local Weyl or
resolvent C-star algebra, that one global multiplier strict topology exists,
or that the resulting maps are point-norm `C0`.

For fixed `n`, define

\[
 \Theta_{t,n}=(\sigma_{t/n}\beta_{t/n})^n .             \tag{1.1}
\]

Then

\[
 \Theta_{t,n}:\mathcal A_X\longrightarrow\mathcal A_{N_n(X)}       \tag{1.2}
\]

is exactly independent of the exhaustion whenever `Lambda` contains
`N_n(X)`.  Its inverse is the reverse word

\[
 \Theta_{t,n}^{-1}=(\beta_{-t/n}\sigma_{-t/n})^n .       \tag{1.3}
\]

The v1.7 finite-stage local-strict theorem makes each individual subflow
stagewise `C0`.  Equations (1.1)--(1.3) are a fixed Trotter level theorem,
not a group theorem for `Theta_(t,n)`: no `n -> infinity` growing-stage
Cauchy, continuous group completion, generator identity, or KMS quotient is
claimed.

## 2. Sandwiched-Renyi history domination

Let `rho` be a faithful finite Gibbs density, let `P` be a unitary partial
split history, let `alpha>1`, and put

\[
 \vartheta={\alpha-1\over\alpha},\qquad
 \widetilde Q_\alpha(P\rho P^*\Vert\rho)
 =\left\|\rho^{-\vartheta/2}P\rho^{1/2}\right\|_{2\alpha}^{2\alpha}.
                                                               \tag{2.1}
\]

For every projection `E`, noncommutative Holder (equivalently sandwiched
Renyi data processing for the binary measurement `{E,1-E}`) gives

\[
 \operatorname {Tr}(P\rho P^*E)
 \le \widetilde Q_\alpha(P\rho P^*\Vert\rho)^{1/\alpha}
      \operatorname {Tr}(\rho E)^\vartheta .             \tag{2.2}
\]

Assume that both `P` and `P*`, for every volume, compact source, split mesh,
partial history, and `|t|<=T`, obey

\[
 \widetilde Q_\alpha(P\rho P^*\Vert\rho),\quad
 \widetilde Q_\alpha(P^*\rho P\Vert\rho)
 \le Q_{\alpha,T}.                                      \tag{2.3}
\]

Then the exact two-orientation estimate is

\[
 \rho(P^*EP)+\rho(PEP^*)
 \le2Q_{\alpha,T}^{1/\alpha}\rho(E)^\vartheta .         \tag{2.4}
\]

The full Renyi hypothesis is sufficient, not necessary.  The actual minimal
target is (2.4), plus its coordinate-polynomial weighted version, for the
specific cutoff-tail projections.

## 3. Gaussian coordinate tails and the corridor arithmetic

Let

\[
 X_S=\max_{x\in S}|q_x|,\qquad E_{S,L}=1_{\{X_S>L\}}.
\]

The registered coordinate moment theorem supplies, for every `a>0`,

\[
 \rho(E_{S,L})\le M_a|S|e^{-aL^2}.                       \tag{3.1}
\]

Put `b=vartheta a`.  Applying (2.2) at every radius and integrating the
tail gives

\[
 \operatorname {Tr}(P\rho P^*X_S^4E_{S,L})
 \le Q_{\alpha,T}^{1/\alpha}(M_a|S|)^\vartheta e^{-bL^2}
 \left(L^4+{2L^2\over b}+{2\over b^2}\right).           \tag{3.2}
\]

For the coordinate-cutoff bond tail,

\[
 |w_{xy,L}|^2\le4c^2X_{\{x,y\}}^4E_{\{x,y\},L}.         \tag{3.3}
\]

Cauchy--Schwarz for a finite edge sum adds only an edge-count polynomial, so
(3.2) controls the required `(V-V_L)^2` history orientation as well.
For `m` candidate edges, the explicit two-orientation coefficient is

\[
 8c^2m^2Q_{\alpha,T}^{1/\alpha}(M_a|S|)^\vartheta
 e^{-bL^2}\left(L^4+{2L^2\over b}+{2\over b^2}\right). \tag{3.3a}
\]

The safe bounded-cutoff corridor is

\[
 8\sqrt2|X|\|A\|e^{\nu_LT}{(\nu_LT)^R\over R!},
 \qquad \nu_L\le{96cL^2\over\hbar}.                     \tag{3.4}
\]

With `L=R^gamma`, `0<gamma<1/2`, its factorial part vanishes.  If a squared
two-sided seminorm estimate carries a history multiplier
`exp(kappa_T L^2)`, (3.2) absorbs it when

\[
 \vartheta a>\kappa_T.                                  \tag{3.5}
\]

If that multiplier acts on the unsquared seminorm after taking the square
root of a probability, the safe condition is

\[
 \vartheta a>2\kappa_T.                                 \tag{3.6}
\]

More generally, if the sandwiched Renyi divergence itself is bounded by
`dL^2+o(L^2)`, replace the left side by `vartheta(a-d)` in (3.5)--(3.6).
Because (3.1) is available for every `a`, a volume-uniform finite `d` would
still close the arithmetic.

## 4. Energy forms and entropy do not imply the Renyi hypothesis

The new scoped failure is

`NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE`.

For `n>=2`, `m>=3`, put

\[
 \rho_n={\operatorname {diag}(1,e^{-n^4})\over1+e^{-n^4}},\qquad
 K_n=\operatorname {diag}(1,1+n^4),                     \tag{4.1}
\]

and let the displayed coordinate observable be `X_n=nP_1`.  Thus the
reference exponential moment is

\[
 \operatorname {Tr}\rho_n e^{aX_n^2}
 ={1+e^{-n^4+an^2}\over1+e^{-n^4}},
\]

which is uniformly bounded for every fixed `a`.

and rotate the two levels in either orientation by an angle satisfying

\[
 \sin^2\theta_{n,m}
 ={1\over(p_{0,n}-p_{1,n})n^{2m}}.                      \tag{4.2}
\]

The tilted excited probability is exactly

\[
 q_n=p_{1,n}+n^{-2m}.                                   \tag{4.3}
\]

Consequently, for every `0<r<=2m`,

\[
 \operatorname {Tr}(U\rho_nU^*X_n^r)
 =n^rp_{1,n}+n^{r-2m},
\]

so every preregistered finite moment list is uniformly bounded after choosing
`m` above its largest required half-order.

The relative entropy and energy excess vanish as `n^(4-2m)`.  The reference
has every Gaussian coefficient, and any preregistered finite tilted-moment
list can be kept uniformly bounded by choosing `m` above it.  Moreover,

\[
 {1\over2}K_n\le U_{n,m}^{\pm}K_nU_{n,m}^{\pm *}\le2K_n. \tag{4.4}
\]

Indeed the generalized relative matrix has determinant one and trace at
most `5/2`.  Yet binary measurement data processing yields

\[
 \widetilde D_\alpha(U\rho_nU^*\Vert\rho_n)
 \ge n^4+\log(1+e^{-n^4})
 -{2m\alpha\over\alpha-1}\log n\longrightarrow\infty.  \tag{4.5}
\]

Thus the present entropy, finite-moment, and two-sided energy-form inputs do
not automatically supply (2.3).  This is not a counterexample to an actual
Q3LOCK Renyi history bound and does not assert dynamics nonexistence.

## 5. Zero-temperature OS temporal mass and GNS coercivity

Let `(pi_omega,H_omega,Omega_omega)` be a zero-temperature phase
representation with

\[
 H_\omega\ge0,\qquad H_\omega\Omega_\omega=0,
 \qquad\ker H_\omega=\mathbb C\Omega_\omega.            \tag{5.1}
\]

Let a unital invariant core have centered vectors
`xi_A=pi(A-omega(A)1)Omega` that form a form core for `H_omega^(1/2)` on the
orthogonal complement of the vacuum.  Define physical imaginary time

\[
 G_A(\tau)=\langle\xi_A,e^{-\tau H_\omega/\hbar}\xi_A\rangle
 =\int_{(0,\infty)}e^{-\tau E/\hbar}\,d\mu_A(E).         \tag{5.2}
\]

For every `Delta>0`, the following are equivalent:

1. `sigma(H_omega) subset {0} union [Delta,infinity)`;
2. on the core,
   \[
   -i\hbar\,\omega(A^*\delta(A))
   \ge\Delta\{\omega(A^*A)-|\omega(A)|^2\};             \tag{5.3}
   \]
3. for all `tau>=0`,
   \[
   G_A(\tau)\le e^{-\Delta\tau/\hbar}G_A(0).            \tag{5.4}
   \]

Here `delta=(i/hbar)[H,.]` and

\[
 -\hbar G_A'(0+)=\langle\xi_A,H_\omega\xi_A\rangle
 =-i\hbar\omega(A^*\delta(A)).                          \tag{5.5}
\]

The spectral theorem proves `(1)=>(3)` and `(1)=>(2)`; the form-core
hypothesis proves the converses.  A useful weaker test is: if every core
observable has a finite `C_A` and one common `m>0` such that

\[
 G_A(\tau)\le C_Ae^{-m\tau}                             \tag{5.6}
\]

for all sufficiently large `tau`, then the spectral measure in (5.2) has no
support below `hbar m`, and `Delta>=hbar m`.

This is a criterion, not the Q3LOCK gap.  A fixed-beta periodic OS/KMS
system reconstructs a thermal Liouvillean, not the positive vacuum
Hamiltonian in (5.1).  The missing input is beta-infinity phase selection and
a phasewise, beta-uniform half-line rate.

## 6. Exact one-site Q3 instanton action

Write the shifted one-site potential as

\[
 U(q)={g\over4}\sum_{e=1}^8(q_e^2-v^2)^2
 +{\lambda\over4}\sum_{\{e,f\}\in E(Q_3)}
 (q_e-q_f)^2(q_e^2+q_f^2),                              \tag{6.1}
\]

with `chi>0`, `v>0`, `g>0`, and `lambda>=0`.  For every absolutely continuous finite-action heteroclinic in `H1_loc`, with `qdot in L2` and endpoint limits from `-v1` to `+v1`,

\[
 I[q]=\int_{-\infty}^{\infty}
 \left({\chi\over2}|\dot q|^2+U(q)\right)dt
 \ge S_{\rm inst}:={16\sqrt2\over3}v^3\sqrt{\chi g}.   \tag{6.2}
\]

Discard the nonnegative Q3 term and use

\[
 {\chi\over2}|\dot q|^2+{g\over4}\sum_e(q_e^2-v^2)^2
 \ge\sqrt{\chi g\over2}
 \sum_e|\dot q_e|\,|q_e^2-v^2|.                       \tag{6.3}
\]

Each endpoint variation contributes at least `4v^3/3`, proving (6.2).
The locked kink

\[
 q_e(t)=v\tanh\!\left(v\sqrt{g\over2\chi}(t-t_0)\right) \tag{6.4}
\]

attains equality and makes the Q3 term vanish.  If `lambda>0`, equality
locks the eight centers and the minimizer is unique up to the common time
translation.  At `lambda=0`, the eight scalar kink centers can translate
independently, so locked uniqueness is not claimed.

For the verifier fixture `chi=1`, `g=2`, `v=3/2`, `lambda=5/7`,

\[
 S_{\rm inst}=36.                                       \tag{6.5}
\]

This is an exact action minimum.  It identifies the expected exponential
scale but proves no eigenvalue splitting or prefactor.

## 7. Conditional low-doublet Ising reference

Assume the exact one-site Hamiltonian has

\[
 \epsilon_0<\epsilon_1<\epsilon_2,                     \tag{7.1}
\]

with simple even/odd Aut(Q3)-singlets `phi_0,phi_1`.  Put

\[
 P=|\phi_0\rangle\langle\phi_0|+|\phi_1\rangle\langle\phi_1|,
 \quad s=|\phi_0\rangle\langle\phi_1|+|\phi_1\rangle\langle\phi_0|,
                                                               \tag{7.2}
\]

\[
 \delta_1=\epsilon_1-\epsilon_0,\quad
 k=h_{\rm site}-\epsilon_0-\delta_1|\phi_1\rangle\langle\phi_1|,
 \quad k\ge\Gamma(1-P),                                \tag{7.3}
\]

where `Gamma=inf sigma(h|P_perp)-epsilon_0`.  Choose phase so that

\[
 m=\langle\phi_0,q_e\phi_1\rangle>0,\qquad R_e=q_e-ms. \tag{7.4}
\]

Symmetry makes `m` independent of `e`, and parity gives `PR_eP=0`.
On a connected finite lattice graph `G`, define

\[
 H_{\rm ref}=\sum_xk_x+{cm^2\over2}
 \sum_{\langle xy\rangle,e}(s_x-s_y)^2,\qquad J=8cm^2. \tag{7.5}
\]

Its zero kernel is exactly spanned by the two product vectors

\[
 \bigotimes_x{\phi_0+\phi_1\over\sqrt2},qquad
 \bigotimes_x{\phi_0-\phi_1\over\sqrt2}.               \tag{7.6}
\]

If `kappa(G)` is the edge connectivity, then

\[
 \operatorname {gap}(H_{\rm ref})
 \ge\min\{\Gamma,2J\kappa(G)\}.                        \tag{7.7}
\]

A high onsite label costs at least `Gamma`; inside the doublet subspace each
disagreeing bond costs `2J`.  For the periodic cubic bond multigraph,
`kappa=6`, so the lower bound is `min{Gamma,12J}`.

The exact full-Hamiltonian decomposition is

\[
 H-\epsilon_0|\Lambda|=H_{\rm ref}+\delta_1\sum_xP_{1,x}
 +{c\over2}\sum_{\langle xy\rangle,e}
 \left[m\{s_x-s_y,R_{x,e}-R_{y,e}\}
 +(R_{x,e}-R_{y,e})^2\right].                          \tag{7.8}
\]

Thus the missing sector-gap certificate is concrete: rigorous enclosures for
`delta_1,Gamma,m`, relative-form bounds for `R_e`, and an
infinite-dimensional two-phase perturbation theorem or controlled
truncation removal.  Equation (7.7) is a conditional reference-model gap,
not the actual Q3LOCK gap.

## 8. Why the direct Yarotsky import does not close the gate

The second new scoped negative is

`NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT`.

The two-phase quantum Pirogov--Sinai theorem summarized by Yarotsky assumes a
finite-dimensional onsite spin space, two exact Hilbert product ground
vectors minimizing every reference local block, strict positivity on their
orthogonal complement (the local-gap/Peierls analogue), a nonzero first-order
splitting vector `k`, and a sufficiently small parameter neighbourhood.  The
exact Q3 onsite space is `L2(R^8)`.  Classical point minima are delta
configurations rather than Hilbert vectors, while the finite quantum onsite
Schrodinger operator has one positive even ground vector.  The required
doublet reduction and small remainder in (7.8) are not registered.

The single-phase relative-perturbation theorem is different: it allows an
infinite-dimensional onsite Hilbert space and can produce an existential
unique gapped weak-coupling regime.  The Q3 bond satisfies, for every
`eta>0`,

\[
 B_{xy}\le\eta[(h_x-\epsilon_0)+(h_y-\epsilon_0)]
 +\left[2\eta\epsilon_0+4\eta gv^4
 +{32c^2\over\eta g}\right]1.                          \tag{8.1}
\]

The scalar residual behind (8.1) is the sum of two squares

\[
 {\eta g\over8}(q^2-2v^2)^2
 +{\eta g\over8}\left(q^2-{4c\over\eta g}\right)^2.   \tag{8.2}
\]

But that theorem yields a unique phase near a product reference, not the
target broken phase.

The registered infrared condition is only

\[
 c>c_{\rm IR}:={\hbar^2J_3^2\over8\chi\theta_Q^2}.      \tag{8.3}
\]

It is a lower bound on `c`; it supplies no upper perturbative radius and none
of `delta_1,Gamma,m,R_e`.  Direct import is therefore invalid.  This is a
hypothesis mismatch, not a no-go for a future controlled low-doublet/QPS
proof or for the actual broken-sector gap.

Primary references for this audit are Yarotsky's
[infinite-dimensional single-phase relative-perturbation theorem](https://arxiv.org/abs/math-ph/0412040)
and the stated
[two-phase quantum Pirogov--Sinai theorem](https://www.mathnet.ru/eng/rm1728).

## 9. Exact status and Pre-A dependency boundary

The common-alpha gate is now:

> **OPEN, WITH FIXED-TROTTER EXHAUSTION COMPATIBILITY AND A CONDITIONAL
> SANDWICHED-RENYI TAIL REDUCTION CLOSED (2026-08-11).**

The broken-sector gap gate is now:

> **OPEN, WITH THE OS TEMPORAL-MASS EQUIVALENCE AND REFERENCE-MODEL ROUTES
> ISOLATED (2026-08-11).**

The active `A5-SECTOR-A-SYNTHESIS` remains the already published `T6`
conditional composition under its seven named hypotheses.  This checkpoint
does not change that card and does not turn it into a physical/full-Class-II
Sector-A theorem.

Physical Pre-A still additionally requires a target-algebra beta-infinity
ground selection, the actual sector coercivity, enlarged-counterterm
continuum control, a same-Hamiltonian physical-empty comparison, and the
prospective validation gate.  The last item requires a genuinely future or
blind target and microscopic observable map frozen before disclosure; no
repository-internal proof can retroactively manufacture that time ordering.
This package does not close Pre-A.

## 10. Devil's-advocate review

1. **Objection:** fixed `n` compatibility already gives the split limit.
   **UPHELD as an overreach.**  The support halo grows with `n`; no Cauchy
   estimate across those stages is proved.
2. **Objection:** v1.7 energy comparability implies the Renyi bound.
   **DISMISSED.**  Section 4 keeps a uniform factor-two energy comparison
   while the sandwiched Renyi divergence diverges.
3. **Objection:** a fixed-beta OS mass is the vacuum gap.
   **UPHELD as an overreach.**  Section 5 requires the positive zero-T
   implementing Hamiltonian and beta-uniform phase selection.
4. **Objection:** the instanton action is a tunnelling-splitting theorem.
   **UPHELD as an overreach.**  Section 6 proves only the action minimum.
5. **Objection:** the conditional Ising reference is the exact Q3LOCK
   Hamiltonian. **DISMISSED.**  Equation (7.8) displays the unbounded
   remainder whose smallness is still missing.
6. **Objection:** all Yarotsky results exclude infinite onsite spaces.
   **DISMISSED.**  The single-phase theorem permits them; the mismatch here is
   specifically the two-phase product reference and missing smallness.
7. **Objection:** these reductions finish Sector A or Pre-A.
   **DISMISSED.**  Section 9 lists the still-open mathematical and prospective
   obligations.

## 11. Reproduction contract

Run, after the manifest and formal authorities are assembled:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_renyi_history_os_gap_reduction_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_renyi_history_os_gap_reduction_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_renyi_history_os_gap_reduction_route_split_verify.py --self-test
```

The primary and non-importing independent engines use different exact
fixtures for the OS and Ising-reference checks.  The integrated layer must
cross-check the shared theorem constants, exact gate and negative sets,
source/result freshness, scope firewalls, and the single checkpoint PDF.
No intermediate PDF is authorized.
