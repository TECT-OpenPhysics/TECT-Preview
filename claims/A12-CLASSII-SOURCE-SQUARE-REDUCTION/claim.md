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

Here (M_6) is the Hilbert-valued (L^6) norm of the strict dyadic
sharp-cube maximal operator and (Q_6) is the exact-shell-weighted derivative
prefix square-function norm. Both are finite uniformly in the terminal cutoff.

## Exact production constants

The Pauli/Fierz identities give the sharp six-real operator bound

\[
0\le B(\psi)\le\beta_{\rm op}|\psi|^2I_6,
\qquad
\beta_{\rm op}=4(a+2b+c)=0.0423749999999894.
\]

For shell (j),

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

The regulator power is (M_R^2), not the (M_R^4) of A9's two-leg
Hilbert-Schmidt term.

## Harmonic-analysis route

A product de la Vallee Poussin cutoff agrees exactly with the sharp cube on
its inner region. The sharp-minus-smooth remainder has uniformly finite
cube-annular overlap. Random signed remainders and normalized derivative
shells satisfy periodic product-Marcinkiewicz mixed-variation bounds.
Khintchine and scale Young then prove the (M_6) and (Q_6) bounds. This does
not assume a multiparameter Carleson theorem.

After the pointwise Pauli/Fierz bound, polarization also produces a six-linear
sharp-cube paraproduct multiplier. Its geometric scale multiplier is bounded
by one and has uniform dyadic face variation. This is an independent analytic
check. The rational fixed-floor (B) is never treated as band-limited.

## Scope and tier

The pinned scope is (L=16), three complex components in the six-real
convention, `rho_regularizer=1e-12`, a common real-even scalar regulator with
supremum (M_R), and strict dyadic sharp rectangular cubes. The claim is T4:
the cutoff-uniform analytic reduction is proved and independently audited, but
the universal harmonic norms do not yet have a certified decimal upper bound.

At (p=1.1), (M_R=1), source-only sextic absorption would require

\[
M_6^4Q_6^2<29.62571266025876.
\]

This is a target, not a result. The obsolete A10 `epsilon_6=0.25` allocation
is not reused.

## Reproduction

```powershell
python codes/foundations/a12_classii_source_square_reduction_verify.py
```

Expected:

```text
PASS: primary (26/26)
PASS: independent (19/19)
ASSERTS: 65/65
A12-CLASSII-SOURCE-SQUARE-REDUCTION-INTEGRATED-PASS
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

## Devil's-advocate

1. **Rational (B) is not band-limited. — DISMISSED.** The proof first uses
   the global pointwise Pauli/Fierz operator bound; it never truncates the
   Fourier support of (B).
2. **The smaller coefficient is a numerical guess. — DISMISSED.** The proof
   derives it from exact Pauli identities including the floor and third
   component, and a doublet tangent direction saturates it.
3. **The shell loses (2\pi/L), a derivative factor, or a covariance factor.
   — DISMISSED.** The exact integer boundary is (N_{j-1}+1); (D^*) has
   symbol norm (|k|); the six-real convention is inherited unchanged.
4. **The source should scale as (M_R^4). — DISMISSED.** It contains one
   (G_j^*) and its norm is squared, hence (M_R^2). The executable rejects
   the fourth-power negative control.
5. **Individual projection bounds imply a maximal bound. — VALID WITH
   MITIGATION.** They do not. The proof uses the stronger annular randomized
   product-Marcinkiewicz square-function argument.
6. **Finite samples certify the infinite-cutoff constant. — UPHELD.** They do
   not. The numerical enclosure remains an explicit open gate and caps the
   present result at T4.
7. **The result extends to radial balls or shell ratios approaching one. —
   UPHELD.** Neither extension is claimed.

## Falsifier

Any failed Fierz identity or tangent sharpness check; violation of the exact
shell boundary, (M_R^2) power, or product-Marcinkiewicz hypotheses; a decimal
claim for (M_6^4Q_6^2) without a certified enclosure; authority hash drift;
or any failed primary, independent, integrated, PDF, or release assertion.

## No-overclaim

This claim does not complete T-047, establish a positive production sextic
reserve, prove the stabilised true-increment log-Laplace estimate or A7 Nelson
bound, construct an interacting measure, remove regulators, take infinite
volume, prove a phase transition or BCC selection, or justify T5, T6, or T7.

## History

- 2026-07-21: Registered at T4 with exact Pauli/Fierz and shell reductions;
  primary 26/26, non-importing independent 19/19, integrated 65/65; five-page
  PDF form and visual QA pass. Numerical (M_6^4Q_6^2) enclosure remains open.
