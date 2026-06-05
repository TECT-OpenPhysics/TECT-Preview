# How to review (or attack) TECT in 30 minutes

This repository is designed to be falsified efficiently. This page tells you
where the weakest joints are and how to hit them.

## 1. Validate the ledger (1 minute)

```bash
python verification/scripts/lint_claims.py
```

Exit 0 means: every claim card parses, the dependency DAG is acyclic, and no
claim overstates its tier relative to its dependencies and hypotheses.

## 2. Read `CLAIMS.md` (5 minutes)

Every claim shows: tier, scope, evidence grade, open gates, and a falsifier.
The tier vocabulary is in `governance/tier-system.md`. Two readings matter:

- Anything at **T5** is closed *only within its pinned scope*. The scope string
  is part of the claim. Attacking the scope boundary is fair and welcome.
- Anything at **T6** is a theorem *modulo named hypotheses*. The hypotheses are
  listed on the card. Attacking a hypothesis is attacking the claim.

## 3. Known weakest joints (honest map)

| Joint | Why it is weak | Where |
|---|---|---|
| **Step-5b** — beyond-layer class-wide bound | Reading-H selection is enumerated-ensemble only; the admissible-class exhaustiveness theorem is open. This is the single gateway to any vacuum-uniqueness claim. | `claims/B1-RH-ENUM`, `claims/GATES.md` |
| **Estimator gap (GAP-2)** | Core $\Delta F$ results are estimator-grade without a controlled error bound $\varepsilon_{\rm ctrl}$. | `claims/B1-RH-ENUM` |
| **Constants firewall (GAP-3)** | No constant is currently PREDICTED. Newton $G$ is a derived *relation* with a matched value — if you find a place where the repository says otherwise, that is a registry defect; please report it. | `claims/C5-NEWTON-G`, `predictions/` |
| **Sector-D dependence on vacuum selection** | Gauge/matter topology results may depend on Reading-H; their tiers are capped while GAP-1 is open. | `claims/D2-GAUGE-FORCING` |
| **Origin of $\hbar$** | Classical derivation routes are REFUTED (8 documented failures). The phase-transition programme is T2 conjecture-grade. | `claims/E3-HBAR-ORIGIN`, `negative-results/` |

## 4. How to falsify a specific claim

Each `claims/<ID>/claim.md` carries a **Falsifier** section, e.g. for Reading-H:

$$
\exists\,\mathcal R\in\mathcal A_{\rm enum}\ \text{such that}\ \Delta F[\mathcal R]<0 .
$$

Produce such an $\mathcal R$ (or a counterexample to a named hypothesis) and the
claim is retired to `negative-results/registry.md` with credit. Reproduction
commands and expected outputs are on the card; environment pinning is in
`governance/verification-standard.md`.

## 5. Reporting

Open an issue (once the GitHub mirror is live) or write to the maintainer.
Review rounds are archived under `reviews/` with verdicts; confirmed defects get
errata under `reviews/errata/` linked to the claim ID.

## 6. What you should NOT take at face value

- Legacy evidence pointers (`legacy:` prefix) cite the pre-2026-06 corpus that
  has not yet been re-validated under this governance. Claims resting on them
  are capped at T6 and flagged.
- Any prose anywhere that sounds stronger than the registered tier is a defect,
  not a claim. The ledger wins. Report the prose.
