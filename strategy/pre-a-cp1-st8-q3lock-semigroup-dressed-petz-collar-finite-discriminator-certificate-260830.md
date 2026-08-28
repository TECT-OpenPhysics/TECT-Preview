# R-397 finite semigroup-dressed Petz collar discriminator

R-397 / EXP-001241 is a T0, claim-nonbearing finite checkpoint.  It tests a
smooth local functional-calculus collar as a replacement for the rank-changing
hard spectral projector used by R-394--R-396.  The local Hamiltonian is shifted
by its finite minimum, `K_A=H_A-inf sigma(H_A)`, and the filter is
`F_s=exp(-s K_A/2)`.  The filtered state is normalized by its measured mass
`m_s=Tr(rho exp(-s K_A))` before one fixed Petz map is built from its B and BC
marginals.

## Finite verification

The declared pilot contains five volume/cutoff systems, twelve tripartitions,
two beta values, five collar scales `s in {1/8,1/4,1/2,1,2}`, and 120 rows.
The primary lane passes 473/473 assertions, the non-importing independent lane
passes 6/6, the hostile lane passes 6/6, the integrated verifier passes 23/23,
and Lean R397 compiles.  The exact finite diagnostics are:

* the largest semigroup composition residual is
  `9.81218636736738e-16`;
* the smallest filtered mass is `0.344378492577764`, and the largest mass
  defect is `0.655621507422236`;
* the measured first-moment mass slack has minimum
  `0.0030674280806310544`, so `1-m_s <= s Tr(rho K_A)` holds on every row;
* the candidate normalized-filter envelope
  `D(rho,rho_s) <= sqrt(1-m_s)+(1-m_s)/2` has minimum slack
  `0.2037704602201066` on this grid;
* projected and transported Petz errors have maxima
  `0.010367294505488315` and `0.01058510613640556`, respectively, and every
  contractivity/triangle/two-ABC check has zero violations;
* the largest adjacent cutoff ratio in the transported profile is
  `2.192041611389991` (only the volume-three d=3 to d=4 comparison has an
  adjacent cutoff in this pilot).

The candidate envelope is recorded as a finite discriminator, not as a new
dimension-free theorem.  Its proof still requires a cutoff-independent local
moment and a common form core.

## Hostile review

The hostile row uses volume 3, cutoff 3, beta 1 and `s=2`.  Removing state
normalization leaves a trace gap `0.4063588377792221`; replacing one
`exp(-sK/2)` leg by `exp(-sK)` has Frobenius residual `0.3341273059636541`;
replacing the smooth filter by a hard ground-state projector has residual
`0.5895002061771643`; and dropping both displacement terms makes the genuine
transport error `0.006145099757872087` exceed the mutated projected-only budget
`0.004143142716819127`.  The genuine budget remains valid.  Reversing the
parameters is deliberately a harmless sentinel (`5.494193648707841e-17`) since
the scalar semigroup filters commute; it is not counted as a false failure.

## Interpretation and boundary

The smooth collar removes rank jumps and lowers the observed pilot transport
ratio relative to R-396, so it is a useful continuation rather than a retired
route.  It does not establish that the ratio stays bounded as the oscillator
cutoff, volume, source, or shape grows.  It supplies no QCMI upper bound, no
cutoff-independent moment, no OS/KMS/GNS reconstruction, no common-alpha or
Lorentzian continuation, and no mass gap, continuum, C6, Sector-A or Pre-A
closure.  The next decisive gate is a cutoff-independent moment and
dimension-safe normalized-filter modulus on a declared common local core.
