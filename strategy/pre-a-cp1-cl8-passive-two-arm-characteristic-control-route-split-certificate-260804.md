# Pre-A CL8 passive two-arm characteristic-control route split

Candidate: `PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0`  
Task: `T-054`  
Claim context: `C6-SPACETIME-SIGNATURE`  
Authority: claim-nonbearing `T0` control certificate

## 1. Verdict and proof boundary

There is an exact fixed-regulator answer to the architectural question left by
the rank-deficient D-K-D circuit.  On the same `16M`-dimensional CL8 canonical
phase space, a passive two-leg rotation has full-rank cross blocks.  Two
adjacent incoming arms determine every edge of a finite directed rectangle,
every monotone bulk cut is reached by an orthogonal symplectic map, and the
same map has exact Weyl, metaplectic and `B(H)` implementations.  A positive
oscillator number and its full-Fock Gibbs density are invariant.

This closes only

```text
PA-CP1-CL8-SAME-DIMENSION-PASSIVE-FULL-RANK-SIDEWAYS-GATE
PA-CP1-CL8-PASSIVE-TWO-ARM-ALL-CUT-SYMPLECTIC-RECONSTRUCTION
PA-CP1-CL8-PASSIVE-TWO-ARM-METAPLECTIC-WEYL-BH-CUT-MAP
PA-CP1-CL8-PASSIVE-POSITIVE-NUMBER-AND-STATIONARY-GIBBS-CONTROL.
```

It does not close the interacting parent.  The inherited positive CL8
quartic kick fails to preserve the passive number, vacuum and Gibbs family.
The next question is therefore not whether a two-arm circuit can exist, but
whether the actual Q3 interaction can enter such a circuit with a new common
positive invariant or an exact work ledger.

No claim card, theorem tier, `C6` status, `C0`, `N1`--`N5`, `CP1`, or `Pre-A`
verdict changes here.

## 2. Authorities, variables and inserted structure

The immediate failed route is
`PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0`.
Its exact Cauchy cone remains valid, and its rank-eight neighbour block remains
a valid no-go for that D-K-D gate.  This certificate changes the gate rather
than superseding the negative result.

The continuum two-arm and oriented-flux bookkeeping comes from the registered
CL8 Goursat and global-continuation certificates.  The Weyl sign and
`B(H)`/Weyl firewall come from the quantum-boundary route split.  The Gaussian
Fock construction is used only as an inserted free comparator.  The positive
onsite quartic comes from `PA-CP1-ST8-Q3LOCK-v0`.

Fix an even `M>=4`, `L>0`, `a=L/M`, and `w=a/8`.  One directed leg carries
exactly the variables of one existing CL8 node,

```text
z=(q_1,...,q_8,p_1,...,p_8),   p_e=w Pi_e,
Omega_leg=sum_e dp_e wedge dq_e.
```

There are exactly `M` legs on every admitted cut, hence `16M` real canonical
coordinates.  Enumerating those legs by the `M` node labels is a canonical
relabeling, not an ancilla construction.  The brickwork pairing, directed
rectangle, microstep, `hbar`, oscillator frequency and characteristic/null
interpretation are nevertheless inserted.  They are not derived from the
static CL8 functional.

<a id="section-3-passive-local-gate"></a>

## 3. Passive local gate and full block rank

Let `gamma,eta` be real and satisfy

```text
gamma^2+eta^2=1,   gamma eta != 0.
```

At one vertex write `W,S` for the west and south input legs and `E,N` for the
east and north output legs.  Define

```text
[ E ]   [ gamma I_16   eta I_16 ] [ W ]
[ N ] = [ -eta I_16  gamma I_16 ] [ S ].
```

If `J_leg` represents either sign of `Omega_leg`, direct multiplication gives

```text
G^T diag(J_leg,J_leg) G
  =(gamma^2+eta^2) diag(J_leg,J_leg),
G^T G=(gamma^2+eta^2) I_32.
```

Thus `G` is symplectic and orthogonal on the declared parameter locus, with
inverse `G^T`.  All four input-output blocks are nonzero scalar multiples of
`I_16`; their ranks are therefore exactly 16 throughout the domain.  This is
the load-bearing difference from the old rank-eight D-K-D neighbour block.

A reproducible rational point is derived from a Pythagorean pair:

```text
gamma=(u^2-v^2)/(u^2+v^2),
eta=2uv/(u^2+v^2).
```

The primary fixture `u=2,v=1` gives `3/5,4/5`.  The independent audit uses a
different integer pair and rectangle.

<a id="section-4-oriented-sideways-inverses"></a>

## 4. Oriented sideways inverses

The full cross rank gives two useful adjacent-side solves.  From `(W,E)` one
gets `(N,S)` by

```text
[ N ]   [ -I/eta          (gamma/eta) I ] [ W ]
[ S ] = [ -(gamma/eta) I       I/eta     ] [ E ].
```

From `(W,N)` one gets `(E,S)` by

```text
[ E ]   [ I/gamma        (eta/gamma) I ] [ W ]
[ S ] = [ (eta/gamma) I   I/gamma       ] [ N ].
```

These are not ordinary positive-energy time steps.  Moving an outgoing edge
to the input side reverses its flux orientation.  With

`Gamma=diag(J_leg,-J_leg)`, both displayed maps preserve the corresponding
oriented difference form after the stated ordering is used.  Equivalently,
after turning the reversed leg back into a standard positive-orientation
oscillator, the mixed solve is a squeeze rather than a passive rotation.

Consequently:

- the complete classical sideways inverse exists and is symplectic;
- its denominators are nonzero pointwise for every admitted fixed pair; but
- oscillator number and Gibbs invariance are not claimed for a mixed
  sideways reshuffle.

The stationary-state theorem below applies to the designated monotone
west-plus-south to bulk-cut maps, each of which is a product of the original
passive `G` gates.  In particular, this is not strict continuous-variable
dual-unitarity: the literal four-leg kernel is not asserted unitary under
every reshuffling, although the separately normalized oriented canonical map
has its metaplectic implementation between the signed tensor products
`H_first tensor conjugate(H_second)` and the corresponding output space.
Momentum reversal is anti-symplectic on a same-positive-orientation factor,
so no ordinary metaplectic unitary on that same oriented Hilbert space is
being asserted.

<a id="section-5-two-arm-boundary-and-corner"></a>

## 5. Two-arm boundary, corner, constraints and quotient

Choose positive integers `m,n` with `m+n=M`.  Put vertices at
`1<=i<=m`, `1<=j<=n`.  Denote horizontal edges by `X_(i,j)` and vertical
edges by `Y_(i,j)`.  The input consists of

```text
west arm:  X_(0,j), j=1,...,n,
south arm: Y_(i,0), i=1,...,m.
```

The arms meet geometrically at the southwest corner, but they do not share a
directed edge variable.  There is no duplicated corner coordinate and no
independent third datum.  This edge convention is deliberately different
from a continuum field-value Goursat corner, where equality of the two endpoint
values is a compatibility condition.

The control boundary therefore has:

```text
real dimension     =16(n+m)=16M,
constraint space   ={0},
symplectic radical ={0},
reduced quotient   =the full boundary space.
```

At every vertex apply

```text
(X_(i,j),Y_(i,j))
  =G(X_(i-1,j),Y_(i,j-1)).
```

The final east and north arms contain the same number of full CL8 legs.

<a id="section-6-all-cut-reconstruction"></a>

## 6. All-cut reconstruction, sweep independence and causality

Order the vertices by the product order.  Induction on `i+j` constructs every
internal edge uniquely.  A monotone cut is the frontier of an order ideal.
It can be encoded by nonincreasing row lengths

```text
m>=r_1>=r_2>=...>=r_n>=0.
```

Its horizontal legs are `X_(r_j,j)`.  Its vertical leg in column `i` is
`Y_(i,c_i)`, where `c_i=max{j:r_j>=i}` and is zero when the set is empty.
There are always `n+m=M` legs.  The number of such cuts is

```text
binomial(m+n,m).
```

Advancing a cut through one ready vertex replaces its two incoming legs by
its two outgoing legs through `G`.  Every advance is orthogonal and
symplectic.  Therefore the map `C_I` from the two input arms to any admissible
cut satisfies

```text
C_I^T C_I=I,
C_I^T J_cut C_I=J_input,
C_I^(-1)=C_I^T.
```

Summing the local identities gives the same result by cancellation:

```text
sum_input Omega = sum_cut Omega,
sum_input ||z||^2 = sum_cut ||z||^2.
```

Row-first and column-first sweeps agree because both solve the same acyclic
recurrence.  More generally, incomparable ready vertices act on disjoint
frontier factors and commute, so every topological sweep gives the same cut
values.  Reverse cut moves reconstruct the arms, proving bijectivity rather
than only forward existence.

The coefficient of `X_(i,j)` or `Y_(i,j)` vanishes outside its southwest
rectangle: it can depend only on west inputs with row index at most `j` and
south inputs with column index at most `i`.  This is an exact discrete causal
support theorem, not an asymptotic group-velocity statement.

## 7. Periodic Cauchy companion

On the same even periodic `M`-node phase space, apply `G` first to the disjoint
even bonds and then to the disjoint odd bonds, including the wrap bond.  Each
half-layer is radius one, orthogonal and symplectic.  One full brickwork period
is reversible and has graph radius at most two; its inverse has the same
finite support.

This periodic object is only a Cauchy companion on the same variables.  The
two-arm theorem above is for open rectangles and their acyclic monotone cuts;
arbitrary wrapped two-arm data require a separate seam and monodromy analysis
and are not proved here.

This supplies a finite-depth Cauchy companion on exactly the same canonical
variables.  It is not the inherited nonlinear D-K-D update and is not an
exact time step of the autonomous CL8 Hamiltonian.  The velocity `a` per
microstep, or `2a` per full brickwork period, is a regulator convention and is
not the derived speed of light.

<a id="section-8-quantum-cut-map"></a>

## 8. Quantum cut map, Weyl algebra and B(H)

One leg has `H_leg=L2(R^8)`.  Every cut has `M` legs and is canonically
identified with

```text
H_cut=L2(R^(8M)).
```

If `C_I` is the real orthogonal mode matrix of an admissible cut, an explicit
unitary is

```text
(U_I Psi)(Q)=Psi((C_I^T tensor I_8)Q).
```

Its Jacobian has absolute determinant one.  On the common Schwartz core its
Heisenberg action sends both `Q` and `P` by `C_I`, so it implements the full
canonical cut map.  Equivalently it is the passive metaplectic or bosonic
second-quantized implementer.

There are two distinct but compatible algebra statements:

1. The symplectic map induces the kinematic Weyl isomorphism
   `W_in(z) -> W_cut(C_I z)`.
2. After identifying both cuts with one fixed Hilbert space and defining
   `alpha(A)=U_I^* A U_I`, the convention
   `W(z)=exp(i sigma(z,Z)/hbar)` gives
   `alpha(W(z))=W(C_I^(-1)z)`.

Conjugation also gives an exact normal star-isomorphism of the corresponding
`B(H)` algebras.  These statements use the full Fock/Schrodinger space; no
finite-dimensional oscillator cutoff is introduced.  They do not quantize
the nonlinear CL8 Goursat map by direct Weyl-generator relabeling.

<a id="section-9-positive-generator-and-state"></a>

## 9. Positive generator and actual stationary states

Insert `nu>0` and `hbar>0`, and define

```text
a_(j,e)=(sqrt(nu)q_(j,e)+i p_(j,e)/sqrt(nu))/sqrt(2hbar),
N=sum_(j,e) a_(j,e)^* a_(j,e).
```

The corresponding classical positive invariant action is

```text
I_nu=(1/2)sum_(j,e)[nu q_(j,e)^2+p_(j,e)^2/nu].
```

Every `G` mixes complete modes by the same real orthogonal matrix, hence
preserves `I_nu` and commutes with `N`.  The oscillator energy is
`H_nu=nu I_nu`; the same invariance is true of every monotone cut unitary and
the periodic brickwork companion.

Let `D=8M` and `zeta=exp(-beta_T hbar nu)` for `beta_T>0`.  Then

```text
Tr zeta^N=(1-zeta)^(-D),
rho_beta=(1-zeta)^D zeta^N.
```

Thus `rho_beta` is a faithful positive trace-one trace-class density on the
full infinite-dimensional Hilbert space.  The input and every monotone target
cut carry a covariant copy satisfying `U_I rho_beta U_I^*=rho_beta` after the
declared canonical edge enumeration.  This is cut covariance between the
source and target algebras.  Genuine stationarity on one fixed algebra holds
for the periodic brickwork companion.  The same statements hold for the
vacuum projector.  An arbitrary density is merely transported by
`rho_I=U_I rho U_I^*`.

The positive invariant used here is

```text
K_nu=hbar nu N>=0.
```

Its vacuum value zero is a declared normal-ordering convention.  The raw
oscillator Hamiltonian adds `D hbar nu/2=4M hbar nu`.  Neither convention is a
physical empty-space definition.  Moreover `nu`, `hbar`, `beta_T`, the complex
structure and the ground/KMS criterion are all inputs.  The continuum of
stationary `beta_T` states supplies no preference by stationarity alone.

<a id="section-10-cl8-quartic-reuse-no-go"></a>

## 10. The CL8 quartic cannot reuse the passive number/state ledger

The inherited Q3 model contains the positive onsite term `w g q^4/4` with
`g>0`.  Its position kick sends one canonical momentum to

```text
p' = p-delta w g q^3.
```

For the passive invariant action of that coordinate,

```text
Delta I_nu
 =-(delta w g/nu)p q^3
  +(delta^2 w^2 g^2/(2nu))q^6.
```

At `p=0`, nonzero `q` and nonzero `delta`, this is strictly positive.  Hence
the passive invariant cannot simply be carried through the CL8 quartic kick.

The quantum obstruction is equally direct.  With

```text
Q=sqrt(hbar/(2nu))(a+a^*),
```

the oscillator basis gives

```text
<4|[N,Q^4]|0>
 =4 sqrt(24) (hbar/(2nu))^2 != 0.
```

The strictly positive Gaussian vacuum is multiplied in configuration space by
`exp[-i delta w g x^4/(4hbar)]`, a nonconstant phase for every nonzero
`delta*w*g`; it is therefore not taken to a scalar multiple of itself.  Since
`rho_beta` is an injective function of `N`, the same noncommutation blocks
automatic Gibbs stationarity.

This no-go is not a classical sideways-inversion no-go.  For a local gate
`F=G o K_V` applied after a `q`-only kick with gradients `V_W,V_S`, pre-kick
`W=(q_W,p_W)` and output `N` give the triangular solve

```text
q_S=(q_N+eta q_W)/gamma,
p_S=[p_N+eta(p_W-delta V_W)]/gamma+delta V_S.
```

The first equation determines the position at which both gradients are
evaluated, so the second is explicit.  The displayed `Delta I_nu` is also an
exact local work increment.  What remains unproved is the actual CL8 coupling
assignment and gate tiling, its all-cut theorem, and a common global
invariant-or-work/state ledger.

This registers
`NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE`.
It rejects only reuse of this passive number and state family.  It does not
exclude a new interacting invariant, an exact work ledger, a nonlinear
number-conserving parent with a proved CL8 reduction, or a larger `B(H)` model
with a separately transported density.

## 11. Gate resolution and next falsifiable target

Closed in passive fixed-regulator control scope:

- same CL8 canonical dimension and `a/8` momentum normalization;
- general full-rank temporal and sideways local maps;
- explicit two arms, one geometric corner, zero constraints and zero radical;
- unique, sweep-independent, reversible, causal and symplectic reconstruction
  to every monotone cut;
- exact metaplectic, Weyl and `B(H)` cut maps; and
- a positive invariant plus actual stationary full-Fock Gibbs densities.

Still open:

- the inherited Q3 interaction in the same characteristic circuit;
- either an interacting positive invariant plus stationary density, or an
  exact work ledger plus transported states only;
- the interacting boundary-bulk algebra intertwiner;
- a regulator-compatible selected state and continuum/Hadamard limit;
- physical empty space and any below-empty-space comparison; and
- `C0`, `N1`--`N5`, `C6`, `CP1`, and `Pre-A`.

The next gate is

```text
PA-CP1-CL8-INTERACTING-SIDEWAYS-GATE-COMMON-INVARIANT-STATE.
```

## 12. Devil's-advocate audit

### Objection 1: left and right channels doubled the CL8 degrees of freedom

**DISMISSED.**  A cut has exactly `M` legs, each leg is exactly one existing
eight-species canonical node, and the real dimension stays `16M`.  The two
arms partition those legs as `n+m=M`.

### Objection 2: one local rank computation was called a global theorem

**DISMISSED.**  The analytic block rank holds for every admitted
`gamma,eta`; all order-ideal cuts are constructed, local fluxes cancel, and
reverse sweeps give exact global inverses.  Independent fixtures use different
Pythagorean parameters and rectangle sizes.

### Objection 3: the mixed sideways solve is another passive unitary

**VALID WITH MITIGATION.**  Its oriented symplectic form has one reversed
edge.  After standard-orientation identification it is a squeeze and does not
preserve positive oscillator number.  Gibbs invariance is restricted to
monotone cut maps built from the original passive gate.

### Objection 4: unitary transport was relabeled as stationarity

**DISMISSED.**  Arbitrary densities are only transported.  Stationarity of
the displayed vacuum/Gibbs family is separately proved from commutation with
`N`.

### Objection 5: the oscillator vacuum is physical empty space

**UPHELD AS AN OVERCLAIM PROHIBITION.**  The complex structure, frequency,
normal ordering and ground criterion are inputs.  No physical empty-space or
no-condensate criterion is supplied.

### Objection 6: the CL8 quartic can be appended without changing the result

**UPHELD.**  The exact classical energy defect and quantum number commutator
show that the passive energy and state ledger then fails.

### Objection 7: sharing the CL8 phase dimension makes this interacting CL8

**UPHELD AS AN OVERCLAIM PROHIBITION.**  The update is a new passive
brickwork rule.  It neither equals nor exactly intertwines the Q3 D-K-D,
continuum Goursat, or autonomous Hamiltonian dynamics.

### Objection 8: the circuit cone derives nullness or light speed

**UPHELD AS AN OVERCLAIM PROHIBITION.**  Orientation, pairing and step are
inserted.  Finite support proves circuit causality only.

### Objection 9: a finite Fock cutoff was used to obtain a density

**DISMISSED.**  The density is the exact trace-class geometric function of
`N` on `L2(R^(8M))`.  Finite ladder matrices are used only as an exact local
matrix-element witness, not as the CCR representation.

External mathematical and physical review is invited.

## 13. Reproduction

Run

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_passive_two_arm_characteristic_control_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_passive_two_arm_characteristic_control_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_passive_two_arm_characteristic_control_route_split_verify.py
```

The primary audit derives the general local identities and an exact rational
all-cut rectangle.  The non-importing standard-library audit uses different
Pythagorean and geometry inputs.  The integrated verifier rebuilds both
artifacts, checks source and authority hashes, the formal negative,
exploration/changelog/task routing, unchanged `C6` status, and stored-result
freshness.
