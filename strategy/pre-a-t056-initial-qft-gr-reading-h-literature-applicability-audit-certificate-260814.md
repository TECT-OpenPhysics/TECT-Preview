# R-170 v1.0 initial QFT/GR/Reading-H literature-applicability audit

Version: R-170 v1.0
Exploration: EXP-000863
Task: T-056
Tier: T0
Claim-bearing: false
Issued: 2026-08-14

## 1. Result and exact closure scope

This certificate completes the first four records required by the binding literature-first policy:

- `B1-RH-ENUM`: `APPLIES`, but only to the live registered `C_full` Reading-H comparison `F_total[Q] > F_total[G_*]` in region `R`, given `A1-KERNEL-CONV`;
- `C4-GRAVITY-1LOOP`: `NOT-YET-ASSESSED`, with no load-bearing import;
- `C5-NEWTON-G`: `NOT-YET-ASSESSED`, with no load-bearing import; and
- `C6-SPACETIME-SIGNATURE`: `DOES-NOT-APPLY` only for the present BCC-premised inheritance route, while non-BCC alternatives remain `NOT-YET-ASSESSED`.

The procedural gate `LITERATURE-FIRST-APPLICABILITY-AUDIT` may therefore be marked exactly `CLOSED@INITIAL-FOUR-RECORDS`. The policy remains binding for every later load-bearing import. Closing the rollout gate is not a global declaration that the literature has been exhausted or that all current claims have applicable sources.

## 2. Decision rule and authority order

The policy permits exactly four overall dispositions: `APPLIES`, `APPLIES-CONDITIONALLY`, `DOES-NOT-APPLY`, and `NOT-YET-ASSESSED`. Every source hypothesis is separately marked `SATISFIED`, `CONDITIONAL`, `FAILED`, or `UNASSESSED`. A load-bearing `FAILED` or `UNASSESSED` row blocks import. A bounded search can locate candidates but cannot prove novelty, source absence, or applicability.

For all four claims, `status.json` is the live authority for tier, lifecycle, hypotheses, dependencies, gates and scope. Older `claim.md` prose is compatibility history where it disagrees with the live card. This matters twice: the B1 prose predates the live T7 `C_full` scope, and the C6 prose still names B3 even though the live card has removed it. This audit records those drifts but does not edit either claim card or silently reconstruct current topology from compatibility prose.

## 3. B1 applies only inside the current Reading-H owner

The imported B1 theorem is

`F_total[Q] > F_total[G_*]`

for every admitted finite real-antipodal amplitude point set `Q` in `C_full`, on the three-dimensional Brazovskii shell `|k|=q0`, and for `(I,mu2)` in the registered region `R`, given `A1-KERNEL-CONV`. The reference `G_*` is the rotation-invariant Gaussian-Hartree shell dressing in the same variational owner.

No physical spatial volume, van Hove sequence, UV cutoff, lattice-spacing regulator, thermodynamic limit, continuum limit, zero-temperature limit, P1 field map, or absolute physical-empty normalization is quantified by the imported statement. In particular,

`F_total[Q] > F_total[G_*]`

does not imply

`F_total[G_*] - F_total[physical empty] < 0`.

Candidate membership in `C_full` is an explicit admission condition, not something supplied by a geometric label or a covariance alone. The correct stop decision is to reuse the current relative ordering and direct new proof effort to a same-parent `G_*`-versus-empty theorem or to the separate Reading-H-to-P1 interface.

## 4. C4 remains NOT-YET-ASSESSED

The live C4 card points only to an unresolved legacy Pillar-3 record and has `PACKAGE-PENDING` reproduction. The selected claim-filtered search returned no rows. A targeted on-demand inspection found Math41, Math45, Math48, Math416 and the Paper-03 README under the configured Contents source root, each with a recorded SHA-256. They remain discovery candidates: they are not selected, copied, registered or current-owner revalidated.

The candidate text is itself conditional. It describes a spatial transverse-traceless candidate, open production runs, missing scaffold, unresolved channel mapping and scheme/limit obligations. A positive Euclidean spatial coefficient does not prove a Lorentzian Einstein-Hilbert action, ghost control, diffeomorphism redundancy or universal coupling. Therefore no theorem is imported and `SCHEME-2LOOP` remains open.

## 5. C5 remains NOT-YET-ASSESSED

The live C5 card names `H-LEGACY-CHAIN` and has `PACKAGE-PENDING` reproduction. The selected claim-filtered search returned no rows. A targeted on-demand inspection found Math291, Math404 and three Math110 candidates. They remain discovery-only.

The candidate relation

`G = c^3 a_BCC^2/(16 pi hbar)`

is not admitted by this audit. Its derivation depends on unregistered or unverified Kibble-Zurek, elastic-density and wave-speed hypotheses. The bounded candidate chain also contains incompatible `16 pi`, `32 pi`, and `64 pi` normalizations. Math404 fixes `a_BCC` using observed constants, so the resulting numerical agreement is `MATCHED` or tautological, not `PREDICTED`. `GAP-3` and `PRED-G-FREEZE` remain open.

## 6. The present C6 BCC route does not apply

The selected legacy anisotropy source starts with a three-dimensional BCC/Brillouin-zone setup. It does not derive why there are three spatial dimensions, construct a temporal degree of freedom, prove one negative kinetic direction, establish hyperbolicity or ghost freedom, or produce a protected common cone. The BCC physical-vacuum premise is also unavailable because `B3-BCC-STRUCT` remains T0 `REFUTED` and retired.

The correct classification is scoped: the present BCC-premised inheritance route `DOES-NOT-APPLY`. This is not a universal no-go for emergent spacetime. A genuinely non-BCC structural owner and low-energy action may still be assessed, so those alternatives remain `NOT-YET-ASSESSED`. `C6-SPACETIME-SIGNATURE` stays T1/ACTIVE and `C6-BCC-PREMISE-BLOCKED` remains open.

## 7. Bounded search and source quarantine

All four selected-index searches used `verification/scripts/legacy_search.py`, the exact claim filter and `--limit 50 --json` on 2026-08-14:

| Claim | Query | Rows | Unique source IDs | Boundary |
|---|---|---:|---:|---|
| B1 | `Reading-H Gaussian Hartree G_* C_full` | 50 | 22 | limit saturated; current stable authority controls |
| C4 | `Einstein-Hilbert one-loop gravity` | 0 | 0 | selected index only; targeted candidates later found |
| C5 | `Newton constant G a_BCC relation` | 0 | 0 | selected index only; targeted candidates later found |
| C6 | `Lorentzian signature 3+1 spacetime` | 50 | 22 | limit saturated; selected source controls |

The zeroes do not mean that no source exists. The saturated counts are not total-corpus counts. Machine-specific absolute Contents roots are not tracked. Candidate `Contents/...` paths and hashes are evidence of bounded discovery only and do not close T-057 or create load-bearing imports.

## 8. Independent verification contract

The primary verifier parses every record, derives its metadata, crosswalk rows, load-bearing rows, section coverage, adversarial axes, source locators and bounded-search facts, then compares the result with clearly labelled test oracles. The independent verifier uses a separate standard-library parser and does not import the primary or integrated module. The integrated verifier compares both derived outputs, rejects dynamic execution and non-standard-library imports in the independent lane, checks exact source hashes and file format, and audits staged or formal lifecycle topology.

The recorded numerical facts are counts and hashes, not model parameters: four records, four selected-index searches, the exact row and unique-source counts shown above, and the final repository topology. They are derived from the records, query results and live ledgers before comparison with labelled oracles. No derived value is copied into an executable derivation path as an unlabelled constant.

## 9. Formal topology and nonduplication

`R-170 v1.0` is a new reusable audit result, not a new physical theorem. It continues the policy decision `EXP-000859` and records the completed first rollout as `EXP-000863`. Exactly one procedural gate closes at the scoped status `CLOSED@INITIAL-FOUR-RECORDS`. The residual T-057, Reading-H interface, physical-empty, C4, C5, C6 and Round-1 gates remain open. No new negative result is registered; the existing B3 structural-selection negative is reused only as a premise-status authority for the C6 route classification.

This does not duplicate R-169. R-169 separates Reading-H owners, realizations and physical-empty obligations. R-170 applies the repository-wide literature gate to four live cards, freezes source/crosswalk/reproduction/adversarial/stop records, and quarantines incompatible or unselected imports.

## 10. Devil's-advocate audit

1. **Sign and reference swap - UPHELD outside the B1 scope.** Candidate minus `G_*` cannot be silently replaced by `G_*` minus physical empty. The record and verifier require the exact orientation.
2. **Factor and convention drift - UPHELD for C5.** The candidate chain contains `16 pi`, `32 pi`, and `64 pi` variants. No coefficient is imported until the convention is reconciled.
3. **Units and owner identity - UPHELD.** Dimensional consistency of a scalar formula does not establish its physical premises, and a spatial TT coefficient is not a Lorentzian action.
4. **Domain and regularity - UPHELD outside the declared B1 class.** B1 requires actual `C_full` membership. C4 requires a current TT/channel/gauge crosswalk. C6 requires a valid state and low-energy mode map.
5. **Convergence and order of limits - UPHELD.** None of C4, C5 or C6 imports a controlled regulator, thermodynamic or continuum passage. B1 imports no such passage either.
6. **Hardcode masking - MITIGATED.** Both lanes derive record counts, statuses, search facts and hashes before comparing labelled test oracles; the integrated AST audit rejects primary reuse by the independent lane.
7. **Zero, empty and saturated-search cases - VALID with explicit boundary.** Zero selected-index hits are not source absence, and a saturated 50-row result is not a corpus total. Both cases are tested.
8. **Stale prose override - UPHELD and blocked.** Live `status.json` remains authoritative over older B1/C6 `claim.md` prose; the verifier checks that the audit records say so.
9. **Gate overclosure - UPHELD and blocked.** `CLOSED@INITIAL-FOUR-RECORDS` does not retire the policy or close future claim-specific audits.

External review is invited on the source locators, B1 owner/reference identity, C4 TT-to-Einstein-Hilbert crosswalk, C5 normalization chain, C6 dimension/signature distinction, and all stop decisions.

## 11. Reproduction commands

Run with the project interpreter:

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/pre_a_t056_initial_qft_gr_reading_h_literature_applicability_audit.py --staged --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/pre_a_t056_initial_qft_gr_reading_h_literature_applicability_audit_independent.py --staged --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/pre_a_t056_initial_qft_gr_reading_h_literature_applicability_audit_verify.py --staged --no-store
```

After the formal authorities land, omit `--staged` and store the primary result, then the independent result. Regenerate once so the catalog contains those two runs, store the integrated result, and regenerate again. Finally rerun all three with `--no-store`, run the release gate, and confirm stored-versus-fresh equality. A child never requires its own result to pre-exist; the integrated lane requires the two stored children and permits its own result to be absent during its first canonical store.

## 12. No-overclaim boundary

This T0, claim-nonbearing audit changes no claim tier or lifecycle. It proves no physical-empty sign, no Reading-H-to-P1 bridge, no Einstein-Hilbert theorem, no Newton-constant prediction, no emergent dimension or Lorentzian signature, no Round-1 admission, and no physical Sector A or Pre-A closure. It registers no new negative result. No R-170 v1.0 PDF is issued.
