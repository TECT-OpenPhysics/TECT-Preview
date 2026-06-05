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
| **STEP-5B** | Beyond-layer class-wide bound (admissible-class exhaustiveness step; pattern-generic Gershgorin attack designated). **The gateway for any whole-Reading-H T6 discussion.** | OPEN — top priority | `archive/legacy/notes/Math442/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt` |
| **G3PB-III** | G3′-b(iii): higher-shell / anisotropic harmonic dominance — AddF ratio extraction | OPEN — priority 2 | legacy: Math442 |
| **G1PP-3B-HEX** | G1″-3b-HEX exact-Wick bracket (HEX competitor margin) | CLOSED within H-layer scope — Math437 v1.2 F10-REPAIR RESOLVED, verified by dual audit | `archive/legacy/notes/` Math437 v1.2 / Math440 / Math441 / Math442 |
| **ESTIMATOR-UPGRADE** | GAP-2 instance for Reading-H: estimator-grade $\Delta F$ → controlled error bound | OPEN | `archive/legacy/notes/` Math427–Math436 enumerated-reading chain (migrated batch 2) |
| **ROBUSTNESS-MU2** | Open-neighbourhood robustness of the selection result in $\mu^2$ around $\mu^2=0.005$ | OPEN | governance draft §15 |
| **H-SUPPRESSION-DISCHARGE** | Discharge of the (H-suppression) hypothesis (full TECT-Hessian + Wetterich projection + negative-eigenvalue derivation) | OPEN | legacy: Pillar-2 record |
| **CP-UNITARITY** | CP structure and unitarity completion of the per-generation quantum-consistency closure | OPEN | legacy: Pillar-7 record |
| **SCHEME-2LOOP** | 2-loop scheme-independence audit of the gravity 1-loop closure | OPEN (recommended) | legacy: Pillar-3 record |
| **PRED-G-FREEZE** | Pre-registered input freeze for an independent $a_{\rm BCC}$ → $G$ prediction | OPEN | `predictions/prediction-ledger.md` |

## Named hypotheses

| Hypothesis | Statement | Discharge path |
|---|---|---|
| **H-LAYER** | Transcribed from Math437 v1.2 §Hypotheses (`archive/legacy/notes/Math437/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt`): the comparison is the **isotropic Gaussian–Hartree variational layer**. Within the diagonal-Gaussian class the isotropic dressing is the infimum (Math427, T6 conditional on H-diag); beyond-diagonal refinements (Bloch off-diagonal, $\sigma(x)$ inhomogeneity) are EXECUTED for the five enumerated readings (Math428–432, Math434, Math436) but remain unexecuted for non-enumerated patterns — that residual is exactly STEP-5B. | STEP-5B (beyond-layer class-wide bound) |
| **H-A0** | Transcribed from Math437 v1.2 §Hypotheses (slimmed in v1.1): the $A=0$ uniqueness and zero-at-gap structure are certified numerically on a consistent quadrature scheme (internal convergence $3.1\times10^{-5}$; the $5.5\times10^{-3}$ scheme-gap offset is a recorded measure-convention systematic). PENALTY constants do **not** rest on this hypothesis: Lemma 3's $P_B$ floors are quadrature-free closed forms at the production anchors ($M_R=0.109414>M_c$, $4.1\times$ margin). | Quadrature-scheme unification of the recorded offset systematic, or an analytic $A=0$ uniqueness proof |
| **H-SUPPRESSION** | Suppression hypothesis of the kinematic-Lorentz theorem (legacy PC-3C form). | H-SUPPRESSION-DISCHARGE |
| **H-LEGACY-CHAIN** | The cited legacy evidence chain is sound as recorded; TSv2 re-validation pending (migration plan M1/M2). Carried by every legacy-translated T6 entry until its pointers are migration-clean. | `governance/migration-plan.md` M2 |
| **H-CP2-BUNDLE-DATA** | The three-patch Čech bundle data on $\mathbb{CP}^2$ as constructed in legacy Math162/Math167. | Migration (plan phase M1) + re-verification of cocycle closure |

## Gate lifecycle

OPEN → CLOSED (with closing evidence + date) or RETIRED (statement absorbed
elsewhere; pointer mandatory). Closing a gate never silently promotes a claim;
promotions follow `governance/claim-standard.md` §5.

## History

- 2026-06-05 — Registry created (bootstrap).
- 2026-06-05 — Migration batch 1 (plan phase M1): H-LAYER / H-A0 placeholder entries replaced by
  verbatim transcriptions from Math437 v1.2; STEP-5B and G1PP-3B-HEX source
  pointers resolved to `archive/legacy/` paths.
- 2026-06-05 — Archive per-tag reorganisation: source pointers updated to
  `archive/legacy/notes/<Tag>/` layout.
- 2026-06-05 — Migration batch 2: the H-LAYER justification chain and the
  estimator chain (Math427–432, Math434+AddA, Math436) migrated and
  re-validated (167/167); ESTIMATOR-UPGRADE source pointer resolved.
