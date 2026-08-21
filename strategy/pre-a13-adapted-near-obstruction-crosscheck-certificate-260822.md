# R-187 adapted NEAR obstruction Lean cross-check

R-187 / EXP-000902 is a T0, claim-nonbearing kernel cross-check of finite
fixtures that delimit the still-open adapted NEAR operator in R-081.  The
fixtures are exact rational diagnostics, not a production lower bound.

## 1. Nonlinear conditional-mean split

For `c=2/5`, root sign `r` and fresh sign `e`, take
`A=e(1+c r)`.  For either root, the conditional mean over `e` is zero.  The
conditional square values are `49/25` at `r=+1` and `9/25` at `r=-1`; their
root average is `29/25`, so the root innovations are `+4/5` and `-4/5`.
Thus `d_j A=0` does not determine `d_j |A|^2`.  Lean proves these identities
over `Rat` by exact normalization.

## 2. Adapted ledger and signed slack

At `gamma=1/20`, the registered adapted ledger is
`a=39/80`, `b=121/240`, slack `1/120`, and moment `6/gamma=120`.
The control-control pair slack
`(gamma-1-2 theta)/6` is respectively `-19/120`, `-23/120`, and `-13/40`
for `theta=0,1/10,1/2`.  All are negative.  This is why the control-control
branch must remain signed and cannot be paid by an unsigned pair estimate.

## 3. Finite Doob witness

For the four atoms `(xi_1,xi_2)` in `{(-1,-1),(-1,1),(1,-1),(1,1)}`, the
finite orthogonal fixture has square sum `2`, terminal `L2` value `2`, terminal
`L6` value `32`, and square-L6 value `8`.  The registered bound `32 <= 8*8`
holds.  This is a bounded witness only; it is not a cutoff-uniform adapted
operator theorem.

## 4. Verification and boundary

The primary lane derives every scalar from the manifest, compiles the pinned
Lean 4.32.1/Mathlib entrypoint, and checks clean output.  The independent lane
uses only stdlib `Fraction` arithmetic.  The integrated lane checks hashes,
theorem markers, AST/import separation, eight hostile mutations, event and
exploration linkage, generated counts, and stored freshness.

The package does not prove the production adapted NEAR operator, the complete
same-root lower bound, arbitrary progressive/revisit uniformity, `OVERLAP_src`,
Nelson, an interacting measure, Sector-A, Pre-A, or any limit.  It does not
close an A13 gate, create a negative result, change a tier, or issue a PDF.

Reproduction commands:

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_adapted_near_obstruction_crosscheck.py --no-store`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_adapted_near_obstruction_crosscheck_independent.py --output %TEMP%\r187-independent.json`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_adapted_near_obstruction_crosscheck_verify.py --staged --no-store`

No R-187 PDF is issued.
