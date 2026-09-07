# Submission-readiness matrix — Q3LOCK

This matrix enforces the project rule that a PDF is produced only after the
content is reviewed and finally organized.

| Gate | Required evidence | Status |
|---|---|---|
| R1 exact model and notation | Frozen Hamiltonian, source, form domain, units | DRAFT COMPLETE; freeze open |
| R2 seven proof blocks | Complete manuscript proofs and dependency map | INCOMPLETE: detailed arguments and composition interface audit present; source-hypothesis/content review and independent acceptance remain |
| R3 external theorem crosswalk | KP/FSS/KKK hypotheses checked line by line | DRAFT; signed review open |
| R4 literature comparison | Bounded primary-source comparison and no priority claim | DRAFT; specialist opinion open |
| R5 claim/result lineage | R-497 remains T0 and claim-bearing=false | CURRENT; bounded decision open |
| R6 primary replay | All canonical finite diagnostics and source hashes | IMMUTABLE FRESH CHECKPOINT PRESENT; independent replay still open |
| R7 independent replay | Non-importing implementation and hostile checks | REQUIRED |
| R8 integrated replay | Current frozen manuscript, manifest, and inputs | REQUIRED |
| R9 content freeze | Notation, bibliography, equations, nonclaims, version | NOT STARTED |
| R10 hash freeze | Fresh SHA-256 for manuscript and all cited package files | NOT STARTED |
| R11 repository release | regen_all.py, doctor.py, release_check.py PASS | REQUIRED AFTER FREEZE |
| R12 signed mathematics review | Completed proof-audit.md and external handoff | OPEN |
| R13 signed literature/novelty review | Completed specialist disposition | OPEN |
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
