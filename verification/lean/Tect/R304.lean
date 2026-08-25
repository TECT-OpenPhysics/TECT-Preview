import Mathlib

namespace Tect.R304

/- R304 checks exact rational constants behind EXP-001133.  It does not
   formalize the C1 product-rule estimate, multiplication operators, form
   representation, modular transfer, or thermodynamic limits. -/

theorem regularized_coordinate_square_fixture (x : Rat) :
    x^2 / (1 + x^2) ≤ (1 : Rat) := by
  have h : 0 < 1 + x^2 := by positivity
  apply (div_le_iff₀ h).2
  nlinarith [sq_nonneg x]

theorem support_bound_fixture (m : Rat) (hm : 0 ≤ m) :
    (2 : Rat) + m ≥ 2 := by
  linarith

theorem cross_orientation_multiplier_fixture (m : Rat) :
    (21 : Rat) * (2 + m) = 42 + 21 * m := by
  ring

theorem degree_multiplier_fixture :
    (1 : Rat) + (10 / 3) * 6 = 21 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R304
