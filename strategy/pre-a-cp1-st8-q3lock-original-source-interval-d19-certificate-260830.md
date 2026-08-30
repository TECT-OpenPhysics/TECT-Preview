# R-438 -- V=2, d=19 original-source interval

`R-438 / EXP-001283` is a T0, claim-nonbearing finite continuation of the
R-436 source-interval route. It keeps the hash-pinned R-419 rational
oscillator fixture and the directed `mpmath.iv` propagation contract, while
increasing the cutoff to `d=19`. The row is fixed before the formal run as
the beta-8, right-orientation unconditional one-site marginal (emission
ordinal zero).

## Exact finite scope

- volume `V=2`, cutoff dimension `d=19`, Hamiltonian dimension `361`;
- beta `8`, right orientation, unconditional one-site Gibbs marginal;
- tail threshold `4`, core indices `5..13`, tail indices `0..4,14..18`;
- source assembled from the hash-pinned R-419 rational fixture;
- exchange/global-parity blocks `[100,81,90,90]`;
- 50-point-digit eigendata, 45-digit interval endpoints and 80-digit interval
  arithmetic;
- fixed probes `4.5 < gap < 4.6`, rejection probe `4.7`, matrix-width budget
  `1e-6`, and bracket-width budget `0.3`.

The row rule and probes are manifest-pinned and are not selected from the
resulting gap. The primary directed interval lane passes `59/59`. Its
residual Rayleigh enclosure is

`[4.51952079482277882931908765479724576244692466,
 4.51952079482279788665653301331650135134669314]`.

The maximum residual-matrix interval width is
`2.63568403984893987213859405798723143872630983e-8`, below `1e-6`. The
interval lies inside the frozen probes and rejects the `4.7` probe.
Hamiltonian residual and Gram upper bounds are
`1.04227424917154243980964855684542951653437286e-40` and
`8.29609617665392593267489237339381184888682063e-42`; coordinate residual
and Gram upper bounds are
`1.51476881245442667960191853367209491931449538e-43` and
`1.63556216629051938120264334498420803889953303e-43`.

The non-importing NumPy control passes `12/12` with gap
`4.5195205287393385`, and the hostile lane rejects `8/8` mutations. The
integrated verifier passes `15/15`; Lean `R438.lean` compiles and its
registry hash is pinned.

## Assumptions

1. The hash-pinned R-419 rational oscillator fixture is unchanged and is the
   exact finite source at `V=2,d=19`.
2. Exchange and global Fock-parity symmetries commute with the finite source
   Hamiltonian, so the four declared blocks preserve its finite spectrum.
3. The R-433 polar-correction and Gibbs-kernel perturbation inequalities
   remain valid after the d=19 residual and Gram checks.
4. The unconditional row is the normalized one-site marginal of the finite
   Gibbs diagonal, and the fixed tail threshold is four.
5. The interval Cholesky and Rayleigh certificates use the same symmetric
   compressed residual enclosure.
6. The `4.5/4.6/4.7` probes and `0.3` bracket allowance were frozen before
   the formal d=19 run by the declared next-step probe rule after R-436.

## Devil's-advocate review

- **Dimension or row mismatch:** the d=19 block count and unconditional row
  cardinality are checked independently and in Lean; a cutoff substitution
  is hostile-rejected. **DISMISSED-FINITE.**
- **Normalization or threshold failure:** directed intervals contain unit mass,
  positive entries, and separate every declared core/tail entry from
  threshold four. **DISMISSED-FINITE.**
- **Cancellation or conditioning:** the same interval enclosure feeds the
  Cholesky and Rayleigh tests, with an explicit matrix-width budget; the float
  lane is only a control. **DISMISSED-FINITE, OPEN-UNIFORM.**
- **Post-selection of a favorable row or probe:** ordinal zero, beta eight,
  right orientation, and the next-step probe values are fixed in the manifest
  before the formal interval run. **DISMISSED-PROTOCOL.**
- **Independent numerical instability:** the independent lane uses a separate
  NumPy reconstruction and agrees with the directed interval; it is not used
  as the interval proof. **DISMISSED-FINITE.**
- **Physical promotion:** no common Q3 core, history transfer, physical
  reference or Yang--Mills map is supplied. **UPHELD-OPEN.**

## Decision and boundary

Advance only this finite original-source datapoint as
`ORIGINAL_SOURCE_INTERVAL_CERTIFIED` at T0. The d=19 row gives a third
cutoff datapoint and a changed certified support, but it does not close
residual reuse, cutoff/volume/phase/exhaustion uniformity, a common core,
history transfer, OS/KMS/GNS reconstruction, a physical sector, or a
continuum limit. It gives no physical-empty energy sign, Reading-H
stationarity, symmetry-projected transverse stability, C6, Sector-A, Pre-A,
Yang--Mills or mass-gap result.

The next mathematical gate is an independently fixed larger cutoff or volume
with a predeclared increasing-core rule and an owner-approved tail modulus.
The d=17--d=19 finite datapoints cannot by themselves establish that
uniformity.

**Proven in:** [R-438 manifest](pre-a-cp1-st8-q3lock-original-source-interval-d19-manifest.json),
[primary run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_d19/primary.json),
[independent run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_d19/independent.json),
[hostile run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-original_source_interval_d19/hostile.json),
[integrated run](../claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-original_source_interval_d19/integrated.json),
and [Lean R438](../verification/lean/Tect/R438.lean).
