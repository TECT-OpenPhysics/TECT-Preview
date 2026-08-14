# R-167 v4.0 certificate: mesoscopic source-ground orbit-smear transfer

Date: 2026-08-14  
Task: T-054  
Exploration: EXP-000844  
Claim-bearing: false (T0 route work)  
PDF: none issued

## 1. Exact scoped result

This certificate closes only
`PA-CP1-ST8-Q3LOCK-MESOSCOPIC-SOURCE-EXACT-GROUND-RESIDUAL-CLOSURE-AND-ZERO-SOURCE-ORBIT-SMEAR-GROUND-PAIR`.

For the exact fixed-spacing positive-`lambda` ST8/Q3LOCK Hamiltonians, choose
finite periodic energy sources in the mesoscopic window

```text
h_L V^2 -> infinity,                 h_L V -> 0,             (1.1)
```

where `V=L^3`. The concrete choice `h_L=h_* V^(-3/2)` lies in this
window. The exact finite-volume ground vectors of
`H_L(+/-h_L)=H_L(0)-(+/-h_L)S_L` retain opposite nonzero order, while their
total zero-source excess energy tends to zero.

The already constructed R-167 v1.6 zero-source categorical orbit-smear
system supplies one target algebra, one point-norm `C0` action and exact
finite-volume representations. A bandlimited graph core makes the represented
zero-source generator defect identically zero. Source-uniform coercivity,
Arveson energy transfer and the mesoscopic upper condition in (1.1) then prove
the R-167 v3.9 combined scalar residual tends to zero on that core. Every
joint weak-star cluster pair is consequently a parity-related pair of
algebraic ground states of the same zero-source categorical action. One fixed
rational sine-smear separates the pair.

This is the first exact-Q3 instantiation of the v3.9 residual theorem, but it
is not a spatial thermodynamic-dynamics theorem. The cluster states use a new
diagonal source-volume limit. They are not identified with the EXP-000790
iterated fixed-source tangent candidates, the EXP-000781 fixed-temperature
DLR tangents, or the v3.8 fixed-temperature source-family KMS states.

## 2. Inherited exact Q3 ground-order input

Use the dyadic periodic cubes of EXP-000789. Put

```text
V=L^3,
S_L=sum_y Q_y,
Q_y=8^(-1/2) sum_(e=1)^8 q_(y,e),
K_L=H_L(0)-E_(0,L)>=0.                                    (2.1)
```

The exact energy-source convention of EXP-000790 is

```text
H_L(h)=H_L(0)-h S_L.                                      (2.2)
```

Let `Omega_L` be the unique even zero-source ground vector and define

```text
m_L^2=<Omega_L,S_L^2 Omega_L>/V^2,
Phi_L=S_L Omega_L/||S_L Omega_L||,
Psi_L^sigma=(Omega_L+sigma Phi_L)/sqrt(2),
sigma in {-1,+1}.                                         (2.3)
```

EXP-000789 proves

```text
liminf_L m_L^2>=rho_*>0,
<Psi_L^sigma,S_L Psi_L^sigma>=sigma V m_L,                 (2.4)
```

and the total zero-source energy excess

```text
epsilon_L
 :=<Psi_L^sigma,K_L Psi_L^sigma>
 <=hbar^2/(4 chi V m_L^2).                                 (2.5)
```

After deleting a finite prefix,

```text
m_L^2>=rho_*/2,
m_0:=sqrt(rho_*/2),
C_e:=hbar^2/(2 chi rho_*),
m_L>=m_0,
epsilon_L<=C_e/V.                                         (2.6)
```

The factor `1/8` in the EXP-000790 source-cusp formulas belongs only to its
fine-oscillator energy-density normalization `E/(8V)`. It does not enter the
total-energy identities (2.5) or the source comparison below.

## 3. Exact nonzero-source ground vectors

Fix a compact source interval `|h|<=h_0`. EXP-000780 gives a closed,
semibounded real polynomial Schrodinger form with compact resolvent for every
such source. The added source is linear, so the quartic potential remains
confining. The finite-dimensional configuration space is connected and the
Feynman--Kac kernel is strictly positive. Hence the heat semigroup is
positivity improving and the lowest eigenvalue is simple.

For `h>0`, write `phi_L^sigma(h)` for the unique normalized strictly positive
ground of

```text
H_L(sigma h)=H_L(0)-sigma h S_L.                           (3.1)
```

The source preserves periodic translations. Uniqueness and strict positivity
therefore make `phi_L^sigma(h)` translation invariant. If `P` is global
field inversion, then

```text
P H_L(h) P=H_L(-h).                                       (3.2)
```

With positive phases chosen for both ground vectors,

```text
P phi_L^+(h)=phi_L^-(h),
E_L(h)=E_L(-h).                                           (3.3)
```

The even zero-source ground is a trial vector and has zero source
expectation. Thus

```text
E_L(sigma h)<=E_(0,L).                                    (3.4)
```

This source-ground uniqueness is a direct extension of the EXP-000789
positivity-improving argument; it is written here because EXP-000789 stated
the argument explicitly only at zero source.

## 4. The mesoscopic source window

Choose a positive sequence `h_L->0`. Discard a finite prefix so that
`0<h_L<=h_0`, as required by the source-uniform coercivity interval, and
abbreviate

```text
phi_L^sigma=phi_L^sigma(h_L),
s_L^sigma=<phi_L^sigma,S_L phi_L^sigma>,
eta_L^sigma=<phi_L^sigma,K_L phi_L^sigma>.                 (4.1)
```

The exact source-ground energy is

```text
E_L(sigma h_L)=E_(0,L)+eta_L^sigma-sigma h_L s_L^sigma.
                                                                    (4.2)
```

Use `Psi_L^sigma` from (2.3) as a trial vector for the same source
Hamiltonian. Its expectation is

```text
E_(0,L)+epsilon_L-h_L V m_L.                              (4.3)
```

The variational principle gives the sign-sensitive exact inequality

```text
eta_L^sigma+h_L(V m_L-sigma s_L^sigma)
 <=epsilon_L<=C_e/V.                                      (4.4)
```

Since `eta_L^sigma>=0`,

```text
sigma s_L^sigma/V
 >=m_L-C_e/(h_L V^2).                                    (4.5)
```

Section 5 proves one constant `C_S` with
`|s_L^sigma|<=C_S V`. Dropping the favorable term `-h_L V m_L` in (4.4)
then gives

```text
eta_L^sigma<=C_e/V+C_S h_L V.                             (4.6)
```

Consequently the sufficient window is exactly

```text
h_L V^2->infinity              for retained order,
h_L V->0                       for eta_L^sigma->0
                                and residual closure.      (4.7)
```

It is nonempty. For the canonical choice

```text
h_L=h_* V^(-3/2),             h_*>0,                       (4.8)
```

equations (4.5)--(4.6) become

```text
sigma s_L^sigma/V
 >=m_0-(C_e/h_*)V^(-1/2),                                 (4.9)

eta_L^sigma
 <=C_e V^(-1)+h_* C_S V^(-1/2)->0.                       (4.10)
```

Put

```text
m_*:=m_0/2=sqrt(rho_*/8).                                 (4.11)
```

For all sufficiently large `L`, (4.9) gives

```text
sigma s_L^sigma/V>=m_*.                                  (4.12)
```

Parity from (3.3) gives `s_L^-=-s_L^+` and
`eta_L^-=eta_L^+` exactly.

## 5. Source-uniform coercivity and the collective form bound

Fix

```text
0<gamma<g/32,
a>0,                                                       (5.1)
```

and define the finite EXP-000792 constant

```text
C_gamma
 =max_(rho>=0)[h_0 rho-(r/2)rho^2-(g/32-gamma)rho^4].     (5.2)
```

For every declared finite volume and `|h|<=h_0`, EXP-000792 proves the
quadratic-form inequality

```text
K_(L,h):=H_L(h)+C_gamma V
 >=sum_x[p_x^2/(2chi)+gamma |q_x|^4]
   +(c/2)sum_<xy>|q_x-q_y|^2.                             (5.3)
```

It also proves, for every set `X`,

```text
sum_(x in X)|q_x|^2
 <=a K_(L,h)+|X|/(4 a gamma).                             (5.4)
```

The centered Gaussian trial of EXP-000780 has zero source expectation and
gives one constant `A_s` such that

```text
E_L(h)<=E_(0,L)<=A_s V.                                   (5.5)
```

Define, rather than paste,

```text
B_a:=a(A_s+C_gamma)+(4 a gamma)^(-1).                     (5.6)
```

At zero source, `K_(L,0)=K_L+E_(0,L)+C_gamma V`. Put
`X=Lambda_L` in (5.4), use (5.5), and use

```text
S_L^2<=(V sum_x Q_x^2)<=(V sum_x |q_x|^2).                (5.7)
```

This proves the exact target quadratic-form inequality

```text
S_L^2<=a V K_L+B_a V^2.                                  (5.8)
```

Apply (5.4) directly in the source ground. Equations (3.4) and (5.5) give

```text
<phi_L^sigma,sum_x|q_x|^2 phi_L^sigma>
 <=B_a V.                                                 (5.9)
```

Together with (5.7),

```text
<S_L^2>_(phi_L^sigma)<=B_a V^2,
|s_L^sigma|/V<=C_S:=sqrt(B_a).                            (5.10)
```

This supplies the constant used in (4.6). No extra additive constant is
needed.

From (5.3), (3.4), (5.5), translation invariance and
`|Q_0|<=|q_0|`,

```text
<|Q_0|^4>_(phi_L^sigma)
 <=C_4:=(A_s+C_gamma)/gamma.                              (5.11)
```

The same estimates give the local kinetic-plus-quartic tightness needed for
separate locally normal time-zero subsequences. The algebraic ground-state
proof below does not identify those time-zero limits with the EXP-000790
iterated tangent states.

## 6. The common zero-source categorical target and graph core

R-167 v1.6 starts from finite-support rational configuration labels `xi`.
For `f in L1(R)`, its finite zero-source representation is

```text
pi_L^0(A_(xi,f))
 =int_R f(t) alpha_t^(L,0)(W_(L,xi)) dt,                  (6.1)
```

and the universal norm is

```text
||A||_H=sup_L ||pi_L^0(A)||.                              (6.2)
```

After quotient and completion this gives the unital separable C-star algebra
`A_H^0`. Kernel translation defines one point-norm `C0` group `theta`, with
exact equivariance

```text
pi_L^0(theta_t A)=alpha_t^(L,0)(pi_L^0(A)).               (6.3)
```

Let `delta_H` be the closed generator of `theta`. Define `D_bl` to be the
unital star-algebra generated by

```text
theta_g(B):=int_R g(t)theta_t(B)dt,                        (6.4)
```

where `B in A_H^0`, `g` is Schwartz and `hat g` has compact support.
Arveson bandwidths add under products and change sign under star, so every
element of `D_bl` has compact Arveson spectrum and lies in
`Dom(delta_H)`.

Choose a real even Schwartz approximate identity `g_j` whose Fourier
transform has compact support. For every `A in Dom(delta_H)`,

```text
theta_(g_j)(A)->A,
delta_H theta_(g_j)(A)=theta_(g_j)(delta_H A)->delta_H A. (6.5)
```

Thus `D_bl` is dense in the graph norm and is a unital star graph core for
`delta_H`.

Differentiate (6.3) in norm. For every `A in D_bl`, with
`A_L=pi_L^0(A)`,

```text
delta_L^0(A_L)
 :=(i/hbar)[H_L(0),A_L]
 =pi_L^0(delta_H A)                                      (6.6)
```

in the bounded generator sense. The v3.9 target-generator defect is
therefore exactly

```text
d_L(A)=delta_L^0(A_L)-pi_L^0(delta_H A)=0.                (6.7)
```

Finite zero-source parity preserves the universal norm and induces

```text
gamma(A_(xi,f))=A_(-xi,f),
gamma theta_t=theta_t gamma.                              (6.8)
```

If

```text
omega_L^sigma(A)
 :=<phi_L^sigma,pi_L^0(A)phi_L^sigma>,                    (6.9)
```

then (3.3) and (6.8) give

```text
omega_L^-=omega_L^+ o gamma.                              (6.10)
```

## 7. Arveson energy transfer and the represented domains

Fix `A in D_bl` and choose `R_A<infinity` with

```text
Sp_theta(A) subset [-R_A,R_A].                            (7.1)
```

Exact equivariance transfers this inclusion to `A_L`. With energy measured
by `K_L`, the standard Arveson energy-transfer relation gives, for
`x>=hbar R_A`,

```text
P_[x,infinity)(K_L) A_L
 =P_[x,infinity)(K_L) A_L
  P_[x-hbar R_A,infinity)(K_L).                           (7.2)
```

For every normalized `phi` with finite
`eta=<phi,K_L phi>`, spectral-tail integration yields

```text
<A_L phi,K_L A_L phi>
 =int_0^infinity ||P_(x,infinity)(K_L)A_L phi||^2 dx
 <=||A||_H^2(eta+hbar R_A).                               (7.3)
```

Apply the same argument to `A^*` and finite products. Hence `A_L`, `A_L^*`
and their products preserve `Dom(K_L^(1/2))`.

Equation (5.8) gives

```text
||S_L psi||^2
 <=a V <psi,K_L psi>+B_a V^2||psi||^2.                   (7.4)
```

Therefore `S_L` is bounded from the zero-source form domain to the Hilbert
space. Its linear form is infinitesimally `K_L`-form bounded, so the
zero-source and `+/-h_L` source Hamiltonians share the same quadratic-form
domain. Equations (7.3)--(7.4) place `phi_L^sigma`, `A_L phi_L^sigma`, and
all vectors used below in every displayed pairing.

The notation

```text
<phi,A_L^*[S_L,A_L]phi>
 :=<A_L phi,S_L A_L phi>-<A_L phi,A_L S_L phi>            (7.5)
```

means precisely this represented vector/form pairing. No claim is made that
`[S_L,A_L]` is a bounded operator.

## 8. Exact source energy identity and residual closure

Let `E_L^sigma=E_L(sigma h_L)`. The source ground form equation, polarization,
(6.6), and the common form domain give, for every `A in D_bl`,

```text
cal E_L^sigma(A)
 :=q_(H_L(sigma h_L)-E_L^sigma)[A_L phi_L^sigma]
 =-i hbar omega_L^sigma(A^*delta_H A)
  -sigma h_L
   <phi_L^sigma,A_L^*[S_L,A_L]phi_L^sigma>
 >=0.                                                       (8.1)
```

This is the exact R-167 v3.9 quadratic-form commutator identity. Because
the defect (6.7) is zero, its complex combined residual reduces to

```text
R_L^sigma(A)
 :=sigma h_L
   <phi_L^sigma,A_L^*[S_L,A_L]phi_L^sigma>.                (8.2)
```

Equations (7.3)--(7.4) imply

```text
||S_L A_L phi_L^sigma||
 <=||A||_H
   sqrt[a V(eta_L^sigma+hbar R_A)+B_a V^2],                (8.3)

||S_L phi_L^sigma||
 <=sqrt[a V eta_L^sigma+B_a V^2].                         (8.4)
```

Cauchy--Schwarz in the two terms of (7.5) now gives

```text
|R_L^sigma(A)|
 <=h_L||A||_H^2
   {sqrt[a V(eta_L^sigma+hbar R_A)+B_a V^2]
    +sqrt[a V eta_L^sigma+B_a V^2]}.                      (8.5)
```

For fixed `A`, the braces are `O(V)`. The upper mesoscopic condition
`h_L V->0` proves

```text
|R_L^sigma(A)|->0,             A in D_bl.                  (8.6)
```

Equivalently, (8.1) has the v3.9 target decomposition

```text
-i hbar omega_L^sigma(A^*delta_H A)
 =cal E_L^sigma(A)+R_L^sigma(A).                           (8.7)
```

## 9. Joint ground-state clusters

The state space of the separable unital algebra `A_H^0` is weak-star
sequentially compact. Pass to one joint subnet or subsequence for the two
signs:

```text
omega_L^sigma -> omega_sigma.                              (9.1)
```

On the unital star graph core `D_bl`, equations (8.6)--(8.7) and
`cal E_L^sigma(A)>=0` give

```text
-i hbar omega_sigma(A^*delta_H A)>=0.                      (9.2)
```

R-167 v3.9 tests (9.2) on `1+zA` for every complex `z`, derives
`omega_sigma(delta_H A)=0`, and then uses graph-core closure. Consequently
each limit is `theta`-invariant and is an algebraic `theta`-ground state.
Equation (6.10) passes to the limit:

```text
omega_-=omega_+ o gamma.                                  (9.3)
```

There is also an independent proof. The R-167 v1.6 negative-Arveson
estimate uses only the zero-source excess energy of the finite vectors.
Replacing its `epsilon_L` by `eta_L^sigma->0` in (4.10) proves the same
ground-state conclusion.

## 10. One fixed odd carrier witness

At one fixed site put

```text
X=sum_(e=1)^8 q_e=sqrt(8)Q_0.                              (10.1)
```

By (5.11) and Lyapunov's inequality,

```text
<|X|^3>_(phi_L^sigma)
 <=M_3:=(64 C_4)^(3/4).                                   (10.2)
```

Choose once and for all a positive rational `r_w` such that

```text
r_w^2 M_3<=3 sqrt(8)m_*.                                  (10.3)
```

The rational label is

```text
xi=r_w(1,...,1),                                          (10.4)
```

not `r_w(1,...,1)/sqrt(8)`. From (4.12), translation
invariance and `|sin z-z|<=|z|^3/6`,

```text
omega_L^+(sin(r_w X))
 >=r_w sqrt(8)m_*-r_w^3 M_3/6
 >=r_w sqrt(8)m_*/2=:d>0.                                (10.5)
```

Parity gives the minus expectation at most `-d`.

Fix `T>0` and the triangular probability density

```text
f_T(t)=T^(-1)(1-|t|/T)_+.                                 (10.6)
```

As in v1.6,

```text
int f_T(t)|t|^(1/2)dt=(8/15)sqrt(T).                       (10.7)
```

The one fixed target element

```text
b=[A_(xi,f_T)-A_(-xi,f_T)]/(2i)                           (10.8)
```

is odd, self-adjoint and has norm at most one. For every contraction `B`,
the scalar spectral inequality gives

```text
|omega_L^sigma(alpha_t^(L,0)(B))-omega_L^sigma(B)|
 <=2 sqrt(2|t| eta_L^sigma/hbar).                         (10.9)
```

Integration against (10.6) gives the exact smear error

```text
|omega_L^sigma(b)-omega_L^sigma(sin(r_w X))|
 <=(16/15)sqrt(2T eta_L^sigma/hbar)->0.                  (10.10)
```

Therefore, eventually,

```text
omega_L^+(b)>=d/2,
omega_L^-(b)<=-d/2.                                      (10.11)
```

Passing to the joint cluster pair,

```text
omega_+(b)>=d/2,
omega_-(b)<=-d/2,
||omega_+-omega_-||>=d.                                  (10.12)
```

Thus the two target ground states are distinct by one fixed carrier
observable chosen before the cluster extraction.

## 11. Why the theorem is nonduplicate

1. **EXP-000781.** Its states are fixed-positive-temperature Euclidean DLR
   and locally normal time-zero tangent states. It neither has the present
   zero-temperature source-ground input nor a common target ground identity.

2. **EXP-000789.** It constructs the hand-built zero-source approximate
   doublets `Psi_L^sigma`. The new theorem starts from the exact finite-volume
   ground vectors of `H_L(sigma h_L)`.

3. **EXP-000790.** Its selected ground candidates use the ordered limit
   `L->infinity` at fixed `h`, followed by `h->0`. The present states use the
   diagonal mesoscopic path (4.7). No equality of the two branches follows
   without a near-zero source-uniform finite-size convergence rate.

4. **R-167 v1.6.** It already proves distinct algebraic ground states on
   `A_H^0`, but only from the EXP-000789 approximate doublets. The new
   increment is exact source-ground selection together with a model-specific
   construction of the v3.9 graph core and residual estimate.

5. **R-167 v3.8.** It concerns fixed-temperature Gibbs/KMS states on a
   source-family carrier. Its zero-source quotient factorization is open.
   Here the source-ground vectors are evaluated directly through the
   zero-source representations `pi_L^0`; no v3.8 factorization is asserted.

6. **R-167 v3.9.** It is conditional and explicitly leaves the exact-Q3
   target representation, graph core and residual open. Sections 5--8 supply
   those data on the categorical zero-source carrier.

The two endpoints in (4.7) are proof boundaries, not no-go theorems. The
existing v3.9 `M_3(C)` fixture remains the exact warning that `h_L->0` alone
does not kill a source residual.

## 12. Devil's-advocate audit

1. **Objection: the source ground need not be unique after parity is broken.
   DISMISSED.** The real linear source preserves confinement and strict
   Feynman--Kac positivity. It selects one strictly positive finite-volume
   ground; parity maps the positive-source ground to the negative-source
   ground.

2. **Objection: the order inequality has the wrong source sign.
   DISMISSED.** `Psi_L^sigma` has source expectation `sigma V m_L`, while
   the Hamiltonian contains `-sigma h_L S_L`; their product is always
   `-h_L V m_L`. Equation (4.4) follows with
   `V m_L-sigma s_L^sigma`.

3. **Objection: one source scaling cannot both select order and remove the
   residual. DISMISSED.** Order needs `h_L V^2->infinity`; the residual bound
   needs `h_L V->0`. The interval is nonempty, and `V^(-3/2)` is explicit.

4. **Objection: `B_a` or `C_4` contains a pasted numerical margin.
   DISMISSED.** Equations (5.6) and (5.11) derive both constants directly
   from `a`, `gamma`, `A_s` and `C_gamma`. No extra `+1` or derived decimal
   is used.

5. **Objection: exact equivariance is weaker than generator equality.
   DISMISSED on `D_bl`.** The target action is point-norm continuous and
   `A in Dom(delta_H)`, so differentiating (6.3) in norm proves (6.6).

6. **Objection: `[S_L,A_L]` was treated as a bounded commutator.
   DISMISSED.** Sections 5 and 7 prove all vector/form domains and define the
   source term only by (7.5). No bounded operator commutator is claimed.

7. **Objection: the Arveson estimate misses a factor of `hbar`.
   DISMISSED.** `R_A` is a physical frequency. The energy-transfer window is
   `hbar R_A`, exactly as shown in (7.2)--(7.3).

8. **Objection: the two weak-star limits could coincide because the order
   observable changes with volume. DISMISSED.** The rational label `xi`, the
   triangular kernel and `b` are fixed before taking the subnet. Equation
   (10.12) gives one uniform state-distance lower bound.

9. **Objection: these are the EXP-000790 source tangents. UPHELD as an
   overclaim.** The limit orders differ. The present theorem constructs a new
   diagonal mesoscopic pair and supplies no identification theorem.

10. **Objection: the categorical carrier is the missing spatial common
    alpha. UPHELD as an overclaim.** Its representations are quotients, raw
    configuration characters can be absent, and temporal smearing supplies
    no commuting spatial local net or exhaustion Cauchy theorem.

11. **Objection: distinct ground states imply purity, disjointness or a
    positive broken-sector gap. UPHELD as false.** None of those properties
    follows from (9.2) and (10.12).

12. **Objection: the result closes beta-infinity selection, DLR/KMS
    identification, C6 or Pre-A. UPHELD as false.** It starts directly from
    zero-temperature finite-source ground vectors on a categorical target
    and leaves every listed parent interface open.

## 13. Scope, lifecycle and reproduction

EXP-000844 establishes R-167 v4.0 as additive T0, claim-nonbearing route
work. It supplies one exact-Q3 mesoscopic source-ground pair, an explicit
zero-source bandlimited graph core, exact target-generator matching, a
vanishing combined scalar residual and one fixed odd separator on the
existing categorical carrier.

It does not identify these states with the EXP-000790 iterated source
tangents, the EXP-000781 DLR tangents or the R-167 v3.8 KMS states. It proves
no v3.8 zero-source quotient factorization, no beta-infinity KMS limit, no
DLR/OS common-action identification, no spatial all-exhaustion thermodynamic
or quasi-local raw oscillator alpha, no purity, factoriality, disjointness,
phase exhaustion or positive broken-sector GNS gap, no regulator removal,
continuum, mass gap, physical vacuum or empty-space comparison, Round-1, C6,
CP1, physical Sector A or Pre-A. All five active parent gates and both
historical gates remain OPEN.

No new negative result is needed. The package reuses, in order:

1. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS`;
2. `NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-AUTOMATIC-ZERO-SOURCE-QUOTIENT-FACTORIZATION`;
3. `NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET`.

Reproduce the proof-first package from the repository root:

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_mesoscopic_source_ground_orbit_smear_transfer_route_split.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_mesoscopic_source_ground_orbit_smear_transfer_route_split_independent.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_mesoscopic_source_ground_orbit_smear_transfer_route_split_verify.py --staged --no-store
```

The scripts derive the mesoscopic exponents, coercive constants, energy-
transfer factor, residual scaling and fixed-witness inequalities from labelled
inputs. The independent implementation uses only exact standard-library
`Fraction` arithmetic. The scripts audit the analytic authority and scope
contract; they do not replace the variational, positivity-improving,
quadratic-form, Arveson or graph-core arguments written here.

No v4.0 PDF is issued.
