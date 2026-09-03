<a id="section-1-verdict"></a>
# PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0

## 1. Verdict

After explicitly declaring `hbar>0` and the canonical momentum
`p=(a/8)Pi`, the fixed periodic CL8 regulator has a rigorous quantum
Schrodinger realization.  It has compact resolvent, one simple strictly
positive ground wavefunction, and a faithful trace-class Gibbs density for
every `beta>0`.

This closes only
`PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-GROUND-AND-GIBBS-STATE`.  It also proves
the scoped negative

`NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE`:

normalization, stationarity, and the declared exact periodic CL8
node/coarse-translation, Q3, and global-Z2 symmetries do not uniquely select
one fixed-regulator quantum state.  The
ground projector and every finite-temperature Gibbs density satisfy all of
those conditions and are different.

The ground-state criterion does select one unique finite-regulator state when
that criterion is added.  Neither the criterion nor `hbar` is derived here.
Quantum characteristic-boundary composition, regulator removal, an
interacting continuum or Hadamard state, a physical energy reference, CP1,
and Pre-A remain open.

<a id="section-2-prior-art"></a>
## 2. Prior-art and novelty boundary

Closed semibounded quadratic forms, compact resolvents for confining
Schrodinger operators, positivity-improving ground-state uniqueness,
harmonic-oscillator heat traces, and finite-volume Gibbs density operators are
standard.  This certificate is not a new general operator theorem and makes
no world-first claim.

The repository-specific work is the exact compatibility audit:

- the inherited `a/8` CL8 symplectic convention;
- the resulting CCR and kinetic coefficient;
- the Q3 quartic coercive constants;
- the fixed-regulator ground and thermal state fork;
- the additive proof-shift ledger;
- the separation of fixed-regulator state construction from a quantum null-boundary
  map, continuum/Hadamard limit, and physical state selection.

Under the programme sequence fixed in
`pre-a-prior-art-novelty-matrix-260803.md`, this is at most a standard
fixed-regulator bulk-state ingredient after a C0 branch and Hamiltonian have
been supplied.  It is not an N1 boundary algebra/state and closes none of
N2--N5.  The Gaussian C0-A finite-image boundary comparator is not superseded:
that comparator has a free finite-image boundary calibration, whereas this
interacting CL8 state still has no boundary-algebra map.

<a id="section-3-canonical-variables"></a>
## 3. Canonical variables and the exact kinetic coefficient

Fix `L>0`, finite `M>=2`, `a=L/M`, and `d=8M`.  The inherited classical form
is

\[
 \Omega_a=w\sum_{i=1}^d d\Pi_i\wedge dq_i,
 \qquad w={a\over8}.                                          \tag{3.1}
\]

Define

\[
 p_i=w\Pi_i.                                                   \tag{3.2}
\]

Then `Omega_a=sum_i dp_i wedge dq_i`.  Declare `hbar>0` and the standard
Schrodinger CCR representation

\[
 [\widehat q_i,\widehat p_k]=i\hbar\delta_{ik},
 \qquad \widehat p_i=-i\hbar\partial_{q_i}                    \tag{3.3}
\]

on `L2(R^d,dq)`.  Since the classical kinetic energy is

\[
 w\sum_i{\Pi_i^2\over2\chi}
 =\sum_i{p_i^2\over2\chi w},                                  \tag{3.4}
\]

the quantum kinetic coefficient is not optional:

\[
 \kappa_a={\hbar^2\over2\chi w}
 ={4\hbar^2\over a\chi}.                                     \tag{3.5}
\]

Thus

\[
 \widehat H_a=-\kappa_a\Delta_{\mathbb R^d}+U_a(q),           \tag{3.6}
\]

\[
 U_a(q)={a\over8}\sum_j\left{
 {c\over2}|D_a^+q_j|^2+W(q_j)\right\}.                       \tag{3.7}
\]

This package inserts the Schrodinger representation and `hbar`; the classical
CL8 theorem alone did not contain them.

For precision, let `mathcal H_a=L2(R^d,dq)` and take the fixed-regulator
observable algebra to be `mathcal A_a=B(mathcal H_a)`.  Although `d=8M` is
finite, `mathcal H_a` is infinite-dimensional and `Hhat_a` is unbounded.  The
declared canonical pairs generate Weyl unitaries in the regular Schrodinger
representation.  Every density matrix below defines the normal state

\[
 \omega_\rho(A)=\operatorname{Tr}(\rho A),\qquad A\in\mathcal A_a, \tag{3.8}
\]

and restricts to the regular Weyl CCR algebra.  Stationarity means
`omega_rho composed with alpha_t=omega_rho`, where

\[
 \alpha_t(A)=e^{it\widehat H_a/\hbar}A
             e^{-it\widehat H_a/\hbar}.                     \tag{3.9}
\]

It follows whenever `rho` commutes with `Hhat_a`.  No nonlinear quantum
characteristic-boundary homomorphism of Weyl algebras is inferred.

<a id="section-4-coercive-form"></a>
## 4. Coercive form and self-adjoint operator

Let `r_-=max(-r,0)`.  Dropping the nonnegative spatial and Q3 terms gives

\[
 U_a(q)\ge {ag\over32}\sum_{i=1}^d q_i^4
             -{ar_-\over16}|q|^2.                             \tag{4.1}
\]

Since `sum_i q_i^4>=|q|^4/d`,

\[
 U_a(q)\ge A_a|q|^4-B_a|q|^2,
 \quad A_a={ag\over32d},\quad B_a={ar_-\over16}.              \tag{4.2}
\]

For every `mu>0`, completing the square in `s=|q|^2` yields

\[
 U_a(q)\ge \mu|q|^2-C_\mu,
 \qquad C_\mu={(B_a+\mu)^2\over4A_a}.                         \tag{4.3}
\]

On `C_c^infinity(R^d)`, consider

\[
 \mathfrak h_a[f]=\kappa_a\|\nabla f\|_2^2
                   +\int U_a(q)|f(q)|^2dq.                    \tag{4.4}
\]

Shift by `C_mu` and close this form in its form norm.  The resulting closed
lower-bounded form defines a unique Friedrichs self-adjoint operator, which is
the declared `Hhat_a`.  This argument does not need an unrecorded assertion of
essential self-adjointness on a preferred core.

The harmonic lower bound (4.3) controls the `L2` tail outside large balls.
On each bounded ball, the gradient term and Rellich compactness give a compact
embedding.  Combining the tail and local arguments shows that the form domain
embeds compactly into `L2`.  Hence `Hhat_a` has compact resolvent and a purely
discrete spectrum with finite multiplicities accumulating only at infinity.

<a id="section-5-ground-state"></a>
## 5. The finite-regulator ground state

Compact resolvent attains the lowest spectral value.  The scalar uniformly
elliptic Schrodinger heat semigroup on connected `R^d` is positivity
improving.  Therefore its lowest eigenvalue is simple, and the corresponding
normalized real wavefunction `Psi_(0,a)` can be chosen strictly positive.
Polynomial smoothness of `U_a` and elliptic regularity make it smooth.

Periodic CL8 node/coarse translations, Q3 graph automorphisms, and global
`q -> -q` commute with `Hhat_a`.  Fine one-site ST8 translation is not
claimed.  Acting with any declared symmetry on the simple ground with its
strictly positive normalized wavefunction gives the same ground.  The projector

\[
 P_{0,a}=|\Psi_{0,a}\rangle\langle\Psi_{0,a}|                 \tag{5.1}
\]

is therefore stationary and invariant under all declared symmetries.  In
particular it is Z2 even, so every odd order parameter has zero expectation.
The unique fixed-regulator ground does not select any one classical ordered
well.  In particular, when `lambda>0` it selects neither of the two collective
`+v` and `-v` wells; at `lambda=0` the classical sign-minimum set is larger.
It proves no spontaneous symmetry breaking.

The ground-state rule is a valid conditional selector:

> among normalized vector states, choose the eigenspace of the least
> spectral value of the declared Hamiltonian.

Simplicity then selects (5.1).  The rule is an additional selection criterion
whose physical justification is not derived.  It is not a consequence of
stationarity alone and not a derived high-energy Pre-A preparation law.

<a id="section-6-thermal-states"></a>
## 6. The finite-temperature Gibbs family

Compact resolvent by itself is not enough to claim that every heat operator is
trace class.  Use the stronger harmonic comparison from (4.3):

\[
 \widehat H_a\ge H_{\rm osc}-C_\mu,
 \qquad H_{\rm osc}=-\kappa_a\Delta+\mu|q|^2.                 \tag{6.1}
\]

Let

\[
 \omega=\sqrt{\kappa_a\mu}.                                  \tag{6.2}
\]

The one-dimensional oscillator `-kappa_a d^2/dq^2+mu q^2` has eigenvalues
`(2n+1)omega`.  Min-max comparison in `d` dimensions therefore gives, for
every `beta>0`,

\[
 \operatorname{Tr}e^{-\beta\widehat H_a}
 \le e^{\beta C_\mu}
 \left({e^{-\beta\omega}\over1-e^{-2\beta\omega}}\right)^d
 <\infty.                                                      \tag{6.3}
\]

Consequently

\[
 \rho_{a,\beta}=
 {e^{-\beta\widehat H_a}\over
  \operatorname{Tr}e^{-\beta\widehat H_a}}                  \tag{6.4}
\]

is a positive faithful trace-class density operator.  It is normalized,
stationary, and invariant under the same exact symmetries.  At every finite
`beta` it is mixed and has strictly positive weights on every eigenstate.  It
is therefore different from the pure ground projector.  Different positive
temperatures also give different spectral weights.

Because the ground eigenvalue is simple and the finite-regulator spectrum is
discrete, the excited spectral weights vanish relative to the ground weight
as `beta` tends to infinity.  Thus

\[
 \rho_{a,\beta}\longrightarrow P_{0,a}
 \quad\hbox{in trace norm}.                                   \tag{6.5}
\]

More explicitly, let `Delta=E_(1,a)-E_(0,a)>0`, fix `beta_0>0`, and set

\[
 R_\beta=\sum_{n\ge1}e^{-\beta(E_{n,a}-E_{0,a})}.
\]

The heat-trace bound makes `R_(beta_0)` finite, and for `beta>=beta_0`,

\[
 R_\beta\le
 e^{-(\beta-\beta_0)\Delta}R_{\beta_0},\qquad
 \|\rho_{a,\beta}-P_{0,a}\|_1
 ={2R_\beta\over1+R_\beta}\le2R_\beta.                    \tag{6.6}
\]

This is a finite-regulator zero-temperature limit, not a regulator or
thermodynamic limit.

<a id="section-7-selection-no-go"></a>
## 7. Stationarity-only quantum selection no-go

Consider the proposed fixed-regulator selection data:

1. a normal state on `B(L2(R^(8M)))`;
2. stationarity under `Hhat_a`;
3. periodic CL8 node/coarse-translation, Q3, and global-Z2 invariance.

The ground projector (5.1) and every thermal density (6.4) satisfy all three
items.  They are distinct by purity and spectral weights.  Hence those data do
not uniquely select a preferred state.  This proves

`NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE`.

The no-go does not reject an independently justified ground-state criterion,
KMS temperature, fixed energy, reservoir, preparation history,
symmetry-breaking condition, boundary condition, or cosmological state rule.
It shows that at least one discriminating criterion beyond stationarity and
the exact symmetries is necessary.

The density matrices also restrict to states on the represented regular Weyl
CCR algebra.  This certificate does not claim that the interacting Heisenberg
dynamics preserves that Weyl C-star algebra; the stationarity no-go is stated
on `B(L2(R^(8M)))`, where the unitary dynamics is an automorphism.

<a id="section-8-energy-shift"></a>
## 8. Additive proof shift and the energy reference

The global Goursat proof used `W_hat=W+C_star`, where

\[
 C_\star={2r_-^2\over g}.                                     \tag{8.1}
\]

At fixed circumference this changes the operator by only

\[
 \widehat H_a\mapsto\widehat H_a+{LC_\star\over8}I.           \tag{8.2}
\]

Every eigenvalue and free energy shifts by the same scalar.  The unnormalized
heat operator is multiplied by a scalar exponential that cancels in (6.4).
The normalized Gibbs densities, ground wavefunction, and ground projector are
unchanged.

This invariance shows that the proof shift cannot define an absolute vacuum
energy.  Relative energy differences are unchanged by the shift, so their
absence has a different cause: no normalized state representing physical
empty space or the no-condensate reference has been identified in the same
regulator, Hamiltonian, normalization, and counterterm convention.  Therefore
no below-empty-space comparison is available.  A positive ground wavefunction
also says nothing about the sign of its energy.

<a id="section-9-boundary-fork"></a>
## 9. Why quantum boundary composition remains open

The current Goursat construction is a nonlinear map between classical trace
and Cauchy data.  Its symplectic theorem concerns the variational linearized
flux about a classical solution.  Neither object is a `star`-homomorphism of
quantum observable algebras or a unitary quantum intertwiner.  The
fixed-regulator ground state therefore cannot simply be "pulled back" to a characteristic
boundary by the existing theorem.

Likewise, `|Psi_(0,a)(q)|^2dq` is only the configuration marginal of a quantum
vector state.  It is not a positive invariant measure on the full classical
phase space and cannot replace the classical boundary measure in the previous
composition theorem.

As `M` changes, the Hilbert spaces and CCR algebras change.  No compatible
embeddings, counterterms, state convergence, algebraic limit, or interacting
continuum construction has been proved.  The present radial coefficient is

\[
 {ag\over32d}={Lg\over256M^2},                                \tag{9.1}
\]

so this particular heat-trace comparison is visibly not cutoff uniform.  A
finite lattice also has no continuum wavefront-set singularity on which to
test the Hadamard condition.

The remaining route is therefore:

- `PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER`;
- `PA-CP1-CL8-CONTINUUM-STATE-AND-HADAMARD-LIMIT`;
- `PA-CP1-CL8-CLASSICAL-AND-QUANTUM-PREFERENCE-CRITERION`;
- `PA-CP1-COMMON-PARENT-PHYSICAL-STATE-AND-REFERENCE`.

<a id="section-10-adversarial"></a>
## 10. Devil's-advocate review

1. **Objection: compact resolvent was silently promoted to heat trace class.**
   **DISMISSED.**  The explicit harmonic comparison (6.3), not compactness
   alone, proves the trace bound.
2. **Objection: the negative mass makes the quantum form unstable.**
   **DISMISSED.**  The quartic radial lower bound (4.2) dominates the negative
   quadratic term.
3. **Objection: the `a/8` factor was dropped during quantization.**
   **DISMISSED.**  Equations (3.2)--(3.5) retain it and force
   `kappa_a=4hbar^2/(a chi)`.
4. **Objection: a positive ground wavefunction means positive vacuum energy.**
   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Positivity is pointwise
   wavefunction positivity; additive constants freely move the eigenvalue.
5. **Objection: uniqueness proves a pure ordered phase.**
   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Finite-volume uniqueness makes
   the ground Z2 even and prevents selection of one classical well.
6. **Objection: stationarity selects the ground.**
   **DISMISSED.**  Every finite-beta Gibbs density is also stationary and
   symmetric.
7. **Objection: the position density is the missing classical invariant
   measure.**  **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  It lacks momentum and
   is not generally invariant under the classical Hamiltonian flow.
8. **Objection: a finite ground state is automatically a Hadamard state.**
   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  No continuum algebra, state limit,
   or microlocal spectrum theorem exists here.
9. **Objection: the finite heat-trace constants prove a cutoff-uniform state.**
   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Equation (9.1) explicitly
   deteriorates with `M`.
10. **Objection: finite regulator means finite-dimensional Hilbert space.**
    **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Only the configuration dimension
    is finite; `L2(R^d)` is infinite-dimensional and the Hamiltonian is
    unbounded.
11. **Objection: the state fork already supplies the N1 boundary state.**
    **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  The states live on a bulk
    fixed-regulator algebra and no quantum characteristic-boundary algebra map
    is constructed.
12. **Objection: the model retains the original fine one-site translation.**
    **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  Only periodic CL8
    node/coarse-translation symmetry is used; the Q3 parent explicitly rejects
    the fine one-site symmetry.

<a id="section-11-reproduction"></a>
## 11. Reproduction

Run

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_finite_quantum_state_boundary_fork.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_finite_quantum_state_boundary_fork_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_finite_quantum_state_boundary_fork_verify.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_finite_quantum_state_boundary_fork_verify.py --check-stored
```

The primary implementation symbolically derives the CCR coefficient,
coercive completion, oscillator spectrum, heat-trace product, additive shift,
and fixed-regulator spectral controls.  The independent implementation uses
rational arithmetic and an exact non-diagonal rationally conjugated spectral
fixture without importing the primary module or SymPy.  The integrated verifier compares both routes, pins
the parent authorities, checks the formal negative and all scope boundaries,
and verifies stored-result freshness.

<a id="section-12-no-overclaim"></a>
## 12. No-overclaim boundary

This package constructs finite-regulator CL8 ground and thermal Gibbs states
after declaring `hbar`, the CCR representation, and a state criterion.  It
refutes only unique quantum preference from stationarity and the listed exact
symmetries alone.  It does not select a pure ordered phase, convert a position
marginal into a classical phase measure, construct a quantum characteristic
boundary map, remove the regulator, build an interacting continuum or
Hadamard state, identify physical empty space, establish an absolute or
below-empty-space energy sign, reach a thermodynamic limit, derive full 3+1
dynamics, gravity or cooling, derive `hbar`, close C0 or any N1--N5 link,
advance C6, complete CP1, or complete Pre-A.
