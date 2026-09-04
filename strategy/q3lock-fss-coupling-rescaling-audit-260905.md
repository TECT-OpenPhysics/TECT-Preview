# Q3LOCK FSS coupling-rescaling audit

**Status:** T0 proof-text correction; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Scope:** finite-grid FSS source shift and bond square completion  
**PDF:** deferred until content freeze and final release review

## 1. Question and strict boundary

The FSS theorem uses an edge field whose divergence is the vertex source.  The
bond square-completion proof also uses an edge field, but that field is divided
by the spatial coupling.  Several earlier Q3LOCK notes used one symbol for both
objects and consequently wrote two incompatible identities at once.  This
audit separates the fields and repairs the affected proof text.

This is an operator-normalization correction only.  It does not alter the FSS
source theorem, the Q3LOCK model, any numerical bound, any claim tier, or the
publication status.  It does not close P-06, P-09, the pressure bridge, the
strict cusp, or DLR multiplicity.

## 2. Two edge fields, with their domains

Let `G:V_0 -> E` be the signed vertex-to-edge gradient, let
`B_FSS=G^*:E -> V_0` be the FSS edge-to-vertex divergence, and let
`L_sp=G^*G=B_FSS B_FSS^*` on the zero-sum vertex space `V_0`.  For a zero-sum
source `j`, define the FSS theorem field

```text
h_FSS = G L_sp^(-1) j = B_FSS^* L_sp^(-1) j.
```

Then

```text
B_FSS h_FSS = j,
||h_FSS||^2 = <j,L_sp^(-1)j>.
```

This is the field that appears in the FSS theorem display
`(2J)^(-1)||h_FSS||^2`.

The Q3LOCK spatial bond has coupling `c>0`.  The field in the completed
square is instead

```text
b = h_FSS/c.
```

Consequently,

```text
c*(G omega,b) = <j,omega>,
(c/2)||b||^2 = (1/(2c))*<j,L_sp^(-1)j>.
```

Equivalently, writing the unscaled field `h_FSS` directly,

```text
(c/2)||G omega||^2 - <j,omega>
  = (c/2)||G omega-h_FSS/c||^2
    - (1/(2c))||h_FSS||^2.
```

The two fields are related but not identical.  Keeping this distinction makes
both the FSS theorem and the bond completion algebraically correct.

## 3. Consequence for the finite-grid bound

For the ordinary scaled-history coordinates

```text
s_y=sqrt(epsilon)*(x_(y,k))_k,
eta_y(t)=t*sqrt(epsilon)*(a_y*u)_k,
```

the source is `eta(t)` and `h_FSS(t)=G L_sp^(-1)eta(t)`.  Its norm is

```text
||h_FSS(t)||^2 = beta*t^2*<a,L_sp^(-1)a>.
```

The FSS Theorem 2.1 therefore gives, at finite time mesh and finite periodic
volume,

```text
log E_(N,L,0) exp[t*X_(N,L)(a)]
  <= beta*t^2/(2*c) * <a,L_sp^(-1)a>.
```

The variance and nonzero-mode Fourier consequences remain

```text
Var(X_(N,L)(a)) <= beta/c * <a,L_sp^(-1)a>,
Dhat_(N,L)(p) <= 1/(2*beta*c*E(p)),  p != 0.
```

No factor of `c`, `beta`, `epsilon`, or `2` is changed by this correction.

## 4. Files repaired

The following load-bearing notes now use `h_FSS` for the divergence solution
and `b=h_FSS/c` for square completion:

* `strategy/q3lock-p09-constant-source-loop-limit-audit-260905.md`
* `strategy/q3lock-p06-p09-independent-proof-audit-round2-260905.md`
* `strategy/q3lock-fss-gradient-adjoint-notation-correction-audit-260905.md`
* `strategy/q3lock-fss-divergence-incidence-convention-audit-260905.md`

The already-correct finite-grid transfer note
`strategy/q3lock-fss-finite-grid-transfer-check-260904.md` and the
low-temperature preregistration use the rescaled field and serve as comparison
checks.  The exact FSS source factors and the scaled-spin map are pinned in
`strategy/q3lock-fss-theorem-factor-transcription-audit-260905.md`.

## 5. Adversarial checks

1. **The field solving `B_FSS h=j` can also be used unchanged in the square
   completion.**  Rejected: the completion uses `b=h/c` when the bond is
   `c/2||G omega||^2`.
2. **The correction changes the FSS Gaussian constant.**  Rejected: the
   theorem still contributes `(2c)^(-1)||h_FSS||^2`; only the notation for the
   equivalent bond shift is separated.
3. **The source scaling needs an additional factor of eight.**  Rejected:
   `u` is unit norm and the eight components are already in `s_y`.
4. **The correction proves the loop-limit theorem.**  Rejected: source/UI,
   weak grid-to-loop convergence, covariance identification, and thermodynamic
   limits remain independent obligations.
5. **A positive finite-grid bound proves a strict cusp.**  Rejected: the
   nonzero-mode upper bound is only one input to the collective zero-mode lower
   bound and pressure tangent argument.

## 6. Disposition

The coupling-rescaling seam is repaired at T0.  The finite-grid constants and
all scientific scope are unchanged.  Independent FSS applicability, loop,
operator, pressure, source-tangent, claim-lineage, clean-replay, external
referee, and final PDF gates remain open.  No claim card, manuscript, release,
submission, or PDF is created.
