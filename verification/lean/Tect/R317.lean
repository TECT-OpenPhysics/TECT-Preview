import Mathlib

namespace Tect.R317

theorem four_leg_scalar_identity (a b c d : Rat) :
    a + b + c + d = (a + b) + (c + d) := by
  ring

theorem local_weight_fixture :
    (2 / 3 : Rat) * (1 + 1) ^ 2 = 8 / 3 := by
  norm_num

theorem global_weight_scope_fixture :
    (2 / 27 : Rat) > 0 := by
  norm_num

theorem local_four_leg_fixture :
    (2 / 3 : Rat) + 8 / 3 + 1 / 3 + 4 / 3 = 5 := by
  norm_num

end Tect.R317
