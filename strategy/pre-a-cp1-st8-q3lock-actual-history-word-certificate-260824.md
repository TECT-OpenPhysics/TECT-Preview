# Actual finite-Q3 local history-word certificate

## Scope

For one species coordinate of the canonical Q3 lock, set the three incident
species coordinates to zero.  The onsite quartic plus the three incident lock
edges then restricts exactly to

`D_on(q,a) = G*(q^4-(q-a)^4)/4`,

with `G = g + 3*lambda`.  For one selected spatial bond use

`D_bond(q,r,a) = c*((q-r)^2-(q-a-r)^2)/2`.

The ordered local multiplication word with `m-1` onsite factors and one bond
factor is

`partial_r[D_on^(m-1) D_bond]` at `q=r=0`.

Its exact coefficient is

`-c*(-G/4)^(m-1) a^(4m-3)`,

and summing the `m` possible bond-insertion positions multiplies this by `m`.
The primary SymPy lane and independent sparse-polynomial Fraction lane verify
the identity for word lengths 1 through 6; Lean R220 checks the rational
fixture `G=51/35`, degree-nine `m=3` case, and its nonzero coefficient.

## Finding

The word tested here is an actual local polynomial word of the canonical Q3
split, not merely a prescribed abstract coefficient family.  It establishes a
nonzero local source-degree witness with degree `4m-3`.

This advances the incidence question only.  It does not determine the signed
coefficient of the complete Duhamel/Dyson series: other species, bonds,
orientations, commutator orderings and cancellations must still be assembled.
Consequently it supplies no repeated-history bound, common-alpha theorem,
thermodynamic QFT, KMS state, GNS gap, continuum, C6, Sector A or Pre-A result.

## Adversarial review

- **Actual incidence — UPHELD:** both factors are derived from the canonical
  Q3 quartic and one spatial quadratic bond.
- **Restriction — UPHELD:** the zeroed coordinates make this a local witness,
  not a full-volume estimate.
- **Position sum — UPHELD:** the factor `m` counts multiplication-word
  insertion positions; it is not a full operator-series sign theorem.
- **Cancellation — UPHELD:** no noncancellation is inferred.
- **Lean — UPHELD:** R220 is scalar rational arithmetic only.
- **QFT firewall — UPHELD:** no QFT or TECT production gate is promoted.

## Reproducibility

Run the primary and independent scripts, then the integrated verifier.  The
integrated lane executes both implementations and `lake env lean Tect/R220.lean`
and stores the three JSON artifacts under the C6 claim run directory.
