# R-372 modular centering and thermal-variance certificate

## Result-first boundary

R-372 is a T0, claim-nonbearing finite checkpoint under EXP-001214.  It
sharpens the R-371 theta-half reduction by centering the moved collision
witness with the *same doubled-bond Gibbs state* that supplies the
Kubo--Mori weights.  The shell is unchanged, while its controlling row sum
becomes a thermal variance.  No uniform variance theorem is claimed.

## 1. Finite algebraic reduction

Let `G` have eigenvalues `lambda_i`, let `p_i` be its finite Gibbs weights,
and let `X` be the Hermitian moved witness in the `G` eigenbasis.  Define

```text
m = sum_i p_i X_ii,
Y = X - m I.
```

Then

```text
sum_i p_i sum_j |Y_ij|^2
  = sum_i p_i sum_j |X_ij|^2 - m^2
  = Tr(rho_G X^2) - (Tr(rho_G X))^2.
```

Only diagonal entries change under `X -> Y`.  Since every theta-half
Kubo--Mori shell term contains `|lambda_i-lambda_j|`, all changed diagonal
terms have zero coefficient.  Therefore the shell is exactly invariant.

Combining this with the R-371 identity and `|p_i-p_j| <= p_i+p_j` gives the
finite target

```text
N_(1/2)^2 <= (4/beta) Var_(rho_G)(X).
```

This is a sharper premise than the raw second moment, but it is not a
uniformity result.

## 2. Verification

The primary and non-importing independent lanes each pass `17002/17002`
assertions over `2816` all-prefix contexts.  The integrated verifier passes
`114/114`, and Lean R372 compiles.  The largest primary/independent numeric
difference is `2.132e-13`.

The largest sampled raw local second moment is `44.58328971021096`; the
corresponding modular thermal variance is `41.64826651661874`.  The maximum
centering identity residual is `1.421e-14`, and the shell-centering residual
is exactly zero in the stored floating-point run.  Edge variance maxima by
cutoff are `2.733031855844076`, `3.4283208579615874`, `4.703343964629605`
and `41.64826651661874` for `d=3,4,5,6`; all square `d=2` bond rows are one
up to roundoff.  Thus centering removes a scalar component but does not
remove the sharp edge cutoff growth.

Reproduce with:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_kubo_mori_modular_centering_verify.py
```

## 3. Lean cross-check

`verification/lean/Tect/R372.lean` proves the finite weighted-variance
decomposition, nonnegativity, zero-gap centering invariance, the Gibbs pair
bound, and nonnegative row control.  It does not formalize numerical matrix
diagonalisation, the full trace passage, a common core, or any regulator
limit.

## 4. Adversarial review

1. **Center choice.**  The mean is taken in the doubled-bond Gibbs basis, the
   same state used by the Kubo--Mori weights; using the full interacting Gibbs
   mean would not give this identity.
2. **Zero-gap diagonal.**  Centering changes only diagonal spectral entries,
   and their transition-energy factor is exactly zero.
3. **Variance sign.**  Nonnegative Gibbs weights and squared centered rows are
   checked directly; no cancellation is used to establish nonnegativity.
4. **Pair sign/factor.**  The finite pair inequality uses absolute
   `|p-q| <= p+q` and the positive factor `2/beta`; Lean checks the same
   ordered-field consequence.
5. **Uniformity.**  The edge variance rises by more than an order of
   magnitude at `d=6`; this is retained as an open cutoff-uniformity gate,
   not called a divergence theorem.
6. **Proxy state.**  The doubled local bond Gibbs state is not a proved global
   KMS state or thermodynamic limit.
7. **Independence.**  The independent lane rebuilds the oscillator, graph,
   Gibbs state, witness, spectra and histories without importing the primary
   R-372 module.
8. **QFT promotion.**  Common core, common alpha, OS/KMS/GNS dynamics, mass
   gap, continuum, C6, Sector-A and Pre-A remain open.

## 5. Decision and next gate

R-372 advances the direct `D,delta-D` route by replacing the raw local
second-moment premise with the exact, sharper thermal-variance premise.  The
next decisive task is an analytic source/volume/cutoff-uniform variance bound
on a Hamiltonian-derived common core.  If that estimate fails, its growth
must be recorded as a route-local obstruction before any common-alpha
promotion.  No new negative result or PDF is issued.
