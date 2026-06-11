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
