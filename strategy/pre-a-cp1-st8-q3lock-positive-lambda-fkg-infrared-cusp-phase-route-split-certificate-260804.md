# EXP-000782 certificate: positive-`lambda` Q3LOCK FKG, infrared order, DLR phase and collective-source cusp

Candidate: `PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-FKG-INFRARED-CUSP-PHASE-ROUTE-SPLIT-v0`  
Result: `PA-CP1-ST8-Q3LOCK-POSITIVE-LAMBDA-LOW-TEMPERATURE-DLR-PHASE-AND-COLLECTIVE-SOURCE-CUSP`  
Tier: T0, claim-nonbearing  
Date: 2026-08-04

<a id="section-1-result-first"></a>
## 1. Result first

This certificate closes a genuine positive-`lambda` phase theorem for the
exact fixed-spacing ST8/Q3LOCK quantum-oscillator family.  The conclusion is
not assumed from the double-well picture and is not imported from an
`O(8)`-rotation-invariant theorem whose hypotheses fail.

Let

\[
 u={1\over\sqrt 8}(1,\ldots,1),\qquad Q_y=u\mathbin\cdot q_y,
 \qquad \theta_Q={-r\over 3(g+\lambda)} .                 \tag{1.1}
\]

Assume

\[
 \hbar,\chi,c,g,\lambda>0,\qquad r<0.                    \tag{1.2}
\]

Define the three-dimensional Watson integral

\[
 {\cal I}_3={1\over(2\pi)^3}
 \int_{(-\pi,\pi]^3}{d^3p\over
 \sum_{j=1}^3(1-\cos p_j)}
 =0.505462019717326\ldots                                  \tag{1.3}
\]

and

\[
 A_0={8c\chi\theta_Q^2\over\hbar^2}.                    \tag{1.4}
\]

If `A_0 > I_3`, put

\[
 \rho=\sqrt{{\cal I}_3/A_0},\quad
 x_*={\rm artanh}\,\rho,\quad
 \beta_*={4\chi\theta_Q\over\hbar^2}x_*\rho .          \tag{1.5}
\]

Then every `beta > beta_*` has all of the following properties.

1. The collective zero-mode Duhamel density is strictly positive.
2. The thermodynamic fine-oscillator energy pressure
   \[
   P_\beta(h)=\lim_{L\to\infty}{1\over8\beta L^3}
     \log {\rm Tr}\,e^{-\beta H_L(hu)}                  \tag{1.6}
   \]
   has a strict cusp at `h=0`.
3. The zero-source tempered Euclidean DLR set contains two distinct,
   parity-related tangent states `mu_+` and `mu_-`, with opposite nonzero
   collective magnetizations.
4. Hence the exact positive-`lambda` fixed-lattice model has a
   low-temperature DLR phase transition and spontaneous global-`Z2`
   breaking in a nonempty explicit parameter regime.

For the quantitative lower bound, let `x_beta` be the unique positive solution
of

\[
 x_\beta\tanh x_\beta
 ={\beta\hbar^2\over4\chi\theta_Q},                     \tag{1.7}
\]

and set

\[
 \delta_\beta=
 \theta_Q{\tanh x_\beta\over x_\beta}
 -{{\cal I}_3\over2\beta c}>0.                          \tag{1.8}
\]

Then

\[
 D_+P_\beta(0)\ge {\sqrt{\delta_\beta}\over8},\qquad
 D_-P_\beta(0)=-D_+P_\beta(0),                          \tag{1.9}
\]

and the EXP-000781 tangent states satisfy

\[
 \int Q_0\,d\mu_+\ge\sqrt{\delta_\beta},\qquad
 \int Q_0\,d\mu_-\le-\sqrt{\delta_\beta}.             \tag{1.10}
\]

This is not an algebraic-KMS theorem, a ground-state theorem, a continuum
theorem, a physical-empty-space comparison, or Pre-A completion.

<a id="section-2-model-and-normalizations"></a>
## 2. Exact model and normalization ledger

On the coarse periodic cube `Lambda_L=(Z/LZ)^3`, `V=L^3`, the source family is

\[
\begin{split}
H_L(h)={}&\sum_{y\in\Lambda_L}\left[
 { |p_y|^2\over2\chi}+{r\over2}|q_y|^2
 +{g\over4}\sum_{e=1}^8q_{y,e}^4\right]\\
&+{\lambda\over4}\sum_y\sum_{\{e,f\}\in E(Q_3)}
 (q_{y,e}-q_{y,f})^2(q_{y,e}^2+q_{y,f}^2)\\
&+{c\over2}\sum_{\langle yz\rangle}|q_y-q_z|^2
 -h\sum_yQ_y .                                         \tag{2.1}
\end{split}
\]

The canonical commutator is
`[q_{y,e},p_{z,f}]=i hbar delta_yz delta_ef`.  Equation (2.1) is the
positive-difference form of the exact EXP-000780/774 Hamiltonian, not a new
comparator.

Three normalizations must not be mixed:

\[
 p_{\beta,L}(h)={1\over V}\log Z_L(h),\qquad
 P_{\beta,L}(h)={p_{\beta,L}(h)\over8\beta},             \tag{2.2}
\]

\[
 (A,B)_{D,L}={1\over\beta}\int_0^\beta
 \langle A(\tau)B(0)\rangle_{L,c}\,d\tau .             \tag{2.3}
\]

At zero source, parity makes the connected and raw two-point functions of
`Q` equal.  The pressure relation `p=8 beta P` is the source of the factor
`1/8` in (1.9); there is no extra `beta` in the physical energy-pressure
slope.

<a id="section-3-continuous-loop-fkg"></a>
## 3. Continuous-loop FKG for the exact nonradial onsite law

Choose any harmonic splitting `a>0` and set `m=chi/hbar^2`.  The one-coordinate
periodic Ornstein--Uhlenbeck reference has covariance operator

\[
 (-m\,d^2/d\tau^2+a)^{-1}.                              \tag{3.1}
\]

The positive `a` is essential: the pure periodic kinetic operator has an
improper constant zero mode.  The compensating one-coordinate term is absorbed
into the local potential and changes no mixed derivative.

For `t>0`, the Mehler kernel has

\[
 \partial_x\partial_y\log K_t(x,y)
 ={m\omega\over\sinh(\omega t)}>0,
 \qquad\omega=\sqrt{a/m}.                               \tag{3.2}
\]

The closing periodic-time kernel has the same sign.  Thus every finite-time
OU skeleton is MTP2.  Products over sites and components remain MTP2.

All off-diagonal energy derivatives of the interacting time-slice law have
the attractive sign.  A spatial bond gives

\[
 \partial_{q_{y,e}}\partial_{q_{z,e}}
 {c\over2}(q_{y,e}-q_{z,e})^2=-c\le0.                  \tag{3.3}
\]

For a Q3 edge,

\[
 W(x,y)={\lambda\over4}(x-y)^2(x^2+y^2),               \tag{3.4}
\]

\[
 \partial_x\partial_yW
 =-{\lambda\over2}(3x^2-4xy+3y^2)
 =-{\lambda\over4}\big[(x+y)^2+5(x-y)^2\big]\le0.    \tag{3.5}
\]

The scalar quadratic, scalar quartic, harmonic-split and linear-source terms
have no off-diagonal derivative.  Every positive-weight Trotter skeleton is
therefore MTP2.

The unbounded interaction causes no limiting gap.  After absorbing all local
quadratic and linear terms into half of the scalar quartic, uniformly on a
compact source set,

\[
 {\cal V}_h(q)\ge {g\over8}\sum_{y,e}q_{y,e}^4-C_h.     \tag{3.6}
\]

The time-slice weights are bounded above by `exp(beta C_h)`, and their Riemann
sums converge on every continuous loop.  Dominated convergence gives total
variation convergence to the exact Feynman--Kac loop law.  MTP2 is preserved
under marginalization and weak convergence.  Hence every finite evaluation
marginal of the exact loop law is MTP2, and order-preserving polygonal
approximation gives path-space FKG for bounded continuous increasing
functionals.  Polynomial coordinates follow by clipping and the uniform
quartic moments.

At `h=0`, global parity yields `E q_e=0`.  Therefore FKG gives

\[
 \langle q_e q_f\rangle_L\ge0\quad(e\ne f).             \tag{3.7}
\]

The fixed-source law is FKG for every source sign.  Stochastic monotonicity in
a scalar source `h v` additionally requires `v` to be coordinatewise
nonnegative; the collective `u` in (1.1) satisfies that condition.  Nothing is
claimed for mixed-sign source order.

<a id="section-4-collective-double-commutator"></a>
## 4. The global collective double commutator

Put

\[
 \Pi_0=V^{-1/2}\sum_y u\mathbin\cdot p_y,\quad
 S_y=\sum_e q_{y,e}^2,\quad
 D_y=\sum_{\{e,f\}\in E(Q_3)}(q_{y,e}-q_{y,f})^2.       \tag{4.1}
\]

The spatially global momentum is load-bearing.  It shifts every cell by the
same vector, so the spatial difference-square energy is exactly invariant.
On the polynomial Schwartz core,

\[
 [\Pi_0,[H_L(0),\Pi_0]]
 =\hbar^2\left[r+{3g\over8V}\sum_yS_y
                  +{\lambda\over8V}\sum_yD_y\right].   \tag{4.2}
\]

The unbounded operator causes no hidden domain assumption.  With
`U_t=exp(-it Pi_0/hbar)`, the translated Hamiltonians
`H(t)=U_t^*H U_t` are a common-form-domain analytic polynomial family.
Their partition function is constant.  Differentiating `log Z(t)` twice gives

\[
 0=-\beta\langle H''(0)\rangle_L
   +\beta^2\operatorname{Var}_{D,L}(H'(0)),              \tag{4.3}
\]

so `E H''(0)>=0`.  Quartic confinement supplies every moment used here; the
same conclusion follows by spectral cutoff and monotone core removal.
Translation invariance turns (4.2) into

\[
 -r\le {3g\over8}\langle S_0\rangle_L
       +{\lambda\over8}\langle D_0\rangle_L.            \tag{4.4}
\]

Q3 is 3-regular.  Using (3.7),

\[
 \langle D_0\rangle_L
 =3\langle S_0\rangle_L
  -2\sum_{\{e,f\}\in E(Q_3)}\langle q_eq_f\rangle_L
 \le3\langle S_0\rangle_L.                             \tag{4.5}
\]

Also

\[
 \langle Q_0^2\rangle_L
 ={1\over8}\left[\langle S_0\rangle_L
 +2\sum_{e<f}\langle q_eq_f\rangle_L\right]
 \ge {1\over8}\langle S_0\rangle_L.                   \tag{4.6}
\]

Combining (4.4)--(4.6) proves the uniform exact-model lower bound

\[
 \boxed{\langle Q_0^2\rangle_L\ge
 \theta_Q={-r\over3(g+\lambda)}>0.}                     \tag{4.7}
\]

Without FKG, the Q3 spectral bound `D_0<=6S_0` gives only a lower bound on
total amplitude; it cannot exclude a purely transverse covariance with
`Q_0=0`.  That weaker calculation is not used to claim collective order.

<a id="section-5-falk-bruch"></a>
## 5. Falk--Bruch conversion to a local Duhamel bound

For the local collective coordinate,

\[
 [Q_0,[\beta H_L,Q_0]]={\beta\hbar^2\over\chi}.         \tag{5.1}
\]

Let `f(0)=1` and, for `x>0`, define

\[
 f(x\tanh x)={\tanh x\over x}.                          \tag{5.2}
\]

The Falk--Bruch inequality says

\[
 (A,A)_D\ge\langle A^2\rangle
 f\!\left({\langle[A,[\beta H,A]]\rangle
              \over4\langle A^2\rangle}\right).       \tag{5.3}
\]

Spectral truncation makes (5.3) directly applicable to `Q_0`; (4.7), (5.1),
and the monotonicity of `s f(k/s)` give

\[
 d_L:=(Q_0,Q_0)_{D,L}\ge
 \theta_Q f\!\left({\beta\hbar^2\over4\chi\theta_Q}\right).
                                                                    \tag{5.4}
\]

This is still a local moment.  By itself it proves neither a volume-squared
zero mode nor a phase.

<a id="section-6-reflection-positivity"></a>
## 6. Spatial reflection positivity and Gaussian domination

Treat the full cell loop as one spin in
`K=L2(S_beta;R8)`.  Across a spatial reflection plane, a bond factor is

\[
 e^{-{c\over2}\|a-b\|_K^2}
 =e^{-{c\over2}\|a\|_K^2}e^{-{c\over2}\|b\|_K^2}
  e^{c\langle a,b\rangle_K}.                            \tag{6.1}
\]

The last factor is positive definite by its nonnegative symmetric-tensor
series.  Every Q3, kinetic-time and scalar-potential factor remains wholly on
one side of the spatial reflection.  Thus the time-sliced law is spatially
reflection positive for any local even nonradial Q3 weight.  The property
passes to the exact loop law by the same dominated limit as in Section 3.
Internal `O(8)` invariance is not used.

Let `D_i phi(y)=phi(y+e_i)-phi(y)` and let `L_sp=D^*D`.  The standard repeated
reflection argument on dyadic periodic cubes gives the twisted-partition
maximum at zero twist.  Expanding the square yields, for every zero-sum
K-valued spatial source `j`,

\[
 \log\left\langle e^{\sum_y\langle j_y,\omega_y\rangle_K}
 \right\rangle_L
 \le {1\over2c}\langle j,L_{sp}^{-1}j\rangle.           \tag{6.2}
\]

Dyadic cubes are sufficient because EXP-000780 proves a unique pressure limit
along all even cubes.  No unproved arbitrary-box chessboard extension is
needed.

Use the Fourier convention

\[
 \widehat Q_p=V^{-1/2}\sum_y e^{-ip\cdot y}Q_y,qquad
 \widehat D_L(p)=(\widehat Q_p,\widehat Q_{-p})_{D,L}.   \tag{6.3}
\]

Choose in (6.2) a time-constant source `j_y(tau)=t a_y u`.  The second
derivative of the left side is `beta^2(a,D_La)` and that of the right side is
`(beta/c)(a,L_sp^{-1}a)`.  Since the spatial Laplacian eigenvalue is

\[
 \ell(p)=2E(p),\qquad E(p)=\sum_{j=1}^3(1-\cos p_j),    \tag{6.4}
\]

one obtains the exact projected infrared bound

\[
 \boxed{\widehat D_L(p)\le{1\over2\beta cE(p)}}
 \qquad(p\ne0).                                        \tag{6.5}
\]

The factors `2` and `beta` in (6.5) follow from (6.2)--(6.4); no internal
component multiplicity appears because `u` is a unit vector.

<a id="section-7-positive-zero-mode"></a>
## 7. Positive zero-mode density and the explicit threshold

Define

\[
 \Pi_L={1\over V}\widehat D_L(0)
 ={1\over V^2}\left(\sum_yQ_y,\sum_zQ_z\right)_{D,L}.   \tag{7.1}
\]

Fourier inversion, (5.4), and (6.5) give

\[
 \Pi_L\ge
 \theta_Q f\!\left({\beta\hbar^2\over4\chi\theta_Q}\right)
 -{1\over2\beta c}{\cal I}_{3,L},                     \tag{7.2}
\]

\[
 {\cal I}_{3,L}={1\over V}\sum_{p\ne0}{1\over E(p)}
 \longrightarrow {\cal I}_3.                          \tag{7.3}
\]

The singularity in (1.3) is `|p|^-2` and is integrable precisely in three
dimensions.  Along the dyadic sequence,

\[
 \liminf_L\Pi_L\ge\delta_\beta.                        \tag{7.4}
\]

To solve the strict inequality exactly, set
`t=beta hbar^2/(4 chi theta_Q)=x tanh x`.  Then

\[
 2\beta c\theta_Q f(t)=A_0\tanh^2x.                    \tag{7.5}
\]

The right side increases strictly from zero to `A_0`.  Therefore a finite
low-temperature threshold exists exactly for this proof route when
`A_0>I_3`, and solving equality gives (1.5).  If `A_0<=I_3`, or if
`beta<=beta_*`, the infrared sufficient condition is inconclusive.  It does
not prove phase absence.

<a id="section-8-zero-mode-to-cusp"></a>
## 8. Griffiths conversion and the tangent DLR states

Let

\[
 X_L=\sum_y\int_0^\beta Q_y(\tau)\,d\tau.               \tag{8.1}
\]

At zero source,

\[
 {1\over V}\log\mathbb E_0e^{hX_L}
 =8\beta\,[P_{\beta,L}(h)-P_{\beta,L}(0)].             \tag{8.2}
\]

Moreover,

\[
 {\mathbb E_0X_L^2\over(\beta V)^2}=\Pi_L.             \tag{8.3}
\]

EXP-000780 supplies the finite limiting log moment-generating function for
every real `h`; parity makes it even, and EXP-000781 supplies the required
exponential moments.  The Griffiths moment-to-slope lemma applied with scale
`V` gives

\[
 8\beta D_+P_\beta(0)\ge
 \beta\sqrt{\limsup_L\Pi_L}.                            \tag{8.4}
\]

Equations (7.4) and (8.4) prove (1.9).  This step does not use FKG, Jensen,
extremality or clustering; FKG was needed upstream to make the collective
local lower bound positive.

EXP-000781 constructs zero-source tempered DLR tangent states satisfying

\[
 \int Q_0\,d\mu_+=8D_+P_\beta(0),\qquad
 \mu_-=\mu_+\circ(q\mapsto-q).                          \tag{8.5}
\]

Thus (1.10) follows.  The states are distinct and the global `Z2` symmetry is
spontaneously broken.  Since the phase definition used by the cited
quantum-crystal theory is multiplicity of tempered Euclidean DLR measures,
this is a positive-`lambda` DLR phase transition.

<a id="section-9-prior-art-boundary"></a>
## 9. Prior-art and contribution boundary

The ingredients are established mathematics:

- Karlin--Rinott MTP2 closure and correlation inequalities;
- Holley/FKG stochastic comparison;
- spatial reflection positivity and Gaussian domination of
  Froehlich--Simon--Spencer;
- the quantum-crystal infrared normalization, Falk--Bruch inequality, and
  Griffiths pressure lemma summarized by Kargol--Kondratiev--Kozitsky;
- EXP-000780 pressure existence and EXP-000781 exact DLR tangent states.

The exact positive-`lambda` Q3LOCK composition was not supplied by the located
phase theorems.  Their closest vector result assumes an `O(nu)`-radial onsite
potential, while Q3LOCK is nonradial.  Sections 3--4 replace that unavailable
hypothesis with the exact Q3 submodularity, global parity, graph regularity,
and collective-shift calculation.  This is a model-specific theorem, not a
new general phase method.  A bounded audit locating no complete counterpart
is neither a world-first claim nor proof of historical priority.

Primary sources:

- J. Froehlich, B. Simon and T. Spencer, *Infrared bounds, phase transitions
  and continuous symmetry breaking*, Communications in Mathematical Physics
  50 (1976), 79--95, DOI `10.1007/BF01608557`.
- A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase Transitions and Quantum
  Stabilization in Quantum Anharmonic Crystals*, arXiv `0710.2303`, especially
  Proposition 3.9, Lemma 3.12, Corollary 3.14, and Proposition 3.18.
- S. Karlin and Y. Rinott, *Classes of orderings of measures and related
  correlation inequalities. I*, Journal of Multivariate Analysis 10 (1980),
  467--498, DOI `10.1016/0047-259X(80)90065-2`.
- A. Colangelo, A. Mueller and M. Scarsini, *Positive dependence and weak
  convergence*, Journal of Applied Probability 43 (2006), 48--59.

<a id="section-10-proof-boundary"></a>
## 10. Exact proof boundary

Closed here:

- exact finite-time MTP2 and continuous-loop FKG;
- collective positive-source monotonicity;
- global-momentum double-commutator and the sharp FKG-improved
  `theta_Q=-r/[3(g+lambda)]` lower bound;
- local Falk--Bruch conversion;
- nonradial onsite-compatible spatial reflection positivity, Gaussian
  domination and collective infrared bound;
- a nonempty explicit positive-`lambda` low-temperature regime with positive
  volume-squared zero mode;
- strict collective-source cusp and two parity-related tangent DLR states.

Open after this certificate:

- algebraic KMS for a pre-existing infinite-volume real-time dynamics;
- extremality, C-star purity, phase completeness and spatial clustering;
- the zero-temperature ground-state phase and a uniform gap statement;
- interacting continuum/counterterm removal;
- physical empty space, below-empty-space sign and absolute gravitational
  energy;
- a genuine `3D -> 1+1` effective map;
- physical light, gravity, cooling and horizon emergence;
- C0, N1--N5, C6, CP1, Sector A and Pre-A completion.

<a id="section-11-devils-advocate"></a>
## 11. Devil's-advocate audit

1. **Objection: the published vector theorem requires `O(8)` symmetry.**  
   **VALID, mitigated.**  It is not imported.  The fixed-direction RP proof is
   reproduced, while MTP2 and Q3 regularity supply the collective moment.

2. **Objection: a pure kinetic periodic Gaussian has a zero mode.**  
   **VALID, mitigated.**  Section 3 uses `a>0` OU splitting and absorbs the
   compensating scalar quadratic locally.

3. **Objection: Q3 is quartic and might destroy FKG.**  
   **DISMISSED.**  The exact sum-of-squares identity (3.5) has the attractive
   mixed sign for every field value.

4. **Objection: the momentum double commutator is unbounded.**  
   **VALID, mitigated.**  The common-form-domain unitary translation argument
   (4.3), corroborated by spectral cutoffs and quartic moments, controls it.

5. **Objection: a total-amplitude lower bound could be transverse.**  
   **UPHELD against the no-FKG shortcut.**  Equations (4.5)--(4.7) use FKG;
   the graph-spectrum-only bound is explicitly non-load-bearing.

6. **Objection: local Duhamel positivity is not long-range order.**  
   **UPHELD.**  Only the nonzero-mode infrared sum in Section 7 produces the
   volume-squared zero-mode density.

7. **Objection: a zero mode need not imply a pressure cusp.**  
   **VALID generally, dismissed under the recorded hypotheses.**  The exact
   scalar moment-generating identity (8.2), all-source pressure limit, parity,
   and Griffiths lemma give the quantitative slope bound (8.4).

8. **Objection: finite-volume response is zero at `h=0`.**  
   **DISMISSED as a phase test.**  The thermodynamic limit precedes the
   one-sided source limit; this is exactly the EXP-000779 firewall.

9. **Objection: `A_0<=I_3` proves no phase.**  
   **UPHELD.**  It says only that this sufficient infrared route does not
   cross its threshold.

10. **Objection: DLR multiplicity is already a full physical vacuum or KMS
    theorem.**  
    **UPHELD.**  All such promotions remain explicitly open in Section 10.

<a id="section-12-reproduction"></a>
## 12. Reproduction

Run from the repository root with the repository virtual environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_verify.py
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/regen_all.py
E:\Dev\TECT.venv\Scripts\python.exe verification/scripts/release_check.py
```

The executable audits check algebra, graph constants, Fourier and source
normalizations, Watson sums, threshold equivalence, hostile mutations, scope,
and repository synchronization.  They are regression witnesses, not
substitutes for the analytic arguments in Sections 3--8.
