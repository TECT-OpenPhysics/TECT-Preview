# Pre-A ST8 nonlinear Q3-locking certificate

**Candidate:** `PA-CP1-ST8-Q3LOCK-v0`  
**Parent:** `PA-CP1-ST8-CB-v0`  
**Task:** `T-054`  
**Context only:** `C6-SPACETIME-SIGNATURE`,
`A2-FULL-PRODUCTION-WELLPOSED`  
**Authority:** T0 exact finite candidate certificate; no claim or tier change  
**Date:** 2026-08-03

## 1. Verdict

The exact ST8 audit showed that the undeformed LT3 Hamiltonian is eight
decoupled coarse real scalar species.  This certificate tests a minimal-degree
analytic candidate that can lock those species without changing their
zero-background Hessian.

The positive quartic Q3-edge term

\[
 \Delta H_\lambda=
 \frac{\lambda}{4}\sum_y\sum_{\{\epsilon,\eta\}\in E(Q_3)}
 (\psi_\epsilon-\psi_\eta)^2
 (\psi_\epsilon^2+\psi_\eta^2),
 \qquad \lambda>0,
\]

has the following exact finite-regulator properties.

1. It is nonnegative, local within a fixed `2 x 2 x 2` block, globally
   `Z2` invariant, and invariant under the automorphisms of the species cube.
2. Its Hessian at the zero field is exactly zero, so all eight ST8 critical
   species modes remain.
3. For `r<0`, the full deformed Hamiltonian has exactly two classical global
   minima, preserves the same-Hamiltonian value
   `H_min=-N^3*r^2/(4g)<H(0,0)=0`, and lifts every other old sign minimum by an
   exactly counted Q3 cut energy.
4. At either ordered minimum, its species Hessian is
   `lambda*v^2*L_Q3`.  The unique collective singlet is the lowest species
   branch, while the other seven directions acquire positive gaps.
5. The collective singlet is an exact invariant classical nonlinear
   reduction, not an arbitrary choice of one of eight species.

This is a new candidate deformation.  It is not derived from LT3, depends on a
fixed block origin, and does not restore an exact finite-regulator causal cone.
The finite quantum ground remains unique and symmetric.  Physical empty space,
a pure ordered quantum phase, characteristic reconstruction from the same
state, CP1, and Pre-A therefore remain open.

## 2. Prior-art boundary

Multicomponent `phi4` models, graph-Laplacian normal modes, quartic Landau
anisotropies, finite anharmonic Schrodinger operators, and invariant singlet
reductions are standard mathematics.  The finite-ground input uses the same
standard Friedrichs, compact-resolvent, and positivity-improving results
already declared by the LT3 certificate.

No new general theorem or world-first statement is made.  The local result is
the convention-level audit of this particular Q3 polynomial against the
registered ST8, PA-H1, common-reference, and CP1 contracts.

<a id="section-3-candidate-definition"></a>
## 3. Candidate definition

Let `N=4m`, `M=N/2`,

\[
 \Lambda_M=(\mathbb Z/M\mathbb Z)^3,
 \qquad \epsilon\in\{0,1\}^3,
\]

and let `E(Q3)` be the twelve undirected edges joining bit strings that differ
in one coordinate.  Starting from the exact ST8 variables, define

\[
\begin{aligned}
H_\lambda={}&
\sum_{y,\epsilon}
\left[
 \frac{\rho_\epsilon(y)^2}{2\chi}
 +\frac r2\psi_\epsilon(y)^2
 +\frac g4\psi_\epsilon(y)^4
\right] \\
&+\frac c2\sum_{y,\epsilon,i}
 \left(\psi_\epsilon(y+e_i)-\psi_\epsilon(y)\right)^2
 +\Delta H_\lambda .
\end{aligned}
\]

The admitted parameter domain is

\[
 \chi>0,\qquad c>0,\qquad g>0,\qquad \lambda>0,
\]

with arbitrary real `r`; the ordered theorem assumes `r<0`.

The polynomial identity

\[
(a-b)^2(a^2+b^2)
=a^4-2a^3b+2a^2b^2-2ab^3+b^4
\]

shows global `Z2` invariance and genuine cross-species interaction.  Its
factorized form shows nonnegativity.  For real `a,b` and positive `lambda`, an
edge term vanishes exactly when `a=b`.

<a id="section-4-complete-square-locking-theorem"></a>
## 4. Complete-square locking theorem

### Theorem Q3LOCK-F

For the finite candidate above and `r<0`, set

\[
 v^2=-\frac r g,
 \qquad V=N^3=8M^3.
\]

Then

\[
\begin{aligned}
H_\lambda+\frac{Vr^2}{4g}
={}&\sum_{y,\epsilon}\frac{\rho_\epsilon(y)^2}{2\chi}
+\frac c2\sum_{y,\epsilon,i}
 \left(\psi_\epsilon(y+e_i)-\psi_\epsilon(y)\right)^2 \\
&+\frac g4\sum_{y,\epsilon}
 \left(\psi_\epsilon(y)^2-v^2\right)^2
+\Delta H_\lambda
\ge 0.
\end{aligned}
\]

All summands are nonnegative.  Because `c>0` and the periodic coarse spatial
graph is connected, equality requires

\[
 \rho=0,
 \qquad \psi_\epsilon(y)=s_\epsilon v,
 \qquad s_\epsilon\in\{-1,+1\},
\]

with every species spatially constant.  Every Q3 edge must also have equal
endpoints.  Since Q3 is connected, all `s_epsilon` are equal.  Hence the only
global minima are

\[
 \psi_\epsilon(y)=+v\quad\hbox{for every }(y,\epsilon),
 \qquad
 \psi_\epsilon(y)=-v\quad\hbox{for every }(y,\epsilon),
\]

and

\[
 H_{\min}=-\frac{N^3r^2}{4g}<H_\lambda(0,0)=0.
\]

This is an exact same-Hamiltonian comparison to the zero configuration.  The
zero configuration is not a normalized state and has not been identified with
physical empty space or a no-condensate reference.

## 5. Exact lifting of the old sign manifold

For one of the 256 old ST8 sign configurations, let `partial_Q3 s` be the set
of cube edges on which the signs disagree.  Each disagreeing edge contributes

\[
 \frac\lambda4(2v)^2(2v^2)=2\lambda v^4
\]

per coarse site.  Therefore

\[
 \Delta E(s)=2\lambda M^3v^4\,|\partial_{Q_3}s|.
\]

The minimum nonzero cube cut has size three, so the exact gap within the old
minimum manifold is `6*lambda*M^3*v^4`.  Exhaustive independent enumeration
gives the cut histogram

\[
\{0:2,\ 3:16,\ 4:30,\ 5:48,\ 6:64,\ 7:48,\
  8:30,\ 9:16,\ 12:2\}.
\]

At `lambda=0`, all 256 old minima return exactly.

<a id="section-6-origin-and-ordered-hessians"></a>
## 6. Origin and ordered Hessians

Because every monomial in `Delta H_lambda` has total degree four,

\[
 D^2\Delta H_\lambda(0)=0.
\]

Thus the full zero-background harmonic symbol is exactly the ST8 symbol times
the eight-dimensional species identity.  At `r=0`, it retains eight
constant-species zero modes.

At a common ordered minimum, write

\[
 \psi_\epsilon=v+u_\epsilon.
\]

For one species edge,

\[
\frac\lambda4
(u_\epsilon-u_\eta)^2
\left[(v+u_\epsilon)^2+(v+u_\eta)^2\right]
=\frac{\lambda v^2}{2}(u_\epsilon-u_\eta)^2+O(u^3).
\]

Hence the ordered species Hessian is

\[
 K_{\rm species}=(-2r)I+\lambda v^2L_{Q_3}.
\]

For the cube characters

\[
 \chi_\alpha(\epsilon)=(-1)^{\alpha\cdot\epsilon},
 \qquad \alpha\in\{0,1\}^3,
\]

one has

\[
 L_{Q_3}\chi_\alpha=2|\alpha|\chi_\alpha,
\]

and therefore

\[
 \operatorname{spec}L_{Q_3}
 =\{0,2^{(3)},4^{(3)},6\}.
\]

The full ordered tangent dispersion is

\[
 \omega_\alpha(q)^2=
 \frac{-2r+4c\sum_i\sin^2(q_i/2)
       +2\lambda v^2|\alpha|}{\chi}.
\]

At each fixed spatial momentum, the `alpha=0` singlet is the unique lowest
species branch.  The first Q3
transverse level is a triplet; it must not be confused with the two real
spatial PA-H1 modes of equal frequency.

<a id="section-7-minimality-and-quadratic-fork"></a>
## 7. Minimality and the quadratic fork

The minimality statement is deliberately narrow.  Consider a nonzero real
polynomial, or a real-analytic Taylor interaction, which

1. is invariant under simultaneous `(a,b)->(-a,-b)`;
2. has its own Hessian zero at the origin; and
3. genuinely couples the two species.

Global `Z2` removes odd Taylor degrees.  Hessian preservation removes degree
two.  The first available nonconstant degree is therefore four, and the
candidate attains this bound.

This is not uniqueness or canonical selection.  It is not a minimality theorem
for arbitrary `C2` or nonanalytic functions; for example, absolute-value
homogeneous terms require a separate regularity class.

Two hostile quartic controls separate the load-bearing properties.

- `(a-b)^4` locks opposite signs but begins at fourth order even around
  `a=b=v`, so it does not split the ordered tangent.
- `(a^2-b^2)^2` gives an ordered quadratic splitting but vanishes for both
  `a=b` and `a=-b`, so it leaves all old sign minima.

The chosen product does both.

Now consider the standard positive quadratic repair

\[
 \Delta H_\eta=
 \frac\eta2\sum_{y,\epsilon\sim\eta'}
 (\psi_\epsilon-\psi_{\eta'})^2,
 \qquad \eta>0.
\]

Its origin Hessian adds `eta*L_Q3`.  A connected positive graph Laplacian has
only the constant vector in its kernel.  For Q3 the critical species nullity
therefore falls from eight to one, with spectrum

\[
 0,\quad 2\eta^{(3)},\quad 4\eta^{(3)},\quad 6\eta.
\]

This proves the scoped no-go
`NG-2026-08-03-PRE-A-CP1-Q3LOCK-QUADRATIC-CONNECTIVITY-CI8`: standard positive
quadratic species connectivity cannot preserve all eight constant-species
critical zero modes.  It does not exclude quartic or higher coupling, signed
or frustrated quadratic forms, constraints, gauge quotients, or zero modes of
a different origin.

## 8. Locality and the block-origin cost

The signed ST8 variables obey

\[
 \phi_{2y+\epsilon}=(-1)^{|y|}\psi_\epsilon(y).
\]

If `epsilon` and `eta` differ in one bit, their fine sites are one spatial step
apart inside the same block.  The common sign cancels from the degree-four
edge term, so the new interaction is finite-range in fine variables.

It nevertheless uses a fixed partition into `2 x 2 x 2` blocks.  A one-fine-
site translation moves some coupled pairs across block boundaries.  The
primary verifier constructs an explicit `N=4` collective ordered field whose
locking energy is zero before translation and strictly positive after one
fine-site translation while the block origin is held fixed.

Thus the candidate preserves coarse translations and Q3 automorphisms, not the
full one-site translation group of the parent.  A physical use must derive,
sum over, gauge, or dynamically select the block origin; this certificate does
none of those things.

<a id="section-9-collective-and-volume-ledgers"></a>
## 9. Collective and physical-volume ledgers

### 9.1 Finite unweighted canonical coordinates

At each coarse site define the normalized diagonal embedding

\[
 \psi_\epsilon=\frac{Q}{\sqrt8},
 \qquad
 \rho_\epsilon=\frac{P}{\sqrt8}.
\]

Then

\[
 \sum_\epsilon d\rho_\epsilon\wedge d\psi_\epsilon
 =dP\wedge dQ.
\]

All Q3-lock forces vanish on the diagonal and the identical base forces agree,
so this is an exact invariant classical nonlinear submanifold.  Its finite
unweighted Hamiltonian is a single lattice `phi4` model with

\[
 g_{\rm eff}=\frac g8.
\]

### 9.2 Physical continuum-density convention

The finite canonical normalization above is not the continuum volume ledger.
Let the coarse spacing be `a` and the inherited fine spacing be `h=a/2`.
Every coarse species sample represents fine volume

\[
 h^3=\frac{a^3}{8}.
\]

This is a newly declared spacing-dependent physical family, not an automatic
substitution into the spacing-one ST8 Hamiltonian.  Relate its canonical
momentum to the momentum density by

\[
 \rho_\epsilon(y)=\frac{a^3}{8}\Pi_\epsilon(y)
 =h^3\Pi_\epsilon(y).
\]

Consequently its kinetic term is

\[
 \frac{\rho_\epsilon(y)^2}{2\chi h^3}
 =h^3\frac{\Pi_\epsilon(y)^2}{2\chi},
\]

not the result of inserting `rho=h^3*Pi` into the unweighted spacing-one
kinetic term.  With this declared convention, the physical semidiscrete forms
are

\[
 \Omega_a=\frac{a^3}{8}
 \sum_{y,\epsilon}\delta\Pi_\epsilon(y)\wedge
 \delta\psi_\epsilon(y),
\]

and

\[
 H_a=\frac{a^3}{8}\sum_{y,\epsilon}
 \left[
 \frac{\Pi_\epsilon^2}{2\chi}
 +\frac{c_{\rm phys}}{2a^2}\sum_i(\Delta_i\psi_\epsilon)^2
 +\frac r2\psi_\epsilon^2+\frac g4\psi_\epsilon^4
 \right]
 +\frac{a^3}{8}\Delta\mathcal V_\lambda.
\]

Formally, the continuum ledger is `(1/8)` times the sum of eight species
integrals.  On the physical diagonal

\[
 \psi_\epsilon=\psi,\qquad \Pi_\epsilon=\Pi,
\]

the factor `1/8` cancels the species count.  The physical diagonal quartic is
therefore still `g`, not `g/8`.

These are two different coordinate conventions, not two predictions.  An
interacting continuum convergence theorem is not proved here.

<a id="section-10-pah1-tangent-calibration"></a>
## 10. PA-H1 tangent calibration

Use only the physical collective diagonal, choose one spatial axis and the
transverse-zero sector, and insert the registered PA-H1 circle circumference

\[
 L=\frac\pi2.
\]

The first spatial wave number is `2*pi/L=4`.  At the common ordered background,
insert

\[
 \frac{c_{\rm phys}}\chi=1,
 \qquad
 -\frac{2r}{\chi}=9.
\]

For the real modes `n=0,+1,-1`, the collective tangent squared frequencies are

\[
 9,\qquad 9+4^2=25,\qquad 9+4^2=25.
\]

This improves the ST8 calibration only by replacing an arbitrary species pick
with the unique Q3 collective singlet.  The circle, axis, transverse sector,
and parameter values are still inserted.  The PA-H1 `5,5` pair is spatial,
not the Q3 triplet.  Shifting the full quartic theory around the ordered
background also creates nonlinear quadratic and cubic force terms, so no
nonlinear PA-H1 identity or quantum boundary state follows.

The three calibrated collective modes are not asserted to be the three lowest
modes of the full tangent.  Under the inserted mass tuning, the first Q3
transverse zero-momentum triplet has squared frequency `9+9*lambda/g`; placing
it strictly above `25` would require the additional input
`lambda/g>16/9` (equality produces an extra triplet at frequency five).

## 11. Finite quantum state boundary

At every fixed finite lattice, the configuration space has finite dimension.
For `chi,g>0`, `c,lambda>=0`, the real polynomial potential is coercive because
of the positive onsite quartic.  The standard Friedrichs realization has
compact resolvent, and the usual positivity-improving heat-kernel theorem gives
one unique strictly positive ground wavefunction.

The Hamiltonian commutes with global `Z2`, coarse translations, and Q3
automorphisms, so the unique ground is invariant under them.  It is not a
doublet and is not supported on the classical diagonal submanifold.  No pure
ordered finite-volume quantum state, thermodynamic broken phase, or uniform
spectral gap is proved.

The classical diagonal reduction is not an invariant full quantum Hilbert
subspace: setting all transverse coordinates to zero is a measure-zero
condition, and the trivial Q3 representation still contains states with
transverse excitations.  Quantizing the reduced Hamiltonian would define a
reduced model unless a constraint or decoupling limit were separately proved.

Only the two global classical phase-space minima are classified.  Other
stationary or metastable points are not.  The unchanged bare origin Hessian
also does not establish interacting or quantum-renormalized pole locations.

The raw finite ground energy also depends on the additive Hamiltonian
convention.  The classical comparison to `H(0,0)=0` does not identify a
physical vacuum or prove a below-empty-space sign.

<a id="section-12-causal-and-cp1-boundary"></a>
## 12. Causal and CP1 boundary

The quartic lock has zero Hessian at the origin, so it cannot repair the
continuous-time semidiscrete analytic-tail obstruction already registered as
`NG-2026-08-03-PRE-A-CP1-ST8-CONTINUOUS-TIME-EXACT-CONE`.  Around an ordered
state it adds further local harmonic species couplings, which likewise do not
create a strict waiting time.

This package advances the following CP1 clauses at fixed regulator:

- one finite phase space and Weyl algebra;
- one local deformed Hamiltonian and additive reference convention;
- one finite selected symmetric ground under standard hypotheses;
- one connected nonlinear interaction hypergraph;
- one exact interacting classical ordering sector; and
- one exact invariant collective classical reduction.

It does not supply:

- a derived block origin or restored fine translation;
- a regulator removal and counterterm theorem;
- physical empty space or a no-condensate state;
- a pure ordered selected quantum state;
- a local exact-causal finite update preserving the same energy and state;
- a controlled continuum Goursat map, corner data, or symplectic flux;
- restriction and reconstruction of the same selected quantum state; or
- a derived PA-H1 boundary role.

Therefore `CP1 complete=false` and `Pre-A complete=false`.

## 13. Adversarial review

### Objection 1: sign enumeration alone proves the global minimum

**DISMISSED only with the complete-square proof.**  Enumeration audits the old
256-point sign manifold.  The global theorem instead follows from the exact
nonnegative decomposition and its equality conditions in Section 4.

### Objection 2: the interaction is harmonic connectivity

**UPHELD.**  Its origin Hessian is zero.  The candidate is connected only as a
nonlinear interaction hypergraph at the critical origin.  Harmonic
connectivity would lift seven critical modes under a positive quadratic form.

### Objection 3: quartic minimality is universal

**UPHELD.**  The proved lower bound is only for polynomial or real-analytic,
global-Z2, origin-Hessian-preserving interactions.  It does not cover arbitrary
nonanalytic `C2` terms and does not make this polynomial unique.

### Objection 4: two classical minima imply two quantum vacua

**UPHELD.**  The fixed finite quantum ground is unique and symmetric.  A pure
ordered phase requires a separately controlled thermodynamic and pinning
limit.

### Objection 5: the collective reduction selects the physical state

**UPHELD.**  It proves a classical invariant submanifold only.  The selected
finite quantum ground has transverse fluctuations and is not supported on it.

### Objection 6: `g/8` and `g` conflict

**DISMISSED by the normalization ledger.**  `g/8` belongs to normalized finite
unweighted canonical coordinates.  The physical continuum-density convention
has a common `1/8` species weight, under which the equal-field diagonal retains
`g`.

### Objection 7: the PA-H1 pair is the Q3 triplet

**DISMISSED.**  The Q3 first transverse level has multiplicity three.  The
PA-H1 repeated frequency is the two-dimensional real spatial sine/cosine pair
in the collective singlet after the exact-circle inputs are inserted.

### Objection 8: locality preserves all parent translations

**UPHELD.**  The term is finite-range but depends on a fixed block origin.  An
explicit one-site translation counterexample is executable.

### Objection 9: negative lambda is a harmless alternative

**UPHELD.**  On the Q3 bipartite ray, the quartic coefficient is
`2g+24lambda`.  For `r<0`, the energy is unbounded already at
`lambda=-g/12` and below.  The admitted candidate uses `lambda>0`.

### Objection 10: connected order completes CP1

**UPHELD.**  The exact-causal, continuum, same-state boundary, physical
reference, and ordered quantum-state gates remain open.

## 14. Reproduction

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_verify.py --self-test
```

The primary implementation uses exact Q3 matrices, rational polynomial
derivatives, finite block maps, and full sign enumeration.  The independent
implementation does not import it; it uses integer-bit cube characters,
shifted bivariate polynomial arithmetic, and a separate sign-cut audit.

## 15. Scope ledger

Established in this candidate scope:

- an exact positive local quartic Q3 lock;
- unchanged zero-background ST8 Hessian and eight critical species modes;
- exactly two finite classical global minima;
- the same-H classical sign below the zero configuration;
- the exact sign-cut spectrum and old-manifold locking gap;
- the ordered Q3 Hessian spectrum;
- an exact invariant classical collective reduction;
- the finite versus physical normalization distinction; and
- the restricted positive-quadratic connectivity no-go.

Not established here:

- derivation or uniqueness of the locking term;
- restoration or gauging of fine one-site translation;
- harmonic origin connectivity;
- a thermodynamic or quantum phase transition;
- a pure ordered selected quantum state;
- physical empty space or a below-empty-space comparison;
- an interacting classical or quantum continuum limit;
- an exact finite causal cone or characteristic reconstruction;
- a same-state PA-H1 boundary map;
- cooling, gravity, or an event horizon;
- CP1 completion; or
- Pre-A completion.
