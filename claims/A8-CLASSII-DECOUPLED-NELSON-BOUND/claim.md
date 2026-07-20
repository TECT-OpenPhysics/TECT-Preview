# A8-CLASSII-DECOUPLED-NELSON-BOUND -- independent-carrier Nelson theorem

**Tier**: T5 PINNED-CLOSURE@INDEPENDENT-DERIVATIVE-PRODUCT-GAUSSIAN
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-20

## Result

Let the A1 production covariance on the fixed torus be (C=A^{-1}), let
(R_\Lambda) be one fixed common real-even A7 regulator family, and put

\[
 M_R=\sup_{\Lambda,k}|r_\Lambda(k)|<\infty.
\]

Take independent production Gaussian copies (Z) and (Y=C^{1/2}\xi_Y).
For a deterministic measurable positive-semidefinite matrix background
(b\in L^2(\mathbb T_L^3;\mathbb R^{6\times6})), define

\[
 G_\Lambda=DR_\Lambda C^{1/2},\qquad
 T_{\Lambda,b}=G_\Lambda^*M_bG_\Lambda,
\]

\[
 Q_{\Lambda,b}(Y)
 ={1\over2}\bigl(
 \langle\xi_Y,T_{\Lambda,b}\xi_Y\rangle
 -\operatorname{Tr}T_{\Lambda,b}\bigr).
\]

Then, for every fixed (p>0),

\[
 \mathbb E_Y e^{-pQ_{\Lambda,b}}
 =\det{}_2(I+pT_{\Lambda,b})^{-1/2},
\]

\[
 0\le \log\mathbb E_Y e^{-pQ_{\Lambda,b}}
 \le {p^2\over4}\|T_{\Lambda,b}\|_{\mathfrak S_2}^2,
\]

and

\[
 \sup_\Lambda\|T_{\Lambda,b}\|_{\mathfrak S_2}^2
 \le {M_R^4S_L\over L^3c_{\rm sym}^2}\|b\|_{L^2}^2.
\]

The last estimate is a spatial-background theorem, not a constant-background
ansatz. It follows from the production (q^{-4}) symbol and

\[
 \sup_q\sum_k
 {1\over\langle k\rangle^2\langle k-q\rangle^2}
 \le \sum_k\langle k\rangle^{-4}<\infty.
\]

## Decoupled product-Gaussian measure

Use the A7 coefficient matrix (B), but evaluate it on the independent value
field (Z_\Lambda=R_\Lambda Z), while (Y_\Lambda=R_\Lambda Y) supplies the
derivatives:

\[
 Q_\Lambda(Z,Y)=Q_{\Lambda,B(Z_\Lambda)}(Y).
\]

The production Class-II matrix is positive definite, so (B(z)\ge0), and

\[
 \|B(z)\|_F\le\beta_B|z|^2,
 \qquad
 \beta_B=12a+48|b|+48c=0.256499999999936.
\]

Together with the positive production sextic, this gives, for every fixed
(p>0),

\[
 \sup_\Lambda\mathbb E_{Z,Y}
 \exp\{-p[U_\Lambda(Z)+Q_\Lambda(Z,Y)]\}<\infty.
\]

For the executable contractive subfamily (M_R=1), the deliberately coarse
certified constants are

~~~text
c_sym                    = 0.108364530587115
S_L upper                = 1752.06849501828
beta_B                   = 0.256499999999936
C_A(1)                   = 36.4264479777321
K_B(1)                   = 0.599144492990436
~~~

For a general fixed admitted family, (C_A(M_R)=M_R^4C_A(1)) and
(K_B(M_R)=M_R^4K_B(1)). No regulator bound is silently set to one in the
analytic statement.

On the common product Gaussian space, the actions converge in probability.
The all-(p) bound gives uniform integrability, so the weights converge in
(L^1), partition functions converge to a strictly positive finite limit,
and normalized product-space densities converge in total variation. Combining
this with (R_\Lambda(Z,Y)\to(Z,Y)) in probability gives full-sequence weak
convergence of the projected Galerkin laws.

## Exact information retained for the physical A7 action

At every finite self-coupled cutoff, whiten
(X_\Lambda=C_\Lambda^{1/2}\xi) and set

\[
 b_\Lambda(\xi)
 =C_\Lambda^{1/2}D^*[B(X_\Lambda)DX_\Lambda].
\]

Then the exact Gaussian-divergence identity is

\[
 2V_\Lambda^{\rm ren}
 =\delta_\gamma b_\Lambda
 =\langle\xi,b_\Lambda\rangle
  -\operatorname{div}_\xi b_\Lambda.
\]

The (DB) trace vanishes because common evenness gives
(D_xC_\Lambda(x,y)|_{y=x}=0); the remaining trace is twice the A7
counterterm. The independent audit checks the full nonlinear finite-dimensional
analogue and includes a parity-breaking negative control. This identity fixes
the correct Boue--Dupuis geometry, but it is not an exponential estimate.

## A7 self-coupling gate

The coefficient and derivative carrier in the physical A7 action are the
same field. Conditioning on (B(X)) therefore does not leave an independent
production Gaussian carrier, and the determinant theorem above cannot be
substituted directly.

One sufficient load-bearing estimate is, uniformly in the cutoff and every
progressive drift (u),

\[
 \mathbb E V_\Lambda^{\rm ren}(X_\Lambda+h_\Lambda(u))
 \ge-\varepsilon\mathbb E\left[
 \int\|u_t\|_2^2\,dt+\|h_\Lambda(u)\|_6^6\right]
 -C_\varepsilon.
\]

An alternative sufficient route is a uniformly bounded positive variation
along an independent-to-self-coupled smart path. Neither sufficient criterion
is proved here, and they are not asserted to be equivalent. The named open
gate is `A7-CLASSII-SELF-COUPLING-INTERPOLATION`.

## Reproduction

~~~powershell
python codes/foundations/a8_classii_decoupled_nelson_verify.py
~~~

Expected:

~~~text
PASS: primary (21/21)
PASS: independent (15/15)
ASSERTS: 54/54
A8-CLASSII-DECOUPLED-NELSON-INTEGRATED-PASS
~~~

The integrated verifier fails closed on the exact authority set and hashes,
PDF review metadata, result schemas, assertion counts, scope firewall, and
tolerance ceilings before it executes either child route.

## Evidence

- `classii_decoupled_nelson_manifest.json`
- `notes/a8-classii-decoupled-nelson-bound-260720-v1.0.tex.txt`
- `notes/a8-classii-decoupled-nelson-bound-260720-v1.0.pdf`
- `../../codes/foundations/a8_classii_decoupled_nelson.py`
- `../../codes/foundations/a8_classii_decoupled_nelson_independent.py`
- `../../codes/foundations/a8_classii_decoupled_nelson_verify.py`
- `runs/2026-07-20-primary-decoupled-nelson/result.json`
- `runs/2026-07-20-independent-decoupled-nelson/result.json`
- `runs/2026-07-20-integrated-decoupled-nelson/result.json`

## Devil's-advocate self-test

1. **VALID-with-mitigation -- the A7 regulator class is not necessarily
   contractive.** The analytic constants carry the required (M_R^4); the
   numeric enclosure is explicitly labeled (M_R=1).
2. **DISMISSED -- the homogeneous (-\Theta(\Lambda^{3/2})) trial by itself
   disproves every Nelson estimate.** It disproves a uniform pathwise lower
   bound. Gaussian trace cancellation is instead encoded by the exact
   (det_2) identity. It does not settle self-coupling.
3. **UPHELD as invalid -- condition on (B(X)) and reuse the independent
   determinant.** The derivative modes are then not an independent Gaussian.
   The two-order scalar negative control catches this model substitution.
4. **DISMISSED -- only constant backgrounds were controlled.** The analytic
   Fourier proof covers arbitrary deterministic spatial PSD (L^2) matrix
   backgrounds; the primary audit also exercises a modulated matrix field.
5. **VALID-with-mitigation -- the rational coefficient can have dangerous
   growth.** At fixed positive floor it has quadratic growth and derivative of
   at most linear growth, while the production sextic absorbs the determinant
   quartic. Floor removal is excluded.
6. **UPHELD -- the Gaussian-divergence identity alone does not exponentiate.**
   It identifies the remaining drift geometry but does not prove the adapted
   drift or smart-path estimate.
7. **UPHELD -- no additional interacting counterterm has been ruled out.**
   If the all-scale self-coupling commutator produces a mass, orientation, or
   vacuum term, it must be registered as a new renormalization condition.
8. **UPHELD as false -- this decoupled measure is the physical full
   three-component Gibbs measure.** It is an independent-carrier product model
   and is kept as a separate claim for exactly that reason.

## Promotion rationale and boundary

T5 is justified only for the pinned independent-carrier theorem: the analytic
determinant, spatial Schatten estimate, sextic absorption, common-space
full-sequence argument, full-(B) divergence check, independent audit, source
hashes, PDF, and one-command reproduction form a closed scoped package.

This claim does not prove the self-coupled A7 Nelson bound, adapted-drift or
smart-path control, a physical full-production Gibbs measure, absence of extra
interacting counterterms, floor removal, infinite volume, a phase transition,
BCC existence or selection, T6, or T7.

## References

- [Boue and Dupuis, variational representation](https://doi.org/10.1214/aop/1022855876)
- [Hariya, unbounded Wiener functionals](https://arxiv.org/abs/1505.02479)
- [Barashkov and Gubinelli, variational method for Phi-four-three](https://arxiv.org/abs/1805.10814)
