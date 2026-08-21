# R-185 finite packet Cauchy Lean cross-check

R-185 / EXP-000900 is a T0, claim-nonbearing kernel cross-check of the
finite packet Cauchy--Schwarz inequality used after the R-081 temporal
packet factorisation.  For every finite set `s` and rational functions `f,g`,
Lean proves

`(sum_i f_i*g_i)^2 <= (sum_i f_i^2)*(sum_i g_i^2)`.

The registered three-packet fixture uses source `(2,-1,3)` and control
`(4,5,-2)`.  Its source norm is `14`, control norm `45`, pairing `-3`, and
exact defect `14*45-(-3)^2=621`.  The primary lane derives these values from
the manifest, compiles the pinned Lean 4.32.1/Mathlib entrypoint, and checks
clean compiler output.  The independent lane uses only the Python standard
library and exact `Fraction` arithmetic.

The finite inequality is the algebraic input for a packet after the analytic
temporal map and covariance weights have been identified.  It does not supply
those maps, nor does it establish uniformity in the time partition, cutoff,
or revisit multiplicity.  In particular, it does not prove the complete
same-root packet, `OVERLAP_src`, the `q=10/9` Nelson estimate, an interacting
measure, Sector-A, Pre-A, or any limit.  A Lean PASS is only the encoded finite
proposition and does not close either A13 gate.

The integrated lane checks source and dependency hashes, theorem markers,
stdlib-only independence, eight hostile mutations, append-only event linkage,
generated counts, and stored-versus-fresh results.

Reproduction commands:

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_finite_packet_cauchy_crosscheck.py --no-store`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_finite_packet_cauchy_crosscheck_independent.py --output %TEMP%\r185-independent.json`

`E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_finite_packet_cauchy_crosscheck_verify.py --staged --no-store`

No R-185 PDF is issued.
