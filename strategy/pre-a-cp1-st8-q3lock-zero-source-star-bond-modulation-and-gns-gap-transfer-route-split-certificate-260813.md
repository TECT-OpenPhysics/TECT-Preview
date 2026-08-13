# R-167 v3.0 proof certificate: zero-source star, bond modulation, and GNS-gap transfer

**Date:** 2026-08-13  
**Task:** T-054  
**Exploration:** EXP-000834, continuing EXP-000833  
**Tier:** T0; `claim_bearing:false`

## 1. Exact scope

This proof-first certificate closes three narrowly scoped children of R-167:

1. the exact zero-source full-oscillator forward-star kernel and gap, together
   with a conditional dimension-uniform two-phase-radius reduction;
2. an exact modulation-commutant classification for standard one-site
   cylinders under one bilinear bond flow, together with a conditional
   summable single-toggle-shell reduction to bidirectional all-shape Cauchy;
3. an abstract transfer from uniform finite-volume Poincare inequalities and
   common local-generator convergence to a target GNS spectral gap.

It also records one implication failure: weak-star convergence of simple
finite-volume ground states plus uniform finite-volume gaps does not identify
a prescribed target generator and therefore cannot by itself transfer a GNS
gap.

The package proves no actual zero-source two-phase full-oscillator theorem, no
summable shell estimate for the exact quartic Q3 dynamics, no all-shape common
alpha, and no Q3 broken-sector GNS gap. All five active parent gates remain
OPEN.

## 2. Source calibration

The two-phase comparison source is D. A. Yarotskii, *Pirogov--Sinai theory
for relatively bounded quantum perturbations of classical lattice models*,
Russian Mathematical Surveys 61:2 (2006), 371--372,
DOI 10.1070/RM2006v061n02ABEH004323. Its stated onsite spaces are finite
dimensional and its small perturbation radius is existential. It does not
provide a radius uniform in an oscillator cutoff, onsite dimension, or the
corridor label `N`. The theorem below therefore isolates that uniform radius
as a premise rather than importing it. This source is distinct from
Yarotsky's single-phase infinite-onsite paper, *Ground states in relatively
bounded quantum perturbations of classical lattice systems*, Commun. Math.
Phys. 261 (2006), 799--819, arXiv:math-ph/0412040.

The oscillator-dynamics literature does not remove the other premise. The
anharmonic theorem in B. Nachtergaele, H. Raz, B. Schlein and R. Sims,
arXiv:0712.3820, places the onsite perturbation under
`V' in L1` and a Fourier first-moment condition. A quartic onsite potential
does not satisfy those assumptions. L. Amour, P. Levy-Bruhl and J. Nourrigat,
arXiv:0904.2717, uses a subquadratic and Fourier-regular perturbation class.
Neither result directly covers the simultaneous exact Q3 quartic onsite term
and unbounded bilinear spatial coupling.

For the final bridge, B. Nachtergaele, R. Sims and A. Young,
arXiv:2010.15337, obtain GNS gaps in a bounded-spin frustration-free/LTQO
setting. J. Henheik and S. Teufel, arXiv:2012.15238, explicitly require the
gapped finite-volume Hamiltonians to generate the same infinite-volume
dynamics. These sources calibrate why common-generator convergence is
load-bearing below; they are not imported as exact-Q3 theorems.

## 3. Zero-source full-oscillator forward star

Work on the registered large-`N` zero-source corridor. On the exact full
onsite oscillator Hilbert space, let

\[
 P_N=|\Omega_N^+\rangle\langle\Omega_N^+|
     +|\Omega_N^-\rangle\langle\Omega_N^-|,
 \qquad Q_N=1-P_N,
 \qquad k_NP_N=P_Nk_N=0,
 \qquad k_N|_{Q_N}\geq \Gamma_N Q_N,
 \qquad \Gamma_N=\min\sigma(k_N|_{Q_N})>0
 \text{ is attained},
 \qquad
 s_N\Omega_N^\pm=\pm\Omega_N^\pm,
 \qquad s_NQ_N=Q_Ns_N=0,                              \tag{3.1}
\]

where `P_N` is the exact even/odd doublet projector and `Q_N` is its
orthogonal complement.  The kernel identities and the attained positive
threshold hold for the compact-resolvent Q3 onsite operator and are
load-bearing for the exact kernel and high-branch equality below.  On a positive cubic edge
`e=(x,x+e_i)` put

\[
 h^0_{e,N}={k_{x,N}+k_{x+e_i,N}\over6}
       +J_N(1-s_{x,N}s_{x+e_i,N}),                    \tag{3.2}
\]

and group the three positive edges at `x`:

\[
 h^0_{x,N}=\sum_{i=1}^3 h^0_{(x,x+e_i),N}.           \tag{3.3}
\]

The three spectral labels at any site are `+`, `-`, and `high`.  Their local
data are `(k,s)=(0,1),(0,-1),(lambda,0)` with `lambda>=Gamma_N`.  Replacing
`lambda` by `Gamma_N` gives the sharp lower envelope, and `lambda=Gamma_N`
is attained.  Every term in (3.3) is diagonal in the corresponding product
partition.

### 3.1 Exact kernel

Every summand in (3.2) is nonnegative. It vanishes only when both endpoints
are low and have the same sign. Since the star is connected, all four labels
must agree. Hence

\[
 \ker h^0_{x,N}=\operatorname{span}\left\{
  (\Omega_N^+)^{\otimes4},(\Omega_N^-)^{\otimes4}
 \right\}.                                           \tag{3.4}
\]

There are exactly two product kernels, not one selected kernel.

### 3.2 Exact attained gap

If the centre is low, the cheapest low defect is one disagreeing low
neighbour and costs `2J_N`. The cheapest high defect is one high neighbour and
costs `Gamma_N/6+J_N`. A high centre costs at least
`Gamma_N/2+3J_N`; adding further defects cannot lower any of these values.
Both one-neighbour candidates are actual product eigenvectors, so the lower
bound is attained:

\[
 g^0_{\star,N}
 =\min\left\{2J_N,{\Gamma_N\over6}+J_N\right\}.       \tag{3.5}
\]

Along the v1.9 corridor, `J_N` tends to eight and the high threshold grows,
so `g^0_(star,N)` tends to sixteen. After enlarging `N_1`, one may use the
uniform lower witness

\[
 J_N\geq1,
 \qquad g^0_{\star,N}\geq g_0=1.                     \tag{3.6}
\]

## 4. Grouped relative form and the exact common-radius reduction

Suppose the inherited edge residual satisfies

\[
 |V_{e,N}(\psi,\psi)|
 \leq \alpha_N h^0_{e,N}(\psi,\psi)
       +\beta_N\|\psi\|^2.                            \tag{4.1}
\]

For the grouped residual
`phi_(x,N)=sum_(i=1)^3 V_((x,x+e_i),N)`, summation gives exactly

\[
 |\phi_{x,N}(\psi,\psi)|
 \leq\alpha_N h^0_{x,N}(\psi,\psi)
       +3\beta_N\|\psi\|^2.                           \tag{4.2}
\]

Define

`H_N(t,h)=sum_x[h^0_(x,N)+t phi_(x,N)]+h sum_x s_(x,N)`.

By the inherited exact edge decomposition, `H_N(1,0)` is the physical
zero-source Hamiltonian up to the already declared scalar.

After dividing the reference star by its exact gap, the two normalized
inputs are

\[
 \alpha_N,
 \qquad {3\beta_N\over g^0_{\star,N}},               \tag{4.3}
\]

not `18 beta_N/u` and not a one-phase selector ratio.

Now make the following explicit conditional hypothesis.

> **Uniform two-phase rectangle.** There exist `a_2,b_2>0` depending only on
> dimension three, the fixed star support and range, and the normalized
> two-ground-pattern Peierls/local-gap datum. They do not depend on onsite
> dimension, oscillator spectral cutoff, `N`, or the upper reference
> spectrum. The theorem applies directly to the exact infinite-dimensional
> form reference, or its finite-cutoff conclusions pass through a separately
> assumed cutoff-stable compactness and identification theorem. Every
> parity-equivariant finite-range symmetric form perturbation with normalized
> inputs `alpha<a_2` and `beta'<b_2` then has the declared two-phase conclusion
> in an odd bounded probe field.

Let

\[
 \alpha_N\leq C_\alpha N^{-2},\qquad
 \beta_N\leq C_\beta N^{-3},\qquad
 g^0_{\star,N}\geq g_0\quad(N\geq N_1).              \tag{4.4}
\]

Strict entry is guaranteed for every `N>=N_*`, where

\[
 N_*=1+\max\left\{
 N_1,
 \left\lfloor\sqrt{C_\alpha/a_2}\right\rfloor,
 \left\lfloor
   \left({3C_\beta\over g_0b_2}\right)^{1/3}
 \right\rfloor
 \right\}.                                           \tag{4.5}
\]

Indeed, (4.5) makes `N` strictly larger than both real thresholds in (4.4),
so (4.3) is strictly inside the assumed rectangle.

Use the exactly parity-odd bounded probe `h sum_x s_(x,N)`. Parity maps
`h` to `-h`, while the derivatives of the all-plus and all-minus product
energies differ by two per site. Conditional on the uniform theorem rectangle
and its local coexistence graph, the nonzero derivative splitting and parity
pin coexistence to `h=0`. At interpolation endpoint `t=1`, that point is the
physical zero-source full oscillator.

The last paragraph is a reduction, not an unconditional phase theorem.
Neither full-oscillator applicability nor cutoff-stable passage nor the uniform
rectangle is supplied by the finite-dimensional existential source.

## 5. Bilinear bond-flow cylinder classification

Let

\[
 {\cal H}_x={\cal H}_y=L^2(\mathbb R^8),\qquad
 (M_s\xi)(q)=e^{is\cdot q}\xi(q),                    \tag{5.1}
\]

and, for `c!=0` and `hbar>0`, define

\[
 B_t=\exp\left({ict\over\hbar}q_x\cdot q_y\right),
 \qquad \beta_t(C)=B_t^*CB_t.                        \tag{5.2}
\]

For any `A in B(H_x)`, decompose over the `q_y=y` fibres. The operator
`A tensor I` is constant in the fibres and `B_t` is `M_((ct/hbar)y)`. Thus

\[
 \|\beta_t(A\otimes I)-A\otimes I\|
 =\operatorname*{ess\,sup}_{y\in\mathbb R^8}
 \|M_{(ct/\hbar)y}^*AM_{(ct/\hbar)y}-A\|.            \tag{5.3}
\]

Put

\[
 F_A(s)=\|M_s^*AM_s-A\|.                              \tag{5.4}
\]

The modulation representation is strong-star continuous. Operator norm is
lower semicontinuous under strong convergence, hence `F_A` is lower
semicontinuous. For `ct!=0`, scaling by `ct/hbar` is a measure-class
bijection of `R^8`. Every nonempty open superlevel set of a lower
semicontinuous function has positive Lebesgue measure. Therefore

\[
 \|\beta_t(A\otimes I)-A\otimes I\|
 =\sup_{s\in\mathbb R^8}F_A(s),
 \qquad c t\ne0.                                     \tag{5.5}
\]

The right side is independent of the size of nonzero `t`. Consequently,
point-norm continuity at zero holds exactly when `F_A` vanishes identically,
which is exactly when `A` commutes with every modulation. By the joint
spectral theorem for the coordinate operators, the modulation commutant is
the multiplication MASA. Hence

\[
 {\mathfrak C}(\beta)\cap
 \big(B({\cal H}_x)\otimes I\big)
 =L^\infty(\mathbb R^8)\otimes I.                    \tag{5.6}
\]

Equation (5.6) is only a cylinder classification. It is not a classification
of the full two-site continuous-element algebra. In particular,
`K(H_x tensor H_y)` is continuous under the strongly continuous implementer,
whereas a nonzero `K(H_x) tensor I` is not a two-site compact. There is no
conflict with the v2.9 finite-volume compact core.

The result strictly strengthens the earlier compact-cylinder witness and is
compatible with the raw basic-resolvent obstruction. It does not prove that
the unsplit exact Q3 flow lacks a common algebra. A dressed embedding, a
state-tempered topology, or another non-cylinder spatial carrier remains
possible.

Combining (5.6) with the v2.8 full-Hamiltonian result gives one useful narrow
corollary: inside the continuous bounded configuration-multiplier cylinder
class, the only elements simultaneously admitted by the standard bond split
and the exact full-H point-norm continuous part are scalars. No statement is
made for arbitrary `L_infinity` multipliers.

## 6. Summable single-toggle shells imply all-shape Cauchy

This section isolates a primitive condition that is stronger than, and
actually implies, the desired all-shape Cauchy property.

Let `A` be one common unital C-star algebra, let `D` be a norm-dense unital
star-subalgebra, and let `J` be a countable interaction-label set. Relative
to a finite seed support `X`, assign every `j in J` an integer shell `r(j)`,
assigning the finitely many core labels shell zero. Require local finiteness:

\[
 \{j:r(j)\leq R\}\text{ is finite for every }R.       \tag{6.0}
\]

For every finite background `F subset J`, suppose `alpha_F` is a point-norm C0
automorphism group of `A`.

Assume that for every `A in D` and `T>0` there are nonnegative weights
`w_j(A,T)` such that for every `j`, every finite intermediate background
`F` not containing `j`, every order of insertion, and both time signs,

\[
 \sup_{|t|\leq T}
 \|\alpha_{F\cup\{j\}}^t(A)-\alpha_F^t(A)\|
 \leq w_j(A,T).                                      \tag{6.1}
\]

The uniformity over all backgrounds is load-bearing. Put

\[
 B_r(A,T)=\sum_{j:r(j)=r}w_j(A,T),
 \qquad \sum_{r\geq0}B_r(A,T)<\infty.                \tag{6.2}
\]

If `F` and `G` contain every label through shell `R`, add the labels in
`G minus F` to `F`, and independently add the labels in `F minus G` to `G`.
Both paths end at `F union G`. The triangle inequality and (6.1) give

\[
 \sup_{|t|\leq T}
 \|\alpha_F^t(A)-\alpha_G^t(A)\|
 \leq\sum_{j\in F\triangle G}w_j(A,T)
 \leq\sum_{r>R}B_r(A,T).                             \tag{6.3}
\]

The last tail tends to zero. Thus the complete directed net, not merely one
chosen exhaustion, is point-norm Cauchy on `D`, uniformly on compact time
intervals and for both signs. Isometry extends the limits uniquely to `A`.
The v2.4 bidirectional completion then passes products, stars, the group law,
inverse identities and surjectivity, producing one exhaustion-independent
point-norm C0 automorphism group.

This is a deterministic sufficient theorem. It supplies no weights for Q3.
In particular, temporal full-H smoothing makes the total generator bounded
on a smooth smear, but does not by itself decompose the unbounded boundary
bond commutators into the summable bounded pieces required by (6.1).

## 7. Uniform finite Poincare plus generator convergence transfers a GNS gap

Let `A` be a unital C-star algebra and `D` a common unital star-subalgebra
contained in the domains of every `delta_n` and `delta`. For every `n`, let
`omega_n` be a state and `delta_n:D->A` a finite-volume generator. Assume
`omega_n` is invariant under its `delta_n` dynamics, so the energy form on
the left of (7.3) is real. Suppose

\[
 \omega_n\overset{w^*}{\longrightarrow}\omega,
 \qquad
 \|\delta_n(A)-\delta(A)\|\longrightarrow0
 \quad(A\in D),                                      \tag{7.1}
\]

where `delta=d/dt alpha_t|_(t=0)` for an `omega`-invariant point-norm C0
group `alpha`. Let `Delta_n>0` satisfy

\[
 \liminf_n\Delta_n\geq\Delta>0                       \tag{7.2}
\]

and assume the finite Poincare inequalities

\[
 -i\hbar\,\omega_n(A^*\delta_n(A))
 \geq\Delta_n\left[
  \omega_n(A^*A)-|\omega_n(A)|^2
 \right]
 \quad(A\in D).                                      \tag{7.3}
\]

For fixed `A`,

\[
\begin{aligned}
 &|\omega_n(A^*\delta_n(A))-\omega(A^*\delta(A))|\\
 &\quad\leq
 \|A\|\,\|\delta_n(A)-\delta(A)\|
 +| (\omega_n-\omega)(A^*\delta(A))|\longrightarrow0.
                                                               \tag{7.4}
\end{aligned}
\]

The variance in (7.3) also converges by weak-star convergence. Taking the
lower limit gives

\[
 -i\hbar\,\omega(A^*\delta(A))
 \geq\Delta\left[
  \omega(A^*A)-|\omega(A)|^2
 \right].                                            \tag{7.5}
\]

Now assume the target GNS implementation has `H>=0`, `H Omega=0`, and the
energy identity

\[
 -i\hbar\,\omega(A^*\delta(A))
 =\langle\pi(A)\Omega,H\pi(A)\Omega\rangle.          \tag{7.6}
\]

Finally assume the centered linear space

\[
 {\cal C}_D=\{\pi(A)\Omega-\omega(A)\Omega:A\in D\} \tag{7.7}
\]

is a form core for `H^(1/2)` on `Omega-perp`. Since `H Omega=0`, equations
(7.5)--(7.7) give on that core

\[
 \|H^{1/2}\xi\|^2\geq\Delta\|\xi\|^2.              \tag{7.8}
\]

Closure of the quadratic form extends (7.8) to its full domain in
`Omega-perp`. Therefore

\[
 H|_{\Omega^\perp}\geq\Delta.                        \tag{7.9}
\]

The target GNS ground vector is simple and its spectral gap is at least
`Delta`.

The exact two-level equality fixture takes
`H=diag(0,Delta)`, `omega=|0><0|`, and
`A=c|1><0|`. Then

\[
 \operatorname{Var}_\omega(A)=|c|^2,
 \qquad
 -i\hbar\omega(A^*\delta(A))=\Delta|c|^2.           \tag{7.10}
\]

For `Delta=3` and `c=2/5`, the two sides are `4/25` and `12/25`, so equality
holds in the gap ratio.

## 8. Uniform finite gaps and weak-star states do not identify the target

On `M_2`, let

\[
 \omega_n=|0\rangle\langle0|,
 \qquad H_n=n|1\rangle\langle1|,
 \qquad \hbar=1.                                     \tag{8.1}
\]

Every state is exactly the same simple ground state, so weak-star convergence
is trivial. Every finite gap is `n`, hence is uniformly at least one. For
`A=|1><0|`, however,

\[
 \delta_n(A)=i[H_n,A]=inA,
 \qquad
 -i\omega_n(A^*\delta_n(A))=n,
 \qquad \operatorname{Var}_{\omega_n}(A)=1.          \tag{8.2}
\]

Moreover

\[
 \|\delta_m(A)-\delta_n(A)\|=|m-n|.                 \tag{8.3}
\]

The local generators are not norm Cauchy. The convergent states and uniform
finite gaps therefore identify no prescribed target generator to which
(7.3) could pass. This proves
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-GAPS-PLUS-WEAKSTAR-STATES-AUTOMATIC-TARGET-GENERATOR-AND-GNS-GAP-TRANSFER`.

This is distinct from the existing post-hoc direct-sum negative. That record
rejects declaring separately reconstructed phasewise systems to be one common
dynamics; the present fixture isolates the missing generator-convergence
premise even when the finite ground state is literally constant.

## 9. Exact arithmetic fixtures

The executable package independently checks the following derived values.

For `J=8` and `Gamma=96`, exhaustive enumeration of the `3^4` forward-star
labels gives kernel dimension two, low-disagreement energy sixteen,
one-high-neighbour energy twenty-four, high-centre energy seventy-two, and
exact gap sixteen. With `alpha=1/100` and `beta=1/1000`, the normalized
grouped additive input is `3/16000`.

For `C_alpha=16`, `C_beta=8`, `a_2=b_2=g_0=1`, and `N_1=10`, equation
(4.5) gives `N_*=11`; both strict inequalities hold at eleven.

The two-dimensional modulation witness `A=sigma_x` and
`M=diag(1,-1)` has distance two, whereas every diagonal witness has distance
zero. The geometric shell choice `B_r=2^(-r)` has tail `1/16` beyond shell
four. Equations (7.10) and (8.1)--(8.3) give the GNS and negative fixture
values recorded in the manifest.

## 10. Devil's-advocate audit

1. **Does the exact two-kernel star prove two phases? UPHELD as an
   overclaim.** It supplies the classical reference datum. The required
   direct infinite-dimensional applicability or a cutoff-stable passage
   theorem and the dimension/cutoff/N-independent theorem rectangle remain
   explicit premises.
2. **Can the one-phase selector theorem be reused at zero source? UPHELD as
   an overclaim.** The reference here has two kernels and needs a genuine
   two-phase theorem. The v2.9 selector add-subtract ratio remains one.
3. **Is the threshold non-strict at an integer equality? DISMISSED.** The
   leading `1+floor` in (4.5) makes every admitted integer strictly exceed
   both real thresholds.
4. **Does (5.6) classify the whole two-site continuous part? UPHELD as an
   overclaim.** It classifies only `C(beta) intersect (B(H_x) tensor I)`.
   Two-site compacts remain continuous.
5. **Can essential supremum be replaced by supremum without proof?
   DISMISSED.** Lower semicontinuity of `F_A` and positivity of Lebesgue
   measure on nonempty open sets supply the equality.
6. **Is the shell premise merely the desired pairwise Cauchy conclusion in
   disguise? DISMISSED.** The primitive estimate toggles one interaction
   label and is required uniformly over every intermediate background and
   insertion order. The arbitrary-pair estimate is the telescope (6.3).
7. **Can finite backgrounds contain every label through a shell if the label
   set is not locally finite? DISMISSED by hypothesis.** Equation (6.0)
   explicitly requires every bounded shell union to be finite.
8. **Does temporal smoothing prove the shell premise? UPHELD as an
   overclaim.** It bounds the total generator of a smear, not each unbounded
   boundary-bond contribution with a summable spatial envelope.
9. **Do finite gaps and state convergence suffice for (7.9)? UPHELD as an
   overclaim.** Section 8 has constant states and increasing gaps but no
   Cauchy local generators.
10. **Does generator convergence alone give a GNS gap? UPHELD as an
   overclaim.** Positivity, the target energy identity, and the centered
   `H^(1/2)` form-core property are separately load-bearing.

## 11. No-overclaim boundary

R-167 v3.0 proves the exact forward-star kernel and gap, an exact conditional
common-radius entry calculation, the standard-cylinder modulation-commutant
classification, a conditional summable single-toggle-shell completion, and
an abstract Poincare/common-generator-to-GNS-gap transfer. It proves no
direct full-oscillator two-phase applicability, cutoff-stable passage,
dimension-uniform two-phase radius, zero-source full-oscillator coexistence,
actual Q3 shell summability, all-shape common alpha, phase-KMS quotient
identification, Q3 target-generator convergence, centered Q3 GNS form core,
or broken-sector GNS gap.

No v3.0 PDF is issued at this proof-first stage. No regulator removal,
continuum, physical empty-space comparison, below-empty sign, Round-1, C6,
CP1, physical Sector A, or Pre-A closure is asserted.
