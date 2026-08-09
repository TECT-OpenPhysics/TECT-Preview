# Pre-A CP1/CL8 centered-nodal Q3 Nelson--Boue--Dupuis and seam limit

**Candidate:** `PA-CP1-CL8-CENTERED-NODAL-Q3-NELSON-BOUE-DUPUIS-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-CENTERED-NODAL-Q3-UI-L1-TV-RP-AND-FIXED-BAND-FULL-WEYL-LIMIT`  
**Exploration:** `EXP-000772`
**Authority:** claim-nonbearing T0 analytic theorem

## 1. The theorem

Let `Lambda_M=Z/MZ`, `a=L/M`, and integrate with

\[
 dz_M=dt\,a\sum_{j\in\Lambda_M}
\]

on `T_(beta0) x Lambda_M`, with even `M`.  Let

\[
 A_M=m_0^2-\partial_t^2-\Delta_a,qquad m_0>0,            \tag{1.1}
\]

and let `Y_M` have eight independent components with covariance `A_M^-1`.
For

\[
 P_M(x)={1\over2}x^TK_Mx+W_4(x),\quad
 \sup_M\|K_M\|\leq\kappa,\quad g>0,\quad\lambda\geq0,   \tag{1.2}
\]

the exact Q3 quartic obeys

\[
 W_4(x)\geq {g\over32}|x|^4.                              \tag{1.3}
\]

Define the signed interaction using the whole polynomial Wick convention,

\[
 R_M=-\int :P_M(Y_M):_{\sigma_M}\,dz_M,qquad
 \sigma_M=\mathbb E Y_{M,e}(z)^2.                         \tag{1.4}
\]

Then, for every `s>0`,

\[
 \boxed{\sup_M\mathbb E e^{sR_M}<\infty.}                \tag{1.5}
\]

Combined with EXP-000770, (1.5) proves full-sequence `L1` and total-
variation convergence of the normalized centered-nodal Q3 densities to the
same Nagoji Q3 measure as the spatial-spectral comparator.  Finite-regulator
reflection positivity passes to this limit.

The same estimate holds locally uniformly after the correctly typed affine
seam shift.  It yields full-sequence, locally uniform convergence of all
fixed-band centered interacting Weyl characteristics and a regular limiting
CCR state on the inductive finite-mode Weyl algebra.

The theorem is for the bounded renormalized matrix family.  It is not a
theorem for the original cutoff-independent raw CL8 quadratic.

## 2. Scalar convention and the energy firewall

For common diagonal covariance `C`,

\[
 :W_4:_C=W_4+{1\over2}x^T[-3C\{(g+\lambda)I+
 \lambda L_{Q3}\}]x+6C^2(g+4\lambda),                   \tag{2.1}
\]

\[
 :{1\over2}x^TKx:_C={1\over2}x^TKx-{C\over2}\operatorname{Tr}K. \tag{2.2}
\]

Thus `E R_M=0`.  If a Hamiltonian instead writes an ordinary quadratic plus
`:W4:`, its exponent differs from (1.4) by the deterministic volume scalar
`(C/2)Tr K`.  The normalized density is identical, but the raw value of
`E exp(sR_M)` changes under such scalars.  Equation (1.5) therefore uses the
whole-Wick-centered representative.

This normalization does not fix absolute energy.  In particular it supplies
no energy below empty space; the common physical reference remains open.

## 3. Finite-dimensional variational reduction

Let `P_N^t` retain the temporal frequencies `|n|<=N`, set
`Y_(M,N)=P_N^tY_M`, and Wick order at its matching covariance.  Apply the
finite-dimensional Boue--Dupuis formula first to `min(sR_(M,N),B)`.  For a
control `theta`, its Cameron--Martin image `I_theta` satisfies exactly

\[
 \|I_\theta\|_{H_M^1}^2
 \leq\int_0^1\|\theta_u\|_2^2du.                          \tag{3.1}
\]

It therefore suffices to bound uniformly in `M,N,B`

\[
 sR_{M,N}(Y+I)-{1\over2}\int_0^1\|\theta_u\|_2^2du.      \tag{3.2}
\]

The bound below is independent of all three cutoffs.  Monotone convergence
removes `B`.  At fixed `M`, Wick convergence as `N` tends to infinity and
Fatou remove the temporal cutoff.  No infinite-dimensional use of the
variational formula is hidden.

## 4. Wick translation, coercivity, and exact exponents

For every component multi-index,

\[
 :Y^\alpha:(Y+I)=
 \sum_{\gamma\leq\alpha}{\alpha\choose\gamma}
 :Y^\gamma:I^{\alpha-\gamma}.                            \tag{4.1}
\]

Consequently the deterministic part is the actual non-radial `P_M(I)`, and

\[
 sP_M(I)\geq {sg\over64}\|I\|_4^4
              -{4s\kappa^2\over g}\,\beta_0L.            \tag{4.2}
\]

Fix `epsilon=1/8`.  If `r=|alpha-gamma|` is `1`, `2`, or `3`, the uniform
fractional product and Gagliardo--Nirenberg estimate is

\[
 \|I^r\|_{W_M^{\epsilon,4/r}}
 \leq C_r\|I\|_4^{r-1/4}\|I\|_{H_M^1}^{1/4}.             \tag{4.3}
\]

Pair with `X_gamma=:Y^gamma:` in `W_M^(-epsilon,4/(4-r))`.
The fraction of the two coercive powers consumed by (4.3) is

\[
 d_r={r-1/4\over4}+{1/4\over2}={4r+1\over16}.             \tag{4.4}
\]

Generalized Young therefore raises the random norm to

\[
 q_r={1\over1-d_r}:qquad
 q_1={16\over11},\quad q_2={16\over7},\quad q_3={16\over3}. \tag{4.5}
\]

There are only finitely many Q3 monomials.  Choosing their Young parameters
jointly leaves positive multiples of `||I||_4^4` and `||I||_(H1)^2`, while
the remainder is a finite sum of Wick norms with maximal moment `16/3`.
Terms with `r=0` are random constants with uniform first moments.

## 5. The all-M hybrid-lattice Wick estimate

Write frequencies as `Gamma_M=Z x I_M`.  The centered-symbol sandwich gives

\[
 c_M(n,m)={1\over\nu_n^2+m_0^2+\widehat k_a(m)^2}
 \leq{\pi^2\over4}{1\over\nu_n^2+m_0^2+k_m^2}
 ={\pi^2\over4}c(n,m).                                   \tag{5.1}
\]

For a chaos of degree `d<=4`, every cyclic equation for the spatial momenta
lifts uniquely to an ordinary equation with total momentum `m+ell M` for one
of finitely many `|ell|<=d`.  Dropping the individual Brillouin restrictions
only increases the convolution sum, so

\[
 \mathbb E|\widehat{:Y^\gamma:}(n,m)|^2
 \leq\gamma!({\pi^2\over4})^d
 \sum_{|\ell|\leq d}c^{*d}(n,m+\ell M).                  \tag{5.2}
\]

Splitting one convolution variable into the two near regions and their
complement proves inductively that, for every `eta>0`,

\[
 c^{*d}(p)\leq B_{d,\eta}\langle p\rangle^{-2+\eta},
 \qquad d=1,2,3,4.                                       \tag{5.3}
\]

The only borderline sum is logarithmic and is absorbed into `eta`.  Since
`m` is the nearest representative, every nonzero lift is at least as large
as `m`, including the Nyquist equality case.  Thus the constant in (5.2) is
independent of `M` and of the temporal cutoff.

For a dyadic block, (5.2)--(5.3) give

\[
 \mathbb E|\Delta_j^M:Y^\gamma:(z)|^2\leq C2^{\eta j}.   \tag{5.4}
\]

Finite-chaos hypercontractivity, the vector-valued square function, and a
choice `eta<2epsilon` imply

\[
 \sup_{M,N}\mathbb E
 \|:Y_{M,N}^\gamma:\|_{W_M^{-\epsilon,p}}^q<\infty       \tag{5.5}
\]

for every finite `p,q` required by (4.5).  Temporal blocks above the spatial
Nyquist contain fewer modes than the two-dimensional counting bound and do
not create a loophole.

For positive regularity, use the piecewise-linear spatial extension.  Its
cellwise `Lp` norm is uniformly equivalent to the nodal norm and

\[
 \|\partial_xE_Mu\|_2=\|D_a^+u\|_2.                      \tag{5.6}
\]

Continuum two-dimensional GN gives (4.3) at the endpoint; the exact discrete
Leibniz identity

\[
 D_a^+(uv)=(D_a^+u)v(\cdot+a)+uD_a^+v                   \tag{5.7}
\]

and interpolation give the fractional product estimate with an `M`-
independent constant.  Equations (4.2)--(5.7) close (1.5).

## 6. Full-sequence density and reflection-positive limit

EXP-000770 proves `R_M->R` in `L2`, hence in probability.  Taking `s=2` in
(1.5), Vitali gives

\[
 \|e^{R_M}-e^R\|_{L^1(\mu)}\longrightarrow0.             \tag{6.1}
\]

Centering and Jensen give `Z_M=E exp(R_M)>=1`, so `Z_M->Z>0` and

\[
 \left\|{e^{R_M}\over Z_M}-{e^R\over Z}\right\|_1
 \longrightarrow0.                                      \tag{6.2}
\]

This is full-sequence total-variation convergence on the common distribution
space.  Bounded reflected cylinder quadratic forms pass through (6.2), so the
Nagoji Q3 limit inherits the exact finite centered time-reflection positivity.

## 7. Exact affine seam

For a fixed-band smooth spatial label `h`, put

\[
 r_h(t)=(t/\beta_0-1/2)h,qquad
 A_{x,M}=m_0^2-\Delta_a.                                 \tag{7.1}
\]

An open path `q(beta0)=q(0)+h` becomes the periodic path `phi=q-r_h`.
The time-derivative cross term telescopes to zero.  Since
`integral s(t)^2dt=beta0/12`, the exact free-action identity is

\[
 S_{0,M}(\phi+r_h)-S_{0,M}(\phi)
 ={\|h\|_a^2\over2\beta_0}+L_{M,h}(\phi)
 +{\beta_0\over24}\langle h,A_{x,M}h\rangle_a,           \tag{7.2}
\]

\[
 L_{M,h}(\phi)=\int_0^{\beta_0}(t/\beta_0-1/2)
 \langle\phi(t),A_{x,M}h\rangle_a dt.                   \tag{7.3}
\]

The midpoint of the two seam endpoints is exactly `phi(0)`.  Thus the finite
Weyl characteristic is

\[
 \chi_M(f,h)=e^{-c_M(h)}
 {\mathbb E_{\mu_M}[e^{i\langle f,\phi(0)\rangle_a}
 e^{R_M(\phi+r_h)-L_{M,h}(\phi)}]
  \over\mathbb E_{\mu_M}e^{R_M(\phi)}},                  \tag{7.4}
\]

\[
 c_M(h)={\|h\|_a^2\over2\beta_0}
       +{\beta_0\over24}\langle h,A_{x,M}h\rangle_a.   \tag{7.5}
\]

Using only `m0^2` instead of `A_(x,M)` would be wrong for spatially varying
`h`.

## 8. Shifted uniform integrability and full Weyl limit

The periodic representative of `r_h` is bounded and of bounded variation in
time.  It multiplies `W^(epsilon,p)` whenever `epsilon<1/p`; `epsilon=1/8`
works for every exponent above.  In the variational proof replace `I` by
`I+r_h`.  The elementary inequality

\[
 |I+r_h|^4\geq |I|^4/8-|r_h|^4                          \tag{8.1}
\]

retains coercivity uniformly for `h` in a compact fixed-band set.  All new
terms contain only bounded deterministic multipliers; `L_(M,h)` is absorbed
by the `H1` control and a uniform Gaussian norm.  Therefore, for every
`s>0` and compact fixed-band `H`,

\[
 \sup_M\sup_{h\in H}\mathbb E\exp\{s[R_M(Y+r_h)-L_{M,h}(Y)]\}<\infty. \tag{8.2}
\]

Wick translation reduces shifted action convergence to chaoses of degree at
most three.  The sawtooth has Sobolev regularity below `1/2`; a fixed spatial
band changes aliases only to `ell M+O(K)`, whose convolution tails still
vanish uniformly on compact `h` sets.  Also `A_(x,M)h->A_xh` at `O(a^2)`.
Thus the shifted exponent converges locally uniformly in probability, and
(8.2) plus Vitali passes the numerator of (7.4).

The exact finite midpoint identity, finite Weyl positivity, and EXP-000771
identity equicontinuity now prove full-sequence locally uniform convergence on
every fixed finite symplectic mode space.  The limit is a regular state on the
inductive finite-mode Weyl algebra.

## 9. Prior art, adversarial review, and boundary

Nagoji supplies the general multivariate terminal variational architecture.
Barashkov--Gunaratnam--Hofstetter Lemma 5.9 supplies a scalar lattice Nelson
precedent.  Delgadino--Smith supplies a radial vector nodal precedent.  None
states the hybrid centered-dispersion, non-radial Q3 matrix-counterterm and
affine-seam theorem above.  This bounded comparison is not a world-first or
novelty proof.

Hostile objections checked in the proof and executable audits are:

1. A deterministic scalar can fake a raw exponential bound: fixed by the
   whole-Wick representative; absolute energy stays open.
2. The original fixed-raw family has a divergent renormalized quadratic:
   excluded explicitly.
3. Nodal aliases could evade ordinary Fourier estimates: handled by every
   finite cyclic lift, including Nyquist.
4. Continuous Euclidean time could hide an infinite-dimensional variational
   step: removed by the finite temporal projector and Fatou.
5. The non-radial Q3 valleys could defeat radial coercivity: the independent
   onsite bound `g>0` is retained; `g=0` is outside scope.
6. A massless zero mode could defeat the Gaussian base: `m0>0` is essential.
7. Unshifted integrability need not imply seam integrability: (8.2) is proved
   separately.
8. The sawtooth is not a periodic Cameron--Martin vector: no such quasi-
   invariance is used.
9. Omitting `-Delta_a` from (7.2) gives a false spatially varying seam: the
   full `A_(x,M)` is retained.
10. Normalized density convergence could be mistaken for a physical energy
    comparison: energy below empty space remains open.

This theorem does not prove complete OS/Markov/Hadamard reconstruction, a
beta-independent Hamiltonian, physical KMS/ground/beta selection, the
original three-dimensional Q3 parent, a physical vacuum or energy below empty
space, a genuine phase transition, physical light, C0, N1--N5, C6, CP1,
Sector A, or Pre-A.

## 10. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_nodal_q3_nelson_boue_dupuis_seam_limit_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_nodal_q3_nelson_boue_dupuis_seam_limit_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_nodal_q3_nelson_boue_dupuis_seam_limit_route_split_verify.py --self-test
```
