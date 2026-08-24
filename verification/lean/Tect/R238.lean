import Mathlib

namespace Tect.R238

theorem quartic_weyl_kappa_positive :
    (51 / 35 : Rat) * (1 / 2 : Rat) * (1 / 3 : Rat) > 0 := by
  norm_num

theorem quartic_weyl_cubic_coefficient :
    (51 / 35 : Rat) * (1 / 2 : Rat) * (1 / 3 : Rat) = 17 / 70 := by
  norm_num

theorem strip_growth_coefficient_positive :
    3 * (17 / 70 : Rat) > 0 := by
  norm_num

theorem strip_sign_choice_positive :
    -(3 * (17 / 70 : Rat) * (-1 : Rat)) > 0 := by
  norm_num

theorem quartic_difference_degree_fixture :
    (4 : Nat) - 1 = 3 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R238
