# EXP-001157 - finite split-step uniformity stress audit

## Question

Does the finite split-step recurrence remain valid under source, beta, volume
and shape changes with the same constants and both term orders?

## Stress design

The audit retains the exact onsite-plus-all-bond product from EXP-001156 with
oscillator dimension 3, delta=1/18, six steps, both signs, both A/A* contexts,
and both onsite-first and reverse term orders.  The cases are:

1. canonical volumes 2, 4 and 6, beta=1, source pair (0,1);
2. canonical volume 6 at beta=1/2;
3. canonical volume 6 at beta=2;
4. shifted source pairs (1,2) at volume 4 and (3,4) at volume 6;
5. path-shaped stress graphs at volumes 4 and 6, beta=1, source pair (0,1).

The tested seminorm is

\[
L_x^2=\|[q_x,A]\|_{\beta,#}^2+\|[p_x,A]\|_{\beta,#}^2,
\]

against

\[
L_x(n+1)\le(1+C\delta)L_x(n)+J\delta\sum_{y\sim x}L_y(n),
\qquad C=J=1.
\]

## Result

The primary lane passes 559/559 assertions, the independent lane passes
558/558, the integrated lane passes 155/155, and Lean R327 compiles.  Each
lane contains 2464 commutator-length rows and 2112 recurrence rows.  There are
no violations in any declared case, term order or context.

| case | primary maximum residual |
|---|---:|
| baseline canonical beta=1 source (0,1) | 1.64553048496507e-14 |
| canonical beta=1/2, V=6 | 1.662813170245e-14 |
| canonical beta=2, V=6 | 1.65309083175331e-14 |
| canonical shifted sources | 1.83980565155742e-14 |
| path-shape source (0,1) | 1.48584855450973e-14 |

The declared recurrence tolerance is 1e-9, so every tested row passes by a
large finite margin.

## Boundary and next gate

This is stronger finite applicability evidence than EXP-001156, but it is not
an analytic uniform estimate.  The path graph is explicitly a stress geometry,
not a claim about the canonical Q3 lattice.  Source, beta, cutoff and volume
uniformity, arbitrary-shape exhaustion, product/core density, common alpha,
OS/KMS/GNS reconstruction, gap, continuum, C6, Sector A and Pre-A remain open.

The next proof obligation is an analytic state-weighted or energy-graph bound
uniform in source, beta and volume, followed by an exhaustion and product/core
argument.
