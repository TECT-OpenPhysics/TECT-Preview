# R-488 certificate — PAH-OMC-008 multi-cylinder local compatibility

## Exact proposition

The separately versioned researcher contract PAH-OMC-008 keeps the displayed
PAH-001 functional, move families, mobility and midpoint normalization fixed.
On the PAH-OMC-004 two-row strip, the neutral inclusion J_(2,3) is tested on
the finite K=2, M_s=M_psi=1, Q=1 fixture. The joint cylinder is
`(ell_a, ell_d, H_0, H_1)`, where H_0 and H_1 are the two closed split-triangle
Z_2 holonomies. Radial roots incident to either matter anchor and both sigma
channels on all five patch links are retained.

## Source pins

| source | SHA-256 |
|---|---|
| PAH-001 | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| PAH-OMC-004 | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| PAH-OMC-005 | `c779edafc99604047767864f14a2ea0840a7d96f8d5a2f7266bcbdfd2aea6ae5` |
| PAH-OMC-006 | `cb1c84e320d2bd24b430ec2b8f19ef9467e3564e1f2a3cd820487730946ddad5` |
| PAH-OMC-007 | `7e4621abecb577855f740b52c14c83bbfd43eb6b0b30b0b9197e7baa9503280a` |
| PAH-OMC-008 | `b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a` |
| PAH-OMC-008 manifest | `83df59e369f2d10dc9c98b05210bff3fc39eb0055936a799953bda4696b02be2` |
| Lean R488 normalized | `dbee3260ae77e9c094ad811b1fa1b27e48b2505e9527919c0160562f287c6d1b` |

## Reproduction and outcome

```text
python codes/foundations/pah_omc008_multi_cylinder.py
python codes/foundations/pah_omc008_multi_cylinder_independent.py
python codes/foundations/pah_omc008_multi_cylinder_hostile.py
python verification/scripts/pah_omc008_multi_cylinder_verify.py
lake env lean Tect/R488.lean
```

The primary lane passes 25/25 assertions and the independent lane passes
16/16. The hostile lane rejects 12/12 mutations. The integrated verifier
passes 17/17, including the pinned Lean 4.32.1 compile. The fixture contains
32,768 states, 90,112 retained radial roots and 327,680 retained link roots,
for 417,792 roots total. The G_2 and G_3 canonical row digest is
`d46a6997029e19e24fb39d492d3f66c312fe048066fffcb712de46cbfb852a80`.
The inherited G_1 -> G_2 matter-transfer control remains Delta F=0 versus
-1.

## Boundaries

This is T0 claim-nonbearing finite/local structural evidence. It does not
provide a source-owned production dynamics, a global common algebra, a
regulator/volume-uniform estimate, an infinite-volume generator, an ordered
limit, or a physical sector. It makes no Pre-A, spacetime, event-horizon,
gravity, QFT, Yang--Mills, continuum, mass-gap, cosmic-origin or TOE claim.
Markov time remains external stochastic time. The next evidence contract is a
source-authorized multi-face/multi-anchor common-core packet with one uniform
interaction envelope.
