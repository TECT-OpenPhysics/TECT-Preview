# Q3LOCK A6--A13 DLR, FKG, reflection, and infrared audit

**Status:** T0 internal proof-text audit; no independent sign-off and no claim-card promotion  
**Date:** 2026-09-07  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Current package:** v0.1.7, fresh audit r8, integrated replay r7  
**PDF:** deferred until content review, literature review, content freeze, hash freeze, and final release review

## 1. Scope and disposition rule

This note audits load-bearing rows A6--A13 of the Q3LOCK manuscript in one
bounded pass.  It compares the displayed DLR, continuous-loop FKG,
reflection-positivity, finite-mesh FSS, Duhamel, and three-dimensional
infrared arguments with the earlier source crosswalks and finite diagnostics.
The purpose is to identify sign, factor, quantifier, topology, and scope
defects before an external mathematics audit.

The result is an **internal consistency finding only**.  A row remains OPEN
unless a qualified independent reviewer supplies a location-specific signed
PASS.  In particular, a source theorem, a finite diagnostic, a successful
replay, or this reread is not an external proof certificate.  The package
remains `T0`, `claim_bearing=false`, `INTERNAL_REVIEW_ONLY`; no paper PDF is
created.

## 2. Evidence and frozen boundaries

The manuscript locations audited here are:

* `sec:dlr-specification`, `eq:dlr-potential-envelope`,
  `eq:one-site-exponential`, `eq:periodic-holder-closure`,
  `eq:dlr-compact-set`, `eq:weighted-tail-direction`,
  `eq:dlr-normalizer-lower`, `eq:kernel-source-lipschitz`, and
  `sec:dlr-source-tangents` (A6--A9);
* `eq:log-supermodular`, `sec:fkg-loop-passage`, and
  `eq:fkg-product-clipping` (A10--A11);
* `eq:hilbert-kernel-positive`, `eq:spatial-reflection-positive`,
  `eq:fss-theorem-input`, `eq:fss-source`, `eq:fss-poisson-energy`,
  `eq:fss-mesh-mgf`, `eq:fss-source-ui`, `eq:duhamel-two-time`,
  `eq:duhamel-poisson`, `eq:infrared-bound`,
  `eq:infrared-continuous-tail`, `eq:infrared-discrete-tail`, and
  `eq:infrared-subtraction` (A12--A13).

The comparison records are the KP vector-hypothesis and source-window audits,
the DLR tangent content note, the three FKG audits, the primary FSS audit, the
FSS-to-loop/infrared audit, and the reflection/infrared content note.  The
finite scripts are diagnostics only:

```text
verification/scripts/q3lock_dlr_tangent_content_audit.py
verification/scripts/q3lock_fkg_mixed_derivative_interpolation_audit.py
verification/scripts/q3lock_fkg_content_audit.py
verification/scripts/q3lock_reflection_infrared_content_audit.py
verification/scripts/q3lock_fss_applicability_audit.py
```

All conclusions below retain the manuscript's limit order: fixed finite
volume and time mesh first, spatial accumulation at fixed source next, and
the source-to-zero tangent only afterwards.  No beta-to-infinity, continuum,
simultaneous `h=h(L)`, or arbitrary-DLR-mixture conclusion is inferred.

## 3. A6--A9: general-vector DLR and source-window passage

### A6. KP hypotheses for the non-radial eight-component potential

The displayed parameter map is internally coherent:

| input | manuscript value | audit finding |
|---|---|---|
| oscillator dimension | `nu=8` | matches the Q3LOCK site field |
| lattice | `Z^3` | satisfies KP lattice regularity |
| residual growth exponent | `r_KP=2` | kept distinct from the physical quadratic coefficient `r<0` |
| quartic lower constant | `A=g/128` | follows from `sum_e q_e^4 >= |q|^4/8` and the two Young absorptions |
| source window | `|h|<=h_0` | all displayed constants are window-uniform, not global in `h` |
| pair interaction | `J_{yz}=c 1_{|y-z|=1}`, `J_0=6c` | finite range; Q3 locking is onsite and is not put into `J` |
| weighted KP interaction | `J_alpha=6c exp(alpha)` | finite and tends to `J_0` as `alpha` decreases to zero |

The residual potential is continuous, quartically confining, and non-radial.
The one-dimensional collective source `h u` does not reduce the field
dimension and does not license KP's scalar order theorems.  The crosswalk
therefore uses only the general-vector DLR existence/compactness input.  No
rotation-invariant vector phase theorem is imported.

The remaining acceptance interface is the exact finite-volume form/core and
Feynman--Kac identification, the imported KP topology, and the statement that
the source-window estimates can be chosen with one common set of constants.
Those are not closed by the parameter table itself.

### A7. Uniform moments and the Holder closure

The manuscript correctly places the finiteness check before the nonlinear
Holder recursion.  For the one-site conditional estimate, the positive
normalizer lower bound `Y_-` is built from the source-window upper envelope,
and the quartic lower envelope supplies an integrable numerator majorant.
The boundary dependence is retained as

```text
exp(theta * sum_z J_yz ||xi_z||_L2^2),
```

rather than being silently discarded.  In the periodic law, the finite
product integral has a positive quartic term at every site, so
`M=E exp(f_y)` is finite before the inequality

```text
M <= exp(C_1) M^t,       t=theta J_0/kappa < 1
```

is divided by `M^t`.  Choosing `theta=kappa/(2J_0)` gives the stated uniform
bound `M<=exp(2C_1)` for the source window and all even `L>=4`.

This order repairs the common circularity in which a Holder recursion is used
to prove the finiteness needed to state the recursion.  The open interfaces
are the exact Gaussian Fernique input, the conditional kernel estimate with
all boundary terms, and independent acceptance of the finite-volume
normalizer/form passage.

### A8. Projective compactness and the tail direction

The countable weights `alpha_k=1/k` are cofinal in the declared projective
topology.  Given summable budgets `epsilon_k`, the moment bounds select
radii `R_k` and the set

```text
K_epsilon = Omega_t intersect intersection_k
            { ||omega||_(alpha_k,sigma) <= R_k }.
```

Markov plus the union bound gives one source-window tail estimate for this
same set.  Compactness uses the stronger, faster-decaying weight at the next
index:

```text
alpha_(k+1) < alpha_k,
sum_{|y|>R} exp(-alpha_k |y|)||omega_y||_L2^2
 <= beta exp(-(alpha_k-alpha_(k+1))R) R_(k+1)^2.
```

The direction is essential.  A bound at a weaker weight cannot control the
tail in a stronger weight; the escaping-amplitude counterexample recorded in
the manuscript is valid.  The diagonal Arzela--Ascoli/local-uniform step and
weighted-tail step together yield convergence in the projective metric, not
merely in one fixed weighted space.

What remains open is not the sign of the tail direction but independent
acceptance of the KP compact embedding, lower-semicontinuity, and the exact
Polish/projective topology used by the source-window DLR sequence.

### A9. Feller kernel, normalizer, and source-to-zero tangent

For a finite region, the displayed coercivity estimate absorbs internal and
boundary bilinear terms into half of the quartic budget.  The positive
normalizer bound is non-circular: a finite product event of bounded Gaussian
loops has probability at least `2^{-n}`, and the action is uniformly bounded
above on that event for `|h|<=h_0` and a compact boundary set.  Hence
`z_(Delta,K)>0` is available before division.

The source difference is only the factor `exp(h X_Delta)`.  The mean-value
bound, the quartic majorant, and the normalizer lower bound yield the displayed
compact-boundary Lipschitz estimate

```text
sup_(xi in K) |pi_Delta^h(f|xi)-pi_Delta^h'(f|xi)|
 <= (2 M_(Delta,K)/z_(Delta,K)) ||f||_infinity |h-h'|.
```

The direct Feller argument replaces finitely many loops and controls the
finite-range boundary pairings; the bounded-continuous determining class then
identifies the full Borel DLR identity.  The source tangent keeps the required
composition order: pressure derivative at positive differentiability points,
spatial DLR accumulation, source-window tightness, uniform kernel comparison,
zero-source Feller passage, and only then removal of the local clip.
The source dictionary has no extra beta:

```text
p_L'(h)=E X_L/V=beta E Q_0,       P_L'(h)=E Q_0/8,
mu_h(Q_0)=8 P_beta'(h).
```

The internal reread found no hidden interchange in this displayed order.
Independent review is still required for the exact KP determining class,
source-window compact-boundary constants, and the unbounded local-observable
limit.  A9 therefore remains OPEN.

## 4. A10--A11: finite association and its loop-limit scope

### A10. Mixed derivatives and finite FKG

For one Q3 edge, the manuscript's exact identity is

```text
-d_x d_y [lambda/4 (x-y)^2 (x^2+y^2)]
 = lambda/4 [(x+y)^2 + 5(x-y)^2] >= 0.
```

Temporal and spatial quadratic difference bonds have the same attractive sign
in the log density; unary quartic, harmonic, counterterm, and source-linear
terms have zero mixed derivative.  Thus the finite time-grid density is
log-supermodular without radiality or internal rotation symmetry.

The conditioning proof is correctly separated from the source citation.  On a
compact product cube, the mixed derivative gives increasing conditional
likelihood ratios; induction gives association; growing cubes and dominated
convergence remove the cutoff for bounded tests.  The finite FKG proposition
is not being used as an infinite-dimensional theorem.

The remaining independent checks are the precise integrability hypotheses for
the chosen FKG formulation and the passage from the mesh density to the exact
finite-volume loop law.

### A11. Interpolation, Borel extension, clips, and selected limits

Periodic polygonal interpolation has nonnegative cell coefficients, including
the wrap cell, so it preserves coordinatewise order.  For bounded continuous
loop tests, weak convergence is applied separately to `F`, `G`, and `F G`;
`F G` need not be increasing for that convergence step.  The subsequent
closed-upper-set argument uses a translation-invariant compatible metric and
the closed pointwise positive cone.  Compact upper subsets plus inner
regularity extend positive correlation to upper Borel sets and then to bounded
increasing Borel functions.

The clip device is also correctly scoped.  Association is first applied to
nonnegative shifted clips.  Fourth moments then give

```text
E |Y Z - clip_R(Y) clip_R(Z)| <= 2 C_4/R^2,
```

so the unbounded coordinate products used in the local graph inequalities
are removed only after a uniform-integrability estimate.  The proof does not
claim that an arbitrary mixture of associated DLR states remains associated;
the two-point negative-covariance counterexample is retained.

The selected spatial and source-tangent limits inherit association only along
the stated weakly convergent sequences.  This is enough for the displayed
finite/selected-state expectation inequalities, but not for all tempered DLR
states.  A11 remains OPEN pending independent acceptance of the projective
cone/Borel approximation and the actual mesh-to-loop and spatial-limit
interfaces.

## 5. A12--A13: reflection, FSS, Duhamel, and the infrared sum

### A12. Hilbert kernel and finite-mesh FSS source map

The local reflection measure uses the physical onsite potential after the
positive-difference convention; no allocated `3c|q|^2` is inserted a second
time.  The crossing kernel

```text
K(v,w)=exp(-c ||v-w||_H^2/2)
```

is bounded and positive definite.  Finite-rank projections reduce it to the
ordinary finite-dimensional Gaussian Fourier identity, and dominated
convergence passes the Gram inequality to the loop Hilbert space.  This is a
valid bounded-kernel argument; it does not posit an identity-covariance
Gaussian measure on an infinite-dimensional Hilbert space.

The reflection result is spatial only.  It is not an OS reconstruction,
real-time positivity, KMS statement, or temporal reflection theorem.

At fixed spatial `L` and time mesh `N`, the rescaled spin is
`s_y=(sqrt(epsilon) x_(y,k))_k` in `R^(8N)`.  The spatial diagonal is `3c`,
the FSS coupling is `J=c`, and the positive quartic gives all quadratic
exponential moments of the prior for that fixed `N`.  The source is typed via
the edge divergence:

```text
eta=t sqrt(epsilon)(f u),
h=G L_sp^(-1) eta,
||h||^2=beta t^2 <f,L_sp^(-1)f>.
```

The theorem is applied only at finite `N`; no mesh-uniform prior constant is
imported.  The normalized collective vector has norm one, so no factor eight
appears.  These checks agree with the primary-source applicability audit.

The open interfaces are the external theorem invocation, the exact
interacting weak loop limit, and the identification of the finite-mesh prior
with the original quantum trace after the earlier Feynman--Kac/form steps.

### A13. Uniform integrability, Duhamel normalization, and nonzero modes

The exact interpolation identity is `X_L(f)(I_N x)=X_(N,L)(f)`.  Weak
convergence is used first for bounded exponential truncations.  Applying the
finite FSS estimate to both signs gives a two-sided exponential bound and
therefore uniform integrability of the source derivatives and second moments.
Passing the unbounded exponential directly through weak convergence would be
invalid; the manuscript does not do that.

With

```text
D_L(y,z)=(1/beta) integral_0^beta C_L(y,z;tau) d tau,
```

time translation gives `Var(X_L(f))=beta^2 <f,D_L f>`.  The finite MGF bound
then gives

```text
<f,D_L f> <= (beta c)^(-1) <f,L_sp^(-1) f>
```

on the zero-sum subspace.  Since the graph eigenvalue is
`2 E(p)`, `E(p)=sum_j(1-cos p_j)`, the displayed nonzero-mode estimate is

```text
0 <= Dhat_L(p) <= 1/(2 beta c E(p)),     p != 0.
```

The constant mode is never inverted.  The continuous and discrete shell
estimates separately show `I_(3,L)->I_3<infinity`; the number of internal
components does not replace the spatial dimension three in this argument.
The resulting subtraction is only

```text
b_L >= D_L(0,0) - I_(3,L)/(2 beta c),
```

and gives no strict positive sign until the independent local/Falk--Bruch
lower bound is supplied.  This is the central nonclaim of A13.

The independent review must check the FSS normalization, the two-time
Duhamel factor, complex Fourier extension, shell bounds, and the order of the
fixed-volume and thermodynamic limits.  A13 remains OPEN.

## 6. Adversarial checks

The following hostile substitutions remain rejected by the current text:

1. identify the KP growth exponent with the physical `r<0`;
2. put the onsite Q3 polynomial into the pair matrix and count it again in
   `J_0`;
3. divide the Holder inequality before proving the periodic exponential
   moment is finite;
4. use the weaker `alpha_(k+1)>alpha_k` direction for a stronger weighted tail;
5. infer a uniform source normalizer lower bound from pointwise positivity
   without a compact-boundary bounded event;
6. pass a source-dependent DLR kernel through weak convergence without first
   removing the source difference uniformly on a compact set;
7. cite a scalar or radial KP phase theorem for the non-radial `R^8` law;
8. reverse the Q3 mixed-derivative sign, use a negative interpolation
   coefficient, or apply FKG directly to an unshifted sign-changing product;
9. assert association for an arbitrary mixture of associated states;
10. use the vertex-source norm instead of the edge Poisson norm in FSS;
11. import prior moments uniform in the time mesh, pass unbounded exponentials
    without truncation/UI, or insert an extra factor of `8` or `beta`;
12. invert the spatial constant mode or infer its positive lower bound from
    the nonzero-mode infrared estimate alone.

No hostile check changes a row to PASS; each only confirms that the manuscript
has kept the corresponding failure mode visible.

## 7. Disposition and next gate

At the internal T0 level, no contradictory sign, factor, source dictionary,
tail direction, branch order, or zero-mode treatment was found in A6--A13.
The result is therefore **advanced as an internal audit, not closed as a
theorem**:

```text
A6 OPEN  A7 OPEN  A8 OPEN  A9 OPEN
A10 OPEN A11 OPEN A12 OPEN A13 OPEN
```

The next gate is a signed independent mathematics review focused on (i) the
KP source-window/projective topology and determining class, (ii) the
continuous-loop FKG and Borel-cone passage, (iii) the FSS theorem invocation
and mesh/UI order, and (iv) the Duhamel/Fourier normalization and zero-mode
boundary.  Literature applicability and all later collective/cusp rows also
remain open.  Content/hash freeze and the first PDF are still final-stage
actions only.

## 8. Explicit nonclaims

This audit does not assert a strict source cusp, positive infrared zero mode,
phase coexistence, DLR multiplicity or classification, extremality, purity,
clustering, a KMS or real-time state, a ground-state phase, spectral gap,
continuum limit, physical vacuum, cosmological interpretation, C6, CP1,
Sector-A/Pre-A closure, Yang--Mills conclusion, theorem-tier promotion,
publication readiness, submission authorization, or a paper PDF.

