# TECT Lean cross-verification lane

This is the repository-pinned Lean 4/Mathlib lane for important exact results.
The machine-readable inventory is `registry.json`; it binds every
`Tect/*.lean` source to a normalised SHA-256, theorem markers, and the exact
Lake/Mathlib lock. The release and doctor gates run its metadata check.
The entry points currently include `Tect/R171.lean`, which kernel-checks the
rational Class-II bracket identity and positivity used by R-171,
`Tect/R057.lean`, which kernel-checks the ordered-field arithmetic consequence
of the R-057 sharp-cube budget lower bound, `Tect/R058.lean`, which checks the
exact-B budget comparison used by R-058, and `Tect/R166.lean`, which checks the
exact rational radial-Gram consequences used by R-166.

For every important exact result, this lane is now the repository policy:
ship a small kernel-checked Lean source, pin and hash-check the authoritative
inputs, reject `sorry`, `admit`, `axiom`, and `unsafe`, run a non-importing
independent verifier, and store a JSON result with the theorem boundary. The
Lean check is a cross-verification of the encoded exact consequence; it is not
allowed to silently import or replace the analytic operator, Fourier,
probability, functional, or limit theorem that supplied its hypotheses.

From this directory, after Lean/elan is installed:

```powershell
lake env lean Tect/R171.lean
```

The repository runner first resolves `lake` from the locally installed
toolchain whose directory encoding matches `lean-toolchain`, then falls back
to PATH/elan.  This keeps the check reproducible when the elan shim cannot
reach its update service but the pinned compiler is already installed.

The theorem is intentionally parameterised by the positive coefficients and
regulariser. A result package must separately hash-check the manifest inputs
before treating the theorem as a cross-check of a concrete run. A successful
Lean compile does not close A13/T-050, the full A1 action, the physical-empty
comparison, or any continuum/thermodynamic limit.

The exact toolchain and Mathlib revision are pinned by `lean-toolchain`,
`lakefile.toml`, and the generated `lake-manifest.json` dependency lock;
`.lake/` and generated input modules are local build state.

## Repository-wide checks

From the repository root, the metadata gate is safe on a Python-only machine:

```powershell
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

On a machine with the pinned elan toolchain installed, compile all registered
entrypoints as a separate cross-check:

```powershell
python -X utf8 verification/scripts/lean_toolchain_check.py --compile
```

The stronger command is intentionally explicit because it may take longer and
requires the local pinned toolchain and locked dependencies. A successful
compile validates only the encoded Lean propositions; it does not identify a
physical reference, supply an analytic limit, or close A13/T-050.
