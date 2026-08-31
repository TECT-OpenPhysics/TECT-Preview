# Mainline direction-control contract

**Version:** 1.1
**Issued:** 2026-08-31
**Scope:** long-running TECT Pre-A and Sector-A proof work
**Machine authority:** `strategy/mainline-direction-control-v1.json`
**Validator:** `verification/scripts/check_direction_control.py`

## 1. Purpose

The repository already preserves claims, results, failures, sources, and next
actions. Preservation alone does not prevent a useful auxiliary line from
displacing the active proof obligation. This contract adds a routing layer that
counts progress by scope, not by file count or the number of finite runs.

This is a work-control policy. It does not replace the Sector-A theorem map,
the Pre-A forward or inverse methods, the QFT bridge, or any claim authority.
It never changes a claim tier, closes a scientific gate, or identifies a
physical theory automatically.

## 2. Active proof obligations

The primary TECT mainline is the forward T-054 obligation:

- task: `T-054`
- gate: `PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE`
- required scope strengthening: a source-owned microscopic dynamics owner,
  compatibility on a common core, and a cutoff/volume/lattice-uniform
  estimate.

The observation-first inverse tasks T-059 and T-061 remain protected parallel
work. They may proceed without replacing T-054, but their input-admission
status is not a physical identification or a Pre-A proof.

T-055, T-057, finite sidecars, and reference-only cross-project calculations
are auxiliary relative to the active forward gate unless a control record shows
that they strengthen the declared mainline scope or fire a named falsifier.

## 3. Result classification

Every post-baseline control record has exactly one classification:

| Classification | Meaning | Mainline count |
|---|---|---:|
| `MAINLINE_ADVANCE` | removes a named assumption, strengthens the declared scope, or changes the active gate with new evidence | yes |
| `AUXILIARY_SUPPORT` | reusable finite, conditional, provenance, or parallel-lane support that does not strengthen the active mainline scope | no |
| `NEGATIVE_RESULT` | a reproducible failure or falsifier; it counts as mainline-relevant only when it changes the active route or closes a named branch | record field decides |
| `NO_PROGRESS` | adds examples, sizes, or parameters without strengthening scope, changing a gate, or adding a new falsifier | no |

The classification is relative to the active mainline. An inverse-lane result
can be scientifically useful while still being `AUXILIARY_SUPPORT` for the
forward T-054 gate.

## 4. Threshold routing and deliberative review

The validator derives the current route from the append-only control ledger.
The thresholds are deliberately conservative triggers for a review, not
automatic scientific stop commands. A hard proof problem can therefore earn a
bounded additional attempt when the researcher states what new evidence could
change the diagnosis and when that attempt must be reconsidered.

1. Two consecutive auxiliary or no-progress records stop auxiliary expansion
   **only long enough to require a review**. The review may authorize a bounded
   continuation, return to the active mainline, require a redesign, or park the
   route.
2. Three checkpoints without an active-gate change require an explicit
   review and a mainline re-entry decision, even if finite results were
   recorded.
3. Two consecutive records with the same blocker fingerprint require a review
   of the counterexample or redesigned-route evidence target.
4. Three consecutive records with the same blocker fingerprint require a
   review before any further attempt; repeating it without a new hash-pinned
   input and an explicit review condition is forbidden.
5. A positive promotion order is always
   `source-compatible -> uniform -> physical-sector -> limit`.

The machine route at each threshold is `REVIEW_REQUIRED`. The validator does
not silently mutate task, claim, or gate status. The next ledger record must be
a `record_type: review` entry containing:

- the exact review question and the basis for the review;
- a hash-pinned or explicitly named new evidence target;
- the continuation condition and the revisit condition;
- a finite `review_budget`; and
- one decision: `CONTINUE_BOUNDED`, `RETURN_TO_MAINLINE`, `REDESIGN`, or
  `PARK_OR_BLOCK`.

`CONTINUE_BOUNDED` authorizes only that finite number of subsequent auxiliary
or parallel attempts. When the budget is exhausted, or another threshold is
reached, the route is `REVIEW_REQUIRED` again and a new review record is
needed. A mainline advance or a relevant falsifier can end the active review
early. `RETURN_TO_MAINLINE`, `REDESIGN`, and `PARK_OR_BLOCK` are explicit
review outcomes rather than automatic conclusions.

Starting a review establishes a new bounded accounting window: the auxiliary,
no-progress, repeated-blocker, and no-gate-change counters are reset for the
declared target. This reset is a control-layer rebase, not evidence that the
underlying scientific gate improved.

Thus the control loop is:

```text
threshold -> REVIEW_REQUIRED -> review question/evidence/conditions
          -> bounded continuation or explicit route change
          -> next review point -> repeat the assessment
```

A new research-admission record may be added autonomously when its provenance,
scope, evidence grade, falsifier, next action, and (when required) review
fields are complete. This is permission to investigate, not a scientific
approval.

### 4.1 Adversarial review of the control layer

The review mechanism itself is subject to hostile checks before release:

- **Premature-stop objection:** a threshold might still silently terminate a
  hard route. **Disposition:** the validator accepts only `REVIEW_REQUIRED`
  at automatic thresholds; continuation requires an explicit review record.
- **Unbounded-loop objection:** a review could become permission to repeat the
  same finite calculation indefinitely. **Disposition:**
  `CONTINUE_BOUNDED` has a finite budget, and budget exhaustion or a later
  threshold requires another review.
- **Evidence-free-renaming objection:** a route could be called a redesign
  without changing its input or target. **Disposition:** redesign/park reviews
  require a changed blocker, a new input hash, or mainline evidence before the
  same blocker can be attempted again.
- **Scientific-promotion objection:** a control decision could be mistaken for
  a theorem or physical result. **Disposition:** all review records are
  `claim_bearing:false` control data with `scientific_transition:false`; claim,
  tier, gate, physical, QFT, and Yang--Mills transitions remain separately
  authorized.

## 5. Self-resolution and approval boundary

The proof lane may resolve bounded in-scope choices without waiting for a user
reply. It may collect an existing canonical source, build a clearly labelled
test fixture, run a reproducible check, and admit the resulting research step.

If a source-owned physical input is absent, the lane must record
`NOT_ADMITTED`, `EMPTY_OWNER_ARTIFACT`, or `TEST_ONLY`; it must not invent the
input or relabel a synthetic fixture as physical evidence. Automatic approval
therefore means *permission to continue bounded research*, never approval of a
theorem premise, continuum limit, QFT/Yang--Mills identity, physical sector,
or empirical prediction.

Claim, tier, and scientific-gate transitions remain operator-authorized under
`SESSION.md` and `GOVERNANCE.md`. This separation allows autonomous progress
without weakening the evidence firewall.

## 6. Required record and session use

The machine manifest and ledger are pointer-only. They do not copy claim,
result, negative-result, observation, or cross-project matrices. Each decision
record points to the existing result/event/negative authority and includes the
active gate, lane, provenance hash (or `NONE`), scope-change flags, blocker
fingerprint, research-admission flag, route decision, and next action.

At session entry, run:

```text
python verification/scripts/check_direction_control.py
```

After a material route decision, append one record with:

```text
python verification/scripts/check_direction_control.py --add --file <record.json>
```

When the reported route is `REVIEW_REQUIRED`, the next record must use
`record_type: review` and the required review fields in the machine manifest.
The append-only ledger keeps the review decision beside the result that
triggered it, so a later session can resume at the declared evidence target
without treating an old finite attempt as a new proof premise.

The ordinary doctor and release gates run the validator automatically. A
control PASS is not a proof PASS; it means only that the routing state is
internally consistent and the next action is mechanically determined.
