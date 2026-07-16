# A2-PDE-WELLPOSED -- local and global well-posedness of the scalar Brazovskii gradient flow

**Tier**: T6 PROVED CONDITIONAL (TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-06-23

## Statement

Under (H1) `mu^2 > 0` and (H2) `gamma > 0`, the scalar Brazovskii `L^2` gradient flow
`partial_t phi = -K(-i nabla) phi - lambda phi^3 - gamma phi^5` on a fixed periodic
cell `T^3`, with `K(q)=mu^2+Y(q^2-q0^2)^2`, is globally well-posed for
`phi_0 in H^s`, `3/2 < s <= 2`: unique global solution, smoothing for `t > 0`,
continuous dependence, and non-increasing energy. The positive `mu^2` condition is
the disordered-side linear gap, not a proof of BCC condensation.

## Scope

One real scalar field, fixed periodic cell, `3/2 < s <= 2`, `Y > 0`,
positive shell mass, and positive sextic coefficient. The spectral fact used is
`lambda0 := min_k K(k) >= mu^2 > 0` (equality is non-generic). `s > 2`
persistence, the full Class-II multi-field action, and the `mu^2 < 0` condensate
branch are separate targets. `A1-PRODUCTION-KERNEL-MANIFEST` is T5 only for the
canonical pure-Brazovskii scalar slice; this theorem does not close the full
Class-II/condensate production backend.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, A1-SCALAR-ANALYTIC-BRANCH
- Hypotheses: A2-H1-KERNEL-POSITIVITY, A2-H2-SEXTIC-COERCIVITY
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED.

- `claims/A2-PDE-WELLPOSED/notes/a2-local-global-wellposedness-260623-260623-v1.2.tex.txt`
- `codes/foundations/a2_wellposedness_checks.py` -- 8/8 self-tests
- `claims/A2-PDE-WELLPOSED/runs/a2_wellposedness_checks.json`
- `claims/A2-PDE-WELLPOSED/bundle/A2-WellPosedness-260623/`

## Falsifier

Finite-time blow-up or non-uniqueness for some `phi_0 in H^s`, `3/2 < s <= 2`,
at `mu^2 > 0`, `gamma > 0`; or `lambda0 <= 0`.

## Reproduction

Status: **AVAILABLE**.

```bash
python codes/foundations/a2_wellposedness_checks.py
```

Expected: 8/8 PASS, exit 0.

## No-overclaim

Not claimed: `s > 2` persistence; full Class-II multi-field PDE; `mu^2 < 0`
condensate branch; BCC condensation; unique global minimiser; well-posedness for
`gamma <= 0`.

## Devil's-advocate record

Operator review on 2026-06-23 raised three defects, all upheld and fixed:
generic `lambda0` is only bounded below by `mu^2`; the Sobolev inclusion direction
had to be corrected; and the theorem range had to be restricted to
`3/2 < s <= 2`.

## History

- 2026-06-05: seeded T1 OPEN.
- 2026-06-23: operator-approved T1 -> T6 PROVED CONDITIONAL within the scalar,
  periodic, positive-shell-mass, positive-sextic scope.
- 2026-07-17: P0 record alignment; removed stale sign-off and mock-backend wording.

## Next required action

No scalar-scope sign-off is pending. Next foundation work is the separate
full-production variational/PDE closure for the Class-II multi-field backend and
the `mu^2 < 0` condensate branch.
