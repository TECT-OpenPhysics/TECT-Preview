# PAH-OMC-025 route-frontier certificate

## Decision

`R-565` records an auxiliary `HOLD_FOR_EVIDENCE` route-dependency result for
`PAH-OMC-020`. The audit does not admit the mainline and does not change the
active gate. It identifies one route-independent cut-set that every permitted
proof route must instantiate before the ordered stationary-semigroup claim can
be re-entered.

The frozen question is whether the existing records, without changing
`PAH-001` or repeating a finite diagnostic, reduce every admissible route to
three required cuts:

1. `S0`: source semantics selecting one finite object and its stationary
   generator;
2. `S1`: one complete comparison and target-identification route; and
3. `S2`: full-domain temporal control in the declared `j`-before-anchored-`n`
   order.

The answer is conditional and negative only in the admission sense: the cut-set
is explicit, but none of the three cuts is currently instantiated by a
source-authorized packet. This is not a universal no-go for an owner-fixed
successor.

## Frozen scope and provenance

The exact immutable inputs are the PAH-001 functional, rates, state, carrier,
external stochastic time, and limit order, plus the registered PAH-OMC-020
records `R-534`, `R-536`, `R-542`, `R-557`, `R-559`, and `R-564`. Their SHA-256
values are recorded in
`strategy/pa-hyp/PAH-OMC-025-route-frontier-result-v1.json` and pinned by the
contract. No new carrier, counterterm, rate fit, abstract oracle, physical
projection, or finite model is introduced.

## Cut-set audit

### S0: source semantics and finite generator identity

The packet must fix root labels and multiplicities, duplicate and invalid
moves, root counting measure, the finite generator, and stationary
normalization. `R-559` is scoped to non-uniqueness of the immutable source
bytes; `R-560` is the current owner-admission boundary. Neither is promoted to
a universal successor no-go. Therefore `S0` is `MISSING`.

### S1: one complete comparison route

The form route requires a common realization, norm/energy control, liminf and
recovery estimates, boundary control, exact `R-512` target identification,
and correlation transfer. The path route requires a common path law,
tightness, generator/form equality, uniqueness, and correlation transfer.
`R-536` and `R-557` leave both field sets incomplete. A radial, finite, or
partial route does not satisfy this cut. Therefore both `FORM_ROUTE` and
`PATH_ROUTE` are `MISSING`.

### S2: full-domain temporal control

The original quantifier order requires a fixed-`n` `J` bound and an anchored
`D` bound, or a source-authorized conditional path/N4 estimate that yields the
same budget. `R-534` keeps the needed terms conditional; `R-542` blocks the
promotion of stationary averages to stopping-time control; `R-564` blocks the
promotion of a finite derivative gap to an anchored-`n` conclusion. Therefore
`S2` is `MISSING`.

The route rule is exactly

```text
admissible = S0 and (FORM_ROUTE or PATH_ROUTE) and S2
```

No partial route is treated as a shortcut.

## Reproducible verification

The primary, independent, hostile, integrated, and Lean artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc025-route-frontier/`.
The replay commands are:

```text
python -X utf8 verification/scripts/pah_omc025_route_frontier.py --check
python -X utf8 codes/foundations/pah_omc025_route_frontier_independent.py --check
python -X utf8 codes/foundations/pah_omc025_route_frontier_hostile.py --check
python -X utf8 verification/scripts/pah_omc025_route_frontier_verify.py --check
Set-Location verification/lean
lake env lean Tect/PahOmc025RouteFrontier.lean
```

The replay results are primary `42/42`, independent `25/25`, hostile `11/11`,
integrated `16/16`, and Lean PASS under the pinned Lean 4.32.1 toolchain. The
Lean file proves the finite Boolean cut-set theorem and the rejection of
partial-route shortcuts; it does not prove the analytic estimates.

## Adversarial boundary

The hostile review rejects five overclaims: treating `R-559` as a universal
no-go, treating `R-564` as a PAH estimate, omitting `S0` after a form proof,
promoting stationary averages to stopping-time control, and calling the
cut-set theorem itself PAH-OMC-020 convergence. All are outside the recorded
scope.

## Re-entry condition and non-claims

Re-open only when one source-authorized, hash-pinned packet instantiates `S0`,
one complete `S1` alternative, and `S2` without changing PAH-001 or the
`j`-before-anchored-`n` order. Otherwise keep the actual route
`HOLD_FOR_EVIDENCE` and do not repeat the existing finite or abstract
diagnostics.

This certificate does not prove ordered convergence, an infinite-volume
process, a common Hilbert or path space, a compensator, a generator, a carrier,
a regulator limit, or any physical conclusion. It makes no claim about
physical Pre-A, spacetime, QFT, gravity, Yang--Mills, continuum, mass gap, or
TOE. Markov time remains external stochastic bookkeeping.
