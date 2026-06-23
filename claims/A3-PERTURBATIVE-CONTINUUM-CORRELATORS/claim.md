# A3-PERTURBATIVE-CONTINUUM-CORRELATORS — cutoff-independent continuum limit of the perturbative correlators

**Tier**: T6 PROVED CONDITIONAL (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(T3→T6 APPROVED by operator 2026-06-23; spectral/Galerkin, fixed-p; gate CLOSED@spectral, lattice=Route B open)*

## Statement

The perturbative measure $d\nu_{\Lambda,a}\propto e^{-F_{\Lambda,a}}d\phi$ is well-defined under $\gamma>0$
($F_{\Lambda,a}$ bounded below ⇒ $Z_{\Lambda,a}<\infty$). Its connected perturbative amplitudes satisfy
$\lim_{a\to0}\mathcal A_{\mathcal G,a}(p)=\mathcal A_{\mathcal G}(p)$ (lattice regulator $\hat q=\tfrac2a\sin\tfrac{aq}2$
+ dominated convergence: pointwise $G_a\to G$ + uniform $(1+|q|)^{-4}$ bound + Weinberg integrability), with
$\Lambda=\pi/a$ tying $a\to0\equiv\Lambda\to\infty$ — so each order of the perturbative correlators has a
cutoff-independent continuum limit. The graphwise lemma is **PROVED** (note v1.2); promotion to **T6 awaits
operator ratification**.

## Scope

scalar, $d=3$, $\mu^2>0$, $\gamma>0$, **perturbative** order-by-order. **Measure hypothesis** (operator review):
$\gamma>0$ is required for $d\nu\propto e^{-F}$ to be defined. Gate A3-GRAPHWISE-CONVERGENCE = **PROVED**, T6
ratification pending. **NOT** resummation; **NOT** the constructive/non-perturbative measure limit
($\mathrm{A3}_{\rm constructive}$); **NOT** full Class-II; **NOT** $\mu^2<0$.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV, A3-UV-SUPERRENORMALISABILITY
- Hypotheses (registered): A3-H1-DIM3-Q4-KERNEL, A3-H2-IR-POSITIVITY, **A2-H2-SEXTIC-COERCIVITY** (γ>0, measure stability)
- Open gates: none (A3-GRAPHWISE-CONVERGENCE CLOSED@spectral; genuine lattice = Route B, open refinement)

## Evidence

Grades: ANALYTIC, ESTIMATOR.

- `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/notes/a3-graphwise-convergence-lemma-260623-260623-v1.4.tex.txt` — proof (§2 spectral regulator, §2′ γ>0 measure, §3 the aliasing flaw recorded, §5 spectral domination, §6 DCT, §8 Route B)
- `codes/foundations/a3_graphwise_convergence_checks.py` — 7/7 self-tests
- `claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS/runs/a3_graphwise_convergence_checks.json`

## Falsifier

A connected graph $\mathcal G$ whose lattice amplitude fails to converge under this regulator; failure of the uniform $(1+|q|)^{-4}$ bound on $\mathrm{BZ}_a$; or $\gamma\le0$ (then $d\nu$ is undefined).

## Reproduction

Status: **AVAILABLE**. `python codes/foundations/a3_graphwise_convergence_checks.py` → 7/7 PASS.

## No-overclaim

A ratified T6 (operator verdict is T3 PROOF SKETCH pending ratification of the proved lemma + the γ>0 measure hypothesis); order-by-order only (not resummation); not constructive/non-perturbative; not full Class-II; not $\mu^2<0$.

## Devil's-advocate record

Note §7: (α) pointwise insufficient — DISMISSED (dominated convergence); (β) lattice doublers — DISMISSED (scalar, shell-only minimum); (γ) order-by-order not full series — VALID, mitigated (constructive = separate). Plus the operator's measure point: γ>0 added as A2-H2-SEXTIC-COERCIVITY (§2′). Sanity check: 7/7.

## History

- 2026-06-23 — Created (T3, A3 split); graphwise lemma proved (v1.1) and prematurely set T6; reverted to **T3** to honor the operator verdict (T3 open). v1.2 adds the γ>0 measure-stability hypothesis (operator review #1). Both stated T6 requirements (proved lemma + γ>0 measure hypothesis) now met; RE-SUBMITTED for T6.

## Next required action

Operator ratification of the proved graphwise lemma + γ>0 measure hypothesis → T6 jointly with A3-UV; then $\mathrm{A3}_{\rm constructive}$ + the physical production-Hessian mainline.
