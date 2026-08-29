# R-417 — Log-domain Lyapunov core-tail corridor

R-417 is a finite, claim-nonbearing refinement of the R-416 log-domain route.
It replaces the fragile pointwise conditional-mass floor by a tail interface:
`V_i=exp(alpha*(log(pi_max)-log(pi_i)))` supplies a Foster-Lyapunov drift on
the low-mass tail, while the complementary induced core is checked through a
projected intrinsic gap, core mass, and a core-to-tail jump rate.

The primary lane passes `18480/18480`, the independent lane `17069/17069`,
the hostile lane `10/10`, the integrated verifier `44/44`, and Lean R417
compiles over 13 cutoffs, 78 profiles, and 1410 conditional rows.  The
minimum tail drift on the tested nonempty alpha/theta tails is
`0.5877888606875677`; the minimum induced core gap is
`0.6867237745188258`; the minimum core mass is `0.9804617527664484`; and the
maximum tail mass is `0.01953824723355167`.  The maximum core-to-tail rate is
`7.208711496205039`.

This finite persistence identifies a possible Lyapunov-Poincare/Schur
corridor, but it does not prove its constants are uniform, does not control
the tail of the actual shell likelihoods, and does not establish a global
Poincare inequality, common Hamiltonian core, OS/KMS/GNS gap, physical mass
gap, continuum, C6, Sector-A or Pre-A closure.  No tier change, negative
result, or PDF is issued.
