# R-167 v1.9 certificate: local history tails and the Q3 onsite doublet

- **Exploration:** `EXP-000806`
- **Result:** `R-167`, additive version `v1.9`; no new result number
- **Stable result ID:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

R-167 v1.9 corrects the next target left by v1.8.  A global,
volume-independent sandwiched-Renyi constant for every all-bond split layer is
not the right target: it is already extensive in the conditional doublet
product reference.  The exact surviving condition lives only on the local
coordinate marginal.  Pure bond layers themselves preserve every coordinate
tail exactly, so all remaining tail loss comes from onsite-interspersed
histories.

Independently, this certificate verifies all hypotheses needed to import the
standard multidimensional two-well semiclassical theorem for the isolated Q3
onsite oscillator.  It then compresses the full spatial Hamiltonian exactly
to its low doublet and identifies the missing infinite-dimensional rank-two
block theorem.  The exact common dynamics and broken-sector GNS gap remain
open.

The closed narrow subgates are exactly:

1. `PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-STATE-WEIGHTED-CUTOFF-IDENTITY`;
2. `PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION`;
3. `PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-LOW-BAND-TFIM-COMPRESSION`.

The parent gates remain open:

- `PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`;
- `PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`;
- `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`.

## 1. Pure all-bond layers preserve coordinate tails exactly

Write the cross-bond multiplication operator as

\[
 V_\times=-c\sum_{\langle xy\rangle}q_x\mathbin\cdot q_y,
 \qquad B_\delta=\exp(-i\delta V_\times/\hbar).       \tag{1.1}
\]

Every bounded coordinate multiplier `F(q_S)` commutes with `B_delta`.
Consequently

\[
 B_\delta^*F(q_S)B_\delta=F(q_S)                     \tag{1.2}
\]

in both history orientations.  This applies to the bounded projection

\[
 E_{S,L}=1_{\{X_S>L\}},\qquad X_S=\max_{x\in S}|q_x|, \tag{1.3}
\]

and, by strong commutation of affiliated multiplication operators, to
`X_S^4 E_(S,L)` and every square of a coordinate cutoff tail on their natural
finite-moment forms.

Let `V_(times,L)` be any coordinate cutoff, put

\[
 W_L=V_\times-V_{\times,L},\qquad
 B_{\delta,L}=\exp(-i\delta V_{\times,L}/\hbar).      \tag{1.4}
\]

The three multiplication operators commute.  For every finite-volume type-I
normal state `sigma` with `sigma(W_L^2)<infinity`, functional calculus gives
the two exact Hilbert--Schmidt identities

\[
 \begin{split}
 \|(B_\delta-B_{\delta,L})\sigma^{1/2}\|_2^2
 &=\|\sigma^{1/2}(B_\delta-B_{\delta,L})\|_2^2\\
 &=\sigma\!\left(4\sin^2{\delta W_L\over2\hbar}\right)\\
 &\le {\delta^2\over\hbar^2}\sigma(W_L^2).
 \end{split}                                          \tag{1.5}
\]

Thus an all-bond state-weighted telescope need not pay the bounded-cutoff
operator-norm factor `exp(C L^2)`.  The missing estimate is instead the
two-orientation `W_L^2` tail in each actual intermediate state after onsite
and bond layers have been interspersed.  Equation (1.5) does not estimate that
state.

## 2. The global volume-uniform Renyi target is overstrong

Use the conditional low-doublet product reference

\[
 \rho_1=\begin{pmatrix}4/5&0\\0&1/5\end{pmatrix},
 \qquad \rho_2=\rho_1\otimes\rho_1,                   \tag{2.1}
\]

and let the doublet coordinate be `m sigma_x`.  One bond layer is

\[
 U_\theta=\exp(i\theta\,\sigma_x\otimes\sigma_x),
 \qquad \theta={8\delta c m^2\over\hbar}
 ={\delta J\over\hbar}.                              \tag{2.2}
\]

Here (2.2) is the complete eight-component spatial bond.  The angle
`delta c m^2/hbar` would describe only one internal-coordinate channel.

For order two, direct matrix multiplication gives

\[
 \widetilde Q_2(U_\theta\rho_2U_\theta^*\Vert\rho_2)
 =\left(1+{9\over4}\sin^2\theta\right)^2
 ={(4+9\sin^2\theta)^2\over16}.                      \tag{2.3}
\]

At `theta=pi/4`,

\[
 \widetilde Q_2={289\over64}>1.                       \tag{2.4}
\]

On `M` disjoint bonds the state and the unitary tensorize, so the quantity in
(2.3) is raised to the `M`-th power.  For `M=3` the exact value is

\[
 {24137569\over262144}.                               \tag{2.5}
\]

It therefore grows exponentially with volume for every fixed angle
`theta` not in `pi Z`.  At the same time every spectral function of the *compressed*
coordinate `m sigma_x` commutes with the kick, so its probability is
unchanged.  This is not an identity for `P 1_(q>L) P` in the full oscillator.
Global quantum divergence can be extensive while the fixture's local
coordinate-algebra event pays zero bond-layer loss.

This fixture rejects only one volume-independent *global* sandwiched-Renyi
bound for all-bond histories in the conditional product reference.  It is not
a full-Q3 Gibbs counterexample and does not reject a local measured-Renyi or
restricted-tail theorem.

## 3. Exact local coordinate-marginal replacement

Fix finite `S`, `alpha>1`, and

\[
 \vartheta={\alpha-1\over\alpha}.                     \tag{3.1}
\]

Let `nu_(0,S)` be the reference law of `X_S`, and let
`nu_(P,S)^+` and `nu_(P,S)^-` be its laws after a partial history and its
adjoint.  The minimal direct target is

\[
 \sup_{u\ge L_0}
 {\nu_{P,S}^{\pm}(X_S>u)\over
  \nu_{0,S}(X_S>u)^\vartheta}
 \le C_{\alpha,T,S},                                  \tag{3.2}
\]

uniformly in the ambient volume, source, mesh, partial history and
orientation.  A stronger checkable condition uses only the commutative
coordinate algebra:

\[
 \int\left({d\nu_{P,S}^{\pm}\over d\nu_{0,S}}\right)^\alpha
 d\nu_{0,S}\le Q_{\alpha,T,S}.                        \tag{3.3}
\]

This measured/classical Renyi condition is strictly weaker than global
quantum sandwiched Renyi.  If the registered static bound is

\[
 \nu_{0,S}(X_S>u)\le M_a|S|e^{-au^2},                 \tag{3.4}
\]

Holder gives

\[
 \nu_{P,S}^+(X_S>L)+\nu_{P,S}^-(X_S>L)
 \le 2Q_{\alpha,T,S}^{1/\alpha}(M_a|S|)^\vartheta
 e^{-\vartheta aL^2}.                                 \tag{3.5}
\]

Putting `b=vartheta a` and integrating the fourth-moment layer cake gives

\[
 2Q_{\alpha,T,S}^{1/\alpha}(M_a|S|)^\vartheta e^{-bL^2}
 \left(L^4+{2L^2\over b}+{2\over b^2}\right).        \tag{3.6}
\]

This is exactly the fixed-`S` weighted coordinate-tail implication.  To feed a
growing corridor one must additionally control `Q_{\alpha,T,S}` uniformly over
translates of the relevant fixed bond shapes, or prove an explicit growth
envelope for `Q_{\alpha,T,S_R}` that remains absorbable as `R` and `L` grow.
The theorem stops at the fixed-`S` reduction: no such uniform Q3LOCK bound,
growth envelope, or onsite-interspersed history estimate has been proved.

## 4. Exact semiclassical normalization of the Q3 onsite oscillator

Put

\[
 R=-r>0,\quad \mu={\lambda\over g}>0,\quad
 v=\sqrt{R/g},\quad E_*=R^2/g,
 \quad h={\hbar g\over\sqrt\chi R^{3/2}}.             \tag{4.1}
\]

After `q=vx` and the standard additive shift, the one-site operator is

\[
 h_{\rm site}=E_*K_h,
 \qquad K_h=-{h^2\over2}\Delta+W_\mu,                \tag{4.2}
\]

where

\[
 W_\mu(x)={1\over4}\sum_{e=1}^8(x_e^2-1)^2
 +{\mu\over4}\sum_{\{e,f\}\in E(Q_3)}
 (x_e-x_f)^2(x_e^2+x_f^2).                            \tag{4.3}
\]

The second term is nonnegative.  Its zero set on the first term's minima
forces all eight signs to agree because `Q_3` is connected.  Hence for
`mu>0` the only global minima are `+1` and `-1`.  Expanding at either minimum
gives

\[
 \operatorname{Hess}W_\mu=2I+\mu L_{Q_3}.             \tag{4.4}
\]

The cube Laplacian spectrum is `0`, `2` with multiplicity three, `4` with
multiplicity three, and `6`.  Thus the Hessian spectrum is

\[
 2,\quad (2+2\mu)^{\times3},\quad
 (2+4\mu)^{\times3},\quad 2+6\mu.                    \tag{4.5}
\]

Both wells are nondegenerate.  The exact R-167 v1.8 action minimization gives
the Agmon distance

\[
 S_0={16\sqrt{2}\over3}.                              \tag{4.6}
\]

The locked path realizes it, and `mu>0` removes the independent relative
kink-center zero modes.

## 5. Imported small-h onsite doublet theorem

The polynomial `W_mu` is smooth and coercive and has exactly two
nondegenerate symmetry-related wells at finite Agmon distance.  These are the
load-bearing hypotheses of the standard multidimensional multiple-well
semiclassical results; uniqueness of the minimizing path is not required for
the logarithmic splitting exponent:

- B. Simon, *Semiclassical analysis of low lying eigenvalues I.
  Non-degenerate minima: asymptotic expansions*, Ann. IHP 38 (1983),
  295--308, <https://www.numdam.org/item/AIHPA_1983__38_3_295_0/>.
  Theorem 1.1 (pp. 298--299) identifies the ordered harmonic-well spectrum;
  Theorem 4.1 (pp. 302--304) gives eigenvalue and eigenvector expansions for
  a simple harmonic level; Theorem 5.1, Theorem 5.3 and Corollary 5.4
  (pp. 304--306) treat degenerate well clusters, eigenvectors and
  symmetry-protected doublets;
- B. Simon, erratum to the preceding paper, Ann. IHP 40 (1984), p. 224,
  <https://www.numdam.org/item/AIHPA_1984__40_2_224_0/>.  The erratum adds
  the same-parity condition for same-well degeneracies in Theorem 5.1.  The
  Q3 local ground and lowest uniform-mode excitation are individually simple;
  their relevant degeneracy is only the copy across the two wells, so the
  corrected condition is satisfied;
- B. Helffer and J. Sjostrand, *Multiple wells in the semi-classical limit I*,
  Comm. PDE 9 (1984), 337--408,
  <https://doi.org/10.1080/03605308408820335>;
- B. Simon, *Semiclassical analysis of low lying eigenvalues II. Tunnelling*,
  Ann. Math. 120 (1984), 89--118,
  <https://annals.math.princeton.edu/1984/120-1/p04>.  Its Theorem 1.5 for a
  symmetric two-well problem identifies the logarithmic splitting exponent
  with the Agmon distance;
- B. Helffer and J. Sjostrand, *Puits multiples ... II. Symmetries*,
  Ann. IHP 42 (1985), 127--212,
  <https://www.numdam.org/item/AIHPA_1985__42_2_127_0/>.

For every fixed `mu>0` there is a non-explicit `h_0(mu)>0` such that for
`0<h<h_0(mu)` the first two eigenvalues are simple.  Their eigenvectors
`phi_0,phi_1` are respectively even and odd under global sign reversal and
are both `Aut(Q_3)` singlets.  Moreover

\[
 \lim_{h\downarrow0}h\log{\epsilon_1-\epsilon_0\over E_*}=-S_0,             \tag{5.1}
\]

and, for every `eta>0`,

\[
 \delta_1:=\epsilon_1-\epsilon_0
 \le E_*C_{\mu,\eta}e^{-(S_0-\eta)/h}.                \tag{5.2}
\]

If `Gamma=epsilon_2-epsilon_0`, the one-well harmonic approximation and (4.5)
give

\[
 {\Gamma\over E_*}=\sqrt{2}\,h+O(h^{3/2}),           \tag{5.3}
\]

so, after decreasing `h_0`, `Gamma>=E_*h/sqrt(2)`.  The well ground energy is

\[
 {\epsilon_0\over E_*}=h e_{\rm well}+O(h^{3/2}),
\quad e_{\rm well}={1\over2}
 [\sqrt{2}+3\sqrt{2+2\mu}+3\sqrt{2+4\mu}+\sqrt{2+6\mu}].                 \tag{5.4}
\]

After fixing the phase of `phi_1`, cube symmetry and localization give, for
every coordinate `e`,

\[
 \begin{split}
 m&=\langle\phi_0,q_e\phi_1\rangle=v[1+O(h)],\\
 a_j&=\langle\phi_j,q_e^2\phi_j\rangle=v^2[1+O(h)],\\
 b_j&=\langle\phi_j,q_e^4\phi_j\rangle=v^4[1+O(h)],\\
 a_1-a_0&=O(v^2h).
 \end{split}                                          \tag{5.5}
\]

The last line is the safe localization estimate needed below.  The cited
general multiple-well results do not, without an additional weighted
Agmon-overlap lemma, license an exponential rate for this even-observable
difference.  All constants in this section are existential.  In particular
this theorem does not certify that the repository's finite `R=9` diagnostic
lies below the unknown `h_0(mu)`.

For clarity, the symmetry and moment statements used here are the following
direct corollary of those cited spectral-projection expansions.  Positivity
improving of the confining Schrodinger semigroup makes the ground state
simple and positive, hence parity even and `Aut(Q_3)` invariant.  The
two-dimensional lowest cluster is generated, up to errors smaller than every
power before tunnelling is resolved, by the two local-well ground quasimodes.
Parity exchanges those modes, while every cube automorphism fixes each well
and its simple harmonic ground mode.  Once the tunnelling splitting is
nonzero, the second vector is therefore parity odd and remains in the trivial
`Aut(Q_3)` representation.  Simon I, Theorems 4.1 and 5.1 together with
Lemma 4.2 and the cited erratum, give through their weighted
polynomial-times-Gaussian eigenvector expansions, after
`x=plus/minus 1+sqrt(h)y` the displayed `m`, `a_j` and `b_j` estimates and the
safe `a_1-a_0=O(v^2h)` consequence.  This paragraph is a derived
harmonic-localization/symmetry lemma, not a numerical estimate of `h_0`.

## 6. Exact low-band transverse-field Ising compression

Let

\[
 P=|\phi_0\rangle\langle\phi_0|+|\phi_1\rangle\langle\phi_1|,
 \quad P_1=|\phi_1\rangle\langle\phi_1|,
 \quad s=|\phi_0\rangle\langle\phi_1|+\text{h.c.}     \tag{6.1}
\]

with `s=0` on `P^perp`.  Parity and cube symmetry imply

\[
 Pq_eP=ms,\qquad Pq_e^2P=\operatorname{diag}(a_0,a_1).                     \tag{6.2}
\]

For

\[
 B_{xy}={c\over2}\sum_{e=1}^8(q_{xe}-q_{ye})^2,       \tag{6.3}
\]

the exact compression to `P_Lambda=P^(tensor Lambda)`, after one scalar
shift, is

\[
 P_\Lambda H P_\Lambda
 =J\sum_{\langle xy\rangle}(1-s_xs_y)
 +\sum_x[\delta_1+4c\deg(x)(a_1-a_0)]P_{1,x},
 \qquad J=8cm^2.                                     \tag{6.4}
\]

On a periodic cubic lattice `deg(x)=z=6`, this becomes

\[
 \delta_{\rm eff}=\delta_1+4zc(a_1-a_0)
 =\delta_1+24c(a_1-a_0).                              \tag{6.5}
\]

For an open finite box the field in (6.4) is site-dependent at the boundary;
the uniform coefficient `24c` is not asserted there.

Thus the entire low--low part of the old `R_e^2` remainder is an exact
renormalization of the transverse field.  It is not an uncontrolled low-band
interaction.

## 7. Exact low/high residual inputs

Let `Q=1-P` and define

\[
 a^2=\max_j(a_j-m^2)=\|Qq_eP\|^2,\qquad
 b^2=\max_j(b_j-a_j^2)=\|Qq_e^2P\|^2.                 \tag{7.1}
\]

Expanding (6.3) and separating low and high factors gives the one-bond bound

\[
 \|(1-P_xP_y)B_{xy}P_xP_y\|
 \le 8c\,[b+2ma+a^2].                                 \tag{7.2}
\]

Put

\[
 k=h_{\rm site}-\epsilon_0-\delta_1P_1\ge\Gamma Q,
 \qquad {\cal R}_e=q_e-ms.                            \tag{7.3}
\]

For every `t>0`,

\[
 \|{\cal R}_e\psi\|^2
 \le(1+t)a^2\|P\psi\|^2
 +(1+t^{-1})A_Q\langle Q\psi,kQ\psi\rangle,          \tag{7.4}
\]

where

\[
 A_Q={v^2\over\Gamma}
 +{2\sqrt{\epsilon_0+\Gamma}\over\Gamma\sqrt g}.    \tag{7.5}
\]

Indeed, nonnegativity of the other potential terms gives, for every
`epsilon>0`,

\[
 q_e^2\le v^2+{4\epsilon\over g}h_{\rm site}
 +{1\over4\epsilon}.                                  \tag{7.6}
\]

Restricting to `Q`, using `k>=Gamma Q`, and optimizing `epsilon` yields (7.5).
Equations (7.1)--(7.5) reduce the missing high-mode estimates to certified
enclosures of `epsilon_0,delta_1,Gamma,m,a_0,a_1,b_0,b_1`.

## 8. A nonempty asymptotic model corridor

Take

\[
 g=\lambda=\chi=\hbar=1,\qquad r=-N^4,\qquad c=N^{-4}.                     \tag{8.1}
\]

Then

\[
 v=N^2,\quad E_*=N^8,\quad h=N^{-6},\quad J\longrightarrow8,
 \quad \Gamma\sim\sqrt{2}N^2.                        \tag{8.2}
\]

The semiclassical moment estimates imply

\[
 a=O(N^{-1}),\qquad b=O(N),\qquad
 \|(1-P_xP_y)B_{xy}P_xP_y\|=O(N^{-3}),
 \qquad cA_Q=O(N^{-2}),\qquad
 cm\sqrt{A_Q}=O(N^{-1}).                              \tag{8.3}
\]

Moreover

\[
 \delta_{\rm eff}=O(N^{-6})
 +O\!\left(N^8e^{-(S_0-\eta)N^6}\right),\qquad
 A_0\sim {2\over9}N^4.                                \tag{8.4}
\]

Thus the effective transverse field and low/high ratios vanish, the Ising
Peierls scale remains order one, and the registered infrared lower condition
is satisfied ever more strongly.  This is an asymptotic family, not a
finite-`N` enclosure and not a QPS theorem.

## 9. Why the published unbounded block theorem does not yet finish the gap

Del Vecchio, Frohlich and Pizzo prove a volume-uniform Lie--Schwinger theorem
for short-range unbounded form-bounded interactions in arbitrary dimension:

- S. Del Vecchio, J. Frohlich and A. Pizzo,
  *Block-diagonalization of infinite-volume lattice Hamiltonians with
  unbounded interactions*, JFA 284 (2023) 109734,
  <https://arxiv.org/pdf/2108.13907>.

Its stated theorem assumes one onsite vector `Omega` and
`H|_(C Omega)^perp>=1`; the local reference projections are tensor products
of rank-one vacuum projections, and the conclusion is a unique ground state
with a uniform gap.  The introduction says that a degenerate extension should
work under an earlier structural assumption, but it does not state or prove a
rank-two onsite-band theorem whose global low space has dimension
`2^|Lambda|`.

Choosing only `phi_0` as the rank-one reference does not repair the mismatch:
its onsite gap is `delta_1`, exponentially smaller than the order-one Ising
scale in (8.2), so the published small-coupling hypothesis lies in the wrong
corridor.

The exact successor is therefore a volume-uniform rank-two band
Lie--Schwinger/Feshbach theorem that subtracts (6.4), block diagonalizes low
and high modes in weighted relative-form norms, and leaves an effective
finite-dimensional interaction small in a two-phase QPS norm.  An equivalent
uniform spectral-cutoff removal theorem would also suffice.  Neither result
is currently registered.

This is a direct-import mismatch, not a no-go for that successor and not a
counterexample to the exact Q3LOCK broken-sector gap.

## 10. Gate verdict

The dynamics parent is

`PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`.

Its honest status is:

> OPEN, WITH FIXED-TROTTER COMPATIBILITY, PURE-BOND COORDINATE-TAIL
> INVARIANCE, AND LOCAL-MEASURED-RENYI SUFFICIENCY ISOLATED. THE
> VOLUME-UNIFORM GLOBAL-RENYI TARGET IS OVERSTRONG IN THE CONDITIONAL
> LOW-DOUBLET PRODUCT REFERENCE. ONSITE-INTERSPERSED LOCAL HISTORY TAILS,
> `n -> infinity`, ALL-SHAPE CAUCHY, GROUP/GENERATOR COMPLETION, AND
> PHASE-KMS QUOTIENT IDENTIFICATION REMAIN OPEN.

The spectral parent is

`PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`.

Its honest status is:

> OPEN, WITH THE SMALL-`h` ONSITE DOUBLET, EXACT LOW-BAND TFIM
> COMPRESSION, AND CENTERED RESIDUAL FORM INPUTS REDUCED. A VOLUME-UNIFORM
> RANK-TWO UNBOUNDED BAND BLOCK DIAGONALIZATION OR UNIFORM CUTOFF REMOVAL,
> A TWO-PHASE QPS TRANSFER, BETA-INFINITY PHASE IDENTIFICATION, AND THE
> ACTUAL PHASEWISE TEMPORAL MASS/GNS GAP REMAIN OPEN.

No statement here closes C6, CP1, physical Sector A, or Pre-A.
