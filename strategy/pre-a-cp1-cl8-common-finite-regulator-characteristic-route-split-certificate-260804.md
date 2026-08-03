# Pre-A CP1 CL8 common finite-regulator characteristic route split

Candidate: `PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-EXACT-CAUSAL-CAUCHY-FLOQUET-BH-STATE-TRANSPORT-AND-ROUTE-NOGOS`  
Date: 2026-08-04  
Status: T0, claim-nonbearing, conditional fixed-regulator result

## 1. Verdict and proof boundary

There is an exact common classical and quantum finite-regulator model on the
current CL8 variables: the symmetric kinetic/potential split circuit.  It has
all of the following properties at every fixed even regulator:

1. an exact nonlinear symplectic update;
2. exact reversal and a radius-one discrete dependency cone;
3. an exact finite-depth unitary implementation on the same Schrodinger
   Hilbert space and with the same declared `hbar`;
4. a normal `B(H)` automorphism with an exact local-algebra cone;
5. exact transport of every declared density state; and
6. exact metaplectic Weyl covariance in the quadratic tangent sector.

This does **not** close the parent characteristic-model gate.  Four distinct
extensions fail:

- the quartic kick does not normalize the nonlinear Weyl C-star algebra;
- the causal split does not conserve the inherited autonomous CL8 Hamiltonian
  or automatically retain its ground/Gibbs stationarity;
- the bounded principal Floquet logarithm has no trace-class Gibbs exponential
  on the infinite-dimensional Hilbert space; and
- the neighbour transfer is rank deficient sideways, so a finite Cauchy cone
  is not a two-null-side Goursat reconstruction.

The proved object is therefore an exact **causal Cauchy Floquet circuit**, not
an event horizon, a physical vacuum, a continuum QFT, or Pre-A.

## 2. Authorities and one-model convention

The exact immediate parents are:

- `PA-CP1-ST8-Q3LOCK-v0` for the eight-species Q3 interaction;
- `PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0` for the one-eighth finite Hamiltonian
  and symplectic ledger;
- `PA-CP1-FD-C1-STRICT-CONE-NOGO-v0` for the continuous-time strict-cone
  boundary;
- `PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0` for the fixed-regulator
  Schrodinger operator and registered ground/Gibbs densities; and
- `PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0` for the
  algebra, state, dynamics, and energy contract.

Let

```text
Lambda_M = Z/(MZ),       M even and M >= 4,
a = L/M,                w = a/8,
p_(j,e) = w Pi_(j,e),   mu = chi w.
```

The two canonical descriptions are exactly the same:

```text
Omega_a = sum_(j,e) dp_(j,e) wedge dq_(j,e)
        = w sum_(j,e) dPi_(j,e) wedge dq_(j,e).
```

The autonomous comparison Hamiltonian is

```text
H_a(q,p) = T_a(p) + U_a(q),
T_a(p)   = sum_(j,e) p_(j,e)^2/(2 mu),
U_a(q)   = w sum_j [ c |D_a^+ q_j|^2/2 + W_Q3(q_j) ].
```

No second normalization, fitted additive constant, independently chosen
boundary state, or separately fitted dispersion is introduced.

<a id="section-3-exact-classical-split-circuit"></a>

## 3. Exact classical split circuit

For a nonzero real step `delta`, put `h=delta/2` and define

```text
D_h(q,p)       = (q + h p/mu, p),
K_delta(q,p)   = (q, p - delta grad U_a(q)),
F_delta        = D_h o K_delta o D_h.
```

In the `(q,p)` ordering their Jacobians are

```text
J_D = [ I       (h/mu) I ],
      [ 0             I ]

J_K = [ I                    0 ],
      [ -delta Hess U_a(q)   I ].
```

With

```text
J = [ 0  I ],
    [ -I 0 ],
```

`J` represents `-Omega_a` in the `(q,p)` ordering; preserving `J` is
equivalent to preserving `Omega_a`.  With that sign convention made explicit,

direct multiplication gives

```text
J_D^T J J_D = J,
J_K^T J J_K = J
```

because `Hess U_a(q)` is symmetric.  Hence

```text
(DF_delta)^T J DF_delta = J
```

at every point.  This is an exact nonlinear symplectomorphism, not a truncation
of the symplectic identity.

The symmetric ordering also gives

```text
F_(-delta) = F_delta^(-1),
R F_delta R = F_delta^(-1),   R(q,p)=(q,-p).
```

The circuit is the exact stroboscopic map of a declared split drive.  It is not
the exact continuous-time flow of `H_a=T_a+U_a`.

## 4. Exact discrete causal cone

The Q3 onsite force at node `j` is local to that node.  The spatial Dirichlet
term contributes only `j-1`, `j`, and `j+1`.  The first drift is onsite, the kick
therefore has radius one, and the final drift is onsite.  Thus

```text
partial F_delta(z)_j / partial z_k = 0
```

whenever the periodic graph distance from `j` to `k` is greater than one.
Induction and the chain rule give

```text
partial F_delta^n(z)_j / partial z_k = 0
```

outside the periodic radius-`n` neighbourhood.  This is an exact zero, not a
Lieb-Robinson tail or an `O(a^2)` estimate.

The numerical speed `a/|delta|` is supplied by the regulator.  Exact finite
support by itself neither derives a Lorentzian light speed nor constructs null
boundary data.

<a id="section-5-exact-quantum-circuit-on-bh"></a>

## 5. Exact quantum circuit on B(H)

Use

```text
H_a = L2(R^(8M)) = tensor_j L2(R^8)
```

with the canonical Schrodinger operators

```text
[Q_(j,e),P_(k,f)] = i hbar delta_jk delta_ef.
```

The self-adjoint kinetic operator and the real polynomial multiplication
operator define the unitaries

```text
Dhat_h       = exp[-i h T_a(P)/hbar],
Khat_delta   = exp[-i delta U_a(Q)/hbar],
Uhat_delta   = Dhat_h Khat_delta Dhat_h.
```

The kick is a modulus-one multiplier even though `U_a` is unbounded.  On the
common Schwartz core, the exact commutator identities terminate:

```text
Dhat_h^* Q Dhat_h = Q + h P/mu,
Dhat_h^* P Dhat_h = P,
Khat_delta^* Q Khat_delta = Q,
Khat_delta^* P Khat_delta = P - delta grad U_a(Q).
```

Consequently the Heisenberg action of `Uhat_delta` agrees with `F_delta` on the
canonical generators.

Define

```text
alpha_delta(A) = Uhat_delta^* A Uhat_delta,
```

on `B(H_a)`.  It is a normal unital star automorphism.  `Dhat_h` is an onsite
product.  The position potential is a sum of mutually commuting onsite and
nearest-neighbour multiplication terms, so `Khat_delta` factorizes into local
phase gates.  Conjugation of a bounded algebra supported on `X` is therefore
supported on the exact radius-one neighbourhood, and the `n`-period action is
supported on the radius-`n` neighbourhood.

This exact nonlinear statement is deliberately made on `B(H_a)`.  It is not a
claim that the concrete Weyl C-star algebra is invariant.

## 6. Quadratic tangent symbol and metaplectic control

On the ordered collective tangent branch,

```text
omega_a(k)^2 = 9 + (4c/(chi a^2)) sin^2(k a/2).
```

For one canonical Fourier pair, set

```text
x_k = delta^2 omega_a(k)^2.
```

The exact D-K-D matrix is

```text
S_delta(k) =
[ 1-x_k/2                 (delta/mu)(1-x_k/4) ],
[ -delta mu omega_a(k)^2  1-x_k/2              ].
```

Direct calculation yields

```text
det S_delta(k) = 1.
```

The elliptic stability window is `0<x_k<4`.  In that window

```text
cos theta_k = 1-x_k/2,
theta_k     = 2 asin(delta omega_a(k)/2),
omega_F(k)  = theta_k/delta.
```

For the full quadratic finite regulator the update is linear symplectic, hence
metaplectically implemented, and its Heisenberg action maps Weyl generators to
Weyl generators.  More precisely, use the inherited convention

```text
W(z) = exp[i sigma(z,Z)/hbar],
alpha_delta(Z) = S_delta Z.
```

Since `S_delta` is symplectic,

```text
alpha_delta(W(z)) = W(S_delta^(-1) z).
```

Thus the label direction is fixed rather than hidden in an orientation
convention.  This is the exact Floquet frequency of the circuit.  It is not
the continuous frequency and does not repair the already registered
centered-sampling dynamics mismatch.

## 7. Exact density-state transport

Let `rho` be any positive trace-one density on `H_a`, including a registered
interacting ground projector or finite-temperature Gibbs density of the
autonomous `H_a`.  Define

```text
rho_n = Uhat_delta^n rho Uhat_delta^(-n).
```

Then `rho_n` is positive, trace one, and normal, and

```text
Tr(rho_n A) = Tr(rho alpha_delta^n(A))
```

for every bounded observable `A`.  Restriction to the Weyl generators remains
regular because unitary conjugation preserves strong continuity of the
represented one-parameter groups.

This is exact state transport, not stationarity.  The statement uses the full
finite Hilbert space, so no unaccounted symplectic complement is hidden in this
Cauchy-to-Cauchy map.

<a id="section-8-nonlinear-weyl-normalizer-no-go"></a>

## 8. Nonlinear Weyl normalizer no-go

Consider one nonzero configuration translation `T_y`, which is a Weyl unitary.
For the quartic position kick,

```text
Khat_delta T_y Khat_delta^* = M_f T_y,
f(x) = exp[-i delta (U(x)-U(x-y))/hbar].
```

Because `g>0`, a one-coordinate restriction of the phase difference has a
nonzero cubic leading term.  If `P` is that cubic polynomial, choose

```text
epsilon_n = pi/P'(x_n),   x_n -> infinity.
```

Then `epsilon_n -> 0`, while Taylor's formula gives

```text
P(x_n+epsilon_n)-P(x_n) -> pi.
```

Thus `exp(iP)` is not uniformly continuous.  Every almost-periodic function is
uniformly continuous.  The remaining algebra-intersection step is elementary
and is included here rather than assumed.  Write the concrete unital Weyl
algebra as

```text
A_W = closure span { M_xi T_y : xi,y in R^(8M) }.
```

If a multiplication operator `A=M_f` lies in `A_W`, it commutes with every
modulation `M_eta`.  Hence it is fixed by

```text
beta_eta(B) = M_eta^* B M_eta.
```

Given a finite Weyl polynomial `P=sum c_l M_(xi_l) T_(y_l)`, average
`beta_eta(P)` over the cube `[-R,R]^(8M)`.  The average multiplier of a term
with `y_l != 0` is a product of sinc factors and tends to zero; the `y_l=0`
terms remain a trigonometric multiplication polynomial.  The averaging map is
contractive.  For any norm approximation `||A-P||<epsilon`, fixedness of `A`
therefore puts `A` within `epsilon+o_R(1)` of an almost-periodic multiplier.
The almost-periodic algebra is norm closed, so `A` is almost periodic.  The
reverse inclusion is immediate from the modulation generators.  Consequently

```text
A_W intersect {multiplication operators} = AP(R^(8M)).
```

It follows that the non-uniformly-continuous `f` cannot be the multiplication
coefficient of an element `M_f T_y` in `A_W`: otherwise right multiplication
by `T_y^* in A_W` would put `M_f` in the displayed intersection.

The kinetic drifts are metaplectic normalizers.  If the full D-K-D circuit
normalized the Weyl algebra, conjugating by the drifts would make the kick a
normalizer, contradicting the witness.  Hence

`NG-2026-08-04-PRE-A-CP1-CL8-NONLINEAR-FLOQUET-WEYL-NORMALIZER` is registered.
The quadratic sector and explicitly enlarged observable algebras survive.

## 9. Inherited energy and stationarity no-go

For the harmonic Hamiltonian

```text
H_0(q,p)=p^2/(2mu)+mu omega^2 q^2/2
```

and initial data `(q,0)`, the split circuit gives

```text
p' = -delta mu omega^2 q,
q' = (1-delta^2 omega^2/2)q,
H_0(q',p')/H_0(q,0) = 1 + (delta omega)^4/4.
```

The ratio is strictly greater than one for nonzero `delta` and `omega`.  The
same obstruction occurs in the actual ordered CL8 model: along a uniform
collective perturbation of `v0=sqrt(-r/g)`, the exact analytic energy defect has
quadratic coefficient

```text
mu omega^6 delta^4/8 > 0,   omega^2=-2r/chi.
```

So the defect is not identically zero in the interacting model.

In the quadratic quantum control, failure of the matrix identity

```text
S_delta^T G S_delta = G
```

means that the metaplectic circuit does not commute with the harmonic
Hamiltonian.  Its ground covariance is squeezed and its finite-beta Gibbs
covariance is not stationary.  Consequently exact finite-depth causality does
not automatically inherit the registered autonomous ground/Gibbs stationarity.

This registers
`NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE`.
It does not exclude a separately proved invariant Floquet state or a different
energy-preserving exact-causal parent.

## 10. Principal Floquet Gibbs-reference no-go

The principal logarithm of a unitary has quasienergies in a bounded interval
of width `2 pi hbar/|delta|`.  Hence its exponential at positive beta is
bounded below by a positive multiple of the identity.  Since `H_a` is
infinite-dimensional,

```text
Tr exp(-beta H_F,principal) = infinity.
```

Thus the bounded principal Floquet Hamiltonian does not define a normal Gibbs
density.  Other logarithm branches are nonunique and may add different integer
multiples of `2 pi hbar/delta` on spectral sectors.  Floquet data alone
therefore selects neither a unique ground nor an absolute additive reference.

This registers
`NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE`.
In particular it gives no physical empty-space state and no
below-empty-space comparison.

<a id="section-11-sideways-characteristic-no-go"></a>

## 11. Sideways characteristic no-go

The exact causal cone is a forward Cauchy statement.  A local two-null-side
reconstruction additionally needs a sideways inverse.

For one species, the derivative from the neighbour input
`(q_(j+1),p_(j+1))` to the output `(q'_j,p'_j)` is proportional to

```text
[ delta/(2mu) ] [ 1  delta/(2mu) ].
[       1      ]
```

This outer product has rank one, not two.  With eight species the corresponding
block has rank at most eight, not the sixteen required to solve locally for a
full neighbouring canonical pair.  Therefore this split gate is not locally
sideways-invertible on the full phase space.

This registers
`NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-SIDEWAYS-CHARACTERISTIC`.
A chiral or dual-unitary enlargement, a proved constrained quotient, or a new
discrete Goursat scheme remains possible.

## 12. Gate resolution

Closed at fixed regulator:

- exact reversible symplectic Cauchy circuit;
- exact radius-one classical and bounded-operator cones;
- exact full interacting `B(H)` automorphism;
- exact density-state transport; and
- exact quadratic metaplectic Weyl control.

Still open:

- a sideways-invertible two-arm characteristic circuit;
- the full finite boundary Weyl algebra and exact CCR map;
- an interacting characteristic boundary-bulk dynamics intertwiner;
- a stationary and physically selected state;
- a unique energy and physical empty-space reference;
- inter-regulator state compatibility;
- the continuum/Hadamard limit; and
- C0, N1-N5, CP1, and Pre-A.

The next route is
`PA-CP1-CL8-SIDEWAYS-INVERTIBLE-TWO-ARM-CHARACTERISTIC-CIRCUIT`.

## 13. Devil's-advocate audit

### Objection 1: the factor `a/8` was dropped when passing to Schrodinger momentum

**DISMISSED.**  The canonical momentum is explicitly `p=(a/8)Pi`, so
`mu=chi a/8` and `T=sum p^2/(2mu)=sum 4p^2/(a chi)`, exactly matching the
registered operator.

### Objection 2: a symplectic integrator was relabelled as the exact autonomous flow

**DISMISSED.**  The package calls it an exact Floquet circuit and separately
proves that the autonomous Hamiltonian is not conserved.

### Objection 3: finite support was relabelled as characteristic reconstruction

**DISMISSED.**  The sideways neighbour block is calculated and its rank defect
is registered as a formal no-go.  The parent characteristic gate remains open.

### Objection 4: unitary conjugation on `B(H)` was silently treated as Weyl closure

**DISMISSED.**  The algebra types are separate.  A cubic-phase multiplier gives
an explicit nonlinear Weyl nonnormalizer witness.

### Objection 5: transported densities were called stationary or preferred

**DISMISSED.**  State transport and stationarity are separate booleans.  The
harmonic energy/covariance witness refutes automatic stationarity.

### Objection 6: a Floquet logarithm supplied a vacuum energy

**DISMISSED.**  The principal-log Gibbs trace diverges and other branches are
nonunique.  Physical empty space and the below-empty-space sign remain open.

### Objection 7: the exact cone derived a physical light speed

**UPHELD WITH BOUNDARY.**  The circuit speed `a/|delta|` is an input.  It is not
an emergent Lorentzian constant and does not advance C6.

## 14. Reproduction

Run:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_verify.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_common_finite_regulator_characteristic_route_split_verify.py --check-stored
```

The primary route uses exact symbolic algebra.  The independent route imports
neither the primary implementation nor shared derived constants and rebuilds
the decisive identities with rational polynomial and matrix arithmetic.  The
integrated verifier rebuilds both children, checks source and parent hashes,
the four negative records, the exploration and task routes, the unchanged C6
status, and stored-result freshness.
