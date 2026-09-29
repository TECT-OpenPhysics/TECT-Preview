# TECT-CLK-005: operational potential calibration and error feasibility

Date: 2026-09-29 UTC. One bounded inverse-lane audit under DCTRL-000045.
Authorities: `TECT-CLK-005-prereg-v1.json`, the frozen
`TECT-CLK-005-calibration-contract-v1.json`, and
`TECT-CLK-005-assessment-v1.json`. Source IDs, exact SHA-256 values, URLs and
page/equation locators are in the assessment. This is a strategy checkpoint,
not a new scientific result card or a proof-note tier transition.

The original contract bytes are preserved. The separate
`TECT-CLK-005-moment-correction-v1.json` supersedes only its moment-tail clause:
hostile review caught the degenerate `V=0` exception to the original
non-strict-tail notation. All fixture inputs and the physical model are intact.

## Decision and exact scope

**AUXILIARY_SUPPORT; empirical admission HOLD_FOR_EVIDENCE.** The reviewed
primary sources establish the sign convention and conditional pair-gravity
law, and provide substantial conventional uncertainty analysis. They do not
establish the actual solar estimator's bare-to-operational calibration and a
coverage-qualified total error set for the frozen cross-source comparison.
This is not a finding that the experiments are invalid or that no owner data
exist. It is a bounded applicability judgment on the acquired sources.

CLK002's hypothetical EM-only massless unscreened static first-response model
is unchanged. Its imported 3+1 metric spacetime, proper time, Rb87/Cs133 ratio,
full material sensitivities and TiAlV/PtRh alloy pair remain fixed. The original
same-Earth comparison is unchanged. The solar/Earth alternative is **not
adopted**. No coupling was fitted; no lattice, volume or continuum limit was
taken. Keeping a Newtonian ratio denominator exact at fixed coupling does not
bound higher-order weak-field or nonlinear scalar effects.

## What the actual sources resolve

1. **Sign and harmonic:** GUENA2012 PDF3 explicitly uses positive
   `U=GM_sun/r`, maximal at perihelion. Its annual harmonic, phase and
   semiamplitude convention are identifiable. The frozen negative
   scalar-response sign is consistent. SYRTE2015 supplies the newer aggregate,
   not its complete sampled estimator/calibration law. Earlier conventions
   are context, not proof that the later design is identical.
2. **Bare versus operational potential:** DD2010 supplies pair coupling.
   BERNUS2023 PDF22 EqA29 and PDF23 measurable mass redefinitions distinguish
   that coupling from fitted ephemeris parameters; PDF11 explains parameter
   re-adjustment. Those sources do not turn the published clock normalization
   into a measured bare solar parameter. PARK2021 is a calibration-method
   example, not a retroactively assigned clock ephemeris. IAU2015B3 nominal
   constants are exact conversion factors, not physical measurements.
3. **Time conventions:** KLIONER2007's compatible scalings of time, distance
   and mass parameter preserve `mu/r`. A lone time-scale multiplier is not a
   correction. The actual epoch scale, phase and binning still matter.
4. **Error meaning:** GUENA2014 documents temporally correlated systematics
   and a warning about a constant-frequency fit. That does not demonstrate
   annual bias. MICRO2022 and MICROANALYSIS2020 provide conditional calibration
   and error propagation; MECM2016 uses plug-in covariance and simulation
   checks. None supplies all the fixed-model theory/material error bounds.
   GUM2008 and VIM require a stated probability interpretation before a
   standard uncertainty becomes a coverage assertion. HEES2016's Bayesian
   sinusoidal power limit is not the signed solar estimator's error law.

No independent-replicate credit is assigned to overlapping clock data.
No raw mission series, full clock covariance or model-error certificate was
acquired. The manifest distinguishes unavailable inputs from proven absence.

## Estimator-aware correction: conditional exact derivation

Let `y` be the sampled fractional frequency ratio; let
`u=Delta U_used/c^2` and `v=Delta U_bare/c^2` use the same declared epochs,
time scale and binning. Let `Z` contain the owner's nuisance regressors and
let `W` be its fixed positive-definite weight matrix. Require full column rank
of `Z` and `[Z,u]`; define

\[
 P=I-Z(Z^TWZ)^{-1}Z^TW,\qquad H=u^TW P u>0,
 \qquad \ell^T=\frac{u^TWP}{H}.
\]

Weighted least squares first eliminates the nuisance coefficients by its
normal equations. Substitution gives `b_hat=ell^T y`. Direct multiplication
gives `P^2=P`, `PZ=0`, `P^TW=WP`, `ell^T u=1` and `ell^T Z=0`. Therefore,
for the **conditional first-response** model

\[
 y=-Kq_S x v+Za+r+\epsilon,\quad x=d^2,\qquad
 \widehat b=-Kq_Sx\,\gamma_{\rm eff}
              +\ell^Tr+\ell^T\epsilon,
 \quad \gamma_{\rm eff}=\ell^Tv.
\]

The sign follows the positive-potential convention. All quantities in this
regression are dimensionless; `ell` is a dimensionless influence row. Actual
masking, estimated weights and data selection need their own conditional or
uniform error argument; these fixed-design identities do not justify them.

If `v=gamma*u+Zc`, then `gamma_eff=gamma`. This is sufficient, not necessary:
the weaker condition `ell^T(v-gamma*u)=0` is enough for this coefficient.
For `v=gamma*u+Zc+r_v`, weighted Cauchy-Schwarz on `range(P)` gives

\[
 |\gamma_{\rm eff}-\gamma|
 =\frac{|(Pu)^TW(Pr_v)|}{H}
 \le\sqrt{\frac{r_v^TWP r_v}{H}}.
\]

Here `H=||Pu||_W^2`, and `r_v^TWP r_v=||Pr_v||_W^2`. Thus a certified
residualized template bound can suffice. No such bound for the actual2015
estimator is supplied by this audit. Template discrepancy must not also be
counted a second time in the remaining response error.

The familiar scalar shortcut is only a conditional reduction. If the measured
orbital template were exactly an isolated Newtonian Sun-Earth relative orbit,
then

\[
 \mu_{\rm pair}=G_*(M_S+M_E)(1+xq_Sq_E),\qquad
 \gamma=\frac{G_*M_S}{\mu_{\rm pair}}
 =\frac{M_S}{(M_S+M_E)(1+xq_Sq_E)}.
\]

If a source-only operational parameter has already removed recoil, the mass
fraction is absent. Neither formula identifies a GR-fitted ephemeris or the
clock paper's printed normalization; coordinate matching and the attractive,
nonsingular fixed-model validity domain remain assumptions.

## What is required for a guaranteed error set

For fixed `ell` and an actual covariance `Sigma`,
`Var(b_hat)=ell^T Sigma ell`. If actual pointwise remainder bounds are
`|r_i|<=rho_i`, then `|ell^T r|<=sum |ell_i|rho_i` by the triangle inequality.
Neither the covariance nor these bounds is supplied merely by a quoted
standard deviation or a good fit.

A nuisance in `range(Z)` is projected out. By contrast an error `B*u` shifts
the annual coefficient by `B` while leaving the full fitted residual exactly
unchanged, since `[Z,u]` contains `u`. This is an algebraic non-implication,
**not evidence of a real annual systematic**.

Choose a single coverage interpretation: either a sampling guarantee uniform
over the admitted nuisance/model domain, or an explicit coherent joint
epistemic probability model. With valid marginal failure probabilities
`alpha_i`, the union bound gives joint coverage at least `1-sum alpha_i`
without cross-probe independence. It does not create the missing marginal
guarantees. If a zero-mean error has certified second moment at most `V`,
Markov's inequality applied to its square gives the Chebyshev radius
`sqrt(V/alpha)` for `V>0, 0<alpha<1`. For `V=0`, the error is zero almost surely.
In both cases `P(|e|>sqrt(V/alpha))<=alpha`; the strict inequality matters at
zero variance. Add an independently justified bias/remainder bound. A
plug-in standard uncertainty is not automatically a certified moment bound.

For freefall preserve the exact conversion
`eta=delta_x/(ac11*mbar)`. A specification envelope for `ac11` is not a
probability law, and `ad11` is a different parameter. If an independently
justified positive scale interval `a in [a_min,a_max]`, bias bound `B`, and
noise radius `r_alpha` apply to `delta_hat_x=a*eta+bias+epsilon`, then

\[
 C_\eta=\{\eta:\exists a\in[a_{\min},a_{\max}],\quad
 |\widehat\delta_x-a\eta|\le B+r_\alpha\}
\]

has the stipulated coverage on the event where its calibration and noise
guarantees hold: insert the true `a` and use the triangle inequality.
Uncertain calibration events enter the same probability budget. This does
not license treating the printed systematic1sigma as `B`, or instrumental
quadratic-response estimates as the scalar theory's nonlinear remainder.

## Reproduction and verification boundary

```powershell
python -X utf8 verification/scripts/tect_clk005_verify.py --check
python -X utf8 verification/scripts/tect_clk005_verify.py --check --source-cache internal/clock
python -X utf8 verification/scripts/tect_clk005_independent.py
```

The first command replays exact TEST_ONLY fixtures, role guards and the
immutable run receipt. The second also checks actual source-cache bytes
against fifteen pinned source hashes. The caches are ignored research intake,
not bundled full-text publications; their public acquisition URLs are in the
assessment. A fresh checkout can run the first command without the caches.

The registered fixture produces `ell=[5/157,27/314,-27/157,-29/157,60/157,-45/314]`.
The template distortion changes `gamma_eff` from `2/3` to `709/942`. Covariance
examples with the same unit diagonal give coefficient variances
`11767/49298`, `0`, and `1`; the latter two are legitimate singular PSD
examples, not actual covariance estimates. A discrete mean-zero, unit-variance
error has coverage `8/9` inside `[-2,2]`, so variance alone does not imply95%
coverage. These are computed test outputs, not physical data or new carriers.

Independent Fraction normal-equation elimination, without importing the
primary SymPy implementation, reproduces the fixture. Source reviewers check
the three distinct theory/clock/freefall roles. The review JSON records exact
hashes, results and limits. The twenty-one selected hostile role mutations
test particular forbidden promotions; they are not exhaustive security or
statistical validation. No new Lean result is claimed: source availability,
experimental probability assumptions and PDF interpretation are not formalized.
The general identities above have ordinary written proofs; fixture PASS is
not substituted for them or for empirical calibration.

## Devil's-advocate review

- **Wrong sign, annual factor or potential units?** DISMISSED for the stated
  convention: positive `GM/r`, semiamplitude rather than peak-to-peak, and
  both templates divided by `c^2`. Actual2015 design remains missing.
- **A GM ratio alone calibrates the measurement?** UPHELD as an objection to
  that shortcut: the estimator and ephemeris mapping must be supplied.
- **Correlated uncertainty necessarily contaminates the annual coefficient?**
  DISMISSED: nuisance-aligned errors cancel. Only their actual annual
  projection matters; the2014 constant-fit warning is not an annual diagnosis.
- **Gaussian residuals or two standard deviations guarantee the requested
  total coverage?** UPHELD as an objection to automatic promotion. Model,
  selection, covariance and bias assumptions remain explicit.
- **No joint covariance forces acquisition of every raw measurement?**
  DISMISSED as a necessity: auditable sufficient statistics/projected error
  can suffice, and justified marginal sets admit a conservative union bound.
- **Exact finite fixture closes the physical comparison?** DISMISSED: all
  empirical calibration/material/remainder inputs stay null. No exclusion,
  detection, independent holdout or scientific gate transition follows.
- **The original moment-tail formula also covers zero variance?** UPHELD:
  its non-strict event has probability one at zero. The hash-pinned addendum
  corrects the clause without changing original bytes; the verifier explicitly
  tests this degenerate boundary. It is an audit repair, not empirical evidence.
- **New laws or a re-fitted ephemeris were smuggled in?** DISMISSED: all new
  sources are applicability context; the protected CLK002 authorities and
  original comparison bytes are unchanged. Independent external review is
  invited, particularly on estimator reconstruction and coverage semantics.

## One next evidence target and reentry condition

The next question is whether a **new owner-auditable2015 annual projection
packet** supplies `u,Z,W` or equivalent sufficient influence/Gram statistics,
the accepted mask/binning/time/phase/normalization, and a fixed-model `v(x)` or
residualized calibration bound with total projected error and a declared
coverage interpretation over a declared coupling domain.

Such a packet need not contain every raw datum. It also would not by itself
close freefall normalization/error, full atomic and composition sensitivities,
or higher-order response bounds. These remain explicit downstream inputs.

The single admitted attempt is spent. Issue REVIEW_REQUIRED and record an
explicit PARK_OR_BLOCK review for this unchanged evidence target, with zero
automatic follow-on budget. Reopen only on that new auditable input or an
exact source-audit correction and a new bounded review. This routing decision
does not change T-054's forward gate or forbid independent mainline evidence.

No physical Pre-A, A/B, spacetime, QFT, GR, horizon, continuum, mass gap or TOE
conclusion is asserted.
