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
(`claims/A1-KERNEL-CONV/runs/260605-migration-revalidation/`, `claims/B2-PROPA-HLAYER/runs/260605-migration-revalidation/`).
One finding: **STALE-ARTEFACT** — the archived Math437 `step5_class_closure.json`
predates the R1 repair (v1.0-era verdict string; numerics identical); the fresh
artefact under `runs/` is canonical for TSv2 citation. Convention check: all
items are themselves the corrected-convention ($r_{\rm braz}=K(q_0)=\mu^2$)
lineage — no stale-convention content. Sign-off: **SIGNED 2026-06-05** (operator review verdict:
"B2-PROPA-HLAYER migration v1.3 = PASS"; chain migration-clean,
reproducible, 277/277).
Batch record note: `claims/B2-PROPA-HLAYER/notes/proposition-a-migration-revalidation-260605-260605-v1.4.tex.txt` (+ PDF beside it; v1.0 .md / v1.1 / v1.2 superseded re-issues, all kept).

All dispositions in this batch are MIGRATED-VERBATIM.

| Legacy path (original) | Consuming claims | Re-validation | Sign-off |
|---|---|---|---|
| `Docs/math/TECT-Math426-G4-Kernel-Convention-Reconciliation.tex.txt` | A1 | script re-run 10/10 | n/a (T5) |
| `Docs/math/TECT-Math426-AddA-Audit-Acceptance-Body-Corrections-G1prime-Spec.tex.txt` | A1 | chain addendum (text) | n/a (T5) |
| `Docs/math/TECT-Math426-AddB-ThirdPass-Body-Summaries-and-AddE-Citation-Rule.tex.txt` | A1 | chain addendum (text) | n/a (T5) |
| `Docs/math/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.0.tex.txt` | A1 (audit trail; superseded by v1.1) | banner intact | n/a (T5) |
| `Docs/math/TECT-Math435-G6-Corrected-Variable-Recomputation-Cascade-260604-v1.1.tex.txt` | A1 (canonical) | script re-run 101/101 | n/a (T5) |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.0.tex.txt` | B2 (audit trail; superseded) | banner intact | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.1.tex.txt` | B2 (audit trail; superseded) | banner intact | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math437-Step5-Pattern-Universal-Restoration-Isotropic-Layer-260604-v1.2.tex.txt` | B1, B2 (canonical) | script re-run 91/91; H-LAYER/H-A0 transcribed to GATES.md | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math440-Section15p5-Consolidated-Audit-SecondWave-PARTIAL-260605-v1.0.tex.txt` | B2 (audit 1) | script re-run 75/75 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math441-F10-SecondLook-Math437v1p1-Repair-PARTIAL-260605-v1.0.tex.txt` | B2 (audit 2) | audit note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math442-F10-Closure-Math437v1p2-CERTIFIED-260605-v1.0.tex.txt` | B1, B2 (certification) | closure note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math426_g4_kernel_reconciliation.py` | A1 | re-run 10/10 PASS | n/a (T5) |
| `Codes/supplementary/Math435_g6_corrected_variable_cascade.py` | A1 | re-run 101/101 PASS | n/a (T5) |
| `Codes/supplementary/Math437_step5_class_closure.py` | B2 | re-run 91/91 PASS | SIGNED 2026-06-05 |
| `Codes/supplementary/Math440_audit_secondwave_recheck.py` | B2 | re-run 75/75 PASS | SIGNED 2026-06-05 |
| `Codes/supplementary/Math374_canonical_BCC_hessian.py` | A1, B2 (import dependency) | exercised by all re-runs | SIGNED 2026-06-05 |
| `Codes/supplementary/Math424_AddA_reading_uniqueness.py` | A1, B2 (import dependency) | exercised by all re-runs | SIGNED 2026-06-05 |
| `Codes/supplementary/Math400_AddE_brazovskii_one_loop.py` | A1, B2 (import dependency) | exercised by all re-runs | SIGNED 2026-06-05 |
| `Runs/math/Math426/g4_kernel_reconciliation.json` | A1 | reproduced within 1e-9 | n/a (T5) |
| `Runs/math/Math435/g6_corrected_cascade.json` | A1 | reproduced within 1e-9 | n/a (T5) |
| `Runs/math/Math435/sweep_checkpoint.json` | A1 (sweep provenance) | provenance file | n/a (T5) |
| `Runs/math/Math437/step5_class_closure.json` | B2 | reproduced within 1e-9; STALE-ARTEFACT verdict string (numerics identical) | SIGNED 2026-06-05 |
| `Runs/math/Math440/audit_recheck.json` | B2 | reproduced within 1e-9 | SIGNED 2026-06-05 |

## Migration batch 2 — enumerated-reading / estimator chain (plan phase M1, 2026-06-05)

Goal: make `B1-RH-ENUM` migration-clean and ground the H-LAYER justification
chain. Re-validation: all eight verification scripts re-run fresh (python
3.12, numpy 2.2.6) — **167/167 self-test asserts PASS** (5+21+19+11+15+25+22+49);
all regenerated JSONs identical to the archived artefacts within rel_tol
$10^{-9}$ — **zero diffs, zero stale-artefact findings** (contrast batch 1's
F-1). Math434/Math436 are checkpoint-resumable by design and completed within
one budget window on this hardware; their archived `state.json` files are kept
as provenance. Fresh artefacts:
`claims/B1-RH-ENUM/runs/260605-migration-revalidation/` (8 JSONs + summary).
Sign-off: rows feed B1 (T5) directly and support hypothesis H-LAYER of the
T6 claim — **operator sign-off: SIGNED 2026-06-05** (review verdict:
"B1-RH-ENUM migration = PASS; evidence chain migration-clean and
reproducible").
Batch record note: `claims/B1-RH-ENUM/notes/enumerated-readings-migration-revalidation-260605-260605-v1.1.tex.txt`.

All dispositions in this batch are MIGRATED-VERBATIM.

| Legacy path (original) | Consuming claims | Re-validation | Sign-off |
|---|---|---|---|
| `Docs/math/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec.tex.txt` | B1 (audit trail; superseded) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math427-G1prime-Diagonal-Isotropy-Theorem-and-G1doubleprime-Spec-260604-v1.1.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math427_g1prime_diagonal_isotropy.py` | B1 | re-run 5/5 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math427/g1prime_diagonal_isotropy.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored.tex.txt` | B1 (audit trail; superseded) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math428-G1doubleprime-BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored-260604-v1.1.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math428_g1doubleprime_bloch_logdet.py` | B1 | re-run 21/21 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math428/g1doubleprime_bloch_logdet.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.0.tex.txt` | B1 (audit trail; superseded) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math429-G1pp1prime-Inhomogeneous-Wick-M-Scan-PASS-260604-v1.1.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math429_g1pp1prime_inhomogeneous_wick.py` | B1 | re-run 19/19 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math429/g1pp1prime_inhomwick.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math430-G1pp2-Dense-Surface-Convergence-PASS-260604-v1.0.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math430_g1pp2_dense_surface_convergence.py` | B1 | re-run 11/11 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math430/g1pp2_surface_convergence.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math431-G1pp3-LAM-HEX-FCC-PASS-260604-v1.0.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math431_g1pp3_lam_hex_fcc.py` | B1 | re-run 15/15 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math431/g1pp3_lam_hex_fcc.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.0.tex.txt` | B1 (audit trail; superseded) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math432-G3prime-Two-Shell-Ensemble-Race-PASS-260604-v1.1.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math432_g3prime_multishell_ensemble.py` | B1 | re-run 25/25 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math432/g3prime_multishell_ensemble.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math434-Section15p5-Independent-Audit-ReadingH-T5-Candidacy-PASS-260604-v1.0.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math434-AddA-T5-Promotion-Record-ReadingH-Selection-260604-v1.0.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math434_lam_exact_wick_bracket.py` | B1 | re-run 22/22 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math434/lam_exact_wick_bracket.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |
| `Runs/math/Math434/state.json` | B1 | checkpoint state (provenance) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.0.tex.txt` | B1 (audit trail; superseded) | note (text) | SIGNED 2026-06-05 |
| `Docs/math/TECT-Math436-G1pp3b-HEX-Exact-Wick-Bracket-PASS-260604-v1.1.tex.txt` | B1 (canonical) | note (text) | SIGNED 2026-06-05 |
| `Codes/supplementary/Math436_hex_exact_wick_bracket.py` | B1 | re-run 49/49 PASS | SIGNED 2026-06-05 |
| `Runs/math/Math436/hex_exact_wick_bracket.json` | B1 | reproduced within 1e-9 | SIGNED 2026-06-05 |

## Translation events (not file migrations)

| Event | Source | Result | Date |
|---|---|---|---|
| Ledger seeding | legacy `Docs/status/TOE-FACT-SHEET.md` (snapshot 2026-06-05, Math442 state) | 17 claim cards under `claims/`, translated per `governance/tier-system.md` §4 | 2026-06-05 |
| Hypothesis transcription | Math437 v1.2 §Hypotheses | H-LAYER, H-A0 verbatim entries in `claims/GATES.md` | 2026-06-05 |
| Archive reorganisation | flat original-path mirror | per-tag layout (`notes/<Tag>/`, `scripts/`, `artefacts/<Tag>/`) + `INDEX.md`; all card paths updated; scripts re-verified runnable post-move (10/10) | 2026-06-05 |

## Migration queue (plan phase M1; updated 2026-06-05)

1. ~~Sector-B chain (Math426/435/437/440/441/442 + scripts + JSONs)~~ — **DONE
   (batch 1)**. A1, B2 migration-clean; B1 partially resolved.
2. ~~Math427–432 / Math434(+AddA) / Math436 enumerated-reading + estimator
   chain~~ — **DONE (batch 2)**. B1 migration-clean; H-LAYER justification
   chain grounded; Packet-A evidence complete.
3. T7-candidates: `C2-LORENTZ-EMERGENT`, `C3-EP`, `D3-CHIRALITY`.
