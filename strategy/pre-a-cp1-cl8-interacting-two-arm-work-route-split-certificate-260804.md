# Pre-A CL8 interacting two-arm work-route split

Candidate: `PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-EXACT-1D-Q3-DRIVEN-ALL-CUT-WORK-TRANSPORT-AND-DIRECT-ORDER-MICROCUT-NOGO`  
Task: `T-054`  
Claim context: `C6-SPACETIME-SIGNATURE`  
Authority: claim-nonbearing `T0` fixed-regulator strategy certificate

<a id="section-1-verdict-and-proof-boundary"></a>

## 1. Verdict and proof boundary

There is an exact interacting continuation of the passive two-arm control on
the explicitly inserted one-dimensional, per-unit-transverse-area CL8 model.
The construction uses the full eight-species Q3 polynomial, the complete
nearest-neighbour spatial density, the inherited one-dimensional kinetic
coefficient, and no phase-space ancilla.  Its nonlinear local gate has global
mixed inverses.  Consequently every monotone cut of an open directed
rectangle is reached by a unique polynomial symplectic diffeomorphism.  The
same ordered factors give exact `B(H)` unitaries, normal-density transport, and
an exact sign-indefinite local-to-global work ledger.

This is a new driven Floquet candidate.  Its inserted full-rank passive
controller changes the ordering and therefore prevents identification with
the inherited autonomous CL8 Hamiltonian, its exact flow, or its D-K-D split.
Conversely, retaining the inherited q-only kick at every microscopic bond
leaves the cross block rank deficient.  This is an exact route split, not a
Pre-A proof.

The package closes only the following fixed-regulator subgates:

```text
PA-CP1-CL8-DRIVEN-1D-Q3-DENSITY-AND-KINETIC-COEFFICIENT-TILING
PA-CP1-CL8-DRIVEN-1D-INTERACTING-LOCAL-GLOBAL-CROSS-INVERSE
PA-CP1-CL8-DRIVEN-1D-INTERACTING-OPEN-RECTANGLE-ALL-CUT-SYMPLECTIC-DIFFEOMORPHISM
PA-CP1-CL8-DRIVEN-1D-INTERACTING-BH-FORWARD-CUT-UNITARY-AND-DENSITY-TRANSPORT
PA-CP1-CL8-DRIVEN-1D-INTERACTING-EXACT-WORK-LEDGER
```

No claim card, theorem tier, `C6` status, `C0`, `N1`--`N5`, `CP1`, or Pre-A
verdict changes.

<a id="section-2-authorities-model-and-inserted-data"></a>

## 2. Authorities, model, and inserted data

The immediate parent is the passive two-arm control
`PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0`.
The inherited one-dimensional canonical normalization comes from
`PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0`; the eight-species polynomial comes
from `PA-CP1-ST8-Q3LOCK-v0`; and the quantum algebra firewall comes from the
finite-quantum-state and boundary-algebra route splits.

The selected model is not the original three-dimensional Q3LOCK regulator.
It is the already inserted transverse-zero, per-unit-transverse-area model.
Fix

```text
M even, M>=4, L>0, a=L/M, w=a/8, mu=chi*w,
chi>0, c>0, g>0, lambda>0, r real, hbar>0, tau!=0,
gamma^2+eta^2=1, gamma*eta!=0.
```

One leg carries `q,p in R^8`, with `p=w Pi` and

```text
Omega_leg=sum_e dp_e wedge dq_e.
```

Every admitted `M`-leg cut therefore has exactly `16M` real canonical
coordinates.  The controller, directed rectangle, microstep, one-dimensional
reduction, `hbar`, and any characteristic interpretation remain inserted.

<a id="section-3-exact-1d-q3-term-ownership"></a>

## 3. Exact one-dimensional Q3 term ledger

Label the Q3 vertices by three-bit strings and write `e~f` when two strings
differ in one bit.  There are exactly twelve undirected Q3 edges.  Define

```text
W_Q3(q)
 =sum_e [r*q_e^2/2+g*q_e^4/4]
  +(lambda/4) sum_(e~f) (q_e-q_f)^2 (q_e^2+q_f^2).
```

The one-dimensional periodic potential is

```text
U_a(q)=w sum_j [c*||q_(j+1)-q_j||^2/(2*a^2)+W_Q3(q_j)].
```

Assign the bond density

```text
V_j(q_j,q_(j+1))
 =w [c*||q_(j+1)-q_j||^2/(2*a^2)
     +(W_Q3(q_j)+W_Q3(q_(j+1)))/2].
```

Then, exactly and without a boundary remainder,

```text
sum_(j in Z/MZ) V_j=U_a.
```

Each spatial bond has one owner and each onsite term has two half-owners.  The
even bonds `(0,1),(2,3),...` and odd bonds
`(1,2),(3,4),...,(M-1,0)` partition the ring.

For an edge term with `x=q_e`, `y=q_f`, its two force contributions are

```text
d_x [(lambda/4)(x-y)^2(x^2+y^2)]
 =(lambda/2)[(x-y)(x^2+y^2)+(x-y)^2*x],

d_y [(lambda/4)(x-y)^2(x^2+y^2)]
 =(lambda/2)[-(x-y)(x^2+y^2)+(x-y)^2*y].
```

These formulas fix the factor and sign conventions used by both executable
audits.

The inherited one-dimensional kinetic function is

```text
T_a(p)=sum_j ||p_j||^2/(2*mu).
```

Set `h=tau/4`.  In one even-plus-odd period, each node enters one gate in
each layer, and each gate contains an input and output drift.  Hence each node
receives four `D_h` shears, totaling `4h=tau`.  This is an exact coefficient-
occurrence ledger.  It is not a claim that the interleaved shears combine into
one global kinetic exponential or that the product equals the autonomous
Hamiltonian flow.

<a id="section-4-local-driven-interacting-gate"></a>

## 4. Local interacting gate

For a single leg define the exact kinetic shear

```text
D_h(q,p)=(q+(h/mu)*p,p).
```

For west and south legs, let `V=V(q_W,q_S)`, `V_W=grad_(q_W)V`, and
`V_S=grad_(q_S)V`.  Define

```text
K_(tau,V)(q_W,p_W,q_S,p_S)
 =(q_W,p_W-tau*V_W,q_S,p_S-tau*V_S),

G(Z_W,Z_S)
 =(gamma*Z_W+eta*Z_S,-eta*Z_W+gamma*Z_S),

F=(D_h direct-sum D_h) after G after K_(tau,V)
  after (D_h direct-sum D_h).
```

Both shears are global polynomial symplectomorphisms.  `G` is an orthogonal
symplectomorphism on complete equal-normalization legs.  Therefore `F` is a
global polynomial symplectomorphism of `R^32`.  Its temporal inverse is the
reverse factor product

```text
F^(-1)=(D_(-h) direct-sum D_(-h)) after K_(-tau,V) after G^T
       after (D_(-h) direct-sum D_(-h)).
```

The `G` factor is an explicit controller insertion.  It is not hidden inside
`T_a`, `U_a`, a counterterm, or a change of variables.

<a id="section-5-global-mixed-inverses"></a>

## 5. Global nonlinear mixed inverse

The nonlinear cross property is global, not merely a nonzero local
determinant.  Given the pre-drift west leg `W` and final north leg `N`, set

```text
W1=D_h(W),     N1=D_(-h)(N).
```

At the central kick-plus-controller stage solve, componentwise,

```text
q_S1=(q_N1+eta*q_W1)/gamma,

p_S1
 =[p_N1+eta*(p_W1-tau*V_W(q_W1,q_S1))]/gamma
  +tau*V_S(q_W1,q_S1).
```

The first equation determines the complete `q_S1` before either gradient is
evaluated.  Thus the quartic coupling creates neither an implicit branch nor
a caustic.  Recover

```text
S=D_(-h)(S1),
```

use the explicit central east formula

```text
q_E1=(q_W1+eta*q_N1)/gamma,
p_E1=(p_W1+eta*p_N1-tau*V_W(q_W1,q_S1))/gamma,
```

and set `E=D_h(E1)`.  The
`eta`-oriented solve is analogous.

For the central map, at fixed west input, the opposite-leg projection-block
determinants are

```text
det partial(N1)/partial(S1)=gamma^16,
det partial(E1)/partial(S1)=eta^16.
```

The Hessian-dependent terms occur only below the block diagonal.  The input
and output drifts have determinant one, so the same cross determinants hold
for the full gate.  They are nonzero throughout the declared parameter
domain and are independent of `r,g,lambda,c` and the field value.  The
complete temporal `32`-dimensional symplectic map itself has determinant one.

The mixed map preserves the corresponding signed difference symplectic form.
This is not strict continuous-variable dual-unitarity on four ordinary
positive-orientation tensor factors.

<a id="section-6-open-rectangle-all-cut-theorem"></a>

## 6. Open-rectangle all-cut theorem

Let `m,n` be positive and `m+n=M`.  Put a copy of `F` at every vertex
`1<=i<=m`, `1<=j<=n`.  The west arm consists of `X_(0,j)` and the south arm
of `Y_(i,0)`.  They meet geometrically at a corner but share no edge variable.
There is no corner constraint, ancilla, quotient, or symplectic radical.

Apply the recurrence

```text
(X_(i,j),Y_(i,j))=F(X_(i-1,j),Y_(i,j-1)).
```

Induction on `i+j` proves existence and uniqueness of every edge.  Ready
incomparable vertices use disjoint unresolved pairs, so their operations
commute.  Hence all topological sweeps give the same assignment.

An order ideal is represented by nonincreasing row lengths

```text
m>=r_1>=...>=r_n>=0.
```

Its frontier contains exactly `m+n=M` legs.  Advancing the frontier through
one ready vertex applies one global symplectic diffeomorphism to two frontier
factors.  Reversing advances applies its exact inverse.  Therefore the map
from the two input arms to every one of the `binomial(m+n,m)` monotone cuts is
a global polynomial symplectic diffeomorphism.

The mixed inverse also gives a global west-plus-north to east-plus-south
reconstruction: sweep columns from west to east and, within each column, rows
from north to south.  Every step has the required west and north legs already
known.  This proves global reconstruction rather than only local block rank.

Each edge depends only on the finite southwest input rectangle.  This exact
graph-causal support is not a continuum light cone or a derivation of the
speed of light.  The theorem is acyclic and open; no arbitrary periodic
two-arm seam or monodromy statement is included.

<a id="section-7-periodic-companion-and-ordering-boundary"></a>

## 7. Periodic companion and ordering boundary

On the same even `M`-node ring, place the declared gate on all disjoint even
bonds and then on all disjoint odd bonds, including `(M-1,0)`.  Each half
layer is a product of global polynomial symplectomorphisms on disjoint pairs.
The full period and its reverse are therefore global polynomial
symplectomorphisms of the same `16M`-dimensional phase space.  The forward and
inverse graph radii are finite at every fixed number of layers.

The bond ledger of Section 3 assigns every Q3/spatial potential coefficient
once and the four quarter-shears assign the inherited kinetic coefficient
once per period.  A separate controller entry is attached to every bond
gate.  Nothing is omitted or double-counted in this ledger.

Nevertheless, coefficient ownership is not model identity.  The odd-layer
potential is evaluated after the even-layer drift, kick, and controller, so
the product is not the commuting global `K_(tau U_a)`.  It is not the
inherited D-K-D order or the exact autonomous `H_a` flow.  At fixed
nontrivial `gamma,eta`, its local zero-step limit retains `G` rather than
approaching the identity.  The periodic ring and open directed rectangle are
also distinct global graphs; no seam map or exact Cauchy/Goursat intertwiner
is inferred from their shared local polynomial.

<a id="section-8-exact-work-ledger"></a>

## 8. Exact work ledger

For any inserted `nu>0` define the positive reference action

```text
I_nu(q,p)=(nu*||q||^2+||p||^2/nu)/2.
```

This is a bookkeeping reference, not the physical energy or vacuum
normalization.  For one leg,

```text
I_nu(D_h(q,p))-I_nu(q,p)
 =(nu*h/mu) q dot p+(nu*h^2/(2*mu^2))||p||^2.
```

For the pair kick, evaluated after the input drifts,

```text
Delta_K I_nu
 =-(tau/nu)(p_W dot V_W+p_S dot V_S)
  +(tau^2/(2*nu))(||V_W||^2+||V_S||^2).
```

The complete-leg controller contributes zero because it is orthogonal with
the same `nu` on both legs.  Define `W_v` as the sum of the two input-drift
increments, the kick increment, and the two output-drift increments evaluated
at their actual intermediate states.  Direct substitution gives

```text
I_nu(E)+I_nu(N)-I_nu(W)-I_nu(S)=W_v.
```

Summing over any order ideal cancels every internal frontier term exactly:

```text
sum_(target cut) I_nu-sum_(input arms) I_nu=sum_(v in ideal) W_v.
```

The result is sweep independent.  `W_v` is sign indefinite, so this proves
work accounting, not conservation of `I_nu`, `H_a`, a common positive
invariant, passivity, or a stationary Gibbs state.

<a id="section-9-interacting-bh-cut-unitaries-and-density-transport"></a>

## 9. Interacting B(H) cut unitaries and density transport

One leg has `H_leg=L2(R^8)`.  Every cut has the canonically enumerated Hilbert
space `L2(R^(8M))`.  Define the single-leg drift and pair kick

```text
Dhat_h=exp[-i*h*||P||^2/(2*mu*hbar)],
Khat_V=exp[-i*tau*V(Q_W,Q_S)/hbar],
```

and let `Ghat` be a metaplectic implementation of the complete-leg passive
controller.  The local forward unitary is

```text
U_F=(Dhat_h tensor Dhat_h) Ghat Khat_V
    (Dhat_h tensor Dhat_h).
```

Each factor is unitary: the drift and polynomial phase are functional-calculus
unitaries of self-adjoint multiplication or kinetic operators, and `Ghat` is
metaplectic.  An ordered product over an order ideal gives a forward-cut
unitary `U_I`.  Ready-vertex ordering is immaterial because ready gates act on
disjoint tensor factors.

Thus

```text
rho_I=U_I rho_in U_I^*
```

preserves positivity, trace class, trace one, and normality for every input
density.  On observables, `A -> U_I^* A U_I` is a normal star-isomorphism of
`B(H)`.

The quantum work formula is the symmetrized operator version of Section 8.
It holds as a quadratic-form identity on the common Schwartz core and in
expectation for densities with the required finite polynomial moments.  In
particular, for one leg it uses

```text
Delta_D Ihat_nu
 =(nu*h/(2*mu))(Q dot P+P dot Q)
  +(nu*h^2/(2*mu^2))||P||^2,

Delta_K Ihat_nu
 =-(tau/(2*nu))(P dot g(Q)+g(Q) dot P)
  +(tau^2/(2*nu))||g(Q)||^2
```

rather than replacing noncommuting operators by a classical product.

The nonlinear phase does not normalize the regular Weyl C-star algebra in the
required linear-generator sense.  No nonlinear Weyl relabeling, stationary
density, preferred state, or mixed-reshuffling quantum unitary is claimed.

<a id="section-10-direct-order-microcut-no-go"></a>

## 10. Direct-order/every-microcut route split

Negative ID:
`NG-2026-08-04-PRE-A-CP1-CL8-EXACT-ORDER-EVERY-MICROCUT-SIDEWAYS`.

For a q-only bond kick, the cross derivative from the opposite complete
phase leg has the form

```text
[       0       0 ]
[ -tau*V_WS     0 ].
```

Its rank is at most eight, whereas a complete CL8 leg has phase dimension
sixteen.  Multiplying this block on either side by the invertible drift
Jacobian does not change its rank.  Therefore neither the inherited q-only
bond kick nor a controller-free `D_h K D_h` bond tile can itself be a
full-sideways microscopic two-arm gate.

Adding nontrivial `G` restores full rank, but later bond potentials are then
evaluated on controller-rotated positions.  Moreover, at fixed nontrivial
`gamma,eta`, the local `tau -> 0` limit retains `G`, while an inherited
Hamiltonian step tends to the identity.  Hence this directly interleaved
microgate architecture cannot simultaneously be called

- the exact inherited commuting `K_(tau U_a)` or D-K-D order; and
- a full-rank sideways gate at every microscopic bond cut.

This does not exclude macro-cuts that hide kick-only layers, a controller
scaled to zero with a separately proved limit, an energy-preserving chiral or
variational discretization, or a different common parent.

<a id="section-11-gate-resolution-and-next-contract"></a>

## 11. Gate resolution and next contract

The fixed-regulator driven work-and-transport branch is closed.  The next
gate is

```text
PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER.
```

It must remove or derive the controller and relate one exact dynamics on the
periodic Cauchy and open two-arm graphs.  A finite-regulator bridge from the
inserted one-dimensional `w=a/8` theory to the original three-dimensional
`a^3/8` Q3LOCK theory is separately required.  A common selected state,
energy/reference convention, regulator-compatible family, continuum state,
and Hadamard test remain absent.

Accordingly:

- `C0` is open because the regulator, reduction, order, controller, microstep,
  `hbar`, and boundary interpretation are inserted;
- `N1` has only an exact driven `B(H)` transport example, not a selected
  common-parent state;
- `N2` has a driven open-rectangle evolution, not an intertwiner to the
  inherited Cauchy dynamics;
- `N3`--`N5`, `CP1`, `C6`, and Pre-A remain open.

<a id="section-12-devils-advocate-audit"></a>

## 12. Devil's-advocate and code-discipline audit

1. **Objection: the one-dimensional density was silently identified with the
   original three-dimensional Q3LOCK regulator.**  **UPHELD as a boundary.**
   The weights, Hilbert spaces, and graph dimensions differ.  This certificate
   is explicitly limited to the inserted `w=a/8` model.
2. **Objection: complete coefficient ownership proves the inherited dynamics.**
   **UPHELD.**  The controller changes the order.  The result is labelled a new
   driven Floquet candidate, not an exact `H_a` flow or D-K-D step.
3. **Objection: a nonzero local determinant might hide nonlinear branches.**
   **DISMISSED.**  The displayed formula first solves `q_S1` linearly and then
   evaluates the gradients, giving a global polynomial inverse.
4. **Objection: the drift can spoil the central cross determinant.**
   **DISMISSED.**  It conjugates the mixed map by determinant-one single-leg
   shears, so the determinants remain `gamma^16` and `eta^16`.
5. **Objection: the energy statement reuses the passive invariant.**
   **DISMISSED by narrowing.**  Only the exact sign-indefinite work identity is
   asserted; conservation and stationarity are false/unproved.
6. **Objection: the quantum work formula ignores ordering.**
   **DISMISSED.**  The certificate uses the symmetrized quadratic-form identity
   on a declared common core and finite-moment states.
7. **Objection: the negative result excludes every possible interacting
   circuit.**  **DISMISSED by scope.**  It excludes only the direct attempt to
   retain q-only inherited micro-order while demanding full sideways rank at
   every such microcut.
8. **Sign and factor audit.**  The Q3 edge gradient, half-onsite bond ownership,
   `p=w Pi`, `mu=chi*w`, `h=tau/4`, kick sign, and Heisenberg phase sign are
   independently recomputed rather than copied as derived numerals.
9. **Units and limit audit.**  `h*p/mu` has field units and
   `tau*grad V` has momentum units.  `tau -> 0` exposes the fixed controller;
   `eta -> 0` or `gamma -> 0` correctly destroys one mixed orientation and is
   outside the stated domain; `lambda -> 0` is a useful code limit but is not
   the admitted locked-Q3 model because the theorem fixes `lambda>0`.
10. **Convergence audit.**  No regulator-removal or infinite-product claim is
    made.  All classical identities are finite polynomial identities and all
    quantum products contain finitely many unitaries at fixed `M,m,n`.
11. **Hardcode-masking audit.**  The executable checks derive all forces,
    ledgers, ranks, cut counts, and work differences from upstream parameters,
    use distinct rational fixtures, and include mutated-fixture reruns.

<a id="section-13-reproduction"></a>

## 13. Reproducibility contract

The primary SymPy audit and independent standard-library `Fraction` audit must
both verify:

- the twelve-edge Q3 graph and analytic gradient;
- exact periodic bond-density ownership and four-drift kinetic ownership;
- full eight-species forward and both mixed local inverses;
- drift-conjugated cross determinants and symplectic factor identities;
- all monotone cuts and reverse reconstruction on distinct rectangles;
- exact local and global work telescoping;
- the q-only cross-rank obstruction and controller ordering witness;
- the `B(H)` direction, density-transport properties, domain firewall, scope
  flags, source hashes, and unchanged `C6` status.

The integrated verifier must rerun both audits under default, mutated, and
shared fixtures and compare only mathematical cross-invariants.  All stored
numeric evidence is exact and contains no binary floating-point values.
