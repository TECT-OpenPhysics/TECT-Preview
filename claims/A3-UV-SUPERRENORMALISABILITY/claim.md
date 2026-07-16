# A3-UV-SUPERRENORMALISABILITY -- scalar Brazovskii UV super-renormalisability

**Tier**: T6 PROVED CONDITIONAL (TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-06-23

## Statement

In `d=3` with `K(q)=mu^2+Y(q^2-q0^2)^2`, positive shell mass, and `Y > 0`,
every connected diagram with `V >= 1` and `I >= 1` has superficial degree
`D = 3 - 3V - I < 0`. By Weinberg's theorem the scalar perturbative expansion is
UV- and IR-finite. No UV-divergent counterterm is required; finite normal
ordering is an optional scheme choice.

## Scope

One scalar field, `d=3`, quartic kernel, positive shell mass, perturbative power
counting, UV-finiteness only. Not claimed: continuum correlator convergence
(separate A3 correlator card), constructive/non-perturbative control, full
Class-II, or `mu^2 < 0`.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, A1-SCALAR-ANALYTIC-BRANCH
- Hypotheses: A3-H1-DIM3-Q4-KERNEL, A3-H2-IR-POSITIVITY
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED.

- `claims/A3-UV-SUPERRENORMALISABILITY/notes/a3-uv-superrenormalisability-260623-260623-v1.1.tex.txt`
- `codes/foundations/a3_renormalisation_checks.py` -- 6/6 self-tests
- `claims/A3-UV-SUPERRENORMALISABILITY/runs/a3_renormalisation_checks.json`
- `claims/A3-UV-SUPERRENORMALISABILITY/bundle/A3-Renormalisation-Foundation-260623/`

## Falsifier

A connected diagram with `V >= 1`, `I >= 1`, and `D >= 0`; or a UV/IR divergence
within the stated scalar, positive-shell-mass scope.

## Reproduction

Status: **AVAILABLE**.

```bash
python codes/foundations/a3_renormalisation_checks.py
```

Expected: 6/6 PASS, exit 0.

## No-overclaim

Not claimed: continuum correlator convergence; constructive/non-perturbative
statements; full Class-II; `mu^2 < 0`; treating the finite tadpole as a required
counterterm.

## Devil's-advocate record

Nested subdivergences are covered by Weinberg power counting because all
subdegrees are negative. UV-finiteness does not by itself prove continuum
correlator convergence, which is handled by the separate correlator card. The
finite tadpole is a scheme choice, not a required UV counterterm.

## History

- 2026-06-23: A3 split; this card carries only the UV super-renormalisability
  result and was operator-approved as T6 within the scalar scope.
- 2026-07-17: P0 record alignment; removed stale sign-off and open-correlator wording.

## Next required action

No UV-scope sign-off is pending. Next foundation work is Route B
regularisation-independence, constructive/non-perturbative control, and the
separate full-production Class-II backend closure.
