# Q3LOCK R-497 loop-limit authority-chain disposition

**Date:** 2026-09-08  
**Exploration:** EXP-001666  
**Task:** T-054  
**Status:** T0 source-integrity audit; claim-nonbearing; PDF deferred

## Question

Does the R-497 source chain still contain the historical EXP-000782 sentence
that incorrectly claims total-variation convergence, and is the current paper
using the corrected weak-convergence and uniform-integrability route without
silently treating the historical sentence as a theorem premise?

## Source comparison

1. The R-497 manifest pins the 2026-08-04 EXP-000782 certificate at
   `b6487a9381bef20cdf1a9abc4dfdec9aa40f69b0b73697595c263ffe574a4d89`.
   The certificate retains the historical sentence at lines 197--200:
   “Dominated convergence gives total variation convergence to the exact
   Feynman--Kac loop law.”  Those bytes are retained as provenance and are not
   a valid current proof step.
2. The append-only P-06 correction audit
   `strategy/q3lock-continuous-loop-weak-not-tv-audit-260905.md` is already a
   hash-pinned R-497 source at
   `71ead8d0f88e98f7f535104587e24193e52fcb5fee652353b37a0c9020575d79`.
   It proves that polygonal finite-mesh laws and the nondegenerate exact loop
   law have incompatible supports at every finite mesh, so total-variation
   convergence is impossible.  It replaces that sentence by weak convergence
   on compact residual sets plus truncation and uniform-integrability control.
3. The current manuscript consumes the corrected route.  Its equation
   `eq:weighted-loop-limit` states weak convergence on `\mathsf E_L` and
   explicitly says “not total-variation convergence” (lines 504--513).
   The source-moment passage later uses truncation and uniform integrability
   (lines 600--612 and 1528--1538), and the FKG passage applies weak convergence
   only to bounded continuous `F`, `G`, and `FG` (lines 1228--1234).

## Disposition

The authority chain is **historical-source plus explicit correction**, not a
claim that every byte of the earliest certificate is mathematically current.
The old total-variation sentence remains available for auditability, but it is
retired and must not be cited as support for FKG, source derivatives, or the
thermodynamic limit.  The current manuscript is textually consistent with the
correction audit.  This resolves a provenance/consumer ambiguity only; it does
not independently prove the Gaussian covariance convergence, compact residual
convergence, source-uniform estimates, selected-limit transfer, or any later
DLR/cusp conclusion.

The external mathematics reviewer must therefore assess the corrected weak/UI
argument directly and record whether it closes the fixed-volume P-06 obligation.
The reviewer should not accept the historical total-variation sentence as a
shortcut, and should not treat the presence of the correction note as signed
acceptance.

## Adversarial checks

| objection | disposition | reason |
|---|---|---|
| Retaining the old certificate makes the false TV statement a current premise. | **UPHELD AS A RISK; MITIGATED BY PRECEDENCE** | The correction audit is pinned in the same R-497 source list, the manuscript states weak convergence, and the review packet labels P-06 open. A signed reviewer must still confirm this reading. |
| Removing the old certificate would hide provenance. | **DISMISSED** | Historical bytes remain hash-pinned; only their consumer status is corrected. |
| Weak convergence by itself justifies unbounded source derivatives. | **UPHELD AS FALSE** | The manuscript and correction audit require truncation and mesh-uniform uniform integrability. |
| This audit closes continuous-loop FKG or the phase theorem. | **DISMISSED** | It is a fixed-volume source-integrity disposition; all A1--A23 rows and external review remain open. |

## Boundary and next action

No claim card, theorem tier, Sector A--F status, paper PDF, submission, or
physical interpretation changes. The next action is a signed line-by-line
P-06 review against the corrected manuscript and the pinned correction audit,
followed by the already required final content freeze and clean replay. PDF
generation remains forbidden until those gates are complete.

## Evidence

- `strategy/q3lock-exp782-independent-result-manifest-260905.json#source_files`
- `strategy/pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split-certificate-260804.md:197-204`
- `strategy/q3lock-continuous-loop-weak-not-tv-audit-260905.md#3-total-variation-convergence-is-impossible`
- `publish/papers/q3lock-phase-coexistence/manuscript.tex:eq:weighted-loop-limit`
- `publish/papers/q3lock-phase-coexistence/proof-audit.md#A11`
- `publish/papers/q3lock-phase-coexistence/submission-readiness.md#R2`

