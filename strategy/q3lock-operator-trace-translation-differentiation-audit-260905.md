# Q3LOCK finite-volume translation trace-differentiation audit

**Status:** T0 fixed-volume operator proof-text audit; common-core review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deferred until mathematical content freeze and final release review

## 1. Purpose and boundary

The finite-volume operator note records the global translation identity but
left the differentiation of the heat trace under an unbounded polynomial
perturbation as an explicit reviewer obligation.  This note supplies a
Feynman--Kac/form argument for that step.  It avoids treating a cubic
multiplication operator as bounded and gives the exact domination needed for
the first two source derivatives.

The argument is at fixed periodic spatial volume and at zero physical source.
It does not prove a volume-uniform common core, a thermodynamic operator
limit, a pressure cusp, or DLR multiplicity.

## 2. Form setup and uniform translated coercivity

Let `q` lie in `R^(8V)` and write the exact positive-difference Hamiltonian as

```text
H_L(t) = -(hbar^2/(2*chi))*Delta_q + U_L(q+t*v),
v_(y,e)=u_e/sqrt(V),  |u|=1.
```

The spatial difference part of `U_L` is invariant under the common shift
`q -> q+t*v`.  On every bounded interval `|t|<=t_0`, quartic coercivity gives

```text
U_L(q+t*v) >= alpha*sum_y |q_y|^4 - C_(L,t_0),
alpha=g/128.
```

The associated form domain is

```text
Q_L = H^1(R^(8V)) intersect
      L^2(R^(8V), (sum_y |q_y|^4)dq),
```

independent of `t`.  Smooth compactly supported functions are a form core by
radial cutoff followed by mollification.  The translated forms are closed,
lower bounded and have compact resolvent.

## 3. Polynomial derivative bounds

On the form core, let

```text
A_L = H_L'(0) = sum_(y,e) v_(y,e)*partial_(y,e) U_L(q),
B_L = H_L''(0) = sum_(y,e,z,f)
       v_(y,e)*v_(z,f)*partial_(y,e)partial_(z,f) U_L(q).
```

The quartic polynomial structure gives constants depending on fixed `L` and
`t_0` such that

```text
|A_L(q)| <= C_(L)*(1+sum_y |q_y|^3),
|B_L(q)| <= C_(L)*(1+sum_y |q_y|^2).
```

For `|t|<=t_0`, the same estimates hold for the derivatives of `U_L(q+t*v)`.
Using `z^k <= eta*z^4+C_(eta,k)` and the coercive bound, the Feynman--Kac
weight has finite moments of every polynomial degree and

```text
integral |A_L|^2*exp(-beta*H_L(t)) < infinity,
integral |B_L|*exp(-beta*H_L(t)) < infinity.
```

The estimates are finite-volume statements; their constants are not asserted
uniform in `V`.

## 4. Differentiating the heat trace without a bounded-operator shortcut

The finite-volume Feynman--Kac formula represents `Tr exp(-beta*H_L(t))` by a
periodic Brownian-loop integral with potential `U_L(q+t*v)`.  The translated
coercive bound in Section 2 and the derivative estimates in Section 3 give a
common integrable majorant for the first and second difference quotients on
`|t|<=t_0`.  Dominated convergence therefore yields

```text
Z_L'(0) = -beta*Tr(A_L*exp(-beta*H_L(0))),
```

and

```text
Z_L''(0)
  = -beta*Tr(B_L*exp(-beta*H_L(0)))
    + beta^2*b_L(A_L),
```

where `b_L` is the Kubo--Mori/Duhamel quadratic form.  To make the operator
identity explicit, first replace `A_L` by bounded smooth polynomial cutoffs.
The standard bounded Duhamel differentiation formula holds for the cutoffs.
The bounds in Section 3 and Cauchy--Schwarz for the Duhamel form let the
cutoffs converge in the Duhamel norm, while the `B_L` term converges by its
ordinary Gibbs moment.  This recovers the displayed identities for the
unbounded polynomial derivatives on the form core and then by form closure.

At zero source, global parity maps `q` to `-q`, leaves `H_L(0)` invariant and
makes `rho_L(A_L)=0`.  Hence `b_L(A_L)` is the Duhamel variance.

## 5. Translation identity and the Q3LOCK moment bound

The operators `H_L(t)` are unitarily equivalent, so `Z_L(t)` is constant.
Using Section 4 gives

```text
0 = -beta*rho_L(B_L) + beta^2*Var_(D,L)(A_L).
```

The positive-difference spatial term has zero second derivative under the
common shift.  Direct differentiation of the onsite scalar and Q3 terms gives

```text
B_L = r
       + (3*g/(8*V))*sum_y S_y
       + (lambda/(8*V))*sum_y D_y,
S_y=sum_e q_(y,e)^2,
D_y=sum_{{e,f} in E(Q3)}(q_(y,e)-q_(y,f))^2.
```

Equivalently, the commutator is
`[Pi_0,[H_L(0),Pi_0]]=hbar^2*B_L`; the displacement derivative itself has no
additional `hbar^2`.

Since the Duhamel variance is nonnegative, `rho_L(B_L)>=0`, and spatial
translation invariance yields

```text
-r <= (3*g/8)*rho_L(S_0) + (lambda/8)*rho_L(D_0).
```

The remaining conversion to `rho_L(Q_0^2)>=theta_Q` uses the independently
audited continuous-loop FKG inequalities and is recorded in the companion
operator note.

## 6. Compatibility with the local Falk--Bruch cutoff

The translation derivative `A_L` in Section 4 is not the local coordinate used
in the Falk--Bruch step.  The latter uses `Q_0=u dot q_0` and the bounded cutoff
`Q_R=R*tanh(Q_0/R)`.  The two arguments are logically separate: Section 5
supplies the second-moment lower bound, while the bounded commutator identity
and cutoff removal supply the local Duhamel lower bound.  The cutoff removal
and its exact `beta*hbar^2/chi` double commutator are audited in
`strategy/q3lock-operator-form-domain-unbounded-commutator-audit-260905.md`.

## 7. Adversarial checks

1. **Differentiate `Tr exp(-beta H_L(t))` by assuming `A_L` is bounded.**
   Rejected: bounded cutoffs are used first and the Duhamel/form estimates
   remove them.
2. **Use a translated quartic lower bound with constants depending on `t` in
   the difference quotient.**  Rejected: one coercive constant is chosen on a
   fixed compact `t` interval.
3. **Include a nonzero spatial contribution in `B_L`.**  Rejected: the full
   positive-difference energy is invariant under a common cell shift.
4. **Identify the translation derivative with the Falk--Bruch coordinate.**
   Rejected: they are distinct observables with distinct roles.
5. **Promote finite-volume dominated convergence to a uniform thermodynamic
   operator theorem.**  Rejected: no volume-uniform estimate is asserted.
6. **Use the trace identity to infer a phase without FKG, IR and Griffiths.**
   Rejected: those downstream inputs remain separate and conditional.

## 8. Disposition and review gate

**Advanced at T0:** the unbounded translation trace differentiation is reduced
to a form/Feynman--Kac dominated-convergence argument with bounded cutoffs, and
the exact global second-derivative identity is re-derived in the Q3LOCK
normalization.

**Still open:** independent verification of the polynomial heat-trace majorant,
the cutoff-to-form closure, volume-uniform common-core estimates, the FKG
moment conversion, the pressure/source-tangent composition, and external
mathematical review.  No claim card, theorem-tier promotion, manuscript
release or PDF is created.
