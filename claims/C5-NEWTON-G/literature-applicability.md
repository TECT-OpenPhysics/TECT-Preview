# C5-NEWTON-G literature applicability

**Claim:** `C5-NEWTON-G`
**Reviewed:** 2026-08-14
**Overall disposition:** `NOT-YET-ASSESSED`
**Load-bearing use:** No.
**Authority rule:** `status.json` is the live claim authority. The existing relation/value split is preserved, but no legacy formula is imported by this audit.

## 1 Exact target and intended role

The target is whether `G=c^3 a_BCC^2/(16 pi hbar)` is a derived current-model relation and, separately, whether it predicts the numerical value of `G`. The intended role would be limited to a dimensionally and conventionally pinned algebraic relation under named hypotheses. A value obtained after using observed `G` to set `a_BCC` is a match or identity, not a prediction.

## 2 Stable source locator or bounded absence record

The live card gives only `legacy:Newton-G relation chain (emergent gravity notes)`, carries `H-LEGACY-CHAIN`, and has `PACKAGE-PENDING` reproduction:

- `claims/C5-NEWTON-G/status.json`, SHA-256 `2d4f704d215b4336c594194d16f21e6de108d0bafc1ba9a83d68919783b87e4a`.
- `claims/C5-NEWTON-G/claim.md`, SHA-256 `9608de91436e41ab8f9670fac90920cef586d33a6ab84caae78294b11b7016c7`.

A bounded selected-index search was run on 2026-08-14 with
`python verification/scripts/legacy_search.py query --text "Newton constant G a_BCC relation" --claim C5-NEWTON-G --limit 50 --json`.
It returned zero rows and zero unique source IDs in the current claim-filtered selected index. A subsequent targeted, on-demand inspection under the configured Contents source root found the following candidate, not admitted, sources:

- `Contents/Docs/math/TECT-Math291-GAP1-Hbar-Canonical-Formula-Reconciliation-Errata.tex.txt`, lines 238-315, 382-396, and 493-519, SHA-256 `072e149c0ba4828f2fce7779f640c63b854c9cb6e356f3475eab6b8b0454adb3`.
- `Contents/Docs/math/TECT-Math404-TECT-Scale-Identification-Planck-Anchor-via-Pillar9.tex.txt`, lines 26-41 and 151-157, SHA-256 `abd41de786b44ccc6737eaf4fee3166eaeb6c84cc75e6abd6cc91bb70695c058`.
- `Contents/Docs/math/TECT-Math110-AddA-Fierz-Pauli-EH-coefficient-verification.tex.txt`, SHA-256 `6a5f9b92806a9832bfdd2d6f9060f96d201a1724aeb8aa913cd88bfb334edf9d`.
- `Contents/Docs/math/TECT-Math110-AddG-Step1-rho-cond-to-G-elastic-derivation.tex.txt`, SHA-256 `92cd15237a0b6173ce0514e7dcc0259b0ea76e7550b3a2d9ab2ce75b97950077`.
- `Contents/Docs/math/TECT-Math110-AddI-Step3-hbar-G-c-closure-RF5-proof.tex.txt`, SHA-256 `ac4b9e68f17f8fcfdf08535a12a2e3102e408d27b1090279a598a374a7b9d006`.

The Math291 candidate states a conditional algebraic theorem and explicitly calls the numerical Planck match tautological. Math404 uses observed constants to set the scale. The Math110 candidates contain unresolved `16 pi`, `32 pi`, and `64 pi` normalization variants and a dimensional objection. These discovery candidates are not selected or current-convention revalidated, so the overall disposition remains `NOT-YET-ASSESSED`. The selected-index query, its 50-row bound, and the targeted filenames above define the audit window; this is explicitly non-exhaustive and makes no world-first or no-source claim.

## 3 Assumption-to-model crosswalk

| Source hypothesis | TECT object or authority | Disposition | Load-bearing for target | Reason |
|---|---|---|---|---|
| A stable primary or immutable archived derivation is admitted | Current C5 card and T-057 registry | `UNASSESSED` | yes | The live pointer is vague and the discovered Contents files are not selected authorities. |
| SI dimensions and positive scalar constants are used consistently | Candidate Math291 formula | `SATISFIED` | no | Dimensional algebra can be checked, but it does not validate the model premises. |
| `rho_cond=c^4/(16 pi G a^2)` and `c_T=c` hold in the current owner | Candidate Math110 AddG/AddH chain | `UNASSESSED` | yes | The hypotheses are not named and revalidated in the current card. |
| Kibble-Zurek timing `tau=a/c_T` and one-cell action equal `hbar` | Candidate Math291 `H_KZ` | `UNASSESSED` | yes | This is the load-bearing physical hypothesis, not a proved identity. |
| The `16 pi` coefficient convention is unique and correct | Candidate normalization chain | `FAILED` | yes | The bounded candidates contain incompatible coefficient variants. |
| Algebraic rearrangement of a fixed formula is valid | Elementary scalar algebra | `SATISFIED` | no | Rearrangement alone does not establish the input formula. |
| `a_BCC` is derived independently of observed `G` and `hbar` | `PRED-G-FREEZE` | `FAILED` | yes | Math404 fixes the scale from observed constants, so the numerical value is matched rather than predicted. |
| A current physical BCC/Reading-H owner supplies the scale | B3/C6 and Reading-H interface state | `FAILED` | yes | The physical BCC premise is unavailable and the interface remains open. |
| Regulator, volume, continuum and renormalization limits are controlled | No current authority | `UNASSESSED` | yes | The candidate is a scalar relation, not a controlled field-theory limit. |

## 4 Exact imported conclusion and scope

No conclusion is imported into C5. If future preservation and revalidation establish the Math291 hypotheses and a unique normalization, elementary algebra would give only a conditional positive-scalar SI relation. The candidate numerical evaluation remains `MATCHED`, not `PREDICTED`, whenever observed `G` or `hbar` is used to define `a_BCC`.

No field space, regulator, volume, state, ensemble, renormalization, or limiting theorem is presently imported.

## 5 Reproduction and independent-check disposition

The live card is `PACKAGE-PENDING`. An independent symbolic unit and rearrangement check would be sufficient for the algebra after the premises are fixed, but it cannot revalidate `H_KZ`, the coefficient convention, or the physical scale owner. No waiver is granted; the route remains blocked from load-bearing use.

## 6 Adversarial checks

- **Convention/sign/factor - UPHELD objection.** The bounded source chain contains incompatible `16 pi`, `32 pi`, and `64 pi` coefficients; the factor is not frozen.
- **Circularity - UPHELD objection.** Solving for `G` after observed `G` helped define `a_BCC` is an identity, not a prediction.
- **Domain/regularity - UPHELD objection.** The Kibble-Zurek, elastic-density, wave-speed, and physical-BCC hypotheses are not revalidated in the current owner.
- **Limit/order-of-limits - UPHELD objection.** No regulator, continuum, thermodynamic, or renormalization passage accompanies the scalar formula.

## 7 Residual proposition or stop decision

Stop load-bearing use of the formula. Select and preserve the candidate chain, resolve the normalization contradiction, register and prove or explicitly assume `H_KZ` plus the Math110 premises, and derive `a_BCC` without observed `G` or the same `hbar` relation. Only then may `PRED-G-FREEZE` test a numerical prediction.

## 8 No-overclaim boundary

This record changes no C5 tier or lifecycle. It does not derive or predict Newton's constant, close `GAP-3` or `PRED-G-FREEZE`, establish a physical BCC scale, or advance C6, Round-1, physical Sector A, or Pre-A.
