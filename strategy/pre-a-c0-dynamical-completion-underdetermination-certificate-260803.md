# Pre-A C0 dynamical-completion underdetermination certificate

**Candidate:** `PA-C0-DYNAMICAL-COMPLETION-NOGO-v0`  
**Authority:** T0 scoped no-go certificate; no TECT claim or tier change  
**Claim context only:** `C6-SPACETIME-SIGNATURE`, with
`A2-FULL-PRODUCTION-WELLPOSED` as a comparison context  
**Task:** `T-054`  
**Issued:** 2026-08-03

## 1. Question and exact answer

The current PA-M2 package starts from a static spatial functional and then
separately declares an inertial Hamiltonian.  This certificate asks whether
the time law, the low-energy exponent, or a causal cone already follows from
the static functional.

The exact answer is no in the following limited sense:

> A time-independent static functional, its critical set, and its spatial
> Hessian do not uniquely identify a temporal completion.  The same static
> data admit inequivalent dissipative and inertial dynamics.  Additional
> kinetic, symplectic, clock, bath, or update-law data are therefore required.

This is a nonidentifiability theorem about the declared input.  It is not a
claim that time or causal order can never emerge from a richer microscopic
theory.  An action with time derivatives, a transfer matrix, reflection
positivity, a microscopic update rule, or a symplectic form already contains
extra data excluded from this theorem's input.

## 2. Finite-dimensional theorem

Let `X_N` be a finite real Galerkin configuration space and let

```text
F:X_N -> R
```

be `C2` and time independent.  Assume that the data called *static* contain
neither a temporal derivative law nor a kinetic metric, mobility, bath,
symplectic form, noise law, clock normalization, or temporal boundary
condition.  At `u_* in Crit(F)`, write

```text
L=D2 F(u_*).
```

For arbitrary `gamma>0` and `chi>0`, two completions are

```text
gradient:  u_t=-gamma grad F(u),
inertial:  chi u_tt=-grad F(u).
```

The gradient used here is itself defined only after a configuration-space
metric has been selected.  That choice is part of the completion, not an
output of the scalar values of `F`.

### Theorem PA-C0-N

The two completions have the same time-independent configuration equilibria,
namely `Crit(F)`, and the same static Hessian `L`.  In inertial phase space the
equilibria are `Crit(F) x {0}`.  On a positive Hessian eigenmode

```text
L e=ell e,  ell>0,
```

their linear characteristic equations and roots are

```text
gradient:  s+gamma ell=0,       s=-gamma ell,
inertial:  chi s^2+ell=0,       s=+/- i sqrt(ell/chi).
```

The gradient equation needs one initial datum per mode and generates a
contractive forward semigroup.  The inertial equation needs two initial data
per mode and generates a reversible oscillatory group.  A real positive
constant rescaling of time cannot change a nonzero negative-real root into an
imaginary conjugate pair, nor can it change first temporal order into second
order.  The completions are therefore dynamically inequivalent.

### Energy identities

Along the gradient completion,

```text
dF/dt=-gamma ||grad F||^2<=0.
```

Along the inertial completion,

```text
d/dt [chi ||u_t||^2/2+F(u)]
 =<u_t,chi u_tt+grad F>=0.
```

In finite Galerkin dimension the reversed law

```text
u_t=+gamma grad F(u)
```

is also a locally well-posed completion of the same static function and has
`dF/dt=+gamma||grad F||^2`.  Requiring stable relaxation would add the
Lyapunov-arrow condition and select the minus sign; that requirement is not
contained in `F` alone.  The exact conclusion is therefore that static data do
not decide between an irreversible semigroup and a reversible group, nor do
they supply a physical arrow of time.

At `ell=0`, the boundary is also different: the gradient zero mode is
constant, whereas the inertial zero mode is `a+b t`.  This reinforces rather
than removes the need for a temporal completion.

## 3. Exact causal-support witness

Consider the common infrared spatial functional on the real line

```text
F_IR[u]=(A/2) int |partial_x u|^2 dx,  A>0.
```

Its static Hessian is `-A partial_x^2`.  With an added mobility `M>0`, its
gradient completion is the heat equation

```text
u_t=M A u_xx.
```

For point data its kernel is

```text
G(x,t)=exp[-x^2/(4 M A t)]/sqrt(4 pi M A t),  t>0.
```

The primary script verifies `G_t-M A G_xx=0`.  Every factor is strictly
positive for every finite real `x` and `t>0`, so compact initial support
immediately develops nonzero tails everywhere.

With an added inertia `chi>0`, the same spatial functional gives

```text
chi u_tt=A u_xx,
v=sqrt(A/chi),
u(x,t)=f(x-vt)+g(x+vt).
```

The scripts verify the wave equation exactly.  Compactly supported profiles
remain inside the d'Alembert domain of dependence.  Thus one static Hessian is
compatible with a parabolic equation having instantaneous tails and with a
hyperbolic equation having finite propagation.  No unique spacetime principal
symbol or null cone follows from the static Hessian alone.  A cone may still emerge
after a microscopic kinetic law is supplied or derived.

For two otherwise identical static copies with inertias `chi_1` and `chi_2`,

```text
v_1^2/v_2^2=chi_2/chi_1.
```

This dimensionless relative-speed freedom cannot be removed by one common
change of time units.  It shows what a multi-sector theory must fix before a
shared physical speed can be claimed.

## 4. Exact PA-M2 critical-node corollary

The PA-M2 static symbol is

```text
K_r(k)=r+c sum_i (k_i^2-q^2)^2,  c>0, q>0.
```

At `Q_sigma=(sigma_1 q,sigma_2 q,sigma_3 q)`,

```text
K_r(Q_sigma+p)
 =r+4 c q^2 |p|^2
   +4 c q sum_i sigma_i p_i^3
   +c sum_i p_i^4,
D2 K_0(Q_sigma)=8 c q^2 I_3.
```

At `r=0`, along a coordinate ray from `Q=(q,q,q)`,

```text
K_0(Q+epsilon e_1)=c epsilon^2(2q+epsilon)^2.
```

The symmetric average cancels the cubic term exactly:

```text
[K_0(Q+epsilon e_1)+K_0(Q-epsilon e_1)]/2
 =c epsilon^2(4q^2+epsilon^2).
```

After a gradient law is added,

```text
Gamma_G=gamma K_0
       =4 gamma c q^2 epsilon^2+O(epsilon^3),
z_G=2.
```

After an inertial law is added,

```text
omega_I^2=K_0/chi,
omega_I=2q sqrt(c/chi) epsilon+O(epsilon^2),
z_I=1,
c_IR=2q sqrt(c/chi).
```

These are Gaussian, tree-level, gapless-boundary exponents.  At fixed finite
`L`, momentum is discrete and there is no literal `p->0` limit.  The exponent
is a formal local-dispersion statement or a statement along a commensurate volume family,
for example `L_N=2 pi N/q` with fixed `q` and `N->infinity`.
It is not an interacting critical exponent.

The static functional does not contain `chi`.  For any declared positive
target slope `c_target`, choosing

```text
chi=4 c q^2/c_target^2
```

reproduces it.  For one sector this includes a choice of clock units; for two
or more sectors the relative-speed ratios remain dimensionless extra data.

Important boundaries are:

- for `r>0` the node is gapped and no gapless `z` is asserted;
- for `r<0` the zero-background gradient and inertial modes are linearly
  unstable, so the displayed critical exponents do not describe a stable
  disordered state;
- at `q=0`, the leading kernel is `c|p|^4`, giving Gaussian `z_G=4` and
  `z_I=2`, rather than `2` and `1`;
- interactions, conserved quantities, noise, and renormalization may change
  the physical dynamical universality class.

Most importantly, the PA-M2 node slope is not a global limiting speed.  Along
`k=(q+R,q,q)`, `R>0`, the positive-frequency inertial branch is

```text
omega=sqrt(c/chi)[(q+R)^2-q^2],
d omega/dR=2 sqrt(c/chi)(q+R),
```

which is unbounded as `R->infinity`.  The exact fourth-order PA-M2 continuum
operator therefore has no certified microscopic relativistic light cone.  Its
`z=1` result is only a low-energy node asymptotic after inertial dynamics has
been inserted.

## 5. What the theorem proves for C0

The forgetful map

```text
declared dynamical completions -> retained static functional
```

is non-injective on the explicit examples.  Consequently PA-M2's static
sector cannot, by itself, close the causal-origin gate `C0`.

Pre-A must now choose and prove one of two honest routes:

1. **C0-A:** declare a primitive causal or temporal update structure.  Then it
   is an input and cannot also be counted as emergent, although a richer
   continuum Lorentzian geometry may still be derived from it.
2. **C0-B:** begin from a premetric substrate and derive causal order, a clock,
   the temporal kinetic law, and the continuum null structure upstream of
   PA-H1.

The theorem does not select between these routes.  It only eliminates the
shortcut from a static free energy directly to a unique physical time law or
speed of light.

## 6. Relation to the existing Pre-A lanes

`PA-H1-DNKG4-v0` proves fixed-background double-null reconstruction after a
1+1 Lorentzian causal structure, time slicing, and field equation are supplied.
It therefore sits downstream of C0 and cannot solve the causal-origin gate.

`PA-M2-CI8-RS-v0` proves a separate three-dimensional static onset theorem and
a conditional inertial low-energy cone.  This certificate proves why that
inertial completion must remain in its inserted-input ledger.  It does not invalidate the PA-M2 variational theorem.

There is still no proved composition map

```text
C0 microscopic law
 -> PA-H1 boundary state and reconstructed bulk
 -> PA-M2 state, normalization, and r(tau).
```

Pre-A is therefore not complete.

## 7. Input-output ledger

Inserted for the no-go witnesses:

- a finite real Galerkin space and a `C2` static function;
- a selected Euclidean/L2 metric when a gradient is written;
- separately chosen mobility `gamma` or inertia `chi`;
- for the causal-support example, an already given spatial line;
- for the PA-M2 corollary, its already declared three-dimensional static
  symbol and critical node.

Derived:

- equality of the static critical sets and Hessians;
- inequivalent temporal orders and generator spectra;
- exact dissipative and conservative energy identities;
- parabolic versus hyperbolic causal-support behavior for one spatial Hessian;
- conditional PA-M2 Gaussian `z=2` versus `z=1` behavior;
- freedom of the inertial node slope and failure of a global PA-M2 limiting
  speed.

Not derived:

- a microscopic time variable, causal order, signature, null structure, or
  physical arrow of time;
- a physical kinetic coefficient, light speed, shared cross-sector cone, or
  interacting exponent;
- a boundary algebra or preferred state;
- Einstein dynamics, an event horizon, cosmic cooling, a phase-history map, or
  the PA-H1-to-PA-M2 composition;
- completion of Pre-A or Sector A.

## 8. Devil's-advocate review

1. **The gradient flow is canonical once `F` is known.**
   **UPHELD AS AN EXTRA-INPUT OBJECTION.**  A gradient requires a metric,
   mobility, bath interpretation, and sign.  Those are not scalar values of
   `F`.
2. **Calling `F` a potential energy forces inertial dynamics.**
   **UPHELD AS AN EXTRA-INPUT OBJECTION.**  It additionally requires phase
   space, a kinetic metric, and `chi`; the latter controls the node slope.
3. **A Euclidean or Lorentzian action can determine a time law.**
   **DISMISSED AS A COUNTEREXAMPLE TO THIS SCOPE.**  Such an action contains
   frequency or temporal information that the static-only hypothesis excludes.
4. **The PA-M2 `z=1` result proves Lorentzian causality.**
   **UPHELD.**  It is only an inserted-inertia infrared asymptotic.  The full
   kernel has unbounded high-frequency group speed.
5. **The quoted `z` values are physical critical exponents.**
   **UPHELD.**  They are Gaussian and tree level; interactions and
   conservation laws remain unanalysed.
6. **A fixed finite torus has no infrared limit.**
   **UPHELD.**  The statement is restricted to formal local momentum or a
   declared commensurate volume sequence.
7. **Changing `chi` is merely changing time units.**
   **VALID WITH MITIGATION.**  For one isolated sector an absolute speed needs
   a clock convention.  The two-copy fixture leaves an invariant relative
   speed, so multi-sector common-speed claims still require extra dynamics.
8. **The no-go proves that time cannot emerge.**
   **DISMISSED.**  It proves only that the current static input is insufficient;
   a richer C0-B microscopic structure remains an open route.

## 9. Reproducible evidence and next gate

Primary:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0_dynamical_completion_underdetermination.py
```

Independent non-importing audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0_dynamical_completion_underdetermination_independent.py
```

Integrated verifier:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0_dynamical_completion_underdetermination_verify.py
```

The next constructive gate is not to choose `chi` by fit.  It is to define a
non-circular C0-A or C0-B microscopic model and derive one temporal/causal law
from its own axioms.  Only then can PA-H1 be interpreted as a continuum
boundary theorem and only after that can a state, energy normalization, and
`r(tau)` history be mapped into PA-M2.
