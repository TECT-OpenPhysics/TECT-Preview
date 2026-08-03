# Pre-A double-null semilinear reconstruction certificate

**Candidate:** `PA-H1-DNKG4-v0`  
**Authority:** T0 Lane-H bridge certificate; no TECT claim or tier change  
**Claim context only:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Issued:** 2026-08-03

## 1. Question and exact scope

This certificate asks for the smallest model in which complete characteristic
boundary data determine an interior state by a theorem rather than by naming a
horizon.  It proves such a result for a fixed 1+1-dimensional Minkowski
background.  The background dimension, Lorentzian signature, time coordinate,
null directions, field equation, mass, coupling, and finite domain are inputs.
They are not derived.

Consequently, this is a boundary-to-bulk reconstruction theorem inside an
already causal theory.  It is not an event-horizon theorem, a gravitational
constraint theorem, a derivation of spacetime, or a completion of Pre-A.

## 2. Linear characteristic theorem

Let

```text
Q=[0,U] x [0,V],                 U,V>0,
partial_u partial_v phi+kappa phi=0,  kappa>=0,
phi(u,0)=A(u),  phi(0,v)=B(v),
A(0)=B(0)=c,
```

with `A in C1([0,U])` and `B in C1([0,V])`.  Define

```text
G(u,v)=A(u)+B(v)-c,
(Kf)(u,v)=int_0^u int_0^v f(s,t) dt ds.
```

### Theorem PA-H1-L

There is a unique classical solution on every finite rectangle, given by the
uniformly convergent Volterra series

```text
phi=sum_(n>=0) (-kappa)^n K^n G.
```

It obeys

```text
||K^n f||_infinity <= (U V)^n/(n!)^2 ||f||_infinity,
||phi||_infinity
 <= I0(2 sqrt(kappa U V)) ||G||_infinity,
||phi-phi_tilde||_infinity
 <= I0(2 sqrt(kappa U V)) ||G-G_tilde||_infinity.
```

For `A,B in C1`, the integral equation gives continuous first derivatives and
a continuous mixed derivative, hence the stated classical equation.  For less
regular continuous traces the same series gives the corresponding mild
Volterra solution.

### Proof

Repeated integration gives the factorial-squared estimate.  Therefore the
Neumann series converges absolutely and uniformly for every finite `U,V`; its
sum solves

```text
phi=G-kappa K phi.
```

If two solutions have the same data, their difference `d` satisfies
`d=-kappa Kd`.  Iteration gives

```text
||d|| <= (kappa U V)^n/(n!)^2 ||d||
```

for every `n`, whose right-hand coefficient tends to zero.  Thus `d=0`.
Applying the same series to a data difference yields the stability estimate.

An equivalent Riemann-Bessel representation is

```text
R(x,y)=J0(2 sqrt(kappa x y)),
phi(u,v)=c R(u,v)
 +int_0^u A'(s)R(u-s,v)ds
 +int_0^v B'(t)R(u,v-t)dt.
```

For constant compatible data it reduces to
`phi=c J0(2 sqrt(kappa u v))`.  The primary script checks the Bessel kernel
equation, both axis values, the Volterra recurrences, and the stability envelope
symbolically; the independent script checks the coefficient algebra using
rational arithmetic only.

## 3. Causal restriction and interior classical state

Fix `tau` with `0<2 tau<=min(U,V)` and set

```text
u=t+x,  v=t-x,  t=(u+v)/2.
```

The slice `t=tau` is therefore `u+v=2 tau`, not `u+v=tau`.  Let
`D_tau=C1([0,2tau]) x_corner C1([0,2tau])` be the compatible boundary-data
space.  On the causal diamond based at the corner, define

```text
P_tau(A,B)=(phi_tau,Pi_tau),
Pi=partial_t phi=partial_u phi+partial_v phi,
x in [-tau,tau].
```

Then

```text
P_tau:D_tau -> C1([-tau,tau]) x C0([-tau,tau]).
```

The differentiated Volterra equation gives

```text
partial_u phi=A'(u)-int_0^v kappa phi(u,t)dt,
partial_v phi=B'(v)-int_0^u kappa phi(s,v)ds.
```

For two data pairs, the pointwise Volterra bound on the characteristic
triangle and `u+v=2tau` give

```text
||delta phi_tau||_infinity
 <=I0(2 tau sqrt(kappa))||delta G||_infinity,

||partial_x delta phi_tau||_infinity
 <=||delta A'||_infinity+||delta B'||_infinity
   +2 kappa tau I0(2 tau sqrt(kappa))||delta G||_infinity,

||delta Pi_tau||_infinity
 <=||delta A'||_infinity+||delta B'||_infinity
   +2 kappa tau I0(2 tau sqrt(kappa))||delta G||_infinity.
```

Hence `P_tau` is an explicit continuous state map in the displayed norms.  It
depends only on the trace segments
`A|_[0,2tau]` and `B|_[0,2tau]`; changing an extension outside those segments
cannot change the reconstructed diamond.  This is causal extension
independence in the declared fixed-background model, not independence from an
unknown gravitational exterior.

## 4. Linear symplectic and algebraic-state transport

For two compatible linearized boundary data sets `d1=(A1,B1)` and
`d2=(A2,B2)` on `[0,2tau]`, define

```text
Omega_H(d1,d2)
 =int_0^(2tau) (A1 A2'-A2 A1')du
 +int_0^(2tau) (B1 B2'-B2 B1')dv,

Omega_Sigma((phi1,Pi1),(phi2,Pi2))
 =int_(-tau)^tau (phi1 Pi2-phi2 Pi1)dx.
```

The Klein-Gordon symplectic current is conserved because the equal mass terms
cancel.  Stokes' theorem on the characteristic triangle therefore gives, for
`0<2tau<=min(U,V)`,

```text
Omega_Sigma(P_tau d1,P_tau d2)=Omega_H(d1,d2).
```

The scripts verify both the general massive current identity and a nontrivial
massless boundary-to-slice fixture exactly.  The state map is injective: zero
slice data have zero `phi_x` as well as zero `Pi`, hence zero nonnegative
Klein-Gordon energy; the exact boundary flux balance below then forces zero
boundary derivatives (and, when `mu>0`, zero boundary values), while for
`mu=0` the remaining common constant is zero on the slice.  Thus `P_tau` is a
symplectic isomorphism from `D_tau` onto its reconstructed image.  The universal
Weyl construction induces a *-isomorphism between the corresponding Weyl-CCR
algebras.  An algebraic boundary state can consequently be transported by

```text
omega_Sigma(W(P_tau d))=omega_H(W(d)).
```

using that isomorphism and its inverse.  This constructs a state map only after
`omega_H` is supplied.  It neither
selects `omega_H` nor proves positivity/Hadamard regularity for a preferred
physical state.  In a general algebraic QFT representation a state need not
be a trace-class density matrix; `rho_Sigma` is legitimate only after a
finite-cutoff or type-I representation is separately declared.

## 5. Local semilinear reconstruction

Now take

```text
partial_u partial_v phi+kappa phi+g phi^3=0,
kappa>=0, g>=0.
```

On the closed sup-norm ball `||phi||<=R`, with `M=||G||`, the Volterra map

```text
T(phi)=G-K(kappa phi+g phi^3)
```

is a self-map and contraction whenever

```text
M+U V (kappa R+g R^3)<=R,
L=U V (kappa+3 g R^2)<1.
```

Banach's fixed-point theorem then gives a unique solution in that declared
ball.

With the physical normalization

```text
kappa=mu^2/4,  g=lambda/4,
```

the equation is

```text
phi_tt-phi_xx+mu^2 phi+lambda phi^3=0.
```

If the two compared data maps use the same `kappa,g,R`, preserve the same
radius-`R` ball, and have Lipschitz constant at most the same `L<1`, then

```text
||phi-phi_tilde||<=||G-G_tilde||/(1-L).
```

This is the scope of the displayed data-stability estimate; it is not an
unconditional comparison between arbitrary solutions.  For `H=||G||` and
`R=2H`, the convenient sufficient condition

```text
U V (mu^2/2+3 lambda H^2)<1
```

implies both gates.  Failure of this inequality says only that this contraction
certificate is insufficient; it is not a blow-up or nonexistence theorem.

## 6. Boundary derivation of the toy interior energy flux balance

For smooth fields the usual local current identity is

```text
partial_t e-partial_x(phi_t phi_x)
 =phi_t(phi_tt-phi_xx+mu^2 phi+lambda phi^3),
e=(phi_t^2+phi_x^2+mu^2 phi^2)/2+lambda phi^4/4.
```

At the theorem's `C1` trace regularity the same result follows directly,
without assuming pure `t` or `x` second derivatives, from

```text
partial_v(phi_u^2)+partial_u(mu^2 phi^2/4+lambda phi^4/8)=0,
partial_u(phi_v^2)+partial_v(mu^2 phi^2/4+lambda phi^4/8)=0.
```

These identities require only the continuous mixed derivative supplied by the
Volterra equation.  Integration over the characteristic triangle, with
`0<=2tau<=min(U,V)`, yields

```text
E_tau=int_(-tau)^tau e(tau,x)dx
 =int_0^(2tau) [A'^2+mu^2 A^2/4+lambda A^4/8]du
 +int_0^(2tau) [B'^2+mu^2 B^2/4+lambda B^4/8]dv.
```

Thus the toy model's finite interior slice energy is the cumulative flux from
its two null boundary segments.  Because the interval expands with `tau`,
`E_tau` is not asserted to be constant in `tau`; it is an exact flux balance
from a conserved current.  The formula does not derive a cosmological
high-energy scale, an
equation of state, a temperature, or a cooling history.

## 7. Input-output ledger and the causal-structure circularity gate

Inserted inputs:

- 1+1 Minkowski geometry and Lorentzian signature;
- the null coordinates, causal diamond, and time slicing;
- a real scalar and its linear or semilinear equation;
- `mu`, `lambda`, the domain, and compatible boundary traces;
- an algebraic state `omega_H` when quantum state transport is invoked.

Derived outputs:

- global finite-rectangle linear existence, uniqueness, and stability;
- causal restriction to the relevant boundary segments;
- an explicit classical slice-state map;
- linear symplectic/Weyl algebra transport;
- local semilinear existence, uniqueness, and stability under explicit gates;
- a conserved current and exact boundary-to-slice energy flux balance.

**Causal-structure circularity gate:** Lane H currently uses the very
Lorentz/null/time structure that the full TECT Pre-A programme ultimately
wants to explain.  The result is therefore provisional on a causal background.
Pre-A must either (a) declare that causal structure as fundamental input and
narrow the emergence claim, or (b) derive a pregeometric causal order and show
that this characteristic theorem is its continuum limit.

## 8. Relation to PA-M2 and to gravity

`PA-H1-DNKG4-v0` is a 1+1 fixed-background dynamical model.
`PA-M2-CI8-RS-v0` is a three-dimensional finite-torus static ordering
functional with a separately inserted inertial completion.  They share no
proved reduction, parameter map, energy normalization, dimension-changing
limit, or control history `r(tau)`.  The composition arrow

```text
PA-H1 boundary output -> PA-M2 initial state and r(tau)
```

is open.  The two certificates must not be described as one physical theory
until that arrow is proved.

The characteristic Einstein literature supplies relevant existence theorems
for richer data on intersecting null hypersurfaces, while a complete cone with
a regular vertex and all constraints can also be sufficient.  Therefore the
earlier one-sheet counterexample is scoped only to a generic open null sheet
carrying a scalar trace; it is not a theorem that every single null boundary is
insufficient.  Neither gravitational result constructs the TECT microscopic
boundary algebra or the desired cosmological state.

Primary anchors:

- J. Luk, *On the local existence for the characteristic initial value problem
  in general relativity*, https://arxiv.org/abs/1107.0898 .
- Y. Choquet-Bruhat, P. T. Chrusciel, and J. M. Martin-Garcia, *The Cauchy
  problem on a characteristic cone for the Einstein equations in arbitrary
  dimensions*, https://arxiv.org/abs/1006.4467 .
- T. Hilditch, J. A. Valiente Kroon, and P. Zhao, *Revisiting the
  characteristic initial value problem for the vacuum Einstein field
  equations*, https://arxiv.org/abs/1911.00047 .
- L. Ciambelli, L. Freidel, and R. G. Leigh, *Quantum null geometry and gravity*,
  https://arxiv.org/abs/2407.11132 .
- C. Dappiaggi, V. Moretti, and N. Pinamonti, *Cosmological horizons and
  reconstruction of quantum field theories*, https://arxiv.org/abs/0712.1770 .

## 9. Devil's-advocate review

1. **The theorem assumes the causal structure it is meant to explain.**
   **UPHELD.**  This is the named causal-structure circularity gate.
2. **A scalar double-null toy is not the Einstein characteristic system.**
   **UPHELD.**  Gauge constraints, corner data, regularity, and uniqueness
   modulo diffeomorphism remain open.
3. **Transporting a state is not selecting a physical state.**
   **UPHELD.**  Positivity is inherited from the supplied algebraic state;
   Hadamard or vacuum selection is not derived.
4. **The local semilinear certificate may fail on a large domain even when a
   solution exists.**  **VALID WITH SCOPE.**  The Banach conditions are
   sufficient, not necessary.
5. **The energy flux balance could be mistaken for a cosmic high-energy
   derivation.**  **UPHELD.**  It is only the energy of the inserted toy field
   with inserted parameters and traces.
6. **The boundary theorem and PA-M2 onset are disconnected.**  **UPHELD.**
   Their composition arrow is a primary remaining Pre-A gate.

## 10. Status and next gate

The exact candidate-scope Lane-H result is now stronger than the earlier
massless polynomial repair: it supplies global linear reconstruction and
stability, a causal slice map, linear algebraic-state transport, a conserved
current and exact energy-flux balance, and a gated local nonlinear extension.

Pre-A is not complete.  The next smallest proof target is a non-circular
boundary model that defines or derives its causal order, boundary algebra and
preferred state, and then produces one state/control history that legally
feeds both the ordering and quantum-dynamics lanes.  Gravity, dimensional
emergence, `r(tau)`, and the PA-M2 composition arrow remain open.

## 11. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_double_null_semilinear_reconstruction.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_double_null_semilinear_reconstruction_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_double_null_semilinear_reconstruction_verify.py --self-test
```

The stored primary, independent, and integrated JSON artifacts live under
`claims/C6-SPACETIME-SIGNATURE/runs/` as T0 context only and do not alter the
open C6 claim.
