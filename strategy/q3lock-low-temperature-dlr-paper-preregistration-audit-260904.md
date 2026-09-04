# Q3LOCK low-temperature DLR phase paper: pre-registration applicability audit

**Status:** PRE-REGISTRATION / RESEARCH DOCUMENT  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782 only  
**Claim status:** no independent claim has yet been registered  
**Publication status:** no P2 manuscript, submission, upload, tag, or publication  
**PDF status:** deliberately deferred until the mathematical content and audits are complete

## 1. Exact target

The proposed independent paper concerns the positive-`lambda`, fixed-spacing,
three-dimensional, eight-component Q3-locked quantum anharmonic crystal.  Its
intended main theorem is the following bounded statement.

Let `hbar>0`, `chi>0`, `c>0`, `g>0`, `lambda>0`, and `r<0`.  On each periodic
even cube `Lambda_L=(Z/LZ)^3`, place one vector `q_y in R^8` at every coarse
site and use

```text
H_L(h) = sum_y [ |p_y|^2/(2 chi) + r |q_y|^2/2
                  + (g/4) sum_e q_(y,e)^4
                  + (lambda/4) sum_(e~f) (q_(y,e)-q_(y,f))^2
                                           (q_(y,e)^2+q_(y,f)^2) ]
         + (c/2) sum_<yz> |q_y-q_z|^2
         - h sum_y u dot q_y,

u=(1,...,1)/sqrt(8).
```

Define the fine energy pressure

```text
P_(beta,L)(h) = [8 beta |Lambda_L|]^-1 log Tr exp[-beta H_L(h)].
```

Set

```text
theta_Q = -r/[3(g+lambda)],
A0      = 8 c chi theta_Q^2/hbar^2,
I3      = (2 pi)^-3 integral_(-pi,pi]^3
          [sum_(j=1)^3 (1-cos p_j)]^-1 dp,
rho     = sqrt(I3/A0),
x_star  = artanh(rho),
beta_star = (4 chi theta_Q/hbar^2) x_star rho.
```

The target conclusion is restricted to `A0>I3` and `beta>beta_star`.  In that
regime the limiting pressure has a strict cusp at zero collective source and
there are at least two distinct parity-related tempered Euclidean DLR states
whose collective expectations have opposite signs.  Failure of either
sufficient inequality is inconclusive.

This target does not contain a common real-time dynamics, an algebraic KMS
identification, a zero-temperature ground-state theorem, a spectral gap,
extremality, purity, clustering, continuum removal, a physical vacuum, a TECT
cosmological interpretation, or closure of C6, CP1, Sector A, or Pre-A.

## 2. Authority partition

| Authority | Load-bearing content allowed in the paper | Content that remains excluded |
|---|---|---|
| EXP-000780 | finite-volume self-adjointness and trace finiteness; open and periodic source-pressure limits; local uniformity, convexity and global parity evenness | phase transition, DLR selection, continuum or physical interpretation |
| EXP-000781 | exact vector quantum-crystal DLR theorem instantiation; compactness and uniform local moments; zero-source source-tangent DLR states and the factor-eight pressure-slope identity | a strict positive slope for positive `lambda`; extremality, purity, clustering or KMS dynamics |
| EXP-000782 | Q3LOCK continuous-loop FKG; collective moment lower bound; Bruch--Falk and infrared chain; explicit sufficient regime; strict cusp and two parity-related DLR states | all-parameter phase, common dynamics, ground phase/gap, continuum or physical interpretation |

Later Q3LOCK explorations may be cited only as non-load-bearing assurance or
scope warnings unless this authority contract is explicitly amended.  They
must not silently enlarge the theorem.

## 3. Primary-source applicability matrix

The dispositions below are deliberately stricter than a bibliography.  An
`APPLIES-CONDITIONALLY` row is not sufficient for a T6 claim until every
remaining check is closed and independently reviewed.

### 3.1 Kozitsky--Pasurek: Euclidean DLR existence and compactness

**Primary source:** Y. Kozitsky and T. Pasurek, *Euclidean Gibbs States of
Interacting Quantum Anharmonic Oscillators*, Journal of Statistical Physics
127 (2007), 985--1047; arXiv:math-ph/0609045;
DOI `10.1007/s10955-006-9274-9`.  Candidate locators: Theorems 3.1--3.3.

**Intended import:** nonemptiness and compactness of the tempered Euclidean
DLR set, uniform exponential one-site moment bounds, and tempered support.

| Source hypothesis or scope | Q3LOCK crosswalk | Disposition |
|---|---|---|
| finite vector dimension `nu` | `nu=8` | SATISFIED |
| countable lattice with summable interaction | `Z^3` with finite-range nearest-neighbour scalar coupling `c` | SATISFIED |
| positive oscillator mass | `m=chi/hbar^2>0` | SATISFIED |
| continuous local potential with uniform superquadratic lower control | `sum_e q_e^4 >= |q|^4/8`, the Q3LOCK quartic is nonnegative, and the linear source is uniformly Young-absorbed on compact source intervals | SATISFIED |
| local upper control required by Assumption 2.1 | after expanding the bond square, choose any fixed harmonic rigidity `a>0`; the remaining translation-invariant polynomial `V_h` is bounded above by one continuous quartic polynomial on every compact source interval | SATISFIED |
| lattice regularity (2.1) | `L=Z^3`; the required uniformly centred polynomial tail is finite for every positive exponent increment | SATISFIED |
| unweighted interaction norm (2.5) | in the source convention `J_(yz)=c` for nearest neighbours and zero otherwise, hence `Jhat_0=6c<infinity` | SATISFIED |
| tempered weights and weighted interaction norm, Assumption 2.5 | take `w_alpha(y,z)=exp(-alpha|y-z|)`: (2.36)--(2.38) hold on `Z^3`, `Jhat_alpha=6c exp(alpha)<infinity`, and `Jhat_alpha-Jhat_0` can be made arbitrarily small | SATISFIED |
| fixed `beta>0` and fixed source | the construction is performed at each fixed `beta` and source before source removal | SATISFIED |
| fixed-source DLR closure | Lemma 2.8 gives the Feller property on every `Omega_alpha`; Lemma 2.11 sends any `W_alpha` accumulation point that remains in `P(Omega^t)` to `G^t`; Theorems 3.1--3.2 give nonemptiness, `W^t` compactness and uniform one-site exponential moments | APPLIES |
| continuity and compactness while the source varies to zero | the source proof of Lemma 4.1 uses only the common lower/upper potential controls, `m`, `a`, `beta` and the interaction norms; the Q3LOCK compact-source family has common such data.  The varying-kernel argument is given below | PAPER-LOCAL EXTENSION PROVED |

**Current disposition:** `APPLIES` for each fixed source.  The additional
compact-source tangent extension is proved at pre-registration level below and
must be reproduced in the manuscript.

The exact lattice, potential, interaction and tempered-weight hypotheses have
now been matched.  Fixed-source DLR existence is therefore a valid import.
The source-removal step is not inferred from the fixed-model theorem alone;
it uses the following uniform-family lemma.

The KP v1 locator correction is recorded in
`strategy/q3lock-kp-locator-correction-audit-260905.md`; the historical PDF is
unchanged and only this local crosswalk is corrected.

#### Compact-source tangent lemma

Fix `h0<infinity` and let `G_h^t` be the tempered DLR set for `|h|<=h0`.
Then the union of these sets is relatively compact in `W^t`.  Moreover, if
`h_n -> 0`, `mu_n in G_(h_n)^t`, and `mu_n -> mu` in `W^t`, then
`mu in G_0^t` and every one-site linear observable is uniformly integrable
along the sequence.

To see uniformity, expand the bond square and choose any `a>0` in the source
harmonic split.  With `b=(r+6c-a)/2`,

```text
V_h(q) >= (g/32)|q|^4 + b|q|^2 - h0|q|
       >= (g/64)|q|^4 + B_(h0).
```

For the common upper function, use

```text
(q_e-q_f)^2(q_e^2+q_f^2) <= 4(q_e^4+q_f^4)
```

and the fact that every Q3 vertex has degree three.  Hence the Q3 term is at
most `3 lambda sum_e q_e^4`, and one common continuous quartic upper function
works for every `|h|<=h0`.  In the proof of Kozitsky--Pasurek Lemma 4.1, the
constant is obtained from precisely these common lower and upper controls,
`m`, `a`, `beta` and `Jhat_0`; Lemmas 4.3--4.5 and the proof of Theorem 3.2
then preserve the same uniformity.  This gives a common exponential one-site
bound and the claimed relative compactness.

For the varying DLR equation, fix a finite `Delta` and write

```text
X_Delta(omega) = sum_(y in Delta) integral_0^beta
                 u dot omega_y(tau) d tau.
```

Relative to the zero-source local kernel,

```text
pi_Delta^h(f|xi)
 = pi_Delta^0(f exp(h X_Delta)|xi)
   / pi_Delta^0(exp(h X_Delta)|xi).
```

Differentiation at an intermediate source `t` gives

```text
|d pi_Delta^t(f|xi)/dt|
 <= 2 ||f||_infinity pi_Delta^t(|X_Delta||xi).
```

The finite-region version of the uniform kernel estimate bounds the last
quantity by a constant plus a finite weighted sum of neighbouring boundary
loop norms.  Integrating against `mu_n` and using the common one-site
exponential moment therefore yields

```text
integral |pi_Delta^(h_n)f-pi_Delta^0 f| dmu_n
 <= C_(Delta,f,h0) |h_n| -> 0.
```

The zero-source Feller property makes `pi_Delta^0 f` bounded and continuous
on each tempered space.  Passing to the limit in
`mu_n(f)=mu_n(pi_Delta^(h_n)f)` proves the zero-source DLR equation.  The same
common exponential estimate gives uniform integrability of the one-site
linear observable.  This closes the source-varying part of the tangent-state
construction without claiming any common real-time dynamics.

### 3.2 Kargol--Kondratiev--Kozitsky: periodic states and pressure tools

**Primary source:** A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase
Transitions and Quantum Stabilization in Quantum Anharmonic Crystals*,
Reviews in Mathematical Physics 20 (2008); arXiv:0710.2303;
DOI `10.1142/S0129055X08003353`.

Candidate locators are Propositions 2.12--2.13, 2.21, 2.23, 3.9, Lemma 3.12,
Corollary 3.14, and Proposition 3.18.

| Source result | Intended role | Current disposition | Required closure |
|---|---|---|---|
| Propositions 2.12--2.13 | for every fixed `beta>0`, `G^t` is nonempty, convex and `W^t`-compact; for every `sigma in (0,1/2)` and `kappa>0`, one constant bounds the stated one-site exponential moment uniformly in the site and `mu in G^t` | APPLIES | the compact-source tangent lemma above supplies the extra family-uniform statement used by this paper |
| Lemma 2.20 and Proposition 2.21 | periodic box laws are `W^t`-relatively compact; their `W^t` accumulation points lie in `G^t` and are translation invariant | APPLIES | use the even periodic boxes of EXP-000780; source removal is covered by the compact-source tangent lemma rather than attributed to Proposition 2.21 |
| Proposition 2.23 | thermodynamic pressure | DOES-NOT-APPLY AS A LOAD-BEARING IMPORT | EXP-000780 gives a self-contained exact-Q3LOCK pressure proof; retain this proposition as background only because the published pressure statement has a different scalar/normalization scope |
| Proposition 3.9 (Griffiths) | if the limiting scaled log moment generating function is differentiable at zero, the normalized collective variable converges against continuous exponentially bounded tests; in general (3.23) bounds the limsup by the maximum over the subgradient interval | APPLIES | use the Euclidean time-integrated source variable `X_L`, not a fictitious commuting equal-time exponential; the exact scaling and factor eight are proved below |
| Lemma 3.12 and Corollary 3.14 | reflection positivity, Gaussian domination and infrared comparison | DOES-NOT-APPLY DIRECTLY TO Q3LOCK | the published corollary assumes the translation- and rotation-invariant vector model; positive-`lambda` Q3LOCK is nonradial.  The paper must prove the Hilbert-valued Q3LOCK version instead of importing the corollary |
| Proposition 3.18 (Bruch--Falk) | for the finite-volume observable `A`, relate `b(A)`, `g(A)` and `c(A)=rho([A,[beta H,A]])` by (3.68) | APPLIES | the unbounded local collective coordinate is reached by the smooth spectral cutoff proved below; the double commutator is `beta hbar^2/chi` in the present normalization |

#### Continuous-loop association audit

The positive-`lambda` Q3 interaction is not being certified by the phrase
"MTP2 is preserved under weak convergence".  MTP2 is a density property and
that shortcut is stronger than what the manuscript needs.  The paper-local
statement will be association of the exact loop law, proved in three bounded
steps.

1.  On a periodic time grid with mesh `epsilon`, add a positive harmonic split
    `a>0` to the one-coordinate kinetic reference.  The resulting Gaussian
    precision matrix is a cyclic M-matrix, so its density is MTP2.  The
    interacting grid density has nonnegative mixed log-derivatives: the
    spatial bond contributes `c epsilon`, and for every Q3 edge

    ```text
    -epsilon d^2/dxdy [(lambda/4)(x-y)^2(x^2+y^2)]
      = (epsilon lambda/4)[(x+y)^2+5(x-y)^2] >= 0.
    ```

    Linear sources and diagonal scalar terms do not change these derivatives.
    The finite-dimensional FKG theorem therefore gives association for every
    grid law, for every fixed source in a compact source interval.  Quartic
    confinement supplies the required integrability.

2.  For each fixed finite spatial volume and source, take the time-grid limit
    first using the standard Feynman--Kac/Trotter interpolation into the
    continuous periodic-loop space.  More explicitly, with `epsilon=beta/N`
    and `m=chi/hbar^2`, the interpolated grid law is obtained from the
    positive harmonic Gaussian reference by the density

    ```text
    exp[-epsilon sum_(y,k) V_h(x_(y,k))]
    ```

    together with the kinetic quadratic action
    `m/(2 epsilon) sum_(y,k)|x_(y,k+1)-x_(y,k)|^2`.  If
    `V_h >= A|q|^4-C` on the compact source interval, the density is bounded
    above by `exp(beta C)` at fixed spatial volume.  The piecewise-linear
    Gaussian interpolations are tight in the continuous sup-norm topology;
    choose `R` so that their sup-norm ball has probability at least `1/2`
    uniformly for all sufficiently fine grids.  Since `V_h` is bounded above
    on that ball, the same event gives a mesh-uniform positive lower bound on
    the normalizer.  The quartic lower bound supplies uniform polynomial
    moments, so the weighted interpolations are tight and uniformly
    integrable.  Feynman--Kac/Trotter convergence identifies every weak
    subsequential limit with the exact local Euclidean loop law.  For bounded
    continuous increasing functionals `F` and `G`, the grid inequality
    `E_epsilon[FG] >= E_epsilon[F]E_epsilon[G]` then passes to the limit because
    `F`, `G`, and `FG` are bounded and continuous.  This proves association of
    every finite evaluation/cylinder marginal.  No total-variation claim is
    needed; the earlier certificate's stronger wording must not be copied into
    the paper without a separate proof.

3.  Coordinate products are recovered by clipping each evaluation at level
    `R`, applying association to the bounded increasing clips, and sending
    `R` to infinity using the common quartic second-moment bound.  At zero
    source the global parity of the full Q3LOCK law gives zero one-point means,
    hence `E[q_(y,e)q_(y,f)] >= 0` for every distinct pair of components.

This closes the analytic route needed for the collective Q3 estimate at the
pre-registration level, but the finite-grid-to-loop tightness and uniform
integrability paragraphs remain mandatory proof text and external-audit items.

For completeness, a stronger finite-dimensional statement is available in
the density-free MTP2 framework of Colangelo--Mueller--Scarsini (Theorem 1,
J. Appl. Prob. 43 (2006), DOI `10.1239/jap/1143936242`): weak limits of
finite-dimensional MTP2 laws remain MTP2 in that definition.  We do not rely
on that theorem for the present paper, because the required observable is an
ordered path functional and the association argument above is shorter and
does not require introducing a path-space lattice MTP2 definition.

#### Exact Griffiths normalization

Let `V_L=|Lambda_L|` and, under the zero-source periodic Euclidean loop law,
define

```text
X_L = sum_(y in Lambda_L) integral_0^beta
      u dot omega_y(tau) d tau.
```

The source tilt is exactly `exp(h X_L)`.  It is not
`exp(beta h sum_y u dot q_y)` inside the zero-source quantum expectation,
because the position sum need not commute with the Hamiltonian.  The
Feynman--Kac identity instead gives

```text
f_L(h) = V_L^-1 log E_0[exp(h X_L)]
       = 8 beta [P_(beta,L)(h)-P_(beta,L)(0)].
```

EXP-000780 gives the finite pointwise limit
`f(h)=8 beta[P_beta(h)-P_beta(0)]`.  Hence

```text
f'_+(0) = 8 beta D_+ P_beta(0).
```

Set `Pi_L=E_0[X_L^2]/(beta V_L)^2`.  Apply Proposition 3.9, equation
(3.23), with `M_L=V_L` and `g(z)=z^2`, which is continuous and bounded by
an exponential.  Since `f` is even and convex, its subgradient interval at
zero is `[-f'_+(0),f'_+(0)]`.  Therefore

```text
beta^2 limsup_L Pi_L
 = limsup_L E_0[(X_L/V_L)^2]
 <= [f'_+(0)]^2
 = [8 beta D_+ P_beta(0)]^2.
```

The infrared step supplies `limsup_L Pi_L >= delta_beta`; consequently

```text
D_+ P_beta(0) >= sqrt(delta_beta)/8.
```

Parity gives the opposite left derivative.  This establishes the exact
Griffiths scaling and the factor `1/8`; the remaining cusp-to-DLR composition
uses the compact-source tangent lemma and does not assume extremality.

#### Unbounded-coordinate Bruch--Falk extension

In one finite periodic volume, let `Q=u dot q_0` and choose the bounded smooth
spectral truncation

```text
Q_R = R tanh(Q/R).
```

The potential is a multiplication operator and commutes with `Q_R`.  On the
Schwartz form core, the kinetic commutator identity is

```text
[Q_R,[beta H_L,Q_R]]
 = (beta hbar^2/chi) sech^4(Q/R).
```

The right side is bounded between zero and `beta hbar^2/chi` and converges
strongly to that constant.  Finite-volume quartic confinement gives a finite
heat trace and all polynomial coordinate moments, so dominated convergence
gives

```text
g(Q_R) -> <Q^2>,
c(Q_R) -> beta hbar^2/chi.
```

For a self-adjoint `B`, the spectral representation of the Duhamel form and
the logarithmic-mean bound give

```text
0 <= b(B) <= <B^2>.
```

Since `|Q-Q_R|<=|Q|` and `Q_R->Q` pointwise,
`<(Q-Q_R)^2> -> 0`; hence `Q_R->Q` in the Duhamel norm and
`b(Q_R)->b(Q)`.  Proposition 3.18 applies to every bounded `Q_R`.  Passing
`R->infinity` through its continuous right-hand side proves

```text
(Q,Q)_D >= <Q^2>
 f((beta hbar^2/chi)/(4<Q^2>)).
```

No operator equality outside the common form core is needed.  Combining this
with `<Q^2>>=theta_Q` and the already verified monotonicity of
`s f(k/s)` yields the local Duhamel lower bound used by EXP-000782.  Thus the
unbounded-observable domain issue is closed at pre-registration level.

### 3.3 Froehlich--Simon--Spencer infrared method

**Primary source:** J. Froehlich, B. Simon and T. Spencer, *Infrared Bounds,
Phase Transitions and Continuous Symmetry Breaking*, Communications in
Mathematical Physics 50 (1976), 79--95; DOI `10.1007/BF01608557`.

**Current disposition:** `APPLIES AFTER A FINITE-GRID EXTENSION`; the published
rotation-invariant corollary is not imported.

The FSS lattice theorem is stated for a fixed finite spin dimension and an
arbitrary single-spin a-priori measure with the required exponential moments;
the authors explicitly note that the Gaussian-domination constant is
independent of internal symmetry and of the number of components.  This is the
relevant source result.  The Q3LOCK loop spin is infinite-dimensional only
because of the Euclidean-time coordinate, so the paper uses the following
finite-dimensional-to-loop extension.

#### Hilbert-valued reflection-positivity/Gaussian-domination lemma

For a time grid of size `N`, regard each site as one spin in
`R^(8N)` with weighted inner product
`<x,y>_N=epsilon sum_k x_k dot y_k`.  Equivalently use ordinary coordinates
`s=sqrt(epsilon)*x`; under this isometry the source vector acquires the
corresponding `sqrt(epsilon)` factor.  The single-site measure contains the
kinetic, scalar, Q3 and (at zero source) harmonic-split factors.  It has all
quadratic exponential moments at fixed `N`, by the quartic lower bound.  Across
any spatial reflection plane the only
cross-plane factor is

```text
exp[-c ||a-b||^2/2]
 = exp[-c ||a||^2/2] exp[-c ||b||^2/2] exp[c <a,b>].
```

The final factor is positive definite: its exponential series is a sum of
nonnegative symmetric-tensor kernels.  Every Q3 and time-kinetic factor is
strictly onsite for this spatial reflection, regardless of the internal
nonradial anisotropy.  The finite-dimensional FSS transfer-matrix argument
therefore gives, for every edge shift `b`,
`Y_N(b) <= Y_N(0)`.

For the load-bearing infrared estimate it is enough to take the zero-sum
time-constant source `j_y(tau)=t a_y u`.  In weighted coordinates this means
`<j,x>_N=t*epsilon*sum_(y,k) a_y*(u dot x_(y,k))`; in ordinary coordinates the
same source has entries `t*sqrt(epsilon)*a_y*u` at every time slice.  Its edge field
`b=(1/c)D L_sp^{-1}j` is time-constant as well, and is represented exactly
on every time grid; no arbitrary-`L2` density theorem is needed.  More
generally, bounded step functions `b_N` can be passed through the
Feynman--Kac/Trotter limit using the common quartic exponential bound, but
that extension is optional and non-load-bearing.  For the required source in
`K^Lambda`, `K=L2(S_beta;R8)`, expanding the shifted square gives

```text
log E_0 exp(sum_y <j_y,omega_y>_K)
 <= (1/(2c)) <j,L_sp^{-1}j>_(K^Lambda).                 (RP-GD)
```

For bounded step-function edge fields the required domination can be made
uniform by

```text
exp[-c||D omega-b_N||^2/2]
 <= exp[c||b_N||^2/2] exp[-c||D omega||^2/4].
```

The right-hand side is integrable against the quartically confined single-site
measure.  Thus the shifted and unshifted partition functions have the same
Feynman--Kac limit along the required constant (or bounded step) source
approximations; no formal infinite-dimensional transfer matrix is being
assumed.

Indeed, with `D` oriented once on every spatial edge,
`c <D omega,b> = <omega,j>` and
`(c/2)||b||^2 = (2c)^(-1)<j,L_sp^(-1)j>`.  For the time-constant choice
`j_y(tau)=t a_y u`, `sum_y a_y=0`, the second derivative of the left side at
`t=0` is `beta^2 a^T D_L^Q a`, whereas the right side contributes
`(beta/c) a^T L_sp^(-1)a`.  This displays the only beta factor and yields the
projected Fourier constant below.

This is the only reflection-positive input used in the paper.  Taking
`j_y(tau)=t a_y u` and differentiating at `t=0` yields, without any component
diagonalization,

```text
(Q-hat_p,Q-hat_-p)_D <= 1/(2 beta c E(p)),   p != 0.
```

The source paper's Corollary 3.14 additionally uses translation and
`O(8)`-rotation invariance to diagonalize the component covariance.  That
corollary is explicitly excluded here; the projected bound above follows
directly from (RP-GD) for the fixed nonradial vector `u`.

#### Constant-source transfer and loop limit

The finite-dimensional input can be stated with no internal symmetry.  At
grid size `N`, collect the eight components and `N` time slices at one site
into `a_y in R^(8N)`, with the weighted inner product
`epsilon sum_k a_(y,k) dot b_(y,k)`.  The onsite density contains the cyclic
kinetic quadratic form, the scalar and Q3 factors, and the harmonic split;
quartic confinement supplies every quadratic exponential moment required by
the Froehlich--Simon--Spencer transfer argument.  After a spatial reflection,
each crossing bond has kernel

```text
K(a,b) = exp[-c||a-b||^2/2]
       = exp[-c||a||^2/2] exp[-c||b||^2/2] exp[c<a,b>].
```

The last factor is positive definite because
`exp[c<a,b>]` is the sum of its nonnegative symmetric-tensor kernels.  The
reflection form is therefore a positive square for the arbitrary anisotropic
onsite measure, and the finite-dimensional FSS theorem gives
`Y_N(b)<=Y_N(0)` for every finite-grid edge shift.

For the only shift needed in the paper,
`j_y(tau)=t a_y u` with `sum_y a_y=0`, the Poisson solution
`b=(1/c)D L_sp^(-1)j` is constant in time and is represented exactly on every
grid.  The shifted integrand is dominated by

```text
exp[-c||D omega-b||^2/2]
 <= exp[c||b||^2/2] exp[-c||D omega||^2/4],
```

and the right-hand side is integrable under the quartically confined local
loop law.  Gaussian interpolation tightness and the same normalizer lower
bound used in the FKG passage give convergence of the shifted and unshifted
partition functions to their Feynman--Kac loop limits.  Thus the finite-grid
inequality passes to the exact loop law for this constant source; no general
infinite-dimensional transfer matrix or arbitrary-`L2` edge-field density
argument is needed for the infrared theorem.

Finally, expanding the shifted square gives

```text
log E_0 exp(<j,omega>) <= (2c)^(-1) <j,L_sp^(-1)j>.
```

For a time-constant source, the left second derivative is
`beta^2 a^T D_L^Q a` and the right second derivative is
`(beta/c) a^T L_sp^(-1)a`.  Since the spatial Laplacian eigenvalue is
`2E(p)`, the projected bound is `1/(2 beta c E(p))`.  The finite-grid transfer,
constant-source loop-limit, and differentiation-under-the-integral details
are now explicit manuscript obligations; an external audit is still required
before P-09 can be promoted.

#### Three-dimensional Watson-sum convergence

The finite-volume infrared remainder can be controlled without treating the
decimal value of `I3` as a proof input.  Let

```text
p_k = 2 pi k/L,
E(p) = sum_j (1-cos p_j),
I_(3,L) = L^(-3) sum_(k != 0) 1/E(p_k),
```

with the usual representatives in `(-pi,pi]^3`.  For `|t|<=pi`,
`1-cos(t) >= 2 t^2/pi^2`; hence, for `0<|p|<=pi`,
`E(p) >= 2|p|^2/pi^2`.  Fix `0<delta<1`.  The contribution from
`0<|p_k|<delta` is bounded by

```text
L^(-3) sum_(0<|k| <= C delta L) C L^2/|k|^2 <= C' delta + C'/L,
```

because the number of integer points in a shell of radius `n` is at most a
constant times `n^2`.  The continuum integral over the same ball obeys the
identical `C delta` bound.  On the complement `|p|>=delta`, `1/E(p)` is
continuous, so the ordinary Riemann-sum theorem applies.  Letting first
`L->infinity` and then `delta->0` proves

```text
I_(3,L) -> I3 = (2 pi)^(-3) integral_(-pi,pi]^3 dp/E(p).
```

The argument works for every periodic side-length sequence and therefore also
for the dyadic sequence used by the reflection argument.  It proves the
analytic convergence required in P-10; the displayed decimal value of `I3`
remains only a reproducible numerical enclosure and must be recomputed from
the integral definition by the verifier.

#### Threshold equivalence

The scalar map `x -> x tanh(x)` is strictly increasing on `(0,infinity)`
because its derivative is `tanh(x)+x sech^2(x)>0`, and it has range
`(0,infinity)`.  Therefore the equation

```text
x_beta tanh(x_beta) = beta hbar^2/(4 chi theta_Q)
```

has exactly one positive solution.  With `f(x tanh x)=tanh(x)/x`,

```text
2 beta c theta_Q f(x_beta tanh x_beta)
  = (8 c chi theta_Q^2/hbar^2) tanh(x_beta)^2
  = A0 tanh(x_beta)^2.
```

Consequently `delta_beta>0` is equivalent to
`A0 tanh(x_beta)^2>I3`.  If `A0<=I3`, this cannot hold because
`tanh(x_beta)^2<1`.  If `A0>I3`, put
`rho=sqrt(I3/A0)` and `x_star=artanh(rho)`.  Monotonicity of `tanh` and of
`x tanh(x)` then gives

```text
delta_beta>0  <=>  x_beta>x_star
                <=>  beta>(4 chi theta_Q/hbar^2) x_star rho
                <=>  beta>beta_star.
```

This closes the paper-local algebra in P-11, including the strict boundary
case; it does not extend the sufficient regime or prove phase absence below
the threshold.

#### Finite-volume and pressure proof spine

The finite-volume part can be transcribed without importing a phase theorem.
For `r_- = max(0,-r)` and a component source `J_e`, the elementary bounds

```text
g x^4/16 - r_- x^2/2 >= -r_-^2/g,
g x^4/16 - |J_e||x| >= -(3/4)(4/g)^(1/3)|J_e|^(4/3)
```

leave a positive `g x^4/8` remainder.  Summing coordinates and retaining the
nonnegative spatial and Q3 terms gives a common quadratic-form lower bound

```text
H_R(J) >= K_R - b_J |R| >= Q_R - b_J |R|,
```

where `K_R` is a tensor product of one-dimensional quartic oscillators and
`Q_R=(g/8) sum_(y,e) q_(y,e)^4`.  The closed polynomial form is therefore
semibounded; the quartic comparison gives compact resolvent and finite heat
trace by min--max eigenvalue comparison.  The quartic term is essential here,
since a free-particle heat trace on the line is infinite.

For an open even rectangle, cutting into two rectangles produces only a
nonnegative crossing spatial form.  The min--max principle makes the ground
energy superadditive and `log Z` subadditive.  Tiling large rectangles and
controlling the even remainders by the common linear-volume bounds gives the
multidimensional Fekete limits for ground and pressure densities.

For an even periodic cube, the seam operator `B_L` is the sum of `24 L^2`
scalar seam bonds.  Young absorption gives, for every `eta>0`,

```text
0 <= B_L <= eta Q_L + 288 c^2 L^2/(eta g).
```

Min--max then sandwiches periodic and open heat traces after a temperature
rescaling by `1+eta`, while the same form estimate sandwiches the ground
energies.  The open log-partition density is convex in `beta` and uniformly
bounded on compact positive-beta/source sets, hence locally Lipschitz there.
Taking `eta=L^(-1/2)` proves equality of periodic and open density limits with
an `O(L^(-1/2))` seam error.  Finally, Holder convexity in the source and the
unitary global inversion `J -> -J` give a finite, convex, even limiting
pressure; pointwise convergence plus the uniform convex bounds gives local
uniform convergence on compact source intervals.  This closes the analytic
content of P-01--P-03 at pre-registration level; the manuscript must still
display the estimates and an independent reviewer must check the seam count,
min--max use and local-uniform convergence argument.

#### Source-tangent and Griffiths bridge

For the collective direction `u`, choose differentiability points
`h_k downarrow 0` of the finite limiting pressure `P_beta`.  Convex secant
squeezing gives

```text
lim_(L->infinity) P_(beta,L)'(h_k) = P_beta'(h_k).
```

The periodic loop laws at each fixed `h_k` have tempered DLR accumulation
points by the cited periodic-DLR theorem.  The common compact-source
exponential moment estimate makes `u dot omega_0(0)` uniformly integrable, so

```text
(1/8) integral u dot omega_0(0) d mu_(h_k) = P_beta'(h_k).
```

The compact-source tangent lemma then supplies a subsequential limit
`mu_+ in G_0^t` as `k->infinity`, and uniform integrability gives

```text
integral Q_0 d mu_+ = 8 D_+ P_beta(0).
```

Global parity sends `mu_+` to a zero-source state `mu_-` with the opposite
expectation.  This construction uses neither extremality nor a common real-
time dynamics.

The pressure-to-slope conversion uses the exact Euclidean source variable

```text
X_L = sum_y integral_0^beta Q_y(tau) d tau,
f_L(h) = L^(-3) log E_0 exp(h X_L)
       = 8 beta [P_(beta,L)(h)-P_(beta,L)(0)].
```

At zero source, `Pi_L=E_0[X_L^2]/(beta L^3)^2`.  Applying the Griffiths
moment-to-slope lemma to `X_L/L^3` with the square test function gives

```text
beta^2 limsup_L Pi_L <= [f'_+(0)]^2
                              = [8 beta D_+ P_beta(0)]^2.
```

Therefore any lower bound `limsup Pi_L>=delta_beta>0` implies
`D_+P_beta(0)>=sqrt(delta_beta)/8`.  The infrared estimate supplies this
lower bound along the dyadic subsequence, while the full pressure limit lets
the limsup inequality be used.  Combining the positive slope with the parity
image yields a strict source cusp and two distinct DLR states.  This closes
the source-tangent and Griffiths algebra at pre-registration level; the future
manuscript must reproduce the convex subsequence choice, the exact source
normalization and the final composition with the FKG/RP lower bound.

#### Collective double-commutator and Q3 projection

Let `Pi_0=V^(-1/2) sum_y u dot p_y` in a finite periodic volume and let
`U_s=exp(-i s Pi_0/hbar)`.  The translation `U_s` shifts every cell by the
same vector `s u/sqrt(V)`, so the spatial difference energy is invariant.  The
polynomial Hamiltonian forms have a common translation-invariant form domain;
quartic confinement gives finite heat-trace moments of every polynomial
appearing below.  Thus the unitarily constant partition function can be
differentiated after finite spectral cutoff and the cutoff removed by the
quartic moment bound.  At zero source,

```text
0 = d^2/ds^2 log Tr exp[-beta U_s^* H_L(0) U_s] at s=0
  = -beta <H''(0)> + beta^2 (H'(0),H'(0))_D,
```

and positivity of the Duhamel covariance implies `<H''(0)> >= 0`.  Direct
differentiation on the polynomial core gives

```text
[Pi_0,[H_L(0),Pi_0]]
 = hbar^2 [ r + (3g/(8V)) sum_y S_y
              + (lambda/(8V)) sum_y D_y ],
```

where `S_y=sum_e q_(y,e)^2` and
`D_y=sum_(e~f)(q_(y,e)-q_(y,f))^2`.  Translation invariance of the finite
periodic Gibbs state therefore yields

```text
-r <= (3g/8) E[S_0] + (lambda/8) E[D_0].
```

The zero-source association result gives `E[q_(0,e)q_(0,f)]>=0` for every
distinct component pair.  Since Q3 is 3-regular,

```text
E[D_0] = 3 E[S_0] - 2 sum_(e~f) E[q_(0,e)q_(0,f)] <= 3 E[S_0],
E[Q_0^2] = (1/8)[E[S_0]+2 sum_(e<f)E[q_(0,e)q_(0,f)]] >= E[S_0]/8.
```

Combining these inequalities gives the uniform collective bound
`E[Q_0^2]>=-r/[3(g+lambda)]=theta_Q>0`.  The argument is genuinely
collective: a Q3 spectral estimate without FKG controls only total amplitude
and does not exclude a covariance transverse to `u`.  This closes the
paper-local algebra and identifies the exact domain passage required for P-07;
an independent reviewer must still check the common-form differentiation and
the FKG moment truncation.

## 4. Paper-local proof obligations

The following obligations may use standard lemmas after their assumptions are
audited, but the model-specific steps must appear in the manuscript rather
than only in executable assertions.

| ID | Required proof text | Current evidence | Registration disposition |
|---|---|---|---|
| P-01 | finite-volume lower boundedness, compact resolvent and finite heat trace | EXP-000780 plus the finite-volume proof spine above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent operator audit remain |
| P-02 | open pressure limit and periodic/open equality, including the `O(L^-1/2)` density seam estimate | EXP-000780 plus the finite-volume proof spine above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent seam/min--max audit remain |
| P-03 | local-uniform convex pressure convergence and parity evenness | EXP-000780 plus the finite-volume proof spine above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent convex-limit audit remain |
| P-04 | exact DLR theorem assumption crosswalk and periodic compactness | EXP-000781 plus section 3.1 above | CLOSED AT PRE-REGISTRATION LEVEL; MANUSCRIPT TRANSCRIPTION REQUIRED |
| P-05 | source-tangent selection and the factor-eight slope/magnetization identity | EXP-000781 plus the source-tangent/Griffiths bridge above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent convex/DLR audit remain |
| P-06 | continuous-loop FKG for the nonradial Q3 interaction, including Trotter limit and unbounded moment truncation | EXP-000782 plus the association audit in section 3.2 | PROOF TEXT AND EXTERNAL AUDIT REQUIRED; the manuscript must use weak-limit association, not an unproved total-variation/MTP2 shortcut |
| P-07 | collective moment lower bound from the exact double commutator and Q3 graph/FKG estimates | EXP-000782 plus the collective double-commutator section above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent domain/FKG audit remain |
| P-08 | Bruch--Falk local Duhamel lower bound with exact normalization | EXP-000782 plus the smooth-cutoff lemma above | CLOSED AT PRE-REGISTRATION LEVEL; MANUSCRIPT TRANSCRIPTION REQUIRED |
| P-09 | Hilbert-valued reflection positivity and Gaussian domination without `O(8)` invariance | EXP-000782 plus the finite-grid FSS extension in section 3.3 | PAPER-LOCAL PROOF AND EXTERNAL AUDIT REQUIRED; finite-grid transfer matrix and the constant-source loop-limit passage remain open |
| P-10 | three-dimensional infrared summation and the definition of `I3` | EXP-000782 plus the Watson-sum estimate above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent numerical enclosure remain |
| P-11 | equivalence of `A0>I3`, `beta>beta_star` and `delta_beta>0` | EXP-000782 plus the threshold-equivalence calculation above | CLOSED AT PRE-REGISTRATION LEVEL; manuscript transcription and independent algebra audit remain |
| P-12 | Griffiths conversion, strict cusp, and construction of two distinct parity DLR states | EXP-000781--782 plus the source-tangent/Griffiths bridge above | CLOSED AT PRE-REGISTRATION LEVEL conditional on P-06/P-09; manuscript composition and independent audit remain |

#### Reproducibility artifact stability gate

The mathematical primary and independent result payloads are deterministic, but
the current integrated verifier records the fresh subprocess stdout verbatim.
That stdout contains the random `TemporaryDirectory` path used for its scratch
JSON files, so two otherwise identical reruns can change the integrated
`result.json` bytes and hash.  This is a tooling reproducibility defect, not a
mathematical discrepancy: the assertion counts and values are unchanged.  The
final release package must canonicalize or omit environment-specific temporary
paths, rerun all three integrated verifiers, and verify byte-stable artifacts
before the clean release gate.  No PDF or claim promotion is permitted while
this gate is open.

## 5. Quantitative normalization audit

Let `x_beta>0` be the unique solution of

```text
x_beta tanh(x_beta) = beta hbar^2/(4 chi theta_Q).
```

The proposed zero-mode lower bound is

```text
delta_beta = theta_Q tanh(x_beta)/x_beta - I3/(2 beta c).
```

Multiplying by `beta` and substituting the defining equation for `x_beta`
shows

```text
delta_beta>0
  iff A0 tanh(x_beta)^2 > I3
  iff tanh(x_beta)>rho
  iff x_beta>x_star
  iff beta>beta_star.
```

Thus `A0>I3` is needed so that `rho<1` and `x_star` is finite.  This algebra
must be rederived in the manuscript and in an independent verifier; the
decimal `I3=0.505462019717326...` must not be treated as a hardcoded proof
oracle.  The integral definition is authoritative, and any numerical value is
only a reproducible enclosure or sanity check.

## 6. Adversarial checks

1. **Rotation-invariance leak -- UPHELD AS A BLOCKER.**  Corollary 3.14 and
   the closest vector phase theorem cannot be imported directly.  P-06 and
   P-09 must remain Q3LOCK-specific proofs.
2. **Long-range order automatically implies multiple DLR states -- UPHELD AS
   FALSE WITHOUT THE PRESSURE STEP.**  The paper must retain the Griffiths
   moment-to-cusp argument and EXP-000781 tangent-state construction.
3. **A zero source slope proves uniqueness -- UPHELD AS FALSE.**  The route is
   one-way; failure of the sufficient inequalities is inconclusive.
4. **Executable PASS proves the analytic theorem -- UPHELD AS FALSE.**  The
   scripts test identities, hypotheses, normalizations, provenance and scope;
   they do not replace the proof of compactness, FKG preservation, reflection
   positivity or limit passage.
5. **Two parity images are automatically pure phases -- UPHELD AS FALSE.**
   Distinct DLR states do not establish extremality, purity, clustering, or
   completeness of the phase set.
6. **Euclidean DLR states are automatically KMS states for one common
   dynamics -- UPHELD AS FALSE.**  No such common dynamics is part of this
   paper.

## 7. Registration decision

An independent Q3LOCK claim must not yet be registered at T6.  The present
package is eligible only for a future bounded T4 registration after this
pre-registration audit and the live EXP-000780--782 reproduction evidence are
attached to the card.  Promotion beyond T4 requires all `UNASSESSED` entries
and P-04 through P-12 proof-text obligations to close, followed by an
independent mathematical audit.

The P2 manuscript folder must be created only after the independent claim card
exists.  Manuscript content review precedes PDF creation.  PDF compilation,
rendering and visual QA are final-stage gates and are intentionally absent
from this document.

## 8. Next action

Close the Q3LOCK-specific continuous-loop FKG and reflection-positivity proof
text, including the finite-grid-to-loop limit passages and the zero-sum source
algebra.  In particular, replace the certificate's unproved total-variation
phrase by the bounded-continuous association argument recorded above.  Only
after those checks should the bounded independent claim be registered with
any remaining external-review gate stated explicitly.
