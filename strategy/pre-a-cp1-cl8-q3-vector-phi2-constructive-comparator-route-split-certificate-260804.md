# Pre-A CL8 Q3 vector P(Phi)2 constructive-comparator route-split certificate

**Candidate:** `PA-CP1-CL8-Q3-VECTOR-PHI2-CONSTRUCTIVE-COMPARATOR-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-Q3-PHI2-NORMALIZABILITY-L1-DENSITY-AND-CONFIGURATION-CHARACTERISTIC-LIMIT-WITH-RP-AND-SELECTION-NOGOS`  
**Date:** 2026-08-04  
**Scope:** claim-nonbearing T0 exact external-theorem instantiation and derived
finite-Euclidean-torus comparator; no C6, CP1 or Pre-A advancement

## 1. Verdict

The exact eight-component Q3 polynomial passes an established multivariate
`P(Phi)_2` normalizability theorem.  On a fixed Euclidean two-torus, with a
positive massive product Gaussian covariance, the resulting Wick interaction
has a normalizable limiting density.  The proof of the external theorem also
gives the cutoff-uniform exponential estimate needed to derive full-sequence
`L1` convergence of the common-Gaussian normalized densities.

For every fixed finite spatial Fourier label space, the sharp-cutoff time-zero
configuration fields have a Gaussian trace limit.  The density estimate gives
uniform interacting second moments, hence full-sequence convergence and
uniform equicontinuity of their configuration characteristic functions.

This is a real constructive advance over the abstract subnet in EXP-000765,
but it is not yet the canonical CL8 state.  It covers only the commuting
time-zero configuration subgroup.  The induced `N=1` projected interacting
sharp-cutoff law is not reflection positive, as an exact three-point witness
shows.  This does not decide the lifted full-field or limiting local measure.
The external theorem does not construct canonical momentum, an OS
Hamiltonian, a KMS or ground state, a Feynman--Kac identification with the CL8
spatial regulator, a Hadamard state, a physical vacuum, or a phase transition.

<a id="section-2-authorities-and-boundary"></a>
## 2. Authorities and prior-art boundary

The external authority is:

- Hirotatsu Nagoji, *Construction of the Gibbs measures associated with
  Euclidean quantum field theory with various polynomial interactions in the
  Wick renormalizable regime*, arXiv:2305.19583v2, 2024-12-13,
  <https://arxiv.org/pdf/2305.19583>.

The package uses only:

1. Theorem 1.7(i), which is Theorem 1.1 specialized to `alpha=d/2`;
2. Theorem 1.7(i) applied to the scaled polynomial `2F`, combined with the
   standard conditional-expectation identity for nested Wick polynomials; and
3. Proposition A.1, which gives almost-sure convergence of the Wick monomials.

Multivariate `P(Phi)_2`, Wick monomials, uniform integrability, Gaussian trace
limits and OS reconstruction are established prior art.  TECT does not claim a
new general theorem in any of those subjects.  The repository-specific content
is:

- the exact substitution of the Q3 polynomial into the external hypotheses;
- the elementary `L1` density corollary from the scaled external estimate;
- the time-zero configuration-characteristic consequence;
- the precise Wick-convention dictionary; and
- the three explicit route separations in Sections 6, 9 and 10.

The external paper explicitly constructs a Euclidean measure.  It does not
prove reflection positivity, OS reconstruction, Hamiltonian equivalence,
canonical momentum, KMS or ground-state identification.  Those facts may be
true after a different construction, but they are not inputs here.

<a id="section-3-exact-q3-polynomial"></a>
## 3. Exact Q3 polynomial and sign convention

Let the Q3 vertices be `e in {0,1}^3`, and let `e~f` denote the twelve cube
edges.  Write

```
L_Q3 = 3 I - A_Q3,
K_int = m_int I + eta_int L_Q3,
```

and

\[
 W_4(x)={g\over4}\sum_e x_e^4
 +{\lambda\over4}\sum_{e\sim f}
 (x_e-x_f)^2(x_e^2+x_f^2),                 \tag{3.1}
\]

with `g>0` and `lambda>=0`.  The local polynomial is

\[
 P_{\rm int}(x)={1\over2}x^T K_{\rm int}x+W_4(x).          \tag{3.2}
\]

Nagoji writes the Euclidean density as `exp(integral :F:)`.  The required
substitution is therefore

\[
 F=-P_{\rm int}.                            \tag{3.3}
\]

This sign is load-bearing.  Substituting `F=+P_int` would be the focusing sign
and would reverse the large-field control.

The already proved onsite sum-of-squares identity gives

\[
 \sum_e x_e^4\ge {|x|^4\over8},
 \qquad
 W_4(x)\ge {g\over32}|x|^4.                \tag{3.4}
\]

No positivity of `K_int` is required.  Its negative directions have only
quadratic growth and are dominated by (3.4).

The covariance (4.1) already contributes the positive base quadratic
`m0^2 I`.  Therefore `K_int` is an interaction residual.  After all
`chi,c,hbar`, coordinate and field rescalings have been declared, matching a
target continuum quadratic requires `K_int=K_target-m0^2 I`.  The domination
proof permits this arbitrary residual, but this package does not prove the
rescaling or the canonical CL8 regulator bridge.

<a id="section-4-external-hypotheses"></a>
## 4. Exact instantiation of Theorem 1.7(i)

Use the massive eight-component product Gaussian on the Euclidean two-torus,

\[
 \mu=\mu_{m_0}^{\otimes8},\qquad
 \operatorname{Cov}(\mu_{m_0})=(m_0^2-\Delta_{T^2})^{-1},
 \qquad m_0>0.                              \tag{4.1}
\]

Remark 1.3 of the external authority replaces the theorem's mass budget
`m<1/2` by `m<m0^2/2`.  We choose `m=0`.

The degree is `k=4`, while `d=2` and `alpha=1`.  Thus

\[
 {k-1\over2k}d={3\over4}<1={d\over2}.       \tag{4.2}
\]

Let `A` be the finite multi-index support of `F`, and

\[
 A^-:=\{\beta:\beta<\xi\text{ componentwise for some }\xi\in A\}.
\]

Since every `xi in A` has total degree at most four and `beta<xi` is strict,

\[
 |\beta|\le3\quad(\beta\in A^-).            \tag{4.3}
\]

At `alpha=d/2`, the external threshold is identically one.  Choose

\[
 q(\beta)={5\over4}>1.                      \tag{4.4}
\]

Then `q(beta)|beta|<=15/4<4`.  Because `A^-` is finite, there is a finite
constant `C_A` such that

\[
 \sum_{\beta\in A^-}|x^\beta|^{5/4}
 \le C_A(1+|x|^{15/4}).                     \tag{4.5}
\]

Using (3.3)--(3.4),

\[
 F(x)+\sum_{\beta\in A^-}|x^\beta|^{5/4}
 \le-{g\over32}|x|^4
 +C_A(1+|x|^{15/4})
 +{1\over2}\|K_{\rm int}\|_{\rm op}|x|^2.  \tag{4.6}
\]

The right side tends to negative infinity as `|x|->infinity`, so its supremum
is finite.  Equations (4.2), (4.4) and (4.6) are exactly the hypotheses of
Theorem 1.7(i).  The limiting Wick weight is therefore integrable and defines
a probability measure on the fixed Euclidean two-torus.

This is an instantiation of an external theorem, not a TECT proof of that
theorem.

The formal maximal support of the expanded Q3 polynomial has 64 indices.  It
is the actual support when `lambda!=0`, `eta_int!=0`, and
`m_int+3 eta_int!=0`.  Direct enumeration of its lower envelope gives 61
indices in `A^-`, with degree counts

\[
 \#\{|\beta|=0,1,2,3\}=1,8,20,32.           \tag{4.7}
\]

The count is an executable maximal-coverage fixture, not an additional theorem
hypothesis.  For example, `m_int=-3 eta_int` cancels the eight diagonal
quadratic monomials and leaves 56 actual indices.  Coefficient cancellations
only shrink the support, so (4.3)--(4.6) remain valid.  In particular, when
`lambda>0` the quartic support already generates the displayed 61-element
lower envelope.  The condition `g>0` is essential: with `g=0`, the Q3 edge
quartic vanishes on the constant-species ray and cannot dominate the lower
monomial envelope.

<a id="section-5-l1-density-corollary"></a>
## 5. Full-sequence common-Gaussian L1 density convergence

Let `P_N` be the simultaneous Euclidean sharp Fourier projector used by the
external authority, and set

\[
 R_N=\int_{T^2}:F(P_N\Phi):\,dz.             \tag{5.1}
\]

Proposition A.1 gives convergence of every Wick monomial in a negative
Sobolev space and almost surely.  Integration over the fixed torus is a
continuous test, hence

\[
 R_N\longrightarrow R\quad\mu\text{-almost surely}.       \tag{5.2}
\]

Now apply the same hypothesis calculation to `2F`.  Its support is unchanged
and its leading negative quartic is stronger.  Wick ordering is linear, so

\[
 R_N^{2F}=2R_N^F.                            \tag{5.3}
\]

Let `G_N` be the sigma-field of the retained Gaussian Fourier modes.  For
every finite `M>=N`, the variance-additive Hermite generating function gives

\[
 \mathbb E_\mu[R_M\mid G_N]=R_N.             \tag{5.4}
\]

The proof of Proposition A.1, in particular its uniform high-moment estimate
(A.3), makes the almost-sure convergence in (5.2) uniformly integrable and
hence gives `R_M->R` in `L1(mu)`.  Conditional expectation is continuous in
`L1`, so taking `M->infinity` in (5.4) proves the terminal identity

\[
 R_N=\mathbb E_\mu[R\mid G_N].               \tag{5.5}
\]

Theorem 1.7(i) applied to `2F` gives `E exp(2R)<infinity`.  Conditional Jensen
then yields

\[
 \sup_N\mathbb E_\mu e^{2R_N}
 \le\mathbb E_\mu e^{2R}<\infty.             \tag{5.6}
\]

The proof of the external Theorem 1.1 applied to `2F`, in particular its
equation (4.1), supplies an independent direct cutoff-uniform
partition-function route.  The martingale route is used here because it
exposes the exact logical dependency.

Equations (5.2)--(5.6) make `{exp(R_N)}` uniformly integrable.  Vitali
convergence gives

\[
 \|e^{R_N}-e^R\|_{L^1(\mu)}\longrightarrow0. \tag{5.7}
\]

Therefore

\[
 Z_N:=\mathbb E_\mu e^{R_N}\to
 Z:=\mathbb E_\mu e^R>0.                    \tag{5.8}
\]

Every positive-total-degree multivariate Wick monomial in the interaction has
zero Gaussian mean.  Indeed, it factorizes over the independent components,
and at least one one-variable Hermite factor has degree one through four and
zero Gaussian expectation.  Hence `E R_N=0`, and Jensen also gives the useful
uniform floor `Z_N>=1`.

The lifted common-space densities

\[
 \rho_N={e^{R_N}\over Z_N},\qquad
 \rho={e^R\over Z}                          \tag{5.9}
\]

satisfy

\[
 \|\rho_N-\rho\|_{L^1(\mu)}\longrightarrow0.\tag{5.10}
\]

This is total variation on one common Gaussian distribution space.  It is not
a total-variation claim between differently embedded finite-dimensional laws.

<a id="section-6-time-zero-configuration"></a>
## 6. Time-zero configuration characteristic functions

Work on a `2pi`-periodic Euclidean time circle and spatial circle; harmless
period rescalings only modify positive coefficients.  Let `f` be a real
spatial test function with Fourier support `|k|<=K`.  The sharp-cutoff
time-zero field is

\[
 Q_N(f)=\sum_{k^2+n^2\le N^2}
 {\widehat f(-k)\,\xi_{n,k}\over
  \sqrt{m_0^2+n^2+k^2}},                    \tag{6.1}
\]

with the standard reality condition.  Its Gaussian `L2` limit `Q(f)` exists
because, for fixed `K`,

\[
 \mathbb E_\mu|Q_N(f)-Q(f)|^2
 =\sum_{|k|\le K}|\widehat f(k)|^2
 \sum_{n^2+k^2>N^2}{1\over m_0^2+n^2+k^2}
 \longrightarrow0.                          \tag{6.2}
\]

Indeed, if `N>K` and `M=floor(sqrt(N^2-K^2))`, the temporal tail is bounded by
`2/M` up to the fixed Fourier normalization.  The convergence is uniform on
bounded subsets of the finite-dimensional label space.

Applying Section 5 to `2F` also gives a uniform `L2(mu)` bound for `rho_N`;
the convergence of `Z_N` gives a uniform positive denominator.  Since a
centered Gaussian satisfies `E Q_N(f)^4=3(E Q_N(f)^2)^2`, Cauchy--Schwarz
gives

\[
 \mathbb E_{\rho_N\mu}|Q_N(f)|^2
 \le\|\rho_N\|_{L^2(\mu)}
    [\mathbb E_\mu Q_N(f)^4]^{1/2}
 \le C_K\|f\|^2.                            \tag{6.3}
\]

Consequently,

\[
 |1-\mathbb E_{\rho_N\mu}e^{iQ_N(f)}|
 \le [\mathbb E_{\rho_N\mu}|Q_N(f)|^2]^{1/2}
 \le\sqrt{C_K}\|f\|.                       \tag{6.4}
\]

This is uniform equicontinuity at the configuration-Weyl identity.  Finally,
split

\[
 \begin{split}
 |\mathbb E_\mu[\rho_Ne^{iQ_N(f)}]
 -\mathbb E_\mu[\rho e^{iQ(f)}]|
 &\le\|\rho_N-\rho\|_1\\
 &\quad+\mathbb E_\mu[\rho|e^{iQ_N(f)}-e^{iQ(f)}|].
 \end{split}                                 \tag{6.5}
\]

The first term vanishes by (5.10).  The second vanishes by (6.2),
`|e^{iu}-e^{iv}|<=|u-v|`, and Holder with `rho in L2(mu)`.  Hence the
configuration characteristics converge along the full sequence.

This does not construct the full canonical Weyl algebra.  In particular, a
sharp-time derivative has divergent free variance and cannot simply be named
the canonical momentum.  Momentum and the CCR require reflection-positive
Hamiltonian reconstruction or an independent canonical limit.

There is also a finite-dimensional exact obstruction.  With `[Q,P]=i`, let

\[
 \psi_0(x)=\pi^{-1/4}e^{-x^2/2},\qquad
 \psi_1=e^{iQ^2/2}\psi_0.                   \tag{6.6}
\]

The two vectors have the identical position distribution and hence the same
configuration characteristic `exp(-t^2/4)`.  But if `U=e^{iQ^2/2}`, then
`U^*PU=P+Q`, so

\[
 \operatorname{Var}_{\psi_0}P={1\over2},
 \qquad
 \operatorname{Var}_{\psi_1}P=1.            \tag{6.7}
\]

Thus configuration characteristics alone do not identify a full Weyl state.
This proves
`NG-2026-08-04-PRE-A-CP1-CL8-TIME-ZERO-CONFIGURATION-ONLY-FULL-WEYL-STATE`.

<a id="section-7-wick-dictionary"></a>
## 7. Wick-convention dictionary

The external authority Wick-orders the whole polynomial.  EXP-000765
Wick-orders `W4` and leaves the renormalized quadratic ordinary.  For a common
diagonal coincidence covariance `C`,

\[
 :{1\over2}x^TK_{\rm int}x:_C
 ={1\over2}x^TK_{\rm int}x-{C\over2}\operatorname{Tr}K_{\rm int}. \tag{7.1}
\]

Thus

\[
 :P_{\rm int}:_C={1\over2}x^TK_{\rm int}x+:W_4:_C
          -{C\over2}\operatorname{Tr}K_{\rm int}.         \tag{7.2}
\]

The difference is a scalar and cancels from every normalized finite-cutoff
probability density.  It cannot be discarded from an absolute energy,
vacuum-energy or below-empty-space comparison.

If the common diagonal covariance changes from `C` to `C+D`, the Q3 Wick
ledger gives

\[
 \delta K(C+D)-\delta K(C)
 =-3D[(g+\lambda)I+\lambda L_{Q3}].          \tag{7.3}
\]

Preserving the raw quadratic polynomial therefore requires

\[
 K_{C+D}=K_C+3D[(g+\lambda)I+\lambda L_{Q3}],              \tag{7.4}
\]

up to an additive scalar.  Formula (7.4) types the finite scheme translation.
It does not prove that a finite-temperature Euclidean covariance, an
infinite-time vacuum covariance and the canonical CL8 lattice covariance are
the same state or regulator.

<a id="section-8-regulator-boundary"></a>
## 8. Regulator and state boundary

The comparator uses a simultaneous two-dimensional Euclidean Fourier cutoff.
The current CL8 construction uses a spatial Hamiltonian regulator and a
canonical pair `(q,p)`.  Equality of the limiting local polynomial is not an
intertwiner between these regulators.

A canonical bridge must still prove at least:

1. a time-local or transfer-matrix approximation with reflection positivity;
2. a Feynman--Kac identity between that approximation and the declared CL8
   finite spatial Hamiltonians;
3. convergence of the canonical momentum and the full Weyl CCR, not only the
   configuration subgroup;
4. compatibility with the natural low-mode embeddings and history-cut
   anchors; and
5. either a fixed-`beta` KMS interpretation or a separately controlled
   `beta->infinity` ground-state limit.

The fixed Euclidean time circle is a thermal geometry.  It does not itself
construct a vacuum.  A fixed spatial circle also cannot prove a thermodynamic
phase transition.

<a id="section-9-reflection-positivity-nogo"></a>
## 9. N=1 projected interacting sharp-cutoff reflection-positivity no-go

Let `E_1=Ran P_1`, `gamma_1=(P_1)_# mu`, and

\[
 \nu_1(d\phi)=Z_1^{-1}e^{R_1(\phi)}\gamma_1(d\phi)
              =(P_1)_\#(\rho_1\mu)(d\phi).                \tag{9.1}
\]

Thus `nu_1` is the induced projected interacting law, not the lifted law
`rho_1 mu` on the full Gaussian field.  The Gaussian `gamma_1` is
nondegenerate on the finite-dimensional coefficient space `E_1`, and `R_1`
is a finite real polynomial.  Hence `nu_1` is equivalent to `gamma_1` and has
full support.  Its second moments are finite; this follows, for example, from
the `2F` estimate and Cauchy--Schwarz.  The projector, Gaussian law and
integrated Wick polynomial are invariant under Euclidean-time translations,
reflection, and global sign.

For any one component, spatial averaging leaves at `N=1`

\[
 X(t)=x_0+ze^{it}+\overline z e^{-it}.                       \tag{9.2}
\]

Time-translation invariance forces `E[x_0z]=E[z^2]=0`.
Consequently,

\[
 \mathbb E_{\nu_1}[X(s)X(t)]=b_0+2b_1\cos(s-t),
 \qquad b_1=\mathbb E_{\nu_1}|z|^2>0.                       \tag{9.3}
\]

Strict positivity of `b_1` follows from full support: an open coefficient set
with `|z|>epsilon` has positive `gamma_1` and hence positive `nu_1` mass.
For the projected Gaussian reference, the same formula holds with
`b_1=1/(m_0^2+1)>0`, up to its positive Fourier normalization.

Choose positive times and real weights

\[
 (t_1,t_2,t_3)=\left({\pi\over6},{\pi\over3},{\pi\over2}\right),
 \qquad
 (w_1,w_2,w_3)=(1,-\sqrt3,\sqrt3-1).                         \tag{9.4}
\]

They satisfy

\[
 \sum_iw_i=0,
 \quad\sum_iw_i\cos t_i=0,
 \quad\sum_iw_i\sin t_i=\sqrt3-2.                           \tag{9.5}
\]

For `A=sum_i w_i X(t_i)` and reflection through zero,

\[
 \mathbb E_{\nu_1}[(\theta A)A]
 =\sum_{i,j}w_iw_j\mathbb E_{\nu_1}[X(-t_i)X(t_j)]
 =-2b_1(2-\sqrt3)^2<0.                                      \tag{9.6}
\]

Smooth positive-time mollifiers around the three times retain the strict
sign.  Therefore the `N=1` projected interacting simultaneous sharp-cutoff
law is not reflection positive.  This proves the projected-law reading of
`NG-2026-08-04-PRE-A-CP1-CL8-FULL-EUCLIDEAN-SHARP-CUTOFF-REFLECTION-POSITIVITY`.

This result does not prove that the lifted law `rho_1 mu` is
non-reflection-positive on the full field's positive-time local algebra:
`P_1` is nonlocal in Euclidean time, so the pullback of the witness is not a
positive-time-local full-field observable.  It also does not determine
reflection positivity for `N>1`, for the limiting local measure, or for a
time-local, spatial-only, heat-kernel, or transfer-matrix regulator.

<a id="section-10-selection-nogo"></a>
## 10. Normalizability-only state-selection no-go

Theorem 1.7(i) accepts every real `K_int`, not one preferred quadratic input.
At the zero-mode cutoff, compare `K_int=0` and `K_int=I` while holding
`m0,g,lambda` fixed.  Both finite densities are strictly positive and
normalizable.  If `V=int_(T^2)1 dz` is the torus measure, their normalized
density ratio has the form

\[
 {\rho_I(x)\over\rho_0(x)}
 =c\,e^{-V|x|^2/2},                           \tag{10.1}
\]

where `c>0` is a scalar normalizer.  The repository convention uses normalized
Haar measure, so `V=1`; for every positive volume the ratio is nonconstant.
The states are therefore distinct.  Both inputs also satisfy (4.6).

Thus coercivity plus constructive normalizability cannot select a unique
canonical or physical state.  This proves
`NG-2026-08-04-PRE-A-CP1-CL8-CONSTRUCTIVE-NORMALIZABILITY-ONLY-PHYSICAL-STATE-SELECTION`.

The no-go does not reject a state selected after fixing a Hamiltonian, beta,
ground criterion, boundary condition, KMS condition, energy reference, or
another physical rule.

<a id="section-11-input-output-ledger"></a>
## 11. Input/output ledger

### Inputs

- the exact Q3 polynomial and coercive SOS from EXP-000765;
- `g>0`, `lambda>=0`, arbitrary real `m_int,eta_int`;
- a declared massive product covariance with `m0>0` on a fixed Euclidean
  two-torus;
- Nagoji Theorem 1.7(i), Proposition A.1, and Wick-martingale conditioning; and
- ordinary Vitali, Holder, Gaussian fourth-moment and Fourier-tail arguments.

### Derived

- exact satisfaction of the multivariate `P(Phi)_2` normalizability criterion;
- existence of the fixed-torus limiting Wick probability density;
- full-sequence `L1` convergence of common-Gaussian normalized densities;
- a time-zero configuration Gaussian trace;
- uniform finite-mode configuration-characteristic equicontinuity;
- full-sequence configuration-characteristic convergence;
- an exact configuration-only/full-Weyl counterexample;
- the same-covariance whole-polynomial/W4-only Wick dictionary;
- an `N=1` projected interacting-law reflection-positivity counterexample; and
- a normalizability-only state-selection counterexample.

### Not derived

- reflection positivity of the limiting measure;
- OS reconstruction or Lorentzian continuation;
- a canonical CL8 Feynman--Kac/regulator equivalence;
- canonical momentum or a full phase-space Weyl state;
- fixed-`beta` KMS identification or a `beta->infinity` ground state;
- an interacting Hadamard state;
- a thermodynamic limit or phase transition;
- the original three-dimensional Q3 parent;
- a physical vacuum or below-empty-space comparison; or
- C0, N1--N5, C6, CP1 or Pre-A completion.

<a id="section-12-adversarial-review"></a>
## 12. Adversarial review

1. **Wrong density sign? DISMISSED.**  The external convention is `exp(R^F)`,
   so Section 3 explicitly uses `F=-P_int`.
2. **The Q3 edge term could spoil coercivity? DISMISSED.**  It is a sum of
   `(x_e-x_f)^2(x_e^2+x_f^2)>=0`; onsite coercivity alone gives (3.4).
3. **An indefinite `K_int` invalidates the theorem? DISMISSED.**  Its growth is
   quadratic and (4.6) is quartically negative.
4. **`A^-` can contain degree four? DISMISSED.**  Componentwise strict
   inequality lowers total degree by at least one.
5. **`q=5/4` fails the alpha=d/2 threshold? DISMISSED.**  The threshold is one
   and `5/4>1`; also `(5/4)3<4`.
6. **The theorem statement at `F` alone gives cutoff `L1` convergence? UPHELD
   AS FALSE.**  Section 5 applies the theorem to `2F`, uses the Wick-martingale
   conditional identity and Jensen, and only then uses Vitali.
7. **Scaling `F` changes the support or Wick relation? DISMISSED.**  For
   nonzero scale two, the support is unchanged and Wick ordering is linear.
8. **Total variation compares different finite-dimensional supports? UPHELD
   AS FALSE.**  The claim is only for densities lifted to the common Gaussian
   distribution space.
9. **A distribution has an automatic time-zero restriction? UPHELD AS
   FALSE.**  Section 6 constructs only the spatially smeared trace by an
   explicit convergent covariance sum.
10. **Configuration convergence gives canonical momentum? UPHELD AS FALSE.**
    The sharp-time derivative diverges; equations (6.6)--(6.7) also give two
    full states with the same configuration characteristic and different
    momentum variance.
11. **Commutation of the cutoff with reflection proves positivity? UPHELD AS
    FALSE.**  Equation (9.6) is an exact negative reflection form for the
    projected interacting law.
12. **The counterexample refutes the continuum local measure? UPHELD AS AN
    OVERCLAIM.**  It refutes only the induced `N=1` projected law; the lifted
    full-field law, higher projected cutoffs and local limit remain undecided.
13. **Whole-polynomial and W4-only Wick schemes disagree physically? DISMISSED
    at fixed covariance for normalized states.**  Their difference is the
    scalar (7.2).  Absolute energy remains incomparable.
14. **Normalizability selects the physical state? UPHELD AS FALSE.**  The
    explicit `K_int=0,I` zero-mode densities are distinct.
15. **Finite Euclidean time proves a vacuum? UPHELD AS FALSE.**  A time circle
    is thermal; the infinite-time ground limit is separate.
16. **A fixed torus proves a phase transition? UPHELD AS FALSE.**  No
    thermodynamic limit or competing infinite-volume states are constructed.
17. **OS reconstruction is now available? UPHELD AS FALSE.**  Reflection
    positivity and the remaining OS hypotheses have not been proved for this
    comparator.
18. **This advances C6 or completes Pre-A? UPHELD AS FALSE.**  The claim card
    is unchanged and the manifest firewalls those booleans.
19. **Nonzero `lambda` and `eta_int` always give 64 support indices? UPHELD AS
    FALSE.**  If `m_int=-3 eta_int`, the eight diagonal quadratic coefficients
    cancel and the actual support has 56 indices.  The 64/61 enumeration is a
    maximal formal fixture; smaller support preserves the degree bound.
20. **The finite Hermite identity automatically identifies its terminal? UPHELD
    AS INCOMPLETE WITHOUT A LIMIT STEP.**  Section 5 records the uniform
    high-moment estimate, `L1` convergence, and continuity of conditional
    expectation before asserting `E[R|G_N]=R_N`.
21. **The zero-mode ratio is volume-free? UPHELD AS FALSE.**  Its exponent is
    `-V|x|^2/2`; normalized Haar gives `V=1`, and nonconstancy survives every
    positive volume.

<a id="section-13-verification"></a>
## 13. Verification

The primary verifier must independently enumerate the maximal Q3 support and
`A^-`, check the diagonal-coefficient cancellation sentinel, exact exponent
margins and coercivity identities, evaluate Gaussian expectations of every
Wick Hermite degree one through four, check the terminal-passage ledger,
finite temporal tails and Gaussian moment implications, derive the Wick
translation, and evaluate the negative fixtures.

The independent verifier must not import the primary module.  It must build
the cube by bit masks, use exact rational/symbolic arithmetic for every shared
oracle, independently center Wick degrees one through four, construct the
projected-law reflection witness from the trigonometric moments, and check
mutation sentinels for the sign, exponent and reflection form.

The integrated verifier must rerun both children, compare independently named
oracles, verify stored-artifact freshness and all formal records, and preserve
the unchanged C6 status.

<a id="section-14-next-gate"></a>
## 14. Next gate

The next gate is
`PA-CP1-CL8-TIME-LOCAL-REFLECTION-POSITIVE-REGULATOR-AND-CANONICAL-FEYNMAN-KAC-BRIDGE`.

The shortest positive route is to replace the simultaneous temporal Fourier
cutoff by a time-local transfer-matrix or spatial-only approximation, prove
reflection positivity at finite cutoff, and identify its semigroup with the
declared finite CL8 Hamiltonian through Feynman--Kac.  Only after that bridge
can the configuration limit be promoted to a full canonical Weyl/KMS state.
The `beta->infinity` ground-state limit, the one-dimensional-to-three-
dimensional parent, and the physical reference remain separate gates.
