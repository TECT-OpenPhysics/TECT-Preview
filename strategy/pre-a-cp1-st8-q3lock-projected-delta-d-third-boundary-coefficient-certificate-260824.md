# EXP-001073 / second nonzero projected D,delta-D boundary Taylor coefficient

## Finding

Let

\[
H_0=\frac{p_q^2}{2\chi}+V_0(q,v),\qquad
H_1=H_0+B(q,v),
\]

where `V_0` is a configuration multiplier and

\[
B(q,v)=\frac c2(q-v)^2+\frac\lambda4(q-v)^2(q^2+v^2).
\]

For \(W_a(q)=\exp(i a q/\hbar)\) and \(L_H=i[H,\cdot]/\hbar\), define

\[
D(t)=e^{tL_{H_1}}(W_a)-e^{tL_{H_0}}(W_a).
\]

Because the bond and the character are configuration multipliers,

\[
D'(0)=0,
\qquad
D''(0)=-\frac{i a}{\chi\hbar}W_aF,
\quad F=\partial_qB.
\]

The next coefficient is

\[
D'''(0)=W_a\left(A_1\partial_q+A_0\right),
\]

with

\[
A_1=-\frac{a}{\chi^2}F'
    -\frac{3 i a^2}{\chi^2\hbar}F,
\qquad
A_0=-\frac{a}{2\chi^2}F''
    -\frac{2 i a^2}{\chi^2\hbar}F'
    +\frac{3a^3}{2\chi^2\hbar^2}F.
\]

The `3*a^3/2` term is the scalar-shift contribution from
`[B,(p_q+a/2)^2]`; dropping the linear shift would give the wrong answer.
Any configuration background `V_0` commutes with `W_a` and `F`, so it does
not change this boundary difference on the polynomial CCR core.

## Fixture and Lean cross-check

For \(\chi=\hbar=c=1\), \(\lambda=1/10\), \(a=1/4\), and the declared
`6 x 6` field grid, the selected point \((q,v)=(3,-2)\) gives

\[
F=12,\quad F'=59/10,\quad F''=12/5,
\]

\[
A_1=-59/40-\frac94 i,
\qquad
A_0=-3/160-\frac{59}{80}i.
\]

The exact grid ceilings are

\[
|\Re A_1|\le59/40,\quad |\Im A_1|\le9/4,
\quad |\Re A_0|\le9/80,\quad |\Im A_0|\le59/80.
\]

Primary symbolic CCR action, independent rational arithmetic, integrated
verification and Lean R255 check these identities.

## Adversarial review

1. **CCR convention — UPHELD.** Signs and \(\hbar\) factors are checked by
   direct differential-operator action.
2. **Scalar shift — UPHELD.** The linear commutator contribution in
   \((p+a/2)^2\) is retained and produces the \(3a^3/2\) term.
3. **Background — UPHELD.** Configuration \(V_0\) cancels from the boundary
   difference; no hidden kinetic background is assumed.
4. **Order — UPHELD.** The result stops at \(D'''(0)\); it does not sum the
   real-time expansion.
5. **Grid — UPHELD.** Component ceilings are finite-grid arithmetic, not
   unbounded operator estimates.
6. **Lean — UPHELD.** R255 checks exact rational fixtures only.
7. **QFT — UPHELD.** Positive-time orbit control, direct \(D,\delta D\),
   OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open.
8. **TECT owner — UPHELD.** No heat-root incidence or A1/R-192 production
   owner is supplied.

## Boundary and next gate

This is a finite CCR-core coefficient bridge. The cubic \(F\) and the linear
momentum coefficient \(A_1\partial_q\) show that the next genuine estimate
needs mixed force-momentum moments and a modular-domain argument. The static
EXP-001072 remainder cannot supply that orbit theorem by itself.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_boundary_coefficient.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_boundary_coefficient_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_boundary_coefficient_verify.py
lake env lean Tect/R255.lean
```

## QFT boundary

This is a finite QFT-facing boundary coefficient only. It is not a dynamics,
OS, KMS/GNS, mass-gap, continuum, C6, Sector-A, Pre-A, TECT production or
Clay result.
