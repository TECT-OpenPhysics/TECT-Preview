# R-420 certificate — Reading-H physical-empty bounded test (blocked)

## 1. Result and exact scope

R-420 is a T0, claim-nonbearing TECT-owner bounded test under EXP-001265.
It preregisters the requested comparison

```text
F_total[G_*] - F_total[E]
```

and the associated full regulated Reading-H stationarity and
symmetry-projected transverse stability checks.  The preregistration freezes
the required common finite-regulator functional, reference, normalization,
finite parts, regulator, volume, boundary condition and limit order as
mandatory fields.  It also freezes the candidate representation, the empty
branch representation, the full tangent, the symmetry orbit and the error
budgets as mandatory fields.

The result is **BLOCKED**.  The latest T-055/R-169 owner is a Reading-H
shell/covariance owner, not a hash-pinned finite-volume Hamiltonian functional
with an absolute physical-empty normalization.  The latest R-170 applicability
audit and the EXP-000790 same-H contract both leave the physical-empty branch
to a future, separately normalized constrained or preparation construction.
Thus no numerical energy, stationarity residual or Hessian is evaluated.

The symbol `E` is nevertheless preregistered as a slot.  It is not identified
with zero, the P1 zero/disordered reference, the Gaussian reference, or an
equilibrium phase.

## 2. Frozen owner contract

The candidate is the native Reading-H Gaussian-Hartree covariance owner
`G_*`, with comparison orientation `G_* minus E`.  The contract contains the
following fifteen required fields:

1. finite-regulator functional;
2. reference definition;
3. normalization;
4. finite-part counterterm scheme;
5. regulator and cutoff;
6. physical volume;
7. boundary condition;
8. thermodynamic-then-continuum limit order;
9. finite representation of `G_*`;
10. finite representation of `E`;
11. full admissible tangent;
12. symmetry group and orbit tangent;
13. transverse projector;
14. Hessian form and error budget; and
15. stationarity residual budget.

The owner status is `NOT_FIXED_IN_ONE_COMMON_OWNER`.  The available Reading-H
intensity convention and the name `G_*` are partial entries only; they do not
fill the finite-volume, regulator, boundary or physical-empty fields.  No
finite evaluation is authorized while any required field is missing.

## 3. Physical-empty preregistration

`E` is registered with the declared role “a normalized constrained,
no-condensate or empty-preparation branch in the same parent as `G_*`”.  Its
admission status is `BLOCKED_NOT_INSTANTIATED` and its supplied-field list is
empty.  EXP-000790 requires a state/configuration representative, a measure or
algebra, normalization and finite parts, a boundary preparation, a physical
interpretation, and a local no-condensate or clustering criterion.  None is
provided by the current Reading-H authorities.

Aliasing `E` to the P1 zero/disordered reference is rejected: that reference
has no registered full Reading-H functional or ensemble intertwiner.  A
one-point zero condition would also not establish a normalized physical-empty
branch.

## 4. Three requested verdicts

| Test | Status | Exact blocker |
|---|---|---|
| `F_total[G_*]-F_total[E]` sign | `BLOCKED_NOT_EVALUATED` | no common finite-regulator owner, no admitted `E`, and no absolute physical-empty normalization |
| Reading-H full-tangent stationarity | `BLOCKED_NOT_EVALUATED` | no full regulated tangent or stationarity residual budget; covariance-owner stationarity is insufficient |
| symmetry-projected transverse stability | `BLOCKED_NOT_EVALUATED` | no common symmetry orbit/tangent, transverse projector, regulated Hessian or error budget |

The blocked statuses are a typed input result, not zero values and not
unknown numerical signs.  The executable lanes assert that no numerical
comparison payload is emitted.

## 5. Assumptions and missing assumptions

The audit assumes that R-169 v1.4 and R-170 are the current TECT owner
boundaries, that all three tests use one common regulated parent, that the sign
orientation is `G_*` minus `E`, and that transverse means orthogonal to the
exact declared symmetry orbit tangent.  It also assumes that refusing an
undefined computation is required rather than silently substituting a zero
reference.

Missing assumptions are a hash-pinned common `F_total`, an admitted normalized
physical-empty state/measure/algebra and preparation, common normalization and
finite counterterms, regulator/volume/boundary/limit data, deterministic maps
for both candidates, a full tangent and symmetry projector, and stationarity
and Hessian error budgets.

## 6. Evidence and adversarial review

Evidence level: **T0 / EXECUTED PREREGISTRATION AND INPUT-ADMISSIBILITY AUDIT**.
The primary and non-importing independent lanes inspect the same authority
hashes and contract fields; the hostile lane mutates zero aliasing, owner
substitution, missing finite parts, missing `E`, premature numeric evaluation,
and missing limit order.  Every mutation is rejected.  Lean R420 compiles an
implication-only firewall: an evaluation requires both a fixed owner and an
admitted `E`; the present hypotheses therefore force the blocked verdict.
This Lean file proves no energy, stationarity or Hessian theorem.

The six hostile checks are controls on input integrity.  They are not a
physical no-go result.

## 7. Boundary and next unlock

R-420 does not add a negative result, change a claim tier, issue a PDF, or
advance C6, Sector A or Pre-A.  The next unlock is concrete: provide one
owner-approved hash-pinned finite parent; instantiate `E` with a normalized
state/configuration, boundary preparation and local physical criterion; map
both `G_*` and `E`; and freeze the full tangent, symmetry projector, finite
parts and error budgets.  Then rerun the unchanged three-lane test.

No Yang--Mills statement, mass-gap statement, physical-vacuum identification,
below-empty sign, continuum limit, thermodynamic limit, OS/KMS/GNS conclusion,
or Hamiltonian spectral conclusion follows from R-420.

