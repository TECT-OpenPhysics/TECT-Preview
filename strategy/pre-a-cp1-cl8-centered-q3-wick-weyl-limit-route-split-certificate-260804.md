# Pre-A CP1/CL8 centered Q3 Wick and Weyl limit route split

**Candidate:** `PA-CP1-CL8-CENTERED-Q3-WICK-WEYL-LIMIT-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-UNIT-FREE-RP-WEYL-SEAM-AND-CENTERED-Q3-WICK-LP-LIMIT-WITH-UI-GATES`  
**Exploration:** `EXP-000770`
**Status:** T0, claim-nonbearing; C6 remains `T1 / ACTIVE / CONDITIONAL`

<a id="section-1-verdict"></a>
## 1. Verdict

This checkpoint closes five exact pieces of the centered CL8-to-Q3 route:

1. the `chi,c,hbar`, Euclidean-time, field and coupling dictionary;
2. full-sequence convergence of the centered free Gaussian field in every
   `H^{-s}`, `s>0`, together with time reflection positivity;
3. the fixed-mode free joint Weyl limit;
4. `L2`, hence every fixed finite `Lp`, convergence of the renormalized
   centered-nodal Q3 Wick interaction; and
5. the exact finite-regulator twisted-Weyl heat-kernel seam identity.

It also proves two route boundaries.  First, the original cutoff-independent
raw CL8 quadratic is not a fixed finite renormalized Q3 family.  Second,
finite-`Lp` convergence of the Wick action does not imply convergence of its
exponential probability weights.

The centered interacting probability limit is therefore not yet closed.  Its
next load-bearing lemma is a centered-nodal uniform exponential moment.  The
full interacting CCR limit additionally needs an off-diagonal seam estimate.

<a id="section-2-prior-art"></a>
## 2. Prior-art boundary

The complete TECT sequence -- horizon-origin input, C0/N1--N5, the CL8/Q3
parent, state selection, physical reference and Sector-A handoff -- was not
located as one proved theory.  This bounded search is not a world-first or
novelty proof.  Its ingredients have strong prior art:

1. M. G. Delgadino and S. A. Smith, *Mass generation for the two dimensional
   O(N) Linear Sigma Model in the large N limit*, arXiv:2601.19630v1,
   <https://arxiv.org/abs/2601.19630>.  Definition 3.1 and Appendix D give a
   particularly close vector centered-lattice precedent, including a
   total-variation lattice limit and inherited reflection positivity.
2. H. Nagoji, *Construction of the Gibbs measures associated with Euclidean
   quantum field theory with various polynomial interactions in the Wick
   renormalizable regime*, arXiv:2305.19583v2,
   <https://arxiv.org/abs/2305.19583>.  EXP-000766/760 already instantiate its
   multivariate terminal-measure theorem for the Q3 polynomial.
3. F. Guerra, L. Rosen and B. Simon, *The P(phi)2 Euclidean quantum field
   theory as classical statistical mechanics*, Ann. Math. 101 (1975),
   <https://www.jstor.org/stable/1970988>, and S. Albeverio, M. Bernabei and
   Z.-M. Zhou, *On the continuum limit of lattice approximations to phi4_2
   models*, J. Math. Phys. 45 (2004),
   <https://doi.org/10.1063/1.1626807>, are scalar lattice precedents.
4. M. Rodriguez Zarate and T. Thiemann, *Hamiltonian renormalisation VIII.
   P(Phi,2) quantum field theory*, arXiv:2505.13030v2,
   <https://arxiv.org/abs/2505.13030>, gives a related scalar Weyl-algebra and
   finite-resolution renormalisation programme.

The `O(N)` quartic is radial.  Its scalar contraction cannot be imported as
the Q3 answer: the twelve-edge Q3 polynomial produces an independent graph-
Laplacian counterterm.  None of the cited sources identifies the registered
CL8 units, the original fixed-raw Hamiltonians, the off-diagonal Q3 seam, the
three-dimensional Q3LOCK parent, or the physical state and energy reference.

<a id="section-3-unit-dictionary"></a>
## 3. Exact CL8-to-Euclidean unit dictionary

The registered inserted-one-dimensional Hamiltonian has

\[
 w={a\over8},\qquad p=w\Pi,
\]

\[
 H_a=\sum_j {|p_j|^2\over2\chi w}
 +w\sum_j\left\{{c\over2}|D_aq_j|^2+W(q_j)\right\}.
 \tag{3.1}
\]

The Gibbs parameter `beta_H` has inverse-energy units.  Physical Euclidean
time is `delta=hbar*t`, and its circumference is `hbar*beta_H`.  Set

\[
 \tau=\sqrt{c/\chi}\,\delta,
 \qquad
 s^2={\sqrt{\chi c}\over8\hbar},
 \qquad
 \phi=sq .                                                \tag{3.2}
\]

Then the exact finite-lattice Euclidean action is

\[
 {S_{E,a}\over\hbar}
 =\int_0^{\beta_0}d\tau\,a\sum_j
 \left\{{1\over2}|\partial_\tau\phi_j|^2
       +{1\over2}|D_a\phi_j|^2+P_E(\phi_j)\right\},       \tag{3.3}
\]

where

\[
 \beta_0=\hbar\beta_H\sqrt{c/\chi}.                       \tag{3.4}
\]

For the CL8/Q3 polynomial the canonical Euclidean coefficients are

\[
 K_E={K_{\rm CL8}\over c},\qquad
 g_E={8\hbar g\over\sqrt\chi\,c^{3/2}},\qquad
 \lambda_E={8\hbar\lambda\over\sqrt\chi\,c^{3/2}}.     \tag{3.5}
\]

If the base Gaussian covariance is `(-Delta+m0^2)^{-1}`, the ordinary
quadratic in the interaction is the residual

\[
 K_{\rm int}=K_E-m_0^2I                                  \tag{3.6}
\]

plus any separately declared finite Q3-matrix direction.  Equation (3.6)
prevents double-counting the base mass.

This is a dictionary, not an origin theorem.  `hbar`, the Euclidean period,
`chi`, `c`, and the inserted one-dimensional reduction are still inputs.

<a id="section-4-free-centered"></a>
## 4. Full-sequence centered free limit

Let `nu_n=2pi n/beta0`, let `k=2pi m/L` be a centered Brillouin label, and
put

\[
 \widehat k_a^2={4\over a^2}\sin^2{ak\over2},
 \qquad
 G_a(n,k)={1\over\nu_n^2+m_0^2+\widehat k_a^2}.            \tag{4.1}
\]

For `|ak|<=pi`, concavity of sine on the half interval gives

\[
 {4\over\pi^2}k^2\le\widehat k_a^2\le k^2.               \tag{4.2}
\]

Couple the centered and continuum spectral fields with the same Fourier
white noises.  Every fixed multiplier converges, and (4.2) supplies the
summable domination

\[
 (1+n^2+k^2)^{-s}
 |G_a^{1/2}-G^{1/2}|^2
 \lesssim (1+n^2+k^2)^{-1-s}.                             \tag{4.3}
\]

The right side is summable in two dimensions for every `s>0`.  Dominated
convergence proves

\[
 \Phi_a\longrightarrow\Phi
 \quad\hbox{in }L^2(\Omega;H^{-s}(\mathbb T^2))
 \quad\hbox{for every }s>0                               \tag{4.4}
\]

along the full sequence.  This also gives all fixed Fourier finite-
dimensional distributions.  Uniform `H^{-s0}` moments followed by the compact
embedding `H^{-s0}->H^{-s}`, `0<s0<s`, give an independent tightness route.

For each spatial mode set

\[
 \omega_{a,k}=\sqrt{m_0^2+\widehat k_a^2}.
\]

On `0<=t,s<=beta0/2`, the time-reflected circle covariance is

\[
 C_{a,k}(t+s)=a_{a,k}
 \{e^{-\omega_{a,k}t}e^{-\omega_{a,k}s}
 +e^{-\omega_{a,k}(\beta_0/2-t)}
  e^{-\omega_{a,k}(\beta_0/2-s)}\},                       \tag{4.5}
\]

with positive `a_(a,k)`.  It is a sum of two rank-one positive kernels.
Products over modes and eight species remain reflection positive.  Weak
convergence passes this inequality to bounded continuous positive-half
cylinders in the free limit.

<a id="section-5-wick-limit"></a>
## 5. Renormalized centered-nodal Q3 Wick convergence

This section concerns the EXP-000765 matrix-counterterm family after the unit
map (3.2)--(3.5), not the original fixed-raw CL8 polynomial.

For one Wick monomial of degree `d<=4`, first replace the nodal spatial sum by
the continuous spatial integral of the same centered Fourier interpolant.
Under the common white-noise coupling, the resulting `d`th-chaos kernels
converge pointwise.  The covariance sandwich (4.2) bounds their squared norms
by

\[
 d!\left({\pi^2\over4}\right)^d(G^{*d})(0)<\infty.        \tag{5.1}
\]

Dominated convergence closes this first difference.

The nodal quadrature zero mode consists of the exact total-momentum-zero
sector plus alias sectors

\[
 k_1+\cdots+k_d=\ell M,
 \qquad 0<|\ell|\le d/2.                                  \tag{5.2}
\]

For the massive two-torus Green kernel `C`, every `C^d` is integrable.
Consequently its Fourier coefficients tend to zero at infinity by the
Riemann--Lebesgue lemma.  Each of the finitely many sectors in (5.2) therefore
vanishes.  Summing the finitely many Q3 monomials proves

\[
 R_M^{\rm nod}\longrightarrow R
 \quad\hbox{in }L^2(\Omega).                              \tag{5.3}
\]

The difference lies in the direct sum of chaoses of orders at most four.
Gaussian hypercontractivity therefore upgrades (5.3) to

\[
 \|R_M^{\rm nod}-R\|_{L^p}\longrightarrow0
 \quad\hbox{for every fixed finite }p.                    \tag{5.4}
\]

As a finite exact control, if every spatial input has bandwidth `K`, its
degree-at-most-four product has bandwidth at most `4K`; `M>4K` leaves no
nonzero multiple of `M`, so nodal quadrature is exact.

Every finite centered law is time-local and reflection positive.  Passing
that property to the interacting limit, however, requires convergence of the
normalized probability weights, not only (5.3).

<a id="section-6-counterterm"></a>
## 6. Fixed-raw no-go and the required Q3 tuning

For common diagonal coincidence covariance `C_M`, the registered Wick ledger
is

\[
 :W_4:_{C_M}=W_4+{1\over2}q^T\delta K(C_M)q
              +6C_M^2(g_E+4\lambda_E),                    \tag{6.1}
\]

\[
 \delta K(C_M)=-3C_M
 [(g_E+\lambda_E)I+\lambda_E L_{Q3}].                     \tag{6.2}
\]

Thus a raw polynomial with quadratic `K_raw(M)` represents finite
renormalized quadratic

\[
 K_R=K_{\rm raw}(M)+3C_M
 [(g_E+\lambda_E)I+\lambda_E L_{Q3}].                     \tag{6.3}
\]

On Q3 Walsh level `s=0,1,2,3`, the matrix in brackets has eigenvalue

\[
 g_E+\lambda_E+2s\lambda_E>0.                             \tag{6.4}
\]

Since `C_M=Theta(log M)`, fixed `K_raw` makes every level of (6.3) diverge.
It cannot converge to a fixed finite Nagoji quadratic.  The necessary tuning
is

\[
 \boxed{K_{\rm raw}(M)=K_R-3C_M
 [(g_E+\lambda_E)I+\lambda_E L_{Q3}]}                     \tag{6.5}
\]

up to the declared scalar-energy convention.  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT`.

If a Hamiltonian is already Wick ordered at the zero-temperature covariance
`C_(0,M)`, changing to the beta-circle loop covariance `C_(beta,M)` needs only
the finite thermal correction.  Indeed

\[
 C_{0,M}-C_{\beta,M}
 =-{1\over L}\sum_k{1\over
 \omega_{a,k}(e^{\beta_0\omega_{a,k}}-1)},                \tag{6.6}
\]

whose spatial sum converges absolutely as `M` tends to infinity.

<a id="section-7-ui"></a>
## 7. Exact exponential-integrability gate

The spectral spatial martingale of EXP-000769 obeys a conditional-Jensen
bound.  The centered-dispersion nodal approximants are not conditional
expectations of the terminal field, so that argument cannot be transferred.

The required estimate is, for some `eta>0`,

\[
 \boxed{\sup_M\mathbb E\exp[(1+\eta)R_M^{\rm nod}]<\infty.} \tag{7.1}
\]

Taking `eta=1` matches the existing Cauchy--Schwarz/Vitali route.  Once (7.1)
is proved, (5.3), uniform integrability and Vitali give `L1` convergence of
the unnormalized weights and hence of the normalized densities to the unique
Nagoji Q3 density.  The finite reflection forms then pass to that limit.

No inference from `L2` alone can supply (7.1).  Let `X_N=N` on an event of
probability `N^{-4}` and zero elsewhere.  Then

\[
 \|X_N\|_2=N^{-1}\to0,
 \qquad
 \mathbb E e^{X_N}=1-N^{-4}+N^{-4}e^N\to\infty.           \tag{7.2}
\]

This proves the inference no-go
`NG-2026-08-04-PRE-A-CP1-CL8-WICK-L2-ONLY-INTERACTING-DENSITY-LIMIT`.
It is not a counterexample to the actual Q3 family; it identifies the missing
lemma exactly.

<a id="section-8-weyl-seam"></a>
## 8. Exact finite-regulator twisted-Weyl seam

For finite `M`, define

\[
 \Phi_a(f)=\langle f,q\rangle_w,
 \qquad
 \Pi_a(h)=h\cdot p,
 \qquad
 \langle f,q\rangle_w=w\sum_i f_iq_i.                    \tag{8.1}
\]

The symmetric Weyl operator

\[
 W_a(f,h)=\exp\{i[\Phi_a(f)+\Pi_a(h)]/\hbar\}
\]

acts as

\[
 (W_a(f,h)\psi)(q)
 =e^{i\langle f,q+h/2\rangle_w/\hbar}\psi(q+h).          \tag{8.2}
\]

Let `K_(a,beta)(x,y)` be the symmetric kernel of `exp(-beta H_a)` and
`Z_a=Tr exp(-beta H_a)`.  Direct kernel composition gives

\[
 \boxed{
 \chi_{a,\beta}(f,h)
 ={1\over Z_a}\int
 e^{i\langle f,x\rangle_w/\hbar}
 K_{a,\beta}(x+h/2,x-h/2)\,dx .}                          \tag{8.3}
\]

Equivalently, it is

\[
 {1\over Z_a}\int
 e^{i\langle f,q+h/2\rangle_w/\hbar}K_{a,\beta}(q+h,q)dq.
 \tag{8.4}
\]

The Feynman--Kac path has `q_beta=q_0+h`, and the phase is evaluated at the
endpoint midpoint.  Its free Cameron--Martin cost is

\[
 {|h|^2\over4\kappa_a\beta}
 ={\chi\|h\|_{2,w}^2\over2\hbar^2\beta},
 \qquad \kappa_a={\hbar^2\over2\chi w}.                  \tag{8.5}
\]

The affine seam is not a periodic Cameron--Martin translate of the closed
loop.  This prevents a false shortcut from diagonal loop convergence.

For a free oscillator mode of frequency `omega_a`, the exact characteristic
is

\[
 \exp\left[-{1\over4\hbar}
 \coth{\beta\hbar\omega_a\over2}
 \left(\chi\omega_a h^2+{F^2\over\chi\omega_a}\right)
 \right].                                                  \tag{8.6}
\]

Because `omega_a-omega=O(a^2)` on each fixed positive-mass mode set, (8.6)
converges at `O(a^2)` uniformly on bounded labels.  This closes the free joint
Weyl limit, not the interacting one.

<a id="section-9-ccr-criterion"></a>
## 9. Interacting regular-CCR criterion

On every fixed finite-mode symplectic test space, it is sufficient to prove:

1. asymptotically symplectic embeddings;
2. pointwise Cauchy convergence of (8.3) for every `(f,h)`; and
3. uniform equicontinuity at the identity,

\[
 \lim_{\delta\downarrow0}\sup_M\sup_{\|F\|\le\delta}
 |1-\chi_M(F)|=0.                                         \tag{9.1}
\]

Finite Weyl-matrix positivity then passes to the limit, and (9.1) makes the
limit a regular CCR state.  A minimal linewise version replaces the inner
supremum by `|1-chi_M(tF)|` for each fixed `F`.

The exact seam density

\[
 D_h(x)=K_\beta(x+h/2,x-h/2)/Z                            \tag{9.2}
\]

is positive and has total mass at most one by semigroup Cauchy--Schwarz.
Hence midpoint moments reduce to diagonal moments.  A useful next target is

\[
 \sup_M\omega_M(\Pi(h)^2)\le C_K\|h\|^2                 \tag{9.3}
\]

for `h` in each fixed low-mode space.  A total-energy bound would imply
(9.3), but is unnecessarily ultraviolet-sensitive.  Direct locally uniform
control of the seam pushforwards is the sharper route.

Diagonal Nagoji/RP convergence proves only `h=0`.  Brownian velocities and
abstract weak-star compactness do not prove (9.1).

<a id="section-10-gate-ledger"></a>
## 10. Gate ledger

Closed here:

- exact CL8 Euclidean unit and field rescaling;
- centered free full-sequence `H^{-s}` convergence;
- centered and limiting free reflection positivity;
- fixed-mode free joint Weyl convergence;
- renormalized centered-nodal Q3 Wick convergence in every fixed finite `Lp`;
- exact matrix-counterterm necessity; and
- exact finite-regulator twisted-Weyl seam identity.

Still open:

- centered Q3 uniform exponential integrability (7.1);
- centered interacting density and terminal-measure identification;
- off-diagonal seam convergence and low-mode momentum equicontinuity;
- complete interacting OS/Markov/Hadamard reconstruction;
- physical beta, ground, preparation, vacuum and energy-reference selection;
- the comparison with empty/no-condensate space and its sign;
- the original three-dimensional Q3LOCK parent;
- the origin of `hbar`, time, physical Lorentz signature and light speed;
- C0, N1--N5, C6, CP1, Sector A, and Pre-A.

The next gate is
`PA-CP1-CL8-CENTERED-Q3-UNIFORM-EXPONENTIAL-INTEGRABILITY-AND-OFFDIAGONAL-SEAM-BOUND`.

<a id="section-11-adversarial"></a>
## 11. Adversarial review

1. **The `a/8` factor disappeared. DISMISSED.**  It is carried through
   (3.1)--(3.3); the field scale is chosen only after the physical Euclidean
   time conversion.
2. **The base mass was added twice. DISMISSED.**  Equation (3.6) subtracts
   `m0^2 I` from the target quadratic.
3. **Fixed-mode convergence proves full Gaussian convergence. UPHELD AS
   INCOMPLETE BY ITSELF.**  Equation (4.3) supplies the missing summable
   domination and closes the full `H^{-s}` sequence.
4. **The old Nyquist no-go contradicts the Wick limit. DISMISSED.**  It rejects
   exact equality at finite `M`; the nonzero alias sectors vanish only in the
   controlled limit.
5. **Raw CL8 and the renormalized family are the same parameters. UPHELD AS
   FALSE.**  Equations (6.3)--(6.5) prove the logarithmically divergent Q3
   matrix tuning.
6. **`L2` convergence of interactions gives `L1` density convergence.
   UPHELD AS FALSE.**  Equation (7.2) is an exact counterexample to that
   inference.  The actual Q3 exponential estimate remains open rather than
   refuted.
7. **The Weyl phase can be placed at one endpoint. UPHELD AS CONVENTION-
   SENSITIVE.**  Symmetric Weyl ordering fixes the midpoint in (8.2)--(8.4).
8. **The seam is a translated periodic loop. UPHELD AS FALSE.**  Its affine
   representative is nonperiodic and carries the cost (8.5).
9. **Configuration convergence constructs momentum. UPHELD AS FALSE.**  It is
   the `h=0` restriction of (8.3); (9.1)--(9.3) remain separate.
10. **The closest O(N) theorem proves Q3. UPHELD AS FALSE.**  Its radial
    contraction is scalar; the Q3 Laplacian direction is load-bearing.
11. **This proves the physical vacuum or energy below empty space. UPHELD AS
    FALSE.**  Neither the physical reference nor the common normalization has
    been constructed.
12. **This completes C6 or Pre-A. UPHELD AS FALSE.**  The C6 card is unchanged,
    and Section 10 lists the remaining gates.

<a id="section-12-verification"></a>
## 12. Reproducible verification

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_centered_q3_wick_weyl_limit_route_split_verify.py --self-test
```

The primary route uses symbolic coefficient and Q3-matrix calculations,
Fourier alias enumeration, centered-symbol and reflected-kernel fixtures,
harmonic Weyl seams, and the rare-spike control.  The independent route uses
only the Python standard library, distinct grids and direct finite sums.  The
integrated verifier reruns both, checks stored artefacts and source diversity,
audits the formal records and generated surfaces, and confirms that C6 and
the below-empty-space boundary are unchanged.
