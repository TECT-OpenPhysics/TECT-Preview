# Q3LOCK momentum-translation derivative versus double-commutator normalization audit

**Status:** T0 operator-notation correction; no claim-card promotion; PDF deferred  
**Scope:** finite-volume global-momentum argument in the Q3LOCK operator audits  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782

## 1. Audit question

The Q3LOCK operator proof uses both the unitary translation
`U_t=exp(-i*t*Pi_0/hbar)` and the double commutator
`[Pi_0,[H_L(0),Pi_0]]`.  Are the factors of `hbar` attached to the correct
object when the second derivative of `H_L(t)=U_t^*H_L(0)U_t` is written?

## 2. Exact relation

On the Schwartz core, and then as a quadratic-form identity after closure,

```text
H_L'(0) = (i/hbar)*[Pi_0,H_L(0)],
H_L''(0) = (1/hbar^2)*[Pi_0,[H_L(0),Pi_0]].
```

The sign in the second line follows from
`[Pi_0,[Pi_0,H_L]]=-[Pi_0,[H_L,Pi_0]]`.  With
`Pi_0=V^(-1/2)*sum_y u dot p_y` and
`U_t^*q_yU_t=q_y+t*u/sqrt(V)`, direct differentiation of the declared
Q3LOCK polynomial gives

```text
B_L := H_L''(0)
   = r + (3g/(8V))*sum_y S_y + (lambda/(8V))*sum_y D_y,
```

where `S_y=sum_e q_(y,e)^2` and
`D_y=sum_{{e,f} in E(Q3)}(q_(y,e)-q_(y,f))^2`.  Equivalently,

```text
[Pi_0,[H_L(0),Pi_0]] = hbar^2*B_L.
```

Thus the factor `hbar^2` belongs to the commutator, not to the derivative
with respect to the physical displacement parameter `t` used in `U_t`.

## 3. Trace identity and unchanged moment bound

For `Z_L(t)=Tr exp(-beta*H_L(t))`, unitary equivalence makes `Z_L` constant.
The form/Feynman--Kac differentiation therefore reads

```text
0 = -beta*rho_L(B_L)
    + beta^2*Var_(D,L)(H_L'(0)),
```

at zero source (parity removes the first-moment term).  Hence
`rho_L(B_L)>=0`, which is exactly

```text
-r <= (3g/8)*rho_L(S_0) + (lambda/8)*rho_L(D_0).
```

No numerical lower bound changes: multiplying the commutator identity by the
positive scalar `hbar^(-2)` gives the same `B_L` and the same
`theta_Q=-r/[3*(g+lambda)]` after the independent FKG conversion.  The local
Falk--Bruch identity is different and correctly retains
`[Q_R,[beta*H_L,Q_R]] -> beta*hbar^2/chi`; it is a coordinate commutator, not a
translation derivative.

## 4. Files corrected

The displayed derivative in
`q3lock-operator-form-domain-unbounded-commutator-audit-260905.md` and the
corresponding `B_L` display in
`q3lock-operator-trace-translation-differentiation-audit-260905.md` are
rewritten to use `B_L=H_L''(0)` without `hbar^2`, with the commutator relation
shown separately.  The upstream EXP-000782 certificate already writes the
double-commutator form and is not changed.  No result JSON, Hamiltonian,
source convention, pressure normalization, proof claim, or scientific scope
is altered.

## 5. Adversarial checks

| objection | disposition | reason |
|---|---|---|
| Keep `hbar^2` on `H_L''(0)` because it appears in the commutator | **UPHELD AS FALSE** | With `U_t=exp(-i*t*Pi_0/hbar)`, the derivative is the commutator divided by `hbar^2`. |
| Removing the factor changes the `theta_Q` bound | **DISMISSED** | The trace identity uses the derivative `B_L`; the positive factor cancels when converting from the commutator. |
| The local Falk--Bruch commutator should also lose `hbar^2` | **UPHELD AS FALSE** | Its kinetic-coordinate commutator is `[Q_R,[beta H,Q_R]]`, whose coefficient is correctly `beta*hbar^2/chi`. |
| The correction proves the unbounded operator argument | **UPHELD AS FALSE** | Form-core, cutoff, trace-differentiation, FKG, thermodynamic and external-review gates remain open. |

## 6. Disposition and boundary

This repairs a dimensional/notation seam in two T0 finite-volume operator audit
notes.  It leaves R-497 at `T0 / INTERNAL_REVIEW_ONLY`,
`claim_bearing=false`, and `pdf_status=DEFERRED`.  Independent common-core and
trace-differentiation review, the P-06/P-09 audits, pressure/tangent
composition, external review, content freeze, and final PDF work remain open.
