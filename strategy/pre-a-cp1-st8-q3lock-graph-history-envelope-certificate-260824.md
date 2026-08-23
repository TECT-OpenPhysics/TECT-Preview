# Conditional bounded-degree graph history certificate

## Scope

For a finite open box in `Z^3`, every vertex has at most six neighbours. A
length-`m` oriented walk from any seed is therefore bounded by `6^m`. Because
the box graph is explicitly undirected, the reversed adjacency graph has the
same walk counts. This gives a volume-independent combinatorial envelope for
any supplied recurrence whose coefficients are bounded by those path counts.

The separate supplied two-orientation scalar recurrence is

`B_(n+1) = (1+C*delta) B_n + J*delta B_n^(+) + J*delta B_n^(-)`.

With `C=1/5`, `J=1/10`, `delta=1/7`, its factor is `37/35` per step. The
primary and independent lanes enumerate sides 1, 2, 3 and 4 through five
steps with exact integer arithmetic and check every seed, order and reverse
orientation. R218 checks the degree and branch arithmetic.

## Finding

The declared finite box-family combinatorial envelope passes and is independent
of `site_count`. This is useful input for a future Q3 history estimate, but it
does not control the actual quartic commutator coefficients, source topology,
or cancellations. It also does not establish arbitrary-shape exhaustion,
common alpha, KMS, GNS gap, continuum or Pre-A.

## Adversarial review

- Path count versus operator coefficient: UPHELD; no coefficient theorem is
  inferred from walk counting.
- Shape coverage: UPHELD; only sides 1 through 4 are tested.
- Adjoint orientation: UPHELD; reverse equality is graph-theoretic only.
- Lean promotion: UPHELD; R218 is scalar arithmetic, not a path formalization.
- QFT promotion: UPHELD; no thermodynamic or QFT result is claimed.

## Reproducibility

Run both exact scripts and the integrated verifier. The integrated verifier
executes both lanes and `lake env lean Tect/R218.lean`, and stores the run JSON
under the C6 claim run directory. The package remains T0, claim-nonbearing,
with no tier change, result, negative result or PDF.
