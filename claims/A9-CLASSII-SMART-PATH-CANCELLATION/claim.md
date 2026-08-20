# A9-CLASSII-SMART-PATH-CANCELLATION -- exact reduction of the A7 self-coupling gate

**Tier**: T5 CLOSED@EXACT-INTERPOLATION-AND-NONCENTRAL-FROZEN-SHELL
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-21

## Result

Let (x,y) be independent cutoff white noises, (X=K_Lambda x),
(G_Lambda=DK_Lambda), and

\[
T(x)=G_Lambda^*M_{B(X)}G_Lambda\ge0.
\]

For (z_s=sx+\sqrt{1-s^2}y), interpolate between A8's independent
derivative carrier at (s=0) and A7's self-coupled carrier at (s=1).  Put
(t=1-s^2), (R_t=(I+ptT)^{-1}), and (S_t=TR_t).  Exact integration of
(y) gives

\[
W_t=-pU-\frac12\log\det{}_2(I+ptT)
+\frac{p(1-t)}2\{\operatorname{Tr}T-x^TS_tx\}.
\]

Writing (T_i=DT(x)[e_i]) and

\[
(a_t)_i=\frac{p^2t^2}{2}\operatorname{Tr}(TR_tT_i)
+\frac{p(1-t)}2
\{\operatorname{Tr}T_i-x^TR_tT_iR_tx\},
\]

Gaussian integration by parts proves

\[
\boxed{
\partial_t\Phi_{Lambda,t}
=\frac p2\mathbb E_{\nu_t}\left[
-p\langle DU,S_tx\rangle
+\langle a_t,S_tx\rangle
+\langle\operatorname{div}S_t,x\rangle\right].}
\]

The apparently divergent traces reduce exactly to Schatten-2 quantities:

\[
\operatorname{Tr}T_i-x^TR_tT_iR_tx
=\operatorname{Tr}[(I-R_t^2)T_i]
-\{x^TR_tT_iR_tx-\operatorname{Tr}(R_tT_iR_t)\},
\]

\[
I-R_t^2=ptS_t(I+R_t).
\]

Common real-even regulation gives (operatorname{div}T=0) and

\[
\|\operatorname{div}S_t\|
\le pt\|S_t\|_{\mathfrak S_2}
\left(\sum_i\|T_i\|_{\mathfrak S_2}^2\right)^{1/2}.
\]

At the fixed production floor, A8's trace-ideal theorem bounds the last sum
uniformly under the base Gaussian law.  Thus the first smart-path derivative
contains no uncancelled trace-class divergence.

## Noncentral frozen-shell theorem

Let (b\ge0) and a derivative source (a) be arbitrary functions measurable
with respect to previously exposed shells.  With

\[
A=M_b^{1/2}G_j,\qquad T=A^*A,\qquad q=M_b^{1/2}a,
\]

\[
Q=\frac12\|q+A\xi_j\|^2-\frac12\operatorname{Tr}T,
\]

one has, for every (p>0),

\[
\begin{aligned}
\log\mathbb E_j e^{-pQ}
={}&\frac12\{p\operatorname{Tr}T-\log\det(I+pT)\}
-\frac p2\|q\|^2\\
&+\frac{p^2}{2}
\langle A^*q,(I+pT)^{-1}A^*q\rangle
\le\frac{p^2}{4}\|T\|_{\mathfrak S_2}^2.
\end{aligned}
\]

The source contribution is nonpositive because
(pA(I+pA^*A)^{-1}A^*\le I).  Equivalently,

\[
\mathbb E_{\nu_j}Q
\ge-\eta H(\nu_j\mid\gamma_j)
-\frac1{4\eta}\|T\|_{\mathfrak S_2}^2.
\]

For a dyadic shell of the production (q^{-4}) covariance,

\[
\|T_{j,b}\|_{\mathfrak S_2}^2
\le C_{\rm sh}(L)M_R^4c_{\rm sym}^{-2}
2^{-j}\|b\|_{L^2}^2.
\]

This proves that every frozen-shell determinant cost is summable and, for
(b=B(z)), quartic in (z), hence absorbable by the production sextic.

## Deterministic and independent shifts

For deterministic (h\in H^2), or random (h) independent of (X_Lambda),
common evenness and exact covariance centering give

\[
\mathbb E_XV_Lambda^{\rm ren}(X_Lambda+h)
=\frac12\sum_i\int
\mathbb E_X[(D_ih)^TB(X_Lambda+h)D_ih]\,dx\ge0.
\]

The unresolved negative mechanism is therefore genuine adapted same-noise
dependence, not an ordinary Cameron-Martin translation.

## Falsified former residual gate

For the designated dyadic-freezing route, with
(phi_j=P_{\le j}\phi) and
(Delta_jB=B(\phi_j)-B(\phi_{j-1})), the only unclosed increment is

\[
\mathcal C_j=\frac12\int(D\phi_j)^T\Delta_jB\,D\phi_j
-\frac12\int\operatorname{Tr}[\Gamma_{\le j}\Delta_jB].
\]

The former designated-route target asked, uniformly in the cutoff and every
tilted law, for

\[
\mathbb E_\nu\sum_{j\le J}\mathcal C_j
\ge-\eta H(\nu\mid\gamma_J)
-\eta\mathbb E_\nu\|\phi_J\|_6^6-C_\eta.
\]

This target is **falsified as stated**.  On the physical scalar ray
\(\Psi=f e_1\), take

\[
g_K=\cos(Kx)+\cos(Ky)-\cos(K(x+y)),\qquad
\phi_j=tK(1+\epsilon g_K)e_1.
\]

The three modes lie in one dyadic annulus and exact Fourier convolution gives

\[
\langle g_K|\nabla g_K|^2\rangle=-K^2,\qquad
\langle g_K^2|\nabla g_K|^2\rangle={5\over2}K^2.
\]

For the covariance-contracted cutoff Gaussian
\(\nu_K=N(h_K,K^{-4}C_J)\) with Cameron--Martin mean,

\[
K^{-6}L^{-3}\mathbb E_\nu\sum_j\mathcal C_j
\longrightarrow-a t^4\epsilon^3(4-5\epsilon),
\]

\[
K^{-6}L^{-3}H(\nu|\gamma_J)
\longrightarrow {3\over2}Yt^2\epsilon^2,\qquad
K^{-6}L^{-3}\mathbb E_\nu\|\phi_J\|_6^6
\longrightarrow t^6M_6(\epsilon).
\]

Thus the displayed bound requires a strictly positive lower threshold

\[
\eta\ge {a\epsilon^3(4-5\epsilon)\over
2\sqrt{((3/2)Y\epsilon^2)M_6(\epsilon)}}.
\]

At the production point and \(\epsilon=0.3\), this threshold is
\(2.4891432\times10^{-4}\), so \(\eta=10^{-4}\) is an explicit
counterexample.  The covariance trace is only \(O(K^3)\) against the
\(O(K^6)\) defect.

## Corrected residual gate

This no-go does not withdraw the positive A9 theorem.  The same witness has
positive covariance-normal frozen source energy with coefficient
\(c_F=4a\epsilon^2\), and

\[
{|\mathcal C_j|\over Q_j^{\rm fr,source}}
\longrightarrow {\epsilon(4-5\epsilon)\over4}
={3\over16}
\quad(\epsilon=0.3).
\]

The first corrected open gate was
`A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND`.  It retained a
fixed fraction of the complete covariance-normal \(Q_j^{\rm fr}\), including
its trace subtraction, and asked to bound only
\(\theta Q_j^{\rm fr}+\mathcal C_j\) with explicit production entropy,
quartic, and sextic budgets.  On the registered ray it supplies the exact
necessary tradeoff
\[
\alpha_c\epsilon_6\ge
{[(c_C-\theta c_F)_+]^2\over4c_Hc_6}.
\]
The value \(\theta=3/16\) neutralises this ray without entropy or sextic
expenditure; it is not an absolute lower bound when positive budgets are
allowed.

The later `A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION` supersedes the first
wording without altering this A9 theorem.  It fixes the determinant trace as
\(\Gamma_j\), proves by a strict-dyadic Blaschke family that the cost-free raw
threshold is sharply \(\theta=1\), and exhibits a common-phase direction with
\(Q_j^{\rm fr}=0\) but a negative cumulative covariance-trace commutator.
Such directions must be entropy-controlled, not excluded. A10 further proves
that the shell sum equals the actual endpoint energy plus a positive past-
energy term, so the naive one-gate composition has the wrong sign. The
`A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION` core is now closed by the
registered A11 true-increment determinant theorem.  The remaining active
core is `A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE`; its source-square
budget must still be proved.  A sharp rectangular-cube independent-
innovation and uniform-`L4` filtration subgate is closed.

## Reproduction

```powershell
python codes/foundations/a9_classii_smart_path_cancellation_verify.py
python codes/foundations/a9_tilted_commutator_nogo_verify.py
```

Expected:

```text
Smart-path regression:
PASS: primary (24/24)
PASS: independent (17/17)
ASSERTS: 58/58
A9-CLASSII-SMART-PATH-INTEGRATED-PASS

No-go addendum:
PASS: primary (24/24)
PASS: independent (17/17)
ASSERTS: 56/56
A9-TILTED-COMMUTATOR-NOGO-INTEGRATED-PASS
```

The verifier fails closed on every authority/source hash, result schema,
assertion count, theorem-boundary phrase, PDF review field, tolerance ceiling,
and cross-route constant before accepting the two child results.  The
independent route does not import the primary route.

## Evidence

- `classii_smart_path_manifest.json`
- `notes/classii-smart-path-cancellation-260720-v1.0.tex.txt`
- `notes/classii-smart-path-cancellation-260720-v1.0.pdf`
- `../../codes/foundations/a9_classii_smart_path_cancellation.py`
- `../../codes/foundations/a9_classii_smart_path_cancellation_independent.py`
- `../../codes/foundations/a9_classii_smart_path_cancellation_verify.py`
- `runs/2026-07-20-primary-smart-path/result.json`
- `runs/2026-07-20-independent-smart-path/result.json`
- `runs/2026-07-20-integrated-smart-path/result.json`
- `tilted_commutator_nogo_manifest.json`
- `notes/classii-tilted-commutator-nogo-260721-v1.0.tex.txt`
- `notes/classii-tilted-commutator-nogo-260721-v1.0.pdf`
- `../../codes/foundations/a9_tilted_commutator_nogo.py`
- `../../codes/foundations/a9_tilted_commutator_nogo_independent.py`
- `../../codes/foundations/a9_tilted_commutator_nogo_verify.py`
- `runs/2026-07-21-primary-tilted-commutator-nogo/result.json`
- `runs/2026-07-21-independent-tilted-commutator-nogo/result.json`
- `runs/2026-07-21-integrated-tilted-commutator-nogo/result.json`

## Devil's-advocate self-test

1. **DISMISSED -- the raw trace proves divergence.** The trace is never
   estimated alone; the exact identities reduce it to a Schatten-2 pairing
   and a centered Hilbert-Schmidt quadratic.
2. **UPHELD as false -- `div T=0` is regulator-independent.** It requires the
   pinned common-even class.  The parity-breaking control produces a nonzero
   correction.
3. **DISMISSED -- the shell theorem ignores the low-frequency derivative
   source.** The noncentral formula retains an arbitrary source and proves its
   net contribution is nonpositive.
4. **UPHELD -- base-law moments are insufficient.** The former all-tilted-law
   commutator-alone gate is now explicitly falsified by a resonant
   covariance-contracted Gaussian tilt with a Cameron--Martin mean.
5. **UPHELD as invalid -- direct Malliavin integration by parts closes the
   Boue-Dupuis drift bound.** It produces a (DB\,D_xH) term not controlled by
   the Cameron-Martin cost.
6. **VALID-with-mitigation -- a later all-scale audit may require another
   counterterm.** None is forced by this first exact reduction, but absence at
   all orders is not claimed.
7. **DISMISSED -- deterministic-shift runaway blocks the route.** Exact
   expectation under every deterministic or independent shift is
   nonnegative.
8. **UPHELD as false -- the physical Gibbs measure is now constructed.** The
   corrected frozen-energy relative estimate and hence the self-coupled
   Nelson bound remain open.
9. **DISMISSED -- the no-go withdraws A9 T5.** The negative term is only the
   coefficient increment after discarding frozen positive energy.  The exact
   determinant, trace cancellation, and frozen-shell theorem are unchanged.
10. **UPHELD as an overclaim -- the corrected relative estimate is proved.**
    This package proves a necessary resonance budget and records a candidate
    closure target, not the all-field estimate.

## Promotion rationale and boundary

T5 is justified only for the pinned exact interpolation reduction and
noncentral frozen-shell theorem: the finite-cutoff algebra is exact, the
all-cutoff Schatten and dyadic bounds are analytic, two non-importing
executables reproduce the signs and factors, quadrature refinement contracts
the integration-by-parts residual, and negative controls fail when common
evenness is removed.

The former commutator-alone infinitesimal bound is falsified, while this
claim's scoped T5 positive theorem is preserved.  This claim does not prove
the corrected frozen-energy relative commutator bound, the self-coupled A7
negative-exponential estimate, a full three-component Gibbs measure, absence
of every possible later counterterm, floor removal, asymmetric-regulator
universality, infinite volume, phase transition, BCC existence or selection,
T6, or T7.

## References

- [Boue and Dupuis, variational representation](https://doi.org/10.1214/aop/1022855876)
- [Barashkov and Gubinelli, variational method for Phi-four-three](https://arxiv.org/abs/1805.10814)
