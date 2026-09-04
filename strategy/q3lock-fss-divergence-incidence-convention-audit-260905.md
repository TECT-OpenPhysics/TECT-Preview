# Q3LOCK FSS divergence--incidence convention audit

**Status:** T0 proof-text notation correction; no claim-card promotion; PDF deferred  
**Scope:** finite-grid Poisson shift in the Q3LOCK P-09 FSS audit  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782

## 1. Audit question

The FSS source theorem is written with a discrete divergence acting on an edge
field, while the Q3LOCK spatial Laplacian is often written as a gradient
incidence operator followed by its adjoint.  Does the Poisson shift use the
correct operator order and source equation?

## 2. One convention with explicit domains

Let `V_0` be the zero-sum subspace of vertex fields on the periodic spatial
torus and let `E` be the oriented nearest-neighbour edge-field space.  Define

```text
B_FSS : E -> V,
(B_FSS h)(y) = sum_i partial_i h_i(y),
G := B_FSS^* : V -> E,
L_sp := B_FSS B_FSS^* = G^* G on V_0.
```

The sign of `G` depends on the chosen orientation; replacing every edge
orientation changes `G` and `B_FSS` by a common minus sign and changes no
norm or Laplacian.  On the periodic cubic torus, `L_sp` has eigenvalue
`2*E(p)` with `E(p)=sum_i(1-cos(p_i))`, and its kernel is the constant vertex
mode.  Therefore `L_sp^(-1)` is well-defined on `V_0`.

For a zero-sum source `j` choose the minimum-norm FSS edge field

```text
h = B_FSS^* L_sp^(-1) j.
```

Then

```text
B_FSS h = j,
||h||^2 = <j,L_sp^(-1)j>.
```

The first identity is `B_FSS B_FSS^* L_sp^(-1)j=j`; the second follows by
moving the adjoint and using the same identity.  This is the operator order
needed by the FSS theorem.  The previous notation `D_FSS*D_FSS^*` was
ambiguous and is replaced by `B_FSS B_FSS^*`.

## 3. Compatibility with the shifted Q3LOCK bond action

The spatial action uses the corresponding signed gradient `G=B_FSS^*`:

```text
(c/2)||G omega||^2 - c< G omega,h>
  = (c/2)||G omega-h/c||^2 - (1/(2c))||h||^2.
```

Since `B_FSS h=j`, the cross term is, up to the fixed orientation sign,
`<j,omega>`; choosing the opposite edge orientation if necessary makes it
exactly `+<j,omega>` in the FSS source convention.  Consequently

```text
(c/2)||h||^2 = (1/(2c))*<j,L_sp^(-1)j>,
```

and the finite-grid estimate remains

```text
log E exp[t*X_(N,L)(a)]
 <= beta*t^2/(2c) * <a,L_sp^(-1)a>.
```

The correction changes only operator names and order.  It does not alter the
`sqrt(epsilon)` source scaling, `J=c`, the zero-sum restriction, the
`2*E(p)` Fourier factor, or the subsequent Duhamel bound.

## 4. Adversarial checks

| objection | disposition | reason |
|---|---|---|
| Set `L_sp=B_FSS^*B_FSS` when `B_FSS` is divergence | **UPHELD AS FALSE** | The divergence maps edges to vertices; the vertex Laplacian is `B_FSS B_FSS^*`. |
| The orientation sign changes the FSS constant | **DISMISSED** | Reversing all edge orientations changes only the signs of `B_FSS`, `G`, and `h`; the norm and Laplacian are unchanged. |
| A constant source may be inverted after adding a pseudoinverse | **UPHELD AS FALSE** | The proof imposes `sum_y a_y=0` and works on `V_0`; no constant-mode estimate is claimed. |
| Correcting operator order changes the infrared denominator | **DISMISSED** | `B_FSS B_FSS^*=G^*G` is the same positive graph Laplacian with eigenvalue `2*E(p)`. |
| The notation correction closes P-09 | **UPHELD AS FALSE** | The finite-grid/Feynman--Kac limit, source UI, Duhamel passage, thermodynamic limit, and external review remain open. |

## 5. Disposition and boundary

The P-09 Poisson-shift note is corrected to use an edge-to-vertex divergence,
its adjoint gradient, and the vertex Laplacian `B_FSS B_FSS^*`.  This removes a
real operator-order ambiguity while preserving every numerical factor and
the T0 research-only status.  No claim card, manuscript, submission package,
or PDF is created.
