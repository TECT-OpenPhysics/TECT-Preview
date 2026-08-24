# EXP-001064 / fixed-beta mixture-seminorm orbit-contract stress test

## Decision

The beta,# contractivity used in EXP-001062 cannot be inferred from a fixed
state alone.  An exact 2x2 witness is enough to make the missing embedding
condition explicit.

Let

\[
 \rho=\frac{I+(3/5)\sigma_z}{2},\qquad
 U=\frac{3I-4i\sigma_x}{5},\qquad
 P_- =\frac{I-\sigma_z}{2},
\]

and use
\(N_\rho(X)^2=\operatorname{Tr}(\rho X^*X)+\operatorname{Tr}(\rho XX^*)\).
The matrix (U) is exactly unitary.  Initially

\[
 N_\rho(P_-)^2=1-3/5=2/5.
\]

For (X'=U^*P_-U), the diagonal entries are (16/25) and (9/25), hence

\[
 N_\rho(X')^2=2\left(\frac45\frac{16}{25}+\frac15\frac9{25}\right)
 =\frac{146}{125}>\frac25.
\]

Thus the fixed state is not invariant under this noncommuting finite orbit.
This does not reject an OS-reconstructed dynamics whose state/topology is
invariant; it rejects only the shortcut from a fixed state and static moments
to the contractivity hypothesis.

## Adversarial review

1. **Matrix exactness — UPHELD.**  All entries and traces are rational after
   the displayed 3-4-5 unitary; no floating-point conclusion is used.
2. **Two-sided norm — UPHELD.**  The test uses the same two-sided seminorm
   target as the fixed-beta OS gate.
3. **Obstruction scope — UPHELD.**  Only automatic fixed-state contractivity is
   rejected; an invariant reconstructed OS group remains viable.
4. **Static-to-dynamic leap — UPHELD.**  EXP-001061/1062 moments are not
   promoted to an embedding theorem.
5. **Volume — UPHELD.**  Dimension two is a stress fixture, not a thermodynamic
   estimate.
6. **Lean — UPHELD.**  R246 checks exact rational values, not operator domains.
7. **QFT/TECT — UPHELD.**  No OS/KMS, gap, continuum, C6, Sector A, Pre-A or
   heat_root_incidence conclusion follows.
8. **Negative boundary — UPHELD.**  The witness is retained as an exploration
   boundary and does not create a global negative authority.

## Next gate

The next proof obligation is an actual finite Hamiltonian-to-OS intertwiner
with invariant beta,# topology, or a replacement weighted orbit estimate that
does not require contractivity.  Direct (D,\delta D), exhaustion and all
QFT/TECT successor gates remain OPEN.
