# PA-CP1-LT3-RS-v0: exact local lattice ordering scaffold and CP1 boundary failure

**Issued:** 2026-08-03  
**Task:** T-054  
**Context:** C6-SPACETIME-SIGNATURE, compared with the scoped PA-M2 work under A2-FULL-PRODUCTION-WELLPOSED  
**Authority:** T0 finite-lattice common-container certificate; not a TECT action, theorem-tier change, completed CP1, physical vacuum, or Pre-A closure

## Result first

This candidate produces the first exact same-Hamiltonian answer registered in
the current TECT/Pre-A programme to the local question that motivated the
repeated empty-space objection:

> At fixed finite lattice, fixed volume, fixed periodic boundary, fixed field
> normalization, fixed couplings and the declared additive convention
> `C=0`, every `r<0` ordered classical ground configuration has
> 
> `H_min=-N^3 r^2/(4g)<H(0,0)=0`.

This is a proved comparison with the zero-field configuration in one and the
same model.  It is not yet a comparison with physical empty space.  In the
quantum theory `phi=0` is a configuration, not a normalizable state, and no
physical no-condensate state has been selected.

The same candidate also proves eight isolated quadratic nodes, exactly 256
classical ground configurations, cubic reciprocal-lattice closure, global
finite classical evolution, and a standard unique full quantum ground state.

It nevertheless fails CP1 as defined by the preceding interface certificate:

> The periodic torus is not a characteristic boundary, and the symmetric
> finite parent data cannot deterministically select a proper nonempty site
> boundary.  No two-sheet characteristic map, corner data, symplectic flux,
> bulk reconstruction or PA-H1 role is derived.

The correct verdict is therefore a partial advance and a sharp stopping point,
not CP1 completion.

## 1. Fixed candidate

Let

```text
Lambda_N=(Z/NZ)^3,    N=4m,    m>=1,    V=N^3,
c>0,    g>0,    chi>0,    hbar>0,    r real.
```

The lattice spacing and cell-volume factor are one in this version.  Let
`S_i` be the unit periodic shift in direction `i` and set

```text
B_i=2-S_i-S_i^(-1)-kappa,    kappa=2,
```

so that

```text
B_i=-S_i-S_i^(-1).
```

The classical phase space is

```text
P_N=R^V_phi direct-sum R^V_pi
```

with canonical symplectic form

```text
sigma((phi,pi),(phi',pi'))
  =sum_x(phi_x pi'_x-pi_x phi'_x).
```

The Hamiltonian is

```text
H_r(phi,pi)
 =sum_x pi_x^2/(2chi)
  +(1/2)sum_x[r phi_x^2+c sum_i(B_i phi)_x^2]
  +(g/4)sum_x phi_x^4.
```

There is no fixed-`N` counterterm in version 0.  The additive scalar is fixed
to `C=0`, so `H_r(0,0)=0`.  This convention is part of the candidate rather
than a derived absolute energy zero.

The exact quantum representation is the regular finite-degree Weyl CCR
representation on `L2(R^V,dphi)`.  An occupation-number compression is not
part of the definition.

## 2. Exact Fourier theorem

For lattice momentum `k_i=2*pi*n_i/N`,

```text
b_i(k)=-2 cos(k_i)
```

and the zero-background static Hessian symbol is

```text
K_r(k)=r+4c sum_i cos(k_i)^2.
```

Because `N` is divisible by four, its minimum set consists of exactly the
eight momenta

```text
Q_sigma=(sigma_1*pi/2,sigma_2*pi/2,sigma_3*pi/2),
sigma_i in {+1,-1}.
```

At every node,

```text
grad K_0(Q_sigma)=0,
D^2 K_0(Q_sigma)=8c I_3.
```

The smallest nonzero eigenvalue of `sum_i B_i^2` is

```text
delta_N=4 sin(2*pi/N)^2.
```

Thus the soft set is an eight-point full-rank Morse star, not a continuous
shell.

## 3. Coercivity and finite classical flow

Writing `X=||phi||_2^2` and using the finite Jensen inequality gives

```text
sum_x phi_x^4 >= X^2/V,
```

hence

```text
H_r >= ||pi||_2^2/(2chi)+rX/2+gX^2/(4V).
```

The Hamiltonian is bounded below and coercive for every real `r`.  It attains
its global minimum because the phase space is finite-dimensional.

Hamilton's equations are a polynomial ordinary differential equation.  Energy
conservation keeps every finite initial condition in a compact sublevel set,
so the maximal solution cannot escape in finite time.  The finite classical
flow is therefore global in both time directions.

This is not a continuum well-posedness theorem.

## 4. Exact same-Hamiltonian reference theorem

### 4.1 Nonnegative side

If `r>=0`, every displayed energy term is nonnegative.  Equality requires
`pi=0` and `phi=0`.  More strongly, the stationary equation dotted with `phi`
gives

```text
r||phi||_2^2+c sum_i||B_i phi||_2^2+g sum_x phi_x^4=0,
```

so the zero field is the unique classical stationary point and global
minimum.

### 4.2 Ordered side

If `r<0`, the exact identity is

```text
H_r+Vr^2/(4g)
 =||pi||_2^2/(2chi)
  +(c/2)sum_i||B_i phi||_2^2
  +(g/4)sum_x(phi_x^2+r/g)^2.
```

Consequently,

```text
min H_r=-Vr^2/(4g),
```

and equality holds exactly when

```text
pi=0,
B_i phi=0 for i=1,2,3,
phi_x^2=-r/g for every x.
```

This proves the negative same-model sign without transporting an energy zero
from PA-H1 or from another regulator.

## 5. Complete classification of classical minima

The kernel equation is

```text
phi_(x+e_i)+phi_(x-e_i)=0,
```

equivalently

```text
phi_(x+2e_i)=-phi_x.
```

Write `x=2m+epsilon`, with `epsilon in {0,1}^3`.  Every kernel field has

```text
phi_(2m+epsilon)=(-1)^(m_1+m_2+m_3) a_epsilon.
```

At a global minimum each of the eight independent `a_epsilon` values is
either `+sqrt(-r/g)` or `-sqrt(-r/g)`.  There are therefore exactly

```text
2^8=256
```

classical global minima.  They include single-star and multi-star patterns;
the model does not select a unique stripe morphology.

Allowing each `a_epsilon` also to vanish solves the kernel-restricted stationary
equation at `r=-g a^2`.  The exact kernel stationary count is

```text
3^8=6561.
```

Use the unitary discrete Fourier convention

```text
phi_hat(k)=V^(-1/2) sum_x exp(-ik.x) phi_x.
```

Every global minimum is nonconstant, has Fourier support only on the eight
nodes, and obeys

```text
(1/V)sum_Q |phi_hat(Q)|^2=-r/g.
```

The ordered Hessian is

```text
Hess_ordered=c sum_i B_i^2-2r I,
```

with strict spectral floor `-2r>0`.  All 256 minima are isolated strict local
minima at fixed `N`.

## 6. Umklapp, the phase-shift control, and what is not inherited

For every `N=4m`, not merely for `N=4`, each node coordinate is `+N/4` or
`-N/4` modulo `N`.  The sum of three such coordinates is again `+N/4` or
`-N/4` modulo `N`.  Hence

```text
Q+Q+Q is in the eight-node set,
3Q=-Q modulo the reciprocal lattice.
```

The eight-node classical subspace is exactly closed under the cubic force.
This repairs the continuum CI8 leakage only by defining a new lattice model
with reciprocal-lattice Umklapp.  It is not a proof that the previous
continuum PA-M2 node truncation was invariant.

The discrete stripe moment is phase sensitive:

```text
phase 0:     <cos^2>=1/2,    <cos^4>=1/2,
phase pi/4:  <cos^2>=1/2,    <cos^4>=1/4.
```

The unshifted cosine reaches only `-Vr^2/(8g)`.  In contrast,

```text
s_x=sqrt(2) cos(Q.x+pi/4)
```

is a sign field, satisfies every `B_i s=0`, and reaches the exact global value
`-Vr^2/(4g)`.  This explicitly dismisses the objection that the unshifted
cosine coefficient is the lattice ground energy.

The continuum cosine moment `3/8` and the continuum PA-M2 amplitude are not
inherited.  Increasing `N` at fixed spacing is a volume limit.  Sending the
spacing to zero moves the physical node `pi/(2a)` to the ultraviolet unless a
separate staggered continuum reduction is proved.

## 7. Harmonic critical dynamics

For the declared inertial Hamiltonian law,

```text
omega^2(k)=[r+4c sum_i cos(k_i)^2]/chi.
```

At `r=0` and `k=Q+p`,

```text
omega^2(Q+p)
 =(4c/chi)sum_i sin(p_i)^2
 =(4c/chi)|p|^2+O(|p|^4).
```

Thus the harmonic node has

```text
z=1,
c_star=2 sqrt(c/chi).
```

Moreover,

```text
sum_i cos(k_i)^2 sin(k_i)^2
 <=sum_i cos(k_i)^2,
```

For `r>0`, the harmonic gradient exists at every momentum and obeys

```text
|grad_k omega|<=2 sqrt(c/chi).
```

For `r=0`, this gradient statement holds only away from the eight nodes.  At a
node `omega` is conical and is not differentiable.  Nevertheless
`omega_0(k)=2 sqrt(c/chi)||cos k||_2` is globally Lipschitz, because the
componentwise cosine map is one-Lipschitz, with the same
`2 sqrt(c/chi)` directional-speed envelope.

This is one scalar-branch harmonic bound.  It is not a photon theorem, a
multi-field common-speed theorem, or a cutoff-uniform interacting causal
estimate.  The inertial time law was declared; it was not derived from the
static functional.

At `N=4` there is no small nonzero momentum near a node.  The analytic node
expansion is exact, but a numerical estimate of `z` or `c_star` must use an
`N=8,12,...` sequence or another controlled limit.

## 8. Low-energy concentration

For `r<0`, let `DeltaH=H-H_min`.  The complete square and the complement gap
give

```text
||P_Qperp phi||_2^2<=2 DeltaH/(c delta_N),
sum_x(phi_x^2+r/g)^2<=4 DeltaH/g.
```

At the exact minima the node concentration is exact rather than asymptotic.
For low-energy configurations the two inequalities control departure from the
node space and from constant magnitude independently.

## 9. Exact finite quantum parent and its limits

The fixed-`N` quantum Hamiltonian is

```text
H_N=-(hbar^2/(2chi)) Delta_R^V+U_r(phi)
```

on the infinite-dimensional Hilbert space `L2(R^V,dphi)`; only the
configuration dimension `V` is finite.  The potential is real, bounded below
and tends to positive infinity as `|phi|` tends to infinity.  Standard
Schrödinger-operator results
then give:

1. essential self-adjointness on `C_c^infinity(R^V)`;
2. a lower-bounded Friedrichs realization;
3. compact resolvent and discrete finite-multiplicity spectrum;
4. a positivity-improving Feynman--Kac semigroup;
5. a simple smooth ground eigenfunction that is strictly positive as a
   function of the field coordinates.

The last use of “positive” describes the wavefunction, not the sign of its
energy.

For every fixed `N` and fixed parameter tuple, the Hamiltonian has one unique
ground state.  Because the Hamiltonian commutes with translations and
`phi -> -phi`, that fixed-volume state is invariant under those symmetries and

```text
<phi_x>_0=0.
```

It does not choose one of the 256 classical wells.  A tunnelling or level-
splitting interpretation would require a separate semiclassical estimate.  A
pure ordered quantum phase requires a declared thermodynamic limit, pinning
field or boundary sector and an order of limits.  None is supplied here.

The standard prior-art anchors used for this scoped operator statement are:

- M. Shubin, [Essential self-adjointness for semi-bounded magnetic
  Schrödinger operators on non-compact manifolds](https://arxiv.org/abs/math/0007019).
- B. Simon, [Schrödinger semigroups](https://www.ams.org/bull/1982-07-03/S0273-0979-1982-15041-8/).
- W. G. Faris and B. Simon, [Degenerate and non-degenerate ground states for
  Schrödinger operators](https://doi.org/10.1215/S0012-7094-75-04251-9).

These are prior-art inputs, not new TECT theorems.

### 9.1 Raw quantum energy

The common-domain quadratic forms are an analytic family in `r`.  Equivalently,
for `r_2>r_1`, evaluation in the normalized ground state at `r_2` gives the
strict variational comparison

```text
E_0(r_2)>=E_0(r_1)+(r_2-r_1)<||phi||_2^2>_(r_2)/2>E_0(r_1).
```

The last expectation is strictly positive for every normalized `L2` state in
the form domain.  Standard analytic-form perturbation therefore also gives
continuity, while the displayed comparison gives strict increase.  At `r=0`,
the nonnegative operator cannot have a zero `L2` eigenfunction, so `E_0(0)>0`.

Around any exact classical sign minimum, take a product Gaussian with mean
square `R/g`, one-site variance `v>0`, and `R=-r>0`.  Its moments and stencil
variance are

```text
<phi_x^2>=R/g+v,
<phi_x^4>=(R/g)^2+6(R/g)v+3v^2,
<|B_i phi|^2>=2v.
```

The onsite, three-axis stiffness and kinetic contributions assemble to

```text
R(v)/V
 =-R^2/(4g)+(3c+R)v+(3g/4)v^2+hbar^2/(8chi v).
```

At fixed positive `c,g,chi,hbar,v`, its coefficient after division by `R^2`
tends to `-1/(4g)`.  The exact rational fixture
`R=20`, `c=g=chi=hbar=v=1` gives `-609/8<0`.  Thus `E_0(r)<0` for sufficiently
negative `r`.  The declared raw `C=0` convention consequently has exactly one
`r_E<0` with `E_0(r_E)=0`.

This is not a quantum phase transition.  Adding `C I` moves the raw zero
without changing the state or dynamics.

### 9.2 Why no finite occupation definition is used

In a finite-dimensional Hilbert space,

```text
tr[Q,P]=0
```

while exact CCR would require

```text
tr(i hbar I_D)=i hbar D !=0.
```

An occupation cutoff can be a Rayleigh--Ritz approximation, but it is not the
exact parent algebra and does not automatically inherit coordinate-space
positivity improvement or the uniqueness theorem.

### 9.3 Normal ordering changes more than the scalar zero

For a translation-invariant Gaussian covariance with diagonal value `C`,

```text
:phi_x^4:_C=phi_x^4-6C phi_x^2+3C^2.
```

Therefore Wick ordering the quartic while keeping the same symbol `r` changes
both the quadratic coefficient and an additive scalar.  A common energy ledger
must record the reference covariance and both compensating counterterms.  The
raw `C=0` model is used here precisely to avoid hiding that change.

## 10. What “below empty space” now means

The result has three distinct levels.

1. **Proved:** the ordered classical minima are below the zero-field
   configuration of the identical fixed Hamiltonian.
2. **Available after a new declaration:** if a normalized finite-energy
   quantum reference `Omega_nc` in the quadratic-form domain is declared in
   the same Hilbert space, the variational principle gives
   
   `E_0<=q_H[Omega_nc]`,
   
   strictly unless `Omega_nc` is the ground state.
3. **Not identified:** no record proves that either the zero configuration or
   a chosen Gaussian is physical empty space.

Defining “no condensate” only by `<phi>=0` is insufficient because the exact
finite ground state also has zero one-point function.  A reference must be
specified by its full state, algebra, regulator and observable criterion.

## 11. Exact boundary-selection obstruction

The finite Hamiltonian and its unique quantum ground state are translation
invariant.  Suppose a deterministic rule uses only these data and is covariant
under translations to select a set of boundary sites `B`.

The input is fixed by every lattice translation, so covariance requires `B`
to be fixed by every translation.  The translation group acts transitively on
the torus sites.  Its only invariant site subsets are therefore

```text
B=empty set
```

and

```text
B=Lambda_N.
```

No proper nonempty site boundary is selected.

This is a narrow no-go.  It does not exclude a state-conditioned sector, a
relational boundary, time-dependent characteristic sheets, a larger
relativistic parent, gravity or global causal structure.  It does show that a
periodic spatial boundary condition cannot be renamed a characteristic or
event-horizon derivation.

## 12. CP1 clause audit

The candidate supplies:

1. one declared finite-regulator family, interpreted separately at each fixed
   `N`;
2. one classical phase space and exact Weyl algebra;
3. one Hamiltonian formula;
4. one volume and periodic spatial boundary convention;
5. one `hbar` and field normalization;
6. one fixed-`N` counterterm and additive convention;
7. one ground-state rule yielding a unique state for each fixed `N` and fixed
   parameter tuple;
8. one exact classical interacting ordering sector.

It does not supply:

1. a characteristic-boundary map or reduction;
2. a PA-H1 boundary role;
3. a proof that the selected finite quantum ground chooses one ordered phase;
4. a single physical `r(tau)` history;
5. a continuum or cutoff-uniform interacting causal theorem.

Therefore

```text
CP1 complete = false.
```

## 13. Adversarial review

### Objection 1: “Dimension mismatch forbids a common parent.”

**DISMISSED at fixed lattice scope.**  The candidate defines one larger
canonical phase space and one exact Weyl algebra from the start.  It does not
identify the old six- and sixteen-dimensional fixtures unchanged.

### Objection 2: “Cubic closure is an `N=4` accident and fails at `N=8`.”

**DISMISSED for the declared nodes.**  At every `N=4m`, a node coordinate is
`+N/4` or `-N/4`; every triple sum is again one of those values modulo `N`.
Direct enumeration at `N=4,8,12` reproduces the eight-node closure.

### Objection 3: “The unshifted cosine gives only `-Vr^2/(8g)`.”

**VALID observation, invalid conclusion.**  Its discrete fourth moment is
`1/2`, so that value is correct for that restricted phase.  The quarter-shift
sign field has fourth moment `1/4`, saturates the complete-square lower bound,
and gives `-Vr^2/(4g)`.

### Objection 4: “The result proves the previous continuum PA-M2 theorem.”

**UPHELD as an overclaim prohibition.**  The lattice coefficients arise from
Umklapp and do not inherit the continuum moment `3/8`.  This is a new candidate
requiring its own continuum or staggered reduction.

### Objection 5: “The 256 classical minima are 256 quantum vacua.”

**UPHELD as an overclaim prohibition.**  At fixed `N` the full quantum ground
is simple and symmetry invariant.  Pure broken phases require additional
limits or sectors.

### Objection 6: “The negative classical energy proves energy below physical
empty space.”

**UPHELD as an overclaim prohibition.**  It proves a same-H zero-field sign.
Physical empty space and a quantum no-condensate reference remain unidentified.

### Objection 7: “The periodic torus is already the required boundary.”

**UPHELD as a fatal CP1 objection.**  Periodicity is a spatial boundary
condition, not a null characteristic sheet.  The transitivity lemma blocks a
proper site boundary selected only from the symmetric fixed-`N` data.

### Objection 8: “The harmonic speed is the speed of light.”

**UPHELD as an overclaim prohibition.**  It is one scalar harmonic group-speed
bound.  Gauge fields, other branches, interactions, regulator control and
gravity are absent.

### Objection 9: “The stationary ground state supplies cooling.”

**UPHELD.**  It supplies no nonconstant history.  Promoting `r` to a canonical
coordinate with a total-energy ledger is a CP2 task.

### Objection 10: “A finite oscillator cutoff is harmless.”

**UPHELD for the exact algebra.**  It violates exact CCR by the trace
obstruction.  Numerical compression must be treated only as a convergent
approximation.

External mathematical and physical review is invited.

## 14. Minimum repair and next proof target

One sufficient next route is a local parent with a regulator-level causal or
locality estimate.  Another admissible route must prove Lorentzian causal
emergence in a controlled limit.  Whichever route is chosen must:

1. have a cutoff-uniform causal estimate for every retained branch;
2. derive the ordering kernel as a controlled static or low-energy reduction;
3. derive two characteristic sheets, corner and constraint data;
4. prove the symplectic flux and bulk reconstruction map;
5. restrict or push the same selected parent state to the boundary algebra;
6. keep the same energy and counterterm ledger;
7. leave actual event-horizon language open until gravity and global causal
   structure are present.

Separately, CP2 must promote `r` to a dynamical coordinate or derive it from a
nonstationary interacting state, then prove a finite-time `r=0` crossing with
the total work and energy ledger.

## 15. Reproduction

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_lt3_rs_common_container.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_lt3_rs_common_container_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_lt3_rs_common_container_verify.py --self-test
```

The primary route uses exact symbolic identities and finite lattice
enumerations.  The independent route does not import it; it reconstructs
`N=4,8,12` symbols, triple sums, all parity-cell minima, all kernel stationary
fields, exact rational energies and a direct Fourier transform.

## 16. Prior-art and novelty boundary

Finite anharmonic lattice Hamiltonians, confining Schrödinger operators,
Feynman--Kac positivity, unique finite-volume ground states, Weyl CCR
representations, lattice Fourier symbols, Umklapp and Landau-type classical
bifurcations are established mathematics and physics.  Constructive continuum
field theory also has much stronger model-specific precedents, for example
Glimm and Jaffe's [cutoff-removal work on the two-dimensional interacting
field](https://annals.math.princeton.edu/1970/91-2/p04).

The repository-specific contribution is the exact audit of this declared
local repair against the PA-H1/PA-M2 incompatibility contract, including the
same-H reference result and the boundary-selection failure.  No world-first
claim is made.

## 17. Final boundary

This package proves a fixed-regulator classical ordering theorem and invokes
standard finite-lattice quantum ground-state theorems under explicit
hypotheses.  It does not inherit the continuum PA-M2 quartic coefficients,
select a quantum broken-symmetry pattern, prove a thermodynamic or quantum
phase transition, identify physical empty space, derive PA-H1, a
characteristic or event horizon, cooling, gravity, a continuum limit, CP1
completion, or Pre-A.
