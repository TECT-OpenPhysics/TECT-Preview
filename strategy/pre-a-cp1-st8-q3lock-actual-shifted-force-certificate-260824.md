# Actual finite-Q3 shifted-force certificate

## Scope

For one Q3-lock edge, the force divided by `lambda` is

`a^3 - (3/2)a^2 b + a b^2 - (1/2)b^3`.

After the source shift `(a,b) -> (a+u,b+v)`, the sums of absolute
coefficients at source degrees one, two and three are exactly `12`, `12` and
`4`. For an onsite cubic and three Q3 neighbours this gives

`(3g+36lambda) Q^2 S + (3g+36lambda) Q S^2 +
(g+12lambda) S^3`,

where `Q` and `S` are the finite-field maximum amplitudes. The spatial linear
force contributes at most `6 c S`. Primary SymPy and independent Fraction
lanes verify the exact identity and every site/species in a side-2 finite
three-dimensional lattice fixture. R219 checks the coefficient arithmetic.

## Finding

This is the first actual Q3 force estimate in the current chain, rather than a
supplied abstract recurrence. It closes only one shifted-force evaluation. It
does not show that repeated commutators or Duhamel histories preserve the same
source type, energy topology, or first-passage decay. All thermodynamic and QFT
gates therefore remain open.

## Adversarial review

- Force convention: UPHELD; the edge derivative and linear spatial term are
  separately explicit.
- Global maxima: UPHELD; `Q,S` are finite global maxima, not a local common-core
  seminorm.
- One-step versus history: UPHELD; no repeated-history claim is made.
- Lean: UPHELD; R219 is scalar coefficient arithmetic only.
- QFT promotion: UPHELD; no KMS, GNS gap, continuum or Pre-A result follows.

## Reproducibility

Run the primary and independent scripts, then the integrated verifier. The
integrated verifier executes both lanes and `lake env lean Tect/R219.lean`, and
stores the three JSON artefacts under the C6 claim run directory.
