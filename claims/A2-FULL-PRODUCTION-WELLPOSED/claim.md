# A2-FULL-PRODUCTION-WELLPOSED -- full production three-component PDE

**Tier**: T4 FULL-PROOF-CANDIDATE (TSv2) -- **Lifecycle**: ACTIVE --
**Last review**: 2026-07-17

## Statement

On the fixed periodic cell, take the real `L2` gradient flow of the canonical
three-component P1 reference functional with the pinned production parameters
and `eta_shell = 0`.  The full linear operator is self-adjoint on `H4`, has a
positive spectral lower bound, and controls the `H2` norm.  The family and lock
terms are positive semidefinite, the Class-II `J-K` coefficient matrix is
positive definite, and the sextic term absorbs the negative quartic term.

The accompanying note assembles the remaining semigroup, energy-continuation,
continuous-dependence, and smoothing argument for global `H2` solutions.  That
argument is a T4 proof candidate, not yet a T6 theorem.

## Scope

The field is `Psi in C3` on the fixed three-torus, regarded as six real
components with the P1 real pairing.  The source of truth is the hash-pinned P1
functional and production coefficient set.  Positive `rho` and Class-II mass
regularisers are retained.  The production shell-bias coefficient is exactly
zero.  The historical external backend remains a non-variational proxy and is
not part of this claim.

## Dependencies and gates

- Hard dependency: `A1-PRODUCTION-FUNCTIONAL-REALISATION`
- Soft context: `A2-PDE-WELLPOSED` (the older scalar theorem, unchanged)
- Open gates: `A2-FULL-NONLINEAR-MAPPING-AUDIT`,
  `A2-FULL-ENERGY-CONTINUATION-AUDIT`, `A2-FULL-SMOOTHING-AUDIT`
- Hypotheses: none

## Evidence

- [Full PDE manifest](full_pde_manifest.json)
- [Proof-candidate note](notes/a2-full-production-wellposedness-260717-v1.0.tex.txt)
- [Deterministic audit script](../../codes/foundations/a2_full_production_wellposedness_checks.py)
- [Audit result](runs/2026-07-17-coercivity-baseline/result.json)

The audit gives 20/20 PASS.  Its load-bearing values are shell mass
`0.260000000009475`, linear `H2` coercivity constant `0.2048572626782363`,
Class-II determinant `7.031249999996483e-06`, and Class-II minimum eigenvalue
`0.001259011500926061`.

## Reproduction

```bash
python codes/foundations/a2_full_production_wellposedness_checks.py
```

Expected: `A2-FULL-COERCIVITY-BASELINE-PASS`, 20/20 assertions, exit 0.

## Falsifier

The baseline fails if a pinned source hash drifts, the full linear operator is
not Hermitian/coercive, the Class-II matrix is not positive definite, or the
regulariser/sextic signs fail.  The theorem candidate fails if its full
Euler-Lagrange map is not locally Lipschitz `H2 -> L2`, if the energy identity
does not justify global continuation, or if blow-up/non-uniqueness occurs in
the declared `H2` scope.

## Devil's-advocate

1. **"P1 T5 already proves this PDE theorem."** UPHELD as an invalid reading:
   P1 is only a discrete variational-matrix result.
2. **"The Class-II cross term can make the energy indefinite."** DISMISSED at
   the production point: the symmetric coefficient matrix has determinant
   `7.031249999996483e-06` and minimum eigenvalue
   `0.001259011500926061`, both positive.
3. **"The shell-bias activation used in P1 tests defines the continuum term."**
   VALID with mitigation: the continuum theorem is restricted to the actual
   production value `eta_shell = 0`; nonzero bias needs a separate
   normalisation/convergence argument.
4. **"Energy decrease was assumed before the Class-II chain rule was
   justified."** UPHELD as an audit requirement: the Galerkin/chain-rule
   passage is the named energy-continuation gate.
5. **"Fourth-order smoothing makes every lower-order mapping estimate
   automatic."** UPHELD as an invalid shortcut: the real-coordinate
   `H2 -> L2` estimate and the positive-time bootstrap remain named audits.

## No-overclaim

This T4 card is not a theorem-tier closure.  It does not cover the historical
proxy, nonzero shell bias, initial data below `H2`, infinite volume, the
negative-shell-mass branch, minimizer or BCC selection, stability, T6, or T7.

## History

- 2026-07-17: created separately from the scalar A2 card.  Algebraic and
  coercive stages closed; full `H2` proof candidate assembled at T4 with three
  named audits retained.

## Next required action

Expand the Class-II Euler-Lagrange map in real coordinates and independently
audit the local Lipschitz estimate `H2 -> L2`.  Then audit the energy
continuation and smoothing stages in that order.
