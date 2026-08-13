# R-167 v3.2 certificate: common-generator zero-temperature KMS transfer and the fixed odd separator boundary

## 1. Verdict and exact scope

This proof-first package closes one abstract conditional T0 theorem and one
exact automatic-implication failure.

`EXP-000836 / R-167 v3.2` closes the scoped child
`PA-CP1-ST8-Q3LOCK-COMMON-TARGET-GENERATOR-ZERO-TEMPERATURE-KMS-AND-FIXED-ODD-WITNESS-DISTINCT-GROUND-STATE-TRANSFER`.

The positive theorem starts with two phase-labelled sequences of KMS states
already identified on one unital C-star algebra. If their inverse
temperatures tend to infinity, their generators converge in norm on one
graph core to one target generator, and the states converge weak-star, then
both limit states are algebraic ground states of the same target dynamics.
If one fixed bounded odd observable retains a uniform sign, the two ground
states are distinct and parity related.

The negative fixture shows why the last condition is load-bearing. Pure,
extremal, factorial, parity-related KMS state pairs can have state-norm
distance two at every finite step and nevertheless converge to the same
ground state when their separating observable changes with the step.

This package does **not** prove that the exact Q3 KMS phases satisfy the
common-algebra, common-generator or fixed-witness premises. It therefore does
not close the common-alpha, full-oscillator two-phase, broken-sector GNS,
Round-1, physical Sector A or Pre-A parents.

## 2. Source convention and the differential KMS inequality

Let `A` be a unital C-star algebra. A point-norm C0 group is written

\[
 \alpha_t=\exp(t\delta).
\]

For a Hamiltonian implementation in physical time,

\[
 \alpha_t(A)=e^{itH/\hbar}Ae^{-itH/\hbar},
 \qquad \delta(A)={i\over\hbar}[H,A].                 \tag{2.1}
\]

If `omega` is a physical inverse-temperature `beta` KMS state, the complex
time strip has width `beta hbar`. Araki's differential KMS condition therefore
reads

\[
 -i\,\beta\hbar\,\omega(A^*\delta(A))
 \geq s\bigl(\omega(A^*A),\omega(AA^*)\bigr),
 \qquad A\in\operatorname{Dom}(\delta),              \tag{2.2}
\]

where

\[
 s(x,y)=
 \begin{cases}
 x\log(x/y),&x>0,\ y>0,\\
 0,&x=0,\ y\geq0,\\
 +\infty,&x>0,\ y=0.
 \end{cases}                                         \tag{2.3}
\]

The dimensionless mathematical convention absorbs `hbar` into the KMS strip
parameter and is identical to (2.2) after that rescaling.

The primary authority is H. Araki, *On KMS states of a C*-dynamical system*,
Lecture Notes in Mathematics 650, 66--84 (1978),
DOI [10.1007/BFb0067390](https://doi.org/10.1007/BFb0067390). A modern open
statement with the same extended boundary convention is Theorem 4.4 of
J. Derezinski, V. Jaksic and C.-A. Pillet, *Miniatures on Open Quantum
Systems* (2026), DOI
[10.1007/s11785-026-01967-9](https://doi.org/10.1007/s11785-026-01967-9).
These sources supply an abstract operator-algebra theorem, not an exact-Q3
common-dynamics construction.

## 3. A rational safe lower bound

Put `u=x/y` when `x,y>0`. The elementary logarithm inequality

\[
 \log u\geq 1-u^{-1}                                \tag{3.1}
\]

gives

\[
 s(x,y)=yu\log u\geq y(u-1)=x-y\geq-y.             \tag{3.2}
\]

The same last inequality holds at all extended boundary cases in (2.3):
`s(0,y)=0`, `s(x,0)=+infinity` for `x>0`, and `s(0,0)=0`.
There is no hidden singular case for a KMS state. If
`x=omega(A*A)=0`, Cauchy--Schwarz gives
`omega(A*delta(A))=0`; if also `y>0`, applying (2.2) to `A*` would put a
positive first argument over a zero second argument and is impossible. The
case `y=0<x` is ruled out directly by the infinite right side. Thus an actual
KMS-domain element can reach the zero boundary only with `x=y=0`.
Since `y=omega(AA*)<=||A||^2`, (2.2) implies the completely explicit bound

\[
 -i\hbar\,\omega(A^*\delta(A))
 \geq-{\|A\|^2\over\beta}.                          \tag{3.3}
\]

The sharper constant `1/e` is unnecessary. The rational coefficient one in
(3.3) avoids importing a numerical approximation into the executable
contract.

## 4. The conditional common-generator transfer theorem

Let `beta_n -> infinity`. For each sign `sigma in {+,-}`, suppose:

1. `alpha_n^sigma` is a point-norm C0 automorphism group on the same
   identified unital C-star algebra `A`, with closed generator
   `delta_n^sigma`;
2. `omega_n^sigma` is a `beta_n`-KMS state for `alpha_n^sigma`;
3. `alpha` is one target point-norm C0 group on `A`, with closed generator
   `delta`;
4. `D` is a common unital star-subalgebra, is contained in every generator
   domain, and is a graph core for `delta`;
5. for every `A in D`,

\[
 \|\delta_n^\sigma(A)-\delta(A)\|\longrightarrow0,
 \qquad
 \omega_n^\sigma\overset{w^*}{\longrightarrow}\omega_\sigma.
                                                               \tag{4.1}
\]

KMS invariance gives `omega_n^sigma(delta_n^sigma(A))=0`. Therefore

\[
\begin{aligned}
 |\omega_n^\sigma(\delta_n^\sigma(A))-\omega_\sigma(\delta(A))|
 &\leq\|\delta_n^\sigma(A)-\delta(A)\|\\
 &\quad+| (\omega_n^\sigma-\omega_\sigma)(\delta(A))|
 \longrightarrow0.                                  \tag{4.2}
\end{aligned}
\]

Thus `omega_sigma(delta(A))=0` on `D`. Graph-core approximation extends this
identity to `Dom(delta)`, hence each limit state is `alpha` invariant.

For the energy form, fixed `A in D` gives

\[
\begin{aligned}
 &|\omega_n^\sigma(A^*\delta_n^\sigma(A))
      -\omega_\sigma(A^*\delta(A))|\\
 &\qquad\leq
 \|A\|\,\|\delta_n^\sigma(A)-\delta(A)\|
 +| (\omega_n^\sigma-\omega_\sigma)(A^*\delta(A))|
 \longrightarrow0.                                  \tag{4.3}
\end{aligned}
\]

Taking the lower limit in (3.3) yields

\[
 -i\hbar\,\omega_\sigma(A^*\delta(A))\geq0,
 \qquad A\in D.                                     \tag{4.4}
\]

If `A_k -> A` and `delta(A_k)->delta(A)` in the graph norm, then the left
side of (4.4) converges because

\[
 \|A_k^*\delta(A_k)-A^*\delta(A)\|
 \leq\|A_k-A\|\,\|\delta(A_k)\|
      +\|A\|\,\|\delta(A_k)-\delta(A)\|.             \tag{4.5}
\]

Hence (4.4) holds on `Dom(delta)`. This is the
standard algebraic ground-state condition. Both `omega_+` and `omega_-` are
ground states of the **same** target dynamics `alpha`.

Generator convergence on the graph core is stronger than merely knowing a
separate dynamics for every `n`, but it does not by itself assert
`alpha_n^sigma -> alpha` uniformly on compact time intervals. No such group
convergence is used or claimed.

## 5. Parity and the fixed odd separator

Let `Theta` be an involutive linear star-automorphism of `A`, with
`Theta(D)=D`. Assume the state identity on all of `A` and the generator
identity on `D`:

\[
 \omega_n^- =\omega_n^+\circ\Theta,
 \qquad
 \delta_n^-\circ\Theta=\Theta\circ\delta_n^+.       \tag{5.1}
\]

Weak-star convergence gives `omega_-=omega_+ o Theta`. Passing to the norm
generator limit gives

\[
 \delta\circ\Theta=\Theta\circ\delta              \tag{5.2}
\]

on `D`. Graph closure first extends (5.2) to `Dom(delta)`. Closed-generator
uniqueness then gives `alpha_t o Theta=Theta o alpha_t`: both sides solve the
same C0 generator equation.

Now assume there is one fixed selfadjoint contraction `B` such that

\[
 \Theta(B)=-B,
 \qquad
 \liminf_n\omega_n^+(B)\geq m_0>0.                  \tag{5.3}
\]

Because the state sequence converges,

\[
 \omega_+(B)\geq m_0,
 \qquad
 \omega_-(B)=-\omega_+(B)\leq-m_0.                 \tag{5.4}
\]

Consequently

\[
 \|\omega_+-\omega_-\|
 \geq |(\omega_+-\omega_-)(B)|
 \geq2m_0.                                          \tag{5.5}
\]

The normalization `||B||<=1` is load-bearing for the last numerical bound.
Without that normalization, the correct lower bound is `2m_0/||B||`.

## 6. What this reduces for exact Q3

The `EXP-000790` source-cusp authority supplies parity-related zero-source
time-zero tangent candidates and a nonzero unbounded coordinate expectation.
Its uniform local fourth-moment control can produce a **candidate** fixed
bounded odd witness. For example, with

\[
 B_R(q)=\operatorname{clip}(q/R,-1,1),               \tag{6.1}
\]

one has `||B_R||<=1`, `B_R` odd, and

\[
 \left|\omega(q/R)-\omega(B_R)\right|
 \leq {\omega(|q|^4)\over R^4}.                     \tag{6.2}
\]

Thus a fixed `R` preserves a positive sign whenever the coordinate lower
bound and fourth-moment ceiling are uniform in the same approximating family.

That observation does not apply the theorem yet. This package does not
identify the source-tangent candidates as weak-star limits of two
`beta_n`-KMS families on one Hamiltonian-derived common C-star algebra, and
does not prove the common-core generator convergence (4.1). Moreover, the
`EXP-000782` thermal infrared separator decays as beta tends to infinity and
cannot itself provide the fixed `m_0` in (5.3).

The exact remaining model inputs are therefore:

- one noncollapsing spatial carrier and one target point-norm C0 action;
- two phase-labelled KMS sequences on that same identified carrier;
- norm convergence of both phase generators to the target generator on one
  graph core;
- a fixed bounded odd witness whose sign does not collapse.

Even if all four are proved, the present theorem gives distinct algebraic
ground states, not a GNS spectral gap. The phasewise Poincare inequality,
positive target implementation, energy identity, and centered linear form
core isolated in R-167 v3.0 remain separate load-bearing hypotheses.

## 7. Exact collapse fixture

Let

\[
 A=C([-1,1]),\qquad \alpha_n^\pm=\alpha=\operatorname{id},
 \qquad \delta_n^\pm=\delta=0,qquad \beta_n=n.      \tag{7.1}
\]

Define `Theta(f)(q)=f(-q)` and

\[
 \omega_n^+=\operatorname{ev}_{1/n},
 \qquad
 \omega_n^-=\operatorname{ev}_{-1/n}.               \tag{7.2}
\]

Because `A` is commutative and the dynamics is trivial, every state is KMS
at every positive inverse temperature. Each evaluation state is pure,
extremal and factorial. The pair is parity related.

For every `n`, the continuous contraction

\[
 f_n(q)=\max\{-1,\min\{1,nq\}\}                     \tag{7.3}
\]

satisfies `f_n(1/n)=1` and `f_n(-1/n)=-1`. Hence

\[
 \|\omega_n^+-\omega_n^-\|=2.                      \tag{7.4}
\]

Nevertheless both state sequences converge weak-star to `ev_0`. The fixed
odd contraction `B(q)=q` has

\[
 \omega_n^+(B)-\omega_n^-(B)={2\over n}\longrightarrow0. \tag{7.5}
\]

The norm-separating observable (7.3) depends on `n`; there is no fixed
noncollapsing witness. More generally, every one fixed `f in C([-1,1])`
satisfies `f(+/-1/n)->f(0)` by continuity, so no fixed observable separates
the two weak-star limits. This disproves only the inference from finite-step
distinctness, purity or extremality to distinct zero-temperature limits. It
does not treat the finite pairs as thermodynamic phases and does not deny
that a genuinely uniform order witness would keep phase limits distinct.

This exact fixture registers
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-FINITE-NORM-SEPARATED-PARITY-KMS-PAIRS-AUTOMATIC-DISTINCT-GROUND-LIMITS`.

## 8. Executable exact fixtures

### 8.1 Two-level differential-KMS equality

Take `H=diag(0,g)` and choose `beta g=log 2`. The Gibbs weights are
`p_0=2/3`, `p_1=1/3`. For `A_up=|1><0|`,

\[
 -i\beta\hbar\,\omega(A_\mathrm{up}^*\delta(A_\mathrm{up}))
 ={2\log2\over3}
 =s(2/3,1/3).                                       \tag{8.1}
\]

For `A_down=|0><1|`,

\[
 -i\beta\hbar\,\omega(A_\mathrm{down}^*\delta(A_\mathrm{down}))
 =-{\log2\over3}
 =s(1/3,2/3)\geq-2/3.                               \tag{8.2}
\]

This checks the sign, the `hbar` scaling, and a case in which the differential
KMS energy form is negative at finite temperature but its lower bound is
`O(beta^-1)` after division by `beta`.

### 8.2 Fixed separator

On the two-point algebra take `B=(-1,1)`. Let the plus probability weights be
`(1/8,7/8)` and the minus weights their parity swap. Then `||B||=1`,
`omega_+(B)=3/4`, `omega_-(B)=-3/4`, and the state-distance lower bound from
the fixed witness is `3/2`.

### 8.3 Boundary and collapse checks

The executable engines check all three boundary values in (2.3), the sample
indices `n=2,3,5,8`, the exact points `+/-1/n`, the fixed-witness gaps `2/n`,
the step-dependent norm separator (7.3), and their common pointwise limit
zero.

The fixtures are proof oracles, not finite-Q3 simulations.

## 9. Literature and route firewall

The differential inequality is general C-star KMS theory. It cannot supply
any of the model-specific identifications assumed in Section 4.

The fixed-beta Euclidean DLR and OS authorities in this repository construct
or compactify thermal phases at a chosen beta. They do not identify a single
beta-independent exact-Q3 spatial action along beta tending to infinity.
R-167 v1.6 constructs a categorical orbit-smear ground carrier, but that
carrier is not the missing Hamiltonian-derived spatial common alpha. R-167
v3.0 proves an abstract finite-Poincare/common-generator-to-GNS-gap transfer,
but not the Q3 generator convergence or form-core premise. These results are
compatible and remain separate.

## 10. Devil's-advocate audit

1. **Does KMS convergence alone imply a ground state for a changing
   dynamics? UPHELD.** It does not. Norm generator convergence on one graph
   core is an explicit premise.
2. **Can the differential KMS energy form be negative? DISMISSED only after
   beta tends to infinity.** Equation (8.2) is negative. The universal
   `-||A||^2/beta` lower bound is what makes its limit nonnegative.
3. **Are zero values of `x` or `y` silently excluded? DISMISSED.** The
   extended definition (2.3) and all three boundary cases are explicit.
4. **Does graph-core positivity automatically give a GNS gap? UPHELD.** It
   gives only the ground-state condition. R-167 v3.0 lists the additional gap
   premises.
5. **Do pure distinct KMS pairs have distinct limits? UPHELD as false.** The
   exact fixture (7.1)--(7.5) has distance two at every finite step and one
   common limit.
6. **Does a varying separator suffice? UPHELD as false.** The theorem requires
   one fixed bounded odd witness.
7. **Is the state-distance bound missing a norm factor? DISMISSED.** The
   theorem declares `||B||<=1`; the unnormalized alternative is stated.
8. **Does parity of states imply parity of the target dynamics? UPHELD without
   generator intertwining.** Equation (5.1) includes generator intertwining,
   and the common limit proves (5.2).
9. **Does this prove beta-infinity KMS? UPHELD as an overclaim.** The limit is
   an algebraic ground state; no KMS label at infinite beta is asserted.
10. **Does this close the exact-Q3 phase programme? UPHELD as false.** The
    common spatial carrier, phase KMS identification, generator convergence
    and uniform witness are still open.

## 11. Reproduction and lifecycle

Run from the repository root:

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_common_generator_zero_temperature_kms_ground_separator_route_split.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_common_generator_zero_temperature_kms_ground_separator_route_split_independent.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_common_generator_zero_temperature_kms_ground_separator_route_split_verify.py --staged --no-store
```

The first engine uses SymPy exact arithmetic. The independent engine uses only
the Python standard library and does not import the first engine. The
integrated verifier checks both payloads, their source hashes, exact authority
topology, lifecycle, formal linkage and independent-import firewall.

No v3.2 PDF is issued. All five active parent gates remain OPEN. This package
proves no beta-infinity KMS label, purity, extremality, factoriality,
disjointness, clustering, simple ground kernel, broken-sector GNS gap, mass
gap, full-oscillator two-phase QPS theorem, selector removal, common spatial
alpha, regulator removal, continuum, physical vacuum or empty-space
comparison, Round-1, C6, CP1, physical Sector A, or Pre-A.
