# A2-FULL-PRODUCTION-WELLPOSED -- full production PDE and pinned equilibrium

**Tier**: T6 CONDITIONAL-THEOREM (TSv2) | **Lifecycle**: ACTIVE |
**Last review**: 2026-08-03

## Statement

Assume `A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL`: the hash-pinned P1 reference
functional is the canonical full-production continuum functional. On the fixed
three-torus, for every three-component complex initial field in `H2`, its
real-`L2` gradient flow has a unique global `H2` solution. The solution depends
continuously on the initial field on every finite interval, obeys the exact
gradient-flow energy identity, and is smooth for every positive time.

For the same pinned functional, R-157 proves the stronger equilibrium bounds
(result ID `A2-PINNED-FUNCTIONAL-UNIQUE-ZERO-GLOBAL-MINIMIZER`):

```text
F_P1[Psi] >= g ||Psi||_2^2,                   g > 1/8,
<DF_P1(Psi),Psi> >= kappa ||Psi||_2^2,       kappa > 1/4.
```

The zero field is therefore the unique critical point and global minimizer in
the unconstrained `H2` field space. Its canonical gradient flow obeys
`||Psi(t)||_2^2 <= exp(-2 kappa t)||Psi(0)||_2^2`.

## Scope

The field has three complex components, treated as six real components. The
domain is the fixed periodic cell with the P1 real pairing. Production
coefficients, positive rho and Class-II mass regularisers, and
`eta_shell = 0` are fixed by the P1 manifest. Initial data are in `H2`.

R-157 selects the minimizer only within this mathematical candidate. Excluded:
the historical non-variational solver, signed A7 stochastic composite, nonzero
shell bias, removal of the regularisers, data below `H2`, infinite volume,
fixed norm or charge, compact `CP2` targets, chemical-potential transforms,
conserved or alternative dynamics, other parameter/function families,
physical-vacuum selection, and T7.

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
6. R-157 completes the scalar Fourier symbol exactly and proves the internal
   mass lower bound `M > (7/250)I`. Completing the quartic-sextic polynomial
   gives
   `g=719818750025582338837/5400000000000000000000 > 1/8`.
7. The pinned Class-II coefficient matrix and its amplitude-ray derivative
   matrix are positive definite for every regularizer ratio
   `0 <= theta <= 1`. The resulting
   `kappa=2101675000076747016511/8100000000000000000000 > 1/4`
   removes all nonzero critical points and gives exponential `L2` decay.

The self-contained proof is
[v2.0 integrated referee theorem](notes/a2-full-production-wellposedness-260717-v2.0.tex.txt).
The pinned equilibrium extension is
[R-157 source note](notes/a2-pinned-functional-unique-zero-global-minimizer-260803-v1.0.tex.txt).

## Evidence and reproduction

Evidence grades: `ANALYTIC`, `EXECUTED`, `CONDITIONAL`.

- Coercivity baseline: 20/20 PASS.
- Six-real-coordinate nonlinear map: 14/14 PASS.
- Galerkin energy and continuation: 12/12 PASS.
- Semigroup and smoothing: 15/15 PASS.
- One-command aggregate: 61/61 PASS.
- R-157 primary exact/backend audit: 26/26 PASS.
- R-157 non-importing Fraction reconstruction: 24/24 PASS.
- R-157 integrated authority, artifact, PDF, and legacy-regression audit: all
  PASS.

Run from the repository root:

```bash
python codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py
```

Expected: primary `26/26`, independent `24/24`, legacy A2 `61/61`, integrated
all PASS, exit 0. Child reruns use temporary JSON and are compared with the
immutable evidence.

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

R-157 additionally fails if a field in the declared unconstrained pinned scope
has energy below `g||Psi||_2^2`, if a nonzero critical point exists, or if the
canonical gradient flow violates the exponential `L2` estimate.

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
8. **"A zero minimizer proves that the physical vacuum is empty."** UPHELD as
   false. R-157 rejects or requires retuning this pinned M1 candidate; it does
   not select a physical law.
9. **"The radial proof transfers to fixed charge, compact `CP2`, or conserved
   dynamics."** UPHELD as false. Radial scaling is admissible in the declared
   unconstrained linear `H2` space only; those alternatives require new
   functionals and Euler--Lagrange equations.

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

R-157 applies only to the unconstrained hash-pinned P1/A2 classical functional
on the fixed torus with `eta_shell=0` and to its canonical `L2` gradient flow.
It makes `Psi=0` the unique critical point and global minimizer and forces
exponential `L2` decay in that flow. It is not a physical-vacuum theorem; it
does not apply to the historical backend, signed A7 stochastic composite,
fixed-norm/charge or compact-target constraints, chemical-potential or
conserved dynamics, other parameters/functionals, or general nonequilibrium
transients.

## History

- 2026-07-17: registered at T4 as a separate full-production proof candidate.
- 2026-07-17: nonlinear mapping audit closed, 14/14 PASS.
- 2026-07-17: energy-continuation audit closed, 12/12 PASS.
- 2026-07-17: continuous-dependence and smoothing audit closed, 15/15 PASS;
  P2 proof package complete at T4.
- 2026-07-17: operator independently reproduced the complete audit matrix;
  v2.0 integrated referee theorem confirmed; one-command verification passed
  61/61; PUBLISHED T6 bundle passed all five entries; T4 -> T6 enacted.
- 2026-08-03: R-157 proved exact positive energy and radial-derivative gaps for
  the pinned P1 functional, making zero the unique critical point and global
  minimizer and forcing exponential decay of its canonical gradient flow. Tier
  remains T6 under the same named identification hypothesis.

## Next required action

Preserve the original T6 bundle and R-157 as the pinned M1 rejection boundary.
Advance the truth-first T-054 tournament with structurally distinct candidates;
do not spend T-053 observable tests on M1. Constrained, compact-target,
chemical-potential, conserved, historical, A7, or retuned branches require
separate candidate definitions and claims.
