# How to review or attack TECT in 30 minutes

TECT is organized so that a reviewer can start from current state, locate the
smallest authority needed for a question, and reproduce or falsify a claim
without loading the historical corpus.

## 1. Start with bounded current views

Open these compact generated pages first:

- [`management/INDEX.md`](management/INDEX.md): live tasks, cited gates, and
  reader routes.
- [`CLAIMS.md`](CLAIMS.md): current claim tiers, scopes, hypotheses, and
  falsifiers.
- [`theory/proof-evidence/INDEX.md`](theory/proof-evidence/INDEX.md): counts and
  targeted proof-evidence search commands.
- [`claims/GATES-INDEX.md`](claims/GATES-INDEX.md): live card-to-gate and
  card-to-hypothesis references, including source mismatches.

The large ledgers remain compatibility and audit authorities. Open them only
at the linked anchor or search them by ID.

```bash
rg -n "<claim-result-gate-or-exploration-id>" theory/proof-evidence-map.md
python verification/scripts/exploration.py search --claim <ID>
python verification/scripts/exploration.py search --verdict failed
```

An exploration verdict is non-tier-bearing: `advanced` is not a proof, and
`failed` is not a global no-go unless a formal negative authority says so.

## 2. Validate the repository

For a quick claim-ledger check:

```bash
python verification/scripts/lint_claims.py
```

For the publication gate used before every repository commit:

```bash
python verification/scripts/release_check.py
```

Exit zero means the generated views match their authorities and the registered
verification gates pass. It does not promote the mathematical or physical tier
of any claim.

## 3. Read one claim at its registered scope

Open `claims/<ID>/claim.md` and `claims/<ID>/status.json`. Check, in order:

1. the exact statement and pinned scope;
2. the maturity tier and lifecycle;
3. named hypotheses and open gates;
4. the falsifier;
5. the reproduction command and expected output;
6. the proof note, run artifact, and adversarial review linked by the card.

`T5` means closed only within its pinned scope. `T6` means a theorem modulo the
listed hypotheses. Neither label establishes a broader physical interpretation.

## 4. Find the current weak points

Do not rely on a hand-written list of "current weakest joints" in a long-lived
document. It becomes stale as gates close or priorities move. Use:

- [`management/INDEX.md`](management/INDEX.md) for live work;
- [`claims/GATES-INDEX.md`](claims/GATES-INDEX.md) for card-cited gates and
  registry/card mismatch warnings;
- [`negative-results/INDEX.md`](negative-results/INDEX.md) for recent failed
  routes and audit findings;
- `todo.py list --status in_progress`, then `--status next` and `--status
  blocked`, for the exact task queue.

The full authorities remain [`claims/GATES.md`](claims/GATES.md),
[`negative-results/registry.md`](negative-results/registry.md), and
[`todo/todo.json`](todo/todo.json).

## 5. Falsify or reproduce a claim

Use the card's own falsifier and reproduction package. A counterexample must
match the registered domain, conventions, regulator, and parameter ledger.
If it breaks a named hypothesis rather than the theorem under that hypothesis,
report that distinction explicitly.

Confirmed failures are recorded in the negative-result registry with evidence
and credit. Reproduction environment requirements are defined in
[`governance/verification-standard.md`](governance/verification-standard.md).

## 6. Reporting

Report the claim ID, exact command or construction, environment, observed
output, and the narrowest conclusion supported by it. Review rounds live under
`reviews/`; confirmed corrections are linked through `reviews/errata/` and the
append-only changelog.

Legacy evidence pointers and prose that exceeds a registered card are not
authoritative. The current claim card and its linked proof authority win.
