# Reproduction-bundle policy (binding from 2026-06-10)

**The final deliverable of every claim is a self-contained referee REPRODUCTION
BUNDLE** -- not merely a note, and not merely "reference code". A claim is not
publication-complete until an outsider, with no TECT checkout, can run the bundle
and obtain the same PASS lines and numbers.

## 1. Why (the two-layer verification gap)

A referee note alone lets an external reviewer verify the *mathematical structure*
(definitions, lemmas, the proof map). It does NOT let them *reproduce the numbers*
(constants, windows, intervals, sanity checks). "Here is the reference code" is also
insufficient: without the environment, the inputs, the expected output, and a version
pin, code is reviewable but not reproducibly verifiable. The bundle closes the gap:

```
note  +  code  +  environment  +  expected output  +  hash/log  +  README
   => external reproduction verification is possible.
```

## 2. Mandatory bundle contents

| Item | Purpose |
|---|---|
| the referee note (`.tex.txt` + `.pdf`) | the self-contained proof map (scope, lemmas, falsifier) |
| every reproduction script | reproduces each numerical claim |
| all transitive local dependencies | removes hidden dependencies (constants/engine modules) |
| `requirements.txt` | exact third-party packages (e.g. numpy) |
| `environment.txt` | python version + platform + package versions at build |
| `expected/<script>.log` | captured stdout = the PASS reference to diff against |
| `MANIFEST.json` | sha256 of every file + a content-addressable bundle digest + `repo_commit` |
| `README.md` | run order + expected PASS + integrity + scope/attack pointer |

The note's `Reproduction command` and `Falsifier` footer fields, and its scope
(T7-SCOPE etc.), MUST be honoured verbatim in the bundle README.

## 3. The builder (reusable, not hand-assembled)

Bundles are generated, never hand-assembled:

```
python verification/scripts/build_reproduction_bundle.py \
    --note   claims/<ID>/<sub>/notes/<note>.tex.txt \
    --scripts codes/.../res5_0NN_*.py ... \
    --out    claims/<ID>/<sub>/bundle/<name> \
    --title  "<one line>"
```

Mechanism: TECT scripts self-locate `REPO = __file__.parents[2]`, so a bundle that
MIRRORS the repo-relative paths of the needed files runs UNCHANGED -- the builder
resolves the transitive local imports by AST, copies them preserving paths, RUNS each
entry script with the bundle as its repository root (capturing `expected/` and emitting
each `result.json` inside the bundle), and writes `requirements.txt`, `environment.txt`,
`README.md`, `MANIFEST.json`. `__pycache__`/`*.pyc` are excluded (gitignored). The build
exits non-zero if any entry script fails, so a bundle never ships with a failing check.

## 4. Version pin

`MANIFEST.json:repo_commit` is stamped at publish (`git rev-parse HEAD`); the
`bundle_digest` (sha256 over `<sha256>  <path>` lines) is content-addressable and fixes
the bundle independently of the commit. A published bundle without a stamped commit and a
matching digest is not citation-grade.

## 5. Reference instance

The first bundle is the Reading-H full-class vacuum-selection result:
`claims/B1-RH-ENUM/Reading-H/bundle/reading-h-cfull-260610/` (note v1.1 + res5_032--036 +
8 code deps; 23 canonical files; all 5 scripts PASS, 27/27 asserts).

## 6. Distribution

Bundles are the publish-tier distribution artefact for a claim: a referee receives the
bundle (or its archive) and reproduces independently. The bundle directory is
self-contained and may be zipped for transport. Mirror exposure (GitHub release / wiki)
links the bundle by its `bundle_digest`.

## 7. Per-claim completion criterion

A claim at tier T5 or above is publication-complete only when its reproduction bundle
exists, builds (all entry scripts PASS), and is registered (RESULTS-LEDGER + this policy's
reference list). Lower-tier claims SHOULD carry a bundle once they have any numerical claim.


## 8. Granularity and threshold (binding from 2026-06-10)

> **SUPERSEDED IN PART by sec.14 (2026-06-11)**: the per-sub-proof-folder bundle unit is retired. Bundles are MAIN-LINE-ONLY and live only at the claim top level; sub-proof folders keep only their final note.

**Unit = the result-bearing sub-proof folder.** One bundle per
`claims/<ID>/<sub>/` folder that carries a result, NOT one per claim (too coarse:
a claim spans several independent sub-results) and NOT one per note (too fine:
notes within a folder share scripts). The bundle reproduces the WHOLE folder:

- entry document = the folder's HEADLINE note -- the latest non-superseded
  consolidation / highest-tier note (names matching consolidation / final /
  referee / audit / enactment / closure are preferred; ties broken by version);
- code = the UNION of reproduction scripts cited by the folder's non-superseded
  notes (so every load-bearing numerical claim in the folder is reproducible),
  plus their transitive local dependencies.

**Threshold -- when a bundle is MANDATORY** (gated on the owning CLAIM's tier):

| Claim tier | Bundle requirement |
|---|---|
| **T7 / T6 / T5** | MANDATORY for every result-bearing sub-proof folder |
| **T4** | RECOMMENDED for the headline sub-proof folder |
| **T3 / T2 / T1 / T0** | not required (sketch / conjecture / open / refuted) |

Rationale: T5 (PINNED-CLOSURE) and above are citable / publication-grade, so they
must be independently reproducible; T4 is strong-evidence (build once stable);
below T4 there is no result to bundle. In addition, **every RESULTS-LEDGER R-NNN
standalone-publishable result MUST be covered by a bundle** -- its sub-proof
folder's bundle, or (if the R-NNN spans folders) its own.

A T5+ claim is publication-complete only when ALL its result-bearing sub-proof
folders have current bundles that build (all entry scripts PASS). Coverage is
tracked by `python verification/scripts/bundle_coverage.py` (a folder at T5+ with
notes but no current bundle is a coverage defect).

## 9. Build / batch

Single folder (auto-discovers headline + union of scripts):
```
python verification/scripts/build_reproduction_bundle.py --folder claims/<ID>/<sub>
```
All mandatory folders + coverage report:
```
python verification/scripts/bundle_coverage.py            # report gaps
python verification/scripts/bundle_coverage.py --build    # build all missing T5+ bundles
```
Heavy folders (many scripts) may be built operator-side; the build is idempotent
and the coverage report is the completeness gate.


## 10. Bundle grades: DRAFT vs PUBLISHED (binding from 2026-06-10)

> **SUPERSEDED IN PART by sec.14 (2026-06-11)**: the DRAFT bundle grade is RETIRED. A bundle is produced only after operator confirmation; every bundle is PUBLISHED. Pre-confirmation inspection uses the note + scripts directly, not a packaged bundle.

Auto-assembling a folder's internal working notes is NOT a first-rate referee
artefact. A bundle has two grades:

- **DRAFT** -- produced by `build_reproduction_bundle.py --folder`, whose entry
  document is the folder's existing headline (internal) note. Useful for internal
  reproduction and as scaffolding; NOT for external publication.
- **PUBLISHED** -- the entry document is a PURPOSE-WRITTEN, self-contained,
  validated **integrated referee package** (the template is
  `reading-h-cfull-referee-package`): one document that states the result, its
  scope, the definitions, the lemmas with proofs, the numerical-reproduction map,
  the devil's-advocate and the falsifier, so a referee reads ONE file and can
  attack it. The package MUST: (i) FORM-CHECK pass and build to PDF with zero
  Overfull-hbox; (ii) be self-contained (no proof dependency on sibling notes);
  (iii) have its reproduction scripts PASS in the bundle. The bundle is then built
  with `--note <referee-package> --scripts <...>` (or `--folder` after the
  package is the folder's headline).

**A claim is publication-complete only when each of its result-bearing sub-proof
folders has a PUBLISHED bundle.** DRAFT bundles satisfy internal reproduction but
not the publication criterion of sec.7-8.

**Self-containment includes runtime file reads.** The dependency resolver
(`build_reproduction_bundle.py` v1.3.0+) follows not only `import` statements but
also runtime `"<name>.py"` string reads (e.g. a script that `read_text()`s a
legacy module), transitively -- a bundle that omits a runtime-read dependency
silently fails reproduction (canonical failure: `g3pb3_ratio_extraction.py`
reading `Math432_*.py`). Every PUBLISHED bundle's scripts MUST pass from a clean
checkout of the bundle alone.

## 11. Workflow per folder -- the operator-confirmation gate (binding from 2026-06-10)

> **SUPERSEDED IN PART by sec.14 (2026-06-11)**: there is no pre-confirmation DRAFT bundle; packaging is the LAST step and is followed by the final integrity check. See sec.14 for the canonical order.

A PUBLISHED bundle is NOT built from an unreviewed referee document. The entry
referee package must be confirmed by the operator FIRST -- a `no-auto-PUBLISHED`
rule, the analogue of the `no-auto-T7` sign-off. The per-folder order (T7 first):

1. WRITE the integrated referee package note (synthesise the folder's result;
   self-contained; honour scope/tier/no-overclaim).
2. VALIDATE: build its PDF (0 overfull); confirm self-containment; run its
   reproduction scripts to PASS.
3. **OPERATOR REVIEW + CONFIRM** -- the operator adversarially reviews the
   package; revise to v(N).(M) until confirmed. Confirmation is recorded in the
   package's revision-history banner (`operator-confirmed <date>`) and in the
   changelog (as the Reading-H v1.0 -> v1.1 -> ACCEPT cycle was).
4. ONLY THEN BUILD the PUBLISHED bundle around the confirmed package
   (`build_reproduction_bundle.py --note <confirmed package> --scripts ...`).
5. Register (RESULTS-LEDGER / coverage) and commit.

Until step 3, the folder may carry a DRAFT bundle (auto `--folder`) for internal
reproduction, but it is NOT publication-grade. A PUBLISHED bundle whose entry
package lacks the `operator-confirmed` marker is a coverage defect. This is
deliberately one-folder-per-increment; the referee package is the deliverable
that takes care, gated by operator confirmation, not an auto-dump.

Reference: the Reading-H package (`reading-h-cfull-referee-package`) was written
v1.0, operator-reviewed (three dependency patches), re-issued v1.1, operator-
confirmed, and only then bundled -- this is the canonical template for every
PUBLISHED bundle.


## 12. Main proof line vs auxiliary (binding from 2026-06-10)

> **SUPERSEDED IN PART by sec.14 (2026-06-11)**: auxiliary/cited folders get NO bundle at all (note only); only main-line results are packaged.

A referee package (PUBLISHED) is written for each result on the **MAIN PROOF LINE**
of the published claim -- the load-bearing final-consolidation documents the
headline package cites as dependencies -- NOT for every sub-proof folder. The
theory's intermediate process produces results that are partly load-bearing,
partly auxiliary (robustness, provenance, controlled-error numerics), and partly
retracted; turning all of them into referee artefacts buries the main line.

Classification (per published claim):

- **Main proof line** -> PUBLISHED referee package (operator-confirmed). Determined
  by the headline package's `Dependencies` footer + the lemma/step citations: every
  document that the published theorem actually rests on.
- **Auxiliary / cited** (robustness sweeps, provenance/migration records,
  controlled-error numerical upgrades, sub-lemmas folded into a main-line document)
  -> DRAFT bundle at most (internal reproduction); NO referee package. They are
  cited by the main line, not independently published.
- **Retracted** -> `negative-results/`; no bundle.

The current main proof line for the published Reading-H C_full result
(T7-SCOPE_{C_full}) is registered in `theory/main-proof-line.md`; that map -- not
the per-folder coverage -- is the referee-package work list. A DRAFT referee
package written for an auxiliary folder is NOT a coverage obligation and is not
promoted to PUBLISHED.


## 13. Bundle location convention (binding from 2026-06-11)

Bundles live at the CLAIM top level, one directory per result, tier- and
date-stamped:
```
claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/
```
e.g. `claims/B1-RH-ENUM/bundle/Reading-H-cFull-T7-260611/`. Rationale: a new
bundle is produced each time the result's TIER changes, so the directory listing
is itself the tier history of the result; and all of a claim's bundles sit
together rather than scattered across sub-proof folders. The builder
(`--folder`, or `--note ... --tier <T> --result <slug>`) emits this path by
default. A superseded tier's bundle is retained (history); the current bundle is
the highest-tier dated one. MANIFEST `bundle_digest` fixes each.

## 14. Canonical bundle model and packaging order (binding from 2026-06-11; supersedes the DRAFT-grade and per-sub-folder parts of sec.8/10/11/12)

Operator directive 2026-06-11. The bundle is the FINAL packaging of a confirmed
result; it is produced LAST, once, and then integrity-checked. There is no
pre-confirmation bundle and no "DRAFT" bundle.

### 14.1 What gets a bundle (main-line only, claim-level only)

- A bundle exists ONLY for a result on the MAIN PROOF LINE (`theory/main-proof-line.md`).
- A bundle lives ONLY at the claim top level:
  `claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/`.
- Sub-proof folders (`claims/<ID>/<sub>/`) keep ONLY their final organised note(s)
  (`.tex.txt` + `.pdf`). They MUST NOT contain a `bundle/` sub-folder.
- Auxiliary / cited / provenance / sub-lemma folders get NO bundle (note only).

### 14.2 No DRAFT bundle; grade is always PUBLISHED

- The DRAFT bundle grade (old sec.10) is RETIRED. A bundle is never built before
  operator confirmation.
- Pre-confirmation inspection is performed on the referee NOTE and its
  reproduction SCRIPTS directly -- e.g. a clean-repo reconstruction that runs the
  scripts and checks the PASS lines -- NOT on a packaged bundle.
- Every bundle's README grade is `PUBLISHED (operator-confirmed)`. The bundle
  name's `<Tier>` is the result's confirmed T-tier (e.g. `T6`, `T7` for a
  T7-SCOPE result). The tag `DRAFT` is forbidden;
  `build_reproduction_bundle.py` rejects it.

### 14.3 Canonical packaging order (bundle is packaged LAST, then checked)

1. WRITE / refine the integrated referee package note (self-contained; honour
   scope / tier / no-overclaim).
2. VALIDATE: build its PDF (0 overfull); confirm self-containment; run its
   reproduction scripts directly to PASS.
3. OPERATOR REVIEW + CONFIRM. Revise `v<N>.<M>` until confirmed; record
   `operator-confirmed <date>` in the banner and the changelog. No bundle yet.
4. ONLY THEN PACKAGE the bundle around the FINAL confirmed note
   (`build_reproduction_bundle.py --note <confirmed note> --scripts <...> --tier <T>
   --result <slug>` -> `claims/<ID>/bundle/<Result>-<Tier>-<YYMMDD>/`).
5. FINAL INTEGRITY CHECK after packaging: the builder's post-build fsync + JSON/PY
   guard (v1.6.0) must report clean, AND `python verification/scripts/release_check.py`
   must reach exit 0. This PASS is the last confirmation that the package is sound.
6. REGISTER (changelog; `main-proof-line.md` PUBLISHED row) and commit.

### 14.4 Tier-change re-packaging (history)

When the result's tier changes, repeat 1-6; the new bundle
`<Result>-<NewTier>-<YYMMDD>/` is added beside the old one, so the claim-level
`bundle/` listing is the tier history. Superseded tiers' bundles are retained as
history; the current bundle is the highest-tier dated one.

## 15. Bundle production ordering: ascending tier, capstone last (binding from 2026-06-12)

Operator directive 2026-06-12 (REVERSING the earlier highest-tier-first practice;
refined same day: DEPENDENCY ORDER takes precedence over tier): within a claim's
MAIN PROOF LINE, referee packages and their bundles are produced and reviewed in
DEPENDENCY-FIRST order -- a package is queued only after every package it depends
on -- with ASCENDING tier order among packages at the same dependency level, and
the highest-tier final consolidation/claim LAST.

Rationale: lower-tier support packages are the INPUTS of the higher-tier
consolidations. Publishing them first means that by the time the highest-tier
package is reviewed, every support result it cites is already PUBLISHED-BUNDLE
CONFIRMED, so the final bundle is a true capstone whose dependency chain is fully
inspected -- rather than a head published over unreviewed supports (the
highest-first order forced exactly that inversion).

Operational rules:

- Ordering keys, in precedence: (1) DEPENDENCY (topological: supports before
  the packages that cite them); (2) ascending tier among same-level packages;
  (3) date. A dependency edge always outranks a tier comparison.
- The claim's final consolidation / synthesis package (the highest-tier item,
  e.g. a T7 C_full theorem package) is reviewed and packaged ONLY AFTER all its
  main-line support packages are PUBLISHED-BUNDLE CONFIRMED.
- The sec.14.3 packaging order applies unchanged WITHIN each package; this
  section fixes the order BETWEEN packages.
- History note: the 2026-06-10/12 cycle ran highest-first (Reading-H C_full T7
  -> Prop-A T6 -> STEP-5B-Rectangle T6 -> SC-SCOPE T5, with DR-2 T7-mod-NT
  remaining); this is grandfathered, not re-ordered. The rule binds FUTURE
  production, starting with the remaining DR-2 package and any subsequent
  claim-level SYNTHESIS layer (T-013).
