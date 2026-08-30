# R-439 -- Cutoff-adaptive threshold-four core rule audit

## Decision

`R-439 / EXP-001284` is a T0, claim-nonbearing finite rule audit. It applies
one preregistered rule to the already certified `V=2`, `beta=8`, right-oriented
unconditional ordinal-zero rows at cutoff dimensions `d=17`, `d=18` and
`d=19`:

```text
phi_i = log(p_max) - log(p_i)
core: upper(phi_i) < 4
tail: lower(phi_i) > 4
otherwise: ambiguous
```

The source interval endpoints are directed, the row selection is frozen
before classification, and the support is recomputed separately at each
cutoff. Every coordinate is unambiguous. The resulting cores are

```text
d=17: [4,5,6,7,8,9,10,11,12]   cardinality 9
d=18: [5,6,7,8,9,10,11,12]      cardinality 8
d=19: [5,6,7,8,9,10,11,12,13]   cardinality 9
```

The raw index sets are not nested and their cardinalities are not monotone.
This is an observed finite bookkeeping boundary, not a failure of every
possible increasing-core construction.

## Executed evidence

- Primary directed-interval rule audit: `31/31`, all coordinates unambiguous.
- Independent non-importing point-log control: `33/33`.
- Hostile finite-scope firewall: `9/9` mutations rejected.
- Integrated verifier: `15/15`; Lean `R439` compiles.
- Primary core cardinalities: `[9, 8, 9]`; raw nesting: `false`; cardinality
  monotonicity: `false`.
- Primary tail-mass interval summaries:
  - `d=17`: `[0.0005717069135964234071546897571969,
    0.0005717069135964234071546897571976]`.
  - `d=18`: `[0.0066373880908657931744010094904060,
    0.0066373880908657931744010094904071]`.
  - `d=19`: `[0.0017950832945981683427319846814631,
    0.0017950832945981683427319846814649]`.

## Exact scope and assumptions

The scope is only the three finite rows from `R-435`, `R-436` and `R-438`
under one fixed `V=2`, `beta=8`, orientation, row kind, emission ordinal and
threshold. The maximum midpoint probability is used as the reference within
each already fixed row; it is not optimized using the resulting support or
gap. The expected supports are manifest-level finite test oracles. Directed
Decimal logarithms are evaluated with enough precision to test strict
threshold inequalities.

## Adversarial review

1. **Threshold drift.** Selection or rule threshold changes are rejected.
2. **Support substitution.** Replacing the per-cutoff support with a fixed
   support is rejected.
3. **Ambiguity hiding.** Any threshold-straddling coordinate is rejected.
4. **Oracle drift.** Altered finite support oracles are rejected.
5. **Nesting promotion.** Setting a nested-core flag is rejected.
6. **Uniform-tail promotion.** Setting the tail-modulus flag is rejected.
7. **Claim promotion.** Turning the result into a claim-bearing result is
   rejected.

## Boundary and next gate

The audit does not supply a cutoff-, volume-, phase- or exhaustion-uniform tail
modulus, a nested common Q3 core, residual-reuse closure, a common unbounded
Hamiltonian domain, OS/KMS/GNS reconstruction, or a physical-sector transfer.
The next gate is an owner-approved uniform tail estimate (or a full-sector
completeness theorem) for the adaptive supports, with explicit embeddings and
limit order. Until then this result remains finite and claim-nonbearing.

No physical-empty sign, Reading-H stationarity, transverse stability, C6,
Sector-A, Pre-A, Yang--Mills or mass-gap conclusion follows.

