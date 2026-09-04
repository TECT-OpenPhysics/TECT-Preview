# Q3LOCK verification-lane result hash integrity audit

**Status:** T0 provenance correction; no claim-card promotion; PDF deferred  
**Scope:** `strategy/q3lock-exp782-independent-result-manifest-260905.json`,
the three registered EXP-000782 result JSONs, and the clean-replay record  
**Authority:** EXP-000782 and EXP-001515; source-hash context EXP-001538

## 1. Audit question

The R-497 manifest pins the canonical result artifacts for the primary,
independent, and integrated verification lanes. Does each stored lane digest
equal the SHA-256 digest of the current result JSON bytes, including the
independent artifact reproduced by the clean replay?

## 2. Recomputed bytes and finding

The audit used the current repository files and the repository virtual
environment. The digest was computed over `Path(path).read_bytes()` with no
newline conversion. The primary and integrated pins agree with their files.
The independent pin is a metadata transcription error:

| lane | manifest pin | current/fresh result bytes | outcome |
|---|---|---|---|
| primary | `a42c5f5684002b2b71908a739c91867411c9d269ca3f4b0343c49d986cfc9882` | `a42c5f5684002b2b71908a739c91867411c9d269ca3f4b0343c49d986cfc9882` | match |
| independent | `566942655d7ffce9f83e3b415cdb2d3339ec32a7b3b49b2828390e17993e0af9` | `566942655d7ffce9f3e83b415cdb2d3339ec32a7b3b49b2828390e17993e0af9` | mismatch |
| integrated | `2aaafe56bd215735bae89b54d87852dd804d7014c6f6fc66ff275903ba6d661e` | `2aaafe56bd215735bae89b54d87852dd804d7014c6f6fc66ff275903ba6d661e` | match |

Both independent clean-replay runs produced the right-hand digest and were
byte-identical to the stored result JSON. The two 64-character strings differ
only at zero-based positions 17--19: the manifest has `83e`, whereas the
result bytes have `3e8`. The independent result file, verifier source, and
mathematical proof text are not changed by this correction.

## 3. Exact correction and reproduction

The manifest's independent `verification_lanes[*].sha256` value is corrected
to

```text
566942655d7ffce9f3e83b415cdb2d3339ec32a7b3b49b2828390e17993e0af9
```

From the repository root, the byte-level check is:

```text
python -X utf8 -c "import hashlib,json; from pathlib import Path; m=json.loads(Path('strategy/q3lock-exp782-independent-result-manifest-260905.json').read_text(encoding='utf-8')); assert all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in m['verification_lanes'])"
```

This assertion checks artifact identity only. It does not certify any FKG,
reflection-positivity, DLR, infrared, cusp, or phase statement.

## 4. Adversarial checks

| objection | disposition | reason |
|---|---|---|
| Rewrite the independent result until it matches the old pin | **UPHELD AS FALSE** | The stored and freshly reproduced result bytes agree; only the manifest transcription is repaired. |
| Treat the corrected digest as new mathematical evidence | **UPHELD AS FALSE** | A digest establishes provenance, not theorem validity or a stronger evidence tier. |
| The mismatch could be an environment-specific newline effect | **DISMISSED** | The raw bytes of the stored result and both clean-replay outputs are identical; primary/integrated pins use the same raw-byte convention. |
| Correcting the pin changes EXP-000780--782 or the Q3LOCK model | **DISMISSED** | No authority record, verifier source, parameter, proof-text line, claim card, or nonclaim is modified. |

## 5. Disposition and boundary

This repairs one R-497 verification-lane hash pin. The manifest remains
`T0 / INTERNAL_REVIEW_ONLY`, `claim_bearing=false`, `publication_status=RESEARCH_ONLY`,
and `pdf_status=DEFERRED`. Independent P-06/P-09 proof audits, source and
operator-domain checks, external review, claim/result lineage review, content
freeze, and release checks remain open. No manuscript, submission package, or
PDF is created.
