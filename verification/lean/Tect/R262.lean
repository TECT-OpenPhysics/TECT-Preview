import Mathlib

namespace Tect.R262

def twoSidedSquared (right left : Rat) : Rat := right + left

theorem two_sided_identity (right left : Rat) :
    twoSidedSquared right left = right + left := by
  rfl

theorem finite_fixture_positive :
    (1 : Rat) > 0 ∧ (3 / 5 : Rat) > 0 ∧ (1 / 10 : Rat) ≥ 0 ∧ (1 / 4 : Rat) > 0 := by
  norm_num

theorem time_tail_scale_fixture :
    (1 / 5 : Rat) * (1 / 10 : Rat) = 1 / 50 := by
  norm_num

theorem smooth_cutoff_midpoint_fixture :
    (1 / 2 : Rat) * (1 + 1) = 1 := by
  norm_num

theorem q3_bond_fixture :
    (1 : Rat) / 2 + (1 / 10 : Rat) / 4 = 21 / 40 := by
  norm_num

theorem modular_floor_fixture :
    (1 / 10 : Rat) > 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R262
