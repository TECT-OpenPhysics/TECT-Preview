# QFT dynamics candidate screen — Math98 Langevin/Onsager–Machlup route

**Status:** T0 route screen; no current dynamics owner is selected.

This note records a bounded audit of QFT-adjacent legacy material. The
canonical source root remains the configured `Contents` tree; the occurrences
below are discovery material and are not admitted current authorities.

## Sources and exact scope

1. `Contents/Docs/math/TECT-Math98-AddJ-pre-transition-quantisation.tex.txt`
   SHA-256
   `48f72ec6ab85bf65ad6cbfd98ba99ec70fbcad45b3a89afc1448e2700efd7ba2`.
   Lines 30–38 write a pre-transition free energy
   `|grad Psi|^2 + mu2 |Psi|^2 + lambda |Psi|^4 + gamma (Delta |Psi|^2)^2`
   and the generic Langevin equation `dPsi/dt = -delta F/delta Psi + eta`.

2. `Contents/Docs/math/TECT-Math98-AddE-Onsager-Machlup-cross-check.tex.txt`
   SHA-256
   `7136cceb90617ad21c0da3c72f75c2b155a5e254383dc25eded06d91345b5d3`.
   Lines 30–50 use `dPsi/dt = -Gamma delta F/delta Psi + zeta` and an
   Onsager–Machlup action. Lines 269–287 explicitly leave rigorous
   pre-transition quantisation and the exact coefficient open.

3. `Contents/Docs/math/TECT-Round-3-4-second-order-audit.tex.txt` SHA-256
   `83db1b8e2d93a1c83b6ae1fe8de333d891582f18d36c1ea60547ad27097acc85`.
   Lines 134–144 classify the kinetic coefficient `Gamma` as an external
   parameter and retain only a conditional status.

## Crosswalk to the current owner

The current A1 convention is
`K(q) = mu2 + Y (q^2 - q0^2)^2`, while the full production functional also
contains family, lock, shell, and Class-II terms. The Math98 formulas do not
provide that shell kernel, the current vector/internal field map, or the
Class-II current placement. No source supplies the R-192 fields
`heat_generator`, `heat_semigroup`, `filtration`,
`raw_current_spatial_intertwiner`, or
`production_one_use_q_ledger`.

The repository does contain a separate conditional deterministic candidate:
A3 records the canonical full-production P1/P2 gradient flow on the fixed
three-torus, conditional on A2-H3. That package is a PDE discretisation and
continuum result; it does not identify a stochastic heat semigroup, root
filtration, raw-current spatial intertwiner, or one-use `q_k` ledger for the
R-192/A13 owner. It is therefore a relevant QFT/PDE dynamical baseline, not a
completion of the missing production owner.

## Decision and boundary

The specific Math98 Langevin/Onsager–Machlup import is parked as a discovery
candidate, not selected as TECT dynamics. Importing it would add an external
kinetic coefficient, a different static functional, and an unproved current
interface. This is not a universal impossibility theorem for a future QFT
construction. A future candidate must be derived from the hash-pinned A1/A7
owner, satisfy all R-192 slots, and pass the Lean, independent, and integrated
lanes. No A13, T-050, Sector-A, Pre-A, physical-empty, real-time, removal, or
continuum conclusion follows.

## Conditional finite candidate selection (EXP-000973)

The declared comparison dynamics is now the finite Galerkin stochastic
quantisation of the hash-pinned `F_ref` functional with beta>0 and identity
mobility,

`dX_t = -grad F_ref,N(X_t) dt + sqrt(2 beta^(-1)) dW_t`.

R-197 and its Lean theorem `gibbs_residual_zero` verify the formal finite
detailed-balance cancellation for this choice.  R-200 independently shows
that the same static Gibbs density and Hessian are compatible with distinct
positive mobility rates, so identity mobility is a declared comparison choice
and not a deduction from static A1 data.  The candidate therefore does not
replace the missing nonlinear A1 production owner: R-192 still requires
`heat_root_incidence`, a root filtration and conditional replicas, a
`raw_current_spatial_intertwiner`, and a once-owned nonnegative production
`q`-ledger.  Until those slots are hash-pinned, this candidate is finite and
conditional only; no KMS, OS, thermodynamic, continuum, real-time, Sector-A,
or Pre-A conclusion follows.

## Math385 discovery-only comparison (EXP-000974)

The configured Contents source `TECT-Math385-RG1-Dynamic-Universality-Class-
Brazovskii-Model-A.tex.txt` (SHA-256
`fc97145b67ace58fa3ceedfe89d37364ff7d7b412d08cd325ed06a0ebfe17921`)
proposes a non-conserved Brazovskii Model A-star equation for a real scalar
free energy.  The linked Math395 adversarial audit
(`3da0c5563de39c853e4e581d7d7991c70f18a4f08abfea378911415daf0160b1`)
classifies the assignment as conditional on the binding A1 axiom and does not
turn it into an independently derived current owner.  Neither source supplies
the current complex three-component Class-II production heat/root incidence,
root filtration, conditional replicas, raw-current spatial intertwiner, or
once-owned q-ledger.  Math385 is therefore discovery-only and is not imported
into the selected finite `F_ref` identity-mobility comparison or the canonical
A1/A13 owner.
