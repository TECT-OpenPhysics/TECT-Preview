# R-168 v1.0 certificate: prospective holdout freeze protocol and current-tree readiness

- **Exploration:** `EXP-000807`; validator hardening correction `EXP-000808`
- **Result:** `R-168`, version `v1.0`
- **Stable result ID:** `PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-READINESS-AUDIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

R-168 does not issue a prediction or a freeze.  It closes the protocol layer
needed before a future blind Pre-A holdout can be issued and audits the exact
registered state at commit `99157442831c0e44d425b5d5f8cd78856c57da53`.
At that checkpoint there are no official freeze records, no admitted
microscopic survivors, and no admitted M1, M2 or M5
microscopic-map/prediction pair.  The parent prospective-evidence gate
therefore remains open.  The initially observed local `freeze/*` tag count is
reported separately as a non-load-bearing live observation, not as an
audited-commit fact or a historical PASS condition.

The closed protocol subgates are exactly:

1. `PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA`;
2. `PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL`;
3. `PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR`;
4. `PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT`.

The following gates remain open:

- `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`;
- `PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER`;
- `PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT`;
- `PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION`;
- `PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-VERIFICATION`.

## 1. Objects that must be frozen separately

A prospective test has one candidate-neutral object and one
candidate-specific object.

The candidate-neutral object is the common target contract:

\[
 {cal T}=({\rm estimand},{\rm units},{\rm raw\ estimator},
           {\rm disclosure\ rule},{\rm independence\ group}).       \tag{1.1}
\]

It defines what the later blind datum means without containing its value.
The raw estimator is a hash-pinned program applied unchanged after
disclosure.

For every microscopic candidate `M_i`, the candidate-specific object is a
map certificate

\[
 {cal M}_i:\ ({\rm microscopic\ parameters,state,reference,limits})
       \longmapsto {cal T}.                           \tag{1.2}
\]

An admitted map records its theorem statement, domain, state and reference,
units map, order of limits, nuisance inputs, proof references, executable
script and normalized source hash.  `ABSENT`, `CONDITIONAL_POSTHOC` and
`NOT_ADMITTED` maps are not eligible.

The effective baseline `M0` is mandatory and unique, but it is not eligible
to win as a microscopic theory.  At least one actual microscopic contestant
must have both an admitted map and a nonempty physical prediction before a
real freeze can validate.

This separation prevents an otherwise fatal ambiguity: freezing a common
experimental number does not by itself freeze how each microscopic theory
maps to that number.

## 2. Machine freeze schema

The machine schema is

`tect/pre-a-round1-prospective-holdout-freeze/1.0`.

Its exact root fields are:

```text
schema, freeze_id, prediction_id, freeze_version, round_id, parent_gate,
status, claim_bearing, fixture_only, contestant_snapshot, evidence_snapshot,
target_contract, observable_contract, prediction_contract,
robustness_contract, provenance, scoring, no_overclaim
```

A valid freeze has status `FROZEN_UNSCORED`, is claim-nonbearing, and is not a
synthetic fixture.  All contestant manifests, evidence snapshots, admitted
map scripts, the raw estimator and the scorer are normalized-SHA-256 pinned.
The contestant IDs are unique; there is exactly one effective baseline; and
every score-eligible microscopic contestant has an admitted map.
The root `freeze_id`, `prediction_id`, `round_id` and `no_overclaim` strings
must be nonempty.  The target `target_id`, `custodian`,
`protocol_or_accession`, `estimand_id` and `units` strings must also be
nonempty.  Its `estimand_id` and `units` must equal those in
`observable_contract.common_estimand`.
Before any semantic comparison, every declared leaf is checked for its exact
Boolean, positive-integer, nonempty-string, digest/OID, UTC-time, null or enum
type, and every declared container is checked as an object or list before
descent.  The contestant, evidence, observable, common-estimand, raw-estimator,
candidate-map, provenance and scoring objects also use exact field allowlists.
Thus a list cannot stand in for a role, signature, input class or estimand
definition, and an integer cannot stand in for a digest or object ID.

The prediction contract freezes:

- one exact `candidate_id` naming the microscopic contestant whose frozen
  prediction is being issued;
- the predicted relation and its physical units;
- theory uncertainty and the acceptance rule;
- the baseline prediction;
- the complete classified input ledger;
- forbidden post-freeze knobs; and
- robustness envelopes for volume, boundary, regulator, coefficients and
  independent implementation.

The exact target-contract fields are:

```text
target_id, custodian, protocol_or_accession, estimand_id, units,
independence_group, blind, predictor_access_before_freeze,
target_value_present, commitment, disclosure
```

The exact commitment fields are:

```text
algorithm, commitment_hex, secret_key_custody, payload_schema,
canonical_serialization, domain_separation, custodian_signature,
public_key_fingerprint, issued_at_utc
```

The exact disclosure fields are:

```text
status, not_before_utc, actual_at_utc
```

The exact prediction fields are:

```text
candidate_id, predicted_relation, physical_output, theory_uncertainty,
acceptance_rule, baseline_prediction, allowed_inputs, forbidden_knobs
```

Every allowed-input row has exactly:

```text
id, class, source, source_id, used_for
```

The robustness contract has exactly `volume`, `boundary`, `regulator`,
`coefficients` and `implementation`, each with a nonempty textual frozen
envelope.  An admitted map must also contain a list-valued `nuisance_inputs`
field, even when that list is empty.  Candidate maps are unique by
`candidate_id`.  The singular frozen prediction is the one-candidate instance
of candidate predictions uniquely keyed by `candidate_id`; its ID must be both
score-eligible and backed by an admitted map, and its predicted relation must
be nonempty.

No declared target value, reported value, observed value, corresponding
interval, or registered target-bearing alias is permitted anywhere in the
freeze object.  Exact root, target, commitment, disclosure, prediction and
allowed-input allowlists also reject undeclared payload fields at those
structurally controlled locations.  This syntactic firewall is not a proof
against arbitrary target information steganographically encoded in an allowed
free-text field.

## 3. Temporal and cryptographic provenance

The required temporal order is

\[
 t_{\rm custodian}\ \leq\ t_{\rm public\ freeze}
 \ <\ t_{\rm disclosure}\ \leq\ t_{\rm score}.       \tag{3.1}
\]

The target and the HMAC key must be held by an independent custodian.  Let
`JCS(T)` denote RFC 8785 JSON canonicalization of a payload with schema
`tect/pre-a-round1-holdout-target-payload/1.0`, and let
`D = TECT-PRE-A-ROUND1-HOLDOUT-TARGET-v1`.  The required commitment is

\[
 C={\rm HMAC\mbox{-}SHA256}
   (K_{\rm custodian},\ D\mathbin\Vert {\tt 0x00}\mathbin\Vert {\rm JCS}(T)).
                                                        \tag{3.2}
\]

Here `0x00` is the single zero-octet domain separator.  The exact machine
field is `secret_key_custody: EXTERNAL_CUSTODIAN`; author-held keys are not
accepted.  The custodian also signs the commitment metadata containing the
payload schema, canonicalization, domain separator, digest and issue time.
A plain unkeyed hash of a low-entropy numerical target is reversible by
enumeration and is not accepted.

The public freeze anchor contract requires:

- the remote repository URL;
- the exact remote commit object ID and observation time;
- the annotated tag `freeze/<PRED-ID>/v<N>`;
- the distinct annotated-tag object ID; and
- the corresponding remote reference.

An unpushed local commit, filesystem modification time, or self-declared
`issued_on` field is not evidence of prospective ordering.  Creation of the
annotated tag is a separate irreversible release action and requires explicit
operator authorization; R-168 creates no tag.

The current executable checks the shape of these fields and local hash pins.
It does not verify a custodian signature against a public key and does not
fetch the remote commit, tag reference or annotated-tag object.  A real
freeze must remain fail-closed until a separate verifier performs those
cryptographic and remote checks and records an independently authenticated
receipt.

Every local hash pin uses a normalized relative POSIX repository path.  Drive
paths, absolute paths, backslashes, dot segments, parent traversal and paths
that resolve outside the repository are rejected.  This local check does not
prove that the path and blob occur in a remote freeze commit; the separate
remote verifier must fetch that commit and establish the binding.

Before disclosure the scoring state must remain `NOT_DISCLOSED`, with no
target or result path.  The frozen scorer is later executed unchanged.

## 4. Discovery and target-independence firewall

Every discovery or fitting datum is listed in `discovery_ids` and copied into
the forbidden-fit set for the blind prediction.  The target independence
group must be disjoint from both discovery and calibration groups.  Inputs
are classified as one of:

```text
INSERTED, FITTED, MATCHED, CALIBRATION, DERIVED, PREDICTED,
VISIBLE_VALIDATION, NOT_AVAILABLE.
```

The allowed-input ledger is nonempty, has unique IDs, identifies a nonempty
`source`, nonempty `source_id` and class for each input, and rejects a
`source_id` in either `discovery_ids` or `forbidden_fit_ids`.  Missing IDs and
undeclared source-ID aliases are rejected by the exact row schema.  These
checks do not make an input scientifically valid; they make prohibited reuse
machine-detectable.

## 5. Fail-closed validator and hostile fixtures

The executable validator is

`codes/foundations/pre_a_round1_prospective_holdout_freeze_protocol.py`.
It validates a synthetic contract whose values are generated only from
fixture data.  It then mutates one load-bearing field at a time and rejects
all 28 hostile classes:

1. an undeclared root payload (`ROOT_FIELDS_EXTRA`);
2. empty root identity strings (`ROOT_VALUES_INVALID`);
3. empty target identity strings (`TARGET_CONTRACT_INVALID`);
4. a target/common-estimand ID or units mismatch
   (`TARGET_ESTIMAND_MISMATCH`);
5. a direct target value or interval (`TARGET_LEAKAGE`);
6. a hidden `sealed_payload` in the commitment (`TARGET_LEAKAGE`);
7. a registered `holdout_value` target alias (`TARGET_LEAKAGE`);
8. disclosure before the public freeze (`TEMPORAL_ORDER_INVALID`);
9. a mutated candidate, evidence, map, estimator or scorer hash
   (`HASH_FAILURE`);
10. a parent-traversing repository path (`HASH_FAILURE`);
11. overlap of target and discovery/calibration independence groups
   (`INDEPENDENCE_OVERLAP`);
12. a missing unique effective baseline (`BASELINE_MISSING`);
13. duplicate candidate maps (`MAP_CANDIDATE_DUPLICATE`);
14. an eligible candidate with no admitted map (`ELIGIBLE_MAP_MISSING`);
15. a generic prediction not bound to an eligible admitted-map candidate
    (`PREDICTION_CANDIDATE_UNBOUND`);
16. a missing allowed-input `source_id` (`INPUT_FIELDS_INVALID`);
17. reuse of a discovery `source_id` (`DISCOVERY_REUSE`);
18. an undeclared `discovery_source_id` alias (`INPUT_FIELDS_INVALID`);
19. a malformed nested commitment type (`COMMITMENT_INVALID`);
20. list-valued signatures and integer-valued commitment digests
    (`COMMITMENT_INVALID`);
21. integer-valued commit and tag object IDs (`REMOTE_ANCHOR_INVALID`);
22. an HTTPS URL with no parsed hostname (`REMOTE_ANCHOR_INVALID`);
23. a list-valued input class and null `used_for`
    (`INPUT_LEDGER_INVALID`);
24. a non-string common-estimand definition (`ESTIMAND_INVALID`);
25. a non-string contestant role (`CONTESTANTS_INVALID`);
26. a non-object common estimand (`ESTIMAND_INVALID`);
27. a non-object raw estimator (`ESTIMAND_INVALID`); and
28. malformed or absent public-anchor metadata (`REMOTE_ANCHOR_INVALID`).

Wrong nested types return structured rejection reports; they do not escape as
attribute or hashing exceptions.

The synthetic fixture has `fixture_only: true`.  Its sole purpose is to test
the schema and hostile mutations without inventing a physical prediction.
The present validator rejects all purported real freezes with an explicit
external-verification requirement; changing `fixture_only` is not sufficient
for promotion.

## 6. Exact current-tree audit

At the audited checkpoint the executable reconstructs the registered state
from the hash-addressed Round-1 manifest, admission freeze, candidate
manifests and freeze-directory blobs.  The exact stable snapshot counts are

\[
 N_{\rm records}=0,\qquad
 N_{\rm admitted\ microscopic\ survivors}=0.          \tag{6.1}
\]

The record and candidate inputs are read from the audited commit blobs rather
than dirty working-tree copies.  Separately,
`N_tags^{local,initial}=0` was a non-load-bearing live observation made during
the initial audit.  It is not encoded by the audited commit, is not a blocker,
is not a remote query or cryptographic receipt, and is not required to remain
zero.  A future legitimate freeze tag may change the live observation without
invalidating the historical R-168 result.

The candidate rows read:

| Candidate | Admitted microscopic map | Frozen physical prediction |
|---|---:|---:|
| M1 | no | no |
| M2 | no | no |
| M5 | no | no |

M2 contains a retrospective conditional mapping only; its registered
`physical_predictions` list is empty and its holdout flag is false.  Such a
post-hoc relation cannot be converted retroactively into a prospective blind
test.

The exact blocker set is:

```text
NO_MACHINE_FREEZE_RECORD
NO_ADMITTED_MICROSCOPIC_SURVIVOR
M1_MAP_AND_PREDICTION_ABSENT
M2_PHYSICAL_PREDICTION_AND_HOLDOUT_ABSENT
M5_MAP_AND_HOLDOUT_ABSENT
PER_PARAMETER_COMMON_INPUT_LEDGER_INCOMPLETE
PROSPECTIVE_PREDICTION_NOT_FROZEN
```

Therefore `actual_freeze_ready=false`.  This conclusion is a deterministic
audit of the seven stable blockers in the registered checkpoint, not a claim
that no future candidate can ever acquire a map or prediction.  The live tag
observation does not enter this Boolean.

## 7. Exact completion condition

The parent gate can advance only after all of the following exist before
target disclosure:

1. an independent custodian's externally keyed, signed canonical
   HMAC-SHA-256 target commitment;
2. a candidate-neutral common estimand and hash-pinned raw estimator;
3. at least one admitted candidate-specific microscopic map;
4. a nonempty physical prediction with a complete common-input ledger;
5. a frozen baseline, uncertainty and acceptance rule;
6. a public remote commit and separately authorized annotated freeze tag;
7. cryptographic signature validation plus independent remote object/ref
   verification and an authenticated receipt;
8. independent implementation and the declared robustness envelope; and
9. later execution of the unchanged scorer after the documented disclosure.

The target itself is external information.  It cannot be manufactured by a
repository proof or repaired retrospectively after disclosure.

## 8. Status and no-overclaim boundary

R-168 closes the schema, provenance-order contract, anti-leakage *schema*
validator and current-tree empty-admission audit.  The anti-leakage result is
syntactic: no declared target-bearing alias or undeclared payload field is
admitted at the exact-controlled structural locations, but arbitrary
free-text steganography is outside the proved scope.  It registers

`NG-2026-08-11-PRE-A-ROUND1-CURRENT-TREE-PROSPECTIVE-HOLDOUT-NONEXISTENCE`

only as a current-checkpoint nonexistence result.  It is not a no-go for a
future independently committed target or for a future admitted microscopic
map.

No cryptographic custodian-signature check, remote-ref verification, actual
freeze, target, prediction, score, candidate selection or tag is created.
Nothing here fixes nature's functional, proves a below-empty sign, selects a
physical vacuum, establishes common Q3LOCK dynamics or a sector gap, closes
C6 or CP1, or closes physical Sector A or Pre-A.
