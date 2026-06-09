> SUPERSEDED by proposition-a-migration-revalidation-260605-260605-v1.1.tex.txt (format re-issue; content identical)

# B2-PROPA-HLAYER — M1 batch-1 migration & re-validation record

> **Version**: v1.0 (first issue) · **Issued**: 2026-06-05 · **Status**: verification record (no tier action)
>
> **Revision history**
> - v1.0 (2026-06-05) — first issue. Records the M1 batch-1 migration of the
>   Sector-B evidence chain, its independent re-execution, one stale-artefact
>   finding, and the hypothesis transcription. No mathematical content is new.

## 1. Purpose and scope

This note is the permanent record of M1 migration batch 1
(`governance/migration-plan.md` §4 priority 1): the evidence chain of claims
`A1-KERNEL-CONV`, `B1-RH-ENUM` (partial), and `B2-PROPA-HLAYER` was copied
verbatim from the frozen legacy repository into `archive/legacy/` and
re-validated by full re-execution. This note makes no new mathematical claim
and performs no tier action; it is citable as the re-validation evidence for
the cards above.

## 2. What was migrated

23 files (11 notes, 7 scripts, 5 run JSONs) covering theory tags Math426
(+AddA/AddB), Math435 (v1.0–v1.1), Math437 (v1.0–v1.2), Math440, Math441,
Math442, plus the three import-dependency modules Math374 / Math400-AddE /
Math424-AddA (script-only). Layout: `archive/legacy/{notes/<Tag>/, scripts/,
artefacts/<Tag>/}`; per-file original paths in `archive/MIGRATION-LEDGER.md`;
per-tag lookup in `archive/legacy/INDEX.md`.

## 3. Re-validation results (fresh environment: python 3.12, numpy 2.2.6)

| Script | Self-test asserts | Runtime | Artefact comparison vs archived JSON |
|---|---|---|---|
| `Math426_g4_kernel_reconciliation.py` | 10/10 PASS | 0.4 s | identical within rel_tol $10^{-9}$ |
| `Math435_g6_corrected_variable_cascade.py` | 101/101 PASS | 3.5 s | identical within rel_tol $10^{-9}$ |
| `Math437_step5_class_closure.py` | 91/91 PASS | 1.2 s | numerics identical; 2 verdict-string diffs (see §4) |
| `Math440_audit_secondwave_recheck.py` | 75/75 PASS | 37.8 s | identical within rel_tol $10^{-9}$ |

Total: **277/277 asserts PASS**. Fresh artefacts:
`runs/A1-KERNEL-CONV/260605-migration-revalidation/`, `runs/B2-PROPA-HLAYER/260605-migration-revalidation/`.
Post-reorganisation, `Math426_g4_kernel_reconciliation.py` was re-executed from
the new `archive/legacy/scripts/` location (10/10 PASS) to confirm the flat
script directory remains runnable.

## 4. Finding F-1 (STALE-ARTEFACT, no numeric impact)

The archived legacy artefact `artefacts/Math437/step5_class_closure.json`
predates the R1 repair of the Math440/Math441 audit cycle: its `claims[90]`
verdict string is the v1.0-era wording ("Region-I positivity + Lemma-B dip
bound + $\Delta_0$ penalty"), while the migrated script (repaired, v1.1
four-interval proof) emits "I-prime all-positivity + band/Region-II anchor-only
$P_B$ floors; $\Delta_0$ demoted to comfort margin". All numeric fields are
identical within $10^{-9}$. Consequence: the fresh artefact under
`runs/B2-PROPA-HLAYER/260605-migration-revalidation/` is canonical for TSv2 citation; the
archived JSON remains as historical record. Process lesson: M1 batches MUST
re-run scripts rather than trust stored artefacts (already binding via
`governance/migration-plan.md` §3 M1).

## 5. Hypothesis transcription

H-LAYER and H-A0 were transcribed verbatim from Math437 v1.2 §Hypotheses into
`claims/GATES.md`. The transcription makes explicit that the H-LAYER
beyond-layer residual **is** gate STEP-5B — the designated gateway for any
whole-Reading-H T6 discussion.

## 6. Devil's-advocate (3 objections)

- **(α) "Re-execution in the same ecosystem is not independent verification."**
  VALID with mitigation: the asserts are the original authors' self-tests, so
  this re-run certifies reproducibility, not correctness. Independent
  correctness evidence for the chain is the dual-audit record (Math440 +
  Math441, different agents) migrated alongside. External reproduction becomes
  possible exactly because of this migration (public scripts + pinned layout);
  CI re-execution on the GitHub runner will add an environment-independent
  check.
- **(β) "One stale artefact suggests others."** VALID: treated as a class, not
  an instance — the re-run-don't-trust rule is binding for every future batch,
  and any artefact cited without a fresh re-run is non-citable
  (`governance/verification-standard.md` §4).
- **(γ) "Archive copies could drift from the frozen legacy originals."**
  DISMISSED: the legacy repository is frozen read-only (M0); copies are
  byte-identical at migration time, recorded in the ledger, and git-tracked
  from this commit forward — any later divergence is visible in history.

Quantitative sanity check (mandatory): the four assert totals (10+101+91+75 =
277) and the $10^{-9}$ comparison tolerance were checked against the comparison
script output; runtimes are O(1–40 s), consistent with the scripts' loop sizes.

## 7. Result footer

```
Result ID:               B2-PROPA-HLAYER (supporting record; also A1-KERNEL-CONV, B1-RH-ENUM partial)
Precise statement:       M1 batch-1 evidence chain migrated verbatim and re-validated by full re-execution (277/277 asserts).
Scope:                   Reproducibility of the migrated chain only; no new mathematical claim; no tier action.
Dependencies:            archive/legacy/ batch-1 file set (see MIGRATION-LEDGER rows of 2026-06-05).
Evidence grade:          EXECUTED
Reproduction command:    cd archive/legacy/scripts && python Math426_g4_kernel_reconciliation.py && python Math435_g6_corrected_variable_cascade.py && python Math437_step5_class_closure.py && python Math440_audit_secondwave_recheck.py
Expected output:         10/10, 101/101, 91/91, 75/75 asserts PASS; exit 0 each; JSONs match archived artefacts within rel_tol 1e-9 (Math437: numerics only, see §4)
Falsification gate:      Any assert failure or artefact mismatch beyond tolerance on re-execution.
Tier before / after:     A1 T5 / T5 · B1 T5 / T5 · B2 T6 / T6 (no change)
No-overclaim statement:  Re-execution certifies reproducibility, not correctness; Reading-H remains T5; STEP-5B remains open.
Next required action:    M1 batch 2 (Math431-HEX chain + Math427/428-432/434/436) to make B1 migration-clean.
```
