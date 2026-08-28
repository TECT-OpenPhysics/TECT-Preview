# R-397 scope note — finite semigroup-dressed Petz collar

R-397 / EXP-001241 tests the smooth route proposed by EXP-001240.  For each
finite core, the local Hamiltonian is shifted to a positive matrix `K_A` and
filtered by `F_s=exp(-sK_A/2)`.  The raw state is normalized by
`m_s=Tr(rho exp(-sK_A))`; the Petz map is built only from the filtered BC and B
marginals and is then reused for the original AB input.

The primary package passes 473/473 assertions on five systems, twelve
tripartitions and 120 collar rows.  The independent lane passes 6/6, the
hostile lane 6/6, the integrated verifier 23/23, and Lean R397 compiles.  The
semigroup residual is at most `9.81218636736738e-16`; the filtered mass is at
least `0.344378492577764`; the largest mass defect is `0.655621507422236`; and
the exact first-moment inequality has minimum slack
`0.0030674280806310544`.  The finite candidate envelope
`sqrt(1-m_s)+(1-m_s)/2` bounds every measured normalized disturbance, with
minimum slack `0.2037704602201066`.

The maximum projected Petz error is `0.010367294505488315`, the maximum
transported error is `0.01058510613640556`, and all finite contractivity and
triangle violation counts are zero.  The pilot's largest adjacent-cutoff
transport ratio is `2.192041611389991`, which is an improvement over the
R-396 pilot but remains a finite profile, not uniformity.

This is a T0 claim-nonbearing finite interface.  The mass and semigroup
identities are exact finite functional-calculus checks.  The normalized
disturbance formula is only a tested candidate envelope; proving it in the
intended operator setting still requires a cutoff-independent local moment and
a common form core.  Cutoff/source/volume/shape uniformity, dimension-safe
QCMI transfer, shell summability, Cook/common-alpha convergence, OS/KMS/GNS,
Lorentzian continuation, gap, continuum, C6, Sector-A and Pre-A remain open.
