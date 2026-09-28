# TECT-CLK-004: active source discovery and calibrated comparison audit

Date: 2026-09-28 UTC. Task: T-054, protected inverse auxiliary lane.

## Decision and scope

Classification: **auxiliary_support**. Empirical admission remains
**HOLD_FOR_EVIDENCE**. The T-054 scientific gate is unchanged. This is new
source acquisition, an exact published-table crosswalk and a proposed
calibration-aware alternative, not another unchanged missing-owner replay.
The operator explicitly requested active search, connections and alternatives.
The preregistration bounded this turn to three source routes, one synthesis,
zero empirical fits and zero new models. CLK002/003 frozen bytes are preserved.

Authority: `TECT-CLK-004-assessment-v1.json`, with ten newly acquired source
hashes, the prior primary MICROSCOPE source hash, locators and printed inputs.
The companion review records three separately prompted read-only agent audits.
They are independent computational/source checks, not experimental replication
or outside peer review. No claim tier, result card or physical claim changes.

## Source-to-input applicability

| Source | Actual new input | Applicability and remaining boundary |
| --- | --- | --- |
| NTS-3 JNC2026 owner abstract, AFRL-2026-0283 | Rb/Cs spacecraft clocks, telemetry and altitude/thermal experiment lead | New Earth-source acquisition route; abstract is not simultaneous unsteered ratio data. Exact isotopes, readout and calibration are not supplied. |
| NAVEX DLR 1989, final 1990 report, 1991 translation, PTTI abstract | Later report locators and documented co-flight ratio context | Full report bodies not acquired. Translation is not independent data. Metadata/public-release status does not grant raw archive access. |
| MICROSCOPE processing paper, sections 5.1 and 5.2.3 | Mask convention and N0c/N2a product definitions | Applies to product interpretation, not unavailable time-series samples or their covariance. |
| Primary 2022 Tables 5, 7, 11 | Analysed windows, ADAM estimates, systematics | Applies to printed estimates; no raw-flight reanalysis or independent holdout. |
| Secondary 2025 Table II | Convenient reuse of nineteen published segments | Not an exact drop-in copy: value/window crosswalk discrepancies below. QCD axion dynamics are not imported. |
| Abgrall et al. 2015, section 5 | Owner solar Rb/Cs aggregate, (7.4 +/- 6.5) x 10^-7 | Solar potential response only. Overlapping earlier series are not independent replicates. No Earth substitution or averaging. |
| GPS Rb 2023, section 2/Table 2 | Active Rb clock method and orbit products | Does not supply a simultaneous Rb/Cs observable. |
| Source-charge paper, Appendix A | Composition-model lead | No numerical charge or uncertainty bound adopted. |

The official MICROSCOPE distribution portal timed out in this bounded round;
this is not evidence that public data do not exist. No owner was contacted,
restricted file purchased or access control bypassed. Acquired PDF pages were
rendered and visually checked where their equations/tables enter this audit.

## Exact published-table audit

All nineteen segments (eighteen sessions, with session 326 split) were checked
independently. The assessment retains both printed versions, without repair.
Units for estimates and errors are 10^-15. Primary/secondary statistical and
systematic entries agree for all nineteen rows.

* Segment 218: primary Table 7 ADAM estimate 6.7, secondary Table II 6.0;
  secondary minus primary is -0.7. The primary MECM column is not 6.0 either.
* With the secondary paper's stated 5946-second orbit convention, its durations
  correspond to 76.1, 92.8 and 40 orbits for 212, 358 and 438; primary Table 5
  analysed windows have 60, 92 and 32 orbits. The secondary values instead match
  full-session durations in primary Table 3. This is a window/scope mismatch,
  not a demonstrated random typo or a refutation of that paper's conclusion.
* Repeated estimates for 438 and 748 already occur in the primary table.
  They are preserved. Coincidence alone does not authorize deduplication.

The secondary summary is quarantined only as an unqualified exact input copy.
Neither paper's science has been refitted, invalidated or silently corrected.

## Product, sign and normalization crosswalk

SUEP inner mass 1 is PtRh and outer mass 2 is TiAlV. The calibrated N2a
half-difference is h=(Gamma_1-Gamma_2)/2. Thus the published full control
acceleration difference is Gamma_d=2h. These are electrostatic control
accelerations, opposite to free-fall acceleration. Primary 2022 Eq. (4)
already uses delta(2,1) in that measured control difference: do not insert a
second sign reversal. The fitted quantity is delta_x=ac11*delta(2,1), whereas
eta_TiPt=delta_x/(ac11*mbar), with mbar the mean gravitational/inertial mass
ratio. Neither factor may be set to one without an admitted calibration.
N2a common-mode control acceleration is not the physical gravitational gbar.

Mask 0 means excluded and 1 retained. The minimum useful raw-product unit is
one accepted SUEP segment with ancillary orbit/attitude/housekeeping, calibrated
N2a, mask, calibration matrix and noise/error products. These definitions make
an eventual acquisition actionable; they do not supply those absent products.

## Proposed cross-source alternative, not adopted

Keep CLK002's hypothetical effective action, species and time. A *different
observation contract* could use a solar clock slope and an Earth free-fall
contrast. This does not satisfy the original same-Earth contract by relabelling.
Define x=d^2, Delta=qTiAlV-qPtRh, qbar their mean, and full Earth/Sun charges
qE/qS. If b_obs uses an operational solar potential U_used, retain
gamma=dU_bare/dU_used; ephemeris GM is not automatically bare G times mass.
The conditional maps would be

    b_obs = -gamma*K*qS*x,
    etaE = Delta*qE*x/(1+qbar*qE*x).

For x>=0, qE!=0 and D=1+qbar*qE*x>0 they imply the necessary identity

    b_obs*(Delta-qbar*etaE) + gamma*K*(qS/qE)*etaE = 0.

Gamma may depend on x and requires a calibrated law, not a free fit parameter.
When the denominator is nonzero, the free-fall inverse is
x=etaE/[qE*(Delta-qbar*etaE)]. Its sign and D must still be checked.
Zero contrast, zero source charge, blind clock response and singular inverse
denominators must be handled using the primitive maps, not division by zero.
Residual zero is not sufficient for an admissible inverse image or detection.
Atomic response K, source charges and higher-response errors remain unbounded
inputs here. No empirical fit or adoption of this alternative has occurred.

A conservative uncertainty alternative is possible in principle: if each
owner/calibration supplies a marginal set C_i with certified coverage at least
1-alpha_i, then P(all true quantities in their C_i)>=1-sum(alpha_i), by applying
the union bound to their failure events. This needs no cross-probe independence
or cross-probe covariance. It does not remove within-probe calibration,
systematics, selection and theoretical-remainder coverage requirements.
Quoted plus/minus errors alone are not certified coverage sets. A nonempty
joint parameter pullback means compatibility, not confirmation; an empty one
is an exclusion only at the justified simultaneous coverage and model scope.

## Verification and adversarial review

Primary verifier: `verification/scripts/tect_clk004_verify.py`. Its run is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-28-tect-clk004/audit.json`.

* PASS: all cached source hashes and three protected authority hashes.
* PASS: nineteen-row exact rational arithmetic and window crosswalk.
* PASS: symbolic necessary residual; an explicitly TEST_ONLY rational fixture
  fails if gamma is omitted. Factor-two identity checked, not raw calibration.
* PASS: seventeen named hostile mutations are rejected. This is not exhaustive
  mutation coverage or automatic validation of arbitrary source text.
* Independent source audit: all nineteen tuples and the N2a/sign convention
  rechecked against separately rendered primary pages.
* Independent algebra audit: separate rational fixture plus six boundary cases;
  no blocking algebra/role defect found within the stated conditional scope.
* No new Lean theorem is claimed. Source transcription/access and error-law
  calibration are not established by Lean; the old CLK002 algebra is unchanged.

Devil's advocate:

1. UPHELD: two satellite clock types need not yield an admitted simultaneous
   ratio. Mitigation: NTS-3 remains an owner abstract/acquisition lead.
2. UPHELD: solar and Earth data cannot silently be paired under the old contract.
   Mitigation: explicit not-adopted proposal, gamma and charge ratio retained.
3. UPHELD: a copied value and whole-session duration can bias downstream reuse.
   Mitigation: both tables preserved, exact discrepancies exposed, no fit.
4. DISMISSED within stated scope: a missing 1/2 or second sign flip is required.
   Primary product/equation conventions give the crosswalk above; unknown scale
   and physical normalization remain unknown rather than fitted to agreement.
5. UPHELD: covariance-free does not mean error-free. Mitigation: only coverage-
   qualified marginal sets may enter; missing sets keep empirical admission held.
6. DISMISSED within audit scope: expected answers replace calculation. The script
   derives differences from separately stored inputs; literals asserting row IDs
   and differences are labelled independent visual test oracles, not estimators.

Reproduce the frozen arithmetic/receipt:

    python -X utf8 verification/scripts/tect_clk004_verify.py --check

Additionally verify acquired bytes when the local caches are available:

    python -X utf8 verification/scripts/tect_clk004_verify.py --check --source-cache internal/clock/clk004/sources --prior-source-cache internal/clock/clk003

The first command alone does not reacquire sources. Independent outside review
of the table locators, control/free-fall sign and gamma calibration is invited.

## Next evidence target and review condition

One bounded next feasibility task: determine from owner-defined potential/time
and error conventions whether the proposed solar/Earth comparison admits a
non-fitted gamma calibration law and coverage-qualified marginal sets. Preserve
the fixed model and old comparison. Derive a usable contract or identify one
specific missing calibration/coverage input; do not fit observations, adopt a
changed contract or repeat old owner-absence scans. Separately, the strongest
direct same-Earth acquisition lead is an actual NTS-3 unsteered ratio/telemetry
product or legally supplied NAVEX final report, not another abstract citation.

Review after one such feasibility attempt, or earlier if a source correction,
incompatible normalization or need for external communication arises. Contract
adoption requires an explicit separate decision. No automatic proof successor,
finite carrier, physical-empty/BCC calculation or model retuning is authorized.
No Pre-A, A/B, physical spacetime, QFT, GR, horizon, continuum, mass-gap or TOE
conclusion. No gate-level mathematical result arose, so this strategy synthesis
does not create a new proof-note PDF; existing release/PDF gates remain binding.
