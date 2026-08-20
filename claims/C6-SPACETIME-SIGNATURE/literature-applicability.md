# C6-SPACETIME-SIGNATURE literature applicability

**Claim:** `C6-SPACETIME-SIGNATURE`
**Reviewed:** 2026-08-14
**Overall disposition:** `DOES-NOT-APPLY` for the present BCC-premised route; non-BCC alternatives remain `NOT-YET-ASSESSED`.
**Load-bearing use:** No.
**Authority rule:** `status.json` is the live claim authority and already removes B3 as a dependency. The older `claim.md` prose still names B3 and is treated as compatibility history, not current topology.

## 1 Exact target and intended role

The target is a theorem deriving three spatial dimensions, one temporal dimension, and Lorentzian signature `(-,+,+,+)` from a valid current TECT state and its low-energy fluctuation action. A usable import must derive rather than assume the dimension and sign, identify the time variable, prove the hyperbolic kinetic structure and common cone, and crosswalk the structural state and limits to the current owner.

## 2 Stable source locator

- Live claim state: `claims/C6-SPACETIME-SIGNATURE/status.json`, SHA-256 `a0d6d7cd99770cd97050eb28fc4dc69180191ba930de629ee023cffc3a2aa811`.
- Retired structural premise: `claims/B3-BCC-STRUCT/status.json`, SHA-256 `c0a651785ec4799540768b796173d8c41dc66b1d3aa8374fd556370e2ca00035`.
- Current failure authority: `negative-results/registry.md#r-2026-06-23-b3-bcc-structural-selection`, registry SHA-256 `546bbd65ee917eae68a9b1a3564431d3fcea72804d4aea79e061e002e097de0e`.
- Selected legacy anisotropy source: `archive/legacy/references/Docs/math/TECT-Math_IR_Bound-v4-thm-v4-2-final-formalization.tex.txt`, especially lines 120-156, source `LEG-SRC-132F4237530C54C6`, SHA-256 `c088cce3026ea41db752eee7c05eb5c8494bbb92837cc61e5d7f93361b3df525`.
- Reviewed geometry record: `archive/legacy/registry/records/LEG-T055-TRUNCATED-OCTAHEDRON-BZ-001.json`, SHA-256 `4b231155a293dc644f9b448326e33be3f5027998513e398b989a71952241755d`.

The selected source concerns anisotropy in a three-dimensional BCC/Brillouin-zone setup. It does not derive why space is three-dimensional or why one direction is temporal.

The bounded selected-index search was run on 2026-08-14 with
`python verification/scripts/legacy_search.py query --text "Lorentzian signature 3+1 spacetime" --claim C6-SPACETIME-SIGNATURE --limit 50 --json`.
It returned 50 rows spanning 22 unique source IDs. The limit was saturated, so the result is a reproducible search window rather than a total-corpus count; the selected source and reviewed record above control this disposition.

## 3 Assumption-to-model crosswalk

| Source hypothesis | TECT object or authority | Disposition | Load-bearing for target | Reason |
|---|---|---|---|---|
| A physical BCC vacuum supplies the background | `B3-BCC-STRUCT` | `FAILED` | yes | B3 is T0 `REFUTED`/retired and cannot be imported as a positive premise. |
| The source conclusion equals the 3+1 Lorentzian target | Selected anisotropy source | `FAILED` | yes | A conditional spatial anisotropy coefficient is not a dimensionality/signature theorem. |
| Three spatial dimensions are derived rather than assumed | `S^2`/three-dimensional Brillouin-zone integral | `FAILED` | yes | The integration domain assumes dimension three. |
| A temporal degree and relational-to-Lorentzian map are defined | No selected source | `UNASSESSED` | yes | No physical time variable or clock construction is imported. |
| The kinetic form is hyperbolic, ghost-free and has one negative signature direction | No selected source | `UNASSESSED` | yes | Positivity or suppression of spatial anisotropy does not fix Lorentzian signature. |
| The legacy field/action maps to the current A1/Reading-H/P1 owner | Current interface authorities | `FAILED` | yes | The required realization and full-energy maps remain open. |
| The source's suppression hypothesis holds | Legacy `H-SUPPRESSION` route | `CONDITIONAL` | no | Even satisfying it would not derive the C6 target. |
| Finite-volume, regulator, continuum and low-energy limits are controlled in one order | No current authority | `UNASSESSED` | yes | No such passage is registered for C6. |

## 4 Exact imported conclusion and scope

No physical conclusion is imported. The selected material may be reused at T0 for Brillouin-zone geometry, cubic-harmonic decomposition, or interval-integration methods after a separate applicability check. It supplies no quantifier over valid physical states, no emergent time, no Lorentzian sign, no common cone, and no current-owner limit theorem.

## 5 Reproduction and independent-check disposition

The reviewed legacy geometry record remains at a T0 ceiling with revalidation incomplete for the C6 target. The C6 card has `PACKAGE-PENDING` reproduction. No waiver is granted, and no numerical anisotropy PASS is accepted as proof of dimension or signature.

## 6 Adversarial checks

- **Convention/sign - UPHELD objection.** A positive or suppressed spatial anisotropy coefficient does not determine the Lorentzian kinetic sign.
- **Domain/regularity - UPHELD objection.** A three-dimensional Brillouin-zone integral assumes, rather than derives, the number of spatial dimensions.
- **Structural premise - UPHELD objection.** The BCC physical-vacuum premise is refuted/retired.
- **Limit/order-of-limits - UPHELD objection.** No temporal, low-energy, thermodynamic, continuum, or regulator passage is supplied.

## 7 Residual proposition or stop decision

Stop the present BCC-premised inheritance route. A successor must first provide a valid physical structural owner or an explicitly non-BCC alternative, then derive the low-energy mode content, one time direction, hyperbolic signature, ghost control, and a protected common cone with controlled limits. Non-BCC routes remain `NOT-YET-ASSESSED` rather than universally excluded.

## 8 No-overclaim boundary

This record does not change the C6 T1/ACTIVE scaffold. It does not prove or universally refute emergent spacetime, close `C6-BCC-PREMISE-BLOCKED`, restore B3, or advance Round-1, physical Sector A, or Pre-A.
