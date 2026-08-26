# EXP-001195 - actual finite Q3 split-step parameter stress

## Question

Do the actual finite-Q3 split-step four-context recurrence rows remain
nonpositive when source support, beta, and finite volume/shape are varied?

## Computation

The canonical quartic Q3 Hamiltonian is rebuilt on the target edge, square
face, and 2x3 rectangular grid (volumes 2, 4, and 6), with oscillator
truncation 3.  The source words are
`exp(i (q_0)/3)` and `exp(i (q_0+q_1)/3)`.  The stress grid uses beta in
`{1/2,1,2}`, both real-time signs, both adjoint contexts, two exact
onsite-plus-all-bond product orders, and two split steps of delta `1/18`.
The tested seminorm is

\[
 L_x^2=\|[q_x,A]\|_{\beta,#}^2+\|[p_x,A]\|_{\beta,#}^2,
\qquad
 \|X\|_{\beta,#}^2=\operatorname{Tr}(\rho X^*X)+\operatorname{Tr}(\rho XX^*).
\]

The candidate recurrence is

\[
 L_x(n+1)\le (1+\delta)L_x(n)+\delta\sum_{y\sim x}L_y(n).
\]

## Result

The primary lane passes `487/487` assertions and the independent lane passes
`470/470`.  Both cover 144 parameter/context histories, 1,728 length rows,
and 1,152 recurrence rows.  The integrated verifier passes `444/444`, and
Lean R354 compiles.  No recurrence violation occurs at the `1e-9` threshold.
The largest primary residual is `2.3028728945237117e-14` (roundoff scale),
the smallest is `-0.07221929223985579`, and the beta-wise maxima are
`2.1538594548489452e-14` for `1/2`, `2.1890950777805194e-14` for `1`, and
`2.3028728945237117e-14` for `2`.

## Adversarial boundary

This strengthens only the finite split-step stress input.  The exact Q3
recurrence has not been proved on an unbounded common core, and no bound is
uniform in volume, cutoff, beta, source class, or exhaustion shape.  The
finite pass does not identify a common Hamiltonian dynamics with an OS
carrier, establish a common alpha or KMS state, prove a GNS/physical-sector
gap, remove the regulator, or close C6, Sector A, Pre-A, or the Clay problem.
A future violation would be a route-local boundary, not a QFT no-go.

No claim tier, result authority, or negative-result authority is changed.