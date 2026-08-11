# R-167 v2.0 certificate: Gibbs resummation, corridor reduction, and compressed phases

- **Exploration:** `EXP-000809` (additive successor to `EXP-000806`)
- **Result:** `R-167`, additive version `v2.0`; no new result number
- **Stable result ID:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

R-167 v2.0 preserves the complete v1.9 certificate below and adds the finite-Gibbs, fixed-edge corridor, global Feshbach, and compressed-phase layers in Sections 11--19. No v2.0 PDF is issued at this proof-first stage.

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

The v1.9 closed narrow subgates retained here are exactly:

1. `PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-STATE-WEIGHTED-CUTOFF-IDENTITY`;
2. `PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION`;
3. `PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-LOW-BAND-TFIM-COMPRESSION`.

The parent gates remain open:

- `PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`;
- `PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`;
- `PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS`;
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

## 11. v2.0 additive checkpoint and formal staging boundary

Sections 1--10 above are retained verbatim as the v1.9 foundation.  R-167
v2.0 adds four narrow theorem-ready children and three scoped negatives under
`EXP-000809`.  At this proof-first stage their formal ledger, gate and negative
rows are intentionally absent; both verifiers must therefore report
`INCOMPLETE` under `--staged` until the parent checkpoint writes those
authorities.  No v2.0 PDF is issued here.

The four proposed closed children are:

1. `PA-CP1-ST8-Q3LOCK-FULL-HAMILTONIAN-TWO-ORIENTATION-STATIC-GIBBS-CUTOFF-UNITARY-RESUMMATION`;
2. `PA-CP1-ST8-Q3LOCK-FIXED-BOND-RESTRICTED-TAIL-TO-GROWING-CORRIDOR-REDUCTION`;
3. `PA-CP1-ST8-Q3LOCK-BELOW-ONE-HIGH-MODE-FESHBACH-AND-RELATIVE-FORM-SMALLNESS-PRECURSOR`;
4. `PA-CP1-ST8-Q3LOCK-EXACT-COMPRESSED-TFIM-TWO-PHASE-QPS-AND-PHASEWISE-GAP`.

Every parent gate listed in Section 10 remains open.

## 12. Full-Hamiltonian finite-Gibbs cutoff resummation

Let `H` and `H_L=H-W_L` be self-adjoint, bounded-below finite-volume
Hamiltonians on a common form domain, and put

\[
 \rho=Z^{-1}e^{-\beta H},\quad
 U(t)=e^{-itH/\hbar},\quad U_L(t)=e^{-itH_L/\hbar}.       \tag{12.1}
\]

Assume the two Duhamel formulas hold as strong limits on a common invariant
form core and that `W_L rho^(1/2)` and `rho^(1/2) W_L` are Hilbert--Schmidt.
For self-adjoint `W_L` this is the single static moment condition
`rho(W_L^2)<infinity`.

For the registered finite-volume Q3 hard/form-cutoff pair these hypotheses
have a direct form-domain realization.  The full and cutoff Hamiltonians are
closed form sums on the common quartic form domain, while `W_L` is a real
quadratic coordinate multiplier, possibly restricted to a hard coordinate
tail.  Thus `W_L^2` has quartic growth and the existing finite-volume Gibbs
coordinate moments put `W_L rho^(1/2)` in `S_2`.  Truncate `W_L` spectrally
or formwise to bounded `W_(L,M)`, apply bounded Duhamel, and pass first in
strong-resolvent/unitary sense and then in `S_2` using
`W_(L,M)rho^(1/2) -> W_Lrho^(1/2)`.  This discharges the displayed
finite-volume hard/form-pair hypotheses.  A differently defined smooth
clipped-coordinate cutoff still requires its own common-domain and form-
convergence check.

The first Duhamel ordering gives

\[
 U(t)-U_L(t)=-{i\over\hbar}\int_0^t
 U_L(t-s)W_LU(s)\,ds.                                \tag{12.2}
\]

Multiplication on the right by `rho^(1/2)`, commutation of `rho` with the
*full* `U(s)`, and left/right unitary invariance of the Hilbert--Schmidt norm
give

\[
 \|(U(t)-U_L(t))\rho^{1/2}\|_2
 \le {|t|\over\hbar}\rho(W_L^2)^{1/2}.                \tag{12.3}
\]

The opposite ordering,

\[
 U(t)-U_L(t)=-{i\over\hbar}\int_0^t
 U(t-s)W_LU_L(s)\,ds,                                \tag{12.4}
\]

puts the commuting full flow next to `rho^(1/2)` on the left and yields

\[
 \|\rho^{1/2}(U(t)-U_L(t))\|_2
 \le {|t|\over\hbar}\rho(W_L^2)^{1/2}.                \tag{12.5}
\]

No commutation of `rho` with `U_L` is used.  Factoring the difference of the
two evolved density matrices into two Hilbert--Schmidt products gives

\[
 \|\rho-U_L(t)\rho U_L(t)^*\|_1
 \le {2|t|\over\hbar}\rho(W_L^2)^{1/2}.               \tag{12.6}
\]

This is a full-Hamiltonian resummation: no intermediate split-history tail
appears.  It is finite-volume and state-weighted, and by itself says nothing
about an observable placed between the unitary difference and the Gibbs
vector.

### 12.1 Bounded half-modular and fixed-Bohr-band contexts

For `alpha_t(A)=U(t)^* A U(t)`, suppose

\[
 A\rho^{1/2}=\rho^{1/2}C_A,\qquad
 C_A=\alpha_{-i\beta\hbar/2}(A)                     \tag{12.7}
\]

extends boundedly.  Apply the same condition separately to `A^*`; this is the
needed context for the left state seminorm.  A two-term telescoping of the
automorphisms and (12.3)--(12.5), also at `-t`, gives

\[
 \begin{split}
 \|[\alpha_t(A)-\alpha_t^{(L)}(A)]\rho^{1/2}\|_2
 &\le (\|A\|+\|C_A\|)\varepsilon_L(t),\\
 \|\rho^{1/2}[\alpha_t(A)-\alpha_t^{(L)}(A)]\|_2
 &\le (\|A\|+\|C_{A^*}\|)\varepsilon_L(t),
 \end{split}                                         \tag{12.8}
\]

where `epsilon_L(t)=|t|rho(W_L^2)^(1/2)/hbar`.

A narrow sufficient class is a finite Bohr-frequency decomposition
`A=sum_omega A_omega`, `[H,A_omega]=omega A_omega`, with
`|omega|<=Omega` and finite projective norm `sum_omega||A_omega||`.  Then

\[
 \|C_A\|,\|C_{A^*}\|
 \le e^{\beta\Omega/2}\sum_\omega\|A_\omega\|.       \tag{12.9}
\]

Equation (12.9) is not claimed for an arbitrary matrix-band condition with
no dimension-independent Schur/projective norm.

## 13. Exact arbitrary-context obstruction

The first new negative is

`NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE`.

For `0<p<1/2`, take

\[
 \rho_p=\operatorname{diag}(1-p,p),\quad
 H={\pi\hbar\over t_0}|1\rangle\langle1|,\quad H_L=0,
 \quad
 \beta={t_0\over\pi\hbar}\log{1-p\over p}.           \tag{13.1}
\]

Thus `rho_p` is exactly the Gibbs state of `H`.  At `t=t_0`, both squared
weighted unitary errors are

\[
 \|(U-U_L)\rho_p^{1/2}\|_2^2
 =\|\rho_p^{1/2}(U-U_L)\|_2^2=4p,                    \tag{13.2}
\]

whereas

\[
 \rho_p(W^2)={\pi^2\hbar^2\over t_0^2}p.             \tag{13.3}
\]

For `A=sigma_x`, `alpha_(t0)(A)-alpha_(t0)^(L)(A)=-2A`.
Both one-sided state-weighted observable-error norms are exactly `2`, hence

\[
 \|\Delta\alpha(A)\rho_p^{1/2}\|_2^2
 +\|\rho_p^{1/2}\Delta\alpha(A)\|_2^2=8.             \tag{13.4}
\]

Both evolved density matrices nevertheless equal `rho_p`, so their trace
distance is exactly zero.  The missing half-modular norm is
`sqrt((1-p)/p)`, which diverges as `p` decreases.  Therefore weighted-unitary
and trace-state stability do not automatically pass an arbitrary bounded
context.  This does not obstruct the class in Section 12.1 or prove Q3LOCK
dynamics nonexistent.

## 14. Uniform fixed-bond tail implies one growing corridor

Let `C_R=[-R,R]^3` and let `E_R` be its induced nearest-neighbour edges.  Then

\[
 m_R:=|E_R|=6R(2R+1)^2\le54R^3.                       \tag{14.1}
\]

Write `W_(R,L)=sum_(e in E_R)w_(e,L)`.  Quadratic-form Cauchy gives

\[
 W_{R,L}^2\le m_R\sum_{e\in E_R}w_{e,L}^2.           \tag{14.2}
\]

For `w_(e,L)=-c(q_x dot q_y)1_(X_e>L)`,
`w_(e,L)^2<=c^2 X_e^4 1_(X_e>L)`.  Hence a uniform
two-orientation fixed-edge bound

\[
 \sup_{e\in E_R}\{\sigma_+(w_{e,L}^2)+
 \sigma_-(w_{e,L}^2)\}\le c^2K_{\rm edge}(L)          \tag{14.3}
\]

implies

\[
 \sigma_+(W_{R,L}^2)+\sigma_-(W_{R,L}^2)
 \le m_R^2c^2K_{\rm edge}(L).                        \tag{14.4}
\]

For the exact illustrative constants `alpha=2`, `theta=1/2`, `a=2`, `b=1`,
`Q=4`, `M_a=1/2` and `|S_e|=2`, the v1.9 formula is

\[
 K_{\rm edge}(L)=4e^{-L^2}(L^4+2L^2+2).              \tag{14.5}
\]

These are hard-tail constants for
`w_(e,L)=-c(q_x dot q_y)1_(X_e>L)`.  They are not the constants of a smooth
clipped-coordinate `Q_L` Hamiltonian; that transfer would need a separate
pointwise-domination and form-convergence audit.

Choosing `L_R=sqrt(R)` and, only for the displayed constant, `c=1/3`, the
right side is bounded by

\[
 1296R^6e^{-R}(R^2+2R+2)\longrightarrow0.             \tag{14.6}
\]

The limit needs no asymptotic guess: `e^R>=R^10/10!` yields a rational
majorant proportional to `R^-2+2R^-3+2R^-4`.

On a periodic cubic torus, translations have three positive-edge orbits,
one for each coordinate direction.  Translation covariance therefore
reduces (14.3) to three canonical orientations, not one.  Cubic rotations
are additionally needed to identify those three.  Open boundaries,
nonuniform sources, local insertions, or ordered partial histories may break
even translation covariance.  The child theorem closes only the deterministic
reduction (14.2)--(14.6); the Q3LOCK fixed-edge history input (14.3) remains
open.

## 15. Homogeneous Gaussian tilted-edge implication no-go

The second new implication negative is

`NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL`.

Relative to the standard Gaussian on one edge, define

\[
 {d\nu_\kappa\over d\nu_0}(x,y)
 =\sqrt{1-\kappa^2}\,e^{\kappa xy},\qquad \kappa={3\over4}.              \tag{15.1}
\]

The tilted precision determinant is `1-kappa^2=7/16>0`; all polynomial
moments are finite, and endpoint exchange and simultaneous sign reversal are
exact symmetries.  Its one-coordinate variance is `16/7`, so its Gaussian
tail exponent is `7/32`.  For `alpha=2`, the reference-power exponent is
`theta/2=1/4`, leaving the positive exponent difference `1/32`.  Thus no
finite constant can satisfy the fixed-edge Holder tail ratio for all large
cutoffs.  Equivalently, the order-two likelihood integral diverges because
the squared-tilt precision determinant is

\[
 1-4\kappa^2=-{5\over4}<0.                            \tag{15.2}
\]

Regard the two endpoints as a two-site periodic cell, or repeat the same tilt
on a homogeneous dimer family.  This is endpoint/two-site or dimer
homogeneity, not full one-site translation invariance on the cubic lattice.
The fixture shows only that Gaussian static tails, the stated symmetry and
all finite moments do not imply (14.3).  It is not a Q3 history, locality or
dynamics nonexistence theorem.

## 16. Below-Gamma global Feshbach precursor and exact 11 overlap

Let

\[
 P_\Lambda=P^{\otimes\Lambda},\quad Q_\Lambda=1-P_\Lambda,
 \quad K_\Lambda=\sum_xk_x\ge\Gamma\sum_xQ_x.         \tag{16.1}
\]

Keep the absolute finite-volume Hamiltonian normalization in which the onsite
ground scalar has been removed but no extensive scalar from rewriting the
low-band TFIM has been subtracted.  The onsite splitting and every Q3 spatial
square bond are then nonnegative.  Therefore

\[
 Q_\Lambda H Q_\Lambda\ge\Gamma Q_\Lambda.           \tag{16.2}
\]

If one later subtracts a volume-dependent low-band scalar, the absolute
threshold in (16.2) shifts with it.  Accordingly `E<Gamma` below is
finite-volume absolute-energy algebra, not thermodynamic isolation of a
ground band.

For every real `E<Gamma`, the exact Feshbach operator on the global low band
is

\[
 F_\Lambda(E)=PHP-E-PHQ(QHQ-E)^{-1}QHP.               \tag{16.3}
\]

In an arbitrary finite cubic subgraph, one nearest-neighbour edge overlaps,
including itself, with at most

\[
 \kappa_{\rm ov}\le1+2(z-1)=11\qquad(z\le6).          \tag{16.4}
\]

Equality holds for bulk edges and sufficiently large periodic tori;
boundary edges can have fewer overlaps.  Disjoint local off-block images are
orthogonal.  With the v1.9 one-bond
constant

\[
 \epsilon=8c(b+2ma+a^2),                              \tag{16.5}
\]

the overlap Cauchy bound and (16.2) give

\[
 \|QHP\|^2\le11|E(\Lambda)|\epsilon^2,
 \qquad
 0\le PHQ(QHQ-E)^{-1}QHP
 \le {11|E(\Lambda)|\epsilon^2\over\Gamma-E}P.       \tag{16.6}
\]

For explicit relative-form bookkeeping, define

\[
 P_{xy}=P_xP_y,\qquad Q_{xy}=1-P_{xy}.                \tag{16.7}
\]

Apply two Young parameters `u,t>0` to the centered estimate (7.4).  The
*diagonal local-high compression* of one bond has high-form coefficient

\[
 \eta_b=8c(1+u^{-1})(1+t^{-1})A_Q                    \tag{16.8}
\]

and local scalar coefficient

\[
 \nu_b=16c[(1+u)m^2+(1+u^{-1})(1+t)a^2].             \tag{16.9}
\]

Because
`Q_(xy)(k_x+k_y)Q_(xy)>=Gamma Q_(xy)`, the precise projected inequality is

\[
 Q_{xy}B_{xy}Q_{xy}
 \le(\eta_b+\nu_b/\Gamma)
 Q_{xy}(k_x+k_y)Q_{xy}.                               \tag{16.10}
\]

Equation (16.10) is only the diagonal high compression.  It is not the
different full centered-residual/off-diagonal estimate (16.5), whose norm
constant is `epsilon=8c(b+2ma+a^2)`.  Summing the six diagonal high forms at
one site gives

\[
 \zeta=6(\eta_b+\nu_b/\Gamma).                        \tag{16.11}
\]

At `u=t=1`, `eta_b=32cA_Q` and `nu_b=32cm^2+64ca^2`.
The v1.9 corridor gives

\[
 \epsilon=O(N^{-3}),\qquad \zeta=O(N^{-2}).           \tag{16.12}
\]

There is therefore a nonempty relative-form smallness precursor.  Equations
(16.3)--(16.10) are not a quasi-local rank-two Lie--Schwinger theorem or a
QPS norm for the oscillator self-energy.

## 17. Exact compressed-TFIM two-phase QPS theorem

This section concerns only the finite-spin Hamiltonian (6.4).  At
`delta_eff=0`, assign each positive-coordinate cubic bond exactly once.  A
forward star contains the center and its three positive neighbours, with
local block

\[
 h_*^{(0)}=J\sum_{i=1}^3(1-s_0s_i).                  \tag{17.1}
\]

Direct enumeration gives

\[
 \operatorname{spec}h_*^{(0)}=
 \{0^{\times2},(2J)^{\times6},(4J)^{\times6},(6J)^{\times2}\}.          \tag{17.2}
\]

The two local ground vectors are the all-plus and all-minus `s` product
vectors and the local gap is `2J`.  Introduce only for phase selection the auxiliary parameter
`u sum_x(1-s_x)`.  With the convention
`k_u=d(e_plus-e_minus)/du`, the plus/minus selector densities are `0` and
`2`, so the first-order energy split is

\[
 k=(0,-2).                                             \tag{17.3}
\]

The physical transverse perturbation `delta_eff sum_x P_(1,x)` is bounded,
finite range and invariant under the global onsite parity that sends
`s_x` to `-s_x`.  Hence the coexistence surface is pinned locally to `u=0`.

The applicable primary authority is D. A. Yarotskii, *Quantum
Pirogov--Sinai theory*, Russian Math. Surveys 61:2 (2006), 371--372,
<https://doi.org/10.1070/RM2006v061n02ABEH004323>,
<https://www.mathnet.ru/eng/rm1728>.  Its stated two-phase theorem now has
the load-bearing finite-dimensional product references, local gap, nonzero
split vector and bounded finite-range perturbation.  Consequently there is
an existential `epsilon_Y>0` such that

\[
 {|\delta_{\rm eff}|\over 2J}<\epsilon_Y              \tag{17.4}
\]

gives the two pure translation-invariant infinite-lattice compressed-TFIM
phases, exponential clustering, and a positive GNS Hamiltonian gap in each
selected phase.

This does not assert finite-torus exact degeneracy, an explicit
`epsilon_Y` or `N_0`, applicability to the finite `r=-9` diagnostic, a
rank-two oscillator block transfer, or the oscillator broken-sector gap.
The distinct single-phase CMP theorem `math-ph/0412040` is not the authority
for (17.4).

## 18. Extensive self-energy does not imply QPS locality

The third new negative is

`NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY`.

Let one high vector of energy `Gamma` couple with equal amplitude `epsilon`
to `M` orthogonal low vectors.  Below the high level, its exact self-energy is

\[
 \Sigma_M(E)={\epsilon^2\over\Gamma-E}{\bf1}{\bf1}^T.                  \tag{18.1}
\]

Its norm is `M epsilon^2/(Gamma-E)`, but every off-diagonal matrix element is
nonzero.  Thus an extensive global norm bound such as (16.6) contains no
interaction-decay, connected-cluster or polymer-locality information.  It
cannot automatically be promoted to a two-phase QPS norm.  The fixture does
not obstruct a linked-cluster, Lie--Schwinger or local resolvent expansion;
that is precisely the remaining oscillator route.

## 19. Adversarial review and updated parent verdicts

1. **Objection -- sign/order:** (12.3) and (12.5) use the same Duhamel
   ordering. **DISMISSED.** They explicitly use opposite orderings; only the
   adjacent full flow commutes with `rho`.
2. **Objection -- context:** trace-distance stability implies observable
   dynamics. **UPHELD as an overreach.** Section 13 has zero trace distance
   and constant automorphism error; bounded half-modular contexts are a real
   extra hypothesis.
3. **Objection -- covariance:** periodic translations identify every bond.
   **UPHELD as an overreach.** They leave three orientation orbits; rotations
   and covariance of the actual partial history are separate inputs.
4. **Objection -- factor:** the cubic bond-overlap constant is ten.
   **DISMISSED.** Ten is the number of *other* incident bonds; the quadratic
   overlap bound includes the bond itself and therefore uses eleven.
5. **Objection -- extensivity:** (16.6) is already a QPS interaction norm.
   **UPHELD as an overreach.** Section 18 gives an exact dense self-energy with
   the same extensive scaling.
6. **Objection -- theorem source:** the single-phase CMP theorem proves the
   two-phase TFIM claim. **DISMISSED.** Section 17 cites the distinct
   Yarotskii two-phase RMS theorem and verifies its forward-star data.
7. **Objection -- finite parameter:** the existential QPS radius includes
   `r=-9` or a displayed finite `N`. **UPHELD.** No explicit radius or finite
   onsite enclosure is available.
8. **Objection -- closure:** the compressed phasewise gap is the oscillator
   GNS gap. **UPHELD.** The rank-two quasi-local transfer and beta-infinity
   oscillator phase identification remain open.

9. **Objection -- units:** the Duhamel and Feshbach bounds mix incompatible
   dimensions. **DISMISSED.** `|t|rho(W^2)^(1/2)/hbar` is dimensionless,
   while `epsilon^2/(Gamma-E)` has energy units, exactly matching the two
   quantities they bound.
10. **Objection -- hardcode masking:** `11`, `1296`, and the star
    multiplicities were pasted conclusions. **DISMISSED.** Both verifiers
    derive the upper `11` from the cubic degree bound and realize equality on
    a sufficiently large periodic fixture, `1296=54^2(1/3)^2 4`, and the
    multiplicities by independent sixteen-configuration enumeration; their
    displayed literals are labelled test oracles.
11. **Objection -- convergence:** finite-volume Duhamel control is already a
    thermodynamic or `n -> infinity` limit. **UPHELD as an overreach.** The
    common form-core/Duhamel hypotheses are finite-volume, and all such limits
    remain in the parent gate.

External adversarial review is invited especially on the unbounded Duhamel
domain hypotheses, the disjoint-edge orthogonality used in (16.6), and the
scope of the cited two-phase Yarotskii theorem.

The dynamics parent
`PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA`
remains open: (14.3), `n -> infinity`, all-shape exhaustion Cauchy,
group/generator completion and the common phase-KMS quotient are missing.

The rank-two parent
`PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS`
remains open: (16.6) is global/extensive and does not produce a quasi-local
oscillator effective interaction or cutoff removal.

The spectral parent
`PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY`
remains open: Section 17 proves a phasewise gap only for the exact compressed
finite-spin TFIM, not for the oscillator lattice.

`PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE` also remains open.
Nothing in v2.0 closes C6, CP1, physical Sector A, or Pre-A.

## 20. Post-validation combined v0.9 checkpoint issuance

After the proof-first package and only after the proof, formal-authority,
integrated, source-form, freshness, extraction, and render-review gates passed,
one combined R-167 v2.0 / R-168 v1.1 gate-level checkpoint was issued.
Its exact artifacts are:

1. source:
   `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-checkpoint-260811-v0.9.tex.txt`;
2. source SHA-256:
   `ca8b0fdc1c4881aa13e3311851c719d0b6a0dfb4b27e0bb30906f7bc77b04239`;
3. PDF:
   `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-checkpoint-260811-v0.9.pdf`;
4. PDF SHA-256:
   `346595c8609be1e49fb33d87e5a469b01f9083c78d7a1fc89d3648b88ea4d243`;
5. page count: exactly 10.

The final R-167 v2.0 primary, non-importing independent, and integrated
contracts are `PASS 153/153`, `PASS 117/117`, and `PASS 220/220`.  The final
R-168 v1.1 contracts are `PASS 205/205`, `PASS 223/223`, and `PASS 262/262`.
Both pypdf and pdfplumber extracted 10/10 nonempty pages.  The build log had
zero Overfull `\hbox` warnings, and direct all-page review found zero
clipping, overlap, broken equations, unreadable identifiers, black glyphs,
malformed page transitions, or other visual defects.

No per-lemma or intermediate PDF was issued.  The v0.9 source/PDF pair is the
single combined post-validation checkpoint for these additive results.  The
historical v0.8 source/PDF remains prior R-167 v1.9 / R-168 v1.0 evidence and
is not current v2.0/v1.1 evidence.  This issuance changes no claim tier and
closes none of the common-alpha, rank-two oscillator, oscillator GNS-gap,
physical-response, prospective-freeze, physical Sector-A, or Pre-A parents.
