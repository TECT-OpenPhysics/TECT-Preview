# A1-KERNEL-CONV — Production-kernel convention and G6 recomputation cascade

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

The production kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$ with Brazovskii shell mass $r_{\rm braz}=K(q_0)=\mu^2$ is the unique normative convention of the canonical record; the corrected-convention recomputation cascade (G6) passes over the canonical note set.

## Scope

CLOSED@CANONICAL-NOTE-SET (2026-06 legacy snapshot). A convention-integrity closure, not a physics theorem.

**Notes**: M1 re-validated 2026-06-05: 111/111 self-test asserts pass in a fresh environment; archived artefacts reproduced exactly (runs/A1-KERNEL-CONV/260605-m1-reval/). Migration-clean: no legacy: pointers remain.

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: none

## Evidence

Grades: EXECUTED. Evidence pointers (`archive/...` = migrated + re-validated; `legacy:` = pending):

- `archive/legacy/Docs/math/TECT-Math426-G4-Kernel-Convention-Reconciliation.tex.txt`
- `archive/legacy/Docs/math/TECT-Math426-AddA-Audit-Acceptance-Body-Corrections-G1prime-Spec.tex.txt`
- `archive/legacy/Docs/math/TECT-Math426-AddB-ThirdPass-Body-Summaries-and-AddE-Citation-Rule.tex.txt`
- `archive/legacy/Docs/math/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.1.tex.txt`
- `archive/legacy/Codes/supplementary/Math426_g4_kernel_reconciliation.py`
- `archive/legacy/Codes/supplementary/Math435_g6_corrected_variable_cascade.py`
- `archive/legacy/Runs/math/Math426/g4_kernel_reconciliation.json`
- `archive/legacy/Runs/math/Math435/g6_corrected_cascade.json`

Legacy pillar(s): none · Legacy tier label: n/a

## Falsifier

Discovery of a canonical-record computation whose registered conclusion changes under the corrected convention $r_{\rm braz}=K(q_0)$.

## Reproduction

Status: **AVAILABLE**. Command: `cd archive/legacy/Codes/supplementary && python Math426_g4_kernel_reconciliation.py && python Math435_g6_corrected_variable_cascade.py`.

Expected: claims: 10/10 PASS then claims: 101/101 PASS (both exit 0); regenerated JSONs match archived artefacts within rel_tol 1e-9

## No-overclaim

G6 CLOSED-PASS is a recomputation cascade, not a tier gate for any physics claim.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.
- 2026-06-05 — M1 migration: Math426/AddA/AddB + Math435 v1.0/v1.1 chain, scripts, and artefacts migrated to `archive/legacy/`; re-validated 111/111 asserts (fresh env), artefacts identical within 1e-9. Reproduction AVAILABLE. Migration-clean.

## Next required action

Wrap the two-script sequence into verify_claim.py (one-command contract) and wire into CI.
