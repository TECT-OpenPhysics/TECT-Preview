# R-472 — A2/R-157-R-158 Lean cross-check certificate

## Result and boundary

`R-472` (`EXP-001347`) is a T0, claim-nonbearing additive sidecar for the
already accepted finite conditional results `R-157` and `R-158`.  The pinned
Lean 4.32.1 entrypoint kernel-checks the exact rational identities used for the
R-157 energy/radial gaps, the Class-II input determinant, and the R-158 internal
characteristic polynomial, affine-square completion, coexistence charge and
transition constants.  The independent Fraction lane reconstructs the same
values from the hash-pinned A1 parameters without importing the primary lane.

This does not replace or enlarge the R-157/R-158 analytic theorem.  Lean sees
only the encoded rational propositions; it does not prove the PDE, variational
domain, Galerkin passage, gradient-flow continuation, physical charge, source
owner, observation map, continuum limit, physical vacuum, Pre-A, Sector-A,
QFT, Yang–Mills, gravity, or mass-gap statements.

## Fixed inputs and method preservation

The A1 P1 manifest, A2 PDE manifest, and R-157/R-158 manifests are hash-pinned
in `strategy/a2-r472-lean-crosscheck-manifest.json`.  The established T-054
forward route, T-059/T-061 observation-first inverse route, owner order,
stopped-loop rules, and promotion firewalls are asserted unchanged.  No new
dynamics, physical assumption, candidate, source owner, or claim-tier change is
introduced.  The current owner state therefore remains the previously recorded
fail-closed empty state.

## Exact checked core

- `g = 719818750025582338837/5400000000000000000000 > 1/8` and
  `kappa = 2101675000076747016511/8100000000000000000000 > 1/4`;
- R-157 shell completion, total mass and Class-II determinant `1/50`;
- R-158 characteristic coefficients
  `t^3-(2/5)t^2+(223/5000)t-3/3125`;
- `rho* = 43/216`, `Q* = 11008/27`, coexistence drop `1849/86400`,
  saddle-node drop `1849/64800`, and the positive radial numerator on
  `0 <= theta <= 1`.

These are exact finite rational consequences only.  The existing source
authorities remain the owners of the hypotheses and analytic interpretation.

## Verification

The primary lane, independent lane, hostile mutation lane, integrated lane,
and Lean compilation all pass.  The hostile lane rejects sign, denominator,
density, charge, tier, claim-bearing, method, missing-field, and Lean-marker
mutations.  The package issues no PDF and no new negative record because this is
a short arithmetic sidecar rather than a gate-level synthesis note.

Reproduction commands from the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a2_r472_lean_crosscheck.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a2_r472_lean_crosscheck_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a2_r472_lean_crosscheck_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/a2_r472_lean_crosscheck_verify.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

## Adversarial review

1. **Could the sidecar be read as a new theorem?** Rejected: the manifest is
   T0 and claim-nonbearing, and it names the existing R-157/R-158 authorities.
2. **Could exact rational agreement hide a changed functional?** Rejected: all
   four authority hashes and method-preservation flags are checked.
3. **Could Lean compilation be promoted to a physical or continuum result?**
   Rejected: the non-claims and missing-assumption lists explicitly fence off
   PDE, owner, physical, QFT, Yang–Mills and limit conclusions.
4. **Could a malformed arithmetic constant pass?** Rejected: primary and
   non-importing independent derivations must agree and the hostile lane rejects
   each tested mutation.

## Next gate

Keep the existing methods and owner order active.  The next mainline advance is
a real source-owned dynamics/observation packet and its common-core and uniform
estimate checks.  Until those inputs exist, retain the fail-closed owner state
and do not repeat blocked physical-empty tests.
