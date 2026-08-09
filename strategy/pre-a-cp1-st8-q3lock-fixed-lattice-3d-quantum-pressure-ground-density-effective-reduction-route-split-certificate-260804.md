# Pre-A ST8/Q3LOCK fixed-lattice quantum thermodynamics and reduction split

Date: 2026-08-04  
Candidate: `PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT-v0`  
Result: `PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-FREE-PERIODIC-SOURCE-PRESSURE-AND-CENTERED-GROUND-ENERGY-DENSITY`  
Exploration: `EXP-000780`
Authority: claim-nonbearing T0 self-contained fixed-lattice analytic theorem

<a id="section-1-result-first"></a>
## 1. Result first

Fix the exact unweighted, fixed-spacing, fixed-block-origin ST8/Q3LOCK
Hamiltonian of `PA-CP1-ST8-Q3LOCK-v0`.  Let

\[
 \hbar>0,\quad \chi>0,\quad c>0,\quad g>0,\quad
 \lambda>0,\quad r\in\mathbb R,                         \tag{1.1}
\]

and add one constant energy-source `J in R^8`.  On every even coarse cube of
side `L`, with

\[
 n_L=8L^3=N^3,\qquad N=2L,                              \tag{1.2}
\]

the finite quantum Hamiltonian is lower bounded, has compact resolvent, and
has finite heat trace.  For every `beta>0`, define the dimensionless
log-partition density, thermodynamic pressure, free-energy density, and
ground-energy density by

\[
 \pi_L(\beta,J)={1\over n_L}\log\operatorname{Tr}
 e^{-\beta H_L(J)},\quad
 P_L={\pi_L\over\beta},\quad
 f_L=-{\pi_L\over\beta},\quad
 e_L={E_0(H_L(J))\over n_L}.                            \tag{1.3}
\]

The following limits exist and are finite.

1. Open rectangular `pi`, `f`, and `e` have limits as all even side lengths
   tend independently to infinity.
2. Periodic even-cube `pi`, `f`, and `e` have limits and agree with the open
   limits.
3. At every fixed positive `beta`, the limiting `pi(beta,J)` and `P(beta,J)`
   are locally uniform in `J`, convex, and invariant under the global
   transformation `J -> -J`.  The limiting `e(J)` is locally uniform,
   concave, and globally even.
4. For every compact source set and every fixed `beta_star>0`, there is a
   finite constant `C` independent of `L`, boundary condition, and
   `beta>=beta_star` such that

\[
 0\le e_L(J)-f_L(\beta,J)\le {C\over\beta}.             \tag{1.4}
\]

Consequently,

\[
 e_\infty(J)
 =\lim_{\beta\to\infty} f_\infty(\beta,J)
 =-\lim_{\beta\to\infty}{\pi_\infty(\beta,J)\over\beta},
                                                               \tag{1.5}
\]

and `f_L(beta,J)` (equivalently `-P_L`) obtains the same scalar value in
either iterated order or along every joint path with even `L -> infinity`
and `beta -> infinity`.  The unscaled `pi_L` itself generally grows linearly
in `beta` and is not claimed to converge at zero temperature.

At zero source, put

\[
 r_-:=\max(0,-r),\qquad \sigma={r_-^2\over4g}.          \tag{1.6}
\]

Then `H_hat=H+sigma*n_L` is nonnegative.  This is an exact classical
complete-square centering, not a physical-vacuum normalization.  Adding a
scalar changes `pi`, `P`, `f`, and `e` while leaving normalized finite-volume
Gibbs states unchanged.  Therefore no physical empty-space or
below-empty-space comparison follows.

The theorem is a fixed-spacing thermodynamic-volume result only.  It does
not prove a pressure cusp, phase transition, selected infinite-volume state,
uniform gap, clustering, continuum regulator removal, a `3+1` quantum field,
or a `3D -> 1+1` effective reduction.  It does not advance C6 or close CP1,
Sector A, or Pre-A.

<a id="section-2-exact-family-and-normalization"></a>
## 2. Exact family and normalization

Let `R` be an even rectangular subset of the coarse lattice.  Its coordinates
are

\[
 \psi_\epsilon(y)\in\mathbb R,qquad
 y\in R,qquad \epsilon\in\{0,1\}^3.                  \tag{2.1}
\]

The open Hamiltonian on `L2(R^(8|R|))` is the Friedrichs operator associated
with

\[
\begin{aligned}
 H_R^{\rm op}(J)={}&
 \sum_{y,\epsilon}\left[
 -{\hbar^2\over2\chi}{\partial^2\over\partial\psi_\epsilon(y)^2}
 +{r\over2}\psi_\epsilon(y)^2
 +{g\over4}\psi_\epsilon(y)^4
 -J_\epsilon\psi_\epsilon(y)
 \right]\\
 &+{c\over2}\sum_{\substack{y,y+e_i\in R\\\epsilon,i}}
 [\psi_\epsilon(y+e_i)-\psi_\epsilon(y)]^2\\
 &+{\lambda\over4}\sum_y
 \sum_{\{\epsilon,\eta\}\in E(Q_3)}
 (\psi_\epsilon(y)-\psi_\eta(y))^2
 (\psi_\epsilon(y)^2+\psi_\eta(y)^2).                \tag{2.2}
\end{aligned}
\]

There are twelve undirected Q3 edges at every coarse site.  The periodic
cube has the same expression with the spatial positive-direction bonds
wrapped modulo `L`.  The source convention in (2.2) is an energy source.
It must not be confused with a dimensionless Euclidean source `j=beta*J`.

The natural volume in the registered unweighted theorem is the number of
fine oscillators, `n_R=8|R|`.  Coarse-cell densities are exactly eight times
the densities in (1.3).  A separately declared physical spacing ledger would
divide by `|R|a^3` and use its own weighted Hamiltonian.  No such ledger is
silently mixed into this theorem.

<a id="section-3-stability-trace-and-linear-bounds"></a>
## 3. Stability, trace class, and linear volume bounds

### 3.1 Source coercivity

For one real coordinate and `j in R`, split the onsite quartic into one half
retained and two quarters used for absorption.  The exact inequalities are

\[
 {g\over16}x^4-{r_-\over2}x^2\ge-{r_-^2\over g},       \tag{3.1}
\]

and

\[
 {g\over16}x^4-|j||x|
 \ge-{3\over4}\left({4\over g}\right)^{1/3}|j|^{4/3}.
                                                               \tag{3.2}
\]

Hence

\[
 {r\over2}x^2+{g\over4}x^4-jx
 \ge {g\over8}x^4-{r_-^2\over g}
 -{3\over4}\left({4\over g}\right)^{1/3}|j|^{4/3}.   \tag{3.3}
\]

Define

\[
 Q_R={g\over8}\sum_{y,\epsilon}\psi_\epsilon(y)^4,
\quad
 K_R=\sum_{y,\epsilon}\left[-{\hbar^2\over2\chi}\partial^2
 +{g\over8}\psi_\epsilon(y)^4\right],                \tag{3.4}
\]

and

\[
 b_J={8r_-^2\over g}
 +{3\over4}\left({4\over g}\right)^{1/3}
 \sum_\epsilon |J_\epsilon|^{4/3}.                    \tag{3.5}
\]

All spatial and Q3-lock terms are nonnegative, so as quadratic forms

\[
 H_R^{\rm op}(J)\ge K_R-b_J|R|\ge Q_R-b_J|R|.         \tag{3.6}
\]

The same statement holds periodically.  At `J=0` the sharper allocation

\[
 H_R(0)\ge K_R-{4r_-^2\over g}|R|                     \tag{3.7}
\]

is available.  More importantly, the un-split onsite polynomial has the exact
bound `r*x^2/2+g*x^4/4 >= -r_-^2/(4g)`.

The closed semibounded polynomial form defines a self-adjoint operator.
Equation (3.6) compares its eigenvalues from below with a tensor product of
confining one-dimensional quartic oscillators.  It therefore has compact
resolvent and finite `Tr exp(-beta H)` for every `beta>0`.  The quartic term
must not be dropped in this trace comparison: the heat trace of a free
particle on the line is infinite.

### 3.2 Explicit product trial

Take a normalized even product Gaussian whose coordinate probability has
variance `s^2`.  For one coordinate,

\[
 \langle\psi^2\rangle=s^2,\qquad
 \langle\psi^4\rangle=3s^4,\qquad
 \left\langle-{\hbar^2\over2\chi}\partial^2\right\rangle
 ={\hbar^2\over8\chi s^2}.                            \tag{3.8}
\]

For two independent centered coordinates `X,Y`,

\[
 \mathbb E[(X-Y)^2(X^2+Y^2)]=8s^4.                   \tag{3.9}
\]

There are 24 periodic spatial bonds and twelve Q3 edges per coarse site.
The trial expectation per coarse site is therefore

\[
 A_s={\hbar^2\over\chi s^2}
 +(4r+24c)s^2+(6g+24\lambda)s^4.                     \tag{3.10}
\]

The source expectation vanishes.  Choose one `s` for which `A_s>0`.  Then,
for open or periodic boxes,

\[
 E_0(H_R(J))\le A_s|R|,qquad
 \log Z_R(\beta,J)\ge-\beta A_s|R|.                 \tag{3.11}
\]

Let

\[
 z_q(\beta)=\operatorname{Tr}\exp\left[-\beta
 \left(-{\hbar^2\over2\chi}\partial^2+{g\over8}x^4\right)
 \right]<\infty.                                     \tag{3.12}
\]

Min-max eigenvalue comparison applied to (3.6), rather than an invalid claim
that the exponential is operator monotone, gives

\[
 \log Z_R(\beta,J)
 \le \beta b_J|R|+8|R|\log z_q(\beta).               \tag{3.13}
\]

Equations (3.11)--(3.13) are uniform on compact source sets and give all
linear-volume bounds used below.

<a id="section-4-open-rectangle-thermodynamic-limits"></a>
## 4. Open-rectangle thermodynamic limits

Cut an open rectangle into two even rectangles across a coordinate plane.
The Hilbert space factors and

\[
 H_R^{\rm op}
 =H_{R_1}^{\rm op}\otimes1+1\otimes H_{R_2}^{\rm op}+B_{12},
 \qquad B_{12}\ge0,                                  \tag{4.1}
\]

where `B_12` is the sum of the crossing spatial difference squares.  The
Q3-lock interaction is onsite and creates no crossing term.

Quadratic-form order and the min-max principle imply

\[
 E_0^{\rm op}(R)\ge E_0^{\rm op}(R_1)+E_0^{\rm op}(R_2),
                                                               \tag{4.2}
\]

and, eigenvalue by eigenvalue,

\[
 Z_R^{\rm op}(\beta,J)
 \le Z_{R_1}^{\rm op}(\beta,J)Z_{R_2}^{\rm op}(\beta,J).
                                                               \tag{4.3}
\]

Thus the ground and free energies are superadditive, while `log Z` is
subadditive.  Tile an arbitrary large even rectangle by copies of any fixed
even rectangle.  Apply (4.2)--(4.3) to the full tiles and use the linear
stability and trace bounds on the even remainders.  Their relative volume
tends to zero as every side tends independently to infinity.  The elementary
multidimensional Fekete argument gives

\[
 \lim_R {E_0^{\rm op}(R,J)\over |R|}
 =\sup_R {E_0^{\rm op}(R,J)\over |R|},                \tag{4.4}
\]

and

\[
 \lim_R {\log Z_R^{\rm op}(\beta,J)\over |R|}
 =\inf_R {\log Z_R^{\rm op}(\beta,J)\over |R|}.       \tag{4.5}
\]

Division by eight gives the fine-oscillator limits used in (1.3).

<a id="section-5-periodic-open-global-form-comparison"></a>
## 5. Periodic/open global-form comparison

For an even cube, write

\[
 H_L^{\rm per}(J)=H_L^{\rm op}(J)+B_L,\qquad B_L\ge0. \tag{5.1}
\]

There are exactly `24L^2` scalar seam bonds.  For every `eta>0`,

\[
 {c\over2}(a-b)^2\le c(a^2+b^2),                     \tag{5.2}
\]

and

\[
 cx^2\le {\eta g\over24}x^4+{6c^2\over\eta g}.       \tag{5.3}
\]

Each coordinate is incident to at most three seam bonds and there are
`48L^2` endpoint occurrences.  Summing (5.2)--(5.3) gives the global form
bound

\[
 0\le B_L\le\eta Q_L+{288c^2\over\eta g}L^2.          \tag{5.4}
\]

This is the step that controls the unbounded seam.  Counting `O(L^2)` bonds
alone would not be sufficient.  From (3.6), `Q_L<=H_L^op+b_JL^3`, so

\[
 H_L^{\rm op}\le H_L^{\rm per}
 \le(1+\eta)H_L^{\rm op}
 +\eta b_JL^3+{288c^2\over\eta g}L^2                 \tag{5.5}
\]

as common-domain quadratic forms.

For the ground energy, min-max gives

\[
 0\le E_L^{\rm per}-E_L^{\rm op}
 \le\eta(E_L^{\rm op}+b_JL^3)
 +{288c^2\over\eta g}L^2.                            \tag{5.6}
\]

Use (3.11) and choose `eta=L^(-1/2)`.  After division by `n_L=8L^3`, the
right side is `O(L^(-1/2))`.

For the heat trace, apply min-max to every eigenvalue in (5.5).  With

\[
 D_L=\eta b_JL^3+{288c^2\over\eta g}L^2,              \tag{5.7}
\]

one obtains

\[
 e^{-\beta D_L}Z_L^{\rm op}(\beta(1+\eta),J)
 \le Z_L^{\rm per}(\beta,J)
 \le Z_L^{\rm op}(\beta,J).                          \tag{5.8}
\]

Let `a_L(beta,J)=L^(-3)log Z_L^op(beta,J)`.  On every compact positive
`beta` interval and compact source set, (3.11)--(3.13) bound `|a_L|`
uniformly.  Every `a_L` is convex in `beta`, because its second derivative is
the energy variance.  A uniformly bounded family of convex functions is
uniformly locally Lipschitz in the interior.  Consequently

\[
 |a_L(\beta(1+\eta),J)-a_L(\beta,J)|\le C_{\beta,J}\eta
                                                               \tag{5.9}
\]

uniformly in `L` for `eta<=1/2`.  Equations (5.7)--(5.9) with
`eta=L^(-1/2)` prove equality of the periodic and open fixed-`beta` density
limits, again at density error `O(L^(-1/2))`.

No total `O(L^2)` surface-error theorem is claimed.  The direct estimate is
the weaker but sufficient `O(L^(5/2))` total bound after optimizing `eta`.

<a id="section-6-uniform-zero-temperature-squeeze"></a>
## 6. Uniform zero-temperature squeeze

Let the finite eigenvalues be `E_0<=E_1<=...`, repeated with multiplicity.
For `beta>=beta_star>0`,

\[
\begin{aligned}
 0\le E_0-F_L(\beta)
 &= {1\over\beta}\log\sum_k e^{-\beta(E_k-E_0)}\\
 &\le {1\over\beta}\log\sum_k e^{-\beta_\star(E_k-E_0)}\\
 &= {\beta_\star E_0+\log Z_L(\beta_\star)\over\beta}.
                                                               \tag{6.1}
\end{aligned}
\]

The last numerator is nonnegative by its spectral definition.  Equations
(3.11) and (3.13) bound it by `C|R|`, uniformly for open and periodic boxes
and locally uniformly in `J`.  Dividing by `n_R=8|R|` proves (1.4).

The ground-density limit was proved independently in Sections 4--5; it is
not inferred by exchanging two unproved limits.  Now the uniform estimate
does justify the exchange and every joint scalar path.  In particular, since
`f=-pi/beta`, the exact zero-temperature formula is (1.5), not
`e=-lim pi`.

<a id="section-7-source-and-scalar-covariance"></a>
## 7. Source and scalar covariance

At finite volume, Holder's inequality makes `pi_L(beta,J)` convex in `J`.
The unitary global field inversion sends `H_L(J)` to `H_L(-J)`, hence

\[
 \pi_L(\beta,J)=\pi_L(\beta,-J),\qquad
 e_L(J)=e_L(-J).                                      \tag{7.1}
\]

This is global evenness only; componentwise sign flips are not symmetries of
the Q3 lock.  Where finite-volume differentiation is used,

\[
 {\partial\pi_L\over\partial J_\epsilon}
 ={\beta\over8L^3}
 \left\langle\sum_y\psi_\epsilon(y)\right\rangle_J.  \tag{7.2}
\]

The pointwise finite limits, convexity or concavity, and the compact-source
volume bounds imply local-uniform convergence on source compacts.  No cusp
sign or tangent state is obtained.

At `J=0`, let `sigma` be (1.6).  If `r<0`, put `v^2=-r/g`; then

\[
 H_L(0)+\sigma n_L
 =T+H_{\rm spatial}+H_{Q3}
 +{g\over4}\sum_{y,\epsilon}(\psi_\epsilon(y)^2-v^2)^2
 \ge0.                                                \tag{7.3}
\]

For `r>=0`, nonnegativity is immediate with `sigma=0`.  The exact scalar
covariance is

\[
 \widehat\pi=\pi-\beta\sigma,\qquad
 \widehat P=P-\sigma,\qquad
 \widehat f=f+\sigma,\qquad
 \widehat e=e+\sigma.                                \tag{7.4}
\]

More generally, `H -> H+d*n_L` gives the same formulas with `d`.  Normalized
Gibbs states and their correlations are unchanged.  At nonzero source,
adding `sigma*n_L` remains an allowed convention change but no longer proves
nonnegativity.  These facts explicitly prevent the mathematical center from
being relabelled as physical empty space or as a proof of energy below empty
space.

<a id="section-8-effective-reduction-remains-open"></a>
## 8. Effective reduction remains open

At one coarse cell decompose the eight species into a collective coordinate
and seven transverse coordinates:

\[
 \psi_\epsilon={Q\over\sqrt8}+r_\epsilon,qquad
 \sum_\epsilon r_\epsilon=0.                          \tag{8.1}
\]

The onsite quartic has the exact identity

\[
 \sum_\epsilon\psi_\epsilon^4
 ={Q^4\over8}+{3\over4}Q^2\|r\|^2
 +\sqrt2 Q\sum_\epsilon r_\epsilon^3
 +\sum_\epsilon r_\epsilon^4.                        \tag{8.2}
\]

Thus the natural collective/transverse tensor Hamiltonian is not additively
factorized.  The Q3 lock supplies further transverse-dependent terms.  The
finite classical diagonal submanifold remains an exact invariant
restriction, but a restriction is not a quantum marginal and the finite
ground vector is not supported on it.  The interacting two-cell marginal
obstruction of `EXP-000779` and the registered natural-low-mode
ground-projectivity no-go therefore remain in force.

Equation (8.2) does not exclude every possible reduction.  A controlled
constraint limit, decoupling theorem, mean-force Hamiltonian, dressed
embedding, or renormalization-group effective action may still exist.  Even
the collective-species restriction is a three-spatial-dimensional lattice
field, not the inserted `1+1` comparator.  The `3D -> 1+1` map remains a
separate gate.

<a id="section-9-prior-art-and-novelty-boundary"></a>
## 9. Prior-art and novelty boundary

This result is not asserted to be a world-first thermodynamic-limit theorem.
Rigorous infinite-volume quantum anharmonic-crystal frameworks already exist,
including Kozitsky--Pasurek's finite-component Gibbs-measure construction
([arXiv:math-ph/0609045](https://arxiv.org/abs/math-ph/0609045)) and the
Faris--Minlos multidimensional weak-coupling ground-state analysis
([author PDF](https://math.arizona.edu/~faris/Crystal.pdf)).

The closest located pressure statement, Theorem 3.10 of
Kozitsky--Pasurek, lies explicitly in their scalar ferroelectric sector.
The broader-looking Proposition 2.23 of Kargol--Kondratiev--Kozitsky
([arXiv:0710.2303](https://arxiv.org/abs/0710.2303)) cites that scalar
theorem and uses a relative-partition normalization.  Neither is imported as
direct authority for the eight-component Q3-locked onsite polynomial.
Nagoji's polynomial Gibbs-measure result
([arXiv:2305.19583](https://arxiv.org/abs/2305.19583)) concerns a
Wick-renormalized continuum field on a fixed torus in a dimension-dependent
regime, not this fixed-spacing three-dimensional oscillator thermodynamic
limit.

The local contribution is the assumption-explicit, self-contained
verification of the exact registered Q3LOCK family and normalization.  No
priority claim over the surrounding mathematical field is made.  The bounded
audit found no single primary theorem that also supplies the TECT-specific
phase, physical-reference, continuum, effective-reduction, C0/N1--N5, or
full Pre-A chain.

<a id="section-10-gate-split"></a>
## 10. Gate split

This package closes:

- fixed-spacing open-rectangle source pressure and ground-density existence;
- periodic even-cube equality with the open scalar densities;
- the uniform zero-temperature scalar-density interchange;
- exact additive-scalar covariance and source-free mathematical centering.

It leaves open:

- the sign of every source-pressure cusp and the construction of tangent,
  KMS, ground, pure, or clustering infinite-volume states;
- any thermodynamic phase transition or spontaneous Z2 breaking;
- every interacting gap and correlation limit;
- lattice-spacing removal, counterterms, Euclidean-four-dimensional control,
  and relativistic reconstruction;
- a genuine ST8/Q3LOCK-to-CL8/Q3 effective reduction;
- a common physical empty-space and renormalized stress-energy reference;
- fine one-site translation restoration, light, gravity, cooling, and an
  event-horizon mechanism;
- C0, N1--N5, C6, CP1, Sector A, and Pre-A.

The next direct gate is
`PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-SOURCE-CUSP-TANGENT-STATES-AND-PHASE`.
The effective-reduction, continuum, and physical-reference gates remain
parallel rather than being hidden inside that phase question.

<a id="section-11-devils-advocate-review"></a>
## 11. Devil's-advocate review

1. **Objection:** Prior literature already proves a thermodynamic theorem,
   so this package is a disguised world-first claim.  
   **VALID WITH MITIGATION.** Closely related frameworks are prior art and
   are cited above.  The nearest located load-bearing pressure proof has a
   scalar ferroelectric scope, so the record neither imports it silently nor
   claims priority.  The contribution is the exact Q3LOCK hypothesis and
   normalization audit.

2. **Objection:** `24L^2` seam bonds imply a surface correction.  
   **VALID WITH MITIGATION.** The seam operators are unbounded, so counting
   alone is rejected.  The global quartic absorption (5.4), the form
   coercivity (3.6), and min-max comparison give the actual optimized
   `O(L^(5/2))` total estimate.  No unproved `O(L^2)` bound is stated.

3. **Objection:** Equation (5.8) evaluates the open trace at the moving
   inverse temperature `beta(1+eta)`, so pointwise convergence at fixed beta
   is insufficient.  
   **VALID WITH MITIGATION.** The uniform linear-volume upper and lower
   bounds plus convexity in beta give the local equicontinuity (5.9), which is
   explicitly included before the periodic limit is taken.

4. **Objection:** The thermal limit was exchanged with zero temperature
   without uniform control.  
   **VALID WITH MITIGATION.** Ground-density existence is proved separately.
   The finite-spectrum comparison (6.1) then supplies a volume- and
   boundary-uniform `C/beta` squeeze, which proves both iterated and joint
   scalar limits without a gap assumption.

5. **Objection:** The nonnegative centered energy proves the physical vacuum
   and its ordering relative to empty space.  
   **UPHELD AS FALSE.** Equation (7.4) shows that the sign moves under an
   additive scalar while normalized states do not.  A physical reference on
   the same algebra and geometry remains external.

6. **Objection:** The collective classical restriction derives the inserted
   `1+1` quantum comparator.  
   **UPHELD AS FALSE.** Equation (8.2) exhibits exact collective/transverse
   interaction, and no marginal, constraint, dressed embedding, decoupling,
   or dimension-changing theorem is present.

7. **Objection:** This proves Pre-A.  
   **UPHELD AS FALSE.** It closes one fixed-spacing scalar thermodynamic gate
   while every phase/state, physical-reference, effective-reduction,
   continuum, causal, C0/N1--N5, C6, CP1, and Sector-A interface remains
   explicit and open.

<a id="section-12-reproduction"></a>
## 12. Reproduction

Run from the repository root with the repository virtual environment:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_fixed_lattice_3d_quantum_pressure_ground_density_effective_reduction_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_fixed_lattice_3d_quantum_pressure_ground_density_effective_reduction_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_fixed_lattice_3d_quantum_pressure_ground_density_effective_reduction_route_split_verify.py
```

The scripts audit exact constants, polynomial identities, edge counts,
finite-dimensional spectral fixtures, provenance, scope, and record
integration.  They do not replace the analytic Fekete, form-order, min-max,
convex-equicontinuity, and zero-temperature arguments written above.
