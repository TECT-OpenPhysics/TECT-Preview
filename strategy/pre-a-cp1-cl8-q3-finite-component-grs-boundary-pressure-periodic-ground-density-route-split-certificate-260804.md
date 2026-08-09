# Pre-A CP1/CL8 Q3 finite-component GRS boundary and periodic density theorem

Date: 2026-08-04  
Candidate: `PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0`  
Result: `PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-HALF-PERIODIC-PRESSURE-PERIODIC-GROUND-AND-SPECIFIC-KL-DENSITY`  
Exploration: `EXP-000778`
Authority: claim-nonbearing T0 analytic theorem

## 1. Scoped theorem

Fix

\[
 m_0>0,\qquad g>0,\qquad \lambda\geq0,               \tag{1.1}
\]

one real symmetric eight-by-eight matrix `K_pl`, and the plane-Wick
interaction

\[
 u(x)=:\!\left({1\over2}\Phi(x)^TK_{\rm pl}\Phi(x)
                  +W_4(\Phi(x))\right)\!:\_{\rm pl}, \tag{1.2}
\]

where

\[
 W_4(q)={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{e\sim f}
 (q_e-q_f)^2(q_e^2+q_f^2).                            \tag{1.3}
\]

The parent theorem `EXP-000777` proves that the spatially sharp line
Hamiltonians have

\[
 \alpha(\ell)=-{E_\ell^\sharp\over\ell}
 \nearrow\alpha_\infty,\qquad 0<\alpha_\infty<\infty. \tag{1.4}
\]

For a rectangle with side lengths `s,t`, let `p_(s,t)^(X;Y)` denote the
normalized logarithmic partition function with Gaussian boundary covariance
`X` and Wick convention `Y`, where

\[
 X,Y\in\{F,D,N,P\}.                                    \tag{1.5}
\]

Here `F` is the full-plane covariance restricted to the rectangle, and `P`
is periodic.  Thus `(X;Y)=(P;F)` is precisely a periodic Gaussian field with
the fixed plane-Wick interaction (1.2), traditionally called the
half-periodic pressure; below write `p_A^HP:=p_A^(P;F)` when the reused GRS
pair notation could be ambiguous.

For the volume-coherent Q3 family declared in `EXP-000775`, the following
statements hold.

1. The finite-component Gaussian conditioning, Q3 subdominant-coupling, and
   boundary-bracketing arguments below extend the pressure part of the
   Guerra--Rosen--Simon boundary theorem to (1.2):

\[
 \boxed{\lim_{s,t\to\infty}p_{s,t}^{X;Y}=\alpha_\infty}
 \quad\hbox{for all }X,Y\in\{F,D,N,P\},               \tag{1.6}
\]

   where both sides tend to infinity independently.
2. Let `E_s^(per,u)` be the transfer ground energy on the circle of
   circumference `s` for the scalar-removed plane-Wick action (1.2).  Fixed
   circumference Feynman--Kac transfer and (1.6) give

\[
 \boxed{\lim_{s\to\infty}-{E_s^{\rm per,u}\over s}
 =\alpha_\infty.}                                      \tag{1.7}
\]

3. With the exact `EXP-000775` Wick scalar ledger, the periodic centered
   ground and specific relative-entropy densities satisfy

\[
 \boxed{\lim_{s\to\infty}-{E_0(\widehat H_s)\over s}
 =\lim_{s\to\infty}{T_s-E_s\over s}
 =\alpha_\infty>0.}                                    \tag{1.8}
\]

4. If

\[
 d(\beta,L)={D(\mu_{\beta,L}\Vert\nu_{\beta,L})
                  \over\beta L},                       \tag{1.9}
\]

   then the joint rectangular limit and both iterated scalar limits close:

\[
 \boxed{
 \lim_{\substack{\beta,L\to\infty\\\rm independently}}d(\beta,L)
 =\lim_{\beta\to\infty}\lim_{L\to\infty}d(\beta,L)
 =\lim_{L\to\infty}\lim_{\beta\to\infty}d(\beta,L)
 =\alpha_\infty>0.}                                    \tag{1.10}
\]

Equations (1.6)--(1.10) are scalar pressure, energy, and relative-entropy
density statements.  They do not prove convergence of states, ground
vectors, gaps, or correlators.  They compare with one named massive Gaussian
reference and do not identify it with physical empty space or fix absolute
gravitational vacuum energy.

## 2. Exact historical boundary and what is new here

Guerra, Rosen, and Simon prove for one real scalar and any semibounded
one-variable polynomial that the full and half `F,D,N,P` pressures have one
thermodynamic limit.  Their Theorem VIII.2 covers all sixteen `(X;Y)` choices,
where `X` labels the Gaussian covariance and `Y` labels the Wick reference,
on rectangles whose two sides independently tend to infinity.  The diagonal
`(X;X)` objects are full pressures, while `Y=F` gives the Half-`X` pressures.
Section VI also uses a different ordered pair, here written `(X|Y)`, for
boundary conditions in the spatial and transfer directions.  Its mixed
`(P|F)` full pressure is not the Section VIII Half-`P` notation.  The
separate Half-`P` trace formula in Theorem VI.7 supplies the Hamiltonian
transfer identity used below.

That source does not state an arbitrary multivariate theorem.  In particular,
pointwise semiboundedness of a multivariate polynomial is not by itself a
valid Wick-normalizability hypothesis.  The present result is therefore not
a verbatim citation and not a world-first claim.  It is the explicit
finite-eight-component port for the special Q3 polynomial, whose additional
radial coercivity is

\[
 W_4(q)\geq c_4|q|^4,\qquad c_4={g\over32}>0.          \tag{2.1}
\]

No Griffiths, GKS, GHS, or scalar field-order inequality enters the pressure
proof.  Those correlation tools occur later in the historical paper and are
not imported here.

## 3. Vector Gaussian conditioning and multivariate Wick identity

For a scalar covariance `C`, the eight-component covariance is

\[
 \mathbf C=C\otimes I_8.                               \tag{3.1}
\]

Every scalar quadratic-form order lifts:

\[
 C_1\leq C_2\quad\Longrightarrow\quad
 C_1\otimes I_8\leq C_2\otimes I_8.                   \tag{3.2}
\]

At a common ultraviolet cutoff, multivariate Wick ordering at coincident
variance `c` is the finite polynomial operator

\[
 :P(q):_c=\exp\!\left(-{c\over2}\Delta_8\right)P(q),
 \qquad \Delta_8=\sum_{e=1}^8\partial_{q_e}^2.         \tag{3.3}
\]

If `Phi=Phi_1+Phi_2` is an independent Gaussian sum with covariances
`C=C_1+C_2`, the heat-semigroup composition law gives

\[
 \mathbb E_{\Phi_2}
 \left[:P(\Phi_1+\Phi_2):_C\mid\Phi_1\right]
 =:P(\Phi_1):_{C_1}.                                  \tag{3.4}
\]

Applying conditional Jensen to the exponential of the integrated
interaction gives the GRS conditioning comparison for every multivariate
polynomial for which the Wick exponential exists.  The covariance lattice
for `F,D,N,P`, direct-sum decompositions across adjacent rectangles, and
Dirichlet/Neumann brackets are scalar operator statements tensored with
`I_8`.  Hence their partition inequalities and sub- or supermultiplicative
directions are unchanged.

The continuum identity follows from the common-cutoff identity by the Q3
uniform integrability established below.  This is a proof port for a coupled
polynomial, not a factorization of the interacting partition function into
eight scalar partition functions.

## 4. Q3 uniform subdominant-coupling theorem

This section supplies the only part of the historical pressure proof that is
not automatic from Gaussian tensoring.

Let `A` be a rectangle, `R` a subrectangle with both sides at least one, and
`X` one of `F,D,N,P`.  At a common ultraviolet cutoff `N`, perturb the fixed
Q3 interaction by a measurable symmetric matrix `B(x)` and scalar `b(x)` on
`R`:

\[
 H_{B,b}= {1\over2}\int_R:\!\Phi^TB\Phi\!:_X dx
          +\int_R b(x)dx.                              \tag{4.1}
\]

For every fixed normalized ball

\[
 \|(B,b)\|_{A,R}
 :=\left({1\over|A|}\int_R\|B(x)\|_{\rm HS}^2dx\right)^{1/2}
  +{1\over|A|}\int_R|b(x)|dx\leq\rho,                \tag{4.2}
\]

there is a constant `C_rho`, depending on the fixed Q3 parameters and eight
components but not on `N,A,R,X`, such that the normalized logarithmic
partition functional obeys the two-sided bound

\[
 \sup_{N,A,R,X,\ \|(B,b)\|_{A,R}\leq\rho}
 |p_{N,A}^X(B,b)|\leq C_\rho.                         \tag{4.2a}
\]

The upper estimate is the finite-component port of GRS Theorem VII.10.  The
matching-`X` Wick monomials have Gaussian mean zero, so Jensen supplies the
corresponding lower estimate.  Thus the bounded convex functional required
by GRS Theorem VIII.1 is uniform in ultraviolet cutoff, rectangle, and the
four classical boundary conditions.

The proof is the scalar GRS proof with the following complete substitutions.

### 4.1 Coercive multi-index replacement

For every multi-index of degree `r<4`, generalized Young gives

\[
 |a q^\gamma|
 \leq\varepsilon|q|^4
 +C_r\varepsilon^{-r/(4-r)}|a|^{4/(4-r)}.             \tag{4.3}
\]

For the only random lower term required by Q3 boundary reordering,

\[
 {1\over2}|q^TBq|
 \leq\theta W_4(q)+{\|B\|_{\rm op}^2\over16\theta c_4}.
                                                               \tag{4.4}
\]

Thus scalar degree `r` coefficient exponent `4/(4-r)` becomes the same
finite multi-index exponent; in particular it is `2` for the matrix
quadratic and `1` for the scalar.

### 4.2 Wick and hypercontractive replacement

For Q3,

\[
 \Delta_8W_4(q)=3q^TA_{Q3}q,\qquad
 \Delta_8^2W_4=48(g+4\lambda).                        \tag{4.5}
\]

Undoing the cutoff Wick ordering therefore produces only finitely many
component-labelled chaoses of degree at most four.  On the product Gaussian
space, every homogeneous chaos obeys

\[
 \|F_r\|_{L^p}\leq(p-1)^{r/2}\|F_r\|_{L^2},
 \qquad p\geq2.                                       \tag{4.6}
\]

The scalar cutoff-difference kernel estimates apply to each component; the
finite multi-index sum changes only the constant.  Equations (2.1), (4.3),
and (4.6) reproduce the cutoff-uniform local estimates corresponding to GRS
Lemmas VII.11--VII.13.

### 4.3 Localization and Duhamel summation

The three reductions in GRS Theorem VII.10 are dimension-blind:

1. conditioning and `C_X tensor I_8 <= c C_F tensor I_8` reduce all four
   boundary conditions to the free estimate;
2. Feynman--Kac locality reduces measurable coefficient fields to the
   constant-coupling pressure majorant; and
3. the Nelson/Glimm--Jaffe linear-volume bound recovers the correct volume
   dependence from a fixed unit block.

The remaining Duhamel expansion is a sum of cutoff-chaos norms.  In the GRS
proof, apply (VII.22) to each component-labelled cutoff polynomial, replace
the scalar coercive estimate (VII.25) by (4.3)--(4.4), and apply the product
Gaussian version of (VII.28) to every multi-index chaos.  Iterating the exact
Duhamel identity (VII.29), the estimates leading to (VII.30) and (VII.31)
then have the same ordered-increment powers and factorial majorant.  The
single scalar monomial label is replaced by the finite set
`(gamma,e_1,...,e_r)`.  Its cardinality depends only on the fixed component
count eight and degree four, never on cutoff or volume, so summing the labels
only enlarges `C_rho`.  The majorant is cutoff-uniform and permits the common-
cutoff limit.  This proves (4.2a) rather than assuming a scalar theorem for a
coupled vector polynomial.

## 5. Boundary Wick differences vanish in the coupling norm

Let

\[
 \delta_{X,Y,A}(x)=C_A^X(x,x)-C_A^Y(x,x).             \tag{5.1}
\]

The exact Q3 heat formula (3.3) gives, with the sign fixed by (5.1),

\[
 :P_K:_Y
 =:P_{K+3\delta_{X,Y,A}A_{Q3}}:_X
  +{\delta_{X,Y,A}\over2}\operatorname{Tr}K
  +6\delta_{X,Y,A}^2(g+4\lambda).                    \tag{5.1a}
\]

Thus changing the Wick convention leaves the quartic part fixed and
introduces only

\[
 B_{X,Y,A}(x)=3\delta_{X,Y,A}(x)A_{Q3},               \tag{5.2}
\]

\[
 b_{X,Y,A}(x)={\delta_{X,Y,A}(x)\over2}
                 \operatorname{Tr}K_{\rm pl}
              +6\delta_{X,Y,A}(x)^2(g+4\lambda),     \tag{5.3}
\]

Exchanging `X,Y` reverses the terms linear in `delta` but not the squared
term; there is no suppressed sign convention in (5.1a)--(5.3).

The massive method-of-images estimates used by GRS imply

\[
 {1\over|A|}\int_A
 \left(|\delta_{X,Y,A}|+|\delta_{X,Y,A}|^2\right)dx
 \longrightarrow0                                    \tag{5.4}
\]

as the shorter side tends to infinity.  Comparisons involving Dirichlet or
Neumann covariance contain boundary-layer terms.  The pure periodic-to-free
image correction is exponentially small in the shorter side.  Tensoring adds
only the fixed factor eight.

The normalized log partition is convex in `(B,b)`.  The elementary convex
Lipschitz lemma on a bounded ball, combined with Section 4 and (5.4), gives

\[
 |p_A^{X;Y}-p_A^{X;X}|\longrightarrow0.               \tag{5.5}
\]

The diagonal full-boundary pressures are bracketed by the Dirichlet and
Neumann pressures through Section 3.  The GRS not-feeling-the-boundary proof
uses only the same covariance image bounds, Holder/Schwarz inequalities, the
linear-volume estimate, and local Gaussian Radon--Nikodym bounds.  Each
operator is tensored with `I_8`, and Section 4 supplies the Q3 interaction
bound.  Hence all diagonal pressures converge to the free value
`alpha_infinity`; (5.5) proves (1.6) for all sixteen generalized
covariance/Wick choices.  The four diagonal objects are the full pressures.
The four objects with `Y=F` are the Half-`X` family and overlap the diagonal
family at `(F;F)`; equivalently, the twelve off-diagonal choices consist of
three nontrivial Half-`X` objects and nine other mismatches.

## 6. Half-periodic transfer and the diagonal argument

The object needed by TECT is `(X;Y)=(P;F)`, not merely the diagonal `(P;P)`
Hamiltonian displayed in the scalar source.  Here the Section VIII symbols
mean periodic Gaussian covariance and free/plane Wick ordering.  They must
not be confused with the Section VI mixed-strip notation, where `P,F` labels
periodic spatial and free transfer-direction boundary conditions.  For the
finite torus object, GRS Theorem VI.7 gives the normalized Feynman--Kac trace
identity

\[
 \exp(stp_{s,t}^{P;F})
 = {\operatorname{Tr}\exp(-tH_s^{\rm per,u})
    \over \operatorname{Tr}\exp(-tH_{0,s})}.          \tag{6.0}
\]

The free Hamiltonian is vacuum normalized, `E_0(H_(0,s))=0`.  Compact
resolvent and the fixed-`s` trace spectral decomposition therefore give

\[
 \lim_{t\to\infty}p_{s,t}^{P;F}
 =-{E_s^{\rm per,u}\over s}.                          \tag{6.1}
\]

No ground-projection estimate uniform in `s` is required.  Given an arbitrary
sequence `s_n->infinity`, the fixed-`s_n` limit permits a choice `t_n>=n`
such that

\[
 \left|p_{s_n,t_n}^{P;F}
       +{E_{s_n}^{\rm per,u}\over s_n}\right|<{1\over n}. \tag{6.1a}
\]

Since both `s_n,t_n` tend independently to infinity, (1.6) gives

\[
 -{E_{s_n}^{\rm per,u}\over s_n}\longrightarrow
 \alpha_\infty.                                       \tag{6.2}
\]

This holds for every sequence and proves (1.7).

## 7. Exact periodic scalar and specific-KL ledger

Let

\[
 a_s={1\over\pi}\sum_{n\geq1}K_0(m_0ns),\qquad
 c_s={a_s\over2}\operatorname{Tr}K_{\rm pl}
       +6a_s^2(g+4\lambda).                           \tag{7.1}
\]

Mass positivity gives `c_s->0`.  The exact `EXP-000775` Wick dictionary is

\[
 E_0(\widehat H_s)=E_s^{\rm per,u}-s c_s.             \tag{7.2}
\]

Equations (1.7) and (7.2), together with the fixed-circumference entropy
identity, prove (1.8).

On a periodic rectangle define

\[
 c_{\beta,L}={D_{\beta,L}^{\rm pl}\over2}
                 \operatorname{Tr}K_{\rm pl}
 +6(D_{\beta,L}^{\rm pl})^2(g+4\lambda).             \tag{7.3}
\]

The exact finite-volume relative-entropy cancellation gives

\[
 d(\beta,L)=p_{\beta,L}^{P;F}(u)+c_{\beta,L}.         \tag{7.4}
\]

When both sides independently tend to infinity, the massive image sum makes
`c_(beta,L)->0`; (1.6) proves the joint limit in (1.10).  `EXP-000775` gives
the first inner limit, and (1.8) gives its outer limit.  Exact exchange
symmetry `d(beta,L)=d(L,beta)` gives the other iterated limit.  Only these
scalar quantities are interchanged.

## 8. What the old surface gate now means

`EXP-000777` correctly rejected an unproved covariance-interpolation estimate
of the stronger form

\[
 |\log Z_A^{\rm per}-\log Z_A^\sharp|
 \leq C(|\partial A|+1).                              \tag{8.1}
\]

Nothing above proves (8.1).  The cutoff-, volume-, and interpolation-uniform
surface-pairing gate remains open as a quantitative theorem.  The GRS
bracketing route proves only the density consequence needed here:

\[
 {E_s^{\rm per,u}-E_s^\sharp\over s}\longrightarrow0. \tag{8.2}
\]

Thus the old gate is bypassed for scalar density limits, not silently marked
proved.  The negative result about fixed-volume uniform integrability remains
valid.

## 9. Phase and physical-reference firewall

The following do not follow from this theorem.

1. The massive Gaussian reference is fixed by `m0`, geometry, and field
   normalization.  It is not derived as cosmic empty space or a physical
   no-condensate state.
2. Adding a local scalar density shifts every raw pressure and ground-energy
   density.  An external stress-tensor renormalization or observable anchor
   is still required for absolute gravitational energy.
3. Pressure independence does not imply uniqueness of Gibbs or vacuum
   states.  It proves no phase transition, order parameter, spontaneous
   symmetry breaking, or cooling dynamics.
4. No zero-temperature state, ground vector, uniform gap, correlation, full
   KMS local algebra, or interacting microlocal-spectrum limit is proved.
5. This remains an inserted `1+1`-dimensional Q3 comparator.  It is not the
   original fixed-raw CL8 regulator or a derived three-dimensional Q3LOCK
   parent.
6. Physical light, C0, N1--N5, C6, CP1, Sector A, and Pre-A remain open.

## 10. Adversarial review

1. **The scalar GRS theorem can be cited verbatim for Q3. UPHELD AS FALSE.**
   Sections 3--5 explicitly port Gaussian conditioning, the subdominant
   coupling theorem, and boundary Wick control to the radially coercive
   finite-component polynomial.
2. **A coupled Q3 partition function factors into eight scalar models.
   UPHELD AS FALSE.**  Only the free covariance and hypercontractive estimate
   tensor; the Q3 interaction remains coupled.
3. **Pointwise semiboundedness is enough in several components. UPHELD AS
   FALSE.**  The proof uses the stronger radial estimate (2.1); `g=0` is
   outside the theorem.
4. **The GRS pressure proof secretly needs scalar correlation order.
   DISMISSED.**  The load-bearing sections use conditioning, covariance
   images, convexity, localization, hypercontractivity, and Duhamel bounds.
   Scalar correlation inequalities begin later and are not used here.
5. **Deterministic Young alone controls the ultraviolet limit. UPHELD AS
   FALSE.**  Young supplies coercive absorption; the cutoff-uniform statement
   also needs the chaos estimates and Duhamel majorant in Sections 4.2--4.3.
6. **The diagonal periodic Hamiltonian in GRS is automatically the TECT
   half-periodic Hamiltonian. UPHELD AS FALSE.**  Section 6 uses the all-sixteen
   pressure theorem and a separate fixed-`s` transfer identity for `(P,F)`.
7. **A uniform ground-projection rate in `s` was assumed. DISMISSED.**  The
   sequence-dependent diagonal choice in Section 6 needs only fixed-`s`
   spectral convergence.
8. **This proves the stronger surface estimate (8.1). UPHELD AS FALSE.**
   Only the density equality (8.2) closes.
9. **Pressure independence proves phase uniqueness. UPHELD AS FALSE.**
   Boundary pressures may agree while states coexist.
10. **Positive specific KL means energy below physical empty space. UPHELD AS
    FALSE.**  It is an invariant comparison with one named Gaussian law, not
    a physical reference selection.
11. **This closes Pre-A. UPHELD AS FALSE.**  Physical reference, phase/state,
    original-parent, causal-emergence, and C0/N1--N5 gates remain open.

## 11. Prior-art sources

- F. Guerra, L. Rosen, and B. Simon, *Nelson's Symmetry and the Infinite
  Volume Behavior of the Vacuum in P(phi)2*, Communications in Mathematical
  Physics 27 (1972), DOI `10.1007/BF01649655`.
- F. Guerra, L. Rosen, and B. Simon, *The Vacuum Energy for P(phi)2: Infinite
  Volume Limit and Coupling Constant Dependence*, Communications in
  Mathematical Physics 29 (1973), DOI `10.1007/BF01645249`.
- F. Guerra, L. Rosen, and B. Simon, *The Pressure is Independent of the
  Boundary Conditions for P(phi)2 Field Theories*, Bulletin of the American
  Mathematical Society 80 (1974), DOI
  `10.1090/S0002-9904-1974-13680-3`.
- F. Guerra, L. Rosen, and B. Simon, *Boundary Conditions for the P(phi)2
  Euclidean Field Theory*, Annales de l'Institut Henri Poincare A 25 (1976),
  231--334, `https://numdam.org/item/AIHPA_1976__25_3_231_0/`.
- H. Nagoji, *Construction of Gibbs measures associated with Euclidean
  quantum field theory with various polynomial interactions in the Wick
  renormalizable regime*, arXiv:2305.19583.

The sources prove the scalar mechanisms and expose the multivariate
normalizability boundary.  The finite-Q3 port in Sections 3--5 is recorded
locally.  No source located in the bounded audit proves the full TECT Pre-A
chain, and this statement is not a novelty or world-first claim.

## 12. Reproduction

Primary audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_finite_component_grs_boundary_pressure_periodic_ground_density_route_split.py --self-test
```

Independent standard-library audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_finite_component_grs_boundary_pressure_periodic_ground_density_route_split_independent.py --self-test
```

Integrated audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_finite_component_grs_boundary_pressure_periodic_ground_density_route_split_verify.py --self-test
```

The executable checks audit the finite-component Wick heat identity, Q3
coercive/Young algebra, covariance-order tensoring, boundary coefficient-norm
scaling, convex Lipschitz step, diagonal transfer logic, exact scalar ledger,
scope firewalls, source scope, and unchanged C6 authority.  They do not
replace the analytic constructive proof in Sections 3--6.
