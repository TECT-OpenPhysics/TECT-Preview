# Literature-First Proof Gate and Legacy-Evidence Audit

**Binding from:** 2026-08-14. This policy governs new substantive proof work,
claim promotions, and any reuse of legacy or external mathematical results.
It complements `governance/claim-standard.md`, the tier system, and the
proof-exploration ledger; it does not make a literature citation into a TECT
theorem.

## 1. Purpose

TECT must not spend proof effort reproducing known mathematics without first
determining whether an existing result applies. Conversely, it must not treat
a named theorem, a legacy note, a simulation, or a previous TECT result as a
load-bearing premise merely because it exists. The required question is:

> What exact conclusion is needed, which source could supply it, and do that
> source's hypotheses hold for the declared TECT object?

The outcome is one of four honest dispositions: `APPLIES`,
`APPLIES-CONDITIONALLY`, `DOES-NOT-APPLY`, or `NOT-YET-ASSESSED`.

## 2. Mandatory applicability record

Before a new T4-or-higher claim, a tier promotion, or a new proof route uses
an external or legacy result as a load-bearing input, create
`claims/<ID>/literature-applicability.md`. A route that has no claim card yet
records the same information in its strategy certificate and in
`explorations/log.jsonl`.

The record must contain:

1. the exact target statement and the intended role of the imported result;
2. a stable primary source or immutable archived source, including theorem,
   proposition, or page locator;
3. an assumption-to-model crosswalk, with every source hypothesis marked
   `SATISFIED`, `CONDITIONAL`, `FAILED`, or `UNASSESSED`;
4. the exact conclusion actually imported, its quantifiers, and its
   regulator, volume, dimension, algebra, and state scope;
5. a reproduction or independent-check disposition, or a reasoned waiver
   that explicitly limits the evidence grade;
6. at least three adversarial checks: convention/sign, domain/regularity, and
   limit/order-of-limits; and
7. the residual proposition that is genuinely new for TECT, or the stop
   decision that no new proof is needed.

Summaries, review articles, search snippets, and informal recollection may
identify candidates but never close this record. They are not primary evidence
for a load-bearing import.

## 3. Literature-first route order

Every substantive route follows this order:

```text
exact target statement
  -> literature and legacy search
  -> source and hypothesis crosswalk
  -> applicability, conditional applicability, or obstruction decision
  -> prove only the residual proposition
  -> independent audit and registered scope boundary
```

If a known theorem applies, cite it and prove only the model-specific
crosswalk. If it does not apply, record the failed hypothesis and do not cite
its conclusion. If no applicable source is found, record the bounded search
scope and queries; this is not a claim of world-first novelty.

## 4. Legacy and internal-result quarantine

Legacy material is provenance, not certification. A legacy or previous TECT
result may be reused only at the strength supported by its current claim card,
reproduction status, evidence grade, hypotheses, open gates, and no-overclaim
statement.

For every load-bearing legacy or internal result, the applicability record
must separately verify:

- identity of the functional, field space, symmetry, regulator, and
  renormalisation convention;
- preservation of the comparison reference and observable normalisation;
- the relevant finite-volume, thermodynamic, continuum, and zero-temperature
  limit order; and
- an independent attempt to falsify the import by a counterexample,
  alternative formulation, or reproduction audit.

A refuted result remains a negative control only. A scoped result cannot be
silently widened, and a verification-script PASS is never an independent
analytic proof audit. Existing claims are not retroactively invalidated by
this policy, but none may be promoted or used to promote a physical conclusion
until its required applicability record is complete.

## 5. Promotion and stop rules

`NOT-YET-ASSESSED` or `FAILED` on any load-bearing crosswalk blocks the route
from supporting a T6/T7 promotion or a physical conclusion. A conditional
import must appear as a named hypothesis in the claim statement. The evidence
grade must state `INHERITED` or `CONDITIONAL` where appropriate.

The correct response to a successful applicability record is often to stop:
reuse the known theorem, preserve its provenance, and redirect effort to the
first unmet hypothesis or residual proposition. The correct response to a
failed crosswalk is also often to stop: register the obstruction or negative
result rather than repair the model by an unregistered assumption.

## 6. Initial rollout

The registered route gate is
`LITERATURE-FIRST-APPLICABILITY-AUDIT`. `T-056` owns the phased rollout. Its first audit set is the live
QFT/GR/Reading-H path: `B1-RH-ENUM`, `C4-GRAVITY-1LOOP`,
`C5-NEWTON-G`, and `C6-SPACETIME-SIGNATURE`. The audit must distinguish
standard background mathematics, valid model-specific imports, unresolved
legacy chains, and genuinely open residual propositions. It must not promote
or demote a claim merely by creating an applicability record.
