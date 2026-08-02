# Boundary, Massless-Mode, and Criticality Research Seed

**Recorded:** 2026-08-02  
**Authority:** T0 research seed / strategy note only  
**Bears on:** C2-LORENTZ-EMERGENT, C6-SPACETIME-SIGNATURE,
D2-GAUGE-FORCING, E2-HBAR-ORIGIN, F1-COSMO-DARK-SECTOR

## 1. Motivating clue

The proposed clue is not a numerical coincidence between the SI value of the
speed of light and a material transition temperature.  It is the repeated
appearance of a structural boundary at which

1. massless or gapless degrees of freedom exist;
2. distinct modes share one limiting propagation speed;
3. a control parameter reaches a critical or self-dual locus; and
4. qualitatively new properties appear through collective order, topology, or
   gauge coupling.

The research question is whether these four features can arise from one
underlying mechanism rather than from unrelated inputs.  Superconductivity is
an experimentally accessible analogue because it exposes phase coherence,
flux quantisation, a gauge-field penetration scale, collective amplitude and
phase modes, and classical or quantum critical behaviour in the same system.
It is an analogue, not evidence that the physical vacuum is an ordinary
superconductor.

## 2. Unit-independent structural data

Raw dimensional values are not discovery targets.  In the modern SI, the
numerical values of `c`, `h`, and `e` define units; changing units changes their
displayed numbers.  Candidate structural information must therefore be an
exact relation, topology, scaling law, spectrum, or dimensionless invariant.

The initial comparison set is:

| Object | Structural role | What must be derived rather than inserted |
|---|---|---|
| `c_*` from the low-energy dispersion | Common causal or limiting cone | Equality of all relevant massless-mode speeds and `c_*=c` |
| `alpha = e^2/(4 pi epsilon_0 hbar c)` | Dimensionless electromagnetic coupling | Its value after an input freeze |
| `Phi_0 = h/q` | Phase-winding flux quantum | Compact phase, integer winding, and the charge unit `q` |
| `R_q = h/q^2` | Natural quantum impedance/resistance scale | Whether it is an exact fixed-point value or only a material-dependent scale |
| `kappa = lambda/xi` | Competition between gauge penetration and order-parameter coherence | The location and meaning of any self-dual boundary |
| `xi ~ |g-g_c|^-nu`, `tau ~ xi^z` | Static and dynamic critical scaling | The universality class and whether `z=1` |

For an ordinary charge-pair condensate, `q=2e` gives the familiar flux and
pair-resistance scales.  Those relations illustrate how global phase topology
can expose microscopic charge.  They do not by themselves derive `h`, `e`, or
the vacuum light cone.

## 3. Candidate structural hypotheses

### H1. Common-speed protection

If several gapless modes have exactly the same limiting speed, the equality
should be protected by a shared effective metric, an exact symmetry, or an
infrared renormalisation-group fixed point.  Accidental equality requiring
mode-by-mode tuning is not explanatory.  The decisive object is the complete
quadratic low-energy kinetic tensor, not a single fitted dispersion curve.

### H2. Critical activation of properties

At a phase boundary, the order parameter, correlation length, or topology can
change the excitation spectrum non-analytically in the thermodynamic limit.
Gauge coupling can convert a phase mode into a screened gauge response while
leaving other modes gapless.  The appearance of a new property is therefore
to be sought in a rank change, zero-mode crossing, topological-sector change,
or renormalisation-group fixed point, rather than described as an unexplained
instantaneous switch.

### H3. Topology before constants

The robust superconducting clue is integer phase winding.  A TECT analogue
should first derive a compact phase space and its allowed winding/defect
classes.  Only then may a relation analogous to `Phi_0=h/q` be used to infer a
charge or action scale.  Inserting `h` or `e` into the phase functional and
recovering the same constants is matching, not derivation.

### H4. Critical exponents connect space and time

The dynamic exponent `z` is a sharper discriminator than a transition
temperature.  A stable `z=1` fixed point is a candidate route to a common
space-time scaling and emergent Lorentz cone.  A value `z!=1`, dissipative
dynamics, or a preferred material rest frame shows that the superconducting
analogue does not supply a vacuum causal structure on its own.

## 4. Falsifier-first programme

1. **Define the boundary.** Specify the TECT control parameter and the two
   phases without using observational constants to choose the critical point.
2. **Derive both spectra.** Compute the full quadratic fluctuation operators on
   both sides and at the boundary, including all mixing blocks.
3. **Classify zero modes.** Separate symmetry, gauge, topological, and accidental
   zero modes; determine which remain physical after constraints.
4. **Test common velocity.** Extract every gapless dispersion
   `omega_a(k)=c_a |k|+...`; test whether all `c_a` coincide without separate
   tuning and whether the equality survives loop and regulator changes.
5. **Determine critical scaling.** Compute or bound `nu`, `z`, and relevant
   anomalous dimensions.  Test specifically whether a stable `z=1` fixed point
   exists.
6. **Derive winding data.** Establish compactness, integer winding, defect
   sectors, and any flux-like quantum before identifying `q`, `hbar`, or `e`.
7. **Freeze inputs and predict.** Only after the structural derivation, freeze
   inputs and compare dimensionless outputs such as `alpha` or mass ratios.

The route is falsified or narrowed if the common speed requires independent
tuning, if regulator removal splits the velocities, if no compact phase or
integer winding exists, if the proposed transition has the wrong zero-mode
count, if `z=1` is unstable, or if the target constants enter before the
prediction freeze.

## 5. TECT boundary and reuse rule

This note supplies no new TECT theorem, tier, vacuum selection, superconducting
prediction, or claim that space-time is a condensate.  It gives a reusable
question map.  Current C2 addresses a one-loop anisotropy sign within a legacy
chain; C6 has not derived the 3+1 Lorentzian signature; D2 has not completed the
physical gauge emergence; and E2 records only a T2 phase-transition programme
for `hbar` after negative classical routes.  The first legitimate advance is a
single model calculation that simultaneously exposes the zero-mode count,
kinetic tensor, winding topology, and dynamic exponent at a preregistered TECT
boundary.

## 6. External anchors

- BIPM, *SI defining constants*:
  https://www.bipm.org/en/measurement-units/si-defining-constants
- NIST, *2022 CODATA recommended values*:
  https://physics.nist.gov/cuu/pdf/wallet_2022.pdf
- Deaver and Fairbank, *Experimental Evidence for Quantized Flux in
  Superconducting Cylinders*, Phys. Rev. Lett. 7, 43 (1961):
  https://doi.org/10.1103/PhysRevLett.7.43
- Rosenstein and Li, *Ginzburg-Landau theory of type II superconductors in
  magnetic field*, Rev. Mod. Phys. 82, 109 (2010):
  https://doi.org/10.1103/RevModPhys.82.109

