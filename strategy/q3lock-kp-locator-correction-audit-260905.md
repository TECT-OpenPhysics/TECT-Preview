# Q3LOCK KP theorem-locator correction audit

**Status:** T0 source-citation correction; no claim-card promotion
**Date:** 2026-09-05
**Owner task:** T-054
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782
**Primary source:** KP arXiv:math-ph/0609045v1
**Pinned source SHA-256:** `607c534774f04481b0af8ddbb891e4caac2c0ca0fd28116c081fabe7c78bc532`
**Audited document:** `strategy/q3lock-low-temperature-dlr-paper-preregistration-audit-260904.md`
**Audited document SHA-256 before correction:** `4d704682b8a6ae0d4ffd51044f5508d5c79958abe173852eab79e0787f5d62f6`
**PDF:** deferred until mathematical content, independent review and claim/result scope are frozen

## 1. Purpose and strict boundary

The Q3LOCK preregistration must identify the exact KP version and theorem
locators used for the general Euclidean-DLR input.  A locator check against the
hash-pinned KP v1 PDF found two off-by-number citations in the fixed-source
DLR-closure row.  This note records the correction and the source evidence.
It changes no Hamiltonian, inequality, parameter condition, theorem scope or
claim tier.

This is a citation/provenance audit, not an independent proof of DLR
compactness or source-tangent composition.  It creates no claim card,
manuscript, release or PDF.

## 2. Exact source locations

The KP v1 PDF states:

| Intended use | Correct KP v1 locator | What it supplies |
|---|---|---|
| continuity of the local specification in the boundary | Lemma 2.8, equation (2.59) | the Feller property on each `Omega_alpha` |
| DLR closure of an accumulation point | Lemma 2.11, equation (2.67) | a `W_alpha` accumulation point lying in `P(Omega^t)` solves the DLR equation |
| general existence and compactness | Theorem 3.1 | non-emptiness and `W^t` compactness of `G^t` |
| uniform one-site exponential moment | Theorem 3.2 | the Holder/L2 exponential estimate |
| tempered support | Theorem 3.3 | the Lebowitz--Presutti-type support set |

The source pages are 14--16 of the 60-page arXiv PDF: Lemma 2.8 appears on
printed page 14, Lemma 2.11 on printed page 16, and Theorems 3.1--3.3 on
printed page 17.  The pinned PDF, not a search-result label, is the citation
authority.

## 3. Correction applied to the preregistration

The row in the preregistration formerly read:

```text
Lemma 2.10 gives the Feller property ...; Lemma 2.13 sends any W_alpha
accumulation point ... to G^t.
```

It is corrected to:

```text
Lemma 2.8 gives the Feller property on every Omega_alpha; Lemma 2.11 sends
any W_alpha accumulation point that remains in P(Omega^t) to G^t; Theorems
3.1--3.2 give nonemptiness, W^t compactness and uniform one-site exponential
moments.
```

The correction is purely bibliographic.  It does not turn the fixed-source
KP input into a proof of the Q3LOCK source-to-zero tangent limit.  That limit
still uses the separate compact-source specification-continuity and uniform
integrability argument, and it remains open to independent review.

## 4. Scope and adversarial checks

1. **The locator mismatch changes the imported theorem.** **DISMISSED:** the
   cited statements are the same KP local specification and DLR facts; only
   the section number was wrong.
2. **The correction permits importing KP's scalar FKG or infrared results.**
   **UPHELD AS FALSE:** only the general-vector Theorems 3.1--3.3 and the
   explicitly identified local lemmas are imported; scalar order propositions
   remain firewalled.
3. **A correct locator closes the Q3LOCK source-tangent proof.** **UPHELD AS
   FALSE:** source-window uniformity, specification convergence, unbounded
   observable truncation and independent review remain required.
4. **The historical KP PDF should be rewritten to match the citation.**
   **DISMISSED:** the source bytes and hash are retained; only the local
   preregistration crosswalk is corrected.

## 5. Disposition and next gate

**Advanced at T0:** the KP v1 citation map now has exact locators for the
Feller, DLR-closure, existence, moment and support inputs.  The Q3LOCK
preregistration is corrected without changing its scientific content.

**Still open:** independent verification that the Q3LOCK potential satisfies
all KP hypotheses uniformly on the source window; the source-to-zero tangent
composition; the P-06/P-09 analytic bridges; claim-card decision; content
freeze; clean replay; external mathematical review; and final release checks.

## 6. Explicit nonclaims and PDF boundary

This audit does not assert a strict cusp, phase coexistence, DLR multiplicity,
extremality, purity, clustering, common real-time dynamics, KMS state,
ground-state phase, spectral gap, continuum limit, physical vacuum,
cosmological interpretation, C6, CP1, Sector A or Pre-A closure.

No claim card, P2 manuscript, submission, upload, tag, release or PDF is
created.  PDF compilation and visual review remain final-stage actions after
all mathematical and external-review gates close.
