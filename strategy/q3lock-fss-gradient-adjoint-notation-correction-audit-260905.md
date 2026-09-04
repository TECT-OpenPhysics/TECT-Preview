# Q3LOCK FSS gradient-adjoint notation correction audit

**Status:** T0 proof-text notation correction; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 -> EXP-001554  
**PDF:** deferred until mathematical content, independent review, clean replay,
and release review are complete

## 1. Question and strict boundary

The EXP-001554 incidence repair correctly fixed the domains
`G:V_0 -> E` and `B_FSS=G^*:E -> V_0`, but its first insertion into the two
load-bearing proof notes wrote `h=G*L_sp^(-1)j`.  With the declared domain of
`G`, that star is an operator-order typo: the minimum-norm edge field solving
`B_FSS h=j` is `h=G L_sp^(-1)j=B_FSS^*L_sp^(-1)j`.

This audit corrects that single symbol in the P-06 and P-09 notes.  It does
not change the source, coupling, Fourier eigenvalue, Poisson norm, infrared
constant, theorem hypothesis, claim tier, or publication status.

## 2. Correct operator calculation

With

```text
G : V_0 -> E,
B_FSS=G^* : E -> V_0,
L_sp=G^*G=B_FSS B_FSS^* on V_0,
```

the zero-sum source `j` has minimum-norm solution

```text
h=G L_sp^(-1)j=B_FSS^*L_sp^(-1)j.
```

Therefore `B_FSS h=j`,
`c*(G omega,h)=(j,omega)`, and
`(c/2)||h||^2=(1/(2c))*(j,L_sp^(-1)j)`.  These are the same identities
used by the FSS domination route; only the domain-consistent display is
retained.

## 3. Verification boundary

The corrected bytes are rehashed in the R-497 manifest and ledger, and the
generated readers are regenerated.  The record remains T0 and
`INTERNAL_REVIEW_ONLY`, with independent FSS, loop-limit, operator,
source-tangent, clean-replay, external-referee, and final content-freeze gates
open.  No LaTeX manuscript or PDF is produced at this stage.

