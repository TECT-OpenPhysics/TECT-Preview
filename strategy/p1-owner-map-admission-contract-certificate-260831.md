# R-471 P1 owner and observation-map admission contract

R-471 is an additive T-061/T-054 support result. It preserves the existing
forward and observation-first inverse methods, their owner order, and every
promotion firewall. It adds a machine-checkable admission state machine so a
future source-owned packet can be resumed without treating a static fit,
finite comparator, software parser, or synthetic fixture as a physical owner.

## Exact scope

The contract is finite and claim-nonbearing. It checks the nine existing
forward owner slots in their established order:

1. generator or transfer;
2. state;
3. physical projection;
4. time boundary;
5. heat-root incidence;
6. root filtration;
7. conditional replicas;
8. raw-current spatial intertwiner;
9. production one-use q ledger.

It also checks the existing ordered inverse stages `F_reg`, `F_lim`, `F_eff`
and `F_obs`, followed by the candidate-neutral estimand, immutable scorer, and
prospective holdout requirements. The current packet is deliberately
`EMPTY_OWNER_ARTIFACT` with zero admitted candidates. A complete synthetic
packet is accepted only as `CONTRACT_TEST_ONLY_COMPLETE`; it cannot enter a
scoring or prospective state.

## Why this is a useful new step

R-449 audited the leakage boundary and R-470 stopped generic parser-source
intake. R-471 does not repeat either audit. It turns their boundary into a
reusable transition predicate: missing source hash, any missing owner slot,
any missing earlier map stage, missing holdout/scorer, or synthetic provenance
is a deterministic fail-closed state. This makes later owner intake resumable
and prevents accidental promotion while leaving the research route itself
unchanged.

## Verification

The primary lane checks the authority hashes, exact slot and stage order,
current empty state, synthetic-fixture firewall, missing-hash boundary,
missing-stage boundary, and missing-holdout boundary. The independent lane
recomputes the same states with a separate set/order implementation. The
hostile lane applies fourteen mutations, including source-hash deletion,
synthetic relabelling, owner-slot deletion, each map-stage deletion, holdout
and scorer unfreezing, malformed digest, and method-firewall reversal; every
mutation is rejected. The integrated verifier runs all three lanes and the
pinned Lean file.

Observed run summary:

| lane | result |
| --- | --- |
| primary | 24/24 PASS |
| independent | 18/18 PASS |
| hostile | 18/18 PASS; 14/14 mutations rejected |
| integrated | 10/10 PASS |
| Lean | `lake env lean Tect/R471.lean` PASS |

## Assumptions and missing assumptions

The R-449 owner/proof boundary, the T-059 four-layer and four-stage map, and
the R-470 parser stopping boundary are hash-pinned authorities. A source hash
identifies bytes but does not prove physical identity. The nine slots and four
stages are existing contracts, not a new dynamics choice. Lean checks only
Boolean admission logic.

Still missing are a versioned physical-owner generator/transfer, state,
projection, time boundary, all five production proof-owner slots, a complete
candidate-neutral map with covariance/nuisance/scorer, and a prospective
holdout. Uniform limits and any QFT, Yang--Mills, gravity, physical-sector or
continuum identification remain outside this result.

## Adversarial review

* A static or deterministic comparator could be promoted to production. **Rejected:** all nine slots and a source hash are required, and the current count
  remains zero.
* A synthetic complete fixture could silently become a candidate. **Rejected:**
  the synthetic bit is checked in both source and packet, and Lean proves it
  cannot satisfy the production predicate.
* A later map stage could be scored while an earlier stage is absent.
  **Rejected:** the ordered stage loop stops at the first missing stage, and
  Lean proves the `F_reg`/`F_lim` guards.
* A holdout could be disclosed or retuned before scoring. **Rejected:** the
  immutable-scorer and prospective-holdout flags are independent required
  fields and hostile unfreezing is rejected.
* This contract could replace the established proof route. **Rejected:** all
  method-preservation flags are asserted and the result changes no claim tier,
  owner order, stopped-loop registry, or physical input.

## Boundary and next gate

Evidence level is T0 model-consistency/admission tooling only. No owner is
admitted, no candidate is scored, and no physical or mathematical claim is
advanced. Keep the state `EMPTY_OWNER_ARTIFACT`; request the versioned
validity/interpolation, common-time-standard, detector-to-geocenter and
timing-uncertainty owner packet for T-061 while resuming the unchanged T-054
owner-level Q3LOCK queue. Only a real non-synthetic packet that fills every
slot and all four map stages may move to the next state.

## Files

* [machine contract](p1-owner-map-admission-contract-v0.1.json)
* [primary lane](../codes/foundations/p1_owner_map_admission_contract.py)
* [independent lane](../codes/foundations/p1_owner_map_admission_contract_independent.py)
* [hostile lane](../codes/foundations/p1_owner_map_admission_contract_hostile.py)
* [integrated verifier](../verification/scripts/p1_owner_map_admission_contract_verify.py)
* [Lean cross-check](../verification/lean/Tect/R471.lean)

