# Submission-readiness matrix — Q3LOCK

This matrix enforces the project rule that a PDF is produced only after the
content is reviewed and finally organized.

| Gate | Required evidence | Status |
|---|---|---|
| R1 exact model and notation | Frozen Hamiltonian, source, form domain, units | DRAFT COMPLETE; freeze open |
| R2 seven proof blocks | Complete manuscript proofs and dependency map | INCOMPLETE: detailed arguments and composition interface audit present; EXP-001669 finite collective-block aid, EXP-001672 FKG cone-text repair, EXP-001674 collective-Jensen precision repair, EXP-001675 A1-A9 coercivity clarification, and EXP-001680 finite thermal-polynomial integrability repair recorded; source-hypothesis/content review and independent acceptance remain |
| R3 external theorem crosswalk | KP/FSS/KKK hypotheses checked line by line | DRAFT; EXP-001682 and EXP-001683 source captures recorded; signed review open |
| R4 literature comparison | Bounded primary-source comparison and no priority claim | DRAFT; EXP-001663 scalar, EXP-001664 vector/scalar-definition, EXP-001667 Kozitsky primary scalar/radial, EXP-001668 extended direct-import, EXP-001673 KP vector/phase-scope, EXP-001676 vector fluctuation, EXP-001677 KKK vector-rotation source-role boundaries, EXP-001678 Faris--Minlos/Froehlich--Lieb supplement, EXP-001679 KKK threshold/radial-boundary recheck, and EXP-001681 targeted scalar/vector/ground-state recheck recorded; broader anisotropic search and specialist opinion open |
| R5 claim/result lineage | R-497 remains T0 and claim-bearing=false | CURRENT; EXP-001665 records the result-level decision; no duplicate Sector A--F claim card |
| R6 primary replay | All canonical finite diagnostics and source hashes | IMMUTABLE FRESH CHECKPOINT PRESENT: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-manuscript-fresh-audit-source-review-v1/`; signed acceptance remains open |
| R7 independent replay | Non-importing implementation and hostile checks | CURRENT INTERNAL REPLAY: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-independent-replay-source-review-v1/result.json` (`306/306` child assertions; `14/14` package checks); external mathematical acceptance remains open |
| R8 integrated replay | Current manuscript, manifest, and inputs | CURRENT INTERNAL REPLAY: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-q3lock-paper-integrated-replay-source-review-v1/result.json`; final clean replay after freeze still required |
| R9 content freeze | Notation, bibliography, equations, nonclaims, version | NOT STARTED |
| R10 hash freeze | Fresh SHA-256 for manuscript and all cited package files | NOT STARTED |
| R11 repository release | regen_all.py, doctor.py, release_check.py PASS | REQUIRED AFTER FREEZE |
| R12 signed mathematics review | Completed proof-audit.md, A1--A23 review matrix, and external handoff | OPEN |
| R13 signed literature/novelty review | Completed specialist disposition, including matrix citation rows | OPEN |
| R14 operator commit/backup | Release-gated commit and remote-head verification | OPEN |
| R15 final PDF | Compile once from frozen source, render every page, inspect | DEFERRED |
| R16 submission | Explicit operator authorization after R1--R15 | NOT AUTHORIZED |

## Re-review triggers

Reopen R1--R15 after any change to the Hamiltonian, source normalization,
limit order, imported theorem, sufficient regime, bibliography, claim tier, or
nonclaim language.  A repair to a proof block requires a new exploration record
and a new source-hash capture; it must not be hidden as a formatting change.

## Final PDF rule

No intermediate PDF is permitted for this paper.  The first PDF is the final
organization candidate and must be accompanied by its source hash, compiler
version, rendered-page review, and release-check record.  A PDF is not evidence
that the theorem is externally accepted.
