# R-365 finite spectral-gap Duhamel certificate

Date: 2026-08-27  
Exploration: EXP-001207  
Task: T-054  
Host claim: C6-SPACETIME-SIGNATURE  
Status: T0 claim-nonbearing finite exact reduction; no parent gate closes

## 1. Question

R-364 isolates the bond-commutant residual but still uses a coarse factor
`||B||_omega`. The next idea is to keep the actual spectral energy difference
in the commutator and control finite-time bond influence by a Duhamel estimate.

## 2. Spectral-gap identity

For a finite Hermitian bond generator
`B=sum_a lambda_a P_a`, let
`U_t=exp(-i t B)` and write `X_ab=P_a X P_b`. Then

```text
||U_t^* X U_t-X||_HS^2
  = sum_(a,b) |exp(i t(lambda_a-lambda_b))-1|^2 ||X_ab||_HS^2,
```

and hence, using `|exp(i y)-1| <= |y|`,

```text
||U_t^* X U_t-X||_HS <= |t| ||[B,X]||_HS.
```

The R-364 spectral pinching may be applied first, because the B-commuting
blocks have zero commutator. For any density matrix `omega`,
||omega||_HS <= 1`, so Hilbert--Schmidt Cauchy also gives the state-trace
corollary

```text
|Tr(omega(U_t^* X U_t-X))|
  <= |t| ||[B,X]||_HS.
```

No commutation of `omega` and `B` is required.

## 3. Finite Q3 verification

The primary and independent lanes use the R-362 `V=2`, cutoff `3,4` fixture,
both beta values, both local sites, both split orientations, both time signs,
every prefix and both history adjoints. They check the spectral coefficient
formula, the finite-time phase identity, factorisation of the doubled bond
unitary, spectral-commutant reduction, the Duhamel bound and the state-trace
bound.

Results:

- primary `777/777` and independent `776/776` assertions pass;
- both lanes cover `256` identical contexts;
- maximum spectral coefficient identity error is `1.505e-13` (independent
  `1.448e-13`);
- maximum finite-time phase identity error is `6.178e-14`;
- maximum spectral reduction error is `1.713e-13`;
- maximum Duhamel-bound violation is `7.006e-14`, within the declared finite
  numerical tolerance;
- maximum finite-time change norm is `0.267414`, while the largest Duhamel
  bound is `0.267991`;
- the largest finite-time/bound ratio is `0.999422`;
- maximum state-trace change is `1.125e-7`, below its largest bound `0.035551`;
- the spectral commutator remains nonzero with minimum nonzero norm `0.867344`;
- integrated verification passes `49/49`, Lean R365 compiles, and the largest
  primary/independent compared-field difference is `2.166e-14`.

## 4. Adversarial review

1. **Sign/conjugation objection — DISMISSED.** The lane compares the direct
   doubled bond unitary with `exp(-i t B)` and derives the phase factor in the
   same `U_t^* X U_t` orientation.
2. **Hidden bond factor objection — DISMISSED for the finite fixture.** The
   doubled unitary factorisation and spectral coefficient identity are checked
   independently, rather than inferred from one norm calculation.
3. **State noncommutation objection — DISMISSED.** The state-trace bound uses
   Hilbert--Schmidt Cauchy with `omega` on the left and never moves it through
   `B`.
4. **Zero-commutator promotion objection — UPHELD-OPEN.** Some contexts have a
   nearly zero commutator, but the minimum nonzero norm is positive and the
   route does not assert universal cancellation.
5. **Finite-to-uniform objection — UPHELD-OPEN.** The finite Duhamel constant
   one does not bound `||[B,X]||_HS` uniformly in cutoff, volume, source or
   history.
6. **QFT promotion objection — UPHELD-OPEN.** No common alpha, local collar,
   OS/KMS/GNS reconstruction, gap, continuum, C6, Sector-A or Pre-A closure
   follows.

## 5. Boundary and next gate

R-365 closes a finite-time unweighted spectral-gap inequality and its finite
state-trace corollary. The next proof target is a local modular or
Lieb--Robinson estimate for the spectral commutator norm, with explicit
cutoff/volume/source/prefix/shape dependence. If that norm grows, register the
growth law rather than promoting the Duhamel statement.

No R-365 PDF is issued.
