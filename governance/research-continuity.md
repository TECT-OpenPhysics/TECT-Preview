# Research continuity contract

**Version:** 1.0  
**Issued:** 2026-08-30  
**Scope:** long-running Pre-A and Sector-A main-proof research  
**Machine authority:** `strategy/main-proof-program-v1.json`  
**Validator:** `verification/scripts/check_research_continuity.py`

## 1. Purpose

This contract makes the research resumable from repository evidence rather
than chat history. It preserves the established stepwise forward proof methods
and the observation-first inverse lane as parallel, independently audited
programmes. Neither lane replaces the other, and neither may certify the other
by reusing the same fitted information.

This is not a redesign of the existing research methods. The Sector-A theorem
map, evidence-first charter, QFT bridge, Lane H/F/Q programme, A13 route reset,
and every issued claim/result/negative authority keep their existing content,
order, and scientific meaning. The phase labels below are only a continuity
overlay: they say which already-issued method is active, what inputs are still
missing, and where a later session resumes. If this overlay conflicts with an
underlying method authority, the underlying authority controls and the
overlay returns to `P0-R` for correction.

The durable objective is to recover and maintain one verified research
baseline, advance Pre-A candidate selection and the Sector-A theorem families
through explicit gates, and retain every reusable advance, failure, redesign,
and stopping condition needed by a later session.

`P0-R` below means *Research Phase 0*. It is unrelated to the P0 publication
tier and to the historical Stage 0 in `ROADMAP.md`.

## 2. Authority model

The continuity layer is a pointer and state layer. It never copies the full
claim, gate, result, negative-result, exploration, candidate, or observation
matrices.

- Claim status remains in `claims/*/status.json`.
- Gate definitions and history remain in `claims/GATES.md`.
- Reusable results remain in `RESULTS-LEDGER.md`.
- Failed routes remain in `negative-results/registry.md`.
- Route verdicts remain in the append-only `explorations/log.jsonl`.
- Live work remains in `todo/todo.json`.
- Transition history remains in `changelog/log.jsonl`.
- `management/INDEX.md` and other generated indexes are readers, not
  authorities.
- Immutable issued strategy records are hash-pinned by the machine programme.
  Mutable authorities are checked by semantic IDs and current schemas instead
  of whole-file hashes.
- Cross-project TECT-YM and YangMills material remains `reference_only` unless
  a separately governed import is approved. A stale snapshot cannot bear a
  TECT claim.

Chat is never a resume authority. A route decision that matters to another
researcher must be written through the existing ledgers before it is reported
as advanced, failed, parked, redesigned, or complete.

## 3. Scientific layers

Every checkpoint declares exactly which layer it addresses.

1. `L1_MATHEMATICAL_THEOREM`: a conclusion follows from pinned assumptions.
2. `L2_MODEL_CONSISTENCY`: state, dynamics, observables, projection,
   regulator, and limits form one model.
3. `L3_PHYSICAL_IDENTITY`: the model is identified with controlled QFT,
   Yang--Mills, gravity, or physical-sector structures.
4. `L4_EMPIRICAL_VALIDATION`: a frozen candidate predicts data not used in
   selection or tuning.

Passing one layer does not promote a result to a later layer. Finite,
conditional, auxiliary, model, continuum, physical, and empirical scopes are
recorded independently.

## 4. Parallel programme continuity overlay

The forward lane retains the established model-first route: freeze a candidate
and owner contract, prove fixed-scope results, obtain a common core and uniform
estimates, take ordered limits, establish physical identity, and only then make
an independent prediction.

The inverse lane starts from frozen observation anchors and effective
QFT/Yang--Mills/gravity targets. It admits a microscopic version only after the
complete `F_reg -> F_lim -> F_eff -> F_obs` map exists, and then tests
existence, quotient identifiability, stability, and prospective predictivity
separately. Non-identifiability produces a surviving equivalence class, never
an invented unique candidate.

The two lanes share the following resume checkpoints. These checkpoints do not
replace or rewrite either lane's proof method.

| Phase | Forward method | Inverse method | Exit character |
|---|---|---|---|
| `P0-R` | Recover Git, tools, authorities, tasks, gates, stopped loops, and one next action | Recover the same baseline and inverse-contract state | Clean, pushed, strict baseline and a durable resume point |
| `P1` | Freeze evidence roles, M0, candidates, and owner intake | Freeze source hashes, covariance, lineage, calibration, retrospective, and prospective roles | No target leakage; exact inputs and roles |
| `P2` | Admit functional, reference, state, generator or transfer, projection, regulator, normalization, finite parts, norm, and limit order | Admit every stage of the predictive map and its uncertainty | At least one version admitted, or an honest empty set/equivalence class |
| `P3` | Use the Sector-A family map for exact fixed-scope theorems with primary, independent, hostile, and Lean dispositions | Test existence of a map-compatible candidate | Finite/model result only; explicit assumptions and non-claims |
| `P4` | Prove common core, one-use control, uniform estimates, and ordered cutoff/volume/exhaustion/phase/beta limits | Test regulator and observation-error stability | Uniform or ordered-limit gate, not a table extrapolation |
| `P5` | Establish physical-empty comparison, OS/QFT reconstruction, gauge/gravity correspondence, and physical sector | Test quotient identifiability against the effective target | Controlled physical identity, or a declared equivalence class |
| `P6` | Freeze the selected version, map, scorer, and prediction before disclosure | Evaluate a genuinely unused prospective holdout against M0 | Predictivity without retuning |
| `P7` | Audit dependencies, assumptions, hostile objections, and release evidence | Audit leakage, equivalence, stability, and holdout provenance | One gate-level synthesis note/PDF and an explicit next cycle or tier action |

The Sector-A five-family theorem map, the Pre-A evidence-first charter, the
QFT bridge order, the Lane H/F/Q programme, the A13 route reset, and the
observation-first inverse contract remain the detailed method authorities.
This contract supplies their persistent orchestration only.

## 5. Synchronization gates

`X1_NO_CIRCULARITY_COMPATIBILITY` compares the two lanes only after their input
lineages are known. Agreement is compatibility evidence, not mutual proof.

`X2_GATE_SYNTHESIS` permits one synthesis note and PDF only at a logical gate
checkpoint. Intermediate lemmas remain in manifests, runs, and the exploration
ledger.

`X3_CLAIM_ACTION` permits a claim or tier action only after the applicable
scientific gate, hostile review, regeneration, release check, and independent
evidence requirements close. A programme-phase transition alone is never a
scientific tier transition.

## 6. Checkpoint contract

Every material checkpoint records:

- programme version, lane, phase, candidate version, exact question, and exact
  scope;
- functional or action, generator or transfer, state, projection, and the
  physical and proof owners;
- assumptions and missing assumptions;
- regulator, volume, boundary condition, reference, normalization, finite
  parts, common norm, and limit order;
- evidence layer `L1`--`L4`, limit scope `FINITE`, `UNIFORM`, or
  `ORDERED_LIMIT`, physical scope `AUXILIARY`, `MODEL`, or `IDENTIFIED`, and
  data role `THEORY`, `CALIBRATION`, `RETROSPECTIVE`, or `PROSPECTIVE`;
- reproduction commands, artefacts, hashes, and primary, independent, hostile,
  and Lean dispositions;
- acceptance condition, falsifier, stop or redesign condition, allowed claims,
  and non-claims;
- exploration, result, negative, event, task, gate, and claim pointers when
  applicable;
- the next action and the exact condition under which another session resumes.

Missing fields remain `MISSING` or `NOT_ADMITTED`; they are not inferred from
nearby evidence.

## 7. State machine and loop control

The allowed stage states are `UNSTARTED`, `READY`, `ACTIVE`, `CHECKPOINTED`,
`BLOCKED`, `PARKED`, `REDESIGN_REQUIRED`, and `COMPLETE`. The ordinary path is
`UNSTARTED -> READY -> ACTIVE -> CHECKPOINTED -> COMPLETE`. A blocked stage may
return to `ACTIVE` only after a new input and a new exploration record. A
redesigned stage may return only with a new candidate, version, or assumption
contract.

At most one phase is `ACTIVE` in each lane. A successor cannot be complete
while its predecessor is open. During shared `P0-R`, both lanes point to that
same active recovery phase.

Every blocker has a stable fingerprint and a reopen condition. Repeating an
identical blocker without a new hash-pinned input is forbidden: the route is
`PARKED`, not reported as another `BLOCKED` result. In particular:

- physical-empty tests stay parked until one same-owner common functional and
  an admitted empty branch `E` exist;
- A13 local-coordinate variants stay parked until Pre-A selects M1 and a
  complete owner packet exists;
- Q3LOCK finite-table variants stay parked unless they attack a named common-
  core, history-transfer, or uniform theorem or provide a new falsifier;
- static Gibbs agreement cannot select heat or mobility dynamics;
- generic source searches are not repeated without a new owner artefact hash;
- no A14 claim is created for a subproof, reduction, obstruction, or route
  comparison under an existing Sector-A host.

## 8. Research Phase 0 recovery

A release-check pass proves that the current public surface is internally
consistent. It does not prove that pending work has been committed, pushed, or
made durable.

`P0-R` begins by recording the local `HEAD`, branch, upstream-tracking ref,
ahead/behind relation, dirty-path counts, commit-queue count, scientific
authority counts, doctor status, release status, and whether the live remote
was actually queried. This is a dated recovery-start snapshot, not a permanent
claim about the repository.

`P0-R` closes only after:

1. doctor and release checks pass;
2. generated surfaces and both diff checks pass;
3. the commit queue is empty and the working tree is clean;
4. local `HEAD` equals the live configured remote branch head;
5. current claim, gate, result, negative, exploration, event, and task counts
   are recorded in the completion checkpoint;
6. lane tasks, gates, immutable pointer hashes, and mutable semantic IDs pass
   the continuity validator; and
7. the next forward and inverse actions are explicit.

Clean-tree, queue, and remote equality are enforced only by
`check_research_continuity.py --strict-baseline` after watcher drain and push.
They are deliberately excluded from the ordinary release gate, which must run
on a dirty pre-commit tree without deadlocking the watcher.

## 9. Resume algorithm

Every resumed main-proof session follows this order:

1. capture the UTC date and run `doctor.py`;
2. run the ordinary continuity validator;
3. read `management/INDEX.md`, live tasks, and gate IDs;
4. load `strategy/main-proof-program-v1.json` and the latest referenced
   exploration checkpoint;
5. verify immutable hashes and mutable semantic IDs;
6. if any pointer, task, gate, phase, or generated surface drifts, return to
   `P0-R` before new proof work;
7. select the one active stage in each lane, freeze scope, acceptance,
   falsifier, and stop condition, then work;
8. record a reusable route verdict and any warranted result or negative record;
9. regenerate, release-check, queue, commit, push, and run the strict baseline
   audit at a logical checkpoint.

The machine programme's current checkpoint and next action take precedence over
stale narrative paragraphs in `ROADMAP.md`, old task notes, or an old theorem-
map frontier summary. Those sources remain historical authorities for their
issued content.

## 10. Hostile review requirements

The validator and human review must reject at least these defects:

- missing or mutated immutable pointer;
- copied aggregate matrix rather than a locator;
- two active phases in one lane or an illegal transition;
- a complete successor with an open predecessor;
- finite or conditional evidence promoted to continuum or physical identity;
- retrospective data labelled prospective;
- inverse PASS with a missing forward-map stage;
- proof-owner tuning after holdout disclosure;
- circular forward/inverse evidence reuse;
- `reference_only` external evidence promoted to a TECT claim;
- a repeated blocker without a new input;
- a strict P0-R pass while the tree is dirty, the queue is nonempty, or the
  live remote differs;
- a material exact result with no independent, hostile, or Lean disposition;
- missing non-claims or missing next action.

## 11. Current scientific boundary

This continuity programme proves no Pre-A origin statement, physical vacuum,
Reading-H physical-empty sign, C6, full Sector A, QFT/Yang--Mills/gravity
identity, physical mass gap, or theory of everything. At issue time the forward
lane lacks an admitted owner-complete microscopic dynamics/map, and the inverse
lane has pending source hashes, an empty prospective lock, and zero admitted
microscopic forward maps. The programme records how to improve those facts
without concealing them.
