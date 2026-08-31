# R-461 fixed-floor smooth Class-II null-branch dichotomy

## Route role

R-461 is an additive T0 lemma for the existing A6/A7 Class-II functional. It
does not replace the forward T-054 route, the observation-first inverse
T-059/T-061 route, the owner order, or any existing regulator and limit
convention. It supplies the branch partition that the open A6 full-field
bare-concentration gate was missing.

## Exact statement and scope

Let `Omega` be a connected `C1` spatial domain (intended application:
the fixed periodic three-torus), let `Psi=(psi_1,psi_2,psi_3)` be `C1`, and
write `z=(psi_1,psi_2)`, `rho=|Psi|^2`,
`m_A=z^dagger sigma_A z`, `q_A=m_A/(rho+epsilon_rho)`,
`J_A=grad m_A`, and `K_A=J_A-q_A grad rho`, with the existing fixed
`epsilon_rho>0`. The existing positive coefficient matrix
`Q_II=[[a,b],[b,c]]` is used without modification.

The exact implications are:

1. Positive definiteness gives
   `a j^2+2b j k+c k^2 = (a j+b k)^2/a + (ac-b^2) k^2/a`, hence zero
   Class-II density forces `J_A=K_A=0` pointwise.
2. `m_1^2+m_2^2+m_3^2=s^2`, where `s=|z|^2`. Therefore a zero Bloch vector
   is equivalent to `z=0`.
3. On a connected domain, a smooth pathwise null field is either the pure
   singlet branch `z=0` with arbitrary `psi_3`, or an active branch with a
   nonzero constant Bloch vector, constant `rho`, and constant rank-one
   doublet projector. The active doublet may carry one local common `U(1)`
   phase; the singlet phase is independent.
4. Both branches give `J_A=K_A=0` and hence zero pathwise Class-II energy.
5. A common-phase active plane wave is pathwise null while the already
   registered `W_epsilon` contraction is strictly positive. Thus
   `W_epsilon^{-1}(0)` cannot replace the pathwise null set.

The calculus step (zero gradient on a connected domain and zero integral of a
continuous nonnegative density) is an explicit analytic assumption. Lean
checks the exact rational Bloch and positive-form core only.

## Reproduction

From the repository root:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/a6_classii_null_branch_dichotomy.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a6_classii_null_branch_dichotomy_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/a6_classii_null_branch_dichotomy_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/a6_classii_null_branch_dichotomy_verify.py
```

The integrated verifier also compiles `verification/lean/Tect/R461.lean` with
the repository-pinned Lean/Lake toolchain. The A1-derived coefficients are
read from the hash-pinned production functional manifest; no derived decimal
coefficient is hardcoded in the audit scripts.

## Adversarial review

The hostile lane rejects eight mutations: sign errors in `m2`/`m3`, a
non-positive coefficient matrix, the inference that constant `rho` is enough,
dropping or changing the quotient derivative term, a nonzero zero-Bloch
doublet, replacing the pathwise null set by `W_epsilon=0`, and premature
promotion to Gibbs/continuum/source-owner/physical status. The primary and
independent lanes enumerate the exact integer grid `[-2,2]^4`, derive all
coefficients from A1, and exercise pure-singlet, common-phase, rotating, plane
wave, and quotient-derivative controls.

## Evidence and boundary

The package is claim-nonbearing T0 evidence (`R-461`) with no tier change and
no PDF. It does not prove Gibbs concentration, tube or entropy estimates,
partition convergence, tightness, floor removal, continuum limits, physical
branch selection, QFT/Yang--Mills correspondence, or a mass gap. It does not
close A6 or A7. The next forward gate is a branch-aware cutoff-uniform
tube/entropy and tightness audit using this dichotomy as an input partition,
while T-054 Q3LOCK owner intake and the T-059/T-061 observation-source locks
continue unchanged.
