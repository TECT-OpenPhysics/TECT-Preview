# R-486 Certificate: Nonzero-Q Matter-Density Cylinder Compatibility

## Result identity

- Result: `R-486`
- Exploration: `EXP-001378`
- Task: `T-054`
- Audit: `PAH-MATTER-CYLINDER-GENERATOR-001`
- Contract: `PAH-OMC-006`
- Verdict: `EXACT_NONZERO_Q_MATTER_DENSITY_CYLINDER_COMPATIBILITY`
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
- `strategy/pa-hyp/PAH-OMC-006-matter-cylinder-v1.json`
  SHA-256 `cb1c84e320d2bd24b430ec2b8f19ef9467e3564e1f2a3cd820487730946ddad5`
- `strategy/pa-hyp/PAH-OMC-006-matter-cylinder-manifest.json` pins all four
  authorities and `verification/lean/Tect/R486.lean`.

PAH-OMC-006 is a researcher-owned successor.  It adds no PAH term, move,
counterterm, rate rescaling, projection, physical identification or limit.

## Exact proposition and scope

The carrier is the genuine PAH-OMC-004 two-row strip.  The comparison is the
neutral coordinate inclusion `J_(2,3): G_2 -> G_3`; both first squares are
already split, so the newly split frontier at column 2 is outside the anchor
neighbour closure.  The observable is the bounded matter-density cylinder
`f(x)=ell_a` at `a=(0,0)`, together with its indicator `1_{ell_a=1}`.

The finite fixture uses the unchanged displayed PAH functional and midpoint
rate with `K=2`, `M_s=M_psi=1`, `Q=1`, `epsilon=1/2`, `beta=nu=1`,
`R_max=1`, `m2=0`, and all displayed couplings used here equal to one.  One
radial occupation quantum is placed at exactly one of `a,b,c,d`; all patch
apertures, phases and links are enumerated, and newly added coordinates are
neutral.  The domain has 32,768 states.

For each state, every directed radial-transfer root on `h00`, `v0` and `d0`
is enumerated.  The exact root tuple is

```text
(patch_state, edge, source, target, Delta F, mobility^2,
 delta ell_a, -beta Delta F/2).
```

The primary and independent lanes each enumerate 49,152 root rows.  Their
canonical row digest is
`716610a6a4694d963e079d4c890ce355f995add1f5f3ad12241f6ce7c2ce35eb`
at both `G_2` and `G_3`.  Thus the complete list of nonzero contributions to
the generator of `ell_a` agrees rootwise on this finite domain.

The earlier `G_1 -> G_2` boundary is retained as a control, not silently
included in the proposition.  With the quantum at `b` and all displayed
labels neutral, the `h00: b -> a` transfer has `Delta F_G1=0` and
`Delta F_G2=-1`, an exact difference of `-1`.  This is the explicit boundary
failure caused by the newly present `d1` covariant term and prevents a
premature all-level claim.

## Verification package

- Primary: `20/20 PASS`, 32,768 states and 49,152 root rows.
- Non-importing independent: `12/12 PASS`, same state and root counts and
  the same G2/G3 digests.
- Hostile: `4/4 PASS`, all `9/9` mutations rejected.
- Integrated: `18/18 PASS`.
- Lean 4.32.1: `verification/lean/Tect/R486.lean` compiles; registry metadata
  and source firewall pass.

Reproduction from the repository root:

```text
python codes/foundations/pah_omc006_matter_cylinder.py
python codes/foundations/pah_omc006_matter_cylinder_independent.py
python codes/foundations/pah_omc006_matter_cylinder_hostile.py
python verification/scripts/pah_omc006_matter_cylinder_verify.py
Set-Location verification/lean; & "$env:USERPROFILE/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe" env lean Tect/R486.lean
```

The four run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc006-matter-cylinder/`.

## Assumptions and missing assumptions

Assumptions are the hash-pinned PAH functional and move conventions, the
PAH-OMC-004 strip incidence, the finite `Q=1` fixture, the neutral inclusion,
and the pointwise `ell_a` cylinder.  The result uses only finite
counting-measure rates and external stochastic Markov time.

Still missing are a total gauge-equivariant state map for arbitrary fine
matter/link cylinders, a common invariant algebra beyond this cylinder, a
source-authorized family of nonzero-`Q` transport maps for all cutoffs and
volumes, and a regulator/volume-uniform interaction estimate in the inherited
limit order.  None is silently supplied by the finite replay.

## Adversarial review

1. **Could `G_1 -> G_2` be declared stable by extrapolation?** **DISMISSED.**
   The exact `0` versus `-1` boundary defect is recorded and the proposition
   starts only at `G_2 -> G_3`.
2. **Could the matter cylinder ignore a frontier covariant term?** **DISMISSED.**
   The full PAH energy is recomputed before and after every anchor-incident
   transfer; the support audit includes `d1` where the endpoint closure needs
   it.
3. **Could the nonzero charge be vacuous or changed by inclusion?** **DISMISSED.**
   Every state has one radial quantum and neutral added coordinates preserve
   the exact charge.
4. **Could the midpoint rows be fitted after seeing `Delta F`?** **DISMISSED.**
   The exponent and endpoint mobility are recomputed from the unchanged PAH
   formula, and hostile mutations reject fitting and mobility changes.
5. **Does this finite cylinder prove a global common core or uniform limit?**
   **UPHELD AND BLOCKED.**  It covers one finite cylinder and fixture only;
   arbitrary cylinders, volume and limits remain open.

## Non-claims and next question

This result does not close the active T-054 gate and is not retroactive
evidence that PAH-001 already contained the refinement map.  It establishes
no global common dynamics, uniform estimate, ordered limit, physical sector,
Pre-A, spacetime, gravity, QFT, Yang--Mills, continuum, mass gap or TOE
conclusion.  Markov time is not quantum real time, proper time or Lorentzian
time.

The single next question is whether several matter and link cylinders can be
placed in one finite common-core class and then given a source-authorized,
regulator/volume-uniform interaction estimate, rather than adding isolated
finite fixtures.
