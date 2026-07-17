# A2-FULL-PRODUCTION-WELLPOSED -- full production three-component PDE

**Tier**: T6 CONDITIONAL-THEOREM (TSv2) | **Lifecycle**: ACTIVE |
**Last review**: 2026-07-17

## Statement

Assume `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`: the hash-pinned P1 reference
functional is the canonical full-production continuum functional. On the fixed
three-torus, for every three-component complex initial field in `H2`, its
real-`L2` gradient flow has a unique global `H2` solution. The solution depends
continuously on the initial field on every finite interval, obeys the exact
gradient-flow energy identity, and is smooth for every positive time.

## Scope

The field has three complex components, treated as six real components. The
domain is the fixed periodic cell with the P1 real pairing. Production
coefficients, positive rho and Class-II mass regularisers, and
`eta_shell = 0` are fixed by the P1 manifest. Initial data are in `H2`.

Excluded: the historical non-variational solver, nonzero shell bias, removal of
the regularisers, data below `H2`, infinite volume, negative shell mass,
minimiser or BCC selection, vacuum stability, and T7.

## Dependencies and hypotheses

- Hard dependency: `A1-PRODUCTION-FUNCTIONAL-REALISATION` (T5).
- Named hypothesis: `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`.
- Soft context: `A2-PDE-WELLPOSED` (older scalar theorem, unchanged).
- Open gates: none.

The named hypothesis is required by TSv2 because the T6 theorem uses a T5
definition of the production functional. It does not weaken the mathematical
theorem for that explicitly defined functional; it prevents transfer to the
historical backend or a different functional.

## Proof map

1. The fourth-order linear operator is positive self-adjoint on `H4` and its
   form domain is `H2`. The continuous shell-symbol minimum is
   `0.260000000009475`, and the `H2` coercivity constant is
   `0.2048572626782363`.
2. The family and lock matrices are positive semidefinite. The Class-II `J-K`
   matrix is positive definite, with determinant
   `7.031249999996483e-06` and minimum eigenvalue
   `0.001259011500926061`.
3. In six real coordinates the regularised Class-II Euler--Lagrange map has
   spatial order two and is locally Lipschitz `H2 -> L2` on bounded balls.
   Analytic-semigroup contraction gives local existence and uniqueness.
4. The projected Fourier-Galerkin chain rule, `H4/H2` compactness, and the
   nonlinear real-gradient chain rule give the exact energy identity. Energy
   coercivity prevents the `H2` continuation alternative, giving global
   existence.
5. Weakly singular Gronwall gives continuous `H2` dependence. Positive-time
   Holder regularity and Duhamel cancellation give the endpoint `H4` gain;
   the order-two nonlinear map then bootstraps by two derivatives to
   `C-infinity`.

The self-contained proof is
[v2.0 integrated referee theorem](notes/a2-full-production-wellposedness-260717-v2.0.tex.txt).

## Evidence and reproduction

Evidence grades: `ANALYTIC`, `EXECUTED`, `CONDITIONAL`.

- Coercivity baseline: 20/20 PASS.
- Six-real-coordinate nonlinear map: 14/14 PASS.
- Galerkin energy and continuation: 12/12 PASS.
- Semigroup and smoothing: 15/15 PASS.
- One-command aggregate: 61/61 PASS.

Run from the repository root:

```bash
python codes/foundations/a2_full_production_verify.py
```

Expected: four PASS lines, `ASSERTS: 61/61`,
`A2-FULL-PRODUCTION-VERIFY-PASS`, exit 0. The wrapper writes only temporary
JSON and does not modify the immutable evidence.

The PUBLISHED referee bundle is
`bundle/A2-Full-Production-WellPosedness-T6-260717/`: 22 files, five entry
scripts all PASS, source commit
`c2c5a97e21ebc1f9368c1f9e5e126eb394fe47be`, bundle digest
`f07a39627a2eccc251fc67d1c988b9de18ec0b5643664fc60c3da0acc2eeeddb`.

## Falsifier

The theorem fails if any initial datum in the declared `H2` scope produces
nonexistence, nonuniqueness, finite-time `H2` blow-up, discontinuous dependence,
failure of the exact energy identity, failure of the positive-time `H4` gain,
or failure of the higher Sobolev bootstrap. A source-hash drift or loss of a
positive production sign invalidates the pinned theorem input rather than being
silently absorbed.

## Devil's-advocate record

1. **"The discrete P1 backend already proves the continuum PDE."** UPHELD as
   false. P1 is carried as a named definitional hypothesis; the continuum proof
   is separate.
2. **"The Class-II cross term destroys positivity."** DISMISSED in the pinned
   scope by the positive determinant and minimum eigenvalue.
3. **"The Class-II denominator is singular at the zero field."** DISMISSED only
   with the pinned positive rho floor. Removing it requires a new theorem.
4. **"The finite Galerkin equality automatically survives the limit."** UPHELD
   as an invalid shortcut. Compactness and the explicit nonlinear chain rule are
   load-bearing.
5. **"Fractional smoothing below one already gives `H4`."** UPHELD as false.
   The endpoint Duhamel cancellation is required.
6. **"Well-posedness proves vacuum or BCC selection."** UPHELD as an overclaim.
   The theorem controls evolution but does not choose the global minimiser.
7. **"This should be T7."** UPHELD as a governance error. The declared physical
   domain excludes several production extensions, and the T7 external-domain
   audit is absent.

## Tier decision and operator sign-off

T5 is insufficient because the result is not merely a closed finite
calculation: it proves a statement for every `H2` initial datum in the declared
domain. T6 is justified by the full proof, named T5 definitional hypothesis,
four independent executable audits, quantitative sanity checks, and PUBLISHED
reproduction bundle.

The operator independently reproduced the four audits and on 2026-07-17
instructed the repository to review eligibility, explain the result, and enact
the justified tier. This records the required operator sign-off for the
T4-to-T6 promotion.

## No-overclaim

This is a T6 theorem conditional on the pinned P1 functional definition. It is
not a theorem for the historical backend, `eta_shell != 0`, data below `H2`,
infinite volume, negative shell mass, minimiser uniqueness, BCC selection,
vacuum stability, T7, or TOE closure.

## History

- 2026-07-17: registered at T4 as a separate full-production proof candidate.
- 2026-07-17: nonlinear mapping audit closed, 14/14 PASS.
- 2026-07-17: energy-continuation audit closed, 12/12 PASS.
- 2026-07-17: continuous-dependence and smoothing audit closed, 15/15 PASS;
  P2 proof package complete at T4.
- 2026-07-17: operator independently reproduced the complete audit matrix;
  v2.0 integrated referee theorem confirmed; one-command verification passed
  61/61; PUBLISHED T6 bundle passed all five entries; T4 -> T6 enacted.

## Next required action

Preserve this bundle as the closed P2 baseline. Extensions to nonzero shell
bias, floor removal, lower-regularity data, infinite volume, or the historical
backend require separate claims. T7 is not an active target.
