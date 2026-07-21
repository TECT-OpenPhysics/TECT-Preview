# A12-CLASSII-SOURCE-SQUARE-REDUCTION

## Claim

For the hash-pinned A1 production coefficients and the A7-A11 strict sharp
rectangular-cube filtration, let

\[
u_j=P_{\le j-1}\phi,
\qquad
\ell_j=G_j^*B(u_j)Du_j.
\]

Then

\[
\sum_j\|\ell_j\|_2^2
\le C_{\rm src}\|\phi\|_6^6,
\qquad
C_{\rm src}=\frac{\beta_{\rm op}^2}{c_{\rm sym}}
M_R^2M_6^4Q_6^2.
\]

Here $M_6$ is the Hilbert-valued $L^6$ norm of the strict dyadic sharp-cube
maximal operator and $Q_6$ is the exact-shell-weighted derivative-prefix
square-function norm. Both are finite uniformly in the terminal cutoff.

The separated constant is nevertheless unusable for production absorption:

\[
M_6\ge8,\qquad Q_6\ge8\sqrt3,
\qquad H_6=M_6^4Q_6^2\ge786432,
\]

whereas the source-only target is $H_6<29.62571266025876$.

## Exact production constants

The Pauli/Fierz identities give the sharp six-real operator bound

\[
0\le B(\psi)\le\beta_{\rm op}|\psi|^2I_6,
\qquad
\beta_{\rm op}=4(a+2b+c)=0.0423749999999894.
\]

Positivity is explicit at the production point:

\[
a>0,\qquad c>0,\qquad
ac-b^2=7.031249999996483\times10^{-6}>0.
\]

For shell $j$,

\[
\kappa_j=\frac{2\pi}{L}(N_{j-1}+1),
\qquad
\|G_j^*F\|_2^2
\le\frac{M_R^2}{c_{\rm sym}(1+\kappa_j^2)}\|F\|_2^2.
\]

Thus

\[
\frac{\beta_{\rm op}^2}{c_{\rm sym}}
=0.016570372383568618.
\]

The regulator power is $M_R^2$, not the $M_R^4$ of A9's two-leg
Hilbert-Schmidt term.

## Qualitative harmonic-analysis route

A product de la Vallee Poussin cutoff agrees exactly with the sharp cube on
its inner region. The sharp-minus-smooth remainder has uniformly finite
cube-annular overlap. Random signed remainders and normalized derivative
shells satisfy periodic product-Marcinkiewicz mixed-variation bounds.
Khintchine and scale Young then prove the $M_6$ and $Q_6$ bounds. This does
not assume a multiparameter Carleson theorem.

After the pointwise Pauli/Fierz bound, polarization also produces a six-linear
sharp-cube paraproduct multiplier. Its geometric scale multiplier is bounded
by one and has uniform dyadic face variation. This proves qualitative
boundedness; it does not make the multilinear $L^6$ operator norm one. The
rational fixed-floor $B$ is never treated as band-limited.

## Exact sharp-cube budget obstruction

Boundary modulation turns a centered dyadic interval projection into the
one-dimensional Riesz projection on every fixed finite trigonometric
polynomial. The exact Riesz projection norm on $L^6$ is two. Tensorising the
same witness in three spatial directions gives

\[
M_6\ge2^3=8.
\]

The corresponding single derivative-prefix term retains the three carrier
derivatives, so

\[
Q_6\ge8\sqrt3,
\qquad
H_6=M_6^4Q_6^2\ge3\,8^6=786432.
\]

This is more than 26,545 times the production target. An independent finite
Gaussian-integer polynomial gives the elementary exact countercertificate

\[
H_6\ge184.5403419180373503\ldots,
\]

which already fires the gate without the sharp asymptotic theorem.

The same boundary witness proves that the coefficient-blind scalar six-linear
envelope has norm at least $786432$. Thus merely replacing $M_6^4Q_6^2$ by a
direct paraproduct theorem after

\[
|B(u)Du|\le\beta_{\rm op}|u|^2|Du|
\]

does not repair the budget.

## Surviving exact-B route

Let $\mathcal J$ be the real global-phase complex structure. The embedded
Pauli generators commute with $\mathcal J$, and their frame vectors satisfy

\[
p_A^T\mathcal JX=v_A^T\mathcal JX=0.
\]

Consequently

\[
B(X)\mathcal JX=0.
\]

The large carrier derivative in the no-go witness lies precisely in this null
direction. The actual A11 source is therefore not refuted. A12's coarse route
also discarded the output shell projection on
$B(S_{j-1}\phi)DS_{j-1}\phi$ and the determinant resolvent. The successor must
retain the exact coefficient, its gauge-null structure, and the output shell
before estimating the source.

## Scope and tier

The pinned scope is $L=16$, three complex components in the six-real
convention, `rho_regularizer=1e-12`, a common real-even scalar regulator with
supremum $M_R$, and strict dyadic sharp rectangular cubes. The claim remains
T4: the cutoff-uniform analytic reduction is proved, while its separated and
coefficient-blind scalar production-budget routes are closed negatively. The
exact-B shell-localised source bound and the production sextic reserve remain
open.

## Reproduction

```powershell
python codes/foundations/a12_classii_sharp_cube_budget_obstruction_verify.py
```

Expected:

```text
PASS: primary (26/26)
PASS: independent (19/19)
ASSERTS: 65/65
A12-CLASSII-SOURCE-SQUARE-REDUCTION-INTEGRATED-PASS
PASS: primary (36/36)
PASS: independent (25/25)
ASSERTS: 83/83
A12-CLASSII-SHARP-CUBE-BUDGET-OBSTRUCTION-INTEGRATED-PASS
```

## Evidence

- `classii_source_square_reduction_manifest.json`
- `notes/classii-source-square-reduction-260721-v1.0.tex.txt`
- `notes/classii-source-square-reduction-260721-v1.0.pdf`
- `../../codes/foundations/a12_classii_source_square_reduction.py`
- `../../codes/foundations/a12_classii_source_square_reduction_independent.py`
- `../../codes/foundations/a12_classii_source_square_reduction_verify.py`
- `runs/2026-07-21-primary-source-square/result.json`
- `runs/2026-07-21-independent-source-square/result.json`
- `runs/2026-07-21-integrated-source-square/result.json`
- `classii_sharp_cube_budget_obstruction_manifest.json`
- `notes/classii-sharp-cube-scalar-budget-obstruction-260721-v1.0.tex.txt`
- `notes/classii-sharp-cube-scalar-budget-obstruction-260721-v1.0.pdf`
- `../../codes/foundations/a12_classii_sharp_cube_budget_obstruction.py`
- `../../codes/foundations/a12_classii_sharp_cube_budget_obstruction_independent.py`
- `../../codes/foundations/a12_classii_sharp_cube_budget_obstruction_verify.py`
- `runs/2026-07-21-primary-sharp-cube-obstruction/result.json`
- `runs/2026-07-21-independent-sharp-cube-obstruction/result.json`
- `runs/2026-07-21-integrated-sharp-cube-obstruction/result.json`
- `../../negative-results/registry.md#ng-2026-07-21-a12-sharp-cube-scalar-budget`

## Devil's-advocate

1. **Rational $B$ is not band-limited - DISMISSED.** The qualitative proof
   uses the global pointwise Pauli/Fierz operator bound; it never truncates the
   Fourier support of $B$.
2. **Positivity follows merely from $b>0$ - DISMISSED.** The audit explicitly
   verifies $a,c>0$ and $ac-b^2>0$.
3. **The shell loses $2\pi/L$, a derivative, or covariance factor -
   DISMISSED.** The exact integer boundary is $N_{j-1}+1$, $D^*$ has symbol
   norm $|k|$, and the six-real convention is inherited unchanged.
4. **The source should scale as $M_R^4$ - DISMISSED.** It contains one $G_j^*$
   and its norm is squared, hence $M_R^2$.
5. **Individual projection bounds imply a maximal bound - VALID WITH
   MITIGATION.** They do not. The qualitative proof uses the annular randomized
   product-Marcinkiewicz square-function argument.
6. **A better decimal upper enclosure can meet the target - DISMISSED.** The
   exact lower bound is $786432$, and the finite rational witness already gives
   $184.5403\ldots$, both above $29.6257\ldots$.
7. **The result extends to radial balls or shell ratios approaching one -
   UPHELD.** Neither extension is claimed.
8. **The no-go disproves the actual Class-II source - UPHELD.** It does not.
   The scalar envelope discarded $B(X)\mathcal JX=0$, the output shell, and the
   determinant resolvent. The coefficient-aware problem remains open.
9. **A generic six-linear paraproduct avoids the separated norms -
   DISMISSED.** The same witness gives a coefficient-blind scalar-envelope
   lower bound of $786432$.

## Falsifier

Any failed Fierz, coefficient-positivity, gauge-null, or tangent sharpness
check; violation of the exact shell boundary, $M_R^2$ power, or qualitative
product-Marcinkiewicz hypotheses; failure of the dyadic modulation identity,
exact Riesz norm, finite rational countercertificate, or lower bound
$H_6\ge786432$; treating the coefficient-blind witness as a counterexample to
the exact source; authority hash drift; or any failed primary, independent,
integrated, PDF, or release assertion.

## No-overclaim

This claim closes T-047 only as a negative result for the separated and
coefficient-blind scalar routes. It does not bound the exact-B shell-localised
source, establish a positive production sextic reserve, prove the stabilised
true-increment log-Laplace estimate or A7 Nelson bound, construct an
interacting measure, remove regulators, take infinite volume, prove a phase
transition or BCC selection, or justify T5, T6, or T7.

## History

- 2026-07-21: Registered at T4 with exact Pauli/Fierz and shell reductions;
  primary 26/26, non-importing independent 19/19, integrated 65/65; five-page
  PDF form and visual QA pass.
- 2026-07-21: Closed the separated enclosure gate negatively. Exact dyadic
  Riesz modulation gives $H_6\ge786432$, an independent rational polynomial
  gives $H_6\ge184.540341918\ldots$, and the coefficient-blind scalar
  paraproduct route also fails. The exact-B shell-localised gate replaces it;
  obstruction primary 36/36, independent 25/25, integrated 83/83. Tier remains
  T4.
