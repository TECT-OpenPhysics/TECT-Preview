# TECT-CLK-003: bounded source intake and continuity checkpoint

## Decision and scope

The frozen CLK-002 model is unchanged. This is an **auxiliary source intake**,
not a new proof attempt. Empirical admission remains **HOLD_FOR_EVIDENCE**.
Seven primary-source files were acquired as actual bytes and pinned in
`TECT-CLK-003-intake-v1.json`. Full third-party PDFs remain in an ignored cache;
the public packet contains source URLs, hashes, locators and limited factual
inputs. Independently prompted clock and free-fall audits inspected their
respective papers; the integration owner also rendered the formula, material,
calibration and NAVEX pages before recording this synthesis.

## Same-source comparison

The solar Guena Rb/Cs coefficient is not an Earth observable. MICROSCOPE's
Sun-synchronous orbit does not make its Earth Ti/Pt measurement Sun-directed.
Their combination is rejected for this frozen comparison.

NAVEX supplies a genuine Earth-orbit Rb/Cs lead. Its flight RFS-CFS comparison
does not, by itself, supply a calibrated radial log-frequency-ratio gradient.
The paper describes incomplete temperature corrections, thermal lag, and
unresolved orientation/orbit residuals. Pairing it with MICROSCOPE therefore
fixes the named source only, not spatial transport, normalization or errors.
Different epochs are not intrinsically forbidden by the static benchmark,
but their transport/calibration contract must actually be supplied.

The two conversions that must not be erased are

\[
z=b_S\,g_U/\bar g,\qquad
\eta=\delta/\overline{(m_g/m_i)}.
\]

Neither denominator ratio has been set to one. The paper's asymptotic order
statement about delta/eta is not a certified numerical remainder over the
CLK-002 parameter domain. Likewise a first-order solar eccentricity template
is not a bound on nonlinear scalar/material or post-Newtonian corrections.

## What is acquired, and what is not

The source packet preserves reported clock and free-fall aggregate values,
then-current fountain corrections, actual alloy mass fractions, a Pt isotope
table, and selected instrument calibration values. Each has a precise source
locator and role. Published segment and systematic tables remain available at
their pinned PDF locators; no covariance is inferred from the diagonal errors.

The Pt table header and its near-unit sum require a convention clarification;
no renormalization was performed. Approximate primed dilaton charges are not
substitutes for full electromagnetic charges. The rounded electronic clock
contrast is not a certified total atomic/nuclear sensitivity.

The MICROSCOPE public portal is reported by the mission, but bounded access
attempts timed out; raw schema, masks and covariance were not inspected.
Author MECM software is acquired, but its synthetic example is not flight data.
This is an access boundary, not a claim that the data do not exist.

Every missing field is explicitly null, with its owner and required input.
The current scalar benchmark is conditional; no likelihood, exclusion,
parameter estimate or prospective success is reported. All exposed publications
are retrospective. SUREF is an instrument control, not an automatic theory
holdout. A new custodian-controlled batch must be assigned before disclosure.

## One next evidence request

Supply a calibrated **Earth-sourced 87Rb/133Cs radial ratio-response packet**:
time tags and units, position/potential/ephemeris data, raw and corrected ratio
series, validity masks, correction pipeline version, nuisance parameters and
full covariance, total EM sensitivity with nuclear uncertainties, a shared
Earth-to-TiAlV/PtRh normalization/transport contract and bounded finite-response
errors. Identify calibration versus untouched validation batches and the
custodian's exposure history. Separate bounded systematics from stochastic
covariance. This request is prepared, not sent; no external person was contacted.
It is a necessary entry point, not a promise that it alone supplies every other
missing free-fall/theory input listed in the manifest.

## Adversarial review

- **UPHELD:** Same source name alone is not a common observable. Keep the Earth
  pair on hold until the estimator and transport contract are provided.
- **UPHELD:** Unknown covariance cannot become zero, and bounded systematics
  cannot silently become Gaussian errors. No combined significance is computed.
- **UPHELD:** Material normalization, total sensitivities and finite-field
  remainders remain unsupplied. Do not hide them in a fitted coupling.
- **DISMISSED by explicit role separation:** Neither old data nor a synthetic
  software example receives prospective prediction credit.
- **DISMISSED by source preservation:** No PAH model, time, carrier or CLK-002
  preregistration is altered; no Sr or other species substitution occurs.

Independent review here means a separately prompted AI audit, not independent
experimental replication or external-person certification. Lean is not a
verifier of source availability, covariance completeness or queue disposition.
The existing seven CLK-002 algebra declarations remain limited to their
conditional first-response statements; no new physical theorem is asserted.

## Operational repair, separately scoped

`CONT-20260928-recovery-v1.json` proves the five old queued Q3LOCK requests have
their support bytes and complete canonical exploration lines in integrated
ancestor commits. They were archived without deletion or re-execution, under
operator-side locks, with all hashes retained. The watcher did not drain those
exact requests. The completion snapshot is refreshed from live authority
counts; all non-checkpoint programme methods, immutable pointers and prior
completion evidence remain unchanged. Strict continuity is checked separately
after the release-gated integration and push; a source audit cannot stand in
for that live check.

The preceding GitHub Pages run (36384572126 at baseline b1aace18) failed four
release consumers because a fresh checkout lacked historical ignored-path
evidence, although its exact-byte archive was tracked. Both CI workflows now
run the existing `portable_evidence.py --restore` before their first consumer.
This restores only missing hash-matching files, refuses differing targets,
does not generate new evidence, and leaves all release checks mandatory.
`test_ci_evidence_bootstrap.py` checks ordering; the existing lane-controller
tests check exact restoration, idempotence and corruption refusal. Actual
deployment success is verified against the new remote commit, not inferred
from this configuration edit.

## Reproduction and stop rule

```
python -X utf8 verification/scripts/tect_clk003_verify.py --check
python -X utf8 verification/scripts/verify_continuity_recovery.py
python -X utf8 verification/scripts/check_research_continuity.py --self-test
python -X utf8 verification/scripts/check_research_continuity.py --strict-baseline
```

The final command belongs in the clean, pushed canonical main checkout only.
Source bytes can be rechecked with `tect_clk003_verify.py --source-cache PATH`;
PATH contains `sources/` and `freefall-sources/` and is never a public authority.
Without that option, the verifier checks the frozen acquisition receipt, not a
new network download. Stop after this checkpoint. Re-enter only with actual
new input bytes or an exact audit error. No physical Pre-A, spacetime, gravity,
QFT, continuum, mass-gap, TOE, geometry or A/B gate conclusion follows.
