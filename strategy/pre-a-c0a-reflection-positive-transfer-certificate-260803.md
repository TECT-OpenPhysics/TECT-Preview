# Pre-A C0-A reflection-positive transfer certificate

**Candidate:** `PA-C0A-RPTM-FS-v0`  
**Authority:** T0 C0-A calibration certificate; no TECT claim or tier change  
**Claim context only:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Issued:** 2026-08-03

## 1. Why this is the first constructive C0-A temporal benchmark

`PA-C0-DYNAMICAL-COMPLETION-NOGO-v0` proves that a static functional alone
does not select a temporal law.  The smallest constructive response is to add
the missing data explicitly and ask whether they are sufficient.

This certificate declares a finite-state transfer operator, a discrete time
ordering, a reflection, and a positive time spacing as C0-A primitives.  It
then reconstructs a positive self-adjoint generator and a real-time unitary
group exactly.  It does not call the declared temporal primitives emergent.
Because it has no space, influence relation, cone, or null structure, it is a
C0-A temporal calibration rather than a full C0-A causal candidate.

This is a finite calibration of the reflection-positive Euclidean
reconstruction strategy pioneered by Osterwalder and Schrader.  It is not a
new general reconstruction theorem and not yet a field theory.

Primary references:

- K. Osterwalder and R. Schrader, *Axioms for Euclidean Green's functions*,
  https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-31/issue-2/Axioms-for-Euclidean-Greens-functions/cmp/1103858969.pdf .
- K. Osterwalder and R. Schrader, *Axioms for Euclidean Green's functions II*,
  https://projecteuclid.org/journals/communications-in-mathematical-physics/volume-42/issue-3/Axioms-for-Euclidean-Greens-functions-II-with-an-Appendix-by/cmp/1103899050.pdf .

## 2. General finite-state theorem

Let `X` be a finite set with at least two points, let `pi_x>0` with
`sum_x pi_x=1`, and let `P` act on the complex Hilbert space
`L2(X,pi;C)`.  Declare

```text
P 1=1,
P_xy>=0,
pi_x P_xy=pi_y P_yx,
0<P<=I,
a>0.
```

The first three conditions make `P` a reversible Markov transfer.  The strict
operator inequality is an additional spectral condition: all eigenvalues of
`P` on `L2(X,pi)` lie in `(0,1]`.  Entrywise nonnegativity and operator
positivity are logically independent, so neither condition may be omitted.
The number `a`, the ordering of transfer steps, and the reflection operation
are inputs.

### Theorem PA-C0A-T

The spectral functional calculus defines

```text
H_a=-(1/a) log P.
```

It is the unique nonnegative self-adjoint operator satisfying

```text
P=exp(-a H_a).
```

Consequently

```text
U(t)=exp(-i t H_a)
```

is a strongly continuous unitary group.  If `P` is irreducible, its constant
eigenvector at eigenvalue one is simple, so
`ker(H_a)=span{1}`.  Equivalently, the ground-state ray is unique and its
normalized strictly-positive real representative is `1`.  If `lambda_1` is
the largest eigenvalue below one, the
finite gap is

```text
Delta_a=-(1/a) log lambda_1.
```

### Proof

Detailed balance is exactly self-adjointness in `L2(X,pi)`.  Strict positivity
and finite dimension permit the unique real logarithm on the spectrum.
Because `0<P<=I`, every eigenvalue of `-log P` is nonnegative.  Exponentiation
recovers `P` eigenvalue by eigenvalue.  Multiplication by `-i` then gives the
unitary group.  Irreducibility makes the Perron eigenvalue one simple.

This theorem reconstructs dynamics from the *full transfer data*.  It does not
reconstruct `P` from the one-time probability `pi` or a static energy alone.

## 3. Reflection-positivity identities

Let a two-sided stationary reversible Markov path have the declared transfer
`P`.

For reflection about a site, condition on the state at the reflection site.
Past and future are conditionally independent and reversibility makes their
conditional laws mirror each other.  For every square-integrable
future-measurable functional `F`, writing `h(x)=E[F|X_0=x]`,

```text
E[conj(F(theta X)) F(X)]
 =sum_x pi_x |E[F|X_0=x]|^2>=0.
```

This is site-reflection positivity.  It is a conditional-square identity and
does not by itself require a positive transfer spectrum.

For reflection through a link, the corresponding one-link form is

```text
E[conj(F(theta X))F(X)]=<h,Ph>_pi,
h(x)=E[F|X_1=x].
```

It is nonnegative for every `h` exactly when `P>=0` on `L2(X,pi)`.  This is why
entrywise transition positivity and detailed balance alone are insufficient
for the positive-log reconstruction.

The converse implication also fails.  With uniform `pi`,
`v=(1,1,-2)`, and

```text
P_op=I-(1/10)vv^T,
```

one has `P_op 1=1`, detailed balance, and spectrum `{1,1,2/5}`, hence
`0<P_op<=I`; nevertheless `(P_op)_12=-1/10`.  Operator positivity therefore
does not supply the missing Markov condition.

## 4. Exact three-state fixture

Choose

```text
pi=(1/2,1/3,1/6),
(Pi_pi f)(x)=sum_y pi_y f(y),
alpha=2/3,
P=alpha I+(1-alpha) Pi_pi.
```

The static probability may be represented at inverse temperature one by

```text
F=(log 2,log 3,log 6)
```

up to an additive constant.  The scripts verify exactly that `Pi_pi` is a
projector, `P` is stochastic, stationary, detailed-balanced, and has spectrum

```text
spec(P)={1,2/3,2/3}.
```

Writing `Q=I-Pi_pi`,

```text
P=Pi_pi+(2/3)Q,
H_a=[log(3/2)/a] Q,
exp(-aH_a)=P,
spec(H_a)={0,log(3/2)/a,log(3/2)/a}.
```

The exact positivity identity is

```text
<f,Qf>_pi
 =sum_(x<y) pi_x pi_y (f_x-f_y)^2>=0.
```

Thus constants are the unique kernel direction.  The real-time group is

```text
U(t)=Pi_pi+exp[-i t log(3/2)/a]Q.
```

The primary and independent scripts also test nontrivial site- and link-Gram
matrices with exact positive principal minors.

## 5. Static marginal still does not select the transfer

With the same `pi`, every

```text
P_alpha=alpha I+(1-alpha)Pi_pi,  0<alpha<1,
```

is a positive reversible transfer.  For example `alpha=1/2` gives

```text
Delta_a=log 2/a
```

instead of `log(3/2)/a`.  The one-time static distribution and its energy
representative are identical, while the temporal correlations and generator
gap differ.  This directly respects the preceding C0 underdetermination
theorem: the constructive result begins only after `P` is supplied.

## 6. Sharp negative control

Set

```text
alpha_bad=-1/10,
P_bad=alpha_bad I+(1-alpha_bad)Pi_pi.
```

For the declared `pi`, every transition entry remains nonnegative, rows sum to
one, the stationary measure is unchanged, and detailed balance holds.  But

```text
spec(P_bad)={1,-1/10,-1/10}.
```

For the zero-mean vector

```text
f=(1,-3/2,0),
```

the link-reflection form is

```text
<f,P_bad f>_pi=alpha_bad ||f||_pi^2<0.
```

There can be no real nonnegative self-adjoint `H` with
`P_bad=exp(-aH)`, because an exponential of such an `H` has strictly positive
spectrum.  Reversibility, stationarity, and entrywise stochasticity therefore
do not suffice.  Operator nonnegativity is the exact link-reflection-positive
gate, while strict operator positivity is the stronger finite-log gate.

The zero boundary makes the distinction exact.  At `alpha=0`,
`P_0=Pi_pi` is entrywise positive, reversible, irreducible, and link-reflection
positive with spectrum `{1,0,0}`.  It cannot equal `exp(-aH)` for any finite
self-adjoint `H`, whose exponential is strictly positive.

## 7. What is input and what is reconstructed

Inserted:

- the finite state set and one-time probability;
- the entire one-step transfer `P`;
- the ordering of steps, reflection operation, and time spacing `a`;
- the interpretation of the reconstructed Hilbert space as a C0-A benchmark.

Reconstructed:

- the weighted complex Hilbert space `L2(X,pi;C)`;
- the unique positive self-adjoint logarithmic generator `H_a`;
- its one-dimensional constant ground space and gap;
- the real-time unitary group generated by that `H_a`;
- site-reflection positivity and, when `P>=0`, link-reflection positivity.

Not reconstructed:

- the transfer from the static energy;
- a physical clock calibration or arrow of time;
- space, locality, a Lorentzian signature, null structure, or limiting speed;
- a quantum field algebra, vacuum/Hadamard state, or continuum limit;
- gravity, an event horizon, a high-energy cosmological state, cooling, or a
  phase transition;
- a map into PA-H1 or PA-M2;
- a physical TECT choice of C0-A over C0-B or completion of Pre-A.

## 8. Why a quantum walk is not the first benchmark

A local discrete-time quantum walk can have an exact finite dependence cone
and a linear long-wavelength dispersion.  It is useful later.  But a unitary
step has quasienergy branch ambiguity, its logarithm can be nonlocal, and it
does not by itself select a positive ground state or a reflection-positive
Euclidean measure.  The finite positive transfer therefore isolates the
minimal reconstruction theorem more cleanly.

The next bridge within this lane should be a reflection-positive Gaussian finite-Galerkin
family.  It must reconstruct a CCR slice algebra and covariance state, prove a
controlled Klein-Gordon dispersion/continuum limit, and construct a symplectic
intertwiner into the PA-H1 slice space.  Only that result could supply PA-H1
with a selected benchmark state through this route rather than merely
transport a state supplied from elsewhere; other state-selection constructions
remain possible.

## 9. Devil's-advocate review

1. **The result derives time from a static probability.**
   **REJECTED.**  It derives a generator from a separately supplied positive
   transfer and time spacing.  The temporal order is declared C0-A input.
2. **Detailed balance is enough for a positive Hamiltonian.**
   **REJECTED.**  The exact `alpha_bad=-1/10` stochastic reversible transfer
   has a negative eigenvalue and fails link reflection positivity.
3. **Operator positivity automatically makes the transfer Markov.**
   **REJECTED.**  The exact `P_op=I-(1/10)vv^T` control is positive definite,
   row preserving, and reversible but has a negative transition entry.
4. **The logarithm might have branch ambiguity.**
   **DISMISSED IN THIS SCOPE.**  A strictly positive self-adjoint `P` has a
   unique real self-adjoint logarithm.  A generic unitary step would not.
5. **The reconstructed unitary group is already physical quantum mechanics.**
   **UPHELD.**  Mathematical unitarity does not establish a field-observable
   interpretation, Born-rule provenance, locality, or empirical selection.
6. **Reflection positivity gives Lorentzian spacetime automatically.**
   **UPHELD.**  This finite system has no space or cone.  Full
   Osterwalder-Schrader reconstruction requires a much richer Euclidean field
   system and axioms.
7. **The ground space is a cosmological boundary state.**
   **UPHELD.**  It is only the unique constant vector of this irreducible
   finite transfer up to normalization and phase.  No PA-H1 Weyl state or
   Hadamard property follows.
8. **Choosing C0-A here settles the TECT ontology.**
   **REJECTED.**  This is a calibration survivor, while the physical branch
   selection remains open and C0-B has a separate symmetry-breaking gate.

## 10. Reproducible evidence

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0a_reflection_positive_transfer.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0a_reflection_positive_transfer_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0a_reflection_positive_transfer_verify.py
```
