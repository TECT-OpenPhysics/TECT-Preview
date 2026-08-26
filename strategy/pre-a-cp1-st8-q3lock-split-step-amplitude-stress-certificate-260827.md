# EXP-001196 - actual finite Q3 split-step source-amplitude stress

## Question

Does the actual finite-Q3 split-step four-context recurrence remain within
the fixed `C=J=1` envelope when the local source amplitude is varied?

## Computation

The canonical quartic Q3 Hamiltonian is rebuilt on the target edge, square
face, and 2x3 rectangular grid (volumes 2, 4, and 6), with oscillator
truncation 3 and beta 1.  The source is supported on sites `{0,1}` and the
amplitudes are `1/6`, `1/3`, `2/3`, `1`, and `2`.  Both real-time signs, both
adjoint contexts, both exact onsite-plus-all-bond product orders, and two
split steps of delta `1/18` are tested.  The seminorm is

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

The primary lane passes `405/405` assertions and the independent lane passes
`389/389`.  Both cover 120 parameter/context histories, 1,440 length rows,
and 960 recurrence rows.  The integrated verifier passes `372/372`, and Lean
R355 compiles.  No recurrence violation occurs at the `1e-9` threshold.  The
largest primary residual is `1.7513747338129368e-14` (roundoff scale), the
smallest is `-0.26820432407804784`, and the maximum primary residuals by
amplitude are `1.7513747338129368e-14` (`1/6`),
`1.645530484965069e-14` (`1/3`), `1.3549546640955606e-14` (`2/3`),
`1.189886717939869e-14` (`1`), and `1.1298525058628922e-14` (`2`).

## Adversarial boundary

This strengthens only the finite split-step source-amplitude stress input.
The exact Q3 recurrence has not been proved on an unbounded common core, and
no bound is uniform in volume, cutoff, beta, source word degree, or exhaustion
shape.  The finite pass does not identify a common Hamiltonian dynamics with
an OS carrier, establish a common alpha or KMS state, prove a GNS/physical-
sector gap, remove the regulator, or close C6, Sector A, Pre-A, or the Clay
problem.  A future violation would be a route-local boundary, not a QFT
no-go.

No claim tier, result authority, or negative-result authority is changed.