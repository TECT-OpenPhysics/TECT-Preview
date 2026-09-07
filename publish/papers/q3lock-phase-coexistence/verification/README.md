# Q3LOCK paper verification package

The paper uses the canonical repository verifiers rather than silently
reimplementing the mathematics in a paper-local script.  Run commands from
E:\Dev\TECT with the repository environment:

    $py = "E:\Dev\TECT.venv\Scripts\python.exe"
    & $py -X utf8 verification/scripts/q3lock_absolute_partition_audit.py
    & $py -X utf8 verification/scripts/q3lock_thermodynamic_pressure_audit.py
    & $py -X utf8 verification/scripts/q3lock_dlr_tangent_content_audit.py
    & $py -X utf8 verification/scripts/q3lock_fkg_content_audit.py
    & $py -X utf8 verification/scripts/q3lock_reflection_infrared_content_audit.py
    & $py -X utf8 verification/scripts/q3lock_collective_falk_bruch_content_audit.py
    & $py -X utf8 verification/scripts/q3lock_strict_cusp_tangent_content_audit.py
    & $py -X utf8 verification/scripts/q3lock_manuscript_source_audit.py

The registered deterministic outputs are under
claims/C6-SPACETIME-SIGNATURE/runs/ and are linked by the R-497 manifest.  The
two newest content checks replay at 40/40 and 42/42 and were byte-stable under
immediate repetition.  Earlier registered inputs include the finite pressure,
DLR, FKG, Gaussian, and reflection/infrared artifacts listed in the manifest.

## What the commands do not prove

The v0.1.1 manuscript audit differentiates pair polynomials, recomputes
Gaussian coefficients from the internal graph, and rejects deliberately
reintroduced log-density sign, entire-pressure and bibliography defects.
It checks source references and current draft fingerprints without compiling.
Its run is `2026-09-06-q3lock-manuscript-content-audit/result.json` under
the same canonical runs tree. It does not alter the older hash-pinned notes.

The v0.1.2 loop audit constructs exact rational
precision inverses and interpolation vectors independently of the existing
Fourier implementation, and executes the earlier content checker in memory.
The earlier output is hash-checked and preserved, with current results written
to `2026-09-06-q3lock-manuscript-loop-audit/result.json`. Do not rerun the
old standalone content writer against the changed manuscript when preserving
that historical run.

The v0.1.3 DLR audit
recomputes envelope/Young identities, finite-region degree allocation,
source factors, Holder closure and compact-boundary kernel coefficients.
Hostile fixtures reject reversed weight control and weak convergence used
without uniform integrability. Its 81 finite checks include structure-only
locators; it calls the loop checker (203 checks) and earlier checker (32)
in memory, preserving both historical output files. Do not run either old
standalone manuscript writer on this changed draft. The current output is
`2026-09-06-q3lock-manuscript-dlr-audit/result.json`. This is an internal
integrated replay, not a signed mathematical review or a clean release
snapshot.

The v0.1.4 infrared audit is now historical.
Its 612 checks use every exact Fourier mode on a diagnostic L=4 torus,
projected rational Gaussian-kernel Gram matrices, enumerated shells and
symbolically recomputed source and tail coefficients. It calls the DLR
checker (81), loop checker (203) and earlier content checker (32) only in
memory and preserves all three older output files. Do not invoke any of
those historical standalone manuscript writers on this changed draft.
Its historical output is
`2026-09-06-q3lock-manuscript-infrared-audit/result.json`. Counts include
structure-only locators and must not be reported as analytic theorem checks.

The v0.1.5 collective audit is now historical.
Its 150 checks independently differentiate the Q3 common-shift polynomial,
verify symbolic scalar-concavity identities and compare matrix/spectral
commutators at exact rational Gibbs weights. Degenerate energies, two-level
saturation, finite Gibbs normalization and deliberately wrong beta, hbar and
normalized-monotonicity substitutions are covered. It invokes all preceding
manuscript checkers only in memory and preserves all four historical outputs.
Do not invoke any historical standalone manuscript writer on this draft.
Its historical output is
`2026-09-06-q3lock-manuscript-collective-audit/result.json`. The scalar
inequality and infinite-dimensional passages are analytic manuscript
arguments, still requiring independent review; the checks do not certify them.

The v0.1.6 composition audit is now historical.
Its 59 exact finite/symbolic and structural checks cover the source dictionary,
threshold identities, squared-tail integral and bounded cylinder witness.
A symmetric two-point toy law rejects an exchange of source and volume limits;
it is not a Q3LOCK phase calculation. The checker verifies the complete 91-file
frozen authority manifest and invokes all five prior manuscript checkers in
memory, preserving their historical output files. Do not run any of those
standalone historical manuscript writers against this changed draft.
Its historical output is
`2026-09-06-q3lock-manuscript-composition-audit/result.json`.

For v0.1.7 use q3lock_manuscript_source_audit.py, as listed above.
It independently evaluates the Q3 quartic on equal-norm vectors,
differentiates an internal edge to test scalar-bilinear rewriting, and checks
the mass/threshold algebra. Its citation/label checks are structural only.
It calls the composition checker and its predecessors in memory, preserving
all six historical runs. The new output is
`2026-09-07-q3lock-manuscript-source-audit/result.json`.
No script certifies the exact source-hypothesis or novelty dispositions.

These scripts recompute finite algebra, normalization, source-factor, graph,
threshold, and provenance checks.  They do not prove an infinite-dimensional
Feynman--Kac passage, an external theorem's applicability, thermodynamic
compactness, a DLR state, a pressure cusp, or literature novelty.  Those are
the explicit proof-audit and external-review obligations.

## Frozen replay protocol

After remaining source/content review and any resulting repairs, make a clean tracked snapshot and run the primary,
independent, and integrated lanes against the exact manuscript and the
hash-pinned R-497 inputs.  The package manifest must then be rewritten with
fresh SHA-256 values and byte-stable output hashes.  Only after that release
check may the first PDF be compiled and rendered for visual inspection.

The current package is intentionally UNFROZEN; no PDF is generated by this
README or by the current manuscript assembly.
