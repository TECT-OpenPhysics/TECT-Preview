# R-167 v2.9 proof certificate: selected full oscillator, maximal continuous cores, and exhaustion boundaries

**Date:** 2026-08-13  
**Task:** T-054  
**Exploration:** EXP-000833, continuing EXP-000831  
**Tier:** T0; `claim_bearing:false`  
**Checkpoint:** proof-first only; no v2.9 PDF is issued

## 1. Exact scope

This certificate adds four narrowly scoped children to R-167 and registers
three implication failures. It does not close any of the five active parent
gates. In particular it proves neither the zero-source two-phase full
oscillator theorem nor the all-shape thermodynamic common alpha.

The first child bypasses a Ritz cutoff by applying a theorem that explicitly
allows infinite-dimensional onsite Hilbert spaces. The price is a fixed
bounded spectral-doublet selector. The remaining children identify maximal
continuous-element algebras for exact finite Hamiltonians, their categorical
product, and the already reconstructed fixed-beta OS-mixture system.

## 2. The full-oscillator selector reference

Work along the registered zero-source periodic corridor. Let

\[
 P_N=|\phi_{0,N}\rangle\langle\phi_{0,N}|
      +|\phi_{1,N}\rangle\langle\phi_{1,N}|,
 \qquad
 s_N=|\phi_{0,N}\rangle\langle\phi_{1,N}|+
     |\phi_{1,N}\rangle\langle\phi_{0,N}|,
\]

and define

\[
 \Omega_N^\pm={\phi_{0,N}\pm\phi_{1,N}\over\sqrt2},
 \qquad p_N^-={P_N-s_N\over2}=|\Omega_N^-\rangle\langle\Omega_N^-|.
\]

The selector (u\sum_xp^-_{x,N}), (0<u\le1), is bounded and translation
invariant. It is a spectral-doublet selector, not the physical linear source.
For a positive cubic edge (e=(x,x+e_i)), set

\[
 h^u_{e,N}={k_{x,N}+k_{y,N}\over6}
 +J_N(1-s_{x,N}s_{y,N})
 +{u\over6}(p^-_{x,N}+p^-_{y,N}).                 \tag{2.1}
\]

Group the three positive edges at (x):

\[
 h^u_{x,N}=\sum_{i=1}^3h^u_{(x,x+e_i),N},
 \qquad \Lambda_* =\{0,e_1,e_2,e_3\}.             \tag{2.2}
\]

Every onsite factor has the orthogonal partition

\[
 \{p_N^+,p_N^-,\text{spectral projections in }1-P_N\}.
\]

The operators (k_N,s_N,p_N^-) are functions of this partition, so (2.2) is
classical in the sense required below. Its only zero vector is
((\Omega_N^+)^{\otimes4}). Direct classification of the center label and
the three neighbour labels gives the exact star gap

\[
 g_{*,N}(u)=\min\left\{u,\;2J_N+{u\over6},\;
                     {\Gamma_N\over6}+J_N\right\}. \tag{2.3}
\]

The all-minus star realizes the first branch. Hence, once (J_N\ge1) and
(Gamma_N) is large, (2.3) equals (u) for (0<u\le1).

Let (V_{e,N}) be the exact physical-edge form minus the selector-free
reference edge from R-167 v1.9, and put
(phi_{x,N}=\sum_{i=1}^3V_{(x,x+e_i),N}). The global identity is exact up
to the already declared scalar:

\[
 \sum_x(h^u_{x,N}+\phi_{x,N})
 =H_N+u\sum_xp^-_{x,N}.                            \tag{2.4}
\]

## 3. Relative-form input and Yarotsky transfer

The v1.9 edge estimate is

\[
 |V_{e,N}(\psi,\psi)|
 \le\alpha_N h^0_{e,N}(\psi,\psi)+\beta_N\|\psi\|^2,
 \qquad
 \alpha_N=O(N^{-2}),\quad\beta_N=O(N^{-3}).        \tag{3.1}
\]

Adding three inequalities and using (h^0_{x,N}\le h^u_{x,N}) gives

\[
 |\phi_{x,N}(\psi,\psi)|
 \le\alpha_Nh^u_{x,N}(\psi,\psi)+3\beta_N\|\psi\|^2. \tag{3.2}
\]

Normalize the star by its exact gap (u). The two dimensionless inputs are `alpha_N` and `3beta_N/u`:

\[
 \widehat\alpha_N=\alpha_N,
 \qquad \widehat\beta_N={3\beta_N\over u}.          \tag{3.3}
\]

The primary source is D. A. Yarotsky, *Ground states in relatively bounded
quantum perturbations of classical lattice systems*, Commun. Math. Phys. 261
(2006), 799--819, DOI `10.1007/s00220-005-1456-9`,
arXiv `math-ph/0412040`. Its setup explicitly permits possibly infinite-dimensional onsite Hilbert spaces and unbounded classical local terms. Equation (1)
requires a unique product ground vector and local gap one; equation (2) is
exactly a quadratic-form estimate of the form (3.2). Theorem 1 supplies
admissible positive constants depending only on dimension and the fixed
interaction support.

Let those constants for dimension three and (Lambda_*) be (a_Y,b_Y>0).
Choose witnesses (C_\alpha,C_\beta,N_1) such that for (N\ge N_1),

\[
 \alpha_N\le C_\alpha N^{-2},\quad
 \beta_N\le C_\beta N^{-3},\quad J_N\ge1.           \tag{3.4}
\]

Then

\[
 N_*(u)=\max\left\{N_1,
 \left\lceil\sqrt{C_\alpha/a_Y}\right\rceil,
 \left\lceil(3C_\beta/(ub_Y))^{1/3}\right\rceil\right\} \tag{3.5}
\]

is sufficient. For every (N\ge N_*(u)), Theorem 1 gives for the exact
selected full-oscillator Hamiltonian:

1. a nondegenerate finite-volume ground vector and a positive gap independent
   of periodic spatial volume;
2. a thermodynamic weak-star limit of these ground states;
3. exponential clustering of bounded local observables; and
4. weak-star analyticity only for parameters whose local forms or resolvents
   are analytic while the same admissibility bounds remain valid.

The published theorem does not state an explicit numerical (a_Y,b_Y),
onset, or gap. We therefore make no numerical large-(N) certification and do
not identify its weak-star state with a ground state of a common Q3 dynamics.
The parity transform gives the opposite selector statement.

If (u=u_N>0) and (\beta_N/u_N\to0), the same argument is eventually
admissible. Thus (u_N=N^{-q}), (0\le q<3), is allowed, but the reference
gap then tends to zero and no (N)-uniform gap or zero-source limit follows.

## 4. Exact selector oracle

Use the three onsite labels (+,-,h) with

\[
 (k,s,p^-)_+=(0,1,0),\quad
 (k,s,p^-)_-=(0,-1,1),\quad
 (k,s,p^-)_h=(100,0,0),
\]

and (J=8,u=1,z=6). Formula (2.1) gives

\[
 e_{++}=0,\quad e_{--}={1\over3},\quad
 e_{+-}={97\over6},\quad e_{+h}={74\over3}.         \tag{4.1}
\]

Enumeration of all (3^4=81) star labels yields one zero and exact next
energy one. Synthetic form inputs (alpha=1/100,\beta=1/1000) give
(3\beta/u=3/1000). This checks the algebra and factors, not the existential
Yarotsky radius for an actual finite (N).

## 5. Why selector add--subtract does not prove zero source

If the selector is inserted in the reference and subtracted in the
perturbation to recover (H_N), the all-minus star has

\[
 \langle h^u_{x,N}\rangle=u,
 \qquad \langle\phi^{\rm counter}_{x,N}\rangle=-u. \tag{5.1}
\]

The normalized relative ratio is exactly one for all (N,u), not a vanishing
large-(N) parameter. At fixed (N), (3\beta_N/u) also diverges as
(u\downarrow0). This proves the scoped negative
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-SELECTOR-ADD-SUBTRACT-AUTOMATIC-ZERO-SOURCE-TRANSFER`.
It is not a no-go for a genuine two-phase theorem.

A second quantifier obstruction is independent. Put
(\theta_N=N^{-3}) and (r_N=N^{-4}). Both are positive and tend to zero,
but (\theta_N>r_N) for every (N\ge2). Thus vanishing defects and a
separately existential positive theorem radius for each (N) do not imply
eventual entry. This proves
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-DEFECT-AUTOMATIC-N-DEPENDENT-TWO-PHASE-RADIUS-ENTRY`.
A common lower radius or quantitative comparison is still needed.

## 6. The finite full-Hamiltonian continuous part

For one exact finite Q3 Hamiltonian (H_\Lambda), set

\[
 \alpha_t^\Lambda=\operatorname{Ad}e^{itH_\Lambda/\hbar},\qquad
 \mathfrak C(H_\Lambda)=
 \{A:\|\alpha_t^\Lambda(A)-A\|\to0\}.              \tag{6.1}
\]

Strong continuity of the implementing group makes the action continuous on
(B(\mathcal H_\Lambda)=M(K(\mathcal H_\Lambda))) in bounded strict, or
bounded strong-star, topology. Standard continuous-vector arguments give:

- (mathfrak C(H_\Lambda)) is the maximal invariant unital C-star
  subalgebra carrying the point-norm C0 action;
- (K(\mathcal H_\Lambda)\subset\mathfrak C(H_\Lambda));
- for bounded \(B\) and \(f\in L^1(\mathbb R)\), the integral in (6.2) is taken in bounded-strict, equivalently bounded-strong-star, topology;
  
  \[
  B_f=\int f(s)\alpha_s(B)\,ds,\qquad
  \|\alpha_t(B_f)-B_f\|\le\|B\|\|f(\cdot-t)-f\|_1; \tag{6.2}
  \]

- (f\in C_c^\infty) implies (delta(B_f)=-B_{f'}), and these smears form
  a norm-generator core.

For every \(s>0\), with \(K_\Lambda=1+H_\Lambda-E_{0,\Lambda}\), compact resolvent makes
(K_\Lambda^{-s}) compact. Hence the full action is isometric C0 in

\[
 q_s(A)=\|AK_\Lambda^{-s}\|+\|K_\Lambda^{-s}A\|.    \tag{6.3}
\]

The finite Gibbs state restricts to a beta-KMS state on (6.1). R-167 v2.8
then gives the sharp intersection

\[
 \mathfrak C(H_\Lambda)\cap
 \{M_f:f\in C_b(\mathbb R^{8|\Lambda|})\}=\mathbb C1. \tag{6.4}
\]

## 7. The categorical all-finite-shape envelope

Let

\[
 \mathfrak M=\prod_\Lambda B(\mathcal H_\Lambda),\qquad
 \widehat\alpha_t((A_\Lambda))=(\alpha_t^\Lambda(A_\Lambda)),
\]

and define

\[
 \mathfrak C_u=\{A\in\mathfrak M:
 \sup_\Lambda\|\alpha_t^\Lambda(A_\Lambda)-A_\Lambda\|\to0\}. \tag{7.1}
\]

It is the maximal invariant unital C-star algebra carrying the diagonal
point-norm C0 action and the norm closure of temporal smears using the same L1 kernel in every coordinate. Coordinate evaluation is a surjective equivariant quotient onto
(mathfrak C(H_\Lambda)): place any target element in one coordinate and
zero elsewhere. Smooth generators intertwine. The universal L1 orbit-smear
carrier from R-167 v1.6 embeds equivariantly.

At fixed beta, every finite Gibbs evaluation state on (7.1) is beta-KMS.
Weak-star cluster points remain KMS because the KMS identity first passes on
the common entire analytic smear core and then by norm density.

This construction is categorical. It has no spatial net or relation that
identifies one local seed across different shapes.

## 8. The fixed-beta OS-mixture continuous part

Let ((\mathfrak M_\beta,\alpha^\beta,\psi_+,\psi_-)) be the canonical
fixed-beta mixture W-star system already proved in R-167 v1.4, and set

\[
 \mathfrak A_{\beta,c}=
 \{X\in\mathfrak M_\beta:\|\alpha_t^\beta(X)-X\|\to0\}. \tag{8.1}
\]

This is the weak-star dense maximal invariant norm-C0 C-star subalgebra.
Weak-star density follows because temporal approximate identities converge
strong-star, hence weak-star, on the W-star algebra. Smooth smears form a
generator core. The restrictions of (psi_\pm) are beta-KMS and remain
distinct. If any bounded order witness \(B\) separates them and
(int f=1), then

\[
 \psi_\pm(B_f)=\int f(t)\psi_\pm(\alpha_t(B))dt=\psi_\pm(B). \tag{8.2}
\]

This is fixed-beta and phase-pair derived. The missing map is an
exhaustion-independent Hamiltonian-to-OS homomorphism.

## 9. Categorical continuity does not imply exhaustion convergence

On (M_2\), take

\[
 H_{2m}=0,\qquad H_{2m+1}=D=\operatorname{diag}(0,1),
 \qquad A_n=\sigma_x.                               \tag{9.1}
\]

The generators are uniformly bounded, so (A=(A_n)\in\mathfrak C_u).
At (t=\pi/2), the images alternate between (sigma_x) and (sigma_y),
whose difference has norm (sqrt2). At beta (=\log2), (P=E_{22}) has
Gibbs expectations

\[
 \omega_{2m}(P)={1\over2},\qquad
 \omega_{2m+1}(P)={1\over3}.                        \tag{9.2}
\]

For the odd system,

\[
 \omega(E_{12}\alpha_{i\beta}(E_{21}))={1\over3}
 =\omega(E_{21}E_{12}).                             \tag{9.3}
\]

Thus a categorical common C0 envelope and KMS compactness imply neither
all-shape Cauchy convergence nor a unique KMS quotient. This proves
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT`.
It is not a Q3 nonexistence theorem.

## 10. Devil's-advocate audit

1. **Objection: the full oscillator is still cut off.** DISMISSED for the
   selected theorem: Yarotsky explicitly permits possibly infinite-dimensional onsite
   spaces. VALID boundary: the selector is artificial and cannot be removed by
   the same argument.
2. **Objection: the finite-volume gap is already a broken-sector GNS gap.**
   UPHELD. The source theorem gives a volume-uniform finite-volume gap and a
   weak-star state, but the repository has not identified the corresponding
   common Q3 dynamics and GNS Hamiltonian core. The GNS parent stays OPEN.
3. **Objection: a maximal common product algebra closes common alpha.**
   UPHELD. It is a categorical product without spatial identifications. The
   exact alternating fixture defeats all-shape Cauchy and unique KMS selection.
4. **Objection: the fixed-beta OS continuous part supplies the missing map.**
   UPHELD. It supplies a target core, not the Hamiltonian exhaustion map into
   that core.
5. **Objection: vanishing defect automatically beats any positive radius.**
   DISMISSED by (\theta_N=N^{-3},r_N=N^{-4}).

## 11. Status and next exact lemma

The four scoped gates listed in the manifest are CLOSED at T0. The three
negative authorities reject only their named automatic implications. All five active parent gates remain OPEN. The next load-bearing lemmas are:

1. a common lower two-phase QPS radius in the exact norm containing every
   generated oscillator residual, or an equivalent zero-source theorem;
2. a two-sign all-shape Cauchy estimate for identified spatial seed images in
   one common locally normal representation; and
3. a core theorem passing a selected full-oscillator finite-volume gap to the
   corresponding common-dynamics GNS Hamiltonian.

No v2.9 PDF is issued. There is no Round-1, C6, CP1, physical Sector A, or
Pre-A closure.
