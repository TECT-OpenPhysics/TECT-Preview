# B4-CONE-CURVATURE-ANCHOR — single-mode-cone uniqueness + positive local curvature anchor

**Tier**: T5 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(honest successor of the retired-name B4-MASS-GAP; created 2026-06-23 by operator verdict)*

## Statement

Within the single-mode ansatz class intersected with the Math56 constraint cone, the BCC critical point is
unique, and the curvature anchor $m^{*2}=+4.247\times10^{-2}$ at $\mu^2=+5\times10^{-3}$ reproduces to 4 digits
on the subset-4-cosine (metastable) branch. This is a positive **local curvature** statement on the cone —
**not** a mass gap ($m^{*2}$ is not identified with the symmetry-projected cone gap $\Delta_{\rm cone}$).

## Scope

CLOSED@SINGLE-MODE-CONE (local curvature anchor). Metastable branch ($\Delta F>0$); Regime-III undetermined
(legacy G2 audit). Explicitly **not** a continuum/thermodynamic mass gap — see **B4-MASS-GAP** (OPEN) for the
mass-gap target and the gap-scope addendum for $\Delta_{\rm cone}$.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses: none · Open gates: none

## Evidence

Grades: ANALYTIC, EXECUTED. Migrated chain (migration-clean; full SHA-256 in `archive/MIGRATION-LEDGER.md` batch 3):

- `archive/legacy/notes/Math01/...BCC-uniqueness-rigorous...` — uniqueness within cone
- `archive/legacy/notes/Math56/...` — constraint cone cluster
- `archive/legacy/notes/Math82/...Addendum-G/G2/G3...` + continuation manifest — curvature anchor
- Migration record: `claims/B4-MASS-GAP/notes/b4-massgap-migration-260623-260623-v1.0.tex.txt`; gap-scope addendum v1.1.

## Falsifier

A second distinct minimiser within the single-mode + cone class at the operating point, or failure to reproduce $m^{*2}$ within tolerance. (A **uniqueness/anchor** falsifier, NOT a gap falsifier — $\Delta_{\rm cone}\le0$ falsifies a mass gap, tracked under B4-MASS-GAP.)

## Reproduction

Status: **PACKAGE-PENDING**. Production-PDE (`continuation_mu2_v25.py` v2.6.4, $N=32$, $L_{\rm bcc}=7$, BCC seed); not sandbox-reproducible; operator-side bundle pending.

## No-overclaim

A mass gap (continuum/thermodynamic); identification $m^{*2}=\Delta_{\rm cone}$; ground-state status beyond the single-mode cone; favourability (the anchor is metastable, $\Delta F>0$).

## History

- 2026-06-23 — Created by operator verdict #2 as the honest successor carrying the local-curvature-anchor content of the old B4-MASS-GAP T5; the name "mass gap" was opened/retired.

## Next required action

Operator-side reproduction bundle for the $m^{*2}$ anchor (production-PDE under TSv2 recording).
