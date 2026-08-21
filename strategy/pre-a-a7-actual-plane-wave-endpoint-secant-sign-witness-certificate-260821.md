# R-171 v1.0 -- actual A7 plane-wave endpoint secant sign witness

## 1. Status and exact scope

This certificate records a narrow T4 result for the deterministic Class-II
component of the hash-pinned A7/A1 model. The torus is the registered
`L=16` three-torus, the field has three complex components in the six-real
convention, the positive A1 coefficients and `rho_regularizer=1e-12` are read
from the pinned manifests, and the embedded Pauli matrices are read from the
hash-pinned A1 backend. The witness is one real polarization `u=e1` and the
dual-lattice mode `n=(1,0,0)`.

This is a component-energy endpoint witness. It is not a new A1 action, not a
random covariance-normal composite, and not a physical state.

## 2. Exact field and current calculation

Set `k=2*pi/16=pi/8`, `theta=k*x_1`, `s=amp*cos(theta)`, and
`d=-amp*k*sin(theta)`. For

`Psi_amp(x)=amp*cos((pi/8)*x_1)*e1`

the three embedded Pauli generators give, with the A7 definitions
`rho=Psi^dagger Psi`, `q_A=(Psi^dagger S_A Psi)/(rho+eps)`,
`p_A=2 S_A Psi`, and `v_A=2(S_A-q_A I)Psi`,

`q_1=q_2=0`, `q_3=s^2/(s^2+eps)`,

`p_1 dot d=p_2 dot d=v_1 dot d=v_2 dot d=0`,

`p_3 dot d=2*s*d`, and
`v_3 dot d=2*eps*s*d/(s^2+eps)`.

Thus the deterministic A7 density

`e_II=(1/2) sum_i (partial_i X)^T B(X) partial_i X`

reduces exactly to

`e_II=(s*d)^2 [2*a+4*b*eps/(s^2+eps)+2*c*eps^2/(s^2+eps)^2]`.

The coefficients are derived from the A1 manifest, not copied as numerical
oracles:

`a=cJJ*alpha_X^2/(M_X^2+classii_mass_regularizer)`,
`b=cJK*alpha_X*beta_X/(M_X^2+classii_mass_regularizer)`, and
`c=cKK*beta_X^2/(M_X^2+classii_mass_regularizer)`.

## 3. Positivity and the endpoint secant

Writing `r=s^2>=0`, the bracket has denominator `(r+eps)^2` and numerator

`2*a*r^2 + 4*eps*(a+b)*r + 2*eps^2*(a+2*b+c)`.

All four quantities `a,b,c,eps` are strictly positive in the pinned model.
Therefore the bracket is positive for every `r>=0`. The prefactor `(s*d)^2`
is nonnegative and is positive on an open set for every nonzero `amp`.
Continuity then gives

`E_II[Psi_amp] > 0`, while `E_II[0]=0`.

The exact endpoint secant is consequently

`E_II[0]-E_II[Psi_amp] < 0`.

As a transparent reproducible check, at `amp=1` and `theta=pi/4`, the
normalized point density is `bracket(r=1/2)/256 > 0`. Integrating only the
first positive term gives the exact lower bound

`E_II[Psi_amp]/(amp^4*pi^2) >= 16*a > 0`.

The primary SymPy derivation and the non-importing Fraction derivation agree
on all exact coefficients, the Pauli current identities, the mode
commensurability, the point witness, and the lower bound.

## 4. Adversarial review

- **Sign/convention:** the factor `1/2` in the A7 density and the two cross
  terms in `B` are retained. The independent lane derives the same bracket;
  replacing the endpoint sign or dropping the cross term fails its mutation
  checks.
- **Mode/torus:** `n=(1,0,0)` gives `k=pi/8` exactly, so the witness is a
  periodic dual-lattice field. Replacing the mode by zero or changing `L`
  invalidates the mode check.
- **Pauli/current:** the S1 and S2 currents vanish only after the actual
  embedded matrices are applied; S3 supplies the displayed normalized
  current. Dropping S2/S3 is rejected by the integrated mutation firewall.
- **Owner separation:** the calculation uses only the deterministic A7
  component density. It does not replace it by the full A1 action, the
  covariance-normal random composite, or a physical free energy.
- **Route boundary:** a negative endpoint secant does not close the complete
  A13/T-050 joint owner. Nelson, measure, phase/morphology, physical-empty,
  Sector-A and Pre-A implications are not inferred.

<a id="lean-kernel-cross-check"></a>
## 5. Lean kernel cross-check

The exact algebraic core is independently checked by the repository-pinned
Lean 4.32.1/Mathlib v4.32.1 lane. `Tect/R171.lean` proves the bracket
denominator identity, ordered-field positivity under explicit `a,b,c,eps>0`
hypotheses, and the nonzero pointwise endpoint factor. The bridge verifies the
five R-171 authority hashes, the Lake dependency lock, theorem markers, and
the absence of `sorry`, `admit`, `axiom`, and `unsafe` escape tokens before
running:

`lake env lean Tect/R171.lean`

The saved bridge artefact reports `LEAN R-171 PASS 18/18` at
`claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-21-lean-r171-kernel-crosscheck/result.json`.
This is an additive kernel cross-check of the local exact identity; it does
not replace the SymPy/Fraction lanes and does not promote the result or close
the full A1/A13/T-050, physical-empty, Gibbs/Nelson, or continuum obligations.

## 6. Stored boundary

This result is saved as R-171 / EXP-000878 under the existing A7 and A13
authorities. It is a model-level relative-sign boundary, not a vacuum
selection theorem. A13 and T-050 remain open, no new negative result is
registered, and no R-171 v1.0 PDF is issued.

<a id="exact-a7-plane-wave-endpoint-secant"></a>
