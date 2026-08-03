# PA-H1 / PA-M2 strict-composition no-go certificate

- Candidate: `PA-H1-M2-STRICT-COMPOSITION-NOGO-v0`
- Version: `0.1.0`
- Date: 2026-08-03
- Task: `T-054`
- Claim context: `C6-SPACETIME-SIGNATURE`
- Comparison context: `A2-FULL-PRODUCTION-WELLPOSED`
- Authority: T0 compatibility and no-go certificate only
- Claim-bearing: no

## 0. Result first

The present PA-H1 finite image and PA-M2 CI8 soft sector cannot be
identified **unchanged** by one interface that simultaneously preserves the
declared full phase space, symplectic form, all-amplitude interacting energy,
zero-background dynamics, and node-only regulator.

This is a narrow result.  A six-to-sixteen symplectic injection exists.  What
fails is a bijective full-generator identification and, independently, an
exact affine energy-preserving or full-flow-intertwining injection for the
current Hamiltonians.  The result is not a no-go for a larger common parent,
a nonlinear or holographic map, a constrained reduction, an ordered-background
Hessian, a growing regulator, a nonstationary state, or a dynamical clock.

The energy-reference issue is load-bearing and is stated before the proof:

> No below-empty-space or no-condensate comparison has been performed.  The
> same PA-H1 vacuum has energy `0` for `dGamma(Omega)` and `13/2` for the raw
> three-oscillator Hamiltonian, with the same state and dynamics.  PA-M2's
> internal `phi=0` reference does not fix this cross-model offset.  Thus a
> statement that the candidate is below empty space is presently undefined,
> not proved false or true.

The correct next object is a common finite-regulator three-torus (`T^3`) parent with one
algebra, state, Hamiltonian, volume, boundary, `hbar`, counterterm, and energy
reference.  A separate dynamical control or proved nonstationary state must
then produce `r(tau)`.

## 1. Imported authorities and exact scope

The two inputs are already registered T0, non-claim-bearing packages:

1. `strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json`
2. `strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-certificate-260803.md`
3. `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-primary-pre-a-c0a-gaussian-ccr-pah1-embedding/result.json`
4. `strategy/pre-a-pa-m2-ci8-rs-dual-lane-manifest.json`
5. `claims/A2-FULL-PRODUCTION-WELLPOSED/runs/2026-08-03-primary-pre-a-pa-m2-ci8-rs-dual-lane/result.json`
6. `strategy/pre-a-c0-dynamical-completion-underdetermination-manifest.json`

The source phase space is

```text
V_H = R^3_q direct-sum R^3_p,
Omega = diag(3,5,5),
sigma_H((q,p),(q',p')) = q.p' - p.q'.
```

It has dimension six and the classical quadratic energy

```text
H_H(q,p) = (p.p + q.Omega^2.q)/2.
```

The target CI8 real-scalar soft sector has four independent complex
amplitudes, hence eight real configuration coordinates `Q_M`.  Lane Q adds
eight conjugate momenta `P_M`, so

```text
V_M = R^8_Q direct-sum R^8_P,
dim(V_M) = 16.
```

At zero background its inertial Hamiltonian begins as

```text
H_M(Q,P) = P.P/(2 chi) + r Q.Q/2
           + g int(phi_Q^4)/4,
chi > 0, g > 0,
```

with the exact local quartic vertex inherited from PA-M2.

## 2. Strict-interface contract

The theorem tests the tempting shortcut that the two existing fixtures can be
used as they stand.  A strict interface must meet all applicable clauses:

1. It is a state-independent affine map `iota(y)=b+A y` whose derivative is
   injective and symplectic.
2. A full equivalence is induced by a linear symplectic bijection between the
   declared phase spaces and their named Weyl generators.
3. Exact energy matching holds for every source amplitude, up to one overall
   quadratic-energy scale and one additive constant.
4. The zero-background linearized flows intertwine, possibly after one
   nonzero constant time rescaling.
5. The unchanged CI8 subspace is invariant under the unprojected local cubic
   force.
6. Energy comparisons use one regulator, volume, boundary, `hbar`,
   counterterm, and reference prescription.
7. If the invariant PA-H1 vacuum is proposed as the sole input to `r(tau)`,
   the state-to-control rule is time-homogeneous and does not insert time by
   hand.

This contract does not cover arbitrary abstract C-star-algebra isomorphisms;
the dimension clause concerns a Weyl-generator-preserving identification
induced by a linear symplectic bijection.

## 3. Theorem

### Theorem PA-H1-M2-STRICT-COMPOSITION-NOGO-v0

For the fixtures in Section 1:

1. no linear symplectic bijection exists between `V_H` and `V_M`; every
   symplectic injection has a ten-dimensional symplectic complement, and the
   PA-H1 finite-image state does not uniquely select a state on that
   complement;
2. for `g>0`, no affine symplectic injection can preserve the two Hamiltonians
   for all amplitudes, even up to an overall quadratic-energy scale and an
   additive constant;
3. at the PA-M2 zero background, no injective time-independent full-flow
   intertwiner exists for any `r/chi`, even after constant time rescaling;
   consequently a zero-fixing `C^1` local flow embedding with injective
   derivative is also excluded;
4. the CI8 node-only configuration space is not invariant under the unchanged
   PA-M2 cubic force.

Therefore the current PA-H1 finite image and current PA-M2 CI8 candidate do
not form one exact, unchanged state-, energy-, dynamics-, and
regulator-preserving finite interface.

The energy-reference, cooling-history, and continuum causal-symbol results in
Sections 8--10 are separate underdetermination or boundary lemmas.  They are
not needed to manufacture the core contradiction.

## 4. Dimension and state extension

Dimension gives

```text
dim(V_H) = 6,
dim(V_M) = 16.
```

Hence there is no invertible linear map, and therefore no linear symplectic
bijection, between the declared spaces.

This does **not** forbid an injection.  In the coordinate orders

```text
(q0,qc,qs,p0,pc,ps)
(Q0,...,Q7,P0,...,P7),
```

map the three source canonical pairs to the first three target pairs.  The
primary and independent programs verify directly that

```text
rank(J) = 6,
J^T sigma_M J = sigma_H.
```

The remaining five target canonical pairs form a nondegenerate symplectic
complement of dimension ten.  Give those five modes frequency two or frequency
seven.  Both choices define positive quasi-free covariance blocks; both
pull back to the same PA-H1 covariance on `J(V_H)`; and they differ on the
complement.  Full-state extension is therefore nonunique.

This is a selection boundary, not a proof that a richer parent cannot contain
the PA-H1 image.

## 5. All-amplitude interacting-energy no-go

Let

```text
iota(y) = b + A y
```

be affine with symplectic derivative

```text
A^T sigma_M A = sigma_H.
```

Assume, for some scale `a` and constant `C`,

```text
H_M(iota(y)) = a H_H(y) + C
```

for every `y`.  Replace `y` by `lambda y`.  The right side is a polynomial of
degree at most two in `lambda`.  The degree-four coefficient on the left is

```text
(g/4) int phi_(A_Q y)^4.
```

The affine translation `b` changes lower coefficients but not this leading
one.  Since `g>0`, equality for every `lambda` requires

```text
int phi_(A_Q y)^4 = 0
```

for every `y`.

The code gives a finite exact injectivity certificate for the real CI8 basis.
Its `L^2` Gram matrix is the identity.  Moreover, Parseval applied to
`phi_Q^2` writes

```text
int phi_Q^4 = sum_k |Fourier_k(phi_Q^2)|^2,
```

and its zero-mode term is

```text
(sum_j Q_j^2)^2.
```

Thus the quartic integral vanishes only when `Q=0`.  It follows that
`A_Q y=0` for every `y`: the derivative image lies entirely in the momentum
subspace.  But a pure-momentum subspace is isotropic, so

```text
A^T sigma_M A = 0,
```

contradicting the nondegenerate `sigma_H`.

This proves the affine all-amplitude statement.  It does not exclude a
nonlinear map, matching only through quadratic order, a single energy-shell
map, a constrained reduction, or a modified/counterterm Hamiltonian.  With
`g=0` the degree-four obstruction disappears; that is an explicit positive
control.

## 6. Zero-background Gaussian-flow no-go

The PA-H1 Hamiltonian generator is

```text
A_H = [[0,I3],[-Omega^2,0]],
Omega = diag(3,5,5).
```

Its characteristic polynomial is

```text
(s^2+9)(s^2+25)^2.
```

At `phi=0`, the PA-M2 CI8 generator is

```text
A_M = [[0,I8/chi],[-r I8,0]],
A_M^2 = -(r/chi) I16,
```

with characteristic polynomial

```text
(s^2+r/chi)^8.
```

Suppose an injective linear map `J` intertwines the flows after a nonzero
constant time rescaling `nu`:

```text
A_M J = nu J A_H.
```

Squaring gives

```text
-(r/chi) J = nu^2 J A_H^2.
```

Injectivity would make `A_H^2` one scalar operator.  Instead it contains both
`-9` and `-25`.  Equivalently, the same scalar would have to satisfy

```text
r/(chi nu^2) = 9 = 25.
```

That is impossible.  A zero-fixing `C^1` nonlinear flow embedding would have
an injective derivative obeying the same equation, so it is excluded at this
linearization as well.

The frequency-three sector alone can match `r/chi=9`; the frequency-five
sector alone can match `r/chi=25`.  A free target with the whole source
frequency multiset copied into it also intertwines under the explicit
injection.  These controls show that the obstruction is the unchanged target
spectrum, not the mere existence of extra coordinates.

This clause is only about a time-independent interface at the PA-M2 zero
background.  A future ordered equilibrium has a different Hessian, and a
time-dependent interface or control law remains open.

## 7. CI8 nonlinear nonclosure

Choose a retained node `Q=q(1,1,1)` and a real stripe

```text
phi(x) = A cos(Q.x).
```

The local quartic energy produces the cubic force

```text
phi^3 = (A^3/4)[3 cos(Q.x) + cos(3Q.x)].
```

The vector `3Q` is not a CI8 node.  In exponential Fourier coefficients the
fundamental coefficient is `3/8`, the `3Q` coefficient is `1/8`, and the
omitted pair has normalized squared magnitude `1/32`.  Hence the full local
vector field is not tangent to the CI8 node subspace.

A projected model using `P_CI8(phi^3)` is mathematically legitimate, but it
changes the unprojected continuum equation.  Enlarging the cutoff to include
`3Q` is also not a one-step closure: cubing that harmonic generates `9Q`.
The repair must therefore declare a regulator-growth rule and prove a limit;
it cannot call the node-only dynamics unchanged.

## 8. Common energy zero is not identified

For the PA-H1 fixture,

```text
sum(Omega_j)/2 = (3+5+5)/2 = 13/2.
```

The second-quantized Markov generator `dGamma(Omega)` normal-orders that
vacuum energy to zero.  Adding a constant to either Hamiltonian leaves its
classical Hamiltonian vector field unchanged; in quantum evolution it changes
only a global phase and leaves normalized state correlations unchanged.

If the cross-model difference is `Delta E`, independent additive constants
give

```text
Delta E -> Delta E + C_M - C_H.
```

Its sign can therefore be reversed without changing any existing internal
result.  PA-M2's candidate-scope exact finite-torus negative relative-energy
bound is still valid **within its own fixed normalization**, comparing an
ordered trial or minimizer with `phi=0` on the same torus.  It cannot be
transported into an absolute
comparison with the PA-H1 vacuum, empty space, or the Sector-B no-condensate
reference.

A common regulator, volume, boundary, field normalization, `hbar`,
counterterm, and reference subtraction are mandatory before a cross-model
sign is meaningful.

## 9. The invariant vacuum cannot supply monotone cooling

For the selected PA-H1 Gaussian vacuum `omega_0`, the primary package proves

```text
omega_0 after alpha_t = omega_0.
```

Therefore any time-homogeneous state functional

```text
r(t) = R(omega_0 after alpha_t)
```

is constant.  It cannot cross zero.

The finite frequencies `3,5,5` also give a `2*pi` periodic flow.  On any
complete orbit, a continuous state-local function that is globally monotone
in time must be constant: periodicity gives equal endpoint values on every
period, while monotonicity prevents variation between them.

This does not say that autonomous dynamics can never cross zero.  A nonvacuum
coherent observable can oscillate through zero on a finite interval.  An
externally assigned `r(t)` can cross zero, and a new canonical clock pair
`(R,P_R)` can generate a changing coordinate.  Those are positive controls,
but the external curve is inserted and the clock requires a declared law and
total-energy ledger.  Open systems, coarse graining, and genuinely
nonstationary interacting states also remain open.

## 10. Global causal-symbol mismatch

This lemma concerns the continuum symbols and is separate from the
finite-dimensional CI8 theorem.

The inserted PA-H1 Klein--Gordon symbol has

```text
omega_H(K) = sqrt(K^2+m^2),
d omega_H/dK -> 1.
```

At `r=0`, along the PA-M2 continuum axis `(K,q,q)` with `K>q`,

```text
omega_M(K) = sqrt(c/chi)(K^2-q^2),
d omega_M/dK = 2 sqrt(c/chi) K.
```

The latter grows without a cutoff-uniform bound.  Thus the unchanged global
principal symbols do not define one Lorentz cone or one limiting group speed.
This statement alone is not a proof of finite-cutoff superluminal signalling.

Near a CI8 node, PA-M2 still has a tree-level `z=1` cone with local speed
`2q sqrt(c/chi)`.  That speed can be fitted to one by setting
`c/chi=1/(4q^2)`, but the fit is an input and does not repair the ultraviolet
symbol.  A finite spectral cutoff bounds the displayed speed only at that
cutoff; the bound grows when the cutoff grows.  A local 3+1 causal ultraviolet
completion is a separate gate.

## 11. The product-parent control

One may always form the direct product

```text
(V_H direct-sum V_M,
 sigma_H direct-sum sigma_M,
 omega_H tensor omega_M,
 H_H + H_M).
```

Its phase dimension is twenty two and its symplectic form is nondegenerate.
This is a useful hostile control: it prevents the false statement that no
common mathematical container exists.

The decoupled product supplies no shared field, coupling, derived or selected
common relative energy normalization, boundary-to-bulk derivation, `r(tau)`,
or reason that PA-M2 emerges from PA-H1.  It therefore does not satisfy the
intended Pre-A composition task.

## 12. Minimal positive successor

The no-go turns the next construction into two explicit positive stages.

### CP1: common finite-regulator parent

Build one three-torus (`T^3`) parent with:

1. one real phase space and Weyl algebra;
2. one finite Fourier or occupation regulator and one removal rule;
3. one volume and boundary convention;
4. one `hbar` and field normalization;
5. one Hamiltonian, counterterm prescription, and energy reference;
6. one selected state;
7. a proved characteristic-boundary map or reduction;
8. a proved interacting ordering-sector map or reduction.

The present 1+1 PA-H1 fixture remains a calibration target.  It is not silently
promoted to the physical upstream component of CP1.

### CP2: derived control history

Choose one of two preregistered routes:

1. add a canonical control pair `(R,P_R)` and prove a finite-time `R=0`
   crossing together with the conserved total-energy ledger; or
2. select a nonstationary interacting state and derive `r(tau)` from a fixed
   1PI/2PI Hessian or an equally explicit state functional.

Only after CP1 and CP2 may the PA-M2 phase-ordering result be interpreted as a
derived high-energy cooling transition.

## 13. Adversarial review and falsifiers

### Sign and factor checks

- The PA-H1 raw offset is recomputed as `sum(Omega)/2`, not pasted into the
  calculation.
- The quartic coefficient is `g/4`; affine translation changes lower powers
  but not the `lambda^4` coefficient.
- `cos^3(theta)` is checked in exponential Fourier coefficients, including
  the `1/32` omitted norm.
- The Hamiltonian-generator convention and both characteristic polynomials
  are reconstructed independently.

### Convention and unit checks

- Phase coordinates are explicitly ordered in both implementations.
- The target phrase "eight real canonical coordinates" is resolved as eight
  real configuration coordinates plus eight momenta.
- A constant time rescaling is allowed in the dynamics no-go.
- The energy-zero result is labelled underdetermination, not impossibility.
- The causal-symbol statement is global and continuum-scoped; the local
  `z=1` cone is retained.

### Hardcode-masking checks

- Dimensions are derived from the source frequency list and CI8 pair count.
- The ten-dimensional complement, zero-point shift, polynomial factors,
  leakage norm, period, and product dimension are computed from those inputs.
- Primary and non-importing independent implementations use different matrix,
  polynomial, and Fourier representations.
- Stored outputs are compared with fresh child executions by the integrator.

### Limit and loophole checks

- A symplectic injection exists even though a bijection does not.
- Removing `g` removes the degree-four obstruction.
- Single-frequency source sectors can intertwine.
- Projecting CI8 defines a changed finite model.
- A nonvacuum finite-interval zero crossing remains possible.
- A dynamic clock and a decoupled product remain possible.
- The ordered PA-M2 background, nonlinear maps, constrained sectors, enlarged
  cutoffs, and ultraviolet completions remain open.

Any counterexample satisfying every clause of the strict-interface contract
falsifies the core no-go.  Any construction satisfying CP1 with a common
energy ledger supersedes the present repair boundary.  External mathematical
and physical review is invited.

## 14. Reproduction

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_pah1_m2_strict_composition_nogo.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_pah1_m2_strict_composition_nogo_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_pah1_m2_strict_composition_nogo_verify.py --self-test
```

The scripts also write JSON artifacts when run without `--self-test`.

## 15. Prior-art and novelty boundary

The dimension, symplectic-complement, polynomial-degree, Parseval,
characteristic-polynomial, Fourier-closure, additive-constant, periodicity,
and dispersion arguments are standard mathematics.  They are not new TECT
discoveries.  The repository-specific result is the exact compatibility audit
of these two declared T0 fixtures, the explicit falsifier set, and the CP1/CP2
repair contract.  No global priority or world-first claim is made.

## 16. Final boundary

This certificate does not invalidate the scoped PA-H1 reconstruction or the
scoped PA-M2 finite-torus variational result.  It does not prove a physical
vacuum, energy below empty space, a no-condensate comparison, a high-energy
initial state, cosmic cooling, a thermodynamic or quantum phase transition,
nonlinear chaos, spacetime emergence, gravity, an event horizon, or a cyclic
universe.  It does not close C0 and does not prove Pre-A.
