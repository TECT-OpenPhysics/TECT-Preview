# R-179: future-variance and forest owner-half coefficient ledger

## Status

R-179 is a T0, claim-nonbearing exact coefficient checkpoint. It rechecks the
finite owner algebra cited by R-125 and R-136; it is not the production
source/sextic one-use theorem.

## Exact owner-half identities

Write `F` for the once-owned adapted forest term and `V` for the legal future
conditional variance. The owner-half coordinate is

`P = F/2 - V/4`.

Lean proves `2P=F-V/2`, `P+V/4=F/2`, and `P(F=0,V=4s)=-s`. Thus the variance
rebate is a genuine one-use term: omitting it changes the owner by `V/4`.
For `V>=0`, `P<=F/2`; equality holds at zero variance. The constant-translation
fixture `F=0,V=4,s=1` gives `P=-1` exactly.

## Verification and boundary

The primary SymPy lane and independent Fraction lane bind R-125, R-136,
R-177 and R-178 source boundaries and agree on every derived value. The Lean
entrypoint has no `sorry`, `admit`, `axiom` or `unsafe` token. The integrated
mutation suite rejects dropping the variance rebate, changing the replica
factor, erasing the constant-translation defect, signing variance without a
nonnegativity hypothesis, closing A13/Sector-A, changing authority hashes, or
inserting a Lean escape.

This does not prove the analytic forest, production current/source/sextic
one-use, T-050, A13, Nelson, an interacting measure, physical-empty,
removal/continuum, Sector-A or Pre-A closure.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_future_variance_forest_owner_half_ledger.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_future_variance_forest_owner_half_ledger_independent.py --output %TEMP%\r179-independent.json
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_future_variance_forest_owner_half_ledger_verify.py --staged --no-store
```

No R-179 PDF is issued. The next action is to insert the differentiated R-178
owner into this coefficient ledger and test source/sextic one-use without
double-spending the variance rebate.
