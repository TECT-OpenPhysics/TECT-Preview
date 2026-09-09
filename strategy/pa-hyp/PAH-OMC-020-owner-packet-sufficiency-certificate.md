# PAH-OMC-020 owner-packet sufficiency bridge

## Decision

`HOLD_FOR_EVIDENCE` for the actual PAH route, with a conditional sufficiency
theorem recorded as auxiliary support.  No PAH-001 field, rate, state, carrier,
regulator, time or limit order was changed.

## Conditional theorem

The packet contract has ten required fields:

1. owner authority and provenance;
2. root labels, multiplicities, duplicate-transition and root-measure semantics;
3. a measure-compatible common realization or equivalent path map;
4. local-cylinder `N1` recovery;
5. `N2b` liminf and recovery;
6. `N2c/N4` compact-time boundary escape;
7. `N2d` identification with the R-512 minimal form;
8. full-domain fixed-`n` `J(n,j)` control;
9. anchored `D(n)` control;
10. primary, independent, hostile and Lean manifests.

Assuming those fields are source-authorized and jointly compatible, together
with

```text
0 <= err(n,j) <= J(n,j) + D(n),
J(n,j) -> 0 at fixed n, and D(n) -> 0 in the anchored order,
```

the exact nested conclusion follows: for every compact external Markov-time
interval and epsilon, choose an anchored `N`, then a fixed-`n` threshold for
each `n >= N`, and obtain the local-correlation error below epsilon for every
later `j`.  This is the precise logical bridge needed by the mainline.

## Why the mainline is still held

The current corpus does not instantiate the antecedent.  R-552 leaves root
multiplicity and root measure source-underdetermined.  R-539/T-063/T-064 are
intake contracts rather than a source-authorized common-space packet.  R-536
does not supply full-domain target identification, and R-548 is only the
amplitude-only radial sector.  Therefore the conditional theorem cannot be
promoted to full PAH-OMC-020 convergence.

The primary verifier passes 19/19 checks, the non-importing independent replay
passes 17/17, hostile mutations pass 10/10, the integrated verifier passes
22/22, and four Lean theorems compile.  The Lean result covers logical packet
admission and the epsilon implication only; it does not formalize the missing
analytic estimates.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_owner_packet_sufficiency.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_sufficiency_independent.py --check
python -X utf8 codes/foundations/pah_omc020_owner_packet_sufficiency_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_owner_packet_sufficiency_verify.py --check
```

Lean:

```text
lake env lean Tect/PahOmc020OwnerPacketSufficiency.lean
```

## Next single question

Can a versioned source-authorized packet satisfy all ten fields simultaneously
while preserving the exact PAH-001 bytes and the `j`-before-`n` order?  Until
then, do not repeat radial or finite-carrier calculations.

No full PAH-OMC-020 convergence, infinite-volume process, continuum, physical
Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion is
claimed.  External Markov time remains stochastic bookkeeping.
