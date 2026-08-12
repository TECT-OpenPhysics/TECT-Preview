# TECT catalog index

Compact generated reader surface. The complete current machine inventory is
`../verification/catalog/index.json`; source files and Git history remain authoritative.
`../CATALOG.md` is a frozen compatibility volume at commit `4db22f4e`
for historical verifiers and no longer grows.

**3831 artefacts** · **49 live claim cards** ·
130 superseded artefacts retained

## By kind

| Kind | Artefacts | Canonical bytes |
|---|---:|---:|
| Claim cards (registry layer) (`claim-card`) | 600 | 5,006,174 |
| Working proof notes (on claim cards) (`proof-note`) | 898 | 107,354,044 |
| Theory synthesis documents (Layer 2) (`synthesis`) | 345 | 7,749,956 |
| Migrated legacy notes (immutable) (`archive-note`) | 34 | 592,937 |
| Migrated legacy scripts (runnable) (`archive-script`) | 16 | 243,058 |
| Migrated legacy run artefacts (immutable) (`archive-artefact`) | 16 | 260,921 |
| Fresh run artefacts (TSv2 evidence) (`run-artefact`) | 929 | 25,451,394 |
| Domain codes (`code`) | 670 | 15,064,660 |
| Verification harness (`verification`) | 40 | 9,268,026 |
| Papers (publication layer) (`paper`) | 1 | 546 |
| Website (publication layer) (`website`) | 4 | 20,775 |
| Registries and ledgers (`registry`) | 42 | 1,340,445 |
| Governance policies (`policy`) | 19 | 150,669 |
| Root documents (`root-doc`) | 14 | 1,515,736 |
| Other tracked files (`other`) | 203 | 9,495,727 |

## Use

- Current compact metadata: `../verification/catalog-summary.json`
- Complete current machine inventory: `../verification/catalog/index.json`
- Frozen machine compatibility volume: `../verification/catalog.json`
- Live claim registry: `../CLAIMS.md`
- Proof and failure navigation: `../theory/proof-evidence-map.md`

New code should consume `catalog-summary.json` when it only needs counts or
top-level claim paths. Current inventory clients load only the required
kind shard from the manifest.
