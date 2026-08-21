# R-184 two-block Douglas identity Lean cross-check

R-184 / EXP-000899 is a T0, claim-nonbearing kernel cross-check of the
finite two-block algebra used by R-081's temporal Cauchy--Douglas reduction.
The registered rational fixture has source coefficients `(3,4)` and control
coordinates `(5,-2)`.  Lean proves the exact identity

`(s1*h1+s2*h2)^2 + (s1*h2-s2*h1)^2 = (s1^2+s2^2)*(h1^2+h2^2)`

for all rational inputs, and therefore proves the corresponding contraction
bound.  The fixture has source norm `25`, control norm `29`, pairing `7`,
wedge `-26`, and exact gap `676=26^2`.

The source and A13 status are hash-pinned.  The pinned Lean 4.32.1/Mathlib
toolchain is compiled with `lake env lean Tect/R184.lean`; the primary lane
also checks the source hashes, theorem markers, clean compiler output, and
the stored run contract.  The independent lane uses only the Python standard
library and exact `Fraction` arithmetic.  The integrated lane checks source
and dependency hashes, AST/import independence, eight hostile boundary
mutations, event linkage, generated counts, and stored-versus-fresh results.

This cross-check is only the finite two-block identity.  It does not prove the
production temporal factorisation, arbitrary partition or revisit uniformity,
the complete same-root packet, `OVERLAP_src`, the Nelson estimate, an
interacting measure, Sector-A, Pre-A, or any limit.  In particular, a Lean
PASS here does not close either A13 gate.

Reproduction commands:

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_two_block_douglas_crosscheck.py --no-store`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_block_douglas_crosscheck_independent.py --output %TEMP%\r184-independent.json`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_block_douglas_crosscheck_verify.py --staged --no-store`

No R-184 PDF is issued.
