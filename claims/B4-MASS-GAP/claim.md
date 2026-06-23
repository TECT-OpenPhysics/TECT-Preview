# B4-MASS-GAP — BCC ground-state uniqueness within the single-mode constraint cone

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · **Migration**: clean (batch 3, 2026-06-23)

## Statement

The BCC ground state is unique within the single-mode ansatz class intersected with the Math56 constraint cone; the numerical anchor $m^{*2}=+4.247\times 10^{-2}$ at $\mu^2=+5\times 10^{-3}$ reproduces to 4 digits on the subset-4-cosine branch (metastable-branch anchor, not ground state).

## Scope

CLOSED@SINGLE-MODE-CONE. The legacy 'PROVED' label is exactly this pinned scope. Three-regime continuation structure (pitchfork at mu^2 approx -0.05 +/- 0.03; branch termination mu^2 <= -0.5) is recorded evidence; Regime-III interpretation remains undetermined per the legacy G2 audit.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): none
- Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED. Evidence migrated verbatim (batch 3, 2026-06-23,
`archive/MIGRATION-LEDGER.md`); migration record + re-validation grade:
`claims/B4-MASS-GAP/notes/b4-massgap-migration-260623-260623-v1.0.tex.txt`.

- `archive/legacy/notes/Math01/TECT-Math01-v2-BCC-uniqueness-rigorous.tex.txt` — uniqueness within cone
- `archive/legacy/notes/Math56/TECT-Math56-AddB-ClassII-guarded-quotient-analytical.tex.txt` — constraint cone (canonical)
- `archive/legacy/notes/Math56/TECT-Math56-Addendum.tex.txt` — cone-cluster base
- `archive/legacy/notes/Math56/TECT-Math56-HessJump-audit.tex.txt` — cone Hessian-jump audit
- `archive/legacy/notes/Math82/TECT-Math82-Addendum-G-Phase-Z-7point-bifurcation-curve.tex.txt` — continuation curve
- `archive/legacy/notes/Math82/TECT-Math82-Addendum-G2-PCG-and-stall-mechanism-audit.tex.txt` — stall-mechanism audit
- `archive/legacy/notes/Math82/TECT-Math82-Addendum-G3-vacuum-floor-guard-implementation.tex.txt` — vacuum-floor guard
- `archive/legacy/artefacts/Math82/math82H_groundstate_N32_Lbcc7_MANIFEST.md` — continuation-run provenance (point #1: $m^{*2}=+4.247\times10^{-2}$ at $\mu^2=+5\times10^{-3}$, metastable)

Legacy pillar(s): 1 · Legacy tier label: PROVED - single-mode/Math56 cone caveat (legacy)

## Falsifier

A second distinct minimiser within the single-mode + cone class at the operating point, or failure to reproduce the anchor within stated tolerance.

## Reproduction

Status: **PACKAGE-PENDING** (unchanged by migration). The anchor is a production
Newton--Krylov continuation fixed point (`continuation_mu2_v25.py` v2.6.4,
$N=32$, $L_{\rm bcc}=7$, BCC analytic seed); not sandbox-reproducible.
Numerical re-execution is deferred to an operator-side reproduction bundle.
Migration certifies the verbatim text (7/7 SHA-256) and manifest provenance,
not re-executability — see the migration record note §3.

## No-overclaim

Ground-state uniqueness beyond the single-mode cone; ground-state status of the subset-4-cosine anchor.

## Devil's-advocate record

Seeding registration only (no tier change performed here). The full
devil's-advocate record (>= 3 concrete objections with verdicts) begins with
the first TSv2 tier action on this claim. (The migration record note carries
its own three-objection self-test for the migration act, not a tier action.)

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (last
  theory tag Math442), translated per `governance/tier-system.md` §4.
- 2026-06-23 — Migration batch 3 (M1, `governance/migration-plan.md` §4
  priority 1): evidence chain migrated verbatim (Math01-v2, Math56 cone
  cluster, Math82-AddG/G2/G3 + continuation manifest); `legacy:` pointers
  resolved to `archive/...`; card is migration-clean. No tier action;
  reproduction stays PACKAGE-PENDING.

## Next required action

Operator-side reproduction bundle for the $m^{*2}$ anchor (production-PDE
re-execution under TSv2 run recording); ground-state continuation with the
full 12-mode bcc_analytic seed (legacy Math82-H queue) remains the path to any
beyond-cone uniqueness statement.
