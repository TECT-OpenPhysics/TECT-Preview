# EXP-001078 / Gibbs-weighted noncommutative fifth-moment-to-Q obstruction

## Decision

EXP-001077 showed that an arbitrary nontracial state cannot justify the
scalar `Q_sigma` candidate from form order alone.  This checkpoint strengthens
the state to a genuine finite-temperature Gibbs state for the abstract energy
`K` and tests whether that extra structure repairs the route.

The tested shortcut is

```text
K=A+P,  A>=0, P>=0,  rho=exp(-beta*K)/Tr(exp(-beta*K))
    => Q_sigma^2 <= (9/4)*m5^(3/10),  m5=phi_rho(K^5).
```

It is still false for a finite exact matrix family.  The result is a stronger
route-local obstruction, not a counterexample to the actual Q3 Hamiltonian or
Gibbs state.

## Exact Gibbs witness

For a Pell pair `(t,s)` with `t^2-2*s^2=-1`, put `L=t^2` and use

```text
K   = diag(1,L)
A   = (1/2) [[1,t],[t,L]] = (1/2) (1,t)^T (1,t)
P   = (1/2) [[1,-t],[-t,L]] = (1/2) (1,-t)^T (1,-t)
rho = diag(L^6/(L^6+1), 1/(L^6+1)).
```

The state is exactly Gibbs for `K` at

```text
beta = 6*log(L)/(L-1) > 0,
```

because `rho_22/rho_11=L^-6=exp(-beta*(L-1))`.  The rank-one factors give
positivity and `K=A+P`.  The Pell identity gives `A^2=s^2 A` and hence

```text
m5  = phi_rho(K^5)       = L^5*(L+1)/(L^6+1)
Q^2 = 2*phi_rho(A^(3/2)) = s*(L^6+L)/(L^6+1).
```

The candidate comparison is tested exactly after raising positive sides to the
tenth power:

```text
(Q^2)^10 > (9/4)^10*m5^3.
```

The three fixtures `(t,s)=(7,5),(41,29),(239,169)` all satisfy this strict
inequality.  The first already has

```text
m5 = 7061881225/6920643601
Q^2 = 34603218125/6920643601,
```

so the failure is not caused by a zero-temperature limit or floating-point
rounding.

## Adversarial review

1. **Gibbs identity — UPHELD.** The state ratio is exactly `L^-6` and the
   displayed positive finite beta realizes it as a Gibbs state for `K`.
2. **Positivity — UPHELD.** `A` and `P` are rank-one positive forms and their
   sum is positive diagonal `K`.
3. **Moment — UPHELD.** Both `m5` and `Q^2` are recomputed as exact rational
   traces under the same Gibbs state, including both diagonal contributions.
4. **Fractional comparison — UPHELD.** The tenth-power comparison is an exact
   rational inequality, with no decimal root or threshold.
5. **Temperature — UPHELD.** Every beta is finite and strictly positive; its
   dependence on `L` is explicit and no beta-independent theorem is claimed.
6. **Q3 identification — UPHELD.** `K` is an abstract 2x2 witness, not the
   interacting Q3 Hamiltonian or its local Gibbs measure.
7. **Lean — UPHELD.** R260 checks only rational Pell, Gibbs-ratio, moment,
   powered-comparison and scope fixtures.
8. **QFT promotion — UPHELD.** OS/KMS/GNS, gap, continuum, C6, Sector A,
   Pre-A and the TECT production owner remain unchanged and open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_gibbs_weighted_noncommutative_moment_transfer_obstruction.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_gibbs_weighted_noncommutative_moment_transfer_obstruction_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_projected_delta_d_third_coefficient_gibbs_weighted_noncommutative_moment_transfer_obstruction_verify.py
lake env lean Tect/R260.lean
python -X utf8 verification/scripts/lean_toolchain_check.py --metadata
```

The primary and independent lanes each pass `52/52`; integrated verification
passes `20/20` with Lean R260 passing.  The Lean registry then has 96
entrypoints and 1446 assertions.

## Boundary and next gate

This is a T0, claim-nonbearing finite Gibbs-weighted obstruction.  It rejects
only the abstract “Gibbs for the dominating K is enough” shortcut.  It does
not reject the actual Q3 Gibbs family, whose Hamiltonian, local algebra,
common quartic form core, and volume-uniform estimates are not represented by
this 2x2 witness.

The next gate is to use the actual Q3 Hamiltonian as the Gibbs generator and
prove a translate- and volume-uniform trace/commutator estimate on the common
form core, including the multiplication and domain hypotheses needed for
`P_sigma` and `Q_sigma`.  Any proposed theorem must first survive this exact
finite Gibbs obstruction.
