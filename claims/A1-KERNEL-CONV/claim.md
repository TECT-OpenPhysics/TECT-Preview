# A1-KERNEL-CONV — Production-kernel convention and G6 recomputation cascade

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-05

## Statement

The production kernel $K(q)=\mu^2+Y(q^2-q_0^2)^2$ with Brazovskii shell mass $r_{\rm braz}=K(q_0)=\mu^2$ is the unique normative convention of the canonical record; the corrected-convention recomputation cascade (G6) passes over the canonical note set.

## Scope

CLOSED@CANONICAL-NOTE-SET (2026-06 legacy snapshot). A convention-integrity closure, not a physics theorem.

**Notes**: M1 re-validated 2026-06-05: 111/111 self-test asserts pass in a fresh environment; archived artefacts reproduced exactly (claims/A1-KERNEL-CONV/runs/260605-migration-revalidation/). Migration-clean: no legacy: pointers remain.

## Dependencies and hypotheses

- Hard dependencies: none
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: none

## Evidence

Grades: EXECUTED. Evidence pointers (`archive/...` = migrated + re-validated; `legacy:` = pending):

- `archive/legacy/notes/Math426/TECT-Math426-G4-Kernel-Convention-Reconciliation.tex.txt`
- `archive/legacy/notes/Math426/TECT-Math426-AddA-Audit-Acceptance-Body-Corrections-G1prime-Spec.tex.txt`
- `archive/legacy/notes/Math426/TECT-Math426-AddB-ThirdPass-Body-Summaries-and-AddE-Citation-Rule.tex.txt`
- `archive/legacy/notes/Math435/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.1.tex.txt`
- `archive/legacy/scripts/Math426_g4_kernel_reconciliation.py`
- `archive/legacy/scripts/Math435_g6_corrected_variable_cascade.py`
- `archive/legacy/artefacts/Math426/g4_kernel_reconciliation.json`
- `archive/legacy/artefacts/Math435/g6_corrected_cascade.json`

Legacy pillar(s): none · Legacy tier label: n/a

## Falsifier

Discovery of a canonical-record computation whose registered conclusion changes under the corrected convention $r_{\rm braz}=K(q_0)$.

## Reproduction

Status: **AVAILABLE**. Command: `cd archive/legacy/scripts && python Math426_g4_kernel_reconciliation.py && python Math435_g6_corrected_variable_cascade.py`.

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
- 2026-06-05 — Archive reorganised to per-tag layout (`notes/<Tag>/`, `scripts/`, `artefacts/<Tag>/`); evidence paths updated; original legacy paths recorded in `archive/MIGRATION-LEDGER.md`. Theory-note record: `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-v1.0.md` (shared batch note).
- 2026-06-05 — Note-format decision: batch record re-issued as v1.1 `.tex.txt`
  (`claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-260605-v1.1.tex.txt`);
  v1.0 `.md` superseded. PDF pipeline verified (`build_note_pdf.py`).
- 2026-06-05 — Batch record re-issued v1.2 (table-width compliance, Overfull 7->0)
  then v1.3 (standard-form banner; FORM-CHECK PASS); PDF now lives beside the
  source in `notes/`; `build/` area retired.

## Next required action

Wrap the two-script sequence into verify_claim.py (one-command contract) and wire into CI.
