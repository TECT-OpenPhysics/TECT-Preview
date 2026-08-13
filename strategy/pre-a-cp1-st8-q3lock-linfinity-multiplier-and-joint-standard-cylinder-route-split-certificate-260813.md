# R-167 v3.1 certificate: essential-range multiplier jump and joint standard-cylinder scalarity

Date: 2026-08-13

Task: T-054

Exploration: EXP-000835 (continues EXP-000834)

Tier and role: T0, `claim_bearing: false`, additive proof-first route split.

Checkpoint status: DEFERRED. No v3.1 PDF is issued.

## 1. Precise scope

Fix one finite Q3 volume `Lambda`. Its configuration representation is

```text
H_Lambda = L2(R^d),                 d = 8 |Lambda|,
H = P^2/(2 chi) + V(Q),             chi > 0,
U_t = exp(-i t H / hbar),           alpha_t(A) = U_t^* A U_t.
```

Here `V` is the exact real semibounded coercive Q3 polynomial, of degree at
most four, and `H` is the self-adjoint closure of its Schwartz-core
realization.  For `f in L_infinity(R^d)`, write `M_f` for multiplication by
`f` and

```text
D_ess(f) = diam essran(f)
         = sup {|a-b| : a,b in essran(f)}.
```

The new theorem is

```text
liminf_(t -> 0, t != 0) ||alpha_t(M_f)-M_f|| >= D_ess(f).       (1.1)
```

If `f` is real, scalar midpoint subtraction also gives the exact two-sided
limit

```text
lim_(t -> 0, t != 0) ||alpha_t(M_f)-M_f||
  = ess sup(f)-ess inf(f).                                      (1.2)
```

Thus every nonessentially-constant bounded measurable configuration
multiplier is excluded from the point-norm continuous part of the exact
finite-volume full-Hamiltonian action.

This is a multiplier theorem.  It is not a classification of the full
continuous-element algebra.  In particular it does not exclude compact,
temporally smeared, resolvent-smoothed, interaction-dressed, bounded-strict,
strong-star, or state-weighted carriers.

## 2. Essential-range and Lebesgue-point preparation

Let `a,b in essran(f)` and let `eta>0`.  The measurable sets

```text
E_a(eta) = {q : |f(q)-a| < eta},
E_b(eta) = {q : |f(q)-b| < eta}
```

have positive measure.  Lebesgue differentiation therefore supplies points
`x in E_a(eta)` and `y in E_b(eta)` at which a precise representative of `f`
has Lebesgue values `f(x)` and `f(y)`.  In particular

```text
|f(x)-a| < eta,              |f(y)-b| < eta.                    (2.1)
```

Choose one real normalized `phi in C_c^infinity(R^d)` and set

```text
phi_(x,epsilon)(q) = epsilon^(-d/2) phi((q-x)/epsilon).
```

For fixed `epsilon>0`, the packet is a Schwartz vector.  At the end of the
argument its multiplier expectations converge to `f(x)` and `f(y)` as
`epsilon -> 0`.

## 3. The moving Galilean packet

For `t != 0`, put

```text
p_t = chi (y-x)/t,
psi_(t,epsilon) = exp(i p_t.Q/hbar) phi_(x,epsilon).             (3.1)
```

The boost commutes with every configuration multiplier, so

```text
<psi_(t,epsilon), M_f psi_(t,epsilon)>
  = <phi_(x,epsilon), M_f phi_(x,epsilon)>.                     (3.2)
```

Let `U_t^0=exp[-i t P^2/(2 chi hbar)]`.  The exact Galilean formula, after
taking absolute values, is

```text
|U_t^0 psi_(t,epsilon)(q)|^2
  = |U_t^0 phi_(x,epsilon)(q-(y-x))|^2.                         (3.3)
```

Only this density identity is used.  The boosted vector itself has a
diverging phase, with a scalar phase diverging like `1/t`, and is not claimed
to converge.

For an intermediate Duhamel time `s` between zero and `t`, including when
`t<0`, one has `s/t in [0,1]`.  Hence the translated packet centre

```text
x + (s/t)(y-x)                                                   (3.4)
```

stays on the fixed compact segment from `x` to `y` for both time directions.

## 4. Uniform polynomial control along the segment

If `m=deg V`, polynomial translation gives a constant depending on the fixed
points and on `V`, but not on `t` or on `s` between zero and `t`, such that

```text
|V(q+a)| <= C_(x,y,V) (1+|q|^m)                                 (4.1)
```

for every `a` on the segment.  Free evolution preserves Schwartz space and
its seminorms are locally bounded in time.  Consequently, for each fixed
`epsilon`,

```text
sup_(s between 0 and t) ||V U_s^0 psi_(t,epsilon)||
  <= C_epsilon                                                     (4.2)
```

for all sufficiently small positive and negative `t`.  Duhamel's formula on
the Schwartz core, followed by closure, gives

```text
||(U_t-U_t^0) psi_(t,epsilon)||
  <= C_epsilon |t|/hbar.                                         (4.3)
```

Boundedness of `M_f` turns (4.3) into the expectation estimate

```text
|<U_t psi,M_f U_t psi>-<U_t^0 psi,M_f U_t^0 psi>|
  <= 2||f||_infinity C_epsilon |t|/hbar.                         (4.4)
```

No estimate for `(U_t-U_t^0)M_f psi`, and no estimate uniform as
`epsilon -> 0`, is asserted or needed.

The executable translation fixture uses

```text
V_*(q)=1/2-q+2q^2-(3/2)q^3+(5/2)q^4,
sum_k |c_k|=15/2,              |a|<=3.
```

For `0<=k<=4`, `|q+a|^k<=1+|q+a|^4`, while
`(|q|+3)^4<=8(|q|^4+3^4)`.  Thus the deliberately conservative exact envelope
is

```text
|V_*(q+a)| <= (15/2)(1+8*3^4)(1+|q|^4)
             = (9735/2)(1+|q|^4).                               (4.5)
```

This finite polynomial is an arithmetic oracle, not the proof of (4.1).

## 5. The lower bound

The operator norm dominates the moving-vector expectation.  By (3.2),
(3.3), and (4.4), first letting `t -> 0` through either sign at fixed
`x,y,epsilon` gives

```text
liminf_(t -> 0, t != 0) ||alpha_t(M_f)-M_f||
 >= | <phi_(y,epsilon),M_f phi_(y,epsilon)>
       - <phi_(x,epsilon),M_f phi_(x,epsilon)> |.                (5.1)
```

Now let `epsilon -> 0` at the two Lebesgue points, use (2.1), and then let
`eta -> 0`.  Taking the supremum over `a,b in essran(f)` proves (1.1).

The safe quantifier order is therefore

```text
eta; x,y; fixed epsilon; two-sided t->0; epsilon->0; eta->0.     (5.2)
```

Reversing the last two limiting operations would require an estimate that was
not proved.

For real `f`, choose the scalar midpoint

```text
c=(ess sup f+ess inf f)/2.
```

Automorphisms fix scalars, so for every `t`

```text
||alpha_t(M_f)-M_f||
 <= 2 ||f-c||_infinity
 = ess sup f-ess inf f
 = D_ess(f).                                                      (5.3)
```

Together with (1.1), this proves (1.2).

## 6. Joint standard-cylinder scalarity

Let finite `Lambda` contain a nearest-neighbour bond `{x,y}`.  Embed a
one-site operator canonically by

```text
j_x(A)=A tensor I_(Lambda minus {x}).
```

Let `beta^(xy)` be the isolated nonzero bilinear bond flow and let
`alpha^Lambda` be the exact full-Q3 finite-volume flow.  R-167 v3.0 proved

```text
C(beta^(xy)) intersect j_x(B(L2(R^8)))
  = j_x(L_infinity(q_x)),                                        (6.1)
```

where `C(gamma)` denotes the point-norm continuous part of an action.  The
v3.1 theorem applied to the lifted multiplier `f(q_x)` says that such a
cylinder is also in `C(alpha^Lambda)` only if `f` is essentially constant.
Therefore the intersection equals the scalar multiples of `I_Lambda`:

```text
C(beta^(xy)) intersect C(alpha^Lambda)
  intersect j_x(B(L2(R^8))) = C I_Lambda.                        (6.2)
```

Equation (6.2) classifies only the canonical standard one-site cylinder under
simultaneous continuity.  It does not classify either full continuous
algebra.  In particular the two-site bond action has many other continuous
elements, including two-site compacts.

## 7. Strict strengthening and append-only history

The new negative authority

```text
NG-2026-08-13-PRE-A-ST8-Q3LOCK-
NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-
FULL-HAMILTONIAN-POINT-NORM-C0
```

strictly strengthens the v2.8 `C_b` configuration-multiplier boundary.  It
also contains the v2.7 raw configuration Weyl result, because the essential
range of `exp(i xi.q)` has diameter two when `xi != 0`.  The v3.0 modulation
commutant theorem contains the older nonzero compact-cylinder bond
obstruction.  Those records remain immutable historical evidence.  A second
joint-cylinder negative is not created: (6.2) is already a corollary of the
new CLOSED result and the v3.0 CLOSED result.

This strengthening does not prove that a common thermodynamic action is
impossible.  It rejects one raw standard-cylinder carrier requirement.

## 8. Exact fixtures

The primary and independent scripts derive the following finite oracles from
their declared inputs.

1. A real step function with essential values `-2` and `3` has midpoint
   `1/2`, essential oscillation `5`, midpoint upper bound `5`, and packet gap
   `5`.
2. A complex step function with essential values `0`, `1+i`, and `-1` has
   pairwise squared distances `2,1,5`, hence squared diameter `5`.  This checks
   only the lower-bound theorem.
3. For `chi=7/3`, `x=(1,-2)`, `y=(4,6)`, and `t=+/-2/5`, the derived boost
   obeys `(p_t/chi)t=y-x=(3,8)` for both signs.
4. Formula (4.5) gives the exact conservative polynomial envelope `9735/2`.
5. The joint truth table has: an off-diagonal witness with bond-modulation
   distance two; a nonscalar diagonal multiplier with bond distance zero and
   full-Hamiltonian lower bound five; and a scalar with both distances zero.

These fixtures catch sign, factor, limit-order, complex-versus-real, and
hardcoded-output regressions.  They are not numerical approximations to the
Q3 thermodynamic limit.

## 9. Surviving positive route

The canonical spatial cylinder is too rigid, but the v3.0 single-toggle
theorem leaves a precise positive target.  Let `D_dr` be a norm-dense unital
star core in a phase- and beta-independent dressed spatial C-star algebra.
For every finite background edge set `F`, every edge `e` outside `F`, every
`|s|<=T`, and every dressed seed `A_X`, the missing exact-Q3 lemma would prove
that the quadratic-form commutator extends boundedly and

```text
||[V_e,alpha_F^s(A_X)]||
 <= C(A_X,T) G_T(d(e,X)),                                        (9.1)
sum_(r>=0) N_X(r)G_T(r) < infinity,
N_X(r)=O_X((1+r)^2).                                              (9.2)
```

The bounds must be uniform in the finite background and insertion order and
valid for both time signs.  Norm Duhamel would then give the single-toggle
weight

```text
w_e(A_X,T)=(T/hbar) C(A_X,T)G_T(d(e,X)),                          (9.3)
```

so v3.0 supplies arbitrary-shape Cauchy convergence and an
exhaustion-independent C0 action.  Exponential `G_T` is summable; a power law
`(1+r)^(-p)` is summable in `Z^3` for `p>3`.

For the exact bond `V_e=(c/2)|R_e|^2`, `R_e=q_x-q_y`, the local identity is

```text
[V_e,D]=(c/2) sum_(a=1)^8
  ( [R_(e,a),[R_(e,a),D]] + 2[R_(e,a),D]R_(e,a) ).               (9.4)
```

The genuinely missing model lemma is a background-uniform spatial norm bound
on this whole form combination for non-scalar compatible dressed seeds.  The
earlier one-sided energy-damped commutator estimates do not bound (9.4) in
operator norm.  Finite-volume temporal smearing is background-dependent and
would make (9.1) circular; finite local energy damping only moves the raw
boundary; and no noncollapsing compatible dressed core is currently proved.

## 10. Literature firewall

The literature audit is used only to delimit direct imports.

- B. Nachtergaele, H. Raz, B. Schlein, and R. Sims,
  arXiv:0712.3820, treats anharmonic oscillator dynamics under Fourier and
  integrability hypotheses that do not include the exact simultaneous Q3
  quartic onsite and unbounded bilinear bond.
- L. Amour, P. Levy-Bruhl, and J. Nourrigat, arXiv:0904.2717, assumes a
  subquadratic, Fourier-regular perturbation class.
- D. Buchholz, arXiv:1605.05259, establishes resolvent-algebra lattice
  dynamics for harmonic pinning with bounded nearest-neighbour potentials;
  its unbounded one-site example does not supply the exact Q3 combination.

No one of these sources proves (9.1) for the exact Q3 Hamiltonian.  They are
not cited as a common-alpha theorem.

## 11. Devil's-advocate audit

**Objection 1: a discontinuous multiplier has no useful point value.**

DISMISSED.  The proof uses Lebesgue points of precise representatives inside
positive-measure essential-range level sets.  Null-set changes do not affect
the multiplication operator or the conclusion.

**Objection 2: the momentum `p_t` diverges, so the interaction Duhamel error
need not be small.**

DISMISSED WITH THE FIXED-EPSILON BOUND.  The Galilean boost disappears from
the modulus.  Intermediate translated centres remain on one compact segment,
and polynomial multiplication is uniformly bounded on the resulting fixed
Schwartz family.  The constant may diverge as `epsilon -> 0`, which is why
the order (5.2) is load-bearing.

**Objection 3: negative times run along another unbounded path.**

DISMISSED.  If `s` lies between zero and negative `t`, then `s/t` still lies
in `[0,1]`; the same compact segment and the same bound apply.

**Objection 4: the complex lower bound implies an exact limit.**

UPHELD AND MITIGATED.  Only real multipliers have the midpoint upper bound
used here.  Complex multipliers receive only (1.1).

**Objection 5: joint scalarity proves common-alpha nonexistence.**

UPHELD AND MITIGATED.  It proves scalarity only in the raw canonical one-site
cylinder under simultaneous isolated-bond and full-Hamiltonian point-norm
continuity.  Dressed, multi-site, smeared, resolvent, strict, strong-star, and
state-weighted routes remain logically available.

**Objection 6: the shell route has now been proved for Q3.**

UPHELD AND MITIGATED.  Equations (9.1)--(9.4) isolate the missing lemma.  No
exact-Q3 background-uniform bound or noncollapsing dressed core is supplied.

## 12. Formal disposition

Close exactly one scoped child:

```text
PA-CP1-ST8-Q3LOCK-LINFINITY-CONFIGURATION-MULTIPLIER-
ESSENTIAL-RANGE-FULL-HAMILTONIAN-NORM-JUMP-AND-
JOINT-STANDARD-CYLINDER-SCALARITY
```

Register exactly one strengthened negative, the nonessentially-constant
`L_infinity` multiplier boundary stated in Section 7.  All five active parent
gates remain OPEN.

R-167 v3.1 proves no exact-Q3 summable shell weights, spatial common alpha,
two-phase full-oscillator transfer, target-generator convergence, GNS gap,
regulator removal, continuum limit, physical empty-space comparison,
Round-1 package, C6, CP1, physical Sector A, or Pre-A.  No v3.1 PDF is issued.

## 13. Reproduction commands

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split_independent.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_linfinity_multiplier_and_joint_standard_cylinder_route_split_verify.py --staged --no-store
```

During proof development these commands write nothing.  Formal runs write the
three declared JSON artifacts only after EXP-000835, the gate and negative
authorities, event 627, T-054, ROADMAP, the strategy index, and theorem map
have landed.  Generated readers are then rebuilt and the repository release
gate is rerun.
