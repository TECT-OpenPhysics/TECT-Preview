# R-184 note: two-block Douglas identity

R-184 records a kernel-checked finite algebraic component of the R-081
temporal overlap route.  For rational source coordinates `s=(s1,s2)` and
control coordinates `h=(h1,h2)`, the exact wedge identity gives

`||s||^2 ||h||^2 - <s,h>^2 = (s1*h2-s2*h1)^2 >= 0`.

The proof is parameterised in Lean over `Rat`, so the displayed fixture is
not the theorem's only input.  The exact fixture `(s1,s2,h1,h2)=(3,4,5,-2)`
has `(source_norm,control_norm,pairing,wedge,gap)=(25,29,7,-26,676)`.

The result is deliberately narrower than R-081.  It does not instantiate the
actual production covariance, identify all temporal maps, control repeated
range visits, or supply the cutoff-uniform signed complete-packet estimate.
`OVERLAP_src`, the full progressive/revisit gate, Nelson, Sector-A, and Pre-A
remain open.
