# R-485 Certificate: Nonzero-Q Anchor Generator Compatibility

## Result identity

- Result: `R-485`
- Exploration: `EXP-001374`
- Task: `T-054`
- Audit: `PAH-NONZERO-Q-GENERATOR-001`
- Contract: `PAH-OMC-005`
- Verdict: `EXACT_NONZERO_Q_ANCHOR_GENERATOR_COMPATIBILITY`
- Programme status: `HOLD_FOR_EVIDENCE`
- Tier: `T0` claim-nonbearing finite/local structural verification
- Active canonical gate changed: no
- Parent bytes changed: no

## Hash-pinned authorities

- `strategy/pa-hyp/PAH-001-v1.json`
  SHA-256 `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- `strategy/pa-hyp/PAH-OMC-004-v1.json`
  SHA-256 `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`
- `strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-v1.json`
  SHA-256 `c779edafc99604047767864f14a2ea0840a7d96f8d5a2f7266bcbdfd2aea6ae5`
- `strategy/pa-hyp/PAH-OMC-005-nonzero-q-generator-manifest.json` pins the
  three authorities and `verification/lean/Tect/R485.lean`.

PAH-OMC-005 is a researcher-owned successor.  It adds no PAH term, move,
counterterm, rate rescaling, projection, physical identification or limit.

## Exact proposition and scope

The geometric carrier is the PAH-OMC-004 two-row strip.  `G_1` has its first
square split into two triangles with an independent diagonal edge; `G_2` splits
the next frontier square.  The anchor `a=(0,0)` has the same interaction closure
at both levels: vertices `a,b,c,d`, edges `h00,v0,d0,h01,v1`, and the two split
faces.  The incidence therefore changes genuinely (one extra edge and one extra
face relative to the unsplit square), while the anchor closure is stable for
`n>=1`.

The finite fixture uses the unchanged displayed PAH functional and midpoint
rate with `K=2`, `M_s=M_psi=1`, `Q=1`, `epsilon=1/2`, `beta=nu=1`, `R_max=1`,
`m2=0`, and all displayed couplings used here equal to one.  One radial
occupation quantum is placed at exactly one of `a,b,c,d`; all four patch phases,
five patch links and four aperture bits are enumerated.  New vertices in the
`G_1 -> G_2` inclusion carry neutral aperture, zero radial occupation and neutral
link/phase labels, so the fixed charge remains `Q=1`.

For every valid patch state, the common observable is a bounded function of the
anchor aperture `s_a`.  Only `AP(a,+/-)` changes this observable.  Its energy
increment uses exactly the onsite term at `a`, the three incident stiffness and
covariant edge terms, and the two triangle Wilson terms; every other full-strip
term is unchanged by the anchor flip.  The mobility and increment are therefore
functions of the same local coordinates at `G_1` and `G_2`.

The exact row tuple is

```text
(patch_state, direction, Delta F, mobility^2, Delta s_a,
 Delta 1_{j_a=1}, -beta Delta F/2).
```

The proposition proved at this finite scope is: states with identical anchor
closure data have identical tuples at every compared post-boundary level; the
neutral inclusion gives such a pair for all audited `Q=1` states.  The local
finite tail is consequently exactly zero after the first split boundary.

## Verification package

- Primary: `21/21 PASS`, all `32768` nonzero-`Q` patch states.
- Non-importing independent: `16/16 PASS`, all `32768` rows reproduced.
- Hostile: `9/9` mutations rejected.
- Integrated: `17/17 PASS`.
- Lean 4.32.1: `verification/lean/Tect/R485.lean` compiles; registry metadata
  and source firewall pass.

Reproduction from the repository root:

```text
python codes/foundations/pah_omc005_nonzero_q_generator.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/primary.json
python codes/foundations/pah_omc005_nonzero_q_generator_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/independent.json
python codes/foundations/pah_omc005_nonzero_q_generator_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/hostile.json
python verification/scripts/pah_omc005_nonzero_q_generator_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/integrated.json
Set-Location verification/lean; & "$env:USERPROFILE/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe" env lean Tect/R485.lean
```

The four run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc005-nonzero-q-generator/`.

## Assumptions and missing assumptions

Assumptions are the hash-pinned PAH functional and move conventions, the
PAH-OMC-004 strip incidence, the finite `Q=1` fixture, the neutral inclusion,
and the anchor-aperture cylinder definition.  The result assumes only finite
counting-measure rates and external stochastic Markov time.

Still missing are a total gauge-equivariant state map for arbitrary fine
matter/link cylinders, a common invariant algebra beyond this coordinate
cylinder, a source-authorized family of nonzero-`Q` transport maps for all
cutoffs and volumes, and a uniform interaction estimate in the inherited limit
order.  None of these missing inputs is silently supplied by the finite replay.

## Adversarial review

1. **Could the nonzero charge be vacuous?** **DISMISSED.**  Every audited state
   has one radial quantum and the independent lane checks the charge sum.
2. **Could the diagonal be only a colour label?** **DISMISSED.**  `d0` is an
   independent edge in both oriented Wilson triangles and is retained by both
   incidence signatures.
3. **Could rates be fitted after projection?** **DISMISSED.**  Both arithmetic
   lanes compute the unchanged midpoint exponent from the full PAH energy
   increment; the hostile lane rejects a fitted exponent and wrong mobility.
4. **Does exact equality on these rows prove global uniformity?** **UPHELD AND
   BLOCKED.**  It covers only the anchor-aperture cylinder and one finite
   nonzero-`Q` fixture; arbitrary cylinders, volumes and limits remain open.
5. **Does `Q=1` identify a physical sector or time?** **DISMISSED.**  The
   contract is a finite researcher hypothesis with external Markov time only.

## Non-claims and next question

This result is not retroactive evidence that PAH-001 already contained the
refinement map.  It does not close the active T-054 gate and does not establish
a global common-core theorem, a uniform bound, an ordered limit, a physical
sector, Pre-A, spacetime, gravity, QFT, Yang--Mills, a continuum, a mass gap or
TOE conclusion.

The single next question is whether a separately justified common-core class
containing a nontrivial matter or link cylinder can be added with a regulator-
uniform interaction bound, instead of only the anchor-aperture cylinder.

