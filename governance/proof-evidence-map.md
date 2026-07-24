# Proof evidence map policy

**Binding from:** 2026-07-23. The proof evidence map is the global navigation
and audit surface for the complete TECT development record. It exists to make
successful advances, proof-route explorations, failed routes, reasons for
failure, current gates, and reproduction anchors visible together without
creating a second truth store.

## 1. Generated surfaces

- `theory/proof-evidence-map.md` is the human one-glance roadmap.
- `verification/proof-evidence-map.json` is the complete machine projection.
- `verification/scripts/build_proof_evidence_map.py` generates and checks both.

The Markdown and JSON are generated files and must never be hand-edited.

## 2. Authority boundary

The map may summarize and link, but it may not change a claim, tier, lifecycle,
gate, verdict, reproduction contract, or proof boundary. Authority remains:

1. `claims/<ID>/status.json` and `claim.md` for current claim state;
2. proof notes, PDFs, manifests, and run JSON for proof evidence;
3. `claims/GATES.md` for gate/hypothesis definitions and registered status;
4. `todo/todo.json` for current work order and blockers;
5. `RESULTS-LEDGER.md` for accepted reusable results;
6. `negative-results/registry.md` for failed, retracted, and audit routes;
7. `explorations/log.jsonl` for non-tier-bearing route assessments;
8. `changelog/log.jsonl` for accepted chronology;
9. `CATALOG.md` / `verification/catalog.json` for file inventory and hashes.

If map prose conflicts with an authority, the authority wins and the generated
map is stale or defective.

## 3. Coverage contract

Every real claim status card (excluding scaffolds), reusable-result index/detail
pair, negative-result index/detail pair, proof-exploration record, accepted
changelog event, task, and current claim-card/live-task route gate is projected.
Per-claim lineage-note,
legacy unordered root-note, PDF, run-JSON, claim-level manifest, top-level
bundle manifest, and frozen embedded-manifest paths are inventoried in disjoint
classes. The generated `LINEAGE.md` remains the ordered drill-down.
The registry's pre-schema process-grade lessons are separately projected as
legacy unnumbered lessons rather than silently omitted or assigned invented
identifiers.

The generator fails rather than silently omit data when it encounters:

- duplicate identifiers;
- a result or negative entry whose index and detail sections do not match;
- a negative entry lacking `Failure mode`, `Evidence`, or `Consequence`;
- a malformed, rewritten, noncanonical, or unresolved proof-exploration record;
- an invalid task status, unknown task claim, unresolved `T-NNN` blocker, or
  undefined gate target on a live task;
- an unknown hard/soft dependency;
- an undefined currently open gate or named hypothesis;
- an `AVAILABLE` reproduction without both command and expected output;
- an unresolved or duplicate graph edge;
- a proof note first issued on or after 2026-07-24 that lacks any of the
  eleven mandatory result-footer labels in `governance/claim-standard.md`, or
  an incomplete note whose issuance date cannot be parsed from version metadata
  or its dated filename;
- stale Markdown or JSON output.

Older incomplete footers and missing historical/superseded sibling PDFs are
grandfathered as visible coverage diagnostics rather than rewritten or hidden.
Footer enforcement covers both ordered lineage notes and legacy-style root
notes, so placing a new note outside `notes/` cannot bypass the gate.
Likewise, a claim card that still lists a gate whose registered status begins
`CLOSED` is reported as reconciliation debt; the map never flips the card.

## 4. Honest labels and graph rules

`R-NNN` means an accepted reusable result, not necessarily a positive theorem.
It may be a no-go lemma, reduction, partial advance, or conditional
consolidation. Negative records retain distinct kinds: retraction, fired
falsifier, no-go, and audit.

Graph node identifiers are namespaced (`claim:`, `result:`, `negative:`,
`exploration:`, `event:`, `gate:`, `task:`). Exact claim references are preferred. A short
family reference such as `A13` is attached only when it occurs in a structured
host field and that family has exactly one real claim card. Result ownership is
derived only from `Proven in`; chronology uses only explicit known
`claim_ids`; negative/audit ownership uses structured fields and explicit
negative-event links. Free-form fixture tokens never create claim edges, every
inference basis is recorded, and ambiguous references remain unbound. The
generator never invents a proof-successor or route-replacement edge from prose.
Exploration edges come only from its structured claim/task/gate/formal/related
fields; `advanced` never becomes a proof edge and `failed` never becomes a
formal no-go edge without an explicit registry reference. Current route order
comes from TODO and registered gate ownership.

A completed task may preserve a retired gate identifier that no longer has a
current `claims/GATES.md` definition. Such a node is explicitly typed
`historical_gate_reference` and anchored to `todo/todo.json`; a live task may
never use that fallback.

Source hashes normalize CRLF/LF before hashing. Manifest discovery uses
case-normalized names and explicit bundle-path classification, so Windows and
Linux generate byte-identical projections from the same tracked content.

## 5. Update workflow

Normal claim, result, failure, exploration, changelog, gate, or TODO updates require no
separate map edit. Regenerate all derived surfaces:

```bash
python verification/scripts/regen_all.py
```

Direct checks are:

```bash
python verification/scripts/build_proof_evidence_map.py --self-test
python verification/scripts/build_proof_evidence_map.py --check
python verification/scripts/exploration.py verify
```

The map check is registered once in `verification/scripts/gates.py`; therefore
`doctor.py`, `release_check.py`, and the commit watcher enforce freshness.
`build_catalog.py` remains last so it inventories the generated map.

## 6. Research and review use

Start with the current proof-route graph and live-task table, then open only the
linked claim, failure, result, gate, or lineage needed for the question. For
token-efficient AI work, search by identifier rather than loading the complete
map:

```bash
rg -n "A13|R-068|SCHUR-JACOBI" theory/proof-evidence-map.md
```

This preserves the full record while minimizing repeated context loading.

## 7. History

- 2026-07-24: v1.1 added complete append-only proof-exploration projection,
  structured graph edges, and the exploration-integrity prerequisite.
- 2026-07-23: v1 policy established the generated Markdown/JSON evidence map,
  complete registry projection, namespaced graph, staleness gate, atomic
  writes, and token-efficient lookup rule.
