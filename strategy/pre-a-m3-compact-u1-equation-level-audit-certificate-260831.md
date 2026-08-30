# R-457 certificate: finite compact-U(1) equation-level audit

## Route role and exact scope

`R-457` / `EXP-001330` is a T0, claim-nonbearing addition to the already
recorded `PA-M3-COMPACT-U1-HAMILTONIAN-v0` design candidate.  It checks the
finite equations as written; it does not create a source owner, choose a
dynamics, or alter the established T-054 forward method or the additive
T-059/T-061 observation-first lane.

The finite scope is the periodic cubic lattice `(Z/LZ)^3` for the declared
sizes `L=2,3`, compact U(1) link phases with the parent endpoint convention,
complex `phi,pi`, and the parent Hamiltonian/Gauss expression.  No continuum,
thermodynamic, quantum, or physical-empty interpretation is included.

## Audited identities

The primary and non-importing independent lanes reconstruct site-charge vectors
from link, field, and momentum factors.  They check every oriented plaquette,
every covariant-link term and its four norm products, matter density, current,
Gauss matter factor, and quartic matter factor.  All declared Hamiltonian and
observable monomials have zero site charge; the two terms of the covariant
difference have the same unit charge at the source site.

The same finite contract gives a conditional Noether statement: the displayed
Gauss constraint is neutral, so its surface is preserved if the declared
canonical generator premise is supplied.  This is not an unconditional
source-owned flow theorem.  The antisymmetric self-bracket identity
`{H,H}=0` is checked algebraically.  For every inserted `lambda>0`, real `m^2`,
and tested `x=|phi|^2>=0`, both lanes verify

`lambda*x^2/4 + m^2*x/2 = lambda/4*(x+m^2/lambda)^2 - (m^2)^2/(4 lambda)`.

This is the finite completion-square lower bound used only for the conditional
finite-flow interpretation.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_m3_compact_u1_equation_audit.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_m3_compact_u1_equation_audit_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_m3_compact_u1_equation_audit_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pre_a_m3_compact_u1_equation_audit_verify.py
C:\Users\NaEun\.elan\toolchains\leanprover--lean4---v4.32.1\bin\lake.exe env lean verification/lean/Tect/R457.lean
```

The integrated verifier checks the manifest hashes, exact lane agreement, the
eight hostile mutations, and the pinned Lean declarations.  The run artefacts
are the authority; no PDF is issued at this intermediate lemma.

## Adversarial review

1. **Method overhaul — DISMISSED.**  This is an additive equation audit.  It
   leaves T-054/T-059/T-061, owner order, and promotion firewalls unchanged.
2. **Gauge name leakage — REJECTED.**  Compact U(1) charge cancellation is not
   Yang--Mills or Standard-Model identification.
3. **Noether overreach — UPHELD-OPEN.**  Gauss-surface preservation is
   conditional on the declared canonical generator and a future source owner.
4. **Finite-to-continuum leakage — REJECTED.**  The completion square and finite
   lattice coverage do not supply any limit or common domain.
5. **Observable overreach — REJECTED.**  Neutrality of a formula is not a
   measured, fitted, or holdout prediction; `F_reg` remains a definition only.
6. **Physical-empty substitution — DISMISSED.**  The parent reference `R0` is
   not identified with Reading-H physical empty space.

## Boundary and next gate

The result is `M3_EQUATION_LEVEL_AUDITED_NOT_ADMITTED`: exact finite equation
consistency with a conditional finite-flow statement, but no candidate
admission.  Missing are a versioned source owner, state/ensemble and
uncertainty contract, physical projection, dynamic two-time estimand, complete
`F_reg/F_lim/F_eff/F_obs` map, prospective holdout, and uniform regulator or
volume estimates.  The next gate is owner intake and a candidate-neutral
dynamic discriminator, not another finite equation table.  No Pre-A,
Sector-A, C6, QFT, Yang--Mills, gravity, continuum, physical-vacuum, or
mass-gap conclusion follows.
