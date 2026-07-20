# A9-CLASSII-SMART-PATH-CANCELLATION -- exact reduction of the A7 self-coupling gate

**Tier**: T5 CLOSED@EXACT-INTERPOLATION-AND-NONCENTRAL-FROZEN-SHELL
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-20

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

## Exact residual gate

For the designated dyadic-freezing route, with
(phi_j=P_{\le j}\phi) and
(Delta_jB=B(\phi_j)-B(\phi_{j-1})), the only unclosed increment is

\[
\mathcal C_j=\frac12\int(D\phi_j)^T\Delta_jB\,D\phi_j
-\frac12\int\operatorname{Tr}[\Gamma_{\le j}\Delta_jB].
\]

It is sufficient to prove, uniformly in the cutoff and every tilted law,

\[
\mathbb E_\nu\sum_{j\le J}\mathcal C_j
\ge-\eta H(\nu\mid\gamma_J)
-\eta\mathbb E_\nu\|\phi_J\|_6^6-C_\eta.
\]

This is now registered as
`A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND`.  It remains open.  Unshifted
Gaussian (L^2) shell summability does not imply this all-tilted-laws bound.

## Reproduction

```powershell
python codes/foundations/a9_classii_smart_path_cancellation_verify.py
```

Expected:

```text
PASS: primary (24/24)
PASS: independent (17/17)
ASSERTS: 58/58
A9-CLASSII-SMART-PATH-INTEGRATED-PASS
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
4. **UPHELD -- base-law moments are insufficient.** The open gate is a
   uniform estimate under the interacting tilted laws.
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
   final tilted commutator estimate and hence the self-coupled Nelson bound
   remain open.

## Promotion rationale and boundary

T5 is justified only for the pinned exact interpolation reduction and
noncentral frozen-shell theorem: the finite-cutoff algebra is exact, the
all-cutoff Schatten and dyadic bounds are analytic, two non-importing
executables reproduce the signs and factors, quadrature refinement contracts
the integration-by-parts residual, and negative controls fail when common
evenness is removed.

This claim does not prove the tilted-law commutator form bound, the
self-coupled A7 negative-exponential estimate, a full three-component Gibbs
measure, absence of every possible later counterterm, floor removal,
asymmetric-regulator universality, infinite volume, phase transition, BCC
existence or selection, T6, or T7.

## References

- [Boue and Dupuis, variational representation](https://doi.org/10.1214/aop/1022855876)
- [Barashkov and Gubinelli, variational method for Phi-four-three](https://arxiv.org/abs/1805.10814)
