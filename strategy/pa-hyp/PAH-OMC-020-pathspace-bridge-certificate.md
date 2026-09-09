# PAH-OMC-020 path-space bridge certificate

Date: 2026-09-08  
Result: R-520  
Task: T-071  
Verdict: HOLD_FOR_EVIDENCE  
Classification: auxiliary_support (conditional, non-claim-bearing)

## Question and boundary

Can the unchanged PAH-001 finite dynamics reach the PAH-OMC-020 scalar local-correlation target through a projective path-space or martingale-problem comparison, without inventing a common `U_n`? The comparison is kept in the preregistered order: first the `j` limit at fixed `n`, then the anchored `n` comparison. It uses the original external unaccelerated Markov time on compact finite intervals, the labelled Gibbs state and the R-510 transfer normalization. No rate, functional, state, carrier, projection, regulator, counterterm, or time interpretation is changed.

The bridge budget is written as

```text
local correlation error
  <= projective state error (R-510)
   + finite local-generator stabilization (R-493)
   + explicit connected-word boundary tail (R-517)
   + target-process/minimal-form identification defect.
```

The first three terms are finite or conditional inputs already registered. The last term is deliberately not set to zero.

## Pinned source inputs

All source bytes were checked before the lane runs:

| Source | SHA-256 |
|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc013-full-q-eventual-intertwining/integrated.json` | `8d005bea7ee33111712f58a32046cdb254f77bc8c17d8eb1a470abcc2adbbbc7` |
| `strategy/pa-hyp/PAH-OMC-017-result-v1.json` | `4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb` |
| `strategy/pa-hyp/PAH-OMC-019-result-v1.json` | `82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd` |
| `strategy/pa-hyp/PAH-OMC-020-root-overlap-result-v1.json` | `9e357158eb6de66bb776b2d674964ddf9fb16547409ac36f8dd254154082bc11` |
| `strategy/pa-hyp/PAH-OMC-020-duhamel-attribution-result-v1.json` | `67825022b3db1078387534baacb818fdf60778ce19f4fe81514484a25cf7cb5d` |
| `strategy/pa-hyp/PAH-OMC-020-projective-correlation-result-v1.json` | `2bfc217bfa7785726d7342ce5ec80d1adab5be030c561d4e6681d49f64cf3248` |

The finite footprint is recomputed from R-516 as 16 roots per column, 4 edge slots, radius 2, overlap branching `b=144`, and the explicit two-copy value `b_eff=288`. The primary width-two fixture gives first-root bound 112, horizon `T=1/4`, and tail distances 128, 192, 256. The independent width-three fixture gives first-root bound 128 and horizon `T=1/6`. These are exact arithmetic test fixtures, not physical constants.

## Verification

The primary lane passed 41/41 checks. The non-importing independent lane passed 33/33 checks. The hostile lane passed 20/20 shortcut and mutation controls. The integrated verifier passed 36/36 checks, including shared source-hash agreement, status firewalls, AST non-import checks, registry/declaration checks, and Lean compilation. Lean 4.32.1 compiled eleven finite rational declarations in `verification/lean/Tect/PahOmc020Pathspace.lean`; its only diagnostic is the non-fatal unused `h_state` linter warning on the triangle fixture.

The reproducible commands are:

```text
python -X utf8 verification/scripts/pah_omc020_pathspace_bridge.py --check
python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_independent.py --check
python -X utf8 codes/foundations/pah_omc020_pathspace_bridge_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_pathspace_bridge_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
lean verification/lean/Tect/PahOmc020Pathspace.lean
```

The stored run artefacts are:

| Run | SHA-256 |
|---|---|
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-pathspace-bridge/primary.json` | `40964f269323e04c77d369f2bdb25abe3276585eba1b3c27873d2bc2b8acb509` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-pathspace-bridge/independent.json` | `48eec745e99e15769ff240ef8ac5f6fa02d100d208e7ca6a1d8985bdd4126f94` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-pathspace-bridge/hostile.json` | `f90cbd2b9adba8cd4630b52f9d8f1a1aa24ccb442d3d9150afce88b4b8933ee6` |
| `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-pathspace-bridge/integrated.json` | `dff4da7f5070cb411b263a634f674bb13ce5a2ba64b9913af578ec3131c8d8a4` |

The Lean source is registered at SHA-256 `79febf8159a1f40cd7f2b66a63e1de91a330a9fd99decb892400f9d44773fa6b` with declarations `bridge_triangle`, `bridge_budget_nonnegative`, `source_overlap_formula`, `source_two_copy_formula`, `source_first_root_width_two`, `independent_first_root_width_three`, `tail_ratio_fixture`, `tail_ratio_primary_fixture`, `state_fixture_pair_decreases`, `independent_state_fixture_pair_decreases`, and `explicit_target_defect_fixture`.

## Missing premises and adversarial review

The result does not supply any of the following four premises:

1. A source-grounded projective path-space or martingale-problem construction for the infinite local process.
2. Existence, non-explosion, and uniqueness of that process on the R-512 cylinder domain for the unbounded rates.
3. An unconditional N2c/N4 boundary-escape estimate for the evolved local test, rather than the conditional finite-fibre attribution.
4. Equality of the resulting process/form limit with the R-512 minimal closed extension, rather than another closed extension.

The hostile lane explicitly rejects: treating a finite tail as an infinite theorem; inferring `U_n` from R-510 state convergence; dropping the boundary or two-copy factor; treating form closure as process uniqueness or minimality; reversing or diagonalizing the preregistered order; and promoting external Markov time to physical time. These objections remain upheld against promotion, not silently discharged.

## Scoped conclusion

The finite scalar bridge contract is algebraically coherent and provides a reusable decomposition that isolates the exact target defect without synthesizing `U_n`. It is therefore recorded as conditional auxiliary support. The PAH-OMC-020 ordered semigroup objective remains `HOLD_FOR_EVIDENCE`; no active T-054 gate changes.

Next single question: can a source-authorized projective path-space construction prove non-explosion and uniqueness for the R-512 cylinder generator and identify its semigroup with the R-512 minimal closed form? Reopen only on such a source/process packet or on an exact non-explosion/uniqueness counterexample; do not repeat the finite radial, word, or coordinate-fibre fixtures.

## Non-claims

- No PAH-OMC-020 semigroup convergence theorem or negative result.
- No common `U_n` or Hilbert isometry, weak Gibbs-L2 theorem, N2b liminf/recovery, N2c/N4 unconditional escape, or N2d minimal-form selection.
- No infinite-volume process, continuum limit, physical Pre-A, spacetime, QFT, gravity, Yang-Mills, mass-gap, or TOE conclusion.
- External Markov time is not quantum real time, proper time, or Lorentzian time.
