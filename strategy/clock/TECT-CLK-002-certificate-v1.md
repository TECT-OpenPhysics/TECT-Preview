# TECT-CLK-002: source-calibrated clock/free-fall comparison

Date: 2026-09-28. Status: conditional effective-response audit, not a new
microscopic TECT theorem. The immutable preregistration is
`TECT-CLK-002-prereg-v1.json` (SHA-256
`eed93e6aa01b4bacc780bba0a24f53ccf7c6b7f6daab394ae20e54afa270c92f`).
The integrated assessment and run JSONs determine execution status.

## 1. Question and external-source crosswalk

Can a single hypothetical scalar coupling supply a falsifiable relation
between an atomic clock ratio gradient and composition-dependent free fall?
This is a new explicitly authorized comparison hypothesis, not a repair of
the absent A2 clock map. PAH-v1/v2, R-574, A2 and CLK-001 remain unchanged.

The candidate restricts the low-energy scalar EFT to its linear electromagnetic
coupling. All other low-energy dilaton coefficients are zero in the declared
matching convention. This is not a universal mass-rescaling model. The metric,
proper time and Standard Model matter are inputs, not outputs of TECT.

Primary sources (exact bytes and URLs are in the preregistration):

| Source | Exact locator (PDF pages are zero-based here) | Import and disposition |
|---|---|---|
| Damour--Donoghue, arXiv:1007.2792v2 | pages 3-4, equations (2)-(8); pages 21-22, (71)-(76) | CONDITIONAL: scalar charge and Newtonian force law, including the Eotvos denominator and FULL electromagnetic charge |
| Hees et al., arXiv:1807.04512v3 | page 1, (1),(2a); pages 2-4, (7)-(21); page 6, (29)-(38) | CONDITIONAL: action, proper-time matter coupling, clock response and static massless source restriction; no oscillatory background |
| Guena et al., arXiv:1205.4235 | pages 1-3, (2)-(4), Tables I-II | RETROSPECTIVE DESIGN: Rb/Cs is an actual ratio observable; its rounded -0.49 electromagnetic coefficient is not an exact physical input |

The first two source imports require a weak, externally prescribed spherical
source, weak self-gravity, slow test bodies, an unscreened massless scalar and
stationary differentiable atomic readout near the asymptotic background.
These hypotheses are CONDITIONAL, not proved for a TECT source. The specified
signature and scalar normalization are SATISFIED by the declared convention;
atomic/nuclear uncertainty and finite-field remainders are UNASSESSED.

The active approximation is the Newtonian first-response model. Its ratios
are evaluated exactly, but this does not make the underlying approximation
an all-orders field theory. This is the weak-potential expansion at fixed d,
not a truncation of every observable at order d^2; the retained denominator
is the ratio of the two retained accelerations. Work only in a weak-field, adiabatic neighborhood
where the photon kinetic factor `1-d*varphi` stays positive and the effective
description applies. The large-coupling saturation below is an algebraic
boundary, not an authorized physical extrapolation. Coordinate radius and
proper distance, and coordinate and operational acceleration, coincide only
to the stated approximation. Their finite-order corrections remain missing.

For intended inward-positive accelerations require both individual factors
`1+qA*qS*d^2` and `1+qB*qS*d^2` positive, not merely their mean. The rational
identities themselves need only a nonzero denominator.

The exact reduction of the full interacting SM to all material sensitivities
with certified error is NOT imported. Instead, the differentiable first
responses are explicitly inherited assumptions. In particular, Guena's
formula also contains the nuclear magnetic-moment ratio. Fixing the other
varying-constant directions is not a proof that every electromagnetic
correction to that ratio is zero. Therefore the total contrast K remains
symbolic. The value -0.49 is approximate context and is not used in any
numerical fit, test oracle, or exact-physical assertion.

Full mass sensitivity Q and clock sensitivity K are different derivatives.
The primed electromagnetic composition charge in Hees is not the full source
charge. Using it alone while keeping other couplings zero changes the model.
A macroscopic mixture needs mass-fraction weights, isotopic/alloy composition,
and treatment of binding energy; element labels alone do not supply them.

## 2. Operational normalization and the conditional joint identity

Let r increase outward and aA,aB denote inward-positive free-fall accelerations
at the same location with the same source component. Let c be the light-speed
unit conversion inherited from the external model, d its one coupling, and
qS,qA,qB full electromagnetic mass sensitivities. K is the total derivative
of the dimensionless clock ratio with respect to ln(alpha_EM).

Set qbar=(qA+qB)/2, DeltaQ=qA-qB and gstar=Gstar*M/r^2. The frozen primitive
response definitions are

```text
varphi = -d*qS*Gstar*M/(r*c^2)
partial_r ln(nuI/nuJ) = K*d*partial_r varphi
aA = gstar*(1+qA*qS*d^2)
aB = gstar*(1+qB*qS*d^2)
gbar = (aA+aB)/2
z = -c^2*partial_r ln(nuI/nuJ)/gbar
eta = (aA-aB)/gbar.
```

These are dimensionless z and eta: c^2 times an inverse length is an
acceleration. z is NOT the usual bare-potential redshift coefficient, and
nuI/nuJ is a co-located ratio, not a relaxation rate or a single-species clock.
The same actual mean acceleration gbar is essential; an unrelated gravimeter
can have a different scalar charge.

Differentiate varphi: its outward derivative equals +d*qS*gstar/c^2;
the differentiation introduces a plus sign, but its value follows d*qS.
Summing the two accelerations gives gbar=gstar*D, with

```text
D = 1+qbar*qS*d^2 > 0,
C = qS*d^2/D,
z = -K*C,
eta = DeltaQ*C.
```

Consequently **DeltaQ*z + K*eta = 0** for this frozen response model. The
derivation does not divide by K, DeltaQ, d or qS, so the identity includes
zero-contrast cases without falsely identifying the coupling there. It also
retains the Eotvos denominator and cancels the bare GM nuisance using one
common operational normalization. A clock calibration can therefore predict
a free-fall response conditionally, if DeltaQ and K are independently fixed;
the two measured observables cannot be tuned independently in this candidate.

This is standard EFT response algebra combined with an explicit calibration
contract, not a claimed novel gravity theorem. It is distinct from CLK-001's
clock-only factorization criterion because a force-law response is involved.

## 3. Inverse image, blindness and conditioning

For fixed qS>0 and qbar>=0 put u=d^2>=0. The map

```text
C(u) = qS*u/(1+qbar*qS*u)
C'(u) = qS/(1+qbar*qS*u)^2 > 0
u(C) = C/[qS*(1-qbar*C)]
```

is injective on nonnegative u, with image C>=0 and 1-qbar*C>0. For qbar>0
this is C in [0,1/qbar); for qbar=0 it is [0,infinity). The formula and
positivity prove both necessity and sufficiency for the algebraic image.
One nonzero contrast recovers C; the other observable tests consistency.
The sign d versus -d remains unidentified by these observables. With qS=0
all signals vanish for arbitrary d, and if both contrasts vanish C cannot
be measured. Unknown source charge prevents the claimed recovery of d^2.
These are inverse-model boundaries, not uniqueness of a microscopic geometry.

Null closure alone is insufficient: z=K and eta=-DeltaQ satisfy the null but
infer C=-1 whenever K is nonzero, outside the stated positive-source image.
The executable implements this as a TEST_ONLY exact counterfixture.

For fixed qS,qbar and admissible C1,C2,

```text
u(C2)-u(C1) = (C2-C1)/[qS*(1-qbar*C1)*(1-qbar*C2)].
```

Thus qS>=s0>0 and both margins at least epsilon>0 give
`|Delta u| <= |Delta C|/(s0*epsilon^2)`. No uniform inverse stability holds
as source charge or a denominator margin tends to zero. Recovering u from
a clock requires division by K, so K near zero is another conditioning
boundary. This bound freezes the charges; it does not remove charge errors.

## 4. Uncertainty and empirical admission

Let z0,eta0,Q0,K0 be reported values with absolute errors ez,eeta,eQ,eK,
where Q0 denotes the contrast DeltaQ. If the true cross-probe residual is
bounded by emodel, a necessary consistency envelope is

```text
|Q0*z0 + K0*eta0| <=
 |Q0|*ez + |z0|*eQ + eQ*ez
 + |K0|*eeta + |eta0|*eK + eK*eeta + emodel.
```

This follows by expansion and the triangle inequality and does not assume
independent errors. It is a deterministic envelope, not a confidence level.
A statistical test needs the actual joint covariance and nuisance model.
Here emodel and the material-response errors are missing, not zero. For example,
L(varphi)=K*d*varphi+b*varphi^2 has L'(0)=K*d but adds
2*b*varphi*partial_r(varphi) to the finite-field log-ratio gradient.
This is an analytic counterexample to inference from a first derivative to a
finite-response bound, not an adopted second candidate. The executable hostile
fixture checks only a nonzero unbounded output remainder; it does not encode
this differentiation or establish the physical realizability of that remainder.

No parameter is fitted. No measured value is scored. No detection, survival
likelihood or empirical exclusion is produced. Guena's annual modulation is
Sun-sourced; MICROSCOPE is Earth-sourced; neither supplies the newly normalized
same-source (z,eta) pair. The previously exposed clock experiments are not
blind holdouts. A prospective holdout list is currently empty.

The single empirical reentry input is a **matched source/calibration/error
packet** defining (z,eta,K,DeltaQ,qS,qbar), with source component, observer,
distance/time conventions, material composition, uncertainties/covariance,
finite-response remainder and calibration-versus-withheld roles. Until then,
empirical admission remains HOLD_FOR_EVIDENCE. Do not repeat a scalar-owner
search or add a fitted parameter to avoid this condition.

## 5. A/B and existing-result crosswalk

| Authority | Disposition | Reason |
|---|---|---|
| A2 scalar gradient flow | DOES-NOT-APPLY as dynamics owner | Different fields, action, time and matter readout; no source map identifies them |
| A5 conditional composition | DOES-NOT-APPLY to close this candidate | Its pinned functional/domain/hypothesis branches are not this external EFT |
| B1/B2/B5 bounded comparison theorems | REFERENCE_ONLY | No identical functional, admissible states, normalization or vacuum comparison is supplied |
| B3 Reading-H ranking | REFERENCE_ONLY | No empty-reference sign, stability or physical BCC consequence |
| PAH-v1/v2 and R-574 | PROTECTED, NOT USED | Their definitions and scoped negative comparison remain unchanged |
| CLK-001 | RETAINED | Its absent A2 map is not retrospectively repaired by the new external assumption |

The useful inverse-lane output is a target constraint for a later genuine
TECT action-to-matter map. The benchmark is not an admitted microscopic
candidate under the full F_reg -> F_lim -> F_eff -> F_obs contract.

## 6. Adversarial and independent review

Separate read-only agents reviewed the source reduction and attacked the
normalization before implementation. They identified the Eotvos denominator,
primed/full charge trap, nuclear-g correction, different-source trap and the
coordinate/proper-distance boundary. Their recommendations are incorporated
as scope restrictions, not adjustments to the frozen candidate.

- **Sign/factor objection: DISMISSED in the response algebra.** Outward
  derivative and inward acceleration conventions give the displayed minus
  sign, and gbar supplies the exact factor of two.
- **Normalization objection: VALID-with-mitigation.** An unrelated gravimeter
  or bare GM calibration can break the null. Both observables explicitly use
  the same mean acceleration; this is not certified for an actual dataset.
- **Atomic/source identity objection: UPHELD for empirical admission.** Full
  charge, nuclear/atomic sensitivity uncertainty and actual mixtures remain
  required inputs. Rounded -0.49 is never treated as exact physical evidence.
- **Limit objection: UPHELD beyond the first-response scope.** No PN,
  finite-field, continuum or microscopic uniform estimate is supplied.
- **Hardcode objection: DISMISSED for derived outputs.** Symbolic derivations
  compute outputs; rational literals occur only in labelled TEST_ONLY fixtures.
- **Null-is-sufficient objection: DISMISSED.** The inverse image condition and
  zero-contrast cases are retained, with an explicit negative-C fixture.

Primary SymPy identities, a non-importing Fraction implementation, hostile
mutations and pinned Lean algebra are separate checks. Independent agent
review is not independent-person or community certification. External review
of the physical response reduction and covariance contract is invited.

## 7. Reproduction and stopping rule

```text
python -X utf8 verification/scripts/tect_clk002_verify.py --check --lean-cache E:/Dev/TECT/verification/lean/.lake/packages --elan-home C:/Users/NaEun/.elan
```

Optionally supply `--source-cache <directory>` containing the three filenames
from the preregistration to recheck exact primary PDF bytes. Public replay
without the cache checks the manifest and protected repository sources; it
does not falsely report re-downloading the papers. Source URLs, versions and
hashes are public; third-party PDFs remain an ignored local cache.

After this one assessment, no automatic successor. The conditional benchmark
can be admitted for testing without admitting it as physical TECT or counting
an empirical success. No mainline gate or claim tier changes. There is no new
R-result or physical no-go. The strategy certificate is the sole synthesis
for this auxiliary checkpoint; no intermediate proof-note PDF is issued.
