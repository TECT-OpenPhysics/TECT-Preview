# R-491 certificate — PAH-OMC-011 eventual generator intertwining

## Verdict

`HOLD_FOR_EVIDENCE`.

The unchanged PAH-OMC-004 neutral coordinate projection gives a correct
image-locality buffer, but it is not a total map on the full fixed-`Q=1`
state spaces used by the R-488/OMC-010 common-cylinder declaration.  Therefore
the all-state identity

`L_(n+1) I_(n,n+1) f = I_(n,n+1) L_n f`

cannot yet be formed as an identity of functions on the full fine Gibbs
domain.  This is a domain-definition obstruction, not a numerical rate
counterexample and not a refutation of PAH-001.

## Frozen sources

| source | SHA-256 |
|---|---|
| PAH-001 | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` |
| PAH-OMC-004 | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` |
| PAH-OMC-008 | `b103665b9361c6a4b52b791280ce2503e5aeddbffe67a78d08c4c2a45fc8228a` |
| PAH-OMC-010 | `8386a70a445af90eca9a5f678e9f6c910369a56dca6544f653ac388894850f69` |
| PAH-OMC-010 manifest | `97c9ebb3a28f83f93a3b79de527ce0e57b0be346ef6f77d99e59e7b3fa9ea4e3` |
| R-484 sidecar | `87f5d3ee29b15f57f3e461b4b4064955b5f1ced0ab0bdf2b4763ed0a7ffe3e3e` |
| R-484 manifest | `88a07db1123a229733bdf7ab4fa413d0e6eb903001bc7faa1e44497ae31e9e57` |
| R-491 contract | `244a300c470fa551dc006a7a2d9ba2a7a5d773d2d5cafbe9b777f9266df50020` |
| Lean R491 normalized | `a89600b59d6b5af2cb3b8cafb033ac8869075e34f71c855cc73c3045dc169141` |

## Exact scope and witness

The carrier is the already declared PAH-OMC-004 two-row strip `G_n`, `n>=2`,
with its split triangles and unsplit frontier square.  The functional, move
families, mobility exponent, midpoint rate, Gibbs weight, and parameter path
are copied by hash from PAH-001/OMC-008/OMC-010; no term, rate, counterterm,
average, or carrier is added.

The common algebra is the algebraic union of bounded gauge- and
anchor-automorphism-invariant cylinders in finitely many `ell_v` and closed
face holonomies, including `(ell_a,ell_d,H_0,H_1)`.  The declared generator
domain is the full finite `Omega_(n,Q)` with `Q=1`.

For `n=2`, the fine carrier `G_3` has new vertex `(4,0)`.  The valid fine state
with `ell_(4,0)=1` and all old `ell_v=0` has fine charge `Q=1`, while the
declared projection that drops the new column has retained charge `0`.  Thus
`p_(3,2)` is not a map `Omega_(3,1) -> Omega_(2,1)`.  The same witness exists
for every `n>=2` at `(n+2,0)`.

## What is proved conditionally

For a finite-support cylinder `f`, let `m_f` be the maximum column in its
already defined PAH interaction closure (`m_f=-1` for the constant cylinder).
The exact support buffer is

`N(f) = max(2, m_f + 1)`.

For `n>=N(f)`, the frontier footprint `{n,n+1,n+2}` containing `q_n`, the
new column, and `d_n` is disjoint from that closure.  Hence the R-484 boundary
defect is separated from the support on the neutral-inclusion image.  This is
an image-restricted locality statement only; it does not repair the full
fixed-`Q` domain obstruction.

R-484's exact boundary values remain recorded: coarse `1/8`, fine-even `1/4`,
fine-odd `-55/36`, hidden diagonal defect `16/9`.  The defect is retained,
not averaged or erased.

R-490's `C_sw=540` is used only as the already verified state-weighted
domination input.  It is not used as an intertwining proof.

## Verification

The primary audit passes 19/19 assertions, the non-importing independent audit
passes 16/16, the hostile mutation firewall passes 10/10, the integrated
verifier passes 17/17, and Lean R491 compiles under the pinned Lean 4.32.1
toolchain.  The run artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc011-eventual-intertwining/`.

Reproduce from `E:/Dev/TECT`:

```text
python -X utf8 codes/foundations/pah_omc011_eventual_intertwining.py
python -X utf8 codes/foundations/pah_omc011_eventual_intertwining_independent.py
python -X utf8 codes/foundations/pah_omc011_eventual_intertwining_hostile.py
python -X utf8 verification/scripts/pah_omc011_eventual_intertwining_verify.py
Set-Location verification/lean; lake env lean Tect/R491.lean
```

## Gibbs-L2 scope and next question

The charge-loss witness has positive finite Gibbs weight, but the lifted
observable and its `L2(W)` defect are undefined on that full-domain state.  The
packet therefore does not claim that weak Gibbs-L2 convergence universally
fails; it is blocked until a total fixed-`Q` map or an explicitly authorized
common domain is supplied.  Conditional averaging, rate fitting, a fixed
`R_max` bypass, and a Q=0 substitution are prohibited.

The single next question is: can a source-authorized full-Q common domain (or
an explicitly admitted full-Q refinement map) make `p_(n+1,n)` total while
preserving every unchanged PAH-001 root rate for every finite-support cylinder,
without conditional averaging or changing the model?

No infinite-volume dynamics, continuum limit, physical Pre-A, spacetime,
gravity, QFT, Yang--Mills, mass-gap, cosmic-origin, or TOE conclusion follows.

