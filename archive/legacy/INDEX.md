# archive/legacy — per-tag index

| Tag | Notes (all versions) | Script | Artefacts | Consuming claims | Batch |
|---|---|---|---|---|---|
| Math426 | G4 kernel-convention reconciliation + AddA + AddB | `scripts/Math426_g4_kernel_reconciliation.py` | `artefacts/Math426/g4_kernel_reconciliation.json` | A1 | batch 1 (2026-06-05) |
| Math435 | G6 corrected-variable recomputation cascade v1.0, v1.1 | `scripts/Math435_g6_corrected_variable_cascade.py` | `artefacts/Math435/g6_corrected_cascade.json`, `sweep_checkpoint.json` | A1 | batch 1 (2026-06-05) |
| Math437 | Step-5 pattern-universal restoration (isotropic layer) v1.0, v1.1, v1.2 | `scripts/Math437_step5_class_closure.py` | `artefacts/Math437/step5_class_closure.json` (STALE-ARTEFACT: pre-repair verdict string; numerics valid — canonical fresh artefact in `claims/B2-PROPA-HLAYER/runs/260605-migration-revalidation/`) | B1, B2 | batch 1 (2026-06-05) |
| Math440 | §15.5 consolidated audit, second wave (PARTIAL) v1.0 | `scripts/Math440_audit_secondwave_recheck.py` | `artefacts/Math440/audit_recheck.json` | B2 | batch 1 (2026-06-05) |
| Math441 | F10 second-look of Math437 v1.1 repair (PARTIAL) v1.0 | — | — | B2 | batch 1 (2026-06-05) |
| Math442 | F10 closure: Math437 v1.2 CERTIFIED v1.0 | — | — | B1, B2 | batch 1 (2026-06-05) |
| Math427 | G1' diagonal-isotropy theorem + G1'' spec (v1.0 unversioned, v1.1) | `scripts/Math427_g1prime_diagonal_isotropy.py` | `artefacts/Math427/g1prime_diagonal_isotropy.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math428 | G1'' BCC Bloch log-det race PASS, continuum-anchored (v1.0, v1.1) | `scripts/Math428_g1doubleprime_bloch_logdet.py` | `artefacts/Math428/g1doubleprime_bloch_logdet.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math429 | G1''-1' inhomogeneous-Wick M-scan PASS (v1.0, v1.1) | `scripts/Math429_g1pp1prime_inhomogeneous_wick.py` | `artefacts/Math429/g1pp1prime_inhomwick.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math430 | G1''-2 dense-surface convergence PASS (v1.0) | `scripts/Math430_g1pp2_dense_surface_convergence.py` | `artefacts/Math430/g1pp2_surface_convergence.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math431 | G1''-3 LAM/HEX/FCC races PASS (v1.0) | `scripts/Math431_g1pp3_lam_hex_fcc.py` | `artefacts/Math431/g1pp3_lam_hex_fcc.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math432 | G3' two-shell ensemble race PASS (v1.0, v1.1) | `scripts/Math432_g3prime_multishell_ensemble.py` | `artefacts/Math432/g3prime_multishell_ensemble.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math434 | S15.5 independent audit of Reading-H T5 candidacy + AddA promotion record | `scripts/Math434_lam_exact_wick_bracket.py` | `artefacts/Math434/lam_exact_wick_bracket.json`, `artefacts/Math434/state.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math436 | G1''-3b HEX exact-Wick bracket PASS (v1.0, v1.1) | `scripts/Math436_hex_exact_wick_bracket.py` | `artefacts/Math436/hex_exact_wick_bracket.json` | B1 (+H-LAYER) | batch 2 (2026-06-05) |
| Math374 | (script-only migration: import dependency) | `scripts/Math374_canonical_BCC_hessian.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |
| Math400 | (script-only migration: import dependency) | `scripts/Math400_AddE_brazovskii_one_loop.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |
| Math424 | (script-only migration: import dependency) | `scripts/Math424_AddA_reading_uniqueness.py` | — | A1, B2 (indirect) | batch 1 (2026-06-05) |
| Math01 | v2 BCC-uniqueness-rigorous (uniqueness within cone) | — | — | B4 | batch 3 (2026-06-23) |
| Math56 | AddB ClassII guarded-quotient (constraint cone, canonical) + Addendum + HessJump-audit | — | — | B4 | batch 3 (2026-06-23) |
| Math82 | Addenda G (7-point bifurcation curve) / G2 (stall-mechanism audit) / G3 (vacuum-floor guard) | — | `artefacts/Math82/math82H_groundstate_N32_Lbcc7_MANIFEST.md` (continuation provenance; anchor m*²=+4.247e-2 at μ²=+5e-3) | B4 | batch 3 (2026-06-23) |
| Math194 | BCC-uniqueness-among-3D-crystallographic-competitors (single-shell SMA ranking) — **SUPERSEDED/REFUTED** by Math400 (script re-run yields BCC rank 9, lamellar rank 1) | `scripts/Math194_brazovskii_lattice_ranking.py` | — | B3 (refuted lineage) | batch 4 (2026-06-23) |
| Math383 | BCC-vs-Competitors-Analytical-and-Numerical (1-mode K_4/K_6 ranking) — **SUPERSEDED/REFUTED**: Math400 T0-refutes main claim + §2 K-table | — | — | B3 (refuted lineage) | batch 4 (2026-06-23) |

Script-only rows: the corresponding notes migrate when a claim consumes them
directly (migration-plan §1.1).

## Reproduction quickstart

```bash
cd archive/legacy/scripts
python Math426_g4_kernel_reconciliation.py     # claims: 10/10 PASS
python Math435_g6_corrected_variable_cascade.py # claims: 101/101 PASS
python Math437_step5_class_closure.py           # claims 91/91
python Math440_audit_secondwave_recheck.py      # claims 75/75
# batch 2 (run in the same directory): Math427/428/429/430/431/432/434/436
# scripts -> 5/5, 21/21, 19/19, 11/11, 15/15, 25/25, 22/22, 49/49 (167 total);
# Math434/436 are checkpoint-resumable (re-run on [CHECKPOINT] until VERDICT).
```

(Scripts write their JSON output to a `Runs/` directory relative to the
current working directory; compare against `artefacts/` and the canonical
fresh artefacts under `claims/<ID>/runs/260605-migration-revalidation/`.)
