# A3-PERTURBATIVE-CONTINUUM-CORRELATORS -- spectral perturbative continuum limit

**Tier**: T6 PROVED CONDITIONAL (TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-06-23

## Statement

Under the spectral/Galerkin regulator, every connected perturbative amplitude of
the scalar Brazovskii theory in `d=3`, with positive shell mass and `gamma > 0`,
converges as the cutoff is removed for each fixed external momentum. The proof uses
pointwise convergence, uniform `q^-4` domination, and Weinberg integrability. The
genuine finite-difference lattice regulator is Route B and remains a separate open
refinement.

## Scope

Scalar field, `d=3`, positive shell mass, `Y > 0`, `gamma > 0`, perturbative
order-by-order, spectral/Galerkin regulator, fixed external momentum. Not claimed:
resummation, constructive/non-perturbative measure convergence, full Class-II,
`mu^2 < 0`, genuine finite-difference lattice Route B, or uniform-in-external-
momentum convergence.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, A1-SCALAR-ANALYTIC-BRANCH, A3-UV-SUPERRENORMALISABILITY
- Hypotheses: A3-H1-DIM3-Q4-KERNEL, A3-H2-IR-POSITIVITY, A2-H2-SEXTIC-COERCIVITY
- Open gates: none for the spectral scope; finite-difference lattice Route B is an open refinement

## Evidence

Grades: ANALYTIC, ESTIMATOR.

- `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/notes/a3-graphwise-convergence-lemma-260623-260623-v1.4.tex.txt`
- `codes/foundations/a3_graphwise_convergence_checks.py` -- 8/8 self-tests
- `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/runs/a3_graphwise_convergence_checks.json`
- `claims/A3-UV-SUPERRENORMALISABILITY/bundle/A3-Renormalisation-Foundation-260623/`

## Falsifier

A connected graph whose amplitude fails to converge under the spectral/Galerkin
regulator; failure of the uniform `q^-4` domination; or `gamma <= 0`, which breaks
the measure stability hypothesis.

## Reproduction

Status: **AVAILABLE**.

```bash
python codes/foundations/a3_graphwise_convergence_checks.py
```

Expected: 8/8 PASS, exit 0.

## No-overclaim

Order-by-order only; not resummation; not constructive/non-perturbative; not full
Class-II; not `mu^2 < 0`; not genuine finite-difference lattice Route B; not
uniform-in-external-momentum convergence.

## Devil's-advocate record

Pointwise convergence alone is insufficient but is paired with domination. The
finite-difference lattice aliasing objection is valid for Route B and is not used
in this spectral result. Order-by-order perturbation theory is not a full series
or constructive measure result.

## History

- 2026-06-23: created during the A3 split; graphwise convergence approved as T6
  within the spectral/Galerkin scope after the measure-stability hypothesis was
  made explicit.
- 2026-07-17: P0 record alignment; corrected stale T6-pending and 7/7 wording.

## Next required action

Route B regularisation-independence, constructive/non-perturbative control, and
the separate full-production Class-II backend closure.
