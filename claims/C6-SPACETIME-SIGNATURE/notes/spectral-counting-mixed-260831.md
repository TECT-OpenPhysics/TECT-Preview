# R-412 mixed spectral-counting note

R-412 is a finite, claim-nonbearing T0 checkpoint.  Instead of forcing one
exponent over every mode, split the ordered positive spectrum at
`1 <= r < d-1`.  For `0 < alpha_IR,alpha_UV < 1`, separate constants on the
head and tail give

```
tr(W^+) <= C_IR^(1/alpha_IR) sum_(k<=r) k^(-1/alpha_IR)
          + C_UV^(1/alpha_UV) sum_(k>r) k^(-1/alpha_UV),
```

with an explicit integral tail for the UV sum.  All 25 declared exponent
pairs and every interior split are checked on every row.  The primary and
independent lanes each pass `592762/592762` assertions over 7 systems, 2688
contexts and 21120 rows.  The selected finite mixed envelope is in
`[0.5800949275086398,2.117318722273093]`; the selected infinite comparison is
in `[0.6295715327320223,3.1299469867610137]`.  The hostile lane passes `9/9`,
the integrated verifier `55/55`, and Lean R412 compiles.

The hostile lane rejects `alpha=1`, unsorted modes, exponent-power inversion,
split-index errors, a linear shortcut inserted into a quadratic bound,
Fiedler-only truncation and the disconnected diagonal-generator mutation.
The optimizer's row-wise pair/split is diagnostic and not a common split rule.
The next obligation is a fixed or analytically controlled IR/UV split with
uniform constants on a common core, followed by R-399 shell transfer and the
R-406 Schur split.  No physical, continuum, C6, Sector-A or Pre-A result is
claimed.
