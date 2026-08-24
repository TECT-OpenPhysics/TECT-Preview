# EXP-001059 / local force moment interface

## Finding

Let

\[
e(q)=\frac r2q^2+\frac g4q^4+\frac{r^2}{2g}\ge0,
\qquad E_{xy}=1+e(q_x)+e(q_y).
\]

The sitewise completion-of-square identity from EXP-001057 gives

\[
q^4\le \frac8g e(q),
\qquad 1+q^4+v^4\le 1+\frac8g(e(q)+e(v)).
\]

Combining this with the EXP-001058 finite force bound

\[
|\partial_qB|^4\le C^4(1+q^4+v^4)^3,
\qquad C=122099/35840,
\]

gives the local endpoint estimate

\[
|\partial_qB|^4\le C^4\max(1,8/g)^3 E_{xy}^3.
\]

Consequently, if the fixed-beta finite-volume Gibbs family supplies the
explicit conditional input

\[
\sup_{\Lambda,x\sim y}\phi_\Lambda(E_{xy}^3)\le M_{\beta,\mathrm{local}},
\]

then

\[
\|\partial_qB\|_{L^4(\phi_\Lambda)}
\le C\max(1,8/g)^{3/4}M_{\beta,\mathrm{local}}^{1/4}.
\]

The second generator coefficient from EXP-001058 gains the factor
`|a|/(hbar*chi)`.  The local moment hypothesis itself is not proved here.

## Verification

- Primary exact SymPy lane: 123/123.
- Independent Fraction lane: 191/191.
- Integrated verifier: 23/23; Lean R241 compiles.
- The fixture derives shift `135/8`, ratio `40/3`, and the exact local
  prefactor power from the manifest values.

## Adversarial review

1. The endpoint comparison is sitewise; no extensive global shift is used as a
   local moment theorem. UPHELD.
2. Uniform local third moment is an explicit conditional input, not a claimed
   consequence of coercivity. UPHELD.
3. The coefficient and one-quarter moment exponent are derived. UPHELD.
4. The estimate applies to the second generator coefficient, not the full
   time-evolved difference. UPHELD.
5. Lean R241 checks arithmetic fixtures only. UPHELD.
6. D,delta-D, OS/KMS, GNS, continuum, C6, Sector A and Pre-A remain open.
   UPHELD.
7. No TECT `heat_root_incidence` or A1/R-192 production owner is supplied.
   UPHELD.

## Next gate

Prove or obstruct the uniform local third-moment hypothesis for the fixed-beta
finite-volume Gibbs family, then insert this conditional coefficient into a
two-sided Duhamel remainder estimate.
