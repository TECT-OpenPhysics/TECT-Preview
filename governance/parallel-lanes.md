# Parallel lanes and the integration controller

Binding operational policy, 2026-09-07. This implements AGENTS.md; it grants
no scientific promotion. Applies to current and future proof, paper, review,
and tooling lanes. `verification/scripts/lane_control.py` is the controller.

## Isolation and ownership

The canonical TECT checkout is the integration workspace. Each writing task
registers its task ID, repository, role and workspace before writing. Same-repo
writers use separate Git worktrees and `codex/lane-<id>` branches. Independently
governed repositories (including TECT-YM) retain their own checkout, checks,
commit history and push target. A thread's displayed project is not permission
to write that project's canonical checkout when its registered workspace differs.
The controller refuses duplicate writer workspaces and nested workspaces across
different repositories. Read-only consumers pin source commit and file hashes.

Run the controller from the canonical checkout with `--root <canonical-path>`
from other workspaces. Its runtime registry, immutable checkpoint requests,
status, blockers and locks live in gitignored `internal/lane-control/`.
These are operational records, never scientific evidence. Loss of runtime state
requires re-registration and reconciliation with Git and actual task states;
never infer that a lost receipt means a checkpoint was integrated.

New lanes use exactly the same registration/provision/submit procedure. The
recurring controller discovers new tasks in this project, verifies their actual
purpose and repository, and registers writers; ambiguous or read-only tasks are
not silently turned into proof workers. Registering a lane does not create a
new research objective, launch a new task or spend an unapproved proof budget.

## Continuous work and immutable checkpoints

1. Work and run source-local tests in the lane workspace. All original evidence,
   exact-byte, append-only, PDF and claim-scope rules still apply there.
2. At a logical checkpoint use the existing release-gated commit procedure.
   Lane branches make local checkpoint commits; only the integrator pushes the
   configured canonical branch. Independent repositories keep their own policy.
3. Submit a fixed base and commit with `submit`. Working edits may continue after
   submission: integration always reads that fixed commit, never a moving HEAD
   or another worker's index. At most one pending checkpoint per lane provides
   backpressure without stopping that lane's research.
4. `prepare` creates a detached validation worktree from the submitted commit
   when its base equals the current canonical HEAD. Checks and PDF work happen
   there, without requiring quiet in every source worktree. An obsolete base
   requests a bounded rebase/replay review for that submission only. Replay
   append-only records with fresh IDs using their authoritative append tools;
   do not merge generated catalogs, renumber published records or overwrite
   source hashes. Regenerate derived surfaces after the authoritative replay.
5. The integration owner verifies the release gate, PDF/render disposition,
   scope, exact submitted HEAD, and clean canonical index, then fast-forwards
   the canonical branch to that HEAD. A canonical change during checks requires
   revalidation against the new base. Push only its configured branch target,
   without force, and verify remote HEAD. Record a receipt only after actual
   promotion, and record push failure separately; local success is not backup.

Never stage another worktree's files. No worktree deletion, pruning, branch
deletion, force pushes, automatic stash/reset, or abandoned lock stealing.
Old snapshots remain recoverable and are reviewed for retention at checkpoints.
Disk pressure pauses new provisioning, not deletion of research.

## One recurring controller, arbitrary lanes

One Codex heartbeat on the coordinating task runs every 30 minutes. Each pass
reads this policy and `tick`, then checks live task status before dispatching.
It handles one integration at a time, oldest eligible request first, skipping
requests that need review. Different repositories need no global release lock.
The commit watcher has an OS-held per-worktree lock; it fails rather than
staging/committing after a source snapshot changed during validation.

Use `dispatching` before sending a task message and `sent` after delivery;
an ambiguous delivery stays `dispatching` until read-back reconciliation. This
prevents a network retry from starting the same task twice. Do not repeatedly
message busy workers or wake completed goals. A controller turn that finds no
actionable change performs no proof runs, PDF builds, catalog generation or
commit. Report meaningful changes, failures and needed decisions only.

Blockers register exact input paths and hashes plus a UTC review time. An input
change or the deadline produces REVIEW_REQUIRED, not scientific success or an
automatic stop. The owner states the next evidence target, continuation limits,
revisit condition and budget before bounded continuation. Repeated unchanged
failure must cause this review, not infinite automatic retries. Existing
direction-control records and explicit research holds remain authoritative.

The heartbeat is a scheduler for safe coordination, not a 24/7 uptime guarantee:
it depends on the host, app, permissions and usage availability. A source lane
can compute continuously; only its brief checkpoint commit must serialize its
own writes. Mathematical conflicts need a scoped owner review. Isolation avoids
shared-index races; it cannot automatically resolve contradictory mathematics.

## Commands

`python verification/scripts/lane_control.py register --lane <slug> --thread <id>
--role proof --repo <path>` registers a same-repo writer for provisioning.
Add `--workspace <path> --external` only for an independently governed repo.
`provision --lane <slug>` creates an isolated worktree at a pinned committed base.
`submit --lane <slug> --head <commit>` submits that fixed checkpoint.
`tick` writes a compact operational status and pending actions.
`prepare --request <id>` makes a detached validation snapshot.
`promote --request <id>` runs release and strict PDF checks in that snapshot,
rechecks both HEADs and clean trees, and fast-forwards under the release lock.
Push/remote verification is the coordinating task's next explicit operation.
After bounded owner replay on a fresh base, `resubmit --request <old-id>
--head <replacement-commit>` preserves the original request and marks it
superseded, without reporting integration. Never rebase a busy worker's index;
replay a fixed checkpoint in another worktree or coordinate its local checkpoint.
`block --lane <slug> --key <slug> --input <path> --review-at <UTC-ISO>
--reason <text>` registers a dependency review. Repeat `--input` as needed.
`review --key <lane:key> --review-at <UTC-ISO> --reason <evidence-and-budget>`
acknowledges review and pins the next input snapshot.
`ack --action <id> --state dispatching|sent --note <text>` records delivery.
`receipt --request <id>` verifies ancestry before marking a checkpoint integrated.
`python -m unittest discover -s verification/tests -p test_lane_control.py`
reproduces the tooling regression suite.

## Adversarial operational review

- Continuous dirty source: submission pins a commit, not filesystem contents;
  a detached validation worktree cannot observe later source edits. Scope is
  tooling isolation, not analytic verification.
- Failed or outdated submission: request-specific review, not a global queue
  stop. No automatic conflict resolution on append-only evidence.
- Concurrent controllers or watcher: OS-held locks release on process exit;
  a busy owner is not declared dead solely because a timeout elapsed.
- Duplicate messages and restart: deterministic action IDs, durable dispatch
  receipts and reconciliation of uncertain deliveries. Status timestamps are
  excluded from identity so routine polling does not create new work.
- New lanes: registration validates repository/workspace identity; role names
  do not silently grant claim promotion, external publication or goal creation.

Independent operational review is invited, especially of crash recovery,
checkout identity and concurrent checkpoint submission.

Checkout timestamps are not new PDF content: provisioning/validation may restore
PDF freshness only when BOTH source and PDF bytes exactly match an already fresh
pair in the source or canonical workspace. This changes filesystem timestamps
only. Changed/missing/stale pairs still require the original checkpoint checks.

Historical references to ignored `tmp/` evidence are preserved byte-for-byte in
`archive/portable-evidence/`, pinned by `verification/portable-evidence.json`.
Admission, provisioning and validation restore only missing targets, verify
SHA-256, and refuse any differing existing target. `doctor.py --fix` performs
the same bootstrap on an independently copied workspace. Historical exploration
records and their expected hashes are never rewritten to hide missing evidence.

Publication checks enumerate the Git-visible release surface. In particular,
the path-length check uses the same inventory as release_check, so an ignored
isolated checkout cannot cause a false central path-length failure. Public
tracked/new files retain the original path budget.
