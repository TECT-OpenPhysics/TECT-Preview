# R-167 v3.9 certificate: finite-source ground residual transfer and clipped-order separation

Date: 2026-08-13  
Task: T-054  
Exploration: EXP-000843  
Claim-bearing: false (T0 route work)  
PDF: none issued

## 1. Exact scoped result

This certificate closes only
`PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-GROUND-RESIDUAL-TRANSFER-AND-CLIPPED-ORDER-SEPARATION`.

It proves two conditional abstract lemmas. First, an exact finite-source ground
energy identity transfers to an algebraic ground state of one target dynamics
when one complex expectation-level residual vanishes on a graph core. Second,
a locally normal unbounded order parameter with a fourth-moment bound yields
one fixed bounded odd separator in a declared carrier whose unit ball is
strong-star dense. An exact `M_3(C)` fixture proves that a vanishing scalar
source, exact target generator, parity and fixed order separation do not
replace the residual hypothesis.

This is not an exact-Q3 common-target construction. It proves neither the
required Q3 represented domains nor the Q3 combined-residual estimate.

## 2. Common target and finite represented ground systems

Let `(A,alpha)` be one unital point-norm `C0` C-star system with closed
generator `delta`, and let `hbar>0`. Let `D` be a unital star-subalgebra of
`Dom(delta)` and a graph core for `delta`.

Fix one sign `sigma in {-1,+1}`. For every index `n`, let

```text
pi_n:A -> B(H_n),                       A_n=pi_n(A),
H_n(sigma h_n)=H_n(0)-sigma h_n S_n,   h_n>0,
```

where `Omega_n` is a normalized ground vector of `H_n(sigma h_n)` with
ground energy `E_n`. The theorem is applied separately to the two signs.
Fixing the sign keeps `pi_n`, `Omega_n`, `E_n`, `tilde omega_n`, `d_n` and
`R_n^sigma` one unambiguous sequence throughout the proof.
The operators or forms `H_n(0)`, `H_n(sigma h_n)` and `S_n` are self-adjoint
under the declared pairings.

For every `A in D`, assume the following domain conditions explicitly:

- `A_n Omega_n` belongs to the quadratic-form domain of
  `H_n(sigma h_n)-E_n`;
- `A_n`, `A_n*` and their actions on `Omega_n` lie in all operator or
  quadratic-form domains needed to evaluate the displayed commutators with
  `H_n(0)` and `S_n`;
- `delta_n^0(A_n)=(i/hbar)[H_n(0),A_n]` is represented by a vector or form
  expression for which multiplication by `A_n*` and the vector-state
  expectation below are defined;
- the quadratic-form commutator identity (3.1) below is valid on these
  declared pairings;
- `pi_n(delta A)` and
  `d_n(A)=delta_n^0(A_n)-pi_n(delta A)` are defined in that same expectation
  sense.

These premises are part of the theorem. No unbounded commutator is asserted
outside them.

Define the represented vector functional and its pullback state on the
single target algebra by

```text
hat omega_n(T)=<Omega_n,T Omega_n>,
tilde omega_n(A)=hat omega_n(pi_n(A)).                       (2.1)
```

The first expression is used only for the declared bounded or vector/form
pairings; the second is a state on the abstract C-star algebra `A`.

Assume `tilde omega_n -> omega` weak-star on `A`.

## 3. Exact energy identity and the combined residual

The source-ground property gives, for every `A in D`,

```text
cal E_n(A)
 =q_(H_n(sigma h_n)-E_n)[A_n Omega_n]
 =-i hbar hat omega_n(A_n* delta_n^0(A_n))
  -sigma h_n hat omega_n(A_n* [S_n,A_n])
 >=0.                                                        (3.1)
```

Here each expectation is shorthand for its declared represented vector/form
pairing. Insert

```text
delta_n^0(A_n)=pi_n(delta A)+d_n(A)                          (3.2)
```

and define the complex scalar residual

```text
R_n^sigma(A)
 =sigma h_n hat omega_n(A_n* [S_n,A_n])
  +i hbar hat omega_n(A_n* d_n(A)).                          (3.3)
```

Then the exact target decomposition is

```text
-i hbar tilde omega_n(A* delta A)
 =cal E_n(A)+R_n^sigma(A).                                  (3.4)
```

The notation in (3.4) means
`tilde omega_n(A*delta A)=<Omega_n,A_n* pi_n(delta A)Omega_n>`.

The sharp hypothesis is

```text
|R_n^sigma(A)| -> 0                                         (3.5)
```

for each `A in D` in the fixed-sign sequence. Applying the theorem to both
signs requires this premise separately for each sign. It is not necessary to prove norm
convergence of the represented generators if the combined scalar residual
can be estimated directly. A stronger sufficient corollary is

```text
||d_n(A)|| -> 0,
sigma h_n hat omega_n(A_n* [S_n,A_n]) -> 0                  (3.6)
```

separately, whenever `d_n(A)` is bounded. Equation (3.6) is sufficient, not
the theorem's minimal premise.

## 4. Passage to an algebraic ground state

Weak-star convergence applies directly to the fixed target element
`A*delta A`. Taking the limit in (3.4), using (3.5) and
`cal E_n(A)>=0`, gives

```text
-i hbar omega(A*delta A)>=0,       A in D.                   (4.1)
```

This real nonnegative form also forces invariance. For any `A in D` and
every `z in C`, use the unitality of `D` in (4.1) with `1+zA`. Since
`delta(1)=0`, the terms linear in `z` are

```text
-i hbar z omega(delta A).                                   (4.2)
```

Nonnegativity and reality for every complex `z` force
`omega(delta A)=0`. Graph-core approximation extends this identity and
(4.1) to `Dom(delta)`: if `A_k->A` and `delta(A_k)->delta(A)` in graph norm,
then

```text
||A_k*delta(A_k)-A*delta(A)||
 <=||A_k-A|| ||delta(A_k)||+||A|| ||delta(A_k)-delta(A)||.   (4.3)
```

Thus `omega(delta A)=0` and
`-i hbar omega(A*delta A)>=0` on `Dom(delta)`. The first identity yields
`alpha`-invariance; the second is the algebraic ground-state condition.

This theorem is strictly expectation-level. R-167 v3.2 used norm convergence
of changing generators in a beta-to-infinity KMS transfer. The present result
starts from finite-source ground vectors and requires only the combined
scalar residual (3.5).

## 5. Clipped order and one carrier observable

Let `M_X` be one local von Neumann algebra in the target representation.
Assume:

- `omega_+` and `omega_-` have normal restrictions to `M_X`;
- a normal involutive parity automorphism `gamma` of `M_X` satisfies
  `omega_-=omega_+ o gamma`;
- `Q` is self-adjoint and affiliated with `M_X`, with

```text
gamma(Q)=-Q,
omega_+(Q)>=m>0,
omega_+(|Q|^4)<=M_4<infinity;                               (5.1)
```

- `B` is a parity-stable unital C-star subalgebra of the same represented
  target/local algebra, and the unit ball of `B` is strong-star dense in the
  unit ball of `M_X`.

For `R>0`, functional calculus defines

```text
B_R=clip(Q/R,-1,1).                                         (5.2)
```

It is an odd self-adjoint contraction. On `|Q|>R`, the pointwise loss from
`Q/R` to the clip is at most `|Q|/R`, and
`|Q| 1_(|Q|>R)<=|Q|^4/R^3`. Therefore

```text
omega_+(B_R)
 >=omega_+(Q)/R-omega_+(|Q|^4)/R^4
 >=d_R:=m/R-M_4/R^4.                                      (5.3)
```

Choose a fixed `R` with `d_R>0`. Normality and Kaplansky density give a net
of contractions from `B` converging strong-star to `B_R`. Self-adjoint and
parity averaging preserves membership in `B`, convergence and norm at most
one. Hence for any fixed `epsilon` with

```text
0<epsilon<d_R                                               (5.4)
```

there is one odd self-adjoint contraction `b in B` such that

```text
|omega_+(b)-omega_+(B_R)|<epsilon.                          (5.5)
```

It follows that

```text
omega_+(b)>=d_R-epsilon,
omega_-(b)<=-(d_R-epsilon),
||omega_+|_B-omega_-|_B||>=2(d_R-epsilon).                  (5.6)
```

The clipped operator `B_R` is not claimed to lie in the carrier. The new
increment beyond the clipping estimate already noted in v3.2 is the explicit
normal/strong-star carrier realization of one fixed odd contraction.

## 6. Exact `M_3(C)` obstruction

This finite-dimensional fixture uses `hbar=1`. In the ordered basis
`(e_-1,e_0,e_+1)`, put

```text
Q=diag(-1,0,1),                 K=Q^2,
h_n=1/n,                        S_n=2nQ,
H_n^sigma=K-sigma h_n S_n=K-2sigma Q.                       (6.1)
```

For either `sigma in {-1,+1}`, the vector `e_sigma` is the unique ground
vector of `H_n^sigma`, with energy `-1`. Let `omega_sigma` be its vector
state and put

```text
A_sigma=|e_0><e_sigma|.                                    (6.2)
```

The target generator is exact:

```text
delta_K(A_sigma)=i[K,A_sigma]=-i A_sigma,
d_n(A_sigma)=0.                                             (6.3)
```

The target energy form is negative,

```text
-i omega_sigma(A_sigma* delta_K(A_sigma))=-1.               (6.4)
```

The finite source ground energy and scalar source residual are

```text
cal E_n(A_sigma)=1,
sigma h_n omega_sigma(A_sigma* [S_n,A_sigma])=-2.            (6.5)
```

Thus the combined residual is `R_n^sigma(A_sigma)=-2`, and (3.4) reads

```text
-1=1+(-2).                                                  (6.6)
```

All displayed values are exact and independent of `n`. The states are
parity related and separated by the same contraction `Q`, since
`omega_sigma(Q)=sigma`. Nevertheless they are not ground states for the
target `K` dynamics because (6.4) violates the ground-form inequality.

The fixture proves
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-VANISHING-SOURCE-EXACT-TARGET-GENERATOR-AND-SEPARATION-AUTOMATIC-TARGET-GROUNDNESS`.
It is not a Q3LOCK counterexample: the selector `S_n=2nQ` grows while
`h_n->0`. Its sole role is to show that the product entering the scalar
residual need not vanish with the source.

## 7. Devil's-advocate audit

1. **Objection: source convergence alone makes the source commutator term
   disappear. UPHELD as false.** The exact fixture has `h_n->0` but the
   scalar source residual is the fixed value `-2`.

2. **Objection: norm generator convergence is hidden in the theorem.
   DISMISSED.** The minimal premise is only the complex combined residual
   (3.5). Norm convergence plus a separate source estimate is listed only as
   a stronger sufficient corollary.

3. **Objection: weak-star convergence cannot pass a changing commutator.
   DISMISSED in the declared theorem.** The changing part is isolated in
   `R_n^sigma(A)`; weak-star passage is applied only to the fixed target
   element `A*delta A`.

4. **Objection: positivity on the graph core does not imply invariance.
   DISMISSED.** Testing `1+zA` for every complex `z` first proves
   `omega(delta A)=0`; graph closure then gives invariance.

5. **Objection: unbounded commutators were used without domains. DISMISSED
   conditionally.** Section 2 makes every vector/form-domain requirement an
   explicit theorem premise. Exact Q3 must still verify it.

6. **Objection: the clipped unbounded observable need not belong to the
   carrier. UPHELD.** It is not asserted to belong. Normality plus strong-star
   density supplies the fixed carrier contraction `b`.

7. **Objection: parity averaging can double the norm. DISMISSED.** The maps
   `x -> (x+x*)/2` and `x -> (x-gamma(x))/2` are contractions for an
   isometric star automorphism, and both preserve strong-star convergence.

8. **Objection: an algebraic ground state already supplies a positive GNS
   gap. UPHELD as false.** No coercivity or isolated-kernel estimate appears.
   The previously registered finite-gap/GNS-transfer negative remains a
   contextual boundary only.

9. **Objection: the theorem identifies the selected exact-Q3 pair as target
   ground states. UPHELD as an overclaim.** No exact-Q3 common target
   representation/core or combined residual estimate is proved here.

## 8. Scope and lifecycle

EXP-000843 establishes R-167 v3.9 as additive T0, claim-nonbearing route
work. It proves a conditional finite-source combined-residual transfer, a
conditional clipped-order carrier-separation lemma, and one exact logical
counterfixture.

It proves no exact-Q3 common target representation, graph core or residual
estimate, no selected Q3 target ground state, no zero-source quotient
factorization, no all-exhaustion thermodynamic or spatial common alpha, no
purity, factoriality, disjointness, phase exhaustion or positive
broken-sector GNS gap, no regulator removal, continuum, mass gap, physical
vacuum or empty-space comparison, Round-1, C6, CP1, physical Sector A or
Pre-A. All five active parent gates and both historical gates remain OPEN.
No v3.9 PDF is issued.

Reproduce the proof-first package from the repository root:

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_source_ground_residual_transfer_and_clipped_order_separation_route_split.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_source_ground_residual_transfer_and_clipped_order_separation_route_split_independent.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_finite_source_ground_residual_transfer_and_clipped_order_separation_route_split_verify.py --staged --no-store
```
