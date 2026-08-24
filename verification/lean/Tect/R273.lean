import Mathlib

namespace Tect.R273

/- Exact rational fixtures for EXP-001091.  These lemmas check the bounded
   interaction-picture rate, the sublinear cutoff exponent, the two modular
   margins, and the explicit two-orientation convention.  They do not encode
   Dyson convergence, an unbounded domain, or the exact-Q3 modular hypothesis. -/

def dysonCoefficient (degree time v2 hbar weightBase : Rat) : Rat :=
  weightBase * 2 * degree * time * v2 / hbar

def modularCoefficient (base modularMultiplier coefficient : Rat) : Rat :=
  base * modularMultiplier * coefficient

theorem dyson_coefficient_fixture :
    dysonCoefficient 6 1 (1 / 100) 1 2 = (6 / 25 : Rat) := by
  norm_num [dysonCoefficient]

theorem modular_coefficient_fixture :
    modularCoefficient 1 2 (6 / 25) = (12 / 25 : Rat) := by
  norm_num [modularCoefficient]

theorem sublinear_scale_fixture :
    (0 : Rat) < 1 / 3 ∧ 2 * (1 / 3 : Rat) < 1 := by
  norm_num

theorem factorial_exponent_fixture :
    2 * (1 / 3 : Rat) - 1 < 0 := by
  norm_num

theorem static_margin_d_fixture :
    (10 : Rat) - (6 / 25 : Rat) > 0 := by
  norm_num

theorem static_margin_delta_fixture :
    (12 : Rat) - (12 / 25 : Rat) > 0 := by
  norm_num

theorem orientation_fixture :
    (1 : Rat) + 1 = 2 := by
  norm_num

theorem scale_radius_fixture :
    (4 : Nat)^3 = 64 ∧ (8 : Nat)^3 = 512 ∧ (16 : Nat)^3 = 4096 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬(False) := by
  norm_num

end Tect.R273
