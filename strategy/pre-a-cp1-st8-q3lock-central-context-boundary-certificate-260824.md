# EXP-001049 — One-sided Q3 graph bounds do not imply central A-context control

## Finding

EXP-001048 identified the sufficient central-context hypothesis
\(\|A^a D A^{-b}\|\le B\) for \(a,b\in\{0,3/4\}\). This checkpoint tests
whether the already available one-sided graph bounds can supply that missing
context by inference.

For \(b\ge2\), \(n\ge1\), let

\[
A_n=\operatorname{diag}(1,b^{4n},b^{8n}),\qquad
D_n=S A_n^{3/4},
\]

where \(S e_0=e_1\), \(S e_1=e_2\), and \(S e_2=0\). Exact matrix arithmetic gives

\[
\|D_nA_n^{-3/4}\|_\infty=1,\quad
\|A_n^{-3/4}D_n\|_\infty=b^{-3n}\le1,
\]

but

\[
\|A_n^{3/4}D_nA_n^{-3/4}\|_\infty=b^{6n}.
\]

At \(b=2\), the central context is \(64^n\). Thus EXP-001045's one-sided
graph bounds cannot by themselves prove the central context required by
EXP-001048. This is a finite inference boundary only; it does not identify
the witness with the actual Q3 source difference and does not establish that
the Q3 central context is impossible.

## Devil's-advocate review

1. The witness is abstract and finite, not an unbounded Q3 multiplier. Upheld.
2. Both one-sided orientations and their unequal exact values are retained. Upheld.
3. The target is the single central conjugation context, distinct from the prior repeated-product target. Upheld.
4. Fractional powers are exact integer powers of the base. Upheld.
5. The result rejects only an inference rule, not all analytic/Frechet, heat-strip or state-weighted routes. Upheld.
6. Lean R231 checks arithmetic only. Upheld.
7. No QFT, KMS, gap, continuum, C6, Sector A or Pre-A closure follows. Upheld.

## Next gate

Do not keep trying to obtain the central context from one-sided graph bounds
alone. Test a non-Leibniz product-level analytic/Frechet or heat/strip-loss
estimate, retaining the spatial weight and both orientations.
