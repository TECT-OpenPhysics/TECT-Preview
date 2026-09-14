# TECT catalog index

Compact generated reader surface. The complete current machine inventory is
`../verification/catalog/index.json`; source files and Git history remain authoritative.
`../CATALOG.md` is a frozen compatibility volume at commit `4db22f4e`
for historical verifiers and no longer grows.

**10693 artefacts** · **49 live claim cards** ·
130 superseded artefacts retained

## By kind

| Kind | Artefacts | Canonical bytes |
|---|---:|---:|
| Claim cards (registry layer) (`claim-card`) | 604 | 5,206,927 |
| Working proof notes (on claim cards) (`proof-note`) | 1014 | 109,064,983 |
| Theory synthesis documents (Layer 2) (`synthesis`) | 345 | 7,747,022 |
| Migrated legacy notes (immutable) (`archive-note`) | 72 | 1,509,315 |
| Migrated legacy scripts (runnable) (`archive-script`) | 22 | 319,000 |
| Migrated legacy run artefacts (immutable) (`archive-artefact`) | 21 | 302,036 |
| Reviewed legacy research records (`legacy-research-record`) | 140 | 164,393 |
| Generated legacy sector, claim, and gate views (`legacy-research-view`) | 16 | 205,000 |
| Fresh run artefacts (TSv2 evidence) (`run-artefact`) | 3310 | 333,301,458 |
| Domain codes (`code`) | 1914 | 29,287,735 |
| Verification harness (`verification`) | 1068 | 25,391,615 |
| Papers (publication layer) (`paper`) | 60 | 1,063,710 |
| Website (publication layer) (`website`) | 4 | 20,775 |
| Registries and ledgers (`registry`) | 42 | 1,617,628 |
| Governance policies (`policy`) | 25 | 236,819 |
| Root documents (`root-doc`) | 14 | 2,420,200 |
| Other tracked files (`other`) | 2022 | 42,658,472 |

## Use

- Current compact metadata: `../verification/catalog-summary.json`
- Complete current machine inventory: `../verification/catalog/index.json`
- Frozen machine compatibility volume: `../verification/catalog.json`
- Live claim registry: `../CLAIMS.md`
- Proof and failure navigation: `../theory/proof-evidence-map.md`

New code should consume `catalog-summary.json` when it only needs counts or
top-level claim paths. Current inventory clients load only the required
kind shard from the manifest.
