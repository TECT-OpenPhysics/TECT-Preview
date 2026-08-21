# R-175 v1.0 certificate

## Scope

R-175 is a T0, claim-nonbearing Lean cross-check under EXP-000890. It freezes
the algebraic interface for a duplicated six-real covariance block. If a real
matrix `L` satisfies `L L^T = C`, define

`G = diag(L,L)`, `Gamma = diag(C,C)`, and
`J = [[0,-I],[I,0]]`.

The exact identities are `G G^T = Gamma`, `J G = G J`, and therefore `G`
commutes with every linear rotation `c I + s J`. The first identity lets a
supplied square-root witness be used in the R-150/R-174 synthesis; the second
preserves the phase rotation used by the antipodal realification.

## Kernel and independent checks

`verification/lean/Tect/R175.lean` proves the identities for arbitrary finite
index type and commutative ring. The primary SymPy lane derives the same block
products symbolically and checks a positive lower-triangular 3 by 3 fixture.
The independent lane uses only standard-library `Fraction` arithmetic and
rebuilds the block products and rotation commutation. The integrated lane
checks pinned authorities, source hashes, Lean escape tokens, AST/import
independence, eight hostile mutations, event/count topology and stored runs.

The fixture is a test witness only. It is not asserted to be the square root of
the actual A1 `C(k)` or `C(2k)` matrix.

## Boundary

R-175 does not establish existence or canonical choice of the actual A1 square
roots. It does not supply heat/root incidence, complement, historical-low,
forest, returned mean, a complete scalar owner, source/sextic one-use, T-050,
A13, Nelson, a measure, phase/PDE, physical-empty, removal, continuum,
Sector-A or Pre-A closure. No new negative, gate closure, tier change or PDF
follows.

No R-175 PDF is issued.
