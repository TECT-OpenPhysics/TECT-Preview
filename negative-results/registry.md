# Negative-Result Registry

Failures are trust assets. Entries are never deleted. Format:
(branch/claim | failure mode | evidence | consequence). Tags: `R-` retracted
result, `F-` fired falsification gate, `NG-` no-go finding.

| Tag | Branch / claim | Failure mode | Evidence | Consequence |
|---|---|---|---|---|
| NG-2026-legacy-convention | old $r=K(0)$ no-condensation convention | wrong variable convention | legacy: Math426 cascade | replaced by $r_{\rm braz}=K(q_0)=\mu^2$; A1-KERNEL-CONV registers the corrected convention |
| NG-2026-legacy-ordered-vacuum | fixed ordered BCC vacuum as ground state | fluctuation restoration | legacy: Reading-H selection chain | Reading-H selected instead (B1-RH-ENUM); ordered-vacuum reading retired |
| R-2026-legacy-newtonG-label | Newton $G$ "independently predicted / T7" label | independent prediction missing ($a_{\rm BCC}$ fixed by $G_{\rm obs}$) | legacy: governance audit | downgraded to RELATION DERIVED / VALUE MATCHED; managed as T6/T7-SPLIT (C5-NEWTON-G) |
| R-2026-legacy-rh-overclaim | estimator-only Reading-H claim above T5 | controlled error bound missing | legacy: estimator chain audits | remains T5 CLOSED@ESTIMATOR-GRADE until ESTIMATOR-UPGRADE and STEP-5B close (B1-RH-ENUM) |
| F-2026-04-30-flat-cartan | Pillar-4 sub-task-2 "closure completed" (flat-Cartan forcing, Mechanism A) | falsified by $c_2(E)=-40\neq 0$ on canonical $\mathbb{CP}^2$ | legacy: Math174, Math245 rollback | sub-task 2 back to T3 (D2-GAUGE-FORCING); Mechanism A refuted; Mechanism B insufficient alone |
| NG-2026-legacy-classical-hbar | classical-field-theoretic derivation of $\hbar$ (8 routes) | each route fails (4 Math59 + 3 Math59-v3 + 1 R5) | legacy: Math59, Math59-v3, R5 record | $\hbar$ stays an external phenomenological parameter; phase-transition programme registered at T2 (E2-HBAR-ORIGIN) |

## Process-grade negative results (carried as lessons, enforced in governance)

- Round-summary over-claim incident (legacy 2026-04-24): higher-tier summaries
  may never outrun pillar-level notes → single-source-of-truth rule
  (`status.json` → generated `CLAIMS.md`).
- Five-rollback cluster (legacy 2026-04-28/29): each rollback was catchable by
  one elementary quantitative sanity check → mandatory sanity-check rule
  (`governance/verification-standard.md` §6).
- Tier-overstatement cluster (legacy 2026-05-27): rushed multi-pillar passes
  produce overstatement → one-claim-per-turn and promotion-procedure rules
  (`governance/claim-standard.md` §5).

## History

- 2026-06-05 — Registry seeded from the legacy record during bootstrap.
