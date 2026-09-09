# PAH-OMC-020 mesh-to-uniform transfer

## Decision

`PASS` / `auxiliary_support` for `R-545`.  The scalar mesh inequality is
verified for the unchanged PAH-001 finite stationary correlations.  Together
with the R-543 deterministic-time modulus and continuity of the exact R-512
target correlation, it gives a conditional compact-time uniform envelope.
The required mesh-pointwise ordered convergence is not proved here, so this
checkpoint does not advance the active T-054 gate.

## Frozen statement

Keep the PAH-001 functional, original rates, labelled Gibbs state, external
stochastic Markov time, sampled local cylinder correlations, and registered
`j`-before-anchored-`n` order unchanged.  For one stabilized local pair `f,g`,
assume the R-543 finite modulus

```text
|C_(n,j)(f,g;t)-C_(n,j)(f,g;s)| <= M_fg |t-s|.
```

Let `C_inf(t)=<f,T_min(t)g>` be the fixed R-512 minimal-form target supplied
by R-530, with modulus of continuity
`omega_inf(delta)=sup_{|t-s|<=delta}|C_inf(t)-C_inf(s)|`.  If a finite mesh
`G_delta` covers `[0,T]` with radius `delta`, then for every retained finite
pair `(n,j)`:

```text
sup_(0<=t<=T)|C_(n,j)(t)-C_inf(t)|
  <= max_(q in G_delta)|C_(n,j)(q)-C_inf(q)|
       + M_fg*delta + omega_inf(delta).
```

Therefore, if ordered mesh-pointwise convergence holds for every fixed mesh,
one may first choose `delta` so the two modulus terms are small and then take
the registered ordered limit on the finite mesh.  This is a transfer lemma,
not a proof of its mesh-pointwise premise.

## Evidence and replay

The primary exact-rational lane uses `T=1`, `delta=1/10`, `M_fg=3`,
`omega_inf=1/20`, and mesh error `1/100`, giving the exact envelope `9/25`.
The independent non-importing lane uses `T=3/2`, radius `1/8`, `M_fg=5/2`,
`omega_inf=3/40`, and mesh error `1/20`, giving `7/16`.  The hostile lane
rejects omission of either modulus, mesh coverage, the finite modulus, the
registered order, or the source-owner/mesh-open conditions.  Lean 4.32.1
checks the rational triangle envelope, strict refinement, and both fixtures.

```text
python -X utf8 verification/scripts/pah_omc020_mesh_uniform.py --check
python -X utf8 codes/foundations/pah_omc020_mesh_uniform_independent.py --check
python -X utf8 codes/foundations/pah_omc020_mesh_uniform_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_mesh_uniform_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Primary `27/27`, independent `16/16`, hostile `15/15`, integrated `30/30`.

## Adversarial review

1. **A finite mesh estimate silently proves all-time convergence.**  Rejected.
   The finite modulus and target continuity only transfer a separately assumed
   mesh-pointwise limit; the premise remains open.
2. **R-543's finite modulus identifies the R-512 target.**  Rejected.  R-543
   supplies equicontinuity only; no common space, path law, or finite-to-target
   identification is imported.
3. **The mesh can be chosen after the limit or after fitting the data.**
   Rejected.  `delta`, the covering mesh, and the order are fixed before the
   finite error is taken in the stated conditional implication.
4. **The target's continuity is a PAH finite conclusion.**  Rejected.  It is
   an input from the fixed R-512 spectral target recorded by R-530, not a
   finite PAH identification.
5. **External Markov time has become physical time.**  Rejected.  The variable
   remains stochastic bookkeeping only.

## Remaining gate

The single next question is whether a source-authorized common-space or
path-space packet proves ordered PAH correlation convergence at every finite
time-mesh point for the unchanged PAH-001 dynamics.  Until that packet and
the R-512 finite-to-target identification are supplied, this result remains
conditional auxiliary support.  There is no physical Pre-A, spacetime, QFT,
gravity, continuum, Yang--Mills, mass-gap, or TOE conclusion.
