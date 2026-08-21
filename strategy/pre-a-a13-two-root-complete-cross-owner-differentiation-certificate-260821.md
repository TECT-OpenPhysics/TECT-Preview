# R-178: complete cross-owner phase differentiation

## Status

R-178 is a T0, claim-nonbearing finite phase-differentiation checkpoint. It
extends the R-177 incidence ledger; it is not an A13 or Sector-A closure.

## Complete cross-owner

For two roots `k` and `2k`, the finite owner retains three independently
coefficiented cross blocks:

`field-field = a1*a2*(c1*c2+s1*s2)`

`current-current = w1*w2*a1*a2*(c1*c2+s1*s2)`

`ordered-field-current = a1*a2*(w2-w1)*(s1*c2-c1*s2)`.

The complete finite cross is `f*field-field + v*current-current +
o*ordered-field-current`, with registered coefficients `f=2`, `v=3`, and
`o=5`. The R-174 fixture has field and current value zero and ordered value
`-1`; the ordered block is therefore not removable by evaluating only that
fixture.

## Lean identities and exact phase derivatives

Lean proves `complete_cross_d1` and `complete_cross_d2`. With
`D1 cos(delta)=-sin(delta)`, `D1 sin(delta)=cos(delta)`, the first derivative
is

`-(f+v*w1*w2)*a1*a2*(s1*c2-c1*s2)
 + o*a1*a2*(w2-w1)*(c1*c2+s1*s2)`.

The second root derivative is its negative. Their sum is exactly zero, as
required by the global phase orbit; this is a symmetry identity, not a phase
selection theorem. At the registered ordered-active phase the ordered term
contributes nonzero derivative `5`, so dropping it changes the differentiated
owner.

The primary SymPy lane binds the chart to the actual R-176 roots and R-177
incidence result. The independent lane recomputes all rational values with the
Python standard library only. The Lean file has no `sorry`, `admit`, `axiom`,
or `unsafe` escape.

## Adversarial boundary

The integrated mutation suite rejects deleting the ordered block, replacing
the actual roots by placeholders, identifying phase differentiation with a
scalar sign, dropping the current block, claiming global phase cancellation
selects a physical phase, marking A13/Sector-A closed, replacing an authority
hash, or inserting a Lean escape token. The result does not determine a
production sign, heat/forest/complement/returned-low terms, source/sextic
one-use bounds, T-050, A13, Nelson, an interacting measure, physical-empty
comparison, removal/continuum limits, Sector-A or Pre-A closure.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_two_root_complete_cross_owner_differentiation.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_complete_cross_owner_differentiation_independent.py --output %TEMP%\r178-independent.json
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_complete_cross_owner_differentiation_verify.py --staged --no-store
```

No R-178 PDF is issued. The next action is to add heat, complement,
historical-low, forest and returned-mean terms and then test the R-125
future-variance, source and sextic windows without reusing a cross block.
