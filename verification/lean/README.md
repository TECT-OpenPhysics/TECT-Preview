# TECT Lean cross-verification lane

This is the repository-pinned Lean 4/Mathlib lane for important exact results.
The entry points currently include `Tect/R171.lean`, which kernel-checks the
rational Class-II bracket identity and positivity used by R-171, and
`Tect/R057.lean`, which kernel-checks the ordered-field arithmetic consequence
of the R-057 sharp-cube budget lower bound.

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
