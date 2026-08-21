# A1 Class-II owner mismatch Lean cross-check

Result `R-172` records a finite exact owner-interface obstruction under
`EXP-000887`. The declared A1 K term has numerator `cKK beta_X^2`, while the
implemented residual has `cJK alpha_X beta_X`. Reading the hash-pinned values
gives `3/320` and `3/400`, respectively, with difference `3/1600`. The common
mass denominator is `4 + 1/1000000000000 > 0`, so the coefficient mismatch
survives the regularizer.

Lean checks the rational identity and non-equality. The Python primary reads
and hash-checks the A1 manifest and compiles Lean; the independent bridge is a
stdlib-only `Fraction` derivation; the integrated verifier compares both and
tests hostile mutations.

This note does not claim a full spatial Class-II variation or close A13. It
fixes the owner choice needed before a canonical finite production cylinder:
the historical residual cannot be silently treated as the gradient of the
declared K energy. No tier or lifecycle changes follow.
