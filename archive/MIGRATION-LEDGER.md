# Migration Ledger — legacy corpus → this repository

Policy: `governance/migration-plan.md`. One row per legacy file touched.
Dispositions: MIGRATED-VERBATIM / REWRITTEN / SUPERSEDED / DROPPED /
COLD-ARCHIVE. A claim is migration-clean when its `legacy_evidence` has no
unresolved `legacy:` pointer.

**Target layout** (since 2026-06-05 reorganisation): migrated files live under
`archive/legacy/` in the per-tag layout — `notes/<TheoryTag>/` (all versions
together), `scripts/` (flat, runnable as-is), `artefacts/<TheoryTag>/`. The
"Legacy path" column below records the ORIGINAL path in the legacy repository;
the target is determined by file kind + tag. Lookup table:
`archive/legacy/INDEX.md`.

## Migration batch 1 — Sector-B evidence chain (plan phase M1, 2026-06-05)

Re-validation: all four §6.3.8 verification scripts re-run in a fresh sandbox
environment (python 3.12, numpy 2.2.6) — **277/277 self-test asserts PASS**;
regenerated JSONs match archived artefacts within rel_tol $10^{-9}$
(`runs/A1-KERNEL-CONV/260605-migration-revalidation/`, `runs/B2-PROPA-HLAYER/260605-migration-revalidation/`).
One finding: **STALE-ARTEFACT** — the archived Math437 `step5_class_closure.json`
predates the R1 repair (v1.0-era verdict string; numerics identical); the fresh
artefact under `runs/` is canonical for TSv2 citation. Convention check: all
items are themselves the corrected-convention ($r_{\rm braz}=K(q_0)=\mu^2$)
lineage — no stale-convention content. Sign-off: migration directed in-session
2026-06-05; **formal operator sign-off for B2-feeding rows: PENDING**.
Batch record note: `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-v1.0.md`.

All dispositions in this batch are MIGRATED-VERBATIM.

| Legacy path (original) | Consuming claims | Re-validation | Sign-off |
|---|---|---|---|
| `Docs/math/TECT-Math426-G4-Kernel-Convention-Reconciliation.tex.txt` | A1 | script re-run 10/10 | n/a (T5) |
| `Docs/math/TECT-Math426-AddA-Audit-Acceptance-Body-Corrections-G1prime-Spec.tex.txt` | A1 | chain addendum (text) | n/a (T5) |
| `Docs/math/TECT-Math426-AddB-ThirdPass-Body-Summaries-and-AddE-Citation-Rule.tex.txt` | A1 | chain addendum (text) | n/a (T5) |
| `Docs/math/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.0.tex.txt` | A1 (audit trail; superseded by v1.1) | banner intact | n/a (T5) |
| `Docs/math/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.1.tex.txt` | A1 (canonical) | script re-run 101/101 | n/a (T5) |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.0.tex.txt` | B2 (audit trail; superseded) | banner intact | PENDING |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.1.tex.txt` | B2 (audit trail; superseded) | banner intact | PENDING |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt` | B1, B2 (canonical) | script re-run 91/91; H-LAYER/H-A0 transcribed to GATES.md | PENDING |
| `Docs/math/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt` | B2 (audit 1) | script re-run 75/75 | PENDING |
| `Docs/math/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt` | B2 (audit 2) | audit note (text) | PENDING |
| `Docs/math/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt` | B1, B2 (certification) | closure note (text) | PENDING |
| `Codes/supplementary/Math426_g4_kernel_reconciliation.py` | A1 | re-run 10/10 PASS | n/a (T5) |
| `Codes/supplementary/Math435_g6_corrected_variable_cascade.py` | A1 | re-run 101/101 PASS | n/a (T5) |
| `Codes/supplementary/Math437_step5_class_closure.py` | B2 | re-run 91/91 PASS | PENDING |
| `Codes/supplementary/Math440_audit_secondwave_recheck.py` | B2 | re-run 75/75 PASS | PENDING |
| `Codes/supplementary/Math374_canonical_BCC_hessian.py` | A1, B2 (import dependency) | exercised by all re-runs | PENDING |
| `Codes/supplementary/Math424_AddA_reading_uniqueness.py` | A1, B2 (import dependency) | exercised by all re-runs | PENDING |
| `Codes/supplementary/Math400_AddE_brazovskii_one_loop.py` | A1, B2 (import dependency) | exercised by all re-runs | PENDING |
| `Runs/math/Math426/g4_kernel_reconciliation.json` | A1 | reproduced within 1e-9 | n/a (T5) |
| `Runs/math/Math435/g6_corrected_cascade.json` | A1 | reproduced within 1e-9 | n/a (T5) |
| `Runs/math/Math435/sweep_checkpoint.json` | A1 (sweep provenance) | provenance file | n/a (T5) |
| `Runs/math/Math437/step5_class_closure.json` | B2 | reproduced within 1e-9; STALE-ARTEFACT verdict string (numerics identical) | PENDING |
| `Runs/math/Math440/audit_recheck.json` | B2 | reproduced within 1e-9 | PENDING |

## Translation events (not file migrations)

| Event | Source | Result | Date |
|---|---|---|---|
| Ledger seeding | legacy `Docs/status/TOE-FACT-SHEET.md` (snapshot 2026-06-05, Math442 state) | 17 claim cards under `claims/`, translated per `governance/tier-system.md` §4 | 2026-06-05 |
| Hypothesis transcription | Math437 v1.2 §Hypotheses | H-LAYER, H-A0 verbatim entries in `claims/GATES.md` | 2026-06-05 |
| Archive reorganisation | flat original-path mirror | per-tag layout (`notes/<Tag>/`, `scripts/`, `artefacts/<Tag>/`) + `INDEX.md`; all card paths updated; scripts re-verified runnable post-move (10/10) | 2026-06-05 |

## Migration queue (plan phase M1; updated 2026-06-05)

1. ~~Sector-B chain (Math426/435/437/440/441/442 + scripts + JSONs)~~ — **DONE
   (batch 1)**. A1, B2 migration-clean; B1 partially resolved.
2. **Math431-HEX estimator chain** (+ Math428–432/434/436 enumerated-reading
   notes) — required for B1-RH-ENUM migration-cleanness and Packet A.
3. Math427 (isotropic-dressing infimum, H-LAYER support) — strengthens the
   H-LAYER justification chain.
4. T7-candidates: `C2-LORENTZ-EMERGENT`, `C3-EP`, `D3-CHIRALITY`.
