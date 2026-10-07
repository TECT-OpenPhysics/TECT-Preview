# Galileo clock response and joint free fall admission

Date: 2026-10-07 UTC. TECT-CLK-008 is one operator-authorized inverse-lane
checkpoint under the frozen CLK002 action. Its preregistration hash is
`a53797b3b5b3390d3942926530f07427972f9cd1728c0f2182442c283633a57d`.
The previous solar-estimator wait is paused, not discharged. The old Rb/Cs
contract and all protected files remain byte-identical.

## Decision and scope

**AUXILIARY_SUPPORT.** A conditional action-to-phase/orbit map is consistent,
and actual public Galileo products have been acquired. The acquired packet
is **not sufficient for a controlled joint empirical test** with Earth free
fall. This is an applicability judgment on these specific files, not a claim
that no public data exist or that the experiments are invalid. No forward
T-054 gate, claim tier or physical identification changes.

The unchanged model is an externally supplied 3+1 Einstein-frame, EM-only,
massless, unscreened scalar effective theory, with metric proper time. The
derivation retains the isolated static spherical weak-field source and
first-response approximation. Slow clocks can sample that background along
worldlines; this does not supply the actual perturbed Earth-satellite model.
There is no lattice, regulator removal, volume or continuum limit. Actual
multipoles, tides, propagation, atom/material errors and higher-order terms
remain obligations. No coupling is fitted and no retrospective data are
credited as a prospective holdout.

## Source applicability

`TECT-CLK-008-sources-v1.json` pins nine acquired sources by URL and SHA-256.
The CLK002 preregistration separately pins DD2010 and HEES2018. The source
checker verifies the actual cached bytes; the portable receipt is not a
substitute for those bytes when redoing source interpretation.

| Source and locator | Imported content | Hypothesis disposition |
|---|---|---|
| CLK002, HEES2018 Eqs1-2,7-8,14-19,29-38 | Action, phase rule, scalar background and mass response | SATISFIED as frozen conventions; physical validity and errors CONDITIONAL |
| DD2010 Eqs2-8,71-76 | Full mass charges and Newtonian force normalization | CONDITIONAL weak-field test bodies; no primed-charge substitution |
| HEES2015 PDF12 Eqs79-81; PDF15 Eq92; PDF16-17 Eqs99-101 | Absolute hyperfine factors differ from ratio sensitivities; general clock comparison needs more than one universal alpha | APPLIES to the distinction; its inverse-frequency/sign convention is not imported |
| DELVA2018 PDF2-5 Eqs2-6, TablesI-II | Gravitational anomaly template, daily affine nuisance, data selection and uncertainty method | APPLIES to the published analysis; fixed-scalar force response through the estimator UNASSESSED |
| HERRMANN2018 PDF2-3 Eqs3-6, TableI | Pre-applied eccentricity correction and a different anomaly template | APPLIES as an independent processing cross-check, not an interchangeable estimate |
| R3CLK/R3SP3/R3SRP/R3SLS | Actual clock/orbit/force/SLR-summary records | SATISFIED bounded byte/header/count checks; empirical sufficiency FAILED for this packet |
| UPCLINE/UPCTN | Alternative detrending-product caution | NOT ADOPTED; interpretation/reuse questions remain |

This is a model-specific crosswalk using known effective-theory mathematics,
not a claim of a new gravity theorem. The remaining proposition concerns
the fixed model's response through the real measurement estimator.

## Phase and observable map

Let `x=d^2`, `mu_star=G_star*M_E`, `U_star=mu_star/r>0`, and use full
electromagnetic mass sensitivities `q_E,q_O,q_A,q_B`. Define the absolute
proper-frequency sensitivity by the response law

\[
 \nu_H(\varphi)/\nu_{H0}=1+dK_H\varphi+\text{remainder},\qquad \nu_{H0}>0.
\]

This definition is meaningful also at `d=0`; it does not divide by zero.
`K_H` is symbolic, has no asserted sign, and is not the old Rb/Cs contrast.
The admitted packet does not contain a certified hydrogen atomic calculation.
Absolute hyperfine energies involve mass, electromagnetic and nuclear
factors; assigning 2 or 4 as an exact complete sensitivity is not authorized.

The preserved phase law is `dN_H=nu_H(varphi)d tau`. Combining
`varphi=-d*q_E*U_star/c^2` with the weak-field proper-time rate gives

\[
 \frac{dN_H}{\nu_{H0}dt}
 =1-\frac{v^2}{2c^2}-(1+xq_EK_H)\frac{U_\star}{c^2}+\mathcal R.
\]

This follows by multiplying the two first-order factors. Their product at
second weak-field order belongs to a remainder not bounded by this audit, not to an exact
finite-field prediction. The retained rational normalizations below are exact
only within this first-response model.

A one-way phase-locked photon comparator has the invariant frequency ratio

\[
 R_{e\to r}=\frac{\nu_e(\varphi_e)}{\nu_r(\varphi_r)}
 \frac{[-u_r^\mu k_\mu]_r}{[-u_e^\mu k_\mu]_e}.
\]

Normalize by the background transition-frequency ratio if defining a
fractional anomaly. The emitted photon is phase-locked to the emitting
clock; the receiver compares it with its own local transition. From the
frozen action, Maxwell's equation is
`nabla_mu[(1-d*varphi)F^(mu nu)]=0`. At leading geometric-optics order its
nonzero prefactor leaves the null principal symbol unchanged: use the
transverse polarization equation with `1-d*varphi>0`. Amplitude transport and
finite-bandwidth errors are not certified by this statement.

For identical stationary H clocks after propagation treatment, satellite
emission and ground reception give

\[
 y_{\rm grav}=(1+xq_EK_H)(U_{\star,g}-U_{\star,s})/c^2.
\]

For a different ground response `K_G`, the numerator instead is
`(1+x*q_E*K_G)*U_star,g-(1+x*q_E*K_H)*U_star,s`. Relative to an identical-H
pair this adds `x*q_E*(K_G-K_H)*U_star,g`. A constant frequency term becomes
linear accumulated phase and is removed only when it belongs to the actual
daily nuisance space. A variable term cannot be dropped for that reason.
Moving-clock synchronized rates also contain `(v_g^2-v_s^2)/(2c^2)`; an
uncorrected radio observable additionally includes light-time and Doppler
terms. These are distinct quantities.

## Conditional orbit calibration and free fall

The following is an explicit conditional normalization, not a claim about
the actual Galileo fitted Earth parameter. If an isolated central test-body
orbit with full bulk charge `q_O`, negligible recoil and compatible units
supplies `mu_O=mu_star*(1+x*q_E*q_O)`, then

\[
 \alpha_O=\frac{1+xq_EK_H}{1+xq_Eq_O}-1
          =\frac{(K_H-q_O)xq_E}{1+xq_Eq_O}.
\]

The subtraction of `q_O` is essential. It is not the hydrogen atom's mass
charge. An externally fixed, multi-body-inferred or jointly adjusted GM
requires its own calibration map. Different satellites may have different
bulk charges, so a published common-alpha fit needs a response-weight crosswalk.

For the preserved Earth free-fall normalization set
`DeltaQ=q_A-q_B`, `qbar=(q_A+q_B)/2`, `h=x*q_E`. Then

\[
 \eta=\frac{\Delta Q h}{1+\bar qh},\qquad
 [\Delta Q+(q_O-\bar q)\eta]\alpha_O-(K_H-q_O)\eta=0.
\]

Proof: the square bracket is
`DeltaQ*(1+q_O*h)/(1+qbar*h)`. Multiply by `alpha_O` and cancel the nonzero
denominators. No division by `DeltaQ`, `K_H-q_O`, `d` or `q_E` is needed.
The formula includes blind directions but does not identify the coupling
there. Algebra requires nonzero orbit/mean denominators; inward-positive
physical use also requires the individual acceleration factors positive,
`x>=0`, a positive photon kinetic factor and a justified weak-field domain.
Null satisfaction alone does not enforce these conditions.

With fixed charges, observed errors `da,de` change the null residual by

\[
 [\Delta Q+(q_O-\bar q)\eta]da
 +[(q_O-\bar q)\alpha_O-(K_H-q_O)]de
 +(q_O-\bar q)da\,de.
\]

The triangle inequality gives a conditional error envelope when actual error
bounds exist. This identity does not supply those bounds; uncertain charges,
calibration and theory remainders must additionally be propagated.

## Actual processing and independently testable residual

DELVA2018 estimates a potential-only anomaly after a GR proper-time baseline,
with daily offset/drift terms and correlated-noise treatment. HERRMANN2018
describes undoing an existing eccentricity correction before applying a
refined model; its principal anomaly coefficient includes kinetic effects.
The two templates and estimates must not be pooled by name alone.

Subtracting a specified GR baseline is not inherently circular. A separate
residual can retain an anomaly. Conversely, free epoch-wise clock estimates
and sensitivity to a phenomenological redshift violation do not establish
sensitivity to a model that also changes the force law. Scalar Earth
multipoles need not equal a common charge times the mass multipoles, and
Moon/Sun scalar responses do not follow from `q_E`.

Let `C` be the actual map from tracking observations to clock/orbit solutions,
including its adopted constants and constraints. The scalar prediction must
be passed through this same map and the same baseline subtraction and
selection. Only when a fixed or justified linearized response `P` and an
actual coefficient influence row `ell` are supplied can one use

\[
 r(x)=P[m_{\rm CLK002}(x)-m_{\rm baseline}]+e,\qquad
 \widehat\alpha(x)=\ell^T r(x).
\]

The vector `m` includes clock phase, orbital and signal-path response, not
just an added sinusoid. These formulas identify the required computation;
they do not assign an unknown transfer factor the value one. CLK005's generic
projection identity is reference-only and is not repeated as new evidence.

## Actual public product audit

The cached repro3 sample is 2016-05-29. The independently counted E18/E14 CLK
records each have 2880 epochs at 30 seconds; their one-value records supply
no individual sigma. The ground reference is TWTF. The corresponding SP3
contains 289 position/velocity epochs at 300 seconds in IGS14, GPS time.
Neither file supplies a full joint clock-orbit covariance. A validated
projected-error summary could suffice instead, but is not established here.
This audit does not convert SP3 velocities or construct an inertial template.

SRP explicitly maps E201 to E18 and E202 to E14. Cross-checking the paper's
clock intervals makes E18/GSAT0201 a PHM-B candidate, whereas E14/GSAT0202
on this date is RAFS and outside the PHM-only selection. This is interval
eligibility, not proof that every E18 sample survives the original mask.
The SLS file is a passage summary, not a sample-matched residual vector;
it contains no E18 passage on the selected day. Missing sigma or SLR samples
are not zero errors.

The UPC alternative is not merged into repro3. Its note describes restoring
a detrending model, but coefficient-label interpretation remains unresolved
against the supplied file. No column is silently swapped. The public FTP
delivery also conflicts with a Confidential checkbox in that note; its full
content stays local. No UPC clock series was fitted or used. Repro4's later
week is not treated as the original paper sample.

## Independent and hostile checks

The primary symbolic run has 13 checks; the independent Fraction program
does not import it. Its TEST_ONLY fixture yields `alpha=148/303`,
`eta=4/327` and zero null. Bare-GM, sign and wrong-denominator mutations
give nonzero residuals. A separate exact fixture satisfies the null with
negative inferred `d^2`, demonstrating why domain admission is independent.
No fixture is an observation. Five Lean declarations check parameterized
field identities, not the EFT reduction or mission processing.

Three separately prompted read-only reviewers examined source products,
theory and hostile cases. This is in-session independent verification, not
external peer review or experimental replication. External review is invited.

The legacy independent-receipt flag `constant_ground_only` names a sufficient
constant-frequency fixture, not a necessity theorem: a sampled nonconstant
term can still lie in the nuisance span or have zero estimator influence.
The primary symbolic substitutions cover blind directions; two tautological
Fraction zero checks are not credited as independent coverage of those cases.

Final hostile replay identified absolute checkout paths in the first Lean
receipt. That receipt and source remain unchanged. A separate portable
wrapper normalizes only exact source-path prefixes, retaining warning text
and the same pinned compiler, packages, source and theorem assumptions.

| Objection | Disposition |
|---|---|
| Absolute H response was replaced by the Rb/Cs contrast or a rounded integer | UPHELD against that shortcut; `K_H` remains an unprovided symbolic input |
| The fitted GM equals the ideal test-body calibration | UPHELD; the ideal identity is conditional and actual calibration remains unestablished |
| GR subtraction removes all independent signal | DISMISSED as a general assertion; the real retained response still requires proof |
| Same Earth removes ground-clock, material and orbital nuisances | UPHELD as an objection; removal requires explicit projection and error control |
| Any E14/E18 file or any published alpha can be pooled | UPHELD; clock identity, time, template and reference products are kept separate |
| Lean or exact fractions establish empirical sufficiency | DISMISSED; only the encoded algebra and local structure checks pass |
| A residual null identifies an admissible coupling | DISMISSED; blind directions, poles and `d^2>=0` are separate conditions |

## Reproduction and one next question

```powershell
python -X utf8 verification/scripts/tect_clk008_primary.py --check
python -X utf8 verification/scripts/tect_clk008_independent.py --check
python -X utf8 verification/scripts/tect_clk008_sources.py --check --cache internal/clock/clk008/sources
python -X utf8 verification/scripts/tect_clk008_lean_portable.py --check --lean-cache E:/Dev/TECT/verification/lean/.lake/packages
```

The source command requires separately acquired bytes at the manifest URLs;
the others replay the committed scoped evidence with the pinned dependencies.
The initial Lean default cache was absent; the explicit already-pinned shared
cache was used. A tactic normalization issue was repaired before issuing its
successful receipt. No theorem assumption or source hash was weakened.

The single next evidence question is: **Can the actual GREAT processing
configuration or a validated response/Jacobian establish the fixed CLK002
clock-plus-orbit signal retained by the selected estimator, with its GM,
ground reference, mask, nuisance projection and projected-error envelope?**

A supplied configuration may permit an injection/recovery audit on the real
estimator, not an arbitrary fitted sinusoid. This is the reentry condition;
there is zero automatic successor budget. Absolute atomic/material inputs
and finite-response/joint-coverage bounds remain downstream obligations even
after this processing question is answered.

No physical Pre-A, Sector-A/B, spacetime, QFT, gravity, horizon, continuum,
mass-gap or TOE conclusion follows. The boundary is not a refutation of
CLK002 or TECT.
