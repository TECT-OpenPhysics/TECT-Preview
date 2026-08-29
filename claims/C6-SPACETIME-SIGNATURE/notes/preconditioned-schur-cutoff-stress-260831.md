# R-416 — Log-domain and projected Schur cutoff stress

R-416 is a finite, claim-nonbearing refinement of the R-415 numerical route.
It reconstructs Gibbs masses and conditional rows in the log domain, projects
the normalized intrinsic graph away from the exact `sqrt(pi)` constant mode,
and checks the R-406 harmonic coarse/residual Schur certificate.

The primary and independent lanes each pass `4370/4370` assertions over 13
cutoffs, 78 profiles and 1410 rows.  The hostile lane passes `9/9`, the
integrated verifier passes `39/39`, and Lean R416 compiles.  Primary projected
gaps are `[0.6867237745188259,11.524804493011532]`; primary Schur gaps are
`[0.3476008247075759,5.985995817095592]`.  Raw zero-mode residuals reach
`1.0782998803365607` in the primary lane and `1.1256888563326983` in the
independent lane, but projected gaps stay positive.  Direct underflow rows are
zero and common weight scaling has residual `0.0`.

The finite result diagnoses a floating-point failure mode and extends the
cutoff stress.  It does not prove a cutoff-, volume-, source-, phase- or
exhaustion-uniform gap, a common Hamiltonian core, OS/KMS/GNS reconstruction,
the physical mass gap, continuum, C6, Sector-A or Pre-A closure.  No tier
change, negative result or PDF is issued at this checkpoint.
