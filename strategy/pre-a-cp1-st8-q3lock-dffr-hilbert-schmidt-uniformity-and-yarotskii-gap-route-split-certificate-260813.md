# R-167 v3.4 proof certificate: DFFR Hilbert--Schmidt uniformity and the conditional Yarotskii gap route

## 1. Verdict and exact authority boundary

This proof-first package closes exactly two conditional reductions:

1. `PA-CP1-ST8-Q3LOCK-CONDITIONAL-M-UNIFORM-DFFR-HILBERT-SCHMIDT-SIMULTANEOUS-ENTRY-REDUCTION`;
2. `PA-CP1-ST8-Q3LOCK-FIXED-RITZ-YAROTSKII-RELATIVE-SPLIT-AND-CONDITIONAL-PHASEWISE-GNS-GAP-REDUCTION`.

It also registers the exact obstruction

`NG-2026-08-13-PRE-A-ST8-Q3LOCK-UNIFORM-RELATIVE-FORM-AND-OPERATOR-BLOCK-BOUNDS-AUTOMATIC-M-UNIFORM-DFFR-HILBERT-SCHMIDT-ENTRY`.

The first result states sufficient *uniform hypotheses* under which the
fixed-`M` theorem of R-167 v3.3 would enter DFFR Theorem 5.2 simultaneously
for every Ritz label. It does
not prove those hypotheses for Q3. The obstruction proves that the available
relative-form and operator-norm estimates cannot supply the missing
Hilbert--Schmidt hypothesis by themselves.

The second result proves an exact finite-dimensional relative-plus-bounded
split. Conditional on one fixed-`M`, `N`-independent Yarotskii two-phase
rectangle and all of that source theorem's hypotheses, it reduces eventual
physical-residual entry to two quantities tending to zero and inherits the
source theorem's phasewise GNS spectral-gap conclusion. It does not provide
the rectangle and does not identify its branches with the DFFR branches.

EXP-000838 records this R-167 v3.4 continuation. No v3.4 PDF is issued.

## 2. Primary-source firewall

The DFFR source is N. Datta, R. Fernandez, J. Frohlich and L. Rey-Bellet,
*Low-Temperature Phase Diagrams of Quantum Lattice Systems. II. Convergent
Perturbation Expansions and Stability in Systems with Infinite Degeneracy*,
Helvetica Physica Acta 69 (1996), 752--820. Its interaction Banach norm in
(4.7) is built from Hilbert--Schmidt norms. Equation (4.10) compares that norm
with operator norm only in finite dimension, with a factor depending on the
local Hilbert-space dimension. Theorem 5.2 and (5.21)--(5.22) use the four
actual Hilbert--Schmidt low/high block constants.

The phrase "infinite degeneracy" in that title concerns degeneracy of a
classical low-energy sector. It is not an infinite-onsite theorem. The same
paper states in Section 4.2 that its Section 5.2 contour method does not apply
to bosonic systems with arbitrarily large onsite occupation without a
regularity condition, obtained there from a suitable hardcore condition for
Gibbs states. This is a direct-import boundary, not a proof that no different
weighted infinite-onsite contour theorem can exist.

The single-phase source is D. A. Yarotsky, *Ground states in relatively
bounded quantum perturbations of classical lattice systems*, Communications
in Mathematical Physics 261 (2006), 799--819, DOI
`10.1007/s00220-005-1456-9`, arXiv `math-ph/0412040`. Its Theorems 1--2 allow
possibly infinite-dimensional onsite spaces, but require one simple product
reference ground vector. They motivate the relative-plus-bounded split below;
they do not establish zero-source two-phase coexistence.

The two-phase source is D. A. Yarotskii, *Pirogov--Sinai theory for relatively
bounded quantum perturbations of classical lattice models*, Russian
Mathematical Surveys 61:2 (2006), 371--372, DOI
`10.1070/RM2006v061n02ABEH004323`. Its announcement assumes a
finite-dimensional onsite spin space, two distinguished product ground
vectors, a positive local gap, smooth finite-range parameter dependence and a
nonzero first-order energy splitting. For a sufficiently small existential
neighbourhood it states exactly two pure translation-invariant ground states
on the coexistence surface, exponential clustering, and in clause (e) a
spectral gap in each ground state. It gives no dimension-, cutoff- or
`N`-uniform rectangle and no numerical gap.

## 3. Conditional simultaneous DFFR entry

Fix `lambda_0` in `(0,1)` and one integer `N_ref` independent of `M`. Let `M`
range over finite complete parity-preserving Ritz labels. For every `M` and
every `N>=N_ref`, assume a complete DFFR two-level reference with the same
finite range and the same two period-one patterns. Suppose there are constants

\[
 \kappa_0,c,\epsilon_*,\bar\kappa_*>0,\qquad C\geq0,
 \qquad A_{\ell\ell},A_{\ell h},A_{h\ell},A_{hh}\geq0                  \tag{3.1}
\]

independent of `M,N` such that

\[
 \kappa_{M,N}\geq\kappa_0,
 \qquad D_{M,N}\geq cN^2-C,                                         \tag{3.2}
\]

and the *actual Hilbert--Schmidt constants in DFFR (5.21)* obey

\[
 \epsilon_{\ell\ell}\leq {A_{\ell\ell}\over N^2},\qquad
 \epsilon_{\ell h}\leq {A_{\ell h}\over N},\qquad
 \epsilon_{h\ell}\leq {A_{h\ell}\over N},\qquad
 \epsilon_{hh}\leq A_{hh}.                                         \tag{3.3}
\]

Finally assume that the constants produced by Theorem 5.2 are uniform on
this family:

\[
 \inf_{M,N}\epsilon_0(M,N)\geq\epsilon_*,
 \qquad
 \inf_{M,N}\bar\kappa(M,N)\geq\bar\kappa_* .                        \tag{3.4}
\]

These two lower bounds are hypotheses. They are not inferred from the
existence of a positive threshold at each fixed `M`.

For `N^2>=2C/c`, put

\[
 K_N=\kappa_0+cN^2-C>0.                                              \tag{3.5}
\]

Then `kappa_(M,N)+D_(M,N)>=K_N`. The five nonthermal entries of DFFR (5.22)
are bounded, uniformly in `M`, by

\[
\begin{split}
 q_{\ell\ell}(N)&={\lambda_0A_{\ell\ell}\over\kappa_0N^2},\\
 q_{\rm pair}(N)&=\lambda_0
  \sqrt{{A_{\ell h}A_{h\ell}\over N^2\kappa_0K_N}},\\
 q_{hh}(N)&={\lambda_0A_{hh}\over K_N},\\
 q_{h\ell}(N)&={\lambda_0A_{h\ell}\over NK_N},\qquad
 q_{\ell h}(N)={\lambda_0A_{\ell h}\over NK_N}.                    \tag{3.6}
\end{split}
\]

Define `q_N` as their maximum. Each expression tends to zero. Therefore any
`N` satisfying

\[
 N\geq N_{\rm ref},\qquad
 N^2\geq {2C\over c},\qquad q_N<\epsilon_*                           \tag{3.7}
\]

and any `beta` satisfying

\[
 e^{-\beta\bar\kappa_*}<\epsilon_*                                  \tag{3.8}
\]

enter Theorem 5.2 simultaneously for every `M`. This proves the conditional
simultaneous-entry reduction. It does not prove a common `N_ref`, (3.3) or
(3.4) for the Q3 Ritz family and does not construct a cutoff limit of the
resulting states.

## 4. Exact Hilbert--Schmidt multiplicity obstruction

For integers `m,N>=1` and fixed `J>0`, take one-site space

\[
 {\cal H}_m=\mathbb C^{m+2},\qquad \operatorname{rank}p_m=2,
 \qquad q_m=1-p_m.                                                    \tag{4.1}
\]

On a two-site edge define

\[
 P_m=p_m\otimes p_m,\qquad Q_m=1-P_m,
 \qquad R_m=q_m\otimes q_m.                                         \tag{4.2}
\]

Thus `rank P_m=4`, `rank R_m=m^2`, and `R_m<=Q_m`. Let `R_dis` be the
projection onto the two disagreeing labels inside the four-dimensional low
space and set

\[
 h^0_{m,N}=N^2Q_m+2J R_{\rm dis},\qquad V_{m,N}=R_m.                 \tag{4.3}
\]

The strict sign `J>0` gives exactly two aligned low zero labels. More importantly for the
tested implication,

\[
 0\leq V_{m,N}\leq Q_m\leq N^{-2}h^0_{m,N}.                         \tag{4.4}
\]

Hence the relative-form coefficient is `N^-2`, with additive coefficient
zero, uniformly in `m`. The low-low and both mixed blocks vanish, while

\[
 \|Q_mV_{m,N}Q_m\|_{\rm op}=1,
 \qquad
 \|Q_mV_{m,N}Q_m\|_{\rm HS}=\sqrt{\operatorname{rank}R_m}=m.        \tag{4.5}
\]

For edge support size two and `lambda_0=1/2`, (5.21) assigns
`epsilon_hh=4m`. Even granting the favourable high penalty `D_N=N^2`, the
high-high entry is

\[
 {\lambda_0\epsilon_{hh}\over\kappa+D_N}
 ={2m\over\kappa+N^2}.                                               \tag{4.6}
\]

For each fixed `m`, (4.6) tends to zero with `N`; for every fixed `N`, its
supremum over `m` is infinite. Thus uniform relative-form decay plus a
uniform operator-norm block does not imply the M-uniform Hilbert--Schmidt
hypothesis (3.3).

This no-go is not the earlier ordinary-operator Schrieffer--Wolff cutoff
obstruction: here the high-high operator norm is exactly one for all cutoffs.
It is not the shrinking-radius fixture either: the failure is already the
explicit unnormalized Hilbert--Schmidt input before any theorem radius is
used. It also is not a no-go for an energy-weighted infinite-onsite contour
theorem that retains the high spectral partition function.

## 5. Exact relative-plus-bounded split

Let `h` be a nonnegative operator on one finite-dimensional local support.
Let

\[
 P=1_{\{0\}}(h),\qquad Q=1-P,
 \qquad h\geq gQ\quad(g>0),\qquad \|h\|=L.                           \tag{5.1}
\]

Suppose the selfadjoint residual `V` satisfies

\[
 |\langle\psi,V\psi\rangle|
 \leq\alpha\langle\psi,h\psi\rangle
       +\epsilon\|\psi\|^2.                                       \tag{5.2}
\]

Put `B=alpha h+epsilon I`. Form domination gives

\[
 V=B^{1/2}{\cal C}B^{1/2},\qquad {\cal C}={\cal C}^*,
 \qquad\|{\cal C}\|\leq1.                                         \tag{5.3}
\]

This is immediate by conjugating with `B^-1/2` when `epsilon>0`; the support
limit gives the same statement when `B` has a kernel. Since `B` commutes with
`P,Q`,

\[
 \|PVP\|\leq\epsilon,
 \qquad
 \|PVQ\|=\|QVP\|
 \leq\sqrt{\epsilon(\alpha L+\epsilon)}.                            \tag{5.4}
\]

Define

\[
 V^{(r)}=QVQ,
 \qquad V^{(b)}=V-V^{(r)}=PVP+PVQ+QVP.                              \tag{5.5}
\]

On `Q`, equations (5.1)--(5.3) give

\[
 |\langle\psi,V^{(r)}\psi\rangle|
 \leq \left(\alpha+{\epsilon\over g}\right)
       \langle\psi,h\psi\rangle.                                  \tag{5.6}
\]

The triangle inequality and (5.4) give

\[
 \|V^{(b)}\|
 \leq \epsilon+2\sqrt{\epsilon(\alpha L+\epsilon)}.               \tag{5.7}
\]

Thus the exact split coefficients are

\[
 a=\alpha+{\epsilon\over g},
 \qquad
b=\epsilon+2\sqrt{\epsilon(\alpha L+\epsilon)}.                  \tag{5.8}
\]

In ASCII notation these coefficients are `a=alpha+epsilon/g` and
`b=epsilon+2 sqrt[epsilon(alpha L+epsilon)]`.

For the grouped Q3 star input, `epsilon_N=3 beta_N`. At fixed Ritz label
`M`, v1.9 gives `alpha_N=O_M(N^-2)` and `beta_N=O_M(N^-3)`, while the fixed
Ritz reference has `g_(M,N)>=g_(0,M)>0` and `L_(M,N)=O_M(N^2)`. Hence

\[
 a_{M,N}=O_M(N^{-2}),\qquad b_{M,N}=O_M(N^{-3/2}).                  \tag{5.9}
\]

After normalizing the local gap to one, the two inputs are `a_(M,N)` and
`b_(M,N)/g_(M,N)`.

## 6. Conditional fixed-Ritz Yarotskii phasewise-gap reduction

Fix one Ritz label `M`. The following is an explicit premise, not a result of
the cited two-page announcement:

> There are positive `a_(Y,M),b_(Y,M)`, independent of `N`, for the fixed
> support and range such that every member of the finite-dimensional
> two-product family satisfying the exact local two-product zero-kernel and
> gap hypotheses, smooth odd-source dependence, nonzero first-order source
> splitting, `a<a_(Y,M)` and `b/g<b_(Y,M)` lies in the Yarotskii two-phase
> neighbourhood. The physical residual is included through a smooth coupling
> coordinate, and the theorem's clause (e) is instantiated as the spectral
> gap of the implementing Hamiltonian in each phase GNS representation.

By (5.9), the normalized split enters this rectangle for all sufficiently
large `N` at fixed `M`. Parity exchanges the two reference patterns, leaves
the physical residual invariant and reverses the bounded odd source. The
smooth maximal-coexistence graph is therefore mapped to itself by source
reflection; its unique source coordinate is zero.

Under the stated premise, at the physical residual endpoint and zero source
the Yarotskii theorem consequently supplies exactly two pure
translation-invariant ground-state branches, exponential clustering, and a
positive phasewise GNS implementing spectral gap in each branch. This is a
logical reduction of the target conclusion to a named uniform rectangle.
Neither the rectangle nor a numerical lower gap is derived here.

In particular, the DFFR stable low-temperature branches and their
beta-to-infinity cluster limits are not automatically the Yarotskii branches.
Their identification would require an additional common-algebra continuation
or uniqueness theorem. Nor does a gap at each fixed `M,N` give an `N`-uniform
or `M`-uniform gap. The finite-dimensional source cannot be passed to the
full oscillator without a new cutoff-stable theorem.

## 7. Exact fixtures

### 7.1 Simultaneous-entry arithmetic

Take

\[
 \lambda_0={1\over2},\quad N_{\rm ref}=1,\quad
 \kappa_0=2,\quad c=C=1,
 \quad\epsilon_*={1\over4},\quad\bar\kappa_*={1\over2},\quad N=5,
\]

and

\[
 (A_{\ell\ell},A_{\ell h},A_{h\ell},A_{hh})=(2,3,3,5).
\]

Then `K_N=26`. Equations (3.6) give, in order,

\[
 {1\over50},\quad {3\sqrt{13}\over260},\quad {5\over52},
 \quad {3\over260},\quad {3\over260}.                              \tag{7.1}
\]

At `beta=6 log 2`, the thermal term is `1/8`. The maximum of all six
entries is `1/8<1/4`. These numbers test only the conditional algebra; they
do not assert Q3 values for the hypothesis constants.

### 7.2 Split arithmetic and a contraction witness

Let

\[
 h=\operatorname{diag}(0,0,16,N^2),\quad N=10,
 \quad\alpha=N^{-2},\quad\beta_{\rm edge}=N^{-3},
 \quad\epsilon=3\beta_{\rm edge}.                                  \tag{7.2}
\]

Then `g=16`, `L=100`, and

\[
 \epsilon={3\over1000},\quad
 a={163\over16000},\quad
 \sqrt{\epsilon(\alpha L+\epsilon)}={\sqrt{3009}\over1000},
 \quad b={3+2\sqrt{3009}\over1000}.                               \tag{7.3}
\]

For a concrete form witness, let `B=alpha h+epsilon I` and take the
selfadjoint contraction `C` that is `+1` on the first and third basis
vectors and swaps the second and fourth. Then `V=B^(1/2) C B^(1/2)` obeys
`-B<=V<=B`; its `PVP`, mixed and `QVQ` pieces attain the component bounds
used in (5.4)--(5.6) on mutually orthogonal blocks.

### 7.3 Minimal finite HS failure sample

In Section 4 take `N=5`, `m=4`, `kappa=1`, `D=N^2` and
`lambda_0=1/2`. The onsite dimension is six,

\[
 \operatorname{rank}P=4,
 \quad\operatorname{rank}Q=32,
 \quad\operatorname{rank}R=16.                                     \tag{7.4}
\]

The relative coefficient is `1/25`, the high-high operator norm is one,
and the Hilbert--Schmidt norm is four. Thus `epsilon_hh=16` and

\[
 {\lambda_0\epsilon_{hh}\over\kappa+D}={4\over13}>{1\over4}.       \tag{7.5}
\]

The symbolic family (4.6), rather than this one sample, proves the no-go.

## 8. Adversarial scope audit

1. **Could the operator-norm estimate be converted uniformly to
   Hilbert--Schmidt norm? UPHELD as a failure.** Equation (4.5) keeps operator
   norm one while Hilbert--Schmidt norm grows exactly like `m`.
2. **Does a positive DFFR threshold for each cutoff give (3.4)? UPHELD as a
   failure.** Pointwise positivity has no positive infimum; the registered
   shrinking-radius fixture remains applicable.
3. **Does DFFR II directly cover the exact oscillator? UPHELD as an import
   mismatch.** Its displayed norms are Hilbert--Schmidt and its own bosonic
   discussion requires extra regularity/hardcore control.
4. **Does the split prove a two-phase theorem? UPHELD as a failure.** It proves
   only (5.8). The fixed-`M` uniform rectangle in Section 6 is an explicit
   premise.
5. **Can the DFFR and Yarotskii branches be silently identified? UPHELD as a
   failure.** This package expressly forbids that identification without a
   common-algebra continuation or uniqueness theorem.
6. **Do ordered ground doublets alone imply a GNS gap? UPHELD as a failure.**
   The prior negative remains. The conditional conclusion here uses clause
   (e) of the assumed applicable Yarotskii theorem, not order alone.
7. **Is the phasewise gap uniform in `N` or `M`? UPHELD as a failure.** No
   lower bound is supplied, so no limiting gap follows.
8. **Does simultaneous DFFR entry pass states through the Ritz cutoff?
   UPHELD as a failure.** A state-compactness/common-algebra/KMS or generator
   identification theorem is still missing.

## 9. No-overclaim boundary

The package proves no actual M-uniform DFFR entry for Q3, no Yarotskii
rectangle, no DFFR/Yarotskii branch identity, no full-oscillator phase
passage, no cutoff-stable KMS or ground state, no common spatial algebra, no
all-shape dynamics, no common-alpha, no exact-Q3 target generator, no
exact-Q3 GNS gap, no mass gap, no regulator removal, no continuum theorem,
no physical-vacuum or empty-space comparison, no Round-1 closure, no C6 or
CP1 closure, and no physical Sector A or Pre-A closure.

All five active parent gates remain OPEN. The historical
`PA-CP1-ST8-Q3LOCK-BETA-INFINITY-GROUND-STATE-SELECTION` also remains OPEN in
its exact-Q3/common-alpha scope. The direct-Yarotsky import, ordered-doublet
gap and shrinking-radius negatives remain valid at their registered scopes.
