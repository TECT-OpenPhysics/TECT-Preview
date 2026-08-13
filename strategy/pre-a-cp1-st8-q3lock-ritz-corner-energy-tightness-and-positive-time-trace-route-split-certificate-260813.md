# R-167 v3.5 proof certificate: Ritz-corner state passage and positive-time trace-class cutoff removal

## 1. Verdict and exact authority boundary

This proof-first package closes exactly two scoped results:

1. `PA-CP1-ST8-Q3LOCK-RITZ-CORNER-PULLBACK-FIXED-WITNESS-AND-LOCAL-ENERGY-TIGHTNESS-STATE-PASSAGE`;
2. `PA-CP1-ST8-Q3LOCK-POSITIVE-IMAGINARY-TIME-ENERGY-DRESSED-TRACE-CLASS-RITZ-REMOVAL`.

It also registers four exact obstructions:

1. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-DIMENSION-NORMALIZED-SCHATTEN-SMALLNESS-AUTOMATIC-DFFR-TRANSITION-OR-CONTOUR-SMALLNESS`;
2. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY`;
3. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-WITNESS-SEPARATED-RITZ-PULLBACKS-AUTOMATIC-LOCALLY-NORMAL-LIMITS`;
4. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-RITZ-CORNER-UCP-AUTOMATIC-ASYMPTOTIC-MULTIPLICATIVITY-AND-DYNAMICS-INTERTWINING`.

The first result gives a correct state-level use of Ritz corners. Compression
is a parity-compatible unital completely positive map into the corner algebra,
not a unital inclusion of that corner into the full algebra. Pulling cutoff
states back along that map preserves a single fixed odd witness. Local energy
tightness then upgrades weak-star compactness to trace-norm compactness on
every bounded local algebra and hence to locally normal cluster states.

The second result removes spectral Ritz projections only after a fixed
positive imaginary time. A relative-form envelope makes the energy-dressed
perturbation trace class, and spectral compressions converge to it in trace
norm. This is not an undressed DFFR contour estimate.

EXP-000839 records the R-167 v3.5 continuation of EXP-000838. No v3.5 PDF is
issued.

## 2. Ritz corner maps are UCP and projective

Let `H` be separable. Let `P_M` be increasing finite-rank projections with
`P_M -> I` strongly. Assume every `P_M` commutes with the onsite parity
unitary. For a finite set `X`, write

\[
 P_{M,X}=\bigotimes_{x\in X}P_M,
 \qquad
 C_{M,X}(A)=P_{M,X}AP_{M,X}.                         \tag{2.1}
\]

The codomain is `B(P_(M,X) H_X)`, whose identity is `P_(M,X)`. If
`W_(M,X):P_(M,X)H_X -> H_X` is the canonical isometry, then

\[
 C_{M,X}(A)=W_{M,X}^* A W_{M,X}.                     \tag{2.2}
\]

Thus `C_(M,X)` is unital and completely positive. For `X subset Y`,

\[
 C_{M,Y}(A\otimes I_{Y\setminus X})
 =C_{M,X}(A)\otimes P_{M,Y\setminus X},              \tag{2.3}
\]

which is exactly compatibility with the unital corner embedding. The local
maps therefore define one global UCP contraction `C_M` from the bounded local
inductive algebra to the cutoff algebra.

If `M<=M'`, compression from the `M'` corner to the `M` corner composes with
`C_(M')` to give `C_M`. This is a projective compression system. The reverse
corner inclusion sends the smaller identity `P_M` to `P_M`, not to `P_(M')`,
and is not a unital inductive homomorphism. No full-oscillator state should be
defined by pretending otherwise.

Parity invariance of `P_M` gives the exact intertwining relation

\[
 C_M\Theta=\Theta_M C_M.                              \tag{2.4}
\]

### 2.1 Multiplication and generator defects

The same compression is generally not multiplicative. For a projection `P`,

\[
 C_P(AB)-C_P(A)C_P(B)=PA(1-P)BP.                       \tag{2.5}
\]

On `l^2(N_0)`, let `S e_n=e_(n+1)` be the unilateral shift, let `P_M` project
onto `e_0,...,e_(M-1)`, and choose `A=S^*`, `B=S`. The right side of (2.5) is
the rank-one projection onto `e_(M-1)`. Its operator norm is one for every
`M`; strong convergence of `P_M` does not make this multiplication defect
small in norm.

There is an analogous exact derivation defect. If
`delta(A)=i[H,A]` and the corner derivation is
`delta_P(D)=i[PHP,D]`, then

\[
 C_P(\delta A)-\delta_P(C_P A)
 =i\{PH(1-P)AP-PA(1-P)HP\}.                           \tag{2.6}
\]

The cross-boundary term need not vanish. Thus a Ritz corner UCP pullback can
transfer states and fixed bounded expectations, but it does not by itself
transfer products, dynamics, KMS boundary conditions, derivations, or
ground-state inequalities.

### 2.2 Exact asymptotic-multiplicativity and dynamics-intertwining obstruction

Equations (2.5)--(2.6) and the fixed unilateral-shift fixture prove the exact
no-go

`NG-2026-08-13-PRE-A-ST8-Q3LOCK-RITZ-CORNER-UCP-AUTOMATIC-ASYMPTOTIC-MULTIPLICATIVITY-AND-DYNAMICS-INTERTWINING`.

For every cutoff rank `M`, both the product defect and the displayed generator
defect have rank one and operator norm one. Strong convergence of the Ritz
projections and validity of the UCP state pullback therefore do not
automatically imply asymptotic multiplicativity or dynamics intertwining.
This conclusion is deliberately one-way: it does not exclude convergence on
a separately specified core, or convergence obtained from additional
cross-boundary estimates.

## 3. Fixed-witness pullback and distinct cluster states

Let `omega_M^+` and `omega_M^-` be cutoff states with

\[
 \omega_M^-=\omega_M^+\circ\Theta_M.                 \tag{3.1}
\]

Define full-algebra states by the Ritz corner pullback

\[
 \widetilde\omega_M^\sigma=\omega_M^\sigma\circ C_M.
                                                               \tag{3.2}
\]

Suppose one fixed local selfadjoint odd contraction `B` and one number `m>0`
satisfy

\[
 \omega_M^+(C_M(B))\geq m,
 \qquad
 \omega_M^-(C_M(B))\leq -m                         \tag{3.3}
\]

along the selected net. State-space weak-star compactness gives a joint
cluster subnet. Equations (2.4) and (3.1) pass to the limit, so

\[
 \omega^-=\omega^+\circ\Theta.                       \tag{3.4}
\]

Because `B` is fixed rather than cutoff-dependent, (3.3) also passes to the
limit. Consequently

\[
 \|\omega^+-\omega^-\|
 \geq |\omega^+(B)-\omega^-(B)|\geq2m.               \tag{3.5}
\]

This proves state distinction on the bounded algebra. It does not yet prove
local normality, a KMS property, a ground-state condition, or a GNS gap.

## 4. Local energy tightness gives locally normal passage

For every finite `X`, assume one fixed positive operator `K_X` with compact
resolvent and embedded corner density matrices `rho_(M,X)^sigma` satisfying

\[
 \operatorname{Tr}(\rho_{M,X}^\sigma K_X)\leq E_X                 \tag{4.1}
\]

uniformly in `M` and `sigma`. For

\[
 E_R={\bf1}_{[0,R]}(K_X),
 \qquad
 \delta_{M,X,R}=\operatorname{Tr}\rho_{M,X}^\sigma(1-E_R),       \tag{4.2}
\]

the spectral inequality `K_X>=R(1-E_R)` gives

\[
 \delta_{M,X,R}\leq {E_X\over R}.                                \tag{4.3}
\]

The gentle compression estimate gives the explicit modulus

\[
 \|\rho_{M,X}^\sigma-E_R\rho_{M,X}^\sigma E_R\|_1
 \leq2\sqrt{\delta_{M,X,R}}
 \leq2\sqrt{E_X/R}.                                                \tag{4.4}
\]

The compressed density matrices in the fixed finite-dimensional range of
`E_R` form a compact set. Equation (4.4) makes the original family uniformly
trace-norm approximable by those compact sets. It is therefore trace-norm
precompact. A diagonal subnet over finite regions gives compatible density
matrices, and the weak-star cluster states from Section 3 are normal on each
`B(H_X)`. They are locally normal and remain separated by (3.5).

EXP-000781 Section 6 is the prior authority for this compact-resolvent local
energy-tail compactness principle in the Q3LOCK Gibbs setting. The new content
here is the corner UCP pullback, its parity and fixed-witness passage, the
explicit `2 sqrt(E_X/R)` gentle modulus, and the singular fixture below. This
package does not relabel the EXP-000781 compactness argument as new.

## 5. Exact energy-escape obstruction

Let

\[
 e_+,e_-,f_1^+,f_1^-,f_2^+,f_2^-,\ldots                         \tag{5.1}
\]

be orthonormal. Let parity exchange every plus/minus pair. Fix `0<m_0<1` and
put

\[
 \psi_n^\pm=\sqrt{m_0}e_\pm+\sqrt{1-m_0}f_n^\pm.                 \tag{5.2}
\]

The two vector states are parity related and have norm distance two for every
`n`. The fixed compact odd contraction

\[
 B_0=|e_+\rangle\langle e_+|-|e_-\rangle\langle e_-|             \tag{5.3}
\]

has expectations `+m_0` and `-m_0`. Nevertheless, for every compact `A`,

\[
 \langle\psi_n^\pm,A\psi_n^\pm\rangle
 \longrightarrow m_0\langle e_\pm,Ae_\pm\rangle.               \tag{5.4}
\]

The restriction of any weak-star cluster state to the compact operators has
mass only `m_0<1`; the remaining mass is singular. If
`K f_n^sigma=n f_n^sigma` and `K e_sigma=0`, then

\[
 \langle\psi_n^\sigma,K\psi_n^\sigma\rangle=(1-m_0)n\to\infty.  \tag{5.5}
\]

Thus fixed-witness separated Ritz pullbacks do not automatically have locally
normal limits. The missing hypothesis is precisely local energy tightness (or
another genuine normal-compactness mechanism).

## 6. Positive imaginary time makes the form perturbation trace class

Let `h>=0` have compact resolvent and let

\[
 P={\bf1}_{\{0\}}(h),\quad r=\operatorname{rank}P<\infty,
 \quad Q=I-P.                                                       \tag{6.1}
\]

Fix `t>0` and assume

\[
 Z_0(t)=\operatorname{Tr}e^{-th}<\infty,
 \qquad
 Z_1(t)=\operatorname{Tr}(he^{-th})<\infty.                       \tag{6.2}
\]

Let `V=V^*` obey the two-sided form inequality

\[
 -B\leq V\leq B,
 \qquad B=\alpha h+\epsilon I,
 \qquad \alpha,\epsilon\geq0.                                    \tag{6.3}
\]

The two-sided factorization lemma supplies a selfadjoint contraction `C` with

\[
 V=B^{1/2}CB^{1/2}.                                                 \tag{6.4}
\]

Since `B` commutes with `h`, the operator

\[
 D_t=e^{-th/2}B^{1/2}                                               \tag{6.5}
\]

is Hilbert--Schmidt and

\[
 \|D_t\|_2^2=\operatorname{Tr}(Be^{-th})
 =\alpha Z_1(t)+\epsilon Z_0(t).                                  \tag{6.6}
\]

Therefore

\[
 T_t=e^{-th/2}Ve^{-th/2}=D_t C D_t^*\in {\cal S}_1,
 \qquad
 \|T_t\|_1\leq\alpha Z_1(t)+\epsilon Z_0(t).                    \tag{6.7}
\]

Let `Pi_M` be increasing finite-rank spectral projections commuting with `h`
and converging strongly to `I`. The standard trace-ideal approximation theorem
then gives

\[
 \|\Pi_M T_t\Pi_M-T_t\|_1\longrightarrow0.                       \tag{6.8}
\]

This is the positive imaginary time energy-dressed trace-class Ritz removal.
It is an actual infinite-onsite limit for the dressed operator at fixed `t`.

## 7. Exact dressed low/high block estimates

Equations (6.4)--(6.6) also give

\[
 \|PVP\|_{\rm op}\leq\epsilon,
 \qquad
 \|PVP\|_{\rm HS}\leq\epsilon\sqrt r,                            \tag{7.1}
\]

\[
 \|PVQe^{-th/2}\|_{\rm HS}
 \leq\sqrt{\epsilon\,
  \operatorname{Tr}_Q[(\alpha h+\epsilon I)e^{-th}]},             \tag{7.2}
\]

and

\[
 \|e^{-th/2}QVQe^{-th/2}\|_1
 \leq\operatorname{Tr}_Q[(\alpha h+\epsilon I)e^{-th}].          \tag{7.3}
\]

These are energy-dressed estimates at `t>0`. They are not the raw
Hilbert--Schmidt constants in DFFR equation (5.21), do not control a
short-time supremum, and do not establish contour or transition smallness.

## 8. Q3 edge heat-trace reduction

For one Q3 edge put

\[
 h_0={k_x+k_y\over6}+J(1-s_xs_y),\qquad J>0,                       \tag{8.1}
\]

where `s=s^*`, `||s||<=1`, and `[k,s]=0` on one site. Operators on different
sites commute. Hence `1-s_xs_y>=0`, and this bond penalty commutes with
`k_x+k_y`. Set `Z_k(u)=Tr exp(-u k)`. Dropping the commuting positive bond
penalty gives

\[
 Z_{0,e}(t)=\operatorname{Tr}e^{-t h_0}
 \leq Z_k(t/6)^2.                                                   \tag{8.2}
\]

For `x>=0`, functional calculus and maximization of `x exp(-tx/2)` give

\[
 xe^{-tx}\leq {2\over et}e^{-tx/2}.                               \tag{8.3}
\]

Consequently, followed by the same commuting-positive-penalty trace bound at
time `t/2`,

\[
 Z_{1,e}(t)=\operatorname{Tr}(h_0e^{-t h_0})
 \leq {2\over et}Z_k(t/12)^2.                                    \tag{8.4}
\]

If the exact residual satisfies

\[
 -\alpha_Nh_0-\beta_NI\leq V_N
 \leq\alpha_Nh_0+\beta_NI,                                      \tag{8.5}
\]

then

\[
 \|e^{-t h_0/2}V_Ne^{-t h_0/2}\|_1
 \leq {2\alpha_N\over et}Z_k(t/12)^2
       +\beta_N Z_k(t/6)^2.                                       \tag{8.6}
\]

For each fixed `N,t` this is useful whenever the onsite heat traces are
finite. An `N`-uniform passage requires an independently proved uniform
heat-trace majorant. R-167 v3.5 does not supply that premise.

## 9. Two exact trace and Schatten obstructions

### 9.1 Dimension-normalized Schatten smallness

On `C direct-sum C^m` let `Q_m` be the high projection and define

\[
 h_{m,N}=N^2Q_m,
 \qquad
 V_m=|f_1\rangle\langle f_2|+|f_2\rangle\langle f_1|.             \tag{9.1}
\]

Then `|V_m|<=N^-2 h_(m,N)` and `||V_m||_op=1`. For finite `p`,

\[
 m^{-1/p}\|V_m\|_p=(2/m)^{1/p}\longrightarrow0,                  \tag{9.2}
\]

but the transition amplitude between `f_1` and `f_2` remains exactly one.
Dimension-normalized Schatten smallness therefore does not automatically
give DFFR transition or contour smallness. It is not a substitute for the
unnormalized local norm required by a source theorem.

### 9.2 Fixed positive time is not short-time control

On `C direct-sum C^m` put

\[
 h_m=mQ_m,\qquad V_m=Q_m.                                          \tag{9.3}
\]

For every fixed `t>0`,

\[
 \|e^{-t h_m/2}V_me^{-t h_m/2}\|_1=me^{-tm}\longrightarrow0.     \tag{9.4}
\]

For every `t_0>0`, however,

\[
 \sup_{0<t\leq t_0}me^{-tm}=m.                                   \tag{9.5}
\]

The raw trace norm is `m` and the raw Hilbert--Schmidt norm is `sqrt(m)`.
Thus fixed positive-time energy-dressed trace control does not automatically
give DFFR contour entry.

## 10. Exact executable fixtures

All numbers below are derived from labelled upstream inputs by both executable
implementations.

1. Compressing the displayed `4 by 4` selfadjoint test matrix to its first two
   coordinates gives `[[1,2],[2,0]]`. The Kadison defect is
   `[[25,39],[39,61]]`, with determinant `4`.
2. For `K=diag(0,4)` and the pure vector with high amplitude `1/4`, the energy
   is `1/4`. At `R=2`, the tail probability is `1/16`, its Markov bound is
   `1/8`, the actual compression error is `sqrt(61)/16`, and the gentle bound
   is `sqrt(2)/2`.
3. For `h=diag(0,0,2,4)`, `alpha=1/4`, `epsilon=1/8` and `t=log(2)`, the
   diagonal contraction fixture gives `Z_0=37/16`, `Z_1=3/4`, and equality
   `||T_t||_1=alpha Z_1+epsilon Z_0=61/128`. The high trace contribution is
   `29/128` and the final Ritz tail is `9/128`.
4. In the actual-compatible high-sector-zero fixture `k=diag(0,0,12)`,
   `s=diag(1,-1,0)`, `J=1`, `N=4`,
   `alpha_N=N^-2`, `beta_N=N^-3` and `t=log(2)`, direct edge enumeration gives
   `Z_(0,e)=97/32`, `Z_(1,e)=85/32`, `Z_k(t/6)^2=81/16`, and
   `Z_k(t/12)^2=25/4`. The residual trace is `437/2048`, strictly below
   `81/1024+25/[32 e log(2)]`.
5. At `N=4,m=8,p=2`, the normalized Schatten fixture has relative coefficient
   `1/16`, operator norm one, raw Schatten norm `sqrt(2)` and normalized value
   `1/2`.
6. At `m=8,t=log(2)`, the fixed-time obstruction has dressed trace `1/32`,
   while its short-time supremum is `8`.
7. At `m_0=1/4,n=8`, the energy-escape fixture has fixed witness values
   `+1/4,-1/4`, norm distance two, compact mass `1/4`, escaped mass `3/4`, and
   energy `6`.
8. In dimension four with the rank-three shift corner, (2.5) has diagonal
   `[0,0,1]` on the corner. With `H=S+S^*` and `A=S`, the coefficient of `i`
   in (2.6) has the same diagonal. Both defects have rank and operator norm
   one.

## 11. Devil's-advocate audit

### Objection 1: compression is being treated as a homomorphic embedding

**DISMISSED.** Equations (2.1)--(2.3) use compression as a UCP map into the
corner whose unit is `P_(M,X)`. The certificate explicitly records that the
reverse corner inclusion is not unital and that the cutoff system is
projective, not an inductive system of unital subalgebras.

### Objection 2: weak-star compactness alone was used to claim normality

**DISMISSED.** Section 4 requires one fixed compact-resolvent `K_X` and a
uniform local energy bound. Section 5 gives a fixed-witness separated sequence
whose cluster points have singular mass when that energy premise fails.

### Objection 3: the positive-time trace norm is being identified with DFFR

**DISMISSED.** Sections 7 and 9 distinguish dressed `t>0` trace ideals from the
undressed Hilbert--Schmidt and contour quantities. The exact `m exp(-tm)`
fixture has perfect fixed-time decay but unbounded short-time supremum.

### Objection 4: dimension normalization hides multiplicity or a fixed channel

**VALID WITH MITIGATION.** It does. Equation (9.2) is registered as a no-go,
not as evidence for DFFR entry. Any future norm must be matched term by term to
the chosen theorem and must retain its unnormalized transition and contour
content.

### Objection 5: fixed-`N,t` heat traces were silently promoted to a uniform limit

**DISMISSED.** Section 8 states the exact fixed-`N,t` conclusion and leaves
`N`-uniform heat-trace control as an explicit premise. No `t -> 0` passage is
made.

### Objection 6: state passage implies dynamics, KMS, ground states or gaps

**UPHELD AS A FIREWALL.** None of those implications is valid without
additional hypotheses. The two results concern bounded-algebra states with
local normality and positive-imaginary-time trace-class operators only.

### Objection 7: exact fixtures mask a sign, factor, unit, or copied number

**DISMISSED BY RECOMPUTATION.** The fixtures are dimensionless exact test data;
they are not physical-unit claims. Every derived number is recomputed from the
labelled upstream inputs in both the symbolic and stdlib-only lanes. In
particular, the coefficient `2/(e t)` is rederived by maximizing
`x exp(-t x/2)`, so the factor two is not copied from the certificate. The
energy-escape state distance is recomputed from explicit disjoint plus/minus
vector supports as `2 sqrt(1-|overlap|^2)`, rather than inserted as the answer.
The integrated AST/import audit and literal-masking firewall are supplemental
checks; the two independent derivations and their exact agreement are the
substantive safeguards.

## 12. Remaining gates and no-overclaim statement

The following all remain unproved:

- an `N`-uniform heat-trace majorant and any `t=0` trace-ideal estimate;
- actual M-uniform DFFR transition, Hilbert--Schmidt and contour entry;
- DFFR phase passage through Ritz removal or all-exhaustion state convergence;
- a common infinite-volume real-time dynamics or algebraic KMS theorem;
- beta-infinity ground-state selection and one fixed target generator;
- a broken-sector GNS gap or a full-oscillator two-phase theorem;
- common-alpha, mass gap, regulator removal, continuum, physical vacuum or
  empty-space comparison;
- Round-1, C6, CP1, physical Sector A, or Pre-A closure.

All five active parent gates remain OPEN. The historical
`PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION` gate also remains
OPEN. No dynamics/KMS/ground/GNS/full-phase claim is made. No v3.5 PDF is
issued.
