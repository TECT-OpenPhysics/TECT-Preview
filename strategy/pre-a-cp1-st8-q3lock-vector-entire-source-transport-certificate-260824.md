# Conditional vector entire-source transport certificate

## Scope

This certificate audits one conditional interface for the Q3 dynamics route. On
a finite three-dimensional periodic torus, let `P` be the average over the six
nearest neighbours and let `M_delta = I + kappa*delta*P`. If a supplied source
history satisfies `a_next = M_delta a`, then Jensen convexity and the
`ell^4` contraction of `P` give

`S(M_delta a) <= (1+kappa*delta)^4 S(a)`,

where `S(a) = sum_x |a_x|^4`. Therefore

`W_sigma(M_delta a) <= W_{sigma(1+kappa*delta)^4}(a)`

for `W_sigma(a) = exp(sigma*S(a))`. Iteration gives the product type update
without a factor depending on the number of sites.

The exact fixture uses dimension 3, side 3, `kappa = 1/5`, total time 1,
six equal steps, and `sigma_0 = 1/5`. Thus the one-step factor is `31/30` and
the six-step type is `(1/5)*(31/30)^24`, which is strictly below the declared
test oracle `1/2`. The primary and independent scripts recompute the vector
bounds with exact rational arithmetic; R217 checks the scalar type arithmetic.

## Finding

The conditional vector transport checkpoint passes. Its type formula is
volume-independent within the declared regular periodic graph class. This is
not yet the Q3 history estimate: the recurrence `a_next = M_delta a` is an
input, not a derived consequence of the quartic Q3 commutator. Open boxes,
all exhaustion shapes, reverse orientations, analytic domains, common alpha,
and the thermodynamic/QFT bridges remain unproved.

## Adversarial review

- Recurrence input: UPHELD. No actual Q3 recurrence is smuggled into the
  fixture.
- Graph class: UPHELD. Periodic regularity is explicit; arbitrary exhaustion
  shapes are not covered.
- Norm/domain: UPHELD. Finite `ell^4` arithmetic is not a common-core domain
  or representation-independent seminorm theorem.
- Lean: UPHELD. R217 checks scalar rational arithmetic only.
- QFT promotion: UPHELD. No KMS, GNS, gap, continuum or production-owner result
  is claimed.

## Reproducibility

Run the primary and independent scripts, then the integrated verifier. The
integrated verifier runs both lanes and `lake env lean Tect/R217.lean`, and can
store its JSON run under the C6 claim run directory. The manifest and scripts
are English-only and the package is T0, claim-nonbearing, with no tier change,
new result, negative result or PDF.
