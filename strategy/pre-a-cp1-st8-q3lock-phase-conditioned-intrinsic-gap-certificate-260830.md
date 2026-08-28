# R-405 certificate - phase-conditioned intrinsic gap and capacity split

## Scope

R-405 is a T0, claim-nonbearing finite checkpoint under EXP-001250.  It
continues R-404 by separating the intrinsic kinetic graph into three pieces:
within-phase coercivity on the negative and positive physical-coordinate
sectors, cross-phase conductance, and any neutral central level.  The split is
made after sorting the finite one-site q spectrum; no central level is silently
assigned to either phase.

For a conditional law `pi` and the q-basis momentum matrix `p`, the tested
conductance is

```
c_ij = (pi_i + pi_j)|p_ij|^2/(2 chi).
```

The full graph uses all edges.  Each induced sector graph restricts both `pi`
and `p` to one sign sector and renormalizes the restricted law.  The cross
quantity is

```
K_cross = sum_{i in minus, j in plus} c_ij,
```

and the neutral mass is the conditional mass of the levels between the two
sectors.

## Finite verification

The primary lane enumerates eight finite Q3 Gibbs systems: volume two with
dimensions `4,5,6,8,10,12`, and volume three with dimensions `4,5`.  It uses
beta in `{1/2,1,2,4,8}`, both left/right collar orientations, every prefix
conditional row, and the complete lower/upper spectrum split.  The primary
passes `1178/1178` assertions over `80` profiles and `1030` conditional rows.
The non-importing independent lane passes `1088/1088` with the same aggregate
values.  The hostile lane passes `5/5`, the integrated verifier passes `33/33`,
and Lean R405 compiles.

The aggregate finite ranges are:

| quantity | minimum | maximum |
|---|---:|---:|
| full intrinsic gap | 0.6310329497027756 | 6.229495058532403 |
| smaller induced sector gap | 1.5773625260965005 | 20.555978652063708 |
| cross-sector capacity | 0.11650039514772156 | 1.222041249326006 |
| phase mass (either sign) | 0.010133814803601744 | - |
| neutral central mass | 0 | 0.3870415227365262 |

The minimum full gap decreases across the beta stress from
`1.0022812277674598` at beta `1/2` to `0.6310329497027756` at beta `8`, while
the minimum induced sector gap remains between `1.5773625260965005` and
`1.5800889283816102`.  This finite separation is evidence for two distinct
scales: a global mode can be softer than either within-phase graph, so a
phasewise proof must not use the global gap as a proxy for sector coercivity.
It is not evidence that either scale is uniform.

## Adversarial review

1. **Partition convention.**  The lower and upper sectors are defined from the
   sorted physical q spectrum; an odd cutoff leaves its central level neutral.
   The sector counts and disjoint union are checked for every system.
2. **Restricted normalization.**  Each sector law is renormalized before its
   generalized eigenvalue is computed.  Using the unnormalized restriction
   would change the gap and is not permitted by the lane.
3. **Global versus phasewise gap.**  Full and induced gaps are retained as
   separate fields.  The observed sector floor above the global floor is not
   converted into a comparison theorem.
4. **Cross-phase bottleneck.**  Cross conductance is summed independently of
   the sector gaps.  Deleting all cross edges produces a second zero mode in
   the hostile representative, so phase coupling cannot be omitted.
5. **Kinetic identification.**  Replacing `p` by the diagonal q operator gives
   zero graph edges in the hostile lane, while the genuine momentum graph is
   connected and has positive gap.
6. **Finite and physical boundary.**  The data are finite Gibbs conditional
   rows only.  No source, phase-selection, cutoff, volume, exhaustion,
   common-core, common-alpha, OS/KMS/GNS, mass-gap, continuum, C6, Sector-A or
   Pre-A conclusion follows.

## Decision and next gate

R-405 advances a new finite route split.  It shows that the intrinsic graph
gap used by R-404 contains a potentially softer global phase-switching mode
and a more robust within-sector scale on this finite grid.  The route should
therefore seek a phase-conditioned common-core lower bound for the induced
sector form, while treating cross-sector capacity as a separate phase
selection/tunnelling obligation.  R-399 shell transfer may only use this split
after both the sector form and the phase boundary condition are controlled.

The next mathematical gate is an analytic sector Poincare estimate with
cutoff/volume/source uniformity and a matching control of neutral mass and
cross-sector capacity.  A finite positive profile is not such an estimate.

## Boundary

No cutoff-independent or volume-independent sector gap, phase-selection
theorem, common core, common alpha, Hamiltonian-to-OS/KMS identification,
broken-sector GNS gap, continuum, C6, Sector-A or Pre-A result is claimed.

Proven in the manifest, primary/independent/hostile scripts, integrated
verifier, Lean entrypoint, scope note and saved run artefacts.
