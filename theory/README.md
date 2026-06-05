# theory/ — integrated theory synthesis (Layer 2)

This folder is NOT the working-note area. It is the **synthesis layer**: the
consolidated, readable exposition of TECT, rebuilt from the claim ledger.

## The three-layer architecture

| Layer | Folders | Content | Rule |
|---|---|---|---|
| **L1 — Proof system** | `claims/` (cards + per-claim `notes/`), `archive/`, `codes/`, `runs/`, `verification/`, `negative-results/`, `predictions/` | granular evidence: claim cards, working proof notes, migrated legacy originals, scripts, run artefacts | append-mostly; every statement gate-checked by the linter |
| **L2 — Theory synthesis** | `theory/sector-X/` | per-sector consolidated documents that weave registered claims into a coherent theory exposition | may cite **only claim IDs at their registered tiers**; no statement stronger than the ledger; regenerable in principle from L1 |
| **L3 — Publication** | `publish/website/`, `publish/papers/` | curated outward artefacts | derived from L2/L1 under `governance/publication-tiers.md` (P2 rules) |

Working proof notes (the successor of legacy Math notes) live with their
claim as LaTeX fragments:
`claims/<ID>/notes/<descriptive-slug>-<YYMMDD>-v<major>.<minor>.tex.txt` —
versioned re-issue, all versions kept, PDF via
`verification/scripts/build_note_pdf.py` (`governance/naming-and-versioning.md`
§3). Division of labour: the claim card (.md) is the web-readable surface;
the note (.tex.txt) is the formal mathematical document; synthesis documents
here stay .md until they transition to `publish/papers/`.

## Synthesis documents

One per sector, created once the sector has enough registered claims:
`theory/sector-<X>-<name>/<descriptive-slug>-synthesis-<YYMMDD-first>-v1.0.md`
(revisions append their own issue date: `...-<YYMMDD-first>-<YYMMDD-current>-v1.1.md`
— two-date rule, `governance/naming-and-versioning.md` §3), same versioned
re-issue scheme, every claim citation as `[claim-ID @ tier]`. A synthesis
document never introduces a result — if something is worth stating, it is
worth a claim card first (file-write-before-claim).
