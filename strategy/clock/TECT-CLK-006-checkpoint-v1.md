# CLK006: prepare the missing-input request, not another proof attempt

## Goal and decision boundary

Keep CLK002 and the CLK005 scientific HOLD unchanged. Prepare one unsent
archival request, a fillable intake manifest, and a local checker for missing
fields, fixed-scope substitutions and attachment byte integrity. Independent
and hostile review, reproducible tests and the normal release workflow close
this tooling task only. They cannot close the calibration or coverage question.

DCTRL-000047 remains PARK_OR_BLOCK with no new scientific attempt budget.
This operator-requested preparation neither reruns the absence audit nor
introduces an automatic successor. No observations are acquired or fitted.
No contact, source search, model change, new theorem or physical promotion
is part of CLK006. The original source laws and their conditional error
interpretation remain those of the preserved CLK005 authorities.

## Deliverables

- `TECT-CLK-006-owner-request-v1.md`: an unsent, concise archival request.
- `TECT-CLK-006-intake-template-v1.json`: an optional researcher transcription
  form, not a demand that an analysis owner complete a new bureaucratic form.
- `TECT-CLK-006-intake-policy-v1.json`: fixed scope, hashes and intake meanings.
- `verification/scripts/tect_clk006_intake.py`: byte-only local manifest checker.
- `verification/tests/test_tect_clk006_intake.py`: synthetic regression cases.
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-10-01-tect-clk006/tooling.json`:
  reproducible tooling report, explicitly not observations.

## Use and interpretation

Copy the template and any legitimately supplied attachments into a private,
quiescent intake directory, for example the ignored `internal/clock/intake/`.
Preserve the actual reply and attachment bytes. Record unknown or not-retained
information honestly. Do not copy private correspondence into tracked records
or assume receipt grants redistribution. The request has not been sent.

From the repository root:

```powershell
python -X utf8 verification/scripts/tect_clk006_intake.py --self-test
python -X utf8 verification/scripts/tect_clk006_intake.py --check
python -X utf8 verification/scripts/tect_clk006_intake.py --packet strategy/clock/TECT-CLK-006-intake-template-v1.json
python -X utf8 verification/scripts/tect_clk006_intake.py --packet "PATH_TO_PRIVATE_PACKET.json"
```

The blank template intentionally returns PARTIAL and exit 2, not a test failure.
Replace the final example's placeholder with the actual private packet path.
An absent path returns MISSING and exit 2.
Use the configured UTF-8 Python environment; no network or numerical package
is required by the checker.

| Intake label | Meaning | Exit |
| --- | --- | --- |
| MISSING | No packet at the specified path | 2 |
| PARTIAL | Schema/integrity checks passed so far, but information or files are missing | 2 |
| MANIFEST_COMPLETE_PENDING_CONTENT_REVIEW | Required declarations and matching attachment bytes are present | 0 |
| REJECTED | Malformed, scope-substituted, unsafe-path or hash-mismatched intake | 1 |

All four labels retain HOLD_FOR_EVIDENCE, no empirical-use authorization,
no scientific reentry, no mainline change and no publication authorization.
REJECTED is not a scientific refutation. Exit 0 is not empirical admissibility.
Tooling size limits may require an explicitly reviewed alternative intake;
they are not physical regularization or scientific exclusion thresholds.

Each attachment uses a relative forward-slash path from the packet directory,
a SHA-256 and a unique ID. References use `attachment_id#declared locator`.
The checker validates this syntax and attachment existence/integrity, but does
not resolve the locator, parse a numerical payload, authenticate the owner,
verify permission, or establish novelty. A fabricated but complete synthetic
manifest is therefore deliberately labelled pending content review, never PASS
for science. Do not treat declared `provided` fields as validated assertions.
Unknown, not-retained and not-applicable entries remain partial for required
owner fields; they are useful replies, not reasons to invent replacements.

Only declared attachment paths are read; there is no download, execution,
unpacking or publishing. Path and reparse guards are defensive input checks,
not a security sandbox against a concurrent filesystem adversary. Freeze the
private input directory during inspection and review content through suitable
safe readers separately. The real symlink test may require Windows privilege;
its skip is recorded separately from the mocked reparse-guard test.
The saved report records this host's coverage. `--check` compares source hashes
and all required deterministic cases while allowing only the real-symlink case
to move between a recorded privilege skip and an actual successful execution.

## What remains the researcher's responsibility

The request asks how the original annual coefficient was obtained. It does
not ask the analysis team to certify our hypothetical force law or guarantee
our new model's error. Actual model template v(x), coordinate matching,
gamma_eff(x), coupling-domain validity, non-duplicated theory remainders,
Earth-freefall normalization, atomic/material sensitivity and joint coverage
remain separate researcher obligations.

An epoch/bin-aligned influence row, a documented projection functional on a
declared template class, or a reproducible estimator and design may be useful
without all raw measurements. A bare Gram matrix, published coefficient,
quoted sigma, nominal GM, or self-declared permission does not establish the
missing calibration or coverage. Data-dependent masks, weights or nuisance
choices must be described as actually used, not silently replaced by fixed
ones. A retrospective observation cannot become independent holdout evidence.

## Review and continuation

Adversarial dispositions:

- UPHELD and repaired: a 5,000-digit JSON integer originally escaped the JSON
  error handler. The Python integer guard remains enabled; this input now
  yields REJECTED with scientific HOLD and is a regression case.
- UPHELD and repaired: replay originally required identical optional symlink
  privilege. Only that optional case/skip is now normalized, preserving all
  required cases and source hashes.
- DISMISSED within scope: a complete manifest might be mistaken for calibrated
  evidence. Every receipt keeps all scientific/publication flags false and
  labels semantic content, locator resolution and authenticity unevaluated.
- DISMISSED within scope: the owner must derive our theoretical correction or
  release every raw point. The request accepts existing records and partial
  replies, while theoretical mapping and error obligations remain ours.
- UPHELD as an excluded stronger claim: mocked reparse detection is not an
  empirical Windows symlink test or protection against concurrent path races.
  The host privilege skip and quiescent-directory requirement remain explicit.

No sign, factor, units or limiting-regime calculation is performed here. Hashes
are input integrity checks, not numerical physics claims. Test counts are
computed from executed cases, not inserted as scientific constants. External
operational review is welcome; the two in-session reviewers are not external
scientific peer review.

Tooling review covers malformed JSON, strict nested keys, altered model/time/
role, reference mistakes, missing data, hash tampering and unsafe local paths.
The exact cases and skipped host-capability tests are in the run JSON. Review
dispositions are in `TECT-CLK-006-review-v1.json`. No Lean proof is asserted:
Lean cannot establish the availability, authenticity or empirical coverage
of an unsupplied archival record. No new proof-note PDF is warranted; existing
fresh-PDF gates remain mandatory at release.

After this preparation, the one next action is obtaining an actual archived
analysis response, if the operator chooses to send the draft. Sending needs
separate instruction. A new scientific review requires substantive new,
owner-auditable estimator/projection/calibration/error evidence or an exact
source-audit correction, with a bounded question and explicit remaining
researcher inputs. A differently formatted copy of already audited evidence,
a newer receipt date, or completion of this manifest alone does not reopen
the route. No claim is made about physical Pre-A, Sector A/B, spacetime,
QFT, gravity, a continuum limit, a horizon, mass gap or TOE.
