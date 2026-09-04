# Q3LOCK EXP-000782 clean reproduction audit

**Status:** T0 reproducibility audit; no theorem-tier change  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until final content freeze and independent proof audit

## 1. Purpose and boundary

This note records a clean rerun of the three verification lanes attached to
the EXP-000782 positive-lambda Q3LOCK package.  It separates an executable
environment defect from the mathematical proof status.  The stored scripts
are algebraic and provenance regression tests; their PASS results are not a
substitute for the still-open independent P-06/P-09 proof audits.

## 2. Environment repair

The repository working venv initially contained NumPy but not the direct
`mpmath` and `sympy` imports required by the primary verifier.  The independent
verifier is standard-library-only and was already runnable.  Installing the
versions declared by `requirements.txt` restored the intended environment:

```text
numpy 2.3.5
sympy 1.14.0
mpmath 1.3.0
```

No repository source file was changed by the installation.  The package
installation is an environment prerequisite for the primary numerical
regression lane; a fresh release checklist must still install
`requirements.txt` before invoking it.

## 3. Commands and results

From the repository root, using the repository's requirements-complete virtual
environment Python executable:

```text
python codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split.py
EXP-000782 PRIMARY PASS 195/195

python codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py
EXP-000782 INDEPENDENT PASS 306/306

python codes/foundations/pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_verify.py
EXP-000782 INTEGRATED PASS 120/120
```

Each command was run twice.  The resulting canonical JSON artifacts were
byte-identical within each lane:

| lane | assertions | SHA-256 of both reruns |
|---|---:|---|
| primary | 195/195 | `A42C5F5684002B2B71908A739C91867411C9D269CA3F4B0343C49D986CFC9882` |
| independent | 306/306 | `566942655D7FFCE9F3E83B415CDB2D3339EC32A7B3B49B2828390E17993E0AF9` |
| integrated | 120/120 | `2AAAFE56BD215735BAE89B54D87852DD804D7014C6F6FC66FF275903BA6D661E` |

The artifacts are the existing claim-run paths under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-{primary,independent,integrated}-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/result.json`.

## 4. What this establishes

The current primary, independent and integrated readers can be executed in a
requirements-complete environment and produce deterministic PASS artifacts.
The three lanes agree on the registered EXP-000782 identity, parameter
threshold algebra, Q3 graph/sign checks, source/factor bookkeeping, scope
firewalls and the unchanged claim-nonbearing status.  This removes the earlier
environment and random-output obstacles from the reproducibility package.

It does **not** independently verify the continuous-loop FKG limit, the
Hilbert-valued FSS-to-loop transfer, the cited DLR form-domain hypotheses, or
the strict-cusp/phase theorem itself.  Those are proof-text and external-audit
obligations, not executable assertions in these lanes.

## 5. Adversarial checks

1. **A stored PASS is enough without a fresh run.**  False: all three lanes
   were rerun from the current worktree, and the artifact bytes were compared.
2. **The independent lane proves the analytic theorem.**  False: it is a
   standard-library convention and scope audit, not a proof of FKG, RP, DLR,
   or the thermodynamic limit.
3. **The primary lane's dependency failure falsifies the result.**  False:
   it was an environment defect; installing the declared numerical
   dependencies restored 195/195, with the defect recorded separately.
4. **Deterministic JSON proves publication readiness.**  False: P-06/P-09
   proof text, source-hypothesis checks, external review, claim registration
   and final content freeze remain required.
5. **Running the commit watcher is harmless at this stage.**  False for the
   current workflow: the watcher invokes the note-PDF builder, so it remains
   intentionally unrun while PDF creation is deferred by user instruction.

## 6. Remaining actions and nonclaims

The next reproducibility gate is a clean-snapshot rerun after the P-06/P-09
proof text and independent source audits are fixed.  Before claim promotion,
the release package must also pin the dependency installation command and
recompute the three hashes without temporary-path or environment-specific
fields.

This audit does not close P-04, P-06, P-09 or P-12 and does not assert a strict
source cusp, positive zero-mode lower bound, DLR multiplicity, extremality,
purity, clustering, real-time dynamics, KMS state, ground state, mass gap,
continuum limit, physical vacuum, cosmological interpretation, Sector-A or
Pre-A closure.  No new claim card, manuscript release or PDF is created.
