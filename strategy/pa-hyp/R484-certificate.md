# R-484 Certificate: Explicit PAH Generator-Row Locality Replay

## Result identity

- Result: `R-484`
- Exploration: `EXP-001371`
- Task: `T-054`
- Audit: `PAH-GENERATOR-REPLAY-001`
- Sidecar: `PAH-OMC-004-GEN-001`
- Verdict: `EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY`
- Programme status: `HOLD_FOR_EVIDENCE`
- Tier: `T0` claim-nonbearing finite/local structural verification
- Active canonical gate changed: no
- Parent bytes changed: no

## Hash-pinned authorities

- `strategy/pa-hyp/PAH-001-v1.json`
  SHA-256 `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- `strategy/pa-hyp/PAH-OMC-004-v1.json`
  SHA-256 `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`
- `strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json`
  SHA-256 `87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e`
- `strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json` pins the
  sidecar and parent hashes and sets `no_parent_mutation=true`.

The sidecar is a researcher verification packet.  It adds no PAH term, move,
counterterm, projection, parameter, normalization or limit and is not an
external or physical source.

## Exact finite replay

The anchor patch has vertices `a,b,c,d`, edges
`h00=(a,b), v0=(a,c), d0=(a,d), h01=(c,d), v1=(b,d)`, and the two oriented
triangles `[h00,v1,d0^(-1)]` and `[d0,h01^(-1),v0^(-1)]`.  The two-row strip
carriers `G_1` and `G_2` have the same incidence closure at `a`; remote terms
do not contain `a` and therefore cancel in an anchor-aperture energy
difference.

The unchanged PAH midpoint rate is recomputed on the exact finite fixture
`K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1`, with displayed couplings
used at value one where present.  Every four-bit aperture assignment and
five-bit `Z_2` link assignment is enumerated: `2^4*2^5=512` states.  For the
single valid anchor aperture root in each state, the recorded exact row tuple
is

```text
(state, direction, Delta F, mobility^2, Delta s_a,
  Delta 1_{j_a=1}, -beta Delta F/2).
```

The tuple is identical for the level-1 and level-2 patch for all 512 states.
The basis observables `1`, `s_a`, and `1_{j_a=1}` therefore have the same
finite generator contribution on this local cylinder.  The primary lane also
checks the affected term support explicitly (`onsite:a`, `edge:h00`,
`edge:v0`, `edge:d0`, and both triangle terms); the remaining patch terms are
remote to the anchor flip.

## Boundary retained

The preceding square-to-diagonal boundary is not hidden.  At all-zero
apertures and links, raising `a` gives

```text
Delta F_square       =  1/8
Delta F_split(d0=0)  =  1/4
Delta F_split(d0=1)  = -55/36
hidden defect         = 16/9.
```

This is a boundary defect for a split intersecting support.  It is not
averaged away, repaired by a counterterm, or promoted to a global no-go.

## Verification package

- Primary: `30/30 PASS`, 512 exact rows.
- Non-importing independent: `14/14 PASS`, 512 exact rows.
- Hostile: `16/16` mutation cases rejected.
- Integrated: `28/28 PASS`.
- Lean 4.32.1: `verification/lean/Tect/R484.lean` compiles; the registry
  metadata gate passes with no forbidden escape token.

Reproduction from the repository root:

```text
python -X utf8 codes/foundations/pah_omc004_generator_replay.py
python -X utf8 codes/foundations/pah_omc004_generator_replay_independent.py
python -X utf8 codes/foundations/pah_omc004_generator_replay_hostile.py
python -X utf8 verification/scripts/pah_omc004_generator_replay_verify.py
Set-Location verification/lean; & "$env:USERPROFILE/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe" env lean Tect/R484.lean
```

The run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-03-pah-omc004-generator-replay/`.

## Adversarial review

1. **Could the replay be a colour-only copy?** **DISMISSED.**  The retained
   diagonal is a real edge in two Wilson triangle incidences, and the finite
   carrier has five edges and two faces.
2. **Could the row equality come from fitting rates after projection?**
   **DISMISSED.**  Both lanes use the displayed midpoint rate and reject rate
   fitting, conditional averaging and counterterms.
3. **Could the all-zero boundary defect be silently erased?** **DISMISSED.**
   The exact `16/9` defect is stored and checked by both arithmetic lanes and
   Lean; equality is asserted only for the post-boundary local patch.
4. **Does 512-state local equality imply a global uniform or continuum result?**
   **UPHELD AND BLOCKED.**  The enumeration is one finite Q=0 cylinder and
   supplies no source-authorized nonzero-Q, volume-uniform or ordered-limit
   estimate.
5. **Does this identify a physical sector?** **DISMISSED.**  Markov time is
   external stochastic time and the sidecar explicitly excludes physical,
   Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap and TOE
   interpretations.

## Non-claims and next question

This result is not retroactive evidence for PAH-001 alone and does not close
the active gate.  It proves exact generator-row equality only for the declared
anchor-aperture cylinder on finite `G_1/G_2` patches.  No common infinite-
volume automorphism, global uniform estimate, ordered limit, physical vacuum,
Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass-gap or TOE result
follows.

The single next question is whether a separately source-authorized nonzero-Q
geometric family can carry the same explicit row-locality mechanism with a
uniform interaction-closure estimate, without modifying PAH-001.

