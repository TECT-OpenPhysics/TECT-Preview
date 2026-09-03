# Pre-A CL8 controller-free common-parent route split

Candidate: `PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-EXACT-DKD-HISTORY-CONJUGACY-BOND-TWIST-AND-ROUTE-NOGOS`  
Task: `T-054`  
Claim context: `C6-SPACETIME-SIGNATURE`  
Authority: claim-nonbearing `T0` classical inserted-1D, balanced-even-`M`,
fixed-regulator D-K-D history-intertwiner certificate

<a id="section-1-verdict-and-proof-boundary"></a>

## 1. Verdict and proof boundary

The inherited nonlinear one-dimensional CL8 D-K-D map has an exact,
controller-free characteristic representation.  It is not necessary to add
the passive controller used by the preceding driven route.  A global linear
change from canonical data to two consecutive history fields conjugates the
full nonlinear D-K-D map to a radius-one Q3 recurrence.  Resolving the two
spacetime parities turns that recurrence into an explicit staggered `A/B`
quad equation whose vertex carries the same sixteen real degrees of freedom
as one canonical CL8 leg.

For every nonzero spatial coupling and nonzero step, every corner of this
quad is recovered by a global polynomial formula.  Consequently every
monotone cut of an open rectangle is related to every other admitted cut by
a sweep-independent global polynomial diffeomorphism.  On the balanced
`M/2` by `M/2` square, periodic endpoint identification removes exactly one
duplicate vertex, so every cut has exactly `M` sixteen-dimensional legs and
meets every spatial residue once.  A discrete symplectic-current divergence
identity supplies the cut two-form and proves that these maps are symplectic
and nondegenerate.  Two alternating checkerboard phases decode successive
history pairs.  Their two parity transfers, including the periodic seam
flip, commute exactly with successive inherited D-K-D steps.

Thus the following gate is closed only in classical, inserted-one-dimensional,
balanced-even-`M`, fixed-regulator D-K-D scope:

```text
PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-DYNAMICS-INTERTWINER
```

Quantum mixed-cut implementation, a common stationary or selected state,
the original three-dimensional Q3LOCK model, regulator compatibility,
continuum/Hadamard control, physical nullness and the remaining Pre-A chain
are not closed.  No claim card or theorem tier changes.

Three alternatives are also separated exactly.  Exact two-site bond flow is
a useful controller-free local parent but develops harmonic caustics and is
not the inherited finite D-K-D map.  Two D-K-D steps repair an interior
adjacent tangent rank but acquire radius-two spectators.  A symmetric
midpoint Q3 quad is not globally single-valued.  These are scoped route
failures, not a no-go theorem against other common parents.

<a id="section-2-model-and-conventions"></a>

## 2. Model and conventions

The selected model remains the explicitly inserted transverse-zero,
per-unit-transverse-area theory, not the original three-dimensional
ST8/Q3LOCK regulator.  Fix

```text
M even, M>=4, L>0, a=L/M, w=a/8, mu=chi*w,
chi>0, c>0, g>0, lambda>0, r real, hbar>0,
delta!=0.
```

At each periodic node `j`,

```text
q_j,p_j in R^8,          p_j=w*Pi_j,
Omega=sum_(j,e) dp_(j,e) wedge dq_(j,e).
```

The eight-species onsite polynomial is

```text
W_Q3(q)
 =sum_e [r*q_e^2/2+g*q_e^4/4]
  +(lambda/4) sum_(e~f in Q3)
       (q_e-q_f)^2*(q_e^2+q_f^2).
```

The periodic Hamiltonian is

```text
H_a(q,p)=sum_j ||p_j||^2/(2*mu)+U_a(q),

U_a(q)=w sum_j [
  c*||q_(j+1)-q_j||^2/(2*a^2)+W_Q3(q_j)
].
```

The one-step map already registered by the common finite-regulator route is

```text
F_delta=D_(delta/2) after K_delta after D_(delta/2),

D_h(q,p)=(q+(h/mu)*p,p),
K_delta(q,p)=(q,p-delta*grad U_a(q)).
```

It is an exact reversible symplectic map and an inserted Floquet dynamics.
It is not the exact autonomous flow of `H_a` and does not in general conserve
`H_a`.

<a id="section-3-exact-history-conjugacy"></a>

## 3. Exact nonlinear history conjugacy

Set

```text
s=delta/(2*mu),
x_minus=q-s*p,
x_plus =q+s*p.
```

For `delta!=0`, this is a global linear bijection with inverse

```text
q=(x_minus+x_plus)/2,
p=(mu/delta)*(x_plus-x_minus).
```

The first half drift in `F_delta` sends `q` exactly to `x_plus`.  The kick
therefore gives

```text
p_prime=(mu/delta)*(x_plus-x_minus)
        -delta*grad U_a(x_plus).
```

The last half drift and the output history transform then give the exact
identity

```text
C_delta F_delta C_delta^(-1)(x_minus,x_plus)
 =(
    x_plus,
    2*x_plus-x_minus-(delta^2/mu)*grad U_a(x_plus)
  ).
```

No linearization, small-field approximation, continuum limit or missing Q3
term occurs in this formula.

The map direction is

```text
C_delta : X_phase -> X_hist.
```

The repository convention is `Omega_phase=sum dp wedge dq`.  Substitution
gives

```text
Omega_hist=(mu/delta) sum dx_plus wedge dx_minus.
C_delta^* Omega_hist=Omega_phase,
(C_delta^(-1))^* Omega_phase=Omega_hist.
```

This sign is load-bearing.  Writing the form as
`(mu/delta) dx_minus wedge dx_plus` would reverse it.  The Jacobian of the
history recurrence is symplectic for `Omega_hist` because the Hessian of
`U_a` is symmetric.

The same recurrence follows from the discrete action with one-step
Lagrangian

```text
L_d(x_n,x_(n+1))
 =mu*||x_(n+1)-x_n||^2/(2*delta)-delta*U_a(x_n).
```

Its discrete Euler-Lagrange equation is exactly the displayed history
recurrence.  This variational identity is structural support; it does not
select `delta` or make the discrete action fundamental physics.

<a id="section-4-node-history-recurrence"></a>

## 4. Exact node recurrence and causal coefficients

Define the dimensionless coefficients

```text
kappa=c*delta^2/(chi*a^2),
beta =delta^2/chi.
```

Since `mu=chi*w`, the history equation at node `j` is exactly

```text
x_(n+1,j)
 =2*(1-kappa)*x_(n,j)
  +kappa*[x_(n,j-1)+x_(n,j+1)]
  -x_(n-1,j)
  -beta*grad W_Q3(x_(n,j)).
```

This is a strict radius-one recurrence per discrete step.  Its four outer
coefficients are `I_8` or `kappa*I_8`; the Q3 nonlinearity is entirely at the
central history field.  Therefore every outer field is algebraically
recoverable when `kappa!=0`, equivalently when `c*delta!=0` in the declared
positive-parameter domain.

At `kappa=1`, or

```text
|delta|=a*sqrt(chi/c),
```

the central linear coefficient vanishes.  This is the familiar CFL-one
alignment of the discrete stencil, not a derivation of physical time,
Lorentzian signature or light speed.  In particular, the exact graph cone is
an inserted property of the selected discrete evolution.

<a id="section-5-staggered-ab-quad"></a>

## 5. The staggered A/B quad is the inherited recurrence

On the spatial universal cover define

```text
A_(i,j)=x_(i+j,   i-j),
B_(i,j)=x_(i+j+1, i-j).
```

Thus `(A_(i,j),B_(i,j))` is one complete sixteen-dimensional history leg:
two consecutive eight-field values at one spatial site.  `A` and `B` are not
ancillas; they are precisely the two history slices already present in
`C_delta`.

For one coarse cell with corners `SW,NW,SE,NE`, the history recurrence first
at the `B_SW`-centred star and then at the `A_NE`-centred star gives

```text
A_NE
 =kappa*(A_NW+A_SE)-A_SW
  +2*(1-kappa)*B_SW-beta*grad W_Q3(B_SW),

B_NE
 =kappa*(B_NW+B_SE)-B_SW
  +2*(1-kappa)*A_NE-beta*grad W_Q3(A_NE).
```

These are exact identities in the full eight-species Q3 theory.  They are
not the separate explicit or midpoint light-cone proposals considered
later.

<a id="section-6-global-corner-inverses"></a>

## 6. Global corner inverses and cross determinants

Given `NW,SE,NE`, recover `SW` without an implicit equation.  The second quad
equation first gives

```text
B_SW
 =kappa*(B_NW+B_SE)
  +2*(1-kappa)*A_NE-beta*grad W_Q3(A_NE)-B_NE.
```

With this value known, the first equation gives

```text
A_SW
 =kappa*(A_NW+A_SE)
  +2*(1-kappa)*B_SW-beta*grad W_Q3(B_SW)-A_NE.
```

Given `SW,SE,NE`, recover `NW` by

```text
A_NW
 =[A_NE-kappa*A_SE+A_SW
   -2*(1-kappa)*B_SW+beta*grad W_Q3(B_SW)]/kappa,

B_NW
 =[B_NE-kappa*B_SE+B_SW
   -2*(1-kappa)*A_NE+beta*grad W_Q3(A_NE)]/kappa.
```

The `SE` formulas are identical after exchanging `NW` and `SE`.  Every
orientation is therefore a global polynomial map over the fixed nonzero
constant `kappa`; no field-dependent denominator, caustic or branch occurs.

Holding `NW,SE` fixed, define

```text
F=2*(1-kappa)*I_8-beta*Hess W_Q3(B_SW),
G=2*(1-kappa)*I_8-beta*Hess W_Q3(A_NE).
```

Then

```text
d Z_NE / d Z_SW
 = [ -I       F       ]
   [ -G      -I+G*F   ].
```

It factors into two symmetric symplectic shears and a central minus identity.
Consequently

```text
det(d Z_NE/d Z_SW)=1.
```

The `NW` and `SE` projection blocks are triangular with diagonal
`kappa*I_8`, so

```text
det(d Z_NE/d Z_NW)=det(d Z_NE/d Z_SE)=kappa^16.
```

This is the honest resolution of the earlier rank-eight q-only microgate
obstruction.  The phase information was not manufactured by a controller;
the same sixteen canonical degrees of freedom were reorganized as two
staggered history fields.

<a id="section-7-open-rectangle-all-cuts"></a>

## 7. Open-rectangle all-cut theorem

Fix an `m` by `n` coarse rectangle.  Supply `A/B` data on row zero and column
zero, counting the common corner once.  There are `m+n+1` complete history
legs.  At cell `(i,j)`, the `SW,NW,SE` values have already been assigned, so
the two displayed quad equations determine `NE` globally.

Induction on `i+j` proves existence and uniqueness of every vertex.  Ready
incomparable cells only assign different target vertices, hence all
topological sweeps agree.  A monotone path from `NW` to `SE` has `m+n+1`
vertices, and there are

```text
binomial(m+n,m)
```

such paths.  A local path flip replaces `SW` by `NE` while retaining `NW`
and `SE`.  The global `SW<->NE` formulas make the flip a global polynomial
diffeomorphism.  Composing flips proves that the input-to-every-cut map is a
global polynomial diffeomorphism, with a polynomial inverse.

This is a classical field-value theorem.  It does not by itself make a
nonlinear mixed cut into a tensor-factor unitary in quantum theory.

<a id="section-8-balanced-periodic-seam"></a>

## 8. Balanced periodic seam and exact dimension

Now take `m=n=M/2`.  In the universal cover the `NW` endpoint `(0,m)` and
`SE` endpoint `(m,0)` both have history time `m`, while their spatial
coordinates are `-m` and `+m`.  These differ by `M`, so the periodic ring
identifies exactly these two endpoint values.

Every monotone path has `M+1` vertices before this identification and exactly
`M` independent vertices afterwards.  Along either an east or a south step,
the spatial coordinate `i-j` increases by one.  Hence a closed path meets
every spatial residue modulo `M` exactly once.  Its real dimension is

```text
16M,
```

exactly the dimension of the canonical periodic phase space.  There is no
unused complement, quotient radical or ancilla.

Let `E_m={ell:ell=m mod 2}` and write

```text
Z_(n,ell)=(x_(n,ell),x_(n+1,ell)).
```

There are two alternating checkerboard phases:

```text
P_m^- = Z_(m,ell)   on E_m,     Z_(m-1,ell) on E_m^c,
P_m^+ = Z_(m,ell)   on E_m,     Z_(m+1,ell) on E_m^c.
```

Thus `P_m^+=P_(m+1)^-` as a history-edge set.  The minus cut supplies all
of `x_m`; the plus cut supplies all of `x_(m+1)`.  The reversible history
equation reconstructs the missing earlier parity.  For example, on the minus
cut,

```text
x_(m-1,j)
 =2*(1-kappa)*x_(m,j)
  +kappa*[x_(m,j-1)+x_(m,j+1)]
  -x_(m+1,j)-beta*grad W_Q3(x_(m,j)).
```

Call the two polynomial decoders

```text
R_m^-:P_m^-->(x_(m-1),x_m),
R_m^+:P_m^+->(x_m,x_(m+1)).
```

Both are global bijections.  Applying `C_delta^(-1)` defines `J_m^-` and
`J_m^+` to the canonical periodic phase.  Translating the minus path by
`(1,1)` gives `P_(m+2)^-`, which decodes `(x_(m+1),x_(m+2))`.

Unbalanced aspect ratios would identify the spatial endpoints with a time
shift; odd `M` does not close the two parity pattern.  Neither is included in
this theorem.

<a id="section-9-discrete-symplectic-current"></a>

## 9. Discrete symplectic current and cut form

Let two tangent solutions be represented by exterior differentials.  Define

```text
K_t(n,j)
 =(mu/delta)*dx_(n+1,j) wedge dx_(n,j),

K_x(n,j)
 =(mu*kappa/delta)*dx_(n,j+1) wedge dx_(n,j)
 =(w*c*delta/a^2)*dx_(n,j+1) wedge dx_(n,j).
```

Wedge the linearized history equation with `dx_(n,j)`.  The central scalar
term vanishes, and the full Q3 Hessian contribution vanishes because the
Hessian is symmetric.  The remaining terms give the exact local identity

```text
K_t(n,j)-K_t(n-1,j)
-K_x(n,j)+K_x(n,j-1)=0.
```

For a closed monotone cut carrying `Z_(n_j,j)` with
`Delta_j=n_(j+1)-n_j` equal to `+1` or `-1`, the oriented flux is

```text
Omega_C
 =sum_j K_t(n_j,j)
  +sum_(Delta_j=+1) K_x(n_j+1,j)
  -sum_(Delta_j=-1) K_x(n_j,j).
```

Raising one valley `n_j=a` to `a+2` changes this expression by the sum of
the two local divergences at `(a+1,j)` and `(a+2,j)`, hence by zero.  Every
monotone cut is connected by such flips, so the formula supplies the exact
cut two-form rather than an assumed product of leg forms.  On a consecutive-
time Cauchy cut it is precisely `Omega_hist`.  The periodic spatial currents
cancel pairwise, proving conservation of the total temporal symplectic flux.

Each cut is globally diffeomorphic to the checkerboard reference cut, which
is globally bijective with the nondegenerate canonical phase.  Pulling back
`Omega_hist` therefore proves that every declared cut form is nondegenerate;
the flux telescope shows that every cut map is symplectic.  This avoids the
incorrect shortcut of assuming a path-independent product of isolated leg
forms when spatial connector currents are present.

<a id="section-10-commuting-dynamics-diagram"></a>

## 10. Exact classical boundary-Cauchy diagram

Let `X_P` be the `16M`-dimensional data space on a balanced periodic monotone
cut `P`, with its current-flux form.  Let `B_(P->Q)` be the unique reversible
quad sweep.  The first parity transfer simultaneously flips every site in
`E_m^c`:

```text
Z_(m+1,j)
 =Q_quad(Z_(m-1,j);Z_(m,j-1),Z_(m,j+1)).
```

The targets are nonadjacent, so the flips commute and send `P_m^-` to
`P_m^+`.  The complementary parity transfer flips every site in `E_m`:

```text
Z_(m+2,j)
 =Q_quad(Z_(m,j);Z_(m+1,j-1),Z_(m+1,j+1)),
```

and sends `P_m^+` to `P_(m+2)^-`.  One of these cells crosses the periodic
seam; the site labels are taken modulo `M`.  The decoders of Section 8 give
the two exact identities

```text
J_m^+ after B_m^-=F_delta after J_m^-,
J_(m+2)^- after B_m^+=F_delta after J_m^+.
```

These equations repair a crucial indexing point: one fixed checkerboard
reference cannot describe both coordinate re-slicing and physical time
advance.  For each integer `n`, choose `P_n=P_n^-`, decoding
`(x_(n-1),x_n)`.  For an admitted cut `C` evaluated at time `n`, define

```text
J_C^[n]
 =C_delta^(-1) after R_n after B_(C->P_n).
```

Within one time label,

```text
J_D^[n] after B_(C->D)=J_C^[n].
```

For a genuine one-step transfer, compatibility of the two quad sweeps gives

```text
J_D^[n+1] after B_(C->D)=F_delta after J_C^[n].
```

All maps are explicit global polynomial diffeomorphisms in field values;
there is no image constraint or complement.  The scope is nevertheless only
the inserted one-dimensional, balanced-even-`M`, fixed-regulator D-K-D
model.  This is not an autonomous-`H_a` flow theorem, an odd or unbalanced
seam theorem, or a cutoff-uniform statement.

The same diagram supplies an exact shared energy ledger.  On every admitted
cut `C` at time label `n`, define

```text
E_C^[n]=H_a after J_C^[n].
```

For two cuts representing the same history state at label `n`,

```text
E_D^[n] after B_(C->D)=E_C^[n].
```

For a physical one-step transfer,

```text
E_D^[n+1] after B_(C->D)-E_C^[n]
 =(H_a after F_delta-H_a) after J_C^[n].
```

The right side is the exact finite-D-K-D energy defect; it is not asserted
to vanish.  Similarly, every supplied measure obeys the pushforward identity

```text
(J_D^[n+1])_* (B_(C->D))_* nu_C
 =(F_delta)_* (J_C^[n])_* nu_C.
```

This is transport, not stationarity or selection.  The ledger is not a
positive locally cut-additive invariant or a physical reference energy.  No
common stationary state, physical energy zero, vacuum, or below-empty-space
comparison follows.

<a id="section-11-quantum-boundary"></a>

## 11. What is and is not quantum-exact

At one site,

```text
X_minus=Q-(delta/(2*mu))*P,
X_plus =Q+(delta/(2*mu))*P,

[X_minus,X_plus]=i*hbar*delta/mu.
```

Thus `Q_h=X_minus` and `P_h=(mu/delta)*X_plus` obey the canonical CCR.  The
linear history change is metaplectic, and the known D-K-D unitary can be
conjugated on `B(H)` in the ordinary time direction.  Forward density
transport is exact.

The nonlinear mixed-cut maps are not thereby proved to be tensor-factor
unitaries or automorphisms of the concrete nonlinear Weyl C-star algebra.
There is no demonstrated quantum analogue of the classical current-flux cut
form, no same-representation cut CCR diagram, and no compatible stationary
state family.  The next gate is therefore

```text
PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY.
```

<a id="section-12-exact-bond-flow-route"></a>

## 12. Exact bond-flow fallback and its caustic

The inherited Hamiltonian also has the exact bond partition

```text
V_j
 =w*[c*||q_(j+1)-q_j||^2/(2*a^2)
     +(W_Q3(q_j)+W_Q3(q_(j+1)))/2],

h_j=(||p_j||^2+||p_(j+1)||^2)/(4*mu)+V_j,

sum_j h_j=H_a.
```

Because `g>0`, each `h_j` is coercive up to a finite lower shift; its exact
Hamiltonian flow is complete and symplectic.  With

```text
k=w*c/a^2,        m_b=2*mu,
```

the spatial cross Hessian is `-k*I_8` everywhere.  The opposite-leg
determinant therefore has the uniform-on-compacts short-time jet

```text
det C_opp(z,t)
 =[k^2/(12*m_b^2)]^8*t^32+O_z(t^33)
 =[k^2/(48*mu^2)]^8*t^32+O_z(t^33).
```

Every fixed compact phase set consequently has a sufficiently small nonzero
time interval on which both opposite-leg blocks are invertible.  This is
only a local chart theorem.

At the zero Q3 equilibrium, one species has normal-mode flow matrices

```text
R_omega(t)
 =[ cos(omega*t)          sin(omega*t)/(m_b*omega) ]
  [ -m_b*omega*sin(omega*t)       cos(omega*t)     ].
```

The opposite-site block is

```text
B(t)=[R_(omega_plus)(t)-R_(omega_minus)(t)]/2,
```

with

```text
det B(t)
 =(1/4)*[
   2-2*cos(omega_plus*t)*cos(omega_minus*t)
   -(omega_plus/omega_minus+omega_minus/omega_plus)
      *sin(omega_plus*t)*sin(omega_minus*t)
 ].
```

Choose the admissible relation

```text
r=4*c/(3*a^2).
```

Then `omega_minus=2*omega_plus`.  At
`t=2*pi/omega_plus`, both rotations are the identity and `B(t)=0`.
Therefore a global all-field, all-time exact-bond-flow sideways theorem is
false.  This registers

```text
NG-2026-08-04-PRE-A-CP1-CL8-BOND-FLOW-GLOBAL-ALL-TIME-SIDEWAYS.
```

Compact nonresonant charts and forward temporal bond flow survive.

<a id="section-13-dkd2-macro-route"></a>

## 13. Two D-K-D steps repair interior rank but add spectators

At a static tangent point let `K=Hess U_a`.  One D-K-D step has blocks

```text
A=I-delta^2*K/(2*mu),
B=delta*I/mu-delta^3*K/(4*mu^2),
C=-delta*K.
```

For adjacent sites set

```text
u=K_WS=-k*I_8,       v=(K^2)_WS.
```

The cross block of the square has subblocks

```text
D=-2*delta^2*u/mu+delta^4*v/(2*mu^2),
P=-3*delta^3*u/(2*mu^2)+delta^5*v/(4*mu^3),
Q=-2*delta*u+delta^3*v/mu.
```

Since `u` is scalar, it commutes with `v`, and exact cancellation gives

```text
D^2-P*Q=delta^4*u^2/mu^2,

det C_opp(F_delta^2)
 =[delta^4*k^2/mu^2]^8 !=0.
```

Thus the one-step rank-eight result must not be overextended to every
macroblock.  However the distance-two position-to-momentum derivative is

```text
delta^3*k^2/mu !=0.
```

The output therefore depends on radius-two spectators and cannot be
identified directly with a two-input/two-output same-sixteen-dimensional-leg
vertex.  This registers only

```text
NG-2026-08-04-PRE-A-CP1-CL8-DKD2-DIRECT-TWO-LEG-LOCALIZATION.
```

Halo, ancilla, larger-leg, quotient and nonlocal macrocell constructions
remain possible.

<a id="section-14-light-cone-quad-routes"></a>

## 14. Separate light-cone quad routes

The explicit configuration-only proposal

```text
q_11=q_10+q_01-q_00-alpha*grad W_Q3(q_00)
```

is globally forward-solvable but carries only `q in R^8` on a null leg.  It
does not supply an independent canonical `(q,p) in R^16` leg or an exact
intertwiner to the finite `U_a` dynamics.  It remains a separate candidate.

The symmetric midpoint proposal

```text
q_11-q_10-q_01+q_00
 =-alpha*grad W_Q3((q_00+q_10+q_01+q_11)/4)
```

is not globally single-valued.  Set three corners to zero and
`q_11=y*1_8`.  The Q3 locking term vanishes and the equation reduces to

```text
y*[1+alpha*r/4+alpha*g*y^2/64]=0.
```

For `r<0`, `alpha=-4/r` is singular.  For `alpha>-4/r`, the zero root and two
nonzero real roots coexist.  This registers

```text
NG-2026-08-04-PRE-A-CP1-CL8-MIDPOINT-QUAD-GLOBAL-UNIQUENESS.
```

Local implicit branches and the exact derived staggered history quad are not
refuted.

<a id="section-15-prior-art-boundary"></a>

## 15. Prior-art boundary

Stormer-Verlet history variables, discrete variational recurrences,
multisymplectic currents, quad equations, twist maps, Hamiltonian bond
splittings and Lie-Trotter products are established mathematics.  No general
theorem or world-first claim is made here.

The repository-specific contribution is narrower: it carries the exact
inserted-one-dimensional `w=a/8`, `mu=chi*w`, full Q3 gradient and repository
`dp wedge dq` sign through the canonical/history conjugacy; derives the
staggered `A/B` quad from that same inherited D-K-D map; audits its global
corner inverses, balanced seam, dimension and current flux; and separates it
from three tempting but inequivalent routes.

<a id="section-16-executable-verification"></a>

## 16. Executable verification

Primary audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe \
  codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split.py
```

Independent standard-library/Fraction audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe \
  codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split_independent.py
```

Integrated publication audit:

```text
E:\Dev\TECT.venv\Scripts\python.exe \
  codes/foundations/pre_a_cp1_cl8_controller_free_common_parent_route_split_verify.py
```

The primary implementation differentiates the symbolic full Q3 potential and
checks the implemented gradient, Hessian action and Hessian symmetry before
running automatic Lie-series, matrix and rational fixtures.  The independent
implementation imports neither the primary script nor a symbolic/array
package.  It reconstructs the Q3 gradient and Hessian action from exact
five-point `Fraction` differences of the potential, rejects sign/factor/
omitted-edge mutants, and separately rebuilds the D-K-D/history maps, quad
inverses, nonlinear `1x5` rectangles, both checkerboard parity transfers,
every balanced monotone-cut flux and the harmonic caustic.  Both use nonzero
positive-step `F0` and hostile negative-step `F1`.  In particular,

```text
F0: s=1/2,  mu/delta=1,    kappa=3/64,  beta=1/8,
F1: s=-3/5, mu/delta=-5/6, kappa=7/300, beta=27/400.
```

The sign change in `mu/delta` is an explicit hostile check of the history
symplectic orientation.

<a id="section-17-adversarial-review"></a>

## 17. Adversarial review

1. **Objection: the A/B fields secretly double the phase space.**  
   **DISMISSED.**  One A/B vertex is exactly two consecutive eight-field
   histories.  `C_delta` is a bijection between these sixteen values and one
   sixteen-dimensional canonical leg.  The balanced seam has exactly `M`
   independent vertices after one endpoint identification.

2. **Objection: local cross determinant one is insufficient for a cut
   symplectic theorem because neighboring vertices are parameters.**  
   **VALID WITH MITIGATION.**  The proof does not infer the global cut form
   from the isolated block.  It derives the full discrete current divergence,
   telescopes it over the region, and proves nondegeneracy by the explicit
   checkerboard-to-canonical bijection.

3. **Objection: the periodic seam may hide a time monodromy.**  
   **VALID WITH SCOPE RESTRICTION.**  Only the balanced square is asserted.
   Its endpoints have the same history time and spatial coordinates differing
   by exactly `M`.  Unbalanced and time-shift seams stay open.

4. **Objection: one fixed checkerboard decoder cannot both re-slice data and
   advance the physical time.**  
   **VALID AND REPAIRED.**  Section 10 uses the distinct `P_m^-` and `P_m^+`
   decoders, proves both parity transitions including the seam cell, and uses
   time-indexed `J_C^[n]` for arbitrary cuts.  The earlier fixed-reference
   formula is not retained.

5. **Objection: the cut diagram silently reuses an energy ledger from the
   controller-driven route.**  
   **VALID AND REPAIRED.**  Section 10 defines
   `E_C^[n]=H_a after J_C^[n]` afresh and
   records the exact finite-D-K-D defect.  It claims neither conservation nor
   a physical energy reference.

6. **Objection: exact classical re-slicing automatically gives a quantum
   dual-unitary circuit.**  
   **UPHELD AGAINST THAT EXTENSION.**  Only ordinary-time metaplectic history
   conjugation and `B(H)` transport are retained.  Mixed-cut CCR, tensor
   factorization and state compatibility are the next gate.

7. **Objection: `kappa=1` derives the physical light speed.**  
   **UPHELD AGAINST THAT INTERPRETATION.**  It is a chosen relation among the
   regulator step, spacing, inertia and stiffness.  No physical clock,
   Lorentzian limit or cutoff-uniform stability theorem is supplied.

8. **Objection: closing this fixed-regulator gate advances C6 or Pre-A.**  
   **UPHELD AGAINST THAT EXTENSION.**  C6 remains `T1 / ACTIVE /
   CONDITIONAL` with `C6-BCC-PREMISE-BLOCKED`.  The original 3D parent,
   quantum state, physical reference, continuum and emergence links are
   absent.

<a id="section-18-gate-and-pre-a-status"></a>

## 18. Gate and Pre-A status

Closed here:

```text
PA-CP1-CL8-EXACT-NONLINEAR-DKD-HISTORY-FIELD-CONJUGACY
PA-CP1-CL8-EXACT-DKD-HISTORY-SYMPLECTIC-FORM-AND-DIMENSION
PA-CP1-CL8-EXACT-DKD-HISTORY-RADIUS-ONE-Q3-RECURRENCE
PA-CP1-CL8-EXACT-DKD-STAGGERED-AB-GLOBAL-CORNER-INVERSES
PA-CP1-CL8-EXACT-DKD-STAGGERED-AB-OPEN-RECTANGLE-ALL-CUT-DIFFEOMORPHISM
PA-CP1-CL8-EXACT-DKD-HISTORY-DISCRETE-SYMPLECTIC-CURRENT
PA-CP1-CL8-EXACT-DKD-HISTORY-BALANCED-PERIODIC-SEAM-AND-DIMENSION
PA-CP1-CL8-CLASSICAL-INSERTED-1D-BALANCED-EVEN-M-TWO-PARITY-DKD-DIAGRAM
PA-CP1-CL8-EXACT-TRANSPORTED-CUT-ENERGY-DEFECT-LEDGER
```

Still open:

```text
PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-AND-STATE-COMPATIBILITY
PA-CP1-CL8-COMMON-POSITIVE-INVARIANT-AND-STATIONARY-STATE
PA-CP1-CL8-ONE-DIMENSIONAL-TO-THREE-DIMENSIONAL-Q3-PARENT
PA-CP1-CL8-REGULATOR-COMPATIBLE-BOUNDARY-STATE-FAMILY
PA-CP1-CL8-CONTINUUM-STATE-AND-HADAMARD-LIMIT
PA-CP1-COMMON-PARENT-PHYSICAL-STATE-AND-REFERENCE
```

The fixed-regulator classical component of the prospective N2 link is now
exact.  N2 itself is not closed because the quantum, regulator-uniform and
physical-characteristic meanings remain absent.  `C0`, `N1`--`N5`, `CP1`
and Pre-A remain open.
