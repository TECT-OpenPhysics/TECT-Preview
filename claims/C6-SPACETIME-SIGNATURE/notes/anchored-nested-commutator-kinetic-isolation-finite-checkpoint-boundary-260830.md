# R-387 anchored nested-commutator kinetic-isolation boundary

R-387 / EXP-001230 is a claim-nonbearing finite checkpoint extending the
R-386 coordinate-resolvent anchor.  For every actual Q3 bond prefix on the
V=2 edge and V=4 square, the prefix is split as `H=T+V`, where `T` contains
the included quadratic momentum terms and `V` contains only coordinate
polynomials.  With `A_z=(i eta I-q_s)^(-1)` and position-only boundary `B`,
the finite matrices satisfy `[V,A_z]=[B,A_z]=0`, hence
`[B,[H,A_z]]=[B,[T,A_z]]`.

The primary lane passes 1019/1019 assertions, the non-importing independent
lane passes 1012/1012, the integrated verifier passes 46/46, and Lean R387
compiles.  The grid has 288 beta-weighted contexts, 144 seed rows and 10 bond
prefixes.  Primary maxima are `7.415006673014076e-16` for `[V,A_z]`,
`2.317703490729531e-16` for `[B,A_z]`, `1.0801915330073514e-15` for the inner
isolation, `1.5436854843327511e-15` for the nested isolation,
`1.984473368162697e-15` for potential-scale invariance and
`7.402251795272793e-16` for the weighted isolation.  The independent maximum
field difference is `7.95529426326475e-18`.

A hostile same-site momentum mutation `V -> V+(1/4)p_left` is rejected: the
minimum selected inner-isolation residual is `0.279128784747792` and the
minimum nested residual is `0.364793624984`, both above `1.0e-7`.

The exact finite cancellation only removes coordinate potentials from the
first nonzero anchored coefficient.  It does not bound `[B,[T,A_z]]`, its
modular companion or higher time coefficients in an unbounded domain.  Phase-
local BKM control, shell `l1` summability, all uniformities, direct Cook and
common-alpha convergence, OS/KMS/GNS identification, a gap, continuum, C6,
Sector-A and Pre-A remain open.  No negative result, tier change or PDF is
issued.
