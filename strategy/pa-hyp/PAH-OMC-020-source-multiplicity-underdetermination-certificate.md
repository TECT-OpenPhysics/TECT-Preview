# PAH-OMC-020 / R-527 source-link multiplicity certificate

## Question and scope

R-527 asks whether the immutable PAH-001 text determines one finite link-root
generator strongly enough for the PAH-OMC-020 temporal comparison.  The audit
uses only the already hashed PAH-OMC-004 finite incidence witness; it does not
add a carrier or import the OMC-004 successor theorem.  PAH-001, its displayed
functional, original rates, Gibbs normalization, state, external Markov time,
and the j-before-n order remain byte-frozen.

## Frozen sources

| Source | SHA-256 | Role |
|---|---|---|
| `strategy/pa-hyp/PAH-001-v1.json` | `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37` | immutable functional and move prose |
| `strategy/pa-hyp/PAH-OMC-004-v1.json` | `38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c` | existing five-edge/two-face witness |
| `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json` | `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3` | active j-before-n temporal target |

The PAH-001 move prose says “one link multiplied by zeta_K or
zeta_K^(-1)” and sums over roots, but contains no duplicate, multiplicity,
invalid-move, or root-measure convention.  The omitted fields are checked
directly in the source JSON rather than inferred from a later successor.

## Exact witness

The OMC-004 fine witness contains the closed triangular face `[0,1,4]`.  At
the declared finite fixture `K=2`, `epsilon=1/2`, `beta=nu=1`, and unit
`kappa_g`, set all apertures and links to their neutral values and flip edge
`0`.  The three endpoint stiffnesses are derived from the displayed
`J_e(s)=2/(s_v+s_w)`:

```
J_e = 2,  J_p = 2,  Delta F = 2*(1-(-1)) = 4,
m^2 = (1/2)*(1/2) = 1/4,  m = 1/2,
Delta f = (1-(-1))-(1-1) = 2,
c = (1/2) exp(-Delta F/2) = (1/2) exp(-2).
```

The observable `f=1-Re(U_p)` is gauge invariant because the face is closed;
the audited anchor automorphism group is the identity, so it is anchor
invariant.  The two source-compatible completions are:

* **A, labelled-sign channels:** retain `LK(edge=0,sigma=+1)` and
  `LK(edge=0,sigma=-1)` as two directed labels and pair them as inverses.
* **B, deduplicated involution:** retain the single coincident flip map and
  take it as its own inverse.

Both use the same state map, energy increment, mobility, midpoint rate and
finite normalization.  The only difference is the unspoken root
multiplicity.  One root contributes `exp(-2)` to `L f` at the witness state;
therefore `L_A f=2 exp(-2)`, `L_B f=exp(-2)`, and
`L_A f-L_B f=exp(-2)>0`.  Thus the displayed PAH-001 prose does not select a
unique finite generator or semigroup.

## Verification

| Lane | Result |
|---|---:|
| primary | `PASS`, 38/38 |
| non-importing independent | `PASS`, 35/35 |
| hostile | `PASS`, 17/17, 6/6 mutations rejected |
| integrated | `PASS`, 33/33 |
| Lean 4.32.1 | `PASS`, 13 registered exact declarations |

The Lean file proves the rational stiffness, Wilson increment, midpoint
exponent, involutive flip and strict positivity of the generator gap.  The
Python lanes pin all three sources and reject channel collapse, altered face
normalization, open-link promotion, fitted rates, parent drift and physical
promotion.  No lane imports the primary implementation into the independent
or hostile reconstruction.

## Decision and boundary

Decision: `HOLD_FOR_EVIDENCE`, classification `auxiliary_support`,
`claim_bearing=false`, `active_gate_change=false`, and
`physical_promotion=false`.

This is a precise source-definition underdetermination witness, not a
universal no-go: a future source owner can fix one multiplicity convention and
then be audited.  Until that packet is hash-pinned, the PAH-OMC-020 N2a
common-space map and all N2b/N2c/N4/N2d semigroup passages remain open.  The
result does not prove or disprove any particular future completion.

No physical Pre-A, spacetime, event-horizon, QFT, gravity, Yang--Mills,
continuum, mass-gap or TOE conclusion follows.  Markov time remains external
stochastic time.

## Reproduction

```text
python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination.py --check
python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_independent.py --check
python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_hostile.py --check
python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination_verify.py --check --lean-cache E:\Dev\TECT\verification\lean\.lake\packages
```

Reopen only when a source-authorized packet fixes root labels/multiplicities,
invalid-move behavior, root measure and a PAH-specific energy-intertwining
map, or when one of the frozen source hashes changes.
