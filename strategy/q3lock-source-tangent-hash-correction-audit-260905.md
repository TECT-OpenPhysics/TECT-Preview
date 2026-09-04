# Q3LOCK source-tangent hash correction audit

**Status:** T0 provenance-integrity correction; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze, independent review, clean replay, and final release review

## 1. Purpose and boundary

The R-497 manifest pin for
`strategy/q3lock-source-tangent-dlr-composition-audit-260905.md` was copied
with 63 hexadecimal characters after the EXP-001560 text correction.  This
note recomputes the digest from the current source bytes and synchronizes the
manifest and RESULTS-LEDGER pin.  It is a provenance repair only: no source
content, theorem, scope, claim tier, or publication status changes.

No claim card, manuscript, submission package, or PDF is created.

## 2. Direct recomputation

The current source file has the exact 64-character SHA-256 digest

```text
7fad177cda60fa3532bb8fc1c56ff2e7ca2f3fdd83ccbfb860bab6d403adb80b
```

The prior manifest value omitted one `b` in the `...d83ccbfb...` segment and
was therefore rejected as a valid source pin.  The source file itself is not
rewritten.  The manifest and its human-readable ledger projection are updated
atomically to the directly recomputed value.

## 3. Adversarial checks

1. **Did the hash correction alter the source-tangent proof text?**  **NO**:
   only the manifest and ledger digest fields are changed.
2. **Can a 63-character digest be accepted as a SHA-256 pin?**  **NO**:
   the manifest integrity check compares the complete 64-character digest.
3. **Does the correction change EXP-001560 or its scientific scope?**  **NO**:
   the pressure-derivative lemma and all nonclaims remain byte-for-byte the
   same.
4. **Does a passing hash check certify the pressure-to-DLR theorem?**  **NO**:
   provenance integrity is separate from the finite derivative, UI, DLR and
   external mathematical gates.
5. **Does this correction authorize PDF generation?**  **NO**: PDF work stays
   deferred until content freeze and independent review.

## 4. Disposition

The source-tangent digest is now directly recomputed and synchronized in the
R-497 manifest and RESULTS-LEDGER.  This is a T0 integrity correction only;
all 18 mathematical and publication gates remain open.
