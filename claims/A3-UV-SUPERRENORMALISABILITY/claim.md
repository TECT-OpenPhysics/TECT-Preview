# A3-UV-SUPERRENORMALISABILITY — UV super-renormalisability of the scalar Brazovskii functional

**Tier**: T6 PROVED CONDITIONAL (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(UV-only; T1→T6 submitted for operator sign-off; renamed from A3-RENORMALISATION)*

## Statement

In $d=3$ with $K(q)=\mu^2+Y(q^2-q_0^2)^2$, $\mu^2>0$, every connected diagram with $V\ge1,I\ge1$ has superficial
degree $D=3-3V-I<0$; by Weinberg's theorem the perturbative expansion is **UV- and IR-finite**. **No UV-divergent
counterterm is required; a finite normal ordering is an optional scheme choice.** (UV half of A3; the continuum
limit of correlators is the separate open card **A3-PERTURBATIVE-CONTINUUM-CORRELATORS**.)

## Scope

NARROW (matching A2): one scalar field, $d=3$, quartic kernel, $\mu^2>0$; **perturbative power counting**,
UV-finiteness only. $D=(d-4)I-dV+d<0$ for $d\le3$ ($d=4$ marginal). **NOT** the continuum limit of correlators;
**NOT** constructive; **NOT** full Class-II; **NOT** $\mu^2<0$.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): A3-H1-DIM3-Q4-KERNEL, A3-H2-IR-POSITIVITY — both SATISFIED
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED.

- `claims/A3-UV-SUPERRENORMALISABILITY/notes/a3-uv-superrenormalisability-260623-260623-v1.1.tex.txt` — proof (UV-only; §3 power counting, §4 Weinberg + precise counterterm statement, §5 tadpole illustration, §6 IR)
- `codes/foundations/a3_renormalisation_checks.py` — 6/6 self-tests (UV core + tadpole illustration)
- `claims/A3-UV-SUPERRENORMALISABILITY/runs/a3_renormalisation_checks.json`

## Falsifier

A connected diagram with $V\ge1,I\ge1$ and $D\ge0$ (would need $d\ge4$ or a softer-than-$q^4$ kernel); or a UV/IR divergence at $\mu^2>0$.

## Reproduction

Status: **AVAILABLE**. `python codes/foundations/a3_renormalisation_checks.py` → 6/6 PASS.

## No-overclaim

The continuum limit of correlation functions (separate card A3-PERTURBATIVE-CONTINUUM-CORRELATORS); any constructive/non-perturbative statement; full Class-II; $\mu^2<0$; treating the finite tadpole as a required counterterm (it is an optional scheme choice).

## Devil's-advocate record

Note §7: (α) nested subdivergences — DISMISSED (Weinberg, all $D'<0$); (β) UV-finiteness ⇒ continuum limit — VALID, the reason for the split (separate card); (γ) finite tadpole is a counterterm — DISMISSED (scheme choice). Sanity check: 6/6.

## History

- 2026-06-23 — A3 deep-dive then operator review SPLIT: this card = UV super-renormalisability only (T6); the stronger continuum-correlators claim moved to A3-PERTURBATIVE-CONTINUUM-CORRELATORS. Renamed from A3-RENORMALISATION.

## Next required action

Operator sign-off; then close A3-GRAPHWISE-CONVERGENCE (graphwise lemma) for the correlators card.
