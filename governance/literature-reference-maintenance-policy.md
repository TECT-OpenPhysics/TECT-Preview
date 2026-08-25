# Literature reference maintenance policy

**Status:** active repository policy
**Owner:** TECT proof and publication lanes
**Effective:** 2026-08-25

## Purpose

Ensure that every load-bearing external theorem, paper, standard result, or
legacy source is distinguishable from TECT-specific work and remains
reproducible when a proof note or publication PDF is assembled.

## Required source record

For every external source used beyond background context, record all of:

- stable `source_id` and complete citation;
- DOI, arXiv identifier, publisher URL, or repository locator;
- theorem, proposition, equation, page or section locator;
- version/date and access or archive hash when available;
- the exact conclusion imported;
- an assumption-to-model crosswalk marking every hypothesis
  `SATISFIED`, `CONDITIONAL`, `FAILED`, or `UNASSESSED`;
- disposition: `APPLIES`, `APPLIES-CONDITIONALLY`, `DOES-NOT-APPLY`, or
  `NOT-YET-ASSESSED`;
- the artifact, claim, gate or proof step that consumes the source;
- an explicit non-claim and stop condition.

Internal scripts, Lean checks, finite runs, legacy copies and exploration IDs
are provenance evidence, not substitutes for an external literature citation.

## Artifact rules

1. **Manifest and certificate:** include external source IDs and precise
   locators in the evidence/provenance section; distinguish prior art from
   TECT-derived calculations.
2. **Claim card:** keep the literature-applicability crosswalk beside the
   claim before any substantive T4-or-higher import.
3. **Synthesis note/PDF:** include a `Prior work and applicability` section, a
   `TECT-specific contribution` section, and a references list. State clearly
   which results are standard, conditional, finite-only, or new to the
   registered model.
4. **Exploration ledger:** record bounded searches, source exclusions,
   applicability failures and unresolved literature questions. A search bound
   is never evidence that no literature exists.

## Publication and PDF economy

Do not issue a PDF for every intermediate lemma. Maintain source IDs and
locators in manifests and certificates, then consolidate them into one
gate-level synthesis PDF. Before publication, run a reference-completeness
audit that rejects missing source IDs, unresolved load-bearing hypotheses,
unlabelled novelty language, and citations without a precise locator.

## Legacy-source handling

Preserve selected legacy sources by path, hash and source ID. Mark them
`reference-only` until the current owner, conventions, finite parts and limits
are revalidated. Superseded or refuted historical conclusions remain visible
as counterevidence and must not be silently reused as positive support.

## Default reporting language

Every proof report must separate:

- established prior theorem;
- source-checked applicability;
- internally verified TECT result;
- conditional interface;
- failed or quarantined route;
- remaining gate.

No claim of novelty, physical interpretation, continuum validity or
Yang--Mills relevance may be made from a citation or finite verification pass
alone.
