import Mathlib

namespace Tect.R249

theorem second_commutator_scaling (n : Rat) :
    2 * (n ^ 2) ^ 2 = 2 * n ^ 4 := by
  ring

theorem n_four_fixture :
    2 * ((4 : Rat) ^ 2) ^ 2 = 512 := by
  norm_num

theorem force_zero_fixture :
    (0 : Rat) ^ 4 = 0 := by
  norm_num

theorem growth_fixture :
    2 * ((4 : Rat) ^ 2) ^ 2 < 2 * ((5 : Rat) ^ 2) ^ 2 := by
  norm_num

theorem scope_fixture :
    (True ∧ True) ∧ ¬False := by
  norm_num

end Tect.R249
