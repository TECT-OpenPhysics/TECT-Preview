# Gate & Hypothesis Registry

Gates are promotion conditions; hypotheses are named assumptions that T6 claims
may rest on. Every `open_gates` / `hypotheses` entry in any `status.json` must
exist here. Last updated: 2026-06-05.

## Umbrella gates (GAPs)

| Gate | Statement | Status |
|---|---|---|
| **GAP-1** | Vacuum uniqueness: $\mathcal R_H=\operatorname{arg\,min}_{\mathcal A_{\rm adm}}F_{\rm TECT}$ over the full admissible class | OPEN |
| **GAP-2** | Error control: $\lvert\Delta F_{\rm true}-\Delta F_{\rm est}\rvert\le\varepsilon_{\rm ctrl}$ with $\Delta F_{\rm est}-\varepsilon_{\rm ctrl}>0$ | OPEN |
| **GAP-3** | Constants firewall complete: every constant labelled derived/matched/inserted/predicted with ledger row | OPEN (ledger seeded) |
| **GAP-4** | Falsifiability: at least one observable deviation predicted before fitting | OPEN |

## Named gates

| Gate | Statement | Status | Source |
|---|---|---|---|
| **STEP-5B** | Beyond-layer class-wide bound (admissible-class exhaustiveness step; pattern-generic Gershgorin attack designated). **The gateway for any whole-Reading-H T6 discussion.** | OPEN — top priority | legacy: Math442 operator verdict, 2026-06-05 |
| **G3PB-III** | G3′-b(iii): higher-shell / anisotropic harmonic dominance — AddF ratio extraction | OPEN — priority 2 | legacy: Math442 |
| **G1PP-3B-HEX** | G1″-3b-HEX exact-Wick bracket (HEX competitor margin) | CLOSED within H-layer scope — Math437 v1.2 F10-REPAIR RESOLVED, verified by dual audit | legacy: Math437/440/441/442 |
| **ESTIMATOR-UPGRADE** | GAP-2 instance for Reading-H: estimator-grade $\Delta F$ → controlled error bound | OPEN | legacy: Math4xx estimator chain |
| **ROBUSTNESS-MU2** | Open-neighbourhood robustness of the selection result in $\mu^2$ around $\mu^2=0.005$ | OPEN | governance draft §15 |
| **H-SUPPRESSION-DISCHARGE** | Discharge of the (H-suppression) hypothesis (full TECT-Hessian + Wetterich projection + negative-eigenvalue derivation) | OPEN | legacy: Pillar-2 record |
| **CP-UNITARITY** | CP structure and unitarity completion of the per-generation quantum-consistency closure | OPEN | legacy: Pillar-7 record |
| **SCHEME-2LOOP** | 2-loop scheme-independence audit of the gravity 1-loop closure | OPEN (recommended) | legacy: Pillar-3 record |
| **PRED-G-FREEZE** | Pre-registered input freeze for an independent $a_{\rm BCC}$ → $G$ prediction | OPEN | `predictions/prediction-ledger.md` |

## Named hypotheses

| Hypothesis | Statement | Discharge path |
|---|---|---|
| **H-LAYER** | Restriction to the H-layer class as defined in the legacy Math437 chain. Precise statement to be transcribed verbatim during M1 migration of the Prop-A chain. | STEP-5B (beyond-layer bound) |
| **H-A0** | The A0 hypothesis as named in the legacy Math437/Math442 certification. Precise statement to be transcribed verbatim during M1 migration. | Prop-A chain migration + dedicated discharge note |
| **H-SUPPRESSION** | Suppression hypothesis of the kinematic-Lorentz theorem (legacy PC-3C form). | H-SUPPRESSION-DISCHARGE |
| **H-LEGACY-CHAIN** | The cited legacy evidence chain is sound as recorded; TSv2 re-validation pending (migration plan M1/M2). Carried by every legacy-translated T6 entry until its pointers are migration-clean. | `governance/migration-plan.md` M2 |
| **H-CP2-BUNDLE-DATA** | The three-patch Čech bundle data on $\mathbb{CP}^2$ as constructed in legacy Math162/Math167. | M1 migration + re-verification of cocycle closure |

## Gate lifecycle

OPEN → CLOSED (with closing evidence + date) or RETIRED (statement absorbed
elsewhere; pointer mandatory). Closing a gate never silently promotes a claim;
promotions follow `governance/claim-standard.md` §5.
