# R-487 certificate — joint matter/closed-face holonomy cylinder

## Exact proposition

R-487 / EXP-001381 audits a separately hashed researcher-owned successor
contract, PAH-OMC-007, composed with the immutable PAH-001 functional and the
PAH-OMC-004 diagonal strip.  The finite fixture is

```
K=2, M_s=M_psi=1, Q=1, epsilon=1/2, beta=nu=1,
R_max=1, m2=0, lambda_4=eta_6=g=lambda_s=kappa_s=kappa_D=kappa_g=1.
```

The common cylinder is the pair `(ell_a,H_0)`, where `a=(0,0)` and `H_0` is
the Z_2 character of the first split triangle with oriented edges `h00`,
`v1`, and `d0^{-1}`.  The closed-face gauge shift cancels exactly.  The
neutral inclusion `J_(2,3):G_2 -> G_3` retains all patch coordinates and adds
neutral remote coordinates.

Every one of the 32768 Q=1 patch states is enumerated.  The retained roots
are the 49152 valid anchor-incident radial roots and the 196608 directed
`LK(h00,sigma)`, `LK(v1,sigma)`, and `LK(d0,sigma)` channels, for 245760 rows.
Both K=2 labels `sigma=+1` and `sigma=-1` remain distinct channels.  Exact
root tuples contain the full local energy increment, endpoint mobility
square, both joint-coordinate increments, and the unchanged midpoint rate
exponent.  The streamed G_2 and G_3 row digest is

```
941059ded832a7804228c739707418bc2998f44c819e1ddbbea970e35b697c32
```

The local difference is assembled from exactly the changed displayed
PAH-001 terms (endpoint onsite/covariant terms for radial roots; covariant
edge and incident Wilson-face terms for link roots).  Bounded full-energy
recomputations agree with these local differences at every audited sample.

## Evidence and reproduction

Primary: 25/25.  Non-importing independent: 16/16.  Hostile: 11/11
mutations rejected.  Integrated: 17/17, including Lean R487 compilation.
The gauge audit checks all 32 patch link configurations against all 16 patch
gauge assignments (512 transformations).

```text
python codes/foundations/pah_omc007_joint_holonomy_cylinder.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/primary.json
python codes/foundations/pah_omc007_joint_holonomy_cylinder_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/independent.json
python codes/foundations/pah_omc007_joint_holonomy_cylinder_hostile.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/hostile.json
python verification/scripts/pah_omc007_joint_holonomy_cylinder_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc007-joint-holonomy-cylinder/integrated.json
Set-Location verification/lean; & "$env:USERPROFILE/.elan/toolchains/leanprover--lean4---v4.32.1/bin/lake.exe" env lean Tect/R487.lean
```

The contract hash is
`7e4621abecb577855f740b52c14c83bbfd43eb6b0b30b0b9197e7baa9503280a`.
Parent hashes are PAH-001
`03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`,
PAH-OMC-004
`38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c`,
PAH-OMC-005
`c779edafc99604047767864f14a2ea0840a7d96f8d5a2f7266bcbdfd2aea6ae5`, and
PAH-OMC-006
`cb1c84e320d2bd24b430ec2b8f19ef9467e3564e1f2a3cd820487730946ddad5`.

## Adversarial boundary

The hostile lane rejects promotion of a pure link coordinate or open-face
path, deletion of Wilson or covariant terms, collapse of the two K=2 link
channels, extension across the known G_1 -> G_2 matter defect (`0` versus
`-1`), fitted midpoint rates, conditional fibre averaging, replacement of
Markov time by quantum time, and physical or global-uniform promotion.

This is T0 finite/local structural evidence only.  The contract is a
researcher proposal and supplies no source-authorized family, common global
algebra, regulator/volume-uniform estimate, infinite-volume generator, or
ordered limit.  It makes no physical Pre-A, spacetime, event-horizon,
gravity, QFT, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE claim.

## Next evidence contract

The next single question is whether several independent face holonomies and
multiple nonzero-Q matter anchors can share one source-authorized support
envelope beyond this one closed face.  Reopen the uniform lane only after a
new hash-pinned owner contract supplies that multi-cylinder transport,
nonzero-Q state transport beyond the fixture, a common invariant core, and a
regulator/volume-uniform estimate in the inherited limit order.
