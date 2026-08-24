import Mathlib

namespace Tect.R255

theorem force_fixture :
    ((3 : Rat) - (-2)) * (2 * (3 : Rat)^2 - (3 : Rat) * (-2) + (-2)^2 + 20) / 20 = 12 := by
  norm_num

theorem force_first_derivative_fixture :
    (3 * (3 : Rat)^2 - 3 * (3 : Rat) * (-2) + (-2)^2 + 10) / 10 = 59 / 10 := by
  norm_num

theorem force_second_derivative_fixture :
    3 * (2 * (3 : Rat) - (-2)) / 10 = 12 / 5 := by
  norm_num

theorem third_a1_real_fixture :
    -(1 / 4 : Rat) * (59 / 10) = -59 / 40 := by
  norm_num

theorem third_a1_imaginary_fixture :
    -3 * (1 / 4 : Rat)^2 * 12 = -9 / 4 := by
  norm_num

theorem third_a0_real_fixture :
    -(1 / 4 : Rat) * (12 / 5) / 2 +
        3 * (1 / 4 : Rat)^3 * 12 / 2 = -3 / 160 := by
  norm_num

theorem third_a0_imaginary_fixture :
    -2 * (1 / 4 : Rat)^2 * (59 / 10) = -59 / 80 := by
  norm_num

theorem degree_fixture :
    (3 : Nat) = 3 ∧ (2 : Nat) = 2 ∧ (1 : Nat) = 1 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R255
