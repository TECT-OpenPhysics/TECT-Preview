# R-497 claim/result lineage decision

**Date:** 2026-09-08  
**Scope:** EXP-000780 -> EXP-000781 -> EXP-000782 and the Q3LOCK phase-coexistence paper package  
**Current tier:** T0, `claim_bearing=false`, `INTERNAL_REVIEW_ONLY`  
**PDF status:** DEFERRED

## Decision

R-497 is already the appropriate independent result registration for the
Q3LOCK paper at the current research stage. No new canonical
`claims/<ID>/` card is created for the paper result.

The result-level authority is the pair
`strategy/q3lock-exp782-independent-result-manifest-260905.json` and the
R-497 entry in `RESULTS-LEDGER.md`, with the manuscript verification package
as its consumer. The manifest records the exact model, authority chain,
bounded statement, evidence role, open gates, nonclaims, reproduction
artifacts, and source hashes. This is sufficient to keep EXP-000782 from
remaining only an exploration record while preserving its honest T0 status.

## Why a separate claim card is not created now

1. The canonical claim-card taxonomy is for the TECT Sector A--F theory
   claims. R-497 is a standalone mathematical-model result used by a
   research-paper package, not a completed physical-sector claim.
2. `C6-SPACETIME-SIGNATURE` is an independent TECT scaffold about emergent
   3+1 Lorentzian structure. Its appearance as `claim_context` in the R-497
   manifest is provenance/routing metadata only; it is not a dependency and
   does not make Q3LOCK evidence for C6.
3. Creating a second T0 card would duplicate the result authority and could
   be misread as a TECT-sector promotion or as evidence for C6. The manifest
   and result ledger already provide the required independent result lineage.
4. A later claim card is permitted only after an explicit sector owner,
   dependency map, and external mathematical disposition are agreed. Such a
   card would be a new integration decision, not a retroactive relabelling of
   R-497.

## Consequences

- The bounded claim/result-lineage gate is resolved as a routing decision;
  R-497 remains T0 and claim-nonbearing.
- The paper may cite R-497 as a reusable result-registration candidate, not
  as a certified theorem or a TECT physical-sector closure.
- The open gates remain the source/form-domain/topology/limit audit,
  external literature and mathematical review, content freeze, clean replay,
  release checks, and final submission review.
- No claim tier, physical interpretation, C6 status, Sector-A status, or
  publication status changes.
- No PDF is generated before content review, signed external disposition, and
  final content freeze.

## Nonclaims

This decision does not establish the Q3LOCK theorem, close any A1--A23 proof
row, promote R-497, establish a common dynamics/KMS or ground-state gap,
remove a regulator, or support a cosmological interpretation. It also does
not make a novelty, priority, or absence claim about the literature.

## Required follow-up

Update the R-497 manifest and paper readiness surfaces to point to this
decision, rerun the result/package/release consistency checks, and then obtain
the outstanding independent mathematical and literature reviews. Only after
those reviews and a content freeze may the final PDF be built and visually
audited.
