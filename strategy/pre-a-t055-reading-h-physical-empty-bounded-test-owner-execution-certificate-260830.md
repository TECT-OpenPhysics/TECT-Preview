# R-441 -- Reading-H physical-empty bounded test owner execution

## Decision

`R-441 / EXP-001286` is a T0, claim-nonbearing TECT-owner input audit. It
keeps the requested orientation
`F_total[G_*] - F_total[E]` and identity-locks the same fifteen fields:
finite-regulator functional, reference, normalization, finite-part
counterterms, regulator/cutoff, physical volume, boundary condition, limit
order, the two branch representations, full tangent, symmetry orbit tangent,
transverse projector, Hessian/error budget and stationarity budget.

The physical-empty branch `E` is preregistered as a named slot, but it is not
admitted: no normalized representative, measure/algebra, boundary
preparation or local no-condensate/clustering criterion is supplied by the
same owner as `G_*`. The P1 zero/disordered reference is explicitly not an
alias for `E`.

The three requested quantities are therefore:

```text
F_total[G_*] - F_total[E]                         BLOCKED_NOT_EVALUATED
full Reading-H stationarity                         BLOCKED_NOT_EVALUATED
symmetry-projected transverse stability             BLOCKED_NOT_EVALUATED
```

This is a blocked input result, not a numerical sign, stationarity or
stability result. No Yang--Mills or mass-gap claim is promoted.

## Exact scope and executed evidence

- Owner: TECT / Reading-H Gaussian-Hartree covariance candidate `G_*`.
- Comparison: exactly `F_total[G_*] - F_total[E]`.
- Contract: fifteen fields, locked to R-427/R-420 by hash-pinned authorities;
  values remain unsupplied in one common parent.
- Empty branch: `E` preregistered, `admitted=false`,
  `BLOCKED_NOT_INSTANTIATED`; zero and P1 aliases rejected.
- Primary input audit: `13/13` assertions pass.
- Independent reversed-field control: `13/13` assertions pass.
- Hostile contract mutations: `7/7` rejected.
- Integrated verifier: `19/19` pass; Lean R441 compiles.

No energy difference, derivative, Hessian, or limit was evaluated because the
finite evaluation gate is false.

## Assumptions

- The six hash-pinned R-427/R-420/R-418/R-170/R-169/EXP-000790 authorities
  are the current owner boundaries.
- All three tests require one common regulated parent and the stated sign
  orientation.
- Locking a field name preserves the contract but does not invent its value.
- A physical-empty branch requires an admitted normalized state or
  configuration and a physical preparation criterion beyond a zero label.
- Missing owner data is a valid bounded-test stop condition, not a physical
  nonexistence theorem.

## Missing assumptions

- A hash-pinned finite `F_total` whose domain contains both `G_*` and `E`.
- A normalized, admitted `E` representative with measure/algebra, boundary
  preparation and a no-condensate or clustering criterion.
- Common reference, normalization, finite parts and renormalization
  conditions.
- Fixed regulator/cutoff, physical volume, boundary condition and explicit
  thermodynamic/continuum limit order.
- Deterministic maps for both branches, a full admissible tangent and an exact
  symmetry orbit tangent.
- A transverse projector, regulated Hessian, stationarity residual budget and
  numerical/limit error budgets.

## Adversarial review

1. **Zero-reference substitution.** Replacing `E` with zero or the P1
   disordered reference is rejected. Disposition: **UPHELD-OPEN**.
2. **Owner substitution.** Combining the Reading-H covariance owner with a
   different finite parent is rejected. Disposition: **UPHELD-OPEN**.
3. **Contract drift.** Removing or changing any of the fifteen fields is
   rejected. Disposition: **UPHELD-OPEN**.
4. **Finite-part/scalar shift.** An unspecified counterterm or scalar shift
   cannot instantiate a missing state-dependent branch. Disposition:
   **UPHELD-OPEN**.
5. **Stationarity overreach.** Covariance-owner stationarity cannot become
   full-field stationarity without the full tangent and residual budget.
   Disposition: **UPHELD-OPEN**.
6. **Transverse stability overreach.** No Hessian infimum is formed without
   the common orbit tangent, projector and error budget. Disposition:
   **UPHELD-OPEN**.
7. **Physical promotion.** A blocked input audit is not a physical-vacuum,
   Yang--Mills or mass-gap result. Disposition: **UPHELD-OPEN**.

## Boundary and next unlock

R-441 records only that the requested physical-empty bounded test cannot be
evaluated under the current owner state. The next unlock is one
owner-approved, hash-pinned finite parent containing both branches, followed
by frozen common finite parts, regulator, volume, boundary, limit order,
tangent, orbit projector and error budgets. Only then may the unchanged three
tests be run.

Evidence level: `T0 / EXECUTED APPEND-ONLY TECT-OWNER INPUT-ADMISSIBILITY
AUDIT; ALL THREE PHYSICAL QUANTITIES BLOCKED_NOT_EVALUATED`.

Non-claims: no sign for `F_total[G_*] - F_total[E]`; no full Reading-H
stationarity; no symmetry-projected transverse stability; no identification of
`E` with zero, P1, a Gaussian state or an equilibrium phase; no physical
vacuum, Yang--Mills, mass-gap, C6, Sector-A, Pre-A, thermodynamic, continuum,
OS/KMS/GNS, Hamiltonian spectral or absolute-energy conclusion.
