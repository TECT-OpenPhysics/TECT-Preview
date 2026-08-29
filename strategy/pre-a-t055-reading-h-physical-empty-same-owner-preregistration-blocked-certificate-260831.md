# R-418 certificate — physical-empty same-owner preregistration boundary

## Result and exact scope

R-418 is a T0, claim-nonbearing TECT-owner input-boundary audit under
EXP-001263. It attempts the requested comparison

```
F_total[G_*] - F_total[E]
```

with one finite-regulator parent, one reference convention, one normalization,
one finite-part prescription, one regulator, one physical volume, one boundary
condition, and one thermodynamic-then-continuum limit order. It also attempts
the associated full-tangent Reading-H stationarity and symmetry-projected
transverse Hessian tests.

The branch symbol `E` is preregistered as a slot for a physical-empty or
empty-preparation state in the same parent. The slot is deliberately not
identified with a zero field, the P1 zero/disordered reference, or `G_*`.
Its admission status is `BLOCKED_NOT_INSTANTIATED` because no state,
normalization, boundary preparation, or physical interpretation is registered
for that slot.

## Authority check

The current R-169 v1.3 authority records the native Reading-H comparison

```
F_RH[Q_BCC,A] - F_RH[G_*] > 0
```

and explicitly records that no sign for `F_RH[G_*]-F_empty` is obtained.
The B1 referee package is a finite shell `Q`-versus-`G_*` result; it does not
provide a physical spatial volume, UV regulator, boundary condition, finite
counterterm trajectory, or absolute physical-empty normalization. R-170 v1.0
reuses that result only at this scope and directs new work to a matched
same-parent `G_*`-versus-empty theorem or a separate Reading-H-to-P1
interface.

The pinned P1 zero/disordered reference is a different side-16 finite parent.
R-169 v1.1 supplies no registered image of `G_*` in that parent and no full
energy or ensemble intertwiner. The A1 manifest also retains an
external-source-audit failure and a declared-functional versus implemented-
residual mismatch. These authorities therefore cannot be combined to create
the requested common functional.

## Preregistration contract and verdicts

The machine manifest freezes the requested fields and marks the contract
`NOT_FIXED_IN_ONE_COMMON_OWNER`. The audit does not evaluate an energy or
Hessian when any required input is absent.

| Test | Status | Exact blocker |
|---|---|---|
| `F_total[G_*]-F_total[E]` sign | `BLOCKED_NOT_EVALUATED` | no common finite-regulator owner; `E` is not admitted; no absolute physical-empty normalization |
| Reading-H stationarity | `BLOCKED_NOT_EVALUATED` | no full regulated tangent; covariance-owner stationarity is not full-field stationarity |
| symmetry-projected transverse stability | `BLOCKED_NOT_EVALUATED` | no common symmetry orbit, transverse projector, regulated Hessian, or error budget |

The evidence level is **T0 / EXECUTED INPUT-BOUNDARY AUDIT**. Primary,
non-importing independent, and hostile mutation lanes verify the same blocker
contract. There is no numerical energy difference, stationarity residual, or
Hessian eigenvalue in this result.

## Assumptions and missing assumptions

The audit assumes that the current native Reading-H G_* owner and the cited
R-169/R-170 boundaries are authoritative, that both states must share one
parent domain and finite prescription, that the sign orientation is
`G_*` minus `E`, and that stationarity is required on the full admissible
regulated tangent.

Missing inputs are a hash-pinned finite `F_total` containing both states, an
admitted physical-empty representative and physical interpretation, common
normalization and finite parts, regulator/volume/boundary/limit data,
deterministic maps for `G_*` and `E`, a full tangent and exact symmetry
projector, and stationarity/Hessian error budgets.

## Adversarial review

The hostile lane tries to (i) alias the P1 zero reference to `E`, (ii) mark a
missing finite-part slot as fixed, and (iii) switch the candidate owner to P1.
Each mutation is rejected by the preregistration validator. It also checks that
no numeric comparison payload is present. These are input-integrity controls,
not a mathematical sign or stability theorem.

## Boundary and next unlock

R-418 does not change the C6 card, close a T-055 gate, add a negative result,
or issue a PDF. It makes the correct next gate explicit: an owner must supply
one hash-pinned common finite-regulator parent, admit `E` with its state and
boundary preparation, map both `G_*` and `E`, and freeze the full tangent,
symmetry projector, finite-part scheme, and error budgets. Only then can the
unchanged primary/independent/hostile lanes evaluate the sign, stationarity and
transverse form. No Yang-Mills or mass-gap conclusion follows at any stage.
