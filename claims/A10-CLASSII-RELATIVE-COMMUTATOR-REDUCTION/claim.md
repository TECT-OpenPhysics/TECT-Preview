# A10-CLASSII-RELATIVE-COMMUTATOR-REDUCTION -- exact successor-gate reduction

**Tier**: T4 PROVED-STRUCTURAL-REDUCTION@FIXED-FLOOR-FINITE-CUTOFF
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-21

## Result

Let

\[
x=\phi_{j-1},\qquad \xi_j=\phi_j-\phi_{j-1},\qquad z=\phi_j,
\]

and define the new-shell and cumulative derivative covariances by
\(\Gamma_j\) and \(\Gamma_{\le j}\).  The A9 noncentral determinant fixes
the frozen variable as

\[
Q_j^{\rm fr}=q_{B(x)}(Dz)-t_{\Gamma_j}(B(x)),
\]

not with the cumulative trace.  The coefficient increment is

\[
\mathcal C_j=q_{B(z)-B(x)}(Dz)
-t_{\Gamma_{\le j}}(B(z)-B(x)).
\]

Thus

\[
\begin{aligned}
R_j^\theta:=\theta Q_j^{\rm fr}+\mathcal C_j
={}&q_{B(z)}(Dz)-(1-\theta)q_{B(x)}(Dz)
-t_{\Gamma_{\le j}}(B(z))\\
&+t_{\Gamma_{\le j-1}}(B(x))
+(1-\theta)t_{\Gamma_j}(B(x)).
\end{aligned}
\]

The production Gram structure gives

\[
B(X)\ge0,\qquad
\|B(X)\|_F\le\beta_B|X|^2,
\qquad
\|DB(X)[h]\|_F\le\beta_1|X||h|,
\]

with

\[
\beta_B=0.2564999999999359,
\qquad
\beta_1=1.1429999999997142.
\]

## Sharp raw threshold

Writing \(q_x=q_{B(x)}(Dz)\) and \(q_z=q_{B(z)}(Dz)\), the raw identity is

\[
\theta Q_{j,\rm raw}^{\rm fr}+\mathcal C_j^{\rm raw}
=q_z-(1-\theta)q_x.
\]

The cost-free all-field value is sharply \(\theta=1\), including under a
legitimate hard dyadic split.  For the inner Blaschke factor

\[
F_a(w)=\frac{w-a}{1-aw},\qquad
F_N=-a+(1-a^2)\sum_{n=1}^N a^{n-1}w^n,
\]

take \(x_m=F_me_1\) and \(z_m=F_{2m}e_1\).  Then
\(x_m=P_{\le m}z_m\), the innovation occupies exactly \(m<n\le2m\), and

\[
\frac{q_z}{q_x}=O_a(m^2a^{2m})\longrightarrow0.
\]

Therefore the negative raw commutator-to-frozen ratio tends to one.  The
previous scalar-triad value \(3/16\) is not a global threshold.

## Exact covariance-trace defect

The load-bearing A6/A7 normalization is

\[
\Gamma_{\le j}=\frac12\operatorname{realify}(D_{\rm complex})
=\operatorname{realify}\!\left(\frac1V\sum_{k\in\Lambda_{\le j}}|k|^2A(k)^{-1}\right),
\]

because \(D_{\rm complex}\) contains the factor
\(\mathbb E[\Psi_k\Psi_k^\dagger]=2A(k)^{-1}\).  The two executable routes
pin this factor and test their finite-cutoff plane-wave slopes against the A6
asymptotic coefficient. Here \(\Lambda_{\le j}\) is the declared momentum
cutoff set; the closed filtration below takes it to be the rectangular cube
\(\{k_n:\max_a|n_a|\le2^j\}\).

For a top-shell common-phase plane wave

\[
x=0,\qquad z(r)=Ae^{ik\cdot r}e_1,
\]

one has \(Q_j^{\rm fr}=0\) and \(J_A=K_A=0\), hence zero raw Class-II
energy.  Nevertheless \(B(z)\ne0\) and

\[
\mathcal C_j=-t_{\Gamma_{\le j}}(B(z))<0.
\]

The former instruction to exclude zero-frozen negative directions is false.
The correct task is to classify and entropy-control them.  In particular, a
uniform relative estimate requires \(\alpha_c>0\): with no entropy term, the
trace loss grows as \(-NA^2\) while fixed quartic and sextic terms remain
independent of \(N\).  This family does not refute a positive-entropy bound,
because its trace-to-Cameron--Martin ratio decays as \(K^{-3}\).

## Necessary triad budget

The registered scalar triad still gives the exact necessary condition

\[
\alpha_c\epsilon_6\ge
\frac{[(c_C-\theta c_F)_+]^2}{4c_Hc_6}.
\]

At \(\epsilon=0.3\), \(\theta=3/16\) neutralises that one ray without extra
budget.  Over its declared family the cost-free supremum is \(7/36\).  Neither
number controls the Blaschke family.

## Exact multiscale action mismatch

For the actual A7 endpoint energy

\[
V_j=q_{B(\phi_j)}(D\phi_j)-t_{\Gamma_{\le j}}(B(\phi_j)),
\]

the shell variables obey

\[
Q_j^{\rm fr}+\mathcal C_j
=V_j-V_{j-1}+q_{B(\phi_{j-1})}(D\phi_{j-1}).
\]

Thus, with \(V_0=0\),

\[
\sum_{j\le J}(Q_j^{\rm fr}+\mathcal C_j)=V_J+E_J,
\qquad E_J:=\sum_{j\le J}q_{B(\phi_{j-1})}(D\phi_{j-1})\ge0.
\]

This falsifies the naive composition: the actual energy is the shell sum
minus \(E_J\). Closing `A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION`
requires either a true-increment determinant theorem or an upper form bound

\[
\mathbb E_\nu E_J\le\alpha_dH(\nu\mid\gamma_J)
+\epsilon_d\mathbb E_\nu\|\phi_J\|_6^6
+K_d\mathbb E_\nu\|\phi_J\|_4^4+C_d.
\]

No such estimate is claimed here.

## Conditional Nelson composition

The filtration prerequisite is closed for the sharp rectangular-cube route
\(N_j=2^j\). Disjoint Fourier blocks are independent, and the tensor product
of the one-dimensional M. Riesz partial-sum bound gives a cutoff-uniform
\(L^4\) projection norm. This closes the scoped
`A10-CLASSII-DYADIC-FILTRATION-REALISATION` subgate; it does not cover
overlapping smooth Littlewood--Paley increments.

Assume both the action upper form bound above and the still-open relative form
bound. If

\[
C_{\rm fr}=C_{\rm sh}(L)M_R^4c_{\rm sym}^{-2}\beta_B^2
C_{\rm LP,4}^4S_{\rm dy},
\qquad
K_f=\frac{(1-\theta)^2C_{\rm fr}}{4\alpha_f},
\]

and

\[
\alpha=\alpha_f+\alpha_c+\alpha_d,\qquad
B_6=\frac\gamma6-\epsilon_6-\epsilon_d,\qquad
A_4=\left[K_\theta+K_f+K_d-\frac\lambda4\right]_+,
\]

then \(B_6>0\) and some \(p>1\) with \(p\alpha<1\) imply

\[
\log\mathbb E_{\gamma_J}e^{-pS_J}
\le p(C_\theta+C_d)+\frac{4pL^3A_4^3}{27B_6^2}
\]

uniformly in the cutoff. This is an implication, not closure: both
`A10-CLASSII-MULTISCALE-ACTION-DECOMPOSITION` and
`A10-CLASSII-STABILISED-RELATIVE-LOG-LAPLACE` remain open.

## Reproduction

```powershell
python codes/foundations/a10_classii_relative_structural_reduction_verify.py
```

Expected:

```text
PASS: primary (47/47)
PASS: independent (34/34)
ASSERTS: 101/101
A10-CLASSII-RELATIVE-STRUCTURAL-REDUCTION-INTEGRATED-PASS
```

The verifier rehashes all authority, code, note, and PDF files before running
the two child routes.  The independent route does not import the primary.

## Evidence

- `classii_relative_structural_reduction_manifest.json`
- `notes/classii-relative-structural-reduction-260721-v1.0.tex.txt`
- `notes/classii-relative-structural-reduction-260721-v1.0.pdf`
- `../../codes/foundations/a10_classii_relative_structural_reduction.py`
- `../../codes/foundations/a10_classii_relative_structural_reduction_independent.py`
- `../../codes/foundations/a10_classii_relative_structural_reduction_verify.py`
- `runs/2026-07-21-primary-relative-structural-reduction/result.json`
- `runs/2026-07-21-independent-relative-structural-reduction/result.json`
- `runs/2026-07-21-integrated-relative-structural-reduction/result.json`

## Devil's-advocate self-test

1. **UPHELD as a repaired defect -- the frozen trace was ambiguous.** The A9
   determinant requires \(\Gamma_j\); the manifest and verifier now reject
   \(\Gamma_{\le j}\) in that position.
2. **UPHELD as a repaired numerical defect -- the six-real covariance was
   halved twice.** Pre-freeze adversarial review found that both executable
   routes omitted the load-bearing complex factor two.  The corrected routes
   implement the displayed A6/A7 convention and fail if the finite plane-wave
   slope misses the pinned asymptotic coefficient.
3. **UPHELD -- \(3/16\) is global.** The strict-dyadic Blaschke family proves
   the raw loss ratio tends to one.
4. **UPHELD as false -- zero frozen energy excludes a negative commutator.**
   The common-phase plane wave is an exact covariance-trace counterexample.
5. **DISMISSED -- the plane wave disproves any entropy estimate.** Its
   trace-to-shift-entropy ratio is \(O(K^{-3})\); it proves only that a positive
   entropy coefficient is necessary.
6. **VALID-with-mitigation -- A9's determinant automatically closes the new
   gate.** For \(\theta<1\), the conditional coefficient is indefinite on
   unbounded past fields.  Endpoint self-coupling or a proved stabiliser
   allocation must remain in the argument.
7. **UPHELD as false -- the shell sum reconstructs the actual A7 action with
   a harmless positive remainder.** The exact identity has the opposite
   consequence: \(V_J\) is the shell sum minus \(E_J\), so a quantitative
   upper form bound or a true-increment theorem is separately required.
8. **UPHELD as an overclaim -- the conditional composition constructs the
   measure.** Both action recovery and stabilised relative log-Laplace remain open, so
   no density convergence, partition limit, or tightness is claimed.
9. **VALID-with-mitigation -- smooth overlapping shells provide independent
   innovations.** They need not. The sharp rectangular-cube route is closed
   by independent Fourier blocks and a tensorised M. Riesz bound; smooth
   overlapping increments remain outside that lemma.
10. **UPHELD as an overclaim -- T5, T6, or T7 is justified.** The current tier
   is T4.  Operator reproduction may later review the same scoped result for
   T5 but cannot close the missing antecedent.

## Promotion rationale and boundary

T4 is justified because the algebraic identities, strict-dyadic construction,
plane-wave trace defect, positive-entropy necessity, exact action mismatch,
sharp-cube filtration lemma, and conditional composition theorem are analytic
and are reproduced by two non-importing routes. The proof PDF passes form,
zero-overfull, and visual QA.

This claim does not prove a production-valid upper form bound on the past
energy mismatch, the all-field relative form or log-Laplace bound,
the self-coupled A7 Nelson estimate, an interacting full three-component Gibbs
measure, density convergence, tightness, an optimal positive-budget global
\(\theta\), floor removal, asymmetric-regulator universality, infinite volume,
phase transition, BCC existence or selection, T6, or T7.

## References

- [Boue and Dupuis, variational representation](https://doi.org/10.1214/aop/1022855876)
- [Barashkov and Gubinelli, variational method for Phi-four-three](https://arxiv.org/abs/1805.10814)
