# Q3LOCK source-tangent hash recomputation audit

**Status:** T0 provenance-integrity correction; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze, independent review, clean replay, and final release review

## 1. Purpose and boundary

After EXP-001561 corrected the source-tangent audit pin, a follow-up direct
manifest check found that the newly copied digest for the hash-correction note
was itself one character short.  This note records the second correction and
requires the final digest to be generated directly from the file bytes rather
than manually transcribed.

No source theorem, proof text, claim tier, publication status, manuscript, or
PDF is changed by this provenance repair.

## 2. Direct byte-derived value

The exact SHA-256 of
`strategy/q3lock-source-tangent-hash-correction-audit-260905.md`, computed
from its current UTF-8/LF bytes, is

```text
12239d6e65d8b6e8d78111179973f2407008d08e31665fafad2374f207f21ece
```

The manifest and RESULTS-LEDGER must contain this complete 64-character value.
No source file is rewritten as part of the correction.

## 3. Adversarial checks

1. **Did the source-tangent or pressure-derivative proof text change?**
   **NO**: only provenance projections and this audit note are involved.
2. **Can a manually copied digest be trusted after the first correction?**
   **NO**: the final value is generated and compared programmatically from the
   source bytes.
3. **Does a valid digest prove the source-tangent theorem?**  **NO**: all
   derivative, UI, DLR specification and external-review hypotheses remain
   separate.
4. **Does this correction change EXP-001560 or EXP-001561's scope?**  **NO**:
   both remain T0, claim-nonbearing and PDF-deferred.
5. **Does manifest integrity allow early PDF generation?**  **NO**: content
   freeze, clean replay and independent mathematical review are still required.

## 4. Disposition

The final source-tangent hash must be computed from bytes and synchronized in
the R-497 manifest and RESULTS-LEDGER.  This is a T0 provenance correction;
all mathematical and publication gates remain open.
