# A2/R-157/R-158 ensemble-minimizers paper

Lifecycle: `draft` (version `0.1.1`, 2026-09-03).

This folder is the self-contained draft lane for the paper
“Global Well-Posedness, Neutral-State Rejection, and Ensemble-Induced Shell
Coexistence in a Regularized Multicomponent Brazovskii Functional.”  It is a
manual P2 manuscript, not a submission or a publication record.

## Contents

* `manuscript.tex` — integrated theorem statements and proof text.
* `manuscript.pdf` — the latest locally compiled draft.
* `claims-cited.md` — registered claims, tiers, and non-bearing sidecars.
* `literature-crosswalk.md` — bounded prior-art applicability and novelty
  boundary.
* `verification/README.md` — canonical source paths and reproducibility
  commands.
* `STATUS.md` — completion gates and lifecycle history.
* `proof-audit.md` — internal adversarial checklist and external-review questions.

## Build

From `E:\Dev\TECT`, use the repository environment and the bundled Tectonic
compiler:

```powershell
$env:PYTHONUTF8 = "1"
$env:TECTONIC_CACHE_DIR = "E:\Dev\TECT\internal\tectonic-cache"
$py = "E:\Dev\TECT.venv\Scripts\python.exe"
& $py -X utf8 "C:\Users\NaEun\.codex\plugins\cache\openai-bundled\latex\0.2.6\scripts\compile_latex.py" `
  "E:\Dev\TECT\publish\papers\a2-r157-r158-ensemble-minimizers\manuscript.tex" --json
```

The verification commands and their registered expected results are in
`verification/README.md`.  Executable checks cover exact arithmetic,
normalizations, spectral intervals, and provenance; they do not replace an
independent proof audit.  The internal checklist in `proof-audit.md` makes the
remaining analytic and external-review obligations explicit.

## Release boundary

The paper remains `draft` until the proof audit, specialist literature review,
operator adversarial review, dedicated integrated reproduction bundle, and
repository release check all pass.  No submission, upload, tag, or claim-tier
promotion is authorized by this folder.
