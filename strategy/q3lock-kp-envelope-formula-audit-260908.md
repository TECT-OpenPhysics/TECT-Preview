# Q3LOCK KP envelope and finite-range weight audit

Date: 2026-09-08. Exploration: EXP-001662. Task: T-054.

Status: T0 internal model-side audit only; `claim_bearing=false`.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
PDF status: deferred until the mathematical content is frozen and signed.

## Question

Does the printed non-radial eight-component Q3LOCK onsite potential supply the
exact lower/upper envelopes and finite-range weight data used in the
Kozitsky--Pasurek (KP) general-vector fixed-source DLR input, without confusing
the KP growth exponent with the Q3LOCK mass coefficient?

This audit checks the displayed algebra and a finite set of exact rational
fixtures. It does not reprove KP, establish the source-window estimate, or
certify any DLR, cusp, or phase conclusion.

## Model-side derivation

Let `d=3`, `nu=2^d=8`, and let the spatial torus have nearest-neighbour
degree `2d`. The Q3LOCK onsite part is

\[
 V_h(q)=\frac{r+2dc-a}{2}|q|^2+\frac g4\sum_e q_e^4
 +\frac\lambda4\sum_{\{e,f\}\in E(Q_3)}
 (q_e-q_f)^2(q_e^2+q_f^2)-h(u,q).
\]

The audit derives, rather than pastes, the quantities

\[
 b=\frac12|r+2dc-a|,\qquad
 A=\frac{g}{16\nu},
\]

by using `sum_e q_e^4 >= |q|^4/nu`, reserving one half of the resulting
quartic coefficient for the quadratic absorption and one quarter for the
linear-source absorption. The exact scalar maxima are

\[
 C_\mathrm{quad}=\frac{b^2}{4k_\mathrm{quad}},\qquad
 C_\mathrm{lin}=\frac34 h_0\left(\frac{h_0}{4k_\mathrm{lin}}\right)^{1/3},
\]

where `k_quad=g/(8 nu)` and `k_lin=g/(16 nu)`. Thus
`C_0=C_quad+C_lin`, and the audit checks

\[
 A|q|^4-C_0\le V_h(q)\le
 (g/4+3\lambda)\sum_e q_e^4+b|q|^2+h_0|q|.
\]

The upper locking coefficient follows from
`(x-y)^2(x^2+y^2) <= 4(x^4+y^4)` and the degree-three internal cube graph.

For the spatial interaction, the audit derives `degree=2d`,
`J_0=2dc`, and for `w_alpha(y,z)=exp(-alpha |y-z|)`

\[
 \widehat J_\alpha=2dc\,e^\alpha,\qquad
 \widehat J_\alpha-\widehat J_0\downarrow0
 \quad(\alpha\downarrow0).
\]

It also checks the multiplicative metric inequality on finite fixtures and a
finite shell-plus-integral bound for the required polynomial lattice sum.

## Disposition

The exact fixture passes if the derived envelope coefficients, Q3 locking
bound, finite-range row sums, weight monotonicity and hostile substitutions all
agree. The result is an internal clarification of A6. It does not change the
proof-audit row from `OPEN`: signed verification of the source's precise
hypotheses, the form/trace interface, the source-window recursion and the
source-to-zero DLR passage remains required.

## Explicit nonclaims

No KP theorem is reproved. No source-uniform estimate, thermodynamic limit,
continuous-loop FKG statement, strict cusp, pair of phases, novelty claim,
claim-tier change, external-review signature, submission, release, or Q3LOCK
paper PDF is created by this audit.
