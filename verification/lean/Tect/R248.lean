import Mathlib

namespace Tect.R248

theorem gibbs_weight_normalization :
    (2 / 3 : Rat) + 1 / 3 = 1 := by
  norm_num

theorem first_commutator_fixture :
    (0 : Rat) - 1 = -1 ∧ (1 : Rat) - 0 = 1 := by
  norm_num

theorem second_commutator_fixture :
    (-1 : Rat) * (-1) = 1 ∧ (1 : Rat) * 1 = 1 := by
  norm_num

theorem initial_seminorm_fixture :
    (2 / 3 : Rat) * 2 + (1 / 3 : Rat) * 2 = 2 := by
  norm_num

theorem double_seminorm_fixture :
    (2 / 3 : Rat) * 2 + (1 / 3 : Rat) * 2 = 2 := by
  norm_num

theorem finite_remainder_bound_fixture :
    ((1 / 10 : Rat)^4 * 2) / 4 = 1 / 20000 := by
  norm_num

theorem finite_scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R248
