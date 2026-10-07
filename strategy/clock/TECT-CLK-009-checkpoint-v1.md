# GREAT processing response evidence and remaining input

TECT-CLK-009, 2026-10-07 UTC. Classification: **auxiliary_support**;
scientific verdict: **HOLD_FOR_EVIDENCE**. The active goal is not complete.
The frozen CLK002 model, physical time, old Rb/Cs contract and T-054 gate are
unchanged. No numerical retained response or error envelope is asserted.

## What the new sources establish

The source manifest pins the original bytes and exact page locators. The
new evidence changes the next action from generic processing discovery to
a focused request for historical campaign provenance and combined response.

| Source | Established content | Limit on reuse |
|---|---|---|
| NAPEOS2009, pp.78-79 | Coupled global/epoch normal equations and epoch elimination | Generic algorithm, not the actual GREAT configuration |
| UPC2021, pp.817-818,820 | Product lineage, ambiguity selection and second-stage clock estimation; explicit radial orbit-clock correlation | Alternative estimator conditional on previous orbit/slow-parameter products |
| Finke2023, printed pp.89,91,105-119,140 | SRP-only orbit sensitivity study; actual postproduct clock processing and revised systematic analysis | Not a full historical implementation or fixed-scalar response |
| Herrmann2018, PDF3 | Nonzero-alpha clock-data injection and modeled-noise tests | Existing postproduct phenomenological template, not full clock-plus-force propagation |
| Delva2018, PDF2-5 | Primary gravitational-only estimator and published uncertainty method | Its alpha is not the differently defined ZARM alpha |

UPC2021 describes repro3 as the penultimate ESOC GREAT product. Its repro4
comparison uses BRUX during2017, while its own second-stage clock datum is
CEBR. The previously acquired repro3 day names TWTF. These are not freely
interchangeable references. The exact final Delva2018 file/campaign mapping
has not been supplied. Finke2023 is a later analysis, not a retroactive byte
specification of either2018 implementation.

## Why the actual response is still required

NAPEOS Eq.6.41 has global parameters x and epoch parameters c_i with blocks
A,C_i,D_i and right-hand sides a,b_i:

\[
 A x+\sum_i C_i^T c_i=a,\qquad C_i x+D_i c_i=b_i.
\]

With invertible D_i, elimination yields

\[
 (A-\sum_i C_i^T D_i^{-1}C_i)x
   =a-\sum_i C_i^T D_i^{-1}b_i.
\]

This is an interpretation of the source's coupled equations, not a new
mission-response theorem. The printed reduced RHS below Eq.6.42 lacks the
cross-block transpose factor. It must not be imported literally. The source
does not provide the actual campaign blocks or show that they decouple.

Likewise, UPC's second-stage input orbit is fixed for that stage, but depends
on the preceding estimation. The authors explicitly discuss orbit-clock
correlation. Setting the first-stage force response to zero would therefore
be an extra assumption, not a consequence of the method.

Finke's Eq.4.34 specifies a GLS estimator with an AR1 covariance estimated
from residuals. Actual selected epochs, daily covariance realizations,
design matrices or the exact code to regenerate them are still required.
Clipping, ambiguity selection and data-dependent weights may change under
a perturbation; a frozen-branch derivative needs a stability domain or a
bound accounting for branch changes. Existing clock-data-only injection
checks (including Herrmann's combined gravitational/Doppler template) do not
establish these properties for the combined fixed CLK002 signal.

## Source transcription and error safeguards

Finke printed p.119 defines V as the inverse sum of inverse variances, but
Eq.4.35 divides the weighted numerator by V. Taken together literally, a
single sample would not return itself and uniform rescaling of its uncertainty
would change its mean. The stated inverse-variance-mean interpretation requires
normalization instead. This is an inconsistency in the printed expressions;
the implementation is unknown. It does not show that the experiment's code
or published result used the inconsistent expression. Because alpha is
dimensionless, an SI-dimension contradiction is not claimed.

Finke printed p.140 revises a magnetic-systematic range relative to the2018
analysis. This reinforces the need to pin the uncertainty version and template.
Neither version supplies an error envelope for the full CLK002 perturbation.
Reported standard uncertainties and typical performance are not deterministic
worst-case bounds; a statistical certificate must instead state its coverage
assumptions. The new audit does not choose whichever uncertainty is smallest.

## Minimum sufficient delivery

The one missing input is a campaign-identified, owner-auditable **combined
CLK002 response at the final estimator with its justified error envelope**.
Two delivery routes remain admissible:

1. Actual data/configuration/code sufficient to reproduce the historical
   clock/orbit solution, selection, calibration and final estimator, then
   derive and independently check the combined response and remainder.
2. A source-validated compressed response and projected-error certificate
   for that same full perturbation, with stated domain and coverage. A full
   normal matrix is not mandatory if this sufficient alternative exists.

Final product hashes, datum/GM treatment, masks, priors, weights and correction
conventions are applicability requirements, not optional decorations. Absolute
atomic/material inputs and physical-model remainder obligations are separate
from obtaining the processing response. A single-arc validation cannot be
silently promoted to a full-campaign response.

The unsent request asks first about archival availability and provenance;
it does not ask an owner to endorse TECT or silently require a new calculation.
External sending needs explicit operator authority and truthful reply identity.

## Independent and hostile review

Three read-only reviewers checked the owner-source acquisition, Finke's exact
postprocessing definitions, and UPC/NAPEOS scope. The parent inspected the
core equation/table pages. These are in-session reviews, not external peer
review or an independent rerun of GREAT.

| Objection | Disposition |
|---|---|
| Free epoch clocks imply no orbit response | UPHELD against the shortcut; source cross-blocks remain |
| A reported injection test closes the full model | UPHELD against the shortcut; perturbation scope differs |
| repro3, repro4, UPC and ZARM outputs can be pooled | UPHELD; campaign, datum and estimator remain distinct |
| Printed formula corrections reproduce actual code | UPHELD; implementation evidence is required |
| A source/hash verifier proves scientific sufficiency | DISMISSED; verifier reports provenance only |
| Missing delivered settings refute the model or experiment | DISMISSED; no such no-go is established |

No new Lean proof is appropriate for missing historical response data. Earlier
parameterized Lean identities remain scoped to their original algebra.
No new result ID, claim-card promotion or proof-note PDF is issued for this
source checkpoint. Existing release and fresh-PDF checks still apply.

## Reproduction and next action

```powershell
python -X utf8 verification/scripts/tect_clk009_sources.py --check
python -X utf8 verification/scripts/tect_clk009_sources.py --check --cache internal/clock
```

The first command checks protected repository bytes, pinned evidence metadata
and the stored receipt. The second additionally hashes the original cached
source bytes. Neither evaluates the physical response. Source downloads are
manual at the pinned public URLs; the checker performs no network access.

Next: obtain permission and reply identity for the one archived GSSC enquiry,
then a substantive owner reply/configuration/response certificate. Do not run
another unchanged archive scan, fit an arbitrary sinusoid or redefine the goal
as completion of this checkpoint. A new evidence packet triggers bounded
applicability and independent-response review, not automatic scientific success.

No physical Pre-A, Sector-A/B, spacetime, QFT, gravity, horizon, continuum,
mass gap or TOE conclusion follows.
