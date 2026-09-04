# Q3LOCK manifest source-hash integrity audit

**Status:** T0 provenance correction; no claim-card promotion; PDF deferred  
**Scope:** `strategy/q3lock-exp782-independent-result-manifest-260905.json`  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  

## 1. Audit question

The R-497 manifest is intended to make every proof-text and verifier input
byte-reproducible. A direct SHA-256 recomputation over each listed source file
found one malformed stored pin: the entry for
`strategy/q3lock-fkg-continuous-association-discretization-audit-260905.md`
contained 63 hexadecimal characters. The file itself was not changed.

## 2. Exact correction

The corrected source hash is

```text
e9557361e9b24da10acfe49d5fc57e05798029fde07641a8930bb05910265bb9
```

The previous manifest value was the same prefix without its final `9`. The
manifest now stores the complete 64-character SHA-256 value. All other listed
source bytes remain unchanged; no authority record, theorem statement,
parameter, verifier result, or nonclaim boundary is altered.

## 3. Reproduction procedure

From the repository root, recompute every `source_files[*].sha256` with

```text
python -X utf8 -c "import hashlib,json; from pathlib import Path; m=json.loads(Path('strategy/q3lock-exp782-independent-result-manifest-260905.json').read_text(encoding='utf-8')); assert all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in m['source_files'])"
```

The assertion is a byte-level provenance check only. It does not certify the
mathematical contents of any source file.

## 4. Adversarial checks

| objection | disposition | reason |
|---|---|---|
| Recompute or normalize the audited note to make its hash fit | **UPHELD AS FALSE** | The note bytes are preserved; only the manifest pin is corrected. |
| A complete hash pin promotes the T0 proof to a theorem | **UPHELD AS FALSE** | Hash agreement proves identity/reproducibility, not mathematical validity. |
| The correction changes the EXP-000780--782 authority chain | **DISMISSED** | The authority records and proof scope are untouched. |
| A hexadecimal prefix is an acceptable SHA-256 pin | **UPHELD AS FALSE** | The release manifest requires the complete 256-bit digest. |

## 5. Disposition and boundary

This repairs a manifest integrity defect and leaves R-497 at
`T0 / INTERNAL_REVIEW_ONLY`. Independent mathematical review, content freeze,
clean replay, external referee review, and all phase/cusp gates remain open.
No claim card, publication manuscript, submission package, or PDF is created.
