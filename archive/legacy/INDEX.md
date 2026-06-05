# archive/legacy — per-tag index

| Tag | Notes (all versions) | Script | Artefacts | Consuming claims | Batch |
|---|---|---|---|---|---|
| Math426 | G4 kernel-convention reconciliation + AddA + AddB | `scripts/Math426_g4_kernel_reconciliation.py` | `artefacts/Math426/g4_kernel_reconciliation.json` | A1 | batch 1 (2026-06-05) |
| Math435 | G6 corrected-variable recomputation cascade v1.0, v1.1 | `scripts/Math435_g6_corrected_variable_cascade.py` | `artefacts/Math435/g6_corrected_cascade.json`, `sweep_checkpoint.json` | A1 | batch 1 (2026-06-05) |
| Math437 | Step-5 pattern-universal restoration (isotropic layer) v1.0, v1.1, v1.2 | `scripts/Math437_step5_class_closure.py` | `artefacts/Math437/step5_class_closure.json` (STALE-ARTEFACT: pre-repair verdict string; numerics valid — canonical fresh artefact in `runs/B2-PROPA-HLAYER/260605-migration-revalidation/`) | B1, B2 | batch 1 (2026-06-05) |
| Math440 | §15.5 consolidated audit, second wave (PARTIAL) v1.0 | `scripts/Math440_audit_secondwave_recheck.py` | `artefacts/Math440/audit_recheck.json` | B2 | batch 1 (2026-06-05) |
| Math441 | F10 second-look of Math437 v1.1 repair (PARTIAL) v1.0 | — | — | B2 | batch 1 (2026-06-05) |
| Math442 | F10 closure: Math437 v1.2 CERTIFIED v1.0 | — | — | B1, B2 | batch 1 (2026-06-05) |
| Math374 | (script-only migration: import dependency) | `scripts/Math374_canonical_BCC_hessian.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |
| Math400 | (script-only migration: import dependency) | `scripts/Math400_AddE_brazovskii_one_loop.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |
| Math424 | (script-only migration: import dependency) | `scripts/Math424_AddA_reading_uniqueness.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |

Script-only rows: the corresponding notes migrate when a claim consumes them
directly (migration-plan §1.1).

## Reproduction quickstart

```bash
cd archive/legacy/scripts
python Math426_g4_kernel_reconciliation.py     # claims: 10/10 PASS
python Math435_g6_corrected_variable_cascade.py # claims: 101/101 PASS
python Math437_step5_class_closure.py           # claims 91/91
python Math440_audit_secondwave_recheck.py      # claims 75/75
```

(Scripts write their JSON output to a `Runs/` directory relative to the
current working directory; compare against `artefacts/` and the canonical
fresh artefacts under `runs/<claim-id>/260605-migration-revalidation/`.)
