# EXP-000798 certificate: modular cutoff and unitary resummation route split

**Result:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT` v1.2 (`R-167`)  
**Task:** `T-054`  
**Claim context:** `C6-SPACETIME-SIGNATURE` only  
**Tier:** T0, claim-nonbearing  
**Date:** 2026-08-10

## 1. Purpose and inherited scope

This is a short additive extension of R-167 v1.1. It does not repeat or alter
the v1.0/v1.1 weighted-energy, cubic-graph, moving-center, or prescribed-word
heat theorems. It answers the two gates left by `EXP-000796`.

1. The proposed fixed-energy-power, coefficientwise first-passage response is
   false already on an exact degree-four substar of the Q3LOCK lattice.
2. The failure is organizational rather than dynamical: the same star resums
   over all orders to an exact unitary phase.
3. A unique-path tree has an exact sequential-activation Duhamel formula, but
   the smallest square exposes the alternate-path remainder on a loopy lattice.
4. At fixed positive temperature, an arithmetic/logarithmic-mean inequality
   converts Duhamel convergence plus one bounded modular derivative into a
   genuine two-sided GNS topology.
5. The already imported Euclidean exponential estimate makes a coordinate-only
   bond cutoff and its first modular derivative exponentially small. What
   remains is a structured projected-Duhamel or modular-multiplier locality
   theorem, not an intrinsically necessary fifth onsite-energy moment.

No new reusable-result number is allocated. The exact result ID remains the
one printed above, and the version is advanced to v1.2.

## 2. Exact fixed-order star and repeat counterexample

Fix one internal component. At a central site 0 and distinct leaves
`j=1,...,m`, put

\[
 V_j=-c q_0q_j,
 \qquad
 W_0(a)=\exp(-ia p_0/\hbar).
\]

The Weyl relation gives `[q_0,W_0(a)]=aW_0(a)`. Every `q_j` commutes with
`W_0(a)` and all of the multiplication operators `V_j` commute. Induction
therefore gives the exact identity

\[
 \operatorname{ad}_{V_m}\cdots\operatorname{ad}_{V_1}W_0(a)
 =(-ca)^m\Big(\prod_{j=1}^m q_j\Big)W_0(a).       \tag{2.1}
\]

All `m!` orderings have the same coefficient and operator. Repeating one edge
instead gives

\[
 \operatorname{ad}_{V}^{,n}W_0(a)=(-ca)^nq_y^nW_0(a). \tag{2.2}
\]

Let `A=1+E_f` be the positive centered energy of R-167 and translate a fixed
smooth product bump so every active leaf coordinate is of size `R`. For this
family,

\[
 \|A^s\psi_R\|=O(R^{4s}),
 \qquad
 \left\|\Big(\prod_{j=1}^m q_j\Big)W_0(a)\psi_R\right\|
 \ge c_0R^m.                                      \tag{2.3}
\]

Taking `A^s psi_R` as the input shows that the right graph operator is
unbounded when `m>4s`; applying the same argument to the adjoint gives the left
orientation. Consequently

\[
 s={1\over2}:\ m=3\text{ is the first translated-bump failure},
 \qquad
 s={3\over4}:\ m=4\text{ is the first failure}.   \tag{2.4}
\]

The cubic lattice has degree six, so both stars occur. One leaf can be called
the length-one first-passage backbone and the others side branches. Thus the
literal v1.1 response target fails inside its declared class. Equation (2.3)
does not decide the endpoint `m=4s`, and it is not a nonexistence theorem for
the dynamics.

This fires
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-S-COEFFICIENTWISE-FIRST-PASSAGE-BRANCH-RESPONSE`.

## 3. All-order cancellation is exact

Put `V_star=sum_j V_j`. Since the first commutator in (2.1) is multiplication
by `-ca sum_j q_j` and that multiplier commutes with `V_star`, the full series
can be summed:

\[
 \operatorname{Ad}\!\left(e^{itV_{\rm star}/\hbar}\right)W_0(a)
 =\exp\!\left[-{icat\over\hbar}\sum_jq_j\right]W_0(a). \tag{3.1}
\]

The missing `i` is essential: for real parameters the new factor is unitary.
If `Z_1(b)=exp(-ibp_1/hbar)`, Weyl covariance gives a scalar response factor,
and hence

\[
 \big\|[Z_1(b),\operatorname{Ad}(e^{itV_{\rm star}/\hbar})W_0(a)]\big\|
 \le {|cabt|\over\hbar}.                            \tag{3.2}
\]

The bound is independent of the number of side branches. The cancellation
therefore occurs across all perturbation orders, not between histories at one
fixed order. Equation (3.1) is only the exact bond subflow; it does not include
the onsite quartic flow or establish thermodynamic locality.

## 4. Unique-path tree theorem and the square boundary

Let a finite graph be a tree and let `e_1,...,e_d` be the unique path between
the supports of local observables `A_0` and `B`. Removing these path edges
leaves components `C_0,...,C_d`. Put every internal and branch interaction of
the `C_k` into `H_0`, and define

\[
 H_k=H_0+\sum_{r=1}^kV_{e_r},\qquad
 \mathcal U_k(t)=\operatorname{Ad}(e^{itH_k/\hbar}),\qquad
 \mathcal D_r={i\over\hbar}\operatorname{ad}_{V_{e_r}}. \tag{4.1}
\]

Successive Duhamel identities and the tree separation property give

\[
\begin{aligned}
 [\mathcal U_d(t)A_0,B]
 ={}&\int_{0<t_1<\cdots<t_d<t}
 \big[\mathcal U_d(t-t_d)\mathcal D_d
 \mathcal U_{d-1}(t_d-t_{d-1})\cdots\\
 &\hspace{32mm}\cdots\mathcal D_1\mathcal U_0(t_1)A_0,B\big]
 \,d\mathbf t .                                    \tag{4.2}
\end{aligned}
\]

Every path edge occurs once. Branches and all repetitions after activation are
inside exact unitary propagators. This is an exact positive theorem, but it
does not supply the graph-energy norm bound on the integrand.

On the square `0-1-2-3-0`, choosing `0-1-2` as a backbone leaves the path
`0-3-2`. Thus the base Hamiltonian can already connect the endpoint supports,
and (4.2) acquires an alternate-path remainder. A general cubic lattice needs
a separating-cut/forest expansion or a global bond resummation. This does not
reject such constructions.

## 5. Surviving phase-independent Trotter gate

Split the exact finite-volume Hamiltonian as

\[
 H=H_{\rm on}+V_{\rm cross},\qquad
 H_{\rm on}=\sum_xh_x,\qquad
 V_{\rm cross}=-c\sum_{\langle xy\rangle}q_x\cdot q_y. \tag{5.1}
\]

All cross-bond terms commute, even when they share a vertex. Hence their
finite-volume kick factorizes exactly. Its canonical action is

\[
 q_x\mapsto q_x,\qquad
 p_x\mapsto p_x+\delta c\sum_{y\sim x}q_y.          \tag{5.2}
\]

The inverse is the negative step, and support expands by at most one graph
layer. A weighted shifted-square inequality plus `q^2<=epsilon q^4+1/(4
epsilon)` gives a finite form-growth precursor. The onsite flow is tensor
local, and the v1.1 cubic graph theorem controls its first force multipliers.

What is still missing is one phase-independent, two-sided graph-Lipschitz
Banach core stable under both exact subflows. If it obeyed the one-step
recurrence

\[
 L_x'\le(1+C\delta)L_x+J\delta\sum_{y\sim x}L_y,     \tag{5.3}
\]

then the exactly `d`-transfer coefficient after `N` steps would be

\[
 {N\choose d}(Jt/N)^d(1+Ct/N)^{N-d}
 \le e^{Ct}(Jt)^d/d!,                              \tag{5.4}
\]

up to the standard finite-`N` correction. This is only a conditional reduction.
The new open gate is
`PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE`.

## 6. Duhamel-to-GNS modular-mean theorem

Let `rho>0` be a faithful Gibbs density in a fixed finite-volume type-I
representation, and suppose that `X` and `[log rho,X]` belong to the Duhamel
form domain. Define

\[
 \|X\|_D^2=\int_0^1\operatorname{Tr}
 (\rho^{1-s}X^*\rho^sX)\,ds,
 \qquad
 \|X\|_\#^2={1\over2}\operatorname{Tr}\rho(X^*X+XX^*). \tag{6.1}
\]

In an eigenbasis of `rho`, these have the logarithmic-mean and arithmetic-mean
weights `L(p_m,p_n)` and `A(p_m,p_n)`. For
`u=|log p_m-log p_n|`,

\[
 {A\over L}={u\over2}\coth{u\over2}\le1+{u\over2}. \tag{6.2}
\]

Indeed, after multiplication by `2(e^u-1)`, (6.2) is `1+u<=e^u`.
Cauchy--Schwarz over the matrix coefficients therefore proves

\[
 \boxed{\quad
 \|X\|_\#^2\le\|X\|_D^2
 +{1\over2}\|X\|_D\|[\log\rho,X]\|_D .\quad}     \tag{6.3}
\]

For `rho=Z^{-1}e^{-beta H}` and
`delta=(i/hbar)[H,.]`,

\[
 [\log\rho,X]=i\beta\hbar\,\delta X.               \tag{6.4}
\]

Thus Duhamel convergence plus a uniform first modular-derivative bound gives
two-sided GNS convergence. On a uniformly operator-bounded set, this implies
strong-star convergence in that one fixed faithful type-I representation.
Faithfulness, or prior restriction to the support, is essential. The matrix
proof here is not a general W-star modular-operator theorem, and (6.3) does not
manufacture a common representation across volumes.

## 7. Exact structured modular multiplier lemma

On a common modular-analytic core define

\[
 M_0(B)=\sup_{|t|\le1/2}\|\rho^tB\rho^{-t}\|,
 \qquad
 M_1(B)=M_0([\log\rho,B]).                           \tag{7.1}
\]

Factoring the Hilbert--Schmidt representatives inside (6.1) gives

\[
 \|[X,B]\|_D\le2M_0(B)\|X\|_D,                    \tag{7.2}
\]

and Jacobi gives

\[
 \|[\log\rho,[X,B]]\|_D
 \le2M_0(B)\|[\log\rho,X]\|_D+2M_1(B)\|X\|_D.    \tag{7.3}
\]

Combining (6.3)--(7.3) yields

\[
\begin{aligned}
 \|[X,B]\|_\#^2\le{}&
 (4M_0^2+2M_0M_1)\|X\|_D^2\\
 &+2M_0^2\|X\|_D\|[\log\rho,X]\|_D.             \tag{7.4}
\end{aligned}
\]

The half-strip conjugations and their first modular commutator must extend
boundedly. Ordinary operator-norm control of `B` is not enough.

## 8. Arbitrary bounded multipliers fail

The insufficiency is finite-dimensional. Let

\[
 H_n=\operatorname{diag}(0,n),\quad
 \rho_n={\operatorname{diag}(1,e^{-\beta n})\over1+e^{-\beta n}},\quad
 W_n=e^{\beta n/4}|1\rangle\langle1|,\quad
 B_n=|1\rangle\langle0|.                            \tag{8.1}
\]

Then `[H_n,W_n]=0` and

\[
 \varphi_n(W_n^2)={e^{-\beta n/2}\over1+e^{-\beta n}}\longrightarrow0.
\]

Nevertheless

\[
 \|[W_n,B_n]\|_D^2
 =e^{\beta n/2}{1-e^{-\beta n}\over
 (1+e^{-\beta n})\beta n}\longrightarrow\infty,   \tag{8.2}
\]

and `phi_n(B_n^*W_n^2B_n)` also diverges. Thus even a static tail with zero
modular derivative cannot be multiplied by arbitrary contractions. This fires
`NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-MODULAR-TAIL-ARBITRARY-BOUNDED-MULTIPLIER`.

## 9. Coordinate cutoff and exact modular tail

`EXP-000781` already maps the exact Q3LOCK potential to the general Euclidean
Gibbs theorems of Kozitsky--Pasurek. Their Theorems 3.1--3.3 provide the
infinite-volume tempered-DLR one-site exponential path estimate. To derive the
finite periodic-volume bridge, define

\[
 A_x=\lambda_\sigma\|\omega_x\|_{C^\sigma}^2
        +\kappa\|\omega_x\|_2^2 .                    \tag{9.1}
\]

Finite-volume confinement makes `mu_(Lambda,h)^per(e^(A_x))` finite. Condition
the periodic Gibbs law at `x`, apply their Lemma 4.1, and integrate. Generalized
Holder with `r_y=vartheta |J^Lambda_(xy)|/kappa` and `sum_y r_y<1` gives

\[
 e^{n_x}\le e^C\prod_y e^{r_y n_y},
 \qquad n_x=\log\mu_{\Lambda,h}^{\rm per}(e^{A_x}),   \tag{9.2}
\]

and therefore

\[
 n_x\le C+{\vartheta\over\kappa}\sum_y|J^\Lambda_{xy}|n_y.
                                                               \tag{9.3}
\]

Here `Jhat_Lambda<=6c`. Periodic translation invariance and
`vartheta Jhat_Lambda < kappa` give

\[
 n_x\le {C\over1-\vartheta\widehat J_\Lambda/\kappa}. \tag{9.4}
\]

The compact-source uniformity of `C` is the stability constant already checked
in `EXP-000781`. Thus the bound is uniform in the periodic volume and compact
source interval. Moreover, for `0<r<=beta`,

\[
 |\omega(0)|^2\le 2r^{-1}\|\omega\|_2^2
                  +2r^{2\sigma}[\omega]_\sigma^2.      \tag{9.5}
\]

Given `a>0`, choose `r<=beta` with
`2 a r^(2 sigma)<=lambda_sigma`, and then choose the freely available
`L2` coefficient `kappa>=2a/r`. The conditional recursion, Holder bound and
(9.5) therefore imply, at each fixed `beta`,

\[
 \sup_{\Lambda,|h|\le h_0,x}
 \varphi_{\Lambda,h}(e^{a|q_x|^2})<\infty
 \qquad\hbox{for every }a>0.                         \tag{9.6}
\]

Primary source: Y. Kozitsky and T. Pasurek,
[*Euclidean Gibbs states of interacting quantum anharmonic oscillators*](https://arxiv.org/abs/math-ph/0609045).

Choose a smooth radial cutoff `Q_L(q)=eta(|q|/L)q`, equal to `q` on the
`L`-ball and zero outside the `2L`-ball, and truncate only the bond coordinate:

\[
 -cq_x\cdot q_y\longmapsto-cQ_L(q_x)\cdot Q_L(q_y). \tag{9.7}
\]

The truncated bond is bounded by `O(L^2)`. With
`rho=rho_(Lambda,h)`, its tail `W_L` and its gradient over both bond endpoints
and all components are polynomials supported on
`max(|q_x|,|q_y|)>L`; hence (9.6) gives, for arbitrary `a>0`,

\[
 \|W_L\|_D^2+\|[\log\rho,W_L]\|_D^2
 \le C_{a,N}L^N e^{-aL^2}.                           \tag{9.8}
\]

For rigor, first impose an outer bounded cutoff `W_(L,M)` on the common
Schrodinger core, prove the double-commutator identity there, and then send
`M` to infinity by the exponential domination in (9.6). The modular term is
then exact rather than heuristic:

\[
 \|[\log\rho,W_L]\|_D^2
 ={\beta\hbar^2\over\chi}
   \varphi(|\nabla_{(x,y)}W_L|^2).                  \tag{9.9}
\]

Suppose the still-open structured projected/multiplier comparison on
`|t|<=T` grows no faster than `poly(L)exp(C_0TL^2)`. Put `L_m=m^alpha`, with
`0<alpha<1/2`, and choose `a>C_0T`. Then

\[
 m^d\operatorname{poly}(L_m)e^{-(a-C_0T)L_m^2}\to0,
 \qquad
 \operatorname{poly}(L_m){(C_1TL_m^2)^m\over m!}\to0. \tag{9.10}
\]

Only (9.1)--(9.9) and the scale arithmetic are closed, with constants depending
on fixed `beta`, `a`, `h_0` and the model data. No beta-to-infinity uniformity
is asserted. Growth faster than `exp(CL^2)` is not covered. The successor gate is
`PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY`.

## 10. Fixed-beta OS mixture precursor

Let `0<lambda<1`, and suppose `mu_+` and `mu_-` use the same reflection,
underlying field space and positive-time test algebra. For
`mu_0=lambda mu_+ +(1-lambda)mu_-`, reflection positivity is linear:

\[
 q_0=\lambda q_+ +(1-\lambda)q_-,\qquad
 N_0=N_+\cap N_-.                                   \tag{10.1}
\]

The map

\[
 [F]_0\longmapsto
 (\sqrt\lambda[F]_+,\sqrt{1-\lambda}[F]_-)
\]

is an isometry into the direct sum of the phasewise OS Hilbert spaces. Its
range need not be the full direct sum. Under a separately proved common-field
reconstruction functor, domination would make the phase functionals normal in
the mixture W-star algebra. Central phase projections require disjointness;
extremality helps only together with a common-KMS-simplex theorem that implies
disjointness. The repository has not proved that `mu_0` is the zero-source
periodic finite-volume limit. This is a fixed-beta envelope
precursor, not a Hamiltonian common alpha or a ground-state theorem.

## 11. Route verdict and remaining proof order

The v1.1 gate
`PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-PRODUCT-AND-ENERGY-TAIL-CLOSURE`
is closed negatively as stated, while its unique-path tree subcase survives.
The v1.1 gate
`PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-MODULAR-CUTOFF-LOCALITY`
is superseded as the primary static requirement: coordinate tails already
close (9.4)--(9.6), but multiplier locality is open.

The next exact alternatives are:

1. `PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE`;
2. `PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY`.

Only after one produces a single phase- and beta-independent Hamiltonian
dynamics may the programme identify both phasewise OS/KMS systems with one
alpha, select algebraic ground states, test a broken-sector GNS gap, remove the
enlarged counterterm regulator, and compare a preregistered physical-empty
preparation under the same Hamiltonian.

## 12. Devil's-advocate audit

1. **Objection:** the star divergence proves no dynamics exists.  
   **Disposition:** UPHELD AS A SCOPE WARNING. It proves only that the fixed-`s`
   coefficientwise route is false; (3.1) shows the exact subflow is unitary.

2. **Objection:** the tree formula applies unchanged on `Z3`.  
   **Disposition:** DISMISSED. The square fixture leaves an alternate path and
   produces the precise missing remainder.

3. **Objection:** small static Gibbs tails survive multiplication by every
   evolved contraction.  
   **Disposition:** DISMISSED by (8.1)--(8.2). The modular multiplier or a
   direct projected estimate is load-bearing.

4. **Objection:** Duhamel convergence alone is already strong-star.  
   **Disposition:** DISMISSED by the prior rank-shift result. Equation (6.3)
   identifies the missing first modular derivative and representation scope.

5. **Objection:** the OS mixture is already the common physical dynamics.  
   **Disposition:** DISMISSED. It is fixed-beta and reconstruction-dependent;
   Hamiltonian, beta-independent, ground and central-decomposition gates remain.

## 13. Exact boundary

This certificate does not prove graph-Lipschitz stability of the exact onsite
flow, graph-topology Trotter convergence, the projected Duhamel or structured
modular-multiplier estimate, a phase- and beta-independent common C-star alpha,
common-alpha KMS identification, algebraic ground states, a broken-sector GNS
or physical mass gap, regulator removal, continuum, physical empty space, a
below-empty sign, functional selection, C6, CP1, Sector A or Pre-A.
