# Pre-A Horizon-Origin and Dual-Lane Proof Programme

**Recorded:** 2026-08-03  
**Authority:** T0 strategy and new-candidate certificate only; no TECT action,
claim-tier change, physical-vacuum selection, event-horizon origin theorem, or
cyclic-cosmology theorem  
**Task:** T-054  
**Candidate:** `PA-M2-CI8-RS-v0`  
**Bears on:** T-053, A2-FULL-PRODUCTION-WELLPOSED,
C2-LORENTZ-EMERGENT, C6-SPACETIME-SIGNATURE, E2-HBAR-ORIGIN,
F1-COSMO-DARK-SECTOR, F3-INFLATION-CMB

## 1. Revised decision: origin before recurrence

This programme does not assume an eternal or self-explanatory cycle.  A return
map, if one is ever derived, would describe recurrence of already defined
physical data; it would not by itself explain why that state space, law, or
first admissible state exists.

The primary Pre-A question is instead:

> Can a declared causal null boundary and its physical state provide sufficient,
> constraint-compatible data for a unique high-energy bulk state whose later
> phase evolution can be tested by the same Lane-F and Lane-Q functional?

The word *event horizon* is not inserted as a conclusion.  An event horizon is
a global causal notion and cannot be identified before a space-time and its
causal domain are specified.  The proof programme therefore begins with a
candidate past null boundary `H^-`.  It must derive, rather than assume, whether
`H^-` has the global properties of an event horizon.

Unknown degrees of freedom beyond `H^-` are not set to zero.  They are outside
the theorem domain.  Any influence on the retained domain must be represented
by a declared boundary observable or channel.

## 2. Three-layer contract

The work is divided into three layers with no vocabulary-based inference.

1. **Lane H (horizon-origin):** specify the null geometry, boundary algebra and
   state, sufficient characteristic data, constraints, and a unique continuous
   reconstruction map to an interior high-energy state.
2. **Lane F (fluctuation/order):** determine whether one shared static
   functional has a stable inhomogeneous state below the identical zero
   reference and locate its exact onset boundary.
3. **Lane Q (quantum formation):** after separately declaring a real-time
   Hamiltonian, test whether scrambling exists, distinguish it from a linear
   instability, and ablate it before making a chaos-causes-order claim.

Lane H must output a state and parameter map that are legal inputs to both
Lane F and Lane Q.  A free-energy crossing is not chaos; polynomial or unstable
mode growth is not many-body chaos; and neither proves that a horizon created
the state.

## 3. First exact Lane-H obstruction and repair

### 3.1 A single null trace is not complete starting data

Use the local double-null toy equation

```text
partial_u partial_v phi = 0.
```

Both

```text
phi_1(u,v)=0,
phi_2(u,v)=u
```

solve the equation and obey the same trace on the null sheet `u=0`, namely
`phi_1(0,v)=phi_2(0,v)=0`, but they differ in the bulk.  Therefore a scalar
field trace on one characteristic sheet is not complete data for even this
minimal second-order hyperbolic problem.

This is a scoped exact no-uniqueness lemma.  It does not say that no horizon
algebra can determine a bulk.  It says that the phrase "the horizon state is
the start" is incomplete until the information content and reconstruction
theorem are stated.  In particular, a complete characteristic cone with a
regular vertex and all Einstein constraints can be sufficient; the
counterexample concerns a generic open null sheet carrying only a scalar
trace.

### 3.2 Minimal double-null repair in the toy problem

Give compatible traces

```text
phi(u,0)=A(u),
phi(0,v)=B(v),
A(0)=B(0).
```

Then the unique toy reconstruction is

```text
phi(u,v)=A(u)+B(v)-A(0).
```

The primary and independent scripts verify the equation and both traces.  In a
gravitational candidate, the analogue is not automatically this formula: one
typically needs data on intersecting null hypersurfaces, compatible corner
data, gauge fixing or quotienting, and all characteristic constraints.

### 3.3 Horizon-origin object to be constructed

The target is a declared tuple

```text
O_H = (H_1^-, H_2^-, C; A_H, omega_H; d_C; lambda_H),
```

where `H_1^-` and `H_2^-` are intersecting characteristic boundaries (or a
proved equivalent data system), `C` is their corner, `A_H` is the physical
boundary-observable algebra, `omega_H` is a positive normalized state, `d_C`
contains compatible corner/constraint data, and `lambda_H` contains declared
boundary control parameters.

The required bridge is

```text
omega_Sigma0 = P_(H->Sigma)(O_H),
```

with existence, uniqueness modulo gauge, continuous dependence, constraint
preservation, and independence from any auxiliary exterior extension.  Here
`omega_Sigma0` is an algebraic state; density-matrix notation is allowed only
after a finite-cutoff or type-I representation is separately established.  The
map must also derive the initial high-energy density and the later control
history `r(tau)` used below.  Merely naming a horizon supplies none of these.

This target already assumes a causal/null structure.  That is a named
causal-structure circularity gate: either Pre-A declares causal order as a
fundamental input, or an upstream theorem must derive it before Lane H can
support spacetime emergence.

## 4. Common Lane-F/Lane-Q candidate: PA-M2-CI8-RS-v0

Let `T_L^3` be a cubic periodic torus, `q=2*pi*m/L` for a positive integer
`m`, and `phi in H2(T_L^3;R)`.  For `c>0` and `g>0`, define

```text
F_r[phi]
 = 1/2 int_T [r phi^2 + c sum_i ((partial_i^2+q^2)phi)^2] dx
   + g/4 int_T phi^4 dx.
```

The reference is `phi=0` on the same torus, volume, Fourier normalization, and
boundary convention.  The control parameter `r` is not called temperature or
cosmic cooling until Lane H or a later gravitational model derives `r(tau)`.

The quadratic symbol

```text
K_r(k)=r+c sum_i(k_i^2-q^2)^2
```

has exactly eight commensurate minima

```text
Q_sigma=(sigma_1 q,sigma_2 q,sigma_3 q),  sigma_i in {-1,+1},
```

and at every node

```text
grad K_r(Q_sigma)=0,
D^2 K_r(Q_sigma)=8 c q^2 I_3.
```

This replaces the rank-one continuously degenerate shell of the bare
`PA-M5-NL3-SV-v0` test with isolated full-rank nodes.  Three spatial dimensions,
cubic axes, the torus, and the field law remain inserted inputs.

## 5. Lane F exact finite-volume result

For `r>=0`, all terms are nonnegative and `phi=0` is the unique zero-energy
field.  For `r<0`, a node trial `phi=A cos(Q.x)` has

```text
F_r/V = r A^2/4 + 3 g A^4/32,
A^2=-4r/(3g),
F_r/V=-r^2/(6g)<0.
```

For a constant field `phi=a`,

```text
F_r[a]/V=(r+3 c q^4)a^2/2+g a^4/4.
```

Consequently, throughout

```text
-3 c q^4 <= r < 0,
```

every constant field has nonnegative energy while the modulated trial is
negative.  Coercivity and the direct method give a global minimizer on the
finite torus, and every global minimizer in this window is nonzero and
spatially inhomogeneous.  This comparison is against the identical zero
reference, not merely against another modulated candidate.

Let `X=||phi||_2^2`, let `D` be the nonnegative higher-derivative quadratic
form, and let `I4=int phi^4`.  At a minimizer the radial stationarity identity
is

```text
r X + D + g I4 = 0.
```

Jensen gives `I4>=X^2/V`, hence

```text
0 < X/V <= -r/g.
```

The energy bracket is

```text
-r^2/(4g) <= inf F_r/V <= -r^2/(6g)  for r<0,
inf F_r=0                              for r>=0.
```

Thus the finite-volume classical order amplitude vanishes at the boundary.
This is not yet an infinite-volume or quantum phase-transition theorem.

## 6. Spectral concentration and leading morphology

Write `h=2*pi/L` and `q=h*m`.  The exact first lattice gap away from the eight
nodes is

```text
delta_L=h^4(2m-1)^2.
```

Indeed, for an integer `n` with `|n|!=m`, the nearest square to `m^2` is
`(m-1)^2`, so `|n^2-m^2|>=2m-1`; changing more than one coordinate only
increases the sum.  Radial stationarity then implies

```text
||P_(Q-perp) phi||_2^2 / ||phi||_2^2 <= |r|/(c delta_L).
```

Therefore minimizer Fourier mass concentrates on the CI8 node star as
`r` approaches zero from below.

For representatives `Q_0=(+++)`, `Q_1=(++-)`, `Q_2=(+-+)`, and
`Q_3=(-++)`, let `z_0,...,z_3` be the four complex amplitudes after imposing
the real-field condition.  Exact zero-momentum convolution gives

```text
m2=2 sum_j |z_j|^2,
m4-(3/2)m2^2
 =12[sum_(i<j)|z_i|^2|z_j|^2
     +4 Re(conj(z_0) z_1 z_2 z_3)].
```

The six pair products can be grouped into three AM-GM pairs, so their sum is
at least `6 sqrt(prod_j |z_j|^2)`, while the resonant term is at least
`-4 sqrt(prod_j |z_j|^2)`.  The excess is nonnegative and equality requires at
most one nonzero `z_j`.  Hence the kernel-restricted leading quartic problem is
minimized by one antipodal node pair, a single-Q stripe, rather than a multi-Q
superposition.

A pure cosine is a variational comparator, not an exact nonlinear stationary
solution.  The corrected branch begins

```text
phi=A cos(Q.x+theta)+B cos(3Q.x+3theta)+...,
A^2=-4r/(3g)+O(r^2),
B=-g A^3/(768 c q^4)+O(A^5),
F_r/V=-r^2/(6g)+O(|r|^3).
```

An explicit complement implicit-function estimate is still required before
this local branch is promoted beyond the candidate certificate.

## 7. Lane Q exact Gaussian boundary

Lane Q declares, rather than inherits, the inertial Hamiltonian

```text
H=int_T pi^2/(2 chi) dx+F_r[phi],  chi>0,
[phi(x),pi(y)]=i hbar delta(x-y),
```

after a finite Galerkin and occupation cutoff.  The current A2 dynamics is a
gradient flow, so this is a new hypothesis.

Near a node at `r=0`,

```text
omega^2=(4 c q^2/chi)|p|^2+O(|p|^3),
c_*^2=4 c q^2/chi,
z=1.
```

The equality of the eight tree-level cones is not radiatively protected.  A
cubic/sign-even self-energy term such as `k_i^2 k_j^2` can split longitudinal
and transverse velocities at a body-diagonal node.

For one exact quadratic mode,

```text
[phi_k(t),phi_-k(0)]
 =-i hbar sin(omega_k t)/(chi omega_k),
C_k(t)=hbar^2 sin^2(omega_k t)/(chi^2 omega_k^2).
```

The OTOC is bounded for positive frequency and tends to
`hbar^2 t^2/chi^2` at a critical zero mode, so its exponential rate is zero.
Hyperbolic growth for `omega_k^2<0` is a one-mode linear instability, not
many-body scrambling.  Criticality alone therefore does not establish quantum
chaos or chaos-caused formation.

## 8. Preregistered interacting Lane-Q test

The unchanged local quartic vertex contains the exact collision

```text
Q_(+++)+Q_(+--)=Q_(+-+)+Q_(++-).
```

One antipodal pair is only one anharmonic oscillator.  The first many-mode
diagnostic retains the full CI8 star and resolves `Z2`, translation momentum,
cubic irreducible representations, reflection, and time reversal before level
statistics or OTOCs are computed.

Use total occupation `N_tot<=Nmax`, compare `Nmax` with `Nmax+4` at fixed
parity, and require negligible weight in the top four occupation layers.  CI8
is not invariant under the cubic force: components at `+/-3q` appear, so the
momentum cutoff must subsequently grow.

The diagnostic ablation is

```text
D(V4)=sum_n P_n V4 P_n,
H_eta=H2+D(V4)+eta[V4-D(V4)],  0<=eta<=1.
```

At `eta=0` the quadratic nodes and all occupation-diagonal self/cross-Kerr
shifts remain, but occupation-changing collisions are removed.  Only `eta=1`
is the unchanged candidate.  No nonzero ablation can preserve the full
coherent-state static functional for every state, so this interpolation must
not be described as a same-static-energy experiment.

A causal claim requires converged chaos diagnostics, temporal precedence,
suppression or parametric delay of the selected order under the declared
ablation after energy matching, and survival under occupation, momentum, and
volume growth.  Correlation alone is insufficient.

## 9. Lane-H gates before the horizon may be called a start

1. **Horizon type:** derive the relevant causal boundary and distinguish an
   event horizon from a Cauchy horizon or an observer-dependent apparent
   boundary.
2. **Boundary observables:** define `A_H`, gauge-invariant generators,
   commutation relations, positivity, normalization, and the regularity class
   of `omega_H`.
3. **Characteristic completeness:** supply two intersecting null sheets and
   corner data, or prove an equivalent complete data system.
4. **Constraint closure:** solve gravitational and gauge constraints without
   counting coordinate data as physical information.
5. **Reconstruction:** prove existence, uniqueness modulo gauge, continuous
   dependence, and independence from an arbitrary exterior extension.
6. **Information ledger:** prove whether the boundary-to-bulk map is an
   isometry, unitary channel, or declared open-system channel; unknown exterior
   information may not be silently erased.
7. **High-energy output:** derive a finite interior state, its energy-density
   scale, and the domain in which an effective bulk description is valid.
8. **Cooling/control bridge:** derive `r(tau)` and the same initial algebraic
   state used by Lane F and Lane Q rather than fitting separate histories; a
   density matrix may be used only in a declared finite-cutoff/type-I setting.
9. **Observable holdout:** preregister at least one late observable not used to
   choose the boundary state or parameters.

Failure of any one gate does not show that no origin exists beyond the horizon.
It shows only that this candidate has not converted that possibility into a
predictive interior theory.

## 10. Cyclic behavior is an optional downstream test

The current A2 autonomous gradient flow obeys

```text
F[Psi(T)]-F[Psi(0)]
 =-int_0^T ||partial_t Psi||_2^2 dt.
```

A periodic orbit up to an energy-preserving symmetry would force the integral
to vanish and hence be stationary.  Thus this gradient law cannot supply a
nontrivial recurrence mechanism.

No cyclic postulate is needed for Lane H, F, or Q.  Only after a complete
boundary-to-bulk and later bulk-to-boundary dynamics exists may one ask whether
the induced physical return map `C` has a fixed point `C(X_*)=X_*`.  Such a
fixed point would be a downstream recurrence result, not an ultimate-origin
explanation.

## 11. Devil's-advocate review

1. **Calling `H^-` an event horizon may presuppose the desired space-time.**
   **UPHELD.**  The programme begins with a null candidate boundary; its global
   event-horizon status is a gate.
2. **One horizon trace cannot determine the bulk.**  **UPHELD AND EXACTLY
   EXHIBITED.**  The two-solution toy counterexample forces extra
   characteristic information.
3. **A boundary algebra could contain more than a scalar trace.**
   **VALID.**  This is why the no-go is scoped and the complete algebra plus
   reconstruction map is the actual target.
4. **The candidate inserts three dimensions and cubic axes.**  **UPHELD.**
   CI8 is a discriminator, not spatial emergence.
5. **Finite-volume classical minimization is not a thermodynamic or quantum
   phase transition.**  **UPHELD.**
6. **A real scalar has no compact phase, gauge redundancy, charge, or photon.**
   **UPHELD.**  PA-M2 cannot complete T-053 alone.
7. **Tree-level common speed may split at loops.**  **UPHELD.**
8. **Gaussian critical growth is not nonlinear chaos.**  **UPHELD AND
   EXACTLY EXHIBITED.**
9. **The scrambling ablation changes coherent-state energetics.**
   **UPHELD.**  It is a diagnostic interpolation; `eta=1` alone is the original
   candidate.
10. **A recurrence law would still not explain the first admissible law or
    state.**  **UPHELD.**  Cyclic behavior is downstream and optional.
11. **The 1+1 Lane-H toy and three-dimensional PA-M2 are independent
    models.**  **UPHELD.**  No state, parameter, energy-normalization,
    dimensional, or `r(tau)` composition map has been proved.

## 12. Status and next proof checkpoint

The package now contains three exact candidate-scope advances:

- Lane H: a one-null-trace nonuniqueness counterexample and a minimal
  double-null reconstruction in the fixed-background toy equation;
- Lane F: an inhomogeneous global minimizer below the identical zero reference,
  a sharper stationary amplitude bound, node concentration, and an exact
  kernel-restricted leading single-Q morphology inequality;
- Lane Q: a zero Gaussian Lyapunov exponent and an exact native four-node
  collision for the first interacting test.

The next checkpoint is not a cyclic model.  It is:

1. formulate the simplest constraint-compatible double-null boundary model;
2. prove its local reconstruction and state-regularity domain;
3. derive, rather than name, the high-energy interior state and `r(tau)`;
4. complete the Lane-F complement implicit-function certificate; and
5. construct the symmetry-resolved CI8 interacting Hamiltonian and ablation,
   then grow the momentum cutoff.

The composition arrow from the 1+1 Lane-H output to the three-dimensional
PA-M2 initial state and `r(tau)` is independently open; no shared physical
theory is claimed before that arrow is proved.

In parallel, a genuinely compact-gauge M3 candidate remains necessary because
the present real scalar has no route to charge or a photon.

## 13. External primary anchors

- T. Hilditch, J. A. Valiente Kroon, and P. Zhao, *Revisiting the
  characteristic initial value problem for the vacuum Einstein field
  equations*, https://arxiv.org/abs/1911.00047 .  This supports using data on
  intersecting null hypersurfaces and a local existence theorem as the relevant
  general-relativistic benchmark; it does not prove the TECT boundary map.
- B. S. Kay, M. J. Radzikowski, and R. M. Wald, *Quantum Field Theory on
  Spacetimes with a Compactly Generated Cauchy Horizon*,
  https://arxiv.org/abs/gr-qc/9603012 .  This warns that Cauchy-horizon quantum
  regularity can fail and must not be conflated with an event-horizon start.
- J. Maldacena, S. H. Shenker, and D. Stanford, *A bound on chaos*,
  https://arxiv.org/abs/1503.01409 .  This anchors OTOC/Lyapunov terminology;
  it does not establish chaos in PA-M2.
- R. Bousso, *A Covariant Entropy Conjecture*,
  https://arxiv.org/abs/hep-th/9905177 .  This motivates explicit screen and
  information-capacity accounting; the conjecture is not assumed as a proved
  TECT theorem.

## 14. No-overclaim

`PA-M2-CI8-RS-v0` remains a T0 new-hypothesis benchmark.  The package does not
prove that an event horizon is the origin of the observed universe, that the
required boundary state exists, that a unique gravitational bulk follows, or
that the derived bulk cools through the PA-M2 transition.  It does not prove a
thermodynamic or quantum phase transition, nonlinear quantum chaos,
chaos-caused ordering, compact gauge structure, emergent space-time, physical
light or mass, a bounce, a cyclic universe, or physical model selection.
