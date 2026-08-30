# R-436 -- V=2, d=18 original-source interval

`R-436 / EXP-001281` is a T0, claim-nonbearing finite continuation of the
R-435 source-interval route. It keeps the hash-pinned R-419 rational oscillator
fixture and the directed `mpmath.iv` propagation contract, while increasing
the cutoff to `d=18`. The row is fixed before interval evaluation as the
beta-8, right-orientation unconditional one-site marginal (emission ordinal
zero).

## Exact finite scope

- volume `V=2`, cutoff dimension `d=18`, Hamiltonian dimension `324`;
- beta `8`, right orientation, unconditional one-site Gibbs marginal;
- tail threshold `4`, core indices `5..12`, tail indices `0..4,13..17`;
- source assembled from the hash-pinned R-419 rational fixture;
- exchange/global-parity blocks `[90,72,81,81]`;
- 50-point-digit eigendata, 45-digit interval endpoints and 80-digit interval
  arithmetic;
- fixed probes `4.3 < gap < 4.4`, rejection probe `4.5`, matrix-width budget
  `1e-6`, and bracket-width budget `0.2`.

The row rule is manifest-pinned and is not selected from the resulting gap.
The primary directed interval lane passes `58/58`. Its residual Rayleigh
enclosure is

`[4.37258598994761155319421318538070164008480175,
4.37258598994761252488250973347361635144049652]`.

The maximum residual-matrix interval width is
`2.069782066602701971726231375141990933117e-10`, below `1e-6`. The interval
lies inside the fixed probes and rejects the `4.5` probe. Hamiltonian residual
and Gram upper bounds are
`8.3258515872660438709154544026055097086e-41` and
`7.2242770739641236691051423511126412e-42`; coordinate residual and Gram
upper bounds are `1.3918941582845464162611530512601031e-43` and
`1.5512427195339811897416082020640233e-43`.

The non-importing NumPy control passes `12/12` with gap
`4.37258594841633`, and the hostile lane rejects `8/8` mutations. The
integrated verifier passes `15/15`; Lean `R436.lean` compiles and its registry
hash is pinned.

## Assumptions

1. The hash-pinned R-419 rational oscillator fixture is unchanged and is the
   exact finite source at `V=2,d=18`.
2. Exchange and global Fock-parity symmetries commute with the finite source
   Hamiltonian, so the four declared blocks preserve its finite spectrum.
3. The R-433 polar-correction and Gibbs-kernel perturbation inequalities remain
   valid after the d=18 residual and Gram checks.
4. The unconditional row is the normalized one-site marginal of the finite
   Gibbs diagonal, and the fixed tail threshold is four.
5. The interval Cholesky and Rayleigh certificates use the same symmetric
   compressed residual enclosure.

## Devil's-advocate review

- **Dimension or row mismatch:** the d=18 block count and unconditional row
  cardinality are checked independently and in Lean; a d=17 substitution is
  hostile-rejected. **DISMISSED-FINITE.**
- **Normalization or threshold failure:** directed intervals contain unit mass,
  positive entries, and separate every declared core/tail entry from threshold
  four. **DISMISSED-FINITE.**
- **Cancellation or conditioning:** the same interval enclosure feeds the
  Cholesky and Rayleigh tests, with an explicit matrix-width budget; the float
  lane is only a control. **DISMISSED-FINITE, OPEN-UNIFORM.**
- **Post-selection of a favorable row:** ordinal zero, beta eight and right
  orientation are fixed in the manifest before interval evaluation. **DISMISSED-
  PROTOCOL.**
- **Physical promotion:** no common Q3 core, history transfer, physical
  reference or Yang--Mills map is supplied. **UPHELD-OPEN.**

## Decision and boundary

Advance only this finite original-source datapoint as
`ORIGINAL_SOURCE_INTERVAL_CERTIFIED` at T0. It does not close residual reuse,
cutoff/volume/phase/exhaustion uniformity, a common core, history transfer,
OS/KMS/GNS reconstruction, a physical sector, or a continuum limit. It gives
no physical-empty energy sign, Reading-H stationarity, symmetry-projected
transverse stability, C6, Sector-A, Pre-A, Yang--Mills or mass-gap result.

The next mathematical gate is an independently fixed larger volume or cutoff
with a predeclared row rule and an owner-approved tail modulus. Without that
uniform control, this remains a finite calibration only.

**Proven in:** [R-436 manifest](strategy/pre-a-cp1-st8-q3lock-original-source-interval-d18-manifest.json),
[primary run](claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_d18/primary.json),
[independent run](claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_d18/independent.json),
[hostile run](claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-original_source_interval_d18/hostile.json),
[integrated run](claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-integrated-original_source_interval_d18/integrated.json),
and [Lean R436](verification/lean/Tect/R436.lean).
