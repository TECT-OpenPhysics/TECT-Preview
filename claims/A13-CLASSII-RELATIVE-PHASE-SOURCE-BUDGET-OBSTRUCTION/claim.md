# A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION

## Claim

For the hash-pinned A1 production coefficients and the A10-A12 strict sharp
rectangular-cube filtration, the exact Class-II matrix has the Fierz form

\[
B(X)=dP-4(b+c)\frac{s}{R}(Z\otimes X+X\otimes Z)
     +4c\frac{s^2}{R^2}X\otimes X,
\]

where

\[
P=4\{sE_Z-(\mathcal JZ)(\mathcal JZ)^T\},\qquad
d=a+2b+c.
\]

It separately annihilates the doublet and singlet phase tangents,

\[
B(X)\mathcal JZ=B(X)\mathcal JW=0,
\]

and the actual next-shell source is the exact commutator

\[
P_j[B(u_j)D u_j]=[P_j,M_{B(u_j)}]D u_j,
\qquad u_j=P_{\le j-1}\phi.
\]

These improvements remove the common-phase counterexample. They do not remove
an opposite-corner internal SU(2) relative-phase carrier. For the explicit
degree-65536 polynomial recorded in the manifest, the asymptotic exact-B
source-to-sextic ratio obeys

\[
C_{\rm rel}>0.9>\frac{\gamma}{3}=0.54.
\]

Hence the deterministic source-only absorption condition

\[
C_{\rm rel}<\frac{\gamma}{3p}
\]

fails for every \(p\ge1\). The determinant resolvent tends to the identity on
the same fixed-envelope high-carrier sequence, so retaining it does not repair
this production budget.

## Scope and tier

The scope is the fixed \(L=16\) torus, three complex fields in the six-real
convention, `rho_regularizer=1e-12`, the A1 production symbol and coefficients,
the common unit sharp cutoff, exact Fourier products, and strict dyadic sharp
rectangular cubes. A13 is scoped T4: the Fierz/null/commutator/resolvent
identities are exact, and two independent finite numerical routes reproduce a
large-margin countercertificate. It is not a formal floating-point interval
proof and is not a positive source theorem.

T-049 is closed negatively as a production-budget gate. A finite exact-B
source bound may still exist; the result only proves that its best constant
cannot fit the current standalone sextic allocation.

## Consequence

The next gate is
`A13-CLASSII-JOINT-SOURCE-POTENTIAL-LOG-LAPLACE`. It must retain a cancellation
between the source and the local potential, redesign the true increment, or
use a genuinely probabilistic cancellation. Improving a standalone
source-square constant or restoring the resolvent cannot defeat this witness.

The obstruction is registered as
`NG-2026-07-21-A13-RELATIVE-PHASE-SOURCE-BUDGET`.

## Reproduction

```powershell
python codes/foundations/a13_classii_relative_phase_source_obstruction_verify.py
```

Expected: primary, non-importing independent, and integrated assertions all
pass; the integrated verifier prints
`A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION-INTEGRATED-PASS`.

## Evidence

- `classii_relative_phase_source_obstruction_manifest.json`
- `notes/classii-relative-phase-source-budget-obstruction-260721-v1.0.tex.txt`
- `notes/classii-relative-phase-source-budget-obstruction-260721-v1.0.pdf`
- `../../codes/foundations/a13_classii_relative_phase_source_obstruction.py`
- `../../codes/foundations/a13_classii_relative_phase_source_obstruction_independent.py`
- `../../codes/foundations/a13_classii_relative_phase_source_obstruction_verify.py`
- `runs/2026-07-21-primary-relative-phase-obstruction/result.json`
- `runs/2026-07-21-independent-relative-phase-obstruction/result.json`
- `runs/2026-07-21-integrated-relative-phase-obstruction/result.json`
- `../../negative-results/registry.md#ng-2026-07-21-a13-relative-phase-source-budget`

## Devil's-advocate

1. **The common-phase null kills the witness - DISMISSED.** The carrier rotates
   the two doublet entries oppositely and is an active SU(2) horizontal
   tangent.
2. **The nonlinear current remains below the previous cutoff - DISMISSED.**
   The tensor Riesz boundary polynomial places the complement of the
   nonpositive octant in the next output cube.
3. **The fixed floor changes the leading carrier - DISMISSED.** The carrier
   has \(ds=d\rho=0\), so every rational radial term vanishes exactly.
4. **A six-real factor or torus factor is missing - DISMISSED.** Both complex
   components, the sextic factor eight, the exact covariance convention, and
   the physical \(2\pi/L\) cancellation are retained and cross-checked.
5. **The finite calculation is a formal interval certificate - VALID WITH
   MITIGATION.** It is not labelled as one. Independent coefficient and
   alias-free grid routes agree with more than 0.36 margin above \(\gamma/3\),
   and the claim remains T4.
6. **The determinant resolvent restores absorption - DISMISSED.** Its shell
   operator is \(O(N^{-2})\) on the fixed-envelope carrier, so the resolvent
   tends to the identity. Amplitude scaling provides the same limit.
7. **The exact source is unbounded - UPHELD.** This is not claimed; only the
   current production budget is refuted.
8. **All constructive routes fail - UPHELD.** Joint source-potential,
   redesigned-increment, and probabilistic routes remain open.

## Falsifier

Any failure of the Fierz matrix identity, either phase null, local phase
covariance, shell commutator, active SU(2) carrier identity, output-octant
count, complex/six-real normalization, finite polynomial cross-route result,
conservative inequality \(C_{\rm rel}>0.9>\gamma/3\), resolvent
\(O(N^{-2})\) limit, source hash, PDF QA, assertion count, or release gate
falsifies the pinned package.

## No-overclaim

This claim does not prove that the exact source is unbounded, rule out a joint
source-potential estimate or a different increment, prove the A11 stabilised
log-Laplace theorem, close the A7 Nelson bound, construct an interacting
measure, remove the floor or regulator, take infinite volume, prove a phase
transition or BCC selection, or justify T5, T6, or T7.

## History

- 2026-07-21: Registered at scoped T4 with exact Fierz, two-phase null,
  shell-commutator and resolvent identities, plus an independently reproduced
  SU(2) relative-phase finite-polynomial obstruction. T-049 closed negatively.
