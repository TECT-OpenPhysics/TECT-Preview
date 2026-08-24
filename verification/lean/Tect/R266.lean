import Mathlib

namespace Tect.R266

def formRatio (r : Rat) : Rat := r ^ 2

theorem cube_edge_fixture : (12 : Nat) = 12 := by
  norm_num

theorem support_layers_fixture : (2 : Nat) < 6 ∧ (6 : Nat) < 8 := by
  norm_num

theorem form_ratio_fixture : formRatio (5 / 4) = 25 / 16 := by
  norm_num [formRatio]

theorem finite_residual_fixture : (1 / 10 : Rat) < 1 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R266
