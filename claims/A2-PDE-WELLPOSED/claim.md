# A2-PDE-WELLPOSED — local & global well-posedness of the scalar Brazovskii gradient flow

**Tier**: T6 PROVED CONDITIONAL (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(T1→T6 PROVED CONDITIONAL — APPROVED by operator 2026-06-23; scope: scalar/periodic/$\mu^2>0$/$\gamma>0$, $3/2<s\le2$)*

## Statement

Under (H1) $\mu^2>0$ and (H2) $\gamma>0$, the **scalar** Brazovskii $L^2$ gradient flow
$\partial_t\phi=-K(-i\nabla)\phi-\lambda\phi^3-\gamma\phi^5$ on a **fixed** periodic cell $\mathbb{T}^3$
($K(q)=\mu^2+Y(q^2-q_0^2)^2$, A1-KERNEL-CONV) is **globally well-posed** for $\phi_0\in H^s$, $\tfrac32<s\le2$:
unique global solution, $C^\infty$ for $t>0$, continuous dependence, $F_{\rm TECT}$ non-increasing. ($\mu^2>0$
is the disordered-side positive linear gap, **not** BCC condensation.)

## Scope

NARROW (operator review 2026-06-23): one real scalar field, fixed periodic cell, $\tfrac32<s\le2$. Uses the
lower bound $\lambda_0:=\min_k K(k)\ge\mu^2>0$ (equality non-generic); Sobolev direction
$H^2\subseteq H^{4\beta}=X^\beta$ for $\beta\le1/2$ (so the energy $H^2$ a priori bound controls $X^\beta$);
$s>2$ persistence is **not** claimed. **NOT** the full Class-II multi-field action; **NOT** the $\mu^2<0$
condensate branch — those are separate targets $\mathrm{A2}_{\text{full Class II}}$, $\mathrm{A2}_{\mu^2<0}$.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): A2-H1-KERNEL-POSITIVITY ($\mu^2>0$ ⇒ $\lambda_0\ge\mu^2>0$), A2-H2-SEXTIC-COERCIVITY ($\gamma>0$) — both SATISFIED@anchor
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED.

- `claims/A2-PDE-WELLPOSED/notes/a2-local-global-wellposedness-260623-260623-v1.1.tex.txt` — proof (operator-corrected v1.1: $\lambda_0$ lower bound, Sobolev direction, $s$-range, narrow scope)
- `codes/foundations/a2_wellposedness_checks.py` — 8/8 self-tests (v1.1)
- `claims/A2-PDE-WELLPOSED/runs/a2_wellposedness_checks.json` — artefact

## Falsifier

Finite-time blow-up or non-uniqueness for some $\phi_0\in H^s$ ($\tfrac32<s\le2$) at $\mu^2>0,\gamma>0$; or $\lambda_0:=\min_k K(k)\le0$ (loss of sectoriality).

## Reproduction

Status: **AVAILABLE**. Command: `python codes/foundations/a2_wellposedness_checks.py` → 8/8 PASS, exit 0.

## No-overclaim

$s>2$ persistence; the full Class-II multi-field action; the $\mu^2<0$ condensate branch; any claim that $\mu^2>0$ proves BCC condensation (it is the disordered-side linear gap); a unique global **minimiser** (Sector B); well-posedness for $\gamma\le0$.

## Devil's-advocate record

Operator review 2026-06-23 raised three defects, all UPHELD and fixed in note v1.1 §7: (α) $\inf\operatorname{spec}L=\mu^2$ false on a generic cell → use $\lambda_0\ge\mu^2>0$; (β) Sobolev inclusion backwards → $H^2\subseteq X^\beta$ (conclusion recovered); (γ) proof closes only for $\tfrac32<s\le2$ → theorem range restricted, $s>2$ not claimed. Scope narrowed to scalar/periodic/$\mu^2>0$/$\gamma>0$. Quantitative sanity check: 8/8 verification (v1.1).

## History

- 2026-06-05 — Seeded T1 OPEN (no legacy evidence).
- 2026-06-23 — A2 deep-dive: local + global well-posedness derived (analytic-semigroup). v1.0 → operator review (3 defects) → v1.1 corrected + scope narrowed. Proposed T1→T6 PROVED CONDITIONAL (scalar/periodic/$\mu^2>0$/$\gamma>0$, $3/2<s\le2$), RE-SUBMITTED for sign-off.

## Next required action

Operator sign-off of the narrowed T6; then **A3-RENORMALISATION** (continuum limit); separately $\mathrm{A2}_{\text{full Class II}}$ and $\mathrm{A2}_{\mu^2<0}$.
