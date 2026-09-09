# PAH-OMC-020 coordinate-preserving terminal-fibre obstruction

## Decision

`HOLD_FOR_EVIDENCE` for the full PAH-OMC-020 objective, with an exact
route-local obstruction recorded for one candidate N2a realization.  The
candidate is the coordinate-preserving density-ratio lift from the original
unsplit terminal square to the split-cell fibre.  Its inverse density ratio is
unbounded on an allowed amplitude ray.  This does not rule out a
source-authorized non-coordinate realization and is not a negative result for
the local temporal correlation target.

## Frozen source and scope

| source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md` | `49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf` |

The functional, labelled Gibbs normalization, OMC-004 terminal-square/split
geometry, original rates, external stochastic Markov time and `j`-before-`n`
order are unchanged.  The witness uses the retained old labels
`h0=h1=vx=vy=+1`, all apertures `s=1`, phases `+1`, and amplitudes
`x0=y0=0`, `x1=y1=A` with `A>=0`.  No diagonal is dropped and no boundary
interaction is averaged away.

## Exact derivation

The source edge rule gives `J_e=2/(1+1)=1` on this fibre.  The old square
has zero covariant edge differences and holonomy `+1`, hence

```text
B_square = 0.
```

Retaining the diagonal label `d` produces the two split triangle energies

```text
B_triangle(d=+1) = A^2/2,
B_triangle(d=-1) = A^2/2 + 4.
```

The source Gibbs weights therefore satisfy the exact identity

```text
rho_split(A)/rho_square(A)
  = exp(-A^2/2) + exp(-(A^2/2+4))
  = (1+exp(-4))*exp(-A^2/2).
```

The ratio is positive and strictly decreases for `A>=0`; its reciprocal grows
like `exp(A^2/2)/(1+exp(-4))` and is therefore unbounded.  A uniformly
bounded coordinate-preserving density-ratio multiplier cannot recover the
finite square law from this split marginal on the full allowed amplitude
domain.

This is an obstruction to that particular full-space realization.  It is not
a statement that every abstract `U_n`, weighted-energy map, or local
correlation comparison is impossible.

## Verification

The four lanes were replayed with the following commands:

```text
python -X utf8 verification/scripts/pah_omc020_boundary_kernel_obstruction.py --check
python -X utf8 codes/foundations/pah_omc020_boundary_kernel_obstruction_independent.py --check
python -X utf8 codes/foundations/pah_omc020_boundary_kernel_obstruction_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_boundary_kernel_obstruction_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

| artefact | SHA-256 |
|---|---|
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-boundary-kernel-obstruction/primary.json` | `ec980b0b299361189ad6d5c6a18b33efe45b2a17fc18fbb6a1d1aab1c8090173` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-boundary-kernel-obstruction/independent.json` | `7eaa20d9e95ff2618138426a11bf42195f717cd9a4f151a1bfae1da81a61bf05` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-boundary-kernel-obstruction/hostile.json` | `199bac95be69ca572f7c7486228bba14708baf85067720932d7a32b4acb28711` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-pah-omc020-boundary-kernel-obstruction/integrated.json` | `a1fec839cf7e63b186a65aa408f32b7fa660dab25d44b0d535baaf2f810ccc15` |

Primary and independent arithmetic agree on the closed ratio and the
challenge-dependent inverse witnesses.  The hostile lane rejects diagonal
omission, the one-third face-average mutation, reversal of the ratio
direction, finite-fibre promotion to a universal `U_n` no-go, and physical
time promotion.  The Lean source
`verification/lean/Tect/PahOmc020.lean` (SHA-256
`f269428a0732204cf37cdec2dd9e87ea094329a7150fdfba6b08ffb762ad9b3c`)
compiles under Lean 4.32.1; `split_fibre_ratio_strict_decay` is registered in
`verification/lean/registry.json` (SHA-256
`adc0fff457b4ead10cbfd9468cfe2df56390a9123ae9a957750bddd5e45a6011`).

## Adversarial boundary

1. **Direction and reciprocal.**  The split/square ratio decays; the
   coordinate-preserving recovery multiplier is its reciprocal, which grows.
2. **Normalization.**  The `4` penalty is from two source triangle face terms
   with the source boundary average at unit edge stiffness.  A one-third
   mutation is rejected.
3. **Limit case.**  The arbitrary-challenge argument uses the symbolic
   exponential formula, not a finite-grid extrapolation.
4. **Scope.**  Only the named coordinate-preserving terminal fibre is
   obstructed.  Non-coordinate bounded-energy maps and local-core recovery
   remain open.
5. **Process firewall.**  No rate, state, carrier, regulator, time or limit
   order is changed; no semigroup or physical claim is inferred.

## Next question

Can a source-authorized non-coordinate bounded-energy `U_n`/common-space
realization preserve the same local cylinders and satisfy N2b, N2c/N4 and N2d,
despite this terminal-fibre obstruction to the coordinate-preserving lift?

## Non-claims

- No full PAH-OMC-020 semigroup negative result, Mosco-liminf failure or
  universal comparison-map impossibility is claimed.
- No PAH-001 functional, rate, state, carrier, regulator order or external
  Markov time is changed.
- No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap,
  Yang--Mills or TOE conclusion follows.
