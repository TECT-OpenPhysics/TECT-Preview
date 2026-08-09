# Pre-A interacting regulator-compatible state route split certificate

**Candidate:** `PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-STATE-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-LOW-MODE-GROUND-ENTANGLEMENT-ALL-BETA-PROJECTIVITY-AND-Q3-WICK-COUNTERTERM-OBSTRUCTIONS`  
**Authority:** claim-nonbearing T0 exact route split  
**Claim context:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Exploration:** `EXP-000764`

## 1. Verdict and boundary

The registered interacting CL8 ground states are not exactly projective under
the natural shared-low-Fourier-mode tensor factor.  The fine pure ground is
entangled between retained and added modes, so its retained density is mixed
and cannot equal the coarse pure ground.

The registered trace-norm zero-temperature limits then exclude exact
same-`beta` Gibbs projectivity on every sufficiently low-temperature tail and,
in particular, exclude one exact family covering all `beta>0`.  Every fine
normal density still has an exact normal low-mode pullback.  A pulled-back fine
Gibbs density is exactly Gibbs for its Hamiltonian of mean force, not
automatically for the inherited coarse CL8 Hamiltonian.

A separate calculation shows that common-diagonal Gaussian Wick ordering of
the Q3 quartic interaction generates a quadratic `L_Q3` counterterm.  For
`lambda>0`, scalar mass and scalar energy counterterms alone cannot absorb it.

These are two narrow route obstructions and one positive mean-force
replacement.  They do not exclude a newly renormalized approximate family or
prove an interacting continuum state.

<a id="section-2-authorities-and-prior-art"></a>
## 2. Authorities and prior-art boundary

Immediate repository inputs are:

- `PA-CP1-ST8-Q3LOCK-v0` for the Q3 quartic polynomial;
- `PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0` for the
  finite-regulator simple positive ground and Gibbs states;
- `PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0`
  for fixed-regulator cut anchors and normal-state transport; and
- `PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0` for the
  free comparator and centered Gaussian route split.

Schmidt factorization, reduced density matrices, positivity-improving
Schrodinger semigroups, Fourier tensor splittings, Hamiltonians of mean force,
Wick ordering, tadpole counterterms, harmonic sums, and constructive
`P(phi)_2` renormalization are established mathematics.  No world-first or new
general theorem is claimed.  The repository contribution is the exact CL8/Q3
convention-level composition and gate audit.

<a id="section-3-natural-low-high-split"></a>
## 3. Natural real-Fourier low/high split

Let the coarse circle have even `M>=4` nodes and spacing `a=L/M`.  Its strict
refinement has

\[
 N=2M,
 \qquad b={L\over N}={a\over2}.                             \tag{3.1}
\]

For each Q3 species, take the real orthonormal Fourier basis on the `N`-node
circle.  The natural `M`-dimensional retained space consists of the zero mode,
the cosine/sine pairs `1<=n<M/2`, and the fine cosine at `n=M/2`.  The last
quadrature corresponds to the coarse self-conjugate Nyquist oscillator, but
its real-mode normalization is different.  Let the retained space's Euclidean
orthogonal complement be the added space.  It contains the fine Nyquist vector
`(-1)^j`.

The real Fourier transform and registered canonical scale are symplectic and
unitarily implemented.  For all eight species,

\[
 \mathcal H_N\simeq
 \mathcal H_{\rm ret}\otimes\mathcal H_{\rm add},
 \qquad
 \iota(A)=A\otimes I.                                      \tag{3.2}
\]

For zero and non-Nyquist shared modes, identify the continuum-normalized
canonical generators.  For the exceptional coarse Nyquist oscillator, exact
sample matching requires the canonical squeeze

\[
 \iota(\Phi^M_{M/2})=\sqrt2\,\Phi^N_{M/2},
 \qquad
 \iota(\Pi^M_{M/2})={1\over\sqrt2}\Pi^N_{M/2}.              \tag{3.3}
\]

Equivalently, on phase-space points `Phi_f=Phi_c/sqrt(2)` and
`Pi_f=sqrt(2)Pi_c`.  Equation (3.3) preserves the CCR and is unitarily
implemented by the one-oscillator squeeze.  Thus the typed embedding is
`iota(A)=U_sq A U_sq^* tensor I` on that factor, with the identity on the
other retained modes.  This does not assert that the two interacting
Hamiltonians intertwine.  Purity versus mixedness below is invariant under
this fixed unitary identification.

<a id="section-4-purity-factorization-lemma"></a>
## 4. Purity and factorization lemma

Let `Psi_N` be the normalized fine ground.  The registered positivity theorem
makes it smooth and strictly positive.  For a bipartite pure vector,

\[
 \operatorname{Tr}_{\rm add}|\Psi_N\rangle\langle\Psi_N|
 \text{ is pure}
 \quad\Longleftrightarrow\quad
 \Psi_N(X,Y)=F(X)G(Y).                                     \tag{4.1}
\]

The fine kinetic operator separates after the orthogonal transformation:

\[
 T_N=T_X+T_Y.                                               \tag{4.2}
\]

If the positive ground factored, its Schrodinger equation with
`T_X=-kappa_N Delta_X` and `T_Y=-kappa_N Delta_Y` would give

\[
 U_N(X,Y)=E_N
 +\kappa_N{\Delta_XF(X)\over F(X)}
 +\kappa_N{\Delta_YG(Y)\over G(Y)}.                        \tag{4.3}
\]

The right side is a retained-only function plus an added-only function.  Thus
every mixed retained/added derivative of a product-ground potential must
vanish.

<a id="section-5-collective-uniform-nyquist-witness"></a>
## 5. Exact collective uniform/Nyquist witness

On the fine circle choose the collective Q3 plane

\[
 q_{j,e}={X+(-1)^jY\over\sqrt L}
 \qquad\text{for every species }e.                          \tag{5.1}
\]

`X` is the retained collective spatial zero mode and `Y` is the added
collective fine Nyquist mode.  Every Q3 lock difference vanishes identically.
Directly summing all eight species and all `N` sites with weight `b/8` gives

\[
 U_N(X,Y)=
 {r\over2}(X^2+Y^2)+{2c\over b^2}Y^2
 +{g\over4L}(X^4+6X^2Y^2+Y^4).                            \tag{5.2}
\]

Therefore

\[
 \boxed{
 \partial_X^2\partial_Y^2U_N={6g\over L}>0}.               \tag{5.3}
\]

The witness is independent of `N`, `r`, and `lambda`.  It survives throughout
the admitted `g>0`, `lambda>=0` domain.  The fine Nyquist is deliberately an
added coordinate, so there is no Nyquist convention ambiguity.

The exact rational hostile fixture `M=4`, `N=8`, `L=4`, `b=1/2`, `r=-1`,
`c=g=1` reads

\[
 U=-{X^2\over2}+{15Y^2\over2}
 +{X^4+Y^4\over16}+{3X^2Y^2\over8},
 \qquad
 \partial_X^2\partial_Y^2U={3\over2}.                     \tag{5.4}
\]

The scripts use this small fixture only as an oracle after deriving (5.2).

<a id="section-6-ground-projectivity-no-go"></a>
## 6. Natural interacting-ground projectivity no-go

### Theorem 6.1

Under the tensorization (3.2),

\[
 \boxed{
 \operatorname{Tr}_{\rm add}P_{0,N}\ne P_{0,M}}.           \tag{6.1}
\]

### Proof

If equality held, the fine pure ground would have a pure retained marginal.
Equation (4.1) would make the fine ground a product.  Equations (4.2)--(4.3)
would make the potential additive across the retained/added variables.  The
nonzero exact mixed derivative (5.3) contradicts additivity.  Hence the fine
ground is entangled, its retained marginal is mixed, and (6.1) follows. `QED`

This proves
`NG-2026-08-04-PRE-A-CP1-CL8-NATURAL-LOW-MODE-INTERACTING-GROUND-PROJECTIVITY`.
It does not exclude approximate consistency, a dressed embedding, a
completely positive coarse-graining, or a new renormalized state family.

<a id="section-7-gibbs-and-mean-force"></a>
## 7. Gibbs tail and the exact mean-force substitute

For every fixed regulator, the registered theorem gives

\[
 \rho_{s,\beta}\longrightarrow P_{0,s}
 \quad\text{in trace norm as }\beta\to\infty.               \tag{7.1}
\]

Partial trace is trace-norm contractive.  Thus

\[
 \operatorname{Tr}_{\rm add}\rho_{N,\beta}
 \longrightarrow\operatorname{Tr}_{\rm add}P_{0,N},
 \qquad
 \rho_{M,\beta}\longrightarrow P_{0,M}.                   \tag{7.2}
\]

The two limits differ by (6.1).  Exact same-`beta` equality is therefore false
for all sufficiently large `beta`, and cannot hold as one family for every
`beta>0`.

There is also a quantitative form.  Put

\[
 \eta=1-\operatorname{Tr}[(P_{0,M}\otimes I)P_{0,N}]>0,
 \qquad
 \epsilon_s(\beta)=\|\rho_{s,\beta}-P_{0,s}\|_1.           \tag{7.3}
\]

Then

\[
 \left\|\rho_{M,\beta}
 -\operatorname{Tr}_{\rm add}\rho_{N,\beta}\right\|_1
 \ge2\max\{0,\eta-\epsilon_M(\beta)-\epsilon_N(\beta)\}.
                                                                    \tag{7.4}
\]

To display that tail, let

\[
 R_s(\beta)=\sum_{n\ge1}e^{-\beta(E_{s,n}-E_{s,0})},
 \qquad \Delta_s=E_{s,1}-E_{s,0}>0.                         \tag{7.5}
\]

For any `beta_0>0`, put

\[
 \beta_*=\beta_0+\max_{s=M,N}{1\over\Delta_s}
 \left[\log{8R_s(\beta_0)\over\eta}\right]_+.             \tag{7.6}
\]

The registered spectral tail estimate gives `epsilon_s(beta)<=eta/4` for
`beta>=beta_*`, and (7.4) is then at least `eta`.  This argument does not exclude one isolated finite `beta` or a cutoff-dependent `beta_N`.

The positive exact substitute is the normal pullback.  Define

\[
 A_\beta=\operatorname{Tr}_{\rm add}e^{-\beta H_N},
 \qquad
 \sigma_\beta={A_\beta\over\operatorname{Tr}A_\beta}.       \tag{7.7}
\]

The heat density is faithful.  For every nonzero retained vector `u` and any
orthonormal added basis `(e_k)`, at least one positive term in
`sum_k <u tensor e_k, exp(-beta H_N) u tensor e_k>` is nonzero.  Hence
`A_beta` has trivial kernel, so its logarithm is well-defined as a possibly
unbounded self-adjoint operator.

and, up to an additive scalar,

\[
 H_{N\to M}^{\rm mf}(\beta)
 =-\beta^{-1}\log A_\beta.                                \tag{7.8}
\]

`sigma_beta` is exactly Gibbs for this Hamiltonian of mean force.  Equality
with the inherited coarse Gibbs state holds exactly only if

\[
 H_{N\to M}^{\rm mf}(\beta)
 =H_M-\beta^{-1}\log(Z_N/Z_M)I.                            \tag{7.9}
\]

The mean-force Hamiltonian is generally cutoff dependent, `beta` dependent,
nonlocal, and outside the bare CL8 polynomial family.  Restriction therefore
supplies a valid state, not inherited-Hamiltonian projectivity or an automatic
KMS theorem.  KMS pullback would additionally require an equivariant dynamics
embedding; (5.3) shows that the retained algebra is not invariant under the
fine interacting dynamics.

<a id="section-8-history-cut-consequence"></a>
## 8. Flat-cut consequence

The registered fixed-regulator cut densities are

\[
 \rho_{a,C}^{[n]}
 =\Gamma_{a,C}^{[n]*}\rho_{a,n}\Gamma_{a,C}^{[n]}.          \tag{8.1}
\]

Choose corresponding flat Cauchy reference cuts at the two regulators.  The
parent theorem supplies each fixed-regulator anchor `Gamma_M` and `Gamma_N`; it
does not itself register an inter-regulator cut square.  Conditionally, suppose
a proposed cut monomorphism `j_C` is required to obey

\[
 j_C(\Gamma_M^*A\Gamma_M)
 =\Gamma_N^*\iota(A)\Gamma_N                              \tag{8.2}
\]

for every coarse bulk observable `A`.  Exact anchored state compatibility at
this reference cut would then reduce to (6.1), so a family anchored to the
registered ground projectors cannot satisfy (8.2) exactly.  The same
conditional conclusion holds for a same-`beta` family covering all
temperatures.

This does not undo the exact fixed-`a` re-slicing and physical-step transport
theorems.

<a id="section-9-common-diagonal-wick-calculus"></a>
## 9. Common-diagonal Wick calculus

To expose the minimum counterterm content of one standard renormalized route,
declare a positive-mass centered Gaussian reference with local covariance

\[
 \mathbb E(q_eq_f)=C\delta_{ef},
 \qquad C>0,                                                \tag{9.1}
\]

and define

\[
 :P:_C=
 \exp\left[-{C\over2}\sum_e\partial_{q_e}^2\right]P.       \tag{9.2}
\]

Then

\[
 :q_e^4:_C=q_e^4-6Cq_e^2+3C^2.                             \tag{9.3}
\]

For one Q3 edge let `P(a,b)=(a-b)^2(a^2+b^2)`.  Exact
contraction gives

\[
 \boxed{
 :P(a,b):_C
 =P(a,b)-8C(a^2+b^2)+12Cab+8C^2}.                          \tag{9.4}
\]

The independent verifier reconstructs (9.4) by a monomial Laplacian rather
than importing the displayed formula.

<a id="section-10-q3-counterterm-matrix"></a>
## 10. Exact Q3 counterterm matrix

Let

\[
 W_4(q)={g\over4}\sum_eq_e^4
 +{\lambda\over4}\sum_{e\sim f}P(q_e,q_f).                 \tag{10.1}
\]

For the cube adjacency `A` and Laplacian `L_Q3=3I-A`, summing (9.3)--(9.4)
gives

\[
 :W_4:_C
 =W_4+{1\over2}q^T\delta K(C)q+6C^2(g+4\lambda),          \tag{10.2}
\]

where

\[
 \boxed{
 \delta K(C)
 =-3C[(g+\lambda)I+\lambda L_{Q3}]}.                       \tag{10.3}
\]

On Walsh level `s=0,1,2,3`,

\[
 \delta K_s(C)=-3C(g+\lambda+2s\lambda),                  \tag{10.4}
\]

with multiplicities `1,3,3,1`.  A raw-basis implementation of this Wick scheme
requires a scalar shift `delta r=-3C(g+lambda)`, a separate Q3-Laplacian
coefficient `delta eta=-3C lambda`, and the scalar energy convention in
(10.2).

For `lambda C>0`, `L_Q3` is nonzero and not proportional to `I`.  Scalar mass
and scalar energy counterterms alone cannot reproduce (10.3).  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-SCALAR-MASS-ONLY-Q3-WICK-RENORMALIZATION`.

The conclusion is typed to the declared common-diagonal reference.  It is not
a uniqueness theorem for every renormalization scheme and does not exclude an
enlarged Q3-invariant quadratic basis or `lambda=0`.

<a id="section-11-logarithmic-reference-growth"></a>
## 11. Logarithmic centered covariance growth

For positive reference stiffness `nu_ref`, define

\[
 C_N={\hbar\over2\chi L}
 \sum_{n\in I_N}{1\over\omega_{N,n}},
 \qquad
 \omega_{N,n}^2
 ={\nu_{\rm ref}+c\widehat k_b(n)^2\over\chi}.             \tag{11.1}
\]

Throughout the Brillouin zone,

\[
 {2\over\pi}|k_n|
 \le|\widehat k_b(n)|\le|k_n|.                             \tag{11.2}
\]

The sine chord bound and `sin x<=x` therefore compare every sufficiently large
nonzero term with `1/|n|`.  Constants `A,B,D>0`, independent of `N`, obey

\[
 A\log N-D\le C_N\le B\log N+D.                            \tag{11.3}
\]

Hence `C_N` diverges logarithmically.  The shift between Walsh level `s` and
the singlet is

\[
 \delta K_s(C_N)-\delta K_0(C_N)=-6s\lambda C_N.            \tag{11.4}
\]

For `lambda>0`, one scalar cutoff mass cannot hold all four Walsh stiffness
levels fixed.  This identifies a necessary counterterm direction, not a proof
that the enlarged theory converges.

<a id="section-12-open-positive-route"></a>
## 12. Open positive route

The surviving route must replace exact equality of the existing finite ground
states by a renormalized approximate construction.  It must provide:

1. an explicit Q3-matrix and scalar-energy counterterm Hamiltonian;
2. uniform lower stability and local form bounds;
3. cutoff-uniform smeared field moments and local-energy estimates;
4. equicontinuity of fixed-observable Weyl characteristic functions;
5. state compactness and identification on a declared algebra;
6. asymptotic coarse/fine compatibility with every typed cut decoder;
7. convergence or equivariance of the dynamics if a KMS claim is made; and
8. a separate ultraviolet two-point analysis for any Hadamard claim.

Weak-star compactness alone may produce a nonregular or nonnormal subnet.  It
does not supply the missing estimates or identify a physical state.

<a id="section-13-input-output-ledger"></a>
## 13. Input/output ledger

### Inputs

- the inserted one-dimensional centered CL8 regulator family;
- `L,chi,c,g,lambda,r,hbar` and a strict even refinement;
- the registered ground or same-beta Gibbs criterion;
- the natural low-mode type-I tensor implementation; and
- a positive-mass common-diagonal Gaussian Wick reference.

### Derived

- the exact retained/added tensor split;
- fine-ground entanglement and natural ground-projectivity failure;
- the quantitative low-temperature Gibbs obstruction;
- exact normal pullback and Hamiltonian-of-mean-force representation;
- the flat-cut consequence;
- the Q3 Wick counterterm matrix and scalar-mass-only no-go; and
- logarithmic reference covariance growth.

### Not derived

- a renormalized interacting state family or uniform estimate;
- sufficiency of the Q3 matrix counterterm;
- a continuum or Hadamard interacting state;
- a physical vacuum, below-empty-space sign, or phase transition;
- physical light, Lorentzian signature, time, `hbar`, gravity, or a horizon;
- the original three-dimensional Q3 parent.

<a id="section-14-adversarial-review"></a>
## 14. Adversarial review

1. **Pure marginal without factorization? DISMISSED.**  A bipartite pure vector
   has a pure marginal exactly at Schmidt rank one.
2. **Ground nodes invalidate division? DISMISSED.**  The registered ground is
   smooth and strictly positive.
3. **Kinetic low/high coupling? DISMISSED.**  The real Fourier map is
   orthogonal, so the fine Laplacian separates.
4. **Nyquist convention artifact? DISMISSED.**  The fine Nyquist is
   intentionally added and orthogonal to the retained zero mode.  The separate
   retained `n=M/2` quadrature is matched to the coarse self-conjugate Nyquist
   oscillator by the explicit symplectic squeeze (3.3).
5. **Q3 lock cancellation? DISMISSED.**  It vanishes on the collective plane;
   the positive coefficient is `6g/L`.
6. **No ground projectivity means no state limit? UPHELD AS AN OVERCLAIM.**
   Approximate and newly renormalized families remain open.
7. **All-beta argument excludes an isolated beta? UPHELD AS AN OVERCLAIM.**
   It excludes the low-temperature tail, not an accidental isolated point.
8. **Gibbs restriction stays inherited KMS? DISMISSED.**  That needs an
   equivariant algebra embedding; the quartic cross term prevents invariance.
9. **Scalar mass absorbs the Wick term? DISMISSED for `lambda>0`.**  `L_Q3`
   is linearly independent of `I`.
10. **Wick ledger is scheme universal? UPHELD AS AN OVERCLAIM.**  It is exact
    for the declared common-diagonal reference only.
11. **Counterterm matrix proves convergence? UPHELD AS A MISSING THEOREM.**
    Uniform stability, moments, energy, compactness, and cut squares remain.
12. **Counterterm energy is a physical reference? DISMISSED.**  Removing
    cutoff dependence does not identify physical empty space.

<a id="section-15-verification"></a>
## 15. Verification

Run:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_interacting_regulator_compatible_state_route_split_verify.py
```

The primary route differentiates the collective CL8 plane and Gaussian
contractions symbolically, checks the Q3 Walsh matrix, and audits centered
covariance growth and scope.  The independent route imports no SymPy or NumPy
and reconstructs the polynomial Laplacian, cube graph, exact `Fraction`
fixture, purity control, and covariance sequence.  The integrated verifier
reruns both, checks stored artifacts and formal records, and enforces unchanged
C6 status.

<a id="section-16-next-gate"></a>
## 16. Next gate

The parent
`PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY`
remains open.  Its exact successor is

`PA-CP1-CL8-Q3-MATRIX-COUNTERTERM-INTERACTING-STATE-COMPACTNESS-AND-CUT-SQUARE`.

Until that candidate constructs the enlarged Hamiltonian, proves uniform
estimates, and closes a typed cut square, the interacting continuum/Hadamard
state, three-dimensional parent, physical state/reference, protected cone,
C0, N1--N5, C6 advancement, CP1, and Pre-A remain open.
