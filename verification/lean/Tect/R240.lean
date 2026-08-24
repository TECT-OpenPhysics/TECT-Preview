import Mathlib

namespace Tect.R240

theorem force_derivative_fixture :
    (1 : Rat) * ((1 : Rat) - 0) + (1 / 10 : Rat) * ((1 : Rat) - 0) *
        (2 * (1 : Rat)^2 - (1 : Rat) * 0 + 0^2) / 2 = 11 / 10 := by
  norm_num

theorem force_degree_fixture :
    (3 : Nat) = 3 := by
  norm_num

theorem second_coefficient_fixture :
    -(1 / 4 : Rat) * (11 / 10 : Rat) / ((1 : Rat) * 1) = -(11 / 40 : Rat) := by
  norm_num

theorem hbar_chi_fixture :
    (1 / ((1 : Rat) * 1)) = 1 := by
  norm_num

theorem first_difference_fixture :
    (0 : Rat) = 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R240
