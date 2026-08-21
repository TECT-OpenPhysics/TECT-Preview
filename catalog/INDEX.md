# TECT catalog index

Compact generated reader surface. The complete current machine inventory is
`../verification/catalog/index.json`; source files and Git history remain authoritative.
`../CATALOG.md` is a frozen compatibility volume at commit `4db22f4e`
for historical verifiers and no longer grows.

**4331 artefacts** · **49 live claim cards** ·
130 superseded artefacts retained

## By kind

| Kind | Artefacts | Canonical bytes |
|---|---:|---:|
| Claim cards (registry layer) (`claim-card`) | 604 | 5,068,432 |
| Working proof notes (on claim cards) (`proof-note`) | 909 | 107,638,085 |
| Theory synthesis documents (Layer 2) (`synthesis`) | 345 | 7,749,956 |
| Migrated legacy notes (immutable) (`archive-note`) | 72 | 1,509,315 |
| Migrated legacy scripts (runnable) (`archive-script`) | 22 | 319,000 |
| Migrated legacy run artefacts (immutable) (`archive-artefact`) | 21 | 302,036 |
| Reviewed legacy research records (`legacy-research-record`) | 140 | 164,393 |
| Generated legacy sector, claim, and gate views (`legacy-research-view`) | 16 | 205,000 |
| Fresh run artefacts (TSv2 evidence) (`run-artefact`) | 1025 | 29,261,894 |
| Domain codes (`code`) | 753 | 16,751,515 |
| Verification harness (`verification`) | 69 | 10,780,909 |
| Papers (publication layer) (`paper`) | 1 | 546 |
| Website (publication layer) (`website`) | 4 | 20,775 |
| Registries and ledgers (`registry`) | 42 | 1,537,569 |
| Governance policies (`policy`) | 21 | 195,650 |
| Root documents (`root-doc`) | 14 | 1,669,502 |
| Other tracked files (`other`) | 273 | 11,358,288 |

## Use

- Current compact metadata: `../verification/catalog-summary.json`
- Complete current machine inventory: `../verification/catalog/index.json`
- Frozen machine compatibility volume: `../verification/catalog.json`
- Live claim registry: `../CLAIMS.md`
- Proof and failure navigation: `../theory/proof-evidence-map.md`

New code should consume `catalog-summary.json` when it only needs counts or
top-level claim paths. Current inventory clients load only the required
kind shard from the manifest.
