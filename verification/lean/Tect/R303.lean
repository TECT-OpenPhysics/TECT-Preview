import Mathlib

namespace Tect.R303

/- R303 checks the rational constants behind EXP-001132.  The analytic
   product-rule estimate is recorded at the finite Weyl-cylinder scope; this
   file does not formalize multiplication operators, form representation,
   modular transfer, or thermodynamic limits. -/

theorem weyl_base_bound_fixture (t : Rat) :
    (2 : Rat) ≤ 2 + t^2 := by
  nlinarith [sq_nonneg t]

theorem support_norm_fixture (t1 t2 t3 t4 : Rat) :
    0 ≤ t1^2 + t2^2 + t3^2 + t4^2 := by
  positivity

theorem cross_orientation_multiplier_fixture (t : Rat) :
    (21 : Rat) * (2 + t^2) = 42 + 21 * t^2 := by
  ring

theorem two_support_norm_fixture (t1 t2 : Rat) :
    2 + (t1^2 + t2^2) = 2 + t1^2 + t2^2 := by
  ring

theorem degree_multiplier_fixture :
    (1 : Rat) + (10 / 3) * 6 = 21 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R303
