# Pre-A Gaussian/CCR to PA-H1 finite-image embedding certificate

**Candidate:** `PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0`  
**Authority:** T0 C0-A/PA-H1 bridge certificate; no TECT claim or tier change  
**Claim context only:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Issued:** 2026-08-03

## 1. Result and novelty boundary

This package proves an exact state-bearing interface between two already
declared TECT benchmarks:

1. a finite-spatial-mode Gaussian Mehler semigroup with its infinite-occupation
   Fock/CCR representation; and
2. the fixed-background PA-H1 characteristic reconstruction.

For an inserted positive Klein--Gordon frequency matrix, the Euclidean
semigroup reconstructs an unbounded nonnegative Hamiltonian, a pure quasi-free
vacuum, and real-time oscillator evolution.  Explicit characteristic traces
then embed the same phase space and state into the finite reconstructed PA-H1
image while preserving the symplectic form and the raw Klein--Gordon energy.

The general Gaussian reconstruction is established mathematics, not a new TECT
theorem.  Time-reflection reconstruction belongs to the Osterwalder--Schrader
and Nelson Markov-field programme; Wiener--Itô second quantisation supplies the
Ornstein--Uhlenbeck spectrum.  Characteristic boundary algebras and state
transport also have established antecedents.  The TECT-specific result here is
the explicit audited compatibility map to the exact PA-H1 conventions, its
normalisation ledger, and its falsifiers.

Primary and technical antecedents:

- K. Osterwalder and R. Schrader, *Axioms for Euclidean Green's functions*,
  https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-31/issue-2/Axioms-for-Euclidean-Greens-functions/cmp/1103858969.pdf .
- K. Osterwalder and R. Schrader, *Axioms for Euclidean Green's functions II*,
  https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-42/issue-3/Axioms-for-Euclidean-Greens-functions-II-with-an-Appendix-by/cmp/1103899050.pdf .
- E. Nelson, *The free Markoff field*,
  https://doi.org/10.1016/0022-1236(73)90025-6 .
- J. M. A. M. van Neerven, *Second quantization and the L-p-spectrum of
  nonsymmetric Ornstein--Uhlenbeck operators*,
  https://arxiv.org/abs/math-ph/0509057 .
- C. Gerard and M. Wrochna, *Construction of Hadamard states by characteristic
  Cauchy problem*, https://arxiv.org/abs/1409.6691 .

No bounded search can establish a global world-first absence result.  The
proper novelty statement is therefore: no new general Mehler, CCR,
Osterwalder--Schrader, or characteristic-state theorem is claimed; the local
contribution is this repository-specific exact interface and proof ledger.

## 2. Gaussian Mehler and time-reflection theorem

Let `E=R^N`, fix `hbar=1`, and insert a real positive-definite frequency
matrix `Omega`.  Set

```text
C=(2 Omega)^(-1),
d gamma(q)=sqrt(det(Omega)/pi^N) exp(-q.Omega.q)dq,
M_t=exp(-t Omega),
Q_t=C-M_t C M_t.
```

Define

```text
(P_t f)(q)=int f(M_t q+sqrt(I-M_t^2)y)d gamma(y).
```

### Theorem PA-C0A-GM

`P_t` is a strongly continuous, self-adjoint, positivity-preserving Markov
contraction semigroup on `L2(gamma)`.  Its two-sided stationary process has

```text
E[Q_s Q_t^T]=C exp(-Omega |t-s|).
```

Stationarity follows from

```text
M_t C M_t+Q_t=C,
Q_(s+t)=Q_s+M_s Q_t M_s.
```

Reversibility is `M_t C=C M_t`.  For every future-measurable square-integrable
functional `F`, conditioning at the reflection surface gives the full
time-reflection identity

```text
E[conj(F(theta Q))F(Q)]
 =||E[F|Q_0]||_L2(gamma)^2>=0.
```

For linear insertions at nonnegative times, the same result is visible as

```text
sum_ij z_i^* C exp[-Omega(t_i+t_j)] z_j
 =1/2 ||sum_i exp(-t_i Omega)Omega^(-1/2)z_i||^2>=0.
```

This reconstructs dynamics from an already supplied Euclidean time order,
reflection, scale, drift, and covariance.  The stationary process is
time-reflection symmetric, so it does not derive a physical arrow of time.

## 3. Infinite occupation, spectrum, and the unbounded logarithm

The Wiener--Itô decomposition gives

```text
L2(gamma)=Gamma_s(E_C),
P_t=Gamma(exp(-t Omega)),
H=dGamma(Omega).
```

If `Omega e_j=omega_j e_j`, product Hermites obey

```text
H h_n=(n.omega)h_n,
P_t h_n=exp[-t(n.omega)]h_n.
```

Consequently, for every `t>0`, `P_t` is injective and
`<f,P_t f>>0` for every nonzero `f`, but it is not bounded below by a positive
constant.  Its eigenvalues accumulate at zero:

```text
0 in spec(P_t),  0 is not an eigenvalue,
inf spec(P_t)=0, ker(P_t)={0}.
```

The exact logarithm is therefore an unbounded spectral-calculus identity,

```text
H=-(1/t)log P_t,
D(H)={sum_n c_n h_n: sum_n (n.omega)^2 |c_n|^2<infinity}.
```

This is the sharp boundary between the earlier finite-state C0-A theorem and a
field oscillator.  The finite-state phrase `0<P` meant a uniform positive
lower bound because the Hilbert space was finite-dimensional.  It may not be
reused here.  For finitely many positive frequencies the vacuum `1` is unique,
the gap is `min_j omega_j`, and

```text
Tr P_t=product_j(1-exp(-t omega_j))^(-1).
```

There are finitely many spatial modes but infinitely many occupation states.
Any finite occupation cutoff fails exact CCR.  At cutoff `K`,

```text
[a_K,a_K^*]=I-(K+1)|K><K|,
```

whose trace is zero rather than the trace of `I`.

## 4. Quasi-free CCR state and the energy offset

On `V=E direct-sum E`, write `y=(q,p)` and

```text
sigma(y,z)=q.p_z-p.q_z,
J(q,p)=(-Omega^(-1)p,Omega q),
mu_V(y,z)=sigma(y,Jz).
```

Then

```text
J^2=-I,
J^T sigma J=sigma,
mu_V(y,y)=q.Omega.q+p.Omega^(-1).p>0.
```

With the Weyl convention

```text
W(y)W(z)=exp[-i sigma(y,z)/2]W(y+z),
```

the compatible pure quasi-free state is

```text
omega_0(W(y))=exp[-mu_V(y,y)/4].
```

On the Gaussian Schrodinger core,

```text
Q_j=q_j,
P_j=-i(partial_j-(Omega q)_j),
[Q_j,P_k]=i delta_jk.
```

The ground-state transform gives exactly

```text
H=sum_j[-1/2 partial_j^2+omega_j q_j partial_j]
 =1/2(P.P+Q.Omega^2.Q)-1/2 Tr Omega
 =H_osc-E_0,
E_0=1/2 Tr Omega.
```

Thus the Markov normalisation sets the vacuum eigenvalue to zero; it does not
derive an absolute energy.  In the exact three-mode fixture below,
`E_0=13/2`.  Adding more modes makes the unrenormalised zero-point sum diverge.
Accordingly this certificate does **not** prove that its state is below empty
space, below a no-condensate state, or the physical cosmological vacuum.  Such
a statement requires a common regulator, volume, boundary convention,
counterterm, and reference state on both sides of the comparison.

The covariance normalisation also remains an input.  The same Gaussian
marginal `C=1/2` supports reversible OU drifts with gaps one and two and,
at `t=log 2`, transfers `1/2` and `1/4`.  Reflection positivity and a static
marginal therefore do not select the drift or the `hbar`/CCR normalisation.

## 5. Exact PA-H1 finite-image embedding

Choose the fixed PA-H1 cylinder fixture

```text
L=U=V=pi/2,  tau=pi/4,  mu=3,  kappa=9/4,
e0=sqrt(2/pi),
ec=2 cos(4x)/sqrt(pi),
es=2 sin(4x)/sqrt(pi),
Omega=diag(3,5,5).
```

The modes are real, orthonormal on `[-tau,tau]`, and diagonalise
`-partial_x^2+9`.  For initial coefficient data `y=(q,p)` at `t=0`, let

```text
phi_y(t,x)=sum_j e_j(x)
 [q_j cos(omega_j t)+(p_j/omega_j)sin(omega_j t)].
```

Define its complete characteristic traces

```text
T(y)=(A_y,B_y),
A_y(u)=phi_y(u/2,u/2),
B_y(v)=phi_y(v/2,-v/2).
```

Every mode solves

```text
partial_u partial_v phi+(9/4)phi=0,
```

and the traces satisfy the corner condition.  Let

```text
S_tau=[[cos(Omega tau),Omega^(-1)sin(Omega tau)],
       [-Omega sin(Omega tau),cos(Omega tau)]].
```

The already certified PA-H1 uniqueness theorem and direct coefficient
extraction give the exact finite-image identity

```text
P_tau T=S_tau.
```

Direct Fourier integration of all 36 cross terms gives

```text
Omega_H(Ty,Tz)=sigma(y,z),
E_H(Ty)=E_KG(y)=1/2[p.p+q.Omega^2.q].
```

In the order `(q0,qc,qs,p0,pc,ps)`, the boundary symplectic matrix is

```text
[[0,I3],[-I3,0]],
```

and the boundary-energy matrix is

```text
diag(9/2,25/2,25/2,1/2,1/2,1/2).
```

The quasi-free state therefore pulls to the image Weyl algebra by

```text
omega_H(W(Ty))=omega_0(W(y)),
omega_Sigma(W(P_tau Ty))=omega_H(W(Ty)).
```

This is a state only on the finite symplectic image.  It is not a selected
state on the full PA-H1 algebra.  Two different quasi-free states on a
symplectic complement give distinct full extensions that agree exactly on the
image, so the extension is nonunique.

The identity is an exact embedding/propagation calibration for a spectral
invariant mode space.  A generic Galerkin subspace is not dynamically
invariant: with `K=diag(1,4)` and
`e=(1,1)/sqrt(2)`,

```text
||(I-|e><e|)Ke||^2=9/4.
```

Therefore a generic fixed-slice symplectic embedding must not be advertised as
a dynamical intertwiner.

## 6. Controlled Galerkin covariance tail and its boundary

For the full fixed cylinder, let

```text
omega_n=sqrt(9+16 n^2)
```

and let `Pi_N` be the exact spectral projection onto `|n|<=N`.  For smooth
real data with

```text
||q||_s^2=sum_n omega_n^(2s)|q_n|^2,
||p||_(s-1)^2=sum_n omega_n^(2s-2)|p_n|^2,
s>3/2,
```

one has

```text
0<=mu_infinity(y,y)-mu_N(y,y)
 <=omega_(N+1)^(1-2s)
   [||q||_s^2+||p||_(s-1)^2].
```

Because `|exp(-a)-exp(-b)|<=|a-b|` for nonnegative `a,b`, the finite and
infinite characteristic functionals compare, under the canonical inclusion of
the finite spectral subalgebra, as

```text
|omega_infinity(W_infinity(y))-omega_N(W_N(Pi_N y))|
 <=[mu_infinity(y,y)-mu_N(y,y)]/4.
```

Here `mu_N` is evaluated only on the finite phase space `Pi_N V`; it is not
extended by zero and called a state on the full Weyl algebra.  Such a zero
extension would violate the uncertainty condition on every omitted canonical
pair.  The estimate is only a cross-algebra pointwise characteristic comparison
on the declared smooth domain, and it yields no unique full-state extension or
weak-star conclusion.  The same spectral projections give compact-time strong
classical-flow convergence for fixed finite-energy data.  This is not
operator-norm convergence, an interacting limit, an infinite-volume limit, or
a microlocal Hadamard certificate.  A finite spectral projector is spatially
nonlocal: its kernel is nonzero at distinct points, so the cutoff field does
not have an exact local commutator delta function or a derived causal cone.

## 7. Exact hostile controls and adversarial review

The primary and non-importing independent implementations certify the positive
fixture and the following failure boundaries.

1. **Negative transfer.**  A stationary reversible scalar Gaussian AR(1) with
   `rho=-1/2` and variance `1/2` has positive transition noise `3/8`, but its
   first-chaos link form is `-1/4`.  Markov positivity and reversibility do not
   imply link reflection positivity.
2. **Zero transfer.**  `rho=0` is link-positive but kills every nonconstant
   chaos, so no finite logarithmic generator exists.
3. **No uniform lower bound.**  The positive Mehler eigenvalues
   `2^(-3n)` tend to zero; the generator is unbounded.
4. **Zero mode.**  At `omega=0`, `(2omega)^(-1)` diverges.  The periodic
   massless zero mode has neither the declared normalisable Gaussian nor the
   unique gapped vacuum.
5. **Negative frequency.**  At `omega=-1`, `exp(-t omega)` expands rather than
   contracts and the positive-energy construction fails.
6. **Finite occupation.**  The four-level commutator is
   `diag(1,1,1,-3)`, not `I`.
7. **Finite-rank nonlocality.**  The three-mode projection kernel at
   `x=0`, `y=pi/8` is `2/pi`, although the points are distinct.
8. **Nonunique extension.**  Complement frequencies two and seven produce
   full Gaussian states that agree on the finite image and differ off it.
9. **Noninvariant cutoff.**  The explicit residual above prevents a generic
   Galerkin embedding from being a dynamical intertwiner.

The code-discipline review is explicit:

- **Sign:** the `rho=-1/2` control distinguishes a positive transition density
  from a positive operator/reflection form; the symplectic sign is reproduced
  independently with an initial-slice and a top-slice convention.
- **Factor and convention:** the Weyl factor `1/2`, quasi-free factor `1/4`,
  `u+v=2 tau`, `kappa=mu^2/4`, raw-energy factor `1/2`, and the normal-order
  shift `Tr(Omega)/2` are pinned in the note and executables.
- **Units:** the circle length, time spacing, mass, and `hbar=1` are
  dimensionless benchmark inputs.  None is reported as a measured cosmic
  number or a predicted constant.
- **Convergence:** spatial-mode removal, occupation growth, zero-mode/IR,
  infinite volume, interacting limits, and zero-point renormalisation are kept
  separate.  Only the displayed smooth spectral covariance tail is proved.
- **Hardcode masking:** the primary derives frequencies, covariance, transfer,
  flow, boundary Grams, and controls from upstream fixture data.  The
  non-importing implementation uses a different top-slice-centred Fourier
  representation and exact rational covariance arithmetic.  Exact displayed
  values in the integrated verifier are labelled fixture test oracles.
- **Limit cases:** zero and negative frequency, zero and negative transfer,
  infinite occupation, finite occupation, nonlocal finite rank, noninvariant
  projection, and nonunique extension are all exercised.

External review is invited specifically on the Weyl/Schrodinger convention,
the boundary energy orientation, the Sobolev tail domain, and the distinction
between finite-image state selection and full-algebra state selection.

## 8. Pre-A verdict

This package closes a narrow calibration question:

> Once a positive local KG spectrum, Euclidean time/reflection, Gaussian
> normalisation, and ground-state criterion are inserted, they define a
> strongly continuous Gaussian transfer with an unbounded positive generator,
> a quasi-free CCR vacuum, and an exact state-, symplectic-, and energy-bearing
> embedding into a finite PA-H1 characteristic image.

It does not close C0 or Pre-A.  The inserted inputs include the Lorentzian
background, KG dispersion, mass, circle, time order and scale, `hbar=1`,
positive-frequency choice, Gaussian covariance, and spectral truncation.
Open gates remain:

- physical selection of C0-A rather than another temporal branch;
- derivation of the time order, clock scale, and arrow;
- `hbar` and covariance normalisation;
- zero-mode and infrared treatment;
- UV/full-algebra extension and a Hadamard theorem;
- locality and a protected causal cone after regulator removal;
- an interacting boundary state;
- common-reference vacuum energy, including the no-condensate comparison;
- gravity, event-horizon meaning, and cosmic scale;
- a common parent law and explicit PA-H1-to-PA-M2 composition; and
- a derived cooling/control history `r(tau)`.

The next load-bearing step is not another free-state calculation.  It is a
common parent state and energy normalisation whose controlled history produces
the PA-M2 control parameter without changing regulator, volume, boundary, or
reference conventions.
