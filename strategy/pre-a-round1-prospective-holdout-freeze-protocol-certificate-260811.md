# R-168 v1.3 certificate: prospective holdout protocol and scoped M2 response-map theorems

- **Explorations retained:** `EXP-000807`, `EXP-000808`, `EXP-000810`, `EXP-000812`
- **Additive exploration:** `EXP-000814`
- **Result:** `R-168`, version `v1.3`
- **Stable result ID:** `PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-READINESS-AUDIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

R-168 v1.3 is cumulative. Sections 1--20 retain every v1.0--v1.2
protocol, current-version audit, fingerprint, nonidentifiability, schema, and
issued v1.2 checkpoint statement. Sections 21--27 add five narrowly scoped
mathematical children and four named shortcut rejections. They create no M2-v1
candidate, physical response, target, prediction, freeze, or claim-tier change.
The audited current-tree checkpoint remains commit
`99157442831c0e44d425b5d5f8cd78856c57da53`; its zero freeze-record and zero
admitted-survivor facts remain unchanged.

The cumulative closed-child list used by this proof-first package is exactly:

1. `PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA`;
2. `PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL`;
3. `PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR`;
4. `PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT`;
5. `PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET`;
6. `PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT`;
7. `PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY`;
8. `PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA`;
9. `PA-M2-CI8-V0-REAL-SCALAR-INTERNAL-U1-TRIVIALITY-AND-NO-INTRINSIC-WINDING`;
10. `PA-M2-CI8-ONE-Q-AUXILIARY-PHASON-CURVATURE-AND-FINITE-TORUS-SECANT`;
11. `PA-M2-CI8-HELICITY-TENSOR-CONTACT-SHIFT-NONIDENTIFIABILITY`;
12. `PA-M2-CI8-ANALYTIC-MAP-INTEGER-EXPONENT-TRANSPORT`; and
13. `PA-M2-CI8-SIX-STAGE-RELATIVE-LOG-SLOPE-ERROR-TRANSPORT`.

The complete open-gate list is:

- `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`;
- `PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER`;
- `PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT`;
- `PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION`;
- `PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-VERIFICATION`;
- `PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND`;
- `PA-M2-SUCCESSOR-SUBSTANTIVE-COMPACT-ACTION-BACKGROUND-PROBE-AND-WINDING-LAW`;
- `PA-M2-SUCCESSOR-ORDERED-STATE-PHYSICAL-MODE-AND-RESPONSE-LIMIT`; and
- `PA-M2-SUCCESSOR-SIX-TERM-CRITICAL-ESTIMAND-ERROR-BUDGET`.

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
## 9. R-168 v1.1 cumulative extension

Sections 1--8 are the retained `EXP-000807` / `EXP-000808` v1.0 protocol,
hardening audit, 28 hostile schema classes, and seven stable readiness
blockers.  `EXP-000810` adds two closed mathematical children and one scoped
current-version no-go without changing any v1.0 conclusion:

1. `PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET`;
2. `PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT`; and
3. `NG-2026-08-11-PRE-A-ROUND1-CURRENT-VERSION-MAP-ONLY-ADMISSION-REPAIR`.

The new open successor gate is
`PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND`.
The stable result ID remains
`PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-READINESS-AUDIT`,
now at `R-168 v1.1`.

## 10. Exact current-version map-only empty set

The current contestant versions are fixed by the normalized hashes in
`pre-a-round1-admission-discriminator-freeze-260810-v1.0.json`.  Reading the
candidate records themselves gives:

| Current version | Exact map evidence | Map-only admitted |
|---|---|---:|
| `PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0` | `observable_map.map_to_round1_measured_observables=false` | no |
| `PA-M2-CI8-RS-v0` | no `observable_map`; `physical_predictions=[]`; `holdout_prediction=false`; the normalized stiffness relation is `ABSENT` and posthoc | no |
| `PA-M5-NL3-SV-v0` | `observable_map.map_to_measured_observables=false` | no |

Thus the set of current hash-pinned versions carrying an admitted
candidate-specific microscopic-to-common-observable map is exactly empty.
This is derived row by row; it is not inferred from the pre-existing empty
survivor list.

Changing any one of those exact candidate records to add or admit a map
changes its content and therefore leaves the pinned version.  That observation
is only the first layer.  The non-tautological second layer binds the frozen
survival rule:

```text
survives iff every D00--D09 hard row is PASS
```

and reads the map-independent or non-map-only residual cells directly from the
frozen categorical matrix:

| Parent law/state preserved | Residual hard rows after a hypothetical map-only addition |
|---|---|
| `M1-v0` | `D01=FAIL`; `D02=NOT_ADMITTED` because no conservative real-time kinetic law/tensor is supplied |
| `M2-v0` | `D03=NOT_ADMITTED`, `D05=NOT_ADMITTED`, `D06=NOT_TESTED`, `D08=NOT_ADMITTED` |
| `M5-v0` | `D04=FAIL`, `D05=FAIL` |

Consequently, even a hypothetical new version that changes only the
microscopic response-map slot while preserving law, state space, reference,
boundary, regulator, dynamics, compactness, quotient data, critical contract,
validation contract, and robustness has no all-PASS survivor.  M2's D05 cell
includes an absent compact configuration and winding/flux law; those objects
cannot be supplied by relabelling an observable response map.  M1 requires a
conservative kinetic law and a D01 state/law/ensemble repair.  M5 requires a
dispersion-changing isolated-node/law repair and a genuine compact gauge
connection.

Adding inertial, compact, gauge, state, law, boundary, or regulator data is
therefore not a map-only repair.  It defines a substantively new candidate
version and must rerun all ten hard rows.  The scoped negative above rejects
only map-only promotion under preserved parent law/state data; it is not a
no-go for such a substantively new candidate.

Two executable engines also reject seven hostile attempts to manufacture this
conclusion: removing a hard row, softening the all-PASS rule, promoting the M1,
M2, or M5 residual cells, dropping regulator preservation from the map-only
scope, or fabricating a survivor.

## 11. Why the retrospective M2 stiffness map is underdetermined

Let the exact mathematical stiffness behave as

\[
  \kappa(t)=C|t|,\qquad C>0.                              \tag{11.1}
\]

The current M2-v0 record does not specify the physical response channel.  Two
target-free completions of that missing slot are

\[
  {\cal R}_1(\kappa)=\kappa/\kappa_0,
  \qquad
  {\cal R}_2(\kappa)=(\kappa/\kappa_0)^2.                \tag{11.2}
\]

They yield exponents one and two, respectively, from the same exact
stiffness.  At the rational fixture `t=1/8`, doubling `t` gives exact response
ratios two and four.  These are logical completions of an absent schema slot,
not admitted physical maps or candidate predictions.  Therefore the old
retrospective exponent one encodes the identity-response choice; it is not
forced by the M2-v0 microscopic record and receives no prospective validation
credit.

## 12. Exact 48-component finite-torus fingerprint

Take the Gaussian M2 kernel

\[
 K(k)=r+c\sum_{j=1}^3(q^2-k_j^2)^2,
 \qquad h={2\pi\over L},\qquad q=mh,\qquad m\in\mathbb N. \tag{12.1}
\]

For every sign node `s` in `{+1,-1}^3`, put `k_s=q s`.  For each axis `i`
define the dimensionless one-step increments

\[
 d_\pm={K(k_s\pm h e_i)-K(k_s)\over c h^4},\quad
 S={d_++d_-\over2},\quad A={d_+-d_-\over2}.             \tag{12.2}
\]

Direct expansion gives

\[
 S=4m^2+1,\qquad A=4s_i m.                               \tag{12.3}
\]

With `bar S_s=(S_{s,1}+S_{s,2}+S_{s,3})/3`, the two
dimensionless components at every node-axis pair are

\[
 R_{s,i}={A\over S}{4m^2+1\over4s_i m}=1,
 \qquad
 U_{s,i}={S\over\bar S_s}=1.                             \tag{12.4}
\]

The declared ordering is lexicographic in the eight sign nodes, then
`i=1,2,3`, then `(R,U)`.  It therefore has exactly
`8*3*2=48` components, all exactly one.  Primary `Fraction` arithmetic and a
non-importing independent integer cross-multiplication engine reconstruct the
whole ordered vector.  This is a finite-torus Gaussian fingerprint, not a
physical dispersion prediction.

## 13. Schema-only M2 successor design

The hypothetical identifier

`PA-M2-CI8-RS-DISPERSION-MAP-v1`

appears only in a machine-validated design object with
`status=DESIGN_ONLY`, `candidate_created=false`, and every admission, map,
prediction, target, freeze, tag, score, and selection status equal to
`NOT_CREATED`.  Its manifest path and hash are null.

The design requires, but does not supply, a physical response channel, a
candidate-neutral estimand, state/reference and unit conventions, order of
limits, a complete prospective input firewall, independent implementation,
and a controlled error budget.  The new hostile suite rejects candidate
materialization, in-place admission, map promotion, prediction/target/freeze/
tag/score/selection payloads, smuggled response maps, incomplete error terms,
and a mutated fingerprint dimension.  These successor hostile cases are
additive; the 28 v1.0 hostile freeze-schema classes remain exact and unchanged.

## 14. Precise open physical-response and error-bound gate

`PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND` remains open until a
new candidate version, frozen before target access, supplies a target-blind
map from its microscopic field/state/reference and all nuisance inputs to the
candidate-neutral estimand, with units, quotients, polarizations, and limit
order fixed.  It must prove a reproducible bound of the form

\[
 |O_{\rm phys}-{\cal R}_{M2}|
 \leq \epsilon_{\rm torus}+\epsilon_{\rm regulator}
      +\epsilon_{\rm nonlinear}+\epsilon_{\rm loop}
      +\epsilon_{\rm state/ref}+\epsilon_{\rm estimator},             \tag{14.1}
\]

where every term is computed from frozen inputs and the total is strictly
smaller than the frozen acceptance margin before disclosure.  The Gaussian
fingerprint alone supplies none of these physical identifications or error
terms.

The scripts expose staged formal checks for `EXP-000810`, the two child gates,
the new negative, the open response gate, and `R-168 v1.1`.  Staging is only a
package-assembly mode; a release PASS requires the append-only authorities.
No v1.1 PDF is issued here.

## 15. Post-validation combined v0.9 checkpoint issuance

After the proof-first package and only after the proof, formal-authority,
integrated, source-form, freshness, extraction, and render-review gates passed,
one combined R-167 v2.0 / R-168 v1.1 gate-level checkpoint was issued.
Its exact artifacts are:

1. source:
   `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-checkpoint-260811-v0.9.tex.txt`;
2. source SHA-256:
   `ca8b0fdc1c4881aa13e3311851c719d0b6a0dfb4b27e0bb30906f7bc77b04239`;
3. PDF:
   `claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-checkpoint-260811-v0.9.pdf`;
4. PDF SHA-256:
   `346595c8609be1e49fb33d87e5a469b01f9083c78d7a1fc89d3648b88ea4d243`;
5. page count: exactly 10.

The final R-167 v2.0 primary, non-importing independent, and integrated
contracts are `PASS 153/153`, `PASS 117/117`, and `PASS 220/220`.  The final
R-168 v1.1 contracts are `PASS 205/205`, `PASS 223/223`, and `PASS 262/262`.
Both pypdf and pdfplumber extracted 10/10 nonempty pages.  The build log had
zero Overfull `\hbox` warnings, and direct all-page review found zero
clipping, overlap, broken equations, unreadable identifiers, black glyphs,
malformed page transitions, or other visual defects.

No per-lemma or intermediate PDF was issued.  The v0.9 source/PDF pair is the
single combined post-validation checkpoint for these additive results.  The
historical v0.8 source/PDF remains prior R-167 v1.9 / R-168 v1.0 evidence and
is not current v2.0/v1.1 evidence.  This issuance changes no claim tier and
closes none of the common-alpha, rank-two oscillator, oscillator GNS-gap,
physical-response, prospective-freeze, physical Sector-A, or Pre-A parents.

## 16. R-168 v1.2 fixed-linear-probe nonidentifiability theorem

The additive exploration is `EXP-000812`.  Fix any finite-dimensional,
finite-volume regulated Lane-Q Hamiltonian `H(t)`, a self-adjoint linear probe
`Q`, a real source `J`, and a target-blind twice differentiable scalar
`d(t)`.  Define

\[
 H_d(t,J)=H(t)-JQ+{V\over2}d(t)J^2 I.                 \tag{16.1}
\]

Every member of this family has exactly the same zero-source Hamiltonian and
first source derivative,

\[
 H_d(t,0)=H(t),\qquad \partial_J H_d(t,0)=-Q.         \tag{16.2}
\]

Consequently the zero-source state, spectrum, field Hessian, and exact
48-component finite-torus fingerprint are unchanged.  At finite beta use the
sign convention

\[
 F_{\beta,d}(t,J)=-\beta^{-1}\log\operatorname{Tr}
 e^{-\beta H_d(t,J)}.                                \tag{16.3}
\]

The contact is scalar, so it factors exactly:

\[
 Z_d(t,J)=e^{-\beta Vd(t)J^2/2}Z_0(t,J),\qquad
 F_{\beta,d}(t,J)=F_{\beta,0}(t,J)+{V\over2}d(t)J^2. \tag{16.4}
\]

This certificate defines the helicity-like curvature with the **positive**
sign

\[
 \Upsilon_d(t)=+{1\over V}\partial_J^2F_{\beta,d}(t,0),
 \qquad \Upsilon_d-\Upsilon_0=+d(t).                 \tag{16.5}
\]

By contrast, the conventional scalar susceptibility is
`-V^-1*d_J^2 F_beta`; the same positive contact shifts that quantity by
`-d(t)`.  At beta infinity, scalar addition shifts every eigenvalue equally,
so wherever the ground branch is stable,

\[
 E_{0,d}(t,J)=E_{0,0}(t,J)+{V\over2}d(t)J^2,
 \qquad {1\over V}\partial_J^2(E_{0,d}-E_{0,0})=d(t). \tag{16.6}
\]

Thus even a completely fixed linear source observable does not identify a
second-order physical response until the quadratic contact or diamagnetic
term and its normalization are frozen.  This closes only
`PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY` and supports
the scoped negative
`NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-STIFFNESS-RESPONSE`.
It does not close `PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND`.

## 17. Exact Fraction and integer-cross-product fixture

The primary verifier uses `Fraction` throughout.  The independent verifier
uses a separately implemented normalized integer-rational engine.  Both take

```text
V=7, beta=3/2, h=1/5,
d_left=5/7, d_right=11/7, delta_d=6/7,
H_0(J)=diag(-J, 4+J).
```

At `J=h`, the difference of scalar contact free energies is exactly `3/25`,
and the finite-beta Boltzmann exponent shift is exactly `-9/50`.  The centered
second difference divided by `V` is exactly `6/7`.  For `J=-h,0,+h`, the first
diagonal branch remains the ground branch, with indices `[0,0,0]`.  The two
normalized ground-energy curvatures are exactly `5/7` and `11/7`, hence their
shift is again exactly `6/7`.  No floating-point logarithm, fitted number, or
hardcoded derived response is used; the displayed rationals are labelled test
oracles and are recomputed from the declared fixture inputs.

The theorem is a nonidentifiability result, not a proposed contact law.  A
source `J*phi` in the current real-scalar Lane-Q record measures a scalar
order-parameter susceptibility.  It is not automatically the physical
helicity or helium superfluid-density response, and the internal fingerprint
does not repair that type mismatch.

## 18. Hardened minimum physical helicity-response successor contract

The schema-child identifier is
`PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA`, with
schema

`tect/pre-a-m2-ci8-physical-response-successor-minimum-contract/1.1`.

Its formal gate authority is now registered, so the child is **closed only as a
syntactic and declared-binding schema contract**.  This does not validate physical
semantics or close the physical-response or Round-1 parents.  Its exact root fields remain:

`schema, contract_id, candidate_id, parent_candidate_id, status, fixture_only, candidate_created, version_delta, physical_control_map, probe_contract, state_reference_contract, response_definition, estimand_binding, critical_prediction, error_budget, common_input_ledger, hard_row_rerun, verification, prospective_firewall, no_overclaim`.

Every artifact reference now has exactly
`path, sha256, role, media_type`.  The path must be a normalized
repository-relative POSIX path with no absolute prefix, drive, backslash, dot
segment or parent traversal, embedded NUL, or length above 4096 characters.
Every segment must use exact case-sensitive on-disk spelling and may not end
in a space or dot; the resolved repository-relative POSIX spelling must equal
the supplied path exactly.  The file must exist, match its normalized SHA-256,
and satisfy the role-specific root, suffix and media-type rule.  `PurePath`,
`resolve`, directory-listing, `is_file`, `stat`, hash and open `OSError`,
`ValueError`, and `RuntimeError` failures become structured rejection rather
than exceptions.  These checks apply to the source law, linear probe,
quadratic contact, compact/gauge action, state-existence result,
physical-control map, response map, raw estimator, proofs, all error scripts
and run JSONs, and the three verifier roles.

A substantive successor declaration is a unique list drawn only from

`SECOND_ORDER_SOURCE_LAW, COMPACT_OR_GAUGE_ACTION, STATE_REFERENCE_CHANGE, PHYSICAL_CONTROL_MAP, REGULATOR_OR_LIMIT_CHANGE, ERROR_BOUND_PROOF, MICROSCOPIC_MAP_ONLY`.

The first six entries are mandatory.  A map-only singleton, a missing
mandatory item, an unknown value, a duplicate, or labels backed only by a
map-only payload fail closed.  This records the exact reason that merely
adding a linear source or microscopic map to the inertial Lane-Q Hamiltonian
does not yet create an honest M2-v1 physical-response candidate.

The contact, compact/gauge action, response, limit order and prediction are
structured enums.  `NONE`, `ABSENT`, `UNSPECIFIED`, `NOT_SUPPLIED`,
`NOT_CREATED`, `TBD`, `PLACEHOLDER`, `N/A`, `NA`, and `NOT_AVAILABLE` are never
accepted as their payloads.  The exact limit order is

`SOURCE_TO_ZERO, THERMODYNAMIC_LIMIT, REGULATOR_REMOVAL, CRITICAL_LIMIT_FROM_ORDERED_SIDE`;

a permutation is rejected.  The prediction must bind its candidate ID to the
contract candidate and its estimand ID to the candidate-neutral response
estimand.  The physical-control-map fields `physical_variable`, `r_of_t`,
`domain`, and `scaling_window`, and the prediction fields
`predicted_relation`, `scaling_window`, and `corrections`, additionally reject
`TARGET`, `HOLDOUT`, `DISCOVERY`, and `FORBIDDEN` tokens.  This finite lexical
firewall is a syntax rule, not a proof of semantic target independence.

The canonical positive-rational language used by both engines is
`[1-9][0-9]*(?:/[1-9][0-9]*)?`, with an explicit maximum length of 128
characters, followed by exact coprimality and canonical-spelling checks.  A
slash form must have denominator at least two; a denominator-one value must use
integer spelling.  Integer-conversion `ValueError` is caught in both engines.
The grammar therefore rejects decimals, signs, zero, whitespace, leading
zeros, zero denominators, unreduced fractions, and `1/1` or `3/1`.  In
particular, `1/10`, `1/100`, `3/50`, and `1` are accepted, while `0.1`, `2/20`,
` 1/10`, `1/1`, and `3/1` are rejected.

Exactly six error terms are required:
`finite_torus_spacing`, `regulator_removal`, `nonlinear_remainder`,
`loop_or_renormalization`, `state_reference_transfer`, and `raw_estimator`.
Every term binds an existing `codes/**/*.py` script ref, an existing
`claims/*/runs/*/result.json` ref, and a unique top-level result key that
actually exists in the run JSON.  All six result keys and all
`(script, run, result-key)` composites are distinct.  At least two distinct
proof refs are required.  The exact total must equal the sum and remain
strictly below the common estimand margin.

The input ledger rejects duplicate row IDs, duplicate source IDs,
`VISIBLE_VALIDATION`, `NOT_AVAILABLE`, and any target, holdout, discovery or
forbidden source ID.  Every section binds a nonempty unique subset of ledger
source IDs.  The firewall's allowed-source list is compared with the ledger
as an order-insensitive exact set.  Its forbidden-choice enum is also exact
and contains no placeholder.  The hard-row object must have length ten and
key set exactly `D00`--`D09`, with every value `PASS`; key order is immaterial.
The primary, non-importing independent, and integrated verifier refs must be
three distinct current `.py` paths under `codes/` with three distinct actual
hashes.

The positive fixture uses only extant repository scripts, the extant M2
manifest, and extant v1.1 run JSONs.  Every such reference is explicitly
`FIXTURE_ONLY_EXISTING_REPOSITORY_ARTIFACTS_NOT_FUTURE_CANDIDATE_EVIDENCE`.
Those files exercise syntax, path, hash, role, media-type and result-key
binding.  Their reuse does not assert that they contain a future physical
source law, compact action, state proof, response map, error proof, candidate
or prediction.  This avoids a circular stored self-hash: both engines compute
current hashes at fixture-construction time, and no script hash is embedded in
its own tracked source.

The positive fixture still uses six exact bounds `1/100`, whose sum is
`3/50 < 1/10`.  Its ten PASS rows remain syntax fixtures, not M2 evidence.  A
reordered-positive metamorphic reverses the substantive list, ledger, error
terms, hard-row insertion order and firewall lists and must still pass.  Each
engine also rejects 48 deterministic malformed rational, NUL/overlong/alias
path, placeholder and target-token, malformed-container, non-string extra-key,
and unhashable-scalar fuzz cases without raising an exception.  Integer,
`None`, and tuple extra dictionary keys are covered explicitly and produce
structured rejection.

The retained hostile suite plus the requested adversarial cases has 57 exact
names and codes.  The additive cases are
`map_only_payload_under_substantive_label`, `unknown_substantive_change`,
`duplicate_substantive_change`, `unbound_probe_hash`,
`probe_artifact_wrong_role`, `quadratic_contact_placeholder`,
`compact_action_placeholder`, `state_existence_ref_unbound`,
`response_map_ref_unbound`, `limit_order_placeholder`,
`limit_order_permuted`, `prediction_placeholder`,
`prediction_candidate_unbound`, `proof_ref_unbound`,
`error_evidence_reused`, `error_result_key_missing`,
`non_script_verifier`, `identical_verifier_hash`,
`integrated_ref_missing`, `duplicate_input_id`, `duplicate_source_id`,
`visible_validation_source`, `forbidden_source_id`,
`source_section_unbound`, `forbidden_choices_placeholder`, `decimal_ratio`,
`unreduced_ratio`, `whitespace_ratio`, `embedded_nul_artifact_path`,
`overlong_artifact_path`, `overlong_rational_literal`,
`trailing_dot_segment_artifact_path`,
`trailing_space_segment_artifact_path`, `case_changed_artifact_path`,
`free_semantic_placeholder`, `prediction_target_leakage`,
`scaling_window_holdout_leakage`, `control_map_r_of_t_target_leakage`,
`control_map_scaling_window_holdout_leakage`, and `denominator_one_ratio`.
Both rational-length and denominator-one cases must include the structured
code `NUMERIC_LITERAL_INVALID`.

The validation boundary has three separate layers:

1. **syntax and declared binding:** validated by the two staged engines;
2. **semantic physical correctness:** not validated by artifact existence or
   hashes, and still requires new physical content and proof; semantic truth,
   change-evidence equivalence, result-key fitness, script/run provenance
   equivalence, and source-class/used-for equivalence are not machine-proved;
   and
3. **external prospective freeze:** not supplied and not constructible from
   this repository fixture.

Accordingly, the schema validator cannot promote the 48-component internal
fingerprint into a common-estimand prediction and cannot close
`PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND`.

## 19. Formalized authority and no-overclaim boundary

During the initial four-file proof-first assembly, only the manifest, this
certificate, the primary verifier, and the non-importing independent verifier
changed.  At that historical staging checkpoint, `--staged` reported these
exact missing authorities:

1. `claims/GATES.md#PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY`;
2. `claims/GATES.md#PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA`;
3. `negative-results/registry.md#NG-2026-08-11-PRE-A-M2-LANE-Q-LINEAR-SOURCE-AUTOMATIC-PHYSICAL-STIFFNESS-RESPONSE`;
4. `RESULTS-LEDGER.md#R-168-v1.2`; and
5. `explorations/log.jsonl#EXP-000812`.

All five authorities are now registered. The schema child is formally closed
only in its syntactic and declared-binding scope; a passing synthetic validator
is not physical evidence. The existing
PA-M2-CI8-RS-DISPERSION-MAP-v1 object remains DESIGN_ONLY and NOT_CREATED.
In particular, D03, D05, D06, and D08 remain non-PASS for a source-only M2
extension, D07 still requires a real prospective holdout, and every
common-input, external-custodian, cryptographic-remote, admitted-map, parent
Round-1, physical Sector A, and Pre-A gate remains open.

## 20. Combined R-167 v2.1 / R-168 v1.2 gate-level checkpoint issuance

The historical proof-first sentence No intermediate v1.2 PDF is issued applied
only to the earlier four-file staging batch. It is superseded by this single
gate-level issuance; no per-lemma or intermediate PDF was issued.

- Source:
  claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-twentieth-moment-edge-cluster-and-m2-response-contract-checkpoint-260811-v1.0.tex.txt
  (raw SHA-256
  b5e21a1aa14492947fa2b0aa4a04d14e89bdc58dc862a77cb273a5905d3d5827).
- PDF:
  claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-twentieth-moment-edge-cluster-and-m2-response-contract-checkpoint-260811-v1.0.pdf
  (raw SHA-256
  a535317888cb712e06a15ef06aa9fef25b317d18830c69235cb798130987d4aa;
  13 pages).
- R-167 verification: primary 209/209, non-importing independent 138/138,
  integrated 251/251.
- R-168 verification: primary 340/340, non-importing independent 361/361,
  integrated 288/288.
- Extraction and render QA: pypdf 13/13 nonempty pages; pdfplumber 13/13
  nonempty pages; all 13 rendered pages visually reviewed with zero clipping,
  overlap, broken equations, unreadable identifiers, black glyphs, or
  malformed page transitions; build OVERFULL-HBOX 0.

The workflow issued one combined source/PDF pair only after the primary,
non-importing independent, integrated, formal-authority, generated-surface,
source-form, dual-extraction, and visual-review checks passed. This formally
issues and strictly verifies only the scoped R-167 v2.1 and R-168 v1.2
children. The physical-response, external-prospective-freeze, common-alpha,
many-edge rank-two/QPS, broken-sector GNS-gap, Round-1, C6, CP1, physical
Sector A, and Pre-A parents remain **OPEN**.

## 21. R-168 v1.3 additive scope

The additive exploration is `EXP-000814`. The five new children are T0,
`claim_bearing: false`, and are closed only in the exact statements below.
They do not change the retained physical-response gate or any Round-1, C6,
CP1, physical Sector-A, or Pre-A parent. The four additive negative IDs are:

1. `NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-WINDING-AND-HELICITY`;
2. `NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-SUPERFLUID-DENSITY`;
3. `NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-EXPONENT`; and
4. `NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-CONTROL`.

## 22. Real one-dimensional internal U(1) and raw-field topology

Let

\[
 \rho:U(1)\longrightarrow GL(1,\mathbb R)=\mathbb R^*
\]

be a continuous pointwise linear representation. Its image is compact and
connected, contains 1, and therefore lies in the positive component
`R_{>0}`. The logarithm sends the image to a compact additive subgroup of
`R`. A nonzero additive subgroup contains all integer multiples of one of its
nonzero elements and is unbounded. Hence the logarithmic image is `{0}` and
`rho` is trivial. The familiar `O(1)={-1,+1}` conclusion is a corollary, not
the theorem's full scope.

The raw real Sobolev configuration space `H^2(T^3;R)` is a topological vector
space and has the explicit contraction

\[
 C_s(\phi)=(1-s)\phi,\qquad 0\le s\le1.
\]

It therefore has no intrinsic winding sectors as a raw real-field target.
This statement does not cover a spatial translation phase of a patterned
state, an emergent complex or two-component amplitude, a defect-complement
configuration space, or an externally supplied compact field. Thus it does
not produce helicity or a physical superfluid response.

## 23. One-Q auxiliary curvature and the periodic-torus secant

Take `c>0`, `q>0`, a sign vector with $s_i\in\{-1,+1\}$, and the trial family

\[
 \phi(x)=A\cos((q s+a)\cdot x),\qquad
 S(a)=\sum_i(2s_iqa_i+a_i^2)^2.
\]

Its averaged trial density is

\[
 f(A,a)={A^2\over4}\{r+cS(a)\}+{3gA^4\over32}.
\]

On the ordered branch `g>0` and `r+cS(a)<0`, exact minimization over
`A^2` gives

\[
 A_*^2=-{4(r+cS(a))\over3g},\qquad
 f_{\min}(a)=-{(r+cS(a))^2\over6g}.
\]

Since every `s_i^2=1`, all mixed second derivatives vanish at zero and

\[
 \operatorname{Hess}_a f_{\min}(0)
 =-{8rcq^2\over3g}I_3.
\]

This continuous derivative is an auxiliary Bloch, supercell, or
thermodynamic curvature. At fixed periodic torus size define the fundamental
reciprocal step

\[
 h={2\pi\over L},\qquad q=m h,\quad m\in\mathbb N_{\ge1}.
\]

Only integer multiples of `h` are allowed shifts. At fixed amplitude `A_0`,
the central secant along a coordinate is

\[
 {f(A_0,h e_i)+f(A_0,-h e_i)-2f(A_0,0)\over h^2}
 ={cA_0^2\over2}(4q^2+h^2).
\]

The fixed-amplitude continuum curvature, finite-step excess, and relative
correction are respectively

\[
 2cA_0^2q^2,\qquad {cA_0^2h^2\over2},\qquad
 {h^2\over4q^2}={1\over4m^2}.
\]

The canonical upstream fixture is

```text
r=-3, c=2, q=5, g=7, h=1, m=q/h=5.
```

It derives, rather than inserts,

```text
A_*^2=-4r/(3g)=4/7,
continuum curvature=400/7,
finite-torus secant=404/7,
excess=4/7,
relative correction=1/100.
```

The independent verifier expands
`cos(theta)=(z+z^-1)/2` three times and obtains Laurent coefficients
`{-3:1/8,-1:3/8,1:3/8,3:1/8}`. Equivalently,

\[
 \cos^3\theta={3\cos\theta+\cos3\theta\over4}.
\]

Thus the cubic Euler equation generates a `3k harmonic` for `g*A != 0`.
The one-Q family is a variational trial and is not automatically an exact
Euler solution. Its auxiliary phason stiffness is not an internal-U(1)
helicity modulus or physical superfluid density.

## 24. Finite-regulator tensor response and contact nonidentifiability

For a finite-volume, finite-regulator norm-C2 family

\[
 H(A)=H_0-\sum_i A_iJ_i+{1\over2}\sum_{ij}A_iT_{ij}A_j,
 \qquad T_{ij}=T_{ji},
\]

the finite-beta free-energy Hessian is

\[
 \Upsilon^{(\beta)}_{ij}={1\over V}
 \left(\langle T_{ij}\rangle_\beta-
 \int_0^\beta\langle\delta J_i(-i\tau)\delta J_j\rangle_\beta\,d\tau\right).
\]

For an isolated simple ground state with positive gap, analytic perturbation
gives

\[
 \Upsilon^{(0)}_{ij}={1\over V}\left(
 \langle0|T_{ij}|0\rangle-2\operatorname{Re}\sum_{n>0}
 {\langle0|J_i|n\rangle\langle n|J_j|0\rangle\over E_n-E_0}
 \right).
\]

For any target-blind real symmetric matrix `D`, the replacement

\[
 T_{ij}\mapsto T_{ij}+VD_{ij}I
\]

leaves `H_0`, every `J_i`, and the zero-source state and spectrum fixed, while
shifting `Upsilon` by exactly `D`: `Upsilon+D`. Therefore even the full linear
probe tensor does not identify the physical response until the quadratic
contact/background convention is supplied. These are future finite-regulator
formulas, not a present Lane-Q compact action, winding law, ordered state, or
physical response.

## 25. Analytic response-map integer exponent transport

Assume a positive linear critical input

\[
 \kappa(\tau)=C\tau(1+o(1)),\qquad C>0,
\]

and an analytic response with `R(0)=0` and first nonzero Taylor order
`n>=1`:

\[
 R(\kappa)=b_n\kappa^n+O(\kappa^{n+1}),
 \qquad b_n>0,\quad n\in\mathbb N_{>0}.
\]

Then

\[
 R(\kappa(\tau))=b_nC^n\tau^n(1+o(1)).
\]

The transported exponent is the positive integer `n`. The unit exponent
requires `n=1`; a sufficient local-diffeomorphism hypothesis is
`R(0)=0` and `R'(0)>0` with `R` C1 (or analytic) through zero. Positive
one-sided local invertibility alone is insufficient: `x^2` is positive and
invertible on `[0,epsilon)`, while `x^3` is locally invertible through zero,
but their leading orders are two and three.

## 26. Six-stage adjacent-ratio relative log-slope transport

Fix `lambda>0`, `lambda!=1`, and both scales
`s in {tau,lambda*tau}`. Let exact and approximate stage outputs
`R_0(s),...,R_6(s)` and `Rhat_0(s),...,Rhat_6(s)` be strictly positive, with
`Rhat_0(s)=R_0(s)`. Define adjacent ratios

\[
 g_j(s)={R_j(s)\over R_{j-1}(s)},\qquad
 \widehat g_j(s)={\widehat R_j(s)\over\widehat R_{j-1}(s)}.
\]

Suppose each exact ratio has a load-bearing positive floor
`g_j(s)>=m_j(s)>0`, and

\[
 |\widehat g_j(s)-g_j(s)|\le\epsilon_j(s),\qquad
 \delta_j(s)={\epsilon_j(s)\over m_j(s)}<1.
\]

Then `|ghat_j/g_j-1|<=delta_j`; telescoping, rather than assumption, gives the
six-factor final ratio for `X(s)=R_6(s)` and `Xhat(s)=Rhat_6(s)`. Consequently

\[
 L=\prod_{j=1}^6{1-\delta_j(\lambda\tau)\over1+\delta_j(\tau)}
 \le {\widehat X(\lambda\tau)/\widehat X(\tau)
       \over X(\lambda\tau)/X(\tau)}
 \le
 U=\prod_{j=1}^6{1+\delta_j(\lambda\tau)\over1-\delta_j(\tau)}.
\]

With

\[
 \nu_\lambda(\tau)={\log(X(\lambda\tau)/X(\tau))\over\log\lambda}
\]

and the analogous `nuhat`,

\[
 |\widehat\nu_\lambda(\tau)-\nu_\lambda(\tau)|
 \le {\max\{-\log L,\log U\}\over|\log\lambda|}.
\]

Exponent transfer needs every `delta_j(tau)` and
`delta_j(lambda*tau)` to tend to zero. Six absolute errors alone do not give
this: `X(tau)=tau` and `Xhat(tau)=tau+epsilon` have a fixed absolute-error
bound, while the dyadic log slope of `Xhat` tends to zero and that of `X` is
one.

## 27. Proof-first staging and no-overclaim boundary

At this exact four-file stage, the verifier's `--staged --no-store` path must
report the following new formal authorities as missing while retaining every
v1.2 authority:

1. `claims/GATES.md#PA-M2-CI8-V0-REAL-SCALAR-INTERNAL-U1-TRIVIALITY-AND-NO-INTRINSIC-WINDING`;
2. `claims/GATES.md#PA-M2-CI8-ONE-Q-AUXILIARY-PHASON-CURVATURE-AND-FINITE-TORUS-SECANT`;
3. `claims/GATES.md#PA-M2-CI8-HELICITY-TENSOR-CONTACT-SHIFT-NONIDENTIFIABILITY`;
4. `claims/GATES.md#PA-M2-CI8-ANALYTIC-MAP-INTEGER-EXPONENT-TRANSPORT`;
5. `claims/GATES.md#PA-M2-CI8-SIX-STAGE-RELATIVE-LOG-SLOPE-ERROR-TRANSPORT`;
6. `claims/GATES.md#PA-M2-SUCCESSOR-SUBSTANTIVE-COMPACT-ACTION-BACKGROUND-PROBE-AND-WINDING-LAW`;
7. `claims/GATES.md#PA-M2-SUCCESSOR-ORDERED-STATE-PHYSICAL-MODE-AND-RESPONSE-LIMIT`;
8. `claims/GATES.md#PA-M2-SUCCESSOR-SIX-TERM-CRITICAL-ESTIMAND-ERROR-BUDGET`;
9. `negative-results/registry.md#NG-2026-08-11-PRE-A-M2-V0-ONE-REAL-SCALAR-AUTOMATIC-INTERNAL-U1-WINDING-AND-HELICITY`;
10. `negative-results/registry.md#NG-2026-08-11-PRE-A-M2-ONE-Q-PHASON-AUTOMATIC-PHYSICAL-SUPERFLUID-DENSITY`;
11. `negative-results/registry.md#NG-2026-08-11-PRE-A-M2-POSITIVE-LOCAL-INVERTIBILITY-AUTOMATIC-UNIT-EXPONENT`;
12. `negative-results/registry.md#NG-2026-08-11-PRE-A-M2-SIX-ABSOLUTE-ERRORS-AUTOMATIC-LOG-SLOPE-CONTROL`;
13. `RESULTS-LEDGER.md#R-168-v1.3`; and
14. `explorations/log.jsonl#EXP-000814`.

`v1_3_checkpoint_synthesis` is `DEFERRED`: source, PDF, hashes, and page count
are all null. This package creates no run JSON, formal ledger entry, generated
surface, integrated-verifier update, PDF, changelog event, commit, or tag.

The three successor gates remain open for, respectively: a substantive compact
action/background probe/winding law; an ordered-state physical-mode quotient
and response limit; and a six-term critical-estimand error budget whose
relative errors vanish in the required scaling limit. The current
`PA-M2-CI8-RS-DISPERSION-MAP-v1` remains DESIGN_ONLY and NOT_CREATED.
R-168 creates no tag. No cryptographic custodian-signature check, remote
verification, physical superfluid response, candidate, prediction, Round-1
closure, C6, CP1, physical Sector A or Pre-A conclusion follows.

## 28. V1.3 devil's-advocate review

The following review is load-bearing for the numerical and asymptotic
statements above.

1. **Sign and factor objection -- DISMISSED for the auxiliary theorem.** A
   sign error in `S(a)`, the amplitude minimization, or the central secant
   would change the Hessian or the `400/7` oracle. The primary engine
   differentiates all eight sign choices symbolically. The independent engine
   extracts the quadratic coefficient of
   `(2*s_i*q*a_i+a_i^2)^2`, differentiates the minimized polynomial, expands
   the Laurent cube, and derives the plus/minus secant before comparing with
   the oracles. Both obtain `-8*r*c*q^2/(3*g)`, the secant factor `1/2`, and
   Laurent coefficients `1/8,3/8,3/8,1/8`.

2. **Tensor sign and contact-convention objection -- VALID with mitigation.**
   This certificate defines `Upsilon=+V^-1 Hess_A F`. A susceptibility written
   with the opposite sign changes the displayed current-current sign. The
   theorem therefore freezes the positive free-energy-curvature convention,
   includes the contact `T_ij`, and claims only the invariant shift
   `Upsilon -> Upsilon+D`. It does not identify that tensor with a measured
   helium response.

3. **Units objection -- VALID with mitigation.** The quantities `q` and `h`
   both have inverse-length units; `m=q/h` and `h^2/(4q^2)` are dimensionless.
   The continuum curvature and secant share the units of `c*A_0^2*q^2`.
   No map from these auxiliary units to a physical helicity or superfluid
   density unit has been supplied, so the physical-response successor remains
   open.

4. **Finite-torus, amplitude, and limit-order objection -- VALID with
   mitigation.** Continuous `a` does not preserve a fixed periodic torus.
   Section 23 uses only reciprocal-lattice shifts there and explicitly keeps
   `A_0` fixed. Reoptimizing the amplitude defines a different finite-step
   observable. The continuous optimized Hessian is therefore labelled
   Bloch/supercell/thermodynamic auxiliary, not a fixed-torus response.

5. **Convergence objection -- UPHELD.** The identity
   `h^2/(4q^2)=1/(4m^2)` tends to zero as `m` grows, but this package proves no
   thermodynamic, regulator-removal, ordered-state, or physical-response limit.
   Likewise the six-stage exponent transfers only when every relative
   `delta_j` at both scales tends to zero. These missing limits remain in the
   three open successor gates.

6. **Hardcode-masking objection -- DISMISSED for the exact fixture.** The only
   fixture inputs are `r=-3,c=2,q=5,g=7,h=1`. Both engines derive
   `A_*^2=-4r/(3g)`, then the curvature, secant, excess, and relative correction.
   The strings `4/7`, `400/7`, `404/7`, `4/7`, and `1/100` are explicit test
   oracles, not pasted computational intermediates. The independent engine
   imports neither the primary module nor its result JSON.

7. **Limit-case objection -- DISMISSED or retained exactly as scoped.** For
   `r>=0` the zero-shear ordered branch condition fails, so no positive
   `A_*^2` conclusion is made. As `h->0` the algebraic secant excess vanishes,
   but the physical limit remains UPHELD as missing. For `0<lambda<1` the
   error bound uses `abs(log(lambda))`; `lambda=1` is excluded. As any
   `delta_j->1`, the denominator bound degenerates and exponent transport is
   not asserted. If `R'(0)=0`, the analytic order can be `n>1`; `x^2` and
   `x^3` are the hostile witnesses against automatic unit exponent.

8. **Physical-promotion objection -- UPHELD.** Nothing here supplies a compact
   action, background probe, winding law, selected ordered state, physical-mode
   quotient, response limit, six-term vanishing error budget, admitted map, or
   prospective freeze. Therefore no physical superfluid-density, Round-1,
   C6, CP1, physical Sector-A, or Pre-A closure follows.

External review is invited specifically on the Kubo sign convention, the
fixed-amplitude versus reoptimized finite-torus distinction, and the
load-bearing adjacent-ratio factorization.

## 29. Combined R-167 v2.2 / R-168 v1.3 gate-level checkpoint issuance

The historical proof-first sentence `No v1.3 PDF or run JSON is created` applies only to
the earlier four-file staging batch and is retained above as stage provenance.
It is superseded for the current result by this single gate-level issuance; no
per-lemma or intermediate PDF was issued.

- Source:
  claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-fifth-history-rank2-gap-and-m2-response-boundary-checkpoint-260811-v1.1.tex.txt
  (33097 bytes; raw SHA-256
  9eea5a425cef38c8741f40d000dc10ac46430598f62a1d55313748de35c277e3).
- PDF:
  claims/C6-SPACETIME-SIGNATURE/notes/pre-a-q3lock-fifth-history-rank2-gap-and-m2-response-boundary-checkpoint-260811-v1.1.pdf
  (415191 bytes; raw SHA-256
  5ae80a7c5dd3f724411ee1b95fbf4db330f85123a4c3058a72f71900af9fdbf7;
  11 pages; 129.247 seconds newer than the source).
- R-167 primary: 253/253; raw script SHA-256
  d9d65080f84c0408200ba64c81449263cfd87095d8bdf1620211bc6fab6d1058.
- R-167 non-importing independent: 154/154; raw script SHA-256
  74dc4a8758d204587963c4e41e720902fd0b66931c35024f7784adaaa09d0b38.
- R-167 integrated: 279/279; raw script SHA-256
  5985f84cdb427d1fb3b3ab8de49e025c0ef3b0767e4462879eaa77e5907ba1bc.
- R-168 primary: 423/423; raw script SHA-256
  69a9486b060c711679314806b302af85652c6d8317fccebba83578b5b2d397a9.
- R-168 non-importing independent: 446/446; raw script SHA-256
  6b100dd08e3daac385fc67fa5627f0c9f8c5d9ff8aa2a416d30018e72a033c26.
- R-168 integrated: 349/349; raw script SHA-256
  34af34a2bb45c50b68af0db88dfaf51004c3ab33d49c2c38464dd2fbed4f618e.
- Extraction and render QA: pypdf 11/11 nonempty pages; pdfplumber 11/11
  nonempty pages; 77/77 required tokens in each extraction; all 11 rendered
  pages were visually reviewed with zero clipping, overlap, broken equations,
  unreadable identifiers, black glyphs, or malformed page transitions; the
  one-pass MiKTeX build reported OVERFULL-HBOX 0.

The workflow issued one combined source/PDF pair only after the primary,
non-importing independent, integrated, formal-authority, generated-surface,
source-form, freshness, dual-extraction, and visual-review checks passed. This
issues only the scoped R-167 v2.2 and R-168 v1.3 children. The all-exhaustion
common-alpha, connected rank-two oscillator-elimination/QPS-norm and cutoff-
compatibility, retained broader rank-two, broken-sector GNS-gap, substantive
compact-action/background-probe/winding-law, ordered-state physical-mode and
response-limit, six-term critical-estimand error-budget, physical-response,
prospective-freeze, Round-1, C6, CP1, physical Sector A, and Pre-A parents
remain **OPEN**. No parent closure follows.

## 30. EXP-000866 generated-reader locator correction

The historical R-168 v1.3 integrated verifier exposed a generated-reader
contract defect after later append-only events moved `EXP-000814` outside the
bounded recent readers. The correction is verification-only: historical
identity is now checked against the complete changelog locator shards and the
complete negative locator. The full changelog locator and full negative locator
are the historical authorities, while `changelog/INDEX.md`, `negative-results/INDEX.md`
and `changelog/index.json.recent` are treated as bounded recent readers whose
contract is current count and window metadata only. The full locator checks
bind schema, shard range, byte count, SHA-256, unique ordinals and the complete
accepted-event count. Deleting the historical event or substituting an
unrelated identifier is an explicit rejected mutation.

This `EXP-000866` correction does not change any theorem, result scope, tier,
negative authority, gate status, candidate, prediction, freeze, C6, Round-1,
Sector-A or Pre-A conclusion. It records no new mathematical result and no
new negative. There is no theorem scope change. The corrected verifier is version
`1.3.1`; its historical
`R-168 integrated: 349/349` issuance pin above remains retained as the prior
checkpoint record, while the current generated-reader locator correction is
re-executed against the live 648-event tree. The integrated output
self-reference is normalized to an invocation placeholder only for stored/fresh
comparison; the live catalog still binds the actual output bytes and SHA.
