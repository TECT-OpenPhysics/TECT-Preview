# R-168 v1.2 certificate: prospective holdout protocol, linear-probe nonidentifiability, and minimum response contract

- **Explorations retained:** `EXP-000807`; validator hardening correction `EXP-000808`; map/fingerprint extension `EXP-000810`
- **Additive exploration:** `EXP-000812`
- **Result:** `R-168`, version `v1.2`
- **Stable result ID:** `PA-ROUND1-PROSPECTIVE-HOLDOUT-FREEZE-PROTOCOL-AND-CURRENT-TREE-READINESS-AUDIT`
- **Claim context:** `C6-SPACETIME-SIGNATURE`
- **Task:** `T-054`
- **Tier:** `T0`, `claim_bearing: false`
- **Date:** 2026-08-11

R-168 v1.2 is cumulative: sections 1--8 retain the v1.0 protocol and audit, sections 9--15 retain the v1.1 current-version map audit, M2 fingerprint, and combined checkpoint, and sections 16--19 add the exact fixed-linear-probe curvature theorem and a hardened minimum physical-response successor schema whose formal authority is now registered in its exact syntactic and declared-binding scope. It does not issue a candidate, prediction, target, or freeze.  The retained v1.0 layer closes the protocol layer
needed before a future blind Pre-A holdout can be issued and audits the exact
registered state at commit `99157442831c0e44d425b5d5f8cd78856c57da53`.
At that checkpoint there are no official freeze records, no admitted
microscopic survivors, and no admitted M1, M2 or M5
microscopic-map/prediction pair.  The parent prospective-evidence gate
therefore remains open.  The initially observed local `freeze/*` tag count is
reported separately as a non-load-bearing live observation, not as an
audited-commit fact or a historical PASS condition.

The current cumulative closed-subgate set, after the staged authorities were registered, is exactly:

1. `PA-ROUND1-COMMON-ESTIMAND-AND-CANDIDATE-MAP-SCHEMA`;
2. `PA-ROUND1-PROSPECTIVE-FREEZE-PROVENANCE-PROTOCOL`;
3. `PA-ROUND1-TARGET-INDEPENDENCE-AND-ANTI-LEAKAGE-SCHEMA-VALIDATOR`;
4. `PA-ROUND1-CURRENT-CANDIDATE-MAP-ADMISSION-EMPTY-SET-AUDIT`;
5. `PA-ROUND1-CURRENT-VERSION-M1-M2-M5-MAP-ONLY-ADMISSION-EMPTY-SET`;
6. `PA-M2-CI8-FINITE-TORUS-GAUSSIAN-DISPERSION-FINGERPRINT`;
7. `PA-M2-CI8-LINEAR-PROBE-SECOND-ORDER-RESPONSE-NONIDENTIFIABILITY`; and
8. `PA-M2-CI8-PHYSICAL-RESPONSE-SUCCESSOR-MINIMUM-CONTRACT-SCHEMA`.

The following gates remain open:

- `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`;
- `PA-ROUND1-PER-PARAMETER-COMMON-INPUT-LEDGER`;
- `PA-ROUND1-INDEPENDENT-CUSTODIAN-OPAQUE-TARGET-COMMITMENT`;
- `PA-ROUND1-ADMISSIBLE-MICROSCOPIC-CANDIDATE-MAP-AND-FROZEN-PREDICTION`;
- `PA-ROUND1-CRYPTOGRAPHIC-CUSTODIAN-SIGNATURE-AND-REMOTE-FREEZE-VERIFICATION`; and
- `PA-M2-CI8-PHYSICAL-RESPONSE-CHANNEL-AND-ERROR-BOUND`.

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
